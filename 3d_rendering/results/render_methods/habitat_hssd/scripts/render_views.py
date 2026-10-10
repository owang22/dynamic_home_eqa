"""The six test views at two camera heights, plus an open drawer and the two residents.

    ~/miniconda3/envs/dynamic_eqa/bin/python render_views.py

Camera rules
  low   0.37 m above the floor, 100-degree lens (horizontal), 640x480, tilt between 0 and 15
        degrees down (the Go2's own camera).
  high  1.0 m, 75-degree lens, 640x480, aimed straight at the things on the spot.
Where to stand: every navigable floor point 0.6-3.2 m from the middle of the spot's visible
things (rings 0.15 m apart, 24 bearings). Each is scored on a 160x120 picture of object ids:
the sum over the spot's things of min(share of picture, 1.5%) / 1.5%, plus up to 0.5 for the
spot's furniture filling up to 30% of the picture. The best one is rendered at 640x480.
Writes pictures/*.jpg, pictures/*_ids.png (object outlines for checking) and views.json.
"""
import json
import math
import os
import subprocess
import sys
import threading
import time

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import scene  # noqa: E402

W, H = 640, 480
LENSES = {"low": dict(height=0.37, hfov=100.0, max_down=15.0, max_up=0.0),
          "high": dict(height=1.0, hfov=75.0, max_down=60.0, max_up=30.0)}
VIEWS = ["kitchen_kitchen_cabinet_by_the_range_countertop_by_the_range",
         "dining_room_dining_table_tabletop",
         "living_room_living_room_coffee_table_top",
         "bedroom_1_nightstand_by_the_main_bed_top_of_the_nightstand",
         "bathroom_2_bathroom_vanity_by_the_bathtub_vanity_top",
         "entryway_floor"]
SHORT = ["1_kitchen_counter", "2_dining_table", "3_coffee_table", "4_nightstand", "5_vanity", "6_entryway_floor"]
PIC = common.OUT / "pictures"
PIC.mkdir(exist_ok=True)


class GpuWatch(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.peak, self.stop, self.own = 0, False, 0

    def run(self):
        while not self.stop:
            try:
                out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used",
                                      "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10).stdout
                self.peak = max(self.peak, int(out.strip().splitlines()[0]))
                # this process's own share, from the process table (a 'G' graphics process)
                table = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=10).stdout
                for line in table.splitlines():
                    if f" {os.getpid()} " in line and "MiB" in line:
                        self.own = max(self.own, int(line.split("MiB")[0].split()[-1]))
            except Exception:
                pass
            time.sleep(0.5)


def cameras():
    out = []
    for name, lens in LENSES.items():
        out += [dict(uuid=f"colour_{name}", kind="colour", width=W, height=H, hfov=lens["hfov"]),
                dict(uuid=f"ids_{name}", kind="ids", width=W, height=H, hfov=lens["hfov"]),
                dict(uuid=f"depth_{name}", kind="depth", width=W, height=H, hfov=lens["hfov"]),
                dict(uuid=f"small_{name}", kind="ids", width=160, height=120, hfov=lens["hfov"])]
    return out


def walkable(home, x, z):
    """On the robot's walkable floor (navmesh, 0.2 m body radius). The navmesh sits at
    y = 0.17 here, so test by snapping rather than with is_navigable at the floor height."""
    q = home.sim.pathfinder.snap_point(np.array([x, 0.17, z], dtype=np.float32))
    return bool(np.isfinite(q[0]) and math.hypot(q[0] - x, q[2] - z) < 0.03 and abs(q[1] - 0.17) < 0.1)


def aim(eye, target, lens):
    d = np.array(target) - np.array(eye)
    yaw = math.atan2(d[0], d[2])
    pitch = math.degrees(math.atan2(d[1], math.hypot(d[0], d[2])))
    pitch = max(-lens["max_down"], min(lens["max_up"], pitch))
    p = math.radians(pitch)
    look = np.array(eye) + np.array([math.sin(yaw) * math.cos(p), math.sin(p), math.cos(yaw) * math.cos(p)])
    return look, math.degrees(yaw), pitch


def spot_things(home, place):
    return [oid for oid, o in home.snap["objects"].items() if o["place"] == place]


def middle_of(home, oids):
    pts = []
    for oid in oids:
        r = home.records[oid]
        if r.get("placed") and not r["hidden_in_snapshot"]:
            lo, hi = common.box_of(home.things[oid])
            pts.append((lo + hi) / 2)
    return np.mean(pts, axis=0) if pts else None


