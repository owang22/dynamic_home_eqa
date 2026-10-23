"""Which frame are the cloud 'obs' cells really in? Align pairs of clouds across a turn with a brute-force
rotation (about the dog) + translation search and compare with the odom yaw change."""
import sys, numpy as np
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1]))
import common
from scipy.spatial import cKDTree

def score(A, B):
    T = cKDTree(B[:, :2]); d, _ = T.query(A[:, :2]); return np.mean(d < 0.08)

s = sys.argv[1] if len(sys.argv) > 1 else '2026-10-20_111931'
d = common.load(s)
od = d['odom']; rows = d['c_row']
yaw = np.unwrap(od[:, 3])
rng = np.random.default_rng(0)
out = []
for _ in range(400):
    i = rng.integers(0, len(rows) - 10); j = i + rng.integers(1, 10)
    dy = yaw[rows[j]] - yaw[rows[i]]; dp = np.hypot(*(od[rows[j], :2] - od[rows[i], :2]))
    if abs(dy) < np.radians(20) or dp > 0.3: continue
    A, _ = common.cloud(d, i); B, _ = common.cloud(d, j)
    if len(A) < 200 or len(B) < 200: continue
    c = od[rows[j], :2]
    best = None
    for r in np.radians(np.arange(-180, 180, 2)):
        R = np.array([[np.cos(r), -np.sin(r)], [np.sin(r), np.cos(r)]])
        A2 = A.copy(); A2[:, :2] = (A[:, :2] - c) @ R.T + c
        sc = score(A2, B)
        if best is None or sc > best[0]: best = (sc, np.degrees(r))
    out.append((np.degrees(dy), best[1], best[0], score(A, B)))
    if len(out) >= 25: break
for o in out: print('odom dyaw %+7.1f  best rot %+7.1f  score %.2f  (no-rot score %.2f)' % o)
