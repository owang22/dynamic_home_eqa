"""Stage A — the one day-level schema both sources are reduced to.

The ICC identity this package estimates needs two variance components that
no single dataset can supply:

    ATUS  (many persons x 1 day)   -> sigma2_total = between + within
    CASAS (few persons x many days) -> sigma2_within
    ICC = 1 - sigma2_within / sigma2_total

That only holds if both sources are reduced to the SAME measurement on the
SAME activity vocabulary, so every decision below is made once here and
applied to both loaders. Getting one of them wrong silently biases every
ICC, which is why they are constants in one module rather than choices
scattered through two loaders.

Decisions (all applied to both sources):

1. **Day boundary at 04:00, not midnight** (:data:`DAY_START_MIN`). A
   midnight boundary splits the main sleep episode in two, so sleep
   duration and bedtime become bimodal artefacts. 04:00 also matches the
   ATUS diary window exactly, so no re-anchoring is needed on that side.
   ``start_min`` is measured from the boundary: 0 = 04:00, 1439 = 03:59.

2. **One canonical statistic per (person, day, activity)** — otherwise
   multi-occurrence activities produce meaningless start variance. A
   bathroom trip happens six times a day; the variance of "the first one"
   is dominated by whether the person happened to get up early:
   * ``start_min``    — the occurrence chosen by the activity's
     :class:`StartRule` (first, last, or none for activities where a start
     time is not a meaningful quantity);
   * ``duration_min`` — SUM of all occurrences that day;
   * ``n_occurrences`` — count.

3. **Boundary straddling.** With the 04:00 anchor, the only activity whose
   start can straddle is sleep, and the fix is the START RULE rather than
   circular statistics: bedtime is the LAST sleep onset of the window
   (23:00 -> 1140, 01:30 -> 1290 — monotone, no wrap), and waking is a
   separate event activity whose start is the END of the first sleep
   episode. No circular mean is needed anywhere, which is the point of
   choosing 04:00. Any future activity that genuinely wraps must declare
   ``StartRule.NONE`` or the crosswalk review must add circular handling.

5. **Episode merging per activity** (``merge_gap_min`` in the crosswalk).
   Sensors fragment a night's sleep; self-report does not. Merging with a
   declared tolerance makes the granularity comparable before any statistic
   is taken. See :func:`merge_episodes`.

4. **``valid_day`` is a flag, never a silent drop.** Callers filter on it
   and the counts of what was dropped are reported (see the loaders'
   ``DropReport``).
"""

from __future__ import annotations

import dataclasses
import enum
from typing import Dict, List, Optional, Sequence, Tuple

DAY_START_MIN = 4 * 60
"""Diary day starts at 04:00 (see module docstring, decision 1)."""

DAY_MINUTES = 1440
DAY_END_MIN = DAY_START_MIN + DAY_MINUTES


class StartRule(enum.Enum):
    """Which occurrence supplies ``start_min`` for an activity."""

    FIRST = "first"
    LAST = "last"
    SPANS_END = "spans_end"   # onset of the episode ongoing at 04:00 next day
    NONE = "none"             # start time is not a meaningful quantity


class DowType(enum.Enum):
    """Weekday/weekend regime — the one covariate both loaders control for."""

    WEEKDAY = "weekday"
    WEEKEND = "weekend"

    @classmethod
    def of(cls, weekday_index: int) -> "DowType":
        """``date.weekday()`` (Mon=0) -> regime."""
        return cls.WEEKEND if weekday_index >= 5 else cls.WEEKDAY


@dataclasses.dataclass(frozen=True)
class DayRow:
    """One (person, day, activity) observation — the shared schema.

    ``start_min`` and ``duration_min`` are None when the activity did not
    occur, or when its start rule is NONE. Units: minutes.
    """

    person_id: str
    source: str                    # "atus" | "casas"
    date: str                      # ISO date of the diary day
    dow_type: str                  # DowType value
    activity: str                  # canonical activity id
    participated: bool
    start_min: Optional[float]
    duration_min: Optional[float]
    n_occurrences: int
    valid_day: bool
    weight: float = 1.0            # ATUS survey weight; 1.0 for CASAS

    FIELDS = ("person_id", "source", "date", "dow_type", "activity",
              "participated", "start_min", "duration_min", "n_occurrences",
              "valid_day", "weight")

    def as_tuple(self) -> Tuple[object, ...]:
        return tuple(getattr(self, f) for f in self.FIELDS)


