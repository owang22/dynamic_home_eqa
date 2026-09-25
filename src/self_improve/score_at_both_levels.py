"""Score the frozen-memory answers at room level and at shelf level, against a floor
and ceiling computed at the same level.

Why both. The hypothesis is about a memory being **more useful for later object
search**. A robot that walks into the right room and looks around has found the
thing; naming the exact shelf is a precision we never asked the memory for. Scoring
only at shelf level counted "bathroom shelf instead of towel rack" and "counter
instead of sink" as failures, and between a fifth and three-quarters of the apparent
errors were of exactly that shape.

So the **room level is primary** and the **shelf level is the strict secondary**. The
shelf number stays visible; nothing is renamed away.

The trap this module exists to avoid. A room-level score may only be quoted against a
room-level floor and ceiling. Rooms are coarser and there are fewer of them, so the
floor rises and **the room available may be narrower rather than wider**. Quoting a
room-level accuracy against a shelf-level floor would be a second mis-specification
of the same kind as the first, and it is entirely possible that at room level the
memory is still at or below the trivial rule - in which case that is the finding.

    python -m self_improve.score_at_both_levels
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence

from self_improve.frozen_household import BEYOND_REACH, FROZEN_BANKS, FrozenHousehold
from self_improve.frozen_memory_test import (FREEZE_POINTS, commonest_place_when_settled,
                                             questions_in_the_window)

PLACE_LEVEL = "the exact shelf"
ROOM_LEVEL = "the right room"

# THREE reference points, named so nobody can read one as another. Conflating the
# first two turned a result into a null for two hours.
SAME_INFORMATION_FLOOR = "a frequency rule with the robot's own sightings"
ORACLE_FLOOR = "a frequency rule with complete observation"
ORACLE_CEILING = "the per-object oracle with complete observation"

# Why the distinction decides the verdict. "Each object's commonest settled place" was
# computed from the TRUE answers to every settled question - complete ground-truth
# observation of the whole house, every object, every day. The robot looked in ONE
# ROOM PER DAY. So that rule is an oracle with thirteen days of perfect house-wide
# observation, and the memory was competing against it with a few hundred sightings
# gathered one room at a time. It was not unbeatable by accident; it was unbeatable by
# construction.
#
# The fair bar is the SAME rule given only what the robot actually saw. It is computed
# PER ARM from that arm's own look stream, because the looking arms see different rooms
# and sharing a baseline between them would hide the whole looking factor.
#
# The oracle floor is kept, as an upper REFERENCE to compare against rather than a bar
# the memory is failing.

# What the floor MEANS depends on the freeze point, and conflating the two caused a
# false alarm. At the control point the notes have seen only the ordinary fortnight
# while the questions come from the disrupted days, so reproducing the settled
# routine is the best any memory built from that evidence could do: the floor is the
# PREDICTED VALUE and landing on it is the design working. At the later points the
# notes have seen the disruption and ought to clear the floor, so there it is a BAR.
FLOOR_IS_A_PREDICTION = "a prediction: landing on it is the design working"
FLOOR_IS_A_BAR = "a bar: the notes have seen the disruption and should clear it"

WHAT_THE_FLOOR_MEANS = {
    "before anything changed": FLOOR_IS_A_PREDICTION,
    "did it learn the new routine": FLOOR_IS_A_BAR,
    "did the looking arm find it sooner": FLOOR_IS_A_BAR,
    "did it keep the old routine": FLOOR_IS_A_BAR,
}


def room_of(household: FrozenHousehold, place_id: Optional[str]) -> Optional[str]:
    if not place_id:
        return None
    room = household.place_room.get(place_id)
    return room if room and room != "person_check" else None


def what_the_robot_itself_saw(looks_file: pathlib.Path, household: FrozenHousehold,
                              settled_days: int = 14) -> Dict[str, Any]:
    """Each object's commonest place, and room, among the sightings THIS ARM made on
    the settled days. The same-information floor's ingredients."""
    by_place: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    by_room: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    if looks_file.exists():
        for line in looks_file.open():
            row = json.loads(line)
            if row.get("kind") != "look" or row.get("day", 99) >= settled_days:
                continue
            for sighting in row.get("sightings", []):
                by_place[sighting["object_id"]][sighting["place_id"]] += 1
                room = room_of(household, sighting["place_id"])
                if room:
                    by_room[sighting["object_id"]][room] += 1
    return {
        "place": {o: (c.most_common(1)[0][0] if c else None) for o, c in by_place.items()},
        "room": {o: (c.most_common(1)[0][0] if c else None) for o, c in by_room.items()},
        "n_sightings_the_robot_made_on_settled_days":
            sum(sum(c.values()) for c in by_place.values()),
        "n_objects_it_ever_saw": len(by_place),
    }


