#!/usr/bin/env python3
"""
diagnose_navmesh_islands.py — D0 of the navmesh-connectivity phase.

Renders every navmesh island color-coded, overlaid with canonical room
polygons and per-scene anchor positions, plus a per-point indoor/outdoor
classification (a ray cast straight up from the navmesh surface; no hit
within _CEILING_RAY_MAX_M means open sky, i.e. outdoor). Companion table:
per island — id, area, vertex-derived centroid, vertical (y) extent, which
canonical rooms/anchors resolve onto it, and its sampled indoor fraction.

This exists to answer, before any navmesh recompute or portal is added:
  1. Which island is actually the house interior? A large island can still
     be mostly yard fused to a wing of the house — island area alone
     doesn't distinguish that from a genuine open-plan interior.
  2. Where do islands nearly touch (small horizontal gap, vertical
     offset)? Those are stair/threshold candidates for D1/D2.

Requires habitat_sim (enable_physics=True — cast_ray is a silent no-op
otherwise, see embodied/sensor.py's module docstring) — run from a conda
env that has it (e.g. explore-eqa).
"""
from __future__ import annotations

import argparse
import csv
import pathlib
from dataclasses import dataclass, field

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from dynamic_home_eqa.embodied.config import NavMeshConfig
from dynamic_home_eqa.generation.regions import load_scene_regions
from dynamic_home_eqa.rooms import CANONICAL_ROOMS, rooms_match
from dynamic_home_eqa.topdown_map import HSSD_DIR, anchor_world_positions, room_centroids

_DATASET_CONFIG = f"{HSSD_DIR}/hssd-hab-uncluttered.scene_dataset_config.json"

# A region's extrusion_height in the HSSD annotations is ~2.8 m and this
# scene has a second floor starting at 2.5 m, so 8 m clears any real
# ceiling from any floor while still being short enough that a ray with no
# hit at all is a reliable "open sky" signal, not just "ceiling is far".
_CEILING_RAY_MAX_M = 8.0
_MAX_CEILING_SAMPLES_PER_ISLAND = 150
_MIN_ISLAND_AREA_FOR_NEAR_TOUCH_M2 = 1.0
_TOP_K_NEAR_TOUCH_PAIRS = 12


@dataclass
class IslandStats:
    island_id: int
    area_m2: float
    n_verts: int
    centroid_x: float
    centroid_z: float
    y_min: float
    y_max: float
    indoor_fraction: float
    rooms: list[str] = field(default_factory=list)
    anchors: list[str] = field(default_factory=list)


def _make_sim(scene_id: str, navmesh: NavMeshConfig = NavMeshConfig()):
    import habitat_sim

    from dynamic_home_eqa.embodied.sensor import assert_enable_physics, raycast_self_test

    backend_cfg = habitat_sim.SimulatorConfiguration()
    backend_cfg.scene_dataset_config_file = _DATASET_CONFIG
    backend_cfg.scene_id = scene_id
    backend_cfg.enable_physics = True
    backend_cfg.create_renderer = False
    assert_enable_physics(backend_cfg)

    agent_cfg = habitat_sim.agent.AgentConfiguration()
    agent_cfg.sensor_specifications = []

    sim = habitat_sim.Simulator(habitat_sim.Configuration(backend_cfg, [agent_cfg]))
    # build_navmesh_vertices segfaults against an unloaded/uncomputed
    # pathfinder (confirmed directly) — always recompute first, same as
    # every other habitat_sim entry point in this package, and always with
    # our own NavMeshConfig (not whatever a pre-baked navmesh carries).
    settings = habitat_sim.NavMeshSettings()
    settings.agent_radius = navmesh.agent_radius
    settings.agent_height = navmesh.agent_height
    settings.agent_max_climb = navmesh.agent_max_climb
    settings.agent_max_slope = navmesh.agent_max_slope
    settings.cell_size = navmesh.cell_size
    settings.cell_height = navmesh.cell_height
    sim.recompute_navmesh(sim.pathfinder, settings)
    raycast_self_test(sim)
    return sim


def _is_indoor(sim, point: tuple[float, float, float], max_distance: float = _CEILING_RAY_MAX_M) -> bool:
    """True if a ray cast straight up from just above `point` hits scene
    geometry within max_distance — a ceiling overhead."""
    import habitat_sim
    import magnum as mn

    origin = mn.Vector3(point[0], point[1] + 0.05, point[2])
    ray = habitat_sim.geo.Ray(origin, mn.Vector3(0.0, 1.0, 0.0))
    result = sim.cast_ray(ray, max_distance=max_distance)
    return result.has_hits()


