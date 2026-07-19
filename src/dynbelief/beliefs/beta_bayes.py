"""B2.5 -- Beta-Bayesian per-edge belief (spec's belief zoo, between B2 and B3).

Where B2 (B2ClassDecay) uses a single MLE leave-RATE per class and a global
co-occurrence prior, B2.5 is fully Bayesian per SOURCE EDGE:

  * leave-vs-stay: per (class, source-receptacle) a Beta(a, b) posterior on the
    per-pair leave probability, updated from consecutive same-day observation
    pairs. The prior Beta(a0, b0) gives calibrated behaviour on little data --
    which is exactly the E1 "few observation days" regime where a point
    estimate is overconfident.
  * destination given a leave: per (class, source-receptacle) a Dirichlet over
    destination receptacles (symmetric prior alpha0), so a leave spreads mass
    over destinations actually seen FROM that source rather than a global prior.

predict(t) for an object last seen at (t_seen, source):
    hazard h = posterior-mean leave prob per average inter-obs gap, converted to
    a rate lam = h / mean_gap; stay-weight w = exp(-lam * elapsed).
    p = w * onehot(source) + (1 - w) * Dirichlet-mean(dest | class, source).

Reduces to a decay model when data is abundant, but with honest uncertainty
(wider spread) when a source edge has few observations. Matches the
BeliefModel Protocol; drop-in for the harness and the day-budget loop.
"""
from __future__ import annotations

import numpy as np

from dynbelief import MIN_PER_DAY
from dynbelief.beliefs.base import _Common

_DEFAULT_GAP = 240.0   # min: fallback mean inter-observation gap for lam scaling


class B25BetaBayes(_Common):
    name = "b25_betabayes"

    def __init__(self, obj_class_of: dict[int, str],
                 leave_prior: tuple[float, float] = (1.0, 3.0),
                 dest_alpha0: float = 0.5) -> None:
        # leave_prior Beta(a0,b0): weakly informative, leaning STAY (mean 0.25
        # leave per observed pair) -- an object at rest in a short window
        # usually stays. Data quickly dominates on well-observed edges.
        super().__init__()
        self.obj_class_of = obj_class_of
        self.a0, self.b0 = leave_prior       # Beta prior on leave probability
        self.dest_alpha0 = dest_alpha0       # symmetric Dirichlet prior
        # per (class, source): [leave_count, stay_count], and dest counts
        self._edge: dict[tuple[str, int], list[float]] | None = None
        self._dest: dict[tuple[str, int], dict[int, float]] | None = None
        self._gap: dict[str, float] | None = None
        self._occ_counts: dict[str, dict[int, int]] = {}   # class -> parent -> n (cold prior)

    def observe(self, t, obs) -> None:
        super().observe(t, obs)
        for obj, (parent, _s) in obs.items():
            cls = self.obj_class_of.get(obj, "?")
            self._occ_counts.setdefault(cls, {})
            self._occ_counts[cls][parent] = self._occ_counts[cls].get(parent, 0) + 1
        self._edge = None   # refit lazily

    def _fit(self) -> None:
        edge: dict[tuple[str, int], list[float]] = {}
        dest: dict[tuple[str, int], dict[int, float]] = {}
        gaps: dict[str, list[float]] = {}
        for obj, pairs in self.pair_stats.items():
            cls = self.obj_class_of.get(obj, "?")
            for (t1, p1, t2, p2) in pairs:
                key = (cls, p1)
                e = edge.setdefault(key, [0.0, 0.0])
                gaps.setdefault(cls, []).append(t2 - t1)
                if p1 != p2:
                    e[0] += 1.0
                    d = dest.setdefault(key, {})
                    d[p2] = d.get(p2, 0.0) + 1.0
                else:
                    e[1] += 1.0
        self._edge = edge
        self._dest = dest
        self._gap = {cls: (float(np.mean(g)) if g else _DEFAULT_GAP)
                     for cls, g in gaps.items()}

    def _occ_prior(self, cls: str) -> np.ndarray:
        v = np.ones(self.n_candidates)
        for parent, n in self._occ_counts.get(cls, {}).items():
            v[parent] += n
        return v / v.sum()

    def _dest_mean(self, cls: str, source: int) -> np.ndarray:
        """Dirichlet posterior mean over destinations != source; falls back to
        the class occupancy prior (renormalised off `source`) when unseen."""
        counts = (self._dest or {}).get((cls, source), {})
        v = np.zeros(self.n_candidates)
        seen_mass = 0.0
        for d, n in counts.items():
            v[d] += n
            seen_mass += n
        if seen_mass > 0:
            # symmetric Dirichlet smoothing over candidates that ever hosted cls
            support = [p for p in range(self.n_candidates)
                       if p != source and (self._occ_counts.get(cls, {}).get(p) or v[p] > 0)]
            for p in support:
                v[p] += self.dest_alpha0
            v[source] = 0.0
            if v.sum() > 0:
                return v / v.sum()
        # cold: occupancy prior with source removed
        prior = self._occ_prior(cls).copy()
        prior[source] = 0.0
        return prior / prior.sum() if prior.sum() > 0 else self.uniform()

    def predict(self, t: int) -> dict[int, np.ndarray]:
        if self._edge is None:
            self._fit()
        out: dict[int, np.ndarray] = {}
        for obj in self.objects:
            cls = self.obj_class_of.get(obj, "?")
            seen = self.last_seen.get(obj)
            if seen is None:
                out[obj] = self._occ_prior(cls)
                continue
            t_seen, source = seen
            a, b = self.a0, self.b0
            e = (self._edge or {}).get((cls, source))
            if e:
                a += e[0]   # leaves
                b += e[1]   # stays
            leave_prob = a / (a + b)                    # Beta posterior mean
            mean_gap = (self._gap or {}).get(cls, _DEFAULT_GAP) or _DEFAULT_GAP
            lam = leave_prob / mean_gap                 # per-minute leave rate
            elapsed = max(0, t - t_seen)
            w = float(np.exp(-lam * elapsed))
            out[obj] = w * self.onehot(source) + (1 - w) * self._dest_mean(cls, source)
        return out
