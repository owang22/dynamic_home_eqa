"""Patrol support on the console (Oliver 11-21: a patrol agent that is safe and picks views from what the dog has seen).

The patrol *brain* runs on cheetah (client cheetah-patrol, repo planning/patrol_brain/). This file holds the console's
side of the split, which is geometry, timing and refusals, never what is worth looking at:

- keep-out zones (/maps/<map>_keepout.json), shown on the console map and refused by every patrol check;
- GET /map/grid.json: the saved occupancy grid plus height layers, keep-outs and a map_id, for cheetah's 2.5-D coverage;
- POST /patrol/check: a batched dry run for candidate poses: ok or refused + why, route length and an estimated time.
  It never claims the dog and never moves it.

- step 3: POST /agent/patrol/start, /agent/patrol/stop and /agent/view, the safety envelope (Patrols below), with
  every view kept on disk under /maps/<map>_patrols/<patrol_id>/ and served by GET /patrols, /patrol/<id>[/<file>].

Later steps (agreed with cheetah, inbox 2026-11-21_1625): /patrol/views, /patrol/prior.
"""
import base64
import json
import math
import os
import re
import threading
import time
from collections import deque

import numpy as np

# est_s model, calibrated 11-21 on the 17 go_to calls in lab_history with a map pose at both ends (10-27 cheetah-lab-agent,
# 11-18 ask-the-dog; 1 Hz rows, so +-1 s each), each re-planned on the current map from its start to end pose. Least squares
# T = c + route_m / WALK_V + planned_turn_rad / TURN_V gives c 2.3 s, 0.21 m/s, 0.39 rad/s (MAE 3.7 s, max 9.8 s; the old 0.35 m/s /
# 0.6 rad/s / 1.5 s under-estimated by 8.8 s on average, x1.65). Exact durations of 11-18 go_tos in logs/agent_chat
# (route_m planned): 4.14 m in 17.8 s, 4.05 m in 23.3 s, 1.65 m in 10.6 s, 3.73 m in 29.9 s (one re-plan), 0.62 m in 5.7 s.
# The data is thin (17 drives; the console speed preset was not logged before 11-16: slow 0.3 m/s is the default since
# 10-23, normal 0.5), but the patrol caps (0.3 slow / 0.4 normal) are in the same range. The turn rate is an effective one: it includes the stop, settle,
# correction and re-plant around each in-place turn. Refit once patrols have logged their own timing (view.json timing).
WALK_V = 0.21          # m/s average along a go_to route, slow-downs and steering included
TURN_V = 0.39          # rad/s of planned heading change, in-place turn overheads included
GOTO_OVERHEAD_S = 2.3  # per go_to: planning, first turn-in-place settle, final approach
SETTLE_S = 1.5         # stand still before a photo (the /agent/view default settle_s)
# Refit 11-21 18:00 on the first two patrols (11 views, 9 with walking; speed "slow", capped at 0.30 m/s): walk_s =
# 3.4 s + walked_m / 0.12 m/s (MAE 4.2 s). The 17 go_tos above ran mostly at "normal". So walking depends on the
# speed preset. Per heading, measured: face median 5.5 s (p90 8.0), settle 1.5 s, still-wait <= 0.5 s.
WALK_BY_SPEED = {"slow": (0.12, 3.4), "normal": (WALK_V, GOTO_OVERHEAD_S)}   # (m/s, overhead s)
# Facing one heading: FACE_A_S + |turn deg| * FACE_S_PER_DEG. Two points from patrols 1-2: median 5.5 s for typical
# turns, ~16 s for 180 deg -> 2.5 s + 0.075 s/deg. Rough: refit from per-shot face_s / face_from_deg (logged from 18:0x).
FACE_A_S, FACE_S_PER_DEG = 2.5, 0.075
STILL_WAIT_S = 0.3     # typical extra wait for stillness after settle_s (<= STILL_EXTRA_S)
MAX_POSES = 40         # per /patrol/check call
SNAP_WARN_M = 0.30     # the planner moved the goal further than this: say so
LAYER_OCC = 2          # go2_mapper.LAYER_OCC

# The podium and the outside door are not hazards (Oliver, 11-21): no zones for them; the planner treats them as furniture.
DEFAULT_KEEPOUT = [
    {"id": "stairwell_door", "kind": "circle", "x": -5.93, "y": 1.62, "r": 1.0, "provisional": True,
     "why": "the stairwell door: the dog must not leave the lab (covers tag C)"},
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


CLEAR_FOV_DEG = 40.0   # half field of view for front_clear_m (the dog camera: ~79 deg horizontal)
CLEAR_BIN_DEG = 10.0
CLEAR_MAX_M = 6.0
CAM_X = 0.30           # the camera lens is about this far ahead of base_link; ranges are from the lens
BODY_X = 0.35          # points closer than this ahead of base_link are the dog's own body / legs
CLEAR_MIN_H = 0.18     # cells lower than this are floor (the lidar reports the floor in ~10 cm steps; same as
                       # go2_agent.BUMP_H[0]): a first try with every cell read 0.06 m in open floor (11-21)


def front_clearance(odom, cloud, cloud_age):
    """Nearest obstacle in the camera's view from the live lidar cells (AUT ask 17:47): front_clear_m within
    +-CLEAR_FOV_DEG of the heading, measured from the lens, and per-10-deg bins. Obstacle cells are the console's live
    cells 0.1-2.0 m above the floor (the dog's persistent ~5-10 cm voxel map, so it can lag or keep stale voxels)."""
    if not cloud or not cloud.get("obs") or odom is None or cloud.get("frame") == "base_link":
        return {"front_clear_m": None, "ranges_deg_m": None, "cloud_age_s": None if cloud_age is None else round(cloud_age, 2),
                "note": "no live lidar cells"}
    pts = np.asarray(cloud["obs"], dtype=np.float64)
    pts = pts[pts[:, 2] >= CLEAR_MIN_H]
    dx, dy = pts[:, 0] - odom["pos"][0], pts[:, 1] - odom["pos"][1]
    c, s_ = math.cos(odom["yaw"]), math.sin(odom["yaw"])
    fx, fy = c * dx + s_ * dy, -s_ * dx + c * dy
    keep = fx > BODY_X
    cx, cy = fx[keep] - CAM_X, fy[keep]
    rng = np.hypot(cx, cy)
    brg = np.degrees(np.arctan2(cy, cx))
    inside = (np.abs(brg) <= CLEAR_FOV_DEG) & (rng <= CLEAR_MAX_M)
    front = float(rng[inside].min()) if inside.any() else None
    bins = []
    for b0 in np.arange(-CLEAR_FOV_DEG, CLEAR_FOV_DEG, CLEAR_BIN_DEG):
        m = (brg >= b0) & (brg < b0 + CLEAR_BIN_DEG) & (rng <= CLEAR_MAX_M)
        bins.append([round(float(b0 + CLEAR_BIN_DEG / 2), 1), round(float(rng[m].min()), 2) if m.any() else None])
    return {"front_clear_m": None if front is None else round(front, 2), "ranges_deg_m": bins,
            "cloud_age_s": None if cloud_age is None else round(cloud_age, 2),
            "rule": f"live lidar cells {CLEAR_MIN_H}-2 m tall (lower things, e.g. a cable on the floor, are not counted), within +-{CLEAR_FOV_DEG:.0f} deg of the heading, from the lens "
                    f"({CAM_X} m ahead of base_link), up to {CLEAR_MAX_M} m; bearing + = left; null = nothing seen"}


TURN_NEED_M = 0.42     # go2_agent.SWEEP_R: an in-place turn needs nothing closer than this to the dog's centre


def _turn_clear(agent, x, y, mp):
    """Clearance (m) all round a stand (AUT ask 18:34): the planner's distance-to-nearest-blocked cell there (saved
    map + live lidar within ~3 m of the dog, refreshed by update_live), and when the stand is where the dog is now,
    the live sweep check too (the smaller wins). Resolution ~0.1 m. Returns (m or None, source)."""
    pl = agent.planner
    out, src = None, None
    if pl is not None:
        with pl.lock:
            if pl.dist is not None:
                r, c = pl.cell(x, y)
                if pl.inside(r, c):
                    out, src = round(float(pl.dist[r, c]), 2), "planner grid (map + live within ~3 m), 0.1 m cells"
    if mp is not None and math.hypot(x - mp["x"], y - mp["y"]) < 0.3 and hasattr(agent, "sweep_hit"):
        h = agent.sweep_hit()
        live = 9.9 if h is None else round(h, 2)       # nothing within the sweep radius: at least that clear
        if out is None or live < out:
            out, src = (min(live, 9.9) if h is not None else out), "live lidar around the dog now"
    return out, src


def _arrival_yaw(path, yaw0):
    """Heading of the last route segment longer than 5 cm (the dog arrives facing about that way), else yaw0."""
    for (ax, ay), (bx, by) in zip(path[-2::-1], path[::-1]):
        if math.hypot(bx - ax, by - ay) >= 0.05:
            return math.atan2(by - ay, bx - ax)
    return yaw0


def check(poses, agent, keepout, speed="slow"):
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
            yd = p.get("yaw_deg")
            if isinstance(yd, list):
                if not yd or len(yd) > MAX_HEADINGS:
                    raise ValueError
                yd = [float(v) for v in yd]
            yaw = None if yd is None else math.radians(float(yd[0] if isinstance(yd, list) else yd))
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
        yaws = p.get("yaw_deg") if isinstance(p.get("yaw_deg"), list) else None
        if yaws:
            yaw = math.radians(float(yaws[0]))
        turn = _turns(path, mp["yaw"], None)            # along the route only; facing is priced per heading below
        walk_v, overhead = WALK_BY_SPEED.get(speed, WALK_BY_SPEED["slow"])
        walk_s = plan["length_m"] / walk_v
        # per heading: from the arrival heading (last route segment) to the first, then from each to the next
        arrive = _arrival_yaw(path, mp["yaw"])
        hs = [math.radians(float(h)) for h in yaws] if yaws else ([yaw] if yaw is not None else [None])
        heads, prev = [], arrive
        for h in hs:
            dd = 0.0 if h is None or prev is None else abs(math.degrees(_wrap(h - prev)))
            face = 0.0 if dd <= 3.0 else FACE_A_S + dd * FACE_S_PER_DEG
            heads.append({"yaw_deg": None if h is None else round(math.degrees(h), 1), "turn_deg": round(dd, 1),
                          "est_face_s": round(face, 1), "est_settle_s": SETTLE_S + STILL_WAIT_S,
                          "est_s": round(face + SETTLE_S + STILL_WAIT_S, 1)})
            prev = h if h is not None else prev
        r.update(ok=True, route_m=round(plan["length_m"], 2),
                 est_s=round(overhead + walk_s + turn / TURN_V + sum(h["est_s"] for h in heads), 1),
                 headings=heads,
                 est={"walk_s": round(walk_s, 1), "turn_s": round(turn / TURN_V, 1), "settle_s": SETTLE_S,
                      "overhead_s": overhead},
                 tight=bool(plan.get("tight")), squeeze=bool(plan.get("squeeze")),
                 goal_used=[round(gx, 2), round(gy, 2)], snapped_m=round(snap, 2))
        tc, tc_src = _turn_clear(agent, gx, gy, mp)
        r.update(turn_clear_m=tc, turn_clear_source=tc_src,
                 ok_to_turn=None if tc is None else bool(tc >= TURN_NEED_M))
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
                 "model": {"speed": speed if speed in WALK_BY_SPEED else "slow",
                           "walk_v": WALK_BY_SPEED.get(speed, WALK_BY_SPEED["slow"])[0], "turn_v": TURN_V,
                           "settle_s": SETTLE_S, "overhead_s": WALK_BY_SPEED.get(speed, WALK_BY_SPEED["slow"])[1],
                           "note": "est_s = overhead + route/walk_v + planned turns/turn_v + settle, for one heading. "
                                   "slow: fitted on 9 patrol views (MAE 4.2 s); normal: on 17 go_tos (MAE 3.7 s). "
                                   "Each extra heading in a view measured about 5.5 s face (p90 8) + settle_s"}}


