"""Step 4: robots and people.

- Lists OmniGibson's robots.
- Drives OmniGibson's Freight base (two wheels) through BEHAVIOR's Rs_int with two cameras carried on
  it, one at 0.37 m (100 degree lens) and one at 1.0 m (75 degree lens), and saves pictures.
- OmniGibson has no quadruped and no people. Isaac Sim's public asset server (no login) has a Unitree
  Go2 model and posed/animatable people; this references both into the same stage as plain USD and
  takes a picture, to show they can be shown (static; not driven, not animated).
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from og_common import OUT, PIC, RIGS, cam_quat, dump, focal_for_hfov, gpu_mem_mib, render, save_png  # noqa: E402

import numpy as np  # noqa: E402
import torch as th  # noqa: E402

import omnigibson as og  # noqa: E402
import omnigibson.lazy as lazy  # noqa: E402
from omnigibson.robots import REGISTERED_ROBOTS  # noqa: E402

ASSET_ROOT = "https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1"
GO2 = f"{ASSET_ROOT}/Isaac/Robots/Unitree/Go2/go2.usd"
PEOPLE = [f"{ASSET_ROOT}/Isaac/People/Characters/F_Business_02/F_Business_02.usd",
          f"{ASSET_ROOT}/Isaac/People/Characters/male_adult_construction_05_new/male_adult_construction_05_new.usd"]


def main():
    out = dict(registered_robots=sorted(REGISTERED_ROBOTS.keys() if hasattr(REGISTERED_ROBOTS, "keys") else [getattr(r, "__name__", str(r)) for r in REGISTERED_ROBOTS]))
    print("ROBOTS", out["registered_robots"], flush=True)
    sensors = []
    for i, (rig, spec) in enumerate(RIGS.items()):
        sensors.append({"sensor_type": "VisionSensor", "name": f"cam_{i}", "relative_prim_path": f"/cam_{i}",
                        "modalities": ["rgb", "depth_linear"],
                        "sensor_kwargs": {"image_height": 480, "image_width": 640,
                                          "focal_length": focal_for_hfov(spec["hfov"]), "clipping_range": (0.01, 100.0)},
                        "position": th.tensor([0.0, 0.0, 3.0]), "orientation": th.tensor([0, 0, 0, 1.0])})
    cfg = {"scene": {"type": "InteractiveTraversableScene", "scene_model": "Rs_int"},
           "robots": [{"type": "Freight", "obs_modalities": ["rgb"], "position": [0.0, 0.0, 0.0],
                       "action_normalize": True, "action_type": "continuous"}],
           "env": {"external_sensors": sensors}}
    t0 = time.time()
    env = og.Environment(configs=cfg)
    out["load_seconds"] = round(time.time() - t0, 1)
    robot = env.scene.robots[0]
    cams = list(env.external_sensors[0].values())
    env.reset()
    # carry the two cameras on the robot: 0.10 m ahead of the base centre, at 0.37 m and 1.0 m
    def mount():
        pos, ori = robot.get_position_orientation()
        from scipy.spatial.transform import Rotation
        yaw = float(Rotation.from_quat(ori.cpu().numpy()).as_euler("xyz")[2])
        p = pos.cpu().numpy()
        for cam, (rig, spec) in zip(cams, RIGS.items()):
            eye = np.array([p[0] + 0.10 * math.cos(yaw), p[1] + 0.10 * math.sin(yaw), spec["height"]])
            pitch = -math.radians(10) if rig.startswith("go2") else -math.radians(20)
            cam.set_position_orientation(position=th.tensor(eye, dtype=th.float32),
                                         orientation=th.tensor(cam_quat(yaw, pitch), dtype=th.float32), frame="scene")
        return p, yaw
    track = []
    # drive: forward, turn, forward (Freight action = [forward velocity, turn rate], normalised)
    plan = [(0.6, 0.0)] * 60 + [(0.0, 0.6)] * 40 + [(0.6, 0.0)] * 60
    for i, (v, w) in enumerate(plan):
        env.step(th.tensor([v, w], dtype=th.float32))
        if i % 40 == 0 or i == len(plan) - 1:
            p, yaw = mount()
            for cam, rig in zip(cams, RIGS):
                rgb, _, _, _ = render(cam, n=3)
                save_png(rgb, f"{PIC}/robot/drive_step{i:03d}_{rig}.png")
            track.append(dict(step=i, base_xy=[round(float(p[0]), 3), round(float(p[1]), 3)],
                              yaw_deg=round(math.degrees(yaw), 1)))
            print("DRIVE", track[-1], flush=True)
    out["drive_track"] = track
    # ---------- Go2 and people from Isaac Sim's asset server, as plain USD references ----------
    stage = lazy.isaacsim.core.utils.stage.get_current_stage()
    p, yaw = mount()
    placed = {}
    for name, url, pos, yaw_deg in [("go2_model", GO2, (p[0] + 1.2 * math.cos(yaw), p[1] + 1.2 * math.sin(yaw), 0.0), 180),
                                    ("person_a", PEOPLE[0], (p[0] + 2.4 * math.cos(yaw) + 0.6, p[1] + 2.4 * math.sin(yaw), 0.0), 200),
                                    ("person_b", PEOPLE[1], (p[0] + 2.6 * math.cos(yaw) - 0.7, p[1] + 2.6 * math.sin(yaw), 0.0), 160)]:
        t1 = time.time()
        try:
            with og.sim.editing_usd() if hasattr(og.sim, "editing_usd") else nullctx():
                prim = stage.DefinePrim(f"/World/{name}", "Xform")
                prim.GetReferences().AddReference(url)
                xf = lazy.pxr.UsdGeom.Xformable(prim)
                xf.ClearXformOpOrder()
                xf.AddTranslateOp().Set(lazy.pxr.Gf.Vec3d(float(pos[0]), float(pos[1]), float(pos[2])))
                xf.AddRotateZOp().Set(float(math.degrees(yaw) + yaw_deg))
            placed[name] = dict(url=url, ok=True, seconds=round(time.time() - t1, 1), position=[float(x) for x in pos])
        except Exception as e:
            placed[name] = dict(url=url, ok=False, error=repr(e))
        print("REF", name, placed[name], flush=True)
    for _ in range(30):
        og.sim.render()
    for cam, rig in zip(cams, RIGS):
        rgb, _, _, _ = render(cam, n=10)
        save_png(rgb, f"{PIC}/robot/go2_and_people_{rig}.png")
    # one more from the side, raised, to see the Go2 whole
    cam = cams[1]
    gx, gy = p[0] + 1.2 * math.cos(yaw), p[1] + 1.2 * math.sin(yaw)
    eye = np.array([gx + 1.3 * math.cos(yaw + 1.2), gy + 1.3 * math.sin(yaw + 1.2), 1.0])
    v = np.array([gx, gy, 0.3]) - eye
    cam.set_position_orientation(position=th.tensor(eye, dtype=th.float32),
                                 orientation=th.tensor(cam_quat(math.atan2(v[1], v[0]),
                                                                math.atan2(v[2], math.hypot(v[0], v[1]))),
                                                       dtype=th.float32), frame="scene")
    rgb, _, _, _ = render(cam, n=10)
    save_png(rgb, f"{PIC}/robot/go2_side_raised.png")
    out["references"] = placed
    out["gpu_mib"] = gpu_mem_mib()
    dump(out, f"{OUT}/robot_people.json")
    og.shutdown()


class nullctx:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


if __name__ == "__main__":
    main()
