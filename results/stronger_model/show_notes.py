"""Print a cell's notes as they stand now (notes.json is rewritten every night).
    python3 results/stronger_model/show_notes.py <cell dir> [--all]   (--all includes set-aside notes)"""
import json, sys, pathlib
d = json.load(open(pathlib.Path(sys.argv[1]) / "notes.json"))
show_all = "--all" in sys.argv
print(f"written up to night {d['written_up_to_day']}; {len(d['claims'])} notes")
for c in d["claims"]:
    if c.get("standing") != "still standing" and not show_all:
        continue
    print(f"- [{c['claim_id'][-4:]} d{c.get('first_written_day')}->d{c.get('last_revised_day')} {c.get('status')}, {c.get('standing')}] "
          f"{c['statement']}  || holds under: {c.get('holds_under')}  (+{len(c.get('supporting_observation_ids', []))}/-{len(c.get('contradicting_observation_ids', []))})")
