"""
M1 tests: sensor.py's visibility oracle and viewpoint_for, on the real scene.

Requires habitat_sim — skipped, not failed, when unavailable (see
embodied/sensor.py's module docstring).
"""
from __future__ import annotations

import json
import math
import pathlib

import pytest

_FIXTURES = pathlib.Path(__file__).parent / "fixtures"
_REAL_SCENE = "102343992"


def _has_habitat_sim() -> bool:
    try:
        import habitat_sim  # noqa: F401
        return True
    except ImportError:
        return False


pytestmark = pytest.mark.skipif(
    not _has_habitat_sim(), reason="habitat_sim not installed in this environment"
)


@pytest.fixture(scope="module")
def real_day():
    result = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_generation_result.json").read_text())
    manifest = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_manifest.json").read_text())
    return result, manifest


@pytest.fixture
def world(real_day):
    from dynamic_home_eqa.embodied.world import EmbodiedWorld
    result, manifest = real_day
    w = EmbodiedWorld(_REAL_SCENE, result, manifest)
    yield w
    w.close()


# ---------------------------------------------------------------------------
# in_fov / in_range — pure geometry, no habitat_sim needed, but kept in this
# module (guarded the same way) since they're part of the same visibility
# contract the rest of this file tests against real geometry.
# ---------------------------------------------------------------------------

def test_in_fov_true_directly_ahead():
    from dynamic_home_eqa.embodied.sensor import in_fov
    assert in_fov((0, 0, 0), yaw_rad=0.0, target_pos=(1, 0, 0), fov_deg=90.0)


def test_in_fov_false_directly_behind():
    from dynamic_home_eqa.embodied.sensor import in_fov
    assert not in_fov((0, 0, 0), yaw_rad=0.0, target_pos=(-1, 0, 0), fov_deg=90.0)


def test_in_fov_true_after_rotating_to_face_it():
    from dynamic_home_eqa.embodied.sensor import in_fov
    target = (-1, 0, 0)
    assert not in_fov((0, 0, 0), yaw_rad=0.0, target_pos=target, fov_deg=90.0)
    assert in_fov((0, 0, 0), yaw_rad=math.pi, target_pos=target, fov_deg=90.0)


def test_in_range_true_within_max():
    from dynamic_home_eqa.embodied.sensor import in_range
    assert in_range((0, 0, 0), (3, 0, 0), max_range_m=5.0)


def test_in_range_false_beyond_max():
    from dynamic_home_eqa.embodied.sensor import in_range
    assert not in_range((0, 0, 0), (10, 0, 0), max_range_m=5.0)


# ---------------------------------------------------------------------------
# Occlusion / full visibility on real scene geometry
# ---------------------------------------------------------------------------

def test_anchor_in_another_room_behind_a_wall_is_not_visible(world):
    from dynamic_home_eqa.embodied.sensor import is_visible

    # kitchen.counter and dining.table are in different rooms with a wall
    # between them (confirmed directly: a ray between these rooms' centroids
    # hits geometry partway through, well short of the far room).
    kitchen_anchor = world._anchor_positions["kitchen.counter"]
    dining_anchor = world._anchor_positions["dining.table"]
    eye_pos = (kitchen_anchor[0], kitchen_anchor[1] + world.config.sensor.eye_height_m, kitchen_anchor[2])
    dx, dz = dining_anchor[0] - kitchen_anchor[0], dining_anchor[2] - kitchen_anchor[2]
    yaw_facing_dining = math.atan2(dz, dx)

    assert not is_visible(world._sim, eye_pos, yaw_facing_dining, dining_anchor, world.config.sensor)


def test_anchor_behind_the_agent_is_not_visible(world):
    from dynamic_home_eqa.embodied.sensor import is_visible

    vp = world.viewpoint_for("dining.table")
    assert vp is not None  # constructed to face the anchor
    anchor_pos = world._anchor_positions["dining.table"]
    eye_pos = (vp.x, vp.y + world.config.sensor.eye_height_m, vp.z)

    assert is_visible(world._sim, eye_pos, vp.yaw_rad, anchor_pos, world.config.sensor)
    behind_yaw = (vp.yaw_rad + math.pi) % (2 * math.pi)
    assert not is_visible(world._sim, eye_pos, behind_yaw, anchor_pos, world.config.sensor)


def test_rotating_makes_an_occluded_by_heading_anchor_visible(world):
    from dynamic_home_eqa.embodied.sensor import is_visible

    # living_room.sofa (used here previously) is now excluded from
    # world._anchor_positions — it sits on the one navmesh fragment the
    # navmesh-connectivity phase's D1 sweep never merged (see
    # config.NavMeshConfig's docstring) — office.desk is unaffected and
    # demonstrates the same face-it/face-away-from-it behavior.
    vp = world.viewpoint_for("office.desk")
    assert vp is not None
    anchor_pos = world._anchor_positions["office.desk"]
    eye_pos = (vp.x, vp.y + world.config.sensor.eye_height_m, vp.z)
    away_yaw = (vp.yaw_rad + math.pi) % (2 * math.pi)

    assert not is_visible(world._sim, eye_pos, away_yaw, anchor_pos, world.config.sensor)
    assert is_visible(world._sim, eye_pos, vp.yaw_rad, anchor_pos, world.config.sensor)


