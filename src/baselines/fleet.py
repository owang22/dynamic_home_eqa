"""Fleet health run: export + healthcheck + bankstats for every realized
household, under ONE shared configuration.

Discovers every household folder with realized timeline artifacts under
the configured profile roots (default: the storyfirst set, which is the
project's sole synthetic data source), exports each with the standard
exporter settings from ``configs/fleet.yaml`` (the hh1 gate-passing
recipe — never tuned per bank), runs the six-gate healthcheck and the
intrinsic bank statistics, and writes one summary row per bank:

* ``fleet_summary.md`` / ``fleet_summary.json`` under the report
  directory — per-gate verdicts and measured values, NeverSense accuracy
  per panel belief, modal-share and stationarity stats, question count,
  and the standard provenance fields;
* one full healthcheck report per bank under ``healthchecks/<slug>/``.

A bank whose export or diagnostic run raises is recorded as an
``error`` row (with the exception text) and the fleet continues — one
broken household must not hide the other nine. Diagnostics never
disqualify a bank; each row carries the list of flags raised plus
``solvable_ok`` (False = bank/harness bug).

All times are seconds since episode start; a day is 86 400 s.
"""

from __future__ import annotations

import dataclasses
import datetime
import hashlib
import json
import logging
import pathlib
from typing import Any, Dict, List, Optional, Tuple

import yaml

from baselines.cli import git_state
from baselines.export_bank import export
from baselines.healthcheck import HealthcheckConfig, run_healthcheck
from baselines.healthcheck import write_report as write_healthcheck_report

logger = logging.getLogger(__name__)

DEFAULT_ROOTS = ("profiles/households/generated",)
"""Profile roots scanned for household folders (relative to the repo cwd).

The attribute-first households set (``profiles/households/``) is the
current data source: whole-unit archetypes with census/ATUS-grounded
schedules, 20 households built as of 2026-08-28. The storyfirst set it
replaces moved to ``old_profiles/revamp_v2/storyfirst`` and stays the
COMPARISON set — point the fleet at it deliberately with ``--roots
old_profiles/revamp_v2/storyfirst`` to reproduce the old numbers. Earlier
profile lines (revamp_v1 and the sets it superseded) remain on disk for
provenance only and are never a data choice."""

SPEC_FILENAMES = ("object_motions.yaml", "program.yaml",
                  "routine_program.yaml")
"""Exporter spec filenames, tried in order, per pipeline generation."""

TIMELINE_DIRNAME = "timeline_seed0"
"""The realized-timeline directory a household must carry to be exported.

The default is seed 0; ``discover_households(..., timeline_dirname=...)``
scans another realization. A household realized under several seeds is
ONE home with several histories — same persona, story and object rules,
different jitter/misplacement draws — so seeded runs are repeats for
variance, never extra households."""

_TIMELINE_FILES = ("events.jsonl", "hourly.csv")


@dataclasses.dataclass(frozen=True)
class FleetExportConfig:
    """The shared exporter settings (one config for the whole fleet)."""

    seed: int
    sightings_per_day: int
    questions_per_day: int
    first_question_day: int
    budget_per_day: int
    query_mode: str
    initial_tour: bool
    # Size-scaling rules; when set they REPLACE the absolute setting above
    # (see baselines.export_bank.export). A flat per-day rate is not
    # household-agnostic once inventories differ by 3x.
    sightings_per_object_day: Optional[float] = None
    budget_per_sensable_receptacle: Optional[float] = None
    # Observation model selection (see baselines.export_bank.export):
    # "glimpse" draws single random objects; "room_visit" runs a patrol
    # schedule from baselines.room_observations.
    observation_model: str = "glimpse"
    patrol: str = "round_robin_patrol"
    visits_per_day: int = 8


@dataclasses.dataclass(frozen=True)
class HouseholdSource:
    """One discovered household: its timeline, spec, and display slug."""

    slug: str                     # e.g. "revamp_v2/storyfirst/gpt-5.6-terra/hh1"
    timeline: pathlib.Path
    spec: pathlib.Path


