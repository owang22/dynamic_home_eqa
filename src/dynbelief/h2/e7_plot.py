"""Render the E7 v2 pooled learning curves: accuracy vs EVENTS-OBSERVED, one panel
per rarity tercile, DeepSeek (LLM) vs frozen C3g vs C1, clustered bootstrap CIs."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dynbelief.h2 import core, e7_learning as e7


def _load(label):
    p = core.OUT / f"e7_rows_{label}.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def _boot(by_clu, nb=3000, seed=7):
    clus = list(by_clu)
    if not clus:
        return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(seed); m = []
    for _ in range(nb):
        pick = rng.integers(0, len(clus), len(clus))
        vals = [v for i in pick for v in by_clu[clus[i]]]
        m.append(np.mean(vals) if vals else 0.0)
    allv = [v for vs in by_clu.values() for v in vs]
    return float(np.mean(allv)), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def curve(rows, rar, model):
    xs, ys, los, his = [], [], [], []
    for k in e7.K_GRID:
        by = defaultdict(list)
        for r in rows:
            if r["rarity"] == rar and r["model"] == model and r["k"] == k:
                by[(r["hh"], r["object"])].append(r["correct"])
        if not by:
            continue
        mean, lo, hi = _boot(by)
        xs.append(k); ys.append(mean); los.append(lo); his.append(hi)
    return np.array(xs), np.array(ys), np.array(los), np.array(his)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="deepseek")
    args = ap.parse_args()
    rows = _load(args.label)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
    series = [(args.label, "DeepSeek (world knowledge)", "#d1495b", "o", "-"),
              ("classical_C3g", "C3g (frozen classical)", "#2e6f95", "s", "-"),
              ("classical_C1", "C1 (persistence)", "#8d99ae", "^", "--")]
    titles = {"rare": "RARE objects  (≤ 47 ev/30d)",
              "medium": "MEDIUM  (47–78 ev/30d)",
              "frequent": "FREQUENT  (> 78 ev/30d)"}
    for ax, (rar, _, _) in zip(axes, e7.TERCILES):
        nobj = len({(r["hh"], r["object"]) for r in rows if r["rarity"] == rar})
        for model, lbl, col, mk, ls in series:
            x, y, lo, hi = curve(rows, rar, model)
            if len(x) == 0:
                continue
            ax.plot(x, y, ls, color=col, marker=mk, label=lbl, lw=2, ms=6, zorder=3)
            ax.fill_between(x, lo, hi, color=col, alpha=0.13, zorder=1)
        ax.set_title(f"{titles[rar]}   (n={nobj} objs)", fontsize=11)
        ax.set_xlabel("events observed of the target object  (k)")
        ax.grid(alpha=0.25)
        ax.set_ylim(-0.03, 1.03)
    axes[0].set_ylabel("prediction accuracy (held-out test week)")
    # annotate the regime-transfer point on the rare panel
    axes[0].annotate("LLM already high at k≤1\n(≈1 diagnostic sighting\n→ regime transfer)",
                     xy=(0.5, 0.0), xytext=(2.2, 0.13), fontsize=8.5, color="#d1495b",
                     va="bottom")
    axes[0].legend(loc="upper right", fontsize=8.5, framealpha=0.9)
    fig.suptitle("E7 — World knowledge buys adaptation the events never can: "
                 "accuracy vs events-observed, by object rarity\n"
                 "(pooled over 18 regime-conditioned objects × 6 households; clustered 95% CI)",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = core.OUT / "e7_learning_curves.png"
    fig.savefig(out, dpi=140)
    print("wrote", out)


if __name__ == "__main__":
    main()
