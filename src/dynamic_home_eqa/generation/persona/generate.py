"""Stage 1 — Persona generation."""
from __future__ import annotations

from typing import Optional

from ..cache import ResponseCache, make_seed
from ..llm_client import DEFAULT_MODEL, DEFAULT_TEMPERATURE, _get_client, generate_json
from ..prompt_registry import PERSONA as _PERSONA_T
from .prompts import PERSONA_SYSTEM_PROMPT
from .schema import PERSONA_SCHEMA


def generate_persona(
    household_type: str,
    household_id: str,
    demographic_notes: str = "",
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    cache: Optional[ResponseCache] = None,
    force: bool = False,
) -> dict:
    """Generate a persona for the given household type.

    Returns the parsed persona dict. Retries up to MAX_RETRIES times on
    JSON parse failure (guided decoding makes this unlikely; each failure is
    logged, and each retry samples with a distinct explicit seed — see
    llm_client.generate_json).

    Deliberately day-invariant: there is no `day` parameter. A household's
    persona (who lives there, tidiness, typical schedule) doesn't change
    Tuesday to Wednesday — only the day-to-day activity trace does. day used
    to be a parameter here purely because it fed the seed; a caller passing
    a different day for the same household would silently get a different
    persona for no conceptual reason. The seed is now pinned to day=0
    internally (make_seed still takes a day slot structurally; persona just
    never varies it) so the interface can't produce that incoherent case.

    Args:
        household_type:    e.g. "work_from_home_adult", "family_with_kids".
        household_id:      Unique ID for seed derivation (e.g. scene_id + profile).
        demographic_notes: Optional free-text constraints (e.g. "two adults, one toddler").
        model:             vLLM model string.
        temperature:       Sampling temperature.
        cache:             ResponseCache instance (None = no caching).
        force:             Ignore cached response and regenerate.
    """
    _stage = _PERSONA_T.tag("persona", builder=True)
    seed = make_seed(household_id, 0, _stage, 0)

    user_parts = [f"Household type: {household_type}"]
    if demographic_notes:
        user_parts.append(f"Additional constraints: {demographic_notes}")
    user = "\n".join(user_parts)

    def _backfill(result: dict) -> dict:
        # Ensure every occupant carries owned_items + bedroom_index, from the
        # LLM when valid, else the deterministic fallback — so downstream
        # (ContextBuilder, manifest, per-owner reports) never has to special-
        # case a missing field, and old cached personas get repaired on read.
        from ..ownership import assign_bedrooms, assign_ownership
        owned = assign_ownership(result)
        bedrooms = assign_bedrooms(result)
        for occ in result.get("occupants", []):
            occ["owned_items"] = owned.get(occ.get("name", ""), [])
            occ["bedroom_index"] = bedrooms.get(occ.get("name", ""), 1)
        return result

    client = _get_client(model)
    return generate_json(
        client, PERSONA_SYSTEM_PROMPT, user, PERSONA_SCHEMA,
        seed=seed, stage=_stage, cache=cache, force=force,
        temperature=temperature, validate=_backfill,
    )
