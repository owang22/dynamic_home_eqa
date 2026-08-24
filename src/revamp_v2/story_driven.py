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
from dynamic_home_eqa.generation.hosted_spend import (        # noqa: E402
    SpendCapExceeded)

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
# 20000, not 32000, and the number is set by an INTERACTION rather than
# by what a story needs (a good day costs ~14k, of which ~12.5k is the
# think block). A runaway think block must hit this cap BEFORE the HTTP
# read timeout, or the request dies with no finish_reason and the
# truncation guard never gets to reseed: at ~49 tok/s single-stream,
# 32000 needs 653 s and the old 600 s timeout fired first, so a bad day
# burned 3 x 600 s retrying the SAME seed (measured on hh1 day 14).
# 20000 caps a runaway at ~408 s, inside the window, so `length` is
# reported and the attempt reseeds. STORY_HTTP_TIMEOUT then covers the
# concurrent case, where per-stream throughput is ~1/N.
STORY_MAX_TOKENS = 20000
STORY_MAX_RETRIES = 3
# Generous, because the failure it guards against is now the cap, not the
# clock: 20k tokens at 3-4 concurrent streams needs ~1200 s.
STORY_HTTP_TIMEOUT = 1800
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
try:                                   # a slow sample is a bad sample:
    import requests as _requests       # reseed rather than re-ask for it
    RETRYABLE = RETRYABLE + (_requests.Timeout, _requests.ConnectionError)
except ImportError:                                   # pragma: no cover
    pass
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

# Lever 3 (soft floor): a day with fewer blocks than this for any resident
# is a FAILED attempt (reroll at a shifted seed), not an accepted thin day.
# Thinking mode has no grammar to enforce a minimum, so the enforcement
# ladder is prompt -> recap steering -> this validator; ATUS puts the
# median at ~18 episodes/person-day, so 8 is a floor, not a target.
MIN_BLOCKS_PER_RESIDENT = 8


STORY_USER_ONE = """\
The household (persona, verbatim):

{persona}

Places in this home (`at` for each block; ELSEWHERE = out of the house):
{locations}

Activity names (the closed list — use the range of it where the persona
supports it; occasional chores and outings belong somewhere in three
weeks):
{vocab}

{recap}

{today}

Write day {lo} for {resident} ONLY (day 0 is a Monday; {weekday_map}).
Give `day`, a one-line `summary` of what this day is in the household's
story, and `blocks` — {resident}'s whole day in 8-16 blocks: `resident`
(always {resident}), `activity`, `start`, `end` (HH:MM), `at`. Write the
anchors (sleep, work, meals) AND the small connective activities a real
day is full of — a coffee, a snack, medication, a shower, taking out the
bins, a quick tidy, ten minutes of phone_time. Small blocks may be 5-20
minutes. Cover the whole day including sleep, at least 8 blocks.
"""


# One tag per PROMPT ACTUALLY USED, not one tag for the module: the
# single-resident per-day path renders STORY_USER and the per-(day,
# resident) path renders STORY_USER_ONE, so mixing both into one hash
# invalidates every cached single-resident day the moment the
# multi-resident template is touched (measured the hard way: adding
# STORY_USER_ONE silently forced hh1 to regenerate all 21 days).
import hashlib as _hashlib
STORY_TAG_DAY += _hashlib.sha256(
    (STORY_SYSTEM + STORY_USER).encode()).hexdigest()[:8]
STORY_TAG_DAY_RES = "story_dayres_think_p" + _hashlib.sha256(
    (STORY_SYSTEM + STORY_USER_ONE).encode()).hexdigest()[:8]


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


