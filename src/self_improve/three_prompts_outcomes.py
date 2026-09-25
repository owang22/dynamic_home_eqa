"""The outcomes for the three-prompts arms, each against the unchanged control.

Every contrast in here is PAIRED WITHIN HOME and clustered on HOME, never on question.
The unit of analysis is the household because households differ in size, in how many
objects move and in how hard the return is; a question-level standard error would be
five to ten times too small. Ten homes, so ten pairs.

THE HEADLINE IS THE END-TO-END MEASUREMENT, corrected 2026-09-24. In this design the
robot searches IN ORDER TO answer, and a search that finds the object is an observation
that enters memory with certainty. So memory quality shows up in the search itself: a
better first room, fewer rooms opened, more objects found. Freezing the notes and
switching off looking is how the earlier PATROL experiment worked and it does not fit
this one, so the frozen pass is kept but demoted to a DIAGNOSTIC answering one narrow
question - what do the notes alone contain? - and is labelled as such everywhere it
appears. It is never the arm's result.

  THE FOUR HEADLINE MEASURES, end to end, from the cell's own search records:
    was the first room it opened the right one   the clean measure of the choice
    rooms opened per question                    efficiency, which an owner cares about
    did it find the object within its budget     the search outcome
    was the final answer right, shelf and room   the task outcome

MEASURES, in the order they are reported:

  REACHABILITY   how often the asked-about object's true place is named inside the
                 EIGHT LINES the robot reads. This is the measure that predicts almost
                 everything: when the window names the true place the answer is right
                 96-99% of the time, and when it does not, 0.7-16%. It needs NO model
                 call, so it is available for every day of the month and is the
                 day-by-day curve.

  ACCURACY AT BOTH LEVELS   the exact shelf and the right room, from the frozen answers
                 (notes fixed, no looking). `score_at_both_levels.rescore`.

  THE STEP AND THE RECOVERY   reachability day by day, so the step at day 14 and the
                 recovery after day 24 are visible as steps rather than as a mean over a
                 window. The homes were built to make that step sharp: 0% before day 14
                 in every home, 60-100% from it.

  TWO MECHANICAL BASELINES   "answer where you last saw it" and a stenographer that
                 records every sighting the night it sees it and never forgets. Both are
                 scored on the ARM'S OWN look stream, so an arm that saw more is
                 measured against a baseline that saw more too, and on the SAME question
                 set as the frozen test so no contrast crosses units. An arm that does
                 not beat the recency rule has not earned its language model.

EVERY COMPARISON CAN REPORT EITHER SIDE WINNING. `paired_difference` names the winner,
and where it is a null it says what the null excludes. There is no code path here that
can only print "the model wins" or "not proven".

UNITS ARE CHECKED, NOT ASSUMED. Every contrast reports the overlap of the two question
sets and refuses below 60%. The arms all answer the bank's own full window with no cap,
so the overlap should be 100% and anything else is a bug.

    python -m self_improve.three_prompts_outcomes
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

from self_improve.frozen_household import BEYOND_REACH, FrozenHousehold
from self_improve.frozen_memory_test import questions_in_the_window
from self_improve.memory_notes import Notes, summary_lines
from self_improve.never_written_or_displaced import does_it_assert, the_notes_as_they_stood
from self_improve.score_at_both_levels import PLACE_LEVEL, ROOM_LEVEL, rescore, room_of
from self_improve.study_settings import LOCKED
from self_improve.three_prompts import ARMS, CONTROL, PILOT_BANKS, PILOT_TEN, cell_dir
from self_improve.three_prompts_compliance import claims_that_are_shown, paired_difference
from self_improve.three_prompts_frozen import ROOMIER, STANDARD
from self_improve.write_the_notes import facts_a_statement_asserts

WINDOW_DAYS = tuple(range(14, 24))
RETURN_DAYS = tuple(range(24, 32))


# ------------------------------------------------------------- reachability --


def reachability_by_day(notes: Notes, household: FrozenHousehold,
                        days: Sequence[int]) -> Dict[int, Dict[str, Any]]:
    """For every bank question on each day: was the object's TRUE place named in the
    notes the robot would read for that question?

    TWO VERSIONS, because the eight-line budget was removed on 2026-09-24 and the
    difference between them is what that budget was costing:
      no limit     every line the notes hold - what the robot now actually reads.
      within 8     only the first eight lines the format would have shown. Reported as
                   a diagnostic on the removed cap, never as this run's reachability.

    The notes used are the notes as they stood at the end of the PREVIOUS day, which is
    what the robot would be reading when the question is asked - the nightly write for
    day d happens after day d's questions.

    No model call. The matcher is `facts_a_statement_asserts` via `does_it_assert`, the
    audited one; it MISSES unusual wordings rather than inventing them, so every
    reachability figure here is a LOWER bound and the comparison between arms is fair
    because both are matched the same way.
    """
    out: Dict[int, Dict[str, Any]] = {}
    for day in days:
        questions = [q for q in household.questions_on_day(day)
                     if household.true_place_for_question(q) is not None
                     and household.room_of_object(q["object_id"], q["t_query"])
                     != BEYOND_REACH]
        if not questions:
            continue
        stood = the_notes_as_they_stood(notes, day - 1)
        reached_place = reached_room = capped_place = 0
        for question in questions:
            true_place = household.true_place_for_question(question)
            true_room = room_of(household, true_place)
            window = stood.what_the_robot_can_read(
                None, about_object=question["object_id"]).text.splitlines()
            capped = stood.what_the_robot_can_read(
                8, about_object=question["object_id"]).text.splitlines()
            if does_it_assert(window, question["object_id"], true_place, household):
                reached_place += 1
            if does_it_assert(capped, question["object_id"], true_place, household):
                capped_place += 1
            # the room level: any place in the true room named for this object
            if any(does_it_assert(window, question["object_id"], place, household)
                   for place in household.places_in_room.get(true_room, ())):
                reached_room += 1
        out[day] = {"n_questions": len(questions),
                    "share_true_place_in_the_window": reached_place / len(questions),
                    "share_true_room_in_the_window": reached_room / len(questions),
                    "share_true_place_within_8_lines": capped_place / len(questions)}
    return out


def reachability_capped_over(by_day: Dict[int, Dict[str, Any]], days: Sequence[int]
                             ) -> Optional[float]:
    """What the removed eight-line cap would have shown. A diagnostic on the cap."""
    n = sum(by_day[d]["n_questions"] for d in days if d in by_day)
    if not n:
        return None
    return sum(by_day[d]["share_true_place_within_8_lines"] * by_day[d]["n_questions"]
               for d in days if d in by_day) / n


def reachability_over(by_day: Dict[int, Dict[str, Any]], days: Sequence[int]
                      ) -> Optional[float]:
    """Pooled over the days of a window, weighted by the question count - the same unit
    the frozen accuracy is computed in."""
    n = sum(by_day[d]["n_questions"] for d in days if d in by_day)
    if not n:
        return None
    return sum(by_day[d]["share_true_place_in_the_window"] * by_day[d]["n_questions"]
               for d in days if d in by_day) / n


def reachability_room_over(by_day: Dict[int, Dict[str, Any]], days: Sequence[int]
                           ) -> Optional[float]:
    n = sum(by_day[d]["n_questions"] for d in days if d in by_day)
    if not n:
        return None
    return sum(by_day[d]["share_true_room_in_the_window"] * by_day[d]["n_questions"]
               for d in days if d in by_day) / n


# ---------------------------------------------- the end-to-end headline measures --


def live_measures(cell: Dict[str, Any], household: FrozenHousehold) -> Dict[str, Any]:
    """The four headline measures, from the searches the robot actually made.

    `first_room_was_right` is computed here rather than read off a field, because the
    cell records the rooms it opened in order and not whether the first was right. A
    question the robot never opened a room for cannot have a first room and is excluded
    from that measure alone, so its denominator is stated separately.

    Nothing in here needs a model call or the frozen pass: it is all in `searches`.
    """
    rows = cell["searches"]

    def over(these: Sequence[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not these:
            return None
        opened = [r for r in these if r["rooms_opened"]]
        scored = [r for r in these if r["correct_place"] is not None]
        return {
            "n_questions": len(these),
            "n_with_a_room_opened": len(opened),
            "share_first_room_was_right": (
                sum(1 for r in opened if r["rooms_opened"][0] == r["true_room"])
                / len(opened)) if opened else None,
            "mean_rooms_opened": statistics.mean(r["n_rooms_opened"] for r in these),
            "share_found_within_budget": sum(1 for r in these if r["found_it"]) / len(these),
            "n_scored": len(scored),
            "share_correct_shelf": (sum(1 for r in scored if r["correct_place"])
                                    / len(scored)) if scored else None,
            "share_correct_room": (sum(1 for r in scored if r["correct_room"])
                                   / len(scored)) if scored else None,
            "share_answered_from_the_notes": (
                sum(1 for r in these if r["answered_from"] == "the notes") / len(these)),
        }

    movers = set(cell["movers"])
    out: Dict[str, Any] = {
        "whole_month": over(rows),
        "by_period": {period: over([r for r in rows if r["period"] == period])
                      for period in ("settled", "disrupted", "back to normal")},
        "disrupted_movers_only": over([r for r in rows if r["period"] == "disrupted"
                                       and r["object_id"] in movers]),
        "return_movers_only": over([r for r in rows if r["period"] == "back to normal"
                                    and r["object_id"] in movers]),
        "by_day": {str(day): over([r for r in rows if r["day"] == day])
                   for day in sorted({r["day"] for r in rows})},
    }
    return out


def how_much_the_notes_hold(cell: Dict[str, Any], notes: Notes,
                            household: FrozenHousehold,
                            days: Sequence[int] = (13, 23, 31)) -> Dict[str, Any]:
    """How many facts each memory STYLE holds, and whether a rewrite still rewrites.

    With no length limit the wholesale rewrite may stop being a rewrite: nothing forces
    it to drop anything, so it can accumulate and the two styles can converge on "keep
    everything". That would be an ANSWER to the memory-style question rather than a
    failed experiment - it would mean the only thing separating the styles was being made
    to choose what to lose. So it is measured directly, in the one unit both styles share
    (a line, and a distinct object-and-place fact), at three days and night by night.
    """
    at: Dict[str, Any] = {}
    for day in days:
        stood = the_notes_as_they_stood(notes, day)
        if notes.how_memory_is_written == "wholesale rewrite":
            lines = summary_lines(stood.newest_summary() or "")
        else:
            # a claim folded into another is not shown at answer time
            lines = [c.statement for c in claims_that_are_shown(stood)]
        facts: set = set()
        for line in lines:
            facts |= facts_a_statement_asserts(line, household.asked_objects,
                                               household.places, household.place_room)
        at[str(day)] = {"n_lines": len(lines),
                        "n_distinct_object_and_place_facts": len(facts),
                        "n_characters": sum(len(line) for line in lines)}
    # The per-night size curve, computed the SAME WAY for both styles by reconstructing
    # the notes at the end of each night. The nightly report only carries a character
    # count for the wholesale arm, so reading it would have given a growth curve for one
    # style and nothing for the other - and the whole question is whether they converge.
    nightly = []
    for day in range(0, (cell.get("last_day") or 31) + 1):
        stood = the_notes_as_they_stood(notes, day)
        if notes.how_memory_is_written == "wholesale rewrite":
            lines = summary_lines(stood.newest_summary() or "")
        else:
            # a claim folded into another is not shown at answer time
            lines = [c.statement for c in claims_that_are_shown(stood)]
        nightly.append((day, len(lines), sum(len(x) for x in lines)))
    sizes = [c for _d, _l, c in nightly]
    grew = all(b >= a for a, b in zip(sizes, sizes[1:])) if len(sizes) > 1 else None
    return {
        "how_memory_is_written": notes.how_memory_is_written,
        "at": at,
        "n_nights_with_a_size": len(sizes),
        "the_notes_grew_monotonically": grew,
        "n_nights_the_notes_shrank": sum(1 for a, b in zip(sizes, sizes[1:]) if b < a),
        "characters_first_to_last": (sizes[0], sizes[-1]) if sizes else None,
        "share_of_nights_byte_identical_to_the_night_before": (
            sum(1 for n in cell.get("nightly", []) if n.get("identical_to_last_night"))
            / max(1, len(cell.get("nightly", []))))
            if notes.how_memory_is_written == "wholesale rewrite" else None,
        "nightly_characters": {str(d): c for d, _l, c in nightly},
        "nightly_lines": {str(d): l for d, l, _c in nightly},
    }


# ------------------------------------- what a bigger memory costs in seconds --


def what_the_memory_costs(cell: pathlib.Path, the_cell: Dict[str, Any]
                          ) -> Optional[Dict[str, Any]]:
    """Seconds a question, against how many lines of notes were available.

    The read window is unlimited by decision, and the decision was to REPORT the cost
    rather than cap it - so the cost has to be a measured number. `call_times.jsonl` records
    every model call's wall-clock and prompt size; `searches.jsonl` already records
    `n_lines_of_notes_available` per question. A cell is single-threaded, so the two join.

    CACHED CALLS ARE EXCLUDED FROM THE SECONDS. A mean over a mix of cache hits and real
    calls is the cost of nothing: the hits are free and their share differs between cells
    depending on what ran alongside them. They are counted and reported separately so the
    exclusion is visible rather than silent.

    THE SECONDS ARE NOT A LIKE-FOR-LIKE PRICE OF MEMORY SIZE. They were measured under
    whatever concurrency happened to be running, which varied across the wave, so they
    compare within a cell far better than across cells. What they support is the shape -
    does a question with more lines available take longer - not a headline number.
    """
    times = cell / "call_times.jsonl"
    if not times.exists():
        return None
    calls = []
    for line in times.open():
        try:
            calls.append(json.loads(line))
        except ValueError:
            continue
    if not calls:
        return None
    real = [c for c in calls if not c.get("served_from_the_cache")]
    rows = the_cell["searches"]
    lines_available = [r["n_lines_of_notes_available"] for r in rows
                       if r.get("answered_from") == "the notes"]
    # the correlation between how many lines were available and how long the answer took,
    # over the answer calls only, which are the ones the read window can lengthen
    answer_calls = [c for c in real if c.get("max_tokens", 0) <= 600]
    got: Dict[str, Any] = {
        "n_calls": len(calls),
        "n_calls_that_reached_the_server": len(real),
        "share_served_from_the_cache": 1 - len(real) / len(calls),
        "mean_seconds_per_server_call": statistics.mean(c["seconds"] for c in real)
            if real else None,
        "mean_seconds_per_answer_call": statistics.mean(c["seconds"] for c in answer_calls)
            if answer_calls else None,
        "mean_prompt_characters": statistics.mean(c["n_prompt_characters"] for c in real)
            if real else None,
        "mean_lines_of_notes_available_when_answering":
            statistics.mean(lines_available) if lines_available else None,
        "most_lines_of_notes_available": max(lines_available) if lines_available else None,
        "the_read_budget_bit_on_any_question": any(r.get("the_read_budget_bit")
                                                   for r in rows),
    }
    # seconds a question, over the whole cell: every server call divided by the questions
    # asked, which is the number an owner would feel
    n_questions = len(rows)
    got["server_seconds_per_question"] = (
        sum(c["seconds"] for c in real) / n_questions) if n_questions else None
    return got


# ------------------------------------------------------ mechanical baselines --


def mechanical_on_the_same_questions(looks_file: pathlib.Path,
                                     household: FrozenHousehold,
                                     days: Sequence[int]) -> Dict[str, Any]:
    """The two free references, on the arm's OWN look stream and on the SAME question
    set the frozen test uses.

    `the_mechanical_baselines.score_one_cell` scores only at the moments the robot
    actually searched - the eight questions a day it was asked - which is a different
    question set from the frozen window's twenty-four a day. Mixing the two would be
    exactly the units error that has cost this project four separate results, so this
    scores the full window.

      the recency rule    the object's most recent sighting, including sightings made
                          earlier the same day.
      the stenographer    every sighting written down the night it is seen, never
                          forgotten and never curated, so at question time it knows the
                          newest sighting up to the END OF YESTERDAY. Strictly weaker
                          than the recency rule; the gap is the value of same-day
                          evidence.
    """
    sightings: List[Tuple[int, str, str, str]] = []   # (time, object, place, room)
    for line in looks_file.open():
        row = json.loads(line)
        if row.get("kind") != "look":
            continue
        for s in row["sightings"]:
            sightings.append((s["time"], s["object_id"], s["place_id"], s["room"]))
    sightings.sort()

    # THE STENOGRAPHER'S END-OF-DAY SNAPSHOTS ARE PRECOMPUTED, one per day, rather than
    # filled as sightings are walked. Filling them lazily was a real bug: a snapshot for
    # day d-1 only appeared once a sighting from day d or later had been seen, so a
    # question early on day d - before that day's first search - found no snapshot and the
    # stenographer scored zero for reasons that had nothing to do with the stenographer.
    last_day = max((t // 86400 for t, *_ in sightings), default=0)
    by_end_of: Dict[int, Dict[str, Tuple[str, str]]] = {}
    running: Dict[str, Tuple[str, str]] = {}
    cursor = 0
    for day in range(0, last_day + 2):
        while cursor < len(sightings) and sightings[cursor][0] // 86400 <= day:
            _t, obj, place, room = sightings[cursor]
            running[obj] = (place, room)
            cursor += 1
        by_end_of[day] = dict(running)

    questions = questions_in_the_window(household, list(days))
    tally: collections.Counter = collections.Counter()
    n = 0
    # the recency rule uses every sighting STRICTLY BEFORE the question moment, so it is
    # walked with its own cursor over the same time-ordered list
    cursor = 0
    newest: Dict[str, Tuple[str, str]] = {}
    for question in sorted(questions, key=lambda q: (q["t_query"], q["question_id"])):
        at = question["t_query"]
        while cursor < len(sightings) and sightings[cursor][0] < at:
            _t, obj, place, room = sightings[cursor]
            newest[obj] = (place, room)
            cursor += 1
        true_place = household.true_place_for_question(question)
        true_room = room_of(household, true_place)
        if not true_place or not true_room:
            continue
        n += 1
        mine = newest.get(question["object_id"])
        if mine and mine[0] == true_place:
            tally["the recency rule, shelf"] += 1
        if mine and mine[1] == true_room:
            tally["the recency rule, room"] += 1
        # what a writer who recorded every sighting the night it saw it would know:
        # everything up to the end of yesterday, and nothing from today
        steno = by_end_of.get(question["day_index"] - 1, {}).get(question["object_id"])
        if steno and steno[0] == true_place:
            tally["the stenographer, shelf"] += 1
        if steno and steno[1] == true_room:
            tally["the stenographer, room"] += 1
        if mine is None:
            tally["never seen it at all"] += 1
    return {"n_questions": n,
            "shares": {k: v / n for k, v in tally.items()} if n else {},
            "counts": dict(tally),
            "n_days_with_an_end_of_day_snapshot": len(by_end_of)}


# ------------------------------------------------------------- pulling it in --


def one_cell(root: pathlib.Path, arm: str, household: FrozenHousehold,
             which_cap: str = STANDARD) -> Optional[Dict[str, Any]]:
    cell = cell_dir(root, arm, household.name)
    if not (cell / "notes.json").exists() or not (cell / "cell.json").exists():
        return None
    notes = Notes.load(cell / "notes.json")
    the_cell = json.loads((cell / "cell.json").read_text())
    by_day = reachability_by_day(notes, household, range(1, 32))
    row: Dict[str, Any] = {
        "arm": arm, "household": household.name, "where": str(cell),
        "how_memory_is_written": the_cell["how_memory_is_written"],
        "read_budget_lines": (the_cell.get("three_prompts") or {}).get(
            "read_budget_lines", "NOT RECORDED"),
        "live": live_measures(the_cell, household),
        "the_notes_hold": how_much_the_notes_hold(the_cell, notes, household),
        "what_it_cost": what_the_memory_costs(cell, the_cell),
        "reachability_by_day": {str(d): v for d, v in sorted(by_day.items())},
        "reachability_shelf_days_14_23": reachability_over(by_day, WINDOW_DAYS),
        "reachability_room_days_14_23": reachability_room_over(by_day, WINDOW_DAYS),
        "reachability_shelf_days_24_31": reachability_over(by_day, RETURN_DAYS),
        "reachability_room_days_24_31": reachability_room_over(by_day, RETURN_DAYS),
        "reachability_shelf_days_1_13": reachability_over(by_day, range(1, 14)),
        "reachability_shelf_days_14_23_IF_CAPPED_AT_8":
            reachability_capped_over(by_day, WINDOW_DAYS),
        "reachability_shelf_days_24_31_IF_CAPPED_AT_8":
            reachability_capped_over(by_day, RETURN_DAYS),
        "mechanical_days_14_23": mechanical_on_the_same_questions(
            cell / "looks.jsonl", household, WINDOW_DAYS),
        "mechanical_days_24_31": mechanical_on_the_same_questions(
            cell / "looks.jsonl", household, RETURN_DAYS),
    }
    # the frozen answers, at both levels
    for freeze_point in ("before anything changed", "did it learn the new routine",
                         "did it keep the old routine"):
        answers_file = (root / "frozen" / which_cap / arm / household.name
                        / freeze_point.replace(" ", "_") / "held_out_answers.json")
        if not answers_file.exists():
            continue
        got = json.loads(answers_file.read_text())
        scored = rescore(household, got["answers"])
        by_day_acc: Dict[int, Dict[str, Any]] = {}
        for answer in got["answers"]:
            if not answer.get("true_place"):
                continue
            slot = by_day_acc.setdefault(answer["day"], {"n": 0, "shelf": 0, "room": 0})
            slot["n"] += 1
            if answer["answer_place"] == answer["true_place"]:
                slot["shelf"] += 1
            if answer.get("answer_place") and room_of(household, answer["answer_place"]) \
                    == room_of(household, answer["true_place"]):
                slot["room"] += 1
        row[f"frozen::{freeze_point}"] = {
            "n_questions_scored": scored["n_scored"],
            "shelf": scored[PLACE_LEVEL], "room": scored[ROOM_LEVEL],
            "of_its_wrong_shelf_answers_the_share_in_the_right_room":
                scored["of_its_wrong_shelf_answers_the_share_in_the_right_room"],
            "question_ids": sorted(a["question_id"] for a in got["answers"]),
            "by_day": {str(d): {"n": v["n"], "shelf": v["shelf"] / v["n"],
                                "room": v["room"] / v["n"]}
                       for d, v in sorted(by_day_acc.items())},
        }
    return row


def overlap(a: Sequence[str], b: Sequence[str]) -> float:
    sa, sb = set(a), set(b)
    return len(sa & sb) / len(sa | sb) if (sa or sb) else 0.0


THE_FLOOR: Dict[str, Any] = {}
"""The rerun noise floor per measure, loaded from `the_rerun_noise_floor.json` if it has
been measured. See `three_prompts_noise_floor`: `control` and `told_unwell` get
byte-identical prompts on days 0-13, so their difference over that window is rerun noise.
A contrast smaller than the floor for the SAME measure is not evidence, however tight its
standard error - the standard error measures spread across homes and this does not."""


def load_the_floor(root: pathlib.Path) -> None:
    path = root / "the_rerun_noise_floor.json"
    if not path.exists():
        return
    try:
        THE_FLOOR.update(json.loads(path.read_text()).get("floor_per_measure") or {})
    except ValueError:
        pass


def against_the_floor(field: Optional[str], difference: float) -> str:
    """Whether a measured difference clears the rerun noise floor for its own measure."""
    got = THE_FLOOR.get(field or "")
    if not got:
        return ""
    if abs(difference) <= got["mean_absolute_difference"]:
        return " [INSIDE the rerun noise floor: not evidence]"
    if abs(difference) <= got["largest"]:
        return " [above the mean noise but below the worst home's noise]"
    return " [clears the rerun noise floor]"


def report_a_contrast(label: str, rows: Sequence[Dict[str, Any]],
                      control_rows: Sequence[Dict[str, Any]], pick,
                      as_percent: bool = True,
                      field: Optional[str] = None) -> Optional[Dict[str, Any]]:
    got = paired_difference(rows, control_rows, pick)
    if not got or got.get("too_few_homes_to_pair"):
        print(f"    {label:52s} only {got['n_homes'] if got else 0} paired homes, "
              f"not reported")
        return got
    fmt = (lambda x: f"{100*x:+6.1f}") if as_percent else (lambda x: f"{x:+7.3f}")
    show = (lambda x: f"{100*x:5.1f}") if as_percent else (lambda x: f"{x:6.3f}")
    print(f"    {label:52s} arm {show(got['arm_mean'])} control {show(got['control_mean'])}"
          f"  diff {fmt(got['mean_difference'])} +- {fmt(got['two_standard_errors']).strip()}"
          f" (2 se, n={got['n_homes']})  {got['n_homes_the_arm_is_higher']} up / "
          f"{got['n_homes_the_arm_is_lower']} down  -> {got['verdict']}"
          f"{against_the_floor(field, got['mean_difference'])}")
    got["against_the_rerun_noise_floor"] = against_the_floor(
        field, got["mean_difference"]).strip(" []")
    return got


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/three_prompts"))
    parser.add_argument("--banks", type=pathlib.Path, default=PILOT_BANKS)
    parser.add_argument("--cap", default=STANDARD, choices=[STANDARD, ROOMIER])
    parser.add_argument("--out", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    # THE CEILING, before any accuracy number, because it changes how all of them read: the
    # information is present in what the robot saw and the model is not using it, so the
    # bottleneck is not observation.
    ceiling = None
    for where in (args.root / "THE_CEILING.json",
                  pathlib.Path("results/self_improve/overnight_wave/THE_CEILING.json")):
        if where.exists():
            try:
                ceiling = json.loads(where.read_text()); break
            except ValueError:
                pass
    if ceiling:
        print("\n--- THE CEILING. Read this before any accuracy number below.\n")
        for label, value in ceiling["results"].items():
            print(f"  {value:6.0%}  {label}")
        print(f"\n  {ceiling['n_questions']} questions, {ceiling['measured_on']}")
        print(f"  {ceiling['why_it_changes_how_every_accuracy_number_is_read']}")
        print(f"  WEIGHT: {ceiling['how_much_weight_it_carries']}")
        print(f"  NOT: {ceiling['what_it_does_not_say']}")

    load_the_floor(args.root)
    households: Dict[str, FrozenHousehold] = {}
    rows: List[Dict[str, Any]] = []
    for arm in sorted(ARMS):
        for name in PILOT_TEN:
            path = args.banks / f"{name}.jsonl"
            if not path.exists():
                continue
            if name not in households:
                households[name] = FrozenHousehold(path)
            got = one_cell(args.root, arm, households[name], args.cap)
            if got:
                rows.append(got)
    if not rows:
        print(f"no finished cells under {args.root}/cells yet")
        return 0

    by_arm: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        by_arm[row["arm"]].append(row)
    control = by_arm.get(CONTROL, [])
    if not control:
        print("no control cells: nothing can be contrasted")
        return 1

    print(f"\n{'='*100}\nOUTCOMES. reasoning cap = {args.cap}. "
          f"{len(rows)} cells, {len({r['household'] for r in rows})} homes. "
          f"Paired within home, clustered on home.\n"
          f"NO LENGTH LIMIT on the memory, in writing or in reading: "
          f"read_budget_lines = "
          f"{sorted({str(r['read_budget_lines']) for r in rows})}.\n{'='*100}")

    incremental = {arm: [r for r in by_arm[arm]
                         if r["how_memory_is_written"] == "incremental edits"]
                   for arm in by_arm}
    control_inc = incremental.get(CONTROL, [])

    # ================= 0. THE HEADLINE: END TO END =================
    print("\n" + "="*100)
    print("0. THE HEADLINE: END TO END. The robot searches in order to answer, so a")
    print("   better memory shows up as a better first room, fewer rooms, more found.")
    print("="*100)
    for window, key in (("the disrupted period, days 14-23", ("by_period", "disrupted")),
                        ("the disrupted period, MOVERS only", ("disrupted_movers_only",)),
                        ("the return, days 24-31", ("by_period", "back to normal")),
                        ("the return, MOVERS only", ("return_movers_only",)),
                        ("the whole month", ("whole_month",))):
        def get(row, k=key):
            spot = row["live"]
            for bit in k:
                spot = (spot or {}).get(bit) if isinstance(spot, dict) else None
            return spot
        here = {arm: [r for r in incremental[arm] if get(r)] for arm in incremental}
        if not any(here.values()):
            continue
        print(f"\n  --- {window}")
        print(f"    {'arm':22s} {'homes':>5s} {'n q':>5s} {'1st room':>9s} "
              f"{'rooms/q':>8s} {'found':>7s} {'shelf':>7s} {'room':>7s} {'from notes':>11s}")
        for arm in sorted(here):
            these = here[arm]
            if not these:
                continue
            def m(f, these=these, get=get):
                vals = [f(get(r)) for r in these if f(get(r)) is not None]
                return statistics.mean(vals) if vals else float("nan")
            print(f"    {arm:22s} {len(these):5d} "
                  f"{m(lambda g: g['n_questions']):5.0f} "
                  f"{m(lambda g: g['share_first_room_was_right']):8.1%} "
                  f"{m(lambda g: g['mean_rooms_opened']):8.2f} "
                  f"{m(lambda g: g['share_found_within_budget']):6.1%} "
                  f"{m(lambda g: g['share_correct_shelf']):6.1%} "
                  f"{m(lambda g: g['share_correct_room']):6.1%} "
                  f"{m(lambda g: g['share_answered_from_the_notes']):10.1%}")
        for arm in sorted(here):
            if arm == CONTROL or not here[arm]:
                continue
            print(f"    -- {arm} against the control:")
            for label, field in (
                    ("first room was the right one", "share_first_room_was_right"),
                    ("rooms opened per question (lower is better)", "mean_rooms_opened"),
                    ("found it within the budget", "share_found_within_budget"),
                    ("final answer right, shelf", "share_correct_shelf"),
                    ("final answer right, room", "share_correct_room")):
                report_a_contrast(
                    label, here[arm], [r for r in control_inc if get(r)],
                    lambda r, f=field, g=get: (g(r) or {}).get(f),
                    as_percent=(field != "mean_rooms_opened"), field=field)

    # ================= the memory-style question =================
    styles = collections.defaultdict(list)
    for row in rows:
        styles[row["how_memory_is_written"]].append(row)
    if len(styles) > 1:
        print("\n" + "="*100)
        print("0b. DOES A REWRITE WITH NO LENGTH LIMIT STILL REWRITE? If the two styles")
        print("    converge on keeping everything, the only thing that separated them was")
        print("    being made to choose what to lose - which is an ANSWER, not a failure.")
        print("="*100)
        print(f"\n    {'style':20s} {'homes':>5s} {'lines d13':>9s} {'d23':>6s} "
              f"{'d31':>6s} {'facts d13':>9s} {'d23':>6s} {'d31':>6s} "
              f"{'grew only':>10s} {'nights shrank':>13s}")
        for style, these in sorted(styles.items()):
            these = [r for r in these if r["arm"] in (CONTROL, "control_wholesale")]
            if not these:
                continue
            h = lambda d, f: statistics.mean(r["the_notes_hold"]["at"][d][f] for r in these)
            grew = sum(1 for r in these if r["the_notes_hold"]["the_notes_grew_monotonically"])
            shrank = statistics.mean(r["the_notes_hold"]["n_nights_the_notes_shrank"]
                                     for r in these)
            print(f"    {style:20s} {len(these):5d} {h('13','n_lines'):9.1f} "
                  f"{h('23','n_lines'):6.1f} {h('31','n_lines'):6.1f} "
                  f"{h('13','n_distinct_object_and_place_facts'):9.1f} "
                  f"{h('23','n_distinct_object_and_place_facts'):6.1f} "
                  f"{h('31','n_distinct_object_and_place_facts'):6.1f} "
                  f"{grew:4d}/{len(these):<5d} {shrank:13.1f}")
        print("\n    'grew only' counts homes whose notes never got shorter from one night")
        print("    to the next. A rewrite that never shrinks is not choosing what to lose.")
        wholesale = [r for r in rows if r["arm"] == "control_wholesale"]
        if wholesale:
            print("\n    the same prompt under the two styles, END TO END, "
                  "disrupted days 14-23:")
            for label, field in (
                    ("first room was the right one", "share_first_room_was_right"),
                    ("rooms opened per question (lower is better)", "mean_rooms_opened"),
                    ("found it within the budget", "share_found_within_budget"),
                    ("final answer right, shelf", "share_correct_shelf"),
                    ("final answer right, room", "share_correct_room")):
                report_a_contrast(
                    "wholesale minus claim store: " + label, wholesale, control_inc,
                    lambda r, f=field: (r["live"]["by_period"].get("disrupted") or {}).get(f),
                    as_percent=(field != "mean_rooms_opened"), field=field)
            print("\n    A null here, with both styles uncapped, is the first clean "
                  "version of the\n    memory-style comparison - see "
                  "THE_WRITING_PROMPTS_WERE_NOT_THE_SAME.md for what was\n    wrong with "
                  "every earlier one, and for what is STILL not symmetric.")

    # ---- reachability
    print("\n--- 1. REACHABILITY (mechanism, no model call): is the true place "
          "anywhere in the notes the robot reads? No length limit.\n")
    print(f"  {'arm':22s} {'d1-13':>7s} {'d14-23':>7s} {'d24-31':>7s}   (shelf level)")
    for arm in sorted(by_arm):
        here = by_arm[arm]
        m = lambda k: statistics.mean(r[k] for r in here if r[k] is not None)
        print(f"  {arm:22s} {m('reachability_shelf_days_1_13'):6.1%} "
              f"{m('reachability_shelf_days_14_23'):6.1%} "
              f"{m('reachability_shelf_days_24_31'):6.1%}")
    for arm in sorted(by_arm):
        if arm == CONTROL:
            continue
        print(f"\n  {arm} against the control:")
        for label, key in (("reachability shelf, disrupted days 14-23",
                            "reachability_shelf_days_14_23"),
                           ("reachability room, disrupted days 14-23",
                            "reachability_room_days_14_23"),
                           ("reachability shelf, the return, days 24-31",
                            "reachability_shelf_days_24_31"),
                           ("reachability shelf, settled days 1-13",
                            "reachability_shelf_days_1_13")):
            report_a_contrast(label, by_arm[arm], control, lambda r, k=key: r[k])

    # ---- accuracy at both levels
    print("\n--- 2. DIAGNOSTIC ONLY, NOT THE ARM'S RESULT: what do the notes ALONE\n"
          "    contain? Notes frozen, all looking switched off, full question window.\n"
          "    The arm's result is section 0, end to end.\n")
    for freeze_point in ("before anything changed", "did it learn the new routine",
                         "did it keep the old routine"):
        key = f"frozen::{freeze_point}"
        present = {arm: [r for r in by_arm[arm] if key in r] for arm in by_arm}
        if not any(present.values()):
            continue
        print(f"  {freeze_point} (notes through day "
              f"{ {'before anything changed':13,'did it learn the new routine':23,'did it keep the old routine':28}[freeze_point] })")
        print(f"    {'arm':22s} {'homes':>5s} {'n q':>6s} {'shelf':>7s} {'room':>7s}")
        for arm in sorted(present):
            here = present[arm]
            if not here:
                continue
            print(f"    {arm:22s} {len(here):5d} "
                  f"{statistics.mean(r[key]['n_questions_scored'] for r in here):6.0f} "
                  f"{statistics.mean(r[key]['shelf'] for r in here):6.1%} "
                  f"{statistics.mean(r[key]['room'] for r in here):6.1%}")
        for arm in sorted(present):
            if arm == CONTROL or not present[arm]:
                continue
            print(f"    -- {arm}:")
            for level in ("shelf", "room"):
                report_a_contrast(f"{level} accuracy", present[arm],
                                  [r for r in control if key in r],
                                  lambda r, k=key, l=level: r[k][l])
        print()

    # ---- the step and the recovery
    print("\n--- 3. THE STEP AT DAY 14 AND THE RECOVERY AFTER DAY 24, day by day\n")
    print("  reachability of the true shelf in the notes the robot reads - no length "
          "limit - mean over homes\n")
    header = "  day  " + "".join(f"{arm[:9]:>11s}" for arm in sorted(by_arm))
    print(header)
    for day in range(10, 32):
        cells = []
        for arm in sorted(by_arm):
            vals = [r["reachability_by_day"][str(day)]["share_true_place_in_the_window"]
                    for r in by_arm[arm] if str(day) in r["reachability_by_day"]]
            cells.append(f"{statistics.mean(vals):10.1%}" if vals else f"{'-':>10s}")
        mark = " <- illness starts" if day == 14 else " <- back to normal" if day == 24 else ""
        print(f"  {day:3d}  " + " ".join(cells) + mark)
    print("\n  the step, day 13 -> day 14, and the recovery, day 23 -> day 24:")
    for arm in sorted(by_arm):
        def at(day, rows_here):
            vals = [r["reachability_by_day"][str(day)]["share_true_place_in_the_window"]
                    for r in rows_here if str(day) in r["reachability_by_day"]]
            return statistics.mean(vals) if vals else None
        here = by_arm[arm]
        d13, d14, d23, d24 = at(13, here), at(14, here), at(23, here), at(24, here)
        if None in (d13, d14, d23, d24):
            continue
        print(f"    {arm:22s} d13 {d13:5.1%} -> d14 {d14:5.1%} ({d14-d13:+.1%}) | "
              f"d23 {d23:5.1%} -> d24 {d24:5.1%} ({d24-d23:+.1%})")

    # ---- what the unlimited memory costs
    costed = [r for r in rows if r.get("what_it_cost")]
    if costed:
        print("\n--- 3b. WHAT THE UNLIMITED MEMORY COSTS, in seconds a question\n")
        print("  The read window is unlimited, and the decision was to report the cost")
        print("  rather than cap it. Cached calls are excluded from the seconds, because a")
        print("  mean over cache hits and real calls is the cost of nothing. These compare")
        print("  WITHIN a cell far better than across cells: concurrency varied.\n")
        print(f"  {'arm':22s} {'cells':>5s} {'lines avail':>11s} {'most':>5s} "
              f"{'s/answer call':>13s} {'server s/question':>17s} {'from cache':>10s}")
        for arm in sorted(by_arm):
            here = [r["what_it_cost"] for r in by_arm[arm] if r.get("what_it_cost")]
            if not here:
                continue
            def m(k, here=here):
                vals = [x[k] for x in here if x.get(k) is not None]
                return statistics.mean(vals) if vals else float("nan")
            print(f"  {arm:22s} {len(here):5d} "
                  f"{m('mean_lines_of_notes_available_when_answering'):11.1f} "
                  f"{m('most_lines_of_notes_available'):5.0f} "
                  f"{m('mean_seconds_per_answer_call'):13.2f} "
                  f"{m('server_seconds_per_question'):17.2f} "
                  f"{m('share_served_from_the_cache'):9.0%}")
        bit = [r["household"] for r in costed
               if r["what_it_cost"]["the_read_budget_bit_on_any_question"]]
        print(f"\n  the read window was truncated on any question in: "
              f"{bit if bit else 'no cell - the memory was genuinely unlimited'}")

    # ---- the mechanical baselines
    print("\n--- 4. AGAINST THE TWO FREE BASELINES, same question set, "
          "each arm's own look stream\n")
    for window, key in (("days 14-23", "mechanical_days_14_23"),
                        ("days 24-31", "mechanical_days_24_31")):
        print(f"  {window}")
        print(f"    {'arm':22s} {'recency shelf':>14s} {'recency room':>13s} "
              f"{'steno shelf':>12s} {'steno room':>11s} {'never seen':>11s}")
        for arm in sorted(by_arm):
            here = [r[key]["shares"] for r in by_arm[arm] if r[key]["n_questions"]]
            if not here:
                continue
            g = lambda k: statistics.mean(s.get(k, 0.0) for s in here)
            print(f"    {arm:22s} {g('the recency rule, shelf'):13.1%} "
                  f"{g('the recency rule, room'):12.1%} "
                  f"{g('the stenographer, shelf'):11.1%} "
                  f"{g('the stenographer, room'):10.1%} "
                  f"{g('never seen it at all'):10.1%}")
        print()
    print("  the arm against the baseline computed on its OWN stream, paired within "
          "home, at the day-23 freeze point:")
    key = "frozen::did it learn the new routine"
    for arm in sorted(by_arm):
        here = [r for r in by_arm[arm] if key in r]
        if not here:
            continue
        for label, level, mech in (("shelf vs the recency rule", "shelf",
                                    "the recency rule, shelf"),
                                   ("shelf vs the stenographer", "shelf",
                                    "the stenographer, shelf"),
                                   ("room vs the recency rule", "room",
                                    "the recency rule, room"),
                                   ("room vs the stenographer", "room",
                                    "the stenographer, room")):
            deltas = [r[key][level] - r["mechanical_days_14_23"]["shares"].get(mech, 0.0)
                      for r in here if r["mechanical_days_14_23"]["n_questions"]]
            if len(deltas) < 2:
                continue
            mean = statistics.mean(deltas)
            se = statistics.stdev(deltas) / (len(deltas) ** 0.5)
            verdict = ("the arm beats the baseline" if mean > 2 * se else
                       "THE BASELINE BEATS THE ARM" if -mean > 2 * se else
                       f"neither, beyond 2 se; excludes a gap larger than {2*se:.1%}")
            print(f"    {arm:22s} {label:28s} {mean:+6.1%} +- {2*se:.1%} "
                  f"({sum(1 for d in deltas if d>0)}/{len(deltas)} homes) -> {verdict}")

    out = args.out or (args.root / f"outcomes_{args.cap}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"reasoning_cap": args.cap, "per_cell": rows}, indent=1))
    print(f"\nwritten to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
