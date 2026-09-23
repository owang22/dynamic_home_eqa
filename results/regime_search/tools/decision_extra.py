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
import math
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


def tracks_correctness(rows_by_method):
    """Does a method's stated confidence predict whether it is actually right?

    Measured as the correlation between confidence and being correct, computed INSIDE each household and then
    averaged over them, per window. This is the mechanism under both the inversion and the value of declining:
    a rule that declines when confidence is low can only help if confidence still predicts correctness.

    Reported with the paired change from the settled weeks, because the claim is about what the shift DOES to
    a method rather than about which method knows itself best in general -- in the settled world they are
    about equal.
    """
    W = {"settled 1-13": range(1, 14), "first sick days 14-16": range(14, 17),
         "rest of spell 17-23": range(17, 24), "first days back 24-26": range(24, 27),
         "a week later 27-31": range(27, 32)}

    def corr(g):
        xs = [c for _, c, _ in g]
        ys = [1.0 if ok else 0.0 for _, _, ok in g]
        n = len(xs)
        if n < 10:
            return None
        mx, my = st.mean(xs), st.mean(ys)
        sx, sy = st.pstdev(xs), st.pstdev(ys)
        if sx == 0 or sy == 0:
            return None
        return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / (n * sx * sy)

    out = {}
    for mem, by_hh in rows_by_method.items():
        per_window, settled = {}, {}
        for hh, g in by_hh.items():
            settled[hh] = corr([x for x in g if x[0] in W["settled 1-13"]])
        for wname, days in W.items():
            vals, diffs = [], []
            for hh, g in by_hh.items():
                c = corr([x for x in g if x[0] in days])
                if c is None:
                    continue
                vals.append(c)
                if settled.get(hh) is not None:
                    diffs.append(c - settled[hh])
            if len(vals) < 2:
                continue
            se = st.stdev(vals) / math.sqrt(len(vals))
            row = {"r": round(st.mean(vals), 3), "se": round(se, 3), "n_hh": len(vals),
                   "differs_from_zero": abs(st.mean(vals)) >= 2 * se}
            if len(diffs) > 1 and wname != "settled 1-13":
                dse = st.stdev(diffs) / math.sqrt(len(diffs))
                row.update({"change_from_settled": round(st.mean(diffs), 3),
                            "change_se": round(dse, 3),
                            "change_clears": abs(st.mean(diffs)) >= 2 * dse})
            per_window[wname] = row
        out[mem] = per_window
    return out


def declining_decomposition(rows_by_method, shuffles=60, seed=5):
    """Split the value of being allowed to decline into the two things it can come from.

      level     what you get from the best ALL-OR-NOTHING choice -- answer everything, or decline everything.
                This needs no confidence signal at all: it pays whenever a method is wrong more often than
                right, because then declining beats answering.
      ordering  what the ORDER of the confidences adds on top of that. This is the only part that requires the
                confidence to carry information.
      null      the same ordering term computed on SHUFFLED labels. A threshold chosen with hindsight can
                always chase noise, so this is the floor: ordering at or below it is not a result.

    The threshold is chosen PER HOUSEHOLD here. That matters and is not the same estimator as the headline
    bars, which choose one threshold across all ten: one shared threshold has little freedom to chase noise,
    so its shuffled null sits near 0.01 and every bar clears it. The per-household estimator has real freedom,
    so its null is large and informative -- which is the whole point of drawing a floor.
    """
    import random
    rnd = random.Random(seed)
    out = {}
    for mem, by_hh in rows_by_method.items():
        per_window = {}
        for wname, days in WINDOWS.items():
            lv, od, acc = [], [], []
            for hh, seq in by_hh.items():
                sq = [x for x in seq if x[0] in days]
                if len(sq) < 20:
                    continue
                one = {hh: sq}
                forced = window_score(one, -1.0, days)
                level = max(forced, 0.0)
                best = max(window_score(one, b, days) or -99 for b in candidate_bars(one))
                lv.append(level - forced)
                od.append(best - level)
                acc.append(100.0 * st.mean([1 if ok else 0 for _, _, ok in sq]))
            if len(lv) < 2:
                continue
            nulls = []
            for _ in range(shuffles):
                v = []
                for hh, seq in by_hh.items():
                    sq = [x for x in seq if x[0] in days]
                    if len(sq) < 20:
                        continue
                    oks = [ok for _, _, ok in sq]
                    rnd.shuffle(oks)
                    sq = [(d, c, o) for (d, c, _), o in zip(sq, oks)]
                    one = {hh: sq}
                    level = max(window_score(one, -1.0, days), 0.0)
                    v.append(max(window_score(one, b, days) or -99 for b in candidate_bars(one)) - level)
                nulls.append(st.mean(v))
            ordering, null = st.mean(od), st.mean(nulls)
            se = st.stdev(od) / math.sqrt(len(od))
            per_window[wname] = {
                "accuracy": round(st.mean(acc), 1), "level": round(st.mean(lv), 2),
                "ordering": round(ordering, 2), "ordering_se": round(se, 2),
                "null_ordering": round(null, 2), "excess": round(ordering - null, 2),
                "beats_noise": ordering - null >= 2 * se,
                "n_hh": len(od)}
        out[mem] = per_window
    return out


def main():
    rows = load_rows()
    if not rows:
        print("no decision rows found")
        return 1
    out = {"windows_order": list(WINDOWS), "methods": {},
           "declining_decomposition": declining_decomposition(
               {m: {hh: list(seq) for hh, seq in by.items()} for m, by in rows.items()}),
           "confidence_tracks_correctness": tracks_correctness(
               {m: {hh: [(d, c, ok) for d, c, ok in seq] for hh, seq in by.items()}
                for m, by in rows.items()})}
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
