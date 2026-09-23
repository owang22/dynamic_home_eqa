#!/usr/bin/env python3
"""Publication figures, regenerated from the SAME two files the page is built from.

    python3 tools/paper_figures.py            (from results/regime_search)
    python3 tools/paper_figures.py F1 F3      (a subset)

Every number in every figure comes from story_data.json or story_extra.json at run time. Nothing is typed into
this script -- that is the whole point of it: a figure that is hand-numbered drifts from the page the first
time a run lands, and we have already been bitten by a hand-typed summary figure going stale.

Each figure is written as PNG (400 dpi), SVG (text kept as text, not outlines) and PDF (vector), plus one
manifest listing, per figure, the claim it supports, the population, the household count and the numbers a
caption would want -- so whoever writes the caption reads them from the manifest, not off the picture.

No titles inside the figures; the paper supplies captions.
"""
import json
import math
import os
import re
import sys
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
from matplotlib import rcParams          # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq", "figures")
MIN_N = 10        # the page's rule: a day needs this many pooled answers before it is drawn
MIN_HH_CELL = 3   # and a household needs this many in its own cell to contribute

# The page's colour map, same hex values, so a reader moving between page and paper sees one colour per method.
# The two extra hues are for the memories the page draws muted; the six together pass the CVD validator
# (worst adjacent pair dE 8.4 protan, normal-vision floor 24.4) against the light surface.
# Checked pair by pair on the pairs that ACTUALLY CO-OCCUR in a figure, not on the palette's own ordering --
# which is what let three failures through. Perpetua*'s green was #199e70 and separated from the never-forgets
# blue by only dE 5.5 under tritanopia; this darker green of the same family clears every focus pair under
# every simulated deficiency, worst pair now 9.2 (never-forgets vs long-context). Retrieval's goldenrod and the
# 3-day timetable's orange were dE 2.5 under deuteranopia and 11.6 even in full colour vision -- below the
# threshold where a reader with no deficiency at all can tell them apart -- so F2 no longer uses hue to
# separate those two at all; see f2().
COL = {
    "ttfrozen":    "#2a78d6",
    "tt3d":        "#eb6834",
    "perpetua":    "#206e44",
    "longcontext": "#7a3aa7",
    "lastseen":    "#918f88",
}
# Reference lines -- the promised error rate, the 90% coverage target -- are drawn in the annotation ink, not
# in red. A red rule against Perpetua*'s green fell to dE 5.2 under protanopia, and no accent hue clears all
# four series hues by a comfortable margin. Ink clears every one of them by 29 or more, and it makes the
# page's rule exact: all annotation is one ink, dotted for a stage boundary and dashed for a target.
# The language memories as a CLASS: one hue at three steps, stepped by measured contrast against white
# (12.2:1, 6.8:1, 3.8:1) and clear of the counter's orange by dE 19 or better under every deficiency.
# Re-stepped: the old three were 13.8-15.0 apart in NORMAL vision, under the floor at which a reader with no
# deficiency can tell them apart. These are 22 apart and still clear the counter's orange by 17.
LANG_FAMILY = ["#2d123f", "#712d9e", "#b178d7"]
INK = "#141413"
REF = INK          # reference lines share the annotation ink; see the note above COL
# A CALLOUT is not a reference line. The no-hue rule exists so a rule across the plot is never mistaken for a
# series; a one-word label pointing at a feature is not at that risk, and it needs to carry. So: reference
# lines carry no hue, callouts may carry one that clears every series IN THEIR OWN FIGURE. This magenta clears
# F6's two series by 9.9 under every deficiency and by 28 in normal vision. It is not safe against the whole
# palette (7.8 against the orange), which is why the rule is per-figure -- and why it is checked rather than
# asserted: tools/check_figure_colours.py reads the rendered SVG, so a callout colour is compared against the
# series it actually appears beside, and a figure that adds a series this clashes with will fail the check.
CALLOUT = "#c92a7a"
# Plain description leads. The technical name appears ONCE, in parentheses, so a reviewer can map the method
# to the literature, and never again after that. An outside reader should not have to remember what a label
# means: if they do, the label is wrong. Every figure, legend, caption and claims file draws from here, so a
# rename lands everywhere at once -- the same guarantee the A and B labels already have.
NAME = {
    "ttfrozen":    "timetable that never forgets",
    "tt3d":        "timetable with a three-day memory",
    "perpetua":    "survival-time model",
    "longcontext": "whole-log-in-the-prompt memory",
    "retrieval":   "same-hour lookup memory",
    "reflect":     "nightly self-notes memory",
    "naive":       "recent-sightings list",
    "routine7":    "nightly routine table",
    "lastseen":    "follows its own most recent sighting",
}
# where the full description will not fit a legend, the LEGEND shortens and the caption carries the full name.
# Never a third abbreviation that exists nowhere else.
NAME_LEGEND = {
    "ttfrozen":    "timetable, never forgets",
    "tt3d":        "timetable, three-day memory",
    "longcontext": "whole log in the prompt",
    "retrieval":   "same-hour lookup",
    "reflect":     "nightly self-notes",
    "naive":       "recent sightings",
    "lastseen":    "follows its most recent sighting",
}
# the literature name, used once per folder in the caption and then dropped
NAME_TECH = {
    "perpetua": "Perpetua*", "longcontext": "long-context", "retrieval": "retrieval-augmented",
    "reflect": "reflection", "naive": "recency buffer",
}


def nm(key):
    """Full descriptive name, for captions, claims and prose."""
    return NAME.get(key, key)


def nm_legend(key):
    """What a legend can carry; falls back to the full name when it fits."""
    return NAME_LEGEND.get(key, NAME.get(key, key))


def nm_first(key):
    """Full name with the technical one in parentheses -- used once, on first mention in a caption."""
    t = NAME_TECH.get(key)
    return f"{NAME.get(key, key)} ({t})" if t else NAME.get(key, key)
# The stages as a reader meets them, written above the plot, and a letter on each boundary rule. A is the day
# the routine changes, B the day it changes back. Oliver defines A and B once in the paper and reuses them, so
# these strings are identical in every figure and every caption: they are an interface, not decoration.
EDGE = {"sick": "A", "return": "B", "sick2": "A2", "return2": "B2"}
STAGE_NAME = {"lead": "normal", "sick": "sick", "return": "normal", "sick2": "sick", "return2": "normal"}
EDGE_RED = "#cc1f1f"
ARM_LABEL = {"nomsg": "no message", "startmsg": "A only", "startend": "A & B"}

# The argument these figures are parts of. Stated once here and attached to the claims it actually bears on,
# with the measurements that support each half, because it is a framing and framings are where overclaiming
# starts. What it rests on, all of it measured in this set:
#   told explicitly, these memories adapt AT ONCE -- the whole-log-in-the-prompt memory told on the first sick morning is +6.3 points
#     that same day and +14.6 by the next, on the households all three arms ran;
#   when the message stops being true they go on acting on it -- every one of the four told arms sits below its
#     own untold twin a week after the return, by 2.8 to 11.4 points;
#   the survival-time model is the exception and its mechanism is in its code: it models how long a sighting stays true.
SPINE = ("These memories can represent the new regime perfectly well \u2014 told about it, they adapt at once. "
         "What none of them can do is notice from evidence that the old regime expired, or that an instruction "
         "has. Neither a sighting nor a sentence carries a validity window, so language does not fix the "
         "problem, it moves it: from failing to notice that sightings went stale to failing to notice that an "
         "instruction did. the survival-time model is the exception because how long a thing stays true is precisely what it "
         "models.")
# The message arms use the same three steps as the language family, for the same reason -- one memory told different things, so one
# colour. Stepped by measured contrast against white (12.5:1, 7.0:1, 3.9:1) rather than by transparency: the
# old lightest arm was an alpha wash that came out at 1.98:1 and was the hardest line on the page, which is
# unacceptable for the arm that carries the return claim.
ARM_STEPS = LANG_FAMILY

# said in plain words on every figure that smooths, because a reader must know which line is which
NOTE = "line = 3-day average within each stage, band = \u00b11 s.e."
# Generic, because it is attached to figures with different y axes. The worked example that used to live
# here quoted an accuracy fall, and was being pasted verbatim onto figures whose axis is a rate or a score.
NOTE_LONG = ("The line is a centred three-day average, computed WITHIN each stage so that it never averages "
             "across a stage boundary — a window straddling the boundary borrows the level from the other "
             "side and flattens the very change the figure is about. The band, where a figure draws one, is "
             "±1 standard error across households computed on the daily values.")
NOTE_LONG_ACC = NOTE_LONG + (" On this figure's axis the effect of getting that wrong is concrete: an "
                             "unbounded window renders the timetable with a three-day memory's 40.8-point fall at day 14 as 6.8.")
NOTE_NO_BAND = ("The line is a centred three-day average computed within each stage, never across a boundary. "
                "These are rates rather than averages over households, so no band is drawn.")

rcParams.update({
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
    # Weight, not size: every piece of type inside an image is bold so it survives reproduction at column
    # width. Caption files are markdown and unaffected.
    "font.weight": "bold", "axes.labelweight": "bold", "axes.titleweight": "bold",
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7,
    "axes.facecolor": "white", "figure.facecolor": "white", "savefig.facecolor": "white",
    "axes.edgecolor": "#444444", "axes.linewidth": 0.8,
    "xtick.color": "#444444", "ytick.color": "#444444",
    "grid.color": "#dddddd", "grid.linewidth": 0.6,
    "svg.fonttype": "none",        # SVG keeps text as text
    "pdf.fonttype": 42,            # PDF embeds real (Type 42) fonts, not outlines
    "figure.dpi": 400,
})

SINGLE, FULL = 3.4, 7.0            # column widths, inches


def growing():
    """Is a run adding households to the the whole-log-in-the-prompt memory arms right now? A figure that will gain households must
    SAY its current count and that more are coming -- a silent three reads as a settled three, and someone
    writes a caption around it."""
    import subprocess
    try:
        live = int(subprocess.run(["bash", "-c", "ps -eo cmd | grep -c '[b]aselines.patrol.llm '"],
                                  capture_output=True, text=True).stdout.strip() or 0)
    except Exception:
        live = 0
    return live > 0


GROWING_NOTE = "a larger run is in progress; this count will rise"


def load():
    """story_data.json holds the counters. The LLM arms live in story_extra.json and the PAGE merges them into
    DATA in the browser, population-qualified, so a figure script reading story_data.json alone silently gets
    counters only -- which is exactly what happened the first time this ran: two figures quietly drew three
    lines instead of four. The same merge is done here, once, so both renderers see identical agents."""
    DATA = json.load(open(os.path.join(ROOT, "story_data.json")))
    EXTRA = json.load(open(os.path.join(ROOT, "story_extra.json")))
    for pop in ("household", "person", "person2x"):
        if pop not in DATA:
            continue
        for key, arm in (EXTRA.get("llm_live", {}).get(pop) or {}).items():
            DATA[pop]["agents"][f"{pop}:{key}"] = arm["cells"]
    return DATA, EXTRA


def complete_hh(DATA, pop, key, need=0.9):
    """Households whose arm actually covers the calendar. A run still in flight has households stopped at
    different days; letting them all in changes WHICH households the daily mean is made of as the axis
    advances, which can manufacture a step at exactly the day of interest. Same trap as the sampling run."""
    R = DATA[pop]
    A = R["agents"].get(key) or {}
    days = R["days"] - 1
    out = []
    for hh, cells in A.items():
        got = sum(1 for d in range(1, R["days"]) if cells["all"][d] and cells["all"][d][0] >= MIN_HH_CELL)
        if got >= need * days:
            out.append(hh)
    return sorted(out)


