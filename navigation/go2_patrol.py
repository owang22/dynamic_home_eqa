"""Patrol support on the console (Oliver 11-21: a patrol agent that is safe and picks views from what the dog has seen).

The patrol *brain* runs on cheetah (client cheetah-patrol, repo planning/patrol_brain/). This file holds the console's
side of the split, which is geometry, timing and refusals, never what is worth looking at:

- keep-out zones (/maps/<map>_keepout.json), shown on the console map and refused by every patrol check;
- GET /map/grid.json: the saved occupancy grid plus height layers, keep-outs and a map_id, for cheetah's 2.5-D coverage;
- POST /patrol/check: a batched dry run for candidate poses: ok or refused + why, route length and an estimated time.
  It never claims the dog and never moves it.

Later steps (agreed with cheetah, inbox 2026-11-21_1625): patrol start/stop (the safety envelope) + /agent/view with
views kept on disk, /patrol/views, /patrol/prior.
"""
import base64
import json
import math
import os
import threading

import numpy as np

WALK_V = 0.35          # m/s average along a go_to route, turns and slow-downs included (provisional until the prior)
TURN_V = 0.6           # rad/s, go2_agent.TURN_SPEED
SETTLE_S = 1.5         # stand still before a photo
MAX_POSES = 40         # per /patrol/check call
SNAP_WARN_M = 0.30     # the planner moved the goal further than this: say so
LAYER_OCC = 2          # go2_mapper.LAYER_OCC

# Provisional zones until Oliver gives the real outlines (cheetah 11-21 agreed on both).
DEFAULT_KEEPOUT = [
    {"id": "stairwell_door", "kind": "circle", "x": -5.93, "y": 1.62, "r": 1.0, "provisional": True,
     "why": "the stairwell door: the dog must not leave the lab (covers tag C)"},
    {"id": "podium_edge", "kind": "circle", "x": -3.59, "y": 0.57, "r": 0.5, "provisional": True,
     "why": "the podium edge (outline still to be given by Oliver)"},
]


def _wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


class Keepout:
    def __init__(self, root, name):
        self.path = os.path.join(root, f"{name}_keepout.json")
        self.lock = threading.Lock()
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump(DEFAULT_KEEPOUT, f, indent=1)
            try:
                os.chown(self.path, 1000, 1000)
            except OSError:
                pass

    def zones(self):
        with self.lock:
            try:
                with open(self.path) as f:
                    return json.load(f)
            except (OSError, ValueError):
                return list(DEFAULT_KEEPOUT)

    def hit(self, x, y, margin=0.0):
        """The first zone (x, y) is inside, or None. margin grows every zone (the dog's half width)."""
        for z in self.zones():
            if z.get("kind") == "circle" and math.hypot(x - z["x"], y - z["y"]) <= z["r"] + margin:
                return z
            if z.get("kind") == "polygon" and _in_poly(x, y, z["points"]):
                return z
        return None


def _in_poly(x, y, pts):
    inside = False
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def _b64(a):
    return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()


def grid_json(mapper, keepout):
    """The saved map for offline use: rows go up (row 0 = lowest y), cell (r, c) centre =
    origin + ((c + 0.5) * res, (r + 0.5) * res). Arrays are base64 of uint8, row-major, cropped to the known area.
    occ: 0 occupied, 254 free, 205 unknown. mid/high: 1 where that height band has structure.
    ceiling_cm: ceiling height in cm, 0 = unknown."""
    base = mapper.grid()
    known = np.argwhere(base != 205)
    if len(known) == 0:
        return None
    (r0, c0), (r1, c1) = known.min(0) - 5, known.max(0) + 6
    r0, c0 = max(r0, 0), max(c0, 0)
    r1, c1 = min(r1, base.shape[0]), min(c1, base.shape[1])
    with mapper.lock:
        mid = (mapper.mid[r0:r1, c0:c1] >= LAYER_OCC).astype(np.uint8)
        high = (mapper.high[r0:r1, c0:c1] >= LAYER_OCC).astype(np.uint8)
        ceil = mapper.ceil[r0:r1, c0:c1].copy()
        ox, oy = mapper.origin
    res = 0.05
    ceil_cm = np.where(np.isnan(ceil), 0, np.clip(ceil * 100, 1, 65535)).astype(np.uint16)
    return {
        "map_id": mapper.saved_at, "res": res, "shape": [int(r1 - r0), int(c1 - c0)],
        "origin": [round(ox + c0 * res, 3), round(oy + r0 * res, 3)],
        "row_order": "row 0 = lowest y (flip vertically to draw like /map.png)",
        "occ": _b64(base[r0:r1, c0:c1]), "mid": _b64(mid), "high": _b64(high),
        "ceiling_cm": base64.b64encode(np.ascontiguousarray(ceil_cm).astype("<u2").tobytes()).decode(),
        "bands_m": {"mid": [0.60, 1.20], "high": [1.20, 2.20], "ceiling_above": 2.20},
        "note": "mid/high/ceiling come only from the lidar, which is clipped near 1.3 m: high and ceiling are mostly empty",
        "keepout": keepout.zones(),
    }


