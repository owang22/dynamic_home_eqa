"""Per-window first-room-right for the stronger-model cells on one household, read from searches.jsonl
as the cells stream. First room right = the first room opened is the object's true room. Partial cells
are shown with the last day reached; a window is blank until the cell has reached it.

    PYTHONPATH=src python3 results/stronger_model/compare.py [household]
"""
import json, pathlib, sys
HH = sys.argv[1] if len(sys.argv) > 1 else "hh_s2_t03"
R = pathlib.Path("results")
CELLS = {
    "Qwen plain, log only (wave_log_only, 29 Sep)": R / "self_improve/wave_log_only/cells/log_only_no_notes",
    "Qwen plain, log+notes (Table 1, 25 Sep, old schema)": R / "self_improve/overnight_wave/cells/the_log_and_notes_about_the_routine",
    "Qwen plain, log+notes (rerun 30 Sep)": R / "stronger_model/qwen38_plain/cells/the_log_and_notes_about_the_routine",
    "Qwen think4000, log only": R / "stronger_model/qwen38_think4000/cells/log_only_no_notes",
    "Qwen think4000, log+notes": R / "stronger_model/qwen38_think4000/cells/the_log_and_notes_about_the_routine",
    "Sonnet, log only": R / "stronger_model/claude_sonnet/cells/log_only_no_notes",
    "Sonnet, log+notes": R / "stronger_model/claude_sonnet/cells/the_log_and_notes_about_the_routine",
}
WINDOWS = [("settled 8-13", range(8, 14)), ("day 14", [14]), ("15-17", range(15, 18)), ("18-23", range(18, 24)),
           ("day 24", [24]), ("25-27", range(25, 28)), ("28-31", range(28, 32)), ("all", range(1, 32))]

def rows(d):
    f = d / HH / "searches.jsonl"
    if not f.exists():
        return []
    out = []
    for l in open(f):
        r = json.loads(l)
        if r.get("kind") == "search":
            out.append(r)
    return out

def pct(xs):
    return f"{100 * sum(xs) / len(xs):5.1f} ({len(xs):3d})" if xs else "     -     "

for subset in ("all questions", "movers only"):
    print(f"\n{HH} - first room right, % (n) - {subset}")
    print(f"{'cell':52s} {'last day':>8s} " + " ".join(f"{w:>11s}" for w, _ in WINDOWS))
    for name, d in CELLS.items():
        rs = rows(d)
        if subset == "movers only":
            rs = [r for r in rs if r["is_a_mover"]]
        last = max((r["day"] for r in rs), default=None)
        cols = []
        for _, days in WINDOWS:
            xs = [r["rooms_opened"][:1] == [r["true_room"]] for r in rs if r["day"] in days]
            cols.append(pct(xs))
        print(f"{name:52s} {str(last):>8s} " + " ".join(cols))
print("\nfound within 3 rooms, all questions, whole run so far:")
for name, d in CELLS.items():
    rs = rows(d)
    if rs:
        print(f"  {name:52s} {100 * sum(r['found_it'] for r in rs) / len(rs):5.1f} ({len(rs)})")
