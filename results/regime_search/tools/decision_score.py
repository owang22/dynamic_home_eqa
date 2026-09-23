"""Decision score (coordinator, 2026-09-22): +1 right, -1 wrong, 0 abstain. Answer iff stated confidence > 0.5.
Classical rows from results/regime_search/sick10_owner/classical; LLM rows from the chain_person run logs."""
import json, glob, os, collections, statistics as st

CLS = "/home/oliver/robot/dynamic_home_eqa/results/regime_search/sick10_owner/classical"
LLM = "/home/oliver/robot/dynamic_home_eqa/results/confidence_shift_2026-09-20/uq/llm_strategies/chain_person/nottold"
WANT = {"TimetableLookup(bin=2h,days=all)": "never-forgets timetable",
        "TimetableLookup(bin=2h,days=all,hl=72h)": "3-day timetable",
        "PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)": "Perpetua*",
        "LastObservation": "last seen"}

rows = collections.defaultdict(lambda: collections.defaultdict(list))  # method -> hh -> (day, conf, correct)
for f in sorted(glob.glob(f"{CLS}/hh_s*_t03.jsonl")):
    hh = os.path.basename(f).split("_t03")[0]
    for line in open(f):
        r = json.loads(line)
        n = WANT.get(r["belief"])
        if n:
            rows[n][hh].append((r["day_index"], float(r["top_prob"]), bool(r["correct"])))

for d in sorted(glob.glob(f"{LLM}/hh_s*_longcontext_nottold_lookoff")):
    hh = os.path.basename(d).split("_t03")[0]
    p = os.path.join(d, "run_log.jsonl")
    if not os.path.exists(p): continue
    for line in open(p):
        r = json.loads(line)
        c = r.get("raw_confidence")
        if c is None: continue
        rows["long-context"][hh].append((r["day_index"], float(c), bool(r["correct"])))

def score_day(seq, bar=0.5):
    per = collections.defaultdict(int)
    for day, conf, ok in seq:
        per[day] += 0 if conf <= bar else (1 if ok else -1)
    return per

print(f"{'method':24s} {'hh':>3} | daily score, mean over households, by window (+1 right, -1 wrong, 0 abstain)")
W = {"lead 9-13": range(9,14), "sick 14-16": range(14,17), "spell 17-23": range(17,24),
     "back 24-26": range(24,27), "after 27-31": range(27,32)}
out = {}
for m, hhs in rows.items():
    per_hh = {h: score_day(s) for h, s in hhs.items()}
    line = []
    for name, rng in W.items():
        vals = [sum(per_hh[h].get(d,0) for d in rng) / max(1,len([d for d in rng if d in per_hh[h]])) for h in per_hh]
        line.append(f"{name} {st.mean(vals):+5.1f}")
    # abstain rate + accuracy for context
    allrows = [x for s in hhs.values() for x in s]
    ab = 100*sum(1 for _,c,_ in allrows if c <= 0.5)/len(allrows)
    acc = 100*sum(1 for _,_,ok in allrows if ok)/len(allrows)
    print(f"{m:24s} {len(hhs):>3} | " + "  ".join(line) + f"   [abstain {ab:4.1f}%, accuracy {acc:4.1f}%]")