def test_anchor_within_range_is_visible_when_unobstructed(world):
    from dynamic_home_eqa.embodied.sensor import is_occluded, is_visible
    from dynamic_home_eqa.topdown_map import anchor_world_positions

    # Find a same-room (or open-plan) anchor pair confirmed unobstructed —
    # search rather than hardcode, since exactly which pairs are open-plan
    # is a property of this specific scene's geometry, not something to
    # assume from room names alone. Uses the raw (unfiltered) per-scene
    # anchor census, not world._anchor_positions: this test is about ray
    # occlusion physics, not navmesh reachability, and the reachability
    # filter (world._ensure_sim) happens to have dropped the living_room
    # cluster that supplies the only close, mutually-unobstructed pair.
    positions = anchor_world_positions(world.scene_id)
    found = False
    for slot_a, pos_a in positions.items():
        eye = (pos_a[0], pos_a[1] + world.config.sensor.eye_height_m, pos_a[2])
        for slot_b, pos_b in positions.items():
            if slot_a == slot_b:
                continue
            dist = sum((pos_a[i] - pos_b[i]) ** 2 for i in range(3)) ** 0.5
            if dist > world.config.sensor.max_sense_range_m or dist < 0.5:
                continue
            if not is_occluded(world._sim, eye, pos_b):
                dx, dz = pos_b[0] - pos_a[0], pos_b[2] - pos_a[2]
                yaw = math.atan2(dz, dx)
                assert is_visible(world._sim, eye, yaw, pos_b, world.config.sensor)
                found = True
                break
        if found:
            break
    assert found, "expected at least one unobstructed same-range anchor pair in this scene"


# ---------------------------------------------------------------------------
# viewpoint_for
# ---------------------------------------------------------------------------

# bedroom.bed in this specific scene has no clear line of sight within the
# full 5 m sensor range from any of 24 sampled angles across 11 radii up to
# 4.9 m — confirmed by direct search, not a radius/sample-count shortfall in
# viewpoint_for. The M4 anchor-sanity check already confirms the position
# itself is navigable-adjacent (you can walk up to it); this is genuinely
# about sightlines, e.g. a low headboard/canopy or enclosing furniture, not
# a bug. Real HSSD scenes can have furniture like this; a "no viewpoint
# within sensor range" answer for it is honest, not a defect to force away.
#
# "fridge" (M3: state-change dynamics — env/inventory.py's
# STATEFUL_FURNITURE) fails even more basically in this scene: its real
# HSSD position isn't navmesh-adjacent at all (confirmed — check_anchor_
# sanity flags it too, see test_topdown_map.py), not just a sightline
# issue — likely recessed into cabinetry with no adjacent floor space at
# all. Same category of real-scene geometry limitation as bedroom.bed, one
# step further; the navmesh-connectivity phase's own precedent is to
# document and exclude rather than force a fix (see NavMeshConfig's
# docstring on the living_room furniture cluster) — see
# experiment_config.py's FROZEN_STATE_LABELS, which excludes "fridge_1"
# for exactly this reason.
_NO_VIEWPOINT_WITHIN_RANGE = {"bedroom.bed", "fridge"}


def test_viewpoint_for_returns_a_visible_pose_for_every_real_anchor(world):
    from dynamic_home_eqa.embodied.sensor import is_visible

    assert world._anchor_positions, "fixture scene must have resolvable anchors"
    failures = []
    for slot, pos in world._anchor_positions.items():
        vp = world.viewpoint_for(slot)
        if vp is None:
            if slot not in _NO_VIEWPOINT_WITHIN_RANGE:
                failures.append((slot, "no viewpoint found"))
            continue
        eye_pos = (vp.x, vp.y + world.config.sensor.eye_height_m, vp.z)
        if not is_visible(world._sim, eye_pos, vp.yaw_rad, pos, world.config.sensor):
            failures.append((slot, "viewpoint pose does not itself pass visibility test"))
    assert not failures, f"anchors without a valid viewpoint: {failures}"


def test_viewpoint_for_is_cached(world):
    vp1 = world.viewpoint_for("dining.table")
    assert "dining.table" in world._viewpoint_cache
    vp2 = world.viewpoint_for("dining.table")
    assert vp1 == vp2


def test_viewpoint_for_unknown_anchor_returns_none(world):
    assert world.viewpoint_for("not_a_real_slot") is None
