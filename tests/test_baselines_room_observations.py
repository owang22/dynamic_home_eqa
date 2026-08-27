"""Tests for the room-visit observation model.

A room visit is the shared observation primitive for both halves of the
study, so its schedules must be deterministic and its realization must
never invent evidence the world does not contain.
"""
from __future__ import annotations

import json
import pathlib

import pytest
import yaml

from baselines.room_observations import (PERSON_CHECK_ROOM, RoomMap,
                                         build_schedules, follow_the_person,
                                         morning_evening_sweep, realize,
                                         round_robin_patrol,
                                         stationed_observer)
from baselines.types import DAY_SECONDS

_H = 3600
HH = pathlib.Path("profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh4")
pytestmark = pytest.mark.skipif(
    not (HH / "program.yaml").exists(),
    reason="storyfirst household not present")


@pytest.fixture(scope="module")
def household():
    from baselines.export_bank import _away_intervals, awake_spans, load_truth
    room_map = RoomMap.from_spec(HH / "program.yaml")
    truth, n_days, _ = load_truth(HH / "timeline_seed0")
    awake = awake_spans(HH / "timeline_seed0", n_days)
    away = _away_intervals(HH / "timeline_seed0")
    return room_map, truth, n_days, awake, away


def test_room_map_partitions_receptacles(household):
    room_map, *_ = household
    spec = yaml.safe_load((HH / "program.yaml").read_text())
    declared = [str(r["id"]) for r in spec["receptacles"]]
    mapped = [r for room in room_map.physical_rooms
              for r in room_map.by_room[room]]
    # every receptacle in exactly one physical room, none invented
    assert sorted(mapped) == sorted(declared)
    assert room_map.by_room[PERSON_CHECK_ROOM] == ("ON_PERSON",)
    assert PERSON_CHECK_ROOM not in room_map.physical_rooms


def test_room_map_requires_a_room_field(tmp_path):
    spec = tmp_path / "spec.yaml"
    spec.write_text(yaml.safe_dump({"receptacles": [{"id": "shelf_a"}]}))
    with pytest.raises(ValueError, match="has no 'room'"):
        RoomMap.from_spec(spec)


def test_schedules_are_deterministic_and_seed_sensitive(household):
    room_map, truth, n_days, awake, _ = household
    a = round_robin_patrol(room_map, n_days, awake, 8, seed=0)
    b = round_robin_patrol(room_map, n_days, awake, 8, seed=0)
    c = round_robin_patrol(room_map, n_days, awake, 8, seed=1)
    assert a == b and a != c
    for visits in (a, c):
        assert visits == sorted(visits, key=lambda v: v.t)


