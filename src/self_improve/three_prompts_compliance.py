"""Did each arm DO what its prompt asked? This runs before any outcome number.

An arm that was asked for something and did not do it is not an arm, and no accuracy
figure from it means anything. Three checks, one per variant, all computed from the
cell's own `notes.json` and `cell.json` with no model call:

  RIVAL BELIEFS   for every revision a claim ever had, reconstruct what it said before
                  and after, and classify:
                    added-and-set-aside   the standing went to "set aside for now" and
                                          the WORDING WAS NOT TOUCHED - the old belief
                                          is still readable. This is what variant 1
                                          asked for.
                    overwrote             the statement changed AND the (object, place)
                                          pairs it asserts changed, so the old belief is
                                          gone from the live claim.
                    reworded              the statement changed but asserts the same
                                          pairs: no information moved either way.
                    evidence or status    neither the wording nor the standing moved.
                  Reported per home. The control baseline from the old homes was 81
                  overwrites to 37 never-written with set-aside almost unused; the
                  comparison that matters is against THIS run's own control, paired
                  within home, because the homes differ.

  DESCRIBE THE PERSON   classify every line of the notes as naming an object-and-place,
                  mentioning a person, a time of day or a routine, or both. Two numbers
                  are reported and the TRADE between them is the point: how many lines
                  became routine lines, and how many distinct object-and-place facts the
                  notes carry and the 8-line read window shows. A variant that added
                  routine lines for free did not obey the budget; a variant that added
                  them at the cost of object facts did.

  THE MESSAGE     the nightly report of every night records what it was told, so the
                  set of nights that carried a message is read straight out of the run
                  and checked against the two intended nights. Checked in the runner
                  too, which refuses to write a cell that fails it; checked again here
                  from the written artifact, because the check that matters is the one
                  run on the file a reader will open.

THE MATCHER CAVEAT, which applies only to the object-and-place side. Deciding whether a
line of prose asserts "glass_ines is on kitchen_table_k1" cannot be done structurally;
we use `write_the_notes.facts_a_statement_asserts`, the matcher this project has
audited and repaired. Its failure mode is to MISS an assertion worded unusually, which
inflates "routine line that names no object and place". So that count is an UPPER bound
and the object-fact counts are LOWER bounds, and a verdict should only be believed if
it is not close.

    python -m self_improve.three_prompts_compliance
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

from self_improve.frozen_household import FrozenHousehold
from self_improve.memory_notes import (SET_ASIDE, STILL_STANDING, Claim, Notes,
                                      summary_lines)
from self_improve.never_written_or_displaced import the_notes_as_they_stood
from self_improve.study_settings import LOCKED
from self_improve.three_prompts import ARMS, CONTROL, PILOT_BANKS, PILOT_TEN
from self_improve.write_the_notes import (facts_a_statement_asserts,
                                         ways_an_object_may_be_written,
                                         where_an_object_is_named)

ADDED_AND_SET_ASIDE = "added and set aside: the old wording is still readable"
OVERWROTE = "overwrote: the old belief is gone from the live claim"
SET_ASIDE_BUT_OVERWRITTEN = ("set aside AND the wording replaced: looks compliant, "
                             "the old belief is gone")
REWORDED = "reworded: the same facts in different words"
NOTHING_MOVED = "evidence or status only: no belief changed"
KINDS = (ADDED_AND_SET_ASIDE, SET_ASIDE_BUT_OVERWRITTEN, OVERWROTE, REWORDED,
         NOTHING_MOVED)

# WHY THE THIRD CATEGORY EXISTS. On the varied_v2 homes the control marks almost every
# claim "set aside for now" while SIMULTANEOUSLY replacing its wording in the same edit.
# The audit trail then claims a non-destructive edit while the readable memory has lost
# the old belief - which is worse than an honest overwrite, because it looks compliant to
# anything that counts standings. So it is counted separately: a set-aside that keeps the
# old statement readable is not the same event as one that does not, and only the first is
# what variant 1 asked for.

# ---- the word lists for the describe-the-person check. Deliberately plain and
# deliberately listed here rather than inferred, so a reader can see exactly what
# counts. Matched on whole words in the lower-cased line.
TIME_OF_DAY_WORDS = (
    "morning", "mornings", "midday", "noon", "afternoon", "afternoons", "evening",
    "evenings", "night", "nights", "overnight", "bedtime", "breakfast", "lunch",
    "lunchtime", "supper", "dinner", "dinnertime", "daytime", "am", "pm",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "weekday", "weekdays", "weekend", "weekends",
)
ROUTINE_WORDS = (
    "routine", "routines", "habit", "habits", "usually", "usual", "normally",
    "typically", "ordinarily", "generally", "pattern", "patterns", "regime",
    "daily", "every day", "each day", "most days", "schedule", "regularly",
    "changed", "change", "changes", "no longer", "since", "lately", "recently",
    "at home", "stays home", "staying home", "staying at home", "out of the house",
    "away", "out", "working", "works", "sleeping", "sleeps", "resting", "rests",
    "unwell", "ill", "illness", "sick", "recovering", "better", "confined",
)
PERSON_WORDS = ("resident", "residents", "person", "people", "household", "occupant",
                "occupants", "they", "their", "someone", "anyone", "both of them")


def claims_that_are_shown(notes: Notes) -> List[Claim]:
    """The claims that can actually reach a prompt.

    A claim with `folded_into` set is NOT shown at answer time. That field arrived in
    shared code on 2026-09-24 for a third memory format; no arm in this directory can
    produce one, so this changes nothing here today. It is read with `getattr` so the same
    analysis runs against notes written before the field existed, and it is in one place so
    a future arm that does produce them cannot be silently miscounted by four separate
    line-counting loops.
    """
    return [c for c in notes.claims if not getattr(c, "folded_into", None)]


def _whole_word(text: str, needle: str) -> bool:
    return re.search(r"(?<![a-z0-9_])" + re.escape(needle) + r"(?![a-z0-9_])",
                     text) is not None


def people_words_for(household: FrozenHousehold) -> Tuple[str, ...]:
    """The tokens that name a person in THIS home: the resident ids the look records
    use, plus the owner's name from every asked-about object id (`glass_ines` -> ines).

    THE NAME ALONE IS NOT ENOUGH, and getting this wrong made the first reading of this
    measure useless. Object ids are `<class>_<owner>`, so "glass_ines is on the sink"
    contains the token "ines" and every single object line scored as mentioning a
    person - the control and the variant alike came out at 10 lines of 10. So
    `classify_a_line` masks every form of every object id OUT of the line before it
    looks for a person, and a name only counts when it is used away from the thing it
    owns: "ines is at home all day", not "ines glass".
    """
    words = set(PERSON_WORDS) | {r.lower() for r in household.resident_ids}
    for object_id in household.asked_objects:
        parts = object_id.split("_")
        if len(parts) >= 2:
            words.add(parts[-1].lower())
    return tuple(sorted(words))


def _with_the_objects_masked(line: str, household: FrozenHousehold) -> str:
    """The line with every form of every asked-about object id blanked out, so the
    owner's name inside an object id cannot be read as a mention of the person."""
    text = (line or "").lower()
    for object_id in household.asked_objects:
        for form in ways_an_object_may_be_written(object_id):
            if form:
                text = re.sub(r"(?<![a-z0-9_])" + re.escape(form) + r"(?![a-z0-9_])",
                              " ", text)
    return text


