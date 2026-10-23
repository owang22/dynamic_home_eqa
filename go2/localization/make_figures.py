"""Report figures (static PNGs for REPORT.md). python3 go2/localization/make_figures.py"""
import json, math, sys
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common, jumps, localizer as L
R, FG = common.HERE / "results", common.HERE / "figs"
C = {"console": "#8a8984", "consensus": "#2a78d6", "saved": "#eb6834", "static": "#1baf7a", "high": "#eda100"}
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e6e5e0",
                     "font.size": 10})

# 1. odom yaw creep while still + console following it
fig, ax = plt.subplots(1, 2, figsize=(13, 4.2))
rows = [l.strip().split(",") for l in open(R / "odom_yaw_drift.csv")][1:]
rows = [r for r in rows if int(r[1]) >= 2]
y = np.arange(len(rows))
ax[0].barh(y - 0.2, [float(r[2]) for r in rows], 0.38, color="#2a78d6", label="odom yaw")
ax[0].barh(y + 0.2, [float(r[5]) if r[5] != "nan" else 0 for r in rows], 0.38, color="#eb6834", label="console map yaw")
ax[0].set_yticks(y, [r[0] for r in rows], fontsize=8); ax[0].invert_yaxis()
ax[0].set_xlabel("deg per minute while standing still (median of 60 s windows)"); ax[0].legend(loc="lower right")
ax[0].set_title("Heading creeps while the dog stands still")
for s, col in (("2026-10-20_111931", "#2a78d6"), ("2026-10-22_160051", "#eb6834")):
    d = common.load(s); o, v, w = jumps.motion(d, 0); m = d["map"]; ok = ~np.isnan(m[:, 0])
    T = common.compose(m, common.inverse(o)); yc = np.degrees(np.unwrap(T[ok, 2])); yc -= yc[0]
    ax[1].plot((d["t"][ok] - d["t"][0]) / 60, yc, color=col, lw=1.5, label=s)
ax[1].set_xlabel("minutes into session"); ax[1].set_ylabel("change of map->odom yaw (deg)")
ax[1].set_title("The console keeps rotating its map->odom to undo it"); ax[1].legend()
plt.tight_layout(); plt.savefig(FG / "fig1_yaw_drift.png", dpi=90); plt.close()

# 2. online tracking: revisit consistency and agreement with pseudo-GT
m = json.load(open(R / "online_metrics.json")); mr = json.load(open(R / "online_metrics_smooth_reloc.json"))
labels = ["console", "consensus", "saved", "static", "high"]
rev = [m["console_revisit"]["ok"]] + [m[k]["revisit_ok"] for k in labels[1:]]
gtok = [m["consensus"]["console_ok"]] + [m[k]["ok"] for k in labels[1:]]
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for a, vals, title in ((ax[0], rev, "Revisit consistency (2,186 registered revisit pairs)"),
                       (ax[1], gtok, "Agreement with pose-graph poses (1,305 keyframes)")):
    b = a.bar(labels, vals, color=[C[k] for k in labels], width=0.6)
    for bb, v in zip(b, vals):
        a.text(bb.get_x() + bb.get_width() / 2, v + 0.01, f"{v:.0%}", ha="center", fontsize=9, color="#3a3a38")
    a.set_ylim(0, 1); a.set_ylabel("share within 0.3 m and 5 deg"); a.set_title(title, fontsize=10)
fig.suptitle("Online tracking replay: offline matcher on four reference maps vs the console", fontsize=11)
plt.tight_layout(); plt.savefig(FG / "fig2_online.png", dpi=90); plt.close()

# 3. global relocalization: success and gated precision
g = json.load(open(R / "global_summary.json"))
fig, ax = plt.subplots(figsize=(10, 4))
maps = ["consensus", "static", "saved", "high"]; x = np.arange(len(maps))
single = {r["map"]: r for r in g if r["query"] == "single"}
ax.bar(x - 0.27, [single[k]["success"] for k in maps], 0.26, color="#2a78d6", label="success, no gate")
ax.bar(x, [single[k]["accept@0.95"] for k in maps], 0.26, color="#86b6ef", label="accepted by gate (runner-up <= 95% of best)")
ax.bar(x + 0.27, [single[k]["precision@0.95"] or 0 for k in maps], 0.26, color="#eb6834", label="precision of accepted")
ax.set_xticks(x, maps); ax.set_ylim(0, 1); ax.legend(fontsize=8, loc="upper right")
ax.set_title("Global relocalization from one snapshot (132 queries per map, truth = pose-graph pose, 0.3 m / 10 deg)", fontsize=10)
plt.tight_layout(); plt.savefig(FG / "fig3_global.png", dpi=90); plt.close()
print("ok")
