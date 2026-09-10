"""Oracle-posterior study: OracleBelief on the representative grid.

Stages (``--stage``, run in this order; each reads the previous one's
files under ``--out``, default ``results/oracle_program_posterior/``):

  realize    re-realize every fleet household's program at the routine
             oracle's seeds and cache the change points
             (:mod:`baselines.beliefs.oracle_program_posterior`).
  sweep      the weighting knobs (``eps`` per disagreement, forgetting
             half-life) on a fixed grid: OracleBelief under the passive
             diet (NeverSense, the bank's own budget) on all 20 banks
             per setting -> ``sweep.csv``, ``sweep.md``. The setting is
             chosen on the CALIBRATION households only (largest passive
             accuracy among settings whose calibration median ESS clears
             ``ESS_STOP``) and written to ``selected.json``; the test
             households' numbers are reported next to it but never
             consulted.
  ess_gate   the degeneracy diagnostic on the fleet at the study's
             setting (``--eps``/``--half-life-h`` when given, else
             ``selected.json``, else the module defaults): the effective
             sample size of the realization weights logged per question
             -> ``ess_passive.csv``, ``ess_gate.md``. Exits 2 when the
             fleet's median ESS is below ``ESS_STOP``: the grid must not
             run before an owner chooses the fix.
  grid       the representative grid (beliefs x {NeverSense,
             SequentialSearch} x budgets {24, 90}) on the test households
             -> ``grid.csv``, ``accuracy_by_day.csv``, question dumps.
             LLM cells are skipped when the cache cannot answer them.
  report     ``findings.md``: policy separation on the oracle belief vs
             the real beliefs, the oracle-vs-best-real gap per budget
             split into belief error and decision error, whether the
             oracle belief beats every real belief cell by cell, the ESS
             distribution, and OracleBelief's passive accuracy against
             the routine oracle's no-observation answer on the same
             questions.

Usage:
  PYTHONPATH=src python -m baselines.oracle_posterior_study \\
      --stage realize sweep ess_gate grid report --workers 10
"""

from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import json
import logging
import pathlib
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.beliefs.oracle_program_posterior import (
    DEFAULT_EPS, DEFAULT_HALF_LIFE_H, DEFAULT_REALIZATION_CACHE,
    default_household_dir, load_or_realize)
from baselines.representative_grid import (BELIEF_SPECS, REPO_ROOT,
                                           REPRESENTATIVE_BUDGETS,
                                           EpisodeRef, GridTask, PolicySpec,
                                           aggregate_rows, episode_index,
                                           fleet_bank_paths, fmt,
                                           llm_pending_fraction, merge_parts,
                                           part_path, provenance, read_csv,
                                           read_dump, reference_split,
                                           run_plain_task, run_pool,
                                           write_csv, DAY_FIELDS, GRID_FIELDS)
from baselines.routine_oracle import DEFAULT_ORACLE_SEEDS

logger = logging.getLogger(__name__)

DEFAULT_OUT = REPO_ROOT / "results" / "oracle_program_posterior"
ESS_STOP = 5.0
"""Median passive ESS below which the study stops before the grid."""
POLICIES = (PolicySpec("never_sense", label="NeverSense"),
            PolicySpec("sequential_search", label="SequentialSearch"))
REAL_BELIEFS = ("LastObservation", "PeriodicPersistence", "PerpetuaStar",
                "LLMBelief")
SWEEP_EPS: Tuple[float, ...] = (0.05, 0.2, 0.4, 0.6, 0.8, 0.9)
SWEEP_HALF_LIVES_H: Tuple[Optional[float], ...] = (None, 96.0, 48.0, 24.0,
                                                   12.0, 6.0)
"""The sweep grid: every eps with every forgetting half-life (None: the
original whole-episode matching)."""
SUBSETS = ("calibration", "test", "fleet")


# ----------------------------------------------------------------- config

