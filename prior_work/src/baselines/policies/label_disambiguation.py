"""Policy: myopic value of information plus a bonus for senses that
settle a LABEL the tree arm's nodes share.

The tree analogue of :mod:`baselines.policies.assumption_disambiguation`.
Each label splits the nodes into those WITH it and those WITHOUT; the
bonus for sensing receptacle ``r`` is::

    bonus(r) = beta * sum over labels L of
                 relevance(L) * expected_entropy_reduction(L, r)

where the entropy is over the two-way split ``(share of node weight with
L, 1 - share)``, the found / not-found likelihoods are the two groups'
predictive mass on ``r`` for the current question's object, and
``relevance(L)`` is the total variation distance between the two groups'
predictive distributions for that object (a label whose two sides agree
about this object attracts no budget). Labels held by every node or by
none contribute nothing.

With ``beta = 0`` the bonus is never computed and the policy IS
:class:`~baselines.policies.voi_sense.VoIThresholdSense`, decision for
decision and draw for draw.
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
    from baselines.beliefs.tree_hypothesis_mixture import TreeHypothesisMixture


def label_bonus(label_dists: Dict[str, Tuple[float, Dict[str, float],
                                             Dict[str, float]]],
                receptacle: str) -> float:
    """``sum_L relevance(L) * expected_entropy_reduction(L, r)``."""
    total = 0.0
    for share, with_, without in label_dists.values():
        rel = tv_distance(with_, without)
        if rel <= 0.0:
            continue
        total += rel * weight_entropy_reduction(
            [share, 1.0 - share],
            [with_.get(receptacle, 0.0), without.get(receptacle, 0.0)])
    return total


class LabelDisambiguationSense(VoIThresholdSense):
    """Myopic VoI plus ``beta`` times the label-targeted bonus."""

    def __init__(self, rng: random.Random, lam: float,
                 belief: "TreeHypothesisMixture", beta: float) -> None:
        super().__init__(rng, lam)
        if beta < 0.0:
            raise ValueError(f"LabelDisambiguationSense: beta {beta} must be "
                             f">= 0")
        self._belief = belief
        self._beta = float(beta)
        self._last_raw_voi: Dict[str, float] = {}
        self.sense_split: List[Tuple[int, bool]] = []   # (t, needed)

    @property
    def name(self) -> str:
        return (f"LabelDisambiguationSense(lambda={self._lam:g},"
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
        dists = self._belief.label_distributions(question.object_id,
                                                 question.t_query)
        if not dists:
            return voi
        return {r: voi[r] + self._beta * label_bonus(dists, r)
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


__all__ = ["LabelDisambiguationSense", "label_bonus"]
