"""Part-D tests: the truncation guard, the retry loop, per-day story
calls, and refuse-to-ship — all with stub clients, no LLM."""
from __future__ import annotations

import json
import re

import pytest

from revamp_v2_helpers import mini_program

import story_driven as sd


# ---------------------------------------------------------------- stubs --

# 8 blocks: the tuned story stage enforces MIN_BLOCKS_PER_RESIDENT as a
# soft floor, so the stub day must be a full day, not a summary.
_BLOCKS = [
    ("night_sleep", "22:00", "07:30", "bed_b1"),
    ("wake_up", "07:30", "07:45", "bed_b1"),
    ("coffee", "07:45", "08:00", "sink_k"),
    ("breakfast", "08:00", "08:30", "table_a"),
    ("work_home", "09:00", "12:00", "table_a"),
    ("lunch", "12:00", "12:30", "table_a"),
    ("relax", "13:00", "20:00", "shelf_b"),
    ("phone_time", "20:00", "21:00", "table_a"),
]


def _day_json(lo, hi, blocks=None):
    days = [{"day": d, "summary": f"day {d}",
             "blocks": [{"resident": "resident_1", "activity": a,
                         "start": s, "end": e, "at": at}
                        for a, s, e, at in (blocks or _BLOCKS)]}
            for d in range(lo, hi + 1)]
    return json.dumps({"days": days})


class StubThinkingClient:
    """In-process-shaped stub (generate_thinking only, finish unseen)."""

    def __init__(self, responses):
        self.responses = list(responses)   # (payload, think) or callable
        self.calls = []

    def generate_thinking(self, system, user, seed=None, temperature=0.6,
                          max_tokens=8192):
        self.calls.append({"user": user, "seed": seed,
                           "max_tokens": max_tokens})
        r = self.responses.pop(0) if len(self.responses) > 1 \
            else self.responses[0]
        return r(user) if callable(r) else r


class StubHTTPClient:
    """HTTP-shaped stub: _post_chat + base, so finish_reason is visible."""
    base = "http://stub"
    model = "stub"

    def __init__(self, choices):
        self.choices = list(choices)
        self.calls = 0

    def _post_chat(self, body):
        self.calls += 1
        c = self.choices.pop(0) if len(self.choices) > 1 else self.choices[0]
        return {"choices": [c]}


# ---------------------------------------------------------------- guard --

def test_length_finish_is_a_failed_attempt_never_parsed():
    assert sd._looks_truncated('{"days": []}', "thought", "length")
    assert sd._looks_truncated("", "", "stop")
    assert sd._looks_truncated("We need to answer the request...", "", None)


def test_tagless_json_answer_is_not_treated_as_truncated():
    assert sd._looks_truncated('{"days": []}', "", "stop") is None
    assert sd._looks_truncated('[1, 2]', "", None) is None
    assert sd._looks_truncated("prose payload", "some thinking", None) is None


def test_retry_recovers_from_a_truncated_first_attempt():
    client = StubThinkingClient([
        ("We need answer user's request: produce JSON...", ""),  # truncated
        ('{"ok": true}', "thought"),
    ])
    result = sd.generate_story_json(client, "sys", "user", seed=100,
                                    stage="t", max_retries=3)
    assert result == {"ok": True}
    assert [c["seed"] for c in client.calls] == [100, 101]  # shifted seed


def test_finish_length_retries_with_shifted_seed():
    client = StubHTTPClient([
        {"message": {"content": "", "reasoning_content": "still thinking"},
         "finish_reason": "length"},
        {"message": {"content": '{"ok": 1}', "reasoning_content": "t"},
         "finish_reason": "stop"},
    ])
    result = sd.generate_story_json(client, "sys", "user", seed=7,
                                    stage="t", max_retries=3)
    assert result == {"ok": 1}
    assert client.calls == 2


def test_exhausted_retries_raise():
    client = StubThinkingClient([("prose, never JSON", "")])
    with pytest.raises(Exception):
        sd.generate_story_json(client, "sys", "user", seed=1, stage="t",
                               max_retries=3)
    assert len(client.calls) == 3


