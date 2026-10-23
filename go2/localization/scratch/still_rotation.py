"""While the dog stands still, odom yaw creeps (+0.6..4.8 deg/min). Physical rotation or estimate drift?
Compare the dog's voxel cells (odom frame) at the start and end of a long still period: cells that appear only
at the end are matched against the start cells with a yaw search about the dog."""
import sys, math, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common, matcher
def field_from(pts, res=0.05, pad=2.0):
    x0, y0 = pts[:, 0].min() - pad - res/2, pts[:, 1].min() - pad - res/2
    W = int((pts[:, 0].max() + pad - x0) / res) + 1; H = int((pts[:, 1].max() + pad - y0) / res) + 1
    occ = np.zeros((H, W), bool)
    occ[np.floor((pts[:, 1] - y0) / res).astype(int), np.floor((pts[:, 0] - x0) / res).astype(int)] = True
    return matcher.Field(occ, res, (x0, y0), sigma=0.07)
for s in sys.argv[1:]:
    d = common.load(s); t = d['t']; o = d['odom']; ct = d['c_t']; rows = d['c_row']
    # find still stretches >= 4 min (path < 10 cm)
    i = 0
    while i < len(rows) - 1:
        j = i
        while j + 1 < len(rows):
            seg = o[rows[i]:rows[j + 1] + 1, :2]
            if np.sum(np.hypot(*np.diff(seg, axis=0).T)) > 0.10: break
            j += 1
        if ct[j] - ct[i] >= 240:
            A, _ = common.cloud(d, i); B, _ = common.cloud(d, j)
            A = A[A[:, 2] >= 0.3]; B = B[B[:, 2] >= 0.3]
            ka = set(map(tuple, np.round(A[:, :2], 2))); newB = np.array([b for b in B[:, :2] if tuple(np.round(b, 2)) not in ka])
            dyaw = math.degrees(np.unwrap(o[rows[i]:rows[j] + 1, 3])[-1] - o[rows[i], 3])
            p = o[rows[j], :2]
            F = field_from(A[:, :2].astype(float))
            out = 'too few new cells'
            if len(newB) > 30:
                rk = matcher.match(F, newB.astype(float) - p, (p[0], p[1], 0.0), 60, 1.0, 0.3, top_k=3)
                prof = matcher.search(F, newB.astype(float) - p, p, np.radians(np.arange(-60, 61, 5)), 0.2)
                out = f"best rot {math.degrees(rk[0][3]):+.1f} deg score {rk[0][0]:.2f} (at 0: {F.score(newB.astype(float)-p,(p[0],p[1],0)):.2f}); profile " + ' '.join(f"{math.degrees(y):+.0f}:{c.max():.2f}" for y, c, _, _ in prof[::2])
            whole = matcher.match(F, B[:, :2].astype(float) - p, (p[0], p[1], 0.0), 60, 1.0, 0.3, top_k=1)[0]
            print(f"{s} {common.hms(ct[i])}-{common.hms(ct[j])} ({(ct[j]-ct[i])/60:.1f} min) odom yaw change {dyaw:+.1f} deg; cells A {len(A)} B {len(B)} new {len(newB)}; whole-B best rot {math.degrees(whole[3]):+.1f} score {whole[0]:.2f}")
            print('    new cells:', out)
        i = j + 1
