"""The budget trend restricted to questions where the 40-sighting cap never bit."""
import collections, json, pathlib, statistics
CAP=40; OURS="the_log_and_notes_about_the_routine"; RULE="last_seen_no_model"
RUNS=[(4,"wave_the_budget_sweep_q4"),(8,"wave_the_budget_sweep_q8"),(24,"wave_wider_five")]
MEAS={"first room right":lambda r:r.get("found_at_step")==1,"found within 3":lambda r:bool(r.get("found_it"))}
FLOOR={"first room right":1.9,"found within 3":2.2}
def rows(cell):
    return {r["question_id"]:r for r in (json.loads(l) for l in (cell/"searches.jsonl").open()) if r.get("kind")=="search"}
def held(cell):
    seen=collections.defaultdict(list)
    for l in (cell/"looks.jsonl").open():
        for s in json.loads(l).get("sightings",[]): seen[s["object_id"]].append(s["time"])
    return {r["question_id"]: sum(1 for t in seen.get(r["object_id"],[]) if t<=r["time"]) for r in rows(cell).values()}
for measure,fn in MEAS.items():
    print(f"\n=== {measure}: our arm minus last-seen, five wider homes, paired, floor {FLOOR[measure]}")
    print(f"{'questions a day':>16s}{'every question':>28s}{'only where nothing was cut':>34s}")
    for q,wave in RUNS:
        root=pathlib.Path("results/self_improve")/wave/"cells"
        homes=sorted(p.name for p in (root/OURS).iterdir() if p.is_dir())
        both={}
        for group in ("all","uncut"):
            per=[];n=0
            for h in homes:
                o,r_,hd=rows(root/OURS/h),rows(root/RULE/h),held(root/OURS/h)
                qs=[k for k in o if k in r_ and (group=="all" or hd[k]<=CAP)]
                if len(qs)<8: continue
                per.append(100*sum(1 for k in qs if fn(o[k]))/len(qs)-100*sum(1 for k in qs if fn(r_[k]))/len(qs)); n+=len(qs)
            tse=2*statistics.stdev(per)/len(per)**0.5
            both[group]=f"{statistics.mean(per):+5.1f} (2 SE {tse:4.1f}, {sum(1 for v in per if v>0)}/{len(per)} up, {n} q)"
        print(f"{q:>16d}{both['all']:>28s}{both['uncut']:>34s}")
