"""Routine-driven query stream: loader strictness and generation timing.
Times are seconds since episode start."""

from __future__ import annotations

import json
import pathlib
import random

import pytest

from baselines.bank import BankFormatError, JsonlBank
from baselines.query_stream import (ActivityInstance, QueryRule,
                                    QueryRuleSet, routine_questions)
from baselines.types import DAY_SECONDS

H = 3600


def _tiny_bank_rows(with_header_field: bool) -> list:
    header = {"kind": "episode_header", "episode_id": "ep0",
              "household_id": "hh", "receptacle_ids": ["a", "b"],
              "object_classes": {"keys_1": "keys"},
              "budget_per_day": 1, "n_days": 1}
    if with_header_field:
        header["query_generation"] = "routine_driven"
    return [header,
            {"kind": "truth", "episode_id": "ep0", "object_id": "keys_1",
             "t": 0, "receptacle_id": "a"},
            {"kind": "question", "episode_id": "ep0", "question_id": "q0",
             "object_id": "keys_1", "t_query": 10, "day_index": 0,
             "origin": "activity:work_away"}]


def test_loader_rejects_routine_bank_without_query_generation(
        tmp_path: pathlib.Path) -> None:
    for with_field, ok in ((False, False), (True, True)):
        path = tmp_path / f"bank_{with_field}.jsonl"
        path.write_text("".join(json.dumps(r) + "\n"
                                for r in _tiny_bank_rows(with_field)))
        if ok:
            episode = next(JsonlBank(path=path).episodes())
            assert episode.questions_by_day[0][0].object_class == "keys"
        else:
            with pytest.raises(BankFormatError, match="query_generation"):
                next(JsonlBank(path=path).episodes())


def test_routine_timestamps_land_near_their_activities() -> None:
    rules = QueryRuleSet(rules={
        "work_away": QueryRule(activity="work_away", trigger="before",
                               objects=("keys",),
                               offset_mean_min=15.0, offset_sd_min=5.0),
        "meal_prep": QueryRule(activity="meal_prep", trigger="during",
                               objects=("pot",)),
    }, background_query_rate=1.0)
    instances = []
    for d in range(3):
        base = d * DAY_SECONDS
        instances.append(ActivityInstance("work_away", "resident_1",
                                          base + 9 * H, base + 17 * H))
        instances.append(ActivityInstance("meal_prep", "resident_1",
                                          base + 18 * H, base + 19 * H))
    classes = {"keys_1": "keys", "pot_1": "pot", "mug_1": "mug"}
    awake = {d: [(d * DAY_SECONDS + 7 * H, d * DAY_SECONDS + 22 * H)]
             for d in range(3)}
    stream = routine_questions(instances, rules, classes, awake,
                               n_days=3, first_question_day=0,
                               questions_per_day=20,
                               rng=random.Random(0))
    assert len(stream) == 60
    departures = [q for q in stream if q[2] == "activity:work_away"]
    meals = [q for q in stream if q[2] == "activity:meal_prep"]
    assert departures and meals
    for obj, t, _ in departures:
        assert obj == "keys_1"
        start = (t // DAY_SECONDS) * DAY_SECONDS + 9 * H
        # Within mean +/- 5 sd of the declared lead time, and never after
        # more than a hair past the start (gaussian tail, clamped to day).
        assert start - 40 * 60 <= t <= start + 10 * 60
    for obj, t, _ in meals:
        assert obj == "pot_1"
        base = (t // DAY_SECONDS) * DAY_SECONDS
        assert base + 18 * H <= t < base + 19 * H
    background = [q for q in stream if q[2] == "background"]
    assert background, "the background floor must be nonzero"
