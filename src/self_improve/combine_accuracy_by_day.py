"""Gather the per-day parts into one tidy table, and read the four shapes off it.

The table is the deliverable; the shapes below are a reading of it, not a
replacement for it. One row per household, day, memory format, condition and
mover/non-mover slice, with COUNTS rather than only shares, so anything can be
re-pooled downstream.

Two rules this file obeys, each of which has already cost this project a result:

  clustering is on HOUSEHOLD, never on question. Each household contributes one
  share per day per line, and the standard error is the spread of those ten
  numbers. A per-question binomial error here comes out about four times too
  narrow.

  an effect is claimed only when the paired mean exceeds TWICE its standard
  error, and a null is always reported with what it excludes.

The phase contrasts are all WITHIN household: each household's own difference
between two day windows, then the mean and standard error of those differences.
At ten households a paired difference is far better behaved than a difference of
pooled shares, which also moves when the composition of the answerable questions
moves.

    python -m self_improve.combine_accuracy_by_day
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import pathlib
import statistics
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

DEFAULT_OUT = pathlib.Path("results/self_improve/accuracy_by_day")

SHELF = "share_right_shelf"
ROOM = "share_right_room"
LEVELS = {"the exact shelf": ("n_right_shelf", SHELF),
          "the right room": ("n_right_room", ROOM)}

# The windows the four expected shapes live in. Chosen from the scenario's own
# calendar - settled 1-13, disrupted 14-23, back to normal 24-31 - and fixed here
# before any number was looked at.
WINDOWS = {
    "last ordinary days": (12, 13),
    "first disrupted days": (14, 15),
    "end of the disrupted spell": (21, 23),
    "first days back to normal": (24, 25),
    "last days back to normal": (29, 31),
    # CHOSEN AFTER SEEING THE CURVE, and labelled as such on every row that uses
    # them. Day 14 is the day the resident falls ill and the objects move DURING
    # it, so the day-14 questions are asked partly before the change: on the
    # movers, day 14 sits at the ordinary level and the fall appears on day 15.
    # The same is true of day 24 and the return. The pre-registered windows above
    # are reported too and neither replaces the other.
    "the first FULL disrupted days": (15, 17),
    "the first FULL days back to normal": (25, 27),
}

POST_HOC = {"the drop at the onset, full days only",
            "the drop at the return, full days only",
            "the climb through the spell, full days only"}

CONTRASTS = [
    ("the drop at the onset", "first disrupted days", "last ordinary days",
     "Oliver's prediction: both lines fall when the resident falls ill on day 14"),
    ("the climb through the spell", "end of the disrupted spell", "first disrupted days",
     "the unfrozen line should climb as the notes are revised; the frozen line "
     "should stay flat because nothing is written"),
    ("the drop at the return", "first days back to normal", "end of the disrupted spell",
     "the unfrozen line should fall again; the FROZEN line should RISE, because the "
     "world comes back to the routine it still holds. A positive number on the "
     "frozen line here is the paper's figure"),
    ("the recovery after the return", "last days back to normal", "first days back to normal",
     "the unfrozen line should climb again"),
    ("the drop at the onset, full days only", "the first FULL disrupted days",
     "last ordinary days",
     "POST HOC WINDOW. The same drop, skipping day 14, the day on which the change "
     "itself happens and the questions straddle it"),
    ("the climb through the spell, full days only", "end of the disrupted spell",
     "the first FULL disrupted days",
     "POST HOC WINDOW. Recovery measured from the bottom of the fall rather than "
     "from the transition day"),
    ("the drop at the return, full days only", "the first FULL days back to normal",
     "end of the disrupted spell",
     "POST HOC WINDOW. On the frozen line a POSITIVE number here is the bounce: the "
     "world has come back to the routine the memory still holds"),
]


def read_parts(out_dir: pathlib.Path) -> Tuple[List[dict], List[dict]]:
    rows, answers = [], []
    for path in sorted((out_dir / "parts").glob("*.rows.jsonl")):
        rows += [json.loads(line) for line in path.open() if line.strip()]
    for path in sorted((out_dir / "parts").glob("*.answers.jsonl")):
        answers += [json.loads(line) for line in path.open() if line.strip()]
    return rows, answers


def what_is_missing(rows: Sequence[dict], days: Sequence[int],
                    households: Sequence[str]) -> Dict[str, Any]:
    """Check the output against what it MUST contain, not against whether the jobs
    exited cleanly. A run that looks complete because everything it did do
    succeeded is the dominant failure mode here."""
    have = {(r["household"], r["memory_format"], r["condition"], r["day"])
            for r in rows if r["slice"] == "all objects"}
    conditions = sorted({r["condition"] for r in rows})
    want = {(h, f, c, d) for h in households
            for f in ("wholesale rewrite", "incremental edits")
            for c in conditions for d in days}
    missing = sorted(want - have)
    bad_night = [r for r in rows
                 if r["condition"] == "frozen at day 13"
                 and r["notes_actually_from_night"] != 13]
    bad_unfrozen = [r for r in rows
                    if r["condition"] == "unfrozen"
                    and r["notes_actually_from_night"] != min(r["day"] - 1, 28)]
    bad_zero = [r for r in rows
                if r["condition"] == "zero looks after the warm start"
                and r["notes_actually_from_night"] != 0]
    # Two identities that MUST hold if the reconstruction is right, and that no
    # accuracy figure would reveal if it were not: on day 14 the unfrozen memory is
    # night 13, which is exactly the frozen line; on day 1 it is night 0, which is
    # exactly the zero-look line. Same notes, same questions, so the counts must be
    # equal cell for cell.
    index = {(r["household"], r["memory_format"], r["condition"], r["day"],
              r["slice"]): r for r in rows}
    identities = []
    for day, other in ((14, "frozen at day 13"),
                       (1, "zero looks after the warm start")):
        agree = disagree = 0
        for key, r in index.items():
            if key[3] != day or key[2] != "unfrozen":
                continue
            twin = index.get((key[0], key[1], other, day, key[4]))
            if twin is None:
                continue
            same = ((r["n_right_shelf"], r["n_right_room"], r["n_scored"])
                    == (twin["n_right_shelf"], twin["n_right_room"], twin["n_scored"]))
            agree += same
            disagree += not same
        identities.append({
            "identity": f"on day {day} the unfrozen memory IS the '{other}' memory",
            "cells_checked": agree + disagree, "cells_that_agree": agree,
            "cells_that_disagree": disagree, "holds": disagree == 0})

    unparsed = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        if r["slice"] != "all objects":
            continue
        key = (r["household"], r["memory_format"], r["condition"])
        unparsed[key][0] += r["n_unparsed"]
        unparsed[key][1] += r["n_asked"]
    noisy = {"/".join(k): round(v[0] / v[1], 3) for k, v in unparsed.items()
             if v[1] and v[0] / v[1] > 0.10}
    return {
        "n_cells_expected": len(want),
        "n_cells_present": len(want) - len(missing),
        "missing_cells": [dict(zip(("household", "memory_format", "condition", "day"), m))
                          for m in missing[:60]],
        "n_missing": len(missing),
        "frozen_rows_not_from_night_13": len(bad_night),
        "zero_look_rows_not_from_night_0": len(bad_zero),
        "unfrozen_rows_not_from_the_previous_night": len(bad_unfrozen),
        "cells_over_the_10pc_unparsed_bar": noisy,
        "identities_that_must_hold": identities,
        "complete": all(i["holds"] for i in identities) and not missing and not bad_night and not bad_unfrozen and not bad_zero,
    }


def per_day(rows: Sequence[dict]) -> List[dict]:
    """One record per day, line, slice and scoring level: each household's own
    share, then the mean and the household-clustered standard error of those."""
    grouped: Dict[Tuple, List[dict]] = collections.defaultdict(list)
    for r in rows:
        grouped[(r["day"], r["period"], r["memory_format"], r["condition"],
                 r["slice"])].append(r)
    out = []
    for (day, period, fmt, condition, slice_name), group in sorted(grouped.items()):
        record = {"day": day, "period": period, "memory_format": fmt,
                  "condition": condition, "slice": slice_name,
                  "n_households": len({g["household"] for g in group}),
                  "n_questions_scored": sum(g["n_scored"] for g in group),
                  "notes_from_night": sorted({g["notes_actually_from_night"]
                                              for g in group})}
        for level, (count_field, _) in LEVELS.items():
            shares = [g[count_field] / g["n_scored"] for g in group if g["n_scored"]]
            pooled_correct = sum(g[count_field] for g in group)
            pooled_n = sum(g["n_scored"] for g in group)
            record[level] = {
                # NAMED estimators: the two are not interchangeable and a figure
                # must say which of them its line is.
                "mean_of_household_shares": statistics.fmean(shares) if shares else None,
                "household_clustered_standard_error":
                    (statistics.stdev(shares) / len(shares) ** 0.5)
                    if len(shares) > 1 else None,
                "pooled_share_over_all_questions":
                    (pooled_correct / pooled_n) if pooled_n else None,
                "n_households_contributing": len(shares),
                "n_correct_pooled": pooled_correct,
                "n_scored_pooled": pooled_n,
            }
        out.append(record)
    return out


def window_share(rows: Sequence[dict], window: Tuple[int, int],
                 count_field: str) -> Optional[float]:
    lo, hi = window
    inside = [r for r in rows if lo <= r["day"] <= hi and r["n_scored"]]
    n = sum(r["n_scored"] for r in inside)
    return (sum(r[count_field] for r in inside) / n) if n else None


def contrasts(rows: Sequence[dict]) -> List[dict]:
    """Each household's own before/after difference, then the paired mean and its
    standard error. Nothing here is a difference of pooled shares."""
    by_line: Dict[Tuple, Dict[str, List[dict]]] = collections.defaultdict(
        lambda: collections.defaultdict(list))
    for r in rows:
        by_line[(r["memory_format"], r["condition"], r["slice"])][r["household"]].append(r)

    out = []
    for (fmt, condition, slice_name), households in sorted(by_line.items()):
        for level, (count_field, _) in LEVELS.items():
            for name, after, before, why in CONTRASTS:
                paired = {}
                for household, household_rows in households.items():
                    a = window_share(household_rows, WINDOWS[after], count_field)
                    b = window_share(household_rows, WINDOWS[before], count_field)
                    if a is not None and b is not None:
                        paired[household] = 100 * (a - b)
                if len(paired) < 2:
                    continue
                values = list(paired.values())
                mean = statistics.fmean(values)
                se = statistics.stdev(values) / len(values) ** 0.5
                out.append({
                    "memory_format": fmt, "condition": condition, "slice": slice_name,
                    "scoring_level": level, "contrast": name,
                    "what_it_is": f"{after} {WINDOWS[after]} minus {before} "
                                  f"{WINDOWS[before]}, in points",
                    "why_it_matters": why,
                    "window_chosen_after_seeing_the_curve": name in POST_HOC,
                    "points": round(mean, 1),
                    "household_clustered_standard_error": round(se, 1),
                    "n_households": len(values),
                    "same_direction_in": sum(1 for v in values if v * mean > 0),
                    "detected_at_two_standard_errors": abs(mean) > 2 * se,
                    "what_a_null_here_excludes":
                        f"a true effect larger than {2 * se:.1f} points in either "
                        f"direction is unlikely given this spread",
                    "per_household": {k: round(v, 1) for k, v in sorted(paired.items())},
                })
    return out


PAIRS = [
    ("unfrozen", "frozen at day 13",
     "what CONTINUING to look and revise after day 13 is worth"),
    ("frozen at day 13", "zero looks after the warm start",
     "what THIRTEEN DAYS of looking in one room a day is worth, over the single "
     "walkthrough of the whole house every arm starts with"),
    ("unfrozen", "zero looks after the warm start",
     "what the whole month of looking is worth over the walkthrough alone"),
]


def learning_minus_not_learning(rows: Sequence[dict]) -> List[dict]:
    """What the looking actually bought, paired within household.

    The shapes read off each line on its own are not enough: the frozen line turns
    out to climb through the disrupted spell as well, so a climb is not by itself
    evidence that anything was learned. The only thing that is, is one line MINUS
    another in the same household and the same window, which is what this computes
    for each pair in PAIRS.
    """
    by: Dict[Tuple, Dict[str, List[dict]]] = collections.defaultdict(
        lambda: collections.defaultdict(list))
    for r in rows:
        by[(r["memory_format"], r["slice"], r["condition"])][r["household"]].append(r)
    out = []
    for fmt in sorted({r["memory_format"] for r in rows}):
        for slice_name in sorted({r["slice"] for r in rows}):
            for better, worse, what in PAIRS:
                more = by[(fmt, slice_name, better)]
                less = by[(fmt, slice_name, worse)]
                if not more or not less:
                    continue
                for level, (count_field, _) in LEVELS.items():
                    for window_name, window in WINDOWS.items():
                        paired = {}
                        for household in sorted(set(more) & set(less)):
                            a = window_share(more[household], window, count_field)
                            b = window_share(less[household], window, count_field)
                            if a is not None and b is not None:
                                paired[household] = 100 * (a - b)
                        if len(paired) < 2:
                            continue
                        values = list(paired.values())
                        mean = statistics.fmean(values)
                        se = statistics.stdev(values) / len(values) ** 0.5
                        out.append({
                            "memory_format": fmt, "slice": slice_name,
                            "scoring_level": level, "window": window_name,
                            "days": list(window),
                            "comparison": f"{better} minus {worse}",
                            "what_it_is": f"{better} minus {worse}, paired within "
                                          f"household, in points",
                            "what_it_measures": what,
                            "points": round(mean, 1),
                            "household_clustered_standard_error": round(se, 1),
                            "n_households": len(values),
                            "same_direction_in": sum(1 for v in values if v * mean > 0),
                            "detected_at_two_standard_errors": abs(mean) > 2 * se,
                            "what_a_null_here_excludes":
                                f"a true gain larger than {2 * se:.1f} points in this "
                                f"window is unlikely given this spread",
                            "per_household": {k: round(v, 1)
                                              for k, v in sorted(paired.items())},
                        })
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    parser.add_argument("--days", type=int, nargs="+", default=list(range(1, 32)))
    args = parser.parse_args(argv)

    rows, answers = read_parts(args.out)
    if not rows:
        print("no parts yet")
        return 1
    households = sorted({r["household"] for r in rows})

    (args.out / "rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    fields = sorted({k for r in rows for k in r})
    with (args.out / "rows.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (args.out / "answers.jsonl").write_text(
        "".join(json.dumps(a) + "\n" for a in answers))

    check = what_is_missing(rows, args.days, households)
    daily = per_day(rows)
    found = contrasts(rows)
    (args.out / "is_it_complete.json").write_text(json.dumps(check, indent=1))
    (args.out / "per_day.json").write_text(json.dumps(daily, indent=1))
    (args.out / "the_four_shapes.json").write_text(json.dumps(found, indent=1))
    bought = learning_minus_not_learning(rows)
    (args.out / "what_the_learning_bought.json").write_text(json.dumps(bought, indent=1))
    (args.out / "DATA_DICTIONARY.json").write_text(json.dumps(DICTIONARY, indent=1))

    print(f"{len(rows)} rows, {len(answers)} answers, {len(households)} households")
    print(f"complete: {check['complete']}  missing cells: {check['n_missing']}"
          f"  frozen rows off night 13: {check['frozen_rows_not_from_night_13']}"
          f"  unfrozen rows off the previous night: "
          f"{check['unfrozen_rows_not_from_the_previous_night']}")
    for identity in check["identities_that_must_hold"]:
        print(f"  {identity['identity']}: {identity['cells_that_agree']}/"
              f"{identity['cells_checked']} agree -> "
              f"{'holds' if identity['holds'] else 'BROKEN'}")
    if check["cells_over_the_10pc_unparsed_bar"]:
        print("  over the unparsed bar:", check["cells_over_the_10pc_unparsed_bar"])
    print()
    order = ["unfrozen", "frozen at day 13", "zero looks after the warm start"]
    present = [c for c in order if c in {r["condition"] for r in rows}]
    lines = [(f, c) for f in ("wholesale rewrite", "incremental edits")
             for c in present]
    for slice_name in ("objects the disruption moved", "objects that never moved",
                       "all objects"):
        for level in LEVELS:
            print(f"=== {slice_name} | {level} | mean of household shares "
                  f"+- one household-clustered standard error (n households)")
            index = {(d["day"], d["memory_format"], d["condition"]): d for d in daily
                     if d["slice"] == slice_name}
            short = {"unfrozen": "unfroz", "frozen at day 13": "froz13",
                     "zero looks after the warm start": "zerolk"}
            print("day  " + "  ".join(f"{f.split()[0][:5]}/{short.get(c, c[:6]):11s}"
                                      for f, c in lines))
            for day in args.days:
                bits = []
                for fmt, condition in lines:
                    d = index.get((day, fmt, condition))
                    cell = d[level] if d else None
                    if not cell or cell["mean_of_household_shares"] is None:
                        bits.append("       -       ")
                    else:
                        bits.append(
                            f"{100*cell['mean_of_household_shares']:5.1f}"
                            f"+-{100*(cell['household_clustered_standard_error'] or 0):4.1f}"
                            f"({cell['n_households_contributing']:2d})")
                mark = " " if day <= 13 else ("*" if day <= 23 else "+")
                print(f"{day:3d}{mark} " + "  ".join(bits))
            print()
    print("=== the shapes, paired within household, points. * = window chosen after "
          "seeing the curve")
    for slice_name in ("objects the disruption moved", "all objects",
                       "objects that never moved"):
        for row in found:
            if row["slice"] != slice_name:
                continue
            verdict = "DETECTED" if row["detected_at_two_standard_errors"] else "not detected"
            star = "*" if row["window_chosen_after_seeing_the_curve"] else " "
            print(f"{row['slice'][:14]:14s} | {row['scoring_level']:15s} | "
                  f"{row['memory_format']:18s} | {row['condition']:16s} | "
                  f"{star}{row['contrast']:44s} "
                  f"{row['points']:+6.1f} +- {row['household_clustered_standard_error']:4.1f} "
                  f"({row['same_direction_in']}/{row['n_households']}) {verdict}")
        print()
    print("=== what the looking bought, paired within household, on the objects the "
          "disruption moved, points")
    for better, worse, what in PAIRS:
        shown = [r for r in bought
                 if r["slice"] == "objects the disruption moved"
                 and r["comparison"] == f"{better} minus {worse}"]
        if not shown:
            continue
        print(f"--- {better} minus {worse}: {what}")
        for row in shown:
            verdict = ("DETECTED" if row["detected_at_two_standard_errors"]
                       else "not detected")
            print(f"    {row['scoring_level']:15s} | {row['memory_format']:18s} | "
                  f"{row['window']:36s} {row['points']:+6.1f} +- "
                  f"{row['household_clustered_standard_error']:4.1f} "
                  f"({row['same_direction_in']}/{row['n_households']}) {verdict}")
    print(f"\nwrote {args.out}/rows.jsonl, rows.csv, per_day.json, "
          f"the_four_shapes.json, what_the_learning_bought.json, is_it_complete.json")
    return 0


DICTIONARY = {
    "what_this_is": (
        "Answering accuracy on every day of a 31-day month, for a robot that looks in "
        "one room a day and answers 'where is X?' from its own nightly notes alone. "
        "Days 1-13 are the ordinary fortnight, days 14-23 one resident is ill and "
        "stays home, days 24-31 ordinary life returns. No nightly writing was redone "
        "for this table: the memory as of each day is reconstructed from the notes' "
        "own history, and only the ANSWERING was rerun."),
    "files": {
        "rows.jsonl / rows.csv": "the tidy table, one row per household, day, memory "
                                 "format, condition and slice",
        "answers.jsonl": "every individual answer, for re-slicing",
        "per_day.json": "per day and line: each household's share, their mean, and the "
                        "household-clustered standard error",
        "the_four_shapes.json": "the paired within-household phase contrasts",
        "is_it_complete.json": "the output checked against what it must contain",
    },
    "row_fields": {
        "household": "one of ten frozen households, hh_s0_t03 .. hh_s9_t03",
        "day": "day index, 1 to 31",
        "period": "settled (1-13), disrupted (14-23), back to normal (24-31)",
        "memory_format": "'wholesale rewrite' rewrites the whole summary each night; "
                         "'incremental edits' makes small evidence-linked edits to a "
                         "claim store",
        "condition": "'unfrozen' answers day D with the notes as at the end of night "
                     "D-1, so the memory keeps learning; 'frozen at day 13' answers "
                     "EVERY day with the notes as at the end of night 13; 'zero looks "
                     "after the warm start' answers EVERY day with the notes as at the "
                     "end of night 0, the single walkthrough of the whole house that "
                     "every arm is given before day 1 - the robot never looks again. "
                     "frozen minus zero-looks is what thirteen days of one room a day "
                     "buys; unfrozen minus frozen is what continuing to look buys.",
        "notes_wanted_from_night": "the night the condition asks for",
        "notes_actually_from_night": "the night it came from. These differ only after "
                                     "night 28, the last night that was written, so "
                                     "days 30 and 31 in the unfrozen condition are "
                                     "answered with a memory 1 and 2 nights stale. "
                                     "Nothing is hidden: filter on "
                                     "notes_stale_by_nights == 0 to drop them.",
        "notes_stale_by_nights": "wanted minus actual; 0 everywhere except days 30-31 "
                                 "unfrozen",
        "slice": "'all objects'; 'objects the disruption moved'; 'objects that never "
                 "moved'. Mover status is measured over daytime hours, the study's "
                 "locked choice, per which_objects_moved.py",
        "n_asked": "questions put to the model in this cell",
        "n_scored": "of those, the ones whose answer parsed onto a real spot",
        "n_unparsed": "n_asked minus n_scored",
        "n_right_shelf": "answers naming the exact spot the object was in",
        "n_right_room": "answers naming a spot in the right room. THE PRIMARY LEVEL: "
                        "a robot that walks into the right room has found the thing",
        "read_budget_lines": "lines of notes either format may put in a prompt; 8, the "
                             "locked setting, below one line per asked object in 9 of "
                             "the 10 households",
        "mean_lines_of_notes_available": "how many lines the memory held, before the "
                                         "budget cut it",
        "share_where_the_read_budget_bit": "share of questions where the memory held "
                                           "more lines than the budget would show",
    },
    "how_to_pool": (
        "Cluster on household, never on question: take each household's own share, "
        "then the mean and the standard deviation over households divided by the root "
        "of ten. A per-question binomial error on this data comes out about four times "
        "too narrow. Two estimators appear in per_day.json under different names - "
        "mean_of_household_shares and pooled_share_over_all_questions - and a figure "
        "must say which one its line is; they differ when households contribute "
        "different numbers of answerable questions."),
    "eight_questions_a_day": (
        "Each household-day contributes at most 8 questions, taken evenly across the "
        "day's 24 rather than as the first 8 (a leading slice would make every number "
        "a statement about the morning). The same 8 go to all four lines, so the lines "
        "are paired question by question."),
    "unparsed_answers_are_abstentions": (
        "0.8% of answers name no spot on the list. Reading them shows they are honest "
        "abstentions: the memory never wrote that object down, so the model says so "
        "instead of guessing. They are EXCLUDED from n_scored, which slightly flatters "
        "a memory that is simply silent about an object - most of all the zero-look "
        "line, and hh_s1_t03 / wholesale rewrite / zero looks, the one cell above 10% "
        "(12%). To score an abstention as wrong instead, divide n_right_* by n_asked "
        "rather than n_scored; both counts are on every row."),
    "sampling_caveat": (
        "A question is dropped when the object was out of the house or in a pocket, so "
        "a day can contribute fewer than 8. n_asked and n_scored are on every row."),
}


if __name__ == "__main__":
    raise SystemExit(main())
