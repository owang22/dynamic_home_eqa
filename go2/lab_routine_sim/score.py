"""Score every run against the truth. python score.py [--out results.json]

Per method: first look right (props in the lab), looks to find (searched props; not found = 6), found within 3,
out-of-lab Brier, verdict on failed searches; split by period and by rule type. Paired differences between methods
use per-lab means (labs are the unit), with 2 standard errors."""
from __future__ import annotations

import argparse
import json
import math
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import world as W  # noqa: E402

PERIODS = {"wk1": range(1, 6), "wk2-3": range(6, 16), "wk4 (after change)": range(16, 21), "wk5-6": range(21, 31)}


def per_lab(run):
    """Per-lab rows: one dict per (day, prop) with the scores."""
    world = W.make_world(run["seed"])
    rows = []
    for d in run["days"]:
        day = d["day"]
        for p, f in d["forecast"].items():
            truth = world.truth[day][p]
            t = W.rule_now(world, p, day)["type"]
            row = {"day": day, "prop": p, "rule": t, "noise": world.noise[day][p], "out": truth is None,
                   "first_right": (f["plan"][:1] == [truth]) if truth else None,
                   "brier": (f["p_out"] - (1.0 if truth is None else 0.0)) ** 2, "failed_forecast": bool(f.get("failed"))}
            s = d["searches"].get(p)
            if s:
                if truth is not None:  # looks only for props really in the lab
                    row["looks"] = s["looks"] if s["found_at"] else 6
                    row["found3"] = bool(s["found_at"]) and s["looks"] <= 3
                    if not s["found_at"]:
                        row["said_out_wrongly"] = f["p_out"] >= 0.5
                else:
                    row["said_out_rightly"] = f["p_out"] >= 0.5
            rows.append(row)
    return rows


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


METRICS = {"first_right": ("first look right", lambda r: r["first_right"]),
           "looks": ("looks to find", lambda r: r.get("looks")),
           "found3": ("found within 3", lambda r: r.get("found3")),
           "brier": ("out-of-lab Brier", lambda r: r["brier"]),
           "out_caught": ("prop really out: said out (p>=0.5)", lambda r: r.get("said_out_rightly")),
           "out_false": ("in lab but not found: said out", lambda r: r.get("said_out_wrongly"))}


def summarize(rows_by_seed, select=lambda r: True):
    """Mean over labs of the per-lab mean, with the per-lab values kept for paired comparisons."""
    out = {}
    for k, (_, fn) in METRICS.items():
        per = {s: mean(fn(r) for r in rows if select(r)) for s, rows in rows_by_seed.items()}
        vals = [v for v in per.values() if v is not None]
        out[k] = {"mean": mean(vals), "per_lab": per}
    return out


def paired(a, b):
    seeds = [s for s in a["per_lab"] if s in b["per_lab"] and a["per_lab"][s] is not None and b["per_lab"][s] is not None]
    diffs = [a["per_lab"][s] - b["per_lab"][s] for s in seeds]
    if len(diffs) < 2:
        return None
    return {"diff": st.mean(diffs), "two_se": 2 * st.stdev(diffs) / math.sqrt(len(diffs)), "n_labs": len(diffs)}


def call_stats(by_seed):
    """How often a model call fell back, kept the old memory, or gave a short plan (per method)."""
    n = fb = kept = short = fc = 0
    for r in by_seed.values():
        for d in r["days"]:
            for key in ("forecast_info", "evening_info"):
                i = d.get(key) or {}
                if i:
                    n += 1
                    fb += bool(i.get("fallback_no_thinking"))
                    kept += bool(i.get("kept_old_memory"))
            for f in d["forecast"].values():
                fc += 1
                short += f.get("plan_given", 5) < 5
    return {"calls": n, "fallback_no_thinking": fb, "kept_old_memory": kept, "short_plans": short, "forecasts": fc}


