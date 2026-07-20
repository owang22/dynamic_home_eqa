"""
Non-persona LLM generation stages: activity trace, displacement, realism
judge, multi-occupant conflict verification. Stage 1 (persona) lives in
generation/persona/ — see that package for its schema, prompt, household
profile list, and generator.

Each stage is a separate LLM call with a separate prompt and guided decoding
schema. They must not be merged: timing does not need the inventory, and
displacement needs the inventory but not the full persona text.

All calls go through the ResponseCache so output is reproducible. Seed
derivation: make_seed(household_id, day, stage, occupant_index).

Model selection:
    Start with the largest locally-servable Qwen3 dense model. Model is a
    config string, not hardcoded — pass it in or set GENERATION_MODEL env var.
    Run stages 1–3 on a small scene sample and measure grounding survival rate
    before committing to a model. See grounding.py.

Temperature: nonzero (default 0.7) for generation diversity. The seed
provides reproducibility; caching provides exact regeneration.
"""
from __future__ import annotations

import hashlib
import json
import logging
from typing import Optional

from .cache import ResponseCache, make_seed
from .llm_client import DEFAULT_MODEL, DEFAULT_TEMPERATURE, _get_client, generate_json
from ..env.anchor_census import census_anchor_vocabulary
from .schemas import (
    ACTIVITY_SCHEMA,
    ACTIVITY_LOCATIONS,
    build_displacement_schema,
    build_realism_schema,
    filter_displacement_proposals,
)
from .prompt_registry import (
    ACTIVITY as _ACTIVITY_T,
    DAY_PLAN as _DAY_PLAN_T,
    ROUTINE_PROFILE as _PROFILE_T,
    CONFLICT_VERIFY as _CONFLICT_T,
    DISPLACEMENT as _DISPLACEMENT_T,
    REALISM_ASIS as _REALISM_ASIS_T,
    REALISM_STRICT as _REALISM_STRICT_T,
)

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_ACTIVITY_SYSTEM = _ACTIVITY_T.text

# ---------------------------------------------------------------------------
# Day-context scenarios — injected into the activity trace user message.
# day_type is drawn once per (household, day) so the whole household lives
# the same kind of day; each occupant then draws their OWN scenario within
# that day_type's pool (see _household_day_type/_occupant_day_scenario).
#
# Each entry is (text, day_type). day_type tells the model whether school/work
# away-time applies at all — without it, "school-age kids are away on a normal
# weekday" has nothing to check against, since prior scenario text never said
# whether the day even *was* a weekday:
#   "weekday" — school/work applies unless the text itself overrides it.
#   "weekend" — no school; work/commute only if the persona's habits say so.
#   "flex"    — day-of-week unspecified (illness, a visitor, a mood) — the
#               scenario text itself governs whether the occupant leaves, not
#               a default weekday/weekend assumption.
# ---------------------------------------------------------------------------

_DAY_SCENARIOS: list[tuple[str, str]] = [
    # --- Routine weekday variations ---
    ("Ordinary Tuesday. Nothing unusual planned; occupant follows their typical routine.", "weekday"),
    ("Slow Monday morning. Occupant woke up later than usual and feels sluggish getting started.", "weekday"),
    ("Efficient Wednesday. Occupant is energised and unusually productive; completes tasks faster than normal.", "weekday"),
    ("Friday afternoon wind-down. Work wraps early; the occupant transitions into weekend mode by mid-afternoon.", "weekday"),
    ("Deadline crunch day. Occupant has a hard deliverable due by end of day and works with few breaks.", "weekday"),

    # --- Weekend ---
    ("Leisurely Saturday morning. No alarm set; occupant sleeps in, makes an elaborate breakfast, reads.", "weekend"),
    ("Sunday errand day. Occupant spends a chunk of the morning out running errands, then returns to relax.", "weekend"),
    ("Lazy Sunday. Occupant barely leaves the living room; comfort food, screen time, minimal tidying.", "weekend"),
    ("Weekend home project. Occupant spends several hours reorganising a room, moving furniture, cleaning.", "weekend"),

    # --- Social / visitors ---
    ("Friend visiting in the evening. Occupant prepares the living area and kitchen in the afternoon.", "flex"),
    ("Small dinner party tonight. Occupant cooks a more involved meal than usual and sets the dining table.", "flex"),
    ("Partner or family member arriving home after a long trip. Occupant tidies up and prepares a welcome.", "flex"),
    ("Video call catch-up with distant family in the morning; rest of day is routine.", "weekday"),

    # --- Health / wellness ---
    ("Sick day. Occupant feels unwell — stays in bed or on the sofa most of the day, eats lightly. "
     "Skips school/work entirely regardless of what day it is.", "flex"),
    ("Recovery day after illness. Mostly resting, some light activity, appetite slowly returning. "
     "Still stays home from school/work.", "flex"),
    ("Gym morning. Occupant leaves early for exercise and returns hungry; eats a large breakfast.", "weekday"),
    ("Meditation and slow-start day. Occupant spends the first two hours on personal wellness before work.", "weekday"),

    # --- Disruptions / unexpected events ---
    ("Plumber or repair technician scheduled mid-morning. Occupant stays home and works around the visit.", "weekday"),
    ("Unexpected grocery run needed. Occupant discovers the fridge is nearly empty and heads out mid-day.", "flex"),
    ("Package deliveries expected. Occupant works from home but is interrupted several times.", "weekday"),
    ("Brief power outage in the morning disrupts the routine; occupant adapts and catches up later.", "weekday"),
    ("Bad weather (heavy rain or heat wave). Occupant cancels any outdoor plans and stays inside all day.", "flex"),

    # --- Emotional / energy state ---
    ("Low-motivation day. Occupant struggles to focus; takes more breaks and moves between rooms often.", "weekday"),
    ("Highly focused deep-work day. Occupant barely leaves the office; minimal kitchen visits.", "weekday"),
    ("Celebratory day (promotion, good news, birthday). Occupant is in high spirits; orders takeout or bakes.", "flex"),

    # --- Seasonal / time-of-year feel ---
    ("Hot summer afternoon. Occupant seeks cool rooms, drinks more water, avoids outdoor time.", "flex"),
    ("Cosy winter day. Occupant makes hot drinks frequently and stays near comfortable areas.", "flex"),
    ("Spring cleaning impulse. Occupant spends an extended session decluttering and reorganising.", "weekend"),
    ("Holiday eve. Occupant is in a festive mood, decorates or prepares special food, sleeps later.", "flex"),

    # --- Late-night / shifted schedule ---
    ("Night-shift schedule. Occupant's day is shifted — sleeps during morning hours, active at night.", "flex"),
    ("Late-night creative session. Occupant works or engages in a hobby well past midnight.", "flex"),
]


