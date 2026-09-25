"""The raw-log baseline: no curated notes at all, a search tool over the log instead.

Every arm in this study so far answers from NOTES - eight lines chosen by the
format's own logic out of a nightly artifact the model wrote. This arm removes the
notes entirely. The model is handed nothing but the question, the house's rooms and
spots, and a search tool over that household's own `looks.jsonl`: every sighting the
robot ever made and every absence it ever recorded, exactly as the harness logged
them. It searches a few times, then answers in the same format every other arm uses.

This is the strongest baseline in the memory literature - retrieval over raw
observations rather than a maintained summary - and it tests the study's premise
directly.

WHAT IT ACTUALLY TURNED OUT TO BE, measured 2026-09-24 and recorded in
THE_ARM_IS_A_RECENCY_LOOKUP.json. Do not read the paragraph above without this one.

  WHERE THE LOG IS THIN OR NOTHING HAS CHANGED YET, the arm is a RECENCY LOOKUP. On the
  patrol logs and at the control freeze point it names the place of the object's most
  recent sighting on 159 of 168 answered questions - 94.6% - and its shelf accuracy is
  identical to the one-line newest-sighting rule in seven of eight cells. There it is
  that rule reached through three to four language-model calls, which explains why a
  richer log barely moved it, why it made 1.12 searches, why it never exhausted a
  four-search budget, and why 89% truncation did it no damage.

  AT THE DECISIVE FREEZE POINT ON A RICH LOG THAT IS NOT TRUE, and the earlier general
  claim is withdrawn. Agreement falls to 75% pooled and 62-67% in the two households
  whose question window is not degenerate, and where the model departs from recency it
  gains 20.8 points at shelf level in both. So the collapse to recency belongs to the
  thin log and to a freeze point before anything has changed, not to the arm.

  It is NOT, however, a detected win: model minus rule is +13.9 points at shelf level
  with a standard error of 6.9 clustered on household, n=3, and at room level +4.2 with
  two of three households negative. Three households of 24 questions settle nothing
  about accuracy; they settle only that the 94.6% figure does not generalise.

  See DECISIVE_PROBE/THE_RECENCY_CLAIM_DOES_NOT_SURVIVE.json. One of those three cells,
  hh_s2_t03, drew a 24-question SUBSAMPLE that a single fact answers 88% of the time and
  must be reported separately rather than pooled - a fault of the cap, not of the
  household, whose full window a single fact answers only 38.3% of. That is why the
  capped sampler in this module spreads over the clock as well as the days.

AND THE RULE THAT GOVERNS EVERY NUMBER THIS MODULE EVER PRODUCED ON A PATROL LOG:

  No patrol-log memory number may be quoted as evidence about curation.

  This applies to several other jobs' numbers as well as this one. On the patrol log
  the newest-sighting rule already takes 91% of everything the log makes available
  (41.8% against a 45.8% ceiling), so every method is pressed against the same ceiling
  and no comparison between memories can separate them. A tie there is the ceiling
  pressing down on both, not curation failing. See THE_THIN_LOG_WAS_THE_CEILING.json.

Three things it must not do, each of which would invalidate the comparison:

  it must not see the future. The log is filtered to observations on or before the
  freeze day, the same day the other arms' notes were frozen at. A question from day
  17 answered at the day-23 freeze point may see days 0 to 23, which is exactly what
  the day-23 notes were written from;

  it must not answer in a different format. The final turn uses the same CONF_SCHEMA,
  the same allowed spot list, the same CONF_SCALE wording and the same max_tokens as
  `frozen_memory_test.question_prompt`, so the scorer cannot tell the arms apart;

  it must not hide truncation. A search that matched more than the cap says so in the
  result, with the count, rather than silently dropping the rest.

What it records beyond accuracy, because a tool-use arm has failure modes accuracy
cannot show:

  how many searches it actually made, and what it searched for. One search and a
  guess is a different result from an exhausted budget;

  the error partition. Of the questions it got wrong: was the answer anywhere in the
  log it could have searched, and did any of its own searches actually return it?
  That splits "the evidence was never gathered" (the sensing limit, which bounds
  every arm equally) from "it did not search for the evidence" from "it saw the
  evidence and answered something else".

    python -m self_improve.raw_log_baseline \
        --households hh_s0_t03 --freeze-points "did it learn the new routine"
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.patrol.llm import CONF_SCALE, CONF_SCHEMA, LLMClient, parse_conf
from self_improve.frozen_household import (FROZEN_BANKS, FrozenHousehold, period_of_day,
                                           plain_place_name)
from self_improve.frozen_memory_test import (FREEZE_POINTS, questions_in_the_window,
                                             sanity_assay, spread_across_the_days)
from self_improve.looking import hours_and_minutes

ARM_NAME = "raw_log_and_a_search_tool"

# The observation stream this arm searches. Memory-guided search only, by the
# coordinator's design call of 2026-09-24, and the write-up must name it that way: this
# arm asks a MEMORY question - does curating notes beat keeping everything and searching
# it - so it has to sit on the same observation stream the primary curated arms sit on.
# Run on the random or fixed-rotation logs it would answer "how good is grep over a
# badly chosen log", which is a different and less interesting question. So every result
# from this module is a comparison WITHIN the memory-guided sensing arm and must never be
# read as a claim about all three looking arms.
DEFAULT_SOURCE = pathlib.Path("results/self_improve/search_driven")
DEFAULT_CELL = "memory-guided_search/wholesale_rewrite"

# The patrol sweep, kept so the measurements taken on it reproduce. It must NOT be used
# for a memory claim: measured on 2026-09-24, its log is so thin that the one-line
# newest-sighting rule already takes 91% of everything the log makes available, so every
# method is pressed against the same ceiling and no comparison between memories can
# separate them. See THE_THIN_LOG_WAS_THE_CEILING.json.
THE_THIN_PATROL_SWEEP = pathlib.Path("results/self_improve/memory_factor_v1")

# Deliberately close to frozen_memory_test.SYSTEM: the only difference is where the
# evidence comes from.
SYSTEM = ("You help a home robot keep track of where household things are. "
          "The robot keeps no notes: it searches its raw observation log instead. "
          "Answer with JSON only.")

RESULT_CAP = 25          # results returned per search, newest first, truncation reported
DEFAULT_MAX_SEARCHES = 4

# Under a joint cap the absences crowd the sightings out, and on a rich log they do it
# badly. Measured on the search-driven log at freeze day 20, hh_s0, a search for
# `book_nora` with what_kind "both" returned 1 sighting and 24 absences while hiding 24
# of that object's 25 sightings - the records that answer the question, dropped in
# favour of records saying where it was not. On the patrol log the cap never bound at
# all (0% of searches truncated), so this only appears once the log is rich.
#
# So the kinds are capped SEPARATELY and each keeps its own slice, with the slack from
# one kind lent to the other so a search that matches no absences still shows 25
# sightings. Newest-first within each kind; the interleaving by date is kept for
# display so the two kinds still read as one timeline.
SIGHTINGS_SHARE_OF_THE_CAP = 15

def spread_across_the_days_and_the_clock(questions: Sequence[dict], how_many: int
                                         ) -> List[dict]:
    """A capped sample spread across the days AND across the hours of each day.

    `frozen_memory_test.spread_across_the_days` fixed a real fault - a cap of N used to
    take the window's chronologically first N, so it measured the first two DAYS - but it
    replaced it with a subtler one of the same family. It round-robins by POSITION within
    each day, and a day's questions are in time order, so a cap of 24 over ten days takes
    positions 0, 1 and 2: the first two or three questions of every day. Measured
    2026-09-24 over all ten households, a cap of 24 covers only hours 7-8 of a window
    that runs 07:00 to 22:00.

    Early morning is when things sit in their resting places, so the window it selects is
    far easier and far more repetitive than the window it claims to sample. The
    one-fact-for-the-whole-house baseline rises from a mean of 29.6% on the full 240
    questions to 52.3% at a cap of 30, and in hh_s2_t03 from 38.3% to 86.7% - a window a
    single fact answers, where no method can differ from any other. That household is
    perfectly healthy on its full window; the degeneracy was manufactured by the cap.

    So this allocates the cap evenly across the days and then takes EVENLY SPACED indices
    within each day, which keeps every day represented and spreads the hours too.

    It lives here rather than in frozen_memory_test because four jobs import that module
    mid-run and changing a shared sampler underneath them would be worse than the bug.
    The fault is written up for its owner instead.
    """
    if how_many >= len(questions):
        return list(questions)
    by_day: Dict[int, List[dict]] = collections.defaultdict(list)
    for question in questions:
        by_day[question["day_index"]].append(question)
    days = sorted(by_day)
    for day in days:
        by_day[day].sort(key=lambda q: (q["t_query"], q["question_id"]))

    # even allocation across days, remainder to the earliest days
    base, extra = divmod(how_many, len(days))
    taken: List[dict] = []
    for index, day in enumerate(days):
        want = base + (1 if index < extra else 0)
        here = by_day[day]
        want = min(want, len(here))
        if want == 0:
            continue
        if want == 1:
            picks = [len(here) // 2]          # the middle of the day, not its first hour
        else:
            picks = [round(i * (len(here) - 1) / (want - 1)) for i in range(want)]
        seen = set()
        for p in picks:
            if p not in seen:
                seen.add(p)
                taken.append(here[p])
    return sorted(taken, key=lambda q: (q["t_query"], q["question_id"]))


# One JSON object per tool turn. Every field is required and nullable, because the
# server's constrained decoding fills required fields reliably and optional ones
# unreliably; null means "do not constrain on this".
SEARCH_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string", "maxLength": 400},
        "what_next": {"type": "string", "enum": ["search", "answer"]},
        "object_id": {"type": ["string", "null"]},
        "room": {"type": ["string", "null"]},
        "place": {"type": ["string", "null"]},
        "day_from": {"type": ["integer", "null"]},
        "day_to": {"type": ["integer", "null"]},
        "what_kind": {"type": "string", "enum": ["sightings", "absences", "both"]},
    },
    "required": ["reasoning", "what_next", "object_id", "room", "place",
                 "day_from", "day_to", "what_kind"],
    "additionalProperties": False,
}


# ------------------------------------------------------------- the log itself --

@dataclass
class Observation:
    """One searchable row. A sighting is one record; an absence is one record per
    (object, room, look), collapsing the per-spot absence rows the harness writes.

    The collapse is not a simplification of the evidence. The harness emits one
    Absence per (object, spot) for every spot behind the target it looked at, and it
    emits them only for objects it did not find anywhere in that look - so the whole
    group means exactly "looked through this room, the thing was not in it". Rendering
    the group as one line says that, names the spot count, and cites the first of the
    observation ids, which is honest in a way that 12 near-identical lines eating the
    result cap would not be.
    """
    kind: str                      # "sighting" or "absence"
    observation_id: str
    object_id: str
    object_class: str
    room: str
    day: int
    time: int
    place_id: Optional[str] = None            # sightings
    place_ids: List[str] = field(default_factory=list)   # absences: every spot checked
    n_more_observation_ids: int = 0

    def as_plain_words(self) -> str:
        when = f"day {self.day} {hours_and_minutes(self.time)}"
        if self.kind == "sighting":
            what = (f"{self.object_id} ({self.object_class})" if self.object_class
                    else self.object_id)
            return (f"[{self.observation_id}] {when}: saw {what} on "
                    f"{plain_place_name(self.place_id)} in the {self.room}")
        tail = (f" (+{self.n_more_observation_ids} more records)"
                if self.n_more_observation_ids else "")
        return (f"[{self.observation_id}{tail}] {when}: looked through the whole "
                f"{self.room} ({len(self.place_ids)} spots) and {self.object_id} "
                f"was NOT there")


class ObservationLog:
    """A household's `looks.jsonl`, filtered to on-or-before the freeze day, with a
    search over it. Nothing here reads the household's truth: the log is what the
    robot's own looks produced and nothing else."""

    def __init__(self, looks_path: pathlib.Path, up_to_and_including_day: int) -> None:
        self.looks_path = looks_path
        self.freeze_day = up_to_and_including_day
        self.rows: List[Observation] = []
        self.n_look_records = 0
        self.n_look_records_withheld_as_future = 0
        # The newest day present in the FILE, before the freeze-day filter. Needed to
        # tell "this log stops at day 23 because it is still being written" from "this
        # log runs to day 31 and I am looking at its day-23 view", which are the same
        # thing once the rows are filtered and completely different for trusting a number.
        self.newest_day_in_the_file = -1
        self.rooms_looked_in: List[str] = []
        self.a_torn_final_line_was_skipped = False
        # A log that is still being written can have a half-flushed final line. Skipping
        # it is correct - the writer appends one record per line and will complete it -
        # but skipping a malformed line ANYWHERE ELSE would be hiding corruption, so only
        # the last line gets that licence and any other bad line is raised.
        lines = looks_path.read_text().splitlines()
        for index, line in enumerate(lines):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError:
                if index == len(lines) - 1:
                    self.a_torn_final_line_was_skipped = True
                    continue
                raise ValueError(
                    f"{looks_path} line {index + 1} of {len(lines)} is not valid JSON, and "
                    f"it is not the final line, so this is corruption rather than a "
                    f"half-written append")
            if row.get("kind") != "look":
                continue
            self.n_look_records += 1
            self.newest_day_in_the_file = max(self.newest_day_in_the_file, int(row["day"]))
            if int(row["day"]) > up_to_and_including_day:
                self.n_look_records_withheld_as_future += 1
                continue
            for target in row.get("targets", []):
                if target["kind"] == "room" and target["name"] not in self.rooms_looked_in:
                    self.rooms_looked_in.append(target["name"])
            for sighting in row.get("sightings", []):
                self.rows.append(Observation(
                    kind="sighting", observation_id=sighting["observation_id"],
                    object_id=sighting["object_id"],
                    object_class=sighting.get("object_class", ""),
                    room=sighting["room"], day=int(sighting["day"]),
                    time=int(sighting["time"]), place_id=sighting["place_id"]))
            grouped: Dict[Tuple[str, str], List[dict]] = collections.defaultdict(list)
            for absence in row.get("absences", []):
                grouped[(absence["object_id"], absence["room"])].append(absence)
            for (object_id, room), group in sorted(grouped.items()):
                group.sort(key=lambda a: a["observation_id"])
                self.rows.append(Observation(
                    kind="absence", observation_id=group[0]["observation_id"],
                    object_id=object_id, object_class="", room=room,
                    day=int(group[0]["day"]), time=int(group[0]["time"]),
                    place_ids=[a["place_id"] for a in group],
                    n_more_observation_ids=len(group) - 1))
        # newest first, and stable within a moment
        self.rows.sort(key=lambda r: (r.day, r.time, r.observation_id), reverse=True)
        self.sightings = [r for r in self.rows if r.kind == "sighting"]
        self.absences = [r for r in self.rows if r.kind == "absence"]

    # ------------------------------------------------------------- the tool --

    def search(self, object_id: Optional[str] = None, room: Optional[str] = None,
               place: Optional[str] = None, day_from: Optional[int] = None,
               day_to: Optional[int] = None, what_kind: str = "both",
               cap: int = RESULT_CAP) -> Dict[str, Any]:
        """Matching observations, newest first, capped, with the truncation stated.

        Matching is by substring, case-insensitively, on the ids the log itself uses,
        so "razor" finds razor_nora and "bath" finds the bathroom. An absence matches
        a `place` if that spot was one of the spots the look checked.
        """
        needle_object = (object_id or "").strip().lower() or None
        # Exact ids win over substrings. Without this, a search for `book_nora` also
        # returns every record about `notebook_nora` and `sketchbook_nora`, because the
        # asked-for id is a substring of both - so the model is handed records about
        # other objects and cannot tell from the line which one it asked for. Harmless
        # on the patrol log's 13 objects; on the search-driven log's 60-plus it is a
        # live source of wrong answers. Substring matching is KEPT for the case it was
        # added for ("razor" -> razor_nora), it just no longer overrides an exact hit.
        exact_object = (needle_object is not None
                        and any(r.object_id.lower() == needle_object for r in self.rows))
        needle_room = (room or "").strip().lower() or None
        needle_place = (place or "").strip().lower() or None
        kinds = ({"sighting"} if what_kind == "sightings" else
                 {"absence"} if what_kind == "absences" else {"sighting", "absence"})
        hits: List[Observation] = []
        for r in self.rows:
            if r.kind not in kinds:
                continue
            if needle_object:
                if exact_object:
                    if r.object_id.lower() != needle_object:
                        continue
                elif needle_object not in r.object_id.lower() \
                        and needle_object not in (r.object_class or "").lower():
                    continue
            if needle_room and needle_room not in r.room.lower():
                continue
            if needle_place:
                if r.kind == "sighting":
                    if needle_place not in (r.place_id or "").lower():
                        continue
                elif not any(needle_place in p.lower() for p in r.place_ids):
                    continue
            if day_from is not None and r.day < int(day_from):
                continue
            if day_to is not None and r.day > int(day_to):
                continue
            hits.append(r)

        # Separate slices per kind, slack lent between them, newest first within each.
        matched_sightings = [h for h in hits if h.kind == "sighting"]
        matched_absences = [h for h in hits if h.kind == "absence"]
        want_sightings = min(len(matched_sightings), SIGHTINGS_SHARE_OF_THE_CAP)
        want_absences = min(len(matched_absences), cap - want_sightings)
        # lend the unused half back to whichever kind still has records waiting
        want_sightings = min(len(matched_sightings), cap - want_absences)
        kept = set(h.observation_id for h in matched_sightings[:want_sightings])
        kept |= set(h.observation_id for h in matched_absences[:want_absences])
        shown = [h for h in hits if h.observation_id in kept]

        shown_sightings = sum(1 for h in shown if h.kind == "sighting")
        return {
            "n_matched": len(hits),
            "n_shown": len(shown),
            "truncated": len(hits) > len(shown),
            "n_sightings_matched": len(matched_sightings),
            "n_absences_matched": len(matched_absences),
            "n_sightings_shown": shown_sightings,
            "n_absences_shown": len(shown) - shown_sightings,
            "n_sightings_hidden": len(matched_sightings) - shown_sightings,
            "n_absences_hidden": len(matched_absences) - (len(shown) - shown_sightings),
            "lines": [h.as_plain_words() for h in shown],
            "shown_observation_ids": [h.observation_id for h in shown],
            "shown_places": [h.place_id for h in shown if h.kind == "sighting"],
        }

    # -------------------------------------------- what the evidence allowed --

    def places_this_object_was_ever_seen_in(self, object_id: str) -> List[str]:
        return sorted({r.place_id for r in self.sightings
                       if r.object_id == object_id and r.place_id})

    def rooms_this_object_was_ever_seen_in(self, object_id: str) -> List[str]:
        return sorted({r.room for r in self.sightings if r.object_id == object_id})


