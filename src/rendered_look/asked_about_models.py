"""Candidate 3D models for the objects the questions ask about, rendered for review.

The ten-home banks ask about 11 object classes. This script gathers candidate
models for each class from what is on disk, renders every candidate alone at
the same framing, and writes one sheet of pictures per class plus a JSON list.
Nothing is chosen here: the sheets are for picking by eye.

Sources, in the order they are tried:
  catalogue  data/objects/external_props/mapping.json (already reviewed)
  pool       data/objects/external_props_candidates (unreviewed, Objaverse cache)
  hssd       the HSSD object library, filtered by name and size
  objaverse  models downloaded for classes nothing on disk covers

Run with the dynamic_eqa env:
    python -m rendered_look.asked_about_models
"""
from __future__ import annotations

import csv
import glob
import json
import os
import pathlib
import re
from typing import Dict, List, Optional

REPO = pathlib.Path(__file__).resolve().parents[2]
HSSD = pathlib.Path(os.environ.get(
    "HSSD_DIR", "/mnt/nvme/oliver/robot/datasets/moving-eqa/scene_datasets/hssd-hab"))
OBJAVERSE_GLBS = pathlib.Path("/mnt/nvme/oliver/robot/objaverse_cache/hf-objaverse-v1/glbs")
CATALOGUE = REPO / "data/objects/external_props"
POOL = REPO / "data/objects/external_props_candidates"
BANKS = REPO / "results/self_improve/varied_homes/ten_homes/banks"
OUT = REPO / "results/rendered_look/asked_about_models"

# Household class -> the catalogue categories that hold models of it.
CATALOGUE_NAME = {
    "water_bottle": ["bottle"], "glass": ["drinkware", "cup"], "mug": ["mug"],
    "towel": ["towel"], "medication": ["medicine"], "book": ["book"],
}

# HSSD filters: main_category (None = any), name must match, name must not
# match, longest side in metres at most.
HSSD_FILTER = {
    "book": (("book", ""), r"\bbook\b|novel",
             r"case|shel[fv]|stand|\bend\b|rack|\bset\b|stack|pile|books\b|note|bunting", 0.35),
    "notebook": (("book",), r"notebook|journal", r"notebooks\b", 0.35),
    "glasses": (("eyeglasses",), r".", r"^$", 0.25),
    "tablet": (None, r"\bipad\b|\btablet\b", r"^$", 0.35),
    "towel": (None, r"towel",
              r"rail|rack|ladder|shelf|warmer|holder|ring|\bbar\b|hook|stand|\bmat\b|radiator"
              r"|pile|\bset\b|pairs|hanging|hooded", 0.6),
    "glass": (("drinkware",), r"tumbler|\bglass\b|highball",
              r"wine|martini|brandy|shot|champagne|flute|\bset\b|glasses|cognac", 0.2),
}

# Downloaded from Objaverse on 2026-09-29 because nothing on disk covers them.
OBJAVERSE_NEW = {
    "razor": ["3c3973f4809a", "a0c1892b3ea6", "116149f04071", "20ca53d875a6",
              "2bb0d75a7a6f", "5af587ad47a5", "0bd85b44a55b", "77bdb06b6973"],
    "charger": ["9735f27518fa", "c7c5dc9851ae", "783ccfb0d0f4", "0d8a9b971436",
                "e984f31d0d6b", "429f8e1add81", "0f08def9c912", "3c43f5c1216a"],
}

MOST_PER_SOURCE = 12


def asked_classes() -> Dict[str, int]:
    """Class -> the most copies of it any one household is asked about."""
    most: Dict[str, int] = {}
    for bank in sorted(BANKS.glob("*.jsonl")):
        classes: Dict[str, str] = {}
        asked = set()
        with bank.open() as rows:
            for line in rows:
                row = json.loads(line)
                if row["kind"] == "episode_header":
                    classes = row["object_classes"]
                elif row["kind"] == "question":
                    asked.add(row["object_id"])
        count: Dict[str, int] = {}
        for object_id in asked:
            count[classes[object_id]] = count.get(classes[object_id], 0) + 1
        for cls, n in count.items():
            most[cls] = max(most.get(cls, 0), n)
    return most


def _objaverse_path(uid_or_prefix: str) -> Optional[str]:
    found = glob.glob(str(OBJAVERSE_GLBS / "*" / f"{uid_or_prefix}*.glb"))
    return found[0] if len(found) == 1 else None


