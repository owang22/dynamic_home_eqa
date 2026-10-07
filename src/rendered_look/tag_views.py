"""Four views of every picked model, for writing and checking its appearance tags.

Each model gets one picture: three-quarter view, front, side and straight
down. Files are named by an opaque number, and the key that says which model
is which is written somewhere else, so a checker who is shown only the
pictures cannot read the class or the owner off a file name.

    python -m rendered_look.tag_views
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
from PIL import Image, ImageDraw

from rendered_look.asked_about_models import OneModelAtATime, REPO

MODELS = pathlib.Path(__file__).with_name("asked_about_models.json")
OUT = REPO / "results/rendered_look/object_tags"
VIEWS = [("from above and to one side", (1.1, 0.9, 1.1)), ("front", (0.0, 0.25, 1.6)),
         ("side", (1.6, 0.25, 0.0)), ("straight down", (0.001, 1.7, 0.0))]


def main() -> None:
    import magnum as mn
    (OUT / "views").mkdir(parents=True, exist_ok=True)
    renderer = OneModelAtATime(size=420)
    hs = renderer.hs
    picked = json.load(MODELS.open())
    order = sorted((m["id"], cls) for cls, group in picked.items() for m in group)
    rng = np.random.default_rng(20260930)
    rng.shuffle(order)            # so neighbouring numbers are not the same class
    key = {}
    for number, (model_id, cls) in enumerate(order, start=1):
        model = next(m for m in picked[cls] if m["id"] == model_id)
        templates = renderer.sim.get_object_template_manager()
        objects = renderer.sim.get_rigid_object_manager()
        template = templates.create_new_template(model["mesh"])
        template.render_asset_handle = model["mesh"]
        template.collision_asset_handle = model["mesh"]
        thing = objects.add_object_by_template_id(templates.register_template(template, model["mesh"]),
                                                  light_setup_key=renderer.LIGHTS)
        thing.motion_type = hs.physics.MotionType.KINEMATIC
        box = thing.root_scene_node.cumulative_bb
        thing.translation = -box.center()
        longest = max(box.size())
        sheet = Image.new("RGB", (840, 880), "white")
        for i, (name, direction) in enumerate(VIEWS):
            eye = np.array(direction) / np.linalg.norm(direction) * longest * 1.9
            facing = mn.Matrix4.look_at(mn.Vector3(*eye), mn.Vector3(0, 0, 0),
                                        mn.Vector3(0, 0, -1) if name == "straight down" else mn.Vector3(0, 1, 0))
            turn = mn.Quaternion.from_matrix(facing.rotation())
            agent = renderer.sim.get_agent(0)
            state = agent.get_state()
            state.position = eye
            state.rotation = np.quaternion(turn.scalar, *turn.vector)
            agent.set_state(state, reset_sensors=True)
            picture = Image.fromarray(renderer.sim.get_sensor_observations()["rgb"][:, :, :3])
            ImageDraw.Draw(picture).text((8, 6), name, fill="black")
            sheet.paste(picture, ((i % 2) * 420, (i // 2) * 420))
        size = [round(v * 100, 1) for v in model["size_m"]]
        ImageDraw.Draw(sheet).text((8, 850), f"object {number:02d}     real size about "
                                             f"{size[0]} x {size[1]} x {size[2]} cm (width, height, depth)",
                                   fill="black")
        sheet.save(OUT / "views" / f"object_{number:02d}.png")
        objects.remove_object_by_id(thing.object_id)
        key[f"object_{number:02d}"] = {"model": model_id, "class": cls, "source": model["source"],
                                       "size_m": model["size_m"], "tag_now": model["looks_like"]}
    (OUT / "key.json").write_text(json.dumps(key, indent=1))
    renderer.close()
    print(len(key), "models,", OUT / "views")


if __name__ == "__main__":
    main()
