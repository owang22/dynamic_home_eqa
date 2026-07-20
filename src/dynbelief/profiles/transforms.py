"""The four REGISTERED atypicality transformations (profile -> profile).

Per the hard rules, these pure functions are the ONLY sanctioned way to
produce atypical profiles — never hand- or model-authored. Each transform:

  * operates on the normalized dict form (profile.raw) and returns a new
    Profile via profile_from_dict (so V5 normalization has already run),
  * leaves object AFFINITIES and placements untouched — only timing/roles,
  * records itself in the output's `transformation` block with parameters,
  * sets derived_from to the source household id and renames the household
    (…_typ_v1 -> …__<transform>_<params>),
  * inherits the source's status: a transformation of a VERIFIED profile is
    itself valid-by-construction (the transform is registered code); a
    transformation of a DRAFT profile stays DRAFT.

Timing edits work on the weekly timeline (minute 0 = Monday 00:00), so a
phase shift that pushes a block across midnight moves it to the right
calendar day and the loader's wrap semantics (end <= start spans midnight)
re-emerge naturally.
"""
from __future__ import annotations

import copy
from typing import Callable

from dynbelief.profiles.schema import (
    DAYS, DAY_IDX, MIN_PER_DAY, MIN_PER_WEEK, Profile, profile_from_dict, parse_hhmm,
)


def _fmt(minute: int) -> str:
    minute %= MIN_PER_DAY
    return f"{minute // 60:02d}:{minute % 60:02d}"


def _stamp(data: dict, source: Profile, name: str, params: dict, slug: str) -> dict:
    data["household"] = f"{source.household}__{slug}"
    data["derived_from"] = source.household
    data["transformation"] = {"type": name, "params": copy.deepcopy(params)}
    data["status"] = source.status
    return data


def _reblock(blocks_weekly: list) -> list[dict]:
    """[(week_start_min, duration, activity[, anchor])] -> schedule block dicts,
    merging identical (activity, start, end, anchor) across days."""
    grouped: dict[tuple, list[str]] = {}
    for item in blocks_weekly:
        w0, dur, act = item[0], item[1], item[2]
        anchor = item[3] if len(item) > 3 else "clock"
        w0 %= MIN_PER_WEEK
        day, start = divmod(w0, MIN_PER_DAY)
        end = (start + dur) % MIN_PER_DAY
        grouped.setdefault((act, start, end, anchor), []).append(DAYS[day])
    out = []
    for (act, start, end, anchor), days in grouped.items():
        days = sorted(set(days), key=DAY_IDX.get)
        blk = {"activity": act, "days": days, "start": _fmt(start), "end": _fmt(end)}
        if anchor != "clock":
            blk["anchor"] = anchor
        out.append(blk)
    out.sort(key=lambda b: (DAY_IDX[b["days"][0]], parse_hhmm(b["start"])))
    return out


def _map_schedules(source: Profile,
                   fn: Callable[[int, int, str, str], list]) -> dict:
    """Apply fn(week_start_min, duration_min, activity, resident_id) ->
    [(new_week_start, new_duration, activity)] to every scheduled day-block.
    The block's anchor is carried onto every image it produces."""
    data = copy.deepcopy(source.raw)
    for rr in data.get("residents") or []:
        weekly = []
        for b in rr.get("schedule") or []:
            start, end = parse_hhmm(b["start"]), parse_hhmm(b["end"])
            dur = (end - start) if end > start else (end - start + MIN_PER_DAY)
            anchor = b.get("anchor", "clock")
            for d in b["days"]:
                w0 = DAY_IDX[d] * MIN_PER_DAY + start
                for img in fn(w0, dur, b["activity"], rr["id"]):
                    weekly.append((img[0], img[1], img[2], anchor))
        rr["schedule"] = _reblock(weekly)
    return data


# ── day-instance helpers for the shift-remapping transforms (T1/T2/T3) ──────

