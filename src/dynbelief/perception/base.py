"""Stage 0.2 — Perceiver protocol.

A Perceiver turns (pose, time) into observations. It is the ONLY seam where
render quality can ever enter the system: Stage 0-2 use OraclePerceiver
(pure geometry against logged positions and collision proxies); Stage 3
swaps in VLMPerceiver behind the identical interface.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Pose:
    x: float
    z: float
    yaw: float  # radians, world XZ plane; 0 faces +x, positive toward +z


class Perceiver(Protocol):
    def observe(self, pose: Pose, t_min: int) -> dict[int, tuple[int, dict]]:
        """{object_id: (parent_id, states)} for every object perceived from
        `pose` at time t_min."""
        ...

    def current_room(self, pose: Pose) -> str | None:
        """Room id the robot currently stands in."""
        ...


class VLMPerceiver:
    """Stage 3 placeholder: identity/state from rendered RGB-D."""

    def observe(self, pose: Pose, t_min: int):  # pragma: no cover - stub
        raise NotImplementedError("VLM perception is Stage 3")

    def current_room(self, pose: Pose):  # pragma: no cover - stub
        raise NotImplementedError("VLM perception is Stage 3")
