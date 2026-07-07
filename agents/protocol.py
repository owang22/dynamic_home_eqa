"""
Agent protocol for Dynamic EQA.

Observation — everything the agent sees before deciding.
Decision     — RESENSE (re-observe) or ANSWER (commit from stale data).

The WorldGraph field is optional: it is populated when running inside a full
PARTNR episode (PerceptionSim mode) and None in standalone semantic mode.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from habitat_llm.world_model.world_graph import WorldGraph


class DecisionKind(str, Enum):
    RESENSE = "resense"
    ANSWER  = "answer"


@dataclass
class Observation:
    # Scene context
    region:          str
    observed_states: dict[str, str]   # {instance_id: current_semantic_slot}
    observed_at:     float            # hour when agent last observed (24h clock)
    query_time:      float            # hour when question is asked
    household_type:  str              # resident profile name

    # Question
    prompt:          str
    options:         list[str]
    observed_option_index: int        # option index answerable from stale obs

    # Budget
    remaining_budget:    int
    questions_remaining: int

    # Optional extras
    time_of_day:   float              # = query_time (convenience alias)
    region_prior:  Optional[dict] = None

    # PARTNR integration: full WorldGraph snapshot at observed_at
    world_graph:   Optional["WorldGraph"] = None

    @property
    def delta(self) -> float:
        return round(self.query_time - self.observed_at, 6)

    @property
    def budget_rate(self) -> float:
        if self.questions_remaining <= 0:
            return 0.0
        return self.remaining_budget / self.questions_remaining


@dataclass
class Decision:
    kind:         DecisionKind
    option_index: Optional[int]   = None   # required for ANSWER
    confidence:   Optional[float] = None   # 0–1; required for ANSWER


class Agent:
    """Abstract base for resense/answer agents."""
    def act(self, obs: Observation) -> Decision:
        raise NotImplementedError