def _instances(rr: dict) -> list[dict]:
    """Explode a resident's schedule into per-day block instances:
    {activity, day (idx), start, end, dur, anchor}. end may exceed 1440 (wrap)."""
    out = []
    for b in rr.get("schedule") or []:
        start, end = parse_hhmm(b["start"]), parse_hhmm(b["end"])
        dur = (end - start) if end > start else (end - start + MIN_PER_DAY)
        for d in b["days"]:
            out.append({"activity": b["activity"], "day": DAY_IDX[d],
                        "start": start, "dur": dur, "anchor": b.get("anchor", "clock")})
    return out


def _pack_instances(instances: list[dict]) -> list[dict]:
    """Per-day block instances -> merged schedule block dicts (group identical
    activity/start/dur/anchor across days). Wrapping handled by end%1440."""
    grouped: dict[tuple, list[int]] = {}
    for it in instances:
        key = (it["activity"], it["start"], it["dur"], it["anchor"])
        grouped.setdefault(key, []).append(it["day"])
    out = []
    for (act, start, dur, anchor), days in grouped.items():
        end = (start + dur) % MIN_PER_DAY
        blk = {"activity": act, "days": sorted({DAYS[d] for d in days}, key=DAY_IDX.get),
               "start": _fmt(start), "end": _fmt(end)}
        if anchor != "clock":
            blk["anchor"] = anchor
        out.append(blk)
    out.sort(key=lambda b: (DAY_IDX[b["days"][0]], parse_hhmm(b["start"])))
    return out


def _find_shift(instances: list[dict], shift_activity, workdays_hint):
    """Locate the base work block: the named activity, else the longest
    clock-anchored non-sleep block. Returns (activity, set(workday idxs))."""
    if shift_activity:
        days = {it["day"] for it in instances if it["activity"] == shift_activity}
        return shift_activity, days
    cand = [it for it in instances
            if it["anchor"] == "clock" and "sleep" not in it["activity"].lower()]
    if not cand:
        raise ValueError("T1/T2: cannot locate a work block; pass shift_activity")
    best = max(cand, key=lambda it: it["dur"])
    days = {it["day"] for it in instances if it["activity"] == best["activity"]}
    return best["activity"], days


# ── 1. phase_shift {hours} ──────────────────────────────────────────────────

def phase_shift(source: Profile, hours: float) -> Profile:
    """Shift every schedule block by `hours` (mod one week). +10h turns an
    office day household into a night-shift one with identical structure."""
    shift = int(round(hours * 60))
    data = _map_schedules(source, lambda w0, dur, act, rid: [(w0 + shift, dur, act)])
    slug = f"phase_shift_{'m' if hours < 0 else 'p'}{abs(hours):g}h"
    return profile_from_dict(_stamp(data, source, "phase_shift", {"hours": hours}, slug))


# ── 2. block_permutation {swap: [[days_a], [days_b]]} ───────────────────────

def block_permutation(source: Profile, swap: list[list[str]]) -> Profile:
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
    return profile_from_dict(_stamp(data, source, "block_permutation", {"swap": swap}, slug))


# ── 3. role_reassignment {activity, from, to} ───────────────────────────────

def role_reassignment(source: Profile, activity: str, from_id: str, to_id: str) -> Profile:
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
    return profile_from_dict(_stamp(data, source, "role_reassignment",
                                    {"activity": activity, "from": from_id, "to": to_id},
                                    slug))


# ── 4. compression {window: [start, end]} ───────────────────────────────────

def compression(source: Profile, window: list[str]) -> Profile:
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
    return profile_from_dict(_stamp(data, source, "compression", {"window": window}, slug))


# ═══════════════════════════════════════════════════════════════════════════
#  Addendum v2 registry: realistic shift-work transformations (T1-T4).
#  All DETERMINISTIC code on VERIFIED typical profiles. Object bindings and
#  placements are inherited byte-for-byte; only schedule TIMING changes.
# ═══════════════════════════════════════════════════════════════════════════

_MAX_FILLER_GAP = 90     # min: collapse the base work-day gap to this on repack
_WAKE_GAP = 15           # min after waking before the first activity
_RETURN_SLEEP_GAP = 60   # min after a shift ends before day-sleep begins