# Calendar mode (gen_dataset --calendar-days): day_type follows a real week
# (day 0 = Monday, days 5/6 = weekend) instead of the seeded pool draw. The
# pool draw gives each (household, day) an INDEPENDENT day type — fine for
# independent-day training data, but it means "day 5" is not Saturday and no
# weekly periodicity exists in the generated world at all, so a weekly
# belief component (dynbelief Section C) would be fitting pure noise. Off by
# default: flipping it changes day_type for existing (household, day) seeds,
# so old outputs stay reproducible only with the flag unset. The flex pool
# (night-shift/late-night scenarios) is unreachable in calendar mode; that
# lifestyle should come from persona habits instead.
_CALENDAR_DAYS = False
_DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
              "Saturday", "Sunday"]


def set_calendar_days(enabled: bool) -> None:
    global _CALENDAR_DAYS
    _CALENDAR_DAYS = enabled


def _day_label(day_type: str, day: int) -> str:
    """What the prompts see: "weekday (Tuesday)" in calendar mode so the
    model can write day-of-week-appropriate plans; bare day_type otherwise."""
    if _CALENDAR_DAYS:
        return f"{day_type} ({_DAY_NAMES[day % 7]})"
    return day_type


def _household_day_type(household_id: str, day: int) -> str:
    """The ONE day_type every member of this household lives on this day —
    seeded per (household, day) only, deliberately no occupant_index. Drawn
    by indexing the full scenario pool so the weekday/weekend/flex frequency
    follows the pool's own composition rather than a separate weight table.
    In calendar mode the calendar decides instead (see _CALENDAR_DAYS)."""
    if _CALENDAR_DAYS:
        return "weekend" if day % 7 >= 5 else "weekday"
    seed = make_seed(household_id, day, "day_type", 0)
    return _DAY_SCENARIOS[seed % len(_DAY_SCENARIOS)][1]


def _occupant_day_scenario(household_id: str, day: int, occupant_index: int,
                            day_type: str) -> str:
    """This occupant's own scenario, drawn WITHIN the household's shared
    day_type pool — same calendar day for everyone (household day-type
    coherence), but each member experiences their own version of it (the
    working adult's deadline crunch is not the toddler's slow morning). The
    scenario text and the persona both feed the trace LLM, which reconciles
    them into this occupant's day."""
    pool = [text for text, t in _DAY_SCENARIOS if t == day_type]
    seed = make_seed(household_id, day, "day_scenario", occupant_index)
    return pool[seed % len(pool)]

_DISPLACEMENT_SYSTEM = _DISPLACEMENT_T.text

_REALISM_SYSTEM = _REALISM_ASIS_T.text

# LLM Option Evaluation round, judge style B: same independence/tidiness
# framing as _REALISM_SYSTEM, but explicitly strict — built for the
# "over-generate varied proposals, select the good ones by design" flow,
# where the proposer is deliberately permissive and the judge is the
# quality gate. The score scale is anchored so most of a varied pool
# SHOULD land low.
_REALISM_SYSTEM_STRICT = _REALISM_STRICT_T.text

_MULTI_OCCUPANT_VERIFY_SYSTEM = _CONFLICT_T.text

_CONFLICT_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "conflicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "occupant":    {"type": "string"},
                    "start":       {"type": "number"},
                    "end":         {"type": "number"},
                    "description": {"type": "string"},
                },
                "required": ["occupant", "start", "end", "description"],
            },
        },
    },
    "required": ["conflicts"],
}


# ---------------------------------------------------------------------------
# Stage 2 — Activity trace (per occupant)
# ---------------------------------------------------------------------------

_GENERIC_OCCUPATIONS = {
    "toddler": {"toddler", "preschooler"},
    "young_child": {"student", "schoolchild", "child"},
    "older_child": {"student", "schoolchild"},
    "teen": {"student", "high", "schooler"},
    "senior": {"retiree", "retired", "senior"},
    "adult": {"homemaker", "parent"},
}
_STOP_WORDS = {"who", "the", "a", "an", "with", "and", "for", "their", "her",
               "his", "as", "at", "of", "to", "in", "on", "up", "works"}


def _profile_occupation_ok(occ: str, member: dict) -> bool:
    """Mechanical persona-consistency check: the profile occupation must
    share a content word with the member's own habits/role, or be a generic
    occupation allowed for their age band. This is the guard the stage1c
    postmortem demanded: a day-0 hallucinated occupation ("night-shift
    nurse" for a yoga instructor) must fail loudly, not become 12 days of
    alternate reality."""
    words = {w.strip(".,;") for w in occ.lower().split()} - _STOP_WORDS
    profile = (str(member.get("habits", "")) + " " + str(member.get("role", ""))).lower()
    if any(w and w in profile for w in words):
        return True
    allowed = _GENERIC_OCCUPATIONS.get(member.get("age_band", "adult"), set())
    return bool(words & allowed)


def _fallback_profile(persona: dict) -> dict[str, dict]:
    """Deterministic no-LLM profile straight from the persona — used when
    generation fails validation after retries. Boring but never wrong."""
    out = {}
    for o in persona.get("occupants", []):
        habits = str(o.get("habits", ""))
        out[o.get("name", "")] = {
            "occupation": o.get("role", "member"),
            "weekday_routine": f"Follows their usual weekday pattern: {habits}",
            "weekend_routine": f"A typical weekend day, per their habits: {habits}",
            "signature_habits": [h.strip() for h in habits.split(";") if h.strip()][:4],
        }
    return out


