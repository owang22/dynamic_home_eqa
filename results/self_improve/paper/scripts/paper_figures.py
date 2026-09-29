#!/usr/bin/env python3
"""Every data figure, drawn twice: once to the written specification, once to Oliver's guidance.

The two disagree on four things, so neither is a subset of the other and both are built:

                      the written spec            Oliver's guidance
  lines per axis      four or five               two, at most three
  uncertainty         a +/-1 SE band behind      no band at all
  text weight         regular, no title          bold, including tick numbers, with a title
  the legend          inside if it fits          below the plot, close, one entry a row

Everything else they agree on: first-guess accuracy on y from 0 to 100, day on x, the illness
shaded with "sick" over the band, one fixed colour per method, a 396 pt canvas.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/paper_figures.py
"""
import collections
import json
import pathlib
import statistics
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                     # noqa: E402

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import paper_data as D                                              # noqa: E402
from self_improve import search_driven as sd                        # noqa: E402
from self_improve.frozen_household import FrozenHousehold           # noqa: E402

OUT = pathlib.Path("results/self_improve/paper/figures")
WIDTH_PT = 396.0
WIDTH_IN = WIDTH_PT / 72.0
SHADE = "#e4e4e1"
INK, MUTED = "#1a1a1a", "#6b6b68"

# validated with the dataviz checker: the four that share an axis in Figure 2 pass on all pairs
# with no warning, and adding the wine for Figure A1 keeps that. Grey-green and brown, which the
# specification suggests, both fail - see FIGURE_CHECKS_BEFORE_DRAWING.md.
COLOUR = {"LastSeen": "#0072B2", "log and notes": "#D55E00", "claim store": "#009E73",
          "ACE-style": "#785EF0", "MemGPT-style": "#882255", "notes hidden": "#BBBBBB",
          # THE TEN-HOUSEHOLD RUN HAS NEITHER PUBLISHED METHOD IN IT. Its ACE-shaped and
          # MemGPT-shaped arms are the CONSTRAINED ones, and the MemGPT-shaped arm ran on a
          # 1,200-character block - a sixteenth of MemGPT's own smallest - which memory_notes.py
          # says must be called the tight variant and never MemGPT. They keep the published
          # methods' colours, because they are those methods' cousins, and different names.
          "reduced ACE": "#785EF0", "tight working memory": "#882255"}
MARKER = {"LastSeen": "o", "log and notes": "s", "claim store": "^", "ACE-style": "D",
          "MemGPT-style": "v", "notes hidden": "X",
          "reduced ACE": "D", "tight working memory": "v"}
ARM_DIR = {"LastSeen": "last_seen_no_model", "log and notes": "the_log_and_notes_about_the_routine",
           "claim store": "incremental_edits", "ACE-style": "ACE_as_published",
           "MemGPT-style": "MemGPT_as_published", "notes hidden": "prior_only_no_notes",
           "reduced ACE": "claim_store_told_if_it_was_right",
           "tight working memory": "a_small_working_memory_and_an_archive"}

STYLES = {"spec": {"weight": "normal", "band": True, "title": False, "legend": "inside",
                   "letters": False, "lines": 5},
          "oliver": {"weight": "bold", "band": False, "title": True, "legend": "below",
                     "letters": True, "lines": 3}}
NUMBERS = []          # everything drawn, for FIGURES.md


def note(text):
    NUMBERS.append(text)
    print(text)


def apply(style):
    plt.rcParams.update({
        "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
        "font.weight": style["weight"], "axes.labelweight": style["weight"],
        "axes.titleweight": style["weight"],
        "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
        "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "axes.grid": True, "grid.color": "#dcdcd8", "grid.linewidth": 0.5,
        "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
        "pdf.fonttype": 42, "figure.constrained_layout.use": False,
        "savefig.bbox": "standard", "savefig.pad_inches": 0.01})


