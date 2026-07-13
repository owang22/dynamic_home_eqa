"""
sensor.py — visibility oracle: is a world position observable from an
agent's eye given heading, field of view, range, and scene geometry
occlusion; and viewpoint_for(), which finds a standing pose from which a
given anchor is visible.

habitat_sim is used purely as a geometry oracle here (see embodied/'s module
docstring): occlusion is a ray cast against the scene's Bullet collision
mesh (requires `enable_physics=True` in the Simulator config — confirmed
empirically that `enable_physics=False` makes cast_ray a silent no-op
against this stage geometry, i.e. it never reports a hit even for a ray
that must cross a wall; enable_physics=True fixes this and needs no
renderer/GPU/display context). If this ever regresses on a future
habitat_sim version, the documented fallback is a 2D line-of-sight test on
topdown_map's occupancy grid — do not silently swap to it; raise instead so
the regression is visible.

Two things are deliberately not modeled, per the embodied-agent phase's
design decision that habitat_sim provides geometry only:
  - inter-object occlusion: only stage/scene geometry blocks a ray, never
    another tracked instance. Two instances can never occlude each other.
  - multiple instances resolved to the same anchor collide at the exact
    same world position unless given distinct offsets — see world.py's
    _resolve_slot_position, which applies a small deterministic radial
    offset seeded by the label's hash so distinct instances at a shared
    anchor are still individually resolvable. That offset exists for
    resolvability, not to model real object occlusion.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from .config import SensorConfig
from .types import Pose

if TYPE_CHECKING:
    from .world import EmbodiedWorld


def assert_enable_physics(backend_cfg) -> None:
    """Raise loudly if `backend_cfg` was not built with enable_physics=True.
    cast_ray silently no-ops without it (see module docstring) — every
    occlusion/visibility check downstream would then report "unoccluded"
    for everything, without ever failing a single assertion. Call this
    right before constructing any Simulator whose cast_ray result feeds a
    visibility/occlusion/placement decision."""
    if not backend_cfg.enable_physics:
        raise RuntimeError(
            "Simulator config has enable_physics=False — cast_ray would "
            "silently no-op against this stage's collision mesh, making "
            "every occlusion/visibility check meaningless. Set "
            "backend_cfg.enable_physics = True before constructing."
        )


_RAYCAST_SELF_TEST_SAMPLES = 5


def raycast_self_test(sim) -> None:
    """Backstop check that cast_ray is actually seeing real collision
    geometry, not just configured to try: from 1.0 m above a
    navmesh-snapped point, cast straight down and require a hit landing
    within [0.8, 1.3] m. A working raycast over a real navmesh point
    should hit the floor almost exactly 1.0 m down; a wider miss or no hit
    at all means the collision mesh isn't loaded/aligned even though
    enable_physics=True was set (e.g. dataset/stage mismatch).

    Samples _RAYCAST_SELF_TEST_SAMPLES random navmesh points and passes if
    ANY one of them lands in-band — confirmed directly (not assumed) that
    a single sample is too flaky to gate construction on: on one real
    scene (102344280), ~20% of get_random_navigable_point() draws land
    under low-clearance overhanging geometry (a real navmesh-generation
    quality wrinkle, not a broken sim — the agent can still stand there),
    hitting well short of 1.0 m. A single unlucky draw must not block
    EmbodiedWorld construction for a scene whose raycasting is otherwise
    completely healthy; only "every sample fails" is the actual
    enable_physics/wrong-stage regression this test exists to catch."""
    import habitat_sim
    import magnum as mn

    failures = []
    for _ in range(_RAYCAST_SELF_TEST_SAMPLES):
        point = sim.pathfinder.get_random_navigable_point()
        origin = mn.Vector3(float(point[0]), float(point[1]) + 1.0, float(point[2]))
        ray = habitat_sim.geo.Ray(origin, mn.Vector3(0.0, -1.0, 0.0))
        result = sim.cast_ray(ray, max_distance=2.0)
        if not result.has_hits():
            failures.append("no hit")
            continue
        dist = result.hits[0].ray_distance
        if 0.8 <= dist <= 1.3:
            return  # at least one clean sample -- raycasting works
        failures.append(f"{dist:.3f} m")

    raise RuntimeError(
        f"raycast self-test failed: none of {_RAYCAST_SELF_TEST_SAMPLES} "
        f"straight-down probes from 1.0 m above a navmesh-snapped point "
        f"landed in the expected [0.8, 1.3] m band (results: {failures}) — "
        f"cast_ray is not seeing real collision geometry on this sim "
        f"(enable_physics misconfigured or the wrong stage loaded)."
    )


def _angle_diff(a: float, b: float) -> float:
    """Smallest signed difference a-b, wrapped to [-pi, pi]."""
    return (a - b + math.pi) % (2 * math.pi) - math.pi


def in_fov(eye_pos: tuple, yaw_rad: float, target_pos: tuple, fov_deg: float) -> bool:
    """True if target_pos is within the horizontal FOV cone from eye_pos
    facing yaw_rad (XZ ground plane, 0 = +X axis, atan2(z, x) convention —
    same as Pose.yaw_rad)."""
    dx = target_pos[0] - eye_pos[0]
    dz = target_pos[2] - eye_pos[2]
    if dx == 0.0 and dz == 0.0:
        return True
    bearing = math.atan2(dz, dx)
    return abs(_angle_diff(bearing, yaw_rad)) <= math.radians(fov_deg) / 2.0


def in_range(eye_pos: tuple, target_pos: tuple, max_range_m: float) -> bool:
    dx, dy, dz = (target_pos[i] - eye_pos[i] for i in range(3))
    return (dx * dx + dy * dy + dz * dz) ** 0.5 <= max_range_m


def is_occluded(sim, eye_pos: tuple, target_pos: tuple) -> bool:
    """True if scene geometry blocks the straight line from eye_pos to
    target_pos.

    A hit within _TARGET_SLACK_M of the target doesn't count as occlusion —
    confirmed on real HSSD geometry that target_pos (an object's HSSD
    `translation`, i.e. its pivot — see topdown_map.anchor_world_positions)
    routinely sits at or near an object's *base*, not its visible top
    surface, so a ray from above legitimately grazes the object's own mesh
    a few tens of centimeters short of the exact pivot point. 0.05 m was
    too tight and misclassified every anchor's own surface as an occluder,
    starving viewpoint_for of any valid candidate; 0.3 m clears that while
    still catching real occlusion, which blocks *much* further short of the
    target (confirmed directly: a ray between two different-room anchors
    hit a wall 3.4 m into an 14.85 m path — nowhere near this slack)."""
    import habitat_sim
    import magnum as mn

    _TARGET_SLACK_M = 0.3

    origin = mn.Vector3(*eye_pos)
    delta = mn.Vector3(*target_pos) - origin
    dist = delta.length()
    if dist < 1e-6:
        return False
    ray = habitat_sim.geo.Ray(origin, delta.normalized())
    result = sim.cast_ray(ray, max_distance=float(dist))
    if not result.has_hits():
        return False
    return result.hits[0].ray_distance < dist - _TARGET_SLACK_M


def is_visible(sim, eye_pos: tuple, yaw_rad: float, target_pos: tuple, config: SensorConfig) -> bool:
    """Full visibility test: range, then FOV, then occlusion — cheapest
    checks first so a ray cast (the expensive one) only runs when the
    target has already passed the free geometric checks."""
    if not in_range(eye_pos, target_pos, config.max_sense_range_m):
        return False
    if not in_fov(eye_pos, yaw_rad, target_pos, config.fov_deg):
        return False
    return not is_occluded(sim, eye_pos, target_pos)


def detect_visible(world: "EmbodiedWorld", pose: Pose) -> tuple:
    """Every currently-existing instance visible from `pose`, as
    OracleDetection tuples. Instances whose slot has no resolvable world
    position (outdoor/away — outside the sensable volume by design) are
    skipped, not reported as invisible-but-present.

    A stateful-furniture instance (M3: state-change dynamics —
    env/inventory.py's STATEFUL_FURNITURE) visible this way also emits one
    additional OracleDetection per tracked state variable: label
    f"{label}::{variable}", category f"{category}::{variable}", anchor =
    the current value. This rides the exact same visibility check as the
    location detection (seeing the object reveals its state too, by
    construction — no separate sensing model), and the synthetic
    label/category is the same key embodied/posterior.py's belief store
    and embodied/question.py's state questions use, so belief-side code
    needs no changes at all to consume it (see posterior.py's module
    docstring)."""
    from .types import OracleDetection

    eye_pos = (pose.x, pose.y + world.config.sensor.eye_height_m, pose.z)
    all_states = world.current_instance_states()
    detections = []
    for label, (category, slot) in world.current_instances().items():
        pos = world._resolve_slot_position(label, slot)
        if pos is None:
            continue
        if is_visible(world._sim, eye_pos, pose.yaw_rad, pos, world.config.sensor):
            detections.append(OracleDetection(
                label=label, category=category, world_pos=pos, anchor=slot, t=world.t,
            ))
            for variable, value in all_states.get(label, {}).items():
                detections.append(OracleDetection(
                    label=f"{label}::{variable}", category=f"{category}::{variable}",
                    world_pos=pos, anchor=value, t=world.t,
                ))
    return tuple(detections)


def viewpoint_from_position(
    world: "EmbodiedWorld",
    pos: tuple[float, float, float],
    n_samples: int = 12,
    radii: tuple[float, ...] = (0.8, 1.2, 1.6, 2.0, 2.5),
    prefer_farthest: bool = False,
) -> Optional[Pose]:
    """A standing pose from which world position `pos` passes the
    visibility test — the ring-sampling core viewpoint_for() uses,
    factored out so a caller with a real position but no named
    SLOT_ANCHORS entry for it (e.g. a room centroid) can still get a
    genuine, visibility-validated viewpoint instead of either an
    unvalidated blind render or an automatic failure. Pure refactor of
    viewpoint_for's prior body — behavior for every existing (world,
    anchor) caller is unchanged, this just also works from a bare
    position.

    prefer_farthest: within the first radius tier that has any passing
    candidate, return the farthest one instead of the nearest (trades a
    slightly less exact standing position for a wider field of view — the
    Spectator Camera round folded scripts/realism_render_job.py's
    duplicated _farthest_passing_viewpoint ring loop into this shared
    function instead of keeping two copies of the same sampling logic).
    Still bounded to one tier, same as the nearest-preferring default —
    trying farther tiers after a nearer one already passed regressed a
    real case (a small spawned object shrunk below the mask area floor
    once given a 3.5m-tier candidate instead of a 1.5m one)."""
    ax, ay, az = pos

    best: Optional[Pose] = None
    best_dist = float("inf") if not prefer_farthest else -1.0
    for radius in radii:
        for i in range(n_samples):
            theta = 2 * math.pi * i / n_samples
            candidate = (ax + radius * math.cos(theta), ay, az + radius * math.sin(theta))
            snapped = world.snap_to_navmesh(candidate)
            dx, dz = ax - snapped[0], az - snapped[2]
            if dx == 0.0 and dz == 0.0:
                continue
            yaw = math.atan2(dz, dx)
            eye_pos = (snapped[0], snapped[1] + world.config.sensor.eye_height_m, snapped[2])
            if is_visible(world._sim, eye_pos, yaw, pos, world.config.sensor):
                d = ((snapped[0] - ax) ** 2 + (snapped[2] - az) ** 2) ** 0.5
                if (d > best_dist) if prefer_farthest else (d < best_dist):
                    best_dist = d
                    best = Pose(snapped[0], snapped[1], snapped[2], yaw)
        if best is not None:
            return best
    return None


def viewpoint_for(
    world: "EmbodiedWorld",
    anchor: str,
    n_samples: int = 12,
    radii: tuple[float, ...] = (0.8, 1.2, 1.6, 2.0, 2.5),
) -> Optional[Pose]:
    """A standing pose from which `anchor` passes the visibility test.

    Samples candidate positions on rings of increasing radius around the
    anchor's real world position, snaps each to the navmesh's main island,
    and returns the nearest (to the anchor) candidate that actually sees
    it — trying larger radii only if no candidate at a smaller radius
    works. None if no candidate at any tried radius works (anchor
    unresolvable, or genuinely no valid sightline within the tried range).
    """
    pos = world._anchor_positions.get(anchor)
    if pos is None:
        return None
    return viewpoint_from_position(world, pos, n_samples, radii)


# ---------------------------------------------------------------------------
# Spectator camera — a STUDY camera for the realism-eval render job, not an
# embodied-agent viewpoint. Deliberately decoupled from navmesh/eye-height:
# the agent-visibility question ("can an embodied agent standing on the
# floor at eye height ever see this anchor") and the study-render question
# ("can we produce a legible picture of this specific object for a human
# annotator") are different questions with different answers — an object
# genuinely unreachable by any navmesh-snapped standing pose (e.g. a
# wardrobe's interior) can still be photographed from a spectator position
# no real agent could stand at. Only stage/scene geometry still blocks the
# ray (see module docstring); it is the "no navmesh, no eye-height, allowed
# to float" constraint that changes, not what counts as an obstruction.
# ---------------------------------------------------------------------------

_SPECTATOR_AZIMUTHS = 12
_SPECTATOR_ELEVATIONS_DEG = (15.0, 30.0, 45.0, 60.0)
# Distance tiers scale with the object's own max extent, not a fixed
# ring — a keys-sized object and a wardrobe-sized object need wildly
# different camera distances to land anywhere near the same framing. A
# naive pinhole-projection derivation (extent / (2*distance) at 90deg
# hfov) suggested (0.35, 1.0, 2.5) x extent, and that DOES rescue the
# fridge case (a real recessed-in-cabinetry anchor with no valid embodied
# viewpoint at all — needs the close 0.35x tier to find any sightline
# through the nook) — but live-tested directly against a second real
# case (a stool, extent 0.48m) and found the naive formula badly
# under-predicts real apparent size: at the SAME 2.5x-extent ratio that
# gave a laptop a comfortable 12% frame area, the stool measured 46% —
# mask_too_large, a real gold-set regression. The naive formula assumes a
# single-axis silhouette; a real object's oblique, multi-axis footprint
# reads larger. Widened to (0.5, 1.5, 4.0) x extent based on that live
# measurement (stool at the 4.0x/30deg pick: 6.5% frame area, well inside
# [0.5%, 40%]) — confirmed this STILL finds fridge candidates (fewer, at
# a higher 60deg elevation tier, but real ones exist). The mask predicate
# (evaluate_object_mask), not this heuristic, is still the actual
# pass/fail gate on the rendered panel — these tiers only decide which
# candidates are ever tried.
_SPECTATOR_DISTANCE_FACTORS = (0.5, 1.5, 4.0)
# Per-tier minimum distances (Floor-Bound Realization round), replacing the
# old single 0.3m floor. For a tiny object the extent-scaled tiers all
# collapsed onto that one floor (candle, extent 0.095m: max(extent x
# {0.5,1.5,4.0}, 0.3) = 0.3/0.3/0.38 — three near-identical, VERY close
# cameras), and 0.3m is inside some assets' own geometry: measured
# directly on the HSSD candle, whose glow shell swallows the camera
# (mask 0% at 0.30m, 42% at 0.38m, sane 16%->0.6% across 0.5-1.0m).
# Distinct per-tier floors keep three genuinely different distances for
# small objects, all outside the glow-shell trap; large objects are
# unaffected (extent-scaled distances already exceed these floors).
_SPECTATOR_TIER_MIN_DISTANCES_M = (0.45, 0.7, 1.0)
# "No slack term" (per the Spectator Camera round's instruction) — unlike
# is_occluded's _TARGET_SLACK_M=0.3 (tuned to tolerate an anchor coordinate
# that's often an object's base/pivot, far from its visible surface), the
# spectator sightline targets a point deliberately chosen to sit ON the
# object's own boundary (AABB top-center or centroid), so an unobstructed
# ray should land almost exactly at the target distance. This epsilon is
# pure float/mesh-precision slack, not a tuned business-logic tolerance.
_SPECTATOR_SIGHTLINE_EPS_M = 0.02


@dataclass
class SpectatorPose:
    camera_pos: tuple[float, float, float]
    look_at: tuple[float, float, float]  # AABB centroid — the aim target for camera_basis()
    distance_m: float
    elevation_deg: float
    azimuth_deg: float

    @property
    def is_high_angle(self) -> bool:
        """Elevation > 30deg — the render job labels these panels
        "spectator view" so annotators aren't misled into reading an
        above-eye-level shot as what an agent standing there would see."""
        return self.elevation_deg > 30.0


def spectator_candidate_embedded(sim, point: tuple[float, float, float]) -> bool:
    """Reuses placement_check's short-ray "embedded in geometry" signature
    (a ring of near-zero-distance horizontal hits) instead of a new
    physics test — same mechanism this project already trusts for "is
    this point inside a wall/furniture body".

    Public (not `_`-prefixed): this is the "existing enclosure-detection
    capability" scripts/realism_render_job.py's mask-too-small/too-large
    corrective sweep reuses for candidate scoring, not just
    spectator_viewpoint's own pass/fail gate below."""
    from .placement_check import check_placement

    return check_placement(sim, point).embedded


