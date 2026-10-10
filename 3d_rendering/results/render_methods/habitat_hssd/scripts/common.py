"""Shared pieces: open household A's HSSD home (articulated version) in habitat-sim,
light it, aim the camera, measure boxes. Adapted from prior_work/src/rendered_look/home.py."""
from __future__ import annotations

import json
import os
import pathlib
from typing import List, Tuple

import numpy as np

REPO = pathlib.Path("/home/oliver/robot/dynamic_home_eqa")
OUT = REPO / "3d_rendering/results/render_methods/habitat_hssd"
SNAPSHOT = REPO / "3d_rendering/results/lived_home/hssd_a/day_07/positions_1800.json"
HSSD = pathlib.Path("/mnt/nvme/oliver/robot/datasets/moving-eqa/scene_datasets/hssd-hab")
DATASET = HSSD / "hssd-hab-articulated.scene_dataset_config.json"
SCENE = "107734254_176000121"
LIGHTS = "six lights from all sides"


def open_home(cameras: List[dict], physics: bool = True, navmesh: bool = True):
    """cameras: [{"uuid", "kind": "colour"|"ids"|"depth", "width", "height", "hfov"}]"""
    import habitat_sim
    import magnum as mn

    backend = habitat_sim.SimulatorConfiguration()
    backend.scene_dataset_config_file = str(DATASET)
    backend.scene_id = SCENE
    backend.enable_physics = physics
    backend.gpu_device_id = 0
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
    if navmesh:
        settings = habitat_sim.NavMeshSettings()
        settings.set_defaults()
        settings.agent_radius = 0.2
        settings.agent_height = 0.5
        settings.include_static_objects = True
        sim.recompute_navmesh(sim.pathfinder, settings)
    return sim


def box_of(thing) -> Tuple[np.ndarray, np.ndarray]:
    """Axis-aligned world box of a rigid object (or articulated object root)."""
    import magnum as mn

    if hasattr(thing, "get_link_ids"):   # articulated: the root node's box is empty; join the links
        pts = []
        for i in [-1] + list(thing.get_link_ids()):
            node = thing.get_link_scene_node(i)
            bb, m = node.cumulative_bb, node.absolute_transformation()
            if bb.size().max() <= 0:
                continue
            for x in (bb.min.x, bb.max.x):
                for y in (bb.min.y, bb.max.y):
                    for z in (bb.min.z, bb.max.z):
                        q = m.transform_point(mn.Vector3(x, y, z))
                        pts.append([q.x, q.y, q.z])
        pts = np.array(pts)
        return pts.min(axis=0), pts.max(axis=0)
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


def snapshot() -> dict:
    return json.load(SNAPSHOT.open())
