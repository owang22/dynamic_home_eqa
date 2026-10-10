"""Step 3: reload the placed BEHAVIOR house and render the six test views at both camera heights,
then one cabinet shut and open with what is inside it.

Camera choice: choose_view() in og_common (8 directions x 2 distances around the spot, eye inside
the room's floor box and outside every piece of furniture, keep the pose where most of the spot's
objects show). Share of picture per object: hide-and-compare on depth (view_record()).
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from og_common import OUT, PIC, RIGS, choose_view, dump, gpu_mem_mib, make_env, render, save_png, view_record, visible_share  # noqa: E402

import numpy as np  # noqa: E402
import torch as th  # noqa: E402

import omnigibson as og  # noqa: E402
from omnigibson import object_states as S  # noqa: E402
from omnigibson.macros import gm  # noqa: E402

# The saved placed scene holds a particle system ("sludge"), which only loads with GPU dynamics on.
gm.USE_GPU_DYNAMICS = True
gm.ENABLE_TRANSITION_RULES = False

SNAP = json.load(open("/home/oliver/robot/dynamic_home_eqa/3d_rendering/results/lived_home/hssd_a/day_07/positions_1800.json"))
LOG = json.load(open(f"{OUT}/mapping/placement_log.json"))
ROOM = {"kitchen": "kitchen_0", "dining_room": "dining_room_0", "living_room": "living_room_0",
        "bedroom_1": "bedroom_0", "bathroom_2": "bathroom_0", "entryway": "entryway_0"}
VIEWS = ["kitchen_kitchen_cabinet_by_the_range_countertop_by_the_range",
         "dining_room_dining_table_tabletop",
         "living_room_living_room_coffee_table_top",
         "bedroom_1_nightstand_by_the_main_bed_top_of_the_nightstand",
         "bathroom_2_bathroom_vanity_by_the_bathtub_vanity_top",
         "entryway_floor"]
STRUCT = {"floors", "ceilings", "walls", "roof", "downlight", "electric_switch", "fixed_window", "baseboard",
          "room_light", "painting", "wall_mounted_light", "showerhead", "railing", "range_hood", "door",
          "sliding_door", "mirror", "openable_window", "wall_clock", "wall_mounted_tv", "lawn", "driveway"}


def main():
    env, load_s = make_env({"type": "InteractiveTraversableScene", "scene_model": "house_single_floor",
                            "scene_file": f"{OUT}/mapping/placed_scene.json"})
    scene = env.scene
    cams = list(env.external_sensors[0].values())
    print("LOADED", round(load_s, 1), "gpu", gpu_mem_mib(), flush=True)
    for _ in range(10):
        og.sim.step()
    reg = {o.name: o for o in scene.objects}
    floors = {o.in_rooms[0]: o for o in scene.objects if o.category == "floors" and o.in_rooms}
    furn_boxes = [[x.cpu().numpy() for x in o.aabb] for o in scene.objects
                  if o.category not in STRUCT and o.name not in SNAP["objects"]]
    views, t_one = [], []
    for vid, spot in enumerate(VIEWS, 1):
        recs = [r for r in LOG if r.get("place") == spot]
        held = [reg[r["obj"]] for r in recs if r.get("sampled") and r["obj"] in reg]
        want = [k for k, o in SNAP["objects"].items() if o["place"] == spot]
        support = None
        for r in recs:
            if r.get("reference_kind") == "place" and r.get("target") in reg:
                support = reg[r["target"]]
                break
        if held:
            pts = np.array([o.get_position_orientation()[0].cpu().numpy() for o in held])
            centre = pts.mean(0)
            ext = float(np.ptp(pts[:, :2], axis=0).max()) + 0.3 if len(pts) > 1 else 0.8
        else:
            lo, hi = [x.cpu().numpy() for x in support.aabb]
            centre, ext = (lo + hi) / 2, 0.8
        fl = floors[ROOM[SNAP["places"][spot]["room"]]]
        flo, fhi = [x.cpu().numpy() for x in fl.aabb]
        room_c = (flo + fhi) / 2

        def eye_ok(eye, flo=flo, fhi=fhi):
            if not (flo[0] + 0.15 < eye[0] < fhi[0] - 0.15 and flo[1] + 0.15 < eye[1] < fhi[1] - 0.15):
                return False
            return not any(np.all(eye > lo - 0.1) and np.all(eye < hi + 0.1) for lo, hi in furn_boxes)

        for ri, rig in enumerate(RIGS):
            cam = cams[ri]
            best = choose_view(cam, rig, centre, ext, held, eye_ok, floor_z=float(fhi[2]),
                               yaw_first=math.atan2(room_c[1] - centre[1], room_c[0] - centre[0]))
            if best is None:
                print("NOVIEW", spot, rig, flush=True)
                continue
            rgb, rec = view_record(best, rig, held + ([support] if support is not None else []), cam,
                                   extra=dict(view=vid, spot=spot, snapshot_objects=want,
                                              placed_objects=[o.name for o in held],
                                              support=support.name if support is not None else None,
                                              frame="OmniGibson world (house_single_floor), z up, metres"))
            fname = f"v{vid}_{spot.split('_')[0]}_{rig}.png"
            save_png(rgb, f"{PIC}/behavior_house/{fname}")
            rec["image"] = f"pictures/behavior_house/{fname}"
            t_one.append(rec["render_seconds_6_frames"] / 6)
            views.append(rec)
            print("VIEW", vid, rig, "shows", rec["objects_over_0p05pct"], "of", rec["objects"], "eye", rec["eye"], flush=True)

    # ---------- a cabinet shut, then open, with what was sampled inside it ----------
    demo = {}
    inside = {}
    for r in LOG:
        if r.get("relation_used") == "inside" and r.get("sampled") and r.get("holds_after_settle"):
            inside.setdefault(r["target"], []).append(r["obj"])
    cands = [t for t in inside if t in reg and S.Open in reg[t].states and reg[t].in_rooms
             and reg[t].in_rooms[0] == "kitchen_0"] or [t for t in inside if t in reg and S.Open in reg[t].states]
    if cands:
        tname = max(cands, key=lambda t: len(inside[t]))
        cab = reg[tname]
        things = [reg[n] for n in inside[tname] if n in reg]
        lo, hi = [x.cpu().numpy() for x in cab.aabb]
        c = (lo + hi) / 2
        fl = floors.get(cab.in_rooms[0]) if cab.in_rooms else None
        flo, fhi = [x.cpu().numpy() for x in fl.aabb] if fl else (lo - 3, hi + 3)
        room_c = (flo + fhi) / 2

        def eye_ok2(eye):
            if not (flo[0] + 0.15 < eye[0] < fhi[0] - 0.15 and flo[1] + 0.15 < eye[1] < fhi[1] - 0.15):
                return False
            return not any(np.all(eye > lo2 - 0.1) and np.all(eye < hi2 + 0.1) for lo2, hi2 in furn_boxes)

        cam = cams[1]
        best = choose_view(cam, "raised_1.0m", c, float(max(hi[:2] - lo[:2])) + 0.6, [cab], eye_ok2,
                           floor_z=float(fhi[2]), yaw_first=math.atan2(room_c[1] - c[1], room_c[0] - c[0]))
        rgb_c, rec_c = view_record(best, "raised_1.0m", things + [cab], cam)
        save_png(rgb_c, f"{PIC}/open_close/{tname}_shut.png")
        cab.states[S.Open].set_value(True, fully=True)
        for _ in range(3):
            og.sim.step()
        rgb_o, rec_o = view_record(best, "raised_1.0m", things + [cab], cam)
        save_png(rgb_o, f"{PIC}/open_close/{tname}_open.png")
        still_inside = {o.name: bool(o.states[S.Inside].get_value(cab)) for o in things}
        demo = dict(cabinet=tname, category=cab.category, things_inside=[o.name for o in things],
                    shut=rec_c, open=rec_o, still_inside_after_opening=still_inside,
                    images=[f"pictures/open_close/{tname}_shut.png", f"pictures/open_close/{tname}_open.png"])
        print("DEMO", tname, len(things), "inside; shut shows", rec_c["objects_over_0p05pct"], "open shows",
              rec_o["objects_over_0p05pct"], flush=True)
    dump(dict(load_seconds=load_s, render_seconds_per_frame_mean=float(np.mean(t_one)) if t_one else None,
              gpu_mib=gpu_mem_mib(), views=views, open_close_demo=demo), f"{OUT}/views.json")
    og.shutdown()


if __name__ == "__main__":
    main()
