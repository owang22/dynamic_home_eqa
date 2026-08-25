#!/usr/bin/env python3
"""storyfirst: the simplified story-first pipeline.

    persona -> story (one call per RESIDENT) -> movement pass -> realization

Three LLM stages instead of six. The old L2 (calendar / object_rules /
special_events) is gone: the story IS the schedule, one-off happenings are
just days the story wrote, and object movement is authored ONCE, after the
story exists, against the activities the story actually contains — post
trip-merge, so a rule can never orphan on a commute name (the failure the
expander's chain-union had to compensate for; here it is fixed at the
root, because authoring order finally matches information order).

Stages, one household:
  L0  receptacles_for(slot)  — deterministic template scaled by bedrooms,
      now with household-TYPE extras (toy chest, crib, ...). The leak
      audit is retired, so type-aware furniture is no longer forbidden.
  L1  persona                — one call, generate.generate_persona
      verbatim, NO leak audit.
  L2  story                  — one call per resident, each authoring that
      person's ENTIRE run of days in one response (day slots pinned by
      prefixItems, so a missing or duplicated day is unwritable, and the
      8-block-per-day floor is schema, not prose). Residents are written
      sequentially, each conditioned on everyone already written — the
      recap mechanism for free, inside the context window.
  L3  movement pass          — one call (retried on gate failure)
      authoring object_movement.yaml: per object its home, drift rate and
      after-rules, with the activity enum pinned to the story's OWN
      effective activities (trips already merged to their dominant name).
      Gated by the same referential/reachability lints as revamp_v2 plus
      a thresholded story-coverage check.
  L4  realization            — deterministic: the story becomes day-patch
      adds over an otherwise empty program (the same vehicle the
      story_calendar arm used), expand_calendar + the unchanged v1
      simulator produce timeline_seed<N>/.

Hosted-only: the per-resident story call relies on server-side
structured outputs (a thinking-mode month does not fit a local think
budget). Both hosted backends work — OpenAI and Gemini's
OpenAI-compatibility layer — and the client picks its own schema dialect,
so nothing in this module is backend-specific.

NOTE for the Gemini dialect: its schema subset has no prefixItems, so the
day-slot pinning below degrades to a plain array of days whose `day`
index is a bounded integer. Missing or duplicated days therefore become
possible again and are caught by the ORIGINAL-schema re-validation in
llm_client._hosted_check (a retry, never a bad artifact) plus the
explicit day-coverage check in generate_story().

Usage:
  GENERATION_ENDPOINT=https://api.openai.com OPENAI_API_KEY=... \
      python src/revamp_v2/storyfirst.py --household hh2 --model gpt-5.6-terra
  GENERATION_ENDPOINT=https://generativelanguage.googleapis.com \
      GEMINI_API_KEY=... python src/revamp_v2/storyfirst.py \
      --household hh2 --model gemini-3.7-flash
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT / "src"))

import expand_calendar as xc                                  # noqa: E402
import generate as gen                                        # noqa: E402
import prompts                                                # noqa: E402
import schemas                                                # noqa: E402
import simulate as sim                                        # noqa: E402
import story_driven as sd                                     # noqa: E402
import validate as v2v                                        # noqa: E402

from dynamic_home_eqa.generation import llm_client            # noqa: E402
from dynamic_home_eqa.generation.cache import (               # noqa: E402
    ResponseCache, make_seed)
from dynamic_home_eqa.generation.hosted_spend import (        # noqa: E402
    SpendCapExceeded)

PIPELINE_VERSION = "storyfirst-a1"
MOVEMENT_MAX_ATTEMPTS = 3

# ------------------------------------------------------------------ L0 --
# Household-type extras on top of the bedroom-scaled template. The leak
# audit is retired (nothing downstream classifies type from furniture any
# more), so realism wins: a family has a toy chest, a toddler home a crib
# and high chair. Isolating furniture leakage is an ABLATION study now,
# not a standing constraint. Ids follow the v1 <thing>_<room-initial><n>
# convention; rooms must be ones the base template already names.
TYPE_RECEPTACLE_EXTRAS = {
    "family_teen_and_child": [
        {"id": "toy_chest_l1", "room": "living"}],
    "couple_with_toddler": [
        {"id": "crib_b2", "room": "bedroom_2"},
        {"id": "high_chair_k1", "room": "kitchen"},
        {"id": "toy_chest_l1", "room": "living"}],
    "single_parent_teens": [
        {"id": "game_shelf_l1", "room": "living"}],
    "retired_couple": [
        {"id": "reading_table_l1", "room": "living"},
        {"id": "medicine_cabinet_ba1", "room": "bathroom"}],
    "night_shift_worker_solo": [
        {"id": "blackout_shelf_b1", "room": "bedroom"}],
    "college_roommates": [
        {"id": "game_shelf_l1", "room": "living"}],
}


def receptacles_for(slot: dict) -> list[dict]:
    recs = gen.synthetic_receptacles(int(slot.get("bedrooms", 2)))
    rooms = {r["room"] for r in recs}
    for extra in TYPE_RECEPTACLE_EXTRAS.get(slot["household_type"], []):
        if extra["room"] in rooms:            # never invent a room
            recs.append(dict(extra))
    return recs


# ------------------------------------------------------------------ L2 --
MONTH_SYSTEM = prompts.PromptTemplate("storyfirst_month", """\
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
DOING, never by the clock. Every day includes sleep. If a block crosses
midnight, write its end as the clock time it actually ends the next
morning. Trips out of the house are written as they happen: a traveling
block, then the destination activity, then traveling home.

