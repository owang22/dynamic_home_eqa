"""
Tests for env/deltas.py's STATE_VARIABLES naming-collision lint (M3).

rooms.resolve_slot()'s fallback synthesizes f"{anchor}.on" as a *location*
slot when no other resolution applies (rooms.py). A state value literally
named "on"/"off" would be ambiguous with that synthesized location-slot
suffix — this is a real lint against the actual vocabulary in use, not
just a docstring promise.
"""
from __future__ import annotations

from dynamic_home_eqa.env.deltas import (
    FURNITURE_TYPE_TO_SLOT,
    SLOT_ANCHORS,
    STATE_VARIABLES,
)

_FORBIDDEN_BARE_VALUES = {"on", "off"}


def _slot_suffixes() -> set[str]:
    return {slot.split(".", 1)[1] for slot in SLOT_ANCHORS if "." in slot}


def test_no_state_value_is_bare_on_or_off():
    for variable, spec in STATE_VARIABLES.items():
        for value in spec["values"]:
            assert value not in _FORBIDDEN_BARE_VALUES, (
                f"STATE_VARIABLES[{variable!r}] uses forbidden bare value {value!r} — "
                "collides with rooms.resolve_slot()'s f'{anchor}.on' fallback"
            )


def test_no_state_value_collides_with_a_slot_anchor_suffix():
    suffixes = _slot_suffixes()
    for variable, spec in STATE_VARIABLES.items():
        for value in spec["values"]:
            assert value not in suffixes, (
                f"STATE_VARIABLES[{variable!r}] value {value!r} collides with a "
                f"SLOT_ANCHORS suffix {suffixes}"
            )


def test_no_state_value_collides_with_a_furniture_type_slot_value():
    slot_values = set(FURNITURE_TYPE_TO_SLOT.values())
    for variable, spec in STATE_VARIABLES.items():
        for value in spec["values"]:
            assert value not in slot_values, (
                f"STATE_VARIABLES[{variable!r}] value {value!r} collides with a "
                "FURNITURE_TYPE_TO_SLOT value"
            )


def test_state_variable_values_are_a_two_tuple():
    # propose_state_changes / grounding assume (off_value, on_value) order.
    for variable, spec in STATE_VARIABLES.items():
        assert len(spec["values"]) == 2, f"{variable!r} must have exactly 2 legal values"


def test_no_category_has_two_state_variables():
    # v1 assumption (env/inventory.py's STATEFUL_FURNITURE is category -> ONE
    # variable) — if this ever fires, that mapping needs to become
    # category -> list[variable] instead of silently overwriting one.
    seen: dict[str, str] = {}
    for variable, spec in STATE_VARIABLES.items():
        for cat in spec["cats"]:
            assert cat not in seen, f"category {cat!r} already claimed by variable {seen[cat]!r}"
            seen[cat] = variable
