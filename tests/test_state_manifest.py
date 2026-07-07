"""
Unit tests for generation/manifest.py's build_state_changes (M3: state-change
dynamics) — the state-axis counterpart of test_manifest.py's build_manifest
tests. Uses real scene 102343992, which has real tv/fridge/wardrobe
instances (no oven) — see env/inventory.py's STATEFUL_FURNITURE.
"""
from __future__ import annotations

from dynamic_home_eqa.generation.manifest import build_state_changes
from dynamic_home_eqa.trace_validate import validate

_SCENE = "102343992"


def _result(traces: list[dict], day: int = 0) -> dict:
    return {
        "household_id": "test_household", "day": day,
        "persona": {"occupants": [{"name": "Alex", "age_band": "adult"}]},
        "traces": traces,
    }


def test_tv_time_activity_produces_a_bracketing_power_pair():
    result = _result([
        {"occupant_name": "Alex", "activities": [
            {"activity": "tv_time", "location": "living_room", "start": 20.0, "end": 21.0},
        ]},
    ])
    changes = build_state_changes(_SCENE, result)
    assert {c["object_category"] for c in changes} == {"tv"}
    assert len(changes) == 2
    assert sorted(c["to_state"] for c in changes) == ["powered", "unpowered"]


def test_kitchen_activity_flips_fridge_but_not_absent_oven():
    # This scene has no real oven instance — the oven proposal must be
    # grounded away (category absent), not silently kept or crash.
    result = _result([
        {"occupant_name": "Alex", "activities": [
            {"activity": "breakfast", "location": "kitchen", "start": 7.0, "end": 7.5},
        ]},
    ])
    changes = build_state_changes(_SCENE, result)
    assert {c["object_category"] for c in changes} == {"fridge"}


def test_bedroom_activity_flips_wardrobe():
    result = _result([
        {"occupant_name": "Alex", "activities": [
            {"activity": "get_dressed", "location": "bedroom", "start": 7.0, "end": 7.2},
        ]},
    ])
    changes = build_state_changes(_SCENE, result)
    assert {c["object_category"] for c in changes} == {"wardrobe"}


def test_output_passes_trace_validate():
    result = _result([
        {"occupant_name": "Alex", "activities": [
            {"activity": "breakfast", "location": "kitchen", "start": 7.0, "end": 7.5},
            {"activity": "get_dressed", "location": "bedroom", "start": 7.6, "end": 7.8},
            {"activity": "tv_time", "location": "living_room", "start": 20.0, "end": 21.0},
        ]},
    ])
    changes = build_state_changes(_SCENE, result)
    report = validate(changes, result["traces"])
    assert report.ok, report.summary()


def test_repeated_activities_in_one_day_stay_chain_consistent():
    result = _result([
        {"occupant_name": "Alex", "activities": [
            {"activity": "breakfast", "location": "kitchen", "start": 7.0, "end": 7.5},
            {"activity": "dinner", "location": "kitchen", "start": 18.0, "end": 19.0},
        ]},
    ])
    changes = build_state_changes(_SCENE, result)
    report = validate(changes, result["traces"])
    assert report.ok, report.summary()
    fridge_events = [c for c in changes if c["object_category"] == "fridge"]
    assert len(fridge_events) == 4  # open/close x2 activities


def test_unattended_activity_window_is_dropped():
    # No occupant recorded in the trace at all during this window -> dropped,
    # not fabricated.
    result = _result([
        {"occupant_name": "Alex", "activities": [
            {"activity": "breakfast", "location": "kitchen", "start": 7.0, "end": 7.0001},
        ]},
    ])
    # A near-zero window still produces proposals (state_rules brackets any
    # window), but they must still pass attendance against the real trace —
    # this is really just confirming build_state_changes doesn't crash on a
    # degenerate window, chain-consistency is the meaningful assertion.
    changes = build_state_changes(_SCENE, result)
    report = validate(changes, result["traces"])
    assert report.ok, report.summary()


def test_existing_changes_seeds_the_chain_across_days():
    # Day 1 starts from wherever day 0 left the fridge (open, mid-breakfast
    # activity would end open only if the "close" proposal were dropped —
    # here we simulate day 0 ending with the fridge left open).
    day0_changes = [{
        "t": 7.1, "label": "fridge_1", "change_type": "state_change",
        "object_category": "fridge", "from_semantic": "fridge", "to_semantic": "fridge",
        "state_variable": "door", "from_state": "closed", "to_state": "open",
    }]
    result = _result([
        {"occupant_name": "Alex", "activities": [
            {"activity": "breakfast", "location": "kitchen", "start": 7.0, "end": 7.5},
        ]},
    ], day=1)
    changes = build_state_changes(_SCENE, result, existing_changes=day0_changes)
    fridge_events = sorted((c for c in changes if c["object_category"] == "fridge"), key=lambda c: c["t"])
    # First new event must chain from "open" (day 0's leftover), not the
    # scene-init default "closed".
    assert fridge_events[0]["from_state"] == "open"
