"""The third way of writing the notes: itemised edits, told whether they worked.

The two ways of writing notes this study started with differ in one thing - whether
the model rewrites one summary or edits a list of claims - and NEITHER of them is
ever told whether its notes actually worked. The robot answers questions all day,
gets them right or wrong, and at night the writer sees only what the robot saw. The
results the notes produced are thrown away.

This module adds the third way. It keeps the claim list of the second way and adds
the two things the method in arxiv 2510.04618 (Zhang, Wang et al., "Agentic Context
Engineering") has and the second way does not:

  told if it was right   Every night the writer is shown the day's questions with
                         what the robot did and whether it worked: which rooms it
                         opened in order, whether the first one held the object,
                         where the object really was, and which of its own claims
                         were about that object. It says which claim helped, which
                         misled, and what it wants changed. That is the paper's
                         Reflector, and its input - the outcome of the task - is
                         the input the second way never gets.

  it may join two notes  An edit may fold one claim into another, so two lines
                         about one object become one line. The second way can only
                         add, reword or set aside, so its notes only ever grow -
                         which is the failure the paper's "grow and refine" step
                         exists to stop, and which this study has already measured
                         as an unbounded read window.

Nothing is deleted. A folded claim keeps its wording, its history and its evidence
and stops being shown, so the question this study turns on - is the ordinary
routine still written down - can be asked of this arm exactly as of the others.

Three differences from the paper, all deliberate and all to be stated in the write-up:
  - the paper's Generator is a reasoning model producing trajectories; here it is
    the robot's own room choices and answers, which is the task this study has.
  - the paper scores its playbook lines on a benchmark with a known answer key. Here
    the outcome is whether the first room opened held the object, which is the
    measure the study reports, so the feedback is honest: nothing in it tells the
    robot a place it has not seen.
  - the paper dedups by comparing sentence vectors. Here the model is asked to fold,
    with a deterministic backstop below when it does not and the notes are over the
    line it has been given.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Sequence

from self_improve import what_the_robot_is_told as told
from self_improve import write_the_notes as writing
from self_improve.frozen_household import FrozenHousehold
from baselines.patrol.llm import LLMClient
from self_improve.looking import LookRecord
from self_improve.memory_notes import (ESTABLISHED, PROVISIONAL, SET_ASIDE,
                                       STILL_STANDING, TOLD_IF_IT_WAS_RIGHT, Notes)

JUDGING_SYSTEM = (
    "You are a robot in somebody's home. At the end of each day you look back at what "
    "you were asked and work out which of your own notes were any use. Answer with JSON "
    "only.")

# When this arm is told it should be able to say what it knows in fewer lines. It is
# NOT the read budget and it is not a limit the other two arms get: the read budget is
# unlimited for every arm, and this number only decides the night on which this arm is
# told "you are carrying more lines than you should need, so join or set aside as well
# as add".
#
# Three lines for each object the robot is asked about, and the reason is measured
# rather than chosen. A mover in these households can be in three states, not two: its
# ordinary spot, the spot it moves to while someone is ill, and where it ends up when
# ordinary life returns - because across the ten homes only 51 of 75 movers, 68%, go
# back to exactly the spot they came from. The other 24 need a third live claim. Two
# lines per object would force a join precisely on the objects whose history the study
# is about, and on the nights after day 24 when the question "is the ordinary claim
# still there" is being asked. Counted by
# results/self_improve/check_how_many_states_a_mover_has.py.
LINES_PER_ASKED_OBJECT_BEFORE_IT_MUST_JOIN = 3

JUDGEMENT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array", "maxItems": 12,
            "items": {
                "type": "object",
                "properties": {
                    "claim_id": {"type": "string"},
                    "it": {"type": "string", "enum": ["helped", "misled"]},
                    "about": {"type": "string", "maxLength": 80},
                    "what_it_taught": {"type": "string", "maxLength": 200},
                },
                "required": ["claim_id", "it", "about", "what_it_taught"],
                "additionalProperties": False}},
        "what_to_change_tonight": {"type": "array", "maxItems": 6,
                                   "items": {"type": "string", "maxLength": 200}},
    },
    "required": ["verdicts", "what_to_change_tonight"], "additionalProperties": False}

EDITS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "edits": {
            "type": "array", "maxItems": 10,
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string",
                               "enum": ["add", "revise", "record evidence",
                                        "join two claims"]},
                    "claim_id": {"type": ["string", "null"]},
                    "join_in_claim_id": {"type": ["string", "null"]},
                    "statement": {"type": ["string", "null"], "maxLength": 240},
                    "holds_under": {"type": ["string", "null"], "maxLength": 120},
                    "status": {"type": ["string", "null"],
                               "enum": [PROVISIONAL, ESTABLISHED, None]},
                    "standing": {"type": ["string", "null"],
                                 "enum": [STILL_STANDING, SET_ASIDE, None]},
                    "supporting_observation_ids": {"type": "array", "maxItems": 6,
                                                   "items": {"type": "string"}},
                    "contradicting_observation_ids": {"type": "array", "maxItems": 6,
                                                      "items": {"type": "string"}},
                    "why": {"type": "string", "maxLength": 240},
                },
                "required": ["action", "claim_id", "join_in_claim_id", "statement",
                             "holds_under", "status", "standing",
                             "supporting_observation_ids",
                             "contradicting_observation_ids", "why"],
                "additionalProperties": False}}},
    "required": ["edits"], "additionalProperties": False}


# --------------------------------------------------------- what the day showed --

def claims_that_name(notes: Notes, object_id: str) -> List[Any]:
    """The live claims that mention this object, by the audited matcher.

    `write_the_notes.where_an_object_is_named` is the same matcher every compliance
    number in this study is computed with, so a claim counts as being about an
    object here exactly when it counts everywhere else.
    """
    return [c for c in notes.claims_in_reading_order(object_id)
            if writing.where_an_object_is_named(c.statement, object_id) >= 0]


def the_day_in_results(notes: Notes, answers_today: Sequence[Any]) -> List[str]:
    """The day's questions and what the robot did, using ONLY what the robot saw.

    NOTHING HERE MAY NAME A PLACE THE ROBOT DID NOT LOOK AT. The first version of
    this function printed "WRONG - the book was in the bedroom" whenever the first
    room opened was not the true room, and printed the true place on every question
    including the ones where the search ran out of rooms and never found the object.
    That is the answer key. The other two arms are never told where anything is - it
    is the first line of memory_notes - so an arm that gets it nightly cannot be
    compared with them on accuracy at all. Found by the research agent checking this
    module against the paper it is built from, before any number was read.

    What the robot genuinely knows at the end of a search, and so what this may say:
      - which rooms it walked into, in order. It chose them.
      - whether the FIRST room had the object: it looked, so it knows.
      - where the object was, but only when the search actually found it. Then it
        saw it with its own eyes.
      - when the search did not find it: that the object was in none of the rooms it
        opened, and that the answer it gave came from its notes and has not been
        marked right or wrong by anyone. That is the real situation a robot is in.
    """
    if not answers_today:
        return ["Nobody asked the robot anything today."]
    out: List[str] = []
    for row in answers_today:
        rooms = ", ".join(row.rooms_opened) if row.rooms_opened else "nowhere"
        first_had_it = bool(row.found_it) and row.found_at_step == 1
        mine = claims_that_name(notes, row.object_id)
        out.append(f"- You were asked where {row.object_id} was. You walked into: "
                   f"{rooms}.")
        if row.rooms_opened:
            out.append("  The first room you tried " +
                       ("HAD it." if first_had_it else "did NOT have it."))
        if row.found_it:
            # It saw the object. Naming the spot is its own observation.
            out.append(f"  You found {row.object_id} on the {row.true_place} in the "
                       f"{row.true_room}.")
        else:
            out.append(f"  You did NOT find {row.object_id} in any room you opened, so "
                       f"it was in none of them. You answered "
                       f"{row.answer_place or 'nothing'} from your notes, and nobody has "
                       f"told you whether that was right.")
        if mine:
            out.append("  Your notes about it at the time: " +
                       "; ".join(f"[{c.claim_id}] {c.statement}" for c in mine))
        else:
            out.append(f"  You had no note about {row.object_id}.")
    return out


def _structured_verdicts(notes: Notes, answers_today: Sequence[Any]) -> List[dict]:
    """The fallback, computed and not asked for - and computed from the looks only.

    A night where the model returns no verdict must not leave the arm with an empty
    tally, or its reading order silently becomes the second arm's. The rule uses one
    fact, which the robot has from its own looking: did the FIRST room it opened hold
    the object. Every live claim naming that object counts as having helped when it
    did and as having misled when it did not. No ground truth is read here, for the
    same reason the prompt above may not state any: a tally built from the answer key
    would move the reading order using information the other arms never get.

    It is coarse - a claim about a different routine gets the same mark as the one
    that was used - which is why the model is asked first and this only fills a gap.
    """
    out: List[dict] = []
    for row in answers_today:
        if not row.rooms_opened:
            continue
        helped = bool(row.found_it) and row.found_at_step == 1
        for claim in claims_that_name(notes, row.object_id):
            out.append({"claim_id": claim.claim_id,
                        "it": "helped" if helped else "misled",
                        "about": row.object_id,
                        "what_it_taught": "counted by rule, not by the model: the "
                                          "first room it opened "
                                          + ("had it" if helped else "did not have it")})
    return out


def judge_the_day(notes: Notes, household: FrozenHousehold, day: int,
                  answers_today: Sequence[Any], client: LLMClient) -> Dict[str, Any]:
    """Step one of the night: which notes helped, which misled, what to change."""
    lines = (
        told.the_people_who_live_here(household.asked_objects, household.resident_ids)
        + ["",
           f"It is the end of day {day}. Here is what you were asked today, what you did, "
           f"and whether it worked.",
           "",
           *the_day_in_results(notes, answers_today),
           "",
           "Say which of your notes helped you and which sent you the wrong way, and what "
           "you want changed tonight.",
           "",
           "A note helped if it sent you into the right room first. A note sent you the "
           "wrong way if you went where it pointed and the thing was not there. Only "
           "judge the notes listed above, by their number.",
           "",
           "A note can be wrong now because the home has changed, or it can have been "
           "wrong all along. It may help to say which of the two you think it is, because "
           "they call for different things: one needs correcting, and one may be worth "
           "keeping beside a new note.",
           "",
           told.how_much_you_may_write(200)])
    text, _ = client.complete(
        [{"role": "system", "content": JUDGING_SYSTEM},
         {"role": "user", "content": "\n".join(lines)}],
        JUDGEMENT_SCHEMA, max_tokens=1200)
    verdicts, wanted = [], []
    if text:
        try:
            got = json.loads(text)
            verdicts = got.get("verdicts") or []
            wanted = got.get("what_to_change_tonight") or []
        except ValueError:
            verdicts, wanted = [], []
    known = {c.claim_id for c in notes.claims}
    kept = [v for v in verdicts if v.get("claim_id") in known
            and v.get("it") in ("helped", "misled")]
    n_named_a_claim_that_does_not_exist = len(verdicts) - len(kept)
    counted_by_rule = False
    if not kept:
        kept = _structured_verdicts(notes, answers_today)
        counted_by_rule = bool(kept)
    for v in kept:
        notes.record_what_a_claim_did(v["claim_id"], v["it"] == "helped", day,
                                     v.get("about") or "",
                                     v.get("what_it_taught") or "")
    return {"model_call_failed": not text,
            "n_verdicts_offered": len(verdicts),
            "n_verdicts_kept": len(kept),
            "n_named_a_claim_that_does_not_exist": n_named_a_claim_that_does_not_exist,
            "the_verdicts_were_counted_by_rule_not_by_the_model": counted_by_rule,
            "n_helped": sum(1 for v in kept if v["it"] == "helped"),
            "n_misled": sum(1 for v in kept if v["it"] == "misled"),
            "what_it_wants_changed": wanted,
            "verdicts": kept}


# ----------------------------------------------------------- changing the notes --

def change_the_notes(notes: Notes, household: FrozenHousehold, day: int, time: int,
                     looks_today: Sequence[LookRecord],
                     judgement: Dict[str, Any], client: LLMClient,
                     max_edits: Optional[int] = None,
                     tell_the_model_everything_it_saw: bool = True,
                     name_the_objects_it_will_be_quizzed_on: bool = False,
                     a_message_tonight: Optional[str] = None) -> Dict[str, Any]:
    """Step two: the itemised edits, this time knowing how today went."""
    live = [c for c in notes.claims if c.folded_into is None]
    current = ("\n".join(c.as_plain_words() for c in notes.claims_in_reading_order())
               if live else "(nothing written yet)")
    allowed = max(LINES_PER_ASKED_OBJECT_BEFORE_IT_MUST_JOIN
                  * len(household.asked_objects), 6)
    over = len(live) > allowed
    judged = []
    for v in judgement.get("verdicts", []):
        judged.append(f"- [{v['claim_id']}] {v['it']} on {v.get('about') or 'a question'}"
                      + (f": {v['what_it_taught']}" if v.get("what_it_taught") else ""))
    wanted = judgement.get("what_it_wants_changed") or []
    # The imperative comes first here too, for the reason recorded in
    # write_the_notes.write_the_notes_incrementally: with the explanation first this
    # model answers a night of fresh sightings with an empty edit list.
    told_what_happened = (
        ["HOW YOUR NOTES DID TODAY, from your own reading of it:"]
        + (judged or ["- nothing was asked, or no note was about what was asked."])
        + (["", "What you said you wanted changed tonight:"] + [f"- {w}" for w in wanted]
           if wanted else [])
        + ["",
           f"You are carrying {len(live)} note(s). " +
           (f"That is more than the {allowed} you should need, so tonight it may help to "
            "join notes or set some aside as well as adding."
            if over else f"You may carry up to {allowed}."),
           ""])
    # Every word of the shared part comes from what_the_robot_is_told, and this arm's own
    # words from HOW_YOUR_MEMORY_WORKS. What is above is not instruction, it is what
    # happened today, which is the one thing this arm has and the others do not.
    lines = told.the_nightly_prompt(
        TOLD_IF_IT_WAS_RIGHT, household, day,
        writing._what_happened_today(looks_today, household.asked_objects,
                                     tell_the_model_everything_it_saw),
        current, 240,
        name_the_things_it_is_asked_about=name_the_objects_it_will_be_quizzed_on,
        a_message_tonight=a_message_tonight,
        extra_before_the_instruction=told_what_happened)
    saw_something = any(s["object_id"] in set(household.asked_objects)
                        for look in looks_today for s in look.sightings)
    # The same allowance as the other claim store, for the same reason: this file's
    # constant said ten, and the arm's very first night wrote exactly ten claims, which
    # is what a limit deciding the memory's contents looks like. See
    # write_the_notes.edits_schema for the measurement and the survey behind it.
    cap = (max_edits if max_edits is not None
           else writing.how_many_edits_a_night(household, notes, looks_today))
    schema = json.loads(json.dumps(EDITS_SCHEMA))
    schema["properties"]["edits"]["maxItems"] = cap
    if saw_something or judgement.get("n_misled"):
        schema["properties"]["edits"]["minItems"] = 1
    text, _ = client.complete(
        [{"role": "system", "content": writing.SYSTEM},
         {"role": "user", "content": "\n".join(lines)}], schema,
        # 260 tokens an edit, not 120: measured on a completion that was cut off
        # mid-array at 120, after which the text does not parse and the whole night
        # writes nothing while the call still looks successful.
        max_tokens=300 + 260 * cap)
    edits: List[dict] = []
    # Whether it parsed is not whether it was empty: night 0 has no looks and returns an
    # empty edit list legitimately, and calling that a parse failure refuses every cell.
    did_not_parse = False
    if text:
        try:
            edits = json.loads(text).get("edits") or []
        except ValueError:
            edits, did_not_parse = [], True
    claims_before = [c.statement for c in notes.claims]
    applied = {"add": 0, "revise": 0, "record evidence": 0, "join two claims": 0}
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
            elif action == "join two claims":
                notes.fold_one_claim_into_another(
                    edit["claim_id"], edit["join_in_claim_id"], day, time,
                    new_statement=edit.get("statement"), why=edit.get("why") or "")
                applied["join two claims"] += 1
            else:
                rejected.append(f"unknown action {action!r}")
        except (KeyError, ValueError) as problem:
            rejected.append(f"{action}: {problem}")
    trimmed = keep_the_notes_from_growing(notes, household, allowed, day, time)
    notes.written_up_to_day = day
    return {"n_claims_it_was_showing": len(live),
            "the_completion_did_not_parse": did_not_parse,
            "how_many_lines_it_was_told_it_may_carry": allowed,
            "it_was_told_it_must_join_tonight": over,
            "model_call_failed": not text,
            "n_edits_offered": len(edits),
            # Same diagnostic as write_the_notes.write_the_notes_incrementally: whether
            # tonight ran into the write-time edits-per-night cap. This arm's own first
            # night hit its cap of 10 claims exactly, by the same fault flagged there.
            "how_many_edits_it_was_allowed": cap,
            "the_edits_cap_bit": len(edits) >= cap,
            "applied": applied, "rejected": rejected,
            "at_least_one_edit_was_required": bool(saw_something or judgement.get("n_misled")),
            "n_claims_now": len([c for c in notes.claims if c.folded_into is None]),
            "n_claims_in_the_file": len(notes.claims),
            "joined_by_rule_not_by_the_model": trimmed,
            "were_the_edits_vacuous": writing.were_the_edits_vacuous(
                [e for e in edits if e.get("action") != "join two claims"],
                claims_before, household)}


def keep_the_notes_from_growing(notes: Notes, household: FrozenHousehold,
                                allowed: int, day: int,
                                time: int) -> List[Dict[str, str]]:
    """The backstop for a night the model was told to join and did not.

    Deterministic and recorded, so a reader can tell the model's joining from the
    code's. It folds the claim with the worst record - most times it misled, fewest
    times it helped, oldest - into the live claim it shares most words with, which is
    the crudest honest stand-in for the paper's comparison of sentence vectors. The
    paper does its version lazily, only when the store is over its window, which is
    when this fires too.

    TWO CLAIMS IT MAY NOT TOUCH, and the reason it may not:

      - a claim whose `holds_under` differs from the candidate's. Two claims about the
        SAME object under DIFFERENT routines - the ordinary spot and the spot it moves
        to while someone is ill - share more long words with each other than with
        anything else in the file, so plain word overlap picks exactly that pair
        first. That pair is the one the whole pre-registered prediction is about: the
        claim for the ordinary routine must survive the disrupted one. A backstop that
        collapses it would destroy the thing being measured, silently, on the nights
        the notes were fullest. Found by the research agent reading this function.
      - a claim that has been set aside. Those are the rival beliefs the study wants
        kept, and they collect the worst tallies precisely because they stopped being
        right - so the plain rule would fold them first.
      - a claim that names none of the same objects. Shared words alone picked a claim
        about a DIFFERENT object on the first test of this function, because "kept",
        "the" and a room name are enough overlap. Folding two different objects'
        claims into one line is not removing a repeat, it is making the notes harder
        to read. Two claims must name a common object the robot is asked about.

    When nothing may be folded, the notes stay over the line they were given. Carrying
    an extra line is a cost; losing the difference between two routines is not a cost,
    it is the result.
    """
    done: List[Dict[str, str]] = []
    def live():
        return [c for c in notes.claims if c.folded_into is None]
    def words(claim):
        return {w for w in claim.statement.lower().split() if len(w) > 3}
    def same_routine(a, b):
        return a.holds_under.strip().lower() == b.holds_under.strip().lower()
    def objects_named(claim):
        return {o for o in household.asked_objects
                if writing.where_an_object_is_named(claim.statement, o) >= 0}
    while len(live()) > allowed:
        here = live()
        candidates = [c for c in here if c.standing != SET_ASIDE]
        if not candidates:
            break
        worst = sorted(candidates,
                       key=lambda c: (-(c.times_it_misled - c.times_it_helped),
                                      c.last_revised_day, c.claim_id))[0]
        mine = objects_named(worst)
        rest = [c for c in here
                if c.claim_id != worst.claim_id and same_routine(c, worst)
                and (objects_named(c) & mine)]
        overlapping = [c for c in rest if words(c) & words(worst)]
        if not overlapping:
            break
        best = max(overlapping, key=lambda c: len(words(c) & words(worst)))
        # The kept claim ends up carrying both wordings. Without that, the code's fold
        # would quietly take content out of the reading window while the file still
        # held it, and a measure of what the robot could read would be wrong for a
        # reason no one could see in the notes.
        joined = best.statement if worst.statement in best.statement else (
            best.statement.rstrip(".") + ". Also: " + worst.statement)
        notes.fold_one_claim_into_another(
            best.claim_id, worst.claim_id, day, time, new_statement=joined,
            why="folded by the code, not by the model: the notes were over the line "
                "they were given, this claim had the worst record, and the two are "
                "claimed under the same routine")
        done.append({"kept": best.claim_id, "folded": worst.claim_id})
    return done


# ------------------------------------------------------------------ one night --

def write_the_notes_told_if_right(notes: Notes, household: FrozenHousehold, day: int,
                                  time: int, looks_today: Sequence[LookRecord],
                                  answers_today: Sequence[Any], client: LLMClient,
                                  max_edits: Optional[int] = None,
                                  tell_the_model_everything_it_saw: bool = True,
                                  name_the_objects_it_will_be_quizzed_on: bool = False,
                                  a_message_tonight: Optional[str] = None
                                  ) -> Dict[str, Any]:
    """One night of this arm: judge the day, then change the notes. Two model calls."""
    judgement = judge_the_day(notes, household, day, answers_today, client)
    report = change_the_notes(
        notes, household, day, time, looks_today, judgement, client,
        max_edits=max_edits,
        tell_the_model_everything_it_saw=tell_the_model_everything_it_saw,
        name_the_objects_it_will_be_quizzed_on=name_the_objects_it_will_be_quizzed_on,
        a_message_tonight=a_message_tonight)
    report["day"] = day
    report["how_it_judged_the_day"] = judgement
    report["n_questions_it_was_shown_the_result_of"] = len(answers_today)
    report["n_model_calls_tonight"] = 2
    return report
