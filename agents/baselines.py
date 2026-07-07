"""
Model-free baseline agents.

All three are instant (no model) and validate the harness + metrics before
any LLM is attached:

  AlwaysAnswer      — sanity floor: accuracy should degrade with Δ.
  AlwaysResense     — efficiency ceiling: high accuracy, worst budget use.
  DeltaThreshold(τ) — sweeping τ gives the simplest prior-free policy curve.
"""
from __future__ import annotations

import math

from dynamic_home_eqa.agents.protocol import Agent, Decision, DecisionKind, Observation


class AlwaysAnswer:
    """Never resenses. Answers immediately from observed_states.

    Confidence decays with staleness (Δ) so calibration scoring sees
    meaningful variation.  Expected behaviour: accuracy degrades as Δ grows
    because it cannot see changes that happened after t0.
    """
    def act(self, obs: Observation) -> Decision:
        conf = _staleness_confidence(obs.delta)
        return Decision(
            kind=DecisionKind.ANSWER,
            option_index=obs.observed_option_index,
            confidence=conf,
        )


class AlwaysResense:
    """Resenses until budget is exhausted, then answers from the (now
    ground-truth) updated observation.

    After resensing, observed_at == query_time, so observed_option_index
    matches the correct answer.  This is the efficiency upper-bound baseline:
    near-perfect accuracy, maximum budget cost.
    """
    def act(self, obs: Observation) -> Decision:
        if obs.remaining_budget > 0:
            return Decision(kind=DecisionKind.RESENSE)
        return Decision(
            kind=DecisionKind.ANSWER,
            option_index=obs.observed_option_index,
            confidence=1.0,
        )


class DeltaThreshold:
    """RESENSE iff Δ > τ, else ANSWER from observed_states.

    Sweeping τ traces the accuracy–budget tradeoff curve without any model.
    It's the simplest policy that engages the temporal reasoning dimension of
    the task.  Compare to the LLM agent whose threshold is adaptive.

    Args:
        tau: staleness threshold in hours.  Resense when query_time - observed_at > tau.
    """
    def __init__(self, tau: float) -> None:
        self.tau = tau

    def act(self, obs: Observation) -> Decision:
        if obs.delta > self.tau and obs.remaining_budget > 0:
            return Decision(kind=DecisionKind.RESENSE)
        conf = _staleness_confidence(obs.delta)
        return Decision(
            kind=DecisionKind.ANSWER,
            option_index=obs.observed_option_index,
            confidence=conf,
        )


# ──────────────────────────────────────────────────────────────────────────────

def _staleness_confidence(delta: float) -> float:
    """Confidence that decays exponentially with staleness.

    δ=0   → 0.95   (recent observation, nearly certain)
    δ=1   → 0.72
    δ=3   → 0.47
    δ=6   → 0.22
    """
    return float(0.95 * math.exp(-0.13 * max(0.0, delta)))
