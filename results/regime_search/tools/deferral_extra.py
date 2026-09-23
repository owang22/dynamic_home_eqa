#!/usr/bin/env python3
"""Can the robot tell when to hand a question over? -> story_extra.json["deferral_live"].

Two things the page needs and nothing else computes, both PER DAY rather than per five-day window, because the
claim is about the moment the routine changes and a window averages that moment away.

1. **The deferral gate.** The robot answers only when its own stated confidence clears a bar it adjusts after
   every question as the resident's corrections come in, aiming to be wrong at most one time in ten on the
   answers it keeps (adaptive conformal control, the same AskGate the arms already use). Per day: the share of
   questions it hands over, and the share it still gets wrong among those it answered. Computed for the
   language memories AND for the 3-day timetable, whose confidence is the top probability of its own
   distribution - the counter had no gate before, so the comparison the page makes had only one family in it.

2. **Within-arm discrimination.** Split each arm's questions at its OWN median confidence in each window and
   compare accuracy above against at-or-below. This separates two competences that "is it calibrated?" scores as
   one: whether the number RANKS its answers, and whether its LEVEL moves when the world changes.

Owns only ``deferral_live``. It does not read or write ``llm_live`` / ``knowno_live``; the ownership guard in
extra_store.py refuses anything else.

    python3 tools/deferral_extra.py     (from results/regime_search)
"""
import collections
import glob
import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load                                    # noqa: E402
from extra_store import write_keys                          # noqa: E402
from llm_live_extra import ARM_RE, AskGate, arm_answers, run_askgate  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FM = "/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/banks_f1"
LLM_DIR = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq", "llm_strategies")
# The no-message person arms live in two places, exactly as llm_live_extra's SOURCES has it: this session's chain
# (retrieval / long-context / reflection / nightly summary) and the workshop session's run1 (buffer, routine table).
# Both use the same banks - verified byte-identical between fm_memory/banks_f1 and sick10_owner/banks.
ARM_DIRS = [os.path.join(LLM_DIR, "chain_person", "nottold"),
            "/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/run1"]
CLASSICAL = os.path.join(ROOT, "sick10_owner", "classical")
BANKS = os.path.join(ROOT, "sick10_owner", "banks")
LABEL = "t03"
MIN_N = 10
ALPHA = 0.10
# One representative per counter family, so the figure is not all timetables. Checked before plotting: neither of
# the added two is saturated the way the language memories are - never-forgets has 255 distinct confidence values
# in the settled week with 2% at its mode, Perpetua* 378 with 1%, against 8-9 values and ~50% at the mode for the
# language memories. A line that cannot move belongs in a caption, not on a chart.
CLASSICAL_BELIEFS = {
    "TimetableLookup(bin=2h,days=all,hl=72h)": "tt3d",
    "TimetableLookup(bin=2h,days=all)": "ttfrozen",
    "PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)": "perpetua",
}
TT3D = "TimetableLookup(bin=2h,days=all,hl=72h)"
NAME = {"naive": "recency buffer", "retrieval": "retrieval", "reflect": "reflection",
        "routine7": "nightly routine table", "summary": "nightly summary", "longcontext": "long-context",
        "tt3d": "3-day timetable", "ttfrozen": "never-forgets timetable", "perpetua": "Perpetua*"}
WINDOWS = {"lead": range(9, 14), "d14_16": range(14, 17), "d17_23": range(17, 24),
           "d24_26": range(24, 27), "d27_31": range(27, 32)}


# Which households each memory's rows came from. The rows themselves are (t_query, day, confidence, correct)
# and carry no household, so the count has to be recorded as they are loaded -- and it has to exist, because
# without it the figures reached for `n`, the QUESTION count, and published "4130 households".
HH_SEEN = collections.defaultdict(set)