def load_runs():
    runs = defaultdict(dict)
    for f in sorted((HERE / "runs").glob("*/seed_*.json")):
        r = json.loads(f.read_text())
        runs[f.parent.name][r["seed"]] = r
    return runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "results.json"))
    ap.add_argument("--min_days", type=int, default=W.N_DAYS)
    a = ap.parse_args()
    runs = load_runs()
    res = {}
    for name, by_seed in runs.items():
        rows = {s: per_lab(r) for s, r in by_seed.items() if len(r["days"]) >= a.min_days}
        if not rows:
            continue
        res[name] = {"n_labs": len(rows), "all": summarize(rows),
                     "period": {k: summarize(rows, lambda r, d=d: r["day"] in d) for k, d in PERIODS.items()},
                     "rule": {t: summarize(rows, lambda r, t=t: r["rule"] == t) for t in W.RULE_TYPES},
                     "rule_after_change": {t: summarize(rows, lambda r, t=t: r["rule"] == t and 16 <= r["day"] <= 20)
                                           for t in W.CHANGING},
                     "failed_forecasts": sum(r["failed_forecast"] for rr in rows.values() for r in rr),
                     "calls": call_stats(by_seed)}
    names = sorted(res, key=lambda n: -(res[n]["all"]["first_right"]["mean"] or 0))
    f3 = lambda v: f"{v:.3f}" if v is not None else "  -  "
    print(f"{'method':22s} labs  first  looks   in3   brier  outOK  outFalse  failed  calls")
    for n in names:
        x = res[n]["all"]
        print(f"{n:22s} {res[n]['n_labs']:4d}  {f3(x['first_right']['mean'])}  {x['looks']['mean']:.2f}  "
              f"{f3(x['found3']['mean'])} {f3(x['brier']['mean'])}  {f3(x['out_caught']['mean'])}  {f3(x['out_false']['mean'])}"
              f"  {res[n]['failed_forecasts']}  {res[n]['calls']}")
    pairs = [("hypotheses", "notes"), ("hypotheses", "full_log"), ("notes", "full_log"), ("full_log_think", "full_log"),
             ("hypotheses", "same_weekday"), ("notes", "same_weekday"), ("full_log", "same_weekday"),
             ("hypotheses", "no_memory"), ("same_weekday", "last_seen"), ("hypotheses", "hypotheses_rerun"),
             ("hypotheses_think", "notes_think"), ("hypotheses_think", "hypotheses"), ("notes_think", "notes"),
             ("hypotheses_think", "full_log_think")]
    print("\npaired differences over labs (A - B; counts if |diff| > 2 SE and > the rerun difference)")
    res["_paired"] = {}
    for a_, b_ in pairs:
        if a_ in res and b_ in res:
            for metric in ("first_right", "looks"):
                pd = paired(res[a_]["all"][metric], res[b_]["all"][metric])
                if pd:
                    res["_paired"][f"{a_}-{b_}:{metric}"] = pd
                    print(f"  {a_:15s} - {b_:15s} {metric:12s} {pd['diff']:+.3f}  (2 SE {pd['two_se']:.3f}, {pd['n_labs']} labs)")
            for per in PERIODS:
                pd = paired(res[a_]["period"][per]["first_right"], res[b_]["period"][per]["first_right"])
                if pd:
                    res["_paired"][f"{a_}-{b_}:first_right:{per}"] = pd
    Path(a.out).write_text(json.dumps(res, indent=1))
    print("\nfirst look right by period")
    print(f"{'method':22s} " + " ".join(f"{k:>18s}" for k in PERIODS))
    for n in names:
        print(f"{n:22s} " + " ".join(f"{(res[n]['period'][k]['first_right']['mean'] or 0):18.3f}" for k in PERIODS))
    print("\nfirst look right by rule")
    print(f"{'method':22s} " + " ".join(f"{t:>9s}" for t in W.RULE_TYPES))
    for n in names:
        print(f"{n:22s} " + " ".join(f"{(res[n]['rule'][t]['first_right']['mean'] or 0):9.3f}" for t in W.RULE_TYPES))
    return res


if __name__ == "__main__":
    main()
