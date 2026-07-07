"""
rooms.py — canonical room vocabulary, shared by generation and validation.

Three different room-name vocabularies exist in this codebase and none of
them agree by construction:
  1. Activity locations (generation/schemas.py's ACTIVITY_LOCATIONS) — a
     fixed 8-value enum plus "away", chosen by the activity-trace stage.
  2. Semantic slot prefixes (env/deltas.py's SLOT_ANCHORS keys) — dotted
     strings like "dining.table_tucked" whose prefix names a room, but only
     covers 5 of the 8 canonical rooms (no bathroom/laundry_room/outdoor
     slots are hand-authored).
  3. Real HSSD region names (generation/regions.py, per-scene) — arbitrary,
     e.g. "bedroom.001", "rec/game", "laundryroom/mudroom".

CANONICAL_ROOMS is the single closed vocabulary everything else maps onto.
generation/schemas.py builds ACTIVITY_LOCATIONS from it (CANONICAL_ROOMS +
"away") so the activity-trace enum and this module's room set can never
drift apart. slot_room() and anchors_in_room()/region_names_for_room() are
the two directions of the mapping: given a slot/anchor, which canonical room
is it in; given a canonical room, which real per-scene anchors/regions
count as "in" it.
"""
from __future__ import annotations

import re
from typing import Iterable, Optional

# ---------------------------------------------------------------------------
# The closed room vocabulary
# ---------------------------------------------------------------------------

CANONICAL_ROOMS: tuple[str, ...] = (
    "kitchen", "dining_room", "living_room", "office", "bedroom",
    "bathroom", "laundry_room", "outdoor",
)

# ---------------------------------------------------------------------------
# Room-name normalisation and fuzzy matching (moved from generation/regions.py
# so this module has no dependency on generation/ — regions.py imports these
# back, since HSSD region names are one of the vocabularies this reconciles).
# ---------------------------------------------------------------------------

_SUFFIX_RE = re.compile(r'\.\d+$')


def normalise_room_name(name: str) -> str:
    """Normalise a room/region name for comparison.

    Steps: lowercase, strip a trailing ".NNN" suffix (bedroom.001 ->
    bedroom), replace spaces/hyphens with underscores, strip whitespace.
    """
    name = name.lower().strip()
    name = _SUFFIX_RE.sub("", name)
    name = name.replace(" ", "_").replace("-", "_")
    return name


# Common name-vocabulary mismatches: LLM-proposed anchors vs. HSSD region
# labels, and HSSD region labels vs. objects.csv's `foundIn` tags. Not
# symmetric by construction — rooms_match() unions both directions.
_ALIASES: dict[str, list[str]] = {
    "living_room":   ["living room", "tv", "rec/game", "rec_game"],
    "laundry":       ["laundryroom", "laundryroom/mudroom"],
    "laundry_room":  ["laundryroom", "laundryroom/mudroom"],
    "tv_room":       ["tv", "living room", "rec/game"],
    "family_room":   ["living room", "tv", "rec/game"],
    "game_room":     ["rec/game", "rec_game"],
    "rec_room":      ["rec/game", "rec_game"],
    "mudroom":       ["laundryroom", "laundryroom/mudroom"],
    "utility_room":  ["laundryroom", "other room"],
    "study":         ["office"],
    "den":           ["office", "tv"],
    "entryway":      ["entryway", "hallway"],
    "foyer":         ["entryway", "hallway"],
    "outdoor":       ["patio", "garden", "balcony", "yard"],
    "patio":         ["outdoor", "balcony"],
    "garden":        ["outdoor", "yard"],
}


def rooms_match(a: str, b: str) -> bool:
    """True if two room/region-ish name strings plausibly refer to the same space."""
    na, nb = normalise_room_name(a), normalise_room_name(b)
    if na == nb:
        return True
    all_a = {na} | {normalise_room_name(x) for x in _ALIASES.get(na, [])}
    all_b = {nb} | {normalise_room_name(x) for x in _ALIASES.get(nb, [])}
    if all_a & all_b:
        return True
    return na in nb or nb in na


# ---------------------------------------------------------------------------
# Slot prefix -> canonical room (env/deltas.py's SLOT_ANCHORS vocabulary)
# ---------------------------------------------------------------------------

_SLOT_PREFIX_ROOM: dict[str, str] = {
    "dining":      "dining_room",
    "kitchen":     "kitchen",
    "living_room": "living_room",
    "office":      "office",
    "bedroom":     "bedroom",
}

