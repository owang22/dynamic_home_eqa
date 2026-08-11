"""Unit tests for the shared negative-evidence (exclusion) bookkeeping in
the belief base class. Times are seconds since episode start."""

from __future__ import annotations

import logging
import random

import pytest

from baselines.beliefs import LastObservation, MostFrequentLocation
from baselines.types import EpisodeContext, Observation, SenseResult

RECS = ("a", "b", "c")


def _context(objects: dict[str, str] | None = None) -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=RECS,
        object_classes=objects or {"o": "mug"}, budget_per_day=1, n_days=2)


def _obs(rec: str, t: int, obj: str = "o") -> Observation:
    return Observation(object_id=obj, object_class="mug", receptacle_id=rec,
                       t=t, source="scripted")


def _empty_sense(rec: str, t: int) -> SenseResult:
    return SenseResult(receptacle_id=rec, t=t, contents=())


def test_exclusion_zeroes_the_sensed_receptacle() -> None:
    model = LastObservation(random.Random(0))
    model.reset(_context())
    model.update(_obs("a", 10))
    model.update(_empty_sense("a", 20))
    # The one-hot base mass on a is reclaimed and spread uniformly over
    # the receptacles not yet ruled out (the brief's uniform fallback).
    pred = model.predict("o", 30)
    assert pred.distribution["a"] == 0.0
    assert pred.distribution["b"] == pytest.approx(0.5)
    assert pred.distribution["c"] == pytest.approx(0.5)
    assert pred.argmax in ("b", "c")


def test_exclusion_from_nonempty_contents() -> None:
    # Absence is evidence even when the sense saw other objects.
    model = LastObservation(random.Random(0))
    model.reset(_context({"o": "mug", "decoy": "coin"}))
    model.update(_obs("a", 10))
    model.update(_obs("a", 10, obj="decoy"))
    model.update(SenseResult(receptacle_id="a", t=20, contents=("decoy",)))
    assert model.predict("o", 30).distribution["a"] == 0.0
    assert model.predict("decoy", 30).argmax == "a"


def test_exclusion_invalidated_by_later_positive() -> None:
    model = LastObservation(random.Random(0))
    model.reset(_context())
    model.update(_obs("a", 10))
    model.update(_empty_sense("a", 20))
    model.update(_obs("a", 30))     # strictly later sighting: back at a
    pred = model.predict("o", 40)
    assert pred.argmax == "a"
    assert pred.distribution == {"a": 1.0}


def test_exclusion_survives_equal_time_positive_elsewhere() -> None:
    # Seeing o at b at the same instant a was sensed empty is consistent
    # with (and does not invalidate) the a-exclusion.
    model = MostFrequentLocation(random.Random(0))
    model.reset(_context())
    model.update(_obs("a", 10))
    model.update(_obs("a", 12))
    model.update(_empty_sense("a", 20))
    model.update(_obs("b", 20))
    pred = model.predict("o", 25)
    assert pred.distribution["a"] == 0.0
    assert pred.argmax == "b"
    assert sum(pred.distribution.values()) == pytest.approx(1.0)


def test_all_excluded_falls_back_with_warning(
        caplog: pytest.LogCaptureFixture) -> None:
    model = LastObservation(random.Random(0))
    model.reset(_context())
    model.update(_obs("a", 10))
    for i, rec in enumerate(RECS):
        model.update(_empty_sense(rec, 20 + i))
    with caplog.at_level(logging.WARNING, logger="baselines.beliefs.base"):
        pred = model.predict("o", 40)
    # Exclusions are ignored entirely (base one-hot on a) and the warning
    # names the object and query time.
    assert pred.distribution == {"a": 1.0}
    assert any("o" in rec.message and "t=40" in rec.message
               for rec in caplog.records)


def test_renormalization_always_sums_to_one() -> None:
    model = MostFrequentLocation(random.Random(0))
    model.reset(_context())
    for rec, t in (("a", 10), ("a", 11), ("b", 12)):
        model.update(_obs(rec, t))
    model.update(_empty_sense("a", 20))
    pred = model.predict("o", 30)
    # Excluded mass (2/3) spreads over {b, c}: b = 1/3 + 1/3, c = 1/3.
    assert sum(pred.distribution.values()) == pytest.approx(1.0)
    assert pred.distribution["a"] == 0.0
    assert pred.distribution["b"] == pytest.approx(2 / 3)
    assert pred.distribution["c"] == pytest.approx(1 / 3)
    assert pred.argmax == "b"


def test_exclusion_floor_keeps_epsilon_mass() -> None:
    model = LastObservation(random.Random(0), exclusion_floor=0.01)
    model.reset(_context())
    model.update(_obs("a", 10))
    model.update(_empty_sense("a", 20))
    pred = model.predict("o", 30)
    assert pred.distribution["a"] == pytest.approx(0.01)
    assert sum(pred.distribution.values()) == pytest.approx(1.0)


def test_exclusion_floor_validation() -> None:
    with pytest.raises(ValueError, match="exclusion_floor"):
        LastObservation(random.Random(0), exclusion_floor=0.5)


def test_query_instant_sighting_outvotes_history() -> None:
    # A positive sighting AT the prediction instant is ground truth then;
    # frequency history must not outvote it.
    model = MostFrequentLocation(random.Random(0))
    model.reset(_context())
    for t in (10, 11, 12, 13):
        model.update(_obs("a", t))
    model.update(SenseResult(receptacle_id="b", t=100, contents=("o",)))
    pred = model.predict("o", 100)
    assert pred.argmax == "b"
    assert pred.distribution == {"b": 1.0}
    # One second later the sighting is ordinary history again and the
    # frequency mode (a: 4 sightings vs b: 1) wins back the argmax.
    assert model.predict("o", 101).argmax == "a"
