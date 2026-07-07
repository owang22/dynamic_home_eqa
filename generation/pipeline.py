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
from collections import defaultdict
from typing import Optional, TYPE_CHECKING

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
from .exports import to_replay_format
from .llm_client import DEFAULT_MODEL, DEFAULT_TEMPERATURE
from .manifest import build_manifest
from .persona import generate_persona
from .regions import load_scene_regions
from .schemas import filter_displacement_proposals
from .selection import select_for_activity
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
) -> dict:
    """Run the full generation pipeline for one scene.

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

    Returns:
        Per-scene output dict (see module docstring).
    """
    household_id = f"{scene_id}_{household_type}"
    if variant:
        household_id += f"_v{variant}"
    cache = ResponseCache(cache_dir) if cache_dir else None

    # ── Inventory ─────────────────────────────────────────────────────────────
    if world_graph is not None:
        inventory        = inventory_from_world_graph(world_graph)
        room_inventory   = room_inventory_from_world_graph(world_graph)
        anchor_inventory = None  # no equivalent census wired for the live-WorldGraph path yet
    else:
        inventory        = inventory_from_scene_state(scene_id)
        room_inventory   = room_inventory_from_scene_state(scene_id)
        anchor_inventory = anchor_inventory_from_scene_state(scene_id)

    # ── Stage 0: Tier 2b clutter placement (once per house + household) ───────
    # Runs before persona/activities/displacements — a clutter object's home is
    # a property of the house and who lives there, not of any day's schedule.
    # Skipped on the live-WorldGraph path: no real anchor census is wired for
    # it yet (anchor_inventory is None there), so there's nothing to ground
    # clutter placements against.
    clutter: list[dict] = []
    if anchor_inventory is not None:
        clutter = generate_clutter(
            household_type=household_type,
            household_id=household_id,
            anchor_inventory=anchor_inventory,
            room_inventory=room_inventory,
            model=model,
            temperature=temperature,
            cache=cache,
            force=force,
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
        )

    # ── Stage 3: Displacement proposals (per activity per occupant) ───────────
    all_raw_proposals: list[dict] = []
    for occ_idx, (occupant, trace) in enumerate(
            zip(persona.get("occupants", []), traces)):
        occ_name = occupant["name"]
        for activity in trace.get("activities", []):
            act_label = activity["activity"]
            act_location = activity.get("location")
            if act_location == "away":
                continue  # no indoor object displacements while away

            displacement = generate_displacements(
                activity=act_label,
                start=float(activity["start"]),
                end=float(activity["end"]),
                occupant_name=occ_name,
                occupant_index=occ_idx,
                persona=persona,
                inventory=inventory,
                room_inventory=room_inventory,
                location=act_location,
                anchor_inventory=anchor_inventory,
                household_id=household_id,
                day=day,
                model=model,
                temperature=temperature,
                cache=cache,
                force=force,
            )
            for prop in displacement.get("proposals", []):
                prop["_activity"]        = act_label
                prop["_occupant"]        = occ_name
                prop["_occupant_index"]  = occ_idx
                prop["_start"]           = activity["start"]
                prop["_end"]             = activity["end"]
                prop["_location"]        = act_location
                all_raw_proposals.append(prop)

    # ── Grounding (batched across the whole scene) ─────────────────────────────
    stats = GroundingStats()
    if env is not None and agent is not None and world_graph is not None:
        grounded, stats = ground_displacement_batch(
            all_raw_proposals, world_graph, env, agent, grasp_mgr, stats, scene_id=scene_id
        )
    elif use_semantic_grounding:
        scene_regions = load_scene_regions(scene_id)  # None if JSON missing
        grounded, stats = ground_displacement_batch_semantic(
            all_raw_proposals, inventory, scene_regions, stats, anchor_inventory=anchor_inventory
        )
    else:
        grounded = all_raw_proposals
        stats.total    = len(all_raw_proposals)
        stats.accepted = len(all_raw_proposals)

    # ── Realism scoring + stochastic selection (per activity occurrence) ───────
    # Judge calls only see one activity's grounded candidates at a time — never
    # the whole scene's pool — so batching for call-count efficiency doesn't
    # reintroduce the "see everything, rank favorites" bias.
    by_activity: dict[tuple, list[dict]] = defaultdict(list)
    for prop in grounded:
        key = (prop["_occupant"], prop["_activity"], prop["_start"], prop["_end"])
        by_activity[key].append(prop)

    selected: list[dict] = []
    selected_realism_scores: list[float] = []
    for (occ_name, act_label, act_start, act_end), group in by_activity.items():
        occ_idx = group[0].get("_occupant_index", 0)
        scores = score_realism_batch(
            candidates=group,
            activity=act_label,
            occupant_name=occ_name,
            persona=persona,
            household_id=household_id,
            day=day,
            start=act_start,
            occupant_index=occ_idx,
            model=model,
            temperature=temperature,
            cache=cache,
            force=force,
        )
        chosen = select_for_activity(group, scores, act_label, household_id, day, start=act_start)
        score_by_id = {id(c): s for c, s in zip(group, scores)}
        selected.extend(chosen)
        selected_realism_scores.extend(score_by_id[id(c)] for c in chosen)

    mean_realism = (
        sum(selected_realism_scores) / len(selected_realism_scores)
        if selected_realism_scores else 0.0
    )

    return {
        "household_id":        household_id,
        "scene_id":            scene_id,
        "profile":             household_type,
        "day":                 day,
        "clutter":             clutter,
        "persona":             persona,
        "traces":              traces,
        "displacements":       selected,
        "raw_proposals":       len(all_raw_proposals),
        "grounded_proposals":  len(grounded),
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
) -> tuple[GroundingStats, float]:
    """Generate, ground, and build manifests for a list of scenes.

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
                    )

                    manifest_seed += 1
                    manifest = build_manifest(scene_id, household_type, actual_day, result, seed=manifest_seed)

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

                replay = to_replay_format(scene_id, household_type, actual_day, result, manifest)
                (scene_dir / "replay.json").write_text(json.dumps(replay, indent=2))

                print(f"  {label}  survival={gs['survival_rate']:.1%}  "
                      f"({gs['accepted']}/{gs['total']} proposals)  "
                      f"realism={result['mean_realism_score']:.2f}  "
                      f"{len(manifest['changes'])} changes  → {scene_dir.name}/")

    mean_realism = realism_sum / realism_count if realism_count else 0.0
    return agg, mean_realism