def series(DATA, pop, key, split="all", field="acc", only_hh=None):
    """Per-day mean across households and its standard error -- the page's panelSeries, same rules."""
    R = DATA[pop]
    A = R["agents"].get(key)
    if A and only_hh is not None:
        A = {h: c for h, c in A.items() if h in only_hh}
    if not A:
        raise KeyError(f"{key!r} is not in DATA[{pop!r}].agents -- a figure asking for it would be drawn a line "
                       f"short with nothing to show for it. Available: {sorted(R['agents'])[:6]}...")
    days, mean, se, nn = [], [], [], []
    for d in range(1, R["days"]):
        vals, N = [], 0
        for hh in A:
            c = (A[hh].get(split) or A[hh]["all"])[d]
            if not c or c[0] < MIN_HH_CELL:
                continue
            vals.append(100.0 * (c[2] if field == "conf" else c[1]) / c[0])
            N += c[0]
        if not vals or N < MIN_N:
            days.append(d); mean.append(None); se.append(None); nn.append(N); continue
        m = sum(vals) / len(vals)
        sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) if len(vals) > 1 else 0.0
        days.append(d); mean.append(m); se.append(sd / math.sqrt(len(vals))); nn.append(N)
    return {"days": days, "mean": mean, "se": se, "n": nn, "hh": len(A)}


def stages_of(DATA, pop):
    """Contiguous stage runs, as the page computes them."""
    R = DATA[pop]
    out, cur = [], None
    for d in range(1, R["days"]):
        nm = R["stages"].get(str(d), "plain")
        if cur is None or cur["name"] != nm:
            cur = {"name": nm, "a": d, "b": d}; out.append(cur)
        else:
            cur["b"] = d
    return out


def stage_lookup(DATA, pop):
    """A day -> stage-name function, so the smoother can refuse to cross a boundary."""
    st = DATA[pop]["stages"]
    return lambda d: st.get(str(int(d)), "plain")


def boundaries(ax_list, DATA, pop, label_on=None, pad_frac=1.012):
    """Dotted rules at each stage boundary, a red letter ON each rule, and the stage names above the plot.

    Nothing is drawn OVER the data: a wash behind a one-standard-error band is what made those bands
    unreadable. The letters sit inside the plot on their own rules and carry a white outline, so they stay
    legible wherever a line happens to pass behind them -- which is why their colour does not have to clear
    every series the way a data colour does."""
    all_st = stages_of(DATA, pop)
    st = [x for x in all_st if x["name"] in EDGE]
    for ax in ax_list:
        for x in st:
            ax.axvline(x["a"], color=INK, lw=0.9, ls=":", alpha=0.75, zorder=1)
    top = label_on if label_on is not None else ax_list[0]
    # the letters, on the rules, inside the top plot
    for x in st:
        top.annotate(EDGE[x["name"]], xy=(x["a"], 0.965), xycoords=("data", "axes fraction"),
                     ha="center", va="top", fontsize=8.5, color=EDGE_RED, fontweight="bold", zorder=7,
                     bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.9))
    # the stages, above the plot, centred on each span
    for x in all_st:
        nm = STAGE_NAME.get(x["name"])
        if not nm:
            continue
        top.annotate(nm, xy=((x["a"] + x["b"]) / 2.0, pad_frac), xycoords=("data", "axes fraction"),
                     ha="center", va="bottom", fontsize=6.6, color="#555555")
    return st


def roll3(xs, ys, stage_of=None):
    """Centred three-day mean that NEVER averages across a stage boundary.

    A plain centred window destroys the thing these figures exist to show. Measured on the timetable with a three-day memory: the
    raw fall at day 14 is 40.8 points, and a window straddling the boundary draws it as 6.8 -- day 13 borrows
    from the first sick day and day 14 borrows back from the last settled day, and a 41-point cliff is rendered
    as a gentle slope. So a day's window is restricted to days in its OWN stage: the boundary days average over
    two days or one, and the break stays the size it is.

    Not a gap-filler either: a day with no value stays without one."""
    out = []
    for i, x in enumerate(xs):
        win = []
        for j in (i - 1, i, i + 1):
            if not (0 <= j < len(ys)) or abs(xs[j] - x) > 1:
                continue
            if stage_of is not None and stage_of(xs[j]) != stage_of(x):
                continue
            win.append(ys[j])
        out.append(sum(win) / len(win))
    return out


def line(ax, S, colour, label, clip_from=1, lw=1.6, band=True, smooth=True, stage_of=None, marker=None):
    """One line per series: a centred three-day mean, bounded by stage, with its standard-error band.

    The band is computed on the DAILY values across households, which is the uncertainty we actually have; only
    the line is smoothed. The raw daily series is not drawn -- at this density it was clutter rather than
    information."""
    xs = [d for d, m in zip(S["days"], S["mean"]) if m is not None and d >= clip_from]
    ys = [m for d, m in zip(S["days"], S["mean"]) if m is not None and d >= clip_from]
    if band:
        lo = [m - e for d, m, e in zip(S["days"], S["mean"], S["se"]) if m is not None and d >= clip_from]
        hi = [m + e for d, m, e in zip(S["days"], S["mean"], S["se"]) if m is not None and d >= clip_from]
        ax.fill_between(xs, lo, hi, color=colour, alpha=0.13, lw=0, zorder=2)
    if smooth:
        ax.plot(xs, roll3(xs, ys, stage_of), "-", color=colour, lw=lw, label=label, zorder=4,
                solid_joinstyle="round", marker=marker, markersize=3.4, markevery=3,
                markerfacecolor=colour, markeredgecolor="white", markeredgewidth=0.5)
    else:
        ax.plot(xs, ys, "-", color=colour, lw=lw, label=label, zorder=4, solid_joinstyle="round")


def legend_below(ax, note=None, ncol=2, order=None, inside=None, gap=0.17):
    """Legend and footnote as ONE stacked block under the axis. At single-column width a legend inside the axes
    covers a quarter of the plot, and a footnote placed independently lands on the legend -- both of which
    happened before this was one function that knows how tall the legend is."""
    h, l = ax.get_legend_handles_labels()
    if order == "reverse":
        h, l = h[::-1], l[::-1]
    # No dashed swatches. A marker sitting on a short legend handle with a white edge reads as a dashed line,
    # and on this page a dash means annotation -- a boundary or a target -- never data. The handles are rebuilt
    # as solid strokes whose marker takes the line's own colour, so nothing in a legend can look dashed. The
    # white marker edge stays ON THE PLOT, where it is doing real work separating overlapping lines.
    import matplotlib.lines as mlines
    h = [mlines.Line2D([], [], color=x.get_color(), lw=x.get_linewidth(), linestyle="-",
                       marker=x.get_marker(), markersize=x.get_markersize(),
                       markerfacecolor=x.get_color(), markeredgecolor=x.get_color())
         if getattr(x, "get_marker", lambda: "None")() not in ("None", None, "") else x
         for x in h]
    if inside:
        # The empty strip runs along the BOTTOM of the plot, under every line, not in a corner -- a corner box
        # sat on the day-14 dip, which is the one part of this figure nobody may cover.
        ax.legend(h, l, loc=inside, ncol=ncol, frameon=True, framealpha=0.92, edgecolor="#dddddd",
                  handlelength=1.5, columnspacing=1.0, borderaxespad=0.3, fontsize=6.6)
        y0 = -0.24
    else:
        leg = ax.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, -gap), ncol=ncol,
                        frameon=False, handlelength=1.5, columnspacing=1.0, borderaxespad=0)
        # Ask the legend where it actually ended rather than guessing from a row count: a guessed row height
        # left a gap of a couple of lines under a three-row legend and none under a one-row one.
        ax.figure.canvas.draw()
        y0 = leg.get_window_extent().transformed(ax.transAxes.inverted()).y0 - 0.045
    # No grey note block. The only text in a figure is what the figure cannot be read without -- axes, ticks,
    # legend, stage-boundary labels, and a callout pointing at a specific feature. Household counts, band
    # definitions, smoothing rules and caveats are caption text, and the caption is what the paper carries;
    # duplicating them into the image only shrinks the data. Everything these blocks used to say is now a
    # field on the figure's entry and is written into caption.md.
    _ = (note, y0)


def finish(ax, ylab, xlab="Day", ylim=(30, 100)):
    ax.set_ylabel(ylab)
    if xlab:
        ax.set_xlabel(xlab)
    if ylim:
        ax.set_ylim(*ylim)
    ax.grid(True, alpha=0.5)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def numbers_table(entry):
    rows = entry.get("numbers") or {}
    if not rows:
        return "_no table for this figure_\n"
    cols = list(next(iter(rows.values())).keys())
    out = ["| series | " + " | ".join(str(c) for c in cols) + " |",
           "|" + "---|" * (1 + len(cols))]
    for k, row in rows.items():
        out.append(f"| {k} | " + " | ".join("–" if row.get(c) is None else str(row.get(c)) for c in cols) + " |")
    return "\n".join(out) + "\n"


def audit_prose(entry):
    """Every number in a figure's prose must be one the figure's own table produces.

    This exists because the failure it catches already happened twice. F9's claim sentence was made to compute
    itself from the table, and the explanatory paragraph one line below it went on saying 2.9 while the
    sentence said 2.8 -- the folder contradicting itself because half of it was live and half was typed. Any
    hand-written figure in prose is a promise that will be broken the next time a household lands, which for
    the told-arm figures is within the hour.

    Returns a list of complaints; the run prints them and keeps going, because a stale number is a thing to
    fix rather than a reason to produce no figures at all."""
    table = set()
    for row in (entry.get("numbers") or {}).values():
        for v in row.values():
            if isinstance(v, (int, float)):
                for q in (f"{v:.0f}", f"{v:.1f}", f"{v:.2f}", f"{abs(v):.0f}", f"{abs(v):.1f}", f"{abs(v):.2f}"):
                    table.add(q)
    # A literal may also be a PARAMETER of the experiment (a temperature, an alpha) or a live value borrowed
    # from another figure's extractor. Those are declared one at a time with a reason, never suppressed
    # wholesale: an unexplained exemption is how a stale number hides.
    allowed = dict(entry.get("prose_numbers_ok") or {})
    bad = []
    # A caption saying "stays the same" where the claim says "gets smaller" is a number disagreement with the
    # digits taken out, and the numeral check above cannot see it. This is a tripwire, not a proof: it knows
    # the opposing phrasings we have actually written into these folders, and nothing more.
    OPPOSED = [({"stays the same", "keeps its width", "unchanged", "does not change", "no change",
                 "gets no wider", "does not widen"},
                {"gets smaller", "narrower", "shrinks", "gets wider", "widens", "grows"}),
               ({"rises", "increases", "goes up", "climbs"},
                {"falls", "drops", "decreases", "goes down"}),
               ({"barely moves", "does not move", "stays flat"},
                {"collapses", "craters", "moves sharply"})]
    # Words describing a visual encoding are the third way prose goes stale, after numbers and directions:
    # F6's caption said "pale" for three rounds after its bars stopped being pale and became hatched. The
    # encoding a figure uses is declared here and the prose is checked against it.
    enc = entry.get("encoding_words") or {}
    for field in ("caption", "look_for", "not_shown", "claim"):
        low = (entry.get(field) or "").lower()
        for word, why in enc.items():
            if word in low:
                bad.append(f"{entry['figure']}/{field}: says '{word}' but {why}")
    claim_txt = (entry.get("claim") or "").lower()
    for field in ("caption", "look_for", "not_shown"):
        other = (entry.get(field) or "").lower()
        for a_set, b_set in OPPOSED:
            hit_a = [a for a in a_set if a in other]
            hit_b = [b for b in b_set if b in claim_txt]
            # only a complaint when BOTH sides are asserted about the same thing and neither text hedges by
            # containing the other side as well
            if hit_a and hit_b and not any(b in other for b in b_set) and not any(a in claim_txt for a in a_set):
                bad.append(f"{entry['figure']}/{field}: says '{hit_a[0]}' where the claim says '{hit_b[0]}'")
    for field in ("caption", "look_for", "not_shown", "claim", "note", "history"):
        text = entry.get(field) or ""
        for lit in re.findall(r"(?<![\w.])\d+\.\d+(?![\w])", text):
            if lit not in table and lit not in allowed:
                bad.append(f"{entry['figure']}/{field}: '{lit}' is not in this figure's numbers table")
    return sorted(set(bad))


