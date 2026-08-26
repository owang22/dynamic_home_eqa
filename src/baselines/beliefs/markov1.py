"""Belief: a per-object first-order Markov chain over receptacles.

Consecutive sightings of an object form transition observations: sighting
``(t1, r1)`` followed by ``(t2, r2)`` counts one ``r1 -> r2`` transition
(``r1 == r2`` is a self-transition — evidence the object stays put).
Prediction propagates ONE step from the last sighting's receptacle: the
Laplace-smoothed transition row for that receptacle, where the single step
stands for "whatever happened since the last sighting". When the elapsed
time since the last sighting exceeds the mixing cutoff the chain is
assumed mixed and the model backs off to the object's stationary
(sighting-frequency) distribution instead.

Fixed a-priori hyperparameters (see :class:`Markov1Config`): Laplace
``alpha = 1.0`` per destination receptacle; mixing cutoff 24 h — the
domain's natural cycle, matching the frozen panel's half-life choice; and
the frozen 24 h count half-life on both transition and frequency counts
(a transition is aged by its destination-sighting time, exactly as
frequency counts are aged by their sighting time).

All times are seconds since episode start. Never-observed objects fall
back to the uniform distribution via the base class.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from baselines.beliefs.base import BeliefModel
from baselines.types import Prediction


@dataclass(frozen=True)
class Markov1Config:
    """Fixed hyperparameters for :class:`Markov1` (no per-bank tuning)."""

    alpha: float = 1.0            # Laplace pseudo-count per destination
    mixing_cutoff_h: float = 24.0  # elapsed time beyond which the chain
    #                                is treated as mixed (stationary backoff)
    half_life_h: float = 24.0     # count decay half-life (frozen, panel-wide)

    def __post_init__(self) -> None:
        if self.alpha <= 0:
            raise ValueError(f"Markov1Config: alpha {self.alpha} must be > 0")
        if self.mixing_cutoff_h <= 0 or self.half_life_h <= 0:
            raise ValueError(
                f"Markov1Config: mixing_cutoff_h {self.mixing_cutoff_h} and "
                f"half_life_h {self.half_life_h} must be > 0")


class Markov1(BeliefModel):
    """One-step transition propagation from the last sighting.

    Within the mixing cutoff: the Laplace-smoothed decayed transition row
    of the last-sighted receptacle. Beyond it: the decayed
    sighting-frequency (stationary) distribution. Argmax ties break by
    preferring the last-sighted receptacle, then by receptacle order — no
    randomness consumed.
    """

    def __init__(self, rng: random.Random, config: Markov1Config,
                 exclusion_floor: float = 0.0) -> None:
        super().__init__(rng, exclusion_floor=exclusion_floor)
        self._cfg = config

    @property
    def name(self) -> str:
        return (f"Markov1(a={self._cfg.alpha:g},"
                f"cut={self._cfg.mixing_cutoff_h:g}h,"
                f"hl={self._cfg.half_life_h:g}h)")

    def _predict_from_history(
            self, history: List[Tuple[int, str]], t: int) -> Prediction:
        half_life_s = self._cfg.half_life_h * 3600
        t_last, r_last = history[-1]
        if t - t_last > self._cfg.mixing_cutoff_h * 3600:
            counts = self._weighted_counts(history, t, half_life_s)
            return self._normalized(counts, tie_break_recency=history)
        row = self._transition_row(history, r_last, t, half_life_s)
        return self._row_prediction(row, r_last)

    def _transition_row(self, history: List[Tuple[int, str]], origin: str,
                        t: int, half_life_s: float) -> Dict[str, float]:
        """Decayed ``origin -> *`` transition counts plus Laplace alpha."""
        row = {r: self._cfg.alpha for r in self._receptacles()}
        for (_, r_from), (t_to, r_to) in zip(history, history[1:]):
            if r_from == origin:
                row[r_to] += 2.0 ** (-max(0, t - t_to) / half_life_s)
        return row

    def _row_prediction(self, row: Dict[str, float],
                        r_last: str) -> Prediction:
        total = sum(row.values())
        dist = {r: c / total for r, c in row.items()}
        top = max(dist.values())
        tied = [r for r in self._receptacles() if dist[r] == top]
        argmax = r_last if r_last in tied else tied[0]
        return Prediction(distribution=dist, argmax=argmax)
