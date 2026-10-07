"""Diagnostic figure for a bank's intrinsic dynamics.

One PNG, four panels, all computed from ground truth + question placement
(no agents), matching the numbers `cli bankstats` prints:

* per-object dwell-weighted modal share vs the stationarity gate — which
  objects are parked and which actually move;
* the distribution of contiguous away-from-home displacement stints —
  short excursions vs persistent displacement (the lever the generator
  work targets);
* true moves per day with weekends marked (day 0 is Monday by the
  profile convention) — quiet-Sunday structure;
* per-day modal share at query times — how often the examiner samples
  the world in its parked state, the direct driver of day-to-day
  accuracy wiggles.

Times are seconds since episode start; durations are binned in hours.
"""

from __future__ import annotations

import dataclasses
import logging
import pathlib
from typing import Any, Dict, List, Tuple

from baselines.bankstats import BankStats, _object_dwell
from baselines.bank import JsonlBank

logger = logging.getLogger(__name__)

# Single accent hue for magnitudes (identity sits on the axes), plus the
# recessive ink/grid tones shared with the package's other figures.
_HUE = "#2a78d6"
_HUE_SOFT = "#b9d2f0"
_INK = "#33322e"
_MUTED = "#6f6d64"
_GRID = "#dddbd2"
_BAND = "#f0efe9"          # weekend background band (position, not color-alone)

_STINT_BINS_H: Tuple[Tuple[str, float, float], ...] = (
    ("<1h", 0.0, 1.0), ("1-3h", 1.0, 3.0), ("3-9h", 3.0, 9.0),
    ("9-24h", 9.0, 24.0), ("1-3d", 24.0, 72.0), (">3d", 72.0, float("inf")))

_WEEKDAY_INITIALS = "MTWTFSS"


@dataclasses.dataclass(frozen=True)
class DailySeries:
    """Per-day views used only by the figure (gate surface unchanged)."""

    moves_by_day: Dict[int, int]
    query_modal_by_day: Dict[int, float]
    stint_hours: Tuple[float, ...]


def compute_daily_series(bank: JsonlBank) -> DailySeries:
    """Per-day move counts, query-time modal shares, and stint lengths."""
    moves: Dict[int, int] = {}
    hits: Dict[int, List[bool]] = {}
    stints: List[float] = []
    for ep in bank.episodes():
        day_s = 86_400
        dwell = {obj: _object_dwell(ep, obj) for obj in ep.trajectories}
        for obj, traj in ep.trajectories.items():
            stints += [s / 3600 for s in dwell[obj].displacement_intervals_s]
            for i in range(1, len(traj)):
                if traj[i][1] != traj[i - 1][1]:
                    d = traj[i][0] // day_s
                    moves[d] = moves.get(d, 0) + 1
        for day in ep.questions_by_day:
            for q in day:
                truth = ep.true_location(q.object_id, q.t_query)
                hits.setdefault(q.day_index, []).append(
                    truth == dwell[q.object_id].modal_receptacle)
    return DailySeries(
        moves_by_day=moves,
        query_modal_by_day={d: sum(h) / len(h) for d, h in hits.items()},
        stint_hours=tuple(sorted(stints)))


