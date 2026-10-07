"""C3 — periodic logistic GLM: multinomial logistic regression of occupancy on
Fourier features (24h + 168h harmonics, W1) PLUS calendar covariates (weekend
flag) and weekend x daily-harmonic interactions. The statistical twin of C2
that can express day-type MIXTURES (needed for T1/T2 atypical households):
the weekend interaction lets weekday and weekend occupancy schedules differ.

L3: features come from calendar_features(t) — a function of t ONLY; no
resident-specific day-type feature exists (asserted structurally in base.py).
L2 covariates (clock, day-of-week/weekend) are allowed.

sklearn LogisticRegression (multinomial, L2); penalty C swept in {0.1, 1, 10}
by held-out observation likelihood (L4). One model per OBJECT (categorical
over receptacles), which keeps the class count small and normalization exact.

Leave rates: same constant per-class MLE as C1 — the GLM only replaces the
occupancy term."""
from __future__ import annotations

from collections import defaultdict

import numpy as np

from dynbelief.classical.rates.base import (
    calendar_features, default_class, hazard_mle, occupancy_counts,
)


class C3PeriodicGLM:
    name = "C3_glm"

    def __init__(self, candidates: list[str], C: float = 1.0):
        self.candidates = list(candidates)
        self._idx = {c: i for i, c in enumerate(candidates)}
        self.C = float(C)
        self._rates: dict[str, float] = {}
        self._occ_obj: dict[str, np.ndarray] = {}
        self._occ_cls: dict[str, np.ndarray] = {}
        self._models: dict[str, object] = {}     # obj -> fitted sklearn model
        self._classes: dict[str, list[int]] = {} # obj -> candidate idx per model class
        self.degenerate: bool = False            # W2 logging

    def fit(self, observation_history: list[dict]) -> None:
        from sklearn.linear_model import LogisticRegression
        self._rates = hazard_mle(observation_history)
        self._occ_obj, self._occ_cls = occupancy_counts(
            observation_history, self.candidates)
        xs: dict[str, list] = defaultdict(list)
        ys: dict[str, list] = defaultdict(list)
        for row in observation_history:
            phi = calendar_features(row["t_min"])
            for o, r in row["parents"].items():
                if r in self._idx:
                    xs[o].append(phi)
                    ys[o].append(self._idx[r])
        self._models, self._classes = {}, {}
        self.degenerate = False
        for o in xs:
            y = np.array(ys[o])
            if len(set(y.tolist())) < 2 or len(y) < 8:
                self.degenerate = True           # single-receptacle or tiny history
                continue                          # -> falls back to empirical occupancy
            m = LogisticRegression(C=self.C, max_iter=1000)
            m.fit(np.array(xs[o]), y)
            self._models[o] = m
            self._classes[o] = list(m.classes_)

    def _dist(self, object_id: str, t: int) -> np.ndarray:
        m = self._models.get(object_id)
        if m is None:
            v = self._occ_obj.get(object_id)
            if v is None:
                v = self._occ_cls.get(default_class(object_id))
            if v is None:
                return np.full(len(self.candidates), 1.0 / len(self.candidates))
            return v
        proba = m.predict_proba(calendar_features(t).reshape(1, -1))[0]
        out = np.full(len(self.candidates), 1e-4)
        for p, ci in zip(proba, self._classes[object_id]):
            out[ci] = p
        return out / out.sum()

    def occupancy(self, object_id: str, receptacle_id: str, t: int) -> float:
        return float(self._dist(object_id, t)[self._idx[receptacle_id]])

    def rate(self, object_id: str, receptacle_id: str, t: int) -> float:
        return self._rates.get(default_class(object_id), 0.0)

    def estimator_for(self, object_id: str) -> str:
        if object_id in self._models:
            return "glm"
        if object_id in self._occ_obj:
            return "fallback_empirical_occ"
        if default_class(object_id) in self._occ_cls:
            return "fallback_class_backoff"
        return "fallback_uniform"
