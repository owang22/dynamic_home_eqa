"""Summarise a settle_<tag>.json from t06_hssd_settle.py."""
import collections
import json
import sys

d = json.load(open(sys.argv[1]))
full = len(sys.argv) > 2
ended = {e["obj"]: e for e in d["ended"]}
sim = [s["obj"] for s in d["settle"]]
mir = set(d.get("mirrored_spots", []))
print("tag", d["tag"], "simulated", len(sim), "joints locked", d.get("joints_locked"), "static", d.get("static_dataset"),
      "steps", d["settle_steps"], "dt", d["sim_step_dt"])
kind = {k: ended[k]["intended_kind"] for k in sim}
ov = {o["obj"]: o for o in d["overlap"]}
big = {s["obj"]: s for s in d["settle_big"]}
print("\nBy the kind of spot the snapshot named (n / pushed out with gravity off / moved >2cm or tilted >10deg in 2 s):")
tot = collections.Counter(kind.values())
for k, n in tot.most_common():
    print(f"  {k:13s} {n:3d} {sum(1 for x in ov if kind[x]==k):3d} {sum(1 for x in big if kind[x]==k):3d}")
print("  on mirrored furniture:", sum(1 for k in sim if ended[k]["intended"] in mir), "objects;",
      sum(1 for k in big if ended[k]["intended"] in mir), "of them moved")
p = collections.Counter()
for o in d["overlap"]:
    b = o["boxes_overlapping_at_placement"]
    p["furniture" if any(n.startswith("hssd") for n in b) else ("another object" if b else "no box overlap (pushed by a tight contact)")] += 1
print("\nPushed with gravity off, what its box overlapped at placement:", dict(p))
dz = [s for s in d["settle"] if s["dz_m"] < -0.10]
print("\nDropped more than 10 cm in the settle:", len(dz))
moves = sorted(big.values(), key=lambda s: -s["moved_m"])
print("Moved >2 cm or tilted >10 deg:", len(big), "of", len(sim))
small_tilt = sum(1 for s in big.values() if s["moved_m"] <= 0.02)
print("  only tilted:", small_tilt, "; moved 2-10 cm:", sum(1 for s in big.values() if 0.02 < s["moved_m"] <= 0.10),
      "; moved >10 cm:", sum(1 for s in big.values() if s["moved_m"] > 0.10))
print("\nWhere things ended (intended kind -> ended kind, counting only those that left their furniture):")
c = collections.Counter((e["intended_kind"], e["ended_kind"]) for e in d["ended"] if not e["same_furniture"])
for k, v in c.most_common():
    print(f"  {v:3d} {k[0]} -> {k[1]}")
flat_to = [e for e in d["ended"] if e["intended_kind"] == "flat surface" and e["ended_kind"] in ("basin", "cooktop", "seat", "bed", "tub")]
print("Flat surface -> basin/cooktop/seat/bed/tub:", [(e["obj"], e["intended"], e["ended"]) for e in flat_to])
print("\nChanges from the snapshot, by reason:")
r = collections.Counter((x["done"].split(" (")[0][:60], x["reason"][:90]) for x in d["changes"])
for k, v in r.most_common():
    print(f"  {v:3d} {k[0]} | {k[1]}")
if d.get("layout"):
    L = d["layout"]
    print("\nLayout: spots", len(L), "objects fitted", sum(v["fitted"] for v in L.values()), "not fitted",
          sum(v["not_fitted"] for v in L.values()), "spots with no surface found",
          [k for k, v in L.items() if v["surface_cells"] == 0])
if full:
    print("\nAll that moved:")
    for s in moves:
        e = ended[s["obj"]]
        print(f"  {s['obj'][:34]:34s} {e['intended'][:48]:48s} moved {s['moved_m']:.2f} tilt {s['tilt_deg']:.0f} -> {e['ended'][:40]}")
