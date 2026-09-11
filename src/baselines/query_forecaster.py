"""Query forecaster: expected per-object query rates from past queries.

``QueryForecaster.expected_queries(t, horizon_hours)`` returns
``{object_id: expected number of queries in [t, t + horizon)}``. The
empirical version here is a counting model: per object, queries observed
on the training days are binned by hour of day and day type (weekday /
weekend, ``day 0 = Monday`` as everywhere in this package) and divided
by the number of training days of that type. A query's expected rate at
hour ``h`` of a weekday is then "how many weekday-``h`` queries this
object averaged during training", and a horizon integrates those hourly
rates over the slots it covers (fractional hours pro-rated).

The interface is fixed so a learned forecaster can drop in later:
construct with a rate table, or fit one with :meth:`fit_empirical`.

All times are seconds since episode start; a day is 86 400 s.
"""

from __future__ import annotations

import collections
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from baselines.types import DAY_SECONDS, Question

HOURS_PER_DAY = 24
WEEKEND_SLOTS = (5, 6)
"""Bank-relative weekday slots counted as weekend (day 0 is a Monday)."""

DAY_TYPES = ("weekday", "weekend")


def day_type_of(day_index: int) -> str:
    return "weekend" if day_index % 7 in WEEKEND_SLOTS else "weekday"


class QueryForecaster:
    """Expected query counts per object over a lookahead window.

    ``rates`` maps ``(object_id, day_type, hour)`` to the expected
    number of queries for that object in that one-hour slot of a day of
    that type. Slots never observed are simply absent (rate 0).
    """

    def __init__(self, rates: Mapping[Tuple[str, str, int], float]) -> None:
        for (obj, day_type, hour), rate in rates.items():
            if day_type not in DAY_TYPES:
                raise ValueError(f"QueryForecaster: day type {day_type!r} "
                                 f"for {obj!r} not in {DAY_TYPES}")
            if not 0 <= hour < HOURS_PER_DAY:
                raise ValueError(f"QueryForecaster: hour {hour} for {obj!r}")
            if rate < 0:
                raise ValueError(f"QueryForecaster: negative rate for "
                                 f"{obj!r}")
        self._rates = dict(rates)
        self._objects = tuple(sorted({obj for obj, _, _ in rates}))
        self._by_slot: Dict[Tuple[str, int],
                            List[Tuple[str, float]]] = (
            collections.defaultdict(list))
        for (obj, day_type, hour), rate in self._rates.items():
            self._by_slot[(day_type, hour)].append((obj, rate))

    @property
    def objects(self) -> Tuple[str, ...]:
        """Objects with any nonzero training rate."""
        return self._objects

    @classmethod
    def fit_empirical(cls, questions: Iterable[Question],
                      training_days: Sequence[int]) -> "QueryForecaster":
        """Empirical counts over the given training days.

        Questions outside ``training_days`` are ignored, so the caller
        chooses the train/held-out split by day index.
        """
        train = set(training_days)
        if not train:
            raise ValueError("QueryForecaster: no training days")
        n_days = {dt: sum(1 for d in train if day_type_of(d) == dt)
                  for dt in DAY_TYPES}
        counts: Dict[Tuple[str, str, int], int] = collections.defaultdict(int)
        for q in questions:
            if q.day_index not in train:
                continue
            hour = (q.t_query % DAY_SECONDS) // 3600
            counts[(q.object_id, day_type_of(q.day_index), hour)] += 1
        rates = {key: c / n_days[key[1]] for key, c in counts.items()
                 if n_days[key[1]] > 0}
        return cls(rates)

    def rate_at(self, object_id: str, day_type: str, hour: int) -> float:
        """The one-hour-slot rate (0 for never-observed slots)."""
        return self._rates.get((object_id, day_type, hour), 0.0)

    def expected_queries(self, t: int, horizon_hours: float
                         ) -> Dict[str, float]:
        """``{object_id: expected queries in [t, t + horizon_hours)}``.

        Integrates the hourly rate table over the window, pro-rating the
        partial slots at both ends and following day-type changes across
        midnight. Objects with zero expectation are omitted.
        """
        if horizon_hours < 0:
            raise ValueError(f"expected_queries: negative horizon "
                             f"{horizon_hours}")
        out: Dict[str, float] = collections.defaultdict(float)
        remaining = horizon_hours * 3600.0
        clock = float(t)
        while remaining > 0:
            slot_end = (clock // 3600 + 1) * 3600
            step = min(remaining, slot_end - clock)
            day_type = day_type_of(int(clock) // DAY_SECONDS)
            hour = int(clock % DAY_SECONDS) // 3600
            fraction = step / 3600.0
            for obj, rate in self._by_slot.get((day_type, hour), ()):
                out[obj] += rate * fraction
            clock += step
            remaining -= step
        return {obj: rate for obj, rate in out.items() if rate > 0.0}