def llm_rows():
    """-> {memory: [(t_query, day, confidence, correct), ...]} pooled over households, no-message arms."""
    out = collections.defaultdict(list)
    seen = set()
    for base in ARM_DIRS:
      for d in sorted(glob.glob(os.path.join(base, f"hh_s*_{LABEL}_*_nottold_lookoff"))):
          m = ARM_RE.match(os.path.basename(d))
          if not m:
              continue
          hh, label, mem, _told, _look = m.groups()
          if (hh, mem) in seen:
              continue
          seen.add((hh, mem))
          HH_SEEN[mem].add(hh)
          bp = f"{FM}/{hh}_{label}.jsonl"
          if not os.path.exists(bp):
              continue
          h, qs = load(bp, 2)
          tq = {}
          for line in open(bp):
              if '"question"' in line:
                  r = json.loads(line)
                  if r.get("kind") == "question":
                      tq[r["question_id"]] = r["t_query"]
          for qid, (loc, conf) in arm_answers(d).items():
              q = qs.get(qid)
              if not q or loc is None:
                  continue
              out[mem].append((tq.get(qid, 0), q["day"], float(conf or 0.0), int(loc == q["truth"])))
    return out


def classical_rows():
    """Each counter's own confidence: the top probability of its distribution, same as everywhere else."""
    out = collections.defaultdict(list)
    for cp in sorted(glob.glob(os.path.join(CLASSICAL, f"hh_s*_{LABEL}.jsonl"))):
        hh = os.path.basename(cp).split("_" + LABEL)[0]
        for line in open(cp):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            key = CLASSICAL_BELIEFS.get(r.get("belief"))
            if not key:
                continue
            HH_SEEN[key].add(hh)
            out[key].append((r.get("t_query", 0), r["day_index"], float(r.get("top_prob") or 0.0),
                             int(bool(r["correct"]))))
    return dict(out)


def per_day_gate(rows, alpha=ALPHA):
    """Run the gate once over the whole chronological stream, then report per day."""
    rows = sorted(rows)
    gate = AskGate(alpha=alpha)
    per = collections.defaultdict(lambda: [0, 0, 0])   # day -> [n, n_answered, n_missed]
    for _t, day, conf, ok in rows:
        answered, missed = gate.update(conf, bool(ok))
        c = per[day]
        c[0] += 1
        c[1] += int(answered)
        c[2] += int(answered and missed)
    out = {}
    for day, (n, na, nm) in sorted(per.items()):
        if n < MIN_N:
            continue
        out[str(day)] = {"n": n, "hand_over": round(100 * (n - na) / n, 1),
                         "wrong_when_answered": round(100 * nm / na, 1) if na else None}
    return out


def discrimination(rows):
    """Accuracy above vs at-or-below the arm's OWN median confidence, per window."""
    out = {}
    for w, days in WINDOWS.items():
        g = [r for r in rows if r[1] in days]
        if len(g) < 40:
            out[w] = None
            continue
        med = st.median([r[2] for r in g])
        hi = [r for r in g if r[2] > med]
        lo = [r for r in g if r[2] <= med]
        if not hi or not lo:
            out[w] = {"n": len(g), "saturated": True, "median": round(med, 3),
                      "n_above": len(hi), "gap": None}
            continue
        a = lambda G: 100 * sum(r[3] for r in G) / len(G)   # noqa: E731
        out[w] = {"n": len(g), "saturated": False, "median": round(med, 3), "n_above": len(hi),
                  "acc_above": round(a(hi), 1), "acc_below": round(a(lo), 1), "gap": round(a(hi) - a(lo), 1)}
    return out



def hindsight(rows, ask_rate):
    """The best a SINGLE FIXED bar could do on this window, chosen knowing the answers - an upper bound nobody
    can reach in deployment. Answer the most-confident (1 - ask_rate) of the questions and count the misses.

    Where the confidence is saturated the sort cannot separate the tied questions, so this lands on the base error
    rate: that is the honest verdict, not a failure of the calculation. A scalar with no spread admits no bar,
    with hindsight or without it.
    """
    n = len(rows)
    n_ans = int(round(n * (1.0 - ask_rate / 100.0)))
    if n_ans < 5:
        return None
    ranked = sorted(rows, key=lambda r: -r[2])
    kept = ranked[:n_ans]
    ties = sum(1 for r in rows if r[2] == kept[-1][2])
    return {"miss": round(100 * (1 - sum(r[3] for r in kept) / n_ans), 1),
            "n_answered": n_ans, "bar": round(kept[-1][2], 3),
            "tied_at_bar": ties, "separable": ties < max(3, 0.25 * n)}


