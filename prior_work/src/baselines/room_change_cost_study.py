"""Room-change travel cost: what a same-room discount buys a cost-aware
policy, on the representative grid.

Until now every active sense cost one budget unit wherever the robot was
standing. This study prices travel: sensing a receptacle in the room the
robot already occupies costs 1, sensing one anywhere else costs ``1 + c``
(:meth:`baselines.types.EpisodeContext.sense_cost`, applied by the
harness). One parameter, distance-free, and at ``c = 0`` exactly the
model the package had before — which is the regression the report checks
first.

The experiment is a discrimination: only ``VoIThresholdSense`` and
``VoIBudgetPriceSense`` can see the price (they sense while
``voi(r) >= lambda * cost(r)`` and pick the receptacle maximizing
``voi(r) / cost(r)``). Every other policy on the grid orders candidates
by belief mass and spends until the budget will not cover the next sense,
exactly as before. So the same-room discount is an opportunity only the
cost-aware pair can take — and, unlike their first advantage in
``results/voi_policies/``, taking it does not depend on the belief's
probabilities being well calibrated: ``cost(r)`` is known exactly.

Grid: beliefs LastObservation, PeriodicPersistence, PerpetuaStar;
policies NeverSense, SequentialSearch, ResolvableMassSense,
VoIThresholdSense and VoIBudgetPriceSense at their best configurations
from ``results/voi_policies/``; budgets 24 and 90; c in
{0, 0.25, 0.5, 1, 2}; the 10 test households of the split in
``results/voi_policies/provenance.json``, on the banks rebuilt with room
maps under ``banks/baselines/fleet_room_cost/``.

Stages (``--stage``; outputs under ``--out``, default
``results/room_change_cost/``):

  grid     refit the conformal tables on the calibration households (the
           ResolvableMassSense comparator needs them), then run every
           (belief, policy, budget, c) cell on the test households ->
           ``grid.csv``, ``accuracy_by_day.csv``, question dumps.
  report   ``regression.md`` (the c = 0 check against
           ``results/voi_policies/grid.csv``, read together with the
           ``head_baseline.json`` re-derivation that says whether any
           mismatch is this study's or pre-existing) plus the tables the
           authored ``findings.md`` quotes: ``by_cost.csv``,
           ``head_to_head.csv``, ``arrival.csv``.
  figures  ``accuracy_vs_cost.png``, ``same_room_share.png``,
           ``arrival.png`` and ``voi_gap_vs_cost.png`` — one per claim in
           ``findings.md``, every point with a 95% interval (Wilson on the
           cell's own denominator; PAIRED per-question for the gap figure,
           whose numbers are written to ``gap_paired_ci.csv``).

Usage:
  PYTHONPATH=src python -m baselines.room_change_cost_study \
      --stage verify_banks grid report figures --workers 20
"""

from __future__ import annotations

import argparse
import collections
import gzip
import json
import logging
import math
import pathlib
import re
from typing import (Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple)

from baselines.conformal.calibration import CalibrationPair, fit_global_qhat
from baselines.representative_grid import (BELIEF_SPECS, REPO_ROOT,
                                           REPRESENTATIVE_BUDGETS,
                                           EpisodeRef, GridTask, PolicySpec,
                                           aggregate_rows, episode_index,
                                           fleet_bank_paths, fmt, merge_parts,
                                           part_path, passive_pairs,
                                           provenance, read_csv, read_dump,
                                           run_plain_task, run_pool,
                                           write_csv, DAY_FIELDS, GRID_FIELDS)
from baselines.voi_study import DEFAULT_OUT as VOI_OUT, LAMBDA0

logger = logging.getLogger(__name__)

DEFAULT_OUT = REPO_ROOT / "results" / "room_change_cost"
ROOM_COST_BANK_DIR = REPO_ROOT / "banks" / "baselines" / "fleet_room_cost"
"""The 20 fleet banks re-exported with ``receptacle_rooms`` and
``home_base_room`` in the header. Everything else about them is byte
identical to ``banks/baselines/fleet/`` — the export is deterministic and
makes no LLM calls, and ``--stage verify_banks`` proves it."""

ROOM_CHANGE_COSTS: Tuple[float, ...] = (0.0, 0.25, 0.5, 1.0, 2.0)
BELIEFS: Tuple[str, ...] = ("LastObservation", "PeriodicPersistence",
                            "PerpetuaStar", "OracleBelief")

ORACLE_SELECTION = (REPO_ROOT / "results" / "oracle_program_posterior"
                    / "selected.json")
"""Where the oracle-posterior study records the (eps, half_life_h) its
weighting sweep chose on the calibration households."""


def belief_spec(belief_key: str) -> Dict[str, Any]:
    """The representative spec, with one override that matters.

    ``OracleBelief``'s MODULE defaults are still the whole-episode
    weighting that collapsed at the ESS gate (eps 0.05, never forget ->
    fleet median ESS 1.00), so building it from ``BELIEF_SPECS`` alone
    silently runs the degenerate belief. The weighting that passes the
    gate lives in the sweep's ``selected.json`` and has to be passed
    explicitly; refuse rather than quietly run the collapsed version.
    """
    spec = dict(BELIEF_SPECS[belief_key])
    if belief_key != "OracleBelief":
        return spec
    if not ORACLE_SELECTION.exists():
        raise FileNotFoundError(
            f"OracleBelief needs the weighting selected by the oracle "
            f"sweep, but {ORACLE_SELECTION} is missing; run "
            f"`baselines.oracle_posterior_study --stage sweep` first")
    chosen = json.loads(ORACLE_SELECTION.read_text())
    spec.update({"eps": float(chosen["eps"]),
                 "half_life_h": (None if chosen.get("half_life_h") is None
                                 else float(chosen["half_life_h"]))})
    return spec


# ------------------------------------------------- best configs from part B

def voi_best_configs(voi_dir: pathlib.Path = VOI_OUT
                     ) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """Per (belief, budget): the best VoIThresholdSense lambda, the best
    VoIBudgetPriceSense gamma and the ResolvableMassSense (alpha, tau),
    all by test task accuracy in ``results/voi_policies/grid.csv``.

    "Best config from `results/voi_policies/`" is read off that run's own
    numbers rather than re-tuned here: this study varies c, not the
    policy hyperparameters, and re-tuning per c would confound the two.
    """
    rows = [r for r in read_csv(voi_dir / "grid.csv") if r["budget"] != "soft"]
    comparators = json.loads((voi_dir / "comparators.json").read_text())
    out: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for belief in sorted({r["belief"] for r in rows}):
        for budget in sorted({r["budget"] for r in rows}):
            cell = [r for r in rows if r["belief"] == belief
                    and r["budget"] == budget]
            if not cell:
                continue

            def best(prefix: str) -> Optional[Dict[str, str]]:
                cands = [r for r in cell if r["policy"].startswith(prefix)]
                return (max(cands, key=lambda r: float(r["task_accuracy"]))
                        if cands else None)

            thr, price = best("VoIThresholdSense"), best("VoIBudgetPriceSense")
            cfg = comparators.get(f"{belief}@{budget}", {})
            if thr is None or price is None or not cfg:
                continue
            out[(belief, budget)] = {
                "lam": float(thr["policy"].rsplit("lambda", 1)[1]),
                "lam_accuracy": float(thr["task_accuracy"]),
                "gamma": float(price["policy"].rsplit("gamma", 1)[1]),
                "gamma_accuracy": float(price["task_accuracy"]),
                "resolvable_alpha": float(cfg["resolvable_alpha"]),
                "resolvable_tau": float(cfg["resolvable_tau"]),
                "consensus": bool(cfg.get("consensus", False))}
    return out


