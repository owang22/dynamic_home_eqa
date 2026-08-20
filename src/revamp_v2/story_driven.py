"""Story-driven generation: the LLM writes the household's three weeks as
a STORY first, then does object-level freeform movement against it.

The weekly-template L2 could only say what recurs, so one-off happenings
had no home and 6-15 of the 50 activity names ever got used. Here the
model authors the 21 days directly — the recurring spine, the weekday/
weekend texture, and storylike arcs (a cold, a visitor, a deadline week)
— one week per call, each call re-reading what it already wrote. That
calendar IS the schedule: its blocks become residents.jsonl, and the
per-day movement pass (same shape as freeform_motion) reads its own
story's day instead of a rule-based simulator's output.

Personas and starting object homes come from the rule_based household so
every method shares one world. Thinking mode throughout; no plausibility
gates — a day that fails to parse is recorded and the run continues.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT / "src"))

import freeform_motion as fm                                  # noqa: E402
from prompts import ACTIVITY_VOCAB, TIME_PATTERN              # noqa: E402

from dynamic_home_eqa.generation import llm_client            # noqa: E402
from dynamic_home_eqa.generation.cache import (               # noqa: E402
    ResponseCache, make_seed)

try:
    import jsonschema
except ImportError:                                           # pragma: no cover
    jsonschema = None

# 32000, up from 24000: the think block and the answer share this budget,
# and Qwen3.8-27B spent all 24k still reasoning on 2 of 3 week-story calls
# (finish_reason="length"), handing the parser a truncated think block.
# _effective_max_tokens verifies the request against the SERVED
# max_model_len — vLLM rejects (400), never truncates, a request whose
# prompt + max_tokens exceeds it — and clamps with a warning.
STORY_MAX_TOKENS = 32000
STORY_MAX_RETRIES = 3
# What a retryable bad sample looks like. jsonschema.ValidationError is
# NOT a ValueError (it derives straight from Exception), so the obvious
# (json.JSONDecodeError, KeyError, ValueError, TypeError) tuple — the one
# llm_client.generate_json_thinking uses — lets a schema violation escape
# the retry loop and kill the whole call on attempt 1. Measured: deepseek
# hh2's three weeks (an invented resident name `Sam`, block-shape drift)
# each failed with zero retries until this tuple included it.
RETRYABLE = (json.JSONDecodeError, KeyError, ValueError, TypeError)
if jsonschema is not None:
    RETRYABLE = RETRYABLE + (jsonschema.ValidationError,)
STORY_TAG_WEEK = "story_v1_think"      # legacy per-week path (cache-compat)
# The per-day tag folds the prompt content hash — the same reason
# PromptTemplate.tag does: seeds derive from the tag, so without it a
# reworded prompt would replay cached stories sampled under the old
# wording. The week tag stays frozen: it exists purely to replay the
# legacy per-week caches byte-identically.
STORY_TAG_DAY = "story_day_think_p"   # + prompt hash, appended below

STORY_SYSTEM = """\
You write the lived three weeks of one simulated household as a concrete
calendar: who does what, when, where — day by day, not as a repeating
template. You are writing for yourself: a later pass will use this
calendar to decide how the household's objects move, so it must be the
kind of specific, believable record a person's actual three weeks leaves.

What three real weeks contain, and a weekly template misses:
- a recurring spine (work, school, sleep) that holds MOST days;
- weekly texture: weekends unlike weekdays, a laundry day, a groceries
  run, the gym nights that actually happen;
- storylike happenings that play out ACROSS days — someone catches a
  cold and is home for two days, a friend visits for a weekend, a work
  deadline makes one week late-heavy, an appointment interrupts a
  morning. Invent arcs the persona supports and let them show in the
  schedule, not just the summary.

Activity names come from a closed list. Pick by WHAT THE PERSON IS
DOING, never by the clock: a night worker sleeping 09:30-17:00 is in
day_sleep (not night_sleep), and their hours before a night shift are
dinner / relax / get_ready (not wake_up). Every resident sleeps every
day. If a block crosses midnight (night shift, sleep), write its end as
the clock time it actually ends the next morning.

