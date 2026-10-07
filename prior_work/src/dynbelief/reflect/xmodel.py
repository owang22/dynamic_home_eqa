"""Cross-model comparison of the reflective-memory arms (pure evidence-ratio fusion).
Consumes all_rows_conf_<label>.jsonl written by report.evaluate() for each model.

Produces:
  - a per-model panel figure (accuracy vs days of experience, receptacle-level,
    pooled over all strata) so the fusion-tracks-envelope + learning-trajectory
    story can be read across models side by side;
  - a compact table: pooled day-1 (cold start) and day-14 (converged) accuracy per
    arm per model, receptacle and room level.
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
from dynbelief.reflect.report import ARANK, COLORS, _cell

PRETTY = {"deepseek_o3": "DeepSeek-V4", "qwen36_o3": "Qwen3.6-35B",
          "glm_o3": "GLM-4.5-Air", "deepseek": "DeepSeek-V4 (all-obs)",
          "qwen36": "Qwen3.6 (all-obs)", "glm": "GLM (all-obs)"}


def _load(label):
    p = OUT / f"all_rows_conf_{label}.jsonl"
    if not p.exists():
        return None
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def table(labels):
    print("=" * 96)
    print("CROSS-MODEL — reflective memory, pure evidence-ratio fusion (obs-per-day=3)")
    print("  pooled accuracy, clustered 95% CI; day 1 = cold start, day 14 = converged")
    print("=" * 96)
    for field, gl in (("correct", "RECEPTACLE"), ("room_correct", "ROOM")):
        print(f"\n### {gl}-level")
        print(f"  {'arm':14}" + "".join(f"{PRETTY.get(l, l)[:20]:>26}" for l in labels))
        print(f"  {'':14}" + "".join(f"{'day1 -> day14':>26}" for _ in labels))
        for arm in ARANK:
            cells = []
            for label in labels:
                rows = _load(label)
                if rows is None:
                    cells.append(f"{'-':>26}"); continue
                c1 = _cell(rows, arm, [1], None, field)
                c14 = _cell(rows, arm, [14], None, field)
                s = (f"{c1[0]:.2f}->{c14[0]:.2f}" if c1 and c14 else "-")
                cells.append(s.rjust(26))
            print(f"  {arm:14}" + "".join(cells))


def figure(labels):
    n = len(labels)
    fig, axes = plt.subplots(1, n, figsize=(5.2 * n, 4.7), sharey=True)
    if n == 1:
        axes = [axes]
    for ax, label in zip(axes, labels):
        rows = _load(label)
        if rows is None:
            ax.set_title(f"{PRETTY.get(label, label)} (no data)"); continue
        for m in ARANK:
            xs, ys = [], []
            for ck in CKPTS:
                c = _cell(rows, m, [ck], None, "correct")
                if c:
                    xs.append(ck); ys.append(c[0])
            ls = "--" if m.startswith("classical") else "-"
            lw = 2.4 if m == "fusion" else 1.6
            ax.plot(xs, ys, ls, color=COLORS[m], marker="o", ms=4, lw=lw, label=m)
        ax.set_title(PRETTY.get(label, label)); ax.grid(alpha=0.25)
        ax.set_xlabel("days of experience"); ax.set_ylim(-0.03, 1.03)
    axes[0].set_ylabel("RECEPTACLE-level accuracy (pooled)")
    axes[-1].legend(fontsize=8, loc="lower right")
    fig.suptitle("Reflective memory across models (obs-per-day=3, pure evidence-ratio fusion) — "
                 "fusion tracks the upper envelope; semantic arms climb from a starved start",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = OUT / "xmodel_obs3.png"
    fig.savefig(out, dpi=140)
    print("\nwrote", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default="deepseek_o3,qwen36_o3,glm_o3")
    args = ap.parse_args()
    labels = args.labels.split(",")
    table(labels)
    figure(labels)


if __name__ == "__main__":
    main()
