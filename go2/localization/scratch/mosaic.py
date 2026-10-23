"""Odom-frame mosaics of short walking spans (3 min: odom yaw drift <~5-15 deg), aligned to the saved map by a
global search, overlaid. If the mosaic's walls line up in one part of the map but not another, the map is bent."""
import sys, math, numpy as np, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common, matcher
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
M = common.load_map(); occ = (M == 0)[::-1]
F = matcher.Field(occ, 0.05, common.MAP_ORIGIN, sigma=0.1)
spans = [(a.split('@')[0], a.split('@')[1]) for a in sys.argv[2:]]
out = sys.argv[1]
fig, axs = plt.subplots(1, len(spans), figsize=(9 * len(spans), 9))
axs = np.atleast_1d(axs)
for ax, (s, hhmmss) in zip(axs, spans):
    d = common.load(s)
    t0 = time.mktime(time.strptime(s[:10] + ' ' + hhmmss, '%Y-%m-%d %H:%M:%S'))
    sel = np.flatnonzero((d['c_t'] >= t0) & (d['c_t'] <= t0 + 180))
    cells = {}
    for i in sel[::2]:
        ob, _ = common.cloud(d, i)
        for x, y, z in ob[ob[:, 2] >= 0.4]:
            k = (round(float(x), 2), round(float(y), 2)); cells[k] = max(cells.get(k, 0), z)
    P = np.array([[k[0], k[1], z] for k, z in cells.items()])
    c0 = P[:, :2].mean(0)
    rel = P[:, :2] - c0
    sub = rel[np.random.default_rng(0).choice(len(rel), min(4000, len(rel)), replace=False)]
    rk = matcher.match(F, sub, (0, 0, 0), 180, 1.0, None, top_k=3)
    b = rk[0]
    q = common.transform_pts((b[1], b[2], b[3]), rel)
    ax.imshow(M, cmap='gray', extent=[-6.85, -6.85 + 283 * 0.05, -5.4, -5.4 + 289 * 0.05], vmin=-100, vmax=300)
    ax.scatter(q[:, 0], q[:, 1], c=P[:, 2], s=3, cmap='jet', vmin=0.4, vmax=1.4, marker='s', alpha=0.6)
    tr = d['odom'][(d['t'] >= t0) & (d['t'] <= t0 + 180), :2] - c0
    tq = common.transform_pts((b[1], b[2], b[3]), tr); ax.plot(tq[:, 0], tq[:, 1], 'm-', lw=1)
    ax.set_title(f"{s} {hhmmss}+3min: {len(P)} cells; global fit {b[0]:.2f} (2nd {rk[1][0]:.2f} at {math.degrees(rk[1][3]-b[3]):+.0f} deg)")
    ax.set_xlim(-6, 7); ax.set_ylim(-5.5, 8)
    print(s, hhmmss, 'fit', round(b[0], 3), 'second', [(round(r[0], 3), round(math.degrees(common.wrap(r[3] - b[3])))) for r in rk[1:]])
plt.tight_layout(); plt.savefig(out, dpi=55)
