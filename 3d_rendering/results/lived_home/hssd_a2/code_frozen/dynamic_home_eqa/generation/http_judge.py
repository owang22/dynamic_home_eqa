"""
HTTP thinking-judge client — score with a model served OUT OF PROCESS.

Some judge models (e.g. the Qwen3-Next-80B MoE FP8) need a newer vLLM than
this env's habitat-sim pin allows. Rather than upgrade in place, that model
is served by its own conda env (vllm_q) as an OpenAI-compatible endpoint
bound to loopback, and this client talks to it over HTTP.

It duck-types _LLMClient.generate_thinking(system, user, seed, temperature,
max_tokens) -> (payload, think), so generate_json_thinking / score_realism_batch
can use it wherever they'd use the in-process client — the only judge path
this supports is thinking mode (no guided decoding), which is all the
model-comparison arm exercises.
"""
from __future__ import annotations

import re
from typing import Optional

import requests


class HTTPThinkingClient:
    def __init__(self, endpoint: str, model: str, timeout: float = 600.0) -> None:
        # endpoint like "http://127.0.0.1:8123"; loopback only by design.
        self.base = endpoint.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate_thinking(self, system: str, user: str, seed: Optional[int] = None,
                          temperature: float = 0.6, max_tokens: int = 12288) -> tuple[str, str]:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "top_p": 0.95,
            "max_tokens": max_tokens,
            # Thinking models default to reasoning on; pass the kwarg anyway so
            # a non-thinking build doesn't silently drop it.
            "chat_template_kwargs": {"enable_thinking": True},
        }
        if seed is not None:
            # make_seed returns an unsigned 64-bit int; the OpenAI API validates
            # seed as a signed int64 (<= 2**63-1). Mask to 63 bits — still
            # deterministic per call, just within range.
            body["seed"] = seed & 0x7FFFFFFFFFFFFFFF
        resp = requests.post(f"{self.base}/v1/chat/completions", json=body, timeout=self.timeout)
        resp.raise_for_status()
        msg = resp.json()["choices"][0]["message"]
        payload = msg.get("content") or ""
        think = msg.get("reasoning_content") or ""
        # If the server didn't split reasoning out, the think block is inline.
        if not think and "</think>" in payload:
            think, payload = payload.rsplit("</think>", 1)
            think = think.replace("<think>", "").strip()
        # Strip a markdown code fence around the JSON payload (same failure
        # modes as the in-process thinking path).
        fence = re.search(r"```(?:json)?\s*(.*?)```", payload, re.S)
        if fence:
            payload = fence.group(1)
        return payload.strip(), think