def spectator_unobstructed(sim, eye: tuple[float, float, float], target: tuple[float, float, float]) -> bool:
    import habitat_sim
    import magnum as mn

    origin = mn.Vector3(*eye)
    delta = mn.Vector3(*target) - origin
    dist = delta.length()
    if dist < 1e-6:
        return True
    ray = habitat_sim.geo.Ray(origin, delta.normalized())
    result = sim.cast_ray(ray, max_distance=float(dist))
    if not result.has_hits():
        return True
    return result.hits[0].ray_distance >= dist - _SPECTATOR_SIGHTLINE_EPS_M


def spectator_viewpoint(
    sim,
    target_aabb: tuple[tuple[float, float, float], tuple[float, float, float]],
    object_max_extent: float,
) -> Optional[SpectatorPose]:
    """A study-camera pose for `target_aabb` ((min_x,min_y,min_z),
    (max_x,max_y,max_z), e.g. build_realized_day.get_world_aabb's return
    shape) — NOT navmesh-constrained and NOT eye-height-constrained (see
    module section docstring above). Candidates are hemisphere-sampled
    around the AABB centroid: 12 azimuths x 4 elevation tiers x 3 distance
    tiers scaled by `object_max_extent`. A candidate is rejected if it's
    embedded in real geometry (spectator_candidate_embedded), else it
    passes if the sightline to EITHER the AABB's top-center OR its
    centroid is unobstructed (spectator_unobstructed, no slack term).

    Among all passing candidates, prefers the lowest elevation first (a
    more natural, less top-down shot), then the largest distance (more
    room context) — NOT the same "smallest tier that has any hit, stop"
    early-termination convention viewpoint_from_position uses; the whole
    passing set is gathered before choosing, since a low-elevation,
    far-distance candidate at a LATER tier can still beat a high-
    elevation, near candidate found earlier.

    Returns None if no candidate at any elevation/distance/azimuth passes
    — the ENCLOSED failure case (see realism_render_job.py's
    STATUS_ENCLOSED), expected only for objects sealed inside closed
    furniture with no gap a ray can pass through."""
    (min_x, min_y, min_z), (max_x, max_y, max_z) = target_aabb
    cx, cz = (min_x + max_x) / 2.0, (min_z + max_z) / 2.0
    cy = (min_y + max_y) / 2.0
    centroid = (cx, cy, cz)
    top_center = (cx, max_y, cz)

    passing: list[SpectatorPose] = []
    for elevation_deg in _SPECTATOR_ELEVATIONS_DEG:
        elev = math.radians(elevation_deg)
        for factor, tier_min in zip(_SPECTATOR_DISTANCE_FACTORS, _SPECTATOR_TIER_MIN_DISTANCES_M):
            distance = max(object_max_extent * factor, tier_min)
            horiz = distance * math.cos(elev)
            height = distance * math.sin(elev)
            for i in range(_SPECTATOR_AZIMUTHS):
                azimuth_deg = 360.0 * i / _SPECTATOR_AZIMUTHS
                az = math.radians(azimuth_deg)
                cam = (cx + horiz * math.cos(az), cy + height, cz + horiz * math.sin(az))
                if spectator_candidate_embedded(sim, cam):
                    continue
                if spectator_unobstructed(sim, cam, top_center) or spectator_unobstructed(sim, cam, centroid):
                    passing.append(SpectatorPose(
                        camera_pos=cam, look_at=centroid, distance_m=distance,
                        elevation_deg=elevation_deg, azimuth_deg=azimuth_deg,
                    ))
    if not passing:
        return None
    passing.sort(key=lambda p: (p.elevation_deg, -p.distance_m))
    return passing[0]


def deterministic_radial_offset(label: str, max_offset_m: float = 0.4) -> tuple[float, float]:
    """Small (dx, dz) offset seeded by label hash — gives distinct instances
    sharing one anchor/room-centroid position distinct, stable positions
    (not for occlusion; see module docstring)."""
    h = int(hashlib.sha256(label.encode()).hexdigest()[:16], 16)
    angle = 2 * math.pi * ((h % 1_000_000) / 1_000_000.0)
    radius = max_offset_m * (((h // 1_000_000) % 1_000_000) / 1_000_000.0)
    return (radius * math.cos(angle), radius * math.sin(angle))
