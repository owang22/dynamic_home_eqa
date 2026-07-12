"""
llm_prior/client.py — the only module in llm_prior that touches a live
model or the network. Wraps a local vLLM model (used uniformly for both
the same-family and cross-family arms — vLLM serves arbitrary HF model
ids with the identical logprobs/sampling API, so one client code path
covers both, only the model_id/quantization differ) with the three
elicitation modes L0 requires.

No other module under llm_prior/ or under tests/ may import vllm — the
infrastructure rule ("no live LLM calls in pytest") is enforced by
keeping every other consumer of this module's output reading from
llm_prior.cache.EliciationCache instead.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# vLLM engines cap --max-logprobs (this deployment's effective ceiling
# measured directly: requesting 32 raised VLLMValidationError against a
# max of 20). Always request the ceiling — a real option letter that
# still doesn't make the top 20 gets scoring.py's floor probability
# instead of vanishing, which is the same treatment a low-probability
# option gets whether or not it's one of the ones evicted by this cap.
_MAX_LOGPROBS_REQUEST = 20


@dataclass(frozen=True)
class ModelSpec:
    """Recorded verbatim into every elicitation manifest — L0's own
    infrastructure rule ("record exact model identifiers, quantization,
    and sampling params")."""
    model_id: str        # vLLM model string, e.g. "Qwen/Qwen3-14B-AWQ"
    family: str           # "qwen" | "phi3" — the lineage L0's circularity table groups by
    provider: str          # "local-vllm" for every model this phase actually has access to
    quantization: str       # "awq" | "none"
    is_generator_family: bool  # True for the same-family (contaminated-reference) arm


QWEN_GENERATOR = ModelSpec(
    model_id="Qwen/Qwen3-14B-AWQ", family="qwen", provider="local-vllm",
    quantization="awq", is_generator_family=True,
)
# L0 rerun (2026-07-07): replaces MISTRAL_CROSS_FAMILY. Mistral-7B-
# Instruct-v0.3 confounded "cross-family" with "smaller and older/non-
# reasoning than Qwen" — no conclusion about cross-family priors was
# possible from v1. Phi-3-medium-4k-instruct is Microsoft lineage
# (genuinely different from Qwen/Alibaba, no relation to Mistral either),
# 14B — matching Qwen-14B's own parameter count almost exactly, closing
# the size confound directly rather than just picking a bigger model in
# the same family already tested. Ungated on the HF Hub (ungated,
# verified directly), ordinary (non-thinking) chat template.
PHI3_CROSS_FAMILY = ModelSpec(
    model_id="microsoft/Phi-3-medium-4k-instruct", family="phi3", provider="local-vllm",
    quantization="none", is_generator_family=False,
)
# Phase A, A1 (2026-07-07): the FM-backbone decision reasoner's primary
# cross-family model. Meta lineage — genuinely different from Qwen
# (generator) and from Phi-3/Microsoft (L0's cross-family pick) — at
# 70B, a real step up in reasoning capability class from L0's 14B-class
# comparison, not just a different lineage at the same size. AWQ INT4
# (~40GB) fits this machine's single 96GB GPU with room for a long-
# context KV cache. casperhansen's quantization: a well-known, widely
# used AutoAWQ release, ungated on the HF Hub (verified directly) —
# meta-llama's own repo is gated and would need an HF_TOKEN this
# environment doesn't have.
LLAMA33_CROSS_FAMILY = ModelSpec(
    model_id="casperhansen/llama-3.3-70b-instruct-awq", family="llama", provider="local-vllm",
    quantization="awq", is_generator_family=False,
)

from dynamic_home_eqa.paths import MODEL_CACHE_DIR as _MODEL_CACHE_DIR


class LLMPriorClient:
    """Lazy-loaded per ModelSpec — call load() once, reuse for every
    elicitation target against that model, exactly like generation/
    llm_client.py's own _LLMClient does (loading a 14B/7B model per call
    would dominate runtime)."""

    def __init__(self, spec: ModelSpec) -> None:
        self.spec = spec
        self._llm = None

    def load(self) -> None:
        if self._llm is not None:
            return
        import os
        os.environ.setdefault("HF_HOME", _MODEL_CACHE_DIR)
        from vllm import LLM
        # trust_remote_code: required for Phi-3 (Microsoft's custom
        # modeling code); a no-op for Qwen (verified — loads identically
        # with or without it).
        self._llm = LLM(model=self.spec.model_id, disable_log_stats=True, trust_remote_code=True)

    def _chat(self, system: str, user: str, *, max_tokens: int, temperature: float,
              seed: Optional[int], logprobs: Optional[int], n: int = 1):
        if self._llm is None:
            self.load()
        from vllm import SamplingParams
        params = SamplingParams(
            temperature=temperature, max_tokens=max_tokens, seed=seed, logprobs=logprobs, n=n,
        )
        conv = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        # enable_thinking=False: Qwen3's chat template inserts a reasoning
        # block before any answer unless told not to (verified directly —
        # without this, mcq_logprob's first generated token was the start
        # of a reasoning trace, not the answer letter, and every mode's
        # short completion budget was consumed by that trace instead of a
        # parseable answer). A no-op for chat templates (e.g. Mistral's)
        # that don't define this variable — Jinja silently ignores unused
        # template variables, verified against both models this phase uses.
        return self._llm.chat(
            [conv], sampling_params=params, chat_template_kwargs={"enable_thinking": False},
        )[0]

    def mcq_logprob(self, system: str, user: str, option_letters: tuple[str, ...], seed: int) -> dict:
        """KnowNo-style: one greedy (temperature=0) single-token
        completion, logprobs read off the first generated position.
        Returns the raw {"top_logprobs": {token_str: logprob}} dict —
        llm_prior/scoring.py turns this into a normalized distribution
        over option_letters, not this module (this module's only job is
        talking to the model, never interpreting the result — see module
        docstring on why no other module imports vllm)."""
        out = self._chat(system, user, max_tokens=1, temperature=0.0, seed=seed, logprobs=_MAX_LOGPROBS_REQUEST).outputs[0]
        top = out.logprobs[0] if out.logprobs else {}
        return {
            "top_logprobs": {lp.decoded_token: lp.logprob for lp in top.values()},
            "greedy_text": out.text,
        }

    def verbalized(self, system: str, user: str, seed: int) -> str:
        """Direct-statement mode: one greedy completion through the same
        chat-template path as every other mode (a prior version called
        vLLM's raw .generate() on a manually concatenated system+user
        string, which skips the chat template's generation-prompt
        scaffolding entirely — verified as the reason Qwen3 free-ran
        instead of answering directly; fixed to use .chat() uniformly)."""
        out = self._chat(system, user, max_tokens=512, temperature=0.0, seed=seed, logprobs=None).outputs[0]
        return out.text.strip()

    def sample_count(self, system: str, user: str, option_letters: tuple[str, ...], k: int, seed: int) -> dict:
        """k independent completions at temperature>0 (0.8 — enough
        spread to get real variation across samples; fixed so results are
        reproducible given the same seed), empirical counts over
        option_letters plus an "other" bucket for anything that doesn't
        parse to one of them."""
        out = self._chat(system, user, max_tokens=4, temperature=0.8, seed=seed, logprobs=None, n=k)
        counts = {letter: 0 for letter in option_letters}
        counts["_other"] = 0
        for completion in out.outputs:
            token = completion.text.strip()[:1].upper()
            if token in counts:
                counts[token] += 1
            else:
                counts["_other"] += 1
        return counts
