"""
Grounding integration — validates displacement proposals against PARTNR's
simulation before accepting them into the dataset.

This is the boundary between LLM-generated semantics and physics. The LLM
proposes {object_category, target_relationship, target_anchor, reason}; this
module asks PARTNR: "can this object actually be placed here?"

Survival rate instrumentation is the primary metric for model selection.

PARTNR API used (verified against actual codebase):

  Spatial relationships:
    "on"      → sample_position_on_furniture(spatial_relation="on", ...)
    "within"  → sample_position_on_furniture(spatial_relation="within", ...)
    "next_to" → spatial_constraint="next_to" on sample_position_on_furniture

  Spatial relation checking (after grounding):
    SimBasedPredicates.is_on_top()   → for "on"
    SimBasedPredicates.is_inside()   → for "within"
    SimBasedPredicates.is_next_to()  → for "next_to"
    SimBasedPredicates.is_in_room()  → for "in_region"

  WorldGraph traversal:
    world_graph.get_all_furnitures() → List[Furniture]
    world_graph.get_all_objects()    → List[Object]
    world_graph.group_furniture_by_room() → Dict[str, List[Furniture]]
    furniture.sample_place_location(spatial_relation, spatial_constraint,
                                    reference_object, env, agent, grasp_mgr)
      → List[Tuple[mn.Vector3, mn.Quaternion]]  — empty list if no valid placement

  Relationship ↔ spatial_relation mapping:
    "on"       → spatial_relation="on",     spatial_constraint=None
    "on_top"   → spatial_relation="on",     spatial_constraint=None
    "within"   → spatial_relation="within", spatial_constraint=None
    "inside"   → spatial_relation="within", spatial_constraint=None
    "next_to"  → spatial_relation="on",     spatial_constraint="next_to"
    "near"     → spatial_relation="on",     spatial_constraint="next_to"
    "in_region"→ validated via SimBasedPredicates.is_in_room() only

All geometry (positions, quaternions, collision checks) is PARTNR's
responsibility. This module never produces or validates coordinates.
"""
from __future__ import annotations

import dataclasses
from collections import defaultdict
from typing import Optional, TYPE_CHECKING

from .schemas import REGION_ONLY_RELATIONSHIPS as _REGION_ONLY

if TYPE_CHECKING:
    from habitat_llm.world_model.world_graph import WorldGraph
    from habitat_llm.world_model.entity import Object, Furniture
    from .regions import SceneRegions

# ---------------------------------------------------------------------------
# Canonical PARTNR relationship vocabulary — extend schemas.py from this
# ---------------------------------------------------------------------------

# Maps our generation relationship strings → PARTNR (spatial_relation, constraint).
# Relationships not in this map are treated as "in_region" (room-level only).
_RELATION_MAP: dict[str, tuple[str, str | None]] = {
    "on":        ("on",     None),
    "on_top":    ("on",     None),
    "within":    ("within", None),
    "inside":    ("within", None),
    "next_to":   ("on",     "next_to"),
    "near":      ("on",     "next_to"),
}


def _partnr_relation(relationship: str) -> tuple[str, str | None] | None:
    """Return (spatial_relation, constraint) pair for a generation relationship string.

    Returns None if the relationship requires only room-level validation.
    """
    if relationship in _REGION_ONLY:
        return None
    return _RELATION_MAP.get(relationship, ("on", None))


# ---------------------------------------------------------------------------
# Grounding result
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class GroundingResult:
    """Outcome of grounding one displacement proposal."""
    proposal:   dict            # Original proposal dict
    accepted:   bool            # True if placement was found
    positions_found: int        # Count of valid placement positions (0 if rejected)
    reason:     str             # Human-readable rejection reason if not accepted


