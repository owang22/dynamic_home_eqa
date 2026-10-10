"""Step 6: the whole snapshot on the HSSD home, then the physics tests the owner asked for.

1. Every snapshot object with a BEHAVIOR model is put at its snapshot spot by computed pose: the spot's
   centre and height come from the snapshot; objects of one spot are laid out in rows inside a square of the
   spot's area (clipped to the furniture's box). Things on / in / next to / under another object are put
   relative to it. Every deviation from the snapshot is recorded with its reason (`changes`).
2. Overlap test: gravity off for the small objects, 10 steps (1/3 s). Anything that moves more than 5 mm or
   turns more than 3 degrees was pushed out of something it was placed inside of; what it touches is recorded.
3. Settle test: back to the placed poses, gravity on, 60 steps = 2.0 s simulated. Moves over 2 cm or tilts over
   10 degrees are counted and named.
4. Where each object ended up: matched to the snapshot spot it now rests on (basin, cooktop, seat, bed, floor ...).
5. Pictures (1.0 m camera) of the busiest spots before and after settling.

CLOTH=1 loads BEHAVIOR's cloth categories as cloth (needs GPU dynamics) and only does PLACES (comma list).
"""
import collections
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from og_common import OUT, PIC, choose_view, dump, gpu_mem_mib, make_env, render, save_png  # noqa: E402
from omnigibson.macros import gm  # noqa: E402

CLOTH = os.environ.get("CLOTH") == "1"
if CLOTH:
    gm.USE_GPU_DYNAMICS = True
gm.ENABLE_TRANSITION_RULES = False

import numpy as np  # noqa: E402
import torch as th  # noqa: E402
from scipy.spatial.transform import Rotation  # noqa: E402

import omnigibson as og  # noqa: E402
from omnigibson import object_states as S  # noqa: E402
from omnigibson.objects.dataset_object import DatasetObject  # noqa: E402
from omnigibson.objects.light_object import LightObject  # noqa: E402
from omnigibson.utils.constants import PrimType  # noqa: E402
from t05_hssd_home import ASSETS, C, HSSD, JOBS, SCN, SNAP, TYPEMAP, to_isaac  # noqa: E402

TAG = os.environ.get("TAG", "cloth" if CLOTH else "rigid")
PLACES = [p for p in os.environ.get("PLACES", "").split(",") if p]
PICS = ["kitchen_kitchen_cabinet_by_the_range_countertop_by_the_range",
        "kitchen_kitchen_sink_cabinet_countertop_beside_the_kitchen_sink",
        "kitchen_kitchen_sink_cabinet_kitchen_sink_basin", "kitchen_range_left_cooktop",
        "bathroom_2_bathroom_vanity_by_the_bathtub_vanity_top", "bathroom_2_floor", "laundryroom_floor",
        "entryway_floor", "office_office_desk_desk_top", "kitchen_barstool_by_the_island_seat_of_the_barstool_by_the_island"]
CLOSED_REF = {"backpack", "tote bag", "first-aid kit", "jeans", "toiletry bag", "pencil case", "wallet", "knife roll",
              "garment bag", "delicates bag", "sewing kit", "laundry basket_closed"}
random.seed(11)
MIRRORED = set()  # HSSD instances with a negative scale (mirrored); imported unmirrored, so misplaced


def is_cloth_category(cat):
    from omnigibson.utils.bddl_utils import get_knowledge_base
    try:
        return "cloth" in get_knowledge_base().get_category(cat).synset.abilities
    except Exception:
        return False


def kind_of_spot(pid):
    p = SNAP["places"][pid]
    n = p["name"].lower()
    if p["furniture"] == "floor":
        return "floor"
    for k, words in [("basin", ["basin"]), ("cooktop", ["cooktop", "grill"]), ("seat", ["seat"]),
                     ("bed", ["mattress"]), ("tub", ["bathtub"]), ("drum", ["drum"])]:
        if any(w in n for w in words):
            return k
    return "closed space" if p["kind"] == "closed" else ("open space" if p["kind"] == "open" else "flat surface")


