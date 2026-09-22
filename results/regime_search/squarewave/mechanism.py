#!/usr/bin/env python3
"""Does the sick routine occupy time-of-day slots the healthy routine never used?

Modelled on tools/break_cells.py: from LEAD-STAGE SIGHTINGS ONLY (patrol room contents + found-it observations
before day 14 - exactly the evidence the timetable has indexed by then), mark each question as
  "new slot"    = that object had NO lead-up sighting in the question's 2 h time-of-day bin, so the timetable's
                  slot for it is empty and it must fall back to the object's overall most-frequent place;
  "unusual place" = the truth differs from that fallback.
Report the share of questions that are "new slot", per window, plus the 3-day and never-forgets timetable accuracy
inside and outside those slots. If the sick routine largely lands in empty slots, the two routines do not collide
in the index; if it lands in the SAME slots with different answers, they do.
"""
import collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, f"{ROOT}/tools")
from analyze import load  # noqa

MIN_N = 10
BIN_S = 2 * 3600
LEAD_END_DAY = 13
TT = {"3-day timetable": "TimetableLookup(bin=2h,days=all,hl=72h)",
      "never-forgets timetable": "TimetableLookup(bin=2h,days=all)"}
WINDOWS = {"lead-up 9-13": range(9, 14), "sick opening 14-16": range(14, 17), "sick all 14-23": range(14, 24),
           "return 24-26": range(24, 27), "late return 27-31": range(27, 32)}


