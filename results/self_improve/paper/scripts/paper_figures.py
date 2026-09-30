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

# THE BASELINE IS BLACK AND DOTTED, and the two methods it is measured against are the brightest
# pair that passes the checker: #EE6100 against #8A3FFC clears every check with no warning at all,
# where the older #D55E00 against #785EF0 only just cleared the contrast one. The five that share
# an axis in Figure A1 pass on all pairs, not only adjacent ones. Grey-green and brown, which the
# specification suggests, both fail - see FIGURE_CHECKS_BEFORE_DRAWING.md.
COLOUR = {"last-seen": "#000000", "log and notes": "#EE6100", "claim store": "#009E73",
          "ACE-style": "#8A3FFC", "MemGPT-style": "#882255", "notes hidden": "#BBBBBB",
          # THE TEN-HOUSEHOLD RUN HAS NEITHER PUBLISHED METHOD IN IT. Its ACE-shaped and
          # MemGPT-shaped arms are the CONSTRAINED ones, and the MemGPT-shaped arm ran on a
          # 1,200-character block - a sixteenth of MemGPT's own smallest - which memory_notes.py
          # says must be called the tight variant and never MemGPT. They keep the published
          # methods' colours, because they are those methods' cousins, and different names.
          "reduced ACE": "#8A3FFC", "tight working memory": "#882255"}
# EVERY line is dashed, the baseline included. The table stays so a method can be given its own
# pattern later; today they all share one.
LINESTYLE = collections.defaultdict(lambda: "--")

# WHAT THE DRAFT CALLS EACH ARM, which is not always what this module keys it by. Two DIFFERENT
# arms are both called "ACE-style playbook" in the paper - `ACE_as_published` in the 50-day run and
# `claim_store_told_if_it_was_right` in the ten-household run - so they keep separate keys here and
# share one label. The same is true of the 1,200-character working memory, which the paper calls
# MemGPT-style and which memory_notes.py says must never be called MemGPT without a qualifier.
LABEL = {"ACE-style": "ACE-style playbook", "reduced ACE": "ACE-style playbook",
         "tight working memory": "MemGPT-style working memory"}


def label(name):
    return LABEL.get(name, name)
MARKER = {"last-seen": "o", "log and notes": "s", "claim store": "^", "ACE-style": "D",
          "MemGPT-style": "v", "notes hidden": "X",
          "reduced ACE": "D", "tight working memory": "v"}
ARM_DIR = {"last-seen": "last_seen_no_model", "log and notes": "the_log_and_notes_about_the_routine",
           "claim store": "incremental_edits", "ACE-style": "ACE_as_published",
           "MemGPT-style": "MemGPT_as_published", "notes hidden": "prior_only_no_notes",
           "reduced ACE": "claim_store_told_if_it_was_right",
           "tight working memory": "a_small_working_memory_and_an_archive"}

# STANDING RULES, applied to BOTH styles and overriding the written spec where they disagree:
# axis labels and titles are capitalised, every piece of text is bold, and anything that needs a
# sentence to explain lives in the caption file beside the figure, not on the figure.
STYLES = {"spec": {"weight": "bold", "band": True, "title": True, "legend": "inside",
                   "letters": False, "lines": 5, "annotate": True},
          # no boxed accuracy numbers on the plot: the caption carries them and they are clutter
          # on a figure whose lines already show the gap.
          "oliver": {"weight": "bold", "band": False, "title": True, "legend": "below",
                     "letters": True, "lines": 3, "annotate": False}}
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
    handles = [plt.Line2D([], [], color=COLOUR[n], marker=MARKER[n], linestyle=LINESTYLE[n],
                          lw=1.6, ms=4.5,
                          markeredgecolor="white", markeredgewidth=0.5, label=label(n)) for n in names]
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
        ax.plot(days, line, color=COLOUR[n], marker=MARKER[n], linestyle=LINESTYLE[n],
                lw=1.6, ms=3.8, markeredgecolor="white", markeredgewidth=0.5, zorder=4)


