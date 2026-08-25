"""
Shared lazy-loaded LLM client used by every generation stage (persona,
activity trace, displacement, realism judge, conflict verification).

Two backends, selected by the GENERATION_ENDPOINT env var:

  unset (default) — in-process vLLM (_LLMClient). The original path; loads
                    the model into this process's GPUs. Tests monkeypatch
                    _LLMClient.generate/generate_thinking, so this stays the
                    default.
  set             — OpenAI-compatible HTTP server (OpenAIHTTPClient), e.g.
                    "http://127.0.0.1:8300". The model is served out of
                    process (scripts/serve_llm.py) and this env only needs
                    `requests` — no vllm/torch import, no GPU claim. Guided
                    JSON goes through the server's response_format
                    json_schema structured-outputs path; determinism via the
                    request `seed` field, same seeds as in-process.

Split out from stages.py so the persona/ package doesn't have to import from
stages.py (which owns the non-persona stages) just to get the client — both
sides import this module instead, with no dependency between them.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from typing import Any, Callable, Optional

from .cache import ResponseCache
from .http_judge import HTTPThinkingClient

# Qwen/Qwen3-32B lives in the standard HF cache (whatever HF_HOME resolves
# to) — no special-cased model directory.
DEFAULT_MODEL       = os.environ.get("GENERATION_MODEL", "Qwen/Qwen3-32B")
DEFAULT_CACHE_DIR   = "/tmp/dynamic-home-eqa-gen-cache"


def model_slug(model: str) -> str:
    """Short filesystem/label-safe identifier for a model string —
    "casperhansen/llama-3.3-70b-instruct-awq" -> "llama-3.3-70b-instruct-awq",
    "Qwen/Qwen3-32B" -> "qwen3-32b". Used to label per-model output folders
    and cache dirs: the response cache is keyed by seed alone (never by
    model), so two models sharing a cache dir would silently replay each
    other's responses — every non-default model MUST get its own cache dir
    (see scripts/regenerate_comparison_set.py)."""
    return model.rsplit("/", 1)[-1].lower().replace("_", "-")
DEFAULT_TEMPERATURE = 0.7
MAX_RETRIES         = 3

_logger = logging.getLogger(__name__)


class _LLMClient:
    """Thin wrapper around vLLM for guided JSON generation.

    Deliberately holds NO sampling state: temperature is a per-call
    SamplingParams argument, never client identity — a singleton client
    that baked in the first caller's temperature silently ignored every
    later stage's own value."""

    def __init__(self, model: str) -> None:
        self.model = model
        self._llm  = None
        # Keyed by a content hash of the schema — GuidedDecodingParams
        # involves grammar compilation, worth caching per schema. id()
        # keying was wrong: two structurally identical schemas built at
        # different call sites missed the cache, and a recycled id could
        # in principle serve the wrong grammar. seed/temperature vary per
        # call and are cheap to rebuild SamplingParams around, so they
        # deliberately aren't part of this key.
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
        key = hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest()
        if key not in self._structured_cache:
            from vllm.sampling_params import GuidedDecodingParams
            self._structured_cache[key] = GuidedDecodingParams(json=schema)
        return self._structured_cache[key]

    def generate(self, system: str, user: str, schema: dict, seed: Optional[int] = None,
                 temperature: float = DEFAULT_TEMPERATURE) -> str:
        if self._llm is None:
            self._load()
        from vllm import SamplingParams
        params = SamplingParams(
            temperature=temperature,
            # 1024 was tight enough that a 4-occupant persona (each now
            # requiring a required free-text `habits` field) truncated
            # mid-string and failed all MAX_RETRIES with a JSONDecodeError
            # — verified via a real run, not a hypothetical margin.
            # 2048 -> 4096: same failure mode again with Qwen3.6-35B-A3B,
            # whose displacement responses run much wordier than Qwen3-32B's
            # — a real displacement_ctx call truncated mid-string on all 3
            # attempts (Unterminated string) and cost the scene.
            max_tokens=4096,
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


class OpenAIHTTPClient(HTTPThinkingClient):
    """OpenAI-compatible chat-completions client for an out-of-process
    served model (vLLM's api_server — see scripts/serve_llm.py).

    Duck-types _LLMClient: generate() (guided JSON) and generate_thinking()
    (inherited from HTTPThinkingClient, the judge-proven implementation),
    so every stage can use it wherever it would use the in-process client.

    Guided decoding rides the server's structured-outputs path via the
    standard response_format={"type": "json_schema", ...} field — the HTTP
    equivalent of SamplingParams(guided_decoding=GuidedDecodingParams(json=
    schema)), and unlike that 0.10.2-era kwarg it survives newer vLLMs
    (the whole point of serving out of process — see http_judge.py).

    enable_thinking=False is passed explicitly on the guided path: in
    process, the JSON grammar suppressed a hybrid Qwen3 model's think block
    as a side effect (see generate_thinking's docstring); over HTTP the
    template kwarg is the documented way to get the same
    straight-to-payload behavior, and templates that don't know the kwarg
    (Llama etc.) simply ignore it.
    """

    # Capability flag: False = a served vLLM endpoint (loopback, unmetered,
    # vLLM-dialect request body). HostedOpenAIClient flips it. Call sites
    # branch on THIS, never on URL string matching.
    hosted = False

    # Transient-failure retries live HERE, not in generate_json's loop:
    # that loop treats a failure as "resample with seed+attempt", which is
    # the wrong medicine for a connection blip (and generate_json doesn't
    # catch requests exceptions anyway — a dead server should abort the
    # scene loudly, not burn MAX_RETRIES reseeding into the void).
    _HTTP_RETRIES = 3

    def _adapt_body(self, body: dict) -> dict:
        """Backend-dialect hook: identity for vLLM (the request body stays
        byte-identical to what this client always sent), overridden by
        HostedOpenAIClient to speak api.openai.com's dialect."""
        return body

    def _post_chat(self, body: dict) -> dict:
        import requests
        last_err: Exception = RuntimeError("unreachable")
        for attempt in range(self._HTTP_RETRIES):
            try:
                resp = requests.post(f"{self.base}/v1/chat/completions",
                                     json=body, timeout=self.timeout)
                resp.raise_for_status()
                return resp.json()
            except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as e:
                status = getattr(getattr(e, "response", None), "status_code", None)
                if status is not None and status < 500:
                    raise  # 4xx is a real request bug, never transient
                last_err = e
                _logger.warning("HTTP LLM call failed (attempt %d/%d): %s",
                                attempt + 1, self._HTTP_RETRIES, e)
                time.sleep(2.0 * (attempt + 1))
        raise last_err

    def generate(self, system: str, user: str, schema: dict, seed: Optional[int] = None,
                 temperature: float = DEFAULT_TEMPERATURE, max_tokens: int = 4096) -> str:
        # max_tokens: callers with long prompts must shrink this — vLLM rejects
        # requests where prompt + max_tokens exceeds --max-model-len (the failure
        # mode that silently zeroed the long-digest llm_nomem arm).
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "generation", "schema": schema},
            },
            "chat_template_kwargs": {"enable_thinking": False},
        }
        if seed is not None:
            # make_seed returns an unsigned 64-bit int; the OpenAI API
            # validates seed as signed int64 — mask to 63 bits (same as
            # HTTPThinkingClient.generate_thinking).
            body["seed"] = seed & 0x7FFFFFFFFFFFFFFF
        data = self._post_chat(self._adapt_body(body))
        return (data["choices"][0]["message"].get("content") or "").strip()


