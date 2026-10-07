"""Pure-logic tests for env/anchor_admission.py — no habitat_sim needed
(the precomputation script that PRODUCES a real map does, see
tests/test_compute_anchor_admission_map.py)."""
from __future__ import annotations

import logging

from dynamic_home_eqa.env.anchor_admission import (
    ADMISSION_VERSION,
    anchor_capacity,
    is_reachable,
    load_anchor_admission_map,
    save_anchor_admission_map,
)


def _sample_map(admission_version: int = ADMISSION_VERSION) -> dict:
    return {
        "scene_id": "999",
        "admission_version": admission_version,
        "footprint_m2": 0.06,
        "anchors": {
            "dining.table": {"reachable": True, "capacity": 6, "capacity_source": "receptacle"},
            "tv": {"reachable": False, "capacity": None, "capacity_source": None},
            "living_room.corner": {"reachable": True, "capacity": None, "capacity_source": None},
        },
    }


class TestSaveLoadRoundTrip:
    def test_round_trips_through_disk(self, tmp_path):
        admission_map = _sample_map()
        path = save_anchor_admission_map(admission_map, out_dir=tmp_path)
        assert path.exists()
        loaded = load_anchor_admission_map("999", out_dir=tmp_path)
        assert loaded == admission_map

    def test_load_missing_scene_returns_none(self, tmp_path):
        assert load_anchor_admission_map("no_such_scene", out_dir=tmp_path) is None

    def test_load_missing_scene_warns(self, tmp_path, caplog):
        with caplog.at_level(logging.WARNING):
            load_anchor_admission_map("no_such_scene", out_dir=tmp_path)
        assert any("no_such_scene" in r.message for r in caplog.records)

    def test_load_stale_version_returns_none(self, tmp_path):
        save_anchor_admission_map(_sample_map(admission_version=ADMISSION_VERSION - 1), out_dir=tmp_path)
        assert load_anchor_admission_map("999", out_dir=tmp_path) is None

    def test_load_stale_version_warns(self, tmp_path, caplog):
        save_anchor_admission_map(_sample_map(admission_version=ADMISSION_VERSION - 1), out_dir=tmp_path)
        with caplog.at_level(logging.WARNING):
            load_anchor_admission_map("999", out_dir=tmp_path)
        assert any("999" in r.message and "stale" in r.message for r in caplog.records)


class TestIsReachable:
    def test_true_for_a_reachable_anchor(self):
        assert is_reachable(_sample_map(), "dining.table") is True

    def test_false_for_a_known_unreachable_anchor(self):
        assert is_reachable(_sample_map(), "tv") is False

    def test_none_for_an_anchor_absent_from_the_map(self):
        assert is_reachable(_sample_map(), "not_in_this_scene_at_all") is None

    def test_none_when_the_map_itself_is_none(self):
        assert is_reachable(None, "dining.table") is None


class TestAnchorCapacity:
    def test_positive_int_for_an_instance_anchor_with_a_receptacle(self):
        assert anchor_capacity(_sample_map(), "dining.table") == 6

    def test_none_for_an_unreachable_anchor(self):
        assert anchor_capacity(_sample_map(), "tv") is None

    def test_none_for_a_region_anchor(self):
        assert anchor_capacity(_sample_map(), "living_room.corner") is None

    def test_none_for_an_anchor_absent_from_the_map(self):
        assert anchor_capacity(_sample_map(), "not_in_this_scene_at_all") is None

    def test_none_when_the_map_itself_is_none(self):
        assert anchor_capacity(None, "dining.table") is None
