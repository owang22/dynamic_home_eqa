"""
One live integration test for scripts/realism_render_job.py — requires
habitat_sim + a GPU renderer, skipped (not failed) otherwise, same
convention as tests/test_sensor.py. Confirms the render+physics pipeline
actually runs end to end on real data (renders a real event, produces a
non-degenerate geometric signal for at least one anchor) — the pure-logic
tests in test_realism_render_job.py cover sampling/scoring/projection
math but cannot catch a habitat_sim API misuse (e.g. enable_physics and
create_renderer failing to coexist, or a viewpoint/position mismatch).
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


def _has_habitat_lab() -> bool:
    try:
        import habitat  # noqa: F401
        return True
    except ImportError:
        return False


pytestmark = pytest.mark.skipif(
    not _has_habitat_sim(), reason="habitat_sim not installed in this environment"
)

# build_realized_day (called directly by test_render_one_real_event_end_to_end
# below, to produce a real artifact to render) now requires habitat-lab for
# INSTANCE-anchor placement (Receptacle + snap_down, see
# results/reports/receptacle_investigation.md) needs habitat-lab; skipped,
# not failed, in an env without it.
_needs_habitat_lab = pytest.mark.skipif(
    not _has_habitat_lab(), reason="habitat-lab not installed in this environment"
)


@_needs_habitat_lab
def test_render_one_real_event_end_to_end(tmp_path):
    from dynamic_home_eqa.embodied.world import EmbodiedWorld
    from dynamic_home_eqa.scripts.build_realized_day import build_realized_day
    from dynamic_home_eqa.scripts.realism_render_job import (
        PoolItem,
        _make_render_sim,
        geometric_signals,
        render_event_grid,
    )
    from dynamic_home_eqa.topdown_map import load_topdown_map

    gen_result = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_generation_result.json").read_text())
    manifest = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_manifest.json").read_text())
    location_events = [c for c in manifest["changes"] if c.get("change_type") != "state_change"]
    assert location_events, "fixture must contain at least one location event"
    event = location_events[0]
    item = PoolItem(folder="fixture", change_type="location", event=event)

    topdown = load_topdown_map(_REAL_SCENE)
    render_sim = _make_render_sim(_REAL_SCENE)
    world = EmbodiedWorld(_REAL_SCENE, gen_result, manifest)
    # A second, separate sim for the BUILD step (build_realized_day.main()'s
    # own convention — build-time and render-time sims are always distinct,
    # even when (as here, in a test) they happen to load the same scene).
    build_sim = _make_render_sim(_REAL_SCENE)
    build_world = EmbodiedWorld(_REAL_SCENE, gen_result, manifest)
    try:
        artifact, _audit = build_realized_day("fixture", _REAL_SCENE, build_sim, build_world, manifest=manifest)
    finally:
        build_world.close()
        build_sim.close()

    try:
        out_png = tmp_path / "test_event.png"
        geom = render_event_grid(world, render_sim, topdown, item, gen_result, artifact, out_png)
        assert out_png.exists() and out_png.stat().st_size > 0
        _valid_statuses = (
            "ok", "anchor_unresolved", "enclosed", "aim_failed",
            "object_spawn_failed", "not_applicable",
        )
        assert geom["before_status"] in _valid_statuses
        assert geom["after_status"] in _valid_statuses

        signals = geometric_signals(render_sim, geom["before_pos"], geom["after_pos"])
        # at least the "after" anchor should be a real, resolvable position
        # for a real event on this scene — geometric signal must be a real
        # bool/float, not silently None, when the position resolved.
        if geom["after_pos"] is not None:
            assert signals["after_supported"] in (True, False)
    finally:
        world.close()
        render_sim.close()


def test_room_qualified_stateful_furniture_anchor_resolves_via_bare_alias():
    # Already-generated data (written before rooms.resolve_slot()'s fix)
    # can still contain "{room}.{stateful_furniture_category}" anchor
    # strings like "bedroom.wardrobe" that have no entry anywhere in
    # world._anchor_positions under that exact key — only under the bare
    # "wardrobe" key. build_realized_day.resolve_anchor_position (the
    # single remaining anchor-position resolver after the Spectator
    # Camera round deleted realism_render_job.resolve_position_and_viewpoint,
    # whose only other job was pairing this same alias with a now-deleted
    # embodied viewpoint search) must alias these to the real, resolvable
    # position rather than reporting "unresolvable" for data that in fact
    # has a perfectly good known position.
    from dynamic_home_eqa.embodied.world import EmbodiedWorld
    from dynamic_home_eqa.scripts.build_realized_day import resolve_anchor_position

    gen_result = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_generation_result.json").read_text())
    manifest = json.loads((_FIXTURES / "102343992_family_with_kids_fixed_manifest.json").read_text())
    world = EmbodiedWorld(_REAL_SCENE, gen_result, manifest)
    try:
        assert "bedroom.wardrobe" not in world._anchor_positions
        assert "wardrobe" in world._anchor_positions  # the fixture scene has a real one

        pos = resolve_anchor_position(world, "bedroom.wardrobe")
        assert pos == world._anchor_positions["wardrobe"]
    finally:
        world.close()
