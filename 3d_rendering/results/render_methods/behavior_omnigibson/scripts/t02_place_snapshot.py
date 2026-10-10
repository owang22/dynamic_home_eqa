"""Step 2: put household A's day-7 18:00 snapshot into BEHAVIOR's house_single_floor.

Every snapshot place is mapped to a piece of furniture of the same kind in the matching room
(FURN below); furniture the house lacks is added from the BEHAVIOR library and set on the room's
floor with OmniGibson's own OnTop sampler (ADD below). Every snapshot object whose type has a
BEHAVIOR category (mapping/type_to_category.json) is added and placed with OmniGibson's samplers:
OnTop, Inside, Under; NextTo has no sampler in OmniGibson, so it is placed by hand next to its
reference on the same surface and then checked with OmniGibson's NextTo test.

After placing, physics runs for a while and every relation is checked again. The whole scene is
saved to placed_scene.json so the renders can reload it without sampling again.
"""
import collections
import json
import os
import random
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from og_common import OUT, dump, gpu_mem_mib  # noqa: E402

import torch as th  # noqa: E402

import omnigibson as og  # noqa: E402
from omnigibson import object_states as S  # noqa: E402
from omnigibson.macros import gm  # noqa: E402
from omnigibson.objects.dataset_object import DatasetObject  # noqa: E402
from omnigibson.utils import object_state_utils as osu  # noqa: E402

# Fewer retries per sampling call (defaults 10 x 10); each retry reloads the whole scene state.
osu.m.DEFAULT_HIGH_LEVEL_SAMPLING_ATTEMPTS = int(os.environ.get("HL_ATTEMPTS", "3"))
osu.m.DEFAULT_LOW_LEVEL_SAMPLING_ATTEMPTS = int(os.environ.get("LL_ATTEMPTS", "4"))

SNAP = "/home/oliver/robot/dynamic_home_eqa/3d_rendering/results/lived_home/hssd_a/day_07/positions_1800.json"
TYPEMAP = json.load(open(f"{OUT}/mapping/type_to_category.json"))
ASSETS = "/mnt/nvme/oliver/robot/render_methods/behavior/BEHAVIOR-1K/datasets/behavior-1k-assets/objects"
SCENE = "house_single_floor"
random.seed(7)

ROOM = {"kitchen": "kitchen_0", "dining_room": "dining_room_0", "living_room": "living_room_0",
        "tv_room": "living_room_1", "bedroom_1": "bedroom_0", "bedroom_2": "childs_room_1",
        "office": "childs_room_0", "bathroom_1": "bathroom_1", "toilet": "bathroom_1",
        "bathroom_2": "bathroom_0", "laundryroom": "utility_room_0", "closet": "closet_0",
        "hallway_1": "corridor_0", "hallway_2": "corridor_0", "entryway": "entryway_0"}

# Extra furniture of the same kind, added because the BEHAVIOR house has none in that room.
ADD = {
    "add_dining_sideboard": ("bottom_cabinet", "dining_room_0"),
    "add_dining_coffee_table": ("coffee_table", "dining_room_0"),
    "add_bedroom_dresser": ("bottom_cabinet", "bedroom_0"),
    "add_bedroom_armchair": ("armchair", "bedroom_0"),
    "add_tv_small_table": ("pedestal_table", "living_room_1"),
    "add_bedroom2_coatrack": ("coatrack", "childs_room_1"),
    "add_hall_piano": ("piano", "corridor_0"),
    "add_hall_piano_stool": ("taboret", "corridor_0"),
    "add_hall_side_table": ("pedestal_table", "corridor_0"),
    "add_living_sideboard": ("bottom_cabinet", "living_room_0"),
    "add_living_end_table": ("pedestal_table", "living_room_0"),
}

