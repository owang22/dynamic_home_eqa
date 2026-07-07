"""
Tests for llm_prior/http_client.py — mocks requests.post so these never
make a real HTTP call or require a running server, per this project's
"no live LLM calls in pytest" rule (an HTTP call to a local vLLM server
is still a live call for this purpose).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from dynamic_home_eqa.llm_prior.client import ModelSpec
from dynamic_home_eqa.llm_prior.http_client import HTTPLLMClient, HTTPModelSpec, from_model_spec

_SPEC = ModelSpec(model_id="test/model", family="test", provider="local-vllm", quantization="awq", is_generator_family=False)


class TestFromModelSpec:
    def test_accepts_loopback_127(self):
        result = from_model_spec(_SPEC, "http://127.0.0.1:8000/v1")
        assert result.base_url == "http://127.0.0.1:8000/v1"
        assert result.model_id == _SPEC.model_id

    def test_accepts_localhost(self):
        result = from_model_spec(_SPEC, "http://localhost:8000/v1")
        assert result.base_url == "http://localhost:8000/v1"

    def test_rejects_non_loopback_host(self):
        with pytest.raises(ValueError, match="loopback"):
            from_model_spec(_SPEC, "http://0.0.0.0:8000/v1")

    def test_rejects_external_host(self):
        with pytest.raises(ValueError, match="loopback"):
            from_model_spec(_SPEC, "http://192.168.1.5:8000/v1")


def _fake_response(token="A", logprob=-0.1, extra=(("B", -8.0),)):
    top_logprobs = [{"token": token, "logprob": logprob, "bytes": [ord(token)]}]
    for t, lp in extra:
        top_logprobs.append({"token": t, "logprob": lp, "bytes": [ord(t)]})
    payload = {
        "choices": [{
            "message": {"content": token},
            "logprobs": {"content": [{"token": token, "logprob": logprob, "top_logprobs": top_logprobs}]},
        }],
    }
    mock_resp = MagicMock()
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status.return_value = None
    return mock_resp


class TestHTTPLLMClientMcqLogprob:
    def test_parses_top_logprobs_into_expected_shape(self):
        spec = HTTPModelSpec(model_id="m", family="f", provider="p", quantization="q", is_generator_family=False, base_url="http://127.0.0.1:8000/v1")
        client = HTTPLLMClient(spec)
        with patch("dynamic_home_eqa.llm_prior.http_client.requests.post", return_value=_fake_response()) as mock_post:
            result = client.mcq_logprob("system", "user", ("A", "B"), seed=0)
        assert result["top_logprobs"]["A"] == pytest.approx(-0.1)
        assert result["top_logprobs"]["B"] == pytest.approx(-8.0)
        assert result["greedy_text"] == "A"
        mock_post.assert_called_once()

    def test_posts_to_correct_endpoint_with_expected_params(self):
        spec = HTTPModelSpec(model_id="my-model", family="f", provider="p", quantization="q", is_generator_family=False, base_url="http://127.0.0.1:9999/v1")
        client = HTTPLLMClient(spec)
        with patch("dynamic_home_eqa.llm_prior.http_client.requests.post", return_value=_fake_response()) as mock_post:
            client.mcq_logprob("sys", "usr", ("A", "B"), seed=7)
        args, kwargs = mock_post.call_args
        assert args[0] == "http://127.0.0.1:9999/v1/chat/completions"
        body = kwargs["json"]
        assert body["model"] == "my-model"
        assert body["max_tokens"] == 1
        assert body["temperature"] == 0.0
        assert body["seed"] == 7
        assert body["logprobs"] is True
        assert body["messages"][0] == {"role": "system", "content": "sys"}
        assert body["messages"][1] == {"role": "user", "content": "usr"}
        # Qwen3 thinking-mode bug (L0) applies identically here — must be
        # disabled on every request, not just the in-process client.
        assert body["chat_template_kwargs"] == {"enable_thinking": False}

    def test_raises_on_http_error(self):
        spec = HTTPModelSpec(model_id="m", family="f", provider="p", quantization="q", is_generator_family=False, base_url="http://127.0.0.1:8000/v1")
        client = HTTPLLMClient(spec)
        error_resp = MagicMock()
        error_resp.raise_for_status.side_effect = Exception("500 error")
        with patch("dynamic_home_eqa.llm_prior.http_client.requests.post", return_value=error_resp):
            with pytest.raises(Exception, match="500 error"):
                client.mcq_logprob("s", "u", ("A", "B"), seed=0)
