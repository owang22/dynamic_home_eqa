"""The whole told family on the five wider homes, paired on household. Days capped at 30
because one cell is still writing day 31."""
import json, pathlib, statistics
ROOT = pathlib.Path("results/self_improve/wave_told_on_the_wider_homes/cells")
HOMES = ["hh_s32_t03","hh_s48_t03","hh_s63_t03","hh_s93_t03","hh_s151_t03"]
WIN = {"settled 1-13": range(1,14), "day 14": range(14,15), "15-16": range(15,17),
       "spell 17-23": range(17,24), "day 24": range(24,25), "25-26": range(25,27),
       "normal 27-30": range(27,31)}
MEAS = {"first": lambda r: r.get("found_at_step")==1,
        "found": lambda r: bool(r.get("found_it")),
        "place": lambda r: bool(r.get("correct_place"))}
FLOOR={"first":1.9,"found":2.2,"place":2.2}
BASE="the_log_and_notes_about_the_routine"
TOLD=["ours_told_the_night_before","ours_told_and_asked_what_changes","ours_told_on_the_first_night","ours_a_profile_and_told"]

def load(arm,home):
    f=ROOT/arm/home/"searches.jsonl"
    if not f.exists(): return None
    return [r for r in (json.loads(l) for l in f.open()) if r.get("kind")=="search" and r["day"]<=30]
data={a:{h:load(a,h) for h in HOMES} for a in [BASE]+TOLD}
def cell(a,h,w,m):
    rs=[r for r in data[a][h] if r["day"] in WIN[w]]
    if len(rs)<8: return None
    return 100*sum(1 for r in rs if MEAS[m](r))/len(rs)
print("last day (<=30) per home:")
for a in [BASE]+TOLD: print(f"  {a:38s} {[max(r['day'] for r in data[a][h]) for h in HOMES]}")
for m in ("first","found"):
    print(f"\n===== {m}: mean over the five homes")
    print(f"{'arm':38s}"+"".join(f"{w:>14s}" for w in WIN))
    for a in [BASE]+TOLD:
        line=f"{a:38s}"
        for w in WIN:
            vs=[v for v in (cell(a,h,w,m) for h in HOMES) if v is not None]
            line += f"{(f'{statistics.mean(vs):.1f}'+('' if len(vs)==5 else f'({len(vs)})')):>14s}" if vs else f"{'-':>14s}"
        print(line)
for m in ("first","found"):
    print(f"\n===== paired, {m}: told arm minus told-nothing, 2 SE across homes, floor {FLOOR[m]}")
    for a in TOLD:
        print(f"  {BASE} -> {a}")
        for w in WIN:
            d=[]
            for h in HOMES:
                x,y=cell(BASE,h,w,m),cell(a,h,w,m)
                if x is not None and y is not None: d.append(round(y-x,1))
            if len(d)<2: continue
            mn=statistics.mean(d); tse=2*statistics.stdev(d)/len(d)**0.5
            same=sum(1 for v in d if v>0), sum(1 for v in d if v<0)
            v="CLEARS" if abs(mn)>tse and abs(mn)>FLOOR[m] else ("under 2 SE" if abs(mn)<=tse else "under the floor")
            print(f"      {w:14s} {mn:+7.1f}  2SE {tse:5.1f}  n={len(d)}  per-home {d}  up/down {same}  {v}")

print("\n\n########## the pair that differs ONLY in the profile (both told on night 0)")
A,Bp="ours_told_on_the_first_night","ours_a_profile_and_told"
for m in ("first","found","place"):
    print(f"\n===== {m}: profile minus no profile, floor {FLOOR[m]}")
    for w in WIN:
        d=[]
        for h in HOMES:
            x,y=cell(A,h,w,m),cell(Bp,h,w,m)
            if x is not None and y is not None: d.append(round(y-x,1))
        if len(d)<2: continue
        mn=statistics.mean(d); tse=2*statistics.stdev(d)/len(d)**0.5
        v="CLEARS" if abs(mn)>tse and abs(mn)>FLOOR[m] else ("under 2 SE" if abs(mn)<=tse else "under the floor")
        print(f"   {w:14s} {mn:+7.1f}  2SE {tse:5.1f}  n={len(d)}  per-home {d}  up {sum(1 for v2 in d if v2>0)} down {sum(1 for v2 in d if v2<0)}  {v}")
