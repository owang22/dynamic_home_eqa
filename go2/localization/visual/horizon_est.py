"""Estimate the real horizon row of the level camera (look 0) from vanishing points of depth lines.

For each trusted look-0 trail frame: undistort (720p calibration scaled to 640x360), detect line segments (LSD),
keep long segments that are neither near-vertical nor near-horizontal, intersect pairs, and keep the vertical
coordinate of intersections that fall near the image centre column (|x - cx| < 150 px). The horizon is where the
vanishing points of floor/ceiling lines (all parallel to the floor) lie; its row gives the camera pitch.
    python3 horizon_est.py   -> results/horizon_est.json
"""
import json, math
import cv2, numpy as np
import vcommon as V

R = [r for r in V.load_records() if r["trusted"] and r["look_deg"] == 0]
K = V.K_for(640, 360, eff=False)
newK = K.copy()
lsd = cv2.createLineSegmentDetector()
vps = []
per_frame = []
for r in R[::3]:
    im = cv2.imread(r["path"], cv2.IMREAD_GRAYSCALE)
    im = cv2.resize(im, (640, 360))
    u = cv2.undistort(im, K, V.DIST720, None, newK)
    L = lsd.detect(u)[0]
    if L is None:
        continue
    L = L[:, 0]
    d = L[:, 2:] - L[:, :2]
    ln = np.hypot(d[:, 0], d[:, 1])
    ang = np.degrees(np.arctan2(np.abs(d[:, 1]), np.abs(d[:, 0])))
    keep = (ln > 40) & (ang > 8) & (ang < 70)
    L = L[keep]
    ys = []
    for i in range(len(L)):
        for j in range(i + 1, len(L)):
            p1, p2, p3, p4 = L[i, :2], L[i, 2:], L[j, :2], L[j, 2:]
            a1 = np.cross(np.append(p1, 1), np.append(p2, 1)); a2 = np.cross(np.append(p3, 1), np.append(p4, 1))
            x = np.cross(a1, a2)
            if abs(x[2]) < 1e-9:
                continue
            x = x[:2] / x[2]
            # lines must converge from opposite sides (one going up-right, the other up-left) to be depth lines
            s1 = np.sign(d[keep][i, 0] * d[keep][i, 1]); s2 = np.sign(d[keep][j, 0] * d[keep][j, 1])
            if s1 == s2:
                continue
            if abs(x[0] - K[0, 2]) < 150 and 100 < x[1] < 300:
                ys.append(x[1])
    if len(ys) >= 5:
        per_frame.append(float(np.median(ys)))
        vps += ys
pitch = [math.degrees(math.atan((y - K[1, 2]) / K[1, 1])) for y in per_frame]
out = {"frames": len(per_frame), "vp_row_median_undistorted": float(np.median(per_frame)),
       "vp_row_iqr": [float(np.percentile(per_frame, 25)), float(np.percentile(per_frame, 75))],
       "cy": float(K[1, 2]), "pitch_down_deg_median": float(np.median(pitch))}
print(out)
json.dump(out, open("results/horizon_est.json", "w"), indent=1)
