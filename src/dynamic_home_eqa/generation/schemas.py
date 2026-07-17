"""
JSON schemas for the three LLM generation stages.

All schemas are used with guided decoding (vLLM StructuredOutputsParams or
equivalent). Free-text parsing is not permitted; invalid output is discarded
and the call is retried.

Schema design principles:
  - Keep each schema as small as possible for the task.
  - No geometry in any schema. Spatial anchors are semantic object categories,
    not coordinates. PARTNR resolves geometry.
  - Relationship strings must come from PARTNR_RELATIONSHIPS; the displacement
    stage validates against this set before emitting.
  - Tidiness is a float [0, 1] consumed by the delta pipeline to scale
    cleanup probabilities. It is generated here and passed through; this
    module does not use it.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# PARTNR spatial-relationship vocabulary
# ---------------------------------------------------------------------------

# Valid relationship strings that PARTNR's spatial-relationship evaluator
# understands. Displacement proposals that use a string not in this set are
# dropped during displacement generation, before grounding.
#
# These are populated from the actual PARTNR codebase in grounding.py.
# The list here is a conservative subset known to be safe; grounding.py
# extends it at import time by reading PARTNR's own registry.
PARTNR_RELATIONSHIPS: set[str] = {
    "on",
    "within",
    "next_to",
    "in_region",
    "on_top",
    "inside",
    "near",
    # Tuck (see TUCK_RELATIONSHIP below): PARTNR-side it grounds exactly like
    # next_to (grounding._RELATION_MAP); the tucked distinction lives in the
    # resolved slot string, not in PARTNR geometry.
    "tucked_under",
}

# Stage 1 (persona) schema/prompts/profiles live in generation/persona/ —
# see that package's __init__.py for AGE_BANDS, PERSONA_SCHEMA, HOUSEHOLD_PROFILES.

# ---------------------------------------------------------------------------
# Stage 2 — Activity trace (per occupant)
# ---------------------------------------------------------------------------

# Fixed, enum-constrained location vocabulary for the activity trace stage.
# Deliberately generic (not tied to a specific scene's real rooms — unlike
# target_anchor in the displacement stage, this is a behavioral-modeling
# concept, not something grounding validates) but closed: an open string
# field here let the model both silently typo real values ("kining_room")
# and simply never reach for "away", since nothing forced the choice.
#
# Built from rooms.CANONICAL_ROOMS (plus "away") rather than hand-duplicated,
# so this enum and the shared room vocabulary (rooms.py, used by the
# displacement stage's room-scoped anchor filtering and by trace_validate.py's
# attendance check) can never drift apart.
from ..rooms import CANONICAL_ROOMS as _CANONICAL_ROOMS

ACTIVITY_LOCATIONS: list[str] = [*_CANONICAL_ROOMS, "away"]

ACTIVITY_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "occupant_name": {"type": "string"},
        "activities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "activity": {
                        "type": "string",
                        "description": (
                            "Short activity label, e.g. 'breakfast', 'work_at_desk', "
                            "'lunch', 'grocery_run', 'dinner', 'tv_time', 'sleep'."
                        ),
                    },
                    "location": {
                        "type": "string",
                        "enum": ACTIVITY_LOCATIONS,
                        "description": "'away' = outside the house entirely (school, work, errands).",
                    },
                    # bounds are grammar-enforced: the trace model
                    # occasionally emitted MINUTES here (e.g. 930.645), and
                    # every downstream time (displacement t, replay windows)
                    # inherits the unit error. 30 allows the legitimate
                    # past-midnight sleep wrap (typical_sleep > 24).
                    "start": {"type": "number", "minimum": 0, "maximum": 30,
                              "description": "Start hour (24h float)."},
                    "end":   {"type": "number", "minimum": 0, "maximum": 30,
                              "description": "End hour (24h float)."},
                },
                "required": ["activity", "location", "start", "end"],
            },
            "minItems": 1,
        },
    },
    "required": ["occupant_name", "activities"],
}

# ---------------------------------------------------------------------------
# Stage 3 — Displacement proposals (per activity)
# ---------------------------------------------------------------------------

# Relationships whose target_anchor is a room/region name rather than a
# furniture category. Kept as grounding.py's validation vocabulary for
# legacy manifests/cached responses, but NO LONGER EMITTABLE (Realizable-
# Anchor Vocabulary round, Part A): build_displacement_schema/
# build_clutter_schema stopped building an in_region branch entirely —
# recon confirmed in_region was the only path to the builder's
# floor-snap (compliance_place_region), so with no emitter the floor-bowl
# mechanism is unreachable. compliance_place_region itself stays intact
# for replaying old manifests.
REGION_ONLY_RELATIONSHIPS: set[str] = {"in_region"}

# Part A relation split: which PARTNR relations need a receptacle SURFACE
# (legal targets: census anchors with >=1 active receptacle) vs. only a
# POSITION (legal targets: every room-tagged census anchor — this is how
# fridge/tv/oven, structurally receptacle-less in HSSD, stay usable for
# next_to/near while becoming impossible to place things ON).
SURFACE_RELATIONSHIPS: set[str] = {"on", "on_top", "inside", "within"}
PROXIMITY_RELATIONSHIPS: set[str] = {"near", "next_to"}

# Tuck (floor-bound furniture only): a chair/stool pushed back under a
# table/counter/desk. Distinct from proximity — resolve_slot appends
# ".tucked" to the anchor so tucked and beside are different slots.
TUCK_RELATIONSHIP = "tucked_under"

# Explicit abstain entry, always present in every anchor enum — the model
# is never forced to pick an inappropriate surface just because the enum
# is small (a room with no valid surfaces offers ONLY this). Abstained
# proposals are dropped before grounding, with a counter
# (generation/pipeline.py) — never grounded, never built.
ABSTAIN_ANCHOR = "none"

# Phase 3 despawn: a symbolic target meaning "the occupant puts this carried
# item away (into a bag/pocket/drawer) and it disappears from the scene." Only
# offered for a window where the occupant has a Tier-3 item currently OUT (see
# generation/stages.py) and only despawns Tier-3 items (gated in the pipeline);
# we deliberately do NOT model where it goes, only that it leaves.
PUT_AWAY_ANCHOR = "put_away"


def _build_placement_item_schema(
    valid_categories: list[str],
    surface_anchors: list[str],
    proximity_anchors: list[str],
    include_assumed_from: bool = False,
    include_put_away: bool = False,
    tuck_anchors: Optional[list[str]] = None,
    conceal_anchors: Optional[list[str]] = None,
) -> dict:
    """Build the {object_category, target_relationship, target_anchor, reason}
    item schema shared by displacement proposals and clutter placements, with
    object_category/target_anchor constrained to this scene's real vocabulary
    via JSON-schema `enum`.

    Realizable-Anchor Vocabulary round (Part A): target_anchor entries are
    room-qualified census INSTANCE labels (env/anchor_census.py —
    "kitchen.counter_2", "bedroom_1.bed_1"), not bare furniture categories,
    and the relation-conditional oneOf split is now surface-vs-proximity
    (SURFACE_RELATIONSHIPS with `surface_anchors`, PROXIMITY_RELATIONSHIPS
    with `proximity_anchors`), not furniture-vs-region — the in_region
    branch is gone entirely (see REGION_ONLY_RELATIONSHIPS's comment). Both
    anchor enums always additionally contain ABSTAIN_ANCHOR, so an empty or
    tiny anchor list is legal and correct (the model abstains), never an
    error to be papered over with scene-wide fallbacks.

    A free-text `object_category` string lets the model propose a plausible
    synonym for a real category ("mug" when the inventory says "drinkware"),
    which then fails grounding as a hallucinated no_object rejection even
    though the underlying intent was valid. Constraining generation itself
    to the real vocabulary (guided decoding) is stronger than filtering
    after the fact — the model physically cannot emit an unknown category.
    The oneOf-with-enum-relationship-per-branch pattern was verified against
    this project's actual vLLM/xgrammar guided-decoding setup in the prior
    round (a flat union enum let the model emit incoherent pairs like "on" a
    room — confirmed on real generation output).

    include_assumed_from adds a required `assumed_from` field: the model's own
    belief about where this object currently is, before this move. Retired for
    displacements (Phase 3 made from_semantic authoritative and the guess was
    measured as 55-79% wrong noise that also anchored the reason to a false
    origin — see results/reports/data_quality_backlog.md #1); left as an opt-in
    param, off everywhere today.

    The leading field is always `reason` — genuine pre-proposal reasoning.
    Guided decoding emits fields in schema order, so the model reasons over
    its inputs (activity, persona, location, current object state, available
    objects/anchors) BEFORE committing to an object change; the reason is
    then carried into the manifest verbatim as the event's trace. (The
    earlier purpose/templated-reason split is retired: it produced two
    half-fields, neither a good trace.)
    """
    cot_field = "reason"
    cot_desc = (
        "Reason FIRST: think through what this activity, done by this person "
        "in this room, plausibly implies for object movement — consult the "
        "current object state for where things are now, name which object "
        "would move, why, and where it would end up. Then fill the fields "
        "below to match that reasoning; they must follow from it, not the "
        "other way around. At most two sentences."
    )

    def _branch(relationships: list[str], anchors: list[str],
                categories: Optional[list[str]] = None) -> dict:
        # The CoT field is deliberately FIRST: guided decoding emits fields in
        # schema order, so the model reasons about what the activity implies
        # BEFORE it commits object_category/target_relationship/target_anchor —
        # genuine chain-of-thought, not a post-hoc justification of an
        # already-picked placement. Order matters here; do not move it down.
        properties = {
            cot_field: {
                "type": "string",
                # Hard cap (grammar-enforced, not just prompted): ~2 full
                # sentences of headroom. Stops the occasional paragraph
                # without truncating a normal 2-sentence reason mid-word
                # (320 clipped ~15% of reasons, manufacturing incoherence).
                "maxLength": 400,
                "description": cot_desc,
            },
            "object_category": {
                "type": "string",
                "enum": categories or valid_categories,
                "description": "Object category present in the scene inventory.",
            },
            "target_relationship": {
                "type": "string",
                "enum": relationships,
            },
            "target_anchor": {
                "type": "string",
                "enum": anchors,
                "description": (
                    "A specific real furniture instance (room.category_N), "
                    f"or {ABSTAIN_ANCHOR!r} to abstain if nothing fits."
                ),
            },
        }
        required = [cot_field, "object_category", "target_relationship", "target_anchor"]
        if include_assumed_from:
            properties["assumed_from"] = {
                "type": "string",
                "description": (
                    "Where this object currently is, before this "
                    "move (your best analysis, e.g. 'kitchen counter'). This is a "
                    "diagnostic only — the pipeline tracks real state itself."
                ),
            }
            required.append("assumed_from")
        return {"type": "object", "properties": properties, "required": required}

    surface_relationships = sorted(SURFACE_RELATIONSHIPS & PARTNR_RELATIONSHIPS)
    proximity_relationships = sorted(PROXIMITY_RELATIONSHIPS & PARTNR_RELATIONSHIPS)
    if not valid_categories or not surface_relationships or not proximity_relationships:
        raise ValueError("_build_placement_item_schema: empty category or relationship vocabulary")

    extra = [ABSTAIN_ANCHOR] + ([PUT_AWAY_ANCHOR] if include_put_away else [])
    # Floor-bound entries — bare seat categories AND seat instance tokens
    # ("stool_2", from generate_displacements' seat_instances vocabulary) —
    # are excluded from the SURFACE branch at the grammar level (a chair is
    # never lifted onto a table) and are the only entries the tuck branch
    # admits. instance_token_category maps both forms to the category.
    from ..env.inventory import FLOOR_BOUND_CATEGORIES
    from .instances import instance_token_category
    floor_bound = sorted(c for c in valid_categories
                         if instance_token_category(c) in FLOOR_BOUND_CATEGORIES)
    non_floor = [c for c in valid_categories if c not in floor_bound]
    branches = [
        _branch(surface_relationships, sorted(set(surface_anchors)) + extra,
                categories=non_floor or valid_categories),
        _branch(proximity_relationships, sorted(set(proximity_anchors)) + extra),
    ]
    # Tuck branch (displacements only): floor-bound categories (chair/stool)
    # can be tucked back under table/counter/desk instances — the inverse of
    # pulling one out (next_to). Own branch so BOTH the category and anchor
    # vocabularies are constrained (a book cannot be tucked; a chair cannot
    # tuck under a bed). resolve_slot maps tucked_under to the distinct
    # "<anchor>.tucked" slot, so a tuck after an untuck at the same furniture
    # is a real state change, not a suppressed no-op.
    if tuck_anchors and floor_bound:
        branches.append(_branch([TUCK_RELATIONSHIP],
                                sorted(set(tuck_anchors)) + [ABSTAIN_ANCHOR],
                                categories=floor_bound))
    # Concealment branch (displacements only): 'inside' a CONCEALING storage
    # anchor (cabinet/wardrobe/fridge/...) is a put-away — the pipeline
    # converts it to a remove event, never a visible placement, so these
    # anchors are legal 'inside' targets even with zero authored interior
    # receptacles. Small items only (non-floor-bound).
    if conceal_anchors:
        branches.append(_branch(["inside"],
                                sorted(set(conceal_anchors)) + [ABSTAIN_ANCHOR],
                                categories=non_floor or valid_categories))
    return {"oneOf": branches}


def build_displacement_schema(
    valid_categories: list[str],
    surface_anchors: list[str],
    proximity_anchors: list[str],
    include_put_away: bool = False,
    tuck_anchors: Optional[list[str]] = None,
    conceal_anchors: Optional[list[str]] = None,
) -> dict:
    """Displacement proposal schema: an {activity, occupant, proposals} object,
    each proposal a placement item (see _build_placement_item_schema).
    `surface_anchors`/`proximity_anchors` are room-scoped census instance
    labels (see generation/stages.py's generate_displacements for how they're
    scoped to the occupant's current room).

    Each proposal leads with `reason` (pre-proposal reasoning over the
    activity/persona/location/current-state inputs; carried into the manifest
    verbatim) and has no `assumed_from` — Phase 3 tracks origin
    authoritatively, so the model's origin guess is never solicited."""
    item_schema = _build_placement_item_schema(
        valid_categories, surface_anchors, proximity_anchors,
        include_assumed_from=False, include_put_away=include_put_away,
        tuck_anchors=tuck_anchors, conceal_anchors=conceal_anchors,
    )
    return {
        "type": "object",
        "properties": {
            "activity":  {"type": "string"},
            "occupant":  {"type": "string"},
            "proposals": {"type": "array", "items": item_schema},
        },
        "required": ["activity", "occupant", "proposals"],
    }


def build_clutter_schema(
    valid_categories: list[str],
    surface_anchors: list[str],
    proximity_anchors: list[str],
) -> dict:
    """Tier 2b clutter-placement schema: just {proposals} — no activity or
    occupant, since clutter's starting position is a property of the scene +
    household, generated once before any activity fires, not tied to a
    specific occupant's specific activity the way a displacement is. Clutter
    has no occupant room to scope by, so its anchor lists are scene-wide
    census labels (see generation/clutter/generate.py)."""
    item_schema = _build_placement_item_schema(
        valid_categories, surface_anchors, proximity_anchors
    )
    return {
        "type": "object",
        "properties": {
            "proposals": {"type": "array", "items": item_schema},
        },
        "required": ["proposals"],
    }


def filter_displacement_proposals(raw: dict) -> dict:
    """Drop proposals whose target_relationship is not in PARTNR_RELATIONSHIPS.

    This is the first validation gate, applied before grounding.
    """
    valid = [
        p for p in raw.get("proposals", [])
        if p.get("target_relationship") in PARTNR_RELATIONSHIPS
    ]
    return {**raw, "proposals": valid}


# ---------------------------------------------------------------------------
# Stage 3.5 — Realism judge (per grounded candidate, batched per activity)
# ---------------------------------------------------------------------------

# One array entry per candidate, keyed by explicit candidate_index rather than
# relying on output order — guided decoding shouldn't be trusted to preserve
# array order 1:1 with the input list across every model.
#
# Static form kept for the thinking-mode judge (no guided schema there) and
# any legacy caller. The GUIDED judge must use build_realism_schema(n) below,
# which pins the array length so the grammar cannot emit an empty/partial
# array — see that function's docstring.
REALISM_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "scores": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "candidate_index": {"type": "integer"},
                    "score":           {"type": "number", "minimum": 0.0, "maximum": 1.0},
                },
                "required": ["candidate_index", "score"],
            },
        },
    },
    "required": ["scores"],
}