def _sample_indices(n: int, max_samples: int) -> list[int]:
    if n <= max_samples:
        return list(range(n))
    stride = n / max_samples
    return sorted({int(i * stride) for i in range(max_samples)})


def _island_vertices(pf, island_id: int) -> np.ndarray:
    verts = pf.build_navmesh_vertices(island_id)
    return np.array(verts) if verts else np.empty((0, 3))


def collect_island_stats(
    sim, scene_id: str, verts_by_island: dict[int, np.ndarray]
) -> tuple[list[IslandStats], list[tuple[float, float, float]]]:
    pf = sim.pathfinder
    anchors = anchor_world_positions(scene_id)
    centroids = room_centroids(scene_id)

    anchor_island = {slot: pf.get_island(list(pos)) for slot, pos in anchors.items()}
    room_island = {
        room: pf.get_island(list(pf.snap_point([x, 0.1, z])))
        for room, (x, z) in centroids.items()
    }

    stats: list[IslandStats] = []
    outdoor_points: list[tuple[float, float, float]] = []
    for island_id, verts in sorted(verts_by_island.items()):
        if len(verts) == 0:
            continue
        xs, ys, zs = verts[:, 0], verts[:, 1], verts[:, 2]

        sample_idx = _sample_indices(len(verts), _MAX_CEILING_SAMPLES_PER_ISLAND)
        n_indoor = 0
        for j in sample_idx:
            pt = (float(xs[j]), float(ys[j]), float(zs[j]))
            if _is_indoor(sim, pt):
                n_indoor += 1
            else:
                outdoor_points.append(pt)
        indoor_fraction = n_indoor / len(sample_idx) if sample_idx else 0.0

        stats.append(IslandStats(
            island_id=island_id,
            area_m2=pf.island_area(island_id),
            n_verts=len(verts),
            centroid_x=float(xs.mean()),
            centroid_z=float(zs.mean()),
            y_min=float(ys.min()),
            y_max=float(ys.max()),
            indoor_fraction=indoor_fraction,
            rooms=sorted(r for r, isl in room_island.items() if isl == island_id),
            anchors=sorted(a for a, isl in anchor_island.items() if isl == island_id),
        ))
    return stats, outdoor_points


def nearest_pairs(
    verts_by_island: dict[int, np.ndarray],
    stats: list[IslandStats],
    min_area_m2: float = _MIN_ISLAND_AREA_FOR_NEAR_TOUCH_M2,
    top_k: int = _TOP_K_NEAR_TOUCH_PAIRS,
) -> list[tuple]:
    """Closest pair of navmesh vertices between every pair of islands whose
    area clears min_area_m2 (skips negligible geometry slivers) — a small
    horizontal gap with a vertical (y) offset is a stair/threshold
    candidate; a small gap with near-zero y offset suggests the recompute
    parameters simply pinched off a real doorway."""
    from scipy.spatial import cKDTree

    real_ids = [s.island_id for s in stats if s.area_m2 >= min_area_m2]
    trees = {i: cKDTree(verts_by_island[i]) for i in real_ids}

    pairs = []
    for a_idx in range(len(real_ids)):
        for b_idx in range(a_idx + 1, len(real_ids)):
            a, b = real_ids[a_idx], real_ids[b_idx]
            va = verts_by_island[a]
            dists, idxs = trees[b].query(va)
            k = int(np.argmin(dists))
            gap = float(dists[k])
            pa, pb = va[k], verts_by_island[b][idxs[k]]
            dxz = float(np.hypot(pa[0] - pb[0], pa[2] - pb[2]))
            dy = float(abs(pa[1] - pb[1]))
            pairs.append((gap, a, b, dxz, dy, tuple(round(float(v), 2) for v in pa),
                          tuple(round(float(v), 2) for v in pb)))
    pairs.sort(key=lambda p: p[0])
    return pairs[:top_k]


def print_table(stats: list[IslandStats]) -> None:
    print(f"{'id':>3} {'area_m2':>9} {'y_range':>13} {'indoor':>7}  {'rooms':<32} anchors")
    for s in sorted(stats, key=lambda s: -s.area_m2):
        yr = f"{s.y_min:.2f}-{s.y_max:.2f}"
        print(f"{s.island_id:>3} {s.area_m2:>9.1f} {yr:>13} {s.indoor_fraction:>6.0%}  "
              f"{','.join(s.rooms):<32} {','.join(s.anchors)}")


