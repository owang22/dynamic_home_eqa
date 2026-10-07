"""The installation tour need not be Monday 00:00 with every object at
its home: ``tour_start=random`` draws a per-seed awake instant, exports the
snapshot at that instant, and withholds everything before it."""

from __future__ import annotations

import json
import pathlib
import random

import pytest

from baselines.export_bank import (DAY_SECONDS, OUT_OF_HOUSE,
                                   draw_tour_instant, export, stamp)


def _fixture(tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    """Four days; obj_a rests at rec_1 but sits on rec_2 09:00-11:00 daily;
    obj_p is carried and out of the house 10:00-19:00 daily."""
    timeline = tmp_path / "timeline"
    timeline.mkdir(exist_ok=True)
    (timeline / "hourly.csv").write_text(
        "t,stamp,obj_a,obj_p\n" + "\n".join(
            f"{h * 60},d{h // 24:02d} Mon {h % 24:02d}:00,rec_1,person:r1"
            for h in range(4 * 24)) + "\n")
    events = []
    for d in range(4):
        events.append({"t": d * 1440 + 540, "object": "obj_a",
                       "from": "rec_1", "to": "rec_2", "by": "activity:x"})
        events.append({"t": d * 1440 + 660, "object": "obj_a",
                       "from": "rec_2", "to": "rec_1", "by": "tidy:x"})
    (timeline / "events.jsonl").write_text(
        "\n".join(json.dumps(e) for e in events) + "\n")
    (timeline / "residents.jsonl").write_text("\n".join(
        json.dumps({"resident": "r1", "activity": "shift",
                    "t0": d * 1440 + 600, "t1": d * 1440 + 1140,
                    "at": "ELSEWHERE"}) for d in range(4)) + "\n")
    spec = tmp_path / "spec.yaml"
    spec.write_text(
        "household: hh_test\n"
        "source_profile: profile.yaml\n"
        "receptacles:\n  - {id: rec_1, room: a}\n  - {id: rec_2, room: b}\n")
    (tmp_path / "profile.yaml").write_text(
        "object_inventory:\n"
        "  - {id: obj_a, class: mug}\n  - {id: obj_p, class: phone}\n")
    return timeline, spec


def _export(tmp_path: pathlib.Path, seed: int, **kw):
    timeline, spec = _fixture(tmp_path)
    return export(timeline, spec, tmp_path / f"bank{seed}.jsonl", seed=seed,
                  sightings_per_day=12, questions_per_day=10,
                  first_question_day=0, budget_per_day=2,
                  query_mode="uniform", **kw)


def test_day0_is_the_original_convention() -> None:
    awake = {d: [(d * DAY_SECONDS + 8 * 3600, d * DAY_SECONDS + 22 * 3600)]
             for d in range(4)}
    assert draw_tour_instant("day0", 3, 4, awake, random.Random(0)) == 0
    with pytest.raises(ValueError):
        draw_tour_instant("random", 4, 4, awake, random.Random(0))
    with pytest.raises(ValueError):
        draw_tour_instant("noon", 0, 4, awake, random.Random(0))


def test_random_draw_lands_in_awake_time_of_an_allowed_day() -> None:
    awake = {d: [(d * DAY_SECONDS + 8 * 3600, d * DAY_SECONDS + 22 * 3600)]
             for d in range(4)}
    seen_days = set()
    for seed in range(40):
        t = draw_tour_instant("random", 1, 4, awake, random.Random(seed))
        day, rem = divmod(t, DAY_SECONDS)
        assert day in (0, 1) and 8 * 3600 <= rem < 22 * 3600
        seen_days.add(day)
    assert seen_days == {0, 1}  # both days are actually drawn
    assert stamp(DAY_SECONDS + 14 * 3600 + 20 * 60) == "d01 Tue 14:20"


def test_random_tour_is_a_snapshot_and_withholds_earlier_evidence(
        tmp_path: pathlib.Path) -> None:
    tours = {}
    for seed in range(6):
        episode = next(_export(tmp_path, seed, tour_start="random",
                               tour_max_day=1).episodes())
        t = episode.tour_t
        tours[seed] = t
        assert t > 0 and all(o.t == t for o in episode.initial_observations)
        # The snapshot is the truth AT the tour instant, not the home.
        seen = {o.object_id: o.receptacle_id
                for o in episode.initial_observations}
        for obj, where in seen.items():
            assert where == episode.true_location(obj, t) != OUT_OF_HOUSE
        # Anything the robot could not see is simply absent from the tour.
        if episode.true_location("obj_p", t) == OUT_OF_HOUSE:
            assert "obj_p" not in seen
        # Nothing from before the installation leaks out.
        assert all(o.t >= t for o in episode.scripted_observations)
        assert all(q.t_query >= t for day in episode.questions_by_day
                   for q in day)
    # Per-seed: the install moment varies across seeds.
    assert len(set(tours.values())) > 1


def test_day0_export_unchanged(tmp_path: pathlib.Path) -> None:
    episode = next(_export(tmp_path, 0, tour_start="day0").episodes())
    assert episode.tour_t == 0
    assert {o.object_id for o in episode.initial_observations} == {"obj_a",
                                                                   "obj_p"}
    assert sum(len(d) for d in episode.questions_by_day) == 40