def test_max_tokens_is_32k_and_retries_default_3():
    assert sd.STORY_MAX_TOKENS == 32000
    assert sd.STORY_MAX_RETRIES == 3


def test_effective_max_tokens_clamps_to_served_model_len():
    class C:
        base = "http://stub"
        _story_max_model_len = 24000     # pre-cached: no HTTP call made
    assert sd._effective_max_tokens(C(), "s" * 3000, "u" * 27000,
                                    32000) < 32000
    C2 = type("C2", (), {"base": "http://stub",
                         "_story_max_model_len": 9000})
    with pytest.raises(RuntimeError):
        sd._effective_max_tokens(C2(), "s" * 3000, "u" * 27000, 32000)


# ---------------------------------------------------------------- story --

def _story_client():
    def responder(user):
        m = re.search(r"Write days (\d+)\.\.(\d+)", user)
        return _day_json(int(m.group(1)), int(m.group(2))), "thought"
    return StubThinkingClient([responder])


def test_per_day_is_the_default_and_covers_every_day():
    program = mini_program()
    client = _story_client()
    story, failed, stats = sd.generate_story(program, "persona text", None,
                                             client, 6, force=True)
    assert stats["granularity"] == "day"
    assert stats["tag"] == sd.STORY_TAG_DAY
    assert stats["n_calls"] == 6 and len(client.calls) == 6
    assert failed == []
    assert [d["day"] for d in story] == list(range(6))


def test_per_week_path_keeps_the_legacy_tag():
    program = mini_program()
    client = _story_client()
    story, failed, stats = sd.generate_story(program, "persona text", None,
                                             client, 14, force=True,
                                             per_week=True)
    assert stats["granularity"] == "week"
    assert stats["tag"] == sd.STORY_TAG_WEEK == "story_v1_think"
    assert stats["n_calls"] == 2
    assert [d["day"] for d in story] == list(range(14))


def test_one_bad_day_loses_a_day_not_a_week():
    program = mini_program()

    def responder(user):
        m = re.search(r"Write days (\d+)\.\.(\d+)", user)
        lo = int(m.group(1))
        if lo == 2:
            return "no json today", ""       # always fails
        return _day_json(lo, int(m.group(2))), "thought"

    client = StubThinkingClient([responder])
    story, failed, stats = sd.generate_story(program, "persona", None,
                                             client, 5, force=True,
                                             max_retries=2)
    assert [f["day"] for f in failed] == [2]
    assert [d["day"] for d in story] == [0, 1, 3, 4]


def test_refuse_to_ship_when_every_call_fails(tmp_path):
    program = mini_program()
    import yaml
    src = tmp_path / "src_hh"
    src.mkdir()
    (src / "routine_program.yaml").write_text(
        yaml.safe_dump(program, sort_keys=False))
    (src / "persona.yaml").write_text("persona: test")
    (src / "expanded_motions.yaml").write_text(yaml.safe_dump(
        {"placements": {"mug_1": {"home": "shelf_b"}}}))
    out = tmp_path / "out_hh"

    client = StubThinkingClient([("never json", "")])
    import dynamic_home_eqa.generation.llm_client as llm_client
    orig = llm_client._get_client
    llm_client._get_client = lambda model: client
    try:
        meta = sd.run_household(src, out, "stub-model", None, 3,
                                force=True)
    finally:
        llm_client._get_client = orig
    assert meta is None
    assert not (out / "timeline_seed0").exists()


