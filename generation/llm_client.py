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

DEFAULT_MODEL       = os.environ.get("GENERATION_MODEL", "Qwen/Qwen3-14B-Instruct")
_MODEL_CACHE        = "/mnt/nvme/oliver/robot/models"
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
        # Keyed by schema id only — StructuredOutputsParams involves grammar
        # compilation, worth caching per schema. seed varies per call (see
        # generate()) and is cheap to rebuild SamplingParams around each time,
        # so it deliberately isn't part of this cache key.
        self._structured_cache: dict = {}

    def _load(self) -> None:
        import os as _os
        _os.environ.setdefault("HF_HOME", _MODEL_CACHE)
        from vllm import LLM
        self._llm = LLM(model=self.model, disable_log_stats=True)

    def _structured_outputs(self, schema: dict):
        key = id(schema)
        if key not in self._structured_cache:
            from vllm.sampling_params import StructuredOutputsParams
            self._structured_cache[key] = StructuredOutputsParams(json=schema)
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
            structured_outputs=self._structured_outputs(schema),
        )
        conv = [
            {"role": "system",  "content": system},
            {"role": "user",    "content": user},
        ]
        out = self._llm.chat([conv], sampling_params=params)
        return out[0].outputs[0].text.strip()


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
