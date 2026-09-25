"""Could the look have told its own two claims apart?

This is the failure mode peculiar to this study. The choosing arm is required to
name two competing claims and say what it expects to see under each. The
degenerate case is that both claims predict the SAME thing at the room it picked,
so whatever it sees, it learns nothing about which claim is right. A look like
that is worthless, and it will never show up in an accuracy number: the arm still
answers questions, still gets some of them right, and nothing in the results
would tell you the looks were empty of purpose.

So we check it directly, mechanically, with no model in the loop. The structured
action requires each claim to list the objects it expects to find at the chosen
room. Then:

  do the two expectations differ?   the sets must not be equal. If they are, the
                                    look cannot discriminate, full stop.
  did the look settle it?           after the look, exactly one of the two
                                    expectations should match what was actually
                                    found. If both match or neither does, the
                                    look did not settle the question it posed -
                                    which can be honest bad luck (the object was
                                    in a third place) so we count it separately.
  was the room even relevant?       at least one of the two claims must place a
                                    named object in the room that was visited.

Report the share of looks that pass the first check. That share is the headline
number for whether the choosing arm is doing the thing the paper says it does.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any, Dict, List, Optional, Sequence

CANNOT_TELL_THEM_APART = "the two claims predict the same thing here"
DIFFERENT_EXPECTATIONS = "the two claims predict different things here"


def judge_one_look(look: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Judge a single logged look. Returns None for looks the schedule chose,
    which make no claims and so cannot be judged."""
    action = look.get("chosen_look")
    if not action:
        return None

    first = set(action.get("objects_expected_if_the_first_claim_holds") or [])
    second = set(action.get("objects_expected_if_the_second_claim_holds") or [])
    expectations_differ = first != second

    found = {s["object_id"] for s in look.get("sightings", [])}
    target = action.get("target")
    # Only objects at the visited target count as "found here".
    found_here = {s["object_id"] for s in look.get("sightings", [])
                  if s.get("revealed_by_target") == target
                  or s.get("room") == target or s.get("place_id") == target}

    # "I expect to find nothing here" is a legitimate and informative prediction:
    # a claim that puts the charger on the desk predicts an empty living room. So
    # a prediction is judged against the objects EITHER claim mentions, and it
    # holds when that set matches exactly. Testing `first <= found_here` instead
    # would have scored every expect-nothing prediction as failed, which would have
    # silently marked the most discriminating looks in the study as settling
    # nothing.
    mentioned_by_either = first | second
    found_among_those = found_here & mentioned_by_either
    first_matched = found_among_those == first
    second_matched = found_among_those == second
    if first_matched and not second_matched:
        settled = "the first claim held"
    elif second_matched and not first_matched:
        settled = "the second claim held"
    elif first_matched and second_matched:
        settled = "both expectations were met, so nothing was settled"
    else:
        settled = "neither expectation was met, so nothing was settled"

    return {
        "look_id": look["look_id"],
        "day": look["day"],
        "period": look.get("period"),
        "target": target,
        "first_claim": action.get("first_claim"),
        "second_claim": action.get("second_claim"),
        "objects_expected_if_the_first_claim_holds": sorted(first),
        "objects_expected_if_the_second_claim_holds": sorted(second),
        "the_look_could_tell_them_apart": expectations_differ,
        "why": DIFFERENT_EXPECTATIONS if expectations_differ else CANNOT_TELL_THEM_APART,
        "objects_actually_found_at_the_target": sorted(found_here),
        "objects_either_claim_mentioned_that_were_found": sorted(found_among_those),
        "what_the_look_settled": settled,
        "either_claim_named_something_in_this_room": bool(first or second),
        "the_look_named_no_expected_objects_at_all": not (first or second),
    }


def check_a_log(log_path: pathlib.Path) -> Dict[str, Any]:
    judged: List[Dict[str, Any]] = []
    n_looks = 0
    for line in log_path.open():
        row = json.loads(line)
        if row.get("kind") != "look":
            continue
        n_looks += 1
        verdict = judge_one_look(row)
        if verdict is not None:
            judged.append(verdict)

    if not judged:
        return {"log": str(log_path), "n_looks": n_looks,
                "n_looks_the_model_chose": 0,
                "note": "no chosen looks in this log, so there is nothing to judge"}

    could = [v for v in judged if v["the_look_could_tell_them_apart"]]
    settled = [v for v in judged if v["what_the_look_settled"].endswith("claim held")]
    empty = [v for v in judged if v["the_look_named_no_expected_objects_at_all"]]
    report = {
        "log": str(log_path),
        "n_looks": n_looks,
        "n_looks_the_model_chose": len(judged),
        "share_that_could_tell_their_two_claims_apart": len(could) / len(judged),
        "share_that_actually_settled_which_claim_held": len(settled) / len(judged),
        "share_that_named_no_expected_objects": len(empty) / len(judged),
        "verdicts": judged,
        "concerns": [],
    }
    if report["share_that_could_tell_their_two_claims_apart"] < 0.7:
        report["concerns"].append(
            f"only {report['share_that_could_tell_their_two_claims_apart']:.0%} of looks "
            f"named two claims that predict different things: the choosing arm is mostly "
            f"not doing what the paper claims")
    if report["share_that_named_no_expected_objects"] > 0.1:
        report["concerns"].append(
            f"{report['share_that_named_no_expected_objects']:.0%} of looks named no "
            f"expected objects at all, so the action was not filled in")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", type=pathlib.Path, nargs="+",
                        help="look logs written by self_improve.looking")
    parser.add_argument("--out", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)
    reports = [check_a_log(p) for p in args.logs]
    for report in reports:
        if report.get("n_looks_the_model_chose"):
            print(f"{report['log']}: {report['n_looks_the_model_chose']} chosen looks; "
                  f"{report['share_that_could_tell_their_two_claims_apart']:.0%} could tell "
                  f"their two claims apart; "
                  f"{report['share_that_actually_settled_which_claim_held']:.0%} settled it")
            for concern in report["concerns"]:
                print(f"   concern: {concern}")
        else:
            print(f"{report['log']}: {report.get('note')}")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(reports, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
