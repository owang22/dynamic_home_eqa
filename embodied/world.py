"""
world.py — EmbodiedWorld: replay + geometry oracle + sensor.

Objects are NOT physically instantiated in habitat_sim. The authoritative
object state is the same manifest.json Change-log the trace-integrity phase
already validates (chain-consistent, insert-once, no no-ops, every event
attended) — this module replays it with env.replay.state_at, the identical
trusted replay every other manifest consumer uses. habitat_sim provides
geometry services only:
  - navmesh: geodesic distance / path following / pose snapping.
  - occlusion: ray casting against the stage's Bullet collision mesh
    (enable_physics=True, create_renderer=False — no GPU rendering; see
    sensor.py's module docstring for why enable_physics is required).

The scene's navmesh can still be fragmented into disconnected islands after
NavMeshConfig's climb fix, and this is not always a small-pocket artifact to
paper over. The navmesh-connectivity phase's D0 diagnostic (see
scripts/diagnose_navmesh_islands.py) revised an earlier, wrong assumption
here: scene 102343992 is NOT a two-floor house missing modeled stairs — the
y=2.6-3.8 m islands that looked like a second floor are ~0% indoor (roof/
exterior), and the real fragmentation (kitchen / living-room-furniture /
office-bedroom-bathroom / etc. landing on separate islands) was recast
pinching off ordinary ground-floor doorways: near-touch gaps of ~0.4 m
horizontal, up to 0.4 m vertical, between islands that were otherwise both
indoor. Raising agent_max_climb to 0.4 (config.NavMeshConfig) merges all of
that into one connected interior. One small furniture-cluster island (the
couch/corner/window_sill slots' physical position, ~9 m²) resisted every
navmesh setting tried, including agent radii far narrower than any real
person — treated as a genuinely disconnected fragment (a wall, not a
pinched doorway), not something to force a portal through. Forcing every
position onto one "main" island (tried first, before the climb fix existed)
simply produced NaN snap results for centroids nowhere near it. Instead,
every position is snapped island-agnostically (nearest navigable point on
any island), and geodesic_time() reports float('inf') between genuinely
disconnected points — an honest reflection of "no walkable path", not a bug
to hide. reachability.check_reachability_invariant() is the pre-flight gate
that should catch a scene where this matters before any experiment runs.

Multiple instances resolved to the same anchor or room centroid get a
small deterministic radial offset seeded by label hash (sensor.py) so they
remain individually resolvable — not a claim about their real relative
positions, and never used to model occlusion between them (only stage
geometry occludes, see sensor.py).

Slots that don't resolve to a room in rooms.CANONICAL_ROOMS (outdoor,
anything mapping to "away") have no world position and are outside the
sensable volume by construction — an instance there is simply never
detected, never a "sensed absent", matching the trace contract's own
treatment of away/outdoor as outside the house.
"""
from __future__ import annotations

import math
from typing import Optional

from ..env.deltas import Change
from ..env.replay import initial_state_and_changes_from_manifest, state_at
from ..env.state import SceneState
from ..rooms import slot_room
from ..topdown_map import HSSD_DIR, anchor_world_positions, room_centroids
from .config import AgentConfig
from .sensor import deterministic_radial_offset, detect_visible, viewpoint_for as _viewpoint_for
from .types import ActionResult, Goto, Pose, Rotate, Sense, SenseSnapshot, UnreachableError

_DATASET_CONFIG = f"{HSSD_DIR}/hssd-hab-uncluttered.scene_dataset_config.json"


