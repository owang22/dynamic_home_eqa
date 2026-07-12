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

import logging
from typing import Optional

from .cache import ResponseCache, make_seed
from .llm_client import DEFAULT_MODEL, DEFAULT_TEMPERATURE, _get_client, generate_json
from ..env.anchor_census import census_anchor_vocabulary
from .schemas import (
    ACTIVITY_SCHEMA,
    ACTIVITY_LOCATIONS,
    REALISM_SCHEMA,
    build_displacement_schema,
    filter_displacement_proposals,
)

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_ACTIVITY_SYSTEM = """\
You are a household activity scheduler. Given a persona and a day context,
produce a realistic day's activity trace for one occupant with continuous
(non-hour-snapped) times. Let the day context meaningfully shape the schedule —
different contexts should produce noticeably different traces. Use the
occupant's habits (given below) to make this specific day theirs, not a
generic template shared with other household members.

Activities must be contiguous and non-overlapping for the occupant, and
together must span the occupant's full day from typical_wake to typical_sleep
(wrapping past midnight if typical_sleep > 24).

Location must be exactly one of: {locations}.
'away' means genuinely outside the house. Whether it applies depends on the
occupant's age_band and the Day type given below:
  - "weekday": older_child and teen are away at school for a substantial
    block unless the day context itself overrides it (sick, holiday).
    young_child is often at school too (grade school); toddler may be home
    or at daycare — use judgement, it's not automatic either way. adult
    often still has a commute, errand, or offsite block even on a nominally
    "work from home" day. senior is often home (retired) unless habits say
    otherwise.
  - "weekend": no school for any age_band. Occupants may or may not leave,
    per their habits and the day context.
  - "flex": the day context text itself determines whether the occupant
    leaves — don't assume either way from the day of week.
A full day with every single activity indoors at home is the exception for a
school-age (older_child/teen) occupant on a weekday, not the default — if you
keep one home, the day context must justify it (illness, holiday), not just
default to it.

Repeated behavior should come from the day context, not habit alone: if the
day context implies frequent recurrence (e.g. "makes hot drinks frequently",
"mostly resting"), repeating that specific activity is correct. Otherwise,
don't reuse the same non-routine activity label more than twice — vary the
label even when the general behavior recurs (tidying, gardening,
arts_and_crafts, reorganizing are all different from "decorating" repeated
four times for no stated reason). Prefer plain, ordinary activity labels
(cooking, cleaning, breakfast) over dramatized ones (e.g.
"cooking_special_dish") unless the day context specifically motivates
something out of the ordinary.

Respond only with valid JSON matching the provided schema. No commentary.
""".format(locations=", ".join(ACTIVITY_LOCATIONS))

# ---------------------------------------------------------------------------
# Day-context scenarios — injected into the activity trace user message.
# One is selected deterministically per (household_id, day, occupant) seed
# so traces are reproducible but vary across days and occupants.
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


def _day_context(seed: int) -> tuple[str, str]:
    """Pick a (day-context text, day_type) pair deterministically from the pool."""
    return _DAY_SCENARIOS[seed % len(_DAY_SCENARIOS)]

