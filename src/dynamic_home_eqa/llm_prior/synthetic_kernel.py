"""
llm_prior/synthetic_kernel.py — turns an elicited (location distribution,
stay probability) pair into a posterior.TransitionKernel, so L0's scoring
can reuse embodied.belief._posterior_validity_at_dwell and scripts/
kernel_reliability_diagram.py's reliability_points/bin_reliability/
write_plot UNCHANGED against an LLM-elicited prior — literal reuse of the
existing kernel reliability machinery, not a parallel reimplementation of
its math against a differently-shaped object.

The elicited "stay probability over the next REFERENCE_HOURS" is a
discrete-time quantity; TransitionKernel's own math is continuous-time
(propagate() uses alpha = exp(-lambda_per_hour * elapsed)). Converting
one to the other is the one piece of interpretation this module owns:
lambda_per_hour = -ln(stay_probability) / REFERENCE_HOURS, the hazard
rate whose exponential survival curve passes through the elicited point
at REFERENCE_HOURS exactly. This is an approximation (a real object's
hazard need not be constant-rate merely because the LLM was asked about
one fixed window) — stated here, not hidden, and it is the SAME
approximation the fitted kernel itself already makes (DecayModel/
TransitionKernel are constant-rate by construction throughout this
codebase), so the LLM prior and the fitted kernel are compared on equal
footing, not a stricter standard applied to one side.
"""
from __future__ import annotations

import math

from dynamic_home_eqa.embodied.posterior import TransitionKernel

REFERENCE_HOURS = 6.0  # matches the dynamics prompts' own fixed window (llm_prior/prompts.py)

# Floor/ceiling so a degenerate elicited probability (exactly 0 or 1, or a
# parse failure defaulting to an extreme) doesn't produce lambda_per_hour
# of 0 or infinity — the fitted kernels this compares against never see
# literal 0/1 either (real dwell data always has some spread).
_MIN_STAY_PROB = 1e-3
_MAX_STAY_PROB = 1.0 - 1e-3


def stay_probability_to_lambda(stay_probability: float, reference_hours: float = REFERENCE_HOURS) -> float:
    p = min(_MAX_STAY_PROB, max(_MIN_STAY_PROB, stay_probability))
    return -math.log(p) / reference_hours


def build_synthetic_kernel(
    category: str, support: tuple[str, ...], dest_dist: dict[str, float], stay_probability: float,
) -> TransitionKernel:
    """dest_dist must be a normalized distribution over exactly `support`
    (the same D1 kernel-state-space support elicit_location produced the
    distribution over) — callers get this from llm_prior/scoring.py's
    mode-specific parsers, never constructed ad hoc here."""
    missing = set(support) - set(dest_dist)
    if missing:
        raise ValueError(f"dest_dist missing support states: {missing}")
    total = sum(dest_dist[s] for s in support)
    if total <= 0:
        raise ValueError("dest_dist sums to zero over the given support")
    normalized = tuple(dest_dist[s] / total for s in support)
    return TransitionKernel(
        category=category, states=support,
        lambda_per_hour=stay_probability_to_lambda(stay_probability),
        dest_dist=normalized,
    )
