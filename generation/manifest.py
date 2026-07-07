"""
Bridge from LLM generation output to the manifest.json Change-log schema.

generate_for_scene() (pipeline.py) produces {persona, traces, displacements,
clutter}, where each displacement proposal carries only an activity time
window ([_start, _end]) and a category-level description (object_category,
target_relationship, target_anchor) — no persistent object identity and no
concrete timestamp. env/replay.py, qa/questions.py, and agents/harness.py all
require a Change log: concrete instance_id, a point-in-time t, and
from_semantic/to_semantic slot strings.

build_manifest() closes that gap: it walks the accepted displacements in
chronological order, replaying them against a running SceneState per
household-day, and applies the trace-integrity contract every exported day
must satisfy (see trace_validate.py, which independently checks all of this):

  - Chain consistency: from_semantic always comes from tracked state
    (current_slot), never from_semantic == to_semantic by construction, and
    never taken from the LLM's own belief about prior state. A label's
    genuine first event has from_semantic=None (nothing to chain from), not
    a fabricated value — see the no-op note below for why that distinction
    matters. Real-instance-backed categories (Tier 1/2a/2b — anything with a
    real starting instance in this scene, see env/inventory.py) are tracked
    by category alone: exactly one real instance is animated per category
    per day, chosen deterministically (sorted pool, first) rather than
    fragmented across (category, occupant) pairs. The old per-occupant
    keying let two occupants' proposals for the same category resolve to
    two different real instances via a pool-exhaustion reuse fallback,
    which is what produced incoherent from/to chains when a scene had more
    than one real instance of a category — this is the actual root cause a
    manual trace audit traced 17 chain breaks in one generated day back to.
  - Insert-once: insert_new fires at most once per label — its true first
    event, and only for volatile (Tier 3, no real starting instance) labels.
    Real-instance-backed labels are always move_existing, including their
    first event (the object already existed in the scene). The prior
    implementation computed change_type per-event from has_real_instance
    alone, so every event for a volatile label was insert_new forever, not
    just the first — the direct cause of ~45% of one audited day's events
    being repeated inserts of an already-tracked label.
  - No no-ops: a proposal whose resolved to_semantic equals the label's
    current from_semantic is dropped (not exported) and counted, since
    nothing observably changed.
  - Attendance: every exported event is attributed to a `mover` — an
    occupant independently confirmed (via `traces`) to be in the event's
    source or destination room at event time. A proposal with no
    attributable occupant is dropped (not exported) and counted. This is
    mostly a formality once generation itself room-scopes each proposal's
    anchor vocabulary to the acting occupant's current activity.location
    (see generation/stages.py's generate_displacements) — the recorded
    `_location` on each proposal already guarantees the destination room
    matches; this check is defense-in-depth against that upstream guarantee
    ever silently failing (e.g. the room-scoping fallback firing, or
    _location being absent on the live-WorldGraph path), not the primary
    mechanism.
  - assumed_from (the LLM's own free-text belief about the object's prior
    location — a diagnostic field, see schemas.py) is preserved verbatim as
    llm_claimed_from and never used to write from_semantic. Divergences
    from the real tracked from_semantic are counted (integrity_stats
    ["llm_claim_divergence"]) as a signal of model/prompt confusion, not
    acted upon.
  - confidence is genuine per-event behavioral-plausibility scoring
    (plausibility.score_confidence) — occupant-capability, egress, and
    ping-pong penalties — not a placeholder constant.

Tier awareness (see env/inventory.py's module docstring for the full
rationale): whether a category is real-instance-backed (move_existing,
never insert_new) or volatile (insert_new once, then move_existing) is
decided by whether it already has a real starting instance in this scene —
not by a hardcoded tier-membership check. That pool is seeded from two
sources before any displacement is replayed: Tier 2a instances HSSD
actually places (load_scene_state) and Tier 2b clutter generation/clutter/
invented a starting slot for (generation_result["clutter"]). Anything with
neither is Tier 3 and falls back to insert_new (spawn/despawn semantics not
yet implemented — see env/inventory.py).
"""
from __future__ import annotations

import logging
from typing import Optional

from ..env.inventory import load_scene_state
from ..env.state import ObjectInstance
from ..plausibility import score_confidence
from ..rooms import occupants_in_room, resolve_slot, slot_room
from .cache import make_seed

_logger = logging.getLogger(__name__)


