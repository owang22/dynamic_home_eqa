#!/usr/bin/env python3
"""Decision score: +1 for a right answer, -1 for a wrong one, 0 for declining to answer.

    python3 tools/decision_extra.py            (from results/regime_search)

Writes ONE key, ``decision_live``, through extra_store, so the page and the paper figures share this
computation instead of each carrying its own copy. Grown out of tools/decision_score.py, which stays as the
quick-look script it was; this is the version the artifacts read.

Why this scoring is worth a figure: it needs no promise and no coverage target to explain, and with +1/-1/0 the
decision-theoretically correct policy is to answer whenever you believe you are likelier right than wrong. The
half-way bar is therefore not an arbitrary choice -- it is what a calibrated confidence implies.

Two quantities come out.

``per_day``  the daily score at each method's OWN best fixed threshold. Methods must be allowed their own
             threshold or the comparison measures their confidence SCALES rather than their judgement: the
             timetables spread mass over dozens of places and rarely exceed 0.5, while long-context says 0.95
             to almost everything.

``windows``  the value of being ALLOWED TO DECLINE: the score under the best threshold for that window minus
             the score when forced to answer every question.

Both pick thresholds with hindsight, knowing the answers for the window being scored, so both are UPPER BOUNDS
on what any real policy could extract. That is stated on the figures, not just here, because it is what makes
the negative result strong: even handed the answers in advance, declining buys the counters almost nothing at
the moment it would matter.
"""
import collections
import glob
import json
import os
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extra_store import write_keys                                      # noqa: E402

CLS = os.path.join(ROOT, "sick10_owner", "classical")
LLM = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq", "llm_strategies",
                   "chain_person", "nottold")
WANT = {"TimetableLookup(bin=2h,days=all)": "ttfrozen",
        "TimetableLookup(bin=2h,days=all,hl=72h)": "tt3d",
        "PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)": "perpetua",
        "LastObservation": "lastseen"}
WINDOWS = {"settled week 9-13": range(9, 14), "first sick days 14-16": range(14, 17),
           "rest of the spell 17-23": range(17, 24), "first days back 24-26": range(24, 27),
           "a week later 27-31": range(27, 32)}
DAYS = 32


def load_rows():
    rows = collections.defaultdict(lambda: collections.defaultdict(list))   # method -> hh -> [(day, conf, ok)]
    for f in sorted(glob.glob(os.path.join(CLS, "hh_s*_t03.jsonl"))):
        hh = os.path.basename(f).split("_t03")[0]
        for line in open(f):
            r = json.loads(line)
            m = WANT.get(r["belief"])
            if m:
                rows[m][hh].append((r["day_index"], float(r["top_prob"]), bool(r["correct"])))
    for d in sorted(glob.glob(os.path.join(LLM, "hh_s*_longcontext_nottold_lookoff"))):
        hh = os.path.basename(d).split("_t03")[0]
        p = os.path.join(d, "run_log.jsonl")
        if not os.path.exists(p):
            continue
        for line in open(p):
            r = json.loads(line)
            c = r.get("raw_confidence")
            if c is not None:
                rows["longcontext"][hh].append((r["day_index"], float(c), bool(r["correct"])))
    return rows


def day_scores(seq, bar):
    """Daily score for one household: answer when confidence is ABOVE the bar, +1 right, -1 wrong, 0 declined."""
    per = collections.defaultdict(int)
    for day, conf, ok in seq:
        per[day] += 0 if conf <= bar else (1 if ok else -1)
    return per


def window_score(by_hh, bar, days):
    """Mean over households of the mean daily score inside the window."""
    vals = []
    for hh, seq in by_hh.items():
        per = day_scores(seq, bar)
        present = [d for d in days if d in per]
        if present:
            vals.append(sum(per[d] for d in present) / len(present))
    return st.mean(vals) if vals else None


def candidate_bars(by_hh):
    """A grid over the confidences the method actually produces, plus a bar below everything (= answer all)."""
    vals = sorted({round(c, 3) for seq in by_hh.values() for _, c, _ in seq})
    if not vals:
        return [-1.0]
    step = max(1, len(vals) // 60)
    return [-1.0] + vals[::step]


def main():
    rows = load_rows()
    if not rows:
        print("no decision rows found")
        return 1
    out = {"windows_order": list(WINDOWS), "methods": {}}
    print(f"{'method':14s} {'hh':>3} {'best bar':>9} | " + "  ".join(f"{w:>24s}" for w in WINDOWS))
    for m, by_hh in sorted(rows.items()):
        bars = candidate_bars(by_hh)
        allday = range(1, DAYS)
        best_all = max(bars, key=lambda b: (window_score(by_hh, b, allday) or -99))
        per_day = {}
        for d in range(1, DAYS):
            v = window_score(by_hh, best_all, [d])
            if v is not None:
                per_day[d] = round(v, 3)
        win = {}
        for wname, days in WINDOWS.items():
            forced = window_score(by_hh, -1.0, days)          # answer everything
            best_bar = max(bars, key=lambda b: (window_score(by_hh, b, days) or -99))
            best = window_score(by_hh, best_bar, days)
            if forced is None or best is None:
                continue
            win[wname] = {"best": round(best, 3), "forced": round(forced, 3),
                          "gain": round(best - forced, 3), "bar": round(best_bar, 3)}
        allrows = [x for seq in by_hh.values() for x in seq]
        out["methods"][m] = {
            "n_hh": len(by_hh), "best_bar_overall": round(best_all, 3), "per_day": per_day, "windows": win,
            "declined_at_best": round(100 * sum(1 for _, c, _ in allrows if c <= best_all) / len(allrows), 1),
            "accuracy": round(100 * sum(1 for _, _, ok in allrows if ok) / len(allrows), 1),
        }
        print(f"{m:14s} {len(by_hh):>3} {best_all:9.3f} | "
              + "  ".join(f"{win[w]['best']:+7.1f} (forced {win[w]['forced']:+5.1f})" if w in win else " " * 24
                          for w in WINDOWS))
    print(write_keys("decision_extra", {"decision_live": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
