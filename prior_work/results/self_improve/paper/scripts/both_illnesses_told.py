"""Told the night before against told nothing, on the bank with two illnesses."""
import json, pathlib, statistics
R=pathlib.Path("results/self_improve/wave_the_second_illness/cells")
HOMES=["hh_s2_t03","hh_s32_t03","hh_s48_t03"]
WIN={"settled 1-13":range(1,14),"day 14":range(14,15),"first spell 15-23":range(15,24),
     "day 24":range(24,25),"between 25-31":range(25,32),"day 32":range(32,33),
     "second spell 33-41":range(33,42),"day 42":range(42,43),"after 43-49":range(43,50)}
MEAS={"first":lambda r:r.get("found_at_step")==1,"found":lambda r:bool(r.get("found_it"))}
FLOOR={"first":1.9,"found":2.2}
BASE="the_log_and_notes_about_the_routine"; TOLD="ours_told_the_night_before"
def load(a,h):
    return [r for r in (json.loads(l) for l in (R/a/h/"searches.jsonl").open()) if r.get("kind")=="search"]
data={a:{h:load(a,h) for h in HOMES} for a in (BASE,TOLD,"last_seen_no_model")}
def cell(a,h,w,m):
    rs=[r for r in data[a][h] if r["day"] in WIN[w]]
    if len(rs)<8: return None
    return 100*sum(1 for r in rs if MEAS[m](r))/len(rs)
for m in ("first","found"):
    print(f"\n===== {m}: mean over the three homes")
    print(f"{'arm':38s}"+"".join(f"{w[:13]:>15s}" for w in WIN))
    for a in (BASE,TOLD,"last_seen_no_model"):
        line=f"{a:38s}"
        for w in WIN:
            vs=[v for v in (cell(a,h,w,m) for h in HOMES) if v is not None]
            line+=f"{(f'{statistics.mean(vs):.1f}'+('' if len(vs)==3 else f'({len(vs)})')):>15s}" if vs else f"{'-':>15s}"
        print(line)
    print(f"  paired: told minus told-nothing, floor {FLOOR[m]}")
    for w in WIN:
        d=[]
        for h in HOMES:
            x,y=cell(BASE,h,w,m),cell(TOLD,h,w,m)
            if x is not None and y is not None: d.append(round(y-x,1))
        if len(d)<2: continue
        mn=statistics.mean(d); tse=2*statistics.stdev(d)/len(d)**0.5
        v="CLEARS" if abs(mn)>tse and abs(mn)>FLOOR[m] else ("under 2 SE" if abs(mn)<=tse else "under the floor")
        print(f"     {w:20s} {mn:+7.1f}  2SE {tse:5.1f}  n={len(d)}  per-home {d}  {v}")
print("\n===== how far each arm falls at each change point (settled window minus the day), first room right")
for a in (BASE,TOLD,"last_seen_no_model"):
    for day,before in (("day 14","settled 1-13"),("day 32","between 25-31")):
        d=[]
        for h in HOMES:
            x,y=cell(a,h,before,"first"),cell(a,h,day,"first")
            if x is not None and y is not None: d.append(round(x-y,1))
        if d: print(f"  {a:38s} {day}: falls {statistics.mean(d):5.1f} (2 SE {2*statistics.stdev(d)/len(d)**0.5:4.1f}) per-home {d}")
