"""
Difficulty stratification for EQA questions.

Two independent axes (spec'd separately so binning can be recalibrated later):
  staleness  — hours since the queried entity last changed before the query time.
               0 if the object never changed (static → trivially easy).
  zone_churn — count of changes to the same semantic zone within ±window hours.

Difficulty score = staleness × zone_churn.  Bin into easy/medium/hard by
tertile over a generated batch (assign_difficulty_bins, modifies specs in-place).

Both raw axes are recorded in MCQuestion.metadata so the binning threshold
can be recalibrated after the prototype without regenerating the questions.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..env.deltas import Change
from ..env.replay import last_observation_before

if TYPE_CHECKING:
    from .questions import QuestionSpec


def staleness_score(spec: "QuestionSpec", changes: list[Change]) -> float:
    """Hours since the queried entity last changed before spec.t.

    For LOCATION: uses spec.instance_id.
    For PRESENCE / COUNT: uses the last change to any instance of
      spec.object_category that touched spec.target_slot.
    Returns 0.0 if the entity never changed (static object is trivially easy).
    """
    if spec.instance_id is not None:
        last = last_observation_before(changes, spec.instance_id, spec.t)
    else:
        relevant = [
            c.t for c in changes
            if c.object_category == spec.object_category
            and spec.target_slot in (c.to_semantic, c.from_semantic)
            and c.t < spec.t
        ]
        last = max(relevant) if relevant else None
    return (spec.t - last) if last is not None else 0.0


def zone_churn_score(
    spec: "QuestionSpec",
    changes: list[Change],
    window: float = 2.0,
) -> int:
    """Count of changes to the same semantic zone within ±window hours of spec.t.

    Zone = spec.target_slot for PRESENCE/COUNT; for LOCATION it is the slot
    the instance most recently moved TO at or before spec.t.
    """
    zone = spec.target_slot
    if zone is None and spec.instance_id is not None:
        prior = [c for c in changes if c.instance_id == spec.instance_id and c.t <= spec.t]
        zone  = prior[-1].to_semantic if prior else None
    if not zone:
        return 0
    return sum(
        1 for c in changes
        if zone in (c.to_semantic, c.from_semantic) and abs(c.t - spec.t) <= window
    )


def difficulty_score(spec: "QuestionSpec", changes: list[Change]) -> float:
    """staleness × zone_churn (the spec's 'product of two axes')."""
    return staleness_score(spec, changes) * zone_churn_score(spec, changes)


def assign_difficulty_bins(
    specs: list["QuestionSpec"],
    changes: list[Change],
) -> None:
    """Set spec.difficulty_bin to 'easy' | 'medium' | 'hard' in-place.

    Uses tertile boundaries computed over the supplied batch so the binning
    stays calibrated regardless of absolute score magnitudes.
    """
    if not specs:
        return
    # Specs with a pre-assigned bin (e.g. "stable") are excluded from tertile
    # computation and their bin is left untouched.
    dynamic = [s for s in specs if s.difficulty_bin not in ("stable",)]
    if not dynamic:
        return
    scores = [difficulty_score(s, changes) for s in dynamic]
    ordered = sorted(scores)
    n  = len(ordered)
    t1 = ordered[n // 3]
    t2 = ordered[(2 * n) // 3]
    for spec, score in zip(dynamic, scores):
        if score <= t1:
            spec.difficulty_bin = "easy"
        elif score <= t2:
            spec.difficulty_bin = "medium"
        else:
            spec.difficulty_bin = "hard"
