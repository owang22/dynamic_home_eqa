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
from self_improve.what_is_in_this_file import print_what_is_in_this_file
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
            # THE SAME MEASURE OVER THE OTHER DENOMINATOR, because the two disagree on the
            # verdict and one of them had to be named rather than chosen silently. Over SCORED
            # questions, ours beats the last-seen rule on exact place by +1.0 (2 SE 1.9, does
            # not clear); counting a question nobody could score as not-right, +2.1 (2 SE 2.0,
            # clears by a hair). The gap is 26 unscorable questions that fall almost entirely
            # in the last-seen cells, so dropping them raises THAT arm's share. Both are
            # defensible - an owner gets nothing useful from an unanswerable question, and
            # penalising an arm for a question nobody can score is also wrong - so both are
            # printed with their denominators, and neither is the report's silent default.
            "share_correct_shelf_counting_unscorable_as_wrong": (
                sum(1 for r in these if r["correct_place"]) / len(these)),
            "n_unscorable": len(these) - len(scored),
            "share_correct_room": (sum(1 for r in scored if r["correct_room"])
                                   / len(scored)) if scored else None,
            "share_answered_from_the_notes": (
                sum(1 for r in these if r["answered_from"] == "the notes") / len(these)),
        }

    movers = set(cell["movers"])

    def where_it_arrived(these):
        """WHICH STEP reached the right room, on the moved objects.

        First-room-right and never-got-there are different failures and the difference bears on
        the rooms-opened measure rather than the first-room one: an arm that reaches the right
        room on step two or three by elimination is reasoning, and one that never arrives is
        not. Measured on hh_s48_t03 days 14+: right first on 10 of 17, on step 2 once, on step 3
        twice, never on 4 - so 13 of 17 arrived, which reads very differently from 10 of 17.
        """
        opened = [r for r in these if r["rooms_opened"] and r["true_room"]]
        if not opened:
            return None
        at = {1: 0, 2: 0, 3: 0, "never": 0}
        for r in opened:
            if r["true_room"] in r["rooms_opened"]:
                at[r["rooms_opened"].index(r["true_room"]) + 1] = \
                    at.get(r["rooms_opened"].index(r["true_room"]) + 1, 0) + 1
            else:
                at["never"] += 1
        reached = sum(v for k, v in at.items() if k != "never")
        return {"n": len(opened), "at_step": {str(k): v for k, v in at.items()},
                "share_reached_at_all": reached / len(opened),
                "share_first_room": at.get(1, 0) / len(opened)}
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
        # where in the search it arrived, on the MOVED objects, per window
        "where_it_arrived_on_movers": {
            period: where_it_arrived([r for r in rows if r["period"] == period
                                      and r["object_id"] in movers])
            for period in ("settled", "disrupted", "back to normal")},
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


