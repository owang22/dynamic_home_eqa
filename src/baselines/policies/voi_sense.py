"""Policies: sense while the one-step value of information pays.

At a decision point the policy holds the belief's distribution ``p`` over
every location and the receptacles it has already sensed this question.
Answering now is worth ``max(p)`` (the probability the argmax is right).
Sensing a sensable, untried receptacle ``r`` is worth: with probability
``p(r)`` the object is found (value 1); otherwise the fresh empty look
zeroes ``r`` (an empty look at the query instant suppresses fully in the
base pipeline), ``p`` renormalizes to ``p'`` and the continuation is
worth ``max(p')``. So

    voi(r) = p(r) + (1 - p(r)) * max(p') - max(p),
    p'(s)  = p(s) / (1 - p(r))  for s != r.

This is exact one-step lookahead under the pipeline's own semantics,
computed arithmetically from ``p`` alone (no belief cloning; the belief
is never mutated by a policy). It is the greedy form of the classical
optimal search-and-stop policy (Ross 1969; Weitzman 1979 for the
stop-vs-explore index), valid here because every sense within a
question is at the query instant, so the target is static during the
search. Cross-question information value (a sense now also sharpens
later questions) is not modelled.

Sensing is not free and need not be uniformly priced: with a room-change
cost ``c`` in force, sensing a receptacle in the room the robot already
occupies costs 1 and one anywhere else costs ``1 + c``
(``context.sense_cost``). ``lambda`` is then a price per unit of cost,
not per sense, so both policies below

* sense while ``voi(r) >= lambda * cost(r)`` rather than
  ``voi(r) >= lambda``, and
* pick the receptacle maximizing ``voi(r) / cost(r)`` rather than
  ``voi(r)``.

At ``c = 0`` every cost is 1 and both reduce to the plain rules exactly.
This is the only cost-awareness in the roster: the other policies cannot
see the price at all.

:class:`VoIThresholdSense` senses the best value-per-cost receptacle
while ``max voi/cost >= lambda`` and budget remains, else answers. Under
a binding per-day cap it runs out and answers from memory; with the cap
disabled its senses per question trace the price-based cost-accuracy
frontier.

:class:`VoIBudgetPriceSense` is the same rule with ``lambda`` adapted to
track the budget: after each question

    lambda += gamma * (spend_rate - budget_rate),   clipped to [0.001, 0.5]

with ``spend_rate`` the senses used per question seen so far in the
episode and ``budget_rate = budget_per_day / questions_per_day`` (the
per-question allowance). Spending above the allowance raises the price,
which cuts sensing; spending below lowers it. ``questions_per_day`` is
not in the agent's context, so the driver passes it (the bank's
questions per query day).

Harness contract: budget is checked before every sense, each receptacle
is sensed at most once per question, and every question ends in
AnswerNow. Ties among equal value-per-cost receptacles prefer the larger
``p(r)``, then the seeded generator. All times are seconds since episode
start.
"""

from __future__ import annotations

import random
from typing import Dict, List, Mapping, Optional, Sequence, Set, Tuple

from baselines.policies.base import DecisionPolicy
from baselines.types import (Action, AnswerNow, EpisodeContext, Prediction,
                             Question, Sense, SenseResult)

LAMBDA_MIN = 0.001
LAMBDA_MAX = 0.5
"""Clip range of the adaptive price."""


def value_of_information(p: Mapping[str, float],
                         candidates: Sequence[str]) -> Dict[str, float]:
    """``voi(r)`` for every candidate receptacle (sensable, untried) under
    the one-step lookahead of the module docstring.

    A candidate with ``p(r) = 1`` is found for sure: voi = 1 - max(p) = 0.
    A candidate with ``p(r) = 0`` cannot be found and its empty look
    changes nothing: voi = 0.
    """
    if not p:
        return {}
    best = max(p.values())
    out: Dict[str, float] = {}
    for r in candidates:
        pr = p.get(r, 0.0)
        rest = 1.0 - pr
        if rest <= 0.0:
            out[r] = 1.0 - best
            continue
        continuation = max((v for s, v in p.items() if s != r), default=0.0) / rest
        out[r] = pr + rest * continuation - best
    return out


