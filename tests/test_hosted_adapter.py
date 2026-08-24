"""Hosted-generation pilot, Task 1: the adapter's stated guarantees, one
test each — auth header iff key set (and never in logs/exceptions),
hosted body dialect, vLLM body byte-identical, 429 retried / 400 not,
spend guard aborts at the cap. No live API calls: requests.post is
monkeypatched throughout.
"""
from __future__ import annotations

import logging
import pathlib
import sys

import pytest
import requests

REPO = pathlib.Path(__file__).resolve().parent.parent
if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))

from dynamic_home_eqa.generation import llm_client  # noqa: E402
from dynamic_home_eqa.generation.hosted_spend import (  # noqa: E402
    SpendCapExceeded, SpendGuard)

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["a"],
    "properties": {"a": {"type": "string"},
                   "opt": {"type": "integer"}},
}
RATES = {"fake-model": {"input_per_1m": 1.0, "output_per_1m": 2.0,
                        "cached_input_per_1m": 0.1}}
USAGE = {"prompt_tokens": 1000, "completion_tokens": 500,
         "prompt_tokens_details": {"cached_tokens": 0},
         "completion_tokens_details": {"reasoning_tokens": 100}}


class FakeResp:
    def __init__(self, status, payload=None, headers=None, text=""):
        self.status_code = status
        self._payload = payload
        self.headers = headers or {}
        self.text = text

    def json(self):
        return self._payload


def ok_response(content='{"a": "x"}'):
    return FakeResp(200, {
        "model": "fake-model-2026-01-01",
        "choices": [{"message": {"content": content},
                     "finish_reason": "stop"}],
        "usage": USAGE,
    })


@pytest.fixture
def hosted(monkeypatch, tmp_path):
    """A HostedOpenAIClient on a fake rate table and a tmp ledger."""
    rates = tmp_path / "rates.yaml"
    rates.write_text("fake-model: {input_per_1m: 1.0, output_per_1m: 2.0, "
                     "cached_input_per_1m: 0.1}\n")
    monkeypatch.setenv("HOSTED_RATES_YAML", str(rates))
    monkeypatch.setenv("HOSTED_SPEND_CAP", "5.0")
    monkeypatch.setenv("HOSTED_SPEND_LEDGER", str(tmp_path / "ledger.json"))
    return llm_client.HostedOpenAIClient("https://api.openai.com",
                                         "fake-model")


def test_hosted_body_dialect(hosted, monkeypatch):
    """max_completion_tokens (not max_tokens), no chat_template_kwargs,
    reasoning_effort none (renamed minimum), strict transformed schema."""
    bodies = []
    monkeypatch.setattr(
        requests, "post",
        lambda url, json=None, **kw: (bodies.append(json),
                                      ok_response())[1])
    hosted.generate("sys", "usr", SCHEMA, seed=42, temperature=0.7)
    body = bodies[0]
    assert "chat_template_kwargs" not in body
    assert "max_tokens" not in body
    assert body["temperature"] == 0.7   # probed accepted; passes through
    assert body["max_completion_tokens"] == 4096
    assert body["reasoning_effort"] == "none"    # the API's renamed minimum
    js = body["response_format"]["json_schema"]
    assert js["strict"] is True
    # the guided schema went through to_hosted_schema: the optional
    # property is now required-but-nullable
    assert set(js["schema"]["required"]) == {"a", "opt"}
    assert js["schema"]["properties"]["opt"]["type"] == ["integer", "null"]


def test_vllm_body_byte_identical(monkeypatch):
    """The golden body: exactly what OpenAIHTTPClient.generate has always
    sent (values AND key order). Any drift here is a regression of the
    'vLLM path byte-identical' guarantee."""
    client = llm_client.OpenAIHTTPClient("http://127.0.0.1:8300", "m")
    captured = {}

    def fake_post(url, json=None, timeout=None, **kw):
        captured["body"] = json
        return type("R", (), {"raise_for_status": lambda s: None,
                              "json": lambda s: ok_response().json()})()

    monkeypatch.setattr(requests, "post", fake_post)
    client.generate("s", "u", SCHEMA, seed=42, temperature=0.7)
    golden = {
        "model": "m",
        "messages": [{"role": "system", "content": "s"},
                     {"role": "user", "content": "u"}],
        "temperature": 0.7,
        "max_tokens": 4096,
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "generation", "schema": SCHEMA},
        },
        "chat_template_kwargs": {"enable_thinking": False},
        "seed": 42,
    }
    assert captured["body"] == golden
    assert list(captured["body"].keys()) == list(golden.keys())


