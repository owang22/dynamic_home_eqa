"""
MCQ text templates for Dynamic EQA questions.

render_question() produces the question prompt string.
slot_desc() and SLOT_DESCRIPTIONS live in env.deltas to keep one source of truth.
"""
from __future__ import annotations

from .._compat import slot_desc  # re-export for callers that import from here


_LOCATION_TEMPLATES = {
    "phone":        "Where is the phone?",
    "wallet":       "Where is the wallet?",
    "keys":         "Where are the keys?",
    "laptop":       "Where is the laptop?",
    "book":         "Where is the book?",
    "candle":       "Where is the candle?",
    "bottle":       "Where is the bottle?",
    "drinkware":    "Where is the drinkware (mug/cup)?",
    "bowl":         "Where is the bowl?",
    "vase":         "Where is the vase?",
    "chair":        "Where is the chair?",
    "stool":        "Where is the stool?",
    "potted_plant": "Where is the potted plant?",
    "table":        "Where is the table?",
    "couch":        "Where is the couch?",
}

_PRESENCE_TEMPLATE  = "Is there a {category} at {slot}?"
_COUNT_TEMPLATE     = "How many {category}(s) are at {slot}?"


def render_question(
    query_type: str,
    object_category: str,
    target_slot: str | None,
) -> str:
    """Return the MCQ question string."""
    if query_type == "location":
        return _LOCATION_TEMPLATES.get(
            object_category,
            f"Where is the {object_category.replace('_', ' ')}?",
        )
    if query_type == "presence":
        return _PRESENCE_TEMPLATE.format(
            category=object_category.replace("_", " "),
            slot=slot_desc(target_slot or ""),
        )
    if query_type == "count":
        return _COUNT_TEMPLATE.format(
            category=object_category.replace("_", " "),
            slot=slot_desc(target_slot or ""),
        )
    return f"What is the state of {object_category}?"
