"""Why did the memory answer wrong? Three faults, and they need different fixes.

Scoring BELOW the trivial "each object's commonest settled place" rule at the
control freeze point is close to self-contradictory: at that point the notes were
written from thirteen ordinary days of looking, and the floor is very nearly what
thirteen ordinary days should have taught. A memory built from exactly that evidence
landing fifteen points under it is far more easily explained by the read window
hiding the claim than by the claim being wrong. That is why this diagnostic exists,
and it costs no GPU at all: the full store and the lines actually read are both
already on disk, and the window is recomputed deterministically.

Every wrong answer falls into exactly one of three buckets:

  the selection rule   a claim naming the true place WAS in the store but was not
                       among the lines the model was shown. The fault is retrieval,
                       and a bigger budget would be a crude fix for it.
  the point of use     a claim naming the true place WAS shown and the model
                       answered against it anyway. That is a finding, not a bug -
                       the same read-time failure a previous study measured at 807
                       of 890 questions.
  write time           no claim named the true place at all. Neither a bigger
                       budget nor a better selection rule can help.

    python -m self_improve.diagnose_the_read_path \
        --results results/self_improve/frozen_memory_test_v1
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence

from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.measure_timeliness import (FIRST_DISRUPTED_DAY, the_notes_assert,
                                             where_the_moved_things_went)
from self_improve.memory_notes import Notes, summary_lines
from self_improve.study_settings import LOCKED

SELECTION = "the selection rule: the right claim was in the store but not in the window"
USE = "the point of use: the right claim was shown and the model answered against it"
WRITE = "write time: no claim named the true place at all"
WRITE_UNAVOIDABLE = ("write time, but unavoidable here: the thing moved AFTER these "
                     "notes were frozen, so no claim could have named the new place")


def lines_of(notes: Notes) -> List[str]:
    """Every line of the store, in the same unit the budget counts in."""
    if notes.how_memory_is_written == "wholesale rewrite":
        return summary_lines(notes.newest_summary() or "")
    return [c.as_plain_words() for c in notes.claims]


def partition_one_arm(notes: Notes, answers: Sequence[Dict[str, Any]],
                      household: FrozenHousehold, read_budget_lines: int,
                      level: str = "the exact shelf") -> Dict[str, Any]:
    """Partition the wrong answers at one level.

    THE LEVEL CHANGES THE ANSWER COMPLETELY and both readings are meaningful, so both are
    reported rather than one being chosen:

      at THE EXACT SHELF - take answers that named the wrong shelf, and ask whether any
      line named the true shelf. Almost none do, so almost every error is write-time: the
      notes do not hold the right shelf, and reading is not the bottleneck.

      at THE RIGHT ROOM - take answers that named the wrong ROOM, and ask whether any line
      placed the object in the right room. Many do, so a large share of room-level errors
      happen despite the notes carrying the right room, and there reading IS losing
      information.
    """
    everything = lines_of(notes)
    # A freeze point can ask about days the notes have not seen. At the control point
    # the notes stop at day 13 and the questions come from days 14-23, so for every
    # object the disruption moved there is no claim that COULD name the true place.
    # Counting those as a write-time fault would blame the memory for not being
    # clairvoyant, so they are split out.
    moved_after_the_notes_were_frozen = set()
    if notes.written_up_to_day < FIRST_DISRUPTED_DAY:
        moved_after_the_notes_were_frozen = set(where_the_moved_things_went(household))
    buckets: collections.Counter = collections.Counter()
    examples: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)

    from self_improve.score_at_both_levels import room_of
    at_room_level = level == "the right room"

    for answer in answers:
        object_id, true_place = answer["object_id"], answer.get("true_place")
        if not true_place:
            continue
        said = answer.get("answer_place")
        if at_room_level:
            # wrong only if it named the wrong ROOM
            if said is not None and room_of(household, said) == room_of(household, true_place):
                continue
        elif answer.get("correct") is not False:
            continue
        # Recomputed exactly as the answer prompt built it, so "the window" here is
        # the window the model actually saw.
        window = notes.what_the_robot_can_read(read_budget_lines,
                                               about_object=object_id).text.splitlines()
        # Strict place matching: the question is whether a line named the TRUE SHELF, so
        # a line naming only the right room does not count. See the note in
        # measure_timeliness.the_notes_assert.
        # At shelf level a line must name the true SHELF. At room level a line placing the
        # object anywhere in the true room counts, which is what the room fallback does.
        strict = not at_room_level
        in_window = any(the_notes_assert(line, object_id, true_place, household, not strict)
                        for line in window)
        in_store = any(the_notes_assert(line, object_id, true_place, household, not strict)
                       for line in everything)
        if in_window:
            bucket = USE
        elif in_store:
            bucket = SELECTION
        elif object_id in moved_after_the_notes_were_frozen:
            bucket = WRITE_UNAVOIDABLE
        else:
            bucket = WRITE
        buckets[bucket] += 1
        if len(examples[bucket]) < 3:
            examples[bucket].append({
                "object_id": object_id, "true_place": true_place,
                "the_arm_said": answer["answer_place"],
                "n_lines_in_the_store": len(everything),
                "n_lines_in_the_window": len(window)})

    # The same recovery diagnostic that licenses the vacuity comparison: if facts are
    # recovered from one arm's lines far more readily than the other's, the partition is
    # partly measuring the extractor rather than the memory.
    from self_improve.write_the_notes import facts_a_statement_asserts
    lines_yielding_a_fact = sum(
        1 for line in everything
        if facts_a_statement_asserts(line, household.asked_objects, household.places,
                                     household.place_room))

    n_wrong = sum(buckets.values())
    return {
        "n_lines_in_the_store_yielding_any_fact": lines_yielding_a_fact,
        "share_of_lines_yielding_any_fact":
            (lines_yielding_a_fact / len(everything)) if everything else None,
        "n_answers": len(answers),
        "n_wrong": n_wrong,
        "n_lines_in_the_store": len(everything),
        "read_budget_lines": read_budget_lines,
        "shares": {bucket: buckets[bucket] / n_wrong
                   for bucket in (SELECTION, USE, WRITE, WRITE_UNAVOIDABLE)}
                  if n_wrong else {},
        "counts": {bucket: buckets[bucket]
                   for bucket in (SELECTION, USE, WRITE, WRITE_UNAVOIDABLE)},
        "n_wrong_that_were_avoidable": n_wrong - buckets[WRITE_UNAVOIDABLE],
        "examples": dict(examples),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/frozen_memory_test_v1"))
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--read-budget-lines", type=int, default=LOCKED.read_budget_lines)
    parser.add_argument("--level", default="the exact shelf",
                        choices=["the exact shelf", "the right room"])
    parser.add_argument("--freeze-point", default=None,
                        help="restrict to one freeze point, e.g. the decisive one")
    parser.add_argument("--out", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    households: Dict[str, FrozenHousehold] = {}
    rows = []
    for answers_file in sorted(args.results.rglob("held_out_answers.json")):
        cell = answers_file.parent
        notes_file = cell / "notes_as_frozen.json"
        if not notes_file.exists():
            continue
        payload = json.loads(answers_file.read_text())
        if args.freeze_point and payload["freeze_point"] != args.freeze_point:
            continue
        name = payload["household"]
        if name not in households:
            households[name] = FrozenHousehold(args.banks / f"{name}.jsonl")
        notes = Notes.load(notes_file)
        report = partition_one_arm(notes, payload["answers"], households[name],
                                   args.read_budget_lines, args.level)
        which_arm = ("incremental edits" if "incremental" in cell.parent.name
                     else "wholesale rewrite" if "wholesale" in cell.parent.name
                     else "unknown")
        report.update({"household": name, "arm": payload["arm"],
                       "which_arm": which_arm,
                       "freeze_point": payload["freeze_point"],
                       "share_correct": payload["share_correct"]})
        rows.append(report)

    if not rows:
        print(f"no answer sets under {args.results} yet")
        return 0

    for r in rows:
        print(f"{r['household']} | {r['arm']} | {r['freeze_point']}")
        print(f"   {r['share_correct']:.0%} correct, {r['n_wrong']} wrong of {r['n_answers']}, "
              f"store holds {r['n_lines_in_the_store']} lines and the window shows "
              f"{r['read_budget_lines']}")
        for bucket, share in r["shares"].items():
            print(f"     {share:5.0%}  {bucket}")

    # Per arm as well as pooled, because an asymmetry in the point-of-use share would be
    # a finding in its own right and an extractor artefact otherwise.
    print()
    print("EXTRACTOR EVEN-HANDEDNESS, per arm: the share of stored lines from which any "
          "fact is recovered. If these are close, the partition is trustworthy for the "
          "same reason the vacuity number is.")
    for arm in sorted({r.get("which_arm") for r in rows if r.get("which_arm")}):
        here = [r for r in rows if r.get("which_arm") == arm]
        shares = [r["share_of_lines_yielding_any_fact"] for r in here
                  if r["share_of_lines_yielding_any_fact"] is not None]
        if shares:
            print(f"  {arm:20s} {statistics.fmean(shares):.0%} of lines yield a fact "
                  f"(worst cell {min(shares):.0%}), {len(here)} cells")
    print()
    for arm in sorted({r.get("which_arm") for r in rows if r.get("which_arm")}):
        here = [r for r in rows if r.get("which_arm") == arm]
        sub = collections.Counter()
        for r in here:
            sub.update(r["counts"])
        n = sum(sub.values())
        avoidable = n - sub[WRITE_UNAVOIDABLE]
        print(f"--- {arm}: {n} wrong answers across {len(here)} cells")
        for bucket in (SELECTION, USE, WRITE, WRITE_UNAVOIDABLE):
            print(f"     {sub[bucket] / n:5.0%}  {bucket}" if n else "")
        if avoidable:
            print(f"     of the {avoidable} avoidable: {sub[USE] / avoidable:.0%} point of "
                  f"use, {sub[WRITE] / avoidable:.0%} write time, "
                  f"{sub[SELECTION] / avoidable:.0%} selection")
    print()

    totals = collections.Counter()
    for r in rows:
        totals.update(r["counts"])
    grand = sum(totals.values())
    if grand:
        print()
        print(f"across {len(rows)} arm(s), {grand} wrong answers:")
        for bucket in (SELECTION, USE, WRITE, WRITE_UNAVOIDABLE):
            print(f"  {totals[bucket] / grand:5.0%}  {bucket}")
        avoidable = grand - totals[WRITE_UNAVOIDABLE]
        if avoidable:
            print()
            print(f"of the {avoidable} wrong answers that were avoidable at all:")
            for bucket in (SELECTION, USE, WRITE):
                print(f"  {totals[bucket] / avoidable:5.0%}  {bucket}")
            biggest = max((SELECTION, USE, WRITE), key=lambda b: totals[b])
            print()
            print(f"dominant avoidable fault: {biggest}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps({"per_arm": rows, "totals": dict(totals)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
