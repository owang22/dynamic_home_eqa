"""Belief: an object is at its modal observed location.

With a configured half-life, sighting counts decay exponentially with
age, so the mode tracks the drifting world instead of being outvoted by
stale history; without one it is the deliberately naive infinite-memory
histogram. The gap between the two on a bank measures how much that
bank drifts.
"""

from __future__ import annotations

import random
from typing import List, Optional, Tuple

from baselines.beliefs.base import BeliefModel
from baselines.types import Prediction


class MostFrequentLocation(BeliefModel):
    """Predict the (optionally decayed) modal receptacle for the object.

    The distribution is the sighting histogram — decayed by
    ``half_life_h`` hours when set — normalized. Modal ties break by
    recency (deterministic — no randomness consumed). Never-observed
    objects fall back to the uniform distribution.
    """

    def __init__(self, rng: random.Random, exclusion_floor: float = 0.0,
                 half_life_h: Optional[float] = None) -> None:
        super().__init__(rng, exclusion_floor=exclusion_floor)
        if half_life_h is not None and half_life_h <= 0:
            raise ValueError(
                f"MostFrequentLocation: half_life_h {half_life_h} must be > 0")
        self._half_life_s = None if half_life_h is None else half_life_h * 3600

    @property
    def name(self) -> str:
        if self._half_life_s is None:
            return "MostFrequentLocation"
        return f"MostFrequentLocation(hl={self._half_life_s / 3600:g}h)"

    def _predict_from_history(
            self, history: List[Tuple[int, str]], t: int) -> Prediction:
        counts = self._weighted_counts(history, t, self._half_life_s)
        return self._normalized(counts, tie_break_recency=history)