# ======================================================================================================================
# Step 3: the patrol envelope. A patrol is owned by one agent client (cheetah-patrol). While it is open, the console,
# not the agent, enforces the limits below on every motion tool from that client; other agents may not claim the dog.
# A person at the console always wins: any takeover (or a console STOP, which is one) ends the patrol at once.
# ======================================================================================================================
PATROL_V = 0.40              # m/s forward cap (prior: human p90 0.39). "slow" uses the console's slow preset if lower
PATROL_TURN_V = 0.6          # rad/s (prior: in-place p90 0.68); "slow" uses the slow preset's turn rate if lower
PATROL_BACK_V = 0.15         # m/s reverse (prior: human p50 0.13 / p90 0.17)
PATROL_BACK_MOVE_M = 0.5     # reverse per move call (prior: episode p50 0.37 m)
PATROL_BACK_TOTAL_M = 1.0    # reverse per patrol, from explicit move calls (re-plant steps return to where they began)
BATTERY_FLOOR = 25           # % : stop and refuse motion below this
STAND_BUDGET_S = 420.0      # continuous standing without walking; then lie down (11-18: collapsed after ~8 min standing; 7 min, coordinator 11-21)
STAND_START_MIN_S = 120.0    # patrol/start needs at least this much standing budget left
LEASE_GRACE_S = 120.0        # after the client's lease lapses: the patrol stays open this long for the same client
MAX_MIN_RANGE, DEFAULT_MIN = (1, 30), 10
VIEW_SETTLE_S, VIEW_SETTLE_MAX_S = 1.5, 5.0
MAX_HEADINGS = 8
VIEW_TIMEOUT_S = 180.0       # one /agent/view call, walk + all headings
FACE_TOL_DEG = 3.0           # don't turn for less than this
WALK_V_MIN, WALK_W_MIN = 0.05, 0.15    # odom speed (m/s, rad/s) that counts as walking (resets the standing clock)
STILL_V, STILL_W = 0.03, 0.05          # and below which a photo counts as still (same as go2_agent._photo)
STILL_WINDOW_S = 0.5                   # the shutter waits for this long below STILL_V/W ...
STILL_EXTRA_S = 2.0                    # ... for at most this long after settle_s (first patrol 11-21: 2 of 4 shots
                                       # were taken while the dog was still moving after a 1.5 s settle)
CAM_MAX_AGE_S = 2.0          # dog camera frame older than this at the shutter: no photo
L515_MATCH_S = 0.6           # an L515 frame further than this from the dog shutter is not "the same instant"
L515_KEEP = 12               # L515 messages kept per kind (~1.5 s at 8 Hz)
MOTOR_STALE_S = 10.0         # same as the console's MOTOR_STALE_S
LOOK_REFRESH_S = 0.4         # while settling with look_deg: re-send the body pitch this often (it springs back otherwise)
LOOK_HELD_FRAC = 0.5         # look_held: the IMU pitch changed by at least this fraction of look_deg
LIE_WAIT_S = 3.0             # monitor: wait this long for an aborted tool to let go before lying down
MONITOR_S = 0.2
KEEPOUT_INSIDE_M = 0.0       # monitor: a patrol tool stops if the dog's centre gets inside a keep-out zone (+ margin)
MIN_BODY_H = 0.18            # go2_agent.MIN_BODY_H: lower means lying down
TILT_LIMIT = 0.6             # go2_agent.TILT_LIMIT
MOTION_CALLS = ("move", "turn", "go_to", "look_around", "look", "view")   # what the envelope checks and interrupts
STICKY = ("time_up", "battery_low", "motor_warm")                         # these halt a patrol for good
PATROL_ID_RE = re.compile(r"^p_\d{8}_\d{6}(_\d{1,3})?$")
FILE_PART_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,80}$")
FILE_TYPES = {".jpg": "image/jpeg", ".png": "image/png", ".json": "application/json"}
HOST_UID = 1000

# what the console subscribes to for views (Collector -> Patrols.l515.on): read-only, nothing is published
L515_TOPICS = (("depth", "Image", "/go2/l515/depth/image_raw"),
               ("color", "CompressedImage", "/go2/l515/color/image_raw/compressed"),
               ("depth_info", "CameraInfo", "/go2/l515/depth/camera_info"),
               ("color_info", "CameraInfo", "/go2/l515/color/camera_info"),
               ("dog_info", "CameraInfo", "/camera/camera_info"))


def _stamp(msg):
    try:
        return msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
    except AttributeError:
        return None


