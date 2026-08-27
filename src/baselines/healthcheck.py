"""Diagnostic report for a candidate bank: does the current experimental
setup produce degenerate behavior?

Runs a FIXED panel of baseline agents over the bank and reports a set of
DIAGNOSTICS — measured values against reference thresholds. Diagnostics
are heuristics: they flag suspicious setups for a human to look at, and
none of them disqualifies a bank. (Dataset acceptance itself happens at
generation time, in ``src/revamp_v2/validate.py``; by the time a bank
exists here, the household content has already been accepted. What this
report probes is the EXPERIMENT built on top of it — the observation
stream, the question sample, the budget — which is iterated on freely.)

The one exception is ``solvable``: unlimited-budget search failing to
find a queried object is not a matter of judgment but a bug in the bank
or the harness, so its failure is reported as an ERROR and the CLI exits
nonzero on it.

The panel:

* NeverSense with each of the three belief models — what passive memory
  alone scores;
* SequentialSearch with each belief model at unlimited budget — the
  ``solvable`` correctness probe;
* SequentialSearch with the best belief at the configured budget — what
  paid sensing adds at that budget.

The diagnostics (thresholds are config values; defaults in
:class:`HealthcheckConfig`). The first is intrinsic — pure ground-truth
arithmetic via :mod:`baselines.bankstats` — and needs no agents:

0. **stationarity** — dwell-weighted modal share, averaged over objects,
   vs a threshold (default 0.60). A permanently-parked object contributes
   exactly 1.0 to this mean, so a high value may just mean the household
   owns realistic stay-put objects; read the per-object distribution and
   ``modal_share_questions`` alongside it. Empirically it is a strong
   predictor of which banks passive memory eventually solves.
1. **solvable** — SequentialSearch@unlimited task accuracy == 1.0 for
   every belief. THE one hard check: failure means a bank or harness bug.
2. **not_trivial** — best passive accuracy vs a ceiling (default 0.65).
   Flags that passive memory alone nearly solves the bank, leaving paid
   sensing little to prove.
3. **not_impossible** — search at the configured budget vs best passive
   + margin (default 0.15). Flags that sensing bought little at this
   budget; note the budget, not the bank, may be what it measures.
4. **discriminative** — the three passive models' accuracy spread vs a
   band (default 0.03). Flags that all models answer alike — usually a
   sign the observation stream is too sparse for them to differ.
5. **powered** — total scored questions vs a minimum (default 300).

Output: a human-readable summary (stdout) and a machine-readable JSON
report with every measured value, threshold, per-diagnostic flag, and
the standard provenance fields (including whether the git tree was
dirty at run time).

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
from baselines.registry import assert_frozen_panel
from baselines.types import Episode

logger = logging.getLogger(__name__)

UNLIMITED_BUDGET = 10_000
"""Per-day budget that no policy can exhaust on realistic banks."""

BELIEF_PANEL: Tuple[Dict[str, Any], ...] = (
    {"name": "last_observation"},
    {"name": "most_frequent", "half_life_h": 24},
    {"name": "timetable", "bin_hours": 1, "day_scheme": "all",
     "half_life_h": 24},
)
"""The frozen instrument: the three basic belief models.

