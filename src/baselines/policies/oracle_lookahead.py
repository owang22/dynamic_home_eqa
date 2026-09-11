"""Oracle lookahead sensing: the policy that has read the query schedule.

Headroom diagnostic, not a deployable method: this policy is handed the
episode's TRUE question schedule (objects and times — never answers) and
values a sense by the current question's one-step value of information
PLUS the discounted VoI it would buy for every scheduled question inside
the lookahead window:

    value(r) = voi_now(r)
             + sum over future questions (o', t') with t < t' <= t + H of
                   voi(p_o', r) * 2^(-(t' - t) / half_life)

where ``p_o'`` is the belief's CURRENT distribution for the future
question's object (read through ``predict_readonly`` so scoring the
future perturbs nothing) and the exponential discount stands in for the
belief's own evidence decay between now and the future query. It senses
the best value-per-cost receptacle while ``value / cost >= lambda``,
with cost read live through ``context.sense_cost`` (the room-change
model; the robot's position rides on the context, so ``decide`` keeps
its signature).

Greedy on both axes — receptacles are picked one step at a time and
today's budget is not reserved for later questions — so measured this
way the lookahead gain is a LOWER BOUND on the true optimum; a real
planner could only widen the gap.

Per-question bookkeeping (:attr:`last_question_stats`): every issued
sense is classified by whether the current question alone justified it
(``voi_now(r) / cost >= lambda``) or only the future term did — the
"senses the myopic policy would never buy".

All times are seconds since episode start.
"""

from __future__ import annotations

import random
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from baselines.policies.voi_sense import (VoIThresholdSense,
                                          value_of_information)
from baselines.types import (Action, AnswerNow, Prediction, Question,
                             Sense, SenseResult)

PredictFn = Callable[[str, int], Prediction]
"""(object_id, t) -> the belief's current distribution, without side
effects — wire it to ``belief.predict_readonly``."""

DEFAULT_HORIZON_DAYS = 2.0
DEFAULT_DECAY_HALF_LIFE_H = 24.0


class OracleLookaheadSense(VoIThresholdSense):
    """VoI sensing with the true upcoming query schedule added in
    (module docstring). ``schedule`` is every question of the episode in
    any order; ``predict_fn`` the belief's read-only prediction."""

    def __init__(self, rng: random.Random, lam: float,
                 schedule: Sequence[Question], predict_fn: PredictFn,
                 horizon_days: float = DEFAULT_HORIZON_DAYS,
                 decay_half_life_h: float = DEFAULT_DECAY_HALF_LIFE_H
                 ) -> None:
        super().__init__(rng, lam=lam)
        if horizon_days <= 0 or decay_half_life_h <= 0:
            raise ValueError(
                f"OracleLookaheadSense: horizon_days {horizon_days} and "
                f"decay_half_life_h {decay_half_life_h} must be positive")
        self._schedule = sorted(schedule, key=lambda q: q.t_query)
        self._predict_fn = predict_fn
        self._horizon_s = horizon_days * 86_400.0
        self._half_life_s = decay_half_life_h * 3600.0
        self._stats = {"senses_for_current": 0, "senses_future_only": 0}

    @property
    def name(self) -> str:
        return (f"OracleLookahead(lambda={self._lam:g},"
                f"H={self._horizon_s / 86_400.0:g}d)")

    @property
    def last_question_stats(self) -> Dict[str, int]:
        """Sense classification for the question decided most recently."""
        return dict(self._stats)

    def _new_question(self, question: Question) -> None:
        super()._new_question(question)
        self._stats = {"senses_for_current": 0, "senses_future_only": 0}

    def _future_weights(self, question: Question
                        ) -> List[Tuple[str, float]]:
        """(object_id, discount) per scheduled question inside the
        window, the current question excluded."""
        t = question.t_query
        out: List[Tuple[str, float]] = []
        for q in self._schedule:
            if q.t_query <= t:
                continue
            if q.t_query > t + self._horizon_s:
                break
            out.append((q.object_id,
                        2.0 ** (-(q.t_query - t) / self._half_life_s)))
        return out

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        if self._question_id != question.question_id:
            self._question_id = question.question_id
            self._new_question(question)
        if (last_sense is not None
                and question.object_id in last_sense.contents):
            return AnswerNow()          # found at query time: certain
        if budget_remaining <= 0:
            return AnswerNow()
        untried = [r for r in self._receptacles if r not in self._tried]
        if not untried:
            return AnswerNow()

        voi_now = value_of_information(prediction.distribution, untried)
        value = dict(voi_now)
        future_predictions: Dict[str, Prediction] = {}
        for obj, discount in self._future_weights(question):
            if obj not in future_predictions:
                future_predictions[obj] = self._predict_fn(obj, t)
            future_voi = value_of_information(
                future_predictions[obj].distribution, untried)
            for r in untried:
                value[r] += discount * future_voi[r]

        costs = {r: self._cost(r) for r in untried}
        affordable = [r for r in untried if costs[r] <= budget_remaining]
        if not affordable:
            return AnswerNow()
        rate = {r: value[r] / costs[r] for r in affordable}
        best = max(rate.values())
        if best < self._lam:
            return AnswerNow()
        top = [r for r in affordable if rate[r] == best]
        if len(top) > 1:
            pmax = max(prediction.distribution.get(r, 0.0) for r in top)
            top = [r for r in top
                   if prediction.distribution.get(r, 0.0) == pmax]
        choice = top[0] if len(top) == 1 else self._rng.choice(top)
        self._tried.add(choice)
        if voi_now[choice] / costs[choice] >= self._lam:
            self._stats["senses_for_current"] += 1
        else:
            self._stats["senses_future_only"] += 1
        return Sense(receptacle_id=choice)
