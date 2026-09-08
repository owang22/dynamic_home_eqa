"""Sweep conformal-triggered sensing over miscoverage levels and age binning.

One run = one bank (or several bank files; each file may hold several
episodes) x a set of belief models. The households are split at
household level into calibration and test (``--split-seed``,
``--calib-frac``; a household is never on both sides). Then, per belief:

1. ONE passive walk of every episode with a never-sensing agent yields
   the calibration pairs (nonconformity ``1 - p(truth)`` + belief age),
   tagged with household so the split is applied afterwards, and the
   NeverSense baseline records for free.
2. For every alpha, a global quantile and an age-binned quantile table
   are fitted on the calibration households' pairs.
3. On the test households, every conformal policy (alpha x {global,
   age_binned}) and the two reference policies (NeverSense from step 1,
   SequentialSearch) are replayed by the harness.

Outputs under ``--out``:

  sweep_results.csv       one row per (belief, policy): task accuracy,
                          full-state belief accuracy, mean senses per
                          question and per day, forced-answer rate, on
                          the TEST households
  coverage_by_age.csv     empirical coverage of the prediction set on the
                          test households per belief x alpha x mode x age
                          bin, with the quantile used and the target
  calibration.json        the fitted tables, the split, the bank hashes
  questions/<belief>__<policy>.jsonl.gz
                          every test-household question record (the
                          harness's own JSON form), one file per
                          (belief, policy, alpha)
  coverage_by_age.png     coverage bars, global vs age-binned, one panel
                          per belief x alpha, target line at 1 - alpha
  accuracy_vs_budget.png  task accuracy against mean senses per question,
                          one point per (policy, alpha), references marked
  summary.md, provenance.json

Usage:
  PYTHONPATH=src python -m baselines.conformal.sweep --demo --out /tmp/d
  PYTHONPATH=src python -m baselines.conformal.sweep \\
      --bank banks/baselines/fleet/*hh_0??_bank.jsonl \\
      --out results/conformal_sweep_v1

Every generator is derived from ``--seed`` through the same recipe the
grid runner uses, so two runs with identical inputs write identical csvs.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import dataclasses
import datetime
import gzip
import json
import logging
import math
import pathlib
import shutil
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.agent import Agent
from baselines.bank import JsonlBank, write_gate_pass_bank
from baselines.cli import _derived_rng, build_agent, git_state
from baselines.conformal.calibration import (DEFAULT_AGE_EDGES_H,
                                             DEFAULT_ALPHAS, MIN_BIN_N,
                                             CalibrationPair, QhatTable,
                                             age_bin_labels, collect_pairs,
                                             coverage_by_age,
                                             fit_age_binned_qhat,
                                             fit_global_qhat,
                                             household_split)
from baselines.harness import QuestionRecord, run_episode
from baselines.healthcheck import BELIEF_PANEL
from baselines.policies.conformal_sense import (ConformalSense,
                                                belief_age_fn)
from baselines.registry import build_registered_belief
from baselines.types import Episode

logger = logging.getLogger(__name__)

DEFAULT_BELIEFS: Tuple[str, ...] = (
    "last_observation", "most_frequent", "timetable",
    "periodic_persistence", "hierarchy_backoff")
"""The frozen panel plus the two bake-off promotions."""

BELIEF_SPECS: Dict[str, Dict[str, Any]] = {
    **{str(spec["name"]): dict(spec) for spec in BELIEF_PANEL},
    "periodic_persistence": {"name": "periodic_persistence"},
    "hierarchy_backoff": {"name": "hierarchy_backoff"},
    "smoothed_recency": {"name": "smoothed_recency"},
    "markov1": {"name": "markov1"},
    "daytype_mixture": {"name": "daytype_mixture"},
}
"""Belief specs by config name: panel members at their frozen settings,
candidates at their registry defaults."""

NEVER_SENSE = "NeverSense"
SEQUENTIAL_SEARCH = "SequentialSearch"
MODES = ("global", "age_binned")

# Plot styling: the package's ink/grid tokens and the validated palette's
# first two categorical slots (identity of the two calibration modes).
_INK = "#33322e"
_MUTED = "#6f6d64"
_GRID = "#dddbd2"
_MODE_HUES = {"global": "#2a78d6", "age_binned": "#eb6834"}
_ALPHA_RAMP = ("#9ec2ee", "#5f9be2", "#2a78d6", "#1a4f93")   # blue, light->dark


# ------------------------------------------------------------- task units

@dataclass(frozen=True)
class PolicySpec:
    """One policy to replay on the test households."""

    kind: str                     # "sequential_search" | "conformal"
    alpha: Optional[float] = None
    binned: bool = False

    @property
    def mode(self) -> str:
        if self.kind == "sequential_search":
            return SEQUENTIAL_SEARCH
        return "age_binned" if self.binned else "global"

    @property
    def slug(self) -> str:
        if self.kind == "sequential_search":
            return "sequential_search"
        return f"conformal_{self.mode}_alpha{self.alpha:g}"


@dataclass(frozen=True)
class RecordSummary:
    """The per-question scalars the aggregates need (records themselves
    go to the JSONL dump, not back through the process pool)."""

    household_id: str
    day_index: int
    correct: bool
    belief_accuracy: float
    budget_spent: int
    forced: bool


def _summaries(records: Sequence[QuestionRecord]) -> Tuple[RecordSummary, ...]:
    return tuple(RecordSummary(r.household_id, r.day_index, r.correct,
                               r.belief_accuracy, r.budget_spent,
                               r.forced_answer) for r in records)


def _load_episode(bank_path: str, episode_id: str,
                  budget: Optional[int] = None) -> Episode:
    """One episode by id; ``budget`` overrides its per-day budget (the
    episode is rebuilt with nothing else changed, as the healthcheck's
    unlimited-budget arm does), so a sweep can isolate the budget cap."""
    for episode in JsonlBank(path=pathlib.Path(bank_path)).episodes():
        if episode.episode_id == episode_id:
            if budget is not None:
                episode = dataclasses.replace(episode, budget_per_day=budget)
            return episode
    raise KeyError(f"{episode_id} not in {bank_path}")


def _write_part(records: Sequence[QuestionRecord], path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as fh:
        for record in records:
            fh.write(json.dumps(record.to_json_dict()) + "\n")


def passive_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Worker: the single passive walk of one episode for one belief."""
    episode = _load_episode(task["bank_path"], task["episode_id"],
                            task.get("budget"))
    agent = build_agent(task["belief_spec"], {"name": "never_sense"},
                        task["seed"], episode.episode_id)
    passive = collect_pairs(agent, episode, belief_age_fn(agent.belief))
    _write_part(passive.records, pathlib.Path(task["part_path"]))
    return {"belief_key": str(task["belief_spec"]["name"]),
            "belief": agent.belief.name, "episode_id": episode.episode_id,
            "household_id": episode.household_id, "pairs": passive.pairs,
            "summaries": _summaries(passive.records),
            "budget_per_day": episode.budget_per_day}


