"""Monte-Carlo routine oracle: the accuracy of perfect routine knowledge
with no observations at all.

The storyfirst pipeline separates authorship from realization: an LLM
writes the household's story days and probabilistic movement rules into
``program.yaml`` once, and a seeded local simulator
(``src/revamp_v2/simulate.py``) realizes them into a concrete timeline —
the daily misplace draws, rule destination draws, tidy races, activity
skips, jitter, and bout fragmentation are all realization randomness.
The bank's world is the seed-0 realization.

The oracle re-realizes the SAME program at many other seeds and, for
each bank question ``(object, t_query)``, predicts the modal receptacle
across those realizations. That is the answer of a predictor that knows
the household's routine perfectly — the program, with the realization
randomness marginalized out — and has seen no observations. It is
deliberately NOT handed the seed-0 realization itself: reading the true
world's own coin flips would shrink the headroom number to nothing.

This is NOT a hard ceiling. The oracle sees no observations, so a model
with a fresh sighting can and should beat it. Oracle accuracy minus
best-model accuracy per budget measures how much of the residual error
is explainable by routine knowledge alone; where observation-fed models
exceed the oracle, recency is carrying the load instead. Both
directions are informative; neither is a bug.

The oracle's accuracy does not depend on the observation budget (it
consumes no observations), so the budget sweep shows it as one flat
reference line, visually distinct from the model curves.

Cost: one realization is ~0.02 s, so the default seed count adds about
16 s per household. Verified against the shipped timelines: the
seed-0 re-realization reproduces ``hourly.csv`` byte-for-byte and every
event field the truth loader reads (the shipped ``events.jsonl`` only
adds spatialization fields from a later pass).
"""

from __future__ import annotations

import collections
import importlib.util
import logging
import pathlib
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple

import yaml

from baselines.export_bank import load_truth, truth_at
from baselines.types import Episode

logger = logging.getLogger(__name__)

DEFAULT_ORACLE_SEEDS = 800
"""Realizations averaged per household.

Set from the measured spread of the estimate itself, not from a guess:
across eight INDEPENDENT 200-seed blocks per household, the per-household
standard deviation of oracle accuracy is 0.003-0.008 (worst: storyfirst
hh7 and hh2). Since it falls as 1/sqrt(seeds), 800 seeds put every
household at sd <= 0.004, i.e. a two-sigma spread of 0.008 — comfortably
inside the 0.02 that separates signal from noise on this fleet. A
realization costs ~0.02 s, so this is ~16 s per household.

A cumulative accuracy-vs-seed-count curve does NOT measure this:
successive points share most of their samples, so the curve can trend in
one direction for hundreds of seeds without meaning anything. Only
disjoint blocks give independent estimates, which is what
``half_split_delta`` below reports.
"""

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

ORACLE_SEED_BASE = 1000
"""First realization seed the oracle draws from. Bank worlds are the
seed-0 realization plus the reseeded 1-4 (households.reseed), so the
oracle's seeds start well above them: it must never average in the
answer's own coin flips. Per-bank runs offset further by the bank's
seed so five seeds of one home get disjoint oracle draws."""


def _load_realizer() -> Any:
    """The realization engine: the self-contained households package
    (households.simulate wraps the vendored simulator). A plain import —
    the old importlib load of src/revamp_v2/simulate.py pulled the v1
    engine out of profiles/revamp_v1, which no longer exists."""
    from households import simulate
    return simulate


def _realized_truth(sim: Any, engine: Any, params: Dict[str, Any],
                    program: Dict[str, Any], hh_dir: pathlib.Path,
                    seed: int) -> Dict[str, List[Tuple[int, str]]]:
    """One realization's projected truth trajectories, via a temp dir.

    Mirrors ``generate_dataset.realize`` up to the write, then reads the
    trajectories back through the same loader/projection the bank export
    uses, so oracle receptacle ids (OUT_OF_HOUSE / ON_PERSON included)
    mean exactly what bank truth means.
    """
    days = int(program["days"])
    log, hourly, blocks, stats, _acts, motions = sim.simulate_program(
        program, days, seed, sa=engine, params=params)
    sim.tag_event_kinds(log)
    carry = params.get("carry_on_departure", {})
    stats["carry_rehome_suppressed"] = sim.suppress_carry_rehome(
        log, hourly, float(carry.get("carry_rehome_min", 0)))
    with tempfile.TemporaryDirectory(prefix="routine_oracle_") as tmp:
        out = pathlib.Path(tmp) / f"timeline_seed{seed}"
        engine.write_outputs(out, motions, log, hourly, blocks, stats,
                             days, seed, hh_dir)
        truth, _n_days, _causes = load_truth(out)
    return truth


