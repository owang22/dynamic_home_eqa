"""Unit tests for the naive LLM belief (prompt, parsing, fallback, cache
key) and its byte-identical prompt regression against the committed
completions fixture. Times are seconds since episode start."""

from __future__ import annotations

import pathlib
import random

import pytest

from baselines.beliefs import (LLMBelief, LLMBeliefConfig, LastObservation,
                               PromptCache)
from baselines.beliefs.llm_belief import (build_messages, cache_key,
                                          format_time, parse_completion,
                                          ranking_distribution, room_groups)
from baselines.registry import build_registered_belief
from baselines.types import EpisodeContext, Observation, SenseResult

RECS = ("bed_b1", "desk_b1", "couch_l1", "chair_k1", "chair_k2",
        "ON_PERSON", "OUT_OF_HOUSE")
ROOMS = {"bed_b1": "bedroom", "desk_b1": "bedroom", "couch_l1": "living",
         "chair_k1": "kitchen", "chair_k2": "kitchen"}
H = 3600


def _context() -> EpisodeContext:
    return EpisodeContext(
        episode_id="hh_x_seed0", household_id="hh_x", receptacle_ids=RECS,
        object_classes={"keys_a": "keys", "mug_b": "mug"}, budget_per_day=1,
        n_days=3, unsensable_receptacle_ids=("OUT_OF_HOUSE",))


def _obs(rec: str, t: int, obj: str = "keys_a") -> Observation:
    return Observation(object_id=obj, object_class="keys", receptacle_id=rec,
                       t=t, source="scripted")


def _empty(rec: str, t: int) -> SenseResult:
    return SenseResult(receptacle_id=rec, t=t, contents=())


def _llm(cache: PromptCache, floor_mass: float = 0.0) -> LLMBelief:
    """floor_mass 0 keeps the ranking arithmetic hand-checkable; the
    pipeline tests below pass the real floor explicitly."""
    model = LLMBelief(random.Random(0), LLMBeliefConfig(), cache, rooms=ROOMS,
                      floor_mass=floor_mass)
    model.reset(_context())
    return model


# ---------------------------------------------------------------- prompt

def test_format_time_weekday_and_clock() -> None:
    assert format_time(0) == "day 0 (Monday) 00:00"
    assert format_time(5 * 86400 + 14 * H + 32 * 60) == "day 5 (Saturday) 14:32"


def test_room_groups_use_bank_rooms_and_keep_specials_out() -> None:
    groups = room_groups(RECS, ROOMS)
    assert groups == [("bedroom", ["bed_b1", "desk_b1"]),
                      ("living room", ["couch_l1"]),
                      ("kitchen", ["chair_k1", "chair_k2"])]
    # Suffix fallback never invents a "kitchen 2".
    assert dict(room_groups(RECS))["kitchen"] == ["chair_k1", "chair_k2"]


def test_prompt_contents() -> None:
    cfg = LLMBeliefConfig(max_history=2)
    msgs = build_messages(
        t=2 * 86400 + 9 * H, object_id="keys_a", object_class="keys",
        receptacle_ids=RECS,
        history=[(0, "bed_b1"), (10 * H, "desk_b1"), (30 * H, "bed_b1")],
        exclusions=[(40 * H, "bed_b1"), (35 * H, "desk_b1")], config=cfg,
        rooms=ROOMS)
    assert msgs[0]["role"] == "system" and msgs[1]["role"] == "user"
    user = msgs[1]["content"]
    assert "Current time: day 2 (Wednesday) 09:00" in user
    assert "Object: keys_a (class: keys)" in user
    assert "bed_b1*, desk_b1*" in user          # seen-at markers
    assert "ON_PERSON" in user and "OUT_OF_HOUSE" in user
    assert "newest 2 of 3" in user and "day 0 (Monday) 00:00" not in user
    # Negative evidence is listed in time order.
    assert user.index("day 1 (Tuesday) 11:00: desk_b1") < user.index(
        "day 1 (Tuesday) 16:00: bed_b1")
    assert "JSON only" in user


# ---------------------------------------------------------------- parsing

def test_parse_completion_ok_dedupes_and_truncates() -> None:
    text = '{"ranking": ["bed_b1", "bed_b1", "OUT_OF_HOUSE", "desk_b1*"], "p_top": 0.7}'
    ranking, p_top, status = parse_completion(text, RECS, 2)
    assert status == "ok"
    assert ranking == ["bed_b1", "OUT_OF_HOUSE"]
    assert p_top == 0.7


