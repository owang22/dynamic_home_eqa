"""Headroom check: does sensing beyond the current query help at all?

Runs :class:`~baselines.policies.oracle_lookahead.OracleLookaheadSense`
(the policy handed the true query schedule) against the best myopic
policy from the room-change cost study (``VoIThresholdSense`` at
``lambda = 0.05``) — same belief (``periodic_persistence``), same banks
(routine-driven), one budget (the banks' own), two room-change costs.
Writes per-question rows, a summary with paired bootstrap confidence
intervals (clustered by day), and the three figures of the brief:

* ``accuracy_by_day.png`` — oracle vs myopic accuracy per day.
* ``gap_vs_c.png`` — the oracle-minus-myopic gap against ``c`` with the
  95% CI per household.
* ``oracle_budget_split.png`` — the oracle's senses split by whether
  the CURRENT question alone justified them, next to the myopic
  policy's sense rate: the extra spend is the lookahead behaviour.

Usage::

    python -m baselines.oracle_lookahead_study \
        --banks banks/baselines/fleet_routine/*_bank.jsonl \
        --out-dir results/oracle_lookahead
"""

from __future__ import annotations

import argparse
import collections
import json
import logging
import pathlib
import random
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
LAMBDA = 0.05
HORIZON_DAYS = 2.0
COSTS = (0.0, 2.0)
ORACLE_COLOR = "#3b6ec5"
MYOPIC_COLOR = "#c58a3b"
BOOTSTRAP = 2000


def _run_one(episode: Episode, c: float, oracle: bool,
             seed: int) -> List[Dict[str, Any]]:
    tag = "oracle" if oracle else "myopic"
    rng_b = _derived_rng(seed, "lookahead", tag, str(c),
                         episode.episode_id)
    rng_p = _derived_rng(seed, "lookahead_policy", tag, str(c),
                         episode.episode_id)
    belief = build_belief(BELIEF_SPEC, rng_b)
    if oracle:
        schedule = [q for day in episode.questions_by_day for q in day]
        policy = OracleLookaheadSense(
            rng_p, lam=LAMBDA, schedule=schedule,
            predict_fn=belief.predict_readonly, horizon_days=HORIZON_DAYS)
    else:
        policy = VoIThresholdSense(rng_p, lam=LAMBDA)
    agent = Agent(belief=belief, policy=policy)
    rows: List[Dict[str, Any]] = []
    for record in run_episode(agent, episode, room_change_cost=c):
        row: Dict[str, Any] = {
            "household": episode.household_id, "c": c, "policy": tag,
            "day": record.day_index, "question_id": record.question_id,
            "correct": int(record.correct),
            "n_senses": record.n_senses,
            "budget_spent": record.budget_spent,
            "forced": int(record.forced_answer)}
        if oracle:
            assert isinstance(policy, OracleLookaheadSense)
            row.update(policy.last_question_stats)
        rows.append(row)
    return rows


def _paired_gap(oracle_rows: List[Dict[str, Any]],
                myopic_rows: List[Dict[str, Any]],
                rng: random.Random) -> Dict[str, float]:
    """Mean oracle-minus-myopic accuracy gap with a 95% bootstrap CI,
    resampling DAYS (the questions of a day are one cluster)."""
    myopic = {r["question_id"]: r["correct"] for r in myopic_rows}
    diffs_by_day: Dict[int, List[int]] = collections.defaultdict(list)
    for r in oracle_rows:
        diffs_by_day[r["day"]].append(r["correct"] - myopic[r["question_id"]])
    days = sorted(diffs_by_day)
    gap = float(np.mean([d for day in days for d in diffs_by_day[day]]))
    means = []
    for _ in range(BOOTSTRAP):
        sample = [rng.choice(days) for _ in days]
        pooled = [d for day in sample for d in diffs_by_day[day]]
        means.append(float(np.mean(pooled)))
    lo, hi = np.percentile(means, [2.5, 97.5])
    return {"gap": gap, "ci_lo": float(lo), "ci_hi": float(hi)}