def render_search_result(query: Dict[str, Any], result: Dict[str, Any]) -> str:
    said = ", ".join(f"{k}={v!r}" for k, v in query.items() if v not in (None, "", "both"))
    head = f"Search ({said or 'no filters'}): {result['n_matched']} record(s) match " \
           f"({result['n_sightings_matched']} sighting(s), " \
           f"{result['n_absences_matched']} absence(s))."
    if result["n_matched"] == 0:
        return head + " Nothing in the log matches this search."
    if result["truncated"]:
        head += (f" Showing the newest {result['n_sightings_shown']} sighting(s) and "
                 f"{result['n_absences_shown']} absence(s); "
                 f"{result['n_sightings_hidden']} older sighting(s) and "
                 f"{result['n_absences_hidden']} older absence(s) are NOT shown - "
                 "narrow the day range to see them.")
    else:
        head += " Showing all of them, newest first."
    return head + "\n" + "\n".join(result["lines"])


# ------------------------------------------------------------- the prompting --

def opening_message(household: FrozenHousehold, log: ObservationLog, question: dict,
                    max_searches: int) -> str:
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
        "from looks it took. It keeps no notes at all. Instead it has the complete",
        "raw log of every look it has ever made, and a search tool over that log.",
        "",
        "The log holds two kinds of record:",
        "  a SIGHTING - the robot saw a named thing on a named spot, on a day, at a time.",
        "  an ABSENCE - the robot looked through a whole room and the named thing was",
        "               NOT anywhere in it. This is evidence too, and often the evidence",
        "               that something has moved.",
        "",
        f"The log runs from day 0 to day {log.freeze_day} and stops there: the robot has",
        "looked in one room a day at 13:00, after one walkthrough of the whole house on",
        "day 0. There is nothing in it about any later day.",
        "",
        f"Question: where is {question['object_id']} right now?",
        "",
        f"You may search the log up to {max_searches} time(s) before you answer. A search takes:",
        "  object_id   a thing's name or part of one (\"razor\" finds razor_nora)",
        "  room        a room name",
        "  place       a spot id or part of one",
        "  day_from    earliest day to include",
        "  day_to      latest day to include",
        "  what_kind   \"sightings\", \"absences\" or \"both\"",
        "Leave a field null to leave it unconstrained. Results come back newest first,",
        f"at most {RESULT_CAP} of them, and you are told when more matched than were shown.",
        "There are many more absences in the log than sightings, so a search for a thing",
        "with what_kind \"sightings\" is the quickest way to see everywhere it has been.",
        "",
        "Reply with JSON. Set what_next to \"search\" and fill in the fields you want,",
        "or set what_next to \"answer\" to stop searching and answer now.",
    ]
    return "\n".join(lines)


