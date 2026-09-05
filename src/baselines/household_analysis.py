"""Per-household passive analysis across seeds, both evaluation modes.

What the bake-off leaderboard averages away: which homes separate the
belief models and which do not, how that separation develops with
history, and how each model's accuracy decays with the AGE of its
evidence. Two modes per bank, same models, same questions:

* continuous — the belief is updated with every sighting strictly
  before each query (:func:`passive_eval.evaluate_continuous`): "how
  good is the belief right now". Query day = history length; age of
  the object's last sighting recorded per question with fine bins.
* frozen — the bake-off's horizon-controlled forecast
  (:func:`passive_eval.evaluate_checkpoint`): belief frozen at day D,
  questions bucketed by how far past D they fall.

Plus the routine oracle per bank (perfect routine knowledge, no
observations; not a hard ceiling — a fresh sighting beats it) binned
the same way, so "reaches the ceiling" is measurable.

Every (household, seed, model, mode, day, horizon, age bin) cell is
written with its question count, correct count and summed log-loss to
``cells.csv.gz``; ``household_report.py`` reads that and averages the
seeds of a home. Deterministic in (banks, config, seed).

Usage:
  python -m baselines.household_analysis                 # all built homes, 5 seeds
  python -m baselines.household_analysis --households hh_001 --seeds 0 \
      --models last_observation most_frequent --oracle-seeds 20 --out-dir /tmp/x
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import csv
import datetime
import gzip
import json
import logging
import pathlib
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

from baselines.bakeoff import bakeoff_specs
from baselines.bank import JsonlBank
from baselines.cli import _derived_rng, git_state
from baselines.passive_eval import (CONTINUOUS_HORIZON,
                                    PassiveProtocolConfig, _horizon_of,
                                    evaluate_checkpoint,
                                    evaluate_continuous, question_ages)
from baselines.registry import build_registered_belief
from baselines.routine_oracle import ORACLE_SEED_BASE, oracle_predictions
from baselines.types import DAY_SECONDS

logger = logging.getLogger(__name__)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BANK_DIR = REPO_ROOT / "banks" / "baselines" / "fleet"
GENERATED = REPO_ROOT / "profiles" / "households" / "generated"
CONTROL = REPO_ROOT / "profiles" / "households" / "control.yaml"
MODEL_SLUG = "gpt-5.6-terra"
SEEDS = (0, 1, 2, 3, 4)
FINE_AGE_EDGES_H = (0.25, 1.0, 3.0, 6.0, 12.0, 24.0, 48.0, 72.0)
"""Age-of-observation bin edges, hours. Fine at the short end, where a
last-observation belief should be near-perfect and where the interesting
crossover with routine-based beliefs happens."""
ORACLE_NAME = "routine_oracle"
DEFAULT_ORACLE_SEEDS_PER_BANK = 200
"""Realizations per bank. Five seed-banks of one home use disjoint draws,
so a home's seed-averaged oracle rests on 1000 realizations (sd ~0.004,
per routine_oracle's measured 1/sqrt(n) spread)."""

COLUMNS = ("household", "seed", "model", "mode", "day", "horizon",
           "age_bin", "n", "correct", "logloss")

ABSENCE_COLUMNS = ("household", "seed", "model", "mode", "day", "horizon",
                   "question_id", "object_id", "t_query", "age_bin",
                   "truth_category", "correct", "max_edge_belief",
                   "sum_edge_belief", "n_edges", "n_fallback_edges")
"""``absence_signal.csv.gz``: one row per scored question of every model
that offers prediction diagnostics (the Perpetua edge models): the
largest per-edge presence belief is the signal a future "not in the
house" answer would threshold, logged next to where the object really
was so its calibration can be read off by age bin."""
RESET_COLUMNS = ("household", "seed", "model", "object_id", "receptacle_id",
                 "t", "direction")
"""``perpetua_resets.csv.gz``: every filter reset of the continuous run."""
EDGE_COLUMNS = ("household", "seed", "model", "object_id", "receptacle_id",
                "t0", "n_events", "n_sightings", "n_persistence_segments",
                "n_emergence_segments", "pf_components", "ef_components",
                "pf_fallback", "ef_fallback", "n_resets")
"""``perpetua_edges.csv.gz``: per-edge state at the end of the continuous
run: how much training data each edge had and whether it was still on the
fallback prior."""
FALLBACK_COLUMNS = ("household", "seed", "model", "day", "n_predictions",
                    "n_predictions_any_fallback", "n_edge_beliefs",
                    "n_fallback_edge_beliefs")
