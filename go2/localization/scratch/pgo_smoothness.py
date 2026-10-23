import sys, math, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common
tot = 0; n = 0
for f in sorted((common.HERE / 'results/pgo_poses').glob('*.npz')):
    z = np.load(f); T = z['T_map_odom']; dog = z['dog']; t = z['t']; j = []
    for k in range(len(T) - 1):
        if t[k + 1] - t[k] > 30: continue
        p1 = common.transform_pts(T[k], dog[k + 1][None])[0]; p2 = common.transform_pts(T[k + 1], dog[k + 1][None])[0]
        j.append((np.hypot(*(p1 - p2)), abs(math.degrees(common.wrap(T[k][2] - T[k + 1][2])))))
    j = np.array(j)
    if len(j):
        nj = int(np.sum((j[:, 0] > 0.3) | (j[:, 1] > 5))); tot += nj; n += len(j)
        print(f.stem, 'n', len(j), 'jumps>0.3m/5deg', nj, 'max %.2f m %.1f deg' % (j[:, 0].max(), j[:, 1].max()))
print('total', tot, 'of', n)
