"""Figures for the confidence-shift study (PNG, matplotlib).

    python3 -m baselines.patrol.confshift_figs --logs "DIR/classical/*.jsonl" "DIR/llm/*/run_log.jsonl" \
        --banks DIR/banks --out DIR/report/figs [--threshold 0.7]

Figure 1: accuracy per day per agent, shift days shaded (weekend columns
fully; a weekday column by the share of households with a major event).
Figure 2: coverage (share answered with confidence >= threshold) and
selective accuracy per day. Figure 3: reliability diagram per agent.
Colours: fixed per agent (never by rank); told arms solid, not-told dashed.
"""
from __future__ import annotations

import argparse
import glob
import pathlib
import sys
from collections import defaultdict
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from baselines.patrol.confshift import (THRESHOLDS, acc, cover, day_label, load_headers, load_logs, reliability,
                                        shift_marks)

STYLE: Dict[str, dict] = {   # fixed slot per agent family
    "last seen": dict(color="#6b7280", ls="-", lw=1.6),
    "most frequent": dict(color="#2a78d6", ls="-", lw=2),
    "timetable": dict(color="#2a78d6", ls=":", lw=1.6),
    "periodic": dict(color="#6b7280", ls=":", lw=1.4),
    "Perpetua*": dict(color="#4a3aa7", ls="-", lw=1.6),
    "llm_naive/told/look_off": dict(color="#eb6834", ls="-", lw=2),
    "llm_naive/not_told/look_off": dict(color="#eb6834", ls="--", lw=2),
    "llm_longleaf/told/look_off": dict(color="#1baf7a", ls="-", lw=2.2),
    "llm_longleaf/not_told/look_off": dict(color="#1baf7a", ls="--", lw=2.2),
    "llm_longleaf_fixed/told/look_off": dict(color="#008300", ls="-", lw=1.6),
    "llm_longleaf_fixed/not_told/look_off": dict(color="#008300", ls="--", lw=1.6),
}
NAME = {"llm_naive/told/look_off": "naive LLM, told", "llm_naive/not_told/look_off": "naive LLM, not told",
        "llm_longleaf/told/look_off": "hypothesis mixture, told", "llm_longleaf/not_told/look_off": "hypothesis mixture, not told",
        "llm_longleaf_fixed/told/look_off": "hyp. mixture (no re-ask), told",
        "llm_longleaf_fixed/not_told/look_off": "hyp. mixture (no re-ask), not told"}


def style(agent: str) -> dict:
    return STYLE.get(agent, dict(color="#9ca3af", ls="-", lw=1.2))


def shade(ax, days: List[int], headers: Dict[str, dict], hh: List[str]) -> None:
    marks = shift_marks(headers)
    day_names = {int(k): v for k, v in next(iter(headers.values()))["day_names"].items()}
    for i, d in enumerate(days):
        share = sum(1 for h in hh if d in marks.get(h, set())) / max(len(hh), 1)
        if share > 0:
            ax.axvspan(i - 0.5, i + 0.5, color="#f2c46d", alpha=0.12 + 0.38 * share, lw=0)
    ax.set_xticks(range(len(days)))
    ax.set_xticklabels([day_label(d, day_names) for d in days])


def fig_accuracy(rows, headers, out: pathlib.Path) -> None:
    days = sorted({r["day_index"] for r in rows})
    hh = sorted({r["household"] for r in rows})
    agents = [a for a in STYLE if a in {r["agent"] for r in rows}] + sorted({r["agent"] for r in rows} - set(STYLE))
    g = defaultdict(list)
    for r in rows:
        g[(r["agent"], r["day_index"])].append(r)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    shade(ax, days, headers, hh)
    for a in agents:
        ys = [100 * acc(g.get((a, d), [])) for d in days]
        ax.plot(range(len(days)), ys, label=NAME.get(a, a), **style(a))
    ax.set_ylim(30, 100); ax.set_ylabel("accuracy (%)"); ax.grid(axis="y", color="#e5e7eb", lw=0.6)
    ax.set_title(f"Accuracy per day ({len(hh)} households; shaded = share of households on a shift day)", fontsize=10)
    ax.legend(fontsize=7, ncol=2, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)


