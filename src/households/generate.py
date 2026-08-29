#!/usr/bin/env python3
"""Generate one household from its control-file record: persona, story,
object movement, realization.

ADAPTED 2026-08-28 from src/revamp_v2/generate_dataset.py (source commit
0d7c3b5e3723d1bf1f46c99dae40780fbde0951e) for the self-contained
src/households package. Owned copy: edit in place. Same L1-L4 shape:

    L1  persona    one call    names, job titles, habits, inventory —
                               AROUND the fixed residents
    L2  story      one call    that person's every day, start to finish
                   per resident
    L3  movement   one call    per object: where it lives, where it
                               lands after each activity
    L4  realize    no LLM      seeded simulator writes the timeline

What changed from the storyfirst original, per the plan:
  - the record fixes WHO lives there (roles, exact ages, occupation
    categories, wfh) and WHEN they work and sleep (whole ATUS
    respondent-day tuples); the persona schema pins ids and ages, and
    the story prompt states the timing numbers as hard requirements.
    The model chooses wording, job titles inside the category, names,
    furniture detail and habits — never who lives there or when they
    work;
  - no cross-household contrast list in any prompt (slots no longer
    couple cache keys);
  - receptacle extras key on household ATTRIBUTES (a toddler brings a
    crib), not on a per-type table;
  - output lands in profiles/households/generated/<model_slug>/<hh>/;
  - spend is capped PER HOUSEHOLD (default $1.50): each household gets
    its own ledger and the guard is rebuilt per household.

Requires an OpenAI-compatible endpoint with strict structured outputs:

    GENERATION_ENDPOINT=https://api.openai.com \\
    OPENAI_API_KEY=... \\
        python -m households.generate --household hh_001 --model gpt-5.6-terra
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import pathlib

import yaml

from . import expand_calendar as xc
from . import grid
from . import normalize
from . import prompts
from . import schemas
from . import simulate as sim
from . import validate as checks

from dynamic_home_eqa.generation import llm_client
from dynamic_home_eqa.generation.cache import ResponseCache, make_seed
from dynamic_home_eqa.generation.hosted_spend import (SpendCapExceeded,
                                                      SpendGuard)

HERE = pathlib.Path(__file__).resolve().parent

PIPELINE_VERSION = "households-b1"
PER_HOUSEHOLD_CAP_USD = "1.50"
STORY_MAX_TOKENS = 20000
MOVEMENT_MAX_TOKENS = 20480
MOVEMENT_MAX_ATTEMPTS = 3
MOVEMENT_REASONING = "medium"


# ------------------------------------------------------------ L0 places --
# A household's furniture: a fixed template scaled by bedroom count, plus
# a few pieces particular to the household type.

def attribute_extras(slot: dict) -> list[dict]:
    """Extra furniture implied by who lives there — keyed on the
    record's attributes, not on a per-type table."""
    res = slot["residents_detail"]
    extras: list[dict] = []
    if any(r["role"] == "child" and r["employment"] == "preschool_child"
           for r in res):
        extras += [{"id": "crib_b2", "room": "bedroom_2"},
                   {"id": "high_chair_k1", "room": "kitchen"},
                   {"id": "toy_chest_l1", "room": "living"}]
    elif any(r["role"] == "child" for r in res):
        extras += [{"id": "toy_chest_l1", "room": "living"}]
    if any(r["role"] == "teen" for r in res):
        extras += [{"id": "game_shelf_l1", "room": "living"}]
    if any(r["age"] >= 65 for r in res):
        extras += [{"id": "reading_table_l1", "room": "living"},
                   {"id": "medicine_cabinet_ba1", "room": "bathroom"}]
    if any(r["schedule_type"] in ("fixed_night_shift", "rotating_shift")
           for r in res):
        extras += [{"id": "blackout_shelf_b1", "room": "bedroom"},
                   {"id": "blackout_shelf_b1", "room": "bedroom_1"}]
    if any(r["employment"] == "student" and r["role"] == "adult"
           for r in res):
        extras += [{"id": "game_shelf_l1", "room": "living"}]
    seen: set = set()
    out = []
    for e in extras:
        if e["id"] not in seen:
            seen.add(e["id"])
            out.append(e)
    return out



def base_receptacles(bedrooms: int) -> list[dict]:
    """The shared template. Ids follow `<thing>_<room-initial><n>`."""
    recs: list[dict] = []
    for i in range(1, bedrooms + 1):
        room = "bedroom" if bedrooms == 1 else f"bedroom_{i}"
        s = f"b{i}"
        recs += [{"id": f"bed_{s}", "room": room},
                 {"id": f"nightstand_{s}", "room": room},
                 {"id": f"desk_{s}", "room": room},
                 {"id": f"bedroom_floor_{s}", "room": room}]
    recs += [{"id": "couch_l1", "room": "living"},
             {"id": "coffee_table_l1", "room": "living"},
             {"id": "tv_stand_l1", "room": "living"},
             {"id": "bookshelf_l1", "room": "living"},
             {"id": "armchair_l1", "room": "living"},
             {"id": "counter_k1", "room": "kitchen"},
             {"id": "sink_k1", "room": "kitchen"},
             {"id": "cupboard_k1", "room": "kitchen"},
             {"id": "dish_rack_k1", "room": "kitchen"},
             {"id": "kitchen_table_k1", "room": "kitchen"},
             {"id": "chair_k1", "room": "kitchen"},
             {"id": "chair_k2", "room": "kitchen"},
             {"id": "bathroom_shelf_ba1", "room": "bathroom"},
             {"id": "towel_rack_ba1", "room": "bathroom"},
             {"id": "entry_table_e1", "room": "entry"},
             {"id": "entry_hook_e1", "room": "entry"},
             {"id": "entry_floor_e1", "room": "entry"}]
    return recs