# Furniture category -> canonical room, for categories whose room is fixed
# regardless of scene (a toilet is always in the bathroom). Deliberately
# excludes ambiguous categories (table, counter, cabinet, shelves, stand,
# chair, ...) that legitimately exist in more than one room — those need
# scene context (room_inventory) or the acting occupant's current activity
# location, not a category-level guess.
CATEGORY_ROOM_HINT: dict[str, str] = {
    "toilet":           "bathroom",
    "bathtub":          "bathroom",
    "shower":           "bathroom",
    "washer_dryer":     "laundry_room",
    "fridge":           "kitchen",
    "oven":             "kitchen",
    "dishwasher":       "kitchen",
    "microwave":        "kitchen",
    "range_hood":       "kitchen",
    "sink":             "kitchen",
    "bed":              "bedroom",
    "wardrobe":         "bedroom",
    "chest_of_drawers": "bedroom",
    "tv":               "living_room",
    "fireplace":        "living_room",
    "couch":            "living_room",
    "bench":            "living_room",
    "filing_cabinet":   "office",
}


def slot_room(slot: Optional[str]) -> Optional[str]:
    """Canonical room for a manifest slot string, or None if unresolvable.

    Tries, in order: the hand-authored slot-prefix table (env/deltas.py's
    SLOT_ANCHORS), the category-room hint table (for synthesized slots like
    "toilet.on" that aren't in SLOT_ANCHORS at all), then fuzzy matching the
    whole slot string against CANONICAL_ROOMS (covers bare region names used
    as in_region slots, e.g. "bathroom_1").
    """
    if not slot:
        return None
    prefix = slot.split(".", 1)[0]
    if prefix in _SLOT_PREFIX_ROOM:
        return _SLOT_PREFIX_ROOM[prefix]
    if prefix in CATEGORY_ROOM_HINT:
        return CATEGORY_ROOM_HINT[prefix]
    for room in CANONICAL_ROOMS:
        if rooms_match(slot, room):
            return room
    return None


def slot_type_for(category: str, anchor: str) -> Optional[tuple[str, str]]:
    """The semantic slot type (category, room) a per-scene anchor string
    belongs to — the cross-scene-portable key D1's hierarchical kernel
    backoff (posterior.shrink_hierarchical) pools statistics under,
    instead of the literal per-scene anchor string, which is otherwise
    disjoint between scenes (scene A's "kitchen.counter" and scene B's
    "kitchen.counter_tucked" are the same functional slot but never
    string-equal). None if the anchor's room can't be resolved (see
    slot_room) — an unmapped anchor, which unmapped_slots below exists to
    catch before it ever reaches belief-fitting time."""
    room = slot_room(anchor)
    return (category, room) if room is not None else None


def unmapped_slots(slots: Iterable[str]) -> list[str]:
    """Every slot in `slots` that slot_room can't resolve to a canonical
    room — the per-scene anchor-mapping check D1 requires to fail AT
    SCENE QUALIFICATION (see embodied.sampling.qualify_labels, which
    calls this alongside its existing reachability check), not silently
    at belief-fitting time, when an unmappable anchor would otherwise
    just be excluded from a kernel's room-pooling step without anyone
    noticing the scene's own anchor vocabulary has a gap."""
    return sorted({s for s in slots if slot_room(s) is None})


def anchors_in_room(
    room: str,
    room_inventory: Optional[dict[str, dict[str, int]]],
    anchor_inventory: Optional[dict[str, int]],
) -> list[str]:
    """Real furniture categories available in `room` for this scene.

    Intersects room_inventory's per-room category breakdown (real per-scene
    geometry, see generation/inventory.py's room_inventory_from_scene_state)
    with anchor_inventory (real anchor-capable furniture) so the result is
    always a subset of what actually exists in the scene. Falls back to
    CATEGORY_ROOM_HINT categories present anywhere in anchor_inventory when
    room_inventory has no matching room (geometry coverage gaps are
    documented, not universal) — this keeps schema construction from ever
    receiving an empty vocabulary for a room that plausibly has furniture.
    """
    anchor_inventory = anchor_inventory or {}
    cats: set[str] = set()
    for raw_room, room_cats in (room_inventory or {}).items():
        if rooms_match(raw_room, room):
            cats.update(room_cats.keys())
    cats &= set(anchor_inventory.keys())
    if not cats:
        cats = {
            cat for cat, hint in CATEGORY_ROOM_HINT.items()
            if hint == room and cat in anchor_inventory
        }
    return sorted(cats)


