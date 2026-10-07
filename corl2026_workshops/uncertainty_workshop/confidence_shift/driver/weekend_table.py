#!/usr/bin/env python3
"""Coverage-matched read of the shift claim. Moved-since-round questions, Thu-Tue, split into each household's OWN shift
days vs its plain days. For every agent: accuracy, mean confidence, and selective accuracy at 25/50/75% coverage (rank the
split's questions by the agent's own confidence, keep the top share). Pooled over households (--hh) and per household.
Only days completed by the mixture (64 answers) are used for every agent, so the comparison is on identical questions."""
import argparse, collections, glob, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT.rsplit('/results', 1)[0], 'src'))
from baselines.patrol.bank import _Truth  # noqa
NIGHT = 3 * 3600


def sel(recs, share):
    if not recs: return None
    k = max(1, int(round(share * len(recs)))); top = sorted(recs, key=lambda r: -r[1])[:k]
    return 100.0 * sum(r[0] for r in top) / len(top)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--hh", default="10,11,14,18,19,25"); ap.add_argument("--dir", default="heldout_fb")
    ap.add_argument("--label", default="t03"); ap.add_argument("--arm", default="told"); ap.add_argument("--per-hh", action="store_true")
    a = ap.parse_args(); D = os.path.join(ROOT, a.dir)
    agents = collections.defaultdict(lambda: collections.defaultdict(list))  # agent -> (hh, split) -> [(ok, conf)]
    days_used = {}
    for s in [int(x) for x in a.hh.split(",")]:
        hh = f"hh_s{s}"; bp = f"{D}/banks/{hh}_{a.label}.jsonl"
        if not os.path.exists(bp): continue
        rows = [json.loads(l) for l in open(bp)]; h = rows[0]; tr = _Truth([r for r in rows if r["kind"] == "truth"]); shift = set(h["shift_days"])
        qs = {}
        for r in rows:
            if r["kind"] != "question": continue
            t = r["t_query"]; d = r["day_index"]
            if d < 2: continue
            if tr.at(r["object_id"], t) == tr.at(r["object_id"], (t // 86400) * 86400 + NIGHT): continue
            qs[r["question_id"]] = ("shift" if d in shift else "plain", tr.at(r["object_id"], t), d)
        lp = glob.glob(f"{D}/hyp/study/{hh}_{a.label}__bank0/arms/passive/*__{a.arm}/live.jsonl")
        mix = {}
        if lp:
            for l in open(lp[0]):
                try: r = json.loads(l)
                except json.JSONDecodeError: continue
                mix[r["question_id"]] = (r["argmax"], max(r["dist"].values()))
        cnt = collections.Counter(json.loads(l)["day"] for l in open(lp[0])) if lp else {}
        done = {d for d, n in cnt.items() if n >= 64}
        days_used[hh] = sorted(done)
        qs = {q: v for q, v in qs.items() if v[2] in done}
        if not qs: continue
        for q, (sp, truth, d) in qs.items():
            if q in mix: agents["mixture (" + a.arm + ")"][(hh, sp)].append((int(mix[q][0] == truth), mix[q][1]))
        for l in open(f"{D}/classical/{hh}_{a.label}.jsonl"):
            r = json.loads(l); v = qs.get(r["question_id"])
            if v and r["belief"] in ("TimetableLookup(bin=2h,days=all)", "LastObservation", "MostFrequentLocation"):
                name = {"TimetableLookup(bin=2h,days=all)": "timetable", "LastObservation": "last seen", "MostFrequentLocation": "most frequent"}[r["belief"]]
                agents[name][(hh, v[0])].append((int(r["correct"]), float(r.get("top_prob", 0))))
        np_ = f"{D}/llm/{hh}_{a.label}_naive_{'told' if a.arm == 'told' else 'nottold'}_lookoff/calls.jsonl"
        if os.path.exists(np_):
            for l in open(np_):
                r = json.loads(l); v = qs.get(r.get("where"))
                if not v: continue
                m = re.search(r'"location"\s*:\s*"([^"]+)"', r["completion"]); c = re.search(r'"confidence"\s*:\s*([0-9.]+)', r["completion"])
                if m: agents["naive LLM"][(hh, v[0])].append((int(m.group(1) == v[1]), float(c.group(1)) if c else 0.0))
    print(f"Days used per household (completed by the mixture): { {h: d for h, d in days_used.items()} }")
    print("\nMoved-since-round questions, Thu-Tue; plain = the household's non-shift days, shift = its own shift days.")
    print("Cells: acc% / mean conf / selective acc at 25|50|75% coverage (n)\n")
    hdr = "| agent | plain | shift | delta acc | delta sel@50 |\n|---|---|---|---|---|"
    def row(name, pl, sh):
        f = lambda v: f"{100*sum(r[0] for r in v)/len(v):.0f} / {sum(r[1] for r in v)/len(v):.2f} / {sel(v,.25):.0f}|{sel(v,.5):.0f}|{sel(v,.75):.0f} (n={len(v)})" if v else "-"
        da = (100*sum(r[0] for r in sh)/len(sh) - 100*sum(r[0] for r in pl)/len(pl)) if pl and sh else None
        ds = (sel(sh,.5) - sel(pl,.5)) if pl and sh else None
        return f"| {name} | {f(pl)} | {f(sh)} | {da:+.0f} | {ds:+.0f} |" if da is not None else f"| {name} | {f(pl)} | {f(sh)} | - | - |"
    print("### pooled\n" + hdr)
    for name in ("mixture (" + a.arm + ")", "timetable", "most frequent", "last seen", "naive LLM"):
        pl = [x for (hh, sp), v in agents[name].items() if sp == "plain" for x in v]; sh = [x for (hh, sp), v in agents[name].items() if sp == "shift" for x in v]
        print(row(name, pl, sh))
    if a.per_hh:
        for hh in sorted({hh for name in agents for (hh, sp) in agents[name]}):
            print(f"\n### {hh} (days {days_used.get(hh)})\n" + hdr)
            for name in ("mixture (" + a.arm + ")", "timetable", "last seen", "naive LLM"):
                print(row(name, agents[name].get((hh, "plain"), []), agents[name].get((hh, "shift"), [])))


if __name__ == "__main__":
    main()