def build_home():
    jobs = {j["template"]: j for j in json.load(open(JOBS)) if j["status"] in ("ok", "exists")}
    inst = json.load(open(f"{HSSD}/scenes-articulated/{SCN}.scene_instance.json"))
    env, load_s = make_env({"type": "Scene", "use_floor_plane": True, "floor_plane_visible": False, "use_skybox": False})
    scene = env.scene
    og.sim.stop()
    stage = DatasetObject(name="hssd_stage", category="hssd_stage", model="qstage", dataset_name="hssd-assets",
                          fixed_base=True, visual_only=True)
    scene.add_object(stage)
    furn = {}
    for lst, art in (("object_instances", False), ("articulated_object_instances", True)):
        for i, o in enumerate(inst[lst]):
            j = jobs.get(o["template_name"])
            if j is None:
                continue
            sc = o.get("non_uniform_scale") or o.get("uniform_scale") or 1.0
            sc = np.abs(C @ np.abs(np.broadcast_to(np.asarray(sc, float), 3)))
            ds = os.environ.get("HSSD_STATIC_DATASET", "hssd-assets") if not art else "hssd-assets"
            obj = DatasetObject(name=f"hssd_{'a' if art else 's'}{i}", category=j["category"], model=j["model"],
                                dataset_name=ds, fixed_base=True, scale=th.tensor(sc, dtype=th.float32))
            if any(x < 0 for x in (o.get("non_uniform_scale") or [1, 1, 1])):
                MIRRORED.add((lst, i))
            try:
                scene.add_object(obj)
            except Exception:
                try:
                    scene.remove_object(obj)
                except Exception:
                    pass
                continue
            p, q = to_isaac(o["translation"], o.get("rotation", [1, 0, 0, 0]), art)
            obj.set_position_orientation(position=th.tensor(p, dtype=th.float32), orientation=th.tensor(q, dtype=th.float32))
            furn[(lst, i)] = obj
    scene.add_object(LightObject(name="dome", light_type="Dome", intensity=300.0))
    rooms = {}
    for p in SNAP["places"].values():
        if p["furniture"] == "floor":
            rooms[p["room"]] = C @ np.asarray(p["geometry"]["center"], float)
    for r, c in rooms.items():
        lt = LightObject(name=f"light_{r}", light_type="Sphere", radius=0.15, intensity=20000.0)
        scene.add_object(lt)
        lt.set_position_orientation(position=th.tensor([c[0], c[1], 2.4], dtype=th.float32))
    return env, scene, furn, rooms, load_s


def box(o):
    lo, hi = [x.cpu().numpy() for x in o.aabb]
    return lo, hi


def put(o, bottom_centre):
    """Move o so its box's bottom centre is at bottom_centre (upright, as modelled)."""
    lo, hi = box(o)
    pos, _ = o.get_position_orientation()
    off = pos.cpu().numpy() - np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    o.set_position_orientation(position=th.tensor(np.asarray(bottom_centre) + off, dtype=th.float32),
                               orientation=th.tensor([0, 0, 0, 1.0]))


