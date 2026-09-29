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

# STANDING RULES, applied to BOTH styles and overriding the written spec where they disagree:
# axis labels and titles are capitalised, every piece of text is bold, and anything that needs a
# sentence to explain lives in the caption file beside the figure, not on the figure.
STYLES = {"spec": {"weight": "bold", "band": True, "title": True, "legend": "inside",
                   "letters": False, "lines": 5},
          "oliver": {"weight": "bold", "band": False, "title": True, "legend": "below",
                     "letters": True, "lines": 3}}
NUMBERS = []          # everything drawn, for FIGURES.md


# ANY TEXT DRAWN OVER THE PLOT AREA GETS ITS OWN BOX. Lines and shading read through unboxed
# text and make it hard to read; this is the same white, barely-padded box everywhere so the
# figures stay consistent.
BOX = dict(facecolor="white", edgecolor="none", alpha=0.85, boxstyle="round,pad=0.25")


def _place(style_name, stem):
    """Each figure gets a directory of its own, so its caption sits beside it."""
    folder = OUT / style_name / stem
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{stem}.pdf"


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
                    ha="center", va="bottom", fontsize=8.5, color=MUTED, bbox=BOX,
                    fontweight=style["weight"], annotation_clip=False)


def finish(fig, ax, style, names, title, ylab, days, counts_strip=None):
    ax.set_ylim(0, 100)
    ax.set_xlim(days[0] - 0.5, days[-1] + 0.5)
    ax.set_ylabel(ylab, fontweight=style["weight"])
    ax.set_xlabel("Day", fontweight=style["weight"])
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
    """Both illnesses, day by day, on the objects that move in both.

    NO QUESTIONS-A-DAY STRIP. It cluttered the figure to carry a fact that belongs in a sentence,
    and the figure is about how fast each memory comes back, not about the sample behind each point.
    The annotations say that: three days after each illness begins, where each of the two leading
    lines has got back to.
    """
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
        note(f"  figure 2 [{style_name}] {n:15s} day 14 {line[13]:5.1f}  days 15-17 "
             f"{statistics.mean(line[14:17]):5.1f}  day 32 {line[31]:5.1f}  days 33-35 "
             f"{statistics.mean(line[32:35]):5.1f}")
    height = 3.1 if style_name == "spec" else 3.3
    fig, ax = plt.subplots(figsize=(WIDTH_IN, height))
    draw_lines(ax, days, names, curves, style)
    shade_sick(ax, [(14, 23), (32, 41)], style, top=100)
    ax.set_ylim(0, 140)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlim(0.5, 49.5)
    ax.set_xticks([1, 14, 24, 32, 42, 49])
    ax.set_ylabel("First Room Right (%)", fontweight=style["weight"])
    ax.set_xlabel("Day", fontweight=style["weight"])
    ax.grid(axis="x", visible=False)

    def three_days_after(start_day):
        return {n: statistics.mean(curves[n][0][start_day:start_day + 3]) for n in names}

    for start_day, x, ha in ((14, 14.6, "left"), (32, 32.6, "left")):
        after = three_days_after(start_day)
        ours, rule = after["log and notes"], after["LastSeen"]
        ax.annotate(f"three days in:\nlog and notes {ours:.0f}%\nLastSeen {rule:.0f}%",
                    xy=(x, 138), ha=ha, va="top", fontsize=7.0, color=INK, bbox=BOX,
                    fontweight=style["weight"], linespacing=1.25)
        note(f"  figure 2 [{style_name}] three days after day {start_day}: "
             + ", ".join(f"{n} {v:.1f}" for n, v in after.items()))
    if style["title"]:
        ax.set_title("The Same Illness, Twice", fontweight=style["weight"], pad=14)
    handles = [plt.Line2D([], [], color=COLOUR[n], marker=MARKER[n], lw=1.6, ms=4.5,
                          markeredgecolor="white", markeredgewidth=0.5, label=n) for n in names]
    if style["legend"] == "inside":
        ax.legend(handles=handles, loc="lower right", fontsize=7.4, handlelength=1.5,
                  labelspacing=0.26, borderpad=0.4, facecolor="white", framealpha=0.9,
                  frameon=True, edgecolor="#d8d8d4")
        fig.subplots_adjust(left=0.115, right=0.985, top=0.855, bottom=0.125)
    else:
        fig.subplots_adjust(left=0.115, right=0.985, top=0.855, bottom=0.30)
        leg = fig.legend(handles=handles, loc="upper center", ncol=len(names), fontsize=8,
                         frameon=False, handlelength=1.5, columnspacing=1.2,
                         bbox_to_anchor=(0.56, 0.20))
        for txt in leg.get_texts():
            txt.set_fontweight("bold")
    out = _place(style_name, "figure2_both_illnesses")
    fig.savefig(out)
    plt.close(fig)
    note(f"  wrote {out}   both-illness-mover questions a day: "
         f"{min(counts.values())} to {max(counts.values())}")