Frequency-style members carry a 24 h count half-life — an infinite-memory
histogram is a known-broken estimator in a drifting world, so the panel
compares the honest strong versions. 24 h is the domain's natural cycle,
fixed a priori; tuning the half-life per bank would be instrument-gaming
and invalidates gate comparisons across banks.
"""

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
class Diagnostic:
    """One diagnostic: a measured value against a reference threshold.

    ``flagged`` means the measurement crossed the threshold — something a
    human should look at, not a disqualification. ``is_bug_check`` marks
    ``solvable``, whose flag DOES mean the results are wrong (a bank or
    harness bug) rather than merely suspicious.
    """

    name: str
    flagged: bool
    measured: float
    threshold: float
    comparison: str       # e.g. ">=" — measured <comparison> threshold is ok
    rationale: str        # one line a non-reader of this package can follow
    is_bug_check: bool = False


@dataclasses.dataclass(frozen=True)
class HealthcheckReport:
    """Everything the report concluded, in both output shapes."""

    diagnostics: Tuple[Diagnostic, ...]
    flags: Tuple[str, ...]   # names of diagnostics that flagged
    solvable_ok: bool        # False = bank/harness bug, results are wrong
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


def _evaluate_diagnostics(
        config: HealthcheckConfig, stats: BankStats,
        never_accs: Dict[str, float], unlimited_accs: Dict[str, float],
        real_acc: float,
        stratified: Optional[Dict[str, float]]) -> List[Diagnostic]:
    """Score every diagnostic; pure function of the panel numbers."""
    n_questions = stats.n_questions
    best_never = max(never_accs.values())
    spread = _spread(never_accs)
    return [
        Diagnostic(
            name="stationarity", measured=stats.modal_share_time,
            threshold=config.stationarity_max_modal_share, comparison="<=",
            flagged=stats.modal_share_time
            > config.stationarity_max_modal_share,
            rationale="mean dwell-weighted modal share; high values mean "
                      "objects mostly sit at their usual spots — read the "
                      "per-object distribution before concluding anything"),
        Diagnostic(
            name="solvable", measured=min(unlimited_accs.values()),
            threshold=1.0, comparison="==", is_bug_check=True,
            flagged=min(unlimited_accs.values())
            < 1.0 - config.solvable_tolerance,
            rationale="unlimited-budget search must find every queried "
                      "object; failure means a bank or harness BUG, not a "
                      "data property"),
        Diagnostic(
            name="not_trivial", measured=best_never,
            threshold=config.not_trivial_max, comparison="<=",
            flagged=best_never > config.not_trivial_max,
            rationale="passive memory alone nearly solves the bank at this "
                      "observation rate; paid sensing has little to prove"),
        Diagnostic(
            name="not_impossible", measured=real_acc,
            threshold=best_never + config.not_impossible_margin,
            comparison=">=",
            flagged=real_acc < best_never + config.not_impossible_margin,
            rationale="sensing bought little over passive at the configured "
                      "budget; may reflect the budget rather than the bank"),
        Diagnostic(
            name="discriminative", measured=spread,
            threshold=config.discriminative_band, comparison=">",
            flagged=not (spread > config.discriminative_band
                         or bool(stratified
                                 and any(v > config.discriminative_band
                                         for v in stratified.values()))),
            rationale="all passive models answer alike; usually the "
                      "observation stream is too sparse for them to differ"),
        Diagnostic(
            name="powered", measured=float(n_questions),
            threshold=float(config.powered_min_questions), comparison=">=",
            flagged=n_questions < config.powered_min_questions,
            rationale="few questions; small accuracy differences drown in "
                      "binomial noise"),
    ]


def run_healthcheck(bank_path: pathlib.Path, config: HealthcheckConfig,
                    config_path: Optional[pathlib.Path]) -> HealthcheckReport:
    """Run the panel, evaluate the diagnostics, assemble both report forms."""
    # Candidate-tagged beliefs may never enter the instrument: a changed
    # panel silently changes what every diagnostic measures.
    assert_frozen_panel(BELIEF_PANEL)
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
    diagnostics = _evaluate_diagnostics(config, stats, never_accs,
                                        unlimited_accs, real_acc, stratified)
    return _assemble(bank, config, config_path, stats, real_budget,
                     str(best_belief["name"]), never_accs, unlimited_accs,
                     real_acc, stratified, diagnostics)


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
              diagnostics: List[Diagnostic]) -> HealthcheckReport:
    """Fold panel numbers + diagnostic flags into the two report forms."""
    commit, dirty = git_state(pathlib.Path(__file__).resolve().parent)
    flags = tuple(d.name for d in diagnostics if d.flagged)
    solvable_ok = not any(d.flagged for d in diagnostics if d.is_bug_check)
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
        "belief_panel": [dict(spec) for spec in BELIEF_PANEL],
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
        "diagnostics": [dataclasses.asdict(d) for d in diagnostics],
        "flags": list(flags),
        "solvable_ok": solvable_ok,
    }
    text = _render_text(json_dict, diagnostics)
    return HealthcheckReport(diagnostics=tuple(diagnostics), flags=flags,
                             solvable_ok=solvable_ok,
                             json_dict=json_dict, text=text)


def _render_text(json_dict: Dict[str, Any],
                 diagnostics: List[Diagnostic]) -> str:
    """The stdout summary; self-explanatory without reading this package."""
    panel = json_dict["panel"]
    real = panel["sequential_search_real_budget"]
    lines = [
        f"DIAGNOSTIC REPORT — {pathlib.Path(json_dict['bank_path']).name}",
        f"  bank:   {json_dict['bank_path']}"
        f"  (manifest {json_dict['bank_manifest_hash'][:12]}…)",
        f"  commit: {json_dict['git_commit'][:12]}"
        f"{' (dirty tree)' if json_dict['git_dirty'] else ''}"
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
        "  Diagnostics (flags mark setups worth a look; nothing here "
        "disqualifies a bank):",
    ]
    for d in diagnostics:
        mark = ("ERROR" if d.flagged and d.is_bug_check
                else "flag" if d.flagged else " ok ")
        lines.append(
            f"    [{mark:>5s}] {d.name:<16} "
            f"measured {d.measured:7.3f}  reference {d.comparison} "
            f"{d.threshold:.3f}")
        lines.append(f"           {d.rationale}")
    strat = json_dict["stratified_discriminative"]
    if isinstance(strat, str):
        lines.append(f"    stratified discriminative check: {strat}")
    else:
        spreads = ", ".join(f"{k}={v:.3f}" for k, v in strat.items())
        lines.append(
            f"    stratified discriminative spreads by household_type: "
            f"{spreads}")
    flags = json_dict["flags"]
    lines += ["", "  " + _summary_line(flags, bool(json_dict["solvable_ok"]))]
    return "\n".join(lines)


def _summary_line(flags: List[str], solvable_ok: bool) -> str:
    if not solvable_ok:
        return ("ERROR: solvable failed — a bank or harness bug; every "
                "number above is suspect until it is fixed")
    if not flags:
        return "no diagnostics flagged"
    return ("flagged: " + ", ".join(flags)
            + "  (diagnostics, not disqualifiers)")


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
