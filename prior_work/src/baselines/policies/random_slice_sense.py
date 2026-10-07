"""Random-slice exploration on top of any sense-or-answer policy.

Sightings only arrive where the policy looks, and the policy looks where
queries point; hypotheses about everything else never get corrected and
calibration numbers only cover cases the belief already liked. This
wrapper spends a small fixed share of the daily budget on receptacles
chosen uniformly at random, ignoring the belief, so evidence and
calibration data reach the objects nobody asks about.

Mechanics, chosen so the inner policy's own behaviour is untouched:

* At the start of each day ``fraction * budget_per_day`` is RESERVED.
  The inner policy is shown ``budget_remaining`` minus what is still
  reserved, so it never spends the slice and never sees it.
* The slice is spent spread through the day: after each question the
  inner policy answers without sensing, one random sense fires (if the
  reserve still covers it), then the answer is given. Random sightings
  therefore land across the day rather than piling up at one hour.
* Candidates are the sensable receptacles not yet sensed today (by
  either policy) whose current price fits the reserve — "reachable" is
  priced through ``context.sense_cost``, so a room-change surcharge
  narrows the pool exactly as it narrows the inner policy's.
* ``fraction = 0`` is the comparison arm and reduces to the inner
  policy exactly (asserted in tests).

The wrapper's generator is its only randomness; the inner policy keeps
its own, so the two arms differ only in the slice.
"""

from __future__ import annotations

import random
from typing import Optional, Set

from baselines.policies.base import DecisionPolicy
from baselines.types import (Action, AnswerNow, EpisodeContext, Prediction,
                             Question, Sense, SenseResult)


class RandomSliceSense(DecisionPolicy):
    """``inner`` decides as usual on the unreserved budget; the slice
    adds one random sense per answered-without-sensing question."""

    def __init__(self, rng: random.Random, inner: DecisionPolicy,
                 fraction: float) -> None:
        if not 0.0 <= fraction < 1.0:
            raise ValueError(
                f"RandomSliceSense: fraction {fraction} outside [0, 1)")
        self._rng = rng
        self._inner = inner
        self._fraction = float(fraction)
        self._context: Optional[EpisodeContext] = None
        self._day = -1
        self._reserve = 0.0
        self._sensed_today: Set[str] = set()
        self._question_id: Optional[str] = None
        self._random_fired = False
        self._answer_pending = False
        self.random_senses = 0
        """Random senses issued this episode (the slice's spend)."""

    @property
    def name(self) -> str:
        return f"RandomSlice(f={self._fraction:g},{self._inner.name})"

    @property
    def fraction(self) -> float:
        return self._fraction

    def reset(self, context: EpisodeContext) -> None:
        self._context = context
        self._inner.reset(context)
        self._day = -1
        self._reserve = 0.0
        self._sensed_today = set()
        self._question_id = None
        self._random_fired = False
        self._answer_pending = False
        self.random_senses = 0

    def _new_day(self, day_index: int) -> None:
        assert self._context is not None
        self._day = day_index
        self._reserve = self._fraction * self._context.budget_per_day
        self._sensed_today = set()

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        assert self._context is not None
        if question.day_index != self._day:
            self._new_day(question.day_index)
        if question.question_id != self._question_id:
            self._question_id = question.question_id
            self._random_fired = False
            self._answer_pending = False
        if self._answer_pending:
            # The random sense just returned; the answer follows it.
            self._answer_pending = False
            return AnswerNow()
        visible = max(0.0, budget_remaining - self._reserve)
        action = self._inner.decide(question, prediction, visible, t,
                                    last_sense)
        if isinstance(action, Sense):
            self._sensed_today.add(action.receptacle_id)
            return action
        if self._fraction <= 0.0 or self._random_fired:
            return AnswerNow()
        affordable = min(self._reserve, budget_remaining)
        candidates = [r for r in self._context.sensable_receptacle_ids
                      if r not in self._sensed_today
                      and self._context.sense_cost(r) <= affordable]
        if not candidates:
            return AnswerNow()
        choice = self._rng.choice(candidates)
        self._reserve -= self._context.sense_cost(choice)
        self._sensed_today.add(choice)
        self._random_fired = True
        self._answer_pending = True
        self.random_senses += 1
        return Sense(receptacle_id=choice)
