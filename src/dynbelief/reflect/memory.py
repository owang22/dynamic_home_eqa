"""Reflective-memory core: nightly reflection call, memory MD rendering, and the
hypothesis-entropy that gates the fusion prior.

The memory is a structured object (JSON, validated by schema) rendered to a
markdown file for the LLM to read back. Per day the LLM sees its current memory
plus that day's raw events and REWRITES the memory: it selects which observations
are diagnostic of the household's persona/routine (discarding mundane events),
and maintains up to THREE persona hypotheses with probabilities summing to 1 —
adding, sharpening, or REMOVING hypotheses as evidence arrives. The entropy of
the top-3 probabilities is the agent's own uncertainty signal: H≈0 means one
confident persona; H≈log2(3) means it has no idea. The fusion arm scales its
prior injection weight by (1 − H/H_max), so an unsure memory defers to the
statistics and a confident one pushes the Bayesian model hard.
"""
from __future__ import annotations

import json
import math

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
H_MAX = math.log2(3.0)

REFLECT_SCHEMA = {
    "type": "object",
    "properties": {
        "hypotheses": {"type": "array", "maxItems": 3, "items": {
            "type": "object", "properties": {
                "persona": {"type": "string"},
                "prob": {"type": "number"},
                "rationale": {"type": "string"}},
            "required": ["persona", "prob", "rationale"]}},
        "selected_evidence": {"type": "array", "maxItems": 15,
                              "items": {"type": "string"}},
        "notes": {"type": "string"}},
    "required": ["hypotheses", "selected_evidence", "notes"]}

REFLECT_SYS = (
    "You are an embodied home agent building a long-term MEMORY about the household "
    "you observe. Each day you receive that day's object-movement events. Day 0 is a "
    "Monday; days 5-6 are the weekend; the weekly pattern repeats. Rewrite your full "
    "memory now:\n"
    "1. SELECTED EVIDENCE — keep only observations that help diagnose WHO lives here "
    "and their routine: objects or timings that discriminate between household types "
    "(a yoga mat out at 05:30, a suitcase leaving for days, a laptop at the home desk "
    "at midday). DISCARD mundane events any household would produce (dishes cycling to "
    "the sink, a remote on the sofa). At most 15 lines, each formatted "
    "'Day D, HH:MM — object at receptacle (why it matters)'. You may drop previously "
    "kept lines that turned out uninformative.\n"
    "2. HYPOTHESES — maintain up to THREE hypotheses about the resident's persona and "
    "weekly routine, each a short description with a probability; probabilities must "
    "sum to 1. Sharpen probabilities as evidence accumulates; REMOVE a hypothesis when "
    "evidence contradicts it; add a new one if the evidence suggests it.\n"
    "3. NOTES — brief working notes: open questions, day-of-week patterns to verify.\n"
    "Return the complete updated memory as JSON."
)

QUERY_SYS = (
    "You answer object-location queries about a household using your MEMORY file: "
    "persona hypotheses with probabilities plus selected evidence. Day 0 is a Monday; "
    "days 5-6 are the weekend; the weekly pattern repeats. Weigh your hypotheses by "
    "their probabilities, consider the queried weekday and time of day, and predict "
    "where the object is. Give up to 3 candidate receptacles with probabilities, most "
    "likely first, using ONLY receptacles from the provided candidate list, or "
    "'elsewhere' if the object is likely out of the home."
)

EMPTY_MEM = {"hypotheses": [], "selected_evidence": [], "notes": ""}


def render_md(mem: dict, after_day: int) -> str:
    """Deterministic markdown render of the memory object (what the LLM reads)."""
    lines = [f"# Household memory — after day {after_day} "
             f"({after_day + 1} day(s) observed)" if after_day >= 0
             else "# Household memory — (empty, no days observed yet)"]
    lines.append("\n## Persona hypotheses (up to 3, probs sum to 1)")
    if mem.get("hypotheses"):
        for i, hyp in enumerate(mem["hypotheses"][:3], 1):
            lines.append(f"{i}. (p={float(hyp.get('prob', 0)):.2f}) "
                         f"{hyp.get('persona', '?')} — {hyp.get('rationale', '')}")
    else:
        lines.append("(none yet)")
    lines.append("\n## Selected evidence")
    ev = mem.get("selected_evidence") or []
    lines += [f"- {e}" for e in ev[:15]] or ["(none yet)"]
    lines.append("\n## Notes")
    lines.append(mem.get("notes") or "(none)")
    return "\n".join(lines)


def entropy_bits(hyps: list[dict]) -> float:
    """Shannon entropy (bits) of the hypothesis probabilities, renormalized.
    No hypotheses -> maximal uncertainty (H_MAX)."""
    ps = [max(1e-9, float(h.get("prob", 0.0))) for h in (hyps or [])[:3]]
    if not ps:
        return H_MAX
    z = sum(ps)
    ps = [p / z for p in ps]
    return -sum(p * math.log2(p) for p in ps)


def prior_weight(h_bits: float) -> float:
    """Frozen linear mapping: w = 1 - H/H_max, clipped to [0,1]."""
    return min(1.0, max(0.0, 1.0 - h_bits / H_MAX))


def day_user_msg(md: str, day: int, event_lines: list[str]) -> str:
    ev = "\n".join(event_lines) if event_lines else "  (no events observed today)"
    return (f"CURRENT MEMORY:\n{md}\n\n"
            f"TODAY (day {day}, {WEEKDAYS[day % 7]}) you observed these events:\n{ev}\n\n"
            f"Update the memory now.")


def reflect_day(client, md: str, day: int, event_lines: list[str]):
    """One nightly reflection call. Returns the new memory dict, or None on any
    failure (caller keeps the previous memory)."""
    try:
        out = json.loads(client.generate(REFLECT_SYS, day_user_msg(md, day, event_lines),
                                         REFLECT_SCHEMA, seed=7, temperature=0.0))
        hyps = out.get("hypotheses") or []
        for hyp in hyps:
            float(hyp["prob"])                      # validate numerics
        return {"hypotheses": hyps[:3],
                "selected_evidence": [str(e) for e in (out.get("selected_evidence") or [])][:15],
                "notes": str(out.get("notes", ""))}
    except Exception:
        return None
