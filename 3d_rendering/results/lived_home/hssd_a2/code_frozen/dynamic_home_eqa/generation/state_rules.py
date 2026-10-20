"""
state_rules.py — deterministic (non-LLM) state-change proposer for M3.

Mirrors the *role* of generation/stages.py's generate_displacements (propose
a change from an activity window) without its LLM call: replicating the
location-displacement stage's full sophistication for state (schema, prompt
engineering, grounding, multi-agent conflict verification) is its own
large undertaking, and that pipeline needed several rounds of real-trace-
audit bugfixing (see generation/manifest.py's module docstring) to reach
its current reliability. A rule-based proposer is cheap, deterministic,
and fully unit-testable; LLM-proposed state changes are a documented
future extension, not built here.

Trigger design: activity.location is a closed enum (rooms.CANONICAL_ROOMS,
via generation/schemas.py's ACTIVITY_LOCATIONS) and is the primary,
robust trigger — any activity located in a room proposes a bracketing
target-state pair for that room's stateful categories. activity (the
free-text label) is NOT a closed vocabulary, so matching against it is a
heuristic; the only label-substring trigger here is "tv" (matching
ACTIVITY_SCHEMA's own documented canonical example "tv_time") — an
acknowledged approximation, not a closed vocabulary, noted here rather
than hidden.

propose_state_changes returns *target* states at a picked time, not
from/to pairs — the same principle generation/manifest.py's build_manifest
already applies to location ("from_semantic always comes from tracked
state, never from the proposal's own belief"): two overlapping activities
(e.g. two occupants both in the kitchen) could otherwise propose
conflicting from/to pairs and break chain consistency. The caller
(generation/manifest.py's build_state_changes) threads these targets
against real tracked per-(label, variable) state in time order, emitting
an event only when the target actually differs from the current value —
chain-consistent and no-op-free by construction.
"""
from __future__ import annotations

from typing import Optional

from ..env.deltas import STATE_VARIABLES
from ..env.inventory import STATEFUL_FURNITURE
from .cache import make_seed

# Room -> stateful categories any activity located there plausibly triggers.
_ROOM_TRIGGERS: dict[str, tuple[str, ...]] = {
    "kitchen": ("oven", "fridge"),
    "bedroom": ("wardrobe",),
}

# Free-text activity-label substring -> stateful categories (see module
# docstring: the one heuristic on top of a non-closed vocabulary).
_LABEL_TRIGGERS: dict[str, tuple[str, ...]] = {
    "tv": ("tv",),
}


def propose_state_changes(
    activity: str,
    start: float,
    end: float,
    location: Optional[str],
    household_id: str,
    day: int,
    index: int,
) -> list[dict]:
    """One bracketing (on-value near window start, off-value near window
    end) proposal pair per stateful category this activity triggers.

    Returns proposal dicts: {_t, _location, object_category,
    state_variable, target_state, reason} — target_state only (see module
    docstring for why not from/to); _t is a deterministic jitter within
    [start, end] seeded the same way generation/manifest.py's _pick_time is.
    """
    categories: set[str] = set()
    if location in _ROOM_TRIGGERS:
        categories.update(_ROOM_TRIGGERS[location])
    lowered = activity.lower()
    for cat, substrings in _LABEL_TRIGGERS.items():
        if any(s in lowered for s in substrings):
            categories.add(cat)

    span = max(end - start, 1e-3)
    proposals: list[dict] = []
    for cat in sorted(categories):
        variable = STATEFUL_FURNITURE.get(cat)
        if variable is None:
            continue
        off_value, on_value = STATE_VARIABLES[variable]["values"]

        seed = make_seed(household_id, day, f"state_rules:{cat}:{index}")
        frac_on  = 0.05 + 0.10 * ((seed % 1000) / 1000.0)
        frac_off = 0.80 + 0.15 * (((seed // 1000) % 1000) / 1000.0)

        proposals.append({
            "_t": round(min(start + frac_on * span, end - 1e-3), 3),
            "_location": location, "object_category": cat, "state_variable": variable,
            "target_state": on_value, "reason": f"{activity} started",
        })
        proposals.append({
            "_t": round(min(start + frac_off * span, end - 1e-3), 3),
            "_location": location, "object_category": cat, "state_variable": variable,
            "target_state": off_value, "reason": f"{activity} ended",
        })
    return proposals
