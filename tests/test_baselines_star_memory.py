"""STAR memory-loop tests: the indexed log's three lookup axes and its
ground-truth isolation, the recall tools, the loop's step/recall caps
and illegal-action path, and the scripted selector's fresh-memory
shortcut and newest-first verification order."""

from __future__ import annotations

import json
import random
from typing import Dict, List, Optional, Tuple

import pytest

from baselines.beliefs.last_observation import LastObservation
from baselines.memory.indexed_observation_log import IndexedObservationLog
from baselines.memory.recall_tools import (recall_object_history,
                                           recall_receptacle_history,
                                           recall_time_pattern)
from baselines.policies.star_memory_loop import (ACTION_SCHEMA, ActionSelector,
                                                 AnswerCall, LoopView,
                                                 QwenSelector, RecallCall,
                                                 ScriptedRecallThenVerify,
                                                 SelectorError, SenseCall,
                                                 StarAction,
                                                 StarMemoryLoopPolicy)
from baselines.star_study import run_star_episode
from baselines.types import (DAY_SECONDS, AnswerNow, Episode, EpisodeContext,
                             Observation, Prediction, Question, Sense,
                             SenseResult)

HOUR = 3600


def obs(object_id: str, receptacle: str, t: int) -> Observation:
    return Observation(object_id=object_id, object_class=object_id.split("_")[0],
                       receptacle_id=receptacle, t=t, source="scripted")


def build_log() -> IndexedObservationLog:
    log = IndexedObservationLog(
        object_classes={"mug_1": "mug", "mug_2": "mug", "key_1": "key"},
        rooms={"counter": "kitchen", "table": "kitchen", "desk": "office"})
    log.ingest(obs("mug_1", "counter", 1 * HOUR))
    log.ingest(obs("key_1", "desk", 2 * HOUR))
    log.ingest(obs("mug_1", "desk", 26 * HOUR))          # day 1, hour 2
    log.ingest(obs("mug_2", "table", 27 * HOUR))
    log.ingest(SenseResult(receptacle_id="counter", t=30 * HOUR,
                           contents=("mug_2",)))
    return log


# ------------------------------------------------------------ the log

def test_spatial_lookup_by_receptacle_and_room() -> None:
    log = build_log()
    at_counter = log.lookup(receptacle_id="counter")
    # mug_1 sighting, then the sense: mug_2 present + absences of mug_1/key_1.
    assert {(r.object_id, r.present) for r in at_counter} == {
        ("mug_1", True), ("mug_2", True), ("mug_1", False), ("key_1", False)}
    kitchen = log.lookup(room_id="kitchen", present=True)
    assert {r.receptacle_id for r in kitchen} == {"counter", "table"}
    office = log.lookup(room_id="office")
    assert [r.object_id for r in office] == ["mug_1", "key_1"]


def test_semantic_lookup_by_object_and_class() -> None:
    log = build_log()
    mug1 = log.lookup(object_id="mug_1", present=True)
    assert [(r.receptacle_id, r.t) for r in mug1] == [
        ("desk", 26 * HOUR), ("counter", 1 * HOUR)]      # newest first
    mugs = log.lookup(object_class="mug", present=True)
    assert {r.object_id for r in mugs} == {"mug_1", "mug_2"}


def test_temporal_lookup_window_weekday_hour_compose() -> None:
    log = build_log()
    day0 = log.lookup(t_min=0, t_max=DAY_SECONDS - 1)
    assert {r.object_id for r in day0} == {"mug_1", "key_1"}
    hour2 = log.lookup(hours={2}, present=True)
    assert {(r.object_id, r.t) for r in hour2} == {
        ("key_1", 2 * HOUR), ("mug_1", 26 * HOUR)}
    # Compose all three axes: mugs, kitchen, day 1 only.
    combined = log.lookup(object_class="mug", room_id="kitchen",
                          t_min=DAY_SECONDS, weekdays={1}, present=True)
    assert [(r.object_id, r.receptacle_id) for r in combined] == [
        ("mug_2", "counter"), ("mug_2", "table")]   # newest first
    assert log.lookup(object_id="mug_1", present=True,
                      limit=1)[0].t == 26 * HOUR


