"""Data-health gate report: is a candidate bank a sound instrument?

The data-generation workstream runs this on every candidate bank. It
replays a FIXED panel of baseline agents over the bank and checks five
gates; the bank is healthy only if all five pass. The panel:

* NeverSense with each of the three belief models — what passive memory
  alone scores (the floor);
* SequentialSearch with each belief model at unlimited budget — a
  correctness probe: search must always find the object;
* SequentialSearch with the best belief at the real budget — what sensing
  buys at the budget agents will actually get.

The gates (thresholds are config values; defaults in
:class:`HealthcheckConfig`). Gate 0 is intrinsic — pure ground-truth
arithmetic via :mod:`baselines.bankstats` — and needs no agents; the
generation workstream should iterate against it (``cli bankstats``)
before ever paying for the panel:

0. **stationarity** — dwell-weighted modal share <= threshold (default
   0.60). Above it, a model that knows nothing but each object's home
   base is right that often at a random moment, and no amount of scale
   makes the bank interesting — scaling a too-stationary bank only buys
   tighter error bars around an uninteresting result.
1. **solvable** — SequentialSearch@unlimited task accuracy == 1.0 for
   every belief (floating-point tolerance only). Failure means a bank or
   harness bug: with unlimited budget the search provably visits every
   receptacle, so a queried object that is inside some receptacle at
   query time must be found.
2. **not_trivial** — max over beliefs of NeverSense accuracy <= threshold
   (default 0.65). Failure means the dynamics are too static: passive
   memory nearly solves the bank and sensing has nothing to prove.
3. **not_impossible** — SequentialSearch@real-budget accuracy >= best
   NeverSense accuracy + margin (default 0.15). Failure means sensing
   cannot buy meaningful accuracy at the allotted budget.
4. **discriminative** — the three beliefs' NeverSense accuracies must not
   all sit within a band (default 0.03) of each other, globally OR within
   at least one household_type stratum (bank metadata; stratified check
   SKIPPED when absent). Failure means the dynamics contain no structure
   that distinguishes different modeling assumptions.
5. **powered** — total scored questions >= minimum (default 300), so a
   few-point accuracy difference between agents is statistically
   resolvable at all.

Output: a human-readable summary (stdout) and a machine-readable JSON
report with every measured value, threshold, per-gate verdict, and the
standard provenance fields. The overall verdict REFUSES to be PASS when
the git tree is dirty — instrument results must be reproducible.

All accuracies are TASK accuracy (queried objects, exact receptacle
match). Times are seconds since episode start.
"""

from __future__ import annotations

import dataclasses
import datetime
import hashlib
import json
import logging
import pathlib
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

from baselines.bank import JsonlBank
from baselines.bankstats import (BankStats, DEFAULT_MAX_MODAL_SHARE,
                                 compute_bank_stats)
from baselines.cli import build_agent, git_state
from baselines.harness import QuestionRecord, run_episode
from baselines.types import Episode

logger = logging.getLogger(__name__)

UNLIMITED_BUDGET = 10_000
"""Per-day budget that no policy can exhaust on realistic banks."""

BELIEF_PANEL: Tuple[Dict[str, Any], ...] = (
    {"name": "last_observation"},
    {"name": "most_frequent"},
    {"name": "timetable", "bin_hours": 1, "day_scheme": "all"},
)
"""The frozen instrument: the three basic belief models."""

_NEVER = {"name": "never_sense"}
_SEARCH = {"name": "sequential_search"}


@dataclasses.dataclass(frozen=True)
class HealthcheckConfig:
    """Seed, budget override, and gate thresholds (defaults = standard)."""

    seed: int = 0
    budget: Optional[int] = None          # None -> the bank's budget_per_day
    stationarity_max_modal_share: float = DEFAULT_MAX_MODAL_SHARE
    solvable_tolerance: float = 1e-9
    not_trivial_max: float = 0.65
    not_impossible_margin: float = 0.15
    discriminative_band: float = 0.03
    powered_min_questions: int = 300


@dataclasses.dataclass(frozen=True)
class GateResult:
    """One gate's verdict: measured value vs threshold plus a rationale."""

    name: str
    passed: bool
    measured: float
    threshold: float
    comparison: str       # e.g. ">=" — measured <comparison> threshold passes
    rationale: str        # one line a non-reader of this package can follow


