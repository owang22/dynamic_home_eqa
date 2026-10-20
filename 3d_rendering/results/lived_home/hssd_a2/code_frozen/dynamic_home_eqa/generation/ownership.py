"""
Per-occupant Tier-3 ownership (phone / wallet / keys / laptop).

Tier-3 items used to be a flat per-scene count (one household laptop), so
every occupant's proposer could move "the laptop" and a single instance
accumulated everyone's moves. Ownership makes each carried item belong to a
specific occupant: only that occupant proposes moving it, and its manifest
instance is owner-named (michael_laptop), so per-owner move counts are
coherent.

assign_ownership() prefers the persona's own per-occupant `owned_items` (new
persona schema field); when absent — an old persona, or an LLM omission — it
falls back to a deterministic age-band default, so the ContextBuilder and the
proposer work on any persona.
"""
from __future__ import annotations

# The carried categories ownership applies to (matches env.inventory.TIER3_MOBILE).
TIER3_CATEGORIES: list[str] = ["phone", "wallet", "keys", "laptop",
                               "backpack", "sunglasses", "headphones", "medicine"]

# Deterministic fallback: who plausibly owns what, by age band. Used only when
# the persona doesn't state owned_items for an occupant. The expansion
# categories are deliberately age-skewed: backpacks belong to school-age
# kids, headphones to teens, medicine to seniors — not "everyone gets
# everything", which would flood every window's vocabulary and read as a
# household of clones.
_FALLBACK_BY_AGE: dict[str, list[str]] = {
    "adult":        ["phone", "wallet", "keys", "laptop", "sunglasses"],
    "senior":       ["phone", "wallet", "keys", "medicine"],
    "teen":         ["phone", "laptop", "keys", "headphones", "backpack"],
    "older_child":  ["phone", "backpack"],
    "young_child":  ["backpack"],
    "toddler":      [],
}


def _normalize(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def fallback_owned(age_band: str) -> list[str]:
    return list(_FALLBACK_BY_AGE.get(age_band, ["phone", "wallet", "keys"]))


def assign_ownership(persona: dict) -> dict[str, list[str]]:
    """{occupant_name: [owned Tier-3 categories]} for every occupant. Uses the
    occupant's persona `owned_items` when present and valid, else the age-band
    fallback."""
    out: dict[str, list[str]] = {}
    for occ in persona.get("occupants", []):
        name = occ.get("name", "")
        stated = occ.get("owned_items")
        if isinstance(stated, list):
            owned = [c for c in stated if c in TIER3_CATEGORIES]
        else:
            owned = fallback_owned(occ.get("age_band", "adult"))
        out[name] = owned
    return out


def _fallback_bedrooms(occupants: list[dict]) -> dict[str, int]:
    """Deterministic bedroom assignment when the persona doesn't state one:
    adults/seniors share bedroom 1 (a couple), each child gets the next index;
    a childless or adultless household falls back to occupant-index order."""
    has_adult = any(o.get("age_band") in ("adult", "senior") for o in occupants)
    if not has_adult:
        return {o.get("name", ""): i + 1 for i, o in enumerate(occupants)}
    out: dict[str, int] = {}
    child_idx = 2
    for o in occupants:
        if o.get("age_band") in ("adult", "senior"):
            out[o.get("name", "")] = 1
        else:
            out[o.get("name", "")] = child_idx
            child_idx += 1
    return out


def assign_bedrooms(persona: dict) -> dict[str, int]:
    """{occupant_name: 1-based bedroom index}. Uses each occupant's persona
    `bedroom_index` when present, else the deterministic household fallback."""
    occs = persona.get("occupants", [])
    fb = _fallback_bedrooms(occs)
    out: dict[str, int] = {}
    for o in occs:
        name = o.get("name", "")
        idx = o.get("bedroom_index")
        out[name] = int(idx) if isinstance(idx, int) and idx >= 1 else fb.get(name, 1)
    return out


def tier3_instance_label(occupant: str, category: str) -> str:
    """Owner-named Tier-3 instance id, e.g. ('Michael', 'laptop') -> 'michael_laptop'."""
    return f"{_normalize(occupant)}_{category}"


def restrict_inventory_to_owner(inventory: dict[str, int], owned: list[str]) -> dict[str, int]:
    """A copy of `inventory` with Tier-3 categories the occupant does NOT own
    removed, so the proposer can't offer this occupant an item they don't
    carry. Non-Tier-3 categories are untouched."""
    owned_set = set(owned)
    return {
        cat: n for cat, n in inventory.items()
        if cat not in TIER3_CATEGORIES or cat in owned_set
    }
