"""Unit tests for trace_validate.py."""
from __future__ import annotations

import json
import pathlib

import pytest

from dynamic_home_eqa.trace_validate import (
    FindingKind,
    Severity,
    validate,
)

_FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> tuple[dict, dict]:
    manifest = json.loads((_FIXTURES / f"{name}_manifest.json").read_text())
    result   = json.loads((_FIXTURES / f"{name}_generation_result.json").read_text())
    return manifest, result


# ---------------------------------------------------------------------------
# Before-picture: the frozen, known-broken trace this whole phase exists to fix.
# Pins the validator's behavior against a real generated trace with known
# hard-invariant violation counts (17 chain breaks / 90 re-inserts / 61
# no-ops, found by an earlier manual audit of this exact scene/seed/day).
# ---------------------------------------------------------------------------

def test_frozen_pre_fix_trace_has_known_violation_counts():
    manifest, result = _load_fixture("102343992_family_with_kids")
    report = validate(manifest["changes"], result["traces"])

    assert report.n_events == 201
    assert report.chain_breaks == 17
    assert report.re_inserts == 90
    assert report.no_ops == 61
    assert report.unattended == 53
    assert not report.ok


# ---------------------------------------------------------------------------
# Unit tests for each invariant in isolation, on synthetic minimal input.
# ---------------------------------------------------------------------------

_TRACES = [
    {
        "occupant_name": "Alex",
        "activities": [
            {"activity": "cooking", "location": "kitchen", "start": 7.0, "end": 9.0},
            {"activity": "working", "location": "office", "start": 9.0, "end": 17.0},
            {"activity": "sleeping", "location": "bedroom", "start": 22.0, "end": 6.5},
        ],
    },
]


def test_chain_consistency_passes_when_from_matches_prior_to():
    changes = [
        {"t": 7.0, "label": "book_1", "change_type": "insert_new",
         "object_category": "book", "from_semantic": None, "to_semantic": "kitchen.counter"},
        {"t": 9.0, "label": "book_1", "change_type": "move_existing",
         "object_category": "book", "from_semantic": "kitchen.counter", "to_semantic": "office.desk"},
    ]
    report = validate(changes, _TRACES)
    assert report.chain_breaks == 0


def test_chain_break_detected_when_from_disagrees_with_prior_to():
    changes = [
        {"t": 7.0, "label": "book_1", "change_type": "insert_new",
         "object_category": "book", "from_semantic": None, "to_semantic": "kitchen.counter"},
        {"t": 9.0, "label": "book_1", "change_type": "move_existing",
         "object_category": "book", "from_semantic": "living_room.shelf", "to_semantic": "office.desk"},
    ]
    report = validate(changes, _TRACES)
    assert report.chain_breaks == 1
    assert report.findings[0].kind == FindingKind.CHAIN_BREAK
    assert report.findings[0].severity == Severity.HARD


def test_insert_once_passes_with_single_insert():
    changes = [
        {"t": 7.0, "label": "book_1", "change_type": "insert_new",
         "object_category": "book", "from_semantic": None, "to_semantic": "kitchen.counter"},
        {"t": 9.0, "label": "book_1", "change_type": "move_existing",
         "object_category": "book", "from_semantic": "kitchen.counter", "to_semantic": "office.desk"},
    ]
    report = validate(changes, _TRACES)
    assert report.re_inserts == 0


def test_re_insert_detected_on_second_insert_new():
    changes = [
        {"t": 7.0, "label": "book_1", "change_type": "insert_new",
         "object_category": "book", "from_semantic": None, "to_semantic": "kitchen.counter"},
        {"t": 9.0, "label": "book_1", "change_type": "insert_new",
         "object_category": "book", "from_semantic": None, "to_semantic": "office.desk"},
    ]
    report = validate(changes, _TRACES)
    assert report.re_inserts == 1
    assert any(f.kind == FindingKind.RE_INSERT for f in report.findings)


def test_no_op_detected_when_from_equals_to():
    changes = [
        {"t": 9.0, "label": "book_1", "change_type": "move_existing",
         "object_category": "book", "from_semantic": "office.desk", "to_semantic": "office.desk"},
    ]
    report = validate(changes, _TRACES)
    assert report.no_ops == 1


def test_insert_new_with_null_from_is_not_a_no_op():
    changes = [
        {"t": 7.0, "label": "book_1", "change_type": "insert_new",
         "object_category": "book", "from_semantic": None, "to_semantic": "kitchen.counter"},
    ]
    report = validate(changes, _TRACES)
    assert report.no_ops == 0


def test_attendance_passes_when_occupant_present_in_destination_room():
    changes = [
        {"t": 8.0, "label": "book_1", "change_type": "insert_new",
         "object_category": "book", "from_semantic": None, "to_semantic": "kitchen.counter"},
    ]
    report = validate(changes, _TRACES)
    assert report.unattended == 0


def test_attendance_passes_when_occupant_present_in_source_room_only():
    # Alex is in the office (9-17h) but not the kitchen at t=10 — the event's
    # *source* room (kitchen) still has no one there either in this trace,
    # so this should actually be unattended; verifies source-room checking by
    # using a case where source room does have the occupant instead.
    changes = [
        {"t": 10.0, "label": "book_1", "change_type": "move_existing",
         "object_category": "book", "from_semantic": "office.desk", "to_semantic": "kitchen.counter"},
    ]
    report = validate(changes, _TRACES)
    assert report.unattended == 0  # source room (office) has Alex at t=10