Write the anchors (sleep, work, meals) AND the small connective
activities a real day is full of — a coffee, a snack, medication, a
shower, taking out the bins, ten minutes of phone_time. Small blocks may
be 5-20 minutes. A real person's diary averages ~18 distinct episodes a
day; a day written as 5 long blocks is a summary, not a day.

Respond only with valid JSON matching the provided schema.""")

MONTH_USER = """\
The household (persona, verbatim):

{persona}

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


def build_month_schema(rid: str, receptacles: list[str], days: int) -> dict:
    """One resident's whole run: day slot i is PINNED to day index i
    (prefixItems — a missing or repeated day is unwritable), and the
    8-block floor is schema, not prose."""
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


def _others_context(persona: dict, months: dict) -> str:
    if not months:
        return ("You are the first person written for this household; "
                "the rest will be written around you.")
    lines = ["Already written for this household — coordinate with it:"]
    names = {r["id"]: r["name"] for r in persona["residents"]}
    for rid, days in months.items():
        lines.append(f"\n{rid} ({names.get(rid, rid)}):")
        for d in days:
            lines.append(f"  d{d['day']:02d}: {d['summary']}")
            lines.append("    " + "; ".join(
                f"{b['start']}-{b['end']} {b['activity']}@{b['at']}"
                for b in d["blocks"]))
    return "\n".join(lines)


def generate_story(slot, persona, persona_text, receptacles, days,
                   client, cache, force, log):
    """One call per resident, sequential, each conditioned on everyone
    already written. Returns merged story: [{day, summary, blocks}]."""
    residents = [r["id"] for r in persona["residents"]]
    names = {r["id"]: r["name"] for r in persona["residents"]}
    rec_ids = [r["id"] for r in receptacles]
    loc_lines = "\n".join(f"  {x}" for x in rec_ids + ["ELSEWHERE"])
    import freeform_motion as fm
    wmap = ", ".join(f"{i}={n}" for i, n in enumerate(fm.DAY_NAMES))
    months: dict[str, list] = {}
    for idx, rid in enumerate(residents):
        schema = build_month_schema(rid, rec_ids, days)
        tag = MONTH_SYSTEM.tag("story_month", builder=True, schema=schema)
        user = MONTH_USER.format(
            persona=persona_text, locations=loc_lines,
            vocab=", ".join(prompts.ACTIVITY_VOCAB), days=days,
            others=_others_context(persona, months),
            resident=rid, name=names.get(rid, rid), weekday_map=wmap)
        seed = make_seed(slot["household_id"], idx, tag)

        def _validate(parsed, _rid=rid):
            import jsonschema
            jsonschema.validate(parsed, schema)
            # Day coverage, explicitly: prefixItems pins day i to slot i
            # on the OpenAI dialect, but the Gemini subset has no
            # prefixItems, so the guarantee must also be checked here —
            # a missing or duplicated day is a retryable bad sample, not
            # a silently short month.
            got = [d["day"] for d in parsed["days"]]
            if sorted(got) != list(range(days)):
                raise ValueError(
                    f"month for {_rid} covers {sorted(set(got))[:5]}... "
                    f"({len(got)} entries) — expected exactly days "
                    f"0..{days - 1}")
            return parsed

        parsed = sd.generate_story_json(
            client, MONTH_SYSTEM.text, user, seed=seed, stage=tag,
            cache=cache, force=force, validate=_validate,
            max_tokens=sd.STORY_MAX_TOKENS, schema=schema)
        months[rid] = parsed["days"]
        log.setdefault("story_calls", []).append(
            {"resident": rid, "seed": seed,
             "usage": dict(client.last_meta or {})
             if getattr(client, "hosted", False) else None})
        print(f"  story {rid}: {sum(len(d['blocks']) for d in months[rid])}"
              f" blocks over {days} days")
    story = []
    anchor = residents[0]
    for d in range(days):
        blocks = [dict(b) for rid in residents
                  for b in months[rid][d]["blocks"]]
        blocks.sort(key=lambda b: (b["start"], b["resident"]))
        story.append({"day": d, "summary": months[anchor][d]["summary"],
                      "blocks": blocks})
    return story