def _pick_time(household_id: str, day: int, index: int, start: float, end: float) -> float:
    """Deterministic point-in-time within [start, end), seeded like the LLM calls.

    Strictly less than end, even after rounding to 3 decimals — rooms.location_at
    (and any other window lookup keyed on this same [start, end)) treats end as
    exclusive, so a jittered t that rounds up to exactly end would silently
    fall outside the activity window it was drawn from.
    """
    if end <= start:
        return round(start, 3)
    seed = make_seed(household_id, day, "manifest_time", index)
    frac = (seed % 10_000) / 10_000.0
    t = start + frac * (end - start)
    return round(min(t, end - 1e-3), 3) if end - start > 1e-3 else round(start, 3)


def _same_claim(llm_claimed: str, from_slot: str) -> bool:
    """Loose match between the LLM's free-text assumed_from guess and the
    real tracked from_slot. Diagnostic only (see llm_claimed_from), so an
    approximate token-overlap check is enough — this never gates anything."""
    norm_claim = llm_claimed.lower().replace(" ", "_").replace("-", "_")
    norm_slot  = from_slot.lower().replace(".", "_").replace(" ", "_")
    if norm_claim in norm_slot or norm_slot in norm_claim:
        return True
    return any(tok in norm_slot for tok in norm_claim.split("_") if len(tok) > 3)


