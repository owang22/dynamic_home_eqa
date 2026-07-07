"""Unit tests for generation/exports.py."""
from __future__ import annotations

from dynamic_home_eqa.generation.exports import (
    category_location_change_stats,
    category_state_flip_stats,
    to_replay_format,
)


def test_category_location_change_stats_counts_and_dwell_time():
    changes = [
        {"t": 1.0, "label": "book_1", "object_category": "book", "to_semantic": "shelf"},
        {"t": 3.0, "label": "book_1", "object_category": "book", "to_semantic": "table"},
        {"t": 6.0, "label": "book_1", "object_category": "book", "to_semantic": "shelf"},
    ]
    stats = category_location_change_stats(changes)
    assert stats["book"]["location_changes"] == 3
    assert stats["book"]["distinct_slots_visited"] == 2  # shelf, table (shelf revisited)
    assert stats["book"]["mean_dwell_hours"] == 2.5  # (3-1 + 6-3) / 2


def test_category_location_change_stats_none_dwell_for_single_event():
    changes = [
        {"t": 1.0, "label": "vase_1", "object_category": "vase", "to_semantic": "table"},
    ]
    stats = category_location_change_stats(changes)
    assert stats["vase"]["location_changes"] == 1
    assert stats["vase"]["mean_dwell_hours"] is None


def test_category_location_change_stats_aggregates_across_labels_same_category():
    changes = [
        {"t": 1.0, "label": "cup_1", "object_category": "cup", "to_semantic": "sink"},
        {"t": 2.0, "label": "cup_2", "object_category": "cup", "to_semantic": "table"},
    ]
    stats = category_location_change_stats(changes)
    assert stats["cup"]["location_changes"] == 2
    assert stats["cup"]["distinct_slots_visited"] == 2


def test_category_location_change_stats_empty_input():
    assert category_location_change_stats([]) == {}


def test_to_replay_format_shape():
    generation_result = {
        "household_id": "102343992_family_with_kids",
        "persona": {"occupants": [{"name": "Alex", "age_band": "adult"}]},
        "traces": [
            {"occupant_name": "Alex", "activities": [
                {"activity": "cooking", "location": "kitchen", "start": 7.0, "end": 8.0},
            ]},
        ],
    }
    manifest = {
        "seed": 1,
        "changes": [
            {"t": 7.5, "label": "bowl_1", "change_type": "move_existing",
             "object_category": "bowl", "from_semantic": "kitchen.counter",
             "to_semantic": "dining.table", "reason": "breakfast", "mover": "Alex"},
        ],
    }
    replay = to_replay_format("102343992", "family_with_kids", 0, generation_result, manifest)

    assert replay["meta"]["scene_id"] == "102343992"
    assert replay["meta"]["household_id"] == "102343992_family_with_kids"
    assert replay["occupants"] == [{
        "name": "Alex", "age_band": "adult",
        "activities": [["cooking", "kitchen", 7.0, 8.0]],
    }]
    assert replay["changes"] == [
        [7.5, "bowl_1", "move_existing", "kitchen.counter", "dining.table", "breakfast", "Alex"],
    ]
    assert "bowl" in replay["category_stats"]


def test_to_replay_format_changes_sorted_by_t():
    generation_result = {"household_id": "x", "persona": {"occupants": []}, "traces": []}
    manifest = {
        "seed": 1,
        "changes": [
            {"t": 10.0, "label": "a", "change_type": "move_existing", "object_category": "cat",
             "from_semantic": "x", "to_semantic": "y", "reason": "", "mover": "Alex"},
            {"t": 2.0, "label": "b", "change_type": "move_existing", "object_category": "cat",
             "from_semantic": "x", "to_semantic": "y", "reason": "", "mover": "Alex"},
        ],
    }
    replay = to_replay_format("s", "p", 0, generation_result, manifest)
    assert [c[0] for c in replay["changes"]] == [2.0, 10.0]


def _state_change(t, label, category, variable, to_state):
    return {
        "t": t, "label": label, "change_type": "state_change",
        "object_category": category, "state_variable": variable, "to_state": to_state,
    }


def test_category_state_flip_stats_counts_and_dwell_time():
    changes = [
        _state_change(1.0, "tv_1", "tv", "power", "powered"),
        _state_change(3.0, "tv_1", "tv", "power", "unpowered"),
        _state_change(6.0, "tv_1", "tv", "power", "powered"),
    ]
    stats = category_state_flip_stats(changes)
    assert stats["tv::power"]["flip_count"] == 3
    assert stats["tv::power"]["mean_dwell_hours"] == 2.5  # (3-1 + 6-3) / 2


def test_category_state_flip_stats_ignores_location_changes():
    changes = [
        {"t": 1.0, "label": "book_1", "change_type": "move_existing",
         "object_category": "book", "to_semantic": "shelf"},
        _state_change(2.0, "tv_1", "tv", "power", "powered"),
    ]
    stats = category_state_flip_stats(changes)
    assert "book" not in stats
    assert list(stats.keys()) == ["tv::power"]


def test_category_state_flip_stats_keyed_by_category_and_variable_separately():
    changes = [
        _state_change(1.0, "fridge_1", "fridge", "door", "open"),
        _state_change(2.0, "tv_1", "tv", "power", "powered"),
    ]
    stats = category_state_flip_stats(changes)
    assert set(stats.keys()) == {"fridge::door", "tv::power"}


def test_category_state_flip_stats_none_dwell_for_single_flip():
    changes = [_state_change(1.0, "tv_1", "tv", "power", "powered")]
    stats = category_state_flip_stats(changes)
    assert stats["tv::power"]["flip_count"] == 1
    assert stats["tv::power"]["mean_dwell_hours"] is None
