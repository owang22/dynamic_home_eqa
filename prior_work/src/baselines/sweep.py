"""Budget sweep with NO ambient sightings and NO initial tour.

The bank is exported with ``sightings_per_day = 0`` and without the t=0
tour, so agents start blind: the ONLY evidence ever available is what
their own paid senses return. Per-day accuracy then starts at the
uniform-fallback chance floor (~1/n_receptacles) and every point above it
is earned through sensing — the budget axis is the whole story.

Output layout (replaces the earlier sightings-x-budget summary):

  <out-dir>/banks/s00.jsonl        the no-sightings bank
  <out-dir>/sweep.csv              tidy: one row per
                                   (budget, belief, policy, day)
  <out-dir>/figs/<belief>__<policy>.png
                                   one figure per strategy: task accuracy
                                   (top panel) and full-state belief
                                   accuracy (bottom panel) over days,
                                   one line per budget level on a
                                   single-hue sequential ramp (budget is
                                   an ordered magnitude, not an identity)

Per-day task accuracy averages ~questions-per-day answers (noisy); per-day
belief accuracy averages questions x objects snapshots (smooth). Both are
plotted; read fine structure off the bottom panels.

Usage:
  python -m baselines.sweep \
      --timeline profiles/revamp_v1/claude-fable-5/hh1/timeline_seed0 \
      --spec profiles/revamp_v1/claude-fable-5/hh1/object_motions.yaml \
      --questions-per-day 90 --out-dir reports/baselines/sweep_hh1
"""

from __future__ import annotations

import argparse
import csv
import logging
import pathlib
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple

from baselines.export_bank import export
from baselines.harness import QuestionRecord
from baselines.healthcheck import UNLIMITED_BUDGET, run_cell

logger = logging.getLogger(__name__)

# 24/day is the headline bank's real budget. The low steps are where the
# learning arc is visible: full-contents senses are so informative (each
# returns every object in the receptacle, and OUT_OF_HOUSE aggregates all
# absent carried items) that 16/day assembles a home-base map within ~2
# days. Unlimited is omitted as a known flat reference — task accuracy is
# pinned at 1.0 by the search invariant and full-state accuracy sits near
# 0.9; the healthcheck panel documents both.
BUDGET_LEVELS: Tuple[Any, ...] = (0, 1, 4, 24)
# Beliefs match the healthcheck panel (frequency members carry the frozen
# 24 h count half-life). FixedSchedule is dropped from the sweep: its
# 6 h/4-stop rotation spends at most 4 senses/day, so every budget >= 4
# produced byte-identical redundant columns.
BELIEF_SPECS: Tuple[Dict[str, Any], ...] = (
    {"name": "last_observation"},
    {"name": "most_frequent", "half_life_h": 24},
    {"name": "timetable", "half_life_h": 24},
)
POLICY_SPECS: Tuple[Dict[str, Any], ...] = (
    {"name": "sequential_search"},
)

# Sequential single-hue ramp, light -> dark, for the ordered budget levels.
_RAMP = ("#b9d2f0", "#7fabe4", "#4489d9", "#1a4e8f")
_INK = "#33322e"
_GRID = "#dddbd2"


@dataclass(frozen=True)
class DayCell:
    """Accuracies of one strategy at one budget on one day."""

    budget: str
    belief: str
    policy: str
    day_index: int
    n_questions: int
    task_accuracy: float
    belief_accuracy: float


def _per_day(records: Sequence[QuestionRecord], budget: str, belief: str,
             policy: str) -> List[DayCell]:
    """Collapse a run's records into per-day task/belief accuracies."""
    by_day: Dict[int, List[QuestionRecord]] = defaultdict(list)
    for r in records:
        by_day[r.day_index].append(r)
    cells = []
    for day, rs in sorted(by_day.items()):
        hits = total = 0
        for r in rs:
            for _, _, ok in r.belief_state.values():
                hits += ok
                total += 1
        cells.append(DayCell(
            budget=budget, belief=belief, policy=policy, day_index=day,
            n_questions=len(rs),
            task_accuracy=sum(r.correct for r in rs) / len(rs),
            belief_accuracy=hits / total))
    return cells


