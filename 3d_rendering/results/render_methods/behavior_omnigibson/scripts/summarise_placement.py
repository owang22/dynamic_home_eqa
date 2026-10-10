"""Count route A placement results per snapshot relation from mapping/placement_log.json."""
import collections
import json
import sys

OUT = "/home/oliver/robot/dynamic_home_eqa/3d_rendering/results/render_methods/behavior_omnigibson"
SNAP = json.load(open("/home/oliver/robot/dynamic_home_eqa/3d_rendering/results/lived_home/hssd_a/day_07/positions_1800.json"))
log = json.load(open(f"{OUT}/mapping/placement_log.json"))
furn = [r for r in log if r.get("kind") == "added furniture"]
objs = {r["obj"]: r for r in log if r.get("kind") != "added furniture"}
print("added furniture:", sum(r["sampled"] for r in furn), "of", len(furn))
rows = collections.OrderedDict()
for rel in ["on_top", "inside", "next_to", "under", "worn_by", "in_pocket_of"]:
    ks = [k for k, o in SNAP["objects"].items() if o["relation"] == rel]
    r = [objs.get(k) for k in ks]
    have_cat = [x for x in r if x and x.get("category")]
    mapped = [x for x in have_cat if x.get("why") not in ("no furniture of this kind mapped", "no surface mapped") and not str(x.get("why", "")).startswith("no ")]
    sampled = [x for x in r if x and x.get("sampled")]
    held = [x for x in sampled if x.get("holds_after_settle")]
    fb = [x for x in r if x and x.get("fallback") == "on_top"]
    rows[rel] = dict(snapshot=len(ks), has_category=len(have_cat), sampled=len(sampled), holds_after_settle=len(held),
                     inside_fell_back_to_on_top=len(fb))
tot = {k: sum(v[k] for v in rows.values()) for k in next(iter(rows.values()))}
for k, v in rows.items():
    print(k, v)
print("total", tot)
why = collections.Counter(x.get("why") or ("error" if x.get("error") else ("sampler said no" if not x.get("sampled") else "ok"))
                          for x in objs.values())
print(why.most_common())
hid = [k for k, o in SNAP["objects"].items() if o["hidden"]]
h_ok = [k for k in hid if objs.get(k, {}).get("holds_after_settle")]
print("hidden in snapshot:", len(hid), "placed and holding:", len(h_ok))
opened = sum(1 for x in objs.values() if x.get("opened_to_sample"))
print("cabinet opened to sample:", opened)
VIEWS = ["kitchen_kitchen_cabinet_by_the_range_countertop_by_the_range", "dining_room_dining_table_tabletop",
         "living_room_living_room_coffee_table_top", "bedroom_1_nightstand_by_the_main_bed_top_of_the_nightstand",
         "bathroom_2_bathroom_vanity_by_the_bathtub_vanity_top", "entryway_floor"]
for v in VIEWS:
    ks = [k for k, o in SNAP["objects"].items() if o["place"] == v]
    print(v[:40], "objects", len(ks), "sampled", sum(1 for k in ks if objs.get(k, {}).get("sampled")),
          "hold", sum(1 for k in ks if objs.get(k, {}).get("holds_after_settle")), "target", objs.get(ks[0], {}).get("target"))
t = json.load(open(f"{OUT}/mapping/placement_timing.json"))
print(t)
fails = [x for x in objs.values() if x.get("category") and not x.get("sampled")]
print("failed examples:", [(x["obj"][:28], x.get("relation_used"), x.get("target"), (x.get("why") or x.get("error", ""))[:50]) for x in fails[:40]])
