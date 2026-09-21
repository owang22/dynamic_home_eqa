#!/usr/bin/env python3
"""Overnight driver check: per-day accuracy / confidence, split by whether the object moved since the
03:00 round, for every agent that has logged anything under a heldout dir (classical, naive calls.jsonl,
mixture live.jsonl). Also prints red flags (arm exit codes, tracebacks, ESS collapse, missing revisions).
Usage: python3 check_fb.py [--dir heldout_fb] [--label t03] [--hh 10-14]"""
import argparse, collections, glob, json, os, re, sys, gzip, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT.rsplit('/results', 1)[0]), 'dynamic_home_eqa', 'src'))
from baselines.patrol.bank import _Truth  # noqa

DAYS = {1: "Wed", 2: "Thu", 3: "Fri", 4: "Sat", 5: "Sun", 6: "Mon", 7: "Tue"}
NIGHT = 3 * 3600


def load_bank(path):
    rows = [json.loads(l) for l in open(path)]
    truth = _Truth([r for r in rows if r["kind"] == "truth"])
    qs = {}
    for r in rows:
        if r["kind"] != "question":
            continue
        t = r["t_query"]; day = t // 86400
        at_q = truth.at(r["object_id"], t)
        at_night = truth.at(r["object_id"], day * 86400 + NIGHT)
        d = r.get("day_index", day)
        qs[r["question_id"]] = {"day": d, "moved": at_q != at_night, "truth": at_q, "t": t, "shift": d in set(rows[0].get("shift_days", []))}
    return rows[0], qs