def _info_dict(m):
    return {"frame_id": m.header.frame_id, "stamp": _stamp(m), "width": int(m.width), "height": int(m.height),
            "distortion_model": m.distortion_model, "d": [float(v) for v in m.d], "k": [float(v) for v in m.k],
            "r": [float(v) for v in m.r], "p": [float(v) for v in m.p]}


class L515Raw:
    """Latest L515 messages straight from ROS (the bridge's page only serves JPEGs): raw 16-bit depth, the colour JPEG
    and both camera_infos, kept for ~1.5 s so a view can take the frame closest to the dog camera's shutter."""

    def __init__(self, keep=L515_KEEP):
        self.lock = threading.Lock()
        self.buf = {k: deque(maxlen=keep if k in ("depth", "color") else 4) for k, _, _ in L515_TOPICS}

    def on(self, kind, msg):
        with self.lock:
            self.buf[kind].append((time.time(), _stamp(msg), msg))

    def online(self, max_age=2.0):
        with self.lock:
            d = self.buf["depth"]
            return bool(d) and time.time() - d[-1][0] < max_age

    def dog_info(self):
        with self.lock:
            b = self.buf["dog_info"]
            return _info_dict(b[-1][2]) if b else None

    def closest(self, t, max_dt=L515_MATCH_S):
        """The depth frame received closest to wall time t, with the colour frame and camera_infos of the same stamp
        (nearest if none has it): {depth (uint16 HxW, mm), color_jpeg, depth_info, color_info, t...}, or None."""
        with self.lock:
            depths, colors = list(self.buf["depth"]), list(self.buf["color"])
            dinfo, cinfo = list(self.buf["depth_info"]), list(self.buf["color_info"])
        if not depths:
            return None
        rt, st, dm = min(depths, key=lambda e: abs(e[0] - t))
        if abs(rt - t) > max_dt:
            return None

        def match(lst):
            if not lst:
                return None
            same = [e for e in lst if st is not None and e[1] == st]
            return same[0] if same else min(lst, key=lambda e: abs(e[0] - rt))
        try:
            depth = np.frombuffer(bytes(dm.data), dtype="<u2" if not dm.is_bigendian else ">u2")
            depth = depth.reshape(int(dm.height), int(dm.step) // 2)[:, :int(dm.width)].astype("<u2")
        except (ValueError, AttributeError):
            return None
        c, di, ci = match(colors), match(dinfo), match(cinfo)
        return {"depth": depth, "depth_encoding": dm.encoding, "depth_recv_t": round(rt, 3), "depth_stamp": st,
                "color_jpeg": bytes(c[2].data) if c else None, "color_recv_t": round(c[0], 3) if c else None,
                "color_stamp": c[1] if c else None,
                "depth_info": _info_dict(di[2]) if di else None, "color_info": _info_dict(ci[2]) if ci else None,
                "dt_to_dog_s": round(rt - t, 3)}


def patrol_file(root, pid, rel):
    """The absolute path of file `rel` (e.g. "views/v001_120000/h0_dog.jpg") in patrol `pid`, or None if either is not
    a plain name we make (no traversal, no hidden files, known types only)."""
    if not isinstance(pid, str) or not PATROL_ID_RE.match(pid) or not isinstance(rel, str):
        return None
    parts = rel.split("/")
    if not 1 <= len(parts) <= 3 or any(not FILE_PART_RE.match(x) or ".." in x for x in parts):
        return None
    if os.path.splitext(parts[-1])[1] not in FILE_TYPES:
        return None
    base = os.path.realpath(os.path.join(root, pid))
    f = os.path.realpath(os.path.join(base, *parts))
    if not f.startswith(base + os.sep) or not os.path.isfile(f):
        return None
    return f


def _chown(path):
    try:
        os.chown(path, HOST_UID, HOST_UID)
    except OSError:
        pass


def _write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=str)
    _chown(tmp)
    os.replace(tmp, path)


def _mkdir(path):
    os.makedirs(path, exist_ok=True)
    _chown(path)
    return path


