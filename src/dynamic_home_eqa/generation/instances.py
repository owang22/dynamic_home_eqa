"""
Per-event resolution of WHICH real Tier-2 instance a category-level proposal
moves — the fix for the single-teleporting-chair artifact.

Proposals are category-level ("chair next_to kitchen.counter_1"); scenes have
many real instances of a category (102344022 has 10 chairs). The old manifest
policy animated exactly ONE instance per category per day (sorted pool,
first), which produced one chair endlessly dragged across the whole house
while its nine siblings never moved. The realistic reading is the opposite:
an occupant uses the chair that is ALREADY IN THEIR ROOM.

pick_real_instance implements that: prefer the instance whose current tracked
slot resolves to the acting occupant's room (lowest index on ties, so
resolution is deterministic); when no instance of the category is in the
room, fall back to the lowest-index instance (someone fetches it — rare in
practice, since Phase 3 room-scopes each proposal's anchors to the occupant's
current room).

Per-label chain consistency is preserved: each label's from_semantic always
comes from that label's OWN tracked slot, whichever instance is picked. The
old one-instance rule existed to avoid per-(category, occupant) keying
breaking chains; room-lookup keying has no such failure mode.

Shared by build_manifest (the authoritative replay) and RunningState (the
prompt/judge-facing state), so both resolve the same instance for the same
(category, room, state) — the judge's per-instance move-history note counts
the same chair the manifest will actually move.
"""
from __future__ import annotations

from typing import Optional


def instance_room(slot: Optional[str]) -> Optional[str]:
    """Room of an instance's current slot string, via the canonical
    slot_room resolution with a dotted-prefix fallback (census-unified
    slots like 'dining_room.table_1.tucked' resolve by prefix)."""
    if not slot:
        return None
    from ..rooms import slot_room
    return slot_room(slot) or (slot.split(".")[0] if "." in slot else None)


def _instance_index(iid: str) -> int:
    try:
        return int(iid.rsplit("_", 1)[1])
    except (IndexError, ValueError):
        return 0


def instance_token_category(token: str) -> str:
    """Category of an instance token: "stool_2" -> "stool", "chair_10" ->
    "chair"; a bare category ("bowl", "potted_plant") passes through
    unchanged. Instance ids are always "<category>_<int>" (scene loader and
    clutter/spawn numbering both), so a trailing integer suffix is the
    complete test — no category list needed."""
    parts = token.rsplit("_", 1)
    return parts[0] if len(parts) == 2 and parts[1].isdigit() else token


def pick_real_instance(
    category: str,
    pool: list[str],
    current_slots: dict[str, Optional[str]],
    room: Optional[str],
) -> str:
    """The instance of `category` this proposal moves (see module docstring).

    Args:
        category:      proposal's object_category (caller guarantees pool
                       is this category's instance ids).
        pool:          real instance ids of the category (e.g. ["chair_1",
                       "chair_2", ...]); must be non-empty.
        current_slots: {instance_id: current slot string} tracked state
                       (build_manifest's current_slot / RunningState's
                       tier2_slots).
        room:          the acting occupant's current room (proposal's
                       _location), or None.
    """
    from ..rooms import rooms_match
    ordered = sorted(pool, key=_instance_index)
    if room:
        in_room = [
            iid for iid in ordered
            if (r := instance_room(current_slots.get(iid))) is not None and rooms_match(r, room)
        ]
        if in_room:
            return in_room[0]
    return ordered[0]