class HostedOpenAIClient(OpenAIHTTPClient):
    """api.openai.com backend for the hosted-generation pilot.

    Same call sites as OpenAIHTTPClient (generate() with a guided-JSON
    schema); the differences are all here, gated on `hosted`:

      - auth: `Authorization: Bearer $OPENAI_API_KEY` when the key is set,
        read from the environment per request and NEVER logged, cached, or
        embedded in an exception;
      - body dialect (_adapt_body): `chat_template_kwargs` stripped
        (vLLM-only; OpenAI rejects unrecognized arguments),
        `max_completion_tokens` instead of `max_tokens`,
        `reasoning_effort: none` (the API's renamed minimum — see
        _adapt_body) on every structured-output call, and
        the guided schema run through to_hosted_schema() with
        `strict: true`; `temperature`/`top_p` pass through unchanged
        (probed accepted on gpt-5.6-luna — evidence in
        reports/hosted_pilot/schema_compat.md);
      - 429 (and 500/502/503) retried with exponential backoff honoring
        Retry-After; every OTHER 4xx still fails fast;
      - usage capture: every response's usage block, snapshot model id and
        finish_reason land in `last_meta` (and `usage_log`), priced and
        accumulated by the SpendGuard, which aborts the run at the cap;
      - snapshot pinning: the alias resolves on the first response; a
        mid-run snapshot change fails loudly.

    Seed caveat: hosted `seed` is BEST-EFFORT (OpenAI documents no
    determinism guarantee). It is still sent — it measurably improves
    stability — but the ResponseCache is the source of truth for
    reproducibility of a finished run.
    """

    hosted = True
    # Which JSON-Schema subset this backend enforces, and which env var
    # carries its key. Subclasses override; everything else is shared.
    schema_dialect = "openai"
    key_env = "OPENAI_API_KEY"
    # One-line keyfile read when key_env is unset, so a key can live on
    # disk (mode 600) and never pass through a shell history, a process
    # listing, or a chat transcript. Same convention as
    # src/dynbelief/llm_agent/clients.py. Overridable per backend.
    key_file = "~/.config/dynamic_eqa/openai_key"
    chat_path = "/v1/chat/completions"

    def _api_key(self) -> str:
        """$KEY_ENV first (a real env var always wins), else the keyfile.
        Never logged, never cached on the instance, never in an
        exception — read fresh per request."""
        key = os.environ.get(self.key_env, "").strip()
        if key:
            return key
        try:
            path = os.path.expanduser(self.key_file)
            with open(path) as fh:
                return fh.read().strip()
        except OSError:
            return ""
    _RETRYABLE_STATUS = frozenset({429, 500, 502, 503})
    _HTTP_RETRIES = 6
    _BACKOFF_BASE_S = 2.0
    _BACKOFF_MAX_S = 120.0

    def __init__(self, endpoint: str, model: str,
                 timeout: float = 600.0) -> None:
        super().__init__(endpoint, model, timeout)
        import threading
        from .hosted_spend import SpendGuard
        self.guard = SpendGuard.from_env()
        self.snapshot: Optional[str] = None   # pinned from first response
        self.usage_log: list[dict] = []       # one entry per live response
        self._lock = threading.Lock()         # snapshot pin + usage_log
        # last_meta is THREAD-LOCAL: the story stage issues per-resident
        # calls concurrently, and a caller reading last_meta right after
        # its own generate() must never see a sibling thread's response.
        self._tls = threading.local()

    @property
    def last_meta(self) -> Optional[dict]:
        return getattr(self._tls, "meta", None)

    def _adapt_body(self, body: dict) -> dict:
        from .hosted_schema import to_hosted_schema
        body = dict(body)
        body.pop("chat_template_kwargs", None)
        # HOSTED_REASONING_EFFORT: none|low|medium|high|xhigh. The brief
        # pinned "minimal", which the gpt-5.6 API retired (probed
        # 2026-08-23); "none" is its literal floor and the default here.
        # It is a KNOB, not a prompt or schema change — raising it leaves
        # the generation contract untouched.
        effort = os.environ.get("HOSTED_REASONING_EFFORT", "none")
        # temperature/top_p are accepted ONLY with reasoning off (probed:
        # with any reasoning effort the API rejects a non-default
        # temperature outright). With reasoning on they are dropped and
        # sampling rides the model's default.
        if effort != "none":
            body.pop("temperature", None)
            body.pop("top_p", None)
        if "max_tokens" in body:
            body["max_completion_tokens"] = body.pop("max_tokens")
        # The brief pinned "minimal"; the gpt-5.6 API renamed the scale
        # (probed 2026-08-23: minimal is gone, supported values are
        # none/low/medium/high/xhigh — see reports/hosted_pilot/). "none"
        # is its successor and the literal minimum.
        body["reasoning_effort"] = effort
        rf = body.get("response_format")
        if rf and rf.get("type") == "json_schema":
            js = dict(rf["json_schema"])
            # HOSTED_SCHEMA_REMOVE: comma-separated extra keywords for
            # to_hosted_schema (e.g. "prefixItems"), set from probe
            # evidence when the default transform is still rejected.
            extra = frozenset(
                k for k in os.environ.get("HOSTED_SCHEMA_REMOVE",
                                          "").split(",") if k)
            js["schema"], _ = to_hosted_schema(js["schema"], extra,
                                               self.schema_dialect)
            js["strict"] = True
            body["response_format"] = dict(rf, json_schema=js)
        return body

    def _post_chat(self, body: dict) -> dict:
        import requests
        self.guard.preflight()
        headers = {}
        key = self._api_key()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        last_err: Exception = RuntimeError("unreachable")
        delay = self._BACKOFF_BASE_S
        for attempt in range(self._HTTP_RETRIES):
            if attempt:
                time.sleep(min(delay, self._BACKOFF_MAX_S))
                delay *= 2
            try:
                resp = requests.post(f"{self.base}{self.chat_path}",
                                     json=body, headers=headers,
                                     timeout=self.timeout)
            except (requests.ConnectionError, requests.Timeout) as e:
                last_err = e
                _logger.warning("hosted call failed (attempt %d/%d): %s",
                                attempt + 1, self._HTTP_RETRIES,
                                type(e).__name__)
                continue
            if resp.status_code in self._RETRYABLE_STATUS:
                retry_after = resp.headers.get("Retry-After")
                try:
                    wait = float(retry_after) if retry_after else 0.0
                except ValueError:
                    wait = 0.0
                if wait > 0:
                    delay = max(delay, wait)
                last_err = RuntimeError(
                    f"hosted API transient {resp.status_code}")
                _logger.warning(
                    "hosted API %d (attempt %d/%d, retry-after=%s)",
                    resp.status_code, attempt + 1, self._HTTP_RETRIES,
                    retry_after)
                continue
            if resp.status_code >= 400:
                # Fail fast, error body verbatim. Deliberately a fresh
                # exception (not requests' HTTPError): it carries only the
                # SERVER's response text, never the outbound request or
                # its auth header.
                raise RuntimeError(
                    f"hosted API {resp.status_code}: {resp.text[:2000]}")
            data = resp.json()
            self._note_response(data)
            return data
        raise last_err

    def _note_response(self, data: dict) -> None:
        model = data.get("model") or ""
        with self._lock:
            if self.snapshot is None:
                self.snapshot = model
                _logger.info("hosted model alias %s resolved to snapshot %s",
                             self.model, model)
            elif model != self.snapshot:
                raise RuntimeError(
                    f"hosted model snapshot changed mid-run: pinned "
                    f"{self.snapshot!r}, this response came from {model!r} "
                    f"— aborting; a pilot must not mix snapshots silently")
        usage = data.get("usage") or {}
        choices = data.get("choices") or [{}]
        meta = {
            "model_snapshot": model,
            "finish_reason": choices[0].get("finish_reason"),
            "usage": usage,
            "cost_usd": None,
        }
        self._tls.meta = meta
        with self._lock:
            self.usage_log.append(meta)
        # charge LAST: SpendCapExceeded must not lose the meta record.
        meta["cost_usd"] = self.guard.charge(model, usage)