@dataclasses.dataclass
class GroundingStats:
    """Rejection statistics for one batch of proposals.

    Deliberately not a single survival rate: no_anchor rejections are mostly
    an infrastructure artifact (region/anchor data the grounder couldn't
    resolve), not a signal about model quality, and blending them into one
    number makes infrastructure gaps look like model failure. See
    infra_rejection_rate / model_rejection_rate.
    """
    total:     int = 0
    accepted:  int = 0
    # Break down rejection reasons for diagnostics
    no_object_in_scene: int = 0
    no_anchor_in_scene: int = 0
    no_valid_placement: int = 0
    unsupported_relation: int = 0
    # {object_category: count} for no_object rejections. A category that
    # recurs here across many proposals usually means our inventory names it
    # differently than the model does (vocabulary mismatch), not that the
    # model is hallucinating objects — worth checking before assuming the
    # latter.
    rejected_categories: dict = dataclasses.field(default_factory=dict)

    def log_rejected_category(self, category: str) -> None:
        self.rejected_categories[category] = self.rejected_categories.get(category, 0) + 1

    @property
    def survival_rate(self) -> float:
        return self.accepted / self.total if self.total else 0.0

    @property
    def infra_rejection_rate(self) -> float:
        """Rejections caused by grounding infrastructure gaps (missing/unresolved
        anchor or region data), not model error. Should trend to ~0 as region
        coverage improves; not a model-quality signal."""
        return self.no_anchor_in_scene / self.total if self.total else 0.0

    @property
    def model_rejection_rate(self) -> float:
        """Rejections attributable to the model: hallucinated categories
        (no_object) or semantically valid but physically ungroundable proposals
        (no_placement). This is the real grounding-quality signal."""
        return (
            (self.no_object_in_scene + self.no_valid_placement + self.unsupported_relation)
            / self.total if self.total else 0.0
        )

    def __str__(self) -> str:
        return (
            f"survival={self.survival_rate:.1%}  "
            f"({self.accepted}/{self.total})  "
            f"infra_rejection={self.infra_rejection_rate:.1%}  "
            f"model_rejection={self.model_rejection_rate:.1%}  "
            f"no_object={self.no_object_in_scene}  "
            f"no_anchor={self.no_anchor_in_scene}  "
            f"no_placement={self.no_valid_placement}  "
            f"bad_relation={self.unsupported_relation}"
        )


# ---------------------------------------------------------------------------
# Object/Furniture lookup helpers
# ---------------------------------------------------------------------------

def _find_objects_by_category(
    world_graph: "WorldGraph",
    category: str,
) -> list["Object"]:
    """Return all Object nodes whose type matches category (case-insensitive)."""
    cat_lower = category.lower()
    return [
        obj for obj in world_graph.get_all_objects()
        if _obj_type(obj).lower() == cat_lower
           or cat_lower in _obj_type(obj).lower()
    ]


def _find_furniture_by_category(
    world_graph: "WorldGraph",
    anchor_category: str,
) -> list["Furniture"]:
    """Return all Furniture nodes whose type matches anchor_category."""
    cat_lower = anchor_category.lower()
    return [
        f for f in world_graph.get_all_furnitures()
        if cat_lower in _furniture_type(f).lower()
    ]


def _obj_type(obj) -> str:
    return (
        getattr(obj, "category", None)
        or obj.properties.get("type", "")
        or getattr(obj, "name", "")
    )


def _furniture_type(f) -> str:
    return (
        getattr(f, "category", None)
        or f.properties.get("type", "")
        or getattr(f, "name", "")
    )


def _ground_in_region_by_geometry(
    proposal: dict,
    world_graph: "WorldGraph",
    scene_id: Optional[str],
) -> Optional[GroundingResult]:
    """Point-in-volume test for an in_region proposal, using real HSSD region
    geometry against furniture translations already present in the WorldGraph.

    Returns None (defer to the string-match fallback) if scene_id is missing,
    the scene has no region annotations, or no furniture node exposes a
    "translation" property — anything that stops this from being a strictly
    better signal than the fallback it's meant to replace.
    """
    if scene_id is None:
        return None
    from .regions import load_scene_regions, region_for_point, rooms_match

    scene_regions = load_scene_regions(scene_id)
    if scene_regions is None:
        return None

    anchor_cat = proposal.get("target_anchor", "")
    matched_positions = 0
    for furn in world_graph.get_all_furnitures():
        translation = furn.properties.get("translation")
        if not translation or len(translation) != 3:
            continue
        region = region_for_point(tuple(translation), scene_regions)
        if region is not None and rooms_match(anchor_cat, region.normalised):
            matched_positions += 1

    if matched_positions == 0:
        # No furniture geometrically confirmed in this region — could mean the
        # region is genuinely empty of tracked furniture, not that it doesn't
        # exist. Defer to the fallback rather than asserting rejection here.
        return None
    return GroundingResult(proposal, True, matched_positions, "")


# ---------------------------------------------------------------------------
# Single-proposal grounder
# ---------------------------------------------------------------------------

