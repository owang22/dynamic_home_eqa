"""Policy: myopic value of information plus a bonus for senses that
sharpen the hypothesis-mixture weights.

Runs only on top of :class:`~baselines.beliefs.hypothesis_mixture.
HypothesisMixture`. The rule extends the myopic threshold policy: sense
the best receptacle while

    (voi(r) + beta * weight_entropy_reduction(r)) / cost(r) >= lambda

``voi(r)`` is the one-step lookahead of :mod:`baselines.policies.
voi_sense`, unchanged. The bonus is the expected reduction in Shannon
entropy (nats) of the mixture's weight vector from sensing ``r``,
computed for the CURRENT question's object O:

* the mixture predicts O is at ``r`` with ``p_mix(r) = sum_i w_i p_i(r)``;
* outcome "found": posterior weights ``w_i ∝ w_i * p_i(r)``;
* outcome "not found": ``w_i ∝ w_i * (1 - p_i(r))``;
* value = ``H(w) - [p_mix(r) H(w|found) + (1 - p_mix(r)) H(w|not)]``,
  one multiply per particle per outcome, never negative (conditioning
  cannot raise expected entropy).

The bonus is independent of whether the sense helps ANSWER the question —
it pays for senses whose outcome the particles disagree about, which is
exactly what tells the mixture which hypothesis is running this
household. Using the current question's object keeps the computation to
the distributions already in hand; scanning other objects for an even
more disambiguating sense is deliberately out.

With ``beta = 0`` the bonus is never computed and the policy IS
:class:`~baselines.policies.voi_sense.VoIThresholdSense`, decision for
decision and draw for draw (asserted in tests).

Each issued sense is classified for the study's split figure: ``needed``
if the raw voi alone cleared the price (the myopic rule would have taken
it too), ``disambiguation`` if only the bonus pushed it over
(``sense_split`` accumulates ``(t, needed)`` per episode).
"""

from __future__ import annotations

import math
import random
from typing import Dict, List, Optional, Sequence, Tuple

from baselines.beliefs.hypothesis_mixture import HypothesisMixture
from baselines.policies.voi_sense import (VoIThresholdSense,
                                          value_of_information)
from baselines.types import (Action, EpisodeContext, Prediction, Question,
                             Sense, SenseResult)


def entropy(weights: Sequence[float]) -> float:
    """Shannon entropy in nats of a normalized weight vector."""
    return -sum(w * math.log(w) for w in weights if w > 0.0)


def weight_entropy_reduction(weights: Sequence[float],
                             particle_p: Sequence[float]) -> float:
    """Expected entropy drop of ``weights`` from a binary found/not-found
    outcome whose per-particle likelihoods are ``particle_p``."""
    p_mix = sum(w * p for w, p in zip(weights, particle_p))
    before = entropy(weights)
    expected_after = 0.0
    for outcome_p, likelihoods in (
            (p_mix, particle_p),
            (1.0 - p_mix, [1.0 - p for p in particle_p])):
        if outcome_p <= 0.0:
            continue
        posterior = [w * lk for w, lk in zip(weights, likelihoods)]
        total = sum(posterior)
        if total <= 0.0:
            continue
        expected_after += outcome_p * entropy([w / total for w in posterior])
    return max(0.0, before - expected_after)


class HypothesisDisambiguationSense(VoIThresholdSense):
    """Myopic VoI plus ``beta`` times the expected weight-entropy drop."""

    def __init__(self, rng: random.Random, lam: float,
                 belief: HypothesisMixture, beta: float) -> None:
        super().__init__(rng, lam)
        if beta < 0.0:
            raise ValueError(
                f"HypothesisDisambiguationSense: beta {beta} must be >= 0")
        self._belief = belief
        self._beta = float(beta)
        self._last_raw_voi: Dict[str, float] = {}
        self.sense_split: List[Tuple[int, bool]] = []   # (t, needed)

    @property
    def name(self) -> str:
        return (f"HypothesisDisambiguationSense(lambda={self._lam:g},"
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
        weights = self._belief.weights
        distributions = self._belief.particle_distributions(
            question.object_id, question.t_query)
        return {r: voi[r] + self._beta * weight_entropy_reduction(
                    weights, [d.get(r, 0.0) for d in distributions])
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
