"""
Running world state for sequential (per-window) generation — Phase 3.

Batch generation proposed every window's moves independently, so the proposer
and judge never knew where an object already was; they guessed (assumed_from).
Phase 3 threads a running {instance: location} state through the day in
chronological window order: after each window's moves are selected, they're
applied here, and the next window's proposer/judge see the authoritative
current state instead of a guess.

Scope of the tracked state (kept compact, matches the prompt block the plan
specifies — "only Tier-3 items and any object already moved today"):
  - tier3: each owned carried item's current location, or None when it's
    put away / not out yet. Keyed by the owner-named manifest label
    (michael_laptop) so it lines up with build_manifest.
  - moved_today: any object (Tier-2 by category, Tier-3 by owner label) that
    has moved today, with its current location.
  - anchor_uses: per-destination-anchor count today, for selection's
    repeat-downweight.

This is prompt/selection-level state (informs the LLM and the sampler);
build_manifest remains the authority for the emitted change log.
"""
from __future__ import annotations

import collections
import hashlib
from typing import Optional

from .ownership import TIER3_CATEGORIES, tier3_instance_label

from .schemas import PUT_AWAY_ANCHOR as PUT_AWAY  # "put_away" despawn target


def _ordinal(n: int) -> str:
    """1 -> '1st', 2 -> '2nd', 7 -> '7th', 11 -> '11th'."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


class RunningState:
    def __init__(self) -> None:
        self.tier3: dict[str, Optional[str]] = {}      # owner_label -> location or None
        self.moved_today: dict[str, str] = {}          # label -> current location
        self.anchor_uses: collections.Counter = collections.Counter()
        # Tier-2a instance tracking (chair_1..chair_N), seeded from the
        # scene's real instances so apply()/move_history_note resolve WHICH
        # chair a category-level proposal moves — the same room-aware
        # resolution build_manifest uses (generation/instances.py), so the
        # judge's per-instance history note counts the instance the manifest
        # will actually move, not a category-wide lump of all ten chairs.
        self.tier2_pool: dict[str, list[str]] = {}     # category -> [instance ids]
        self.tier2_slots: dict[str, Optional[str]] = {}  # instance id -> current slot
        # Ordered list of destinations each instance has been moved to today,
        # keyed the same way as moved_today (owner label for Tier-3, category
        # otherwise). Fed to the JUDGE (not the sampler) as a candidate-line
        # annotation — "this is potted_plant_1's 7th move today (bedroom -> ...)"
        # — so it can price cumulative implausibility contextually (a phone's
        # 7th move is fine, a potted plant's 7th is absurd), which a blind
        # per-object formula can't distinguish.
        self.move_history: dict[str, list[str]] = {}

    @classmethod
    def initial(cls, ownership: dict[str, list[str]],
                scene_state=None) -> "RunningState":
        st = cls()
        for occ, owned in ownership.items():
            for cat in owned:
                st.tier3[tier3_instance_label(occ, cat)] = None  # starts not out
        if scene_state is not None:
            for iid, inst in scene_state.instances.items():
                if inst.category in TIER3_CATEGORIES or inst.states:
                    continue  # Tier-3 handled above; stateful furniture never moves
                st.tier2_pool.setdefault(inst.category, []).append(iid)
                st.tier2_slots[iid] = inst.current_semantic or None
        return st

    def _tier2_label(self, category: str, room: Optional[str]) -> Optional[str]:
        """Which real instance a category-level proposal touches, or None
        when the category has no tracked real instances (clutter categories
        stay category-keyed)."""
        pool = self.tier2_pool.get(category)
        if not pool:
            return None
        from .instances import pick_real_instance
        return pick_real_instance(category, pool, self.tier2_slots, room)

    # ── prompt block ────────────────────────────────────────────────────────
    def object_state_block(self, occupant: str, owned: list[str]) -> str:
        """Compact current-state block for the acting occupant: their own
        carried items' whereabouts + everything already moved today."""
        lines: list[str] = []
        for cat in owned:
            lbl = tier3_instance_label(occupant, cat)
            loc = self.tier3.get(lbl)
            lines.append(f"  {cat} (yours): {'put away / not out yet' if loc is None else loc}")
        for lbl, loc in sorted(self.moved_today.items()):
            if lbl in self.tier3:
                continue  # this occupant's Tier-3 already listed above; others' shown here
            lines.append(f"  {lbl}: {loc}")
        # other occupants' Tier-3 that are currently out
        for lbl, loc in sorted(self.tier3.items()):
            if loc is not None and lbl not in {tier3_instance_label(occupant, c) for c in owned}:
                lines.append(f"  {lbl}: {loc}")
        if not lines:
            return ""
        return ("Current object state (start-of-day placements plus what has moved so "
                "far today — reason against THIS, not a guess):\n" + "\n".join(lines))

    def state_hash(self, occupant: str, owned: list[str]) -> str:
        """8-char hash of this occupant's state block — folded into the
        displacement/judge stage tags so later windows depend on earlier
        outcomes and stale cache is never served (Phase 3 cache-correctness)."""
        return hashlib.sha256(self.object_state_block(occupant, owned).encode()).hexdigest()[:8]

    # ── judge move-history annotation ────────────────────────────────────────
    def move_history_note(self, occupant: str, category: str,
                          room: Optional[str] = None) -> str:
        """One-line annotation for the judge's candidate line: how many times
        this object has already moved today and the room-level path it took, so
        the judge can weigh CUMULATIVE plausibility (a phone's 7th move is fine,
        a potted plant's 7th is absurd). Empty when it hasn't moved yet."""
        from ..rooms import slot_room
        if category in TIER3_CATEGORIES:
            lbl = tier3_instance_label(occupant, category)
        else:
            lbl = self._tier2_label(category, room) or category
        hist = self.move_history.get(lbl, [])
        if not hist:
            return ""
        rooms = [slot_room(a) or (a.split(".")[0] if "." in a else a) for a in hist]
        chain = " -> ".join(rooms)
        # This candidate, if selected, would be the (len+1)th move of the day.
        # Fact only — the cumulative-justification rubric lives once in the
        # judge prompt (prompt_registry), not repeated per candidate.
        return (f"move history: this would be {lbl}'s {_ordinal(len(hist) + 1)} relocation "
                f"today (already moved {len(hist)}x: {chain})")

    # ── live surface occupancy ────────────────────────────────────────────────
    def anchors_in_use(self, room: Optional[str]) -> dict[str, int]:
        """{anchor: count} of objects currently sitting on anchors in `room`
        (matched via the canonical room aliasing), for the live
        surface_occupancy block."""
        from ..rooms import rooms_match
        out: collections.Counter = collections.Counter()
        seen_locs = list(self.moved_today.values()) + [v for v in self.tier3.values() if v]
        for loc in seen_locs:
            if not loc or loc == PUT_AWAY:
                continue
            anchor_room = loc.split(".")[0] if "." in loc else loc
            if room is None or rooms_match(anchor_room, room):
                out[loc] += 1
        return dict(out)

    # ── apply a window's selected moves ───────────────────────────────────────
    def apply(self, chosen: list[dict]) -> None:
        for p in chosen:
            cat = p.get("object_category", "")
            anchor = p.get("target_anchor", "")
            occ = p.get("_occupant", "")
            if p.get("_despawn") or anchor == PUT_AWAY:
                lbl = tier3_instance_label(occ, cat)
                self.tier3[lbl] = None
                self.moved_today.pop(lbl, None)
                continue
            if cat in TIER3_CATEGORIES:
                lbl = tier3_instance_label(occ, cat)
                self.tier3[lbl] = anchor
                self.moved_today[lbl] = anchor
            else:
                lbl = self._tier2_label(cat, p.get("_location")) or cat
                if lbl in self.tier2_slots:
                    self.tier2_slots[lbl] = anchor
                self.moved_today[lbl] = anchor
            self.anchor_uses[anchor] += 1
            self.move_history.setdefault(lbl, []).append(anchor)