@dataclasses.dataclass(frozen=True)
class HealthcheckReport:
    """Everything the healthcheck concluded, in both output shapes."""

    gates: Tuple[GateResult, ...]
    gates_pass: bool      # all gates passed
    overall_pass: bool    # gates_pass AND clean git tree
    json_dict: Dict[str, Any]
    text: str


def load_healthcheck_config(path: Optional[pathlib.Path]) -> HealthcheckConfig:
    """Config from YAML (unknown keys are an error); defaults when absent."""
    if path is None:
        return HealthcheckConfig()
    raw = yaml.safe_load(path.read_text()) or {}
    known = {f.name for f in dataclasses.fields(HealthcheckConfig)}
    unknown = set(raw) - known
    if unknown:
        raise ValueError(
            f"{path}: unknown healthcheck config keys {sorted(unknown)}; "
            f"known: {sorted(known)}")
    return HealthcheckConfig(**raw)


def run_cell(bank: JsonlBank, belief_spec: Dict[str, Any],
             policy_spec: Dict[str, Any], seed: int,
             budget: Optional[int] = None) -> List[QuestionRecord]:
    """One (belief, policy) agent over the whole bank, optional budget
    override (episodes are rebuilt with the new budget; nothing else
    changes, so the override isolates budget)."""
    records: List[QuestionRecord] = []
    for episode in bank.episodes():
        if budget is not None:
            episode = dataclasses.replace(episode, budget_per_day=budget)
        agent = build_agent(belief_spec, policy_spec, seed,
                            episode.episode_id)
        records += list(run_episode(agent, episode))
    return records


def _task_accuracy(records: Sequence[QuestionRecord]) -> float:
    if not records:
        raise ValueError("no records to score — empty bank?")
    return sum(r.correct for r in records) / len(records)


def _spread(accuracies: Dict[str, float]) -> float:
    return max(accuracies.values()) - min(accuracies.values())


def _stratified_spreads(
        never: Dict[str, List[QuestionRecord]],
        episodes: Sequence[Episode]) -> Optional[Dict[str, float]]:
    """Per-household_type NeverSense accuracy spreads; None when the bank
    carries no household_type metadata (stratified check SKIPPED)."""
    type_of = {e.episode_id: e.household_type for e in episodes}
    strata = sorted({t for t in type_of.values() if t is not None})
    if not strata:
        return None
    spreads: Dict[str, float] = {}
    for stratum in strata:
        accs = {}
        for belief, records in never.items():
            in_stratum = [r for r in records
                          if type_of[r.episode_id] == stratum]
            if in_stratum:
                accs[belief] = _task_accuracy(in_stratum)
        if accs:
            spreads[stratum] = _spread(accs)
    return spreads


def _evaluate_gates(
        config: HealthcheckConfig, stats: BankStats,
        never_accs: Dict[str, float], unlimited_accs: Dict[str, float],
        real_acc: float,
        stratified: Optional[Dict[str, float]]) -> List[GateResult]:
    """Score all six gates; pure function of the panel + intrinsic numbers."""
    n_questions = stats.n_questions
    best_never = max(never_accs.values())
    gates = [
        GateResult(
            name="stationarity", measured=stats.modal_share_time,
            threshold=config.stationarity_max_modal_share, comparison="<=",
            passed=stats.modal_share_time
            <= config.stationarity_max_modal_share,
            rationale="dwell-weighted modal share: how often a "
                      "home-base-only model is right at a random moment; "
                      "computable from ground truth alone (cli bankstats) "
                      "before paying for the panel"),
        GateResult(
            name="solvable", measured=min(unlimited_accs.values()),
            threshold=1.0, comparison="==",
            passed=min(unlimited_accs.values())
            >= 1.0 - config.solvable_tolerance,
            rationale="unlimited-budget search must find every queried "
                      "object; failure means a bank or harness bug"),
        GateResult(
            name="not_trivial", measured=best_never,
            threshold=config.not_trivial_max, comparison="<=",
            passed=best_never <= config.not_trivial_max,
            rationale="if passive memory nearly solves the bank, the "
                      "dynamics are too static to test sensing"),
        GateResult(
            name="not_impossible", measured=real_acc,
            threshold=best_never + config.not_impossible_margin,
            comparison=">=",
            passed=real_acc >= best_never + config.not_impossible_margin,
            rationale="sensing at the real budget must buy meaningful "
                      "accuracy over the best passive belief"),
        GateResult(
            name="discriminative", measured=_spread(never_accs),
            threshold=config.discriminative_band, comparison=">",
            passed=_spread(never_accs) > config.discriminative_band
            or bool(stratified
                    and any(s > config.discriminative_band
                            for s in stratified.values())),
            rationale="different modeling assumptions must score "
                      "differently somewhere, or the bank cannot rank "
                      "belief models"),
        GateResult(
            name="powered", measured=float(n_questions),
            threshold=float(config.powered_min_questions), comparison=">=",
            passed=n_questions >= config.powered_min_questions,
            rationale="too few questions and accuracy differences between "
                      "agents drown in binomial noise"),
    ]
    return gates