def decomposition(rows, per_day):
    """Per window: what the causal adaptive bar achieved, what one fixed bar could have achieved at the SAME ask
    rate with hindsight, and the gap between them - the cost of not knowing where the level has moved to."""
    out = {}
    for w, days in WINDOWS.items():
        g = [r for r in rows if r[1] in days]
        if len(g) < 40:
            out[w] = None
            continue
        ds = [per_day[str(d)] for d in days if str(d) in per_day]
        if not ds:
            out[w] = None
            continue
        ask = st.mean(x["hand_over"] for x in ds)
        miss = [x["wrong_when_answered"] for x in ds if x["wrong_when_answered"] is not None]
        achieved = st.mean(miss) if miss else None
        hs = hindsight(g, ask)
        out[w] = {"n": len(g), "ask_rate": round(ask, 1),
                  "miss_achieved": round(achieved, 1) if achieved is not None else None,
                  "miss_hindsight": hs["miss"] if hs else None,
                  "gap": round(achieved - hs["miss"], 1) if (hs and achieved is not None) else None,
                  "bar": hs["bar"] if hs else None,
                  "separable": hs["separable"] if hs else None,
                  "tied_at_bar": hs["tied_at_bar"] if hs else None}
    return out



def mass_below_bar(rows):
    """Per day: the share of answers falling below a bar FIXED at this method's settled lead-up median.

    The mean of a bounded confidence is the wrong summary and it misled us: the buffer's mean moved one point
    (88% to 87%) while twelve points of mass crossed a threshold, and retrieval's moved 2.6 while twenty-nine
    points crossed a bar at 0.95. What a deferral decision actually depends on is how much mass sits on the far
    side of the bar, so that is what this reports. Two bars per method - its settled median and its settled lower
    quartile - because these confidences are quantised into about nine values and whether the distribution
    "moves" depends entirely on which of those values the bar sits between.
    """
    lead = [v for _t, d, v, _ok in rows if d in WINDOWS["lead"]]
    if len(lead) < 40:
        return None
    med = st.median(lead)
    q1 = sorted(lead)[len(lead) // 4]
    per = collections.defaultdict(lambda: [0, 0, 0])
    for _t, d, v, _ok in rows:
        c = per[d]
        c[0] += 1
        c[1] += int(v < med)
        c[2] += int(v < q1)
    out = {"bar_median": round(med, 4), "bar_q1": round(q1, 4), "per_day": {}}
    for d, (n, bm, bq) in sorted(per.items()):
        if n < MIN_N:
            continue
        out["per_day"][str(d)] = {"n": n, "below_median_bar": round(100 * bm / n, 1),
                                  "below_q1_bar": round(100 * bq / n, 1)}
    return out


def value_spread(rows):
    """How much resolution the confidence actually has: a bar can only sit between the values that occur."""
    lead = [v for _t, d, v, _ok in rows if d in WINDOWS["lead"]]
    if len(lead) < 40:
        return None
    c = collections.Counter(round(v, 3) for v in lead)
    top, n_top = c.most_common(1)[0]
    return {"n": len(lead), "distinct_values": len(c), "mode": top,
            "share_at_mode": round(100 * n_top / len(lead), 1), "median": round(st.median(lead), 3)}



def answered_vs_handed(rows):
    """Accuracy of what the gate ANSWERS against what it HANDS OVER, per window.

    The sign of this difference is what the confidence is worth. Positive means the robot is keeping the questions
    it is better at, which is the whole point of a gate. Negative means it is keeping the ones it is WORSE at -
    the confidence is not merely uninformative, it points the wrong way, and the robot would do better answering
    the questions it just refused.
    """
    gate = AskGate(alpha=ALPHA)
    dec = []
    for _t, day, conf, ok in sorted(rows):
        answered, _ = gate.update(conf, bool(ok))
        dec.append((day, bool(answered), ok))
    out = {}
    for w, days in WINDOWS.items():
        g = [d for d in dec if d[0] in days]
        A = [d for d in g if d[1]]
        H = [d for d in g if not d[1]]
        if len(g) < 40 or len(A) < MIN_N or len(H) < MIN_N:
            out[w] = None
            continue
        aA = 100 * sum(d[2] for d in A) / len(A)
        aH = 100 * sum(d[2] for d in H) / len(H)
        out[w] = {"n": len(g), "answered_acc": round(aA, 1), "handed_acc": round(aH, 1),
                  "n_answered": len(A), "n_handed": len(H), "edge": round(aA - aH, 1),
                  "inverted": bool(aA < aH)}
    return out



def edge_by_household(mem):
    """The answered-minus-handed-over edge computed INSIDE each household, so a pooled figure cannot be carried
    by one or two large ones. Returns mean, sd, se, and how many households keep the sign - the check that
    separates a result from an optimistic sample."""
    if mem not in CLASSICAL_BELIEFS.values():
        return None
    belief = [b for b, k in CLASSICAL_BELIEFS.items() if k == mem][0]
    per = collections.defaultdict(list)
    for cp in sorted(glob.glob(os.path.join(CLASSICAL, f"hh_s*_{LABEL}.jsonl"))):
        hh = os.path.basename(cp).split("_" + LABEL)[0]
        for line in open(cp):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("belief") == belief:
                per[hh].append((r.get("t_query", 0), r["day_index"], float(r.get("top_prob") or 0.0),
                                int(bool(r["correct"]))))
    out = {}
    for w, days in WINDOWS.items():
        edges = []
        for hh, rows in sorted(per.items()):
            gate = AskGate(alpha=ALPHA)
            dec = []
            for _t, d, c, ok in sorted(rows):
                a, _ = gate.update(c, bool(ok))
                dec.append((d, bool(a), ok))
            sel = [x for x in dec if x[0] in days]
            A = [x for x in sel if x[1]]
            H = [x for x in sel if not x[1]]
            if len(A) < 5 or len(H) < 5:
                continue
            edges.append(100 * sum(x[2] for x in A) / len(A) - 100 * sum(x[2] for x in H) / len(H))
        if len(edges) < 3:
            out[w] = None
            continue
        m = st.mean(edges)
        sd = st.stdev(edges)
        out[w] = {"n_hh": len(edges), "mean": round(m, 1), "sd": round(sd, 1),
                  "se": round(sd / len(edges) ** 0.5, 1),
                  "kept_sign": sum(1 for e in edges if e > 0),
                  "per_hh": [round(e) for e in sorted(edges)]}
    return out


def main():
    src = llm_rows()
    src.update(classical_rows())
    out, lines = {}, []
    for mem, rows in sorted(src.items()):
        if len(rows) < 100:
            continue
        out[mem] = {"name": NAME.get(mem, mem), "n": len(rows), "n_hh": len(HH_SEEN.get(mem, ())),
                    "classical": mem in CLASSICAL_BELIEFS.values(),
                    "per_day": per_day_gate(rows), "discrimination": discrimination(rows)}
        out[mem]["decomposition"] = decomposition(rows, out[mem]["per_day"])
        out[mem]["mass_below_bar"] = mass_below_bar(rows)
        out[mem]["value_spread"] = value_spread(rows)
        out[mem]["answered_vs_handed"] = answered_vs_handed(rows)
        eh = edge_by_household(mem)
        if eh:
            out[mem]["edge_by_household"] = eh
        d = out[mem]["discrimination"].get("d14_16") or {}
        pd = out[mem]["per_day"]
        shift = [pd[str(x)] for x in (14, 15, 16) if str(x) in pd]
        ho = st.mean([x["hand_over"] for x in shift]) if shift else float("nan")
        wr = st.mean([x["wrong_when_answered"] for x in shift if x["wrong_when_answered"] is not None]) if shift else float("nan")
        dec = (out[mem]["decomposition"] or {}).get("d14_16") or {}
        hs = dec.get("miss_hindsight")
        tail = (f" | best fixed bar with hindsight {hs:4.0f}%  (gap {dec.get('gap'):+.0f})" if hs is not None
                else " | no bar exists")
        if dec.get("separable") is False:
            tail += "  [confidence too tied to separate]"
        lines.append(f"  {NAME.get(mem, mem):26s} 14-16: hands over {ho:4.0f}%, wrong on {wr:4.0f}%" + tail)
    print("deferral gate, per day, alpha=0.10 (target: wrong at most 1 in 10 of what it answers)")
    print("\n".join(lines))
    print(write_keys("deferral_extra", {"deferral_live": {"alpha": ALPHA, "min_n": MIN_N, "memories": out}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
