"""Value-of-information policies: the one-step voi formula on hand-computed
distributions, the threshold rule, and the budget-price controller's
update direction and clipping. Times are seconds since episode start."""

from __future__ import annotations

import random

import pytest

from baselines.policies.voi_sense import (LAMBDA_MAX, LAMBDA_MIN,
                                          VoIBudgetPriceSense,
                                          VoIThresholdSense,
                                          value_of_information)
from baselines.types import (AnswerNow, EpisodeContext, Prediction, Question,
                             Sense, SenseResult)

H = 3600
OUT = "OUT_OF_HOUSE"
RECS = ("a", "b", "c", OUT)
SENSABLE = ("a", "b", "c")


def _context(budget: int = 10) -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=RECS,
        object_classes={"o": "mug"}, budget_per_day=budget, n_days=1,
        unsensable_receptacle_ids=(OUT,))


def _q(qid: str = "q0") -> Question:
    return Question(question_id=qid, object_id="o", t_query=10 * H, day_index=0)


def test_voi_hand_computed() -> None:
    # p = (a 0.5, b 0.3, c 0.15, OUT 0.05); answer now = 0.5.
    # Sense a: found w.p. 0.5; else p' = (b 0.6, c 0.3, OUT 0.1), max 0.6.
    #   voi = 0.5 + 0.5 * 0.6 - 0.5 = 0.30.
    # Sense b: found w.p. 0.3; else p' = (a 0.5/0.7, ...), max 0.714.
    #   voi = 0.3 + 0.7 * (0.5 / 0.7) - 0.5 = 0.30.
    # Sense c: 0.15 + 0.85 * (0.5 / 0.85) - 0.5 = 0.15.
    p = {"a": 0.5, "b": 0.3, "c": 0.15, OUT: 0.05}
    voi = value_of_information(p, SENSABLE)
    assert voi["a"] == pytest.approx(0.30)
    assert voi["b"] == pytest.approx(0.30)
    assert voi["c"] == pytest.approx(0.15)
    # In general: voi(argmax) = second-largest mass, voi(other) = p(other).
    p2 = {"a": 0.7, "b": 0.2, "c": 0.1, OUT: 0.0}
    voi2 = value_of_information(p2, SENSABLE)
    assert voi2["a"] == pytest.approx(0.2)
    assert voi2["b"] == pytest.approx(0.2)
    assert voi2["c"] == pytest.approx(0.1)
    # Already tried receptacles are simply not candidates.
    assert set(value_of_information(p2, ("b", "c"))) == {"b", "c"}


def test_voi_out_of_house_holds_max_and_no_sense_pays() -> None:
    # Every sensable receptacle has been seen empty at the query instant:
    # their mass is exactly 0, OUT holds everything. Sensing anything is
    # found with probability 0 and leaves p unchanged: voi 0 everywhere.
    p = {"a": 0.0, "b": 0.0, "c": 0.0, OUT: 1.0}
    voi = value_of_information(p, SENSABLE)
    assert voi == {"a": 0.0, "b": 0.0, "c": 0.0}
    assert max(voi.values()) == 0.0
    policy = VoIThresholdSense(random.Random(0), lam=0.01)
    policy.reset(_context())
    pred = Prediction(distribution=p, argmax=OUT)
    assert isinstance(policy.decide(_q(), pred, 5, 10 * H), AnswerNow)
    # OUT holds the max but a sensable receptacle keeps some mass: sensing
    # it pays exactly its mass (find it), and the price decides.
    p3 = {"a": 0.3, "b": 0.0, "c": 0.0, OUT: 0.7}
    voi3 = value_of_information(p3, SENSABLE)
    assert voi3["a"] == pytest.approx(0.3) and voi3["b"] == 0.0
    cheap = VoIThresholdSense(random.Random(0), lam=0.2)
    cheap.reset(_context())
    assert cheap.decide(_q(), Prediction(distribution=p3, argmax=OUT), 5, 10 * H) == Sense("a")
    dear = VoIThresholdSense(random.Random(0), lam=0.31)
    dear.reset(_context())
    assert isinstance(dear.decide(_q(), Prediction(distribution=p3, argmax=OUT), 5, 10 * H), AnswerNow)


def test_voi_certain_belief_never_senses() -> None:
    p = {"a": 1.0, "b": 0.0, "c": 0.0, OUT: 0.0}
    assert value_of_information(p, SENSABLE) == {"a": 0.0, "b": 0.0, "c": 0.0}


