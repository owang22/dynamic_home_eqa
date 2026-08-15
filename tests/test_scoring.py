"""Regression tests for the shared scoring path.

The uniform-floor test is the one that matters: it is the assertion the
superseded pilot lacked, and its absence let a tie-break artifact be
reported as a chance baseline for three protocols.
"""

from __future__ import annotations

import math
import random

import pytest

from beliefsim.scoring import (DEFAULT_SEEDS, aggregate, aggregation_note,
                               argmax_tiebroken, brier, log_loss,
                               score_instant, unit_counts)


def test_uniform_predictor_scores_chance():
    """A flat belief must score 1/|R|, not the occupancy of whichever
    receptacle sorts first."""
    receptacles = [f"rec_{i:02d}" for i in range(20)]
    flat = {r: 1.0 / len(receptacles) for r in receptacles}
    # Ground truth concentrated on ONE receptacle, and deliberately the
    # alphabetically-first one: key-order tie-breaking would score 1.0 here.
    truths = [receptacles[0]] * 2000
    accs = []
    for seed in DEFAULT_SEEDS:
        rng = random.Random(seed)
        hits = sum(score_instant(flat, t, receptacles, rng)["correct"]
                   for t in truths)
        accs.append(hits / len(truths))
    mean = sum(accs) / len(accs)
    assert abs(mean - 1.0 / len(receptacles)) < 0.01, accs


def test_uniform_predictor_scores_chance_on_spread_truth():
    receptacles = [f"rec_{i:02d}" for i in range(10)]
    flat = {r: 0.1 for r in receptacles}
    rng = random.Random(0)
    truths = [receptacles[i % 10] for i in range(5000)]
    hits = sum(score_instant(flat, t, receptacles, rng)["correct"]
               for t in truths)
    assert abs(hits / len(truths) - 0.1) < 0.02


def test_argmax_tiebreak_is_seeded_and_covers_all_tied_keys():
    dist = {"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25}
    picks = {argmax_tiebroken(dist, random.Random(s)) for s in range(50)}
    assert picks == {"a", "b", "c", "d"}
    # Same seed, same answer: the tie-break must not make runs irreproducible.
    assert (argmax_tiebroken(dist, random.Random(7))
            == argmax_tiebroken(dist, random.Random(7)))


def test_argmax_tiebreak_does_not_shuffle_a_real_ranking():
    dist = {"a": 0.4, "b": 0.3, "c": 0.3}
    assert {argmax_tiebroken(dist, random.Random(s)) for s in range(20)} \
        == {"a"}


def test_argmax_insertion_order_does_not_decide():
    """The pilot's failure mode: a flat dict whose first key wins."""
    forward = {"a": 0.5, "b": 0.5}
    backward = {"b": 0.5, "a": 0.5}
    assert (argmax_tiebroken(forward, random.Random(3))
            == argmax_tiebroken(backward, random.Random(3)))


def test_brier_and_log_loss_bounds():
    recs = ["a", "b", "c", "d"]
    perfect = {"a": 1.0}
    assert brier(perfect, "a", recs) == pytest.approx(0.0)
    assert log_loss(perfect, "a") == pytest.approx(0.0)
    flat = {r: 0.25 for r in recs}
    assert brier(flat, "a", recs) == pytest.approx(0.75)
    assert log_loss(flat, "a") == pytest.approx(math.log(4))
    # Confident and wrong is punished far harder than uninformative.
    assert log_loss({"b": 1.0}, "a") > 5 * log_loss(flat, "a")


def test_brier_scores_over_full_receptacle_set():
    """Omitting receptacles must not be rewarded."""
    recs = ["a", "b", "c", "d"]
    truncated = {"a": 1.0}
    assert brier(truncated, "b", recs) == pytest.approx(2.0)


def test_micro_and_macro_differ_and_are_explicit():
    rows = ([{"household": "A", "correct": 1.0}] * 90
            + [{"household": "A", "correct": 0.0}] * 10
            + [{"household": "B", "correct": 0.0}] * 2)
    assert aggregate(rows, "correct", mode="micro") \
        == pytest.approx(90 / 102)
    assert aggregate(rows, "correct", mode="macro") == pytest.approx(0.45)
    with pytest.raises(ValueError):
        aggregate(rows, "correct", mode="weighted")
    assert "MICRO" in aggregation_note("micro")
    assert "MACRO" in aggregation_note("macro")


def test_unit_counts_expose_unequal_contribution():
    rows = ([{"household": "A", "x": 1.0}] * 3
            + [{"household": "B", "x": ""}] * 5)
    assert unit_counts(rows, "x") == {"A": 3}
