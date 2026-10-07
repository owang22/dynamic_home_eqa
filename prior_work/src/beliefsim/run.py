"""Run the factorial and write the single source of truth.

    PYTHONPATH=src python -m beliefsim.run --out results

Emits ``results/raw_results.csv`` (long format, one row per timestep per
scored group) and ``results/provenance.json``. Every table and figure in
``results/`` is derived from that CSV by ``beliefsim.report``; no number is
computed by a second code path.

Two cells are dropped from the full cross product because they are
DUPLICATES, not because they are uninteresting:

* every policy at budget 0 is the never-sense policy, so budget 0 is run
  once, under ``never_sense``;
* never-sense at any budget is never-sense at budget 0, so it is not rerun
  per budget.

The forced held-out ablation (B6) is a deliberately small side condition:
one policy, four budgets, all five mask draws. Its purpose is a controlled
version of the transfer question — the same k objects are invisible to
every method, so cross-method comparison is not confounded by different
policies happening to leave different objects unseen.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import pathlib
import time
from typing import Dict, Iterator, List, Tuple

from beliefsim.beliefs import BELIEF_FACTORIES, FREMEN_ORDER, make_belief
from beliefsim.loop import ALL_BUDGET, ROW_FIELDS, RunSpec, run_cell
from beliefsim.policies import POLICY_FACTORIES, make_policy
from beliefsim.scoring import DEFAULT_SEEDS
from beliefsim.world import HOURS, World, load_world

BUDGETS: Tuple[object, ...] = (0, 1, 2, 5, 10, 25, 50, ALL_BUDGET)
BELIEFS = tuple(BELIEF_FACTORIES)
POLICIES = tuple(p for p in POLICY_FACTORIES if p != "never_sense")
HOUSEHOLDS = ("A", "B", "C")

HELDOUT_POLICY = "staleness_first"
HELDOUT_BUDGETS: Tuple[object, ...] = (1, 5, 25, ALL_BUDGET)
HELDOUT_SEED = 0

_WORLDS: Dict[str, World] = {}


def _world(traces: pathlib.Path, household: str) -> World:
    """Per-process world cache: loading a trace costs more than running a
    low-budget cell, and every worker reuses its three."""
    if household not in _WORLDS:
        _WORLDS[household] = load_world(traces, household)
    return _WORLDS[household]


def specs(masks: Dict) -> Iterator[RunSpec]:
    for household in HOUSEHOLDS:
        for belief in BELIEFS:
            for seed in DEFAULT_SEEDS:
                yield RunSpec(household, belief, "never_sense", 0, seed)
                for policy in POLICIES:
                    for budget in BUDGETS:
                        if budget == 0:
                            continue
                        yield RunSpec(household, belief, policy, budget, seed)
            for budget in HELDOUT_BUDGETS:
                for draw, held in enumerate(masks["draws"][household]):
                    yield RunSpec(household, belief, HELDOUT_POLICY, budget,
                                  HELDOUT_SEED, condition="heldout",
                                  heldout=tuple(held), draw=str(draw))


def _run_one(args) -> List[Dict[str, object]]:
    traces, spec = args
    return run_cell(_world(traces, spec.household), make_belief(spec.belief),
                    make_policy(spec.policy), spec)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("results"))
    ap.add_argument("--traces", type=pathlib.Path,
                    default=pathlib.Path("data/homer_traces"))
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    masks = json.loads((args.traces / "heldout_masks.json").read_text())
    todo = list(specs(masks))
    print(f"{len(todo)} cells on {args.workers} workers")

    started = time.time()
    n_rows = 0
    with open(args.out / "raw_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ROW_FIELDS)
        writer.writeheader()
        with concurrent.futures.ProcessPoolExecutor(args.workers) as pool:
            for i, rows in enumerate(pool.map(
                    _run_one, ((args.traces, s) for s in todo),
                    chunksize=4), start=1):
                writer.writerows(rows)
                n_rows += len(rows)
                if i % 200 == 0:
                    print(f"  {i}/{len(todo)} cells, {n_rows} rows, "
                          f"{time.time() - started:.0f}s")

    worlds = {h: load_world(args.traces, h) for h in HOUSEHOLDS}
    provenance = {
        "experiment": "budgeted whole-house belief tracking on HOMER+",
        "observation_model": "object-level (observe object o, learn its "
                             "receptacle at that instant)",
        "budget_semantics": "per day, spread evenly over the scored hours "
                            "by the harness",
        "scoring": "every object, every hour in HOURS, every scored day; "
                   "sensing at hour h precedes scoring at hour h",
        "hours": list(HOURS),
        "budgets": [str(b) for b in BUDGETS],
        "beliefs": list(BELIEFS),
        "policies": ["never_sense"] + list(POLICIES),
        "seeds": list(DEFAULT_SEEDS),
        "fremen_order": FREMEN_ORDER,
        "heldout": {"policy": HELDOUT_POLICY,
                    "budgets": [str(b) for b in HELDOUT_BUDGETS],
                    "seed": HELDOUT_SEED,
                    "k": masks["k"], "mask_seed": masks["seed"],
                    "n_draws": len(masks["draws"]["A"])},
        "households": {h: {"objects": len(w.objects),
                           "receptacles": len(w.receptacles),
                           "learn_days": len(w.learn_days),
                           "score_days": len(w.score_days),
                           "displaced_instants": sum(
                               w.is_displaced(o, d, hh) for o in w.objects
                               for d in w.score_days for hh in HOURS),
                           "scored_instants": (len(w.objects)
                                               * len(w.score_days)
                                               * len(HOURS))}
                       for h, w in worlds.items()},
        "n_cells": len(todo), "n_rows": n_rows,
        "runtime_seconds": round(time.time() - started, 1),
    }
    (args.out / "provenance.json").write_text(json.dumps(provenance, indent=2))
    print(f"wrote {args.out / 'raw_results.csv'} ({n_rows} rows) in "
          f"{time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