def classify_a_line(line: str, household: FrozenHousehold,
                    people: Sequence[str]) -> Dict[str, bool]:
    """What kind of thing one line of notes is. Not mutually exclusive by design: a
    line can name an object's spot AND say when it holds it, and that is the line the
    default prompt already nudges toward."""
    text = (line or "").lower()
    flat = text.replace("_", " ")
    pairs = facts_a_statement_asserts(line, household.asked_objects, household.places,
                                      household.place_room)
    masked = _with_the_objects_masked(line, household)
    masked_flat = masked.replace("_", " ")
    person = any(_whole_word(masked, w) or _whole_word(masked_flat, w) for w in people)
    when = any(_whole_word(masked_flat, w) for w in TIME_OF_DAY_WORDS) or \
        re.search(r"\b\d{1,2}:\d{2}\b", masked) is not None
    routine = any((_whole_word(masked_flat, w) if " " not in w else w in masked_flat)
                  for w in ROUTINE_WORDS)
    return {
        "names_an_object_and_place": bool(pairs),
        "mentions_a_person": person,
        "mentions_a_time_of_day": when,
        "mentions_a_routine": routine,
        "is_about_the_people_or_the_routine": person or when or routine,
        # the strict version: it talks about people or routine and does NOT pin an
        # object to a spot, so it is a line the object-and-place notes did not have
        "a_routine_line_that_names_no_object_and_place":
            (person or when or routine) and not pairs,
    }


