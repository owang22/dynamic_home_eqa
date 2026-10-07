"""Phase 2 — evaluation protocols E1 and E2 over the canonical trace.

E1 (standard localization): models see every training-split row; the test
split is NEVER observed. Queries ask each object's location at fixed
timestamps on test days — pure forecasting. Feeding test-day observations
up to the query instant would make the persistence floor an oracle (the
canonical rows ARE the change-points, so "last observation" would equal
the truth); withholding them is what lets the floors and the models
separate.

Query timestamps: every hour on the hour from 07:00 to 23:00 inclusive
(17 per day). The day-initial row sits at ~06:00, so state is defined at
every query; 24:00 is excluded because the day ends there.

E2 (held-out object generalization): identical, except the mask's k
objects contribute ZERO training rows. Every method instead receives the
held-out object's INITIAL PLACEMENT — its receptacle at the first snapshot
of training day 0 — as a static fact. That is the brief's "initial
placement only", frozen here so every method sees exactly the same thing.
Masks come in several draws because k=2 from a small mover pool is
high-variance; the spread across draws is part of the result.
"""

from __future__ import annotations

import collections
import dataclasses
import bisect
from typing import Dict, List, Sequence, Tuple

from homer.loader import TraceRow

QUERY_HOURS = tuple(range(7, 24))          # 07:00 .. 23:00 inclusive


@dataclasses.dataclass(frozen=True)
class Query:
    household_id: str
    day_index: int                          # test-split day number
    timestamp: float                        # minutes from midnight
    object_id: str
    truth: str


class StateIndex:
    """Piecewise-constant state lookup over one split's rows."""

    def __init__(self, rows: Sequence[TraceRow]) -> None:
        self._times: Dict[Tuple[str, int], List[float]] = \
            collections.defaultdict(list)
        self._recs: Dict[Tuple[str, int], List[str]] = \
            collections.defaultdict(list)
        for r in sorted(rows, key=lambda r: (r.object_id, r.day_index,
                                             r.timestamp)):
            key = (r.object_id, r.day_index)
            self._times[key].append(r.timestamp)
            self._recs[key].append(r.receptacle_id)

    def at(self, object_id: str, day_index: int, t: float) -> str | None:
        key = (object_id, day_index)
        times = self._times.get(key)
        if not times:
            return None
        i = bisect.bisect_right(times, t) - 1
        return self._recs[key][i] if i >= 0 else None


def initial_placements(train_rows: Sequence[TraceRow]) -> Dict[str, str]:
    """Each object's receptacle at the first snapshot of training day 0."""
    day0 = [r for r in train_rows if r.day_index == 0]
    t0 = min(r.timestamp for r in day0)
    placements: Dict[str, str] = {}
    for r in day0:
        if r.timestamp == t0:
            placements[r.object_id] = r.receptacle_id
    # Objects whose first day-0 row is later than t0 (should not happen —
    # day-initial state covers everyone) fall back to their earliest row.
    for r in sorted(day0, key=lambda r: r.timestamp):
        placements.setdefault(r.object_id, r.receptacle_id)
    return placements


def build_queries(rows: Sequence[TraceRow]) -> List[Query]:
    """The fixed E1/E2 query set: hourly, every object, every test day."""
    test = [r for r in rows if r.split == "test"]
    state = StateIndex(test)
    objects = sorted({r.object_id for r in rows})
    days = sorted({r.day_index for r in test})
    household = rows[0].household_id
    queries: List[Query] = []
    for day in days:
        for hour in QUERY_HOURS:
            t = float(hour * 60)
            for obj in objects:
                truth = state.at(obj, day, t)
                if truth is not None:
                    queries.append(Query(household_id=household,
                                         day_index=day, timestamp=t,
                                         object_id=obj, truth=truth))
    return queries


def hourly_occupancy(train_rows: Sequence[TraceRow]
                     ) -> Dict[str, List[Dict[int, str]]]:
    """object -> per-train-day {hour: receptacle}, sampled on the hour.

    The shared discretization every statistical baseline trains on (hours
    0-23; before the ~06:00 day-initial snapshot the day's first known
    state is used, since HOMER+ days are self-contained and nothing moves
    before wake-up).
    """
    state = StateIndex(train_rows)
    days = sorted({r.day_index for r in train_rows})
    objects = sorted({r.object_id for r in train_rows})
    out: Dict[str, List[Dict[int, str]]] = {o: [] for o in objects}
    for obj in objects:
        for day in days:
            byhour: Dict[int, str] = {}
            first: str | None = None
            for hour in range(24):
                rec = state.at(obj, day, float(hour * 60))
                if rec is None:
                    if first is None:
                        # find the day's first known state once
                        key = (obj, day)
                        times = state._times.get(key)
                        first = (state._recs[(obj, day)][0]
                                 if times else None)
                    rec = first
                if rec is not None:
                    byhour[hour] = rec
            out[obj].append(byhour)
    return out
