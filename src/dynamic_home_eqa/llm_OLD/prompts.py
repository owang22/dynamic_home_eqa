"""
llm_prior/prompts.py — L0's prompt templates. Behavior-bearing: hashed
(PROMPT_VERSION + the template text itself) into every elicitation
manifest alongside code_hash. Changing a template's wording invalidates
that elicitation's cached results, same semantics as a code change — see
this module's PROMPT_VERSION.

Every prompt is built from (persona_text, room_inventory_text, category,
time_bin, support) alone — never from a train-day event. The scene is
described only by profile and room inventory, per L0's own hard rule
("the LLM must not see realized dynamics").
"""
from __future__ import annotations

import hashlib

# l0-v2 (2026-07-07): room-inventory rendering now includes a standing
# "also present" category list (llm_prior/targets.py's render_room_
# inventory, known_categories param) — v1 never told the model that most
# of the categories it was being asked to locate existed in the household
# at all, and models correctly inferred "not in inventory -> OUTSIDE" for
# them (see l0_rerun.md). This is a real prompt content change (a
# category name now appears in the room-inventory block that didn't
# before) even though the template code producing that block is
# unchanged, so the version bumps per this module's own stated rule.
PROMPT_VERSION = "l0-v2"

_TIME_BIN_LABELS = {
    0: "early morning (00:00-06:00)",
    1: "morning/midday (06:00-12:00)",
    2: "afternoon (12:00-18:00)",
    3: "evening/night (18:00-24:00)",
}

SYSTEM_PROMPT = (
    "You are estimating typical patterns in a specific household, based only on "
    "the household's profile (who lives there, their routines) and a static "
    "inventory of furniture per room. You have NOT been shown any specific day's "
    "events, so answer from general household-routine knowledge, not from any "
    "particular incident. Answer only in the exact format requested."
)


def time_bin_label(time_bin: int) -> str:
    return _TIME_BIN_LABELS[time_bin]


def _context_block(persona_text: str, room_inventory_text: str) -> str:
    return (
        f"Household profile:\n{persona_text}\n\n"
        f"Room inventory (furniture present, by room):\n{room_inventory_text}"
    )


def _option_letters(n: int) -> tuple[str, ...]:
    return tuple(chr(ord("A") + i) for i in range(n))


def location_mcq_prompt(
    persona_text: str, room_inventory_text: str, category: str, time_bin: int, support: tuple[str, ...],
) -> tuple[str, str, tuple[str, ...]]:
    """Returns (system, user, option_letters). Options are the exact D1
    kernel-state-space support, in the given order — option order is part
    of the prompt hash, so a caller must not silently reorder support
    between elicitation and scoring."""
    letters = _option_letters(len(support))
    options_block = "\n".join(f"{letter}) {slot}" for letter, slot in zip(letters, support))
    user = (
        f"{_context_block(persona_text, room_inventory_text)}\n\n"
        f"Question: At this time of day ({time_bin_label(time_bin)}), where is a typical "
        f'"{category}" most likely to be found in this household right now?\n'
        f"Options:\n{options_block}\n\n"
        f"Answer with only the single letter of the most likely option."
    )
    return SYSTEM_PROMPT, user, letters


def location_verbalized_prompt(
    persona_text: str, room_inventory_text: str, category: str, time_bin: int, support: tuple[str, ...],
) -> tuple[str, str]:
    """Returns (system, user) — routed through LLMPriorClient.verbalized's
    .chat() call like every other mode, not a manually concatenated
    single string (see client.py's own docstring for why that matters)."""
    slots_block = ", ".join(f'"{s}"' for s in support)
    user = (
        f"{_context_block(persona_text, room_inventory_text)}\n\n"
        f"Question: At this time of day ({time_bin_label(time_bin)}), estimate the probability "
        f'that a typical "{category}" is at each of these locations right now: {slots_block}.\n\n'
        f"Respond with ONLY a JSON object mapping each location string to a probability, "
        f"with the probabilities summing to 1.0. Example shape: "
        f'{{"{support[0]}": 0.5, "{support[-1]}": 0.5}}'
    )
    return SYSTEM_PROMPT, user


def location_sample_prompt(
    persona_text: str, room_inventory_text: str, category: str, time_bin: int, support: tuple[str, ...],
) -> tuple[str, tuple[str, ...]]:
    """Same shape as the MCQ prompt (a single-letter answer) — sample_count
    mode draws k independent completions of this prompt at temperature>0
    instead of reading logprobs off one greedy completion."""
    system, user, letters = location_mcq_prompt(persona_text, room_inventory_text, category, time_bin, support)
    return f"{system}\n\n{user}", letters


def dynamics_mcq_prompt(
    persona_text: str, room_inventory_text: str, category: str, time_bin: int, is_state: bool,
) -> tuple[str, str, tuple[str, ...]]:
    """A binary stay-vs-change MCQ — P(stay) is read off option A's
    elicited probability. reference_window is fixed at the same width as
    one time bin (6h) so "stay probability" has a well-defined horizon
    across every target, converted to an hourly hazard rate at scoring
    time (see llm_prior/synthetic_kernel.py)."""
    thing = "state" if is_state else "location"
    user = (
        f"{_context_block(persona_text, room_inventory_text)}\n\n"
        f'Question: Consider a typical "{category}" in this household at this time of day '
        f"({time_bin_label(time_bin)}). Over the next 6 hours, how likely is its {thing} to "
        f"stay exactly the same, with no change at all?\n"
        f"Options:\nA) Stays the same\nB) Changes\n\n"
        f"Answer with only the single letter of the more likely outcome."
    )
    return SYSTEM_PROMPT, user, ("A", "B")


def dynamics_verbalized_prompt(persona_text: str, room_inventory_text: str, category: str, time_bin: int, is_state: bool) -> tuple[str, str]:
    thing = "state" if is_state else "location"
    user = (
        f"{_context_block(persona_text, room_inventory_text)}\n\n"
        f'Question: Consider a typical "{category}" in this household at this time of day '
        f"({time_bin_label(time_bin)}). Over the next 6 hours, what is the probability its "
        f"{thing} stays exactly the same, with no change at all?\n\n"
        f'Respond with ONLY a JSON object of the shape {{"stay_probability": <number between 0 and 1>}}.'
    )
    return SYSTEM_PROMPT, user


def dynamics_sample_prompt(persona_text: str, room_inventory_text: str, category: str, time_bin: int, is_state: bool) -> tuple[str, tuple[str, ...]]:
    system, user, letters = dynamics_mcq_prompt(persona_text, room_inventory_text, category, time_bin, is_state)
    return f"{system}\n\n{user}", letters


def prompt_hash(*parts: str) -> str:
    """Hashed into every elicitation manifest alongside code_hash — see
    module docstring. Includes PROMPT_VERSION so a deliberate template
    rewrite (even one that reuses the exact same text by coincidence,
    which can't happen, but as a defensive convention) always changes the
    hash when the version bump itself is the intended signal."""
    h = hashlib.sha256()
    h.update(PROMPT_VERSION.encode())
    for p in parts:
        h.update(b"\x00")
        h.update(p.encode())
    return h.hexdigest()[:16]