def _fig_accuracy_by_day(rows: List[Dict[str, Any]],
                         out: pathlib.Path) -> None:
    households = sorted({r["household"] for r in rows})
    fig, axes = plt.subplots(len(COSTS), len(households),
                             figsize=(4.6 * len(households),
                                      3.0 * len(COSTS)), squeeze=False)
    for i, c in enumerate(COSTS):
        for j, hh in enumerate(households):
            ax = axes[i][j]
            for tag, color in (("oracle", ORACLE_COLOR),
                               ("myopic", MYOPIC_COLOR)):
                by_day: Dict[int, List[int]] = collections.defaultdict(list)
                for r in rows:
                    if (r["household"], r["c"], r["policy"]) == (hh, c, tag):
                        by_day[r["day"]].append(r["correct"])
                days = sorted(by_day)
                ax.plot(days, [np.mean(by_day[d]) for d in days],
                        color=color, linewidth=2, label=tag)
            ax.set_title(f"{hh}, c={c:g}", fontsize=10)
            ax.set_ylim(0.4, 1.0)
            if i == len(COSTS) - 1:
                ax.set_xlabel("day")
            if j == 0:
                ax.set_ylabel("accuracy")
            if i == 0 and j == 0:
                ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Oracle lookahead vs best myopic (periodic_persistence, "
                 f"lambda={LAMBDA:g})")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def _fig_gap_vs_c(summary: Dict[str, Dict[str, float]],
                  out: pathlib.Path) -> None:
    households = sorted({key.split("@")[0] for key in summary})
    fig, ax = plt.subplots(figsize=(5.0, 3.6))
    for k, hh in enumerate(households):
        xs, gaps, los, his = [], [], [], []
        for c in COSTS:
            cell = summary[f"{hh}@{c:g}"]
            xs.append(c + (k - 1) * 0.06)
            gaps.append(cell["gap"])
            los.append(cell["gap"] - cell["ci_lo"])
            his.append(cell["ci_hi"] - cell["gap"])
        ax.errorbar(xs, gaps, yerr=[los, his], fmt="o", capsize=3,
                    label=hh, markersize=5)
    ax.axhline(0.0, color="#999999", linewidth=1)
    ax.set_xticks(list(COSTS))
    ax.set_xlabel("room-change cost c")
    ax.set_ylabel("accuracy gap (oracle - myopic)")
    ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Lookahead headroom against c (95% day-bootstrap CI)")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def _fig_budget_split(rows: List[Dict[str, Any]],
                      out: pathlib.Path) -> None:
    cells: List[Tuple[str, float]] = sorted(
        {(r["household"], r["c"]) for r in rows})
    labels, for_current, future_only, myopic_rate = [], [], [], []
    for hh, c in cells:
        oracle = [r for r in rows
                  if (r["household"], r["c"], r["policy"])
                  == (hh, c, "oracle")]
        myopic = [r for r in rows
                  if (r["household"], r["c"], r["policy"])
                  == (hh, c, "myopic")]
        n_days = len({r["day"] for r in oracle})
        labels.append(f"{hh}\nc={c:g}")
        for_current.append(sum(r["senses_for_current"] for r in oracle)
                           / n_days)
        future_only.append(sum(r["senses_future_only"] for r in oracle)
                           / n_days)
        myopic_rate.append(sum(r["n_senses"] for r in myopic) / n_days)
    xs = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(1.4 * len(labels) + 2, 3.8))
    ax.bar(xs, for_current, color=ORACLE_COLOR,
           label="oracle: current question justified")
    ax.bar(xs, future_only, bottom=for_current, color="#9dbbe8",
           label="oracle: future questions only")
    ax.scatter(xs, myopic_rate, color=MYOPIC_COLOR, zorder=3, s=40,
               label="myopic senses/day")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("senses per day")
    ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Where the oracle spends budget the myopic policy does not")
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
    all_rows: List[Dict[str, Any]] = []
    summary: Dict[str, Dict[str, float]] = {}
    for path in args.banks:
        episode = next(JsonlBank(path=path).episodes())
        for c in COSTS:
            per_policy: Dict[str, List[Dict[str, Any]]] = {}
            for oracle in (False, True):
                rows = _run_one(episode, c, oracle, args.seed)
                per_policy["oracle" if oracle else "myopic"] = rows
                all_rows.extend(rows)
                acc = float(np.mean([r["correct"] for r in rows]))
                logger.info("%s c=%g %s: acc=%.3f senses/day=%.1f",
                            episode.household_id, c,
                            "oracle" if oracle else "myopic", acc,
                            sum(r["n_senses"] for r in rows)
                            / episode.n_days)
            key = f"{episode.household_id}@{c:g}"
            summary[key] = _paired_gap(per_policy["oracle"],
                                       per_policy["myopic"],
                                       random.Random(args.seed))
            logger.info("%s: gap=%+.3f [%.3f, %.3f]", key,
                        summary[key]["gap"], summary[key]["ci_lo"],
                        summary[key]["ci_hi"])
    with open(args.out_dir / "questions.jsonl", "w") as f:
        for row in all_rows:
            f.write(json.dumps(row) + "\n")
    with open(args.out_dir / "summary.json", "w") as f:
        json.dump({"belief": BELIEF_SPEC["name"], "lambda": LAMBDA,
                   "horizon_days": HORIZON_DAYS, "costs": list(COSTS),
                   "gaps": summary}, f, indent=2)
    _fig_accuracy_by_day(all_rows, args.out_dir / "accuracy_by_day.png")
    _fig_gap_vs_c(summary, args.out_dir / "gap_vs_c.png")
    _fig_budget_split(all_rows, args.out_dir / "oracle_budget_split.png")
    logger.info("results -> %s", args.out_dir)


if __name__ == "__main__":
    main()