def by_day(cells, arm_dir, homes, days, objects_of, banks=None):
    """Per household, then averaged: the spec asks for households averaged, not questions pooled."""
    per_home, counts = {}, collections.Counter()
    for home in homes:
        keep = objects_of(home)
        got = collections.Counter()
        tot = collections.Counter()
        rows = (json.loads((pathlib.Path(cells) / arm_dir / home / "searches.jsonl").read_text()
                           .splitlines()[0]) if False else None)
        for r in D.rows(pathlib.Path(cells), arm_dir, home):
            if r["day"] in days and r["object_id"] in keep:
                tot[r["day"]] += 1
                got[r["day"]] += r.get("found_at_step") == 1
        per_home[home] = {d: (100 * got[d] / tot[d] if tot[d] else None) for d in days}
        for d in days:
            counts[d] += tot[d]
    line, band = [], []
    for d in days:
        vals = [per_home[h][d] for h in homes if per_home[h][d] is not None]
        line.append(statistics.mean(vals) if vals else float("nan"))
        band.append(statistics.stdev(vals) / len(vals) ** 0.5 if len(vals) > 1 else 0.0)
    return line, band, counts, per_home


def shade_sick(ax, spans, style, top=None):
    for first, last in spans:
        ax.axvspan(first - 0.5, last + 0.5, color=SHADE, lw=0, zorder=0,
                   ymax=(top / ax.get_ylim()[1]) if top else 1.0)
        # in the headroom above the labelled range, not inside the data: at 94 it sat behind
        # the log-and-notes line, which reaches 97 mid-illness, and printed as "ick".
        ax.annotate("sick", xy=((first + last) / 2, (top + 6) if top else 101),
                    xycoords=("data", "data"),
                    ha="center", va="bottom", fontsize=8.5, color=MUTED,
                    fontweight=style["weight"], annotation_clip=False)


def finish(fig, ax, style, names, title, ylab, days, counts_strip=None):
    ax.set_ylim(0, 100)
    ax.set_xlim(days[0] - 0.5, days[-1] + 0.5)
    ax.set_ylabel(ylab, fontweight=style["weight"])
    ax.set_xlabel("day", fontweight=style["weight"])
    ax.grid(axis="x", visible=False)
    if style["title"] and title:
        ax.set_title(title, fontweight=style["weight"], pad=14)
    handles = [plt.Line2D([], [], color=COLOUR[n], marker=MARKER[n], lw=1.6, ms=4.5,
                          markeredgecolor="white", markeredgewidth=0.5, label=n) for n in names]
    if style["legend"] == "inside":
        leg = ax.legend(handles=handles, loc="lower right", ncol=1, fontsize=7.8,
                        handlelength=1.6, labelspacing=0.3, borderpad=0.3,
                        facecolor="white", framealpha=0.85, frameon=True, edgecolor="none")
    else:
        leg = fig.legend(handles=handles, loc="upper center", ncol=1, fontsize=8.5,
                         frameon=False, handlelength=1.7, labelspacing=0.32,
                         bbox_to_anchor=(0.5, style["_legend_y"]))
        for t in leg.get_texts():
            t.set_fontweight("bold")
    return leg


def draw_lines(ax, days, names, curves, style):
    for n in names:
        line, band = curves[n]
        if style["band"]:
            ax.fill_between(days, [a - b for a, b in zip(line, band)],
                            [a + b for a, b in zip(line, band)],
                            color=COLOUR[n], alpha=0.14, lw=0, zorder=2)
        ax.plot(days, line, color=COLOUR[n], marker=MARKER[n], lw=1.6, ms=3.8,
                markeredgecolor="white", markeredgewidth=0.5, zorder=4)