def generate_routine_profile(
    persona: dict,
    household_id: str,
    model: str = DEFAULT_MODEL,
    cache: Optional[ResponseCache] = None,
    force: bool = False,
) -> dict[str, dict]:
    """One guided call per HOUSEHOLD (not per day): the stable weekly routine
    each member repeats, validated against the persona. Returns
    {name: {occupation, weekday_routine, weekend_routine, signature_habits}}.
    Cached by household seed, so every day of every run renders the same
    profile."""
    occupants = persona.get("occupants", [])
    names = [o.get("name") for o in occupants]
    if not names:
        return {}
    stage = _PROFILE_T.tag("routine_profile", builder=True)
    seed = make_seed(household_id, 0, stage, 0)
    lines = [
        f"- {o.get('name')}: age_band={o.get('age_band', 'adult')}, "
        f"role={o.get('role', 'member')}, wake={o.get('typical_wake', 7.0)}, "
        f"sleep={o.get('typical_sleep', 22.0)}, "
        f"habits={o.get('habits', 'none given')}"
        for o in occupants
    ]
    user = ("Household members:\n" + "\n".join(lines)
            + "\n\nWrite the routine profile for every member.")
    schema = {
        "type": "object",
        "properties": {"occupants": {
            "type": "array", "minItems": len(names), "maxItems": len(names),
            "items": {"type": "object", "properties": {
                "name": {"type": "string", "enum": names},
                "occupation": {"type": "string", "maxLength": 60},
                "weekday_routine": {"type": "string", "maxLength": 500},
                "weekend_routine": {"type": "string", "maxLength": 500},
                "signature_habits": {"type": "array", "minItems": 2, "maxItems": 4,
                                      "items": {"type": "string", "maxLength": 120}},
            }, "required": ["name", "occupation", "weekday_routine",
                             "weekend_routine", "signature_habits"]},
        }},
        "required": ["occupants"],
    }
    by_name = {o.get("name"): o for o in occupants}

    def _validate(result: dict) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for e in (result.get("occupants", []) if isinstance(result, dict) else []):
            nm = str(e.get("name", "")).strip()
            if nm not in by_name:
                continue
            if not _profile_occupation_ok(str(e.get("occupation", "")), by_name[nm]):
                raise ValueError(
                    f"profile occupation {e.get('occupation')!r} contradicts "
                    f"{nm}'s profile — regenerate")
            out[nm] = {k: e[k] for k in ("occupation", "weekday_routine",
                                          "weekend_routine", "signature_habits")}
        missing = [n for n in names if n not in out]
        if missing:
            raise ValueError(f"profile missing members {missing!r}")
        return out

    client = _get_client(model)
    try:
        return generate_json(
            client, _PROFILE_T.text, user, schema,
            seed=seed, stage=stage, cache=cache, force=force, validate=_validate,
        )
    except Exception as exc:
        _logger.warning("routine profile failed for %s (%s) — mechanical fallback",
                        household_id, exc)
        return _fallback_profile(persona)


def generate_day_plan(
    persona: dict,
    household_id: str,
    day: int,
    day_type: str,
    profile: Optional[dict] = None,
    event_note: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    cache: Optional[ResponseCache] = None,
    force: bool = False,
) -> dict[str, str]:
    """Household-level day planning — one THINKING-model call per
    (household, day) that writes each member's day scenario from their own
    profile, replacing the persona-blind template draw (which produced
    meditating toddlers and teens who skip school to supervise plumbers).

    day_type stays a deterministic household draw (_household_day_type) and
    is handed to the model as a constraint, so the weekday/weekend/flex mix
    keeps following the scenario pool's composition. Thinking mode is safe
    here by the established rule (see generate_thinking's docstring): the
    output carries no vocabulary claims — free-text scenarios only, no
    anchors/categories — and its shape is normalized by `_validate` with
    retries. On total failure the caller falls back to the template pool,
    so a day always has scenarios.

    Returns {occupant_name: scenario}; {} on failure (caller falls back).
    Cached per (household, day, day_type, prompt version) — every occupant's
    trace call hits the same cached plan.
    """
    occupants = persona.get("occupants", [])
    if not occupants:
        return {}
    # calendar mode folds the day name into the tag: the response cache is
    # keyed by seed alone, so a Tuesday plan must never replay a cached
    # pool-draw plan generated under the same (household, day)
    profile = profile or {}
    tag = f"day_plan_{day_type}" + (f"_cal{day % 7}" if _CALENDAR_DAYS else "")
    # cache keys are seed-only: a plan rendered under a different profile or
    # scheduled event must never replay a stale entry
    ctx_text = json.dumps(profile, sort_keys=True) + "|" + (event_note or "")
    tag += "_ch" + hashlib.sha256(ctx_text.encode()).hexdigest()[:8]
    stage = _DAY_PLAN_T.tag(tag, builder=True)
    seed = make_seed(household_id, day, stage, 0)
    lines = [
        f"- {o.get('name')}: age_band={o.get('age_band', 'adult')}, "
        f"role={o.get('role', 'member')}, habits={o.get('habits', 'none given')}"
        for o in occupants
    ]
    profile_lines = []
    for nm, ch in profile.items():
        routine = ch.get("weekend_routine" if day_type == "weekend" else "weekday_routine", "")
        profile_lines.append(f"- {nm} ({ch.get('occupation', '?')}): {routine} "
                             f"Signature habits: {'; '.join(ch.get('signature_habits', []))}")
    user = (
        f"Day type: {_day_label(day_type, day)}\n"
        f"Household members:\n" + "\n".join(lines) + "\n\n"
        f"Routine profile (authoritative for this day type):\n"
        + "\n".join(profile_lines) + "\n\n"
        f"Today's scheduled event: {event_note or 'none — ordinary day'}\n\n"
        "Render this household's day and write each member's scenario."
    )
    names = [o.get("name") for o in occupants]

    def _validate(result: dict) -> dict[str, str]:
        plan: dict[str, str] = {}
        entries = result.get("occupants", []) if isinstance(result, dict) else []
        for e in entries:
            if isinstance(e, dict) and e.get("name") and e.get("scenario"):
                plan[str(e["name"]).strip()] = str(e["scenario"]).strip()
        missing = [n for n in names if n not in plan]
        if missing:
            raise ValueError(f"day plan missing scenarios for {missing!r}")
        return plan

    client = _get_client(model)
    try:
        if "qwen3" in model.lower():
            # Qwen3: thinking mode (no guided decoding possible alongside a
            # think block — see generate_thinking's docstring).
            from .llm_client import generate_json_thinking
            return generate_json_thinking(
                client, _DAY_PLAN_T.text, user,
                seed=seed, stage=stage, cache=cache, force=force, validate=_validate,
            )
        # Other model families (Llama, ...): no think block, so guided JSON
        # is available — same plan contract, schema-enforced shape, with the
        # occupant names enum-pinned so the plan can't drift from the persona.
        schema = {
            "type": "object",
            "properties": {
                "household_context": {"type": "string"},
                "occupants": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "enum": names},
                            "scenario": {"type": "string"},
                        },
                        "required": ["name", "scenario"],
                    },
                    "minItems": len(names), "maxItems": len(names),
                },
            },
            "required": ["household_context", "occupants"],
        }
        return generate_json(
            client, _DAY_PLAN_T.text, user, schema,
            seed=seed, stage=stage, cache=cache, force=force, validate=_validate,
        )
    except Exception as exc:
        _logger.warning("day plan failed for %s day %s (%s) — template fallback", household_id, day, exc)
        return {}