def test_lookup_never_reads_past_now() -> None:
    log = build_log()
    early = log.lookup(object_id="mug_1", t_max=2 * HOUR)
    assert [(r.receptacle_id,) for r in early] == [("counter",)]


def test_memory_never_sees_ground_truth() -> None:
    """The log is built from the agent stream only: an object that truth
    moved but the stream never reported stays where the stream left it,
    and ingest refuses non-agent-visible types outright."""
    log = IndexedObservationLog(object_classes={"mug_1": "mug"})
    log.ingest(obs("mug_1", "counter", 1 * HOUR))
    # Truth (never shown to the log): mug_1 moved to the desk at t=2h.
    records = log.lookup(object_id="mug_1")
    assert [(r.receptacle_id, r.present) for r in records] == [
        ("counter", True)]
    with pytest.raises(TypeError):
        log.ingest(("mug_1", "desk", 2 * HOUR))  # type: ignore[arg-type]


# ------------------------------------------------------- recall tools

def test_recall_tools_text_and_records() -> None:
    log = build_log()
    now = 31 * HOUR
    history = recall_object_history(log, "mug_1", now)
    assert "seen at desk (office)" in history.text
    assert "absent from counter" in history.text
    assert history.records[0].t == 30 * HOUR  # the absence is newest
    assert len(history.text.splitlines()) <= 15

    receptacle = recall_receptacle_history(log, "counter", now)
    assert "mug_2" in receptacle.text
    assert all(r.present for r in receptacle.records)

    pattern = recall_time_pattern(log, "mug_1", 26 * HOUR + 30 * 60,
                                  hour_window=1)
    lines = pattern.text.splitlines()
    # Both sightings fall near hour 2 (t=1h is within the +/-1h window);
    # equal counts rank the fresher receptacle first.
    assert "desk" in lines[1] and "counter" in lines[2]
    empty = recall_object_history(log, "sock_9", now)
    assert empty.records == () and "no records" in empty.text


# ------------------------------------------------------------ the loop

def make_context() -> EpisodeContext:
    return EpisodeContext(
        episode_id="ep0", household_id="hh0",
        receptacle_ids=("counter", "table", "desk", "OUT_OF_HOUSE"),
        object_classes={"mug_1": "mug", "key_1": "key"},
        budget_per_day=5, n_days=2,
        unsensable_receptacle_ids=("OUT_OF_HOUSE",))