def load_fleet_config(path: pathlib.Path
                      ) -> Tuple[FleetExportConfig, HealthcheckConfig]:
    """Parse configs/fleet.yaml; unknown keys are an error."""
    raw = yaml.safe_load(path.read_text())
    known = {f.name for f in dataclasses.fields(FleetExportConfig)}
    unknown = set(raw.get("export", {})) - known
    if unknown or set(raw) - {"export", "healthcheck"}:
        raise ValueError(
            f"{path}: unknown fleet config keys "
            f"{sorted(unknown | (set(raw) - {'export', 'healthcheck'}))}")
    export_cfg = FleetExportConfig(**raw["export"])
    hc_raw = raw.get("healthcheck") or {}
    hc_cfg = dataclasses.replace(HealthcheckConfig(**hc_raw),
                                 seed=export_cfg.seed)
    return export_cfg, hc_cfg


def discover_households(roots: Tuple[pathlib.Path, ...],
                        timeline_dirname: str = TIMELINE_DIRNAME
                        ) -> List[HouseholdSource]:
    """Every ``<root>/**/hh*`` folder with a realized timeline and a spec.

    A folder with a timeline but no recognized spec file is an error (it
    should have been exportable); a folder with no timeline is silently
    skipped (persona-only households that were never realized).
    """
    sources: List[HouseholdSource] = []
    for root in roots:
        if not root.is_dir():
            raise FileNotFoundError(f"fleet root {root} does not exist")
        for household in sorted(root.glob("*/hh*")):
            timeline = household / timeline_dirname
            if not all((timeline / f).exists() for f in _TIMELINE_FILES):
                continue
            spec = next((household / name for name in SPEC_FILENAMES
                         if (household / name).exists()), None)
            if spec is None:
                raise FileNotFoundError(
                    f"{household}: realized timeline but no spec file "
                    f"(looked for {SPEC_FILENAMES})")
            sources.append(HouseholdSource(
                slug=str(household), timeline=timeline, spec=spec))
    if not sources:
        raise FileNotFoundError(
            f"no {timeline_dirname} households under roots "
            f"{[str(r) for r in roots]}")
    return sources


def _bank_name(source: HouseholdSource) -> str:
    """Filesystem-safe bank filename from the household path AND its
    realization: two seeds of one household are different banks, and a
    name without the seed silently overwrote one with the other."""
    slug = source.slug.replace("profiles/", "", 1).replace("/", "__")
    seed_dir = source.timeline.name
    suffix = ("" if seed_dir == TIMELINE_DIRNAME
              else "__" + seed_dir.replace("timeline_", ""))
    return f"{slug}{suffix}_bank.jsonl"


def _summary_row(source: HouseholdSource,
                 healthcheck_json: Dict[str, Any]) -> Dict[str, Any]:
    """One fleet_summary row from a completed healthcheck report."""
    stats = healthcheck_json["bank_stats"]
    return {
        "household": source.slug,
        "status": "ok",
        "bank_path": healthcheck_json["bank_path"],
        "bank_manifest_hash": healthcheck_json["bank_manifest_hash"],
        "household_type": stats.get("household_type"),
        "n_questions": healthcheck_json["n_questions"],
        "diagnostics": {d["name"]: {"flagged": d["flagged"],
                                    "measured": d["measured"],
                                    "threshold": d["threshold"]}
                        for d in healthcheck_json["diagnostics"]},
        "flags": healthcheck_json["flags"],
        "solvable_ok": healthcheck_json["solvable_ok"],
        "never_sense_accuracy":
            healthcheck_json["panel"]["never_sense_task_accuracy"],
        "search_real_budget":
            healthcheck_json["panel"]["sequential_search_real_budget"],
        "modal_share_time": stats["modal_share_time"],
        "modal_share_questions": stats["modal_share_questions"],
        "moves_per_day": stats["moves_per_day"],
        "displaced_time_share": stats["displaced_time_share"],
        "displacement_median_h": stats["displacement_median_h"],
    }


def run_fleet(sources: List[HouseholdSource], export_cfg: FleetExportConfig,
              hc_cfg: HealthcheckConfig, banks_dir: pathlib.Path,
              out_dir: pathlib.Path) -> List[Dict[str, Any]]:
    """Export + healthcheck every household; return the summary rows."""
    banks_dir.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []
    for source in sources:
        logger.info("fleet: %s", source.slug)
        try:
            rows.append(_run_one(source, export_cfg, hc_cfg,
                                 banks_dir, out_dir))
        except Exception as err:   # deliberate: one bank must not end the run
            logger.exception("fleet: %s failed", source.slug)
            rows.append({"household": source.slug, "status": "error",
                         "error": f"{type(err).__name__}: {err}"})
    return rows


