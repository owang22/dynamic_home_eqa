"""Ground truth for one household, on the hourly grid the experiment uses.

Wraps the canonical HOMER+ trace (``src/homer/loader.py``) in the accessor
the budgeted loop needs: "where is object o at hour h of day d". The class
deliberately owns ALL ground-truth access — the loop reads it, the agent
never receives it, and :class:`beliefsim.policies.AgentView` has no
reference to it. That is the same isolation-by-construction the baselines
package gets from ``Episode``/``EpisodeContext``.

Two properties of HOMER+ that shape everything downstream:

* **Days are self-contained.** Each day is an independent VirtualHome
  rollout of a sampled schedule, opening with a full-state snapshot at
  ~06:00. Objects do not physically persist across the midnight boundary;
  what makes yesterday informative about today is schedule regularity, not
  continuity. An agent's stale observation is therefore evidence about a
  recurring habit, not about an object that has been sitting still.
* **There is no weekly structure.** Day-of-week is not a variable in the
  generator (confirmed by the recovered spectra,
  ``reports/homer_spectra/``), so any belief model keyed on weekday is
  fitting noise here. Timetable's ``day_scheme`` is left at ``"all"`` for
  that reason.

The hourly grid runs 07:00-23:00 (:data:`HOURS`), matching the pilot's
query window: the day-initial snapshot lands at ~06:00 so state is defined
throughout, and 24:00 is excluded because the day ends there.
"""

from __future__ import annotations

import bisect
import collections
import dataclasses
import pathlib
from typing import Dict, List, Mapping, Sequence, Tuple

from homer.loader import TraceRow, read_traces

HOURS: Tuple[int, ...] = tuple(range(7, 24))
"""Hours of the day at which the agent may sense and the belief is scored."""

SECONDS_PER_DAY = 86_400
"""Matches ``baselines.types.DAY_SECONDS``: the belief models reused from
that package parse ``day_index = t // DAY_SECONDS`` and time-of-day from
``t % DAY_SECONDS``, so global time must be expressed on the same clock."""


def to_seconds(day: int, hour: int) -> int:
    """Global timestamp on the baselines clock (seconds since day 0, 00:00)."""
    return day * SECONDS_PER_DAY + hour * 3600


@dataclasses.dataclass(frozen=True)
class World:
    """Hourly ground truth plus the metric definitions derived from it."""

    household: str
    objects: Tuple[str, ...]
    receptacles: Tuple[str, ...]
    object_classes: Mapping[str, str]
    learn_days: Tuple[int, ...]
    score_days: Tuple[int, ...]
    _state: Mapping[Tuple[str, int], Mapping[int, str]]
    _modal: Mapping[str, str]

    def location(self, object_id: str, day: int, hour: int) -> str:
        """True receptacle of ``object_id`` at (day, hour)."""
        return self._state[(object_id, day)][hour]

    def habitual(self, object_id: str) -> str:
        """The object's modal receptacle over the LEARNING days.

        Defines the displaced-instant slice. Computed from ground truth over
        the learning period only, and used exclusively for scoring — no
        agent or belief model ever receives it. Restricting the slice this
        way is what separates "the model knows where things usually are"
        from "the model can find a thing that has moved"; on HOMER+ the
        former accounts for ~91% of instants and swamps everything else.
        """
        return self._modal[object_id]

    def is_displaced(self, object_id: str, day: int, hour: int) -> bool:
        return self.location(object_id, day, hour) != self._modal[object_id]


def _global_day(row: TraceRow, n_learn_days: int) -> int:
    """Day index on one continuous timeline.

    The canonical trace numbers each SPLIT from zero, so raw ``day_index``
    values 0-9 denote both training days and test days. The budgeted loop
    walks a single timeline and keys ground truth by day, so test days are
    shifted past the training block. Keying by the raw index instead
    silently merges the two splits' change-points for days 0-9 — the state
    table then answers with whichever split's rows sorted last.
    """
    return row.day_index + (n_learn_days if row.split == "test" else 0)


def _hourly_state(rows: Sequence[TraceRow]
                  ) -> Dict[Tuple[str, int], Dict[int, str]]:
    """(object, day) -> {hour: receptacle} on the HOURS grid.

    The canonical trace stores change-points, so state at an hour is the
    most recent change-point at or before it. An object whose first
    change-point of the day is later than 07:00 carries that day's first
    known state backwards: HOMER+ days open with a complete snapshot, so
    this only fires for the rare object whose snapshot row is timestamped a
    few minutes after the hour.
    """
    times: Dict[Tuple[str, int], List[float]] = collections.defaultdict(list)
    recs: Dict[Tuple[str, int], List[str]] = collections.defaultdict(list)
    for r in sorted(rows, key=lambda r: (r.object_id, r.day_index,
                                         r.timestamp)):
        times[(r.object_id, r.day_index)].append(r.timestamp)
        recs[(r.object_id, r.day_index)].append(r.receptacle_id)

    out: Dict[Tuple[str, int], Dict[int, str]] = {}
    for key, ts in times.items():
        by_hour: Dict[int, str] = {}
        for hour in HOURS:
            i = bisect.bisect_right(ts, float(hour * 60)) - 1
            by_hour[hour] = recs[key][i] if i >= 0 else recs[key][0]
        out[key] = by_hour
    return out


def load_world(traces_dir: pathlib.Path, household: str) -> World:
    """Build the world for one household from the committed traces.

    The pilot's train/test split is kept as the learn/score split so the
    scored window is unchanged from the superseded experiment and the two
    remain comparable. Its MEANING has changed: the learning days are no
    longer handed to the models as complete state, they are simply the days
    over which the agent spends its budget before scoring begins.
    """
    rows = read_traces(traces_dir, household)
    learn_days = tuple(sorted({r.day_index for r in rows
                               if r.split == "train"}))
    rows = [dataclasses.replace(r, day_index=_global_day(r, len(learn_days)))
            for r in rows]
    state = _hourly_state(rows)
    objects = tuple(sorted({r.object_id for r in rows}))
    receptacles = tuple(sorted({r.receptacle_id for r in rows}))
    score_days = tuple(sorted({r.day_index for r in rows
                               if r.split == "test"}))

    modal: Dict[str, str] = {}
    for obj in objects:
        counts: collections.Counter = collections.Counter()
        for day in learn_days:
            counts.update(state[(obj, day)].values())
        modal[obj] = counts.most_common(1)[0][0]

    # "class#id" is the loader's object id format; the class half is shared
    # across households and is what the pooled model borrows statistics over.
    classes = {o: o.split("#")[0] for o in objects}

    missing = [(o, d) for o in objects for d in learn_days + score_days
               if (o, d) not in state]
    if missing:
        raise ValueError(f"Household{household}: {len(missing)} (object, day) "
                         f"cells absent from the trace, e.g. {missing[:3]}")

    return World(household=household, objects=objects,
                 receptacles=receptacles, object_classes=classes,
                 learn_days=learn_days, score_days=score_days,
                 _state=state, _modal=modal)
