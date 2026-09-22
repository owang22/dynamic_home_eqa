#!/usr/bin/env python3
"""Why a disruption breaks a time-of-day learner: the 2x2 that separates "new hour" novelty from "unusual place"
novelty, on the same windows, for several regimes.

For every spell question, from LEAD-STAGE SIGHTINGS ONLY (patrol contents + found-it observations before day 14 —
the same evidence the timetable has, not the questions):
  hour seen  = that object had at least one lead-stage sighting in the question's 2 h bin (so the bin is not empty)
  usual place = the truth equals that object's most frequent lead-stage place overall (the whole-history
                most-frequent answer, which is exactly what TimetableLookup falls back to when the bin IS empty)
Each cell reports its share of the window's questions and the 3-day timetable's accuracy inside it, so the break can
be attributed: an empty bin whose fallback is right costs nothing ("new hour, usual place"), an empty bin whose
fallback is wrong is the expensive cell ("new hour, unusual place").

    python3 tools/break_cells.py sick10_owner guests10 vacation   (run from results/regime_search)
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
LEAD_END_DAY = 13
WINDOWS = {"lead 9-13": range(9, 14), "14-16": range(14, 17), "rest of spell": range(17, 24), "24-26": range(24, 27)}
TT3D = "TimetableLookup(bin=2h,days=all,hl=72h)"
CELLS = [(True, True), (True, False), (False, True), (False, False)]
CELL_NAME = {(True, True): "hour seen · usual place", (True, False): "hour seen · UNUSUAL place",
             (False, True): "new hour · usual place", (False, False): "new hour · UNUSUAL place"}


def lead_sightings(bank_path):
    """-> (bins: {(obj, bin): count}, usual: {obj: most frequent lead-stage place}) from lead-stage sightings only."""
    bins = collections.Counter()
    places = collections.defaultdict(collections.Counter)
    cutoff = (LEAD_END_DAY + 1) * 86400
    for l in open(bank_path):
        r = json.loads(l)
        k = r.get("kind")
        if k == "room_visit" and r["t"] < cutoff:
            for rec, objs in (r.get("contents") or {}).items():
                for o in objs:
                    bins[(o, (r["t"] % 86400) // BIN_S)] += 1
                    places[o][rec] += 1
        elif k == "observation" and r["t"] < cutoff:
            bins[(r["object_id"], (r["t"] % 86400) // BIN_S)] += 1
            places[r["object_id"]][r["receptacle_id"]] += 1
    usual = {o: c.most_common(1)[0][0] for o, c in places.items()}
    return bins, usual


def report(regime, label="t03"):
    cell = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))   # window -> cell -> n, ok
    lead_acc = [0, 0]
    hh_done = 0
    for s in range(10):
        bp = f"{ROOT}/{regime}/banks/hh_s{s}_{label}.jsonl"
        cp = f"{ROOT}/{regime}/classical/hh_s{s}_{label}.jsonl"
        if not (os.path.exists(bp) and os.path.exists(cp)):
            continue
        hh_done += 1
        h, qs = load(bp, 2)
        bins, usual = lead_sightings(bp)
        tq = {}
        for l in open(bp):
            if '"question"' in l:
                r = json.loads(l)
                if r.get("kind") == "question":
                    tq[r["question_id"]] = r["t_query"]
        for r in (json.loads(l) for l in open(cp)):
            if r["belief"] != TT3D:
                continue
            q = qs[r["question_id"]]
            d = q["day"]
            if 9 <= d <= LEAD_END_DAY:
                lead_acc[0] += 1
                lead_acc[1] += int(r["correct"])
            b = (tq[r["question_id"]] % 86400) // BIN_S
            key = (bins[(q["obj"], b)] > 0, q["truth"] == usual.get(q["obj"]))
            for w, days in WINDOWS.items():
                if d in days:
                    c = cell[w][key]
                    c[0] += 1
                    c[1] += int(r["correct"])
    lead = 100 * lead_acc[1] / lead_acc[0] if lead_acc[0] else float("nan")
    print(f"\n=== {regime}: {hh_done}/10 households; 3-day timetable, settled lead-up (days 9-13) = {lead:.0f}% ===")
    print(f"{'window':16s} " + "  ".join(f"{CELL_NAME[c]:>26s}" for c in CELLS) + "     window acc / break")
    print(f"{'':16s} " + "  ".join(f"{'share · accuracy':>26s}" for _ in CELLS))
    for w in WINDOWS:
        tot = sum(cell[w][c][0] for c in CELLS)
        if not tot:
            continue
        cells = []
        for c in CELLS:
            n, ok = cell[w][c]
            cells.append(f"{100 * n / tot:3.0f}% · {(f'{100 * ok / n:.0f}%' if n >= MIN_N else '-'):>4s}".rjust(26))
        wacc = 100 * sum(cell[w][c][1] for c in CELLS) / tot
        print(f"{w:16s} " + "  ".join(cells) + f"     {wacc:.0f}% / {lead - wacc:+.0f}")
    # decomposition of each window's break against the lead window: how much comes from questions MOVING into
    # harder cells (mix) vs from the SAME cells getting harder (within)
    L = cell["lead 9-13"]; ltot = sum(L[c][0] for c in CELLS)
    if ltot:
        lsh = {c: L[c][0] / ltot for c in CELLS}
        lac = {c: (L[c][1] / L[c][0] if L[c][0] else 0.0) for c in CELLS}
        print(f"{'':16s} break decomposition vs the lead window (percentage points):")
        for w in WINDOWS:
            if w == "lead 9-13":
                continue
            S = cell[w]; tot = sum(S[c][0] for c in CELLS)
            if not tot:
                continue
            ssh = {c: S[c][0] / tot for c in CELLS}
            sac = {c: (S[c][1] / S[c][0] if S[c][0] else 0.0) for c in CELLS}
            mix = 100 * sum((lsh[c] - ssh[c]) * lac[c] for c in CELLS)
            within = 100 * sum(ssh[c] * (lac[c] - sac[c]) for c in CELLS)
            worst = 100 * (ssh[(False, False)] - lsh[(False, False)])
            unusual = 100 * ((ssh[(True, False)] + ssh[(False, False)]) - (lsh[(True, False)] + lsh[(False, False)]))
            newhour = 100 * ((ssh[(False, True)] + ssh[(False, False)]) - (lsh[(False, True)] + lsh[(False, False)]))
            print(f"{'  ' + w:16s} total {mix + within:+5.0f}  = mix {mix:+5.0f} + within-cell {within:+5.0f}"
                  f"   | share shift: unusual place {unusual:+4.0f}, new hour {newhour:+4.0f}, both {worst:+4.0f}")


def main():
    for regime in sys.argv[1:] or ["sick10_owner"]:
        report(regime)


if __name__ == "__main__":
    main()
