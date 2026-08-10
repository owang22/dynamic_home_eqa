"""Belief: an object is at its modal observed location."""

from __future__ import annotations

from collections import Counter
from typing import List, Tuple

from baselines.beliefs.base import BeliefModel
from baselines.types import Prediction


class MostFrequentLocation(BeliefModel):
    """Predict the most frequently sighted receptacle for the object.

    The distribution is the sighting-frequency histogram, normalized. When
    several receptacles tie for the mode, the most recently sighted of the
    tied set wins (deterministic — no randomness consumed). Never-observed
    objects fall back to the uniform distribution.
    """

    def _predict_from_history(
            self, history: List[Tuple[int, str]], t: int) -> Prediction:
        counts = Counter(receptacle for _, receptacle in history)
        return self._normalized(counts, tie_break_recency=history)
