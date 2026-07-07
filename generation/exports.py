"""
Replay-viewer export format and per-category calibration stats.

build_manifest() (manifest.py) produces the canonical Change-log format
consumed by qa/questions.py, env/replay.py, and agents/harness.py. This
module produces a second, compact view of the same day — the format a
timeline/replay viewer wants: occupant activity windows as plain tuples and
changes as arrays instead of dicts — plus a per-category summary of how much
an object category actually moved, which is the input the future hazard-rate
calibration work consumes.

category_location_change_stats() operates on manifest.json's `changes`,
which by construction (see manifest.py's no-op suppression) only ever
contains genuine location changes — no separate accounting is needed here to
keep no-ops from inflating a "how often does this category move" statistic.
"""
from __future__ import annotations


def to_replay_format(
    scene_id: str,
    household_type: str,
    day: int,
    generation_result: dict,
    manifest: dict,
) -> dict:
    """Compact replay-viewer JSON: {meta, occupants, changes, category_stats}.

    occupants: one entry per persona occupant, activities as
      [activity, room, start, end] tuples (room, not the manifest's semantic
      slot vocabulary — this is the same location string the activity-trace
      stage generated, i.e. one of rooms.CANONICAL_ROOMS or "away").
    changes: [t, label, change_type, from_semantic, to_semantic, reason, mover]
      tuples, sorted by t — the same events build_manifest() already
      resolved and filtered, just flattened for a smaller/faster-to-parse
      payload than the dict-per-event form.
    """
    persona = generation_result.get("persona", {})
    traces  = generation_result.get("traces", [])
    trace_by_name = {t.get("occupant_name"): t for t in traces}

    occupants = []
    for occ in persona.get("occupants", []):
        name  = occ["name"]
        trace = trace_by_name.get(name, {})
        occupants.append({
            "name": name,
            "age_band": occ.get("age_band"),
            "activities": [
                [a["activity"], a["location"], a["start"], a["end"]]
                for a in trace.get("activities", [])
            ],
        })

    changes = [
        [c["t"], c["label"], c["change_type"], c["from_semantic"], c["to_semantic"],
         c["reason"], c.get("mover")]
        for c in sorted(manifest.get("changes", []), key=lambda c: c["t"])
    ]

    return {
        "meta": {
            "scene_id":         scene_id,
            "resident_profile": household_type,
            "household_id":     generation_result.get("household_id"),
            "day":              day,
            "seed":             manifest.get("seed"),
        },
        "occupants":      occupants,
        "changes":        changes,
        "category_stats": category_location_change_stats(manifest.get("changes", [])),
    }


def category_location_change_stats(changes: list[dict]) -> dict[str, dict]:
    """Per-category summary: {location_changes, distinct_slots_visited,
    mean_dwell_hours}, computed from real location-change events (`changes`
    already excludes no-ops and rejected proposals — see manifest.py).

    mean_dwell_hours is the mean time a label spends in one slot before its
    next move (gap between one event's t and the same label's next event's
    t) — None if a category's labels never moved more than once, since a
    dwell time needs two consecutive events to measure.
    """
    by_label: dict[str, list[dict]] = {}
    for c in changes:
        by_label.setdefault(c["label"], []).append(c)

    by_category: dict[str, dict] = {}
    for label, events in by_label.items():
        events = sorted(events, key=lambda c: c["t"])
        cat = events[0]["object_category"]
        agg = by_category.setdefault(cat, {"count": 0, "slots": set(), "dwell_times": []})
        agg["count"] += len(events)
        for i, e in enumerate(events):
            agg["slots"].add(e["to_semantic"])
            if i + 1 < len(events):
                agg["dwell_times"].append(events[i + 1]["t"] - e["t"])

    stats: dict[str, dict] = {}
    for cat, agg in by_category.items():
        dwell = agg["dwell_times"]
        stats[cat] = {
            "location_changes":      agg["count"],
            "distinct_slots_visited": len(agg["slots"]),
            "mean_dwell_hours":      round(sum(dwell) / len(dwell), 3) if dwell else None,
        }
    return stats


def category_state_flip_stats(changes: list[dict]) -> dict[str, dict]:
    """Per-(category, state_variable) summary: {flip_count, mean_dwell_hours}
    — the state-axis counterpart of category_location_change_stats, same
    shape (flip_count in place of location_changes, mean_dwell_hours meaning
    "mean time between flips" rather than "mean time between moves"),
    computed from change_type == "state_change" events only.

    Keyed by "{category}::{state_variable}" (e.g. "tv::power") — the same
    synthetic key embodied/posterior.py's belief store and
    embodied/question.py's state questions use, so a decay/kernel model fit
    from this dict slots into that machinery without translation.
    """
    by_label_variable: dict[tuple[str, str], list[dict]] = {}
    for c in changes:
        if c.get("change_type") != "state_change":
            continue
        by_label_variable.setdefault((c["label"], c["state_variable"]), []).append(c)

    by_key: dict[str, dict] = {}
    for (_label, variable), events in by_label_variable.items():
        events = sorted(events, key=lambda c: c["t"])
        cat = events[0]["object_category"]
        key = f"{cat}::{variable}"
        agg = by_key.setdefault(key, {"count": 0, "dwell_times": []})
        agg["count"] += len(events)
        for i in range(len(events) - 1):
            agg["dwell_times"].append(events[i + 1]["t"] - events[i]["t"])

    stats: dict[str, dict] = {}
    for key, agg in by_key.items():
        dwell = agg["dwell_times"]
        stats[key] = {
            "flip_count":       agg["count"],
            "mean_dwell_hours": round(sum(dwell) / len(dwell), 3) if dwell else None,
        }
    return stats
