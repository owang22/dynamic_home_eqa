"""Of the facts the robot saw repeatedly and got wrong: never written, or displaced?

The notes did not carry `glass_yuki on kitchen_table_k1`, an object this arm had seen
at that exact shelf five times and in that room thirty-seven times. There are two
quite different reasons and they point at opposite remedies:

  NEVER WRITTEN        the writer saw it and never recorded it. A SELECTION failure.
                       No larger budget helps.
  WRITTEN AND GONE     it went in, and a later night's rewrite pushed it out. A
                       CAPACITY failure of the artifact.
  OUTSIDE THE WINDOW   it is still in the notes, but the 8-line read window did not
                       show it for this question. A CAPACITY failure of the read.
  IN THE WINDOW        it was right there in the prompt and the answer was still
                       wrong. Neither: the model ignored its own notes.

That is the difference between "language models are bad at deciding what to record"
and "eight lines is too few for a house", and they are different papers.

Both formats keep their own per-night history, so the notes state at any day is
reconstructed exactly rather than guessed: the wholesale arm keeps every night's
summary in `nightly_summaries`, and the claim store keeps every previous wording in
each claim's `revision_history`, so replaying the revisions that happened AFTER a day
recovers what the claim said ON that day.

A WARNING ABOUT METHOD, because it is the one measure in this strand that needs it.
Everything else here is computed from structured sighting records. Deciding whether a
line of prose asserts "glass_yuki is on kitchen_table_k1" cannot be. We use
`write_the_notes.facts_a_statement_asserts`, the matcher this project has already
audited and repaired - whole-word matching, the person-possessive forms the rewrite
arm actually writes, underscore-flattening, and a room requirement where bare place
words are ambiguous across rooms. Its known failure mode is to MISS an assertion
worded in a way it does not recognise, which would inflate "never written". So that
bucket is an upper bound and the two capacity buckets are lower bounds, and the
verdict should only be believed if it is not close.

    python -m self_improve.never_written_or_displaced --days 14 23
"""
from __future__ import annotations

import argparse
import collections
import copy
import json
import pathlib
from typing import Any, Dict, List, Optional, Sequence, Tuple

from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.memory_notes import Claim, Notes, summary_lines
from self_improve.study_settings import LOCKED
from self_improve.write_the_notes import facts_a_statement_asserts

NEVER_WRITTEN = "never written: a selection failure, no budget helps"
WRITTEN_AND_GONE = "written and gone: the artifact lost it"
OUTSIDE_THE_WINDOW = "in the notes but outside the read window"
IN_THE_WINDOW = "in the read window and the answer was still wrong"
BUCKETS = (NEVER_WRITTEN, WRITTEN_AND_GONE, OUTSIDE_THE_WINDOW, IN_THE_WINDOW)


def the_notes_as_they_stood(notes: Notes, day: int) -> Notes:
    """The notes exactly as they were at the end of `day`.

    For the wholesale arm: the newest summary written on or before that day.
    For the claim store: every claim first written on or before that day, with any
    revision made AFTER that day undone - walking the revision history backwards and
    restoring the earliest `was` recorded after the day.
    """
    rebuilt = Notes(notes.path, notes.household, notes.arm, notes.how_memory_is_written)
    rebuilt.written_up_to_day = day
    if notes.how_memory_is_written == "wholesale rewrite":
        rebuilt.nightly_summaries = [s for s in notes.nightly_summaries
                                     if s["day"] <= day]
        return rebuilt
    for claim in notes.claims:
        if claim.first_written_day > day:
            continue
        older = copy.deepcopy(claim)
        later = sorted((r for r in claim.revision_history if r["day"] > day),
                       key=lambda r: (r["day"], r["time"]))
        if later:
            was = later[0]["was"]
            older.statement = was.get("statement", older.statement)
            older.holds_under = was.get("holds_under", older.holds_under)
            older.status = was.get("status", older.status)
            older.standing = was.get("standing", older.standing)
        older.revision_history = [r for r in claim.revision_history if r["day"] <= day]
        # Which side of the working memory it was on THAT DAY, not at the end of the run.
        # The flag on the claim only ever describes the end, so a note promoted on day 28
        # appeared for free in a day-23 snapshot and one evicted by day 31 wrongly needed a
        # search in that same snapshot. A check that rebuilds at the LAST day cannot see
        # this, because there the two agree - which is why it went unnoticed.
        older.moved_between_memory_and_archive = [
            m for m in claim.moved_between_memory_and_archive if m["day"] <= day]
        older.in_working_memory = notes.was_it_in_working_memory_on(claim, day)
        older.last_revised_day = (older.revision_history[-1]["day"]
                                  if older.revision_history else claim.first_written_day)
        rebuilt.claims.append(older)
    return rebuilt