"""``perpetua_fallback.csv.gz``: per query day of the continuous run, how
many predictions (and edge beliefs) came from the fallback prior."""
SIDE_FILES = {"absence": ("absence_signal.csv.gz", ABSENCE_COLUMNS),
              "resets": ("perpetua_resets.csv.gz", RESET_COLUMNS),
              "edges": ("perpetua_edges.csv.gz", EDGE_COLUMNS),
              "fallback": ("perpetua_fallback.csv.gz", FALLBACK_COLUMNS)}


def truth_category(receptacle_id: str) -> str:
    """Where an object really is, coarsely: ``out of house``, ``on a
    person`` or ``ordinary receptacle`` (the report's grouping)."""
    upper = receptacle_id.upper()
    if "OUT" in upper:
        return "out of house"
    if "PERSON" in upper:
        return "on a person"
    return "ordinary receptacle"


def _absence_rows(scored: Sequence[Any], episode: Any, household: str,
                  seed: int, mode: str) -> List[Tuple[Any, ...]]:
    rows = []
    for q in scored:
        d = q.diagnostics
        if d is None:
            continue
        truth = episode.true_location(q.object_id, q.t_query)
        rows.append((household, seed, q.belief, mode, q.checkpoint_day,
                     q.horizon_days, q.question_id, q.object_id, q.t_query,
                     q.recency_bin, truth_category(truth), int(q.correct),
                     round(d["max_edge_belief"], 6),
                     round(d["sum_edge_belief"], 6), int(d["n_edges"]),
                     int(d["n_fallback_edges"])))
    return rows


def _perpetua_rows(belief: Any, household: str, seed: int
                   ) -> Dict[str, List[Tuple[Any, ...]]]:
    """Reset, edge and fallback rows of a finished continuous run, for
    models that keep them (duck-typed on the Perpetua diagnostics)."""
    if not all(hasattr(belief, a) for a in
               ("reset_events", "edge_summary", "fallback_summary")):
        return {}
    name = belief.name
    resets = [(household, seed, name, e["object_id"], e["receptacle_id"],
               e["t"], e["direction"]) for e in belief.reset_events]
    edges = [(household, seed, name, *(e[c] for c in EDGE_COLUMNS[3:]))
             for e in belief.edge_summary()]
    fallback = [(household, seed, name, day, *(v[c] for c in FALLBACK_COLUMNS[4:]))
                for day, v in belief.fallback_summary().items()]
    return {"resets": resets, "edges": edges, "fallback": fallback}


def bank_path(household: str, seed: int,
              bank_dir: Optional[pathlib.Path] = None) -> pathlib.Path:
    """The fleet's bank for one (household, seed); ``bank_dir`` points a
    sweep at its own exported banks (same naming)."""
    suffix = "" if seed == 0 else f"__seed{seed}"
    return ((bank_dir or BANK_DIR) / f"households__generated__{MODEL_SLUG}__"
                                     f"{household}{suffix}_bank.jsonl")


def timeline_dir(household: str, seed: int) -> pathlib.Path:
    return GENERATED / MODEL_SLUG / household / f"timeline_seed{seed}"


def household_meta(bank_dir: Optional[pathlib.Path] = None
                   ) -> Dict[str, Dict[str, Any]]:
    """Built households (a seed-0 bank exists in ``bank_dir``) with the
    control-file fields the report groups on."""
    control = yaml.safe_load(CONTROL.read_text())
    out = {}
    for rec in control["households"]:
        hid = rec["household_id"]
        if not bank_path(hid, 0, bank_dir).exists():
            continue
        out[hid] = {
            "household_type": rec["household_type"],
            "archetype": rec["archetype"], "overlay": rec["overlay"],
            "variant": rec["variant"], "wave": rec["wave"],
            "residents": rec["residents"], "tags": rec.get("tags", []),
            "resident_group": ("1" if rec["residents"] == 1
                               else "2" if rec["residents"] == 2 else "3+"),
        }
    return out


def _agg_rows(agg: Dict[Tuple, List], household: str, seed: int) -> List[Tuple[Any, ...]]:
    rows = []
    for (model, mode, day, horizon, age_bin), (n, c, ll) in sorted(
            agg.items(), key=lambda kv: tuple(map(str, kv[0]))):
        rows.append((household, seed, model, mode, day, horizon, age_bin,
                     n, c, None if ll is None else round(ll, 6)))
    return rows


