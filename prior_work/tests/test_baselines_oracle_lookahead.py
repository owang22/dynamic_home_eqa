"""Oracle lookahead policy: future-question senses and the horizon.
Times are seconds since episode start."""

from __future__ import annotations

import random

from baselines.policies.oracle_lookahead import OracleLookaheadSense
from baselines.types import (AnswerNow, DAY_SECONDS, EpisodeContext,
                             Prediction, Question, Sense)

H = 3600
RECS = ("shelf_a", "shelf_b", "shelf_c")


def _context() -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=RECS,
        budget_per_day=10, n_days=2)


def _predict_fn(obj: str, t: int) -> Prediction:
    # Future object "keys" is split between b and c; everything else is
    # confidently on a.
    if obj == "keys":
        return Prediction(distribution={"shelf_b": 0.5, "shelf_c": 0.5},
                          argmax="shelf_b")
    return Prediction(distribution={"shelf_a": 1.0}, argmax="shelf_a")


def _current(t: int) -> Question:
    return Question(question_id="q_now", object_id="mug", t_query=t,
                    day_index=t // DAY_SECONDS, object_class="mug")


def _one_hot() -> Prediction:
    return Prediction(distribution={"shelf_a": 1.0}, argmax="shelf_a")


def test_senses_for_a_future_question_the_current_one_never_needs() -> None:
    t = 9 * H
    future = Question(question_id="q_later", object_id="keys",
                      t_query=t + 2 * H, day_index=0, object_class="keys")
    policy = OracleLookaheadSense(random.Random(0), lam=0.05,
                                  schedule=[_current(t), future],
                                  predict_fn=_predict_fn, horizon_days=1.0)
    policy.reset(_context())
    # Current belief is one-hot: voi_now = 0 everywhere, so a myopic
    # policy answers. The oracle senses for the upcoming keys question.
    action = policy.decide(_current(t), _one_hot(), 10.0, t)
    assert isinstance(action, Sense)
    assert action.receptacle_id in ("shelf_b", "shelf_c")
    assert policy.last_question_stats == {"senses_for_current": 0,
                                          "senses_future_only": 1}


def test_future_question_beyond_horizon_is_ignored() -> None:
    t = 9 * H
    far = Question(question_id="q_far", object_id="keys",
                   t_query=t + 3 * DAY_SECONDS, day_index=3,
                   object_class="keys")
    policy = OracleLookaheadSense(random.Random(0), lam=0.05,
                                  schedule=[_current(t), far],
                                  predict_fn=_predict_fn, horizon_days=1.0)
    policy.reset(_context())
    action = policy.decide(_current(t), _one_hot(), 10.0, t)
    assert isinstance(action, AnswerNow)
