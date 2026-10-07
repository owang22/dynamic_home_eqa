"""Policy: myopic value of information plus a bonus for senses that
settle an ASSUMPTION the graph arm's hypotheses share.

Runs only on top of :class:`~baselines.beliefs.llm_hypothesis_mixture.
LLMHypothesisMixture` in graph mode. The rule extends the myopic
threshold policy exactly as :mod:`baselines.policies.
hypothesis_disambiguation` does — sense the best receptacle while

    (voi(r) + bonus(r)) / cost(r) >= lambda

— but the bonus targets assumption nodes instead of the flat weight
vector::

    bonus(r) = beta * sum over assumptions a of
                 relevance(a) * expected_entropy_reduction(a, r)

``expected_entropy_reduction(a, r)`` is the flat policy's found /
not-found binary-outcome computation applied to the ROLLED-UP value
weights of ``a``: each value's likelihood of "object at r" is the
weighted predictive distribution of the leaves carrying that value.

``relevance(a)`` is the fraction of the current question's object's
predicted mass that differs across ``a``'s values: the total variation
distance between the per-value predicted distributions of the two
highest-weighted values. An assumption whose values agree about where
this object is scores zero, so an open but irrelevant premise attracts
no budget.

With ``beta = 0`` the bonus is never computed and the policy IS
:class:`~baselines.policies.voi_sense.VoIThresholdSense`, decision for
decision and draw for draw (asserted in tests, as for the flat policy).
Each issued sense is classified ``needed`` / ``disambiguation`` as the
flat policy does (``sense_split``).
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple

from baselines.llm_hypotheses.assumption_graph import tv_distance
from baselines.policies.hypothesis_disambiguation import (
    weight_entropy_reduction)
from baselines.policies.voi_sense import (VoIThresholdSense,
                                          value_of_information)
from baselines.types import (Action, EpisodeContext, Prediction, Question,
                             Sense, SenseResult)

if TYPE_CHECKING:
    from baselines.beliefs.llm_hypothesis_mixture import LLMHypothesisMixture


def relevance(per_value: Dict[str, Tuple[float, Dict[str, float]]]) -> float:
    """TV distance between the predicted distributions of the two
    highest-weighted values; 0 with fewer than two weighted values."""
    ranked = sorted(((w, v) for v, (w, _) in per_value.items() if w > 0.0),
                    reverse=True)
    if len(ranked) < 2:
        return 0.0
    (_, top), (_, second) = ranked[0], ranked[1]
    return tv_distance(per_value[top][1], per_value[second][1])


def assumption_bonus(value_dists: Dict[str, Dict[str, Tuple[float,
                                                             Dict[str, float]]]],
                     receptacle: str) -> float:
    """``sum_a relevance(a) * expected_entropy_reduction(a, r)`` from the
    mixture's per-assumption value distributions."""
    total = 0.0
    for per_value in value_dists.values():
        rel = relevance(per_value)
        if rel <= 0.0:
            continue
        weights = [w for w, _ in per_value.values()]
        likelihoods = [d.get(receptacle, 0.0) for _, d in per_value.values()]
        total += rel * weight_entropy_reduction(weights, likelihoods)
    return total


class AssumptionDisambiguationSense(VoIThresholdSense):
    """Myopic VoI plus ``beta`` times the assumption-targeted bonus."""

    def __init__(self, rng: random.Random, lam: float,
                 belief: "LLMHypothesisMixture", beta: float) -> None:
        super().__init__(rng, lam)
        if beta < 0.0:
            raise ValueError(
                f"AssumptionDisambiguationSense: beta {beta} must be >= 0")
        self._belief = belief
        self._beta = float(beta)
        self._last_raw_voi: Dict[str, float] = {}
        self.sense_split: List[Tuple[int, bool]] = []   # (t, needed)

    @property
    def name(self) -> str:
        return (f"AssumptionDisambiguationSense(lambda={self._lam:g},"
                f"beta={self._beta:g})")

    @property
    def beta(self) -> float:
        return self._beta

    def reset(self, context: EpisodeContext) -> None:
        super().reset(context)
        self._last_raw_voi = {}
        self.sense_split = []

    def _sense_values(self, question: Question, prediction: Prediction,
                      untried: Sequence[str]) -> Dict[str, float]:
        voi = value_of_information(prediction.distribution, untried)
        self._last_raw_voi = dict(voi)
        if self._beta == 0.0:
            return voi          # bit-exact myopic policy, no bonus computed
        value_dists = self._belief.value_distributions(question.object_id,
                                                       question.t_query)
        if not value_dists:
            return voi          # flat file: nothing to target
        return {r: voi[r] + self._beta * assumption_bonus(value_dists, r)
                for r in untried}

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        action = super().decide(question, prediction, budget_remaining, t,
                                last_sense)
        if isinstance(action, Sense):
            raw = self._last_raw_voi.get(action.receptacle_id, 0.0)
            needed = raw >= self._lam * self._cost(action.receptacle_id)
            self.sense_split.append((question.t_query, needed))
        return action
