"""Combine the search-driven cells, check them against what the run had to contain,
and report the numbers paired within household.

Clustering is on HOUSEHOLD, never on question. A per-question standard error here
comes out about four times too narrow, because the questions inside one household
share its notes, its rooms and its object set.

    python -m self_improve.combine_search_driven
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.search_driven import (FIXED_ROTATION, MEMORY_GUIDED, NEVER_SAW_IT,
                                        RANDOM, SAW_IT_OFTEN, SAW_IT_ONCE, SENSING_ARMS,
                                        sanity_assay_on_searches)

PATROL = pathlib.Path("results/self_improve/memory_factor_v1")


# ------------------------------------------------------------------ loading --


def load_cells(root: pathlib.Path) -> List[Dict[str, Any]]:
    cells = []
    for path in sorted(root.glob("hh_s*/*/*/cell.json")):
        cells.append(json.loads(path.read_text()))
        cells[-1]["_dir"] = str(path.parent)
    return cells


# ------------------------------------------------------------- the checking --


def check_a_cell(cell: Dict[str, Any], expect_last_day: int) -> List[str]:
    """What the output had to contain. A clean exit is not evidence."""
    problems: List[str] = []
    where = f"{cell['household']}/{cell['sensing_arm']}/{cell['how_memory_is_written']}"
    searches = cell["searches"]
    if not searches:
        problems.append(f"{where}: no searches at all")
        return problems
    days_seen = {r["day"] for r in searches}
    if cell["last_day"] != expect_last_day:
        problems.append(f"{where}: ran to day {cell['last_day']}, not {expect_last_day}")
    if len(cell["per_day"]) != expect_last_day + 1:
        problems.append(f"{where}: {len(cell['per_day'])} per-day rows, "
                        f"expected {expect_last_day + 1}")
    missing = set(range(1, expect_last_day + 1)) - days_seen
    if missing:
        problems.append(f"{where}: no questions on days {sorted(missing)}")
    budget = cell["budget_rooms_per_question"]
    for row in searches:
        if row["n_rooms_opened"] > budget:
            problems.append(f"{where}: {row['question_id']} opened "
                            f"{row['n_rooms_opened']} rooms, budget is {budget}")
            break
        if len(set(row["rooms_opened"])) != len(row["rooms_opened"]):
            problems.append(f"{where}: {row['question_id']} opened the same room twice")
            break
        if row["found_it"] and row["correct_place"] is not True:
            problems.append(f"{where}: {row['question_id']} found the object but is not "
                            f"scored correct - the scoring and the search disagree")
            break
    if not cell["there_was_no_patrol_and_no_warm_start"]:
        problems.append(f"{where}: a patrol or warm start was used")
    nightly = cell["nightly"]
    failed = sum(1 for n in nightly if n.get("model_call_failed"))
    if failed > 3:
        problems.append(f"{where}: the nightly note-writing call failed on {failed} nights")
    if cell["how_memory_is_written"] == "incremental edits":
        first = next((n for n in nightly if n["day"] == 1), None)
        if first is not None and not first.get("n_edits_offered"):
            problems.append(
                f"{where}: night 1 offered NO edits. This model replies {{'edits': []}} "
                f"when the explanation precedes the imperative; the arm is silently "
                f"empty and no accuracy number would show it")
        revised = sum(n.get("applied", {}).get("revise", 0) for n in nightly)
        if revised == 0:
            problems.append(f"{where}: never revised a claim - an append-only log, "
                            f"not an edited store")
    else:
        if not any(n.get("n_characters") for n in nightly):
            problems.append(f"{where}: the rewrite arm never wrote a summary")
    assay = sanity_assay_on_searches(cell)
    for concern in assay["concerns"]:
        problems.append(f"{where}: SANITY ASSAY: {concern}")
    return problems


def check_the_arms_got_the_same_questions(cells: Sequence[Dict[str, Any]]) -> List[str]:
    """The sample depends on the bank alone, so every cell of one household must
    have been asked exactly the same questions. If not, the pairing is broken."""
    problems = []
    by_household: Dict[str, Dict[str, Tuple[str, ...]]] = collections.defaultdict(dict)
    for cell in cells:
        key = f"{cell['sensing_arm']}/{cell['how_memory_is_written']}"
        by_household[cell["household"]][key] = tuple(r["question_id"] for r in cell["searches"])
    for household, arms in sorted(by_household.items()):
        distinct = {ids for ids in arms.values()}
        if len(distinct) > 1:
            sizes = {k: len(v) for k, v in arms.items()}
            problems.append(f"{household}: the arms were asked DIFFERENT questions "
                            f"({sizes}) - nothing is paired")
    return problems


# ----------------------------------------------------------- the accounting --


def patrol_observation(banks: pathlib.Path, households: Sequence[str]) -> Dict[str, Any]:
    """Room-visits and distinct objects per day in the PATROL run, so the ratio
    against the search design can be stated in one line rather than found late."""
    per_day: List[Dict[str, Any]] = []
    for name in households:
        looks_file = PATROL / name / "incremental_edits" / "looks.jsonl"
        if not looks_file.exists():
            continue
        household = FrozenHousehold(banks / f"{name}.jsonl")
        asked = set(household.asked_objects)
        by_day: Dict[int, Dict[str, Any]] = collections.defaultdict(
            lambda: {"rooms": [], "objects": set(), "residents": set()})
        for line in looks_file.open():
            row = json.loads(line)
            if row.get("kind") != "look":
                continue
            bucket = by_day[row["day"]]
            bucket["rooms"] += [t["name"] for t in row["targets"]]
            bucket["objects"].update(s["object_id"] for s in row.get("sightings", []))
            bucket["residents"].update(row.get("residents_seen", []))
        for day, bucket in sorted(by_day.items()):
            per_day.append({
                "household": name, "day": day, "design": "patrol",
                "room_visits": len(bucket["rooms"]),
                "distinct_rooms": len(set(bucket["rooms"])),
                "distinct_objects_observed": len(bucket["objects"]),
                "distinct_asked_about_objects_observed": len(bucket["objects"] & asked),
                "distinct_residents_seen": len(bucket["residents"]),
            })
    if not per_day:
        return {}
    return {
        "n_household_days": len(per_day),
        "mean_room_visits_per_day": statistics.mean(r["room_visits"] for r in per_day),
        "mean_distinct_rooms_per_day": statistics.mean(r["distinct_rooms"] for r in per_day),
        "mean_distinct_objects_per_day":
            statistics.mean(r["distinct_objects_observed"] for r in per_day),
        "mean_distinct_asked_about_objects_per_day":
            statistics.mean(r["distinct_asked_about_objects_observed"] for r in per_day),
        "mean_distinct_residents_per_day":
            statistics.mean(r["distinct_residents_seen"] for r in per_day),
        "per_day": per_day,
    }


# ------------------------------------------------------------- the numbers --


def which_side_won(mean: Optional[float], two_se: Optional[float],
                   higher_is: str, lower_is: str) -> str:
    """The signed verdict, stored beside the number rather than only printed.

    A bare mean in JSON can be read either way by a later reader who never sees the
    sentence that framed it, and a one-sided test cannot express one of its outcomes
    at all: a verdict line that could only say "the model beats it" or "not proven"
    printed "does NOT clear the bar" over a ten-point gap that cleared the bar in the
    RIVAL's favour. So every contrast carries the name of the side that won.
    """
    if mean is None:
        return "no value"
    if two_se is None:
        return f"one household, no bar ({mean:+.3f})"
    if mean > two_se:
        return f"{higher_is} ({mean:+.3f} vs 2 SE {two_se:.3f})"
    if -mean > two_se:
        return f"{lower_is} ({mean:+.3f} vs 2 SE {two_se:.3f})"
    return f"neither clears the 2 SE bar ({mean:+.3f} vs 2 SE {two_se:.3f})"


def mean_and_standard_error(values: Sequence[float]) -> Dict[str, Optional[float]]:
    """Clustered on household: one value per household, n = the number of
    households. With three households the standard error has two degrees of
    freedom and is very wide; that is the honest width, not a reason to switch to
    a per-question error bar four times too narrow."""
    values = [v for v in values if v is not None]
    if not values:
        return {"n": 0, "mean": None, "standard_error": None, "two_se": None}
    mean = statistics.mean(values)
    se = (statistics.stdev(values) / (len(values) ** 0.5)) if len(values) > 1 else None
    return {"n": len(values), "mean": mean, "standard_error": se,
            "two_se": (2 * se) if se is not None else None,
            "per_household": list(values)}


MEASURES = ("share_correct_room", "share_correct_place", "share_found_within_budget",
            "mean_rooms_opened_per_question")


def paired_differences(cells: Sequence[Dict[str, Any]], against: str = FIXED_ROTATION
                       ) -> Dict[str, Any]:
    """Every difference is taken INSIDE a household, then averaged across
    households. Never pool the arms and subtract the pooled means: a composition
    shift between households would show up as an effect."""
    index: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for cell in cells:
        index[(cell["household"], cell["how_memory_is_written"], cell["sensing_arm"])] = cell
    households = sorted({c["household"] for c in cells})
    formats = sorted({c["how_memory_is_written"] for c in cells})
    out: Dict[str, Any] = {}
    for how in formats:
        for arm in SENSING_ARMS:
            if arm == against:
                continue
            diffs: Dict[str, List[float]] = {m: [] for m in MEASURES}
            used = []
            for household in households:
                a = index.get((household, how, arm))
                b = index.get((household, how, against))
                if not a or not b:
                    continue
                used.append(household)
                for m in MEASURES:
                    va, vb = a["summary"][m], b["summary"][m]
                    if va is not None and vb is not None:
                        diffs[m].append(va - vb)
            if used:
                block: Dict[str, Any] = {"households": used}
                for m in MEASURES:
                    got = mean_and_standard_error(diffs[m])
                    cheaper = m == "mean_rooms_opened_per_question"
                    got["which_side_won"] = which_side_won(
                        got["mean"], got["two_se"],
                        higher_is=(f"{against} opens fewer rooms" if cheaper
                                   else f"{arm} is better"),
                        lower_is=(f"{arm} opens fewer rooms" if cheaper
                                  else f"{against} is better"))
                    block[m] = got
                out[f"{arm} minus {against}, {how}"] = block
    return out


def by_day_rows(cells: Sequence[Dict[str, Any]], banks: pathlib.Path) -> List[Dict[str, Any]]:
    """Tidy per-day rows with the mover / non-mover slice, days 0-31. One number for
    the run would hide the whole shape: a drop at day 14, recovery through the
    spell, a second drop at day 24."""
    rows: List[Dict[str, Any]] = []
    for cell in cells:
        movers = set(cell["movers"])
        by_day: Dict[Tuple[int, str], List[Dict[str, Any]]] = collections.defaultdict(list)
        for r in cell["searches"]:
            slice_name = "mover" if r["object_id"] in movers else "non-mover"
            by_day[(r["day"], slice_name)].append(r)
            by_day[(r["day"], "all")].append(r)
        ledger = {r["day"]: r for r in cell["per_day"]}
        for (day, slice_name), here in sorted(by_day.items()):
            scored = [r for r in here if r["correct_place"] is not None]
            rows.append({
                "household": cell["household"], "day": day,
                "period": here[0]["period"],
                "arm": cell["sensing_arm"],
                "format": cell["how_memory_is_written"],
                "slice": slice_name,
                "correct_room": sum(1 for r in scored if r["correct_room"]),
                "correct_place": sum(1 for r in scored if r["correct_place"]),
                "found": sum(1 for r in here if r["found_it"]),
                "rooms_opened": sum(r["n_rooms_opened"] for r in here),
                "total": len(scored),
                "asked": len(here),
                "room_visits_that_day": ledger.get(day, {}).get("room_visits"),
                "distinct_rooms_that_day": ledger.get(day, {}).get("distinct_rooms"),
                "distinct_objects_that_day":
                    ledger.get(day, {}).get("distinct_objects_observed"),
            })
    return rows


WINDOWS = (("settled, days 1-13", range(1, 14)),
           ("the transition, days 14-15", range(14, 16)),
           ("disrupted, days 16-23", range(16, 24)),
           ("the return, days 24-25", range(24, 26)),
           ("back to normal, days 26-31", range(26, 32)))


def the_shape_by_window(rows: Sequence[Dict[str, Any]], slice_name: str = "all"
                        ) -> Dict[str, Any]:
    """The four-phase shape, per arm, averaged over households INSIDE each window.

    One number for the run would hide it: we expect a drop at day 14, recovery
    through the spell and a second drop at day 24, and a mean over the month can
    be flat while every one of those is happening.

    Each household contributes one share per window, and the windows' shares are
    then averaged across households - never pooled question counts, which would
    weight a household by how many questions it happened to be asked.
    """
    out: Dict[str, Any] = {}
    here = [r for r in rows if r["slice"] == slice_name]
    arms = sorted({(r["arm"], r["format"]) for r in here})
    households = sorted({r["household"] for r in here})
    for arm, fmt in arms:
        block: Dict[str, Any] = {}
        for label, days in WINDOWS:
            per_household_room, per_household_found, per_household_rooms = [], [], []
            for household in households:
                mine = [r for r in here if r["arm"] == arm and r["format"] == fmt
                        and r["household"] == household and r["day"] in days]
                total = sum(r["total"] for r in mine)
                asked = sum(r["asked"] for r in mine)
                if total:
                    per_household_room.append(sum(r["correct_room"] for r in mine) / total)
                if asked:
                    per_household_found.append(sum(r["found"] for r in mine) / asked)
                    per_household_rooms.append(sum(r["rooms_opened"] for r in mine) / asked)
            block[label] = {
                "share_correct_room": mean_and_standard_error(per_household_room),
                "share_found": mean_and_standard_error(per_household_found),
                "mean_rooms_opened": mean_and_standard_error(per_household_rooms),
            }
        out[f"{arm} / {fmt}"] = block
    return out


def the_settled_slope(rows: Sequence[Dict[str, Any]], slice_name: str = "all"
                      ) -> Dict[str, Any]:
    """Is the robot LEARNING the ordinary fortnight, days 1-13?

    With no day-0 walkthrough the settled routine has to be learned from scratch, so
    days 1-13 should show a CLIMB, not a plateau. If the settled period is flat and
    low the robot never learned the ordinary routine, the disruption has nothing to
    break, and every later number is about noise - the same failure the night-shift
    control was built to detect.

    Reported as the least-squares slope in accuracy points per day, per household,
    then averaged across households; and as the plain difference between the first
    four settled days and the last four, which needs no model.
    """
    out: Dict[str, Any] = {}
    here = [r for r in rows if r["slice"] == slice_name and 1 <= r["day"] <= 13]
    for arm, fmt in sorted({(r["arm"], r["format"]) for r in here}):
        slopes, firsts, lasts = [], [], []
        for household in sorted({r["household"] for r in here}):
            mine = sorted((r for r in here if r["arm"] == arm and r["format"] == fmt
                           and r["household"] == household), key=lambda r: r["day"])
            points = [(r["day"], r["correct_room"] / r["total"])
                      for r in mine if r["total"]]
            if len(points) < 5:
                continue
            n = len(points)
            mean_x = sum(x for x, _ in points) / n
            mean_y = sum(y for _, y in points) / n
            var = sum((x - mean_x) ** 2 for x, _ in points)
            if not var:
                continue
            slopes.append(sum((x - mean_x) * (y - mean_y) for x, y in points) / var)
            early = [r for r in mine if r["day"] <= 4 and r["total"]]
            late = [r for r in mine if r["day"] >= 10 and r["total"]]
            if early and late:
                firsts.append(sum(r["correct_room"] for r in early)
                              / sum(r["total"] for r in early))
                lasts.append(sum(r["correct_room"] for r in late)
                             / sum(r["total"] for r in late))
        out[f"{arm} / {fmt}"] = {
            "slope_in_accuracy_points_per_day": mean_and_standard_error(
                [s * 100 for s in slopes]),
            "days_1_to_4": mean_and_standard_error(firsts),
            "days_10_to_13": mean_and_standard_error(lasts),
            "the_climb": mean_and_standard_error(
                [b - a for a, b in zip(firsts, lasts)]),
        }
    return out


def the_error_split(cells: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Pooled and per arm, from the structured sighting records. No text matcher."""
    out: Dict[str, Any] = {}
    groups = {"pooled": list(cells)}
    for arm in SENSING_ARMS:
        groups[arm] = [c for c in cells if c["sensing_arm"] == arm]
    for label, here in groups.items():
        totals = collections.Counter()
        for cell in here:
            split = cell["summary"]["the_three_way_error_split"]
            for bucket in (NEVER_SAW_IT, SAW_IT_ONCE, SAW_IT_OFTEN):
                totals[bucket] += split[bucket]
        n = sum(totals.values())
        out[label] = {
            "n_errors": n,
            **{bucket: {"n": totals[bucket], "share": (totals[bucket] / n) if n else None}
               for bucket in (NEVER_SAW_IT, SAW_IT_ONCE, SAW_IT_OFTEN)},
            "share_that_is_a_sensing_failure": (totals[NEVER_SAW_IT] / n) if n else None,
        }
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/search_driven"))
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--last-day", type=int, default=31)
    args = parser.parse_args(argv)

    cells = load_cells(args.root)
    if not cells:
        print(f"no cells under {args.root}")
        return 1
    households = sorted({c["household"] for c in cells})

    problems: List[str] = []
    for cell in cells:
        problems += check_a_cell(cell, args.last_day)
    problems += check_the_arms_got_the_same_questions(cells)

    per_cell = [{
        "household": c["household"], "sensing_arm": c["sensing_arm"],
        "how_memory_is_written": c["how_memory_is_written"],
        **{k: c["summary"][k] for k in
           ("n_questions_scored", "share_correct_room", "share_correct_place",
            "share_found_within_budget", "mean_rooms_opened_per_question",
            "share_correct_place_movers", "share_correct_place_non_movers",
            "n_choice_calls_that_failed")},
        "share_never_saw_it": c["summary"]["the_three_way_error_split"]["share_never_saw_it"],
        **{f"observation_{k}": v for k, v in c["summary"]["observation"].items()},
    } for c in cells]

    report = {
        "households": households,
        "n_cells": len(cells),
        "problems_found_checking_the_output": problems,
        "per_cell": per_cell,
        "across_households_clustered_on_household": {
            f"{arm} / {how}": {
                m: mean_and_standard_error([c["summary"][m] for c in cells
                                            if c["sensing_arm"] == arm
                                            and c["how_memory_is_written"] == how])
                for m in MEASURES}
            for arm in SENSING_ARMS
            for how in sorted({c["how_memory_is_written"] for c in cells})},
        "paired_against_the_fixed_rotation": paired_differences(cells, FIXED_ROTATION),
        "paired_against_random": paired_differences(cells, RANDOM),
        "the_three_way_error_split": the_error_split(cells),
        "the_observation_confound": {
            "search": {
                f"{arm} / {how}": {
                    k: mean_and_standard_error([c["summary"]["observation"][k] for c in cells
                                                if c["sensing_arm"] == arm
                                                and c["how_memory_is_written"] == how])["mean"]
                    for k in ("mean_room_visits_per_day", "mean_distinct_rooms_per_day",
                              "mean_distinct_objects_per_day",
                              "mean_distinct_asked_about_objects_per_day")}
                for arm in SENSING_ARMS
                for how in sorted({c["how_memory_is_written"] for c in cells})},
            "patrol": patrol_observation(args.banks, households),
        },
    }
    patrol = report["the_observation_confound"]["patrol"]
    if patrol:
        # Averaged over the search cells rather than taken from whichever arm the
        # dict happened to yield first: the arms differ in room-visits (that is a
        # result), so naming one arbitrarily would put a different number in the
        # sentence depending on dict order.
        search_cells = report["the_observation_confound"]["search"].values()
        a_search = {k: statistics.mean([c[k] for c in search_cells if c[k] is not None])
                    for k in ("mean_room_visits_per_day", "mean_distinct_rooms_per_day",
                              "mean_distinct_objects_per_day",
                              "mean_distinct_asked_about_objects_per_day")}
        report["the_observation_confound"]["the_ratio_in_one_line"] = (
            f"averaged over the six search cells, search opens "
            f"{a_search['mean_room_visits_per_day']:.1f} rooms a day against "
            f"the patrol's {patrol['mean_room_visits_per_day']:.1f}, and observes "
            f"{a_search['mean_distinct_objects_per_day']:.1f} distinct objects a day "
            f"against {patrol['mean_distinct_objects_per_day']:.1f} - "
            f"{a_search['mean_room_visits_per_day'] / max(1e-9, patrol['mean_room_visits_per_day']):.0f}x "
            f"the room-visits. The search arms are NOT comparable like for like with "
            f"the patrol results; the three search arms share a budget and are "
            f"comparable with each other.")
        del patrol["per_day"]

    rows = by_day_rows(cells, args.banks)
    report["the_shape_by_window"] = the_shape_by_window(rows, "all")
    report["the_shape_by_window_movers_only"] = the_shape_by_window(rows, "mover")
    report["did_it_learn_the_settled_fortnight"] = the_settled_slope(rows, "all")
    args.root.mkdir(parents=True, exist_ok=True)
    (args.root / "combined.json").write_text(json.dumps(report, indent=1))
    with (args.root / "accuracy_by_day.jsonl").open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    fields = ["household", "day", "period", "arm", "format", "slice", "correct_room",
              "correct_place", "found", "rooms_opened", "total", "asked",
              "room_visits_that_day", "distinct_rooms_that_day", "distinct_objects_that_day"]
    with (args.root / "accuracy_by_day.csv").open("w") as fh:
        fh.write(",".join(fields) + "\n")
        for row in rows:
            fh.write(",".join(str(row.get(f, "")) for f in fields) + "\n")

    print(f"{len(cells)} cells, households {households}")
    if problems:
        print(f"\n!! {len(problems)} PROBLEMS CHECKING THE OUTPUT:")
        for p in problems:
            print("   ", p)
    else:
        print("\nthe output contains everything it had to contain")
    print()
    head = (f"{'household':11s} {'arm':22s} {'format':18s} {'n':>4s} {'room':>6s} "
            f"{'shelf':>6s} {'found':>6s} {'rooms/q':>8s} {'neverSaw':>9s} {'obj/day':>8s}")
    print(head)
    for r in per_cell:
        print(f"{r['household']:11s} {r['sensing_arm']:22s} {r['how_memory_is_written']:18s} "
              f"{r['n_questions_scored']:4d} "
              f"{(r['share_correct_room'] or 0):6.1%} {(r['share_correct_place'] or 0):6.1%} "
              f"{(r['share_found_within_budget'] or 0):6.1%} "
              f"{(r['mean_rooms_opened_per_question'] or 0):8.2f} "
              f"{(r['share_never_saw_it'] or 0):9.1%} "
              f"{(r['observation_mean_distinct_objects_per_day'] or 0):8.1f}")
    print()
    for label, block in report["paired_against_the_fixed_rotation"].items():
        print(f"--- {label} (paired inside household, n={block[MEASURES[0]]['n']})")
        for m in MEASURES:
            b = block[m]
            if b["mean"] is None:
                continue
            bar = "" if b["two_se"] is None else f" (2 SE {b['two_se']:+.3f})"
            print(f"      {m:32s} {b['mean']:+.3f}{bar}  per household "
                  f"{[round(v, 3) for v in b['per_household']]}")
    print()
    print("--- did it learn the settled fortnight? (days 1-13, room level, no priors)")
    for label, block in report["did_it_learn_the_settled_fortnight"].items():
        slope = block["slope_in_accuracy_points_per_day"]
        climb = block["the_climb"]
        if slope["mean"] is None:
            continue
        bar = "" if slope["two_se"] is None else f" (2 SE {slope['two_se']:.2f})"
        line = f"      {label:44s} slope {slope['mean']:+.2f} pts/day{bar}"
        if block["days_1_to_4"]["mean"] is not None and \
                block["days_10_to_13"]["mean"] is not None:
            line += (f", days 1-4 {block['days_1_to_4']['mean']:.1%} -> days 10-13 "
                     f"{block['days_10_to_13']['mean']:.1%} "
                     f"(climb {climb['mean']:+.1%})")
        print(line)
    print()
    for label, block in report["the_shape_by_window"].items():
        print(f"--- the shape by window: {label}")
        for window, b in block.items():
            room = b["share_correct_room"]["mean"]
            found = b["share_found"]["mean"]
            opened = b["mean_rooms_opened"]["mean"]
            if room is None:
                continue
            print(f"      {window:28s} room {room:6.1%}  found {found:6.1%}  "
                  f"rooms/q {opened:.2f}")
    print()
    for label, block in report["the_shape_by_window_movers_only"].items():
        print(f"--- movers only: {label}")
        for window, b in block.items():
            room = b["share_correct_room"]["mean"]
            if room is None:
                continue
            print(f"      {window:28s} room {room:6.1%}  "
                  f"found {b['share_found']['mean']:6.1%}")
    print()
    print(json.dumps(report["the_three_way_error_split"], indent=1))
    if report["the_observation_confound"].get("the_ratio_in_one_line"):
        print()
        print("OBSERVATION CONFOUND:", report["the_observation_confound"]["the_ratio_in_one_line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
