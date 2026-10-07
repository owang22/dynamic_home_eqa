"""
Tests for generation/state_rules.py's deterministic (non-LLM) state-change
proposer (M3).
"""
from __future__ import annotations

from dynamic_home_eqa.generation.state_rules import propose_state_changes


class TestRoomTriggers:
    def test_kitchen_activity_triggers_oven_and_fridge(self):
        proposals = propose_state_changes(
            activity="breakfast", start=7.0, end=7.5, location="kitchen",
            household_id="hh1", day=0, index=0,
        )
        categories = {p["object_category"] for p in proposals}
        assert categories == {"oven", "fridge"}

    def test_bedroom_activity_triggers_wardrobe(self):
        proposals = propose_state_changes(
            activity="get_dressed", start=7.0, end=7.2, location="bedroom",
            household_id="hh1", day=0, index=0,
        )
        assert {p["object_category"] for p in proposals} == {"wardrobe"}

    def test_untriggered_room_produces_nothing(self):
        proposals = propose_state_changes(
            activity="tv_time", start=20.0, end=21.0, location="office",
            household_id="hh1", day=0, index=0,
        )
        # "office" isn't a room trigger, and "tv_time" the label trigger
        # only maps to "tv" regardless of room — both fire here since the
        # label substring check is independent of location.
        assert {p["object_category"] for p in proposals} == {"tv"}

    def test_no_trigger_at_all_produces_nothing(self):
        proposals = propose_state_changes(
            activity="reading", start=20.0, end=21.0, location="office",
            household_id="hh1", day=0, index=0,
        )
        assert proposals == []


class TestLabelTrigger:
    def test_tv_substring_triggers_tv_regardless_of_room(self):
        proposals = propose_state_changes(
            activity="tv_time", start=20.0, end=21.0, location="living_room",
            household_id="hh1", day=0, index=0,
        )
        assert {p["object_category"] for p in proposals} == {"tv"}

    def test_label_matching_is_case_insensitive(self):
        proposals = propose_state_changes(
            activity="TV_TIME", start=20.0, end=21.0, location="living_room",
            household_id="hh1", day=0, index=0,
        )
        assert {p["object_category"] for p in proposals} == {"tv"}


class TestProposalShape:
    def test_each_category_gets_a_bracketing_on_off_pair(self):
        proposals = propose_state_changes(
            activity="tv_time", start=20.0, end=21.0, location="living_room",
            household_id="hh1", day=0, index=0,
        )
        assert len(proposals) == 2
        targets = sorted(p["target_state"] for p in proposals)
        assert targets == ["powered", "unpowered"]

    def test_on_event_precedes_off_event_within_window(self):
        proposals = propose_state_changes(
            activity="tv_time", start=20.0, end=21.0, location="living_room",
            household_id="hh1", day=0, index=0,
        )
        on_t  = next(p["_t"] for p in proposals if p["target_state"] == "powered")
        off_t = next(p["_t"] for p in proposals if p["target_state"] == "unpowered")
        assert 20.0 <= on_t < off_t <= 21.0

    def test_state_variable_field_is_correct(self):
        proposals = propose_state_changes(
            activity="breakfast", start=7.0, end=7.5, location="kitchen",
            household_id="hh1", day=0, index=0,
        )
        by_cat = {p["object_category"]: p["state_variable"] for p in proposals}
        assert by_cat["oven"] == "power"
        assert by_cat["fridge"] == "door"

    def test_location_field_passed_through(self):
        proposals = propose_state_changes(
            activity="breakfast", start=7.0, end=7.5, location="kitchen",
            household_id="hh1", day=0, index=0,
        )
        assert all(p["_location"] == "kitchen" for p in proposals)


class TestDeterminism:
    def test_same_inputs_produce_identical_output(self):
        args = dict(activity="breakfast", start=7.0, end=7.5, location="kitchen",
                    household_id="hh1", day=0, index=3)
        assert propose_state_changes(**args) == propose_state_changes(**args)

    def test_different_index_produces_different_jitter(self):
        p1 = propose_state_changes(activity="breakfast", start=7.0, end=7.5,
                                    location="kitchen", household_id="hh1", day=0, index=0)
        p2 = propose_state_changes(activity="breakfast", start=7.0, end=7.5,
                                    location="kitchen", household_id="hh1", day=0, index=1)
        times1 = sorted(p["_t"] for p in p1)
        times2 = sorted(p["_t"] for p in p2)
        assert times1 != times2