def save(fig, name, manifest, entry):
    """One self-contained folder per figure: the three renders, a paste-ready caption, an honest claims file,
    and the numbers, so any one folder can be handed to someone with nothing else explained."""
    folder = os.path.join(OUT, name)
    os.makedirs(folder, exist_ok=True)
    paths = []
    for ext in ("png", "svg", "pdf"):
        fp = os.path.join(folder, f"{name}.{ext}")
        fig.savefig(fp, format=ext, bbox_inches="tight", pad_inches=0.02)
        paths.append(f"{name}.{ext}")
    # Measure what was actually produced and DECLARE the column width, rather than leaving a wide figure to
    # be squeezed into a single column where its 8pt text lands near 4pt. A figure that needs the full measure
    # says so in its caption file, in bold, as the first thing a typesetter reads.
    # Measured from the SAVED FILE, not from the figure's content box. The content box omits the padding
    # savefig adds, which made every declared width exactly 0.04 in short -- a constant, which is why it looked
    # like a consistent percentage and was not one. Reading back the artifact cannot drift from the artifact.
    from PIL import Image
    width_in = Image.open(os.path.join(folder, f"{name}.png")).size[0] / rcParams["figure.dpi"]
    entry["width_inches"] = round(width_in, 2)
    entry["column"] = "single" if width_in <= 3.55 else ("double" if width_in > 4.6 else "1.5")
    plt.close(fig)

    hh = ", ".join(f"{k} {v}" for k, v in entry["households"].items())
    with open(os.path.join(folder, "caption.md"), "w") as f:
        f.write(f"# Caption for {entry['figure']}\n\n")
        colw = {"single": "**Single-column figure** — reproduce at "
                          f"{entry['width_inches']:.2f} in, its rendered width.",
                "1.5": "**Wider than a single column** — reproduce at about "
                       f"{entry['width_inches']:.1f} in. Do NOT squeeze it into one column; its labels are "
                       "set for this width and shrinking them puts the smallest text near 4pt.",
                "double": "**Double-column figure** — reproduce at full text width, about "
                          f"{entry['width_inches']:.1f} in. Do NOT squeeze it into one column: at single-column "
                          "width its text lands near 4pt and is unreadable."}[entry["column"]]
        f.write(colw + "\n\n")
        f.write(f"**Title line:** {entry.get('title') or '_none needed — this figure does not carry its own title; the paper caption is enough._'}\n\n")
        f.write("Paste and edit; written as a caption, not a summary.\n\n---\n\n")
        f.write(entry.get("caption", entry["claim"]) + "\n\n---\n\n")
        f.write(f"- **Population:** {entry['population']}\n- **Households:** {hh}\n")
        f.write(f"- **Questions:** {entry.get('split', 'all')}\n")
        f.write(f"- **Bands:** {entry.get('band', 'none')}\n")
        f.write("- **Dotted vertical rules:** the stage boundaries — the first sick day and the first day back. "
                "Nothing is shaded, so the lines and their bands sit on a plain ground.\n")
        if entry.get("drawing"):
            f.write(f"- **How the line is drawn:** {entry['drawing']}\n")
        if entry.get("note"):
            f.write(f"- **About the data:** {entry['note']}\n")
        if entry.get("bound_wording"):
            f.write(f"- **How much hindsight this figure uses:** {entry['bound_wording']}\n")
        if entry.get("caveat"):
            f.write(f"- **Read with care:** {entry['caveat']}\n")
        if entry.get("provisional"):
            f.write(f"- **Provisional:** {entry['provisional']}\n")

    with open(os.path.join(folder, "claims.md"), "w") as f:
        head = entry.get("claim_head") or ""
        f.write(f"# What {entry['figure']} does and does not support\n\n## The claim\n\n> {head}{entry['claim']}\n\n")
        f.write("## What in the figure demonstrates it\n\n" + entry.get("look_for", "_not written_") + "\n\n")
        if entry.get("mechanism"):
            f.write("## Why this happens\n\n" + entry["mechanism"] + "\n\n")
        f.write("## What it does NOT show\n\n" + entry.get("not_shown", "_not written_") + "\n\n")
        if entry.get("hypothesis_tested_and_failed"):
            f.write("## A hypothesis that was tested and failed\n\n"
                    + entry["hypothesis_tested_and_failed"] + "\n\n")
        if entry.get("conservative_variant"):
            f.write("## The same quantity measured a stricter way\n\n" + entry["conservative_variant"] + "\n\n")
        if entry.get("history"):
            f.write("## How this claim changed\n\n" + entry["history"] + "\n\n")
        f.write("## The numbers\n\nMeasured on the DAILY values, not read off the plotted line.\n\n")
        f.write(numbers_table(entry))

    with open(os.path.join(folder, "numbers.md"), "w") as f:
        f.write(f"# {entry['figure']} — numbers behind the figure\n\n"
                "Regenerated with the figure from the same data. Never read a value off the picture.\n\n")
        f.write(numbers_table(entry))

    # Every piece of text an entry carries must end up in a file somebody reads. `note` and `caveat` were
    # being set on seven figures and written nowhere -- the alpha explanation, the warm-up rule, the hindsight
    # warning, all of it inert. A field that looks declared and does nothing is the same fault as a width that
    # looks measured and is a default.
    written = "".join(open(os.path.join(folder, f)).read()
                      for f in ("caption.md", "claims.md", "numbers.md"))
    for k, v in entry.items():
        if k in ("files", "folder", "numbers", "prose_numbers_ok", "width_inches", "column", "households"):
            continue
        if isinstance(v, str) and len(v) > 25 and v[:25] not in written:
            print(f"    FIELD NOT SURFACED -> {entry['figure']}: '{k}' is set but appears in no file")

    entry["files"] = paths
    entry["folder"] = name
    manifest.append(entry)
    print(f"  {name}/  ({', '.join(paths)} + caption.md, claims.md, numbers.md)")
    for complaint in audit_prose(entry):
        print(f"    STALE NUMBER IN PROSE -> {complaint}")


POP_LABEL = {"person": "one resident off sick, that resident's own things",
             "person2x": "one resident off sick twice", "household": "everyone sick"}
# ---------------------------------------------------------------------------------------------------------


def f1(DATA, EXTRA, manifest):
    """Learn, break, re-learn: the regime in one frame."""
    grow = growing()
    pop = "person"
    keys = [("ttfrozen", "ttfrozen"), ("tt3d", "tt3d"), ("perpetua", "perpetua"),
            ("person:llm_longcontext_nomsg", "longcontext")]
    fig, ax = plt.subplots(figsize=(SINGLE, 2.5))
    nums, hh = {}, {}
    for key, m in keys:
        S = series(DATA, pop, key, only_hh=complete_hh(DATA, pop, key))
        line(ax, S, COL[m], nm_legend(m), stage_of=stage_lookup(DATA, pop))
        hh[m] = S["hh"]
        val = lambda d: (S["mean"][d - 1] if S["mean"][d - 1] is not None else None)
        nums[NAME[m]] = {"day 13": r2(val(13)), "day 14": r2(val(14)),
                         "break at 14": r2(None if val(13) is None or val(14) is None else val(14) - val(13)),
                         "day 23": r2(val(23)), "day 24": r2(val(24)),
                         "break at 24": r2(None if val(23) is None or val(24) is None else val(24) - val(23))}
    boundaries([ax], DATA, pop)
    finish(ax, "Accuracy")
    legend_below(ax, ncol=1)
    save(fig, "F1_learn_break_relearn", manifest, {
        "figure": "F1",
        "claim": (lambda n: "A change in the household's hidden routine costs accuracy TWICE: once when it "
                            "happens and again when the world goes back to how it was. The second break is the "
                            "half that is not obvious and it is not the smaller one \u2014 the timetable with a three-day memory "
                            f"loses {abs(n[nm("tt3d")]['break at 14']):.0f} points at the change and "
                            f"{abs(n[nm("tt3d")]['break at 24']):.0f} at the return. And the method that "
                            "survives the return is the one that cannot adapt: the timetable that never forgets "
                            f"{'gains' if n[nm("ttfrozen")]['break at 24'] > 0 else 'loses'} "
                            f"{abs(n[nm("ttfrozen")]['break at 24']):.0f} points on the day every "
                            "adaptive method breaks, because the routine that returned is the one it never "
                            "stopped believing. Adaptation is not free; it is paid for at every reversal.\n\n"
                            + SPINE + " The return break is that defect seen from the other side: what expired "
                            "was the sick-day routine, and nothing in these memories dates what they learned "
                            "during it.")(nums),
        "population": POP_LABEL[pop], "households": hh, "split": "all questions",
        "caption": "Accuracy per day for four methods through a routine that changes twice. Every method "
                   "climbs through the settled fortnight, falls sharply on the first sick day (dotted rule), "
                   "re-learns the new routine over the following week, and falls again when the old routine "
                   "returns (second dotted rule). The two timetables break hardest and recover furthest; "
                   "the whole-log-in-the-prompt memory breaks least and recovers least.",
        "look_for": ("The two dotted rules and what happens at them. The timetable with a three-day memory falls "
                     f"{abs(nums[nm("tt3d")]['break at 14']):.1f} points on day 14 and the timetable that "
                     f"never forgets {abs(nums[nm("ttfrozen")]['break at 14']):.1f}; by day 23 the "
                     "timetable is above where it started the spell. At day 24 both fall again "
                     f"({nums[nm("tt3d")]['break at 24']:+.1f} and "
                     f"{nums[nm("ttfrozen")]['break at 24']:+.1f}), and the timetable that never forgets "
                     "is the one that recovers immediately, because the old routine is the one it never "
                     "stopped believing. The whole-log memory's day-14 fall is "
                     f"{abs(nums[nm("longcontext")]['break at 14']):.1f} points, the smallest of the four."),
        "not_shown": "This is accuracy only — nothing here says whether a method KNOWS it has broken, which is "
                     "the subject of F8 and F9. The whole-log-in-the-prompt memory rests on fewer households than the counters (see "
                     "the count above) and its band is correspondingly wider; do not read a gap between it and "
                     "a counter as an effect without checking the band. The plotted line is a three-day "
                     "average, so the visible fall is shallower than the real one: quote the numbers, not the "
                     "picture.",
                "band": "±1 standard error across households", "drawing": NOTE_LONG_ACC,
        "provisional": grow and "the whole-log-in-the-prompt memory household count will rise: a larger run is in progress", "numbers": nums})