def what_the_revisions_did(notes: Notes, household: FrozenHousehold,
                           up_to_day: Optional[int] = None) -> Dict[str, Any]:
    """Every revision any claim ever had, classified. See the module docstring.

    `up_to_day` counts only what had happened by that night. Without it, two arms read at
    different nights are not comparable at all: revisions accumulate, so an arm that has
    run one night longer has more of everything. Any cross-arm table must pass the same
    `up_to_day` to every arm - the "never compare two things computed on different units"
    rule, applied to time.

    It is implemented by reconstructing the notes at that night with
    `the_notes_as_they_stood`, which already drops claims first written later and trims
    each claim's revision history, rather than by filtering inside the three loops below:
    one reconstruction cannot disagree with itself, three separate filters can.
    """
    if up_to_day is not None:
        counted = what_the_revisions_did(the_notes_as_they_stood(notes, up_to_day),
                                         household)
        counted["counted_up_to_day"] = up_to_day
        return counted
    counts: collections.Counter = collections.Counter()
    per_night: Dict[int, collections.Counter] = collections.defaultdict(
        collections.Counter)
    examples: Dict[str, List[str]] = collections.defaultdict(list)
    for claim in notes.claims:
        history = sorted(claim.revision_history, key=lambda r: (r["day"], r["time"]))
        for i, revision in enumerate(history):
            was = revision.get("was") or {}
            after = (history[i + 1]["was"] if i + 1 < len(history)
                     else {"statement": claim.statement, "holds_under": claim.holds_under,
                           "status": claim.status, "standing": claim.standing})
            before_statement = was.get("statement", "")
            after_statement = after.get("statement", "")
            before_standing = was.get("standing", STILL_STANDING)
            after_standing = after.get("standing", STILL_STANDING)
            wording_untouched = before_statement.strip() == after_statement.strip()
            went_aside = (before_standing != SET_ASIDE and after_standing == SET_ASIDE)
            if went_aside and wording_untouched:
                kind = ADDED_AND_SET_ASIDE
            elif went_aside and not wording_untouched:
                kind = SET_ASIDE_BUT_OVERWRITTEN
            elif not wording_untouched:
                before_pairs = facts_a_statement_asserts(
                    before_statement, household.asked_objects, household.places,
                    household.place_room)
                after_pairs = facts_a_statement_asserts(
                    after_statement, household.asked_objects, household.places,
                    household.place_room)
                kind = OVERWROTE if before_pairs != after_pairs else REWORDED
            else:
                kind = NOTHING_MOVED
            counts[kind] += 1
            per_night[revision["day"]][kind] += 1
            if len(examples[kind]) < 3:
                examples[kind].append(
                    f"day {revision['day']} {claim.claim_id}: "
                    f"{before_statement[:70]!r} -> {after_statement[:70]!r} "
                    f"(standing {before_standing} -> {after_standing})")

    # Variant 1 asked for TWO things in the same set of edits: a new claim for where
    # the thing is now, AND the old claim set aside with its wording untouched. A
    # set-aside with no accompanying add is half-compliance: the old belief survives
    # but the new one was never written, which is worse than an overwrite. So the
    # pairing is counted, not assumed.
    added_on: Dict[int, set] = collections.defaultdict(set)
    for claim in notes.claims:
        added_on[claim.first_written_day] |= facts_a_statement_asserts(
            claim.statement, household.asked_objects, household.places,
            household.place_room)
    paired = 0
    for claim in notes.claims:
        history = sorted(claim.revision_history, key=lambda r: (r["day"], r["time"]))
        for i, revision in enumerate(history):
            was = revision.get("was") or {}
            after = (history[i + 1]["was"] if i + 1 < len(history)
                     else {"statement": claim.statement, "standing": claim.standing})
            if was.get("standing", STILL_STANDING) == SET_ASIDE or \
                    after.get("standing", STILL_STANDING) != SET_ASIDE:
                continue
            if was.get("statement", "").strip() != after.get("statement", "").strip():
                continue
            objects_here = {o for o, _p in facts_a_statement_asserts(
                claim.statement, household.asked_objects, household.places,
                household.place_room)}
            if objects_here & {o for o, _p in added_on.get(revision["day"], set())}:
                paired += 1

    # Both kinds of overwrite lose the old belief from the readable claim, so both go in
    # the denominator; only a set-aside that KEPT the wording goes in the numerator.
    n_decisive = (counts[ADDED_AND_SET_ASIDE] + counts[OVERWROTE]
                  + counts[SET_ASIDE_BUT_OVERWRITTEN])
    return {
        "n_set_aside_with_a_new_claim_for_the_same_object_the_same_night": paired,
        "n_claims": len(notes.claims),
        "n_revisions": sum(counts.values()),
        "counts": {k: counts[k] for k in KINDS},
        "n_added_and_set_aside": counts[ADDED_AND_SET_ASIDE],
        "n_overwrote": counts[OVERWROTE],
        "n_set_aside_but_the_wording_was_replaced": counts[SET_ASIDE_BUT_OVERWRITTEN],
        "n_that_look_compliant_but_lost_the_old_belief": counts[SET_ASIDE_BUT_OVERWRITTEN],
        "share_of_belief_changes_that_kept_the_old_one":
            (counts[ADDED_AND_SET_ASIDE] / n_decisive) if n_decisive else None,
        "n_belief_changes": n_decisive,
        "n_claims_set_aside_and_still_readable":
            sum(1 for c in notes.claims if c.standing == SET_ASIDE),
        "examples": dict(examples),
        "per_night": {str(d): dict(c) for d, c in sorted(per_night.items())},
    }


def what_the_lines_say(notes: Notes, household: FrozenHousehold, day: int
                       ) -> Dict[str, Any]:
    """The notes as they stood at the end of `day`, line by line, plus what the 8-line
    read window actually shows - because the budget binds at READ time."""
    people = people_words_for(household)
    stood = the_notes_as_they_stood(notes, day)
    # THE WHOLESALE FORMAT HAS NO CLAIMS. Reading `stood.claims` for it returned an empty
    # list, so every line measure would have been silently zero for that arm - a whole
    # arm's compliance reading reported as "it wrote nothing about anyone", which is
    # exactly the kind of clean-looking wrong number this project keeps producing.
    if notes.how_memory_is_written == "wholesale rewrite":
        lines = summary_lines(stood.newest_summary() or "")
    else:
        lines = [c.statement for c in claims_that_are_shown(stood)]
    verdicts = [classify_a_line(line, household, people) for line in lines]
    pairs_in_the_notes: set = set()
    for line in lines:
        pairs_in_the_notes |= facts_a_statement_asserts(
            line, household.asked_objects, household.places, household.place_room)

    # what the read window shows, averaged over the objects the robot is asked about -
    # the same window the answer step gets, one object at a time
    in_window_pairs: List[int] = []
    in_window_routine: List[int] = []
    for object_id in household.asked_objects:
        window = stood.what_the_robot_can_read(
            LOCKED.read_budget_lines, about_object=object_id).text.splitlines()
        pairs: set = set()
        routine = 0
        for line in window:
            pairs |= facts_a_statement_asserts(line, household.asked_objects,
                                               household.places, household.place_room)
            if classify_a_line(line, household, people)[
                    "a_routine_line_that_names_no_object_and_place"]:
                routine += 1
        in_window_pairs.append(len(pairs))
        in_window_routine.append(routine)

    n = len(lines)
    return {
        "day": day,
        "n_lines": n,
        "n_lines_that_name_an_object_and_place":
            sum(1 for v in verdicts if v["names_an_object_and_place"]),
        "n_lines_about_the_people_or_the_routine":
            sum(1 for v in verdicts if v["is_about_the_people_or_the_routine"]),
        "n_routine_lines_that_name_no_object_and_place":
            sum(1 for v in verdicts if v["a_routine_line_that_names_no_object_and_place"]),
        "n_lines_mentioning_a_person": sum(1 for v in verdicts if v["mentions_a_person"]),
        "n_lines_mentioning_a_time_of_day":
            sum(1 for v in verdicts if v["mentions_a_time_of_day"]),
        "n_lines_mentioning_a_routine": sum(1 for v in verdicts if v["mentions_a_routine"]),
        "share_of_lines_about_the_people_or_the_routine":
            (sum(1 for v in verdicts if v["is_about_the_people_or_the_routine"]) / n)
            if n else None,
        "n_distinct_object_and_place_facts_in_the_whole_notes": len(pairs_in_the_notes),
        "mean_object_and_place_facts_inside_the_8_line_read_window":
            statistics.mean(in_window_pairs) if in_window_pairs else None,
        "mean_routine_lines_inside_the_8_line_read_window":
            statistics.mean(in_window_routine) if in_window_routine else None,
        "n_characters_of_notes": sum(len(line) for line in lines),
    }


