#!/usr/bin/env python3
"""Regime-search diagnostics on a confshift output dir (banks/ + classical/).
Per agent: accuracy per day (all questions and the moved-since-round half), with the weekday letter.
Oracles from truth alone: RECENCY (location at the last sighting before t: patrol or feedback) and ROUTINE
(leave-one-day-out: most common true location of the object in the same hour bin on previous days of the same
kind, weekday/weekend), plus a SAME-TIME-YESTERDAY oracle. Per object class: n, moved share, last-5-day accuracy
of each agent and of the routine oracle -> which classes are learnable.
Usage: analyze.py <dir> [--label t03] [--bin 2] [--last 5] [--classes] [--stage]"""
import argparse, collections, glob, json, os, sys, bisect
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)).rsplit('/results', 1)[0], 'src'))
from baselines.patrol.bank import _Truth  # noqa
WD = "MTWTFSS"
SHORT = {"LastObservation": "lastseen", "MostFrequentLocation": "mostfreq", "TimetableLookup(bin=2h,days=all)": "timetable",
         "PeriodicPersistence(min_dep=2,bin=1h,hl=24h)": "periodic", "PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)": "perpetua",
         "TimetableLookup(bin=2h,days=all,hl=72h)": "timetable_hl3d", "TimetableLookup(bin=2h,days=all,hl=24h)": "timetable_hl1d",
         "MostFrequentLocation(hl=24h)": "mostfreq_hl1d", "MostFrequentLocation(hl=72h)": "mostfreq_hl3d",
         "TimetableLookup(bin=2h,days=all,hl=168h)": "timetable_hl7d", "MostFrequentLocation(hl=168h)": "mostfreq_hl7d"}