def commonest_room_when_settled(household: FrozenHousehold) -> Dict[str, Optional[str]]:
    """Each object's commonest settled ROOM, counted at question moments - the
    room-level twin of the shelf-level yardstick."""
    counts: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for question in household.questions:
        if question["day_index"] >= 14:
            continue
        room = household.room_of_object(question["object_id"], question["t_query"])
        if room != BEYOND_REACH:
            counts[question["object_id"]][room] += 1
    return {o: (c.most_common(1)[0][0] if c else None) for o, c in counts.items()}


def yardsticks_at_both_levels(household: FrozenHousehold, freeze_point: str,
                              looks_file: Optional[pathlib.Path] = None
                              ) -> Dict[str, Dict[str, Any]]:
    """The three reference points at each level.

    `looks_file` is that arm's own look stream. Without it the same-information floor
    is reported as None rather than silently falling back to the oracle.
    """
    plan = FREEZE_POINTS[freeze_point]
    questions = questions_in_the_window(household, plan["questions_from_days"])
    if not questions:
        return {}
    truths_place = [household.true_place_for_question(q) for q in questions]
    truths_room = [room_of(household, p) for p in truths_place]

    settled_place = commonest_place_when_settled(household)
    settled_room = commonest_room_when_settled(household)
    seen = (what_the_robot_itself_saw(looks_file, household)
            if looks_file is not None else None)

    out: Dict[str, Dict[str, float]] = {}
    for level, truths, settled in ((PLACE_LEVEL, truths_place, settled_place),
                                   (ROOM_LEVEL, truths_room, settled_room)):
        n = len(questions)
        per_object: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        for question, truth in zip(questions, truths):
            per_object[question["object_id"]][truth] += 1
        whole_house = collections.Counter(truths)
        floor = sum(1 for q, t in zip(questions, truths)
                    if settled.get(q["object_id"]) == t) / n
        ceiling = sum(c.most_common(1)[0][1] for c in per_object.values()) / n
        fair = None
        if seen is not None:
            key = "place" if level == PLACE_LEVEL else "room"
            fair = sum(1 for q, t in zip(questions, truths)
                       if seen[key].get(q["object_id"]) == t) / n
        out[level] = {
            "n_questions": n,
            "one_fact_for_the_whole_house": whole_house.most_common(1)[0][1] / n,
            SAME_INFORMATION_FLOOR: fair,
            ORACLE_FLOOR: floor,
            ORACLE_CEILING: ceiling,
            "room_above_the_same_information_floor":
                (ceiling - fair) if fair is not None else None,
            "n_sightings_behind_the_same_information_floor":
                seen["n_sightings_the_robot_made_on_settled_days"] if seen else None,
            # kept, so the move away from judging against the oracle stays visible
            "floor_a_never_updated_memory_reaches": floor,
            "ceiling_the_per_object_oracle_reaches": ceiling,
            "room_available": ceiling - floor,
        }
    return out


