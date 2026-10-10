"""Step 4b: a clearer picture of the Unitree Go2 model (Isaac Sim asset server) standing in BEHAVIOR's
Rs_int with a resident figure, plus the two robot cameras placed on the Go2 model: 0.37 m at its head,
1.0 m on a mast over its body. Static figures only: nothing here is driven or animated."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from og_common import OUT, PIC, cam_quat, dump, make_env, render, save_png  # noqa: E402

import numpy as np  # noqa: E402
import torch as th  # noqa: E402

import omnigibson as og  # noqa: E402
import omnigibson.lazy as lazy  # noqa: E402

ROOT = "https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac"
GO2 = f"{ROOT}/Robots/Unitree/Go2/go2.usd"
PERSON = f"{ROOT}/People/Characters/F_Business_02/F_Business_02.usd"


def ref(stage, name, url, pos, yaw_deg):
    prim = stage.DefinePrim(f"/World/{name}", "Xform")
    prim.GetReferences().AddReference(url)
    xf = lazy.pxr.UsdGeom.Xformable(prim)
    xf.ClearXformOpOrder()
    xf.AddTranslateOp().Set(lazy.pxr.Gf.Vec3d(*[float(x) for x in pos]))
    xf.AddRotateZOp().Set(float(yaw_deg))
    return prim


def aim(cam, eye, tgt):
    v = np.asarray(tgt, float) - np.asarray(eye, float)
    q = cam_quat(math.atan2(v[1], v[0]), math.atan2(v[2], math.hypot(v[0], v[1])))
    cam.set_position_orientation(position=th.tensor(eye, dtype=th.float32), orientation=th.tensor(q, dtype=th.float32),
                                 frame="scene")
    return q


def main():
    env, load_s = make_env({"type": "InteractiveTraversableScene", "scene_model": "Rs_int"})
    cams = list(env.external_sensors[0].values())  # cam_0: 100 deg lens, cam_1: 75 deg lens
    stage = lazy.isaacsim.core.utils.stage.get_current_stage()
    go2_xy, go2_yaw = np.array([0.4, -0.6]), 90.0  # standing in the open floor of Rs_int, facing +y
    with og.sim.editing_usd():  # OmniGibson refuses USD edits outside this context
        ref(stage, "go2_model", GO2, (go2_xy[0], go2_xy[1], 0.33), go2_yaw)
        ref(stage, "person_a", PERSON, (0.9, 1.6, 0.0), -110.0)
    for _ in range(40):
        og.sim.render()
    shots = {}
    # side view of the Go2 and the person from a 1.0 m camera
    q = aim(cams[1], (-1.3, -1.6, 1.0), (0.6, 0.2, 0.45))
    rgb, *_ = render(cams[1], n=12)
    save_png(rgb, f"{PIC}/robot/go2_model_and_person_raised.png")
    shots["side"] = dict(eye=[-1.3, -1.6, 1.0], target=[0.6, 0.2, 0.45])
    # cameras on the Go2: 0.37 m at the head (0.36 m ahead of the body centre), 1.0 m on a mast over the body
    yaw = math.radians(go2_yaw)
    head = np.array([go2_xy[0] + 0.36 * math.cos(yaw), go2_xy[1] + 0.36 * math.sin(yaw), 0.37])
    fwd = head + np.array([math.cos(yaw), math.sin(yaw), -math.tan(math.radians(10))])
    aim(cams[0], head, fwd)
    rgb, *_ = render(cams[0], n=12)
    save_png(rgb, f"{PIC}/robot/on_go2_head_0.37m.png")
    mast = np.array([go2_xy[0], go2_xy[1], 1.0])
    aim(cams[1], mast, mast + np.array([math.cos(yaw), math.sin(yaw), -math.tan(math.radians(20))]))
    rgb, *_ = render(cams[1], n=12)
    save_png(rgb, f"{PIC}/robot/on_go2_mast_1.0m.png")
    shots["head_cam"] = dict(eye=head.tolist(), pitch_deg=-10, hfov_deg=100)
    shots["mast_cam"] = dict(eye=mast.tolist(), pitch_deg=-20, hfov_deg=75)
    dump(dict(load_seconds=load_s, go2_usd=GO2, person_usd=PERSON, shots=shots), f"{OUT}/go2_people.json")
    og.shutdown()


if __name__ == "__main__":
    main()