def figure_2(style_name):
    """Both illnesses, day by day, on the objects that move in both.

    NO QUESTIONS-A-DAY STRIP. It cluttered the figure to carry a fact that belongs in a sentence,
    and the figure is about how fast each memory comes back, not about the sample behind each point.
    The annotations say that: three days after each illness begins, where each of the two leading
    lines has got back to.
    """
    style = dict(STYLES[style_name])
    apply(style)
    names = ["last-seen", "log and notes", "claim store", "ACE-style"]
    if style["lines"] == 3:
        names = ["last-seen", "log and notes", "ACE-style"]
    days = list(range(1, 50))
    curves, counts = {}, None
    for n in names:
        line, band, counts, per = by_day(D.WAVE_50, ARM_DIR[n], D.HOMES_50, days,
                                         D.both_spell_movers)
        curves[n] = (line, band)
        note(f"  figure 2 [{style_name}] {n:15s} day 14 {line[13]:5.1f}  days 15-17 "
             f"{statistics.mean(line[14:17]):5.1f}  day 32 {line[31]:5.1f}  days 33-35 "
             f"{statistics.mean(line[32:35]):5.1f}")
    height = 3.1 if style["annotate"] else 2.65
    fig, ax = plt.subplots(figsize=(WIDTH_IN, height))
    draw_lines(ax, days, names, curves, style)
    shade_sick(ax, [(14, 23), (32, 41)], style, top=100)
    # only enough headroom for what is actually drawn above the data
    ax.set_ylim(0, 140 if style["annotate"] else 112)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlim(0.5, 49.5)
    ax.set_xticks([1, 14, 24, 32, 42, 49])
    ax.set_ylabel("First Room Right (%)", fontweight=style["weight"])
    # the label sits close to its own axis, which widens the gap to the legend below without
    # spending any more of the canvas on white
    ax.set_xlabel("Day", fontweight=style["weight"], labelpad=1.5)
    ax.grid(axis="x", visible=False)

    def three_days_after(start_day):
        return {n: statistics.mean(curves[n][0][start_day:start_day + 3]) for n in names}

    for start_day, x, ha in ((14, 14.6, "left"), (32, 32.6, "left")):
        after = three_days_after(start_day)
        if style["annotate"]:
            ax.annotate(f"three days in:\nlog and notes {after['log and notes']:.0f}%\n"
                        f"last-seen {after['last-seen']:.0f}%",
                        xy=(x, 138), ha=ha, va="top", fontsize=7.0, color=INK, bbox=BOX,
                        fontweight=style["weight"], linespacing=1.25)
        note(f"  figure 2 [{style_name}] three days after day {start_day}: "
             + ", ".join(f"{n} {v:.1f}" for n, v in after.items()))
    if style["title"]:
        ax.set_title("The Same Illness, Twice", fontweight=style["weight"], pad=14)
    handles = [plt.Line2D([], [], color=COLOUR[n], marker=MARKER[n], linestyle=LINESTYLE[n],
                          lw=1.6, ms=4.5,
                          markeredgecolor="white", markeredgewidth=0.5, label=label(n)) for n in names]
    if style["legend"] == "inside":
        ax.legend(handles=handles, loc="lower right", fontsize=7.4, handlelength=1.5,
                  labelspacing=0.26, borderpad=0.4, facecolor="white", framealpha=0.9,
                  frameon=True, edgecolor="#d8d8d4")
        fig.subplots_adjust(left=0.115, right=0.985, top=0.855, bottom=0.125)
    else:
        # AT THE FOOT OF THE FIGURE, with the axes lifted to leave room. Both an axes-relative
        # and a figure-relative anchor landed on the "Day" label; letting matplotlib place it at
        # the bottom and reserving the space is the one that cannot collide.
        fig.subplots_adjust(left=0.105, right=0.99, top=0.885, bottom=0.26)
        leg = fig.legend(handles=handles, loc="lower center", ncol=len(names), fontsize=8,
                         frameon=False, handlelength=1.5, columnspacing=1.2)
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