def make_question(qid: str = "q0", t: int = 30 * HOUR) -> Question:
    return Question(question_id=qid, object_id="mug_1", t_query=t,
                    day_index=t // DAY_SECONDS)


def uniform_prediction() -> Prediction:
    locations = ("counter", "table", "desk", "OUT_OF_HOUSE")
    return Prediction(distribution={r: 0.25 for r in locations},
                      argmax="counter")


class FixedSelector(ActionSelector):
    """Replays a scripted list of actions/errors for loop tests."""

    def __init__(self, actions: List[object]) -> None:
        self._actions = list(actions)
        self.views: List[LoopView] = []

    def select(self, view: LoopView) -> StarAction:
        self.views.append(view)
        if not self._actions:
            return AnswerCall(receptacle_id=view.fallback_receptacle,
                              from_fallback=True)
        item = self._actions.pop(0)
        if isinstance(item, Exception):
            raise item
        assert isinstance(item, (RecallCall, SenseCall, AnswerCall))
        return item


def test_recall_cap_forces_fallback() -> None:
    recalls = [RecallCall(tool="recall_object_history") for _ in range(10)]
    selector = FixedSelector(list(recalls))
    policy = StarMemoryLoopPolicy(selector, max_steps=8, max_recalls=4)
    policy.reset(make_context())
    action = policy.decide(make_question(), uniform_prediction(), 5,
                           30 * HOUR)
    # 4 recalls run, the 5th+6th are illegal (cap) -> fallback answer.
    assert isinstance(action, AnswerNow)
    stats = policy.last_question_stats
    assert stats["recalls"] == 4
    assert stats["illegal"] == 2
    assert stats["fallbacks"] == 1
    assert policy.answer_override is None


def test_step_cap_bounds_the_loop() -> None:
    policy = StarMemoryLoopPolicy(
        FixedSelector([SenseCall("counter"), SenseCall("table"),
                       SenseCall("desk")]),
        max_steps=2, max_recalls=1)
    policy.reset(make_context())
    q = make_question()
    a1 = policy.decide(q, uniform_prediction(), 5, q.t_query)
    assert isinstance(a1, Sense)
    miss = SenseResult(receptacle_id=a1.receptacle_id, t=q.t_query,
                       contents=())
    policy.observe(miss)
    a2 = policy.decide(q, uniform_prediction(), 4, q.t_query, miss)
    assert isinstance(a2, Sense)
    miss2 = SenseResult(receptacle_id=a2.receptacle_id, t=q.t_query,
                        contents=())
    policy.observe(miss2)
    a3 = policy.decide(q, uniform_prediction(), 3, q.t_query, miss2)
    assert isinstance(a3, AnswerNow)
    assert policy.last_question_stats["step_cap_hits"] == 1


def test_illegal_actions_rejected_then_fallback() -> None:
    # Unknown receptacle twice in a row -> rejection line, retry, fallback.
    policy = StarMemoryLoopPolicy(
        FixedSelector([SenseCall("no_such"), SenseCall("no_such")]))
    policy.reset(make_context())
    action = policy.decide(make_question(), uniform_prediction(), 5,
                           30 * HOUR)
    assert isinstance(action, AnswerNow)
    stats = policy.last_question_stats
    assert stats["illegal"] == 2 and stats["fallbacks"] == 1


def test_illegal_then_legal_recovers() -> None:
    policy = StarMemoryLoopPolicy(
        FixedSelector([SenseCall("OUT_OF_HOUSE"), SenseCall("counter")]))
    policy.reset(make_context())
    action = policy.decide(make_question(), uniform_prediction(), 5,
                           30 * HOUR)
    assert isinstance(action, Sense) and action.receptacle_id == "counter"
    # The rejection line is in working memory for the next selector view.


def test_zero_budget_sense_is_illegal_not_forced() -> None:
    policy = StarMemoryLoopPolicy(
        FixedSelector([SenseCall("counter"), SenseCall("counter")]))
    policy.reset(make_context())
    action = policy.decide(make_question(), uniform_prediction(), 0,
                           30 * HOUR)
    assert isinstance(action, AnswerNow)
    assert policy.last_question_stats["illegal"] == 2


def test_found_at_query_instant_answers() -> None:
    policy = StarMemoryLoopPolicy(FixedSelector([SenseCall("desk")]))
    policy.reset(make_context())
    q = make_question()
    a1 = policy.decide(q, uniform_prediction(), 5, q.t_query)
    assert isinstance(a1, Sense)
    hit = SenseResult(receptacle_id="desk", t=q.t_query,
                      contents=("mug_1",))
    policy.observe(hit)
    a2 = policy.decide(q, uniform_prediction(), 4, q.t_query, hit)
    assert isinstance(a2, AnswerNow)
    # A found answer needs no override: the belief one-hots at the instant.
    assert policy.answer_override is None


def test_answer_override_and_memory_flag() -> None:
    policy = StarMemoryLoopPolicy(
        FixedSelector([AnswerCall(receptacle_id="OUT_OF_HOUSE")]))
    policy.reset(make_context())
    action = policy.decide(make_question(), uniform_prediction(), 5,
                           30 * HOUR)
    assert isinstance(action, AnswerNow)
    assert policy.answer_override == "OUT_OF_HOUSE"
    stats = policy.last_question_stats
    assert stats["answered_from_memory"] == 1


# --------------------------------------------------- scripted selector

def scripted_policy(fresh_age_s: int = 3600) -> StarMemoryLoopPolicy:
    return StarMemoryLoopPolicy(
        ScriptedRecallThenVerify(fresh_age_s=fresh_age_s))


def test_scripted_fresh_memory_shortcut() -> None:
    policy = scripted_policy()
    policy.reset(make_context())
    t_now = 30 * HOUR
    policy.observe(obs("mug_1", "table", t_now - 30 * 60))  # 30 min old
    action = policy.decide(make_question(t=t_now), uniform_prediction(),
                           5, t_now)
    assert isinstance(action, AnswerNow)
    assert policy.answer_override == "table"
    stats = policy.last_question_stats
    assert stats["recalls"] == 1 and stats["senses"] == 0
    assert stats["answered_from_memory"] == 1


def test_scripted_verifies_newest_first_and_skips_tried() -> None:
    policy = scripted_policy()
    policy.reset(make_context())
    t_now = 40 * HOUR
    policy.observe(obs("mug_1", "counter", 2 * HOUR))
    policy.observe(obs("mug_1", "desk", 10 * HOUR))
    policy.observe(obs("mug_1", "table", 20 * HOUR))     # newest, stale
    q = make_question(t=t_now)
    a1 = policy.decide(q, uniform_prediction(), 5, t_now)
    assert isinstance(a1, Sense) and a1.receptacle_id == "table"
    miss = SenseResult(receptacle_id="table", t=t_now, contents=())
    policy.observe(miss)
    a2 = policy.decide(q, uniform_prediction(), 4, t_now, miss)
    assert isinstance(a2, Sense) and a2.receptacle_id == "desk"
    miss2 = SenseResult(receptacle_id="desk", t=t_now, contents=())
    policy.observe(miss2)
    a3 = policy.decide(q, uniform_prediction(), 3, t_now, miss2)
    assert isinstance(a3, Sense) and a3.receptacle_id == "counter"
    hit = SenseResult(receptacle_id="counter", t=t_now,
                      contents=("mug_1",))
    policy.observe(hit)
    a4 = policy.decide(q, uniform_prediction(), 2, t_now, hit)
    assert isinstance(a4, AnswerNow)


def test_scripted_exhausted_recall_falls_back_to_argmax() -> None:
    policy = scripted_policy()
    policy.reset(make_context())
    t_now = 40 * HOUR
    # No sightings at all: recall is empty, no plan, answer the argmax.
    action = policy.decide(make_question(t=t_now), uniform_prediction(),
                           5, t_now)
    assert isinstance(action, AnswerNow)
    assert policy.answer_override == "counter"  # the argmax, via fallback
    assert policy.last_question_stats["answered_from_memory"] == 0


# ------------------------------------------------------- QwenSelector

def fixed_generate(payloads: List[str]) -> "list[str] | object":
    def generate(system: str, user: str, schema: Dict[str, object],
                 seed: int) -> str:
        assert schema is ACTION_SCHEMA
        return payloads.pop(0)
    return generate


def make_view(working: Tuple[str, ...] = ()) -> LoopView:
    return LoopView(
        question=make_question(), object_class="mug",
        working_memory=working, budget_remaining=3, steps_used=0,
        recalls_used=0, max_steps=8, max_recalls=4, tried=(),
        sensable_receptacles=("counter", "table", "desk"),
        all_locations=("counter", "table", "desk", "OUT_OF_HOUSE"),
        rooms={"counter": "kitchen", "table": "kitchen", "desk": "office"},
        fallback_receptacle="counter", last_recall=None)


def test_qwen_selector_parses_actions_and_rejects_garbage() -> None:
    payloads = [
        json.dumps({"action": "recall_object_history", "args": {}}),
        json.dumps({"action": "sense", "args": {"receptacle_id": "desk"}}),
        json.dumps({"action": "answer",
                    "args": {"receptacle_id": "OUT_OF_HOUSE"}}),
        "not json at all",
        json.dumps({"action": "dance", "args": {}}),
        json.dumps({"action": "sense", "args": {}}),
    ]
    generate = fixed_generate(payloads)
    selector = QwenSelector(generate)  # type: ignore[arg-type]
    view = make_view()
    a1 = selector.select(view)
    assert isinstance(a1, RecallCall) and a1.object_id == "mug_1"
    a2 = selector.select(view)
    assert isinstance(a2, SenseCall) and a2.receptacle_id == "desk"
    a3 = selector.select(view)
    assert isinstance(a3, AnswerCall) and not a3.from_fallback
    for _ in range(3):
        with pytest.raises(SelectorError):
            selector.select(view)
    assert selector.calls == 6


def test_qwen_prompt_carries_view() -> None:
    captured: List[str] = []

    def generate(system: str, user: str, schema: Dict[str, object],
                 seed: int) -> str:
        captured.append(user)
        return json.dumps({"action": "answer",
                           "args": {"receptacle_id": "counter"}})

    selector = QwenSelector(generate)
    selector.select(make_view(working=("recall ... -> memory line",)))
    prompt = captured[0]
    assert "mug_1" in prompt and "kitchen" in prompt
    assert "memory line" in prompt
    assert "REMAINING SENSE BUDGET TODAY: 3" in prompt
    assert "OUT_OF_HOUSE" in prompt


# ------------------------------------------- study runner integration

def tiny_episode() -> Episode:
    """Two-day episode: mug_1 silently moves to the desk before the
    query, so recall-then-verify must sense to find it; key_1 is queried
    fresh."""
    recs = ("counter", "table", "desk", "OUT_OF_HOUSE")
    t_move = 5 * HOUR
    questions = (
        (Question(question_id="d0q0", object_id="mug_1",
                  t_query=8 * HOUR, day_index=0),),
        (Question(question_id="d1q0", object_id="key_1",
                  t_query=DAY_SECONDS + 1 * HOUR, day_index=1),),
    )
    return Episode(
        episode_id="tiny", household_id="hh_tiny", receptacle_ids=recs,
        object_classes={"mug_1": "mug", "key_1": "key"},
        initial_observations=(
            obs("mug_1", "counter", 0), obs("key_1", "desk", 0)),
        scripted_observations=(
            obs("key_1", "desk", DAY_SECONDS + 30 * 60),),
        questions_by_day=questions, budget_per_day=3,
        trajectories={
            "mug_1": ((0, "counter"), (t_move, "desk")),
            "key_1": ((0, "desk"),)},
        unsensable_receptacle_ids=("OUT_OF_HOUSE",))


def test_run_star_episode_scripted_end_to_end() -> None:
    episode = tiny_episode()
    belief = LastObservation(random.Random(0))
    policy = scripted_policy()
    records = list(run_star_episode(belief, policy, episode))
    assert [r["question_id"] for r in records] == ["d0q0", "d1q0"]
    first, second = records
    # mug_1: last seen counter (stale), verify counter -> miss, then no
    # other recalled location: fallback argmax now points at the desk?
    # LastObservation one-hots on the newest sighting; after the counter
    # miss its suppressed mass moves off the counter. The scripted plan
    # is exhausted, so the answer is the belief argmax at that point.
    assert first["budget_spent"] == 1
    assert first["star"]["recalls"] == 1
    # key_1 was seen 30 minutes before the query: fresh shortcut.
    assert second["correct"] and second["budget_spent"] == 0
    assert second["answer_receptacle"] == "desk"
    assert second["answer_overridden"]
    assert second["star"]["answered_from_memory"] == 1
