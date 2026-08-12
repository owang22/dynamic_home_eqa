#!/usr/bin/env python3
"""Render one ATUS respondent-day as a 24-hour timeline figure.

Two stacked strips over the diary window (04:00 -> 04:00 next morning):

* ACTIVITY — one block per diary entry, hue = ATUS major category. The eight
  most common majors hold fixed palette slots so a category keeps its colour
  across diaries; everything rarer folds into a neutral "Other" rather than
  inventing a ninth hue.
* WHERE — the same day as location context, drawn in a single-hue ramp
  (home -> away -> in transit) because that reads as ordered distance from
  home and keeps the identity colours above unambiguous. Time not asked
  (asleep, personal care) is left near-blank.

Usage:
  python atus/plot_diary.py --caseid 20250503251407 \
      --out reports/atus/diary_20250503251407.png
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Dict, List

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from read_extract import (DAY_END_MIN, DAY_START_MIN, DEFAULT_EXTRACT,  # noqa: E402
                          Activity, by_case)

# Validated categorical palette, fixed order (light mode).
SLOTS = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100",
         "#e87ba4", "#008300", "#4a3aa7", "#e34948")
OTHER = "#8f8d84"
# Fixed major-category -> slot assignment: colour follows the category, never
# its rank within a particular diary.
MAJOR_SLOT: Dict[str, int] = {
    "01": 0,   # Personal care
    "02": 1,   # Household activities
    "05": 2,   # Work
    "11": 3,   # Eating and drinking
    "12": 4,   # Socializing, relaxing, leisure
    "18": 5,   # Travel
    "07": 6,   # Consumer purchases
    "03": 7,   # Caring for household members
}
# Single-hue ramp for the location strip: home -> away -> transit.
WHERE_RAMP = {"home": "#b9d2f0", "away": "#4489d9", "transit": "#1a4e8f",
              "niu": "#eceae2"}
WHERE_ORDER = ("home", "away", "transit", "niu")
WHERE_TEXT = {"home": "At home", "away": "Away (workplace, shops, other)",
              "transit": "In transit", "niu": "Not asked (asleep etc.)"}
_INK, _MUTED, _GRID = "#33322e", "#6f6d64", "#dddbd2"
FIG_WIDTH_IN = 14.0
LABEL_FONT_PT = 7.5
# Characters that fit inside a block: minutes -> inches -> character widths
# (~0.6 * font size per char). Labels are truncated to fit rather than
# allowed to spill across neighbouring blocks.
CHARS_PER_MINUTE = (FIG_WIDTH_IN / 1440) / (LABEL_FONT_PT * 0.6 / 72)
LABEL_MIN_CHARS = 7         # narrower than this, leave the block unlabeled


def where_class(a: Activity) -> str:
    if a.where == 9999 or a.where == 9998:
        return "niu"
    if a.is_travel:
        return "transit"
    return "home" if a.is_home else "away"


def render(acts: List[Activity], caseid: str, out: pathlib.Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    fig, (ax_a, ax_w) = plt.subplots(
        2, 1, figsize=(FIG_WIDTH_IN, 5.2), height_ratios=[3, 1], sharex=True)

    majors_seen: List[str] = []
    for a in acts:
        colour = (SLOTS[MAJOR_SLOT[a.code[:2]]] if a.code[:2] in MAJOR_SLOT
                  else OTHER)
        stop = min(a.stop_min, DAY_END_MIN)
        # 2px surface gap between adjacent blocks (spacer rule).
        ax_a.barh(0, stop - a.start_min - 1.5, left=a.start_min, height=0.62,
                  color=colour, edgecolor="white", linewidth=0.8)
        fits = int(a.duration * CHARS_PER_MINUTE) - 1
        if fits >= LABEL_MIN_CHARS:
            text = (a.label if len(a.label) <= fits
                    else a.label[:fits - 1].rstrip(" ,(") + "…")
            ax_a.text((a.start_min + stop) / 2, 0, text,
                      ha="center", va="center", fontsize=LABEL_FONT_PT,
                      color="white" if colour != "#eda100" else _INK)
        key = a.code[:2] if a.code[:2] in MAJOR_SLOT else "other"
        if key not in majors_seen:
            majors_seen.append(key)
        wc = where_class(a)
        ax_w.barh(0, stop - a.start_min - 1.5, left=a.start_min, height=0.55,
                  color=WHERE_RAMP[wc], edgecolor="white", linewidth=0.8)

    for ax in (ax_a, ax_w):
        ax.set_xlim(DAY_START_MIN, DAY_END_MIN)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.xaxis.grid(True, color=_GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color(_MUTED)
    ticks = list(range(DAY_START_MIN, DAY_END_MIN + 1, 120))
    ax_w.set_xticks(ticks, [f"{(t // 60) % 24:02d}:00" for t in ticks])
    ax_w.tick_params(colors=_INK, labelsize=8.5)
    ax_a.tick_params(labelbottom=False)

    from read_extract import MAJOR_LABELS
    ax_a.legend(handles=[
        Patch(facecolor=SLOTS[MAJOR_SLOT[m]] if m != "other" else OTHER,
              label=MAJOR_LABELS.get(m, "Other / data codes"))
        for m in majors_seen],
        loc="upper left", bbox_to_anchor=(0, -0.06), ncol=4, fontsize=8,
        frameon=False, title="activity category", title_fontsize=8)
    ax_w.legend(handles=[Patch(facecolor=WHERE_RAMP[k], label=WHERE_TEXT[k])
                         for k in WHERE_ORDER
                         if any(where_class(a) == k for a in acts)],
                loc="upper left", bbox_to_anchor=(0, -0.55), ncol=4,
                fontsize=8, frameon=False, title="where",
                title_fontsize=8)

    at_home = sum(a.duration for a in acts if where_class(a) == "home")
    away = sum(a.duration for a in acts if where_class(a) == "away")
    transit = sum(a.duration for a in acts if where_class(a) == "transit")
    niu = sum(a.duration for a in acts if where_class(a) == "niu")
    places = len({a.where for a in acts if a.where < 9000})
    fig.suptitle(
        f"ATUS diary — respondent {caseid}   ·   {len(acts)} activities, "
        f"{places} distinct locations   ·   home {at_home / 60:.1f} h, "
        f"away {away / 60:.1f} h, transit {transit / 60:.1f} h, "
        f"not asked {niu / 60:.1f} h",
        x=0.011, ha="left", fontsize=10.5, color=_INK)
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"wrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--extract", type=pathlib.Path, default=DEFAULT_EXTRACT)
    ap.add_argument("--caseid", required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()
    diaries = by_case(args.extract)
    if args.caseid not in diaries:
        raise SystemExit(f"caseid {args.caseid} not in extract")
    render(diaries[args.caseid], args.caseid, args.out)


if __name__ == "__main__":
    main()
