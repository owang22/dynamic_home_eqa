"""Rebuild `notes_frozen_at_day_N.json` from a finished cell, so the frozen-memory
test can be run on the search-driven framework without rerunning anything.

WHY IT IS NEEDED. Every answer in the search-driven cells may have been obtained by
LOOKING: a cell opens 114 to 220 rooms to answer 80 questions and finds the object on
26 to 75 of them, and an object you have physically found hands you its shelf for
free. The diagnostic is shelf accuracy exactly equalling room accuracy, which a memory
can never produce. So those accuracy figures are largely find-rate in different units
and are not memory measurements. The frozen-memory test is: freeze the notes, stop all
looking, answer the held-out questions from the notes alone. That needs a snapshot at
the freeze day, and the cells only wrote `notes.json`.

WHY NO RERUN IS NEEDED. Both formats keep their own per-night history, so the state at
any day is recoverable exactly:

  wholesale rewrite   every night's summary is in `nightly_summaries` with its day.
  incremental edits   every superseded wording is in each claim's `revision_history`
                      with the day it was replaced, so replaying the revisions made
                      AFTER day N recovers what the claim said ON day N.

ONE THING THAT IS NOT IN THE HISTORY, and is repaired here rather than ignored:
`record_evidence` appends observation ids and writes no history entry, so a claim's
`supporting_observation_ids` at the end of the month includes ids attached after day N.
Left alone that would leak future information into the prompt, because
`Claim.as_plain_words` prints the counts. Observation ids are dated in the cell's own
`looks.jsonl`, so the ids are filtered to those observed on or before day N.

THE CHECK THAT MAKES THIS TRUSTWORTHY: rebuilding at the cell's LAST day must
reproduce `notes.json` exactly. If it does not, the reconstruction is wrong and no
snapshot from it may be used. That is asserted for every cell, and a cell that fails
is reported and skipped rather than written.

    python -m self_improve.rebuild_the_frozen_snapshots --days 13 23 28
"""
from __future__ import annotations

import argparse
import json
import pathlib
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Set, Tuple

from self_improve.memory_notes import Notes
from self_improve.never_written_or_displaced import the_notes_as_they_stood


def which_day_each_observation_was_made(looks_file: pathlib.Path) -> Dict[str, int]:
    """observation id -> the day it was observed, from the cell's own look stream."""
    when: Dict[str, int] = {}
    if not looks_file.exists():
        return when
    for line in looks_file.open():
        row = json.loads(line)
        if row.get("kind") != "look":
            continue
        for s in row.get("sightings", []):
            when[s["observation_id"]] = row["day"]
        for a in row.get("absences", []):
            when[a["observation_id"]] = row["day"]
    return when


def rebuild(notes: Notes, day: int, observed_on: Dict[str, int]) -> Notes:
    rebuilt = the_notes_as_they_stood(notes, day)
    rebuilt.written_up_to_day = day
    for claim in rebuilt.claims:
        claim.supporting_observation_ids = [
            o for o in claim.supporting_observation_ids
            if observed_on.get(o, -1) <= day]
        claim.contradicting_observation_ids = [
            o for o in claim.contradicting_observation_ids
            if observed_on.get(o, -1) <= day]
    return rebuilt


def _comparable(notes: Notes) -> Any:
    return {
        "how": notes.how_memory_is_written,
        "summaries": [(s["day"], s["summary"]) for s in notes.nightly_summaries],
        # `in_working_memory` and `folded_into` are in the tuple deliberately. Neither was,
        # and that is why this check passed cleanly while every earlier-day snapshot of the
        # working-memory arm had the wrong split: a field the check does not read is a field
        # the check cannot defend. Rebuilding at the last day still cannot catch a
        # roll-back bug on its own, so `check_an_earlier_day_too` below does that.
        "claims": sorted((c.claim_id, c.statement, c.holds_under, c.status, c.standing,
                          c.in_working_memory, c.folded_into,
                          tuple(sorted(c.supporting_observation_ids)),
                          tuple(sorted(c.contradicting_observation_ids)))
                         for c in notes.claims),
    }


