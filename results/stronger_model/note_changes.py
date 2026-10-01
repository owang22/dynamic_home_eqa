"""Notes added or revised each night from night A to B (text as it stood at the end of that night).
    python3 results/stronger_model/note_changes.py <cell dir> A B"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
src = open(pathlib.Path(__file__).parent / "notes_on_night.py").read().split("d = json.load")[0]
exec(src)
d = json.load(open(pathlib.Path(sys.argv[1]) / "notes.json"))
a, b = int(sys.argv[2]), int(sys.argv[3])
prev = dict(notes_at(d["claims"], a - 1))
for n in range(a, b + 1):
    cur = dict(notes_at(d["claims"], n))
    for i, s in cur.items():
        p = prev.get(i)
        tag = "NEW" if p is None else ("REV" if (s["statement"], s.get("holds_under")) != (p["statement"], p.get("holds_under")) else None)
        if p is not None and s.get("standing") != p.get("standing"):
            tag = f"STANDING->{s.get('standing')}"
        if tag:
            print(f"night {n} {tag} [{i[-4:]}] {s['statement'][:260]} || {s.get('holds_under')}")
    prev = cur