class EmbodiedWorld:
    def __init__(
        self,
        scene_id: str,
        generation_result: dict,
        manifest: dict,
        config: Optional[AgentConfig] = None,
        day_start: float = 0.0,
    ) -> None:
        self.scene_id = scene_id
        self.generation_result = generation_result
        self.config = config or AgentConfig()

        self.initial_state, self.changes = initial_state_and_changes_from_manifest(manifest)
        self.t = day_start

        self._sim = None
        self._anchor_positions = anchor_world_positions(scene_id)
        self._room_centroids = room_centroids(scene_id)
        self._geodesic_cache: dict[tuple, float] = {}
        self._viewpoint_cache: dict[str, Optional[Pose]] = {}

        self.pose = self._default_pose()

    # -- lifecycle -----------------------------------------------------

    def _ensure_sim(self) -> None:
        if self._sim is not None:
            return
        import habitat_sim

        backend_cfg = habitat_sim.SimulatorConfiguration()
        backend_cfg.scene_dataset_config_file = _DATASET_CONFIG
        backend_cfg.scene_id = self.scene_id
        backend_cfg.enable_physics = True
        backend_cfg.create_renderer = False

        agent_cfg = habitat_sim.agent.AgentConfiguration()
        agent_cfg.sensor_specifications = []

        self._sim = habitat_sim.Simulator(habitat_sim.Configuration(backend_cfg, [agent_cfg]))
        # Always recompute with our own NavMeshConfig, regardless of
        # whether a navmesh happened to load from disk — a pre-baked
        # navmesh carries whatever settings baked it (this scene has none,
        # but relying on that is fragile), and the navmesh-connectivity
        # phase's agent_max_climb=0.4 fix (see config.NavMeshConfig's
        # docstring) must always be the one actually in effect.
        nm = self.config.navmesh
        settings = habitat_sim.NavMeshSettings()
        settings.agent_radius = nm.agent_radius
        settings.agent_height = nm.agent_height
        settings.agent_max_climb = nm.agent_max_climb
        settings.agent_max_slope = nm.agent_max_slope
        settings.cell_size = nm.cell_size
        settings.cell_height = nm.cell_height
        self._sim.recompute_navmesh(self._sim.pathfinder, settings)

        # Drop anchors resolving onto a navmesh island smaller than
        # min_component_area_m2 — a documented, disqualified micro-fragment
        # (see NavMeshConfig's docstring), not part of the connected
        # interior. An object placed at such an anchor could never be
        # sensed by any policy; falling back to the slot's room centroid
        # (_resolve_slot_position) keeps it on the connected interior
        # instead of silently stranding it forever.
        pf = self._sim.pathfinder
        min_area = nm.min_component_area_m2

        def _on_small_island(pos: tuple[float, float, float]) -> bool:
            island = pf.get_island(list(pos))
            return island < 0 or pf.island_area(island) < min_area

        self._anchor_positions = {
            slot: pos for slot, pos in self._anchor_positions.items()
            if not _on_small_island(pos)
        }

    def close(self) -> None:
        if self._sim is not None:
            self._sim.close()
            self._sim = None

    def __enter__(self) -> "EmbodiedWorld":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # -- navmesh / position resolution ----------------------------------

    def snap_to_navmesh(self, point: tuple[float, float, float]) -> tuple[float, float, float]:
        """Nearest navigable point to `point`, on whichever island is
        closest — not constrained to one global island (see module
        docstring: this scene's floors are genuinely disconnected, and
        forcing one island produces NaN snaps for the other floor(s))."""
        self._ensure_sim()
        snapped = self._sim.pathfinder.snap_point(list(point))
        return (float(snapped[0]), float(snapped[1]), float(snapped[2]))

    def _island_indoor_fraction(self, island_id: int, max_samples: int = 60) -> float:
        """Fraction of `island_id`'s navmesh vertices with a ceiling
        overhead (ray cast straight up, no hit within 8 m = open sky —
        same test scripts/diagnose_navmesh_islands.py uses). Distinguishes
        a real interior island from a large outdoor navmesh fragment that
        happens to be the largest by area (confirmed on this scene: before
        the navmesh-connectivity phase's climb fix, the largest-by-area
        island was only 55% indoor — a yard fused to three real rooms)."""
        import habitat_sim
        import magnum as mn

        verts = self._sim.pathfinder.build_navmesh_vertices(island_id)
        if not verts:
            return 0.0
        stride = max(1, len(verts) // max_samples)
        sample = verts[::stride]
        hits = 0
        for v in sample:
            origin = mn.Vector3(float(v[0]), float(v[1]) + 0.05, float(v[2]))
            ray = habitat_sim.geo.Ray(origin, mn.Vector3(0.0, 1.0, 0.0))
            if self._sim.cast_ray(ray, max_distance=8.0).has_hits():
                hits += 1
        return hits / len(sample)

    def _default_pose(self) -> Pose:
        """Start on the room centroid whose navmesh island has the largest
        area among islands clearing config.navmesh.min_indoor_fraction —
        not simply the largest island overall. Raw area cannot distinguish
        a real interior from a large outdoor yard that happens to abut the
        house (confirmed on this scene, see NavMeshConfig's docstring and
        _island_indoor_fraction). Falls back to the largest island overall,
        with a warning, only if no room's island clears the threshold at
        all — should not happen on a scene that passed the reachability
        pre-flight (see reachability.check_reachability_invariant)."""
        self._ensure_sim()
        min_indoor = self.config.navmesh.min_indoor_fraction
        candidates = []
        for room, (x, z) in self._room_centroids.items():
            snapped = self.snap_to_navmesh((x, 0.1, z))
            island = self._sim.pathfinder.get_island(list(snapped))
            area = self._sim.pathfinder.island_area(island) if island >= 0 else 0.0
            indoor_fraction = self._island_indoor_fraction(island) if island >= 0 else 0.0
            candidates.append((area, indoor_fraction, room, snapped))

        qualifying = [c for c in candidates if c[1] >= min_indoor]
        pool = qualifying if qualifying else candidates
        if not qualifying and candidates:
            import warnings
            warnings.warn(
                f"no room centroid's island clears min_indoor_fraction={min_indoor}; "
                f"falling back to largest island overall (best indoor fraction "
                f"{max(c[1] for c in candidates):.2f}) — scene should not have passed "
                f"the reachability pre-flight in this state",
                stacklevel=2,
            )
        if pool:
            _area, _indoor, _room, snapped = max(pool, key=lambda c: c[0])
            return Pose(*snapped, yaw_rad=0.0)
        pt = self._sim.pathfinder.get_random_navigable_point()
        return Pose(float(pt[0]), float(pt[1]), float(pt[2]), 0.0)

    def room_centroid_pose(self, room: str) -> Optional[Pose]:
        """Navmesh-snapped pose at `room`'s centroid, or None if this scene
        has no matching HSSD region for it."""
        if room not in self._room_centroids:
            return None
        x, z = self._room_centroids[room]
        snapped = self.snap_to_navmesh((x, 0.1, z))
        return Pose(*snapped, yaw_rad=0.0)

    def _resolve_slot_position(self, label: str, slot: str) -> Optional[tuple[float, float, float]]:
        """World (x, y, z) for a label currently at `slot`, or None if the
        slot is outside the sensable volume (outdoor/away — no canonical
        room, see module docstring). Prefers a real per-scene anchor
        position; falls back to the slot's room centroid with a small
        deterministic offset so distinct labels sharing a fallback position
        remain individually resolvable."""
        if slot in self._anchor_positions:
            return self._anchor_positions[slot]
        room = slot_room(slot)
        if room is None or room not in self._room_centroids:
            return None
        cx, cz = self._room_centroids[room]
        dx, dz = deterministic_radial_offset(label)
        # 0.5 m: a typical surface height (real anchors in this scene run
        # ~0.37-0.6 m — counters, beds, tables), not floor level. A floor-
        # level fallback (0.1 m) made a generic in_region placement (e.g.
        # bare "bedroom", not tied to a specific real anchor) spuriously
        # "occluded" from its own room's centroid viewpoint far more often
        # than a real anchor ever was in the M1 visibility tests — a steep
        # downward ray from standing eye height to a near-floor point
        # clips ordinary furniture edges that a torso-height ray clears.
        return (cx + dx, 0.5, cz + dz)

    # -- replay -----------------------------------------------------------

    def advance_to(self, t: float) -> None:
        """Advance the clock to t (monotonic — sim time never runs
        backward within an episode). Object state at any queried time is
        derived fresh via env.replay.state_at, not incrementally mutated —
        the trace is small enough (order 100-200 events/day) that a full
        replay per query is microseconds, and re-deriving from the trusted
        replay function is simpler to get right than hand-rolled
        incremental application of the same events."""
        self.t = max(self.t, t)

    def current_instances(self) -> dict[str, tuple[str, str]]:
        """{label: (category, current_semantic_slot)} at self.t."""
        state = state_at(self.initial_state, self.changes, self.t)
        return {iid: (inst.category, inst.current_semantic) for iid, inst in state.instances.items()}

    def current_instance_states(self) -> dict[str, dict[str, str]]:
        """{label: {state_variable: value}} at self.t (M3: state-change
        dynamics) — only labels with a non-empty `states` dict are
        included (see env/inventory.py's STATEFUL_FURNITURE seeding).
        Separate from current_instances() rather than folded into its
        2-tuple return so every existing (category, slot)-unpacking caller
        stays unchanged."""
        state = state_at(self.initial_state, self.changes, self.t)
        return {iid: dict(inst.states) for iid, inst in state.instances.items() if inst.states}

    def instance_world_position(self, label: str) -> Optional[tuple[float, float, float]]:
        instances = self.current_instances()
        if label not in instances:
            return None
        _, slot = instances[label]
        return self._resolve_slot_position(label, slot)

    # -- geodesic distance / viewpoints -----------------------------------

    def geodesic_time(self, a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
        """Shortest-path travel time in seconds between two world points
        (walk_speed_mps-scaled), cached per (rounded) endpoint pair.
        float('inf') if no path exists (e.g. disconnected islands — should
        not happen for points already snapped to the main island)."""
        key = (
            round(a[0], 2), round(a[1], 2), round(a[2], 2),
            round(b[0], 2), round(b[1], 2), round(b[2], 2),
        )
        if key in self._geodesic_cache:
            return self._geodesic_cache[key]
        self._ensure_sim()
        import habitat_sim

        path = habitat_sim.ShortestPath()
        path.requested_start = list(a)
        path.requested_end = list(b)
        found = self._sim.pathfinder.find_path(path)
        dist = path.geodesic_distance if found else float("inf")
        seconds = dist / self.config.motion.walk_speed_mps
        self._geodesic_cache[key] = seconds
        return seconds

    def viewpoint_for(self, anchor: str) -> Optional[Pose]:
        """Cached standing pose from which `anchor` passes the visibility
        test — see sensor.viewpoint_for."""
        if anchor not in self._viewpoint_cache:
            self._ensure_sim()
            self._viewpoint_cache[anchor] = _viewpoint_for(self, anchor)
        return self._viewpoint_cache[anchor]

    # -- actions -----------------------------------------------------------

    def execute(self, action) -> ActionResult:
        self._ensure_sim()
        if isinstance(action, Sense):
            snap = self._sense_here(cost_seconds=self.config.motion.sense_duration_s)
            return ActionResult(self.t, self.pose, (snap,))
        if isinstance(action, Rotate):
            return self._do_rotate(action)
        if isinstance(action, Goto):
            return self._do_goto(action)
        raise TypeError(f"unknown action {action!r}")

    def _sense_here(self, cost_seconds: float) -> SenseSnapshot:
        # Apply the time cost BEFORE detecting, so every OracleDetection's
        # own .t agrees exactly with the returned snapshot's .t (and with
        # self.t immediately after this call). Detecting first and
        # incrementing after made a detection's timestamp systematically
        # earlier than the snapshot/self.t that contains it — a real bug
        # found via a runaway policy loop: a "did I just observe this
        # label" check comparing timestamps never matched, so
        # AlwaysResense/DecayThreshold/DecayVoi kept re-issuing the same
        # resense plan forever (confirmed: a smoke test run this way grew
        # to 6.6 hours and 162 GB of RAM before being killed).
        self.t += cost_seconds / 3600.0
        detections = detect_visible(self, self.pose)
        return SenseSnapshot(self.t, self.pose, detections)

    def _do_rotate(self, action: Rotate) -> ActionResult:
        turn_seconds = abs(action.delta_yaw_rad) * (180.0 / math.pi) / self.config.motion.turn_speed_dps
        self.t += turn_seconds / 3600.0
        new_yaw = (self.pose.yaw_rad + action.delta_yaw_rad) % (2 * math.pi)
        self.pose = Pose(self.pose.x, self.pose.y, self.pose.z, new_yaw)
        snap = self._sense_here(cost_seconds=self.config.motion.sense_duration_s)
        return ActionResult(self.t, self.pose, (snap,))

    def _do_goto(self, action: Goto) -> ActionResult:
        import habitat_sim

        start = self.pose.position
        target = self.snap_to_navmesh(action.target)

        path = habitat_sim.ShortestPath()
        path.requested_start = list(start)
        path.requested_end = list(target)
        found = self._sim.pathfinder.find_path(path)
        if not found or len(path.points) < 2:
            raise UnreachableError(
                f"no navmesh path from {start} to {target} (different island? "
                f"see types.UnreachableError's docstring)"
            )
        waypoints = list(path.points)

        snapshots: list[SenseSnapshot] = []
        cadence = self.config.motion.sense_cadence_m
        walk_speed = self.config.motion.walk_speed_mps
        traveled_since_sense = 0.0

        for i in range(len(waypoints) - 1):
            p0, p1 = waypoints[i], waypoints[i + 1]
            seg = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
            seg_len = (seg[0] ** 2 + seg[1] ** 2 + seg[2] ** 2) ** 0.5
            if seg_len < 1e-9:
                continue
            direction = (seg[0] / seg_len, seg[1] / seg_len, seg[2] / seg_len)
            yaw = math.atan2(direction[2], direction[0])
            traveled = 0.0
            while traveled < seg_len - 1e-9:
                step = min(cadence - traveled_since_sense, seg_len - traveled)
                traveled += step
                traveled_since_sense += step
                pos = (p0[0] + direction[0] * traveled,
                       p0[1] + direction[1] * traveled,
                       p0[2] + direction[2] * traveled)
                self.t += (step / walk_speed) / 3600.0
                self.pose = Pose(pos[0], pos[1], pos[2], yaw)
                if traveled_since_sense >= cadence - 1e-9:
                    # En-route glances are free (already moving, no
                    # separate "stop and look" cost) — only Sense()/Rotate()
                    # and the final arrival snapshot cost sense_duration_s.
                    snapshots.append(self._sense_here(cost_seconds=0.0))
                    traveled_since_sense = 0.0

        final_yaw = action.face_yaw_rad if action.face_yaw_rad is not None else self.pose.yaw_rad
        self.pose = Pose(target[0], target[1], target[2], final_yaw)
        snapshots.append(self._sense_here(cost_seconds=self.config.motion.sense_duration_s))
        return ActionResult(self.t, self.pose, tuple(snapshots))