class GeminiOpenAIClient(HostedOpenAIClient):
    """Google Gemini through its OpenAI-compatibility layer
    (https://generativelanguage.googleapis.com/v1beta/openai/).

    Same call sites, same spend guard, same usage capture. The
    differences, all probed rather than assumed:

      - key from $GEMINI_API_KEY (Bearer, same header shape);
      - the compat layer takes `max_tokens`, NOT OpenAI's
        `max_completion_tokens` — the base class rewrites one into the
        other, so this rewrites it back;
      - `reasoning_effort` IS supported (Google maps it onto
        thinking_level/thinking_budget) and must never be sent alongside
        thinking_level;
      - the schema subset descends from OpenAPI 3.0 — no prefixItems, no
        const, no all-required rule — hence schema_dialect="gemini";
      - documented behaviour of the compat layer: unrecognised
        parameters are SILENTLY IGNORED rather than rejected, so a
        missing feature shows up as a quality regression, never a 400.
        That is why `strict` is not relied on and every response is
        re-validated against the original schema downstream.
    """

    schema_dialect = "gemini"
    key_env = "GEMINI_API_KEY"
    key_file = "~/.config/dynamic_eqa/gemini_key"
    # the compat layer mounts the OpenAI surface under this prefix; the
    # endpoint is given as the bare host root.
    chat_path = "/v1beta/openai/chat/completions"

    def _adapt_body(self, body: dict) -> dict:
        body = super()._adapt_body(body)
        if "max_completion_tokens" in body:
            body["max_tokens"] = body.pop("max_completion_tokens")
        return body