def test_threshold_policy_contract() -> None:
    policy = VoIThresholdSense(random.Random(0), lam=0.1)
    policy.reset(_context())
    q = _q()
    p = Prediction(distribution={"a": 0.5, "b": 0.3, "c": 0.15, OUT: 0.05},
                   argmax="a")
    # voi(a) = voi(b) = 0.30: tie prefers the larger p(r) -> a.
    assert policy.decide(q, p, 5, q.t_query) == Sense("a")
    # A miss zeroes a; b (0.6) vs c (0.3): voi(b) = 0.3, voi(c) = 0.3, tie
    # prefers b. Never re-senses a.
    after = Prediction(distribution={"a": 0.0, "b": 0.6, "c": 0.3, OUT: 0.1},
                       argmax="b")
    miss = SenseResult(receptacle_id="a", t=q.t_query, contents=())
    assert policy.decide(q, after, 4, q.t_query, miss) == Sense("b")
    # Found: answer at once.
    hit = SenseResult(receptacle_id="b", t=q.t_query, contents=("o",))
    assert isinstance(policy.decide(q, Prediction(distribution={"b": 1.0}, argmax="b"),
                                    3, q.t_query, hit), AnswerNow)
    # Zero budget: answer even when voi is high.
    fresh = VoIThresholdSense(random.Random(0), lam=0.1)
    fresh.reset(_context())
    assert isinstance(fresh.decide(q, p, 0, q.t_query), AnswerNow)
    # Everything tried: answer.
    sweep = VoIThresholdSense(random.Random(0), lam=0.0)
    sweep.reset(_context())
    flat = Prediction(distribution={"a": 0.3, "b": 0.3, "c": 0.3, OUT: 0.1},
                      argmax="a")
    seen = {sweep.decide(q, flat, 9, q.t_query) for _ in range(3)}
    assert seen == {Sense("a"), Sense("b"), Sense("c")}
    assert isinstance(sweep.decide(q, flat, 6, q.t_query), AnswerNow)
    assert policy.name == "VoIThresholdSense(lambda=0.1)"
    with pytest.raises(ValueError):
        VoIThresholdSense(random.Random(0), lam=-0.1)


def test_price_controller_direction_and_clipping() -> None:
    # budget 2 per day over 4 questions: allowance 0.5 senses per question.
    policy = VoIBudgetPriceSense(random.Random(0), gamma=0.1, budget_per_day=2,
                                 questions_per_day=4, lam0=0.05)
    policy.reset(_context(budget=2))
    assert policy.budget_rate == 0.5 and policy.lam == 0.05
    p = Prediction(distribution={"a": 0.5, "b": 0.3, "c": 0.15, OUT: 0.05},
                   argmax="a")
    # q0: two senses (spend 2 > allowance 0.5) -> the price RISES.
    q0 = _q("q0")
    assert policy.decide(q0, p, 2, q0.t_query) == Sense("a")
    after = Prediction(distribution={"a": 0.0, "b": 0.6, "c": 0.3, OUT: 0.1},
                       argmax="b")
    assert policy.decide(q0, after, 1, q0.t_query,
                         SenseResult("a", q0.t_query, ())) == Sense("b")
    q1 = _q("q1")
    policy.decide(q1, p, 0, q1.t_query)         # books q0: spend_rate 2.0
    assert policy.spend_rate == pytest.approx(2.0)
    assert policy.lam == pytest.approx(0.05 + 0.1 * (2.0 - 0.5))
    # q1 spent nothing (no budget); q2 arrives: spend_rate 1.0, still above
    # the allowance -> rises again.
    q2 = _q("q2")
    policy.decide(q2, p, 0, q2.t_query)
    assert policy.lam == pytest.approx(0.2 + 0.1 * (1.0 - 0.5))
    # Many zero-spend questions: spend_rate falls below the allowance and
    # the price FALLS, never below LAMBDA_MIN.
    for i in range(3, 400):
        policy.decide(_q(f"q{i}"), p, 0, 10 * H)
    assert policy.spend_rate < 0.5
    assert policy.lam == pytest.approx(LAMBDA_MIN)
    # Upper clip.
    hot = VoIBudgetPriceSense(random.Random(0), gamma=10.0, budget_per_day=0,
                              questions_per_day=1, lam0=0.05)
    hot.reset(_context(budget=5))
    hot.decide(_q("a0"), p, 5, 10 * H)          # one sense
    hot.decide(_q("a1"), p, 4, 10 * H)          # books a0: spend 1 > 0
    assert hot.lam == pytest.approx(LAMBDA_MAX)
    assert hot.name == "VoIBudgetPriceSense(gamma=10,lambda0=0.05)"
    # Reset restores the initial price and the counters.
    hot.reset(_context(budget=5))
    assert hot.lam == 0.05 and hot.spend_rate == 0.0 and hot.lam_history == []
    with pytest.raises(ValueError):
        VoIBudgetPriceSense(random.Random(0), gamma=-1, budget_per_day=1,
                            questions_per_day=1)
    with pytest.raises(ValueError):
        VoIBudgetPriceSense(random.Random(0), gamma=0.1, budget_per_day=1,
                            questions_per_day=0)


def test_price_gates_sensing() -> None:
    # Same distribution, price above every voi: answers; at or below: senses.
    p = Prediction(distribution={"a": 0.5, "b": 0.3, "c": 0.15, OUT: 0.05},
                   argmax="a")
    policy = VoIBudgetPriceSense(random.Random(0), gamma=0.0, budget_per_day=1,
                                 questions_per_day=1, lam0=0.31)
    policy.reset(_context())
    assert isinstance(policy.decide(_q(), p, 5, 10 * H), AnswerNow)
    policy = VoIBudgetPriceSense(random.Random(0), gamma=0.0, budget_per_day=1,
                                 questions_per_day=1, lam0=0.30)
    policy.reset(_context())
    assert policy.decide(_q(), p, 5, 10 * H) == Sense("a")