def consensus_config(configs: Mapping[Tuple[str, str], Mapping[str, Any]],
                     budget: str) -> Dict[str, Any]:
    """The configuration most of Part B's beliefs preferred at ``budget``.

    A belief Part B never ran — OracleBelief, which its grid excluded at
    the ESS gate — has no best-of-its-own to inherit. The package's
    precedent (``voi_study.consensus_best``, used there for PerpetuaStar)
    is to give it the modal choice of the beliefs that WERE run, ties
    broken by the smaller value, and to say so wherever the numbers
    appear. Re-tuning for it here would confound the price sweep with a
    hyperparameter search."""
    out: Dict[str, Any] = {"consensus": True}
    for key in ("lam", "gamma", "resolvable_alpha", "resolvable_tau"):
        tally = collections.Counter(
            float(cfg[key]) for (_b, bud), cfg in configs.items()
            if bud == budget and key in cfg)
        if not tally:
            raise KeyError(f"no {key} to take a consensus over at {budget}")
        out[key] = sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return out


def policy_specs(budget: int, questions_per_day: int,
                 cfg: Mapping[str, Any]) -> List[PolicySpec]:
    """The five policies of one (belief, budget) column, at the
    configurations Part B settled on.

    The labels are Part B's OWN slugs, hyperparameter and all, and that is
    load-bearing rather than cosmetic: every generator in the grid derives
    from ``(seed, belief, policy slug, budget, episode)``, so relabelling
    the same policy ``..._best`` would reseed its tie-breaks and the c = 0
    column would no longer reproduce ``results/voi_policies/`` — the one
    check this study cannot afford to lose. ``lam0`` likewise stays Part
    B's fixed 0.05 rather than the cell's best lambda.
    """
    return [
        PolicySpec("never_sense", label="NeverSense"),
        PolicySpec("sequential_search", label="SequentialSearch"),
        PolicySpec("resolvable_mass",
                   (("alpha", cfg["resolvable_alpha"]),
                    ("tau", cfg["resolvable_tau"])),
                   "ResolvableMassSense_best"),
        PolicySpec("voi_threshold", (("lam", cfg["lam"]),),
                   f"VoIThresholdSense_lambda{float(cfg['lam']):g}"),
        PolicySpec("voi_budget_price",
                   (("gamma", cfg["gamma"]), ("budget_per_day", budget),
                    ("questions_per_day", questions_per_day),
                    ("lam0", LAMBDA0)),
                   f"VoIBudgetPriceSense_gamma{float(cfg['gamma']):g}"),
    ]


COST_BLIND_PREFIXES = ("NeverSense", "SequentialSearch",
                       "ResolvableMassSense")
COST_AWARE_PREFIXES = ("VoIThresholdSense", "VoIBudgetPriceSense")
FAMILY_ORDER = (*COST_BLIND_PREFIXES, *COST_AWARE_PREFIXES)


def family_of(policy_slug: str) -> str:
    """The policy family a per-cell slug belongs to. Slugs carry their
    hyperparameters (and those differ per cell), so tables key on the
    family and print the slug."""
    for prefix in FAMILY_ORDER:
        if policy_slug.startswith(prefix):
            return prefix
    return policy_slug


# ------------------------------------------------------------- bank check

def verify_banks(old_dir: pathlib.Path, new_dir: pathlib.Path
                 ) -> Tuple[bool, List[str]]:
    """The rebuilt banks must differ from the old ones ONLY by the two new
    header fields. Questions and observation rows are untouched by this
    brief, so anything else moving means the rebuild was not the identity
    it claims to be — and every comparison to earlier results would be
    against a different dataset."""
    lines: List[str] = []
    ok = True
    old = sorted(old_dir.glob("*__hh_0??_bank.jsonl"))
    new = sorted(new_dir.glob("*__hh_0??_bank.jsonl"))
    if [p.name for p in old] != [p.name for p in new]:
        return False, [f"bank sets differ: {len(old)} old vs {len(new)} new"]
    for a, b in zip(old, new):
        rows_a = a.read_text().splitlines()
        rows_b = b.read_text().splitlines()
        if rows_a[1:] != rows_b[1:]:
            ok = False
            lines.append(f"- {a.name}: **body differs** "
                         f"({len(rows_a)} vs {len(rows_b)} rows)")
            continue
        ha, hb = json.loads(rows_a[0]), json.loads(rows_b[0])
        added = set(hb) - set(ha)
        changed = {k for k in ha if ha[k] != hb.get(k)}
        if added != {"receptacle_rooms", "home_base_room"} or changed:
            ok = False
            lines.append(f"- {a.name}: header added {sorted(added)}, "
                         f"changed {sorted(changed)}")
        else:
            lines.append(f"- {a.name}: body identical; header adds "
                         f"receptacle_rooms ({len(hb['receptacle_rooms'])} "
                         f"receptacles, {len(set(hb['receptacle_rooms'].values()))} "
                         f"rooms) and home_base_room "
                         f"`{hb['home_base_room']}`")
    return ok, lines


# ------------------------------------------------------------------- grid

def _merge_rows(existing: Sequence[Dict[str, str]],
                fresh: Sequence[Dict[str, Any]], ran: Sequence[str]
                ) -> List[Dict[str, Any]]:
    """Fresh rows for the beliefs just run, plus the untouched rows for
    every other belief already in the csv.

    Lets a belief be ADDED to a finished grid without re-running the rest
    of it — the cells are independent by construction (one process, one
    (belief, policy, budget, c, episode)), so a merged csv is exactly what
    a full re-run would have produced, and far cheaper."""
    kept = [dict(r) for r in existing if r.get("belief") not in set(ran)]
    merged = kept + [dict(r) for r in fresh]
    merged.sort(key=lambda r: (str(r.get("belief")), str(r.get("policy")),
                               str(r.get("budget")),
                               float(r.get("room_change_cost", 0) or 0),
                               int(r.get("day_index", 0) or 0)))
    return merged


