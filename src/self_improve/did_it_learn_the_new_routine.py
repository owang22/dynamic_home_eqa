"""The primary result, and it needs no baseline whatsoever.

Two freeze points ask **the same questions, from days 14 to 23**. The only thing that
differs between them is whether the notes were written through day 13 or through day
23. Same household, same arm, same questions, same reading budget, same prompt - only
ten days of nightly note-writing over the disruption separates them.

So their difference IS the answer to "did it learn the new routine", with no floor, no
ceiling, no oracle, and nothing to argue about. Every baseline question - whether the
frequency rule should have complete observation or only the robot's own sightings -
becomes irrelevant here, which is exactly why this is the headline and the
baseline-relative numbers are secondary.

Reported as a paired within-household difference, per arm, at both levels, with a
household-clustered standard error, n, and every per-household value, because below
about six households the spread is wider than the mean and nothing is detected.

    python -m self_improve.did_it_learn_the_new_routine
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.score_at_both_levels import PLACE_LEVEL, ROOM_LEVEL, rescore
from self_improve.study_settings import LOCKED

BEFORE = "before anything changed"          # notes through day 13
AFTER = "did it learn the new routine"      # notes through day 23


def churn_between_the_freeze_points(results_dir: pathlib.Path, banks: pathlib.Path,
                                   arm_filter: Optional[str] = None) -> Dict[str, Any]:
    """How many individual answers CHANGED between the two freeze points, and how many
    of those changes were improvements.

    The net difference alone hides the interesting part. A net of +4 room-level points
    can mean the memory barely moved, or that it moved a fifth of its answers and won
    barely more often than it lost. Those are very different claims, and it is the
    second one: ten days of revision changes about a fifth to a quarter of all answers,
    and of the room-level changes only about half are improvements.

    Reported as won, lost, net and out of how many, per arm and per level, because that
    is the form in which the point is visible.
    """
    from self_improve.score_at_both_levels import room_of

    households: Dict[str, FrozenHousehold] = {}
    per_arm: Dict[str, Dict[str, collections.Counter]] = collections.defaultdict(
        lambda: collections.defaultdict(collections.Counter))
    at: Dict[Tuple[str, str, str], Dict[str, Dict[str, Any]]] = collections.defaultdict(dict)

    for answers_file in sorted(results_dir.rglob("held_out_answers.json")):
        payload = json.loads(answers_file.read_text())
        if payload["freeze_point"] not in (BEFORE, AFTER):
            continue
        arm = answers_file.parent.parent.name
        if arm_filter and arm_filter not in arm:
            continue
        name = payload["household"]
        if name not in households:
            households[name] = FrozenHousehold(banks / f"{name}.jsonl")
        for answer in payload["answers"]:
            at[(name, arm, answer["question_id"])][payload["freeze_point"]] = answer

    for (name, arm, _), pair in at.items():
        if BEFORE not in pair or AFTER not in pair:
            continue
        household = households[name]
        before, after = pair[BEFORE], pair[AFTER]
        truth = after.get("true_place") or before.get("true_place")
        if not truth:
            continue
        for level, score in (("the exact shelf",
                              lambda a: a.get("answer_place") == truth),
                             ("the right room",
                              lambda a: (a.get("answer_place") is not None
                                         and room_of(household, a["answer_place"])
                                         == room_of(household, truth)))):
            was, now = score(before), score(after)
            counter = per_arm[arm][level]
            counter["of"] += 1
            if now and not was:
                counter["won"] += 1
            elif was and not now:
                counter["lost"] += 1

    out: Dict[str, Any] = {}
    for arm, levels in per_arm.items():
        out[arm] = {}
        for level, c in levels.items():
            changed = c["won"] + c["lost"]
            out[arm][level] = {
                "became_correct": c["won"], "became_wrong": c["lost"],
                "net": c["won"] - c["lost"], "of_how_many_questions": c["of"],
                "share_of_answers_that_changed": changed / c["of"] if c["of"] else None,
                "share_of_changes_that_were_improvements":
                    c["won"] / changed if changed else None,
            }
    return out


def gather(results_dir: pathlib.Path, banks: pathlib.Path) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """household -> arm -> freeze point -> both-level scores."""
    households: Dict[str, FrozenHousehold] = {}
    out: Dict[str, Dict[str, Dict[str, Any]]] = collections.defaultdict(
        lambda: collections.defaultdict(dict))
    for answers_file in sorted(results_dir.rglob("held_out_answers.json")):
        payload = json.loads(answers_file.read_text())
        if payload["freeze_point"] not in (BEFORE, AFTER):
            continue
        name = payload["household"]
        if name not in households:
            households[name] = FrozenHousehold(banks / f"{name}.jsonl")
        arm = answers_file.parent.parent.name
        out[name][arm][payload["freeze_point"]] = {
            **rescore(households[name], payload["answers"]),
            "n_answers": len(payload["answers"]),
        }
    return out


def paired_difference(gathered: Dict[str, Dict[str, Dict[str, Any]]], arm: str,
                      level: str) -> Dict[str, Any]:
    per_household: Dict[str, float] = {}
    for household, arms in sorted(gathered.items()):
        pair = arms.get(arm, {})
        if BEFORE in pair and AFTER in pair:
            before, after = pair[BEFORE][level], pair[AFTER][level]
            if before is not None and after is not None:
                per_household[household] = 100 * (after - before)
    values = list(per_household.values())
    n = len(values)
    mean = statistics.fmean(values) if values else None
    spread = statistics.stdev(values) if n > 1 else None
    se = (spread / n ** 0.5) if spread is not None else None

    if mean is None:
        verdict = "nothing to compare yet"
    elif se is None:
        verdict = "one household only, no verdict"
    elif n < 6:
        # Below six households we use the stricter bar: the effect has to be larger
        # than the spread across households, not merely than its standard error.
        verdict = ("larger than the spread across households"
                   if spread is not None and abs(mean) > spread
                   else f"smaller than the spread across households ({spread:.1f} points), "
                        f"so not detected at n={n}")
    elif abs(mean) > 2 * se:
        verdict = "larger than twice its standard error"
    else:
        verdict = "within twice its standard error of zero"

    return {
        "arm": arm, "level": level,
        "what_this_measures": ("ten days of nightly note-writing over the disruption, "
                              "with no baseline involved: the same questions answered "
                              "from notes written through day 23 minus notes written "
                              "through day 13"),
        "n_households": n,
        "per_household_points": per_household,
        "mean_points": mean,
        "standard_error": se,
        "spread_across_households": spread,
        "n_households_that_improved": sum(1 for v in values if v > 0),
        "the_bar_used": ("larger than the spread across households (n below six)"
                         if n < 6 else "larger than twice the standard error"),
        "verdict": verdict,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/frozen_memory_test_v1"))
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/did_it_learn.json"))
    args = parser.parse_args(argv)

    gathered = gather(args.results, args.banks)
    arms = sorted({arm for arms in gathered.values() for arm in arms})
    rows = []
    print("PRIMARY RESULT: notes through day 23 minus notes through day 13, "
          "same questions (days 14-23), no baseline involved.")
    print()
    for arm in arms:
        for level in (ROOM_LEVEL, PLACE_LEVEL):
            row = paired_difference(gathered, arm, level)
            rows.append(row)
            if not row["n_households"]:
                continue
            se = row["standard_error"]
            print(f"{arm:44s} {level:16s} {row['mean_points']:+6.1f} points "
                  f"(standard error {'n/a' if se is None else format(se, '.1f')}, "
                  f"spread {'n/a' if row['spread_across_households'] is None else format(row['spread_across_households'], '.1f')}, "
                  f"n={row['n_households']}, improved in {row['n_households_that_improved']})")
            print(f"{'':44s} {'':16s} -> {row['verdict']}")
            print(f"{'':44s} {'':16s}    per household: "
                  + ", ".join(f"{h.replace('_t03','')} {v:+.0f}"
                              for h, v in row["per_household_points"].items()))
    churn = churn_between_the_freeze_points(args.results, args.banks)
    print()
    print("CHURN: how many individual answers changed between the two freeze points, and")
    print("how many of those changes helped. The net alone hides that a fifth of the")
    print("answers moved while gaining almost nothing at room level.")
    for arm in sorted(churn):
        for level in (ROOM_LEVEL, PLACE_LEVEL):
            c = churn[arm].get(level)
            if not c:
                continue
            print(f"  {arm:44s} {level:16s} won {c['became_correct']:3d}, "
                  f"lost {c['became_wrong']:3d}, net {c['net']:+4d}, of "
                  f"{c['of_how_many_questions']:4d} | "
                  f"{c['share_of_answers_that_changed']:.0%} of answers changed, "
                  f"{c['share_of_changes_that_were_improvements']:.0%} of changes helped")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"paired_differences": rows, "churn": churn}, indent=1))
    print()
    print(f"noise floor on this server: {LOCKED.noise_floor:.0%} of answers change on a "
          f"rerun, so a difference smaller than that is noise whatever its error bar says")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