def generate_activity_trace(
    persona: dict,
    occupant_name: str,
    occupant_index: int,
    household_id: str,
    day: int,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    cache: Optional[ResponseCache] = None,
    force: bool = False,
    variant_tag: str = "",
    conflict_context: str = "",
    profile: Optional[dict] = None,
    event_note: Optional[str] = None,
) -> dict:
    """Generate a day's activity trace for one occupant.

    Returns the parsed activity trace dict.

    Args:
        persona:         Output from generate_persona().
        occupant_name:   Name of the occupant to generate a trace for.
        occupant_index:  Index within the persona's occupant list (for seed derivation).
        household_id:    Unique household ID (for seed derivation).
        day:             Day index (different days → different seeds → different traces).
        variant_tag:     Folded into the seed's stage string to get a DISTINCT
                         but still deterministic (cacheable) trace for the same
                         occupant — used by the conflict-resolution pass to
                         resample a conflicting occupant without either reusing
                         the cached original or force-regenerating
                         non-reproducibly (see verification.resolve_conflicts).
        conflict_context: "Coordination notes" appended to the request — the
                         detected clashes with other occupants' plans this
                         regeneration must plan around ("Sarah also wants the
                         kitchen at 12:00, ..."). Without it, the conflict-
                         resolution pass just resampled blind and hoped the
                         clash vanished by luck. Folded into the stage tag
                         (content hash) so different conflict sets never
                         share a cache entry.
    """
    # Day-type coherence, two levels: day_type is drawn ONCE per (household,
    # day) — everyone lives the same calendar day (it previously hung off the
    # per-occupant seed, giving one home a weekday and a weekend
    # simultaneously) — while each occupant's SCENARIO is their own draw
    # within that shared day_type's pool, so members experience individual
    # versions of the same kind of day. Both are folded into the stage tag
    # below because the response cache is keyed by seed alone, not prompt
    # text — without it, traces generated under other contexts would replay
    # from cache.
    day_type = _household_day_type(household_id, day)
    plan = generate_day_plan(persona, household_id, day, day_type,
                             profile=profile, event_note=event_note,
                             model=model, cache=cache, force=force)
    day_text = plan.get(occupant_name) or _occupant_day_scenario(
        household_id, day, occupant_index, day_type)
    # the occupant's profile routine rides along into the trace prompt so the
    # schedule stays anchored to the household's stable pattern, not just to
    # today's one-line scenario
    _ch = (profile or {}).get(occupant_name, {})
    routine_text = _ch.get("weekend_routine" if day_type == "weekend"
                           else "weekday_routine", "")

    base = "activity" + (f"_{variant_tag}" if variant_tag else "")
    base += "_dc" + hashlib.sha256(
        f"{_day_label(day_type, day)}|{day_text}|{routine_text}".encode()).hexdigest()[:8]
    if conflict_context:
        base += "_cc" + hashlib.sha256(conflict_context.encode()).hexdigest()[:8]
    stage = _ACTIVITY_T.tag(base, builder=True)
    seed = make_seed(household_id, day, stage, occupant_index)

    # Pull the occupant's role, schedule, and tidiness from the persona.
    # tidiness is per-occupant (not a household-wide average), so it comes
    # from here, not from the persona dict's top level.
    occupant_info = next(
        (o for o in persona.get("occupants", []) if o["name"] == occupant_name),
        {"name": occupant_name, "role": "unknown", "age_band": "adult",
         "typical_wake": 7.0, "typical_sleep": 22.0, "habits": "", "tidiness": 0.5},
    )
    user = (
        f"Occupant: {occupant_name} ({occupant_info.get('role', 'unknown')}), "
        f"age_band={occupant_info.get('age_band', 'adult')}\n"
        f"Habits: {occupant_info.get('habits', 'none given')}\n"
        f"Household type: {persona.get('household_type', 'unknown')}\n"
        f"Tidiness level: {occupant_info.get('tidiness', 0.5):.1f}/1.0\n"
        f"Schedule notes: {persona.get('schedule_notes', 'none')}\n"
        f"Typical wake: {occupant_info.get('typical_wake', 7.0):.1f}h  "
        f"Typical sleep: {occupant_info.get('typical_sleep', 22.0):.1f}h\n"
        f"Day type: {_day_label(day_type, day)}\n"
        + (f"Stable routine (repeats week after week): {routine_text}\n" if routine_text else "")
        + f"Day context: {day_text}\n"
        + (f"\nCoordination notes — this occupant's previous plan clashed with other "
           f"household members'; plan around these (see system prompt):\n{conflict_context}\n"
           if conflict_context else "")
        + f"\nGenerate a full day's activity trace for {occupant_name}, reflecting their habits."
    )

    def _validate(result: dict) -> dict:
        result["activities"] = _repair_activity_trace(result.get("activities", []))
        return result

    client = _get_client(model)
    trace = generate_json(
        client, _ACTIVITY_SYSTEM, user, ACTIVITY_SCHEMA,
        seed=seed, stage=stage, cache=cache, force=force, validate=_validate,
        temperature=temperature,
    )
    # Persist the day context that shaped this trace (weekday/weekend/flex and
    # the specific scenario text, e.g. a dinner party or errand day). It drives
    # the schedule but was previously prompt-only — invisible in the output, so
    # a reviewer couldn't tell what kind of day it was. Kept on the trace so it
    # rides along into generation_result["traces"] and the manifest.
    trace["day_type"] = day_type
    trace["day_context"] = day_text
    return trace


def _repair_activity_trace(activities: list[dict]) -> list[dict]:
    """Deterministically clip overlapping activity windows.

    "Contiguous and non-overlapping" is prose-only in the prompt — there's no
    JSON Schema keyword for "sorted, non-overlapping array" the way there's an
    enum for location or a min/max for sleep hour, so this holds the
    guarantee in code instead of hoping the model complies across a long
    per-day array. Walks the array in generation order (not re-sorted — the
    model's own convention puts an overnight-wraparound sleep block first
    and/or last, and reordering would break that) and clips each activity's
    end to the next activity's start whenever they overlap. Wraparound
    entries (end <= start, i.e. spanning midnight) are left untouched since
    they're expected to extend past the array's own bounds.
    """
    if len(activities) < 2:
        return activities
    repaired = [dict(a) for a in activities]
    was_wraparound = [a["end"] <= a["start"] for a in repaired]
    for i in range(len(repaired) - 1):
        cur, nxt = repaired[i], repaired[i + 1]
        if was_wraparound[i]:
            continue
        if nxt["start"] < cur["end"]:
            cur["end"] = max(nxt["start"], cur["start"])
    # Drop only entries clipping produced as degenerate (start==end); a
    # wraparound entry (end <= start) is legitimate and must survive this
    # filter, not just the loop above — checking "end > start" alone would
    # wrongly treat every wraparound sleep block as degenerate and drop it.
    return [a for a, wrapped in zip(repaired, was_wraparound) if wrapped or a["end"] > a["start"]]


# ---------------------------------------------------------------------------
# Stage 3 — Displacement proposals (per activity)
# ---------------------------------------------------------------------------

