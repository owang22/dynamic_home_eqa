"""
sampling.py — joint-quota item assignment for the realism eval webapp.

Adapted from the reference time-series QA webapp's own joint-quota
sampler (marginal per-axis weights -> exact cross-product quotas via
largest-remainder rounding -> a quota-seeded deterministic shuffle per
cell). Pure logic, no FastAPI/SQLite — unit-tested directly.

change_type is the axis currently sampled (proportional to the pool, not
a fixed target — see app.py's SAMPLING_DISTRIBUTIONS). Suspicion-based
stratification (a fixed 50/50 tail/random_baseline quota) was removed
along with the suspicion-scoring machinery that fed it.
"""
from __future__ import annotations

import json
import math
import random
from collections import Counter
from typing import Optional


def normalize_distribution(
    dist: Optional[dict[str, float]], values: list[str], items: list[dict], axis: str,
) -> dict[str, float]:
    """dist=None means "uncontrolled" — weight by the pool's own empirical
    proportions for this axis, not a uniform prior (an axis like `profile`
    with a dozen unevenly-represented values should sample roughly like
    the pool, not force-equalize households the generator itself didn't
    generate evenly)."""
    if dist is None:
        counts = Counter(it[axis] for it in items)
        total = sum(counts.get(v, 0) for v in values)
        if total <= 0:
            return {v: 1.0 / len(values) for v in values} if values else {}
        return {v: counts.get(v, 0) / total for v in values}
    total = sum(dist.get(v, 0.0) for v in values)
    if total <= 0:
        return {v: 1.0 / len(values) for v in values} if values else {}
    return {v: dist.get(v, 0.0) / total for v in values}


def make_joint_sampling_quotas(
    total_items: int,
    distributions: dict[str, Optional[dict[str, float]]],
    items: list[dict],
) -> list[dict]:
    """Cross-product of every axis's values, weighted by the product of
    marginal weights, rounded to integer per-cell counts that sum exactly
    to total_items via largest-remainder rounding (deterministic tiebreak:
    sort by fractional remainder desc, then by the quota's own sorted-key
    JSON dump — matches the reference app's tiebreak convention so re-runs
    are reproducible)."""
    axes = list(distributions.keys())
    axis_values: dict[str, list[str]] = {}
    axis_weights: dict[str, dict[str, float]] = {}
    for axis in axes:
        values = sorted({it[axis] for it in items if it.get(axis) is not None})
        axis_values[axis] = values
        axis_weights[axis] = normalize_distribution(distributions[axis], values, items, axis)

    combos: list[dict] = [{}]
    for axis in axes:
        combos = [dict(c, **{axis: v}) for c in combos for v in axis_values[axis]]

    weighted = []
    for combo in combos:
        w = 1.0
        for axis in axes:
            w *= axis_weights[axis].get(combo[axis], 0.0)
        weighted.append((combo, w))

    total_weight = sum(w for _combo, w in weighted) or 1.0
    raw = [(combo, total_items * w / total_weight) for combo, w in weighted]

    def _key(combo: dict) -> str:
        return json.dumps(combo, sort_keys=True)

    counts = {_key(combo): int(math.floor(r)) for combo, r in raw}
    remainder = total_items - sum(counts.values())
    fracs = sorted(raw, key=lambda cr: (-(cr[1] - math.floor(cr[1])), _key(cr[0])))
    for combo, _r in fracs[:max(0, remainder)]:
        counts[_key(combo)] += 1

    quotas = []
    for combo, _w in weighted:
        n = counts[_key(combo)]
        if n > 0:
            quotas.append(dict(combo, n=n))
    return quotas


def item_matches_quota(item: dict, quota: dict) -> bool:
    return all(item.get(k) == v for k, v in quota.items() if k != "n")


def assign_items_joint(items: list[dict], quotas: list[dict], base_seed: str) -> list[str]:
    """For each quota independently: shuffle its matching candidates with a
    quota-specific seed and take the first n. Raises ValueError if a quota
    can't be filled — surfaced loudly (a silent short-fill would quietly
    change the study's stratification without anyone noticing)."""
    used: set[str] = set()
    assigned: list[str] = []
    for quota in quotas:
        n = quota["n"]
        candidates = [it for it in items if it["item_id"] not in used and item_matches_quota(it, quota)]
        quota_seed = f"{base_seed}:{json.dumps(quota, sort_keys=True)}"
        rng = random.Random(quota_seed)
        rng.shuffle(candidates)
        if len(candidates) < n:
            raise ValueError(
                f"quota {quota} needs {n} items but only {len(candidates)} candidates available"
            )
        picked = candidates[:n]
        used.update(it["item_id"] for it in picked)
        assigned.extend(it["item_id"] for it in picked)

    rng = random.Random(f"{base_seed}:final_order")
    rng.shuffle(assigned)
    return assigned


def assignment_seed(participant_id: str, mode: str, shared_seed: int) -> str:
    """"shared": every participant gets the identical item set/order (same
    seed always). "per_user": a stable per-participant seed derived from a
    hash of their id, same convention the reference app uses."""
    if mode == "shared":
        return str(shared_seed)
    if mode == "per_user":
        import hashlib
        return str(int(hashlib.md5(participant_id.encode()).hexdigest()[:8], 16))
    raise ValueError(f"unknown ASSIGNMENT_MODE: {mode!r}")