def receptacles_for(slot: dict) -> list[dict]:
    recs = base_receptacles(int(slot.get("bedrooms", 2)))
    rooms = {r["room"] for r in recs}
    for extra in attribute_extras(slot):
        if extra["room"] in rooms:
            recs.append(dict(extra))
    return recs


# ------------------------------------------------------------- plumbing --

class _LongForm:
    """Raises the completion budget for one call. The client's default is
    sized for short responses; a month of days or a full object table
    needs far more."""

    def __init__(self, inner, max_tokens: int) -> None:
        self.inner = inner
        self.max_tokens = max_tokens

    def generate(self, system, user, schema, seed=None, temperature=0.7):
        return self.inner.generate(system, user, schema, seed=seed,
                                   temperature=temperature,
                                   max_tokens=self.max_tokens)

    def __getattr__(self, name):
        if name == "inner":
            raise AttributeError(name)
        return getattr(self.inner, name)


@contextlib.contextmanager
def _reasoning(effort: str):
    """Set the reasoning effort for the calls made inside this block."""
    key = "HOSTED_REASONING_EFFORT"
    old = os.environ.get(key)
    try:
        os.environ[key] = effort
        yield
    finally:
        if old is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old


def _take_reasoning(raw: dict, record: dict, key: str) -> dict:
    """Move the response's scratchpad into the build log. It is written
    first so the model deliberates before committing, and it never
    belongs in the artifact."""
    raw = dict(raw)
    if raw.get("reasoning"):
        record[key] = str(raw["reasoning"])[:2000]
    raw.pop("reasoning", None)
    return raw


def _minutes(clock: str) -> int:
    """"07:05" -> 425; a trailing "+1" adds a day."""
    plus = clock.count("+")
    h, m = clock.split("+")[0].split(":")
    return int(h) * 60 + int(m) + 1440 * plus


def _usage(client, cache, seed: int) -> dict | None:
    """Token counts and cost for a call. Live responses carry it on the
    client; replayed ones carry it in the cache record, so a rebuild
    keeps the provenance of the run that actually paid for it."""
    meta = getattr(client, "last_meta", None)
    if meta:
        return dict(meta)
    record = cache.get_record(seed) if cache else None
    if record and record.get("usage"):
        return {k: record[k] for k in
                ("model_snapshot", "finish_reason", "usage", "cost_usd")
                if k in record}
    return None


# ------------------------------------------------------------ L1 person --

PERSONA = prompts.PromptTemplate("persona_households_v1", """\
You are writing the profile of ONE fictional household for a research
simulation. The simulation will later animate it: objects will move
around the home over days and weeks, driven by what the residents do.
Right now we are only writing WHO lives here and WHAT objects they own.
Daily schedules with clock times come in a later step — do not write
any times of day or hour-by-hour routines.

The request FIXES the household's structure: how many residents, each
one's role, exact age, employment, work-schedule kind, and occupation
CATEGORY. Keep all of it exactly. What you invent: names, the specific
job title inside each given category, personalities, habits, how the
home is laid out and shared, and the object inventory. Make these
people specific and believable — not the first cliche the category
suggests.

Fields to produce (returned as JSON matching the provided schema):
household_id, household_type: as given, copy exactly.
residents: id/age as given; name, occupation (a SPECIFIC job title
  inside the given category — "pediatric nurse", not "healthcare";
  "retired", "student", or the school stage for non-workers),
  personality (2-3 traits that affect how they treat objects), habits
  (5-8 concrete habits about how they use and leave objects around the
  home; habits may involve another resident).
relationships: 2-3 sentences — who these people are to each other, how
  they divide chores, spaces and belongings, with at least one point of
  friction or coordination.
home_layout_notes: 2-3 sentences — rooms and surfaces each person uses
  most, who shares a bedroom, which spaces are shared.
daily_life_summary: 3-4 sentences, a typical day in plain words,
  STILL WITHOUT clock times; mention how the residents' days overlap or
  miss each other.
quirks: 0-2 ways this household differs from the stereotype of its
  kind.
object_inventory: choose classes only from the vocabulary in the
  request. Ids MUST begin with their class ("mug_marie", not
  "maries_mug"); personal objects carry the owner's name, shared or
  interchangeable ones a number index. Aim for 15-20 objects for a solo
  resident, plus roughly 4-6 per additional resident. Per-person items
  (phone, keys, wallet) exist per resident old enough to carry them,
  and each `role` says what the object is used for, where it tends to
  be left, and HOW IT TRAVELS if it leaves the house with its owner.

Respond only with valid JSON matching the provided schema.""")


def slot_digest(slot: dict) -> str:
    """Everything in the record that shapes a prompt, hashed into the
    cache tags: a changed constraint must never replay a stale cached
    response. Wave is excluded (it schedules, it does not prompt)."""
    core = {k: v for k, v in slot.items() if k != "wave"}
    return hashlib.sha256(
        json.dumps(core, sort_keys=True, default=str).encode()
    ).hexdigest()[:8]