@pytest.mark.parametrize("text, status", [
    ("not json at all", "no_json"),
    ('{"ranking": "bed_b1", "p_top": 0.5}', "bad_shape"),
    ('{"ranking": [], "p_top": 0.5}', "empty"),
    ('{"ranking": ["garage"], "p_top": 0.5}', "off_list"),
    (None, "no_json"),
])
def test_parse_completion_failures(text, status) -> None:
    ranking, _, got = parse_completion(text, RECS, 5)
    assert ranking is None and got == status


def test_parse_completion_tolerates_surrounding_text() -> None:
    text = 'Sure: {"ranking": ["couch_l1"], "p_top": 0.4} done'
    ranking, _, status = parse_completion(text, RECS, 5)
    assert status == "ok" and ranking == ["couch_l1"]


def test_ranking_distribution_is_geometric_and_normalized() -> None:
    dist = ranking_distribution(["a", "b", "c"], 0.5)
    assert dist["a"] == pytest.approx(4 / 7)
    assert dist["b"] == pytest.approx(2 / 7)
    assert dist["c"] == pytest.approx(1 / 7)
    assert sum(dist.values()) == pytest.approx(1.0)


# ------------------------------------------------------------------ model

def test_collect_mode_records_prompt_and_falls_back_to_lastobs() -> None:
    cache = PromptCache(collect=True)
    model = _llm(cache, floor_mass=0.02)
    model.update(_obs("bed_b1", 10))
    model.update(_empty("bed_b1", 20))
    pred = model.predict("keys_a", 30)
    # LastObs fallback through the pipeline: the ten-second-old empty
    # look all but erases bed_b1, and the floor holds the rest.
    assert pred.distribution["bed_b1"] < 0.01
    assert pred.argmax != "bed_b1"
    assert len(cache.prompts) == 1
    assert model.counts == {"predictions": 1, "pending": 1}
    diag = model.last_prediction_diagnostics()
    assert diag is not None and diag["fallback"] == 1.0 and diag["pending"] == 1.0


def test_cache_key_and_answer_mode() -> None:
    cache = PromptCache(collect=True)
    model = _llm(cache)
    model.update(_obs("bed_b1", 10))
    model.update(_empty("bed_b1", 20))
    model.predict("keys_a", 30)
    key = next(iter(cache.prompts))
    assert key == cache_key("hh_x_seed0", "keys_a", (10, "bed_b1"),
                            (20, "bed_b1"), 30, LLMBeliefConfig())
    # Same hour bucket, same evidence -> same key (one completion reused).
    model.predict("keys_a", 30 + 600)
    assert len(cache.prompts) == 1
    # Now answer from the cache.
    answered = _llm(PromptCache(answers={
        key: '{"ranking": ["OUT_OF_HOUSE", "couch_l1"], "p_top": 0.6}'}))
    answered.update(_obs("bed_b1", 10))
    answered.update(_empty("bed_b1", 20))
    pred = answered.predict("keys_a", 30)
    assert pred.argmax == "OUT_OF_HOUSE"
    assert pred.distribution["OUT_OF_HOUSE"] == pytest.approx(2 / 3)
    assert pred.distribution["couch_l1"] == pytest.approx(1 / 3)
    assert answered.counts == {"predictions": 1, "answered": 1}
    diag = answered.last_prediction_diagnostics()
    assert diag is not None and diag["p_top"] == 0.6 and diag["n_ranked"] == 2.0


def test_off_list_name_counts_as_fallback() -> None:
    cache = PromptCache(collect=True)
    probe = _llm(cache)
    probe.update(_obs("bed_b1", 10))
    probe.predict("keys_a", 30)
    key = next(iter(cache.prompts))
    model = _llm(PromptCache(answers={key: '{"ranking": ["garage"], "p_top": 1}'}))
    model.update(_obs("bed_b1", 10))
    pred = model.predict("keys_a", 30)
    assert pred.argmax == "bed_b1" and pred.distribution["bed_b1"] == 1.0
    assert model.counts["fallback"] == 1 and model.counts["fallback_off_list"] == 1


def test_llm_answer_is_not_overridden_by_base_exclusions() -> None:
    # The LLM saw the negative evidence in the prompt; if it still says
    # bed_b1, that answer stands (no hard exclusion on top).
    cache = PromptCache(collect=True)
    probe = _llm(cache)
    probe.update(_obs("bed_b1", 10))
    probe.update(_empty("bed_b1", 20))
    probe.predict("keys_a", 30)
    key = next(iter(cache.prompts))
    model = _llm(PromptCache(answers={key: '{"ranking": ["bed_b1"], "p_top": 0.9}'}))
    model.update(_obs("bed_b1", 10))
    model.update(_empty("bed_b1", 20))
    assert model.predict("keys_a", 30).argmax == "bed_b1"


