"""Precision vs coverage of the verified relocalization (task 3): accept a query's pose when the best match has
>= T inliers (and optionally no strong match > 2 m away: margin). Correct = position within 1 m and yaw within
15 deg of the query's console pose. Coverage is over all queries that have a true neighbour.
    python3 refine_curves.py -> results/refine_curves.json, figs/refine_curves.png
"""
import json, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = {}
TH = [25, 40, 60, 80, 100, 150, 200]
TH_LG = [25, 50, 75, 100, 150, 200, 300, 400]
fig, axes = plt.subplots(2, 3, figsize=(15, 8.4), sharey=True)
for ax, (split, mt) in zip(axes.ravel(), [(s, m) for m in ("", "_lg") for s in ["within_10-20", "x_20v22", "x_22v20"]]):
  for region, c in [("full", "#4269d0"), ("upper", "#ef7d22"), ("lower", "#6cc5b0")]:
        TT = TH_LG if mt else TH
        rows = json.load(open(f"results/refine_{split}_{region}_rfull{mt}.json"))
        hp = [r for r in rows if r["has_pos"]]
        res = []
        for margin in (False, True):
            pts = []
            for t in TT:
                acc = [r for r in hp if r.get("inl", 0) >= t and (not margin or r["second_far_inl"] < 0.5 * r["inl"])]
                ok = [r for r in acc if r["err_m_w"] <= 1.0 and r["err_yaw_w"] <= 15]
                pts.append({"T": t, "coverage": len(acc) / len(hp), "precision": len(ok) / max(1, len(acc)), "n_acc": len(acc),
                            "pos_med": float(np.median([r["err_m_w"] for r in ok])) if ok else None,
                            "yaw_med": float(np.median([r["err_yaw_w"] for r in ok])) if ok else None})
            res.append(pts)
            pp = [p for p in pts if p["n_acc"] >= 3]          # thresholds that accept < 3 queries are not plotted
            ax.plot([p["coverage"] for p in pp], [p["precision"] for p in pp], "-o" if not margin else "--", color=c,
                    ms=3, label=f"{region}{' + margin' if margin else ''}")
        out[f"{split}|{region}{mt}"] = {"no_margin": res[0], "margin": res[1]}
        p = res[0]
        print(split, region + mt, " ".join(f"T{x['T']}:{x['coverage']:.2f}/{x['precision']:.2f}" for x in p), "| margin:",
              " ".join(f"T{x['T']}:{x['coverage']:.2f}/{x['precision']:.2f}" for x in res[1]))
  ax.set_title(split + (" SuperPoint+LightGlue" if mt else " SIFT")); ax.set_xlabel("coverage (share of queries given a pose)"); ax.grid(alpha=.3)
for a in axes[:, 0]: a.set_ylabel("precision (pos <= 1 m and yaw <= 15 deg)")
axes[0, 0].legend(fontsize=8)
for a in axes.ravel(): a.set_ylim(0.5, 1.02)
plt.tight_layout(); plt.savefig("figs/refine_curves.png", dpi=110)
json.dump(out, open("results/refine_curves.json", "w"), indent=1)