def run_healthcheck(bank_path: pathlib.Path, config: HealthcheckConfig,
                    config_path: Optional[pathlib.Path]) -> HealthcheckReport:
    """Run the panel, evaluate the gates, and assemble both report forms."""
    bank = JsonlBank(path=bank_path)
    episodes = list(bank.episodes())
    stats = compute_bank_stats(bank)
    real_budget = (config.budget if config.budget is not None
                   else episodes[0].budget_per_day)

    never: Dict[str, List[QuestionRecord]] = {}
    unlimited_accs: Dict[str, float] = {}
    for spec in BELIEF_PANEL:
        belief = str(spec["name"])
        never[belief] = run_cell(bank, spec, _NEVER, config.seed)
        unlimited_accs[belief] = _task_accuracy(
            run_cell(bank, spec, _SEARCH, config.seed,
                     budget=UNLIMITED_BUDGET))
        logger.info("panel: %s done (never %.3f, search@unlimited %.3f)",
                    belief, _task_accuracy(never[belief]),
                    unlimited_accs[belief])
    never_accs = {b: _task_accuracy(rs) for b, rs in never.items()}
    best_belief = max(BELIEF_PANEL,
                      key=lambda s: never_accs[str(s["name"])])
    real_acc = _task_accuracy(
        run_cell(bank, best_belief, _SEARCH, config.seed,
                 budget=real_budget))

    stratified = _stratified_spreads(never, episodes)
    gates = _evaluate_gates(config, stats, never_accs,
                            unlimited_accs, real_acc, stratified)
    return _assemble(bank, config, config_path, stats, real_budget,
                     str(best_belief["name"]), never_accs, unlimited_accs,
                     real_acc, stratified, gates)


def _config_hash(config: HealthcheckConfig,
                 config_path: Optional[pathlib.Path]) -> str:
    """Hash of the config file when given, else of the effective values."""
    if config_path is not None:
        return hashlib.sha256(config_path.read_bytes()).hexdigest()
    effective = json.dumps(dataclasses.asdict(config), sort_keys=True)
    return hashlib.sha256(effective.encode()).hexdigest()


def _assemble(bank: JsonlBank, config: HealthcheckConfig,
              config_path: Optional[pathlib.Path], stats: BankStats,
              real_budget: int, best_belief: str,
              never_accs: Dict[str, float],
              unlimited_accs: Dict[str, float], real_acc: float,
              stratified: Optional[Dict[str, float]],
              gates: List[GateResult]) -> HealthcheckReport:
    """Fold panel numbers + gate verdicts into the two report forms."""
    commit, dirty = git_state(pathlib.Path(__file__).resolve().parent)
    gates_pass = all(g.passed for g in gates)
    overall_pass = gates_pass and not dirty
    json_dict: Dict[str, Any] = {
        "bank_path": str(bank.path),
        "bank_manifest_hash": bank.manifest_hash,
        "config": dataclasses.asdict(config),
        "config_hash": _config_hash(config, config_path),
        "git_commit": commit,
        "git_dirty": dirty,
        "seed": config.seed,
        "timestamp": datetime.datetime.now(
            datetime.timezone.utc).isoformat(),
        "n_questions": stats.n_questions,
        "real_budget_per_day": real_budget,
        "bank_stats": dataclasses.asdict(stats),
        "panel": {
            "never_sense_task_accuracy": never_accs,
            "sequential_search_unlimited_task_accuracy": unlimited_accs,
            "sequential_search_real_budget": {
                "belief": best_belief, "budget_per_day": real_budget,
                "task_accuracy": real_acc},
        },
        "stratified_discriminative": (
            "SKIPPED (no household_type in bank metadata)"
            if stratified is None else stratified),
        "gates": [dataclasses.asdict(g) for g in gates],
        "gates_pass": gates_pass,
        "overall_pass": overall_pass,
        "overall_note": _overall_note(gates_pass, dirty, gates),
    }
    text = _render_text(json_dict, gates)
    return HealthcheckReport(gates=tuple(gates), gates_pass=gates_pass,
                             overall_pass=overall_pass,
                             json_dict=json_dict, text=text)


