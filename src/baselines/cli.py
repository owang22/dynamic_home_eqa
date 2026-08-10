"""Single entry point: run a config against a bank, write logs + results.

Usage::

    python -m baselines.cli configs/smoke.yaml

The config (YAML) declares the bank, the seed, the output directory, and
the agent grid (beliefs x policies). Every run writes, under ``out_dir``:

* ``run_log.jsonl`` — one record per (agent, question); replayable.
* ``questions.csv`` / ``aggregate.csv`` — see :mod:`baselines.metrics`.
* ``accuracy_by_agent.png`` / ``accuracy_by_day.png`` — the two basic plots.
* ``provenance.json`` — config hash, bank path + manifest hash, git commit,
  seed, timestamp. A results directory missing these fields is a bug.

Determinism: a run is fully determined by (bank, config, seed). Each
(agent, episode) pair gets its own generator seeded from a stable hash of
``(seed, agent name, episode_id)`` — no module-level RNG state anywhere.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import hashlib
import json
import logging
import pathlib
import random
import subprocess
from typing import Any, Dict, Iterator, List, Tuple

import yaml

from baselines.agent import Agent
from baselines.bank import EpisodeBank, JsonlBank, write_synthetic_bank
from baselines.beliefs.base import BeliefModel
from baselines.beliefs.last_observation import LastObservation
from baselines.beliefs.most_frequent import MostFrequentLocation
from baselines.beliefs.timetable import TimetableConfig, TimetableLookup
from baselines.harness import QuestionRecord, run_episode
from baselines.metrics import (aggregate, plot_accuracy_bar,
                               plot_accuracy_by_day, write_aggregate_csv,
                               write_questions_csv)
from baselines.policies.always_sense import AlwaysSense
from baselines.policies.base import DecisionPolicy
from baselines.policies.fixed_schedule import FixedSchedule, FixedScheduleConfig
from baselines.policies.never_sense import NeverSense

logger = logging.getLogger(__name__)

SYNTHETIC_BANK = "synthetic"
"""Config value for ``bank`` that builds the fixture bank into ``out_dir``."""


@dataclasses.dataclass(frozen=True)
class RunConfig:
    """A validated run configuration (see ``configs/smoke.yaml``)."""

    bank: str
    seed: int
    out_dir: str
    beliefs: Tuple[Dict[str, Any], ...]
    policies: Tuple[Dict[str, Any], ...]

    def __post_init__(self) -> None:
        if not self.beliefs or not self.policies:
            raise ValueError("RunConfig: beliefs and policies must be non-empty")
        for spec in (*self.beliefs, *self.policies):
            if "name" not in spec:
                raise ValueError(f"RunConfig: spec without name: {spec}")


def load_config(path: pathlib.Path) -> RunConfig:
    """Parse and validate a YAML config file."""
    raw = yaml.safe_load(path.read_text())
    try:
        return RunConfig(
            bank=str(raw["bank"]), seed=int(raw["seed"]),
            out_dir=str(raw["out_dir"]),
            beliefs=tuple(raw["agents"]["beliefs"]),
            policies=tuple(raw["agents"]["policies"]))
    except (KeyError, TypeError) as err:
        raise ValueError(f"{path}: malformed config: {err}") from err


def _derived_rng(seed: int, *parts: str) -> random.Random:
    """A generator seeded stably from (seed, *parts) — hash-salt-proof."""
    digest = hashlib.sha256(
        ":".join([str(seed), *parts]).encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


def build_belief(spec: Dict[str, Any], rng: random.Random) -> BeliefModel:
    """Instantiate a belief model from its config spec."""
    name = str(spec["name"])
    if name == "last_observation":
        return LastObservation(rng)
    if name == "most_frequent":
        return MostFrequentLocation(rng)
    if name == "timetable":
        cfg = TimetableConfig(
            bin_hours=int(spec.get("bin_hours", 1)),
            day_scheme=str(spec.get("day_scheme", "all")))
        return TimetableLookup(rng, cfg)
    raise ValueError(f"unknown belief {name!r}")


def build_policy(spec: Dict[str, Any]) -> DecisionPolicy:
    """Instantiate a decision policy from its config spec."""
    name = str(spec["name"])
    if name == "never_sense":
        return NeverSense()
    if name == "always_sense":
        return AlwaysSense()
    if name == "fixed_schedule":
        cfg = FixedScheduleConfig(
            rotation=tuple(str(r) for r in spec["rotation"]),
            every_hours=float(spec["every_hours"]))
        return FixedSchedule(cfg)
    raise ValueError(f"unknown policy {name!r}")


def run_grid(config: RunConfig, bank: EpisodeBank
             ) -> Iterator[QuestionRecord]:
    """Run every belief x policy cell over every episode of the bank.

    Agents are constructed fresh per (cell, episode) so no state leaks
    between episodes, with per-pair seeded generators for determinism.
    """
    for episode in bank.episodes():
        for belief_spec in config.beliefs:
            for policy_spec in config.policies:
                policy = build_policy(policy_spec)
                rng = _derived_rng(config.seed, str(belief_spec["name"]),
                                   policy.name, episode.episode_id)
                agent = Agent(belief=build_belief(belief_spec, rng),
                              policy=policy)
                yield from run_episode(agent, episode)


def provenance(config_path: pathlib.Path, config: RunConfig,
               bank: EpisodeBank) -> Dict[str, object]:
    """Provenance block embedded with every results directory."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
            cwd=config_path.resolve().parent, check=True).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True,
            cwd=config_path.resolve().parent, check=True).stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit, dirty = "unknown", True
    return {
        "config_path": str(config_path),
        "config_hash": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "bank_path": str(bank.path),
        "bank_manifest_hash": bank.manifest_hash,
        "git_commit": commit, "git_dirty": dirty,
        "seed": config.seed,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=pathlib.Path)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s")

    config = load_config(args.config)
    out_dir = pathlib.Path(config.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if config.bank == SYNTHETIC_BANK:
        bank: EpisodeBank = write_synthetic_bank(out_dir / "synthetic_bank.jsonl")
    else:
        bank = JsonlBank(path=pathlib.Path(config.bank))

    records: List[QuestionRecord] = list(run_grid(config, bank))
    with open(out_dir / "run_log.jsonl", "w") as f:
        for record in records:
            f.write(json.dumps(record.to_json_dict()) + "\n")

    budget = next(bank.episodes()).budget_per_day
    rows = aggregate(records, budget_per_day=budget)
    write_questions_csv(records, out_dir / "questions.csv")
    write_aggregate_csv(rows, out_dir / "aggregate.csv")
    plot_accuracy_bar(rows, out_dir / "accuracy_by_agent.png")
    plot_accuracy_by_day(rows, out_dir / "accuracy_by_day.png")
    (out_dir / "provenance.json").write_text(
        json.dumps(provenance(args.config, config, bank), indent=2))

    overall = {r.agent: r.accuracy for r in rows if r.stratum_type == "overall"}
    print(f"ran {len(records)} question-answers across {len(overall)} agents")
    for agent, acc in sorted(overall.items(), key=lambda kv: -kv[1]):
        print(f"  {acc:.3f}  {agent}")
    print(f"results -> {out_dir}")


if __name__ == "__main__":
    main()
