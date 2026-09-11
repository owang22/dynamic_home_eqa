"""Indexed long-term memory over the agent's own observation stream.

One :class:`MemoryRecord` per object-level observation: a positive
sighting (``present=True``) or an established absence (``present=False``
-- the object was missing from a sensed receptacle's full contents).
Three exact-match lookup axes, freely composable in one
:meth:`IndexedObservationLog.lookup` call:

* spatial   -- by receptacle, or by room (when the bank exposes a
  receptacle -> room map);
* semantic  -- by object id, or by object class (from the episode
  context's ``object_classes``);
* temporal  -- a ``[t_min, t_max]`` window, a day-of-week filter and an
  hour-of-day filter.

There are no embeddings and no vector search: the banks are symbolic and
every question the generator emits names exact ids, so exact-match
indices cover the whole query space. If a caller ever needs fuzzy
matching, that is a schema change to discuss, not a retrieval model to
bolt on here.

Ground-truth isolation: the log ingests ONLY the evidence types agents
receive (:class:`~baselines.types.Observation`,
:class:`~baselines.types.SenseResult`) -- the same diet the belief models
eat. It never touches an :class:`~baselines.types.Episode` and has no
way to read a trajectory; ``tests/test_baselines_star_memory.py`` pins
this behaviourally.

All times are seconds since episode start; ``day_index = t // 86400``,
``weekday = day_index % 7`` (a bank-relative weekday slot, not a
calendar day), ``hour = (t % 86400) // 3600``.
"""

from __future__ import annotations

import dataclasses
from typing import (AbstractSet, Dict, List, Mapping, Optional, Tuple,
                    Union)

from baselines.types import DAY_SECONDS, Observation, SenseResult

SECONDS_PER_HOUR = 3600


@dataclasses.dataclass(frozen=True)
class MemoryRecord:
    """One remembered object-level observation.

    ``present`` True: ``object_id`` was seen at ``receptacle_id`` at
    ``t``. False: a sense of ``receptacle_id`` at ``t`` returned full
    contents that did not include ``object_id`` (an established
    absence). ``room_id`` is None when the bank exposes no room map.
    """

    t: int
    object_id: str
    object_class: str
    receptacle_id: str
    room_id: Optional[str]
    present: bool

    @property
    def day_index(self) -> int:
        return self.t // DAY_SECONDS

    @property
    def weekday(self) -> int:
        """Bank-relative weekday slot in [0, 7)."""
        return self.day_index % 7

    @property
    def hour(self) -> int:
        """Hour of day in [0, 24)."""
        return (self.t % DAY_SECONDS) // SECONDS_PER_HOUR


