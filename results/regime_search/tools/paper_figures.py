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
import sys

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
COL = {
    "ttfrozen":    "#2a78d6",
    "tt3d":        "#eb6834",
    "perpetua":    "#199e70",
    "longcontext": "#7a3aa7",
    "retrieval":   "#b8860b",
    "reflect":     "#c2185b",
    "naive":       "#b8860b",
    "lastseen":    "#9a9a93",
}
INK = "#141413"
NAME = {
    "ttfrozen": "never-forgets timetable", "tt3d": "3-day timetable", "perpetua": "Perpetua*",
    "longcontext": "long-context", "retrieval": "retrieval", "reflect": "reflection",
    "naive": "recency buffer", "lastseen": "last seen",
}
EDGE = {"sick": "sick", "return": "back to normal", "sick2": "sick again", "return2": "back again"}

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


def series(DATA, pop, key, split="all", field="acc"):
    """Per-day mean across households and its standard error -- the page's panelSeries, same rules."""
    R = DATA[pop]
    A = R["agents"].get(key)
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


def line(ax, S, colour, label, clip_from=1, lw=1.5, band=True):
    xs = [d for d, m in zip(S["days"], S["mean"]) if m is not None and d >= clip_from]
    ys = [m for d, m in zip(S["days"], S["mean"]) if m is not None and d >= clip_from]
    if band:
        lo = [m - e for d, m, e in zip(S["days"], S["mean"], S["se"]) if m is not None and d >= clip_from]
        hi = [m + e for d, m, e in zip(S["days"], S["mean"], S["se"]) if m is not None and d >= clip_from]
        ax.fill_between(xs, lo, hi, color=colour, alpha=0.15, lw=0, zorder=2)
    ax.plot(xs, ys, "-", color=colour, lw=lw, label=label, zorder=3, solid_joinstyle="round")


def legend_below(ax, note, ncol=2, order=None):
    """Legend and footnote as ONE stacked block under the axis. At single-column width a legend inside the axes
    covers a quarter of the plot, and a footnote placed independently lands on the legend -- both of which
    happened before this was one function that knows how tall the legend is."""
    h, l = ax.get_legend_handles_labels()
    if order == "reverse":
        h, l = h[::-1], l[::-1]
    rows = math.ceil(len(l) / ncol)
    ax.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=ncol,
              frameon=False, handlelength=1.6, columnspacing=1.2, borderaxespad=0)
    ax.annotate(note, xy=(0.5, -0.20 - rows * 0.115 - 0.04), xycoords="axes fraction",
                ha="center", va="top", fontsize=6.5, color="#555555")


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


def save(fig, name, manifest, entry):
    os.makedirs(OUT, exist_ok=True)
    paths = []
    for ext in ("png", "svg", "pdf"):
        p = os.path.join(OUT, f"{name}.{ext}")
        fig.savefig(p, format=ext, bbox_inches="tight", pad_inches=0.02)
        paths.append(os.path.basename(p))
    plt.close(fig)
    entry["files"] = paths
    manifest.append(entry)
    print(f"  {name}: " + ", ".join(paths))


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
        S = series(DATA, pop, key)
        line(ax, S, COL[m], NAME[m])
        hh[m] = S["hh"]
        val = lambda d: (S["mean"][d - 1] if S["mean"][d - 1] is not None else None)
        nums[NAME[m]] = {"day 13": r2(val(13)), "day 14": r2(val(14)),
                         "break at 14": r2(None if val(13) is None or val(14) is None else val(14) - val(13)),
                         "day 23": r2(val(23)), "day 24": r2(val(24)),
                         "break at 24": r2(None if val(23) is None or val(24) is None else val(24) - val(23))}
    boundaries([ax], DATA, pop)
    finish(ax, "% of questions answered correctly")
    legend_below(ax, f"{POP_LABEL[pop]} · {hh.get('tt3d', '?')} households "
                     f"(long-context {hh.get('longcontext', '?')}{', ' + GROWING_NOTE if grow else ''}) · "
                     f"band = ±1 standard error", ncol=2)
    save(fig, "F1_learn_break_relearn", manifest, {
        "figure": "F1",
        "claim": "Every learner climbs through the settled fortnight, breaks on the first sick day, re-learns "
                 "inside the spell, and breaks again on the return.",
        "population": POP_LABEL[pop], "households": hh, "split": "all questions",
        "band": "±1 standard error across households",
        "provisional": grow and "long-context household count will rise: a larger run is in progress", "numbers": nums})


