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


def figure_3(style_name):
    """Told the cause: the prediction, the day that confirmed it, the night that retracted it.

    Every quote is read from the claim's own revision history at the night in question. The history
    stores the text a revision REPLACED, under `was`, as a whole prior state - so the night-13
    wording is the `was` of the first revision after night 13, not `statement`, which is what the
    claim says on night 31.
    """
    style = dict(STYLES[style_name])
    apply(style)
    night13 = ("Tomas is unwell and staying home. Expect him in bedroom_1 or living room "
               "during day/evening, not office. His laptop/mug/charger likely in bedroom_1 "
               "or living, not office desk.")
    night14 = ("Tomas works from the office during the day (seen 14:08)… The 'unwell' "
               "hypothesis from Day 13 is not supported by Day 14 activity.")
    glass = "Tomas's glass is on the bedroom nightstand during the day (seen 08:07-15:12)."
    bedroom, living, office, total = 7, 4, 0, 11
    note(f"  figure 3 [{style_name}] day 14, Tomas's moved objects: {total} questions, "
         f"bedroom_1 {bedroom}, living {living}, office {office}")
    note(f"  figure 3 [{style_name}] night 13 quote: {night13!r}")
    note(f"  figure 3 [{style_name}] night 14 quote: {night14!r}")
    note(f"  figure 3 [{style_name}] night 14 glass note (a night-13 claim revised): {glass!r}")

    fig = plt.figure(figsize=(WIDTH_IN, 2.45))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 0.92, 1.25], wspace=0.30)
    ours = COLOUR["log and notes"]

    def card(ax, text, x, y, w, h, colour, size=6.2, italic=True):
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor="#fbfbfa", edgecolor=colour, lw=0.9))
        ax.text(x + 0.045, y + h - 0.055, text, ha="left", va="top", fontsize=size,
                color=INK, wrap=True, style="italic" if italic else "normal",
                linespacing=1.45, transform=ax.transData)

    # --- panel 1: the prediction
    ax = fig.add_subplot(gs[0])
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Night 13: told one sentence,\nwrites a prediction", fontsize=8,
                 fontweight=style["weight"], pad=4, linespacing=1.3)
    card(ax, _wrap(night13, 30), 0.02, 0.06, 0.96, 0.78, ours)

    # --- panel 2: the day that confirmed it
    ax = fig.add_subplot(gs[1])
    ax.set_title("Day 14: the prediction is right", fontsize=8,
                 fontweight=style["weight"], pad=4)
    left = 0
    for count, colour, label in ((bedroom + living, ours, "predicted rooms"),
                                 (office, "#c0392b", "office"),
                                 (total - bedroom - living - office, "#cfcfca", "other")):
        if count == 0 and label != "office":
            continue
        ax.barh([0], [count], left=left, height=0.5, color=colour, lw=0)
        if count:
            ax.text(left + count / 2, 0, f"{count} of {total}\n{100*count/total:.0f}%",
                    ha="center", va="center", fontsize=7, color="white",
                    fontweight=style["weight"], linespacing=1.2)
        left += count
    ax.text(total, 0, "  office: 0", ha="left", va="center", fontsize=7, color="#c0392b",
            fontweight=style["weight"])
    ax.set_xlim(0, total * 1.42)
    ax.set_ylim(-0.75, 0.75)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.grid(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.text(0, -0.52, f"bedroom_1 {bedroom} · living {living} · office {office}",
            ha="left", va="center", fontsize=6.4, color=MUTED)

    # --- panel 3: the retraction, beside the note written the same night
    ax = fig.add_subplot(gs[2])
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Night 14: the update retracts it", fontsize=8,
                 fontweight=style["weight"], pad=4)
    # WRAPPED TO THE CARD, NOT TO A GUESS. At 30 characters the two cards' text ran straight
    # through each other and the panel was unreadable; the cards are half the width of panel 1's,
    # so the wrap has to be too.
    card(ax, _wrap(night14, 19), 0.01, 0.06, 0.47, 0.78, ours, size=5.8)
    card(ax, _wrap(glass, 19), 0.52, 0.06, 0.47, 0.78, MUTED, size=5.8)
    ax.text(0.755, 0.035, "revised the same night", ha="center", va="top", fontsize=5.9,
            color=MUTED, fontweight=style["weight"])
    ax.annotate("written the same night", xy=(0.5, 0.905), ha="center", va="bottom",
                fontsize=6.4, color=INK, fontweight=style["weight"])
    ax.plot([0.04, 0.96], [0.885, 0.885], color=MUTED, lw=0.6)
    for x in (0.04, 0.96):
        ax.plot([x, x], [0.858, 0.885], color=MUTED, lw=0.6)

    fig.subplots_adjust(left=0.015, right=0.985, top=0.80, bottom=0.04)
    # the arrows that make it a strip rather than three pictures
    for x in (0.345, 0.635):
        fig.add_artist(matplotlib.patches.FancyArrowPatch(
            (x, 0.42), (x + 0.022, 0.42), transform=fig.transFigure,
            arrowstyle="-|>", mutation_scale=8, color=MUTED, lw=0.9))
    out = OUT / style_name / "figure3_told_the_cause.pdf"
    fig.savefig(out)
    plt.close(fig)
    note(f"  wrote {out}")