def choose_stand(home, place, oids, lens_name, furniture_ids, nearest=0.6):
    lens = LENSES[lens_name]
    target = middle_of(home, oids)
    if target is None:
        target = np.array(home.snap["places"][place]["geometry"]["center"])
    sids = {home.facts[o]["sid"] for o in oids if o in home.facts and home.records[o].get("placed")}
    best = None
    tried = 0
    for d in np.arange(nearest, 3.21, 0.15):
        for b in np.arange(0, 2 * math.pi, math.pi / 12):
            x, z = target[0] + d * math.sin(b), target[2] + d * math.cos(b)
            if not walkable(home, x, z):
                continue
            tried += 1
            eye = np.array([x, lens["height"], z])
            look, yaw, pitch = aim(eye, target, lens)
            common.look_from(home.sim, eye, look)
            ids = home.shoot(f"small_{lens_name}")[f"small_{lens_name}"]
            n = ids.size
            score = 0.0
            vals, counts = np.unique(ids, return_counts=True)
            share = dict(zip(vals.tolist(), (counts / n).tolist()))
            for s in sids:
                score += min(share.get(s, 0.0), 0.015) / 0.015
            fshare = sum(share.get(f, 0.0) for f in furniture_ids)
            score += 0.5 * min(fshare, 0.3) / 0.3
            if best is None or score > best[0]:
                best = (score, eye, look, yaw, pitch, d)
    return best, tried, target


def picture(home, lens_name, eye, look, name, highlight):
    common.look_from(home.sim, eye, look)
    t0 = time.time()
    shot = home.shoot(f"colour_{lens_name}", f"ids_{lens_name}", f"depth_{lens_name}")
    took = time.time() - t0
    colour = shot[f"colour_{lens_name}"][:, :, :3]
    ids = shot[f"ids_{lens_name}"]
    Image.fromarray(colour).save(PIC / f"{name}.jpg", quality=92)
    # a checking copy: each of the spot's things outlined in yellow
    from scipy import ndimage
    check = colour.copy()
    for s in highlight:
        m = ids == s
        if m.any():
            edge = m & ~ndimage.binary_erosion(m, iterations=1)
            check[ndimage.binary_dilation(edge)] = (255, 230, 0)
    Image.fromarray(check).save(PIC / "checks" / f"{name}_outlined.jpg", quality=85)
    return colour, ids, shot[f"depth_{lens_name}"], took


def describe(home, ids, colour, oids):
    n = ids.size
    light = colour.astype(float) @ np.array([0.299, 0.587, 0.114]) / 255
    vals, counts = np.unique(ids, return_counts=True)
    share = dict(zip(vals.tolist(), counts.tolist()))
    by_sid = {f["sid"]: oid for oid, f in home.facts.items()}
    things = []
    for oid in oids:
        r = home.records[oid]
        sid = home.facts.get(oid, {}).get("sid")
        px = share.get(sid, 0) if sid else 0
        things.append({"object": oid, "type": r["type"], "relation": r["relation"],
                       "hidden_in_snapshot": r["hidden_in_snapshot"], "placed": bool(r.get("placed")),
                       "model": (r.get("model") or {}).get("source"), "pixels": int(px),
                       "share_of_picture": round(px / n, 5)})
    others = sorted([(by_sid[s], c) for s, c in share.items() if s in by_sid and by_sid[s] not in oids],
                    key=lambda t: -t[1])
    people = {who: int(share.get(scene.FIRST_PERSON + k, 0)) for k, who in enumerate(sorted(home.figures))}
    return {"spot_things": things,
            "spot_things_seen_20px": sum(1 for t in things if t["pixels"] >= 20),
            "other_snapshot_things_in_picture": [{"object": o, "pixels": int(c)} for o, c in others[:15]],
            "people_pixels": people,
            "mean_brightness_0_255": round(float(light.mean() * 255), 1)}