def policy_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Worker: one (belief, policy) replay of one test episode."""
    episode = _load_episode(task["bank_path"], task["episode_id"],
                            task.get("budget"))
    spec: PolicySpec = task["policy"]
    belief_spec = task["belief_spec"]
    seed = task["seed"]
    if spec.kind == "sequential_search":
        agent = build_agent(belief_spec, {"name": "sequential_search"},
                            seed, episode.episode_id)
    else:
        table: QhatTable = task["table"]
        belief_name = str(belief_spec["name"])
        policy_rng = _derived_rng(seed, "policy", belief_name, spec.slug,
                                  episode.episode_id)
        belief_rng = _derived_rng(seed, belief_name, spec.slug,
                                  episode.episode_id)
        belief = build_registered_belief(dict(belief_spec), belief_rng)
        policy = ConformalSense(policy_rng, table, belief_age_fn(belief),
                                binned=spec.binned)
        agent = Agent(belief=belief, policy=policy)
    records = list(run_episode(agent, episode))
    _write_part(records, pathlib.Path(task["part_path"]))
    return {"belief": agent.belief.name, "policy": agent.policy.name,
            "episode_id": episode.episode_id, "summaries": _summaries(records)}


# --------------------------------------------------------------- aggregate

def aggregate(summaries: Sequence[RecordSummary], budget_per_day: int
              ) -> Dict[str, Any]:
    n = len(summaries)
    if n == 0:
        raise ValueError("aggregate: no questions")
    days = {(s.household_id, s.day_index) for s in summaries}
    spent = sum(s.budget_spent for s in summaries)
    return {
        "n_households": len({s.household_id for s in summaries}),
        "n_questions": n,
        "task_accuracy": round(sum(s.correct for s in summaries) / n, 6),
        "belief_accuracy": round(
            sum(s.belief_accuracy for s in summaries) / n, 6),
        "mean_budget": round(spent / n, 6),
        "mean_budget_per_day": round(spent / len(days), 6),
        "forced_answer_rate": round(sum(s.forced for s in summaries) / n, 6),
        "budget_per_day": budget_per_day,
    }


def _short(belief_name: str) -> str:
    """Belief display name without its parameter suffix, for axis labels."""
    return belief_name.split("(", 1)[0]


def wilson_interval(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson score interval for k successes in n trials."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


# ------------------------------------------------------------------- plots

def plot_coverage_by_age(rows: Sequence[Dict[str, Any]], beliefs: Sequence[str],
                         alphas: Sequence[float], labels: Sequence[str],
                         path: pathlib.Path, min_n: int = MIN_BIN_N,
                         plot_alpha: Optional[float] = None) -> None:
    """One panel per belief, for ONE alpha (the largest by default; every
    alpha is in the csv): how often the true receptacle was inside the
    prediction set, per belief-age bin, with one global threshold versus
    one threshold per age bin. Dashed line = the promised rate 1 - alpha.
    Bin sizes sit on the ticks; bins thinner than ``min_n`` are skipped."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    alpha = max(alphas) if plot_alpha is None else plot_alpha
    n = len(beliefs)
    fig, axes = plt.subplots(1, n, sharey=True, figsize=(3.0 * n + 0.8, 3.6),
                             squeeze=False)
    xs = list(range(len(labels)))
    for idx, belief in enumerate(beliefs):
        ax = axes[0][idx]
        for mode in MODES:
            cells = {r["age_bin"]: r for r in rows
                     if r["belief"] == belief and r["alpha"] == alpha
                     and r["mode"] == mode}
            pts = [(x, cells[lab]) for x, lab in zip(xs, labels)
                   if lab in cells and cells[lab]["n"] >= min_n]
            ys = [c["coverage"] for _, c in pts]
            lo = [max(0.0, c["coverage"] - wilson_interval(c["n_covered"], c["n"])[0])
                  for _, c in pts]
            hi = [max(0.0, wilson_interval(c["n_covered"], c["n"])[1] - c["coverage"])
                  for _, c in pts]
            ax.errorbar([x for x, _ in pts], ys, yerr=[lo, hi],
                        color=_MODE_HUES[mode], marker="o", markersize=6,
                        linewidth=2, capsize=3,
                        label={"global": "one threshold for all ages",
                               "age_binned": "one threshold per age bin"}[mode])
        ax.axhline(1 - alpha, color=_INK, linewidth=1.0, linestyle="--",
                   label=f"promised rate {1 - alpha:.2f}")
        counts = [next((r["n"] for r in rows if r["belief"] == belief
                        and r["alpha"] == alpha and r["mode"] == "global"
                        and r["age_bin"] == lab), 0) for lab in labels]
        ax.set_xticks(xs)
        ax.set_xticklabels([f"{lab}\nn={c}" for lab, c in zip(labels, counts)],
                           fontsize=8)
        ax.set_xlim(-0.5, len(labels) - 0.5)
        ax.set_ylim(0, 1.04)
        ax.set_title(_short(belief), color=_INK, fontsize=10, loc="left")
        if idx == 0:
            ax.set_ylabel("share of questions whose true place\nwas inside "
                          "the prediction set", color=_INK, fontsize=9)
        ax.set_xlabel("time since the object was last seen", color=_INK,
                      fontsize=9)
        ax.tick_params(colors=_INK, labelsize=8)
        ax.yaxis.grid(True, color=_GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color(_MUTED)
        ax.spines["bottom"].set_color(_MUTED)
    handles, names = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, names, loc="lower center", ncol=3, frameon=False,
               fontsize=9)
    fig.suptitle(f"Does the prediction set contain the truth? alpha = {alpha:g}, "
                 "test households", color=_INK, fontsize=11, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.1, 1, 0.94))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_accuracy_vs_budget(rows: Sequence[Dict[str, Any]],
                            beliefs: Sequence[str], alphas: Sequence[float],
                            path: pathlib.Path) -> None:
    """One panel per belief: accuracy against senses per question. The two
    calibration modes are two lines through their alpha points (alpha
    written next to each point); NeverSense (star) and SequentialSearch
    (triangle) are the two reference policies."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    n = len(beliefs)
    fig, axes = plt.subplots(1, n, sharey=True, figsize=(3.2 * n + 0.8, 3.8),
                             squeeze=False)
    for idx, belief in enumerate(beliefs):
        ax = axes[0][idx]
        mine = [r for r in rows if r["belief"] == belief]
        for mode in MODES:
            pts = sorted((r for r in mine if r["mode"] == mode),
                         key=lambda r: r["alpha"])
            ax.plot([r["mean_budget"] for r in pts],
                    [r["task_accuracy"] for r in pts], color=_MODE_HUES[mode],
                    marker="o", markersize=5, linewidth=1.6, zorder=3)
            # Alphas whose points coincide (vacuous thresholds all land on
            # "always sense") share one range label instead of a pile-up.
            groups: List[List[Dict[str, Any]]] = []
            for r in pts:
                if groups and abs(groups[-1][0]["mean_budget"] - r["mean_budget"]) < 0.02 \
                        and abs(groups[-1][0]["task_accuracy"] - r["task_accuracy"]) < 0.01:
                    groups[-1].append(r)
                else:
                    groups.append([r])
            for group in groups:
                text = (f"{group[0]['alpha']:g}" if len(group) == 1 else
                        f"{group[0]['alpha']:g}-{group[-1]['alpha']:g}")
                ax.annotate(text, (group[0]["mean_budget"], group[0]["task_accuracy"]),
                            xytext=(4, 3 if mode == "global" else -9),
                            textcoords="offset points", fontsize=7,
                            color=_MODE_HUES[mode])
        for r in mine:
            if r["mode"] == NEVER_SENSE:
                ax.scatter([r["mean_budget"]], [r["task_accuracy"]], marker="*",
                           s=120, color=_INK, zorder=4)
            elif r["mode"] == SEQUENTIAL_SEARCH:
                ax.scatter([r["mean_budget"]], [r["task_accuracy"]], marker="^",
                           s=70, color=_INK, zorder=4)
        ax.set_title(_short(belief), color=_INK, fontsize=10, loc="left")
        ax.set_xlabel("senses per question (cost)", color=_INK, fontsize=9)
        if idx == 0:
            ax.set_ylabel("share of questions answered right", color=_INK,
                          fontsize=9)
        ax.tick_params(colors=_INK, labelsize=8)
        ax.grid(True, color=_GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color(_MUTED)
        ax.spines["bottom"].set_color(_MUTED)
    handles = [
        Line2D([], [], color=_MODE_HUES["global"], marker="o",
               label="one threshold for all ages (number = alpha)"),
        Line2D([], [], color=_MODE_HUES["age_binned"], marker="o",
               label="one threshold per age bin (number = alpha)"),
        Line2D([], [], marker="*", linestyle="", color=_INK, markersize=11,
               label="never sense"),
        Line2D([], [], marker="^", linestyle="", color=_INK,
               label="always search until found")]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False,
               fontsize=9)
    fig.suptitle("Accuracy bought per sense, test households", color=_INK,
                 fontsize=11, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.14, 1, 0.94))
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- driver

@dataclass(frozen=True)
class SweepConfig:
    bank_paths: Tuple[pathlib.Path, ...]
    out: pathlib.Path
    seed: int
    split_seed: int
    calib_frac: float
    alphas: Tuple[float, ...]
    age_edges_h: Tuple[float, ...]
    beliefs: Tuple[str, ...]
    min_bin_n: int
    workers: int
    budget: Optional[int] = None      # None: the bank's own budget_per_day

    def __post_init__(self) -> None:
        unknown = [b for b in self.beliefs if b not in BELIEF_SPECS]
        if unknown:
            raise ValueError(f"unknown beliefs {unknown}; known: "
                             f"{sorted(BELIEF_SPECS)}")
        if not self.alphas or any(not 0 < a < 1 for a in self.alphas):
            raise ValueError(f"alphas must lie in (0, 1): {self.alphas}")


def _episode_index(bank_paths: Sequence[pathlib.Path]
                   ) -> List[Tuple[str, str, str]]:
    """``(bank_path, episode_id, household_id)`` for every episode, in
    file then file order; ids must be unique across the input."""
    index: List[Tuple[str, str, str]] = []
    seen = set()
    for path in bank_paths:
        for episode in JsonlBank(path=path).episodes():
            if episode.episode_id in seen:
                raise ValueError(f"duplicate episode_id {episode.episode_id}")
            seen.add(episode.episode_id)
            index.append((str(path), episode.episode_id, episode.household_id))
    if not index:
        raise ValueError("no episodes found")
    return index


def _run_pool(fn: Any, tasks: Sequence[Dict[str, Any]], workers: int
              ) -> List[Dict[str, Any]]:
    if workers <= 1:
        return [fn(t) for t in tasks]
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(fn, t) for t in tasks]
        out = []
        for i, fut in enumerate(futures, start=1):
            out.append(fut.result())
            if i % 10 == 0 or i == len(futures):
                logger.info("%d/%d tasks done", i, len(futures))
        return out


def _merge_parts(parts: Sequence[pathlib.Path], target: pathlib.Path) -> None:
    """Concatenate gzip members (a valid multi-member gzip file)."""
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "wb") as out:
        for part in parts:
            with open(part, "rb") as fh:
                shutil.copyfileobj(fh, out)


def run_sweep(config: SweepConfig) -> List[Dict[str, str]]:
    """Run the whole sweep; returns the sweep_results rows."""
    out = config.out
    out.mkdir(parents=True, exist_ok=True)
    parts_dir = out / "questions" / "parts"
    if parts_dir.exists():
        shutil.rmtree(parts_dir)
    index = _episode_index(config.bank_paths)
    split = household_split({h for _, _, h in index}, config.split_seed,
                            config.calib_frac)
    test_index = [e for e in index if split[e[2]] == "test"]
    calib_index = [e for e in index if split[e[2]] == "calibration"]
    if not test_index or not calib_index:
        raise ValueError(
            f"split left {len(calib_index)} calibration / {len(test_index)} "
            f"test episodes; need at least one household on each side")
    labels = age_bin_labels(config.age_edges_h)
    logger.info("%d episodes, %d households (%d calibration, %d test)",
                len(index), len(split),
                sum(v == "calibration" for v in split.values()),
                sum(v == "test" for v in split.values()))

    # Phase 1: one passive walk per (belief, episode).
    passive_tasks = [
        {"bank_path": bp, "episode_id": eid, "belief_spec": BELIEF_SPECS[b],
         "seed": config.seed, "budget": config.budget,
         "part_path": str(parts_dir / f"{b}__never_sense__{eid}.jsonl.gz")}
        for b in config.beliefs for bp, eid, _ in index]
    passive = _run_pool(passive_task, passive_tasks, config.workers)
    passive.sort(key=lambda r: (r["belief_key"], r["episode_id"]))
    budget_per_day = passive[0]["budget_per_day"]
    display = {r["belief_key"]: r["belief"] for r in passive}

    pairs_calib: Dict[str, List[CalibrationPair]] = {b: [] for b in config.beliefs}
    pairs_test: Dict[str, List[CalibrationPair]] = {b: [] for b in config.beliefs}
    never_summaries: Dict[str, List[RecordSummary]] = {b: [] for b in config.beliefs}
    for res in passive:
        b = res["belief_key"]
        side = split[res["household_id"]]
        (pairs_calib if side == "calibration" else pairs_test)[b].extend(
            res["pairs"])
        if side == "test":
            never_summaries[b].extend(res["summaries"])

    # Phase 2: fit tables per (belief, alpha).
    tables: Dict[Tuple[str, float, str], QhatTable] = {}
    for b in config.beliefs:
        for alpha in config.alphas:
            tables[(b, alpha, "global")] = fit_global_qhat(
                pairs_calib[b], alpha, config.age_edges_h)
            tables[(b, alpha, "age_binned")] = fit_age_binned_qhat(
                pairs_calib[b], alpha, config.age_edges_h, config.min_bin_n)

    # Phase 3: replay policies on the test households.
    policy_specs = [PolicySpec("sequential_search")] + [
        PolicySpec("conformal", alpha, binned)
        for alpha in config.alphas for binned in (False, True)]
    policy_tasks = []
    for b in config.beliefs:
        for spec in policy_specs:
            for bp, eid, _ in test_index:
                task = {"bank_path": bp, "episode_id": eid,
                        "belief_spec": BELIEF_SPECS[b], "seed": config.seed,
                        "budget": config.budget, "policy": spec,
                        "part_path": str(parts_dir /
                                         f"{b}__{spec.slug}__{eid}.jsonl.gz")}
                if spec.kind == "conformal":
                    task["table"] = tables[(b, spec.alpha, spec.mode)]
                policy_tasks.append(task)
    replays = _run_pool(policy_task, policy_tasks, config.workers)

    # Aggregate sweep_results.
    result_rows: List[Dict[str, Any]] = []
    for b in config.beliefs:
        row = {"belief": display[b], "policy": NEVER_SENSE, "mode": NEVER_SENSE,
               "alpha": None, "qhat_global": ""}
        row.update(aggregate(never_summaries[b], budget_per_day))
        result_rows.append(row)
        for spec in policy_specs:
            summaries: List[RecordSummary] = []
            policy_name = None
            for task, res in zip(policy_tasks, replays):
                if task["belief_spec"] is BELIEF_SPECS[b] and task["policy"] == spec:
                    summaries.extend(res["summaries"])
                    policy_name = res["policy"]
            row = {"belief": display[b], "policy": policy_name,
                   "mode": spec.mode, "alpha": spec.alpha,
                   "qhat_global": "" if spec.alpha is None else
                   f"{tables[(b, spec.alpha, spec.mode)].global_qhat:.6f}"}
            row.update(aggregate(summaries, budget_per_day))
            result_rows.append(row)
    result_fields = ["belief", "policy", "mode", "alpha", "n_households",
                     "n_questions", "task_accuracy", "belief_accuracy",
                     "mean_budget", "mean_budget_per_day",
                     "forced_answer_rate", "budget_per_day", "qhat_global"]
    with open(out / "sweep_results.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=result_fields)
        writer.writeheader()
        writer.writerows(_csv_row(r) for r in result_rows)

    # Coverage by age on the test households (passive prediction sets).
    coverage_rows: List[Dict[str, Any]] = []
    for b in config.beliefs:
        for alpha in config.alphas:
            for mode in MODES:
                table = tables[(b, alpha, mode)]
                for label, n, covered, qhat in coverage_by_age(
                        pairs_test[b], table, mode == "age_binned"):
                    coverage_rows.append({
                        "belief": display[b], "alpha": alpha, "mode": mode,
                        "age_bin": label, "n": n, "n_covered": covered,
                        "coverage": round(covered / n, 6) if n else "",
                        "qhat": round(qhat, 6), "target": round(1 - alpha, 6),
                        "n_calibration": table.bin_counts[labels.index(label)],
                        "fallback_to_global": (
                            table.bin_fallback[labels.index(label)]
                            if mode == "age_binned" else "")})
    cov_fields = ["belief", "alpha", "mode", "age_bin", "n", "n_covered",
                  "coverage", "qhat", "target", "n_calibration",
                  "fallback_to_global"]
    with open(out / "coverage_by_age.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cov_fields)
        writer.writeheader()
        writer.writerows(coverage_rows)

    # Per-question dumps: one file per (belief, policy).
    qdir = out / "questions"
    for b in config.beliefs:
        slugs = ["never_sense"] + [s.slug for s in policy_specs]
        for slug in slugs:
            episodes = index if slug == "never_sense" else test_index
            parts = [parts_dir / f"{b}__{slug}__{eid}.jsonl.gz"
                     for _, eid, _ in sorted(episodes, key=lambda e: e[1])]
            _merge_parts(parts, qdir / f"{b}__{slug}.jsonl.gz")
    shutil.rmtree(parts_dir)

    # Calibration tables, provenance, plots, summary.
    (out / "calibration.json").write_text(json.dumps({
        "split": split, "age_edges_h": list(config.age_edges_h),
        "age_bin_labels": list(labels), "min_bin_n": config.min_bin_n,
        "tables": [{"belief": display[b], "alpha": alpha, "mode": mode,
                    "global_qhat": t.global_qhat, "n_global": t.n_global,
                    "bin_qhats": list(t.bin_qhats),
                    "bin_counts": list(t.bin_counts),
                    "bin_fallback": list(t.bin_fallback)}
                   for (b, alpha, mode), t in sorted(
                       tables.items(), key=lambda kv: (kv[0][0], kv[0][1],
                                                       kv[0][2]))]},
        indent=2))
    commit, dirty = git_state(config.bank_paths[0])
    (out / "provenance.json").write_text(json.dumps({
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "git_commit": commit, "git_dirty": dirty,
        "banks": [{"path": str(p), "sha256": JsonlBank(path=p).manifest_hash}
                  for p in config.bank_paths],
        "seed": config.seed, "split_seed": config.split_seed,
        "calib_frac": config.calib_frac, "alphas": list(config.alphas),
        "age_edges_h": list(config.age_edges_h),
        "beliefs": list(config.beliefs), "min_bin_n": config.min_bin_n,
        "budget_override": config.budget,
        "n_episodes": len(index), "n_test_episodes": len(test_index)},
        indent=2))
    belief_names = [display[b] for b in config.beliefs]
    plot_coverage_by_age(coverage_rows, belief_names, config.alphas, labels,
                         out / "coverage_by_age.png", config.min_bin_n)
    plot_accuracy_vs_budget(result_rows, belief_names, config.alphas,
                            out / "accuracy_vs_budget.png")
    summary = summary_table(result_rows)
    (out / "summary.md").write_text(summary + "\n")
    return [{k: str(v) for k, v in _csv_row(row).items()}
            for row in result_rows]


def _csv_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Alpha is numeric in memory (the plots key on it) and ``%g`` text
    in the csv; baselines carry an empty alpha."""
    out = dict(row)
    out["alpha"] = "" if row["alpha"] is None else f"{row['alpha']:g}"
    return out


