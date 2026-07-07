"""
M0 tests: EmbodiedWorld replay + geodesic time.

Requires habitat_sim (see embodied/world.py's module docstring) — skipped,
not failed, when unavailable (this repo's default LLM-generation environment
doesn't have it; run these from a conda env that does, e.g. explore-eqa).
"""
from __future__ import annotations

import json
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
    # The *fixed* real-model output (post trace-integrity phase), not the
    # frozen "before" fixture kept elsewhere only to pin trace_validate's
    # regression counts — this one is representative of what the embodied
    # phase will actually process.
    result = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_generation_result.json").read_text())
    manifest = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_manifest.json").read_text())
    return result, manifest


def test_fixture_is_trace_valid(real_day):
    """Sanity check on the fixture itself: the embodied phase builds on a
    validated day, not a known-broken one (that's the separate frozen
    fixture trace_validate's own regression test pins)."""
    from dynamic_home_eqa.trace_validate import validate

    result, manifest = real_day
    report = validate(manifest["changes"], result["traces"])
    assert report.ok, report.summary()


@pytest.fixture
def world(real_day):
    from dynamic_home_eqa.embodied.world import EmbodiedWorld
    result, manifest = real_day
    w = EmbodiedWorld(_REAL_SCENE, result, manifest)
    yield w
    w.close()


# ---------------------------------------------------------------------------
# Replay diff test: EmbodiedWorld's replayed state must agree with
# ground_truth.true_anchor (both built on env.replay.state_at) at every
# event boundary, not just at t=0 and t=end.
# ---------------------------------------------------------------------------

def test_current_instances_matches_ground_truth_at_every_event_boundary(world, real_day):
    from dynamic_home_eqa.embodied.ground_truth import true_anchor

    _, manifest = real_day
    changes = manifest["changes"]
    check_times = sorted({0.0} | {c["t"] for c in changes} | {c["t"] + 1e-6 for c in changes})

    for t in check_times:
        world.advance_to(t)
        instances = world.current_instances()
        for label, (_cat, slot) in instances.items():
            expected = true_anchor(label, t, world.initial_state, world.changes)
            assert slot == expected, f"label={label} t={t}: world says {slot!r}, ground truth says {expected!r}"


def test_instance_absent_before_its_insert_new_event(world, real_day):
    _, manifest = real_day
    inserts = [c for c in manifest["changes"] if c["change_type"] == "insert_new"]
    assert inserts, "fixture must contain at least one insert_new event"
    first_insert = min(inserts, key=lambda c: c["t"])

    world.advance_to(max(0.0, first_insert["t"] - 0.01))
    instances_before = world.current_instances()
    assert first_insert["label"] not in instances_before

    world.advance_to(first_insert["t"])
    instances_after = world.current_instances()
    assert first_insert["label"] in instances_after


# ---------------------------------------------------------------------------
# Geodesic time
# ---------------------------------------------------------------------------

def test_geodesic_time_is_finite_and_positive_for_connected_rooms(world):
    # dining_room and laundry_room are confirmed (real scene inspection) to
    # be on the same navmesh island in this scene.
    a = world.room_centroid_pose("dining_room")
    b = world.room_centroid_pose("laundry_room")
    assert a is not None and b is not None
    t = world.geodesic_time(a.position, b.position)
    assert 0.0 < t < float("inf")


def test_geodesic_time_is_symmetric(world):
    a = world.room_centroid_pose("dining_room")
    b = world.room_centroid_pose("laundry_room")
    t_ab = world.geodesic_time(a.position, b.position)
    t_ba = world.geodesic_time(b.position, a.position)
    assert abs(t_ab - t_ba) < 1e-3


def test_geodesic_time_is_cached(world):
    a = world.room_centroid_pose("dining_room")
    b = world.room_centroid_pose("laundry_room")
    n_before = len(world._geodesic_cache)
    world.geodesic_time(a.position, b.position)
    n_after_first = len(world._geodesic_cache)
    world.geodesic_time(a.position, b.position)
    n_after_second = len(world._geodesic_cache)
    assert n_after_first == n_before + 1
    assert n_after_second == n_after_first


def test_geodesic_time_is_inf_for_a_genuinely_disconnected_fragment(world):
    # The navmesh-connectivity phase's D1 fix (agent_max_climb 0.2 -> 0.4,
    # see config.NavMeshConfig) merged every canonical room's centroid
    # (including kitchen and bedroom, previously thought to be on
    # disconnected floors — that assumption was wrong, see world.py's
    # module docstring) into one connected island. The living_room
    # furniture anchors (sofa/corner/open_floor/window_sill) are the one
    # fragment that resisted every swept navmesh setting and remains
    # genuinely disconnected — world._anchor_positions filters them out
    # (see world._ensure_sim), so fetch the raw position directly to
    # confirm geodesic_time still honestly reports no path, not a bug.
    from dynamic_home_eqa.topdown_map import anchor_world_positions

    kitchen = world.room_centroid_pose("kitchen")
    assert kitchen is not None
    raw_sofa_pos = anchor_world_positions(world.scene_id)["living_room.sofa"]
    t = world.geodesic_time(kitchen.position, raw_sofa_pos)
    assert t == float("inf")


def test_room_centroid_positions_are_never_nan(world):
    for room in world._room_centroids:
        pose = world.room_centroid_pose(room)
        assert pose is not None
        assert pose.x == pose.x  # NaN != NaN
        assert pose.z == pose.z


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_replay_is_deterministic_across_independent_world_instances(real_day):
    from dynamic_home_eqa.embodied.world import EmbodiedWorld

    result, manifest = real_day
    w1 = EmbodiedWorld(_REAL_SCENE, result, manifest)
    w2 = EmbodiedWorld(_REAL_SCENE, result, manifest)
    try:
        for t in (0.0, 6.5, 12.0, 18.25, 23.9):
            w1.advance_to(t)
            w2.advance_to(t)
            assert w1.current_instances() == w2.current_instances()
    finally:
        w1.close()
        w2.close()


def test_execute_sequence_is_deterministic_across_independent_world_instances(real_day):
    from dynamic_home_eqa.embodied.world import EmbodiedWorld
    from dynamic_home_eqa.embodied.types import Goto, Rotate, Sense

    result, manifest = real_day
    w1 = EmbodiedWorld(_REAL_SCENE, result, manifest)
    w2 = EmbodiedWorld(_REAL_SCENE, result, manifest)
    try:
        # "living_room" (not "kitchen"): the default starting pose is on
        # the largest connected navmesh island (dining_room/laundry_room/
        # living_room — this scene's navmesh splits into several
        # disconnected islands, confirmed directly, and kitchen is alone on
        # a different one). This test is about determinism, not
        # reachability, so it must target a room actually reachable from
        # the default start.
        living1 = w1.room_centroid_pose("living_room")
        living2 = w2.room_centroid_pose("living_room")
        assert living1 == living2

        r1 = w1.execute(Goto(target=living1.position))
        r2 = w2.execute(Goto(target=living2.position))
        assert r1.final_t == r2.final_t
        assert r1.final_pose == r2.final_pose
        assert len(r1.snapshots) == len(r2.snapshots)

        r1b = w1.execute(Rotate(delta_yaw_rad=1.0))
        r2b = w2.execute(Rotate(delta_yaw_rad=1.0))
        assert r1b.final_t == r2b.final_t
        assert r1b.final_pose == r2b.final_pose
    finally:
        w1.close()
        w2.close()
