#!/usr/bin/env python3
"""
asset_candidate_acceptance.py — mechanical (non-visual-judgment) accept/
reject pass over the Objaverse asset candidates for `keys`/`wallet`
(results/reports/asset_coverage.md's timeboxed asset-sourcing task).

Per candidate, in a real qualified scene, at a known anchor
(dining.table):
  (a) scale check — instanced AABB max extent within 20% of the category
      target (0.12m keys, 0.11m wallet).
  (b) mask predicate — the SAME instance-segmentation output-truth check
      scripts/realism_render_job.py's render_event_grid uses (see
      evaluate_object_mask): the object's own semantic mask must be
      non-empty, 0.5%-40% of the frame, and centered in the frame.
      Supersedes the earlier whole-frame pixel-diff check (deleted from
      realism_render_job.py — see the round's standing rule: a check that
      fails at scale is a finding, not a calibration target, and the
      pixel-diff check itself was the guard that got wrongly widened in
      an earlier round instead of investigated).
  (c) support check — embodied/placement_check.py's real collision check;
      the object must land supported, not embedded, at the standard
      raycast-plus-bounding-box placement.

Survivors get one render saved to results/reports/asset_candidates/ for
owner review — this script does NOT pick a winner; the owner chooses
from the survivor renders.
"""
from __future__ import annotations

import argparse
import json
import pathlib

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.sensor import spectator_viewpoint
from dynamic_home_eqa.scripts.build_realized_day import get_world_aabb, resolve_anchor_position
from dynamic_home_eqa.scripts.realism_render_job import (
    _SPAWNED_OBJECT_SEMANTIC_ID,
    _make_render_sim,
    capture_rgb_semantic_and_basis,
    evaluate_object_mask,
    project_point,
    world_aabb_centroid,
)

_ASSET_DIR = _DYNAMIC_EQA / "data" / "objects" / "external_props"
_OUT_DIR = _DYNAMIC_EQA / "results" / "reports" / "asset_candidates"
_CATEGORY_TARGET_M = {"key": 0.12, "wallet": 0.11, "phone": 0.15}
_SCALE_TOLERANCE = 0.20


def spawn_candidate(sim, uid: str):
    """Loads and spawns one external_props candidate by UID. Returns the
    rigid object (or None if the template failed to load/spawn)."""
    config_path = _ASSET_DIR / "configs" / f"{uid}.object_config.json"
    obj_attr_mgr = sim.get_object_template_manager()
    if not obj_attr_mgr.get_template_handles(uid):
        obj_attr_mgr.load_object_configs(str(config_path))
    templates = obj_attr_mgr.get_template_handles(uid)
    if not templates:
        return None
    rigid_mgr = sim.get_rigid_object_manager()
    return rigid_mgr.add_object_by_template_handle(templates[0])


def check_candidate(sim, world, topdown, uid: str, category: str, anchor: str) -> dict:
    """Runs checks (a)/(b)/(c) for one candidate at `anchor`. Returns a
    result dict with each sub-check's pass/fail and the raw measurements
    — never raises, a failed load/spawn is itself a rejection reason."""
    import habitat_sim
    import magnum as mn

    from dynamic_home_eqa.embodied.placement_check import check_placement
    from dynamic_home_eqa.scripts.build_realized_day import resolve_surface_height

    result = {"uid": uid, "category": category, "anchor": anchor}

    pos = resolve_anchor_position(world, anchor)
    if pos is None:
        result["reject_reason"] = "anchor_unresolved"
        return result

    obj = spawn_candidate(sim, uid)
    if obj is None:
        result["reject_reason"] = "spawn_failed"
        return result

    bb = obj.root_scene_node.cumulative_bb
    max_extent = max(bb.size().x, bb.size().y, bb.size().z)
    target = _CATEGORY_TARGET_M[category]
    scale_ok = abs(max_extent - target) / target <= _SCALE_TOLERANCE
    result["scale_check"] = {"max_extent_m": max_extent, "target_m": target, "passed": scale_ok}

    surface_y = resolve_surface_height(sim, pos)
    surface_resolved = surface_y is not None
    if surface_y is None:
        surface_y = pos[1]
    obj.translation = mn.Vector3(pos[0], surface_y - bb.min[1], pos[2])
    obj.motion_type = habitat_sim.physics.MotionType.KINEMATIC

    # Spectator Camera round: the camera search is now the SAME
    # embodied.sensor.spectator_viewpoint hemisphere search production
    # rendering uses (scripts/realism_render_job.render_event_grid) — a
    # candidate that only clears the mask predicate from a real production
    # camera should be accepted, and one that can't should be rejected,
    # not judged against a since-deleted, differently-behaved search.
    aabb = get_world_aabb(obj)
    (min_x, min_y, min_z), (max_x, max_y, max_z) = aabb
    obj_max_extent = max(max_x - min_x, max_y - min_y, max_z - min_z)
    vp = spectator_viewpoint(sim, aabb, obj_max_extent)
    if vp is None:
        result["reject_reason"] = "enclosed"
        remove_candidate(sim, obj)
        return result

    # Single source of truth for position (same mechanism
    # realism_render_job.render_event_grid uses) — camera aims at the
    # object's own post-spawn world AABB centroid, not the raw anchor.
    actual_pos = world_aabb_centroid(obj)
    obj.semantic_id = _SPAWNED_OBJECT_SEMANTIC_ID
    # capture_rgb_semantic_and_basis adds the sensor's fixed +1.5m local
    # offset to whatever agent position it's given (see
    # render_event_grid's identical fix) — spectator_viewpoint already
    # returns the exact eye position, so that offset must be subtracted
    # back out first.
    agent_pos = (vp.camera_pos[0], vp.camera_pos[1] - 1.5, vp.camera_pos[2])
    rgb, semantic, eye, forward, right, up = capture_rgb_semantic_and_basis(sim, agent_pos, actual_pos)
    mask = semantic == _SPAWNED_OBJECT_SEMANTIC_ID
    anchor_px = project_point(eye, forward, right, up, pos)
    mask_passed, fail_reason, mask_info = evaluate_object_mask(mask, anchor_px)
    result["mask_check"] = {
        "area_px": mask_info["area_px"], "area_fraction": mask_info["area_fraction"],
        "fail_reason": None if mask_passed else fail_reason, "passed": mask_passed,
    }

    surface_pos = (pos[0], obj.translation[1] + bb.min[1], pos[2])
    placement = check_placement(sim, surface_pos)
    support_ok = placement.supported and not placement.embedded
    result["support_check"] = {
        "supported": placement.supported, "embedded": placement.embedded,
        "support_distance_m": placement.support_distance_m, "surface_resolved": surface_resolved,
        "passed": support_ok,
    }

    result["passed"] = scale_ok and mask_passed and support_ok

    if result["passed"]:
        _save_candidate_render(rgb, mask_info["centroid_px"], uid, category, result, topdown, pos)

    remove_candidate(sim, obj)
    return result


