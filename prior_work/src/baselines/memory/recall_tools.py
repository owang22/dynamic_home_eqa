"""Recall tools: prompt-sized text views over the indexed memory.

These are the TEMPORAL actions of the STAR-style loop (Sense is the
spatial one): free retrievals from long-term memory, each returning a
short text block (at most ~15 lines) for a working-memory prompt.

Each tool also returns the structured records behind the text, so the
scripted control selector can act on them without parsing its own
prompt strings; the LLM selector only ever sees the text.

All times are seconds since episode start; ages are reported in hours
relative to the caller's ``now_t`` (the query time), and no tool can
read a record newer than ``now_t``.
"""

from __future__ import annotations

import dataclasses
from typing import List, Optional, Tuple

from baselines.memory.indexed_observation_log import (IndexedObservationLog,
                                                      MemoryRecord)

DEFAULT_LIMIT = 12
"""Default record cap per recall: keeps every tool's block <= ~15 lines."""

SECONDS_PER_HOUR = 3600.0


@dataclasses.dataclass(frozen=True)
class RecallResult:
    """One recall: the prompt text block plus the records behind it."""

    text: str
    records: Tuple[MemoryRecord, ...]


def _age_h(now_t: int, t: int) -> float:
    return max(0, now_t - t) / SECONDS_PER_HOUR


def _place(log: IndexedObservationLog, receptacle_id: str) -> str:
    room = log.room_of(receptacle_id)
    return f"{receptacle_id} ({room})" if room else receptacle_id


def recall_object_history(log: IndexedObservationLog, object_id: str,
                          now_t: int,
                          limit: int = DEFAULT_LIMIT) -> RecallResult:
    """Last ``limit`` sightings and established absences of one object,
    newest-first, with ages in hours."""
    records = log.lookup(object_id=object_id, t_max=now_t, limit=limit)
    if not records:
        return RecallResult(
            text=f"memory: no records for {object_id}", records=())
    lines = [f"memory of {object_id}, newest first:"]
    for r in records:
        verb = "seen at" if r.present else "absent from"
        lines.append(f"- {_age_h(now_t, r.t):.1f}h ago: {verb} "
                     f"{_place(log, r.receptacle_id)}")
    return RecallResult(text="\n".join(lines), records=tuple(records))


def recall_receptacle_history(log: IndexedObservationLog,
                              receptacle_id: str, now_t: int,
                              limit: int = DEFAULT_LIMIT) -> RecallResult:
    """What has been SEEN at one receptacle (positive sightings only),
    newest-first, with ages in hours."""
    records = log.lookup(receptacle_id=receptacle_id, t_max=now_t,
                         present=True, limit=limit)
    if not records:
        return RecallResult(
            text=f"memory: nothing seen at {receptacle_id}", records=())
    lines = [f"objects seen at {_place(log, receptacle_id)}, newest first:"]
    for r in records:
        lines.append(f"- {_age_h(now_t, r.t):.1f}h ago: {r.object_id} "
                     f"({r.object_class})")
    return RecallResult(text="\n".join(lines), records=tuple(records))


def recall_time_pattern(log: IndexedObservationLog, object_id: str,
                        now_t: int, hour_window: int = 1,
                        limit: int = 60) -> RecallResult:
    """Where this object was seen around this hour of day on previous
    days: sightings whose hour is within ``hour_window`` of now's hour,
    aggregated per receptacle (count and freshest age)."""
    now_hour = (now_t % 86_400) // 3600
    hours = {(now_hour + d) % 24
             for d in range(-abs(hour_window), abs(hour_window) + 1)}
    records = log.lookup(object_id=object_id, t_max=now_t, present=True,
                         hours=hours, limit=limit)
    if not records:
        return RecallResult(
            text=(f"memory: no sightings of {object_id} near hour "
                  f"{now_hour:02d}:00 on any day"), records=())
    per_receptacle: dict[str, List[MemoryRecord]] = {}
    for r in records:
        per_receptacle.setdefault(r.receptacle_id, []).append(r)
    ranked = sorted(per_receptacle.items(),
                    key=lambda kv: (-len(kv[1]), kv[1][0].t * -1))
    lines = [f"sightings of {object_id} near hour {now_hour:02d}:00 "
             f"(+/-{abs(hour_window)}h), by receptacle:"]
    for receptacle, group in ranked[:12]:
        newest = group[0]
        lines.append(f"- {_place(log, receptacle)}: {len(group)}x, newest "
                     f"{_age_h(now_t, newest.t):.1f}h ago")
    return RecallResult(text="\n".join(lines), records=tuple(records))


def freshest_sighting(records: Tuple[MemoryRecord, ...]
                      ) -> Optional[MemoryRecord]:
    """Newest POSITIVE record in a recall result (records arrive
    newest-first), or None. Shared by the scripted selector."""
    for r in records:
        if r.present:
            return r
    return None
