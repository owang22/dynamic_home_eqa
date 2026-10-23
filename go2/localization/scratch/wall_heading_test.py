import sys, math, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common, walls, jumps
MAP_DIR = float(sys.argv[1]); zmin = float(sys.argv[2]); sess = sys.argv[3:]
calls = jumps.agent_calls(); res = []
for s in sess:
    d = common.load(s); o, v, w = jumps.motion(d, 0); evs = jumps.events(d, 0, calls); calm = jumps.calm_mask(d, evs, 0)
    m = d['map']; rows = d['c_row']
    idx = [i for i in range(len(rows)) if calm[rows[i]]]
    for i in idx[::max(1, len(idx) // 25)]:
        r = rows[i]; ob, _ = common.cloud(d, i); ob = ob[ob[:, 2] >= zmin][:, :2].astype(float)
        if len(ob) < 50: continue
        a, con, sec, _ = walls.manhattan_dir(ob, step=0.5)
        Tc = common.compose(m[r], common.inverse(o[r]))
        pred = MAP_DIR - a  # map->odom yaw mod 90
        err = float(walls.wrap90(pred - math.degrees(Tc[2])))
        res.append((err, con, sec))
a = np.array(res)
for cmin in (0, 1.3, 1.6, 2.0):
    k = a[:, 1] >= cmin
    if k.sum(): print(f"zmin {zmin} contrast>={cmin}: n={k.sum()} |err| med {np.median(np.abs(a[k,0])):.1f} p75 {np.percentile(np.abs(a[k,0]),75):.1f} within 3deg {np.mean(np.abs(a[k,0])<3):.2f} within 5 {np.mean(np.abs(a[k,0])<5):.2f}; median signed {np.median(a[k,0]):+.1f}")