@dataclasses.dataclass(frozen=True)
class OracleConfig:
    """OracleBelief's weighting knobs for one run of the study."""

    eps: float = DEFAULT_EPS
    half_life_h: Optional[float] = DEFAULT_HALF_LIFE_H

    @property
    def hl_label(self) -> str:
        return "none" if self.half_life_h is None else f"{self.half_life_h:g}h"

    @property
    def slug(self) -> str:
        return f"eps{self.eps:g}__hl{self.hl_label}"

    @property
    def label(self) -> str:
        return (f"eps {self.eps:g} per disagreement, forgetting half-life "
                f"{'none (whole episode)' if self.half_life_h is None else f'{self.half_life_h:g} h'}")

    def spec(self) -> Dict[str, Any]:
        return dict(BELIEF_SPECS["OracleBelief"], eps=self.eps,
                    half_life_h=self.half_life_h)

    def to_json(self) -> Dict[str, Any]:
        return {"eps": self.eps, "half_life_h": self.half_life_h}

    @classmethod
    def from_json(cls, doc: Dict[str, Any]) -> "OracleConfig":
        hl = doc.get("half_life_h")
        return cls(float(doc["eps"]), None if hl is None else float(hl))


SWEEP_CONFIGS: Tuple[OracleConfig, ...] = tuple(
    OracleConfig(eps, hl) for eps in SWEEP_EPS for hl in SWEEP_HALF_LIVES_H)


def belief_specs_with(config: OracleConfig) -> Dict[str, Dict[str, Any]]:
    specs = {k: dict(v) for k, v in BELIEF_SPECS.items()}
    specs["OracleBelief"] = config.spec()
    return specs


def resolve_config(out: pathlib.Path, eps: Optional[float],
                   half_life_h: Optional[float]) -> OracleConfig:
    """Explicit flags win; else the sweep's ``selected.json``; else the
    module defaults. ``half_life_h`` at or below 0 means none."""
    if eps is not None or half_life_h is not None:
        hl = (None if half_life_h is None or half_life_h <= 0.0
              else float(half_life_h))
        return OracleConfig(DEFAULT_EPS if eps is None else float(eps), hl)
    selected = out / "selected.json"
    if selected.exists():
        return OracleConfig.from_json(json.loads(selected.read_text()))
    return OracleConfig()


# ---------------------------------------------------------------- realize

def _realize_one(args: Tuple[EpisodeRef, int]) -> str:
    ref, n_seeds = args
    ens = load_or_realize(default_household_dir(ref.household_id),
                          ref.household_id, ref.episode_id, ref.n_days,
                          n_seeds, DEFAULT_REALIZATION_CACHE)
    return f"{ref.household_id}: {ens.n_seeds} seeds, {len(ens.objects)} objects"


def stage_realize(refs: Sequence[EpisodeRef], n_seeds: int,
                  workers: int) -> None:
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        for line in pool.map(_realize_one, [(r, n_seeds) for r in refs]):
            logger.info("realize: %s", line)


# --------------------------------------------------------- passive fleet

PASSIVE_CELL = ("OracleBelief", "NeverSense", "bank")


def passive_fleet(cell_dir: pathlib.Path, refs: Sequence[EpisodeRef],
                  seed: int, workers: int, config: OracleConfig
                  ) -> List[Dict[str, Any]]:
    """OracleBelief at ``config`` under NeverSense at every bank's own
    budget; one row per question (household, day, ESS after the
    question, correct, and whether the routine oracle's no-observation
    answer was correct). The question dump lands under ``cell_dir``."""
    tasks = [GridTask("OracleBelief", config.spec(), POLICIES[0],
                      ref.budget_per_day, ref, seed,
                      part_path(cell_dir, PASSIVE_CELL, ref.episode_id))
             for ref in refs]
    run_pool(run_plain_task, tasks, workers)
    merge_parts(cell_dir)
    dump = cell_dir / "questions" / ("__".join(PASSIVE_CELL) + ".jsonl.gz")
    rows: List[Dict[str, Any]] = []
    for r in read_dump(dump):
        rows.append({"household_id": r["household_id"],
                     "day_index": int(r["day_index"]),
                     "ess": round(float(r.get("ess", 0.0)), 4),
                     "correct": int(r["correct"]),
                     "routine_correct": int(
                         r.get("routine_argmax") == r["truth_receptacle"])})
    rows.sort(key=lambda r: (r["household_id"], r["day_index"]))
    return rows


