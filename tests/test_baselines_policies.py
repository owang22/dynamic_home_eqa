"""Unit tests for the basic decision policies."""

from __future__ import annotations

import random

import pytest

from baselines.policies import (FixedSchedule, FixedScheduleConfig,
                                NeverSense, SequentialSearch)
from baselines.types import (AnswerNow, EpisodeContext, Prediction, Question,
                             Sense, SenseResult)

H = 3600


def _context() -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=("a", "b"),
        object_classes={"o": "mug"}, budget_per_day=2, n_days=1)


def _question(qid: str = "q0", t: int = 10 * H) -> Question:
    return Question(question_id=qid, object_id="o", t_query=t,
                    day_index=t // 86400)


def _search(threshold: float = 1.0) -> SequentialSearch:
    policy = SequentialSearch(random.Random(0),
                              confidence_threshold=threshold)
    policy.reset(_context())
    return policy


PRED = Prediction(distribution={"a": 0.75, "b": 0.25}, argmax="a")
ONE_HOT = Prediction(distribution={"a": 1.0}, argmax="a")


def test_never_sense_always_answers() -> None:
    policy = NeverSense()
    assert isinstance(policy.decide(_question(), PRED, 5, 10 * H), AnswerNow)


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


def test_sequential_search_stops_when_object_found() -> None:
    policy = _search()
    q = _question()
    # First decide: senses the top-probability receptacle.
    assert policy.decide(q, PRED, 5, 10 * H) == Sense("a")
    # Miss: the exclusion-updated belief now ranks b; the search follows.
    empty = SenseResult(receptacle_id="a", t=10 * H, contents=())
    after_miss = Prediction(distribution={"a": 0.0, "b": 1.0}, argmax="b")
    assert policy.decide(q, after_miss, 4, 10 * H, empty) == Sense("b")
    # Hit: answer immediately.
    found = SenseResult(receptacle_id="b", t=10 * H, contents=("o",))
    assert isinstance(policy.decide(q, after_miss, 3, 10 * H, found),
                      AnswerNow)


def test_sequential_search_never_trusts_bare_certainty() -> None:
    # At the default threshold 1.0 a one-hot prediction alone must NOT
    # stop the search: one-hot beliefs claim certainty for stale
    # sightings. Only a sense that returns the object may answer early.
    policy = _search()
    assert policy.decide(_question(), ONE_HOT, 5, 10 * H) == Sense("a")


def test_sequential_search_threshold_answers_early() -> None:
    policy = _search(threshold=0.7)
    # 0.75 >= 0.7: trust the belief, answer without spending.
    assert isinstance(policy.decide(_question(), PRED, 5, 10 * H), AnswerNow)


def test_sequential_search_threshold_ignores_tried_receptacles() -> None:
    # Confidence about a receptacle already sensed empty this question is
    # contradicted by same-instant evidence; the search must go on.
    policy = _search(threshold=0.7)
    q = _question(t=11 * H)
    low = Prediction(distribution={"a": 0.6, "b": 0.4}, argmax="a")
    assert policy.decide(q, low, 5, 11 * H) == Sense("a")
    empty = SenseResult(receptacle_id="a", t=11 * H, contents=())
    stuck = Prediction(distribution={"a": 0.75, "b": 0.25}, argmax="a")
    assert policy.decide(q, stuck, 4, 11 * H, empty) == Sense("b")


def test_sequential_search_exhausts_receptacles_then_answers() -> None:
    policy = _search()
    q = _question()
    empty_a = SenseResult(receptacle_id="a", t=10 * H, contents=())
    empty_b = SenseResult(receptacle_id="b", t=10 * H, contents=())
    assert policy.decide(q, PRED, 9, 10 * H) == Sense("a")
    assert policy.decide(q, PRED, 8, 10 * H, empty_a) == Sense("b")
    # Both receptacles tried, object never seen: must terminate.
    assert isinstance(policy.decide(q, PRED, 7, 10 * H, empty_b), AnswerNow)


def test_sequential_search_respects_budget_and_new_question() -> None:
    policy = _search()
    assert isinstance(policy.decide(_question("q0"), PRED, 0, 10 * H),
                      AnswerNow)
    # A new question restarts the search set.
    assert policy.decide(_question("q1"), PRED, 1, 10 * H) == Sense("a")


def test_sequential_search_tie_break_is_seeded() -> None:
    tie = Prediction(distribution={"a": 0.5, "b": 0.5}, argmax="a")
    picks = []
    for _ in range(2):
        policy = SequentialSearch(random.Random(7))
        policy.reset(_context())
        action = policy.decide(_question(), tie, 5, 10 * H)
        assert isinstance(action, Sense)
        picks.append(action.receptacle_id)
    # Same seed, same choice — determinism, not receptacle-order bias.
    assert picks[0] == picks[1]
    assert picks[0] in ("a", "b")


def test_sequential_search_threshold_validation() -> None:
    with pytest.raises(ValueError, match="confidence_threshold"):
        SequentialSearch(random.Random(0), confidence_threshold=0.0)
    with pytest.raises(ValueError, match="confidence_threshold"):
        SequentialSearch(random.Random(0), confidence_threshold=1.5)