def generate_displacements(
    activity: str,
    start: float,
    end: float,
    occupant_name: str,
    occupant_index: int,
    persona: dict,
    inventory: dict[str, int],
    room_inventory: dict[str, dict[str, int]] | None,
    household_id: str,
    day: int,
    location: Optional[str] = None,
    anchor_inventory: dict[str, int] | None = None,
    anchor_census: Optional[dict] = None,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    cache: Optional[ResponseCache] = None,
    force: bool = False,
    trace: Optional[dict] = None,
    include_context: bool = False,
    bedroom_index: Optional[int] = None,
    current_state_block: Optional[str] = None,
    live_occupancy: Optional[dict] = None,
    allow_put_away: bool = False,
    seat_instances: Optional[dict] = None,
    revision_feedback: Optional[str] = None,
) -> dict:
    """Propose object displacements for one activity.

    seat_instances — {instance_id: current slot} for the floor-bound seats
    (chair/stool) currently in the occupant's room (RunningState.
    seat_instances_in_room). When given, the schema's object vocabulary
    offers those INSTANCE ids ("stool_2") in place of the bare seat
    category, so the model commits to a specific seat — the fix for two
    occupants' category-level proposals silently resolving onto the same
    chair. The state block lists each instance's current slot, so the model
    can pick one that isn't already in use. The pipeline normalizes the
    token back to (category, _instance) before grounding.

    Phase 2 enrichment (default off, so the baseline is unchanged):
      include_context — prepend the occupant_card / temporal_context /
        surface_occupancy blocks (needs `trace` for the activities-so-far
        sequence), so the proposer knows who is acting and when.
      bedroom_index — when location == "bedroom", scope the anchor vocabulary
        to THIS occupant's own bedroom (bedroom_<index>.*), not every bedroom
        in the scene — the fix for the bedroom_1 monopoly.

    Returns the parsed displacement dict with proposals pre-filtered to valid
    PARTNR relationship strings.

    Args:
        activity:      Activity label (e.g. "breakfast", "work_at_desk").
        start, end:    Activity start/end hours.
        occupant_name: Name of the occupant performing the activity.
        inventory:     {category: count} for the scene (from inventory.py).
        room_inventory: {room: {category: count}} (optional, for richer context).
        location:      The occupant's activity.location for this window (one
                       of rooms.CANONICAL_ROOMS) — the room the occupant is
                       physically in while this activity happens. When given,
                       target_anchor is additionally scoped to anchors in
                       *this room only* (census_anchor_vocabulary on the
                       census path; rooms.anchors_in_room on the legacy
                       fallback), not the whole-scene census.
                       Without this, the model could — and did, on real
                       generated output — place an object in the bedroom
                       while the occupant's trace says they're in the
                       kitchen; nothing prevented it because the anchor
                       vocabulary spanned every room in the scene regardless
                       of where the activity said the occupant was. None
                       (e.g. the not-yet-wired WorldGraph path) falls back to
                       the whole-scene vocabulary, same as before this param
                       existed.
        anchor_inventory: {furniture_category: count} of real anchor-capable
                       furniture in this scene (env.inventory.ANCHOR_CATEGORIES
                       census). LEGACY-FALLBACK ONLY now (see anchor_census):
                       used when no anchor census exists for this scene.
        anchor_census: the realizable-anchor census (env/anchor_census.py's
                       load_anchor_census output) — the Part A vocabulary
                       source. When present, target_anchor enums are
                       room-qualified census INSTANCE labels
                       ("kitchen.counter_2"), split surface-vs-proximity by
                       receptacle backing and scoped to the occupant's
                       current room only — no CATEGORY_ROOM_HINT and no
                       scene-wide anchor_inventory fallback on this path: a
                       room with few/no valid surfaces gets a small enum
                       plus the "none" abstain entry, which is correct, not
                       a gap to paper over. None (no census computed for
                       this scene, or the WorldGraph path) falls back to
                       the legacy bare-category vocabulary with a loud
                       warning.

    object_category and target_anchor are constrained via guided-decoding enum
    to this scene's real vocabulary (see schemas.build_displacement_schema) so
    the model cannot hallucinate a synonym category or anchor, and target_anchor
    is relation-conditional (room names only for in_region, furniture categories
    otherwise) so it cannot pair "on" with a room name either. Using
    anchor_inventory (rather than the abstract slot vocabulary) means every
    furniture anchor the model can emit is guaranteed to actually exist in
    this scene — grounding's anchor-existence check is built from the same
    census, so the two stay consistent by construction.
    """
    from .inventory import format_inventory_for_prompt
    from ..env.deltas import FURNITURE_TYPE_TO_SLOT
    from ..rooms import anchors_in_room
    # start disambiguates repeat occurrences of the same activity label within
    # a day (e.g. "work" split across four windows, "brush_teeth" twice) — the
    # seed used to be keyed on activity label alone, so every recurrence
    # collided on the same cache entry and reused byte-identical proposals.
    _base = "displacement" + ("_ctx" if include_context else "")
    if current_state_block:
        # Phase 3: the proposal depends on the running world state; fold its
        # hash into the tag so later windows never serve a stale cached call.
        _base += "_st" + hashlib.sha256(current_state_block.encode()).hexdigest()[:8]
    if revision_feedback:
        # judge-retry revision round: distinct cache entry per feedback set
        _base += "_rev" + hashlib.sha256(revision_feedback.encode()).hexdigest()[:8]
    _stage_tag = _DISPLACEMENT_T.tag(_base, builder=True)
    seed = make_seed(household_id, day, f"{_stage_tag}_{activity}_{start:.2f}", occupant_index)

    # tidiness is per-occupant, not a household average — look up this
    # occupant's own value rather than a persona-level field.
    occupant_info = next(
        (o for o in persona.get("occupants", []) if o["name"] == occupant_name),
        {"role": "", "tidiness": 0.5},
    )
    inv_text = format_inventory_for_prompt(inventory, room_inventory)
    location_line = f"Occupant's current room: {location}\n" if location else ""
    if include_context:
        # occupant_card carries role/age/tidiness/ownership/bedroom; temporal
        # context the clock time + activities so far; current_state_block (Phase
        # 3) the authoritative running object state; surface occupancy the
        # objects on the room's anchors (live from running state when given).
        from .context import occupant_card, surface_occupancy, temporal_context
        ctx = [occupant_card(persona, occupant_name),
               temporal_context(trace, start, end)]
        if current_state_block:
            ctx.append(current_state_block)
        so = surface_occupancy(location, live_occupancy if live_occupancy is not None else room_inventory,
                               live=live_occupancy is not None)
        if so:
            ctx.append(so)
        header = "\n".join(ctx) + "\n\n"
    else:
        header = (f"Occupant: {occupant_name} ({occupant_info.get('role', '')})\n"
                  f"{location_line}"
                  f"Household tidiness: {occupant_info.get('tidiness', 0.5):.1f}/1.0\n")
    user = (
        f"{header}"
        f"Activity: {activity} ({start:.1f}h – {end:.1f}h)\n"
        f"\n{inv_text}\n"
        f"\nPropose object displacements caused by this activity."
    )

    # Only offer categories that can actually be MOVED — Tier-1 fixtures
    # (fridge, tv, wardrobe, counter, ...) are placement anchors, not carried
    # objects, and the proposer must never suggest relocating them.
    from ..env.inventory import FLOOR_BOUND_CATEGORIES, MOVABLE_CATEGORIES
    valid_categories = [c for c in sorted(inventory.keys()) if c in MOVABLE_CATEGORIES] or ["object"]
    if seat_instances:
        # Seats are proposed by INSTANCE id, never by bare category: replace
        # "chair"/"stool" with the ids of the instances actually in this room
        # (see docstring). A seat category with no in-room instance was
        # already excluded by the pipeline's seat-in-room vocabulary gate.
        valid_categories = [c for c in valid_categories if c not in FLOOR_BOUND_CATEGORIES]
        valid_categories += sorted(seat_instances.keys())
        valid_categories = valid_categories or ["object"]

    if anchor_census is not None:
        # Part A: room-scoped census instance labels, surface-vs-proximity
        # split by real receptacle backing. Current-room-only (the
        # conservative choice, matching the prior room-scoping behavior);
        # location=None (shouldn't happen on the census path — pipeline
        # skips "away" activities and every other location is canonical)
        # degrades to the whole-scene census rather than inventing rooms.
        # Deliberately NO fallback to CATEGORY_ROOM_HINT or scene-wide
        # anchor_inventory here: an empty/small list plus the schema's own
        # "none" abstain entry IS the correct vocabulary for a room with
        # no valid surfaces.
        surface_anchors, proximity_anchors = census_anchor_vocabulary(anchor_census, location)
        # Bedroom scoping: a "bedroom" activity resolves to THIS occupant's own
        # bedroom_<index> anchors only, so each occupant animates their own
        # room rather than everyone piling into bedroom_1. Falls back to all
        # bedroom anchors if the scene has fewer bedrooms than the index.
        if location == "bedroom" and bedroom_index is not None:
            pref = f"bedroom_{bedroom_index}."
            s = [a for a in surface_anchors if a.startswith(pref)]
            p = [a for a in proximity_anchors if a.startswith(pref)]
            surface_anchors, proximity_anchors = (s or surface_anchors), (p or proximity_anchors)
        # Tuckable anchors: this room's census instances a chair/stool can be
        # tucked back under (the inverse of pulling one out via next_to).
        from ..rooms import census_label_parts
        _TUCKABLE = {"table", "counter", "desk"}
        tuck_anchors = [
            a for a in proximity_anchors
            if (parts := census_label_parts(a)) is not None and parts[1] in _TUCKABLE
        ]
        # Concealment vocabulary: census anchors whose category is closed
        # storage (cabinet/wardrobe/fridge/...) accept `inside` as a put-away
        # (see CONCEALING_STORAGE_CATEGORIES) regardless of receptacle backing.
        from ..env.inventory import CONCEALING_STORAGE_CATEGORIES
        conceal_anchors = [
            a for a in set(surface_anchors) | set(proximity_anchors)
            if (parts := census_label_parts(a)) is not None
            and parts[1] in CONCEALING_STORAGE_CATEGORIES
        ]
        schema = build_displacement_schema(valid_categories, surface_anchors, proximity_anchors,
                                           include_put_away=allow_put_away, tuck_anchors=tuck_anchors,
                                           conceal_anchors=conceal_anchors)
    else:
        _logger.warning(
            "generate_displacements: no anchor census for this scene — falling back to the "
            "legacy bare-category anchor vocabulary (run scripts/compute_anchor_census.py "
            "to enable room-qualified instance anchors)"
        )
        # Legacy vocabulary (pre-Part-A): bare categories, room-scoped via
        # anchors_in_room's own CATEGORY_ROOM_HINT/scene-wide fallbacks.
        room_furniture_anchors = anchors_in_room(location, room_inventory, anchor_inventory) if location else []
        valid_furniture_anchors = (
            room_furniture_anchors
            or (sorted(anchor_inventory.keys()) if anchor_inventory else sorted(FURNITURE_TYPE_TO_SLOT.keys()))
            or ["furniture"]
        )
        schema = build_displacement_schema(valid_categories, valid_furniture_anchors, valid_furniture_anchors, include_put_away=allow_put_away)

    if revision_feedback:
        user += (
            "\n\nREVISION ROUND — a realism reviewer rejected some of your earlier "
            "proposals for this activity. Each line below gives the rejected move, "
            "your original reason, the reviewer's critique, and (when present) a "
            "suggested fix. Propose a REVISED set addressing the critiques: usually "
            "that means moving the object to the destination your own reasoning "
            "supports, or picking a more sensible object/destination. Drop any move "
            "that cannot be fixed; do NOT re-propose a rejected move unchanged, and "
            "do NOT re-propose moves that were already accepted.\n"
            + revision_feedback)
    client = _get_client(model)
    return generate_json(
        client, _DISPLACEMENT_SYSTEM, user, schema,
        seed=seed, stage=_stage_tag, cache=cache, force=force,
        validate=filter_displacement_proposals,
        temperature=temperature,
    )