def analyze_bank(task: Dict[str, Any]) -> Dict[str, Any]:
    """One (household, seed) bank: every model in both modes + oracle.
    Runs in a worker process; returns aggregated cells only."""
    household, seed = task["household"], task["seed"]
    specs: Sequence[Dict[str, Any]] = task["specs"]
    config = PassiveProtocolConfig(seed=task["rng_seed"],
                                   recency_bin_edges_h=FINE_AGE_EDGES_H)
    bank_dir = task.get("bank_dir")
    path = bank_path(household, seed,
                     pathlib.Path(bank_dir) if bank_dir else None)
    episodes = list(JsonlBank(path=path).episodes())
    agg: Dict[Tuple, List] = collections.defaultdict(lambda: [0, 0, 0.0])
    oracle_stats: Optional[Dict[str, Any]] = None
    side: Dict[str, List[Tuple[Any, ...]]] = {k: [] for k in SIDE_FILES}

    def add(key: Tuple, correct: bool, logloss: Optional[float]) -> None:
        cell = agg[key]
        cell[0] += 1
        cell[1] += int(correct)
        if logloss is None:
            cell[2] = None
        elif cell[2] is not None:
            cell[2] += logloss

    for episode in episodes:
        for spec in specs:
            rng = _derived_rng(task["rng_seed"], "household_analysis",
                               str(spec["name"]), episode.episode_id,
                               "continuous")
            belief = build_registered_belief(dict(spec), rng)
            name = belief.name
            scored = evaluate_continuous(episode, belief, config)
            for q in scored:
                add((name, "continuous", q.checkpoint_day,
                     CONTINUOUS_HORIZON, q.recency_bin),
                    q.correct, q.log_loss)
            side["absence"] += _absence_rows(scored, episode, household,
                                             seed, "continuous")
            for key, rows in _perpetua_rows(belief, household, seed).items():
                side[key] += rows
            for checkpoint in config.checkpoint_days:
                rng = _derived_rng(task["rng_seed"], "household_analysis",
                                   str(spec["name"]), episode.episode_id,
                                   str(checkpoint))
                belief = build_registered_belief(dict(spec), rng)
                scored = evaluate_checkpoint(episode, belief, checkpoint,
                                             config)
                for q in scored:
                    add((name, "frozen", checkpoint, q.horizon_days,
                         q.recency_bin), q.correct, q.log_loss)
                side["absence"] += _absence_rows(scored, episode, household,
                                                 seed, "frozen")

        if task["oracle_seeds"] > 0:
            result = oracle_predictions(
                timeline_dir(household, seed), episode,
                n_seeds=task["oracle_seeds"],
                seed_base=ORACLE_SEED_BASE + seed * 10_000)
            if result is not None:
                modal, oracle_stats = result
                questions = [q for day in episode.questions_by_day
                             for q in day]
                ages_now = question_ages(episode)
                ages_at = {D: question_ages(episode, D * DAY_SECONDS)
                           for D in config.checkpoint_days}
                for pred, q in zip(modal, questions):
                    correct = pred == episode.true_location(q.object_id,
                                                            q.t_query)
                    add((ORACLE_NAME, "continuous",
                         q.t_query // DAY_SECONDS, CONTINUOUS_HORIZON,
                         config.recency_bin(ages_now[q.question_id])),
                        correct, None)
                    for D in config.checkpoint_days:
                        elapsed = q.t_query - D * DAY_SECONDS
                        if elapsed <= 0:
                            continue
                        h = _horizon_of(elapsed, config.horizons_days)
                        if h is None:
                            continue
                        add((ORACLE_NAME, "frozen", D, h,
                             config.recency_bin(ages_at[D][q.question_id])),
                            correct, None)
    return {"household": household, "seed": seed,
            "rows": _agg_rows(agg, household, seed),
            "oracle": oracle_stats, "side": side}


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--households", nargs="*", default=None)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(SEEDS))
    ap.add_argument("--models", nargs="*", default=None,
                    help="registry spec names (default: the bake-off slate)")
    ap.add_argument("--oracle-seeds", type=int,
                    default=DEFAULT_ORACLE_SEEDS_PER_BANK,
                    help="realizations per bank; 0 skips the oracle")
    ap.add_argument("--rng-seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out-dir", type=pathlib.Path,
                    default=REPO_ROOT / "reports" / "baselines"
                    / "household_analysis")
    ap.add_argument("--bank-dir", type=pathlib.Path, default=None,
                    help="banks to analyse (default: the fleet's)")
    args = ap.parse_args()
    specs = select_specs(args.models)
    run_analysis(households=args.households, seeds=args.seeds, specs=specs,
                 oracle_seeds=args.oracle_seeds, rng_seed=args.rng_seed,
                 workers=args.workers, out_dir=args.out_dir,
                 bank_dir=args.bank_dir)


