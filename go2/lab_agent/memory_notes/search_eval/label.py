"""python3 label.py "<query>" "<relevant indices: 1,2,5-9 or all-3,4 or none>" ["note"] -> appends to labels.json"""
import sys, json, os
idx = json.load(open("sheets/index.json"))
q, spec = sys.argv[1], sys.argv[2]
ids = idx[q]
def rng(s):
    out = set()
    for p in filter(None, s.split(",")):
        a, _, b = p.partition("-")
        out |= set(range(int(a), int(b or a) + 1))
    return out
if spec == "none": rel = set()
elif spec.startswith("all"): rel = set(range(len(ids))) - rng(spec[4:])
else: rel = rng(spec)
L = json.load(open("labels.json")) if os.path.exists("labels.json") else {}
L[q] = {"relevant": [ids[i] for i in sorted(rel)], "pool": len(ids), "note": sys.argv[3] if len(sys.argv) > 3 else ""}
json.dump(L, open("labels.json", "w"), indent=1)
print(q, len(rel), "/", len(ids))
