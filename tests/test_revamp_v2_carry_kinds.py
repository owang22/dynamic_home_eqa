"""Part-B tests: event `kind` tagging, carry-rehome suppression, and the
downstream-consumers-run-unchanged contract for the additive field."""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys

import yaml

from revamp_v2_helpers import REPO, mini_program

import simulate as sim


def _carry_program():
    """mini_program reshaped so the departure-carry mechanism fires daily:
    mug_1 rides resident_1 (person-homed), a morning walk takes it OUT,
    a short snack at home sets it down (after-rule -> during putdown
    normalization), and errands 45 min later take it out again — the
    putdown/pickup pair the rehome window is for."""
    program = mini_program()
    program["weekly_blocks"] = [
        {"resident": "resident_1", "activity": "walk",
         "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
         "start": "09:00", "end": "09:30", "at": "ELSEWHERE",
         "jitter": "external", "skip_p": 0.0, "sleep": False, "cites": "c"},
        {"resident": "resident_1", "activity": "snack",
         "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
         "start": "09:30", "end": "10:15", "at": "table_a",
         "jitter": "external", "skip_p": 0.0, "sleep": False, "cites": "c"},
        {"resident": "resident_1", "activity": "errands",
         "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
         "start": "10:15", "end": "12:00", "at": "ELSEWHERE",
         "jitter": "external", "skip_p": 0.0, "sleep": False, "cites": "c"},
        {"resident": "resident_1", "activity": "reading",
         "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
         "start": "20:00", "end": "21:30", "at": "table_a",
         "jitter": "external", "skip_p": 0.0, "sleep": False, "cites": "c"},
    ]
    program["object_rules"] = [
        {"object": "mug_1", "home": "person:resident_1", "cites": "c",
         "rules": [
             # after-rule on a HOME activity for a person-homed object:
             # the expander normalizes it to a during putdown.
             {"activity": "snack", "phase": "after", "dest": "table_a",
              "cites": "c"}]},
        # a plain rule-driven object, so `rule` events exist alongside the
        # suppressible carry pairs
        {"object": "book_1", "home": "shelf_b", "cites": "c",
         "rules": [
             {"activity": "reading", "phase": "during", "dest": "table_a",
              "only_from": ["shelf_b"], "cites": "c"},
             {"activity": "reading", "phase": "after", "dest": "shelf_b",
              "only_from": ["table_a"], "cites": "c"}]},
    ]
    program["activities"] = [{"name": "snack", "cites": "c"}]
    program["arc_events"] = []
    return program


def _params(rehome_min):
    params = copy.deepcopy(sim.load_params())
    params["carry_on_departure"] = {"enabled": True, "carry_p": 1.0,
                                    "carry_rehome_min": rehome_min}
    return params


def _run(rehome_min, days=7, seed=0):
    params = _params(rehome_min)
    log, hourly, blocks, stats, acts, motions = sim.simulate_program(
        _carry_program(), days, seed, params=params)
    sim.tag_event_kinds(log)
    n = sim.suppress_carry_rehome(log, hourly, rehome_min)
    return log, hourly, n, motions


def _replay_matches_hourly(log, hourly, motions):
    """events.jsonl and hourly.csv must tell ONE story: replaying the
    events from the starting homes reproduces every hourly snapshot."""
    pos = {o: p["home"] for o, p in motions["placements"].items()}
    i = 0
    log = sorted(log, key=lambda e: e["t"])
    for row in hourly:
        while i < len(log) and log[i]["t"] < row["t"]:
            pos[log[i]["object"]] = log[i]["to"]
            i += 1
        for o in pos:
            assert row[o] == pos[o], \
                f"hourly/{o} at t={row['t']}: {row[o]} != replay {pos[o]}"


def test_every_event_carries_a_kind():
    log, _, _, _ = _run(rehome_min=0)
    kinds = {e["kind"] for e in log}
    assert all("kind" in e for e in log)
    assert kinds <= {"carry_pickup", "carry_putdown", "rule", "misplace",
                     "tidy"}
    assert "carry_pickup" in kinds and "carry_putdown" in kinds


def test_kind_tagging_classifies_by_mechanism():
    log, _, _, _ = _run(rehome_min=0)
    for e in log:
        if e["kind"] == "carry_pickup":
            assert e["to"] == "person:resident_1"
        if e["kind"] == "carry_putdown":
            assert e["from"] == "person:resident_1"


