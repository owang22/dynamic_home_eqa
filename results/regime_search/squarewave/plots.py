#!/usr/bin/env python3
"""The two figures for the square-wave / indexing questions. Palette: the dataviz reference instance
(categorical slots in their documented order); identity is carried by direct labels and line style as well as hue."""
import json, math, os, statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

import analysis as A

OUT = os.path.dirname(os.path.abspath(__file__))
S1, S2, S3, S4, S5 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8983", "#e7e6e2"
SURFACE = "#fcfcfb"
SHADE = "#f3e3d8"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE})

LLM_HH = sorted(A.EXTRA["person2x"]["llm_naive_nomsg"]["cells"])


def series(pop, method, split, hhs, days, smooth=3):
    """Pooled accuracy per day over `hhs`, as a centred rolling window of `smooth` days (so a day with ~15
    answers is not read as a point estimate). Returns (days, pct)."""
    n = [0] * days
    ok = [0] * days
    for hh in hhs:
        c = A.cells(pop, method, hh)
        if c is None:
            continue
        for d in range(days):
            n[d] += c[split][d][0]
            ok[d] += c[split][d][1]
    xs, ys = [], []
    h = smooth // 2
    for d in range(days):
        lo, hi = max(0, d - h), min(days, d + h + 1)
        nn, kk = sum(n[lo:hi]), sum(ok[lo:hi])
        if nn >= A.MIN_N:
            xs.append(d)
            ys.append(100 * kk / nn)
    return xs, ys


def place_labels(ax, items, x, gap=6.0, lo=0.0, hi=100.0, ha="left", dx=6, fontsize=8):
    """Direct labels at one edge, pushed apart so they never collide."""
    items = sorted(items, key=lambda it: it[0])
    ys = [it[0] for it in items]
    for i in range(1, len(ys)):
        ys[i] = max(ys[i], ys[i - 1] + gap)
    over = ys[-1] - hi
    if over > 0:
        ys = [y - over for y in ys]
        for i in range(len(ys) - 2, -1, -1):
            ys[i] = min(ys[i], ys[i + 1] - gap)
    for y, (y0, text, color, bold) in zip(ys, items):
        ax.annotate(text, (x, max(lo, y)), xytext=(dx, 0), textcoords="offset points", fontsize=fontsize,
                    color=color, va="center", ha=ha, fontweight="bold" if bold else "normal")


def squarewave():
    days = A.DATA["person2x"]["days"]
    classical = [("ttfrozen", S1, "-"), ("tt3d", S2, "-"), ("bma", S3, "-"), ("periodic", S4, "-"),
                 ("lastseen", S5, "-")]
    llm = [("llm_naive_nomsg", S1, "--"), ("llm_retrieval_nomsg", S2, "--")]
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 7.6), sharex=True, sharey=True)
    for col, split in enumerate(("all", "cold")):
        for row, (group, title) in enumerate(((classical, "counters that file evidence (classical)"),
                                              (llm, "language-model memories"))):
            ax = axes[row][col]
            for a, b in ((14, 21), (28, 35)):
                ax.axvspan(a - 0.5, b - 0.5, color=SHADE, lw=0, zorder=0)
            for a, b in ((14, 17), (28, 31)):
                ax.axvspan(a - 0.5, b - 0.5, facecolor="none", edgecolor="#c9a084", lw=1.0, ls=(0, (3, 2)), zorder=1)
            ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
            ax.set_axisbelow(True)
            labels = []
            if row == 1:
                x, y = series("person2x", "ttfrozen", split, LLM_HH, days)
                ax.plot(x, y, color=MUTED, lw=1.2, alpha=0.55, zorder=2)
                labels.append((y[-1], "timetable, never forgets", MUTED, False))
            for key, color, ls in group:
                x, y = series("person2x", key, split, LLM_HH, days)
                ax.plot(x, y, color=color, lw=2.0, ls=ls, zorder=3, solid_capstyle="round")
                labels.append((y[-1], A.LABEL[key].replace("LLM ", ""), color, True))
            place_labels(ax, labels, x[-1])
            ax.set_title(f"{title}   -   {'every question' if split == 'all' else 'cold questions only'}",
                         fontsize=9.5, color=INK, loc="left", pad=6)
            ax.set_xlim(0, days + 9)
            ax.set_ylim(0, 100)
            ax.set_yticks([0, 25, 50, 75, 100])
            ax.set_yticklabels(["0", "25", "50", "75", "100%"])
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            if row == 1:
                ax.set_xlabel("day")
    for ax in axes[0]:
        ax.annotate("spell 1", (17, 96), ha="center", fontsize=8, color="#9a6a45")
        ax.annotate("spell 2", (31, 96), ha="center", fontsize=8, color="#9a6a45")
    fig.suptitle("The square wave: two sick spells, same three households (hh_s0-s2), 3-day rolling accuracy",
                 x=0.012, ha="left", fontsize=13, color=INK, fontweight="bold", y=0.985)
    fig.text(0.012, 0.935, "Shaded = resident off sick (days 14-20 and 28-34); dashed outline = the two opening "
             "windows compared in the paired table (days 14-16 vs 28-30).\nClassical counters are drawn solid, "
             "language-model memories dashed; the grey line repeats the never-forgets timetable for reference.",
             fontsize=8.5, color=INK2, va="top")
    fig.tight_layout(rect=(0, 0, 1, 0.915))
    fig.savefig(f"{OUT}/squarewave.png", dpi=150)
    plt.close(fig)