def main():
    idle = int(subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                              capture_output=True, text=True).stdout.strip().splitlines()[0])
    watch = GpuWatch()
    watch.start()
    t0 = time.time()
    home = scene.Home(extra_cameras=cameras())
    home.place_everything()
    people = home.add_people()
    load_s = time.time() - t0
    (PIC / "checks").mkdir(exist_ok=True)
    views = []
    render_times = []
    for place, short in zip(VIEWS, SHORT):
        oids = spot_things(home, place)
        furn = home.furniture_of(place)
        fids = home.ids_of(furn) if furn is not None else set()
        for lens_name, lens in LENSES.items():
            best, tried, target = choose_stand(home, place, oids, lens_name, fids)
            score, eye, look, yaw, pitch, d = best
            name = f"{short}_{lens_name}_{lens['height']:.2f}m"
            colour, ids, depth, took = picture(home, lens_name, eye, look, name,
                                                [home.facts[o]["sid"] for o in oids if o in home.facts])
            render_times.append(took)
            info = describe(home, ids, colour, oids)
            views.append({"picture": f"pictures/{name}.jpg", "spot": place, "camera": lens_name,
                          "eye_xyz_m": [round(float(v), 3) for v in eye],
                          "looks_at_xyz_m": [round(float(v), 3) for v in look],
                          "yaw_deg_about_y_from_plus_z": round(yaw, 1), "pitch_deg": round(pitch, 1),
                          "hfov_deg": lens["hfov"], "resolution": [W, H],
                          "metres_from_middle_of_things": round(float(d), 2),
                          "stands_tried": tried, "score": round(score, 2), **info})
            print(name, "seen", info["spot_things_seen_20px"], "of", len(oids), "score", round(score, 2), "d", round(d, 2))
    # the open drawer: kitchen drawer cabinet, bottom drawer (7 things)
    drawer = "kitchen_kitchen_drawer_cabinet_bottom_drawer_of_the_kitchen_drawer_cabinet"
    oids = spot_things(home, drawer)
    extra = []
    opened = home.open_part(drawer, 1.0)
    stands = {ln: choose_stand(home, drawer, oids, ln, set(), nearest=1.0)[0] for ln in LENSES}
    home.open_part(drawer, 0.0)
    for state in ("shut", "open"):
        if state == "open":
            opened = home.open_part(drawer, 1.0)
        for lens_name in ("high", "low"):
            lens = LENSES[lens_name]
            score, eye, look, yaw, pitch, d = stands[lens_name]
            name = f"drawer_{state}_{lens_name}_{lens['height']:.2f}m"
            colour, ids, depth, took = picture(home, lens_name, eye, look, name,
                                                [home.facts[o]["sid"] for o in oids if o in home.facts])
            info = describe(home, ids, colour, oids)
            extra.append({"picture": f"pictures/{name}.jpg", "spot": drawer, "camera": lens_name, "drawer": state,
                          "opened": opened if state == "open" else None,
                          "eye_xyz_m": [round(float(v), 3) for v in eye],
                          "looks_at_xyz_m": [round(float(v), 3) for v in look], "pitch_deg": round(pitch, 1),
                          "hfov_deg": lens["hfov"], "resolution": [W, H], **info})
            print(name, "seen", info["spot_things_seen_20px"], "of", len(oids))
    home.open_part(drawer, 0.0)
    # residents
    for who, fig in home.figures.items():
        lo, hi = common.box_of(fig)
        target = (lo + hi) / 2
        sid = scene.FIRST_PERSON + sorted(home.figures).index(who)
        best = None
        for d in np.arange(1.2, 3.6, 0.2):
            for b in np.arange(0, 2 * math.pi, math.pi / 12):
                x, z = target[0] + d * math.sin(b), target[2] + d * math.cos(b)
                if not walkable(home, x, z):
                    continue
                eye = np.array([x, 1.0, z])
                look, yaw, pitch = aim(eye, target, LENSES["high"])
                common.look_from(home.sim, eye, look)
                ids = home.shoot("small_high")["small_high"]
                s = min(float((ids == sid).mean()), 0.12)
                if best is None or s > best[0]:
                    best = (s, eye, look, yaw, pitch, d)
        s, eye, look, yaw, pitch, d = best
        name = f"resident_{who}_high_1.00m"
        colour, ids, depth, took = picture(home, "high", eye, look, name, [sid])
        extra.append({"picture": f"pictures/{name}.jpg", "resident": who, "camera": "high",
                      "eye_xyz_m": [round(float(v), 3) for v in eye], "looks_at_xyz_m": [round(float(v), 3) for v in look],
                      "pitch_deg": round(pitch, 1), "hfov_deg": 75.0, "resolution": [W, H],
                      "person_share_of_picture": round(float((ids == sid).mean()), 4), **people[who]})
        print(name, round(float((ids == sid).mean()), 3))
    # speed: the same picture 30 times, colour only and colour+ids+depth
    common.look_from(home.sim, np.array(views[2]["eye_xyz_m"]), np.array(views[2]["looks_at_xyz_m"]))
    t1 = time.time()
    for _ in range(30):
        home.shoot("colour_high")
    colour_only = (time.time() - t1) / 30
    t1 = time.time()
    for _ in range(30):
        home.shoot("colour_high", "ids_high", "depth_high")
    all_three = (time.time() - t1) / 30
    watch.stop = True
    speed = {"load_scene_and_place_everything_s": round(load_s, 1), **home.timings,
             "colour_picture_640x480_s": round(colour_only, 4),
             "colour_ids_depth_640x480_s": round(all_three, 4),
             "gpu_memory_mib_whole_card_before": idle, "gpu_memory_mib_whole_card_peak": watch.peak,
             "gpu_memory_mib_rise": watch.peak - idle, "gpu_memory_mib_this_process_peak": watch.own,
             "note": "includes 9 sensors on the agent; only the ones named are drawn per call"}
    out = {"snapshot": str(common.SNAPSHOT), "scene": common.SCENE,
           "coordinates": "habitat world: y up, metres; yaw measured about +y from +z toward +x",
           "views": views, "extra": extra, "people": people, "speed": speed}
    (common.OUT / "views.json").write_text(json.dumps(out, indent=1, default=str))
    json.dump({"records": home.records, "people": people, "timings": home.timings,
               "grids": {p: {"area_m2": round(g.valid.sum() * scene.CELL ** 2, 3),
                             "snapshot_area": home.snap["places"][p]["geometry"]["area"]} for p, g in home.grids.items()}},
              open(common.OUT / "checks/placement.json", "w"), indent=1, default=str)
    print(json.dumps(speed))


if __name__ == "__main__":
    main()
