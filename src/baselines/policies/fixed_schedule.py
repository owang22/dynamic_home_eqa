"""Policy: sense a fixed rotation of receptacles on a fixed cadence,
independent of what is being asked."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from baselines.policies.base import DecisionPolicy
from baselines.types import (Action, AnswerNow, EpisodeContext, Prediction,
                             Question, Sense, SenseResult)

SECONDS_PER_HOUR = 3600


@dataclass(frozen=True)
class FixedScheduleConfig:
    """Rotation of receptacles to patrol and the cadence in query-hours.

    ``every_hours`` is the minimum sim-time gap between scheduled senses;
    the schedule fires on the first question whose ``t_query`` is at least
    that far past the previous scheduled sense (the very first question of
    an episode is always due).
    """

    rotation: Tuple[str, ...]
    every_hours: float

    def __post_init__(self) -> None:
        if not self.rotation:
            raise ValueError("FixedScheduleConfig: rotation must be non-empty")
        if self.every_hours <= 0:
            raise ValueError(
                f"FixedScheduleConfig: every_hours must be > 0, "
                f"got {self.every_hours}")


class FixedSchedule(DecisionPolicy):
    """Patrol ``rotation`` in order, one sense whenever the cadence is due.

    The question content is ignored by design: this baseline measures what
    blind periodic refreshing buys. At most one sense per question (the
    cadence check fails on the immediate re-ask), hence termination.
    """

    def __init__(self, config: FixedScheduleConfig) -> None:
        self._config = config
        self._next_index = 0
        self._last_sense_t: int | None = None

    @property
    def name(self) -> str:
        return (f"FixedSchedule(k={self._config.every_hours}h,"
                f"n_rot={len(self._config.rotation)})")

    def reset(self, context: EpisodeContext) -> None:
        self._next_index = 0
        self._last_sense_t = None

    def _due(self, t: int) -> bool:
        if self._last_sense_t is None:
            return True
        return t - self._last_sense_t >= self._config.every_hours * SECONDS_PER_HOUR

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: int, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        if budget_remaining > 0 and self._due(t):
            receptacle = self._config.rotation[
                self._next_index % len(self._config.rotation)]
            self._next_index += 1
            self._last_sense_t = t
            return Sense(receptacle_id=receptacle)
        return AnswerNow()
