#!/usr/bin/env python3
"""Accuracy by day under the two room choosers, on the same three homes and the same arms.

A window table hides what the day curves show, and the days that matter here are the first few
after each transition - day 14, when the illness starts, and day 24, when it ends. So this plots
every day, pools the three households (they are the same households in both waves), and marks the
two transitions.

LastSeen is drawn in both panels' background as the fixed reference: it makes no model call, so its
curve is identical in the two waves by construction.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/plot_the_chooser.py
"""
import json
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                   # noqa: E402

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import figure_style as st                                         # noqa: E402
from self_improve import search_driven as sd                      # noqa: E402
from self_improve.frozen_household import FrozenHousehold         # noqa: E402

st.apply(plt)
ROOM_FIRST = pathlib.Path("results/self_improve/overnight_wave_24_questions/cells")
REASON_FIRST = pathlib.Path("results/self_improve/wave_reasons_first/cells")
BANKS = pathlib.Path("results/self_improve/varied_homes/ten_homes/banks")
HOMES = ("hh_s2_t03", "hh_s32_t03", "hh_s48_t03")
ARMS = [("the_log_and_notes_about_the_routine", "log and notes"),
        ("incremental_edits", "claim store"),
        ("ACE_as_published", "ACE"),
        ("ours_allowance_derived", "counted allowance")]
DAYS = list(range(1, 32))


def rows(wave, arm, home):
    return [r for r in (json.loads(l) for l in (wave / arm / home / "searches.jsonl").open())
            if r.get("kind") == "search"]


def curve(wave, arm, movers_only):
    """Pooled over the three homes, one point a day, plus the questions behind each point."""
    got, tot = {d: 0 for d in DAYS}, {d: 0 for d in DAYS}
    for home in HOMES:
        movers = sd.the_movers(FrozenHousehold(BANKS / f"{home}.jsonl")) if movers_only else None
        for r in rows(wave, arm, home):
            if r["day"] not in tot or (movers_only and r["object_id"] not in movers):
                continue
            tot[r["day"]] += 1
            got[r["day"]] += r.get("found_at_step") == 1
    return ([100 * got[d] / tot[d] if tot[d] else float("nan") for d in DAYS],
            [tot[d] for d in DAYS])


def main() -> int:
    fig, axes = plt.subplots(2, 4, figsize=(st.TEXT_WIDTH_IN, 3.4), sharex=True, sharey=True)
    for col, (arm, label) in enumerate(ARMS):
        for row, movers_only in enumerate((False, True)):
            ax = axes[row][col]
            ax.axvspan(13.5, 23.5, color=st.ILLNESS_SHADE, lw=0, zorder=0)
            rule, _ = curve(ROOM_FIRST, "last_seen_no_model", movers_only)
            ax.plot(DAYS, rule, color="#b9b9b4", lw=0.9, zorder=2)
            a, counts = curve(ROOM_FIRST, arm, movers_only)
            b, _ = curve(REASON_FIRST, arm, movers_only)
            ax.plot(DAYS, a, color=st.MUTED, lw=1.1, ls=(0, (2.5, 1.5)), zorder=3)
            ax.plot(DAYS, b, color=st.COLOUR["log and notes"] if col == 0 else
                    ["", st.COLOUR["claim store"], st.COLOUR["ACE"],
                     st.COLOUR["LastSeen"]][col], lw=1.4, zorder=4)
            for day in (14, 24):
                ax.axvline(day, color=st.INK, lw=0.5, ls=(0, (1, 2)), zorder=1)
            ax.set_xlim(1, 31)
            ax.set_ylim(0, 105)
            ax.set_xticks([1, 14, 24, 31])
            if row == 0:
                ax.set_title(label, fontsize=8, pad=3,
                             color=st.COLOUR["log and notes"] if col == 0 else
                             ["", st.COLOUR["claim store"], st.COLOUR["ACE"],
                              st.COLOUR["LastSeen"]][col])
            if row == 1:
                ax.set_xlabel("day")
            if col == 0:
                ax.set_ylabel("every question\nfirst room right (%)" if row == 0
                              else "moved objects\nfirst room right (%)")
    axes[0][0].plot([], [], color=st.MUTED, lw=1.1, ls=(0, (2.5, 1.5)), label="room first")
    axes[0][0].plot([], [], color=st.COLOUR["log and notes"], lw=1.4, label="reason first")
    axes[0][0].plot([], [], color="#b9b9b4", lw=0.9, label="LastSeen (same in both)")
    axes[0][0].legend(loc="lower left", fontsize=6.5, handlelength=1.5, borderpad=0.1,
                      labelspacing=0.25)
    out = pathlib.Path("results/self_improve/paper/figures/the_chooser_by_day.pdf")
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out}")
    for arm, label in ARMS:
        for movers_only in (False, True):
            a, counts = curve(ROOM_FIRST, arm, movers_only)
            b, _ = curve(REASON_FIRST, arm, movers_only)
            what = "moved" if movers_only else "all  "
            picks = {d: (a[DAYS.index(d)], b[DAYS.index(d)], counts[DAYS.index(d)])
                     for d in (13, 14, 15, 16, 23, 24, 25, 26)}
            print(f"  {label:20s} {what}  " + "  ".join(
                f"d{d}: {x:.0f}->{y:.0f}" for d, (x, y, n) in picks.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
