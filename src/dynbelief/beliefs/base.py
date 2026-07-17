"""Stage 0.5 — belief-model protocol and shared plumbing.

A belief model consumes observations and, for any query time, returns each
object's probability distribution over candidate receptacles.

Candidate axis: a distribution is a length-(R+1) numpy vector indexed
directly by receptacle id (the registry guarantees contiguous ids with
ELSEWHERE at index 0). The candidate set is the FULL receptacle vocabulary
plus elsewhere/absent — never a per-object shortlist, and no tree/fixed-
furniture assumption: movable receptacles are simply objects that also
appear in the receptacle vocabulary, each with its own parent belief.

reset() contract (drives the Stage-1 displacement probe): clears the
per-day filtering state (last observations, edge posteriors) but KEEPS any
routine parameters learned from earlier observation feeds. A fully fresh
model is a new instance.
"""
from __future__ import annotations

import math
from typing import Protocol

import numpy as np


class BeliefModel(Protocol):
    def reset(self, objects: list[int], receptacles: list[int], t0: int) -> None: ...

    def observe(self, t: int, obs: dict[int, tuple[int, dict]]) -> None: ...

    def predict(self, t: int) -> dict[int, np.ndarray]: ...

    def entropy(self, t: int) -> dict[int, float]: ...


def shannon(p: np.ndarray) -> float:
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1.0)
    p = p / p.sum()
    return float(-(p * np.log(p)).sum())


class _Common:
    """Bookkeeping shared by every tier: candidate axis, per-object last
    observation, pairwise sufficient statistics for rate estimation, and
    the entropy() default. Subclasses implement predict()."""

    def __init__(self) -> None:
        self.n_candidates = 0
        self.objects: list[int] = []
        self.t0 = 0
        self.last_seen: dict[int, tuple[int, int]] = {}   # obj -> (t, parent)
        # rate-estimation stats survive reset() (learned routine knowledge):
        # per object: previous (t, parent) across ALL feeds ever seen
        self._prev_obs: dict[int, tuple[int, int]] = {}
        self.pair_stats: dict[int, list[tuple[int, int, int, int]]] = {}
        # obj -> [(t1, p1, t2, p2)] consecutive observation pairs

    def reset(self, objects: list[int], receptacles: list[int], t0: int) -> None:
        self.objects = list(objects)
        self.n_candidates = max(receptacles) + 1
        self.t0 = t0
        self.last_seen = {}
        self._prev_obs = {}

    def observe(self, t: int, obs: dict[int, tuple[int, dict]]) -> None:
        from dynbelief import MIN_PER_DAY
        for obj, (parent, _states) in obs.items():
            prev = self._prev_obs.get(obj)
            if prev is not None and t > prev[0]:
                # Pairs that span a day boundary are excluded from the rate
                # statistics: this generator's days are independent, and the
                # logger's explicit midnight reset events are bookkeeping,
                # not organic motion — counting them as moves inflated every
                # leave-hazard (measured: b3 decayed off a fresh observation
                # hours early and flipped to the historical mode, losing to
                # b0 on the Stage-1 probe).
                if prev[0] // MIN_PER_DAY == t // MIN_PER_DAY:
                    self.pair_stats.setdefault(obj, []).append((prev[0], prev[1], t, parent))
            self._prev_obs[obj] = (t, parent)
            self.last_seen[obj] = (t, parent)

    def uniform(self) -> np.ndarray:
        return np.full(self.n_candidates, 1.0 / self.n_candidates)

    def onehot(self, parent: int) -> np.ndarray:
        v = np.zeros(self.n_candidates)
        v[parent] = 1.0
        return v

    def entropy(self, t: int) -> dict[int, float]:
        return {o: shannon(p) for o, p in self.predict(t).items()}

    # subclasses provide
    def predict(self, t: int) -> dict[int, np.ndarray]:  # pragma: no cover
        raise NotImplementedError


def object_class(label: str) -> str:
    """Instance label -> class: "bowl_3" -> "bowl", "ana_phone" -> "phone"
    (owner-prefixed Tier-3 labels classify by their trailing category)."""
    parts = label.rsplit("_", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0]
    return parts[-1] if len(parts) == 2 else label
