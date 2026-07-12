"""
topdown_map.py — habitat-sim top-down occupancy map + world<->pixel
projection, and the anchor-sanity check it enables.

Loads an HSSD scene into a minimal, sensorless, renderer-less habitat_sim
Simulator (navmesh/pathfinder only — no GPU rendering needed to build the
occupancy grid), computes its navmesh if not pre-baked, and exposes both the
top-down grid and the exact world<->pixel transform used to build it. This
is the module the embodied-agent phase's M0 trace-diff test imports; the
CLI that turns this into an actual rendered animation is
scripts/render_topdown.py.

Requires habitat_sim (available in the dynamic_eqa conda env — see the
README's Environment section).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from dynamic_home_eqa.paths import HSSD_DIR
_DATASET_CONFIG = f"{HSSD_DIR}/hssd-hab-uncluttered.scene_dataset_config.json"


@dataclass
class TopdownMap:
    """A scene's top-down occupancy grid plus the transform used to build it.

    grid[row, col] is True where navigable. world_to_pixel()/is_navigable_at()
    use the identical (bounds_min, meters_per_pixel) transform habitat_sim's
    own PathFinder.get_topdown_view used to build `grid` — verified directly
    against real navigable points (get_random_navigable_point → project →
    check the same cell reads True), not assumed from documentation, since
    get_topdown_view's exact pixel convention isn't spelled out in the API.
    """
    grid: np.ndarray
    meters_per_pixel: float
    bounds_min: np.ndarray
    bounds_max: np.ndarray
    height: float

    def world_to_pixel(self, x: float, z: float) -> tuple[int, int]:
        row = int((z - self.bounds_min[2]) / self.meters_per_pixel)
        col = int((x - self.bounds_min[0]) / self.meters_per_pixel)
        return row, col

    def is_in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.grid.shape[0] and 0 <= col < self.grid.shape[1]

    def is_navigable_at(self, x: float, z: float, radius_px: int = 1) -> bool:
        """True if (x, z) projects to a navigable cell, or within radius_px
        pixels of one — an anchor sitting flush against a wall or inside a
        furniture footprint can legitimately land just outside the navmesh
        boundary, so an exact single-cell match is too strict a bar."""
        row, col = self.world_to_pixel(x, z)
        if not self.is_in_bounds(row, col):
            return False
        r0, r1 = max(0, row - radius_px), min(self.grid.shape[0], row + radius_px + 1)
        c0, c1 = max(0, col - radius_px), min(self.grid.shape[1], col + radius_px + 1)
        return bool(self.grid[r0:r1, c0:c1].any())


def load_topdown_map(scene_id: str, meters_per_pixel: float = 0.05) -> TopdownMap:
    """Load `scene_id` (HSSD scenes-uncluttered variant) and compute its
    top-down occupancy map. No GPU rendering: create_renderer=False and no
    sensors are attached, so this only needs the stage mesh + navmesh, not a
    display or EGL context."""
    import habitat_sim

    backend_cfg = habitat_sim.SimulatorConfiguration()
    backend_cfg.scene_dataset_config_file = _DATASET_CONFIG
    backend_cfg.scene_id = scene_id
    backend_cfg.enable_physics = False
    backend_cfg.create_renderer = False

    agent_cfg = habitat_sim.agent.AgentConfiguration()
    agent_cfg.sensor_specifications = []

    sim = habitat_sim.Simulator(habitat_sim.Configuration(backend_cfg, [agent_cfg]))
    try:
        if not sim.pathfinder.is_loaded:
            sim.recompute_navmesh(sim.pathfinder, habitat_sim.NavMeshSettings())
        bounds_min, bounds_max = sim.pathfinder.get_bounds()
        height = float(bounds_min[1]) + 0.1
        grid = np.array(sim.pathfinder.get_topdown_view(
            meters_per_pixel=meters_per_pixel, height=height,
        ))
    finally:
        sim.close()

    return TopdownMap(
        grid=grid, meters_per_pixel=meters_per_pixel,
        bounds_min=np.array(bounds_min), bounds_max=np.array(bounds_max),
        height=height,
    )


# ---------------------------------------------------------------------------
# Per-scene anchor/room world positions
# ---------------------------------------------------------------------------

def anchor_world_positions(scene_id: str) -> dict[str, tuple[float, float, float]]:
    """{slot_name: (x, y, z)} for every SLOT_ANCHORS entry with at least one
    matching real instance in this scene, plus one entry per present
    STATEFUL_FURNITURE category keyed by its own bare category name (M3:
    state-change dynamics — e.g. "fridge") — its real surveyed position,
    not the room-centroid fallback embodied/world.py's
    _resolve_slot_position falls back to for an anchor absent here. Without
    this, embodied/sensor.py's viewpoint_for("fridge") (needed to resense a
    state variable — see posterior.PosteriorBeliefStore's resense_anchors)
    has no real position to sample viewpoints around at all.

    A slot whose category has no matching instance here is omitted, not
    given a fabricated position — this is a per-scene view, and not every
    scene has every slot's furniture category. Uses the same real per-scene
    census generation/manifest.py's slot resolution is built from (Tier 1
    furniture census + Tier 2a instance positions), so a slot's projected
    position here is the same real object the Change-log claims it's
    anchored to, not an independent guess.
    """
    from .env.deltas import SLOT_ANCHORS
    from .env.inventory import STATEFUL_FURNITURE, load_furniture_census, load_scene_state

    positions_by_cat: dict[str, list[tuple]] = {
        cat: list(positions) for cat, positions in load_furniture_census(scene_id).items()
    }
    for inst in load_scene_state(scene_id).instances.values():
        if inst.position is not None:
            positions_by_cat.setdefault(inst.category, []).append(inst.position)

    out: dict[str, tuple[float, float, float]] = {}
    for slot, spec in SLOT_ANCHORS.items():
        for cat in spec.get("cats", []):
            positions = positions_by_cat.get(cat)
            if positions:
                out[slot] = positions[0]  # first in census order — deterministic
                break

    for cat in STATEFUL_FURNITURE:
        positions = positions_by_cat.get(cat)
        if positions:
            out[cat] = positions[0]

    for room, cats in instance_room_positions(scene_id).items():
        for cat, positions in cats.items():
            key = f"{room}.{cat}"
            if key not in out:  # SLOT_ANCHORS entries (legacy naming, e.g. "dining.table") take priority
                out[key] = positions[0]
    return out


def instance_room_positions(scene_id: str) -> dict[str, dict[str, list[tuple[float, float, float]]]]:
    """{room: {category: [positions]}} — every real HSSD furniture/native-
    clutter instance (TIER1_FURNITURE anchors + TIER2_HSSD_NATIVE movable
    clutter), room-tagged via the SAME geometric point-in-region test +
    foundIn-tag eligibility gate generation/inventory.py's
    room_inventory_from_scene_state already established (reused here, not
    reimplemented) — the only difference is this keeps each instance's
    real POSITION instead of collapsing straight to a count.

    Built for rooms.resolve_slot()'s census-grounded fallback (Realized
    World Phase round 2): resolve_slot() needs to know not just "does a
    table exist somewhere in this scene" (env/inventory.py's scene-wide
    anchor_inventory, room-blind by construction) but "does a table exist
    IN THIS SPECIFIC ROOM" — no existing function joined per-instance
    position with room before this; anchor_world_positions (above) itself
    now calls this to populate room-qualified keys beyond the 16
    hand-authored SLOT_ANCHORS entries.

    room keys are rooms.CANONICAL_ROOMS names (matching what
    resolve_slot's own `room` parameter actually receives — see
    generation/schemas.py's ACTIVITY_LOCATIONS), not raw HSSD region
    strings (region.normalised) — the canonical-room match happens here,
    once, rather than pushed onto every caller."""
    from .env.inventory import TIER2_HSSD_NATIVE, found_in_rooms, load_furniture_census, load_scene_state
    from .generation.regions import load_scene_regions, region_for_point
    from .rooms import CANONICAL_ROOMS, rooms_match

    scene_regions = load_scene_regions(scene_id)
    if scene_regions is None:
        return {}

    positions_by_cat: dict[str, list[tuple]] = {
        cat: list(positions) for cat, positions in load_furniture_census(scene_id).items()
    }
    for inst in load_scene_state(scene_id).instances.values():
        if inst.position is not None and inst.category in TIER2_HSSD_NATIVE:
            positions_by_cat.setdefault(inst.category, []).append(inst.position)

    out: dict[str, dict[str, list[tuple]]] = {}
    for cat, positions in positions_by_cat.items():
        tags = found_in_rooms(cat)
        for pos in positions:
            region = region_for_point(pos, scene_regions)
            if region is None:
                continue
            if tags and not any(rooms_match(region.normalised, t) for t in tags):
                continue  # geometry/foundIn-tag disagree — the same coarse-region-boundary false positive room_inventory_from_scene_state guards against
            room = next((r for r in CANONICAL_ROOMS if rooms_match(region.normalised, r)), None)
            if room is None:
                continue
            out.setdefault(room, {}).setdefault(cat, []).append(pos)
    return out


def room_centroids(scene_id: str) -> dict[str, tuple[float, float]]:
    """{canonical_room: (x, z)} centroid for each of rooms.CANONICAL_ROOMS
    this scene has a matching real HSSD region for (via rooms.rooms_match).
    Used to place occupant markers at a representative point for whatever
    room their current activity says they're in — the activity trace only
    names a room, not a position, so this is the position source.

    Picks the LARGEST (by XZ bounding-box area) matching region's own
    bounding-box center — not the mean across all matching regions. HSSD
    scenes can be multi-story (confirmed on real scenes: e.g. "bedroom"
    matching regions on both floor_height=0.0 and floor_height=2.5), and
    averaging bounding-box centers across different floors produces a
    centroid at neither real room's location — often not even navigable.
    Picking one real region's own center, the same tie-break
    anchor_world_positions already uses for multiple real instances of a
    category, guarantees the result is always an actual point inside a
    real room.
    """
    from .generation.regions import load_scene_regions
    from .rooms import CANONICAL_ROOMS, rooms_match

    scene_regions = load_scene_regions(scene_id)
    if scene_regions is None:
        return {}

    def _area(r) -> float:
        return (r.max_bounds[0] - r.min_bounds[0]) * (r.max_bounds[2] - r.min_bounds[2])

    out: dict[str, tuple[float, float]] = {}
    for room in CANONICAL_ROOMS:
        matches = [r for r in scene_regions.regions if rooms_match(r.normalised, room)]
        if not matches:
            continue
        largest = max(matches, key=_area)
        out[room] = (
            float((largest.min_bounds[0] + largest.max_bounds[0]) / 2),
            float((largest.min_bounds[2] + largest.max_bounds[2]) / 2),
        )
    return out


# ---------------------------------------------------------------------------
# Anchor-sanity check
# ---------------------------------------------------------------------------

@dataclass
class AnchorSanityResult:
    checked: int
    offenders: list[str]  # slot names that failed the navigable-adjacency check

    @property
    def ok(self) -> bool:
        return not self.offenders

    def summary(self) -> str:
        return f"{self.checked - len(self.offenders)}/{self.checked} anchors land on/near navigable space"


def check_anchor_sanity(
    scene_id: str,
    topdown: Optional[TopdownMap] = None,
    radius_px: int = 2,
) -> AnchorSanityResult:
    """Every SLOT_ANCHORS position resolvable in this scene must land on or
    adjacent to navigable space in the top-down map. A failure here means
    either the anchor's real-instance position is wrong, or it sits deep
    enough inside furniture footprint that no nearby navmesh cell exists —
    either way, worth knowing before trusting a render or a downstream
    placement decision built on this same position data. This check never
    existed before this module.
    """
    if topdown is None:
        topdown = load_topdown_map(scene_id)
    positions = anchor_world_positions(scene_id)
    offenders = [
        slot for slot, (x, _, z) in positions.items()
        if not topdown.is_navigable_at(x, z, radius_px=radius_px)
    ]
    return AnchorSanityResult(checked=len(positions), offenders=offenders)