def _requirements_block(slot: dict) -> str:
    """The fixed household structure, spelled out for the prompt."""
    lines = [f"archetype: {slot['archetype']}"
             + (f" with the {slot['overlay']} overlay"
                if slot.get("overlay") else "")]
    for i, r in enumerate(slot["residents_detail"], 1):
        bits = [f"resident_{i}: {r['role']}, age {r['age']},"
                f" {r['employment'].replace('_', ' ')}"]
        if r.get("occupation_category"):
            bits.append(f"occupation category: "
                        f"{r['occupation_category'].replace('_', ' ')}")
        sched = r["schedule_type"]
        if sched != "none":
            bits.append(f"work schedule kind: {sched.replace('_', ' ')}")
        if r.get("wfh"):
            bits.append("works from home")
        lines.append("  " + "; ".join(bits))
    return "\n".join(lines)


def persona_user_prompt(slot: dict, vocabulary: list[str]) -> str:
    return (
        f"household_id: {slot['household_id']}\n"
        f"household_type: {slot['household_type']}\n\n"
        f"Fixed structure (do not change any of it):\n"
        f"{_requirements_block(slot)}\n\n"
        f"Object vocabulary (choose classes from these; do not invent "
        f"new classes):\n[{', '.join(vocabulary)}]\n")


def build_persona_schema_pinned(slot: dict, vocabulary: list[str]) -> dict:
    """The shared persona schema with each resident's id and age pinned
    by position, so the model cannot drift from the record."""
    base = schemas.build_persona_schema(
        slot["household_id"], slot["household_type"],
        len(slot["residents_detail"]), vocabulary)
    residents = base["properties"]["residents"]
    item = residents.pop("items")
    pinned = []
    for i, spec in enumerate(slot["residents_detail"]):
        it = json.loads(json.dumps(item))
        it["properties"]["id"] = {"type": "string",
                                  "const": f"resident_{i + 1}"}
        it["properties"]["age"] = {"type": "integer",
                                   "const": int(spec["age"])}
        pinned.append(it)
    residents["prefixItems"] = pinned
    residents["items"] = False
    return base


def generate_persona(slot: dict, control: dict, client, cache,
                     force: bool) -> tuple[dict, str, int, str]:
    """(persona, canonical_yaml, seed, scratchpad). One call. Style
    problems reported by the normalizer are retryable."""
    schema = build_persona_schema_pinned(slot,
                                         control["object_vocabulary"])
    tag = (PERSONA.tag("persona", builder=True, schema=schema)
           + f"_a{slot_digest(slot)}")
    seed = make_seed(slot["household_id"], 0, tag)
    scratchpad: list[str] = []

    def _validate(parsed: dict) -> dict:
        parsed = dict(parsed)
        if parsed.get("reasoning"):
            scratchpad.append(str(parsed["reasoning"])[:2000])
        parsed.pop("reasoning", None)
        for r, spec in zip(parsed["residents"], slot["residents_detail"]):
            if int(r["age"]) != int(spec["age"]):
                raise ValueError(f"{r['id']}: age {r['age']} departs "
                                 f"from the record's {spec['age']}")
        log: list[str] = []
        canonical = normalize.canonicalize(parsed, log,
                                           slot["household_id"])
        problems = normalize.validate(normalize.strip_styles(canonical),
                                      slot["household_id"])
        if problems:
            raise ValueError("; ".join(problems))
        return canonical

    canonical = llm_client.generate_json(
        client, PERSONA.text, persona_user_prompt(
            slot, control["object_vocabulary"]),
        schema, seed=seed, stage=tag, cache=cache, force=force,
        validate=_validate)
    text = yaml.dump(canonical, Dumper=normalize.Dumper, sort_keys=False,
                     allow_unicode=True, width=78, indent=2,
                     default_flow_style=False)
    return (normalize.strip_styles(canonical), text, seed,
            scratchpad[-1] if scratchpad else "")


# ------------------------------------------------------------- L2 story --

STORY = prompts.PromptTemplate("storyfirst_month", """\
You write the lived days of ONE PERSON in a simulated household as a
concrete calendar: what they do, when, where — day by day, not as a
repeating template. You are writing for yourself: a later pass will use
this calendar to decide how the household's objects move, so it must be
the kind of specific, believable record a person's actual weeks leave.

What real weeks contain, and a weekly template misses:
- a recurring spine (work, school, sleep) that holds MOST days;
- weekly texture: weekends unlike weekdays, a laundry day, a groceries
  run, the gym nights that actually happen;
- storylike happenings that play out ACROSS days — a cold that keeps
  them home for two days, a visitor, a deadline-heavy week, an
  appointment interrupting a morning. Invent arcs the persona supports
  and let them show in the schedule, not just the summary.

Activity names come from a closed list. Pick by WHAT THE PERSON IS
DOING, never by the clock. Every day includes sleep. Trips out of the
house are written as they happen: a traveling block, then the
destination activity, then traveling home.

Time convention, followed exactly: within one day a person's blocks
must not overlap. A block that crosses midnight (a night shift, the
night's sleep) is written ONCE, on the day it STARTS, with `end` as the
clock time it actually ends the next morning — never restated on the
next day. The next day's first block begins at or after the crossing
block's end; sleep that crosses into a day's morning counts as that
day's sleep.

Write the anchors (sleep, work, meals) AND the small connective
activities a real day is full of — a coffee, a snack, medication, a
shower, taking out the bins, ten minutes of phone_time. Small blocks may
be 5-20 minutes. A real person's diary averages ~18 distinct episodes a
day; a day written as 5 long blocks is a summary, not a day.

Respond only with valid JSON matching the provided schema.""")

