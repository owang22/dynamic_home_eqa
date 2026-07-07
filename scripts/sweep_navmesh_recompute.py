#!/usr/bin/env python3
"""
sweep_navmesh_recompute.py — D1 of the navmesh-connectivity phase.

D0 found the interior of scene 102343992 fragmented into ~6 disconnected
navmesh islands even on a single floor (kitchen / living-room-furniture /
office-bedroom-bathroom / etc.), with near-touch gaps between them of
~0.4-0.57 m horizontally and up to 0.4 m vertically — consistent with
recast pinching off narrow doorways and small thresholds, not real stairs.

This sweeps NavMeshSettings (recomputed on the same loaded stage, no
GPU/renderer needed) and reports, per config: how many distinct islands the
16 SLOT_ANCHORS anchors land on (1 = fully connected interior), which
island that is, and its sampled indoor fraction (so a config that "merges"
by fusing into the outdoor yard is visible, not mistaken for success).

Requires habitat_sim (enable_physics=True for the indoor/outdoor ray cast)
— run from a conda env that has it (e.g. explore-eqa).
"""
from __future__ import annotations

import argparse
import pathlib
import sys
from dataclasses import dataclass

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.topdown_map import HSSD_DIR, anchor_world_positions, room_centroids

_DATASET_CONFIG = f"{HSSD_DIR}/hssd-hab-uncluttered.scene_dataset_config.json"
_CEILING_RAY_MAX_M = 8.0
_CEILING_SAMPLES_FOR_DOMINANT_ISLAND = 200


@dataclass(frozen=True)
class SweepCandidate:
    label: str
    agent_radius: float
    agent_max_climb: float
    agent_max_slope: float
    cell_size: float
    cell_height: float


# Baseline is habitat_sim.NavMeshSettings()'s own defaults (confirmed
# directly: agent_radius=0.1, agent_max_climb=0.2, agent_max_slope=45,
# cell_size=0.05, cell_height=0.2) — NOT the 0.25 the phase brief assumed;
# every candidate below is relative to the real baseline, not a guess.
_CANDIDATES: tuple[SweepCandidate, ...] = (
    SweepCandidate("baseline",              0.10, 0.20, 45.0, 0.05, 0.20),
    SweepCandidate("climb_0.3",             0.10, 0.30, 45.0, 0.05, 0.20),
    SweepCandidate("climb_0.4",             0.10, 0.40, 45.0, 0.05, 0.20),
    SweepCandidate("climb_0.5",             0.10, 0.50, 45.0, 0.05, 0.20),
    SweepCandidate("climb_0.6",             0.10, 0.60, 45.0, 0.05, 0.20),
    SweepCandidate("climb_0.4_radius_0.08", 0.08, 0.40, 45.0, 0.05, 0.20),
    SweepCandidate("climb_0.4_radius_0.06", 0.06, 0.40, 45.0, 0.05, 0.20),
    SweepCandidate("climb_0.4_radius_0.04", 0.04, 0.40, 45.0, 0.05, 0.20),
    SweepCandidate("climb_0.5_radius_0.06", 0.06, 0.50, 45.0, 0.05, 0.20),
    SweepCandidate("climb_0.6_radius_0.06", 0.06, 0.60, 45.0, 0.05, 0.20),
    SweepCandidate("climb_0.4_fine_xz_only",       0.10, 0.40, 45.0, 0.03, 0.20),
    SweepCandidate("climb_0.4_finer_xz_only",      0.10, 0.40, 45.0, 0.02, 0.20),
    SweepCandidate("climb_0.4_radius_0.04_fine_xz", 0.04, 0.40, 45.0, 0.02, 0.20),
)


def _make_sim(scene_id: str):
    import habitat_sim

    backend_cfg = habitat_sim.SimulatorConfiguration()
    backend_cfg.scene_dataset_config_file = _DATASET_CONFIG
    backend_cfg.scene_id = scene_id
    backend_cfg.enable_physics = True
    backend_cfg.create_renderer = False

    agent_cfg = habitat_sim.agent.AgentConfiguration()
    agent_cfg.sensor_specifications = []
    return habitat_sim.Simulator(habitat_sim.Configuration(backend_cfg, [agent_cfg]))