def widen_day_bounds(schema: dict, lo: int, hi: int) -> dict:
    """Cache-friendly twin of a story schema: the SAME shape and the SAME
    array length, with only the `day` INDEX bounds widened to the whole
    run, so every call of a household presents one identical schema.

    The array length must not move: build_story_schema derives
    minItems/maxItems from (hi - lo + 1), so rebuilding it over the full
    range demands 21 days per call instead of one — measured the
    expensive way (every response failed the narrow validator, ~10x cost
    per call, read timeouts). Only the bounds are relaxed here, and the
    NARROW schema still validates the response, so the exact day index
    stays enforced end to end."""
    import copy
    out = copy.deepcopy(schema)
    out["properties"]["days"]["items"]["properties"]["day"].update(
        {"minimum": lo, "maximum": hi})
    return out


def _persona_name_map(persona_text: str, residents: list[str]) -> dict:
    """{lowercased persona name (and first name) -> resident id}. The
    calendar stage runs WITHOUT guided decoding (the JSON grammar
    suppresses the think block), so the resident-id enum is only checked,
    never enforced — and the model reliably writes the person's NAME.
    Measured: deepseek hh2 lost all three weeks to `Sam`, qwen hh3 a day
    to `Eleanor`. The map is what lets that be repaired instead of
    rerolled."""
    out: dict = {}
    try:
        persona = yaml.safe_load(persona_text)
    except Exception:                                  # pragma: no cover
        return out
    if not isinstance(persona, dict):                  # not a persona YAML
        return out
    for r in persona.get("residents") or []:
        if not isinstance(r, dict):
            continue
        rid, name = r.get("id"), str(r.get("name") or "").strip()
        if rid in residents and name:
            out[name.lower()] = rid
            out[name.split()[0].lower()] = rid
    return out


def _repair_time(text) -> str | None:
    """Clock-time drift the pattern rejects: '24:00' (midnight written as
    the end of the day), '8:00' (unpadded), '08:00:00' (seconds), and
    '8:00 AM'. Returns None when nothing sane can be recovered."""
    if not isinstance(text, str):
        return None
    s = text.strip().upper()
    plus = "+1" if s.endswith("+1") else ""
    s = s[:-2].strip() if plus else s
    ampm = ""
    for suffix in ("AM", "PM"):
        if s.endswith(suffix):
            ampm, s = suffix, s[:-len(suffix)].strip()
    parts = s.split(":")
    if len(parts) < 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return None
    h, m = int(parts[0]), int(parts[1])
    if ampm == "PM" and h < 12:
        h += 12
    elif ampm == "AM" and h == 12:
        h = 0
    if h == 24 and m == 0:            # "24:00" IS midnight; the block's
        h = 0                         # own end<=start rule rolls the day
    if not (0 <= h <= 23 and 0 <= m <= 59):
        return None
    return f"{h:02d}:{m:02d}{plus}"