FINAL_TURN = ("No more searches. Answer from what the log showed you. "
              "Name exactly one spot from the list of spots above. " + CONF_SCALE)


@dataclass
class RawLogAnswer:
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
    n_searches: int
    searches: List[Dict[str, Any]]
    stopped_because: str
    n_observation_lines_seen: int
    places_the_searches_returned: List[str]
    n_model_calls: int


def answer_one_question(household: FrozenHousehold, log: ObservationLog,
                        client: LLMClient, question: dict, max_searches: int,
                        allowed: set) -> RawLogAnswer:
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": opening_message(household, log, question,
                                                            max_searches)}]
    searches: List[Dict[str, Any]] = []
    places_returned: List[str] = []
    n_lines_seen = 0
    n_model_calls = 0
    stopped = "used the whole budget"
    for turn in range(max_searches):
        text, _ = client.complete(messages, SEARCH_SCHEMA, max_tokens=400)
        n_model_calls += 1
        step = None
        if text:
            try:
                step = json.loads(text)
            except ValueError:
                step = None
        if not isinstance(step, dict):
            stopped = "the search step did not parse"
            break
        if step.get("what_next") != "search":
            stopped = "it chose to stop searching"
            break
        query = {"object_id": step.get("object_id"), "room": step.get("room"),
                 "place": step.get("place"), "day_from": step.get("day_from"),
                 "day_to": step.get("day_to"),
                 "what_kind": step.get("what_kind") or "both"}
        result = log.search(**query)
        rendered = render_search_result(query, result)
        n_lines_seen += result["n_shown"]
        places_returned.extend(p for p in result["shown_places"] if p)
        searches.append({"turn": turn + 1, "query": query,
                         "why": step.get("reasoning", ""),
                         "n_matched": result["n_matched"],
                         "n_shown": result["n_shown"],
                         "truncated": result["truncated"],
                         "observation_ids": result["shown_observation_ids"]})
        messages.append({"role": "assistant", "content": text})
        messages.append({"role": "user", "content": rendered})

    messages.append({"role": "user", "content": FINAL_TURN})
    text, _ = client.complete(messages, CONF_SCHEMA, max_tokens=400)
    n_model_calls += 1
    place, confidence, reasoning, status = parse_conf(text, allowed)
    true_place = household.true_place_for_question(question)
    return RawLogAnswer(
        question_id=question["question_id"], object_id=question["object_id"],
        object_class=question.get("object_class", ""), day=question["day_index"],
        time=question["t_query"], period=period_of_day(question["day_index"]),
        answer_place=place, true_place=true_place,
        correct=None if place is None else place == true_place,
        confidence=confidence, reasoning=reasoning, parse_status=status,
        n_searches=len(searches), searches=searches, stopped_because=stopped,
        n_observation_lines_seen=n_lines_seen,
        places_the_searches_returned=sorted(set(places_returned)),
        n_model_calls=n_model_calls)