def main():
    t0 = time.time()
    env, scene, furn, rooms, load_s = build_home()
    objs = SNAP["objects"]
    keys = sorted(k for k in objs if not PLACES or objs[k]["place"] in PLACES)
    changes, made, cloth = [], {}, []
    per_cat = collections.defaultdict(list)
    for k in keys:
        o = objs[k]
        cat = TYPEMAP[o["type"]][0]
        if o["relation"] in ("worn_by", "in_pocket_of"):
            changes.append(dict(obj=k, snapshot=f"{o['relation']} {o['reference']}", done="left out",
                                reason="no residents in the scene"))
            continue
        if not cat:
            changes.append(dict(obj=k, snapshot=f"{o['relation']} {o['reference']}", done="left out",
                                reason=f"no BEHAVIOR model for '{o['type']}'"))
            continue
        if TYPEMAP[o["type"]][1] == "near":
            changes.append(dict(obj=k, snapshot=o["type"], done=f"stand-in model {cat}", reason=TYPEMAP[o["type"]][2]))
        models = sorted(os.listdir(os.path.join(ASSETS, cat)))
        m = models[len(per_cat[cat]) % len(models)] if per_cat[cat] else random.choice(models)
        if per_cat[cat]:
            i0 = models.index(per_cat[cat][0])
            m = models[(i0 + len(per_cat[cat])) % len(models)]
        per_cat[cat].append(m)
        pt = PrimType.CLOTH if (CLOTH and is_cloth_category(cat)) else PrimType.RIGID
        if pt == PrimType.CLOTH:
            cloth.append(k)
        made[k] = DatasetObject(name=k, category=cat, model=m, prim_type=pt)
    og.sim.stop()
    cloth_failed = []
    for i, (k, o) in enumerate(list(made.items())):
        try:
            scene.add_object(o)
        except Exception as e:  # some BEHAVIOR cloth models have no cloth mesh; load those rigid
            cloth_failed.append((k, repr(e)[:120]))
            try:
                scene.remove_object(o)
            except Exception:
                pass
            o = DatasetObject(name=k + "_r", category=o.category, model=o.model)
            scene.add_object(o)
            made[k] = o
            if k in cloth:
                cloth.remove(k)
        o.set_position_orientation(position=th.tensor([80.0 + 1.5 * (i % 15), 80.0 + 1.5 * (i // 15), 0.5]))
    n_locked = 0
    if os.environ.get("LOCK", "1") == "1":  # HSSD doors and drawers are free joints; under load they slid open
        with og.sim.editing_usd():
            for (lst, _), fo in furn.items():
                if lst != "articulated_object_instances":
                    continue
                import omnigibson.lazy as lazy
                for jprim in lazy.pxr.Usd.PrimRange(fo.prim):
                    if jprim.GetTypeName() not in ("PhysicsRevoluteJoint", "PhysicsPrismaticJoint"):
                        continue
                    lo_a, hi_a = jprim.GetAttribute("physics:lowerLimit"), jprim.GetAttribute("physics:upperLimit")
                    if lo_a and hi_a and lo_a.IsValid() and hi_a.IsValid():
                        v = lo_a.Get()
                        if v is not None:
                            hi_a.Set(float(v) + 1e-3)
                            n_locked += 1
    og.sim.play()
    og.sim.step()
    n_limit = n_locked
    if os.environ.get("LOCK", "1") == "1":  # shut doors/drawers and stop them moving (max joint speed ~0, high friction)
        for (lst, _), fo in furn.items():
            if lst != "articulated_object_instances" or not fo.joints:
                continue
            for jn, jp in fo.joints.items():
                try:
                    jp.set_pos(0.0)
                    jp.max_velocity = 1e-4
                    jp.friction = 1e3
                    n_locked += 1
                except Exception as e:
                    print("LOCK FAIL", fo.name, jn, repr(e)[:80], flush=True)
        og.sim.step()
    print("LOCKED", n_locked, "joints (", n_limit, "by USD limits)", flush=True)
    build_s = time.time() - t0
    print("BUILT", len(furn), "furniture", len(made), "objects", len(cloth), "cloth", round(build_s, 1), flush=True)

    # ---------- layout by computed pose ----------
    placed_at = {}  # obj -> intended spot
    by_place = collections.defaultdict(list)
    for k in made:
        if objs[k]["reference_kind"] == "place":
            by_place[objs[k]["reference"]].append(k)
    from omnigibson.utils.sampling_utils import raytest_batch
    GRID = 0.03
    layout_notes = {}
    for pid, ks in by_place.items():
        g = SNAP["places"][pid]["geometry"]
        c = C @ np.asarray(g["center"], float)
        h = float(g.get("height", 0.0))
        side = math.sqrt(max(0.02, float(g.get("area", 0.3))))
        sup = furn.get((g.get("instance_list"), g.get("instance_index"))) if g.get("instance_list") else None
        half = side * (0.45 if sup is None else 0.75)
        x0, x1, y0, y1 = c[0] - half, c[0] + half, c[1] - half, c[1] + half
        if sup is not None:
            lo, hi = box(sup)
            x0, x1, y0, y1 = max(x0, lo[0]), min(x1, hi[0]), max(y0, lo[1]), min(y1, hi[1])
        xs, ys = np.arange(x0, x1 + 1e-6, GRID), np.arange(y0, y1 + 1e-6, GRID)
        starts = [[x, y, h + 0.06] for x in xs for y in ys]
        ends = [[x, y, h - 0.06] for x in xs for y in ys]
        valid = {}
        if starts:
            res = raytest_batch(starts, ends)
            for (sx, sy, _), r in zip(starts, res):
                if not r["hit"] or abs(float(r["position"][2]) - h) > 0.03 or float(r["normal"][2]) < 0.8:
                    continue
                if sup is not None and not str(r["rigidBody"]).startswith(sup.prim_path):
                    continue
                valid[(int(round((sx - x0) / GRID)), int(round((sy - y0) / GRID)))] = float(r["position"][2])
        cells = sorted(valid, key=lambda ij: math.hypot(x0 + ij[0] * GRID - c[0], y0 + ij[1] * GRID - c[1]))
        ks = sorted(ks, key=lambda k: -float(np.prod((box(made[k])[1] - box(made[k])[0])[:2])))
        rects, n_fit, n_nofit = [], 0, 0
        for k in ks:
            lo, hi = box(made[k])
            w, d = hi[0] - lo[0], hi[1] - lo[1]
            spot_ok = None
            for (i, j) in cells:
                x, y = x0 + i * GRID, y0 + j * GRID
                r = (x - w / 2 - 0.01, x + w / 2 + 0.01, y - d / 2 - 0.01, y + d / 2 + 0.01)
                if any(not (r[1] <= q[0] or q[1] <= r[0] or r[3] <= q[2] or q[3] <= r[2]) for q in rects):
                    continue
                # most of the footprint must stand on the surface (corners pulled in by a quarter)
                cs = [(x + sx * w / 4, y + sy * d / 4) for sx in (-1, 1) for sy in (-1, 1)]
                if all((int(round((cx - x0) / GRID)), int(round((cy - y0) / GRID))) in valid for cx, cy in cs):
                    zs = [valid[(int(round((cx - x0) / GRID)), int(round((cy - y0) / GRID)))] for cx, cy in cs]
                    spot_ok = (x, y, max(zs + [valid[(i, j)]]), r)
                    break
            if spot_ok is None:
                n_nofit += 1
                # fall back: nearest free cell, ignoring overlap; recorded
                if cells:
                    i, j = cells[min(len(cells) - 1, n_nofit * 3)]
                    spot_ok = (x0 + i * GRID, y0 + j * GRID, valid[(i, j)], None)
                else:
                    spot_ok = (c[0], c[1], h, None)
                changes.append(dict(obj=k, snapshot=f"on {pid}", done="placed where it overlaps or overhangs",
                                    reason="no free place on the surface under the spot that fits its footprint"
                                    if cells else "ray test found no surface at the spot's height (furniture missing or shaped differently)"))
            else:
                n_fit += 1
                rects.append(spot_ok[3])
            put(made[k], [spot_ok[0], spot_ok[1], spot_ok[2] + 0.002])
            placed_at[k] = pid
        layout_notes[pid] = dict(surface_cells=len(valid), objects=len(ks), fitted=n_fit, not_fitted=n_nofit)
    # relative to other objects, in an order where the reference is already placed
    rel_keys = [k for k in made if objs[k]["reference_kind"] == "object"]
    hidden_kept_out = []
    for _ in range(4):
        for k in list(rel_keys):
            o = objs[k]
            ref = o["reference"]
            if ref not in placed_at and ref in made:
                continue
            rel_keys.remove(k)
            if ref not in made:
                changes.append(dict(obj=k, snapshot=f"{o['relation']} {ref}", done="left out",
                                    reason="its reference has no model"))
                made[k].visible = False
                continue
            rtype = objs[ref]["type"]
            rlo, rhi = box(made[ref])
            lo, hi = box(made[k])
            rc = (rlo + rhi) / 2
            n_same = sum(1 for kk in placed_at if objs[kk]["reference"] == ref and objs[kk]["relation"] == o["relation"])
            if o["relation"] == "inside" and (rtype in CLOSED_REF or objs[ref].get("holds") == "closed"):
                made[k].visible = False
                hidden_kept_out.append(k)
                changes.append(dict(obj=k, snapshot=f"inside {ref} ({rtype})", done="kept out of sight, not simulated",
                                    reason="BEHAVIOR's bag and kit models are solid shells; nothing fits inside"))
                continue
            if o["relation"] == "inside":  # an open container: a bowl, tray or basket
                put(made[k], [rc[0], rc[1], rlo[2] + 0.01 + 0.05 * n_same])
            elif o["relation"] == "on_top":
                dx = (n_same % 2 - 0.5) * 0.4 * (rhi[0] - rlo[0]) if n_same else 0.0
                dy = (n_same // 2 - 0.5) * 0.4 * (rhi[1] - rlo[1]) if n_same else 0.0
                put(made[k], [rc[0] + dx, rc[1] + dy, rhi[2] + 0.002])
            elif o["relation"] == "under":
                # coaster under a mug: coaster where the mug is, mug lifted onto it
                put(made[k], [rc[0], rc[1], rlo[2]])
                put(made[ref], [rc[0], rc[1], rlo[2] + (hi[2] - lo[2]) + 0.002])
            else:  # next_to: beside it, same height
                put(made[k], [rhi[0] + (hi[0] - lo[0]) / 2 + 0.02 + 0.1 * n_same, rc[1], rlo[2]])
            placed_at[k] = placed_at.get(ref)
    # park hidden ones far away so they take no part
    for i, k in enumerate(hidden_kept_out):
        made[k].set_position_orientation(position=th.tensor([200.0 + 2 * i, 200.0, 0.5]))
    sim_keys = [k for k in placed_at if k not in hidden_kept_out]
    og.sim.render()

    def poses():
        return {k: (made[k].get_position_orientation()[0].cpu().numpy().copy(),
                    made[k].get_position_orientation()[1].cpu().numpy().copy()) for k in sim_keys}

    def moved(a, b):
        d = float(np.linalg.norm(b[0] - a[0]))
        ra, rb = Rotation.from_quat(a[1]), Rotation.from_quat(b[1])
        up_a, up_b = ra.apply([0, 0, 1]), rb.apply([0, 0, 1])
        tilt = math.degrees(math.acos(max(-1, min(1, float(np.dot(up_a, up_b))))))
        return d, tilt

    cam_pose = {}

    def shots(tag):
        cam = list(env.external_sensors[0].values())[1]
        for pid in PICS:
            if PLACES and pid not in PLACES:
                continue
            if pid in cam_pose:
                e, q = cam_pose[pid]
                cam.set_position_orientation(position=th.tensor(e, dtype=th.float32),
                                             orientation=th.tensor(q, dtype=th.float32), frame="scene")
                rgb, *_ = render(cam, n=8)
                save_png(rgb, f"{PIC}/settle_{TAG}/{pid[:60]}_{tag}.png")
                continue
            ks = [k for k in sim_keys if placed_at.get(k) == pid]
            g = SNAP["places"][pid]["geometry"]
            c = C @ np.asarray(g["center"], float)
            boxes = [box(f) for f in furn.values()]
            rc = rooms.get(SNAP["places"][pid]["room"], c)
            best = choose_view(cam, "raised_1.0m", c, max(0.8, math.sqrt(float(g.get("area", 0.5)))) + 0.3,
                               [made[k] for k in ks], lambda e: not any(np.all(e > lo - 0.1) and np.all(e < hi + 0.1)
                                                                      for lo, hi in boxes),
                               yaw_first=math.atan2(rc[1] - c[1], rc[0] - c[0]))
            if best is None:
                continue
            cam_pose[pid] = (best["eye"], best["q"])
            rgb, *_ = render(cam, n=8)
            save_png(rgb, f"{PIC}/settle_{TAG}/{pid[:60]}_{tag}.png")

    shots("placed")
    p0 = poses()
    box0 = {k: box(made[k]) for k in sim_keys}
    fbox = {f.name: box(f) for f in furn.values()}

    def box_partners(k):
        lo, hi = box0[k]
        out = []
        for name, (l2, h2) in list(fbox.items()) + [(kk, box0[kk]) for kk in sim_keys if kk != k]:
            pen = np.minimum(hi, h2) - np.maximum(lo, l2)
            if np.all(pen > 0.01):
                out.append(name)
        return out
    # ---------- overlap test: gravity off ----------
    for k in sim_keys:
        try:
            made[k].disable_gravity()
        except Exception:
            pass
    for _ in range(10):
        og.sim.step()
    p1 = poses()
    overlap = []
    near_names = list(furn.values()) + [made[k] for k in sim_keys]
    for k in sim_keys:
        d, tilt = moved(p0[k], p1[k])
        if d > 0.005 or tilt > 3:
            overlap.append(dict(obj=k, spot=placed_at[k], pushed_m=round(d, 3), turned_deg=round(tilt, 1),
                                boxes_overlapping_at_placement=box_partners(k)))
    print("OVERLAP", len(overlap), "of", len(sim_keys), flush=True)
    # ---------- settle test: back to placed poses, gravity on, 2 s ----------
    for k in sim_keys:
        made[k].set_position_orientation(position=th.tensor(p0[k][0]), orientation=th.tensor(p0[k][1]))
        try:
            made[k].keep_still()
        except Exception:
            pass
        for link in made[k].links.values():
            try:
                link.enable_gravity()
            except Exception:
                pass
    dt = og.sim.get_sim_step_dt()
    n_steps = int(round(2.0 / dt))
    for _ in range(n_steps):
        og.sim.step()
    p2 = poses()
    settle = []
    for k in sim_keys:
        d, tilt = moved(p0[k], p2[k])
        settle.append(dict(obj=k, type=objs[k]["type"], spot=placed_at[k], moved_m=round(d, 3), tilt_deg=round(tilt, 1),
                           dz_m=round(float(p2[k][0][2] - p0[k][0][2]), 3), cloth=k in cloth))
    big = [s for s in settle if s["moved_m"] > 0.02 or s["tilt_deg"] > 10]
    print("SETTLE", n_steps, "steps of", round(dt, 4), "s;", len(big), "of", len(settle), "moved >2 cm or tilted >10 deg", flush=True)
    # ---------- where did things end up ----------
    spots = []
    for pid, p in SNAP["places"].items():
        g = p["geometry"]
        f = furn.get((g.get("instance_list"), g.get("instance_index"))) if g.get("instance_list") else None
        spots.append((pid, C @ np.asarray(g["center"], float), float(g.get("height", 0)), f, math.sqrt(max(0.02, g.get("area", 0.3)))))
    ended = []
    for k in sim_keys:
        lo, hi = box(made[k])
        cx, cy, bz = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]
        best, bd = None, 1e9
        for pid, c, h, f, side in spots:
            if abs(bz - h) > 0.06:
                continue
            if f is not None:
                flo, fhi = box(f)
                if not (flo[0] - 0.02 <= cx <= fhi[0] + 0.02 and flo[1] - 0.02 <= cy <= fhi[1] + 0.02):
                    continue
            dd = math.hypot(cx - c[0], cy - c[1])
            if f is None and dd > 3.0:
                continue
            if dd < bd:
                best, bd = pid, dd
        intended = placed_at[k]
        if best is None:
            best = "floor (no spot)" if bz < 0.06 else "no surface found (between things or resting on another object)"
        same_furn = best == intended or (best in SNAP["places"] and SNAP["places"][best]["furniture"] == SNAP["places"][intended]["furniture"]
                                         and SNAP["places"][best]["room"] == SNAP["places"][intended]["room"])
        ended.append(dict(obj=k, intended=intended, intended_kind=kind_of_spot(intended), ended=best,
                          ended_kind=kind_of_spot(best) if best in SNAP["places"] else best.split(" (")[0],
                          on_reference_object=objs[k]["reference_kind"] == "object", same_spot=best == intended,
                          same_furniture=same_furn, bottom_z=round(float(bz), 3)))
    shots("settled")
    snap_kinds = collections.Counter(kind_of_spot(objs[k]["place"]) for k in objs if objs[k]["relation"] not in ("worn_by", "in_pocket_of"))
    mirrored_spots = [pid for pid, p in SNAP["places"].items() if p["geometry"].get("instance_list")
                      and (p["geometry"]["instance_list"], p["geometry"]["instance_index"]) in MIRRORED]
    dump(dict(tag=TAG, cloth_failed=cloth_failed if CLOTH else [], mirrored_spots=mirrored_spots, layout=layout_notes, joints_locked=n_locked,
              static_dataset=os.environ.get("HSSD_STATIC_DATASET", "hssd-assets"), cloth_objects=cloth, load_seconds=load_s, build_seconds=build_s, sim_step_dt=dt, settle_steps=n_steps,
              gpu_mib=gpu_mem_mib(), n_simulated=len(sim_keys), snapshot_spot_kinds=snap_kinds,
              changes=changes, overlap=overlap, settle=settle, settle_big=big, ended=ended),
         f"{OUT}/settle_{TAG}.json")
    print("DONE", flush=True)
    og.shutdown()


if __name__ == "__main__":
    main()
