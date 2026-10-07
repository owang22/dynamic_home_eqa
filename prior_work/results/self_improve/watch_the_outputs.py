#!/usr/bin/env python3
"""Look at what the model actually wrote, across every running job.

Accuracy hides the three ways an arm breaks: answers piling onto one spot,
consecutive answers identical, and the model not answering at all. Two degenerate
arms have each cost this project a night, and both would have been caught here in
the first minutes. Exits 1 if anything trips.
"""
import collections, json, pathlib, sys

ROOT = pathlib.Path("results/self_improve")
JOBS = ["accuracy_by_day", "memory_factor_rich_looks", "search_driven",
        "raw_log_baseline", "rewrite_wording", "frozen_memory_test_v1_full_window"]
tripped = []


def look_at_answers(p):
    d = json.loads(p.read_text())
    ans = d.get("answers") or []
    if not ans:
        return None
    places = [a.get("answer_place") for a in ans if a.get("answer_place")]
    c = collections.Counter(places)
    rep = sum(1 for i in range(1, len(places)) if places[i] == places[i - 1])
    return {"n": len(ans), "unparsed": 1 - len(places) / len(ans),
            "distinct": len(c),
            "commonest": (c.most_common(1)[0][1] / len(places)) if places else 1.0,
            "repeat": rep / (len(places) - 1) if len(places) > 1 else 0.0,
            "acc": d.get("share_correct")}


def look_at_notes(p):
    d = json.loads(p.read_text())
    cl = d.get("claims") or []
    ns = d.get("nightly_summaries") or []
    txts = [c.get("statement", "") for c in cl] or \
           [(s.get("summary") if isinstance(s.get("summary"), str) else "\n".join(s.get("summary") or []))
            for s in ns]
    if not txts:
        return None
    blank = sum(1 for t in txts if not (t or "").strip())
    return {"lines": len(txts), "blank": blank,
            "chars": sum(len(t or "") for t in txts) // max(1, len(txts))}


for job in JOBS:
    base = ROOT / job
    if not base.exists():
        continue
    cells = sorted(base.rglob("held_out_answers.json"))
    notes = sorted(base.rglob("notes.json")) + sorted(base.rglob("notes_frozen_at_day_*.json"))
    print(f"\n=== {job}: {len(cells)} answer cell(s), {len(notes)} notes file(s)")
    for p in cells[-6:]:
        try:
            r = look_at_answers(p)
        except (ValueError, OSError):
            print(f"   UNREADABLE (still being written?) {p.parent.name}")
            continue
        if not r:
            continue
        flags = []
        if r["commonest"] > 0.6: flags.append(f"{r['commonest']:.0%} on one spot")
        if r["repeat"] > 0.8: flags.append("consecutive answers nearly always identical")
        if r["unparsed"] > 0.1: flags.append(f"{r['unparsed']:.0%} unparsed")
        if r["distinct"] <= 2 and r["n"] > 10: flags.append(f"only {r['distinct']} spots ever named")
        tag = "  <-- " + "; ".join(flags) if flags else ""
        if flags: tripped.append((job, str(p.parent), flags))
        print(f"   {str(p.parent.relative_to(base))[:58]:60s} n={r['n']:4d} "
              f"acc={(r['acc'] or 0)*100:5.1f}% distinct={r['distinct']:3d} "
              f"commonest={r['commonest']:.2f} repeat={r['repeat']:.2f}{tag}")
    blanks = 0
    for p in notes[-40:]:
        try:
            r = look_at_notes(p)
        except (ValueError, OSError):
            continue
        if r and r["blank"]:
            blanks += r["blank"]
    if blanks:
        print(f"   {blanks} blank note line(s) across the last {min(40, len(notes))} notes files")
        tripped.append((job, "notes", [f"{blanks} blank lines"]))

print("\n" + ("NOTHING TRIPPED" if not tripped else
              "TRIPPED:\n" + "\n".join(f"  {j} :: {w} :: {'; '.join(f)}" for j, w, f in tripped)))
sys.exit(1 if tripped else 0)
