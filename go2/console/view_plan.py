"""Where to stand to photograph a thing: ranked candidate viewpoints around its map position.

The goal is a picture that shows the thing, not a fixed standing spot. Candidates are positions on rings around
the thing, the dog facing it. Each must be enterable on the graded-cost grid (nav_proto.Grid: hard block within
0.20 m of an obstacle), have a straight line of sight to the thing on the map, and be reachable from the dog.
Ranking:
- view distance close to what the thing needs: its width should fill 25-60% of the 73 deg picture, and its top
  must be inside the view (camera at 0.4 m, 16 deg tilt up at most, vertical field of view about 45 deg);
- clearance (more room = the dog gets there and can turn);
- walking cost from the dog (a tie-breaker);
- past confirmed views of this thing (go2/data/views.json) come first.
    from view_plan import viewpoints;  viewpoints(grid, dist_from_dog, target_xy, width_m, top_m, k=6)
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HFOV, VFOV, CAM_H, MAX_TILT = 73.0, 45.0, 0.40, 16.0
VIEWS = Path(__file__).resolve().parents[1] / "data" / "views.json"


def need_distance(width_m, top_m):
    """Closest and best distance: the thing fits the picture's width, and its top fits under the view's top edge."""
    fit_w = (width_m / 2) / math.tan(math.radians(HFOV / 2) * 0.8)            # fills ~80% of the width
    top_angle = math.radians(MAX_TILT + VFOV / 2 - 3)
    fit_top = max(0.0, (top_m - CAM_H) / math.tan(top_angle))
    near = max(0.5, fit_w * 0.6, fit_top)
    best = max(near, (width_m / 2) / math.tan(math.radians(HFOV / 2) * 0.45))  # fills ~45%
    tilt = 0.0 if top_m - CAM_H < best * math.tan(math.radians(VFOV / 2 - 3)) else MAX_TILT
    return near, best, tilt


def known_views(name):
    try:
        return json.loads(VIEWS.read_text()).get(name, [])
    except Exception:  # noqa: BLE001
        return []


def remember_view(name, pose, photo_url, why):
    d = json.loads(VIEWS.read_text()) if VIEWS.exists() else {}
    d.setdefault(name, []).insert(0, {"x": pose["x"], "y": pose["y"], "yaw_deg": round(math.degrees(pose["yaw"]), 1),
                                     "photo": photo_url, "why": why})
    d[name] = d[name][:5]
    VIEWS.write_text(json.dumps(d, indent=1))


def viewpoints(G, g, target, width_m=0.5, top_m=0.6, k=6, name=None):
    near, best, tilt = need_distance(width_m, top_m)
    tc = G.cell(*target)
    out = []
    for v in known_views(name) if name else []:
        out.append({**v, "tilt_deg": tilt, "source": "confirmed before", "score": -1.0})
    for r in np.arange(near, max(near, best) + 0.81, 0.2):
        for a in range(0, 360, 15):
            x = target[0] + r * math.cos(math.radians(a))
            y = target[1] + r * math.sin(math.radians(a))
            c = G.cell(x, y)
            if not G.ok(c) or not np.isfinite(g[c]) or not G.line_of_sight(c, tc):
                continue
            score = 1.0 * abs(r - best) + 1.5 * max(0.0, 0.45 - G.dist[c]) + 0.03 * g[c]
            out.append({"x": round(float(x), 2), "y": round(float(y), 2), "yaw_deg": round(
                        math.degrees(math.atan2(target[1] - y, target[0] - x)), 1), "dist_m": round(float(r), 2),
                        "clearance_m": round(float(G.dist[c]), 2), "tilt_deg": tilt, "source": "sampled",
                        "score": round(float(score), 3)})
    out.sort(key=lambda v: v["score"])
    picked = []
    for v in out:            # spread the choices: no two within 0.4 m of each other
        if all(math.hypot(v["x"] - p["x"], v["y"] - p["y"]) > 0.4 for p in picked):
            picked.append(v)
        if len(picked) >= k:
            break
    return picked