# ------------------------------------------------------------------ L3 --

def effective_activities(story: list[dict]) -> tuple[set, set]:
    """(at_home, trips) as the EXPANDER will see them: per resident,
    consecutive ELSEWHERE blocks merge into one trip named for its
    DOMINANT (longest) member — so the movement pass authors rules
    against names that actually survive, and a rule can never orphan on
    a commute. Mirrors expand_calendar's away-chain merge."""
    def dur(b):
        d = (xc._minutes(b["end"]) - xc._minutes(b["start"]))
        return d + 1440 if d <= 0 else d
    at_home, trips = set(), set()
    per: dict[str, list] = {}
    for d in story:
        for b in d["blocks"]:
            per.setdefault(b["resident"], []).append(
                dict(b, _abs=d["day"] * 1440 + xc._minutes(b["start"])))
    for rid, mine in per.items():
        mine.sort(key=lambda b: b["_abs"])
        i = 0
        while i < len(mine):
            if mine[i]["at"] != xc.ELSEWHERE:
                if not any(s in mine[i]["activity"]
                           for s in xc.SLEEP_TOKENS):
                    at_home.add(mine[i]["activity"])
                i += 1
                continue
            j = i + 1
            while j < len(mine) and mine[j]["at"] == xc.ELSEWHERE:
                j += 1
            trips.add(max(mine[i:j], key=dur)["activity"])
            i = j
    return at_home, trips


def activity_digest(story: list[dict], persona: dict) -> str:
    """What the movement pass conditions on: each effective activity with
    who does it, how often, and where — compact, not the whole story."""
    at_home, trips = effective_activities(story)
    names = {r["id"]: r["name"] for r in persona["residents"]}
    rows: dict[str, dict] = {}
    for d in story:
        for b in d["blocks"]:
            a = b["activity"]
            if a not in at_home and a not in trips:
                continue
            r = rows.setdefault(a, {"n": 0, "who": set(), "at": {}})
            r["n"] += 1
            r["who"].add(names.get(b["resident"], b["resident"]))
            r["at"][b["at"]] = r["at"].get(b["at"], 0) + 1
    lines = []
    for a in sorted(rows):
        r = rows[a]
        spots = ", ".join(k for k, _ in sorted(r["at"].items(),
                                               key=lambda kv: -kv[1])[:2])
        kind = "TRIP (out of the house; the dist says where things LAND "\
               "at the homecoming)" if a in trips else f"at {spots}"
        lines.append(f"  {a}: {r['n']}x by {', '.join(sorted(r['who']))} "
                     f"— {kind}")
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


@contextlib.contextmanager
def _reasoning(effort: str | None):
    """Per-stage reasoning override (the adapter reads the env per call)."""
    key = "HOSTED_REASONING_EFFORT"
    old = os.environ.get(key)
    try:
        if effort:
            os.environ[key] = effort
        yield
    finally:
        if old is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old


def storyfirst_coverage(story, object_rules) -> list[str]:
    """The at-home coverage check, storyfirst edition: same thresholds as
    validate.py, computed over the STORY's effective at-home activities
    (the program's weekly_blocks are empty here by design)."""
    at_home, _ = effective_activities(story)
    bound = {r["activity"] for e in object_rules
             for r in e.get("rules") or []}
    uncovered = sorted(at_home - bound)
    allowed = max(v2v.MIN_ALLOWED_UNCOVERED,
                  v2v.MAX_UNCOVERED_FRACTION * len(at_home))
    if len(uncovered) > allowed:
        return [f"coverage: {len(uncovered)} of {len(at_home)} at-home "
                f"story activities appear in no object rule "
                f"({uncovered[:6]}{'...' if len(uncovered) > 6 else ''}; "
                f"tolerance {allowed:.1f})"]
    return []