def ground_proposal(
    proposal: dict,
    world_graph: "WorldGraph",
    env,
    agent,
    grasp_mgr=None,
    scene_id: Optional[str] = None,
) -> GroundingResult:
    """Validate one displacement proposal against PARTNR's simulation.

    Args:
        proposal:    One entry from the displacement stage output.
                     Keys: object_category, target_relationship, target_anchor, reason.
        world_graph: Live PARTNR WorldGraph for the current scene.
        env:         PARTNR EnvironmentInterface (for sample_place_location).
        agent:       ArticulatedAgentBase (for sample_place_location).
        grasp_mgr:   RearrangeGraspManager (for placement sampling; None = skip
                     grasp-based placement, still validates via in_region check).
        scene_id:    HSSD scene id. When given and region annotations exist,
                     in_region proposals are validated by a real point-in-volume
                     test (generation/regions.py) against furniture translations,
                     instead of substring-matching WorldGraph's own room names —
                     the latter can diverge from HSSD's region geometry. Falls
                     back to the string-match when scene_id is omitted, region
                     data is missing, or furniture nodes carry no translation
                     (this path is not covered by an integration test against a
                     live WorldGraph; the fallback keeps prior behavior intact
                     if the geometry check can't run for any reason).

    Returns:
        GroundingResult with accepted=True if at least one valid placement exists.
    """
    obj_cat    = proposal.get("object_category", "")
    relation   = proposal.get("target_relationship", "")
    anchor_cat = proposal.get("target_anchor", "")

    # Find objects of the proposed category in the scene
    objects = _find_objects_by_category(world_graph, obj_cat)
    if not objects:
        return GroundingResult(proposal, False, 0,
                               f"no {obj_cat!r} found in scene")

    # in_region proposals: real point-in-volume test when possible, falling
    # back to substring-matching WorldGraph's own room names.
    if relation in _REGION_ONLY:
        geo_result = _ground_in_region_by_geometry(proposal, world_graph, scene_id)
        if geo_result is not None:
            return geo_result
        room_map = world_graph.group_furniture_by_room()
        anchor_lower = anchor_cat.lower()
        room_match = any(anchor_lower in r.lower() for r in room_map)
        return GroundingResult(
            proposal, room_match, int(room_match),
            "" if room_match else f"room {anchor_cat!r} not in scene"
        )

    # Find anchor furniture
    anchors = _find_furniture_by_category(world_graph, anchor_cat)
    if not anchors:
        return GroundingResult(proposal, False, 0,
                               f"no furniture matching {anchor_cat!r} found")

    partnr_rel = _partnr_relation(relation)
    if partnr_rel is None:
        return GroundingResult(proposal, False, 0,
                               f"unsupported relationship {relation!r}")

    spatial_relation, spatial_constraint = partnr_rel

    # Try sampling a placement on each anchor furniture.
    # First success → accepted.
    total_positions = 0
    for anchor in anchors:
        try:
            positions = anchor.sample_place_location(
                spatial_relation=spatial_relation,
                spatial_constraint=spatial_constraint,
                reference_object=None,
                env=env,
                agent=agent,
                grasp_mgr=grasp_mgr,
            )
        except Exception:
            positions = []
        total_positions += len(positions)
        if positions:
            return GroundingResult(proposal, True, len(positions), "")

    return GroundingResult(
        proposal, False, 0,
        f"no valid placement for {obj_cat!r} {relation!r} {anchor_cat!r}"
    )


# ---------------------------------------------------------------------------
# Batch grounder with survival-rate instrumentation
# ---------------------------------------------------------------------------