def _overall_note(gates_pass: bool, dirty: bool,
                  gates: List[GateResult]) -> str:
    if gates_pass and not dirty:
        return "all gates passed on a clean git tree"
    if gates_pass:
        return ("REFUSED: all gates passed but the git tree is dirty — "
                "commit first so the result is reproducible, then re-run")
    failed = ", ".join(g.name for g in gates if not g.passed)
    return f"gates failed: {failed}"


def _render_text(json_dict: Dict[str, Any],
                 gates: List[GateResult]) -> str:
    """The stdout summary; self-explanatory without reading this package."""
    panel = json_dict["panel"]
    real = panel["sequential_search_real_budget"]
    lines = [
        f"DATA-HEALTH GATE REPORT — {pathlib.Path(json_dict['bank_path']).name}",
        f"  bank:   {json_dict['bank_path']}"
        f"  (manifest {json_dict['bank_manifest_hash'][:12]}…)",
        f"  commit: {json_dict['git_commit'][:12]}"
        f"{' (DIRTY TREE)' if json_dict['git_dirty'] else ''}"
        f"  seed {json_dict['seed']}"
        f"  questions {json_dict['n_questions']}"
        f"  budget {json_dict['real_budget_per_day']}/day",
        "",
        _intrinsic_line(json_dict),
        "",
        "  Panel — task accuracy (fraction of questions whose answered "
        "receptacle is exactly right):",
        _panel_line("NeverSense (answer from memory, never look)",
                    panel["never_sense_task_accuracy"]),
        _panel_line("SequentialSearch @ unlimited budget",
                    panel["sequential_search_unlimited_task_accuracy"]),
        f"    {'SequentialSearch @ real budget':<44}"
        f"{real['belief']} {real['task_accuracy']:.3f}",
        "",
        "  Gates (bank is healthy only if ALL pass):",
    ]
    for g in gates:
        verdict = "PASS" if g.passed else "FAIL"
        lines.append(
            f"    [{verdict}] {g.name:<16} measured {g.measured:7.3f}  "
            f"need {g.comparison} {g.threshold:.3f}")
        lines.append(f"           {g.rationale}")
    strat = json_dict["stratified_discriminative"]
    if isinstance(strat, str):
        lines.append(f"    stratified discriminative check: {strat}")
    else:
        spreads = ", ".join(f"{k}={v:.3f}" for k, v in strat.items())
        lines.append(
            f"    stratified discriminative spreads by household_type: "
            f"{spreads}")
    lines += ["",
              f"  OVERALL: {'PASS' if json_dict['overall_pass'] else 'FAIL'}"
              f" — {json_dict['overall_note']}"]
    return "\n".join(lines)


def _intrinsic_line(json_dict: Dict[str, Any]) -> str:
    b = json_dict["bank_stats"]
    return ("  Intrinsic (ground truth only — see `cli bankstats`): "
            f"modal share {b['modal_share_time']:.3f} time-weighted / "
            f"{b['modal_share_questions']:.3f} at query times; "
            f"{b['moves_per_day']:.1f} moves/day; displacement median "
            f"{b['displacement_median_h']:.1f} h, p90 "
            f"{b['displacement_p90_h']:.1f} h")


def _panel_line(label: str, accs: Dict[str, float]) -> str:
    cells = "  ".join(f"{b} {a:.3f}" for b, a in accs.items())
    return f"    {label:<44}{cells}"


def write_report(report: HealthcheckReport, out_dir: pathlib.Path) -> None:
    """Write healthcheck.json + healthcheck.txt under ``out_dir``."""
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "healthcheck.json").write_text(
        json.dumps(report.json_dict, indent=2) + "\n")
    (out_dir / "healthcheck.txt").write_text(report.text + "\n")
    logger.info("wrote %s/healthcheck.{json,txt}", out_dir)
