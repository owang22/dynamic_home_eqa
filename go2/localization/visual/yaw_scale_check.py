"""Independent check of odom yaw scale vs the camera: pairs of trail frames at the same spot separated by a full
turn. If odom is right, (unwrapped odom yaw change) = 360 * n + (image-estimated residual rotation).
Residual rotations are small, so this is insensitive to the focal length.
    python3 yaw_scale_check.py -> results/yaw_scale_check.json
"""
import json, math
import numpy as np
import vcommon as V, geo

R = V.load_records()
S = V._sessions()
T = [r for r in R if r["source"] == "trail" and r["session"]]
rows = []
by = {}
for r in T:
    by.setdefault(r["session"], []).append(r)
for sess, fr in by.items():
    tt, od, mp = S[sess]
    uy = np.degrees(np.unwrap(od[:, 3]))
    idx = np.clip(np.searchsorted(tt, [r["t"] for r in fr]), 0, len(tt) - 1)
    for i in range(len(fr)):
        for j in range(i + 1, len(fr)):
            if fr[j]["t"] - fr[i]["t"] > 180: break
            dpos = math.hypot(*(od[idx[j], :2] - od[idx[i], :2]))
            dy = uy[idx[j]] - uy[idx[i]]
            n = round(dy / 360)
            if n == 0 or dpos > 0.25 or abs(dy - 360 * n) > 40: continue
            o = geo.rel_pose(fr[i], fr[j])
            if o["inl"] < 40: continue
            true = 360 * n + o["yaw"]
            rows.append({"session": sess, "a": fr[i]["id"], "b": fr[j]["id"], "dt": fr[j]["t"] - fr[i]["t"],
                         "dpos": dpos, "odom_deg": dy, "image_residual": o["yaw"], "true_deg": true,
                         "ratio": dy / true, "inl": o["inl"]})
r = np.array([x["ratio"] for x in rows])
summ = {"n_pairs": len(rows), "sessions": sorted(set(x["session"] for x in rows)),
        "ratio_median": float(np.median(r)) if len(r) else None,
        "ratio_iqr": [float(np.percentile(r, 25)), float(np.percentile(r, 75))] if len(r) else None}
per = {}
for x in rows: per.setdefault(x["session"], []).append(x["ratio"])
summ["per_session_median"] = {k: [len(v), round(float(np.median(v)), 4)] for k, v in per.items()}
print(json.dumps(summ, indent=1))
json.dump({"summary": summ, "pairs": rows}, open("results/yaw_scale_check.json", "w"), indent=1)