_DISPLACEMENT_SYSTEM = """\
You are a household object-placement modeller. Given an activity and a scene
inventory, propose CANDIDATE objects the occupant might move and where to.
You are a proposer, not a filter — a separate downstream stage grounds,
scores, and selects the final subset, so proposing more candidates than
would realistically all happen at once is fine, and preferred, over a short
"safe" list.

Rules:
- Only propose object categories that appear in the inventory.
- target_anchor entries name SPECIFIC real furniture instances in the format
  room.category_N (e.g. kitchen.counter_2 = the second counter in the
  kitchen, bedroom_1.bed_1 = the bed in the first bedroom). These are the
  ONLY real placement targets in the occupant's current room — there are no
  other surfaces, and nothing outside this list exists for this activity.
- Surface relations (on, on_top, inside, within) may only target anchors
  offered on the surface list — each has a real, physically usable surface.
  Proximity relations (near, next_to) may target any listed anchor: placing
  an object NEXT TO a fridge or tv is fine even though nothing can be placed
  ON them.
- Chairs and stools are FLOOR objects: they get pushed in, pulled out, or
  moved next to furniture — never lifted onto a table/counter/bed. For
  chair/stool, only use proximity relations (near, next_to); a chair/stool
  surface proposal will be discarded.
- If no listed anchor is an appropriate destination for an object, choose
  "none" (abstain) for that proposal rather than forcing a bad fit. An
  abstained proposal is dropped, not penalised — a wrong surface is worse
  than no proposal.
- The occupant is physically in one room for this whole activity (given
  below, when known). Every target_anchor offered to you already belongs to
  that room — you cannot place an object somewhere the occupant isn't. The
  object being moved does not have to already be in that room (it can be
  something they're carrying in from elsewhere); only the destination is
  room-constrained.
- Vary target_anchor across candidates when multiple objects could plausibly
  move — do not default every object to the same nearest surface. A
  breakfast candidate pool can spread across the table and both counters,
  not the same table three times over.
- A candidate must still be physically sensible for the activity (a cup can
  move to the table during breakfast; a sofa does not move during
  breakfast). Behavioral realism — how *likely* the move is, not just
  whether it's conceivable — is judged downstream; do not self-censor a
  plausible-but-less-common move here.
- Give a brief behavioural reason for each proposal.
- assumed_from: state your own best guess of where the object currently is,
  before this move. This is a diagnostic only — the pipeline tracks the
  real authoritative state itself and does not take your word for it — but
  answer as accurately as you can regardless.

Respond only with valid JSON matching the provided schema. No commentary.
"""

_REALISM_SYSTEM = """\
You are a behavioral-plausibility judge for household object placements.
Grounding has already confirmed each candidate below is physically
placeable; your job is a separate judgment — how behaviorally plausible is
it, given the activity, occupant, and household.

For EACH candidate, independently assign a realism score in [0, 1]: how
plausible is it that this specific object would end up at this location
because of this activity, for this occupant, in this household.

Score every candidate strictly on its own merits. Do not compare candidates
to each other or rank them, and do not let pool size influence a score — the
same candidate in a context should score the same whether the pool has 2
entries or 10.

Household tidiness scales plausible clutter, it does not gate realism: a
low-tidiness household plausibly leaves more objects out of place, so a
borderline "left behind" placement should score higher there than in a tidy
household — but a placement with no behavioral connection to the activity
should still score low regardless of tidiness.

A placement can be physically valid but behaviorally implausible — e.g. a
laptop on the dining table during dinner is placeable but out of place for
that activity, and should score low even though grounding accepted it.

Respond only with valid JSON matching the provided schema. No commentary.
"""

# LLM Option Evaluation round, judge style B: same independence/tidiness
# framing as _REALISM_SYSTEM, but explicitly strict — built for the
# "over-generate varied proposals, select the good ones by design" flow,
# where the proposer is deliberately permissive and the judge is the
# quality gate. The score scale is anchored so most of a varied pool
# SHOULD land low.
_REALISM_SYSTEM_STRICT = """\
You are a strict behavioral-plausibility judge for household object
placements. Grounding has already confirmed each candidate below is
physically placeable; your job is to decide how believably a real person
doing this activity would produce this exact placement. The proposal pool
is deliberately over-generated and varied — most candidates are NOT
supposed to pass. Be selective.

For EACH candidate, independently assign a realism score in [0, 1]:
  - 0.8–1.0: the placement is exactly what a typical person doing this
    activity would do; you would not notice it in a photo of a real home.
  - 0.5–0.7: plausible but noticeably less common; needs the household
    context (tidiness, occupant) to make sense.
  - 0.2–0.4: conceivable but contrived — you'd need a story to explain it.
  - 0.0–0.1: no believable behavioral connection to the activity, or
    physically-technically-possible-but-absurd (electronics in the fridge,
    a candle on a bed, food items in the bathroom).

Actively penalize: placements with no behavioral connection to THIS
activity; odd object-surface pairings a person wouldn't choose (books in a
bathtub, a vase on a toilet); the same object repeatedly shuffled to
arbitrary surfaces; safety-implausible placements. When in doubt, score
LOWER — a missed good candidate costs little in an over-generated pool, a
bad selection pollutes the dataset.

Score every candidate strictly on its own merits. Do not compare candidates
to each other or rank them, and do not let pool size influence a score.

Household tidiness scales plausible clutter, it does not gate realism: a
low-tidiness household plausibly leaves more objects out of place — but a
placement with no behavioral connection to the activity should still score
low regardless of tidiness.

Respond only with valid JSON matching the provided schema. No commentary.
"""