def select_specs(names: Optional[Sequence[str]]) -> List[Dict[str, Any]]:
    """The bake-off specs, optionally restricted to the given spec names
    (a name with several variants, e.g. the two perpetua_star entries,
    keeps all of them)."""
    specs = list(bakeoff_specs())
    if names:
        specs = [s for s in specs if s["name"] in names]
        missing = set(names) - {s["name"] for s in specs}
        if missing:
            raise SystemExit(f"unknown model specs {sorted(missing)}")
    return specs


def run_analysis(households: Optional[Sequence[str]], seeds: Sequence[int],
                 specs: Sequence[Dict[str, Any]], oracle_seeds: int,
                 rng_seed: int, workers: int, out_dir: pathlib.Path,
                 bank_dir: Optional[pathlib.Path] = None,
                 extra_provenance: Optional[Dict[str, Any]] = None) -> int:
    """Analyse every (household, seed) bank under ``bank_dir`` with the
    given specs; write cells, side files, households.json and
    provenance.json into ``out_dir``. Returns the cell count."""
    meta = household_meta(bank_dir)
    households = list(households) if households else sorted(meta)
    unknown = [h for h in households if h not in meta]
    if unknown:
        raise SystemExit(f"no seed-0 bank for {unknown}")
    tasks = [{"household": h, "seed": s, "specs": list(specs),
              "oracle_seeds": oracle_seeds, "rng_seed": rng_seed,
              "bank_dir": str(bank_dir) if bank_dir else None}
             for h in households for s in seeds
             if bank_path(h, s, bank_dir).exists()]
    skipped = [(h, s) for h in households for s in seeds
               if not bank_path(h, s, bank_dir).exists()]
    if skipped:
        logger.warning("no bank for %s — skipped", skipped)
    logger.info("%d banks x %d models, %d workers", len(tasks),
                len(specs), workers)

    out_dir.mkdir(parents=True, exist_ok=True)
    oracle: Dict[str, Dict[str, Any]] = {}
    n_rows = 0
    side_handles = {key: gzip.open(out_dir / fname, "wt", newline="")
                    for key, (fname, _) in SIDE_FILES.items()}
    side_writers = {key: csv.writer(fh) for key, fh in side_handles.items()}
    for key, (_, columns) in SIDE_FILES.items():
        side_writers[key].writerow(columns)
    n_side = {key: 0 for key in SIDE_FILES}
    try:
        with gzip.open(out_dir / "cells.csv.gz", "wt", newline="") as fh, \
                concurrent.futures.ProcessPoolExecutor(
                    max_workers=workers) as pool:
            writer = csv.writer(fh)
            writer.writerow(COLUMNS)
            futures = {pool.submit(analyze_bank, t): t for t in tasks}
            for fut in concurrent.futures.as_completed(futures):
                res = fut.result()
                writer.writerows(res["rows"])
                n_rows += len(res["rows"])
                for key, rows in res["side"].items():
                    side_writers[key].writerows(rows)
                    n_side[key] += len(rows)
                if res["oracle"]:
                    oracle[f"{res['household']}:{res['seed']}"] = res["oracle"]
                logger.info("done %s seed %s (%d cells)", res["household"],
                            res["seed"], len(res["rows"]))
    finally:
        for fh in side_handles.values():
            fh.close()

    (out_dir / "households.json").write_text(json.dumps(
        {"households": meta, "oracle_per_bank": oracle}, indent=2))
    (out_dir / "provenance.json").write_text(json.dumps({
        "generated_at": datetime.datetime.now(
            datetime.timezone.utc).isoformat(),
        "git": git_state(REPO_ROOT), "rng_seed": rng_seed,
        "seeds": list(seeds), "households": households,
        "models": [s["name"] for s in specs],
        "modes": ["continuous", "frozen"],
        "age_bin_edges_h": list(FINE_AGE_EDGES_H),
        "checkpoint_days": list(PassiveProtocolConfig().checkpoint_days),
        "horizons_days": list(PassiveProtocolConfig().horizons_days),
        "oracle_seeds_per_bank": oracle_seeds,
        "bank_dir": str(bank_dir) if bank_dir else str(BANK_DIR),
        "n_cells": n_rows,
        "side_files": {SIDE_FILES[k][0]: n for k, n in n_side.items()},
        **(extra_provenance or {})}, indent=2))
    print(f"household_analysis: {len(tasks)} banks, {n_rows} cells -> "
          f"{out_dir}")
    return n_rows


if __name__ == "__main__":
    main()
