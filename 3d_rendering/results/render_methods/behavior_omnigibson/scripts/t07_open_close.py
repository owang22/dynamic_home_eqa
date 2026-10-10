"""Step 7: a BEHAVIOR cabinet shut, then open, with a mug and a bowl sampled Inside it (Rs_int kitchen).
OmniGibson's own Open state and Inside sampler; pictures from a 1.0 m camera; share of picture per object by
hide-and-compare."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from og_common import OUT, PIC, cam_quat, dump, make_env, render, save_png, visible_share  # noqa: E402
from omnigibson.macros import gm  # noqa: E402

gm.ENABLE_TRANSITION_RULES = False
import numpy as np  # noqa: E402
import torch as th  # noqa: E402

import omnigibson as og  # noqa: E402
from omnigibson import object_states as S  # noqa: E402
from omnigibson.objects.dataset_object import DatasetObject  # noqa: E402


def main():
    env, load_s = make_env({"type": "InteractiveTraversableScene", "scene_model": "Rs_int"})
    scene = env.scene
    cam = list(env.external_sensors[0].values())[1]
    cabs = [o for o in scene.objects if o.category in ("bottom_cabinet", "bottom_cabinet_no_top") and S.Open in o.states]
    print("CABINETS", [(c.name, c.in_rooms) for c in cabs], flush=True)
    og.sim.stop()
    things = [DatasetObject(name="demo_mug", category="mug", model=sorted(os.listdir(
        "/mnt/nvme/oliver/robot/render_methods/behavior/BEHAVIOR-1K/datasets/behavior-1k-assets/objects/mug"))[0]),
        DatasetObject(name="demo_bowl", category="bowl", model=sorted(os.listdir(
            "/mnt/nvme/oliver/robot/render_methods/behavior/BEHAVIOR-1K/datasets/behavior-1k-assets/objects/bowl"))[0])]
    for i, t in enumerate(things):
        scene.add_object(t)
        t.set_position_orientation(position=th.tensor([30.0 + i, 30.0, 0.5]))
    og.sim.play()
    og.sim.step()
    result = dict(load_seconds=load_s)
    for cab in cabs:
        cab.states[S.Open].set_value(True, fully=True)
        for _ in range(5):
            og.sim.step()
        ok = [bool(t.states[S.Inside].set_value(cab, True)) for t in things]
        print("SAMPLE", cab.name, ok, flush=True)
        if all(ok):
            break
    else:
        print("NO CABINET TOOK BOTH", flush=True)
    cab.states[S.Open].set_value(False, fully=True)
    for _ in range(30):
        og.sim.step()
    lo, hi = [x.cpu().numpy() for x in cab.aabb]
    c = (lo + hi) / 2
    # camera 1.3 m from the cabinet towards the middle of its room, 1.0 m up
    fl = [o for o in scene.objects if o.category == "floors" and o.in_rooms and o.in_rooms[0] == cab.in_rooms[0]][0]
    flo, fhi = [x.cpu().numpy() for x in fl.aabb]
    rc = (flo + fhi) / 2
    dvec = np.array([rc[0] - c[0], rc[1] - c[1]])
    dvec /= np.linalg.norm(dvec)
    eye = np.array([c[0] + 1.3 * dvec[0], c[1] + 1.3 * dvec[1], 1.0])
    v = c - eye
    q = cam_quat(math.atan2(v[1], v[0]), math.atan2(v[2], math.hypot(v[0], v[1])))
    best = (0, eye, q)
    sc, eye, q = best
    cam.set_position_orientation(position=th.tensor(eye, dtype=th.float32), orientation=th.tensor(q, dtype=th.float32),
                                 frame="scene")
    for _ in range(5):
        og.sim.step()
    shut_share = visible_share(cam, things + [cab])
    rgb, *_ = render(cam, n=8)
    save_png(rgb, f"{PIC}/open_close/{cab.name}_shut.png")
    inside_shut = {t.name: bool(t.states[S.Inside].get_value(cab)) for t in things}
    cab.states[S.Open].set_value(True, fully=True)
    for _ in range(5):
        og.sim.step()
    open_share = visible_share(cam, things + [cab])
    rgb, *_ = render(cam, n=8)
    save_png(rgb, f"{PIC}/open_close/{cab.name}_open.png")
    inside_open = {t.name: bool(t.states[S.Inside].get_value(cab)) for t in things}
    result.update(cabinet=cab.name, category=cab.category, eye=eye.tolist(), quat_xyzw=list(map(float, q)), hfov_deg=75,
                  shut_share_pct=shut_share, open_share_pct=open_share, inside_when_shut=inside_shut,
                  inside_when_open=inside_open, open_state_shut=False, open_state_open=bool(cab.states[S.Open].get_value()),
                  images=[f"pictures/open_close/{cab.name}_shut.png", f"pictures/open_close/{cab.name}_open.png"])
    print("DEMO", result, flush=True)
    dump(result, f"{OUT}/open_close.json")
    og.shutdown()


if __name__ == "__main__":
    main()
