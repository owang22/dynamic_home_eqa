"""Stage C loader — ATUS diaries -> the Stage A day-level schema.

ATUS supplies sigma2_total: one diary day per respondent, across many
respondents, so its cross-sectional variance contains BOTH the
between-person and the within-person component. It cannot separate them
(one day per person), which is why CASAS is the other half of the identity.

Three source-specific decisions that would silently corrupt the estimate if
skipped:

1. **Time heaping.** ATUS respondents round reported times to :00/:15/:30,
   producing a spike comb rather than a smooth distribution, which inflates
   the raw variance. Each day-level statistic is de-heaped by inferring its
   granularity from its own modulus (30 -> 15 -> 10 -> 5 -> 1 minutes) and
   adding U(-g/2, +g/2). The jitter is applied to the STATISTIC, not to raw
   episode boundaries, so contiguity of the diary is never broken. Both the
   raw and de-heaped variances are reported (:func:`variance_report`) so the
   effect of this choice is visible rather than assumed. Seeded.

2. **Weights.** ATUS oversamples weekends (~25% of diaries per weekend day
   vs ~10% per weekday), so an unweighted variance is not a population
   variance. Every respondent carries the final weight from the person
   record and Stage C uses weighted moments.

3. **2020 is excluded.** Two independent reasons: this extract's weight
   field is blank for all 8,782 diaries of 2020 (that year needs ATUS's
   special pandemic-period weight, a different variable), and 2020 behaviour
   contains a structural break — collection was suspended 2020-03-18 to
   2020-05-09 and the remaining days are lockdown days. Either reason alone
   would justify exclusion; both are recorded in the DropReport.
"""

from __future__ import annotations

import collections
import datetime
import pathlib
import random
import re
import sys
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "atus"))

from read_extract import (DEFAULT_EXTRACT, HOME, PERSONAL_CARE,  # noqa: E402
                          _hms_to_min, _open, layout_of)

from icc import crosswalk
from icc.schema import (DAY_END_MIN, DAY_MINUTES, DAY_START_MIN, DayRow,
                        DowType, DropReport, StartRule, spanning_start_end,
                        merge_episodes, reduce_episodes)

EXCLUDED_YEARS = (2020,)
WEIGHT_PATTERN = re.compile(r"(\d+\.\d{6})")
DATE_AT = (40, 48)
WEIGHT_AT = 48
GRANULARITIES = (30, 15, 10, 5)


def person_index(path: pathlib.Path
                 ) -> Tuple[Dict[str, datetime.date], Dict[str, float]]:
    """caseid -> diary date, and caseid -> survey weight."""
    dates: Dict[str, datetime.date] = {}
    weights: Dict[str, float] = {}
    with _open(path) as f:
        for raw in f:
            if raw[0] != "2":
                continue
            case = raw[6:20]
            d = raw[DATE_AT[0]:DATE_AT[1]]
            dates[case] = datetime.date(int(d[:4]), int(d[4:6]), int(d[6:8]))
            m = WEIGHT_PATTERN.match(raw[WEIGHT_AT:])
            if m:
                weights[case] = float(m.group(1))
    return dates, weights


def deheap(value: Optional[float], rng: random.Random) -> Optional[float]:
    """Add uniform jitter sized to the value's own inferred granularity.

    A reported 09:30 could have been anything in [09:15, 09:45) had the
    respondent not rounded; a reported 09:37 was already fine-grained. The
    modulus tells us which, per statistic (decision 1).
    """
    if value is None:
        return None
    v = int(round(value))
    for g in GRANULARITIES:
        if v % g == 0:
            return value + rng.uniform(-g / 2.0, g / 2.0)
    return value


