"""Which asked-about objects actually move when the resident falls ill.

This decides what the memory has to do. An object that moves needs a claim
revised; an object that never moves needs a claim preserved. A scenario where
everything moves to the same place needs one sentence and cannot separate a
per-claim store from a wholesale rewrite.

It also decides which households are in the study, through a rule written down
before any arm runs.

An important warning about method, measured and not assumed. "The object's usual
place" can be computed over the hours the robot looks, or over the moments the
questions are asked, and the two disagree. In household s4 six of thirteen asked
objects change their usual daytime place - the disruption plainly happened - but
only one changes its usual place at question times, because the question stream
does not sample those objects at the hours they have moved. So:

  measured over daytime hours, no household has fewer than three movers;
  measured at question times, s4 has one and every other household has three or
  more.

Excluding a household on the question-times measure is excluding it because the
measurement cannot see the event, not because the event did not happen. That is
a defensible thing to do but it selects on the outcome measure, which inflates
whatever effect the remaining households show. Both counts are reported for
every household so the choice is visible rather than buried.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
from typing import Any, Dict, List, Optional, Sequence

from baselines.types import ON_PERSON, OUT_OF_HOUSE
from self_improve.frozen_household import FrozenHousehold

SETTLED_DAYS = tuple(range(0, 14))
DISRUPTED_DAYS = tuple(range(14, 24))
BACK_TO_NORMAL_DAYS = tuple(range(24, 32))

# The hours a daytime look could happen. 10:00-17:00 is where 71-75% of the
# disruption is visible; we take the wider waking day so the count is not an
# artefact of the exact look time.
DAYTIME_HOURS = tuple(range(8, 23))


def _commonest_place(household: FrozenHousehold, object_id: str,
                     times: Sequence[int]) -> Optional[str]:
    counts: collections.Counter = collections.Counter()
    for t in times:
        place = household.place_of_object(object_id, t)
        if place and place not in (OUT_OF_HOUSE, ON_PERSON):
            counts[place] += 1
    return counts.most_common(1)[0][0] if counts else None


def _daytime_moments(days: Sequence[int]) -> List[int]:
    return [day * 86400 + hour * 3600 for day in days for hour in DAYTIME_HOURS]


def _question_moments(household: FrozenHousehold, object_id: str,
                      days: Sequence[int]) -> List[int]:
    wanted = set(days)
    return [q["t_query"] for q in household.questions
            if q["object_id"] == object_id and q["day_index"] in wanted]


def describe_one_household(household: FrozenHousehold) -> Dict[str, Any]:
    objects: List[Dict[str, Any]] = []
    for object_id in household.asked_objects:
        row: Dict[str, Any] = {"object_id": object_id,
                               "object_class": household.object_class.get(object_id, "")}
        for label, moments in (("over daytime hours", _daytime_moments),
                               ("at question times", None)):
            def moments_for(days):
                return (moments(days) if moments is not None
                        else _question_moments(household, object_id, days))
            settled = _commonest_place(household, object_id, moments_for(SETTLED_DAYS))
            disrupted = _commonest_place(household, object_id, moments_for(DISRUPTED_DAYS))
            back = _commonest_place(household, object_id, moments_for(BACK_TO_NORMAL_DAYS))
            moved = bool(settled and disrupted and settled != disrupted)
            if not moved:
                what_the_return_did = "did not move in the first place"
            elif back == settled:
                what_the_return_did = "went back to where it was"
            elif back == disrupted:
                what_the_return_did = "stayed where the disruption put it"
            else:
                what_the_return_did = "ended up somewhere third"
            row[label] = {"usual place when settled": settled,
                          "usual place when disrupted": disrupted,
                          "usual place back to normal": back,
                          "moved": moved,
                          "what the return did": what_the_return_did}
        objects.append(row)

    out: Dict[str, Any] = {"household": household.name,
                           "n_questions": len(household.questions),
                           "n_asked_objects": len(household.asked_objects),
                           "objects": objects}
    for label in ("over daytime hours", "at question times"):
        movers = [o for o in objects if o[label]["moved"]]
        destinations = collections.Counter(o[label]["usual place when disrupted"] for o in movers)
        returns = collections.Counter(o[label]["what the return did"] for o in movers)
        out[label] = {
            "n_that_moved": len(movers),
            "n_that_never_moved": len(objects) - len(movers),
            "where_they_moved_to": dict(destinations.most_common()),
            "n_distinct_destinations": len(destinations),
            "share_of_movers_on_the_commonest_destination":
                (destinations.most_common(1)[0][1] / len(movers)) if movers else None,
            "what_the_return_did": dict(returns.most_common()),
            "share_that_went_back_cleanly":
                (returns.get("went back to where it was", 0) / len(movers)) if movers else None,
        }
    return out


# ------------------------------------------------------ the exclusion rule --

RULE = ("drop any household where fewer than two asked-about objects change "
        "their usual place when the resident falls ill")
MINIMUM_MOVERS = 2


def households_in_the_study(descriptions: Sequence[Dict[str, Any]],
                            measured: str = "over daytime hours"
                            ) -> Dict[str, Any]:
    """Apply the exclusion rule. `measured` is the choice that decides the
    answer, so it is an argument and it is recorded in the output."""
    kept, dropped = [], []
    for d in descriptions:
        n = d[measured]["n_that_moved"]
        (kept if n >= MINIMUM_MOVERS else dropped).append(
            {"household": d["household"], "n_that_moved": n})
    return {"rule": RULE, "measured": measured, "minimum_movers": MINIMUM_MOVERS,
            "kept": kept, "dropped": dropped}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--banks", type=pathlib.Path,
                        default=pathlib.Path("results/regime_search/sick10_partial/banks"))
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/which_objects_moved.json"))
    args = parser.parse_args(argv)

    descriptions = [describe_one_household(FrozenHousehold(p))
                    for p in sorted(args.banks.glob("hh_s*_t03.jsonl"))]
    for d in descriptions:
        day, ask = d["over daytime hours"], d["at question times"]
        print(f"{d['household']}: {d['n_questions']} questions, "
              f"{d['n_asked_objects']} asked objects | "
              f"movers: {day['n_that_moved']} over daytime hours, "
              f"{ask['n_that_moved']} at question times | "
              f"{day['n_distinct_destinations']} destinations, "
              f"{day['share_of_movers_on_the_commonest_destination']:.0%} on the commonest | "
              f"{day['share_that_went_back_cleanly']:.0%} went back cleanly")
    both = {measured: households_in_the_study(descriptions, measured)
            for measured in ("over daytime hours", "at question times")}
    print()
    for measured, verdict in both.items():
        names = [d["household"] for d in verdict["dropped"]] or ["none"]
        print(f"rule measured {measured}: drops {', '.join(names)}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"households": descriptions,
                                    "exclusion_rule": both}, indent=1))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
