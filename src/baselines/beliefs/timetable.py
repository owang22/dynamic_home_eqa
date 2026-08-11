"""Belief: an object follows a timetable — predict from same-time-of-day
sightings.

Observations are binned by (time-of-day bin, day category); a query is
answered from the frequency histogram of its own bin, falling back to
whole-history most-frequent behaviour when the bin is empty.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from baselines.beliefs.base import BeliefModel
from baselines.types import DAY_SECONDS, Prediction

HOURS_PER_DAY = 24
_WEEKEND_DAYS = (5, 6)  # day_index % 7 for Saturday, Sunday (day 0 = Monday)

DAY_SCHEMES = ("all", "weekday_weekend", "per_day")
"""Supported day-category schemes: one shared category, weekday vs weekend,
or one category per day of the week."""


@dataclass(frozen=True)
class TimetableConfig:
    """Binning scheme for :class:`TimetableLookup`.

    ``bin_hours`` must divide 24 so bins tile the day exactly.
    ``day_scheme`` selects how days group into categories (see
    :data:`DAY_SCHEMES`).
    """

    bin_hours: int = 1
    day_scheme: str = "all"

    def __post_init__(self) -> None:
        if self.bin_hours <= 0 or HOURS_PER_DAY % self.bin_hours != 0:
            raise ValueError(
                f"TimetableConfig: bin_hours must divide {HOURS_PER_DAY}, "
                f"got {self.bin_hours}")
        if self.day_scheme not in DAY_SCHEMES:
            raise ValueError(
                f"TimetableConfig: day_scheme {self.day_scheme!r} "
                f"not in {DAY_SCHEMES}")

    def bin_of(self, t: int) -> Tuple[int, int]:
        """(time-of-day bin, day category) for a timestamp in seconds."""
        seconds_into_day = t % DAY_SECONDS
        time_bin = seconds_into_day // (self.bin_hours * 3600)
        day = t // DAY_SECONDS
        if self.day_scheme == "all":
            category = 0
        elif self.day_scheme == "weekday_weekend":
            category = 1 if day % 7 in _WEEKEND_DAYS else 0
        else:  # per_day
            category = day % 7
        return int(time_bin), category


class TimetableLookup(BeliefModel):
    """Predict the modal receptacle among sightings sharing the query's bin.

    The distribution is the bin's sighting-frequency histogram, normalized;
    modal ties break by recency within the bin. An empty bin (including the
    never-observed case, which the base class routes to the uniform
    fallback before this method is reached) degrades gracefully: the whole
    history is used instead, i.e. exact
    :class:`~baselines.beliefs.most_frequent.MostFrequentLocation`
    behaviour.
    """

    def __init__(self, rng: random.Random, config: TimetableConfig,
                 exclusion_floor: float = 0.0,
                 half_life_h: Optional[float] = None) -> None:
        super().__init__(rng, exclusion_floor=exclusion_floor)
        if half_life_h is not None and half_life_h <= 0:
            raise ValueError(
                f"TimetableLookup: half_life_h {half_life_h} must be > 0")
        self._config = config
        self._half_life_s = None if half_life_h is None else half_life_h * 3600

    @property
    def name(self) -> str:
        suffix = ("" if self._half_life_s is None
                  else f",hl={self._half_life_s / 3600:g}h")
        return (f"TimetableLookup(bin={self._config.bin_hours}h,"
                f"days={self._config.day_scheme}{suffix})")

    def _predict_from_history(
            self, history: List[Tuple[int, str]], t: int) -> Prediction:
        query_bin = self._config.bin_of(t)
        in_bin = [(ot, rec) for ot, rec in history
                  if self._config.bin_of(ot) == query_bin]
        pool = in_bin if in_bin else history
        counts = self._weighted_counts(pool, t, self._half_life_s)
        return self._normalized(counts, tie_break_recency=pool)
