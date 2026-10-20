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
    real starting instance in this scene, see env/inventory.py) resolve WHICH
    instance moves per event via generation/instances.pick_real_instance:
    the instance currently in the acting occupant's room, lowest index on
    ties, lowest-index fallback when the room has none. (Replaced the old
    one-instance-per-category-per-day rule, which produced a single chair
    endlessly teleported across the house while its siblings never moved.
    Chains stay consistent because each label's from_semantic comes from
    that label's OWN tracked slot regardless of which instance is picked;
    the failure mode the old rule guarded against was (category, occupant)
    KEYING, not per-event room lookup.)
  - Insert-once: insert_new fires at most once per label — its true first
    event, and only for volatile (Tier 3, no real starting instance) labels.
    Real-instance-backed labels are always move_existing, including their
    first event (the object already existed in the scene); a volatile label
    is insert_new exactly once, move_existing for every later event.
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
  - reason is the proposal's own leading `reason` field, verbatim — genuine
    pre-proposal reasoning (guided decoding emits it before the object/anchor
    fields, so it drives the choice). The prompt instructs any origin mention
    to come from the authoritative Current-object-state block, and
    from_semantic itself always comes from the chronological replay — never
    from model text. Each change also carries `activity`, the window this
    movement was part of. (assumed_from and the purpose/templated-reason
    split are both retired — see data_quality_backlog.md #1.)
  - There is no per-event confidence field. The old one (plausibility.
    score_confidence) was measured near-constant 1.0 on real generations —
    its capability/egress/ping-pong factors almost never fired — and was
    dropped rather than shipped as a constant that looks meaningful.
    Plausibility is now priced where it has signal: the realism judge
    (with move-history context) gates selection and clutter admission
    via selection.REALISM_FLOOR.

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

import dataclasses
import logging
from collections import Counter
from typing import Optional

from ..env.anchor_admission import anchor_capacity, is_reachable, load_anchor_admission_map
from ..env.inventory import load_scene_state
from .ownership import TIER3_CATEGORIES, tier3_instance_label
from .instances import pick_real_instance
from .schemas import PUT_AWAY_ANCHOR
from ..env.state import ObjectInstance
from ..rooms import UnresolvableSlotError, occupants_in_room, resolve_slot, slot_room
from ..topdown_map import instance_room_positions
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


def build_manifest(
    scene_id: str,
    household_type: str,
    day: int,
    generation_result: dict,
    seed: int = 1,
    include_state_changes: bool = False,
    reachability_filtering: bool = False,
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

    reachability_filtering (default False, Reachability Removal Phase 1):
    gates the two is_reachable(...) hard-gate rejections below (clutter and
    displacement proposals targeting a navmesh-unreachable anchor). Off by
    default — with interior doors closed and out of scope, navmesh
    reachability is wrong for most indoor rooms and was the confirmed
    driver of outdoor objects being selected for indoor instructions. A
    flag rather than a deletion so this can be restored once door handling
    lands. Does NOT touch the capacity gate below (anchor_capacity/
    slot_occupancy) — capacity is a separate, still-live admission
    mechanism keyed off receptacle curation, not navmesh reachability, and
    survives this phase unconditionally.
    """
    household_id = generation_result["household_id"]
    persona = generation_result.get("persona", {})
    traces  = generation_result.get("traces", [])
    occupant_age_band = {
        o["name"]: o.get("age_band") for o in persona.get("occupants", [])
    }

    # load_scene_state is @lru_cache'd (env/inventory.py) — a real,
    # pre-existing bug, not something new: the clutter loop just below
    # mutates scene_state.instances in place, which was silently
    # corrupting that SAME cached object for every OTHER caller in this
    # process for the rest of its lifetime (any later
    # generate_for_scene/room_inventory_from_scene_state call for this
    # scene_id would see this run's clutter instances leak in as if they
    # were real starting furniture). Confirmed directly: two consecutive
    # build_manifest calls for the same scene_id, verified via
    # `load_scene_state(id) is load_scene_state(id)` returning True.
    # Copying instances here (not the ObjectInstance values themselves,
    # which this function never mutates) is the fix — the cache stays a
    # read-only source of truth, exactly what @lru_cache is supposed to
    # provide.
    _cached_scene_state = load_scene_state(scene_id)
    scene_state = dataclasses.replace(_cached_scene_state, instances=dict(_cached_scene_state.instances))

    # Realized World Phase round 2: the SAME real per-scene, per-room
    # furniture census resolve_slot()'s census-grounded fallback checks
    # against — computed once per manifest build (one scene), not once per
    # displacement, since it's identical for every call below.
    room_instance_categories = {
        room: set(cats) for room, cats in instance_room_positions(scene_id).items()
    }

    # Anchor Admission round (Version B): the hard, authoritative backstop
    # — generation/anchor_reachability_filter.py's pruning is soft (shrinks
    # what the LLM/grounder ever see), this is what actually rejects
    # anything that slips through anyway (a stale/missing cache at
    # generation time, the documented empty-room-list fallback in
    # generate_displacements, ...). None (no cache) makes every gate below
    # a no-op — today's exact behavior — but is never silent. Reachability
    # Removal Phase 1: the two is_reachable(...) rejections below (clutter
    # and displacement) are now additionally gated on
    # reachability_filtering (default False) — the capacity gate further
    # down (anchor_capacity/slot_occupancy) is a separate mechanism and is
    # NOT gated; it stays live regardless of this flag.
    admission_map = load_anchor_admission_map(scene_id)
    if admission_map is None:
        _logger.warning("manifest: building scene=%s day=%s without an anchor admission map — "
                         "reachability/capacity gates disabled for this manifest", scene_id, day)

    # Tier 2b: clutter generation/clutter/ invented a starting slot for.
    # Merged into the same pool as Tier 2a so the real-instance-backed vs.
    # volatile decision below doesn't need to know which sub-tier a category
    # is — it just checks whether a real starting instance exists at all.
    # Clutter has no occupant/activity context (it's the day's t=0 starting
    # state, not something anyone "did"), so its slot resolution has no room
    # to disambiguate with — same room-agnostic resolution as before.
    clutter_counters: dict[str, int] = {}
    n_clutter_rejected_unreachable = 0
    for placement in generation_result.get("clutter", []):
        cat = placement["object_category"]
        slot = resolve_slot(placement["target_anchor"], placement["target_relationship"],
                             room_instance_categories=room_instance_categories)
        if reachability_filtering and is_reachable(admission_map, slot) is False:
            # No capacity gate here (by design, not an oversight): clutter
            # is the day's t=0 starting state, not a "reject and retry"
            # event — its contribution to occupancy is captured directly
            # by seeding slot_occupancy from current_slot below, once this
            # instance is actually added.
            n_clutter_rejected_unreachable += 1
            _logger.warning("manifest: rejecting clutter placement cat=%s at unreachable anchor %s", cat, slot)
            continue
        clutter_counters[cat] = clutter_counters.get(cat, 0) + 1
        iid = f"{cat}_{clutter_counters[cat]}"
        scene_state.instances[iid] = ObjectInstance(
            instance_id=iid, category=cat, current_semantic=slot,
        )

    furniture_pool: dict[str, list[str]] = {}
    for iid, inst in scene_state.instances.items():
        furniture_pool.setdefault(inst.category, []).append(iid)

    volatile_assigned: dict[tuple[str, str], str] = {}
    volatile_counters: dict[str, int] = {}
    seen_labels: set[str] = set()
    current_slot: dict[str, str] = {
        iid: inst.current_semantic for iid, inst in scene_state.instances.items()
    }
    # Seeded from the real starting state (which already includes accepted
    # Tier 2b clutter, added to scene_state.instances above) so a slot that
    # already starts crowded counts toward its own capacity immediately —
    # not only once a displacement additionally lands there.
    slot_occupancy: dict[str, int] = dict(Counter(current_slot.values()))

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
    n_dropped_bad_time = 0
    n_rejected_unbacked_anchor = 0
    n_rejected_unreachable_anchor = 0
    n_rejected_over_capacity = 0
    n_dropped_despawn_notout = 0
    n_rejected_no_seat_in_room = 0
    n_spawned_from_storage = 0

    for t, idx, prop in timed:
        cat      = prop["object_category"]
        occupant = prop.get("_occupant", "")
        location = prop.get("_location")
        # Phase 3 despawn/put-away: the occupant puts their own Tier-3 item
        # away at night. There's no destination anchor to resolve — the item
        # leaves the tracked world ("away"). We don't model where it goes, only
        # that it's no longer placed anywhere. Emitted as change_type="remove",
        # the established "object leaves the world" contract every downstream
        # consumer already implements (env/replay.py pops the instance,
        # env/world_graph_adapter.py no-ops, build_realized_day knows it) —
        # NOT a new synonym they'd all have to special-case. Skip resolve_slot
        # and the anchor-admission gates: they're about a real target surface a
        # removal doesn't have.
        is_despawn = bool(prop.get("_despawn")) or prop.get("target_anchor") == PUT_AWAY_ANCHOR
        if is_despawn:
            to_slot = "away"
        else:
          try:
            to_slot = resolve_slot(prop["target_anchor"], prop["target_relationship"], room=location,
                                    room_instance_categories=room_instance_categories)
          except UnresolvableSlotError as exc:
            # Realized World Phase round 2's admission rule enforced at the
            # source: the LLM's (category, room) pick had no real backing
            # instance in that room — reject here rather than let
            # resolve_slot synthesize an unbacked slot string downstream
            # code would trust. Counted, not silently dropped (see
            # integrity_stats below) — this is a generation-quality signal,
            # not a routine, expected outcome.
            n_rejected_unbacked_anchor += 1
            _logger.warning("manifest: rejecting proposal with unbacked anchor cat=%s room=%s: %s", cat, location, exc)
            continue

        # Anchor Admission round (Version B): the hard backstop —
        # generation/anchor_reachability_filter.py's soft, upstream
        # pruning should already keep most of these out, but a proposal
        # can still reach here (stale/missing cache when the vocabulary
        # was built, the documented empty-room-list fallback, ...).
        # is_reachable(...) is None (unknown, e.g. no cache at all) is
        # NOT a rejection — only a confirmed False is. Gated on
        # reachability_filtering (default False, Reachability Removal
        # Phase 1) — see build_manifest's own docstring.
        if reachability_filtering and is_reachable(admission_map, to_slot) is False:
            n_rejected_unreachable_anchor += 1
            _logger.warning("manifest: rejecting proposal targeting known-unreachable anchor cat=%s slot=%s",
                             cat, to_slot)
            continue

        has_real_instance = bool(furniture_pool.get(cat))
        spawned = False
        if has_real_instance:
            # Instance resolution per event, not per day: the occupant uses
            # the instance already in THEIR room. For floor-bound seating
            # (chair/stool) that is a HARD requirement — scenes are seat-poor
            # (992: two chairs, both on the patio), and the lowest-index
            # fallback teleported one chair across the whole house, so a
            # seatless room means NO seat move (you sit on built-in seating).
            # The pipeline's vocabulary gate should prevent these proposals
            # existing at all; this is the replay-level backstop. Non-seating
            # categories (books, bowls) keep the lowest-index fallback —
            # carrying those between rooms is ordinary behavior.
            from ..env.inventory import ABUNDANT_STORAGE_CATEGORIES, TIER2_CLUTTER_CATALOG
            from ..env.inventory import FLOOR_BOUND_CATEGORIES
            from ..rooms import rooms_match
            from .instances import instance_room
            if cat in FLOOR_BOUND_CATEGORIES:
                in_room = [iid for iid in sorted(furniture_pool[cat])
                           if location
                           and (r := instance_room(current_slot.get(iid))) is not None
                           and rooms_match(r, location)]
                if not in_room:
                    n_rejected_no_seat_in_room += 1
                    _logger.warning("manifest: rejecting %s move — no %s currently in %s",
                                     cat, cat, location)
                    continue
            # Instance-explicit proposals (seat instances the proposer picked
            # by id — see generate_displacements' seat vocabulary): honor the
            # model's own choice when it names a real instance; this is what
            # lets two occupants use DIFFERENT chairs instead of both
            # resolving onto the same lowest-index one. Floor-bound safety
            # still applies: an explicit seat not currently in the acting
            # room falls back to the picker (which the in_room gate above
            # already vetted) rather than teleporting across the house.
            explicit = prop.get("_instance")
            if explicit and explicit in furniture_pool[cat] and not (
                cat in FLOOR_BOUND_CATEGORIES and location and (
                    (r := instance_room(current_slot.get(explicit))) is None
                    or not rooms_match(r, location))):
                label = explicit
            else:
                label = pick_real_instance(cat, furniture_pool[cat], current_slot, location)
            # Abundant-storage spawn: the resolved instance is already AT the
            # proposed destination (previously a dropped no-op). For abundant
            # categories that collision means "take a fresh one from storage"
            # — a home holds more bowls/cups/books than the few set out at
            # t=0, and nobody reuses the used one on the table. Allocate the
            # next instance id (insert_new, from storage) while total
            # instances stay within the clutter catalog cap; at cap, fall
            # through to the ordinary no-op drop below.
            if (cat in ABUNDANT_STORAGE_CATEGORIES
                    and not is_despawn
                    and current_slot.get(label) is not None
                    and current_slot.get(label) == to_slot
                    and len(furniture_pool[cat]) < TIER2_CLUTTER_CATALOG.get(cat, 0)):
                clutter_counters[cat] = clutter_counters.get(cat, 0) + 1
                label = f"{cat}_{clutter_counters[cat]}"
                furniture_pool[cat].append(label)
                spawned = True
                n_spawned_from_storage += 1
        else:
            key = (cat, occupant)
            if key not in volatile_assigned:
                if cat in TIER3_CATEGORIES:
                    # Owner-named Tier-3 instance (michael_laptop) so per-owner
                    # move counts are coherent — each occupant carries their own.
                    volatile_assigned[key] = tier3_instance_label(occupant, cat)
                else:
                    volatile_counters[cat] = volatile_counters.get(cat, 0) + 1
                    volatile_assigned[key] = f"{cat}_{volatile_counters[cat]}"
            label = volatile_assigned[key]

        from_slot = current_slot.get(label)  # None => label's genuine first event

        if is_despawn:
            # Nothing to put away in this chronological replay: the placement
            # that would have set it out was itself rejected/dropped upstream
            # (over-capacity, unattended, unbacked anchor), so RunningState and
            # the manifest replay diverged. Drop rather than emit a despawn
            # from nowhere — keeps the change log self-consistent.
            if from_slot is None or from_slot == "away":
                n_dropped_despawn_notout += 1
                continue
            # The occupant carries their own item, so they're the mover by
            # definition — no room-attendance check (the item is with them,
            # not sitting in from_slot's room waiting to be picked up).
            mover = occupant
        else:
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
        if is_despawn:
            change_type = "remove"
        else:
            # `spawned` — an abundant-storage instance allocated above enters
            # the world here, from storage, exactly like a volatile label's
            # first event (from_slot is None for both).
            change_type = ("insert_new" if (spawned or (is_first_event and not has_real_instance))
                           else "move_existing")

        # No-op suppression. A label's true first event always has
        # from_slot=None (never pre-seeded for volatile labels, always a
        # real distinct value for real-instance-backed ones unless the
        # scene's own starting slot happens to equal the very first proposed
        # destination — a legitimate no-op, correctly dropped too), so this
        # only meaningfully filters a label's 2nd+ event.
        if from_slot is not None and from_slot == to_slot:
            n_dropped_noop += 1
            continue

        # Capacity gate, after no-op suppression (a no-op is not a new
        # arrival, so it must not consume budget) and before this event
        # is actually committed. anchor_capacity(...) is None both for
        # "no cache"/"no data" and for an anchor with no per-object
        # budget at all (a region anchor, or an instance anchor with no
        # usable receptacle) — either way, None means no gate applies.
        cap = anchor_capacity(admission_map, to_slot)
        if cap is not None and slot_occupancy.get(to_slot, 0) >= cap:
            n_rejected_over_capacity += 1
            _logger.warning("manifest: rejecting proposal — %s at capacity (%d/%d), cat=%s",
                             to_slot, slot_occupancy.get(to_slot, 0), cap, cat)
            continue
        if cap is not None:
            slot_occupancy[to_slot] = slot_occupancy.get(to_slot, 0) + 1
        if from_slot is not None and from_slot in slot_occupancy:
            # Frees the budget at the label's PREVIOUS slot now that it's
            # moving away — required for correctness across a full day's
            # chained moves, or this gate only ever gets stricter as the
            # day progresses regardless of what actually left.
            slot_occupancy[from_slot] = max(0, slot_occupancy[from_slot] - 1)

        # Time-sanity backstop behind the schema bounds: an event outside
        # [0, 30) hours (past-midnight sleep wrap allowed) is a unit error
        # (minutes-as-hours), and replay would place it on a phantom day.
        if not (0.0 <= t < 30.0):
            n_dropped_bad_time += 1
            _logger.warning("manifest: dropping event with out-of-range t=%.3f (label=%s)", t, label)
            continue
        current_slot[label] = to_slot
        changes.append({
            "t":                t,
            "label":            label,
            "change_type":      change_type,
            "object_category":  cat,
            "from_semantic":    from_slot,
            "to_semantic":      to_slot,
            # Floor-Bound Realization round: the proposal's own spatial
            # relation, carried through so the builder can realize
            # near/next_to as a floor placement beside the anchor instance
            # instead of on its surface (see env/deltas.py's Change).
            "target_relationship": prop.get("target_relationship"),
            "mover":            mover,
            # The proposal's leading `reason` (pre-proposal reasoning, guided
            # decoding emits it before the object/anchor fields) carried
            # verbatim — the event's trace. `activity` names the window this
            # movement was part of, so a manifest row is interpretable on its
            # own. (The earlier purpose/templated-reason split is retired.)
            "activity":         prop.get("_activity"),
            "reason":           prop.get("reason", ""),
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
        # Generating model (comparison label; "" on old generation_results).
        "model":            generation_result.get("model", ""),
        # {owner label -> render asset uid}: the LLM's in-character pick for
        # each owned Tier-3 item (generation/asset_binding.py). Carried here
        # so build_realized_day binds the same asset the generation chose;
        # {} on old generation_results.
        "asset_bindings":   generation_result.get("asset_bindings", {}),
        # Per-occupant day context (weekday/weekend/flex + scenario text) that
        # shaped each activity trace — surfaced here so the day's character is
        # visible at the manifest level, not buried in generation_result. Note
        # each occupant draws its own scenario today (see data_quality_backlog:
        # household day-type coherence).
        "day_context":      {
            tr.get("occupant_name", ""): {
                "day_type":    tr.get("day_type"),
                "day_scenario": tr.get("day_context"),
            }
            for tr in traces
        },
        "changes":          changes,
        "integrity_stats": {
            "rejected_unattended":          n_rejected_unattended,
            "dropped_noop":                 n_dropped_noop,
            "dropped_bad_time":             n_dropped_bad_time,
            "spawned_from_storage":         n_spawned_from_storage,
            "rejected_unbacked_anchor":     n_rejected_unbacked_anchor,
            "rejected_unreachable_anchor":  n_rejected_unreachable_anchor,
            "rejected_over_capacity":       n_rejected_over_capacity,
            "dropped_despawn_notout":       n_dropped_despawn_notout,
            "rejected_no_seat_in_room":     n_rejected_no_seat_in_room,
            "clutter_rejected_unreachable": n_clutter_rejected_unreachable,
            "admission_map_used":           admission_map is not None,
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
            "mover": mover, "reason": p["reason"], "object_handle": None,
        })
        tracked[key] = target

    return changes