def coverage_and_duplication(notes: Notes, household: FrozenHousehold,
                             day: int) -> Dict[str, Any]:
    """How many asked-about objects have a live claim, and how many have MORE than one.

    WHY BOTH ARE NEEDED NOW. Under the nightly edit allowance the claim store writes about
    the whole house on its first night - measured: 58 claims for 47 objects seen - where the
    old eight-edit cap took four nights to reach one claim per object. That removes a
    coverage ramp from the settled period, which is better (a change at day 14 is then a
    change in the ROUTINE rather than a mixture of learning the house and learning the
    routine), but it moves what two measures mean:

      COVERAGE at day 13. If it is near 100% in every arm, reachability cannot discriminate
      between arms in the settled period at all, and only the disrupted window can. Any
      reachability comparison from an earlier wave is then not like-for-like with this one.

      DUPLICATION at day 13. A second live claim about an object is only evidence of keeping
      a rival belief if the first night did not already produce two. 58 claims for 47 objects
      means duplication existed before any routine had changed, so the rival-beliefs reading
      has to be a CHANGE in duplication between day 13 and day 23, not its level at 23.

    Live means not folded into another claim. Matched with the audited matcher, whose failure
    mode is to miss an unusual wording, so coverage is a lower bound.
    """
    stood = the_notes_as_they_stood(notes, day)
    if notes.how_memory_is_written == "wholesale rewrite":
        lines = summary_lines(stood.newest_summary() or "")
        per_object = {o: sum(1 for line in lines
                             if where_an_object_is_named(line.lower(), o) >= 0)
                      for o in household.asked_objects}
    else:
        live = claims_that_are_shown(stood)
        per_object = {o: sum(1 for c in live
                             if where_an_object_is_named(c.statement.lower(), o) >= 0)
                      for o in household.asked_objects}
    n = len(household.asked_objects)
    covered = [o for o, k in per_object.items() if k >= 1]
    duplicated = [o for o, k in per_object.items() if k >= 2]
    return {
        "day": day,
        "n_asked_objects": n,
        "n_with_a_live_claim": len(covered),
        "share_covered": len(covered) / n if n else None,
        "n_with_more_than_one_live_claim": len(duplicated),
        "share_with_more_than_one": len(duplicated) / n if n else None,
        "mean_live_claims_per_asked_object":
            (sum(per_object.values()) / n) if n else None,
        "most_live_claims_on_one_object": max(per_object.values()) if per_object else 0,
        "n_live_lines_in_total": (len(lines)
                                 if notes.how_memory_is_written == "wholesale rewrite"
                                 else len(claims_that_are_shown(stood))),
    }


def the_growth_curve(notes: Notes, household: FrozenHousehold,
                     last_day: int = 31) -> Dict[str, Any]:
    """Live lines and characters at the end of every night, for the growth figure.

    Oliver asked how growth should be bounded and the honest answer came from this project's
    own data; the survey of eight published memory systems found that none of them reports
    this curve for its own method. So it is worth a plot rather than a sentence.
    """
    out: Dict[str, Any] = {}
    for day in range(0, last_day + 1):
        stood = the_notes_as_they_stood(notes, day)
        if notes.how_memory_is_written == "wholesale rewrite":
            lines = summary_lines(stood.newest_summary() or "")
        else:
            lines = [c.statement for c in claims_that_are_shown(stood)]
        out[str(day)] = {"n_lines": len(lines),
                         "n_characters": sum(len(x) for x in lines)}
    return out


# What disqualifies a `holds_under` value from being a condition. Added 2026-09-25 after the
# coordinator found that the 99% "current" figure was measuring the DISPLAY and not the model:
# each existing note was shown as one run-together line, `[claim_0001] statement (holds under:
# X; provisional; 6 sighting(s) for, 0 against; last revised on day 2)`, and the model copied
# the whole string back into the field. Real values from that period include
# `"Day 1-2, 09:00-16:00; provisional; 12 sighting(s) for, 0 against; last revised on day 2"`.
#
# So a condition has to be rejected for three separate reasons, not one, and they are counted
# separately because they say different things about what went wrong:
#   nothing        empty, "current", "not said", or a standing value in the wrong field
#   the rendering  it echoes our own display back at us - our bug, not the model's
#   only a date    a date, a clock time or an observation id and nothing else: true of the
#                  note's provenance, but it is not a CONDITION under which the note holds
THE_RENDERING = ("sighting(s)", "last revised on day", "provisional;", "established;",
                 "holds under:", "claim_0")