class Patrols:
    """The open patrol (at most one), its envelope, its monitor thread and its files.

    hooks (all callables, from the console): battery() -> {soc, stale?} | None; motors() -> (motors dict | None, age_s);
    deploying() -> dict | None; presets() -> {"slow": (vx, vy, wz), ...}; markers() -> markers snapshot | None.
    The monitor only ever calls _halt_motion (Agents.interrupt: abort the tool + stop) and _lie_down (the posture
    path's node.action("lie")); it never sends a velocity."""

    def __init__(self, ag, keepout, root, map_name, hooks, clock=time.monotonic):
        self.ag, self.keepout, self.hooks, self.clock = ag, keepout, hooks, clock
        self.root = os.path.join(root, f"{map_name}_patrols")
        self.lock = threading.RLock()
        self.p = None                 # the current (or last) patrol record
        self.l515 = L515Raw()
        self.boot = clock()
        self.stand_since = None       # monotonic start of the current standing-still spell
        self.after = None             # after an ending: {"patrol_id"} while the stand budget still watches the dog
        self.interrupted = None       # {code, detail}: why the monitor stopped the running patrol tool
        self._thread = None
        self._close_stale()

    # ---------- files ----------
    def _close_stale(self):
        """Patrols left open by an earlier console process (restart, deploy) are closed on disk."""
        if not os.path.isdir(self.root):
            return
        for pid in os.listdir(self.root):
            f = os.path.join(self.root, pid, "patrol.json")
            try:
                with open(f) as fh:
                    d = json.load(fh)
                if d.get("state") != "ended":
                    d.update(state="ended", stop_reason="console_restart", ended_t=round(time.time(), 2))
                    _write_json(f, d)
            except (OSError, ValueError):
                pass

    def _dir(self, *parts):
        return os.path.join(self.root, self.p["patrol_id"], *parts)

    def _save(self):
        p = self.p
        if p is None:
            return
        rec = {k: v for k, v in p.items() if not k.startswith("_")}
        rec["envelope"] = self._envelope()
        try:
            _write_json(self._dir("patrol.json"), rec)
        except OSError as e:
            print(f"[patrol] could not write patrol.json: {e!r}", flush=True)

    def _event(self, kind, **kw):
        self.p["events"].append(dict(kw, t=round(time.time(), 2), kind=kind))
        self.p["events"] = self.p["events"][-200:]

    def list(self):
        out = []
        if os.path.isdir(self.root):
            for pid in sorted(os.listdir(self.root), reverse=True):
                if not PATROL_ID_RE.match(pid):
                    continue
                try:
                    with open(os.path.join(self.root, pid, "patrol.json")) as f:
                        d = json.load(f)
                except (OSError, ValueError):
                    continue
                out.append({k: d.get(k) for k in ("patrol_id", "client", "state", "started_t", "ended_t", "stop_reason",
                                                  "max_min", "speed", "n_views", "walked_m")})
        return {"patrols": out}

    def view_points(self):
        """[t, x, y, yaw_rad] of every saved patrol shot with a map pose (for /patrol/views seen counts). Cached; the
        cache is refreshed when the patrols folder or any patrol's views folder changes."""
        try:
            stamp = tuple(sorted((pid, os.path.getmtime(os.path.join(self.root, pid, "views")))
                                 for pid in os.listdir(self.root)
                                 if PATROL_ID_RE.match(pid) and os.path.isdir(os.path.join(self.root, pid, "views"))))
        except OSError:
            return []
        if getattr(self, "_vp_stamp", None) == stamp:
            return list(self._vp)
        pts = []
        for pid, _ in stamp:
            vd = os.path.join(self.root, pid, "views")
            for vid in sorted(os.listdir(vd)):
                try:
                    with open(os.path.join(vd, vid, "view.json")) as f:
                        v = json.load(f)
                except (OSError, ValueError):
                    continue
                for sh in v.get("shots", []):
                    ps = sh.get("pose")
                    if ps and sh.get("t"):
                        pts.append([sh["t"], ps["x"], ps["y"], math.radians(ps["yaw_deg"])])
        self._vp_stamp, self._vp = stamp, pts
        return list(pts)

    def get(self, pid):
        if not isinstance(pid, str) or not PATROL_ID_RE.match(pid):
            return None
        d = os.path.join(self.root, pid)
        try:
            with open(os.path.join(d, "patrol.json")) as f:
                rec = json.load(f)
        except (OSError, ValueError):
            return None
        views = []
        vd = os.path.join(d, "views")
        for vid in sorted(os.listdir(vd)) if os.path.isdir(vd) else []:
            try:
                with open(os.path.join(vd, vid, "view.json")) as f:
                    v = json.load(f)
                views.append({k: v.get(k) for k in ("view_id", "t", "goal", "result", "stop_reason", "walked_m", "urls")}
                             | {"headings": [s.get("yaw_deg") for s in v.get("shots", [])]})
            except (OSError, ValueError):
                continue
        with self.lock:
            if self.p and self.p["patrol_id"] == pid:
                rec["envelope"] = self._envelope()
        return dict(rec, views=views)

    def file(self, pid, rel):
        f = patrol_file(self.root, pid, rel)
        if f is None:
            return None, None
        with open(f, "rb") as fh:
            return fh.read(), FILE_TYPES[os.path.splitext(f)[1]]

    # ---------- state ----------
    def is_open(self):
        return self.p is not None and self.p["state"] != "ended"

    def owns(self, client):
        """True while an open patrol belongs to client: its tools go through the envelope."""
        with self.lock:
            return self.is_open() and self.p["client"] == client

    def blocks(self, client):
        """Why another agent may not claim or drive now, or None. Raw /cmd motion is refused for every agent."""
        with self.lock:
            if not self.is_open() or (client is not None and self.p["client"] == client):
                return None
            return {"code": "patrol_open", "detail": f"patrol {self.p['patrol_id']} of {self.p['client']} is open"}

    def envelope_for(self, client):
        with self.lock:
            if self.p is None or self.p["client"] != client:
                return None
            return self._envelope()

    def brief(self):
        """One line for the console page header."""
        with self.lock:
            p = self.p
            if p is None or (p["state"] == "ended" and time.time() - (p.get("ended_t") or 0) > 600):
                return None
            e = self._envelope()
            return {"patrol_id": p["patrol_id"], "client": p["client"], "state": p["state"],
                    "time_left_s": e["time_left_s"], "stop_reason": p.get("stop_reason"),
                    "halt": (p.get("halt") or {}).get("code"), "standing_s": e["standing_s"]}

    def _time_left(self):
        p = self.p
        end = p["ended_t"] if p["state"] == "ended" else time.time()
        return max(0.0, p["max_min"] * 60 - (end - p["started_t"]))

    def _standing_s(self):
        return 0.0 if self.stand_since is None else max(0.0, self.clock() - self.stand_since)

    def _sensors(self):
        odom, imu, state, _, _, ages = self.ag.snap()
        b = self.hooks["battery"]()
        mot, mage = self.hooks["motors"]()
        li = self.ag.mapper.loc_info(track_n=0) if self.ag.mapper is not None else {}
        return odom, imu, state, ages, b, mot, mage, li

    def _envelope(self):
        p = self.p
        _, _, _, _, b, mot, mage, li = self._sensors()
        mot_ok = mot is not None and mage <= MOTOR_STALE_S
        grace = None
        if p["state"] == "grace":
            grace = round(max(0.0, LEASE_GRACE_S - (self.clock() - p["_grace_since"])), 1)
        return {"patrol_id": p["patrol_id"], "state": p["state"], "time_left_s": round(self._time_left(), 1),
                "battery": (b or {}).get("soc") if b and not b.get("stale") else None,
                "hottest_motor_c": mot.get("max") if mot_ok else None,
                "motor_level": mot.get("level") if mot_ok else None,
                "standing_s": round(self._standing_s(), 1), "stand_budget_s": STAND_BUDGET_S,
                "reverse_used_m": round(p["reverse_used_m"], 2), "reverse_budget_m": PATROL_BACK_TOTAL_M,
                "loc": {"lost": li.get("lost"), "suspect": li.get("suspect"), "track_fit": li.get("track_fit")},
                "halt": p.get("halt"), "grace_left_s": grace, "stop_reason": p.get("stop_reason")}

    def conditions(self, start=False):
        """Everything that forbids motion now, as [{code, detail}], most important first."""
        out = []
        odom, imu, state, ages, b, mot, mage, li = self._sensors()
        dep = self.hooks["deploying"]()
        if dep:
            out.append({"code": "deploying", "detail": f"the console is deploying: {dep.get('msg')}"})
        if self.p is not None and not start and self.is_open() and self._time_left() <= 0:
            out.append({"code": "time_up", "detail": f"the patrol's {self.p['max_min']} min are used up"})
        if b is None or b.get("soc") is None or b.get("stale"):
            out.append({"code": "battery_unknown", "detail": "no fresh battery reading"})
        elif b["soc"] < BATTERY_FLOOR:
            out.append({"code": "battery_low", "detail": f"battery {b['soc']}% is below {BATTERY_FLOOR}%"})
        if mot is None or mage > MOTOR_STALE_S or mot.get("max") is None:
            out.append({"code": "motors_unknown", "detail": "no fresh motor temperatures"})
        elif mot.get("level") in ("warm", "hot"):
            out.append({"code": "motor_warm", "detail": f"motor {mot.get('hottest')} at {mot.get('max')} degC "
                                                        f"({mot.get('level')}, warn {mot.get('warn_c')} degC)"})
        if odom is None or imu is None or ages.get("odom", 99) > 1.0 or ages.get("imu", 99) > 1.0:
            out.append({"code": "stale_sensors", "detail": "odometry or IMU is not live"})
        else:
            if abs(imu["rpy"][0]) > TILT_LIMIT or abs(imu["rpy"][1]) > TILT_LIMIT:
                out.append({"code": "fallen", "detail": "roll or pitch over the tilt limit"})
        if state is None or ages.get("state", 99) > 1.0 or state["body_height"] < MIN_BODY_H:
            out.append({"code": "not_standing", "detail": "the dog is not standing (body height low or unknown)"})
        if li.get("lost"):
            out.append({"code": "loc_lost", "detail": "the map fit has been low: the map pose is probably wrong; relocalize"})
        if li.get("suspect"):
            sw = li.get("suspect_why") or {}
            out.append({"code": "loc_suspect", "source": sw.get("source"),
                        "detail": (sw.get("detail") or "the pose is suspect") + "; relocalize (tag mode, or set) before moving on",
                        **({"marks": sw["marks"], "shift_m": sw.get("shift_m")} if sw.get("marks") else {})})
        mp = self.ag.map_pose_now()
        if mp is None:
            out.append({"code": "no_map_pose", "detail": "the console is not lined up with the map"})
        else:
            z = self.keepout.hit(mp["x"], mp["y"], margin=KEEPOUT_INSIDE_M)
            if z:
                out.append({"code": "in_keep_out", "detail": f"the dog is inside keep-out zone {z['id']}", "zone": z["id"]})
        return out

    def caps(self):
        slow = (self.hooks["presets"]() or {}).get("slow")
        v, w = PATROL_V, PATROL_TURN_V
        if self.p["speed"] == "slow" and slow:
            v, w = min(v, slow[0]), min(w, slow[2])
        return {"v": v, "turn_v": w, "back_v": PATROL_BACK_V,
                "back_m": max(0.0, min(PATROL_BACK_MOVE_M, PATROL_BACK_TOTAL_M - self.p["reverse_used_m"]))}

    def _refuse(self, why, more=None, code=409):
        out = {"result": "refused", "reason": why["detail"], "stop_reason": "refused", "why": why}
        if more:
            out["why_all"] = more
        return code, out

    # ---------- start / stop ----------
    def start(self, client, req):
        try:
            max_min = float(req.get("max_min", DEFAULT_MIN))
            if not MAX_MIN_RANGE[0] <= max_min <= MAX_MIN_RANGE[1]:
                raise ValueError
        except (TypeError, ValueError):
            return 400, {"result": "error", "reason": f"max_min must be {MAX_MIN_RANGE[0]}-{MAX_MIN_RANGE[1]}",
                         "stop_reason": "bad_arguments"}
        speed = req.get("speed", "slow")
        if speed not in ("slow", "normal"):
            return 400, {"result": "error", "reason": "speed must be slow or normal", "stop_reason": "bad_arguments"}
        with self.lock:
            if self.is_open():
                if self.p["client"] == client and req.get("patrol_id") == self.p["patrol_id"]:
                    self.touch(client)
                    return 200, {"result": "done", "resumed": True, "patrol_id": self.p["patrol_id"]}
                return self._refuse({"code": "patrol_open", "detail": f"patrol {self.p['patrol_id']} of "
                                     f"{self.p['client']} is open; stop it first (or pass its patrol_id to resume)",
                                     "patrol_id": self.p["patrol_id"]})
            conds = self.conditions(start=True)
            # the monitor tracks standing-still spells from console start (odom speed); a console restart counts as
            # the start of a spell, which can under-count a dog that was already standing
            self._update_standing()
            left = STAND_BUDGET_S - self._standing_s()
            if left < STAND_START_MIN_S and not any(c["code"] == "not_standing" for c in conds):
                conds.append({"code": "stand_budget", "detail": f"the dog has stood without walking for "
                              f"{self._standing_s():.0f} s; walk it or lie it down first"})
            if conds:
                return self._refuse(conds[0], conds)
            now = time.time()
            pid = time.strftime("p_%Y%m%d_%H%M%S", time.localtime(now))
            n = 1
            while os.path.exists(os.path.join(self.root, pid)):
                n += 1
                pid = time.strftime("p_%Y%m%d_%H%M%S", time.localtime(now)) + f"_{n}"
            _mkdir(self.root)
            _mkdir(os.path.join(self.root, pid))
            mp = self.ag.map_pose_now()
            self.p = {"patrol_id": pid, "client": client, "state": "open", "started_t": round(now, 2),
                      "ended_t": None, "max_min": max_min, "speed": speed, "stop_reason": None, "halt": None,
                      "reverse_used_m": 0.0, "walked_m": 0.0, "n_views": 0, "events": [],
                      "start_pose": {k: round(v, 3) for k, v in mp.items()},
                      "map_id": self.ag.mapper.saved_at if self.ag.mapper is not None else None,
                      "_human_seq": self.ag.human_seq, "_grace_since": None}
            self.p["limits"] = dict(self.caps(), battery_floor=BATTERY_FLOOR, stand_budget_s=STAND_BUDGET_S,
                                    lease_grace_s=LEASE_GRACE_S, front_clear="go2_agent.FRONT_CLEAR (unchanged)",
                                    rear_clear="go2_agent.REAR_CLEAR (unchanged)")
            self.after = None
            self.interrupted = None
        try:          # the mount check: whatever is in view from the start pose, without moving
            mount = self._capture(_mkdir(self._dir("mount")), "mount", f"/patrol/{pid}/mount/")
        except RuntimeError as e:
            mount = {"error": str(e)}
        with self.lock:
            self.p["mount_check"] = mount
            self._event("start", client=client, pose=self.p["start_pose"])
            self._save()
            return 200, {"result": "done", "patrol_id": pid, "limits": self.p["limits"], "mount_check": mount,
                         "start_pose": self.p["start_pose"], "map_id": self.p["map_id"]}

    def stop(self, client):
        with self.lock:
            if not self.is_open() or self.p["client"] != client:
                return 409, {"result": "not_owner", "reason": "no open patrol of yours", "stop_reason": "refused"}
        self._halt_motion(f"patrol stopped by {client}")
        with self.lock:
            self._end("client_stop")
            return 200, {"result": "done", "patrol_id": self.p["patrol_id"], "summary": self._summary()}

    def _summary(self):
        p = self.p
        return {k: p.get(k) for k in ("patrol_id", "state", "stop_reason", "started_t", "ended_t", "n_views",
                                       "walked_m", "reverse_used_m", "halt")} | {
            "duration_s": round((p.get("ended_t") or time.time()) - p["started_t"], 1)}

    def _end(self, reason):
        p = self.p
        if p is None or p["state"] == "ended":
            return
        p.update(state="ended", stop_reason=reason, ended_t=round(time.time(), 2))
        self._event("end", stop_reason=reason)
        p["summary"] = self._summary()
        # Nobody may be left in charge of a standing dog: keep the stand budget watching after the end (except when a
        # person took over: then they are in charge).
        self.after = None if reason in ("human_took_over", "stand_budget") else {"patrol_id": p["patrol_id"]}
        self._save()
        print(f"[patrol] {p['patrol_id']} ended: {reason}", flush=True)

    def touch(self, client):
        """A call from the patrol's client: it is alive (ends a lease-lapse grace)."""
        with self.lock:
            p = self.p
            if p is not None and p["state"] == "grace" and p["client"] == client:
                p["state"] = "halted" if p.get("halt") else "open"
                p["_grace_since"] = None
                self._event("resumed", client=client)
                self._save()

    # ---------- the envelope around the agent tools ----------
    def refusal(self, call, req):
        """{code, detail} if this call from the patrol client may not run now, else None."""
        p = self.p
        if call == "posture" and str(req.get("pose")) == "lie":
            return None
        if call in ("photo", "relocalize", "claim"):
            return None
        if p.get("halt"):
            return dict(p["halt"], detail=f"patrol halted: {p['halt']['detail']}")
        conds = self.conditions()
        if call == "posture":       # standing up is how not_standing is fixed; loc problems don't matter for it
            conds = [c for c in conds if c["code"] not in ("not_standing", "loc_lost", "loc_suspect", "no_map_pose",
                                                           "in_keep_out")]
        return conds[0] if conds else None

    def tool(self, call, client, req):
        """An existing agent tool from the patrol client, through the envelope. (http code, reply)."""
        self.touch(client)
        with self.lock:
            why = self.refusal(call, req)
            if why:
                return self._refuse(why)
            caps = self.caps()
            req = dict(req)
            if call == "move":
                m = float(req["m"])
                if m < 0:
                    if caps["back_m"] < 0.05:
                        return self._refuse({"code": "reverse_budget", "detail": f"the patrol's {PATROL_BACK_TOTAL_M} m "
                                             "of reverse are used up"})
                    if -m > caps["back_m"]:
                        req["m"] = -caps["back_m"]
                        req["clamped_from_m"] = m
            if call == "go_to":
                try:
                    gx, gy, gyaw, _ = self.ag._goal(req)
                except (RuntimeError, KeyError, ValueError, TypeError) as e:
                    return 400, {"result": "error", "reason": f"bad arguments: {e}", "stop_reason": "bad_arguments"}
                code, chk = check([{"x": gx, "y": gy, "yaw_deg": None if gyaw is None else math.degrees(gyaw)}],
                                  self.ag, self.keepout)
                if code != 200:
                    return self._refuse({"code": chk.get("code", "no_route"), "detail": chk.get("error")})
                r = chk["results"][0]
                if not r["ok"]:
                    return self._refuse(r["why"])
            self.interrupted = None
        code, out = self.ag.tool(call, client, req, caps=caps)
        with self.lock:
            if call == "move" and isinstance(out.get("moved_m"), (int, float)) and out["moved_m"] < 0:
                self.p["reverse_used_m"] += -out["moved_m"]
            if isinstance(out.get("moved_m"), (int, float)):
                self.p["walked_m"] = round(self.p["walked_m"] + abs(out["moved_m"]), 2)
            if "clamped_from_m" in req:
                out["clamped"] = {"m": req["m"], "asked_m": req["clamped_from_m"], "why": "reverse cap"}
            self._mark_interrupt(out)
            self._save()
        return code, out

    def _mark_interrupt(self, out):
        if self.interrupted and out.get("result") in ("aborted", "error"):
            out["why"] = self.interrupted
            out["stop_reason"] = self.interrupted["code"]
        self.interrupted = None

    # ---------- the monitor ----------
    def start_monitor(self):
        def loop():
            while True:
                try:
                    self.tick()
                except Exception as e:          # never let the monitor die
                    print(f"[patrol] monitor error: {e!r}", flush=True)
                time.sleep(MONITOR_S)
        self._thread = threading.Thread(target=loop, daemon=True, name="patrol-monitor")
        self._thread.start()
        return self

    def _update_standing(self):
        odom, _, state, ages, *_ = self._sensors()
        now = self.clock()
        if state is None or ages.get("state", 99) > 2.0 or state["body_height"] < MIN_BODY_H:
            self.stand_since = None
            return False
        v = odom["vel"] if odom else [0, 0, 0]
        walking = (math.hypot(v[0], v[1]) > WALK_V_MIN or abs(v[2]) > WALK_W_MIN
                   or now - (self.ag.last_motion or -1e9) < 0.3)
        if walking or self.stand_since is None:
            self.stand_since = now
        return True

    def tick(self):
        """One monitor step. Works out what to do under the lock, then does it (stop or lie down) outside it."""
        act = None
        with self.lock:
            standing = self._update_standing()
            p = self.p
            if p is None:
                return
            if p["state"] == "ended":
                a = self.after
                if a is None:
                    return
                if self.ag.human_seq != p["_human_seq"] or not standing:
                    self.after = None        # a person is in charge, or the dog lay down: nothing left to watch
                    return
                o = self.ag.owner_now()
                if (self._standing_s() >= STAND_BUDGET_S and o is None and self.ag.current is None
                        and not self.hooks["deploying"]()):
                    self.after = None
                    act = ("lie", "stand budget after the patrol ended", None)
            else:
                act = self._open_tick(p, standing)
        if act:
            kind, reason, end = act
            if kind == "stop":
                self._halt_motion(reason)
            elif kind == "lie":
                self._halt_motion(reason)
                ok = self._lie_down(reason)
                with self.lock:
                    if self.p is not None:
                        self._event("lie_down", reason=reason, done=ok)
                        if end:
                            self._end(end)
                        else:
                            self._save()

    def _open_tick(self, p, standing):
        cur = self.ag.current
        mine = cur is not None and cur.get("client") == p["client"]
        # 1. a person took over (or pressed STOP at the console): end now; human_drives already stopped the dog
        o = self.ag.owner_now()
        if self.ag.human_seq != p["_human_seq"] or (o and o["kind"] == "human"):
            self._end("human_took_over")
            return None
        if self.hooks["deploying"]():
            self._end("deploying")
            return None
        # 2. standing budget: lie down and end
        if standing and self._standing_s() >= STAND_BUDGET_S:
            return ("lie", f"patrol {p['patrol_id']}: stood {self._standing_s():.0f} s without walking", "stand_budget")
        # 3. the client's lease
        alive = (o is not None and o["kind"] == "agent" and o["client"] == p["client"]) or mine
        if not alive:
            if p["state"] != "grace":
                p["state"], p["_grace_since"] = "grace", self.clock()
                self._event("lease_lapsed", grace_s=LEASE_GRACE_S)
                self._save()
                return ("stop", f"patrol {p['patrol_id']}: the client's lease lapsed", None)
            if self.clock() - p["_grace_since"] > LEASE_GRACE_S:
                self._end("lease_lapsed")
            return None
        if p["state"] == "grace":           # the lease is back (claim from the same client)
            p["state"], p["_grace_since"] = ("halted" if p.get("halt") else "open"), None
            self._event("resumed")
            self._save()
        # 4. conditions: sticky ones halt the patrol; any of them stops a running motion tool
        if p.get("halt") and not standing:   # halted and lying down: nothing more can happen in this patrol
            self._end(p["halt"]["code"])
            return None
        conds = self.conditions()
        for c in conds:
            if c["code"] in STICKY and not p.get("halt"):
                p["halt"], p["state"] = c, "halted"
                self._event("halt", **c)
                self._save()
        if mine and cur.get("call") in MOTION_CALLS:
            why = p.get("halt") or (conds[0] if conds else None)
            if why and not self.ag.abort.is_set():
                self.interrupted = {"code": why["code"], "detail": why["detail"]}
                self._event("interrupt", call=cur.get("call"), **self.interrupted)
                return ("stop", f"patrol envelope: {why['detail']}", None)
        return None

    def _halt_motion(self, reason):
        """Abort the running tool and stop the dog (Agents.interrupt: abort flag, StopMove / avoid zero move). Skipped
        when the dog is lying with no tool running: StopMove could undo lying down (see Agents.run)."""
        _, _, state, _, _, ages = self.ag.snap()
        lying = state is not None and ages.get("state", 99) < 2.0 and state["body_height"] < MIN_BODY_H
        if lying and self.ag.current is None:
            return
        self.ag.interrupt(reason)

    def _lie_down(self, reason):
        """Lie the dog down as the posture tool does (node.action("lie"): StopMove, then StandDown), holding the tool
        lock so no agent tool runs meanwhile. Not if a person is in charge, the dog fell, or the console is deploying."""
        end = time.monotonic() + LIE_WAIT_S
        while not self.ag.busy.acquire(blocking=False):
            if time.monotonic() > end:
                print(f"[patrol] lie down skipped (a tool did not stop): {reason}", flush=True)
                return False
            self.ag.interrupt(reason)
            time.sleep(0.05)
        try:
            o = self.ag.owner_now()
            _, imu, *_ = self.ag.snap()
            if (o and o["kind"] == "human") or (self.p and self.ag.human_seq != self.p["_human_seq"]) \
                    or self.hooks["deploying"]() or imu is None \
                    or abs(imu["rpy"][0]) > TILT_LIMIT or abs(imu["rpy"][1]) > TILT_LIMIT:
                return False
            print(f"[patrol] lying the dog down: {reason}", flush=True)
            self.ag.node.action("lie")
            return True
        finally:
            self.ag.busy.release()

    # ---------- /agent/view ----------
    def view(self, client, req):
        self.touch(client)
        t_call = time.monotonic()
        with self.lock:
            if not self.owns(client):
                return self._refuse({"code": "no_patrol", "detail": "view only works inside an open patrol of yours "
                                     "(POST /agent/patrol/start)"})
            try:
                x, y = float(req["x"]), float(req["y"])
                yaws = req.get("yaw_deg")
                yaws = [yaws] if isinstance(yaws, (int, float)) else list(yaws or [])
                yaws = [float(v) for v in yaws]
                if len(yaws) > MAX_HEADINGS:
                    raise ValueError(f"at most {MAX_HEADINGS} headings")
                look = req.get("look_deg")
                look = None if look is None else max(-30.0, min(30.0, float(look)))
                settle = max(0.0, min(VIEW_SETTLE_MAX_S, float(req.get("settle_s", VIEW_SETTLE_S))))
                timeout_s = max(5.0, min(VIEW_TIMEOUT_S, float(req.get("timeout_s", VIEW_TIMEOUT_S))))
            except (KeyError, TypeError, ValueError) as e:
                return 400, {"result": "error", "reason": f"bad arguments: {e} (x, y; yaw_deg: number or list; "
                             "look_deg?, settle_s? 0-5)", "stop_reason": "bad_arguments"}
            why = self.refusal("view", req)
            if why:
                return self._refuse(why)
            code, chk = check([{"x": x, "y": y, "yaw_deg": yaws[0] if yaws else None}], self.ag, self.keepout)
            if code != 200:
                return self._refuse({"code": chk.get("code", "no_route"), "detail": chk.get("error")})
            r = chk["results"][0]
            if not r["ok"]:
                return self._refuse(r["why"])
            if yaws and len(yaws) > 1 and r.get("ok_to_turn") is False:   # AUT ask 18:34 #3
                return self._refuse({"code": "turn_clearance",
                                     "detail": f"{len(yaws)} headings need turning in place, but the stand has only "
                                               f"{r['turn_clear_m']} m clear all round (needs {TURN_NEED_M} m)",
                                     "turn_clear_m": r["turn_clear_m"]})
            caps = self.caps()
            self.p["n_views"] += 1
            vid = f"v{self.p['n_views']:03d}_{time.strftime('%H%M%S')}"
            vdir = _mkdir(os.path.join(_mkdir(self._dir("views")), vid))
            url = f"/patrol/{self.p['patrol_id']}/views/{vid}/"
            self.interrupted = None
        plan_s = time.monotonic() - t_call
        info = {"view_id": vid, "patrol_id": self.p["patrol_id"], "t": round(time.time(), 2),
                "goal": {"x": x, "y": y, "yaw_deg": yaws, "look_deg": look, "settle_s": settle},
                "check": {k: r.get(k) for k in ("route_m", "est_s", "goal_used", "snapped_m", "tight", "squeeze", "flags")},
                "caps": caps}
        timing = {"plan_s": round(plan_s, 2), "walk_s": 0.0, "face_s": 0.0, "settle_s": 0.0, "photo_s": 0.0}
        shots = []

        def run():
            deadline = time.monotonic() + timeout_s
            t0 = time.monotonic()
            self.ag._stop_if_lost = True
            try:
                g = self.ag._go_to({"x": x, "y": y}, timeout_s)
            finally:
                self.ag._stop_if_lost = False
            timing["walk_s"] = round(time.monotonic() - t0, 2)
            res = {"walked_m": g.get("moved_m", 0.0), "go_to": {k: g.get(k) for k in ("result", "reason", "route_m",
                                                                                       "replans", "fallback")}}
            if g["result"] != "done":
                return dict(g, **res)
            try:
                for i, yaw in enumerate(yaws or [None]):
                    t0 = time.monotonic()
                    if yaw is not None:
                        mp = self.ag.map_pose_now()
                        d = wrap_deg(yaw - math.degrees(mp["yaw"]))
                        if abs(d) > FACE_TOL_DEG:
                            rt = self.ag._turn(d, max(1.0, deadline - time.monotonic()))
                            if rt["result"] != "done":
                                return dict(rt, **res)
                    face_i = time.monotonic() - t0
                    timing["face_s"] = round(timing["face_s"] + face_i, 2)
                    shot = self._shoot(vdir, f"h{i}", url, look, settle, deadline, timing, yaw)
                    shot["face_s"] = round(face_i, 2)       # this heading's turn (AUT ask 17:52: refit est_face_s)
                    shot["face_from_deg"] = None if yaw is None else round(d if abs(d) > FACE_TOL_DEG else 0.0, 1)
                    shots.append(shot)
            finally:
                if look and not self.ag.abort.is_set():   # level again (walking would level it anyway); not after
                    self.ag.node.look(0.0)                # an abort: a person may have taken over
            return dict(res, result="done")

        code, out = self.ag.run(client, "view", dict(req, client=client), run, caps=caps)
        with self.lock:
            self._mark_interrupt(out)
            b = self.hooks["battery"]()
            mot, mage = self.hooks["motors"]()
            info.update(result=out.get("result"), reason=out.get("reason"), stop_reason=out.get("stop_reason"),
                        why=out.get("why"), walked_m=out.get("walked_m", 0.0), go_to=out.get("go_to"), timing=timing,
                        shots=shots, battery_end=(b or {}).get("soc"),
                        hottest_motor_c_end=mot.get("max") if mot and mage <= MOTOR_STALE_S else None,
                        urls={"view_json": url + "view.json", "patrol": f"/patrol/{self.p['patrol_id']}"},
                        envelope=self._envelope())
            self.p["walked_m"] = round(self.p["walked_m"] + float(out.get("walked_m") or 0.0), 2)
            self._event("view", view_id=vid, result=out.get("result"), stop_reason=out.get("stop_reason"))
            try:
                _write_json(os.path.join(vdir, "view.json"), info)
            except OSError as e:
                info["save_error"] = repr(e)
            self._save()
        reply = dict(out, **{k: v for k, v in info.items() if k not in ("result", "reason", "stop_reason")})
        reply["result"], reply["stop_reason"] = out.get("result"), out.get("stop_reason")
        if req.get("inline"):
            for s in reply["shots"]:
                s["inline"] = {}
                for k, rel in (s.get("files") or {}).items():
                    try:
                        with open(os.path.join(vdir, rel), "rb") as f:
                            s["inline"][k] = base64.b64encode(f.read()).decode()
                    except OSError:
                        pass
        return code, reply

    def _shoot(self, vdir, prefix, url, look, settle, deadline, timing, yaw):
        """Optional camera tilt, settle (tracking stillness), then capture. Runs inside the view's tool call."""
        _, imu0, *_ = self.ag.snap()
        pitch0 = imu0["rpy"][1] if imu0 else None
        t0 = time.monotonic()
        if look:
            self.ag.node.look(math.radians(look))
        recent = deque()                         # (t, v, w) over the last STILL_WINDOW_S
        last_head = time.monotonic()
        end = time.monotonic() + settle
        hard_end = end + STILL_EXTRA_S
        while True:
            now = time.monotonic()
            if now >= hard_end:
                break
            if self.ag.abort.is_set():
                raise _aborted(self.ag)
            odom = self.ag.snap()[0]
            if odom:
                recent.append((now, math.hypot(odom["vel"][0], odom["vel"][1]), abs(odom["vel"][2])))
            while recent and now - recent[0][0] > STILL_WINDOW_S:
                recent.popleft()
            calm = (recent and now - recent[0][0] >= STILL_WINDOW_S * 0.8
                    and all(v < STILL_V and w < STILL_W for _, v, w in recent))
            if now >= end and calm:
                break
            if look and time.monotonic() - last_head >= LOOK_REFRESH_S:
                self.ag.node.send_head()          # the pitch springs back by itself otherwise (10-23, 11-18)
                last_head = time.monotonic()
            time.sleep(0.05)
        timing["settle_s"] = round(timing["settle_s"] + time.monotonic() - t0, 2)
        self.ag.tick(deadline)                    # fallen / lying / stale / lost: no photo, the call ends
        vmax = max((v for _, v, _ in recent), default=None)
        wmax = max((w for _, _, w in recent), default=None)
        t1 = time.monotonic()
        shot = self._capture(vdir, prefix, url, still_vw=(vmax, wmax))
        timing["photo_s"] = round(timing["photo_s"] + time.monotonic() - t1, 2)
        pitch1 = shot.get("body_pitch_deg")
        shot.update(yaw_deg=yaw, look_deg=look, body_pitch_before_deg=None if pitch0 is None else round(math.degrees(pitch0), 1))
        if look and pitch0 is not None and pitch1 is not None:
            delta = pitch1 - math.degrees(pitch0)
            shot["look_pitch_change_deg"] = round(delta, 1)
            shot["look_held"] = abs(delta) >= LOOK_HELD_FRAC * abs(look)
        return shot

    def _capture(self, d, prefix, url, still_vw=None):
        """Dog camera (full size) + the L515 frame closest to it + pose/loc/markers, written to directory d."""
        ag = self.ag
        with ag.lock:
            img, ft = ag.full["img"], ag.full["t"]
        if img is None or time.time() - ft > CAM_MAX_AGE_S:
            raise RuntimeError("no_camera_frame: the dog camera has no recent frame")
        odom, imu, state, cloud, _, ages = ag.snap()
        import cv2
        files = {}
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 92])
        with open(os.path.join(d, f"{prefix}_dog.jpg"), "wb") as f:
            f.write(buf.tobytes())
        files["dog"] = f"{prefix}_dog.jpg"
        lr = self.l515.closest(ft)
        l515 = None
        if lr is not None:
            ok, png = cv2.imencode(".png", lr["depth"])
            with open(os.path.join(d, f"{prefix}_l515_depth.png"), "wb") as f:
                f.write(png.tobytes())
            files["l515_depth"] = f"{prefix}_l515_depth.png"
            if lr["color_jpeg"]:
                with open(os.path.join(d, f"{prefix}_l515_color.jpg"), "wb") as f:
                    f.write(lr["color_jpeg"])
                files["l515_color"] = f"{prefix}_l515_color.jpg"
            l515 = {k: v for k, v in lr.items() if k not in ("depth", "color_jpeg")}
            l515.update(depth_shape=list(lr["depth"].shape), depth_units="mm (16UC1 from the receiver)")
        for k in files.values():
            _chown(os.path.join(d, k))
        mp = ag.map_pose_now()
        li = ag.mapper.loc_info(track_n=0) if ag.mapper is not None else {}
        mk = self.hooks["markers"]() or {}
        mk_t = mk.get("frame_t")
        sightings = mk.get("list", []) if mk_t and abs(mk_t - ft) <= 0.5 else []
        v = odom["vel"] if odom else None
        if still_vw is None:
            still_vw = (math.hypot(v[0], v[1]), abs(v[2])) if v else (None, None)
        still = None if still_vw[0] is None else bool(still_vw[0] < STILL_V and still_vw[1] < STILL_W)
        return {"t": round(ft, 3), "files": files, "urls": {k: url + f for k, f in files.items()},
                "dog": {"t": round(ft, 3), "width": int(img.shape[1]), "height": int(img.shape[0]),
                        "camera_info": self.l515.dog_info()},
                "l515": l515,
                "pose": None if mp is None else {"x": round(mp["x"], 3), "y": round(mp["y"], 3),
                                                  "yaw_deg": round(math.degrees(mp["yaw"]), 1)},
                "odom_age_s": round(ages.get("odom", 99), 2),
                "clearance": front_clearance(odom, cloud, ages.get("cloud")),
                "loc": {"map_id": ag.mapper.saved_at if ag.mapper is not None else None,
                        "track_fit": li.get("track_fit"), "fresh_fit": li.get("fresh_fit"),
                        "lost": li.get("lost"), "suspect": li.get("suspect")},
                "markers": {"frame_t": mk_t, "list": sightings},
                "look_deg_cmd": round(math.degrees(getattr(ag.node, "head", 0.0))),
                "body_pitch_deg": round(math.degrees(imu["rpy"][1]), 1) if imu else None,
                "body_height": state["body_height"] if state else None,
                "still": still, "max_speed_before_shutter": {"v": None if still_vw[0] is None else round(still_vw[0], 3),
                                                            "w": None if still_vw[1] is None else round(still_vw[1], 3)}}


