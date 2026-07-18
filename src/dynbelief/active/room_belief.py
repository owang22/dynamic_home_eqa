"""Room-granularity belief reads + negative-evidence conditioning — the
"granularity lock" every policy shares.

The whole probe runs at ROOM granularity: the belief (natively over
receptacles) is marginalized to rooms at every read, and the reserved
elsewhere/absent receptacle mass maps to the single scene-invariant
ELSEWHERE option. Sensing is room-level presence. Nothing mixes receptacle-
level belief with room-level sensing.
"""
from __future__ import annotations

import numpy as np

from dynbelief import ELSEWHERE_ID
from dynbelief.eqa.answerer import _room_mass

ELSEWHERE = "elsewhere"


def sensable_rooms(world) -> list[str]:
    """The scene's room list C (sensable + answerable). ELSEWHERE is NOT
    here — it is answer-only (you cannot sense 'elsewhere')."""
    return sorted(world.rooms())


def room_belief(world, belief, obj: int, t_query: int) -> dict[str, float]:
    """Marginalize the tier's receptacle prediction to rooms ∪ {ELSEWHERE}.
    _room_mass already folds ELSEWHERE_ID and un-roomable receptacles into
    the 'elsewhere' key — exactly the reserved-mass → ELSEWHERE mapping the
    brief requires. Missing rooms get 0.0 so every C-room is present."""
    dist = belief.predict(t_query)[obj]
    mass = _room_mass(world, dist)
    out = {r: float(mass.get(r, 0.0)) for r in sensable_rooms(world)}
    out[ELSEWHERE] = float(mass.get(ELSEWHERE, 0.0))
    s = sum(out.values())
    if s > 0:
        for k in out:
            out[k] /= s
    return out


def condition_absent(p: dict[str, float], absent_rooms) -> dict[str, float]:
    """Hard negative evidence: zero the rooms sensed ABSENT and renormalize
    over the remaining rooms + ELSEWHERE. This is how EVERY tier consumes a
    negative sense result. It is applied on top of the tier's OWN predictive
    distribution, so the behaviour differs by tier for free: on b3 the base
    room mass is routine-weighted, so zeroing 'kitchen' and renormalizing
    yields 'given routine AND not kitchen, where now?' (routine-conditioned
    re-prediction, elsewhere-mass included); on b2 the base is decay-weighted,
    so the same op yields only decay-conditioned elimination."""
    q = {k: (0.0 if k in absent_rooms else v) for k, v in p.items()}
    s = sum(q.values())
    if s <= 0:  # everything sensed absent and no elsewhere mass — fall to ELSEWHERE
        q = {k: (1.0 if k == ELSEWHERE else 0.0) for k in p}
        return q
    return {k: v / s for k, v in q.items()}


def true_room_at(world, obj: int, t_query: int) -> str:
    """Ground-truth answer at t_query: the object's room, or ELSEWHERE if it
    is in no nameable/sensable room (ELSEWHERE_ID or un-roomable parent)."""
    parent = world.true_parent(obj, t_query)
    if parent == ELSEWHERE_ID:
        return ELSEWHERE
    return world.room_of(parent) or ELSEWHERE
