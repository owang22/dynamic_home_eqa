"""FreMEn validation on synthetic signals with known periodicity.

The brief's requirement, verbatim in spirit: a bad FreMEn implementation
would silently understate the strongest classical baseline — an error in
our favor — so the implementation must recover known structure before it
is allowed near HOMER+. Three properties are checked:

1. a clean 24 h square wave is recovered: the top component sits at the
   24 h period and the reconstruction tracks the signal;
2. recovery survives observation gaps (40% of samples masked), because
   the projection must not depend on complete sampling even though
   HOMER+ happens to provide it;
3. a two-frequency signal (24 h + 7 d) yields both periods in the top
   components, in amplitude order.
"""

from __future__ import annotations

import numpy as np
import pytest

from homer.fremen import MIN_PER_DAY, Spectral

WEEK = 7 * MIN_PER_DAY


def square_wave(t: np.ndarray, period: float, duty_lo: float,
                duty_hi: float) -> np.ndarray:
    frac = (t % period) / period
    return ((duty_lo <= frac) & (frac < duty_hi)).astype(float)


def test_recovers_a_daily_cycle() -> None:
    t = np.arange(0, 28 * MIN_PER_DAY, 10.0)
    s = square_wave(t, MIN_PER_DAY, 0.25, 0.50)   # "in the kitchen 06:00-12:00"
    m = Spectral(order=2).fit(t, s)
    top_period = 2 * np.pi / m.components[0][0]
    assert top_period == pytest.approx(MIN_PER_DAY, rel=1e-6)
    # Reconstruction separates the on-phase from the off-phase decisively.
    on = np.mean([m.p(float(x)) for x in t[s > 0.5]])
    off = np.mean([m.p(float(x)) for x in t[s < 0.5]])
    assert on - off > 0.4
    assert m.a0 == pytest.approx(0.25, abs=0.02)


def test_survives_observation_gaps() -> None:
    rng = np.random.default_rng(7)
    t = np.arange(0, 28 * MIN_PER_DAY, 10.0)
    s = square_wave(t, MIN_PER_DAY, 0.25, 0.50)
    keep = rng.random(len(t)) > 0.4               # drop 40% of samples
    m = Spectral(order=2).fit(t[keep], s[keep])
    top_period = 2 * np.pi / m.components[0][0]
    assert top_period == pytest.approx(MIN_PER_DAY, rel=1e-6)
    on = np.mean([m.p(float(x)) for x in t[s > 0.5]])
    off = np.mean([m.p(float(x)) for x in t[s < 0.5]])
    assert on - off > 0.35


def test_two_frequencies_rank_by_amplitude() -> None:
    t = np.arange(0, 8 * WEEK, 10.0)
    daily = 0.4 * np.cos(2 * np.pi * t / MIN_PER_DAY)
    weekly = 0.2 * np.cos(2 * np.pi * t / WEEK)
    s = np.clip(0.5 + daily + weekly, 0, 1)
    m = Spectral(order=2).fit(t, s)
    periods = sorted(2 * np.pi / w for w, _, _ in m.components)
    assert periods[0] == pytest.approx(MIN_PER_DAY, rel=1e-6)
    assert periods[1] == pytest.approx(WEEK, rel=1e-6)
    amps = {round(2 * np.pi / w): a for w, a, _ in m.components}
    assert amps[MIN_PER_DAY] > amps[WEEK]         # amplitude order preserved
