"""Step 5: load HSSD home 107734254_176000121 itself into OmniGibson.

Every piece of HSSD furniture was imported into OmniGibson's object format (dataset "hssd-assets")
by hssd_og_import.py. Here each instance is placed with its HSSD pose, converted from Habitat's
y-up frame to Isaac's z-up frame. The walls and floors (HSSD "stage") are visual only; a hidden
floor plane gives the floor collision. HSSD homes have no lamps, so lights are added: a dome
light and one ceiling sphere light per room of the snapshot.

Then the six test spots are filled with BEHAVIOR objects using OmniGibson's samplers on the HSSD
furniture, and rendered at both camera heights. MODE=kitchen does only the kitchen view.
"""
import json
import math
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from og_common import OUT, PIC, RIGS, choose_view, dump, gpu_mem_mib, make_env, save_png, view_record  # noqa: E402

import numpy as np  # noqa: E402
import torch as th  # noqa: E402
from scipy.spatial.transform import Rotation  # noqa: E402

import omnigibson as og  # noqa: E402
from omnigibson import object_states as S  # noqa: E402
from omnigibson.objects.dataset_object import DatasetObject  # noqa: E402
from omnigibson.objects.light_object import LightObject  # noqa: E402

HSSD = "/mnt/nvme/oliver/robot/datasets/moving-eqa/scene_datasets/hssd-hab"
SCN = "107734254_176000121"
JOBS = "/mnt/nvme/oliver/robot/render_methods/behavior/hssd_import/jobs/all_result.json"
SNAP = json.load(open("/home/oliver/robot/dynamic_home_eqa/3d_rendering/results/lived_home/hssd_a/day_07/positions_1800.json"))
TYPEMAP = json.load(open(f"{OUT}/mapping/type_to_category.json"))
ASSETS = "/mnt/nvme/oliver/robot/render_methods/behavior/BEHAVIOR-1K/datasets/behavior-1k-assets/objects"
MODE = os.environ.get("MODE", "all")
C = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)  # Habitat (x, y up, z) -> Isaac (x, y, z up)
ART_FIX = Rotation.from_euler("x", float(os.environ.get("ART_FIX_DEG", "90")), degrees=True)  # OmniGibson drops the HSSD URDF root link and its -90 deg x turn

VIEWS = ["kitchen_kitchen_cabinet_by_the_range_countertop_by_the_range",
         "dining_room_dining_table_tabletop",
         "living_room_living_room_coffee_table_top",
         "bedroom_1_nightstand_by_the_main_bed_top_of_the_nightstand",
         "bathroom_2_bathroom_vanity_by_the_bathtub_vanity_top",
         "entryway_floor"]
if MODE == "kitchen":
    VIEWS = VIEWS[:1]


def to_isaac(t, q_wxyz, articulated=False):
    p = C @ np.asarray(t, float)
    R = Rotation.from_quat([q_wxyz[1], q_wxyz[2], q_wxyz[3], q_wxyz[0]]).as_matrix()
    Ri = Rotation.from_matrix(C @ R @ C.T)
    if articulated:
        Ri = Ri * ART_FIX
    return p, Ri.as_quat()