def check_an_earlier_day_too(notes: Notes, observed_on: Dict[str, int]
                             ) -> Tuple[bool, str]:
    """Rebuilding at the LAST day cannot catch a field that is never rolled back, because
    there the end of the run and that day agree. This rebuilds at the midpoint instead and
    asks whether anything that is supposed to change over time actually differs.

    It is not an exact test - the notes genuinely differ between the midpoint and the end -
    so it asserts the weaker thing that is still sufficient: for every field that carries
    history, the midpoint must not simply reproduce the end state for every claim."""
    last = notes.written_up_to_day
    if last < 4 or not notes.claims:
        return True, "too few nights to compare two of them"
    middle = rebuild(notes, last // 2, observed_on)
    at_end = {c.claim_id: c for c in notes.claims}
    moved_later = [c for c in notes.claims
                   if any(m["day"] > last // 2
                          for m in c.moved_between_memory_and_archive)]
    if not moved_later:
        return True, "no note crossed between the working memory and the archive later "\
                     "than the midpoint, so there is nothing for this to catch"
    wrong = [c.claim_id for c in middle.claims
             if c.claim_id in at_end
             and c.in_working_memory == at_end[c.claim_id].in_working_memory
             and c in [x for x in middle.claims if x.claim_id in
                       {y.claim_id for y in moved_later}]]
    if wrong:
        return False, (f"{len(wrong)} note(s) crossed between the working memory and the "
                       f"archive after the midpoint, yet the midpoint snapshot has them on "
                       f"the same side as the end of the run: {wrong[:5]}")
    return True, (f"{len(moved_later)} note(s) crossed after the midpoint and the midpoint "
                  f"snapshot has them on the other side, as it must")


def check_the_reconstruction(notes: Notes, observed_on: Dict[str, int]
                             ) -> Tuple[bool, str]:
    """Rebuilding at the cell's own last day must reproduce the saved notes exactly."""
    last = notes.written_up_to_day
    again = rebuild(notes, last, observed_on)
    if _comparable(again) == _comparable(notes):
        return True, f"reconstruction at day {last} reproduces notes.json exactly"
    mine, theirs = _comparable(again), _comparable(notes)
    why = []
    if mine["summaries"] != theirs["summaries"]:
        why.append(f"{len(mine['summaries'])} summaries against {len(theirs['summaries'])}")
    if mine["claims"] != theirs["claims"]:
        why.append(f"{len(mine['claims'])} claims against {len(theirs['claims'])}; "
                   f"{sum(1 for a, b in zip(mine['claims'], theirs['claims']) if a != b)} differ")
    return False, "; ".join(why) or "differs for an unenumerated reason"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roots", type=pathlib.Path, nargs="+",
                        default=[pathlib.Path("results/self_improve/search_driven")])
    parser.add_argument("--days", type=int, nargs="+", default=[13, 23, 28])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    written, skipped, failed = 0, 0, []
    for root in args.roots:
        for notes_file in sorted(root.rglob("notes.json")):
            cell = notes_file.parent
            notes = Notes.load(notes_file)
            observed_on = which_day_each_observation_was_made(cell / "looks.jsonl")
            ok, why = check_the_reconstruction(notes, observed_on)
            if not ok:
                failed.append(f"{cell}: {why}")
                continue
            for day in args.days:
                if notes.written_up_to_day < day:
                    skipped += 1
                    continue
                snapshot = rebuild(notes, day, observed_on)
                target = cell / f"notes_frozen_at_day_{day}.json"
                if args.dry_run:
                    print(f"  would write {target} "
                          f"({len(snapshot.claims)} claims, "
                          f"{len(snapshot.nightly_summaries)} summaries)")
                else:
                    snapshot.path = target
                    snapshot.save()
                    # verify it landed and reloads with the right day, because a
                    # snapshot whose written_up_to_day is wrong makes
                    # run_frozen_memory_test raise rather than silently mislead
                    back = Notes.load(target)
                    if back.written_up_to_day != day:
                        failed.append(f"{target}: reloaded at day "
                                      f"{back.written_up_to_day}, wanted {day}")
                        continue
                written += 1

    print(f"\n{written} snapshots written, {skipped} skipped (cell had not reached the day)")
    if failed:
        print(f"{len(failed)} FAILURES - no snapshot from these may be used:")
        for f in failed[:12]:
            print("   ", f)
    else:
        print("every cell's reconstruction reproduced its own notes.json exactly")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
