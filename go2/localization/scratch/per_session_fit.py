"""Per session: pool its keyframes (console poses vs pgo poses) and find the rigid transform that best fits the
pooled cells onto the saved map. A consistent pose source needs ~0 everywhere."""
import sys, math, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common, matcher
M = common.load_map(); F = matcher.Field((M == 0)[::-1], 0.05, common.MAP_ORIGIN, sigma=0.1)
for f in sorted((common.HERE / 'results' / 'pgo_poses').glob('*.npz')):
    z = np.load(f); d = common.load(f.stem); out = []
    for key in ('T_console', 'T_map_odom'):
        pts = []
        for c, T in zip(z['cloud'], z[key]):
            ob, _ = common.cloud(d, int(c)); ob = ob[ob[:, 2] >= 0.4][:, :2].astype(float)
            pts.append(common.transform_pts(T, ob))
        if not pts: continue
        P = np.unique(np.round(np.concatenate(pts) / 0.1).astype(int), axis=0) * 0.1
        ctr = P.mean(0)
        b = matcher.match(F, P - ctr, (ctr[0], ctr[1], 0.0), 25, 0.5, 1.0, top_k=1)[0]
        out.append(f"{key[2:]:9s} fit at identity {F.score(P-ctr,(ctr[0],ctr[1],0)):.2f} best {b[0]:.2f} needs {math.hypot(b[1]-ctr[0],b[2]-ctr[1]):.2f} m {math.degrees(b[3]):+5.1f} deg")
    print(f.stem, len(z['cloud']), ' | '.join(out))
