"""Does GLOBAL (shared-state) grouping spread doubt or damage onto the resident whose routine did NOT change,
compared with the same method split --group person? Per-object learners (the timetable, most-frequent, last-seen)
keep separate records per object by construction, so they pass this by definition — this script is only for the
methods with genuinely shared state: the hedge (one household-wide weight vector), the conformal threshold (one
q_t), and the detector+reset (one martingale). Same 5 windows as uq_windows.py, UNAFFECTED group only, two metrics:
accuracy (does global grouping make the unaffected resident more often WRONG?) and confidence/set-size (does it make
them LESS SURE, even when the answer is unchanged?).

    python3 -m baselines.patrol.uq_shared_state --regimes sick10_partial,sick10_partial_s10_19 \
        --out ../results/confidence_shift_2026-09-20/uq/shared_state.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from baselines.patrol.uq_windows import WINDOW_ORDER, PAIRS, household_window_acc, stats

PAIRS_DEF = [
    ("hedge", "bma_hit", "bma_person", "prob"),
    ("conformal", "ocp_tt", "ocpperson_tt", "set"),
    ("reset", "mart_tt72", "detperson_tt72", "prob"),
]


def metric_series(hh_acc: dict, window: str, metric: str) -> list:
    vals = []
    for hh, d in hh_acc.items():
        n, ok, sum_conf, sum_set = d["unaffected"][window]
        if n == 0:
            continue
        vals.append(100 * sum_conf / n if metric == "prob" else sum_set / n)
    return vals


def accuracy_series(hh_acc: dict, window: str) -> list:
    vals = []
    for hh, d in hh_acc.items():
        n, ok = d["unaffected"][window][0], d["unaffected"][window][1]
        if n:
            vals.append(100 * ok / n)
    return vals


def paired_change(hh_acc: dict, window: str, ref: str, metric: str, is_acc: bool) -> dict:
    changes = []
    for hh, d in hh_acc.items():
        cw, cr = d["unaffected"][window], d["unaffected"][ref]
        if cw[0] == 0 or cr[0] == 0:
            continue
        if is_acc:
            vw, vr = 100 * cw[1] / cw[0], 100 * cr[1] / cr[0]
        else:
            idx = 2 if metric == "prob" else 3
            scale = 100 if metric == "prob" else 1
            vw, vr = scale * cw[idx] / cw[0], scale * cr[idx] / cr[0]
        changes.append(vw - vr)
    return stats(changes)


def analyze_pair(regimes: list, global_agent: str, person_agent: str, metric: str) -> dict:
    hh_g, hh_p = {}, {}
    for regime in regimes:
        hh_g.update(household_window_acc(regime, global_agent))
        hh_p.update(household_window_acc(regime, person_agent))
    out = {"windows": {}, "pairs": {}}
    for w in WINDOW_ORDER:
        out["windows"][w] = {
            "global_acc": stats(accuracy_series(hh_g, w)), "person_acc": stats(accuracy_series(hh_p, w)),
            "global_metric": stats(metric_series(hh_g, w, metric)), "person_metric": stats(metric_series(hh_p, w, metric)),
        }
    for w, ref in PAIRS:
        key = f"{w}_vs_{ref}"
        out["pairs"][key] = {
            "global_acc_change": paired_change(hh_g, w, ref, metric, True), "person_acc_change": paired_change(hh_p, w, ref, metric, True),
            "global_metric_change": paired_change(hh_g, w, ref, metric, False), "person_metric_change": paired_change(hh_p, w, ref, metric, False),
        }
    out["n_households"] = len(set(hh_g) | set(hh_p))
    out["metric"] = metric
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--regimes", required=True)
    ap.add_argument("--out", type=pathlib.Path, default=None)
    a = ap.parse_args(argv)
    regimes = a.regimes.split(",")

    result = {}
    for name, g, p, metric in PAIRS_DEF:
        r = analyze_pair(regimes, g, p, metric)
        result[name] = r
        mlabel = "confidence (top_prob, %)" if metric == "prob" else "set size (places)"
        print(f"\n== {name}: {g} (global) vs {p} (per-person) — unaffected resident, n={r['n_households']} hh ==", file=sys.stderr)
        for w in WINDOW_ORDER:
            d = r["windows"][w]
            print(f"  {w:13s} acc  global {d['global_acc']['mean']:5.1f}±{d['global_acc']['sd']:4.1f}  person {d['person_acc']['mean']:5.1f}±{d['person_acc']['sd']:4.1f}"
                  f"   |  {mlabel} global {d['global_metric']['mean']:5.1f}±{d['global_metric']['sd']:4.1f}  person {d['person_metric']['mean']:5.1f}±{d['person_metric']['sd']:4.1f}", file=sys.stderr)
        for key, p2 in r["pairs"].items():
            ga, pa = p2["global_acc_change"], p2["person_acc_change"]
            gm, pm = p2["global_metric_change"], p2["person_metric_change"]
            print(f"  {key}: acc change global {ga['mean']:+5.1f}±{ga['sd']:4.1f} vs person {pa['mean']:+5.1f}±{pa['sd']:4.1f}   |   "
                  f"{mlabel} change global {gm['mean']:+5.1f}±{gm['sd']:4.1f} vs person {pm['mean']:+5.1f}±{pm['sd']:4.1f}", file=sys.stderr)

    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(result, indent=1, sort_keys=True))
        print(f"\nwrote {a.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
