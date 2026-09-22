#!/usr/bin/env python3
"""Collect the data for the story page: per regime, per agent, per household, per day: [n, ok, sum_conf] for all
questions and for the moved-since-round half (sum_conf = sum of the method's own stated confidence for its answer,
so mean confidence = sum_conf/n); stage per day; detector fire days per household per base; conformal coverage / set
size per day (pooled); BMA short-memory weight per day (mean over households); reliability bins (5 confidence bins,
[n, ok, sum_conf] each) per agent, per split (all / moved-only), per stage (lead / sick / return / any) — the
calibration data, pooled over households. No re-run of any model: every number here already sits in the classical
and UQ jsonl logs (top_prob, or conf_set = 1/|conformal set| for the honest-sets agents)."""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load, SHORT  # noqa
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UQ = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq", "regime")
CLASSICAL = {"timetable_hl3d": "tt3d", "timetable": "ttfrozen", "mostfreq_hl3d": "mf3d", "mostfreq": "mffrozen", "lastseen": "lastseen",
             "perpetua": "perpetua", "timetable_hl1d": "tt1d", "mostfreq_hl1d": "mf1d"}
# uq/regime/<regime>/<dir-name>/*.jsonl -> series key. mart_tt72/mart_tt are the change-alarm-with-reset agent on the
# 3-day and never-forgets timetable bases; bma_tt/bma_obj are the hedge with one shared vs one per-object trust
# vector; ocp_tt is the nudging honest-sets conformal agent, nexcp_tt the weighted-quantile variant (Barber, Candès,
# Ramdas, Tibshirani 2023).
UQA = {"mart_tt72": "detector3d", "mart_tt": "detectorfrozen", "bma_tt": "bma", "bma_obj": "bmaobj",
       "ocp_tt": "conformal", "nexcp_tt": "nexcp"}
N_BINS = 5


def conf_of(r):
    """The method's own claimed confidence for its answer: 1/|set| for the honest-sets agents, its stated
    top probability otherwise. Always in [0, 1]."""
    c = r.get("conf_set")
    return float(c) if c is not None else float(r.get("top_prob", 0.0))


def regime(d, label="t03"):
    out = {"agents": {}, "stages": {}, "days": 0, "day0": "Monday", "hh": [], "fires": {}, "conformal": {}, "bma_short": {}, "calib": {}}
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
                conf = conf_of(r); ok = int(r["correct"])
                A = out["agents"].setdefault(key, {}).setdefault(hh, {"all": [[0, 0, 0.0] for _ in range(h["n_days"])], "moved": [[0, 0, 0.0] for _ in range(h["n_days"])]})
                a0 = A["all"][q["day"]]; a0[0] += 1; a0[1] += ok; a0[2] += conf
                if q["moved"]:
                    a1 = A["moved"][q["day"]]; a1[0] += 1; a1[1] += ok; a1[2] += conf
                # reliability bins: claimed confidence vs. actual correctness, pooled over households, split by
                # split (all questions / moved-only) and by stage (lead / sick / return / any = every stage pooled)
                C = out["calib"].setdefault(key, {})
                b = min(N_BINS - 1, max(0, int(conf * N_BINS)))
                for sp in (("all",) if not q["moved"] else ("all", "moved")):
                    Csp = C.setdefault(sp, {})
                    for stage in (q["stage"], "any") if q.get("stage") else ("any",):
                        bins = Csp.setdefault(stage, [[0, 0, 0.0] for _ in range(N_BINS)])
                        cell = bins[b]; cell[0] += 1; cell[1] += ok; cell[2] += conf
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
        print(k, len(v["hh"]), "hh", v["days"], "days", "agents", sorted(v["agents"]),
              "fires", {a: sum(len(x) for x in b.values()) for a, b in v["fires"].items()},
              "conf days", len(v["conformal"]), "bma days", len(v["bma_short"]),
              "calib agents", len(v["calib"]))


if __name__ == "__main__":
    main()