def lines_ever_written_up_to(notes: Notes, day: int) -> List[str]:
    """Every line the notes have EVER held on or before this day, including wordings
    since replaced and summaries since rewritten. This is what makes "it went in and
    was pushed out" distinguishable from "it never went in"."""
    lines: List[str] = []
    if notes.how_memory_is_written == "wholesale rewrite":
        for night in notes.nightly_summaries:
            if night["day"] <= day:
                lines += summary_lines(night["summary"])
        return lines
    for claim in notes.claims:
        if claim.first_written_day > day:
            continue
        lines.append(claim.statement)
        for revision in claim.revision_history:
            if revision["day"] <= day:
                was = revision.get("was") or {}
                if was.get("statement"):
                    lines.append(was["statement"])
    return lines


def does_it_assert(lines: Sequence[str], object_id: str, place_id: str,
                   household: FrozenHousehold) -> bool:
    for line in lines:
        if (object_id, place_id) in facts_a_statement_asserts(
                line, [object_id], [place_id], household.place_room):
            return True
    return False


def was_it_true_when_it_was_written(notes: Notes, household: FrozenHousehold,
                                    object_id: str, place_id: str, up_to_day: int
                                    ) -> Optional[bool]:
    """For a fact that was written and then dropped: was it TRUE on the night it was
    written, or did it only become true later?

    This is the difference between a strong claim and a hedged one. "It dropped a fact
    that was true at the time" is what a reader will take "the artifact lost its own
    evidence" to mean. "It dropped a fact that later became true again" still supports
    the architecture criticism, but not that sentence.

    True if the fact held at ANY of the nights it was written - checked against the
    household's own truth at that night's moment, not against a later state of the
    world. None if we cannot find a night that asserted it.
    """
    nights: List[Tuple[int, List[str]]] = []
    if notes.how_memory_is_written == "wholesale rewrite":
        nights = [(night["day"], summary_lines(night["summary"]))
                  for night in notes.nightly_summaries if night["day"] <= up_to_day]
    else:
        for claim in notes.claims:
            if claim.first_written_day > up_to_day:
                continue
            nights.append((claim.first_written_day, [claim.statement]))
            for revision in claim.revision_history:
                if revision["day"] <= up_to_day:
                    was = (revision.get("was") or {}).get("statement")
                    if was:
                        nights.append((revision["day"], [was]))
    any_night = False
    for day, lines in nights:
        if not does_it_assert(lines, object_id, place_id, household):
            continue
        any_night = True
        # was it there at the moment the note was written, 23:30 that night
        at_time = day * 86400 + 23 * 3600 + 30 * 60
        if household.place_of_object(object_id, at_time) == place_id:
            return True
    return False if any_night else None


