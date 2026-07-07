"""
config.py — frozen configuration for the embodied agent phase.

Every physical/behavioral constant the agent depends on lives here, not
scattered as magic numbers across world/sensor/policy modules, so every
milestone's test can construct an explicit config rather than depending on
module-level defaults it can't override per test.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MotionConfig:
    """Fixed motion model consuming sim time. There is no step quantum —
    time advances continuously as actions execute, in decimal sim-hours
    (the same clock the generated trace uses)."""
    walk_speed_mps:  float = 1.0
    turn_speed_dps:  float = 120.0
    sense_duration_s: float = 1.0
    # Spatial cadence at which goto() emits an intermediate sense snapshot
    # while following a path — this is the mechanism that makes
    # opportunistic en-route belief refresh automatic rather than a special
    # case the policy has to ask for.
    sense_cadence_m: float = 0.5


@dataclass(frozen=True)
class SensorConfig:
    """Visibility oracle parameters. An instance is detected iff it is
    within fov_deg of the agent's forward heading, within max_sense_range_m
    of the agent's eye position (eye_height_m above the agent's navmesh
    pose), and the ray from eye to instance position is unobstructed by
    scene geometry (see sensor.py)."""
    fov_deg:           float = 90.0
    eye_height_m:      float = 1.4
    max_sense_range_m: float = 5.0


@dataclass(frozen=True)
class NavMeshConfig:
    """Recast navmesh-bake parameters. Not habitat_sim's own defaults —
    the navmesh-connectivity phase's D0/D1 diagnostics (see
    scripts/diagnose_navmesh_islands.py, scripts/sweep_navmesh_recompute.py)
    found scene 102343992's interior fragmented into ~6 disconnected
    islands at habitat_sim.NavMeshSettings()'s own defaults (agent_radius
    0.1, agent_max_climb 0.2, cell_size 0.05, cell_height 0.2), with
    near-touch gaps of ~0.4 m horizontal and up to 0.4 m vertical between
    them — consistent with recast pinching off ordinary door thresholds,
    not real stairs. Raising agent_max_climb to 0.4 (confirmed: 0.3 does
    not merge, 0.4 does, sharply) merges 5 of those islands into one
    994.8 m² component covering every canonical room's centroid and all
    but 4 of the 16 hand-authored anchors, and *raises* (not lowers) the
    sampled indoor fraction of the dominant island — evidence it bridged
    real interior doorways rather than fusing into the yard. Every other
    field stays at habitat_sim's own default; this is the minimal change
    that produced the merge (confirmed by sweeping agent_radius and
    cell_size/cell_height independently — neither helped, and shrinking
    cell_height re-fragmented the mesh).

    This config is part of the frozen experiment fingerprint
    (experiment_config.FrozenConfig); any change to these values
    invalidates every prior milestone's attribution-table row.
    """
    agent_radius:     float = 0.10
    agent_height:     float = 1.5
    agent_max_climb:  float = 0.40
    agent_max_slope:  float = 45.0
    cell_size:        float = 0.05
    cell_height:      float = 0.20
    # Minimum sampled indoor fraction (ceiling-raycast, see
    # diagnose_navmesh_islands._is_indoor) an island must clear to be
    # eligible as the agent's default start island — replaces the old
    # "largest island by area" rule, which could not distinguish a real
    # interior from a large outdoor yard that happens to abut the house
    # (confirmed on this scene: the largest-by-area island before the
    # climb fix was only 55% indoor).
    min_indoor_fraction: float = 0.5
    # Anchors resolving onto a navmesh island smaller than this are treated
    # as a documented, disqualified micro-fragment rather than a real part
    # of the house — confirmed on scene 102343992: the 4 living_room
    # furniture anchors (sofa/corner/open_floor/window_sill) sit on a
    # genuinely disconnected ~9.3 m² island that no swept navmesh setting
    # (agent_radius down to 0.04, far narrower than any real agent) ever
    # merged, with a 0.27 m horizontal / 0 m vertical gap to the main
    # component — evidence of a real wall, not a pinched doorway, so no
    # portal was built for it (see reachability.py, world._ensure_sim).
    # Human decision (navmesh-connectivity phase, D3): exclude by area
    # rather than build a speculative portal or disqualify the whole scene.
    min_component_area_m2: float = 10.0


@dataclass(frozen=True)
class CostModelConfig:
    """What travel cost a policy is TOLD when it calls travel_time_to,
    during its own resense/answer tradeoff (E1 — travel-cost
    heterogeneity). Does not touch simulation: EmbodiedWorld.execute(Goto)
    and geodesic_time() always report the real navmesh-geodesic distance
    for scoring (distance_traveled_m, answer_latency_s) and for
    reachability (a genuinely unreachable anchor is still float('inf')
    under both modes) — only the FINITE cost value a policy's
    cost/benefit math sees is swapped. This isolates the question E1
    asks: do policy rankings change if the policy's own model of travel
    cost is flat rather than distance-aware, independent of the agent's
    real embodiment (which never changes)?

    mode="real_geodesic" (default) reproduces every prior milestone's
    behavior exactly — E0/M1/M2/M3 never set this field.
    """
    mode:             str = "real_geodesic"  # "real_geodesic" | "flat"
    flat_leg_seconds: float = 0.0  # only consulted when mode == "flat"


@dataclass(frozen=True)
class AgentConfig:
    motion:     MotionConfig     = field(default_factory=MotionConfig)
    sensor:     SensorConfig     = field(default_factory=SensorConfig)
    navmesh:    NavMeshConfig    = field(default_factory=NavMeshConfig)
    cost_model: CostModelConfig  = field(default_factory=CostModelConfig)
    seed:       int = 0
