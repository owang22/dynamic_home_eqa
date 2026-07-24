"""Observation-density sweep: how the reflective / fusion / classical arms compare
as the SYSTEM's observations-per-day varies. All arms see the identical thinned
stream at each density (equal-information, post-fix).

Consumes all_rows_conf_<model>_o<spec>.jsonl for spec in {3,5,10,rand3,rand5,rand10}
(and the full-obs run as the saturated endpoint). Produces:
  - accuracy-vs-density curves (one line per arm), per model, at a chosen checkpoint
    (default: pooled over all days, and separately day-14 converged);
  - the crossover story: LLM-alone dominant when observations are thin, classical
    catching up as density rises, fusion tracking the better one.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dynbelief.reflect.run import OUT
from dynbelief.reflect.report import COLORS

# x-axis: mean observations/day. fixed N -> N; randN -> N (mean); full -> the
# measured mean events/day (~30) placed at the right edge.
SPEC_ORDER = [("o3", 3, "3"), ("orand3", 3, "~3"), ("o5", 5, "5"),
              ("orand5", 5, "~5"), ("o10", 10, "10"), ("orand10", 10, "~10"),
              ("", 30, "all")]
ARMS = ["llm_direct", "llm_nomem", "fusion", "classical_C3g", "classical_C1"]
MODELS = ["deepseek", "qwen36", "glm"]
PRETTY = {"deepseek": "DeepSeek-V4", "qwen36": "Qwen3.6-35B", "glm": "GLM-4.5-Air"}


def _rows(model, spec_tag):
    lbl = f"{model}_{spec_tag}" if spec_tag else model
    p = OUT / f"all_rows_conf_{lbl}.jsonl"
    if not p.exists():
        return None
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def _acc(rows, arm, field, ckpts=None):
    """clustered mean + CI over (hh,object) for arm, optionally restricted to ckpts."""
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


def _alpha(rows):
    a = [r.get("alpha") for r in rows if r["model"] == "fusion" and r.get("alpha") is not None]
    return a[0] if a else None


def table(field="correct", ckpts=None, tag="pooled"):
    lab = "RECEPTACLE" if field == "correct" else "ROOM"
    print("=" * 100)
    print(f"OBS-DENSITY SWEEP — {lab} accuracy ({tag}); all arms see the same thinned stream")
    print("=" * 100)
    for model in MODELS:
        print(f"\n### {PRETTY[model]}")
        hdr = f"  {'obs/day':>9}{'alpha*':>7}" + "".join(f"{a[:12]:>14}" for a in ARMS)
        print(hdr)
        for tagx, xval, xlab in SPEC_ORDER:
            rows = _rows(model, tagx)
            if rows is None:
                continue
            cells = []
            for a in ARMS:
                r = _acc(rows, a, field, ckpts)
                cells.append(f"{r[0]:.2f}" if r else "-")
            al = _alpha(rows)
            print(f"  {xlab:>9}{('' if al is None else al):>7}" +
                  "".join(f"{c:>14}" for c in cells))


def figure(field="correct", ckpts=None, tag="pooled"):
    lab = "receptacle" if field == "correct" else "room"
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), sharey=True)
    for ax, model in zip(axes, MODELS):
        for a in ARMS:
            xs, ys, los, his = [], [], [], []
            for tagx, xval, xlab in SPEC_ORDER:
                rows = _rows(model, tagx)
                if rows is None:
                    continue
                r = _acc(rows, a, field, ckpts)
                if r:
                    xs.append(xval); ys.append(r[0]); los.append(r[1]); his.append(r[2])
            if not xs:
                continue
            ls = "--" if a.startswith("classical") else "-"
            lw = 2.4 if a == "fusion" else 1.7
            ax.plot(xs, ys, ls, color=COLORS[a], marker="o", ms=5, lw=lw, label=a)
            ax.fill_between(xs, los, his, color=COLORS[a], alpha=0.10)
        ax.set_xscale("log"); ax.set_xticks([3, 5, 10, 30])
        ax.set_xticklabels(["3", "5", "10", "all(~30)"])
        ax.set_title(PRETTY[model]); ax.grid(alpha=0.25, which="both")
        ax.set_xlabel("observations per day (system-wide)"); ax.set_ylim(-0.03, 1.03)
    axes[0].set_ylabel(f"{lab}-level accuracy ({tag})")
    axes[-1].legend(fontsize=8.5, loc="best")
    fig.suptitle(f"Observation-density sweep ({tag}, {lab}-level) — equal thinned stream to all arms\n"
                 "thin obs → semantic memory (llm_direct) dominates starved statistics; "
                 "density → classical recovers, fusion tracks the better arm",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    out = OUT / f"obs_sweep_{lab}_{tag}.png"
    fig.savefig(out, dpi=140); print("wrote", out)


# ---- time-preserving view: accuracy vs DAYS, one panel per density ----
from dynbelief.reflect.run import CKPTS
TIME_ARMS = ["llm_direct", "fusion", "classical_C3g"]
TIME_SPECS = [("o3", "obs/day = 3"), ("o5", "obs/day = 5"),
              ("o10", "obs/day = 10"), ("", "obs/day = all (~30)")]


def _acc_at(rows, arm, ck, field):
    by = defaultdict(list)
    for r in rows:
        if r["model"] == arm and r["ckpt"] == ck:
            by[(r["hh"], r["object"])].append(r[field])
    allv = [v for vs in by.values() for v in vs]
    return float(np.mean(allv)) if allv else None


def time_grid(model, field="correct"):
    lab = "receptacle" if field == "correct" else "room"
    specs = [(t, ttl) for (t, ttl) in TIME_SPECS if _rows(model, t) is not None]
    if not specs:
        return
    fig, axes = plt.subplots(1, len(specs), figsize=(4.4 * len(specs), 4.6), sharey=True)
    if len(specs) == 1:
        axes = [axes]
    for ax, (tagx, ttl) in zip(axes, specs):
        rows = _rows(model, tagx)
        for a in TIME_ARMS:
            xs, ys = [], []
            for ck in CKPTS:
                v = _acc_at(rows, a, ck, field)
                if v is not None:
                    xs.append(ck); ys.append(v)
            ls = "--" if a.startswith("classical") else "-"
            lw = 2.4 if a == "fusion" else 1.8
            ax.plot(xs, ys, ls, color=COLORS[a], marker="o", ms=4, lw=lw, label=a)
        ax.set_title(ttl); ax.grid(alpha=0.25); ax.set_ylim(-0.03, 1.03)
        ax.set_xlabel("days of experience")
    axes[0].set_ylabel(f"{lab}-level accuracy (pooled over objects)")
    axes[-1].legend(fontsize=8.5, loc="lower right")
    fig.suptitle(f"{PRETTY[model]} — learning curves OVER TIME at each observation density "
                 f"({lab}-level; equal thinned stream to all arms)\n"
                 "denser observations steepen classical's trajectory; the LLM curve is "
                 "density-robust; watch where fusion crosses",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    out = OUT / f"obs_time_{model}_{lab}.png"
    fig.savefig(out, dpi=140); print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day14", action="store_true", help="pooled-over-days density summary")
    ap.add_argument("--time", action="store_true",
                    help="time-preserving: accuracy vs days, one panel per density")
    args = ap.parse_args()
    if args.time:
        for model in MODELS:
            for field in ("correct", "room_correct"):
                time_grid(model, field)
        return
    ckpts = [14] if args.day14 else None
    tag = "day14" if args.day14 else "pooled"
    for field in ("correct", "room_correct"):
        table(field, ckpts, tag)
        figure(field, ckpts, tag)


if __name__ == "__main__":
    main()
