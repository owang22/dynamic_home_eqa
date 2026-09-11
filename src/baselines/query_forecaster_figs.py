"""Figures for the query forecaster: predicted vs observed rates on
held-out days.

For each routine-driven bank the forecaster is fit on the first
``train_fraction`` of question days and evaluated on the rest. Writes:

* ``forecast_heatmaps.png`` — per household, predicted and observed
  query totals over the held-out days, object class x hour of day (the
  same layout as the query stream's heatmap).
* ``forecast_scatter.png`` — per household, predicted vs observed
  totals per (object, hour) cell on the held-out days, with the y = x
  line.

Usage::

    python -m baselines.query_forecaster_figs \
        --banks banks/baselines/fleet_routine/*_bank.jsonl \
        --out-dir reports/baselines/query_forecaster
"""

from __future__ import annotations

import argparse
import collections
import logging
import pathlib
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from baselines.bank import JsonlBank
from baselines.query_forecaster import QueryForecaster, day_type_of
from baselines.types import DAY_SECONDS, Episode

logger = logging.getLogger(__name__)

POINT_COLOR = "#3b6ec5"
TRAIN_FRACTION = 0.6


def _split_days(episode: Episode, train_fraction: float
                ) -> Tuple[List[int], List[int]]:
    days = [d for d, qs in enumerate(episode.questions_by_day) if qs]
    cut = max(1, int(len(days) * train_fraction))
    return days[:cut], days[cut:]


def _cells(episode: Episode, forecaster: QueryForecaster,
           held_out: List[int]) -> Dict[Tuple[str, int], List[float]]:
    """(object, hour) -> [predicted total, observed total] over the
    held-out days."""
    cells: Dict[Tuple[str, int], List[float]] = collections.defaultdict(
        lambda: [0.0, 0.0])
    for day in held_out:
        day_type = day_type_of(day)
        for hour in range(24):
            for obj in forecaster.objects:
                rate = forecaster.rate_at(obj, day_type, hour)
                if rate:
                    cells[(obj, hour)][0] += rate
        for q in episode.questions_by_day[day]:
            hour = (q.t_query % DAY_SECONDS) // 3600
            cells[(q.object_id, hour)][1] += 1.0
    return cells


def _class_grid(episode: Episode,
                cells: Dict[Tuple[str, int], List[float]], index: int,
                order: List[str]) -> "np.ndarray[Any, Any]":
    grid = np.zeros((len(order), 24))
    row = {cls: i for i, cls in enumerate(order)}
    for (obj, hour), pair in cells.items():
        grid[row[episode.object_classes[obj]], hour] += pair[index]
    return grid


def _heatmaps(per_bank: List[Tuple[Episode,
                                   Dict[Tuple[str, int], List[float]]]],
              out: pathlib.Path) -> None:
    fig, axes = plt.subplots(len(per_bank), 2,
                             figsize=(12.0, 6.5 * len(per_bank)),
                             squeeze=False)
    for row_axes, (episode, cells) in zip(axes, per_bank):
        totals: Dict[str, float] = collections.defaultdict(float)
        for (obj, _), pair in cells.items():
            totals[episode.object_classes[obj]] += pair[1]
        order = sorted(totals, key=lambda c: -totals[c])
        pred = _class_grid(episode, cells, 0, order)
        obs = _class_grid(episode, cells, 1, order)
        vmax = max(pred.max(), obs.max())
        for ax, grid, label in ((row_axes[0], pred, "predicted"),
                                (row_axes[1], obs, "observed")):
            im = ax.imshow(grid, aspect="auto", cmap="Blues", vmin=0.0,
                           vmax=vmax, interpolation="nearest")
            ax.set_yticks(range(len(order)))
            ax.set_yticklabels(order, fontsize=7)
            ax.set_xticks(range(0, 24, 3))
            ax.set_xlabel("hour of day")
            ax.set_title(f"{episode.household_id} — {label}", fontsize=10)
            fig.colorbar(im, ax=ax, shrink=0.6, label="queries (held-out)")
    fig.suptitle("Forecaster vs held-out days: class x hour totals")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def _scatter(per_bank: List[Tuple[Episode,
                                  Dict[Tuple[str, int], List[float]]]],
             out: pathlib.Path) -> None:
    fig, axes = plt.subplots(1, len(per_bank),
                             figsize=(4.2 * len(per_bank), 4.0),
                             squeeze=False)
    for ax, (episode, cells) in zip(axes[0], per_bank):
        pred = np.array([pair[0] for pair in cells.values()])
        obs = np.array([pair[1] for pair in cells.values()])
        top = float(max(pred.max(), obs.max())) * 1.05
        ax.plot([0, top], [0, top], color="#999999", linewidth=1)
        ax.scatter(pred, obs, s=10, alpha=0.35, color=POINT_COLOR,
                   edgecolors="none")
        r = float(np.corrcoef(pred, obs)[0, 1])
        ax.set_title(f"{episode.household_id} (r={r:.2f}, "
                     f"n={len(cells)} cells)", fontsize=10)
        ax.set_xlabel("predicted queries (held-out)")
    axes[0][0].set_ylabel("observed queries (held-out)")
    fig.suptitle("Forecaster: per (object, hour) totals on held-out days")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--banks", type=pathlib.Path, nargs="+",
                        required=True)
    parser.add_argument("--train-fraction", type=float,
                        default=TRAIN_FRACTION)
    parser.add_argument("--out-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    per_bank = []
    for path in args.banks:
        episode = next(JsonlBank(path=path).episodes())
        train, held_out = _split_days(episode, args.train_fraction)
        questions = [q for day in train
                     for q in episode.questions_by_day[day]]
        forecaster = QueryForecaster.fit_empirical(questions, train)
        per_bank.append((episode, _cells(episode, forecaster, held_out)))
        logger.info("%s: train days %s..%s, held-out %s..%s",
                    episode.household_id, train[0], train[-1],
                    held_out[0], held_out[-1])
    _heatmaps(per_bank, args.out_dir / "forecast_heatmaps.png")
    _scatter(per_bank, args.out_dir / "forecast_scatter.png")
    logger.info("figures -> %s", args.out_dir)


if __name__ == "__main__":
    main()