def remove_candidate(sim, obj) -> None:
    if obj is not None:
        sim.get_rigid_object_manager().remove_object_by_id(obj.object_id)


def _save_candidate_render(rgb, marker, uid: str, category: str, result: dict, topdown, pos) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(rgb)
    if marker is not None:
        axes[0].plot(marker[0], marker[1], "r*", markersize=20, markeredgecolor="white")
    axes[0].set_title(f"{category}: {uid[:12]}")
    axes[0].axis("off")

    axes[1].imshow(topdown.grid, cmap="gray", origin="lower")
    row, col = topdown.world_to_pixel(pos[0], pos[2])
    axes[1].plot(col, row, "r*", markersize=14)
    axes[1].set_title("top-down")
    axes[1].axis("off")

    sc = result["scale_check"]
    mc = result["mask_check"]
    fig.suptitle(
        f"scale: {sc['max_extent_m']:.3f}m (target {sc['target_m']:.2f}m)  "
        f"mask_area: {mc['area_px']}px ({mc['area_fraction']:.3%})  "
        f"supported: {result['support_check']['supported']}",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    fig.savefig(_OUT_DIR / f"{category}_{uid[:12]}.png", dpi=120, facecolor="white")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scene", default="102343992")
    ap.add_argument("--folder", default="102343992_family_with_kids")
    ap.add_argument("--anchor", default="dining.table")
    ap.add_argument("--mapping", default=str(_ASSET_DIR / "mapping.json"))
    args = ap.parse_args()

    from dynamic_home_eqa.embodied.world import EmbodiedWorld
    from dynamic_home_eqa.topdown_map import load_topdown_map

    out_dir = _DYNAMIC_EQA / "generation_out"
    gen_result = json.loads((out_dir / args.folder / "generation_result.json").read_text())
    manifest = json.loads((out_dir / args.folder / "manifest.json").read_text())
    mapping = json.loads(pathlib.Path(args.mapping).read_text())

    topdown = load_topdown_map(args.scene)
    sim = _make_render_sim(args.scene)
    world = EmbodiedWorld(args.scene, gen_result, manifest)
    results = []
    try:
        for row in mapping:
            r = check_candidate(sim, world, topdown, row["uid"], row["category"], args.anchor)
            results.append(r)
            status = "PASS" if r.get("passed") else f"REJECT ({r.get('reject_reason', 'failed a check')})"
            print(f"{row['category']:6s} {row['uid'][:12]}  {status}")
    finally:
        world.close()
        sim.close()

    report_path = _DYNAMIC_EQA / "results" / "reports" / "asset_candidates_result.json"
    report_path.write_text(json.dumps(results, indent=2, default=str))
    survivors = [r for r in results if r.get("passed")]
    print(f"\n{len(survivors)}/{len(results)} candidates passed. Renders: {_OUT_DIR}")
    print(f"Full result log: {report_path}")


if __name__ == "__main__":
    main()
