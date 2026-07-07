"""
llm_prior/http_client.py — Phase A: an HTTP-based LLMPriorClient
equivalent, for the ONE real constraint L0 never had to deal with: A1's
FMDecisionPolicy runs inside a live habitat_sim episode
(QuestionEpisodeRunner, under the explore-eqa conda env), but this
machine's habitat_sim env has no vllm installed, and vllm's own env has
no habitat_sim — installing either into the other's env risks a real
CUDA/torch version conflict neither environment was built to survive.

The fix is decoupling, not merging environments: run vLLM's own
OpenAI-compatible server (vllm.entrypoints.openai.api_server) as a
separate process from whichever env has vllm installed, bound to
127.0.0.1 ONLY (never 0.0.0.0 — this is a local inference endpoint, not a
served model, and must not be reachable from the network), and have this
module talk to it over plain HTTP with the `requests` library — already
present in the explore-eqa env, no new dependency, and no vllm import
anywhere in this file. FMDecisionPolicy can use either
llm_prior.client.LLMPriorClient (in-process, same env as vllm — what
llm_prior/elicit.py uses) or this HTTPLLMClient (cross-process, works
from an env that has no vllm at all) interchangeably — both expose the
same mcq_logprob(system, user, option_letters, seed) -> dict shape.

Response shape verified directly against a running server before this
was written (see phaseA_backbone.md's own setup notes) —
choices[0].logprobs.content[0].top_logprobs is a list of
{"token": str, "logprob": float, "bytes": [...]}, not the {token_id:
Logprob} dict the in-process vllm.LLM().chat() API returns. Both are
normalized to the same {"top_logprobs": {token_str: logprob}} shape
llm_prior.scoring.parse_mcq_logprob_distribution already expects, so
that parser needs no changes to serve either backend.
"""
from __future__ import annotations

from dataclasses import dataclass

import requests

from dynamic_home_eqa.llm_prior.client import ModelSpec

_DEFAULT_TIMEOUT_S = 120


@dataclass(frozen=True)
class HTTPModelSpec:
    """Same fields as llm_prior.client.ModelSpec, plus the running
    server's base URL — kept as a separate type (not a subclass) so a
    caller can't accidentally pass an in-process spec to the HTTP client
    or vice versa without a type error."""
    model_id: str
    family: str
    provider: str
    quantization: str
    is_generator_family: bool
    base_url: str  # e.g. "http://127.0.0.1:8123/v1" — loopback only, enforced below


def from_model_spec(spec: ModelSpec, base_url: str) -> HTTPModelSpec:
    if not base_url.startswith("http://127.0.0.1") and not base_url.startswith("http://localhost"):
        raise ValueError(
            f"base_url must be loopback-only (http://127.0.0.1:.. or http://localhost:..), got {base_url!r} — "
            "this is a local inference endpoint, never a served model."
        )
    return HTTPModelSpec(
        model_id=spec.model_id, family=spec.family, provider=f"{spec.provider}-http",
        quantization=spec.quantization, is_generator_family=spec.is_generator_family, base_url=base_url,
    )


class HTTPLLMClient:
    """Talks to an already-running `vllm.entrypoints.openai.api_server`
    process over HTTP. Does not start or stop the server — that is a
    separate, explicit step (see scripts/ for the launch command), kept
    out of this class so a test or a short-lived script never
    accidentally spawns a multi-GB model load as a side effect of
    constructing a client object."""

    def __init__(self, spec: HTTPModelSpec) -> None:
        self.spec = spec

    def mcq_logprob(self, system: str, user: str, option_letters: tuple[str, ...], seed: int) -> dict:
        resp = requests.post(
            f"{self.spec.base_url}/chat/completions",
            json={
                "model": self.spec.model_id,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "max_tokens": 1,
                "temperature": 0.0,
                "seed": seed,
                "logprobs": True,
                "top_logprobs": 20,
                # enable_thinking=False: Qwen3's chat template emits a
                # reasoning block before any answer unless told not to —
                # the exact bug L0 found and fixed for the in-process
                # client (llm_prior/client.py's own comment). A no-op for
                # chat templates that don't define this variable, verified
                # against both Qwen and non-Qwen models there; same
                # verification applies here since this is the identical
                # server-side chat template, just reached over HTTP.
                "chat_template_kwargs": {"enable_thinking": False},
            },
            timeout=_DEFAULT_TIMEOUT_S,
        )
        resp.raise_for_status()
        data = resp.json()
        top = data["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
        return {
            "top_logprobs": {entry["token"]: entry["logprob"] for entry in top},
            "greedy_text": data["choices"][0]["message"]["content"],
        }