def story_to_program(slot, persona, receptacles, story, object_rules,
                     days: int) -> dict:
    """The realization vehicle: an otherwise-empty program whose every
    story block is a dated one-off add (expand_calendar consumes these as
    day patches — the key is `arc_events` for v1-interface compatibility,
    nothing narrative about it here). Jitter/skip are constants: the
    story already wrote its own day-to-day variation."""
    js = sim.load_params()["jitter_scale"]
    mid = round(min(max(1.0, js["min"]), js["max"]), 2)
    arcs = []
    for d in story:
        adds = [{"resident": b["resident"], "activity": b["activity"],
                 "start": b["start"], "end": b["end"], "at": b["at"],
                 "jitter": "routine", "skip_p": 0.0}
                for b in d["blocks"]]
        arcs.append({"day": d["day"], "note": d.get("summary", ""),
                     "patch": {"add": adds}})
    return {
        "household": slot["household_id"],
        "household_type": slot["household_type"],
        "source_persona": "persona.yaml",
        "object_semantics": xc.AFTER_ONLY_V3,
        "object_owners": {o["id"]: o["owner"]
                         for o in persona["object_inventory"]},
        "days": days, "day0": "Monday",
        "residents": [{"id": r["id"], "jitter_scale": mid}
                      for r in persona["residents"]],
        "receptacles": [dict(r) for r in receptacles],
        "sleep_schedule": [], "weekly_blocks": [],
        "object_rules": object_rules, "activities": [],
        "arc_events": arcs,
    }


def generate_movement(slot, persona, persona_text, receptacles, story,
                      days, client, cache, force, log,
                      effort: str = "medium"):
    """The movement pass: one call, retried with distinct seeds on gate
    failure. Returns (object_rules, program) or (None, None)."""
    at_home, trips = effective_activities(story)
    scheduled = sorted(at_home | trips)
    params = sim.load_params()
    object_ids = [o["id"] for o in persona["object_inventory"]]
    rec_ids = [r["id"] for r in receptacles]
    resident_ids = [r["id"] for r in persona["residents"]]
    schema = schemas.build_objects_schema(
        slot["household_id"], resident_ids, object_ids, rec_ids, days,
        params, scheduled)
    tag = MOVEMENT.tag("movement", builder=True, schema=schema)
    user = MOVEMENT_USER.format(
        persona=persona_text, days=days,
        digest=activity_digest(story, persona),
        places="\n".join(f"  {r}" for r in rec_ids))
    for attempt in range(MOVEMENT_MAX_ATTEMPTS):
        seed = make_seed(slot["household_id"], 0, tag, attempt)
        record: dict = {"attempt": attempt, "seed": seed}
        try:
            with _reasoning(effort):
                raw = llm_client.generate_json(
                    gen._LongFormClient(client, gen.PROGRAM_MAX_TOKENS),
                    MOVEMENT.text, user, schema, seed=seed, stage=tag,
                    cache=cache, force=force)
        except SpendCapExceeded:
            raise
        except Exception as e:
            record["failures"] = [f"generation: {e!r}"[:300]]
            log.setdefault("movement_attempts", []).append(record)
            continue
        raw = gen._take_reasoning(raw, record, "reasoning")
        object_rules = raw["object_rules"]
        program = story_to_program(slot, persona, receptacles, story,
                                   object_rules, days)
        failures = (v2v.check_referential(program, persona)
                    + v2v.check_reachability(program)
                    + storyfirst_coverage(story, object_rules))
        record["failures"] = failures
        record["uncovered_at_home"] = sorted(
            effective_activities(story)[0]
            - {r["activity"] for e in object_rules
               for r in e.get("rules") or []})
        if getattr(client, "hosted", False) and client.last_meta:
            record["usage"] = dict(client.last_meta)
        log.setdefault("movement_attempts", []).append(record)
        if not failures:
            return object_rules, program
    return None, None


# -------------------------------------------------------------- driver --

