#!/usr/bin/env python3
"""Population home-occupancy curves: share of respondents at home by clock
time, weekday vs weekend, split by household type.

The single-diary timelines in :mod:`plot_diary` answer "what did this day
look like", but one diary per cell cannot show a weekday/weekend EFFECT —
individual variation swamps it. This aggregates every diary in the extract
instead: for each minute of the ATUS window (04:00 -> 04:00) it plots the
fraction of respondents who were at home, weekday against weekend.

Household type is read from the diary itself, since demographic labels need
the DDI: a diary containing childcare activity (major 03) is a household
with children; one with neither paid work (05) nor childcare is the
"no work, no childcare" group (retirees, non-employed adults).

"At home" follows the same rule as the timelines: location is the
respondent's home or yard, or location was not asked and the activity is
personal care (asleep, grooming); a not-asked non-personal-care record
carries the previous location forward.

Usage:
  python atus/plot_occupancy.py --out reports/atus/occupancy_weekday_weekend.png
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Dict, List, Tuple

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from read_extract import (DAY_END_MIN, DAY_MINUTES, DAY_START_MIN,  # noqa: E402
                          DEFAULT_EXTRACT, HOME, PERSONAL_CARE, _hms_to_min,
                          _open, diary_dates, layout_of)

SLOTS = ("#2a78d6", "#eb6834")
_INK, _MUTED, _GRID = "#33322e", "#6f6d64", "#dddbd2"
GROUPS = ("family with children", "no paid work or childcare")


def accumulate(path: pathlib.Path
               ) -> Tuple[Dict[Tuple[str, bool], List[int]],
                          Dict[Tuple[str, bool], int]]:
    """(group, is_weekend) -> per-minute at-home counts, and diary counts."""
    col = layout_of(path)
    dates = diary_dates(path)
    if not dates:
        raise SystemExit(f"{path} has no diary-date field — weekday vs "
                         f"weekend needs it (add DAY to the IPUMS extract)")
    counts = {(g, w): [0] * DAY_MINUTES for g in GROUPS for w in (False, True)}
    n_diaries = {(g, w): 0 for g in GROUPS for w in (False, True)}

    caseid = None
    spans: List[Tuple[int, int]] = []      # at-home spans of the current diary
    work = kids = 0
    at_home, offset, prev_stop = True, 0, 0

    def flush() -> None:
        nonlocal spans, work, kids
        if caseid is None:
            return
        group = ("family with children" if kids >= 60
                 else "no paid work or childcare" if work == 0 and kids == 0
                 else None)
        when = dates.get(caseid)
        if group is not None and when is not None:
            key = (group, when.weekday() >= 5)
            n_diaries[key] += 1
            row = counts[key]
            for a, b in spans:
                for m in range(max(a, DAY_START_MIN), min(b, DAY_END_MIN)):
                    row[m - DAY_START_MIN] += 1
        spans, work, kids = [], 0, 0

    with _open(path) as f:
        for raw in f:
            if raw[0] != "3":
                continue
            case = raw[6:20]
            if case != caseid:
                flush()
                caseid = case
                at_home, offset, prev_stop = True, 0, 0
            code = raw[col["activity"][0]:col["activity"][1]]
            where = int(raw[col["where"][0]:col["where"][1]])
            start = _hms_to_min(raw[col["start"][0]:col["start"][1]])
            stop = _hms_to_min(raw[col["stop"][0]:col["stop"][1]])
            if start + offset < prev_stop:
                offset += DAY_MINUTES
            s, e = start + offset, stop + offset
            if e < s:
                e += DAY_MINUTES
            prev_stop = e
            dur = e - s
            if where == HOME:
                at_home = True
            elif where >= 9000:
                if code[:2] == PERSONAL_CARE:
                    at_home = True
            else:
                at_home = False
            if code[:2] == "05":
                work += dur
            if code[:2] == "03":
                kids += dur
            if at_home:
                spans.append((s, e))
        flush()
    return counts, n_diaries


def render(counts, n_diaries, out: pathlib.Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.6), sharey=True)
    xs = [DAY_START_MIN + i for i in range(DAY_MINUTES)]
    for ax, group in zip(axes, GROUPS):
        series = {}
        for colour, weekend in zip(SLOTS, (False, True)):
            key = (group, weekend)
            ys = [c / n_diaries[key] for c in counts[key]]
            series[weekend] = (ys, colour)
            ax.plot(xs, ys, color=colour, linewidth=2)
        # Direct-label each curve where the two are FURTHEST apart: at the
        # right edge both converge on "everyone asleep at home" and labels
        # would collide there.
        wd, wk = series[False][0], series[True][0]
        i = max(range(DAY_MINUTES), key=lambda j: abs(wd[j] - wk[j]))
        for weekend, (ys, colour) in series.items():
            above = ys[i] > (wd[i] + wk[i]) / 2
            ax.annotate("weekend" if weekend else "weekday",
                        xy=(xs[i], ys[i]),
                        xytext=(0, 9 if above else -16),
                        textcoords="offset points", ha="center",
                        color=colour, fontsize=8.5)
        ax.set_title(f"{group}\n"
                     f"{n_diaries[(group, False)]:,} weekday + "
                     f"{n_diaries[(group, True)]:,} weekend diaries",
                     fontsize=9.5, color=_INK, loc="left")
        ax.set_xlim(DAY_START_MIN, DAY_END_MIN)
        ax.set_ylim(0, 1.02)
        ticks = list(range(DAY_START_MIN, DAY_END_MIN + 1, 240))
        ax.set_xticks(ticks, [f"{(t // 60) % 24:02d}:00" for t in ticks])
        ax.tick_params(colors=_INK, labelsize=8.5)
        ax.yaxis.grid(True, color=_GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color(_MUTED)
        ax.spines["left"].set_color(_MUTED)
    axes[0].set_ylabel("share of respondents at home", fontsize=9, color=_INK)
    for ax in axes:
        ax.set_xlabel("time of day (04:00 to 04:00)", fontsize=9,
                      color=_MUTED)
    axes[0].legend(handles=[Line2D([], [], color=c, linewidth=2.5,
                                   label=lab)
                            for c, lab in zip(SLOTS, ("weekday (Mon-Fri)",
                                                      "weekend (Sat-Sun)"))],
                   loc="lower left", fontsize=8.5, frameon=False)
    fig.suptitle("Who is home, and when — ATUS 2006-2025, weekday vs weekend",
                 x=0.006, ha="left", fontsize=11, color=_INK)
    fig.text(0.006, 0.9,
             "Unweighted share of respondents at home (home/yard; asleep and "
             "personal care count as at home). Household type read from "
             "diary content.",
             ha="left", fontsize=8.5, color=_MUTED)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"wrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--extract", type=pathlib.Path, default=DEFAULT_EXTRACT)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()
    counts, n_diaries = accumulate(args.extract)
    for key, n in sorted(n_diaries.items()):
        print(f"  {key[0]:<26} {'weekend' if key[1] else 'weekday'}: "
              f"{n:,} diaries")
    render(counts, n_diaries, args.out)


if __name__ == "__main__":
    main()