class IndexedObservationLog:
    """Per-episode memory store built from the agent's evidence stream.

    Construct once per episode with the agent-visible vocabulary
    (``object_classes`` from the episode context; ``rooms`` an optional
    receptacle -> room map the driver reads from the bank), then
    :meth:`ingest` every piece of evidence in delivery order -- the same
    order the belief models receive it. Records are stored append-only;
    lookups return newest-first.
    """

    def __init__(self, object_classes: Mapping[str, str],
                 rooms: Optional[Mapping[str, str]] = None) -> None:
        self._object_classes: Dict[str, str] = dict(object_classes)
        self._rooms: Dict[str, str] = dict(rooms or {})
        self._records: List[MemoryRecord] = []
        # Index lists hold positions in self._records, ascending.
        self._by_object: Dict[str, List[int]] = {}
        self._by_receptacle: Dict[str, List[int]] = {}

    def __len__(self) -> int:
        return len(self._records)

    @property
    def rooms(self) -> Mapping[str, str]:
        """The receptacle -> room map this log labels records with."""
        return self._rooms

    def room_of(self, receptacle_id: str) -> Optional[str]:
        return self._rooms.get(receptacle_id)

    def ensure_object(self, object_id: str, object_class: str) -> None:
        """Register an object discovered after construction (open object
        set). Idempotent; an existing class is never overwritten."""
        self._object_classes.setdefault(object_id, object_class or "unknown")

    # ------------------------------------------------------------ ingest

    def ingest(self, evidence: Union[Observation, SenseResult]) -> None:
        """Fold one piece of agent-visible evidence into the store.

        An :class:`Observation` is one positive record. A
        :class:`SenseResult` is object-level evidence about every known
        object: one positive record per object in its contents, one
        absence record for each known object NOT in them -- the same
        expansion the belief base class applies.
        """
        if isinstance(evidence, Observation):
            self._append(evidence.t, evidence.object_id,
                         evidence.receptacle_id, present=True)
            return
        if isinstance(evidence, SenseResult):
            present = set(evidence.contents)
            for obj in evidence.contents:
                self._append(evidence.t, obj, evidence.receptacle_id,
                             present=True)
            for obj in self._object_classes:
                if obj not in present:
                    self._append(evidence.t, obj, evidence.receptacle_id,
                                 present=False)
            return
        raise TypeError(
            f"IndexedObservationLog.ingest: unsupported evidence type "
            f"{type(evidence).__name__}; only agent-visible Observation/"
            f"SenseResult may enter memory")

    def _append(self, t: int, object_id: str, receptacle_id: str,
                present: bool) -> None:
        record = MemoryRecord(
            t=t, object_id=object_id,
            object_class=self._object_classes.get(object_id, "unknown"),
            receptacle_id=receptacle_id,
            room_id=self._rooms.get(receptacle_id), present=present)
        position = len(self._records)
        self._records.append(record)
        self._by_object.setdefault(object_id, []).append(position)
        self._by_receptacle.setdefault(receptacle_id, []).append(position)

    # ------------------------------------------------------------ lookup

    def lookup(self, *, object_id: Optional[str] = None,
               object_class: Optional[str] = None,
               receptacle_id: Optional[str] = None,
               room_id: Optional[str] = None,
               t_min: Optional[int] = None, t_max: Optional[int] = None,
               weekdays: Optional[AbstractSet[int]] = None,
               hours: Optional[AbstractSet[int]] = None,
               present: Optional[bool] = None,
               limit: Optional[int] = None) -> List[MemoryRecord]:
        """Records matching every given filter, newest-first.

        All filters compose (object X, in room Y, on weekday-slot
        mornings). ``weekdays`` and ``hours`` are sets of allowed
        weekday slots / hours of day. ``limit`` caps the returned list
        (None: no cap). ``t_max`` is the caller's "now": pass the query
        time so memory never reads past it.
        """
        positions = self._candidate_positions(object_id, receptacle_id)
        out: List[MemoryRecord] = []
        for position in reversed(positions):
            record = self._records[position]
            if t_max is not None and record.t > t_max:
                continue
            if t_min is not None and record.t < t_min:
                continue
            if object_id is not None and record.object_id != object_id:
                continue
            if receptacle_id is not None and record.receptacle_id != receptacle_id:
                continue
            if object_class is not None and record.object_class != object_class:
                continue
            if room_id is not None and record.room_id != room_id:
                continue
            if weekdays is not None and record.weekday not in weekdays:
                continue
            if hours is not None and record.hour not in hours:
                continue
            if present is not None and record.present != present:
                continue
            out.append(record)
            if limit is not None and len(out) >= limit:
                break
        return out

    def _candidate_positions(self, object_id: Optional[str],
                             receptacle_id: Optional[str]) -> List[int]:
        """Narrowest applicable index (records are scanned newest-first
        from it; an id nothing was recorded under yields no candidates)."""
        candidates: List[List[int]] = []
        if object_id is not None:
            candidates.append(self._by_object.get(object_id, []))
        if receptacle_id is not None:
            candidates.append(self._by_receptacle.get(receptacle_id, []))
        if not candidates:
            return list(range(len(self._records)))
        return min(candidates, key=len)
