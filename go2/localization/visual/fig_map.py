"""Map figure: where the pictures are, by day, clean vs excluded (figs/map_pictures.png)."""
import numpy as np, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import vcommon as V
import common as C   # ../common.py (lidar study), read-only use of the saved console map

R = V.load_records()
m = C.load_map(); h, w = m.shape
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
cols = {"10-19": "#4269d0", "10-20": "#ef7d22", "10-22": "#3ca951"}
for ax, d in zip(axes, ["10-19", "10-20", "10-22"]):
    ax.imshow(m, cmap="gray", vmin=0, vmax=255)
    for clean, mk, al in ((False, "x", 0.5), (True, "o", 0.9)):
        rr = [r for r in R if r["day"] == d and r["clean"] == clean]
        if not rr: continue
        c, rw = C.world_to_px([r["x"] for r in rr], [r["y"] for r in rr], h)
        u = np.cos(np.radians([r["yaw_deg"] for r in rr])); v = np.sin(np.radians([r["yaw_deg"] for r in rr]))   # angles="uv": screen up = map +y here
        ax.quiver(c, rw, u, v, color=cols[d] if clean else "#e15759", alpha=al, scale=40, width=0.003)
    ax.set_title(f"{d}: {sum(r['day']==d and r['clean'] for r in R)} clean (arrows), {sum(r['day']==d and not r['clean'] for r in R)} excluded (red)")
    xs, ys = C.world_to_px(np.array([r["x"] for r in R]), np.array([r["y"] for r in R]), h)
    ax.set_xlim(xs.min() - 20, xs.max() + 20); ax.set_ylim(ys.max() + 20, ys.min() - 20); ax.axis("off")
plt.tight_layout(); plt.savefig("figs/map_pictures.png", dpi=100)