def _remap_workday(instances_day: list[dict], shift_act: str,
                   shift_start: int, shift_end: int, sleep_dur: int,
                   recovery_extra: int = 0) -> list[dict]:
    """Rebuild ONE workday's block instances around an overnight shift
    [shift_start, shift_end] (wraps). Rule-based re-anchoring:
      shift block   -> [shift_start, shift_end]
      day sleep     -> shift_end + gap, length sleep_dur (+recovery_extra)
      wake-anchored -> packed from wake in base order, base meal-gaps kept,
                       the work-day gap collapsed to _MAX_FILLER_GAP
      shift_start   -> ends at shift_start (pre-shift departure)
      shift_end     -> begins at shift_end (post-shift return)
      clock (other) -> unchanged
    Returns new instances for that day (start may exceed 1440 for the wrap)."""
    day = instances_day[0]["day"]
    d0 = day * MIN_PER_DAY
    out = []
    # 1. shift
    out.append({"activity": shift_act, "day": day, "start": shift_start % MIN_PER_DAY,
                "dur": (shift_end - shift_start) % MIN_PER_DAY or MIN_PER_DAY,
                "anchor": "clock"})
    # 2. day sleep (replaces the base workday sleep block)
    sleep_start = (shift_end + _RETURN_SLEEP_GAP)
    wake = sleep_start + sleep_dur + recovery_extra
    out.append({"activity": "day_sleep", "day": day, "start": sleep_start % MIN_PER_DAY,
                "dur": sleep_dur + recovery_extra, "anchor": "shift_end"})
    # 3. wake-anchored, packed from wake
    wake_blocks = sorted([it for it in instances_day if it["anchor"] == "wake"],
                         key=lambda it: it["start"])
    cursor = wake + _WAKE_GAP
    prev_end = None
    for it in wake_blocks:
        if prev_end is not None:
            gap = min(max(0, it["start"] - prev_end_base), _MAX_FILLER_GAP)
            cursor = prev_new_end + gap
        out.append({"activity": it["activity"], "day": day, "start": cursor % MIN_PER_DAY,
                    "dur": it["dur"], "anchor": "wake"})
        prev_end_base = it["start"] + it["dur"]
        prev_new_end = cursor + it["dur"]
        prev_end = it["start"]
        cursor = prev_new_end
    # 4. shift_start-anchored (end at shift_start)
    for it in [x for x in instances_day if x["anchor"] == "shift_start"]:
        out.append({"activity": it["activity"], "day": day,
                    "start": (shift_start - it["dur"]) % MIN_PER_DAY,
                    "dur": it["dur"], "anchor": "shift_start"})
    # 5. shift_end-anchored (begin at shift_end + base offset from base shift end)
    for it in [x for x in instances_day if x["anchor"] == "shift_end"]:
        out.append({"activity": it["activity"], "day": day,
                    "start": (shift_end + 0) % MIN_PER_DAY, "dur": it["dur"],
                    "anchor": "shift_end"})
    # 6. other clock blocks (not sleep, not the shift) kept as-is
    for it in instances_day:
        if it["anchor"] == "clock" and it["activity"] != shift_act \
                and "sleep" not in it["activity"].lower():
            out.append(dict(it))
    return out


