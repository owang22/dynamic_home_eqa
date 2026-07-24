"""Gate-justification diagnostic: is the memory's own hypothesis entropy actually
predictive of its query accuracy?

Plots llm_direct accuracy as a function of the memory's top-3 hypothesis entropy H
at the answering checkpoint, pooled across households x objects x checkpoints x
test days, binned in H with clustered bootstrap CIs (cluster = household x object).
One curve per model, panels for receptacle- and room-level accuracy.

Reading it: a clearly DOWNWARD curve means high-entropy memories really do answer
worse -- weighting the fusion prior by (1-H/H_max) is justified. A flat curve means
entropy is not a useful confidence signal and the prior weight should not depend on
it. (The earlier absolute gate FAILED (P4); this diagnostic asks whether the signal
itself was bad, or only the hard-zero mechanism.)
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dynbelief.reflect import memory as M
from dynbelief.reflect.report import _load_rows
from dynbelief.reflect.run import OUT

# fixed H bins (bits) for cross-model comparability; last bin reaches H_max=1.585
H_BINS = [(0.0, 0.05), (0.05, 0.25), (0.25, 0.55), (0.55, 0.95), (0.95, 1.59)]
MCOL = {"deepseek": "#d1495b", "qwen36": "#457b9d", "glm": "#6a994e"}


def _bin_of(h):
    for i, (lo, hi) in enumerate(H_BINS):
        if lo <= h < hi or (i == len(H_BINS) - 1 and h >= lo):
            return i
    return 0


def _boot(by_clu, nb=4000, seed=31):
    clus = list(by_clu)
    if not clus:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    m = [np.mean([v for i in rng.integers(0, len(clus), len(clus))
                  for v in by_clu[clus[i]]]) for _ in range(nb)]
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def curve(label, field):
    rows = [r for r in _load_rows("conf", label)
            if r["model"] == "llm_direct" and r.get("H") is not None]
    pts = []
    for i, (lo, hi) in enumerate(H_BINS):
        by = defaultdict(list)
        for r in rows:
            if _bin_of(r["H"]) == i:
                by[(r["hh"], r["object"])].append(r[field])
        allv = [v for vs in by.values() for v in vs]
        if not allv:
            continue
        clo, chi = _boot(by)
        pts.append(((lo + min(hi, M.H_MAX)) / 2, float(np.mean(allv)), clo, chi,
                    len(allv), len(by)))
    return pts


def report(labels):
    print("=" * 86)
    print("ENTROPY DIAGNOSTIC — llm_direct accuracy vs memory hypothesis entropy H")
    print("  clustered 95% CI (household x object); n = queries in bin")
    print("=" * 86)
    for label in labels:
        for field, gl in (("correct", "receptacle"), ("room_correct", "room")):
            pts = curve(label, field)
            if not pts:
                print(f"\n  {label} [{gl}]: (no rows)")
                continue
            print(f"\n  {label} [{gl}]:")
            print(f"    {'H bin center':>13}{'acc':>8}{'95% CI':>18}{'n':>7}{'clusters':>9}")
            for (hc, m, lo, hi, n, nc) in pts:
                print(f"    {hc:>13.2f}{m:>8.2f}{f'[{lo:.2f},{hi:.2f}]':>18}{n:>7}{nc:>9}")


def figure(labels):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    for ax, (field, gl) in zip(axes, [("correct", "RECEPTACLE"), ("room_correct", "ROOM")]):
        for label in labels:
            pts = curve(label, field)
            if not pts:
                continue
            x = [p[0] for p in pts]; y = [p[1] for p in pts]
            lo = [p[2] for p in pts]; hi = [p[3] for p in pts]
            c = MCOL.get(label, "#888")
            ax.plot(x, y, "-o", color=c, lw=2, ms=6, label=label)
            ax.fill_between(x, lo, hi, color=c, alpha=0.14)
        ax.set_xlabel("memory hypothesis entropy H (bits)")
        ax.set_title(f"{gl}-level accuracy")
        ax.axvline(M.H_MAX, color="#999", ls=":", lw=1)
        ax.grid(alpha=0.25); ax.set_ylim(-0.03, 1.03)
    axes[0].set_ylabel("llm_direct accuracy")
    axes[0].legend(fontsize=9)
    fig.suptitle("Does the memory's own entropy predict its accuracy?  "
                 "(downward slope ⇒ entropy-weighting justified)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    out = OUT / "entropy_diagnostic.png"
    fig.savefig(out, dpi=140)
    print("\nwrote", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default="deepseek")
    args = ap.parse_args()
    labels = args.labels.split(",")
    report(labels)
    figure(labels)


if __name__ == "__main__":
    main()
