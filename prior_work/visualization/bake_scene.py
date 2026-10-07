#!/usr/bin/env python3
"""Bake a static topdown asset bundle for one HSSD scene.

Self-contained (no imports from the legacy dynamic_home_eqa package or
EXPRESS-Bench): loads the scene into a minimal, sensorless, renderer-less
habitat_sim Simulator — navmesh/pathfinder only, no GPU — and writes
everything the web viewer needs as static files:

  <out>/map.png     topdown occupancy image (light = navigable)
  <out>/scene.json  world<->pixel transform + per-room floor polygons from
                    the scene's semantic_config.json region annotations

Pixel convention (verified empirically below, not assumed): with the grid
from pathfinder.get_topdown_view(mpp, height),
    row = (z - bounds_min.z) / mpp,  col = (x - bounds_min.x) / mpp.
The bake asserts this by projecting sampled navigable points and checking
the grid reads True at their cells.

This is the ONLY step that needs habitat_sim; run it in the dynamic_eqa
conda env. The viewer and spatializer consume the baked files without any
habitat dependency:

  /home/nesl/anaconda3/envs/dynamic_eqa/bin/python bake_scene.py \
      --scene 108736689_177263340 --out assets/108736689_177263340
"""

from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np

HSSD_DEFAULT = "/data/oliver/robot/EXPRESS-Bench/data/versioned_data/hssd-hab"


def normalise_room(name: str) -> str:
    """'bedroom.001' / 'Living Room' -> 'bedroom' / 'living_room'."""
    return name.lower().replace(" ", "_").split(".")[0]


def load_regions(hssd: pathlib.Path, scene: str) -> list[dict]:
    cfg = hssd / "semantics" / "scenes" / f"{scene}.semantic_config.json"
    data = json.loads(cfg.read_text())
    rooms = []
    for r in data.get("region_annotations", []):
        rooms.append({
            "name": r.get("name", ""),
            "room": normalise_room(r.get("name", "")),
            "label": r.get("label", ""),
            "poly": [[p[0], p[2]] for p in r.get("poly_loop", [])],  # (x, z)
            "floor_height": float(r.get("floor_height", 0.0)),
            "min_bounds": r.get("min_bounds"),
            "max_bounds": r.get("max_bounds"),
        })
    return rooms


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--hssd", type=pathlib.Path, default=pathlib.Path(HSSD_DEFAULT))
    ap.add_argument("--mpp", type=float, default=0.03, help="meters per pixel")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    import habitat_sim  # deferred: only this step needs it

    backend = habitat_sim.SimulatorConfiguration()
    backend.scene_id = args.scene
    backend.scene_dataset_config_file = str(
        args.hssd / "hssd-hab-uncluttered.scene_dataset_config.json")
    backend.create_renderer = False
    backend.enable_physics = False
    agent = habitat_sim.agent.AgentConfiguration()
    agent.sensor_specifications = []
    sim = habitat_sim.Simulator(habitat_sim.Configuration(backend, [agent]))

    if not sim.pathfinder.is_loaded:
        settings = habitat_sim.NavMeshSettings()
        settings.set_defaults()
        sim.recompute_navmesh(sim.pathfinder, settings)
    assert sim.pathfinder.is_loaded, "navmesh failed to load/compute"

    rooms = load_regions(args.hssd, args.scene)
    bounds_min, bounds_max = sim.pathfinder.get_bounds()
    floor = min((r["floor_height"] for r in rooms), default=float(bounds_min[1]))
    height = floor + 0.15
    grid = sim.pathfinder.get_topdown_view(args.mpp, height)

    # verify the row/col convention against real navigable points
    checked = 0
    for _ in range(200):
        p = sim.pathfinder.get_random_navigable_point()
        if abs(float(p[1]) - height) > 0.5:
            continue  # other floor (shouldn't exist in a 1-story apartment)
        row = int((p[2] - bounds_min[2]) / args.mpp)
        col = int((p[0] - bounds_min[0]) / args.mpp)
        if 0 <= row < grid.shape[0] and 0 <= col < grid.shape[1]:
            assert grid[row, col], f"projection convention violated at {p}"
            checked += 1
    assert checked > 50, "too few same-floor navigable samples to trust the check"

    args.out.mkdir(parents=True, exist_ok=True)
    from PIL import Image
    img = np.where(grid, 235, 48).astype(np.uint8)  # light floor, dark walls
    Image.fromarray(img, mode="L").save(args.out / "map.png")

    (args.out / "scene.json").write_text(json.dumps({
        "scene_id": args.scene,
        "meters_per_pixel": args.mpp,
        "bounds_min": [float(v) for v in bounds_min],
        "bounds_max": [float(v) for v in bounds_max],
        "height": height,
        "grid_shape": list(grid.shape),   # [rows, cols]
        "pixel_convention": "row=(z-bounds_min[2])/mpp, col=(x-bounds_min[0])/mpp",
        "rooms": rooms,
    }, indent=1))
    sim.close()
    print(f"baked {args.scene}: grid {grid.shape}, {len(rooms)} rooms, "
          f"{checked} projection checks passed -> {args.out}")


if __name__ == "__main__":
    main()