UPPER = ["top_cabinet_lkxmne_0", "top_cabinet_lkxmne_1", "top_cabinet_lkxmne_2"]
# snapshot "room|furniture" -> {spot kind: BEHAVIOR object}. "under" marks spots that sit under the furniture.
FURN = {
    "kitchen|kitchen cabinet by the range": {"surface": "countertop_kelker_0", "closed": "bottom_cabinet_no_top_gjeoer_0"},
    "kitchen|kitchen cabinet by the upper cabinet": {"surface": "countertop_kelker_0", "closed": "bottom_cabinet_no_top_gjeoer_0"},
    "kitchen|kitchen cabinet by the other upper cabinet": {"surface": "countertop_kelzer_0", "closed": "bottom_cabinet_no_top_rkgjer_0"},
    "kitchen|kitchen cabinet by the sink": {"surface": "countertop_kelzer_0", "closed": "bottom_cabinet_no_top_rkgjer_0"},
    "kitchen|kitchen sink cabinet": {"surface": "countertop_kelzer_0", "closed": "bottom_cabinet_no_top_rkgjer_0", "open": "drop_in_sink_awvzkn_0"},
    "kitchen|kitchen drawer cabinet": {"surface": "countertop_kelker_0", "closed": "bottom_cabinet_no_top_gjeoer_0"},
    "kitchen|kitchen island": {"surface": "bar_udatjt_0"},
    "kitchen|refrigerator": {"closed": "fridge_dszchb_0"},
    "kitchen|range": {"surface": "burner_mjvqii_0", "closed": "oven_ffitak_0"},
    "kitchen|barstool by the island": {"surface": "taboret_ivtoxu_0"},
    "kitchen|barstool by the other island stool": {"surface": "taboret_ivtoxu_1"},
    "kitchen|barstool by the island 2": {"surface": "taboret_ivtoxu_2"},
    "dining_room|dining table": {"surface": "breakfast_table_rhjoby_0"},
    "dining_room|dining room sideboard": {"surface": "add_dining_sideboard", "closed": "add_dining_sideboard"},
    "dining_room|coffee table by the armchairs": {"surface": "add_dining_coffee_table"},
    "bedroom_1|bed in the main bedroom": {"surface": "bed_gxfipj_0", "under": "bed_gxfipj_0"},
    "bedroom_1|dresser by the armchair": {"surface": "add_bedroom_dresser", "closed": "add_bedroom_dresser"},
    "bedroom_1|nightstand by the main bed": {"surface": "nightstand_wbxekb_1"},
    "bedroom_1|nightstand by the main bed 2": {"surface": "nightstand_wbxekb_0"},
    "bedroom_1|armchair by the small table": {"surface": "add_bedroom_armchair"},
    "closet|wardrobe by the ottoman": {"closed": "wardrobe_lrokhl_0"},
    "closet|wardrobe by the other wardrobe": {"closed": "wardrobe_lrokhl_0"},
    "tv_room|coffee table by the sectional": {"surface": "coffee_table_qtwqqb_0"},
    "tv_room|sectional sofa": {"surface": "sofa_bskyog_0"},
    "tv_room|small table by the television": {"surface": "add_tv_small_table"},
    "bedroom_2|bed in the second bedroom": {"surface": "bed_rrcvaq_1"},
    "bedroom_2|chair by the coat rack": {"surface": "eames_chair_hndxiw_0"},
    "bedroom_2|coat rack by the chair": {"surface": "add_bedroom2_coatrack"},
    "bedroom_2|nightstand by the second bedroom bed": {"surface": "nightstand_wbxekb_2", "closed": "nightstand_wbxekb_2"},
    "bathroom_1|low table by the armchair": {"surface": "shelf_fjozhc_0"},
    "bathroom_1|bathroom vanity by the toilet": {"surface": "multi_station_furniture_sink_upwldu_0", "closed": "multi_station_furniture_sink_upwldu_0"},
    "toilet|small bathroom sink": {"surface": "multi_station_furniture_sink_upwldu_0"},
    "toilet|toilet by the small sink": {"surface": "toilet_udiezm_0", "closed": "toilet_udiezm_0"},
    "laundryroom|toilet by the bathroom vanity": {"surface": "countertop_ikwqer_0", "closed": "bottom_cabinet_no_top_gjrero_3", "open": "tabletop_sink_vekaaf_0"},
    "laundryroom|laundry sink cabinet": {"surface": "countertop_ikwqer_0", "closed": "bottom_cabinet_no_top_gjrero_3"},
    "laundryroom|laundry drawer cabinet": {"surface": "countertop_ikwqer_0", "closed": "bottom_cabinet_no_top_gjrero_0"},
    "laundryroom|laundry cabinet by the washing machine": {"surface": "countertop_fjkase_0", "closed": "bottom_cabinet_no_top_gjrero_1"},
    "laundryroom|clothes rail by the laundry cabinets": {"surface": "wardrobe_pyuwgc_0"},
    "laundryroom|washing machine by the other washer": {"closed": "washer_ynwamu_0"},
    "laundryroom|washing machine by the laundry cabinet": {"closed": "clothes_dryer_xsuyua_0"},
    "bathroom_2|bathroom vanity by the bathtub": {"surface": "bottom_cabinet_xqmipa_0", "open": "tabletop_sink_qnequy_0"},
    "bathroom_2|bathtub": {"open": "bathtub_pdcrfs_0"},
    "bathroom_2|toilet by the bathtub": {"surface": "toilet_udiezm_1", "closed": "toilet_udiezm_1"},
    "office|office desk": {"surface": "desk_xhjsub_0", "closed": "desk_xhjsub_0"},
    "office|office chair": {"surface": "swivel_chair_tbzfgf_0"},
    "hallway_2|piano": {"surface": "add_hall_piano", "closed": "add_hall_piano"},
    "hallway_2|piano stool": {"surface": "add_hall_piano_stool"},
    "hallway_2|side table by the sofa chair": {"surface": "add_hall_side_table"},
    "living_room|living room coffee table": {"surface": "coffee_table_rlsebe_0"},
    "living_room|living room sectional": {"surface": "sofa_hiphpn_0"},
    "living_room|living room sideboard": {"surface": "add_living_sideboard", "closed": "add_living_sideboard"},
    "living_room|end table by the accent chairs": {"surface": "add_living_end_table"},
}