def _turns(path, yaw0, yaw_goal):
    """Total heading change (rad) to follow path from heading yaw0 and end facing yaw_goal (None = don't care)."""
    total, h = 0.0, yaw0
    for (ax, ay), (bx, by) in zip(path, path[1:]):
        if math.hypot(bx - ax, by - ay) < 0.05:
            continue
        nh = math.atan2(by - ay, bx - ax)
        if h is not None:
            total += abs(_wrap(nh - h))
        h = nh
    if yaw_goal is not None and h is not None:
        total += abs(_wrap(yaw_goal - h))
    return total


def check(poses, agent, keepout):
    """Dry run for a batch of poses [{x, y, yaw_deg?, look_deg?}] from where the dog is now.
    Returns (http_code, body). Never claims or moves the dog."""
    if not isinstance(poses, list) or not poses:
        return 400, {"error": "poses must be a non-empty list of {x, y, yaw_deg?}"}
    if len(poses) > MAX_POSES:
        return 400, {"error": f"at most {MAX_POSES} poses per call"}
    mp = agent.map_pose_now()
    if mp is None:
        return 409, {"error": "not lined up with the map", "code": "no_map_pose"}
    if agent.planner is None:
        return 503, {"error": "no planner (no map loaded)", "code": "no_map"}
    agent.update_live()
    out = []
    for i, p in enumerate(poses):
        try:
            x, y = float(p["x"]), float(p["y"])
            yaw = None if p.get("yaw_deg") is None else math.radians(float(p["yaw_deg"]))
        except (KeyError, TypeError, ValueError):
            out.append({"i": i, "ok": False, "why": {"code": "bad_pose", "detail": "x and y (map m) are required"}})
            continue
        r = {"i": i, "x": x, "y": y, "yaw_deg": p.get("yaw_deg")}
        z = keepout.hit(x, y, margin=0.2)
        if z:
            r.update(ok=False, why={"code": "keep_out", "detail": f"inside keep-out zone {z['id']}: {z['why']}",
                                    "zone": z["id"]})
            out.append(r)
            continue
        plan = agent.planner.plan(mp["x"], mp["y"], x, y)
        if "path" not in plan:
            r.update(ok=False, why={"code": "no_route", "detail": plan.get("error") or "no route",
                                    "planner_why": plan.get("why")})
            out.append(r)
            continue
        path = plan["path"]
        crossed = next((keepout.hit(px, py, margin=0.15) for px, py in path if keepout.hit(px, py, margin=0.15)), None)
        if crossed:
            r.update(ok=False, why={"code": "route_keep_out", "detail": f"the only route found crosses keep-out zone "
                                    f"{crossed['id']}", "zone": crossed["id"]}, route_m=round(plan["length_m"], 2))
            out.append(r)
            continue
        gx, gy = plan.get("goal", [x, y])
        snap = math.hypot(gx - x, gy - y)
        turn = _turns(path, mp["yaw"], yaw)
        walk_s = plan["length_m"] / WALK_V
        r.update(ok=True, route_m=round(plan["length_m"], 2), est_s=round(walk_s + turn / TURN_V + SETTLE_S, 1),
                 est={"walk_s": round(walk_s, 1), "turn_s": round(turn / TURN_V, 1), "settle_s": SETTLE_S},
                 tight=bool(plan.get("tight")), squeeze=bool(plan.get("squeeze")),
                 goal_used=[round(gx, 2), round(gy, 2)], snapped_m=round(snap, 2))
        flags = []
        if snap > SNAP_WARN_M:
            flags.append(f"goal moved {snap:.2f} m to open floor")
        if plan.get("fallback"):
            flags.append(f"planner fallback: {plan['fallback']}")
        if plan.get("pose_suspect"):
            flags.append("the live lidar view looks shifted against the map: pose suspect")
        if flags:
            r["flags"] = flags
        out.append(r)
    return 200, {"from": {"x": round(mp["x"], 2), "y": round(mp["y"], 2), "yaw_deg": round(math.degrees(mp["yaw"]), 1)},
                 "results": out,
                 "model": {"walk_v": WALK_V, "turn_v": TURN_V, "settle_s": SETTLE_S,
                           "note": "est_s is a rough estimate (provisional speeds until the driving prior)"}}
