"""The re-asking layer of LLMHypothesisMixture, driven by a fake
elicitor: scheduled asks, the prediction-quality trigger (and that
weight collapse alone does NOT trigger), the call cap, and a rebuild
that keeps weights for kept ids and replays history into revised
particles. Times are seconds since episode start; day 0 is Monday."""

from __future__ import annotations

import json
import random

import pytest

from baselines.beliefs.llm_hypothesis_mixture import (LLMHypothesisMixture,
                                                      ReaskConfig)
from baselines.types import DAY_SECONDS, EpisodeContext, Observation

H = 3600
RECS = ("desk", "kitchen_table", "shelf", "hamper", "OUT_OF_HOUSE")
OBJECTS = {"laptop_1": "laptop", "mug_1": "mug", "towel_1": "towel"}


def _ctx() -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep", household_id="hh_test", receptacle_ids=RECS,
        object_classes=OBJECTS, budget_per_day=2, n_days=28,
        unsensable_receptacle_ids=("OUT_OF_HOUSE",))


def _obs(obj, rec, day, hour):
    return Observation(object_id=obj, object_class=OBJECTS[obj],
                       receptacle_id=rec, t=int(day * DAY_SECONDS + hour * H),
                       source="scripted")


H_DESK = {"hypothesis_id": "h1", "rationale": "laptop lives on the desk",
          "distinguishing_prediction": "laptop_1 on desk at 13:00 weekdays",
          "distinguishing_check": {"target": "laptop_1", "at": "desk",
                                   "days": "weekday", "hour": 13.0},
          "rest": {"laptop_1": "desk"}, "activities": []}
H_TABLE = {"hypothesis_id": "h2", "rationale": "laptop lives on the table",
           "rest": {"laptop_1": "kitchen_table"}, "activities": []}


def _mixture(tmp_path, hyps, reask, elicitor):
    d = tmp_path / "hyps"; d.mkdir(exist_ok=True)
    (d / "hh_test.json").write_text(json.dumps({"hypotheses": hyps}))
    m = LLMHypothesisMixture(random.Random(0), d, reask=reask,
                             elicitor=elicitor)
    m.reset(_ctx())
    return m


class _Recorder:
    """Fake elicitor: records reports, returns a fixed revision."""

    def __init__(self, revision=None):
        self.calls = []; self.revision = revision

    def __call__(self, report, previous, context):
        self.calls.append((report, previous))
        return self.revision if self.revision is not None else previous


def test_scheduled_asks_fire_once_each_and_respect_cap(tmp_path):
    rec = _Recorder()
    m = _mixture(tmp_path, [H_DESK, H_TABLE],
                 ReaskConfig(window=1000, scheduled_days=(3, 7), max_calls=1),
                 rec)
    for day in range(10):
        m.update(_obs("laptop_1", "desk", day, 9))
    assert [e["reason"] for e in m.reask_events] == ["scheduled day 3"]
    assert m.calls_made == 1 and len(rec.calls) == 1


def test_quality_trigger_fires_when_mixture_is_surprised(tmp_path):
    rec = _Recorder()
    m = _mixture(tmp_path, [H_DESK, H_TABLE],
                 ReaskConfig(window=6, threshold=-1.5, scheduled_days=(),
                             max_calls=3, min_gap=6), rec)
    # The laptop cycles through a different receptacle every sighting:
    # neither hypothesis nor the statistical particle can predict it, so
    # the WHOLE mixture's likelihood stays poor.
    cycle = ("shelf", "hamper", "kitchen_table", "desk")
    for i in range(16):
        m.update(_obs("laptop_1", cycle[i % 4], i // 4, 8 + (i % 4) * 3))
    assert any(e["reason"].startswith("quality") for e in m.reask_events)


def test_weight_collapse_alone_does_not_trigger(tmp_path):
    rec = _Recorder()
    m = _mixture(tmp_path, [H_DESK, H_TABLE],
                 ReaskConfig(window=6, threshold=-1.5, scheduled_days=(),
                             max_calls=3), rec)
    # Sightings agree with h1 every time: weights collapse onto h1, the
    # mixture predicts well, and nothing should fire.
    for i in range(20):
        m.update(_obs("laptop_1", "desk", i // 4, 8 + (i % 4) * 3))
    assert m.weights[0] > 0.8
    assert m.reask_events == []


def test_rebuild_keeps_weight_for_kept_id_and_replays_history(tmp_path):
    revised = [dict(H_DESK), {"hypothesis_id": "h3", "rationale": "shelf",
                              "rest": {"laptop_1": "shelf"}, "activities": []}]
    rec = _Recorder(revision=revised)
    m = _mixture(tmp_path, [H_DESK, H_TABLE],
                 ReaskConfig(window=1000, scheduled_days=(2,), max_calls=1),
                 rec)
    for day in range(2):
        for hour in (8, 12, 18):
            m.update(_obs("laptop_1", "desk", day, hour))
    w_before = dict(zip([p.name for p in m.particles], m.weights))
    m.update(_obs("laptop_1", "desk", 2, 8))          # fires the ask
    names = [p.name for p in m.particles]
    assert names[:2] == ["HypothesisProgram(h1)", "HypothesisProgram(h3)"]
    assert names[-1].startswith("PeriodicPersistence")
    w_after = dict(zip(names, m.weights))
    # h1 kept its lead; the newcomer did not inherit it.
    assert w_after["HypothesisProgram(h1)"] > w_after["HypothesisProgram(h3)"]
    # The rebuilt h3 has the history replayed: it knows 7 desk sightings.
    assert len(m.particles[1]._history["laptop_1"]) == 7
    assert m.reask_events[-1]["changed"] is True


def test_revision_report_contents(tmp_path):
    rec = _Recorder()
    m = _mixture(tmp_path, [H_DESK, H_TABLE],
                 ReaskConfig(window=1000, scheduled_days=(), max_calls=0), rec)
    cycle = ("shelf", "hamper", "kitchen_table")
    for day in range(3):
        m.update(_obs("laptop_1", cycle[day], day, 13))   # weekday 13:00
        m.update(_obs("mug_1", "kitchen_table", day, 8))  # no hypothesis covers mug
    report = m.revision_report(int(3 * DAY_SECONDS))
    ids = {h["hypothesis_id"]: h for h in report["hypotheses"]}
    assert ids["h1"]["verdict"] == "came true 0/3 times"
    assert ids["h2"]["verdict"] is None
    assert any(w["object"] == "laptop_1" and w["predicted"] != w["actual"]
               for w in report["worst_objects"])
    assert {u["object"] for u in report["uncovered_objects"]} == {"mug_1", "towel_1"}
    assert "PER-OBJECT STATISTICS" in report["statistics"]


def test_no_elicitor_means_no_reask_and_no_cost(tmp_path):
    m = _mixture(tmp_path, [H_DESK, H_TABLE],
                 ReaskConfig(window=2, threshold=0.0, scheduled_days=(1,)),
                 None)
    for day in range(5):
        m.update(_obs("laptop_1", "shelf", day, 13))
    assert m.reask_events == [] and m.calls_made == 0