def build_household(slot, control, out_root: pathlib.Path, model: str,
                    days: int, seed: int, client, cache, force) -> bool:
    suffix = slot["household_id"].split("_")[-1]
    hh_dir = out_root / (f"hh{int(suffix)}" if suffix.isdigit()
                         else slot["household_id"])
    hh_dir.mkdir(parents=True, exist_ok=True)
    receptacles = receptacles_for(slot)
    log: dict = {"household": slot["household_id"],
                 "household_type": slot["household_type"],
                 "model": model, "pipeline": PIPELINE_VERSION,
                 "days": days,
                 "prompts": {t.name: t.version for t in
                             (prompts.PERSONA, MONTH_SYSTEM, MOVEMENT)}}
    aborted = None
    try:
        # L1 — persona, one call, no leak audit.
        persona, persona_text, persona_seed, reasoning = \
            gen.generate_persona(slot, control, client, cache, force)
        log["persona_seed"] = persona_seed
        log["persona_reasoning"] = reasoning
        (hh_dir / "persona.yaml").write_text(persona_text)
        # L2 — the story, one call per resident.
        story = generate_story(slot, persona, persona_text, receptacles,
                               days, client, cache, force, log)
        (hh_dir / "story.yaml").write_text(
            "# GENERATED by src/revamp_v2/storyfirst.py — every "
            "resident's days,\n# one LLM call per resident, merged.\n"
            + yaml.safe_dump({"household": slot["household_id"],
                              "days": story}, sort_keys=False,
                             allow_unicode=True, width=100))
        # L3 — the movement pass.
        object_rules, program = generate_movement(
            slot, persona, persona_text, receptacles, story, days,
            client, cache, force, log)
    except SpendCapExceeded as e:
        aborted, object_rules, program = e, None, None
    except Exception as e:                    # a lost story is a lost hh
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
        "# GENERATED by src/revamp_v2/storyfirst.py — the movement pass:\n"
        "# per object its home, drift rate and after-rules, authored\n"
        "# against the story's own effective activities.\n"
        + yaml.safe_dump({"object_rules": object_rules}, sort_keys=False,
                         width=100, allow_unicode=True))
    (hh_dir / "program.yaml").write_text(
        "# GENERATED — the assembled realization program (story days as\n"
        "# one-off adds + the movement pass rules). Never hand-edited.\n"
        + yaml.safe_dump(program, sort_keys=False, width=100,
                         allow_unicode=True))
    # L4 — deterministic realization (same block as the story arm).
    sa = sim.load_v1()
    params = sim.load_params()
    tl_log, hourly, blocks, stats, acts, motions = sim.simulate_program(
        program, days, seed, sa=sa, params=params)
    sim.tag_event_kinds(tl_log)
    carry_cfg = params.get("carry_on_departure", {})
    stats["carry_rehome_suppressed"] = sim.suppress_carry_rehome(
        tl_log, hourly, float(carry_cfg.get("carry_rehome_min", 0)))
    out_tl = hh_dir / f"timeline_seed{seed}"
    sa.write_outputs(out_tl, motions, tl_log, hourly, blocks, stats, days,
                     seed, hh_dir)
    meta = json.loads((out_tl / "meta.json").read_text())
    at_home, trips = effective_activities(story)
    meta.update({
        "engine": "storyfirst", "model": model,
        "pipeline": PIPELINE_VERSION,
        "n_story_activities": len(at_home | trips),
        "effective_trips": sorted(trips),
        "uncovered_at_home": (log.get("movement_attempts") or [{}])[-1]
        .get("uncovered_at_home", []),
    })
    (out_tl / "meta.json").write_text(json.dumps(meta, indent=2))
    (hh_dir / "build_log.json").write_text(json.dumps(log, indent=2))
    print(f"{slot['household_id']}: OK — {meta['n_events']} events, "
          f"{len(at_home | trips)} activities -> {hh_dir}")
    return True


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--household")
    group.add_argument("--all", action="store_true")
    ap.add_argument("--model", default=os.environ.get("GENERATION_MODEL",
                                                      "gpt-5.6-terra"))
    ap.add_argument("--out-root", type=pathlib.Path, default=None)
    ap.add_argument("--days", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    control = yaml.safe_load((sim.PROFILES_DIR / "control.yaml").read_text())
    days = args.days or int(control["days"])
    slug = llm_client.model_slug(args.model)
    out_root = args.out_root or sim.PROFILES_DIR / "storyfirst" / slug
    cache = ResponseCache(args.cache_dir or
                          f"/tmp/dynamic-home-eqa-gen-cache-storyfirst-{slug}")
    client = llm_client._get_client(args.model)
    if not getattr(client, "hosted", False):
        raise SystemExit(
            "storyfirst is hosted-only (per-resident story calls need "
            "server-side structured outputs) — set GENERATION_ENDPOINT "
            "to https://api.openai.com or "
            "https://generativelanguage.googleapis.com")
    print(f"backend: {type(client).__name__} "
          f"(schema dialect {client.schema_dialect})")
    slots = control["households"]
    if not args.all:
        digits = "".join(c for c in args.household if c.isdigit())
        slots = [s for s in slots
                 if int(s["household_id"].split("_")[-1]) == int(digits)]
        if not slots:
            raise SystemExit(f"no slot matches {args.household!r}")
    try:
        ok = all([build_household(s, control, out_root, args.model, days,
                                  args.seed, client, cache, args.force)
                  for s in slots])
    except SpendCapExceeded as e:
        print(f"ABORTED: {e}")
        raise SystemExit(2)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    _main()