# ---------------------------------------------------------------------------
# Stage 3.5 — Realism judge (per grounded candidate, batched per activity)
# ---------------------------------------------------------------------------

class PartialJudgeScores(ValueError):
    """Judge returned scores for only a subset of the candidates.

    Subclasses ValueError so generate_json/generate_json_thinking treat it
    as a retryable failure (same path as a JSON parse failure). Carries the
    partial scores so the caller can apply an explicit fallback if every
    retry exhausts — never a silent per-candidate default."""

    def __init__(self, scores: dict, missing: list[int], n_candidates: int) -> None:
        self.scores = scores
        self.missing = missing
        super().__init__(
            f"judge returned {len(scores)}/{n_candidates} scores "
            f"(missing candidate indices: {missing})"
        )


_SCORE_KEYS = ("score", "realism_score", "value", "rating")


def _entry_score(entry: dict) -> float:
    """Pull the numeric score out of a judge entry dict, tolerating the key
    aliases the UNGUIDED thinking-mode judge drifts to (realism_score, ...) —
    the guided judge always emits `score`, but thinking mode has no grammar
    to hold it to that."""
    for key in _SCORE_KEYS:
        if key in entry:
            return float(entry[key])
    raise KeyError("score")


def _normalize_judge_scores(result, n_candidates: int) -> dict:
    """Canonical {int index: {"score": float, "reason": str}} from any of the
    judge output shapes observed in the real thinking-mode comparison
    (results/reports/llm_comparison/thinking_vs_moe.md): the schema's
    {"scores": [{candidate_index, reason, score}]} array, a {"scores":
    {"0": 0.6}} dict, a flat {"0": 0.9} dict, or a bare list of
    floats/dicts. `reason` is the judge's own pre-score evidence weighing
    (guided schema orders it before the score; "" for shapes that lack it).
    Raises ValueError on anything else, and PartialJudgeScores when any
    candidate index is missing — both trigger the caller's retry."""
    def _entry(v) -> dict:
        if isinstance(v, dict):
            return {"score": _entry_score(v), "reason": str(v.get("reason", "")),
                    "fix": str(v.get("fix", ""))}
        return {"score": float(v), "reason": "", "fix": ""}

    scores = result.get("scores", result) if isinstance(result, dict) else result
    out: dict = {}
    if isinstance(scores, list):
        for i, entry in enumerate(scores):
            idx = int(entry.get("candidate_index", i)) if isinstance(entry, dict) else i
            out[idx] = _entry(entry)
    elif isinstance(scores, dict):
        for k, v in scores.items():
            out[int(k)] = _entry(v)
    else:
        raise ValueError(f"unrecognized judge output shape: {type(scores).__name__}")
    # Any candidate without a score is partial coverage — INCLUDING the
    # degenerate all-empty {"scores": []} the judge sometimes emits, which
    # is 0-of-N covered, not a distinct failure. Both take the retry-then-
    # style-dependent-fallback path in score_realism_batch; neither is ever
    # a silent per-candidate default, and an empty response must not crash
    # the whole scene.
    missing = [i for i in range(n_candidates) if i not in out]
    if missing:
        _logger.warning(
            "judge returned %d/%d scores (missing candidate indices: %s)",
            len(out), n_candidates, missing,
        )
        raise PartialJudgeScores(out, missing, n_candidates)
    return out