def ground_displacement_batch(
    proposals: list[dict],
    world_graph: "WorldGraph",
    env,
    agent,
    grasp_mgr=None,
    stats: GroundingStats | None = None,
    scene_id: Optional[str] = None,
) -> tuple[list[dict], GroundingStats]:
    """Ground all proposals, returning (accepted_proposals, stats).

    Accumulates stats into the provided GroundingStats (or creates a new one).
    Stats are the empirical model-selection metric — log them per model.

    Args:
        proposals: List of raw displacement proposals from the generation stage.
        stats:     Existing GroundingStats to accumulate into (for cross-scene totals).
        scene_id:  Passed through to ground_proposal for geometry-based in_region
                   validation; see ground_proposal's docstring.

    Returns:
        (accepted, stats) — accepted is the subset that passed grounding.
    """
    if stats is None:
        stats = GroundingStats()

    accepted: list[dict] = []
    for prop in proposals:
        stats.total += 1
        result = ground_proposal(prop, world_graph, env, agent, grasp_mgr, scene_id=scene_id)
        if result.accepted:
            stats.accepted += 1
            accepted.append(prop)
        else:
            reason = result.reason
            if "no " + prop.get("object_category", "") + " found" in reason:
                stats.no_object_in_scene += 1
                stats.log_rejected_category(prop.get("object_category", ""))
            elif "no furniture" in reason or "room" in reason and "not in scene" in reason:
                stats.no_anchor_in_scene += 1
            elif "no valid placement" in reason:
                stats.no_valid_placement += 1
            elif "unsupported relationship" in reason:
                stats.unsupported_relation += 1

    return accepted, stats


# ---------------------------------------------------------------------------
# Standalone (no sim) fallback — semantic plausibility check
# ---------------------------------------------------------------------------

def ground_proposal_semantic(
    proposal: dict,
    inventory: dict[str, int],
    scene_regions: Optional["SceneRegions"] = None,
    anchor_inventory: Optional[dict[str, int]] = None,
    anchor_census: Optional[dict] = None,
) -> GroundingResult:
    """Lightweight semantic grounding when PARTNR sim is unavailable.

    Checks:
      1. Object category exists in scene inventory (count > 0).
      2. Relationship string is in the supported set.
      3. For in_region (legacy manifests/caches only — no longer emittable,
         see schemas.REGION_ONLY_RELATIONSHIPS): anchor matches a real
         region in this scene.
      4. For everything else, WITH an anchor census (Part A, the live
         path): the anchor must be a census instance label present in this
         scene's census — and for a surface relation (on/on_top/inside/
         within) it must have >= 1 active receptacle. This is the
         "generation and grounding consistent by construction" property:
         both sides now read the same census views
         (env/anchor_census.py), so a schema-emittable anchor is
         grounding-acceptable by definition and anything else (a legacy
         cache replayed against new code, a hand-edited generation_result)
         is rejected loudly.
      5. WITHOUT a census (legacy fallback): anchor matches a real
         furniture category present in this scene (anchor_inventory), as
         before. anchor_inventory=None preserves the old permissive
         behaviour for callers that pass neither.

    This is not a physics simulation — it does not check collision, reachability,
    or placement feasibility. Use for quick iteration without Habitat-sim.
    Always run full sim-based grounding before committing to the dataset.
    """
    from .schemas import PARTNR_RELATIONSHIPS, SURFACE_RELATIONSHIPS
    from .regions import anchor_matches_region

    obj_cat  = proposal.get("object_category", "")
    relation = proposal.get("target_relationship", "")
    anchor   = proposal.get("target_anchor", "")

    if inventory.get(obj_cat, 0) < 1:
        return GroundingResult(proposal, False, 0,
                               f"{obj_cat!r} not in scene inventory")
    if relation not in PARTNR_RELATIONSHIPS:
        return GroundingResult(proposal, False, 0,
                               f"unknown relationship {relation!r}")
    if relation in _REGION_ONLY:
        if scene_regions is not None:
            if not anchor_matches_region(anchor, scene_regions):
                return GroundingResult(proposal, False, 0,
                                       f"room {anchor!r} not in scene")
        # If scene_regions is None (no JSON available), accept the proposal —
        # we cannot validate but also cannot reject without data.
    elif anchor_census is not None:
        from ..env.inventory import FLOOR_BOUND_CATEGORIES

        record = anchor_census["anchors"].get(anchor)
        if record is None:
            return GroundingResult(proposal, False, 0,
                                   f"no furniture matching {anchor!r} found in scene census")
        if relation in SURFACE_RELATIONSHIPS and record["active_receptacles"] < 1:
            return GroundingResult(proposal, False, 0,
                                   f"no furniture matching {anchor!r} with an active receptacle "
                                   f"(surface relation {relation!r} on a proximity-only anchor)")
        if relation in SURFACE_RELATIONSHIPS and obj_cat in FLOOR_BOUND_CATEGORIES:
            # Floor-Bound Realization round: defense-in-depth behind
            # generation/pipeline.py's own pre-grounding drop of the same
            # class — a chair/stool never goes ON a surface.
            return GroundingResult(proposal, False, 0,
                                   f"no valid placement for floor-bound {obj_cat!r} "
                                   f"{relation!r} {anchor!r} (floor objects take proximity relations only)")
    else:
        if anchor_inventory is not None:
            if anchor_inventory.get(anchor, 0) < 1:
                return GroundingResult(proposal, False, 0,
                                       f"no furniture matching {anchor!r} found in scene")
        # If anchor_inventory is None (caller didn't pass one), accept —
        # we cannot validate but also cannot reject without data.
    return GroundingResult(proposal, True, 1, "")