def _is_gemini_endpoint(endpoint: str) -> bool:
    from urllib.parse import urlparse
    host = urlparse(endpoint).hostname or ""
    return host.endswith("generativelanguage.googleapis.com")


def _is_hosted_endpoint(endpoint: str) -> bool:
    from urllib.parse import urlparse
    host = urlparse(endpoint).hostname or ""
    return (host == "api.openai.com" or host.endswith(".api.openai.com")
            or _is_gemini_endpoint(endpoint))


def _hosted_check(client, schema: dict, parsed, live: bool = True):
    """The hosted umbrella (applied by generate_json when client.hosted):
    truncation guard (live calls only — a cached hit has no fresh
    finish_reason), null-stripping, and re-validation of the response
    against the ORIGINAL schema — the downstream re-check that makes
    to_hosted_schema()'s keyword removals safe at every call site.
    Raises ValueError (the retry trigger) on any violation."""
    from .hosted_schema import drop_nulls
    meta = getattr(client, "last_meta", None)
    if live and meta is not None and meta.get("finish_reason") == "length":
        raise ValueError("hosted truncation: finish_reason=length")
    parsed = drop_nulls(parsed)
    try:
        import jsonschema
    except ImportError:                                # pragma: no cover
        return parsed
    try:
        jsonschema.validate(parsed, schema)
    except jsonschema.ValidationError as e:
        raise ValueError(f"original-schema violation "
                         f"(constraint lost to the hosted transform?): "
                         f"{e.message[:300]}") from None
    return parsed