def score_realism_batch(
    candidates: list[dict],
    activity: str,
    occupant_name: str,
    persona: dict,
    household_id: str,
    day: int,
    start: float = 0.0,
    occupant_index: int = 0,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    cache: Optional[ResponseCache] = None,
    force: bool = False,
    judge_thinking: bool = False,
    judge_style: str = "asis",
    end: float = 0.0,
    trace: Optional[dict] = None,
    include_context: bool = False,
    exemplar_block: Optional[str] = None,
    sample_index: int = 0,
    judge_client=None,
    model_tag: str = "",
    current_state_block: Optional[str] = None,
    request_fix: bool = False,
    round_tag: str = "",
) -> tuple[list[float], dict]:
    """Score behavioral plausibility for a pool of grounded displacement candidates.

    Phase 2 judge knobs (all default off, so the baseline is unchanged):
      include_context — prepend the occupant_card + temporal_context blocks
        (needs `trace` for the activity-so-far sequence and `end` for the
        window clock time), so the judge knows who the occupant is and when.
      exemplar_block — a few-shot exemplar string (judge_eval.exemplars);
        switches the system prompt to the strict+few-shot template whose
        version hashes the exemplars (clean cache split).
      sample_index — self-consistency sample id; folded into the tag when >0
        so each of a k>1 run's samples gets a distinct, cacheable seed. The
        caller (harness) takes the per-candidate median across samples.

    A separate LLM call from displacement generation and from grounding: this
    judges plausibility, not placeability. Only call this on candidates that
    already passed grounding — scoring ungroundable candidates wastes judge
    calls on proposals that can never be selected.

    Candidates are batched into one call per activity for efficiency, but the
    prompt instructs the model to score each independently rather than rank
    the pool — batching must not reintroduce the "see everything, pick
    favorites" bias this stage exists to avoid.

    start disambiguates repeat occurrences of the same activity label within a
    day, same reason as generate_displacements — without it, two windows of
    the same activity share a cache entry and get byte-identical scores.

    judge_thinking (LLM Option Evaluation round, Arm 1): score with Qwen3
    thinking mode — no guided decoding (impossible alongside a think
    block on this vLLM version), shapes normalized by
    _normalize_judge_scores, reasoning trace stored in the cache entry.
    The judge is the SAFE stage for thinking (its output carries no
    vocabulary claims — scores only); the proposer is not (see
    generate_thinking's docstring). judge_style: "asis" (_REALISM_SYSTEM)
    or "strict" (_REALISM_SYSTEM_STRICT — calibrated for an
    over-generated pool where most candidates should score low). Both
    knobs are folded into the seed's stage string, per the cache-key
    precedent, so arms never replay each other's cached scores.

    Coverage: the judge must score every candidate. A response covering
    only a subset is a retryable failure (PartialJudgeScores, same path
    as a JSON parse failure). If every retry exhausts, missing scores
    default to 0.0 under judge_style="strict" (an unscored candidate in
    an over-generated pool must not be selectable by default) and to the
    schema midpoint 0.5 otherwise — logged as an error either way, never
    silent.

    Returns (scores, judge_meta): scores is a list in [0, 1] parallel to
    `candidates`; judge_meta carries provenance for persistence —
    {"stage_tag", "seed", "think" (truncated excerpt, "" when absent),
    "score_fallback" (missing-index list, only present on retry
    exhaustion)}.
    """
    if not candidates:
        return [], {"stage_tag": "", "seed": 0, "think": ""}

    from .context import candidate_line, occupant_card, temporal_context

    if exemplar_block:
        from .prompt_registry import realism_strict_fewshot
        template = realism_strict_fewshot(exemplar_block)
    else:
        template = _REALISM_STRICT_T if judge_style == "strict" else _REALISM_ASIS_T
    base = "realism"
    if judge_thinking:
        base += "_think"
    if judge_style != "asis":
        base += f"_{judge_style}"
    if include_context:
        base += "_ctx"
    if exemplar_block:
        base += "_fs"
    if current_state_block:
        base += "_st" + hashlib.sha256(current_state_block.encode()).hexdigest()[:8]
    if model_tag:
        base += f"_m{model_tag}"
    if sample_index:
        base += f"_s{sample_index}"
    # judge-retry plumbing: request_fix marks the round-1 call (fix field in
    # schema + user instruction); round_tag separates the round-2 kill-only
    # call's cache entries from round 1's (same window, different pool).
    if request_fix:
        # "_fixh" (not "_fix"): the hopeless-sentinel instruction changed the
        # fix contract, and the marker rename invalidates exactly the round-1
        # fix-requesting judge entries — everything else (profiles, plans,
        # traces, displacements, kill-only judges) replays from cache
        base += "_fixh"
    if round_tag:
        base += f"_{round_tag}"
    stage_tag = template.tag(base, builder=True)
    seed = make_seed(household_id, day, f"{stage_tag}_{activity}_{start:.2f}", occupant_index)

    # tidiness is per-occupant, not a household average.
    occupant_tidiness = next(
        (o.get("tidiness", 0.5) for o in persona.get("occupants", []) if o.get("name") == occupant_name),
        0.5,
    )
    n = len(candidates)
    lines: list[str] = []
    if include_context:
        # occupant_card carries role/age/tidiness/ownership/bedroom; temporal
        # context the clock time and today's activities so far; current_state
        # block (Phase 3) the authoritative running object state.
        lines.append(occupant_card(persona, occupant_name))
        lines.append(temporal_context(trace, start, end))
        if current_state_block:
            lines.append(current_state_block)
        lines.append(f"Activity: {activity}")
    else:
        lines.append(f"Activity: {activity}")
        lines.append(f"Occupant: {occupant_name}")
        lines.append(f"Household tidiness: {occupant_tidiness:.1f}/1.0")
    lines.append("")
    lines.append(
        f"Score all {n} candidate(s) below — output exactly {n} score object(s), "
        f"one per candidate, using its candidate_index (0..{n - 1}):"
    )
    if request_fix:
        # instruction lives in the USER message, not the template: the
        # round-2 judge must run the unmodified kill-only contract, and a
        # template edit would leak the fix idea into every call.
        lines.append(
            "For each candidate you score below 0.3, also fill `fix`: the "
            "minimal edit that would make the move plausible (usually the "
            "destination the candidate's own reason argues for). If NO small "
            "edit can repair it — the move makes no sense for this occupant/"
            "activity at all — write exactly the word 'hopeless' instead, so "
            "it is not retried. Leave `fix` empty for acceptable candidates.")
    for i, c in enumerate(candidates):
        lines.append(candidate_line(i, c))
    user = "\n".join(lines)

    def _validate(result: dict) -> dict:
        return _normalize_judge_scores(result, len(candidates))

    system_prompt = template.text
    # judge_client lets the caller substitute an out-of-process model (e.g. the
    # HTTP MoE endpoint) for the thinking path; falls back to the in-process
    # vLLM client for the normal case.
    client = judge_client if judge_client is not None else _get_client(model)
    judge_meta: dict = {"stage_tag": stage_tag, "seed": seed, "think": ""}
    try:
        if judge_thinking:
            from .llm_client import generate_json_thinking
            by_index, think = generate_json_thinking(
                client, system_prompt, user,
                seed=seed, stage=stage_tag, cache=cache, force=force, validate=_validate,
                return_think=True,
            )
            judge_meta["think"] = think
        else:
            by_index = generate_json(
                client, system_prompt, user,
                build_realism_schema(len(candidates), with_fix=request_fix),
                seed=seed, stage=stage_tag, cache=cache, force=force, validate=_validate,
                temperature=temperature,
            )
    except PartialJudgeScores as e:
        # Retries exhausted with the judge still covering only a subset.
        # Explicit fallback, logged loudly: 0.0 under "strict" (an unscored
        # candidate in an over-generated pool must not be selectable by
        # default), the schema midpoint 0.5 otherwise.
        default = 0.0 if judge_style == "strict" else 0.5
        _logger.error(
            "[%s] judge coverage incomplete after retries (seed=%d): %s — "
            "defaulting %d missing score(s) to %.1f",
            stage_tag, seed, e, len(e.missing), default,
        )
        by_index = dict(e.scores)
        for i in e.missing:
            by_index[i] = {"score": default, "reason": ""}
        judge_meta["score_fallback"] = list(e.missing)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        # The judge produced NO usable output at all after every retry —
        # a truncated/malformed response (max_tokens hit mid-JSON) or an
        # unrecognized shape. Operationally identical to zero coverage:
        # default EVERY candidate, logged loudly, rather than letting one
        # bad activity-batch crash the whole scene's generation (which
        # discards the persona, traces, and every other activity's work).
        default = 0.0 if judge_style == "strict" else 0.5
        _logger.error(
            "[%s] judge output unusable after retries (seed=%d): %s — "
            "defaulting all %d score(s) to %.1f",
            stage_tag, seed, e, len(candidates), default,
        )
        by_index = {i: {"score": default, "reason": ""} for i in range(len(candidates))}
        judge_meta["score_fallback"] = list(range(len(candidates)))
        judge_meta["fallback_reason"] = str(e)[:200]
    # Coverage is enforced above, so this lookup cannot silently invent a
    # score — every index is present, from the judge or the logged fallback.
    judge_meta["reasons"] = [by_index[i].get("reason", "") for i in range(len(candidates))]
    judge_meta["fixes"] = [by_index[i].get("fix", "") for i in range(len(candidates))]
    return [by_index[i]["score"] for i in range(len(candidates))], judge_meta