def split_one_cell(cell_dir: pathlib.Path, household: FrozenHousehold,
                   days: range, at_least_this_many_sightings: int = 2
                   ) -> Optional[Dict[str, Any]]:
    cell_file = cell_dir / "cell.json"
    notes_file = cell_dir / "notes.json"
    if not cell_file.exists() or not notes_file.exists():
        return None
    cell = json.loads(cell_file.read_text())
    notes = Notes.load(notes_file)
    movers = set(cell["movers"])
    buckets: collections.Counter = collections.Counter()
    trajectory: collections.Counter = collections.Counter()
    examples: Dict[str, List[str]] = collections.defaultdict(list)

    for row in cell["searches"]:
        if row["day"] not in days or row["object_id"] not in movers:
            continue
        if row.get("correct_place") is not False or not row.get("true_place"):
            continue
        if row.get("times_seen_there_before", 0) < at_least_this_many_sightings:
            continue
        object_id, true_place = row["object_id"], row["true_place"]
        # the notes as they stood the night before this question was asked
        as_they_stood = the_notes_as_they_stood(notes, row["day"] - 1)
        window = as_they_stood.what_the_robot_can_read(
            LOCKED.read_budget_lines, about_object=object_id).text.splitlines()
        if does_it_assert(window, object_id, true_place, household):
            bucket = IN_THE_WINDOW
        else:
            everything_now = (summary_lines(as_they_stood.newest_summary() or "")
                              if notes.how_memory_is_written == "wholesale rewrite"
                              else [c.statement for c in as_they_stood.claims])
            if does_it_assert(everything_now, object_id, true_place, household):
                bucket = OUTSIDE_THE_WINDOW
            elif does_it_assert(lines_ever_written_up_to(notes, row["day"] - 1),
                                object_id, true_place, household):
                bucket = WRITTEN_AND_GONE
                was_true = was_it_true_when_it_was_written(
                    notes, household, object_id, true_place, row["day"] - 1)
                trajectory[("true when written" if was_true else
                            "only became true later" if was_true is False
                            else "could not tell")] += 1
            else:
                bucket = NEVER_WRITTEN
        buckets[bucket] += 1
        if len(examples[bucket]) < 3:
            examples[bucket].append(
                f"day {row['day']} {object_id} on {true_place}, seen there "
                f"{row['times_seen_there_before']}x, answered {row['answer_place']}")

    n = sum(buckets.values())
    if not n:
        return None
    return {
        "household": household.name,
        "sensing_arm": cell["sensing_arm"],
        "how_memory_is_written": cell["how_memory_is_written"],
        "n_wrong_on_things_it_had_seen_at_least_twice": n,
        "counts": {b: buckets[b] for b in BUCKETS},
        "shares": {b: buckets[b] / n for b in BUCKETS},
        "of_the_written_and_gone_was_it_true_when_written": dict(trajectory),
        "examples": dict(examples),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/search_driven"))
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--days", type=int, nargs=2, default=[14, 23])
    parser.add_argument("--min-sightings", type=int, default=2)
    parser.add_argument("--out", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    days = range(args.days[0], args.days[1] + 1)
    households: Dict[str, FrozenHousehold] = {}
    rows: List[Dict[str, Any]] = []
    for cell_file in sorted(args.root.rglob("cell.json")):
        cell_dir = cell_file.parent
        name = json.loads(cell_file.read_text())["household"]
        if name not in households:
            households[name] = FrozenHousehold(args.banks / f"{name}.jsonl")
        got = split_one_cell(cell_dir, households[name], days, args.min_sightings)
        if got:
            got["where"] = str(cell_dir)
            rows.append(got)

    if not rows:
        print(f"no finished cells under {args.root} with a qualifying error yet")
        return 0

    print(f"\n=== days {args.days[0]}-{args.days[1]}, movers, WRONG ANSWERS on objects "
          f"the robot had already seen at that exact shelf at least "
          f"{args.min_sightings} times ===")
    print("Selection failure vs capacity failure. The matcher caveat is in the module "
          "docstring:\n'never written' is an UPPER bound and the capacity buckets are "
          "LOWER bounds.\n")
    by_format: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        by_format[row["how_memory_is_written"]].append(row)
    summary: Dict[str, Any] = {}
    for how, here in sorted(by_format.items()):
        totals: collections.Counter = collections.Counter()
        for row in here:
            for b in BUCKETS:
                totals[b] += row["counts"][b]
        n = sum(totals.values())
        print(f"--- {how}: {n} errors across {len(here)} cells, "
              f"{len({r['household'] for r in here})} households")
        for b in BUCKETS:
            print(f"      {totals[b] / n:6.1%}  ({totals[b]:3d})  {b}")
        selection = totals[NEVER_WRITTEN] / n
        capacity = (totals[WRITTEN_AND_GONE] + totals[OUTSIDE_THE_WINDOW]) / n
        print(f"      -> at most {selection:.0%} selection, at least {capacity:.0%} "
              f"capacity, {totals[IN_THE_WINDOW] / n:.0%} ignored its own notes")
        traj: collections.Counter = collections.Counter()
        for row in here:
            traj.update(row["of_the_written_and_gone_was_it_true_when_written"])
        n_traj = sum(traj.values())
        if n_traj:
            print(f"      of the {n_traj} 'written and gone', was the fact TRUE on a "
                  f"night it was written?")
            for k in ("true when written", "only became true later", "could not tell"):
                if traj[k]:
                    print(f"         {traj[k] / n_traj:6.1%}  ({traj[k]:3d})  {k}")
            strong = traj["true when written"] / n
            print(f"      -> {strong:.0%} of ALL errors are facts it held WHILE TRUE "
                  f"and then dropped")
        summary[how] = {"n_errors": n, "n_cells": len(here),
                        "of_the_written_and_gone_was_it_true_when_written": dict(traj),
                        "share_of_all_errors_that_were_dropped_while_true":
                            (traj["true when written"] / n) if n else None,
                        "n_households": len({r["household"] for r in here}),
                        "counts": {b: totals[b] for b in BUCKETS},
                        "shares": {b: totals[b] / n for b in BUCKETS},
                        "at_most_this_share_is_selection": selection,
                        "at_least_this_share_is_capacity": capacity}
        example = next((r for r in here if r["examples"].get(NEVER_WRITTEN)), None)
        if example:
            print(f"      examples of never written ({example['household']}, "
                  f"{example['sensing_arm']}):")
            for e in example["examples"][NEVER_WRITTEN]:
                print(f"         {e}")
        print()

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(
            {"days": args.days, "min_sightings": args.min_sightings,
             "per_format": summary, "per_cell": rows}, indent=1))
        print(f"written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
