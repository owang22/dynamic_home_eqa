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
from typing import Dict, List, Tuple

from baselines.beliefs.base import BeliefModel
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
                 exclusion_floor: float = 0.0) -> None:
        super().__init__(rng, exclusion_floor=exclusion_floor)
        self._cfg = config

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
        object_class = self._context.object_classes.get(object_id)
        class_history = [
            (ot, r)
            for obj, h in self._history.items()
            if self._context.object_classes.get(obj) == object_class
            for ot, r in h]
        global_history = [(ot, r) for h in self._history.values()
                          for ot, r in h]
        object_counts = self._weighted_counts(history, t, half_life_s)
        class_counts = self._weighted_counts(class_history, t, half_life_s)
        global_counts = self._weighted_counts(global_history, t, half_life_s)
        if not global_counts:
            return self._uniform()
        lower = _shrink(_normalize(class_counts), _normalize(global_counts),
                        float(len(class_history)),
                        self._cfg.class_pseudocount)
        dist = _shrink(_normalize(object_counts), lower,
                       float(len(history)),
                       self._cfg.object_pseudocount)
        return self._normalized(dist, tie_break_recency=history)


def _normalize(counts: Dict[str, float]) -> Dict[str, float]:
    total = sum(counts.values())
    return {r: c / total for r, c in counts.items()} if total else {}


def _shrink(upper: Dict[str, float], lower: Dict[str, float],
            upper_count: float, pseudocount: float) -> Dict[str, float]:
    """Mix ``upper`` toward ``lower`` with weight N/(N + pseudocount)."""
    weight = upper_count / (upper_count + pseudocount)
    mixed = {r: weight * p for r, p in upper.items()}
    for r, p in lower.items():
        mixed[r] = mixed.get(r, 0.0) + (1.0 - weight) * p
    return mixed