STORY_USER = """\
The household (persona, verbatim):

{persona}

FIXED schedule requirements (from real time-use survey respondents —
hard constraints, not suggestions; hit each stated clock time within
about 30 minutes on the days it applies, and keep the WEEKLY PATTERN it
describes):
{requirements}

Places in this home (`at` for each block; ELSEWHERE = out of the house):
{locations}

Activity names (the closed list — use the range of it where the persona
supports it; occasional chores and outings belong somewhere in {days}
days):
{vocab}

{others}

Write ALL {days} days (day 0 is a Monday; {weekday_map}) for {resident}
ONLY — {name}. For each day give `day`, a one-line `summary` of what the
day is in this person's story, and `blocks`: their whole day in 8-18
blocks with `resident` (always {resident}), `activity`, `start`, `end`
(HH:MM), `at`. Coordinate with what the others already have — shared
meals, lifts, who is home when — and keep your own arcs coherent across
the days.
"""




def _hhmm(minutes) -> str:
    m = int(minutes) % 1440
    return f"{m // 60:02d}:{m % 60:02d}"


def _tuple_line(day: dict, label: str) -> str:
    bits = []
    if day.get("wake") is not None:
        bits.append(f"wake ~{_hhmm(day['wake'])}")
    if (day.get("work_start") is not None
            and day.get("work_end") is not None
            and day.get("work_min", 0) >= 120):
        cross = " (crosses midnight)" if day["work_end"] < day["work_start"] else ""
        bits.append(f"work {_hhmm(day['work_start'])}-"
                    f"{_hhmm(day['work_end'])}{cross}")
    if day.get("sleep_min"):
        bits.append(f"sleep ~{day['sleep_min'] / 60:.1f}h total")
    return f"  {label}: " + (", ".join(bits) if bits else "no constraint")


SCHEDULE_PATTERNS = {
    "fixed_daytime": "workdays are Monday-Friday",
    "fixed_evening": "about 5 evening shifts a week, mostly weekdays",
    "fixed_night_shift": "about 5 night shifts a week; sleep follows "
                         "the shift, during the day",
    "irregular_gig": "3-5 gig work days a week on an IRREGULAR pattern "
                     "— vary the days and shift the times some, keeping "
                     "them in the neighbourhood of the stated block",
    "irregular_academic": "irregular academic hours: a mix of on-campus "
                          "days and work-from-home days, with odd "
                          "evening work blocks; no two weeks identical",
}


def timing_requirements(slot: dict) -> str:
    lines = []
    for i, r in enumerate(slot["residents_detail"], 1):
        rid = f"resident_{i}"
        sched = r["schedule_type"]
        head = f"{rid} ({r['role']}, {r['employment'].replace('_', ' ')}"
        if sched != "none":
            head += f", {sched.replace('_', ' ')}"
        if r.get("wfh"):
            head += ", WORKS FROM HOME: work blocks happen at home, not "
            head += "ELSEWHERE"
        head += "):"
        lines.append(head)
        if r["role"] == "child":
            blk = r.get("school_block")
            if blk:
                lines.append(f"  school days (Mon-Fri): out of the house "
                             f"{_hhmm(blk['start'])}-{_hhmm(blk['end'])}")
            else:
                lines.append("  preschool age: home unless taken along "
                             "by an adult")
            continue
        t = r.get("timing") or {}
        if sched == "rotating_shift":
            lines.append("  ROTATING shift — cycle through the three "
                         "phases below in multi-day stretches (2-4 days "
                         "each, with rest days at phase changes); say "
                         "which phase each day is in its summary:")
            for phase in ("daytime", "evening", "night"):
                day = t.get(f"workday_{phase}")
                if day:
                    lines.append(_tuple_line(day, f"  {phase} phase"))
        elif sched == "none":
            day = t.get("typical_day")
            if day:
                lines.append(_tuple_line(day, "typical day"))
        else:
            day = t.get("workday")
            if day:
                lines.append(_tuple_line(day, "workdays"))
            pattern = SCHEDULE_PATTERNS.get(sched)
            if pattern:
                lines.append(f"  pattern: {pattern}")
        off = t.get("dayoff")
        if off:
            lines.append(_tuple_line(off, "days off"))
    return "\n".join(lines)

OVERLAP_TOLERANCE_MIN = 15      # sub-15-minute nudges realize harmlessly


def overlap_problems(days_list: list[dict]) -> list[str]:
    """Violations of the authored time convention: overlapping blocks
    within a day, and blocks starting inside the previous day's
    crossing block (a restated overnight sleep or a re-listed shift
    tail — realization resolves overlaps by truncation, which silently
    rewrites the story, so the story must not contain them)."""
    out: list[str] = []
    carry = 0                    # previous day's overflow past midnight
    for day in days_list:
        blocks = sorted(day["blocks"], key=lambda b: _minutes(b["start"]))
        prev_end, prev_name = carry, "previous day's crossing block"
        day_carry = 0
        for b in blocks:
            s0, e0 = _minutes(b["start"]), _minutes(b["end"])
            if e0 <= s0:
                e0 += 1440
            if s0 < prev_end - OVERLAP_TOLERANCE_MIN:
                out.append(f"d{day['day']:02d} {b['start']} "
                           f"{b['activity']} overlaps {prev_name}")
            prev_end, prev_name = max(prev_end, e0), b["activity"]
            day_carry = max(day_carry, e0 - 1440)
        carry = day_carry
    return out