def spot_target(snap, place_id, floors):
    """(relation, BEHAVIOR object name, note) for an object placed on/in a snapshot place."""
    p = snap["places"][place_id]
    room, furn, kind = p["room"], p["furniture"], p["kind"]
    if furn == "floor":
        return "on_top", floors[ROOM[room]], "room floor"
    if furn.startswith("upper kitchen cabinet"):
        ups = sorted({q["furniture"] for q in snap["places"].values() if q["furniture"].startswith("upper kitchen cabinet")})
        return "inside", UPPER[ups.index(furn) % 3], "one of 3 upper cabinets for 13"
    m = FURN.get(f"{room}|{furn}")
    if m is None:
        return None, None, "no furniture of this kind mapped"
    if "under" in m and ("bottom shelf" in p["name"] or "middle shelf" in p["name"]) and "bed" in furn:
        return "under", m["under"], "shelf under the bed -> under the bed"
    if kind == "surface":
        if "surface" in m:
            return "on_top", m["surface"], ""
        return None, None, "no surface mapped"
    if kind in ("closed", "open"):
        t = m.get(kind) or m.get("closed") or m.get("open")
        if t:
            return "inside", t, ""
    return None, None, f"no {kind} spot mapped"


def park(i):
    """Waiting spot on the lawn north of the house (a grid, 1.5 m apart). BEHAVIOR's own sampler parks
    objects in mid-air far away; here that made them fall forever and sampling slowed to minutes per object."""
    return th.tensor([-6.0 + 1.5 * (i % 10), 30.0 + 1.5 * (i // 10), 1.0])


def pick_models(cat, n):
    models = sorted(os.listdir(os.path.join(ASSETS, cat)))
    random.shuffle(models)
    return [models[i % len(models)] for i in range(n)]


def main():
    snap = json.load(open(SNAP))
    gm.ENABLE_OBJECT_STATES = True
    # BEHAVIOR's cooking/mixing rules fired during placement (things on a cutting board by the burner) and
    # crashed Isaac Sim while making particles, after 55 minutes of sampling. Off: nothing here should cook.
    gm.ENABLE_TRANSITION_RULES = False
    t0 = time.time()
    env = og.Environment(configs={"scene": {"type": "InteractiveTraversableScene", "scene_model": SCENE}})
    scene = env.scene
    load_s = time.time() - t0
    print("LOADED", round(load_s, 1), flush=True)
    floors = {}
    for o in scene.objects:
        if o.category == "floors" and o.in_rooms:
            floors[o.in_rooms[0]] = o.name

    # ---------- decide what to add ----------
    objs = snap["objects"]
    cats = {k: TYPEMAP[o["type"]][0] for k, o in objs.items()}
    per_cat = collections.Counter(c for c in cats.values() if c)
    model_pool = {c: pick_models(c, n) for c, n in per_cat.items()}
    model_of = {}
    for k in sorted(objs):
        c = cats[k]
        if c:
            model_of[k] = model_pool[c].pop(0)
    add_models = {}
    for name, (cat, room) in ADD.items():
        add_models[name] = pick_models(cat, 1)[0]

    # ---------- add everything far away ----------
    t1 = time.time()
    og.sim.stop()
    new = {}
    i = 0
    for name, (cat, room) in ADD.items():
        o = DatasetObject(name=name, category=cat, model=add_models[name], in_rooms=[room])  # fixed_base=True breaks the sampler (RigidKinematicPrim has no get_linear_velocity)
        scene.add_object(o)
        o.set_position_orientation(position=park(i))
        new[name] = o
        i += 1
    for k in sorted(objs):
        if k not in model_of:
            continue
        o = DatasetObject(name=k, category=cats[k], model=model_of[k])
        scene.add_object(o)
        o.set_position_orientation(position=park(i))
        new[k] = o
        i += 1
    og.sim.play()
    og.sim.step()
    add_s = time.time() - t1
    print("ADDED", len(new), round(add_s, 1), "gpu", gpu_mem_mib(), flush=True)

    def get(name):
        return new.get(name) or scene.object_registry("name", name)

    log = []

    def sample(rel, obj, target):
        st = {"on_top": S.OnTop, "inside": S.Inside, "under": S.Under}[rel]
        return bool(obj.states[st].set_value(target, True))

    # ---------- extra furniture on its room floor ----------
    for name, (cat, room) in ADD.items():
        t = time.time()
        ok = False
        err = ""
        try:
            ok = sample("on_top", new[name], get(floors[room]))
        except Exception as e:
            err = repr(e)
        log.append(dict(obj=name, kind="added furniture", category=cat, model=add_models[name], relation="on_top",
                        target=floors[room], sampled=ok, error=err, seconds=round(time.time() - t, 2)))
        print("FURN", name, ok, err[:120], flush=True)

    # ---------- small objects, references first ----------
    todo = [k for k in objs if objs[k]["relation"] in ("on_top", "inside", "under", "next_to")]
    done = set()
    order = []
    while todo:
        progress = False
        for k in list(todo):
            o = objs[k]
            if o["reference_kind"] != "object" or o["reference"] in done or o["reference"] not in objs:
                order.append(k)
                done.add(k)
                todo.remove(k)
                progress = True
        if not progress:
            order += todo
            break
    opened = set()
    for k in order:
        o = objs[k]
        rec = dict(obj=k, type=o["type"], category=cats[k], model=model_of.get(k), relation=o["relation"],
                   reference=o["reference"], reference_kind=o["reference_kind"], hidden=o["hidden"], place=o["place"])
        t = time.time()
        if k not in new:
            rec.update(sampled=False, why="no BEHAVIOR category for this type")
            log.append(rec)
            continue
        obj = new[k]
        rel = o["relation"]
        try:
            if o["reference_kind"] == "place":
                prel, tname, note = spot_target(snap, o["reference"], floors)
                rec["note"] = note
                if prel is None:
                    rec.update(sampled=False, why=note)
                    log.append(rec)
                    continue
                if rel == "next_to":  # next to a place: put it on that place
                    rec["note"] = "next_to a place: placed on it"
                    rel_used = prel
                else:
                    rel_used = prel
                target = get(tname)
                rec["target"] = tname
                if target is None:
                    rec.update(sampled=False, why=f"target {tname} not in scene")
                    log.append(rec)
                    continue
                rec["relation_used"] = rel_used
                ok = sample(rel_used, obj, target)
                if not ok and rel_used == "inside" and S.Open in target.states:
                    target.states[S.Open].set_value(True, fully=True)
                    opened.add(tname)
                    for _ in range(5):
                        og.sim.step()
                    ok = sample(rel_used, obj, target)
                    rec["opened_to_sample"] = True
                rec["sampled"] = ok
            else:  # reference is another snapshot object
                ref = new.get(o["reference"])
                rec["target"] = o["reference"]
                if ref is None or not any(r["obj"] == o["reference"] and r.get("sampled") for r in log):
                    rec.update(sampled=False, why="reference object not placed")
                    log.append(rec)
                    continue
                if rel in ("on_top", "inside", "under"):
                    rec["relation_used"] = rel
                    if rel == "inside":  # inside a bag, bowl or kit: few tries (a failed Inside costs ~3 min)
                        hl, ll = osu.m.DEFAULT_HIGH_LEVEL_SAMPLING_ATTEMPTS, osu.m.DEFAULT_LOW_LEVEL_SAMPLING_ATTEMPTS
                        osu.m.DEFAULT_HIGH_LEVEL_SAMPLING_ATTEMPTS, osu.m.DEFAULT_LOW_LEVEL_SAMPLING_ATTEMPTS = 1, 3
                        try:
                            ok = sample(rel, obj, ref)
                        finally:
                            osu.m.DEFAULT_HIGH_LEVEL_SAMPLING_ATTEMPTS, osu.m.DEFAULT_LOW_LEVEL_SAMPLING_ATTEMPTS = hl, ll
                    else:
                        ok = sample(rel, obj, ref)
                    if not ok and rel == "inside":
                        # fall back: on top of it (a bowl, a basket or a bag that cannot be sampled into)
                        ok2 = sample("on_top", obj, ref)
                        rec["fallback"] = "on_top" if ok2 else None
                    rec["sampled"] = ok
                else:  # next_to: same surface as the reference, then move beside it
                    ok = place_next_to(obj, ref, log, o["reference"], get, floors, snap)
                    rec["relation_used"] = "next_to (by hand)"
                    rec["sampled"] = ok
        except Exception as e:
            rec.update(sampled=False, error=repr(e), tb=traceback.format_exc()[-600:])
        rec["seconds"] = round(time.time() - t, 2)
        log.append(rec)
        if len(log) % 10 == 0:  # checkpoint: a crash late in the run must not lose the record
            dump(log, f"{OUT}/mapping/placement_log_partial.json")
        print("PLACE", k, rec.get("relation_used"), rec.get("target"), rec.get("sampled"), rec.get("why", ""),
              rec.get("error", "")[:100], rec["seconds"], flush=True)

    # close what was opened, settle, then check every relation again
    for tname in opened:
        get(tname).states[S.Open].set_value(False, fully=True)
    for _ in range(60):
        og.sim.step()
    for rec in log:
        if not rec.get("sampled") or rec.get("kind") == "added furniture":
            continue
        obj = new[rec["obj"]]
        tgt = get(rec["target"]) if rec["reference_kind"] == "place" else new.get(rec["reference"])
        r = rec.get("relation_used", "")
        try:
            if r.startswith("next_to"):
                rec["holds_after_settle"] = bool(obj.states[S.NextTo].get_value(tgt))
            else:
                st = {"on_top": S.OnTop, "inside": S.Inside, "under": S.Under}[r]
                rec["holds_after_settle"] = bool(obj.states[st].get_value(tgt))
        except Exception as e:
            rec["holds_after_settle"] = None
            rec["check_error"] = repr(e)
        rec["final_pos"] = obj.get_position_orientation()[0].tolist()
    dump(log, f"{OUT}/mapping/placement_log.json")
    print("LOGSAVED", flush=True)
    for name in ADD:
        o = new[name]
        print("ADDPOS", name, o.get_position_orientation()[0].tolist(), "openable", S.Open in o.states, flush=True)
    og.sim.save(json_paths=[f"{OUT}/mapping/placed_scene.json"])
    dump(dict(load_seconds=load_s, add_seconds=add_s, place_seconds=round(sum(r.get("seconds", 0) for r in log), 1),
              gpu_mib=gpu_mem_mib(), opened=sorted(opened)), f"{OUT}/mapping/placement_timing.json")
    print("SAVED", flush=True)
    og.shutdown()


def place_next_to(obj, ref, log, ref_key, get, floors, snap):
    """Put obj on the same support as ref, beside it, and check OmniGibson's NextTo."""
    rec = next(r for r in log if r["obj"] == ref_key)
    support = get(rec["target"]) if rec["reference_kind"] == "place" else None
    if support is None:
        return False
    if not obj.states[S.OnTop].set_value(support, True):
        return False
    rlo, rhi = ref.aabb
    olo, ohi = obj.aabb
    slo, shi = support.aabb
    rc, oc = (rlo + rhi) / 2, (olo + ohi) / 2
    pos, ori = obj.get_position_orientation()
    off_obj = pos - oc  # object frame origin relative to its box centre
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
        gap = 0.03
        cx = rc[0] + dx * ((rhi[0] - rlo[0]) / 2 + (ohi[0] - olo[0]) / 2 + gap)
        cy = rc[1] + dy * ((rhi[1] - rlo[1]) / 2 + (ohi[1] - olo[1]) / 2 + gap)
        hx, hy = (ohi[0] - olo[0]) / 2, (ohi[1] - olo[1]) / 2
        if not (slo[0] + hx <= cx <= shi[0] - hx and slo[1] + hy <= cy <= shi[1] - hy) and rec["reference_kind"] == "place" \
                and support.category != "floors":
            continue
        cz = oc[2] + 0.01
        new_pos = th.tensor([cx, cy, cz]) + off_obj
        obj.set_position_orientation(position=new_pos, orientation=ori)
        for _ in range(10):
            og.sim.step()
        if obj.states[S.NextTo].get_value(ref) and obj.states[S.OnTop].get_value(support):
            return True
    return False


if __name__ == "__main__":
    main()