def replot(out: pathlib.Path) -> List[Dict[str, str]]:
    """Rebuild the two plots and summary.md from the csvs already under
    ``out`` (``--plots-only``); returns the sweep_results rows."""
    with open(out / "sweep_results.csv") as fh:
        result_rows: List[Dict[str, Any]] = list(csv.DictReader(fh))
    with open(out / "coverage_by_age.csv") as fh:
        coverage_rows: List[Dict[str, Any]] = list(csv.DictReader(fh))
    for row in result_rows:
        row["alpha"] = float(row["alpha"]) if row["alpha"] else None
        for key in ("task_accuracy", "belief_accuracy", "mean_budget"):
            row[key] = float(row[key])
    for row in coverage_rows:
        row["alpha"] = float(row["alpha"])
        row["n"] = int(row["n"])
        row["n_covered"] = int(row["n_covered"])
        row["coverage"] = float(row["coverage"]) if row["coverage"] else 0.0
    beliefs = list(dict.fromkeys(r["belief"] for r in result_rows))
    alphas = sorted({r["alpha"] for r in coverage_rows})
    labels = list(dict.fromkeys(r["age_bin"] for r in coverage_rows))
    plot_coverage_by_age(coverage_rows, beliefs, alphas, labels,
                         out / "coverage_by_age.png")
    plot_accuracy_vs_budget(result_rows, beliefs, alphas,
                            out / "accuracy_vs_budget.png")
    (out / "summary.md").write_text(summary_table(result_rows) + "\n")
    return [{k: str(v) for k, v in _csv_row(row).items()}
            for row in result_rows]


