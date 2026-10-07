"""FreMEn-style spectral switching prior f(t) for b3_perpetua_star.

f(t) modulates an edge's transition hazards over time-of-day. Sources:
  constant: f(t) = 1 (rates are time-homogeneous).
  fremen:   fit from observed change times — build the count of change
            events per time-of-day bin (all training days folded together),
            take the top-K Fourier components plus DC, reconstruct a
            non-negative rate modulator, normalize its mean to 1 so the
            base rates keep their MLE scale.

Exposed as a callable object with a cumulative integral (needed by the
closed-form Perpetua recursion, which advances posteriors by
F(t0,t1) = ∫ f). The integral is a cached per-minute cumulative sum over
one day, extended periodically — exact for the piecewise representation.
"""
from __future__ import annotations

import numpy as np

from dynbelief import MIN_PER_DAY


class SwitchingPrior:
    """f(t_min) >= 0 with mean 1 over its period, periodic. The period is
    len(per_min) — one day for the classic daily prior, seven for the weekly
    prior (Section C); any whole-day multiple is accepted."""

    def __init__(self, per_min: np.ndarray) -> None:
        assert per_min.ndim == 1 and len(per_min) % MIN_PER_DAY == 0
        per_min = np.maximum(per_min, 1e-4)
        self.per_min = per_min / per_min.mean()
        self.period = len(per_min)
        self._cum = np.concatenate([[0.0], np.cumsum(self.per_min)])

    def __call__(self, t_min: float) -> float:
        return float(self.per_min[int(t_min) % self.period])

    def cumulative(self, t0: float, t1: float) -> float:
        """∫_{t0}^{t1} f(t) dt in minutes of effective time."""
        if t1 <= t0:
            return 0.0

        def C(t: float) -> float:
            periods, rem = divmod(t, self.period)
            return periods * float(self._cum[-1]) + float(self._cum[int(rem)])

        return C(t1) - C(t0)


def constant_prior() -> SwitchingPrior:
    return SwitchingPrior(np.ones(MIN_PER_DAY))


def fremen_prior(change_times_min: list[int], top_k: int = 3,
                 bin_min: int = 10) -> SwitchingPrior:
    """Spectral fit of the time-of-day change-rate profile."""
    n_bins = MIN_PER_DAY // bin_min
    counts = np.zeros(n_bins)
    for t in change_times_min:
        counts[(int(t) % MIN_PER_DAY) // bin_min] += 1
    if counts.sum() == 0:
        return constant_prior()
    spec = np.fft.rfft(counts)
    keep = np.zeros_like(spec)
    keep[0] = spec[0]  # DC
    if top_k > 0 and len(spec) > 1:
        order = np.argsort(np.abs(spec[1:]))[::-1][:top_k] + 1
        keep[order] = spec[order]
    recon = np.fft.irfft(keep, n=n_bins)
    per_min = np.repeat(np.maximum(recon, 0.0), bin_min)
    return SwitchingPrior(per_min)


# ── Section C: weekly periodic component ─────────────────────────────────────

def weekly_gate(train_days: list[int]) -> bool:
    """A weekly component may be fit only when every day-of-week has >= 4
    training instances (brief guardrail: a weekly term on 2 weeks overfits).
    Assumes calendar data (day 0 = Monday) — meaningless on episodes
    generated without --calendar-days."""
    counts = [0] * 7
    for d in train_days:
        counts[d % 7] += 1
    return min(counts) >= 4


WEEK_MIN = 7 * MIN_PER_DAY


def fremen_prior_weekly(change_times_min: list[int], train_days: list[int],
                        top_k: int = 3, bin_min: int = 10) -> SwitchingPrior:
    """Week-period prior: per-day-of-week rate scale x day-CLASS spectral
    shape. Deliberately not a raw FFT over the 7-day axis: with a handful of
    weeks the week-scale Fourier components are noise, whereas (a) how MUCH
    motion each day-of-week carries and (b) the within-day shape of weekday
    vs weekend days are both estimable and are exactly the weekday/weekend
    conditioning the brief scopes to. Caller must check weekly_gate() first;
    this falls back to the daily fit when the gate fails.
    """
    if not weekly_gate(train_days):
        return fremen_prior(change_times_min, top_k=top_k, bin_min=bin_min)
    n_dow = [0] * 7          # observed training instances per day-of-week
    for d in train_days:
        n_dow[d % 7] += 1
    counts_dow = [0] * 7     # change events per day-of-week
    wk_times, we_times = [], []
    for t in change_times_min:
        dow = (int(t) // MIN_PER_DAY) % 7
        counts_dow[dow] += 1
        (we_times if dow >= 5 else wk_times).append(t)
    if sum(counts_dow) == 0:
        return constant_prior()
    # per-dow rate (events per observed instance), then within-day shapes
    rate_dow = [counts_dow[d] / max(n_dow[d], 1) for d in range(7)]
    mean_rate = np.mean([r for r in rate_dow]) or 1.0
    shape_wk = fremen_prior(wk_times, top_k=top_k, bin_min=bin_min).per_min
    shape_we = fremen_prior(we_times, top_k=top_k, bin_min=bin_min).per_min
    week = np.concatenate([
        (shape_we if d >= 5 else shape_wk) * max(rate_dow[d] / mean_rate, 1e-3)
        for d in range(7)])
    return SwitchingPrior(week)


def weekly_component_report(change_times_min: list[int],
                            train_days: list[int]) -> dict:
    """Per-object (or per-class) diagnostics for Section C: weekday vs
    weekend move rates, the weekly contrast, and whether a weekly component
    is SELECTED for this stream (gate passed + the contrast is above what
    Poisson noise explains, via a two-rate Poisson test)."""
    from scipy.stats import binomtest
    n_wk = sum(1 for d in train_days if d % 7 < 5)
    n_we = sum(1 for d in train_days if d % 7 >= 5)
    c_wk = sum(1 for t in change_times_min if (int(t) // MIN_PER_DAY) % 7 < 5)
    c_we = len(change_times_min) - c_wk
    r_wk = c_wk / max(n_wk, 1)
    r_we = c_we / max(n_we, 1)
    gate = weekly_gate(train_days)
    # under H0 (one rate), each event lands on a weekend day w.p. n_we/(n_wk+n_we)
    p = None
    if gate and (c_wk + c_we) > 0 and n_wk and n_we:
        p = binomtest(c_we, c_wk + c_we, n_we / (n_wk + n_we)).pvalue
    contrast = (r_we / r_wk) if r_wk > 0 else float("inf") if r_we > 0 else 1.0
    return {"gate_passed": gate, "n_events": c_wk + c_we,
            "weekday_rate": round(r_wk, 3), "weekend_rate": round(r_we, 3),
            "weekend_over_weekday": round(contrast, 3) if contrast != float("inf") else None,
            "p_value": p,
            "selected": bool(gate and p is not None and p < 0.05)}
