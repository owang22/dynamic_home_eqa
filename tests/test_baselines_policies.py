"""Unit tests for the three basic decision policies."""

from __future__ import annotations

import pytest

from baselines.policies import (AlwaysSense, FixedSchedule,
                                FixedScheduleConfig, NeverSense)
from baselines.types import AnswerNow, EpisodeContext, Prediction, Question, Sense

H = 3600


def _context() -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=("a", "b"),
        object_classes={"o": "mug"}, budget_per_day=2, n_days=1)


def _question(qid: str = "q0", t: int = 10 * H) -> Question:
    return Question(question_id=qid, object_id="o", t_query=t,
                    day_index=t // 86400)


PRED = Prediction(distribution={"a": 0.75, "b": 0.25}, argmax="a")


def test_never_sense_always_answers() -> None:
    policy = NeverSense()
    assert isinstance(policy.decide(_question(), PRED, 5, 10 * H), AnswerNow)


def test_always_sense_senses_argmax_then_answers() -> None:
    policy = AlwaysSense()
    policy.reset(_context())
    first = policy.decide(_question(), PRED, 2, 10 * H)
    assert first == Sense(receptacle_id="a")
    # Re-asked for the same question after the sense: must terminate.
    second = policy.decide(_question(), PRED, 1, 10 * H)
    assert isinstance(second, AnswerNow)


def test_always_sense_respects_zero_budget() -> None:
    policy = AlwaysSense()
    policy.reset(_context())
    assert isinstance(policy.decide(_question(), PRED, 0, 10 * H), AnswerNow)


def test_fixed_schedule_rotation_order_and_cadence() -> None:
    policy = FixedSchedule(FixedScheduleConfig(rotation=("b", "a"),
                                               every_hours=6))
    policy.reset(_context())
    # First question: due immediately, patrols rotation[0].
    assert policy.decide(_question("q0", 1 * H), PRED, 2, 1 * H) == Sense("b")
    # Immediate re-ask: cadence not due -> answer (termination).
    assert isinstance(policy.decide(_question("q0", 1 * H), PRED, 1, 1 * H),
                      AnswerNow)
    # 5h later: still inside the 6h cadence.
    assert isinstance(policy.decide(_question("q1", 6 * H), PRED, 1, 6 * H),
                      AnswerNow)
    # 7h after the first sense: due again, rotation advances to "a".
    assert policy.decide(_question("q2", 8 * H), PRED, 1, 8 * H) == Sense("a")
    # Rotation wraps.
    assert policy.decide(_question("q3", 15 * H), PRED, 1, 15 * H) == Sense("b")


def test_fixed_schedule_ignores_budgetless_slots() -> None:
    policy = FixedSchedule(FixedScheduleConfig(rotation=("b",), every_hours=1))
    policy.reset(_context())
    assert isinstance(policy.decide(_question(), PRED, 0, 10 * H), AnswerNow)


def test_fixed_schedule_config_validation() -> None:
    with pytest.raises(ValueError, match="rotation"):
        FixedScheduleConfig(rotation=(), every_hours=1)
    with pytest.raises(ValueError, match="every_hours"):
        FixedScheduleConfig(rotation=("a",), every_hours=0)