def print_near_touch(pairs: list[tuple]) -> None:
    print("\nNearest island pairs (real islands only, sorted by gap):")
    for gap, a, b, dxz, dy, pa, pb in pairs:
        print(f"  island {a:>2} <-> island {b:>2}: gap={gap:5.2f}m  dxz={dxz:5.2f}m  "
              f"dy={dy:5.2f}m  pt_a={pa}  pt_b={pb}")


def write_csv(stats: list[IslandStats], out_csv: pathlib.Path) -> None:
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["island_id", "area_m2", "n_verts", "centroid_x", "centroid_z",
                          "y_min", "y_max", "indoor_fraction", "rooms", "anchors"])
        for s in sorted(stats, key=lambda s: -s.area_m2):
            writer.writerow([s.island_id, f"{s.area_m2:.2f}", s.n_verts,
                              f"{s.centroid_x:.2f}", f"{s.centroid_z:.2f}",
                              f"{s.y_min:.2f}", f"{s.y_max:.2f}", f"{s.indoor_fraction:.2f}",
                              ";".join(s.rooms), ";".join(s.anchors)])


def render(
    scene_id: str,
    stats: list[IslandStats],
    verts_by_island: dict[int, np.ndarray],
    outdoor_points: list[tuple[float, float, float]],
    out_png: pathlib.Path,
) -> None:
    fig, ax = plt.subplots(figsize=(11, 11))
    cmap = plt.get_cmap("tab20")

    for s in stats:
        verts = verts_by_island[s.island_id]
        ax.scatter(verts[:, 0], verts[:, 2], s=5, color=cmap(s.island_id % 20),
                   label=f"island {s.island_id} ({s.area_m2:.0f} m²)", zorder=2)
        ax.annotate(str(s.island_id), (s.centroid_x, s.centroid_z), fontsize=9,
                    fontweight="bold", ha="center", va="center", color="black",
                    bbox=dict(boxstyle="circle", fc="white", ec="black", alpha=0.75), zorder=4)

    if outdoor_points:
        pts = np.array(outdoor_points)
        ax.scatter(pts[:, 0], pts[:, 2], s=22, marker="x", color="red", linewidths=1.1,
                   label="outdoor (no ceiling)", zorder=5)

    regions = load_scene_regions(scene_id)
    if regions is not None:
        for room in CANONICAL_ROOMS:
            for r in regions.regions:
                if not rooms_match(r.normalised, room) or len(r.poly_loop) < 3:
                    continue
                poly = np.array(r.poly_loop + [r.poly_loop[0]])
                ax.plot(poly[:, 0], poly[:, 1], color="black", linewidth=1.0, alpha=0.6, zorder=3)
                cx, cz = poly[:-1, 0].mean(), poly[:-1, 1].mean()
                ax.text(cx, cz, room, fontsize=7, color="black", ha="center", va="center",
                        style="italic", alpha=0.85, zorder=3)

    anchors = anchor_world_positions(scene_id)
    for slot, (x, _y, z) in anchors.items():
        ax.scatter(x, z, s=45, marker="^", color="blue", zorder=6)
        ax.annotate(slot, (x, z), fontsize=6, color="blue", xytext=(3, 3),
                    textcoords="offset points", zorder=6)

    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("z (m)")
    ax.set_title(f"Navmesh islands — scene {scene_id}\n"
                 f"(red x = no ceiling within {_CEILING_RAY_MAX_M:.0f} m, i.e. outdoor)")
    ax.legend(loc="upper left", fontsize=6, framealpha=0.7, ncol=2)
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scene", default="102343992")
    ap.add_argument("--out-dir", default=str(_DYNAMIC_EQA / "results" / "diagnostics"))
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / f"navmesh_islands_{args.scene}.png"
    csv_path = out_dir / f"navmesh_islands_{args.scene}.csv"

    print(f"Loading scene {args.scene} into habitat_sim (enable_physics=True for cast_ray)...")
    sim = _make_sim(args.scene)
    try:
        pf = sim.pathfinder
        print(f"num_islands: {pf.num_islands}")
        verts_by_island = {i: _island_vertices(pf, i) for i in range(pf.num_islands)}

        stats, outdoor_points = collect_island_stats(sim, args.scene, verts_by_island)
        pairs = nearest_pairs(verts_by_island, stats)

        print_table(stats)
        print_near_touch(pairs)
        write_csv(stats, csv_path)
        render(args.scene, stats, verts_by_island, outdoor_points, png_path)
    finally:
        sim.close()

    print(f"\nWrote {png_path}\nWrote {csv_path}")


if __name__ == "__main__":
    main()
