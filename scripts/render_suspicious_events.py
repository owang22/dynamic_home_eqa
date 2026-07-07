#!/usr/bin/env python3
"""
render_suspicious_events.py — Phase-adjacent realism-eval tooling
(parallel track, not Phase A/B): renders a before/after grid (egocentric
RGB + top-down, one row each) for the most suspicious change events in a
validated folder, ranked by a real suspicion score — not a uniform
sample, per the task's own instruction to surface the tail first.

Suspicion signals actually available in this data (confirmed by direct
inspection of a real manifest.json event: fields are t, label,
change_type, object_category, from_semantic, to_semantic, mover,
llm_claimed_from, reason, confidence, object_handle — no per-event
collision/occupancy or "capability" flag exists anywhere in the pipeline
today):
  - cross-room move (from_semantic's room != to_semantic's room)
  - rare category-anchor pairing (this (category, anchor) pair almost
    never occurs pool-wide — reuses generation_diversity_report.py's own
    folder discovery, not a second implementation of "which folders are
    valid")
  - low grounding confidence (the `confidence` field, when < 1.0)
  - ping-pong (the same label returns to a recently-left anchor)

"Collision/occupancy failure at anchor" and "capability-flagged" from
the original task list are NOT implemented — no per-event field carries
either signal in the current pipeline. Stated as a gap, not silently
dropped: `grounding_stats` in generation_result.json is an aggregate
summary (total/accepted/rejection-rate counts), not a per-event record,
so neither signal is reconstructable after the fact without changing the
generation pipeline itself to emit it.

Requires habitat_sim AND a renderer/GPU (create_renderer=True — unlike
every other habitat_sim consumer in this project, which stays sensorless
for performance). Run under explore-eqa or similar.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import defaultdict

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.embodied.sensor import viewpoint_for
from dynamic_home_eqa.embodied.world import EmbodiedWorld
from dynamic_home_eqa.rooms import slot_room
from dynamic_home_eqa.scripts.generation_diversity_report import discover_valid_folders
from dynamic_home_eqa.topdown_map import HSSD_DIR, load_topdown_map

_REPORTS_DIR = _DYNAMIC_EQA / "results" / "reports"
_RENDER_DIR = _REPORTS_DIR / "suspicious_events"
_DATASET_CONFIG = f"{HSSD_DIR}/hssd-hab-uncluttered.scene_dataset_config.json"


def pool_category_anchor_counts(out_dir: pathlib.Path, folders: list[str]) -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for folder in folders:
        manifest = json.loads((out_dir / folder / "manifest.json").read_text())
        for c in manifest["changes"]:
            if c.get("change_type") == "state_change":
                continue
            counts[(c["object_category"], c["to_semantic"])] += 1
    return counts


def score_events(changes: list[dict], category_anchor_counts: dict[tuple[str, str], int]) -> list[tuple[float, dict, list[str]]]:
    by_label: dict[str, list[dict]] = defaultdict(list)
    for c in changes:
        if c.get("change_type") != "state_change":
            by_label[c["label"]].append(c)
    for evs in by_label.values():
        evs.sort(key=lambda c: c["t"])

    scored = []
    for label, evs in by_label.items():
        for i, c in enumerate(evs):
            score = 0.0
            reasons = []
            from_room = slot_room(c["from_semantic"]) if c.get("from_semantic") else None
            to_room = slot_room(c["to_semantic"])
            if from_room and to_room and from_room != to_room:
                score += 1.0
                reasons.append(f"cross-room ({from_room}->{to_room})")
            freq = category_anchor_counts.get((c["object_category"], c["to_semantic"]), 0)
            if freq <= 2:
                score += 1.5
                reasons.append(f"rare pairing (seen {freq}x pool-wide)")
            confidence = c.get("confidence", 1.0)
            if confidence < 1.0:
                score += (1.0 - confidence) * 2.0
                reasons.append(f"low confidence ({confidence:.2f})")
            if i >= 2 and evs[i - 2].get("to_semantic") == c["to_semantic"]:
                score += 2.0
                reasons.append("ping-pong (returned to a recent prior anchor)")
            scored.append((score, c, reasons))
    scored.sort(key=lambda x: -x[0])
    return scored


def _make_render_sim(scene_id: str):
    import habitat_sim
    import numpy as np

    backend_cfg = habitat_sim.SimulatorConfiguration()
    backend_cfg.scene_dataset_config_file = _DATASET_CONFIG
    backend_cfg.scene_id = scene_id
    backend_cfg.enable_physics = False
    backend_cfg.create_renderer = True

    rgb_spec = habitat_sim.CameraSensorSpec()
    rgb_spec.uuid = "rgb"
    rgb_spec.sensor_type = habitat_sim.SensorType.COLOR
    rgb_spec.resolution = [360, 480]
    rgb_spec.position = np.array([0.0, 1.5, 0.0])  # eye height above agent origin

    agent_cfg = habitat_sim.agent.AgentConfiguration()
    agent_cfg.sensor_specifications = [rgb_spec]
    return habitat_sim.Simulator(habitat_sim.Configuration(backend_cfg, [agent_cfg]))


def capture_rgb_looking_at(sim, camera_pos: tuple[float, float, float], target_pos: tuple[float, float, float]):
    """Places the render agent at camera_pos, oriented to look directly at
    target_pos (a look-at construction, not a reuse of Pose.yaw_rad —
    sidesteps any ambiguity between this project's own yaw convention and
    habitat_sim's default agent-forward axis by computing the rotation
    directly from the two positions, verified empirically to produce
    non-degenerate images before being used for real)."""
    import numpy as np
    from habitat_sim.utils.common import quat_from_angle_axis

    dx = target_pos[0] - camera_pos[0]
    dz = target_pos[2] - camera_pos[2]
    yaw = np.arctan2(dx, -dz)  # habitat_sim default forward is -Z

    agent = sim.get_agent(0)
    state = sim.get_agent(0).get_state()
    state.position = np.array(camera_pos, dtype=np.float32)
    state.rotation = quat_from_angle_axis(yaw, np.array([0.0, 1.0, 0.0]))
    agent.set_state(state)
    obs = sim.get_sensor_observations()
    return obs["rgb"][:, :, :3]


def resolve_position_and_viewpoint(world: EmbodiedWorld, anchor: str):
    """viewpoint_for (embodied/sensor.py) only resolves furniture/slot-
    level anchors (world._anchor_positions, from topdown_map.
    anchor_world_positions) — confirmed by direct testing that a bare
    room name like "bedroom" (a real, legal to_semantic value this
    project's own generation produces) is NOT in that dict at all; room-
    level positions live in a SEPARATE dict, world._room_centroids
    (topdown_map.room_centroids), which EmbodiedWorld's own occupant-
    placement code already reads directly rather than through
    viewpoint_for. This is a real, pre-existing split in what
    viewpoint_for can resolve, not a bug introduced here — worked around
    locally (falling back to a snapped room centroid as both the
    "position" and the "viewpoint" for a room-level anchor) rather than
    changing viewpoint_for itself, which every real experiment in this
    project also calls and should not have its behavior altered for a
    parallel-track rendering tool's sake.

    Returns (position_xyz, viewpoint_pose) or (None, None) if truly
    unresolvable at either granularity.
    """
    pos = world._anchor_positions.get(anchor)
    if pos is not None:
        vp = viewpoint_for(world, anchor)
        return (pos, vp) if vp is not None else (None, None)

    centroid = world._room_centroids.get(anchor)
    if centroid is not None:
        cx, cz = centroid
        # topdown map's own "height" is a fixed slice near floor level
        # (see topdown_map.load_topdown_map) — good enough as a starting
        # Y for a 3D snap query; snap_to_navmesh finds the true navigable
        # point regardless of the exact Y offered.
        from dynamic_home_eqa.embodied.types import Pose
        snapped = world.snap_to_navmesh((cx, 0.0, cz))
        return snapped, Pose(*snapped, yaw_rad=0.0)

    return None, None


def render_event_grid(world: EmbodiedWorld, render_sim, topdown, event: dict, reasons: list[str], out_path: pathlib.Path) -> bool:
    """Returns True if both viewpoints were resolvable and the image was
    written; False (logged, not raised) if the anchor(s) involved have no
    valid viewpoint — a real, expected outcome for some anchors (outdoor/
    unresolvable slots), not a bug in this tool."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    to_anchor = event["to_semantic"]
    from_anchor = event.get("from_semantic")

    to_pos, after_vp = resolve_position_and_viewpoint(world, to_anchor)
    if from_anchor:
        from_pos, before_vp = resolve_position_and_viewpoint(world, from_anchor)
    else:
        from_pos, before_vp = to_pos, after_vp
    if to_pos is None or after_vp is None or from_pos is None or before_vp is None:
        return False

    rgb_before = capture_rgb_looking_at(render_sim, (before_vp.x, before_vp.y, before_vp.z), from_pos)
    rgb_after = capture_rgb_looking_at(render_sim, (after_vp.x, after_vp.y, after_vp.z), to_pos)

    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    axes[0][0].imshow(rgb_before); axes[0][0].set_title(f"BEFORE (egocentric): {from_anchor or 'n/a'}"); axes[0][0].axis("off")
    axes[0][1].imshow(rgb_after); axes[0][1].set_title(f"AFTER (egocentric): {to_anchor}"); axes[0][1].axis("off")

    for ax, pos, title in ((axes[1][0], from_pos, "BEFORE (top-down)"), (axes[1][1], to_pos, "AFTER (top-down)")):
        ax.imshow(topdown.grid, cmap="gray", origin="lower")
        row, col = topdown.world_to_pixel(pos[0], pos[2])
        ax.plot(col, row, "r*", markersize=18)
        ax.set_title(title)
        ax.axis("off")

    caption = (
        f'label={event["label"]}  category={event["object_category"]}  t={event["t"]:.2f}h\n'
        f'{from_anchor or "(new)"} -> {to_anchor}  mover={event.get("mover")}  confidence={event.get("confidence", 1.0):.2f}\n'
        f'reason: {event.get("reason", "")}\n'
        f'suspicion: {"; ".join(reasons) if reasons else "(none — included for balance)"}'
    )
    fig.suptitle(caption, fontsize=9, wrap=True)
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    fig.savefig(out_path, dpi=130, facecolor="white")
    plt.close(fig)
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scene", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--folder", required=True, help="e.g. 102343992_family_with_kids")
    ap.add_argument("--top-n", type=int, default=15)
    args = ap.parse_args()

    out_dir = _DYNAMIC_EQA / "generation_out"
    folders = discover_valid_folders(out_dir)
    print(f"{len(folders)} validated folders pool-wide for frequency counting")
    category_anchor_counts = pool_category_anchor_counts(out_dir, folders)

    manifest = json.loads((out_dir / args.folder / "manifest.json").read_text())
    generation_result = json.loads((out_dir / args.folder / "generation_result.json").read_text())
    scored = score_events(manifest["changes"], category_anchor_counts)
    top = scored[: args.top_n]
    print(f"Top {len(top)} most suspicious events in {args.folder} (of {len(scored)} total location events):")
    for score, event, reasons in top:
        print(f"  score={score:.2f}  {event['label']:15s} t={event['t']:.2f}  {'; '.join(reasons)}")

    world = EmbodiedWorld(args.scene, generation_result, manifest)
    topdown = load_topdown_map(args.scene)
    render_sim = _make_render_sim(args.scene)

    _RENDER_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    try:
        for rank, (score, event, reasons) in enumerate(top):
            out_path = _RENDER_DIR / f"{args.folder}_{event['label']}_t{event['t']:.2f}_rank{rank:02d}.png"
            ok = render_event_grid(world, render_sim, topdown, event, reasons, out_path)
            if ok:
                written += 1
                print(f"  wrote {out_path}")
            else:
                print(f"  SKIPPED (no resolvable viewpoint): {event['label']} t={event['t']:.2f}")
    finally:
        render_sim.close()
        world.close()

    print(f"\n{written}/{len(top)} events rendered to {_RENDER_DIR}")


if __name__ == "__main__":
    main()
