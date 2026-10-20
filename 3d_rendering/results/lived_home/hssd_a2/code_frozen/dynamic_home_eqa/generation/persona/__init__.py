"""
persona/ — everything for Stage 1 (persona generation): the guided-decoding
schema, the household-type vocabulary, the system prompt, and the generator.

Kept separate from generation/stages.py (which owns the activity-trace,
displacement, and realism-judge stages) so persona-specific iteration —
tweaking age bands, adding household profiles, rewording the prompt — never
requires touching unrelated stage code.
"""
from __future__ import annotations

from .generate import generate_persona
from .profiles import HOUSEHOLD_PROFILES
from .prompts import PERSONA_SYSTEM_PROMPT
from .schema import AGE_BANDS, PERSONA_SCHEMA

__all__ = [
    "generate_persona",
    "HOUSEHOLD_PROFILES",
    "PERSONA_SYSTEM_PROMPT",
    "AGE_BANDS",
    "PERSONA_SCHEMA",
]
