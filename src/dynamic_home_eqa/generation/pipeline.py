"""
Top-level generation pipeline.

Runs all three stages in order (persona → activity trace → displacement),
optionally runs multi-agent cross-verification, then grounds each displacement
proposal through PARTNR's simulation.

Two modes:
  standalone  — semantic grounding only (no Habitat-sim).
                Fast; use for prompt iteration and model selection baseline.
  sim         — full PARTNR simulation grounding.
                Required for dataset acceptance. Measures grounding survival rate.

The grounding survival rate is the empirical model-selection metric.
Measure it on a small scene sample (10–20 scenes) before committing to
a model or prompt design.

Displacement pipeline, per activity occurrence:
    1. Propose (LLM, over-generates by design — stages.generate_displacements).
    2. Ground (deterministic; physically un-placeable candidates rejected).
    3. Score realism (separate LLM judge call; behavioral plausibility, not
       placeability — stages.score_realism_batch).
    4. Select (stochastic; Poisson count around a per-activity mean, sampled
       weighted by realism score — selection.select_for_activity).
Grounding runs batched across the whole scene for efficiency, then results
are regrouped by activity for realism scoring and selection, since the judge
should only see one activity's candidates at a time.

Output format (per scene):
    {
      "household_id":   str,
      "scene_id":       str,
      "profile":        str,
      "day":            int,
      "clutter":        [dict, ...],     # Tier 2b starting placements (empty on world_graph path)
      "persona":        dict,
      "traces":         [dict, ...],     # one per occupant
      "displacements":  [dict, ...],     # final selected subset
      "raw_proposals":  int,             # count before grounding
      "grounded_proposals": int,         # count after grounding, before selection
      "mean_realism_score": float,       # mean realism of *selected* displacements
      "grounding_stats": {               # rejection-cause instrumentation
          "total": int,
          "accepted": int,
          "survival_rate": float,
          "infra_rejection_rate": float, # no_anchor — infra gap, not model error
          "model_rejection_rate": float, # no_object + no_placement — real signal
          "rejected_categories": {str: int},
          ...
      },
      "conflict_report": dict,           # empty for single-occupant
    }
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter, defaultdict
from typing import Optional, TYPE_CHECKING

from .anchor_reachability_filter import (
    prune_room_inventory_by_reachability,
    prune_scene_wide_by_reachability,
)
from .cache import ResponseCache, make_seed
from .clutter import generate_clutter
from .grounding import (
    GroundingStats,
    ground_displacement_batch,
    ground_displacement_batch_semantic,
)
from .inventory import (
    inventory_from_scene_state,
    room_inventory_from_scene_state,
    anchor_inventory_from_scene_state,
    inventory_from_world_graph,
    room_inventory_from_world_graph,
)
from ..env.anchor_admission import load_anchor_admission_map
from ..env.anchor_census import load_anchor_census
from ..topdown_map import instance_room_positions
from .schemas import ABSTAIN_ANCHOR
from .exports import to_replay_format
from .llm_client import DEFAULT_MODEL, DEFAULT_TEMPERATURE
from .manifest import build_manifest
from .persona import generate_persona
from .regions import load_scene_regions
from .schemas import filter_displacement_proposals
from .selection import REALISM_FLOOR, select_for_activity
from .stages import (
    generate_activity_trace,
    generate_displacements,
    score_realism_batch,
)
from .verification import needs_verification, run_verification_pass

if TYPE_CHECKING:
    from habitat_llm.world_model.world_graph import WorldGraph


# ---------------------------------------------------------------------------
# Per-scene generation
# ---------------------------------------------------------------------------

def _preflight_replay_gates(candidates, state, occupant, room_instance_categories,
                            admission_map, slot_occupancy):
    """Mirror build_manifest's replay gates (unbacked anchor, no-op-with-
    spawn-allowance, capacity) against the running state, BEFORE the Poisson
    selection draw — so the draw operates on the pool of moves that will
    actually materialize, and lambda is a clean scene-activity knob whose
    shape no downstream gate silently eats into.

    Survivors get `_resolved_slot` (the same resolved slot string
    build_manifest will record — RunningState.apply stores it so the no-op
    comparison stays manifest-grade across windows); excluded candidates get
    `_gate_excluded` = reason and ride into choices.jsonl unselected.

    Deliberately NOT preflighted: attendance (event t is jittered inside the
    manifest and proposals are already room-scoped to the acting occupant,
    so it essentially never fires) and same-window capacity races (two
    chosen candidates filling one slot in the same draw). build_manifest
    remains the authority; a rare late drop there costs one event, not the
    Poisson shape.
    """
    from ..env.anchor_admission import anchor_capacity
    from ..env.inventory import ABUNDANT_STORAGE_CATEGORIES, TIER2_CLUTTER_CATALOG
    from ..rooms import UnresolvableSlotError, resolve_slot
    from .ownership import TIER3_CATEGORIES, tier3_instance_label

    gated: list[dict] = []
    excluded: Counter = Counter()
    for c in candidates:
        if c.get("_despawn"):
            # A put-away is always feasible — except concealing a Tier-2
            # instance that is ALREADY stored away (slot None): the manifest
            # would drop that as despawn-of-nothing, so exclude it here and
            # let the Poisson draw pick something real instead.
            cat0 = c.get("object_category", "")
            if c.get("_concealed_in") and cat0 not in TIER3_CATEGORIES:
                explicit = c.get("_instance")
                lbl0 = explicit if (explicit and explicit in state.tier2_slots) \
                    else state._tier2_label(cat0, c.get("_location"))
                if lbl0 is not None and state.tier2_slots.get(lbl0) is None:
                    c["_gate_excluded"] = "already_stored"
                    excluded["already_stored"] += 1
                    continue
            gated.append(c)
            continue
        cat = c.get("object_category", "")
        loc = c.get("_location")
        try:
            to_slot = resolve_slot(c["target_anchor"], c["target_relationship"], room=loc,
                                   room_instance_categories=room_instance_categories)
        except UnresolvableSlotError:
            c["_gate_excluded"] = "unbacked_anchor"
            excluded["unbacked_anchor"] += 1
            continue
        # Current slot of the instance this proposal would actually move —
        # same resolution order as build_manifest (explicit _instance first,
        # then the room-aware picker).
        if cat in TIER3_CATEGORIES:
            cur = state.tier3.get(tier3_instance_label(c.get("_occupant", occupant), cat))
        else:
            explicit = c.get("_instance")
            lbl = explicit if (explicit and explicit in state.tier2_slots) \
                else state._tier2_label(cat, loc)
            cur = state.tier2_slots.get(lbl) if lbl else state.moved_today.get(cat)
        if cur is not None and cur == to_slot:
            can_spawn = (cat in ABUNDANT_STORAGE_CATEGORIES
                         and len(state.tier2_pool.get(cat, []))
                         < TIER2_CLUTTER_CATALOG.get(cat, 0))
            if not can_spawn:
                c["_gate_excluded"] = "noop"
                excluded["noop"] += 1
                continue
        cap = anchor_capacity(admission_map, to_slot)
        if cap is not None and slot_occupancy.get(to_slot, 0) >= cap:
            c["_gate_excluded"] = "capacity"
            excluded["capacity"] += 1
            continue
        c["_resolved_slot"] = to_slot
        gated.append(c)
    return gated, excluded


def generate_for_scene(
    scene_id: str,
    household_type: str,
    day: int = 0,
    variant: int = 0,
    demographic_notes: str = "",
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    cache_dir: Optional[str] = None,
    force: bool = False,
    world_graph: Optional["WorldGraph"] = None,
    env=None,
    agent=None,
    grasp_mgr=None,
    use_semantic_grounding: bool = True,
    reachability_filtering: bool = False,
    judge_thinking: bool = False,
    judge_style: str = "asis",
    enrich_context: bool = False,
    exemplar_block=None,
    activity_scale: float = 1.0,
    judge_retry: bool = False,
) -> dict:
    """Run the full generation pipeline for one scene.

    judge_thinking/judge_style (LLM Option Evaluation round, Arm 1):
    passed straight to score_realism_batch — thinking-mode judge and/or
    the strict scoring prompt. Proposer and every other stage are
    unaffected (guided decoding intact).

    Args:
        scene_id:        HSSD scene identifier (e.g. "102343992").
        household_type:  Profile name (e.g. "work_from_home_adult").
        day:             Day index (seeds vary per day for trace diversity).
        variant:         Which persona to generate for this exact
                         (scene_id, household_type) — 0, 1, 2, ... give
                         different households (different occupants, ages,
                         habits, tidiness), not different days of the same
                         household. This is the "k examples" knob: call with
                         variant=0..k-1 to get k distinct families for the
                         same house. Folded into household_id (below) rather
                         than threaded as a separate seed component through
                         every stage — every stage's seed already derives
                         from household_id, so changing it once here cascades
                         to persona, activity, displacement, realism, and
                         conflict-verification seeds together. That matters:
                         a variant that only perturbed the persona seed could
                         still produce near-identical activity traces if two
                         personas happened to land on similar text; cascading
                         through household_id guarantees the activity/
                         displacement/realism seeds differ too, independent
                         of how much the persona text itself varies.
        demographic_notes: Optional persona constraints (passed to persona stage).
        model:           vLLM model string.
        temperature:     Sampling temperature (applies to all three stages).
        cache_dir:       Directory for response caching. None = no caching.
        force:           Ignore cached responses and regenerate.
        world_graph:     Live PARTNR WorldGraph for sim-based grounding.
                         None = use standalone CSV-based inventory.
        env, agent, grasp_mgr: PARTNR simulation handles for placement sampling.
                         Required for sim-based grounding; None = semantic only.
        use_semantic_grounding: If True and sim handles are unavailable, fall
                         back to semantic plausibility checking (no physics).
        reachability_filtering: Reachability Removal Phase 1 (default
                         False). When False, prune_room_inventory_by_
                         reachability/prune_scene_wide_by_reachability are
                         bypassed entirely — the LLM/grounder vocabulary is
                         the raw census, unfiltered by navmesh reachability.
                         With interior doors closed and out of scope,
                         navmesh reachability is wrong for most indoor
                         rooms and was the confirmed driver of outdoor
                         objects being selected for indoor instructions. A
                         flag rather than a deletion so this can be
                         restored once door handling lands. Threaded to
                         build_manifest's own same-named flag by run_batch.

    Returns:
        Per-scene output dict (see module docstring).
    """
    household_id = f"{scene_id}_{household_type}"
    if variant:
        household_id += f"_v{variant}"
    cache = ResponseCache(cache_dir) if cache_dir else None

    # ── Inventory ─────────────────────────────────────────────────────────────
    room_instance_categories: dict = {}
    admission_map: Optional[dict] = None
    anchor_census: Optional[dict] = None
    if world_graph is not None:
        inventory        = inventory_from_world_graph(world_graph)
        room_inventory   = room_inventory_from_world_graph(world_graph)
        anchor_inventory = None  # no equivalent census wired for the live-WorldGraph path yet
    else:
        inventory        = inventory_from_scene_state(scene_id)
        room_inventory   = room_inventory_from_scene_state(scene_id)
        anchor_inventory = anchor_inventory_from_scene_state(scene_id)
        # Anchor Admission round (Version B): the SAME conversion
        # manifest.py's build_manifest already makes, so resolve_slot's
        # census-grounded fallback probe (inside the prune_* functions
        # below) stays consistent with what build_manifest itself will
        # later resolve for these exact proposals.
        room_instance_categories = {
            room: set(cats) for room, cats in instance_room_positions(scene_id).items()
        }
        admission_map = load_anchor_admission_map(scene_id)  # None -> every prune_* call below is a no-op
        # Realizable-Anchor Vocabulary round (Part A): the room-qualified,
        # receptacle-backed instance census that IS the target_anchor
        # vocabulary now (see generate_displacements/generate_clutter).
        # None (not precomputed for this scene) falls back to the legacy
        # bare-category vocabulary, with load_anchor_census's own WARNING.
        anchor_census = load_anchor_census(scene_id)

    # Soft, generation-time-only exclusion of navmesh-unreachable anchors
    # (see generation/anchor_reachability_filter.py's own docstring for
    # why this is deliberately redundant with manifest.py's hard gate,
    # not a replacement for it).
    #
    # Reachability Removal Phase 1 (default reachability_filtering=False):
    # bypassed entirely rather than deleted, so restoring this once door
    # handling lands is a one-flag flip, not a re-implementation. With
    # interior doors closed and out of scope, navmesh reachability is
    # wrong for most indoor rooms and was the confirmed driver of outdoor
    # objects being selected for indoor instructions.
    #
    # KNOWN TENSION, deliberately left for the door-handling phase to
    # resolve, not solved here: anchor_inventory_reachable now flows into
    # BOTH generate_displacements and grounding unchanged (Census
    # Unification, below) — under this phase's default (flag off) the two
    # are byte-identical to the raw census, so this is a genuine no-op
    # today. But if reachability_filtering is flipped back on without
    # revisiting this, room_inventory_reachable (pruned PER-ROOM) and
    # anchor_inventory_reachable (pruned SCENE-WIDE, a coarser room=None
    # probe) would both flow into rooms.anchors_in_room's
    # `cats &= set(anchor_inventory.keys())` intersection — a category
    # genuinely reachable via THIS room's own instance could still get
    # dropped scene-wide (a different, unreachable instance elsewhere
    # resolved first), silently flattening the room-scoped precision
    # anchor_inventory was previously kept unpruned to protect. Unifying
    # the census (this phase's explicit requirement) and preserving that
    # room-scoped precision (a pre-existing, still-valid concern) are in
    # real tension only once reachability_filtering=True again — not
    # something Phase 1 needs to resolve, but flagged here so it isn't
    # silently reintroduced later.
    if reachability_filtering:
        room_inventory_reachable = prune_room_inventory_by_reachability(
            room_inventory, room_instance_categories, admission_map
        )
        anchor_inventory_reachable = prune_scene_wide_by_reachability(
            anchor_inventory, room_instance_categories, admission_map
        )
    else:
        room_inventory_reachable = room_inventory
        anchor_inventory_reachable = anchor_inventory

    # ── Stage 0: Tier 2b clutter placement (once per house + household) ───────
    # Runs before persona/activities/displacements — a clutter object's home is
    # a property of the house and who lives there, not of any day's schedule.
    # Skipped on the live-WorldGraph path: no real anchor census is wired for
    # it yet (anchor_inventory is None there), so there's nothing to ground
    # clutter placements against.
    clutter: list[dict] = []
    n_abstained_clutter = 0
    n_clutter_below_floor = 0
    n_clutter_over_cap = 0
    clutter_rejected: list[dict] = []
    if anchor_inventory is not None:
        clutter = generate_clutter(
            household_type=household_type,
            household_id=household_id,
            anchor_inventory=anchor_inventory_reachable,
            room_inventory=room_inventory_reachable,
            anchor_census=anchor_census,
            model=model,
            temperature=temperature,
            cache=cache,
            force=force,
        )
        # Part A: drop abstained placements ("none" anchor — the model's
        # explicit "nothing here fits") before they enter the scene's
        # starting state; counted, never silent.
        n_abstained_clutter = sum(1 for p in clutter if p.get("target_anchor") == ABSTAIN_ANCHOR)
        clutter = [p for p in clutter if p.get("target_anchor") != ABSTAIN_ANCHOR]

        # Judge + floor + catalog cap (clutter admission). Clutter previously
        # entered the world unjudged, so census-starved scenes produced absurd
        # start states (measured: 18 bowls in one home, 6 of them on a bed,
        # when the census offered no kitchen counter — see
        # data_quality_backlog). Reuse the displacement judge: each placement
        # is priced as a persistent start-of-day home for that object, gated
        # by the same REALISM_FLOOR selection uses, then capped per category
        # to TIER2_CLUTTER_CATALOG's intended quantities (highest-scored
        # kept). Judged with day pinned to 0 and no occupant context: clutter
        # runs before persona exists and is day-invariant by design — a
        # day-dependent judge seed would fracture the same house's start
        # state across days.
        if clutter:
            from ..env.inventory import TIER2_CLUTTER_CATALOG
            from .selection import REALISM_FLOOR
            c_scores, c_meta = score_realism_batch(
                candidates=clutter,
                activity="static clutter placement (each object's persistent, start-of-day home in this house)",
                occupant_name="the household",
                persona={},
                household_id=household_id,
                day=0, start=0.0, end=0.0, occupant_index=0,
                model=model, temperature=temperature, cache=cache, force=force,
                judge_thinking=judge_thinking, judge_style=judge_style,
                include_context=False, exemplar_block=None,
            )
            c_reasons = c_meta.get("reasons") or [""] * len(clutter)
            for p, s, jr in zip(clutter, c_scores, c_reasons):
                p["_judge_score"] = s
                p["_judge_stage_tag"] = c_meta["stage_tag"]
                if jr:
                    p["_judge_reason"] = jr
            from .clutter.generate import admit_clutter
            clutter, clutter_rejected, n_clutter_below_floor, n_clutter_over_cap = admit_clutter(
                clutter, c_scores, REALISM_FLOOR, TIER2_CLUTTER_CATALOG,
            )

        clutter_counts: dict[str, int] = {}
        for placement in clutter:
            cat = placement["object_category"]
            clutter_counts[cat] = clutter_counts.get(cat, 0) + 1
        for cat, n in clutter_counts.items():
            inventory[cat] = inventory.get(cat, 0) + n

    # ── Stage 1: Persona ──────────────────────────────────────────────────────
    # Deliberately no day= here — persona is day-invariant by design (see
    # generate_persona's docstring); passing day through would let two calls
    # for the same household on different days silently disagree.
    persona = generate_persona(
        household_type=household_type,
        household_id=household_id,
        demographic_notes=demographic_notes,
        model=model,
        temperature=temperature,
        cache=cache,
        force=force,
    )

    # ── Stage 1.5: routine charter (once per HOUSEHOLD — cached across days)
    # and today's calendar event (seeded, sparse; None = ordinary day). The
    # charter pins each member's stable weekly pattern so day plans render
    # rather than re-imagine the household; the calendar makes variety an
    # explicit sampled quantity instead of a prompt exhortation.
    from .stages import generate_routine_charter
    from .event_calendar import event_for_day
    charter = generate_routine_charter(persona, household_id, model=model,
                                       cache=cache, force=force)
    event = event_for_day(household_id, day, persona)
    event_note = event["note"] if event else None

    # ── Stage 2: Activity traces (one per occupant) ───────────────────────────
    traces: list[dict] = []
    for occ_idx, occupant in enumerate(persona.get("occupants", [])):
        occ_name = occupant["name"]
        trace = generate_activity_trace(
            persona=persona,
            occupant_name=occ_name,
            occupant_index=occ_idx,
            household_id=household_id,
            day=day,
            model=model,
            temperature=temperature,
            cache=cache,
            force=force,
            charter=charter,
            event_note=event_note,
        )
        # occupant_name is free-text in ACTIVITY_SCHEMA (not enum-constrained
        # to the real persona name — nothing stops the model from echoing it
        # back slightly wrong). Every downstream identity join (attendance
        # checks in rooms.py/trace_validate.py, conflict verification's
        # trace_text) must use the same name the rest of the pipeline already
        # tracks authoritatively, not trust the model's self-report — so this
        # is stamped from occ_name unconditionally, the same principle as
        # from_semantic never being taken from LLM output in manifest.py.
        trace["occupant_name"] = occ_name
        traces.append(trace)

    # ── Multi-agent verification (multi-occupant households only) ─────────────
    conflict_report: dict = {"conflicts": []}
    if needs_verification(persona):
        traces, conflict_report = run_verification_pass(
            traces=traces,
            persona=persona,
            inventory=inventory,
            household_id=household_id,
            day=day,
            model=model,
            temperature=temperature,
            cache=cache,
            force=force,
            charter=charter,
            event_note=event_note,
        )

    # ── Stage 3: displacement + grounding + judge + select, per chronological
    #    WINDOW (Phase 3 — sequential state threading) ──────────────────────────
    # Per-occupant Tier-3 ownership + bedroom (Phase 2.1): the proposer only
    # offers an occupant their OWN carried items, and a "bedroom" activity
    # scopes to that occupant's own bedroom.
    #
    # Windows (one activity occurrence each) are processed in chronological
    # order, interleaving occupants. A running object state is threaded through:
    # after each window's moves are selected they are applied to the state, and
    # the next window's proposer AND judge see the authoritative current state
    # instead of the proposer's assumed_from guess. The state block's hash is
    # folded into the displacement/judge cache tags, so editing an earlier
    # window correctly invalidates every later window.
    from .ownership import (
        assign_bedrooms, assign_ownership, restrict_inventory_to_owner,
        tier3_instance_label as tier3_label, TIER3_CATEGORIES,
    )
    from .running_state import RunningState
    from ..env.inventory import FLOOR_BOUND_CATEGORIES
    from .schemas import SURFACE_RELATIONSHIPS, PUT_AWAY_ANCHOR

    ownership = assign_ownership(persona)
    bedrooms = assign_bedrooms(persona)

    # Strategy 2+ asset binding: each owner's Tier-3 item gets a specific
    # render asset, chosen by the LLM from the reviewer-tagged pool so the
    # pick is in character (generation/asset_binding.py). Carried on the
    # result + manifest; build_realized_day obeys it verbatim.
    from .asset_binding import bind_owner_assets
    asset_bindings = bind_owner_assets(
        persona, ownership, household_id, model=model, cache=cache, force=force)

    def _floor_bound_surface(p: dict) -> bool:
        return (p.get("object_category") in FLOOR_BOUND_CATEGORIES
                and p.get("target_relationship") in SURFACE_RELATIONSHIPS)

    windows: list[tuple] = []
    for occ_idx, (occupant, trace) in enumerate(zip(persona.get("occupants", []), traces)):
        occ_name = occupant["name"]
        for activity in trace.get("activities", []):
            if activity.get("location") == "away":
                continue  # no indoor object displacements while away
            windows.append((float(activity["start"]), occ_idx, occ_name, trace, activity))
    windows.sort(key=lambda w: (w[0], w[1]))  # chronological, tie-break by occupant

    scene_regions = load_scene_regions(scene_id) if (use_semantic_grounding and world_graph is None) else None
    from ..env.inventory import load_scene_state as _load_scene_state
    try:
        _scene_state = _load_scene_state(scene_id)
    except Exception:
        _scene_state = None  # live-WorldGraph/synthetic paths: category-keyed fallback
    state = RunningState.initial(ownership, scene_state=_scene_state)
    # Tier-2b clutter enters the tracked state as real instances (bowl_1...),
    # mirroring build_manifest's numbering, so the state block/prompt and the
    # manifest replay agree on which bowl is where — and so the abundant-
    # storage spawn cap (catalog total) counts the clutter already out.
    # The resolver stores manifest-grade resolved slots, which the gate
    # preflight's no-op comparison requires.
    from ..rooms import resolve_slot as _resolve_slot
    state.seed_clutter(clutter, resolver=lambda p: _resolve_slot(
        p["target_anchor"], p["target_relationship"],
        room_instance_categories=room_instance_categories))
    # Live slot occupancy for the preflight's capacity gate — seeded from
    # every tracked instance's starting slot, the same way build_manifest
    # seeds its own slot_occupancy.
    slot_occupancy: dict[str, int] = dict(Counter(
        v for v in state.tier2_slots.values() if v))
    preflight_excluded: Counter = Counter()
    stats = GroundingStats()
    all_raw_proposals: list[dict] = []   # post-filter, pre-grounding (len only)
    all_candidates: list[dict] = []
    selected: list[dict] = []
    selected_realism_scores: list[float] = []
    retry_stats = {"windows_with_rejects": 0, "rejected_first_pass": 0,
                   "revision_proposals": 0, "revived_eligible": 0,
                   "killed_second_pass": 0, "hopeless_skipped": 0}
    n_abstained = 0
    n_floor_bound_dropped = 0

    for start, occ_idx, occ_name, trace, activity in windows:
        act_label = activity["activity"]
        act_end = float(activity["end"])
        act_location = activity.get("location")
        owned = ownership.get(occ_name, [])
        occ_inventory = restrict_inventory_to_owner(inventory, owned)
        # Seat-in-room gate: floor-bound furniture (chair/stool) is only in
        # this window's movable vocabulary if an instance is CURRENTLY in the
        # acting occupant's room — no chair in the room means you sit on the
        # built-in seating, not fetch one from the bedroom. Presence is a
        # pure function of start slots + moves-so-far, both covered by the
        # state hash, so caching stays correct.
        _present = state.categories_present_in(act_location)
        occ_inventory = {c: n for c, n in occ_inventory.items()
                         if c not in FLOOR_BOUND_CATEGORIES or c in _present}
        # Per-instance seat vocabulary: the seats currently in this room, by
        # id — offered to the proposer in place of the bare category (see
        # generate_displacements' seat_instances docstring) and listed in the
        # state block so it can pick one that isn't in use.
        seat_instances = state.seat_instances_in_room(act_location) if enrich_context else {}
        state_block = (state.object_state_block(occ_name, owned, room=act_location)
                       if enrich_context else None)
        live_occ = state.anchors_in_use(act_location) if enrich_context else None
        # Offer "put_away" only when this occupant has a carried item currently
        # out — nothing to put away otherwise (Phase 3 despawn).
        out_labels = {tier3_label(occ_name, c) for c in owned
                      if state.tier3.get(tier3_label(occ_name, c)) is not None}
        allow_put_away = enrich_context and bool(out_labels)

        displacement = generate_displacements(
            activity=act_label, start=start, end=act_end,
            occupant_name=occ_name, occupant_index=occ_idx, persona=persona,
            inventory=occ_inventory, room_inventory=room_inventory_reachable,
            location=act_location, anchor_inventory=anchor_inventory_reachable,
            anchor_census=anchor_census, household_id=household_id, day=day,
            model=model, temperature=temperature, cache=cache, force=force,
            trace=trace, include_context=enrich_context, bedroom_index=bedrooms.get(occ_name),
            current_state_block=state_block, live_occupancy=live_occ,
            allow_put_away=allow_put_away, seat_instances=seat_instances,
        )
        window_props: list[dict] = []
        from .instances import instance_token_category
        for prop in displacement.get("proposals", []):
            # Normalize instance-token proposals ("stool_2") back to
            # (category, _instance) so grounding/judge/selection see a real
            # category and the manifest/running state move the model's own
            # chosen instance instead of re-resolving one.
            token = prop.get("object_category", "")
            if token in seat_instances:
                prop["_instance"] = token
                prop["object_category"] = instance_token_category(token)
            prop["_activity"]       = act_label
            prop["_occupant"]       = occ_name
            prop["_occupant_index"] = occ_idx
            prop["_start"]          = activity["start"]
            prop["_end"]            = activity["end"]
            prop["_location"]       = act_location
            window_props.append(prop)

        n_abstained += sum(1 for p in window_props if p.get("target_anchor") == ABSTAIN_ANCHOR)
        window_props = [p for p in window_props if p.get("target_anchor") != ABSTAIN_ANCHOR]
        n_floor_bound_dropped += sum(1 for p in window_props if _floor_bound_surface(p))
        window_props = [p for p in window_props if not _floor_bound_surface(p)]

        # Phase 3 despawn: split off "put_away" proposals. They bypass grounding
        # (a put-away is always feasible), but only for a Tier-3 item currently
        # out; anything else claiming put_away is dropped. Marked _despawn so the
        # manifest and running state treat them as the item leaving the scene.
        despawns_w: list[dict] = []
        placements_w: list[dict] = []
        from ..env.inventory import CONCEALING_STORAGE_CATEGORIES
        from ..rooms import census_label_parts as _clp
        for p in window_props:
            if p.get("target_anchor") == PUT_AWAY_ANCHOR:
                if (p.get("object_category") in TIER3_CATEGORIES
                        and tier3_label(occ_name, p["object_category"]) in out_labels):
                    p["_despawn"] = True
                    despawns_w.append(p)
                # else: invalid put_away, silently dropped
            elif (p.get("target_relationship") == "inside"
                  and (_pp := _clp(p.get("target_anchor", ""))) is not None
                  and _pp[1] in CONCEALING_STORAGE_CATEGORIES):
                # Concealment: 'inside' closed storage is a put-away, not a
                # visible placement — the object is stored out of sight.
                # Bypasses grounding (always feasible) like put_away.
                p["_despawn"] = True
                p["_concealed_in"] = p["target_anchor"]
                despawns_w.append(p)
            else:
                placements_w.append(p)
        all_raw_proposals.extend(placements_w + despawns_w)

        if env is not None and agent is not None and world_graph is not None:
            grounded_w, stats = ground_displacement_batch(
                placements_w, world_graph, env, agent, grasp_mgr, stats, scene_id=scene_id)
        elif use_semantic_grounding:
            grounded_w, stats = ground_displacement_batch_semantic(
                placements_w, inventory, scene_regions, stats,
                anchor_inventory=anchor_inventory_reachable, anchor_census=anchor_census)
        else:
            grounded_w = placements_w
            stats.total += len(placements_w)
            stats.accepted += len(placements_w)
        grounded_w = grounded_w + despawns_w  # despawns join the judged/selected pool
        if not grounded_w:
            continue

        scores, judge_meta = score_realism_batch(
            candidates=grounded_w, activity=act_label, occupant_name=occ_name,
            persona=persona, household_id=household_id, day=day, start=start, end=act_end,
            occupant_index=occ_idx, model=model, temperature=temperature, cache=cache, force=force,
            judge_thinking=judge_thinking, judge_style=judge_style, trace=trace,
            include_context=enrich_context, exemplar_block=exemplar_block,
            current_state_block=state_block,
            request_fix=judge_retry,
        )
        judge_reasons = judge_meta.get("reasons") or [""] * len(grounded_w)
        for c, s, jr in zip(grounded_w, scores, judge_reasons):
            c["_judge_score"]     = s
            c["_judge_stage_tag"] = judge_meta["stage_tag"]
            c["_judge_seed"]      = judge_meta["seed"]
            # The judge's own pre-score evidence weighing (guided schema puts
            # reason before score) — persisted so choices.jsonl carries the
            # WHY next to every score, selected and rejected alike.
            if jr:
                c["_judge_reason"] = jr
            if judge_meta.get("think"):
                c["_judge_think"] = judge_meta["think"][:500]
            if judge_meta.get("score_fallback"):
                c["_judge_score_fallback"] = judge_meta["score_fallback"]

        # ── Judge-retry: ONE revision round per window ──────────────────
        # The strict judge is precise about WHY a candidate fails (most
        # often: sound reason, incongruous destination). Feeding each
        # reject's critique + fix hint back to the proposer for a single
        # revision grows the ELIGIBLE pool — the term that binds move counts
        # whenever pool < Poisson draw — without touching lambda or the
        # floor. The revised set is re-grounded and re-judged by a fresh
        # kill-only call (no fix request, separate seed/tag, no round 3):
        # its rejects are final.
        if judge_retry:
            _floor = REALISM_FLOOR
            fixes = judge_meta.get("fixes") or [""] * len(grounded_w)
            fix_by_id = {id(c): f for c, f in zip(grounded_w, fixes)}
            all_rejects = [c for c, s in zip(grounded_w, scores)
                           if s < _floor and not c.get("_despawn")]
            # "hopeless" sentinel (cheap string check): the judge marked the
            # reject as unrepairable by any small edit — sending it back to
            # the proposer wastes a revision slot and, when a whole window's
            # rejects are hopeless, the entire revision + second-judge round
            # (two LLM calls) is skipped.
            rejected_w = [c for c in all_rejects
                          if "hopeless" not in fix_by_id.get(id(c), "").lower()]
            retry_stats["hopeless_skipped"] += len(all_rejects) - len(rejected_w)
            if rejected_w:
                retry_stats["windows_with_rejects"] += 1
                retry_stats["rejected_first_pass"] += len(rejected_w)
                fb_lines = []
                for c in rejected_w:
                    line = (f"- {c.get('object_category')} -> "
                            f"{c.get('target_anchor')} "
                            f"({c.get('target_relationship')}) | your reason: "
                            f"{str(c.get('reason', ''))[:160]} | reviewer: "
                            f"{str(c.get('_judge_reason', ''))[:200]}")
                    if fix_by_id.get(id(c)):
                        line += f" | suggested fix: {fix_by_id[id(c)][:200]}"
                    fb_lines.append(line)
                rev_disp = generate_displacements(
                    activity=act_label, start=start, end=act_end,
                    occupant_name=occ_name, occupant_index=occ_idx, persona=persona,
                    inventory=occ_inventory, room_inventory=room_inventory_reachable,
                    location=act_location, anchor_inventory=anchor_inventory_reachable,
                    anchor_census=anchor_census, household_id=household_id, day=day,
                    model=model, temperature=temperature, cache=cache, force=force,
                    trace=trace, include_context=enrich_context,
                    bedroom_index=bedrooms.get(occ_name),
                    current_state_block=state_block, live_occupancy=live_occ,
                    allow_put_away=allow_put_away, seat_instances=seat_instances,
                    revision_feedback="\n".join(fb_lines),
                )
                rev_props: list[dict] = []
                for prop in rev_disp.get("proposals", [])[:len(rejected_w)]:
                    token = prop.get("object_category", "")
                    if token in seat_instances:
                        prop["_instance"] = token
                        prop["object_category"] = instance_token_category(token)
                    if prop.get("target_anchor") == ABSTAIN_ANCHOR:
                        continue
                    if _floor_bound_surface(prop):
                        continue
                    if prop.get("target_anchor") == PUT_AWAY_ANCHOR:
                        continue  # revision round is placements-only
                    prop["_activity"] = act_label
                    prop["_occupant"] = occ_name
                    prop["_occupant_index"] = occ_idx
                    prop["_start"] = activity["start"]
                    prop["_end"] = activity["end"]
                    prop["_location"] = act_location
                    prop["_revision_round"] = 1
                    rev_props.append(prop)
                retry_stats["revision_proposals"] += len(rev_props)
                if env is not None and agent is not None and world_graph is not None:
                    rev_grounded, stats = ground_displacement_batch(
                        rev_props, world_graph, env, agent, grasp_mgr, stats,
                        scene_id=scene_id)
                elif use_semantic_grounding:
                    rev_grounded, stats = ground_displacement_batch_semantic(
                        rev_props, inventory, scene_regions, stats,
                        anchor_inventory=anchor_inventory_reachable,
                        anchor_census=anchor_census)
                else:
                    rev_grounded = rev_props
                    stats.total += len(rev_props)
                    stats.accepted += len(rev_props)
                all_raw_proposals.extend(rev_props)
                if rev_grounded:
                    rev_scores, rev_meta = score_realism_batch(
                        candidates=rev_grounded, activity=act_label,
                        occupant_name=occ_name, persona=persona,
                        household_id=household_id, day=day, start=start,
                        end=act_end, occupant_index=occ_idx, model=model,
                        temperature=temperature, cache=cache, force=force,
                        judge_thinking=judge_thinking, judge_style=judge_style,
                        trace=trace, include_context=enrich_context,
                        exemplar_block=exemplar_block,
                        current_state_block=state_block,
                        round_tag="r2kill",
                    )
                    rev_reasons = rev_meta.get("reasons") or [""] * len(rev_grounded)
                    for c, s, jr in zip(rev_grounded, rev_scores, rev_reasons):
                        c["_judge_score"] = s
                        c["_judge_stage_tag"] = rev_meta["stage_tag"]
                        c["_judge_seed"] = rev_meta["seed"]
                        if jr:
                            c["_judge_reason"] = jr
                    revived = sum(1 for s in rev_scores if s >= _floor)
                    retry_stats["revived_eligible"] += revived
                    retry_stats["killed_second_pass"] += len(rev_scores) - revived
                    grounded_w = grounded_w + rev_grounded
                    scores = scores + rev_scores

        # Replay-gate preflight BEFORE the Poisson draw (see
        # _preflight_replay_gates): the draw shapes the FINAL manifest count,
        # gates only shrink the pool it draws from.
        score_by_id = {id(c): s for c, s in zip(grounded_w, scores)}
        gated_w, excl = _preflight_replay_gates(
            grounded_w, state, occ_name, room_instance_categories,
            admission_map, slot_occupancy)
        preflight_excluded.update(excl)

        chosen = select_for_activity(gated_w, [score_by_id[id(c)] for c in gated_w],
                                     act_label, household_id, day,
                                     start=start, activity_scale=activity_scale)
        chosen_ids = {id(c) for c in chosen}
        for c in grounded_w:
            c["_selected"] = id(c) in chosen_ids
        all_candidates.extend(grounded_w)
        selected.extend(chosen)
        selected_realism_scores.extend(score_by_id[id(c)] for c in chosen)

        # Commit the chosen moves' capacity consumption (mirrors
        # build_manifest: only slots with a real per-object budget count).
        from ..env.anchor_admission import anchor_capacity as _anchor_capacity
        for c in chosen:
            slot = c.get("_resolved_slot")
            if slot and _anchor_capacity(admission_map, slot) is not None:
                slot_occupancy[slot] = slot_occupancy.get(slot, 0) + 1

        state.apply(chosen)  # thread the running state to the next window

    grounded = all_candidates  # grounded_proposals == len(all_candidates)

    mean_realism = (
        sum(selected_realism_scores) / len(selected_realism_scores)
        if selected_realism_scores else 0.0
    )

    return {
        "household_id":        household_id,
        "scene_id":            scene_id,
        # the household's stable weekly pattern (once per household) and this
        # day's scheduled calendar event (None = ordinary day) — the two
        # structures that replaced free-text day imagination (see
        # event_calendar.py's postmortem note)
        "routine_charter":     charter,
        "calendar_event":      event,
        # judge-retry accounting (all zeros when the flag is off): how many
        # windows had first-pass rejects, how many revision proposals came
        # back, and the second judge's verdict split (kill-only, no round 3).
        "judge_retry_stats":   retry_stats,
        # The generating model — the run's comparison label (qwen-style vs
        # llama-style arms; the eval webapp's future `condition` field).
        "model":               model,
        "profile":             household_type,
        "day":                 day,
        "clutter":             clutter,
        # {owner label -> render asset uid} for owned Tier-3 items (LLM-
        # bound from the tagged pool; see generation/asset_binding.py).
        "asset_bindings":      asset_bindings,
        "persona":             persona,
        "traces":              traces,
        "displacements":       selected,
        # Every judge-scored candidate (selected AND rejected), each with
        # _judge_score/_judge_stage_tag/_judge_seed[/_judge_think] and
        # _selected — the full record a judge comparison needs. Also
        # mirrored one-per-line to choices.jsonl by run_batch.
        "candidates":          all_candidates,
        "raw_proposals":       len(all_raw_proposals),
        "grounded_proposals":  len(grounded),
        # Part A abstain counters — proposals whose target_anchor was the
        # explicit "none" entry, dropped before grounding (see above).
        "abstained_proposals": n_abstained,
        "abstained_clutter":   n_abstained_clutter,
        # Clutter admission (judge + floor + catalog cap — see Stage 0):
        # below-floor and over-cap are counted separately, and the rejected
        # placements ride along (with their _judge_score) for inspection.
        "clutter_below_floor": n_clutter_below_floor,
        "clutter_over_cap":    n_clutter_over_cap,
        "clutter_rejected":    clutter_rejected,
        # Floor-Bound Realization round: chair/stool surface proposals
        # dropped before grounding (see the filter above).
        "floor_bound_surface_dropped": n_floor_bound_dropped,
        # Replay-gate preflight exclusions (pre-Poisson; see
        # _preflight_replay_gates). These candidates ride in `candidates`
        # with _gate_excluded set; the manifest's own integrity_stats should
        # show ~zero corresponding drops now.
        "preflight_excluded":  dict(preflight_excluded),
        "mean_realism_score":  round(mean_realism, 4),
        "grounding_stats": {
            "total":                stats.total,
            "accepted":             stats.accepted,
            "survival_rate":        round(stats.survival_rate, 4),
            "infra_rejection_rate": round(stats.infra_rejection_rate, 4),
            "model_rejection_rate": round(stats.model_rejection_rate, 4),
            "no_object":            stats.no_object_in_scene,
            "no_anchor":            stats.no_anchor_in_scene,
            "no_placement":         stats.no_valid_placement,
            "bad_relation":         stats.unsupported_relation,
            "rejected_categories":  dict(stats.rejected_categories),
        },
        "conflict_report": conflict_report,
    }


# ---------------------------------------------------------------------------
# Batch run + aggregate survival rate
# ---------------------------------------------------------------------------

def run_batch(
    scene_ids: list[str],
    household_type: str,
    out_dir: pathlib.Path,
    day: int = 0,
    n_variants: int = 1,
    n_days: int = 1,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    cache_dir: Optional[str] = None,
    force: bool = False,
    use_semantic_grounding: bool = True,
    validate_trace: bool = True,
    reachability_filtering: bool = False,
    judge_thinking: bool = False,
    judge_style: str = "asis",
    judge_retry: bool = False,
    enrich_context: bool = False,
    exemplar_block=None,
    activity_scale: float = 1.0,
) -> tuple[GroundingStats, float]:
    """Generate, ground, and build manifests for a list of scenes.

    activity_scale: scene-activity knob — multiplies every window's Poisson
    mean (see selection.select_for_activity), so one number makes the whole
    batch's homes busier (>1) or quieter (<1) without touching gates,
    prompts, or judge behavior.

    Writes one subfolder per (scene, variant, day) under
    out_dir/<scene_id>_<household_type>[_v<variant>][_day<N>]/ (the _v suffix
    is omitted for variant 0 and the _day suffix is omitted entirely when
    n_days == 1 — the default — so single-day runs produce the exact same
    layout as before this parameter existed):
      generation_result.json — full pipeline output (persona, traces, displacements).
      manifest.json          — Change-log form consumed by qa/questions.py,
                                env/replay.py, agents/harness.py, and the
                                downstream eval/figure scripts.
      replay.json             — compact replay-viewer format (exports.py):
                                occupant activity tuples, change tuples
                                extended with mover, and a per-category
                                location-change summary (count, distinct
                                slots visited, mean dwell time) — the input
                                future hazard-rate calibration consumes.

    n_variants: how many distinct persona variants to generate per scene —
    the "k examples" knob (see generate_for_scene's `variant` docstring for
    why this is a different household, not a different day of the same
    household, and why it's guaranteed to actually perturb the downstream
    activity/displacement/realism seeds too).

    n_days: how many independent days to generate for the *same* household
    (persona held fixed — day-invariant by design — while activity traces
    and displacements vary, since their seeds include day). This is what
    the DecayModel calibration protocol needs: fit per-category hazard
    rates on a train split of days, evaluate on held-out days. Days run
    `day, day+1, ..., day+n_days-1`. The day-suffix is included for every
    day (including the first) whenever n_days > 1, since otherwise day 0
    would collide with the no-suffix convention single-day runs rely on.

    validate_trace: run trace_validate.validate() against each manifest
    immediately after it's built and treat a hard-invariant violation as a
    generation failure for that (scene, variant) — same try/except boundary
    as a raw generation error, so one bad scene is reported and skipped, not
    a silent bad manifest.json written to disk. Set False to load/rebuild
    manifests from older generation_result.json data for before/after
    comparison, where hard-invariant violations are expected and shouldn't
    abort the run.

    Returns (aggregated GroundingStats, mean realism score of selected
    displacements) — kept as two independent values rather than one blended
    number; see GroundingStats.infra_rejection_rate / model_rejection_rate
    for why grounding itself is already split two ways.

    reachability_filtering: Reachability Removal Phase 1 (default False).
    Threaded to both generate_for_scene (soft, vocabulary-level pruning)
    and build_manifest (hard, rejection-level gate) so the two stay in
    sync — see either function's own docstring for the full rationale.
    """
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    agg = GroundingStats()
    realism_sum   = 0.0
    realism_count = 0
    manifest_seed = 0

    for scene_id in scene_ids:
        for variant in range(n_variants):
            for day_offset in range(n_days):
                actual_day = day + day_offset
                label = (
                    f"{scene_id}"
                    + (f" variant {variant}" if variant else "")
                    + (f" day {actual_day}" if n_days > 1 else "")
                )
                try:
                    result = generate_for_scene(
                        scene_id=scene_id,
                        household_type=household_type,
                        day=actual_day,
                        variant=variant,
                        model=model,
                        temperature=temperature,
                        cache_dir=cache_dir,
                        force=force,
                        use_semantic_grounding=use_semantic_grounding,
                        reachability_filtering=reachability_filtering,
                        judge_thinking=judge_thinking,
                        judge_style=judge_style,
                        judge_retry=judge_retry,
                        enrich_context=enrich_context,
                        exemplar_block=exemplar_block,
                        activity_scale=activity_scale,
                    )

                    manifest_seed += 1
                    manifest = build_manifest(
                        scene_id, household_type, actual_day, result, seed=manifest_seed,
                        reachability_filtering=reachability_filtering,
                    )

                    if validate_trace:
                        from ..trace_validate import validate as validate_trace_fn
                        report = validate_trace_fn(manifest["changes"], result["traces"])
                        if not report.ok:
                            raise RuntimeError(f"trace_validate failed: {report.summary()}")
                except Exception as e:
                    print(f"  [ERROR] {label}: {e}")
                    continue

                gs = result["grounding_stats"]
                agg.total                += gs["total"]
                agg.accepted             += gs["accepted"]
                agg.no_object_in_scene   += gs["no_object"]
                agg.no_anchor_in_scene   += gs["no_anchor"]
                agg.no_valid_placement   += gs["no_placement"]
                agg.unsupported_relation += gs["bad_relation"]
                for cat, n in gs.get("rejected_categories", {}).items():
                    agg.rejected_categories[cat] = agg.rejected_categories.get(cat, 0) + n

                n_selected = len(result["displacements"])
                if n_selected:
                    realism_sum   += result["mean_realism_score"] * n_selected
                    realism_count += n_selected

                folder_name = (
                    f"{scene_id}_{household_type}"
                    + (f"_v{variant}" if variant else "")
                    + (f"_day{actual_day}" if n_days > 1 else "")
                )
                scene_dir = out_dir / folder_name
                scene_dir.mkdir(parents=True, exist_ok=True)
                (scene_dir / "generation_result.json").write_text(json.dumps(result, indent=2))
                (scene_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
                # One JSON object per judge-scored candidate (selected and
                # rejected) — the flat, greppable form of result["candidates"].
                (scene_dir / "choices.jsonl").write_text(
                    "".join(json.dumps(c) + "\n" for c in result["candidates"])
                )

                replay = to_replay_format(scene_id, household_type, actual_day, result, manifest)
                (scene_dir / "replay.json").write_text(json.dumps(replay, indent=2))

                print(f"  {label}  survival={gs['survival_rate']:.1%}  "
                      f"({gs['accepted']}/{gs['total']} proposals)  "
                      f"realism={result['mean_realism_score']:.2f}  "
                      f"{len(manifest['changes'])} changes  → {scene_dir.name}/")

    mean_realism = realism_sum / realism_count if realism_count else 0.0
    return agg, mean_realism
