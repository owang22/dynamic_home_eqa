"""ResolvableMassSense's value-of-sensing gate and ACISense's recursion,
feedback gating and set bookkeeping. Times are seconds since episode
start."""

from __future__ import annotations

import random

import pytest

from baselines.conformal.calibration import QhatTable
from baselines.policies.aci_sense import ACISense, truth_revealed
from baselines.policies.resolvable_mass_sense import ResolvableMassSense
from baselines.types import (AnswerNow, EpisodeContext, Prediction, Question,
                             Sense)

H = 3600
OUT = "OUT_OF_HOUSE"
RECS = ("a", "b", "c", OUT)


def _context() -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh", receptacle_ids=RECS,
        object_classes={"o": "mug"}, budget_per_day=10, n_days=1,
        unsensable_receptacle_ids=(OUT,))


def _table(alpha: float = 0.3, qhat: float = 0.9) -> QhatTable:
    return QhatTable(alpha=alpha, age_edges_h=(6.0,), global_qhat=qhat,
                     n_global=100, bin_qhats=(qhat, qhat), bin_counts=(50, 50),
                     bin_fallback=(False, False))


def _age(object_id: str, t: int) -> float:
    return 1.0


Q = Question(question_id="q0", object_id="o", t_query=10 * H, day_index=0)


def test_resolvable_mass_gate() -> None:
    # Set at qhat 0.9 = {r: p >= 0.1}. Spread over sensable a, b: mass 0.8
    # resolvable -> sense a at tau 0.6; the same set with the mass on OUT
    # (a 0.15, OUT 0.85) has resolvable mass 0.15 -> answer.
    spread = Prediction(distribution={"a": 0.5, "b": 0.3, "c": 0.1, OUT: 0.1},
                        argmax="a")
    left = Prediction(distribution={"a": 0.15, "b": 0.0, "c": 0.0, OUT: 0.85},
                      argmax=OUT)
    policy = ResolvableMassSense(random.Random(0), _table(), _age, False, 0.6)
    policy.reset(_context())
    assert policy.decide(Q, spread, 5, Q.t_query) == Sense("a")
    assert isinstance(policy.decide(Q, left, 5, Q.t_query), AnswerNow)
    # Singleton set: answer regardless of tau.
    sure = Prediction(distribution={"a": 0.95, "b": 0.05, "c": 0.0, OUT: 0.0},
                      argmax="a")
    assert isinstance(policy.decide(Q, sure, 5, Q.t_query), AnswerNow)
    # Tried members no longer count as resolvable: after sensing a, the
    # set {a, b, c} at tau 0.6 has only b + c = 0.4 left -> answer.
    policy2 = ResolvableMassSense(random.Random(0), _table(), _age, False, 0.6)
    policy2.reset(_context())
    assert policy2.decide(Q, spread, 5, Q.t_query) == Sense("a")
    assert isinstance(policy2.decide(Q, spread, 4, Q.t_query), AnswerNow)
    assert policy2.name == "ResolvableMassSense(alpha=0.3,tau=0.6,global)"
    with pytest.raises(ValueError):
        ResolvableMassSense(random.Random(0), _table(), _age, False, 0.0)


def test_aci_recursion_and_first_set() -> None:
    scores = [i / 20 for i in range(20)]        # 0.0 .. 0.95
    policy = ACISense(random.Random(0), scores, alpha_target=0.2, gamma=0.1,
                      age_fn=_age, feedback_mode="oracle")
    policy.reset(_context())
    static_qhat = policy.qhat()
    pred = Prediction(distribution={"a": 0.6, "b": 0.3, "c": 0.1, OUT: 0.0},
                      argmax="a")
    action = policy.decide(Q, pred, 5, Q.t_query)
    assert policy.first_qhat == static_qhat and policy.first_alpha == 0.2
    assert policy.first_set == {r for r in RECS
                                if 1 - pred.distribution[r] <= static_qhat}
    assert isinstance(action, Sense)
    # An error raises alpha... no: an error LOWERS alpha (more conservative).
    policy.feedback(True)
    assert policy.alpha == pytest.approx(0.2 + 0.1 * (0.2 - 1))
    assert policy.qhat() >= static_qhat
    policy.feedback(False)
    assert policy.alpha == pytest.approx(0.2 + 0.1 * (0.2 - 1) + 0.1 * 0.2)
    assert policy.n_updates == 2
    # Above 1 the set is empty; the recursion itself is unclipped.
    policy.alpha = 1.2
    assert policy.qhat() == 0.0
    assert policy.name == "ACISense(alpha=0.2,gamma=0.1,oracle)"
    with pytest.raises(ValueError):
        ACISense(random.Random(0), scores, 0.2, 0.1, _age, "guess")


def test_truth_revealed_by_own_senses() -> None:
    sensable = ("a", "b", "c")
    found = [{"type": "sense", "receptacle_id": "a", "contents": ["x"]},
             {"type": "sense", "receptacle_id": "b", "contents": ["o"]},
             {"type": "answer"}]
    assert truth_revealed(found, "o", sensable)
    partial = [{"type": "sense", "receptacle_id": "a", "contents": []},
               {"type": "answer"}]
    assert not truth_revealed(partial, "o", sensable)
    swept = [{"type": "sense", "receptacle_id": r, "contents": []}
             for r in sensable] + [{"type": "answer"}]
    assert truth_revealed(swept, "o", sensable)
    assert not truth_revealed([{"type": "answer"}], "o", sensable)