Respond only with valid JSON matching the provided schema. No
commentary."""

STORY_USER = """\
The household (persona, verbatim):

{persona}

Places in this home (`at` for each block; ELSEWHERE = out of the house):
{locations}

Activity names (the closed list — use the range of it where the persona
supports it; occasional chores and outings belong somewhere in three
weeks):
{vocab}

{recap}

Write days {lo}..{hi} (day 0 is a Monday; {weekday_map}). For each day:
`day`, a one-line `summary` of what this day is in the household's story,
and `blocks` — every resident's day in 8-16 blocks: `resident`,
`activity`, `start`, `end` (HH:MM), `at`. Write the anchors (sleep, work,
meals) AND the small connective activities a real day is full of — a
coffee, a snack, medication, a shower, taking out the bins, a quick tidy,
ten minutes of phone_time. Small blocks may be 5-20 minutes. A real
person's diary averages ~18 distinct episodes a day; a day written as 5
long blocks is a summary, not a day. Cover each resident's whole day
including sleep, at least 8 blocks per resident.
"""

import hashlib as _hashlib
STORY_TAG_DAY += _hashlib.sha256(
    (STORY_SYSTEM + STORY_USER).encode()).hexdigest()[:8]

# Lever 3 (soft floor): a day with fewer blocks than this for any resident
# is a FAILED attempt (reroll at a shifted seed), not an accepted thin day.
# Thinking mode has no grammar to enforce a minimum, so the enforcement
# ladder is prompt -> recap steering -> this validator; ATUS puts the
# median at ~18 episodes/person-day, so 8 is a floor, not a target.
MIN_BLOCKS_PER_RESIDENT = 8


def build_story_schema(resident_ids, receptacles, lo, hi):
    block = {
        "type": "object", "additionalProperties": False,
        "required": ["resident", "activity", "start", "end", "at"],
        "properties": {
            "resident": {"enum": resident_ids},
            "activity": {"enum": ACTIVITY_VOCAB},
            "start": {"type": "string", "pattern": TIME_PATTERN},
            "end": {"type": "string", "pattern": TIME_PATTERN},
            "at": {"enum": receptacles + ["ELSEWHERE"]},
        },
    }
    day = {
        "type": "object", "additionalProperties": False,
        "required": ["day", "summary", "blocks"],
        "properties": {
            "day": {"type": "integer", "minimum": lo, "maximum": hi},
            "summary": {"type": "string", "maxLength": 200},
            "blocks": {"type": "array", "minItems": 1,
                       "maxItems": max(60, 18 * len(resident_ids)),
                       "items": block},
        },
    }
    n = hi - lo + 1
    return {"type": "object", "additionalProperties": False,
            "required": ["days"],
            "properties": {"days": {"type": "array", "minItems": n,
                                    "maxItems": n, "items": day}}}


def _normalize_story(parsed):
    if isinstance(parsed, list):
        parsed = {"days": parsed}
    elif isinstance(parsed, dict) and "days" not in parsed:
        for k in ("calendar", "schedule", "story"):
            if k in parsed and isinstance(parsed[k], list):
                parsed = {"days": parsed[k]}
                break
    return parsed


def _recap(days: list[dict]) -> str:
    """What the model already wrote, compact — summaries for all prior
    days, full blocks only for the most recent 3 (context budget), plus
    the closed-list activities NOT yet used: models repeat what the recap
    shows them, so without the unused line a story converges on the same
    dozen names (measured: 20-28 of 50 across 21 days) and the object
    layer inherits the bias."""
    if not days:
        return ("This is the first week; nothing is written yet. Start the "
                "story from day 0.")
    lines = ["The story you have already written:"]
    for d in days:
        lines.append(f"  d{d['day']:02d} {fm.DAY_NAMES[d['day'] % 7]}: "
                     f"{d['summary']}")
    lines.append("The last days' blocks, so times stay coherent:")
    for d in days[-3:]:
        for b in d["blocks"]:
            lines.append(f"  d{d['day']:02d} {b['resident']} "
                         f"{b['start']}-{b['end']} {b['activity']} @ {b['at']}")
    used = {b["activity"] for d in days for b in d["blocks"]}
    unused = [a for a in ACTIVITY_VOCAB if a not in used]
    if unused:
        lines.append(
            "Activities from the closed list you have NOT used yet — weave "
            "in the ones this persona plausibly would, where the story "
            "supports them: " + ", ".join(unused))
    return "\n".join(lines)


def _write_story(out_hh: pathlib.Path, household: str,
                 story: list[dict]) -> None:
    """Persist the calendar so far. Called after EVERY week: a household
    takes the better part of an hour, and a run that writes nothing until
    it finishes is a run nobody can check on."""
    out_hh.mkdir(parents=True, exist_ok=True)
    (out_hh / "story.yaml").write_text(
        "# GENERATED by src/revamp_v2/story_driven.py — the household's\n"
        "# 21-day calendar as authored by the model, week by week.\n"
        + yaml.safe_dump({"household": household, "days": story},
                         sort_keys=False, allow_unicode=True, width=100))


def _served_max_model_len(client) -> int | None:
    """The serving config's max_model_len, when the client is an HTTP one
    (queried once and cached on the client). None in-process or on any
    query failure — the guard then simply cannot clamp."""
    base = getattr(client, "base", None)
    if not base:
        return None
    cached = getattr(client, "_story_max_model_len", False)
    if cached is not False:
        return cached
    mm = None
    try:
        import requests
        data = requests.get(f"{base}/v1/models", timeout=10).json()
        mm = int(data["data"][0]["max_model_len"])
    except Exception:                                  # pragma: no cover
        pass
    client._story_max_model_len = mm
    return mm


def _effective_max_tokens(client, system: str, user: str, want: int) -> int:
    """Clamp the generation budget so prompt + max_tokens fits the served
    max_model_len — vLLM REJECTS (400) such a request rather than
    truncating it, so an unclamped budget loses the call outright. The
    prompt estimate is deliberately generous (~3 chars/token + margin)."""
    mm = _served_max_model_len(client)
    if mm is None:
        return want
    est_prompt = (len(system) + len(user)) // 3 + 1024
    allowed = mm - est_prompt
    if allowed < 8192:
        raise RuntimeError(
            f"served max_model_len {mm} leaves only {allowed} tokens for a "
            f"~{est_prompt}-token story prompt — serve with a larger "
            f"--max-model-len (>= {est_prompt + STORY_MAX_TOKENS} for the "
            f"full budget)")
    if allowed < want:
        print(f"  [story] clamping max_tokens {want} -> {allowed} "
              f"(served max_model_len {mm})")
    return min(want, allowed)


def _thinking_call(client, system: str, user: str, seed: int,
                   max_tokens: int) -> tuple[str, str, str | None]:
    """(payload, think, finish_reason). Over HTTP the request is made
    directly (via the client's own retrying _post_chat) so finish_reason
    is visible — the piece the generate_thinking contract discards, and
    the only reliable truncation signal. In-process falls back to
    generate_thinking with finish_reason None."""
    if hasattr(client, "_post_chat") and getattr(client, "base", None):
        import re
        body = {
            "model": client.model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "temperature": 0.6, "top_p": 0.95, "max_tokens": max_tokens,
            "chat_template_kwargs": {"enable_thinking": True},
            "seed": seed & 0x7FFFFFFFFFFFFFFF,
        }
        choice = client._post_chat(body)["choices"][0]
        msg = choice["message"]
        payload = msg.get("content") or ""
        think = msg.get("reasoning_content") or ""
        if not think and "</think>" in payload:
            think, payload = payload.rsplit("</think>", 1)
            think = think.replace("<think>", "").strip()
        fence = re.search(r"```(?:json)?\s*(.*?)```", payload, re.S)
        if fence:
            payload = fence.group(1)
        return payload.strip(), think, choice.get("finish_reason")
    payload, think = client.generate_thinking(
        system, user, seed=seed, temperature=0.6, max_tokens=max_tokens)
    return payload, think, None


def _looks_truncated(payload: str, think: str,
                     finish_reason: str | None) -> str | None:
    """The truncation guard: the reason string when this response must be
    treated as a failed attempt WITHOUT parsing, else None.
    finish_reason == "length" is definitive. An empty payload, or one
    with no reasoning anywhere (no split-out think, no </think>) that is
    plainly not JSON, is the unterminated-think signature: the model spent
    the budget reasoning and the raw trace must never be parsed as the
    answer. A tagless response that IS JSON (a model that simply answered)
    passes through to the parser."""
    if finish_reason == "length":
        return f"finish_reason=length (think+answer overran max_tokens)"
    if not payload.strip():
        return "empty payload"
    if not think and not payload.lstrip().startswith(("{", "[")):
        return "unterminated think block (no </think>; payload is prose)"
    return None


def generate_story_json(client, system, user, *, seed, stage, cache=None,
                        force=False, validate=lambda r: r,
                        max_tokens=STORY_MAX_TOKENS,
                        max_retries=STORY_MAX_RETRIES):
    """The story stage's own cache/retry/validate loop — the same contract
    as llm_client.generate_json_thinking (cache checked at `seed`, live
    attempts at seed+attempt, successes cached under `seed`) plus the
    truncation guard above, which that shared helper cannot host because
    finish_reason dies inside generate_thinking. Raises the last error
    after max_retries failed attempts; truncated responses are never
    parsed and never cached."""
    if cache and not force:
        record = cache.get_record(seed)
        if record is not None and record.get("raw") is not None:
            try:
                return validate(json.loads(record["raw"]))
            except RETRYABLE as e:
                print(f"  [{stage}] cached response failed validation "
                      f"(seed={seed}): {e} — regenerating")
    eff = _effective_max_tokens(client, system, user, max_tokens)
    last_err: Exception = RuntimeError(
        f"generate_story_json: max_retries={max_retries} is not positive")
    for attempt in range(max_retries):
        payload, think, finish = _thinking_call(
            client, system, user, seed + attempt, eff)
        truncated = _looks_truncated(payload, think, finish)
        if truncated:
            last_err = RuntimeError(f"truncated response: {truncated}")
            print(f"  [{stage}] attempt {attempt + 1}/{max_retries} "
                  f"(seed={seed + attempt}): {truncated} — retrying")
            continue
        try:
            result = validate(json.loads(payload))
        except RETRYABLE as e:
            last_err = e
            print(f"  [{stage}] attempt {attempt + 1}/{max_retries} "
                  f"(seed={seed + attempt}): {type(e).__name__}: "
                  f"{str(e)[:160]} — retrying")
            continue
        if cache:
            cache.put(seed, user, payload, think=think[:20000])
        return result
    raise last_err


def generate_story(program, persona_text, cache, client, days_total,
                   force, out_hh=None, per_week=False,
                   max_retries=STORY_MAX_RETRIES):
    """The shared story stage (both story arms). Default is one call PER
    DAY — a day's story fits the thinking budget where a week's often did
    not, and one bad sample now loses a day, not a week — re-reading the
    recap of everything already written. per_week=True keeps the original
    one-call-per-week shape (its own cache tag, so existing per-week
    caches replay byte-identically) for A/B.

    Returns (story, failed_calls, call_stats)."""
    tag = STORY_TAG_WEEK if per_week else STORY_TAG_DAY
    residents = [r["id"] for r in program["residents"]]
    receptacles = [r["id"] for r in program["receptacles"]]
    loc_lines = "\n".join(f"  {x}" for x in receptacles + ["ELSEWHERE"])
    wmap = ", ".join(f"{i}={n}" for i, n in enumerate(fm.DAY_NAMES))
    if per_week:
        units = [(w, lo, min(lo + 6, days_total - 1))
                 for w, lo in enumerate(range(0, days_total, 7))]
    else:
        units = [(d, d, d) for d in range(days_total)]
    story: list[dict] = []
    failed_calls: list[dict] = []
    n_attempts = 0
    for idx, lo, hi in units:
        schema = build_story_schema(residents, receptacles, lo, hi)

        def _validate(parsed):
            parsed = _normalize_story(parsed)
            if jsonschema is not None:
                jsonschema.validate(parsed, schema)
            for d in parsed["days"]:
                per: dict = {}
                for b in d["blocks"]:
                    per[b["resident"]] = per.get(b["resident"], 0) + 1
                thin = [r for r in residents
                        if per.get(r, 0) < MIN_BLOCKS_PER_RESIDENT]
                if thin:
                    raise ValueError(
                        f"day {d['day']}: fewer than "
                        f"{MIN_BLOCKS_PER_RESIDENT} blocks for {thin} — "
                        f"a day written that thin is a summary, not a day")
            return parsed

        user = STORY_USER.format(persona=persona_text, locations=loc_lines,
                                 vocab=", ".join(ACTIVITY_VOCAB),
                                 recap=_recap(story), lo=lo, hi=hi,
                                 weekday_map=wmap)
        seed = make_seed(program["household"], idx, tag)
        n_attempts += 1
        try:
            parsed = generate_story_json(
                client, STORY_SYSTEM, user, seed=seed, stage=tag,
                cache=cache, force=force, validate=_validate,
                max_tokens=STORY_MAX_TOKENS, max_retries=max_retries)
        except Exception as e:
            unit = {"week" if per_week else "day": idx,
                    "error": repr(e)[:200]}
            failed_calls.append(unit)
            print(f"  {'week' if per_week else 'day'} {idx}: STORY FAILED "
                  f"({type(e).__name__})")
            continue
        got = sorted(parsed["days"], key=lambda d: d["day"])
        story.extend(got)
        if out_hh is not None:
            _write_story(out_hh, program["household"], story)
        acts = {b["activity"] for d in got for b in d["blocks"]}
        print(f"  {'week' if per_week else 'day'} {idx}: days {lo}-{hi}, "
              f"{sum(len(d['blocks']) for d in got)} blocks, "
              f"{len(acts)} activities")
    call_stats = {"granularity": "week" if per_week else "day",
                  "tag": tag, "n_calls": len(units),
                  "n_failed_calls": len(failed_calls),
                  "max_retries": max_retries,
                  "max_tokens": STORY_MAX_TOKENS}
    return story, failed_calls, call_stats


def blocks_to_residents(story, days_total):
    """story blocks -> the same residents.jsonl rows simulate.py writes.
    A block whose end <= start crosses midnight into the next day."""
    rows = []
    for d in story:
        base = d["day"] * 1440
        for b in d["blocks"]:
            t0 = base + int(b["start"][:2]) * 60 + int(b["start"][3:])
            t1 = base + int(b["end"][:2]) * 60 + int(b["end"][3:])
            if t1 <= t0:
                t1 += 1440
            rows.append({"resident": b["resident"], "activity": b["activity"],
                         "t0": t0, "t1": min(t1, days_total * 1440),
                         "at": b["at"], "note": ""})
    rows.sort(key=lambda r: r["t0"])
    return rows


def run_household(hh_src, out_hh, model, cache, days, force,
                  per_week=False):
    program = yaml.safe_load((hh_src / "routine_program.yaml").read_text())
    persona_text = (hh_src / "persona.yaml").read_text()
    motions = yaml.safe_load((hh_src / "expanded_motions.yaml").read_text())
    client = llm_client._get_client(model)

    story, failed_calls, call_stats = generate_story(
        program, persona_text, cache, client, days, force,
        out_hh=out_hh, per_week=per_week)
    _write_story(out_hh, program["household"], story)
    # Persona, program and starting homes belong on disk from the start —
    # they are what the movement pass reads, and a half-built household
    # should still be inspectable.
    for name in ("persona.yaml", "routine_program.yaml",
                 "expanded_motions.yaml"):
        (out_hh / name).write_text((hh_src / name).read_text())
    # Refuse-to-ship: a household whose EVERY story call failed has no
    # story to drive anything — a timeline built from it would be 100%
    # fallback wearing a story-driven label (the deepseek hh2 trap). No
    # timeline is written; the caller exits nonzero for it.
    if not story:
        print(f"  {program['household']}: every story call failed — "
              f"NO TIMELINE WRITTEN")
        return None
    (out_hh / "timeline_seed0").mkdir(parents=True, exist_ok=True)
    with open(out_hh / "timeline_seed0" / "residents.jsonl", "w") as f:
        for r in blocks_to_residents(story, days):
            f.write(json.dumps(r) + "\n")

    object_ids = list(motions["placements"])
    residents = [r["id"] for r in program["residents"]]
    receptacles = [r["id"] for r in program["receptacles"]]
    locations = receptacles + ["ELSEWHERE"] + \
        [f"person:{r}" for r in residents]
    story_by_day = {d["day"]: d for d in story}
    all_acts = sorted({b["activity"] for d in story for b in d["blocks"]})
    mv_schema = fm.build_schema(object_ids, locations, all_acts)

    state = {o: p["home"] for o, p in motions["placements"].items()}
    events, hourly, history, failed_days = [], [], [], []
    loc_lines = "\n".join(f"  {x}" for x in locations)

    for day in range(days):
        weekday = fm.DAY_NAMES[day % 7]
        d = story_by_day.get(day)
        if d is None:                       # its story week failed
            failed_days.append({"day": day, "error": "no story"})
            d = {"summary": "(story missing)", "blocks": []}
        sched = "\n".join(
            f"  {b['resident']}  {b['start']}-{b['end']}  "
            f"{b['activity']} @ {b['at']}"
            for b in sorted(d["blocks"], key=lambda b: b["start"]))
        recent = [h for h in history if h.startswith(f"d{day-1:02d}")
                  or h.startswith(f"d{day-2:02d}")]
        if recent:
            hist = ("Movements over the last two days (your own earlier "
                    "output):\n" + "\n".join(f"  {h}" for h in recent))
        elif day == 0:
            hist = ("This is the first day; the home starts tidy, "
                    "everything at the spot listed above.")
        else:
            hist = ("No object moved in the last two days; positions above "
                    "are current.")
        user = fm.USER_TEMPLATE.format(
            persona=persona_text, locations=loc_lines, day=day, days=days,
            weekday=weekday,
            schedule=f"  Today in the story: {d['summary']}\n" + sched,
            state="\n".join(f"  {o}: {state[o]}" for o in object_ids),
            history=hist)
        seed = make_seed(program["household"], day, "story_motion_v1_think")

        def _validate(parsed):
            if isinstance(parsed, list):
                parsed = {"movements": parsed}
            elif isinstance(parsed, dict) and "movements" not in parsed:
                for k in ("moves", "events", "movement_log", "actions"):
                    if k in parsed and isinstance(parsed[k], list):
                        parsed = {"movements": parsed[k]}
                        break
            if jsonschema is not None:
                jsonschema.validate(parsed, mv_schema)
            return parsed

        try:
            parsed = llm_client.generate_json_thinking(
                client, fm.SYSTEM, user, seed=seed,
                stage="story_motion_v1_think", cache=cache, force=force,
                validate=_validate, max_tokens=fm.THINKING_MAX_TOKENS,
                max_retries=1)
        except Exception as e:
            failed_days.append({"day": day, "error": repr(e)[:200]})
            print(f"  day {day:2d} {weekday}: GENERATION FAILED "
                  f"({type(e).__name__}) — counted, not retried")
            parsed = {"movements": []}

        moves = sorted(parsed["movements"], key=lambda m: m["time"])
        day_moves = mi = 0

        def _apply(m):
            nonlocal day_moves
            src = state[m["object"]]
            if m["to"] == src:
                return
            t = day * 1440 + int(m["time"][:2]) * 60 + int(m["time"][3:])
            ev = {"t": t, "stamp": f"d{day:02d} {weekday} {m['time']}",
                  "object": m["object"], "from": src, "to": m["to"],
                  "by": f"activity:{m['activity']}"}
            if m.get("note"):
                ev["note"] = m["note"][:60]
            events.append(ev)
            state[m["object"]] = m["to"]
            history.append(
                f"d{day:02d} {m['time']} {m['object']}: {src} -> {m['to']} "
                f"({m['activity']})")
            day_moves += 1

        for hr in range(24):
            t_hour = day * 1440 + hr * 60
            while mi < len(moves):
                m = moves[mi]
                t_m = (day * 1440 + int(m["time"][:2]) * 60
                       + int(m["time"][3:]))
                if t_m > t_hour:
                    break
                _apply(m)
                mi += 1
            snap = {"t": t_hour, "stamp": f"d{day:02d} {weekday} {hr:02d}:00"}
            snap.update({o: state[o] for o in object_ids})
            hourly.append(snap)
        while mi < len(moves):
            _apply(moves[mi])
            mi += 1
        print(f"  day {day:2d} {weekday}: {day_moves} movements")

    out = out_hh / "timeline_seed0"
    out.mkdir(parents=True, exist_ok=True)
    events.sort(key=lambda e: e["t"])
    with open(out / "events.jsonl", "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    with open(out / "hourly.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "stamp"] + object_ids)
        for row in hourly:
            w.writerow([row["t"], row["stamp"]] + [row[o] for o in object_ids])
    with open(out / "residents.jsonl", "w") as f:
        for r in blocks_to_residents(story, days):
            f.write(json.dumps(r) + "\n")
    moves_ct = {o: 0 for o in object_ids}
    for e in events:
        moves_ct[e["object"]] += 1
    # Fallback days (no story authored for that day) are the story stage's
    # failure, distinct from movement-generation failures — both live in
    # failed_days for the day loop, but only the former mark the household.
    fallback_days = sorted(d for d in range(days) if d not in story_by_day)
    meta = {"household": program["household"],
            "household_type": program.get("household_type"),
            "source": str(out_hh), "engine": "story_driven_llm",
            "model": model, "single_pass": True,
            "story_call_stats": call_stats,
            "failed_story_calls": failed_calls, "failed_days": failed_days,
            "n_failed_days": len(failed_days),
            "fallback_days": fallback_days,
            "n_fallback_days": len(fallback_days),
            "not_story_driven": len(fallback_days) > 0.3 * days,
            "days": days, "seed": 0,
            "n_events": len(events),
            "story_activities": all_acts,
            "n_story_activities": len(all_acts),
            "moves_per_object": dict(sorted(moves_ct.items(),
                                            key=lambda kv: -kv[1]))}
    if meta["not_story_driven"]:
        print(f"  {program['household']}: {len(fallback_days)}/{days} "
              f"fallback days — marked NOT story-driven")
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    return meta


def _main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--households", nargs="+", required=True,
                    help="rule_based household dirs (persona + program + "
                         "expanded_motions)")
    ap.add_argument("--out-root", type=pathlib.Path, required=True)
    ap.add_argument("--model",
                    default=os.environ.get("GENERATION_MODEL",
                                           llm_client.DEFAULT_MODEL))
    ap.add_argument("--days", type=int, default=21)
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--per-week", action="store_true",
                    help="one story call per week (the original shape; "
                         "replays existing per-week caches) instead of "
                         "the per-day default")
    args = ap.parse_args()
    slug = llm_client.model_slug(args.model)
    cache = ResponseCache(args.cache_dir or
                          f"/tmp/dynamic-home-eqa-gen-cache-story-{slug}")
    failed = []
    for hh in args.households:
        hh_src = pathlib.Path(hh)
        out_hh = args.out_root / hh_src.name
        print(f"{hh_src.name}: story-driven, {args.days} days")
        meta = run_household(hh_src, out_hh, args.model, cache,
                             args.days, args.force, per_week=args.per_week)
        if meta is None:
            failed.append(hh_src.name)
            continue
        print(f"{meta['household']}: {meta['n_events']} events, "
              f"{meta['n_story_activities']} story activities -> {out_hh}")
    if failed:
        print(f"FAILED (no story, no timeline): {failed}")
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
