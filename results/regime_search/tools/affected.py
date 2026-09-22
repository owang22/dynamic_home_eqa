#!/usr/bin/env python3
"""Partial shift: affected (objects owned by the sick resident) vs unaffected (everyone else's) — per agent, per stage:
accuracy and mean stated confidence (top_prob), with sd across households. Usage: affected.py <dir> [resident_1]"""
import sys, os, json, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load, SHORT
d = sys.argv[1]; sick = sys.argv[2] if len(sys.argv) > 2 else "resident_1"; label = "t03"
ORDER = ["timetable_hl1d", "timetable_hl3d", "timetable_hl7d", "timetable", "mostfreq_hl3d", "mostfreq", "perpetua", "lastseen"]
acc = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0.0]))  # agent -> (hh, stage, group) -> n, ok, conf
stages = {}
for bp in sorted(glob.glob(f"{d}/banks/hh_s*_{label}.jsonl")):
    hh = os.path.basename(bp).split("_" + label)[0]; rows = [json.loads(l) for l in open(bp)]; h = rows[0]
    stages = {int(k): v for k, v in (h.get("stages") or {}).items()}
    name_to_id = {r["name"].lower(): r["resident_id"] for r in h["protocol"]["residents"]}
    owner_of = lambda obj: name_to_id.get(obj.rsplit("_", 1)[-1].lower(), "shared")
    qs = {r["question_id"]: r for r in rows if r["kind"] == "question"}
    cp = f"{d}/classical/{hh}_{label}.jsonl"
    if not os.path.exists(cp): continue
    for l in open(cp):
        r = json.loads(l); q = qs.get(r["question_id"]); ag = SHORT.get(r["belief"])
        if not q or not ag: continue
        grp = "affected" if owner_of(q["object_id"]) == sick else "unaffected"
        x = acc[ag][(hh, stages.get(q["day_index"], "plain"), grp)]; x[0] += 1; x[1] += int(r["correct"]); x[2] += float(r.get("top_prob", 0))
print(f"{os.path.basename(d)}: affected = {sick}'s objects. Cells: accuracy% ± sd across hh / mean confidence")
print(f"{'agent':24s} " + " ".join(f"{st:>9s}-{g[:3]:3s}" for st in ("lead", "sick", "return") for g in ("affected", "unaffected")))
for ag in ORDER:
    if ag not in acc: continue
    cells = []
    for st in ("lead", "sick", "return"):
        for g in ("affected", "unaffected"):
            vals = [(100 * v[1] / v[0], v[2] / v[0]) for (hh, s, gg), v in acc[ag].items() if s == st and gg == g and v[0]]
            if not vals: cells.append(f"{'-':>13s}"); continue
            m = sum(a for a, _ in vals) / len(vals); sd = (sum((a - m) ** 2 for a, _ in vals) / max(1, len(vals) - 1)) ** 0.5; c = sum(b for _, b in vals) / len(vals)
            cells.append(f"{m:3.0f}±{sd:2.0f}/{c:.2f}")
    print(f"{ag:24s} " + " ".join(cells))
n = collections.Counter()
for ag in acc:
    for (hh, st, g), v in acc[ag].items(): n[(st, g)] += v[0]
    break
print("questions per stage/group:", dict(n))