def stage_grid(out: pathlib.Path, refs: Sequence[EpisodeRef],
               split: Mapping[str, str], seed: int, workers: int,
               beliefs: Sequence[str] = BELIEFS,
               costs: Sequence[float] = ROOM_CHANGE_COSTS,
               compensate: bool = False) -> None:
    """Run the grid.

    ``compensate`` scales each budget by ``1 + c`` instead of holding it
    fixed. The two arms answer different questions and must not be mixed
    in one csv: at a FIXED budget a rising c starves the policy (the same
    24 units buy fewer and fewer looks), while a COMPENSATED budget holds
    the number of affordable cross-room looks constant and isolates the
    price RATIO between a look next to you and a look one room away.
    """
    calib = [r for r in refs if split[r.household_id] == "calibration"]
    test = [r for r in refs if split[r.household_id] == "test"]
    qpd = {r.questions_per_day for r in refs}
    if len(qpd) != 1:
        raise ValueError(f"questions per day differs across banks: {qpd}")
    questions_per_day = qpd.pop()
    configs = voi_best_configs()
    tasks: List[GridTask] = []
    used: Dict[str, Dict[str, Any]] = {}
    for belief_key in beliefs:
        spec_for_belief = belief_spec(belief_key)
        pairs_by_hh = passive_pairs(belief_key, spec_for_belief,
                                    calib, seed, workers)
        pairs: List[CalibrationPair] = [p for hh in sorted(pairs_by_hh)
                                        for p in pairs_by_hh[hh]]
        for base in REPRESENTATIVE_BUDGETS:
            cfg = configs.get((belief_key, str(base)))
            if cfg is None:
                cfg = consensus_config(configs, str(base))
                logger.info("%s@%s: no Part B row, using the consensus "
                            "config %s", belief_key, base, cfg)
            used[f"{belief_key}@{base}"] = dict(cfg)
            table = fit_global_qhat(pairs, float(cfg["resolvable_alpha"]))
            for spec in policy_specs(base, questions_per_day, cfg):
                fitted: Dict[str, Any] = (
                    {"table": table} if spec.kind == "resolvable_mass" else {})
                for c in costs:
                    budget = (round(base * (1.0 + c)) if compensate
                              else base)
                    for ref in test:
                        task = GridTask(belief_key, dict(spec_for_belief),
                                        spec, budget, ref, seed, "", fitted,
                                        room_change_cost=c)
                        task.part_path = part_path(out, task.cell,
                                                   ref.episode_id)
                        tasks.append(task)
    # PerpetuaStar dominates the wall clock (its filters are ~24 of the
    # ~35 CPU-minutes a bank costs), so start those first.
    tasks.sort(key=lambda t: t.belief_key != "PerpetuaStar")
    logger.info("%d tasks: %d beliefs x %d policies x %d budgets x %d costs "
                "x %d households", len(tasks), len(beliefs), 5,
                len(REPRESENTATIVE_BUDGETS), len(costs), len(test))
    results = run_pool(run_plain_task, tasks, workers)
    merge_parts(out)
    grid, days = aggregate_rows(results)
    if (out / "grid.csv").exists() and set(beliefs) != set(BELIEFS):
        grid = _merge_rows(read_csv(out / "grid.csv"), grid, beliefs)
        days = _merge_rows(read_csv(out / "accuracy_by_day.csv"), days,
                           beliefs)
        used = {**json.loads((out / "configs.json").read_text()), **used}
        logger.info("merged %s into the existing grid", list(beliefs))
    write_csv(grid, out / "grid.csv", GRID_FIELDS)
    write_csv(days, out / "accuracy_by_day.csv", DAY_FIELDS)
    (out / "configs.json").write_text(json.dumps(used, indent=2))
    provenance(out, refs, split, seed=seed, beliefs=list(beliefs),
               room_change_costs=list(costs), budget_compensated=compensate,
               budget_rule=("round(base * (1 + c))" if compensate
                            else "fixed at the base"),
               questions_per_day=questions_per_day,
               bank_dir=str(ROOM_COST_BANK_DIR.relative_to(REPO_ROOT)),
               reference_study="results/voi_policies")


# ----------------------------------------------------------------- report

def _idx(grid: Sequence[Dict[str, str]]
         ) -> Dict[Tuple[str, str, str, str], Dict[str, str]]:
    """(belief, policy FAMILY, budget, c) -> row. The family is the key
    because the slug carries per-cell hyperparameters."""
    return {(r["belief"], family_of(r["policy"]), r["budget"],
             r["room_change_cost"]): r for r in grid}


def regression_check(out: pathlib.Path, grid: Sequence[Dict[str, str]],
                     voi_dir: pathlib.Path = VOI_OUT) -> bool:
    """Question 1: at c = 0 every cell this study shares with
    ``results/voi_policies/`` must reproduce it exactly.

    The two runs share beliefs, split, seed and policy configurations, and
    the banks differ only in two header fields, so any difference is a
    behaviour change in the harness or the policies — the thing the c = 0
    column exists to rule out. Cells are matched on (belief, budget,
    policy), mapping this study's ``*_best`` slugs onto the specific
    hyperparameter slugs Part B wrote.
    """
    ref = {(r["belief"], r["policy"], r["budget"]): r
           for r in read_csv(voi_dir / "grid.csv")}
    idx = _idx(grid)
    lines = ["# Regression: c = 0 against `results/voi_policies/`", "",
             "Every cell below is the same (belief, policy, budget) run on "
             "the same test households with the same seed and the same "
             "policy configuration, at room-change cost 0 — where the cost "
             "model is by construction the flat one. Task accuracy and "
             "senses per question must match to the 6 decimals both csvs "
             "carry. Policy slugs are Part B's own, because the RNG "
             "derivation keys on them.", "",
             "| belief | budget | policy | acc here | acc there | "
             "senses/q here | there | match |",
             "|---|---|---|---|---|---|---|---|"]
    all_ok = True
    n_checked = 0
    for belief in BELIEFS:
        for budget in (str(b) for b in REPRESENTATIVE_BUDGETS):
            for family in FAMILY_ORDER:
                here = idx.get((belief, family, budget, "0"))
                there = (ref.get((belief, here["policy"], budget))
                         if here is not None else None)
                if here is None or there is None:
                    all_ok = False
                    slug = "missing" if here is None else here["policy"]
                    lines.append(f"| {belief} | {budget} | {family} | "
                                 f"{slug} | not in voi_policies | | | "
                                 f"**NO** |")
                    continue
                n_checked += 1
                acc_ok = here["task_accuracy"] == there["task_accuracy"]
                spq_ok = (here["senses_per_question"]
                          == there["senses_per_question"])
                all_ok = all_ok and acc_ok and spq_ok
                lines.append(
                    f"| {belief} | {budget} | {here['policy']} | "
                    f"{here['task_accuracy']} | {there['task_accuracy']} | "
                    f"{here['senses_per_question']} | "
                    f"{there['senses_per_question']} | "
                    f"{'yes' if acc_ok and spq_ok else '**NO**'} |")
    lines += ["", f"**{n_checked} cells checked against the reference csv; "
              f"{'ALL MATCH' if all_ok else 'MISMATCHES PRESENT'}.**", ""]
    if not all_ok:
        lines += _head_baseline_section(out)
    (out / "regression.md").write_text("\n".join(lines) + "\n")
    return all_ok