def test_round_robin_bounds_the_revisit_gap(household):
    """The point of a round robin: no room is starved. Every room is seen
    at least once per ceil(n_rooms / visits_per_day) days."""
    room_map, truth, n_days, awake, _ = household
    per_day = 8
    visits = round_robin_patrol(room_map, n_days, awake, per_day, seed=0)
    seen = {}
    for v in visits:
        seen.setdefault(v.room, []).append(v.t)
    assert set(seen) == set(room_map.physical_rooms)
    cycle_days = -(-len(room_map.physical_rooms) // per_day)
    for room, times in seen.items():
        gaps = [times[i + 1] - times[i] for i in range(len(times) - 1)]
        assert max(gaps) <= (cycle_days + 1) * DAY_SECONDS, room


def test_sweep_covers_every_room_twice_a_day(household):
    room_map, truth, n_days, awake, _ = household
    visits = morning_evening_sweep(room_map, n_days)
    assert len(visits) == 2 * n_days * len(room_map.physical_rooms)
    day0 = [v for v in visits if v.t < DAY_SECONDS]
    assert {v.room for v in day0} == set(room_map.physical_rooms)


def test_stationed_observer_skews_evidence_toward_its_home(household):
    room_map, truth, n_days, awake, _ = household
    home = room_map.physical_rooms[0]
    visits = stationed_observer(room_map, n_days, awake, home,
                                station_interval_s=2 * _H,
                                excursions_per_day=3, seed=0)
    at_home = sum(1 for v in visits if v.room == home)
    assert at_home > 0.5 * len(visits)
    assert any(v.room != home for v in visits)      # excursions happen


def test_follow_the_person_tracks_one_resident(household):
    """Following must be a function of the followed resident alone —
    with several residents in the house, a schedule that merged all their
    blocks would depend on file order rather than on who is followed."""
    room_map, truth, n_days, awake, _ = household
    residents = sorted({json.loads(line)["resident"]
                        for line in open(HH / "timeline_seed0" /
                                         "residents.jsonl")})
    assert len(residents) > 1, "fixture must have several residents"
    first = follow_the_person(room_map, n_days, awake, HH / "timeline_seed0",
                              4, seed=0, resident=residents[0])
    other = follow_the_person(room_map, n_days, awake, HH / "timeline_seed0",
                              4, seed=0, resident=residents[1])
    assert [v.room for v in first] != [v.room for v in other]


def test_realize_never_invents_evidence(household):
    """Every emitted sighting is true at its instant, and nothing at
    OUT_OF_HOUSE is ever reported."""
    from baselines.export_bank import truth_at
    room_map, truth, n_days, awake, away = household
    visits = build_schedules(room_map, n_days, awake, HH / "timeline_seed0",
                             6, 0)["round_robin_patrol"]
    stream = realize(visits, room_map, truth, "ep0", away)
    assert stream.sightings
    for row in stream.sightings:
        obj, t, rec = (str(row["object_id"]), int(str(row["t"])),
                       str(row["receptacle_id"]))
        assert truth_at(truth[obj], t) == rec
        assert rec != "OUT_OF_HOUSE"


def test_realize_reports_every_object_present_in_the_visited_room(household):
    """The defining property of a room visit: it reveals the WHOLE room,
    so no object present in it at that instant may be missed."""
    from baselines.export_bank import truth_at
    room_map, truth, n_days, awake, away = household
    visits = build_schedules(room_map, n_days, awake, HH / "timeline_seed0",
                             6, 0)["round_robin_patrol"][:40]
    stream = realize(visits, room_map, truth, "ep0", away)
    by_visit = {}
    for row in stream.visit_rows:
        contents = row["contents"]
        assert isinstance(contents, dict)
        by_visit[(int(str(row["t"])), str(row["room"]))] = contents
    for visit in visits:
        if visit.room == PERSON_CHECK_ROOM:
            continue
        contents = by_visit[(visit.t, visit.room)]
        # every inspected receptacle appears, EMPTY ones included — the
        # emptiness is the negative-evidence half of the visit
        assert set(contents) == set(room_map.by_room[visit.room])
        found = {o for objs in contents.values() for o in objs}
        expected = {o for o in truth
                    if truth_at(truth[o], visit.t)
                    in room_map.by_room[visit.room]}
        assert found == expected
        for receptacle, objs in contents.items():
            for o in objs:
                assert truth_at(truth[o], visit.t) == receptacle


def test_room_visit_export_beats_glimpse_on_evidence(tmp_path, household):
    """The whole reason for the change: one visit yields many sightings,
    so a smaller event budget delivers far more evidence per object."""
    from baselines.export_bank import export
    glimpse = export(HH / "timeline_seed0", HH / "program.yaml",
                     tmp_path / "g.jsonl", 0, 10, 30, 3, 24,
                     observation_model="glimpse")
    rooms = export(HH / "timeline_seed0", HH / "program.yaml",
                   tmp_path / "r.jsonl", 0, 10, 30, 3, 24,
                   observation_model="room_visit", visits_per_day=8)
    g = next(glimpse.episodes())
    r = next(rooms.episodes())
    assert len(r.scripted_observations) > 4 * len(g.scripted_observations)
    seen_g = {o.object_id for o in g.scripted_observations}
    seen_r = {o.object_id for o in r.scripted_observations}
    assert len(seen_r) >= len(seen_g)


def test_unknown_patrol_is_refused(tmp_path):
    from baselines.export_bank import export
    with pytest.raises(ValueError, match="unknown patrol"):
        export(HH / "timeline_seed0", HH / "program.yaml",
               tmp_path / "x.jsonl", 0, 10, 30, 3, 24,
               observation_model="room_visit", patrol="no_such_patrol")


# ------------------------------------------------- negative evidence


def _write_visit_bank(path, visits_contents, truth_rows, objects,
                      receptacles, unsensable=("OUT_OF_HOUSE",)):
    """A minimal room-visit bank: tour at t=0 plus explicit visits."""
    import json as _json
    rows = [{"kind": "episode_header", "episode_id": "ep0",
             "household_id": "hh0",
             "receptacle_ids": list(receptacles),
             "object_classes": {o: "widget" for o in objects},
             "budget_per_day": 2, "n_days": 3,
             "unsensable_receptacles": list(unsensable)}]
    rows += truth_rows
    for t, contents in visits_contents:
        rows.append({"kind": "room_visit", "episode_id": "ep0",
                     "t": t, "room": "roomless", "contents": contents})
    with open(path, "w") as f:
        for row in rows:
            f.write(_json.dumps(row) + "\n")
    from baselines.bank import JsonlBank
    return JsonlBank(path=path)


def test_room_visit_emptiness_is_exclusion_evidence(tmp_path):
    """An object last seen at shelf_a silently moves; a later visit finds
    shelf_a empty. A positive-only diet keeps believing shelf_a; the visit
    evidence must rule it out."""
    import random
    from baselines.registry import build_registered_belief
    truth = [
        {"kind": "truth", "episode_id": "ep0", "object_id": "wallet",
         "t": 0, "receptacle_id": "shelf_a"},
        {"kind": "truth", "episode_id": "ep0", "object_id": "wallet",
         "t": 3600, "receptacle_id": "shelf_b"},
        {"kind": "observation", "episode_id": "ep0", "object_id": "wallet",
         "t": 0, "receptacle_id": "shelf_a", "source": "initial_tour"},
    ]
    bank = _write_visit_bank(
        tmp_path / "b.jsonl",
        visits_contents=[(7200, {"shelf_a": []})],
        truth_rows=truth, objects=["wallet"],
        receptacles=["shelf_a", "shelf_b", "shelf_c", "OUT_OF_HOUSE"])
    episode = next(bank.episodes())
    belief = build_registered_belief({"name": "last_observation"},
                                     random.Random(0))
    belief.reset(episode.agent_view())
    for obs in episode.initial_observations:
        belief.update(obs)
    for event in episode.evidence_stream():
        belief.update(event)
    prediction = belief.predict("wallet", 10800)
    assert prediction.distribution.get("shelf_a", 0.0) == 0.0
    assert prediction.argmax != "shelf_a"


def test_room_visits_let_passive_beliefs_infer_out_of_house(tmp_path):
    """The payoff case: visits that cover every sensable receptacle and
    find the object nowhere must concentrate belief on OUT_OF_HOUSE —
    an answer a positive-only passive diet can never reach."""
    import random
    from baselines.registry import build_registered_belief
    truth = [
        {"kind": "truth", "episode_id": "ep0", "object_id": "keys",
         "t": 0, "receptacle_id": "shelf_a"},
        {"kind": "truth", "episode_id": "ep0", "object_id": "keys",
         "t": 3600, "receptacle_id": "OUT_OF_HOUSE"},
        {"kind": "observation", "episode_id": "ep0", "object_id": "keys",
         "t": 0, "receptacle_id": "shelf_a", "source": "initial_tour"},
    ]
    bank = _write_visit_bank(
        tmp_path / "b.jsonl",
        visits_contents=[(7200, {"shelf_a": [], "shelf_b": []}),
                         (7500, {"shelf_c": []})],
        truth_rows=truth, objects=["keys"],
        receptacles=["shelf_a", "shelf_b", "shelf_c", "OUT_OF_HOUSE"])
    episode = next(bank.episodes())
    belief = build_registered_belief({"name": "last_observation"},
                                     random.Random(0))
    belief.reset(episode.agent_view())
    for obs in episode.initial_observations:
        belief.update(obs)
    for event in episode.evidence_stream():
        belief.update(event)
    prediction = belief.predict("keys", 9000)
    assert prediction.argmax == "OUT_OF_HOUSE"


def test_positive_half_still_flows_to_scripted_observations(tmp_path):
    """Recency readouts and the viewer read scripted_observations; a
    room-visit bank must still expose the positive sightings there."""
    truth = [
        {"kind": "truth", "episode_id": "ep0", "object_id": "mug",
         "t": 0, "receptacle_id": "shelf_a"},
        {"kind": "observation", "episode_id": "ep0", "object_id": "mug",
         "t": 0, "receptacle_id": "shelf_a", "source": "initial_tour"},
    ]
    bank = _write_visit_bank(
        tmp_path / "b.jsonl",
        visits_contents=[(3600, {"shelf_a": ["mug"], "shelf_b": []})],
        truth_rows=truth, objects=["mug"],
        receptacles=["shelf_a", "shelf_b", "OUT_OF_HOUSE"])
    episode = next(bank.episodes())
    assert [(o.object_id, o.t, o.receptacle_id)
            for o in episode.scripted_observations] == [("mug", 3600,
                                                         "shelf_a")]
    # and the evidence stream carries BOTH receptacles' results
    from baselines.types import SenseResult
    sense = [e for e in episode.evidence_stream()
             if isinstance(e, SenseResult)]
    assert {(e.receptacle_id, e.contents) for e in sense} == {
        ("shelf_a", ("mug",)), ("shelf_b", ())}
