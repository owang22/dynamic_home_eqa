"""Unit tests for generation/instances.py — per-event resolution of which
real Tier-2 instance a category-level proposal moves (the fix for one chair
teleporting across the house while its siblings never move)."""
from __future__ import annotations

from dynamic_home_eqa.generation.instances import pick_real_instance


def test_prefers_instance_in_the_acting_room():
    slots = {"chair_1": "dining_room.table_1.tucked", "chair_2": "kitchen.counter_1"}
    assert pick_real_instance("chair", ["chair_1", "chair_2"], slots, "kitchen") == "chair_2"
    assert pick_real_instance("chair", ["chair_1", "chair_2"], slots, "dining_room") == "chair_1"


def test_lowest_index_tie_break_in_room():
    slots = {"chair_3": "kitchen.table_1", "chair_10": "kitchen.counter_1"}
    assert pick_real_instance("chair", ["chair_10", "chair_3"], slots, "kitchen") == "chair_3"


def test_falls_back_to_lowest_index_when_room_has_none():
    slots = {"chair_1": "bedroom_1.bed_1", "chair_2": "bedroom_2.bed_1"}
    assert pick_real_instance("chair", ["chair_2", "chair_1"], slots, "kitchen") == "chair_1"


def test_room_aliasing_matches():
    # tv_room aliases to the living_room family via rooms_match
    slots = {"chair_1": "tv_room.table_1", "chair_2": "bedroom_1.bed_1"}
    assert pick_real_instance("chair", ["chair_1", "chair_2"], slots, "living_room") == "chair_1"


def test_none_room_uses_lowest_index():
    slots = {"chair_1": "kitchen.table_1", "chair_2": "kitchen.counter_1"}
    assert pick_real_instance("chair", ["chair_2", "chair_1"], slots, None) == "chair_1"
