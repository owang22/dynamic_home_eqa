"""Belief: an object is wherever it was most recently seen."""

from __future__ import annotations

from typing import List, Tuple

from baselines.beliefs.base import BeliefModel
from baselines.types import Prediction


class LastObservation(BeliefModel):
    """Predict the receptacle of the most recent sighting, with certainty 1.

    The distribution is one-hot on the last observed receptacle. Sightings
    are kept in arrival order, which the harness guarantees is time order;
    if two sightings share a timestamp the later-arriving one wins.
    Never-observed objects fall back to the uniform distribution over all
    receptacles (see :class:`~baselines.beliefs.base.BeliefModel.predict`).
    """

    def _predict_from_history(
            self, history: List[Tuple[int, str]], t: int) -> Prediction:
        last_receptacle = history[-1][1]
        return Prediction(distribution={last_receptacle: 1.0},
                          argmax=last_receptacle)