def _modal_receptacle(counter: "collections.Counter[str]") -> str:
    """Highest count; exact ties break to the lexicographically smallest
    receptacle. A tie means routine knowledge genuinely cannot separate
    the tied receptacles, so any deterministic choice is as honest as
    another and this one is reproducible."""
    top = max(counter.values())
    return min(r for r, c in counter.items() if c == top)


def oracle_predictions(timeline: pathlib.Path, episode: Episode,
                       n_seeds: int = DEFAULT_ORACLE_SEEDS,
                       seed_base: int = ORACLE_SEED_BASE
                       ) -> Optional[Tuple[List[str], Dict[str, Any]]]:
    """(modal receptacle per bank question in question order, stats), or
    None when the household has no stored program to re-realize. Seeds
    seed_base+1 .. seed_base+n_seeds; the bank's own world is never one
    of them."""
    hh_dir = timeline.resolve().parent
    program_path = hh_dir / "program.yaml"
    if not program_path.exists():
        logger.info("routine oracle: no %s — skipping", program_path)
        return None
    program = yaml.safe_load(program_path.read_text())
    if int(program["days"]) != episode.n_days:
        logger.warning(
            "routine oracle: program days %s != episode days %s — skipping",
            program["days"], episode.n_days)
        return None

    sim = _load_realizer()
    engine = sim.load_v1()
    params = sim.load_params()
    questions = [(q.object_id, q.t_query)
                 for day in episode.questions_by_day for q in day]
    counts: List["collections.Counter[str]"] = [
        collections.Counter() for _ in questions]
    # Two DISJOINT halves, not a prefix and the whole: the stability
    # figure must compare independent estimates.
    half_counts: List[List["collections.Counter[str]"]] = [
        [collections.Counter() for _ in questions] for _ in range(2)]
    half = n_seeds // 2
    for k in range(1, n_seeds + 1):
        seed = seed_base + k
        truth = _realized_truth(sim, engine, params, program, hh_dir, seed)
        for i, (object_id, t_query) in enumerate(questions):
            if object_id not in truth:
                raise ValueError(
                    f"routine oracle: {object_id!r} missing from the "
                    f"seed-{seed} realization of {hh_dir} — the stored "
                    f"program has drifted from the bank")
            receptacle = truth_at(truth[object_id], t_query)
            counts[i][receptacle] += 1
            half_counts[0 if k <= half else 1][i][receptacle] += 1

    modal = [_modal_receptacle(c) for c in counts]

    def accuracy(preds: List[str]) -> float:
        hits = sum(pred == episode.true_location(obj, t)
                   for pred, (obj, t) in zip(preds, questions))
        return round(hits / len(questions), 4) if questions else 0.0

    full = accuracy(modal)
    halves = [accuracy([_modal_receptacle(c) for c in cs])
              for cs in half_counts]
    delta = round(abs(halves[0] - halves[1]), 4)
    logger.info(
        "routine oracle: %s — accuracy %.4f over %d seeds "
        "(disjoint halves %.4f / %.4f, delta %.4f)",
        hh_dir.name, full, n_seeds, halves[0], halves[1], delta)
    stats = {
        "n_seeds": n_seeds,
        "seed_range": [seed_base + 1, seed_base + n_seeds],
        "n_questions": len(questions),
        "accuracy": full,
        "accuracy_halves": [halves[0], halves[1]],
        "half_split_delta": delta,
        "note": ("perfect routine knowledge, no observations; NOT a hard "
                 "ceiling — models with fresh sightings can exceed it"),
    }
    return modal, stats


def build_oracle_section(timeline: pathlib.Path, episode: Episode,
                         n_seeds: int = DEFAULT_ORACLE_SEEDS
                         ) -> Optional[Dict[str, Any]]:
    """The budget sweep's oracle entry, or None when not computable."""
    result = oracle_predictions(timeline, episode, n_seeds)
    return None if result is None else result[1]
