"""Spend-matched headroom check: accuracy-vs-spend frontiers.

A single ``lambda`` cannot compare the myopic policy with the lookahead
one — their value scales differ by ~100x (see
:mod:`baselines.policies.oracle_lookahead`), so any fixed threshold puts
the two at different spend levels and the accuracy difference then
measures the spend, not the lookahead. This study instead sweeps
``lambda`` per policy and reports accuracy against REALIZED senses per
day, so the two frontiers are compared at matched spend.

The headroom question becomes: is the oracle's frontier above the
myopic's anywhere? If not, sensing beyond the current query does not
help on these banks.

Usage::

    python -m baselines.oracle_lookahead_frontier \
        --banks banks/baselines/fleet_routine/*_bank.jsonl \
        --out-dir results/oracle_lookahead_frontier
"""

from __future__ import annotations

import argparse
import json
import logging
import pathlib
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from baselines.agent import Agent
from baselines.bank import JsonlBank
from baselines.cli import _derived_rng, build_belief
from baselines.harness import run_episode
from baselines.policies.oracle_lookahead import OracleLookaheadSense
from baselines.policies.voi_sense import VoIThresholdSense
from baselines.types import Episode

logger = logging.getLogger(__name__)

BELIEF_SPEC = {"name": "periodic_persistence"}
HORIZON_DAYS = 2.0
COSTS = (0.0, 2.0)
MYOPIC_LAMBDAS = (0.0005, 0.002, 0.01, 0.05)
ORACLE_LAMBDAS = (0.0002, 0.001, 0.004, 0.01)
ORACLE_COLOR = "#3b6ec5"
MYOPIC_COLOR = "#c58a3b"


def _run(episode: Episode, c: float, oracle: bool, lam: float,
         seed: int) -> Dict[str, Any]:
    tag = "oracle" if oracle else "myopic"
    belief = build_belief(
        BELIEF_SPEC, _derived_rng(seed, "frontier", tag, str(lam), str(c),
                                  episode.episode_id))
    rng_p = _derived_rng(seed, "frontier_policy", tag, str(lam), str(c),
                         episode.episode_id)
    policy: VoIThresholdSense
    if oracle:
        schedule = [q for day in episode.questions_by_day for q in day]
        policy = OracleLookaheadSense(
            rng_p, lam=lam, schedule=schedule,
            predict_fn=belief.predict_readonly, horizon_days=HORIZON_DAYS)
    else:
        policy = VoIThresholdSense(rng_p, lam=lam)
    correct = n = n_senses = 0
    spend = 0.0
    for record in run_episode(Agent(belief=belief, policy=policy), episode,
                              room_change_cost=c):
        correct += int(record.correct)
        n += 1
        n_senses += record.n_senses
        spend += record.budget_spent
    return {"household": episode.household_id, "c": c, "policy": tag,
            "lam": lam, "accuracy": correct / n,
            "senses_per_day": n_senses / episode.n_days,
            "spend_per_day": spend / episode.n_days, "n_questions": n}


def _figure(rows: List[Dict[str, Any]], out: pathlib.Path) -> None:
    households = sorted({r["household"] for r in rows})
    fig, axes = plt.subplots(len(COSTS), len(households),
                             figsize=(4.4 * len(households),
                                      3.4 * len(COSTS)), squeeze=False)
    for i, c in enumerate(COSTS):
        for j, hh in enumerate(households):
            ax = axes[i][j]
            for tag, color in (("myopic", MYOPIC_COLOR),
                               ("oracle", ORACLE_COLOR)):
                pts = sorted(
                    ((r["senses_per_day"], r["accuracy"]) for r in rows
                     if (r["household"], r["c"], r["policy"]) == (hh, c, tag)))
                if pts:
                    ax.plot([p[0] for p in pts], [p[1] for p in pts],
                            marker="o", color=color, linewidth=2,
                            markersize=5, label=tag)
            ax.set_title(f"{hh}, c={c:g}", fontsize=10)
            if i == len(COSTS) - 1:
                ax.set_xlabel("realized senses per day")
            if j == 0:
                ax.set_ylabel("accuracy")
            if i == 0 and j == 0:
                ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Spend-matched headroom: accuracy vs realized spend "
                 "(periodic_persistence)")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--banks", type=pathlib.Path, nargs="+",
                        required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []
    for path in args.banks:
        episode = next(JsonlBank(path=path).episodes())
        for c in COSTS:
            for oracle, lambdas in ((False, MYOPIC_LAMBDAS),
                                    (True, ORACLE_LAMBDAS)):
                for lam in lambdas:
                    row = _run(episode, c, oracle, lam, args.seed)
                    rows.append(row)
                    logger.info(
                        "%s c=%g %s lam=%g: acc=%.3f senses/day=%.1f",
                        row["household"], c, row["policy"], lam,
                        row["accuracy"], row["senses_per_day"])
    with open(args.out_dir / "frontier.json", "w") as f:
        json.dump(rows, f, indent=2)
    _figure(rows, args.out_dir / "frontier.png")
    logger.info("results -> %s", args.out_dir)


if __name__ == "__main__":
    main()
