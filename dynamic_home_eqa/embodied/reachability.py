"""
reachability.py — scene-qualification pre-flight for the embodied-agent
phase.

Verifies every canonical room centroid and every hand-authored anchor this
scene resolves shares one connected navmesh component with the agent's
selected start pose, under the configured NavMeshConfig. This is the
invariant the navmesh-connectivity phase exists to add: the M1 gate's 80%
abstain rate (identical across all six policies) was this exact failure
mode going undetected until an experiment was already running — 4 of 5
patrol-time frozen labels sat on islands the start pose could never reach.
Scenes that fail this check should be rejected before any generation or
experiment touches them, not discovered mid-experiment.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .config import NavMeshConfig
from .islands import is_reachable_island
from .sensor import assert_enable_physics, raycast_self_test
from ..topdown_map import HSSD_DIR, anchor_world_positions, room_centroids

_DATASET_CONFIG = f"{HSSD_DIR}/hssd-hab-uncluttered.scene_dataset_config.json"
_CEILING_RAY_MAX_M = 8.0


@dataclass
class ReachabilityResult:
    scene_id: str
    start_room: str
    start_island: int
    checked: int
    unreachable: list[str] = field(default_factory=list)  # "room:<name>" / "anchor:<slot>"
    # Rooms/anchors sitting on an island below navmesh.min_component_area_m2
    # — documented, disqualified micro-fragments (see NavMeshConfig's
    # docstring), not counted against `checked`/`unreachable` since
    # world.EmbodiedWorld filters these out of _anchor_positions itself
    # (an object there always falls back to its room centroid instead).
    excluded_small_fragment: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.unreachable

    def summary(self) -> str:
        base = (f"{self.checked - len(self.unreachable)}/{self.checked} rooms+anchors "
                f"reachable from start room '{self.start_room}' (island {self.start_island})")
        if self.excluded_small_fragment:
            base += f"; {len(self.excluded_small_fragment)} excluded as sub-threshold fragments"
        return base


def make_sim(scene_id: str, navmesh: NavMeshConfig):
    import habitat_sim

    backend_cfg = habitat_sim.SimulatorConfiguration()
    backend_cfg.scene_dataset_config_file = _DATASET_CONFIG
    backend_cfg.scene_id = scene_id
    backend_cfg.enable_physics = True
    backend_cfg.create_renderer = False
    assert_enable_physics(backend_cfg)

    agent_cfg = habitat_sim.agent.AgentConfiguration()
    agent_cfg.sensor_specifications = []
    sim = habitat_sim.Simulator(habitat_sim.Configuration(backend_cfg, [agent_cfg]))

    settings = habitat_sim.NavMeshSettings()
    settings.agent_radius = navmesh.agent_radius
    settings.agent_height = navmesh.agent_height
    settings.agent_max_climb = navmesh.agent_max_climb
    settings.agent_max_slope = navmesh.agent_max_slope
    settings.cell_size = navmesh.cell_size
    settings.cell_height = navmesh.cell_height
    sim.recompute_navmesh(sim.pathfinder, settings)
    raycast_self_test(sim)
    return sim


def _indoor_fraction(sim, island_id: int, max_samples: int = 60) -> float:
    import habitat_sim
    import magnum as mn

    verts = sim.pathfinder.build_navmesh_vertices(island_id)
    if not verts:
        return 0.0
    stride = max(1, len(verts) // max_samples)
    sample = verts[::stride]
    hits = 0
    for v in sample:
        origin = mn.Vector3(float(v[0]), float(v[1]) + 0.05, float(v[2]))
        ray = habitat_sim.geo.Ray(origin, mn.Vector3(0.0, 1.0, 0.0))
        if sim.cast_ray(ray, max_distance=_CEILING_RAY_MAX_M).has_hits():
            hits += 1
    return hits / len(sample)


def _select_start(sim, scene_id: str, navmesh: NavMeshConfig):
    """Same rule as world.EmbodiedWorld._default_pose: largest-area island
    among those clearing min_indoor_fraction, falling back to largest
    overall if none qualify."""
    pf = sim.pathfinder
    centroids = room_centroids(scene_id)
    candidates = []
    for room, (x, z) in centroids.items():
        snapped = pf.snap_point([x, 0.1, z])
        island = pf.get_island(list(snapped))
        area = pf.island_area(island) if island >= 0 else 0.0
        indoor = _indoor_fraction(sim, island) if island >= 0 else 0.0
        candidates.append((area, indoor, room, snapped, island))
    if not candidates:
        return None
    qualifying = [c for c in candidates if c[1] >= navmesh.min_indoor_fraction]
    pool = qualifying if qualifying else candidates
    return max(pool, key=lambda c: c[0])


def check_reachability_invariant(
    scene_id: str, navmesh: NavMeshConfig = NavMeshConfig(),
) -> ReachabilityResult:
    """Run the pre-flight: every room centroid and anchor must be
    pairwise-reachable (finite geodesic path) from the agent's selected
    start pose. Call this once per scene before generation or an
    experiment sweep, not per-episode — it re-derives the same navmesh
    every EmbodiedWorld instance would build, so a scene that fails here
    would fail identically, silently, inside every episode."""
    import habitat_sim

    sim = make_sim(scene_id, navmesh)
    try:
        pf = sim.pathfinder
        selected = _select_start(sim, scene_id, navmesh)
        if selected is None:
            return ReachabilityResult(scene_id, start_room="<none>", start_island=-1, checked=0)
        _area, _indoor, start_room, start_pos, start_island = selected

        centroids = room_centroids(scene_id)
        anchors = anchor_world_positions(scene_id)

        unreachable: list[str] = []
        excluded: list[str] = []
        checked = 0
        for room, (x, z) in centroids.items():
            pos3 = (x, 0.1, z)
            if not is_reachable_island(pf, pos3, navmesh.min_component_area_m2, snap_first=True):
                excluded.append(f"room:{room}")
                continue
            checked += 1
            snapped = pf.snap_point(list(pos3))
            path = habitat_sim.ShortestPath()
            path.requested_start = list(start_pos)
            path.requested_end = list(snapped)
            if not pf.find_path(path):
                unreachable.append(f"room:{room}")
        for slot, pos in anchors.items():
            if not is_reachable_island(pf, pos, navmesh.min_component_area_m2, snap_first=True):
                excluded.append(f"anchor:{slot}")
                continue
            checked += 1
            snapped = pf.snap_point(list(pos))
            path = habitat_sim.ShortestPath()
            path.requested_start = list(start_pos)
            path.requested_end = list(snapped)
            if not pf.find_path(path):
                unreachable.append(f"anchor:{slot}")

        return ReachabilityResult(
            scene_id=scene_id, start_room=start_room, start_island=start_island,
            checked=checked, unreachable=unreachable, excluded_small_fragment=excluded,
        )
    finally:
        sim.close()
