"""Stage B loader — CASAS episodes -> the Stage A day-level schema.

CASAS supplies the WITHIN-person variance: a handful of homes observed for
57-220 days each. It cannot supply the between-person component (four homes
is not a population), which is exactly why ATUS is the other half of the
identity.

Two source-specific decisions, both recorded in the DropReport:

* **person_id granularity.** Most CASAS labels are home-level, so the unit
  is the testbed. Where a label is resident-tagged (cairo/tulum2 use
  ``R1_``/``R2_`` prefixes) the unit is ``testbed:R1``. A home-level label
  in a two-resident home therefore MIXES residents, which inflates its
  day-to-day variance — recorded as a known bias, not silently averaged.

* **Episode-to-day assignment is by OVERLAP, not by start.** An ATUS diary
  day is the window [04:00, 04:00) and a sleep episode running 23:00 ->
  07:00 contributes its 23:00-04:00 part to one day and its 04:00-07:00
  part to the next. Assigning a CASAS episode wholly to the day it starts
  in would put a whole night on the earlier day, so CASAS "total sleep"
  would miss the morning tail and CASAS "wake" would land on the window
  boundary instead of the real waking time — the two sources would not be
  measuring the same quantity, and the sleep ICC would be garbage (measured:
  a within-person SD of 6.7 h before this was fixed). Each episode is
  therefore clipped into every diary day it overlaps.

* **valid_day.** Sensor outages look like a day with almost no labels. A
  day is valid when it has >= :data:`MIN_EPISODES_PER_DAY` labelled
  episodes AND its largest gap inside the waking window is <=
  :data:`MAX_WAKING_GAP_MIN`. The first and last calendar days of a
  recording are partial by construction and always invalid.
"""

from __future__ import annotations

import collections
import csv
import datetime
import pathlib
import re
from typing import Dict, List, Optional, Sequence, Tuple

from icc import crosswalk
from icc.schema import (DAY_END_MIN, DAY_MINUTES, DAY_START_MIN, DayRow,
                        DowType, DropReport, StartRule, spanning_start_end,
                        merge_episodes, reduce_episodes)

TESTBEDS = ("aruba", "cairo", "milan", "tulum2")
MIN_EPISODES_PER_DAY = 5
MAX_WAKING_GAP_MIN = 8 * 60
WAKING_WINDOW = (8 * 60, 22 * 60)        # clock minutes, for the gap test
RESIDENT_TAG = re.compile(r"^(R\d)_")


def _resident_of(label: str) -> Optional[str]:
    m = RESIDENT_TAG.match(label)
    return m.group(1) if m else None


def _diary_day(ts: datetime.datetime) -> datetime.date:
    """Which 04:00-anchored diary day a timestamp belongs to."""
    return (ts - datetime.timedelta(minutes=DAY_START_MIN)).date()


def _overlapping_days(start: datetime.datetime,
                      end: datetime.datetime) -> List[datetime.date]:
    """Every 04:00-anchored diary day the episode touches."""
    first, last = _diary_day(start), _diary_day(end)
    days, day = [], first
    while day <= last:
        days.append(day)
        day += datetime.timedelta(days=1)
    return days


def _minutes_from_boundary(ts: datetime.datetime,
                           day: datetime.date) -> float:
    anchor = datetime.datetime.combine(
        day, datetime.time()) + datetime.timedelta(minutes=DAY_START_MIN)
    return DAY_START_MIN + (ts - anchor).total_seconds() / 60.0