class VoIThresholdSense(DecisionPolicy):
    """Sense the best value-per-cost receptacle while
    ``max voi/cost >= lambda``."""

    def __init__(self, rng: random.Random, lam: float) -> None:
        if lam < 0.0:
            raise ValueError(f"VoIThresholdSense: lambda {lam} must be >= 0")
        self._rng = rng
        self._lam = float(lam)
        self._receptacles: Tuple[str, ...] = ()
        self._context: Optional[EpisodeContext] = None
        self._question_id: Optional[str] = None
        self._tried: Set[str] = set()
        self.last_max_voi = 0.0

    @property
    def name(self) -> str:
        return f"VoIThresholdSense(lambda={self._lam:g})"

    @property
    def lam(self) -> float:
        return self._lam

    def reset(self, context: EpisodeContext) -> None:
        # Held for its live ``sense_cost``: the harness keeps the robot's
        # room inside this context, so the price is read fresh at every
        # decision rather than cached here.
        self._context = context
        self._receptacles = context.sensable_receptacle_ids
        self._question_id = None
        self._tried = set()

    def _cost(self, receptacle_id: str) -> float:
        """Budget price of sensing ``receptacle_id`` right now (1.0 with
        no context, i.e. the flat model)."""
        if self._context is None:
            return 1.0
        return self._context.sense_cost(receptacle_id)

    def _new_question(self, question: Question) -> None:
        """Hook for per-question bookkeeping (the price controller)."""
        self._tried = set()

    def _price(self) -> float:
        return self._lam

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        if self._question_id != question.question_id:
            self._question_id = question.question_id
            self._new_question(question)
        if last_sense is not None and question.object_id in last_sense.contents:
            return AnswerNow()          # found at query time: certain
        if budget_remaining <= 0:
            return AnswerNow()
        untried = [r for r in self._receptacles if r not in self._tried]
        if not untried:
            return AnswerNow()
        voi = value_of_information(prediction.distribution, untried)
        # Value per unit of budget: with a room-change cost the same voi
        # is worth less when it needs a trip. At c = 0 every cost is 1
        # and this is voi(r) and the plain threshold, exactly.
        rate = {r: voi[r] / self._cost(r) for r in untried}
        best = max(rate.values())
        self.last_max_voi = max(voi.values())
        if best < self._price():
            return AnswerNow()
        top = [r for r in untried if rate[r] == best]
        if len(top) > 1:
            pmax = max(prediction.distribution.get(r, 0.0) for r in top)
            top = [r for r in top if prediction.distribution.get(r, 0.0) == pmax]
        choice = top[0] if len(top) == 1 else self._rng.choice(top)
        self._tried.add(choice)
        self._on_sense()
        return Sense(receptacle_id=choice)

    def _on_sense(self) -> None:
        """Hook: a sense was issued for the current question."""


class VoIBudgetPriceSense(VoIThresholdSense):
    """VoIThresholdSense whose price tracks the budget."""

    def __init__(self, rng: random.Random, gamma: float, budget_per_day: int,
                 questions_per_day: int, lam0: float = 0.05) -> None:
        if gamma < 0.0:
            raise ValueError(f"VoIBudgetPriceSense: gamma {gamma} must be >= 0")
        if questions_per_day <= 0 or budget_per_day < 0:
            raise ValueError("VoIBudgetPriceSense: questions_per_day must be "
                             "positive and budget_per_day non-negative")
        super().__init__(rng, lam=lam0)
        self._gamma = float(gamma)
        self._lam0 = float(lam0)
        self._budget_rate = budget_per_day / questions_per_day
        self._questions_seen = 0
        self._senses_used = 0
        self._senses_this_question = 0
        self._open_question = False
        self.lam_history: List[float] = []

    @property
    def name(self) -> str:
        return (f"VoIBudgetPriceSense(gamma={self._gamma:g},"
                f"lambda0={self._lam0:g})")

    @property
    def gamma(self) -> float:
        return self._gamma

    @property
    def budget_rate(self) -> float:
        return self._budget_rate

    @property
    def spend_rate(self) -> float:
        return (self._senses_used / self._questions_seen
                if self._questions_seen else 0.0)

    def reset(self, context: EpisodeContext) -> None:
        super().reset(context)
        self._lam = self._lam0
        self._questions_seen = 0
        self._senses_used = 0
        self._senses_this_question = 0
        self._open_question = False
        self.lam_history = []

    def _new_question(self, question: Question) -> None:
        if self._open_question:
            self.close_question()
        super()._new_question(question)
        self._senses_this_question = 0
        self._open_question = True

    def _on_sense(self) -> None:
        self._senses_this_question += 1

    def close_question(self) -> None:
        """Book the finished question and update the price: called when
        the next question arrives (the last question of an episode is
        never booked, which changes nothing downstream)."""
        self._questions_seen += 1
        self._senses_used += self._senses_this_question
        self._open_question = False
        self.update_price()

    def update_price(self) -> None:
        self._lam = min(LAMBDA_MAX, max(
            LAMBDA_MIN,
            self._lam + self._gamma * (self.spend_rate - self._budget_rate)))
        self.lam_history.append(self._lam)
