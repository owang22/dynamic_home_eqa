#!/usr/bin/env python3
"""Overnight driver check for the feedback protocol.

Tables: per-day accuracy / mean confidence split by whether the object moved since the 03:00 round, for every
agent that has logged anything (classical, naive calls.jsonl, mixture live.jsonl).
Red flags: mechanical (crash, stall, bad revisions) and statistical (the run has the wrong shape).
Story checks: what the GOAL demands, per household and pooled, PASS / FAIL / n.a. (not enough data yet).

Goal: the hypothesis mixture (told) loses confidence when the household's routine shifts and keeps accuracy on
the answers it is still confident about; the timetable counter learns, stays confident and gets worse on shift
days; the naive LLM stays confident and tracks last seen. Everything is read on the moved-since-round half
(the still half is recency's by construction) and on each household's OWN shift days vs its plain days.

Usage: python3 check_fb.py [--dir heldout_fb] [--label t03] [--hh 10,11,...] [--flags-only] [--story]"""
import argparse, collections, glob, json, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT.rsplit('/results', 1)[0], 'src'))
from baselines.patrol.bank import _Truth  # noqa

DAYS = {1: "Wed", 2: "Thu", 3: "Fri", 4: "Sat", 5: "Sun", 6: "Mon", 7: "Tue"}
NIGHT = 3 * 3600
Rec = collections.namedtuple("Rec", "hh day moved ok conf shift qid ans")


def load_bank(path):
    rows = [json.loads(l) for l in open(path)]
    h = rows[0]; truth = _Truth([r for r in rows if r["kind"] == "truth"]); shift = set(h.get("shift_days", []))
    qs = {}
    for r in rows:
        if r["kind"] != "question": continue
        t = r["t_query"]; day = t // 86400; d = r.get("day_index", day)
        at_q = truth.at(r["object_id"], t); at_night = truth.at(r["object_id"], day * 86400 + NIGHT)
        qs[r["question_id"]] = {"day": d, "moved": at_q != at_night, "truth": at_q, "shift": d in shift}
    msg_days = sorted(m["day_index"] for m in h.get("hint_messages", []) if "day_index" in m)
    return h, qs, msg_days


def acc(recs):
    return (100.0 * sum(r.ok for r in recs) / len(recs)) if recs else None


def conf(recs):
    return (sum(r.conf for r in recs) / len(recs)) if recs else None


def fmt(x, pct=True):
    return "-" if x is None else (f"{x:.0f}" if pct else f"{x:.2f}")


