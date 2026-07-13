"""
Judge-quality metrics against human bands.

All operate on parallel lists of (judge_score in [0,1], human_band in 0-3).
The canonical judge-score -> band mapping (score_to_band) lives here so the
label-set builder and the harness agree by construction.
"""
from __future__ import annotations

import statistics
from typing import Optional

# Strict-rubric band cutoffs, aligned to _REALISM_SYSTEM_STRICT's own scale
# (0.8-1.0 typical, 0.5-0.7 plausible-uncommon, 0.2-0.4 contrived, 0.0-0.1
# absurd); gap values fall to the nearer band.
def score_to_band(score: float) -> int:
    if score >= 0.75:
        return 3
    if score >= 0.45:
        return 2
    if score >= 0.15:
        return 1
    return 0


BAND_LABEL = {3: "typical", 2: "plausible-uncommon", 1: "contrived", 0: "absurd"}


def spearman(scores: list[float], bands: list[int]) -> Optional[float]:
    """Spearman rank correlation. Ties are averaged (scipy). None if fewer
    than 3 points or zero variance."""
    if len(scores) < 3:
        return None
    try:
        from scipy.stats import spearmanr
    except Exception:
        return _spearman_fallback(scores, bands)
    rho, _p = spearmanr(scores, bands)
    if rho != rho:  # NaN (zero variance)
        return None
    return float(rho)


def _spearman_fallback(scores: list[float], bands: list[int]) -> Optional[float]:
    def ranks(xs: list[float]) -> list[float]:
        order = sorted(range(len(xs)), key=lambda i: xs[i])
        r = [0.0] * len(xs)
        i = 0
        while i < len(xs):
            j = i
            while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rs, rb = ranks(scores), ranks([float(b) for b in bands])
    n = len(scores)
    mrs, mrb = sum(rs) / n, sum(rb) / n
    num = sum((a - mrs) * (b - mrb) for a, b in zip(rs, rb))
    den = (sum((a - mrs) ** 2 for a in rs) * sum((b - mrb) ** 2 for b in rb)) ** 0.5
    return None if den == 0 else num / den


def band_separation(scores: list[float], bands: list[int]) -> dict[int, dict]:
    """mean/std judge score within each human band. Monotonically increasing
    means with non-overlapping spreads = the judge separates the bands."""
    buckets: dict[int, list[float]] = {0: [], 1: [], 2: [], 3: []}
    for s, b in zip(scores, bands):
        buckets[b].append(s)
    out: dict[int, dict] = {}
    for b in (0, 1, 2, 3):
        vals = buckets[b]
        out[b] = {
            "n": len(vals),
            "mean": (sum(vals) / len(vals)) if vals else None,
            "std": (statistics.pstdev(vals) if len(vals) > 1 else 0.0) if vals else None,
        }
    return out


def confusion(scores: list[float], bands: list[int]) -> dict:
    """4x4 confusion of predicted band (score_to_band) vs human band, plus
    exact-match / off-by-one / over- vs under-scoring rates."""
    mat = [[0] * 4 for _ in range(4)]  # mat[human][pred]
    exact = off1 = over = under = 0
    for s, human in zip(scores, bands):
        pred = score_to_band(s)
        mat[human][pred] += 1
        d = pred - human
        if d == 0:
            exact += 1
        if abs(d) <= 1:
            off1 += 1
        if d > 0:
            over += 1
        elif d < 0:
            under += 1
    n = len(scores) or 1
    return {
        "matrix": mat,
        "exact_rate": exact / n,
        "within_one_rate": off1 / n,
        "over_rate": over / n,     # judge scored HIGHER than the human (its known failure)
        "under_rate": under / n,
        "n": len(scores),
    }


def worst_disagreements(
    items: list[tuple], k: int = 10,
) -> list[dict]:
    """items: (candidate, judge_score). Ranked by |predicted - human| then by
    raw score gap. Returns dict rows for the report."""
    rows = []
    for c, s in items:
        pred = score_to_band(s)
        rows.append({
            "candidate_id": c.candidate_id,
            "scene": c.scene,
            "object": c.object_category,
            "relation": c.target_relationship,
            "anchor": c.target_anchor,
            "activity": c.activity,
            "human_band": c.human_band,
            "judge_score": round(s, 2),
            "pred_band": pred,
            "band_gap": pred - c.human_band,
            "notes": c.notes,
        })
    rows.sort(key=lambda r: (abs(r["band_gap"]), abs(r["judge_score"] - r["human_band"] / 3.0)), reverse=True)
    return rows[:k]