def figure_2(style_name):
    """Both illnesses, day by day, on the objects that move in both."""
    style = dict(STYLES[style_name])
    apply(style)
    names = ["LastSeen", "log and notes", "claim store", "ACE-style"]
    if style["lines"] == 3:
        names = ["LastSeen", "log and notes", "ACE-style"]
    days = list(range(1, 50))
    curves, counts = {}, None
    for n in names:
        line, band, counts, per = by_day(D.WAVE_50, ARM_DIR[n], D.HOMES_50, days,
                                         D.both_spell_movers)
        curves[n] = (line, band)
        note(f"  figure 2 [{style_name}] {n:15s} day 14 {line[13]:5.1f}  day 32 {line[31]:5.1f}"
             f"  (per home day 14 "
             + "/".join(f"{per[h][14]:.0f}" for h in D.HOMES_50) + ", day 32 "
             + "/".join(f"{per[h][32]:.0f}" for h in D.HOMES_50) + ")")
    style["_legend_y"] = 0.235
    height = 3.3 if style_name == "spec" else 3.5
    fig, (ax, strip) = plt.subplots(2, 1, figsize=(WIDTH_IN, height), sharex=True,
                                    gridspec_kw={"height_ratios": [5, 1]})
    draw_lines(ax, days, names, curves, style)
    shade_sick(ax, [(14, 23), (32, 41)], style, top=100)
    for first, last in ((14, 23), (32, 41)):
        strip.axvspan(first - 0.5, last + 0.5, color=SHADE, lw=0, zorder=0)
    # THE SPECIFIED WORDING IS NOT WHAT THE DATA SAYS. It asks for "second illness: only
    # summary-only memories drop", but measured against each line's own level on days 28-31 the
    # trail falls 31.4 points on day 32 and our notes 29.2 - not "barely". What is true is that
    # they fall about HALF as far as the summary-only memories, which fall 47.8 and 54.9, whereas
    # on day 14 all four fell within eight points of each other. The numbers are in FIGURES.md.
    # The axis is LABELLED 0 to 100 and drawn to 122, because the specification asks for these two
    # notes "in the empty space above the lines" and there is none - the lines reach 100. The
    # headroom is the empty space; the ticks stop at 100 so the scale still reads 0 to 100.
    # THE WORDING IS COMPUTED FROM THE LINES ACTUALLY DRAWN, because the two styles draw a
    # different number of them and a fixed "all four" was wrong in the three-line version.
    falls = {n: (statistics.mean(curves[n][0][9:13]) - curves[n][0][13],
                 statistics.mean(curves[n][0][27:31]) - curves[n][0][31]) for n in names}
    first = [f for f, _ in falls.values()]
    raw = [falls[n][1] for n in names if n in ("LastSeen", "log and notes")]
    rest = [falls[n][1] for n in names if n not in ("LastSeen", "log and notes")]
    ax.annotate(f"first illness:\nall {'four' if len(names) == 4 else 'three'} fall "
                f"{min(first):.0f}-{max(first):.0f} points",
                xy=(13.2, 120), ha="left", va="top",
                fontsize=7.2, color=INK, fontweight=style["weight"], linespacing=1.2)
    # right-aligned at the axis edge: left-aligned from day 31 it ran off the canvas, and the
    # canvas is fixed so it was simply cut.
    ax.annotate(f"second illness: the trail and our notes\nfall {min(raw):.0f}-{max(raw):.0f} "
                f"points, the rest {min(rest):.0f}-{max(rest):.0f}",
                xy=(49.3, 120), ha="right", va="top", fontsize=7.2, color=INK,
                fontweight=style["weight"], linespacing=1.2)
    strip.bar(days, [counts[d] for d in days], color="#9a9a96", width=0.8, lw=0)
    strip.set_ylabel("questions/day", fontsize=7, fontweight=style["weight"])
    strip.set_yticks([])
    strip.grid(False)
    strip.set_xlabel("day", fontweight=style["weight"])
    ax.set_ylim(0, 122)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlim(0.5, 49.5)
    ax.set_ylabel("first room right (%)", fontweight=style["weight"])
    ax.grid(axis="x", visible=False)
    if style["title"]:
        ax.set_title("The same illness, twice", fontweight=style["weight"], pad=14)
    handles = [plt.Line2D([], [], color=COLOUR[n], marker=MARKER[n], lw=1.6, ms=4.5,
                          markeredgecolor="white", markeredgewidth=0.5, label=n) for n in names]
    if style["legend"] == "inside":
        ax.legend(handles=handles, loc="lower right", fontsize=7.6, handlelength=1.6,
                  labelspacing=0.28, borderpad=0.3, facecolor="white", framealpha=0.9,
                  frameon=True, edgecolor="none")
        fig.subplots_adjust(left=0.10, right=0.985, top=0.90, bottom=0.11, hspace=0.12)
    else:
        fig.subplots_adjust(left=0.10, right=0.985, top=0.88, bottom=0.30, hspace=0.12)
        leg = fig.legend(handles=handles, loc="upper center", ncol=len(names), fontsize=8,
                         frameon=False, handlelength=1.5, columnspacing=1.2,
                         bbox_to_anchor=(0.54, 0.185))
        for t in leg.get_texts():
            t.set_fontweight("bold")
    out = OUT / style_name / "figure2_both_illnesses.pdf"
    fig.savefig(out)
    plt.close(fig)
    note(f"  wrote {out}   both-illness-mover questions a day: "
         f"{min(counts.values())} to {max(counts.values())}")


