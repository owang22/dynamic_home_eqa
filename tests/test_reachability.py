"""
Tests for embodied/reachability.py and the navmesh-connectivity phase's
NavMeshConfig — the scene-qualification pre-flight this phase adds so a
scene like the one M1's gate hit (80% abstain rate, identical across every
policy, traced to unreachable frozen labels) is rejected before an
experiment runs, not discovered mid-run.

Requires habitat_sim — skipped, not failed, when unavailable.
"""
from __future__ import annotations

import pytest

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


def test_scene_qualifies_under_the_navmesh_connectivity_fix():
    from dynamic_home_eqa.embodied.config import NavMeshConfig
    from dynamic_home_eqa.embodied.reachability import check_reachability_invariant

    result = check_reachability_invariant(_REAL_SCENE, NavMeshConfig())
    assert result.ok, f"unreachable: {result.unreachable}"
    assert result.start_room  # a start room was actually selected
    assert result.start_island >= 0


def test_living_room_furniture_cluster_is_excluded_not_unreachable():
    """The living_room navmesh fragment D1's sweep never merged (sofa/
    corner/open_floor/window_sill anchors, ~9.3 m², confirmed disconnected
    at every swept setting including agent_radius=0.04) must show up as an
    excluded sub-threshold fragment, not silently pass and not count as a
    failure — this is the exact distinction that keeps the invariant from
    being either too strict (blocking on a real, tiny, disqualified
    fragment) or too lax (missing a real reachability gap).

    "tv" (M3: state-change dynamics — env/inventory.py's STATEFUL_FURNITURE)
    joins this same known fragment in this scene — its real HSSD position
    resolves into the same disconnected media-console nook as the sofa
    cluster, not a new/different disconnection.

    anchor_world_positions was widened to a real
    per-room furniture census (not just the 16 hand-authored SLOT_ANCHORS
    entries) — this surfaced MORE real anchors landing in the SAME
    disconnected living_room fragment (living_room.couch/table/cabinet/
    potted_plant — the same real instances behind sofa/corner/etc., just
    newly given their own census-derived keys too), confirmed by direct
    inspection to be the identical small fragment, not a new one. It ALSO
    surfaced a genuinely SEPARATE, previously-invisible disconnected
    fragment: "bathroom.bathtub" — a different room, a different island,
    not folded into "the living room cluster" naming even though both are
    reported by the same check. Two known small fragments now, not one;
    this is a real, disclosed finding about this scene's navmesh, not
    something to paper over by growing the assertion silently."""
    from dynamic_home_eqa.embodied.config import NavMeshConfig
    from dynamic_home_eqa.embodied.reachability import check_reachability_invariant

    result = check_reachability_invariant(_REAL_SCENE, NavMeshConfig())
    excluded_anchors = {e.split(":", 1)[1] for e in result.excluded_small_fragment if e.startswith("anchor:")}
    assert excluded_anchors == {
        "living_room.sofa", "living_room.corner",
        "living_room.open_floor", "living_room.window_sill",
        "living_room.couch", "living_room.table",
        "living_room.cabinet", "living_room.potted_plant",
        "tv",
        "bathroom.bathtub",
    }


def test_reachability_fails_loudly_when_min_component_area_is_impossibly_large():
    """Sanity check on the invariant itself: if every island is excluded as
    "too small", checked collapses to 0 rooms+anchors — a degenerate config
    that should be obviously visible (checked=0), not silently reported as
    passing."""
    from dataclasses import replace

    from dynamic_home_eqa.embodied.config import NavMeshConfig
    from dynamic_home_eqa.embodied.reachability import check_reachability_invariant

    config = replace(NavMeshConfig(), min_component_area_m2=1_000_000.0)
    result = check_reachability_invariant(_REAL_SCENE, config)
    assert result.checked == 0


def test_navmesh_config_is_frozen_and_hashable():
    from dataclasses import FrozenInstanceError

    from dynamic_home_eqa.embodied.config import NavMeshConfig

    config = NavMeshConfig()
    with pytest.raises(FrozenInstanceError):
        config.agent_max_climb = 1.0  # type: ignore[misc]
    hash(config)  # must not raise


def test_world_anchor_positions_exclude_the_disqualified_fragment(tmp_path):
    import json
    import pathlib

    from dynamic_home_eqa.embodied.world import EmbodiedWorld

    fixtures = pathlib.Path(__file__).parent / "fixtures"
    result = json.loads((fixtures / "102343992_family_with_kids_fixed_generation_result.json").read_text())
    manifest = json.loads((fixtures / "102343992_family_with_kids_fixed_manifest.json").read_text())

    world = EmbodiedWorld(_REAL_SCENE, result, manifest)
    try:
        for slot in ("living_room.sofa", "living_room.corner",
                     "living_room.open_floor", "living_room.window_sill"):
            assert slot not in world._anchor_positions
        # A representative anchor on the merged main island must survive.
        assert "kitchen.counter" in world._anchor_positions
    finally:
        world.close()


def test_default_pose_lands_on_an_island_clearing_min_indoor_fraction():
    import json
    import pathlib

    from dynamic_home_eqa.embodied.world import EmbodiedWorld

    fixtures = pathlib.Path(__file__).parent / "fixtures"
    result = json.loads((fixtures / "102343992_family_with_kids_fixed_generation_result.json").read_text())
    manifest = json.loads((fixtures / "102343992_family_with_kids_fixed_manifest.json").read_text())

    world = EmbodiedWorld(_REAL_SCENE, result, manifest)
    try:
        island = world._sim.pathfinder.get_island(list(world.pose.position))
        assert island >= 0
        indoor_fraction = world._island_indoor_fraction(island)
        assert indoor_fraction >= world.config.navmesh.min_indoor_fraction
    finally:
        world.close()
