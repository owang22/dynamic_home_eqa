"""Policy: never spend budget; always answer straight from belief."""

from __future__ import annotations

from baselines.policies.base import DecisionPolicy
from baselines.types import Action, AnswerNow, Prediction, Question


class NeverSense(DecisionPolicy):
    """Always :class:`~baselines.types.AnswerNow`. The zero-cost floor."""

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: int, t: int) -> Action:
        return AnswerNow()
