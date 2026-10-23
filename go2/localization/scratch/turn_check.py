"""Is odom yaw or the console right across turns? Match single clouds (odom frame) to the saved map, around the
console's map->odom, with a wide yaw window; compare the matched map->odom yaw before/after turning bouts."""
import sys, math, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common, matcher, jumps
M = common.load_map()
occ = (M == 0)[::-1]  # row 0 = min y
F = matcher.Field(occ, 0.05, common.MAP_ORIGIN, sigma=0.1)
s = sys.argv[1]; zmin = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
d = common.load(s); o, v, w = jumps.motion(d, 0)
rows = d['c_row']; m = d['map']
step = max(1, len(rows) // 60)
print('t        n   console(m->o yaw)  matched m->o yaw  dyaw  dxy   score(console) score(best) 2nd   odomyaw(unwrapped)')
yaw_u = np.degrees(np.unwrap(d['odom'][:, 3]))
for i in range(0, len(rows), step):
    r = rows[i]
    if np.isnan(m[r, 0]) or w[r] > math.radians(5): continue
    ob, _ = common.cloud(d, i)
    ob = ob[(ob[:, 2] >= zmin)][:, :2].astype(float)
    if len(ob) < 100: continue
    od = d['odom'][r, [0, 1, 3]]
    Tc = common.compose(m[r], common.inverse(od))  # console map->odom
    # match: pts relative to dog in odom-aligned frame; pose searched = map pose of the pivot w/ yaw = map->odom yaw
    rel = ob - od[:2]
    guess = (m[r, 0], m[r, 1], Tc[2])
    rk = matcher.match(F, rel, guess, 30, 1.0, 1.0, top_k=2)
    b = rk[0]; sec = rk[1][0] if len(rk) > 1 else float('nan')
    sc0 = F.score(rel, guess)
    print(f"{common.hms(d['t'][r])} {len(ob):4d} {math.degrees(Tc[2]):8.1f}  {math.degrees(b[3]):8.1f}  {math.degrees(common.wrap(b[3]-Tc[2])):+6.1f} {math.hypot(b[1]-guess[0], b[2]-guess[1]):5.2f}  {sc0:.2f} {b[0]:.2f} {sec:.2f}  {yaw_u[r]:8.0f}")
