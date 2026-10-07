"""Shared fitting utilities for the rate models.

Input format everywhere: `observation_history` = list of bank observation rows
{day, t_min, parents: {object_label: receptacle_label}} (held-out objects
already stripped by the runner). All statistics below are derived from this
stream ONLY (L1). Calendar covariates derived from t_min are allowed (L2);
nothing here may consult a profile YAML (L3 assertion in features()).
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np

from dynbelief import MIN_PER_DAY

MIN_PER_WEEK = 7 * MIN_PER_DAY


def default_class(obj_id: str) -> str:
    from dynbelief.profiles.schema import default_class as dc
    return dc(obj_id)


def consecutive_pairs(history: list[dict]) -> dict[str, list[tuple[int, str, int, str]]]:
    """Per object: consecutive same-day observation pairs (t1, r1, t2, r2) —
    the sufficient statistics for hazard MLE (same-day only: overnight pairs
    conflate the closed gap with organic motion; measured earlier in the
    project to inflate leave-hazards)."""
    rows = sorted(history, key=lambda r: r["t_min"])
    prev: dict[str, tuple[int, str]] = {}
    out: dict[str, list] = defaultdict(list)
    for row in rows:
        for o, r in row["parents"].items():
            if o in prev:
                t1, r1 = prev[o]
                if t1 // MIN_PER_DAY == row["t_min"] // MIN_PER_DAY:
                    out[o].append((t1, r1, row["t_min"], r))
            prev[o] = (row["t_min"], r)
    return dict(out)


def hazard_mle(history: list[dict]) -> dict[str, float]:
    """Per-CLASS constant leave rate (per minute): changed pairs / total time.
    Reference: the persistence-filter survival view (Rosen et al.) with an
    exponential survival function -> lambda is the MLE of the change hazard."""
    pairs = consecutive_pairs(history)
    num: dict[str, float] = defaultdict(float)
    den: dict[str, float] = defaultdict(float)
    for o, ps in pairs.items():
        c = default_class(o)
        for (t1, r1, t2, r2) in ps:
            num[c] += float(r1 != r2)
            den[c] += (t2 - t1)
    return {c: (num[c] / den[c] if den[c] > 0 else 0.0) for c in den}


def occupancy_counts(history: list[dict], candidates: list[str],
                     alpha: float = 0.5):
    """Per-object and per-class Laplace-smoothed empirical occupancy over the
    candidate axis. Returns (per_obj, per_class) dicts of np arrays."""
    idx = {c: i for i, c in enumerate(candidates)}
    per_obj: dict[str, np.ndarray] = {}
    per_cls: dict[str, np.ndarray] = {}
    for row in history:
        for o, r in row["parents"].items():
            v = per_obj.setdefault(o, np.zeros(len(candidates)))
            if r in idx:
                v[idx[r]] += 1
            cv = per_cls.setdefault(default_class(o), np.zeros(len(candidates)))
            if r in idx:
                cv[idx[r]] += 1
    def norm(d):
        return {k: (v + alpha) / (v + alpha).sum() for k, v in d.items()}
    return norm(per_obj), norm(per_cls)


# ── calendar features (L2-allowed; L3-asserted) ──────────────────────────────

def calendar_features(t: int) -> np.ndarray:
    """Fourier features on 24h + 168h (W1) plus the weekend flag and
    weekend x daily-harmonic interactions. Derived from t ONLY — asserting the
    L3 rule structurally: no household/profile input exists in scope."""
    day = 2 * math.pi * (t % MIN_PER_DAY) / MIN_PER_DAY
    week = 2 * math.pi * (t % MIN_PER_WEEK) / MIN_PER_WEEK
    weekend = 1.0 if ((t // MIN_PER_DAY) % 7) >= 5 else 0.0   # Sa/Su (calendar)
    base = [math.sin(day), math.cos(day), math.sin(2 * day), math.cos(2 * day),
            math.sin(week), math.cos(week), math.sin(2 * week), math.cos(2 * week),
            weekend]
    inter = [weekend * base[0], weekend * base[1], weekend * base[2], weekend * base[3]]
    return np.array(base + inter)


def split_history(history: list[dict], frac: float = 0.8):
    """Chronological fit/validation split by DAY for held-out-likelihood
    hyperparameter selection (L4). Returns (fit_rows, val_rows); val empty when
    there are not >=2 distinct days (W2: cold start — caller must log)."""
    days = sorted({r["day"] for r in history})
    if len(days) < 2:
        return history, []
    cut = days[max(1, int(round(len(days) * frac))) - 1]
    return [r for r in history if r["day"] <= cut], [r for r in history if r["day"] > cut]


def heldout_loglik(rm, val_rows: list[dict], candidates: list[str]) -> float:
    """Mean log-likelihood of held-out snapshot states under the rate model's
    occupancy prior (pure prior likelihood — never query accuracy; L4)."""
    if not val_rows:
        return float("nan")
    tot, n = 0.0, 0
    for row in val_rows:
        for o, r in row["parents"].items():
            p = np.array([max(1e-9, rm.occupancy(o, c, row["t_min"])) for c in candidates])
            p = p / p.sum()
            j = candidates.index(r) if r in candidates else None
            if j is not None:
                tot += math.log(max(1e-9, p[j]))
                n += 1
    return tot / max(1, n)
