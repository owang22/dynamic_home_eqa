"""Shared helpers for the OmniGibson trial: start an environment with free cameras, aim a
camera, render, and measure how much of the picture each object fills.

Run every script with
  OMNIGIBSON_HEADLESS=1 OMNI_KIT_ACCEPT_EULA=YES /mnt/nvme/oliver/robot/render_methods/behavior/conda_env/bin/python <script>
"""
import json
import math
import os
import subprocess
import time

import numpy as np
import torch as th

import omnigibson as og
from omnigibson.macros import gm

OUT = "/home/oliver/robot/dynamic_home_eqa/3d_rendering/results/render_methods/behavior_omnigibson"
PIC = os.path.join(OUT, "pictures")
W, H = 640, 480
APERTURE = 20.995  # OmniGibson's default horizontal aperture (mm)


def focal_for_hfov(hfov_deg):
    """Focal length (mm) that gives this horizontal field of view with the default aperture."""
    return APERTURE / (2 * math.tan(math.radians(hfov_deg) / 2))


# Two rigs from the shared test: Go2 built-in camera and a raised camera.
RIGS = {"go2_0.37m": dict(height=0.37, hfov=100.0, max_tilt=15.0),
        "raised_1.0m": dict(height=1.0, hfov=75.0, max_tilt=None)}


def gpu_mem_mib():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=20).stdout
        return int(out.strip().splitlines()[0])
    except Exception:
        return -1


def make_env(scene_cfg, n_cams=2, hq=False):
    gm.ENABLE_HQ_RENDERING = hq
    sensors = []
    for i, (rig, spec) in enumerate(list(RIGS.items())[:n_cams]):
        sensors.append({
            "sensor_type": "VisionSensor", "name": f"cam_{i}", "relative_prim_path": f"/cam_{i}",
            "modalities": os.environ.get("OG_MODALITIES", "rgb,depth_linear").split(","),
            "sensor_kwargs": {"image_height": H, "image_width": W, "focal_length": focal_for_hfov(spec["hfov"]),
                              "clipping_range": (0.01, 100.0)},
            "position": th.tensor([0.0, 0.0, 5.0]), "orientation": th.tensor([0.0, 0.0, 0.0, 1.0]),
        })
    cfg = {"scene": scene_cfg, "env": {"external_sensors": sensors}}
    t0 = time.time()
    env = og.Environment(configs=cfg)
    return env, time.time() - t0


