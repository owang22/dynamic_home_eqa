"""Has the bottleneck moved from sensing to note-taking?

Under the patrol design, 75% of the memory's errors were objects the robot had
NEVER SEEN in their new place. That is a sensing bottleneck: no note-taking policy
of any kind can record what was never observed. The search design gives roughly
twenty times the observation - up to 24 room-visits a day against the patrol's
1.26 - so the question is whether that 75% collapses.

The two outcomes are two different papers and both are strong:

  never-saw collapses toward zero AND the memory still fails to recover: the
  bottleneck has MOVED. Under a patrol you cannot learn what you never see; under
  search you see it repeatedly and still do not learn it. The failure is then
  definitively note-taking, not sensing.

  never-saw stays high even at 24 rooms a day: the sensing limit is far deeper than
  the patrol, and that needs explaining before it is believed.

NO TEXT MATCHER IS INVOLVED. The split is computed from the structured sighting
records alone, and the failure is defined by what the robot DID rather than by
grepping its prose for a place name - every text-matching measure in this project
has needed repair and every structured one has held.

Two definitions of failure are reported, because they answer different questions
and only one of them needs the answer step:

  THE FIRST ROOM WAS WRONG. The robot walked into a room and the object was not
  there. Needs only looks.jsonl, so it is available for every cell the moment it
  starts, and it is the measure the design turns on.

  THE ANSWER WAS WRONG. Needs searches.jsonl or cell.json. Reported where present.

For each failure we count how many times this arm had ALREADY seen that object at
the place it actually was, strictly before the question was asked - so "saw it
repeatedly and still got it wrong" cannot be a latency artefact of evidence that
arrived later.

    python -m self_improve.where_the_bottleneck_moved --days 14 23 --movers-only
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.search_cost_from_the_looks import find_the_cells
from self_improve.search_driven import (answerable_questions_on_day,
                                        questions_spread_across_the_day, the_movers)

NEVER_SAW_IT = "never saw the object there"
SAW_IT_ONCE = "saw it there once and still got it wrong"
SAW_IT_OFTEN = "saw it there repeatedly and still got it wrong"
BUCKETS = (NEVER_SAW_IT, SAW_IT_ONCE, SAW_IT_OFTEN)


def one_cell(looks_file: pathlib.Path, household: FrozenHousehold,
             days: range, movers_only: bool, questions_per_day: int = 8
             ) -> Optional[Dict[str, Any]]:
    """Walk this cell's looks in time order, keeping a running count of what it has
    seen where, and bucket every first-room failure by how much evidence it already
    had."""
    movers = the_movers(household)
    wanted: Dict[Tuple[int, int], dict] = {}
    for day in range(household.n_days + 1):
        for question in questions_spread_across_the_day(
                answerable_questions_on_day(household, day), questions_per_day):
            wanted[(question["day_index"], question["t_query"])] = question

    by_moment: Dict[Tuple[int, int], List[dict]] = collections.defaultdict(list)
    for line in looks_file.open():
        row = json.loads(line)
        if row.get("kind") == "look":
            by_moment[(row["day"], row["time"])].append(row)

    # seen[(object, place)] and seen_room[(object, room)] BEFORE the current moment
    seen_place: collections.Counter = collections.Counter()
    seen_room: collections.Counter = collections.Counter()
    buckets: collections.Counter = collections.Counter()
    buckets_room: collections.Counter = collections.Counter()
    n_failures = 0
    n_questions = 0
    examples: Dict[str, List[str]] = collections.defaultdict(list)

    for moment in sorted(by_moment):
        looks = sorted(by_moment[moment], key=lambda r: r["look_id"])
        question = wanted.get(moment)
        in_scope = (question is not None and moment[0] in days
                    and (not movers_only or question["object_id"] in movers))
        if question is not None and in_scope:
            n_questions += 1
            object_id = question["object_id"]
            true_place = household.true_place_for_question(question)
            true_room = household.place_room.get(true_place or "")
            first_room = looks[0]["targets"][0]["name"] if looks else None
            first_room_was_wrong = first_room != true_room
            if first_room_was_wrong and true_place:
                n_failures += 1
                times = seen_place[(object_id, true_place)]
                bucket = (NEVER_SAW_IT if times == 0
                          else SAW_IT_ONCE if times == 1 else SAW_IT_OFTEN)
                buckets[bucket] += 1
                times_room = seen_room[(object_id, true_room)]
                buckets_room[NEVER_SAW_IT if times_room == 0
                             else SAW_IT_ONCE if times_room == 1
                             else SAW_IT_OFTEN] += 1
                if len(examples[bucket]) < 3:
                    examples[bucket].append(
                        f"day {moment[0]} {object_id}: was on {true_place} in "
                        f"{true_room}, went to {first_room}, had seen it there "
                        f"{times}x (in that room {times_room}x)")
        # only now does this moment's evidence count as seen
        for look in looks:
            for s in look["sightings"]:
                seen_place[(s["object_id"], s["place_id"])] += 1
                seen_room[(s["object_id"], s["room"])] += 1

    if not n_failures:
        return None
    return {
        "household": household.name,
        "n_questions_in_scope": n_questions,
        "n_first_room_failures": n_failures,
        "share_of_questions_that_failed": n_failures / n_questions if n_questions else None,
        "at_the_exact_shelf": {b: buckets[b] for b in BUCKETS},
        "at_the_exact_shelf_shares": {b: buckets[b] / n_failures for b in BUCKETS},
        "at_the_room_level": {b: buckets_room[b] for b in BUCKETS},
        "at_the_room_level_shares": {b: buckets_room[b] / n_failures for b in BUCKETS},
        "examples": dict(examples),
    }


def the_answer_side(root: pathlib.Path, days: range, movers_only: bool
                    ) -> Dict[str, Any]:
    """The same split defined on WRONG ANSWERS rather than wrong first rooms, from
    whatever cells have produced searches.jsonl or cell.json. `times_seen_there_before`
    is recorded by the harness at the moment the question was asked, so it is already
    strictly prior evidence."""
    rows: List[dict] = []
    for path in sorted(root.rglob("searches.jsonl")):
        for line in path.open():
            row = json.loads(line)
            if row.get("kind") == "search":
                rows.append({**row, "_cell": str(path.parent)})
    for path in sorted(root.rglob("cell.json")):
        cell = json.loads(path.read_text())
        if any(r["_cell"] == str(path.parent) for r in rows):
            continue
        movers = set(cell["movers"])
        for row in cell["searches"]:
            rows.append({**row, "_cell": str(path.parent),
                         "is_a_mover": row["object_id"] in movers})
    wrong = [r for r in rows
             if r.get("correct_place") is False and r["day"] in days
             and (not movers_only or r.get("is_a_mover"))]
    buckets: collections.Counter = collections.Counter()
    for r in wrong:
        times = r.get("times_seen_there_before", 0)
        buckets[NEVER_SAW_IT if times == 0
                else SAW_IT_ONCE if times == 1 else SAW_IT_OFTEN] += 1
    n = sum(buckets.values())
    return {"n_cells_with_answers": len({r["_cell"] for r in rows}),
            "n_wrong_answers_in_scope": n,
            "counts": {b: buckets[b] for b in BUCKETS},
            "shares": ({b: buckets[b] / n for b in BUCKETS} if n else None)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/search_driven"))
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--days", type=int, nargs=2, default=[14, 23])
    parser.add_argument("--movers-only", action="store_true")
    parser.add_argument("--questions-per-day", type=int, default=8)
    parser.add_argument("--only-arm", default=None)
    parser.add_argument("--out", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    days = range(args.days[0], args.days[1] + 1)
    households: Dict[str, FrozenHousehold] = {}
    per_cell: List[Dict[str, Any]] = []
    for key, looks_file in sorted(find_the_cells(args.root).items()):
        if args.only_arm and key[1] != args.only_arm:
            continue
        if key[0] not in households:
            households[key[0]] = FrozenHousehold(args.banks / f"{key[0]}.jsonl")
        got = one_cell(looks_file, households[key[0]], days, args.movers_only,
                       args.questions_per_day)
        if got:
            got["sensing_arm"], got["how_memory_is_written"] = key[1], key[2]
            per_cell.append(got)

    print(f"\n=== days {args.days[0]}-{args.days[1]}"
          f"{', MOVERS ONLY' if args.movers_only else ''} ===")
    print("Failure = the FIRST room it walked into was not the room the object was in.")
    print("Buckets = how many times this arm had already seen that object at the place")
    print("it actually was, strictly BEFORE the question was asked.\n")
    print(f"{'arm':22s} {'format':18s} {'fails':>6s} {'of':>5s}  "
          f"{'never saw':>10s} {'saw once':>9s} {'saw often':>10s}")
    by_arm: Dict[Tuple[str, str], List[Dict[str, Any]]] = collections.defaultdict(list)
    for row in per_cell:
        by_arm[(row["sensing_arm"], row["how_memory_is_written"])].append(row)
    summary: Dict[str, Any] = {}
    for (arm, how), here in sorted(by_arm.items()):
        totals = collections.Counter()
        n_f = n_q = 0
        for row in here:
            for b in BUCKETS:
                totals[b] += row["at_the_exact_shelf"][b]
            n_f += row["n_first_room_failures"]
            n_q += row["n_questions_in_scope"]
        n = sum(totals.values())
        print(f"{arm:22s} {how:18s} {n_f:6d} {n_q:5d}  "
              + "  ".join(f"{totals[b] / n:9.1%}" for b in BUCKETS)
              + f"   (n households {len(here)})")
        # THE NEVER-SAW SHARE IS A COMPOSITION OF THE FAILURE SET, so it inverts if
        # quoted alone: the memory-guided arm's 23% against the controls' 5% reads as
        # the arm doing worse, when it fails on 56 of 126 mover-questions against the
        # rotation's 115 of 126 and what remains is concentrated on genuinely novel
        # placements. So the share is not exposed as a bare number anywhere in this
        # output - it is carried inside a string that states the failure rate with it,
        # and the raw counts are there for anyone recomputing.
        summary[f"{arm} / {how}"] = {
            "n_first_room_failures": n_f, "n_questions_in_scope": n_q,
            "failure_rate": (n_f / n_q) if n_q else None,
            "counts": {b: totals[b] for b in BUCKETS},
            "never_saw_share_WITH_ITS_FAILURE_RATE": (
                f"{totals[NEVER_SAW_IT] / n:.1%} of failures, but this arm failed on "
                f"{n_f} of {n_q} questions ({(n_f / n_q) if n_q else 0:.0%}); the share "
                f"is a composition of the failure set and inverts if quoted alone"),
            "shares_WITH_ITS_FAILURE_RATE": {
                b: (f"{totals[b] / n:.1%} of {n_f} failures in {n_q} questions")
                for b in BUCKETS},
            "per_household_never_saw_with_failure_rates": [
                f"{row['at_the_exact_shelf_shares'][NEVER_SAW_IT]:.0%} of "
                f"{row['n_first_room_failures']} failures in "
                f"{row['n_questions_in_scope']} questions ({row['household']})"
                for row in here],
        }
    answers = the_answer_side(args.root, days, args.movers_only)
    print(f"\nthe same split on WRONG ANSWERS, from "
          f"{answers['n_cells_with_answers']} cells that have answers: "
          f"{answers['n_wrong_answers_in_scope']} wrong answers in scope")
    if answers["shares"]:
        for b in BUCKETS:
            print(f"      {answers['shares'][b]:6.1%}  ({answers['counts'][b]:3d})  {b}")
    print("\nthe patrol design, for comparison: 75% never-saw")
    example = next((r for r in per_cell if r["examples"].get(SAW_IT_OFTEN)), None)
    if example:
        print(f"\nexamples of 'saw it repeatedly and still got it wrong' "
              f"({example['sensing_arm']}, {example['household']}):")
        for e in example["examples"][SAW_IT_OFTEN]:
            print("   ", e)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(
            {"days": args.days, "movers_only": args.movers_only,
             "per_arm": summary, "per_cell": per_cell,
             "on_wrong_answers": answers}, indent=1))
        print(f"\nwritten to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
