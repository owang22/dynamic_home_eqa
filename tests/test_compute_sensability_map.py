"""Tests for scripts/compute_sensability_map.py.

Pure-logic pieces (save/load round-trip, is_robot_visible) need no
habitat_sim. compute_sensability_map itself needs a real EmbodiedWorld —
guarded the same way tests/test_sensor.py is."""
from __future__ import annotations

import json
import pathlib

import pytest

from dynamic_home_eqa.scripts.compute_sensability_map import (
    is_robot_visible,
    load_sensability_map,
    save_sensability_map,
)

_FIXTURES = pathlib.Path(__file__).parent / "fixtures"
_REAL_SCENE = "102343992"


def _has_habitat_sim() -> bool:
    try:
        import habitat_sim  # noqa: F401
        return True
    except ImportError:
        return False


class TestSaveLoadRoundTrip:
    def test_round_trips_through_disk(self, tmp_path):
        scene_map = {
            "scene_id": "999", "code_hash": "abc123",
            "anchors": {
                "dining.table": {"robot_visible": True, "pose": {"x": 1.0, "y": 0.5, "z": 2.0, "yaw_rad": 0.1}},
                "fridge": {"robot_visible": False, "pose": None},
            },
        }
        path = save_sensability_map(scene_map, out_dir=tmp_path)
        assert path.exists()
        loaded = load_sensability_map("999", out_dir=tmp_path)
        assert loaded == scene_map

    def test_load_missing_scene_returns_none(self, tmp_path):
        assert load_sensability_map("no_such_scene", out_dir=tmp_path) is None


class TestIsRobotVisible:
    def test_true_for_a_visible_anchor(self):
        scene_map = {"anchors": {"dining.table": {"robot_visible": True, "pose": {}}}}
        assert is_robot_visible(scene_map, "dining.table") is True

    def test_false_for_a_known_unreachable_anchor(self):
        scene_map = {"anchors": {"fridge": {"robot_visible": False, "pose": None}}}
        assert is_robot_visible(scene_map, "fridge") is False

    def test_none_for_an_anchor_absent_from_the_map(self):
        scene_map = {"anchors": {"fridge": {"robot_visible": False, "pose": None}}}
        assert is_robot_visible(scene_map, "not_in_this_scene_at_all") is None


pytestmark_live = pytest.mark.skipif(not _has_habitat_sim(), reason="habitat_sim not installed in this environment")


@pytestmark_live
def test_compute_sensability_map_matches_world_viewpoint_for_directly():
    from dynamic_home_eqa.embodied.world import EmbodiedWorld
    from dynamic_home_eqa.scripts.compute_sensability_map import compute_sensability_map

    gen_result = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_generation_result.json").read_text())
    manifest = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_manifest.json").read_text())
    world = EmbodiedWorld(_REAL_SCENE, gen_result, manifest)
    try:
        world._ensure_sim()
        scene_map = compute_sensability_map(_REAL_SCENE, world)

        assert scene_map["scene_id"] == _REAL_SCENE
        assert set(scene_map["anchors"]) == set(world._anchor_positions)

        # Cross-check every entry against a fresh, independent call to the
        # same underlying search — the map must be a faithful cache, not
        # an approximation of it.
        for anchor, entry in scene_map["anchors"].items():
            vp = world.viewpoint_for(anchor)
            if vp is None:
                assert entry["robot_visible"] is False
                assert entry["pose"] is None
            else:
                assert entry["robot_visible"] is True
                assert entry["pose"] == {"x": vp.x, "y": vp.y, "z": vp.z, "yaw_rad": vp.yaw_rad}

        # The known-unreachable fridge anchor (see test_sensor.py's
        # _NO_VIEWPOINT_WITHIN_RANGE) must show up as robot_visible=False
        # here too — same underlying search, same real scene geometry.
        assert scene_map["anchors"]["fridge"]["robot_visible"] is False
    finally:
        world.close()
