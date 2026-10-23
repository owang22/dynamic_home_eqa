"""Are a session's console poses in the saved map's frame? Hit rate (cloud cells 0.4-1.1 m within 0.1 m of a
map wall) at the console pose vs at perturbed poses."""
import sys, math, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common, jumps
from scipy import ndimage
M = common.load_map(); occ = (M == 0)[::-1]
dist = ndimage.distance_transform_edt(~occ) * 0.05
def look(xy):
    c = np.floor((xy[:, 0] + 6.85) / 0.05).astype(int); r = np.floor((xy[:, 1] + 5.4) / 0.05).astype(int)
    ok = (c >= 0) & (c < 283) & (r >= 0) & (r < 289); v = np.full(len(xy), 9.0); v[ok] = dist[r[ok], c[ok]]; return v
for s in common.sessions():
    d = common.load(s); m = d['map']
    if np.isnan(m[:, 0]).mean() > 0.9: print(s, 'no map pose'); continue
    o, v, w = jumps.motion(d, 0)
    hits = []; pert = []
    for i in range(0, len(d['c_row']), max(1, len(d['c_row']) // 40)):
        r = d['c_row'][i]
        if np.isnan(m[r, 0]) or v[r] > 0.1 or w[r] > 0.1: continue
        ob, _ = common.cloud(d, i); ob = ob[(ob[:, 2] >= 0.4) & (ob[:, 2] < 1.1)][:, :2].astype(float)
        if len(ob) < 50: continue
        T = common.compose(m[r], common.inverse(o[r]))
        hits.append(np.mean(look(common.transform_pts(T, ob)) <= 0.1))
        ph = []
        for dth in (-20, 20):
            P = m[r].copy(); P[2] += math.radians(dth)
            T2 = common.compose(P, common.inverse(o[r])); ph.append(np.mean(look(common.transform_pts(T2, ob)) <= 0.1))
        for dx, dy in ((0.6, 0), (0, 0.6), (-0.6, 0), (0, -0.6)):
            P = m[r].copy(); P[0] += dx; P[1] += dy
            T2 = common.compose(P, common.inverse(o[r])); ph.append(np.mean(look(common.transform_pts(T2, ob)) <= 0.1))
        pert.append(np.mean(ph))
    if hits:
        print(f"{s} n={len(hits):3d} hit at console pose {np.median(hits):.2f}  perturbed {np.median(pert):.2f}  ratio {np.median(hits)/np.median(pert):.2f}")