# ------------------------------------------------------- the error partition --

def partition_the_errors(household: FrozenHousehold, log: ObservationLog,
                         answers: Sequence[RawLogAnswer]) -> Dict[str, Any]:
    """Of the questions it got wrong, where did the answer fail?

    Three cells, and they are not the same failure:

      the evidence was never gathered   the true spot never appears in the log at all,
                                        for this object. No amount of searching
                                        recovers an observation the robot never made,
                                        so this cell bounds every arm equally and is
                                        the sensing limit the curated arms also face;
      it never searched for it          the true spot IS in the log, but none of this
                                        question's own searches returned a sighting
                                        there. A retrieval failure;
      it saw it and answered otherwise  a search DID return a sighting at the true
                                        spot and the model named a different one. A
                                        reasoning failure.
    """
    cells = collections.Counter()
    rows: List[Dict[str, Any]] = []
    for a in answers:
        if a.correct is None or a.correct or not a.true_place:
            continue
        seen_places = log.places_this_object_was_ever_seen_in(a.object_id)
        in_log = a.true_place in seen_places
        returned = a.true_place in a.places_the_searches_returned
        cell = ("the evidence was never gathered" if not in_log else
                "it saw it and answered otherwise" if returned else
                "it never searched for it")
        cells[cell] += 1
        rows.append({"question_id": a.question_id, "object_id": a.object_id,
                     "day": a.day, "true_place": a.true_place,
                     "answer_place": a.answer_place, "cell": cell,
                     "n_searches": a.n_searches,
                     "places_this_object_was_ever_seen_in": seen_places})
    n = sum(cells.values())
    return {
        "n_wrong_at_shelf_level": n,
        "counts": dict(cells),
        "shares": {k: v / n for k, v in cells.items()} if n else {},
        "per_question": rows,
    }


