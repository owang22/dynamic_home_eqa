"""The four REGISTERED atypicality transformations (charter -> charter).

Per the hard rules, these pure functions are the ONLY sanctioned way to
produce atypical charters — never hand- or model-authored. Each transform:

  * operates on the normalized dict form (charter.raw) and returns a new
    Charter via charter_from_dict (so V5 normalization has already run),
  * leaves object AFFINITIES and placements untouched — only timing/roles,
  * records itself in the output's `transformation` block with parameters,
  * sets derived_from to the source household id and renames the household
    (…_typ_v1 -> …__<transform>_<params>),
  * inherits the source's status: a transformation of a VERIFIED charter is
    itself valid-by-construction (the transform is registered code); a
    transformation of a DRAFT charter stays DRAFT.

Timing edits work on the weekly timeline (minute 0 = Monday 00:00), so a
phase shift that pushes a block across midnight moves it to the right
calendar day and the loader's wrap semantics (end <= start spans midnight)
re-emerge naturally.
"""
from __future__ import annotations

import copy
from typing import Callable

from dynbelief.charters.schema import (
    DAYS, DAY_IDX, MIN_PER_DAY, MIN_PER_WEEK, Charter, charter_from_dict, parse_hhmm,
)


def _fmt(minute: int) -> str:
    minute %= MIN_PER_DAY
    return f"{minute // 60:02d}:{minute % 60:02d}"


def _stamp(data: dict, source: Charter, name: str, params: dict, slug: str) -> dict:
    data["household"] = f"{source.household}__{slug}"
    data["derived_from"] = source.household
    data["transformation"] = {"type": name, "params": copy.deepcopy(params)}
    data["status"] = source.status
    return data


def _reblock(blocks_weekly: list[tuple[int, int, str]]) -> list[dict]:
    """[(week_start_min, duration, activity)] -> schedule block dicts,
    merging identical (activity, start, end) across days."""
    grouped: dict[tuple, list[str]] = {}
    for w0, dur, act in blocks_weekly:
        w0 %= MIN_PER_WEEK
        day, start = divmod(w0, MIN_PER_DAY)
        end = (start + dur) % MIN_PER_DAY
        grouped.setdefault((act, start, end), []).append(DAYS[day])
    out = []
    for (act, start, end), days in grouped.items():
        days = sorted(set(days), key=DAY_IDX.get)
        out.append({"activity": act, "days": days,
                    "start": _fmt(start), "end": _fmt(end)})
    out.sort(key=lambda b: (DAY_IDX[b["days"][0]], parse_hhmm(b["start"])))
    return out


def _map_schedules(source: Charter,
                   fn: Callable[[int, int, str, str], list[tuple[int, int, str]]]) -> dict:
    """Apply fn(week_start_min, duration_min, activity, resident_id) ->
    [(new_week_start, new_duration, activity)] to every scheduled day-block."""
    data = copy.deepcopy(source.raw)
    for rr in data.get("residents") or []:
        weekly = []
        for b in rr.get("schedule") or []:
            start, end = parse_hhmm(b["start"]), parse_hhmm(b["end"])
            dur = (end - start) if end > start else (end - start + MIN_PER_DAY)
            for d in b["days"]:
                w0 = DAY_IDX[d] * MIN_PER_DAY + start
                weekly.extend(fn(w0, dur, b["activity"], rr["id"]))
        rr["schedule"] = _reblock(weekly)
    return data


# ── 1. phase_shift {hours} ──────────────────────────────────────────────────

def phase_shift(source: Charter, hours: float) -> Charter:
    """Shift every schedule block by `hours` (mod one week). +10h turns an
    office day household into a night-shift one with identical structure."""
    shift = int(round(hours * 60))
    data = _map_schedules(source, lambda w0, dur, act, rid: [(w0 + shift, dur, act)])
    slug = f"phase_shift_{'m' if hours < 0 else 'p'}{abs(hours):g}h"
    return charter_from_dict(_stamp(data, source, "phase_shift", {"hours": hours}, slug))


# ── 2. block_permutation {swap: [[days_a], [days_b]]} ───────────────────────