def region_names_for_room(
    room: str,
    room_inventory: Optional[dict[str, dict[str, int]]],
) -> list[str]:
    """Real per-scene HSSD region names (room_inventory keys) matching `room`."""
    return sorted(
        raw_room for raw_room in (room_inventory or {})
        if rooms_match(raw_room, room)
    )


# ---------------------------------------------------------------------------
# Anchor + room -> slot resolution (used by generation/manifest.py)
# ---------------------------------------------------------------------------

def resolve_slot(
    target_anchor: str,
    target_relationship: str,
    room: Optional[str] = None,
) -> str:
    """Map a (target_anchor, target_relationship) proposal to a semantic slot
    string, disambiguated by `room` when given.

    Several SLOT_ANCHORS entries share the same furniture category (e.g.
    "table" is the anchor for dining.table, living_room.open_floor,
    living_room.window_sill, office.desk, and bedroom.nightstand) — without
    room context, resolution defaults to whichever slot happens to be listed
    first, which silently collapses an office desk and a dining table onto
    the same slot string. When `room` is known (from the occupant's activity
    location at generation time), this picks the slot whose own room matches,
    so "table" in the office resolves to "office.desk", not "dining.table".

    When room is given but no hand-authored SLOT_ANCHORS entry exists for
    that (anchor, room) pair (e.g. no slot is authored for "outdoor" at
    all), this synthesizes a slot IN THAT ROOM ("{room}.{anchor}") rather
    than falling through to the room-agnostic FURNITURE_TYPE_TO_SLOT lookup
    — that lookup is keyed by anchor category alone and can resolve to a
    *different* room's slot (e.g. "cabinet" defaulting to "kitchen.cabinet"
    even when the occupant is outdoors), which would silently contradict
    the room the caller explicitly supplied. A caller-given room is a
    stronger, more specific signal than the anchor-only vocabulary and must
    win — every slot resolve_slot returns for a given room must itself
    resolve back to that same room via slot_room(), or downstream room-
    consistency checks (rooms.occupants_in_room, trace_validate's
    attendance check) would disagree with the very call that produced the
    slot in the first place.

    Falls back to the room-agnostic first-match (same as the pre-existing
    behavior) only when room is None, then to a synthesized "{anchor}.on"
    slot so every (anchor, relationship) pair still resolves to *some*
    stable string.
    """
    from .env.deltas import SLOT_ANCHORS, FURNITURE_TYPE_TO_SLOT

    anchor_norm = target_anchor.lower().strip().replace(" ", "_")

    if target_relationship == "in_region":
        return anchor_norm

    if room is not None:
        candidates = sorted(
            slot for slot, spec in SLOT_ANCHORS.items()
            if anchor_norm in spec.get("cats", []) and _SLOT_PREFIX_ROOM.get(slot.split(".", 1)[0]) == room
        )
        if candidates:
            return candidates[0]
        return f"{room}.{anchor_norm}"

    if anchor_norm in FURNITURE_TYPE_TO_SLOT:
        return FURNITURE_TYPE_TO_SLOT[anchor_norm]
    for ftype, slot in FURNITURE_TYPE_TO_SLOT.items():
        if ftype in anchor_norm or anchor_norm in ftype:
            return slot
    return f"{anchor_norm}.on"


# ---------------------------------------------------------------------------
# Occupant location lookup — shared by manifest.py (generation-time
# attendance enforcement) and trace_validate.py (independent re-derivation).
# ---------------------------------------------------------------------------

def location_at(activities: list[dict], t: float) -> Optional[str]:
    """The location of one occupant's activity trace at hour t, or None.

    Windows can wrap past midnight (end < start means overnight, e.g. sleep
    22.0-6.5) — t falls inside such a window if t >= start or t < end.
    """
    for act in activities:
        start, end = float(act["start"]), float(act["end"])
        if end < start:
            if t >= start or t < end:
                return act.get("location")
        else:
            if start <= t < end:
                return act.get("location")
    return None


def occupants_in_room(traces: list[dict], room: Optional[str], t: float) -> list[str]:
    """Names of occupants whose activity-trace location at t equals `room`.

    Activity locations are drawn from the same closed room vocabulary as
    `room` (CANONICAL_ROOMS / generation/schemas.py's ACTIVITY_LOCATIONS), so
    this is a direct equality check, not fuzzy matching — the fuzzy side
    (rooms_match / slot_room) already happened when the caller turned a
    semantic slot into `room`.
    """
    if room is None:
        return []
    return [
        trace.get("occupant_name", "")
        for trace in traces
        if location_at(trace.get("activities", []), t) == room
    ]
