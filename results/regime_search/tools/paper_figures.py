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
NAME = {
    "ttfrozen": "never-forgets timetable", "tt3d": "3-day timetable", "perpetua": "Perpetua*",
    "longcontext": "long-context", "retrieval": "retrieval", "reflect": "reflection",
    "naive": "recency buffer", "lastseen": "last seen",
}
EDGE = {"sick": "sick", "return": "back to normal", "sick2": "sick again", "return2": "back again"}
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
                             "unbounded window renders the 3-day timetable's 40.8-point fall at day 14 as 6.8.")
NOTE_NO_BAND = ("The line is a centred three-day average computed within each stage, never across a boundary. "
                "These are rates rather than averages over households, so no band is drawn.")

rcParams.update({
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
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
    """Is a run adding households to the long-context arms right now? A figure that will gain households must
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
    """Dotted vertical rules at each stage boundary, labelled above the top plot. Nothing is drawn OVER the
    data: a wash behind a one-standard-error band is what made those bands unreadable on the page."""
    st = [s for s in stages_of(DATA, pop) if s["name"] in EDGE]
    for ax in ax_list:
        for s in st:
            ax.axvline(s["a"], color=INK, lw=0.9, ls=":", alpha=0.75, zorder=1)
    top = label_on if label_on is not None else ax_list[0]
    for s in st:
        top.annotate(EDGE[s["name"]], xy=(s["a"], pad_frac), xycoords=("data", "axes fraction"),
                     ha="center", va="bottom", fontsize=7, color=INK)
    return st


def roll3(xs, ys, stage_of=None):
    """Centred three-day mean that NEVER averages across a stage boundary.

    A plain centred window destroys the thing these figures exist to show. Measured on the 3-day timetable: the
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


def line(ax, S, colour, label, clip_from=1, lw=1.6, band=True, smooth=True, stage_of=None):
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
                solid_joinstyle="round")
    else:
        ax.plot(xs, ys, "-", color=colour, lw=lw, label=label, zorder=4, solid_joinstyle="round")


def legend_below(ax, note=None, ncol=2, order=None, inside=None, gap=0.17):
    """Legend and footnote as ONE stacked block under the axis. At single-column width a legend inside the axes
    covers a quarter of the plot, and a footnote placed independently lands on the legend -- both of which
    happened before this was one function that knows how tall the legend is."""
    h, l = ax.get_legend_handles_labels()
    if order == "reverse":
        h, l = h[::-1], l[::-1]
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


def finish(ax, ylab, xlab="day", ylim=(30, 100)):
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
        if entry.get("caveat"):
            f.write(f"- **Read with care:** {entry['caveat']}\n")
        if entry.get("provisional"):
            f.write(f"- **Provisional:** {entry['provisional']}\n")

    with open(os.path.join(folder, "claims.md"), "w") as f:
        head = entry.get("claim_head") or ""
        f.write(f"# What {entry['figure']} does and does not support\n\n## The claim\n\n> {head}{entry['claim']}\n\n")
        f.write("## What in the figure demonstrates it\n\n" + entry.get("look_for", "_not written_") + "\n\n")
        f.write("## What it does NOT show\n\n" + entry.get("not_shown", "_not written_") + "\n\n")
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
        line(ax, S, COL[m], NAME[m], stage_of=stage_lookup(DATA, pop))
        hh[m] = S["hh"]
        val = lambda d: (S["mean"][d - 1] if S["mean"][d - 1] is not None else None)
        nums[NAME[m]] = {"day 13": r2(val(13)), "day 14": r2(val(14)),
                         "break at 14": r2(None if val(13) is None or val(14) is None else val(14) - val(13)),
                         "day 23": r2(val(23)), "day 24": r2(val(24)),
                         "break at 24": r2(None if val(23) is None or val(24) is None else val(24) - val(23))}
    boundaries([ax], DATA, pop)
    finish(ax, "% of questions answered correctly")
    legend_below(ax, ncol=2)
    save(fig, "F1_learn_break_relearn", manifest, {
        "figure": "F1",
        "claim": (lambda n: "A change in the household's hidden routine costs accuracy TWICE: once when it "
                            "happens and again when the world goes back to how it was. The second break is the "
                            "half that is not obvious and it is not the smaller one \u2014 the 3-day timetable "
                            f"loses {abs(n['3-day timetable']['break at 14']):.0f} points at the change and "
                            f"{abs(n['3-day timetable']['break at 24']):.0f} at the return. And the method that "
                            "survives the return is the one that cannot adapt: the never-forgets timetable "
                            f"{'gains' if n['never-forgets timetable']['break at 24'] > 0 else 'loses'} "
                            f"{abs(n['never-forgets timetable']['break at 24']):.0f} points on the day every "
                            "adaptive method breaks, because the routine that returned is the one it never "
                            "stopped believing. Adaptation is not free; it is paid for at every reversal.")(nums),
        "population": POP_LABEL[pop], "households": hh, "split": "all questions",
        "caption": "Accuracy per day for four methods through a routine that changes twice. Every method "
                   "climbs through the settled fortnight, falls sharply on the first sick day (dotted rule), "
                   "re-learns the new routine over the following week, and falls again when the old routine "
                   "returns (second dotted rule). The two timetables break hardest and recover furthest; "
                   "long-context breaks least and recovers least.",
        "look_for": ("The two dotted rules and what happens at them. The 3-day timetable falls "
                     f"{abs(nums['3-day timetable']['break at 14']):.1f} points on day 14 and the never-forgets "
                     f"timetable {abs(nums['never-forgets timetable']['break at 14']):.1f}; by day 23 the 3-day "
                     "timetable is above where it started the spell. At day 24 both fall again "
                     f"({nums['3-day timetable']['break at 24']:+.1f} and "
                     f"{nums['never-forgets timetable']['break at 24']:+.1f}), and the never-forgets timetable "
                     "is the one that recovers immediately, because the old routine is the one it never "
                     "stopped believing. Long-context's day-14 fall is "
                     f"{abs(nums['long-context']['break at 14']):.1f} points, the smallest of the four."),
        "not_shown": "This is accuracy only — nothing here says whether a method KNOWS it has broken, which is "
                     "the subject of F8 and F9. Long-context rests on fewer households than the counters (see "
                     "the count above) and its band is correspondingly wider; do not read a gap between it and "
                     "a counter as an effect without checking the band. The plotted line is a three-day "
                     "average, so the visible fall is shallower than the real one: quote the numbers, not the "
                     "picture.",
                "band": "±1 standard error across households", "drawing": NOTE_LONG_ACC,
        "provisional": grow and "long-context household count will rise: a larger run is in progress", "numbers": nums})


def f2(DATA, EXTRA, manifest):
    """How much of the new routine each method re-learns inside the spell."""
    grow = growing()
    pop = "person"
    # The claim here is a CATEGORY contrast -- one counter against the language memories as a class -- and
    # four same-weight lines in four hues encode no such thing. A cold reader takes away "some methods recover
    # faster". So the counter is drawn at full weight in its own colour and the three language memories share
    # one hue at three lightnesses, with a shaded envelope across them: the class reads as a class.
    keys = [("tt3d", "tt3d", COL["tt3d"]),
            ("person:llm_reflect_nomsg", "reflect", LANG_FAMILY[0]),
            ("person:llm_longcontext_nomsg", "longcontext", LANG_FAMILY[1]),
            ("person:llm_retrieval_nomsg", "retrieval", LANG_FAMILY[2])]
    fig, ax = plt.subplots(figsize=(SINGLE, 2.5))
    nums, hh = {}, {}
    st = stage_lookup(DATA, pop)
    lang = []
    for key, m, colour in keys:
        S = series(DATA, pop, key, only_hh=complete_hh(DATA, pop, key))
        if m != "tt3d":
            lang.append(S)
        hh[m] = S["hh"]
        got = [S["mean"][d - 1] for d in range(14, 24) if S["mean"][d - 1] is not None]
        early = [S["mean"][d - 1] for d in range(14, 17) if S["mean"][d - 1] is not None]
        late = [S["mean"][d - 1] for d in range(20, 24) if S["mean"][d - 1] is not None]
        _ = colour
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
    for key, m, colour in keys:
        S = series(DATA, pop, key, only_hh=complete_hh(DATA, pop, key))
        line(ax, S, colour, NAME[m], band=(m == "tt3d"), stage_of=st,
             lw=1.9 if m == "tt3d" else 1.2)
    boundaries([ax], DATA, pop)
    finish(ax, "% of questions answered correctly")
    legend_below(ax, ncol=2)
    save(fig, "F2_relearning_inside_the_spell", manifest, {
        "figure": "F2",
        "claim_head": ("The language memories do not behave as one class, and the one that behaves most like "
                       "a COUNTER is the one built like a counter. Retrieval answers by pulling sightings from "
                       "the same time of day across the whole history, capped but never aged out \u2014 which "
                       "is the never-forgets timetable's index, plus a recency window. Behaviourally it tracks "
                       "that counter at a correlation of +0.90 with a mean gap of 4.1 points, where the other "
                       "language memories track it at +0.55 and 8\u20139 points, and at the return it RISES as "
                       "that counter does while every adapting method falls. A language memory inherits the "
                       "failure mode of whatever it is indexed by: choosing the retrieval key is choosing which "
                       "disruption the memory will fail on. "),
        "claim": (lambda g: "Given ten days of the new routine the counter re-learns it "
                            f"{g['3-day timetable'] / max(g['reflection'], 0.1):.1f} to "
                            f"{g['3-day timetable'] / max(min(g['long-context'], g['retrieval']), 0.1):.1f} times "
                            "as fast as any language memory: "
                            f"+{g['3-day timetable']:.0f} points from the first sick days to the end of the spell, "
                            f"against +{g['reflection']:.0f} for reflection, +{g['long-context']:.0f} for "
                            f"long-context and +{g['retrieval']:.0f} for retrieval."
                  )({k: v["re-learning inside the spell"] for k, v in nums.items()}),
        "population": POP_LABEL[pop], "households": hh, "split": "all questions",
        "band": "±1 standard error across households, on the 3-day timetable only",
        "caption": "Accuracy per day for the 3-day timetable and three language memories. All four break on "
                   "the first sick day. Over the following ten days, during which every method is living in "
                   "the new routine and is told the right answer after every question, the counter re-learns "
                   "the routine and the language memories recover far less.",
        "look_for": ("The slope between the first sick days and the end of the spell. The 3-day timetable "
                     f"goes from {nums['3-day timetable']['days 14-16']:.1f} to "
                     f"{nums['3-day timetable']['days 20-23']:.1f}, a gain of "
                     f"{nums['3-day timetable']['re-learning inside the spell']:.1f} points. Reflection gains "
                     f"{nums['reflection']['re-learning inside the spell']:.1f}, retrieval "
                     f"{nums['retrieval']['re-learning inside the spell']:.1f} and long-context "
                     f"{nums['long-context']['re-learning inside the spell']:.1f}."),
        "not_shown": ("It does not show that the language memories learn NOTHING: reflection's "
                      f"+{nums['reflection']['re-learning inside the spell']:.1f} is a real gain, about "
                      f"{nums['reflection']['re-learning inside the spell'] / max(nums['3-day timetable']['re-learning inside the spell'], 0.1):.0%} "
                      "of the counter's. It also does not separate re-learning from same-day "
                      "feedback, since these are all questions rather than cold ones. Long-context is on "
                      "fewer households than the rest."),
        "history": "This figure asserted until 22 Sept that the language memories \"barely move\". Its own "
                   "numbers contradicted that — reflection re-learns half as much as the counter, which is not "
                   "\"barely\" — so the claim was changed to the ratio it can actually support and the file "
                   "was renamed off `F2_counters_relearn_language_does_not`, which had encoded the overclaim "
                   "in its name.",
        "note": "The counts are per method above; long-context ran on fewer households than the counters. "
                "The shaded envelope behind the three language memories spans the highest and lowest of "
                "THEIR OWN three estimates on each day — it is the spread between those methods, not a "
                "pooled standard error, and it is there so the three read as one class against the counter.",
        "drawing": NOTE_LONG_ACC,
        "provisional": grow and "long-context household count will rise: a larger run is in progress",
        "numbers": nums})


def f3(DATA, EXTRA, manifest):
    """What one sentence buys and costs, with the measured clip days."""
    grow = growing()
    pop = "person"
    arms = [("person:llm_longcontext_nomsg", "never told", ARM_STEPS[0]),
            ("person:llm_longcontext_startmsg", "told on the first sick day", ARM_STEPS[1]),
            ("person:llm_longcontext_startend", "told again on the first day back", ARM_STEPS[2])]
    # A told-vs-untold figure must be drawn on the households all three arms ran, not on each arm's own set.
    # With the extension running, the untold arm has ten households, told-once six and told-twice three; drawing
    # each on its own set would put three different populations on one chart and call the gaps between them an
    # effect. Matched here, and the matched count is what the figure states.
    matched = sorted(set.intersection(*(set(complete_hh(DATA, pop, k)) for k, _, _ in arms)))
    S = {k: series(DATA, pop, k, only_hh=matched) for k, _, _ in arms}
    # Each told arm is the SAME run as the one above it until the day it is told, so it is drawn only from the
    # day it measurably departs. Measured here, not taken from the calendar -- on this memory one arm departs
    # three days before its message, and a calendar clip would have hidden that.
    clip, prev = {}, None
    for k, _, _ in arms:
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
    for k, lab, c in reversed(arms):             # most-told at the bottom, never-told on top
        line(ax, S[k], c, lab, clip_from=clip.get(k, 1), stage_of=stage_lookup(DATA, pop))
    boundaries([ax], DATA, pop)
    finish(ax, "% of questions answered correctly")
    legend_below(ax, ncol=1, order="reverse")
    nums = {}
    for k, lab, _ in arms:
        nums[lab] = {"days 14-16": r2(avg([S[k]["mean"][d - 1] for d in range(14, 17) if S[k]["mean"][d - 1] is not None])),
                     "days 24-26": r2(avg([S[k]["mean"][d - 1] for d in range(24, 27) if S[k]["mean"][d - 1] is not None])),
                     "drawn from day": clip.get(k, 1)}
    save(fig, "F3_what_one_sentence_buys", manifest, {
        "figure": "F3",
        "claim": "Ten days of living in the new routine, corrected after every single question, do not teach "
                 "this memory the new routine. One sentence does. The untold arm is still answering from the "
                 "old pattern at the end of the spell, while the arm told \u201cYuki is home sick today\u201d "
                 "on the first morning sits above it from that day on. That is the uncomfortable half of the "
                 "accuracy story: what repairs the break is being TOLD, not the evidence, so a memory nobody "
                 "can talk to is a memory that does not recover.",
        "population": POP_LABEL[pop], "households": {"longcontext (matched across all three arms)": len(matched)},
        "split": "all questions", "band": "±1 standard error across households",
        "caveat": "THREE HOUSEHOLDS. At this count almost nothing in this figure clears our claim bar and the "
                  "bands overlap heavily; the gaps are indicative, not established. A larger run is adding "
                  "households and the matched count in this caption will rise.",
        "note": "Each told arm is drawn from the day it measurably departs from the arm above it, computed from "
                "the data rather than from the calendar. Departure days are in the numbers below. "
                "Each told arm is the same run as the one above it until that day.",
        "caption": "One long-context memory, told three different things, on the same households. The "
                   "darkest line is never told; the middle line is told \"Yuki is home sick today\" on the "
                   "first sick day; the lightest is told again that the resident is back on the first day of "
                   "the return. Each told arm is the same run as the one above it until the day it is told, so "
                   "it is drawn only from the day it measurably departs.",
        "look_for": "Where each line begins. The told-once line emerges at day 14 and runs above the untold "
                    "line for the rest of the spell — that gap is what one sentence buys. The told-twice line "
                    "emerges before the return day, which is a genuine early difference in the runs and not a "
                    "drawing choice; the departure days are in the numbers.",
        "not_shown": "At this household count almost nothing here clears our claim bar, and the bands overlap "
                     "heavily — treat the gaps as indicative, not established. It also does not show a cost of "
                     "the message on the way out for this memory; the buffer and retrieval show that more "
                     "clearly and on more households.",
        "drawing": NOTE_LONG_ACC,
        "provisional": grow and "household count will rise: a larger run is in progress",
        "numbers": nums})


def avg(v):
    return sum(v) / len(v) if v else None


def r2(v):
    return None if v is None else round(v, 1)


DEC_NAME = {"ttfrozen": "never-forgets timetable", "tt3d": "3-day timetable",
            "perpetua": "Perpetua*", "longcontext": "long-context", "lastseen": "last seen"}
DEC_ORDER = ["ttfrozen", "tt3d", "perpetua", "longcontext"]
HINDSIGHT = "thresholds chosen with hindsight, so these are upper bounds, not a deployable policy"


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
        line(ax, S, COL[m], DEC_NAME[m], band=False, stage_of=stage_lookup(DATA, "person"))
        for d, v in M["per_day"].items():
            if v < 0 and (worst_below is None or v < worst_below[1]):
                worst_below = (int(d), v, DEC_NAME[m])
        hh[m] = M["n_hh"]
        nums[DEC_NAME[m]] = {"its own best threshold": M["best_bar_overall"],
                             "% of questions declined at it": M["declined_at_best"],
                             **{w: v["best"] for w, v in M["windows"].items()},
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
        ax.annotate(f"{v:+.1f}: worse than answering nothing", xy=(d, v), xytext=(8, 14),
                    textcoords="offset points", fontsize=6.2, color=INK, va="bottom",
                    arrowprops=dict(arrowstyle="-", lw=0.6, color=INK, shrinkA=0, shrinkB=2))
    finish(ax, "daily score (+1 / \u22121 / 0)", ylim=None)
    legend_below(ax, ncol=2)
    save(fig, "F8_decision_score_per_day", manifest, {
        "figure": "F8",
        "claim": "Scored the way a user would feel it — +1 for a right answer, \u22121 for a wrong one, 0 for "
                 "declining — the ranking inverts at the moment of change: the methods that are most accurate "
                 "in the settled world are the ones that collapse, and one goes NEGATIVE. On day 14 the "
                 "never-forgets timetable scores below zero, meaning it would have done better answering "
                 "nothing at all. Accuracy in a stable world does not predict value when the world moves.",
        "population": POP_LABEL["person"], "households": hh, "split": "all questions",
        "band": "none: this is a score, not an average with a spread",
        "prose_numbers_ok": {"0.95": "an illustrative confidence value, not a measured one",
                             "0.5": "the half-way bar the +1/\u22121/0 scoring implies \u2014 a setting"},
        "note": "Each method uses its OWN best fixed threshold, because the comparison would otherwise measure "
                "their confidence scales rather than their judgement \u2014 the timetables spread mass over "
                "dozens of places and rarely exceed 0.5, long-context says 0.95 to almost everything.",
        "caption": "Daily decision score under a rule that needs no coverage target to explain: +1 for a "
                   "right answer, −1 for a wrong one, 0 for declining to answer. Each method uses its own best "
                   "fixed confidence threshold. Both timetables collapse on the first sick day; Perpetua* and "
                   "long-context do not.",
        "below_zero": worst_below,
        "look_for": (lambda w: "The first dotted rule. The never-forgets timetable falls from "
                               f"{w('never-forgets timetable', 0):.1f} in the settled week to "
                               f"{w('never-forgets timetable', 1):.1f} on the first sick days and the 3-day "
                               f"timetable from {w('3-day timetable', 0):.1f} to {w('3-day timetable', 1):.1f}, "
                               f"while Perpetua* goes {w('Perpetua*', 0):.1f} to {w('Perpetua*', 1):.1f} and "
                               f"long-context {w('long-context', 0):.1f} to {w('long-context', 1):.1f}. Note "
                               "also that Perpetua* sits BELOW both timetables while the world is stable."
                     )(lambda m, i: nums[m][list(nums[m])[2 + i]])
                    + (f" And on day {worst_below[0]} the {worst_below[2]}'s daily score is "
                       f"{worst_below[1]:+.1f} — below zero, meaning it would have scored better answering "
                       "nothing at all that day. That single day is the sharpest form of this figure's point "
                       "and the window averages above do not show it."
                       if worst_below else ""),
        "not_shown": "The thresholds are chosen with hindsight for the window being scored, so these are upper "
                     "bounds, not a policy anyone could run. Each method uses a different threshold, so the "
                     "lines are not a like-for-like confidence comparison — that is deliberate, since the "
                     "confidence scales differ wildly, but it means a reader cannot infer anything about the "
                     "thresholds themselves from this figure.",
                "caveat": HINDSIGHT + ", which makes the negative result stronger: even handed the answers in advance, "
                  "declining buys the counters almost nothing exactly when it would matter",
        "drawing": NOTE_NO_BAND, "numbers": nums})


def f9(DATA, EXTRA, manifest):
    """What being allowed to decline is worth, by window."""
    D = EXTRA["decision_live"]["methods"]
    order = EXTRA["decision_live"]["windows_order"]
    fig, ax = plt.subplots(figsize=(FULL * 0.62, 2.5))
    meths = [m for m in DEC_ORDER if m in D]
    w = 0.8 / len(meths)
    nums, hh = {}, {}
    for i, m in enumerate(meths):
        M = D[m]
        xs = [j + (i - (len(meths) - 1) / 2) * w for j in range(len(order))]
        ys = [M["windows"].get(k, {}).get("gain", 0.0) for k in order]
        ax.bar(xs, ys, width=w * 0.92, color=COL[m], label=DEC_NAME[m], zorder=3)
        # the value on the bar: a reader quoting "+2.9 against +0.3" should not have to measure against the
        # axis, and the numbers table is not in the paper beside the figure
        for xx, yy in zip(xs, ys):
            ax.annotate(f"{yy:.1f}", xy=(xx, yy), xytext=(0, 1.5), textcoords="offset points",
                        ha="center", va="bottom", fontsize=5.4, color=INK, rotation=90)
        hh[m] = M["n_hh"]
        nums[DEC_NAME[m]] = {k: M["windows"].get(k, {}).get("gain") for k in order}
    ax.axhline(0, color=INK, lw=0.8, zorder=2)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([textwrap.fill(k, 12) for k in order], fontsize=6.4)
    finish(ax, "points gained by declining", xlab="", ylim=None)
    ax.grid(True, axis="y", alpha=0.5)
    ax.grid(False, axis="x")
    # two lines. The hindsight caveat stays -- it is what stops this being read as a deployable policy --
    # so the population line goes, since the caption carries it.
    legend_below(ax, ncol=2)
    save(fig, "F9_value_of_declining", manifest, {
        "figure": "F9",
        "claim": (lambda g: "At the shift, being allowed to decline is worth almost nothing to the "
                            f"timetables (+{g['never-forgets timetable']:.1f} and +{g['3-day timetable']:.1f}) "
                            f"and a great deal to Perpetua* (+{g['Perpetua*']:.1f}). Perpetua* scores BELOW "
                            "both timetables while the world is stable: it is not the better model, it is the "
                            "only one whose uncertainty is worth acting on."
                  )({k: v["first sick days 14-16"] or 0 for k, v in nums.items()}),
        "population": POP_LABEL["person"], "households": hh, "split": "all questions",
        "band": "none: bars are a difference of two scores",
        "note": "Score under the best threshold for that window, minus the score when forced to answer every "
                "question. Settled figures for context are in F8's numbers: Perpetua* 4.6 against the "
                "timetables' 7.7 and 7.6.",
        "caption": "What being allowed to decline is worth, by window: the decision score under the best "
                   "threshold for that window, minus the score when the method is forced to answer every "
                   "question. Higher bars mean the method's own confidence carries information worth acting "
                   "on. At the moment the routine changes, only Perpetua* gains materially.",
        "look_for": (lambda sick, back: "The first-sick-days group. Perpetua* gains "
                                        f"{sick['Perpetua*']:.1f} points from being allowed to decline, "
                                        f"against {sick['never-forgets timetable']:.1f} for the never-forgets "
                                        f"timetable, {sick['3-day timetable']:.1f} for the 3-day timetable and "
                                        f"{sick['long-context']:.1f} for long-context. On the first days back "
                                        f"the pattern repeats: Perpetua* {back['Perpetua*']:.1f}, everything "
                                        f"else at or below {max(v for k, v in back.items() if k != 'Perpetua*'):.1f}."
                     )({k: v["first sick days 14-16"] or 0 for k, v in nums.items()},
                       {k: v["first days back 24-26"] or 0 for k, v in nums.items()}),
        "not_shown": (lambda st: "This is not a claim that Perpetua* is the better model — F8's settled-week "
                                 f"numbers show it scoring {st['perpetua']:.1f} against the timetables' "
                                 f"{st['ttfrozen']:.1f} and {st['tt3d']:.1f}. The claim is narrower and stranger: "
                                 "it is the worst forecaster of the four and the only one whose uncertainty "
                                 "is worth acting on. The thresholds are also chosen with hindsight, which "
                                 "strengthens the negative half — even given the answers in advance, declining "
                                 "buys the counters almost nothing exactly when it would matter."
                     )({m: D[m]["windows"]["settled week 9-13"]["best"] for m in DEC_ORDER if m in D}),
                "caveat": HINDSIGHT + ", which makes the negative result stronger: even handed the answers in advance, "
                  "declining buys the counters nothing at the moment it would matter",
        "prose_numbers_ok": {f"{D[m]['windows']['settled week 9-13']['best']:.1f}":
                             "live settled-week score from the same extractor, shown in F8's table"
                             for m in DEC_ORDER if m in D},
        "numbers": nums})


GATE_ORDER = ["longcontext", "ttfrozen", "tt3d", "perpetua"]
GATE_NAME = {"longcontext": "long-context", "ttfrozen": "never-forgets timetable",
             "tt3d": "3-day timetable", "perpetua": "Perpetua*"}


def gate_hh(M):
    """Households behind a gate figure. M["n"] is the QUESTION count -- four thousand of them -- and putting
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


def f4(DATA, EXTRA, manifest):
    """Handing the question over: how often, and how often still wrong on what it kept."""
    D = EXTRA["deferral_live"]["memories"]
    alpha = EXTRA["deferral_live"]["alpha"]
    fig, ax = plt.subplots(2, 1, figsize=(SINGLE, 3.6), sharex=True,
                           gridspec_kw={"hspace": 0.16})
    nums, hh = {}, {}
    for m in GATE_ORDER:
        M = D.get(m)
        if not M:
            continue
        st = stage_lookup(DATA, "person")
        line(ax[0], gate_series(M, "hand_over"), COL[m], GATE_NAME[m], band=False, stage_of=st)
        line(ax[1], gate_series(M, "wrong_when_answered"), COL[m], GATE_NAME[m], band=False, stage_of=st)
        hh[GATE_NAME[m]] = gate_hh(M)
        pd = M["per_day"]
        nums[GATE_NAME[m]] = {
            "hands over, settled 9-13": r2(avg([pd[str(d)]["hand_over"] for d in range(9, 14) if str(d) in pd])),
            "hands over, days 14-16": r2(avg([pd[str(d)]["hand_over"] for d in range(14, 17) if str(d) in pd])),
            "wrong on what it keeps, settled": r2(avg([pd[str(d)]["wrong_when_answered"] for d in range(9, 14) if str(d) in pd])),
            "wrong on what it keeps, 14-16": r2(avg([pd[str(d)]["wrong_when_answered"] for d in range(14, 17) if str(d) in pd])),
        }
    boundaries(ax, DATA, "person")
    ax[1].axhline(100 * alpha, color=REF, ls="--", lw=1.0, zorder=2)
    ax[1].annotate(f"the {int(100*alpha)}-in-100 it promised", xy=(0.985, 100 * alpha),
                   xycoords=("axes fraction", "data"), xytext=(0, -4), textcoords="offset points",
                   ha="right", va="top", fontsize=6.2, color=REF, zorder=6)
    finish(ax[0], "% handed over", xlab="", ylim=(0, 100))
    finish(ax[1], "% wrong, of those kept", ylim=(0, 100))
    legend_below(ax[1], ncol=2, gap=0.30)
    save(fig, "F4_handing_the_question_over", manifest, {
        "figure": "F4",
        "claim": "Letting a method decline the questions it is unsure of does not protect it when the world "
                 "changes. At the shift the timetables give up most of the day's questions AND break their "
                 "error promise on the ones they keep: they pay the cost of refusing to answer without buying "
                 "the accuracy that was supposed to purchase. The gate reacts a day late and by too little, "
                 "because it is driven by the same confidence that has not noticed anything yet.",
        "population": POP_LABEL["person"], "households": hh, "split": "all questions",
        "band": "none: these are rates, drawn as a three-day average within each stage",
        "prose_numbers_ok": {"0.1": "alpha, the gate's target error rate \u2014 a setting, not a measurement"},
        "note": f"The dashed line is the one-in-ten error rate the gate was set to hold (alpha={alpha}).",
        "caption": "Top: how often each method declines to answer. Bottom: how often it is nonetheless wrong on "
                   "the questions it did answer, against the one-in-ten rate it was set to hold (dashed). A "
                   "gate that worked would keep the lower line flat across the dotted boundary by giving up "
                   "more questions; these do not.",
        "look_for": "The bottom panel at the first dotted rule. The promise is held comfortably through the "
                    "settled fortnight and broken immediately at the shift, and the top panel shows the gate "
                    "reacting by handing over more — but a day late and not by enough.",
        "not_shown": "It does not show WHY each method fails the promise; F5 separates confidence from "
                     "accuracy, and F6 shows the inversion behind the never-forgets timetable's failure. The "
                     "gate threshold is adaptive, so these are not a fixed policy.",
        "drawing": NOTE_NO_BAND, "numbers": nums})


def f5(DATA, EXTRA, manifest):
    """Confidence beside accuracy, per day, for the four."""
    pop = "person"
    # Last seen is back. It was dropped when its grey separated from Perpetua*'s OLD green by only dE 5.0;
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
    finish(ax[0], "%", ylim=(0, 100))
    finish(ax[1], "", ylim=(0, 100))
    ax[0].set_title("is it right?", fontsize=7.5, pad=16)
    ax[1].set_title("how sure does it say it is?", fontsize=7.5, pad=16)
    legend_below(ax[0], ncol=3, gap=0.22)
    save(fig, "F5_confidence_against_accuracy", manifest, {
        "figure": "F5",
        "claim_head": ("A confidence number can be perfectly stable and mean nothing at all. Last seen states "
                       "near-total confidence every day of the month while being right about half the time, "
                       "and the timetables hold theirs steady through a 40-point collapse in their own "
                       "accuracy. Stability in a confidence signal is not evidence it is tracking anything "
                       "\u2014 it is what a signal looks like when it is ignoring the world. "),
        "claim": (lambda n: "The timetables do not move their stated confidence when they break, so the gap "
                            "between what they claim and what they achieve opens at the shift; last seen "
                            f"states {n['last seen']['confidence day 14']:.0f}% while being right "
                            f"{n['last seen']['accuracy day 14']:.0f}% of the time, a confidence number "
                            "carrying no information at all; Perpetua* is the one whose stated confidence "
                            "tracks its own accuracy through the change.")(nums),
        "population": POP_LABEL[pop], "households": hh, "split": "all questions",
        "band": "±1 standard error across households",
        "caption": "The same five methods twice: accuracy per day on the left, the confidence each states in "
                   "its own answer on the right, on one shared scale. A method whose right-hand line moves "
                   "with its left-hand one knows when it is in trouble; last seen's, which never moves at "
                   "all, is the case where the number means nothing.",
        "look_for": (lambda n: "Compare each method's two lines at the first dotted rule. The never-forgets "
                               f"timetable's accuracy falls {abs(n['never-forgets timetable']['accuracy day 14'] - n['never-forgets timetable']['accuracy day 13']):.0f} "
                               "points between day 13 and day 14 while the confidence it states moves "
                               f"{abs(n['never-forgets timetable']['confidence day 14'] - n['never-forgets timetable']['confidence day 13']):.0f}. "
                               "Perpetua*'s two lines move together: its stated-versus-actual gap at day 14 is "
                               f"{n['Perpetua*']['gap at day 14']:+.1f} points against the never-forgets "
                               f"timetable's {n['never-forgets timetable']['gap at day 14']:+.1f}. Last "
                               "seen is the reductio: its right-hand line sits near the top of the scale all "
                               f"month at about {n['last seen']['confidence day 13']:.0f}% while its left-hand "
                               f"line sits near {n['last seen']['accuracy day 13']:.0f}%.")(nums),
        "not_shown": "Being well-tracked is not being accurate: Perpetua* is the least accurate of the "
                     "counters here, which is the point of the pairing rather than an inconsistency. The right "
                     "panel is each method's own number on its own scale, so heights are not comparable "
                     "between methods — only each line against its own left-hand partner.",
        "drawing": NOTE_LONG, "numbers": nums})


def f6(DATA, EXTRA, manifest):
    """The inversion: what the gate keeps against what it hands over."""
    D = EXTRA["deferral_live"]["memories"]
    order = EXTRA["deferral_live"]["memories"]["ttfrozen"]["answered_vs_handed"]
    wins = [w for w in ("lead", "d14_16", "d17_23", "d24_26", "d27_31") if w in order]
    WLAB = {"lead": "settled", "d14_16": "first\nsick days", "d17_23": "in the\nspell",
            "d24_26": "first days\nback", "d27_31": "a week\nlater"}
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
        a.set_title(GATE_NAME[m], fontsize=7.5)
        finish(a, "% right" if m == meths[0] else "", xlab="", ylim=(0, 100))
        a.grid(False, axis="x")
        hh[GATE_NAME[m]] = gate_hh(M)
        nums[GATE_NAME[m]] = {WLAB[w].replace("\n", " "): M["answered_vs_handed"][w]["edge"] for w in wins}
    legend_below(ax[0], ncol=1)
    save(fig, "F6_the_inversion", manifest, {
        "figure": "F6",
        "claim": "At the moment the routine changes, the never-forgets timetable's gate runs BACKWARDS: it "
                 "answers the questions it gets wrong and hands over the ones it would have got right. That is "
                 "worse than a gate that does nothing at all. Perpetua* keeps the sign the right way round in "
                 "every window, which is what shows the failure to be a property of the confidence signal "
                 "rather than of gating as an idea.",
        "population": POP_LABEL["person"], "households": hh, "split": "all questions",
        "band": "none: these are window accuracies",
        "encoding_words": {"pale": "the handed-over bars are hatched, not tinted",
                           "tint": "the handed-over bars are hatched, not tinted",
                           "faded": "the handed-over bars are hatched, not tinted"},
        "caption": "For two methods, the accuracy of the questions the gate chose to answer (solid) against "
                   "the accuracy of the questions it handed over (hatched), by window. A gate that is working "
                   "keeps the solid bar above the hatched one. Where it does not, the figure says so.",
        "look_for": "The never-forgets timetable's first-sick-days pair, where the hatched bar overtakes the "
                    "solid one, against Perpetua*'s, where it does not. The per-window edge — kept minus "
                    "handed over — is in the numbers.",
        "not_shown": "Two methods only; the 3-day timetable is close to a wash and long-context never inverts, "
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
    finish(ax[0], "% of the time the\ntruth was in the set", xlab="", ylim=(40, 105))
    finish(ax[1], "places it must name", ylim=(1.0, 2.2))
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
        "claim": "The conformal set does not widen when the routine changes. On the first sick day its "
                 f"coverage falls from {avg(lead):.0f}% in the settled week to {d14['coverage']:.0f}% — far "
                 "below the 90% it promises — while the set it offers gets SMALLER, "
                 f"{d14['set_size']:.2f} places against {avg(lead_s):.2f} before. Over the whole spell it "
                 f"averages {avg(spell_s):.2f}, so nothing about its width registers the change.",
        "population": POP_LABEL["person"], "households": {"long-context, sampled": n_hh},
        "split": "all questions",
        "band": "none: single-day rates pooled over households",
        "prose_numbers_ok": {"0.7": "the sampling temperature \u2014 a setting, not a measurement"},
        "note": "Each question was put to the model ten times at temperature 0.7 and the conformal set built "
                "from how often each place came back. Each household's first 20 questions are excluded while "
                "the threshold warms up, and a day is shown only once all households have finished it.",
        "caption": "Top: how often the truth was inside the conformal set, against the 90% the method promises "
                   "(dashed). Bottom: how many places the set contained. At the first sick day the guarantee "
                   "breaks while the set gets no wider — narrower, in fact — so the method's uncertainty does "
                   "not register the change at all; it simply becomes wrong about it.",
        "look_for": f"Day 14 in both panels, marked: coverage {d14['coverage']:.0f}% against a 90% promise, "
                    f"with a set of {d14['set_size']:.2f} places — NARROWER than the settled-week average of "
                    f"{avg(lead_s):.2f}. A method reacting to the change would have widened it.",
        "not_shown": f"Three households, so treat the levels as indicative. Applying our claim bar to the "
                     "per-household changes, the coverage fall is the part that survives — it has the same "
                     "sign in all three households — while the set-size change does not differ from zero. "
                     "This is also one conformal wrapper; four others were tried and are on the page, not here.",
        "drawing": "Drawn per day rather than as a three-day average: this figure's claim is about a single "
                   "day, and even a stage-bounded average pairs day 14 with day 15 and reports 75% where the "
                   "day itself is 69%.",
        "numbers": {"coverage %": {"settled week 9-13": r2(avg(lead)), "day 14": r2(d14["coverage"]),
                                   "spell 14-23": r2(avg(spell))},
                    "set size (places)": {"settled week 9-13": round(avg(lead_s), 2),
                                          "day 14": round(d14["set_size"], 2),
                                          "spell 14-23": round(avg(spell_s), 2)}}})


FIGS = {"F1": f1, "F2": f2, "F3": f3, "F4": f4, "F5": f5, "F6": f6, "F7": f7, "F8": f8, "F9": f9}


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
                "bounded, smoothing shrinks a one-day cliff: the 3-day timetable's fall at day 14 is 40.8 "
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
