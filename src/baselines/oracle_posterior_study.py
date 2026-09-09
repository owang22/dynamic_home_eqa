"""Oracle-posterior study: OracleBelief on the representative grid.

Stages (``--stage``, run in this order; each reads the previous one's
files under ``--out``, default ``results/oracle_program_posterior/``):

  realize    re-realize every fleet household's program at the routine
             oracle's seeds and cache the change points
             (:mod:`baselines.beliefs.oracle_program_posterior`).
  ess_gate   the degeneracy diagnostic on the fleet: OracleBelief under
             the passive diet (NeverSense, the bank's own budget) on all
             20 banks, the effective sample size of the realization
             weights logged per question -> ``ess_passive.csv``,
             ``ess_gate.md``. Exits 2 when the fleet's median ESS is
             below ``ESS_STOP``: the grid must not run before an owner
             chooses the fix (eps, matching granularity, seed count).
  grid       the representative grid (beliefs x {NeverSense,
             SequentialSearch} x budgets {24, 90}) on the test households
             -> ``grid.csv``, ``accuracy_by_day.csv``, question dumps.
             LLM cells are skipped when the cache cannot answer them.
  report     ``findings.md``: policy separation on the oracle belief vs
             the real beliefs, the oracle-vs-best-real gap per budget
             split into belief error and decision error, the ESS
             distribution, and OracleBelief's passive accuracy against
             the routine oracle's no-observation answer on the same
             questions.

Usage:
  PYTHONPATH=src python -m baselines.oracle_posterior_study \\
      --stage realize ess_gate grid report --workers 40
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import logging
import pathlib
import statistics
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.beliefs.oracle_program_posterior import (
    DEFAULT_REALIZATION_CACHE, default_household_dir, load_or_realize)
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
"""Fleet median passive ESS below which the study stops before the grid."""
POLICIES = (PolicySpec("never_sense", label="NeverSense"),
            PolicySpec("sequential_search", label="SequentialSearch"))
REAL_BELIEFS = ("LastObservation", "PeriodicPersistence", "PerpetuaStar",
                "LLMBelief")


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


# --------------------------------------------------------------- ess gate

def stage_ess_gate(out: pathlib.Path, refs: Sequence[EpisodeRef], seed: int,
                   workers: int) -> float:
    """Passive OracleBelief on every fleet bank; per-question ESS."""
    gate_dir = out / "ess_gate"
    tasks = [GridTask("OracleBelief", dict(BELIEF_SPECS["OracleBelief"]),
                      POLICIES[0], ref.budget_per_day, ref, seed,
                      part_path(gate_dir, ("OracleBelief", "NeverSense",
                                           "bank"), ref.episode_id))
             for ref in refs]
    results = run_pool(run_plain_task, tasks, workers)
    merge_parts(gate_dir)
    rows: List[Dict[str, Any]] = []
    for res in results:
        for s in res["summaries"]:
            rows.append({"household_id": s.household_id,
                         "day_index": s.day_index, "ess": round(s.ess or 0, 4),
                         "correct": int(s.correct)})
    write_csv(rows, out / "ess_passive.csv")
    fleet = sorted(r["ess"] for r in rows)
    median = fleet[len(fleet) // 2]
    per_hh: Dict[str, List[float]] = {}
    for r in rows:
        per_hh.setdefault(r["household_id"], []).append(r["ess"])
    lines = ["# ESS gate: OracleBelief under the passive diet, 20 fleet banks",
             "",
             f"Effective sample size ``1 / sum(w_i^2)`` of the realization "
             f"weights ({DEFAULT_ORACLE_SEEDS} seeds, eps 0.05), read after "
             f"every question of a NeverSense replay at the bank's own "
             f"budget. Per-question values in `ess_passive.csv`.", "",
             f"Fleet: {len(fleet)} questions, median ESS **{median:.2f}**, "
             f"quartiles {_quantile(fleet, 0.25):.2f} / "
             f"{_quantile(fleet, 0.75):.2f}, min {fleet[0]:.2f}, "
             f"max {fleet[-1]:.2f}. Stop threshold: median < {ESS_STOP:g}.",
             "", "| household | n | median ESS | p10 | p90 | max |",
             "|---|---|---|---|---|---|"]
    for hh, vals in sorted(per_hh.items()):
        vals.sort()
        lines.append(f"| {hh} | {len(vals)} | {vals[len(vals) // 2]:.2f} | "
                     f"{_quantile(vals, 0.1):.2f} | {_quantile(vals, 0.9):.2f} "
                     f"| {vals[-1]:.2f} |")
    by_day: Dict[int, List[float]] = {}
    for r in rows:
        by_day.setdefault(int(r["day_index"]), []).append(r["ess"])
    lines += ["", "| query day | n | median ESS |", "|---|---|---|"]
    for day, vals in sorted(by_day.items()):
        vals.sort()
        lines.append(f"| {day} | {len(vals)} | {vals[len(vals) // 2]:.2f} |")
    verdict = ("STOP: median ESS below the threshold; the grid was not run. "
               "The fix (eps, matching granularity, seed count) is an owner "
               "decision." if median < ESS_STOP else
               "PASS: the grid may run.")
    lines += ["", f"**Verdict.** {verdict}"]
    (out / "ess_gate.md").write_text("\n".join(lines) + "\n")
    logger.info("ess_gate: fleet median ESS %.3f (%s)", median, verdict[:4])
    return median


def _quantile(sorted_vals: Sequence[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(len(sorted_vals) - 1, max(0, int(round(q * (len(sorted_vals) - 1)))))
    return float(sorted_vals[idx])


# ------------------------------------------------------------------- grid

def representative_tasks(out: pathlib.Path, refs: Sequence[EpisodeRef],
                         beliefs: Sequence[str], policies: Sequence[PolicySpec],
                         budgets: Sequence[Optional[int]], seed: int,
                         fitted: Optional[Dict[str, Dict[str, Any]]] = None
                         ) -> List[GridTask]:
    tasks = []
    for belief_key in beliefs:
        for policy in policies:
            for budget in budgets:
                for ref in refs:
                    task = GridTask(belief_key, dict(BELIEF_SPECS[belief_key]),
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
               split: Dict[str, str], seed: int, workers: int) -> None:
    test = [r for r in refs if split[r.household_id] == "test"]
    beliefs = list(BELIEF_SPECS)
    note = llm_skip_note(test)
    if note:
        beliefs.remove("LLMBelief")
        (out / "llm_skip.md").write_text(note + "\n")
        logger.warning(note)
    tasks = representative_tasks(out, test, beliefs, POLICIES,
                                 list(REPRESENTATIVE_BUDGETS), seed)
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
               oracle_seeds=DEFAULT_ORACLE_SEEDS, llm_skipped=bool(note))


# ----------------------------------------------------------------- report

def _grid_index(rows: Sequence[Dict[str, str]]
                ) -> Dict[Tuple[str, str, str], Dict[str, str]]:
    return {(r["belief"], r["policy"], r["budget"]): r for r in rows}


def _passive_vs_routine(out: pathlib.Path) -> Dict[str, Any]:
    """OracleBelief passive accuracy vs the routine oracle's answer on the
    same questions (both from the NeverSense dump, which carries
    ``routine_argmax``), overall and by query-day third."""
    dumps = sorted((out / "questions").glob("OracleBelief__NeverSense__*.jsonl.gz"))
    if not dumps:
        return {}
    n = ob = ro = both = 0
    by_hh: Dict[str, List[int]] = {}
    ess_correct: Dict[str, List[int]] = {"ess<=1.5": [], "1.5<ess<=5": [],
                                          "ess>5": []}
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
        key = "ess<=1.5" if e <= 1.5 else "1.5<ess<=5" if e <= 5 else "ess>5"
        ess_correct[key].append(o)
    return {"n": n, "oracle_belief": ob / n, "routine": ro / n,
            "both": both / n, "by_household": by_hh,
            "by_ess": {k: (len(v), sum(v) / len(v) if v else 0.0)
                       for k, v in ess_correct.items()}}


def stage_report(out: pathlib.Path) -> None:
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
             "weighted by consistency with the observation history (eps "
             "0.05 per disagreement, soft). Produced by "
             "`python -m baselines.oracle_posterior_study`; raw numbers, "
             "no intervals. Per-day accuracy for every cell is in "
             "`accuracy_by_day.csv`.", ""]
    if note_path.exists():
        lines += [note_path.read_text().strip(), ""]

    # 1. Policy separation.
    lines += ["## 1. Do policies separate more or less on the oracle belief?",
              "", "Task accuracy, NeverSense -> SequentialSearch, and the "
              "difference (the policy's contribution), per belief and budget. "
              "Senses per question in parentheses for SequentialSearch.", "",
              "| belief | budget | NeverSense | SequentialSearch | separation |",
              "|---|---|---|---|---|"]
    for b in beliefs:
        for budget in budgets:
            ns = idx.get((b, "NeverSense", budget))
            ss = idx.get((b, "SequentialSearch", budget))
            if not ns or not ss:
                continue
            sep = float(ss["task_accuracy"]) - float(ns["task_accuracy"])
            lines.append(f"| {b} | {budget} | {fmt(ns['task_accuracy'])} | "
                         f"{fmt(ss['task_accuracy'])} "
                         f"({fmt(ss['senses_per_question'], 2)}) | "
                         f"{sep:+.3f} |")
    seps = {}
    for b in beliefs:
        for budget in budgets:
            ns = idx.get((b, "NeverSense", budget))
            ss = idx.get((b, "SequentialSearch", budget))
            if ns and ss:
                seps[(b, budget)] = float(ss["task_accuracy"]) - float(ns["task_accuracy"])
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
                        choices=("realize", "ess_gate", "grid", "report"),
                        required=True)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--n-seeds", type=int, default=DEFAULT_ORACLE_SEEDS)
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
        if stage == "realize":
            stage_realize(refs, args.n_seeds, args.workers)
        elif stage == "ess_gate":
            median = stage_ess_gate(args.out, refs, args.seed, args.workers)
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
            stage_grid(args.out, refs, split, args.seed, args.workers)
        elif stage == "report":
            stage_report(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