def figure_A1(style_name):
    """The first illness on the ten households, five methods."""
    style = dict(STYLES[style_name])
    apply(style)
    names = ["last-seen", "log and notes", "claim store", "reduced ACE", "tight working memory"]
    cells = "results/self_improve/overnight_wave/cells"
    banks = pathlib.Path("results/self_improve/varied_homes/ten_homes/banks")
    movers = lambda h: sd.the_movers(FrozenHousehold(banks / f"{h}.jsonl"))
    have = [n for n in names if (pathlib.Path(cells) / ARM_DIR[n]).exists()]
    if style["lines"] == 3:
        have = [n for n in have if n in ("last-seen", "log and notes", "reduced ACE")]
    days = list(range(1, 32))
    curves = {}
    for n in have:
        line, band, counts, per = by_day(cells, ARM_DIR[n], D.HOMES_10, days, movers)
        curves[n] = (line, band)
        note(f"  figure A1 [{style_name}] {n:15s} days 10-13 "
             f"{statistics.mean(line[9:13]):5.1f}  day 14 {line[13]:5.1f}  day 24 {line[23]:5.1f}")
    fig, ax = plt.subplots(figsize=(WIDTH_IN, 3.1))
    draw_lines(ax, days, have, curves, style)
    ax.set_ylim(0, 132)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlim(0.5, 31.5)
    ax.set_xticks([1, 5, 10, 14, 20, 24, 31])
    shade_sick(ax, [(14, 23)], style, top=100)
    lo = min(curves[n][0][13] for n in have)
    hi = max(curves[n][0][13] for n in have)
    # A LEADER LINE, because the reader could not tell which dip the number described and read
    # 30-42% off the axis for it.
    # one annotation to the LEFT of its dip and one to the RIGHT of its own, because side by side
    # above the middle they overlapped each other and ran off the canvas
    ax.annotate(f"day 14: all methods\nfall to {lo:.0f}-{hi:.0f}%",
                xy=(14, hi + 2), xytext=(1.2, 130), ha="left", va="top", fontsize=7.2,
                color=INK, fontweight=style["weight"], bbox=BOX,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7,
                                connectionstyle="angle,angleA=0,angleB=90,rad=3"))
    # the second dip, which the reader noticed was nearly as deep and went unmentioned
    d24lo = min(curves[n][0][23] for n in have)
    d24hi = max(curves[n][0][23] for n in have)
    ax.annotate(f"day 24, back to normal:\nthey fall again, to {d24lo:.0f}-{d24hi:.0f}%",
                xy=(24, d24hi + 2), xytext=(31.2, 130), ha="right", va="top", fontsize=7.2,
                color=INK, fontweight=style["weight"], linespacing=1.25, bbox=BOX,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7,
                                connectionstyle="angle,angleA=0,angleB=90,rad=3"))
    ax.set_ylabel("First Room Right (%)", fontweight=style["weight"])
    ax.set_xlabel("Day", fontweight=style["weight"])
    ax.grid(axis="x", visible=False)
    if style["title"]:
        ax.set_title("Adapting Inside the First Illness", fontweight=style["weight"], pad=12)
    handles = [plt.Line2D([], [], color=COLOUR[n], marker=MARKER[n], linestyle=LINESTYLE[n],
                          lw=1.6, ms=4.5,
                          markeredgecolor="white", markeredgewidth=0.5, label=label(n)) for n in have]
    if style["legend"] == "below":
        # THE SAME PLACE AS EVERY OTHER FIGURE IN THIS SET: under the plot, one row, close
        # enough that it costs no white. Three entries fit a 396 pt canvas in one row.
        fig.subplots_adjust(left=0.115, right=0.985, top=0.885, bottom=0.235)
        leg = fig.legend(handles=handles, loc="lower center", ncol=len(have), fontsize=8,
                         frameon=False, handlelength=1.5, columnspacing=1.2)
    else:
        # ABOVE THE AXES: at lower right it covered the lower part of the tight-working-memory
        # line, and five entries in one row is wider than a 396 pt canvas, so three across.
        fig.subplots_adjust(left=0.115, right=0.985, top=0.76, bottom=0.135)
        leg = fig.legend(handles=handles, loc="upper center", ncol=3, fontsize=7.4,
                         frameon=False, handlelength=1.4, columnspacing=1.4,
                         bbox_to_anchor=(0.56, 1.0))
    if style["legend"] != "inside":
        for txt in leg.get_texts():
            txt.set_fontweight("bold")
    out = _place(style_name, "figureA1_first_illness")
    fig.savefig(out)
    plt.close(fig)
    note(f"  wrote {out}")


