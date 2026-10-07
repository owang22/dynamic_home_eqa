"""Part-C tests: the broadened reachability check (at-home coverage) and
the panel's dead_days / non-carry columns."""
from __future__ import annotations

import json

from revamp_v2_helpers import mini_program

import realism_panel
import validate as v2v


def test_covered_program_passes():
    assert v2v.check_reachability(mini_program()) == []


def _unbound_block(activity: str, day: str = "Mo") -> dict:
    return {"resident": "resident_1", "activity": activity,
            "days": [day], "start": "19:00", "end": "20:00",
            "at": "table_a", "jitter": "flexible", "skip_p": 0.0,
            "sleep": False, "cites": "evenings"}


def test_one_uncovered_at_home_activity_is_tolerated_but_reported():
    """The gate filters the degenerate habit, not a single considered
    miss: an at-home activity that genuinely moves no tracked object is
    legitimate content (measured on the hosted set — gpt-5.6-terra leaves
    exactly one at reasoning=medium). It is REPORTED, never silent."""
    program = mini_program()
    program["weekly_blocks"].append(_unbound_block("watch_tv"))
    assert v2v.uncovered_at_home(program) == ["watch_tv"]
    assert not [p for p in v2v.check_reachability(program) if "at-home" in p]


def test_too_many_uncovered_at_home_activities_fail_named():
    """Past the tolerance the program is rejected, and the message names
    the offenders — the near-static home this gate exists to catch."""
    program = mini_program()
    extra = ["watch_tv", "reading", "gaming", "hobby", "study", "music"]
    for i, act in enumerate(extra):
        program["weekly_blocks"].append(
            _unbound_block(act, day=["Mo", "Tu", "We", "Th", "Fr", "Sa"][i]))
    problems = [p for p in v2v.check_reachability(program) if "at-home" in p]
    assert problems, "a near-static home must reject"
    assert any("watch_tv" in p for p in problems)
    assert set(extra) <= set(v2v.uncovered_at_home(program))


def test_elsewhere_blocks_are_exempt():
    program = mini_program()
    program["weekly_blocks"].append(
        {"resident": "resident_1", "activity": "gym",
         "days": ["Mo"], "start": "18:00", "end": "19:00",
         "at": "ELSEWHERE", "jitter": "external", "skip_p": 0.0,
         "sleep": False, "cites": "fitness"})
    assert v2v.check_reachability(program) == []


def test_sleep_blocks_are_exempt_by_flag_and_by_name():
    program = mini_program()
    program["weekly_blocks"].append(
        {"resident": "resident_1", "activity": "nap",
         "days": ["Sa"], "start": "14:00", "end": "15:00",
         "at": "bed_b1", "jitter": "loose", "skip_p": 0.3,
         "sleep": True, "cites": "weekend dozes"})
    program["weekly_blocks"].append(
        {"resident": "resident_1", "activity": "lie_down",
         "days": ["Su"], "start": "14:00", "end": "15:00",
         "at": "bed_b1", "jitter": "loose", "skip_p": 0.3,
         "sleep": True, "cites": "weekend dozes"})
    assert v2v.check_reachability(program) == []


def test_reset_all_counts_as_a_binding():
    # the hh1 fixture's own pattern: a tidying block moves objects via
    # reset_all, no per-object rule needed
    program = mini_program()
    program["weekly_blocks"].append(
        {"resident": "resident_1", "activity": "tidy_up",
         "days": ["Sa"], "start": "10:00", "end": "10:30",
         "at": "table_a", "jitter": "flexible", "skip_p": 0.2,
         "sleep": False, "cites": "weekend reset"})
    program["activities"].append(
        {"name": "tidy_up", "cites": "weekend reset",
         "reset_all": {"p": 0.8, "objects": ["mug_1"]}})
    assert v2v.check_reachability(program) == []


def test_arc_add_blocks_are_not_checked():
    program = mini_program()
    program["arc_events"].append(
        {"day": 2, "note": "one-off",
         "patch": {"add": [
             {"resident": "resident_1", "activity": "hobby",
              "start": "15:00", "at": "table_a", "jitter": "loose"}]}})
    assert v2v.check_reachability(program) == []


# ---------------------------------------------------------------- panel --

def _timeline(tmp_path, events, residents, days=2, meta_extra=None):
    tl = tmp_path / "timeline"
    tl.mkdir()
    objects = sorted({e["object"] for e in events}) or ["mug_1"]
    with open(tl / "events.jsonl", "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    with open(tl / "hourly.csv", "w") as f:
        f.write(",".join(["t", "stamp"] + objects) + "\n")
        for h in range(days * 24):
            f.write(",".join([str(h * 60), f"d{h//24:02d}"]
                             + ["x"] * len(objects)) + "\n")
    with open(tl / "residents.jsonl", "w") as f:
        for r in residents:
            f.write(json.dumps(r) + "\n")
    meta = {"household": "hh_t", "days": days}
    meta.update(meta_extra or {})
    (tl / "meta.json").write_text(json.dumps(meta))
    return tl


def test_panel_stats_run_on_non_carry_basis(tmp_path):
    events = (
        [{"t": 60 * i, "object": "mug_1", "from": "a", "to": "b",
          "kind": "rule"} for i in range(4)]
        + [{"t": 100 + 60 * i, "object": "phone_1", "from": "a",
            "to": "person:r1", "kind": "carry_pickup"} for i in range(12)])
    tl = _timeline(tmp_path, events, [])
    s = realism_panel.timeline_stats(tl)
    assert s["n_events"] == 4                       # non-carry only
    assert s["carry_frac"] == 0.75
    assert s["fano_all"] != s["daily_fano"]
    assert s["top2"] == 1.0                          # one object owns all


def test_dead_days_counts_home_awake_days_with_no_events(tmp_path):
    residents = [
        # day 0: home awake 8h, day 1: same — but only day 0 has events
        {"resident": "r1", "activity": "relax", "t0": 480, "t1": 960,
         "at": "table_a"},
        {"resident": "r1", "activity": "relax", "t0": 1920, "t1": 2400,
         "at": "table_a"},
    ]
    events = [{"t": 500 + i, "object": "mug_1", "from": "a", "to": "b",
               "kind": "rule"} for i in range(3)]
    tl = _timeline(tmp_path, events, residents)
    s = realism_panel.timeline_stats(tl)
    assert s["dead_days"] == 1


def test_days_away_or_asleep_are_never_dead(tmp_path):
    residents = [
        {"resident": "r1", "activity": "travel_away", "t0": 0, "t1": 1440,
         "at": "ELSEWHERE"},
        {"resident": "r1", "activity": "night_sleep", "t0": 1440,
         "t1": 2880, "at": "bed_b1"},
    ]
    tl = _timeline(tmp_path, [], residents)
    s = realism_panel.timeline_stats(tl)
    assert s["dead_days"] == 0


def test_not_story_driven_marked_in_render(tmp_path):
    tl = _timeline(tmp_path, [{"t": 10, "object": "mug_1", "from": "a",
                               "to": "b", "kind": "rule"}], [],
                   meta_extra={"n_fallback_days": 1,
                               "not_story_driven": True})
    row = realism_panel.timeline_stats(tl)
    assert row["fallback_days"] == 1 and row["not_story_driven"]
    text = realism_panel.render([row], None)
    assert "NOT story-driven" in text
    assert "fallback_days" in text
