#!/usr/bin/env python3
"""The paper's four figures, as vector PDF.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/make_figures.py
    CORL_TEXTWIDTH_IN=5.87 PYTHONPATH=src python3 .../make_figures.py     # once the real width is known

Read `figure_style.py` first: it holds the one text width, the type sizes and the validated method
colours, and it says why the width has to be checked against corl_2026.sty.

Every figure prints the numbers it drew, so the caption can be written from this output rather than
from reading the picture.
"""
import pathlib
import statistics
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                    # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle          # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import figure_style as st                                          # noqa: E402
import paper_data as D                                             # noqa: E402

OUT = pathlib.Path("results/self_improve/paper/figures")
st.apply(plt)


def spread_down(labelled, gap, ceiling):
    """Place labels from the top down so none is pushed off the axes. `labelled` is
    (name, value) pairs; returns (name, y) with at least `gap` between neighbours."""
    out, last = [], ceiling
    for name, value in sorted(labelled, key=lambda kv: -kv[1]):
        y = min(value, last)
        out.append((name, y))
        last = y - gap
    return out


def spread(values, gap):
    """Nudge labels apart so two lines ending at the same height do not print on top of each
    other. Returns a y for each value, keeping their order and their rough position."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = list(values)
    for k, i in enumerate(order):
        if k and out[i] - out[order[k - 1]] < gap:
            out[i] = out[order[k - 1]] + gap
    return out


def shade(ax, days, label=None):
    ax.axvspan(days[0] - 0.5, days[-1] + 0.5, color=st.ILLNESS_SHADE, zorder=0, lw=0)
    if label:
        ax.text((days[0] + days[-1]) / 2, ax.get_ylim()[1], label, ha="center", va="top",
                fontsize=7, color=st.MUTED)


# ------------------------------------------------------------------ figure 2 --
def recurrence_first_day():
    """Found within 3 rooms on both-spell movers: the first day of each illness."""
    arms = ["last-seen", "log and notes", "claim store", "ACE"]
    by_arm = {a: {} for a in arms}
    for directory, label in D.ARM_50.items():
        for home in D.HOMES_50:
            rs = D.rows(D.WAVE_50, directory, home)
            movers = D.both_spell_movers(home)
            pick = lambda day: [r for r in rs if r["day"] == day and r["object_id"] in movers]
            a, b = pick(14), pick(32)
            by_arm[label][home] = (D.share(a, "found"), D.share(b, "found"), len(a), len(b))

    fig, axes = plt.subplots(1, 4, figsize=(st.TEXT_WIDTH_IN, 2.05), sharey=True)
    print("\n=== figure 2: found within 3 rooms on both-spell movers, day 14 -> day 32")
    for ax, label in zip(axes, arms):
        moves = []
        rows_here = sorted(by_arm[label].items())
        left = spread([v[1][0] for v in rows_here], 9)
        right = spread([v[1][1] for v in rows_here], 9)
        for (home, (y14, y32, n14, n32)), ly, ry in zip(rows_here, left, right):
            ax.plot([0, 1], [y14, y32], "-o", color=st.COLOUR[label], lw=1.2, ms=3.5,
                    markerfacecolor="white", markeredgewidth=1.0, zorder=3)
            ax.annotate(f"{n14}", (0, ly), textcoords="offset points", xytext=(-7, 0),
                        fontsize=6.5, color=st.MUTED, ha="right", va="center")
            ax.annotate(f"{n32}", (1, ry), textcoords="offset points", xytext=(7, 0),
                        fontsize=6.5, color=st.MUTED, ha="left", va="center")
            moves.append(y32 - y14)
        mean = statistics.mean(moves)
        tse = 2 * statistics.stdev(moves) / len(moves) ** 0.5
        ax.set_title(label, color=st.COLOUR[label], pad=6)
        ax.text(0.5, 0.02, f"{mean:+.1f} points\n2 SE {tse:.1f}", transform=ax.transAxes,
                ha="center", va="bottom", fontsize=7.2, color=st.INK, linespacing=1.3,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.2))
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["day 14", "day 32"])
        ax.set_xlim(-0.45, 1.45)
        ax.set_ylim(0, 108)
        ax.grid(axis="x", visible=False)
        print(f"  {label:14s} " + "  ".join(
            f"{h.replace('_t03','')}: {a:.0f}->{b:.0f} ({na}/{nb} q)"
            for h, (a, b, na, nb) in sorted(by_arm[label].items()))
            + f" | mean {mean:+.1f}, 2 SE {tse:.1f}")
    axes[0].set_ylabel("found within 3 rooms (%)")
    axes[0].set_yticks([0, 25, 50, 75, 100])
    fig.savefig(OUT / "recurrence_first_day.pdf")
    plt.close(fig)


# ------------------------------------------------------------------ figure 3 --
def recurrence_timeline():
    """The same measure, every day of the 50-day month, averaged over the three homes."""
    days = list(range(1, 50))
    fig, (ax, bar) = plt.subplots(2, 1, figsize=(st.TEXT_WIDTH_IN, 2.9), sharex=True,
                                  gridspec_kw={"height_ratios": [4, 1]})
    print("\n=== figure 3: found within 3 rooms on both-spell movers, by day")
    counts = {d: 0 for d in days}
    ends = {}
    for directory, label in D.ARM_50.items():
        per_home = {}
        for home in D.HOMES_50:
            movers = D.both_spell_movers(home)
            rs = [r for r in D.rows(D.WAVE_50, directory, home) if r["object_id"] in movers]
            per_home[home] = rs
            if label == "last-seen":
                for r in rs:
                    counts[r["day"]] = counts.get(r["day"], 0) + 1
        line, band = [], []
        for day in days:
            rates = [D.share([r for r in per_home[h] if r["day"] == day], "found")
                     for h in D.HOMES_50]
            rates = [r for r in rates if r is not None]
            line.append(statistics.mean(rates) if rates else float("nan"))
            band.append(statistics.stdev(rates) / len(rates) ** 0.5 if len(rates) > 1 else 0.0)
        ax.fill_between(days, [m - s for m, s in zip(line, band)],
                        [m + s for m, s in zip(line, band)],
                        color=st.COLOUR[label], alpha=0.13, lw=0, zorder=2)
        ax.plot(days, line, color=st.COLOUR[label], lw=1.3, zorder=3, label=label)
        ends[label] = line[-1]
        print(f"  {label:14s} settled {statistics.mean([v for d, v in zip(days, line) if d < 14]):.0f}"
              f"  day 14 {line[13]:.0f}  spell 1 "
              f"{statistics.mean([v for d, v in zip(days, line) if 14 <= d <= 23]):.0f}"
              f"  day 32 {line[31]:.0f}  spell 2 "
              f"{statistics.mean([v for d, v in zip(days, line) if 32 <= d <= 41]):.0f}")
    ax.set_ylim(0, 105)
    for label, y in spread_down(list(ends.items()), 7.5, 101):
        ax.annotate(label, (49.6, y), fontsize=7.5, color=st.COLOUR[label], va="center")
    ax.set_ylabel("found within 3 rooms (%)")
    shade(ax, list(D.SPELL_1))
    shade(ax, list(D.SPELL_2))
    for day in (14, 32):
        ax.axvline(day, color=st.MUTED, lw=0.7, ls=(0, (2, 2)), zorder=1)
        ax.annotate(f"day {day}", (day, 103), fontsize=7, color=st.MUTED, ha="center", va="top",
                    backgroundcolor="white")
    bar.bar(days, [counts[d] for d in days], color=st.MUTED, width=0.75, lw=0)
    bar.set_ylabel("questions", fontsize=7.5)
    bar.set_xlabel("day")
    bar.set_xlim(0.2, 58)
    bar.grid(axis="x", visible=False)
    shade(bar, list(D.SPELL_1))
    shade(bar, list(D.SPELL_2))
    ax.set_xlim(0.2, 58)
    fig.savefig(OUT / "recurrence_timeline.pdf")
    plt.close(fig)
    print(f"  both-spell-mover questions a day, over three homes: "
          f"{min(counts.values())} to {max(counts.values())}")


# ------------------------------------------------------------------ figure 4 --
def first_illness_adaptation():
    """First room right on spell-1 movers, the ten-household run, one panel per method.

    SIX LINES ON ONE AXIS WOULD NOT HAVE BEEN LEGIBLE. Seven method colours cannot all sit at the
    validator's normal-vision floor of dE 15 at once, and the dataviz rule for that case is to
    facet rather than to cycle hues, so each method gets a panel with the other five behind it in
    grey. Identity is then colour AND position, and no pair has to be told apart by hue alone.
    """
    print("\n=== figure 4: first room right on spell-1 movers, ten-household run, by day")
    days = list(range(1, 32))
    curves = {}
    for directory, label in D.ARM_10.items():
        per_home = {}
        for home in D.HOMES_10:
            movers = D.spell_1_movers(home)
            per_home[home] = [r for r in D.rows(D.WAVE_10, directory, home)
                              if r["object_id"] in movers]
        line, band = [], []
        for day in days:
            rates = [D.share([r for r in per_home[h] if r["day"] == day], "first")
                     for h in D.HOMES_10]
            rates = [r for r in rates if r is not None]
            line.append(statistics.mean(rates) if rates else float("nan"))
            band.append(statistics.stdev(rates) / len(rates) ** 0.5 if len(rates) > 1 else 0.0)
        curves[label] = (line, band)
        print(f"  {label:22s} settled 8-13 "
              f"{statistics.mean(line[7:13]):.0f}  day 14 {line[13]:.0f}  "
              f"day 17 {line[16]:.0f}  day 24 {line[23]:.0f}")
    fig, axes = plt.subplots(2, 3, figsize=(st.TEXT_WIDTH_IN, 3.0), sharex=True, sharey=True)
    for ax, (label, (line, band)) in zip(axes.ravel(), curves.items()):
        for other, (ol, _) in curves.items():
            if other != label:
                ax.plot(days, ol, color="#cfcfca", lw=0.7, zorder=2)
        ax.fill_between(days, [m - s for m, s in zip(line, band)],
                        [m + s for m, s in zip(line, band)],
                        color=st.COLOUR[label], alpha=0.16, lw=0, zorder=3)
        ax.plot(days, line, color=st.COLOUR[label], lw=1.4, zorder=4)
        ax.set_title(label, color=st.COLOUR[label], pad=4, fontsize=8)
        shade(ax, list(range(14, 24)))
        ax.set_ylim(0, 105)
        ax.set_xlim(1, 31)
        ax.set_xticks([1, 14, 24, 31])
    for ax in axes[:, 0]:
        ax.set_ylabel("first room right (%)")
    for ax in axes[1, :]:
        ax.set_xlabel("day")
    fig.savefig(OUT / "first_illness_adaptation.pdf")
    plt.close(fig)


# ------------------------------------------------------------------ figure 1 --
def overview():
    """The schematic: the calendar, what the illness does to one object, and the loop.

    Hand-placed geometry, because the first version let matplotlib route the return arrow and it
    drew a curve straight through the five boxes and into the first one from above.
    """
    fig = plt.figure(figsize=(st.TEXT_WIDTH_IN, 3.7))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 1.6, 1.5])

    # --- top: the calendar
    ax = fig.add_subplot(gs[0])
    ax.set_axis_off()
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 1)
    for start_day, end_day, name, ill in [(0, 13, "normal", False), (14, 23, "illness", True),
                                          (24, 31, "normal", False), (32, 41, "illness", True),
                                          (42, 49, "normal", False)]:
        ax.add_patch(Rectangle((start_day, 0.30), end_day - start_day + 1, 0.36,
                               facecolor=st.ILLNESS_SHADE if ill else "white",
                               edgecolor=st.MUTED, lw=0.6))
        ax.text((start_day + end_day + 1) / 2, 0.48, name, ha="center", va="center",
                fontsize=7.8, color=st.INK if ill else st.MUTED)
        ax.text(start_day + 0.3, 0.22, f"day {start_day}", ha="left", va="top", fontsize=6.5,
                color=st.MUTED)
    ax.text(25, 0.92, "a resident is unwell and stays home. The robot is never told.",
            ha="center", va="center", fontsize=8.2, color=st.INK)

    # --- middle: where one object is, as a share of the day
    ax = fig.add_subplot(gs[1])
    rooms = ["office", "kitchen", "living", "bedroom"]
    normal = [0.55, 0.20, 0.15, 0.10]
    ill = [0.10, 0.15, 0.20, 0.55]
    x = range(len(rooms))
    ax.bar([i - 0.19 for i in x], normal, width=0.36, color=st.MUTED, lw=0)
    ax.bar([i + 0.19 for i in x], ill, width=0.36, color=st.COLOUR["log and notes"], lw=0)
    for i, (a, b) in enumerate(zip(normal, ill)):
        ax.text(i - 0.19, a + 0.02, "normal" if i == 0 else "", ha="center", fontsize=7,
                color=st.MUTED)
        ax.text(i + 0.19, b + 0.02, "illness" if i == 0 else "", ha="center", fontsize=7,
                color=st.COLOUR["log and notes"])
    ax.set_xticks(list(x))
    ax.set_xticklabels(rooms)
    ax.set_ylim(0, 0.70)
    ax.set_yticks([0, 0.25, 0.5])
    ax.set_yticklabels(["0", ".25", ".5"])
    ax.set_ylabel("share of the day")
    ax.grid(axis="x", visible=False)
    ax.set_title("where one mug is, hour by hour", fontsize=8.2, pad=4, color=st.INK)
    ax.text(1.5, 0.63, "the weight moves; the mug never sits in one place",
            fontsize=7, color=st.MUTED, ha="center", va="center")

    # --- bottom: the loop
    ax = fig.add_subplot(gs[2])
    ax.set_axis_off()
    ax.set_xlim(0, 10.3)
    ax.set_ylim(0, 1)
    steps = ["a question", "open up to\n3 rooms", "log every object\nin those rooms",
             "nightly memory\nupdate", "the next day's\nsearch"]
    width, gap, top, height = 1.72, 0.35, 0.50, 0.34
    lefts = [0.08 + i * (width + gap) for i in range(len(steps))]
    for left, text in zip(lefts, steps):
        ax.add_patch(Rectangle((left, top), width, height, facecolor="white",
                               edgecolor=st.MUTED, lw=0.6))
        ax.text(left + width / 2, top + height / 2, text, ha="center", va="center",
                fontsize=6.8, color=st.INK, linespacing=1.25)
    for left in lefts[:-1]:
        ax.add_patch(FancyArrowPatch((left + width + 0.03, top + height / 2),
                                     (left + width + gap - 0.03, top + height / 2),
                                     arrowstyle="-|>", mutation_scale=6.5,
                                     color=st.MUTED, lw=0.7))
    # the return leg, drawn BELOW the row with three straight segments
    x_last, x_first, y = lefts[-1] + width / 2, lefts[0] + width / 2, top - 0.20
    ax.plot([x_last, x_last], [top, y], color=st.MUTED, lw=0.7)
    ax.plot([x_last, x_first], [y, y], color=st.MUTED, lw=0.7)
    ax.add_patch(FancyArrowPatch((x_first, y), (x_first, top - 0.015), arrowstyle="-|>",
                                 mutation_scale=6.5, color=st.MUTED, lw=0.7))
    ax.text((x_first + x_last) / 2, y - 0.035, "every day for a month", ha="center", va="top",
            fontsize=7, color=st.MUTED)
    fig.savefig(OUT / "overview.pdf")
    plt.close(fig)
    print("\n=== figure 1: schematic, no data")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    if not st.TEXT_WIDTH_WAS_GIVEN:
        print(f"!! drawing at {st.TEXT_WIDTH_IN} in, a GUESS: corl_2026.sty is not in this repo.\n"
              f"   Re-run with CORL_TEXTWIDTH_IN=<the real \\textwidth in inches>.")
    recurrence_first_day()
    recurrence_timeline()
    first_illness_adaptation()
    overview()
    print("\nwrote:")
    for f in sorted(OUT.glob("*.pdf")):
        print(f"  {f}  {f.stat().st_size/1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
