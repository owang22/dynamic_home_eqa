#!/usr/bin/env python3
"""Render ATUS respondent-days as 24-hour home-occupancy timelines.

Each diary is collapsed to what happens INSIDE the home (full activity
detail) plus merged "out of house" spans — see
:func:`read_extract.home_blocks`. Colour, labels, and the legend are keyed
to the DETAILED activity, not its major category: the eight activities with
the most total minutes ACROSS EVERY PANEL IN THE FIGURE take the validated
palette's fixed slots, so an activity keeps one colour in all panels;
rarer activities share a neutral (they stay directly labelled where they
fit, so detail is never lost), and time out of the house is hatched.

Ranking the hue slots over the whole figure rather than per panel is the
point: colour follows the activity, never its rank within one day.

Usage:
  python atus/plot_diary.py --caseid <ID> --out one_day.png
  python atus/plot_diary.py --panels "Home A, work day=2025...:Home B, ...=2025..." \
      --out compare.png
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import math
import sys
import textwrap
from typing import Dict, List, Tuple

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from read_extract import (DAY_END_MIN, DAY_START_MIN, DEFAULT_EXTRACT,  # noqa: E402
                          Block, by_case, home_blocks)

SLOTS = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100",
         "#e87ba4", "#008300", "#4a3aa7", "#e34948")
LIGHT_TEXT_ON = {"#eda100", "#1baf7a"}      # these want ink, not white
OTHER = "#8f8d84"
AWAY = "#e8e6de"
_INK, _MUTED, _GRID = "#33322e", "#6f6d64", "#dddbd2"

FIG_WIDTH_IN = 15.0
LABEL_FONT_PT = 7.0
CHARS_PER_MINUTE = (FIG_WIDTH_IN / 1440) / (LABEL_FONT_PT * 0.6 / 72)
LABEL_MIN_CHARS = 6


def assign_hues(panels: List[Tuple[str, List[Block]]]) -> Dict[str, str]:
    """activity label -> colour, ranked by total minutes over ALL panels."""
    total: collections.Counter[str] = collections.Counter()
    for _, blocks in panels:
        for b in blocks:
            if b.at_home:
                total[b.label] += b.duration
    return {label: SLOTS[i]
            for i, (label, _) in enumerate(total.most_common(len(SLOTS)))}


def render(panels: List[Tuple[str, List[Block]]], out: pathlib.Path,
           title: str, subtitle: str = "") -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    hue = assign_hues(panels)
    n = len(panels)
    # Header height grows with the wrapped subtitle so it can never ride up
    # into the title.
    sub_lines = textwrap.wrap(subtitle, 128) if subtitle else []
    head_in = 0.5 + 0.19 * len(sub_lines)          # title + wrapped subtitle
    n_legend = len(hue) + 2                        # + "other" + "out of house"
    legend_in = 0.3 + 0.19 * math.ceil(n_legend / 4)
    axis_in = 0.55                                 # ticks + x label
    fig_h = 1.15 * n + head_in + axis_in + legend_in
    fig, axes = plt.subplots(n, 1, figsize=(FIG_WIDTH_IN, fig_h), sharex=True)
    axes = [axes] if n == 1 else list(axes)
    used_other = used_away = False

    for ax, (label, blocks) in zip(axes, panels):
        for b in blocks:
            if not b.at_home:
                ax.barh(0, b.duration - 2, left=b.start_min, height=0.6,
                        color=AWAY, edgecolor="white", linewidth=0.8,
                        hatch="///")
                used_away = True
                continue
            colour = hue.get(b.label, OTHER)
            used_other = used_other or b.label not in hue
            ax.barh(0, b.duration - 2, left=b.start_min, height=0.6,
                    color=colour, edgecolor="white", linewidth=0.8)
            fits = int(b.duration * CHARS_PER_MINUTE) - 1
            if fits >= LABEL_MIN_CHARS:
                text = (b.label if len(b.label) <= fits
                        else b.label[:fits - 1].rstrip(" ,(") + "…")
                ax.text((b.start_min + b.stop_min) / 2, 0, text,
                        ha="center", va="center", fontsize=LABEL_FONT_PT,
                        color=_INK if colour in LIGHT_TEXT_ON or colour == AWAY
                        else "white")
        home = sum(b.duration for b in blocks if b.at_home)
        ax.set_ylabel(f"{label}\n{home / 60:.1f} h home", rotation=0,
                      ha="right", va="center", fontsize=8.5, color=_INK,
                      labelpad=12)
        ax.set_xlim(DAY_START_MIN, DAY_END_MIN)
        ax.set_ylim(-0.45, 0.45)
        ax.set_yticks([])
        ax.xaxis.grid(True, color=_GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color(_MUTED)

    ticks = list(range(DAY_START_MIN, DAY_END_MIN + 1, 120))
    axes[-1].set_xticks(ticks, [f"{(t // 60) % 24:02d}:00" for t in ticks])
    axes[-1].tick_params(colors=_INK, labelsize=8.5)
    axes[-1].set_xlabel("time of day (ATUS diary window, 04:00 to 04:00)",
                        fontsize=9, color=_MUTED)

    handles = [Patch(facecolor=c, label=lab) for lab, c in hue.items()]
    if used_other:
        handles.append(Patch(facecolor=OTHER, label="other home activity "
                                                   "(see block labels)"))
    if used_away:
        handles.append(Patch(facecolor=AWAY, hatch="///",
                             label="out of house"))
    # Figure coordinates: axes-relative anchoring drifts with panel count.
    fig.legend(handles=handles, loc="lower left",
               bbox_to_anchor=(0.027, 0.012), ncol=4, fontsize=8,
               frameon=False, title="activity", title_fontsize=8.5,
               alignment="left")
    fig.tight_layout(rect=(0.02, (legend_in + 0.12) / fig_h, 0.995,
                           1 - head_in / fig_h))
    y = 1 - 0.16 / fig_h
    fig.text(0.008, y, title, ha="left", va="top", fontsize=11, color=_INK)
    for i, line in enumerate(sub_lines):
        fig.text(0.008, y - (0.24 + 0.19 * (i + 1)) / fig_h, line,
                 ha="left", va="top", fontsize=8.5, color=_MUTED)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"wrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--extract", type=pathlib.Path, default=DEFAULT_EXTRACT)
    ap.add_argument("--caseid", default=None)
    ap.add_argument("--panels", default=None,
                    help="colon-separated 'label=caseid' pairs")
    ap.add_argument("--title", default="ATUS home-occupancy diaries")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    diaries = by_case(args.extract)
    if args.panels:
        spec = [p.split("=", 1) for p in args.panels.split(":")]
    elif args.caseid:
        spec = [(f"respondent {args.caseid}", args.caseid)]
    else:
        raise SystemExit("give --caseid or --panels")
    panels = []
    for label, caseid in spec:
        caseid = caseid.strip()
        if caseid not in diaries:
            raise SystemExit(f"caseid {caseid} not in extract")
        panels.append((label.strip(), home_blocks(diaries[caseid])))
    render(panels, args.out, args.title, args.subtitle)


if __name__ == "__main__":
    main()
