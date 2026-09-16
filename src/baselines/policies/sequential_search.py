"""Policy: search receptacles in belief order until the object is found.

Per question the loop is:

1. Read the belief's prediction for the queried object.
2. If the top receptacle's probability meets ``confidence_threshold``,
   answer. At the default threshold of 1.0 this early stop is deliberately
   restricted to certainty grounded at query time — a sense THIS question
   that returned the object. Sub-1.0 thresholds instead trust the
   belief's stated confidence and answer without confirmation; that is
   only sound for calibrated beliefs (the basic one-hot recency belief
   claims near-certainty for arbitrarily old sightings), so the panel and
   all defaults use 1.0.
3. Otherwise, if budget remains, sense the highest-probability receptacle
   not yet tried this question. A miss is an empty look at the query
   instant inside the belief (base pipeline, weight 1: full suppression),
   so the next prediction naturally ranks the next-best receptacle. A hit
   answers immediately.
4. On a person-sensing bank, once every sensable receptacle has been
   tried: sense every resident the sweep listed, one at a time
   (:class:`~baselines.types.SensePerson`). A resident found carrying
   the object answers ``ON_PERSON`` immediately (a hit at the query
   instant, like a receptacle hit).
5. With no budget left (or everything tried), answer from the current
   belief.

There is no elimination logic here. OUT_OF_HOUSE, which no sense can
reach, is answered because the belief's floor mass on it survives when
everything else has been looked at empty this question: after a full
sweep the belief's own argmax is the remainder. ON_PERSON is not
inferred: on a person-sensing bank it is looked at through the
residents, and the belief base class suppresses it once every resident
has been cleared at the query instant — looked at empty, or listed in
no room by the full sweep, i.e. out. So after the sweep and the
resident pass exactly one location is left standing, OUT_OF_HOUSE, and
the unlimited-budget invariant (any bank whose queried objects are
each somewhere at query time scores task accuracy 1.0, with every
belief model) holds without the policy naming anything. On a bank
without person sensing the two answer tokens are both unobservable and
the invariant holds only up to their tie.

The tried set is cheap insurance against re-sensing and bounds the loop
(each receptacle and each resident at most once per question); in
principle it is redundant, because a within-question empty look is
fresh, its factor is 0, and the argmax has already moved off that
receptacle. The one guard that remains is the found-this-question
early stop: a hit at the query instant is ground truth, and the
belief's one-hot override at that instant agrees with it.

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
                             Sense, SensePerson, SenseResult)


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
        self._person_sensing = False
        self._question_id: Optional[str] = None
        self._tried: Set[str] = set()
        self._listed: List[str] = []       # residents the sweep listed
        self._residents_tried: Set[str] = set()

    def reset(self, context: EpisodeContext) -> None:
        # Only sensable receptacles are searchable; an unsensable one
        # (OUT_OF_HOUSE) is answered when the belief's mass ends up there.
        self._receptacles = context.sensable_receptacle_ids
        self._person_sensing = context.person_sensing
        self._question_id = None
        self._tried = set()
        self._listed = []
        self._residents_tried = set()

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        if self._question_id != question.question_id:
            self._question_id = question.question_id
            self._tried = set()
            self._listed = []
            self._residents_tried = set()
        if last_sense is not None:
            for res in last_sense.residents_present:
                if res not in self._listed:
                    self._listed.append(res)
        if last_sense is not None and question.object_id in last_sense.contents:
            return AnswerNow()          # found at query time: certain
        if self._answer_early(prediction):
            return AnswerNow()
        if budget_remaining <= 0:
            return AnswerNow()          # forced: answer the current belief
        untried = [r for r in self._receptacles if r not in self._tried]
        if untried:
            choice = self._best_untried(prediction, untried)
            self._tried.add(choice)
            return Sense(receptacle_id=choice)
        if self._person_sensing:
            for res in self._listed:
                if res not in self._residents_tried:
                    self._residents_tried.add(res)
                    return SensePerson(resident_id=res)
        return AnswerNow()              # searched everywhere

    def _answer_early(self, prediction: Prediction) -> bool:
        """Confidence early stop; never on a receptacle sensed this
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
