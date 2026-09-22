#!/usr/bin/env python3
"""Regime novelty: for every question in a non-lead stage, is the true location different from the LEAD-stage answer
for that (object, 2 h bin) (the mode of truth at lead-stage question times)? Share of 'novel' questions per stage and
per class = the ceiling of any accuracy drop a perfect lead-regime learner can suffer. Also: which residents' activities
the shift-stage questions come from (question moment text is not stored, so we use the object's owner)."""
import sys, json, glob, collections, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).rsplit('/results',1)[0] + '/src')
from baselines.patrol.bank import _Truth
d = sys.argv[1]; lead = sys.argv[2] if len(sys.argv) > 2 else "lead"
nov = collections.defaultdict(lambda: [0, 0]); novc = collections.defaultdict(lambda: [0, 0]); own = collections.defaultdict(lambda: [0, 0])
for bp in sorted(glob.glob(f"{d}/banks/hh_s*_t03.jsonl")):
    rows = [json.loads(l) for l in open(bp)]; h = rows[0]; tr = _Truth([r for r in rows if r["kind"] == "truth"])
    stages = {int(k): v for k, v in (h.get("stages") or {}).items()}
    qs = [r for r in rows if r["kind"] == "question"]
    mode = collections.defaultdict(collections.Counter)
    for r in qs:
        if stages.get(r["day_index"]) == lead:
            mode[(r["object_id"], (r["t_query"] % 86400) // 7200)][tr.at(r["object_id"], r["t_query"])] += 1
    for r in qs:
        st = stages.get(r["day_index"], "plain")
        if st == lead: continue
        k = (r["object_id"], (r["t_query"] % 86400) // 7200); truth = tr.at(r["object_id"], r["t_query"])
        lead_ans = mode[k].most_common(1)[0][0] if mode[k] else None
        novel = int(truth != lead_ans)
        nov[st][0] += 1; nov[st][1] += novel
        novc[(st, r.get("object_class"))][0] += 1; novc[(st, r.get("object_class"))][1] += novel
        o = r["object_id"].rsplit("_", 1)[-1]; own[(st, o)][0] += 1; own[(st, o)][1] += novel
print("share of questions whose truth differs from the lead-regime answer (ceiling of a drop):")
for st, v in sorted(nov.items()): print(f"  {st:10s} {100*v[1]/v[0]:.0f}% of {v[0]}")
print("by object owner suffix:")
for (st, o), v in sorted(own.items()): print(f"  {st:10s} {o:10s} {100*v[1]/v[0]:.0f}% ({v[0]})")
print("by class (shift stages only), sorted by novelty:")
for (st, c), v in sorted(novc.items(), key=lambda x: -x[1][1]/max(1,x[1][0])):
    if st != "return" and v[0] >= 30: print(f"  {st:10s} {c:16s} {100*v[1]/v[0]:.0f}% ({v[0]})")
