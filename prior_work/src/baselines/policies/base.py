"""Decision-policy interface.

A policy looks at one question plus the belief's current prediction and
either commits to an answer or spends one budget unit sensing a
receptacle. After a sense, the harness feeds the result to the belief and
asks the policy again for the *same* question, so policies must terminate:
every implementation guarantees a bounded number of Sense decisions per
question, and the harness additionally forces an answer once the day's
budget can no longer cover the requested sense. Budget accounting itself
lives in the harness — ``budget_remaining`` is read-only information, and
a float: a sense costs 1.0 in the room the robot is already in and
``1 + c`` in any other, so a policy that wants to price its options reads
``context.sense_cost(receptacle_id)`` off the
:class:`~baselines.types.EpisodeContext` it was reset with (the harness
keeps the robot's position live inside it).

All times are seconds since episode start.
"""

from __future__ import annotations

import abc

from typing import Optional

from baselines.types import (Action, EpisodeContext, Prediction, Question,
                             SenseResult)


class DecisionPolicy(abc.ABC):
    """Base class for sense-or-answer decision policies."""

    @property
    def name(self) -> str:
        """Stable identifier used in logs and result tables."""
        return type(self).__name__

    def reset(self, context: EpisodeContext) -> None:
        """Start a fresh episode. Stateless policies need not override."""

    @abc.abstractmethod
    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        """Answer now, or sense one receptacle first.

        Called repeatedly for the same question after each sense; must
        eventually return :class:`~baselines.types.AnswerNow`. Returning
        :class:`~baselines.types.Sense` whose cost exceeds
        ``budget_remaining`` is treated by the harness as a forced answer
        (and logged as such), so polite policies check the budget
        themselves.

        ``last_sense`` is the result of this question's most recent sense
        (None before the first): search-style policies read it to notice
        when the queried object has been found. It duplicates what the
        belief already ingested, so ignoring it is always safe.
        """
