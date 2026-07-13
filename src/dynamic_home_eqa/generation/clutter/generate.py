"""Tier 2b clutter placement — invents a starting slot for small objects
HSSD's uncluttered scene variant doesn't place (book, candle, vase, bowl,
cup, drinkware, bottle), so they enter the scene the same way Tier 1/2a
furniture does: a real slot from t=0, not an insert_new event mid-timeline.

Runs once per (scene, household) — before persona's occupants get activity
traces, and before any displacement is proposed — since a clutter object's
home is a property of the house and who lives there, not of any single
day's activities.
"""
from __future__ import annotations

from typing import Optional

from ..cache import ResponseCache, make_seed
from ..llm_client import DEFAULT_MODEL, DEFAULT_TEMPERATURE, _get_client, generate_json
from ..schemas import build_clutter_schema, filter_displacement_proposals
from ..prompt_registry import CLUTTER as _CLUTTER_T
from .prompts import CLUTTER_SYSTEM_PROMPT


def generate_clutter(
    household_type: str,
    household_id: str,
    anchor_inventory: dict[str, int],
    room_inventory: Optional[dict[str, dict[str, int]]],
    anchor_census: Optional[dict] = None,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    cache: Optional[ResponseCache] = None,
    force: bool = False,
) -> list[dict]:
    """Propose Tier 2b clutter placements for this household's house.

    Returns a list of {object_category, target_relationship, target_anchor,
    reason} dicts — the same shape as a displacement proposal, minus the
    activity/occupant/time fields clutter doesn't have (it's placed once,
    not tied to a specific occupant's specific activity).

    Args:
        household_type:   e.g. "family_with_kids" — informs what clutter
                          fits this household (toys vs. reading glasses).
        household_id:     Unique household ID (for seed derivation).
        anchor_inventory: {furniture_category: count} real Tier 1 census for
                          this scene (env.inventory.anchor_inventory) —
                          prompt context, and the legacy anchor vocabulary
                          used only when no anchor census exists.
        room_inventory:   {room: {category: count}} real per-scene rooms —
                          prompt context (the in_region-era room vocabulary;
                          in_region is no longer emittable, see
                          schemas.REGION_ONLY_RELATIONSHIPS).
        anchor_census:    the realizable-anchor census (env/anchor_census.py,
                          Part A). When present, target_anchor enums are
                          SCENE-WIDE room-qualified census instance labels —
                          clutter has no occupant room to scope by; spreading
                          objects across the whole house is its job — split
                          surface-vs-proximity by receptacle backing, plus
                          the "none" abstain entry.
    """
    from ..inventory import format_inventory_for_prompt
    from ...env.anchor_census import census_anchor_vocabulary
    from ...env.inventory import TIER2_CLUTTER_CATALOG

    # variant/day-independent: clutter's starting position is a property of
    # the house + household, not of any one day, so this seed is pinned the
    # same way persona's is (see persona/generate.py's docstring).
    _stage = _CLUTTER_T.tag("clutter", builder=True)
    seed = make_seed(household_id, 0, _stage, 0)

    inv_text = format_inventory_for_prompt(anchor_inventory, room_inventory)
    user = (
        f"Household type: {household_type}\n"
        f"\n{inv_text}\n"
        f"\nPropose the static clutter objects for this home and where each lives."
    )

    valid_categories = sorted(TIER2_CLUTTER_CATALOG.keys())
    if anchor_census is not None:
        surface_anchors, proximity_anchors = census_anchor_vocabulary(anchor_census, location=None)
        schema = build_clutter_schema(valid_categories, surface_anchors, proximity_anchors)
    else:
        valid_furniture_anchors = sorted(anchor_inventory.keys()) or ["furniture"]
        schema = build_clutter_schema(valid_categories, valid_furniture_anchors, valid_furniture_anchors)

    client = _get_client(model)
    result = generate_json(
        client, CLUTTER_SYSTEM_PROMPT, user, schema,
        seed=seed, stage=_stage, cache=cache, force=force,
        validate=filter_displacement_proposals,
        temperature=temperature,
    )
    return result.get("proposals", [])
