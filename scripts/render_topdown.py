#!/usr/bin/env python3
"""
render_topdown.py — geometry-faithful top-down replay animation.

Renders one generated day (scene, profile, variant) as an animation over the
scene's real navmesh: object markers colored by category at their current
anchor, occupant markers at room centroids from the activity trace, a clock,
and event flashes on moves. This is the spatial-realism companion to the
schematic (non-geometric) HTML replay viewer — it also doubles as an
anchor-sanity check (topdown_map.check_anchor_sanity): every SLOT_ANCHORS
position this scene resolves must land on or near navigable space, or the
render (and anything built on the same position data) can't be trusted.

Requires habitat_sim — not installed in the environment this repo's LLM
generation pipeline normally runs in. Use a conda env that has it (e.g.
explore-eqa/fine-eqa on this machine):

Usage:
    /path/to/env-with-habitat-sim/bin/python3 scripts/render_topdown.py \\
        --scene 102343992 --profile family_with_kids --fps 4 \\
        --hours-per-second 0.5 --out day.mp4

    ... --variant 1 --gif --out day.gif    # gif fallback if ffmpeg is unavailable
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT   = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from dynamic_home_eqa.rooms import CANONICAL_ROOMS, slot_room
from dynamic_home_eqa.topdown_map import (
    anchor_world_positions,
    check_anchor_sanity,
    load_topdown_map,
    room_centroids,
)

_DAY_START, _DAY_END = 0.0, 24.0


def _category_colors(categories: list[str]) -> dict[str, tuple]:
    cmap = plt.get_cmap("tab20")
    cats = sorted(set(categories))
    return {cat: cmap(i % 20) for i, cat in enumerate(cats)}


def _activity_at(activities: list[list], t: float) -> tuple[str, str] | None:
    """(activity, room) active at hour t from a replay-format activity list
    ([activity, room, start, end] tuples) — handles overnight wraparound."""
    for act, room, start, end in activities:
        if end < start:
            if t >= start or t < end:
                return act, room
        else:
            if start <= t < end:
                return act, room
    return None


def _label_position(
    label_slot: str,
    label_jitter: tuple[float, float],
    anchors: dict[str, tuple],
    centroids: dict[str, tuple],
) -> tuple[float, float] | None:
    """World (x, z) for a label currently at `label_slot`.

    Prefers a real per-scene anchor position (anchor_world_positions); falls
    back to the slot's canonical room's centroid (jittered slightly so
    several objects in the same room don't render as one overlapping dot) —
    this is a schematic placement for slots with no hand-authored
    SLOT_ANCHORS entry (e.g. synthesized "bathroom.sink"-style slots), not a
    claim of the object's exact real position.
    """
    if label_slot in anchors:
        x, _, z = anchors[label_slot]
        return x, z
    room = slot_room(label_slot)
    if room in centroids:
        cx, cz = centroids[room]
        jx, jz = label_jitter
        return cx + jx, cz + jz
    return None


def render_day(
    replay: dict,
    topdown,
    anchors: dict[str, tuple],
    centroids: dict[str, tuple[float, float]],
    fps: int,
    hours_per_second: float,
    out_path: pathlib.Path,
    gif: bool,
) -> None:
    changes    = replay["changes"]     # [t, label, type, from, to, reason, mover]
    occupants  = replay["occupants"]   # [{name, age_band, activities}]
    categories = {c[1].rsplit("_", 1)[0] if "_" in c[1] else c[1] for c in changes}
    # object_category isn't in the flattened tuple; recover it from the
    # underlying manifest-shaped changes if present, else fall back to label.
    label_to_category = {}
    for c in changes:
        t, label, ctype, frm, to, reason, mover = c
        label_to_category.setdefault(label, label.rsplit("_", 1)[0])
    colors = _category_colors(list(label_to_category.values()))

    duration_sim_hours = _DAY_END - _DAY_START
    n_frames = max(1, int(duration_sim_hours / hours_per_second * fps))

    rng = np.random.default_rng(0)
    jitters = {
        label: (rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4))
        for label in label_to_category
    }

    fig, ax = plt.subplots(figsize=(8, 8))
    extent = [
        topdown.bounds_min[0], topdown.bounds_max[0],
        topdown.bounds_max[2], topdown.bounds_min[2],  # z inverted for image display
    ]
    ax.imshow(topdown.grid, cmap="gray", extent=extent, origin="upper", alpha=0.6)
    ax.set_xlim(topdown.bounds_min[0], topdown.bounds_max[0])
    ax.set_ylim(topdown.bounds_max[2], topdown.bounds_min[2])
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])

    clock_text = ax.text(0.02, 0.98, "", transform=ax.transAxes,
                         va="top", ha="left", fontsize=14, color="black",
                         bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"))
    object_scatter = ax.scatter([], [], s=60, zorder=3)
    flash_scatter  = ax.scatter([], [], s=220, facecolors="none",
                                edgecolors="red", linewidths=2, zorder=4)
    occ_scatter    = ax.scatter([], [], s=140, marker="*", c="blue", zorder=5)
    occ_labels     = [ax.text(0, 0, "", fontsize=8, color="blue", zorder=5) for _ in occupants]

    legend_handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=colors[cat],
                   markersize=8, label=cat)
        for cat in sorted(set(label_to_category.values()))
    ]
    ax.legend(handles=legend_handles, loc="upper right", fontsize=7, framealpha=0.7)

    def _frame(i):
        t = _DAY_START + (i / n_frames) * duration_sim_hours

        current_slot: dict[str, str] = {}
        for c in changes:
            ct, label, ctype, frm, to, reason, mover = c
            if ct <= t:
                current_slot[label] = to

        xs, zs, cs, flash_xs, flash_zs = [], [], [], [], []
        for label, slot in current_slot.items():
            pos = _label_position(slot, jitters.get(label, (0.0, 0.0)), anchors, centroids)
            if pos is None:
                continue
            x, z = pos
            xs.append(x); zs.append(z)
            cs.append(colors.get(label_to_category.get(label, ""), (0, 0, 0, 1)))

        for c in changes:
            ct, label, ctype, frm, to, reason, mover = c
            if abs(ct - t) <= (duration_sim_hours / n_frames):
                pos = _label_position(to, jitters.get(label, (0.0, 0.0)), anchors, centroids)
                if pos is not None:
                    flash_xs.append(pos[0]); flash_zs.append(pos[1])

        object_scatter.set_offsets(np.c_[xs, zs] if xs else np.empty((0, 2)))
        object_scatter.set_color(cs if cs else None)
        flash_scatter.set_offsets(np.c_[flash_xs, flash_zs] if flash_xs else np.empty((0, 2)))

        occ_xs, occ_zs = [], []
        for occ, label_text in zip(occupants, occ_labels):
            hit = _activity_at(occ.get("activities", []), t)
            if hit is not None and hit[1] in centroids:
                cx, cz = centroids[hit[1]]
                occ_xs.append(cx); occ_zs.append(cz)
                label_text.set_position((cx, cz))
                label_text.set_text(occ["name"])
            else:
                label_text.set_text("")
        occ_scatter.set_offsets(np.c_[occ_xs, occ_zs] if occ_xs else np.empty((0, 2)))

        hh, mm = int(t) % 24, int((t % 1) * 60)
        clock_text.set_text(f"{hh:02d}:{mm:02d}")
        return object_scatter, flash_scatter, occ_scatter, clock_text, *occ_labels

    anim = animation.FuncAnimation(fig, _frame, frames=n_frames, interval=1000 / fps, blit=False)

    if gif:
        anim.save(str(out_path), writer=animation.PillowWriter(fps=fps))
    else:
        anim.save(str(out_path), writer=animation.FFMpegWriter(fps=fps))
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scene", required=True, help="HSSD scene id, e.g. 102343992")
    ap.add_argument("--profile", required=True, help="Household profile, e.g. family_with_kids")
    ap.add_argument("--variant", type=int, default=0, help="Household variant (default: 0)")
    ap.add_argument("--out-dir", default=str(_DYNAMIC_EQA / "generation_out"),
                    help="Where to find <scene>_<profile>[_vN]/replay.json (default: generation_out/)")
    ap.add_argument("--fps", type=int, default=4)
    ap.add_argument("--hours-per-second", type=float, default=0.5,
                    help="Simulated hours per real second of video (default: 0.5)")
    ap.add_argument("--out", default="day_topdown.mp4")
    ap.add_argument("--gif", action="store_true", help="Write a GIF (PillowWriter) instead of mp4 (ffmpeg)")
    ap.add_argument("--meters-per-pixel", type=float, default=0.05)
    ap.add_argument("--skip-anchor-check", action="store_true",
                    help="Skip the anchor-sanity check (default: on; fails loudly if any "
                         "resolved anchor doesn't land on/near navigable space)")
    args = ap.parse_args()

    folder = f"{args.scene}_{args.profile}" + (f"_v{args.variant}" if args.variant else "")
    replay_path = pathlib.Path(args.out_dir) / folder / "replay.json"
    if not replay_path.exists():
        sys.exit(f"No replay.json at {replay_path} — run scripts/gen_dataset.py first.")
    replay = json.loads(replay_path.read_text())

    print(f"Loading scene {args.scene} into habitat_sim (navmesh/pathfinder only, no rendering)...")
    topdown = load_topdown_map(args.scene, meters_per_pixel=args.meters_per_pixel)

    if not args.skip_anchor_check:
        sanity = check_anchor_sanity(args.scene, topdown=topdown)
        print(f"Anchor sanity: {sanity.summary()}")
        if not sanity.ok:
            sys.exit(f"Anchor(s) failing navmesh-adjacency check: {sanity.offenders}")

    anchors   = anchor_world_positions(args.scene)
    centroids = room_centroids(args.scene)
    if not centroids:
        print("Warning: no room centroids resolved for this scene (no HSSD region "
              "annotations?) — occupant markers will not render.")

    out_path = pathlib.Path(args.out)
    print(f"Rendering {folder} → {out_path} "
          f"(fps={args.fps}, {args.hours_per_second} sim-h/s, {'gif' if args.gif else 'mp4'})...")
    render_day(replay, topdown, anchors, centroids, args.fps, args.hours_per_second, out_path, args.gif)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
