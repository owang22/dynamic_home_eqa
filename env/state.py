from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ObjectInstance:
    instance_id: str
    category: str
    current_semantic: str
    last_moved_at: Optional[float] = None
    position: Optional[tuple[float, float, float]] = None  # (x, y, z), HSSD world frame
    # {state_variable: current_value}, e.g. {"power": "unpowered"} — M3's
    # state-change dynamics. Location-only instances leave this empty;
    # never assumed non-empty by location code (env/replay.py's
    # move_existing/insert_new branches never touch it).
    states: dict[str, str] = field(default_factory=dict)


@dataclass
class IntervalRecord:
    activity: str
    start: float    # hour of day
    end: float      # hour of day


@dataclass
class SceneState:
    instances: dict[str, ObjectInstance] = field(default_factory=dict)
    open_intervals: dict[str, IntervalRecord] = field(default_factory=dict)

    def log_move(
        self,
        instance_id: str,
        from_semantic: str,
        to_semantic: str,
        t: float,
    ) -> None:
        """Stub — signature is final; storage backend is not yet built."""
