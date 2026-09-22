#!/usr/bin/env python3
"""Window report for a regime's classical logs, with the ceiling beside the break.

Per window (lead 9-13 | 14-16 | 17-23 | 24-26 | 27-31): n answers, accuracy on all questions and on cold questions
(the first question about an object that day, before that day's feedback), and the CEILING — the share of that
window's questions whose truth differs from the settled lead-up answer for that (object, 2 h bin), and "no ref" —
the share that have NO lead-up answer at that hour at all, because the disruption also changed WHEN things are
asked. NOTE (04:35): neither column predicts the BREAK — see tools/break_cells.py, which shows the share of questions
where the object is somewhere other than where it usually lives is what tracks it. These two are kept as bounds only, so an 11-point break at a 35% ceiling and at a 70% ceiling mean
different things. Any window (or cold subset) with fewer than MIN_N answers prints "-" rather than a number, the
same rule the story page applies to thin in-progress days.

    python3 tools/guests_report.py guests10 guests10_eve guests10_morn   (run from results/regime_search)
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load  # noqa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_N = 10
BIN_S = 2 * 3600
WINDOWS = {"lead 9-13": range(9, 14), "14-16": range(14, 17), "17-23": range(17, 24),
           "24-26": range(24, 27), "27-31": range(27, 32)}
BELIEFS = {"LastObservation": "last seen", "TimetableLookup(bin=2h,days=all,hl=24h)": "timetable 1-day",
           "TimetableLookup(bin=2h,days=all,hl=72h)": "timetable 3-day", "TimetableLookup(bin=2h,days=all)": "never-forgets"}


def pct(num, den):
    return f"{100 * num / den:.0f}" if den >= MIN_N else "-"


def report(regime, label="t03"):
    acc = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0, 0]))  # method -> window -> n, ok, n_cold, ok_cold
    ceil = collections.defaultdict(lambda: [0, 0, 0])                                     # window -> n, n_novel, n_no_lead_reference
    per_day = collections.defaultdict(lambda: [0, 0])                                     # day -> n, ok (3-day timetable)
    nq = collections.Counter()
    hh_done = 0
    for s in range(10):
        bp = f"{ROOT}/{regime}/banks/hh_s{s}_{label}.jsonl"
        cp = f"{ROOT}/{regime}/classical/hh_s{s}_{label}.jsonl"
        if not (os.path.exists(bp) and os.path.exists(cp)):
            continue
        hh_done += 1
        h, qs = load(bp, 2)
        tq = {}
        for l in open(bp):
            if '"question"' in l:
                r = json.loads(l)
                if r.get("kind") == "question":
                    tq[r["question_id"]] = r["t_query"]
        modes = collections.defaultdict(collections.Counter)
        for qid, q in qs.items():
            if q["day"] <= 13:
                modes[(q["obj"], (tq[qid] % 86400) // BIN_S)][q["truth"]] += 1
        for qid, q in qs.items():
            stage = "lead" if q["day"] <= 13 else "spell" if q["day"] <= 23 else "return"
            nq[stage] += 1
            m = modes.get((q["obj"], (tq[qid] % 86400) // BIN_S))
            novel = int(m is not None and m.most_common(1)[0][0] != q["truth"])
            unseen = int(m is None)   # no lead-up answer exists for this object at this hour: the learner has nothing
            for w, days in WINDOWS.items():
                if q["day"] in days:
                    ceil[w][0] += 1
                    ceil[w][1] += novel
                    ceil[w][2] += unseen
        rows = [json.loads(l) for l in open(cp)]
        for name in BELIEFS.values():
            seen = set()
            for r in sorted([r for r in rows if BELIEFS.get(r["belief"]) == name], key=lambda r: tq[r["question_id"]]):
                q = qs[r["question_id"]]
                cold = (q["day"], q["obj"]) not in seen
                seen.add((q["day"], q["obj"]))
                if name == "timetable 3-day":
                    pd = per_day[q["day"]]
                    pd[0] += 1
                    pd[1] += int(r["correct"])
                for w, days in WINDOWS.items():
                    if q["day"] in days:
                        a = acc[name][w]
                        a[0] += 1
                        a[1] += int(r["correct"])
                        a[2] += cold
                        a[3] += cold and int(r["correct"])

    print(f"\n=== {regime}: {hh_done}/10 households scored; questions per stage {dict(nq)} ===")
    print(f"{'window':12s} {'n':>6s} {'ceiling':>8s} {'no ref':>7s}   " + "   ".join(f"{m:>16s}" for m in BELIEFS.values()))
    print(f"{'':12s} {'':>6s} {'differs':>8s} {'at that':>7s}   " + "   ".join(f"{'all / cold':>16s}" for _ in BELIEFS.values()))
    for w in WINDOWS:
        cells = "   ".join(f"{pct(acc[m][w][1], acc[m][w][0]) + ' / ' + pct(acc[m][w][3], acc[m][w][2]):>16s}" for m in BELIEFS.values())
        print(f"{w:12s} {ceil[w][0]:6d} {pct(ceil[w][1], ceil[w][0]) + '%':>8s} {pct(ceil[w][2], ceil[w][0]) + '%':>7s}   {cells}")
    print(f"{'break (lead -> 14-16)':21s}" + "  ".join(
        f"{m}: {(100 * acc[m]['lead 9-13'][1] / acc[m]['lead 9-13'][0] - 100 * acc[m]['14-16'][1] / acc[m]['14-16'][0]):+.0f} all / "
        f"{(100 * acc[m]['lead 9-13'][3] / acc[m]['lead 9-13'][2] - 100 * acc[m]['14-16'][3] / acc[m]['14-16'][2]):+.0f} cold"
        for m in BELIEFS.values() if acc[m]["lead 9-13"][0] >= MIN_N and acc[m]["14-16"][0] >= MIN_N))
    thin = [d for d in sorted(per_day) if per_day[d][0] < MIN_N]
    if thin:
        print(f"per-day points masked (fewer than {MIN_N} answers): days {thin} — window means above pool the days, "
              f"so they stay usable; do not read this regime day by day")


def main():
    for regime in sys.argv[1:] or ["guests10"]:
        report(regime)


if __name__ == "__main__":
    main()