SAYS_NOTHING = ("", "current", "not said", "unknown", "n/a", "none", "unspecified",
                "always", "any time", "ongoing")
ONLY_A_DATE = re.compile(
    r"^[\s,;.\-]*(?:(?:day|days)\s*\d+(?:\s*[-\u2013to]+\s*\d+)?|\d{1,2}:\d{2}"
    r"(?:\s*[-\u2013to]+\s*\d{1,2}:\d{2})?|sighting_\d+|observation_\d+"
    r"|[\s,;.\-]+)+$", re.I)


def why_a_condition_is_not_one(holds_under: str) -> Optional[str]:
    """None if it really names a condition, otherwise which of the three reasons it does not."""
    text = (holds_under or "").strip()
    low = text.lower()
    if low in SAYS_NOTHING or low in (SET_ASIDE.lower(), STILL_STANDING.lower()):
        return "says nothing"
    if any(bit in low for bit in THE_RENDERING):
        return "echoes our own rendering"
    if ONLY_A_DATE.match(text):
        return "only a date, a time or an observation id"
    return None


def what_the_conditions_say(notes: Notes) -> Dict[str, Any]:
    """What the model puts in `holds_under`, the field that records WHICH ROUTINE a claim
    is claimed for.

    WHY THIS IS A COMPLIANCE MEASURE AND NOT A CURIOSITY. `holds_under` is the only thing
    in a claim that can distinguish an ordinary-routine belief from a disrupted-routine
    belief. The whole rationale for keeping rival beliefs is the prompt's own sentence:
    "A claim about one routine does not have to be undone to write a claim about another."
    If both rivals carry the same condition, the reader is handed two contradictory claims
    with nothing to choose between them, and keeping the loser cannot help.

    Measured 2026-09-24 over 270 claims in the claim-store arms past night 15: **96.3% say
    exactly "current"** and the other 3.7% say "set aside for now", which is a STANDING
    value in the wrong field. Not one claim named a routine or a condition. So this is
    reported for every arm, and a rival-beliefs result has to be read next to it.
    """
    values = collections.Counter(c.holds_under.strip().lower() for c in notes.claims)
    n = sum(values.values())
    why = collections.Counter()
    real = []
    for c in notes.claims:
        reason = why_a_condition_is_not_one(c.holds_under)
        if reason is None:
            real.append(c.holds_under.strip())
        else:
            why[reason] += 1
    # a condition that actually says something about when it holds, rather than "current"
    # or a standing value put in the wrong field
    vacuous = {"current", "not said", "", "unknown", "n/a", "none",
               SET_ASIDE.lower(), STILL_STANDING.lower()}
    informative = sum(k for v, k in values.items() if v not in vacuous)
    return {
        "n_claims": n,
        "n_that_name_a_real_condition": len(real),
        "share_that_name_a_real_condition": (len(real) / n) if n else None,
        "why_the_rest_do_not": dict(why),
        "examples_of_real_conditions": sorted({r for r in real})[:6],
        "n_distinct_real_conditions": len({r.lower() for r in real}),
        "the_baseline_this_replaces": (
            "the 99% 'current' figure from every earlier arm was measuring our own DISPLAY, "
            "not the model: notes were shown as one run-together line and the model copied it "
            "back into the field. Any earlier reading of this field is void, in every arm."),
        "n_distinct_conditions": len(values),
        "n_claims_whose_condition_says_nothing": n - informative,
        "n_claims_whose_condition_names_a_routine": informative,
        "share_whose_condition_names_a_routine": (informative / n) if n else None,
        "commonest": values.most_common(5),
    }


def the_message_nights(cell: Dict[str, Any]) -> Dict[str, Any]:
    """Which nights carried a message, read out of the run's own nightly reports."""
    carried = {int(night["day"]): night.get("the_message_it_was_told_tonight")
               for night in cell.get("nightly", [])
               if night.get("the_message_it_was_told_tonight")}
    said_nothing = [int(night["day"]) for night in cell.get("nightly", [])
                    if not night.get("the_message_it_was_told_tonight")]
    return {"nights_that_carried_a_message": sorted(carried),
            "n_nights_with_no_message": len(said_nothing),
            "the_messages": {str(d): m for d, m in sorted(carried.items())}}


def one_cell(cell_dir: pathlib.Path, household: FrozenHousehold,
             days: Sequence[int] = (13, 23, 31)) -> Optional[Dict[str, Any]]:
    cell_file, notes_file, arm_file = (cell_dir / "cell.json", cell_dir / "notes.json",
                                       cell_dir / "arm.json")
    if not (cell_file.exists() and notes_file.exists() and arm_file.exists()):
        return None
    cell = json.loads(cell_file.read_text())
    arm = json.loads(arm_file.read_text())
    notes = Notes.load(notes_file)
    row: Dict[str, Any] = {
        "arm": arm["arm"], "household": household.name, "where": str(cell_dir),
        "nights_the_writer_ran": arm["n_nights_the_writer_ran"],
        "asked_for": {k: arm[k] for k in ("keep_rival_beliefs", "describe_the_person",
                                          "tell_it_the_resident_is_unwell")},
        # counted over the whole month AND at a fixed night, so a cross-arm table can use
        # the day-23 figures and be comparing the same number of nights in every arm
        "rival_beliefs": what_the_revisions_did(notes, household),
        "rival_beliefs_to_day_23": what_the_revisions_did(notes, household, 23),
        "the_conditions": what_the_conditions_say(notes),
        "coverage": {str(d): coverage_and_duplication(notes, household, d)
                     for d in (13, 23, 31)},
        "growth": the_growth_curve(notes, household),
        "the_lines": {str(d): what_the_lines_say(notes, household, d) for d in days},
        "the_message": the_message_nights(cell),
    }
    wanted = ([arm["first_disrupted_day"], arm["first_day_back"]]
              if arm["tell_it_the_resident_is_unwell"] else [])
    row["the_message"]["wanted"] = wanted
    row["the_message"]["exactly_the_intended_nights"] = \
        row["the_message"]["nights_that_carried_a_message"] == wanted
    return row


