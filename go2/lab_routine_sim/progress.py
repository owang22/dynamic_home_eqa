"""Days done per method, plus how often calls fell back or kept the old memory. python progress.py"""
import glob, json, collections
rows = collections.defaultdict(list)
for f in sorted(glob.glob("runs/*/seed_*.json")):
    r = json.load(open(f)); m = f.split("/")[1]
    kept = sum(bool((d.get("evening_info") or {}).get("kept_old_memory")) for d in r["days"])
    fb = sum(bool((d.get("evening_info") or {}).get("fallback_no_thinking")) or bool((d.get("forecast_info") or {}).get("fallback_no_thinking")) for d in r["days"])
    short = sum(f_.get("plan_given", 5) < 5 for d in r["days"] for f_ in d["forecast"].values())
    rows[m].append((r["seed"], len(r["days"]), kept, fb, short))
for m, v in rows.items():
    print(f"{m:18s} days {[x[1] for x in v]}  kept_old {sum(x[2] for x in v)}  fallback {sum(x[3] for x in v)}  short_plans {sum(x[4] for x in v)}")
