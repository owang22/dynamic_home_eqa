"""System prompt for the Tier 2b clutter-placement stage.

The template now lives in generation/prompt_registry.py (single source, with
its content hash); this re-exports it under the original name for callers.
"""
from __future__ import annotations

from ..prompt_registry import CLUTTER as _CLUTTER

CLUTTER_SYSTEM_PROMPT = _CLUTTER.text