def table(name, recs):
    """recs: list of (day, moved, correct, conf). Print acc%/conf per day for moved | still | all."""
    agg = collections.defaultdict(lambda: [0, 0, 0.0])
    ps = collections.defaultdict(lambda: [0, 0, 0.0])
    for day, moved, ok, conf, shift in recs:
        if moved and day >= 2:  # Thu-Tue, moved half: the household's own shift days vs its plain days
            k = ps["shift" if shift else "plain"]; k[0] += 1; k[1] += ok; k[2] += conf
        for key in ((day, "moved" if moved else "still"), (day, "all")):
            a = agg[key]; a[0] += 1; a[1] += ok; a[2] += conf
    days = sorted({d for d, _ in agg})
    line = f"{name:34s}"
    for split in ("moved", "still", "all"):
        cells = []
        for d in days:
            a = agg.get((d, split))
            cells.append(f"{100*a[1]/a[0]:3.0f}/{a[2]/a[0]:.2f}({a[0]})" if a else "   -    ")
        line += f" | {split:5s} " + " ".join(cells)
    pl, sh = ps.get("plain"), ps.get("shift")
    fmt = lambda a: f"{100*a[1]/a[0]:.0f}%@{a[2]/a[0]:.2f}(n={a[0]})" if a and a[0] else "-"
    line += f" | moved Thu-Tue plain {fmt(pl)} vs shift {fmt(sh)}"
    print(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="heldout_fb"); ap.add_argument("--label", default="t03")
    ap.add_argument("--hh", default="10,11,12,13,14,18,19,25", help="comma list or a-b range")
    ap.add_argument("--flags-only", action="store_true")
    a = ap.parse_args()
    seeds = list(range(*[int(x) + i for i, x in enumerate(a.hh.split("-"))])) if "-" in a.hh else [int(x) for x in a.hh.split(",")]
    D = os.path.join(ROOT, a.dir)
    banks = {}
    for s in seeds:
        p = f"{D}/banks/hh_s{s}_{a.label}.jsonl"
        if os.path.exists(p):
            banks[f"hh_s{s}"] = load_bank(p)
    if not banks:
        print("no banks under", D); return
    print(f"== {a.dir} ({a.label}) households {sorted(banks)}; cells = acc%/mean conf(n); days Wed..Tue")
    per_agent = collections.defaultdict(list)
    # classical
    for hh in banks:
        p = f"{D}/classical/{hh}_{a.label}.jsonl"
        if not os.path.exists(p):
            continue
        qs = banks[hh][1]
        for l in open(p):
            r = json.loads(l); q = qs.get(r["question_id"])
            if not q: continue
            per_agent["classical:" + r["belief"]].append((q["day"], q["moved"], int(r["correct"]), float(r.get("top_prob", 0)), q["shift"]))
    # naive LLM
    for d in sorted(glob.glob(f"{D}/llm/*_naive_*")):
        hh = os.path.basename(d).split("_" + a.label)[0]
        if hh not in banks: continue
        told = "nottold" if "nottold" in d else "told"
        qs = banks[hh][1]; p = f"{d}/calls.jsonl"
        if not os.path.exists(p): continue
        for l in open(p):
            r = json.loads(l); q = qs.get(r.get("where"))
            if not q: continue
            m = re.search(r'"location"\s*:\s*"([^"]+)"', r["completion"]); c = re.search(r'"confidence"\s*:\s*([0-9.]+)', r["completion"])
            if not m: continue
            per_agent[f"naive:{told}"].append((q["day"], q["moved"], int(m.group(1) == q["truth"]), float(c.group(1)) if c else 0.0, q["shift"]))
    # per-household last-seen reference on the moved half (to compare the mixture against)
    ls_ref = collections.defaultdict(lambda: [0, 0])
    for hh in banks:
        p = f"{D}/classical/{hh}_{a.label}.jsonl"
        if not os.path.exists(p): continue
        qs = banks[hh][1]
        for l in open(p):
            r = json.loads(l); q = qs.get(r["question_id"])
            if q and r["belief"] == "LastObservation" and q["moved"]:
                k = ls_ref[(hh, q["day"])]; k[0] += 1; k[1] += int(r["correct"])
    # naive: confidence concentration (a naive LLM that says one number everywhere and beats last seen = suspicious)
    flags = []
    for name in list(per_agent):
        if not name.startswith("naive:"): continue
        confs = collections.Counter(round(x[3], 2) for x in per_agent[name])
        top_c, top_n = confs.most_common(1)[0]; n = sum(confs.values())
        if n >= 200 and top_n / n > 0.9:
            flags.append(f"{name}: {100*top_n/n:.0f}% of {n} answers at confidence {top_c} (one-number confidence)")
    # mixture arms (live.jsonl)
    argmax_by = collections.defaultdict(dict)  # (hh, told) -> qid -> argmax
    for d in sorted(glob.glob(f"{D}/hyp/study/*/arms/passive/*")):
        hh = os.path.basename(d.split("/arms/")[0]).split("_" + a.label)[0]
        if hh not in banks: continue
        told = "nottold" if d.endswith("nottold") else "told"
        qs = banks[hh][1]; p = f"{d}/live.jsonl"
        if not os.path.exists(p): continue
        ess_by_day = collections.defaultdict(list); n = 0
        st = collections.defaultdict(lambda: [0, 0, 0.0])  # (day, moved) -> n, ok, conf
        alive = os.popen(f"pgrep -fc 'run_tour_start --household {hh}_{a.label} '").read().strip() not in ("", "0")
        age_min = (time.time() - os.path.getmtime(p)) / 60
        if alive and age_min > 40 and os.path.getsize(p) > 0:
            flags.append(f"{hh} {told}: process alive but no new answer for {age_min:.0f} min (stall?)")
        for l in open(p):
            try: r = json.loads(l)
            except json.JSONDecodeError: continue
            q = qs.get(r["question_id"]);
            if not q: continue
            n += 1
            top = max(r["dist"].values()) if r.get("dist") else 0.0
            ok = int(r["argmax"] == q["truth"])
            per_agent[f"mixture:{told}"].append((q["day"], q["moved"], ok, top, q["shift"]))
            ess_by_day[q["day"]].append(r.get("ess", 0))
            k = st[(q["day"], q["moved"])]; k[0] += 1; k[1] += ok; k[2] += top
            argmax_by[(hh, told)][r["question_id"]] = r["argmax"]
        revs = collections.Counter(); nvalid = []
        for f in sorted(glob.glob(f"{d}/revisions/*.json")):
            try: j = json.load(open(f)); revs[int(j.get("day", -1))] += 1; nvalid.append(int(j.get("n_valid", 1)))
            except Exception: pass
        if len(nvalid) >= 2 and nvalid[-1] == 0 and nvalid[-2] == 0:
            flags.append(f"{hh} {told}: last two revisions had n_valid 0")
        # per completed day: expectation checks (a day is complete at 64 answers)
        for day in sorted({k[0] for k in st}):
            mv, stl = st.get((day, True)), st.get((day, False))
            if (mv[0] if mv else 0) + (stl[0] if stl else 0) < 64: continue
            if stl and stl[1] / stl[0] < 0.80:
                flags.append(f"{hh} {told}: still-object accuracy {100*stl[1]/stl[0]:.0f}% on day {day} ({DAYS.get(day)}) < 80%")
            if mv and stl and mv[0] >= 8 and mv[2] / mv[0] >= stl[2] / stl[0]:
                flags.append(f"{hh} {told}: confidence on moved {mv[2]/mv[0]:.2f} >= still {stl[2]/stl[0]:.2f} on day {day} ({DAYS.get(day)})")
            if mv and mv[0] >= 8 and mv[1] / mv[0] > 0.80:
                flags.append(f"{hh} {told}: moved accuracy {100*mv[1]/mv[0]:.0f}% on day {day} — implausibly high, check for a feedback leak")
            ref = ls_ref.get((hh, day))
            if day in (2, 3) and mv and ref and ref[0] and mv[1] / mv[0] < ref[1] / ref[0]:
                flags.append(f"{hh} {told}: moved accuracy {100*mv[1]/mv[0]:.0f}% on {DAYS.get(day)} is BELOW last seen ({100*ref[1]/ref[0]:.0f}%)")
        days_done = sorted(ess_by_day)
        for day in days_done:
            e = ess_by_day[day]
            if len(e) >= 32 and max(e) < 1.05:
                flags.append(f"{hh} {told}: ESS<=1.05 for all of day {day} ({DAYS.get(day)}) — weights collapsed")
        last = days_done[-1] if days_done else 0
        print(f"   arm {hh:6s} {told:7s}: {n:3d} answers, through {DAYS.get(last,'-')}; revisions by day {dict(sorted(revs.items()))}; "
              f"mean ESS by day {[round(sum(ess_by_day[k])/len(ess_by_day[k]),1) for k in days_done]}")
        if told == "nottold" and last >= 5 and sum(revs.values()) == 0:
            flags.append(f"{hh} nottold: no revisions at all through day {last}")
    # told vs not told identical after the first message day
    for hh in banks:
        t, nt = argmax_by.get((hh, "told")), argmax_by.get((hh, "nottold"))
        if not t or not nt: continue
        msg_days = sorted(m["day_index"] for m in banks[hh][0].get("hint_messages", []) if "day_index" in m)
        if not msg_days: continue
        qs = banks[hh][1]
        after = [q for q in t if q in nt and qs[q]["day"] > msg_days[0]]
        if len(after) >= 32 and all(t[q] == nt[q] for q in after):
            flags.append(f"{hh}: told and not-told give IDENTICAL answers on {len(after)} questions after the first message day {msg_days[0]}")
    # arm logs: exit codes and tracebacks
    for f in sorted(glob.glob(f"{D}/arm_s*_*.log")):
        txt = open(f, errors="replace").read()
        if "Traceback" in txt:
            age = (time.time() - os.path.getmtime(f)) / 60
            tag = " (STALE, log untouched for %.0f min)" % age if age > 30 else ""
            flags.append(f"{os.path.basename(f)}: Traceback{tag}: " + txt.strip().splitlines()[-1][:140])
    p = f"{D}/arms_fb.log"
    if os.path.exists(p):
        for l in open(p):
            if re.search(r"exit [1-9]", l): flags.append("arms_fb.log: " + l.strip())
    if not a.flags_only:
        for name in sorted(per_agent):
            table(name, per_agent[name])
    print("RED FLAGS:" if flags else "no red flags")
    for f in flags: print("  !!", f)


if __name__ == "__main__":
    main()