def candidates_for(cls: str) -> List[dict]:
    out: List[dict] = []
    names = CATALOGUE_NAME.get(cls, [])
    for entry in json.load((CATALOGUE / "mapping.json").open()):
        if entry["category"] in names:
            mesh = CATALOGUE / "meshes" / f"{entry['uid']}.glb"
            config = json.load((CATALOGUE / "configs" / f"{entry['uid']}.object_config.json").open())
            out.append({"source": "catalogue", "id": entry["uid"], "mesh": str(mesh),
                        "scale": config["scale"][0], "up": config["up"],
                        "name": ", ".join(entry.get("tags", []))})
    have = {c["id"].split("_")[-1][:8] for c in out}
    for entry in json.load((POOL / "candidates_mapping.json").open()):
        if entry["category"] in names and entry.get("source") == "objaverse":
            if entry["objaverse_uid"][:8] in have:
                continue
            mesh = _objaverse_path(entry["objaverse_uid"])
            if mesh:
                out.append({"source": "pool", "id": entry["uid"], "mesh": mesh,
                            "name": entry["category"]})
    if cls in HSSD_FILTER:
        categories, must, must_not, longest = HSSD_FILTER[cls]
        kept = 0
        with (HSSD / "semantics/objects.csv").open() as handle:
            for row in csv.DictReader(handle):
                if kept >= MOST_PER_SOURCE:
                    break
                name = row.get("name") or ""
                if categories is not None and row.get("main_category") not in categories:
                    continue
                if not re.search(must, name, re.I) or re.search(must_not, name, re.I):
                    continue
                if (row.get("hasMultipleObjects") or "").lower() == "true":
                    continue
                try:
                    dims = [float(x) for x in row["aligned.dims"].split(",")]
                except (KeyError, ValueError):
                    continue
                mesh = HSSD / "objects" / row["id"][0] / f"{row['id']}.glb"
                if max(dims) > longest or not mesh.exists():
                    continue
                kept += 1
                out.append({"source": "hssd", "id": row["id"], "mesh": str(mesh),
                            "name": name, "dims_m": [round(d, 3) for d in dims]})
    for prefix in OBJAVERSE_NEW.get(cls, []):
        mesh = _objaverse_path(prefix)
        if mesh:
            out.append({"source": "objaverse", "id": f"{cls}_{prefix}", "mesh": mesh,
                        "name": cls})
    return out


class OneModelAtATime:
    """Renders single models with habitat-sim, the renderer the experiments use.

    trimesh and pyrender cannot read the compressed textures in the HSSD files:
    every HSSD model came out plain grey, so they are not used here.
    """

    LIGHTS = "three lights"

    def __init__(self, size: int = 256) -> None:
        import habitat_sim
        import magnum as mn

        self.hs, self.mn = habitat_sim, mn
        backend = habitat_sim.SimulatorConfiguration()
        backend.scene_id = "NONE"
        backend.enable_physics = True
        backend.gpu_device_id = int(os.environ.get("DYNAMIC_EQA_RENDER_GPU", "0"))
        camera = habitat_sim.CameraSensorSpec()
        camera.uuid = "rgb"
        camera.sensor_type = habitat_sim.SensorType.COLOR
        camera.resolution = [size, size]
        camera.position = mn.Vector3(0, 0, 0)
        camera.hfov = 45
        camera.clear_color = mn.Color4(0.92, 0.92, 0.92, 1.0)
        agent = habitat_sim.agent.AgentConfiguration()
        agent.sensor_specifications = [camera]
        self.sim = habitat_sim.Simulator(habitat_sim.Configuration(backend, [agent]))
        light = habitat_sim.gfx.LightInfo
        world = habitat_sim.gfx.LightPositionModel.Global
        self.sim.set_light_setup([
            light(vector=[-1.0, -1.5, -1.0, 0.0], color=[2.2, 2.2, 2.2], model=world),
            light(vector=[1.0, -0.5, -0.3, 0.0], color=[1.2, 1.2, 1.2], model=world),
            light(vector=[-0.2, -0.3, 1.0, 0.0], color=[0.9, 0.9, 0.9], model=world),
        ], self.LIGHTS)

    def close(self) -> None:
        self.sim.close()

    def render(self, mesh_path: str):
        """Returns (picture, size of the file along x, y, z in its own units).

        The camera distance follows the model's longest side, so the picture
        says nothing about real size.
        """
        import numpy as np

        hs, mn = self.hs, self.mn
        templates = self.sim.get_object_template_manager()
        objects = self.sim.get_rigid_object_manager()
        template = templates.create_new_template(mesh_path)
        template.render_asset_handle = mesh_path
        template.collision_asset_handle = mesh_path
        template_id = templates.register_template(template, mesh_path)
        model = objects.add_object_by_template_id(template_id, light_setup_key=self.LIGHTS)
        try:
            model.motion_type = hs.physics.MotionType.KINEMATIC
            box = model.root_scene_node.cumulative_bb
            size = [float(x) for x in box.size()]
            model.translation = -box.center()
            eye = np.array([1.1, 0.9, 1.1])
            eye = eye / np.linalg.norm(eye) * max(size) * 1.9
            facing = mn.Matrix4.look_at(mn.Vector3(*eye), mn.Vector3(0, 0, 0), mn.Vector3(0, 1, 0))
            turn = mn.Quaternion.from_matrix(facing.rotation())
            agent = self.sim.get_agent(0)
            state = agent.get_state()
            state.position = eye
            state.rotation = np.quaternion(turn.scalar, *turn.vector)
            agent.set_state(state, reset_sensors=True)
            picture = self.sim.get_sensor_observations()["rgb"][:, :, :3].copy()
        finally:
            objects.remove_object_by_id(model.object_id)
        return picture, size