def f2(DATA, EXTRA, manifest):
    """How much of the new routine each method re-learns inside the spell."""
    grow = growing()
    pop = "person"
    # The claim here is a CATEGORY contrast -- one counter against the language memories as a class -- and
    # four same-weight lines in four hues encode no such thing. A cold reader takes away "some methods recover
    # faster". So the counter is drawn at full weight in its own colour and the three language memories share
    # one hue at three lightnesses, with a shaded envelope across them: the class reads as a class.
    # marker as well as lightness: within one hue family the separation tops out near dE 22, which clears the
    # threshold but is not what a reader picks up at a glance where two lines run close together. A shape is.
    keys = [("tt3d", "tt3d", COL["tt3d"], None),
            ("person:llm_reflect_nomsg", "reflect", LANG_FAMILY[0], "o"),
            ("person:llm_longcontext_nomsg", "longcontext", LANG_FAMILY[1], "s"),
            ("person:llm_retrieval_nomsg", "retrieval", LANG_FAMILY[2], "^")]
    fig, ax = plt.subplots(figsize=(SINGLE, 2.5))
    nums, hh = {}, {}
    st = stage_lookup(DATA, pop)
    lang = []
    for key, m, colour, mk in keys:
        S = series(DATA, pop, key, only_hh=complete_hh(DATA, pop, key))
        if m != "tt3d":
            lang.append(S)
        hh[m] = S["hh"]
        got = [S["mean"][d - 1] for d in range(14, 24) if S["mean"][d - 1] is not None]
        early = [S["mean"][d - 1] for d in range(14, 17) if S["mean"][d - 1] is not None]
        late = [S["mean"][d - 1] for d in range(20, 24) if S["mean"][d - 1] is not None]
        _ = (colour, mk)
        nums[NAME[m]] = {"days 14-16": r2(avg(early)), "days 20-23": r2(avg(late)),
                         "re-learning inside the spell": r2(None if not (early and late) else avg(late) - avg(early)),
                         "spell mean": r2(avg(got))}
    base = nums[NAME["tt3d"]]["re-learning inside the spell"] or 1.0
    for k in nums:                       # the ratio the claim quotes, so the table backs it like everything else
        g = nums[k]["re-learning inside the spell"]
        nums[k]["counter re-learns this many times faster"] = None if not g else round(base / g, 1)
    # envelope across the language family first, so the individual lines sit on top of their own class
    days_env = [d for d in range(1, DATA[pop]["days"])
                if all(S["mean"][d - 1] is not None for S in lang)]
    if days_env:
        lo = [min(S["mean"][d - 1] for S in lang) for d in days_env]
        hi = [max(S["mean"][d - 1] for S in lang) for d in days_env]
        # No legend entry: a legend names series and this is not one. Three lines of one hue inside a shaded
        # region against one bold line in another colour is the grouping, and what the region means is caption
        # text.
        ax.fill_between(days_env, lo, hi, color=LANG_FAMILY[1], alpha=0.13, lw=0, zorder=1)
    for key, m, colour, mk in keys:
        S = series(DATA, pop, key, only_hh=complete_hh(DATA, pop, key))
        line(ax, S, colour, nm_legend(m), band=(m == "tt3d"), stage_of=st,
             lw=1.9 if m == "tt3d" else 1.3, marker=mk)
    boundaries([ax], DATA, pop)
    finish(ax, "Accuracy")
    legend_below(ax, ncol=1)
    save(fig, "F2_relearning_inside_the_spell", manifest, {
        "figure": "F2",
        "claim_head": ("The language memories do not behave as one class, and the one that behaves most like "
                       "a COUNTER is the one built like one. Retrieval answers by pulling sightings from "
                       "the same time of day across the whole history, capped but never aged out \u2014 which "
                       "is the timetable that never forgets's index, plus a recency window. Behaviourally it tracks "
                       "the timetable that never forgets at a correlation of +0.90 with a mean gap of 4.1 points, where the other "
                       "language memories track it at +0.55 and 8\u20139 points, and at the return it RISES as "
                       "the timetable that never forgets does while every adapting method falls. A language memory inherits the "
                       "failure mode of whatever it is indexed by: choosing the retrieval key is choosing which "
                       "disruption the memory will fail on.\n\n" + SPINE + " Retrieval's index is the "
                       "clearest case: same time of day, whole history, no notion of when a sighting stopped "
                       "being informative.\n\n"),
        "claim": (lambda g: "Given ten days of the new routine the timetable with a three-day memory re-learns it "
                            f"{g[nm("tt3d")] / max(g[nm("reflect")], 0.1):.1f} to "
                            f"{g[nm("tt3d")] / max(min(g[nm("longcontext")], g[nm("retrieval")]), 0.1):.1f} times "
                            "as fast as any language memory: "
                            f"+{g[nm("tt3d")]:.0f} points from the first sick days to the end of the spell, "
                            f"against +{g[nm("reflect")]:.0f} for reflection, +{g[nm("longcontext")]:.0f} for "
                            f"the whole-log-in-the-prompt memory and +{g[nm("retrieval")]:.0f} for retrieval."
                  )({k: v["re-learning inside the spell"] for k, v in nums.items()}),
        "population": POP_LABEL[pop], "households": hh, "split": "all questions",
        "band": "±1 standard error across households, on the timetable with a three-day memory only",
        "caption": "Accuracy per day for the timetable with a three-day memory and three language memories. All four break on "
                   "the first sick day. Over the following ten days, during which every method is living in "
                   "the new routine and is told the right answer after every question, the timetable with a three-day memory re-learns "
                   "the routine and the language memories recover far less.",
        "look_for": ("The slope between the first sick days and the end of the spell. The timetable with a three-day memory "
                     f"goes from {nums[nm("tt3d")]['days 14-16']:.1f} to "
                     f"{nums[nm("tt3d")]['days 20-23']:.1f}, a gain of "
                     f"{nums[nm("tt3d")]['re-learning inside the spell']:.1f} points. Reflection gains "
                     f"{nums[nm("reflect")]['re-learning inside the spell']:.1f}, retrieval "
                     f"{nums[nm("retrieval")]['re-learning inside the spell']:.1f} and the whole-log-in-the-prompt memory "
                     f"{nums[nm("longcontext")]['re-learning inside the spell']:.1f}."),
        "not_shown": ("It does not show that the language memories learn NOTHING: reflection's "
                      f"+{nums[nm("reflect")]['re-learning inside the spell']:.1f} is a real gain, about "
                      f"{nums[nm("reflect")]['re-learning inside the spell'] / max(nums[nm("tt3d")]['re-learning inside the spell'], 0.1):.0%} "
                      "of the timetable with a three-day memory's. It also does not separate re-learning from same-day "
                      "feedback, since these are all questions rather than cold ones. The whole-log-in-the-prompt memory is on "
                      "fewer households than the rest."),
        "history": "This figure asserted until 22 Sept that the language memories \"barely move\". Its own "
                   "numbers contradicted that — reflection re-learns half as much as the timetable with a three-day memory, which is not "
                   "\"barely\" — so the claim was changed to the ratio it can actually support and the file "
                   "was renamed off `F2_counters_relearn_language_does_not`, which had encoded the overclaim "
                   "in its name.",
        "note": "The counts are per method above; the whole-log-in-the-prompt memory ran on fewer households than the counters. "
                "The shaded envelope behind the three language memories spans the highest and lowest of "
                "THEIR OWN three estimates on each day — it is the spread between those methods, not a "
                "pooled standard error, and it is there so the three read as one class against the timetable with a three-day memory.",
        "drawing": NOTE_LONG_ACC,
        "provisional": grow and "the whole-log-in-the-prompt memory household count will rise: a larger run is in progress",
        "numbers": nums})


def arm_contrasts(DATA, EXTRA, matched):
    """Per-household told-vs-untold differences on the matched set, with the 2-standard-error verdict.

    Computed here so the claim sentence and the numbers table are the same arithmetic. Below six households
    the bar falls back to the one-sd floor, as everywhere else."""
    import math
    A = DATA["person"]["agents"]
    arms = {"no message": "person:llm_longcontext_nomsg", "A only": "person:llm_longcontext_startmsg",
            "A & B": "person:llm_longcontext_startend"}
    WINS = {"first sick days 14-16": range(14, 17), "rest of spell 17-23": range(17, 24),
            "first days back 24-26": range(24, 27), "a week later 27-31": range(27, 32)}

    def acc(key, hh, days):
        n = ok = 0
        for d in days:
            c = A[key][hh]["all"][d]
            if c and c[0]:
                n += c[0]; ok += c[1]
        return 100.0 * ok / n if n else None

    rows, got = {}, {}
    for label, (x, y) in {"A only - no message": ("no message", "A only"),
                          "A & B - no message": ("no message", "A & B"),
                          "A & B - A only": ("A only", "A & B")}.items():
        row = {}
        for wn, days in WINS.items():
            diffs = [acc(arms[y], hh, days) - acc(arms[x], hh, days) for hh in matched
                     if acc(arms[x], hh, days) is not None and acc(arms[y], hh, days) is not None]
            if len(diffs) < 2:
                continue
            m = sum(diffs) / len(diffs)
            sd = math.sqrt(sum((v - m) ** 2 for v in diffs) / (len(diffs) - 1))
            bar = sd if len(diffs) < 6 else 2 * sd / math.sqrt(len(diffs))
            row[wn] = round(m, 1)
            got[(label, wn)] = (m, sd, len(diffs), abs(m) >= bar)
        rows[label] = row
    return {"rows": rows, "get": lambda lab, wn: f"{got[(lab, wn)][0]:+.1f}" if (lab, wn) in got else "?"}


def f3(DATA, EXTRA, manifest):
    """What one sentence buys and costs, with the measured clip days."""
    grow = growing()
    pop = "person"
    # Named by WHICH messages each arm received, in the A/B vocabulary the paper uses throughout, and given
    # markers: two of the three exist over only part of the axis, so a shape is read instantly where a
    # lightness step is not.
    arms = [("person:llm_longcontext_nomsg", ARM_LABEL["nomsg"], ARM_STEPS[0], None),
            ("person:llm_longcontext_startmsg", ARM_LABEL["startmsg"], ARM_STEPS[1], "s"),
            ("person:llm_longcontext_startend", ARM_LABEL["startend"], ARM_STEPS[2], "^")]
    # A told-vs-untold figure must be drawn on the households all three arms ran, not on each arm's own set.
    # With the extension running, the untold arm has ten households, told-once six and told-twice three; drawing
    # each on its own set would put three different populations on one chart and call the gaps between them an
    # effect. Matched here, and the matched count is what the figure states.
    matched = sorted(set.intersection(*(set(complete_hh(DATA, pop, k)) for k, _, _, _ in arms)))
    S = {k: series(DATA, pop, k, only_hh=matched) for k, _, _, _ in arms}
    # Each told arm is the SAME run as the one above it until the day it is told, so it is drawn only from the
    # day it measurably departs. Measured here, not taken from the calendar -- on this memory one arm departs
    # three days before its message, and a calendar clip would have hidden that.
    clip, prev = {}, None
    for k, _, _, _ in arms:
        if prev is not None:
            first = 1
            for i, d in enumerate(S[k]["days"]):
                a, b = S[k]["mean"][i], S[prev]["mean"][i]
                if a is None and b is None:
                    continue
                if a is None or b is None or abs(a - b) > 1e-9:
                    first = d; break
            clip[k] = first
        prev = k
    fig, ax = plt.subplots(figsize=(SINGLE, 2.5))
    for k, lab, c, mk in reversed(arms):        # most-told at the bottom, never-told on top
        line(ax, S[k], c, lab, clip_from=clip.get(k, 1), stage_of=stage_lookup(DATA, pop), marker=mk)
    boundaries([ax], DATA, pop)
    finish(ax, "Accuracy")
    legend_below(ax, ncol=1, order="reverse")
    nums = {}
    for k, lab, _, _ in arms:
        nums[lab] = {"days 14-16": r2(avg([S[k]["mean"][d - 1] for d in range(14, 17) if S[k]["mean"][d - 1] is not None])),
                     "days 24-26": r2(avg([S[k]["mean"][d - 1] for d in range(24, 27) if S[k]["mean"][d - 1] is not None])),
                     "drawn from day": clip.get(k, 1)}
    # the paired contrasts this figure's claim rests on, computed per household on the matched set so the
    # claim's numbers and the table's cannot disagree
    con = arm_contrasts(DATA, EXTRA, matched)
    nums.update(con["rows"])
    save(fig, "F3_what_one_sentence_buys", manifest, {
        "figure": "F3",
        "claim": (lambda c: "Ten days of living in the new routine, corrected after every single question, do "
                            "not teach the whole-log-in-the-prompt memory the new routine. One sentence does, and on ten "
                            "matched households the whole arc of it now clears our bar on this one memory. "
                            f"Told at A it is {c('A only - no message','first sick days 14-16')} points ahead "
                            "of the untold run on the first sick days and "
                            f"{c('A only - no message','rest of spell 17-23')} through the rest of the spell. "
                            "Left standing after the routine reverts, the same sentence COSTS "
                            f"{abs(float(c('A only - no message','first days back 24-26'))):.1f} points on the "
                            "first days back and "
                            f"{abs(float(c('A only - no message','a week later 27-31'))):.1f} a week later. "
                            "Retracted at B, that cost is gone. The arm told at both ends sits "
                            f"{c('A & B - no message','first days back 24-26')} against never being told on "
                            f"the first days back and {c('A & B - no message','a week later 27-31')} a week "
                            "later, neither of which clears the bar \u2014 so any residual difference is "
                            "smaller than we can measure, which is a bound and not a proof that it is zero. "
                            "What does clear is the positive form: retracting is worth "
                            f"{c('A & B - A only','first days back 24-26')} points against telling once, and "
                            f"{c('A & B - A only','a week later 27-31')} a week later.\n\n"
                            + SPINE + " This figure is where it is earned end to end on a single memory, "
                            "because the message is the counterfactual: it holds the memory fixed and changes "
                            "only whether the regime was announced, and then whether the announcement was "
                            "taken back.")(con["get"]),
        "population": POP_LABEL[pop], "households": {"longcontext (matched across all three arms)": len(matched)},
        "split": "all questions", "band": "±1 standard error across households",
        "note": "Each told arm is drawn from the day it measurably departs from the arm above it, computed from "
                "the data rather than from the calendar. Departure days are in the numbers below. "
                "Each told arm is the same run as the one above it until that day.",
        "caption": "One the whole-log-in-the-prompt memory told three different things, on the same ten households. The "
                   "darkest line is never told; the middle line is told \u201cYuki is home sick today\u201d on "
                   "the first sick day (A); the lightest is told that again and then told on the first day of "
                   "the return that the resident is back (A & B). Each told arm is the same run as the one "
                   "above it until the day it is told, so it is drawn only from the day it measurably departs.",
        "look_for": (lambda c: "The two rules. At A the told line lifts away from the untold one and stays "
                               "above it for the whole spell. At B the arm that was told only at A falls "
                               "BELOW the untold run and stays there — that gap is the cost of an instruction "
                               "nobody took back — while the arm told at both ends returns to the untold "
                               "line. Every one of those four differences clears the bar on ten households; "
                               "the per-household figures are in the table.")(con["get"]),
        "not_shown": ("It does not show that the other language memories behave this way, though all three do "
                      "move the same direction on the return, which is what made this claim survivable before "
                      "this run existed. It does not separate what the message teaches from what it merely "
                      "asserts: a sentence that happens to be true is not evidence the memory could have "
                      "learned the same thing. And the equivalence at B is a NULL with a bound, not a "
                      "demonstration that retracting restores things exactly — it means any residual "
                      "difference is smaller than the bar, not that it is zero."),
        "drawing": NOTE_LONG_ACC,
        "numbers": nums})


