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
                        "description": "'away' = outside the house entirely (school, work commute, errands).",
                    },
                    "start": {"type": "number", "description": "Start hour (24h float)."},
                    "end":   {"type": "number", "description": "End hour (24h float)."},
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

# Explicit abstain entry, always present in every anchor enum — the model
# is never forced to pick an inappropriate surface just because the enum
# is small (a room with no valid surfaces offers ONLY this). Abstained
# proposals are dropped before grounding, with a counter
# (generation/pipeline.py) — never grounded, never built.
ABSTAIN_ANCHOR = "none"


def _build_placement_item_schema(
    valid_categories: list[str],
    surface_anchors: list[str],
    proximity_anchors: list[str],
    include_assumed_from: bool = False,
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

    include_assumed_from adds a required `assumed_from` field: the model's
    own belief about where this object currently is, before this move. It is
    never used to write from_semantic (that always comes from the pipeline's
    tracked scene state — see generation/manifest.py) — it is a diagnostic
    only. Displacement proposals set this True; clutter placements (no
    "before" state) leave it False.
    """
    def _branch(relationships: list[str], anchors: list[str]) -> dict:
        properties = {
            "object_category": {
                "type": "string",
                "enum": valid_categories,
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
            "reason": {
                "type": "string",
                "description": "One-sentence behavioural justification.",
            },
        }
        required = ["object_category", "target_relationship", "target_anchor", "reason"]
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

    return {"oneOf": [
        _branch(surface_relationships, sorted(set(surface_anchors)) + [ABSTAIN_ANCHOR]),
        _branch(proximity_relationships, sorted(set(proximity_anchors)) + [ABSTAIN_ANCHOR]),
    ]}


def build_displacement_schema(
    valid_categories: list[str],
    surface_anchors: list[str],
    proximity_anchors: list[str],
) -> dict:
    """Displacement proposal schema: an {activity, occupant, proposals} object,
    each proposal a placement item (see _build_placement_item_schema).
    `surface_anchors`/`proximity_anchors` are room-scoped census instance
    labels (see generation/stages.py's generate_displacements for how they're
    scoped to the occupant's current room)."""
    item_schema = _build_placement_item_schema(
        valid_categories, surface_anchors, proximity_anchors,
        include_assumed_from=True,
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


def build_realism_schema(n_candidates: int) -> dict:
    """Guided realism-judge schema for a batch of exactly n_candidates.

    Pins the scores array to exactly n_candidates entries
    (minItems == maxItems == n): the grammar physically cannot emit the
    empty {"scores": []} the model otherwise takes ~half the time, nor a
    partial array — full coverage is enforced at decode time, not patched
    up after. No per-score `reason` field: it is unused downstream (only
    the score is consumed) and its free text is what pushed large batches
    past the token cap and truncated the JSON. Judge rationale, when
    wanted, comes from the thinking-mode trace, not this field.
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
                        "score":           {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    },
                    "required": ["candidate_index", "score"],
                },
            },
        },
        "required": ["scores"],
    }
