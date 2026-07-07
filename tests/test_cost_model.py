"""
Tests for the E1 (travel-cost heterogeneity) cost_model toggle:
embodied/config.py's CostModelConfig and the travel_time_to closure in
runner.py's run_question that consults it.

Pure logic — a duck-typed FakeWorld stands in for EmbodiedWorld so these
run without habitat_sim, matching this repo's existing split between
smoke tests (real EmbodiedWorld, tests/test_embodied_smoke.py) and
policy/runner-logic tests (fakes, e.g. tests/test_belief.py).
"""
from __future__ import annotations

import math

from dynamic_home_eqa.embodied.config import AgentConfig, CostModelConfig
from dynamic_home_eqa.embodied.question import MCQQuestion
from dynamic_home_eqa.embodied.runner import EpisodeConfig, QuestionEpisodeRunner
from dynamic_home_eqa.embodied.scoring import Abstain
from dynamic_home_eqa.embodied.types import Pose
from dynamic_home_eqa.env.state import SceneState

_KNOWN_ANCHOR = "kitchen.counter"
_UNREACHABLE_ANCHOR = "attic.shelf"
_REAL_COST_SECONDS = 42.0


class _FakeViewpoint:
    def __init__(self) -> None:
        self.position = (1.0, 0.0, 1.0)
        self.yaw_rad = 0.0


class _FakeWorld:
    """Duck-typed EmbodiedWorld stand-in exposing only what run_question's
    travel_time_to closure and _score need: config, pose, t, viewpoint_for,
    geodesic_time, initial_state, changes."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.pose = Pose(0.0, 0.0, 0.0, 0.0)
        self.t = 10.0
        self.initial_state = SceneState()
        self.changes: list = []

    def viewpoint_for(self, anchor: str):
        return _FakeViewpoint() if anchor == _KNOWN_ANCHOR else None

    def geodesic_time(self, a, b) -> float:
        return _REAL_COST_SECONDS


class _RecordingPolicy:
    """Calls travel_time_to for both a reachable and an unreachable anchor,
    records what it saw, then abstains — isolating the closure's own
    behavior from any belief/search logic."""

    def __init__(self) -> None:
        self.observed_known: "float | None" = None
        self.observed_unreachable: "float | None" = None

    def act(self, belief, question, pose, t, config, travel_time_to):
        self.observed_known = travel_time_to(_KNOWN_ANCHOR)
        self.observed_unreachable = travel_time_to(_UNREACHABLE_ANCHOR)
        return Abstain()


def _question() -> MCQQuestion:
    return MCQQuestion(
        label="mug_1", category="mug", stem="Where is the mug?",
        options=("kitchen.counter", "OUTSIDE"), correct_index=0, asked_t=10.0,
        hazard_class="stable", distractor_provenance=("real", "real"),
    )


def _run(cost_model: CostModelConfig) -> _RecordingPolicy:
    world = _FakeWorld(AgentConfig(cost_model=cost_model))
    policy = _RecordingPolicy()
    runner = QuestionEpisodeRunner(world, belief=None, policy=policy, episode_config=EpisodeConfig())
    runner.run_question(_question())
    return policy


class TestCostModelConfig:
    def test_default_mode_is_real_geodesic(self):
        assert CostModelConfig().mode == "real_geodesic"

    def test_is_frozen(self):
        cfg = CostModelConfig()
        try:
            cfg.mode = "flat"
        except Exception:
            pass
        else:
            raise AssertionError("CostModelConfig must be frozen")

    def test_agent_config_defaults_to_real_geodesic(self):
        assert AgentConfig().cost_model.mode == "real_geodesic"


class TestTravelTimeToClosure:
    def test_real_geodesic_mode_reports_the_real_cost(self):
        policy = _run(CostModelConfig(mode="real_geodesic"))
        assert policy.observed_known == _REAL_COST_SECONDS

    def test_flat_mode_reports_the_flat_constant_for_a_reachable_anchor(self):
        policy = _run(CostModelConfig(mode="flat", flat_leg_seconds=7.0))
        assert policy.observed_known == 7.0
        assert policy.observed_known != _REAL_COST_SECONDS

    def test_flat_mode_still_reports_inf_for_an_unreachable_anchor(self):
        policy = _run(CostModelConfig(mode="flat", flat_leg_seconds=7.0))
        assert policy.observed_unreachable == math.inf

    def test_real_geodesic_mode_also_reports_inf_for_an_unreachable_anchor(self):
        policy = _run(CostModelConfig(mode="real_geodesic"))
        assert policy.observed_unreachable == math.inf
