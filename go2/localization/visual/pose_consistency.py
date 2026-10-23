"""How consistent are the console yaws (and positions) between pictures of the same place? (ground-truth check)

For each trusted picture, its 10 nearest DINOv2-VLAD (full frame) neighbours among trusted pictures (excluding the
same session within 60 s) are verified with SIFT + essential matrix (effective K). For verified pairs (>= 60
inliers, console positions within 1.5 m) the image relative yaw is compared with the console yaw difference.
Output: results/pair_yaw.json (all verified pairs) and a per day-pair table of |console dyaw - image dyaw|.
    python3 pose_consistency.py
"""
import json, math, collections
import numpy as np
import vcommon as V, vpr_eval as E, geo

R = V.load_records()
ids = [r["id"] for r in R]
D = E.load_desc("", "full", ids, [r["day"] in ("10-19", "10-20") for r in R])
S = D["dino_vlad"]
tr = np.array([r["trusted"] for r in R]); T = np.array([r["t"] for r in R])
idx = np.where(tr)[0]
sim = S[idx] @ S[idx].T
sess = np.array([str(R[i]["session"]) for i in idx])
excl = (np.abs(T[idx][:, None] - T[idx][None]) < 60) & (sess[:, None] == sess[None]) | np.eye(len(idx), dtype=bool)
sim[excl] = -9
done = set(); pairs = []
for a in range(len(idx)):
    for b in np.argsort(-sim[a])[:10]:
        key = (min(a, b), max(a, b))
        if key in done: continue
        done.add(key)
        ra, rb = R[idx[key[0]]], R[idx[key[1]]]
        dpos = math.hypot(ra["x"] - rb["x"], ra["y"] - rb["y"])
        if dpos > 1.5: continue
        o = geo.rel_pose(ra, rb)
        if o["inl"] < 60: continue
        cy = float(V.wrap_deg(rb["yaw_deg"] - ra["yaw_deg"]))
        pairs.append({"a": ra["id"], "b": rb["id"], "da": ra["day"], "db": rb["day"], "ta": ra["time"][-5:], "tb": rb["time"][-5:],
                      "dpos": dpos, "console_dyaw": cy, "image_dyaw": o["yaw"], "err": float(V.wrap_deg(cy - o["yaw"])),
                      "inl": o["inl"], "rot_only": o["rot_only"], "bearing": o["bearing"]})
json.dump(pairs, open("results/pair_yaw.json", "w"), indent=1)
g = collections.defaultdict(list)
for p in pairs:
    g[tuple(sorted((p["da"], p["db"])))].append(abs(p["err"]))
print("day pair: n, median |console - image| yaw, p75, p90, share > 10 deg")
for k in sorted(g):
    v = np.array(g[k]); print(k, len(v), np.median(v).round(1), np.percentile(v, 75).round(1), np.percentile(v, 90).round(1), (v > 10).mean().round(2))
