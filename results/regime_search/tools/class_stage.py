#!/usr/bin/env python3
"""Per class x stage accuracy for one agent (default timetable) on a regime dir: which classes carry the break."""
import sys, json, glob, collections, os
d = sys.argv[1]; agent = sys.argv[2] if len(sys.argv) > 2 else "TimetableLookup(bin=2h,days=all)"
acc = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0])); stages = []
for cp in sorted(glob.glob(f"{d}/classical/hh_s*.jsonl")):
    for l in open(cp):
        r = json.loads(l)
        if r["belief"] != agent: continue
        st = r.get("stage") or "plain"
        if st not in stages: stages.append(st)
        x = acc[r["object_class"]][st]; x[0] += 1; x[1] += int(r["correct"])
print(f"{agent} — accuracy per class and stage (n)")
print(f"{'class':16s} " + " ".join(f"{s:>14s}" for s in stages))
for c in sorted(acc, key=lambda c: -sum(v[0] for v in acc[c].values())):
    print(f"{c:16s} " + " ".join(f"{100*acc[c][s][1]/acc[c][s][0]:5.0f} ({acc[c][s][0]:4d})" if acc[c][s][0] else f"{'-':>14s}" for s in stages))
