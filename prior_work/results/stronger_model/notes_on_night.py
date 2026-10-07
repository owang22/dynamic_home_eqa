"""The notes as they stood at the end of night N, rebuilt from notes.json.
A revision dated day D stores under `was` the text it REPLACED, so the text at the end of night N is the
`was` of the first revision after N, or the current text if there is none.
    python3 results/stronger_model/notes_on_night.py <cell dir> N [N ...]"""
import json, sys, pathlib

def notes_at(claims, n):
    out = []
    for c in claims:
        if (c.get("first_written_day") or 0) > n:
            continue
        later = [h for h in c.get("revision_history", []) if h["day"] > n]
        s = later[0]["was"] if later else {k: c.get(k) for k in ("statement", "holds_under", "status", "standing")}
        out.append((c["claim_id"], s))
    return out

d = json.load(open(pathlib.Path(sys.argv[1]) / "notes.json"))
for n in map(int, sys.argv[2:]):
    ns = notes_at(d["claims"], n)
    standing = [(i, s) for i, s in ns if s.get("standing") == "still standing"]
    print(f"\n=== end of night {n}: {len(standing)} standing notes ({len(ns) - len(standing)} set aside)")
    for i, s in standing:
        print(f"- [{i[-4:]} {s.get('status')}] {s['statement']}  || holds under: {s.get('holds_under')}")
