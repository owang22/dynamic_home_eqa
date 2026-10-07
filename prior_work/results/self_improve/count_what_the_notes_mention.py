"""What do the notes actually MENTION? Asked-about things, other things, residents.

The direct test of whether richer look descriptions change what the memory records.
Before this, the description handed to the note-writer was filtered to the objects the
robot is quizzed on, and the notes mentioned 12 of one household's 13 asked objects and
ZERO of the other 54 things its looks recorded. If telling the model everything it saw
does nothing to that count, the memory is caching answers to anticipated questions and
the richer description changed only the prompt length.

Counting is STRUCTURAL where it can be. An object counts as named by
`write_the_notes.where_an_object_is_named`, the same audited matcher the vacuity check
uses, which knows that the rewrite arm writes "Nora's book" for book_nora. A resident
counts as named only by its identifier (resident_1, resident_2) or the bare word
"resident"/"people" - none of which occurs inside any object id, so no object mention
can be miscounted as a resident mention.

    python results/self_improve/count_what_the_notes_mention.py \
        --sweeps results/self_improve/memory_factor_v1 \
                 results/self_improve/memory_factor_rich_looks --day 23
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import statistics
import sys
from typing import Any, Dict, List

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.memory_notes import Notes
from self_improve.write_the_notes import _find_whole_words, where_an_object_is_named

RESIDENT_WORDS = ("resident", "residents", "people", "person", "occupant", "occupants")


def what_the_notes_are(notes: Notes) -> str:
    """The whole memory as text, whichever format it is. Not the read window: this is
    a question about what was WRITTEN, not about what fits in eight lines."""
    if notes.claims:
        return "\n".join(c.as_plain_words() for c in notes.claims)
    return notes.newest_summary() or ""


def objects_the_looks_recorded(looks_file: pathlib.Path) -> List[str]:
    """Every distinct object this arm's own looks actually saw. The universe the notes
    COULD have mentioned."""
    seen = set()
    if looks_file.exists():
        for line in looks_file.open():
            row = json.loads(line)
            if row.get("kind") != "look":
                continue
            for sighting in row.get("sightings", []):
                seen.add(sighting["object_id"])
    return sorted(seen)


def count_one_cell(cell_dir: pathlib.Path, household: FrozenHousehold,
                   day: int) -> Dict[str, Any]:
    snapshot = cell_dir / f"notes_frozen_at_day_{day}.json"
    if not snapshot.exists():
        return {}
    notes = Notes.load(snapshot)
    text = what_the_notes_are(notes)
    low = text.lower()
    seen = objects_the_looks_recorded(cell_dir / "looks.jsonl")
    asked = set(household.asked_objects)
    others = [o for o in seen if o not in asked]

    named_asked = [o for o in sorted(asked) if where_an_object_is_named(low, o) >= 0]
    named_other = [o for o in others if where_an_object_is_named(low, o) >= 0]
    # A LOOSER cross-check, reported separately and never mixed with the strict count.
    # The strict matcher deliberately refuses a bare class word ("the mug" cannot be
    # attributed to a person), so a summary that said "tissues appeared by the couch"
    # would score zero above. This counts the class words of non-asked objects, minus
    # any class word an asked object also has, so a hit is a thing the notes mention
    # that they were never quizzed on.
    asked_classes = {household.object_class.get(o, "").replace("_", " ").lower()
                     for o in asked}
    other_classes = sorted({household.object_class.get(o, "").replace("_", " ").lower()
                            for o in others} - asked_classes - {""})
    class_words_present = [c for c in other_classes if _find_whole_words(low, c) >= 0]

    resident_ids = [r for r in household.resident_ids if _find_whole_words(low, r) >= 0]
    resident_word_hits = sum(len(re.findall(rf"\b{w}\b", low)) for w in RESIDENT_WORDS)

    return {
        "household": household.name,
        "arm": cell_dir.name,
        "notes_through_day": notes.written_up_to_day,
        "n_characters": len(text),
        "n_lines": len([l for l in text.splitlines() if l.strip()]),
        "n_asked_objects": len(asked),
        "n_asked_objects_the_notes_name": len(named_asked),
        "n_other_objects_the_looks_saw": len(others),
        "n_other_objects_the_notes_name": len(named_other),
        "which_other_objects": named_other[:12],
        "n_other_object_classes_the_looks_saw": len(other_classes),
        "n_other_object_class_words_in_the_notes_loose": len(class_words_present),
        "which_class_words_loose": class_words_present[:12],
        "n_residents_named_by_id": len(resident_ids),
        "n_times_a_resident_word_appears": resident_word_hits,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweeps", type=pathlib.Path, nargs="+", required=True)
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--day", type=int, default=23)
    parser.add_argument("--out", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    households: Dict[str, FrozenHousehold] = {}
    rows: List[Dict[str, Any]] = []
    for root in args.sweeps:
        for household_dir in sorted(root.glob("hh_s*")):
            name = household_dir.name
            if name not in households:
                households[name] = FrozenHousehold(args.banks / f"{name}.jsonl")
            for cell_dir in sorted(d for d in household_dir.iterdir() if d.is_dir()):
                row = count_one_cell(cell_dir, households[name], args.day)
                if row:
                    row["sweep"] = root.name
                    rows.append(row)

    if not rows:
        print("nothing found")
        return 1

    print(f"notes frozen at day {args.day}")
    print(f"{'sweep':26s} {'household':11s} {'format':20s} {'chars':>6s} {'lines':>5s} "
          f"{'asked named':>12s} {'others named':>13s} {'of':>4s} {'resident ids':>12s} "
          f"{'resident words':>14s} {'loose classes':>13s}")
    for r in rows:
        print(f"{r['sweep'][:26]:26s} {r['household']:11s} {r['arm'][:20]:20s} "
              f"{r['n_characters']:6d} {r['n_lines']:5d} "
              f"{r['n_asked_objects_the_notes_name']:5d}/{r['n_asked_objects']:<6d} "
              f"{r['n_other_objects_the_notes_name']:8d}     "
              f"{r['n_other_objects_the_looks_saw']:4d} "
              f"{r['n_residents_named_by_id']:12d} {r['n_times_a_resident_word_appears']:14d} "
              f"{r['n_other_object_class_words_in_the_notes_loose']:6d}/"
              f"{r['n_other_object_classes_the_looks_saw']:<6d}")

    print()
    for sweep in sorted({r["sweep"] for r in rows}):
        for arm in sorted({r["arm"] for r in rows if r["sweep"] == sweep}):
            here = [r for r in rows if r["sweep"] == sweep and r["arm"] == arm]
            def mean(key):
                return statistics.fmean(r[key] for r in here)
            print(f"{sweep} / {arm}: n={len(here)} households, "
                  f"mean {mean('n_characters'):.0f} characters, "
                  f"{mean('n_asked_objects_the_notes_name'):.1f} of "
                  f"{mean('n_asked_objects'):.1f} asked objects named, "
                  f"{mean('n_other_objects_the_notes_name'):.1f} of "
                  f"{mean('n_other_objects_the_looks_saw'):.1f} other objects named, "
                  f"{mean('n_other_object_class_words_in_the_notes_loose'):.1f} of "
                  f"{mean('n_other_object_classes_the_looks_saw'):.1f} other class words "
                  f"(loose), residents named by id in "
                  f"{sum(1 for r in here if r['n_residents_named_by_id']):d} households")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps({"day": args.day, "per_cell": rows}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