def indexing():
    order = ["ttfrozen", "tt3d", "bma", "llm_retrieval_nomsg", "llm_naive_nomsg", "llm_reflect_nomsg",
             "llm_routine7_nomsg", "llm_longcontext_nomsg"]
    res = {}
    for m in order:
        p = A.paired("person", m, "cold", range(9, 14), range(27, 32))
        if p["n"]:
            res[m] = p
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.5, 6.6), gridspec_kw={"width_ratios": [1.05, 1]})

    # left: paired slope, lead-up -> late return (mean over the same households in both columns)
    axL.grid(axis="y", color=GRID, lw=0.8)
    axL.set_axisbelow(True)
    right, left = [], []
    for m, p in res.items():
        is_llm = m in A.LLM
        color = S2 if is_llm else S1
        ls = "--" if is_llm else "-"
        a, b = p["acc_a"], p["acc_b"]
        axL.plot([0, 1], [a, b], color=color, lw=2.0, ls=ls, marker="o", ms=7, mec=SURFACE, mew=1.5, zorder=3)
        tag = A.LABEL[m] + (f"  ({p['n']} hh only)" if p["n"] < 10 else "")
        right.append((b, f"{tag}   {b:.0f}%", color, m in ("ttfrozen", "llm_longcontext_nomsg")))
        left.append((a, f"{a:.0f}%", MUTED, False))
    place_labels(axL, right, 1, gap=3.4, lo=36, hi=99, fontsize=8.5, dx=9)
    place_labels(axL, left, 0, gap=2.6, lo=36, hi=95, fontsize=8, dx=-8, ha="right")
    axL.set_xlim(-0.22, 1.95)
    axL.set_ylim(35, 100)
    axL.set_xticks([0, 1])
    axL.set_xticklabels(["settled lead-up\n(days 9-13)", "late return\n(days 27-31)"], fontsize=9)
    axL.set_ylabel("cold accuracy")
    axL.set_yticks([40, 50, 60, 70, 80, 90, 100])
    axL.set_yticklabels(["40", "50", "60", "70", "80", "90", "100%"])
    for sp in ("top", "right"):
        axL.spines[sp].set_visible(False)
    axL.set_title("Does it come back to where it started?", fontsize=10.5, color=INK, loc="left", pad=8)
    axL.legend(handles=[Line2D([], [], color=S1, lw=2, label="classical counter"),
                        Line2D([], [], color=S2, lw=2, ls="--", label="language-model memory")],
               loc="lower left", frameon=False, fontsize=8.5)

    # right: the paired per-household difference, with +/-1 SE and the 2 SE bar
    ms = sorted(res, key=lambda m: res[m]["mean"])
    ys = range(len(ms))
    axR.axvline(0, color=MUTED, lw=1)
    for y, m in zip(ys, ms):
        p = res[m]
        color = S2 if m in A.LLM else S1
        axR.errorbar(p["mean"], y, xerr=p["se"], color=color, fmt="o", ms=8, lw=2.2, capsize=4,
                     mec=SURFACE, mew=1.5, zorder=3)
        axR.errorbar(p["mean"], y, xerr=2 * p["se"], color=color, fmt="none", lw=0.9, alpha=0.5, capsize=0, zorder=2)
        axR.annotate(f"{p['mean']:+.1f} ± {p['se']:.1f}   n={p['n']}", (p["mean"], y), xytext=(0, 11),
                     textcoords="offset points", fontsize=8, color=INK2, ha="center")
    axR.set_yticks(list(ys))
    axR.set_yticklabels([A.LABEL[m] + ("  (3 hh only)" if res[m]["n"] < 10 else "") for m in ms], fontsize=9)
    axR.set_ylim(-0.7, len(ms) - 0.3)
    axR.set_xlabel("late return minus settled lead-up (percentage points, paired by household)")
    axR.grid(axis="x", color=GRID, lw=0.8)
    axR.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        axR.spines[sp].set_visible(False)
    axR.set_title("Paired drop, per household (thick bar = 1 SE, thin = 2 SE)", fontsize=10.5, color=INK,
                  loc="left", pad=8)

    fig.suptitle("Indexed forever vs unindexed forever: cold accuracy before the spell and after it",
                 x=0.012, ha="left", fontsize=13, color=INK, fontweight="bold", y=0.985)
    fig.text(0.012, 0.935, "Population: one sick spell (days 14-23). Each row uses the SAME households in both "
             "windows. Long context ran on 3 of 10 households - flagged, and not used to carry a conclusion.",
             fontsize=8.5, color=INK2, va="top")
    fig.tight_layout(rect=(0, 0, 1, 0.915))
    fig.savefig(f"{OUT}/indexing.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    squarewave()
    indexing()
    print("wrote", f"{OUT}/squarewave.png", f"{OUT}/indexing.png")
