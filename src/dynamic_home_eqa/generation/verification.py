"""
Multi-agent cross-verification for multi-occupant households.

Single-pass LLM generation of joint activity traces produces physically
incoherent schedules in ~70% of cases for multi-occupant households:
two occupants using one chair simultaneously, an occupant simultaneously
at dinner and marked as 'away', contradictory location presence, etc.

This module implements the cross-verification pass described in the spec:
  1. Generate each occupant's trace independently (stages.py).
  2. Run detect_occupant_conflicts() — a separate LLM call that reads all
     traces and returns a conflict list.
  3. For each conflict, mark the conflicting activity spans for regeneration.
  4. Regenerate only the flagged spans (targeted resample, not full redo).

This is only called for households with more than one occupant. For single-
occupant profiles it is a no-op to avoid dead weight.

Conflict types detected:
  - Scarce-object contention: two occupants using an object with count=1 simultaneously.
  - Presence contradiction: occupant is both 'away' and at a location.
  - Impossible joint activity: two occupants in mutually exclusive states.

The verification pass reduces multi-agent incoherence; it does not
guarantee zero conflicts — downstream grounding rejects physically
impossible states.
"""
from __future__ import annotations

from typing import Optional


def needs_verification(persona: dict) -> bool:
    """Returns True iff the household has more than one occupant.

    The verification pass is dead weight for single-occupant households
    and must not be called for them.
    """
    return len(persona.get("occupants", [])) > 1


def resolve_conflicts(
    traces: list[dict],
    conflicts: dict,
    persona: dict,
    inventory: dict[str, int],
    household_id: str,
    day: int,
    model: str,
    temperature: float,
    cache,
    force: bool = False,
    max_rounds: int = 2,
) -> list[dict]:
    """Regenerate activity spans flagged as conflicting.

    For each conflict: identify the occupant and time range, replace the
    conflicting activities with regenerated ones, then re-run conflict
    detection. At most max_rounds of correction.

    Args:
        traces:   List of activity trace dicts (one per occupant).
        conflicts: Output of stages.detect_occupant_conflicts().
        persona:  Persona dict (for context on regeneration calls).
        inventory: Scene inventory (for scarce-object context).
        household_id, day, model, temperature, cache, force: Standard params.
        max_rounds: Maximum correction rounds before returning as-is.

    Returns:
        Corrected list of trace dicts. May still have conflicts if
        max_rounds is reached — caller should note this in metadata.
    """
    from .stages import generate_activity_trace, detect_occupant_conflicts

    current_traces = list(traces)
    occupant_by_name = {
        o["name"]: i
        for i, o in enumerate(persona.get("occupants", []))
    }

    for round_idx in range(max_rounds):
        conflict_list = conflicts.get("conflicts", [])
        if not conflict_list:
            break

        # Build a set of (occupant_name, span_start, span_end) to regenerate
        spans_to_fix: dict[str, list[tuple[float, float]]] = {}
        for c in conflict_list:
            occ = c.get("occupant", "")
            if occ:
                spans_to_fix.setdefault(occ, []).append(
                    (float(c.get("start", 0)), float(c.get("end", 24)))
                )

        for occ_name, spans in spans_to_fix.items():
            idx = occupant_by_name.get(occ_name)
            if idx is None:
                continue
            # Regenerate this occupant's trace under a DISTINCT but
            # deterministic seed (variant_tag folds the round index into the
            # stage string), so it differs from the cached original without
            # force-regenerating non-reproducibly. Same conflict on the same
            # input now resamples the same replacement every run, and the
            # original activity cache entry is left intact.
            new_trace = generate_activity_trace(
                persona=persona,
                occupant_name=occ_name,
                occupant_index=idx,
                household_id=household_id,
                day=day,
                model=model,
                temperature=temperature,
                cache=cache,
                force=force,
                variant_tag=f"conflictfix_r{round_idx}",
            )
            # Splice in only the conflicting spans from the new trace;
            # keep non-conflicting activities from the original.
            current_traces[idx] = _splice_trace(
                original=current_traces[idx],
                replacement=new_trace,
                spans=spans,
            )

        # Re-check for conflicts. The seed is content-derived (a hash of the
        # traces), so the now-spliced traces get their own cache entry
        # without force — deterministic and cacheable across runs.
        conflicts = detect_occupant_conflicts(
            traces=current_traces,
            inventory=inventory,
            household_id=household_id,
            day=day,
            model=model,
            temperature=temperature,
            cache=cache,
            force=force,
        )

    return current_traces


def _splice_trace(
    original: dict,
    replacement: dict,
    spans: list[tuple[float, float]],
) -> dict:
    """Replace activities in `spans` time ranges with activities from `replacement`.

    Activities that fall entirely outside all conflict spans are kept from
    the original trace. Activities inside a conflict span are replaced with
    the corresponding replacement activities.
    """
    def _in_spans(start: float, end: float) -> bool:
        return any(s <= start and end <= e for s, e in spans)

    kept = [
        a for a in original.get("activities", [])
        if not _in_spans(a["start"], a["end"])
    ]
    from_replacement = [
        a for a in replacement.get("activities", [])
        if _in_spans(a["start"], a["end"])
    ]
    merged = sorted(kept + from_replacement, key=lambda a: a["start"])

    return {**original, "activities": merged}


def run_verification_pass(
    traces: list[dict],
    persona: dict,
    inventory: dict[str, int],
    household_id: str,
    day: int,
    model: str,
    temperature: float,
    cache,
    force: bool = False,
) -> tuple[list[dict], dict]:
    """Full verification pass for a multi-occupant household.

    Returns (corrected_traces, final_conflict_report). Caller uses the
    conflict report for metadata — it records whether conflicts remain after
    max correction rounds.

    This function is a no-op (returns traces unchanged) for single-occupant
    households; always check needs_verification() before calling.
    """
    from .stages import detect_occupant_conflicts

    if not needs_verification(persona):
        return traces, {"conflicts": []}

    conflicts = detect_occupant_conflicts(
        traces=traces,
        inventory=inventory,
        household_id=household_id,
        day=day,
        model=model,
        temperature=temperature,
        cache=cache,
        force=force,
    )

    if not conflicts.get("conflicts"):
        return traces, conflicts

    corrected = resolve_conflicts(
        traces=traces,
        conflicts=conflicts,
        persona=persona,
        inventory=inventory,
        household_id=household_id,
        day=day,
        model=model,
        temperature=temperature,
        cache=cache,
        force=force,
    )

    # Final conflict check for metadata. Content-derived seed (see
    # detect_occupant_conflicts) makes this cacheable without force.
    final_conflicts = detect_occupant_conflicts(
        traces=corrected,
        inventory=inventory,
        household_id=household_id,
        day=day,
        model=model,
        temperature=temperature,
        cache=cache,
        force=force,
    )
    return corrected, final_conflicts