def search_behaviour(answers: Sequence[RawLogAnswer], max_searches: int) -> Dict[str, Any]:
    n = len(answers)
    if not n:
        return {}
    calls = [a.n_model_calls for a in answers]
    searches = [a.n_searches for a in answers]
    fields = collections.Counter()
    for a in answers:
        for s in a.searches:
            for key, value in s["query"].items():
                if value not in (None, "", "both"):
                    fields[key] += 1
    return {
        "mean_model_calls_per_question": sum(calls) / n,
        "mean_searches_per_question": sum(searches) / n,
        "share_that_used_the_whole_search_budget":
            sum(1 for s in searches if s >= max_searches) / n,
        "share_that_searched_once_or_not_at_all": sum(1 for s in searches if s <= 1) / n,
        "share_that_never_searched": sum(1 for s in searches if s == 0) / n,
        "how_many_searches": dict(collections.Counter(searches)),
        "why_it_stopped": dict(collections.Counter(a.stopped_because for a in answers)),
        "which_fields_it_constrained_on": dict(fields),
        "mean_observation_lines_seen_per_question":
            sum(a.n_observation_lines_seen for a in answers) / n,
        "share_of_searches_that_were_truncated": (
            sum(1 for a in answers for s in a.searches if s["truncated"])
            / max(1, sum(searches))),
    }


