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
# furniture category. Single source of truth for the oneOf split in
# build_displacement_schema and the equivalent split in grounding.py.
REGION_ONLY_RELATIONSHIPS: set[str] = {"in_region"}


def _build_placement_item_schema(
    valid_categories: list[str],
    valid_furniture_anchors: list[str],
    valid_room_anchors: list[str],
    include_assumed_from: bool = False,
) -> dict:
    """Build the {object_category, target_relationship, target_anchor, reason}
    item schema shared by displacement proposals and clutter placements, with
    object_category/target_anchor constrained to this scene's real vocabulary
    via JSON-schema `enum`.

    A free-text `object_category` string lets the model propose a plausible
    synonym for a real category ("mug" when the inventory says "drinkware"),
    which then fails grounding as a hallucinated no_object rejection even
    though the underlying intent was valid. Constraining generation itself
    to the real vocabulary (guided decoding) is stronger than filtering
    after the fact — the model physically cannot emit an unknown category.

    target_anchor is relation-conditional via oneOf: an in_region proposal
    must pick from valid_room_anchors, everything else from
    valid_furniture_anchors. A flat union enum was tried first and let the
    model emit incoherent pairs like {"target_relationship": "on",
    "target_anchor": "kitchen"} ("on" a room) — confirmed on real generation
    output, not just theoretically. oneOf with a `const` relationship per
    branch has been verified against this project's actual vLLM/xgrammar
    guided-decoding setup (see generation/schemas.py git history / build
    notes) rather than assumed to work.

    include_assumed_from adds a required `assumed_from` field: the model's
    own belief about where this object currently is, before this move. It is
    never used to write from_semantic (that always comes from the pipeline's
    tracked scene state — see generation/manifest.py) — it is a diagnostic
    only, logged and compared against tracked state to surface cases where
    the model's picture of the scene has drifted from the actual timeline.
    Displacement proposals set this True; clutter placements (which have no
    "before" state — they invent a first-ever position) leave it False.

    All three vocab lists must be non-empty — guided decoding requires a
    non-empty enum.
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
                "description": "Must be reachable in the scene.",
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
                    "Where you believe this object currently is, before this "
                    "move (your best guess, e.g. 'kitchen counter'). This is a "
                    "diagnostic only — the pipeline tracks real state itself."
                ),
            }
            required.append("assumed_from")
        return {"type": "object", "properties": properties, "required": required}

    furniture_relationships = sorted(PARTNR_RELATIONSHIPS - REGION_ONLY_RELATIONSHIPS)
    region_relationships     = sorted(PARTNR_RELATIONSHIPS & REGION_ONLY_RELATIONSHIPS)

    branches = []
    if furniture_relationships and valid_furniture_anchors:
        branches.append(_branch(furniture_relationships, valid_furniture_anchors))
    if region_relationships and valid_room_anchors:
        branches.append(_branch(region_relationships, valid_room_anchors))
    if not branches:
        raise ValueError("_build_placement_item_schema: no valid (relationship, anchor) branch available")

    return branches[0] if len(branches) == 1 else {"oneOf": branches}


def build_displacement_schema(
    valid_categories: list[str],
    valid_furniture_anchors: list[str],
    valid_room_anchors: list[str],
) -> dict:
    """Displacement proposal schema: an {activity, occupant, proposals} object,
    each proposal a placement item (see _build_placement_item_schema)."""
    item_schema = _build_placement_item_schema(
        valid_categories, valid_furniture_anchors, valid_room_anchors,
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
    valid_furniture_anchors: list[str],
    valid_room_anchors: list[str],
) -> dict:
    """Tier 2b clutter-placement schema: just {proposals} — no activity or
    occupant, since clutter's starting position is a property of the scene +
    household, generated once before any activity fires, not tied to a
    specific occupant's specific activity the way a displacement is."""
    item_schema = _build_placement_item_schema(
        valid_categories, valid_furniture_anchors, valid_room_anchors
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
                    "reason":          {"type": "string"},
                },
                "required": ["candidate_index", "score", "reason"],
            },
        },
    },
    "required": ["scores"],
}