def build_realism_schema(n_candidates: int, with_fix: bool = False) -> dict:
    """Guided realism-judge schema for a batch of exactly n_candidates.

    Pins the scores array to exactly n_candidates entries
    (minItems == maxItems == n): the grammar physically cannot emit the
    empty {"scores": []} the model otherwise takes ~half the time, nor a
    partial array — full coverage is enforced at decode time, not patched
    up after.

    Per-score `reason` comes FIRST (schema order = decode order, the same
    reason-before-commitment pattern as the proposer's CoT field): the judge
    weighs the evidence in text, then emits a score consistent with that
    reasoning — and the reason is persisted to choices.jsonl for debugging
    judge behavior. An earlier revision deliberately dropped this field
    because free-text reasons pushed large batches past the 2048 token cap;
    that cap is now 4096 (llm_client) and the prompt bounds reasons to two
    sentences, which is what made it affordable to restore.
    """
    n = max(1, n_candidates)
    return {
        "type": "object",
        "properties": {
            "scores": {
                "type": "array",
                "minItems": n,
                "maxItems": n,
                "items": {
                    "type": "object",
                    "properties": {
                        "candidate_index": {"type": "integer", "minimum": 0, "maximum": n - 1},
                        "reason": {
                            "type": "string",
                            "maxLength": 400,
                            "description": "Weigh the evidence for/against this exact "
                                           "placement BEFORE scoring. At most two sentences.",
                        },
                        "score":           {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        # judge-retry round 1 only (with_fix): a repair hint
                        # decoded AFTER the score so it cannot bias it. The
                        # round-2 (kill-only) judge uses the plain schema.
                        **({"fix": {
                            "type": "string", "maxLength": 240,
                            "description": "For scores below ~0.3: the minimal edit "
                                           "(destination, object, or relation) that "
                                           "would make the move plausible — or exactly "
                                           "the word 'hopeless' if no small edit can "
                                           "repair it. Empty string for acceptable "
                                           "candidates.",
                        }} if with_fix else {}),
                    },
                    "required": ["candidate_index", "reason", "score"]
                                + (["fix"] if with_fix else []),
                },
            },
        },
        "required": ["scores"],
    }