def lead_index(bank_path):
    bins, places = collections.Counter(), collections.defaultdict(collections.Counter)
    cutoff = (LEAD_END_DAY + 1) * 86400
    for l in open(bank_path):
        r = json.loads(l)
        k, t = r.get("kind"), r.get("t")
        if t is None or t >= cutoff:
            continue
        if k == "room_visit":
            for rec, objs in (r.get("contents") or {}).items():
                for o in objs:
                    bins[(o, (t % 86400) // BIN_S)] += 1
                    places[o][rec] += 1
        elif k == "observation":
            bins[(r["object_id"], (t % 86400) // BIN_S)] += 1
            places[r["object_id"]][r["receptacle_id"]] += 1
    return bins, {o: c.most_common(1)[0][0] for o, c in places.items()}


def sightings(bank_path, days):
    """(object, 2h bin) of every sighting whose day is in `days`."""
    out = []
    for l in open(bank_path):
        r = json.loads(l)
        t = r.get("t")
        if t is None or (t // 86400) not in days:
            continue
        if r.get("kind") == "room_visit":
            for rec, objs in (r.get("contents") or {}).items():
                for o in objs:
                    out.append((o, (t % 86400) // BIN_S))
        elif r.get("kind") == "observation":
            out.append((r["object_id"], (t % 86400) // BIN_S))
    return out


def contamination(regime, label, nhh):
    """The other side of the same coin: of the evidence the SICK spell writes into the index, how much lands in
    slots the healthy routine also uses (and so can outvote / be outvoted on the return)?"""
    sick_in_lead_slot = sick_tot = 0
    ret_q_touched = ret_q = 0
    for s in range(10):
        bp = f"{ROOT}/{regime}/banks/hh_s{s}_{label}.jsonl"
        if not os.path.exists(bp):
            continue
        lead_bins = {k for k, v in lead_index(bp)[0].items() if v}
        sick_bins = collections.Counter(sightings(bp, set(range(14, 24))))
        for k, v in sick_bins.items():
            sick_tot += v
            if k in lead_bins:
                sick_in_lead_slot += v
        _, qs = load(bp, 2)
        tq = {}
        for l in open(bp):
            if '"question"' in l:
                r = json.loads(l)
                if r.get("kind") == "question":
                    tq[r["question_id"]] = r["t_query"]
        for qid, q in qs.items():
            if 27 <= q["day"] <= 31:
                ret_q += 1
                if (q["obj"], (tq[qid] % 86400) // BIN_S) in sick_bins:
                    ret_q_touched += 1
    print(f"\ncontamination of the healthy index by the sick spell ({nhh} households, {regime}):")
    print(f"  sick-spell sightings filed into a slot the lead-up also used: {sick_in_lead_slot}/{sick_tot} = "
          f"{100 * sick_in_lead_slot / sick_tot:.0f}%  (the rest land in slots the healthy routine never queries)")
    print(f"  late-return questions (days 27-31) whose own (object, slot) cell holds sick-spell evidence: "
          f"{ret_q_touched}/{ret_q} = {100 * ret_q_touched / ret_q:.0f}%")


def main(regime="sick10_owner", label="t03"):
    # window -> (new_slot, unusual) -> [n, ok_tt3d, ok_ttfrozen]
    cell = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))
    nhh = 0
    for s in range(10):
        bp, cp = f"{ROOT}/{regime}/banks/hh_s{s}_{label}.jsonl", f"{ROOT}/{regime}/classical/hh_s{s}_{label}.jsonl"
        if not (os.path.exists(bp) and os.path.exists(cp)):
            continue
        nhh += 1
        _, qs = load(bp, 2)
        bins, usual = lead_index(bp)
        tq = {}
        for l in open(bp):
            if '"question"' in l:
                r = json.loads(l)
                if r.get("kind") == "question":
                    tq[r["question_id"]] = r["t_query"]
        ok = collections.defaultdict(dict)   # qid -> belief -> correct
        for l in open(cp):
            r = json.loads(l)
            if r["belief"] in TT.values():
                ok[r["question_id"]][r["belief"]] = int(r["correct"])
        for qid, q in qs.items():
            if TT["3-day timetable"] not in ok.get(qid, {}):
                continue
            b = (tq[qid] % 86400) // BIN_S
            key = (bins[(q["obj"], b)] == 0, q["truth"] != usual.get(q["obj"]))
            for w, days in WINDOWS.items():
                if q["day"] in days:
                    c = cell[w][key]
                    c[0] += 1
                    c[1] += ok[qid][TT["3-day timetable"]]
                    c[2] += ok[qid].get(TT["never-forgets timetable"], 0)
    print(f"=== {regime}: {nhh} households, {'MIN_N'} = {MIN_N} ===")
    print("share of questions whose 2 h time-of-day slot had NO lead-up sighting of that object ('new slot'),")
    print("and, inside that, the share where the fallback (overall most-frequent lead-up place) is also wrong.\n")
    print(f"{'window':20s} {'n':>5s} {'new slot':>9s} {'new slot &':>11s} {'old slot &':>11s} "
          f"{'tt3d new':>9s} {'tt3d old':>9s} {'ttfrz new':>10s} {'ttfrz old':>10s}")
    print(f"{'':20s} {'':>5s} {'share':>9s} {'unusual':>11s} {'unusual':>11s} {'acc':>9s} {'acc':>9s} {'acc':>10s} {'acc':>10s}")
    for w in WINDOWS:
        tot = sum(cell[w][k][0] for k in cell[w])
        if tot < MIN_N:
            print(f"{w:20s} {tot:5d}   UNUSABLE (fewer than {MIN_N} answers)")
            continue
        new = sum(cell[w][k][0] for k in cell[w] if k[0])
        newun = cell[w][(True, True)][0]
        oldun = cell[w][(False, True)][0]
        def acc(pred, col):
            n = sum(cell[w][k][0] for k in cell[w] if pred(k))
            o = sum(cell[w][k][col] for k in cell[w] if pred(k))
            return f"{100 * o / n:.0f}% ({n})" if n >= MIN_N else "unusable"
        print(f"{w:20s} {tot:5d} {100 * new / tot:8.0f}% {100 * newun / tot:10.0f}% {100 * oldun / tot:10.0f}% "
              f"{acc(lambda k: k[0], 1):>9s} {acc(lambda k: not k[0], 1):>9s} "
              f"{acc(lambda k: k[0], 2):>10s} {acc(lambda k: not k[0], 2):>10s}")
    contamination(regime, label, nhh)
    print("\nreading: 'new slot share' is the share of that window's questions landing in a time-of-day slot the")
    print("healthy routine never filled for that object. 'new slot & unusual' is the expensive corner: empty slot")
    print("AND the whole-history fallback is wrong - the only cell where the two routines really collide.")


if __name__ == "__main__":
    main(*(sys.argv[1:] or ["sick10_owner"]))
