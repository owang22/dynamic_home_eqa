"""Belief: per-object hazard model — exponential dwell plus a time-of-day
return histogram.

The strongest classical per-object comparator. Two estimates per object,
both from its sighting history alone:

* **Leave rate** (hazard) per receptacle, from the censoring-aware
  exponential-dwell MLE: for each consecutive sighting pair
  ``(t1, r1), (t2, r2)`` the gap ``t2 - t1`` is exposure time attributed
  to ``r1``, and a departure from ``r1`` is counted when ``r2 != r1``.
  ``rate(r) = departures(r) / exposure(r)`` — the maximum-likelihood leave
  rate under an exponential dwell whose observations are right-censored by
  the next sighting. Rates are estimated from raw durations (they are not
  counts, so the frozen count half-life does not apply to them).
* **Time-of-day return histogram**: where the object tends to be at the
  query's time-of-day bin, from the decayed sighting counts in that bin
  (frozen 24 h half-life), falling back to the whole decayed history when
  the bin is empty — exactly the timetable model's fallback shape.

Prediction at elapsed time ``dt`` since the last sighting at ``r_last``:
``p_stay = exp(-rate(r_last) * dt)`` mass on ``r_last``; the remaining
``1 - p_stay`` distributed by the return histogram.

Count floors (few-transition objects degrade to frequency, not garbage):
``rate(r_last)`` is used only when ``r_last`` has at least
``min_departures`` observed departures; otherwise the object's pooled
rate (total departures / total exposure) substitutes, and when even the
pooled history holds fewer than ``min_departures`` departures the model
returns the plain decayed-frequency distribution outright.

All times are seconds since episode start; a day is 86 400 s.
Never-observed objects fall back to uniform via the base class.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from baselines.beliefs.base import BeliefModel
from baselines.types import DAY_SECONDS, Prediction

HOURS_PER_DAY = 24


@dataclass(frozen=True)
class DwellEstimate:
    """Hazard sufficient statistics for one object (exposed for unit tests)."""

    departures: Dict[str, int]      # receptacle -> observed departures
    exposure_s: Dict[str, int]      # receptacle -> attributed exposure

    @property
    def total_departures(self) -> int:
        return sum(self.departures.values())

    @property
    def total_exposure_s(self) -> int:
        return sum(self.exposure_s.values())

    def rate(self, receptacle: str, min_departures: int) -> float | None:
        """Leave rate (1/s) for ``receptacle`` under the count floor.

        Falls back to the pooled all-receptacle rate when the receptacle
        has too few departures; ``None`` when even the pooled history is
        below the floor (caller degrades to frequency).
        """
        if (self.departures.get(receptacle, 0) >= min_departures
                and self.exposure_s.get(receptacle, 0) > 0):
            return self.departures[receptacle] / self.exposure_s[receptacle]
        if (self.total_departures >= min_departures
                and self.total_exposure_s > 0):
            return self.total_departures / self.total_exposure_s
        return None


def estimate_dwell(history: List[Tuple[int, str]]) -> DwellEstimate:
    """Censoring-aware exponential-dwell statistics from a sighting list.

    Zero-length gaps (duplicate timestamps) contribute neither exposure
    nor departures. Edge case: a single sighting yields empty statistics.
    """
    departures: Dict[str, int] = {}
    exposure: Dict[str, int] = {}
    for (t1, r1), (t2, r2) in zip(history, history[1:]):
        gap = t2 - t1
        if gap <= 0:
            continue
        exposure[r1] = exposure.get(r1, 0) + gap
        if r2 != r1:
            departures[r1] = departures.get(r1, 0) + 1
    return DwellEstimate(departures=departures, exposure_s=exposure)


@dataclass(frozen=True)
class PeriodicPersistenceConfig:
    """Fixed hyperparameters (no per-bank tuning)."""

    min_departures: int = 2       # count floor for trusting a hazard rate
    bin_hours: int = 1            # time-of-day bin width for the histogram
    half_life_h: float = 24.0     # count decay half-life (frozen, panel-wide)

    def __post_init__(self) -> None:
        if self.min_departures < 1:
            raise ValueError(
                f"PeriodicPersistenceConfig: min_departures "
                f"{self.min_departures} must be >= 1")
        if self.bin_hours <= 0 or HOURS_PER_DAY % self.bin_hours != 0:
            raise ValueError(
                f"PeriodicPersistenceConfig: bin_hours must divide "
                f"{HOURS_PER_DAY}, got {self.bin_hours}")
        if self.half_life_h <= 0:
            raise ValueError(
                f"PeriodicPersistenceConfig: half_life_h {self.half_life_h} "
                f"must be > 0")


class PeriodicPersistence(BeliefModel):
    """Last-sighting location decayed by dwell hazard, remainder by the
    time-of-day return histogram. See the module docstring for the exact
    estimators and count floors. Argmax ties break by preferring the
    last-sighted receptacle, then receptacle order — no randomness."""

    def __init__(self, rng: random.Random,
                 config: PeriodicPersistenceConfig,
                 exclusion_floor: float = 0.0) -> None:
        super().__init__(rng, exclusion_floor=exclusion_floor)
        self._cfg = config

    @property
    def name(self) -> str:
        return (f"PeriodicPersistence(min_dep={self._cfg.min_departures},"
                f"bin={self._cfg.bin_hours}h,hl={self._cfg.half_life_h:g}h)")

    def _predict_from_history(
            self, history: List[Tuple[int, str]], t: int) -> Prediction:
        half_life_s = self._cfg.half_life_h * 3600
        rate = estimate_dwell(history).rate(history[-1][1],
                                            self._cfg.min_departures)
        if rate is None:
            counts = self._weighted_counts(history, t, half_life_s)
            return self._normalized(counts, tie_break_recency=history)
        t_last, r_last = history[-1]
        p_stay = math.exp(-rate * max(0, t - t_last))
        histogram = self._return_histogram(history, t, half_life_s)
        dist = {r: (1.0 - p_stay) * p for r, p in histogram.items()}
        dist[r_last] = dist.get(r_last, 0.0) + p_stay
        total = sum(dist.values())
        dist = {r: p / total for r, p in dist.items()}
        top = max(dist.values())
        tied = [r for r in dist if dist[r] == top]
        argmax = r_last if r_last in tied else min(tied)
        return Prediction(distribution=dist, argmax=argmax)

    def _return_histogram(self, history: List[Tuple[int, str]], t: int,
                          half_life_s: float) -> Dict[str, float]:
        """Normalized decayed counts in the query's time-of-day bin,
        falling back to the whole history when the bin is empty."""
        bin_size = self._cfg.bin_hours * 3600
        query_bin = (t % DAY_SECONDS) // bin_size
        in_bin = [(ot, r) for ot, r in history
                  if (ot % DAY_SECONDS) // bin_size == query_bin]
        pool = in_bin if in_bin else history
        counts = self._weighted_counts(pool, t, half_life_s)
        total = sum(counts.values())
        return {r: c / total for r, c in counts.items()}
