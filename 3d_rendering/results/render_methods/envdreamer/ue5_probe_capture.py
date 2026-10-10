"""Probe: can a packaged Unreal Engine 5 program render pictures offscreen on this machine?

This is NOT EnvDreamer (EnvDreamer needs the UE5 editor). It uses Microsoft/IAMAI Project AirSim's
"Blocks" demo (UE 5.2.1, MIT, 557 MB zip) because it is a ready-built UE5 Linux program that needs no
Epic account. It answers one question: does UE5's Vulkan renderer start without a display on the
RTX PRO 6000 Blackwell with driver 580, and return camera pictures to Python?

Run the program first, offscreen, in another shell:
  env -u DISPLAY /mnt/nvme/oliver/robot/render_methods/envdreamer/ue5_probe/Blocks/Blocks.sh \
      -RenderOffScreen -nosound -unattended
Then:
  /mnt/nvme/oliver/robot/render_methods/envdreamer/ue5_probe/env/bin/python ue5_probe_capture.py
"""
import json
import os
import sys
import time

import cv2
from projectairsim import Drone, ProjectAirSimClient, World
from projectairsim.types import Pose, Quaternion, Vector3
from projectairsim.utils import rpy_to_quaternion, unpack_image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ue5_probe")
CFG = ("/mnt/nvme/oliver/robot/render_methods/envdreamer/ue5_probe/pas_src/client/python/"
       "example_user_scripts/sim_config/")
os.makedirs(OUT, exist_ok=True)

client = ProjectAirSimClient()
t0 = time.time()
client.connect()
world = World(client, "scene_computer_vision.jsonc", delay_after_load_sec=2, sim_config_path=CFG)
t_load = time.time() - t0
cam = Drone(client, world, "CV")

# Camera heights 0.37 m and 1.0 m as in the shared test (NED frame: z is down, so negative).
poses = [("h037_level", 0.37, 0.0), ("h037_tilt15", 0.37, -15.0), ("h100_tilt15", 1.0, -15.0)]
records = []
for name, h, pitch_deg in poses:
    q = rpy_to_quaternion(0.0, pitch_deg * 3.14159265 / 180.0, 0.0)
    pose = Pose({"translation": Vector3({"x": 0.0, "y": 0.0, "z": -h}),
                 "rotation": Quaternion({"w": q[0], "x": q[1], "y": q[2], "z": q[3]}),
                 "frame_id": "DEFAULT_ID"})
    cam.set_pose(pose, True)
    time.sleep(0.5)
    t1 = time.time()
    imgs = cam.get_images("Camera", [0])
    dt = time.time() - t1
    img = unpack_image(imgs[0])
    path = os.path.join(OUT, f"blocks_{name}.png")
    cv2.imwrite(path, img)
    records.append({"file": os.path.basename(path), "height_m": h, "pitch_deg": pitch_deg,
                    "fov_deg": 90, "shape": list(img.shape), "seconds_to_get_image": round(dt, 3)})
    print(name, img.shape, f"{dt:.3f}s")

json.dump({"scene_load_seconds": round(t_load, 2), "pictures": records},
          open(os.path.join(OUT, "probe_views.json"), "w"), indent=2)
client.disconnect()
