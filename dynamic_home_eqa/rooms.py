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

# Realizable-Anchor Vocabulary round (Part A): a census instance label —
# "<room>.<category>_<N>" (kitchen.counter_2, bedroom_1.bed_1,
# rec/game.toilet_1). The room part may itself carry a _N dedup suffix
# and/or a "/" (real HSSD region names); the final "_<digits>" after the
# dot is what distinguishes this from every legacy slot string
# (dining.table_tucked ends in letters, bare categories have no dot).
CENSUS_LABEL_RE = re.compile(r'^[a-z0-9_/]+\.[a-z_]+_\d+$')
_TRAILING_INDEX_RE = re.compile(r'_\d+$')


def census_label_parts(label: str) -> Optional[tuple[str, str]]:
    """(room, category) for a census instance label, or None if `label`
    isn't one. "bedroom_2.bed_1" -> ("bedroom_2", "bed");
    "kitchen.counter_3" -> ("kitchen", "counter")."""
    if not CENSUS_LABEL_RE.match(label):
        return None
    room, rest = label.split(".", 1)
    return room, _TRAILING_INDEX_RE.sub("", rest)


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
    "toilet.on" that aren't in SLOT_ANCHORS at all), the slot's own room
    prefix stripped of a census _N dedup suffix (Part A census labels —
    "bedroom_2.bed_1" -> bedroom, "laundryroom.cabinet_1" -> laundry_room
    via the same rooms_match aliasing everything else uses; a census label
    whose room is genuinely non-canonical — garage, closet — resolves to
    None, correctly: such anchors are never offered by the room-scoped
    vocabulary in the first place, since activity locations are canonical),
    then fuzzy matching the whole slot string against CANONICAL_ROOMS
    (covers bare region names used as in_region slots, e.g. "bathroom_1").
    """
    if not slot:
        return None
    prefix = slot.split(".", 1)[0]
    if prefix in _SLOT_PREFIX_ROOM:
        return _SLOT_PREFIX_ROOM[prefix]
    if prefix in CATEGORY_ROOM_HINT:
        return CATEGORY_ROOM_HINT[prefix]
    prefix_base = _TRAILING_INDEX_RE.sub("", prefix)
    for room in CANONICAL_ROOMS:
        if rooms_match(prefix_base, room):
            return room
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

class UnresolvableSlotError(ValueError):
    """resolve_slot() cannot back `target_anchor` with any real instance —
    per the Realized World Phase's admission rule, this is now a REJECTION
    at generation time, not a guess. Raised only from the room-qualified,
    non-STATEFUL_FURNITURE, no-SLOT_ANCHORS-match path (see resolve_slot's
    docstring) — every other branch still always returns a string."""


def resolve_slot(
    target_anchor: str,
    target_relationship: str,
    room: Optional[str] = None,
    room_instance_categories: Optional[dict[str, set[str]]] = None,
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

    `room_instance_categories`: {room: {category, ...}} — which categories
    have at least one REAL instance in each room, per the scene's actual
    furniture census (topdown_map.instance_room_positions; a caller
    resolving many events for one scene should compute this ONCE and pass
    it in, not per call — see generation/manifest.py). This is the
    When room is given but no
    hand-authored SLOT_ANCHORS entry exists for that (anchor, room) pair,
    resolve_slot used to blindly SYNTHESIZE "{room}.{anchor}" — a string
    that looks like a real dotted slot and passes slot_room()'s own room
    resolution fine, but had never been checked against anything. That
    string was frequently wrong in a confirmed, concrete way ("kitchen.table"
    when the real hand-authored slot is "dining.table", "living_room.bed"
    naming a bed that doesn't exist in that room) — not because the LLM's
    underlying (category, room) pick was ungrounded (generation/stages.py's
    JSON-schema enum already constrains it to real per-scene categories),
    but because SLOT_ANCHORS' 16 hand-authored (room, category) pairs
    predate the full real census and resolve_slot never checked the
    fallback string it invented against anything past that point.

    Now: the fallback resolves against `room_instance_categories` — the
    SAME real per-scene, per-room furniture census the LLM's own proposal
    was grounded against (env/inventory.py's anchor_inventory, extended
    with real room tags) — not the 16-entry legacy table. A real matching
    instance in that room -> the slot resolves (still "{room}.{anchor}",
    now verified rather than assumed). No real instance in that room ->
    UnresolvableSlotError: the proposal must be rejected/re-proposed at
    generation time (see generation/manifest.py's ANCHOR_UNRESOLVABLE
    stat), not silently accepted with a name nothing backs. Region
    proposals (target_relationship == "in_region") are unaffected — those
    were never furniture-instance claims.

    SLOT_ANCHORS survives unchanged as the first-checked table (its 16
    entries — dining.table, office.desk, etc. — are real, hand-verified,
    and predate this fix; nothing about them was wrong) and, separately,
    as the resolution path for every region-style anchor (living_room.corner,
    living_room.open_floor, kitchen.counter_tucked — their "offset":
    "floor_near"/"current" entries describe a floor area near typical
    furniture, not a strict single-instance claim, so they are not
    subject to the census check here at all — see
    scripts/build_realized_day.py's classify_anchor for where that
    region/instance split is actually enforced downstream).

    room_instance_categories=None (the parameter's own default) is a
    caller error for any anchor that would reach the fallback branch —
    not a silent permission to revert to blind synthesis. Every real
    caller must pass real census data; tests inject a synthetic dict
    instead of loading a real scene, which is exactly what the parameter
    is for.

    Falls back to the room-agnostic first-match only when room is None,
    then to a synthesized "{anchor}.on" slot — that path is used by
    clutter placement (generation/manifest.py's room-agnostic call), a
    separate proposal class.
    """
    from .env.deltas import SLOT_ANCHORS, FURNITURE_TYPE_TO_SLOT
    from .env.inventory import STATEFUL_FURNITURE

    anchor_norm = target_anchor.lower().strip().replace(" ", "_")

    # Realizable-Anchor Vocabulary round (Part A): a census instance label
    # ("bedroom_2.bed_1", "kitchen.counter_3") IS the slot — it already
    # names one specific real furniture instance, room-qualified, drawn
    # from a guided-decoding enum built from the anchor census
    # (env/anchor_census.py), so there is nothing left to resolve or
    # verify here. Membership/realizability enforcement lives where the
    # data is: the schema (can only emit census labels), semantic
    # grounding (census-membership check), and the builder (census
    # lookup; a miss is a loud anchor_unbacked, never a guess). No legacy
    # slot string matches CENSUS_LABEL_RE (see its definition), so this
    # cannot shadow any existing resolution path.
    if CENSUS_LABEL_RE.match(anchor_norm):
        return anchor_norm

    if target_relationship == "in_region":
        return anchor_norm

    if room is not None:
        candidates = sorted(
            slot for slot, spec in SLOT_ANCHORS.items()
            if anchor_norm in spec.get("cats", []) and _SLOT_PREFIX_ROOM.get(slot.split(".", 1)[0]) == room
        )
        if candidates:
            return candidates[0]
        # anchor_norm itself may already be independently resolvable —
        # STATEFUL_FURNITURE categories (wardrobe, fridge, oven, tv) are
        # registered under their own bare category name (see
        # topdown_map.anchor_world_positions), never under a room-qualified
        # dotted slot — see the module-level bug this fixed, documented in
        # results/reports/human_realism_study.md.
        if anchor_norm in STATEFUL_FURNITURE:
            return anchor_norm

        available = (room_instance_categories or {}).get(room, set())
        if anchor_norm in available:
            return f"{room}.{anchor_norm}"
        raise UnresolvableSlotError(
            f"no real {anchor_norm!r} instance found in room {room!r} "
            f"(target_relationship={target_relationship!r}) — refusing to synthesize an unbacked slot"
        )

    if anchor_norm in STATEFUL_FURNITURE:
        return anchor_norm

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
