import sys, math, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common, matcher, jumps
M = common.load_map(); occ = (M == 0)[::-1]
s = sys.argv[1]; zmin = float(sys.argv[2]); sig = float(sys.argv[3])
F = matcher.Field(occ, 0.05, common.MAP_ORIGIN, sigma=sig)
d = common.load(s); o, v, w = jumps.motion(d, 0); rows = d['c_row']; m = d['map']
for i in np.linspace(3, len(rows) - 3, 8).astype(int):
    r = rows[i]
    if np.isnan(m[r, 0]): continue
    ob, _ = common.cloud(d, i); ob = ob[ob[:, 2] >= zmin][:, :2].astype(float)
    od = o[r]; Tc = common.compose(m[r], common.inverse(od)); rel = ob - od[:2]
    res = matcher.search(F, rel, m[r, :2], Tc[2] + np.radians(np.arange(-40, 41, 2)), 1.0)
    prof = [(math.degrees(y - Tc[2]), cor.max()) for y, cor, _, _ in res]
    best = max(prof, key=lambda a: a[1])
    line = ' '.join(f"{p[1]:.2f}" for p in prof[::4])
    print(f"{common.hms(d['t'][r])} n={len(ob)} best yaw off {best[0]:+.0f} score {best[1]:.2f} at0 {dict(prof)[0.0]:.2f} | {line}")