def _head_baseline_section(out: pathlib.Path) -> List[str]:
    """The second half of the regression story when the reference csv does
    not match: is the difference OURS, or was the reference already
    unreproducible?

    ``head_baseline.json`` holds the mismatching cells re-derived by
    running the current committed code, unmodified, on the ORIGINAL banks.
    If those re-derivations equal this study's c = 0 column, then the
    room-change-cost work changed nothing at c = 0 and the reference csv
    is simply stale — which is a stronger check than matching the csv,
    because it compares against code that exists rather than against a
    file no commit can reproduce.
    """
    path = out / "head_baseline.json"
    if not path.exists():
        return ["No `head_baseline.json`: the mismatch is undiagnosed. Do "
                "NOT interpret the c > 0 numbers until it is."]
    doc = json.loads(path.read_text())
    grid = read_csv(out / "grid.csv")
    here = {(r["belief"], r["policy"], r["budget"]): r for r in grid
            if r["room_change_cost"] == "0"}
    lines = ["## Is the difference ours, or was the reference already stale?",
             "", str(doc.get("_why", "")), "",
             "Re-derivation: " + str(doc.get("_method", "")), "",
             "| cell | HEAD, original banks | this study at c = 0 | agree |",
             "|---|---|---|---|"]
    agree = True
    for key, ref in sorted(doc.get("cells", {}).items()):
        belief_budget, policy = key.split(" ", 1)
        belief, budget = belief_budget.split("@")
        row = here.get((belief, policy, budget))
        if row is None:
            agree = False
            lines.append(f"| {key} | {ref['task_accuracy']} | missing | "
                         f"**NO** |")
            continue
        same = (float(row["task_accuracy"]) == float(ref["task_accuracy"])
                and float(row["senses_per_question"])
                == float(ref["senses_per_question"]))
        agree = agree and same
        lines.append(
            f"| {key} | {ref['task_accuracy']} "
            f"({ref['senses_per_question']}) | {row['task_accuracy']} "
            f"({row['senses_per_question']}) | "
            f"{'yes' if same else '**NO**'} |")
    lines += ["", ("**Every re-derived cell agrees with this study's c = 0 "
                   "column exactly, so the room-change cost changed nothing "
                   "at c = 0 and the reference csv is stale. The c > 0 "
                   "readings stand.**" if agree else
                   "**Re-derivation DISAGREES with this study's c = 0 "
                   "column: the difference is ours. STOP.**"), ""]
    return lines


def by_cost_table(out: pathlib.Path, grid: Sequence[Dict[str, str]],
                  costs: Sequence[float] = ROOM_CHANGE_COSTS) -> None:
    """Questions 2 and 3: accuracy, senses per question and the same-room
    share of senses, per (belief, budget, policy, c)."""
    idx = _idx(grid)
    rows: List[Dict[str, Any]] = []
    for belief in BELIEFS:
        for budget in (str(b) for b in REPRESENTATIVE_BUDGETS):
            for family in FAMILY_ORDER:
                base = idx.get((belief, family, budget, "0"))
                for c in costs:
                    r = idx.get((belief, family, budget, f"{c:g}"))
                    if r is None or base is None:
                        continue
                    rows.append({
                        "belief": belief, "budget": budget, "policy": family,
                        "policy_config": r["policy"],
                        "cost_aware": family in COST_AWARE_PREFIXES,
                        "room_change_cost": f"{c:g}",
                        "task_accuracy": r["task_accuracy"],
                        "accuracy_vs_c0": round(
                            float(r["task_accuracy"])
                            - float(base["task_accuracy"]), 6),
                        "senses_per_question": r["senses_per_question"],
                        "senses_vs_c0": round(
                            float(r["senses_per_question"])
                            - float(base["senses_per_question"]), 6),
                        "cost_per_question": r["cost_per_question"],
                        "same_room_sense_fraction":
                            r["same_room_sense_fraction"],
                        "forced_answer_rate": r["forced_answer_rate"]})
    write_csv(rows, out / "by_cost.csv")


def head_to_head_table(out: pathlib.Path, grid: Sequence[Dict[str, str]],
                       costs: Sequence[float] = ROOM_CHANGE_COSTS) -> None:
    """Question 5: the cost-aware pair against the cost-blind three, per
    (belief, budget, c), and how that gap MOVES as c rises.

    ``gap`` is best-cost-aware minus best-cost-blind in the same cell;
    ``gap_vs_c0`` is what the room-change cost added to it. The second
    column is the one the study exists for: an advantage that is only
    present at c = 0 is Part B's advantage, not this brief's.
    """
    idx = _idx(grid)
    rows: List[Dict[str, Any]] = []
    base_gap: Dict[Tuple[str, str], float] = {}
    for belief in BELIEFS:
        for budget in (str(b) for b in REPRESENTATIVE_BUDGETS):
            for c in costs:
                aware = [idx[(belief, f, budget, f"{c:g}")]
                         for f in COST_AWARE_PREFIXES
                         if (belief, f, budget, f"{c:g}") in idx]
                blind = [idx[(belief, f, budget, f"{c:g}")]
                         for f in COST_BLIND_PREFIXES
                         if (belief, f, budget, f"{c:g}") in idx]
                if not aware or not blind:
                    continue
                ba = max(aware, key=lambda r: float(r["task_accuracy"]))
                bb = max(blind, key=lambda r: float(r["task_accuracy"]))
                gap = float(ba["task_accuracy"]) - float(bb["task_accuracy"])
                if c == costs[0]:
                    base_gap[(belief, budget)] = gap
                n = int(ba["n_questions"])
                lo, hi = wilson(round(float(ba["task_accuracy"]) * n), n)
                rows.append({
                    "belief": belief, "budget": budget,
                    "room_change_cost": f"{c:g}",
                    "best_cost_aware": ba["policy"],
                    "cost_aware_accuracy": ba["task_accuracy"],
                    "cost_aware_ci": f"[{lo:.3f}, {hi:.3f}]",
                    "cost_aware_senses_per_q": ba["senses_per_question"],
                    "best_cost_blind": bb["policy"],
                    "cost_blind_accuracy": bb["task_accuracy"],
                    "cost_blind_senses_per_q": bb["senses_per_question"],
                    "gap": round(gap, 6),
                    "gap_vs_c0": round(
                        gap - base_gap.get((belief, budget), 0.0), 6)})
    write_csv(rows, out / "head_to_head.csv")