@dataclasses.dataclass
class DropReport:
    """What a loader excluded and why — printed, never silently discarded."""

    source: str
    counts: Dict[str, int] = dataclasses.field(default_factory=dict)

    def drop(self, reason: str, n: int = 1) -> None:
        self.counts[reason] = self.counts.get(reason, 0) + n

    def render(self) -> str:
        if not self.counts:
            return f"{self.source}: nothing dropped"
        parts = ", ".join(f"{k}={v}" for k, v in sorted(self.counts.items()))
        return f"{self.source} drops: {parts}"


def merge_episodes(episodes: Sequence[Tuple[float, float]],
                   gap_min: float) -> List[Tuple[float, float]]:
    """Join episodes separated by <= ``gap_min`` into one.

    A source-asymmetry correction, applied identically to both sources
    (decision 5): ambient sensors fragment a night's sleep into several
    labelled episodes, while a self-reported diary records one. Comparing
    the fragmented series to the unfragmented one measures labelling
    granularity rather than behaviour. ``gap_min = 0`` leaves episodes
    untouched, which is the default for every activity where the two
    sources agree on granularity.
    """
    if gap_min <= 0 or not episodes:
        return sorted(episodes)
    merged: List[Tuple[float, float]] = []
    for s, e in sorted(episodes):
        if merged and s - merged[-1][1] <= gap_min:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def reduce_episodes(episodes: Sequence[Tuple[float, float]],
                    rule: StartRule) -> Tuple[Optional[float],
                                              Optional[float], int]:
    """Episodes [(start_min, end_min), ...] -> (start, summed duration, n).

    Episodes are clipped to the diary window and sorted by start. The
    canonical statistic definitions live here so both loaders cannot drift
    apart (decision 2 in the module docstring).
    """
    clipped: List[Tuple[float, float]] = []
    for s, e in episodes:
        s2, e2 = max(s, DAY_START_MIN), min(e, DAY_END_MIN)
        if e2 > s2:
            clipped.append((s2, e2))
    if not clipped:
        return None, None, 0
    clipped.sort()
    duration = sum(e - s for s, e in clipped)
    if rule is StartRule.NONE:
        start: Optional[float] = None
    elif rule is StartRule.SPANS_END:
        # Bedtime = onset of the episode still running at the window end,
        # the mirror image of how waking is the end of the episode already
        # running at the window start. Taking "the last onset" instead lets
        # a day whose evening sleep went unlabelled report the MORNING
        # tail's onset (0 = 04:00) as a bedtime: measured on CASAS, 9 such
        # days out of 611 supplied most of the within-person variance.
        spanning = [(s, e) for s, e in clipped if e >= DAY_END_MIN - 1e-6]
        start = spanning[-1][0] - DAY_START_MIN if spanning else None
    elif rule is StartRule.LAST:
        start = clipped[-1][0] - DAY_START_MIN
    else:
        start = clipped[0][0] - DAY_START_MIN
    return start, duration, len(clipped)


def spanning_start_end(episodes: Sequence[Tuple[float, float]]
                       ) -> Optional[float]:
    """End of the episode already running at the window START (decision 3).

    This is how ``wake`` is measured. Requiring the episode to SPAN the
    boundary — rather than taking the earliest episode's end — keeps the
    measure meaning "when did this person get up" even on a day whose sleep
    was fragmented or whose first labelled episode is an afternoon nap. When
    nobody was asleep at 04:00 (a night-shift day) waking is undefined for
    that window and the row carries None rather than a fabricated time.
    """
    for s, e in sorted(episodes):
        if s <= DAY_START_MIN + 1e-6 and e > s:
            return min(e, DAY_END_MIN) - DAY_START_MIN
    return None