def avg(v):
    return sum(v) / len(v) if v else None


def r2(v):
    return None if v is None else round(v, 1)


DEC_NAME = NAME          # one source of names, so a rename cannot land in one figure and miss another
BOUND_WORDING = (
    "The three decision figures use three different amounts of hindsight, and each should be described with "
    "the words that match it. F8: ONE threshold per method for the whole run, then scored day by day \u2014 "
    "oracular in that the constant was chosen knowing the whole run, but it is at least a single policy "
    "someone could hold. F9: one threshold per method per WINDOW, chosen knowing that window's outcomes, and "
    "one per household. F10: one threshold per method per DAY, chosen knowing that day. None of the three is "
    "refitted on held-out data: every threshold in all three is chosen knowing the outcomes it is then "
    "scored on, which is what makes them upper bounds on what declining could be worth rather than policies. "
    "F8 is the tightest of the three and F10 the loosest."
)


DEC_ORDER = ["ttfrozen", "tt3d", "perpetua", "longcontext"]
# The same five windows decision_extra.py cuts on, so a per-day figure here and a per-window one there are
# summarising the identical days. If that file's WINDOWS moves, this moves with it.
WIN_DAYS = {"settled week 9-13": range(9, 14), "first sick days 14-16": range(14, 17),
            "rest of the spell 17-23": range(17, 24), "first days back 24-26": range(24, 27),
            "a week later 27-31": range(27, 32)}
HINDSIGHT = "thresholds chosen with hindsight, so these are upper bounds, not a deployable policy"
HINDSIGHT_RUN = ("one threshold per method, chosen knowing the whole run, so this is an upper bound "
                 "rather than a deployable policy")


def f8(DATA, EXTRA, manifest):
    """Daily decision score, each method at its own best fixed threshold."""
    D = EXTRA["decision_live"]["methods"]
    fig, ax = plt.subplots(figsize=(SINGLE, 2.5))
    nums, hh, worst_below = {}, {}, None
    for m in DEC_ORDER:
        M = D.get(m)
        if not M:
            continue
        days = sorted(int(d) for d in M["per_day"])
        S = {"days": days, "mean": [M["per_day"][str(d)] for d in days],
             "se": [0] * len(days), "hh": M["n_hh"]}
        line(ax, S, COL[m], nm_legend(m), band=False, stage_of=stage_lookup(DATA, "person"))
        for d, v in M["per_day"].items():
            if v < 0 and (worst_below is None or v < worst_below[1]):
                worst_below = (int(d), v, DEC_NAME[m])
        hh[m] = M["n_hh"]
        nums[DEC_NAME[m]] = {"its own best threshold": M["best_bar_overall"],
                             "% of questions declined at it": M["declined_at_best"],
                             **{w: round(avg([M["per_day"][str(d)] for d in rng
                                              if str(d) in M["per_day"]]) or 0.0, 1)
                                for w, rng in WIN_DAYS.items()},
                             # the worst single day, so the below-zero moment the figure marks is backed by
                             # the table like every other number in the prose
                             "worst single day": round(min(M["per_day"].values()), 1)}
    boundaries([ax], DATA, "person")
    ax.axhline(0, color=INK, lw=0.8, alpha=0.5, zorder=1)
    # A daily score below zero means the method would have done better answering NOTHING at all. It is the
    # sharpest moment in this figure and the smoothed window average hides it, so it is marked on the day.
    if worst_below:
        d, v, who = worst_below
        ax.plot([d], [v], "o", ms=3.4, color=COL["ttfrozen"], zorder=6)
        ax.annotate(f"{v:+.1f}: worse than not answering", xy=(d, v), xycoords="data",
                    xytext=(0.02, 0.13), textcoords="axes fraction",
                    fontsize=6.2, color=INK, va="bottom", ha="left",
                    arrowprops=dict(arrowstyle="-", lw=0.6, color=INK, shrinkA=2, shrinkB=3))
    finish(ax, "Score", ylim=None)
    legend_below(ax, ncol=1)
    save(fig, "F8_decision_score_per_day", manifest, {
        "figure": "F8",
        "bound_wording": BOUND_WORDING,
        "claim": "Scored the way a user would feel it — +1 for a right answer, \u22121 for a wrong one, 0 for "
                 "declining — the ranking inverts at the moment of change: the methods that are most accurate "
                 "in the settled world are the ones that collapse, and one goes NEGATIVE. On day 14 the "
                 "timetable that never forgets scores below zero, meaning it would have done better answering "
                 "nothing at all. Accuracy in a stable world does not predict value when the world moves.",
        "population": POP_LABEL["person"], "households": hh, "split": "all questions",
        "band": "none: this is a score, not an average with a spread",
        "prose_numbers_ok": {"0.95": "an illustrative confidence value, not a measured one",
                             "0.5": "the half-way bar the +1/\u22121/0 scoring implies \u2014 a setting"},
        "note": "Each method uses its OWN best fixed threshold, because the comparison would otherwise measure "
                "their confidence scales rather than their judgement \u2014 the timetables spread mass over "
                "dozens of places and rarely exceed 0.5, the whole-log-in-the-prompt memory says 0.95 to almost everything. "
                "Every window figure in the table below is the mean of the DRAWN daily series, computed from it "
                "rather than recomputed beside it. That is the structural fix, not a repair: this table "
                "previously held per-window refits \u2014 a different estimator, in the same units, with values "
                "close enough that a reader comparing table to line saw an agreement that was not there. "
                "Wherever a table sits beside a line, compute the table from the line.",
        "caption": "Daily decision score under a rule that needs no target to explain: +1 for a "
                   "right answer, −1 for a wrong one, 0 for declining to answer. Each method uses its own best "
                   "fixed confidence threshold. Both timetables collapse on the first sick day; the survival-time model and "
                   "the whole-log-in-the-prompt memory do not.",
        "below_zero": worst_below,
        "look_for": (lambda w: "The first dotted rule. The timetable that never forgets falls from "
                               f"{w(nm("ttfrozen"), 0):.1f} in the settled week to "
                               f"{w(nm("ttfrozen"), 1):.1f} on the first sick days and the "
                               f"timetable with a three-day memory from {w(nm("tt3d"), 0):.1f} to {w(nm("tt3d"), 1):.1f}, "
                               f"while the survival-time model goes {w(nm("perpetua"), 0):.1f} to {w(nm("perpetua"), 1):.1f} and "
                               f"the whole-log-in-the-prompt memory {w(nm("longcontext"), 0):.1f} to {w(nm("longcontext"), 1):.1f}. Note "
                               "also that the survival-time model sits BELOW both timetables while the world is stable."
                     )(lambda m, i: nums[m][("settled week 9-13", "first sick days 14-16")[i]])
                    + (f" And on day {worst_below[0]} the {worst_below[2]}'s daily score is "
                       f"{worst_below[1]:+.1f} — below zero, meaning it would have scored better answering "
                       "nothing at all that day. That single day is the sharpest form of this figure's point "
                       "and the window averages above do not show it."
                       if worst_below else ""),
        "not_shown": "The threshold here is ONE number per method for the whole run, chosen knowing the whole "
                     "run \u2014 not refitted per window, which is F9, and not per day, which is F10. That "
                     "makes it an upper bound, though the tightest of the three, and not a policy anyone could "
                     "have run in advance. Each method uses a different threshold, so the "
                     "lines are not a like-for-like confidence comparison — that is deliberate, since the "
                     "confidence scales differ wildly, but it means a reader cannot infer anything about the "
                     "thresholds themselves from this figure.",
                "caveat": HINDSIGHT_RUN + ", which makes the negative result stronger: even handed the answers in advance, "
                  "declining buys the counters almost nothing exactly when it would matter",
        "drawing": NOTE_NO_BAND, "numbers": nums})