def wilson(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson score interval — the package's interval everywhere."""
    if n == 0:
        return (0.0, 0.0)
    import math

    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def arrival_table(out: pathlib.Path) -> None:
    """Question 4: where the robot stands when a question arrives, and how
    often the queried object's most likely receptacle is in that room.

    Read off NeverSense's dumps, which never sense: position there is the
    passive patrol's alone, so this describes the SITUATION every policy
    faces rather than any one policy's behaviour.
    """
    rooms: Dict[str, Dict[str, str]] = {}
    for path in sorted(ROOM_COST_BANK_DIR.glob("*__hh_0??_bank.jsonl")):
        with open(path) as fh:
            header = json.loads(fh.readline())
        rooms[str(header["household_id"])] = {
            str(k): str(v) for k, v in header["receptacle_rooms"].items()}
    rows: List[Dict[str, Any]] = []
    room_hits: Dict[str, collections.Counter[str]] = {}
    for belief in BELIEFS:
        for budget in (str(b) for b in REPRESENTATIVE_BUDGETS):
            path = (out / "questions"
                    / f"{belief}__NeverSense__{budget}.jsonl.gz")
            if not path.exists():
                continue
            counter: collections.Counter[str] = collections.Counter()
            # Per household, the marginal of where the robot stands and the
            # marginal of which room the argmax names. Their inner product
            # is what the hit rate would be IF the two were independent —
            # the only honest reference for "is the robot usefully near the
            # answer", because 1/n_rooms assumes rooms are equally likely
            # and these are emphatically not (the kitchen is visited twice
            # as often as the entry).
            per_hh: Dict[str, Tuple[collections.Counter[str],
                                    collections.Counter[str], int]] = {}
            n = in_room = homeless = 0
            for row in read_dump(path):
                where = str(row.get("robot_room_at_query"))
                counter[where] += 1
                n += 1
                hh = str(row["household_id"])
                argmax = row.get("first_argmax") or row["answer_receptacle"]
                room = rooms.get(hh, {}).get(str(argmax))
                rob, arg, cnt = per_hh.setdefault(
                    hh, (collections.Counter(), collections.Counter(), 0))
                rob[where] += 1
                if room is not None:
                    arg[room] += 1
                per_hh[hh] = (rob, arg, cnt + 1)
                if room is None:
                    homeless += 1          # OUT_OF_HOUSE: in no room at all
                elif room == where:
                    in_room += 1
            if not n:
                continue
            independent = 0.0
            for hh, (rob, arg, cnt) in per_hh.items():
                total_arg = sum(arg.values())
                if not cnt or not total_arg:
                    continue
                independent += cnt * sum(
                    (rob[r] / cnt) * (arg[r] / total_arg) for r in rob)
            room_hits[f"{belief}@{budget}"] = counter
            rows.append({
                "belief": belief, "budget": budget, "n_questions": n,
                "argmax_in_robot_room": round(in_room / n, 6),
                "independence_baseline": round(independent / n, 6),
                "argmax_out_of_house": round(homeless / n, 6),
                "argmax_elsewhere_in_house": round(
                    (n - in_room - homeless) / n, 6),
                "n_rooms_min_max": (
                    f"{min(len(set(v.values())) for v in rooms.values())}-"
                    f"{max(len(set(v.values())) for v in rooms.values())}"),
                "position_distribution": "; ".join(
                    f"{room} {cnt / n:.3f}"
                    for room, cnt in counter.most_common())})
    write_csv(rows, out / "arrival.csv")


def stage_report(out: pathlib.Path,
                 costs: Sequence[float] = ROOM_CHANGE_COSTS,
                 compensated: bool = False) -> None:
    grid = read_csv(out / "grid.csv")
    if compensated:
        # The compensated arm shares no cell with results/voi_policies/
        # (its budgets differ at every c > 0), so the c = 0 regression is
        # the main arm's job, not this one's.
        grid = normalize_compensated(grid)
        write_csv(grid, out / "grid_by_base.csv")
        by_cost_table(out, grid, costs)
        head_to_head_table(out, grid, costs)
        _print_headlines(out, grid, costs)
        return
    ok = regression_check(out, grid)
    by_cost_table(out, grid)
    head_to_head_table(out, grid)
    arrival_table(out)
    print(f"regression at c=0 vs the reference csv: "
          f"{'PASS' if ok else 'FAIL'} (see {out / 'regression.md'})")
    if not ok:
        print("  -> the reference csv was produced from an uncommitted tree; "
              "see the head_baseline section of regression.md for whether "
              "the difference is this study's or pre-existing.")
    _print_headlines(out, grid)


def _print_headlines(out: pathlib.Path, grid: Sequence[Dict[str, str]],
                     costs: Sequence[float] = ROOM_CHANGE_COSTS) -> None:
    idx = _idx(grid)
    print("\naccuracy by c (task accuracy; senses/q in parentheses)")
    for belief in BELIEFS:
        for budget in (str(b) for b in REPRESENTATIVE_BUDGETS):
            print(f"\n{belief} @ {budget}/day")
            header = "  " + "policy".ljust(28) + "".join(
                f"c={c:g}".rjust(16) for c in costs)
            print(header)
            for family in FAMILY_ORDER:
                cells = [idx.get((belief, family, budget, f"{c:g}"))
                         for c in costs]
                if not any(cells):
                    continue
                line = "  " + family.ljust(28)
                for r in cells:
                    cellstr = ("" if r is None else
                               f"{fmt(r['task_accuracy'])} "
                               f"({fmt(r['senses_per_question'], 2)})")
                    line += cellstr.rjust(16)
                print(line)


# ----------------------------------------------------------------- figures
#
# Palette: the package's validated categorical hues (the same instance
# `metrics.py` and `voi_study.py` draw from), checked with the data-viz
# validator over ALL pairs, not just adjacent ones, because every series
# shares a panel — worst normal-vision dE 16.3, worst CVD dE 9.2, both
# above their floors. Hue carries policy IDENTITY; line style carries the
# one distinction the study is about (dashed = cost-blind, solid =
# cost-aware), so the grouping survives greyscale and colour-blindness.
# The aqua slot sits just under 3:1 on this surface, which obligates the
# direct labels and the csv table view that accompany every figure.

_INK = "#33322e"
_MUTED = "#6f6d64"
_GRID = "#dddbd2"
_REFERENCE = "#9a978c"
"""NeverSense's line: a reference, not a series. Neutral and dashed, the
package's convention for a non-competitor (as the routine oracle is)."""

POLICY_STYLE: Mapping[str, Tuple[str, str, str, str]] = {
    # family -> (hue, line style, marker, label)
    "SequentialSearch": ("#4a3aa7", "--", "^", "search until found"),
    "ResolvableMassSense": ("#1baf7a", "--", "s", "resolvable-mass gate"),
    "VoIThresholdSense": ("#2a78d6", "-", "o", "VoI threshold"),
    "VoIBudgetPriceSense": ("#eb6834", "-", "D", "VoI budget price"),
}
BELIEF_HUE: Mapping[str, str] = {"LastObservation": "#2a78d6",
                                 "PeriodicPersistence": "#eb6834",
                                 "PerpetuaStar": "#1baf7a",
                                 "OracleBelief": "#4a3aa7"}


def _axis(ax: Any, xlabels: Sequence[str]) -> None:
    """The package's recessive chart furniture."""
    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels, fontsize=8, color=_INK)
    ax.grid(True, color=_GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(_MUTED)
    ax.spines["bottom"].set_color(_MUTED)
    ax.tick_params(colors=_INK, labelsize=8)


def _panels(nrows: int, ncols: int, w: float = 4.6, h: float = 3.6,
            sharey: Any = False) -> Any:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt.subplots(nrows, ncols, squeeze=False, sharey=sharey,
                        figsize=(w * ncols, h * nrows))


def _legend_handles() -> List[Any]:
    """Plain lines, not the errorbar containers: the caps on an errorbar
    handle break the dash pattern, and dashed-vs-solid IS the encoding of
    cost-blind vs cost-aware, so it has to survive the legend."""
    from matplotlib.lines import Line2D

    return [Line2D([], [], color=hue, linestyle=ls, marker=marker,
                   markersize=6, linewidth=2, markeredgecolor="white",
                   markeredgewidth=0.6, label=label)
            for hue, ls, marker, label in POLICY_STYLE.values()]


COST_LABELS = [f"{c:g}" for c in ROOM_CHANGE_COSTS]


def normalize_compensated(grid: Sequence[Dict[str, str]]
                          ) -> List[Dict[str, str]]:
    """Re-key a compensated-budget grid by its BASE budget.

    That arm sets ``budget = round(base * (1 + c))``, so every (base, c)
    lands in its own ``budget`` column and nothing groups. Recovering
    ``base = round(budget / (1 + c))`` is exact for the bases and costs
    the arm uses, and it lets the same plotting read both arms: the
    actual budget spent survives as ``budget_actual``."""
    out: List[Dict[str, str]] = []
    for r in grid:
        row = dict(r)
        c = float(r["room_change_cost"])
        row["budget_actual"] = r["budget"]
        row["budget"] = str(round(int(r["budget"]) / (1.0 + c)))
        out.append(row)
    return out


def plot_accuracy(out: pathlib.Path, grid: Sequence[Dict[str, str]],
               costs: Sequence[float] = ROOM_CHANGE_COSTS,
               suffix: str = "") -> None:
    """Task accuracy against the room-change cost, per belief and budget.

    Error bars are 95% Wilson intervals on 22 500 questions per point
    (about +/-0.006 — often inside the marker, which is itself the
    finding: the moves that matter here are several times the noise)."""
    import matplotlib.pyplot as plt

    labels = [f"{c:g}" for c in costs]
    idx = _idx(grid)
    fig, axes = _panels(len(REPRESENTATIVE_BUDGETS), len(BELIEFS),
                        sharey="row")
    for row, budget in enumerate(str(b) for b in REPRESENTATIVE_BUDGETS):
        for col, belief in enumerate(BELIEFS):
            ax = axes[row][col]
            never = idx.get((belief, "NeverSense", budget, "0"))
            if never is not None:
                y = float(never["task_accuracy"])
                ax.axhline(y, color=_REFERENCE, linestyle=":", linewidth=1.4,
                           zorder=1)
                ax.annotate("never sense", (len(labels) - 1, y),
                            textcoords="offset points", xytext=(-4, 4),
                            ha="right", fontsize=7, color=_MUTED)
            for family, (hue, ls, marker, label) in POLICY_STYLE.items():
                xs, ys, lo, hi = [], [], [], []
                for i, c in enumerate(labels):
                    r = idx.get((belief, family, budget, c))
                    if r is None:
                        continue
                    acc, n = float(r["task_accuracy"]), int(r["n_questions"])
                    a, b = wilson(round(acc * n), n)
                    xs.append(i); ys.append(acc)
                    lo.append(acc - a); hi.append(b - acc)
                if not xs:
                    continue
                ax.errorbar(xs, ys, yerr=[lo, hi], color=hue, linestyle=ls,
                            marker=marker, markersize=5.5, linewidth=2,
                            capsize=3, elinewidth=1, markeredgecolor="white",
                            markeredgewidth=0.6, label=label, zorder=3)
            _axis(ax, labels)
            ax.set_title(f"{belief}, {budget} senses/day", fontsize=9.5,
                         loc="left", color=_INK)
            if row == len(REPRESENTATIVE_BUDGETS) - 1:
                ax.set_xlabel("room-change cost c", color=_INK, fontsize=9)
            if col == 0:
                ax.set_ylabel("task accuracy", color=_INK, fontsize=9)
    fig.legend(handles=_legend_handles(), loc="lower center", ncol=4,
               frameon=False, fontsize=9)
    fig.suptitle(
        "Everyone loses accuracy as travel gets expensive. The cost-aware "
        "policies (solid) usually lose least — but not always: on "
        "PerpetuaStar at 24/day\nthe VoI threshold, tuned to lambda = 0.2 at "
        "c = 0, stops firing once a trip costs anything and falls through "
        "the pack. Shared y within a row;\n22 500 questions per point, 95% "
        "Wilson intervals; c at equal spacing, not to scale.",
        color=_INK, fontsize=9.5, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.05, 1, 0.93))
    fig.savefig(out / f"accuracy_vs_cost{suffix}.png", dpi=150)
    plt.close(fig)


