"""
clutter/ — Tier 2b static-clutter placement (see env/inventory.py's module
docstring for the full tier rationale).

HSSD's uncluttered scene variant places Tier 1 furniture and Tier 2a
(chair/stool/potted_plant/cushion) with real ground-truth positions, but
omits small clutter (books, candles, vases, bowls, cups, drinkware,
bottles) entirely. Without this stage, those categories only ever "existed"
via a flat insert_new assumption with no real starting position — exactly
the kind of generation-schedule artifact the tier split exists to remove.
This stage invents a real starting slot for them once, before any
activity/displacement stage runs, so they enter the scene the same way
Tier 1/2a furniture does.
"""
from __future__ import annotations

from .generate import generate_clutter
from .prompts import CLUTTER_SYSTEM_PROMPT

__all__ = ["generate_clutter", "CLUTTER_SYSTEM_PROMPT"]
