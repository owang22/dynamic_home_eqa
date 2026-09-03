"""Command-line entry point: grid runs and the diagnostic report.

Usage::

    python -m baselines.cli run configs/smoke.yaml
    python -m baselines.cli healthcheck banks/baselines/some_bank.jsonl \
        --out-dir smoke_results/healthcheck_some_bank

``run`` executes a belief x policy grid from a YAML config (bank, seed,
out_dir, agent grid) and writes, under ``out_dir``:

* ``run_log.jsonl`` — one record per (agent, question); replayable.
* ``questions.csv`` / ``aggregate.csv`` — see :mod:`baselines.metrics`.
* ``accuracy_by_agent.png`` / ``accuracy_by_day.png`` — the two basic plots.
* ``provenance.json`` — config hash, bank path + manifest hash, git commit,
  seed, timestamp. A results directory missing these fields is a bug.

``healthcheck`` runs the fixed instrument panel over a bank and emits a
DIAGNOSTIC report (see :mod:`baselines.healthcheck`): advisory flags,
nothing disqualifying. Exit status is nonzero only when the ``solvable``
bug check failed.

``bankstats`` computes the ground-truth-intrinsic statistics (see
:mod:`baselines.bankstats`) — no agents, so it runs in well under a
second. Its stationarity threshold is a diagnostic reference, not a
gate; the exit status still reflects it for scripting convenience.

Determinism: a run is fully determined by (bank, config, seed). Each
(agent, episode) pair gets its own generators seeded from a stable hash of
``(seed, agent name, episode_id)`` — no module-level RNG state anywhere.
Policies that need randomness (SequentialSearch tie-breaks) get a stream
separate from the belief's, so neither perturbs the other.
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
import sys
from typing import Any, Dict, Iterator, List, Tuple

import yaml

from baselines.agent import Agent
from baselines.bank import EpisodeBank, JsonlBank, write_synthetic_bank
from baselines.beliefs.base import BeliefModel
from baselines.harness import QuestionRecord, run_episode
from baselines.registry import build_registered_belief
from baselines.metrics import (aggregate, plot_accuracy_bar,
                               plot_accuracy_by_day, write_aggregate_csv,
                               write_questions_csv)
from baselines.policies.base import DecisionPolicy
from baselines.policies.fixed_schedule import FixedSchedule, FixedScheduleConfig
from baselines.policies.never_sense import NeverSense
from baselines.policies.sequential_search import SequentialSearch

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
    """Instantiate a belief model from its config spec.

    Delegates to :mod:`baselines.registry`, which knows every buildable
    model (frozen panel members and bake-off candidates alike) and their
    ``panel`` tags.
    """
    return build_registered_belief(spec, rng)


def build_policy(spec: Dict[str, Any], rng: random.Random) -> DecisionPolicy:
    """Instantiate a decision policy from its config spec.

    ``rng`` is the policy's own seeded generator (tie-breaks); policies
    without randomness ignore it.
    """
    name = str(spec["name"])
    if name == "never_sense":
        return NeverSense()
    if name == "sequential_search":
        return SequentialSearch(
            rng, confidence_threshold=float(
                spec.get("confidence_threshold", 1.0)))
    if name == "fixed_schedule":
        cfg = FixedScheduleConfig(
            rotation=tuple(str(r) for r in spec["rotation"]),
            every_hours=float(spec["every_hours"]))
        return FixedSchedule(cfg)
    raise ValueError(f"unknown policy {name!r}")


def build_agent(belief_spec: Dict[str, Any], policy_spec: Dict[str, Any],
                seed: int, episode_id: str) -> Agent:
    """One agent with per-(cell, episode) seeded generators.

    The belief's generator derivation is keyed on the policy's display
    name (stable across configs); the policy gets an independent stream so
    its tie-break draws never perturb the belief's.
    """
    belief_name = str(belief_spec["name"])
    policy_rng = _derived_rng(seed, "policy", belief_name,
                              str(policy_spec["name"]), episode_id)
    policy = build_policy(policy_spec, policy_rng)
    belief_rng = _derived_rng(seed, belief_name, policy.name, episode_id)
    return Agent(belief=build_belief(belief_spec, belief_rng), policy=policy)


def run_grid(config: RunConfig, bank: EpisodeBank
             ) -> Iterator[QuestionRecord]:
    """Run every belief x policy cell over every episode of the bank.

    Agents are constructed fresh per (cell, episode) so no state leaks
    between episodes.
    """
    for episode in bank.episodes():
        for belief_spec in config.beliefs:
            for policy_spec in config.policies:
                agent = build_agent(belief_spec, policy_spec, config.seed,
                                    episode.episode_id)
                yield from run_episode(agent, episode)


def git_state(anchor: pathlib.Path) -> Tuple[str, bool]:
    """(commit hash, dirty flag) of the repo containing ``anchor``.

    Unknown/absent git resolves to ("unknown", dirty=True) — results that
    cannot be pinned to a commit are treated as unreproducible.
    """
    cwd = anchor if anchor.is_dir() else anchor.parent
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
            cwd=cwd, check=True).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True,
            cwd=cwd, check=True).stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown", True
    return commit, dirty


def provenance(config_path: pathlib.Path, config: RunConfig,
               bank: EpisodeBank) -> Dict[str, object]:
    """Provenance block embedded with every results directory."""
    commit, dirty = git_state(config_path.resolve())
    return {
        "config_path": str(config_path),
        "config_hash": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "bank_path": str(bank.path),
        "bank_manifest_hash": bank.manifest_hash,
        "git_commit": commit, "git_dirty": dirty,
        "seed": config.seed,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def _run_command(args: argparse.Namespace) -> int:
    """The ``run`` subcommand: full grid + logs + results + plots."""
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

    overall = {r.agent: r.task_accuracy for r in rows
               if r.stratum_type == "overall"}
    print(f"ran {len(records)} question-answers across {len(overall)} agents")
    for agent, acc in sorted(overall.items(), key=lambda kv: -kv[1]):
        print(f"  {acc:.3f}  {agent}")
    print(f"results -> {out_dir}")
    return 0


def _bankstats_command(args: argparse.Namespace) -> int:
    """The ``bankstats`` subcommand; exit 0 iff stationarity passes."""
    from baselines.bank import JsonlBank
    from baselines.bankstats import (compute_bank_stats, render_text,
                                     stationarity_passes, write_report)

    bank = JsonlBank(path=pathlib.Path(args.bank))
    stats = compute_bank_stats(bank)
    print(render_text(bank.path, stats, args.max_modal_share))
    if args.out_dir is not None:
        write_report(bank, stats, args.max_modal_share,
                     pathlib.Path(args.out_dir))
        if args.figs:
            from baselines.bankstats_figs import write_dynamics_figure
            write_dynamics_figure(
                bank, stats, args.max_modal_share,
                pathlib.Path(args.out_dir) / "bank_dynamics.png")
    elif args.figs:
        raise SystemExit("bankstats: --figs requires --out-dir")
    return 0 if stationarity_passes(stats, args.max_modal_share) else 1


def _fleet_command(args: argparse.Namespace) -> int:
    """The ``fleet`` subcommand: export + healthcheck every household."""
    import baselines.fleet as fleet

    export_cfg, hc_cfg = fleet.load_fleet_config(args.config)
    sources = fleet.discover_households(
        tuple(args.roots), timeline_dirname=f"timeline_seed{args.seed}")
    rows = fleet.run_fleet(sources, export_cfg, hc_cfg, args.banks_dir,
                           args.out_dir)
    provenance = fleet.provenance_block(args.config, export_cfg.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "fleet_summary.json").write_text(json.dumps(
        {"provenance": provenance, "banks": rows}, indent=2) + "\n")
    (args.out_dir / "fleet_summary.md").write_text(
        fleet.render_summary_md(rows, provenance))
    clean = [r for r in rows if r["status"] == "ok" and not r["flags"]]
    print(f"fleet: {len(rows)} banks, {len(clean)} with no diagnostics "
          f"flagged -> {args.out_dir}/fleet_summary.{{md,json}}")
    for row in rows:
        verdict = (row["error"] if row["status"] != "ok"
                   else "no flags" if not row["flags"]
                   else "flagged: " + ",".join(row["flags"]))
        print(f"  {row['household']}: {verdict}")
    return 0 if all(r["status"] == "ok" for r in rows) else 1


def _healthcheck_command(args: argparse.Namespace) -> int:
    """The ``healthcheck`` subcommand: a diagnostic report. Exit is 0
    unless the ``solvable`` bug check failed — flags are informational."""
    from baselines.healthcheck import (load_healthcheck_config,
                                       run_healthcheck, write_report)

    config = load_healthcheck_config(args.config)
    report = run_healthcheck(pathlib.Path(args.bank), config, args.config)
    print(report.text)
    if args.out_dir is not None:
        write_report(report, pathlib.Path(args.out_dir))
    return 0 if report.solvable_ok else 1


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser(
        "run", help="run a belief x policy grid from a YAML config")
    run_parser.add_argument("config", type=pathlib.Path)

    hc_parser = sub.add_parser(
        "healthcheck", help="run the data-health gate report on a bank")
    hc_parser.add_argument("bank", type=pathlib.Path)
    hc_parser.add_argument("--config", type=pathlib.Path, default=None,
                           help="YAML with seed/budget/threshold overrides "
                                "(defaults are the standard gates)")
    hc_parser.add_argument("--out-dir", type=pathlib.Path, default=None,
                           help="write healthcheck.json + healthcheck.txt here")

    fleet_parser = sub.add_parser(
        "fleet", help="export + healthcheck every realized household under "
                      "one shared config; write the fleet summary")
    fleet_parser.add_argument(
        "--roots", type=pathlib.Path, nargs="+",
        default=None,
        help="profile roots to scan (default: the attribute-first "
             "households set, profiles/households/generated; pass "
             "old_profiles/revamp_v2/storyfirst for the comparison set)")
    fleet_parser.add_argument(
        "--seed", type=int, default=0,
        help="which realization of each household to scan "
             "(timeline_seed<N>); the export RNG seed stays the "
             "config's own")
    fleet_parser.add_argument(
        "--config", type=pathlib.Path,
        default=pathlib.Path("src/baselines/configs/fleet.yaml"))
    fleet_parser.add_argument(
        "--banks-dir", type=pathlib.Path,
        default=pathlib.Path("banks/baselines/fleet"))
    fleet_parser.add_argument(
        "--out-dir", type=pathlib.Path,
        default=pathlib.Path("reports/baselines/fleet"))

    stats_parser = sub.add_parser(
        "bankstats", help="ground-truth-intrinsic stats + stationarity gate "
                          "(no agents; the fast generator feedback loop)")
    stats_parser.add_argument("bank", type=pathlib.Path)
    stats_parser.add_argument("--max-modal-share", type=float, default=None,
                              help="stationarity ceiling (default 0.60)")
    stats_parser.add_argument("--out-dir", type=pathlib.Path, default=None,
                              help="write bankstats.json + bankstats.txt here")
    stats_parser.add_argument("--figs", action="store_true",
                              help="also render bank_dynamics.png (4-panel "
                                   "dynamics diagnostic) into --out-dir")

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s")
    if args.command == "bankstats" and args.max_modal_share is None:
        from baselines.bankstats import DEFAULT_MAX_MODAL_SHARE
        args.max_modal_share = DEFAULT_MAX_MODAL_SHARE
    if args.command == "fleet" and args.roots is None:
        from baselines.fleet import DEFAULT_ROOTS
        args.roots = [pathlib.Path(r) for r in DEFAULT_ROOTS]
    handlers = {"run": _run_command, "healthcheck": _healthcheck_command,
                "bankstats": _bankstats_command, "fleet": _fleet_command}
    sys.exit(handlers[args.command](args))


if __name__ == "__main__":
    main()