def wrap_deg(a):
    return (a + 180.0) % 360.0 - 180.0


def _aborted(ag):
    from go2_agent import Aborted
    return Aborted(ag.abort_reason or "stopped")


# ---------- step 4: /patrol/views (geometry only: candidates, what was seen from near them, walk length) ----------
VIEW_GRID_M = 1.0          # sampled candidates: one free cell per this many metres
VIEW_HEADINGS = 8          # headings per sampled cell
VIEW_CLEAR_M = 0.35        # sampled cells need at least this clearance (planner ROBOT_R 0.28 + margin)
SEEN_R_M, SEEN_DEG = 0.5, 30.0   # a frame counts as "seen from here" within this distance and heading
SEEN_RULE = ("2-D, pose-matched: trail/view frames taken within 0.5 m and 30 deg of the candidate pose. "
             "Not a visibility model; cheetah's 2.5-D model is the reference.")


def _geodesic(planner, sx, sy, rr=0.28):
    """Walk length (m) from (sx, sy) to every planning cell with clearance >= rr, 8-connected Dijkstra on the planner
    grid. Returns (dist array or None, why)."""
    try:
        from scipy.sparse import csr_matrix
        from scipy.sparse.csgraph import dijkstra
    except ImportError:
        return None, "scipy missing"
    with planner.lock:
        planner._grid()
        if planner.occ is None:
            return None, "no map"
        free = planner.dist >= rr
        cell = 0.10
        sr, sc = planner.cell(sx, sy)
        if not planner.inside(sr, sc):
            return None, "the dog is off the map"
        free = free.copy()
        free[sr, sc] = True
    h, w = free.shape
    idx = -np.ones(free.shape, np.int64)
    n = int(free.sum())
    idx[free] = np.arange(n)
    rows, cols, wts = [], [], []
    for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
        r0, r1 = (0, h - dr) if dr >= 0 else (-dr, h)
        c0, c1 = (0, w - dc) if dc >= 0 else (-dc, w)
        A = free[r0:r1, c0:c1]
        B = free[r0 + dr:r1 + dr, c0 + dc:c1 + dc]
        both = A & B
        ia = idx[r0:r1, c0:c1][both]
        ib = idx[r0 + dr:r1 + dr, c0 + dc:c1 + dc][both]
        d = cell * math.hypot(dr, dc)
        rows += [ia, ib]
        cols += [ib, ia]
        wts += [np.full(len(ia), d), np.full(len(ia), d)]
    g = csr_matrix((np.concatenate(wts), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))
    dd = dijkstra(g, directed=False, indices=int(idx[sr, sc]))
    out = np.full(free.shape, np.inf)
    out[free] = dd
    return out, None