def build_story_schema(rid: str, receptacles: list[str], days: int) -> dict:
    """One resident's whole run. Day slot i is pinned to day index i, and
    the per-day block floor is part of the grammar."""
    block = {
        "type": "object", "additionalProperties": False,
        "required": ["resident", "activity", "start", "end", "at"],
        "properties": {
            "resident": {"type": "string", "const": rid},
            "activity": {"enum": prompts.ACTIVITY_VOCAB},
            "start": {"type": "string", "pattern": prompts.TIME_PATTERN},
            "end": {"type": "string", "pattern": prompts.TIME_PATTERN},
            "at": {"enum": receptacles + ["ELSEWHERE"]},
        },
    }

    def day_slot(i: int) -> dict:
        return {"type": "object", "additionalProperties": False,
                "required": ["day", "summary", "blocks"],
                "properties": {
                    "day": {"type": "integer", "const": i},
                    "summary": {"type": "string", "maxLength": 200},
                    "blocks": {"type": "array", "minItems": 8,
                               "maxItems": 18, "items": block}}}

    return {"type": "object", "additionalProperties": False,
            "required": ["days"],
            "properties": {"days": {
                "type": "array", "minItems": days, "maxItems": days,
                "prefixItems": [day_slot(i) for i in range(days)],
                "items": False}}}


def _written_so_far(persona: dict, months: dict) -> str:
    if not months:
        return ("You are the first person written for this household; "
                "the rest will be written around you.")
    names = {r["id"]: r["name"] for r in persona["residents"]}
    lines = ["Already written for this household — coordinate with it:"]
    for rid, days in months.items():
        lines.append(f"\n{rid} ({names.get(rid, rid)}):")
        for d in days:
            lines.append(f"  d{d['day']:02d}: {d['summary']}")
            lines.append("    " + "; ".join(
                f"{b['start']}-{b['end']} {b['activity']}@{b['at']}"
                for b in d["blocks"]))
    return "\n".join(lines)


def generate_story(slot, persona, persona_text, receptacles, days,
                   client, cache, force, log) -> list[dict]:
    """One call per resident, in order, each seeing everyone already
    written. Returns the merged household story."""
    residents = [r["id"] for r in persona["residents"]]
    names = {r["id"]: r["name"] for r in persona["residents"]}
    rec_ids = [r["id"] for r in receptacles]
    places = "\n".join(f"  {x}" for x in rec_ids + ["ELSEWHERE"])
    weekdays = ", ".join(f"{i}={n}" for i, n in enumerate(xc.DAY_NAMES))
    months: dict[str, list] = {}

    for index, rid in enumerate(residents):
        schema = build_story_schema(rid, rec_ids, days)
        tag = (STORY.tag("story_month", builder=True, schema=schema)
               + f"_a{slot_digest(slot)}")
        user = STORY_USER.format(
            persona=persona_text, requirements=timing_requirements(slot),
            locations=places,
            vocab=", ".join(prompts.ACTIVITY_VOCAB), days=days,
            others=_written_so_far(persona, months),
            resident=rid, name=names.get(rid, rid), weekday_map=weekdays)
        seed = make_seed(slot["household_id"], index, tag)

        def _validate(parsed: dict, _rid=rid) -> dict:
            got = sorted(d["day"] for d in parsed["days"])
            if got != list(range(days)):
                raise ValueError(
                    f"month for {_rid} covers {got[:5]}... ({len(got)} "
                    f"entries) — expected exactly days 0..{days - 1}")
            problems = overlap_problems(parsed["days"])
            if problems:
                raise ValueError(
                    f"{len(problems)} day-boundary violations for "
                    f"{_rid}, e.g. " + "; ".join(problems[:4]))
            return parsed

        parsed = llm_client.generate_json(
            _LongForm(client, STORY_MAX_TOKENS), STORY.text, user, schema,
            seed=seed, stage=tag, cache=cache, force=force,
            validate=_validate)
        months[rid] = parsed["days"]
        log.setdefault("story_calls", []).append(
            {"resident": rid, "seed": seed,
             "usage": _usage(client, cache, seed)})
        print(f"  story {rid}: "
              f"{sum(len(d['blocks']) for d in months[rid])} blocks "
              f"over {days} days")

    story = []
    for day in range(days):
        blocks = [dict(b) for rid in residents
                  for b in months[rid][day]["blocks"]]
        blocks.sort(key=lambda b: (b["start"], b["resident"]))
        story.append({"day": day,
                      "summary": months[residents[0]][day]["summary"],
                      "blocks": blocks})
    return story


# ---------------------------------------------------------- L3 movement --

def effective_activities(story: list[dict]) -> tuple[set, set]:
    """(at_home, trips) as realization will see them. A resident's
    consecutive out-of-house blocks are one trip, named for its longest
    leg, so the movement pass writes rules against names that survive."""
    def duration(b: dict) -> int:
        span = _minutes(b["end"]) - _minutes(b["start"])
        return span + 1440 if span <= 0 else span

    at_home: set = set()
    trips: set = set()
    per_resident: dict[str, list] = {}
    for day in story:
        for b in day["blocks"]:
            per_resident.setdefault(b["resident"], []).append(
                dict(b, _at=day["day"] * 1440 + _minutes(b["start"])))
    for blocks in per_resident.values():
        blocks.sort(key=lambda b: b["_at"])
        i = 0
        while i < len(blocks):
            if blocks[i]["at"] != xc.ELSEWHERE:
                if not any(s in blocks[i]["activity"]
                           for s in xc.SLEEP_TOKENS):
                    at_home.add(blocks[i]["activity"])
                i += 1
                continue
            j = i + 1
            while j < len(blocks) and blocks[j]["at"] == xc.ELSEWHERE:
                j += 1
            trips.add(max(blocks[i:j], key=duration)["activity"])
            i = j
    return at_home, trips