def figure_A1(style_name):
    """The first illness on the ten households, five methods."""
    style = dict(STYLES[style_name])
    apply(style)
    names = ["LastSeen", "log and notes", "claim store", "reduced ACE", "tight working memory"]
    cells = "results/self_improve/overnight_wave/cells"
    banks = pathlib.Path("results/self_improve/varied_homes/ten_homes/banks")
    movers = lambda h: sd.the_movers(FrozenHousehold(banks / f"{h}.jsonl"))
    have = [n for n in names if (pathlib.Path(cells) / ARM_DIR[n]).exists()]
    if style["lines"] == 3:
        have = [n for n in have if n in ("LastSeen", "log and notes", "reduced ACE")]
    days = list(range(1, 32))
    curves = {}
    for n in have:
        line, band, counts, per = by_day(cells, ARM_DIR[n], D.HOMES_10, days, movers)
        curves[n] = (line, band)
        note(f"  figure A1 [{style_name}] {n:15s} days 10-13 "
             f"{statistics.mean(line[9:13]):5.1f}  day 14 {line[13]:5.1f}  day 24 {line[23]:5.1f}")
    fig, ax = plt.subplots(figsize=(WIDTH_IN, 2.9))
    draw_lines(ax, days, have, curves, style)
    ax.set_ylim(0, 122)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlim(0.5, 31.5)
    shade_sick(ax, [(14, 23)], style, top=100)
    lo = min(curves[n][0][13] for n in have)
    hi = max(curves[n][0][13] for n in have)
    ax.annotate(f"all methods fall to {lo:.0f}-{hi:.0f}%", xy=(14.6, 119), ha="left", va="top",
                fontsize=7.4, color=INK, fontweight=style["weight"])
    ax.set_ylabel("first room right (%)", fontweight=style["weight"])
    ax.set_xlabel("day", fontweight=style["weight"])
    ax.grid(axis="x", visible=False)
    if style["title"]:
        ax.set_title("Adapting inside the first illness", fontweight=style["weight"], pad=12)
    handles = [plt.Line2D([], [], color=COLOUR[n], marker=MARKER[n], lw=1.6, ms=4.5,
                          markeredgecolor="white", markeredgewidth=0.5, label=n) for n in have]
    if style["legend"] == "inside":
        ax.legend(handles=handles, loc="lower right", fontsize=7.4, handlelength=1.5,
                  labelspacing=0.26, borderpad=0.3, facecolor="white", framealpha=0.9,
                  frameon=True, edgecolor="none")
        fig.subplots_adjust(left=0.105, right=0.985, top=0.90, bottom=0.135)
    else:
        fig.subplots_adjust(left=0.105, right=0.985, top=0.87, bottom=0.30)
        leg = fig.legend(handles=handles, loc="upper center", ncol=len(have), fontsize=8,
                         frameon=False, handlelength=1.5, columnspacing=1.2,
                         bbox_to_anchor=(0.54, 0.18))
        for txt in leg.get_texts():
            txt.set_fontweight("bold")
    out = OUT / style_name / "figureA1_first_illness.pdf"
    fig.savefig(out)
    plt.close(fig)
    note(f"  wrote {out}")