def paired_difference(rows: Sequence[Dict[str, Any]], control_rows: Sequence[Dict[str, Any]],
                      pick) -> Optional[Dict[str, Any]]:
    """The within-home difference against the control, clustered on HOME.

    Paired on the household, never pooled over claims or questions: the unit of
    analysis is the home because the homes differ in size, in how many objects move and
    in how many revisions there are to make.
    """
    control_by_home = {r["household"]: r for r in control_rows}
    pairs: List[Tuple[str, float, float]] = []
    for row in rows:
        other = control_by_home.get(row["household"])
        if other is None:
            continue
        mine, theirs = pick(row), pick(other)
        if mine is None or theirs is None:
            continue
        pairs.append((row["household"], float(mine), float(theirs)))
    if len(pairs) < 2:
        return {"n_homes": len(pairs), "too_few_homes_to_pair": True,
                "per_home": [{"household": h, "arm": a, "control": c} for h, a, c in pairs]}
    deltas = [a - c for _h, a, c in pairs]
    mean = statistics.mean(deltas)
    se = statistics.stdev(deltas) / (len(deltas) ** 0.5)
    return {
        "n_homes": len(pairs),
        "arm_mean": statistics.mean(a for _h, a, _c in pairs),
        "control_mean": statistics.mean(c for _h, _a, c in pairs),
        "mean_difference": mean,
        "standard_error": se,
        "two_standard_errors": 2 * se,
        "beyond_two_standard_errors": abs(mean) > 2 * se,
        "n_homes_the_arm_is_higher": sum(1 for d in deltas if d > 0),
        "n_homes_the_arm_is_lower": sum(1 for d in deltas if d < 0),
        "n_homes_tied": sum(1 for d in deltas if d == 0),
        "verdict": ("the arm is higher" if mean > 0 and abs(mean) > 2 * se else
                    "the control is higher" if mean < 0 and abs(mean) > 2 * se else
                    f"no difference beyond 2 se; this excludes a difference larger "
                    f"than {2 * se:.3g} in either direction"),
        "per_home": [{"household": h, "arm": a, "control": c, "difference": a - c}
                     for h, a, c in pairs],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/three_prompts"))
    parser.add_argument("--banks", type=pathlib.Path, default=PILOT_BANKS)
    parser.add_argument("--out", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    households: Dict[str, FrozenHousehold] = {}
    rows: List[Dict[str, Any]] = []
    for arm in sorted(ARMS):
        for name in PILOT_TEN:
            cell_dir = args.root / "cells" / arm / name
            if name not in households:
                path = args.banks / f"{name}.jsonl"
                if not path.exists():
                    continue
                households[name] = FrozenHousehold(path)
            got = one_cell(cell_dir, households[name])
            if got:
                rows.append(got)
    if not rows:
        print(f"no finished cells under {args.root}/cells yet")
        return 0

    by_arm: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        by_arm[row["arm"]].append(row)
    control = by_arm.get(CONTROL, [])

    print(f"\n{'='*78}\nCOMPLIANCE, before any outcome. "
          f"{len(rows)} cells, {len({r['household'] for r in rows})} homes.\n{'='*78}")

    print("\n--- 1. RIVAL BELIEFS: what every revision actually did (whole month)\n")
    print(f"{'arm':22s} {'homes':>5s} {'claims':>7s} {'revis':>6s} {'KEPT old':>9s} "
          f"{'set-aside BUT':>14s} {'overwrote':>10s} {'reworded':>9s} "
          f"{'kept share':>11s} {'+ADD same nt':>13s}")
    print(f"{'':22s} {'':5s} {'':7s} {'':6s} {'wording kept':>9s} "
          f"{'wording gone':>14s} {'honestly':>10s}")
    for arm in sorted(by_arm):
        here = by_arm[arm]
        kept = sum(r["rival_beliefs"]["n_added_and_set_aside"] for r in here)
        fake = sum(r["rival_beliefs"]["n_set_aside_but_the_wording_was_replaced"]
                   for r in here)
        over = sum(r["rival_beliefs"]["n_overwrote"] for r in here)
        word = sum(r["rival_beliefs"]["counts"][REWORDED] for r in here)
        claims = sum(r["rival_beliefs"]["n_claims"] for r in here)
        revs = sum(r["rival_beliefs"]["n_revisions"] for r in here)
        paired = sum(r["rival_beliefs"][
            "n_set_aside_with_a_new_claim_for_the_same_object_the_same_night"]
            for r in here)
        share = kept / (kept + over + fake) if (kept + over + fake) else None
        print(f"{arm:22s} {len(here):5d} {claims:7d} {revs:6d} {kept:9d} {fake:14d} "
              f"{over:10d} {word:9d} "
              f"{('%.1f%%' % (100*share)) if share is not None else 'n/a':>11s} "
              f"{paired:13d}")
    print()
    print("  'set-aside BUT wording gone' is the deceptive case: the standing says the "
          "claim was\n  set aside while the readable text has been replaced, so an audit "
          "that counts standings\n  reads as compliant while the old belief is gone. It "
          "is counted with the overwrites in\n  the denominator of 'kept share', never "
          "with the real set-asides.")
    print("  '+ADD same nt' counts set-asides where a NEW claim about the same object was "
          "added\n  the same night - which is the whole of what variant 1 asked for. A "
          "set-aside with no\n  add is half-compliance: the old belief survives and the "
          "new one was never written.")
    print("\n  per home, share of belief changes that KEPT the old claim readable:")
    for arm in sorted(by_arm):
        if arm == CONTROL:
            continue
        got = paired_difference(
            by_arm[arm], control,
            lambda r: r["rival_beliefs"]["share_of_belief_changes_that_kept_the_old_one"])
        if got and not got.get("too_few_homes_to_pair"):
            print(f"    {arm:22s} arm {got['arm_mean']:6.1%} control "
                  f"{got['control_mean']:6.1%}  diff {got['mean_difference']:+.1%} "
                  f"+- {got['two_standard_errors']:.1%} (2 se, n={got['n_homes']} homes) "
                  f"-> {got['verdict']}")

    print("\n--- 2. DESCRIBE THE PERSON: what the lines are, and the trade "
          "(notes at the end of day 23)\n")
    print(f"{'arm':22s} {'lines':>6s} {'obj+place':>10s} {'routine':>8s} "
          f"{'routine only':>13s} {'facts':>6s} {'facts in 8':>11s} {'routine in 8':>13s}")
    for arm in sorted(by_arm):
        here = [r["the_lines"]["23"] for r in by_arm[arm]]
        if not here:
            continue
        m = lambda k: statistics.mean(x[k] for x in here if x[k] is not None)
        print(f"{arm:22s} {m('n_lines'):6.1f} "
              f"{m('n_lines_that_name_an_object_and_place'):10.1f} "
              f"{m('n_lines_about_the_people_or_the_routine'):8.1f} "
              f"{m('n_routine_lines_that_name_no_object_and_place'):13.1f} "
              f"{m('n_distinct_object_and_place_facts_in_the_whole_notes'):6.1f} "
              f"{m('mean_object_and_place_facts_inside_the_8_line_read_window'):11.2f} "
              f"{m('mean_routine_lines_inside_the_8_line_read_window'):13.2f}")
    print("\n  paired within home against the control, day 23:")
    for arm in sorted(by_arm):
        if arm == CONTROL:
            continue
        for label, key in (
                ("routine lines that name no object+place",
                 "n_routine_lines_that_name_no_object_and_place"),
                ("object+place facts in the whole notes",
                 "n_distinct_object_and_place_facts_in_the_whole_notes"),
                ("object+place facts inside the 8-line window",
                 "mean_object_and_place_facts_inside_the_8_line_read_window")):
            got = paired_difference(by_arm[arm], control,
                                   lambda r, k=key: r["the_lines"]["23"][k])
            if got and not got.get("too_few_homes_to_pair"):
                print(f"    {arm:22s} {label:44s} {got['mean_difference']:+7.2f} "
                      f"+- {got['two_standard_errors']:.2f}  -> {got['verdict']}")

    print("\n--- 1a. WHAT THE TWO PROMPTS BEING COMPARED ACTUALLY DIFFER BY\n")
    print("  `the log and notes about the routine` against `incremental edits` is the")
    print("  comparison the paper turns on, so what separates their prompts is part of the")
    print("  result and not a footnote. As of 2026-09-25 they differ by EXACTLY ONE")
    print("  PARAGRAPH - the one telling the record-reading arm that everything it has ever")
    print("  seen is kept for it and shown on request, so copying the record into a note")
    print("  adds nothing. Verified by diffing the two method blocks: one paragraph added,")
    print("  none removed, and the 2,278-character shared part byte-identical across all")
    print("  five methods.")
    print()
    print("  It was not so a few hours ago, and both differences were in the direction that")
    print("  would have flattered this arm or handicapped it rather than left it alone:")
    print("    * its block carried four extra pieces of advice about HOW TO THINK that its")
    print("      control never saw. Those are now in the shared part and every arm gets them.")
    print("    * its day description LEFT OUT what each look did not find, costing it about")
    print("      15% of the characters and evidence its control was given. Absence is")
    print("      evidence; it now sees exactly what its control sees.")
    print("  Any earlier number comparing these two arms is not a comparison of the method.")

    print("\n--- 1b. COVERAGE AND DUPLICATION. Under the nightly allowance the store")
    print("    describes the whole house on night 1, so the settled period no longer has a")
    print("    coverage ramp. Two consequences are measured here.\n")
    print(f"  {'arm':22s} {'day':>4s} {'covered':>8s} {'>1 claim':>9s} "
          f"{'claims/object':>13s} {'most on one':>11s} {'live lines':>10s}")
    for arm in sorted(by_arm):
        for day in ("13", "23"):
            here = [r["coverage"][day] for r in by_arm[arm] if day in r.get("coverage", {})]
            if not here:
                continue
            m = lambda k: statistics.mean(x[k] for x in here if x[k] is not None)
            print(f"  {arm:22s} {day:>4s} {m('share_covered'):7.1%} "
                  f"{m('share_with_more_than_one'):8.1%} "
                  f"{m('mean_live_claims_per_asked_object'):13.2f} "
                  f"{m('most_live_claims_on_one_object'):11.1f} "
                  f"{m('n_live_lines_in_total'):10.1f}")
    print("\n  If coverage at day 13 is near 100% in every arm, reachability cannot")
    print("  discriminate between arms in the settled period and only the disrupted window")
    print("  can - and no reachability figure from an earlier wave is like-for-like.")
    print("  A second claim about an object is evidence of keeping a rival belief only as a")
    print("  CHANGE from day 13 to day 23, never as its level at day 23.")
    for arm in sorted(by_arm):
        if arm == CONTROL:
            continue
        got = paired_difference(
            by_arm[arm], control,
            lambda r: (r["coverage"]["23"]["share_with_more_than_one"]
                       - r["coverage"]["13"]["share_with_more_than_one"]))
        if got and not got.get("too_few_homes_to_pair"):
            print(f"    {arm:22s} change in duplication, day 13 -> 23, against the "
                  f"control: {got['mean_difference']:+.1%} +- "
                  f"{got['two_standard_errors']:.1%} -> {got['verdict']}")

    print("\n--- 2a. DOES THE CONDITION FIELD HOLD A CONDITION? Baseline: zero, every arm.\n")
    print("  The 99% 'current' figure from every earlier arm was measuring our own display,")
    print("  not the model - notes were shown as one run-together line and the model copied it")
    print("  back into the field. Any earlier reading of this field is void in EVERY arm, so")
    print("  this wave is the first in which it means anything. It matters most for the")
    print("  rival-beliefs question, which is asked entirely of this field.\n")
    print(f"  {'arm':22s} {'cells':>5s} {'notes':>6s} {'a real condition':>16s} "
          f"{'nothing':>8s} {'rendering':>10s} {'date only':>10s} {'distinct':>8s}")
    for arm in sorted(by_arm):
        here = [r["the_conditions"] for r in by_arm[arm] if r["the_conditions"]["n_claims"]]
        if not here:
            continue
        notes_n = sum(x["n_claims"] for x in here)
        real = sum(x["n_that_name_a_real_condition"] for x in here)
        why = collections.Counter()
        for x in here:
            why.update(x.get("why_the_rest_do_not") or {})
        distinct = len({e.lower() for x in here for e in x.get("examples_of_real_conditions", [])})
        print(f"  {arm:22s} {len(here):5d} {notes_n:6d} {real/notes_n if notes_n else 0:15.1%} "
              f"{why['says nothing']:8d} {why['echoes our own rendering']:10d} "
              f"{why['only a date, a time or an observation id']:10d} {distinct:8d}")
    print("\n  'distinct' counts how many DIFFERENT real conditions were written, because one")
    print("  condition repeated on every note is 'current' with more words. Examples per arm:")
    for arm in sorted(by_arm):
        ex = sorted({e for r in by_arm[arm] for e in
                     r["the_conditions"].get("examples_of_real_conditions", [])})[:4]
        if ex:
            print(f"    {arm:22s} {'; '.join(e[:44] for e in ex)}")

    print("\n--- 2b. THE CONDITION FIELD: can two kept rivals even be told apart?\n")
    print("  `holds_under` records WHICH ROUTINE a claim is claimed for. It is the only")
    print("  thing that can distinguish an ordinary-routine belief from a disrupted one, so")
    print("  a rival-beliefs result has to be read next to this.\n")
    print(f"  {'arm':22s} {'cells':>5s} {'claims':>7s} {'distinct':>8s} "
          f"{'names a routine':>15s}  commonest condition")
    for arm in sorted(by_arm):
        here = [r for r in by_arm[arm] if r["the_conditions"]["n_claims"]]
        if not here:
            continue
        claims = sum(r["the_conditions"]["n_claims"] for r in here)
        named = sum(r["the_conditions"]["n_claims_whose_condition_names_a_routine"]
                    for r in here)
        distinct = len({v for r in here for v, _k in r["the_conditions"]["commonest"]})
        top = collections.Counter()
        for r in here:
            for v, k in r["the_conditions"]["commonest"]:
                top[v] += k
        print(f"  {arm:22s} {len(here):5d} {claims:7d} {distinct:8d} "
              f"{named/claims if claims else 0:14.1%}  "
              f"{', '.join(repr(v) for v, _k in top.most_common(2))[:46]}")
    print("\n  A condition of 'current' on every claim means two kept rivals carry the same")
    print("  condition, so the reader is handed two contradictory claims with nothing to")
    print("  choose between them. If reachability rises and accuracy does not, this is why.")

    print("\n--- 3. THE MESSAGE: exactly two nights and nowhere else\n")
    for arm in sorted(by_arm):
        here = by_arm[arm]
        ok = all(r["the_message"]["exactly_the_intended_nights"] for r in here)
        nights = sorted({tuple(r["the_message"]["nights_that_carried_a_message"])
                         for r in here})
        shown = ("none, on any night, which is correct for this arm"
                 if nights == [()] else
                 ", ".join("/".join(str(d) for d in n) for n in nights))
        print(f"  {arm:22s} {len(here)} homes, message nights: {shown} -- "
              f"{'PASS' if ok else 'FAIL'}")
        bad = [r["household"] for r in here
               if not r["the_message"]["exactly_the_intended_nights"]]
        if bad:
            print(f"      FAILED in: {bad}")

    out = args.out or (args.root / "compliance.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"per_cell": rows}, indent=1))
    print(f"\nwritten to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
