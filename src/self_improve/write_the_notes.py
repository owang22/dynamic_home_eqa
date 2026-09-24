"""How the robot writes its notes each night. This is factor one of the study.

Two ways, and the prompts are identical apart from the way itself:

  wholesale rewrite   the model is shown today's looks and last night's summary,
                      and writes a new summary of the household from scratch.
  incremental edits   the model is shown today's looks and its current claims,
                      and emits individual edits: add a claim, revise one, or
                      attach today's evidence to one.

Both are shown today's looks through the same function,
`looking.describe_look_for_the_model`, so both receive sightings and absences in
exactly the same words. If only one format could represent "looked and it was not
there", the two factors would be confounded and no measured difference would be
attributable to either.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Sequence

from baselines.patrol.llm import LLMClient
from self_improve.frozen_household import FrozenHousehold, period_of_day
from self_improve.looking import LookRecord, describe_look_for_the_model
from self_improve.memory_notes import ESTABLISHED, PROVISIONAL, SET_ASIDE, STILL_STANDING, Notes

SYSTEM = ("You help a home robot keep notes about where a household's things are "
          "kept. Nobody tells the robot the right answer; everything it knows "
          "comes from looking. Answer with JSON only.")

EDITS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "edits": {
            "type": "array", "maxItems": 8,
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["add", "revise", "record evidence"]},
                    "claim_id": {"type": ["string", "null"]},
                    "statement": {"type": ["string", "null"], "maxLength": 240},
                    "holds_under": {"type": ["string", "null"], "maxLength": 120},
                    "status": {"type": ["string", "null"],
                               "enum": [PROVISIONAL, ESTABLISHED, None]},
                    "standing": {"type": ["string", "null"],
                                 "enum": [STILL_STANDING, SET_ASIDE, None]},
                    "supporting_observation_ids": {"type": "array", "items": {"type": "string"},
                                                   "maxItems": 6},
                    "contradicting_observation_ids": {"type": "array", "items": {"type": "string"},
                                                      "maxItems": 6},
                    "why": {"type": "string", "maxLength": 240},
                },
                "required": ["action", "claim_id", "statement", "holds_under", "status",
                             "standing", "supporting_observation_ids",
                             "contradicting_observation_ids", "why"],
                "additionalProperties": False},
        },
    },
    "required": ["edits"], "additionalProperties": False}

SUMMARY_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {"summary": {"type": "string", "maxLength": 2400}},
    "required": ["summary"], "additionalProperties": False}


def _what_happened_today(looks_today: Sequence[LookRecord],
                         asked_objects: Sequence[str]) -> str:
    if not looks_today:
        return "The robot did not look anywhere today."
    return "\n\n".join(describe_look_for_the_model(look, asked_objects)
                       for look in looks_today)


def _shared_preamble(household: FrozenHousehold, day: int,
                     looks_today: Sequence[LookRecord]) -> List[str]:
    """Every word here is the same for both ways of writing notes."""
    return [
        f"It is the end of day {day}.",
        "",
        "The rooms of this home and the spots in each:",
        *[f"- {room}: {', '.join(household.places_in_room[room])}"
          for room in household.rooms],
        "",
        "The things the robot is asked about: " + ", ".join(household.asked_objects),
        "",
        "Nobody tells the robot where anything is. What it saw today, and what it",
        "looked for and did not find, is all it has:",
        "",
        _what_happened_today(looks_today, household.asked_objects),
        "",
    ]


def rewrite_the_notes_wholesale(notes: Notes, household: FrozenHousehold, day: int,
                                time: int, looks_today: Sequence[LookRecord],
                                client: LLMClient) -> Dict[str, Any]:
    previous = notes.newest_summary()
    lines = _shared_preamble(household, day, looks_today) + [
        "Your notes as they stand:",
        "",
        previous or "(nothing written yet)",
        "",
        "Write the notes again from scratch. Produce one summary of where this",
        "household keeps the things above, as you now believe it to be. It",
        "replaces what is there: whatever you do not write down is gone.",
        "Say which routine or condition each part of it holds under. A household",
        "can be in more than one routine over a month.",
    ]
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": "\n".join(lines)}]
    text, _ = client.complete(messages, SUMMARY_SCHEMA, max_tokens=900)
    summary = None
    if text:
        try:
            summary = json.loads(text).get("summary")
        except ValueError:
            summary = None
    if summary is None:
        summary = previous or ""
        failed = True
    else:
        failed = False
    notes.write_nightly_summary(day, time, summary)
    return {"day": day, "model_call_failed": failed,
            "n_characters": len(summary),
            "identical_to_last_night": bool(previous) and summary.strip() == previous.strip()}


def write_the_notes_incrementally(notes: Notes, household: FrozenHousehold, day: int,
                                  time: int, looks_today: Sequence[LookRecord],
                                  client: LLMClient) -> Dict[str, Any]:
    current = ("\n".join(c.as_plain_words() for c in notes.claims)
               if notes.claims else "(nothing written yet)")
    lines = _shared_preamble(household, day, looks_today) + [
        "Your notes as they stand. Each one is a separate claim with its own id:",
        "",
        current,
        "",
        # THE INSTRUCTION COMES FIRST AND THE EXPLANATION AFTER. Measured on
        # 2026-09-24: with the explanation first - even one sentence of it - this
        # model replied {"edits": []} to a night with six fresh sightings and an
        # empty notes file, on every variant tried. Put the imperative first and
        # it writes the edits. That is a silently empty arm no accuracy number
        # would have exposed, so any edit to this block must be re-smoked for it:
        # run compare_the_two_memory_formats on a few days and check that night 0
        # produces edits.
        "Write the edits today's looks call for: anything you saw today that no "
        "claim covers yet needs a claim, and anything a claim got wrong needs "
        "that claim revised.",
        "",
        "An edit either adds a new claim, revises an existing claim by its id, or "
        "attaches today's observation ids to an existing claim by its id as "
        "supporting or contradicting evidence.",
        "",
        "Revising a claim keeps its previous wording in its history, so a claim "
        f'is never lost. Set a claim\'s standing to "{SET_ASIDE}" when the '
        "evidence now goes against it: that keeps the claim and records that it "
        "is not holding at the moment. A claim about one routine does not have "
        "to be undone to write a claim about another. A household can be in more "
        "than one routine over a month and your notes can hold claims for each.",
        "",
        "Cite the observation ids in square brackets above for anything you "
        "assert. If today's looks only confirm what a claim already says, attach "
        "the evidence to it rather than writing the claim again.",
    ]
    # On a night whose look found something the robot is asked about, the schema
    # REQUIRES at least one edit. Measured on 2026-09-24, one household, 29
    # nights: without it the model replied {"edits": []} on 17 of the 19 nights
    # that saw an asked-about object, ending the month with 6 claims for a
    # 15-object household while the rewrite arm wrote 1,885 characters. Wording
    # the instruction three different ways did not fix it; the schema does. A
    # night that found nothing is still allowed to make no edit, so the model is
    # never forced to invent.
    saw_something = any(s["object_id"] in set(household.asked_objects)
                        for look in looks_today for s in look.sightings)
    schema = EDITS_SCHEMA
    if saw_something:
        schema = json.loads(json.dumps(EDITS_SCHEMA))
        schema["properties"]["edits"]["minItems"] = 1
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": "\n".join(lines)}]
    text, _ = client.complete(messages, schema, max_tokens=1400)
    edits: List[dict] = []
    if text:
        try:
            edits = json.loads(text).get("edits") or []
        except ValueError:
            edits = []
    applied = {"add": 0, "revise": 0, "record evidence": 0}
    rejected: List[str] = []
    for edit in edits:
        action = edit.get("action")
        try:
            if action == "add":
                if not edit.get("statement"):
                    rejected.append("add with no statement")
                    continue
                notes.add_claim(edit["statement"], edit.get("holds_under") or "not said",
                                day, time,
                                edit.get("supporting_observation_ids") or (),
                                edit.get("status") or PROVISIONAL)
                applied["add"] += 1
            elif action == "revise":
                notes.revise_claim(edit["claim_id"], day, time,
                                   new_statement=edit.get("statement"),
                                   new_holds_under=edit.get("holds_under"),
                                   new_status=edit.get("status"),
                                   new_standing=edit.get("standing"),
                                   why=edit.get("why") or "")
                applied["revise"] += 1
            elif action == "record evidence":
                for ids, supports in ((edit.get("supporting_observation_ids") or (), True),
                                      (edit.get("contradicting_observation_ids") or (), False)):
                    if ids:
                        notes.record_evidence(edit["claim_id"], ids, day, time, supports)
                applied["record evidence"] += 1
            else:
                rejected.append(f"unknown action {action!r}")
        except (KeyError, ValueError) as problem:
            rejected.append(f"{action}: {problem}")
    notes.written_up_to_day = day
    return {"day": day, "model_call_failed": not text,
            "the_look_saw_something_it_is_asked_about": saw_something,
            "at_least_one_edit_was_required": saw_something,
            "n_edits_offered": len(edits), "applied": applied,
            "rejected": rejected, "n_claims_now": len(notes.claims)}


def write_the_notes(notes: Notes, household: FrozenHousehold, day: int, time: int,
                    looks_today: Sequence[LookRecord], client: LLMClient) -> Dict[str, Any]:
    if notes.how_memory_is_written == "wholesale rewrite":
        return rewrite_the_notes_wholesale(notes, household, day, time, looks_today, client)
    return write_the_notes_incrementally(notes, household, day, time, looks_today, client)
