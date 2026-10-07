"""Open object set: belief models discover objects lazily instead of
requiring the object list at reset. Times are seconds since episode
start."""

from __future__ import annotations

import random

import pytest

from baselines.beliefs import MostFrequentLocation
from baselines.beliefs.base import cold_start_distribution
from baselines.beliefs.hierarchy_backoff import (HierarchyBackoff,
                                                 HierarchyBackoffConfig)
from baselines.types import EpisodeContext, Observation, SenseResult

RECS = ("counter_k", "desk_o", "entry_e", "shelf_l")


def _open_context() -> EpisodeContext:
    """A context with NO object list: everything is discovered."""
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=RECS,
        budget_per_day=2, n_days=3)


def _obs(obj: str, cls: str, rec: str, t: int) -> Observation:
    return Observation(object_id=obj, object_class=cls, receptacle_id=rec,
                       t=t, source="scripted")


def test_predict_unregistered_object_returns_cold_start() -> None:
    """No exception, and the pooled cold-start distribution (through the
    identity pipeline at floor_mass 0)."""
    model = HierarchyBackoff(random.Random(0), HierarchyBackoffConfig(),
                             floor_mass=0.0)
    model.reset(_open_context())
    model.update(_obs("mug_1", "mug", "counter_k", 100))
    model.update(_obs("mug_1", "mug", "counter_k", 200))
    model.update(_obs("keys_1", "keys", "entry_e", 300))
    pred = model.predict("mug_2", 400)   # never registered, never sighted
    tracked = {"mug_1": ("mug", [(100, "counter_k"), (200, "counter_k")]),
               "keys_1": ("keys", [(300, "entry_e")])}
    # mug_2 has an unknown class here (never registered), so the pool is
    # the household-wide counts.
    expected = cold_start_distribution(None, tracked, RECS, 400)
    for rec, p in expected.items():
        assert pred.distribution[rec] == pytest.approx(p)
    assert abs(sum(pred.distribution.values()) - 1.0) < 1e-9


def test_object_registered_by_question_then_moves_on_sighting() -> None:
    model = MostFrequentLocation(random.Random(0), floor_mass=0.0)
    model.reset(_open_context())
    model.ensure_object("keys_1", "keys")     # what the harness does
    before = model.predict("keys_1", 10)
    assert abs(sum(before.distribution.values()) - 1.0) < 1e-9
    model.update(_obs("keys_1", "keys", "entry_e", 20))
    after = model.predict("keys_1", 30)
    # One sighting, so the frequency path's Dirichlet prior keeps real
    # mass on every other receptacle.
    assert after.argmax == "entry_e"
    assert 0.3 < after.distribution["entry_e"] < 1.0


def test_object_registered_from_sense_result() -> None:
    model = MostFrequentLocation(random.Random(0), floor_mass=0.0)
    model.reset(_open_context())
    model.update(SenseResult(receptacle_id="desk_o", t=50,
                             contents=("laptop_1",),
                             object_classes={"laptop_1": "laptop"}))
    assert model.known_objects == {"laptop_1": "laptop"}
    pred = model.predict("laptop_1", 60)
    assert pred.argmax == "desk_o"
    # A later sense elsewhere excludes laptop_1 there (it is now a known
    # object), leaving the registration usable end to end.
    model.update(SenseResult(receptacle_id="entry_e", t=70, contents=()))
    assert model.negative_observations("laptop_1", 80) == {"entry_e": 70}


def test_cold_start_class_without_siblings_uses_household_pool() -> None:
    tracked = {"mug_1": ("mug", [(100, "counter_k")]),
               "book_1": ("book", [(100, "shelf_l"), (200, "shelf_l")])}
    dist = cold_start_distribution("keys", tracked, RECS, 300)
    # No tracked keys: the class pool is empty, weight 0, so the result
    # is exactly the household-wide pool.
    household = cold_start_distribution(None, tracked, RECS, 300)
    assert dist == pytest.approx(household)
    assert abs(sum(dist.values()) - 1.0) < 1e-9
    # And with no tracked objects at all: uniform.
    empty = cold_start_distribution("keys", {}, RECS, 0)
    assert empty == {r: pytest.approx(1 / len(RECS)) for r in RECS}