def test_auth_header_iff_key_set_and_never_in_logs(hosted, monkeypatch,
                                                   caplog):
    sent_headers = []

    def fake_post(url, json=None, headers=None, **kw):
        sent_headers.append(dict(headers or {}))
        return ok_response()

    monkeypatch.setattr(requests, "post", fake_post)
    key = "sk-test-NEVER-LOG-ME"
    monkeypatch.setenv("OPENAI_API_KEY", key)
    hosted.generate("s", "u", SCHEMA, seed=1)
    assert sent_headers[-1]["Authorization"] == f"Bearer {key}"
    monkeypatch.delenv("OPENAI_API_KEY")
    hosted.generate("s", "u", SCHEMA, seed=2)
    assert "Authorization" not in sent_headers[-1]
    # ...and the key reaches no log line and no exception text, even
    # through a retried 429 and a fail-fast 400
    monkeypatch.setenv("OPENAI_API_KEY", key)
    monkeypatch.setattr(llm_client.time, "sleep", lambda s: None)
    responses = iter([FakeResp(429, headers={"Retry-After": "1"}),
                      FakeResp(400, text='{"error": "bad request"}')])
    monkeypatch.setattr(requests, "post", lambda *a, **kw: next(responses))
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(RuntimeError) as exc:
            hosted._post_chat({"model": "fake-model", "messages": []})
    assert key not in str(exc.value)
    assert all(key not in r.getMessage() for r in caplog.records)


def test_429_retried_with_backoff_400_not(hosted, monkeypatch):
    sleeps, calls = [], []
    monkeypatch.setattr(llm_client.time, "sleep",
                        lambda s: sleeps.append(s))
    responses = iter([FakeResp(429, headers={"Retry-After": "7"}),
                      FakeResp(503),
                      ok_response()])
    monkeypatch.setattr(
        requests, "post",
        lambda *a, **kw: (calls.append(1), next(responses))[1])
    data = hosted._post_chat({"model": "fake-model", "messages": []})
    assert data["choices"][0]["message"]["content"] == '{"a": "x"}'
    assert len(calls) == 3
    assert sleeps and sleeps[0] >= 7            # Retry-After honored
    # 400 is a request bug: one attempt, fail fast
    calls.clear()
    monkeypatch.setattr(
        requests, "post",
        lambda *a, **kw: (calls.append(1),
                          FakeResp(400, text="schema rejected"))[1])
    with pytest.raises(RuntimeError, match="hosted API 400"):
        hosted._post_chat({"model": "fake-model", "messages": []})
    assert len(calls) == 1


def test_spend_guard_aborts_at_cap(tmp_path):
    """Fake rate table + canned usage blocks: the crossing call is still
    recorded (its tokens were spent), then everything aborts — including
    the preflight of any later call, from any process on this ledger."""
    ledger = tmp_path / "l.json"
    guard = SpendGuard(RATES, cap_usd=0.005, ledger_path=ledger)
    # canned usage: 1000 in @ $1/M + 500 out @ $2/M = $0.002/call
    assert guard.charge("fake-model-2026-01-01", USAGE) == \
        pytest.approx(0.002)
    guard.charge("fake-model", USAGE)                    # total 0.004
    with pytest.raises(SpendCapExceeded, match="crossed"):
        guard.charge("fake-model", USAGE)                # 0.006 > cap
    other_process = SpendGuard(RATES, 0.005, ledger)
    assert other_process.spent() == pytest.approx(0.006)
    with pytest.raises(SpendCapExceeded, match="before the call"):
        other_process.preflight()
