"""Stage 1 — Persona generation."""
from __future__ import annotations

from typing import Optional

from ..cache import ResponseCache, make_seed
from ..llm_client import DEFAULT_MODEL, DEFAULT_TEMPERATURE, _get_client, generate_json
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
    seed = make_seed(household_id, 0, "persona", 0)

    user_parts = [f"Household type: {household_type}"]
    if demographic_notes:
        user_parts.append(f"Additional constraints: {demographic_notes}")
    user = "\n".join(user_parts)

    client = _get_client(model, temperature)
    return generate_json(
        client, PERSONA_SYSTEM_PROMPT, user, PERSONA_SCHEMA,
        seed=seed, stage="persona", cache=cache, force=force,
    )