def night_shift_reversion(source: Profile, work_block_start: str = "23:00",
                          work_block_end: str = "07:00", workdays: list[str] | None = None,
                          transition_block: bool = True,
                          shift_activity: str | None = None) -> Profile:
    """T1. On workdays, remap the base work block to an overnight window and
    re-anchor the dependent chain (day-sleep after the shift, meals relative to
    wake). Off-days are copied UNCHANGED (reversion) except the first off-day
    after the last shift, which gets an extended recovery sleep (the transition
    block). Bindings/placements untouched."""
    data = copy.deepcopy(source.raw)
    ws, we = parse_hhmm(work_block_start), parse_hhmm(work_block_end)
    for rr in data.get("residents") or []:
        insts = _instances(rr)
        shift_act, shift_days = _find_shift(insts, shift_activity, workdays)
        wdays = {DAY_IDX[d] for d in workdays} if workdays else shift_days
        if not wdays:
            continue
        sleep_dur = max((it["dur"] for it in insts
                         if "sleep" in it["activity"].lower() and it["day"] in wdays),
                        default=465)
        new_insts = []
        last_workday = max(wdays)
        transition_day = (last_workday + 1) % 7
        for d in range(7):
            day_insts = [it for it in insts if it["day"] == d]
            if not day_insts:
                continue
            if d in wdays:
                new_insts += _remap_workday(day_insts, shift_act, ws, we, sleep_dur)
            elif transition_block and d == transition_day:
                # recovery sleep after the final shift; drop base blocks it covers
                rec_start = (we + _RETURN_SLEEP_GAP)
                rec_dur = sleep_dur + 120
                rec_end = rec_start + rec_dur
                new_insts.append({"activity": "recovery_sleep", "day": d,
                                  "start": rec_start % MIN_PER_DAY, "dur": rec_dur,
                                  "anchor": "shift_end"})
                for it in day_insts:
                    s = it["start"]; e = s + it["dur"]
                    if "sleep" in it["activity"].lower():
                        continue                      # base off-day sleep replaced
                    if s < rec_end and e > rec_start:
                        continue                      # overlaps recovery -> drop
                    new_insts.append(dict(it))
            else:
                new_insts += [dict(it) for it in day_insts]   # pure reversion
        rr["schedule"] = _pack_instances(new_insts)
    slug = f"atyp_t1_night_{work_block_start.replace(':', '')}-{work_block_end.replace(':', '')}"
    params = {"work_block_start": work_block_start, "work_block_end": work_block_end,
              "workdays": workdays, "transition_block": transition_block,
              "shift_activity": shift_activity}
    out = profile_from_dict(_stamp(data, source, "night_shift_reversion", params, slug))
    out.raw["household"] = out.household
    return out


# ── T2 workday_pattern {pattern} ────────────────────────────────────────────

_T2_PATTERNS = {
    "three_twelves": {"workdays": ["Mo", "Tu", "We"], "shift": ["07:00", "19:30"]},  # VERIFY [nursing 3x12]
    "weekend_worker": {"workdays": ["Tu", "We", "Th", "Fr", "Sa"], "shift": None},   # VERIFY [BLS]
    "mwf_parttime": {"workdays": ["Mo", "We", "Fr"], "shift": None},                  # VERIFY
}