def _seen(points, x, y, yaw):
    """(n frames, last t) of trail/view frames taken near pose (x, y, yaw)."""
    n, last = 0, None
    for p in points:
        if abs(p[1] - x) > SEEN_R_M or abs(p[2] - y) > SEEN_R_M:
            continue
        if math.hypot(p[1] - x, p[2] - y) > SEEN_R_M or abs(math.degrees(_wrap(p[3] - yaw))) > SEEN_DEG:
            continue
        n += 1
        last = p[0] if last is None else max(last, p[0])
    return n, last


def views(agent, keepout, trail, places, prior_dir, patrols=None, sampled=True, limit=400):
    """Candidate viewpoints with geometry: source, keep-out, what was seen from near them, walk length and est_s from
    the dog now (when lined up). Value (what is worth looking at) is the patrol brain's job, not this."""
    cands = []
    for pid, p in (places or {}).items():
        if "x" in p and "y" in p:
            cands.append({"x": p["x"], "y": p["y"], "yaw_deg": p.get("yaw_deg", 0.0), "source": f"place:{pid}"})
    try:
        with open(os.path.join(prior_dir, "dwell_views.json")) as f:
            spots = json.load(f)["spots"].get("human+unattributed") or []
        for s in spots:
            cands.append({"x": s["x"], "y": s["y"], "yaw_deg": s["yaw_deg"], "source": "dwell",
                          "dwell": {k: s.get(k) for k in ("count", "dwell_s", "nearest_place", "first_seen",
                                                          "last_seen", "windows") if k in s}})
    except (OSError, ValueError, KeyError):
        pass
    mp = agent.map_pose_now()
    planner = agent.planner
    geo, geo_why = (None, "not lined up with the map") if mp is None else _geodesic(planner, mp["x"], mp["y"])
    if sampled and planner is not None:
        with planner.lock:
            planner._grid()
            dist = None if planner.occ is None else planner.dist.copy()
            step = max(1, int(round(VIEW_GRID_M / 0.10)))
        if dist is not None:
            for r0 in range(0, dist.shape[0], step):          # the most open cell of each VIEW_GRID_M block
                for c0 in range(0, dist.shape[1], step):
                    blk = dist[r0:r0 + step, c0:c0 + step]
                    if blk.size == 0 or blk.max() < VIEW_CLEAR_M:
                        continue
                    br, bc = np.unravel_index(int(np.argmax(blk)), blk.shape)
                    x, y = planner.xy(r0 + br, c0 + bc)
                    for k in range(VIEW_HEADINGS):
                        cands.append({"x": round(x, 2), "y": round(y, 2),
                                      "yaw_deg": round(-180 + k * 360.0 / VIEW_HEADINGS, 1), "source": "sampled"})
    with trail.lock:
        pts = [p[:4] for p in trail.points]
    if patrols is not None:
        pts += patrols.view_points()
    out = []
    for cnd in cands:
        x, y, yaw = float(cnd["x"]), float(cnd["y"]), math.radians(float(cnd["yaw_deg"]))
        n, last = _seen(pts, x, y, yaw)
        cnd.update(seen_n=n, last_seen_t=last)
        z = keepout.hit(x, y, margin=0.2)
        if z:
            cnd.update(refuse={"code": "keep_out", "detail": f"inside keep-out zone {z['id']}"})
        if geo is not None:
            r, c = planner.cell(x, y)
            d = geo[r, c] if planner.inside(r, c) else math.inf
            if math.isfinite(d):
                cnd["route_m"] = round(float(d), 2)
                cnd["est_s"] = round(WALK_BY_SPEED["slow"][1] + d / WALK_BY_SPEED["slow"][0] + SETTLE_S, 1)
            elif "refuse" not in cnd:
                cnd["refuse"] = {"code": "no_route", "detail": "no walkable path at the planner's normal clearance "
                                                               "(the full /patrol/check may still find a tight one)"}
        out.append(cnd)
    out.sort(key=lambda v: (v["source"] == "sampled", v.get("route_m", 1e9)))
    return {"from": None if mp is None else {"x": round(mp["x"], 2), "y": round(mp["y"], 2)},
            "route_note": geo_why or "route_m: 8-connected walk on the planning grid at 0.28 m clearance, no turns; "
                                      "use /patrol/check for the planner's real route and refusals",
            "seen_rule": SEEN_RULE, "n": len(out), "candidates": out[:limit], "truncated": len(out) > limit,
            "map_id": getattr(agent.mapper, "saved_at", None)}


def prior(prior_dir):
    """The driving prior (Oliver's hand driving, 11-21 analysis) as one JSON."""
    try:
        with open(os.path.join(prior_dir, "prior.json")) as f:
            p = json.load(f)
        with open(os.path.join(prior_dir, "dwell_views.json")) as f:
            d = json.load(f)
    except (OSError, ValueError) as e:
        return None, str(e)
    return {"prior": p, "dwell_views": d, "report": "/patrol/prior/REPORT.md", "map": "/patrol/prior/paths.png",
            "note": "dwell = where Oliver stopped; it reflects what he was recording, not what is worth looking at"}, None
