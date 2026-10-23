"""Report figure: cross-day queries (10-22) with the top-1 10-20 picture retrieved from the full frame and from
the upper crop (line at row 162 marks the crop). Picks cases where (a) both right, (b) only upper right,
(c) only full right, (d) both wrong. Writes figs/xday_<case>.jpg.
"""
import numpy as np, cv2
import vcommon as V, vpr_eval as E, montage_util as M

R = V.load_records()
q, db, _ = E.splits(R, "clean")["x_22v20"]
pos, dist, ang = E.gt(R, q, db)
rf = np.load("cache/rank_clean_dino_vlad_full_x_22v20.npy"); ru = np.load("cache/rank_clean_dino_vlad_upper_x_22v20.npy")
has = pos.any(1)
cf = pos[np.arange(len(q)), rf[:, 0]]; cu = pos[np.arange(len(q)), ru[:, 0]]
cases = {"both_right": has & cf & cu, "only_upper_right": has & ~cf & cu, "only_full_right": has & cf & ~cu, "both_wrong": has & ~cf & ~cu}
rng = np.random.default_rng(5)
for name, m in cases.items():
    idx = np.where(m)[0]
    print(name, len(idx))
    tiles = []
    for i in rng.choice(idx, min(4, len(idx)), replace=False):
        a = R[q[i]]; f = R[db[rf[i, 0]]]; u = R[db[ru[i, 0]]]
        g = lambda ok: (0, 200, 0) if ok else (0, 0, 255)
        tiles += [M.tile(a["path"], f"query 10-22 {a['time'][-5:]} ({a['x']:.1f},{a['y']:.1f}) {a['yaw_deg']:.0f}", 426, 240, lines=[(162, (0, 255, 255))]),
                  M.tile(f["path"], f"full top-1: {dist[i, rf[i, 0]]:.1f} m, {ang[i, rf[i, 0]]:.0f} deg", 426, 240, border=g(cf[i])),
                  M.tile(u["path"], f"upper top-1: {dist[i, ru[i, 0]]:.1f} m, {ang[i, ru[i, 0]]:.0f} deg", 426, 240, lines=[(162, (0, 255, 255))], border=g(cu[i]))]
    cv2.imwrite(f"figs/xday_{name}.jpg", M.grid(tiles, 3), [cv2.IMWRITE_JPEG_QUALITY, 82])
