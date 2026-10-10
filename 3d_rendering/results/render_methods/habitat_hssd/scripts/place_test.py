"""Build the scene, place all 251 objects, write checks/placement.json and print counts."""
import collections, json, sys, time
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import scene, common
t0 = time.time()
home = scene.Home()
home.place_everything()
people = home.add_people()
print("timings", home.timings, "total", round(time.time() - t0, 1))
recs = home.records
c = collections.Counter((r["relation"], r.get("placed", False)) for r in recs.values())
print(sorted(c.items()))
for oid, r in recs.items():
    if not r.get("placed"):
        print("NOT", oid, r.get("why"))
print(people)
grids = {p: {"cells": int(g.valid.sum()), "area_m2": round(g.valid.sum() * scene.CELL ** 2, 3),
             "snapshot_area": home.snap["places"][p]["geometry"]["area"]} for p, g in home.grids.items()}
json.dump({"records": recs, "people": people, "timings": home.timings, "grids": grids},
          open(common.OUT / "checks/placement.json", "w"), indent=1, default=str)
for p, g in grids.items():
    print(p[:70], g)
