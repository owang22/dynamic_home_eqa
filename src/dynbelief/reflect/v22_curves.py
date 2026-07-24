"""VERSION22 accuracy curves: vs days of experience and vs observations/day.

Left block: accuracy vs DAYS (checkpoints 1..14), one panel per observation
density (distractor level), every arm overlaid. Right: accuracy vs total
OBSERVATIONS/day at the converged day-14 checkpoint (the distractor axis, since
true obs stay ~3.3/day and distractors inflate the count without adding signal).
"""
from __future__ import annotations

import json
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dynbelief.reflect.run import OUT, CKPTS
from dynbelief.reflect.distractor_sweep import _rows, LEVELS, ACOLORS

# measured mean observations/day per distractor level (true ~3.3 kept + N)
OBS_PER_DAY = {0: 3.3, 3: 6.3, 6: 9.3, 12: 15.3}
ARMS = ["llm_direct", "llm_surprise", "llm_nomem", "fusion", "classical_C3g"]
PRETTY = {"llm_direct": "LLM nightly reflection", "llm_surprise": "LLM surprise-gated",
          "llm_nomem": "LLM raw digest", "fusion": "fusion (LLM+classical)",
          "classical_C3g": "classical C3g"}


def _acc(rows, arm, field, ckpts=None):
    by = defaultdict(list)
    for r in rows:
        if r["model"] == arm and (ckpts is None or r["ckpt"] in ckpts):
            by[(r["hh"], r["object"])].append(r[field])
    allv = [v for vs in by.values() for v in vs]
    if not allv:
        return None
    clus = list(by); rng = np.random.default_rng(5)
    m = [np.mean([v for i in rng.integers(0, len(clus), len(clus)) for v in by[clus[i]]])
         for _ in range(1500)]
    return float(np.mean(allv)), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def build(field="correct"):
    lab = "Receptacle" if field == "correct" else "Room"
    fig = plt.figure(figsize=(19, 4.6))
    gs = fig.add_gridspec(1, len(LEVELS) + 1, width_ratios=[1] * len(LEVELS) + [1.15],
                          wspace=0.28)
    # ---- accuracy vs DAYS, one panel per observation density ----
    for i, lv in enumerate(LEVELS):
        ax = fig.add_subplot(gs[0, i])
        rows = _rows(lv)
        for a in ARMS:
            xs, ys = [], []
            for ck in CKPTS:
                r = _acc(rows, a, field, [ck])
                if r:
                    xs.append(ck); ys.append(r[0])
            if not xs:
                continue
            ls = "--" if a == "classical_C3g" else "-"
            lw = 2.4 if a in ("llm_direct", "llm_surprise") else 1.6
            ax.plot(xs, ys, ls, color=ACOLORS[a], marker="o", ms=4, lw=lw,
                    label=PRETTY[a])
        ax.set_title(f"~{OBS_PER_DAY[lv]:.0f} obs/day  ({lv} distractors)", fontsize=10)
        ax.set_xlabel("days of experience"); ax.grid(alpha=0.25); ax.set_ylim(0, 0.6)
        if i == 0:
            ax.set_ylabel(f"{lab}-level accuracy")
        if i == 0:
            ax.legend(fontsize=7.5, loc="upper left")
    # ---- accuracy vs OBSERVATIONS/day at day 14 ----
    ax = fig.add_subplot(gs[0, len(LEVELS)])
    for a in ARMS:
        xs, ys, los, his = [], [], [], []
        for lv in LEVELS:
            r = _acc(_rows(lv), a, field, [14])
            if r:
                xs.append(OBS_PER_DAY[lv]); ys.append(r[0]); los.append(r[1]); his.append(r[2])
        if not xs:
            continue
        ls = "--" if a == "classical_C3g" else "-"
        lw = 2.4 if a in ("llm_direct", "llm_surprise") else 1.6
        ax.plot(xs, ys, ls, color=ACOLORS[a], marker="o", ms=5, lw=lw, label=PRETTY[a])
        ax.fill_between(xs, los, his, color=ACOLORS[a], alpha=0.10)
    ax.set_title("day-14 accuracy vs observation density", fontsize=10)
    ax.set_xlabel("observations / day  (true ~3.3 + distractors)")
    ax.set_ylabel(f"{lab}-level accuracy"); ax.grid(alpha=0.25); ax.set_ylim(0, 0.6)
    ax.set_xticks([OBS_PER_DAY[l] for l in LEVELS])
    ax.set_xticklabels([f"{OBS_PER_DAY[l]:.0f}" for l in LEVELS])
    fig.suptitle(f"VERSION22 (DeepSeek-V4) — {lab.lower()}-level accuracy vs days of experience "
                 f"(per observation density) and vs observations/day at convergence\n"
                 "true useful observations held at ~3.3/day; distractors are static-object "
                 "sightings that inflate obs/day but are never queried", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    out = OUT / f"v22_curves_{field}.png"
    fig.savefig(out, dpi=140); print("wrote", out)


if __name__ == "__main__":
    for f in ("correct", "room_correct"):
        build(f)
