"""Policy: sense until the conformal prediction set is a single receptacle.

Per question the loop is:

1. Read the belief's distribution for the queried object and its belief
   age (hours since the newest positive sighting the answer rests on).
2. Look up the calibrated quantile ``qhat`` for that age from a
   :class:`~baselines.conformal.calibration.QhatTable` — one global value,
   or the value of the question's age bin in age-binned mode.
3. Form the prediction set ``{r : 1 - p(r) <= qhat}``. A singleton means
   the calibrated belief is confident enough at the target coverage:
   answer. Anything else (several plausible receptacles, or an empty set
   when the belief is unusually spread out) means sense.
4. Sense the highest-probability sensable receptacle not yet tried this
   question (seeded tie-break). A miss becomes an exclusion inside the
   belief and shrinks the set; a hit is a sighting at query time and the
   next call answers.
5. With no budget left, or every sensable receptacle tried, answer from
   the current exclusion-updated belief.

Termination: receptacles are never re-sensed within a question, so a
question costs at most one sense per sensable receptacle — a belief that
never concentrates (a uniform one) sweeps the house once and then answers.
Unsensable receptacles (OUT_OF_HOUSE) are reached by elimination exactly
as in :mod:`baselines.policies.sequential_search`.

All times are seconds since episode start.
"""

from __future__ import annotations

import random
from typing import List, Optional, Set, Tuple

from baselines.beliefs.base import BeliefModel
from baselines.conformal.calibration import (AgeFn, QhatTable,
                                             prediction_set)
from baselines.policies.base import DecisionPolicy
from baselines.types import (Action, AnswerNow, EpisodeContext, Prediction,
                             Question, Sense, SenseResult)

SECONDS_PER_HOUR = 3600.0


def belief_age_fn(belief: BeliefModel) -> AgeFn:
    """``(object_id, t) -> hours`` since the belief's newest positive
    sighting of the object at or before ``t``; None if it has never been
    sighted. Reads the base class's public accessor, so it works for
    every belief model without touching their bookkeeping."""
    def age_h(object_id: str, t: int) -> Optional[float]:
        last = belief.last_positive_sighting_time(object_id, t)
        return None if last is None else (t - last) / SECONDS_PER_HOUR
    return age_h


class ConformalSense(DecisionPolicy):
    """Answer when the conformal prediction set is a singleton, else sense."""

    def __init__(self, rng: random.Random, table: QhatTable, age_fn: AgeFn,
                 binned: bool) -> None:
        self._rng = rng
        self._table = table
        self._age_fn = age_fn
        self._binned = binned
        self._receptacles: Tuple[str, ...] = ()
        self._all_receptacles: Tuple[str, ...] = ()
        self._question_id: Optional[str] = None
        self._tried: Set[str] = set()

    @property
    def name(self) -> str:
        mode = "age_binned" if self._binned else "global"
        return f"ConformalSense(alpha={self._table.alpha:g},{mode})"

    @property
    def table(self) -> QhatTable:
        return self._table

    @property
    def binned(self) -> bool:
        return self._binned

    def reset(self, context: EpisodeContext) -> None:
        self._receptacles = context.sensable_receptacle_ids
        self._all_receptacles = context.receptacle_ids
        self._question_id = None
        self._tried = set()

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: int, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        if self._question_id != question.question_id:
            self._question_id = question.question_id
            self._tried = set()
        if last_sense is not None and question.object_id in last_sense.contents:
            return AnswerNow()          # found at query time: certain
        qhat = self._table.qhat_for(self._age_fn(question.object_id, t),
                                    self._binned)
        if len(prediction_set(prediction.distribution, qhat,
                              self._all_receptacles)) == 1:
            return AnswerNow()          # calibrated-confident
        if budget_remaining <= 0:
            return AnswerNow()          # forced: exclusion-updated belief
        untried = [r for r in self._receptacles if r not in self._tried]
        if not untried:
            return AnswerNow()          # searched everywhere
        choice = self._best_untried(prediction, untried)
        self._tried.add(choice)
        return Sense(receptacle_id=choice)

    def _best_untried(self, prediction: Prediction,
                      untried: List[str]) -> str:
        top = max(prediction.distribution.get(r, 0.0) for r in untried)
        tied = [r for r in untried
                if prediction.distribution.get(r, 0.0) == top]
        return tied[0] if len(tied) == 1 else self._rng.choice(tied)
