"""AUT ask 19:36: move the dwell spots (prior.json dwell_spots/parks_top, dwell_views.json) from the old (10-23) map frame
to the 19:29 map, with the same per-node correction moves.py used for places (median rigid correction of the matched
graph nodes within 0.75 m, or the nearest, heading too). Reads the live lab_prior files, writes converted copies here."""
import copy, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import HERE, wrap
from rebuild_1121 import frame, poses

run = "r2"; F = frame(os.path.join(HERE, "out", run, "frame.json"))
sessions = json.load(open(os.path.join(HERE, "out", run, "sessions.json")))
I, X = [], []
for s in sessions:
    if os.path.exists(os.path.join(HERE, "track", f"fix_{s}.npz")):
        continue
    T = np.load(os.path.join(HERE, "track", f"old_{s}.npz")); P = poses(run, s, F)["node"]
    ok = (T["src"] == 1) & np.isfinite(T["X"][:, 0]); I.append(T["X"][ok]); X.append(P[ok])
I, X = np.vstack(I), np.vstack(X)

def move(p):
    p = np.asarray(p, float); d = np.hypot(I[:, 0] - p[0], I[:, 1] - p[1])
    near = np.nonzero(d < max(0.75, d.min() + 0.05))[0]
    res = []
    for k in near:
        th = wrap(X[k, 2] - I[k, 2]); c, s = math.cos(th), math.sin(th); dd = p - I[k, :2]
        res.append((X[k, :2] + np.array([c * dd[0] - s * dd[1], s * dd[0] + c * dd[1]]), th))
    return np.median([r[0] for r in res], 0), float(np.median([r[1] for r in res])), float(d.min()), len(near)

shifts = []
def fix(spot):
    q, th, dmin, n = move([spot["x"], spot["y"]])
    shifts.append(math.hypot(q[0] - spot["x"], q[1] - spot["y"]))
    spot["old_frame"] = {"x": spot["x"], "y": spot["y"], "yaw_deg": spot.get("yaw_deg")}
    spot["x"], spot["y"] = round(float(q[0]), 3), round(float(q[1]), 3)
    if spot.get("yaw_deg") is not None:
        spot["yaw_deg"] = round(math.degrees(wrap(math.radians(spot["yaw_deg"]) + th)), 1)
    spot["converted"] = {"to_map": "2026-11-21 19:29:40", "nearest_node_m": round(dmin, 2), "nodes": n}

LP = "/home/nesl/oliver/go2_maps/lab_prior"
dv = json.load(open(os.path.join(LP, "dwell_views.json"))); pr = json.load(open(os.path.join(LP, "prior.json")))
for d in (dv, pr):
    spots = d["spots"] if "spots" in d else d["dwell_spots"]
    for bucket in spots.values():
        for sp in bucket:
            fix(sp)
for sp in pr.get("parks_top", []):
    fix(sp)
note = "converted to the 19:29 map (2026-11-21) by per-node correction (remap_1121/moves.py rule); old values in old_frame"
dv["frame"] = pr["frame"] = note
out = os.path.dirname(os.path.abspath(__file__))
json.dump(dv, open(os.path.join(out, "dwell_views.json"), "w"), indent=1); json.dump(pr, open(os.path.join(out, "prior.json"), "w"), indent=1)
a = np.array(shifts); print(f"converted {len(a)} spots: shift p50 {np.median(a):.2f} m, p90 {np.percentile(a, 90):.2f}, max {a.max():.2f}")
