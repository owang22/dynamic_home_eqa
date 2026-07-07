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
from typing import TYPE_CHECKING, Optional

from .config import SensorConfig
from .types import Pose

if TYPE_CHECKING:
    from .world import EmbodiedWorld


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
    ax, ay, az = pos

    best: Optional[Pose] = None
    best_dist = float("inf")
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
                if d < best_dist:
                    best_dist = d
                    best = Pose(snapped[0], snapped[1], snapped[2], yaw)
        if best is not None:
            return best
    return None


def deterministic_radial_offset(label: str, max_offset_m: float = 0.4) -> tuple[float, float]:
    """Small (dx, dz) offset seeded by label hash — gives distinct instances
    sharing one anchor/room-centroid position distinct, stable positions
    (not for occlusion; see module docstring)."""
    h = int(hashlib.sha256(label.encode()).hexdigest()[:16], 16)
    angle = 2 * math.pi * ((h % 1_000_000) / 1_000_000.0)
    radius = max_offset_m * (((h // 1_000_000) % 1_000_000) / 1_000_000.0)
    return (radius * math.cos(angle), radius * math.sin(angle))
