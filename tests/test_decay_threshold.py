"""
Tests for embodied/policy.py's DecayThreshold Mondrian (per-wait-bucket)
theta mode — the coverage-repair phase's fix for a global theta's dwell-
time covariate shift (see belief.calibrate_conformal_theta_by_wait's own
docstring). Pure logic — belief.BeliefStore, no habitat_sim needed.
"""
from __future__ import annotations

from dynamic_home_eqa.embodied.belief import BeliefStore, DecayModel
from dynamic_home_eqa.embodied.policy import DecayThreshold, DecayThresholdConfig
from dynamic_home_eqa.embodied.scoring import Abstain, Choice
from dynamic_home_eqa.embodied.types import OracleDetection, Pose

_POSE = Pose(0.0, 0.0, 0.0, 0.0)


def _observed_store(t=0.0, lambda_per_hour=0.5) -> BeliefStore:
    store = BeliefStore(decay_models={"book": DecayModel("book", lambda_per_hour=lambda_per_hour)})
    store.observe_detection(
        OracleDetection(label="book_1", category="book", world_pos=(0, 0, 0), anchor="shelf", t=t),
        _POSE,
    )
    return store


class TestThetaFor:
    def test_scalar_theta_ignores_elapsed_time(self):
        policy = DecayThreshold(DecayThresholdConfig(theta=0.42))
        store = _observed_store(t=0.0)
        assert policy._theta_for(store, "book_1", t=100.0) == 0.42

    def test_bucketed_theta_picks_the_nearest_bucket_to_elapsed_time(self):
        policy = DecayThreshold(DecayThresholdConfig(theta_by_wait={0.25: 0.9, 1.0: 0.5, 4.0: 0.1}))
        store = _observed_store(t=0.0)
        assert policy._theta_for(store, "book_1", t=0.3) == 0.9   # elapsed=0.3, closest to 0.25
        assert policy._theta_for(store, "book_1", t=1.1) == 0.5   # elapsed=1.1, closest to 1.0
        assert policy._theta_for(store, "book_1", t=5.0) == 0.1   # elapsed=5.0, closest to 4.0

    def test_bucketed_theta_falls_back_to_scalar_when_never_observed(self):
        policy = DecayThreshold(DecayThresholdConfig(theta=0.33, theta_by_wait={0.25: 0.9}))
        store = BeliefStore(decay_models={})
        assert policy._theta_for(store, "never_seen", t=1.0) == 0.33

    def test_default_theta_by_wait_is_none(self):
        assert DecayThresholdConfig().theta_by_wait is None


class TestActUsesTheSelectedTheta:
    def test_bucketed_theta_can_trigger_resense_where_scalar_would_not(self):
        # validity at elapsed=1.0h under lambda=0.5 is exp(-0.5)=0.607.
        # A bucketed theta of 0.9 at that bucket should trigger a resense
        # (validity < theta); the scalar default (0.5) would not.
        store = _observed_store(t=0.0, lambda_per_hour=0.5)
        scalar_policy = DecayThreshold(DecayThresholdConfig(theta=0.5))
        bucketed_policy = DecayThreshold(DecayThresholdConfig(theta_by_wait={1.0: 0.9}))

        from dynamic_home_eqa.embodied.question import MCQQuestion
        question = MCQQuestion(
            label="book_1", category="book", stem="Where is the book?",
            options=("shelf", "OUTSIDE"), correct_index=0, asked_t=1.0,
            hazard_class="stable", distractor_provenance=("real", "real"),
        )

        scalar_decision = scalar_policy.act(store, question, _POSE, t=1.0, config=None, travel_time_to=lambda a: 1.0)
        bucketed_decision = bucketed_policy.act(store, question, _POSE, t=1.0, config=None, travel_time_to=lambda a: 1.0)

        assert isinstance(scalar_decision, (Choice, Abstain)) or hasattr(scalar_decision, "targets")
        # scalar theta=0.5 <= validity=0.607 -> answers immediately (Choice)
        assert isinstance(scalar_decision, Choice)
        # bucketed theta=0.9 > validity=0.607 -> wants to resense
        assert not isinstance(bucketed_decision, Choice)
