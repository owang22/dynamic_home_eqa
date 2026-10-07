"""The growth figure: how big each arm's memory gets, night by night.

WHY A FIGURE. Oliver asked how a memory's growth should be bounded, and the honest answer
came from this project's own data rather than from the literature: a survey of eight
published memory systems found that **none of them reports this curve for its own method.**
So the curve is worth a plot rather than a sentence.

TWO PANELS, NOT TWO Y-AXES. Live lines and characters are measures of different scale, and
a dual-axis chart is the single most common way to mislead with one - the reader cannot tell
which axis a line belongs to, and the crossing point is an artefact of the two scalings. So
they are small multiples sharing one x-axis.

THE PALETTE IS THE VALIDATED CATEGORICAL ORDER, assigned in fixed slot order and never
cycled, so an arm keeps its colour if another arm is dropped from the plot. Validated with
the data-viz validator at six slots on the light surface: lightness band, chroma floor, CVD
separation (worst adjacent 9.1) and normal-vision floor (worst adjacent 19.6) all pass.
Contrast against the light surface WARNs for three slots, which obliges relief - so this
writes a **CSV table beside the figure**, and the same numbers are in `compliance.json`.
Identity is never colour alone: every arm is in the legend.

    python -m self_improve.three_prompts_growth_figure
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from self_improve.three_prompts import ARMS, PILOT_TEN

# the validated categorical order, light mode. Slots are assigned by the fixed arm order
# below and never by rank, so a filtered plot does not repaint the survivors.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e3e2de"

ARM_ORDER = ("control", "rival_beliefs", "describe_the_person", "told_unwell",
             "rival_and_describe", "control_wholesale")


def curves(compliance: Dict[str, Any]) -> Dict[str, Dict[int, Dict[str, float]]]:
    """arm -> night -> mean over homes of {n_lines, n_characters}."""
    by_arm: Dict[str, Dict[int, List[Dict[str, Any]]]] = {}
    for row in compliance["per_cell"]:
        growth = row.get("growth") or {}
        for night, got in growth.items():
            by_arm.setdefault(row["arm"], {}).setdefault(int(night), []).append(got)
    out: Dict[str, Dict[int, Dict[str, float]]] = {}
    for arm, nights in by_arm.items():
        out[arm] = {}
        for night, these in nights.items():
            out[arm][night] = {
                "n_lines": statistics.mean(g["n_lines"] for g in these),
                "n_characters": statistics.mean(g["n_characters"] for g in these),
                "n_homes": len(these),
            }
    return out


def draw(data: Dict[str, Dict[int, Dict[str, float]]], out_png: pathlib.Path,
         n_homes: int) -> None:
    arms = [a for a in ARM_ORDER if a in data]
    colour = {arm: SERIES[ARM_ORDER.index(arm) % len(SERIES)] for arm in arms}

    fig, axes = plt.subplots(2, 1, figsize=(9.5, 8.2), sharex=True,
                             gridspec_kw={"hspace": 0.16})
    fig.patch.set_facecolor(SURFACE)
    for ax, field, label in ((axes[0], "n_lines", "live lines of notes"),
                             (axes[1], "n_characters", "characters of notes")):
        ax.set_facecolor(SURFACE)
        # the two boundaries the study turns on, drawn recessively and labelled once
        for day, text in ((14, "illness starts"), (24, "back to normal")):
            ax.axvline(day, color=GRID, linewidth=1.5, zorder=0)
            if field == "n_lines":
                ax.annotate(text, xy=(day, 1.005), xycoords=("data", "axes fraction"),
                            ha="center", va="bottom", fontsize=8.5,
                            color=INK_SECONDARY)
        for arm in arms:
            nights = sorted(data[arm])
            ax.plot(nights, [data[arm][n][field] for n in nights],
                    color=colour[arm], linewidth=2.0, solid_capstyle="round",
                    label=arm.replace("_", " "), zorder=3)
        ax.set_ylabel(label, fontsize=10, color=INK_SECONDARY)
        ax.grid(True, axis="y", color=GRID, linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GRID)
        ax.tick_params(colors=INK_SECONDARY, labelsize=9)
        ax.set_ylim(bottom=0)

    axes[1].set_xlabel("night", fontsize=10, color=INK_SECONDARY)
    axes[0].set_title(
        "How big each arm's memory gets, night by night",
        fontsize=13, color=INK, loc="left", pad=26)
    axes[0].annotate(
        f"mean over {n_homes} homes. No length limit, in writing or in reading.\n"
        f"Two panels rather than two y-axes: lines and characters are different scales.",
        xy=(0, 1.055), xycoords="axes fraction", ha="left", va="bottom",
        fontsize=9, color=INK_SECONDARY)
    axes[0].legend(frameon=False, fontsize=9, labelcolor=INK_SECONDARY,
                   ncol=3, loc="upper left", bbox_to_anchor=(0, -0.02))
    fig.savefig(out_png, dpi=170, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/three_prompts"))
    args = parser.parse_args(argv)

    path = args.root / "compliance.json"
    if not path.exists():
        print(f"no {path} yet - run three_prompts_compliance first")
        return 0
    compliance = json.loads(path.read_text())
    data = curves(compliance)
    if not data:
        print("no growth curves in compliance.json")
        return 0
    n_homes = max((g["n_homes"] for arm in data.values() for g in arm.values()), default=0)

    png = args.root / "the_growth_curve.png"
    draw(data, png, n_homes)

    # the table view, which the contrast WARN on three palette slots obliges
    csv_path = args.root / "the_growth_curve.csv"
    with csv_path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["arm", "night", "n_homes", "mean_live_lines",
                         "mean_characters"])
        for arm in ARM_ORDER:
            if arm not in data:
                continue
            for night in sorted(data[arm]):
                got = data[arm][night]
                writer.writerow([arm, night, got["n_homes"],
                                 f"{got['n_lines']:.2f}", f"{got['n_characters']:.0f}"])
    print(f"written {png}")
    print(f"written {csv_path}  (the table view: identity is never colour alone)")
    for arm in ARM_ORDER:
        if arm not in data:
            continue
        nights = sorted(data[arm])
        first, last = data[arm][nights[0]], data[arm][nights[-1]]
        print(f"  {arm:22s} night {nights[0]:2d}: {first['n_lines']:5.1f} lines -> "
              f"night {nights[-1]:2d}: {last['n_lines']:5.1f} lines, "
              f"{last['n_characters']:6.0f} characters  ({last['n_homes']} homes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