def test_sighting_at_query_instant_short_circuits() -> None:
    model = _llm(PromptCache(collect=True))
    model.update(_obs("couch_l1", 50))
    pred = model.predict("keys_a", 50)
    assert pred.argmax == "couch_l1" and model.counts == {}


def test_registry_builds_llm_with_rooms_and_cache() -> None:
    cache = PromptCache(collect=True)
    model = build_registered_belief(
        {"name": "llm", "cache": cache, "rooms": ROOMS, "max_history": 5},
        random.Random(0))
    assert isinstance(model, LLMBelief)
    assert model.config.max_history == 5 and model.rooms == ROOMS
    assert model.cache is cache


# ------------------------------------------- fallback and the pipeline

def test_fallback_is_last_obs_through_the_pipeline() -> None:
    # Pending (collect mode): the answer is LastObs, and it gets the base
    # pipeline's negative evidence like any classical model.
    model = _llm(PromptCache(collect=True), floor_mass=0.02)
    plain = LastObservation(random.Random(0))
    plain.reset(_context())
    for m in (model, plain):
        m.update(_obs("bed_b1", 10 * H))
        m.update(_empty("bed_b1", 12 * H))
    assert model.predict("keys_a", 12 * H).distribution == pytest.approx(
        plain.predict("keys_a", 12 * H).distribution)
    assert model.predict("keys_a", 12 * H).distribution["bed_b1"] == 0.0
    assert model.counts["pending"] == 2


def test_llm_answer_gets_floor_but_not_suppression() -> None:
    cache = PromptCache(collect=True)
    probe = _llm(cache)
    probe.update(_obs("bed_b1", 10 * H))
    probe.update(_empty("bed_b1", 12 * H))
    probe.predict("keys_a", 12 * H)
    key = next(iter(cache.prompts))
    model = _llm(PromptCache(answers={key: '{"ranking": ["bed_b1", "desk_b1"], "p_top": 0.9}'}),
                 floor_mass=0.02)
    model.update(_obs("bed_b1", 10 * H))
    model.update(_empty("bed_b1", 12 * H))
    pred = model.predict("keys_a", 12 * H)
    f = model.floor_mass
    n = len(RECS)
    assert pred.argmax == "bed_b1"
    assert pred.distribution["bed_b1"] == pytest.approx((1 - f) * 2 / 3 + f / n)
    assert pred.distribution["OUT_OF_HOUSE"] == pytest.approx(f / n)


FIXTURE_DIR = pathlib.Path("reports/baselines/llm_floor/test")
FIXTURE_BANK = pathlib.Path(
    "banks/baselines/fleet/households__generated__gpt-5.6-terra__hh_001_bank.jsonl")


@pytest.mark.skipif(not (FIXTURE_DIR / "prompt.jsonl").exists()
                    or not FIXTURE_BANK.exists(),
                    reason="llm_floor test fixture or hh_001 bank not present")
def test_prompt_and_key_match_the_committed_fixture() -> None:
    """The prompt and cache key the belief builds for the fixture question
    must be byte-identical to the committed ``test/prompt.jsonl`` (the
    one the completions cache was generated against); a drift here would
    silently orphan every offline completion."""
    import json
    from baselines.bank import JsonlBank
    from baselines.llm_floor import bank_rooms
    fixture = json.loads((FIXTURE_DIR / "prompt.jsonl").read_text().splitlines()[0])
    episode_id, object_id, _, _, bucket = fixture["key"].split("|")
    episode = next(e for e in JsonlBank(path=FIXTURE_BANK).episodes()
                   if e.episode_id == episode_id)
    cache = PromptCache(collect=True)
    model = LLMBelief(random.Random(0), LLMBeliefConfig(), cache,
                      rooms=bank_rooms("hh_001", 0))
    model.reset(episode.agent_view())
    for obs in episode.initial_observations:
        model.update(obs)
    # "day 4 (Friday) 18:20" in the fixture's user message.
    t = 4 * 86400 + 18 * H + 20 * 60
    assert t // 3600 == int(bucket)
    for event in episode.evidence_stream():
        if event.t > t:
            break
        model.update(event)
    model.predict(object_id, t)
    assert model.last_key == fixture["key"]
    assert model.last_messages == fixture["messages"]
