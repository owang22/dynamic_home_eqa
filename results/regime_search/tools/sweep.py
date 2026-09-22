#!/usr/bin/env python3
"""Memory x spell-length summary: for each regime dir and agent, stage means (mean of per-household stage accuracy, ± sd),
the break at the shift (day 13 -> 14), the break at the return (last sick day -> first return day), days inside the
spell until the agent is back within 5 points of its lead level, and the return re-learn time."""
import sys, os, json, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load, SHORT
ORDER = ["timetable_hl1d", "timetable_hl3d", "timetable_hl7d", "timetable", "mostfreq_hl1d", "mostfreq_hl3d", "mostfreq_hl7d", "mostfreq", "lastseen"]
LABEL = {"timetable_hl1d": "timetable 1 d", "timetable_hl3d": "timetable 3 d", "timetable_hl7d": "timetable 7 d", "timetable": "timetable never forgets",
         "mostfreq_hl1d": "most freq 1 d", "mostfreq_hl3d": "most freq 3 d", "mostfreq_hl7d": "most freq 7 d", "mostfreq": "most freq never forgets", "lastseen": "last seen"}


def summarize(d, label="t03"):
    per = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))  # agent -> (hh, day) -> [n, ok]
    stages = {}; nd = 0
    for bp in sorted(glob.glob(f"{d}/banks/hh_s*_{label}.jsonl")):
        hh = os.path.basename(bp).split("_" + label)[0]; h, qs = load(bp, 2); nd = h["n_days"]
        stages = {int(k): v for k, v in (h.get("stages") or {}).items()}
        cp = f"{d}/classical/{hh}_{label}.jsonl"
        if not os.path.exists(cp): continue
        for l in open(cp):
            r = json.loads(l); q = qs.get(r["question_id"]); ag = SHORT.get(r["belief"])
            if q and ag: x = per[ag][(hh, q["day"])]; x[0] += 1; x[1] += int(r["correct"])
    days_of = collections.defaultdict(list)
    for dd in range(1, nd): days_of[stages.get(dd, "plain")].append(dd)
    out = {}
    for ag in ORDER:
        if ag not in per: continue
        def daily(dd):
            n = ok = 0
            for (hh, x), v in per[ag].items():
                if x == dd: n += v[0]; ok += v[1]
            return 100 * ok / n if n else None
        def stage(name):
            vals = []
            for hh in {k[0] for k in per[ag]}:
                n = ok = 0
                for dd in days_of[name]:
                    v = per[ag].get((hh, dd), [0, 0]); n += v[0]; ok += v[1]
                if n: vals.append(100 * ok / n)
            m = sum(vals) / len(vals); sd = (sum((v - m) ** 2 for v in vals) / max(1, len(vals) - 1)) ** 0.5
            return m, sd
        lead = stage("lead"); sick = stage("sick"); ret = stage("return")
        s0, s1 = days_of["sick"][0], days_of["sick"][-1]; r0 = days_of["return"][0]
        entry = daily(s0) - daily(s0 - 1); back = daily(r0) - daily(s1)
        lead_level = sum(daily(dd) for dd in days_of["lead"][-5:]) / 5
        rec = next((dd - s0 + 1 for dd in days_of["sick"] if daily(dd) >= lead_level - 5), None)
        rec_r = next((dd - r0 + 1 for dd in days_of["return"] if daily(dd) >= lead_level - 5), None)
        out[ag] = dict(lead=lead, sick=sick, ret=ret, entry=entry, back=back, rec=rec, rec_r=rec_r)
    return out, len(days_of["sick"])


if __name__ == "__main__":
    for d in sys.argv[1:]:
        out, L = summarize(d)
        print(f"\n== {os.path.basename(d)}: spell {L} days.  stage mean±sd (lead | sick | return) · drop at entry · drop at return · days to recover in spell / on return")
        for ag, v in out.items():
            f = lambda t: f"{t[0]:4.0f}±{t[1]:2.0f}"
            print(f"  {LABEL[ag]:24s} {f(v['lead'])} | {f(v['sick'])} | {f(v['ret'])}   {v['entry']:+4.0f}   {v['back']:+4.0f}   {v['rec'] if v['rec'] else '-':>3} / {v['rec_r'] if v['rec_r'] else '-'}")