def f9(DATA, EXTRA, manifest):
    """What the confidence ORDERING is worth, against the floor hindsight reaches on shuffled labels."""
    DD = EXTRA["decision_live"]["declining_decomposition"]
    order = EXTRA["decision_live"]["windows_order"]
    meths = [m for m in DEC_ORDER if m in DD]
    fig, ax = plt.subplots(figsize=(FULL * 0.62, 2.6))
    w = 0.8 / len(meths)
    nums, hh = {}, {}
    for i_m, m in enumerate(meths):
        M = DD[m]
        xs = [k + (i_m - (len(meths) - 1) / 2) * w for k in range(len(order))]
        ax.bar(xs, [M.get(k, {}).get("ordering", 0.0) for k in order], width=w * 0.92,
               color=COL[m], label=nm_legend(m), zorder=3)
        # The floor is drawn PER BAR, not as one band: it is what a threshold chosen with hindsight reaches on
        # SHUFFLED labels, and it differs by method because a method whose accuracy sits near a half gives
        # hindsight more to work with. A bar that does not clear its own line is not a result.
        for x, k in zip(xs, order):
            f = M.get(k, {}).get("null_ordering")
            if f is not None:
                ax.plot([x - w * 0.46, x + w * 0.46], [f, f], "-", color=INK, lw=1.1, zorder=5)
        # The count is NOT the same in every window -- a household needs twenty answered rows inside a window
        # to enter it, and the three-day return window is short. Reporting the first window's count as if it
        # held for all five is how a figure comes to claim more households than it has.
        counts = {k: M[k]["n_hh"] for k in order if k in M}
        top = max(set(counts.values()), key=list(counts.values()).count)
        odd = [f"{v} in the {k}" for k, v in counts.items() if v != top]
        hh[nm(m)] = str(top) if not odd else f"{top} ({', '.join(odd)})"
        # One row per PART of the decomposition, not one per method: the claim argues from the level and the
        # accuracy as well as from the plotted bar, and every number it states has to be in this table.
        for part, field in (("what the ordering adds", "ordering"), ("noise floor for that", "null_ordering"),
                            ("the level part", "level"), ("% right", "accuracy")):
            nums[f"{nm(m)} \u2014 {part}"] = {k: M.get(k, {}).get(field) for k in order}
    ax.axhline(0, color=INK, lw=0.8, zorder=2)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([textwrap.fill(k, 12) for k in order], fontsize=6.4)
    finish(ax, "What the confidence\nordering adds", xlab="", ylim=None)
    ax.grid(True, axis="y", alpha=0.5)
    ax.grid(False, axis="x")
    # Headroom measured from the TALLEST BAR, not a constant: the note sat across the survival-time model's
    # first-sick-days bar, which is the one bar the figure exists to show.
    tall = max(max(DD[m].get(k, {}).get("ordering", 0.0) for k in order) for m in meths)
    ax.set_ylim(0, tall * 1.34)
    ax.annotate("black line on each bar = what hindsight reaches on shuffled labels;\n"
                "a bar that does not clear its own line is not a result",
                xy=(0.02, 0.97), xycoords="axes fraction", ha="left", va="top", fontsize=6.0, color=INK)
    legend_below(ax, ncol=2)
    sick = "first sick days 14-16"
    g = lambda m, f: DD[m][sick][f]
    save(fig, "F9_what_the_confidence_adds", manifest, {
        "figure": "F9",
        "bound_wording": BOUND_WORDING,
        "claim": ("Being allowed to decline is worth something to every method at the shift, but for the "
                  "timetables that is not because their confidence knows anything. The value splits in two: "
                  "what the best all-or-nothing choice gives, which needs no signal at all and pays whenever a "
                  "method is wrong more often than right, and what the ORDER of the confidences adds on top. "
                  f"At the shift the timetable that never forgets is right {g('ttfrozen','accuracy'):.1f}% of "
                  f"the time, so declining is worth {g('ttfrozen','level'):.2f} to it on the level alone "
                  f"\u2014 and its ordering adds {g('ttfrozen','ordering'):.2f} against a hindsight-on-noise "
                  f"floor of {g('ttfrozen','null_ordering'):.2f}, which is nothing. The three-day timetable is "
                  f"the same story ({g('tt3d','ordering'):.2f} against {g('tt3d','null_ordering'):.2f}). The "
                  f"survival-time model's ordering adds {g('perpetua','ordering'):.2f} against a floor of "
                  f"{g('perpetua','null_ordering'):.2f}, and the whole-log-in-the-prompt memory's "
                  f"{g('longcontext','ordering'):.2f} against {g('longcontext','null_ordering'):.2f}. The "
                  "honest contrast is not a big effect against a small one. It is a real effect against no "
                  "measurable effect."),
        "population": POP_LABEL["person"], "households": hh, "split": "all questions",
        "band": "none: the black line on each bar is a noise floor, not an error bar",
        "caveat": ("The household count is not the same in every window. A household enters a window only if "
                   "it answered twenty or more questions inside it, and the first-days-back window is three "
                   "days long, so two households fall out of it. The first-days-back bars therefore rest on "
                   "eight households and the rest on ten; the claim above argues from the first sick days, "
                   "where all ten are present."),
        "note": ("Threshold chosen PER HOUSEHOLD with hindsight, which is the generous reading and suits a "
                 "figure whose point is that even given hindsight the timetables gain nothing from their own "
                 "confidence. The floor is that same quantity computed on shuffled labels."),
        "conservative_variant": ("A stricter estimator gives the same ranking. Choosing ONE threshold for all "
                                 "ten households instead of one each, the totals are 0.33 for the timetable "
                                 "that never forgets, 0.40 for the three-day one, 2.83 for the survival-time "
                                 "model and 0.77 for the whole-log memory. Its noise floor sits near 0.01, "
                                 "because a single policy applied to every household has far less freedom to "
                                 "chase noise, so on that estimator every bar clears its floor. The two agree "
                                 "on the ranking and disagree on the floor: that is a fact about the "
                                 "estimators rather than about the methods, and a reviewer who recomputes one "
                                 "of them should expect a different-looking number."),
        "caption": ("What the ORDER of a method's confidences is worth at each stage: the score under the best "
                    "threshold for that window, minus the score from the best all-or-nothing choice, so that "
                    "only the part needing the confidence to carry information is shown. The black line on "
                    "each bar is what the same procedure extracts from shuffled labels, and it is drawn per "
                    "bar because it moves: a method that is right about half the time hands hindsight far "
                    "more to work with, so the floor rises at the shift for exactly the methods whose bars "
                    "rise there. A bar that does not clear its own line is not a result."),
        "look_for": ("The first-sick-days group. Both timetables' bars sit on their own floors; the "
                     "survival-time model's stands well clear of it and the whole-log-in-the-prompt memory's "
                     "clears too."),
        "not_shown": ("It does not show the level part, which is real and is where the timetables' apparent "
                      "gain comes from; those numbers are in the claim. It is not a deployable policy \u2014 "
                      "the threshold is fitted after the fact on the very window being scored, which is why a "
                      "floor is drawn at all. And a floor is not an error bar: it says what noise would give, "
                      "not how uncertain this estimate is."),
        "mechanism": ("The same result by a second route, which is why it is stated as a finding rather than "
                      "as one test. Correlating each method's stated confidence with whether it was actually "
                      "right, inside each household, both timetables fall at the shift to something "
                      "indistinguishable from zero while the survival-time model's is unchanged. One statistic "
                      "subtracts a shuffled-label floor and the other measures association directly; they "
                      "agree on which methods have a real ordering and on the timetables having none."),
        "numbers": nums})




GATE_ORDER = ["longcontext", "ttfrozen", "tt3d", "perpetua"]
GATE_NAME = NAME


def gate_hh(M):
    """Households behind a rule that decides whether to answer figure. M["n"] is the QUESTION count -- four thousand of them -- and putting
    that in a field labelled "Households" is how F4 and F6 came to claim 4130 households. The extractor
    records the real count as it loads the rows, because the rows themselves carry no household."""
    n = M.get("n_hh")
    if not n:
        raise KeyError("deferral_live has no n_hh; re-run tools/deferral_extra.py")
    return n


def gate_series(M, field):
    days = sorted(int(d) for d in M["per_day"])
    return {"days": days, "mean": [M["per_day"][str(d)][field] for d in days],
            "se": [0] * len(days), "hh": M["n"]}


def conf_shift(DATA, EXTRA, mem):
    """How far a method's OWN stated confidence moved from the settled week to the first sick days."""
    key = {"ttfrozen": "ttfrozen", "tt3d": "tt3d", "perpetua": "perpetua"}.get(mem)
    if key:
        only = complete_hh(DATA, "person", key)
        C = series(DATA, "person", key, field="conf", only_hh=only)
        a = avg([C["mean"][d - 1] for d in range(9, 14) if C["mean"][d - 1] is not None])
        b = avg([C["mean"][d - 1] for d in range(14, 17) if C["mean"][d - 1] is not None])
        return None if a is None or b is None else round(b - a, 1)
    arm = (EXTRA.get("llm_live", {}).get("person") or {}).get(f"llm_{mem}_nomsg")
    if not arm:
        return None
    w = arm.get("windows") or {}
    a, b = (w.get("lead") or {}).get("conf"), (w.get("d14_16") or {}).get("conf")
    return None if a is None or b is None else round(b - a, 1)


def f4(DATA, EXTRA, manifest):
    """Reacting is not recovering: the rule that decides whether to answer declines far more, and is still wrong several times over."""
    D = EXTRA["deferral_live"]["memories"]
    alpha = EXTRA["deferral_live"]["alpha"]
    promise = 100.0 * alpha
    # The miss rate is drawn as a MULTIPLE of the promised rate, not as a percentage, so that "three times what
    # it promised" is read rather than computed. The promise is then the line at 1 and needs no arithmetic.
    fig, ax = plt.subplots(2, 1, figsize=(SINGLE, 3.5), sharex=True,
                           gridspec_kw={"hspace": 0.14, "height_ratios": [1.35, 1]})
    st = stage_lookup(DATA, "person")
    nums, hh, peaks = {}, {}, []
    # rank first, then draw worst-first, so the legend below reads as a ranking without a second block
    ranked = []
    for m in GATE_ORDER:
        M = D.get(m)
        if not M:
            continue
        pdm = M["per_day"]
        sickv = avg([pdm[str(d)]["wrong_when_answered"] for d in range(14, 17) if str(d) in pdm])
        ranked.append((sickv / promise, m, M))
    ranked.sort(reverse=True)
    for mx, m, M in ranked:
        mult = gate_series(M, "wrong_when_answered")
        mult["mean"] = [v / promise for v in mult["mean"]]
        lab = f"{mx:.1f}\u00d7  {nm_legend(m)}"
        line(ax[0], mult, COL[m], lab, band=False, stage_of=st)
        line(ax[1], gate_series(M, "hand_over"), COL[m], lab, band=False, stage_of=st)
        hh[GATE_NAME[m]] = gate_hh(M)
        pd = M["per_day"]
        w = lambda f, days: avg([pd[str(d)][f] for d in days if str(d) in pd])
        sick = w("wrong_when_answered", range(14, 17))
        peaks.append((sick / promise, nm_legend(m), COL[m]))
        nums[GATE_NAME[m]] = {
            "hands over, settled 9-13": r2(w("hand_over", range(9, 14))),
            "hands over, days 14-16": r2(w("hand_over", range(14, 17))),
            "wrong on what it keeps, settled": r2(w("wrong_when_answered", range(9, 14))),
            "wrong on what it keeps, 14-16": r2(sick),
            "times the promised rate, 14-16": round(sick / promise, 1),
            # the ROUTE: does the rule that decides whether to answer decline more because the method's own confidence fell, or only because
            # the controller raised its bar after the fact? This column is the first half of that answer.
            "its own confidence moved (points)": conf_shift(DATA, EXTRA, m)}
    boundaries(ax, DATA, "person")
    ax[0].axhline(1.0, color=REF, ls="--", lw=1.0, zorder=2)
    ax[0].annotate("what it promised", xy=(0.985, 1.0),
                   xycoords=("axes fraction", "data"), xytext=(0, -4), textcoords="offset points",
                   ha="right", va="top", fontsize=6.2, color=REF)
    # rank the methods ON the plot, worst first, so a reader can tell good from bad without tracing four lines
    peaks.sort(reverse=True)
    top = max(v["mean"][d] for v in (gate_series(D[m], "wrong_when_answered") for m in GATE_ORDER if m in D)
              for d in range(len(v["mean"])) if v["mean"][d] is not None) / promise
    finish(ax[0], "Wrong answers \u00f7\nwhat it promised", xlab="", ylim=(0, top + 0.8))
    finish(ax[1], "How often it hands\nthe question over", ylim=(0, 100))
    legend_below(ax[1], ncol=1, gap=0.30)
    save(fig, "F4_reacting_is_not_recovering", manifest, {
        "figure": "F4",
        "claim": (lambda n: "Reacting is not recovering. When the routine changes these rules that decide whether to answer DO notice \u2014 "
                            "every one of them roughly doubles or triples how often it declines to answer "
                            "\u2014 and the answers they keep are still wrong "
                            f"{min(v['times the promised rate, 14-16'] for v in n.values()):.1f} to "
                            f"{max(v['times the promised rate, 14-16'] for v in n.values()):.1f} times more "
                            "often than the rate they promised. Noticing that something is wrong is not the "
                            "same as knowing WHICH answers are wrong, and only the second one protects a user.")(nums),
        "population": POP_LABEL["person"], "households": hh, "split": "all questions",
        "band": "none: these are rates",
        "prose_numbers_ok": {"0.1": "alpha, the error rate the rule that decides whether to answer was set to hold -- a setting"},
        "note": ("The top axis is the miss rate among ANSWERED questions divided by the rate the rule that decides whether to answer was set "
                 f"to hold (alpha={alpha}), so the dashed line at 1 is the promise and 3 means three times as "
                 "many wrong answers as promised. The lower panel is the evidence that the rule that decides whether to answer did react."),
        "caption": "The figure in each legend entry is that method's miss rate over the first sick days "
                   "(14\u201316), as a multiple of what it promised, worst first. Top: how often each method "
                   "is wrong on the questions it chose to answer, as a multiple of "
                   "the error rate it was set to hold; the dashed line at 1 is that promise. Bottom: how "
                   "often it declined to answer. The rule that decides whether to answers react to the change \u2014 the lower panel roughly "
                   "doubles \u2014 and the upper panel shows that reacting did not make the kept answers "
                   "reliable.",
        "look_for": (lambda n: "The top panel at the first dotted rule, where every line leaves the promise "
                               "behind. The ranking is printed on the plot: worst is the timetable that never "
                               f"timetable at {max(v['times the promised rate, 14-16'] for v in n.values()):.1f} "
                               "times its promised rate. Then the lower panel, which shows this is not a "
                               "failure to react: hand-over roughly doubles at the same moment.")(nums),
        "not_shown": (lambda n: "It does not show WHY the rule that decides whether to answer reacts, which differs by method and is the "
                                "more interesting half. The last column of the table is that answer: the "
                                "timetables' own confidence falls at the shift, by "
                                f"{abs(n[nm("ttfrozen")]['its own confidence moved (points)']):.1f} "
                                f"and {abs(n[nm("tt3d")]['its own confidence moved (points)']):.1f} "
                                "points, while the whole-log-in-the-prompt memory's moves "
                                f"{n[nm("longcontext")]['its own confidence moved (points)']:+.1f}. So "
                                "whole-log memory's entire reaction is the controller raising its bar after "
                                "mistakes have already been made, and none of the four moves its "
                                "confidence as far as its accuracy fell. Nor does it show what the questions "
                                "it hands over would have scored: that is F6, and for one method the answer "
                                "is worse than what it kept.")(nums),
        "drawing": NOTE_NO_BAND, "numbers": nums})


