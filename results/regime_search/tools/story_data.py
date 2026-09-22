#!/usr/bin/env python3
"""Collect the data for the story page: per regime, per agent, per household, per day: [n, ok] for all questions and
for the moved-since-round half; stage per day; detector fire days per household per base; conformal coverage / set
size per day (pooled); BMA short-memory weight per day (mean over households)."""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load, SHORT  # noqa
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UQ = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq", "regime")
CLASSICAL = {"timetable_hl3d": "tt3d", "timetable": "ttfrozen", "mostfreq_hl3d": "mf3d", "mostfreq": "mffrozen", "lastseen": "lastseen",
             "perpetua": "perpetua", "timetable_hl1d": "tt1d", "mostfreq_hl1d": "mf1d"}
UQA = {"mart_tt72": "detector3d", "bma_tt": "bma", "ocp_tt": "conformal"}


def regime(d, label="t03"):
    out = {"agents": {}, "stages": {}, "days": 0, "day0": "Monday", "hh": [], "fires": {}, "conformal": {}, "bma_short": {}}
    for bp in sorted(glob.glob(f"{d}/banks/hh_s*_{label}.jsonl")):
        hh = os.path.basename(bp).split("_" + label)[0]; h, qs = load(bp, 2)
        out["days"] = h["n_days"]; out["day0"] = h.get("day0_weekday", "Monday"); out["hh"].append(hh)
        for dd, st in (h.get("stages") or {}).items(): out["stages"][str(dd)] = st
        srcs = [(f"{d}/classical/{hh}_{label}.jsonl", None)] + [(f"{UQ}/{os.path.basename(d)}/{a}/{hh}_{label}.jsonl", a) for a in UQA]
        for cp, forced in srcs:
            if not os.path.exists(cp): continue
            cov = collections.defaultdict(lambda: [0, 0, 0]); wshort = collections.defaultdict(lambda: [0, 0.0])
            for l in open(cp):
                r = json.loads(l); q = qs.get(r["question_id"])
                if not q: continue
                key = UQA.get(forced) if forced else CLASSICAL.get(SHORT.get(r["belief"], ""))
                if not key: continue
                A = out["agents"].setdefault(key, {}).setdefault(hh, {"all": [[0, 0] for _ in range(h["n_days"])], "moved": [[0, 0] for _ in range(h["n_days"])]})
                A["all"][q["day"]][0] += 1; A["all"][q["day"]][1] += int(r["correct"])
                if q["moved"]: A["moved"][q["day"]][0] += 1; A["moved"][q["day"]][1] += int(r["correct"])
                if forced == "ocp_tt":
                    c = cov[q["day"]]; c[0] += 1; c[1] += int(r.get("covered") in (True, "True")); c[2] += float(r.get("set_size", 0))
                if forced == "bma_tt" and r.get("weights"):
                    w = r["weights"]; short = sum(float(v) for k, v in w.items() if k not in ("None", "inf", None) and float(k) <= 72)
                    x = wshort[q["day"]]; x[0] += 1; x[1] += short
            if forced == "ocp_tt":
                for day, c in cov.items():
                    x = out["conformal"].setdefault(str(day), [0, 0, 0.0]); x[0] += c[0]; x[1] += c[1]; x[2] += c[2]
            if forced == "bma_tt":
                for day, x in wshort.items():
                    y = out["bma_short"].setdefault(str(day), [0, 0.0]); y[0] += x[0]; y[1] += x[1]
        for a, key in (("mart_tt72", "detector3d"), ("mart_tt", "detectorfrozen")):
            sp = f"{UQ}/{os.path.basename(d)}/{a}/{hh}_{label}.side.json"
            if os.path.exists(sp):
                out["fires"].setdefault(key, {})[hh] = sorted({int(f["day"]) for f in json.load(open(sp)).get("fires", [])})
    return out


def main():
    regimes = {"household": "sick10_all", "household_rep": "sick10_all_s10_19", "person": "sick10_owner"}
    data = {k: regime(f"{ROOT}/{v}") for k, v in regimes.items()}
    json.dump(data, open(f"{ROOT}/story_data.json", "w"), separators=(",", ":"))
    for k, v in data.items():
        print(k, len(v["hh"]), "hh", v["days"], "days", "agents", sorted(v["agents"]), "fires", {a: sum(len(x) for x in b.values()) for a, b in v["fires"].items()}, "conf days", len(v["conformal"]), "bma days", len(v["bma_short"]))


if __name__ == "__main__":
    main()
