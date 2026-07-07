"""
Tests for llm_prior/cache.py's EliciationCache — pure disk I/O, no model
calls. This is the cache that makes L0's "no live LLM calls in pytest"
rule enforceable: everything scoring/elicit reads comes back through
this class, never a fresh model call.
"""
from __future__ import annotations

from dynamic_home_eqa.llm_prior.cache import EliciationCache, cache_key


class TestCacheKey:
    def test_deterministic(self):
        assert cache_key("m", "p", "mcq_logprob", 0) == cache_key("m", "p", "mcq_logprob", 0)

    def test_differs_by_each_component(self):
        base = cache_key("model-a", "hash1", "mcq_logprob", 0)
        assert base != cache_key("model-b", "hash1", "mcq_logprob", 0)
        assert base != cache_key("model-a", "hash2", "mcq_logprob", 0)
        assert base != cache_key("model-a", "hash1", "verbalized", 0)
        assert base != cache_key("model-a", "hash1", "mcq_logprob", 1)


class TestEliciationCache:
    def test_miss_returns_none(self, tmp_path):
        cache = EliciationCache(tmp_path)
        assert cache.get("m", "p", "mcq_logprob", 0) is None
        assert not cache.has("m", "p", "mcq_logprob", 0)

    def test_put_then_get_roundtrips(self, tmp_path):
        cache = EliciationCache(tmp_path)
        cache.put("m", "p", "mcq_logprob", 0, prompt="hello", raw_response={"top_logprobs": {"A": -0.1}})
        assert cache.has("m", "p", "mcq_logprob", 0)
        entry = cache.get("m", "p", "mcq_logprob", 0)
        assert entry["model_id"] == "m"
        assert entry["prompt_hash"] == "p"
        assert entry["mode"] == "mcq_logprob"
        assert entry["seed"] == 0
        assert entry["prompt"] == "hello"
        assert entry["raw_response"] == {"top_logprobs": {"A": -0.1}}

    def test_distinct_keys_do_not_collide_on_disk(self, tmp_path):
        cache = EliciationCache(tmp_path)
        cache.put("m", "p", "mcq_logprob", 0, prompt="x", raw_response="first")
        cache.put("m", "p", "verbalized", 0, prompt="x", raw_response="second")
        assert cache.get("m", "p", "mcq_logprob", 0)["raw_response"] == "first"
        assert cache.get("m", "p", "verbalized", 0)["raw_response"] == "second"
