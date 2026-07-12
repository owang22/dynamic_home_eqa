"""
placement_check.py — geometric collision/occupancy signal for a placed
object anchor, computed against the scene's real static Bullet collision
mesh (walls, floors, furniture — all baked into the HSSD stage geometry).

Scope, stated precisely because it is easy to overclaim here: Tier-2b
clutter objects are NOT physically instantiated in habitat_sim (see
embodied/world.py's module docstring) — there is no object mesh to
collision-test against another object's mesh. What this module CAN check,
using the same ray-cast-against-the-stage-mesh mechanism
embodied/sensor.py's occlusion check and embodied/reachability.py's
ceiling check already use, is whether the ANCHOR POINT itself is a
geometrically plausible resting place:

  - supported: a ray cast straight down from the anchor finds a surface
    within a short distance (not floating in mid-air).
  - embedded: a short ring of horizontal rays cast from the anchor finds
    solid geometry immediately (near-zero distance) in most directions,
    the signature of a point sitting inside a wall/furniture body rather
    than in open space beside it.

This is an approximate, ray-based proxy for "collision/occupancy at
anchor" — not a full contact-manifold physics test (no object mesh exists
for that). It requires enable_physics=True (cast_ray is a silent no-op
otherwise — see sensor.py's module docstring, confirmed empirically
there).

Per the standing instruction to stop presenting purely-heuristic scores
as judgments: this signal, like every other automatic signal in the
realism-eval tooling (suspicion score, deterministic plausibility
confidence, LLM self-graded realism), is a CANDIDATE for sampling
stratification and human-correlation — never a judgment on its own.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

_SUPPORT_MAX_M = 0.5       # downward ray must hit within this to count "supported"
_SUPPORT_PROBE_UP_M = 0.05  # start the downward ray slightly above the anchor
_SUPPORT_RAY_MAX_M = 2.0    # give up looking for a floor/surface beyond this
_RING_RADIUS_M = 0.3        # approximate small-object footprint radius
_RING_RAYS = 8
_EMBEDDED_HIT_MAX_M = 0.03      # a ring hit this close means "already inside something"
_EMBEDDED_FRACTION = 0.5        # this fraction of ring rays hitting near-zero => embedded


@dataclass
class PlacementCheck:
    supported: bool
    support_distance_m: Optional[float]   # None if no hit within _SUPPORT_RAY_MAX_M
    embedded: bool
    embedded_ring_fraction: float          # fraction of ring rays that hit near-zero

    @property
    def passed(self) -> bool:
        """A single pass/fail summary: supported and not embedded."""
        return self.supported and not self.embedded


def classify_placement(
    support_hit_distance: Optional[float],
    ring_hit_distances: list[Optional[float]],
    support_max_m: float = _SUPPORT_MAX_M,
    embedded_hit_max_m: float = _EMBEDDED_HIT_MAX_M,
    embedded_fraction: float = _EMBEDDED_FRACTION,
) -> PlacementCheck:
    """Pure classification logic, unit-testable without habitat_sim —
    check_placement() below does the actual ray casting and calls this."""
    supported = support_hit_distance is not None and support_hit_distance <= support_max_m

    near_hits = sum(
        1 for d in ring_hit_distances if d is not None and d <= embedded_hit_max_m
    )
    ring_fraction = near_hits / len(ring_hit_distances) if ring_hit_distances else 0.0
    embedded = ring_fraction >= embedded_fraction

    return PlacementCheck(
        supported=supported,
        support_distance_m=support_hit_distance,
        embedded=embedded,
        embedded_ring_fraction=ring_fraction,
    )


def check_placement(
    sim,
    position: tuple[float, float, float],
    ring_radius_m: float = _RING_RADIUS_M,
    ring_rays: int = _RING_RAYS,
) -> PlacementCheck:
    """Casts the real rays against `sim`'s stage collision mesh.
    `sim` must have been constructed with enable_physics=True."""
    import habitat_sim
    import magnum as mn

    x, y, z = position

    # RayHitInfo.ray_distance is already in meters along the ray (confirmed
    # against embodied/sensor.py's own occlusion check, which compares it
    # directly to a meter distance with no rescaling) — not a 0-1 fraction
    # of max_distance.
    down_origin = mn.Vector3(x, y + _SUPPORT_PROBE_UP_M, z)
    down_ray = habitat_sim.geo.Ray(down_origin, mn.Vector3(0.0, -1.0, 0.0))
    down_result = sim.cast_ray(down_ray, max_distance=_SUPPORT_RAY_MAX_M)
    support_hit_distance = down_result.hits[0].ray_distance if down_result.has_hits() else None

    ring_hit_distances: list[Optional[float]] = []
    for i in range(ring_rays):
        angle = 2.0 * math.pi * i / ring_rays
        direction = mn.Vector3(math.cos(angle), 0.0, math.sin(angle))
        ray = habitat_sim.geo.Ray(mn.Vector3(x, y, z), direction)
        result = sim.cast_ray(ray, max_distance=ring_radius_m)
        ring_hit_distances.append(result.hits[0].ray_distance if result.has_hits() else None)

    return classify_placement(support_hit_distance, ring_hit_distances)


def aggregate_placement_checks(
    checks: list[tuple[str, str, PlacementCheck]],  # (category, anchor, check)
) -> dict:
    """Per-category and per-anchor pass-rate aggregation — pure counting,
    the same shape as generation_diversity_report.py's per-category tables."""
    from collections import defaultdict

    by_category: dict[str, list[bool]] = defaultdict(list)
    by_anchor: dict[str, list[bool]] = defaultdict(list)
    for category, anchor, check in checks:
        by_category[category].append(check.passed)
        by_anchor[anchor].append(check.passed)

    def _rates(d: dict[str, list[bool]]) -> dict[str, dict]:
        return {
            key: {"n": len(vals), "pass_rate": sum(vals) / len(vals)}
            for key, vals in d.items()
        }

    return {"by_category": _rates(by_category), "by_anchor": _rates(by_anchor)}
