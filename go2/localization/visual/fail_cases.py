"""Failure cases of retrieval (task 2): for a split / descriptor / crop, how many top-1 failures are nevertheless
geometrically verified (same scene, SIFT+E >= 40 inliers) and how far apart the console poses say they are.
Writes a montage of failures: query | top-1 | nearest true positive.
    python3 fail_cases.py within_10-22 dino_vlad full [gt=clean]
"""
import sys, math, json
import numpy as np, cv2
import vcommon as V, vpr_eval as E, geo, montage_util as M

sn, dn, crop = sys.argv[1:4]
gtk = sys.argv[4] if len(sys.argv) > 4 else "clean"
R = V.load_records(); ids = [r["id"] for r in R]
q, db, excl = E.splits(R, gtk)[sn]
rank = np.load(f"cache/rank_{gtk}_{dn}_{crop}_{sn}.npy")
pos, dist, ang = E.gt(R, q, db)
if excl is not None: pos = pos & ~excl
has = pos.any(1)
fails = [i for i in range(len(q)) if has[i] and not pos[i, rank[i, 0]]]
ver, info = 0, []
for i in fails:
    a, b = R[q[i]], R[db[rank[i, 0]]]
    o = geo.rel_pose(a, b)
    v = o["inl"] >= 40
    ver += v
    info.append((i, v, dist[i, rank[i, 0]], ang[i, rank[i, 0]], o["inl"]))
d = np.array([x[2] for x in info]); an = np.array([x[3] for x in info]); vv = np.array([x[1] for x in info])
print(f"{sn} {dn} {crop}: {len(fails)} top-1 failures of {has.sum()}; verified same scene: {ver} ({ver/len(fails):.0%})")
print("  verified failures: console dist med %.2f m, yaw diff med %.0f deg; unverified: dist med %.2f, yaw %.0f" % (
    np.median(d[vv]) if vv.any() else np.nan, np.median(an[vv]) if vv.any() else np.nan, np.median(d[~vv]), np.median(an[~vv])))
print("  verified failures with dist<=1 (yaw>30):", int((vv & (d <= 1)).sum()), " dist 1-2 m:", int((vv & (d > 1) & (d <= 2)).sum()), " >2 m:", int((vv & (d > 2)).sum()))
rng = np.random.default_rng(1)
pick = rng.choice(len(info), min(6, len(info)), replace=False)
tiles = []
for k in pick:
    i, v, dd, aa, inl = info[k]
    a = R[q[i]]; b = R[db[rank[i, 0]]]
    j = np.where(pos[i])[0]; j = j[np.argmin(dist[i, j])]; c = R[db[j]]
    tiles += [M.tile(a["path"], f"Q {a['id'][-7:]} {a['day']} {a['time'][-5:]} ({a['x']:.1f},{a['y']:.1f}) {a['yaw_deg']:.0f}", 426, 240),
              M.tile(b["path"], f"top1 {b['day']} {b['time'][-5:]} d={dd:.1f}m dyaw={aa:.0f} inl={inl}", 426, 240, border=(0, 0, 255) if not v else (0, 200, 255)),
              M.tile(c["path"], f"true {c['day']} {c['time'][-5:]} d={dist[i, j]:.1f}m dyaw={ang[i, j]:.0f}", 426, 240, border=(0, 200, 0))]
cv2.imwrite(f"figs/fail_{sn}_{dn}_{crop}.jpg", M.grid(tiles, 3), [cv2.IMWRITE_JPEG_QUALITY, 80])
