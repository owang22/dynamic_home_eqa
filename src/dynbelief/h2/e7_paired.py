"""E7 paired-difference analysis: the comparison is PAIRED (same object, household,
k, both arms scored on the same queries), so plotting the per-cluster difference
(LLM - C3g) with a bootstrap CI cancels between-object variance and reveals effects
that overlapping marginal bands hide.

Free re-analysis of the existing e7_rows_<label>.jsonl (no new LLM calls). Also
reports the deployment-weighted headlines: cold-start (k=0) paired gap and the
early-evidence region (k<=4) paired gap, per rarity stratum.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dynbelief.h2 import core, e7_learning as e7

EARLY_K = [k for k in e7.K_GRID if k <= 4]


def _load(label):
    p = core.OUT / f"e7_rows_{label}.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def _cluster_acc(rows, rar, model, ks):
    """per-cluster mean accuracy over the given k-set: {(hh,object): acc}."""
    by = defaultdict(list)
    for r in rows:
        if r["rarity"] == rar and r["model"] == model and r["k"] in ks:
            by[(r["hh"], r["object"])].append(r["correct"])
    return {c: float(np.mean(v)) for c, v in by.items() if v}


def paired_diff(rows, rar, llm, ks, nb=5000, seed=11):
    """paired (LLM - C3g) per cluster over k-set ks; bootstrap CI over clusters."""
    a = _cluster_acc(rows, rar, llm, ks)
    b = _cluster_acc(rows, rar, "classical_C3g", ks)
    clus = sorted(set(a) & set(b))
    diffs = np.array([a[c] - b[c] for c in clus])
    if len(diffs) == 0:
        return np.nan, np.nan, np.nan, 0, np.nan
    rng = np.random.default_rng(seed)
    boot = [np.mean(diffs[rng.integers(0, len(diffs), len(diffs))]) for _ in range(nb)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    p_gt0 = float(np.mean(np.array(boot) > 0))       # bootstrap P(diff>0)
    return float(diffs.mean()), float(lo), float(hi), len(diffs), p_gt0


def report(label):
    rows = _load(label)
    print("=" * 78)
    print(f"E7 PAIRED differences (LLM − C3g), model={label}   [+ = LLM better]")
    print("  per-cluster paired diff, bootstrap 95% CI over clusters (household×object)")
    print("=" * 78)
    for rar, _, _ in e7.TERCILES:
        print(f"\n### {rar.upper()}")
        print(f"  {'k':>6}{'Δ(LLM−C3g)':>16}{'95% CI':>22}{'P(Δ>0)':>10}{'n':>5}")
        for k in e7.K_GRID:
            m, lo, hi, n, p = paired_diff(rows, rar, label, [k])
            star = " *" if (lo > 0 or hi < 0) else ""
            print(f"  {k:>6}{m:>+16.3f}{f'[{lo:+.2f},{hi:+.2f}]':>22}{p:>10.2f}{n:>5}{star}")
        # headline regions
        for name, ks in (("cold-start k=0", [0]), ("early-k k≤4", EARLY_K),
                         ("all k", e7.K_GRID)):
            m, lo, hi, n, p = paired_diff(rows, rar, label, ks)
            star = " SIG" if (lo > 0 or hi < 0) else ""
            print(f"    {name:16} Δ={m:+.3f}  CI[{lo:+.2f},{hi:+.2f}]  P(Δ>0)={p:.2f}{star}")


def plot(label):
    rows = _load(label)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), sharey=True)
    titles = {"rare": "RARE (≤47 ev/30d)", "medium": "MEDIUM (47–78)",
              "frequent": "FREQUENT (>78)"}
    for ax, (rar, _, _) in zip(axes, e7.TERCILES):
        xs, ys, los, his = [], [], [], []
        for k in e7.K_GRID:
            m, lo, hi, n, p = paired_diff(rows, rar, label, [k])
            xs.append(k); ys.append(m); los.append(lo); his.append(hi)
        xs = np.array(xs)
        ax.axhline(0, color="#444", lw=1, zorder=1)
        ax.fill_between(xs, los, his, color="#d1495b", alpha=0.18, zorder=2)
        ax.plot(xs, ys, "-o", color="#d1495b", lw=2, ms=6, zorder=3)
        # shade the deployment-relevant early-k region
        ax.axvspan(-0.4, 4, color="#ffd166", alpha=0.15, zorder=0)
        ax.set_title(titles[rar], fontsize=11)
        ax.set_xlabel("events observed (k)")
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("paired Δ accuracy  (LLM − C3g)")
    axes[0].text(0.2, 0.02, "early-k\n(deployment)", fontsize=8, color="#b8860b", va="bottom")
    fig.suptitle("E7 PAIRED difference (LLM − C3g): per-cluster, between-object variance removed\n"
                 "shaded = 95% CI over clusters; Δ>0 ⟺ world knowledge helps; yellow = early-evidence regime",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    out = core.OUT / "e7_paired_diff.png"
    fig.savefig(out, dpi=140)
    print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="deepseek")
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()
    report(args.label)
    if not args.no_plot:
        plot(args.label)


if __name__ == "__main__":
    main()