def cam_quat(yaw, pitch):
    f = np.array([math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), math.sin(pitch)])
    r = np.cross(f, [0, 0, 1.0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return Rotation.from_matrix(np.stack([r, u, -f], axis=1)).as_quat()


def main():
    jobs = {j["template"]: j for j in json.load(open(JOBS)) if j["status"] in ("ok", "exists")}
    inst = json.load(open(f"{HSSD}/scenes-articulated/{SCN}.scene_instance.json"))
    env, load_s = make_env({"type": "Scene", "use_floor_plane": True, "floor_plane_visible": False,
                            "use_skybox": False})
    scene = env.scene
    cams = list(env.external_sensors[0].values())
    t0 = time.time()
    og.sim.stop()
    furn = {}  # (instance_list, index) -> object
    stage = DatasetObject(name="hssd_stage", category="hssd_stage", model="qstage", dataset_name="hssd-assets",
                          fixed_base=True, visual_only=True)
    scene.add_object(stage)
    stage.set_position_orientation(position=th.zeros(3), orientation=th.tensor([0, 0, 0, 1.0]))
    skipped = []
    for lst, art in (("object_instances", False), ("articulated_object_instances", True)):
        for i, o in enumerate(inst[lst]):
            j = jobs.get(o["template_name"])
            if j is None:
                skipped.append(o["template_name"])
                continue
            sc = o.get("non_uniform_scale") or o.get("uniform_scale") or 1.0
            sc = np.abs(np.broadcast_to(np.asarray(sc, float), 3))
            sc = C @ sc
            obj = DatasetObject(name=f"hssd_{'a' if art else 's'}{i}", category=j["category"], model=j["model"],
                                dataset_name="hssd-assets", fixed_base=True, scale=th.tensor(np.abs(sc), dtype=th.float32))
            try:
                scene.add_object(obj)
            except Exception as e:  # e.g. "local transform is not orthogonal" on an HSSD oven door
                skipped.append(f"{o['template_name']} ({lst} {i}): {repr(e)[:160]}")
                print("SKIP", o["template_name"], repr(e)[:160], flush=True)
                try:
                    scene.remove_object(obj)
                except Exception:
                    pass
                continue
            p, q = to_isaac(o["translation"], o.get("rotation", [1, 0, 0, 0]), art)
            obj.set_position_orientation(position=th.tensor(p, dtype=th.float32), orientation=th.tensor(q, dtype=th.float32))
            furn[(lst, i)] = obj
    # lights
    dome = LightObject(name="dome", light_type="Dome", intensity=float(os.environ.get("DOME", "300")))
    scene.add_object(dome)
    rooms = {}
    for p in SNAP["places"].values():
        if p["furniture"] == "floor":
            rooms[p["room"]] = C @ np.asarray(p["geometry"]["center"], float)
    for r, c in rooms.items():
        lt = LightObject(name=f"light_{r}", light_type="Sphere", radius=0.15, intensity=float(os.environ.get("ROOM_LIGHT", "20000")))
        scene.add_object(lt)
        lt.set_position_orientation(position=th.tensor([c[0], c[1], 2.4], dtype=th.float32))
    og.sim.play()
    for _ in range(5):
        og.sim.step()
    arts = [o for (lst, _), o in furn.items() if lst == "articulated_object_instances"]
    for fo in arts:
        try:
            fo.set_joint_positions(th.zeros(fo.n_dof))
            fo.keep_still()
        except Exception as e:
            print("JOINT", fo.name, repr(e)[:100], flush=True)
    for _ in range(5):
        og.sim.step()
    build_s = time.time() - t0
    print("BUILT", len(furn), "objects", round(build_s, 1), "s, skipped", len(skipped), "gpu", gpu_mem_mib(), flush=True)

    # check that furniture sits where the snapshot says: spot heights vs the furniture's box top
    checks = []
    for pid, p in SNAP["places"].items():
        g = p["geometry"]
        if g.get("instance_list") is None:
            continue
        obj = furn.get((g["instance_list"], g["instance_index"]))
        if obj is None:
            continue
        lo, hi = [x.cpu().numpy() for x in obj.aabb]
        c = C @ np.asarray(g["center"], float)
        inside_xy = bool(lo[0] - 0.05 <= c[0] <= hi[0] + 0.05 and lo[1] - 0.05 <= c[1] <= hi[1] + 0.05)
        checks.append(dict(place=pid, spot=c.tolist(), box_lo=lo.tolist(), box_hi=hi.tolist(), spot_in_box_xy=inside_xy,
                           spot_z_minus_box_top=round(float(c[2] - hi[2]), 3)))
    ok = sum(c["spot_in_box_xy"] for c in checks)
    print("POSE CHECK", ok, "of", len(checks), "spots fall inside their furniture's box", flush=True)
    zc = [c for c in checks if "articulated" in str(c.get("place")) or True]
    arts_z = []
    for (lst, i), fo in furn.items():
        if lst == "articulated_object_instances":
            lo, hi = [x.cpu().numpy() for x in fo.aabb]
            arts_z.append((fo.name, round(float(lo[2]), 2), round(float(hi[2]), 2)))
    print("ART Z", arts_z[:12], flush=True)
    if os.environ.get("POSE_ONLY"):
        og.shutdown()
        return

    # ---------- fill the test spots ----------
    log, views, t_render = [], [], []
    rng = np.random.default_rng(3)
    used_models = {}
    for vid, spot in enumerate(VIEWS, 1):
        p = SNAP["places"][spot]
        g = p["geometry"]
        support = furn.get((g.get("instance_list"), g.get("instance_index"))) if g.get("instance_list") else None
        centre = C @ np.asarray(g["center"], float)
        keys = [k for k, o in SNAP["objects"].items() if o["place"] == spot]
        keys.sort(key=lambda k: SNAP["objects"][k]["reference_kind"] == "object")
        og.sim.stop()
        made = {}
        for k in keys:
            cat = TYPEMAP[SNAP["objects"][k]["type"]][0]
            if not cat:
                log.append(dict(obj=k, spot=spot, placed=False, why="no BEHAVIOR category"))
                continue
            models = sorted(os.listdir(os.path.join(ASSETS, cat)))
            i = used_models.get(cat, int(rng.integers(len(models))))
            used_models[cat] = i + 1
            o = DatasetObject(name=k, category=cat, model=models[i % len(models)])
            scene.add_object(o)
            o.set_position_orientation(position=th.tensor([60.0 + 1.5 * len(made), 60.0 + 3.0 * vid, 0.5]))  # parked on the floor plane, far away
            made[k] = o
        og.sim.play()
        og.sim.step()
        # Placement by computed pose (no physics): the snapshot gives each spot's centre and height on the
        # HSSD furniture, so objects are laid out in rows around that centre at that height; things on
        # another object go on its box top; things inside a closed thing stay hidden (not drawn).
        for fo in arts:
            try:
                fo.set_joint_positions(th.zeros(fo.n_dof))
                fo.keep_still()
            except Exception:
                pass
        area = max(0.05, float(g.get("area", 0.4)))
        side = math.sqrt(area) * 0.8
        order = [k for k in made if SNAP["objects"][k]["reference_kind"] != "object"]
        n = max(1, len(order))
        cols = max(1, int(math.ceil(math.sqrt(n))))
        h = float(g.get("height", 0.0))
        for idx, k in enumerate(order):
            o = made[k]
            lo, hi = [x.cpu().numpy() for x in o.aabb]
            r_, c_ = divmod(idx, cols)
            dx = (c_ - (cols - 1) / 2) * side / max(1, cols)
            dy = (r_ - (math.ceil(n / cols) - 1) / 2) * side / max(1, math.ceil(n / cols))
            pos, ori = o.get_position_orientation()
            off = pos.cpu().numpy() - (lo + hi) / 2
            tgt = np.array([centre[0] + dx, centre[1] + dy, h + (hi[2] - lo[2]) / 2 + 0.003]) + off
            o.set_position_orientation(position=th.tensor(tgt, dtype=th.float32))
            log.append(dict(obj=k, spot=spot, relation=SNAP["objects"][k]["relation"], placed=True,
                            how="computed pose at the snapshot spot centre and height"))
        for k, o in made.items():
            so = SNAP["objects"][k]
            if so["reference_kind"] != "object":
                continue
            ref = made.get(so["reference"])
            if so["hidden"] or so["relation"] == "inside" and SNAP["objects"].get(so["reference"], {}).get("holds") == "closed":
                o.visible = False
                log.append(dict(obj=k, spot=spot, relation=so["relation"], placed=True, hidden=True,
                                how="inside a closed thing: kept out of sight"))
                continue
            if ref is None:
                log.append(dict(obj=k, spot=spot, placed=False, why="reference not here"))
                continue
            rlo, rhi = [x.cpu().numpy() for x in ref.aabb]
            lo, hi = [x.cpu().numpy() for x in o.aabb]
            pos, ori = o.get_position_orientation()
            off = pos.cpu().numpy() - (lo + hi) / 2
            rc = (rlo + rhi) / 2
            if so["relation"] in ("on_top", "inside"):
                tgt = np.array([rc[0], rc[1], rhi[2] + (hi[2] - lo[2]) / 2 + 0.003]) + off
            else:  # next_to
                tgt = np.array([rhi[0] + (hi[0] - lo[0]) / 2 + 0.02, rc[1], rlo[2] + (hi[2] - lo[2]) / 2]) + off
            o.set_position_orientation(position=th.tensor(tgt, dtype=th.float32))
            log.append(dict(obj=k, spot=spot, relation=so["relation"], placed=True,
                            how=f"computed pose {so['relation']} {so['reference']}"))
        og.sim.render()
        placed = [made[r["obj"]] for r in log if r.get("spot") == spot and r.get("placed") and not r.get("hidden")]
        pts = np.array([o.get_position_orientation()[0].cpu().numpy() for o in placed])
        c2 = centre.copy()  # aim at the snapshot's spot
        ext = float(np.ptp(pts[:, :2], axis=0).max()) + 0.3 if len(pts) > 1 else 0.8
        room_c = rooms.get(p["room"], centre)
        boxes = [[x.cpu().numpy() for x in fo.aabb] for fo in furn.values()]

        def eye_ok(eye):
            return not any(np.all(eye > lo - 0.1) and np.all(eye < hi + 0.1) for lo, hi in boxes)

        for ri, rig in enumerate(RIGS):
            cam = cams[ri]
            best = choose_view(cam, rig, c2, ext, placed, eye_ok, floor_z=0.0,
                               yaw_first=math.atan2(room_c[1] - c2[1], room_c[0] - c2[0]))
            if best is None:
                print("NOVIEW", spot, rig, flush=True)
                continue
            rgb, rec = view_record(best, rig, list(made.values()) + ([support] if support is not None else []), cam,
                                   extra=dict(view=vid, spot=spot, snapshot_objects=keys,
                                              placed_objects=[o.name for o in placed],
                                              frame="Isaac world = HSSD Habitat world with (x, y, z) -> (x, -z, y); z up, metres"))
            fname = f"v{vid}_{spot.split('_')[0]}_{rig}.png"
            save_png(rgb, f"{PIC}/hssd_home/{fname}")
            rec["image"] = f"pictures/hssd_home/{fname}"
            t_render.append(rec["render_seconds_6_frames"] / 6)
            views.append(rec)
            print("VIEW", vid, rig, "shows", rec["objects_over_0p05pct"], "of", rec["objects"], "eye", rec["eye"], flush=True)
    dump(dict(load_seconds=load_s, build_seconds=build_s, skipped_templates=skipped, pose_checks=checks,
              render_seconds_mean=float(np.mean(t_render)) if t_render else None, gpu_mib=gpu_mem_mib(),
              placement=log, views=views), f"{OUT}/hssd_home_views.json")
    og.shutdown()


if __name__ == "__main__":
    main()
