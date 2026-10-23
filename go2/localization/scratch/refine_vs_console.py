"""Local search of each calm snapshot against the saved map around the console pose: how far is the best match,
and how clear is it (margin to the best pose >= 0.3 m / 10 deg away)?"""
import sys, math, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common, matcher, jumps
M = common.load_map(); occ = (M == 0)[::-1]
zmin = float(sys.argv[1]); zmax = float(sys.argv[2]); sig = float(sys.argv[3]); sess = sys.argv[4:]
F = matcher.Field(occ, 0.05, common.MAP_ORIGIN, sigma=sig)
calls = jumps.agent_calls()
allr = []
for s in sess:
    d = common.load(s); o, v, w = jumps.motion(d, 0); evs = jumps.events(d, 0, calls); calm = jumps.calm_mask(d, evs, 0)
    m = d['map']; rows = d['c_row']
    idx = [i for i in range(len(rows)) if calm[rows[i]]]
    for i in idx[::max(1, len(idx) // 30)]:
        r = rows[i]; ob, _ = common.cloud(d, i)
        ob = ob[(ob[:, 2] >= zmin) & (ob[:, 2] < zmax)][:, :2].astype(float)
        if len(ob) < 50: continue
        Tc = common.compose(m[r], common.inverse(o[r])); rel = ob - o[r, :2]
        guess = (m[r, 0], m[r, 1], Tc[2])
        res = matcher.search(F, rel, guess[:2], Tc[2] + np.radians(np.arange(-30, 31, 1.0)), 1.0)
        rk = matcher.best_poses(F, res, top_k=6, min_sep_deg=10, min_sep_m=0.3)
        b = matcher.refine_pose(F, rel, rk[0])
        alt = max([c[0] for c in rk[1:]], default=0)
        allr.append((math.hypot(b[1] - guess[0], b[2] - guess[1]), abs(math.degrees(common.wrap(b[3] - Tc[2]))), b[0] - alt, b[0], F.score(rel, guess)))
a = np.array(allr)
print(f"z [{zmin},{zmax}) sigma {sig}: n={len(a)} |dxy| med {np.median(a[:,0]):.2f} p75 {np.percentile(a[:,0],75):.2f}; |dyaw| med {np.median(a[:,1]):.1f} p75 {np.percentile(a[:,1],75):.1f}; "
      f"within 0.3m&5deg {np.mean((a[:,0]<0.3)&(a[:,1]<5)):.2f}; margin med {np.median(a[:,2]):.3f}; score best {np.median(a[:,3]):.2f} console {np.median(a[:,4]):.2f}")
