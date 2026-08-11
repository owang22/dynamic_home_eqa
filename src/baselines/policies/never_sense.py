"""Policy: never spend budget; always answer straight from belief."""

from __future__ import annotations

from typing import Optional

from baselines.policies.base import DecisionPolicy
from baselines.types import (Action, AnswerNow, Prediction, Question,
                             SenseResult)


class NeverSense(DecisionPolicy):
    """Always :class:`~baselines.types.AnswerNow`. The zero-cost floor."""

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: int, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        return AnswerNow()
