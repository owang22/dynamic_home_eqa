"""
Shared lazy-loaded vLLM client used by every generation stage (persona,
activity trace, displacement, realism judge, conflict verification).

Split out from stages.py so the persona/ package doesn't have to import from
stages.py (which owns the non-persona stages) just to get the client — both
sides import this module instead, with no dependency between them.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Callable, Optional

from .cache import ResponseCache

# Qwen/Qwen3-32B lives in the standard HF cache (whatever HF_HOME resolves
# to) — no special-cased model directory.
DEFAULT_MODEL       = os.environ.get("GENERATION_MODEL", "Qwen/Qwen3-32B")
DEFAULT_CACHE_DIR   = "/tmp/dynamic-home-eqa-gen-cache"
DEFAULT_TEMPERATURE = 0.7
MAX_RETRIES         = 3

_logger = logging.getLogger(__name__)


class _LLMClient:
    """Thin wrapper around vLLM for guided JSON generation."""

    def __init__(self, model: str, temperature: float) -> None:
        self.model       = model
        self.temperature = temperature
        self._llm        = None
        # Keyed by schema id only — GuidedDecodingParams involves grammar
        # compilation, worth caching per schema. seed varies per call (see
        # generate()) and is cheap to rebuild SamplingParams around each time,
        # so it deliberately isn't part of this cache key.
        #
        # GuidedDecodingParams (not StructuredOutputsParams) and
        # SamplingParams(guided_decoding=...) (not structured_outputs=...):
        # this project targets vllm==0.10.2 (see dynamic_eqa env setup) —
        # StructuredOutputsParams/structured_outputs= is a later vllm
        # rename (0.11.x+) that this version doesn't have.
        self._structured_cache: dict = {}

    def _load(self) -> None:
        # No forced HF_HOME override (previously hardcoded to
        # /mnt/nvme/oliver/robot/models) — standard huggingface_hub
        # resolution now, same cache every other tool on this machine
        # already uses (~/.cache/huggingface/hub unless the shell's own
        # HF_HOME says otherwise). A caller that specifically needs a
        # model from the old /mnt/nvme cache can still set HF_HOME itself
        # before invoking this.
        from vllm import LLM
        self._llm = LLM(model=self.model, disable_log_stats=True)

    def _structured_outputs(self, schema: dict):
        key = id(schema)
        if key not in self._structured_cache:
            from vllm.sampling_params import GuidedDecodingParams
            self._structured_cache[key] = GuidedDecodingParams(json=schema)
        return self._structured_cache[key]

    def generate(self, system: str, user: str, schema: dict, seed: Optional[int] = None) -> str:
        if self._llm is None:
            self._load()
        from vllm import SamplingParams
        params = SamplingParams(
            temperature=self.temperature,
            # 1024 was tight enough that a 4-occupant persona (each now
            # requiring a required free-text `habits` field) truncated
            # mid-string and failed all MAX_RETRIES with a JSONDecodeError
            # — verified via a real run, not a hypothetical margin.
            max_tokens=2048,
            seed=seed,
            guided_decoding=self._structured_outputs(schema),
        )
        conv = [
            {"role": "system",  "content": system},
            {"role": "user",    "content": user},
        ]
        out = self._llm.chat([conv], sampling_params=params)
        return out[0].outputs[0].text.strip()

    def generate_thinking(self, system: str, user: str, seed: Optional[int] = None,
                           temperature: float = 0.6, max_tokens: int = 8192) -> tuple[str, str]:
        """Thinking-mode call (LLM Option Evaluation round, Arm 1): Qwen3
        chat-template thinking enabled, NO guided decoding — measured
        directly (results/reports/llm_comparison/thinking_vs_moe.md) that
        the JSON grammar suppresses the think block outright, so the two
        cannot be combined on this vLLM version. Returns (payload, think):
        payload is the text after the </think> block with any markdown
        code fence stripped (the same real failure modes the comparison
        run hit), think is the raw reasoning trace.

        Only safe for stages whose output carries no vocabulary claims —
        the judge (scores only). The comparison run showed the proposer
        hallucinates census labels without the grammar; do not wire this
        into a proposal-emitting stage.

        temperature defaults to 0.6 (Qwen3's own recommended thinking-
        mode setting; near-greedy values are documented by the model card
        to cause degenerate repetition in long think blocks — deliberately
        NOT the 0.0-0.2 a non-thinking judge would use)."""
        if self._llm is None:
            self._load()
        import re

        from vllm import SamplingParams
        params = SamplingParams(temperature=temperature, top_p=0.95, max_tokens=max_tokens, seed=seed)
        conv = [
            {"role": "system",  "content": system},
            {"role": "user",    "content": user},
        ]
        out = self._llm.chat([conv], sampling_params=params,
                              chat_template_kwargs={"enable_thinking": True})
        text = out[0].outputs[0].text
        think = ""
        payload = text
        if "</think>" in text:
            think, payload = text.rsplit("</think>", 1)
            think = think.replace("<think>", "").strip()
        fence = re.search(r"```(?:json)?\s*(.*?)```", payload, re.S)
        if fence:
            payload = fence.group(1)
        return payload.strip(), think


_client: Optional[_LLMClient] = None


def _get_client(model: str, temperature: float) -> _LLMClient:
    global _client
    if _client is None or _client.model != model:
        _client = _LLMClient(model, temperature)
    return _client


def generate_json(
    client: _LLMClient,
    system: str,
    user: str,
    schema: dict,
    *,
    seed: int,
    stage: str,
    cache: Optional[ResponseCache] = None,
    force: bool = False,
    max_retries: int = MAX_RETRIES,
    validate: Callable[[dict], Any] = lambda result: result,
) -> Any:
    """Get one guided-JSON response from the LLM: cache, retry, and failure
    logging in one path shared by every generation stage, instead of five
    near-identical copies of the same loop.

    validate(parsed_json) -> whatever the caller actually wants back (e.g.
    unwrapping a nested structure); raise KeyError/ValueError from it to
    trigger a retry the same as a JSON parse failure. Applied uniformly to
    cache hits and fresh generations, so a call site doesn't need a second
    copy of its own post-processing for the cache-hit path.

    Two things this fixes relative to the old per-stage loops:
      - Every failed attempt's raw output is logged (not silently discarded)
        before retrying. A JSON-parse failure under guided decoding is much
        more likely a schema-satisfaction edge case than one-off noise, and
        that's exactly the signal you can't reconstruct after the fact in a
        500-scene batch run.
      - Each retry passes an explicit, distinct seed (seed + attempt) to the
        sampler, so a retry is guaranteed to actually resample rather than
        repeat the identical call and (depending on decoder internals)
        reproduce the same malformed output.
    """
    if cache and not force:
        raw = cache.get(seed)
        if raw is not None:
            return validate(json.loads(raw))

    last_err: Exception = RuntimeError(f"generate_json: max_retries={max_retries} is not positive")
    for attempt in range(max_retries):
        raw = client.generate(system, user, schema, seed=seed + attempt)
        try:
            result = validate(json.loads(raw))
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            last_err = e
            _logger.warning(
                "[%s] guided-JSON failure on attempt %d/%d (seed=%d): %s\nRaw output: %r",
                stage, attempt + 1, max_retries, seed + attempt, e, raw,
            )
            continue
        if cache:
            cache.put(seed, user, raw)
        return result
    raise last_err


def generate_json_thinking(
    client: _LLMClient,
    system: str,
    user: str,
    *,
    seed: int,
    stage: str,
    cache: Optional[ResponseCache] = None,
    force: bool = False,
    max_retries: int = MAX_RETRIES,
    validate: Callable[[dict], Any] = lambda result: result,
    temperature: float = 0.6,
    max_tokens: int = 8192,
) -> Any:
    """Thinking-mode sibling of generate_json (LLM Option Evaluation
    round): same cache/retry/validate contract, but no schema (no guided
    decoding is possible with a think block on this vLLM version — see
    _LLMClient.generate_thinking), so `validate` carries the full burden
    of shape checking/normalizing, and callers should expect drifted
    shapes (measured: fenced JSON, renamed keys, flat dicts instead of
    arrays). The cached `raw` is the post-think, post-fence payload —
    directly json-parseable on cache hits, same contract as
    generate_json; the reasoning trace is stored alongside (truncated)
    for eval review."""
    if cache and not force:
        raw = cache.get(seed)
        if raw is not None:
            return validate(json.loads(raw))

    last_err: Exception = RuntimeError(f"generate_json_thinking: max_retries={max_retries} is not positive")
    for attempt in range(max_retries):
        payload, think = client.generate_thinking(
            system, user, seed=seed + attempt, temperature=temperature, max_tokens=max_tokens,
        )
        try:
            result = validate(json.loads(payload))
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            last_err = e
            _logger.warning(
                "[%s] thinking-JSON failure on attempt %d/%d (seed=%d): %s\nPayload: %r",
                stage, attempt + 1, max_retries, seed + attempt, e, payload[:500],
            )
            continue
        if cache:
            cache.put(seed, user, payload, think=think[:2000])
        return result
    raise last_err
