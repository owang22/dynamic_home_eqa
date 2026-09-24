"""How much of a household does a three-room look actually cover?

This is the first question the study has to answer. If three rooms a day already
covers nearly every object the robot will be asked about, then the arm that
chooses rooms cannot beat the arm that follows a fixed schedule, no matter how
good its reasoning is, and the "where it looks" half of the design is dead.

We read the frozen question banks and do not write anything into them. Every
number is per household; nothing is pooled.

Run:
    python -m self_improve.measure_room_coverage
"""
from __future__ import annotations

import argparse
import bisect
import collections
import json
import pathlib
import statistics
from typing import Dict, List, Tuple

FROZEN_BANKS = pathlib.Path(
    "/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/banks_f1")

# A room name the simulator uses for "ask whether a person is home", not a real room.
NOT_A_REAL_ROOM = "person_check"
# A place that cannot be looked into at all.
OUTSIDE_THE_HOUSE = "OUT_OF_HOUSE"


class HouseholdTruth:
    """Where every object really is, at any moment, for one household.

    Kept for the coverage measurement's own history. New code should use
    self_improve.frozen_household.FrozenHousehold, which does the same job and
    also knows about places and look targets."""

    def __init__(self, bank_path: pathlib.Path) -> None:
        self.header = None
        self.questions: List[dict] = []
        moves: Dict[str, List[Tuple[int, str]]] = collections.defaultdict(list)
        for line in bank_path.open():
            row = json.loads(line)
            kind = row["kind"]
            if kind == "episode_header":
                self.header = row
            elif kind == "truth":
                moves[row["object_id"]].append((row["t"], row["receptacle_id"]))
            elif kind == "question":
                self.questions.append(row)
        if self.header is None:
            raise ValueError(f"{bank_path} has no episode_header row")
        for history in moves.values():
            history.sort()
        self.moves = moves
        self.receptacle_room: Dict[str, str] = self.header["receptacle_rooms"]
        self.real_rooms = sorted(
            {room for room in self.receptacle_room.values() if room != NOT_A_REAL_ROOM})
        self.asked_objects = sorted({q["object_id"] for q in self.questions})

    def room_of_object(self, object_id: str, at_time: int) -> str:
        """The room holding this object at this moment, or 'nowhere we can look'."""
        history = self.moves.get(object_id, ())
        if not history:
            return "nowhere we can look"
        index = bisect.bisect_right(history, (at_time, "￿")) - 1
        if index < 0:
            return "nowhere we can look"
        receptacle = history[index][1]
        if receptacle == OUTSIDE_THE_HOUSE:
            return "nowhere we can look"
        return self.receptacle_room.get(receptacle, "nowhere we can look")

    def asked_objects_by_room(self, at_time: int) -> collections.Counter:
        """How many asked-about objects sit in each room at this moment."""
        found = collections.Counter()
        for object_id in self.asked_objects:
            room = self.room_of_object(object_id, at_time)
            if room != "nowhere we can look":
                found[room] += 1
        return found


def coverage_table(truth: HouseholdTruth, look_hour: int, n_days: int,
                   budgets=(1, 2, 3)) -> dict:
    """For each look budget: what a perfect chooser, the best fixed rooms, and a
    fair rotation would each see."""
    per_day = {day: truth.asked_objects_by_room(day * 86400 + look_hour * 3600)
               for day in range(n_days)}
    objects_in_house_per_day = {day: sum(counts.values()) for day, counts in per_day.items()}
    across_all_days = collections.Counter()
    for counts in per_day.values():
        across_all_days.update(counts)

    out = {"look_hour": look_hour,
           "n_real_rooms": len(truth.real_rooms),
           "n_asked_objects": len(truth.asked_objects),
           "rooms_ever_holding_an_asked_object": sorted(across_all_days),
           "budgets": {}}

    for budget in budgets:
        best_fixed = [room for room, _ in across_all_days.most_common(budget)]
        perfect, fixed, rotation = [], [], []
        for day, counts in per_day.items():
            in_house = objects_in_house_per_day[day]
            if not in_house:
                continue
            perfect.append(sum(n for _, n in counts.most_common(budget)) / in_house)
            fixed.append(sum(n for room, n in counts.items() if room in best_fixed) / in_house)
            rotating = [truth.real_rooms[(day * budget + i) % len(truth.real_rooms)]
                        for i in range(budget)]
            rotation.append(sum(n for room, n in counts.items() if room in rotating) / in_house)
        out["budgets"][budget] = {
            "best_fixed_rooms": best_fixed,
            "share_seen_by_a_perfect_chooser": statistics.mean(perfect),
            "share_seen_by_the_best_fixed_rooms": statistics.mean(fixed),
            "share_seen_by_a_fair_rotation": statistics.mean(rotation),
            "headroom_for_choosing_over_best_fixed":
                statistics.mean(perfect) - statistics.mean(fixed),
        }
    return out


def answer_room_concentration(truth: HouseholdTruth) -> dict:
    """At the moment each question is asked, which room holds the answer?
    If three rooms hold nearly all the answers, the house is effectively small."""
    by_room = collections.Counter()
    by_stage = collections.defaultdict(collections.Counter)
    for question in truth.questions:
        room = truth.room_of_object(question["object_id"], question["t_query"])
        by_room[room] += 1
        by_stage[question["stage"]][room] += 1
    total = sum(by_room.values())
    top_three = sum(n for _, n in by_room.most_common(3))
    return {"n_questions": total,
            "answer_rooms": by_room.most_common(),
            "share_of_answers_in_the_three_commonest_rooms": top_three / total,
            "by_stage": {stage: dict(counts.most_common()) for stage, counts in by_stage.items()}}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--look-hours", type=int, nargs="+", default=[8, 12, 18, 21])
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/room_coverage.json"))
    args = parser.parse_args(argv)

    report = {}
    for bank_path in sorted(args.banks.glob("hh_s*_t03.jsonl")):
        household = bank_path.stem
        truth = HouseholdTruth(bank_path)
        n_days = truth.header["n_days"]
        report[household] = {
            "household_type": truth.header["household_type"],
            "n_residents": len(truth.header["resident_ids"]),
            "n_real_rooms": len(truth.real_rooms),
            "real_rooms": truth.real_rooms,
            "n_receptacles": len(truth.receptacle_room),
            "n_asked_objects": len(truth.asked_objects),
            "answers": answer_room_concentration(truth),
            "coverage_by_look_hour": {
                hour: coverage_table(truth, hour, n_days) for hour in args.look_hours},
        }
        print(f"{household}: {len(truth.real_rooms)} real rooms, "
              f"{len(truth.asked_objects)} asked-about objects, "
              f"{report[household]['answers']['share_of_answers_in_the_three_commonest_rooms']:.0%} "
              f"of answers sit in its three commonest rooms")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