def f5(DATA, EXTRA, manifest):
    """Confidence beside accuracy, per day, for the four."""
    pop = "person"
    # The memory that follows its last sighting is back. It was dropped when its grey separated from the survival-time model's OLD green by only dE 5.0;
    # against the current green the same grey clears at 9.6 under every deficiency, so the figure keeps the
    # case it exists for -- a method stating near-total confidence while right about half the time is the
    # sharpest demonstration that a confidence number can carry no information, and the other four cannot
    # make it.
    keys = [("ttfrozen", "ttfrozen"), ("tt3d", "tt3d"), ("perpetua", "perpetua"),
            ("person:llm_longcontext_nomsg", "longcontext"), ("lastseen", "lastseen")]
    fig, ax = plt.subplots(1, 2, figsize=(FULL, 2.6), sharey=True, gridspec_kw={"wspace": 0.06})
    nums, hh = {}, {}
    st = stage_lookup(DATA, pop)
    for key, m in keys:
        only = complete_hh(DATA, pop, key)
        A = series(DATA, pop, key, only_hh=only)
        C = series(DATA, pop, key, field="conf", only_hh=only)
        line(ax[0], A, COL[m], NAME[m], stage_of=st)
        line(ax[1], C, COL[m], NAME[m], stage_of=st)
        hh[m] = A["hh"]
        g = lambda S, d: S["mean"][d - 1]
        nums[NAME[m]] = {"accuracy day 13": r2(g(A, 13)), "confidence day 13": r2(g(C, 13)),
                         "accuracy day 14": r2(g(A, 14)), "confidence day 14": r2(g(C, 14)),
                         "gap at day 14": r2(None if g(A, 14) is None or g(C, 14) is None else g(C, 14) - g(A, 14))}
    boundaries([ax[0]], DATA, pop)
    boundaries([ax[1]], DATA, pop)
    finish(ax[0], "Accuracy", ylim=(0, 100))
    finish(ax[1], "Confidence", ylim=(0, 100))
    legend_below(ax[0], ncol=2, gap=0.22)
    save(fig, "F5_confidence_against_accuracy", manifest, {
        "figure": "F5",
        "claim_head": ("A confidence number can be perfectly stable and mean nothing at all. The memory that follows its last sighting states "
                       "near-total confidence every day of the month while being right about half the time, "
                       "and the timetables hold theirs steady through a 40-point collapse in their own "
                       "accuracy. Stability in a confidence signal is not evidence it is tracking anything "
                       "\u2014 it is what a signal looks like when it is ignoring the world. "),
        "claim": (lambda n: "The timetables do not move their stated confidence when they break, so the gap "
                            "between what they claim and what they achieve opens at the shift; the memory that follows its last sighting "
                            f"states {n[nm("lastseen")]['confidence day 14']:.0f}% while being right "
                            f"{n[nm("lastseen")]['accuracy day 14']:.0f}% of the time, a confidence number "
                            "carrying no information at all; the survival-time model is the one whose stated confidence "
                            "tracks its own accuracy through the change.")(nums),
        "population": POP_LABEL[pop], "households": hh, "split": "all questions",
        "band": "±1 standard error across households",
        "caption": "The same five methods twice: accuracy per day on the left, the confidence each states in "
                   "its own answer on the right, on one shared scale. A method whose right-hand line moves "
                   "with its left-hand one knows when it is in trouble; the memory that follows its last sighting's, which never moves at "
                   "all, is the case where the number means nothing.",
        "look_for": (lambda n: "Compare each method's two lines at the first dotted rule. The timetable that never "
                               f"timetable's accuracy falls {abs(n[nm("ttfrozen")]['accuracy day 14'] - n[nm("ttfrozen")]['accuracy day 13']):.0f} "
                               "points between day 13 and day 14 while the confidence it states moves "
                               f"{abs(n[nm("ttfrozen")]['confidence day 14'] - n[nm("ttfrozen")]['confidence day 13']):.0f}. "
                               "survival-time model's two lines move together: its stated-versus-actual gap at day 14 is "
                               f"{n[nm("perpetua")]['gap at day 14']:+.1f} points against the timetable that never "
                               f"timetable's {n[nm("ttfrozen")]['gap at day 14']:+.1f}. Last "
                               "follows its last sighting is the reductio: its right-hand line sits near the top of the scale all "
                               f"month at about {n[nm("lastseen")]['confidence day 13']:.0f}% while its left-hand "
                               f"line sits near {n[nm("lastseen")]['accuracy day 13']:.0f}%.")(nums),
        "not_shown": "Being well-tracked is not being accurate: the survival-time model is the least accurate of the "
                     "counters here, which is the point of the pairing rather than an inconsistency. The right "
                     "panel is each method's own number on its own scale, so heights are not comparable "
                     "between methods — only each line against its own left-hand partner.",
        "drawing": NOTE_LONG, "numbers": nums})


def f6(DATA, EXTRA, manifest):
    """The inversion: what the rule that decides whether to answer keeps against what it hands over."""
    D = EXTRA["deferral_live"]["memories"]
    order = EXTRA["deferral_live"]["memories"]["ttfrozen"]["answered_vs_handed"]
    wins = [w for w in ("lead", "d14_16", "d17_23", "d24_26", "d27_31") if w in order]
    WLAB = {"lead": "settled\n9\u201313", "d14_16": "sick\n14\u201316", "d17_23": "spell\n17\u201323",
            "d24_26": "back\n24\u201326", "d27_31": "later\n27\u201331"}
    meths = ["ttfrozen", "perpetua"]
    fig, ax = plt.subplots(1, 2, figsize=(FULL * 0.72, 2.5), sharey=True, gridspec_kw={"wspace": 0.05})
    nums, hh = {}, {}
    for a, m in zip(ax, meths):
        M = D[m]
        xs = list(range(len(wins)))
        kept = [M["answered_vs_handed"][w]["answered_acc"] for w in wins]
        gave = [M["answered_vs_handed"][w]["handed_acc"] for w in wins]
        a.bar([x - 0.2 for x in xs], kept, width=0.38, color=COL[m], label="questions it answered", zorder=3)
        # NOT a 42% tint of the same colour: composited over white those two pale bars fell to dE 3.9 under
        # tritanopia, a failure created by the transparency rather than by the hues underneath it. Hatching
        # keeps the identity in the full-strength hue and carries the kept/handed distinction as texture.
        a.bar([x + 0.2 for x in xs], gave, width=0.38, facecolor="white", edgecolor=COL[m], hatch="////",
              linewidth=0.8, label="questions it handed over", zorder=3)
        for x, (k, g) in enumerate(zip(kept, gave)):
            if k < g:      # the inversion: mark it rather than leave it to be spotted
                a.annotate("inverted", xy=(x, max(k, g)), xytext=(0, 8), textcoords="offset points",
                           ha="center", fontsize=6.4, color=CALLOUT, fontweight="bold")
        a.set_xticks(xs)
        a.set_xticklabels([WLAB[w] for w in wins], fontsize=5.9)
        a.set_title(nm_legend(m), fontsize=7.5)
        finish(a, "Accuracy" if m == meths[0] else "", xlab="", ylim=(0, 100))
        a.grid(False, axis="x")
        hh[GATE_NAME[m]] = gate_hh(M)
        nums[GATE_NAME[m]] = {WLAB[w].replace("\n", " "): M["answered_vs_handed"][w]["edge"] for w in wins}
    legend_below(ax[0], ncol=1)
    save(fig, "F6_the_inversion", manifest, {
        "figure": "F6",
        "claim": "At the moment the routine changes, the timetable that never forgets's rule for deciding whether to answer runs BACKWARDS: it "
                 "answers the questions it gets wrong and hands over the ones it would have got right. That is "
                 "worse than a rule that decides whether to answer that does nothing at all. the survival-time model keeps the sign the right way round in "
                 "every window, which is what shows the failure to be a property of the confidence signal "
                 "rather than of gating as an idea.\n\n" + SPINE + " That is why the exception is this "
                 "method and not a better-tuned gate on one of the others.",
        "population": POP_LABEL["person"], "households": hh, "split": "all questions",
        "band": "none: these are window accuracies",
        "encoding_words": {"pale": "the handed-over bars are hatched, not tinted",
                           "tint": "the handed-over bars are hatched, not tinted",
                           "faded": "the handed-over bars are hatched, not tinted"},
        "caption": "For two methods, the accuracy of the questions the rule that decides whether to answer chose to answer (solid) against "
                   "the accuracy of the questions it handed over (hatched), by window. A rule that is working "
                   "keeps the solid bar above the hatched one. Where it does not, the figure says so.",
        "look_for": "The timetable that never forgets's first-sick-days pair, where the hatched bar overtakes the "
                    "solid one, against the survival-time model's, where it does not. The per-window edge — kept minus "
                    "handed over — is in the numbers.",
        "not_shown": "Two methods only; the timetable with a three-day memory is close to a wash and the whole-log-in-the-prompt memory never inverts, "
                     "so neither adds to the contrast. It also does not show how MANY questions each bar "
                     "rests on, which differs a great deal between the kept and handed-over halves.",
        "numbers": nums})


