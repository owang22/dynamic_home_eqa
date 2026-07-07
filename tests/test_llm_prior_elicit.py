"""
Tests for llm_prior/elicit.py's caching orchestration (_elicit_location,
_elicit_dynamics) — a fake client stands in for LLMPriorClient so these
never touch vLLM or the network, per L0's "no live LLM calls in pytest"
rule. What's tested here is the CACHING logic (call once, reuse on a
second pass) and prompt-hash wiring, not model quality.
"""
from __future__ import annotations

from dataclasses import dataclass

from dynamic_home_eqa.llm_prior.cache import EliciationCache
from dynamic_home_eqa.llm_prior.client import ModelSpec
from dynamic_home_eqa.llm_prior.elicit import _elicit_dynamics, _elicit_location
from dynamic_home_eqa.llm_prior.targets import ElicitationTarget


@dataclass
class _FakeClient:
    spec: ModelSpec
    calls: list = None

    def __post_init__(self):
        self.calls = []

    def mcq_logprob(self, system, user, option_letters, seed):
        self.calls.append(("mcq_logprob", user))
        return {"top_logprobs": {letter: -0.1 * i for i, letter in enumerate(option_letters)}, "greedy_text": option_letters[0]}

    def verbalized(self, system, user, seed):
        self.calls.append(("verbalized", user))
        return '{"stay_probability": 0.5}'

    def sample_count(self, system, user, option_letters, k, seed):
        self.calls.append(("sample_count", user))
        return {letter: k // len(option_letters) for letter in option_letters}


_SPEC = ModelSpec(model_id="fake/model", family="fake", provider="test", quantization="none", is_generator_family=False)


def _target(axis="location", key="book", time_bin=1, support=("shelf", "table", "OUTSIDE")):
    return ElicitationTarget(axis=axis, key=key, time_bin=time_bin, support=support, scene="s", profile="p")


class TestElicitLocationCaching:
    def test_calls_model_once_per_mode_on_first_pass(self, tmp_path):
        client = _FakeClient(_SPEC)
        cache = EliciationCache(tmp_path)
        _elicit_location(client, cache, _target(), "persona text", "room text")
        modes_called = [c[0] for c in client.calls]
        assert sorted(modes_called) == ["mcq_logprob", "sample_count", "verbalized"]

    def test_second_pass_hits_cache_not_model(self, tmp_path):
        client = _FakeClient(_SPEC)
        cache = EliciationCache(tmp_path)
        _elicit_location(client, cache, _target(), "persona text", "room text")
        n_calls_after_first = len(client.calls)
        _elicit_location(client, cache, _target(), "persona text", "room text")
        assert len(client.calls) == n_calls_after_first  # no new calls

    def test_returns_option_letters_matching_support_length(self, tmp_path):
        client = _FakeClient(_SPEC)
        cache = EliciationCache(tmp_path)
        result = _elicit_location(client, cache, _target(), "persona text", "room text")
        assert len(result["option_letters"]) == 3

    def test_different_targets_produce_different_hashes(self, tmp_path):
        client = _FakeClient(_SPEC)
        cache = EliciationCache(tmp_path)
        r1 = _elicit_location(client, cache, _target(key="book"), "persona text", "room text")
        r2 = _elicit_location(client, cache, _target(key="candle"), "persona text", "room text")
        assert r1["mcq_logprob"] != r2["mcq_logprob"]


class TestElicitDynamicsCaching:
    def test_calls_model_once_per_mode(self, tmp_path):
        client = _FakeClient(_SPEC)
        cache = EliciationCache(tmp_path)
        _elicit_dynamics(client, cache, _target(axis="state", key="fridge::door", support=("closed", "open")), "p", "r")
        modes_called = [c[0] for c in client.calls]
        assert sorted(modes_called) == ["mcq_logprob", "sample_count", "verbalized"]

    def test_state_and_location_axis_use_different_wording(self, tmp_path):
        client = _FakeClient(_SPEC)
        cache = EliciationCache(tmp_path)
        loc = _elicit_dynamics(client, cache, _target(axis="location"), "p", "r")
        state = _elicit_dynamics(client, cache, _target(axis="state", key="fridge::door"), "p", "r")
        assert loc["mcq_logprob"] != state["mcq_logprob"]