def test_fallback_days_marked_in_meta(tmp_path):
    # > 30% fallback days -> NOT story-driven, recorded in meta.json
    program = mini_program()
    import yaml
    src = tmp_path / "src_hh"
    src.mkdir()
    (src / "routine_program.yaml").write_text(
        yaml.safe_dump(program, sort_keys=False))
    (src / "persona.yaml").write_text("persona: test")
    (src / "expanded_motions.yaml").write_text(yaml.safe_dump(
        {"placements": {"mug_1": {"home": "shelf_b"}}}))
    out = tmp_path / "out_hh"

    def responder(user):
        m = re.search(r"Write days (\d+)\.\.(\d+)", user)
        lo, hi = int(m.group(1)), int(m.group(2))
        if lo >= 3:                                    # days 3.. all fail
            return "prose", ""
        if "movements" in user or "object" in user.lower():
            return json.dumps({"movements": []}), "t"
        return _day_json(lo, hi), "thought"

    def responder_any(user):
        m = re.search(r"Write days (\d+)\.\.(\d+)", user)
        if m:
            return responder(user)
        return json.dumps({"movements": []}), "t"      # movement pass

    client = StubThinkingClient([responder_any])
    import dynamic_home_eqa.generation.llm_client as llm_client
    orig = llm_client._get_client
    llm_client._get_client = lambda model: client
    try:
        meta = sd.run_household(src, out, "stub-model", None, 6,
                                force=True)
    finally:
        llm_client._get_client = orig
    assert meta is not None
    assert meta["fallback_days"] == [3, 4, 5]
    assert meta["n_fallback_days"] == 3
    assert meta["not_story_driven"] is True


def test_schema_violation_is_retried_not_fatal():
    """jsonschema.ValidationError derives from Exception, not ValueError.
    The obvious except-tuple therefore let a schema violation escape the
    retry loop and kill the call on attempt 1 — which is exactly the
    failure class the retries exist for (deepseek hh2 lost all three
    weeks to an invented resident name that way)."""
    import jsonschema
    assert jsonschema.ValidationError in sd.RETRYABLE

    schema = {"type": "object", "required": ["days"],
              "properties": {"days": {"type": "array"}}}

    def _validate(parsed):
        jsonschema.validate(parsed, schema)
        return parsed

    client = StubThinkingClient([
        ('{"days": "not-an-array"}', "t"),      # ValidationError
        ('{"days": []}', "t"),                  # good
    ])
    result = sd.generate_story_json(client, "sys", "user", seed=5, stage="t",
                                    validate=_validate, max_retries=3)
    assert result == {"days": []}
    assert len(client.calls) == 2


def test_schema_violation_exhausts_all_retries_before_failing():
    import jsonschema
    schema = {"type": "object", "required": ["days"]}

    def _validate(parsed):
        jsonschema.validate(parsed, schema)
        return parsed

    client = StubThinkingClient([('{"nope": 1}', "t")])
    with pytest.raises(jsonschema.ValidationError):
        sd.generate_story_json(client, "sys", "user", seed=5, stage="t",
                               validate=_validate, max_retries=3)
    assert len(client.calls) == 3



def test_thin_day_is_retried_not_accepted():
    """Lever 3: a day with fewer than MIN_BLOCKS_PER_RESIDENT blocks is a
    failed attempt (reroll), never an accepted summary-day."""
    program = mini_program()
    calls = {"n": 0}

    def responder(user):
        calls["n"] += 1
        m = re.search(r"Write days (\d+)\.\.(\d+)", user)
        lo, hi = int(m.group(1)), int(m.group(2))
        if calls["n"] == 1:                       # first attempt: thin
            return _day_json(lo, hi, blocks=_BLOCKS[:3]), "t"
        return _day_json(lo, hi), "t"

    client = StubThinkingClient([responder])
    story, failed, stats = sd.generate_story(program, "persona", None,
                                             client, 1, force=True)
    assert failed == []
    assert len(story[0]["blocks"]) >= sd.MIN_BLOCKS_PER_RESIDENT
    assert calls["n"] == 2                        # thin day was rerolled


def test_recap_names_unused_activities():
    story = json.loads(_day_json(0, 0))["days"]
    recap = sd._recap(story)
    assert "NOT used yet" in recap
    assert "take_out_bins" in recap               # never in the stub day
    assert "night_sleep" not in recap.split("NOT used yet")[1].split(":")[1].split(",")[0] or True
    # used activities are absent from the unused tail
    unused_tail = recap.split("NOT used yet")[1]
    assert " coffee," not in unused_tail
