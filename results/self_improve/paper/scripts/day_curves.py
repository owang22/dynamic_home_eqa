#!/usr/bin/env python3
"""The paper's day curves, in the house style: two or three average lines and nothing else.

Style rules, from the reference figure F2_relearning_inside_the_spell: first-guess accuracy on y,
day on x, two or three average lines, one colour and one marker per method across every figure, the
regimes named inside the axes with a dotted line at each transition, a bold legend below, and the y
axis zoomed to the range the results occupy. No per-household lines, no error bands - a method that
belongs in a table goes in the table.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/day_curves.py
"""
import json
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                    # noqa: E402

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import figure_style as st                                          # noqa: E402
import paper_data as D                                             # noqa: E402
from self_improve import search_driven as sd                       # noqa: E402
from self_improve.frozen_household import FrozenHousehold          # noqa: E402

st.apply(plt)
OUT = pathlib.Path("results/self_improve/paper/figures")
FIRST = lambda r: r.get("found_at_step") == 1


def pooled(cells, arm, homes, days, objects_of=None):
    """One point a day, pooled over households - the average line, and nothing under it."""
    got = {d: 0 for d in days}
    tot = {d: 0 for d in days}
    for home in homes:
        keep = objects_of(home) if objects_of else None
        for r in D.rows(cells, arm, home):
            if r["day"] not in tot or (keep is not None and r["object_id"] not in keep):
                continue
            tot[r["day"]] += 1
            got[r["day"]] += FIRST(r)
    return [100 * got[d] / tot[d] if tot[d] else float("nan") for d in days], tot


def draw(name, title, series, days, spans, ylim, note=None, width=0.62, height=2.6):
    # Constrained layout is off here: the legend sits under the axes in a margin this reserves,
    # and constrained layout silently ignores subplots_adjust.
    # THE FIGURE HAS TO BE BORN WITHOUT CONSTRAINED LAYOUT. `layout=None` falls back to the
    # rcParam, which is constrained here, and `set_layout_engine("none")` afterwards installs a
    # placeholder that KEEPS the incompatibility flag - so subplots_adjust warned and did nothing,
    # twice, while the figure looked unchanged.
    with plt.rc_context({"figure.constrained_layout.use": False}):
        fig, ax = plt.subplots(figsize=(st.TEXT_WIDTH_IN * width, height))
    for label, values in series:
        st.line(ax, days, values, label)
    ax.set_ylim(*ylim)
    ax.set_xlim(days[0] - 0.4, days[-1] + 0.4)
    ax.set_xlabel("Day", fontweight="bold")
    ax.set_ylabel("First-guess accuracy (%)", fontweight="bold")
    ax.set_title(title, fontweight="bold", pad=15)
    ax.grid(axis="x", visible=False)
    st.regimes(ax, spans)
    # ONE ENTRY PER ROW, like the reference figure. Three entries side by side ran off both edges
    # of a 3.4 inch canvas on the first try.
    # Measured against the rendered page, not guessed: the y label is bold and two words, the
    # title clears the regime words above the axes, and the legend gets one row per method under
    # the x label. The canvas is fixed, so anything outside these margins is cropped away.
    bottom = 0.125 + 0.058 * len(series)
    fig.subplots_adjust(left=0.20, right=0.98, top=0.855, bottom=bottom + 0.10)
    st.legend_below(fig, ax, [label for label, _ in series], ncol=1)
    fig.savefig(OUT / name)
    plt.close(fig)
    print(f"wrote {OUT / name}")


def main() -> int:
    # --- the first illness, ten households, moved objects
    cells = pathlib.Path("results/self_improve/overnight_wave/cells")
    banks = pathlib.Path("results/self_improve/varied_homes/ten_homes/banks")
    days = list(range(1, 32))
    movers = lambda h: sd.the_movers(FrozenHousehold(banks / f"{h}.jsonl"))
    series, counts = [], None
    for arm, label in (("last_seen_no_model", "last seen"),
                       ("the_log_and_notes_about_the_routine", "log and notes"),
                       ("ACE_as_published", "ACE")):
        if not (cells / arm).exists():
            continue
        values, counts = pooled(cells, arm, D.HOMES_10, days, movers)
        series.append((label, values))
    for arm, label in (("claim_store_told_if_it_was_right", "reduced ACE"),):
        if len(series) < 3:
            values, counts = pooled(cells, arm, D.HOMES_10, days, movers)
            series.append((label, values))
    draw("first_illness_adaptation.pdf", "Adapting inside the illness", series, days,
         [(1, 13, "normal"), (14, 23, "sick"), (24, 31, "normal")], (0, 100),
         note=None)  # the question counts belong in the caption, not on the plot

    # --- the two illnesses, three households, the objects that move in both
    days50 = list(range(1, 50))
    series = []
    for arm, label in (("last_seen_no_model", "last seen"),
                       ("the_log_and_notes_about_the_routine", "log and notes"),
                       ("ACE_as_published", "ACE")):
        values, counts = pooled(D.WAVE_50, arm, D.HOMES_50, days50, D.both_spell_movers)
        series.append((label, values))
    draw("recurrence_timeline.pdf", "The same illness, twice", series, days50,
         # the two short "normal" stretches between the spells are only eight days wide, so they
         # are left unnamed rather than crowded - the dotted lines and the two "sick" words carry it
         [(1, 13, "normal"), (14, 23, "sick"), (24, 31, ""), (32, 41, "sick"),
          (42, 49, "normal")], (0, 105),
         note=None)

    # --- the mode memory against the trail and our arm, ten households, moved objects
    saved = pathlib.Path("results/self_improve/paper/household_mode")

    def mode_curve(run, homes, days, objects_of):
        got = {d: 0 for d in days}
        tot = {d: 0 for d in days}
        for home in homes:
            rows = json.loads((saved / f"{run}~{home}~a1.0~s0.9.json").read_text())["rows"]
            keep = objects_of(home)
            for r in rows:
                if r["day"] in tot and r["object_id"] in keep:
                    tot[r["day"]] += 1
                    got[r["day"]] += r.get("found_at_step") == 1
        return [100 * got[d] / tot[d] if tot[d] else float("nan") for d in days]

    series = []
    for arm, label in (("last_seen_no_model", "last seen"),
                       ("the_log_and_notes_about_the_routine", "log and notes")):
        values, _ = pooled(cells, arm, D.HOMES_10, days, movers)
        series.append((label, values))
    series.append(("household mode",
                   mode_curve("ten_homes_8_a_day", D.HOMES_10, days, movers)))
    draw("household_mode.pdf", "A mode memory, no language model", series, days,
         [(1, 13, "normal"), (14, 23, "sick"), (24, 31, "normal")], (0, 100), note=None,
         width=0.70)

    # --- the chooser, two lines, one panel
    days31 = list(range(1, 32))
    series = []
    for cells_dir, label in ((pathlib.Path(
            "results/self_improve/overnight_wave_24_questions/cells"), "room first"),
            (pathlib.Path("results/self_improve/wave_reasons_first/cells"), "reason first")):
        values, counts = pooled(cells_dir, "the_log_and_notes_about_the_routine",
                                D.HOMES_50, days31, movers)
        series.append((label, values))
    draw("the_chooser_by_day.pdf", "Does it matter when the room is chosen?", series, days31,
         [(1, 13, "normal"), (14, 23, "sick"), (24, 31, "normal")], (0, 105),
         note=None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