def fig_coverage(rows, headers, out: pathlib.Path, thr: float) -> None:
    days = sorted({r["day_index"] for r in rows})
    hh = sorted({r["household"] for r in rows})
    agents = [a for a in STYLE if a in {r["agent"] for r in rows}] + sorted({r["agent"] for r in rows} - set(STYLE))
    g = defaultdict(list)
    for r in rows:
        g[(r["agent"], r["day_index"])].append(r)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharex=True)
    for ax, what in zip(axes, ("coverage", "selective accuracy")):
        shade(ax, days, headers, hh)
        for a in agents:
            vals = []
            for d in days:
                c, sa, n = cover(g.get((a, d), []), thr)
                vals.append(100 * (c if what == "coverage" else sa))
            ax.plot(range(len(days)), vals, label=NAME.get(a, a), **style(a))
        ax.set_ylim(0, 102); ax.grid(axis="y", color="#e5e7eb", lw=0.6)
        ax.set_title(f"{what} at confidence >= {thr}", fontsize=10)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("% of questions answered at or above threshold"); axes[1].set_ylabel("accuracy on those (%)")
    axes[1].legend(fontsize=7, ncol=2, frameon=False)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)


def fig_reliability(rows, out: pathlib.Path) -> None:
    agents = [a for a in STYLE if a in {r["agent"] for r in rows}] + sorted({r["agent"] for r in rows} - set(STYLE))
    n = len(agents)
    cols = min(4, n); rws = (n + cols - 1) // cols
    fig, axes = plt.subplots(rws, cols, figsize=(3.2 * cols, 3.2 * rws), squeeze=False)
    for k, a in enumerate(agents):
        ax = axes[k // cols][k % cols]
        rs = [r for r in rows if r["agent"] == a]
        bins = reliability(rs)
        ax.plot([0, 1], [0, 1], color="#d1d5db", lw=1)
        xs = [b["mean_conf"] for b in bins if b["n"]]; ys = [b["acc"] for b in bins if b["n"]]
        sz = [max(12, 220 * b["n"] / len(rs)) for b in bins if b["n"]]
        ax.scatter(xs, ys, s=sz, color=style(a)["color"], alpha=0.85, edgecolor="white", lw=1)
        ax.plot(xs, ys, color=style(a)["color"], lw=1)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_title(NAME.get(a, a), fontsize=9)
        ax.set_xlabel("stated confidence", fontsize=8); ax.set_ylabel("observed accuracy", fontsize=8)
        ax.tick_params(labelsize=7)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    for k in range(n, rws * cols):
        axes[k // cols][k % cols].axis("off")
    fig.suptitle("Reliability (dot size = share of answers in the bin; pooled over the week)", fontsize=10)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--logs", nargs="+", required=True)
    ap.add_argument("--banks", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--threshold", type=float, default=0.7)
    ap.add_argument("--confidence", default="top_prob", choices=("top_prob", "agreement"))
    a = ap.parse_args(argv)
    import baselines.patrol.confshift as cs
    cs.CONFIDENCE_FIELD = a.confidence
    paths = [p for pat in a.logs for p in glob.glob(pat)]
    rows = load_logs(paths)
    headers = load_headers(a.banks)
    a.out.mkdir(parents=True, exist_ok=True)
    fig_accuracy(rows, headers, a.out / "fig1_accuracy_per_day.png")
    for thr in THRESHOLDS:
        fig_coverage(rows, headers, a.out / f"fig2_coverage_selective_{thr}.png", thr)
    fig_reliability(rows, a.out / "fig3_reliability.png")
    print(f"wrote figures to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