def activity_digest(story: list[dict], persona: dict) -> str:
    """What the movement pass conditions on: each activity with who does
    it, how often, and where."""
    at_home, trips = effective_activities(story)
    names = {r["id"]: r["name"] for r in persona["residents"]}
    rows: dict[str, dict] = {}
    for day in story:
        for b in day["blocks"]:
            activity = b["activity"]
            if activity not in at_home and activity not in trips:
                continue
            row = rows.setdefault(activity, {"n": 0, "who": set(), "at": {}})
            row["n"] += 1
            row["who"].add(names.get(b["resident"], b["resident"]))
            row["at"][b["at"]] = row["at"].get(b["at"], 0) + 1
    lines = []
    for activity in sorted(rows):
        row = rows[activity]
        spots = ", ".join(k for k, _ in
                          sorted(row["at"].items(), key=lambda kv: -kv[1])[:2])
        where = ("TRIP (out of the house; the dist says where things LAND "
                 "at the homecoming)" if activity in trips else f"at {spots}")
        lines.append(f"  {activity}: {row['n']}x by "
                     f"{', '.join(sorted(row['who']))} — {where}")
    return "\n".join(lines)


MOVEMENT = prompts.PromptTemplate("storyfirst_movement", """\
You are writing the OBJECT half of a simulated household: its calendar
already exists (the activity table in the request is what these people
actually do), and your job is what that life DOES to their things.

One entry per inventory object, in order. For each object:
- `home` — where it can usually be found; where a tidy-up returns it.
- `p_misplace` (per day, 0.1-0.4 for carried items) when its role
  suggests absent-minded drift; omit it for objects that do not drift.
- `rules` — AFTER-only: each rule names an `activity` from the table,
  `phase: after`, and a `dist` of 2-5 outcomes summing to 1 over where
  the object LANDS when that activity ends. While the activity runs the
  object is simply WITH the person (the simulator handles that leg).
  `NO_OP` mass is how "sometimes" and "rarely" are written — a vacuum
  that comes out one deep_clean in five is NO_OP 0.8, not a missing
  rule. `rules: []` stays the honest answer for an object nothing in
  this life touches.
- TRIP activities (marked in the table) are how carried things leave the
  house and come back: a wallet with `after work_away` pointing at its
  own home is real movement — carried out at departure, set back down at
  the homecoming. Give every carried item (phone, keys, wallet, bag) at
  least one trip rule for its owner's trips.
- Cover the at-home life too: most at-home activities in the table
  should appear in at least one object's rules — a home where every
  activity moves nothing is not a home. A couple of genuinely
  object-free activities are fine.
- NO TWO OBJECTS share identical rules; `cites` comes first in every
  rule, one short clause, written before you choose numbers.

Respond only with valid JSON matching the provided schema.""")

MOVEMENT_USER = """\
The household (persona, verbatim):

{persona}

What these people actually do ({days} days, from their written story):
{digest}

Places in this home:
{places}

Write the movement entry for every object in the inventory, in order.
"""

# Appended verbatim on retry; the exact bytes are part of the cache key.
UNCOVERED_RETRY = (
    "\n\nA previous attempt left these at-home activities "
    "with NO object rule at all:\n"
    "{missed}"
    "\nFor each, either give some object a rule naming it "
    "(a shower moves a towel; a video_call moves a laptop; "
    "waking moves a phone off the nightstand), or leave it "
    "out only because this household owns nothing that "
    "activity would touch. Keep everything else as you had "
    "it.\n")


def uncovered_at_home(story: list[dict], object_rules: list[dict]) -> list[str]:
    """At-home activities no object rule names."""
    at_home, _ = effective_activities(story)
    bound = {r["activity"] for entry in object_rules
             for r in entry.get("rules") or []}
    return sorted(at_home - bound)


def check_coverage(story: list[dict], object_rules: list[dict]) -> list[str]:
    """A home where nothing responds to what people do is not a home.
    A few object-free activities are allowed; a majority is not."""
    at_home, _ = effective_activities(story)
    missed = uncovered_at_home(story, object_rules)
    allowed = max(checks.MIN_ALLOWED_UNCOVERED,
                  checks.MAX_UNCOVERED_FRACTION * len(at_home))
    if len(missed) > allowed:
        return [f"coverage: {len(missed)} of {len(at_home)} at-home story "
                f"activities appear in no object rule "
                f"({missed[:6]}{'...' if len(missed) > 6 else ''}; "
                f"tolerance {allowed:.1f})"]
    return []


