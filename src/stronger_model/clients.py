"""Two drop-in replacements for `baselines.patrol.llm.LLMClient`, for asking what a stronger model adds.

Both keep the interface every runner in src/self_improve uses - `complete(messages, schema,
max_tokens) -> (text, usage)` and a `stats` dict - so `overnight_wave.run_one_arm` runs unchanged.

QwenThinkingClient: the same Qwen3.8 server, with the think block switched ON and capped by vLLM's
`thinking_token_budget`. Measured on 2026-09-30 (vLLM 0.25, --reasoning-parser qwen3): the JSON
grammar is applied only after </think>, so thinking and the schema now combine; with no cap one
room choice thought for 5,930 tokens (222 s), with a 1,000-token cap it stopped at the cap, closed
the block and wrote valid JSON (43 s). `max_tokens` is the arm's own answer allowance PLUS the
thinking budget, so the answer keeps exactly the room it had without thinking.

ClaudeClient: one fresh `claude -p` call per prompt - no conversation carried between calls, no
tools, no settings or MCP servers - so the model sees what Qwen sees and nothing else. It runs on
the logged-in subscription; `__init__` refuses if ANTHROPIC_API_KEY is set, because then the CLI
would bill the API. Claude Code adds ~500 tokens of its own context (the user's email, the working
directory, the date; checked 2026-09-30), nothing about the task.

Neither may share a cache directory with LLMClient: the shared key hashes model, messages, schema,
max_tokens, temperature and seed, and neither the thinking switch nor the backend is in it, so a
shared directory would replay non-thinking Qwen answers as if they were these. Each client adds its
own setting to the key AND refuses the shared directory.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from baselines.patrol.llm import LLMClient

SHARED_CACHE = pathlib.Path("llm_prior_cache/self_improve").resolve()


def _refuse_shared(cache_dir: pathlib.Path) -> None:
    if cache_dir.resolve() == SHARED_CACHE:
        raise ValueError(f"{cache_dir} is the shared non-thinking Qwen cache; give this client its own")


def with_the_fields_stated(messages: List[dict], schema: Optional[dict]) -> List[dict]:
    """Append one line naming the answer's fields to the system message.

    Without thinking, the grammar forces the fields in order as the model writes, so the prompt never
    had to name them. With thinking, the grammar starts only after </think>, and on 2026-09-30 the
    first several hundred thinking tokens of every test prompt went on guessing the format ("Could
    output {"spot": ...}"; there is no field called spot). Naming the fields costs one line and
    carries no information about the home."""
    if schema is None or "properties" not in schema:
        return messages
    fields = ", ".join(schema["properties"])
    line = (f"After you have thought it through, reply with one JSON object whose fields are, in this order: "
            f"{fields}.")
    out = copy.deepcopy(messages)
    for m in out:
        if m["role"] == "system":
            m["content"] = m["content"] + "\n\n" + line
            return out
    return [{"role": "system", "content": line}] + out


class QwenThinkingClient(LLMClient):
    def __init__(self, cache_dir: pathlib.Path, thinking_budget: int, state_the_fields: bool = True, **kw) -> None:
        _refuse_shared(cache_dir)
        super().__init__(cache_dir, **kw)
        self.thinking_budget = int(thinking_budget)
        self.state_the_fields = state_the_fields
        self.stats.update(reasoning_tokens_est=0, hit_the_thinking_cap=0)

    def key(self, messages, schema, max_tokens) -> str:
        blob = json.dumps({"base": super().key(messages, schema, max_tokens),
                           "enable_thinking": True, "thinking_token_budget": self.thinking_budget,
                           "state_the_fields": self.state_the_fields},
                          sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    def complete(self, messages: List[dict], schema: Optional[dict], max_tokens: int) -> Tuple[Optional[str], dict]:
        path = self.cache_dir / f"{self.key(messages, schema, max_tokens)}.json"
        if path.exists():
            rec = json.loads(path.read_text())
            with self.lock:
                self.stats["cached"] += 1
            return rec["text"], rec.get("usage", {})
        if self.replay_only:
            return None, {}
        sent = with_the_fields_stated(messages, schema) if self.state_the_fields else messages
        body: Dict[str, Any] = {"model": self.model, "messages": sent,
                                "max_tokens": max_tokens + self.thinking_budget,
                                "temperature": 0, "seed": 0,
                                "chat_template_kwargs": {"enable_thinking": True},
                                "thinking_token_budget": self.thinking_budget}
        if schema is not None:
            body["response_format"] = {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}}
        t0 = time.time()
        text, reasoning, usage, finish = None, None, {}, None
        for attempt in range(self.ATTEMPTS):
            try:
                d = self._post(body)
                msg = d["choices"][0]["message"]
                text = msg.get("content")
                reasoning = msg.get("reasoning") or msg.get("reasoning_content") or ""
                finish = d["choices"][0].get("finish_reason")
                usage = d.get("usage") or {}
                break
            except Exception as e:  # noqa: BLE001 - same retry policy as LLMClient
                print(f"thinking call failed ({attempt + 1}/{self.ATTEMPTS}): {type(e).__name__}: {e}",
                      file=sys.stderr, flush=True)
                time.sleep(2 * (attempt + 1))
        dt = time.time() - t0
        with self.lock:
            self.stats["calls"] += 1
            self.stats["prompt_tokens"] += int(usage.get("prompt_tokens", 0))
            self.stats["completion_tokens"] += int(usage.get("completion_tokens", 0))
            self.stats["seconds"] += dt
            if text is None:
                self.stats["lost"] = self.stats.get("lost", 0) + 1
            # ~4 characters a token; only used to count how often the cap bound
            est = len(reasoning or "") // 4
            self.stats["reasoning_tokens_est"] += est
            if est >= 0.9 * self.thinking_budget:
                self.stats["hit_the_thinking_cap"] += 1
        if text is not None:
            tmp = path.with_name(f"{path.stem}.{threading.get_ident()}.tmp")
            tmp.write_text(json.dumps({"text": text, "reasoning": reasoning, "usage": usage, "finish": finish,
                                       "model": self.model, "thinking_token_budget": self.thinking_budget,
                                       "seconds": round(dt, 1)}))
            tmp.replace(path)
        return text, usage


def _enforce_schema_limits(obj: Any, schema: dict, cut: List[str], where: str = "$") -> Any:
    """Apply maxLength / maxItems the way Qwen's grammar does (it cannot write past them), and record
    every cut. Claude's structured output validates types and enums but is not guaranteed to honour
    length limits, and an arm whose notes are allowed to be longer is a different arm."""
    if not isinstance(schema, dict):
        return obj
    if isinstance(obj, str) and "maxLength" in schema and len(obj) > schema["maxLength"]:
        cut.append(f"{where}: string {len(obj)} > {schema['maxLength']}")
        return obj[: schema["maxLength"]]
    if isinstance(obj, list):
        if "maxItems" in schema and len(obj) > schema["maxItems"]:
            cut.append(f"{where}: {len(obj)} items > {schema['maxItems']}")
            obj = obj[: schema["maxItems"]]
        return [_enforce_schema_limits(x, schema.get("items", {}), cut, f"{where}[{i}]") for i, x in enumerate(obj)]
    if isinstance(obj, dict):
        props = schema.get("properties", {})
        return {k: _enforce_schema_limits(v, props.get(k, {}), cut, f"{where}.{k}") for k, v in obj.items()}
    return obj


def _strip_limits(schema: Any) -> Any:
    """The schema sent to Claude, without the length keywords its structured output may reject.
    Limits are applied afterwards by _enforce_schema_limits, and the prompts already state them."""
    if isinstance(schema, dict):
        return {k: _strip_limits(v) for k, v in schema.items() if k not in ("maxLength", "maxItems", "minItems")}
    if isinstance(schema, list):
        return [_strip_limits(x) for x in schema]
    return schema


class ClaudeClient:
    def __init__(self, cache_dir: pathlib.Path, model: str = "sonnet", effort: Optional[str] = None,
                 timeout_s: float = 1800.0) -> None:
        if os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY is set: `claude -p` would bill the API. Unset it.")
        _refuse_shared(cache_dir)
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model, self.effort, self.timeout_s = model, effort, timeout_s
        self.replay_only = False
        self.lock = threading.Lock()
        self.workdir = pathlib.Path(tempfile.mkdtemp(prefix="claude_as_robot_"))
        self.stats = {"calls": 0, "cached": 0, "prompt_tokens": 0, "completion_tokens": 0, "seconds": 0.0,
                      "list_price_usd": 0.0, "fields_cut_to_the_schema_limit": 0, "lost": 0}

    def key(self, messages, schema, max_tokens) -> str:
        blob = json.dumps({"backend": "claude -p", "model": self.model, "effort": self.effort,
                           "messages": messages, "schema": schema, "max_tokens": max_tokens}, sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    def _call(self, messages: List[dict], schema: Optional[dict]) -> dict:
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        turns = [m for m in messages if m["role"] != "system"]
        if len(turns) != 1 or turns[0]["role"] != "user":
            raise ValueError("ClaudeClient expects one system and one user message, like every arm so far")
        cmd = ["claude", "-p", "--model", self.model, "--system-prompt", system, "--tools", "",
               "--setting-sources", "", "--strict-mcp-config", "--no-session-persistence",
               "--output-format", "json"]
        if self.effort:
            cmd += ["--effort", self.effort]
        if schema is not None:
            cmd += ["--json-schema", json.dumps(_strip_limits(schema))]
        p = subprocess.run(cmd, input=turns[0]["content"], capture_output=True, text=True,
                           timeout=self.timeout_s, cwd=self.workdir)
        if p.returncode != 0 and not p.stdout.strip():
            raise RuntimeError(f"claude -p exit {p.returncode}: {p.stderr[-500:]}")
        return json.loads(p.stdout)

    def complete(self, messages: List[dict], schema: Optional[dict], max_tokens: int) -> Tuple[Optional[str], dict]:
        path = self.cache_dir / f"{self.key(messages, schema, max_tokens)}.json"
        if path.exists():
            rec = json.loads(path.read_text())
            with self.lock:
                self.stats["cached"] += 1
            return rec["text"], rec.get("usage", {})
        if self.replay_only:
            return None, {}
        t0 = time.time()
        d, text, cut, raw = None, None, [], None
        for attempt in range(2):
            try:
                d = self._call(messages, schema)
                if d.get("is_error"):
                    raise RuntimeError(str(d.get("result"))[:300])
                obj = d.get("structured_output")
                raw = d.get("result")
                if schema is not None:
                    if obj is None:
                        obj = json.loads(raw)
                    obj = _enforce_schema_limits(obj, schema, cut)
                    text = json.dumps(obj)
                else:
                    text = raw
                break
            except Exception as e:  # noqa: BLE001
                print(f"claude call failed ({attempt + 1}/2): {type(e).__name__}: {e}", file=sys.stderr, flush=True)
                time.sleep(5 * (attempt + 1))
        dt = time.time() - t0
        u = (d or {}).get("usage") or {}
        usage = {"prompt_tokens": int(u.get("input_tokens", 0)) + int(u.get("cache_read_input_tokens", 0))
                 + int(u.get("cache_creation_input_tokens", 0)),
                 "completion_tokens": int(u.get("output_tokens", 0))}
        with self.lock:
            self.stats["calls"] += 1
            self.stats["prompt_tokens"] += usage["prompt_tokens"]
            self.stats["completion_tokens"] += usage["completion_tokens"]
            self.stats["seconds"] += dt
            self.stats["list_price_usd"] += float((d or {}).get("total_cost_usd") or 0)
            self.stats["fields_cut_to_the_schema_limit"] += len(cut)
            if text is None:
                self.stats["lost"] += 1
        if text is not None:
            tmp = path.with_name(f"{path.stem}.{threading.get_ident()}.tmp")
            tmp.write_text(json.dumps({"text": text, "raw_result": raw, "cut": cut, "usage": usage,
                                       "model_usage": (d or {}).get("modelUsage"), "model": self.model,
                                       "effort": self.effort, "seconds": round(dt, 1)}))
            tmp.replace(path)
        return text, usage
