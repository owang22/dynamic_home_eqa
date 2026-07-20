"""C2 — spectral (FreMEn-style) occupancy.

p_edge(obj, r, t) = mu + sum_j [a_j cos(w_j t) + b_j sin(w_j t)], coefficients
from streaming Fourier sums over the binary edge-occupancy series sampled at
the (irregular) snapshot times; keep the top-K components by amplitude. K is a
hyperparameter swept in {1,2,3,5} by held-out observation likelihood (L4);
K=0 = DC-only = the C1 special case (unit-tested equivalence).

Candidate period set (W1: MUST include 24h and 168h):
    {168h, 84h, 56h, 42h, 24h, 12h, 8h, 6h, 4h}

Leave rates: same constant per-class MLE as C1 — C2 differs from C1 ONLY in
the occupancy term (the brief's "differ only in rate parameterization").

References consulted (reimplemented, not depended on): FreMEn
github.com/gestom/fremen (+wiki: incremental spectral update + order
selection), gestom/fremen_activity (per-state activity pipeline),
sergimolina/STeF-Map (histogram->FreMEn->prediction walkthrough)."""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np

from dynbelief import MIN_PER_DAY
from dynbelief.classical.rates.base import (
    default_class, hazard_mle, occupancy_counts,
)

CANDIDATE_PERIODS_MIN = [168 * 60, 84 * 60, 56 * 60, 42 * 60,
                         24 * 60, 12 * 60, 8 * 60, 6 * 60, 4 * 60]


class C2Spectral:
    name = "C2_spectral"

    def __init__(self, candidates: list[str], K: int = 2,
                 periods_min=None):
        self.candidates = list(candidates)
        self._idx = {c: i for i, c in enumerate(candidates)}
        self.K = int(K)
        self.periods = list(periods_min or CANDIDATE_PERIODS_MIN)
        self._rates: dict[str, float] = {}
        self._occ_obj: dict[str, np.ndarray] = {}
        self._occ_cls: dict[str, np.ndarray] = {}
        # per (obj, recep): (mu, [(w, a, b) x K]) — kept components
        self._spec: dict[tuple, tuple] = {}

    def fit(self, observation_history: list[dict]) -> None:
        self._rates = hazard_mle(observation_history)
        self._occ_obj, self._occ_cls = occupancy_counts(
            observation_history, self.candidates)
        # streaming Fourier sums per (obj, recep) edge over binary occupancy
        sums: dict[tuple, dict] = defaultdict(
            lambda: {"n": 0, "s": 0.0,
                     "re": np.zeros(len(self.periods)),
                     "im": np.zeros(len(self.periods))})
        w = np.array([2 * math.pi / p for p in self.periods])
        for row in observation_history:
            t = row["t_min"]
            ct, st = np.cos(w * t), np.sin(w * t)
            for o, r_obs in row["parents"].items():
                for r in self.candidates:
                    x = 1.0 if r == r_obs else 0.0
                    e = sums[(o, r)]
                    e["n"] += 1
                    e["s"] += x
                    e["re"] += x * ct
                    e["im"] += x * st
        # basis sample-means once (irregular sampling makes cos/sin means != 0)
        ts = np.array([r["t_min"] for r in observation_history], dtype=float)
        mean_ct = np.array([np.mean(np.cos(wj * ts)) for wj in w]) if len(ts) else np.zeros(len(w))
        mean_st = np.array([np.mean(np.sin(wj * ts)) for wj in w]) if len(ts) else np.zeros(len(w))
        self._spec = {}
        for key, e in sums.items():
            n = max(1, e["n"])
            mu = e["s"] / n
            # centered component amplitudes (FreMEn incremental estimate)
            a = 2 * (e["re"] / n - mu * mean_ct)
            b = 2 * (e["im"] / n - mu * mean_st)
            amp = np.sqrt(a ** 2 + b ** 2)
            order = np.argsort(-amp)[: self.K]
            comps = [(float(w[j]), float(a[j]), float(b[j])) for j in order]
            self._spec[key] = (float(mu), comps)

    def occupancy(self, object_id: str, receptacle_id: str, t: int) -> float:
        spec = self._spec.get((object_id, receptacle_id))
        if spec is None:                              # unseen object (W3)
            v = self._occ_cls.get(default_class(object_id))
            if v is None:
                return 1.0 / len(self.candidates)
            return float(v[self._idx[receptacle_id]])
        mu, comps = spec
        p = mu + sum(a * math.cos(w * t) + b * math.sin(w * t)
                     for (w, a, b) in comps)
        return float(min(0.999, max(1e-4, p)))

    def rate(self, object_id: str, receptacle_id: str, t: int) -> float:
        return self._rates.get(default_class(object_id), 0.0)

    def estimator_for(self, object_id: str) -> str:
        if any((object_id, r) in self._spec for r in self.candidates):
            return "spectral"
        if default_class(object_id) in self._occ_cls:
            return "fallback_class_backoff"
        return "fallback_uniform"


