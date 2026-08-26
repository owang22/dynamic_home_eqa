"""Unit tests for the candidate belief slate (registry-tagged candidate).

Covers: hand-computed hazard estimation (the periodic_persistence
estimator the paper baseline rests on), markov1 transition rows and
mixing backoff, hierarchy_backoff pooling for never-sighted objects,
daytype clustering, and the registry's frozen-panel assertion.
"""
from __future__ import annotations

import math
import random

import pytest

from baselines.beliefs.hierarchy_backoff import (HierarchyBackoff,
                                                 HierarchyBackoffConfig)
from baselines.beliefs.markov1 import Markov1, Markov1Config
from baselines.beliefs.periodic_persistence import (PeriodicPersistence,
                                                    PeriodicPersistenceConfig,
                                                    estimate_dwell)
from baselines.registry import (BELIEF_REGISTRY, CANDIDATE_SLATE,
                                assert_frozen_panel, build_registered_belief)
from baselines.types import DAY_SECONDS, EpisodeContext, Observation

_H = 3600


def _context(receptacles=("a", "b", "c"), classes=None) -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep0", household_id="hh0",
        receptacle_ids=tuple(receptacles),
        object_classes=classes or {"obj": "widget"},
        budget_per_day=2, n_days=7)


def _obs(obj: str, t: int, rec: str) -> Observation:
    return Observation(object_id=obj, object_class="widget",
                       receptacle_id=rec, t=t, source="scripted")


# ---------------------------------------------------------------- hazard


def test_estimate_dwell_hand_computed():
    # (0,a)->(10,a): 10s exposure at a, no departure.
    # (10,a)->(30,b): 20s exposure at a, one departure from a.
    # (30,b)->(40,b): 10s exposure at b.  (40,b)->(70,a): 30s + departure.
    est = estimate_dwell([(0, "a"), (10, "a"), (30, "b"), (40, "b"),
                          (70, "a")])
    assert est.exposure_s == {"a": 30, "b": 40}
    assert est.departures == {"a": 1, "b": 1}
    assert est.rate("a", min_departures=1) == pytest.approx(1 / 30)
    # Below the per-receptacle floor: pooled rate 2 departures / 70s.
    assert est.rate("a", min_departures=2) == pytest.approx(2 / 70)
    # Below even the pooled floor: no usable hazard.
    assert est.rate("a", min_departures=3) is None


def test_estimate_dwell_ignores_zero_gaps():
    est = estimate_dwell([(5, "a"), (5, "b"), (10, "b")])
    assert est.exposure_s == {"b": 5}
    assert est.departures == {}


def test_periodic_persistence_stay_probability_hand_computed():
    # One departure from a after exactly 100s of single-interval exposure:
    # rate(a) = 1/100 with min_departures=1; back at a at t=300, queried
    # at t=400 -> p_stay = exp(-100/100) = e^-1 on a, remainder on the
    # time-of-day histogram.
    belief = PeriodicPersistence(
        random.Random(0),
        PeriodicPersistenceConfig(min_departures=1))
    belief.reset(_context())
    for t, rec in ((0, "a"), (100, "b"), (300, "a")):
        belief.update(_obs("obj", t, rec))
    prediction = belief.predict("obj", 400)
    # histogram over sightings (all in one 1h bin): a=2 of 3 (decay is
    # negligible over 400s), so p(a) = e^-1 + (1-e^-1) * 2/3.
    expected_a = math.exp(-1.0) + (1 - math.exp(-1.0)) * (2 / 3)
    assert prediction.distribution["a"] == pytest.approx(expected_a, abs=1e-3)
    assert prediction.argmax == "a"


def test_periodic_persistence_few_transitions_degrades_to_frequency():
    belief = PeriodicPersistence(random.Random(0),
                                 PeriodicPersistenceConfig())
    belief.reset(_context())
    belief.update(_obs("obj", 0, "a"))
    belief.update(_obs("obj", 100, "a"))    # zero departures anywhere
    prediction = belief.predict("obj", DAY_SECONDS)
    assert prediction.argmax == "a"
    assert prediction.distribution["a"] == pytest.approx(1.0)


# ---------------------------------------------------------------- markov1


