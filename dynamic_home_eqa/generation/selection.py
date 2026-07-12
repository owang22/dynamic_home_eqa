"""
Stochastic, realism-weighted selection of displacement candidates.

The displacement stage over-generates by design (stages.generate_displacements):
grounding narrows the pool to physically placeable candidates, and this module
narrows further to a behaviorally plausible, run-to-run varying subset.
Selecting the entire groundable pool every time is what produces "everything
dumped on the nearest surface" datasets — over-generation is only useful if
something downstream prunes it non-deterministically.
"""
from __future__ import annotations

import numpy as np

from .cache import make_seed

# Expected object-displacement count per activity (Poisson mean), keyed by
# keyword match against the activity label. Activities are LLM-generated
# free text (see generation/stages.py), not drawn from a fixed enum, so this
# is a best-effort keyword heuristic rather than a per-profile lookup table —
# tune the keyword groups as generated activity labels reveal gaps.
_LAMBDA_KEYWORDS: list[tuple[tuple[str, ...], float]] = [
    (("breakfast", "lunch", "dinner", "cook", "meal", "snack", "party"), 3.0),
    (("clean", "tidy", "organiz", "chore", "laundry", "declutter"), 2.5),
    (("work", "desk", "study", "read", "call", "meeting"), 1.2),
    (("tv", "relax", "rest", "lounge", "nap", "movie"), 0.8),
    (("sleep", "away", "outdoor", "gym", "errand", "shower", "bath"), 0.3),
]
_DEFAULT_LAMBDA = 1.5


def lambda_moves_for(activity: str) -> float:
    """Expected displacement count for an activity label (Poisson mean, not a cap)."""
    label = activity.lower()
    for keywords, lam in _LAMBDA_KEYWORDS:
        if any(k in label for k in keywords):
            return lam
    return _DEFAULT_LAMBDA


def select_displacements(candidates, realism_scores, lambda_moves, rng,
                         temperature=1.0):
    """Select a stochastic subset of displacement candidates.

    Count is drawn from Poisson(lambda_moves), clamped to the pool size, so
    the number of objects moved varies run-to-run around the activity's
    expected value with no hard cap. Selection is weighted by realism score
    so implausible candidates are unlikely — but not impossible — to be
    chosen, preserving occasional realistic surprises.

    Args:
        candidates:     list of grounded displacement candidates.
        realism_scores: parallel list of plausibility scores in [0, 1].
        lambda_moves:   activity's expected displacement count (Poisson mean).
        rng:            seeded numpy Generator for reproducibility.
        temperature:    softmax temperature on the selection weights.
                        Lower sharpens toward high-realism candidates;
                        higher flattens toward uniform.

    Returns:
        Selected subset of candidates.
    """
    if not candidates:
        return []
    n_target = min(rng.poisson(lambda_moves), len(candidates))
    if n_target == 0:
        return []
    weights = np.exp(np.array(realism_scores) / temperature)
    weights /= weights.sum()
    idx = rng.choice(len(candidates), size=n_target, replace=False, p=weights)
    return [candidates[i] for i in idx]


def select_for_activity(
    candidates: list[dict],
    realism_scores: list[float],
    activity: str,
    household_id: str,
    day: int,
    start: float = 0.0,
    temperature: float = 1.0,
) -> list[dict]:
    """select_displacements(), with lambda_moves and a reproducible seed derived
    from (household_id, day, activity, start, "select") so selections are
    stable across re-runs and adding activities elsewhere doesn't reshuffle
    existing draws.

    start disambiguates repeat occurrences of the same activity label within a
    day (e.g. "work" split across four windows) — without it every recurrence
    drew the identical Poisson count and the identical weighted sample, so a
    repeated activity always selected the same candidates verbatim.
    """
    seed = make_seed(household_id, day, f"select_{activity}_{start:.2f}", 0)
    rng = np.random.default_rng(seed)
    lam = lambda_moves_for(activity)
    return select_displacements(candidates, realism_scores, lam, rng, temperature)
