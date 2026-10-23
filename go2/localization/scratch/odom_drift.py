"""Is odometry consistent over time? Align cloud B to cloud A (both odom frame) with the correlative matcher.
If odom were perfect the correction would be ~0. Report correction vs time gap and accumulated turning."""
import sys, math, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common, matcher

def field_from(pts, res=0.05, pad=1.0):
    x0, y0 = pts[:, 0].min() - pad - res / 2, pts[:, 1].min() - pad - res / 2  # cloud cells land on field cell centres
    W = int((pts[:, 0].max() + pad - x0) / res) + 1; H = int((pts[:, 1].max() + pad - y0) / res) + 1
    occ = np.zeros((H, W), bool)
    occ[np.floor((pts[:, 1] - y0) / res).astype(int), np.floor((pts[:, 0] - x0) / res).astype(int)] = True
    return matcher.Field(occ, res, (x0, y0), sigma=0.07)

s = sys.argv[1]
gaps = [float(g) for g in sys.argv[2:]] or [5, 30, 120, 600]
d = common.load(s); od = d['odom']; rows = d['c_row']; ct = d['c_t']
yaw_u = np.unwrap(od[:, 3]); turn_cum = np.concatenate([[0], np.cumsum(np.abs(np.diff(yaw_u)))])
rng = np.random.default_rng(1)
for gap in gaps:
    res = []
    for _ in range(3000):
        i = rng.integers(0, len(ct))
        j = np.searchsorted(ct, ct[i] + gap)
        if j >= len(ct) or abs(ct[j] - ct[i] - gap) > 5: continue
        pa, pb = od[rows[i]], od[rows[j]]
        if math.hypot(pa[0] - pb[0], pa[1] - pb[1]) > 1.0: continue
        A, _ = common.cloud(d, i); B, _ = common.cloud(d, j)
        if len(A) < 300 or len(B) < 300: continue
        A = A[:, :2].astype(float); B = B[:, :2].astype(float)
        F = field_from(A)
        rel = B - pb[:2]
        r = matcher.match(F, rel, (pb[0], pb[1], 0.0), 12, 1.0, 0.4, top_k=1)[0]
        sc0 = F.score(rel, (pb[0], pb[1], 0.0))
        res.append((r[0], sc0, r[1] - pb[0], r[2] - pb[1], math.degrees(r[3]),
                    math.degrees(turn_cum[rows[j]] - turn_cum[rows[i]])))
        if len(res) >= 40: break
    a = np.array(res)
    if not len(a): print(gap, 'no pairs'); continue
    print(f"gap {gap:5.0f}s n={len(a)}: score id {np.median(a[:,1]):.2f} -> best {np.median(a[:,0]):.2f}; |dxy| med {np.median(np.hypot(a[:,2],a[:,3])):.3f} p90 {np.percentile(np.hypot(a[:,2],a[:,3]),90):.3f} m; |dyaw| med {np.median(np.abs(a[:,4])):.1f} p90 {np.percentile(np.abs(a[:,4]),90):.1f} deg; turned med {np.median(a[:,5]):.0f} deg")
    if gap >= 120:
        for row in a[np.argsort(-np.abs(a[:,4]))][:5]: print('    dyaw %+.1f deg dxy %.2f m turned %.0f deg score %.2f->%.2f' % (row[4], math.hypot(row[2], row[3]), row[5], row[1], row[0]))
