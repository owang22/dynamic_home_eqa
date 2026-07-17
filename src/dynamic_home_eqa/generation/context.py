"""
ContextBuilder — named, composable prompt blocks.

Each stage assembles the blocks it needs from these builders instead of
hand-rolling prompt strings at the call site. All blocks are static-state
safe (nothing here needs the running world state Phase 3 adds); surface
occupancy is explicitly labeled "start-of-day" until then.

Blocks:
  occupant_card(persona, name)   — who this occupant is, what they own, where they sleep
  temporal_context(trace, start) — the window's clock time + today's activities so far
  surface_occupancy(room, ...)   — start-of-day object counts per anchor in a room
  candidate_line(i, c)           — the per-candidate line the judge/proposer share

Changing what these emit is a prompt change that the cache can't hash
automatically (it's Python, not a template) — bump BUILDER_VERSION in
prompt_registry when you do (see that module's docstring).
"""
from __future__ import annotations

from typing import Optional

from .ownership import assign_bedrooms, assign_ownership


def clock(hour: float) -> str:
    """8.5 -> '08:30', 19.0 -> '19:00', 22.25 -> '22:15' (wraps past 24h)."""
    h = hour % 24
    hh = int(h)
    mm = int(round((h - hh) * 60))
    if mm == 60:
        hh = (hh + 1) % 24
        mm = 0
    return f"{hh:02d}:{mm:02d}"


def occupant_card(persona: dict, occupant_name: str) -> str:
    """One-block description of the acting occupant: role, age, tidiness, the
    carried items they own, and their bedroom. Gives the judge/proposer the
    identity context ('Michael is the son') the bare name never carried."""
    occ = next((o for o in persona.get("occupants", []) if o.get("name") == occupant_name), None)
    owned = assign_ownership(persona).get(occupant_name, [])
    bedroom = assign_bedrooms(persona).get(occupant_name, 1)
    if occ is None:
        return f"Occupant: {occupant_name} (unknown to persona)."
    parts = [
        f"Occupant: {occupant_name} ({occ.get('role', 'unknown')}, {occ.get('age_band', 'adult')})",
        f"tidiness {float(occ.get('tidiness', 0.5)):.1f}/1.0",
        f"owns: {', '.join(owned) if owned else 'no carried items'}",
        f"sleeps in bedroom {bedroom}",
    ]
    if occ.get("habits"):
        parts.append(f"habits: {occ['habits']}")
    return " | ".join(parts) + "."


def temporal_context(trace: Optional[dict], start: float, end: float) -> str:
    """The window as clock time plus the occupant's activity sequence earlier
    today (fully known from the trace — no running state needed). Lets the
    judge reason about 'this is dinner at 19:00, after a full day' rather than
    an isolated activity label."""
    header = f"Time: {clock(start)}–{clock(end)}."
    if not trace:
        return header
    prior = [
        a for a in trace.get("activities", [])
        if float(a.get("start", 0)) < start and float(a.get("start", 0)) <= float(a.get("end", 0)) + 24
    ]
    prior.sort(key=lambda a: float(a.get("start", 0)))
    if not prior:
        return header + " Earlier today: (start of day)."
    seq = ", ".join(f"{clock(float(a['start']))} {a.get('activity', '?')}" for a in prior[-8:])
    return header + f" Earlier today: {seq}."


def surface_occupancy(room: Optional[str], data: Optional[dict], live: bool = False) -> str:
    """Object counts for the room's anchors.

    live=False (default): start-of-day — `data` is the whole room_inventory,
    keyed room -> {category: count}, labeled "start-of-day".
    live=True (Phase 3): `data` is already {anchor: count} for objects
    currently sitting in this room, from the running state, labeled "now"."""
    if not room or not data:
        return ""
    if live:
        items = ", ".join(f"{anchor}×{n}" for anchor, n in sorted(data.items()))
        return f"Objects currently placed in {room}: {items}."
    cats = data.get(room)
    if not cats:
        return ""
    items = ", ".join(f"{cat}×{n}" for cat, n in sorted(cats.items()))
    return f"Start-of-day objects in {room}: {items}."


def candidate_line(i: int, c: dict) -> str:
    """The per-candidate line shared by the judge and (centralized here) any
    future proposer echo — one place to change the format.

    Shows the proposer's `reason` (its pre-proposal reasoning) and, for an
    instance-explicit proposal (seat instances), WHICH instance moves —
    the judge should know it's stool_2 being returned, not "a stool"."""
    reason = c.get("reason", "")
    obj = c.get("_instance") or c.get("object_category", "")
    return (f"  [{i}] {obj} {c.get('target_relationship', '')} "
            f"{c.get('target_anchor', '')} — reason: {reason}")
