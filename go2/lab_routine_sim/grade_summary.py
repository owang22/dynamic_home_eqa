"""Summarise grades/: share of props whose rule the memory states correctly (or partly), by method, day and rule
type; and how often a changed rule was said to have changed. python grade_summary.py"""
import collections, glob, json, sys
sys.path.insert(0, ".")
import world as W
G = collections.defaultdict(list)
for f in glob.glob("grades/*/seed_*_day_*.json"):
    g = json.load(open(f))
    if not g["grades"]:
        continue
    w = W.make_world(g["seed"])
    for p, v in g["grades"].items():
        G[g["method"]].append({"day": g["day"], "seed": g["seed"], "prop": p, "rule": W.rule_now(w, p, g["day"])["type"],
                               "grade": v["rule"], "change": v["change_noticed"], "reason": v["reason"]})
out = {}
for m, rows in sorted(G.items()):
    print(f"\n== {m}  ({len(rows)} prop-grades)")
    days = sorted({r["day"] for r in rows})
    print("day      " + " ".join(f"{d:>11d}" for d in days) + "   (correct / correct+partial)")
    line = []
    for d in days:
        rr = [r for r in rows if r["day"] == d]
        c = sum(r["grade"] == "correct" for r in rr) / len(rr); cp = sum(r["grade"] in ("correct", "partial") for r in rr) / len(rr)
        line.append(f"{c:.2f}/{cp:.2f}")
    print("all      " + " ".join(f"{x:>11s}" for x in line))
    for t in W.RULE_TYPES:
        rr = [r for r in rows if r["rule"] == t]
        by = []
        for d in days:
            x = [r for r in rr if r["day"] == d]
            by.append(f"{sum(r['grade'] == 'correct' for r in x)}/{len(x)}")
        print(f"{t:9s}" + " ".join(f"{x:>11s}" for x in by))
    ch = [r for r in rows if r["day"] >= W.CHANGE_DAY and W.make_world(r["seed"]).rules[r["prop"]]["after"]]
    print("change noticed (changed props, days >= 20): " + ", ".join(
        f"day {d}: {sum(r['change'] == 'yes' for r in ch if r['day'] == d)}/{sum(1 for r in ch if r['day'] == d)}" for d in days if d >= 20))
    out[m] = rows
json.dump(out, open("grades_summary.json", "w"))
