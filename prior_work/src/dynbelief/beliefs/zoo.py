"""Belief tiers b0–b2 (b3 lives in perpetua.py).

b0_lastseen   predicted parent = last observed, probability 1.0.
b1_longmem    per-object running frequency over past observations
              (Laplace-smoothed; sees every feed it was ever given).
b2_classdecay last-seen one-hot decays exponentially toward a per-CLASS
              co-occurrence prior; per-class decay rate by MLE.

b2 rate MLE: consecutive observation pairs (t1,p1)→(t2,p2) of an object are
the data. Under an exponential change model, P(no change in Δt) = e^{-λΔt};
treating a pair with p1 != p2 as ">=1 change" gives the standard hazard
estimator λ̂_class = (# changed pairs) / (Σ Δt over all pairs), pooled per
object class. Pairs come from every observation fed to the model — training
feeds included — and survive reset() (routine knowledge, not test-day state).
"""
from __future__ import annotations

import math

import numpy as np

from dynbelief.beliefs.base import _Common, object_class


class B0LastSeen(_Common):
    name = "b0_lastseen"

    def predict(self, t: int) -> dict[int, np.ndarray]:
        out = {}
        for obj in self.objects:
            seen = self.last_seen.get(obj)
            out[obj] = self.onehot(seen[1]) if seen else self.uniform()
        return out


class B1LongMem(_Common):
    name = "b1_longmem"

    def __init__(self) -> None:
        super().__init__()
        self.counts: dict[int, dict[int, int]] = {}  # obj -> parent -> n

    def observe(self, t, obs) -> None:
        super().observe(t, obs)
        for obj, (parent, _s) in obs.items():
            self.counts.setdefault(obj, {})
            self.counts[obj][parent] = self.counts[obj].get(parent, 0) + 1

    def predict(self, t: int) -> dict[int, np.ndarray]:
        out = {}
        for obj in self.objects:
            v = np.ones(self.n_candidates)  # Laplace
            for parent, n in self.counts.get(obj, {}).items():
                v[parent] += n
            out[obj] = v / v.sum()
        return out


class B2ClassDecay(_Common):
    name = "b2_classdecay"

    def __init__(self, obj_class_of: dict[int, str]) -> None:
        super().__init__()
        self.obj_class_of = obj_class_of
        self._rates: dict[str, float] | None = None
        self._priors: dict[str, np.ndarray] | None = None
        self._prior_counts: dict[str, dict[int, int]] = {}  # class -> parent -> n

    def observe(self, t, obs) -> None:
        super().observe(t, obs)
        for obj, (parent, _s) in obs.items():
            cls = self.obj_class_of.get(obj, "?")
            self._prior_counts.setdefault(cls, {})
            self._prior_counts[cls][parent] = self._prior_counts[cls].get(parent, 0) + 1
        self._rates = None  # stats changed; re-fit lazily
        self._priors = None

    def _fit(self) -> None:
        rates: dict[str, list] = {}
        for obj, pairs in self.pair_stats.items():
            cls = self.obj_class_of.get(obj, "?")
            rates.setdefault(cls, [0, 0.0])
            for (t1, p1, t2, p2) in pairs:
                rates[cls][0] += int(p1 != p2)
                rates[cls][1] += (t2 - t1)
        self._rates = {cls: (n / dt if dt > 0 else 0.0) for cls, (n, dt) in rates.items()}
        self._priors = {}
        for cls, counts in self._prior_counts.items():
            v = np.ones(self.n_candidates)
            for parent, n in counts.items():
                v[parent] += n
            self._priors[cls] = v / v.sum()

    def predict(self, t: int) -> dict[int, np.ndarray]:
        if self._rates is None:
            self._fit()
        out = {}
        for obj in self.objects:
            cls = self.obj_class_of.get(obj, "?")
            prior = (self._priors or {}).get(cls)
            if prior is None:
                prior = self.uniform()
            seen = self.last_seen.get(obj)
            if seen is None:
                out[obj] = prior
                continue
            t_seen, parent = seen
            lam = (self._rates or {}).get(cls, 0.0)
            w = math.exp(-lam * max(0, t - t_seen))
            out[obj] = w * self.onehot(parent) + (1 - w) * prior
        return out