def generate_movement(slot, persona, persona_text, receptacles, story, days,
                      client, cache, force, log,
                      effort: str = MOVEMENT_REASONING):
    """One call, retried with the coverage gap named. Returns
    (object_rules, program) or (None, None) when attempts run out."""
    at_home, trips = effective_activities(story)
    params = sim.load_params()
    object_ids = [o["id"] for o in persona["object_inventory"]]
    rec_ids = [r["id"] for r in receptacles]
    resident_ids = [r["id"] for r in persona["residents"]]
    schema = schemas.build_objects_schema(
        slot["household_id"], resident_ids, object_ids, rec_ids, days,
        params, sorted(at_home | trips))
    tag = (MOVEMENT.tag("movement", builder=True, schema=schema)
           + f"_r{effort}_a{slot_digest(slot)}")
    user = MOVEMENT_USER.format(
        persona=persona_text, days=days,
        digest=activity_digest(story, persona),
        places="\n".join(f"  {r}" for r in rec_ids))
    retry_note = ""

    for attempt in range(MOVEMENT_MAX_ATTEMPTS):
        # The retry note changes the response, so it changes the cache key.
        attempt_tag = tag + ("_h" + hashlib.sha256(
            retry_note.encode()).hexdigest()[:8] if retry_note else "")
        seed = make_seed(slot["household_id"], 0, attempt_tag, attempt)
        record: dict = {"attempt": attempt, "seed": seed, "effort": effort,
                        "hinted": bool(retry_note)}
        try:
            with _reasoning(effort):
                raw = llm_client.generate_json(
                    _LongForm(client, MOVEMENT_MAX_TOKENS), MOVEMENT.text,
                    user + retry_note, schema, seed=seed, stage=attempt_tag,
                    cache=cache, force=force)
        except SpendCapExceeded:
            raise
        except Exception as e:
            record["failures"] = [f"generation: {e!r}"[:300]]
            log.setdefault("movement_attempts", []).append(record)
            continue

        raw = _take_reasoning(raw, record, "reasoning")
        object_rules = raw["object_rules"]
        program = assemble_program(slot, persona, receptacles, story,
                                   object_rules, days)
        failures = (checks.check_referential(program, persona)
                    + checks.check_reachability(program)
                    + check_coverage(story, object_rules))
        record["failures"] = failures
        record["uncovered_at_home"] = uncovered_at_home(story, object_rules)
        record["usage"] = _usage(client, cache, seed)
        log.setdefault("movement_attempts", []).append(record)
        if not failures:
            return object_rules, program
        if record["uncovered_at_home"]:
            retry_note = UNCOVERED_RETRY.format(
                missed="\n".join(f"  {a}"
                                  for a in record["uncovered_at_home"]))
    return None, None


# ------------------------------------------------------------ L4 realize --

def assemble_program(slot, persona, receptacles, story, object_rules,
                     days: int) -> dict:
    """The realization input: every story block as a dated entry, plus
    the movement rules. Timing variation is not added here — the story
    already wrote each day differently."""
    jitter = sim.load_params()["jitter_scale"]
    scale = round(min(max(1.0, jitter["min"]), jitter["max"]), 2)
    dated = []
    for day in story:
        dated.append({
            "day": day["day"], "note": day.get("summary", ""),
            "patch": {"add": [
                {"resident": b["resident"], "activity": b["activity"],
                 "start": b["start"], "end": b["end"], "at": b["at"],
                 "jitter": "routine", "skip_p": 0.0}
                for b in day["blocks"]]}})
    return {
        "household": slot["household_id"],
        "household_type": slot["household_type"],
        "source_persona": "persona.yaml",
        "object_semantics": xc.AFTER_ONLY_V3,
        "object_owners": {o["id"]: o["owner"]
                          for o in persona["object_inventory"]},
        "days": days, "day0": "Monday",
        "residents": [{"id": r["id"], "jitter_scale": scale}
                      for r in persona["residents"]],
        "receptacles": [dict(r) for r in receptacles],
        "sleep_schedule": [], "weekly_blocks": [],
        "object_rules": object_rules, "activities": [],
        "arc_events": dated,
    }


def realize(hh_dir: pathlib.Path, program: dict, story: list[dict],
            object_rules: list[dict], model: str, days: int,
            seed: int) -> dict:
    """Run the seeded simulator and write the timeline. No LLM."""
    engine = sim.load_v1()
    params = sim.load_params()
    log, hourly, blocks, stats, _acts, motions = sim.simulate_program(
        program, days, seed, sa=engine, params=params)
    sim.tag_event_kinds(log)
    carry = params.get("carry_on_departure", {})
    stats["carry_rehome_suppressed"] = sim.suppress_carry_rehome(
        log, hourly, float(carry.get("carry_rehome_min", 0)))
    timeline = hh_dir / f"timeline_seed{seed}"
    engine.write_outputs(timeline, motions, log, hourly, blocks, stats,
                         days, seed, hh_dir)
    (hh_dir / "expanded_motions.yaml").write_text(
        "# GENERATED — object homes and per-activity rules in the shape\n"
        "# the simulator and the viewer read.\n"
        + yaml.safe_dump(motions, sort_keys=False, width=100,
                         allow_unicode=True))
    at_home, trips = effective_activities(story)
    meta = json.loads((timeline / "meta.json").read_text())
    meta.update({"engine": "storyfirst", "pipeline": PIPELINE_VERSION,
                 "model": model,
                 "n_story_activities": len(at_home | trips),
                 "effective_trips": sorted(trips),
                 "uncovered_at_home": uncovered_at_home(story,
                                                        object_rules)})
    (timeline / "meta.json").write_text(json.dumps(meta, indent=2))
    return meta


# --------------------------------------------------------------- driver --

