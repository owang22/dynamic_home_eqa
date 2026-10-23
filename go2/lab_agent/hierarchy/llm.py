"""A small OpenAI-compatible chat client for the hierarchy (vLLM, or any server with /v1/chat/completions).

Tool calls use a JSON-action protocol with structured outputs (response_format json_schema), not the server's
native tool calling: the vLLM on :8300 runs without --enable-auto-tool-choice, and Khang's server may differ too.
The model returns one JSON object per step: {"thought": ..., "tool": ..., "args": {...}}.

Config (environment or arguments):
  HIER_SMALL_URL    default http://127.0.0.1:8300/v1   (the 27B tonight, as a stand-in for the 8B)
  HIER_SMALL_MODEL  default: the first model the server lists
"""
from __future__ import annotations

import base64
import io
import json
import os
import time
import urllib.request

DEFAULT_URL = os.environ.get("HIER_SMALL_URL", "http://127.0.0.1:8300/v1")


def jpg_small(jpg: bytes, width: int = 768, quality: int = 85) -> bytes:
    from PIL import Image
    im = Image.open(io.BytesIO(jpg))
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)))
    b = io.BytesIO()
    im.convert("RGB").save(b, "JPEG", quality=quality)
    return b.getvalue()


def image_part(jpg: bytes, width: int = 768) -> dict:
    return {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,"
                                               + base64.b64encode(jpg_small(jpg, width)).decode()}}


class LLM:
    """One model on one OpenAI-compatible server."""

    def __init__(self, url: str = DEFAULT_URL, model: str | None = None, timeout: float = 300,
                 thinking: bool = False, name: str | None = None):
        self.url = url.rstrip("/")
        self.model = model or os.environ.get("HIER_SMALL_MODEL") or self._first_model()
        self.timeout = timeout
        self.thinking = thinking
        self.name = name or self.model.split("/")[-1]

    def _first_model(self) -> str:
        with urllib.request.urlopen(self.url + "/models", timeout=10) as r:
            return json.load(r)["data"][0]["id"]

    def chat(self, messages: list, schema: dict | None = None, max_tokens: int = 800, temperature: float = 0.0,
             logprobs: bool = False, extra: dict | None = None) -> dict:
        """Returns {"text", "json" (if schema), "finish", "secs", "usage", "logprobs"}."""
        body = {"model": self.model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature,
                "chat_template_kwargs": {"enable_thinking": self.thinking}}
        if schema is not None:
            body["response_format"] = {"type": "json_schema", "json_schema": {"name": "a", "schema": schema}}
        if logprobs:
            body["logprobs"], body["top_logprobs"] = True, 5
        body.update(extra or {})
        req = urllib.request.Request(self.url + "/chat/completions", json.dumps(body).encode(),
                                     {"Content-Type": "application/json"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            out = json.loads(r.read())
        ch = out["choices"][0]
        res = {"text": ch["message"].get("content") or "", "finish": ch.get("finish_reason"),
               "secs": round(time.time() - t0, 3), "usage": out.get("usage", {}),
               "logprobs": (ch.get("logprobs") or {}).get("content")}
        if schema is not None:
            try:
                res["json"] = json.loads(res["text"])
            except json.JSONDecodeError:
                res["json"] = None
        return res
