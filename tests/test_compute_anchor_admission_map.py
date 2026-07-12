"""
One live integration test for scripts/compute_anchor_admission_map.py —
requires habitat-lab (not just habitat_sim), same convention as
tests/test_realism_render_job_live.py's _needs_habitat_lab: capacity
estimation reuses build_realized_day.py's resolve_furniture_receptacles
(habitat-lab's find_receptacles), so this only runs for real under
an env with habitat-lab (dynamic_eqa). Skipped, not failed, otherwise.
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


def _has_habitat_lab() -> bool:
    try:
        import habitat  # noqa: F401
        return True
    except ImportError:
        return False


pytestmark = pytest.mark.skipif(
    not _has_habitat_sim(), reason="habitat_sim not installed in this environment"
)
_needs_habitat_lab = pytest.mark.skipif(
    not _has_habitat_lab(), reason="habitat-lab not installed in this environment"
)


@_needs_habitat_lab
def test_compute_anchor_admission_map_on_real_scene():
    from dynamic_home_eqa.embodied.config import NavMeshConfig
    from dynamic_home_eqa.embodied.reachability import make_sim
    from dynamic_home_eqa.scripts.compute_anchor_admission_map import compute_anchor_admission_map
    from dynamic_home_eqa.scripts.build_realized_day import classify_anchor
    from dynamic_home_eqa.topdown_map import anchor_world_positions

    sim = make_sim(_REAL_SCENE, NavMeshConfig())
    try:
        admission_map = compute_anchor_admission_map(_REAL_SCENE, sim)
    finally:
        sim.close()

    assert admission_map["scene_id"] == _REAL_SCENE

    # Key invariant vs. compute_sensability_map's approach: the map covers
    # every REAL census anchor, unpruned — including known-unreachable ones
    # (EmbodiedWorld._anchor_positions would have already silently dropped
    # them by this point).
    assert set(admission_map["anchors"]) == set(anchor_world_positions(_REAL_SCENE))

    # The tv-class navmesh-island finding this whole feature exists to
    # close, confirmed directly against real scene geometry, not assumed.
    assert admission_map["anchors"]["tv"]["reachable"] is False
    assert admission_map["anchors"]["tv"]["capacity"] is None

    for anchor, entry in admission_map["anchors"].items():
        kind, _cats = classify_anchor(anchor)
        if kind == "region":
            assert entry["capacity"] is None, f"{anchor!r} is a region anchor, must have no capacity"
        if entry["capacity"] is not None:
            assert entry["capacity"] > 0, f"{anchor!r} has a non-positive capacity"
            assert entry["capacity_source"] in ("receptacle", "synthetic")
        if not entry["reachable"]:
            assert entry["capacity"] is None, f"unreachable anchor {anchor!r} must have no capacity"
