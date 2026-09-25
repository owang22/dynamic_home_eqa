"""How many days before the robot notices the household has changed?

Coverage turned out to be the wrong thing to measure. In a nine-room house at one
room a day, a fair rotation sees **19 of 19** asked-about objects within the ten
days of the disruption: complete coverage. There is nothing left for a cleverer
chooser to win, so every coverage number would say the rota is as good as anything.
That is an artefact of the budget matching the size of the house, not a result
about choosing where to look.

Timeliness has real headroom and cannot be won by sweeping. Defined precisely:

  for each household, the number of days from the first day of the disruption
  (day 14) until the robot's notes first assert something CORRECT about a moved
  object's new place.

Under a fair rotation the disrupted room comes up on about the fifth day of ten and
which day is luck. A chooser worth having gets there on the first or second. If the
rota still wins, the looking half of the paper is a negative result and we say so.

Reported per household, paired within household, with a standard error and n. Never
pooled across households and never per question.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence

from baselines.types import ON_PERSON, OUT_OF_HOUSE
from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold, plain_place_name

FIRST_DISRUPTED_DAY = 14
LAST_DISRUPTED_DAY = 23
DAYTIME_HOURS = tuple(range(8, 23))

# What we say when the notes never got there at all. Kept as a token rather than a
# number so no mean can quietly treat "never" as if it were the last day.
NEVER = None


def where_the_moved_things_went(household: FrozenHousehold) -> Dict[str, str]:
    """Each asked-about object that changed its usual daytime place when the
    resident fell ill, and the place it moved TO. Harness-side; no arm sees it."""
    def commonest(object_id: str, days) -> Optional[str]:
        counts: collections.Counter = collections.Counter()
        for day in days:
            for hour in DAYTIME_HOURS:
                place = household.place_of_object(object_id, day * 86400 + hour * 3600)
                if place and place not in (OUT_OF_HOUSE, ON_PERSON):
                    counts[place] += 1
        return counts.most_common(1)[0][0] if counts else None

    moved = {}
    for object_id in household.asked_objects:
        settled = commonest(object_id, range(0, FIRST_DISRUPTED_DAY))
        disrupted = commonest(object_id, range(FIRST_DISRUPTED_DAY, LAST_DISRUPTED_DAY + 1))
        if settled and disrupted and settled != disrupted:
            moved[object_id] = disrupted
    return moved


def the_notes_assert(text: str, object_id: str, place_id: str,
                     household: FrozenHousehold,
                     a_line_naming_only_the_right_room_counts: bool = True) -> bool:
    """Do these notes say this thing is in this place?

    Delegates to the AUDITED extractor in write_the_notes rather than matching strings
    itself. The version this replaced matched a place by its identifier or by
    `plain_place_name`, which is article-prefixed - so it missed "Kitchen cupboard",
    `KITCHEN_TABLE` and every possessive form like "Felix's book". Those faults were
    found and fixed for the vacuity measure, where they moved a closely related number
    by 18 points and did so asymmetrically, against the arm that writes prose. This
    function fed the error partition and the timeliness measure, so both inherited them
    until now.

    Matched line by line, so an object named on one line and a place on another does not
    count as an assertion joining them.
    """
    from self_improve.write_the_notes import (facts_a_statement_asserts,
                                              where_an_object_is_named)
    room = (household.place_room.get(place_id) or "").lower()
    for line in (text or "").splitlines():
        pairs = facts_a_statement_asserts(line, [object_id], household.places,
                                          household.place_room)
        if (object_id, place_id) in pairs:
            return True
        # A line naming the right room and no other room counts too: "his mug is in the
        # living room" asserts a move into the living room without naming the shelf.
        #
        # RIGHT for timeliness, WRONG for the error partition, and the hand check caught
        # it: with this on, notes saying "kitchen sink" are credited with asserting
        # "kitchen table", and notes saying BATHROOM_TOWEL_RACK with asserting the
        # bathroom shelf. Same room, different shelf. In the partition that turns a
        # write-time error at shelf level into a point-of-use error, which inflates the
        # single bucket the paper's contribution rests on. So the partition passes False.
        if not a_line_naming_only_the_right_room_counts:
            continue
        flat = line.lower().replace("_", " ")
        if room and where_an_object_is_named(line.lower(), object_id) >= 0:
            room_words = room.replace("_", " ")
            if room_words in flat and not [
                    r for r in household.rooms
                    if r != room and r.replace("_", " ") in flat]:
                return True
    return False


def days_until_it_noticed(notes_by_night: Sequence[Dict[str, Any]],
                          household: FrozenHousehold) -> Dict[str, Any]:
    """The headline measure for the looking factor."""
    moved = where_the_moved_things_went(household)
    by_night = {row["day"]: row.get("text", "") for row in notes_by_night}
    first_day_for: Dict[str, Optional[int]] = {}
    for object_id, place_id in moved.items():
        first = NEVER
        for day in range(FIRST_DISRUPTED_DAY, LAST_DISRUPTED_DAY + 1):
            if day in by_night and the_notes_assert(by_night[day], object_id, place_id,
                                                    household):
                first = day
                break
        first_day_for[object_id] = first

    noticed = [d - FIRST_DISRUPTED_DAY for d in first_day_for.values() if d is not NEVER]
    return {
        "n_moved_objects": len(moved),
        "where_they_moved_to": moved,
        "first_day_the_notes_got_each_one_right": first_day_for,
        "n_ever_noticed": len(noticed),
        "n_never_noticed": len(moved) - len(noticed),
        "days_until_the_first_one_was_noticed": min(noticed) if noticed else NEVER,
        "mean_days_over_the_ones_it_noticed": statistics.fmean(noticed) if noticed else NEVER,
        "share_of_moved_objects_ever_noticed": (len(noticed) / len(moved)) if moved else None,
    }


def paired_across_households(per_household: Dict[str, Dict[str, float]],
                             first_arm: str, second_arm: str,
                             field: str = "days_until_the_first_one_was_noticed"
                             ) -> Dict[str, Any]:
    """The paired difference, household by household. Households where either arm
    never noticed at all are reported separately rather than given a number."""
    both, incomparable = [], []
    for household, arms in sorted(per_household.items()):
        a, b = arms.get(first_arm), arms.get(second_arm)
        if a is None or b is None:
            continue
        if a.get(field) is NEVER or b.get(field) is NEVER:
            incomparable.append({"household": household,
                                 first_arm: a.get(field), second_arm: b.get(field)})
            continue
        both.append((household, a[field] - b[field]))
    differences = [d for _, d in both]
    n = len(differences)
    return {
        "measure": field,
        "first_arm": first_arm, "second_arm": second_arm,
        "clustered_on": "household",
        "n_households_compared": n,
        "per_household_difference_in_days": dict(both),
        "mean_difference_in_days": statistics.fmean(differences) if differences else None,
        "standard_error": (statistics.stdev(differences) / (n ** 0.5)) if n >= 2 else None,
        "households_where_one_arm_never_noticed": incomparable,
        "note": ("a negative mean means the first arm noticed sooner; households where "
                 "either arm never noticed are listed rather than scored, because "
                 "'never' is not a number of days"),
    }


def placebo_timeliness(notes_by_night: Sequence[Dict[str, Any]],
                       household: FrozenHousehold,
                       pretend_first_day: int = 7) -> Dict[str, Any]:
    """The same measure applied to a disruption that never happened.

    This measure conditions on "the objects the disruption moved", and that set is
    chosen by comparing two windows - the selection bias the gate's author measured
    at a 16-point false break on a scenario that should show none. Timeliness cannot
    avoid conditioning on moved objects (an object that did not move cannot be
    noticed to have moved), so it needs a placebo instead.

    So: pretend the disruption began on day 7, inside the ordinary fortnight, and
    pick "moved" objects by comparing days 0-6 against days 7-13 exactly as the real
    measure compares before and during. Nothing really changed in that window, so
    whatever number comes out is the measure's own noise floor. A real result has to
    clear it.
    """
    def commonest(object_id: str, days) -> Optional[str]:
        counts: collections.Counter = collections.Counter()
        for day in days:
            for hour in DAYTIME_HOURS:
                place = household.place_of_object(object_id, day * 86400 + hour * 3600)
                if place and place not in (OUT_OF_HOUSE, ON_PERSON):
                    counts[place] += 1
        return counts.most_common(1)[0][0] if counts else None

    pretend_moved = {}
    for object_id in household.asked_objects:
        before = commonest(object_id, range(0, pretend_first_day))
        after = commonest(object_id, range(pretend_first_day, FIRST_DISRUPTED_DAY))
        if before and after and before != after:
            pretend_moved[object_id] = after

    by_night = {row["day"]: row.get("text", "") for row in notes_by_night}
    first_day_for = {}
    for object_id, place_id in pretend_moved.items():
        first = NEVER
        for day in range(pretend_first_day, FIRST_DISRUPTED_DAY):
            if day in by_night and the_notes_assert(by_night[day], object_id, place_id,
                                                    household):
                first = day
                break
        first_day_for[object_id] = first
    noticed = [d - pretend_first_day for d in first_day_for.values() if d is not NEVER]
    return {
        "what_this_is": ("the same measure on a disruption that never happened, so it "
                         "is the measure's own noise floor"),
        "pretend_first_day": pretend_first_day,
        "n_objects_that_look_moved_by_ordinary_drift": len(pretend_moved),
        "n_ever_noticed": len(noticed),
        "days_until_the_first_one_was_noticed": min(noticed) if noticed else NEVER,
        "share_ever_noticed": (len(noticed) / len(pretend_moved)) if pretend_moved else None,
    }


def notes_by_night_from_any_layout(cell_dir: pathlib.Path) -> Optional[List[Dict[str, Any]]]:
    """The notes as they read at the end of each night, from either sweep layout.

    Cells this module launches log it directly. The memory-factor sweep does not, but
    its notes.json still carries the information: a wholesale-rewrite arm keeps every
    night's summary with its day, and a claim store records the day each claim was
    first written. So the peer sweep's fixed-rotation cells can be measured without
    being run a second time.

    The claim-store route is a reconstruction: it shows each claim from the night it
    first appeared and ignores later re-wordings. That is exact for "when did the
    notes first say this", which is all the measure asks.
    """
    direct = cell_dir / "notes_by_night.jsonl"
    if direct.exists():
        return [json.loads(l) for l in direct.open() if l.strip()]
    notes_file = cell_dir / "notes.json"
    if not notes_file.exists():
        return None
    notes = json.loads(notes_file.read_text())
    if notes.get("nightly_summaries"):
        return [{"day": row["day"], "text": row["summary"],
                 "reconstructed": False}
                for row in notes["nightly_summaries"]]
    claims = notes.get("claims") or []
    if not claims:
        return None
    last_day = max(c.get("last_revised_day", 0) for c in claims)
    return [{"day": day,
             "text": "\n".join(c["statement"] for c in claims
                                if c.get("first_written_day", 0) <= day),
             "reconstructed": True}
            for day in range(last_day + 1)]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cells", type=pathlib.Path, nargs="+",
                        default=[pathlib.Path("results/self_improve/looking_factor_illness_v1")],
                        help="one or more sweep roots, each holding hh_*/<cell>/ directories")
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/timeliness.json"))
    args = parser.parse_args(argv)

    per_household: Dict[str, Dict[str, Any]] = collections.defaultdict(dict)
    households: Dict[str, FrozenHousehold] = {}
    all_household_dirs = [d for root in args.cells for d in sorted(root.glob("hh_s*"))]
    for household_dir in all_household_dirs:
        name = household_dir.name
        if name not in households:
            households[name] = FrozenHousehold(args.banks / f"{name}.jsonl")
        for cell_dir in sorted(d for d in household_dir.iterdir() if d.is_dir()):
            rows = notes_by_night_from_any_layout(cell_dir)
            if not rows:
                continue
            real = days_until_it_noticed(rows, households[name])
            real["reconstructed_from_claim_dates"] = bool(rows[0].get("reconstructed"))
            real["placebo"] = placebo_timeliness(rows, households[name])
            per_household[name][cell_dir.name] = real

    for name, arms in sorted(per_household.items()):
        print(f"=== {name}")
        for arm, r in sorted(arms.items()):
            first = r["days_until_the_first_one_was_noticed"]
            placebo = r["placebo"]["days_until_the_first_one_was_noticed"]
            print(f"  {arm:64s} noticed after "
                  f"{'never' if first is NEVER else str(first) + ' day(s)':>12s} | "
                  f"{r['n_ever_noticed']}/{r['n_moved_objects']} moved things ever noticed"
                  f" | placebo on a disruption that never happened: "
                  f"{'never' if placebo is NEVER else str(placebo) + ' day(s)'}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"per_household": per_household}, indent=1))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
