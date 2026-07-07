"""Unit tests for rooms.py."""
from __future__ import annotations

from dynamic_home_eqa.rooms import (
    CANONICAL_ROOMS,
    anchors_in_room,
    location_at,
    occupants_in_room,
    region_names_for_room,
    resolve_slot,
    rooms_match,
    slot_room,
    slot_type_for,
    unmapped_slots,
)


def test_canonical_rooms_is_the_eight_room_closed_set():
    assert set(CANONICAL_ROOMS) == {
        "kitchen", "dining_room", "living_room", "office", "bedroom",
        "bathroom", "laundry_room", "outdoor",
    }


def test_rooms_match_normalises_case_and_spacing():
    assert rooms_match("Living Room", "living_room")
    assert rooms_match("bedroom.001", "bedroom")


def test_rooms_match_uses_aliases():
    assert rooms_match("den", "office")
    assert rooms_match("patio", "outdoor")


def test_rooms_match_rejects_unrelated_rooms():
    assert not rooms_match("kitchen", "bedroom")


def test_slot_room_from_hand_authored_prefix():
    assert slot_room("dining.table_tucked") == "dining_room"
    assert slot_room("kitchen.counter") == "kitchen"
    assert slot_room("bedroom.nightstand") == "bedroom"


def test_slot_room_from_category_hint_for_synthesized_slots():
    assert slot_room("toilet.on") == "bathroom"
    assert slot_room("washer_dryer.on") == "laundry_room"


def test_slot_room_fuzzy_fallback_for_bare_region_names():
    assert slot_room("bathroom_1") == "bathroom"


def test_slot_room_none_for_empty_or_unresolvable():
    assert slot_room(None) is None
    assert slot_room("") is None
    assert slot_room("xyzzy_totally_unknown") is None


# ---------------------------------------------------------------------------
# slot_type_for / unmapped_slots (D1: kernel generalization)
# ---------------------------------------------------------------------------

def test_slot_type_for_pairs_category_with_resolved_room():
    assert slot_type_for("book", "dining.table_tucked") == ("book", "dining_room")
    assert slot_type_for("fridge", "kitchen.counter") == ("fridge", "kitchen")


def test_slot_type_for_none_when_room_unresolvable():
    assert slot_type_for("book", "xyzzy_totally_unknown") is None


def test_slot_type_for_is_deterministic_round_trip():
    # Same (category, anchor) input always resolves to the same slot type —
    # no hidden state, no dependence on call order.
    first = slot_type_for("book", "living_room.shelf")
    second = slot_type_for("book", "living_room.shelf")
    assert first == second == ("book", "living_room")


def test_unmapped_slots_returns_only_unresolvable_ones():
    slots = ["kitchen.counter", "xyzzy_totally_unknown", "bedroom.nightstand", "another_bad_one"]
    assert unmapped_slots(slots) == sorted(["xyzzy_totally_unknown", "another_bad_one"])


def test_unmapped_slots_empty_when_everything_resolves():
    assert unmapped_slots(["kitchen.counter", "dining.table_tucked", "bathroom_1"]) == []


def test_unmapped_slots_empty_for_empty_input():
    assert unmapped_slots([]) == []


def test_anchors_in_room_filters_by_room_and_real_inventory():
    room_inventory = {
        "kitchen": {"counter": 2, "cabinet": 3},
        "office": {"table": 1},
    }
    anchor_inventory = {"counter": 2, "cabinet": 3, "table": 1}
    assert anchors_in_room("kitchen", room_inventory, anchor_inventory) == ["cabinet", "counter"]
    assert anchors_in_room("office", room_inventory, anchor_inventory) == ["table"]


def test_anchors_in_room_falls_back_to_category_hint_when_room_inventory_empty():
    anchor_inventory = {"toilet": 1, "table": 2}
    result = anchors_in_room("bathroom", {}, anchor_inventory)
    assert result == ["toilet"]


def test_region_names_for_room_matches_real_hssd_names():
    room_inventory = {"bedroom.001": {"bed": 1}, "kitchen": {"counter": 1}}
    assert region_names_for_room("bedroom", room_inventory) == ["bedroom.001"]


def test_resolve_slot_disambiguates_by_room():
    assert resolve_slot("table", "on", room="office") == "office.desk"
    assert resolve_slot("table", "on", room="dining_room") == "dining.table"


def test_resolve_slot_in_region_returns_normalised_anchor():
    assert resolve_slot("Living Room", "in_region", room=None) == "living_room"


def test_resolve_slot_synthesizes_slot_for_unmapped_category_with_room():
    assert resolve_slot("sink", "on", room="bathroom") == "bathroom.sink"


def test_resolve_slot_never_crosses_into_a_different_room_than_requested():
    # "cabinet" IS in FURNITURE_TYPE_TO_SLOT (-> "kitchen.cabinet"), but no
    # SLOT_ANCHORS entry is authored for "outdoor" at all. The room-agnostic
    # fallback must not silently win here — a caller-given room always wins,
    # even via a synthesized slot, so slot_room() of the result agrees with
    # the room that was asked for.
    result = resolve_slot("cabinet", "on_top", room="outdoor")
    assert result == "outdoor.cabinet"
    assert slot_room(result) == "outdoor"


def test_resolve_slot_falls_back_without_room_context():
    # No room given: falls back to the room-agnostic first match (pre-existing
    # behavior), not a crash or an unresolved slot.
    assert resolve_slot("table", "on", room=None) == "dining.table"


_ACTIVITIES = [
    {"activity": "cooking", "location": "kitchen", "start": 7.0, "end": 9.0},
    {"activity": "working", "location": "office", "start": 9.0, "end": 17.0},
    {"activity": "sleeping", "location": "bedroom", "start": 22.0, "end": 6.5},
]


def test_location_at_finds_containing_window():
    assert location_at(_ACTIVITIES, 8.0) == "kitchen"
    assert location_at(_ACTIVITIES, 10.0) == "office"


def test_location_at_handles_overnight_wraparound():
    assert location_at(_ACTIVITIES, 23.0) == "bedroom"
    assert location_at(_ACTIVITIES, 2.0) == "bedroom"


def test_location_at_none_outside_any_window():
    assert location_at(_ACTIVITIES, 18.0) is None


def test_occupants_in_room_matches_by_exact_canonical_room():
    traces = [{"occupant_name": "Alex", "activities": _ACTIVITIES}]
    assert occupants_in_room(traces, "kitchen", 8.0) == ["Alex"]
    assert occupants_in_room(traces, "bedroom", 2.0) == ["Alex"]
    assert occupants_in_room(traces, "office", 8.0) == []


def test_occupants_in_room_none_room_returns_empty():
    traces = [{"occupant_name": "Alex", "activities": _ACTIVITIES}]
    assert occupants_in_room(traces, None, 8.0) == []
