"""Fragmentation of single static objects under grouping settings. Ground truth: the hand-labelled search pictures
of objects there is only one of (blue mop bucket, sofa, grey equipment case, fridge, plant, podium). For each:
how many instances its sightings fall into, and the share in the largest. Also total instances (fewer = more
merging; purity is checked by hand separately)."""
import sys, json, itertools
sys.path.insert(0, "/home/oliver/robot/dynamic_home_eqa/go2/lab_agent")
import memory_instances as I
L = json.load(open("/home/oliver/robot/dynamic_home_eqa/go2/lab_agent/memory_notes/search_eval/labels.json"))
GT = {"blue mop bucket": ("bucket", "blue"), "sofa": ("sofa", ""), "grey equipment case": ("case", ""),
      "fridge": ("fridge", ""), "plant": ("plant", ""), "podium": ("podium", "")}
ss = I.sightings()


def score(groups):
    where = {s["key"]: n for n, g in enumerate(groups) for s in g}
    out = []
    for q, (name, col) in GT.items():
        rel = set(L[q]["relevant"])
        mine = [s for s in ss if s["id"] in rel and s["name"] == name and (not col or col in s["ckey"]) and s["key"] in where]
        if not mine:
            continue
        cnt = {}
        for s in mine:
            cnt[where[s["key"]]] = cnt.get(where[s["key"]], 0) + 1
        out.append((q, len(mine), len(cnt), max(cnt.values()) / len(mine)))
    return out


base = dict(JOIN_M=I.JOIN_M, JOIN_BIG_M=I.JOIN_BIG_M, BIG=set(I.BIG))
variants = [("JOIN 1.0, colour gate for all", dict(JOIN_M=1.0, JOIN_BIG_M=1.0, BIG=set())),
            ("JOIN 1.5, colour gate for all", dict(JOIN_M=1.5, JOIN_BIG_M=1.5, BIG=set())),
            ("JOIN 2.0, colour gate for all", dict(JOIN_M=2.0, JOIN_BIG_M=2.0, BIG=set())),
            ("JOIN 1.0, BIG 2.0 no colour", dict(JOIN_M=1.0)),
            ("JOIN 1.5, BIG 2.0 no colour (chosen)", {}),
            ("JOIN 2.0, BIG 2.0 no colour", dict(JOIN_M=2.0))]
for label, kw in variants:
    for k, v in {**base, **kw}.items():
        setattr(I, k, v)
    g = I.group(ss)
    sc = score(g)
    print(f"{label:38} instances {len(g):4}  " + "  ".join(f"{q.split()[-1]}:{n}->{k} ({top:.2f})" for q, n, k, top in sc))
for k, v in base.items():
    setattr(I, k, v)