def summary_table(rows: Sequence[Dict[str, Any]]) -> str:
    """Markdown table of sweep_results (what ``--demo`` prints)."""
    header = ["belief", "policy", "task_acc", "belief_acc", "senses/q",
              "senses/day", "forced", "n_q"]
    lines = ["| " + " | ".join(header) + " |",
             "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        lines.append("| " + " | ".join([
            str(r["belief"]), str(r["policy"]),
            f"{float(r['task_accuracy']):.3f}",
            f"{float(r['belief_accuracy']):.3f}",
            f"{float(r['mean_budget']):.2f}",
            f"{float(r['mean_budget_per_day']):.1f}",
            f"{float(r['forced_answer_rate']):.3f}",
            str(r["n_questions"])]) + " |")
    return "\n".join(lines)


# ------------------------------------------------------------------- demo

def write_demo_bank(path: pathlib.Path, n_households: int = 6) -> pathlib.Path:
    """A multi-household bank for ``--demo``: the gate-pass fixture under
    ``n_households`` seeds, each relabelled as its own household so the
    household split has something to split."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as out:
        for i in range(n_households):
            single = path.with_name(f"_demo_part{i}.jsonl")
            write_gate_pass_bank(single, seed=i)
            with open(single) as fh:
                for line in fh:
                    row = json.loads(line)
                    row["episode_id"] = f"demo_hh_{i:02d}_ep"
                    if row["kind"] == "episode_header":
                        row["household_id"] = f"demo_hh_{i:02d}"
                    out.write(json.dumps(row) + "\n")
            single.unlink()
    return path


def _floats(text: str) -> Tuple[float, ...]:
    return tuple(float(x) for x in text.split(",") if x.strip())


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--bank", nargs="*", type=pathlib.Path, default=[],
                        help="bank jsonl file(s); every episode of every "
                             "file is used")
    parser.add_argument("--demo", action="store_true",
                        help="run on a generated six-household fixture bank")
    parser.add_argument("--plots-only", action="store_true",
                        help="rebuild the plots and summary from the csvs "
                             "already under --out; no replay")
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--split-seed", type=int, default=0)
    parser.add_argument("--calib-frac", type=float, default=0.5)
    parser.add_argument("--alphas", default=",".join(f"{a:g}" for a in DEFAULT_ALPHAS))
    parser.add_argument("--age-edges", default=",".join(
        f"{e:g}" for e in DEFAULT_AGE_EDGES_H), help="hours")
    parser.add_argument("--beliefs", default=",".join(DEFAULT_BELIEFS))
    parser.add_argument("--min-bin-n", type=int, default=MIN_BIN_N)
    parser.add_argument("--budget", type=int, default=None,
                        help="override every episode's budget_per_day "
                             "(default: the bank's own)")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    # Non-verbose runs hide the beliefs' per-object stale-exclusion warnings
    # (a sensing sweep triggers thousands); -v shows them plus progress.
    logging.basicConfig(level=logging.INFO if args.verbose else logging.ERROR,
                        format="%(asctime)s %(levelname)s %(message)s")
    if args.plots_only:
        print(summary_table(replot(args.out)))
        return 0
    banks = list(args.bank)
    if args.demo:
        banks = [write_demo_bank(args.out / "demo_bank.jsonl")]
    if not banks:
        parser.error("--bank or --demo is required")
    config = SweepConfig(
        bank_paths=tuple(banks), out=args.out, seed=args.seed,
        split_seed=args.split_seed, calib_frac=args.calib_frac,
        alphas=_floats(args.alphas), age_edges_h=_floats(args.age_edges),
        beliefs=tuple(b.strip() for b in args.beliefs.split(",") if b.strip()),
        min_bin_n=args.min_bin_n, workers=args.workers, budget=args.budget)
    rows = run_sweep(config)
    print(summary_table(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
