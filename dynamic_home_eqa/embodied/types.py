"""
types.py — pure data records shared by world.py and sensor.py.

Split out so sensor.py can use these types without importing world.py (which
imports sensor.py) — avoids a circular import, not a layering statement.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union


@dataclass(frozen=True)
class Pose:
    """Agent pose on the navmesh. yaw_rad is heading in the XZ ground plane,
    0 = +X axis, increasing counter-clockwise (standard atan2(z, x) convention)."""
    x: float
    y: float
    z: float
    yaw_rad: float

    @property
    def position(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass(frozen=True)
class OracleDetection:
    """One instance the sensor confirmed visible at sense time."""
    label:     str
    category:  str
    world_pos: tuple[float, float, float]
    anchor:    str      # the instance's current semantic slot
    t:         float


@dataclass(frozen=True)
class SenseSnapshot:
    t:          float
    pose:       Pose
    detections: tuple[OracleDetection, ...]


@dataclass(frozen=True)
class ActionResult:
    """Result of one execute() call. `snapshots` has exactly one entry for
    Sense/Rotate; Goto emits one per sense_cadence_m traveled plus a final
    arrival snapshot — this is the mechanism that makes opportunistic
    en-route belief refresh automatic rather than something a policy has to
    request separately."""
    final_t:    float
    final_pose: Pose
    snapshots:  tuple[SenseSnapshot, ...]


@dataclass(frozen=True)
class Goto:
    """Walk the shortest navmesh path to `target`. face_yaw_rad sets the
    heading to arrive facing (None = keep the heading of final travel)."""
    target: tuple[float, float, float]
    face_yaw_rad: Optional[float] = None


@dataclass(frozen=True)
class Rotate:
    """Turn in place by delta_yaw_rad (signed; positive = counter-clockwise)."""
    delta_yaw_rad: float


@dataclass(frozen=True)
class Sense:
    """Look from the current pose without moving or turning."""
    pass


Action = Union[Goto, Rotate, Sense]


class UnreachableError(Exception):
    """Raised by EmbodiedWorld.execute(Goto(...)) when no navmesh path
    exists to the target (e.g. a different, disconnected floor — confirmed
    on a real scene: no modeled stair connectivity between two of its
    floors). Callers must handle this explicitly; the alternative (falling
    back to a straight-line "path") would let the agent teleport through
    walls/floors, silently contradicting geodesic_time()'s honest
    float('inf') for the same unreachable pair — a real bug found this way:
    an agent "resensed" an object on a different floor in ~5 seconds by
    walking in a straight line through the intervening floor slab."""
