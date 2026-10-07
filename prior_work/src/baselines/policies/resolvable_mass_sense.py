"""Policy: conformal set plus a value-of-sensing gate.

A conformal set with several members says the belief is not confident
enough; it does not say a sense will fix that. The set may be spread
over receptacles the robot can look at (one sense resolves most of it)
or over the unsensable remainder (OUT_OF_HOUSE: looking anywhere
resolves nothing). This policy senses only when the belief mass sitting
on sensable, not-yet-tried members of the set — the *resolvable mass* —
is at least ``tau``:

1. Read the belief's distribution and its age; look up ``qhat`` for that
   age (global or age-binned table, as in
   :class:`~baselines.policies.conformal_sense.ConformalSense`) and form
   the prediction set over every location.
2. If the set has more than one member AND
   ``resolvable_mass = sum p(r) for sensable untried set members r``
   is at least ``tau`` and budget remains: sense the highest-probability
   such member (seeded tie-break). A hit answers next call; a miss is a
   fresh empty look and the set shrinks by itself.
3. Otherwise answer from the belief as it stands.

With OUT_OF_HOUSE mass honest (the base pipeline's floor is all that
survives a sweep), low resolvable mass largely MEANS "the belief thinks
it left": this is the value-aware trigger in its natural form. Bounded
like ConformalSense: at most one sense per sensable receptacle per
question. All times are seconds since episode start.
"""

from __future__ import annotations

import random
from typing import List, Optional, Set, Tuple

from baselines.conformal.calibration import (AgeFn, QhatTable,
                                             prediction_set)
from baselines.policies.base import DecisionPolicy
from baselines.types import (Action, AnswerNow, EpisodeContext, Prediction,
                             Question, Sense, SenseResult)


class ResolvableMassSense(DecisionPolicy):
    """Sense only when enough of the conformal set can be looked at."""

    def __init__(self, rng: random.Random, table: QhatTable, age_fn: AgeFn,
                 binned: bool, tau: float) -> None:
        if not 0.0 < tau <= 1.0:
            raise ValueError(f"ResolvableMassSense: tau {tau} outside (0, 1]")
        self._rng = rng
        self._table = table
        self._age_fn = age_fn
        self._binned = binned
        self._tau = float(tau)
        self._receptacles: Tuple[str, ...] = ()
        self._all_receptacles: Tuple[str, ...] = ()
        self._question_id: Optional[str] = None
        self._tried: Set[str] = set()

    @property
    def name(self) -> str:
        mode = "age_binned" if self._binned else "global"
        return (f"ResolvableMassSense(alpha={self._table.alpha:g},"
                f"tau={self._tau:g},{mode})")

    @property
    def tau(self) -> float:
        return self._tau

    def reset(self, context: EpisodeContext) -> None:
        self._receptacles = context.sensable_receptacle_ids
        self._all_receptacles = context.receptacle_ids
        self._question_id = None
        self._tried = set()

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        if self._question_id != question.question_id:
            self._question_id = question.question_id
            self._tried = set()
        if last_sense is not None and question.object_id in last_sense.contents:
            return AnswerNow()          # found at query time: certain
        if budget_remaining <= 0:
            return AnswerNow()
        qhat = self._table.qhat_for(self._age_fn(question.object_id, t),
                                    self._binned)
        members = prediction_set(prediction.distribution, qhat,
                                 self._all_receptacles)
        if len(members) <= 1:
            return AnswerNow()          # confident (or too flat to act on)
        resolvable = [r for r in self._receptacles
                      if r in members and r not in self._tried]
        mass = sum(prediction.distribution.get(r, 0.0) for r in resolvable)
        if not resolvable or mass < self._tau:
            return AnswerNow()          # a sense would not resolve enough
        choice = self._best(prediction, resolvable)
        self._tried.add(choice)
        return Sense(receptacle_id=choice)

    def _best(self, prediction: Prediction, candidates: List[str]) -> str:
        top = max(prediction.distribution.get(r, 0.0) for r in candidates)
        tied = [r for r in candidates
                if prediction.distribution.get(r, 0.0) == top]
        return tied[0] if len(tied) == 1 else self._rng.choice(tied)