def test_markov1_transition_row_within_cutoff():
    belief = Markov1(random.Random(0),
                     Markov1Config(alpha=1.0, mixing_cutoff_h=24,
                                   half_life_h=1e9))  # decay off in effect
    belief.reset(_context())
    # Pairs from a: (0,a)->(10,b) and (20,a)->(30,b); last sighting at a.
    for t, rec in ((0, "a"), (10, "b"), (20, "a"), (30, "b"), (40, "a")):
        belief.update(_obs("obj", t, rec))
    prediction = belief.predict("obj", 50)
    # Row from a: count b=2 (b->a transitions belong to row b), plus
    # alpha=1 everywhere: a=1, b=3, c=1, total 5.
    assert prediction.distribution["b"] == pytest.approx(3 / 5, abs=1e-6)
    assert prediction.distribution["a"] == pytest.approx(1 / 5, abs=1e-6)
    assert prediction.argmax == "b"


def test_markov1_backs_off_to_frequency_beyond_cutoff():
    belief = Markov1(random.Random(0), Markov1Config(mixing_cutoff_h=1))
    belief.reset(_context())
    for t, rec in ((0, "a"), (10, "b"), (20, "a")):
        belief.update(_obs("obj", t, rec))
    prediction = belief.predict("obj", 2 * _H + 30)
    # Beyond the cutoff: the decayed frequency histogram (a twice, b once).
    assert prediction.argmax == "a"
    assert prediction.distribution["b"] < prediction.distribution["a"]
    assert "c" not in prediction.distribution


# ------------------------------------------------------- hierarchy_backoff


def test_hierarchy_backoff_never_sighted_object_uses_class():
    classes = {"mug_1": "mug", "mug_2": "mug", "sock_1": "sock"}
    belief = HierarchyBackoff(random.Random(0), HierarchyBackoffConfig())
    belief.reset(_context(classes=classes))
    for t in (0, 10, 20):
        belief.update(_obs("mug_1", t, "a"))
    belief.update(_obs("sock_1", 30, "c"))
    # mug_2 was never sighted: its prediction leans on the mug class (a),
    # not uniform and not the global mode alone.
    prediction = belief.predict("mug_2", 100)
    assert prediction.argmax == "a"
    assert prediction.distribution["a"] > prediction.distribution["c"]


def test_hierarchy_backoff_no_evidence_is_uniform():
    belief = HierarchyBackoff(random.Random(0), HierarchyBackoffConfig())
    belief.reset(_context(classes={"obj": "widget"}))
    prediction = belief.predict("obj", 100)
    assert set(prediction.distribution) == {"a", "b", "c"}
    for p in prediction.distribution.values():
        assert p == pytest.approx(1 / 3)


# ---------------------------------------------------------------- registry


def test_registry_tags_and_builders():
    assert {s["name"] for s in CANDIDATE_SLATE} <= set(BELIEF_REGISTRY)
    for spec in CANDIDATE_SLATE:
        assert BELIEF_REGISTRY[str(spec["name"])].panel == "candidate"
        built = build_registered_belief(dict(spec), random.Random(0))
        assert built.name    # display name resolves


def test_assert_frozen_panel_accepts_the_real_panel():
    from baselines.healthcheck import BELIEF_PANEL
    assert_frozen_panel(BELIEF_PANEL)


def test_assert_frozen_panel_rejects_candidates():
    with pytest.raises(ValueError, match="candidate"):
        assert_frozen_panel(({"name": "last_observation"},
                             {"name": "markov1"}))
    with pytest.raises(ValueError, match="not registered"):
        assert_frozen_panel(({"name": "no_such_belief"},))


def test_healthcheck_refuses_candidate_panel(tmp_path, monkeypatch):
    """The healthcheck itself must refuse a tampered panel, not just the
    helper — a candidate in the instrument would silently change every
    gate."""
    import baselines.healthcheck as healthcheck
    from baselines.bank import write_synthetic_bank

    bank = write_synthetic_bank(tmp_path / "bank.jsonl")
    monkeypatch.setattr(
        healthcheck, "BELIEF_PANEL",
        (*healthcheck.BELIEF_PANEL, {"name": "periodic_persistence"}))
    with pytest.raises(ValueError, match="frozen"):
        healthcheck.run_healthcheck(bank.path,
                                    healthcheck.HealthcheckConfig(), None)