def figure_3(style_name):
    """Told the cause, then retracting it: two notes, and one line about the day between them.

    THE MIDDLE PANEL IS GONE. It was a stacked bar of eleven questions that said one thing - they
    were all in a predicted room - and a bar chart of a single 11-of-11 count tells a reader
    nothing a sentence does not. It is a sentence now, on the arrow between the two nights.
    "bedroom_1 7" also read as "bedroom_17", so the counts are written out in words.

    Every quote comes from the claim's own revision history at the night in question: the history
    stores the text a revision REPLACED, under `was`, so night 13's wording is the `was` of the
    first revision after night 13, not `statement`, which is what the claim says on night 31.
    """
    style = dict(STYLES[style_name])
    apply(style)
    night13 = ("Tomas is unwell and staying home. Expect him in bedroom_1 or living room "
               "during day/evening, not office. His laptop/mug/charger likely in bedroom_1 "
               "or living, not office desk.")
    night14 = ("Tomas works from the office during the day (seen 14:08)\u2026 The 'unwell' "
               "hypothesis from Day 13 is not supported by Day 14 activity.")
    glass = "Tomas's glass is on the bedroom nightstand during the day (seen 08:07-15:12)."
    bedroom, living, office, total = 7, 4, 0, 11
    note(f"  figure 3 [{style_name}] day 14, Tomas's moved objects: {total} questions, "
         f"bedroom_1 {bedroom}, living {living}, office {office}")
    for label, q in (("night 13", night13), ("night 14", night14), ("night 14 glass", glass)):
        note(f"  figure 3 [{style_name}] {label} quote: {q!r}")

    fig = plt.figure(figsize=(WIDTH_IN, 3.25))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.06, 0.88, 1.06], wspace=0.14)
    ours = COLOUR["log and notes"]
    SIZE = 7.4

    def card(ax, text, top, width_chars=24, size=SIZE, label=None):
        body = _wrap(text, width_chars)
        lines = body.count("\n") + 1
        height = 0.055 * lines + 0.085
        ax.add_patch(plt.Rectangle((0.0, top - height), 1.0, height, facecolor="#fbfbfa",
                                   edgecolor=ours, lw=1.1))
        ax.text(0.05, top - 0.048, body, ha="left", va="top", fontsize=size, color=INK,
                style="italic", linespacing=1.5)
        if label:
            ax.text(0.5, top - height - 0.024, label, ha="center", va="top", fontsize=6.9,
                    color=MUTED, fontweight=style["weight"], linespacing=1.3)
        return top - height

    ax = fig.add_subplot(gs[0])
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Night 13\nTold One Sentence,\nWrites a Prediction", fontsize=8.4,
                 fontweight=style["weight"], pad=6, linespacing=1.35)
    card(ax, night13, 0.94)

    # the middle is an arrow and a sentence, not a chart
    mid = fig.add_subplot(gs[1])
    mid.set_axis_off()
    mid.set_xlim(0, 1)
    mid.set_ylim(0, 1)
    mid.set_title("Day 14\nEvery Prediction\nHolds", fontsize=8.4,
                  fontweight=style["weight"], pad=6, linespacing=1.35)
    mid.annotate("", xy=(0.97, 0.60), xytext=(0.03, 0.60),
                 arrowprops=dict(arrowstyle="-|>,head_width=3.4,head_length=5.0",
                                 mutation_scale=2.2, color="#4a4a48", lw=2.2))
    mid.text(0.5, 0.545, _wrap(f"all {total} questions about his moved objects were answered in "
                               f"a room the note named: {bedroom} in bedroom_1, {living} in the "
                               f"living room, none in the office", 26),
             ha="center", va="top", fontsize=7.2, color=INK, linespacing=1.45,
             fontweight=style["weight"])

    ax = fig.add_subplot(gs[2])
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Night 14\nThe Update\nRetracts It", fontsize=8.4,
                 fontweight=style["weight"], pad=6, linespacing=1.35)
    bottom = card(ax, night14, 0.94)
    card(ax, glass, bottom - 0.105, label="revised the same night")
    ax.text(0.5, bottom - 0.052, "and, the same night:", ha="center", va="center",
            fontsize=7.0, color=MUTED, fontweight=style["weight"])

    fig.subplots_adjust(left=0.025, right=0.975, top=0.80, bottom=0.03)
    out = _place(style_name, "figure3_told_the_cause")
    fig.savefig(out)
    plt.close(fig)
    note(f"  wrote {out}")


