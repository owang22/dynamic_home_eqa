"""Shared fixtures for the revamp_v2 tests: sys.path setup for the
src/revamp_v2 flat modules, and a minimal synthetic household (persona +
injected program) that passes all static checks."""
from __future__ import annotations

import copy
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SRC = REPO / "src" / "revamp_v2"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

RECEPTACLES = [
    {"id": "table_a", "room": "living"},
    {"id": "shelf_b", "room": "living"},
    {"id": "bed_b1", "room": "bedroom"},
    {"id": "sink_k", "room": "kitchen"},
]

PERSONA = {
    # no `reasoning` key: the scratchpad is stripped before the persona
    # ever becomes an artifact (see generate_persona)
    "household_id": "hh_test",
    "household_type": "test_type",
    "residents": [
        {"id": "resident_1", "name": "T", "age": 30, "occupation": "tester",
         "personality": "tidy", "habits": ["a", "b", "c", "d", "e"]},
    ],
    "relationships": "lives alone",
    "home_layout_notes": "one room",
    "object_inventory": [
        {"id": "mug_1", "class": "mug", "owner": "resident_1", "role": "coffee"},
        {"id": "book_1", "class": "book", "owner": "resident_1",
         "role": "decorative; never moves"},
    ],
    "daily_life_summary": "simple days",
    "quirks": "none",
}


def mini_program(**overrides) -> dict:
    """A small, fully valid INJECTED program (receptacles/household_type
    present). Deep-copied so tests can mutate freely."""
    program = {
        "household": "hh_test",
        "household_type": "test_type",
        "source_persona": "persona.yaml",
        "days": 21,
        "day0": "Monday",
        "residents": [{"id": "resident_1", "jitter_scale": 1.0}],

        "receptacles": copy.deepcopy(RECEPTACLES),

        "weekly_blocks": [
            {"resident": "resident_1", "activity": "breakfast",
             "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
             "start": "08:00", "end": "08:30", "at": "table_a",
             "jitter": "routine", "skip_p": 0.0, "sleep": False,
             "cites": "coffee"},
            {"resident": "resident_1", "activity": "relax",
             "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
             "start": "21:00", "end": "21:45", "at": "table_a",
             "jitter": "flexible", "skip_p": 0.0, "sleep": False,
             "cites": "simple days"},
        ],
        "sleep_schedule": [
            {"resident": "resident_1", "activity": "night_sleep",
             "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
             "start": "22:00", "end": "07:30+1", "at": "bed_b1",
             "jitter": "routine", "cites": "simple days"},
        ],
        "object_rules": [
            {"object": "mug_1", "home": "shelf_b", "cites": "coffee",
             "rules": [
                {"activity": "breakfast", "phase": "during",
                 "only_from": ["shelf_b"],
                 "dest": "table_a", "cites": "coffee"},
                {"activity": "breakfast", "phase": "after", "dest": "sink_k",
                 "p": 0.8, "else": "table_a", "only_from": ["table_a"],
                 "cites": "coffee"},
                # at-home coverage (broadened check 3): every at-home,
                # non-sleep weekly activity needs at least one binding —
                # "relax" gets the mug within reach, same as a real
                # evening.
                {"activity": "relax", "phase": "during", "dest": "table_a",
                 "only_from": ["shelf_b", "sink_k"],
                 "cites": "simple days"}]},
            {"object": "book_1", "home": "table_a", "cites": "never moves",
             "motion": "rarely_moved", "rules": []},   # declared static
        ],
        "activities": [{"name": "breakfast", "cites": "coffee"}],
        "arc_events": [
            {"day": 3, "patch": {"drop": ["relax"]},
             "note": "an off evening"},
            {"day": 5, "patch": {"add": [
                {"resident": "resident_1", "activity": "errands",
                 "start": "10:00", "at": "ELSEWHERE",
                 "jitter": "external"}]},
             "note": "an appointment"},
            {"day": 8, "patch": {"drop": ["relax"]}, "note": "tired"},
            {"day": 9, "patch": {"drop": ["relax"]}, "note": "tired"},
        ],
    }
    program.update(overrides)
    return copy.deepcopy(program)


def mini_program_v3(**overrides) -> dict:
    """The v3-shape sibling of mini_program: after-only dist rules with
    NO_OP mass (the shape build_program_schema now enforces). mini_program
    stays old-style on purpose — the expander must keep realizing every
    program already on disk byte-identically."""
    program = mini_program()
    program["object_rules"] = [
        {"object": "mug_1", "cites": "coffee", "home": "shelf_b",
         "p_misplace": 0.1,
         "rules": [
             {"cites": "coffee", "activity": "breakfast", "phase": "after",
              "dist": [{"dest": "sink_k", "p": 0.7},
                       {"dest": "table_a", "p": 0.3}]},
             {"cites": "simple days", "activity": "relax", "phase": "after",
              "dist": [{"dest": "NO_OP", "p": 0.8},
                       {"dest": "shelf_b", "p": 0.2}]}]},
        {"object": "book_1", "cites": "never moves", "home": "table_a",
         "rules": []},
    ]
    program.update(overrides)
    return copy.deepcopy(program)