def the_movers_curve_for_one_cell(cell: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Per day, on the objects the illness moves: was the first room opened the right one,
    and HOW MANY QUESTIONS that rests on.

    WHY THE COUNT IS PART OF THE MEASURE. At 8 questions a day a point on this line rested on
    3.7 mover questions and 79 of 310 home-days had one or two, so a 0% or 100% day was
    arithmetic rather than signal - which is what Oliver noticed on the artifact. The count is
    printed beside every point and any day under `THIN_DAY` is marked, so a thin point cannot
    be read as a measurement. At 24 questions a day the same homes give 4.7 to 17.9 mover
    questions a day, and days under five fall from 25% to 8%.
    """
    movers = set(cell.get("movers") or ())
    out: Dict[str, Dict[str, Any]] = {}
    by_day: Dict[int, List[Dict[str, Any]]] = collections.defaultdict(list)
    for row in cell["searches"]:
        if row["object_id"] in movers:
            by_day[row["day"]].append(row)
    for day, rows in sorted(by_day.items()):
        opened = [r for r in rows if r["rooms_opened"]]
        out[str(day)] = {
            "n_mover_questions": len(rows),
            "n_with_a_room_opened": len(opened),
            "share_first_room_was_right": (
                sum(1 for r in opened if r["rooms_opened"][0] == r["true_room"])
                / len(opened)) if opened else None,
            "period": rows[0].get("period"),
        }
    return out


# A day this thin is arithmetic, not a measurement, and is marked rather than plotted.
THIN_DAY = 5


def one_cell(root: pathlib.Path, arm: str, household: FrozenHousehold,
             which_cap: str = STANDARD) -> Optional[Dict[str, Any]]:
    cell = cell_dir(root, arm, household.name)
    if not (cell / "cell.json").exists():
        return None
    the_cell = json.loads((cell / "cell.json").read_text())
    if (cell / "notes.json").exists():
        notes = Notes.load(cell / "notes.json")
    elif the_cell.get("sensing_arm") in ("last seen, no model",
                                        "newest sighting, no model"):
        # AN ARM THAT WRITES NO NOTES HAS NO NOTES FILE, and requiring one made this arm
        # invisible: `one_cell` returned None for all ten of its cells, so the no-model rule
        # was silently absent from every table - including the headline row, which is
        # specified as arm 1 against THIS baseline on the same questions and the same look
        # stream. An empty memory is the correct reading of its notes, not missing data.
        notes = Notes(cell / "notes.json", household.name, the_cell["arm"],
                      the_cell["how_memory_is_written"])
    else:
        return None
    by_day = reachability_by_day(notes, household, range(1, 32))
    row: Dict[str, Any] = {
        "arm": arm, "household": household.name, "where": str(cell),
        "how_memory_is_written": the_cell["how_memory_is_written"],
        "read_budget_lines": (the_cell.get("three_prompts") or {}).get(
            "read_budget_lines", "NOT RECORDED"),
        "live": live_measures(the_cell, household),
        "the_movers_curve": the_movers_curve_for_one_cell(the_cell),
        "the_forced_identity": found_and_place_on_the_same_questions(the_cell),
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


THE_FLOOR_SOURCE = [""]
# Measured elsewhere, so it is BORROWED and says so. A noise floor is per arm and per window,
# never a project constant - but a wave with no floor of its own was printing no floor line at
# all, which reads as "this difference is clean" when nothing was checked. Borrowed and
# labelled beats absent.
BORROWED_FLOOR = pathlib.Path("results/self_improve/three_prompts/the_rerun_noise_floor.json")


def load_the_floor(root: pathlib.Path) -> None:
    for path, where in ((root / "the_rerun_noise_floor.json", "this wave"),
                        (BORROWED_FLOOR, "three_prompts d0-13, 7 homes, BORROWED")):
        if not path.exists():
            continue
        try:
            got = json.loads(path.read_text())
        except ValueError:
            continue
        THE_FLOOR.update(got.get("floor_per_measure") or {})
        THE_FLOOR_SOURCE[0] = where
        return


def against_the_floor(field: Optional[str], difference: float) -> str:
    """Whether a measured difference clears the rerun noise floor FOR ITS OWN MEASURE, with the
    floor's own value and where it was measured, in the same string.

    The value is in the line because a bracket saying "inside the floor" invites the reader to
    assume some small floor; our arm's 1.5-point lead on found-within-budget sits under a
    1.9-point floor, and those two numbers have to be readable together or the lead gets quoted
    on its own."""
    got = THE_FLOOR.get(field or "")
    if not got:
        return " [no rerun floor for this measure: unchecked]"
    mean = 100 * got["mean_absolute_difference"]
    worst = 100 * got["largest"]
    where = THE_FLOOR_SOURCE[0]
    if abs(difference) <= got["mean_absolute_difference"]:
        return (f" [INSIDE the {mean:.1f}-pt rerun floor ({where}): not evidence]")
    if abs(difference) <= got["largest"]:
        return (f" [over the {mean:.1f}-pt floor, under the worst home's {worst:.1f} ({where})]")
    return f" [clears the {mean:.1f}-pt rerun floor, worst home {worst:.1f} ({where})]"


def found_and_place_on_the_same_questions(cell: Dict[str, Any]) -> Dict[str, int]:
    """Does `found it within the budget` pick out exactly the same questions as `exact place
    right`? Counted per question, which is where the identity lives.

    Measured on the shares it looked FALSE - 94.4% found against 95.5% exact place for the
    last-seen rule - and that difference is only the 26 unscorable questions, which are in the
    first denominator and not the second. Per question the two agree on all 2,454 scorable ones
    and disagree on none, while the plain claim store disagrees on 66 and ours on 13. So the
    claim to protect is "the same QUESTIONS", not "the same number", and stating it the second
    way invites a reader to check the shares and conclude it is not true.
    """
    agree = disagree = unscorable = 0
    for row in cell.get("searches") or ():
        if row.get("correct_place") is None:
            unscorable += 1
            continue
        if bool(row.get("found_it")) == bool(row.get("correct_place")):
            agree += 1
        else:
            disagree += 1
    return {"agree_on": agree, "disagree_on": disagree, "unscorable": unscorable}


def arms_where_found_and_place_are_one_number(by_arm) -> Dict[str, int]:
    """Arms where `found within the budget` and `exact place right` are the SAME number in
    every home and every window - which for a last-seen rule is FORCED, not observed.

    Its first guess is the room the object was last seen in, so when the search fails, the
    last-seen shelf is always inside a room it has already opened: the two measures cannot come
    apart. Reported as one column with that sentence, never as two findings, because quoting
    them separately claims two agreements where the arm's construction allows only one.

    Detected from the data rather than from the arm's name, and the detection has power: on the
    ten-home wave it holds in 40 of 40 home-windows for `last seen, no model` and in 14 of 40
    and 23 of 40 for the two claim-store arms, which are therefore NOT collapsed.
    """
    out: Dict[str, int] = {}
    for arm, these in by_arm.items():
        agree = sum((r.get("the_forced_identity") or {}).get("agree_on", 0) for r in these)
        differ = sum((r.get("the_forced_identity") or {}).get("disagree_on", 0) for r in these)
        if agree and not differ:
            out[arm] = agree
    return out


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
    # WHICH ARM IS THE CONTROL IS NOW AN ARGUMENT. This module was written for the
    # three_prompts variants, where the control was called "control". In the overnight wave
    # the one-variable partner for "the log and notes about the routine" is
    # "incremental_edits" - the plain claim store it is a fork of - and a hardcoded name made
    # the report exit with "no control cells" on a wave with 54 finished ones.
    parser.add_argument("--only-this-memory-format", default=None,
                        help="restrict the headline to cells written this way "
                             "(the three_prompts waves used 'incremental edits'); "
                             "by default every arm is in it")
    parser.add_argument("--wholesale-arm", default="control_wholesale",
                        help="the arm whose memory style is the wholesale rewrite")
    parser.add_argument("--control", default=CONTROL,
                        help="the arm every contrast is against "
                             "(directory name under cells/)")
    args = parser.parse_args(argv)

    print_what_is_in_this_file(args.root, f"OUTCOMES at reasoning cap {args.cap}")

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

    # NO FAILED-NIGHT EXCLUSION RULE ANY MORE, and nothing about it in the accuracy
    # section. Every lost call in this wave was one bug - a socket built with
    # `timeout=min(600.0, DEADLINE_S)` against a 900-second watchdog, so the socket gave up
    # while the server was still generating - and the affected cells were rerun rather than
    # annotated. THE_FAILED_NIGHTS_were_one_bug.md records the fault, not a caveat on
    # these numbers; a rerun still in flight shows in the header at the top of this file.

    # EVERY NIGHT WHOSE CALL FAILED, PER CELL, AS A LIST. A count cannot be acted on: the
    # response cache makes a rerun resume from the first lost night, so which nights were lost
    # decides what a rerun costs, and a cell that lost night 8 is most of a cell while one that
    # lost night 29 is nearly free. Printed before any accuracy number, from each cell's own
    # arm.json, so a wave where the watchdog started biting says so at the top.
    lost = []
    for a in sorted((args.root / "cells").glob("*/*/arm.json")):
        try:
            got = json.loads(a.read_text())
        except ValueError:
            continue
        nights = got.get("nights_whose_call_failed") or []
        if nights:
            lost.append((a.parent.parent.name, a.parent.name, sorted(nights),
                         got.get("questions_per_day")))
    print("\n--- NIGHTS WHOSE MODEL CALL FAILED, per cell, as a list\n")
    if not lost:
        print("  none, in any finished cell under this root")
    else:
        for arm, home, nights, qpd in lost:
            print(f"  {arm:40s} {home:14s} at {qpd} q/day: nights {nights}")
        print(f"\n  {len(lost)} cell(s). The cheapest repair is to rerun these cells with a")
        print("  raised deadline once the wave has landed: the response cache makes a rerun")
        print("  resume from the first lost night rather than restart. A cell that lost an")
        print("  EARLY night is most of a cell; one that lost a late night is nearly free.")

    load_the_floor(args.root)
    households: Dict[str, FrozenHousehold] = {}
    rows: List[Dict[str, Any]] = []
    # discovered from the directories, for the reason in three_prompts_compliance
    arms = sorted(d.name for d in (args.root / "cells").glob("*") if d.is_dir())
    for arm in arms:
        for name in sorted(d.name for d in (args.root / "cells" / arm).glob("*")
                           if d.is_dir()):
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
    # ===== 0c. the per-home, per-day curve on the moved objects, with its n =====
    print("\n" + "="*100)
    print("0c. ONE HOME AT A TIME, DAY BY DAY, ON THE OBJECTS THE ILLNESS MOVES:")
    print("    was the first room opened the right one. The count each point rests on is")
    print(f"    printed beside it, and a day of fewer than {THIN_DAY} mover questions is")
    print("    marked * - at that width a 0% or a 100% day is arithmetic, not signal.")
    print("="*100)
    homes = sorted({r["household"] for r in rows})
    arms_here = sorted(by_arm)
    for home in homes:
        print(f"\n  --- {home}")
        print("    day  " + "".join(f"{a[:13]:>16s}" for a in arms_here))
        thin_here = 0
        for day in range(1, 32):
            cells_row = []
            for arm in arms_here:
                got = [r["the_movers_curve"].get(str(day)) for r in by_arm[arm]
                       if r["household"] == home]
                got = [g for g in got if g]
                if not got:
                    cells_row.append(f"{'-':>16s}")
                    continue
                g = got[0]
                n = g["n_mover_questions"]
                thin = "*" if n < THIN_DAY else " "
                if g["share_first_room_was_right"] is None:
                    cells_row.append(f"{'no room':>14s}{thin} ")
                else:
                    cells_row.append(f"{g['share_first_room_was_right']:11.0%} n={n:<2d}{thin}")
                if n < THIN_DAY:
                    thin_here += 1
            mark = ("  <- illness starts" if day == 14 else
                    "  <- back to normal" if day == 24 else "")
            print(f"    {day:3d}  " + "".join(cells_row) + mark)
        print(f"    thin points (n < {THIN_DAY}) in this home: {thin_here}")
    print("\n  This is the measure the 24-questions wave exists for. Pooled over ten homes a")
    print("  day's point rests on ~37 mover questions and is fine; one home's line at 8")
    print("  questions a day rests on ~3.7 and is not. Both waves stand, in separate")
    print("  directories, and the first line of this file says which one this is.")

    control = by_arm.get(args.control, [])
    if not control:
        print("no control cells: nothing can be contrasted")
        return 1

    print(f"\n{'='*100}\nOUTCOMES. reasoning cap = {args.cap}. "
          f"{len(rows)} cells, {len({r['household'] for r in rows})} homes. "
          f"Paired within home, clustered on home.\n"
          f"NO LENGTH LIMIT on the memory, in writing or in reading: "
          f"read_budget_lines = "
          f"{sorted({str(r['read_budget_lines']) for r in rows})}.\n{'='*100}")

    # THE HEADLINE USED TO DROP EVERY ARM WHOSE MEMORY FORMAT WAS NOT "incremental edits".
    # That was right for the three_prompts wave, where every arm shared one format and only
    # the writing PROMPT differed, so the restriction kept the compared things alike. In the
    # overnight wave the arms ARE formats, so the same line silently dropped four of the six
    # finished arms - including `the log and notes about the routine`, the arm the wave
    # exists to measure - and printed a headline table of two arms without saying anything
    # was missing. What keeps units comparable here is the question set, which
    # `report_a_contrast` pairs within home; the format is printed in the table instead.
    #
    # `--only-this-memory-format` restores the old behaviour for the older wave.
    def for_the_headline(rows_of_an_arm):
        if not args.only_this_memory_format:
            return list(rows_of_an_arm)
        return [r for r in rows_of_an_arm
                if r["how_memory_is_written"] == args.only_this_memory_format]

    incremental = {arm: for_the_headline(by_arm[arm]) for arm in by_arm}
    control_inc = incremental.get(args.control, [])
    dropped = {arm: len(by_arm[arm]) - len(incremental[arm]) for arm in by_arm}
    if any(dropped.values()):
        print(f"\n  NOTE: --only-this-memory-format="
              f"{args.only_this_memory_format!r} drops "
              f"{', '.join(f'{a} {n}' for a, n in sorted(dropped.items()) if n)} cells "
              f"from the headline.")

    forced_identity = arms_where_found_and_place_are_one_number(by_arm)

    # ================= 0. THE HEADLINE: END TO END =================
    print("\n" + "="*100)
    print("0. THE HEADLINE: END TO END. The robot searches in order to answer, so a")
    print("   better memory shows up as a better first room, fewer rooms, more found.")
    print("="*100)
    for arm, n in sorted(forced_identity.items()):
        print(f"\n  NOTE on {arm}: 'found it within the budget' and 'exact place right' pick out")
        print(f"  EXACTLY THE SAME QUESTIONS - all {n} scorable ones agree, none disagree - and")
        print("  that is forced rather than observed: its first guess IS the room the object was")
        print("  last seen in, so when the search fails, the last-seen shelf is always inside a")
        print("  room it has already opened. Reported as ONE column against this arm, never as")
        print("  two findings. The two SHARES still differ by a few tenths of a point, because")
        print("  unscorable questions are in the first denominator and not the second - which is")
        print("  why the claim is about the questions and not about the number.")
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
            if arm == args.control or not here[arm]:
                continue
            print(f"    -- {arm} against the control:")
            one_number = arm in forced_identity or args.control in forced_identity
            measures = [("first room was the right one (the MEMORY question)",
                         "share_first_room_was_right"),
                        ("rooms opened per question (lower is better)", "mean_rooms_opened")]
            if one_number:
                # BOTH LINES, each labelled as the same questions. Collapsing them to one line
                # was wrong in the other direction: the two shares are NOT the same number
                # (different denominators - the unscorable questions), and the exact-place
                # difference is its own finding. What must not happen is the two being read as
                # two independent agreements, so each label says they are one set of questions.
                measures += [("found within budget (SAME questions as exact place)",
                              "share_found_within_budget"),
                             ("exact place right (same questions; other denominator)",
                              "share_correct_shelf")]
            else:
                measures += [("found it within the budget (what an OWNER feels)",
                              "share_found_within_budget"),
                             ("final answer right, shelf", "share_correct_shelf")]
            measures.append(("exact place, unscorable counted as wrong",
                             "share_correct_shelf_counting_unscorable_as_wrong"))
            measures.append(("final answer right, room", "share_correct_room"))
            for label, field in measures:
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
            # restricted to the PAIR that differs only in memory style, so this table is
            # not a mix of arms. Which arm holds the rewrite is an argument for the same
            # reason the control is: the wave calls it `wholesale_rewrite`.
            these = [r for r in these if r["arm"] in (args.control, args.wholesale_arm)]
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
                    ("first room was the right one (the MEMORY question)",
             "share_first_room_was_right"),
                    ("rooms opened per question (lower is better)", "mean_rooms_opened"),
                    ("found it within the budget (what an OWNER feels)",
             "share_found_within_budget"),
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
        if arm == args.control:
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
            if arm == args.control or not present[arm]:
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

    # ---- where in the search it arrived, on the moved objects
    print("\n--- 1c. WHERE IN THE SEARCH IT ARRIVED, on the objects the illness moves\n")
    print("  First-room-right and never-arrived are different failures. An arm that reaches the")
    print("  right room on step two or three by elimination is reasoning; one that never arrives")
    print("  is not - and the difference bears on rooms-opened rather than on first-room.\n")
    print("  Two numbers, and they are not interchangeable: '1st' is the memory question -")
    print("  did the notes point at the right room before any looking. 'arrived' is what an")
    print("  owner feels - did it get there at all within its three rooms. On hh_s48_t03 days")
    print("  14+ those were 10 of 17 and 13 of 17, which read very differently.\n")
    print(f"  {'arm':38s} {'window':16s} {'n':>4s} {'1st':>6s} {'2nd':>5s} {'3rd':>5s} "
          f"{'never':>6s} {'arrived':>8s}")
    for arm in sorted(by_arm):
        for period in ("disrupted", "back to normal"):
            got = [r["live"]["where_it_arrived_on_movers"].get(period) for r in by_arm[arm]
                   if r["live"].get("where_it_arrived_on_movers", {}).get(period)]
            if not got:
                continue
            n = sum(x["n"] for x in got)
            step = lambda k: sum(x["at_step"].get(k, 0) for x in got)
            print(f"  {arm:38s} {period:16s} {n:4d} {step('1'):6d} {step('2'):5d} "
                  f"{step('3'):5d} {step('never'):6d} "
                  f"{(n-step('never'))/n if n else 0:7.0%}")

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