_client = None  # _LLMClient | OpenAIHTTPClient — whichever _get_client last built


def _get_client(model: str):
    """Shared client singleton. GENERATION_ENDPOINT set -> HTTP client
    against that OpenAI-compatible server; unset -> in-process vLLM.
    Re-read per call (not import time) so tests and callers can flip the
    env var without re-importing the module."""
    global _client
    endpoint = os.environ.get("GENERATION_ENDPOINT", "").strip()
    if endpoint:
        # api.openai.com -> the metered hosted adapter (pilot); anything
        # else -> the served-vLLM client, exactly as before. The check
        # lives HERE, once — call sites branch on client.hosted only.
        cls = (GeminiOpenAIClient if _is_gemini_endpoint(endpoint)
               else HostedOpenAIClient if _is_hosted_endpoint(endpoint)
               else OpenAIHTTPClient)
        if (type(_client) is not cls
                or _client.model != model
                or _client.base != endpoint.rstrip("/")):
            _client = cls(endpoint, model)
    else:
        if not isinstance(_client, _LLMClient) or _client.model != model:
            _client = _LLMClient(model)
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
    temperature: float = DEFAULT_TEMPERATURE,
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
    hosted = getattr(client, "hosted", False)
    if cache and not force:
        raw = cache.get(seed)
        if raw is not None:
            try:
                parsed = json.loads(raw)
                if hosted:
                    parsed = _hosted_check(client, schema, parsed,
                                           live=False)
                return validate(parsed)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # A cached response the current validate rejects (e.g. a
                # partial-coverage judge response cached before coverage
                # was enforced) is treated as a cache miss, not a fatal
                # error — regenerate and overwrite it.
                _logger.warning(
                    "[%s] cached response failed validation (seed=%d): %s — regenerating",
                    stage, seed, e,
                )

    last_err: Exception = RuntimeError(f"generate_json: max_retries={max_retries} is not positive")
    for attempt in range(max_retries):
        raw = client.generate(system, user, schema, seed=seed + attempt, temperature=temperature)
        try:
            parsed = json.loads(raw)
            if hosted:
                parsed = _hosted_check(client, schema, parsed)
            result = validate(parsed)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            last_err = e
            _logger.warning(
                "[%s] guided-JSON failure on attempt %d/%d (seed=%d): %s\nRaw output: %r",
                stage, attempt + 1, max_retries, seed + attempt, e, raw,
            )
            continue
        if cache:
            # Hosted: the usage block, snapshot id and finish_reason ride
            # in the cache record (Task 1.4) — the raw data the pilot
            # report is built from.
            extra = (dict(client.last_meta)
                     if hosted and getattr(client, "last_meta", None)
                     else None)
            cache.put(seed, user, raw, extra=extra)
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
    return_think: bool = False,
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
    for eval review.

    return_think=True returns (result, think_excerpt) instead of result —
    the truncated reasoning trace, from the live call or the cache record
    ("" when the response had no think block)."""
    if cache and not force:
        record = cache.get_record(seed)
        if record is not None and record.get("raw") is not None:
            try:
                result = validate(json.loads(record["raw"]))
                return (result, record.get("think", "")) if return_think else result
            except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
                _logger.warning(
                    "[%s] cached response failed validation (seed=%d): %s — regenerating",
                    stage, seed, e,
                )

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
        # 20k, not 2k: at 2000 chars the freeform day-planner's trace was
        # cut mid-sentence and the model's actual reasoning was lost to
        # review. Storage is a JSON file per call; the extra chars are
        # noise-level on disk and priceless when auditing a bad day.
        think = think[:20000]
        if cache:
            cache.put(seed, user, payload, think=think)
        return (result, think) if return_think else result
    raise last_err
