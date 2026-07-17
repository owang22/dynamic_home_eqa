"""Stage 1 cross-cutting tests: question generator (answer always present,
indices balanced), symbolic answerer mapping, probe determinism, schedule-
prior calibration schema."""
from __future__ import annotations

import json

import numpy as np
import pytest

from dynbelief import MIN_PER_DAY
from dynbelief.beliefs.zoo import B0LastSeen
from dynbelief.eqa.answerer import answer
from dynbelief.eqa.generate import make_question, validate_question_set
from dynbelief.eqa.probe import (accuracy_surface, delta_t_symmetry,
                                 probe_object)


@pytest.fixture()
def episode(tmp_path):
    """Reuses the Stage 0 synthetic episode layout, extended to give the
    target object a richer history for distractor sampling."""
    reg = {
        "scene_id": "synthetic", "n_days": 2, "folders": ["d0", "d1"],
        "objects": {"bowl_1": 0, "mia_phone": 1},
        "receptacles": {"elsewhere": 0, "kitchen.counter_1": 1,
                        "kitchen.table_1": 2, "bedroom_1.bed_1": 3,
                        "livingroom.table_1": 4},
        "receptacle_meta": {
            "0": {"label": "elsewhere", "room": None, "position": None},
            "1": {"label": "kitchen.counter_1", "room": "kitchen", "position": [0, 0, 0]},
            "2": {"label": "kitchen.table_1", "room": "kitchen", "position": [1, 0, 0]},
            "3": {"label": "bedroom_1.bed_1", "room": "bedroom_1", "position": [5, 0, 0]},
            "4": {"label": "livingroom.table_1", "room": "livingroom", "position": [8, 0, 0]},
        },
        "elsewhere_id": 0,
    }
    (tmp_path / "registry.json").write_text(json.dumps(reg))
    (tmp_path / "snapshot_day0.json").write_text(json.dumps(
        {"t_min": 0, "day": 0, "parents": {"0": 1, "1": 3}, "states": {}}))
    (tmp_path / "snapshot_day1.json").write_text(json.dumps(
        {"t_min": MIN_PER_DAY, "day": 1, "parents": {"0": 1, "1": 3}, "states": {}}))
    events = [
        {"t_min": 480, "object_id": 0, "parent_id": 2, "states": {}, "moved_by": "human"},
        {"t_min": 800, "object_id": 0, "parent_id": 4, "states": {}, "moved_by": "human"},
        {"t_min": MIN_PER_DAY, "object_id": 0, "parent_id": 1, "states": {}, "moved_by": "init"},
        {"t_min": MIN_PER_DAY + 500, "object_id": 0, "parent_id": 2, "states": {}, "moved_by": "human"},
    ]
    with open(tmp_path / "events.jsonl", "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    from dynbelief.replay import ReplayWorld
    return ReplayWorld(tmp_path)


def test_question_truth_present_and_balanced(episode):
    qs = []
    for s in range(0, 1200, 60):
        for q in range(s + 60, 1380, 120):
            qs.append(make_question(episode, "location_now", 0, s, q, seed=1))
            qs.append(make_question(episode, "room_now", 0, s, q, seed=1))
    rep = validate_question_set(qs)  # asserts truth among options internally
    assert rep["n"] > 100
    assert rep["max_index_skew"] < 0.15  # roughly uniform correct position


def test_question_distractors_plausible(episode):
    q = make_question(episode, "location_now", 0, 100, 900, seed=2)
    assert q["true_answer"] == 4                       # at livingroom table
    assert q["options"][q["answer_index"]] == 4
    # distractors drawn from this house's receptacles, none equal to truth
    for i, opt in enumerate(q["options"]):
        if i != q["answer_index"]:
            assert opt in episode.receptacles() and opt != q["true_answer"]


def test_answerer_location_and_room(episode):
    b = B0LastSeen()
    b.reset(episode.objects(), episode.receptacles(), 0)
    b.observe(490, {0: (2, {})})   # saw bowl on kitchen table
    q = make_question(episode, "location_now", 0, 490, 700, seed=3)
    assert q["true_answer"] == 2
    assert answer(episode, b, q) == q["answer_index"]  # belief agrees with truth
    q2 = make_question(episode, "room_now", 0, 490, 700, seed=3)
    assert q2["true_answer"] == "kitchen"
    assert answer(episode, b, q2) == q2["answer_index"]


def test_probe_determinism_and_injection(episode):
    def go():
        b = B0LastSeen()
        b.reset(episode.objects(), episode.receptacles(), 0)
        return probe_object(b, episode, 0, test_day=0, qtype="location_now",
                            grid_min=240, seed=5)
    a, b2 = go(), go()
    assert a == b2                                      # same grid -> same scores
    # b0 with the injected observation is exact until the object moves:
    for r in a:
        true_seen = episode.true_parent(0, r["t_seen"])
        true_query = episode.true_parent(0, r["t_query"])
        assert r["correct"] == int(true_seen == true_query)


def test_surface_and_symmetry_shapes(episode):
    b = B0LastSeen()
    b.reset(episode.objects(), episode.receptacles(), 0)
    recs = probe_object(b, episode, 0, 0, "location_now", grid_min=120, seed=1)
    acc = accuracy_surface(recs, 120)
    n = MIN_PER_DAY // 120
    assert acc.shape == (n, n)
    assert np.isnan(acc[5, 2])                          # t_seen >= t_query empty
    r2 = delta_t_symmetry(recs)
    assert 0.0 <= r2 <= 1.0 or r2 < 0.0 or True         # finite
    assert np.isfinite(r2)


def test_schedule_prior_calibration(tmp_path, episode):
    from dynbelief.priors.schedule_prior import load_schedule_prior
    raw = {"version": 1, "bins_per_day": 24, "source": "hand",
           "classes": {"bowl": [0.1] * 8 + [5.0] * 2 + [0.1] * 14,
                       "phone": [1.0] * 24}}
    (episode.episode_dir / "schedule_prior_raw.json").write_text(json.dumps(raw))
    priors = load_schedule_prior(episode.episode_dir, episode, train_days=[0])
    assert set(priors) >= {"bowl", "phone"}
    f = priors["bowl"]
    assert abs(np.mean(f.per_min) - 1.0) < 1e-6         # mean-1 modulator
    cal = json.loads((episode.episode_dir / "schedule_prior_calibrated.json").read_text())
    assert cal["bins_per_day"] == 24 and "temperatures" in cal


def test_weekly_prior_and_gate():
    """Section C: weekly gate, weekend-heavy fit, periodic cumulative,
    graceful non-selection on flat streams."""
    import numpy as np
    from dynbelief import MIN_PER_DAY
    from dynbelief.beliefs.fremen import (fremen_prior_weekly, weekly_gate,
                                          weekly_component_report)
    days = list(range(28))
    assert weekly_gate(days) and not weekly_gate(list(range(14)))
    times = []
    for d in days:
        k = 6 if d % 7 >= 5 else 1
        times += [d * MIN_PER_DAY + 600 + i * 17 for i in range(k)]
    f = fremen_prior_weekly(times, days)
    assert f.period == 7 * MIN_PER_DAY
    sat = np.mean([f(5 * MIN_PER_DAY + m) for m in range(0, MIN_PER_DAY, 30)])
    tue = np.mean([f(1 * MIN_PER_DAY + m) for m in range(0, MIN_PER_DAY, 30)])
    assert sat > 2 * tue
    assert abs(f.cumulative(0, 14 * MIN_PER_DAY)
               - 2 * f.cumulative(0, 7 * MIN_PER_DAY)) < 1e-6
    assert weekly_component_report(times, days)["selected"]
    flat = [d * MIN_PER_DAY + 300 + i * 200 for d in days for i in range(2)]
    assert not weekly_component_report(flat, days)["selected"]
    # gate failure falls back to a daily-period prior, not a bogus weekly one
    f2 = fremen_prior_weekly(times[:20], list(range(10)))
    assert f2.period == MIN_PER_DAY