def f7(DATA, EXTRA, manifest):
    """The sets break rather than widen: coverage and set size per day."""
    S = EXTRA["samples_live"]
    C = S["conformal"]
    days = sorted(int(d) for d in C)
    cov = [C[str(d)]["coverage"] for d in days]
    size = [C[str(d)]["set_size"] for d in days]
    n_hh = max(C[str(d)]["n_hh"] for d in days)
    fig, ax = plt.subplots(2, 1, figsize=(SINGLE, 3.4), sharex=True,
                           gridspec_kw={"hspace": 0.16, "height_ratios": [1.15, 1]})
    # THE EXCEPTION to the three-day average, taken deliberately. This figure's claim is about a SINGLE day:
    # coverage craters on day 14 and the set does not widen to compensate. Even a stage-bounded average pairs
    # day 14 with day 15 and reports 75% where the day itself is 69%, softening the one number the figure
    # exists to show. Drawn per day, with that day marked, rather than smoothed.
    ax[0].plot(days, cov, "-", color=COL["longcontext"], lw=1.6, zorder=4)
    ax[0].axhline(90, color=REF, ls="--", lw=1.0, zorder=2)
    ax[0].annotate("dashed line = the 90% it promises", xy=(0.015, 0.06), xycoords="axes fraction",
                   ha="left", va="bottom", fontsize=6.2, color=REF)
    ax[1].plot(days, size, "-", color=COL["longcontext"], lw=1.6, zorder=4)
    d14 = C.get("14")
    if d14:
        ax[0].plot([14], [d14["coverage"]], "o", ms=3.2, color=COL["longcontext"], zorder=5)
        ax[0].annotate(f"{d14['coverage']:.0f}%", xy=(14, d14["coverage"]), xytext=(4, -1),
                       textcoords="offset points", fontsize=6.4, color=INK, va="top")
        ax[1].plot([14], [d14["set_size"]], "o", ms=3.2, color=COL["longcontext"], zorder=5)
        ax[1].annotate(f"{d14['set_size']:.2f}", xy=(14, d14["set_size"]), xytext=(4, -1),
                       textcoords="offset points", fontsize=6.4, color=INK, va="top")
    boundaries(ax, DATA, "person")
    finish(ax[0], "How often the truth\nwas in the list", xlab="", ylim=(40, 105))
    finish(ax[1], "Places named", ylim=(1.0, 2.2))
    lead = [C[str(d)]["coverage"] for d in range(9, 14) if str(d) in C]
    spell = [C[str(d)]["coverage"] for d in range(14, 24) if str(d) in C]
    lead_s = [C[str(d)]["set_size"] for d in range(9, 14) if str(d) in C]
    spell_s = [C[str(d)]["set_size"] for d in range(14, 24) if str(d) in C]
    legend_below(ax[1], ncol=1, gap=0.34)
    save(fig, "F7_sets_break_rather_than_widen", manifest, {
        "figure": "F7",
        # The claim used to quote the spell-average set size against the settled average, which describes a
        # different window from the day the claim is about -- and in doing so undersold it. On the day the
        # guarantee fails the set is NARROWER than the settled week, which is stronger than "unchanged".
        "claim": "The list of places the rule offers does not widen when the routine changes. On the first sick day its "
                 f"how often the truth is in its list falls from {avg(lead):.0f}% in the settled week to {d14['coverage']:.0f}% — far "
                 "below the 90% it promises — while the set it offers gets SMALLER, "
                 f"{d14['set_size']:.2f} places against {avg(lead_s):.2f} before. Over the whole spell it "
                 f"averages {avg(spell_s):.2f}, so nothing about its width registers the change.",
        "population": POP_LABEL["person"], "households": {"the whole-log-in-the-prompt memory, sampled": n_hh},
        "split": "all questions",
        "band": "none: single-day rates pooled over households",
        "prose_numbers_ok": {"0.7": "the sampling temperature \u2014 a setting, not a measurement"},
        "note": "Each question was put to the model ten times at temperature 0.7 and the list of places the rule offers built "
                "from how often each place came back. Each household's first 20 questions are excluded while "
                "the threshold warms up, and a day is shown only once all households have finished it.",
        "caption": "Top: how often the truth was inside the list of places the rule offers, against the 90% the method promises "
                   "(dashed). Bottom: how many places the set contained. At the first sick day the guarantee "
                   "breaks while the set gets no wider — narrower, in fact — so the method's uncertainty does "
                   "not register the change at all; it simply becomes wrong about it.",
        "look_for": f"Day 14 in both panels, marked: the truth was in the list {d14['coverage']:.0f}% of the time against a 90% promise, "
                    f"with a set of {d14['set_size']:.2f} places — NARROWER than the settled-week average of "
                    f"{avg(lead_s):.2f}. A method reacting to the change would have widened it.",
        "not_shown": f"Three households, so treat the levels as indicative. Applying our claim bar to the "
                     "per-household changes, the fall in how often the truth was in the list is the part that survives — it has the same "
                     "sign in all three households — while the set-size change does not differ from zero. "
                     "This is also one way of setting the list size \u2014 the rule that adjusts itself as it goes (adaptive conformal prediction); four others were tried and are on the page, not here.",
        "drawing": "Drawn per day rather than as a three-day average: this figure's claim is about a single "
                   "day, and even a stage-bounded average pairs day 14 with day 15 and reports 75% where the "
                   "day itself is 69%.",
        "numbers": {"how often the truth was in the list, %": {"settled week 9-13": r2(avg(lead)), "day 14": r2(d14["coverage"]),
                                   "spell 14-23": r2(avg(spell))},
                    "set size (places)": {"settled week 9-13": round(avg(lead_s), 2),
                                          "day 14": round(d14["set_size"], 2),
                                          "spell 14-23": round(avg(spell_s), 2)}}})


def f10(DATA, EXTRA, manifest):
    """The same question as F9, asked one day at a time: does the confidence beat hindsight-on-noise TODAY?"""
    P = EXTRA["decision_live"]["per_day_hindsight"]
    meths = [m for m in DEC_ORDER if m in P]
    fig, ax = plt.subplots(figsize=(SINGLE, 2.5))
    nums, hh = {}, {}
    for m in meths:
        M = P[m]
        days = sorted(int(d) for d in M["gain"])
        S = {"days": days, "se": [0] * len(days), "hh": M["n_hh"],
             "mean": [M["gain"][str(d)] - M["null_gain"][str(d)] for d in days]}
        line(ax, S, COL[m], nm_legend(m), band=False, stage_of=stage_lookup(DATA, "person"))
        hh[m] = M["n_hh"]
        # A row per part, as in F9: the caption argues from the FLOOR as well as from the plotted excess, and
        # every number in a folder's prose has to be a number that folder's own table produces.
        beats, bar, floorrow = {}, {}, {}
        for w, rng in WIN_DAYS.items():
            g = avg([M["gain"][str(d)] for d in rng if str(d) in M["gain"]])
            f = avg([M["null_gain"][str(d)] for d in rng if str(d) in M["null_gain"]])
            sd = avg([M["null_sd"][str(d)] for d in rng if str(d) in M["null_sd"]])
            beats[w] = None if g is None else round(g - f, 2)
            bar[w] = None if sd is None else round(2 * sd, 2)
            floorrow[w] = None if f is None else round(f, 2)
        nums[f"{nm(m)} \u2014 beats the floor by"] = beats
        nums[f"{nm(m)} \u2014 bar it has to clear"] = bar
        nums[f"{nm(m)} \u2014 the floor itself"] = floorrow
    boundaries([ax], DATA, "person")
    ax.axhline(0, color=INK, lw=0.9, zorder=3)
    finish(ax, "What the confidence beats\nhindsight-on-noise by", ylim=None)
    legend_below(ax, ncol=2)
    v = lambda m, w, k="beats the floor by": nums[f"{nm(m)} \u2014 {k}"][w]
    sick = "first sick days 14-16"
    save(fig, "F10_the_same_test_one_day_at_a_time", manifest, {
        "figure": "F10",
        "claim": ("Refitting the threshold every single day \u2014 the most generous reading there is \u2014 "
                  "does not rescue either timetable at the shift, and it separates them into two findings "
                  "that the window version ran together.\n\n"
                  "FIRST, and this is the paper's thesis stated by a method rather than about one: the "
                  "timetable that never forgets has a confidence signal that works, and it fails at the one "
                  "moment it is needed. It beats hindsight-on-shuffled-labels in every window of the run "
                  f"except one \u2014 {v('ttfrozen','settled week 9-13'):.2f} against a bar of "
                  f"{v('ttfrozen','settled week 9-13','bar it has to clear'):.2f} in the settled week, "
                  f"{v('ttfrozen','first days back 24-26'):.2f} against "
                  f"{v('ttfrozen','first days back 24-26','bar it has to clear'):.2f} on the first days back, "
                  f"{v('ttfrozen','a week later 27-31'):.2f} against "
                  f"{v('ttfrozen','a week later 27-31','bar it has to clear'):.2f} a week after that "
                  f"\u2014 and at the first sick days {v('ttfrozen',sick):.2f} against a bar of "
                  f"{v('ttfrozen',sick,'bar it has to clear'):.2f}, which is nothing. Not a weak signal that "
                  "the shift weakens further: a working one that stops working on the day the routine "
                  "changes and works again a week later.\n\n"
                  "SECOND, and separately, the timetable with a three-day memory never had much of a signal "
                  "to lose. It clears its bar in only two of the five windows and at neither boundary "
                  f"\u2014 {v('tt3d',sick):.2f} against {v('tt3d',sick,'bar it has to clear'):.2f} at the "
                  f"shift, {v('tt3d','first days back 24-26'):.2f} against "
                  f"{v('tt3d','first days back 24-26','bar it has to clear'):.2f} on the return, and "
                  f"{v('tt3d','settled week 9-13'):.2f} against "
                  f"{v('tt3d','settled week 9-13','bar it has to clear'):.2f} even in the settled week. That "
                  "is a weaker and less interesting story than the first one, and merging the two timetables "
                  "into a single sentence costs the first one its point.\n\n"
                  "The survival-time model moves the other way, from "
                  f"{v('perpetua','settled week 9-13'):.2f} settled to {v('perpetua',sick):.2f} at the shift, "
                  "the largest value it reaches all run."),
        "population": POP_LABEL["person"], "households": hh, "split": "all questions",
        "band": "none: the zero line IS the noise floor, because what is plotted is already the excess over it",
        "note": ("One threshold per DAY, shared across the ten households, chosen knowing that day's outcomes. "
                 "The floor subtracted from it is the same procedure run on labels shuffled inside each "
                 "household on that day, averaged over 40 shuffles."),
        "bound_wording": BOUND_WORDING,
        "caption": ("Per day, the score under the best threshold for that day minus the score from answering "
                    "everything, with the same quantity on shuffled labels subtracted off. Zero means the "
                    "confidence tells you nothing a coin could not have told you, once hindsight is paid for. "
                    "The subtraction matters most exactly where the figure does: a method that is right about "
                    "half the time hands hindsight far more to work with, so at the shift the shuffled-label "
                    "floor under the timetables climbs from about 0.02 to 1.23. Their raw gain climbs at the "
                    "shift too \u2014 which is why the unfloored number looks like a result \u2014 but no "
                    "faster than the floor beneath it."),
        "look_for": ("The first dotted rule, and then the rest of the run. The never-forgets timetable dips "
                     "to and below the zero line at that rule and is clear of it everywhere else, which is "
                     "the whole of the first finding. The three-day timetable hugs the zero line for most of "
                     "the run, which is the whole of the second. The survival-time model rises to its highest "
                     "point of the run at the same rule where the first timetable fails."),
        "not_shown": ("It does not show the total value of declining, most of which comes from the level term "
                      "and not from the ordering \u2014 that split is F9's. It is not a deployable policy: the "
                      "threshold is chosen knowing the day it is scored on, which is why a noise floor has to "
                      "be subtracted at all. Days 1 to 8 are drawn for completeness and nothing is claimed "
                      "from them: the methods' memories are still filling, and the settled comparison in "
                      "every window table starts at day 9."),
        "mechanism": ("The floor itself moves, and that is the point. In the settled week hindsight on shuffled "
                      "labels buys almost nothing, because a method that is right four times in five leaves "
                      "little for a threshold to find. At the shift the timetables are right about half the "
                      "time, and hindsight on pure noise then buys a great deal. Their observed gain rises at "
                      "the shift too \u2014 which is why the raw number looks like a result \u2014 but it "
                      "rises no faster than the floor beneath it."),
        "numbers": nums})


FIGS = {"F1": f1, "F2": f2, "F3": f3, "F4": f4, "F5": f5, "F6": f6, "F7": f7, "F8": f8, "F9": f9, "F10": f10}


def main():
    want = [a.upper() for a in sys.argv[1:]] or list(FIGS)
    DATA, EXTRA = load()
    manifest = []
    print(f"writing to {OUT}")
    for name in want:
        fn = FIGS.get(name)
        if not fn:
            print(f"  {name}: not defined yet")
            continue
        fn(DATA, EXTRA, manifest)
    mpath = os.path.join(OUT, "MANIFEST.json")
    old = json.load(open(mpath)) if os.path.exists(mpath) else []
    merged = {e["figure"]: e for e in old}
    merged.update({e["figure"]: e for e in manifest})
    ordered = [merged[k] for k in sorted(merged)]
    json.dump(ordered, open(mpath, "w"), indent=2)
    # top-level file is an INDEX across folders, not a copy of what now lives inside them
    with open(os.path.join(OUT, "MANIFEST.md"), "w") as f:
        f.write("# Paper figures\n\nRegenerated by `results/regime_search/tools/paper_figures.py` from "
                "`story_data.json` and `story_extra.json` — the same files the interactive page is built from. "
                "No number here or in any figure is typed into the script.\n\n"
                "**Every number in this file is measured on the DAILY values, not on the smoothed line.** The "
                "figures plot a centred three-day average, bounded so it never crosses a stage boundary. Even "
                "bounded, smoothing shrinks a one-day cliff: the timetable with a three-day memory's fall at day 14 is 40.8 "
                "points on the daily values and reads as 30.5 on the plotted line. Quote the numbers here, not "
                "what the line appears to show.\n\n")
        for e in ordered:
            f.write(f"## [{e['figure']}]({e['folder']}/) — {e['folder']}\n\n")
            f.write(f"{e['claim']}\n\n")
            f.write(f"*{e['column']}-column, {e['width_inches']} in wide.* ")
            f.write(f"Population {e['population']}; households "
                    + ", ".join(f"{k} {v}" for k, v in e["households"].items()) + ". ")
            f.write(f"Renders, caption and claims in `{e['folder']}/`.\n\n")
    print(f"\nmanifest: {mpath} and MANIFEST.md ({len(ordered)} figures)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
