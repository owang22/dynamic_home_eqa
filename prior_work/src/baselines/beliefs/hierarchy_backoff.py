"""Belief: sighting-frequency model with hierarchical backoff.

Object-level decayed sighting counts, backed off to the object's
inventory-class counts (pooled over every object sharing the class, from
the bank's ``object_classes`` metadata), backed off to the global counts
over all objects. The point of the hierarchy: a rarely-sighted object
borrows the placement statistics of its class ("mugs live near the sink")
and, failing that, of the household ("things pile up on the coffee
table") — including objects never sighted at all, which a purely
per-object frequency model can only answer uniformly.

Backoff weights are a fixed function of evidence counts — pseudo-count
shrinkage with a-priori constants, no tuning loops:

    p = w_o * P_object + (1 - w_o) * (w_c * P_class + (1 - w_c) * P_global)
    w_o = N_o / (N_o + object_pseudocount)
    w_c = N_c / (N_c + class_pseudocount)

where ``N_o`` / ``N_c`` are the RAW total object / class sighting counts
— backoff is gated by evidence volume, never by evidence freshness (the
level DISTRIBUTIONS use the frozen 24 h count half-life, but a
well-sighted object whose sightings are merely old must keep trusting
its own history rather than borrow the global histogram, which mostly
reflects where recently-sighted OTHER objects are). A level with zero
counts contributes nothing and its weight shifts down the hierarchy;
with no sightings anywhere the prediction is uniform. Times are seconds
since episode start.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from baselines.beliefs.base import (DEFAULT_FLOOR_MASS, BeliefModel,
                                    cold_start_distribution, shrink)
from baselines.types import Prediction


@dataclass(frozen=True)
class HierarchyBackoffConfig:
    """Fixed hyperparameters (no per-bank tuning)."""

    object_pseudocount: float = 5.0   # counts at which object evidence
    #                                   carries half the weight
    class_pseudocount: float = 5.0    # same, class vs global
    half_life_h: float = 24.0         # count decay half-life (frozen)

    def __post_init__(self) -> None:
        if self.object_pseudocount <= 0 or self.class_pseudocount <= 0:
            raise ValueError(
                f"HierarchyBackoffConfig: pseudocounts must be > 0, got "
                f"{self.object_pseudocount}/{self.class_pseudocount}")
        if self.half_life_h <= 0:
            raise ValueError(
                f"HierarchyBackoffConfig: half_life_h {self.half_life_h} "
                f"must be > 0")


class HierarchyBackoff(BeliefModel):
    """Object -> class -> global frequency backoff (see module docstring).

    Overrides ``_predict_for_object`` because it pools evidence across
    objects — a never-sighted object still gets its class/global
    distribution instead of the uniform fallback. Exclusions,
    renormalization, and the sighting-at-instant override stay in the
    base class. Argmax ties break by the object's own sighting recency
    (deterministic), then lexicographically.
    """

    def __init__(self, rng: random.Random, config: HierarchyBackoffConfig,
                 floor_mass: float = DEFAULT_FLOOR_MASS,
                 negative_half_life_h: Optional[float] = None) -> None:
        super().__init__(rng, floor_mass=floor_mass,
                         negative_half_life_h=negative_half_life_h)
        self._cfg = config

    def _default_negative_half_life_h(self) -> float:
        """The model's count half-life (frozen, panel-wide)."""
        return float(self._cfg.half_life_h)

    @property
    def name(self) -> str:
        return (f"HierarchyBackoff(po={self._cfg.object_pseudocount:g},"
                f"pc={self._cfg.class_pseudocount:g},"
                f"hl={self._cfg.half_life_h:g}h)")

    def _predict_for_object(self, object_id: str,
                            history: List[Tuple[int, str]],
                            t: int) -> Prediction:
        half_life_s = self._cfg.half_life_h * 3600
        assert self._context is not None   # predict() guarantees reset ran
        if not any(self._history.values()):
            return self._uniform()
        # Class -> global pooling is the shared cold-start arithmetic; the
        # object's own history is part of the pools, as before.
        tracked = {obj: (self._objects.get(obj), h)
                   for obj, h in self._history.items()}
        lower = cold_start_distribution(
            self._objects.get(object_id), tracked,
            self._context.receptacle_ids, t,
            half_life_h=self._cfg.half_life_h,
            class_pseudocount=self._cfg.class_pseudocount)
        object_counts = self._weighted_counts(history, t, half_life_s)
        total = sum(object_counts.values())
        dist = shrink({r: c / total for r, c in object_counts.items()}
                      if total else {}, lower,
                      float(len(history)), self._cfg.object_pseudocount)
        return self._normalized(dist, tie_break_recency=history)