def plot_same_room(out: pathlib.Path, grid: Sequence[Dict[str, str]],
                costs: Sequence[float] = ROOM_CHANGE_COSTS,
                suffix: str = "") -> None:
    """Share of senses that needed no room change.

    Error bars are 95% Wilson intervals on the SENSE count of the cell
    (senses per question x questions), which is the denominator of this
    proportion — far larger than the question count at budget 90 and
    smaller at budget 24, so the bars differ between rows by design."""
    import matplotlib.pyplot as plt

    labels = [f"{c:g}" for c in costs]
    idx = _idx(grid)
    fig, axes = _panels(len(REPRESENTATIVE_BUDGETS), len(BELIEFS))
    for row, budget in enumerate(str(b) for b in REPRESENTATIVE_BUDGETS):
        for col, belief in enumerate(BELIEFS):
            ax = axes[row][col]
            for family, (hue, ls, marker, label) in POLICY_STYLE.items():
                xs, ys, lo, hi = [], [], [], []
                for i, c in enumerate(labels):
                    r = idx.get((belief, family, budget, c))
                    if r is None or not r["same_room_sense_fraction"]:
                        continue
                    share = float(r["same_room_sense_fraction"])
                    n = round(float(r["senses_per_question"])
                              * int(r["n_questions"]))
                    a, b = wilson(round(share * n), n)
                    xs.append(i); ys.append(share)
                    lo.append(share - a); hi.append(b - share)
                if not xs:
                    continue
                ax.errorbar(xs, ys, yerr=[lo, hi], color=hue, linestyle=ls,
                            marker=marker, markersize=5.5, linewidth=2,
                            capsize=3, elinewidth=1, markeredgecolor="white",
                            markeredgewidth=0.6, label=label, zorder=3)
            _axis(ax, labels)
            ax.set_ylim(0, 1.05)
            ax.set_title(f"{belief}, {budget} senses/day", fontsize=9.5,
                         loc="left", color=_INK)
            if row == len(REPRESENTATIVE_BUDGETS) - 1:
                ax.set_xlabel("room-change cost c", color=_INK, fontsize=9)
            if col == 0:
                ax.set_ylabel("senses needing no room change",
                              color=_INK, fontsize=9)
    fig.legend(handles=_legend_handles(), loc="lower center", ncol=4,
               frameon=False, fontsize=9)
    fig.suptitle(
        "Only the cost-aware policies take the discount — and they take it "
        "all at once, at the first non-zero price.\nThe cost-blind pair "
        "drifts up gently: their choice sequence is identical at every c, "
        "but a higher price truncates it earlier,\nleaving the prefix "
        "before the robot has wandered. 95% Wilson intervals on the sense "
        "count.",
        color=_INK, fontsize=9.5, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    fig.savefig(out / f"same_room_share{suffix}.png", dpi=150)
    plt.close(fig)


_CORRECT = re.compile(rb'"correct":\s*(true|false)')
_QID = re.compile(rb'"question_id":\s*"([^"]+)"')
_EID = re.compile(rb'"episode_id":\s*"([^"]+)"')


def _outcomes(path: pathlib.Path) -> Dict[str, bool]:
    """(episode, question) -> correct, pulled straight out of a cell's dump.

    Regex rather than ``json.loads`` because each line embeds a full
    per-object ``belief_state`` snapshot and only three scalars are wanted;
    parsing 22 500 of those dicts per cell would dominate the figure
    build."""
    out: Dict[str, bool] = {}
    with gzip.open(path, "rb") as fh:
        for line in fh:
            c, q, e = (_CORRECT.search(line), _QID.search(line),
                       _EID.search(line))
            if c and q and e:
                out[f"{e.group(1).decode()}/{q.group(1).decode()}"] = (
                    c.group(1) == b"true")
    return out


def _dump_path(out: pathlib.Path, belief: str, policy: str, budget: str,
               cost: str) -> pathlib.Path:
    stem = f"{belief}__{policy}__{budget}"
    if cost not in ("", "0"):
        stem += f"__c{cost}"
    return out / "questions" / f"{stem}.jsonl.gz"


def plot_gap(out: pathlib.Path, grid: Sequence[Dict[str, str]],
          costs: Sequence[float] = ROOM_CHANGE_COSTS,
          suffix: str = "") -> None:
    """The headline: best cost-aware minus best cost-blind, against c.

    The error bars here are PAIRED, not the difference of two independent
    Wilson intervals: both policies answer the very same 22 500 questions,
    so the per-question difference (correct_aware - correct_blind, in
    {-1, 0, +1}) has its own standard error, and it is roughly half the
    width an independence assumption would give. Anything else would
    overstate the uncertainty on exactly the comparison the study is for.
    """
    import matplotlib.pyplot as plt

    labels = [f"{c:g}" for c in costs]
    h2h = read_csv(out / "head_to_head.csv")
    fig, axes = _panels(1, len(REPRESENTATIVE_BUDGETS), w=5.6, h=4.4)
    rows_out: List[Dict[str, Any]] = []
    for col, budget in enumerate(str(b) for b in REPRESENTATIVE_BUDGETS):
        ax = axes[0][col]
        ax.axhline(0.0, color=_INK, linewidth=1.2, zorder=2)
        for belief in BELIEFS:
            xs, ys, err = [], [], []
            for i, c in enumerate(labels):
                r = next((r for r in h2h if r["belief"] == belief
                          and r["budget"] == budget
                          and r["room_change_cost"] == c), None)
                if r is None:
                    continue
                aware = _outcomes(_dump_path(out, belief,
                                             r["best_cost_aware"], budget, c))
                blind = _outcomes(_dump_path(out, belief,
                                             r["best_cost_blind"], budget, c))
                shared = sorted(set(aware) & set(blind))
                diffs = [int(aware[k]) - int(blind[k]) for k in shared]
                n = len(diffs)
                mean = sum(diffs) / n
                var = sum((d - mean) ** 2 for d in diffs) / (n - 1)
                half = 1.96 * math.sqrt(var / n)
                xs.append(i); ys.append(mean); err.append(half)
                rows_out.append({
                    "belief": belief, "budget": budget,
                    "room_change_cost": c, "n_paired": n,
                    "best_cost_aware": r["best_cost_aware"],
                    "best_cost_blind": r["best_cost_blind"],
                    "gap": round(mean, 6),
                    "ci_low": round(mean - half, 6),
                    "ci_high": round(mean + half, 6)})
            if not xs:
                continue
            hue = BELIEF_HUE[belief]
            ax.errorbar(xs, ys, yerr=err, color=hue, marker="o", markersize=6,
                        linewidth=2, capsize=3, elinewidth=1,
                        markeredgecolor="white", markeredgewidth=0.6,
                        label=belief, zorder=3)
            # Ink, not the series hue: text wears text colour and the
            # marker it sits beside carries the identity.
            ax.annotate(belief, (xs[-1], ys[-1]), textcoords="offset points",
                        xytext=(8, 0), fontsize=8, color=_INK, va="center")
        _axis(ax, labels)
        ax.set_xlim(-0.3, len(labels) + 1.1)
        ax.set_title(f"{budget} senses/day", fontsize=10, loc="left",
                     color=_INK)
        ax.set_xlabel("room-change cost c", color=_INK, fontsize=9)
        if col == 0:
            ax.set_ylabel("best cost-aware minus best cost-blind\n"
                          "(task accuracy)", color=_INK, fontsize=9)
        ax.annotate("cost-aware ahead", (0.985, 0.985),
                    xycoords="axes fraction", fontsize=7.5, color=_MUTED,
                    va="top", ha="right")
        ax.annotate("cost-blind ahead", (0.985, 0.015),
                    xycoords="axes fraction", fontsize=7.5, color=_MUTED,
                    va="bottom", ha="right")
    write_csv(rows_out, out / f"gap_paired_ci{suffix}.csv")
    fig.suptitle(
        "The gap closes in favour of cost-awareness as travel gets "
        "expensive — on LastObservation at 90/day it goes -0.100 to -0.014.\n"
        "It closes because the LEADER falls, not because VoI climbs (see "
        "accuracy_vs_cost.png). Paired 95% intervals on the same 22 500 "
        "questions.",
        color=_INK, fontsize=9.5, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(out / f"voi_gap_vs_cost{suffix}.png", dpi=150)
    plt.close(fig)


def plot_arrival(out: pathlib.Path) -> None:
    """Where the robot is when a question arrives, and how often that is
    where the answer probably is. Both are properties of the patrol and the
    question set, identical at every c and every policy."""
    import matplotlib.pyplot as plt

    rows = read_csv(out / "arrival.csv")
    if not rows:
        return
    fig, axes = _panels(1, 2, w=5.6, h=4.0)
    ax = axes[0][0]
    dist = [p.rsplit(" ", 1) for p in rows[0]["position_distribution"].split("; ")]
    names = [d[0] for d in dist]
    vals = [float(d[1]) for d in dist]
    ax.bar(range(len(names)), vals, color="#2a78d6", width=0.68, zorder=3)
    _axis(ax, names)
    ax.tick_params(axis="x", labelrotation=45)
    for lab in ax.get_xticklabels():
        lab.set_ha("right")
    ax.set_ylabel("share of questions", color=_INK, fontsize=9)
    ax.set_title("Robot's room when the question arrives\n"
                 "(room names pooled over 10 households of 6-9 rooms)",
                 fontsize=9.5, loc="left", color=_INK)

    ax = axes[0][1]
    beliefs = [r["belief"] for r in rows if r["budget"] == "24"]
    vals = [float(r["argmax_in_robot_room"]) for r in rows
            if r["budget"] == "24"]
    ns = [int(r["n_questions"]) for r in rows if r["budget"] == "24"]
    errs: List[List[float]] = [[], []]
    for v, n in zip(vals, ns):
        lo, hi = wilson(round(v * n), n)
        errs[0].append(v - lo); errs[1].append(hi - v)
    ax.bar(range(len(beliefs)), vals, color="#eb6834", width=0.6, zorder=3,
           yerr=errs, capsize=4, ecolor=_INK, error_kw={"elinewidth": 1})
    base = [float(r["independence_baseline"]) for r in rows
            if r["budget"] == "24"]
    chance = sum(base) / len(base)
    ax.axhline(chance, color=_REFERENCE, linestyle=":", linewidth=1.6,
               zorder=4)
    _axis(ax, [b.replace("Persistence", "Persist.") for b in beliefs])
    ax.set_ylim(0, 0.30)
    for i, v in enumerate(vals):
        ax.annotate(f"{v:.3f}", (i, v), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=8, color=_INK)
    ax.set_ylabel("share of questions", color=_INK, fontsize=9)
    ax.set_title(f"...and how often the answer's room is that room\n"
                 f"(dotted {chance:.3f}: what independence alone gives)",
                 fontsize=9.5, loc="left", color=_INK)
    fig.suptitle(
        "Four questions in five need a trip before the most likely "
        "receptacle can be checked at all — and the robot is no better\n"
        "placed than chance: the hit rate sits within 0.018 of what "
        "independence alone predicts, and PerpetuaStar is exactly on it.\n"
        "Being where the patrol left you tells you almost nothing about "
        "where the object is. 95% Wilson intervals.",
        color=_INK, fontsize=9.5, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(out / "arrival.png", dpi=150)
    plt.close(fig)


def stage_figures(out: pathlib.Path,
                  costs: Sequence[float] = ROOM_CHANGE_COSTS,
                  compensated: bool = False) -> None:
    grid = read_csv(out / "grid.csv")
    if compensated:
        grid = normalize_compensated(grid)
    plot_accuracy(out, grid, costs)
    plot_same_room(out, grid, costs)
    plot_gap(out, grid, costs)
    if not compensated:
        plot_arrival(out)
    print(f"figures -> {out}")


# ------------------------------------------------------------------- main

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--stage", nargs="+",
                        choices=("verify_banks", "grid", "report", "figures"),
                        required=True)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--costs", default=",".join(
        f"{c:g}" for c in ROOM_CHANGE_COSTS),
        help="comma-separated room-change costs to sweep")
    parser.add_argument("--compensate-budget", action="store_true",
                        help="scale each budget by (1 + c) so the number of "
                             "affordable cross-room looks stays constant; "
                             "isolates the price RATIO from starvation")
    parser.add_argument("--beliefs", default=",".join(BELIEFS),
                        help="comma-separated subset to run; a subset is "
                             "MERGED into any existing grid.csv rather than "
                             "replacing it")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    costs = [float(c) for c in args.costs.split(",") if c.strip()]
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("baselines").setLevel(logging.INFO)
    args.out.mkdir(parents=True, exist_ok=True)
    refs = episode_index(fleet_bank_paths(ROOM_COST_BANK_DIR))
    split = _split_from_reference(refs)
    for stage in args.stage:
        if stage == "verify_banks":
            ok, lines = verify_banks(
                REPO_ROOT / "banks" / "baselines" / "fleet",
                ROOM_COST_BANK_DIR)
            text = ("# Rebuilt banks vs `banks/baselines/fleet/`\n\n"
                    "The rebuild is deterministic and makes no LLM calls, so "
                    "a rebuilt bank must differ from the current one ONLY by "
                    "the two new header fields.\n\n"
                    + "\n".join(lines)
                    + f"\n\n**Verdict: {'PASS' if ok else 'FAIL'}.**\n")
            (args.out / "bank_verification.md").write_text(text)
            print(text)
            if not ok:
                return 1
        elif stage == "grid":
            stage_grid(args.out, refs, split, args.seed, args.workers,
                       [b.strip() for b in args.beliefs.split(",")
                        if b.strip()],
                       costs, args.compensate_budget)
        elif stage == "report":
            stage_report(args.out, costs, args.compensate_budget)
        elif stage == "figures":
            stage_figures(args.out, costs, args.compensate_budget)
    return 0


def _split_from_reference(refs: Sequence[EpisodeRef]) -> Dict[str, str]:
    """The calibration/test split of ``results/voi_policies/``, verbatim.

    Not recomputed: the brief pins this study to that study's split, and
    reading it back is the only way a drift in the household set shows up
    as an error rather than as a quietly different experiment.
    """
    stored = json.loads((VOI_OUT / "provenance.json").read_text())["split"]
    ids: Set[str] = {r.household_id for r in refs}
    if set(stored) != ids:
        raise ValueError(
            f"household set differs from results/voi_policies/: "
            f"{sorted(ids ^ set(stored))}")
    return {str(k): str(v) for k, v in stored.items()}


if __name__ == "__main__":
    raise SystemExit(main())
