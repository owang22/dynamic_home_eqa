"""Served-LLM glue for the STAR memory loop: HTTP + prompt cache.

The loop is sequential -- each step's prompt depends on the previous
outcome -- so the collect-then-batch PromptCache pattern of
``beliefs/llm_belief.py`` does not apply (and is deliberately not
copied). Instead the model runs in vLLM SERVER mode and every step is
one HTTP chat call through the existing generation client
(:class:`dynamic_home_eqa.generation.llm_client.OpenAIHTTPClient`:
loopback endpoint, structured JSON via ``response_format``, per-request
seed, transient-failure retries; no vllm import, no GPU claim here).

Completions are cached on disk keyed by a hash of the FULL request
(model, system, user, schema, seed, sampling), so a rerun of the same
subset costs nothing; the hit rate is reported into the run's
provenance. Cache entries also carry the server's token usage, summed
for the findings' token accounting.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import time
from typing import Any, Dict, Optional, Tuple

from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient

DEFAULT_MAX_TOKENS = 128
"""One action object is tiny; this bounds a runaway completion."""

THROTTLE_ENV = "STAR_LLM_THROTTLE_S"
"""Seconds slept after every UNCACHED call (float; unset/0 = none).
A GPU duty-cycle brake for thermally constrained boxes -- the only
power lever available without root; cache hits never sleep."""


class _UsageClient(OpenAIHTTPClient):
    """The generation client, plus a variant of ``generate`` that also
    returns the server's usage block (the base method discards it)."""

    def generate_with_usage(
            self, system: str, user: str, schema: Dict[str, Any],
            seed: Optional[int], temperature: float,
            max_tokens: int) -> Tuple[str, Dict[str, int]]:
        body: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "star_action", "schema": schema},
            },
            "chat_template_kwargs": {"enable_thinking": False},
        }
        if seed is not None:
            body["seed"] = seed & 0x7FFFFFFFFFFFFFFF
        data = self._post_chat(self._adapt_body(body))
        text = (data["choices"][0]["message"].get("content") or "").strip()
        usage = data.get("usage") or {}
        return text, {
            "prompt_tokens": int(usage.get("prompt_tokens", 0)),
            "completion_tokens": int(usage.get("completion_tokens", 0)),
        }


class CachedStructuredClient:
    """Guided-JSON chat calls against a served model, disk-cached.

    The cache file is JSONL, one ``{"key", "text", "usage"}`` line per
    completed request, loaded fully at construction and appended on
    every miss -- append-only, so concurrent readers of a finished run
    see a consistent file. ``generate`` matches the loop's
    :data:`~baselines.policies.star_memory_loop.GenerateFn` signature.
    """

    def __init__(self, endpoint: str, model: str,
                 cache_path: pathlib.Path, temperature: float = 0.0,
                 max_tokens: int = DEFAULT_MAX_TOKENS,
                 timeout: float = 600.0) -> None:
        self._client = _UsageClient(endpoint, model, timeout=timeout)
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._cache_path = cache_path
        self._cache: Dict[str, str] = {}
        self.hits = 0
        self.misses = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        if cache_path.exists():
            with cache_path.open() as fh:
                for line in fh:
                    if line.strip():
                        row = json.loads(line)
                        self._cache[str(row["key"])] = str(row["text"])
        else:
            cache_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def model(self) -> str:
        return self._client.model

    @property
    def endpoint(self) -> str:
        return str(self._client.base)

    def cache_stats(self) -> Dict[str, Any]:
        return {"hits": self.hits, "misses": self.misses,
                "hit_rate": (self.hits / (self.hits + self.misses)
                             if self.hits + self.misses else 0.0),
                "new_prompt_tokens": self.prompt_tokens,
                "new_completion_tokens": self.completion_tokens,
                "cache_path": str(self._cache_path),
                "entries": len(self._cache)}

    def _key(self, system: str, user: str, schema: Dict[str, Any],
             seed: int) -> str:
        payload = json.dumps(
            {"model": self._client.model, "system": system, "user": user,
             "schema": schema, "seed": seed,
             "temperature": self._temperature,
             "max_tokens": self._max_tokens},
            sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def generate(self, system: str, user: str, schema: Dict[str, Any],
                 seed: int) -> str:
        key = self._key(system, user, schema, seed)
        cached = self._cache.get(key)
        if cached is not None:
            self.hits += 1
            return cached
        self.misses += 1
        text, usage = self._client.generate_with_usage(
            system, user, schema, seed, self._temperature,
            self._max_tokens)
        throttle = float(os.environ.get(THROTTLE_ENV, "0") or "0")
        if throttle > 0:
            time.sleep(throttle)
        self.prompt_tokens += usage["prompt_tokens"]
        self.completion_tokens += usage["completion_tokens"]
        self._cache[key] = text
        with self._cache_path.open("a") as fh:
            fh.write(json.dumps({"key": key, "text": text,
                                 "usage": usage}) + "\n")
        return text


def server_provenance(endpoint: str) -> Dict[str, Any]:
    """Best-effort identity of the serving process: vLLM version and the
    served model list, for the run's provenance file. Failures are
    recorded, never raised -- provenance must not kill a finished run."""
    import requests
    out: Dict[str, Any] = {"endpoint": endpoint}
    base = endpoint.rstrip("/")
    for label, path in (("version", "/version"), ("models", "/v1/models")):
        try:
            response = requests.get(f"{base}{path}", timeout=10)
            response.raise_for_status()
            out[label] = response.json()
        except Exception as err:  # noqa: BLE001 - best-effort probe
            out[label] = f"unavailable: {err}"
    return out