def build_household(slot, control, out_root: pathlib.Path, model: str,
                    days: int, seed: int, client, cache, force) -> bool:
    hh_dir = out_root / slot["household_id"]
    hh_dir.mkdir(parents=True, exist_ok=True)
    receptacles = receptacles_for(slot)
    log: dict = {"household": slot["household_id"],
                 "household_type": slot["household_type"],
                 "archetype": slot["archetype"], "overlay": slot["overlay"],
                 "variant": slot["variant"], "wave": slot["wave"],
                 "model": model, "pipeline": PIPELINE_VERSION, "days": days,
                 "prompts": {t.name: t.version
                             for t in (PERSONA, STORY, MOVEMENT)}}
    aborted = None
    try:
        persona, persona_text, persona_seed, scratchpad = generate_persona(
            slot, control, client, cache, force)
        log["persona_seed"] = persona_seed
        log["persona_reasoning"] = scratchpad
        (hh_dir / "persona.yaml").write_text(persona_text)

        story = generate_story(slot, persona, persona_text, receptacles,
                               days, client, cache, force, log)
        (hh_dir / "story.yaml").write_text(
            "# GENERATED — every resident's days, one LLM call per\n"
            "# resident, merged.\n"
            + yaml.safe_dump({"household": slot["household_id"],
                              "days": story}, sort_keys=False,
                             allow_unicode=True, width=100))

        object_rules, program = generate_movement(
            slot, persona, persona_text, receptacles, story, days,
            client, cache, force, log)
    except SpendCapExceeded as e:
        aborted, object_rules, program = e, None, None
    except Exception as e:
        log["failed"] = repr(e)[:400]
        (hh_dir / "build_log.json").write_text(json.dumps(log, indent=2))
        print(f"{slot['household_id']}: FAILED ({type(e).__name__})")
        return False

    if getattr(client, "hosted", False):
        log["hosted"] = {"model_snapshot": getattr(client, "snapshot", None),
                         "spend": client.guard.summary()}
    if aborted is not None:
        log["aborted"] = str(aborted)
        (hh_dir / "build_log.json").write_text(json.dumps(log, indent=2))
        raise aborted
    if program is None:
        (hh_dir / "build_log.json").write_text(json.dumps(log, indent=2))
        print(f"{slot['household_id']}: FAILED (movement pass exhausted "
              f"{MOVEMENT_MAX_ATTEMPTS} attempts)")
        return False

    (hh_dir / "object_movement.yaml").write_text(
        "# GENERATED — per object: where it lives, how often it drifts,\n"
        "# and where it lands after each activity.\n"
        + yaml.safe_dump({"object_rules": object_rules}, sort_keys=False,
                         width=100, allow_unicode=True))
    (hh_dir / "program.yaml").write_text(
        "# GENERATED — the realization input: the story's days as dated\n"
        "# entries, plus the movement rules.\n"
        + yaml.safe_dump(program, sort_keys=False, width=100,
                         allow_unicode=True))
    meta = realize(hh_dir, program, story, object_rules, model, days, seed)
    log["uncovered_at_home"] = uncovered_at_home(story, object_rules)
    report = checks.write_attribute_check(hh_dir, slot, days, seed)
    log["attribute_advisories"] = report["advisories"]
    if report["advisories"]:
        print(f"  attribute advisories ({len(report['advisories'])}):")
        for a in report["advisories"]:
            print(f"    - {a}")
    (hh_dir / "build_log.json").write_text(json.dumps(log, indent=2))
    print(f"{slot['household_id']}: OK — {meta['n_events']} events, "
          f"{meta['n_story_activities']} activities -> {hh_dir}")
    return True


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--household", help="e.g. hh_001")
    group.add_argument("--all", action="store_true")
    ap.add_argument("--model", default=os.environ.get("GENERATION_MODEL",
                                                      "gpt-5.6-terra"))
    ap.add_argument("--out-root", type=pathlib.Path, default=None)
    ap.add_argument("--days", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--force", action="store_true",
                    help="regenerate instead of replaying cached responses")
    args = ap.parse_args()

    control = yaml.safe_load(
        (grid.DATA_DIR / "control.yaml").read_text())
    days = args.days or int(control["days"])
    slug = llm_client.model_slug(args.model)
    out_root = args.out_root or grid.DATA_DIR / "generated" / slug
    cache = ResponseCache(
        args.cache_dir
        or f"/tmp/dynamic-home-eqa-gen-cache-households-{slug}")
    # the guard reads its rate table from this package's owned copy —
    # nothing under src/revamp_v2 is consulted
    os.environ.setdefault("HOSTED_RATES_YAML",
                          str(HERE / "hosted_rates.yaml"))
    os.environ.setdefault("HOSTED_SPEND_CAP", PER_HOUSEHOLD_CAP_USD)
    client = llm_client._get_client(args.model)
    if not getattr(client, "hosted", False):
        raise SystemExit(
            "this pipeline needs strict structured outputs — set "
            "GENERATION_ENDPOINT=https://api.openai.com")

    slots = control["households"]
    if not args.all:
        slots = [s for s in slots
                 if s["household_id"] == args.household]
        if not slots:
            raise SystemExit(f"no household matches {args.household!r}")
    results = []
    for slot in slots:
        # per-household cap: fresh ledger, guard rebuilt so the cap
        # bounds THIS household, not the whole run
        os.environ["HOSTED_SPEND_LEDGER"] = (
            f"/tmp/dynamic-home-eqa-households-spend-"
            f"{slug}-{slot['household_id']}.json")
        client.guard = SpendGuard.from_env()
        try:
            results.append(build_household(
                slot, control, out_root, args.model, days, args.seed,
                client, cache, args.force))
        except SpendCapExceeded as e:
            print(f"{slot['household_id']}: ABORTED at its own cap: {e}")
            results.append(False)
    raise SystemExit(0 if all(results) else 1)


if __name__ == "__main__":
    _main()