def _repair_day_index(value):
    """'d04' / 'day 4' / '04' -> 4."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        digits = "".join(c for c in value if c.isdigit())
        if digits:
            return int(digits)
    return None


def repair_story(parsed, residents, receptacles, name_map, repairs):
    """Deterministic repair of the format drift that guided decoding would
    have made unwritable, appending one line per fix to `repairs` so no
    change is silent. Follows the expander's five-normalizations
    precedent: the thing the model wrote describes something real, it just
    wrote it wrong, and rejecting a whole day over it protects no
    invariant. Anything NOT repairable is left alone for the validator to
    reject, which reseeds the attempt."""
    parsed = _normalize_story(parsed)
    rec_ok = set(receptacles) | {"ELSEWHERE"}
    res_ok = set(residents)
    for d in parsed.get("days") or []:
        if not isinstance(d, dict):
            continue
        fixed = _repair_day_index(d.get("day"))
        if fixed is not None and fixed != d.get("day"):
            repairs.append(f"day_index {d.get('day')!r}->{fixed}")
            d["day"] = fixed
        if isinstance(d.get("summary"), (list, dict)):
            repairs.append("summary_not_a_string")
            d["summary"] = str(d["summary"])[:200]
        for b in d.get("blocks") or []:
            if not isinstance(b, dict):
                continue
            r = b.get("resident")
            if r not in res_ok and isinstance(r, str):
                hit = name_map.get(r.strip().lower()) or \
                    name_map.get(r.strip().split()[0].lower()) if r.strip() \
                    else None
                if hit:
                    repairs.append(f"resident {r!r}->{hit}")
                    b["resident"] = hit
            for key in ("start", "end"):
                v = b.get(key)
                fixed_t = _repair_time(v)
                if fixed_t is not None and fixed_t != v:
                    repairs.append(f"{key} {v!r}->{fixed_t!r}")
                    b[key] = fixed_t
            at = b.get("at")
            if at not in rec_ok and isinstance(at, str):
                cand = {x.lower(): x for x in rec_ok}.get(at.strip().lower())
                if cand:
                    repairs.append(f"at {at!r}->{cand!r}")
                    b["at"] = cand
            act = b.get("activity")
            if isinstance(act, str) and act not in ACTIVITY_VOCAB:
                cand = act.strip().lower().replace(" ", "_").replace("-", "_")
                if cand in ACTIVITY_VOCAB:
                    repairs.append(f"activity {act!r}->{cand!r}")
                    b["activity"] = cand
    return parsed


def _normalize_story(parsed):
    if isinstance(parsed, list):
        parsed = {"days": parsed}
    elif isinstance(parsed, dict) and "days" not in parsed:
        for k in ("calendar", "schedule", "story"):
            if k in parsed and isinstance(parsed[k], list):
                parsed = {"days": parsed[k]}
                break
        else:
            # a BARE day object, written without its wrapper — the
            # "Additional properties ('blocks','day','summary')" failure
            if "blocks" in parsed and ("day" in parsed or "summary" in parsed):
                parsed = {"days": [parsed]}
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
        # The client's transient-failure loop retries the SAME request
        # (same seed) up to 3 times, which is exactly wrong for a
        # too-long generation: the identical sample is regenerated and
        # times out again (measured: hh1 day 14 burned 3 x 600 s). One
        # attempt here; reseeding is generate_story_json's job.
        if getattr(client, "_HTTP_RETRIES", 1) != 1:
            client._HTTP_RETRIES = 1
        if getattr(client, "timeout", 0) < STORY_HTTP_TIMEOUT:
            client.timeout = STORY_HTTP_TIMEOUT
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
                        max_retries=STORY_MAX_RETRIES, schema=None):
    """The story stage's own cache/retry/validate loop — the same contract
    as llm_client.generate_json_thinking (cache checked at `seed`, live
    attempts at seed+attempt, successes cached under `seed`) plus the
    truncation guard above, which that shared helper cannot host because
    finish_reason dies inside generate_thinking. Raises the last error
    after max_retries failed attempts; truncated responses are never
    parsed and never cached.

    HOSTED path (client.hosted, hosted-generation pilot): hosted models
    expose no think block, so the thinking path is NOT ported. The call
    routes through the structured-outputs path (client.generate with
    `schema` — the same per-day story schema the local validator already
    checks), and the truncation guard reduces to finish_reason ==
    "length". The local thinking path below is untouched."""
    hosted = getattr(client, "hosted", False) and schema is not None
    if cache and not force:
        record = cache.get_record(seed)
        if record is not None and record.get("raw") is not None:
            try:
                parsed = json.loads(record["raw"])
                if hosted:
                    from dynamic_home_eqa.generation.hosted_schema import \
                        drop_nulls
                    parsed = drop_nulls(parsed)
                return validate(parsed)
            except RETRYABLE as e:
                print(f"  [{stage}] cached response failed validation "
                      f"(seed={seed}): {e} — regenerating")
    if hosted:
        return _hosted_story_json(client, system, user, schema, seed=seed,
                                  stage=stage, cache=cache,
                                  validate=validate, max_tokens=max_tokens,
                                  max_retries=max_retries)
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


def _hosted_story_json(client, system, user, schema, *, seed, stage, cache,
                       validate, max_tokens, max_retries):
    """The hosted arm of generate_story_json: structured outputs, no think
    block, finish_reason=="length" as the whole truncation guard. Usage/
    snapshot/cost provenance rides into the cache record (Task 1.4)."""
    from dynamic_home_eqa.generation.hosted_schema import drop_nulls
    last_err: Exception = RuntimeError(
        f"_hosted_story_json: max_retries={max_retries} is not positive")
    for attempt in range(max_retries):
        try:
            raw = client.generate(system, user, schema,
                                  seed=seed + attempt, max_tokens=max_tokens)
        except RETRYABLE as e:               # transport-level bad sample
            last_err = e
            print(f"  [{stage}] attempt {attempt + 1}/{max_retries} "
                  f"(seed={seed + attempt}): {type(e).__name__}: "
                  f"{str(e)[:160]} — retrying")
            continue
        meta = getattr(client, "last_meta", None)
        if meta is not None and meta.get("finish_reason") == "length":
            last_err = RuntimeError(
                "truncated response: finish_reason=length")
            print(f"  [{stage}] attempt {attempt + 1}/{max_retries} "
                  f"(seed={seed + attempt}): finish_reason=length — "
                  f"retrying")
            continue
        try:
            result = validate(drop_nulls(json.loads(raw)))
        except RETRYABLE as e:
            last_err = e
            print(f"  [{stage}] attempt {attempt + 1}/{max_retries} "
                  f"(seed={seed + attempt}): {type(e).__name__}: "
                  f"{str(e)[:160]} — retrying")
            continue
        if cache:
            cache.put(seed, user, raw,
                      extra=dict(meta) if meta else None)
        return result
    raise last_err


def _today_context(day_blocks: list[dict]) -> str:
    """What the household's OTHER residents already have on this day —
    the anchor-coherence mechanism. Without it, per-resident calls write N
    parallel solo lives: nobody drives anyone to school, no meal is
    shared. Residents after the first write against a FIXED anchor day,
    which is what lets them run concurrently and still coordinate."""
    if not day_blocks:
        return ("You are the first person written for this day; the rest of "
                "the household will be written around you.")
    lines = ["Already written for TODAY by the other residents — coordinate "
             "with it (shared meals, lifts, handovers, who is home when):"]
    for b in sorted(day_blocks, key=lambda b: b["start"]):
        lines.append(f"  {b['resident']} {b['start']}-{b['end']} "
                     f"{b['activity']} @ {b['at']}")
    return "\n".join(lines)


def generate_story(program, persona_text, cache, client, days_total,
                   force, out_hh=None, per_week=False,
                   max_retries=STORY_MAX_RETRIES, per_resident=None,
                   max_workers=4):
    """The shared story stage (both story arms).

    Default granularity is one call PER DAY; for a MULTI-RESIDENT
    household it is one call per (day, resident), because a whole
    household-day does not fit the budget: measured on hh2 (4 residents,
    8-16 blocks each), the monolithic call exceeded the client's 600 s
    read timeout on every attempt and the days were lost outright. The
    think block is ~12.5k of the ~14k tokens a call spends and is largely
    fixed per call, so splitting trades N x that overhead for calls that
    actually finish.

    Coherence is preserved by ANCHOR ordering: residents[0] is written
    first, sequentially, and the rest are written against that fixed
    anchor day — so they can be issued CONCURRENTLY (vLLM serves
    --max-num-seqs in parallel) without any of them depending on another
    concurrent result. Order of completion therefore cannot change the
    output: each call's prompt is fully determined before the batch
    starts, and blocks are merged back in resident order.

    per_week=True keeps the original one-call-per-week shape (its own
    frozen cache tag, so existing per-week caches replay byte-identically).

    Returns (story, failed_calls, call_stats)."""
    residents = [r["id"] for r in program["residents"]]
    receptacles = [r["id"] for r in program["receptacles"]]
    loc_lines = "\n".join(f"  {x}" for x in receptacles + ["ELSEWHERE"])
    wmap = ", ".join(f"{i}={n}" for i, n in enumerate(fm.DAY_NAMES))
    name_map = _persona_name_map(persona_text, residents)
    if per_resident is None:
        per_resident = (not per_week) and len(residents) > 1
    tag = (STORY_TAG_WEEK if per_week
           else (STORY_TAG_DAY_RES if per_resident else STORY_TAG_DAY))
    # ...and fold the persona + the household's own places into the tag.
    # Seeds derive from it, and the persona is an INPUT to every story
    # prompt: without this a reworked persona (more objects, different
    # habits) reuses the same seed, hits the cache, and silently replays
    # the story written for the OLD persona — describing an inventory
    # that no longer exists. The template hash alone cannot catch that,
    # because the template did not change. Same reasoning as
    # PromptTemplate.tag folding the schema; the week tag is exempt so
    # the frozen legacy per-week caches still replay.
    if not per_week:
        tag += "_i" + _hashlib.sha256(
            (persona_text + "|".join(receptacles)).encode()).hexdigest()[:8]
    story: list[dict] = []
    failed_calls: list[dict] = []
    repairs: list[str] = []

    def _make_validator(who: list[str], schema):
        def _validate(parsed):
            parsed = repair_story(parsed, residents, receptacles, name_map,
                                  repairs)
            if jsonschema is not None:
                jsonschema.validate(parsed, schema)
            for d in parsed["days"]:
                per: dict = {}
                for b in d["blocks"]:
                    per[b["resident"]] = per.get(b["resident"], 0) + 1
                thin = [r for r in who
                        if per.get(r, 0) < MIN_BLOCKS_PER_RESIDENT]
                if thin:
                    raise ValueError(
                        f"day {d['day']}: fewer than "
                        f"{MIN_BLOCKS_PER_RESIDENT} blocks for {thin} — "
                        f"a day written that thin is a summary, not a day")
            return parsed
        return _validate

    def _call(seed, system, user, who, schema, request_schema=None):
        # request_schema (hosted only): the grammar actually SENT may be
        # day-widened so all of a household's story calls share one
        # schema — OpenAI's prompt cache keys on the full request prefix,
        # schema included, and per-day bounds gave 0% cache hits across
        # 84 calls (measured). Validation stays on the NARROW schema, so
        # the day index is still enforced end-to-end.
        return generate_story_json(
            client, system, user, seed=seed, stage=tag, cache=cache,
            force=force, validate=_make_validator(who, schema),
            max_tokens=STORY_MAX_TOKENS, max_retries=max_retries,
            schema=request_schema or schema)

    # ---------------------------------------------------------- per week --
    if per_week or not per_resident:
        units = ([(w, lo, min(lo + 6, days_total - 1))
                  for w, lo in enumerate(range(0, days_total, 7))]
                 if per_week else [(d, d, d) for d in range(days_total)])
        label = "week" if per_week else "day"
        for idx, lo, hi in units:
            schema = build_story_schema(residents, receptacles, lo, hi)
            wide = (widen_day_bounds(schema, 0, days_total - 1)
                    if getattr(client, "hosted", False) and not per_week
                    else None)
            user = STORY_USER.format(
                persona=persona_text, locations=loc_lines,
                vocab=", ".join(ACTIVITY_VOCAB), recap=_recap(story),
                lo=lo, hi=hi, weekday_map=wmap)
            try:
                parsed = _call(make_seed(program["household"], idx, tag),
                               STORY_SYSTEM, user, residents, schema,
                               request_schema=wide)
            except SpendCapExceeded:        # cap abort: never a failed call
                raise
            except Exception as e:
                failed_calls.append({label: idx, "error": repr(e)[:200]})
                print(f"  {label} {idx}: STORY FAILED ({type(e).__name__})")
                continue
            got = sorted(parsed["days"], key=lambda d: d["day"])
            story.extend(got)
            if out_hh is not None:
                _write_story(out_hh, program["household"], story)
            acts = {b["activity"] for d in got for b in d["blocks"]}
            print(f"  {label} {idx}: days {lo}-{hi}, "
                  f"{sum(len(d['blocks']) for d in got)} blocks, "
                  f"{len(acts)} activities")
        n_calls = len(units)
    # ------------------------------------------------- per (day, resident) --
    else:
        from concurrent.futures import ThreadPoolExecutor
        n_calls = 0

        def _one(day, rid, today):
            """One resident's day. Seed folds the resident index so each
            (day, resident) has its own cache entry."""
            schema = build_story_schema([rid], receptacles, day, day)
            wide = (widen_day_bounds(schema, 0, days_total - 1)
                    if getattr(client, "hosted", False) else None)
            user = STORY_USER_ONE.format(
                persona=persona_text, locations=loc_lines,
                vocab=", ".join(ACTIVITY_VOCAB), recap=_recap(story),
                today=today, lo=day, resident=rid, weekday_map=wmap)
            seed = make_seed(program["household"], day, tag,
                             residents.index(rid))
            return _call(seed, STORY_SYSTEM, user, [rid], schema,
                         request_schema=wide)

        for day in range(days_total):
            day_blocks: list[dict] = []
            summary = None
            n_calls += 1
            try:                                    # anchor, sequential
                parsed = _one(day, residents[0], _today_context([]))
                d0 = parsed["days"][0]
                summary = d0.get("summary", "")
                day_blocks += [dict(b, resident=residents[0])
                               for b in d0["blocks"]]
            except SpendCapExceeded:
                raise
            except Exception as e:
                failed_calls.append({"day": day, "resident": residents[0],
                                     "error": repr(e)[:200]})
                print(f"  day {day} {residents[0]}: STORY FAILED "
                      f"({type(e).__name__})")
            anchor_ctx = _today_context(day_blocks)
            rest = residents[1:]
            n_calls += len(rest)
            results: dict = {}
            if rest:
                with ThreadPoolExecutor(
                        max_workers=min(max_workers, len(rest))) as ex:
                    futs = {ex.submit(_one, day, rid, anchor_ctx): rid
                            for rid in rest}
                    for fut, rid in futs.items():
                        try:
                            results[rid] = fut.result()
                        except Exception as e:
                            results[rid] = e
            for rid in rest:                        # merge in RESIDENT order
                got = results.get(rid)
                if isinstance(got, SpendCapExceeded):
                    raise got
                if isinstance(got, Exception) or got is None:
                    failed_calls.append({"day": day, "resident": rid,
                                         "error": repr(got)[:200]})
                    print(f"  day {day} {rid}: STORY FAILED "
                          f"({type(got).__name__})")
                    continue
                dd = got["days"][0]
                if summary is None:
                    summary = dd.get("summary", "")
                day_blocks += [dict(b, resident=rid) for b in dd["blocks"]]
            if not day_blocks:
                continue                            # whole day lost
            day_blocks.sort(key=lambda b: (b["start"], b["resident"]))
            story.append({"day": day, "summary": summary or "",
                          "blocks": day_blocks})
            if out_hh is not None:
                _write_story(out_hh, program["household"], story)
            acts = {b["activity"] for b in day_blocks}
            print(f"  day {day}: {len(day_blocks)} blocks across "
                  f"{len({b['resident'] for b in day_blocks})} resident(s), "
                  f"{len(acts)} activities")

    call_stats = {"granularity": ("week" if per_week
                                  else ("day_resident" if per_resident
                                        else "day")),
                  "tag": tag, "n_calls": n_calls,
                  "n_failed_calls": len(failed_calls),
                  "max_retries": max_retries,
                  "max_tokens": STORY_MAX_TOKENS,
                  "n_repairs": len(repairs),
                  "repairs": repairs[:80]}
    if repairs:
        print(f"  [repair] {len(repairs)} deterministic fix(es) applied "
              f"(guided decoding would have made these unwritable): "
              f"{repairs[:6]}{'...' if len(repairs) > 6 else ''}")
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
