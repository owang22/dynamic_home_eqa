"""What frame is cloud['flat'] in? Find the SE2 that maps flat onto the obs cells (odom frame) and compare with
the odom pose (body->odom) at nearby times."""
import sys, math, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common, matcher, jumps
s = sys.argv[1]
d = common.load(s); rows = d['c_row']
def field_from(pts, res=0.05, pad=4.0):
    x0, y0 = pts[:, 0].min() - pad - res/2, pts[:, 1].min() - pad - res/2
    W = int((pts[:, 0].max() + pad - x0) / res) + 1; H = int((pts[:, 1].max() + pad - y0) / res) + 1
    occ = np.zeros((H, W), bool)
    occ[np.floor((pts[:, 1] - y0) / res).astype(int), np.floor((pts[:, 0] - x0) / res).astype(int)] = True
    return matcher.Field(occ, res, (x0, y0), sigma=0.07)
to = d['t'] - d['age'][:, 0]
for i in np.linspace(5, len(rows) - 5, 12).astype(int):
    ob, fl = common.cloud(d, i)
    if len(fl) < 50: continue
    F = field_from(ob[ob[:, 2] >= 0.25][:, :2].astype(float))
    r = rows[i]; od = d['odom'][r, [0, 1, 3]]
    rk = matcher.match(F, fl.astype(float), (od[0], od[1], od[2]), 180, 2.0, 3.0, top_k=2)
    b = rk[0]
    # which odom time matches b best?
    ts = d['t'][r] + np.arange(-6, 2.01, 0.1)
    P = jumps.odom_at(d, ts)
    err = np.hypot(P[:, 0] - b[1], P[:, 1] - b[2]) + 0.5 * np.abs(common.wrap(P[:, 2] - b[3]))
    k = np.argmin(err)
    print(f"cloud {i} {common.hms(d['t'][r])} fit {b[0]:.2f} (2nd {rk[1][0]:.2f}) T=({b[1]:.2f},{b[2]:.2f},{math.degrees(b[3]):.0f}) odom now=({od[0]:.2f},{od[1]:.2f},{math.degrees(od[2]):.0f}) best odom dt={ts[k]-d['t'][r]:+.1f}s err {err[k]:.2f}  age_cloud {d['c_age'][i]}")