def table(name, recs):
    agg = collections.defaultdict(list)
    for r in recs:
        agg[(r.day, "moved" if r.moved else "still")].append(r); agg[(r.day, "all")].append(r)
    days = sorted({d for d, _ in agg})
    line = f"{name:34s}"
    for split in ("moved", "still", "all"):
        cells = []
        for d in days:
            a = agg.get((d, split))
            cells.append(f"{acc(a):3.0f}/{conf(a):.2f}({len(a)})" if a else "   -    ")
        line += f" | {split:5s} " + " ".join(cells)
    mv = [r for r in recs if r.moved and r.day >= 2]
    pl, sh = [r for r in mv if not r.shift], [r for r in mv if r.shift]
    f2 = lambda a: f"{acc(a):.0f}%@{conf(a):.2f}(n={len(a)})" if a else "-"
    print(line + f" | moved Thu-Tue plain {f2(pl)} vs shift {f2(sh)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="heldout_fb"); ap.add_argument("--label", default="t03")
    ap.add_argument("--hh", default="10,11,12,13,14,18,19,25")
    ap.add_argument("--flags-only", action="store_true"); ap.add_argument("--story", action="store_true")
    a = ap.parse_args()
    seeds = [int(x) for x in a.hh.split(",")]
    D = os.path.join(ROOT, a.dir)
    banks = {}
    for s in seeds:
        p = f"{D}/banks/hh_s{s}_{a.label}.jsonl"
        if os.path.exists(p): banks[f"hh_s{s}"] = load_bank(p)
    if not banks:
        print("no banks under", D); return
    print(f"== {a.dir} ({a.label}) households {sorted(banks)}; cells = acc%/mean conf(n); days Wed..Tue; {time.strftime('%H:%M')}")
    A = collections.defaultdict(list)          # agent -> [Rec]
    flags = []
    # ---- classical
    for hh, (h, qs, _) in banks.items():
        p = f"{D}/classical/{hh}_{a.label}.jsonl"
        if not os.path.exists(p): continue
        for l in open(p):
            r = json.loads(l); q = qs.get(r["question_id"])
            if q: A["classical:" + r["belief"]].append(Rec(hh, q["day"], q["moved"], int(r["correct"]), float(r.get("top_prob", 0)), q["shift"], r["question_id"], r["answer"]))
    # ---- naive LLM (calls.jsonl, partial while running)
    for d in sorted(glob.glob(f"{D}/llm/*_naive_*")):
        hh = os.path.basename(d).split("_" + a.label)[0]
        if hh not in banks: continue
        told = "nottold" if "nottold" in d else "told"; qs = banks[hh][1]; p = f"{d}/calls.jsonl"
        if not os.path.exists(p): continue
        for l in open(p):
            try: r = json.loads(l)
            except json.JSONDecodeError: continue
            q = qs.get(r.get("where"))
            if not q: continue
            m = re.search(r'"location"\s*:\s*"([^"]+)"', r["completion"]); c = re.search(r'"confidence"\s*:\s*([0-9.]+)', r["completion"])
            if m: A[f"naive:{told}"].append(Rec(hh, q["day"], q["moved"], int(m.group(1) == q["truth"]), float(c.group(1)) if c else 0.0, q["shift"], r["where"], m.group(1)))
    # ---- mixture arms (live.jsonl, streamed)
    arm_info = {}
    for d in sorted(glob.glob(f"{D}/hyp/study/*/arms/passive/*")):
        hh = os.path.basename(d.split("/arms/")[0]).split("_" + a.label)[0]
        if hh not in banks: continue
        told = "nottold" if d.endswith("nottold") else "told"; qs = banks[hh][1]; p = f"{d}/live.jsonl"
        if not os.path.exists(p): continue
        alive = os.popen(f"pgrep -fc 'run_tour_start --household {hh}_{a.label} '").read().strip() not in ("", "0")
        age = (time.time() - os.path.getmtime(p)) / 60
        if alive and age > 40:
            flags.append(f"{hh} {told}: process alive but no new answer for {age:.0f} min ({'still no first answer' if os.path.getsize(p) == 0 else 'stall?'})")
        ess = collections.defaultdict(list); n = 0; wmax = collections.defaultdict(list)
        for l in open(p):
            try: r = json.loads(l)
            except json.JSONDecodeError: continue
            q = qs.get(r["question_id"])
            if not q: continue
            n += 1; top = max(r["dist"].values()) if r.get("dist") else 0.0
            A[f"mixture:{told}"].append(Rec(hh, q["day"], q["moved"], int(r["argmax"] == q["truth"]), top, q["shift"], r["question_id"], r["argmax"]))
            ess[q["day"]].append(r.get("ess", 0)); wmax[q["day"]].append(max(r["weights"].values()) if r.get("weights") else 0)
        revs = collections.Counter(); nvalid = []
        for f in sorted(glob.glob(f"{d}/revisions/*.json")):
            try: j = json.load(open(f)); revs[int(j.get("day", -1))] += 1; nvalid.append(int(j.get("n_valid", 1)))
            except Exception: pass
        if len(nvalid) >= 2 and nvalid[-1] == 0 and nvalid[-2] == 0:
            flags.append(f"{hh} {told}: last two revisions had n_valid 0")
        for day, e in ess.items():
            if len(e) >= 32 and max(e) < 1.05: flags.append(f"{hh} {told}: ESS<=1.05 for all of {DAYS.get(day)} — weights collapsed")
            if len(e) >= 64 and sum(e) / len(e) < 3: flags.append(f"{hh} {told}: mean ESS {sum(e)/len(e):.1f} on {DAYS.get(day)} < 3 (f1's expectation >= 3)")
            if len(wmax[day]) >= 64 and min(wmax[day]) > 0.7: flags.append(f"{hh} {told}: one document above 0.7 weight for all of {DAYS.get(day)}")
        days_done = sorted(ess); last = days_done[-1] if days_done else 0
        arm_info[(hh, told)] = dict(n=n, last=last, alive=alive)
        print(f"   arm {hh:6s} {told:7s}: {n:3d} answers, through {DAYS.get(last,'-')}{'' if alive else ' [no process]'}; revisions by day {dict(sorted(revs.items()))}; mean ESS {[round(sum(ess[k])/len(ess[k]),1) for k in days_done]}; max doc weight {[round(max(wmax[k]),2) for k in days_done]}")
        if told == "nottold" and last >= 5 and not revs: flags.append(f"{hh} nottold: no revisions through {DAYS.get(last)}")
    # ---- naive one-number confidence
    for name in [k for k in A if k.startswith("naive:")]:
        cc = collections.Counter(round(r.conf, 2) for r in A[name]); v, k = cc.most_common(1)[0]
        if len(A[name]) >= 200 and k / len(A[name]) > 0.9: flags.append(f"{name}: {100*k/len(A[name]):.0f}% of answers at confidence {v}")
    # ---- logs
    for f in sorted(glob.glob(f"{D}/arm_s*_*.log")):
        txt = open(f, errors="replace").read()
        if "Traceback" in txt:
            age = (time.time() - os.path.getmtime(f)) / 60
            flags.append(f"{os.path.basename(f)}: Traceback{' (STALE, %.0f min old)' % age if age > 30 else ''}: {txt.strip().splitlines()[-1][:120]}")
    if os.path.exists(f"{D}/arms_fb.log"):
        for l in open(f"{D}/arms_fb.log"):
            if re.search(r"exit [1-9]", l): flags.append("arms_fb.log: " + l.strip())

    if not a.flags_only:
        for name in sorted(A): table(name, A[name])

    # ================= STORY CHECKS =================
    # Each check: (label, verdict, detail). Verdict PASS / FAIL / n.a. Computed per household for the mixture,
    # pooled for the references. Only completed days (64 answers) count.
    story = []
    def by_hh(name): 
        out = collections.defaultdict(list)
        for r in A.get(name, []): out[r.hh].append(r)
        return out
    def completed(recs):
        c = collections.Counter(r.day for r in recs); return {d for d, n in c.items() if n >= 64}
    LS, TT = by_hh("classical:LastObservation"), by_hh("classical:TimetableLookup(bin=2h,days=all)")
    NV = by_hh("naive:told"); MX, MXN = by_hh("mixture:told"), by_hh("mixture:nottold")
    for hh in sorted(banks):
        h, qs, msg_days = banks[hh]; shift = set(h.get("shift_days", []))
        for arm, M in (("told", MX), ("nottold", MXN)):
            recs = M.get(hh, []); done = completed(recs)
            if not done: continue
            tag = f"{hh} {arm}"
            mv = lambda days: [r for r in recs if r.moved and r.day in days]
            st = lambda days: [r for r in recs if not r.moved and r.day in days]
            # 1. learning on the moved half: Fri (or latest plain weekday) above Wed by >= 5, and >= last seen
            plain_wk = sorted(d for d in done if d in (2, 3) and d not in shift)
            if 1 in done and plain_wk:
                d = plain_wk[-1]; a0, a1 = acc(mv({1})), acc(mv({d}))
                ls = acc([r for r in LS.get(hh, []) if r.moved and r.day == d])
                story.append((f"{tag}: learns on moved (Wed {fmt(a0)} -> {DAYS[d]} {fmt(a1)}; last seen {fmt(ls)})",
                              "FAIL" if (a1 is not None and (a1 - (a0 or 0) < 5 or (ls is not None and a1 < ls))) else "PASS"))
            # 2. flat? all-question accuracy spread over completed days < 4 points AND moved-half spread < 8
            if len(done) >= 4:
                allacc = [acc([r for r in recs if r.day == d]) for d in sorted(done)]
                mvacc = [acc(mv({d})) for d in sorted(done)]
                flat = (max(allacc) - min(allacc) < 4) and (max(mvacc) - min(mvacc) < 8)
                story.append((f"{tag}: not flat (all {[round(x) for x in allacc]}, moved {[round(x) for x in mvacc]})", "FAIL" if flat else "PASS"))
            # 3. break on the household's own shift days (moved half, Thu-Tue): accuracy AND confidence lower than plain
            pl = [r for r in recs if r.moved and r.day >= 2 and r.day in done and not r.shift]
            sh = [r for r in recs if r.moved and r.day >= 2 and r.day in done and r.shift]
            if len(pl) >= 40 and len(sh) >= 40:
                story.append((f"{tag}: shift days lower ACC on moved (plain {fmt(acc(pl))} vs shift {fmt(acc(sh))})", "FAIL" if acc(sh) >= acc(pl) else "PASS"))
                story.append((f"{tag}: shift days lower CONF on moved (plain {fmt(conf(pl),0)} vs shift {fmt(conf(sh),0)})", "FAIL" if conf(sh) >= conf(pl) - 0.01 else "PASS"))
                # 4. selective accuracy at >= 0.7 holds on shift days (the counters' failure the mixture must not have)
                pc = [r for r in pl if r.conf >= 0.7]; sc = [r for r in sh if r.conf >= 0.7]
                if len(pc) >= 8 and len(sc) >= 8:
                    story.append((f"{tag}: selective acc@0.7 holds on shift (plain {fmt(acc(pc))} vs shift {fmt(acc(sc))}; coverage {100*len(pc)/len(pl):.0f}% -> {100*len(sc)/len(sh):.0f}%)",
                                  "FAIL" if acc(sc) < acc(pc) - 10 else "PASS"))
                    story.append((f"{tag}: coverage@0.7 dips on shift ({100*len(pc)/len(pl):.0f}% -> {100*len(sc)/len(sh):.0f}%)", "FAIL" if len(sc)/len(sh) >= len(pc)/len(pl) else "PASS"))
            # 5. accuracy RISING after the shift on the still-parked objects is fine, but rising ON shift days vs the day before = suspicious
            # (Wed is excluded: Wed -> Thu is the learning step, not a shift effect)
            plain_after_wed = {d for d in done if d >= 2 and d not in shift}
            if plain_after_wed:
                b = acc(mv(plain_after_wed))
                for d in sorted(done):
                    if d in shift and d >= 2:
                        s_ = acc(mv({d}))
                        if b is not None and s_ is not None and s_ > b + 10 and len(mv({d})) >= 10:
                            story.append((f"{tag}: moved accuracy on shift day {DAYS[d]} ({fmt(s_)}) ABOVE its plain-day level ({fmt(b)}) — shift not a shift?", "FAIL"))
            # 5b. per completed day: confidence on moved questions below confidence on still questions
            for d in sorted(done):
                m_, s_ = mv({d}), st({d})
                if len(m_) >= 8 and len(s_) >= 8:
                    story.append((f"{tag}: conf moved < still on {DAYS[d]} ({conf(m_):.2f} vs {conf(s_):.2f})", "FAIL" if conf(m_) >= conf(s_) else "PASS"))
            # 6. still half stays high (no erosion)
            for d in sorted(done):
                s = acc(st({d}))
                if s is not None and s < 80: story.append((f"{tag}: still-object accuracy {fmt(s)} on {DAYS[d]} < 80", "FAIL"))
            # 7. mixture is its own agent: answers differ from last seen and from the naive LLM on a real share of moved questions
            for refname, R in (("last seen", LS), ("naive", NV)):
                ref = {r.qid: r.ans for r in R.get(hh, [])}
                common = [r for r in recs if r.moved and r.qid in ref]
                if len(common) >= 40:
                    same = sum(r.ans == ref[r.qid] for r in common) / len(common)
                    story.append((f"{tag}: not a copy of {refname} on moved ({100*same:.0f}% identical answers)", "FAIL" if same > 0.9 else "PASS"))
            # 8. confidence moves at all across the week
            if len(done) >= 3:
                cs = [conf([r for r in recs if r.day == d]) for d in sorted(done)]
                story.append((f"{tag}: confidence moves over the week ({[round(c,2) for c in cs]})", "FAIL" if max(cs) - min(cs) < 0.03 else "PASS"))
        # 9. told vs not told: differ after the first message; told better on moved the day after
        t, nt = MX.get(hh, []), MXN.get(hh, [])
        if t and nt and msg_days:
            m0 = msg_days[0]; ta = {r.qid: r for r in t if r.day > m0}; na = {r.qid: r for r in nt if r.day > m0}
            common = [q for q in ta if q in na]
            if len(common) >= 32:
                same = sum(ta[q].ans == na[q].ans for q in common) / len(common)
                story.append((f"{hh}: told differs from not-told after message day {DAYS.get(m0)} ({100*same:.0f}% identical)", "FAIL" if same > 0.97 else "PASS"))
                nxt = [q for q in common if ta[q].day == m0 + 1 and ta[q].moved]
                if len(nxt) >= 8:
                    at, an = acc([ta[q] for q in nxt]), acc([na[q] for q in nxt])
                    story.append((f"{hh}: told recovers faster on {DAYS.get(m0+1)} moved (told {fmt(at)} vs not told {fmt(an)})", "FAIL" if at < an else "PASS"))
    # 10. pooled: everything moving together? per-day all-question accuracy deltas of mixture vs timetable vs naive
    names = [("mixture", A.get("mixture:told", [])), ("timetable", A.get("classical:TimetableLookup(bin=2h,days=all)", [])), ("naive", A.get("naive:told", []))]
    done_all = None
    for _, recs in names:
        c = collections.Counter(r.day for r in recs); ds = {d for d, n in c.items() if n >= 64}
        done_all = ds if done_all is None else done_all & ds
    if done_all and len(done_all) >= 4:
        hhs = {r.hh for r in A.get("mixture:told", [])}
        vec = {nm: [acc([r for r in recs if r.day == d and r.hh in hhs]) for d in sorted(done_all)] for nm, recs in names}
        dl = {nm: [round(v[i+1]-v[i]) for i in range(len(v)-1)] for nm, v in vec.items()}
        same = all(abs(dl["mixture"][i] - dl["timetable"][i]) <= 2 for i in range(len(dl["mixture"])))
        story.append((f"pooled: mixture does not just move with the timetable (day deltas mixture {dl['mixture']} timetable {dl['timetable']} naive {dl['naive']})", "FAIL" if same else "PASS"))

    if a.story or not a.flags_only:
        print("STORY CHECKS" + ("" if story else ": n.a. (no completed days yet)"))
        for label, v in story: print(f"  [{v}] {label}")
    fails = [l for l, v in story if v == "FAIL"]
    print("RED FLAGS:" if (flags or fails) else "no red flags")
    for f in flags: print("  !!", f)
    for f in fails: print("  !! story:", f)


if __name__ == "__main__":
    main()