def _run_one(source: HouseholdSource, export_cfg: FleetExportConfig,
             hc_cfg: HealthcheckConfig, banks_dir: pathlib.Path,
             out_dir: pathlib.Path) -> Dict[str, Any]:
    """Export one bank, run its healthcheck, write its report dir."""
    bank_path = banks_dir / _bank_name(source)
    export(source.timeline, source.spec, bank_path, export_cfg.seed,
           export_cfg.sightings_per_day, export_cfg.questions_per_day,
           export_cfg.first_question_day, export_cfg.budget_per_day,
           export_cfg.query_mode, initial_tour=export_cfg.initial_tour,
           sightings_per_object_day=export_cfg.sightings_per_object_day,
           budget_per_sensable_receptacle=(
               export_cfg.budget_per_sensable_receptacle),
           observation_model=export_cfg.observation_model,
           patrol=export_cfg.patrol,
           visits_per_day=export_cfg.visits_per_day)
    report = run_healthcheck(bank_path, hc_cfg, None)
    slug_dir = out_dir / "healthchecks" / _bank_name(source).removesuffix(
        "_bank.jsonl")
    write_healthcheck_report(report, slug_dir)
    row = _summary_row(source, report.json_dict)
    # household_type lives in the episode header, not the intrinsic stats;
    # read it back from the exported bank's header line.
    with open(bank_path) as f:
        row["household_type"] = json.loads(
            f.readline()).get("household_type")
    return row


def provenance_block(config_path: pathlib.Path, seed: int) -> Dict[str, Any]:
    commit, dirty = git_state(pathlib.Path(__file__).resolve().parent)
    return {
        "config_path": str(config_path),
        "config_hash": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "git_commit": commit, "git_dirty": dirty, "seed": seed,
        "timestamp": datetime.datetime.now(
            datetime.timezone.utc).isoformat(),
    }


def render_summary_md(rows: List[Dict[str, Any]],
                      provenance: Dict[str, Any]) -> str:
    """The human-readable fleet table."""
    lines = [
        "# Fleet health run",
        "",
        f"One shared config (`{provenance['config_path']}`, hash "
        f"`{provenance['config_hash'][:12]}…`), seed "
        f"{provenance['seed']}, commit `{provenance['git_commit'][:12]}`"
        f"{' (dirty tree)' if provenance['git_dirty'] else ''}, "
        f"run {provenance['timestamp']}.",
        "",
        "`diagnostics` = flags in order: stationarity / solvable / "
        "not_trivial / not_impossible / discriminative / powered "
        "(`.` = not flagged, letter = flagged; flags are advisory, "
        "nothing disqualifies). NeverSense columns are passive task "
        "accuracy for the frozen panel beliefs.",
        "",
        "| household | type | questions | diagnostics | flags | "
        "NS last_obs | NS most_freq | NS timetable | search@budget "
        "| modal share (time/query) | moves/day |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        if row["status"] != "ok":
            lines.append(f"| {row['household']} | — | — | ERROR | — | — | "
                         f"— | — | — | {row['error']} | — |")
            continue
        marks = "".join(g[0].upper() if row["diagnostics"][g]["flagged"]
                        else "." for g in
                        ("stationarity", "solvable", "not_trivial",
                         "not_impossible", "discriminative", "powered"))
        ns = row["never_sense_accuracy"]
        search = row["search_real_budget"]
        lines.append(
            f"| {row['household']} | {row['household_type'] or '—'} "
            f"| {row['n_questions']} | `{marks}` "
            f"| {len(row['flags'])} "
            f"| {ns['last_observation']:.3f} | {ns['most_frequent']:.3f} "
            f"| {ns['timetable']:.3f} | {search['task_accuracy']:.3f} "
            f"| {row['modal_share_time']:.3f}/"
            f"{row['modal_share_questions']:.3f} "
            f"| {row['moves_per_day']:.1f} |")
    lines.append("")
    return "\n".join(lines)