def _wrap(text, width):
    import textwrap
    return "\n".join(textwrap.wrap(text, width))


def figure_A2(style_name):
    """Two panels, each labelled and captioned: what the notes held, and what "evening" came to mean.

    REBUILT after a reader with no context could not say what the right half claimed. It was two
    unrelated charts under one caption that named a night only the left one shows; "mentions
    illness" sat on an axis whose other entries were methods; and the four greys could not be told
    apart at this size.

    The four conditions are ORDERED, from the most general to the least, so they are drawn as a
    single-hue ramp with monotone lightness rather than four categorical colours - every
    four-colour categorical set tried failed the checker's lightness band. The count is printed on
    every segment big enough to hold it, so nothing depends on telling two steps apart.
    """
    style = dict(STYLES[style_name])
    apply(style)
    audit = json.load(open("results/self_improve/paper/night31_audit.json"))
    thresh = json.load(open("results/self_improve/paper/evening_threshold.json"))
    order = ["claim store", "log and notes", "reduced ACE", "tight working memory"]
    conds = [("always", "#08306b"), ("a time of day", "#2b7bba"),
             ("a person home or away", "#7fb8da"), ("other", "#cfe1f2")]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(WIDTH_IN, 2.9),
                                 gridspec_kw={"width_ratios": [1.0, 1.0], "wspace": 0.34})
    # ---------------------------------------------------------------- (a)
    xs = list(range(len(order)))
    bottoms = [0] * len(order)
    for name, colour in conds:
        vals = [audit["by_arm"][m].get(name, 0) for m in order]
        ax.bar(xs, vals, bottom=bottoms, color=colour, width=0.66, lw=0, label=name)
        for x, v, b in zip(xs, vals, bottoms):
            if v >= 12:
                ax.text(x, b + v / 2, str(v), ha="center", va="center", fontsize=6.4,
                        color="white" if colour in ("#08306b", "#2b7bba") else INK)
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    for x, total in zip(xs, bottoms):
        ax.text(x, total + 4, str(total), ha="center", va="bottom", fontsize=7.6,
                color=INK, fontweight=style["weight"])
    ax.set_xticks(xs)
    ax.set_xticklabels(["claim\nstore", "log and\nnotes", "reduced\nACE", "tight\nmemory"],
                       fontsize=6.8)
    ax.set_ylabel("Live Notes (count)", fontweight=style["weight"])
    # ROOM RATHER THAN BOXES. Boxing the legend and the red note only made their collisions
    # visible; the panel needed headroom so the two could sit side by side above the tallest bar.
    ax.set_ylim(0, max(bottoms) * 1.60)
    ax.grid(axis="x", visible=False)
    # NOT a fifth bar on the method axis: it is a fact about all four, so it is written as one.
    # over the shortest bar, where there is room: at the top it sat on the legend
    # over the shortest bar and inside the axes: at the top right it crowded the "114" label and
    # its first line was clipped by the axis edge
    # ABOVE THE AXES, NOT IN THEM. This is a sentence, and a sentence is 22 characters wide in a
    # 2.2 inch panel: wherever it was put inside, it covered a bar or a total. Above the axes it
    # has the full width of the panel and covers nothing.
    ax.text(0.5, 1.012, f"none of these {sum(bottoms)} notes mentions the illness",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=7.2,
            color="#b03020", fontweight="bold")
    leg = ax.legend(loc="upper right", fontsize=6.3, handlelength=0.9, labelspacing=0.22,
                    borderpad=0.4, frameon=True, facecolor="white", framealpha=0.95,
                    edgecolor="#d8d8d4", title="the condition the note carries")
    leg.get_title().set_fontsize(6.3)
    ax.set_title("(a)  night 31: notes naming an object\nand a room it moves to when ill",
                 fontsize=7.4, fontweight=style["weight"], pad=17, linespacing=1.3)
    note(f"  figure A2 [{style_name}] (a) totals " +
         ", ".join(f"{m} {b}" for m, b in zip(order, bottoms)) + f", grand total {sum(bottoms)}")

    # ---------------------------------------------------------------- (b)
    nights = [n for n, _ in thresh]
    hours = [h for _, h in thresh]
    bx.plot(nights, hours, color=COLOUR["ACE-style"], marker="D", ms=4.4, lw=1.8,
            markeredgecolor="white", markeredgewidth=0.5, zorder=3)
    plateau = min(hours)
    first_plateau = nights[hours.index(plateau)]
    bx.annotate(f"from night {first_plateau} on,\n\u2018evening\u2019 starts at 11:47",
                xy=(max(nights) + 0.3, plateau - 0.6), ha="right", va="top", fontsize=7.0,
                color=INK, fontweight=style["weight"], linespacing=1.25, bbox=BOX)
    bx.set_ylim(6, 24)
    bx.set_yticks([6, 9, 12, 15, 18, 21, 24])
    bx.set_yticklabels([f"{h:02d}:00" for h in (6, 9, 12, 15, 18, 21, 24)], fontsize=7)
    bx.set_xlim(min(nights) - 0.5, max(nights) + 0.5)
    bx.set_xticks([13, 15, 17, 19, 21])
    bx.set_xlabel("Night", fontweight=style["weight"])
    bx.set_ylabel("\u2018Evening\u2019 Begins At", fontweight=style["weight"], fontsize=7.8)
    bx.grid(axis="x", visible=False)
    bx.set_title("(b)  one ACE-style note:\nwhen it says \u2018evening\u2019 begins",
                 fontsize=7.4, fontweight=style["weight"], pad=5, linespacing=1.3)
    # the shaded band spanned the whole panel, so it marked nothing. It is a sentence now.
    note(f"  figure A2 [{style_name}] (b) threshold by night: "
         + ", ".join(f"n{n} {int(h):02d}:{int(round((h % 1) * 60)):02d}" for n, h in thresh))
    fig.subplots_adjust(left=0.105, right=0.985, top=0.76, bottom=0.135)
    out = _place(style_name, "figureA2_what_the_notes_held")
    fig.savefig(out)
    plt.close(fig)
    note(f"  wrote {out}")