def sheet(cls: str, needed: int, candidates: List[dict],
          renderer: "OneModelAtATime") -> pathlib.Path:
    from PIL import Image, ImageDraw

    size, label, across = 256, 46, 4
    down = max(1, -(-len(candidates) // across))
    page = Image.new("RGB", (across * size, 30 + down * (size + label)), "white")
    draw = ImageDraw.Draw(page)
    draw.text((6, 8), f"{cls}: {len(candidates)} candidates, {needed} needed in one household",
              fill="black")
    for i, candidate in enumerate(candidates):
        x, y = (i % across) * size, 30 + (i // across) * (size + label)
        try:
            picture, file_size = renderer.render(candidate["mesh"])
            # Share of the picture that is not background. A model can load
            # without error and still draw nothing.
            filled = float((abs(picture.astype(int) - 235).max(axis=2) > 12).mean())
            candidate["share_of_picture_filled"] = round(filled, 3)
            if filled < 0.01:
                raise ValueError(f"the picture is empty ({filled:.1%} of it is not background)")
            scale = candidate.get("scale", 1.0)
            if candidate["source"] in ("catalogue", "hssd"):
                candidate["size_m"] = [round(x * scale, 3) for x in file_size]
            else:  # no scale has been set for this file yet
                candidate["size_in_file_units"] = [round(x, 3) for x in file_size]
            candidate["rendered"] = True
            page.paste(Image.fromarray(picture), (x, y))
        except Exception as problem:  # a model that cannot be drawn is a finding, not a crash
            candidate["rendered"] = False
            candidate["render_error"] = f"{type(problem).__name__}: {problem}"[:200]
            draw.text((x + 6, y + 100), "COULD NOT RENDER", fill="red")
        draw.text((x + 4, y + size + 2), f"{i + 1}. {candidate['source']}  {candidate['id'][-12:]}",
                  fill="black")
        draw.text((x + 4, y + size + 16), candidate["name"][:40], fill=(90, 90, 90))
        if "size_m" in candidate:
            draw.text((x + 4, y + size + 30),
                      "m: " + " x ".join(f"{d:.2f}" for d in candidate["size_m"]), fill=(90, 90, 90))
        elif candidate.get("rendered"):
            draw.text((x + 4, y + size + 30), "real size not set", fill=(170, 90, 0))
    path = OUT / f"{cls}.png"
    page.save(path)
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {}
    renderer = OneModelAtATime()
    for cls, needed in sorted(asked_classes().items()):
        candidates = candidates_for(cls)
        path = sheet(cls, needed, candidates, renderer)
        drawn = sum(1 for c in candidates if c.get("rendered"))
        report[cls] = {"needed_in_one_household": needed, "candidates": candidates}
        print(f"{cls:14} needed {needed}  candidates {len(candidates):3}  rendered {drawn:3}  {path}")
        for c in candidates:
            if not c.get("rendered"):
                print(f"    could not render {c['id']}: {c.get('render_error')}")
    renderer.close()
    (OUT / "candidates.json").write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
