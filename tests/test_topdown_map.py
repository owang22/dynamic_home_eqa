"""
Unit tests for topdown_map.py.

anchor_world_positions/room_centroids only need real HSSD scene JSON (no
habitat_sim) and run in any environment. load_topdown_map/check_anchor_sanity
need habitat_sim itself (not installed in this repo's default LLM-generation
environment — see topdown_map.py's module docstring) and are skipped when
it's unavailable rather than failing the whole suite.
"""
from __future__ import annotations

import numpy as np
import pytest

from dynamic_home_eqa.topdown_map import (
    TopdownMap,
    anchor_world_positions,
    room_centroids,
)

_REAL_SCENE = "102343992"  # present in the HSSD dataset this machine has mounted


def _make_topdown(navigable_slice=None) -> TopdownMap:
    grid = np.zeros((10, 10), dtype=bool)
    if navigable_slice:
        grid[navigable_slice] = True
    return TopdownMap(
        grid=grid, meters_per_pixel=1.0,
        bounds_min=np.array([0.0, 0.0, 0.0]),
        bounds_max=np.array([10.0, 3.0, 10.0]),
        height=0.0,
    )


def test_world_to_pixel_uses_bounds_min_and_meters_per_pixel():
    tm = _make_topdown()
    assert tm.world_to_pixel(x=3.0, z=5.0) == (5, 3)  # row=z, col=x


def test_world_to_pixel_respects_nonzero_bounds_min():
    grid = np.zeros((10, 10), dtype=bool)
    tm = TopdownMap(grid=grid, meters_per_pixel=1.0,
                    bounds_min=np.array([-5.0, 0.0, -5.0]),
                    bounds_max=np.array([5.0, 3.0, 5.0]), height=0.0)
    assert tm.world_to_pixel(x=0.0, z=0.0) == (5, 5)


def test_is_navigable_at_true_on_exact_cell():
    tm = _make_topdown(navigable_slice=(5, 5))
    assert tm.is_navigable_at(x=5.0, z=5.0, radius_px=0)


def test_is_navigable_at_false_when_cell_and_neighbors_not_navigable():
    tm = _make_topdown()  # all False
    assert not tm.is_navigable_at(x=5.0, z=5.0, radius_px=1)


def test_is_navigable_at_true_within_radius():
    tm = _make_topdown(navigable_slice=(5, 6))  # navigable one cell over
    assert tm.is_navigable_at(x=5.0, z=5.0, radius_px=1)
    assert not tm.is_navigable_at(x=5.0, z=5.0, radius_px=0)


def test_is_navigable_at_out_of_bounds_is_false():
    tm = _make_topdown()
    assert not tm.is_navigable_at(x=1000.0, z=1000.0, radius_px=1)


def test_anchor_world_positions_returns_real_scene_data():
    positions = anchor_world_positions(_REAL_SCENE)
    assert positions  # scene has at least some furniture
    for slot, pos in positions.items():
        assert len(pos) == 3
        assert all(isinstance(v, float) for v in pos)


def test_anchor_world_positions_only_includes_known_slots_or_stateful_categories():
    from dynamic_home_eqa.env.deltas import SLOT_ANCHORS
    from dynamic_home_eqa.env.inventory import STATEFUL_FURNITURE
    positions = anchor_world_positions(_REAL_SCENE)
    # Keys are either a real SLOT_ANCHORS slot, or a bare STATEFUL_FURNITURE
    # category name (M3: state-change dynamics — e.g. "fridge", the real
    # anchor a state question's resense targets, not a location slot).
    assert set(positions.keys()) <= set(SLOT_ANCHORS.keys()) | set(STATEFUL_FURNITURE.keys())


def test_anchor_world_positions_includes_present_stateful_furniture():
    from dynamic_home_eqa.env.inventory import STATEFUL_FURNITURE
    positions = anchor_world_positions(_REAL_SCENE)
    present_stateful = set(positions.keys()) & set(STATEFUL_FURNITURE.keys())
    assert present_stateful, "expected at least one stateful-furniture category in this real scene"


def test_room_centroids_returns_canonical_room_keys():
    from dynamic_home_eqa.rooms import CANONICAL_ROOMS
    centroids = room_centroids(_REAL_SCENE)
    assert set(centroids.keys()) <= set(CANONICAL_ROOMS)
    for room, (x, z) in centroids.items():
        assert isinstance(x, float) and isinstance(z, float)


def test_room_centroids_empty_for_unknown_scene():
    assert room_centroids("nonexistent_scene_id_xyz") == {}


def test_room_centroids_picks_one_real_region_not_a_cross_floor_average():
    # Scene 102343992 is multi-story: "bedroom" matches regions on both
    # floor_height=0.0 (bedroom.004) and floor_height=2.5 (bedroom, .001-.003).
    # The centroid must equal one real region's own center, not a blended
    # point that falls between floors (which is what a naive mean across
    # all matches produces, and which snapped to NaN on the real navmesh —
    # the bug this test pins).
    from dynamic_home_eqa.generation.regions import load_scene_regions
    from dynamic_home_eqa.rooms import rooms_match

    scene_regions = load_scene_regions(_REAL_SCENE)
    bedroom_regions = [r for r in scene_regions.regions if rooms_match(r.normalised, "bedroom")]
    assert len(bedroom_regions) > 1  # confirms this scene actually exercises the bug

    real_centers = {
        (round((r.min_bounds[0] + r.max_bounds[0]) / 2, 3),
         round((r.min_bounds[2] + r.max_bounds[2]) / 2, 3))
        for r in bedroom_regions
    }
    centroids = room_centroids(_REAL_SCENE)
    got = (round(centroids["bedroom"][0], 3), round(centroids["bedroom"][1], 3))
    assert got in real_centers


# ---------------------------------------------------------------------------
# habitat_sim-dependent tests — skipped (not the whole module) when
# habitat_sim isn't importable, since importorskip at module level would
# skip the plain-Python tests above too.
# ---------------------------------------------------------------------------

def _has_habitat_sim() -> bool:
    try:
        import habitat_sim  # noqa: F401
        return True
    except ImportError:
        return False


_needs_habitat_sim = pytest.mark.skipif(
    not _has_habitat_sim(), reason="habitat_sim not installed in this environment"
)


@_needs_habitat_sim
def test_load_topdown_map_real_scene():
    from dynamic_home_eqa.topdown_map import load_topdown_map
    tm = load_topdown_map(_REAL_SCENE)
    assert tm.grid.ndim == 2
    assert tm.grid.dtype == bool
    assert 0.0 < tm.grid.mean() < 1.0  # neither empty nor fully navigable


@_needs_habitat_sim
def test_check_anchor_sanity_real_scene():
    from dynamic_home_eqa.topdown_map import check_anchor_sanity

    # "fridge" (M3: state-change dynamics) genuinely fails navmesh-adjacency
    # in this scene — likely recessed into cabinetry with no adjacent floor
    # space — confirmed by direct inspection, not a registration bug (see
    # test_sensor.py's _NO_VIEWPOINT_WITHIN_RANGE and experiment_config.py's
    # FROZEN_STATE_LABELS, which excludes "fridge_1" for exactly this reason).
    _KNOWN_NON_ADJACENT = {"fridge"}

    result = check_anchor_sanity(_REAL_SCENE)
    assert result.checked > 0
    unexpected_offenders = set(result.offenders) - _KNOWN_NON_ADJACENT
    assert not unexpected_offenders, f"anchors failing navmesh-adjacency check: {unexpected_offenders}"
