"""
Tests for embodied/policy.py's two E2 control baselines:
RandomResense (budget_matched_random) and TimeOnlyThreshold
(time_only_threshold) — cheap, model-free comparison points the LLM agent
(L1+) will also need to beat, per results/reports/INDEX.md.

Pure logic — belief.BeliefStore, no habitat_sim needed.
"""
from __future__ import annotations

from dynamic_home_eqa.embodied.belief import BeliefStore, DecayModel
from dynamic_home_eqa.embodied.policy import (
    ResensePlan,
    RandomResense,
    RandomResenseConfig,
    TimeOnlyThreshold,
    TimeOnlyThresholdConfig,
    _deterministic_unit_interval,
)
from dynamic_home_eqa.embodied.question import MCQQuestion
from dynamic_home_eqa.embodied.scoring import Abstain, Choice
from dynamic_home_eqa.embodied.types import OracleDetection, Pose

_POSE = Pose(0.0, 0.0, 0.0, 0.0)


def _question(options=("shelf", "table", "OUTSIDE")) -> MCQQuestion:
    return MCQQuestion(
        label="book_1", category="book", stem="Where is the book?",
        options=options, correct_index=0, asked_t=1.0,
        hazard_class="stable", distractor_provenance=("real", "real", "real"),
    )


def _empty_store() -> BeliefStore:
    return BeliefStore(decay_models={"book": DecayModel("book", lambda_per_hour=0.5)})


def _observed_store(anchor="shelf", t=0.0) -> BeliefStore:
    store = _empty_store()
    store.observe_detection(
        OracleDetection(label="book_1", category="book", world_pos=(0, 0, 0), anchor=anchor, t=t),
        _POSE,
    )
    return store


class TestDeterministicUnitInterval:
    def test_deterministic_given_same_inputs(self):
        a = _deterministic_unit_interval(seed=7, label="book_1", t=3.5)
        b = _deterministic_unit_interval(seed=7, label="book_1", t=3.5)
        assert a == b

    def test_in_unit_interval(self):
        for t in (0.0, 1.0, 4.0, 24.0):
            v = _deterministic_unit_interval(seed=1, label="x", t=t)
            assert 0.0 <= v < 1.0

    def test_varies_with_seed(self):
        a = _deterministic_unit_interval(seed=1, label="book_1", t=3.5)
        b = _deterministic_unit_interval(seed=2, label="book_1", t=3.5)
        assert a != b


class TestRandomResense:
    def test_abstains_when_nothing_believed(self):
        store = _empty_store()
        decision = RandomResense(RandomResenseConfig(p_resense=1.0)).act(
            store, _question(), _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0,
        )
        assert decision == Abstain()

    def test_p_one_always_resenses_when_something_is_believed_and_not_just_confirmed(self):
        store = _observed_store(t=0.0)
        decision = RandomResense(RandomResenseConfig(p_resense=1.0)).act(
            store, _question(), _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0,
        )
        assert isinstance(decision, ResensePlan)

    def test_p_zero_never_resenses(self):
        store = _observed_store(t=0.0)
        decision = RandomResense(RandomResenseConfig(p_resense=0.0)).act(
            store, _question(), _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0,
        )
        assert isinstance(decision, Choice)

    def test_just_confirmed_answers_regardless_of_p(self):
        # Observed at t=5.0 and asked again at t=5.0 (within the "just
        # observed" epsilon) — should answer immediately even at p=1.0,
        # matching every other search policy's _just_confirmed short-circuit.
        store = _observed_store(t=5.0)
        decision = RandomResense(RandomResenseConfig(p_resense=1.0)).act(
            store, _question(), _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0,
        )
        assert isinstance(decision, Choice)

    def test_deterministic_across_repeated_calls(self):
        store = _observed_store(t=0.0)
        cfg = RandomResenseConfig(p_resense=0.5, seed=3)
        d1 = RandomResense(cfg).act(store, _question(), _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0)
        d2 = RandomResense(cfg).act(store, _question(), _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0)
        assert type(d1) == type(d2)


class TestTimeOnlyThreshold:
    def test_abstains_when_nothing_believed(self):
        store = _empty_store()
        decision = TimeOnlyThreshold().act(
            store, _question(), _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0,
        )
        assert decision == Abstain()

    def test_answers_immediately_when_within_threshold(self):
        store = _observed_store(t=4.5)
        decision = TimeOnlyThreshold(TimeOnlyThresholdConfig(threshold_hours=1.0)).act(
            store, _question(), _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0,
        )
        assert decision == Choice(option_index=0, confidence=1.0)

    def test_resenses_once_past_threshold(self):
        store = _observed_store(t=0.0)
        decision = TimeOnlyThreshold(TimeOnlyThresholdConfig(threshold_hours=1.0)).act(
            store, _question(), _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0,
        )
        assert isinstance(decision, ResensePlan)

    def test_ignores_category_decay_rate(self):
        # Two categories with very different fitted hazard rates should
        # make the identical stale/not-stale call at the identical elapsed
        # time — the whole point of "category-blind".
        fast = BeliefStore(decay_models={"book": DecayModel("book", lambda_per_hour=5.0)})
        slow = BeliefStore(decay_models={"book": DecayModel("book", lambda_per_hour=0.01)})
        for store in (fast, slow):
            store.observe_detection(
                OracleDetection(label="book_1", category="book", world_pos=(0, 0, 0), anchor="shelf", t=0.0),
                _POSE,
            )
        cfg = TimeOnlyThresholdConfig(threshold_hours=1.0)
        d_fast = TimeOnlyThreshold(cfg).act(fast, _question(), _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0)
        d_slow = TimeOnlyThreshold(cfg).act(slow, _question(), _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0)
        assert isinstance(d_fast, ResensePlan)
        assert isinstance(d_slow, ResensePlan)

    def test_confidence_is_flat_one_not_validity(self):
        store = _observed_store(t=4.5)
        decision = TimeOnlyThreshold(TimeOnlyThresholdConfig(threshold_hours=1.0)).act(
            store, _question(), _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0,
        )
        assert isinstance(decision, Choice)
        assert decision.confidence == 1.0
