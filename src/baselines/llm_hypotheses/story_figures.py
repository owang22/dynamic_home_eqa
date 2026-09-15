"""Two headline figures for a run: the active-protocol story and the paired
differences. Everything else (passive, per-object, ESS) stays in
``analyze_tour_start``; these two are the ones meant to be read first.

    python -m baselines.llm_hypotheses.story_figures [--household hh_001__bank0]
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from baselines.llm_hypotheses.analyze_tour_start import STUDY_DIR, daily, load, overall, paired, score
from baselines.types import DAY_SECONDS

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "axes.titlelocation": "left", "axes.titleweight": "bold", "axes.titlesize": 11})

# Fixed order and colour per arm: colour follows the arm, never its rank.
ARMS: List[Tuple[str, str, str, str]] = [
    # key, label, colour, group
    ("active__routine_posterior__f0", "routine posterior (ceiling: knows the routine)", INK2, "ceiling"),
    ("active__tree__tree_named__f0", "tree LLM, re-asking", "#2a78d6", "ours"),
    ("active__tree_fixed__tree_named__f0", "tree LLM, fixed roots", "#2a78d6", "ours"),
    ("active__graph_fixed__graph_named__f0", "graph LLM, fixed set", "#1baf7a", "ours"),
    ("active__llm__tour_named__f0", "flat LLM, re-asking", "#eda100", "ours"),
    ("active__llm_fixed__tour_named__f0", "flat LLM, fixed set", "#eda100", "ours"),
    ("active__log_reader__named__f0", "log reader (one LLM call per decision)", "#e87ba4", "baseline"),
    ("active__mostfreq72__f0", "most-frequent 72 h (no LLM)", "#eb6834", "baseline"),
]
LABEL = {k: lab for k, lab, _, _ in ARMS}
COLOR = {k: c for k, _, c, _ in ARMS}
CURVES = ["active__tree__tree_named__f0", "active__graph_fixed__graph_named__f0",
          "active__log_reader__named__f0", "active__mostfreq72__f0", "active__routine_posterior__f0"]
ANON = {
    "active__tree__tree_named__f0": "active__tree__tree_anonymized__f0",
    "active__tree_fixed__tree_named__f0": "active__tree_fixed__tree_anonymized__f0",
    "active__graph_fixed__graph_named__f0": "active__graph_fixed__graph_anonymized__f0",
    "active__llm__tour_named__f0": "active__llm__tour_anonymized__f0",
    "active__llm_fixed__tour_named__f0": "active__llm_fixed__tour_anonymized__f0",
}
FIXED = {
    "active__tree__tree_named__f0": "active__tree_fixed__tree_named__f0",
    "active__llm__tour_named__f0": "active__llm_fixed__tour_named__f0",
}


def present(arms, keys: Sequence[str]) -> List[str]:
    return [k for k in keys if k in arms]


def add_partial_log_reader(arms, study_dir: pathlib.Path, household: str) -> None:
    """A log-reader arm still running has only notes/calls.jsonl; rebuild its
    answers so far so the curve panel can show it, marked partial."""
    key = "active__log_reader__named__f0"
    if key in arms:
        return
    calls_path = study_dir / household / "arms" / "active" / key / "notes" / "calls.jsonl"
    ref = next((arms[k] for k in ("active__mostfreq72__f0", "active__routine_posterior__f0") if k in arms), None)
    if not calls_path.exists() or ref is None:
        return
    by_q = {(r["object_id"], r["t_query"]): r for r in ref["rows"]}
    rows = []
    for line in calls_path.read_text().splitlines():
        c = json.loads(line)
        if c.get("action") != "answer" or not c.get("ranked"):
            continue
        r = by_q.get((c["object"], c["t"]))
        if r is None:
            continue
        top = c["ranked"][0]
        rows.append({"question_id": r["question_id"], "object_id": r["object_id"], "t_query": r["t_query"],
                     "truth": r["truth"], "argmax": top, "dist": {top: 1.0},
                     "tour_absent": r.get("tour_absent", False)})
    if not rows:
        return
    for r in rows:
        r["top1"], r["ll"] = score(r, merged=False)
        r["top1m"], r["llm"] = score(r, merged=True)
        r["day"] = r["t_query"] // DAY_SECONDS
    arms[key] = {"rows": rows, "diag": {"partial": True, "tour_absent_objects": ref["diag"].get("tour_absent_objects")}}
    LABEL[key] = f"log reader (still running: {len(rows)} answers so far, through day {rows[-1]['day']})"


def tour_absent_rows(arms, key: str) -> List[dict]:
    absent = set(arms[key]["diag"].get("tour_absent_objects") or [])
    return [r for r in arms[key]["rows"] if r.get("tour_absent", r["object_id"] in absent)]


def style(ax) -> None:
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def hbar_panel(ax, arms, keys: Sequence[str], rows_of, title: str, xlim, ticklabels: bool) -> None:
    """One horizontal bar per arm in story order, 95% CI whisker, value at the end."""
    ys = np.arange(len(keys))[::-1]
    for y, k in zip(ys, keys):
        o = overall(rows_of(k)); ci = 1.96 * o["top1_se"]
        ax.barh(y, o["top1"], color=COLOR[k], height=0.62, alpha=0.9 if k != "active__routine_posterior__f0" else 0.55)
        ax.errorbar(o["top1"], y, xerr=ci, fmt="none", ecolor=INK, elinewidth=1.2, capsize=3)
        ax.text(o["top1"] + ci + 0.006, y, f"{o['top1']:.3f} ± {ci:.3f}", va="center", ha="left", fontsize=9, color=INK)
    ax.set_yticks(ys); ax.set_yticklabels([LABEL[k] for k in keys] if ticklabels else [])
    ax.set_xlim(*xlim); ax.set_xticks(np.arange(xlim[0], 0.91, 0.1))
    ax.set_xlabel("top-1 accuracy (exact match), 95% CI")
    ax.set_title(title); style(ax)
    # thin separators between story groups
    groups = [dict((k, g) for k, _, _, g in ARMS)[k] for k in keys]
    for i in range(1, len(keys)):
        if groups[i] != groups[i - 1]:
            ax.axhline(ys[i] + 0.5, color=GRID, lw=1)


def fig_main(arms, out: pathlib.Path, household: str) -> None:
    keys = [k for k in present(arms, [k for k, *_ in ARMS]) if not arms[k]["diag"].get("partial")]
    curves = present(arms, CURVES)
    n = len(arms[keys[0]]["rows"])
    n_abs = len(tour_absent_rows(arms, keys[0]))

    fig = plt.figure(figsize=(20, 6.8))
    y0, h = 0.21, 0.59
    ax0 = fig.add_axes([0.035, y0, 0.30, h])
    ax1 = fig.add_axes([0.535, y0, 0.22, h])   # room on its left for the arm names
    ax2 = fig.add_axes([0.785, y0, 0.20, h])   # same rows as b, names not repeated

    for k in curves:
        d, m, lo, hi = daily(arms[k]["rows"], "top1", win=3)
        ceiling = k == "active__routine_posterior__f0"
        ax0.fill_between(d, lo, hi, color=COLOR[k], alpha=0.10, lw=0)
        ax0.plot(d, m, color=COLOR[k], lw=2.2, ls=(0, (4, 2)) if ceiling else "-", label=LABEL[k])
    ax0.set_xlabel("day of the episode (day 0 = Monday; walkthrough tour on day 0)")
    ax0.set_ylabel("top-1 accuracy (3-day rolling mean, 95% CI band)")
    ax0.set_xticks(range(0, 28, 7)); ax0.set_xlim(0, 27)
    ax0.set_title("a. Accuracy over the episode")
    ax0.grid(axis="y", color=GRID, lw=0.8); ax0.set_axisbelow(True); ax0.tick_params(length=0)
    fig.legend(*ax0.get_legend_handles_labels(), loc="lower left", bbox_to_anchor=(0.035, 0.01), ncol=5,
               frameon=False, fontsize=9.5, handlelength=2.4, columnspacing=2.0)

    hbar_panel(ax1, arms, keys, lambda k: arms[k]["rows"], f"b. All {n} questions", (0.60, 0.98), True)
    hbar_panel(ax2, arms, keys, lambda k: tour_absent_rows(arms, k),
               f"c. Objects the tour never saw ({n_abs} questions)", (0.30, 0.98), False)

    fig.suptitle(f"{household.replace('__bank', ', bank seed ')}: active protocol, 24 looks a day, {n} questions over 28 days. "
                 "Every LLM arm is named (the model sees object owners).",
                 x=0.04, ha="left", fontsize=13, fontweight="bold", y=0.975)
    fig.text(0.04, 0.905, "Exact-match scoring: ON_PERSON and OUT_OF_HOUSE are different answers. "
             "Bars show the mean with a 95% confidence interval; arms are in story order, not sorted.",
             fontsize=10, color=INK2)
    fig.savefig(out / "main_active_accuracy.png", dpi=150)
    plt.close(fig)


def fig_paired(arms, out: pathlib.Path, household: str) -> None:
    """Paired per-question differences in top-1 accuracy, 95% bootstrap CI."""
    groups: List[Tuple[str, List[Tuple[str, str, str]]]] = []
    mf = "active__mostfreq72__f0"
    groups.append(("LLM belief − most-frequent (no LLM)",
                   [(k, mf, LABEL[k]) for k, *_ in ARMS if k in arms and k not in (mf, "active__routine_posterior__f0")
                    and not arms[k]["diag"].get("partial")]))
    groups.append(("named − anonymized, same arm",
                   [(k, a, LABEL[k]) for k, a in ANON.items() if k in arms and a in arms]))
    groups.append(("re-asking − fixed set, same arm",
                   [(k, f, LABEL[k].split(",")[0]) for k, f in FIXED.items() if k in arms and f in arms]))
    groups = [(t, items) for t, items in groups if items]

    n_rows = sum(len(items) for _, items in groups) + len(groups)
    fig, ax = plt.subplots(figsize=(11, 0.42 * n_rows + 2.2))
    fig.subplots_adjust(left=0.36, right=0.97, top=0.80, bottom=0.12)
    y = n_rows; ticks, labels = [], []
    for title, items in groups:
        y -= 1
        ax.text(-0.005, y, title, transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=10, fontweight="bold", color=INK)
        for a, b, lab in items:
            y -= 1
            m, lo, hi = paired(arms[a]["rows"], arms[b]["rows"], "top1")
            c = COLOR.get(a, INK2)
            ax.plot([lo, hi], [y, y], color=c, lw=2.2, solid_capstyle="butt")
            ax.plot(m, y, "o", color=c, ms=8, mec=SURF, mew=1.5)
            ax.text(hi + 0.004, y, f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}]", va="center", ha="left", fontsize=9, color=INK)
            ticks.append(y); labels.append(lab)
    ax.set_yticks(ticks); ax.set_yticklabels(labels)
    ax.axvline(0, color=INK, lw=1)
    ax.set_ylim(-0.8, n_rows + 0.2)
    lo_all = min(ax.get_xlim()[0], -0.03); ax.set_xlim(lo_all, ax.get_xlim()[1] + 0.06)
    ax.set_xlabel("difference in top-1 accuracy, paired per question (95% bootstrap CI)")
    style(ax)
    n = len(arms[mf]["rows"])
    fig.suptitle(f"{household.replace('__bank', ', bank seed ')}: what each design choice buys, active protocol, {n} questions",
                 x=0.02, ha="left", fontsize=13, fontweight="bold", y=0.97)
    fig.text(0.02, 0.885, "Positive = the first arm is more often right. An interval crossing zero means the run cannot tell the two apart.",
             fontsize=10, color=INK2)
    fig.savefig(out / "paired_differences.png", dpi=150)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--household", default="hh_001__bank0")
    ap.add_argument("--study-dir", type=pathlib.Path, default=STUDY_DIR / "main")
    args = ap.parse_args()
    arms = load(args.household, args.study_dir)
    add_partial_log_reader(arms, args.study_dir, args.household)
    out = args.study_dir / args.household / "figures"; out.mkdir(exist_ok=True)
    missing = [k for k, *_ in ARMS if k not in arms]
    if missing:
        print("not in this run (skipped):", ", ".join(missing))
    fig_main(arms, out, args.household)
    fig_paired(arms, out, args.household)
    print("wrote", out / "main_active_accuracy.png", "and", out / "paired_differences.png")


if __name__ == "__main__":
    main()