def load(bank_path, bin_h):
    rows = [json.loads(l) for l in open(bank_path)]
    h = rows[0]; truth = _Truth([r for r in rows if r["kind"] == "truth"])
    day0 = h.get("day0_weekday", "Tuesday"); names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    i0 = names.index(day0)
    kind = lambda d: "we" if names[(i0 + d) % 7] in ("Saturday", "Sunday") else "wd"
    # sightings per object (patrol contents + observations), sorted by t
    sight = collections.defaultdict(list)
    for r in rows:
        if r["kind"] == "room_visit":
            for rec, objs in (r.get("contents") or {}).items():
                for o in objs: sight[o].append((r["t"], rec))
        elif r["kind"] == "observation":
            sight[r["object_id"]].append((r["t"], r["receptacle_id"]))
    for o in sight: sight[o].sort()
    qs = {}
    for r in rows:
        if r["kind"] != "question": continue
        t = r["t_query"]; d = r["day_index"]; o = r["object_id"]
        at = truth.at(o, t); night = truth.at(o, (t // 86400) * 86400 + 3 * 3600)
        ts = [s[0] for s in sight[o]]; i = bisect.bisect_left(ts, t) - 1
        recency = sight[o][i][1] if i >= 0 else None
        # routine oracle: same hour bin on previous days of the same kind, from truth
        hb = (t % 86400) // (bin_h * 3600); votes = collections.Counter()
        for pd in range(0, d):
            if kind(pd) != kind(d): continue
            votes[truth.at(o, pd * 86400 + hb * bin_h * 3600 + bin_h * 1800)] += 1
        routine = votes.most_common(1)[0][0] if votes else None
        yest = truth.at(o, t - 86400) if d >= 1 else None
        qs[r["question_id"]] = dict(day=d, wd=kind(d), cls=r.get("object_class", o.rsplit("_", 1)[0]), obj=o, truth=at,
                                    moved=(at != night), recency=recency, routine=routine, yest=yest, stage=r.get("stage"))
    return h, qs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--label", default="t03"); ap.add_argument("--bin", type=int, default=2)
    ap.add_argument("--last", type=int, default=5); ap.add_argument("--classes", action="store_true"); ap.add_argument("--stage", action="store_true")
    ap.add_argument("--moved-only", action="store_true")
    a = ap.parse_args()
    acc = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))  # agent -> (day, split) -> [n, ok]
    cls = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))  # agent -> cls -> [n, ok] (last N days)
    clsinfo = collections.defaultdict(lambda: [0, 0])
    stage = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    ndays = 0; day0 = None
    for bp in sorted(glob.glob(f"{a.dir}/banks/hh_s*_{a.label}.jsonl")):
        hh = os.path.basename(bp).split("_" + a.label)[0]
        h, qs = load(bp, a.bin); ndays = max(ndays, h["n_days"]); day0 = h.get("day0_weekday")
        lastdays = set(range(h["n_days"] - a.last, h["n_days"]))
        def add(agent, q, ok):
            for sp in (("moved" if q["moved"] else "still"), "all"):
                x = acc[agent][(q["day"], sp)]; x[0] += 1; x[1] += ok
            if q["day"] in lastdays and (q["moved"] or not a.moved_only):
                x = cls[agent][q["cls"]]; x[0] += 1; x[1] += ok
            if q.get("stage") is not None:
                x = stage[agent][(q["stage"], "moved" if q["moved"] else "still")]; x[0] += 1; x[1] += ok
        for q in qs.values():
            clsinfo[q["cls"]][0] += 1; clsinfo[q["cls"]][1] += q["moved"]
            add("oracle:recency", q, int(q["recency"] == q["truth"]))
            add("oracle:routine", q, int(q["routine"] == q["truth"]))
            add("oracle:yesterday", q, int(q["yest"] == q["truth"]))
        cp = f"{a.dir}/classical/{hh}_{a.label}.jsonl"
        if os.path.exists(cp):
            for l in open(cp):
                r = json.loads(l); q = qs.get(r["question_id"])
                if q: add(SHORT.get(r["belief"], r["belief"]), q, int(r["correct"]))
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]; i0 = names.index(day0 or "Tuesday")
    hdr = " ".join(f"{names[(i0+d)%7][0]}{d:<2d}" for d in range(1, ndays))
    print(f"{a.dir}: {ndays} days from {day0}; accuracy per day (%), then the moved-since-round half\n{'agent':17s} {hdr}")
    for split in ("all", "moved"):
        print(f"--- {split}")
        for agent in ["oracle:recency", "oracle:yesterday", "oracle:routine", "lastseen", "mostfreq", "mostfreq_hl1d", "mostfreq_hl3d", "timetable", "timetable_hl7d", "timetable_hl3d", "timetable_hl1d", "periodic", "perpetua"]:
            if agent not in acc: continue
            cells = [acc[agent].get((d, split), [0, 0]) for d in range(1, ndays)]
            print(f"{agent:17s} " + " ".join(f"{100*x[1]/x[0]:3.0f}" if x[0] else "  -" for x in cells))
    if a.classes:
        print(f"\n--- per class, last {a.last} days ({'moved half only' if a.moved_only else 'all questions'}): n, moved%, then accuracy per agent")
        agents = [g for g in ["oracle:routine", "lastseen", "mostfreq", "timetable", "periodic", "perpetua"] if g in cls]
        print(f"{'class':18s} {'n':>5s} {'mv%':>4s} " + " ".join(f"{g[:9]:>9s}" for g in agents))
        for c, (n, mv) in sorted(clsinfo.items(), key=lambda x: -x[1][0])[:40]:
            print(f"{c:18s} {n:5d} {100*mv/n:4.0f} " + " ".join(f"{100*cls[g][c][1]/cls[g][c][0]:9.0f}" if cls[g][c][0] else f"{'-':>9s}" for g in agents))
    if a.stage and stage:
        print("\n--- per stage (moved | still)")
        for agent in stage:
            print(f"{agent:17s} " + "  ".join(f"{k[0]}:{100*v[1]/v[0]:.0f}({v[0]})" for k, v in sorted(stage[agent].items())))


if __name__ == "__main__":
    main()
