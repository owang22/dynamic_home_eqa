"""The primary measurement: freeze the notes, then answer with no further looking.

An arm that answers well might have better notes, or it might simply have
searched better and be answering from a fresh sighting. Those are different
claims and the paper only makes the first one. So at each freeze point we take
each arm's notes exactly as they stand, stop all looking, and put the same
held-out questions to every arm.

Freeze points, by day index:
  13   the end of the ordinary fortnight, before anything has changed. Expected
       to be a null: no arm has seen the disruption yet, so this is the control
       that tells us the arms are otherwise comparable. If they differ here,
       something other than the intervention is differing.
  23   the end of the disrupted period, the night before the resident is back.
       This is where the study's prediction lives: notes that kept the ordinary
       routine alongside the new one should answer both kinds of question.
  31   the end of the back-to-normal period, which tests whether the ordinary
       routine was reused rather than relearned.

The held-out questions are the frozen bank's own question rows for the days
AFTER the freeze, so no arm has seen the answers and every arm gets the same
list. Nothing about the questions depends on the arm.

The answer format, the retrieval budget and the prompt are identical across
arms. The only difference is what the notes contain and how they were written.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.patrol.llm import CONF_SCALE, CONF_SCHEMA, LLMClient, parse_conf
from baselines.types import DAY_SECONDS
from self_improve.frozen_household import (BEYOND_REACH, FrozenHousehold, period_of_day,
                                           plain_place_name)
from self_improve.looking import hours_and_minutes
from self_improve.memory_notes import Notes

# Which day's notes are frozen, and which days' questions are then asked of them.
# Every question in the window, not a held-out slice of it. With the
# post-question truth removed, asking a question teaches the robot nothing, so
# there is nothing to hold out against and a slice would throw away free power.
# One day of questions gave only 4 to 16 usable ones per household - a standard
# error of up to 25 percentage points on one household's share - so the whole
# window it is.
#
# Three freeze points, and what each can and cannot show. The room each leaves is
# measured on the frozen banks and stated here so no arm is read without it.
FREEZE_POINTS = {
    "before anything changed": {
        "notes_through_day": 13, "questions_from_days": list(range(14, 24)),
        "what_it_tests": (
            "the control. No arm has seen a disrupted day, so every arm has the "
            "same information and they should agree. If they differ here, "
            "something other than the intervention is differing."),
        "room_to_move": (
            "a memory that learned only the ordinary fortnight scores 13-60% "
            "(mean 34%) here; nothing any arm does can change that at this "
            "freeze point"),
    },
    "did it learn the new routine": {
        "notes_through_day": 23, "questions_from_days": list(range(14, 24)),
        "what_it_tests": (
            "revision. The notes have seen the whole disrupted period; the "
            "questions are that period's own."),
        "room_to_move": (
            "floor 34% (the ordinary fortnight's places, never revised), ceiling "
            "80% (every object's own commonest place in this window, known "
            "perfectly): 46 percentage points of room"),
    },
    "did the looking arm find it sooner": {
        "notes_through_day": 16, "questions_from_days": list(range(17, 20)),
        "what_it_tests": (
            "the LOOKING factor, which is only visible early. At one room a day a "
            "fixed rotation has already found 92% of the moved objects by about "
            "day 4.4, so by any late freeze point both looking arms have seen "
            "everything and will sit on top of each other. The looking factor has "
            "to be reported here and the memory factor at the late points."),
        "room_to_move": (
            "three days of questions, 72 per household: thin, so the looking "
            "factor is reported with its own standard error and never pooled with "
            "the memory factor"),
    },
    "did it keep the old routine": {
        "notes_through_day": 28, "questions_from_days": list(range(29, 32)),
        "what_it_tests": (
            "preservation, and this is where the study's prediction lives. Notes "
            "that kept the ordinary-routine claim alongside the new one should "
            "answer the return; notes that overwrote it should not."),
        "room_to_move": (
            "keeping the ordinary routine is worth about 68% here and is already "
            "within 2 points of this window's oracle; replacing it with the "
            "disrupted routine is worth about 45%. So the predicted gap between "
            "the two ways of writing notes is roughly 23 percentage points. "
            "Frozen at day 28, not 31: at day 31 the questions come from days the "
            "notes have already been written over."),
    },
}

SYSTEM = ("You help a home robot keep track of where household things are. "
          "Read the robot's notes and answer with JSON only.")


@dataclass
class HeldOutAnswer:
    question_id: str
    object_id: str
    object_class: str
    day: int
    time: int
    period: str
    answer_place: Optional[str]
    true_place: Optional[str]
    correct: Optional[bool]
    confidence: Optional[float]
    reasoning: str
    parse_status: str


def questions_in_the_window(household: FrozenHousehold, days: Sequence[int]) -> List[dict]:
    """The same list for every arm: every one of the bank's questions on these
    days, dropping only the ones whose answer no look could ever reach."""
    out = []
    for day in days:
        for question in household.questions_on_day(day):
            true_place = household.true_place_for_question(question)
            if true_place is None:
                continue
            if household.room_of_object(question["object_id"],
                                        question["t_query"]) == BEYOND_REACH:
                continue
            out.append(question)
    return sorted(out, key=lambda q: (q["t_query"], q["question_id"]))


def questions_a_settled_memory_gets_wrong(household: FrozenHousehold,
                                          questions: Sequence[dict]) -> set:
    """The only questions that can separate the arms.

    A memory that learned the ordinary fortnight and then never updated already
    answers a good share of any window correctly, because most objects never
    move. Those questions carry no information about the intervention and they
    dilute every difference. This is the yardstick: answer every question with
    the object's commonest place during the settled period, and collect the ones
    it gets wrong.

    The commonest place is counted at the moments the questions were ASKED, not
    over an even grid of hours. That is not a detail: counted over an hourly grid
    the same yardstick scores 30% on the settled days instead of 70%, because an
    even grid weights the long stretches when things sit still and the questions
    are asked while things are in use. The grid version would have marked 94-98%
    of every window as "separating", which is meaningless.
    """
    commonest = commonest_place_when_settled(household)
    wrong = set()
    for question in questions:
        if commonest.get(question["object_id"]) != household.true_place_for_question(question):
            wrong.add(question["question_id"])
    return wrong


def commonest_place_when_settled(household: FrozenHousehold) -> Dict[str, Optional[str]]:
    """Each asked object's commonest place across the settled fortnight, counted
    at question moments."""
    import collections
    counts: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for question in household.questions:
        if question["day_index"] >= 14:
            continue
        place = household.true_place_for_question(question)
        if place and household.room_of_object(question["object_id"],
                                              question["t_query"]) != BEYOND_REACH:
            counts[question["object_id"]][place] += 1
    return {object_id: (c.most_common(1)[0][0] if c else None)
            for object_id, c in counts.items()}


def yardsticks_for_a_window(household: FrozenHousehold,
                            questions: Sequence[dict]) -> Dict[str, Any]:
    """The three numbers every arm must be read against. Reproduced exactly
    against an independent measurement on 2026-09-24: on the disrupted window the
    one-fact yardstick averages 58% and the per-object oracle 80%.

      one fact for the whole house   answer every question with the single
                                     commonest place in the window. No per-object
                                     knowledge at all.
      per-object oracle              know every object's own commonest place in
                                     this window, perfectly. The ceiling for any
                                     memory that stores one place per object.
      settled memory, never updated  the commonest place from the ordinary
                                     fortnight, never revised. The floor an
                                     updating memory must beat.
    """
    import collections
    truths = [household.true_place_for_question(q) for q in questions]
    n = len(questions)
    if not n:
        return {}
    whole_house = collections.Counter(truths)
    per_object: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for question, truth in zip(questions, truths):
        per_object[question["object_id"]][truth] += 1
    settled = commonest_place_when_settled(household)
    return {
        "n_questions": n,
        "one_fact_for_the_whole_house": whole_house.most_common(1)[0][1] / n,
        "the_one_fact": whole_house.most_common(1)[0][0],
        "per_object_oracle": sum(c.most_common(1)[0][1] for c in per_object.values()) / n,
        "settled_memory_never_updated":
            sum(1 for q, t in zip(questions, truths) if settled.get(q["object_id"]) == t) / n,
    }


def question_prompt(household: FrozenHousehold, notes: Notes, question: dict,
                    retrieval_budget: int) -> List[dict]:
    """Identical across arms apart from the notes themselves."""
    places = sorted(household.places)
    lines = [
        f"It is day {question['day_index']} at {hours_and_minutes(question['t_query'])}.",
        "",
        "The rooms of this home and the spots in each:",
    ]
    for room in household.rooms:
        lines.append(f"- {room}: {', '.join(household.places_in_room[room])}")
    lines += [
        "",
        "The robot has not been told where anything is. Everything it knows comes",
        "from looks it took. These are its notes:",
        "",
        notes.what_the_robot_can_read(retrieval_budget),
        "",
        f"Question: where is {question['object_id']} right now?",
        "",
        "Name exactly one spot from the list above. " + CONF_SCALE,
    ]
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": "\n".join(lines)}]


def run_frozen_memory_test(household: FrozenHousehold, notes: Notes, client: LLMClient,
                           freeze_point: str, retrieval_budget: int,
                           out_dir: pathlib.Path,
                           max_questions: Optional[int] = None) -> Dict[str, Any]:
    """Freeze these notes and answer the held-out questions. No looking happens
    here at all: the notes are read-only for the whole test."""
    if freeze_point not in FREEZE_POINTS:
        raise ValueError(f"unknown freeze point {freeze_point!r}; "
                         f"expected one of {sorted(FREEZE_POINTS)}")
    plan = FREEZE_POINTS[freeze_point]
    if notes.written_up_to_day != plan["notes_through_day"]:
        raise ValueError(
            f"{household.name}/{notes.arm}: notes are written up to day "
            f"{notes.written_up_to_day} but the freeze point "
            f"{freeze_point!r} needs day {plan['notes_through_day']}")

    questions = questions_in_the_window(household, plan["questions_from_days"])
    if max_questions is not None:
        questions = questions[:max_questions]
    allowed = set(household.places)

    out_dir.mkdir(parents=True, exist_ok=True)
    frozen = notes.snapshot_to(out_dir / "notes_as_frozen.json")
    settled_memory_wrong = questions_a_settled_memory_gets_wrong(household, questions)
    answers: List[HeldOutAnswer] = []
    for question in questions:
        messages = question_prompt(household, frozen, question, retrieval_budget)
        text, _ = client.complete(messages, CONF_SCHEMA, max_tokens=400)
        place, confidence, reasoning, status = parse_conf(text, allowed)
        true_place = household.true_place_for_question(question)
        answers.append(HeldOutAnswer(
            question_id=question["question_id"], object_id=question["object_id"],
            object_class=question.get("object_class", ""),
            day=question["day_index"], time=question["t_query"],
            period=period_of_day(question["day_index"]),
            answer_place=place, true_place=true_place,
            correct=None if place is None else place == true_place,
            confidence=confidence, reasoning=reasoning, parse_status=status))

    scored = [a for a in answers if a.correct is not None]
    result = {
        "household": household.name,
        "arm": notes.arm,
        "how_memory_is_written": notes.how_memory_is_written,
        "freeze_point": freeze_point,
        "notes_written_up_to_day": notes.written_up_to_day,
        "retrieval_budget": retrieval_budget,
        "n_questions_asked": len(answers),
        "n_questions_scored": len(scored),
        "n_correct": sum(1 for a in scored if a.correct),
        "share_correct": (sum(1 for a in scored if a.correct) / len(scored)) if scored else None,
        "n_unparsed": sum(1 for a in answers if a.correct is None),
        "question_ids_a_settled_memory_gets_wrong": sorted(settled_memory_wrong),
        "answers": [a.__dict__ for a in answers],
    }
    (out_dir / "held_out_answers.json").write_text(json.dumps(result, indent=1))
    return result


# --------------------------------------------------- the first-minute assay --


def sanity_assay(result: Dict[str, Any]) -> Dict[str, Any]:
    """Run this on an arm's first answers, before trusting anything.

    Three ways an arm is broken in a way accuracy will not show:
      the answers pile onto one spot regardless of the question;
      consecutive answers are identical;
      the model would not answer at all.
    """
    answers = result["answers"]
    places = [a["answer_place"] for a in answers if a["answer_place"]]
    counts: Dict[str, int] = {}
    for p in places:
        counts[p] = counts.get(p, 0) + 1
    commonest = max(counts.values()) / len(places) if places else None
    repeats = sum(1 for i in range(1, len(places)) if places[i] == places[i - 1])
    report = {
        "n_answers": len(answers),
        "n_distinct_spots_named": len(counts),
        "share_on_the_commonest_spot": commonest,
        "share_identical_to_the_previous_answer": repeats / (len(places) - 1) if len(places) > 1 else None,
        "share_unparsed": result["n_unparsed"] / len(answers) if answers else None,
        "concerns": [],
    }
    if commonest is not None and commonest > 0.6:
        report["concerns"].append(
            f"{commonest:.0%} of answers name the same spot: the answer distribution is degenerate")
    if len(counts) <= 2 and len(places) > 10:
        report["concerns"].append(
            f"only {len(counts)} distinct spots ever named across {len(places)} answers")
    if report["share_identical_to_the_previous_answer"] is not None and \
            report["share_identical_to_the_previous_answer"] > 0.8:
        report["concerns"].append("consecutive answers are nearly always identical")
    if report["share_unparsed"] and report["share_unparsed"] > 0.1:
        report["concerns"].append(
            f"{report['share_unparsed']:.0%} of answers did not parse")
    return report
