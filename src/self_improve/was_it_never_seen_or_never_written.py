"""The write-time errors split three ways: did the robot ever SEE the thing where it was?

98% of wrong answers are write-time failures - no line of the notes names the true shelf.
That is compatible with two completely different papers:

  the robot **never saw** the object at its true place, in which case no note-writing policy
  of any kind could have recorded it, and the bottleneck is **observation**;

  the robot **did see** it and the notes do not carry it, in which case the bottleneck is
  **note-taking** on evidence the robot actually had.

At one room per day the first is very plausible, and the two lead to opposite framings, so it
is worth a number rather than a guess. Everything needed is already on disk: each arm's own
`looks.jsonl` records every sighting it made.

The split, for each write-time error, counting sightings of that object at that exact place
on or before the freeze day:

  0 sightings   a sensing failure - unfixable by any memory format
  1 sighting    a note-taking failure - the memory dropped an observation it made
  2 or more     the strongest form of note-taking failure

Reported pooled and per arm.

    python -m self_improve.was_it_never_seen_or_never_written
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
from typing import Any, Dict, List, Optional

from self_improve.diagnose_the_read_path import lines_of
from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.measure_timeliness import the_notes_assert
from self_improve.memory_notes import Notes
from self_improve.score_at_both_levels import looks_file_for
from self_improve.study_settings import LOCKED

NEVER_SAW_IT = "a sensing failure: the robot never saw it there at all"
SAW_IT_ONCE = "a note-taking failure: seen there once, and no line names it"
SAW_IT_OFTEN = "a note-taking failure: seen there more than once, and no line names it"


def sightings_by_object_and_place(looks_file: pathlib.Path, up_to_day: int
                                  ) -> Dict[tuple, int]:
    """How many times this arm saw each object at each place, on or before a day."""
    counts: collections.Counter = collections.Counter()
    if looks_file and looks_file.exists():
        for line in looks_file.open():
            row = json.loads(line)
            if row.get("kind") != "look" or row.get("day", 999) > up_to_day:
                continue
            for sighting in row.get("sightings", []):
                counts[(sighting["object_id"], sighting["place_id"])] += 1
    return dict(counts)


def split_one_cell(answers_file: pathlib.Path, household: FrozenHousehold,
                   read_budget_lines: int) -> Optional[Dict[str, Any]]:
    payload = json.loads(answers_file.read_text())
    notes_file = answers_file.parent / "notes_as_frozen.json"
    if not notes_file.exists():
        return None
    notes = Notes.load(notes_file)
    everything = lines_of(notes)
    seen = sightings_by_object_and_place(looks_file_for(answers_file),
                                        notes.written_up_to_day)

    buckets: collections.Counter = collections.Counter()
    examples: Dict[str, List[str]] = collections.defaultdict(list)
    for answer in payload["answers"]:
        if answer.get("correct") is not False or not answer.get("true_place"):
            continue
        object_id, true_place = answer["object_id"], answer["true_place"]
        window = notes.what_the_robot_can_read(
            read_budget_lines, about_object=object_id).text.splitlines()
        # strict shelf matching, as in the partition
        if any(the_notes_assert(line, object_id, true_place, household, False)
               for line in window):
            continue
        if any(the_notes_assert(line, object_id, true_place, household, False)
               for line in everything):
            continue
        times = seen.get((object_id, true_place), 0)
        bucket = (NEVER_SAW_IT if times == 0
                  else SAW_IT_ONCE if times == 1 else SAW_IT_OFTEN)
        buckets[bucket] += 1
        if len(examples[bucket]) < 2:
            examples[bucket].append(f"{object_id} on {true_place} (seen {times}x)")

    n = sum(buckets.values())
    if not n:
        return None
    return {
        "household": payload["household"],
        "arm": ("claim store" if "incremental" in answers_file.parent.parent.name
                else "wholesale rewrite"),
        "freeze_point": payload["freeze_point"],
        "n_write_time_errors": n,
        "counts": {b: buckets[b] for b in (NEVER_SAW_IT, SAW_IT_ONCE, SAW_IT_OFTEN)},
        "examples": dict(examples),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/frozen_memory_test_v1"))
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--freeze-point", default="did it learn the new routine")
    parser.add_argument("--read-budget-lines", type=int, default=LOCKED.read_budget_lines)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path(
                            "results/self_improve/never_seen_or_never_written.json"))
    args = parser.parse_args(argv)

    households: Dict[str, FrozenHousehold] = {}
    rows = []
    for answers_file in sorted(args.results.rglob("held_out_answers.json")):
        payload = json.loads(answers_file.read_text())
        if args.freeze_point and payload["freeze_point"] != args.freeze_point:
            continue
        name = payload["household"]
        if name not in households:
            households[name] = FrozenHousehold(args.banks / f"{name}.jsonl")
        row = split_one_cell(answers_file, households[name], args.read_budget_lines)
        if row:
            rows.append(row)

    if not rows:
        print(f"no cells at '{args.freeze_point}' under {args.results}")
        return 0

    def show(label: str, here: List[Dict[str, Any]]) -> None:
        totals: collections.Counter = collections.Counter()
        for r in here:
            totals.update(r["counts"])
        n = sum(totals.values())
        print(f"--- {label}: {n} write-time errors across {len(here)} cells")
        for bucket in (NEVER_SAW_IT, SAW_IT_ONCE, SAW_IT_OFTEN):
            print(f"      {totals[bucket] / n:5.0%}  ({totals[bucket]:3d})  {bucket}")
        sensing = totals[NEVER_SAW_IT] / n
        note_taking = 1 - sensing
        print(f"      -> {sensing:.0%} observation, {note_taking:.0%} note-taking")

    show("pooled", rows)
    print()
    for arm in sorted({r["arm"] for r in rows}):
        show(arm, [r for r in rows if r["arm"] == arm])
    print()
    example = next((r for r in rows if r["examples"].get(NEVER_SAW_IT)), None)
    if example:
        print("examples of the sensing-failure kind: "
              + "; ".join(example["examples"][NEVER_SAW_IT]))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
