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
    (("breakfast", "lunch", "dinner", "cook", "meal", "snack", "party"), 6.0),
    (("clean", "tidy", "organize", "chore", "laundry", "declutter"), 6.0),
    (("work", "desk", "study", "read", "call", "meeting"), 5.0),
    (("tv", "relax", "rest", "lounge", "nap", "movie"), 4.0),
    (("sleep", "gym", "errand", "shower", "bath"), 3.0),
    (("away", "outdoor"), 1.0),
]
_DEFAULT_LAMBDA = 3.0


def lambda_moves_for(activity: str) -> float:
    """Expected displacement count for an activity label (Poisson mean, not a cap)."""
    label = activity.lower()
    for keywords, lam in _LAMBDA_KEYWORDS:
        if any(k in label for k in keywords):
            return lam
    return _DEFAULT_LAMBDA


# Judge-score floor for selection eligibility. Grounded in the judge harness's
# measured band separation (results/reports/prompting_p2.md, strict_ctx_fs:
# band means 0.11 absurd / 0.36 contrived / 0.50 plausible / 0.80 natural) —
# 0.3 sits between the absurd and contrived means, so it rejects what the
# judge calls absurd and most of contrived while keeping plausible/natural.
# This deliberately replaces the old "unlikely but not impossible" philosophy:
# measured on real generations, a window whose pool was junk-dominated STILL
# selected from it (72% of selected candidates scored <0.3, mean selected
# realism 0.25), because the Poisson draw was a quota. Below-floor candidates
# are now simply not moves — a window where nothing plausible was proposed
# moves nothing, which is itself realistic behavior.
REALISM_FLOOR = 0.3


def select_displacements(candidates, realism_scores, lambda_moves, rng,
                         temperature=1.0,
                         realism_floor=REALISM_FLOOR):
    """Select a stochastic subset of displacement candidates.

    THE FINAL COUNT-SHAPER: the caller (pipeline) runs the replay-gate
    preflight FIRST (no-op/capacity/unbacked-anchor — the same gates
    build_manifest enforces), so `candidates` is already the pool of moves
    that will actually materialize if drawn. That makes lambda_moves a clean
    scene-activity knob: the number of manifest events per window is
    min(Poisson(lambda), pool), with no downstream gate silently eating into
    the drawn count.

    Candidates scoring below `realism_floor` are ineligible outright — the
    judge's verdict is a gate, not merely a weight. Among eligible candidates,
    count is drawn from Poisson(lambda_moves) as a CAP (clamped to the eligible
    pool size, possibly 0), so the number of objects moved varies run-to-run
    around the activity's expected value and can naturally be zero: a quiet
    window is a valid outcome, not a failure to fill a quota. Selection among
    eligible candidates is weighted by realism score so stronger candidates
    are favored. (The old per-anchor repeat-downweight is retired: surface
    spreading is the proposer's job now — the live surface-occupancy block
    and the vary-target_anchor prompt rule — not a sampler-side correction.)

    Args:
        candidates:     list of gate-surviving displacement candidates.
        realism_scores: parallel list of plausibility scores in [0, 1].
        lambda_moves:   activity's expected displacement count (Poisson mean).
        rng:            seeded numpy Generator for reproducibility.
        temperature:    softmax temperature on the selection weights.
                        Lower sharpens toward high-realism candidates;
                        higher flattens toward uniform.
        realism_floor:  absolute judge-score eligibility threshold (see
                        REALISM_FLOOR for how the default was chosen).

    Returns:
        Selected subset of candidates (possibly empty).
    """
    if not candidates:
        return []
    eligible = [i for i, s in enumerate(realism_scores) if s >= realism_floor]
    if not eligible:
        return []
    n_target = min(rng.poisson(lambda_moves), len(eligible))
    if n_target == 0:
        return []
    elig_scores = np.array([realism_scores[i] for i in eligible])
    weights = np.exp(elig_scores / temperature)
    weights /= weights.sum()
    idx = rng.choice(len(eligible), size=n_target, replace=False, p=weights)
    return [candidates[eligible[i]] for i in idx]


def select_for_activity(
    candidates: list[dict],
    realism_scores: list[float],
    activity: str,
    household_id: str,
    day: int,
    start: float = 0.0,
    temperature: float = 1.0,
    activity_scale: float = 1.0,
) -> list[dict]:
    """select_displacements(), with lambda_moves and a reproducible seed derived
    from (household_id, day, activity, start, "select") so selections are
    stable across re-runs and adding activities elsewhere doesn't reshuffle
    existing draws.

    start disambiguates repeat occurrences of the same activity label within a
    day (e.g. "work" split across four windows) — without it every recurrence
    drew the identical Poisson count and the identical weighted sample, so a
    repeated activity always selected the same candidates verbatim.

    activity_scale: the scene-activity knob. Multiplies every window's
    Poisson mean, so 2.0 roughly doubles how many objects move in a day and
    0.5 halves it, uniformly across activity types — the single number to
    turn when a dataset needs busier or quieter homes. It shapes the FINAL
    manifest count directly because the pipeline gate-preflights the pool
    before this draw (see select_displacements).

    (There is deliberately no per-object repeat-move penalty and no per-anchor
    repeat-downweight here: proposals are instance-explicit for seats and
    spawn fresh instances for abundant clutter, and surface spreading is
    prompt-side — the sampler stays a pure realism-weighted Poisson draw.)
    """
    seed = make_seed(household_id, day, f"select_{activity}_{start:.2f}", 0)
    rng = np.random.default_rng(seed)
    lam = lambda_moves_for(activity) * activity_scale
    return select_displacements(candidates, realism_scores, lam, rng, temperature)
