"""Did each arm DO what its prompt asked? This runs before any outcome number.

An arm that was asked for something and did not do it is not an arm, and no accuracy
figure from it means anything. Three checks, one per variant, all computed from the
cell's own `notes.json` and `cell.json` with no model call:

  VOID BEFORE 2026-09-25: every set-aside figure derived from the `standing` FIELD, in every
  arm, including the "12% against 62% and 88%" compliance table reported earlier. The field was
  optional on every edit and was filled while the model was rewording, so it recorded how the
  field was offered rather than a choice. Setting aside is now its own action; see
  `the_two_standing_actions`.

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
from self_improve.what_is_in_this_file import print_what_is_in_this_file
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


MEMGPT = "a small working memory and an archive"

MEMGPT_CAVEAT = (
    "WHAT THIS ARM'S NUMBERS SUPPORT: 'does a 1,200-character working memory plus an archive "
    "search help', and NOT 'does an overflow-driven eviction loop help'. The overflow refusal "
    "is the mechanism that makes this arm MemGPT rather than a small claim store with a "
    "search, and the refusal count printed above is how often it fired - read it there rather "
    "than here, because a restated number goes stale and this one has: it was written as "
    "'zero over sixteen nights on one home' when that was all there was. The model keeps its "
    "window nearly full and revises what is already there rather than adding, so it rarely "
    "asks for room it does not have. A mechanism that does not fire is a finding about the "
    "workload, not missing data, which is why the count is reported rather than omitted. It "
    "also parks rather than answers whether our one-retry limit holds the method back. "
    "NOT 'cut for time': ten cells were launched like every other arm's; how many "
    "have landed is in the header at the top of this file.")


def how_memgpt_used_its_memory(cell: Dict[str, Any]) -> Dict[str, Any]:
    """MemGPT's own four numbers, and the caveat that has to travel with them.

    THE ONE THAT IS ABOUT THE METHOD RATHER THAN OUR HARNESS: it revises in place and never
    preserves. On one home, 47 revisions, 0 set aside, 0 brought back. That is the paper's own
    design - its only editing primitive is a replace - and the research agent found their own
    example of it rewriting "boyfriend named James" into "ex-boyfriend named James". If it
    holds across ten homes it is a clean result: the published system that manages its own
    memory best is also the one that cannot keep a belief it has stopped believing, which is
    exactly what this study asks about.

    IT ALSO CITES NOTHING. `attach evidence` is a separate action here and it is used zero
    times, where the other arms cite through add and revise.
    """
    applied = {"add": 0, "revise": 0, "record evidence": 0,
               "set a note aside": 0, "bring a note back": 0}
    refusals = unresolved = 0
    nights_it_fired: List[int] = []
    used = []
    for night in cell.get("nightly", []):
        for k, v in (night.get("applied") or {}).items():
            applied[k] = applied.get(k, 0) + v
        # READ THE FIELDS THE WRITER ACTUALLY WRITES. These two counts were read from
        # `n_writes_refused_for_want_of_room` and `n_refusals_still_unresolved`, which
        # `write_the_notes_memgpt` has never written: it writes the refusal LIST
        # (`refused_because_working_memory_was_full`), the retry flag and
        # `still_refused_after_the_retry`. So this reported "0 writes refused for want of room"
        # over 320 nights while two of them had fired - and the arm's caveat was built on that
        # zero, saying the mechanism that makes it MemGPT had never been exercised. The two
        # nights it fired are the two cells that crashed on the render assert, so they were
        # also the two cells missing when the earlier count was taken: a survivorship zero on
        # top of an absent-field zero. The old keys are still read, so a cell that ever
        # records them keeps working.
        refused_here = night.get("refused_because_working_memory_was_full")
        refusals += (len(refused_here) if isinstance(refused_here, list)
                     else night.get("n_writes_refused_for_want_of_room", 0) or 0)
        still = night.get("still_refused_after_the_retry")
        unresolved += (len(still) if isinstance(still, list)
                       else night.get("n_refusals_still_unresolved", 0) or 0)
        if refused_here or night.get("it_was_given_a_second_go_after_a_refusal"):
            nights_it_fired.append(night["day"])
        share = night.get("share_of_the_working_memory_used")
        if share is not None:
            used.append(share)
    return {
        "the_nights_the_refusal_fired": sorted(nights_it_fired),
        "applied": applied,
        "n_writes_refused_for_want_of_room": refusals,
        "n_refusals_still_unresolved_after_the_one_retry": unresolved,
        "mean_share_of_the_working_memory_used":
            (sum(used) / len(used)) if used else None,
        "most_of_the_working_memory_ever_used": max(used) if used else None,
        "it_revises_in_place_and_never_preserves":
            applied.get("revise", 0) > 0 and applied.get("set a note aside", 0) == 0,
        "it_cites_nothing": applied.get("record evidence", 0) == 0,
        "what_its_numbers_support": MEMGPT_CAVEAT,
    }


# THE GAP BETWEEN NOTICING AND RECORDING. Two patterns, deliberately one narrow and one
# broad, because this is a regex over free text and the honest thing is to show how much the
# answer moves with the pattern. NARROW is language that can only be a refutation; BROAD adds
# phrasings that are usually one but sometimes describe the world ("Felix does not clean them
# up immediately" is a claim, not a contradiction).
# A NEGATED MATCH IS NOT A REFUTATION. "No sightings today contradicted this" contains
# "contradict" and means the opposite: nothing went against the note. Counting those as
# ignored refutations is how an earlier version of this measure reported "a third of notes
# carry an invisible refutation" - of 24 notes called unchanged in one arm, 11 were of this
# kind, so the true figure was at most 13. Checked against a case known to differ before it
# was trusted, the rule this project adopted for any null-producing comparison.
IT_IS_A_NEGATION = re.compile(
    r"\b(?:no|nothing|none|not|never|neither|n[o']t)\b[^.;]{0,40}"
    r"(?:contradict|refut|disconfirm)", re.I)

SAYS_IT_IS_CONTRADICTED = re.compile(
    r"contradict\w*|refut\w*|disconfirm\w*|no longer|instead of|"
    r"turned out (?:to be )?(?:false|wrong)|this is wrong", re.I)
SAYS_IT_MIGHT_BE = re.compile(
    r"contradict\w*|refut\w*|disconfirm\w*|no longer|instead of|not seen|not in the|"
    r"not on the|was not|has stopped|appears to have (?:stopped|changed)|"
    r"unverified|does not hold|changed", re.I)


def noticing_without_recording(notes: Notes) -> Dict[str, Any]:
    """Notes whose own reason names a contradiction while `contradicting_observation_ids` is
    empty - the size of the gap between noticing a refutation and recording it where a reader
    can see it.

    WHY THIS REPLACES A SIMPLER READING. "0 of 452 live notes cite evidence against themselves"
    was filed as "the arms never look for disconfirmation". One note disproves that reading: it
    says "Day 24 19:50 shows Yuki in the dining room, not the living room. This contradicts the
    previous pattern", carries four supporting sightings and zero contradicting ones, and stands
    unrevised - so at answer time it reads as a well-supported belief with nothing against it.
    The model identified the refutation, stated it precisely, named the sighting and the time,
    and put it in a free-text field no reader of the notes ever sees.
    So the gap is between noticing and RECORDING, which is a different and more fixable claim.

    THE MEASUREMENT IS CRUDE AND IS REPORTED AS SUCH. It is a regex over prose. The narrow
    pattern matches only language that must be a refutation; the broad one matches phrasings
    that usually are. Both are reported, because the distance between them is the error bar.
    """
    live = [c for c in notes.claims if c.folded_into is None]
    cites = 0
    # WHAT HAPPENED TO THE NOTE IN THE SAME EDIT AS THE CONTRADICTION. Counting the phrase
    # alone counted CORRECTIONS as failures: "Glasses found in living room, contradicting
    # previous belief they were in office" is how this model narrates rewriting a note to
    # state the new truth, which is the behaviour we want. So the reason is split by what
    # happened to the note, and only the notes left UNCHANGED are the dangling kind.
    rewritten = set_aside = unchanged = negated = 0
    examples = {"rewritten": [], "unchanged": []}
    for c in live:
        if c.contradicting_observation_ids:
            cites += 1
            continue
        hist = sorted(c.revision_history, key=lambda r: (r["day"], r["time"]))
        for i, rev in enumerate(hist):
            why = rev.get("why") or ""
            if not SAYS_IT_IS_CONTRADICTED.search(why):
                continue
            if IT_IS_A_NEGATION.search(why):
                negated += 1
                break
            was = rev.get("was") or {}
            after = (hist[i + 1]["was"] if i + 1 < len(hist)
                     else {"statement": c.statement, "standing": c.standing})
            reworded = was.get("statement", "").strip() != after.get("statement", "").strip()
            went_aside = (was.get("standing", STILL_STANDING) != SET_ASIDE
                          and after.get("standing", STILL_STANDING) == SET_ASIDE)
            if reworded:
                rewritten += 1
                if len(examples["rewritten"]) < 2:
                    examples["rewritten"].append(
                        {"was": was.get("statement"), "now": after.get("statement"),
                         "why": why, "day": rev["day"]})
            elif went_aside:
                set_aside += 1
            else:
                unchanged += 1
                if len(examples["unchanged"]) < 2:
                    examples["unchanged"].append(
                        {"note": after.get("statement"), "why": why, "day": rev["day"],
                         "standing_now": c.standing,
                         "n_supporting": len(c.supporting_observation_ids)})
            break
    return {
        "n_live_notes": len(live),
        "n_that_cite_the_observation_that_disconfirmed_them": cites,
        "n_rewritten_in_that_edit_THE_CORRECT_RESPONSE": rewritten,
        "n_set_aside_in_that_edit": set_aside,
        "n_left_unchanged_AN_UPPER_BOUND": unchanged,
        "n_whose_phrase_was_A_NEGATION_not_a_refutation": negated,
        "why_unchanged_is_an_upper_bound": (
            "some were set aside at a LATER edit than the one carrying the contradiction, so "
            "they are counted here but were dealt with"),
        "the_measurement_is_a_regex_over_prose": True,
        "examples": examples,
    }


def nights_that_changed_nothing(cell: Dict[str, Any]) -> Dict[str, Any]:
    """Three numbers, never one percentage.

    Two of us measured this and got 9 and 0 for the same arm, and both were right: one function
    excused a night the model flagged `it_had_nothing_to_add`, the other counted it. For the
    record-reading arm that flag is the designed behaviour - most nights genuinely have nothing
    new to say about how a household works, and its writer imposes no minimum precisely so the
    model is not forced to invent a routine. So the split is what carries meaning:

      nights where the model applied nothing at all
      of those, nights where it SAID it had nothing to add
      unexplained

    Ours is 9 / 9 / 0. The MemGPT-style arm is 60 / 0 / 60. One percentage covering both would
    say they behave alike.

    Day 0 is excluded throughout: it has no looks, so every arm changes nothing and a 3.1%
    figure for three arms was entirely that one night per cell.

    THE ESTIMATOR IS NAMED because there are three. `applied` for the claim stores and the
    record-reading arm, `did` where a writer reports it that way, and
    `identical_to_last_night` for `wholesale rewrite` - a byte comparison of the whole summary,
    which is a stricter test than "no edit was applied" and not interchangeable with it.
    """
    changed_nothing = said_so = 0
    estimator = "no signal"
    for night in cell.get("nightly", []):
        if night.get("day") == 0:
            continue
        nothing = None
        for key in ("applied", "did"):
            if key in night:
                nothing, estimator = not any((night[key] or {}).values()), key
                break
        else:
            if "identical_to_last_night" in night:
                nothing, estimator = bool(night["identical_to_last_night"]), \
                    "identical_to_last_night"
        if not nothing:
            continue
        changed_nothing += 1
        if night.get("it_had_nothing_to_add"):
            said_so += 1
    return {"n_nights_that_changed_nothing": changed_nothing,
            "of_those_it_said_it_had_nothing_to_add": said_so,
            "unexplained": changed_nothing - said_so,
            "the_estimator": estimator,
            "n_nights_after_day_0": max(0, len(cell.get("nightly", [])) - 1)}


def the_two_standing_actions(cell: Dict[str, Any]) -> Dict[str, Any]:
    """How often a note was SET ASIDE and how often it was BROUGHT BACK, counted from the
    nightly `applied` tallies rather than inferred from the standing field.

    WHY THE FIELD CANNOT BE COUNTED AND THESE CAN. Until 2026-09-25 `standing` was an optional
    field on every edit, so the model filled it while doing something else: in `hh_s109_t03`
    23 of 24 set-asides happened in the same edit as a rewording, in `hh_s123_t03` 30 of 30,
    and the stated reasons were reasons for KEEPING a note - "No new evidence to change
    status", "This supports the routine". About 85% of notes ended up marked as not currently
    true whatever the routine was doing, which destroyed the one measure this study reads off
    that field and meant the robot answered from thirty notes all flagged as false.

    Setting aside and bringing back are now their own actions, `standing` is gone from every
    edit schema, and a revision cannot touch it. So these two counts are unambiguous in a way
    the field never was - and they are countable in both directions, which the study needs,
    because the whole point is that routines come back.

    **Any set-aside count from before this change is void, in every arm**, for the same reason
    the condition-field readings are void: it measured how a field was offered, not a choice.
    """
    per_night = []
    aside = back = 0
    for night in cell.get("nightly", []):
        applied = night.get("applied") or {}
        a = applied.get("set a note aside", 0)
        b = applied.get("bring a note back", 0)
        aside += a
        back += b
        if a or b:
            per_night.append({"day": night.get("day"), "set_aside": a, "brought_back": b})
    return {
        "n_set_aside": aside,
        "n_brought_back": back,
        "n_nights_that_moved_a_standing": len(per_night),
        "per_night": per_night,
        "the_field_this_replaces_is_void_before_2026_09_25": True,
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
                             day: int,
                             movers: Optional[Sequence[str]] = None) -> Dict[str, Any]:
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
    # COVERAGE OF THE OBJECTS THE ILLNESS MOVES, which is the only coverage the headline row
    # rests on: an arm can describe the whole house and still say nothing about the handful of
    # objects that change place. Passed in from the cell, because the household does not know
    # which objects a scenario moves. `None` keeps the old return exactly.
    on_movers: Dict[str, Any] = {"n_movers": None, "n_movers_with_a_live_claim": None,
                                 "share_of_movers_covered": None,
                                 "movers_with_no_live_claim": None}
    if movers:
        want = [o for o in movers if o in per_object]
        got = [o for o in want if per_object[o] >= 1]
        on_movers = {"n_movers": len(want), "n_movers_with_a_live_claim": len(got),
                     "share_of_movers_covered": (len(got) / len(want)) if want else None,
                     "movers_with_no_live_claim": sorted(set(want) - set(got))}
    return {
        **on_movers,
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
    # ONE ESTIMATOR ONLY, and it is `why_a_condition_is_not_one`. There used to be a second
    # one here: a `vacuous` set of exact strings ("current", "not said", ...), whose share was
    # reported beside the first under a different name. Once the display bug was fixed nothing
    # said exactly "current" any more, so that set matched nothing and the column read
    # **100.0% for every arm** while the real figure was 54-87%. Two estimators of one
    # quantity, in one dict, printed in two sections, and the weaker one flattered the result.
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


def the_edit_allowance(cell: Dict[str, Any]) -> Dict[str, Any]:
    """How many edits the writer was ALLOWED each night, and how often that bound it.

    WHY THIS IS A COMPLIANCE MEASURE. The allowance is a sentence in the nightly prompt, so
    two arms with different allowances are not running the same prompt whatever else matches.
    `the log and notes about the routine` uses a fixed allowance, because its notes may not
    name places at all and an allowance derived from the objects it saw would make no sense
    for it; its control derives one per night. That is a deliberate design choice and it is
    also a SECOND difference between the two arms the paper turns on, so it is measured here
    rather than described in a comment.
    """
    by_period: Dict[str, Dict[str, Any]] = {}
    for night in cell.get("nightly", []):
        allowed = night.get("how_many_edits_it_was_allowed")
        if allowed is None:
            continue
        row = by_period.setdefault(night.get("period") or "unknown",
                                   {"nights": 0, "allowed": [], "offered": [], "cap_bit": 0})
        row["nights"] += 1
        row["allowed"].append(allowed)
        row["offered"].append(night.get("n_edits_offered") or 0)
        row["cap_bit"] += bool(night.get("the_edits_cap_bit"))
    out: Dict[str, Any] = {}
    for period, row in by_period.items():
        out[period] = {
            "nights": row["nights"],
            "mean_allowed": statistics.mean(row["allowed"]),
            "the_allowance_never_changed": len(set(row["allowed"])) == 1,
            "mean_offered": statistics.mean(row["offered"]),
            "n_nights_the_cap_bit": row["cap_bit"],
            "share_of_nights_the_cap_bit": row["cap_bit"] / row["nights"],
        }
    return out


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
        # READ WITH DEFAULTS, and derived from the run's own nights where it can be.
        # This module was written for the three_prompts variants, whose `arm.json` recorded
        # which writing-prompt switches were on. The overnight wave's arms are memory
        # FORMATS - no such switches exist, so its `arm.json` has no such keys and every
        # cell raised KeyError here. A default of False is the right reading for those arms
        # (no message, no rival-beliefs instruction) and it is the existing behaviour for
        # the variants, which still carry the keys.
        "nights_the_writer_ran": arm.get(
            "n_nights_the_writer_ran",
            sum(1 for n in cell.get("nightly", []) if not n.get("no_notes_were_written"))),
        "asked_for": {k: bool(arm.get(k, False))
                      for k in ("keep_rival_beliefs", "describe_the_person",
                                "tell_it_the_resident_is_unwell")},
        # counted over the whole month AND at a fixed night, so a cross-arm table can use
        # the day-23 figures and be comparing the same number of nights in every arm
        "rival_beliefs": what_the_revisions_did(notes, household),
        "rival_beliefs_to_day_23": what_the_revisions_did(notes, household, 23),
        "the_conditions": what_the_conditions_say(notes),
        "the_two_standing_actions": the_two_standing_actions(cell),
        "nights_that_changed_nothing": nights_that_changed_nothing(cell),
        "the_edit_allowance": the_edit_allowance(cell),
        "noticing_without_recording": noticing_without_recording(notes),
        "memgpt": (how_memgpt_used_its_memory(cell)
                   if arm.get("how_memory_is_written") == MEMGPT else None),
        "coverage": {str(d): coverage_and_duplication(notes, household, d,
                                                      movers=cell.get("movers"))
                     for d in (13, 23, 31)},
        "growth": the_growth_curve(notes, household),
        "the_lines": {str(d): what_the_lines_say(notes, household, d) for d in days},
        "the_message": the_message_nights(cell),
    }
    wanted = ([arm["first_disrupted_day"], arm["first_day_back"]]
              if arm.get("tell_it_the_resident_is_unwell") else [])
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
    # WHICH ARM IS THE CONTROL IS NOW AN ARGUMENT. This module was written for the
    # three_prompts variants, where the control was called "control". In the overnight wave
    # the one-variable partner for "the log and notes about the routine" is
    # "incremental_edits" - the plain claim store it is a fork of - and a hardcoded name made
    # the report exit with "no control cells" on a wave with 54 finished ones.
    parser.add_argument("--control", default=CONTROL,
                        help="the arm every contrast is against "
                             "(directory name under cells/)")
    args = parser.parse_args(argv)

    print_what_is_in_this_file(args.root, "COMPLIANCE, the gate that runs before any outcome")

    households: Dict[str, FrozenHousehold] = {}
    rows: List[Dict[str, Any]] = []
    # ARMS ARE DISCOVERED FROM THE DIRECTORIES, not from a hardcoded list. This module was
    # written for the three_prompts variants and its list did not contain the memory-method
    # arms, so pointed at the overnight wave it would have found nothing and printed "no
    # finished cells" over 54 complete cells - a silent empty report rather than an error.
    arms = sorted(d.name for d in (args.root / "cells").glob("*") if d.is_dir())
    for arm in arms:
        for name in sorted(d.name for d in (args.root / "cells" / arm).glob("*")
                           if d.is_dir()):
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
    control = by_arm.get(args.control, [])

    print(f"\n{'='*78}\nCOMPLIANCE, before any outcome. "
          f"{len(rows)} cells, {len({r['household'] for r in rows})} homes.\n{'='*78}")

    print("\n--- 0. SET ASIDE AND BROUGHT BACK, as their own actions\n")
    print("  Until 2026-09-25 `standing` was an optional field on every edit, so it got filled")
    print("  while the model was doing something else: 23 of 24 set-asides in one household")
    print("  and 30 of 30 in another happened in the same edit as a rewording, with stated")
    print("  reasons that were reasons for KEEPING the note. About 85% of notes ended up")
    print("  flagged as not currently true whatever the routine was doing.")
    print("  ANY SET-ASIDE COUNT FROM BEFORE THAT CHANGE IS VOID, IN EVERY ARM - the same")
    print("  footnote the condition field carries, and for the same reason.\n")
    print(f"  {'arm':22s} {'cells':>5s} {'set aside':>10s} {'brought back':>13s} "
          f"{'nights that moved one':>21s}")
    for arm in sorted(by_arm):
        here = [r.get("the_two_standing_actions") for r in by_arm[arm]
                if r.get("the_two_standing_actions")]
        if not here:
            continue
        print(f"  {arm:22s} {len(here):5d} {sum(x['n_set_aside'] for x in here):10d} "
              f"{sum(x['n_brought_back'] for x in here):13d} "
              f"{sum(x['n_nights_that_moved_a_standing'] for x in here):21d}")
    print("\n  Both directions matter: the study's question is whether a belief written for the")
    print("  ordinary routine survives the disrupted one AND is used again when it returns, so")
    print("  'brought back' is half the measure and the old field could not express it at all.")

    memgpt = [r["memgpt"] for r in rows if r.get("memgpt")]
    if memgpt:
        print("\n--- 0b. MEMGPT: its four numbers, and what they do and do not support\n")
        m = lambda k: sum((x.get(k) or 0) for x in memgpt)
        av = [x["mean_share_of_the_working_memory_used"] for x in memgpt
              if x["mean_share_of_the_working_memory_used"] is not None]
        print(f"  cells: {len(memgpt)}")
        if av:
            print(f"  working memory used: mean {statistics.mean(av):.0%}, "
                  f"most ever {max(x['most_of_the_working_memory_ever_used'] or 0 for x in memgpt):.0%}")
        print(f"  writes refused for want of room:          "
              f"{m('n_writes_refused_for_want_of_room')}")
        print(f"  refusals still unresolved after one retry: "
              f"{m('n_refusals_still_unresolved_after_the_one_retry')}")
        tot = {}
        for x in memgpt:
            for k, v in x["applied"].items():
                tot[k] = tot.get(k, 0) + v
        print(f"  actions: " + ", ".join(f"{k} {v}" for k, v in sorted(tot.items())))
        print(f"  revises in place and never preserves: "
              f"{all(x['it_revises_in_place_and_never_preserves'] for x in memgpt)}")
        fired = [(r["household"], (r.get("memgpt") or {}).get("the_nights_the_refusal_fired")
                                   or []) for r in rows if r.get("memgpt")]
        fired = [(h, d) for h, d in fired if d]
        if fired:
            print("  the nights the overflow refusal FIRED, per cell: "
                  + "; ".join(f"{h} day(s) {d}" for h, d in fired))
        else:
            print("  the overflow refusal never fired in any cell of this arm")
        print(f"  cites nothing (attach evidence unused): "
              f"{all(x['it_cites_nothing'] for x in memgpt)}")
        print()
        for line in (MEMGPT_CAVEAT[i:i+94] for i in range(0, len(MEMGPT_CAVEAT), 94)):
            print(f"  {line}")

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
        if arm == args.control:
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
        if arm == args.control:
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
    print("")
    print("  THE PROMPT PARAGRAPH IS NOT THE ONLY DIFFERENCE, and the other one is measured")
    print("  rather than described: the two arms are given different NIGHTLY EDIT ALLOWANCES,")
    print("  which is a sentence in the same prompt. Deliberate - a record-reading arm's notes")
    print("  may not name places, so an allowance derived from the objects it saw would make no")
    print("  sense for it - but it is a second variable, and it does not fall evenly across the")
    print("  windows the headline row reads:")
    print("")
    print(f"  {'arm':22s} {'window':15s} {'nights':>6s} {'allowed':>8s} {'fixed?':>6s} "
          f"{'offered':>7s} {'cap bit':>7s}")
    for arm in sorted(by_arm):
        got = [r["the_edit_allowance"] for r in by_arm[arm] if r.get("the_edit_allowance")]
        if not got:
            continue
        for window in ("settled", "disrupted", "back to normal"):
            here = [g[window] for g in got if window in g]
            if not here:
                continue
            nights = sum(x["nights"] for x in here)
            allowed = statistics.mean([x["mean_allowed"] for x in here])
            fixed = all(x["the_allowance_never_changed"] for x in here)
            offered = statistics.mean([x["mean_offered"] for x in here])
            bit = sum(x["n_nights_the_cap_bit"] for x in here)
            print(f"  {arm:22s} {window:15s} {nights:6d} {allowed:8.1f} "
                  f"{'yes' if fixed else 'no':>6s} {offered:7.1f} "
                  f"{bit:3d} ({bit/nights:4.0%})")
    print("")
    print("  A bound cap means the writer had more it wanted to change than it was allowed to,")
    print("  on a night when the routine was changing. Which way it cuts is stated with the")
    print("  outcome, not here: fewer edits allowed when there is most to change can only")
    print("  handicap the arm it binds, so it cannot manufacture a win for that arm - but it")
    print("  can manufacture a loss.")

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
        if arm == args.control:
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
          f"{'a real condition':>16s}  commonest condition")
    for arm in sorted(by_arm):
        here = [r for r in by_arm[arm] if r["the_conditions"]["n_claims"]]
        if not here:
            continue
        claims = sum(r["the_conditions"]["n_claims"] for r in here)
        # the SAME estimator as 2a, named in the column header, because this section and
        # that one are two readings of one field and used to disagree by 40 points
        named = sum(r["the_conditions"]["n_that_name_a_real_condition"] for r in here)
        distinct = len({v for r in here for v, _k in r["the_conditions"]["commonest"]})
        top = collections.Counter()
        for r in here:
            for v, k in r["the_conditions"]["commonest"]:
                top[v] += k
        print(f"  {arm:22s} {len(here):5d} {claims:7d} {distinct:8d} "
              f"{named/claims if claims else 0:15.1%}  "
              f"{', '.join(repr(v) for v, _k in top.most_common(2))[:46]}")
    print("\n  A condition of 'current' on every claim means two kept rivals carry the same")
    print("  condition, so the reader is handed two contradictory claims with nothing to")
    print("  choose between them. If reachability rises and accuracy does not, this is why.")

    # ================== 1c. coverage of the objects the illness moves ==================
    print("\n--- 0c. NIGHTS THAT CHANGED THE MEMORY NOT AT ALL, as three numbers.")
    print("    Never as one percentage: for the record-reading arm a night with nothing to add")
    print("    is the designed behaviour - its writer imposes no minimum, so the model is not")
    print("    forced to invent a routine - and for the MemGPT-style arm the same nights are")
    print("    unaccounted for. Day 0 is excluded: it has no looks, so every arm changes")
    print("    nothing and counting it made three arms look alike at 3.1%.\n")
    print(f"  {'arm':40s} {'nights':>6s} {'changed nothing':>15s} {'it SAID so':>10s} "
          f"{'UNEXPLAINED':>11s}  estimator")
    for arm in sorted(by_arm):
        here = [r["nights_that_changed_nothing"] for r in by_arm[arm]
                if r.get("nights_that_changed_nothing")]
        if not here:
            continue
        add = lambda k: sum(x[k] for x in here)
        estimators = sorted({x["the_estimator"] for x in here})
        print(f"  {arm:40s} {add('n_nights_after_day_0'):6d} "
              f"{add('n_nights_that_changed_nothing'):15d} "
              f"{add('of_those_it_said_it_had_nothing_to_add'):10d} "
              f"{add('unexplained'):11d}  {', '.join(estimators)}")
    print("\n  The estimator column matters: `wholesale rewrite` is measured by")
    print("  `identical_to_last_night`, a byte comparison of the whole summary, which is a")
    print("  THIRD estimator and a stricter test than 'no edit was applied'. Its 6 nights of")
    print("  31 are not interchangeable with the other arms' numbers, and they are")
    print("  consecutive (days 8 to 13) rather than scattered.\n")

    print("\n--- 1c. COVERAGE OF THE OBJECTS THE ILLNESS MOVES. The headline row rests on")
    print("    these objects only, so whole-house coverage is not the number that matters.\n")
    print(f"  {'arm':22s} {'cells':>5s} {'movers':>6s} "
          f"{'covered d13':>11s} {'d23':>6s} {'d31':>6s}   never covered by day 23")
    for arm in sorted(by_arm):
        here = [r for r in by_arm[arm] if r["coverage"]["23"].get("n_movers")]
        if not here:
            print(f"  {arm:22s} {'-':>5s} no cell recorded which objects move")
            continue
        n_mov = sum(r["coverage"]["23"]["n_movers"] for r in here)
        def share(day: str) -> float:
            want = sum(r["coverage"][day]["n_movers"] for r in here)
            got = sum(r["coverage"][day]["n_movers_with_a_live_claim"] for r in here)
            return got / want if want else 0.0
        never = sorted({o for r in here
                        for o in (r["coverage"]["23"]["movers_with_no_live_claim"] or [])})
        print(f"  {arm:22s} {len(here):5d} {n_mov:6d} {share('13'):11.1%} "
              f"{share('23'):6.1%} {share('31'):6.1%}   "
              f"{', '.join(never[:3])}{' ...' if len(never) > 3 else ''}")
    print("\n  Pooled over homes, so a home with more movers weighs more; the per-home spread")
    print("  is in compliance.json. An arm cannot be read as answering about an object whose")
    print("  place its notes never mention - that is what 'never covered' names.")

    # ============ 4. the gap between noticing a refutation and recording it ============
    print("\n--- 4. DOES A NOTE EVER CITE THE OBSERVATION THAT DISCONFIRMED IT?\n")
    print(f"  {'arm':22s} {'cells':>5s} {'live notes':>10s} {'CITE IT':>8s} "
          f"{'said so and rewrote':>19s} {'set aside':>9s} {'unchanged':>9s} "
          f"{'was a negation':>14s}")
    for arm in sorted(by_arm):
        here = [r["noticing_without_recording"] for r in by_arm[arm]
                if r.get("noticing_without_recording")]
        if not here:
            continue
        add = lambda k: sum(x[k] for x in here)
        print(f"  {arm:22s} {len(here):5d} {add('n_live_notes'):10d} "
              f"{add('n_that_cite_the_observation_that_disconfirmed_them'):8d} "
              f"{add('n_rewritten_in_that_edit_THE_CORRECT_RESPONSE'):19d} "
              f"{add('n_set_aside_in_that_edit'):9d} "
              f"{add('n_left_unchanged_AN_UPPER_BOUND'):9d} "
              f"{add('n_whose_phrase_was_A_NEGATION_not_a_refutation'):14d}")
    print("\n  WHAT THE ZERO MEANS, and what it does not. `contradicting_observation_ids` is")
    print("  the field a READER of the notes sees: at answer time a note with four sightings")
    print("  for and none against reads as a well-supported belief. Zero there does NOT mean")
    print("  the arms never look for disconfirmation - the 'said so and rewrote' column is")
    print("  the model identifying a refutation and acting on it correctly. The gap is")
    print("  between noticing and RECORDING, and it is the recording that a later night, or")
    print("  a reader, or an answer step can use.")
    print("  'unchanged' is an UPPER BOUND and the whole column is a regex over prose: some")
    print("  of those notes were dealt with at a later edit than the one carrying the phrase.")
    print("  'was a negation' is the regex's own false-positive rate, counted rather than")
    print("  estimated: 'No sightings today contradicted this' matches the word and means the")
    print("  opposite. Those are excluded from every other column here. An earlier version of")
    print("  this measure did not exclude them and reported a third of notes as carrying an")
    print("  invisible refutation.")
    for arm in sorted(by_arm):
        ex = {"rewritten": [], "unchanged": []}
        for r in by_arm[arm]:
            for kind in ex:
                ex[kind] += (r.get("noticing_without_recording", {})
                             .get("examples", {}).get(kind) or [])
        if not (ex["rewritten"] or ex["unchanged"]):
            continue
        print(f"\n  {arm} - one example of each kind:")
        if ex["rewritten"]:
            e = ex["rewritten"][0]
            print(f"    REWROTE (correct), day {e['day']}:")
            print(f"      was: {(e.get('was') or '')[:150]}")
            print(f"      now: {(e.get('now') or '')[:150]}")
            print(f"      its reason: {(e.get('why') or '')[:150]}")
        if ex["unchanged"]:
            e = ex["unchanged"][0]
            print(f"    LEFT AS IT WAS, day {e['day']}, standing now "
                  f"{e.get('standing_now')!r}, {e.get('n_supporting')} sightings for and "
                  f"0 against on the face of it:")
            print(f"      the note: {(e.get('note') or '')[:150]}")
            print(f"      its reason: {(e.get('why') or '')[:150]}")

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
