"""Policy: search receptacles in belief order until the object is found.

Per question the loop is:

1. Read the belief's prediction for the queried object.
2. If the top receptacle's probability meets ``confidence_threshold``,
   answer. At the default threshold of 1.0 this early stop is deliberately
   restricted to certainty grounded at query time — a sense THIS question
   that returned the object (see the guard notes below). Sub-1.0
   thresholds instead trust the belief's stated confidence and answer
   without confirmation; that is only sound for calibrated beliefs (the
   basic one-hot recency belief claims probability 1.0 for arbitrarily old
   sightings), so the panel and all defaults use 1.0.
3. Otherwise, if budget remains, sense the highest-probability receptacle
   not yet tried this question. A miss becomes an exclusion inside the
   belief (base-class negative evidence), so the next prediction naturally
   ranks the next-best receptacle. A hit answers immediately.
4. With no budget left (or every receptacle tried), answer from the
   current exclusion-updated belief.

Guards that make the unlimited-budget invariant hold (any bank whose
queried objects are each inside some receptacle at query time scores task
accuracy 1.0, with every belief model):

* The early stop never fires on a receptacle already sensed empty this
  question — a belief can claim certainty about such a receptacle when
  stale exclusions force its all-excluded fallback, and same-timestamp
  evidence outranks any prediction.
* The early stop at threshold 1.0 requires the queried object to have
  been in this question's most recent sense result. Belief confidence of
  1.0 alone is not proof: one-hot beliefs emit it for stale sightings,
  and exclusion renormalization can concentrate mass on a receptacle
  nobody has looked at.
* Receptacles are never re-sensed within a question (tried set), so the
  search visits each at most once and must reach the object's receptacle.

Tie-breaking among equal-probability untried receptacles uses the seeded
generator supplied at construction — no unseeded randomness. All times
are seconds since episode start.
"""

from __future__ import annotations

import random
from typing import List, Optional, Set, Tuple

from baselines.policies.base import DecisionPolicy
from baselines.types import (Action, AnswerNow, EpisodeContext,
                             PROBABILITY_TOLERANCE, Prediction, Question,
                             Sense, SenseResult)


class SequentialSearch(DecisionPolicy):
    """Probability-ordered search with a confidence-threshold early stop."""

    def __init__(self, rng: random.Random,
                 confidence_threshold: float = 1.0) -> None:
        if not 0.0 < confidence_threshold <= 1.0:
            raise ValueError(
                f"SequentialSearch: confidence_threshold "
                f"{confidence_threshold} outside (0, 1]")
        self._rng = rng
        self._threshold = confidence_threshold
        self._receptacles: Tuple[str, ...] = ()
        self._question_id: Optional[str] = None
        self._tried: Set[str] = set()

    def reset(self, context: EpisodeContext) -> None:
        self._receptacles = context.receptacle_ids
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
        if self._answer_early(prediction):
            return AnswerNow()
        if budget_remaining <= 0:
            return AnswerNow()          # forced: exclusion-updated belief
        untried = [r for r in self._receptacles if r not in self._tried]
        if not untried:
            return AnswerNow()          # searched everywhere
        choice = self._best_untried(prediction, untried)
        self._tried.add(choice)
        return Sense(receptacle_id=choice)

    def _answer_early(self, prediction: Prediction) -> bool:
        """Confidence early stop; never on a receptacle sensed empty this
        question, and never at the certainty-only default threshold (the
        found-check in ``decide`` is the sole 1.0-grounded stop)."""
        if self._threshold > 1.0 - PROBABILITY_TOLERANCE:
            return False
        return (prediction.confidence >= self._threshold
                and prediction.argmax not in self._tried)

    def _best_untried(self, prediction: Prediction,
                      untried: List[str]) -> str:
        """Highest-probability untried receptacle; seeded-RNG tie-break."""
        top = max(prediction.distribution.get(r, 0.0) for r in untried)
        tied = [r for r in untried
                if prediction.distribution.get(r, 0.0) == top]
        return tied[0] if len(tied) == 1 else self._rng.choice(tied)
