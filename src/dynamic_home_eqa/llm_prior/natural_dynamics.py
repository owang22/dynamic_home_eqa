"""
llm_prior/natural_dynamics.py — Phase A, A2: a quick check, not a study.
Asks the FM to reason in prose about a household's routine and an
object's typical behavior — the model's native modality — rather than
forcing a bucketed simplex response the way L0's mcq_logprob/verbalized/
sample_count modes all did (L0 penalized that format; this is a
deliberately different elicitation shape, not a rerun of L0 with a new
model). The model reasons freely, then states a single concluding number
on its own line, which is what gets extracted and scored.

Reuses llm_prior.synthetic_kernel.build_synthetic_kernel and scripts/
kernel_reliability_diagram.py's reliability_points/bin_reliability to
score the resulting stay-probability against the fitted kernel on
IDENTICAL held-out dwell events — same machinery T0 and L0 both used,
not a new scoring construction invented for this one quick check.
"""
from __future__ import annotations

import re

from dynamic_home_eqa.llm_prior.prompts import _context_block, time_bin_label

_STAY_PROBABILITY_RE = re.compile(r"STAY_PROBABILITY:\s*([0-9]*\.?[0-9]+)", re.IGNORECASE)


class NaturalParseFailure(Exception):
    """Raised when the model's free-form reasoning never produces a
    parseable concluding line — recorded, not silently defaulted, same
    convention as llm_prior.scoring.ParseFailure."""


def natural_dynamics_prompt(
    persona_text: str, room_inventory_text: str, category: str, time_bin: int, is_state: bool = False,
) -> tuple[str, str]:
    thing = "state" if is_state else "location"
    system = (
        "You are reasoning about a specific household's daily routine and how "
        "objects in it typically behave, based on the household profile and room "
        "inventory given. Think through your reasoning in a few sentences of prose "
        "— who is likely to interact with this object and when, given their "
        "routines — then end your response with your conclusion on its own final "
        "line, in exactly this format: STAY_PROBABILITY: <a number between 0 and 1>"
    )
    user = (
        f"{_context_block(persona_text, room_inventory_text)}\n\n"
        f'Reason about a typical "{category}" in this household at this time of day '
        f"({time_bin_label(time_bin)}). Over the next 6 hours, how likely is its "
        f"{thing} to stay exactly the same, with no change at all? Think it through, "
        f"then conclude with the STAY_PROBABILITY line."
    )
    return system, user


def parse_natural_stay_probability(raw_text: str) -> float:
    match = _STAY_PROBABILITY_RE.search(raw_text)
    if not match:
        raise NaturalParseFailure(f"no STAY_PROBABILITY line found in: {raw_text!r}")
    p = float(match.group(1))
    if not (0.0 <= p <= 1.0):
        raise NaturalParseFailure(f"STAY_PROBABILITY out of [0,1]: {p} in {raw_text!r}")
    return p