def load(root: pathlib.Path = pathlib.Path("casas"),
         testbeds: Sequence[str] = TESTBEDS
         ) -> Tuple[List[DayRow], DropReport]:
    """All testbeds reduced to day rows, plus the drop report."""
    mappings = crosswalk.included()
    mapped_labels = {lab for m in mappings for lab in m.casas_labels}
    report = DropReport(source="casas")
    rows: List[DayRow] = []

    for tb in testbeds:
        path = root / tb / "activities.csv"
        if not path.exists():
            report.drop(f"missing_testbed:{tb}")
            continue
        # Episodes are keyed by RAW LABEL, not by canonical activity: two
        # activities may legitimately read the same episodes (`wake` reads
        # the sleep episodes for their end, `sleep` for their onset), and a
        # label -> activity dict would silently give the episodes to
        # whichever mapping happened to come last in the crosswalk.
        eps: Dict[Tuple[str, datetime.date, str], List[Tuple[float, float]]] = \
            collections.defaultdict(list)
        per_day_episodes: Dict[Tuple[str, datetime.date], int] = \
            collections.Counter()
        marks: Dict[datetime.date, List[Tuple[float, float]]] = \
            collections.defaultdict(list)

        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                label = r["activity"]
                start = datetime.datetime.fromisoformat(r["start"])
                end = datetime.datetime.fromisoformat(r["end"])
                mapped = label in mapped_labels
                if not mapped:
                    report.drop("label_excluded_by_crosswalk")
                resident = _resident_of(label)
                person = f"{tb}:{resident}" if resident else tb
                # Clip the episode into every diary day it overlaps.
                for day in _overlapping_days(start, end):
                    s = _minutes_from_boundary(start, day)
                    e = _minutes_from_boundary(end, day)
                    s2, e2 = max(s, DAY_START_MIN), min(e, DAY_END_MIN)
                    if e2 <= s2:
                        continue
                    marks[day].append((s2, e2))
                    if mapped:
                        eps[(person, day, label)].append((s2, e2))
                        per_day_episodes[(person, day)] += 1

        days = sorted(marks)
        if not days:
            report.drop(f"empty_testbed:{tb}")
            continue
        partial = {days[0], days[-1]}
        valid: Dict[datetime.date, bool] = {}
        for day in days:
            spans = sorted(marks[day])
            gap = 0.0
            lo, hi = DAY_START_MIN + WAKING_WINDOW[0] - 4 * 60, \
                DAY_START_MIN + WAKING_WINDOW[1] - 4 * 60
            cursor = lo
            for s, e in spans:
                if s > cursor:
                    gap = max(gap, min(s, hi) - cursor)
                cursor = max(cursor, e)
                if cursor >= hi:
                    break
            gap = max(gap, hi - cursor) if cursor < hi else gap
            enough = sum(v for (p, d), v in per_day_episodes.items()
                         if d == day) >= MIN_EPISODES_PER_DAY
            valid[day] = (day not in partial and enough
                          and gap <= MAX_WAKING_GAP_MIN)
            if not valid[day]:
                report.drop("invalid_casas_day")

        persons = sorted({p for (p, _, _) in eps})
        labels_here = {lab for (_, _, lab) in eps}
        for person in persons:
            for day in days:
                dow = DowType.of(day.weekday()).value
                for m in mappings:
                    mine = [lab for lab in m.casas_labels if lab in labels_here]
                    if not mine:
                        continue        # this testbed cannot express it
                    episodes = [e for lab in mine
                                for e in eps.get((person, day, lab), [])]
                    rows.append(_row(person, day, dow, m.activity, m,
                                     episodes, valid[day]))
    return rows, report


def _row(person: str, day: datetime.date, dow: str, activity: str,
         mapping: crosswalk.Mapping, episodes: List[Tuple[float, float]],
         valid: bool) -> DayRow:
    """One DayRow, honouring the mapping's measure and start rule."""
    episodes = merge_episodes(episodes, mapping.merge_gap_min)
    if mapping.is_event:
        # An event reads an instant from the episodes and carries no
        # minutes: `wake` = end of the first episode, `leave_home` = start
        # of the first episode.
        if activity == "wake":
            start = spanning_start_end(episodes)
        else:
            start, _, _ = reduce_episodes(episodes, StartRule.FIRST)
        return DayRow(person_id=person, source="casas", date=day.isoformat(),
                      dow_type=dow, activity=activity,
                      participated=start is not None, start_min=start,
                      duration_min=None, n_occurrences=len(episodes),
                      valid_day=valid)
    start, duration, n = reduce_episodes(episodes, mapping.start_rule)
    return DayRow(person_id=person, source="casas", date=day.isoformat(),
                  dow_type=dow, activity=activity, participated=n > 0,
                  start_min=start, duration_min=duration, n_occurrences=n,
                  valid_day=valid)