def _diary_rows(caseid: str, day: datetime.date, weight: float,
                episodes: List[Tuple[str, int, float, float]],
                mappings: Sequence[crosswalk.Mapping],
                valid: bool, rng: random.Random) -> Iterator[DayRow]:
    """One diary's episodes -> one DayRow per canonical activity."""
    dow = DowType.of(day.weekday()).value
    for m in mappings:
        if m.activity == "leave_home":
            # Derived from LOCATION, not from an activity code: the first
            # minute of the first away-from-home spell.
            away = [(s, e) for code, where, s, e in episodes
                    if where != HOME and not (where >= 9000
                                              and code[:2] == PERSONAL_CARE)]
            start, _, n = reduce_episodes(away, StartRule.FIRST)
            yield DayRow(person_id=caseid, source="atus", date=day.isoformat(),
                         dow_type=dow, activity=m.activity,
                         participated=start is not None,
                         start_min=deheap(start, rng), duration_min=None,
                         n_occurrences=n, valid_day=valid, weight=weight)
            continue
        mine = merge_episodes(
            [(s, e) for code, where, s, e in episodes
             if any(code.startswith(p) for p in m.atus_codes)
             and (not m.atus_home_only or where == HOME)],
            m.merge_gap_min)
        if m.is_event:                       # `wake`: end of first episode
            start = spanning_start_end(mine)
            yield DayRow(person_id=caseid, source="atus", date=day.isoformat(),
                         dow_type=dow, activity=m.activity,
                         participated=start is not None,
                         start_min=deheap(start, rng), duration_min=None,
                         n_occurrences=len(mine), valid_day=valid,
                         weight=weight)
            continue
        start, duration, n = reduce_episodes(mine, m.start_rule)
        yield DayRow(person_id=caseid, source="atus", date=day.isoformat(),
                     dow_type=dow, activity=m.activity, participated=n > 0,
                     start_min=deheap(start, rng),
                     duration_min=deheap(duration, rng), n_occurrences=n,
                     valid_day=valid, weight=weight)


def iter_day_rows(path: pathlib.Path = DEFAULT_EXTRACT, seed: int = 0,
                  report: Optional[DropReport] = None) -> Iterator[DayRow]:
    """Stream day rows. 3.8 M activity records do not fit comfortably in
    memory as objects, so Stage C consumes this rather than a list."""
    col = layout_of(path)
    dates, weights = person_index(path)
    mappings = crosswalk.included()
    rng = random.Random(seed)
    rep = report if report is not None else DropReport(source="atus")

    caseid: Optional[str] = None
    episodes: List[Tuple[str, int, float, float]] = []
    offset = prev_stop = 0

    def emit() -> Iterator[DayRow]:
        if caseid is None:
            return
        day = dates.get(caseid)
        if day is None:
            rep.drop("no_diary_date")
            return
        if day.year in EXCLUDED_YEARS:
            rep.drop(f"excluded_year:{day.year}")
            return
        weight = weights.get(caseid)
        if weight is None:
            rep.drop("missing_weight")
            return
        total = sum(min(e, DAY_END_MIN) - s for _, _, s, e in episodes)
        valid = abs(total - DAY_MINUTES) < 1e-6
        if not valid:
            rep.drop("diary_not_1440_minutes")
        yield from _diary_rows(caseid, day, weight, episodes, mappings,
                               valid, rng)

    with _open(path) as f:
        for raw in f:
            if raw[0] != "3":
                continue
            case = raw[6:20]
            if case != caseid:
                yield from emit()
                caseid, episodes, offset, prev_stop = case, [], 0, 0
            code = raw[col["activity"][0]:col["activity"][1]]
            where = int(raw[col["where"][0]:col["where"][1]])
            s = _hms_to_min(raw[col["start"][0]:col["start"][1]])
            e = _hms_to_min(raw[col["stop"][0]:col["stop"][1]])
            if s + offset < prev_stop:
                offset += DAY_MINUTES
            s += offset
            e += offset
            if e < s:
                e += DAY_MINUTES
            prev_stop = e
            episodes.append((code, where, float(s), float(e)))
        yield from emit()