def run_sweep(timeline: pathlib.Path, spec: pathlib.Path, seed: int,
              questions_per_day: int, out_dir: pathlib.Path) -> List[DayCell]:
    """Export the no-sightings bank and run every strategy at every budget."""
    bank = export(
        timeline, spec, out_dir / "banks" / "s00_notour.jsonl", seed=seed,
        sightings_per_day=0, questions_per_day=questions_per_day,
        first_question_day=3, budget_per_day=2, query_mode="uniform",
        initial_tour=False)
    cells: List[DayCell] = []
    for level in BUDGET_LEVELS:
        budget = UNLIMITED_BUDGET if level == "unlimited" else int(level)
        for belief_spec in BELIEF_SPECS:
            for policy_spec in POLICY_SPECS:
                records = run_cell(bank, belief_spec, policy_spec, seed, budget)
                cells += _per_day(records, str(level),
                                  str(belief_spec["name"]),
                                  str(policy_spec["name"]))
                logger.info("budget=%s %s+%s done", level,
                            belief_spec["name"], policy_spec["name"])
    return cells


def write_csv(cells: Sequence[DayCell], path: pathlib.Path) -> None:
    """Tidy CSV, one row per (budget, strategy, day)."""
    fields = ("budget", "belief", "policy", "day_index", "n_questions",
              "task_accuracy", "belief_accuracy")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for c in cells:
            writer.writerow([getattr(c, field) for field in fields])
    logger.info("wrote %s", path)


def plot_strategy(cells: Sequence[DayCell], belief: str, policy: str,
                  path: pathlib.Path) -> None:
    """One strategy's figure: task (top) and belief (bottom) accuracy over
    days, one line per budget level."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MaxNLocator

    fig, (ax_task, ax_belief) = plt.subplots(
        2, 1, figsize=(7.5, 6), sharex=True)
    for bi, level in enumerate(BUDGET_LEVELS):
        series = sorted((c for c in cells
                         if c.belief == belief and c.policy == policy
                         and c.budget == str(level)),
                        key=lambda c: c.day_index)
        days = [c.day_index for c in series]
        for ax, metric in ((ax_task, "task_accuracy"),
                           (ax_belief, "belief_accuracy")):
            ax.plot(days, [getattr(c, metric) for c in series],
                    color=_RAMP[bi], linewidth=2, marker="o", markersize=4)
    for ax, label in ((ax_task, "task accuracy (queried objects)"),
                      (ax_belief, "belief accuracy (all objects)")):
        ax.set_ylim(0, 1.02)
        ax.set_ylabel(label, fontsize=9, color=_INK)
        ax.yaxis.grid(True, color=_GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(colors=_INK, labelsize=9)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    ax_belief.set_xlabel("day", fontsize=10, color=_INK)
    ax_belief.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax_task.set_title(f"{belief} + {policy} — no sightings, no tour; "
                      f"questions from day 3",
                      fontsize=10, color=_INK, loc="left")
    handles = [Line2D([], [], color=_RAMP[i], linewidth=3,
                      label=f"budget {lv}/day")
               for i, lv in enumerate(BUDGET_LEVELS)]
    ax_task.legend(handles=handles, loc="lower left", fontsize=8,
                   frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    logger.info("wrote %s", path)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeline", type=pathlib.Path, required=True)
    parser.add_argument("--spec", type=pathlib.Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--questions-per-day", type=int, default=28)
    parser.add_argument("--out-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    (args.out_dir / "figs").mkdir(parents=True, exist_ok=True)
    cells = run_sweep(args.timeline, args.spec, args.seed,
                      args.questions_per_day, args.out_dir)
    write_csv(cells, args.out_dir / "sweep.csv")
    for belief_spec in BELIEF_SPECS:
        for policy_spec in POLICY_SPECS:
            belief = str(belief_spec["name"])
            policy = str(policy_spec["name"])
            plot_strategy(cells, belief, policy,
                          args.out_dir / "figs" / f"{belief}__{policy}.png")
    print(f"wrote {args.out_dir}/sweep.csv and "
          f"{len(BELIEF_SPECS) * len(POLICY_SPECS)} figures in "
          f"{args.out_dir}/figs/")


if __name__ == "__main__":
    main()
