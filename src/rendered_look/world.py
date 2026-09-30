"""One household placed in one home: furniture, surfaces, the things and the people."""
from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Dict, List, Optional

import numpy as np

from rendered_look import home, surfaces

REPO = pathlib.Path(__file__).resolve().parents[2]
MODELS = pathlib.Path(__file__).with_name("asked_about_models.json")
BANKS = REPO / "results/self_improve/varied_homes/ten_homes/banks"

HFOV = 75   # at 90 degrees, upright things near the edge of the frame look tilted
VIEW = dict(width=960, height=720, hfov=HFOV)
FIRST_THING_ID = 5000     # ids in the picture of ids: furniture below, things and people above
FIRST_PERSON_ID = 9000
LIES_FLAT = {"razor", "book", "notebook", "tablet", "glasses", "charger", "towel"}
STACKS = {"towel", "book", "notebook"}   # flat things that may be put on top of each other


def steady_number(*parts) -> float:
    """The same number in [0, 1) for the same words, on every run."""
    digest = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(digest[:12], 16) / float(16 ** 12)


class World:
    def __init__(self, binding) -> None:
        self.binding = binding
        self.sim = home.open_home(binding.HOME, [
            dict(uuid="colour", kind="colour", **VIEW),
            dict(uuid="ids", kind="ids", **VIEW),
            dict(uuid="depth", kind="depth", **VIEW),
            dict(uuid="down_depth", kind="depth", width=512, height=512, hfov=90),
            dict(uuid="down_ids", kind="ids", width=512, height=512, hfov=90),
        ])
        self.regions = {r["name"]: r for r in home.regions_of(binding.HOME)}
        self.objects = self.sim.get_rigid_object_manager()
        self.furniture: Dict[str, object] = {}
        for handle, thing in self.objects.get_objects_by_handle_substring("").items():
            thing.semantic_id = thing.object_id + 10
            self.furniture[handle] = thing
        self.surfaces: Dict[str, surfaces.Surface] = {}
        self.place_problems: Dict[str, str] = {}
        self.things: Dict[str, object] = {}
        self.thing_facts: Dict[str, dict] = {}
        self.people: Dict[str, Dict[str, object]] = {}

    def close(self) -> None:
        self.sim.close()

    # ---- furniture and surfaces -------------------------------------------------
    def furniture_for(self, place: str):
        spec = self.binding.PLACES[place]
        wanted = f"{spec['furniture']}"
        instance = spec.get("instance", 0)
        found = sorted(h for h in self.furniture
                       if h.startswith(wanted) and h.endswith(f"_:{instance:04d}"))
        if len(found) != 1:
            raise ValueError(f"{place}: {len(found)} pieces of furniture match {wanted} #{instance}")
        return self.furniture[found[0]]

    def room_of(self, place: str, receptacle_rooms: Dict[str, str]) -> dict:
        return self.regions[self.binding.ROOMS[receptacle_rooms[place]]]

    def find_surfaces(self, receptacle_rooms: Dict[str, str]) -> None:
        for place, spec in self.binding.PLACES.items():
            try:
                if spec["kind"] == "surface":
                    self.surfaces[place] = surfaces.find_surface(
                        self.sim, place, self.furniture_for(place), spec["band"],
                        spec.get("camera_height"), spec.get("tolerance", 0.02))
                elif spec["kind"] == "floor":
                    self.surfaces[place] = surfaces.floor_surface(
                        self.sim, place, spec["near"], self.room_of(place, receptacle_rooms))
            except ValueError as problem:
                self.place_problems[place] = str(problem)

    # ---- things -------------------------------------------------------------------
    def add_model(self, mesh: str, scale: float, semantic_id: int, light: str = ""):
        import habitat_sim
        import magnum as mn

        templates = self.sim.get_object_template_manager()
        key = f"{mesh}@{scale:.6f}"
        template = templates.create_new_template(key)
        template.render_asset_handle = mesh
        template.collision_asset_handle = mesh
        template.scale = mn.Vector3(scale, scale, scale)
        template_id = templates.register_template(template, key)
        thing = self.objects.add_object_by_template_id(template_id, light_setup_key=home.LIGHTS)
        thing.motion_type = habitat_sim.physics.MotionType.KINEMATIC
        thing.semantic_id = semantic_id
        return thing

    def add_things(self, which_model: Dict[str, dict]) -> None:
        models = {m["id"]: m for group in json.load(MODELS.open()).values() for m in group}
        for number, (object_id, given) in enumerate(sorted(which_model.items())):
            model = models[given["model"]]
            thing = self.add_model(model["mesh"], model["scale"], FIRST_THING_ID + number)
            box = thing.root_scene_node.cumulative_bb
            self.things[object_id] = thing
            size = [box.size().x, box.size().y, box.size().z]
            # a razor or a book stood on end is laid on its side instead
            laid_flat = (given["class"] in LIES_FLAT and size[1] > 2 * min(size[0], size[2]))
            if laid_flat:
                size = [size[0], size[2], size[1]]
            self.thing_facts[object_id] = {
                "class": given["class"], "looks_like": given["looks_like"],
                "semantic_id": FIRST_THING_ID + number,
                "laid_flat": laid_flat, "height": float(size[1]),
                "stacks": given["class"] in STACKS,
                "radius": 0.5 * float(np.hypot(size[0], size[2])),
            }
            self.put_away(object_id)

    def put_away(self, object_id: str) -> None:
        import magnum as mn
        self.things[object_id].translation = mn.Vector3(0.0, -50.0 - len(self.things), 0.0)

    def rest(self, thing, turn, x: float, y: float, z: float) -> None:
        """Turn the thing, then move it so that its box is centred on x, z and
        the bottom of its box is at height y."""
        import magnum as mn
        thing.rotation = turn
        thing.translation = mn.Vector3(0, 0, 0)
        low, high = home.world_box(thing)
        thing.translation = mn.Vector3(float(x - (low[0] + high[0]) / 2), float(y - low[1]),
                                       float(z - (low[2] + high[2]) / 2))

    def put(self, object_id: str, x: float, y: float, z: float, yaw: float) -> None:
        import magnum as mn
        turn = mn.Quaternion.rotation(mn.Rad(yaw), mn.Vector3(0, 1, 0))
        if self.thing_facts[object_id]["laid_flat"]:
            turn = turn * mn.Quaternion.rotation(mn.Rad(np.pi / 2), mn.Vector3(1, 0, 0))
        self.rest(self.things[object_id], turn, x, y, z)
