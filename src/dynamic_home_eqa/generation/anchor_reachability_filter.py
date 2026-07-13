"""
anchor_reachability_filter.py — Anchor Admission round (Version B):
soft, generation-time exclusion of navmesh-unreachable anchors from the
vocabulary the LLM/grounder/clutter stage ever get to see.

Pure (no habitat imports) — the reachability facts themselves come from
a precomputed env/anchor_admission.py cache, never a live sim call
here. This is the SOFT filter: it shrinks what generation offers, but
generation/manifest.py's build_manifest is the hard, authoritative
backstop that actually rejects a proposal that slips through anyway
(a stale/missing cache at generation time that gets refreshed later, or
the documented empty-room-list fallback in generation/stages.py).
Redundant by design, same "defense-in-depth against an upstream
guarantee silently failing" pattern manifest.py's own attendance check
already uses (see its module docstring).

Granularity note: anchor_inventory/room_inventory are {category: count}
dicts with no per-instance identity. rooms.resolve_slot(category,
relation, room, room_instance_categories) is already the exact
deterministic (category, room) -> slot collapse the admission cache is
keyed on (topdown_map.anchor_world_positions and resolve_slot's own
SLOT_ANCHORS/census fallback pick the same first-in-census-order
representative instance per resolved slot) — reusing it as a probe here
gives room-scoped precision (a category can stay offered in one room
even if the SAME category's instance in a different room is
unreachable) without inventing any new resolution logic.
"""
from __future__ import annotations

from typing import Optional

from ..env.anchor_admission import is_reachable
from ..rooms import CANONICAL_ROOMS, UnresolvableSlotError, resolve_slot, rooms_match


def _canonical_room(raw_room: str) -> str:
    """Best-effort canonical room for a raw room_inventory key (a real
    HSSD region name, not guaranteed to already equal a CANONICAL_ROOMS
    string — see rooms.py's own module docstring on the three room-name
    vocabularies). Falls back to the raw string unchanged if no
    canonical room fuzzy-matches; resolve_slot's own
    room_instance_categories lookup will then simply find nothing for
    that room, which is the correct "no data" outcome, not an error."""
    for room in CANONICAL_ROOMS:
        if rooms_match(raw_room, room):
            return room
    return raw_room


def _resolved_reachability(
    category: str, room: Optional[str], room_instance_categories: dict, admission_map: dict,
) -> Optional[bool]:
    """is_reachable(...) for the slot `category` resolves to in `room`,
    or None if resolve_slot itself can't back the (category, room) pair
    at all — that's the existing unbacked-anchor gate's job
    (generation/manifest.py's UnresolvableSlotError handling), not
    something this filter should duplicate or short-circuit."""
    try:
        slot = resolve_slot(category, "on", room=room, room_instance_categories=room_instance_categories)
    except UnresolvableSlotError:
        return None
    return is_reachable(admission_map, slot)


def prune_room_inventory_by_reachability(
    room_inventory: Optional[dict[str, dict[str, int]]],
    room_instance_categories: dict[str, set],
    admission_map: Optional[dict],
) -> Optional[dict[str, dict[str, int]]]:
    """Drop a (room, category) entry only when THAT room's resolved slot
    is known-unreachable (is_reachable(...) is False) — never for an
    unknown/unresolvable one, and never scene-wide. admission_map=None
    (no cache) is a no-op, returning room_inventory unchanged."""
    if admission_map is None or not room_inventory:
        return room_inventory
    pruned: dict[str, dict[str, int]] = {}
    for raw_room, cats in room_inventory.items():
        canonical = _canonical_room(raw_room)
        kept = {
            cat: n for cat, n in cats.items()
            if _resolved_reachability(cat, canonical, room_instance_categories, admission_map) is not False
        }
        if kept:
            pruned[raw_room] = kept
    return pruned


def prune_scene_wide_by_reachability(
    anchor_inventory: Optional[dict[str, int]],
    room_instance_categories: dict[str, set],
    admission_map: Optional[dict],
) -> Optional[dict[str, int]]:
    """Same idea at the room-blind granularity generate_clutter and
    ground_displacement_batch_semantic already operate at (room=None
    probes resolve_slot's scene-wide fallback path, which never raises
    UnresolvableSlotError — see resolve_slot's own room=None branch —
    so every category gets a real slot to check, possibly one absent
    from admission_map entirely, in which case is_reachable returns
    None and the category is correctly kept). admission_map=None is a
    no-op."""
    if admission_map is None or not anchor_inventory:
        return anchor_inventory
    return {
        cat: n for cat, n in anchor_inventory.items()
        if _resolved_reachability(cat, None, room_instance_categories, admission_map) is not False
    }
