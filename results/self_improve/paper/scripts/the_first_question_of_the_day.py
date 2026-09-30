#!/usr/bin/env python3
"""What each memory knew at each onset BEFORE that day's looking could teach it.

Day 14 and day 32 accuracy mixes two things: what the memory carried into the day, and what it
worked out during the day from its own looks. This separates them. For each of the 14 objects that
change room in both illnesses, it takes the FIRST question about that object on the onset day, and
keeps it only if no look earlier that day had already seen the object. What is left is retained
knowledge alone.

The day-32 version is the one that matters: if experience from the first illness is retained, it
should show here, before any day-32 sighting can help.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/the_first_question_of_the_day.py
"""
import json
import pathlib
import statistics
import sys

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import paper_data as D                                              # noqa: E402

ARMS = (("last-seen", "last_seen_no_model"),
        ("log and notes", "the_log_and_notes_about_the_routine"),
        ("claim store", "incremental_edits"),
        ("ACE-style playbook", "ACE_as_published"))
DAYS = (14, 32)


def first_sighting_times(arm_dir, home, day):
    """object -> the time of the first look that day which saw it."""
    seen = {}
    path = D.WAVE_50 / arm_dir / home / "looks.jsonl"
    for line in path.open():
        r = json.loads(line)
        if r.get("kind") != "look" or r.get("day") != day:
            continue
        for s in r.get("sightings", []):
            seen.setdefault(s["object_id"], min(seen.get(s["object_id"], r["time"]), r["time"]))
    return seen


def main() -> int:
    for filtered in (False, True):
        for day in DAYS:
            what = ("before any sighting of it that day" if filtered
                    else "whether or not it had already been seen that day")
            print(f"\n===== day {day}: the first question about each object, {what}")
            print(f"  {'method':20s} {'kept':>5s} {'dropped':>8s}  {'first room right':>17s} "
                  f"{'found within 3':>15s}   per household, first room right")
            for name, arm_dir in ARMS:
                kept_all, dropped_all, per_first, per_found = 0, 0, [], []
                for home in D.HOMES_50:
                    movers = D.both_spell_movers(home)
                    seen = first_sighting_times(arm_dir, home, day)
                    firsts = {}
                    for r in D.rows(D.WAVE_50, arm_dir, home):
                        if r["day"] != day or r["object_id"] not in movers:
                            continue
                        o = r["object_id"]
                        if o not in firsts or r["time"] < firsts[o]["time"]:
                            firsts[o] = r
                    kept = [r for o, r in firsts.items()
                            if not filtered or o not in seen or seen[o] >= r["time"]]
                    kept_all += len(kept)
                    dropped_all += len(firsts) - len(kept)
                    if kept:
                        per_first.append(100 * sum(1 for r in kept
                                                   if r.get("found_at_step") == 1) / len(kept))
                        per_found.append(100 * sum(1 for r in kept
                                                   if r.get("found_it")) / len(kept))
                shown = "  ".join(f"{v:.0f}" for v in per_first)
                print(f"  {name:20s} {kept_all:5d} {dropped_all:8d}  "
                      f"{statistics.mean(per_first):17.1f} "
                      f"{statistics.mean(per_found):15.1f}   {shown}")
    print("\n  'kept' counts object-days over the three households; 'dropped' are the objects the "
          "robot\n  had already seen that day, while answering an earlier question, before it was "
          "first asked\n  about them. Every room opening records every object in the room, which "
          "is why the filter\n  removes most of the sample.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