def rescore(household: FrozenHousehold, answers: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    scored = [a for a in answers if a.get("true_place")]
    right_shelf = [a for a in scored if a["answer_place"] == a["true_place"]]
    right_room = [a for a in scored
                  if a.get("answer_place")
                  and room_of(household, a["answer_place"]) == room_of(household, a["true_place"])]
    wrong_shelf = [a for a in scored if a not in right_shelf]
    wrong_shelf_right_room = [a for a in wrong_shelf
                              if a.get("answer_place")
                              and room_of(household, a["answer_place"])
                              == room_of(household, a["true_place"])]
    return {
        "n_scored": len(scored),
        PLACE_LEVEL: len(right_shelf) / len(scored) if scored else None,
        ROOM_LEVEL: len(right_room) / len(scored) if scored else None,
        "of_its_wrong_shelf_answers_the_share_in_the_right_room":
            len(wrong_shelf_right_room) / len(wrong_shelf) if wrong_shelf else None,
    }


def share_of_the_room(accuracy: Optional[float], yard: Dict[str, float]) -> Optional[float]:
    if accuracy is None or not yard or not yard["room_available"]:
        return None
    return (accuracy - yard["floor_a_never_updated_memory_reaches"]) / yard["room_available"]


def looks_file_for(answers_file: pathlib.Path) -> Optional[pathlib.Path]:
    """The look stream of the arm that wrote these answers.

    The answers live at .../<household>/<cell>_[<sweep root>]/<freeze point>/, so the
    arm's own looks.jsonl is recoverable from the directory name. Per arm, never
    shared: two looking arms see different rooms and a shared baseline would hide the
    looking factor entirely.
    """
    arm_dir = answers_file.parent.parent.name
    household = answers_file.parent.parent.parent.name
    if arm_dir.endswith("]") and "_[" in arm_dir:
        cell, root = arm_dir.rsplit("_[", 1)
        root = root[:-1]
    else:
        cell, root = arm_dir, None
    here = answers_file.parent.parent.parent.parent.parent  # results/self_improve/
    candidates = ([here / root / household / cell / "looks.jsonl"] if root else []) + [
        path / household / cell / "looks.jsonl" for path in sorted(here.glob("*"))
        if path.is_dir()]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def the_outcome_null(results_dir: pathlib.Path, banks: pathlib.Path,
                     freeze_point: str = "did it learn the new routine") -> Dict[str, Any]:
    """The paper's headline null: incremental minus wholesale, paired within household.

    Reported as an EXCLUSION rather than an absence - "whatever incremental revision buys
    over wholesale rewriting is smaller than X points" - because a null that names what it
    rules out is a finding and a bare null is not.
    """
    import collections
    households: Dict[str, FrozenHousehold] = {}
    scores: Dict[str, Dict[str, Dict[str, Any]]] = collections.defaultdict(dict)
    for answers_file in sorted(results_dir.rglob("held_out_answers.json")):
        payload = json.loads(answers_file.read_text())
        if payload["freeze_point"] != freeze_point:
            continue
        name = payload["household"]
        if name not in households:
            households[name] = FrozenHousehold(banks / f"{name}.jsonl")
        arm = answers_file.parent.parent.name
        which = ("incremental" if "incremental" in arm else
                 "wholesale" if "wholesale" in arm else None)
        if which:
            scores[name][which] = rescore(households[name], payload["answers"])

    out: Dict[str, Any] = {"freeze_point": freeze_point, "by_level": {}}
    for level in (ROOM_LEVEL, PLACE_LEVEL):
        per_household = {}
        for name, arms in sorted(scores.items()):
            if "incremental" in arms and "wholesale" in arms:
                a, b = arms["incremental"][level], arms["wholesale"][level]
                if a is not None and b is not None:
                    per_household[name] = 100 * (a - b)
        values = list(per_household.values())
        n = len(values)
        mean = statistics.fmean(values) if values else None
        se = (statistics.stdev(values) / n ** 0.5) if n > 1 else None
        out["by_level"][level] = {
            "n_households": n, "per_household_points": per_household,
            "mean_points": mean, "standard_error": se,
            "n_favouring_incremental": sum(1 for v in values if v > 0),
            "what_this_null_excludes": (
                None if mean is None or se is None else
                f"anything larger than about {abs(mean) + 2 * se:.1f} points in favour of "
                f"incremental revision, and about {abs(mean - 2 * se):.1f} points against"),
            "verdict": ("not measurable" if mean is None or se is None else
                        "detected" if abs(mean) > 2 * se else "not detected"),
        }
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/frozen_memory_test_v1"))
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/scored_at_both_levels.json"))
    args = parser.parse_args(argv)

    households: Dict[str, FrozenHousehold] = {}
    rows: List[Dict[str, Any]] = []
    for answers_file in sorted(args.results.rglob("held_out_answers.json")):
        payload = json.loads(answers_file.read_text())
        name = payload["household"]
        if name not in households:
            households[name] = FrozenHousehold(args.banks / f"{name}.jsonl")
        household = households[name]
        yards = yardsticks_at_both_levels(household, payload["freeze_point"],
                                          looks_file_for(answers_file))
        scores = rescore(household, payload["answers"])
        rows.append({"household": name, "arm": payload["arm"],
                     "freeze_point": payload["freeze_point"],
                     "what_the_floor_means": WHAT_THE_FLOOR_MEANS.get(
                         payload["freeze_point"], FLOOR_IS_A_BAR),
                     "points_above_its_own_floor": {
                         level: (None if scores[level] is None or level not in yards
                                 else 100 * (scores[level]
                                             - yards[level]["floor_a_never_updated_memory_reaches"]))
                         for level in (ROOM_LEVEL, PLACE_LEVEL)},
                     "scores": scores, "yardsticks": yards,
                     "share_of_the_room": {
                         level: share_of_the_room(scores[level], yards.get(level, {}))
                         for level in (ROOM_LEVEL, PLACE_LEVEL)}})

    if not rows:
        print(f"no answer files under {args.results}")
        return 0

    print(f"{'household':11s} {'freeze point':32s} "
          f"{'room %':>7s} {'floor':>6s} {'ceil':>6s} {'of room':>8s}   "
          f"{'shelf %':>7s} {'floor':>6s} {'ceil':>6s} {'of room':>8s}")
    for r in rows:
        y_room = r["yardsticks"].get(ROOM_LEVEL, {})
        y_place = r["yardsticks"].get(PLACE_LEVEL, {})
        def pct(x):
            return f"{x:.0%}" if x is not None else "  n/a"
        print(f"{r['household'][:11]:11s} {r['freeze_point'][:32]:32s} "
              f"{pct(r['scores'][ROOM_LEVEL]):>7s} {pct(y_room.get('floor_a_never_updated_memory_reaches')):>6s} "
              f"{pct(y_room.get('ceiling_the_per_object_oracle_reaches')):>6s} "
              f"{pct(r['share_of_the_room'][ROOM_LEVEL]):>8s}   "
              f"{pct(r['scores'][PLACE_LEVEL]):>7s} {pct(y_place.get('floor_a_never_updated_memory_reaches')):>6s} "
              f"{pct(y_place.get('ceiling_the_per_object_oracle_reaches')):>6s} "
              f"{pct(r['share_of_the_room'][PLACE_LEVEL]):>8s}")

    # Grouped by freeze point, because the floor means different things at each and a
    # pooled number across freeze points would average a prediction with a bar.
    for freeze_point in sorted({r["freeze_point"] for r in rows}):
        here = [r for r in rows if r["freeze_point"] == freeze_point]
        print()
        print(f"--- {freeze_point}: its floor is {here[0]['what_the_floor_means']}")
        for level in (ROOM_LEVEL, PLACE_LEVEL):
            diffs = [r["points_above_its_own_floor"][level] for r in here
                     if r["points_above_its_own_floor"][level] is not None]
            if not diffs:
                continue
            mean = statistics.fmean(diffs)
            se = (statistics.stdev(diffs) / len(diffs) ** 0.5) if len(diffs) > 1 else None
            if se is None:
                verdict = "one household only, no verdict"
            elif mean - 2 * se > 0:
                verdict = "clears its floor"
            elif mean + 2 * se < 0:
                verdict = "below its floor"
            else:
                verdict = "indistinguishable from its floor"
            print(f"    {level:16s} {mean:+6.1f} points vs floor, "
                  f"standard error {se if se is None else round(se, 1)}, "
                  f"n={len(diffs)} households -> {verdict}")

    for level in (ROOM_LEVEL, PLACE_LEVEL):
        vals = [r["scores"][level] for r in rows if r["scores"][level] is not None]
        floors = [r["yardsticks"][level]["floor_a_never_updated_memory_reaches"]
                  for r in rows if level in r["yardsticks"]]
        rooms = [r["yardsticks"][level]["room_available"]
                 for r in rows if level in r["yardsticks"]]
        beats = sum(1 for r in rows
                    if r["scores"][level] is not None and level in r["yardsticks"]
                    and r["scores"][level] > r["yardsticks"][level]["floor_a_never_updated_memory_reaches"])
        print()
        print(f"{level}: mean {statistics.fmean(vals):.0%} "
              f"(standard error {statistics.stdev(vals)/len(vals)**0.5:.1%}, n={len(vals)}) "
              f"against a mean floor of {statistics.fmean(floors):.0%} and "
              f"{statistics.fmean(rooms):.0%} of room; "
              f"beats its own floor in {beats} of {len(rows)} arm-points")

    null = the_outcome_null(args.results, args.banks)
    print()
    print(f"THE OUTCOME NULL at '{null['freeze_point']}': incremental minus wholesale, "
          f"paired within household")
    for level, r in null["by_level"].items():
        if not r["n_households"]:
            continue
        print(f"  {level:16s} {r['mean_points']:+6.1f} points, standard error "
              f"{'n/a' if r['standard_error'] is None else format(r['standard_error'], '.1f')}, "
              f"n={r['n_households']}, favours incremental in "
              f"{r['n_favouring_incremental']} -> {r['verdict']}")
        if r["what_this_null_excludes"]:
            print(f"  {'':16s} excludes {r['what_this_null_excludes']}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"per_cell": rows, "the_outcome_null": null}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