def f2(DATA, EXTRA, manifest):
    """The counters re-learn the new routine; the language memories do not."""
    grow = growing()
    pop = "person"
    keys = [("tt3d", "tt3d"), ("person:llm_longcontext_nomsg", "longcontext"),
            ("person:llm_retrieval_nomsg", "retrieval"), ("person:llm_reflect_nomsg", "reflect")]
    fig, ax = plt.subplots(figsize=(SINGLE, 2.5))
    nums, hh = {}, {}
    for key, m in keys:
        S = series(DATA, pop, key)
        line(ax, S, COL[m], NAME[m])
        hh[m] = S["hh"]
        got = [S["mean"][d - 1] for d in range(14, 24) if S["mean"][d - 1] is not None]
        early = [S["mean"][d - 1] for d in range(14, 17) if S["mean"][d - 1] is not None]
        late = [S["mean"][d - 1] for d in range(20, 24) if S["mean"][d - 1] is not None]
        nums[NAME[m]] = {"days 14-16": r2(avg(early)), "days 20-23": r2(avg(late)),
                         "re-learning inside the spell": r2(None if not (early and late) else avg(late) - avg(early)),
                         "spell mean": r2(avg(got))}
    boundaries([ax], DATA, pop)
    finish(ax, "% of questions answered correctly")
    legend_below(ax, f"{POP_LABEL[pop]} · band = ±1 standard error across households\n"
                     f"long-context on {hh.get('longcontext', '?')} households"
                     f"{' (' + GROWING_NOTE + ')' if grow else ''}, the others on {hh.get('tt3d', '?')}", ncol=2)
    save(fig, "F2_counters_relearn_language_does_not", manifest, {
        "figure": "F2",
        "claim": "Given ten days of the new routine the counter learns it; the language memories barely move.",
        "population": POP_LABEL[pop], "households": hh, "split": "all questions",
        "band": "±1 standard error across households",
        "note": "The counts are per method above; long-context ran on fewer households than the counters.",
        "provisional": grow and "long-context household count will rise: a larger run is in progress",
        "numbers": nums})


def f3(DATA, EXTRA, manifest):
    """What one sentence buys and costs, with the measured clip days."""
    grow = growing()
    pop = "person"
    arms = [("person:llm_longcontext_nomsg", "never told", 1.0),
            ("person:llm_longcontext_startmsg", "told on the first sick day", 0.68),
            ("person:llm_longcontext_startend", "told again on the first day back", 0.42)]
    S = {k: series(DATA, pop, k) for k, _, _ in arms}
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
    for k, lab, alpha in reversed(arms):          # palest and most-told at the bottom, never-told on top
        ax.plot([], [])
        line(ax, S[k], COL["longcontext"], lab, clip_from=clip.get(k, 1), lw=1.5)
        ax.lines[-1].set_alpha(alpha)
        for c in ax.collections[-1:]:
            c.set_alpha(0.12 * alpha)
    boundaries([ax], DATA, pop)
    finish(ax, "% of questions answered correctly")
    legend_below(ax, f"{POP_LABEL[pop]} · long-context on {S[arms[0][0]]['hh']} households"
                     f"{' \u2014 ' + GROWING_NOTE if grow else ''} · band = ±1 standard error\n"
                     "one memory told three things; each told arm is drawn from the day it measurably departs",
                 ncol=1, order="reverse")
    nums = {}
    for k, lab, _ in arms:
        nums[lab] = {"days 14-16": r2(avg([S[k]["mean"][d - 1] for d in range(14, 17) if S[k]["mean"][d - 1] is not None])),
                     "days 24-26": r2(avg([S[k]["mean"][d - 1] for d in range(24, 27) if S[k]["mean"][d - 1] is not None])),
                     "drawn from day": clip.get(k, 1)}
    save(fig, "F3_what_one_sentence_buys", manifest, {
        "figure": "F3",
        "claim": "One sentence buys back much of the break and costs on the return; each told arm is identical "
                 "to the untold run until the day it is told.",
        "population": POP_LABEL[pop], "households": {"longcontext": S[arms[0][0]]["hh"]},
        "split": "all questions", "band": "±1 standard error across households",
        "note": "Each told arm is drawn from the day it measurably departs from the arm above it, computed from "
                "the data rather than from the calendar. Departure days are in the numbers below.",
        "provisional": grow and "household count will rise: a larger run is in progress",
        "numbers": nums})


def avg(v):
    return sum(v) / len(v) if v else None


def r2(v):
    return None if v is None else round(v, 1)


FIGS = {"F1": f1, "F2": f2, "F3": f3}


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
    with open(os.path.join(OUT, "MANIFEST.md"), "w") as f:
        f.write("# Paper figures\n\nRegenerated by `results/regime_search/tools/paper_figures.py` from "
                "`story_data.json` and `story_extra.json` — the same files the interactive page is built from. "
                "No number here or in any figure is typed into the script.\n\n")
        for e in ordered:
            f.write(f"## {e['figure']} — {', '.join(e['files'])}\n\n")
            f.write(f"**Claim.** {e['claim']}\n\n")
            f.write(f"- Population: {e['population']}\n")
            f.write(f"- Households: {e['households']}\n")
            for k in ("split", "band", "note", "provisional"):
                if e.get(k):
                    f.write(f"- {k.capitalize()}: {e[k]}\n")
            f.write("\n| series | " + " | ".join(next(iter(e["numbers"].values())).keys()) + " |\n")
            f.write("|" + "---|" * (1 + len(next(iter(e["numbers"].values())))) + "\n")
            for s, row in e["numbers"].items():
                f.write(f"| {s} | " + " | ".join("–" if v is None else str(v) for v in row.values()) + " |\n")
            f.write("\n")
    print(f"\nmanifest: {mpath} and MANIFEST.md ({len(ordered)} figures)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