def build_manifest(
    scene_id: str,
    household_type: str,
    day: int,
    generation_result: dict,
    seed: int = 1,
    include_state_changes: bool = False,
) -> dict:
    """Convert generate_for_scene()'s output into a manifest.json-shaped dict.

    Displacements are sorted by activity start time and replayed against a
    running SceneState (seeded from the scene's real furniture instances) so
    from_semantic/to_semantic form a coherent day, not independent snapshots.
    See the module docstring for the full trace-integrity contract this
    enforces; trace_validate.validate() checks it independently.

    include_state_changes (M3, default False): also mix in
    build_state_changes()'s deterministic state-change events. Defaults to
    False so every existing caller/test keeps its exact current output —
    opt in explicitly for a fresh full-pipeline run that wants the state
    stratum too. The frozen scene's existing manifests were never built
    with this on; scripts/generate_state_stratum.py adds state changes to
    them separately (new sibling folders), not by flipping this flag and
    rebuilding in place (see experiment_config.py's module docstring on
    why the frozen folders are never regenerated in place).
    """
    household_id = generation_result["household_id"]
    persona = generation_result.get("persona", {})
    traces  = generation_result.get("traces", [])
    occupant_age_band = {
        o["name"]: o.get("age_band") for o in persona.get("occupants", [])
    }

    scene_state = load_scene_state(scene_id)  # Tier 2a: real HSSD instances

    # Tier 2b: clutter generation/clutter/ invented a starting slot for.
    # Merged into the same pool as Tier 2a so the real-instance-backed vs.
    # volatile decision below doesn't need to know which sub-tier a category
    # is — it just checks whether a real starting instance exists at all.
    # Clutter has no occupant/activity context (it's the day's t=0 starting
    # state, not something anyone "did"), so its slot resolution has no room
    # to disambiguate with — same room-agnostic resolution as before.
    clutter_counters: dict[str, int] = {}
    for placement in generation_result.get("clutter", []):
        cat = placement["object_category"]
        clutter_counters[cat] = clutter_counters.get(cat, 0) + 1
        iid = f"{cat}_{clutter_counters[cat]}"
        slot = resolve_slot(placement["target_anchor"], placement["target_relationship"])
        scene_state.instances[iid] = ObjectInstance(
            instance_id=iid, category=cat, current_semantic=slot,
        )

    furniture_pool: dict[str, list[str]] = {}
    for iid, inst in scene_state.instances.items():
        furniture_pool.setdefault(inst.category, []).append(iid)

    # One real instance animated per category per day (see module docstring
    # for why this replaced (category, occupant)-scoped assignment).
    real_assigned: dict[str, str] = {}
    volatile_assigned: dict[tuple[str, str], str] = {}
    volatile_counters: dict[str, int] = {}
    seen_labels: set[str] = set()
    current_slot: dict[str, str] = {
        iid: inst.current_semantic for iid, inst in scene_state.instances.items()
    }
    move_times: dict[str, list[float]] = {}

    displacements = sorted(
        generation_result.get("displacements", []),
        key=lambda p: (float(p.get("_start", 0.0)), p.get("_occupant", ""), p.get("_activity", "")),
    )

    # t is picked with jitter within each proposal's own [_start, _end] window
    # (_pick_time), so two proposals' _start order does not guarantee their
    # picked-t order — a proposal starting later can still land an earlier t
    # than one starting earlier, if their jitter happens to land that way.
    # State must be threaded in the order events actually appear in the
    # output (sorted by t, since that's the only ordering any reader of
    # manifest.json — including this label's from/to chain — can see), not
    # in _start order, or the same-label chain can end up internally
    # consistent by _start but scrambled once sorted by t for export. Seeds
    # still derive from the _start-sorted index (idx) so this reordering
    # doesn't perturb the existing seed/reproducibility contract.
    timed = [
        (
            _pick_time(
                household_id, day, idx,
                float(prop.get("_start", 0.0)), float(prop.get("_end", prop.get("_start", 0.0))),
            ),
            idx,
            prop,
        )
        for idx, prop in enumerate(displacements)
    ]
    timed.sort(key=lambda item: (item[0], item[1]))

    changes: list[dict] = []
    n_rejected_unattended = 0
    n_dropped_noop = 0
    n_claim_divergence = 0

    for t, idx, prop in timed:
        cat      = prop["object_category"]
        occupant = prop.get("_occupant", "")
        location = prop.get("_location")
        to_slot  = resolve_slot(prop["target_anchor"], prop["target_relationship"], room=location)

        has_real_instance = bool(furniture_pool.get(cat))
        if has_real_instance:
            if cat not in real_assigned:
                real_assigned[cat] = sorted(furniture_pool[cat])[0]
            label = real_assigned[cat]
        else:
            key = (cat, occupant)
            if key not in volatile_assigned:
                volatile_counters[cat] = volatile_counters.get(cat, 0) + 1
                volatile_assigned[key] = f"{cat}_{volatile_counters[cat]}"
            label = volatile_assigned[key]

        from_slot = current_slot.get(label)  # None => label's genuine first event

        # Attendance (defense-in-depth — see module docstring). dest_room is
        # always derived from the *actual* resolved to_slot, never from
        # `location` directly — `location` is only a disambiguation hint fed
        # into resolve_slot (and, for in_region proposals, resolve_slot
        # doesn't consult it at all, since the anchor itself already is the
        # destination room). Trusting `location` here instead of re-deriving
        # from to_slot would make this check tautological: if generation's
        # room-scoping ever falls back to the whole-scene vocabulary (see
        # generate_displacements) and the model picks an anchor outside the
        # occupant's real room, to_slot reflects that real (wrong) room, and
        # dest_room must reflect it too, or this gate would rubber-stamp the
        # exact failure mode it exists to catch.
        dest_room = slot_room(to_slot)
        src_room  = slot_room(from_slot)
        present = set(occupants_in_room(traces, dest_room, t)) | set(occupants_in_room(traces, src_room, t))
        if occupant in present:
            mover = occupant
        elif present:
            mover = sorted(present)[0]  # deterministic tie-break, not set iteration order
        else:
            mover = None

        if mover is None:
            n_rejected_unattended += 1
            _logger.warning(
                "manifest: dropping unattributable displacement cat=%s %s->%s "
                "@t=%.2f (dest_room=%s src_room=%s; no occupant present)",
                cat, from_slot, to_slot, t, dest_room, src_room,
            )
            continue

        is_first_event  = label not in seen_labels
        seen_labels.add(label)
        change_type = "insert_new" if (is_first_event and not has_real_instance) else "move_existing"

        # No-op suppression. A label's true first event always has
        # from_slot=None (never pre-seeded for volatile labels, always a
        # real distinct value for real-instance-backed ones unless the
        # scene's own starting slot happens to equal the very first proposed
        # destination — a legitimate no-op, correctly dropped too), so this
        # only meaningfully filters a label's 2nd+ event.
        if from_slot is not None and from_slot == to_slot:
            n_dropped_noop += 1
            continue

        llm_claimed = prop.get("assumed_from")
        if llm_claimed and from_slot is not None and not _same_claim(llm_claimed, from_slot):
            n_claim_divergence += 1

        prior_moves = move_times.setdefault(label, [])
        confidence = score_confidence(
            cat, occupant_age_band.get(mover), slot_room(to_slot), prior_moves, t,
        )
        prior_moves.append(t)

        current_slot[label] = to_slot
        changes.append({
            "t":                t,
            "label":            label,
            "change_type":      change_type,
            "object_category":  cat,
            "from_semantic":    from_slot,
            "to_semantic":      to_slot,
            "mover":            mover,
            "llm_claimed_from": llm_claimed,
            "reason":           prop.get("reason", ""),
            "confidence":       confidence,
            "object_handle":    None,
        })

    changes.sort(key=lambda c: c["t"])
    if include_state_changes:
        changes.extend(build_state_changes(scene_id, generation_result, existing_changes=None))
        changes.sort(key=lambda c: c["t"])

    return {
        "scene_id":         scene_id,
        "resident_profile": household_type,
        "seed":             seed,
        "changes":          changes,
        "integrity_stats": {
            "rejected_unattended":  n_rejected_unattended,
            "dropped_noop":         n_dropped_noop,
            "llm_claim_divergence": n_claim_divergence,
        },
    }


