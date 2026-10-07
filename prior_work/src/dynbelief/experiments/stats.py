"""Bootstrap CIs and paired per-episode deltas (Bank/Eval revisions R2).

Deterministic (fixed rng) so summaries are reproducible. Paired deltas
(arm - C0 on the SAME episodes) are the high-powered arm-vs-arm statistic:
the shared streams guarantee episode alignment.
"""
from __future__ import annotations

import numpy as np

_RNG = np.random.default_rng(12345)


def boot_ci(values, n_boot: int = 2000, alpha: float = 0.05):
    """Mean + (lo, hi) percentile bootstrap CI. NaN-safe (empty -> nans)."""
    v = np.asarray([x for x in values if x == x], dtype=float)
    if len(v) == 0:
        return float("nan"), (float("nan"), float("nan"))
    if len(v) == 1:
        return float(v[0]), (float(v[0]), float(v[0]))
    idx = _RNG.integers(0, len(v), size=(n_boot, len(v)))
    means = v[idx].mean(axis=1)
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(v.mean()), (float(lo), float(hi))


def paired_delta_ci(arm_vals: dict, ref_vals: dict, n_boot: int = 2000,
                    alpha: float = 0.05):
    """Bootstrap CI of mean(arm - ref) over episodes present in BOTH, keyed by
    episode id. arm_vals/ref_vals: {episode_key: metric}."""
    keys = [k for k in arm_vals if k in ref_vals]
    d = np.array([arm_vals[k] - ref_vals[k] for k in keys], dtype=float)
    if len(d) == 0:
        return float("nan"), (float("nan"), float("nan")), 0
    if len(d) == 1:
        return float(d[0]), (float(d[0]), float(d[0])), 1
    idx = _RNG.integers(0, len(d), size=(n_boot, len(d)))
    means = d[idx].mean(axis=1)
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(d.mean()), (float(lo), float(hi)), len(d)


def fmt_ci(mean, ci, prec=3):
    if mean != mean:
        return "-"
    return f"{mean:.{prec}f} [{ci[0]:.{prec}f},{ci[1]:.{prec}f}]"


def monotone_trend(xs, ys) -> float:
    """Spearman-like sign consistency of y over x (for the C0/C5 flatness check).
    Returns the fraction of adjacent increases minus decreases in [-1,1];
    |value| near 1 = a monotone trend worth flagging."""
    pairs = sorted(zip(xs, ys))
    y = [p[1] for p in pairs if p[1] == p[1]]
    if len(y) < 3:
        return 0.0
    ups = sum(1 for a, b in zip(y, y[1:]) if b > a)
    downs = sum(1 for a, b in zip(y, y[1:]) if b < a)
    return (ups - downs) / max(1, (ups + downs))