def _wrap(text, width):
    import textwrap
    return "\n".join(textwrap.wrap(text, width))


def figure_A2(style_name):
    """Night 31: what the notes held, and the hour "evening" slid to."""
    style = dict(STYLES[style_name])
    apply(style)
    audit = json.load(open("results/self_improve/paper/night31_audit.json"))
    thresh = json.load(open("results/self_improve/paper/evening_threshold.json"))
    order = ["claim store", "log and notes", "reduced ACE", "tight working memory"]
    conds = [("always", "#4a4a48"), ("a time of day", "#8a8a86"),
             ("a person home or away", "#b9b9b4"), ("other", "#dcdcd8")]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_IN, 2.5),
                                 gridspec_kw={"width_ratios": [1.05, 1.0], "wspace": 0.32})
    # --- left: the notes, by the condition attached
    xs = list(range(len(order)))
    bottoms = [0] * len(order)
    for name, colour in conds:
        vals = [audit["by_arm"][m].get(name, 0) for m in order]
        ax.bar(xs, vals, bottom=bottoms, color=colour, width=0.62, lw=0, label=name)
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    for x, total in zip(xs, bottoms):
        ax.text(x, total + 5, str(total), ha="center", va="bottom", fontsize=7.5,
                color=INK, fontweight=style["weight"])
    ax.bar([len(order)], [0], color="none", edgecolor="#c0392b", lw=1.0, width=0.62)
    ax.plot([len(order) - 0.31, len(order) + 0.31], [0, 0], color="#c0392b", lw=1.2)
    ax.text(len(order), 5, "0", ha="center", va="bottom", fontsize=10, color="#c0392b",
            fontweight="bold")
    ax.set_xticks(xs + [len(order)])
    # the full names collided at this width; these are the same methods, shortened, and the
    # caption carries the full ones
    ax.set_xticklabels(["claim\nstore", "log and\nnotes", "reduced\nACE", "tight\nmemory",
                        "mentions\nillness"], fontsize=6.4)
    ax.set_ylabel("live notes naming an object\nand one of its illness places",
                  fontweight=style["weight"], fontsize=7.6)
    ax.set_ylim(0, max(bottoms) * 1.22)
    ax.grid(axis="x", visible=False)
    leg = ax.legend(loc="upper right", fontsize=6.4, handlelength=1.0, labelspacing=0.22,
                    borderpad=0.25, frameon=False, title="the condition attached")
    leg.get_title().set_fontsize(6.4)
    note(f"  figure A2 [{style_name}] totals " +
         ", ".join(f"{m} {t}" for m, t in zip(order, bottoms)) +
         f"; grand total {sum(bottoms)}; mentioning illness 0")
    for name, _ in conds:
        note(f"  figure A2 [{style_name}] condition '{name}': "
             + ", ".join(f"{m} {audit['by_arm'][m].get(name, 0)}" for m in order))

    # --- right: the hour "evening" slid to
    nights = [n for n, _ in thresh]
    hours = [h for _, h in thresh]
    bx.axhspan(6, 23, color=SHADE, lw=0, zorder=0)
    bx.text(nights[-1], 22.4, "he was in the house every one of these hours",
            ha="right", va="top", fontsize=6.2, color=MUTED)
    bx.plot(nights, hours, color=COLOUR["ACE-style"], marker="D", ms=4.2, lw=1.6,
            markeredgecolor="white", markeredgewidth=0.5, zorder=3)
    # anchored inside the axes rather than offset from the point, which ran off the right edge
    bx.annotate("'evening' now starts at 11:47", xy=(min(nights) + 0.4, 8.4), ha="left",
                va="center", fontsize=6.8, color=INK, fontweight=style["weight"])
    bx.annotate("", xy=(nights[hours.index(min(hours))], min(hours) - 0.35),
                xytext=(min(nights) + 3.2, 8.9),
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    bx.set_ylim(6, 24)
    bx.set_yticks([6, 9, 12, 15, 18, 21, 24])
    bx.set_yticklabels([f"{h:02d}:00" for h in (6, 9, 12, 15, 18, 21, 24)], fontsize=7)
    bx.set_xlim(min(nights) - 0.5, max(nights) + 0.5)
    bx.set_xlabel("night", fontweight=style["weight"])
    bx.set_ylabel("the hour it says ‘evening’ begins", fontweight=style["weight"],
                  fontsize=7.6)
    bx.grid(axis="x", visible=False)
    note(f"  figure A2 [{style_name}] threshold by night: "
         + ", ".join(f"n{n} {int(h):02d}:{int(round((h%1)*60)):02d}" for n, h in thresh))
    if style["title"]:
        ax.set_title("What the notes held on night 31", fontsize=8,
                     fontweight=style["weight"], pad=6)
        bx.set_title("and what 'evening' came to mean", fontsize=8,
                     fontweight=style["weight"], pad=6)
    fig.subplots_adjust(left=0.115, right=0.985, top=0.86 if style["title"] else 0.95,
                        bottom=0.20)
    out = OUT / style_name / "figureA2_what_the_notes_held.pdf"
    fig.savefig(out)
    plt.close(fig)
    note(f"  wrote {out}")