_MULTI_OCCUPANT_VERIFY_SYSTEM = """\
You are reviewing activity traces for a multi-occupant household for
scheduling conflicts.

A conflict is:
  - Two occupants using the same scarce object simultaneously
    (e.g. both occupants eating at the single dining table at the same time is
     fine if there are 2+ seats; both using the single computer simultaneously
     is a conflict).
  - An occupant marked as 'away' also doing an indoor activity at the same time.
  - Any logically contradictory joint state.

For each conflict found, return the occupant name, the conflicting time range,
and a brief description. If no conflicts, return an empty list.

Respond only with valid JSON.
"""

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
) -> dict:
    """Generate a day's activity trace for one occupant.

    Returns the parsed activity trace dict.

    Args:
        persona:         Output from generate_persona().
        occupant_name:   Name of the occupant to generate a trace for.
        occupant_index:  Index within the persona's occupant list (for seed derivation).
        household_id:    Unique household ID (for seed derivation).
        day:             Day index (different days → different seeds → different traces).
    """
    seed = make_seed(household_id, day, "activity", occupant_index)

    # Pull the occupant's role, schedule, and tidiness from the persona.
    # tidiness is per-occupant (not a household-wide average), so it comes
    # from here, not from the persona dict's top level.
    occupant_info = next(
        (o for o in persona.get("occupants", []) if o["name"] == occupant_name),
        {"name": occupant_name, "role": "unknown", "age_band": "adult",
         "typical_wake": 7.0, "typical_sleep": 22.0, "habits": "", "tidiness": 0.5},
    )
    day_text, day_type = _day_context(seed)
    user = (
        f"Occupant: {occupant_name} ({occupant_info.get('role', 'unknown')}), "
        f"age_band={occupant_info.get('age_band', 'adult')}\n"
        f"Habits: {occupant_info.get('habits', 'none given')}\n"
        f"Household type: {persona.get('household_type', 'unknown')}\n"
        f"Tidiness level: {occupant_info.get('tidiness', 0.5):.1f}/1.0\n"
        f"Schedule notes: {persona.get('schedule_notes', 'none')}\n"
        f"Typical wake: {occupant_info.get('typical_wake', 7.0):.1f}h  "
        f"Typical sleep: {occupant_info.get('typical_sleep', 22.0):.1f}h\n"
        f"Day type: {day_type}\n"
        f"Day context: {day_text}\n"
        f"\nGenerate a full day's activity trace for {occupant_name}, reflecting their habits."
    )

    def _validate(result: dict) -> dict:
        result["activities"] = _repair_activity_trace(result.get("activities", []))
        return result

    client = _get_client(model, temperature)
    return generate_json(
        client, _ACTIVITY_SYSTEM, user, ACTIVITY_SCHEMA,
        seed=seed, stage="activity", cache=cache, force=force, validate=_validate,
    )


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
) -> dict:
    """Propose object displacements for one activity.

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
    seed = make_seed(household_id, day, f"displacement_{activity}_{start:.2f}", occupant_index)

    # tidiness is per-occupant, not a household average — look up this
    # occupant's own value rather than a persona-level field.
    occupant_info = next(
        (o for o in persona.get("occupants", []) if o["name"] == occupant_name),
        {"role": "", "tidiness": 0.5},
    )
    inv_text = format_inventory_for_prompt(inventory, room_inventory)
    location_line = f"Occupant's current room: {location}\n" if location else ""
    user = (
        f"Activity: {activity} ({start:.1f}h – {end:.1f}h)\n"
        f"Occupant: {occupant_name} ({occupant_info.get('role', '')})\n"
        f"{location_line}"
        f"Household tidiness: {occupant_info.get('tidiness', 0.5):.1f}/1.0\n"
        f"\n{inv_text}\n"
        f"\nPropose object displacements caused by this activity."
    )

    valid_categories = sorted(inventory.keys()) or ["object"]

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
        schema = build_displacement_schema(valid_categories, surface_anchors, proximity_anchors)
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
        schema = build_displacement_schema(valid_categories, valid_furniture_anchors, valid_furniture_anchors)

    client = _get_client(model, temperature)
    return generate_json(
        client, _DISPLACEMENT_SYSTEM, user, schema,
        seed=seed, stage="displacement", cache=cache, force=force,
        validate=filter_displacement_proposals,
    )


# ---------------------------------------------------------------------------
# Stage 3.5 — Realism judge (per grounded candidate, batched per activity)
# ---------------------------------------------------------------------------

def _normalize_judge_scores(result, n_candidates: int) -> dict:
    """Canonical {int index: float score} from any of the judge output
    shapes observed in the real thinking-mode comparison
    (results/reports/llm_comparison/thinking_vs_moe.md): the schema's
    {"scores": [{candidate_index, score, ...}]} array, a {"scores":
    {"0": 0.6}} dict, a flat {"0": 0.9} dict, or a bare list of
    floats/dicts. Raises ValueError on anything else (triggers the
    caller's retry)."""
    scores = result.get("scores", result) if isinstance(result, dict) else result
    out: dict = {}
    if isinstance(scores, list):
        for i, entry in enumerate(scores):
            if isinstance(entry, dict):
                out[int(entry.get("candidate_index", i))] = float(entry["score"])
            else:
                out[i] = float(entry)
    elif isinstance(scores, dict):
        for k, v in scores.items():
            idx = int(k)
            out[idx] = float(v["score"] if isinstance(v, dict) else v)
    else:
        raise ValueError(f"unrecognized judge output shape: {type(scores).__name__}")
    if not out:
        raise ValueError("judge output contained no scores")
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
) -> list[float]:
    """Score behavioral plausibility for a pool of grounded displacement candidates.

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

    Returns a list of scores in [0, 1] parallel to `candidates`.
    """
    if not candidates:
        return []

    stage_tag = "realism"
    if judge_thinking:
        stage_tag += "_think"
    if judge_style != "asis":
        stage_tag += f"_{judge_style}"
    seed = make_seed(household_id, day, f"{stage_tag}_{activity}_{start:.2f}", occupant_index)

    # tidiness is per-occupant, not a household average.
    occupant_tidiness = next(
        (o.get("tidiness", 0.5) for o in persona.get("occupants", []) if o["name"] == occupant_name),
        0.5,
    )
    lines = [
        f"Activity: {activity}",
        f"Occupant: {occupant_name}",
        f"Household tidiness: {occupant_tidiness:.1f}/1.0",
        "",
        "Candidates (score each independently):",
    ]
    for i, c in enumerate(candidates):
        lines.append(
            f"  [{i}] {c.get('object_category','')} {c.get('target_relationship','')} "
            f"{c.get('target_anchor','')} — proposed reason: {c.get('reason', '')}"
        )
    user = "\n".join(lines)

    def _validate(result: dict) -> dict:
        return _normalize_judge_scores(result, len(candidates))

    system_prompt = _REALISM_SYSTEM_STRICT if judge_style == "strict" else _REALISM_SYSTEM
    client = _get_client(model, temperature)
    if judge_thinking:
        from .llm_client import generate_json_thinking
        by_index = generate_json_thinking(
            client, system_prompt, user,
            seed=seed, stage=stage_tag, cache=cache, force=force, validate=_validate,
        )
    else:
        by_index = generate_json(
            client, system_prompt, user, REALISM_SCHEMA,
            seed=seed, stage=stage_tag, cache=cache, force=force, validate=_validate,
        )
    return [by_index.get(i, 0.5) for i in range(len(candidates))]


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
    """
    seed = make_seed(household_id, day, "conflict_verify", 0)

    # Summarise all traces compactly for the model
    trace_text = "\n\n".join(
        f"Occupant: {t['occupant_name']}\n" +
        "\n".join(
            f"  {a['start']:.1f}–{a['end']:.1f}h  {a['activity']} @ {a['location']}"
            for a in t.get("activities", [])
        )
        for t in traces
    )
    # Scarce-resource context from inventory
    scarce = [cat for cat, n in inventory.items() if n == 1]
    user = (
        f"Household has {len(traces)} occupants.\n"
        f"Scarce objects (only 1 in scene): {', '.join(scarce) if scarce else 'none known'}\n\n"
        f"Activity traces:\n{trace_text}\n\n"
        f"Identify any scheduling conflicts."
    )

    client = _get_client(model, temperature)
    return generate_json(
        client, _MULTI_OCCUPANT_VERIFY_SYSTEM, user, _CONFLICT_SCHEMA,
        seed=seed, stage="conflict_verify", cache=cache, force=force,
    )
