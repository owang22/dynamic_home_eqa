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

This is prompt/selection-level state (informs the LLM and the sampler);
build_manifest remains the authority for the emitted change log.
"""
from __future__ import annotations

import collections
import hashlib
from typing import Optional

from .ownership import TIER3_CATEGORIES, tier3_instance_label

from .schemas import PUT_AWAY_ANCHOR as PUT_AWAY  # "put_away" despawn target


class RunningState:
    def __init__(self) -> None:
        self.tier3: dict[str, Optional[str]] = {}      # owner_label -> location or None
        self.moved_today: dict[str, str] = {}          # label -> current location
        # Tier-2 instance tracking (chair_1..chair_N, bowl_1..bowl_N), seeded
        # from the scene's real instances (Tier-2a) plus the clutter pass's
        # invented starting placements (Tier-2b, via seed_clutter) so apply()
        # resolves WHICH instance a proposal moves — the same room-aware
        # resolution build_manifest uses (generation/instances.py), so the
        # prompt state and the manifest replay track the same instance.
        self.tier2_pool: dict[str, list[str]] = {}     # category -> [instance ids]
        self.tier2_slots: dict[str, Optional[str]] = {}  # instance id -> current slot
        # label -> the relationship of its current placement ("on_top",
        # "next_to", "tucked_under", ...) — display-context for the state
        # block ("stool_1: tucked under kitchen.counter_1" reads very
        # differently from "next to kitchen.counter_1", and the bare slot
        # string doesn't always distinguish them).
        self.relations: dict[str, str] = {}

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

    def seed_clutter(self, placements: list[dict], resolver=None) -> None:
        """Register the clutter pass's Tier-2b starting placements as tracked
        instances (bowl_1..bowl_N), mirroring build_manifest's own numbering
        (same iteration order over the accepted placements) so the labels the
        prompt state shows are the labels the manifest will emit. `resolver`
        (placement -> slot string, i.e. rooms.resolve_slot bound to this
        scene's census) makes the tracked slots the SAME resolved strings the
        manifest uses — required for the gate preflight's no-op comparison;
        without it the raw target_anchor is stored (prompt-display quality
        only)."""
        counters: dict[str, int] = {}
        for p in placements:
            cat = p.get("object_category", "")
            counters[cat] = counters.get(cat, 0) + 1
            iid = f"{cat}_{counters[cat]}"
            self.tier2_pool.setdefault(cat, []).append(iid)
            slot = None
            if resolver is not None:
                try:
                    slot = resolver(p)
                except Exception:
                    slot = None
            self.tier2_slots[iid] = slot or p.get("target_anchor") or None
            if p.get("target_relationship"):
                self.relations[iid] = p["target_relationship"]

    def categories_present_in(self, room: Optional[str]) -> set[str]:
        """Tier-2a categories with at least one instance currently in `room`
        (canonical room aliasing). Drives the seat-in-room vocabulary gate:
        chair/stool are only proposable where one physically is — nobody
        fetches a bedroom chair to sit at lunch; scenes are seat-poor (992
        has two chairs, both on the patio), so absent this gate the
        lowest-index fallback teleported one chair everywhere."""
        if room is None:
            return set(self.tier2_pool.keys())
        from .instances import instance_room
        from ..rooms import rooms_match
        out: set[str] = set()
        for cat, pool in self.tier2_pool.items():
            for iid in pool:
                r = instance_room(self.tier2_slots.get(iid))
                if r is not None and rooms_match(r, room):
                    out.add(cat)
                    break
        return out

    def _tier2_label(self, category: str, room: Optional[str]) -> Optional[str]:
        """Which real instance a category-level proposal touches, or None
        when the category has no tracked real instances (clutter categories
        stay category-keyed)."""
        pool = self.tier2_pool.get(category)
        if not pool:
            return None
        from .instances import pick_real_instance
        return pick_real_instance(category, pool, self.tier2_slots, room)

    def seat_instances_in_room(self, room: Optional[str]) -> dict[str, str]:
        """{instance_id: current slot} for floor-bound seat instances (chair/
        stool) currently in `room` — the per-instance seat vocabulary the
        proposer offers (schema enum) so two occupants can use DIFFERENT
        chairs instead of both collapsing onto the same lowest-index one."""
        from ..env.inventory import FLOOR_BOUND_CATEGORIES
        from .instances import instance_room
        from ..rooms import rooms_match
        out: dict[str, str] = {}
        for cat in FLOOR_BOUND_CATEGORIES:
            for iid in self.tier2_pool.get(cat, []):
                slot = self.tier2_slots.get(iid)
                r = instance_room(slot)
                if slot and r is not None and (room is None or rooms_match(r, room)):
                    out[iid] = slot
        return out

    def _placed(self, lbl: str, loc: str) -> str:
        """'on kitchen.table_1' / 'tucked under kitchen.counter_1' /
        'kitchen.table_1' (no relation known) — the state-block location
        text, with the placement relationship for context."""
        rel = self.relations.get(lbl, "")
        rel = {"on_top": "on", "on": "on", "inside": "inside", "within": "inside",
               "next_to": "next to", "near": "near",
               "tucked_under": "tucked under"}.get(rel, rel.replace("_", " "))
        if rel == "tucked under" and loc.endswith(".tucked"):
            loc = loc[:-len(".tucked")]  # "tucked under kitchen.counter_1.tucked" reads twice
        return f"{rel} {loc}" if rel else loc

    # ── prompt block ────────────────────────────────────────────────────────
    def object_state_block(self, occupant: str, owned: list[str],
                           room: Optional[str] = None) -> str:
        """Compact current-state block for the acting occupant: their own
        carried items' whereabouts + everything already moved today + (when
        `room` is given) each seat instance currently in that room, by id, so
        the proposer can name a specific free seat instead of a bare
        category that resolves onto whichever chair someone else is using."""
        lines: list[str] = []
        for cat in owned:
            lbl = tier3_instance_label(occupant, cat)
            loc = self.tier3.get(lbl)
            lines.append(f"  {cat} (yours): "
                         f"{'put away / not out yet' if loc is None else self._placed(lbl, loc)}")
        for lbl, loc in sorted(self.moved_today.items()):
            if lbl in self.tier3:
                continue  # this occupant's Tier-3 already listed above; others' shown here
            lines.append(f"  {lbl}: {self._placed(lbl, loc)}")
        # other occupants' Tier-3 that are currently out
        for lbl, loc in sorted(self.tier3.items()):
            if loc is not None and lbl not in {tier3_instance_label(occupant, c) for c in owned}:
                lines.append(f"  {lbl}: {self._placed(lbl, loc)}")
        seats = self.seat_instances_in_room(room) if room else {}
        for iid, slot in sorted(seats.items()):
            moved = " (moved earlier today)" if iid in self.moved_today else ""
            lines.append(f"  {iid} (floor-standing, in this room): {self._placed(iid, slot)}{moved}")
        # Clutter instances already OUT in this room (start-of-day placements
        # that haven't moved — moved ones are listed above): the abundance
        # rule tells the proposer a fresh bowl may come out even when one is
        # already sitting out, which only means something if it can SEE the
        # one that's out.
        if room:
            from ..env.inventory import TIER2_CLUTTER_CATALOG
            from .instances import instance_room
            from ..rooms import rooms_match
            for cat in sorted(set(self.tier2_pool) & set(TIER2_CLUTTER_CATALOG)):
                for iid in self.tier2_pool[cat]:
                    slot = self.tier2_slots.get(iid)
                    r = instance_room(slot)
                    if (slot and iid not in self.moved_today
                            and r is not None and rooms_match(r, room)):
                        lines.append(f"  {iid} (out in this room): {self._placed(iid, slot)}")
        if not lines:
            return ""
        return ("Current object state (start-of-day placements plus what has moved so "
                "far today — reason against THIS, not a guess):\n" + "\n".join(lines))

    def state_hash(self, occupant: str, owned: list[str],
                   room: Optional[str] = None) -> str:
        """8-char hash of this occupant's state block — folded into the
        displacement/judge stage tags so later windows depend on earlier
        outcomes and stale cache is never served (Phase 3 cache-correctness)."""
        return hashlib.sha256(self.object_state_block(occupant, owned, room=room).encode()).hexdigest()[:8]

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
        from ..env.inventory import ABUNDANT_STORAGE_CATEGORIES, TIER2_CLUTTER_CATALOG
        for p in chosen:
            cat = p.get("object_category", "")
            # Prefer the manifest-grade resolved slot the gate preflight
            # attached (see pipeline's preflight) — the same string
            # build_manifest will record — falling back to the raw anchor
            # for callers that didn't preflight (tests, legacy paths).
            anchor = p.get("_resolved_slot") or p.get("target_anchor", "")
            occ = p.get("_occupant", "")
            if p.get("_despawn") or p.get("target_anchor") == PUT_AWAY or anchor == PUT_AWAY:
                if cat in TIER3_CATEGORIES:
                    lbl = tier3_instance_label(occ, cat)
                    self.tier3[lbl] = None
                    self.moved_today.pop(lbl, None)
                else:
                    # Tier-2 concealment ('inside' closed storage): the
                    # instance is out of sight — state shows WHERE it was
                    # stored so later proposers/judges know it's gone.
                    explicit = p.get("_instance")
                    lbl = explicit if (explicit and explicit in self.tier2_slots) \
                        else self._tier2_label(cat, p.get("_location"))
                    if lbl:
                        self.tier2_slots[lbl] = None
                        self.relations.pop(lbl, None)
                        self.moved_today[lbl] = (
                            f"put away (stored in {p.get('_concealed_in', 'storage')})")
                continue
            if cat in TIER3_CATEGORIES:
                lbl = tier3_instance_label(occ, cat)
                self.tier3[lbl] = anchor
                self.moved_today[lbl] = anchor
            else:
                explicit = p.get("_instance")
                if explicit and explicit in self.tier2_slots:
                    lbl = explicit
                else:
                    lbl = self._tier2_label(cat, p.get("_location")) or cat
                # Abundant-storage spawn, mirroring build_manifest: the
                # resolved instance is already at the destination, so this
                # move brings a FRESH one out of storage — track it as a new
                # instance rather than re-recording the same slot (which is
                # what made the state block lie about how many are out).
                if (cat in ABUNDANT_STORAGE_CATEGORIES
                        and lbl in self.tier2_slots
                        and self.tier2_slots.get(lbl) == anchor
                        and len(self.tier2_pool.get(cat, [])) < TIER2_CLUTTER_CATALOG.get(cat, 0)):
                    lbl = f"{cat}_{len(self.tier2_pool[cat]) + 1}"
                    self.tier2_pool[cat].append(lbl)
                if lbl in self.tier2_slots or lbl in self.tier2_pool.get(cat, []):
                    self.tier2_slots[lbl] = anchor
                self.moved_today[lbl] = anchor
            if p.get("target_relationship"):
                self.relations[lbl] = p["target_relationship"]