def write_dynamics_figure(bank: JsonlBank, stats: BankStats,
                          max_modal_share: float,
                          out_path: pathlib.Path) -> None:
    """Render the four-panel dynamics diagnostic to ``out_path``."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    series = compute_daily_series(bank)
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    _panel_modal_bars(axes[0][0], stats, max_modal_share)
    _panel_stints(axes[0][1], series)
    _panel_moves(axes[1][0], series, stats)
    _panel_query_modal(axes[1][1], series, stats)
    fig.suptitle(
        f"{bank.path.name} — dwell-weighted modal share "
        f"{stats.modal_share_time:.3f} (gate ≤ {max_modal_share:.2f}), "
        f"{stats.moves_per_day:.1f} moves/day",
        x=0.02, ha="left", fontsize=11, color=_INK)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    logger.info("wrote %s", out_path)


def _style(ax: Any) -> None:
    ax.tick_params(colors=_INK, labelsize=8)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def _panel_modal_bars(ax: Any, stats: BankStats,
                      max_modal_share: float) -> None:
    """Per-object modal share, sorted; gate and mean as reference lines."""
    items = sorted(stats.per_object_modal_share.items(), key=lambda kv: kv[1])
    ax.barh(range(len(items)), [v for _, v in items], color=_HUE, height=0.62)
    ax.set_yticks(range(len(items)), [k for k, _ in items], fontsize=7)
    ax.axvline(max_modal_share, color=_INK, linestyle="--", linewidth=1)
    ax.text(max_modal_share, len(items) - 0.2, f" gate ≤ {max_modal_share:.2f}",
            fontsize=8, color=_INK, va="top")
    ax.axvline(stats.modal_share_time, color=_MUTED, linestyle=":",
               linewidth=1.2)
    ax.text(stats.modal_share_time, -0.45,
            f" mean {stats.modal_share_time:.2f}", fontsize=8, color=_MUTED)
    ax.set_xlim(0, 1.02)
    ax.set_xlabel("share of time at home base", fontsize=9, color=_INK)
    ax.set_title("Who is parked? (dwell-weighted modal share per object)",
                 fontsize=9.5, color=_INK, loc="left")
    ax.xaxis.grid(True, color=_GRID, linewidth=0.8)
    _style(ax)


def _panel_stints(ax: Any, series: DailySeries) -> None:
    """Histogram of contiguous away-from-home stint durations."""
    counts = [sum(1 for h in series.stint_hours if lo <= h < hi)
              for _, lo, hi in _STINT_BINS_H]
    labels = [name for name, _, _ in _STINT_BINS_H]
    ax.bar(range(len(counts)), counts, color=_HUE, width=0.62)
    ax.set_xticks(range(len(counts)), labels)
    for i, c in enumerate(counts):
        if c:
            ax.text(i, c, f" {c}", ha="center", va="bottom", fontsize=8,
                    color=_MUTED)
    ax.set_xlabel("displacement stint length", fontsize=9, color=_INK)
    ax.set_ylabel("stints", fontsize=9, color=_INK)
    ax.set_title("How long do objects stay displaced?",
                 fontsize=9.5, color=_INK, loc="left")
    ax.yaxis.grid(True, color=_GRID, linewidth=0.8)
    _style(ax)


def _day_ticks(ax: Any, days: List[int]) -> None:
    ax.set_xticks(days,
                  [f"{d}\n{_WEEKDAY_INITIALS[d % 7]}" for d in days],
                  fontsize=7)
    for d in days:                      # weekend band: Sat + Sun columns
        if d % 7 in (5, 6):
            ax.axvspan(d - 0.5, d + 0.5, color=_BAND, zorder=0)


def _panel_moves(ax: Any, series: DailySeries, stats: BankStats) -> None:
    """True moves per day; weekends carry a background band."""
    days = list(range(stats.n_days))
    _day_ticks(ax, days)
    ax.bar(days, [series.moves_by_day.get(d, 0) for d in days],
           color=_HUE, width=0.62, zorder=2)
    ax.set_xlabel("day (weekends shaded)", fontsize=9, color=_INK)
    ax.set_ylabel("true moves", fontsize=9, color=_INK)
    ax.set_title("How much does the world move each day?",
                 fontsize=9.5, color=_INK, loc="left")
    ax.yaxis.grid(True, color=_GRID, linewidth=0.8)
    _style(ax)


def _panel_query_modal(ax: Any, series: DailySeries,
                       stats: BankStats) -> None:
    """Per-day modal share at query times (the examiner's sampling)."""
    days = sorted(series.query_modal_by_day)
    _day_ticks(ax, list(range(stats.n_days)))
    ax.plot(days, [series.query_modal_by_day[d] for d in days],
            color=_HUE, linewidth=2, marker="o", markersize=4.5, zorder=2)
    mean = stats.modal_share_questions
    ax.axhline(mean, color=_MUTED, linestyle=":", linewidth=1.2)
    ax.text(stats.n_days - 0.6, mean - 0.03, f"mean {mean:.2f}", fontsize=8,
            color=_MUTED, ha="right", va="top")
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("day (weekends shaded)", fontsize=9, color=_INK)
    ax.set_ylabel("share of questions with home-base answer",
                  fontsize=9, color=_INK)
    ax.set_title("How often does the examiner catch objects at home?",
                 fontsize=9.5, color=_INK, loc="left")
    ax.yaxis.grid(True, color=_GRID, linewidth=0.8)
    _style(ax)