def test_unattended_detected_when_no_occupant_in_either_room():
    changes = [
        {"t": 12.0, "label": "book_1", "change_type": "move_existing",
         "object_category": "book", "from_semantic": "living_room.shelf", "to_semantic": "bedroom.nightstand"},
    ]
    # Alex is in the office at t=12; neither living_room nor bedroom match.
    report = validate(changes, _TRACES)
    assert report.unattended == 1
    assert report.findings[0].kind == FindingKind.UNATTENDED


def test_overnight_wraparound_location_is_resolved_correctly():
    # Sleeping window is 22.0-6.5 (wraps past midnight); t=2.0 should resolve
    # to "bedroom", not None.
    changes = [
        {"t": 2.0, "label": "book_1", "change_type": "move_existing",
         "object_category": "book", "from_semantic": "living_room.shelf", "to_semantic": "bedroom.nightstand"},
    ]
    report = validate(changes, _TRACES)
    assert report.unattended == 0


def test_empty_changes_is_trivially_ok():
    report = validate([], _TRACES)
    assert report.ok
    assert report.n_events == 0


# ---------------------------------------------------------------------------
# state_change branch (M3: state-change dynamics)
# ---------------------------------------------------------------------------

def _state_change(t, from_state, to_state, label="oven_1", variable="power"):
    return {
        "t": t, "label": label, "change_type": "state_change",
        "object_category": "oven", "from_semantic": "oven", "to_semantic": "oven",
        "state_variable": variable, "from_state": from_state, "to_state": to_state,
    }


def test_state_chain_consistency_passes_when_from_matches_prior_to():
    changes = [
        _state_change(7.5, "unpowered", "powered"),
        _state_change(8.5, "powered", "unpowered"),
    ]
    report = validate(changes, _TRACES)
    assert report.chain_breaks == 0


def test_state_chain_break_detected_when_from_disagrees_with_prior_to():
    changes = [
        _state_change(7.5, "unpowered", "powered"),
        _state_change(8.5, "unpowered", "powered"),  # should chain from "powered", not "unpowered"
    ]
    report = validate(changes, _TRACES)
    assert report.chain_breaks == 1


def test_state_no_op_detected_when_from_state_equals_to_state():
    changes = [_state_change(7.5, "unpowered", "unpowered")]
    report = validate(changes, _TRACES)
    assert report.no_ops == 1


def test_state_change_is_not_a_location_no_op_despite_equal_semantics():
    # from_semantic == to_semantic == "oven" is EXPECTED for a state_change
    # event (the furniture never moves) — must not be flagged as a location no-op.
    changes = [_state_change(7.5, "unpowered", "powered")]
    report = validate(changes, _TRACES)
    assert report.no_ops == 0


def test_state_chain_is_independent_per_variable():
    # oven_1's "power" and "door" (hypothetically) chains must not cross-check.
    changes = [
        _state_change(7.5, "unpowered", "powered", variable="power"),
        _state_change(7.6, "closed", "open", variable="door"),
    ]
    report = validate(changes, _TRACES)
    assert report.chain_breaks == 0


def test_state_attendance_uses_the_furnitures_fixed_room():
    # oven -> kitchen via CATEGORY_ROOM_HINT; Alex is in kitchen 7.0-9.0.
    changes = [_state_change(7.5, "unpowered", "powered")]
    report = validate(changes, _TRACES)
    assert report.unattended == 0


def test_state_unattended_detected_when_no_occupant_present():
    # 12.0 falls in no activity window for Alex (9-17 is "office", not kitchen).
    changes = [_state_change(12.0, "unpowered", "powered")]
    report = validate(changes, _TRACES)
    assert report.unattended == 1


# ---------------------------------------------------------------------------
# Report.validation_hash() (Suite Buildout phase A: contamination audit)
# ---------------------------------------------------------------------------

def test_validation_hash_is_deterministic_for_identical_reports():
    changes = [
        {"t": 7.0, "label": "book_1", "change_type": "insert_new",
         "object_category": "book", "from_semantic": None, "to_semantic": "kitchen.counter"},
    ]
    r1 = validate(changes, _TRACES)
    r2 = validate(changes, _TRACES)
    assert r1.validation_hash() == r2.validation_hash()


def test_validation_hash_differs_for_ok_vs_failing_reports():
    ok_changes = [
        {"t": 7.0, "label": "book_1", "change_type": "insert_new",
         "object_category": "book", "from_semantic": None, "to_semantic": "kitchen.counter"},
    ]
    bad_changes = [
        {"t": 9.0, "label": "book_1", "change_type": "move_existing",
         "object_category": "book", "from_semantic": "office.desk", "to_semantic": "office.desk"},
    ]
    ok_report = validate(ok_changes, _TRACES)
    bad_report = validate(bad_changes, _TRACES)
    assert ok_report.validation_hash() != bad_report.validation_hash()


def test_validation_hash_differs_when_violation_counts_differ():
    one_violation = validate(
        [{"t": 9.0, "label": "a", "change_type": "move_existing",
          "object_category": "book", "from_semantic": "x", "to_semantic": "x"}],
        _TRACES,
    )
    two_violations = validate(
        [
            {"t": 9.0, "label": "a", "change_type": "move_existing",
             "object_category": "book", "from_semantic": "x", "to_semantic": "x"},
            {"t": 9.0, "label": "b", "change_type": "move_existing",
             "object_category": "book", "from_semantic": "y", "to_semantic": "y"},
        ],
        _TRACES,
    )
    assert one_violation.validation_hash() != two_violations.validation_hash()