# ---------------------------------------------------------------- the runner --

def run_raw_log_arm(household: FrozenHousehold, looks_path: pathlib.Path,
                    client: LLMClient, freeze_point: str, out_dir: pathlib.Path,
                    max_searches: int = DEFAULT_MAX_SEARCHES,
                    max_questions: Optional[int] = None,
                    allow_an_unfinished_log: bool = False) -> Dict[str, Any]:
    if freeze_point not in FREEZE_POINTS:
        raise ValueError(f"unknown freeze point {freeze_point!r}")
    plan = FREEZE_POINTS[freeze_point]
    log = ObservationLog(looks_path, plan["notes_through_day"])
    if log.n_look_records == 0:
        raise ValueError(f"{looks_path} holds no look records")

    # A freeze-day view of a log that is STILL BEING WRITTEN is only complete once the
    # log has passed that day. Read a day earlier and the arm silently answers from a
    # partial log, the accuracy is wrong, and nothing about the run looks broken - the
    # exact failure this project keeps paying for. So it is refused rather than warned
    # about, and the refusal names the day it is waiting for.
    freeze_day = plan["notes_through_day"]
    newest_day = log.newest_day_in_the_file      # the FILE, not the filtered view
    last_day_of_the_scenario = household.n_days - 1
    # Safe if the log has PASSED the freeze day, or if the log is finished (in which case
    # its last day is final even when it equals the freeze day).
    the_view_is_final = (newest_day > freeze_day
                         or newest_day >= last_day_of_the_scenario)
    if not the_view_is_final and not allow_an_unfinished_log:
        raise ValueError(
            f"{looks_path} reaches only day {newest_day}, and this freeze point needs "
            f"observations through day {freeze_day}. If the log is still being written its "
            f"day-{freeze_day} view is not final, and every number taken from it would "
            f"move later. Wait until the log passes day {freeze_day}, or pass "
            f"--allow-an-unfinished-log to measure something other than the study's "
            f"freeze point on purpose.")

    questions = questions_in_the_window(household, plan["questions_from_days"])
    if max_questions is not None:
        questions = spread_across_the_days(questions, max_questions)
    allowed = set(household.places)

    out_dir.mkdir(parents=True, exist_ok=True)
    answers: List[RawLogAnswer] = []
    # A tool-use arm is several blocking calls a question, so a cell is hours rather
    # than minutes. Progress is printed as it goes, with the running accuracy and the
    # calls per question, so a stalled or degenerate cell is visible in the first
    # minutes instead of at the end.
    import time
    started = time.time()
    for index, question in enumerate(questions, 1):
        answers.append(answer_one_question(household, log, client, question,
                                           max_searches, allowed))
        if index % 10 == 0 or index == len(questions):
            done = [a for a in answers if a.correct is not None]
            elapsed = time.time() - started
            print(f"  {household.name} {freeze_point[:22]:22s} "
                  f"{index:3d}/{len(questions)} "
                  f"running shelf accuracy "
                  f"{(sum(1 for a in done if a.correct) / len(done)) if done else 0:.1%} "
                  f"| {sum(a.n_model_calls for a in answers) / index:.2f} calls/question "
                  f"| {elapsed / index:.1f}s/question "
                  f"| {elapsed / 60:.0f} min in", flush=True)
        if index % 20 == 0 and index < len(questions):
            # A cell is hours long. Without this, a cell killed at hour four leaves
            # nothing on disk at all - the mirror image of the failure this project
            # keeps hitting, and just as expensive. The partial file is named so it
            # can never be mistaken for a finished cell, and `rglob
            # held_out_answers.json` does not pick it up.
            (out_dir / "answers_so_far_INCOMPLETE.json").write_text(json.dumps({
                "this_cell_is_still_running": True,
                "household": household.name, "arm": ARM_NAME,
                "freeze_point": freeze_point,
                "n_questions_answered_so_far": index,
                "n_questions_in_the_window": len(questions),
                "answers": [a.__dict__ for a in answers]}, indent=1))

    scored = [a for a in answers if a.correct is not None]
    result = {
        "household": household.name,
        "arm": ARM_NAME,
        "how_memory_is_written": "it is not written: the raw observation log is searched",
        "freeze_point": freeze_point,
        "notes_written_up_to_day": plan["notes_through_day"],
        "the_log_it_could_search": {
            "path": str(looks_path),
            "observations_on_or_before_day": log.freeze_day,
            "n_look_records_in_reach": log.n_look_records - log.n_look_records_withheld_as_future,
            "n_look_records_withheld_as_future": log.n_look_records_withheld_as_future,
            "n_sightings": len(log.sightings),
            "n_absence_records_after_collapsing_to_one_per_object_room_look":
                len(log.absences),
            "rooms_it_had_looked_in": log.rooms_looked_in,
        },
        "max_searches_allowed": max_searches,
        "the_freeze_day_view_of_the_log_is_final": the_view_is_final,
        "newest_day_in_the_log_file": newest_day,
        "n_questions_asked": len(answers),
        "n_questions_scored": len(scored),
        "n_correct": sum(1 for a in scored if a.correct),
        "share_correct": (sum(1 for a in scored if a.correct) / len(scored)) if scored else None,
        "n_unparsed": sum(1 for a in answers if a.correct is None),
        "how_it_searched": search_behaviour(answers, max_searches),
        "the_error_partition": partition_the_errors(household, log, answers),
        "answers": [a.__dict__ for a in answers],
    }
    (out_dir / "held_out_answers.json").write_text(json.dumps(result, indent=1))
    assay = sanity_assay(result)
    (out_dir / "sanity_assay.json").write_text(json.dumps(assay, indent=1))
    result["sanity_assay"] = assay
    return result


