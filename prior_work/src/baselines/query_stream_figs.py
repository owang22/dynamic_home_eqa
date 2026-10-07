"""Figures for the routine-driven query stream (one-shot, no agents).

Reads routine-driven banks plus their timelines and writes, per run:

* ``query_heatmap.png`` — object class x hour of day, query count, one
  panel per household.
* ``queries_per_day.png`` — per-day question counts split into routine
  and background origins (totals are fixed by construction; the split
  is the varying part).
* ``query_offsets.png`` — for selected activities, the distribution of
  query offsets relative to the triggering activity's start.

Usage::

    python -m baselines.query_stream_figs \
        --banks banks/baselines/fleet_routine/*_bank.jsonl \
        --out-dir reports/baselines/query_stream
"""

from __future__ import annotations

import argparse
import collections
import json
import logging
import pathlib
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from baselines.query_stream import activity_instances
from baselines.types import DAY_SECONDS

logger = logging.getLogger(__name__)

ROUTINE_COLOR = "#3b6ec5"
BACKGROUND_COLOR = "#c58a3b"
OFFSET_ACTIVITIES = ("work_away", "take_medication", "coffee")


def _load_bank(path: pathlib.Path
               ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    header: Dict[str, Any] = {}
    questions: List[Dict[str, Any]] = []
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            if row["kind"] == "episode_header":
                header = row
            elif row["kind"] == "question":
                questions.append(row)
    return header, questions


def _heatmap(banks: List[Tuple[Dict[str, Any], List[Dict[str, Any]]]],
             out: pathlib.Path) -> None:
    fig, axes = plt.subplots(1, len(banks),
                             figsize=(6.0 * len(banks), 7.0), squeeze=False)
    for ax, (header, questions) in zip(axes[0], banks):
        classes_of = header["object_classes"]
        counts: Dict[str, "np.ndarray[Any, Any]"] = (
            collections.defaultdict(lambda: np.zeros(24)))
        for q in questions:
            hour = (q["t_query"] % DAY_SECONDS) // 3600
            counts[classes_of[q["object_id"]]][hour] += 1
        order = sorted(counts, key=lambda c: -counts[c].sum())
        grid = np.array([counts[c] for c in order])
        im = ax.imshow(grid, aspect="auto", cmap="Blues",
                       interpolation="nearest")
        ax.set_yticks(range(len(order)))
        ax.set_yticklabels(order, fontsize=7)
        ax.set_xticks(range(0, 24, 3))
        ax.set_xlabel("hour of day")
        ax.set_title(str(header["household_id"]), fontsize=10)
        fig.colorbar(im, ax=ax, shrink=0.6, label="queries")
    fig.suptitle("Routine-driven queries: object class x hour of day")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def _per_day(banks: List[Tuple[Dict[str, Any], List[Dict[str, Any]]]],
             out: pathlib.Path) -> None:
    fig, axes = plt.subplots(1, len(banks),
                             figsize=(5.0 * len(banks), 3.2), squeeze=False)
    for ax, (header, questions) in zip(axes[0], banks):
        by_day: Dict[int, Dict[str, int]] = collections.defaultdict(
            lambda: {"routine": 0, "background": 0})
        for q in questions:
            kind = ("background" if q.get("origin") == "background"
                    else "routine")
            by_day[q["day_index"]][kind] += 1
        days = sorted(by_day)
        routine = [by_day[d]["routine"] for d in days]
        background = [by_day[d]["background"] for d in days]
        ax.bar(days, routine, color=ROUTINE_COLOR, label="routine",
               width=0.8)
        ax.bar(days, background, bottom=routine, color=BACKGROUND_COLOR,
               label="background", width=0.8)
        ax.set_xlabel("day")
        ax.set_ylabel("queries")
        ax.set_title(str(header["household_id"]), fontsize=10)
        if ax is axes[0][0]:
            ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Queries per day by origin (total fixed per day)")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def _offsets(header: Dict[str, Any], questions: List[Dict[str, Any]],
             timeline: pathlib.Path, out: pathlib.Path) -> None:
    """Offset of each activity-tagged query from the start of the nearest
    same-day instance of its activity (negative = before the start)."""
    instances = activity_instances(timeline)
    starts: Dict[Tuple[str, int], List[int]] = collections.defaultdict(list)
    for inst in instances:
        base = inst.activity.split("__", 1)[0]
        starts[(base, inst.t0 // DAY_SECONDS)].append(inst.t0)
    fig, axes = plt.subplots(1, len(OFFSET_ACTIVITIES),
                             figsize=(4.0 * len(OFFSET_ACTIVITIES), 3.0),
                             squeeze=False)
    for ax, activity in zip(axes[0], OFFSET_ACTIVITIES):
        offsets = []
        for q in questions:
            if q.get("origin") != f"activity:{activity}":
                continue
            day_starts = starts.get((activity, q["day_index"]), [])
            if not day_starts:
                continue
            offsets.append(min((q["t_query"] - t0 for t0 in day_starts),
                               key=abs) / 60.0)
        ax.hist(offsets, bins=30, color=ROUTINE_COLOR)
        ax.axvline(0.0, color="#555555", linewidth=1)
        ax.set_title(f"{activity} (n={len(offsets)})", fontsize=10)
        ax.set_xlabel("query offset from activity start (min)")
    axes[0][0].set_ylabel("queries")
    fig.suptitle(f"Query offsets, {header['household_id']} "
                 f"(negative = before the start)")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--banks", type=pathlib.Path, nargs="+",
                        required=True)
    parser.add_argument("--timeline-root", type=pathlib.Path,
                        default=pathlib.Path(
                            "profiles/households/generated/gpt-5.6-terra"))
    parser.add_argument("--out-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    banks = [_load_bank(p) for p in args.banks]
    _heatmap(banks, args.out_dir / "query_heatmap.png")
    _per_day(banks, args.out_dir / "queries_per_day.png")
    header, questions = banks[0]
    _offsets(header, questions,
             args.timeline_root / str(header["household_id"])
             / "timeline_seed0",
             args.out_dir / "query_offsets.png")
    logger.info("figures -> %s", args.out_dir)


if __name__ == "__main__":
    main()