def block_permutation(source: Charter, swap: list[list[str]]) -> Charter:
    """Swap the schedules of two equal-length day sets pairwise
    (e.g. [[Sa,Su],[Mo,Tu]]: weekend routine runs on Mon/Tue and vice
    versa). Days not listed keep their schedule."""
    days_a, days_b = swap
    if len(days_a) != len(days_b):
        raise ValueError("block_permutation: day sets must have equal length")
    m = {}
    for a, b in zip(days_a, days_b):
        m[DAY_IDX[a]], m[DAY_IDX[b]] = DAY_IDX[b], DAY_IDX[a]

    def fn(w0, dur, act, rid):
        day, start = divmod(w0, MIN_PER_DAY)
        return [(m.get(day, day) * MIN_PER_DAY + start, dur, act)]

    data = _map_schedules(source, fn)
    slug = "blockperm_" + "".join(days_a) + "-" + "".join(days_b)
    return charter_from_dict(_stamp(data, source, "block_permutation", {"swap": swap}, slug))


# ── 3. role_reassignment {activity, from, to} ───────────────────────────────

def role_reassignment(source: Charter, activity: str, from_id: str, to_id: str) -> Charter:
    """Move every schedule block of `activity` from resident `from_id` to
    `to_id` (who cooks / who does the school run flips)."""
    data = copy.deepcopy(source.raw)
    residents = {r["id"]: r for r in data.get("residents") or []}
    if from_id not in residents or to_id not in residents:
        raise ValueError(f"role_reassignment: unknown resident in {from_id}->{to_id}")
    moved = [b for b in residents[from_id].get("schedule") or []
             if b["activity"] == activity]
    if not moved:
        raise ValueError(f"role_reassignment: {from_id} has no {activity!r} blocks")
    residents[from_id]["schedule"] = [b for b in residents[from_id]["schedule"]
                                      if b["activity"] != activity]
    residents[to_id].setdefault("schedule", []).extend(copy.deepcopy(moved))
    slug = f"role_{activity}_{from_id}-to-{to_id}"
    return charter_from_dict(_stamp(data, source, "role_reassignment",
                                    {"activity": activity, "from": from_id, "to": to_id},
                                    slug))


# ── 4. compression {window: [start, end]} ───────────────────────────────────

def compression(source: Charter, window: list[str]) -> Charter:
    """Affinely squeeze each day's 24h of activity into `window`
    ([\"16:00\",\"23:00\"]: the whole routine plays out compressed into the
    evening; durations scale by window/24h). Wrapping blocks are anchored by
    their start day."""
    w0, w1 = parse_hhmm(window[0]), parse_hhmm(window[1])
    if not w1 > w0:
        raise ValueError("compression: window end must be after start (same day)")
    scale = (w1 - w0) / MIN_PER_DAY

    def fn(ws, dur, act, rid):
        day, start = divmod(ws, MIN_PER_DAY)
        new_start = w0 + int(round(start * scale))
        new_dur = max(1, int(round(dur * scale)))
        return [(day * MIN_PER_DAY + new_start, new_dur, act)]

    data = _map_schedules(source, fn)
    # jitter scales with time itself, or compressed days re-inflate to overlap
    for a in (data.get("activities") or {}).values():
        if "jitter_min" in a:
            a["jitter_min"] = max(1, int(round(a["jitter_min"] * scale)))
    slug = f"compress_{window[0].replace(':', '')}-{window[1].replace(':', '')}"
    return charter_from_dict(_stamp(data, source, "compression", {"window": window}, slug))


REGISTERED = {
    "phase_shift": phase_shift,
    "block_permutation": block_permutation,
    "role_reassignment": role_reassignment,
    "compression": compression,
}


def apply_transform(source: Charter, kind: str, **params) -> Charter:
    if kind not in REGISTERED:
        raise ValueError(f"unregistered transformation {kind!r}; "
                         f"registered: {sorted(REGISTERED)}")
    if kind == "role_reassignment":
        return role_reassignment(source, params["activity"], params["from"], params["to"])
    return REGISTERED[kind](source, **params)