def look_at_quat(eye, target):
    """Quaternion (x, y, z, w) for an Isaac camera at eye looking at target (z up).
    Isaac cameras look along their local -Z with +Y up."""
    eye, target = np.asarray(eye, float), np.asarray(target, float)
    f = target - eye
    f /= np.linalg.norm(f)
    up = np.array([0.0, 0.0, 1.0])
    r = np.cross(f, up)
    if np.linalg.norm(r) < 1e-6:
        r = np.array([1.0, 0.0, 0.0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    R = np.stack([r, u, -f], axis=1)  # columns: camera x, y, z in world
    from scipy.spatial.transform import Rotation
    return Rotation.from_matrix(R).as_quat()  # x, y, z, w


def aim(cam, eye, target):
    q = look_at_quat(eye, target)
    cam.set_position_orientation(position=th.tensor(eye, dtype=th.float32),
                                 orientation=th.tensor(q, dtype=th.float32), frame="scene")
    return q


def relabel_all(scene):
    """Give every object its own semantic class (its name). Instance segmentation crashes Isaac Sim 5.1
    here (segfault in omni.syntheticdata), so per-object masks come from semantic segmentation instead."""
    import omnigibson.lazy as lazy
    sem = lazy.isaacsim.core.utils.semantics
    with og.sim.editing_usd():
        for o in scene.objects:
            try:
                sem.upgrade_prim_semantics_to_labels(prim=o._prim)
                sem.remove_labels(o._prim, instance_name="class")
                sem.add_labels(prim=o._prim, labels=[o.name.lower()], instance_name="class")
            except Exception as e:
                print("RELABEL FAIL", o.name, repr(e)[:100], flush=True)


def render(cam, n=3):
    """Render n frames (the first frames after a move can lag) and return rgb, seg, {id: name}, depth.
    Reads the annotators directly (OmniGibson's own get_obs asserts every label is a known category)."""
    for _ in range(n):
        if os.environ.get("OG_RENDER_MODE", "render") == "step":
            og.sim.step()
        else:
            og.sim.render()
    ann = cam._annotators
    rgb = np.asarray(ann["rgb"].get_data())[..., :3].astype(np.uint8)
    seg, idm, depth = np.zeros(rgb.shape[:2], np.int64), {}, None
    if "seg_semantic" in ann:
        raw = ann["seg_semantic"].get_data()
        seg = np.asarray(raw["data"]).astype(np.int64)
        idm = {int(k): v.get("class", "") for k, v in raw["info"]["idToLabels"].items()}
    if "depth_linear" in ann:
        depth = np.squeeze(np.asarray(ann["depth_linear"].get_data()))
    return rgb, seg, idm, depth


def project(eye, q_xyzw, hfov_deg, pts):
    """Pixel (u, v) and depth along the view axis of world points, for an Isaac camera (looks along -Z)."""
    from scipy.spatial.transform import Rotation
    R = Rotation.from_quat(q_xyzw).as_matrix()
    pc = (np.asarray(pts, float) - np.asarray(eye, float)) @ R  # world -> camera frame
    f = W / (2 * math.tan(math.radians(hfov_deg) / 2))
    z = -pc[:, 2]
    with np.errstate(divide="ignore", invalid="ignore"):
        u = W / 2 + f * pc[:, 0] / z
        v = H / 2 - f * pc[:, 1] / z
    return u, v, z


def quick_visible(depth, eye, q, hfov_deg, objs):
    """Cheap test used to choose a camera direction: is each object's box centre in the frame and not
    hidden behind something nearer (one depth picture)."""
    out = {}
    for o in objs:
        lo, hi = [x.cpu().numpy() for x in o.aabb]
        c = (lo + hi) / 2
        u, v, z = project(eye, q, hfov_deg, [c])
        u, v, z = float(u[0]), float(v[0]), float(z[0])
        ok = z > 0.05 and 0 <= u < W and 0 <= v < H
        if ok and depth is not None:
            d = float(depth[int(v), int(u)])
            ok = d > z - max(0.08, 0.5 * float(np.max(hi - lo)))
        out[o.name] = bool(ok)
    return out


def visible_share(cam, objs, n=int(os.environ.get("VIS_FRAMES", "5"))):
    """Share of the picture (percent) where each object is the nearest thing, measured by hiding the
    object and seeing which pixels' depth changes. (Isaac Sim's segmentation annotators crash here.)"""
    _, _, _, d0 = render(cam, n=n)
    out = {}
    for o in objs:
        was = o.visible
        if not was:  # already hidden (e.g. inside a closed bag): it fills nothing
            out[o.name] = 0.0
            continue
        o.visible = False
        _, _, _, d1 = render(cam, n=n)
        o.visible = was
        a, b = np.nan_to_num(d0, posinf=1e3), np.nan_to_num(d1, posinf=1e3)
        m = np.abs(b - a) > 0.002
        out[o.name] = round(100.0 * float(m.mean()), 3)
    render(cam, n=n)
    return out


def coverage(seg, id_map):
    """Share of the picture (percent) filled by each object name."""
    ids, counts = np.unique(seg, return_counts=True)
    tot = seg.size
    out = {}
    for i, c in zip(ids.tolist(), counts.tolist()):
        name = id_map.get(i, id_map.get(str(i), f"id{i}"))
        out[name] = round(100.0 * c / tot, 3)
    return out


def save_png(rgb, path):
    from PIL import Image
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(rgb).save(path)


def dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w"), indent=1, default=lambda x: x.tolist() if hasattr(x, "tolist") else str(x))


def cam_quat(yaw, pitch):
    """Camera looking along heading yaw (rad, from +x) with pitch (rad, + up)."""
    from scipy.spatial.transform import Rotation
    f = np.array([math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), math.sin(pitch)])
    r = np.cross(f, [0, 0, 1.0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return Rotation.from_matrix(np.stack([r, u, -f], axis=1)).as_quat()


def choose_view(cam, rig, centre, ext, objs, eye_ok, floor_z=0.0, yaw_first=None):
    """Try 8 directions x 2 distances around centre; keep the camera pose where most of objs show.
    eye_ok(eye) -> bool rejects eyes outside the room or inside furniture."""
    spec = RIGS[rig]
    hf = math.radians(spec["hfov"])
    base_d = max(0.7, (ext / 2) / math.tan(hf / 2 * 0.7))
    dists = [base_d + 0.4, base_d + 0.9] if rig.startswith("go2") else [base_d, base_d + 0.4]
    y0 = 0.0 if yaw_first is None else yaw_first
    best, tried = None, 0
    for d in dists:
        for k in [0, 1, -1, 2, -2, 3, -3, 4]:
            yo = y0 + k * math.pi / 4
            eye = np.array([centre[0] + d * math.cos(yo), centre[1] + d * math.sin(yo), floor_z + spec["height"]])
            if not eye_ok(eye):
                continue
            vec = np.asarray(centre) - eye
            yaw = math.atan2(vec[1], vec[0])
            pitch = math.atan2(vec[2], math.hypot(vec[0], vec[1]))
            if spec["max_tilt"] is not None:
                pitch = min(0.0, max(-math.radians(spec["max_tilt"]), pitch))
            q = cam_quat(yaw, pitch)
            cam.set_position_orientation(position=th.tensor(eye, dtype=th.float32),
                                         orientation=th.tensor(q, dtype=th.float32), frame="scene")
            rgb, _, _, depth = render(cam, n=4)
            tried += 1
            vis = quick_visible(depth, eye, q, spec["hfov"], objs)
            score = (sum(vis.values()), -abs(k))
            if best is None or score > best["score"]:
                best = dict(score=score, eye=eye, q=q, yaw=yaw, pitch=pitch, rgb=rgb, depth=depth, d=d, quick=vis)
    if best is not None:
        cam.set_position_orientation(position=th.tensor(best["eye"], dtype=th.float32),
                                     orientation=th.tensor(best["q"], dtype=th.float32), frame="scene")
        best["tried"] = tried
    return best


def view_record(best, rig, objs, cam, extra=None):
    """Final picture plus measured share of picture per object (hide-and-compare)."""
    spec = RIGS[rig]
    t = time.time()
    rgb, _, _, depth = render(cam, n=6)
    t_one = time.time() - t
    share = visible_share(cam, objs)
    vfov = 2 * math.degrees(math.atan(math.tan(math.radians(spec["hfov"]) / 2) * H / W))
    rec = dict(rig=rig, eye=[round(float(x), 3) for x in best["eye"]], quat_xyzw=[round(float(x), 4) for x in best["q"]],
               yaw_deg=round(math.degrees(best["yaw"]), 1), pitch_deg=round(math.degrees(best["pitch"]), 1),
               hfov_deg=spec["hfov"], vfov_deg=round(vfov, 1), distance_m=round(float(best["d"]), 2),
               width=W, height=H, poses_tried=best.get("tried"), render_seconds_6_frames=round(t_one, 3),
               share_of_picture_pct=dict(sorted(share.items(), key=lambda x: -x[1])),
               objects_over_0p05pct=sum(v > 0.05 for v in share.values()), objects=len(objs))
    if extra:
        rec.update(extra)
    return rgb, rec