def _is_indoor(sim, point: tuple[float, float, float], max_distance: float = _CEILING_RAY_MAX_M) -> bool:
    import habitat_sim
    import magnum as mn

    origin = mn.Vector3(point[0], point[1] + 0.05, point[2])
    ray = habitat_sim.geo.Ray(origin, mn.Vector3(0.0, 1.0, 0.0))
    return sim.cast_ray(ray, max_distance=max_distance).has_hits()


def evaluate_candidate(sim, scene_id: str, candidate: SweepCandidate) -> dict:
    import habitat_sim

    settings = habitat_sim.NavMeshSettings()
    settings.agent_radius = candidate.agent_radius
    settings.agent_height = 1.5
    settings.agent_max_climb = candidate.agent_max_climb
    settings.agent_max_slope = candidate.agent_max_slope
    settings.cell_size = candidate.cell_size
    settings.cell_height = candidate.cell_height

    ok = sim.recompute_navmesh(sim.pathfinder, settings)
    pf = sim.pathfinder

    anchors = anchor_world_positions(scene_id)
    centroids = room_centroids(scene_id)
    anchor_island = {slot: pf.get_island(list(pos)) for slot, pos in anchors.items()}
    room_island = {
        room: pf.get_island(list(pf.snap_point([x, 0.1, z])))
        for room, (x, z) in centroids.items()
    }
    all_islands = list(anchor_island.values()) + list(room_island.values())
    distinct = sorted(set(all_islands))

    # The dominant island: whichever one the most anchors+rooms share.
    from collections import Counter
    counts = Counter(all_islands)
    dominant_island, dominant_count = counts.most_common(1)[0]

    indoor_fraction = float("nan")
    dominant_area = float("nan")
    if dominant_island >= 0:
        verts = pf.build_navmesh_vertices(dominant_island)
        if len(verts) > 0:
            dominant_area = pf.island_area(dominant_island)
            stride = max(1, len(verts) // _CEILING_SAMPLES_FOR_DOMINANT_ISLAND)
            sample = verts[::stride]
            hits = sum(_is_indoor(sim, tuple(float(c) for c in v)) for v in sample)
            indoor_fraction = hits / len(sample)

    return {
        "label": candidate.label,
        "recompute_ok": ok,
        "num_islands": pf.num_islands,
        "n_distinct_among_anchors_rooms": len(distinct),
        "dominant_island": dominant_island,
        "dominant_count": dominant_count,
        "dominant_of": len(all_islands),
        "dominant_area_m2": dominant_area,
        "dominant_indoor_fraction": indoor_fraction,
        "anchor_island": anchor_island,
        "room_island": room_island,
    }


def print_result(result: dict) -> None:
    print(f"\n=== {result['label']} ===")
    print(f"  recompute_ok={result['recompute_ok']}  num_islands={result['num_islands']}")
    print(f"  distinct islands among anchors+rooms: {result['n_distinct_among_anchors_rooms']}")
    print(f"  dominant island {result['dominant_island']}: "
          f"{result['dominant_count']}/{result['dominant_of']} anchors+rooms, "
          f"area={result['dominant_area_m2']:.1f} m², indoor={result['dominant_indoor_fraction']:.0%}")
    if result["n_distinct_among_anchors_rooms"] > 1:
        by_island: dict[int, list[str]] = {}
        for slot, isl in result["anchor_island"].items():
            by_island.setdefault(isl, []).append(f"anchor:{slot}")
        for room, isl in result["room_island"].items():
            by_island.setdefault(isl, []).append(f"room:{room}")
        for isl, members in sorted(by_island.items()):
            print(f"    island {isl}: {', '.join(sorted(members))}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scene", default="102343992")
    args = ap.parse_args()

    print(f"Loading scene {args.scene} into habitat_sim...")
    sim = _make_sim(args.scene)
    try:
        results = []
        for candidate in _CANDIDATES:
            result = evaluate_candidate(sim, args.scene, candidate)
            print_result(result)
            results.append(result)

        print("\n=== summary ===")
        for r in results:
            merged = "MERGED" if r["n_distinct_among_anchors_rooms"] == 1 else f"{r['n_distinct_among_anchors_rooms']} islands"
            print(f"  {r['label']:28s} num_islands={r['num_islands']:3d}  {merged:12s}  "
                  f"dominant_indoor={r['dominant_indoor_fraction']:.0%}")
    finally:
        sim.close()


if __name__ == "__main__":
    main()
