"""Benchmark the LLM hypothesis belief on the distribution metrics.

Runs :func:`baselines.distribution_metrics.analyze_bank` — the existing
belief benchmark, unchanged — over:

* ``most_frequent`` (24 h) and ``periodic_persistence``: the
  statistical floor. ``periodic_persistence`` doubles as the no-LLM
  comparison arm: it is exactly the mixture's statistical particle
  alone, so (LLM mixture − periodic_persistence) is what the LLM
  descriptions plus weighting machinery added, and (named − anonymized)
  is what KNOWING the object names added.
* the LLM hypothesis mixture on the named and anonymized elicitations;
* the same mixture at ``decay=1.0`` — the pure Bayesian posterior over a
  fixed hypothesis set, i.e. no forgetting at all. The tempered default
  (0.99) is a hedge against misspecification-driven collapse and against
  regime change inside an episode; this arm is what says whether that
  hedge pays;
* ``oracle_program_posterior`` (OracleBelief), the ceiling.

Scoring treats ``ON_PERSON`` and ``OUT_OF_HOUSE`` as one location by
default (:data:`baselines.passive_eval.AWAY_EQUIVALENCE`): the robot
never sights anything at either, so no belief can learn the difference
and exact match was scoring the floor-mass tie-break. ``--exact-match``
restores the historical rule for comparison.

Because ``distribution_metrics`` averages over the whole episode — which
hides any early-history advantage — this driver also writes a
learning-curve breakdown: per-day-bucket accuracy and log-loss per
model from the same per-question rows (a re-analysis, not a re-run).

Usage (after ``elicit`` has produced the hypothesis files):
  python -m baselines.llm_hypotheses.run_eval \
      --households hh_001 hh_002
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
import math
import pathlib
from typing import Any, Dict, List, Sequence, Tuple

from baselines.cli import git_state
from baselines.distribution_metrics import (COLUMNS, LOG_LOSS_EPSILON,
                                            SELECTED, aggregate,
                                            analyze_bank, render_calibration,
                                            render_recall, render_scores,
                                            write_metrics_csv, write_summary)
from baselines.household_analysis import REPO_ROOT
from baselines.llm_hypotheses.elicit import DEFAULT_OUT_DIR
from baselines.passive_eval import AWAY_EQUIVALENCE
from baselines.types import DAY_SECONDS

logger = logging.getLogger(__name__)

DAY_BUCKETS: Tuple[Tuple[int, int], ...] = (
    (0, 3), (4, 7), (8, 14), (15, 27))
"""History buckets for the learning curve: how much sighting history
preceded the question, in days."""


def build_specs(hyp_root: pathlib.Path, conditions: Sequence[str],
                decay_ablation: bool = True) -> List[Dict[str, Any]]:
    specs: List[Dict[str, Any]] = [
        {"name": "most_frequent", "half_life_h": 24.0},
        {"name": "periodic_persistence"},
    ]
    for condition in conditions:
        specs.append({"name": "llm_hypothesis_mixture",
                      "hypotheses_dir": str(hyp_root / condition),
                      "label": f"LLMHyp({condition})"})
    if decay_ablation and conditions:
        # decay=1.0 is the pure Bayesian posterior over a fixed hypothesis
        # set — no forgetting. It is the principled default when the set
        # is fixed and correctly specified, and the tempered default only
        # earns its place if it beats this. Run both rather than assert.
        specs.append({"name": "llm_hypothesis_mixture",
                      "hypotheses_dir": str(hyp_root / conditions[0]),
                      "decay": 1.0,
                      "label": f"LLMHyp({conditions[0]},decay=1.0)"})
    if SELECTED.exists():
        cfg = json.loads(SELECTED.read_text())
        specs.append({"name": "oracle_program_posterior",
                      "eps": cfg["eps"], "half_life_h": cfg["half_life_h"]})
    else:
        logger.warning("no oracle selected.json — ceiling omitted")
    return specs


def learning_curve(rows: Sequence[dict]) -> List[Dict[str, Any]]:
    """Per (model, day-bucket): question count, accuracy, mean log-loss."""
    grouped: Dict[Tuple[str, int], List[dict]] = collections.defaultdict(list)
    for row in rows:
        day = int(row["t_query"]) // DAY_SECONDS
        for index, (lo, hi) in enumerate(DAY_BUCKETS):
            if lo <= day <= hi:
                grouped[(row["model"], index)].append(row)
                break
    out = []
    for (model, index), sub in sorted(grouped.items()):
        lo, hi = DAY_BUCKETS[index]
        lls = [-math.log(max(r["p_truth"], LOG_LOSS_EPSILON)) for r in sub]
        out.append({"model": model, "days": f"{lo}-{hi}",
                    "n": len(sub),
                    "top1": sum(r["correct"] for r in sub) / len(sub),
                    "log_loss": sum(lls) / len(lls)})
    return out


def write_learning_curve(rows: Sequence[dict],
                         out_dir: pathlib.Path) -> None:
    curve = learning_curve(rows)
    with open(out_dir / "learning_curve.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(curve[0]))
        writer.writeheader()
        writer.writerows(curve)
    models = sorted({c["model"] for c in curve})
    lines = ["# Learning curve: accuracy by history preceding the question",
             "", "| model | " + " | ".join(
                 f"d{lo}-{hi}" for lo, hi in DAY_BUCKETS) + " |",
             "|---|" + "---|" * len(DAY_BUCKETS)]
    by_key = {(c["model"], c["days"]): c for c in curve}
    for model in models:
        cells = []
        for lo, hi in DAY_BUCKETS:
            c = by_key.get((model, f"{lo}-{hi}"))
            cells.append(f"{c['top1']:.3f} (n={c['n']})" if c else "—")
        lines.append(f"| {model} | " + " | ".join(cells) + " |")
    (out_dir / "learning_curve.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--households", nargs="+", required=True)
    ap.add_argument("--conditions", nargs="+",
                    default=["named", "anonymized"])
    ap.add_argument("--hyp-dir", type=pathlib.Path,
                    default=DEFAULT_OUT_DIR / "hypotheses")
    ap.add_argument("--out-dir", type=pathlib.Path,
                    default=DEFAULT_OUT_DIR / "eval")
    ap.add_argument("--rng-seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--no-decay-ablation", action="store_true",
                    help="skip the decay=1.0 (pure posterior) arm")
    ap.add_argument("--exact-match", action="store_true",
                    help="score ON_PERSON and OUT_OF_HOUSE as distinct "
                         "(the historical rule); default scores them as "
                         "one location, see passive_eval.AWAY_EQUIVALENCE")
    args = ap.parse_args()
    equivalence = () if args.exact_match else AWAY_EQUIVALENCE

    specs = build_specs(args.hyp_dir, args.conditions,
                        decay_ablation=not args.no_decay_ablation)
    for spec in specs:
        if "hypotheses_dir" in spec:
            for household in args.households:
                path = pathlib.Path(spec["hypotheses_dir"]) / f"{household}.json"
                if not path.exists():
                    raise SystemExit(f"missing hypotheses file {path}; "
                                     f"run elicit first")
    tasks = [{"household": h, "specs": specs, "rng_seed": args.rng_seed,
              "bank_dir": None, "location_equivalence": equivalence}
             for h in args.households]
    rows: List[Tuple[Any, ...]] = []
    with concurrent.futures.ProcessPoolExecutor(args.workers) as pool:
        for household, res in zip(args.households,
                                  pool.map(analyze_bank, tasks)):
            logger.info("done %s (%d rows)", household, len(res))
            rows += res

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with gzip.open(args.out_dir / "per_question.csv.gz", "wt",
                   newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(COLUMNS)
        writer.writerows(rows)
    dicts = [dict(zip(COLUMNS, r)) for r in rows]
    metrics = aggregate(dicts)
    prov = {"timestamp": datetime.datetime.now(datetime.timezone.utc)
            .isoformat(timespec="seconds"),
            "git": dict(zip(("commit", "dirty"), git_state(REPO_ROOT))),
            "households": list(args.households),
            "n_households": len(args.households), "specs": specs,
            "rng_seed": args.rng_seed,
            "log_loss_epsilon": LOG_LOSS_EPSILON,
            "location_equivalence": [list(g) for g in equivalence]}
    (args.out_dir / "provenance.json").write_text(json.dumps(prov, indent=2))
    write_metrics_csv(metrics, args.out_dir)
    render_scores(metrics, args.out_dir / "scores_by_model.png")
    render_recall(metrics, args.out_dir / "recall_at_k.png")
    render_calibration(metrics, args.out_dir / "calibration.png")
    write_summary(metrics, args.out_dir, prov)
    write_learning_curve(dicts, args.out_dir)
    logger.info("wrote %s", args.out_dir)


if __name__ == "__main__":
    main()