def figure_A2(style_name):
    """One panel: what the notes written on night 31 make an object's room depend on.

    REBUILT TWICE. First after a reader with no context could not say what it claimed - it was two
    unrelated charts under one caption. Now the second panel, about the hour one note called
    "evening", is gone: it was a detail about one note and not what this figure is for.

    The four conditions get four separate colours, checked with the palette checker for the light
    surface (all six checks pass; the contrast warning is answered by the count printed on every
    segment). The tight-working-memory arm is dropped - it wrote 101 notes to the claim store's
    595, so its bar carried almost nothing.
    """
    style = dict(STYLES[style_name])
    apply(style)
    audit = json.load(open("results/self_improve/paper/night31_audit.json"))
    order = ["claim store", "log and notes", "reduced ACE"]
    # (key in the audit file, what the legend calls it, fill, ink for the count printed on it)
    conds = [("always", "always true", "#4053A3", "white"),
             ("a time of day", "a time of day", "#E69F00", INK),
             ("a person home or away", "a person home or away", "#CC79A7", INK),
             ("other", "other", "#56B4E9", INK)]
    fig, ax = plt.subplots(figsize=(WIDTH_IN, 2.75))
    xs = list(range(len(order)))
    bottoms = [0] * len(order)
    for key, label, colour, ink in conds:
        vals = [audit["by_arm"][m].get(key, 0) for m in order]
        ax.bar(xs, vals, bottom=bottoms, color=colour, width=0.52, lw=0, label=label)
        for x, v, b in zip(xs, vals, bottoms):
            if v >= 12:
                ax.text(x, b + v / 2, str(v), ha="center", va="center", fontsize=7.0, color=ink,
                        fontweight=style["weight"])
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    for x, total in zip(xs, bottoms):
        ax.text(x, total + 4, str(total), ha="center", va="bottom", fontsize=8.0,
                color=INK, fontweight=style["weight"])
    ax.set_xticks(xs)
    ax.set_xlim(-0.62, len(order) - 0.38)
    ax.set_xticklabels(["Claim Store", "Log and Notes", "ACE-Style Playbook"], fontsize=8.0,
                       fontweight=style["weight"])
    ax.set_ylabel("Notes (count)", fontweight=style["weight"])
    # ROOM RATHER THAN BOXES. Boxing the legend and the red note only made their collisions
    # visible; the panel needs headroom so the two can sit side by side above the tallest bar.
    ax.set_ylim(0, max(bottoms) * 1.42)
    ax.grid(axis="x", visible=False)
    # NOT a fourth bar on the method axis: it is a fact about all three, so it is written as one,
    # and ABOVE the axes, where it covers no bar and no total.
    #
    # It used to read "none of these 426 notes mentions the illness". True, and no longer what
    # the figure is FOR: the bars are about the conditions, and the point is that the conditions
    # do not separate ill days from well ones. Measured on these three arms: "always" and "a time
    # of day" are 371 of the 426, and the 12 that name a person home or away all say things like
    # "Dana is at home", which is true on a well day as well. That is 90%, so "most" is safe.
    ax.text(0.5, 1.012, "most conditions hold on ill and well days alike",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=7.6,
            color="#b03020", fontweight="bold")
    leg = ax.legend(loc="upper right", fontsize=7.2, handlelength=1.0, labelspacing=0.26,
                    borderpad=0.45, frameon=True, facecolor="white", framealpha=0.95,
                    edgecolor="#d8d8d4", title="Object Location Conditioned On")
    leg.get_title().set_fontsize(7.2)
    leg.get_title().set_fontweight(style["weight"])
    for txt in leg.get_texts():
        txt.set_fontweight(style["weight"])
    if style["title"]:
        ax.set_title("Notes About Object Rules on Night 31",
                     fontsize=9.5, fontweight=style["weight"], pad=16)
    note(f"  figure A2 [{style_name}] totals " +
         ", ".join(f"{m} {b}" for m, b in zip(order, bottoms)) + f", grand total {sum(bottoms)}")
    fig.subplots_adjust(left=0.105, right=0.985, top=0.835, bottom=0.115)
    out = _place(style_name, "figureA2_what_the_notes_held")
    fig.savefig(out)
    plt.close(fig)
    note(f"  wrote {out}")
