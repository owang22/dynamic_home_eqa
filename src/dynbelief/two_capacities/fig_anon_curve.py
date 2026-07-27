"""C4 — anonymization learning curves, one panel per LLM.

Accuracy vs DAYS OF EVIDENCE AVAILABLE (not query day — see confirm_curve.py for
why the single-point harness has no learning axis). Each panel overlays the two
LLM arms against the two non-LLM controls, all seeing the identical truncated
digest at each x.

The read: llm_anon's SLOPE is learning with no world knowledge; the gap between
llm_named and llm_anon is the semantic prior; classical is flat at 0 because the
queried objects are held out (no edge to learn, no transfer channel); class_freq
is flat because it ignores the digest entirely.
"""
from __future__ import annotations

import json
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from dynbelief.h2 import core
from dynbelief.h2.confirm_curve import CUTOFFS

OUT = core.OUT.parent / "corrected"

# dataviz categorical slots in FIXED order + secondary encoding (style, marker)
# so identity never rests on hue alone.
ARMS = [
    ("llm_named",  "LLM (named)",        "#2a78d6", "-",  "o", 2.2),
    ("llm_anon",   "LLM (anonymized)",   "#eb6834", "-",  "s", 2.6),
    ("class_freq", "class-frequency",    "#eda100", "--", "^", 1.8),
    ("classical",  "classical (C3)",     "#52514e", ":",  "x", 1.8),
]
MODELS = [("deepseek", "DeepSeek-V4-Flash"),
          ("qwen36", "Qwen3.6-35B-A3B"),
          ("glm", "GLM-4.5-Air")]


def _boot_ci(by_hh, nb=2000, seed=0):
    hhs = list(by_hh)
    if not hhs:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    m = []
    for _ in range(nb):
        pick = rng.integers(0, len(hhs), len(hhs))
        pool = [v for i in pick for v in by_hh[hhs[i]]]
        m.append(np.mean(pool) if pool else 0.0)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def series(rows, arm):
    xs, ys, los, his = [], [], [], []
    for D in CUTOFFS:
        by_hh = defaultdict(list)
        for r in rows:
            if r["arm"] == arm and r["evidence_days"] == D:
                by_hh[r["household"]].append(r["correct"])
        allv = [v for vs in by_hh.values() for v in vs]
        if not allv:
            continue
        lo, hi = _boot_ci(by_hh)
        xs.append(D); ys.append(float(np.mean(allv))); los.append(lo); his.append(hi)
    return map(np.array, (xs, ys, los, his))


CHANCE = 0.065          # 1/(candidates+elsewhere), measured over the bank
# P(the query's true receptacle is one the digest actually mentions) — the hard
# ceiling for any arm that has ONLY the digest (i.e. llm_anon).
COVERAGE = {"target": 0.450, "conventional": 0.067}
KINDS = [("target", "REGIME-FLIPPED targets  (the routine moves them)"),
         ("conventional", "CONVENTIONAL objects  (the routine ignores them)")]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    avail = [(k, t) for k, t in MODELS if (core.OUT / f"curve_rows_{k}.jsonl").exists()]
    if not avail:
        print("no curve rows yet"); return
    fig, axes = plt.subplots(2, len(avail), figsize=(5.4 * len(avail), 8.6),
                             sharey=True, sharex=True, facecolor="#fcfcfb")
    axes = np.atleast_2d(axes)
    for ci, (key, title) in enumerate(avail):
        rows = [json.loads(l) for l in
                (core.OUT / f"curve_rows_{key}.jsonl").read_text().splitlines() if l.strip()]
        for ri, (kind, klab) in enumerate(KINDS):
            ax = axes[ri][ci]
            ax.set_facecolor("#fcfcfb")
            sub = [r for r in rows if r["kind"] == kind]
            # reference lines: chance floor, and the digest-coverage ceiling that
            # bounds any digest-only arm.
            ax.axhline(CHANCE, color="#a8a7a2", lw=1, ls=(0, (1, 3)), zorder=1)
            ax.axhline(COVERAGE[kind], color="#eb6834", lw=1, ls=(0, (5, 4)),
                       alpha=0.55, zorder=1)
            if ci == 0:
                ax.annotate("chance", (CUTOFFS[0], CHANCE), xytext=(0, -13),
                            textcoords="offset points", fontsize=8, color="#a8a7a2")
                ax.annotate("digest coverage ceiling", (CUTOFFS[0], COVERAGE[kind]),
                            xytext=(0, 5), textcoords="offset points", fontsize=8,
                            color="#eb6834", alpha=0.9)
            for arm, lab, col, ls, mk, lw in ARMS:
                xs, ys, los, his = series(sub, arm)
                if not len(xs):
                    continue
                ax.fill_between(xs, los, his, color=col, alpha=0.11, linewidth=0)
                ax.plot(xs, ys, ls, color=col, lw=lw, marker=mk, ms=6.5,
                        mec="#fcfcfb", mew=1.2 if mk != "x" else 0, label=lab, zorder=3)
                ax.annotate(f"{ys[-1]:.2f}", (xs[-1], ys[-1]), xytext=(6, 0),
                            textcoords="offset points", va="center", fontsize=9,
                            color="#52514e")
            if ri == 0:
                ax.set_title(title, fontsize=12, color="#0b0b0b", pad=10)
            if ri == 1:
                ax.set_xlabel("days of observation available", fontsize=10, color="#52514e")
            ax.set_xticks(CUTOFFS)
            ax.grid(axis="y", color="#e6e5e1", lw=0.8)
            ax.set_axisbelow(True)
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            for s in ("left", "bottom"):
                ax.spines[s].set_color("#c9c8c3")
            ax.tick_params(colors="#52514e", labelsize=9)
    for ri, (kind, klab) in enumerate(KINDS):
        axes[ri][0].set_ylabel("accuracy (exact receptacle)", fontsize=10,
                               color="#52514e")
        # row identity on the RIGHT edge so it cannot collide with tick labels
        axes[ri][-1].text(1.035, 0.5, klab, transform=axes[ri][-1].transAxes,
                          rotation=270, va="center", ha="left", fontsize=9.5,
                          color="#0b0b0b")
    axes[0][0].set_ylim(-0.03, 0.85)
    axes[0][0].legend(frameon=False, fontsize=9.5, loc="upper left", labelcolor="#0b0b0b")
    fig.suptitle("Anonymized vs named receptacles, split by whether the routine moves the object",
                 fontsize=13.5, color="#0b0b0b", y=0.985)
    fig.text(0.5, 0.006,
             "TOP vs BOTTOM is the asymmetry: the anonymized LLM tracks the DIGEST-COVERAGE CEILING — it answers only when the digest names the answer, "
             "and the digest only ever\ntalks about the routine-shifted objects. On conventional objects it sits at chance, because naming those requires exactly the world knowledge that was stripped. "
             "class_freq is the mirror image.\nCurves are FLAT because this sweep grows evidence VOLUME, not CONTENT: digest lines go 15->185 but distinct facts only 15->27, saturating by D=5. "
             "Bands = clustered bootstrap 95% CI by household.",
             ha="center", fontsize=8.3, color="#52514e")
    fig.tight_layout(rect=[0, 0.055, 1, 0.965])
    p = OUT / "C4_anon_learning_curves.png"
    fig.savefig(p, dpi=170, facecolor="#fcfcfb")
    print(f"wrote {p}  (models: {', '.join(k for k, _ in avail)})")


if __name__ == "__main__":
    main()