def _remap_dayshift(day_insts: list[dict], shift_act: str, base_shift_start: int,
                    shift_start: int, shift_end: int) -> list[dict]:
    """Rebuild one workday around a long DAYTIME shift [shift_start, shift_end]:
    morning wake-blocks packed to end at shift_start, evening wake-blocks packed
    from shift_end, night sleep filling the gap between evening's end and the
    morning's start. Used by T2.three_twelves."""
    day = day_insts[0]["day"]
    out = [{"activity": shift_act, "day": day, "start": shift_start,
            "dur": (shift_end - shift_start) % MIN_PER_DAY, "anchor": "clock"}]
    # pre-shift departure blocks end at shift_start; morning packs before them
    pre = [it for it in day_insts if it["anchor"] == "shift_start"]
    pre_total = sum(it["dur"] for it in pre)
    cur = shift_start - pre_total
    for it in pre:
        out.append({"activity": it["activity"], "day": day, "start": cur % MIN_PER_DAY,
                    "dur": it["dur"], "anchor": "shift_start"})
        cur += it["dur"]
    morning_edge = shift_start - pre_total
    wake = sorted([it for it in day_insts if it["anchor"] == "wake"],
                  key=lambda it: it["start"])
    morning = [it for it in wake if it["start"] < base_shift_start]
    evening = [it for it in wake if it["start"] >= base_shift_start]
    cur = morning_edge
    for it in reversed(morning):        # pack morning backward before departure
        cur -= it["dur"]
        out.append({"activity": it["activity"], "day": day, "start": cur % MIN_PER_DAY,
                    "dur": it["dur"], "anchor": "wake"})
    morning_start = cur
    cur = shift_end                     # post-shift return, then evening
    for it in [x for x in day_insts if x["anchor"] == "shift_end"]:
        out.append({"activity": it["activity"], "day": day, "start": cur % MIN_PER_DAY,
                    "dur": it["dur"], "anchor": "shift_end"})
        cur += it["dur"]
    # pack the evening tight so it does not wrap past midnight into the next
    # (often off-)day's early sleep; leave a 15-min pre-midnight margin.
    ev_total = sum(it["dur"] for it in evening)
    room = (MIN_PER_DAY - 15) - (cur % MIN_PER_DAY)     # minutes to 23:45 today
    gap = max(0, min(15, (room - ev_total) // max(1, len(evening)))) if evening else 0
    cur += gap
    for it in evening:
        out.append({"activity": it["activity"], "day": day, "start": cur % MIN_PER_DAY,
                    "dur": it["dur"], "anchor": "wake"})
        cur += it["dur"] + gap
    evening_end = cur
    # night sleep (reuse this resident's own sleep activity name) fills the gap
    sleep_name = next((it["activity"] for it in day_insts
                       if "sleep" in it["activity"].lower()), "sleep")
    sleep_dur = (morning_start + MIN_PER_DAY - evening_end)
    if sleep_dur > 30:
        out.append({"activity": sleep_name, "day": day, "start": evening_end % MIN_PER_DAY,
                    "dur": sleep_dur, "anchor": "clock"})
    return out


def workday_pattern(source: Profile, pattern: str) -> Profile:
    """T2. Reassign which calendar days use the base WORKDAY template vs the
    base OFF-DAY template, per `pattern`. three_twelves additionally remaps the
    workday around a stretched 12h day shift. Bindings/placements untouched."""
    if pattern not in _T2_PATTERNS:
        raise ValueError(f"workday_pattern: unknown {pattern!r}; {list(_T2_PATTERNS)}")
    spec = _T2_PATTERNS[pattern]
    new_workdays = {DAY_IDX[d] for d in spec["workdays"]}
    data = copy.deepcopy(source.raw)
    for rr in data.get("residents") or []:
        insts = _instances(rr)
        shift_act, base_workdays = _find_shift(insts, None, None)
        base_shift_start = next((it["start"] for it in insts
                                 if it["activity"] == shift_act and it["day"] in base_workdays), 0)
        wd_ref, off_pool = min(base_workdays), {it["day"] for it in insts} - base_workdays
        off_ref = min(off_pool) if off_pool else None
        wd_tpl = [it for it in insts if it["day"] == wd_ref]
        off_tpl = [it for it in insts if it["day"] == off_ref] if off_ref is not None else []
        new_insts = []
        for d in range(7):
            tpl = [dict(it, day=d) for it in (wd_tpl if d in new_workdays else off_tpl)]
            if d in new_workdays and pattern == "three_twelves" and spec["shift"]:
                ss, se = parse_hhmm(spec["shift"][0]), parse_hhmm(spec["shift"][1])
                new_insts += _remap_dayshift(tpl, shift_act, base_shift_start, ss, se)
            else:
                new_insts += tpl
        rr["schedule"] = _pack_instances(new_insts)
    slug = f"atyp_t2_{pattern}"
    out = profile_from_dict(_stamp(data, source, "workday_pattern", {"pattern": pattern}, slug))
    out.raw["household"] = out.household
    return out


# ── T3 split_shift {block1, block2} ─────────────────────────────────────────

def split_shift(source: Profile, block1: str = "10:00-14:00",
                block2: str = "17:00-23:00") -> Profile:
    """T3. Replace the single work block with two; relocate cook/dinner into the
    midday gap and move evening wind-down past block2."""
    b1s, b1e = [parse_hhmm(x) for x in block1.split("-")]
    b2s, b2e = [parse_hhmm(x) for x in block2.split("-")]
    data = copy.deepcopy(source.raw)
    for rr in data.get("residents") or []:
        insts = _instances(rr)
        shift_act, wdays = _find_shift(insts, None, None)
        new = []
        for it in insts:
            if it["day"] in wdays and it["activity"] == shift_act:
                new.append({**it, "start": b1s, "dur": (b1e - b1s) % MIN_PER_DAY})
                new.append({**it, "activity": shift_act, "start": b2s,
                            "dur": (b2e - b2s) % MIN_PER_DAY})
            elif it["day"] in wdays and it["activity"] in ("cook_dinner", "dinner"):
                # into the midday gap between the two blocks
                new.append({**it, "start": (b1e + 15 + (it["start"] % 45)) % MIN_PER_DAY,
                            "anchor": "clock"})
            elif it["day"] in wdays and it["anchor"] == "wake" and "tv" in it["activity"]:
                new.append({**it, "start": (b2e + 15) % MIN_PER_DAY, "anchor": "clock"})
            else:
                new.append(dict(it))
        rr["schedule"] = _pack_instances(new)
    slug = f"atyp_t3_split_{block1.replace(':','')}_{block2.replace(':','')}"
    out = profile_from_dict(_stamp(data, source, "split_shift",
                                   {"block1": block1, "block2": block2}, slug))
    out.raw["household"] = out.household
    return out


# ── T4 rotating_shift (implemented; EXCLUDED from reportable banks) ──────────

def rotating_shift(source: Profile, period_weeks: int = 2) -> Profile:
    """T4. Alternate a day-template week and a night-template (T1) week. Since
    a profile encodes ONE week, this returns a two-week variant flagged
    non_reportable; the bank builder must refuse it in reportable banks."""
    night = night_shift_reversion(source)
    data = copy.deepcopy(night.raw)
    data["reportable"] = False
    slug = f"atyp_t4_rotating_{period_weeks}wk"
    out = profile_from_dict(_stamp(data, source, "rotating_shift",
                                   {"period_weeks": period_weeks,
                                    "note": "week B = night_shift_reversion; EXCLUDED from reportable banks"},
                                   slug))
    out.raw["household"] = out.household
    return out


# ── atypicality distance (EMD over per-class activity-time mass) ─────────────

_BIN = 15   # minutes


def _activity_mass(ch: Profile) -> dict[str, list[float]]:
    """Per activity class: minutes of that activity in each 15-min bin over the
    week (7*96 bins), summed across residents. The profile's weekly footprint."""
    nbins = 7 * MIN_PER_DAY // _BIN
    mass: dict[str, list[float]] = {}
    for r in ch.residents:
        for b in r.schedule:
            v = mass.setdefault(b.activity, [0.0] * nbins)
            for (t0, t1, _a) in b.week_intervals():
                for t in range(t0, t1):
                    v[(t // _BIN) % nbins] += 1.0
    return mass


def _emd_1d(a: list[float], b: list[float]) -> float:
    """1-D earth-mover distance between two mass vectors on a cyclic line,
    normalised to total mass. Uses the cumulative-difference integral."""
    sa, sb = sum(a), sum(b)
    if sa == 0 and sb == 0:
        return 0.0
    a = [x / sa for x in a] if sa else [0.0] * len(a)
    b = [x / sb for x in b] if sb else [0.0] * len(b)
    cum, total = 0.0, 0.0
    for x, y in zip(a, b):
        cum += x - y
        total += abs(cum)
    return total / len(a)


def atypicality_distance(base: Profile, transformed: Profile) -> float:
    """Mean over activity classes of the 1-D EMD between the two profiles'
    per-class activity-time mass functions. Timing-only metric (0 == same
    weekly timing). Reported in atypical headers + the bank manifest; E2's harm
    curve plots against THIS, not the transformation family."""
    ma, mb = _activity_mass(base), _activity_mass(transformed)
    classes = set(ma) | set(mb)
    n = len(classes) or 1
    z = [0.0] * (7 * MIN_PER_DAY // _BIN)
    return round(sum(_emd_1d(ma.get(c, z), mb.get(c, z)) for c in classes) / n, 5)


REGISTERED = {
    "night_shift_reversion": night_shift_reversion,
    "workday_pattern": workday_pattern,
    "split_shift": split_shift,
    "rotating_shift": rotating_shift,
    "phase_shift": phase_shift,
    "block_permutation": block_permutation,
    "role_reassignment": role_reassignment,
    "compression": compression,
}


def apply_transform(source: Profile, kind: str, **params) -> Profile:
    if kind not in REGISTERED:
        raise ValueError(f"unregistered transformation {kind!r}; "
                         f"registered: {sorted(REGISTERED)}")
    if kind == "role_reassignment":
        return role_reassignment(source, params["activity"], params["from"], params["to"])
    return REGISTERED[kind](source, **params)
