"""Policy: verify every answer by sensing the predicted receptacle first."""

from __future__ import annotations

from baselines.policies.base import DecisionPolicy
from baselines.types import (Action, AnswerNow, EpisodeContext, Prediction,
                             Question, Sense)


class AlwaysSense(DecisionPolicy):
    """Sense the belief's argmax once per question (budget permitting).

    On the first ``decide`` for a question, if budget remains, sense the
    prediction's argmax; when re-asked after that sense — or when budget is
    already exhausted — answer. Tracking the current question_id guarantees
    exactly one sense per question, hence termination.
    """

    def __init__(self) -> None:
        self._sensed_question: str | None = None

    def reset(self, context: EpisodeContext) -> None:
        self._sensed_question = None

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: int, t: int) -> Action:
        if budget_remaining > 0 and self._sensed_question != question.question_id:
            self._sensed_question = question.question_id
            return Sense(receptacle_id=prediction.argmax)
        return AnswerNow()