def looks_path_for(source: pathlib.Path, household_name: str, cell: str) -> pathlib.Path:
    return source / household_name / cell / "looks.jsonl"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--households", nargs="+", required=True)
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--source", type=pathlib.Path, default=DEFAULT_SOURCE,
                        help="the sweep whose looks.jsonl is the observation log. Read, "
                             "never written.")
    parser.add_argument("--cell", default=DEFAULT_CELL,
                        help="the path fragment under the household that holds "
                             "looks.jsonl. Under memory-guided search the log DEPENDS ON "
                             "THE NOTES - the robot searched where its notes sent it - so "
                             "each memory format has its own log and the cell names both "
                             "the looking arm and the format. This is a change from the "
                             "patrol sweep, where both formats shared one identical log.")
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/raw_log_baseline"))
    parser.add_argument("--cache", type=pathlib.Path,
                        default=pathlib.Path("llm_prior_cache/self_improve"))
    parser.add_argument("--freeze-points", nargs="+",
                        default=["did it learn the new routine"],
                        choices=list(FREEZE_POINTS))
    parser.add_argument("--max-searches", type=int, default=DEFAULT_MAX_SEARCHES)
    parser.add_argument("--max-questions", type=int, default=None,
                        help="SMOKE ONLY. Spread across the days of the window, never "
                             "the window's first N. The full window is 240 questions "
                             "and every reported number uses all of them.")
    parser.add_argument("--allow-an-unfinished-log", action="store_true",
                        help="read a log that has not yet passed the freeze day. Its "
                             "numbers are NOT the study's freeze point and will move; only "
                             "for deliberately measuring something else.")
    parser.add_argument("--tag", default=ARM_NAME,
                        help="the arm directory name under the household")
    args = parser.parse_args(argv)

    client = LLMClient(args.cache)
    for household_name in args.households:
        household = FrozenHousehold(args.banks / f"{household_name}.jsonl")
        looks_path = looks_path_for(args.source, household_name, args.cell)
        if not looks_path.exists():
            print(f"{household_name}: no log at {looks_path}", flush=True)
            continue
        # The scorer finds an arm's own look stream beside its answers, so put a copy
        # of exactly the log this arm searched where it will be found. Copied, never
        # moved: the source sweep belongs to the memory-factor run.
        arm_dir = args.out / household_name / args.tag
        arm_dir.mkdir(parents=True, exist_ok=True)
        # Atomically, because one process per freeze point means two processes can
        # copy the same household's log at the same moment and a torn file would be
        # a silent corruption of the thing the scorer reads.
        import os
        temporary = arm_dir / f"looks.jsonl.{os.getpid()}.tmp"
        temporary.write_bytes(looks_path.read_bytes())
        temporary.replace(arm_dir / "looks.jsonl")
        for freeze_point in args.freeze_points:
            where = arm_dir / freeze_point.replace(" ", "_")
            result = run_raw_log_arm(household, looks_path, client, freeze_point, where,
                                     args.max_searches, args.max_questions,
                                     args.allow_an_unfinished_log)
            behaviour = result["how_it_searched"]
            print(f"{household_name} | {freeze_point:34s} | "
                  f"{result['share_correct']:.1%} correct on "
                  f"{result['n_questions_scored']} of {result['n_questions_asked']} "
                  f"| {behaviour['mean_model_calls_per_question']:.2f} model calls and "
                  f"{behaviour['mean_searches_per_question']:.2f} searches per question",
                  flush=True)
            for concern in result["sanity_assay"]["concerns"]:
                print(f"      ASSAY CONCERN: {concern}", flush=True)
            partition = result["the_error_partition"]
            for cell, share in sorted(partition["shares"].items()):
                print(f"      of {partition['n_wrong_at_shelf_level']} wrong: "
                      f"{share:.0%} {cell}", flush=True)
    print(f"model calls {client.stats['calls']}, cache hits {client.stats['cached']}",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