def build_state_changes(
    scene_id: str,
    generation_result: dict,
    existing_changes: Optional[list[dict]] = None,
) -> list[dict]:
    """Deterministic state-change events for one day (M3: state-change
    dynamics) — the state-axis counterpart of build_manifest()'s location
    walk above, called from it for a fresh full-pipeline run, and also
    callable standalone (scripts/generate_state_stratum.py) against an
    already-generated day's traces with no LLM re-run needed.

    Proposals (generation/state_rules.py) carry only a *target* value, not
    a from/to pair — this function threads them against real tracked
    per-(label, variable) state in time order, emitting an event only when
    the target actually differs from the current value (chain-consistent
    and no-op-free by construction, mirroring the location walk's own
    no-op suppression above), and drops any proposal with no occupant
    present in the category's room at that instant (attendance,
    mirroring the location walk's mover gate above).

    existing_changes seeds the starting tracked state from any
    state_change events already present (e.g. this same day's manifest
    already has some — a repeated call must chain from them, not from
    scene-init again); None starts every stateful instance at its
    scene-init value (env/inventory.py's load_scene_state).
    """
    from ..env.deltas import STATE_VARIABLES
    from ..env.inventory import STATEFUL_FURNITURE
    from .grounding import ground_state_proposal_batch
    from .state_rules import propose_state_changes

    scene_state = load_scene_state(scene_id)
    stateful_instances = {
        inst.category: inst for inst in scene_state.instances.values()
        if inst.category in STATEFUL_FURNITURE
    }
    stateful_categories = set(stateful_instances)

    tracked: dict[tuple[str, str], str] = {
        (inst.instance_id, variable): value
        for inst in stateful_instances.values()
        for variable, value in inst.states.items()
    }
    for entry in sorted(existing_changes or [], key=lambda c: c["t"]):
        if entry.get("change_type") == "state_change":
            tracked[(entry["label"], entry["state_variable"])] = entry["to_state"]

    household_id = generation_result["household_id"]
    day = generation_result.get("day", 0)
    traces = generation_result.get("traces", [])

    all_proposals: list[dict] = []
    index = 0
    for trace in traces:
        occupant = trace.get("occupant_name", "")
        for activity in trace.get("activities", []):
            proposals = propose_state_changes(
                activity=activity["activity"], start=activity["start"], end=activity["end"],
                location=activity.get("location"), household_id=household_id, day=day, index=index,
            )
            for p in proposals:
                p["_occupant"] = occupant
            all_proposals.extend(proposals)
            index += 1

    accepted, _results = ground_state_proposal_batch(all_proposals, stateful_categories)
    accepted.sort(key=lambda p: p["_t"])

    changes: list[dict] = []
    for p in accepted:
        cat = p["object_category"]
        variable = p["state_variable"]
        label = stateful_instances[cat].instance_id
        key = (label, variable)
        current = tracked.get(key, STATE_VARIABLES[variable]["values"][0])
        target = p["target_state"]
        if target == current:
            continue

        t = p["_t"]
        room = slot_room(cat)  # bare category name -> CATEGORY_ROOM_HINT
        present = set(occupants_in_room(traces, room, t))
        occupant = p.get("_occupant", "")
        mover = occupant if occupant in present else (sorted(present)[0] if present else None)
        if mover is None:
            continue

        changes.append({
            "t": t, "label": label, "change_type": "state_change",
            "object_category": cat, "from_semantic": cat, "to_semantic": cat,
            "state_variable": variable, "from_state": current, "to_state": target,
            "mover": mover, "reason": p["reason"], "confidence": 1.0, "object_handle": None,
        })
        tracked[key] = target

    return changes