def test_rehome_window_removes_close_putdown_pickup_pairs():
    log0, hourly0, n0, _ = _run(rehome_min=0)
    log90, hourly90, n90, motions = _run(rehome_min=90)
    assert n0 == 0
    assert n90 > 0
    assert len(log90) == len(log0) - 2 * n90
    # what remains is exactly the non-suppressed events, in order
    _replay_matches_hourly(log90, hourly90, motions)


def test_rehome_zero_is_the_old_behaviour():
    log0, hourly0, _, motions = _run(rehome_min=0)
    _replay_matches_hourly(log0, hourly0, motions)


def test_suppression_only_pairs_the_same_person_and_spot():
    # synthetic: putdown then pickup by a DIFFERENT person is never a
    # kept-bag pair, however close in time.
    log = [
        {"t": 600, "object": "mug_1", "from": "person:r1", "to": "table_a",
         "kind": "carry_putdown"},
        {"t": 630, "object": "mug_1", "from": "table_a", "to": "person:r2",
         "kind": "carry_pickup"},
    ]
    assert sim.suppress_carry_rehome(log, [], 90) == 0
    assert len(log) == 2


def test_suppression_respects_day_boundary_and_window():
    def pair(t1, t2):
        return [
            {"t": t1, "object": "m", "from": "person:r1", "to": "x",
             "kind": "carry_putdown"},
            {"t": t2, "object": "m", "from": "x", "to": "person:r1",
             "kind": "carry_pickup"},
        ]
    log = pair(1400, 1450)          # crosses midnight: kept
    assert sim.suppress_carry_rehome(log, [], 90) == 0
    log = pair(600, 700)            # 100 min >= 90: kept
    assert sim.suppress_carry_rehome(log, [], 90) == 0
    log = pair(600, 650)            # 50 min, same day: suppressed
    assert sim.suppress_carry_rehome(log, [], 90) == 1
    assert log == []


def test_suppression_patches_hourly_snapshots():
    log = [
        {"t": 590, "object": "m", "from": "person:r1", "to": "x",
         "kind": "carry_putdown"},
        {"t": 650, "object": "m", "from": "x", "to": "person:r1",
         "kind": "carry_pickup"},
    ]
    hourly = [{"t": 540, "m": "person:r1"}, {"t": 600, "m": "x"},
              {"t": 660, "m": "person:r1"}]
    assert sim.suppress_carry_rehome(log, hourly, 90) == 1
    assert [r["m"] for r in hourly] == ["person:r1"] * 3


def test_export_bank_consumes_kind_tagged_timeline(tmp_path):
    """`kind` is additive: the unchanged downstream chain must run. The
    heaviest consumer (export_bank) is executed for real on a tagged
    timeline; spatialize/the viewer read events with the same
    json.loads-per-line pattern."""
    from revamp_v2_helpers import PERSONA
    hh = tmp_path / "hh_test"
    hh.mkdir()
    program = _carry_program()
    (hh / "routine_program.yaml").write_text(
        yaml.safe_dump(program, sort_keys=False))
    (hh / "persona.yaml").write_text(yaml.safe_dump(PERSONA,
                                                    sort_keys=False))
    out = hh / "timeline_seed0"
    sim.write_timeline(hh, out, 7, 0)
    events = [json.loads(line) for line in
              (out / "events.jsonl").read_text().splitlines()]
    assert events and all("kind" in e for e in events)
    meta = json.loads((out / "meta.json").read_text())
    assert meta["activity_stats"]["carry_rehome_suppressed"] > 0
    env = dict(os.environ,
               PYTHONPATH=str(REPO / "src") + os.pathsep
               + os.environ.get("PYTHONPATH", ""))
    r = subprocess.run(
        [sys.executable, "-m", "baselines.export_bank",
         "--timeline", str(out), "--spec",
         str(hh / "routine_program.yaml"),
         "--seed", "0", "--out", str(tmp_path / "bank.jsonl")],
        capture_output=True, text=True, env=env, cwd=REPO)
    assert r.returncode == 0, r.stderr[-2000:]
    assert (tmp_path / "bank.jsonl").exists()
