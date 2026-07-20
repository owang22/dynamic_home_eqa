"""C1 — constant-rate filter (the B2 baseline). Single exponential decay toward
a per-class stationary distribution; leave rates fit by MLE from observed
same-day transitions. C1 is the constant-rate special case of C2 (unit-tested:
C2 restricted to its DC component reproduces C1).

Reference consulted: Persistence Filter (Rosen et al., github.com/
david-m-rosen/Persistence-Filter) — exponential survival with MLE hazard;
reimplemented in our shared-filter interface."""
from __future__ import annotations

import numpy as np

from dynbelief.classical.rates.base import (
    default_class, hazard_mle, occupancy_counts,
)


class C1Constant:
    name = "C1_constant"

    def __init__(self, candidates: list[str]):
        self.candidates = list(candidates)
        self._idx = {c: i for i, c in enumerate(candidates)}
        self._rates: dict[str, float] = {}
        self._occ_obj: dict[str, np.ndarray] = {}
        self._occ_cls: dict[str, np.ndarray] = {}

    def fit(self, observation_history: list[dict]) -> None:
        self._rates = hazard_mle(observation_history)
        self._occ_obj, self._occ_cls = occupancy_counts(
            observation_history, self.candidates)

    def _stationary(self, object_id: str) -> np.ndarray:
        v = self._occ_obj.get(object_id)
        if v is None:
            v = self._occ_cls.get(default_class(object_id))
        if v is None:                                  # unseen object/class (W3)
            v = np.full(len(self.candidates), 1.0 / len(self.candidates))
        return v

    def occupancy(self, object_id: str, receptacle_id: str, t: int) -> float:
        return float(self._stationary(object_id)[self._idx[receptacle_id]])

    def rate(self, object_id: str, receptacle_id: str, t: int) -> float:
        return self._rates.get(default_class(object_id), 0.0)

    def estimator_for(self, object_id: str) -> str:
        if object_id in self._occ_obj:
            return "constant"
        if default_class(object_id) in self._occ_cls:
            return "fallback_class_backoff"
        return "fallback_uniform"
