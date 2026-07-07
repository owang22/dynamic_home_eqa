"""
Unit tests for env/replay.py, focused on initial_state_and_changes_from_manifest
— specifically the bug found while building the embodied-agent world: a
volatile (insert_new) label was being seeded into the t=0 initial state from
its first *move_existing* event (a later event, chronologically after its
real first-ever appearance), making it look like it existed before its own
insert_new event fired.
"""
from __future__ import annotations

from dynamic_home_eqa.env.replay import initial_state_and_changes_from_manifest, state_at

_SCENE = "102343992"  # real scene; has real "chair" instances, no real "keys"/"phone" instances


def _manifest(changes: list[dict]) -> dict:
    return {"scene_id": _SCENE, "resident_profile": "test", "seed": 1, "changes": changes}


def test_volatile_label_absent_from_initial_state_before_its_insert_event():
    changes = [
        {"t": 6.0, "label": "keys_1", "change_type": "insert_new",
         "object_category": "keys", "from_semantic": None, "to_semantic": "bedroom",
         "reason": "", "mover": "Alex"},
        {"t": 10.0, "label": "keys_1", "change_type": "move_existing",
         "object_category": "keys", "from_semantic": "bedroom", "to_semantic": "kitchen",
         "reason": "", "mover": "Alex"},
    ]
    initial_state, parsed_changes = initial_state_and_changes_from_manifest(_manifest(changes))

    assert "keys_1" not in initial_state.instances

    state_before = state_at(initial_state, parsed_changes, t=5.0)
    assert "keys_1" not in state_before.instances

    state_after_insert = state_at(initial_state, parsed_changes, t=6.0)
    assert state_after_insert.instances["keys_1"].current_semantic == "bedroom"

    state_after_move = state_at(initial_state, parsed_changes, t=10.0)
    assert state_after_move.instances["keys_1"].current_semantic == "kitchen"


def test_real_instance_backed_label_is_seeded_from_first_move_existing():
    changes = [
        {"t": 5.0, "label": "chair_1", "change_type": "move_existing",
         "object_category": "chair", "from_semantic": "kitchen.counter_tucked",
         "to_semantic": "dining.table", "reason": "", "mover": "Alex"},
    ]
    initial_state, _ = initial_state_and_changes_from_manifest(_manifest(changes))
    # chair_1 has a real starting instance in this scene — it exists from
    # t=0 at whatever from_semantic its first (only) event reports.
    assert "chair_1" in initial_state.instances
    assert initial_state.instances["chair_1"].current_semantic == "kitchen.counter_tucked"


def test_repeated_calls_do_not_leak_mutation_across_independent_results():
    # load_scene_state() is lru_cache'd per scene_id; this function must not
    # mutate its cached return value in place, or a second manifest for the
    # same scene would silently inherit the first call's per-label edits.
    changes_a = [
        {"t": 5.0, "label": "chair_1", "change_type": "move_existing",
         "object_category": "chair", "from_semantic": "kitchen.counter_tucked",
         "to_semantic": "dining.table", "reason": "", "mover": "Alex"},
    ]
    changes_b: list[dict] = []

    state_a, _ = initial_state_and_changes_from_manifest(_manifest(changes_a))
    state_b, _ = initial_state_and_changes_from_manifest(_manifest(changes_b))

    assert state_a.instances["chair_1"].current_semantic == "kitchen.counter_tucked"
    # state_b was built from an empty change list — its chair_1 (if the
    # scene has a real one) must reflect load_scene_state's own default,
    # not state_a's mutation.
    if "chair_1" in state_b.instances:
        assert state_b.instances["chair_1"].current_semantic != "dining.table"
