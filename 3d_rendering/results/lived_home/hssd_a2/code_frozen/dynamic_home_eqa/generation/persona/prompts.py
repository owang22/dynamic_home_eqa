"""System prompt for the persona stage.

The template now lives in generation/prompt_registry.py (single source, with
its content hash); this re-exports it under the original name for callers.
"""
from __future__ import annotations

from ..prompt_registry import PERSONA as _PERSONA

PERSONA_SYSTEM_PROMPT = _PERSONA.text
