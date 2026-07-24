"""Distractor-sweep summary (version22): accuracy vs distractor sightings/day.

Consumes all_rows_v22_distractor_d{N}.jsonl (nightly arms + offline classical/
fusion, written by report.py) and rows_surprise_v22_surprise_d{N}.jsonl (the
surprise arm), and produces:
  - a pooled + day-14 table per arm per distractor level,
  - accuracy-vs-distractors curves (receptacle + room),
  - the surprise-efficiency table (accuracy vs number of reflection calls).

True observations stay ~3/day (rand3) at every level; distractors only add
static-object sightings that never appear in queries.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dynbelief.reflect.run import OUT, CKPTS
from dynbelief.reflect.report import COLORS

LEVELS = [0, 3, 6, 12]
ARMS = ["llm_direct", "llm_nomem", "llm_surprise", "fusion", "classical_C3g"]
ACOLORS = {**COLORS, "llm_surprise": "#f2a541"}


def _rows(level):
    out = []
    p = OUT / f"all_rows_v22_distractor_d{level}.jsonl"
    if p.exists():
        out += [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    p = OUT / f"rows_surprise_v22_surprise_d{level}.jsonl"
    if p.exists():
        out += [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return out or None


def _acc(rows, arm, field, ckpts=None):
    by = defaultdict(list)
    for r in rows:
        if r["model"] == arm and (ckpts is None or r["ckpt"] in ckpts):
            by[(r["hh"], r["object"])].append(r[field])
    allv = [v for vs in by.values() for v in vs]
    if not allv:
        return None
    clus = list(by); rng = np.random.default_rng(5)
    m = [np.mean([v for i in rng.integers(0, len(clus), len(clus))
                  for v in by[clus[i]]]) for _ in range(2000)]
    return float(np.mean(allv)), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def table(field="correct", ckpts=None, tag="pooled"):
    lab = "RECEPTACLE" if field == "correct" else "ROOM"
    print("=" * 96)
    print(f"VERSION22 DISTRACTOR SWEEP — {lab} accuracy ({tag}); true obs ~3/day, "
          f"distractor sightings never queried")
    print("=" * 96)
    hdr = f"  {'dist/day':>9}" + "".join(f"{a[:13]:>15}" for a in ARMS)
    print(hdr)
    for lv in LEVELS:
        rows = _rows(lv)
        if rows is None:
            continue
        cells = []
        for a in ARMS:
            r = _acc(rows, a, field, ckpts)
            cells.append(f"{r[0]:.2f}" if r else "-")
        print(f"  {lv:>9}" + "".join(f"{c:>15}" for c in cells))


def efficiency_table():
    print("\nSURPRISE EFFICIENCY — reflection calls vs nightly (14/hh), pooled receptacle acc")
    print(f"  {'dist/day':>9}{'nightly acc':>13}{'surprise acc':>14}{'refl/hh':>9}{'saving':>8}")
    for lv in LEVELS:
        rows = _rows(lv)
        if rows is None:
            continue
        d = _acc(rows, "llm_direct", "correct")
        s = _acc(rows, "llm_surprise", "correct")
        nr = [r["n_reflect"] for r in rows
              if r["model"] == "llm_surprise" and r["ckpt"] == 14]
        mean_nr = float(np.mean(nr)) if nr else float("nan")
        print(f"  {lv:>9}"
              + (f"{d[0]:>13.2f}" if d else f"{'-':>13}")
              + (f"{s[0]:>14.2f}" if s else f"{'-':>14}")
              + f"{mean_nr:>9.1f}{(1 - mean_nr / 14) * 100:>7.0f}%")


def figure(field="correct"):
    lab = "receptacle" if field == "correct" else "room"
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), sharey=True)
    for ax, (ckpts, ttl) in zip(axes, [(None, "pooled over checkpoints"),
                                       ([14], "day-14 (converged)")]):
        for a in ARMS:
            xs, ys, los, his = [], [], [], []
            for lv in LEVELS:
                rows = _rows(lv)
                if rows is None:
                    continue
                r = _acc(rows, a, field, ckpts)
                if r:
                    xs.append(lv); ys.append(r[0]); los.append(r[1]); his.append(r[2])
            if not xs:
                continue
            ls = "--" if a.startswith("classical") else "-"
            lw = 2.3 if a in ("llm_direct", "llm_surprise") else 1.6
            ax.plot(xs, ys, ls, color=ACOLORS[a], marker="o", ms=5, lw=lw, label=a)
            ax.fill_between(xs, los, his, color=ACOLORS[a], alpha=0.10)
        ax.set_title(ttl); ax.grid(alpha=0.25)
        ax.set_xlabel("distractor sightings / day (true obs ~3/day)")
        ax.set_xticks(LEVELS); ax.set_ylim(-0.03, 1.03)
    axes[0].set_ylabel(f"{lab}-level accuracy")
    axes[-1].legend(fontsize=8.5, loc="best")
    fig.suptitle("VERSION22 distractor sweep (DeepSeek) — static-object sightings inflate "
                 "observations/day but are never queried", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    out = OUT / f"v22_distractor_sweep_{lab}.png"
    fig.savefig(out, dpi=140)
    print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    args = ap.parse_args()
    for field in ("correct", "room_correct"):
        table(field, None, "pooled")
        table(field, [14], "day14")
        figure(field)
    efficiency_table()


if __name__ == "__main__":
    main()
