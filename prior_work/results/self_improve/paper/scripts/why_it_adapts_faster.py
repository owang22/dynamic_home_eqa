#!/usr/bin/env python3
"""Why the log-and-summary memory comes back faster after a change. Three measurements.

The obvious explanation - it generalises from a few objects to the rest - is WRONG, and the
paired test says so: on the questions where neither memory has yet seen the object in the place it
now is, the two score identically. What actually happens is in the second and third looks.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/why_it_adapts_faster.py
"""
import statistics
import sys
import pathlib

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import paper_data as D                                             # noqa: E402

RULE, OURS = "last_seen_no_model", "the_log_and_notes_about_the_routine"


def main() -> int:
    print("1. On the day the change begins, neither can PREDICT the new room.")
    print("   Paired, on the questions where neither had ever seen the object where it now is:")
    per = []
    for home in D.HOMES_50:
        both = D.both_spell_movers(home)
        a = {r["question_id"]: r for r in D.rows(D.WAVE_50, RULE, home)
             if r["day"] in range(14, 18) and r["object_id"] in both}
        b = {r["question_id"]: r for r in D.rows(D.WAVE_50, OURS, home)
             if r["day"] in range(14, 18) and r["object_id"] in both}
        qs = [q for q in a if q in b and a[q].get("times_seen_there_before", 0) == 0
              and b[q].get("times_seen_there_before", 0) == 0]
        if len(qs) < 4:
            continue
        per.append((100 * sum(1 for q in qs if a[q].get("found_at_step") == 1) / len(qs),
                    100 * sum(1 for q in qs if b[q].get("found_at_step") == 1) / len(qs), len(qs)))
    print(f"     last-seen {statistics.mean([x for x, _, _ in per]):.1f}%   "
          f"log and notes {statistics.mean([y for _, y, _ in per]):.1f}%   "
          f"({sum(n for _, _, n in per)} questions) - identical\n")

    print("2. But given three rooms, one of them FINDS it on the day of the change.")
    for name, arm in (("last-seen", RULE), ("log and notes", OURS)):
        first, found = [], []
        for home in D.HOMES_50:
            both = D.both_spell_movers(home)
            rs = [r for r in D.rows(D.WAVE_50, arm, home)
                  if r["day"] == 14 and r["object_id"] in both]
            first.append(100 * sum(1 for r in rs if r.get("found_at_step") == 1) / len(rs))
            found.append(100 * sum(1 for r in rs if r.get("found_it")) / len(rs))
        print(f"     {name:16s} day 14: first room right {statistics.mean(first):.0f}%, "
              f"found within three rooms {statistics.mean(found):.0f}%")

    print("\n3. So by the next three days it has already SEEN the objects where they now are.")
    for name, arm in (("last-seen", RULE), ("log and notes", OURS),
                      ("claim store", "incremental_edits"), ("ACE-style", "ACE_as_published")):
        share, acc = [], []
        for home in D.HOMES_50:
            both = D.both_spell_movers(home)
            rs = [r for r in D.rows(D.WAVE_50, arm, home)
                  if r["day"] in range(15, 18) and r["object_id"] in both]
            share.append(100 * sum(1 for r in rs
                                   if r.get("times_seen_there_before", 0) >= 1) / len(rs))
            acc.append(100 * sum(1 for r in rs if r.get("found_at_step") == 1) / len(rs))
        print(f"     {name:16s} days 15-17: had already seen it there on "
              f"{statistics.mean(share):.0f}% of questions, first room right "
              f"{statistics.mean(acc):.0f}%")
    print("\n   The claim store has the same exposure and does not convert it: seeing the new "
          "place\n   is necessary and not sufficient.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
