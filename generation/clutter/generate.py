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
from .prompts import CLUTTER_SYSTEM_PROMPT


def generate_clutter(
    household_type: str,
    household_id: str,
    anchor_inventory: dict[str, int],
    room_inventory: Optional[dict[str, dict[str, int]]],
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
                          this scene (env.inventory.anchor_inventory) — also
                          the target_anchor vocabulary for on/within/next_to.
        room_inventory:   {room: {category: count}} real per-scene rooms —
                          the target_anchor vocabulary for in_region.
    """
    from ..inventory import format_inventory_for_prompt
    from ...env.inventory import TIER2_CLUTTER_CATALOG

    # variant/day-independent: clutter's starting position is a property of
    # the house + household, not of any one day, so this seed is pinned the
    # same way persona's is (see persona/generate.py's docstring).
    seed = make_seed(household_id, 0, "clutter", 0)

    inv_text = format_inventory_for_prompt(anchor_inventory, room_inventory)
    user = (
        f"Household type: {household_type}\n"
        f"\n{inv_text}\n"
        f"\nPropose the static clutter objects for this home and where each lives."
    )

    valid_categories = sorted(TIER2_CLUTTER_CATALOG.keys())
    valid_furniture_anchors = sorted(anchor_inventory.keys()) or ["furniture"]
    valid_room_anchors = sorted((room_inventory or {}).keys()) or ["room"]
    schema = build_clutter_schema(valid_categories, valid_furniture_anchors, valid_room_anchors)

    client = _get_client(model, temperature)
    result = generate_json(
        client, CLUTTER_SYSTEM_PROMPT, user, schema,
        seed=seed, stage="clutter", cache=cache, force=force,
        validate=filter_displacement_proposals,
    )
    return result.get("proposals", [])