def ground_displacement_batch_semantic(
    proposals: list[dict],
    inventory: dict[str, int],
    scene_regions: Optional["SceneRegions"] = None,
    stats: GroundingStats | None = None,
    anchor_inventory: Optional[dict[str, int]] = None,
    anchor_census: Optional[dict] = None,
) -> tuple[list[dict], GroundingStats]:
    """Semantic-only batch grounding — no Habitat-sim required."""
    if stats is None:
        stats = GroundingStats()
    accepted: list[dict] = []
    for prop in proposals:
        stats.total += 1
        result = ground_proposal_semantic(prop, inventory, scene_regions, anchor_inventory, anchor_census)
        if result.accepted:
            stats.accepted += 1
            accepted.append(prop)
        else:
            reason = result.reason
            if "not in scene inventory" in reason:
                stats.no_object_in_scene += 1
                stats.log_rejected_category(prop.get("object_category", ""))
            elif "no furniture matching" in reason or ("room" in reason and "not in scene" in reason):
                stats.no_anchor_in_scene += 1
            elif "unknown relationship" in reason:
                stats.unsupported_relation += 1
    return accepted, stats


# ---------------------------------------------------------------------------
# Update schemas.PARTNR_RELATIONSHIPS from the live PARTNR registry at import
# ---------------------------------------------------------------------------

def _sync_relationship_vocab() -> None:
    """Extend schemas.PARTNR_RELATIONSHIPS with the relationships this module
    knows are valid in PARTNR's spatial-relation system.

    Called at module import so schemas.py stays in sync without circular imports.
    """
    from .schemas import PARTNR_RELATIONSHIPS
    PARTNR_RELATIONSHIPS.update(set(_RELATION_MAP.keys()) | _REGION_ONLY)


_sync_relationship_vocab()


# ---------------------------------------------------------------------------
# State-proposal grounding (M3) — no PARTNR, no geometry: a state-change
# proposal (generation/state_rules.py) only needs (a) its category to be a
# real, present stateful-furniture instance in this scene, and (b) its
# target value to be in that variable's legal domain (env/deltas.py's
# STATE_VARIABLES). Kept in this module because it plays the same *role*
# as the geometry grounding above ("does this proposal correspond to
# something real"), even though the mechanism here is a membership check,
# not a PARTNR placement query — deterministic proposals drawn from the
# same registry that validates them should essentially always pass; this
# is defense-in-depth, not a meaningful survival-rate metric like
# GroundingStats above.
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class StateGroundingResult:
    proposal: dict
    accepted: bool
    reason:   str


def ground_state_proposal(proposal: dict, stateful_categories: set[str]) -> StateGroundingResult:
    """Validate one state-change proposal against this scene's real
    stateful-furniture categories and STATE_VARIABLES's legal domain."""
    from ..env.deltas import STATE_VARIABLES

    category = proposal.get("object_category")
    variable = proposal.get("state_variable")
    target   = proposal.get("target_state")

    if category not in stateful_categories:
        return StateGroundingResult(proposal, False, f"category {category!r} not present in this scene")
    spec = STATE_VARIABLES.get(variable)
    if spec is None:
        return StateGroundingResult(proposal, False, f"unknown state_variable {variable!r}")
    if target not in spec["values"]:
        return StateGroundingResult(proposal, False, f"target_state {target!r} not in {spec['values']}")
    return StateGroundingResult(proposal, True, "")


def ground_state_proposal_batch(
    proposals: list[dict], stateful_categories: set[str],
) -> tuple[list[dict], list[StateGroundingResult]]:
    """Batch form: (accepted proposals, every proposal's grounding result —
    including rejections, for diagnostics)."""
    results = [ground_state_proposal(p, stateful_categories) for p in proposals]
    accepted = [r.proposal for r in results if r.accepted]
    return accepted, results
