"""Belief: the object is probably where it was last seen, with that
confidence decaying over elapsed time toward the object's frequency
distribution.

The two panel recency-family beliefs are each degenerate at one end:
``LastObservation`` puts probability 1.0 on one receptacle (its log loss
explodes on any miss and its confidence carries no information), and
``MostFrequentLocation`` ignores how recently anything was seen. This
model interpolates between them with a single elapsed-time weight

    w = 2^(-(t - t_last) / smoothing_half_life)

on the last-seen receptacle, with the remaining ``1 - w`` spread over the
object's decayed sighting histogram. A fresh sighting behaves like
last-observation, a stale one like most-frequent, and the distribution
is proper throughout, so log loss and calibration are finite and
meaningful.

The frequency component uses the panel's frozen 24 h count half-life
(see the registry module docstring). The smoothing half-life was chosen
once on a three-household development split (storyfirst hh1/hh2/hh3,
mean question-set accuracy over the budget-sweep levels, candidates
{2, 6, 12, 24, 48} h; 6 h won at 0.6371 with 2 h at 0.6359) and then
frozen — it is deliberately not tuned per bank.

When negative evidence excludes the last-seen receptacle, the reclaimed
mass falls back on the same frequency distribution rather than uniform
(see :meth:`~baselines.beliefs.base.BeliefModel._exclusion_backoff`):
"not where I last saw it" should mean "probably at one of its usual
spots", not "anywhere in the house".
"""

from __future__ import annotations

import dataclasses
import random
from typing import Dict, List, Tuple, Union

from baselines.beliefs.base import BeliefModel
from baselines.types import Prediction


@dataclasses.dataclass(frozen=True)
class SmoothedRecencyConfig:
    """Fixed knobs; see the module docstring for how each was set."""

    smoothing_half_life_h: float = 6.0
    frequency_half_life_h: float = 24.0

    def __post_init__(self) -> None:
        if self.smoothing_half_life_h <= 0:
            raise ValueError(
                f"SmoothedRecencyConfig: smoothing_half_life_h "
                f"{self.smoothing_half_life_h} must be > 0")
        if self.frequency_half_life_h <= 0:
            raise ValueError(
                f"SmoothedRecencyConfig: frequency_half_life_h "
                f"{self.frequency_half_life_h} must be > 0")


class SmoothedRecency(BeliefModel):
    """Last-seen receptacle, decaying toward the frequency histogram.

    Never-observed objects fall back to the uniform distribution (base
    class behavior). Argmax ties break by recency, deterministically.
    """

    def __init__(self, rng: random.Random, config: SmoothedRecencyConfig,
                 exclusion_floor: float = 0.0) -> None:
        super().__init__(rng, exclusion_floor=exclusion_floor)
        self._config = config
        self._smoothing_s = config.smoothing_half_life_h * 3600
        self._frequency_s = config.frequency_half_life_h * 3600

    @property
    def name(self) -> str:
        return (f"SmoothedRecency(hl={self._config.smoothing_half_life_h:g}h,"
                f"freq={self._config.frequency_half_life_h:g}h)")

    def _frequency_distribution(
            self, history: List[Tuple[int, str]], t: int) -> Dict[str, float]:
        counts = self._weighted_counts(history, t, self._frequency_s)
        total = sum(counts.values())
        return {r: c / total for r, c in counts.items()}

    def _predict_from_history(
            self, history: List[Tuple[int, str]], t: int) -> Prediction:
        t_last, last_receptacle = history[-1]
        weight = 2.0 ** (-max(0, t - t_last) / self._smoothing_s)
        frequency = self._frequency_distribution(history, t)
        dist = {r: (1.0 - weight) * p for r, p in frequency.items()}
        dist[last_receptacle] = dist.get(last_receptacle, 0.0) + weight
        return self._normalized(dist, tie_break_recency=history)

    def _exclusion_backoff(self, object_id: str, t: int
                           ) -> Union[Dict[str, float], None]:
        """The frequency histogram: an excluded last-seen receptacle
        sends its mass to the object's other usual spots, not uniform."""
        history = self._history.get(object_id, [])
        if not history:
            return None
        return self._frequency_distribution(history, t)