# ---------------------------------------------------------------------------
# Multi-agent conflict detection (Stage 2 cross-verification)
# ---------------------------------------------------------------------------

def detect_occupant_conflicts(
    traces: list[dict],
    inventory: dict[str, int],
    household_id: str,
    day: int,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    cache: Optional[ResponseCache] = None,
    force: bool = False,
) -> dict:
    """Cross-verify activity traces across occupants for scheduling conflicts.

    Only called for multi-occupant households (len(traces) > 1).

    Returns a dict with a 'conflicts' list. Each conflict has:
      occupant, start, end, description.

    The caller (pipeline.py) regenerates conflicting spans.

    The seed folds in a content hash of the traces being checked, so each
    distinct set of traces (the original, then each conflict-resolution
    round's spliced result) gets its own deterministic, cacheable seed.
    Without this the seed was fixed per (household, day) and every round
    collided on one cache entry — which is why the caller previously had
    to pass force=True (bypassing the cache non-reproducibly) to see
    updated results across rounds.
    """
    # Summarise all traces compactly for the model
    trace_text = "\n\n".join(
        f"Occupant: {t['occupant_name']}\n" +
        "\n".join(
            f"  {a['start']:.1f}–{a['end']:.1f}h  {a['activity']} @ {a['location']}"
            for a in t.get("activities", [])
        )
        for t in traces
    )
    trace_key = hashlib.sha256(trace_text.encode()).hexdigest()[:8]
    _stage_tag = _CONFLICT_T.tag(f"conflict_verify_{trace_key}", builder=True)
    seed = make_seed(household_id, day, _stage_tag, 0)
    # Scarce-resource context from inventory
    scarce = [cat for cat, n in inventory.items() if n == 1]
    user = (
        f"Household has {len(traces)} occupants.\n"
        f"Scarce objects (only 1 in scene): {', '.join(scarce) if scarce else 'none known'}\n\n"
        f"Activity traces:\n{trace_text}\n\n"
        f"Identify any scheduling conflicts."
    )

    client = _get_client(model)
    return generate_json(
        client, _MULTI_OCCUPANT_VERIFY_SYSTEM, user, _CONFLICT_SCHEMA,
        seed=seed, stage=_stage_tag, cache=cache, force=force,
        temperature=temperature,
    )
