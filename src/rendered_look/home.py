"""Opening one HSSD home in habitat-sim, and the geometry questions asked of it."""
from __future__ import annotations

import csv
import json
import os
import pathlib
from typing import Dict, List, Optional, Tuple

import numpy as np

HSSD = pathlib.Path(os.environ.get(
    "HSSD_DIR", "/mnt/nvme/oliver/robot/datasets/moving-eqa/scene_datasets/hssd-hab"))
DATASET = HSSD / "hssd-hab-uncluttered.scene_dataset_config.json"
LIGHTS = "six lights from all sides"


def regions_of(scene: str) -> List[dict]:
    path = HSSD / "semantics/scenes" / f"{scene}.semantic_config.json"
    return json.load(path.open())["region_annotations"]


def inside(x: float, z: float, polygon) -> bool:
    within = False
    for i in range(len(polygon)):
        x1, _, z1 = polygon[i]
        x2, _, z2 = polygon[(i + 1) % len(polygon)]
        if (z1 > z) != (z2 > z) and x < (x2 - x1) * (z - z1) / (z2 - z1) + x1:
            within = not within
    return within


def region_at(x: float, z: float, regions: List[dict]) -> Optional[str]:
    for region in regions:
        if inside(x, z, region["poly_loop"]):
            return region["name"]
    return None


_NAMES: Optional[Dict[str, dict]] = None


def model_facts(model_id: str) -> dict:
    global _NAMES
    if _NAMES is None:
        with (HSSD / "semantics/objects.csv").open() as handle:
            _NAMES = {row["id"]: row for row in csv.DictReader(handle)}
    return _NAMES.get(model_id, {})


def open_home(scene: str, cameras: List[dict], physics: bool = True):
    """cameras: [{"uuid", "kind": "colour"|"ids"|"depth", "width", "height", "hfov"}]"""
    import habitat_sim
    import magnum as mn

    backend = habitat_sim.SimulatorConfiguration()
    backend.scene_dataset_config_file = str(DATASET)
    backend.scene_id = scene
    backend.enable_physics = physics
    backend.gpu_device_id = int(os.environ.get("DYNAMIC_EQA_RENDER_GPU", "0"))
    # The home's own lights leave it too dark to read (mean brightness 58 of 255).
    backend.override_scene_light_defaults = True
    backend.scene_light_setup = LIGHTS
    kinds = {"colour": habitat_sim.SensorType.COLOR, "ids": habitat_sim.SensorType.SEMANTIC,
             "depth": habitat_sim.SensorType.DEPTH}
    specs = []
    for camera in cameras:
        spec = habitat_sim.CameraSensorSpec()
        spec.uuid = camera["uuid"]
        spec.sensor_type = kinds[camera["kind"]]
        spec.resolution = [camera["height"], camera["width"]]
        spec.position = mn.Vector3(0, 0, 0)
        spec.hfov = camera.get("hfov", 90)
        specs.append(spec)
    agent = habitat_sim.agent.AgentConfiguration()
    agent.sensor_specifications = specs
    agent.height = 0.0
    sim = habitat_sim.Simulator(habitat_sim.Configuration(backend, [agent]))
    light, fixed = habitat_sim.gfx.LightInfo, habitat_sim.gfx.LightPositionModel.Global
    sim.set_light_setup([
        light(vector=mn.Vector4(*direction, 0.0), color=mn.Color3(strength, strength, strength),
              model=fixed)
        for direction, strength in [((0, -1, 0), 1.0), ((1, -0.6, 0.3), 0.7), ((-1, -0.6, -0.3), 0.7),
                                    ((0.3, -0.6, 1), 0.7), ((-0.3, -0.6, -1), 0.7), ((0, 1, 0), 0.35)]
    ], LIGHTS)
    settings = habitat_sim.NavMeshSettings()
    settings.set_defaults()
    settings.agent_radius = 0.25
    settings.agent_height = 1.4
    settings.include_static_objects = True
    sim.recompute_navmesh(sim.pathfinder, settings)
    return sim


def world_box(thing) -> Tuple[np.ndarray, np.ndarray]:
    """Axis-aligned box of a rigid object in world coordinates: (low, high)."""
    import magnum as mn

    box = thing.root_scene_node.cumulative_bb
    matrix = thing.transformation
    corners = [matrix.transform_point(mn.Vector3(x, y, z))
               for x in (box.min.x, box.max.x) for y in (box.min.y, box.max.y)
               for z in (box.min.z, box.max.z)]
    points = np.array([[c.x, c.y, c.z] for c in corners])
    return points.min(axis=0), points.max(axis=0)


def look_from(sim, eye, target) -> None:
    import magnum as mn

    eye_v, target_v = mn.Vector3(*[float(v) for v in eye]), mn.Vector3(*[float(v) for v in target])
    facing = mn.Matrix4.look_at(eye_v, target_v, mn.Vector3(0, 1, 0))
    turn = mn.Quaternion.from_matrix(facing.rotation())
    agent = sim.get_agent(0)
    state = agent.get_state()
    state.position = np.array(eye, dtype=np.float32)
    state.rotation = np.quaternion(turn.scalar, *turn.vector)
    agent.set_state(state, reset_sensors=True)


def furniture(sim, scene: str) -> List[dict]:
    regions = regions_of(scene)
    out = []
    manager = sim.get_rigid_object_manager()
    for handle, thing in manager.get_objects_by_handle_substring("").items():
        low, high = world_box(thing)
        centre = (low + high) / 2
        model_id = handle.split("_:")[0]
        facts = model_facts(model_id)
        out.append({"handle": handle, "object_id": thing.object_id, "model": model_id,
                    "category": facts.get("main_category") or "", "name": facts.get("name") or "",
                    "room": region_at(centre[0], centre[2], regions),
                    "low": [round(float(v), 3) for v in low],
                    "high": [round(float(v), 3) for v in high]})
    return out
