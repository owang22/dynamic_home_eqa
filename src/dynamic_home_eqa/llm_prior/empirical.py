"""
llm_prior/empirical.py — the train-split ground truth L0's own scoring
rule calls for: "score each (model, mode) prior against empirical
train-split frequencies." Distinct from scripts/kernel_reliability_
diagram.py's held-out EVAL-folder dwell events (which score the wait-
hours/survival axis) — this module scores the (category, time_bin)
location-prior axis directly against what the train split's own change
events actually did in that bucket.
"""
from __future__ import annotations

from dynamic_home_eqa.embodied.posterior import OUTSIDE


def empirical_location_frequency(bucket_changes: list[dict], category: str, support: tuple[str, ...]) -> dict[str, float]:
    """Normalized frequency of `to_semantic` among this bucket's
    change events for `category`, over `support` (states never landed on
    in this bucket get 0.0, not omitted — the caller's support is the
    fixed D1 kernel state space, not "whatever this bucket happened to
    show"). Raises ValueError if the category never moved in this bucket
    (nothing to score against — the caller should have already filtered
    to occurring (category, time_bin) pairs via llm_prior.targets)."""
    counts = {s: 0 for s in support}
    n = 0
    for c in bucket_changes:
        if c.get("object_category") != category:
            continue
        dest = c.get("to_semantic") or OUTSIDE
        if dest in counts:
            counts[dest] += 1
        n += 1
    if n == 0:
        raise ValueError(f"category {category!r} has no change events in this bucket")
    return {s: v / n for s, v in counts.items()}


def empirical_state_frequency(bucket_changes: list[dict], category_variable: str, support: tuple[str, ...]) -> dict[str, float]:
    """State-axis counterpart of empirical_location_frequency: normalized
    frequency of `to_state` (NOT `to_semantic` — state_change events carry
    a value like "open"/"closed", never a navmesh slot) among this
    bucket's state_change events for `category_variable`
    ("{category}::{variable}", the same synthetic key llm_prior.targets
    uses), over `support`. Filters on both object_category and
    state_variable — today's STATEFUL_FURNITURE maps one variable per
    category, but filtering only on category would silently pool two
    variables' events together if that ever changes."""
    category, variable = category_variable.split("::")
    counts = {s: 0 for s in support}
    n = 0
    for c in bucket_changes:
        if c.get("change_type") != "state_change":
            continue
        if c.get("object_category") != category or c.get("state_variable") != variable:
            continue
        dest = c.get("to_state")
        if dest in counts:
            counts[dest] += 1
        n += 1
    if n == 0:
        raise ValueError(f"category_variable {category_variable!r} has no state_change events in this bucket")
    return {s: v / n for s, v in counts.items()}


def empirical_stay_probability(bucket_changes: list[dict], all_changes_sorted_by_label: dict[str, list[dict]],
                                category: str, reference_hours: float) -> float:
    """Fraction of this category's dwell gaps (in ANY bucket — dwell gaps
    span from one event to the next, not confined to a single 6h bucket)
    that lasted at least reference_hours, restricted to gaps that started
    in this bucket's time-of-day window. Mirrors embodied.belief.
    dwell_events' own gap construction, filtered to category and bucket
    membership by the caller (see llm_prior/report.py)."""
    starts_in_bucket_ts = {c["t"] for c in bucket_changes if c.get("object_category") == category}
    if not starts_in_bucket_ts:
        raise ValueError(f"category {category!r} has no change events in this bucket")
    survived = 0
    total = 0
    for label, events in all_changes_sorted_by_label.items():
        events = sorted(events, key=lambda c: c["t"])
        for i in range(len(events) - 1):
            if events[i]["object_category"] != category:
                continue
            if events[i]["t"] not in starts_in_bucket_ts:
                continue
            gap = events[i + 1]["t"] - events[i]["t"]
            total += 1
            if gap >= reference_hours:
                survived += 1
    if total == 0:
        raise ValueError(f"category {category!r} has no measurable dwell gaps starting in this bucket")
    return survived / total