def _quantile(sorted_vals: Sequence[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(len(sorted_vals) - 1, max(0, int(round(q * (len(sorted_vals) - 1)))))
    return float(sorted_vals[idx])


def summarize_rows(rows: Sequence[Dict[str, Any]]) -> Dict[str, float]:
    ess = sorted(float(r["ess"]) for r in rows)
    n = len(rows)
    return {"n": n, "median_ess": _quantile(ess, 0.5),
            "q25_ess": _quantile(ess, 0.25), "q75_ess": _quantile(ess, 0.75),
            "p10_ess": _quantile(ess, 0.1), "p90_ess": _quantile(ess, 0.9),
            "min_ess": ess[0] if ess else 0.0, "max_ess": ess[-1] if ess else 0.0,
            "accuracy": (sum(r["correct"] for r in rows) / n) if n else 0.0,
            "routine_accuracy": (sum(r["routine_correct"] for r in rows) / n)
            if n else 0.0}


# ------------------------------------------------------------------ sweep

SWEEP_FIELDS = ["config", "eps", "half_life_h", "subset", "n", "median_ess",
                "q25_ess", "q75_ess", "p10_ess", "p90_ess", "max_ess",
                "accuracy", "routine_accuracy", "eligible"]


def select_config(table: Sequence[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """The calibration row with the largest passive accuracy among those
    whose calibration median ESS clears ``ESS_STOP``; ties go to the
    larger ESS. None when no setting clears the gate."""
    eligible = [r for r in table
                if r["subset"] == "calibration" and r["eligible"]]
    if not eligible:
        return None
    return max(eligible, key=lambda r: (r["accuracy"], r["median_ess"]))


def stage_sweep(out: pathlib.Path, refs: Sequence[EpisodeRef],
                split: Dict[str, str], seed: int, workers: int,
                configs: Sequence[OracleConfig] = SWEEP_CONFIGS
                ) -> Optional[OracleConfig]:
    table: List[Dict[str, Any]] = []
    for config in configs:
        rows = passive_fleet(out / "sweep" / config.slug, refs, seed, workers,
                             config)
        write_csv(rows, out / "sweep" / config.slug / "ess_passive.csv")
        for subset in SUBSETS:
            sub = [r for r in rows
                   if subset == "fleet" or split[r["household_id"]] == subset]
            stats = summarize_rows(sub)
            table.append({"config": config.slug, "eps": config.eps,
                          "half_life_h": ("" if config.half_life_h is None
                                          else config.half_life_h),
                          "subset": subset, **stats,
                          "eligible": int(stats["median_ess"] >= ESS_STOP)})
        cal = next(r for r in table
                   if r["config"] == config.slug and r["subset"] == "calibration")
        logger.info("sweep: %s calibration median ESS %.2f accuracy %.3f "
                    "(routine %.3f)", config.label, cal["median_ess"],
                    cal["accuracy"], cal["routine_accuracy"])
    for r in table:
        for k in ("median_ess", "q25_ess", "q75_ess", "p10_ess", "p90_ess",
                  "max_ess"):
            r[k] = round(r[k], 3)
        for k in ("accuracy", "routine_accuracy"):
            r[k] = round(r[k], 6)
    write_csv(table, out / "sweep.csv", SWEEP_FIELDS)
    chosen = select_config(table)
    selected = (None if chosen is None else
                OracleConfig(float(chosen["eps"]),
                             None if chosen["half_life_h"] == "" else
                             float(chosen["half_life_h"])))
    _write_sweep_md(out, table, split, selected)
    if selected is None:
        (out / "selected.json").unlink(missing_ok=True)
        logger.warning("sweep: no setting clears the ESS gate on the "
                       "calibration households")
    else:
        (out / "selected.json").write_text(
            json.dumps(selected.to_json(), indent=2) + "\n")
        logger.info("sweep: selected %s", selected.label)
    return selected


def _write_sweep_md(out: pathlib.Path, table: Sequence[Dict[str, Any]],
                    split: Dict[str, str],
                    selected: Optional[OracleConfig]) -> None:
    n_cal = sum(1 for v in split.values() if v == "calibration")
    n_test = sum(1 for v in split.values() if v == "test")
    by = {(r["config"], r["subset"]): r for r in table}
    configs = list(dict.fromkeys(r["config"] for r in table))
    routine = by[(configs[0], "calibration")]["routine_accuracy"]
    routine_test = by[(configs[0], "test")]["routine_accuracy"]
    lines = ["# OracleBelief weighting sweep: eps x forgetting half-life, "
             "passive diet, 20 fleet banks", "",
             f"Every setting replays NeverSense at each bank's own budget on "
             f"all 20 banks ({DEFAULT_ORACLE_SEEDS} realizations). ESS is "
             f"``1 / sum(w_i^2)`` after each question. The setting is chosen "
             f"on the {n_cal} calibration households only: the largest "
             f"passive accuracy among settings whose calibration median ESS "
             f"is at least {ESS_STOP:g}. The {n_test} test households are "
             f"shown for the record and were not consulted. The routine "
             f"oracle's no-observation answer (same realizations, uniform "
             f"weights) scores {routine:.3f} on calibration and "
             f"{routine_test:.3f} on test. Per-question rows per setting in "
             f"`sweep/<setting>/ess_passive.csv`; this table in `sweep.csv`.",
             "", "| eps | half-life | cal median ESS | cal p10 / p90 | "
             "cal accuracy | gate | test median ESS | test accuracy |",
             "|---|---|---|---|---|---|---|---|"]
    for slug in configs:
        c, t = by[(slug, "calibration")], by[(slug, "test")]
        hl = "none" if c["half_life_h"] == "" else f"{float(c['half_life_h']):g} h"
        mark = " **(selected)**" if (selected is not None
                                     and selected.slug == slug) else ""
        lines.append(f"| {c['eps']:g} | {hl} | {c['median_ess']:.2f} | "
                     f"{c['p10_ess']:.2f} / {c['p90_ess']:.2f} | "
                     f"{c['accuracy']:.3f} | "
                     f"{'pass' if c['eligible'] else 'STOP'} | "
                     f"{t['median_ess']:.2f} | {t['accuracy']:.3f}{mark} |")
    if selected is None:
        verdict = (f"No setting reaches a calibration median ESS of "
                   f"{ESS_STOP:g}; nothing selected, the grid must not run.")
    else:
        c = by[(selected.slug, "calibration")]
        verdict = (f"Selected: {selected.label} (calibration median ESS "
                   f"{c['median_ess']:.2f}, passive accuracy "
                   f"{c['accuracy']:.3f} vs routine {routine:.3f}). Written "
                   f"to `selected.json`; `ess_gate`, `grid` and `report` "
                   f"use it unless `--eps`/`--half-life-h` override.")
    lines += ["", f"**Selection.** {verdict}"]
    (out / "sweep.md").write_text("\n".join(lines) + "\n")


# --------------------------------------------------------------- ess gate

def stage_ess_gate(out: pathlib.Path, refs: Sequence[EpisodeRef], seed: int,
                   workers: int, config: OracleConfig) -> float:
    """Passive OracleBelief on every fleet bank; per-question ESS."""
    rows = passive_fleet(out / "ess_gate", refs, seed, workers, config)
    write_csv(rows, out / "ess_passive.csv")
    fleet = summarize_rows(rows)
    median = fleet["median_ess"]
    per_hh: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        per_hh.setdefault(r["household_id"], []).append(r)
    lines = [f"# ESS gate: OracleBelief under the passive diet, 20 fleet banks",
             "",
             f"Effective sample size ``1 / sum(w_i^2)`` of the realization "
             f"weights ({DEFAULT_ORACLE_SEEDS} seeds; {config.label}), read "
             f"after every question of a NeverSense replay at the bank's own "
             f"budget. Per-question values in `ess_passive.csv`.", "",
             f"Fleet: {fleet['n']} questions, median ESS **{median:.2f}**, "
             f"quartiles {fleet['q25_ess']:.2f} / {fleet['q75_ess']:.2f}, "
             f"min {fleet['min_ess']:.2f}, max {fleet['max_ess']:.2f}; "
             f"passive accuracy {fleet['accuracy']:.3f} (routine oracle "
             f"{fleet['routine_accuracy']:.3f}). Stop threshold: median < "
             f"{ESS_STOP:g}.",
             "", "| household | n | median ESS | p10 | p90 | max | accuracy |",
             "|---|---|---|---|---|---|---|"]
    for hh, sub in sorted(per_hh.items()):
        s = summarize_rows(sub)
        lines.append(f"| {hh} | {s['n']} | {s['median_ess']:.2f} | "
                     f"{s['p10_ess']:.2f} | {s['p90_ess']:.2f} | "
                     f"{s['max_ess']:.2f} | {s['accuracy']:.3f} |")
    by_day: Dict[int, List[Dict[str, Any]]] = {}
    for r in rows:
        by_day.setdefault(int(r["day_index"]), []).append(r)
    lines += ["", "| query day | n | median ESS | accuracy |", "|---|---|---|---|"]
    for day, sub in sorted(by_day.items()):
        s = summarize_rows(sub)
        lines.append(f"| {day} | {s['n']} | {s['median_ess']:.2f} | "
                     f"{s['accuracy']:.3f} |")
    verdict = ("STOP: median ESS below the threshold; the grid was not run. "
               "The fix (eps, matching granularity, seed count) is an owner "
               "decision." if median < ESS_STOP else
               "PASS: the grid may run.")
    lines += ["", f"**Verdict.** {verdict}"]
    (out / "ess_gate.md").write_text("\n".join(lines) + "\n")
    logger.info("ess_gate: fleet median ESS %.3f (%s)", median, verdict[:4])
    return median


# ------------------------------------------------------------------- grid

def representative_tasks(out: pathlib.Path, refs: Sequence[EpisodeRef],
                         beliefs: Sequence[str], policies: Sequence[PolicySpec],
                         budgets: Sequence[Optional[int]], seed: int,
                         fitted: Optional[Dict[str, Dict[str, Any]]] = None,
                         specs: Optional[Dict[str, Dict[str, Any]]] = None
                         ) -> List[GridTask]:
    specs = specs or {k: dict(v) for k, v in BELIEF_SPECS.items()}
    tasks = []
    for belief_key in beliefs:
        for policy in policies:
            for budget in budgets:
                for ref in refs:
                    task = GridTask(belief_key, dict(specs[belief_key]),
                                    policy, budget, ref, seed, "",
                                    fitted=dict((fitted or {}).get(belief_key, {})))
                    task.part_path = part_path(out, task.cell, ref.episode_id)
                    tasks.append(task)
    return tasks


def llm_skip_note(refs: Sequence[EpisodeRef]) -> Optional[str]:
    """None when every test episode's queried predictions are answerable
    from the cache; otherwise the reason the LLM cells are skipped."""
    fractions = {r.household_id: llm_pending_fraction(r) for r in refs}
    worst = max(fractions.values())
    if worst == 0.0:
        return None
    return (f"LLMBelief cells skipped: the cached completions "
            f"(`reports/baselines/llm_floor/completions.jsonl`, a stratified "
            f"sample of the passive questions) leave "
            f"{min(fractions.values()):.0%}-{worst:.0%} of the queried "
            f"predictions of a passive replay unanswered per test household, "
            f"and any sensing changes the prompts further; running the cell "
            f"would need new LLM calls.")


def stage_grid(out: pathlib.Path, refs: Sequence[EpisodeRef],
               split: Dict[str, str], seed: int, workers: int,
               config: OracleConfig) -> None:
    test = [r for r in refs if split[r.household_id] == "test"]
    beliefs = list(BELIEF_SPECS)
    note = llm_skip_note(test)
    if note:
        beliefs.remove("LLMBelief")
        (out / "llm_skip.md").write_text(note + "\n")
        logger.warning(note)
    tasks = representative_tasks(out, test, beliefs, POLICIES,
                                 list(REPRESENTATIVE_BUDGETS), seed,
                                 specs=belief_specs_with(config))
    # PerpetuaStar episodes take minutes; schedule them first so the pool
    # never ends on a long tail.
    tasks.sort(key=lambda t: (t.belief_key != "PerpetuaStar",
                              t.belief_key != "OracleBelief"))
    results = run_pool(run_plain_task, tasks, workers)
    merge_parts(out)
    grid, days = aggregate_rows(results)
    write_csv(grid, out / "grid.csv", GRID_FIELDS)
    write_csv(days, out / "accuracy_by_day.csv", DAY_FIELDS)
    provenance(out, refs, split, seed=seed, beliefs=beliefs,
               policies=[p.slug for p in POLICIES],
               budgets=list(REPRESENTATIVE_BUDGETS),
               oracle_seeds=DEFAULT_ORACLE_SEEDS, llm_skipped=bool(note),
               oracle_config=config.to_json())


# ----------------------------------------------------------------- report

def _grid_index(rows: Sequence[Dict[str, str]]
                ) -> Dict[Tuple[str, str, str], Dict[str, str]]:
    return {(r["belief"], r["policy"], r["budget"]): r for r in rows}


def _passive_vs_routine(out: pathlib.Path) -> Dict[str, Any]:
    """OracleBelief passive accuracy vs the routine oracle's answer on the
    same questions (both from the NeverSense dump, which carries
    ``routine_argmax``), overall, by household and by ESS band."""
    dumps = sorted((out / "questions").glob("OracleBelief__NeverSense__*.jsonl.gz"))
    if not dumps:
        return {}
    n = ob = ro = both = 0
    by_hh: Dict[str, List[int]] = {}
    ess_correct: Dict[str, List[int]] = {"ess<=1.5": [], "1.5<ess<=5": [],
                                          "5<ess<=50": [], "ess>50": []}
    for row in read_dump(dumps[0]):
        n += 1
        o = int(row["correct"])
        r = int(row.get("routine_argmax") == row["truth_receptacle"])
        ob += o
        ro += r
        both += int(o and r)
        cell = by_hh.setdefault(row["household_id"], [0, 0, 0])
        cell[0] += 1
        cell[1] += o
        cell[2] += r
        e = float(row.get("ess", 0.0))
        key = ("ess<=1.5" if e <= 1.5 else "1.5<ess<=5" if e <= 5
               else "5<ess<=50" if e <= 50 else "ess>50")
        ess_correct[key].append(o)
    return {"n": n, "oracle_belief": ob / n, "routine": ro / n,
            "both": both / n, "by_household": by_hh,
            "by_ess": {k: (len(v), sum(v) / len(v) if v else 0.0)
                       for k, v in ess_correct.items()}}


def stage_report(out: pathlib.Path, config: OracleConfig) -> None:
    grid = read_csv(out / "grid.csv")
    idx = _grid_index(grid)
    beliefs = list(dict.fromkeys(r["belief"] for r in grid))
    budgets = [str(b) for b in REPRESENTATIVE_BUDGETS]
    real = [b for b in beliefs if b != "OracleBelief"]
    note_path = out / "llm_skip.md"
    lines = ["# OracleBelief on the representative grid", "",
             "Inputs: the 10 test households of `results/conformal_sweep_v2/` "
             "(split seed 0), budgets 24 and 90 senses per day, policies "
             "NeverSense and SequentialSearch, beliefs "
             + ", ".join(beliefs) + ". OracleBelief: the routine oracle's "
             f"{DEFAULT_ORACLE_SEEDS} re-realizations of each household's "
             "program (seeds 1001-1800; the bank's seed-0 world excluded), "
             f"weighted by consistency with the observation history "
             f"({config.label}; soft weights). Produced by "
             "`python -m baselines.oracle_posterior_study`; raw numbers, "
             "no intervals. Per-day accuracy for every cell is in "
             "`accuracy_by_day.csv`.", ""]
    if (out / "sweep.md").exists():
        lines += ["The setting was chosen by the sweep in `sweep.md` on the "
                  "calibration households only (largest passive accuracy "
                  f"among settings with median ESS >= {ESS_STOP:g}); the test "
                  "households below never entered that choice.", ""]
    if note_path.exists():
        lines += [note_path.read_text().strip(), ""]

    # 1. Policy separation.
    lines += ["## 1. Do policies separate more or less on the oracle belief?",
              "", "Task accuracy, NeverSense -> SequentialSearch, and the "
              "difference (the policy's contribution), per belief and budget. "
              "Senses per question in parentheses for SequentialSearch.", "",
              "| belief | budget | NeverSense | SequentialSearch | separation |",
              "|---|---|---|---|---|"]
    seps: Dict[Tuple[str, str], float] = {}
    for b in beliefs:
        for budget in budgets:
            ns = idx.get((b, "NeverSense", budget))
            ss = idx.get((b, "SequentialSearch", budget))
            if not ns or not ss:
                continue
            sep = float(ss["task_accuracy"]) - float(ns["task_accuracy"])
            seps[(b, budget)] = sep
            lines.append(f"| {b} | {budget} | {fmt(ns['task_accuracy'])} | "
                         f"{fmt(ss['task_accuracy'])} "
                         f"({fmt(ss['senses_per_question'], 2)}) | "
                         f"{sep:+.3f} |")
    if "OracleBelief" in beliefs:
        for budget in budgets:
            o = seps.get(("OracleBelief", budget))
            rs = [seps[(b, budget)] for b in real if (b, budget) in seps]
            if o is not None and rs:
                lines.append("")
                lines.append(
                    f"At budget {budget}: separation on OracleBelief "
                    f"{o:+.3f} vs real beliefs {min(rs):+.3f} to {max(rs):+.3f} "
                    f"(mean {sum(rs) / len(rs):+.3f}) — policies separate "
                    f"{'LESS' if o < min(rs) else 'MORE' if o > max(rs) else 'within the real range'} "
                    f"on the oracle belief.")

    # 2. Gap split.
    lines += ["", "## 2. Oracle vs best real belief per budget: belief error "
              "vs decision error", "",
              "The passive gap (NeverSense: OracleBelief minus the best real "
              "belief) is belief error — what better routine knowledge alone "
              "buys with no sensing. The search gap (SequentialSearch, same "
              "budget) is what remains once the policy spends the budget; "
              "the difference between the two is what sensing recovers of "
              "the belief gap (decision error, negative when sensing closes "
              "it).", "",
              "| budget | best real (passive) | oracle passive | passive gap | "
              "best real (search) | oracle search | search gap | "
              "recovered by sensing |", "|---|---|---|---|---|---|---|---|"]
    beats: List[str] = []
    if "OracleBelief" in beliefs:
        for budget in budgets:
            pas = {b: float(idx[(b, "NeverSense", budget)]["task_accuracy"])
                   for b in real if (b, "NeverSense", budget) in idx}
            srch = {b: float(idx[(b, "SequentialSearch", budget)]["task_accuracy"])
                    for b in real if (b, "SequentialSearch", budget) in idx}
            if not pas or not srch:
                continue
            bp = max(pas, key=lambda b: pas[b])
            bs = max(srch, key=lambda b: srch[b])
            op = float(idx[("OracleBelief", "NeverSense", budget)]["task_accuracy"])
            os_ = float(idx[("OracleBelief", "SequentialSearch", budget)]["task_accuracy"])
            pg, sg = op - pas[bp], os_ - srch[bs]
            lines.append(f"| {budget} | {bp} {pas[bp]:.3f} | {op:.3f} | {pg:+.3f} | "
                         f"{bs} {srch[bs]:.3f} | {os_:.3f} | {sg:+.3f} | "
                         f"{pg - sg:+.3f} |")
            beats.append(f"- Budget {budget}, NeverSense: OracleBelief "
                         f"{'beats' if pg > 0 else 'does NOT beat'} the best "
                         f"real belief ({bp}) by {pg:+.3f}.")
            beats.append(f"- Budget {budget}, SequentialSearch: OracleBelief "
                         f"{'beats' if sg > 0 else 'does NOT beat'} the best "
                         f"real belief ({bs}) by {sg:+.3f}.")
        lines += ["", "Cell by cell:", ""] + beats
    else:
        lines.append("| (OracleBelief not in the grid) | | | | | | | |")

    # 3. ESS + passive vs routine.
    lines += ["", "## 3. ESS distribution, and does conditioning on "
              "observations buy anything?", ""]
    gate = out / "ess_gate.md"
    if gate.exists():
        body = gate.read_text().splitlines()
        fleet_line = next((l for l in body if l.startswith("Fleet:")), "")
        lines += [f"Passive ESS on the 20 fleet banks (`ess_gate.md`, "
                  f"`ess_passive.csv`): {fleet_line}", ""]
    ess_rows = [r for r in grid if r["belief"] == "OracleBelief"]
    if ess_rows:
        lines += ["| policy | budget | median ESS after the question |",
                  "|---|---|---|"]
        lines += [f"| {r['policy']} | {r['budget']} | {r['median_ess']} |"
                  for r in ess_rows]
    pvr = _passive_vs_routine(out)
    if pvr:
        lines += ["", f"OracleBelief passive (NeverSense, test households, "
                  f"n={pvr['n']}) vs the routine oracle's no-observation "
                  f"modal answer on the same questions (same {DEFAULT_ORACLE_SEEDS} "
                  f"realizations, uniform weights):", "",
                  "| predictor | accuracy |", "|---|---|",
                  f"| routine oracle (no observations) | {pvr['routine']:.3f} |",
                  f"| OracleBelief (observation-weighted) | {pvr['oracle_belief']:.3f} |",
                  f"| both right | {pvr['both']:.3f} |", "",
                  "| household | n | routine | OracleBelief |", "|---|---|---|---|"]
        for hh, (n, o, r) in sorted(pvr["by_household"].items()):
            lines.append(f"| {hh} | {n} | {r / n:.3f} | {o / n:.3f} |")
        lines += ["", "OracleBelief accuracy by the ESS at the question:", "",
                  "| ESS band | n | accuracy |", "|---|---|---|"]
        for k, (n, acc) in pvr["by_ess"].items():
            lines.append(f"| {k} | {n} | {acc:.3f} |")
        delta = pvr["oracle_belief"] - pvr["routine"]
        lines += ["", f"Conditioning on observations changes passive accuracy "
                  f"by {delta:+.3f} against the same ensemble unweighted."]
    (out / "findings.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


# ------------------------------------------------------------------- main

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--stage", nargs="+",
                        choices=("realize", "sweep", "ess_gate", "grid",
                                 "report"), required=True)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--n-seeds", type=int, default=DEFAULT_ORACLE_SEEDS)
    parser.add_argument("--eps", type=float, default=None,
                        help="OracleBelief eps (overrides selected.json)")
    parser.add_argument("--half-life-h", type=float, default=None,
                        help="OracleBelief forgetting half-life in hours; "
                             "0 or negative means none (overrides "
                             "selected.json)")
    parser.add_argument("--force-grid", action="store_true",
                        help="run the grid even when the ESS gate stopped")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                        format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("baselines").setLevel(logging.INFO)
    refs = episode_index(fleet_bank_paths())
    split = reference_split(refs)
    args.out.mkdir(parents=True, exist_ok=True)
    for stage in args.stage:
        config = resolve_config(args.out, args.eps, args.half_life_h)
        if stage == "realize":
            stage_realize(refs, args.n_seeds, args.workers)
        elif stage == "sweep":
            if stage_sweep(args.out, refs, split, args.seed,
                           args.workers) is None:
                print("sweep: no setting clears the ESS gate on the "
                      "calibration households (see sweep.md)", file=sys.stderr)
                return 2
        elif stage == "ess_gate":
            median = stage_ess_gate(args.out, refs, args.seed, args.workers,
                                    config)
            if median < ESS_STOP and not args.force_grid:
                print(f"ESS gate: fleet median {median:.2f} < {ESS_STOP:g}; "
                      f"stopping before the grid (see ess_gate.md)",
                      file=sys.stderr)
                return 2
        elif stage == "grid":
            gate = args.out / "ess_gate.md"
            if gate.exists() and "STOP" in gate.read_text() and not args.force_grid:
                print("ESS gate stopped this study; pass --force-grid to "
                      "override (owner decision)", file=sys.stderr)
                return 2
            stage_grid(args.out, refs, split, args.seed, args.workers, config)
        elif stage == "report":
            stage_report(args.out, config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
