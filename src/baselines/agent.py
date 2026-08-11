"""Agent = one belief model + one decision policy, nothing else.

The factorization is the point: any belief composes with any policy, and
later phases add new members on either axis without touching this class or
the harness. If a behaviour seems to need an Agent subclass, it belongs in
a belief model or a policy instead.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from baselines.beliefs.base import BeliefModel
from baselines.policies.base import DecisionPolicy
from baselines.types import (Action, EpisodeContext, Observation, Prediction,
                             Question, SenseResult)


@dataclass(frozen=True)
class Agent:
    """Composition of a belief model and a decision policy."""

    belief: BeliefModel
    policy: DecisionPolicy

    @property
    def name(self) -> str:
        """`belief+policy`, used as the row key in all result tables."""
        return f"{self.belief.name}+{self.policy.name}"

    def reset(self, context: EpisodeContext) -> None:
        """Start a fresh episode for both components."""
        self.belief.reset(context)
        self.policy.reset(context)

    def observe(self, evidence: Union[Observation, SenseResult]) -> None:
        """Fold stream observations or paid sense results into the belief."""
        self.belief.update(evidence)

    def predict(self, question: Question) -> Prediction:
        """Current belief about the questioned object at query time."""
        return self.belief.predict(question.object_id, question.t_query)

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: int,
               last_sense: Union[SenseResult, None] = None) -> Action:
        """Delegate the sense-or-answer choice to the policy."""
        return self.policy.decide(question, prediction, budget_remaining,
                                  question.t_query, last_sense)
