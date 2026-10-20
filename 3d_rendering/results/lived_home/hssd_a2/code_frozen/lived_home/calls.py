"""Calling the model: cached by a hash of model, effort, stage, prompt and schema,
retried with the problem named when a response fails a check. Every call is
appended to calls.jsonl as it happens, so a run can be read while it runs."""
from __future__ import annotations

import hashlib
import json
import pathlib
import threading
import time
from typing import Callable, Optional

from dynamic_home_eqa.generation.cache import ResponseCache


def to_minute(text: str) -> Optional[int]:
    try:
        h, m = text.strip().split(":")
        h, m = int(h), int(m)
    except (ValueError, AttributeError):
        return None
    if not (0 <= h <= 24 and 0 <= m < 60):
        return None
    return h * 60 + m


class Caller:
    def __init__(self, client, cache_dir: pathlib.Path, model: str, effort: str,
                 log_path: Optional[pathlib.Path] = None) -> None:
        self.client, self.model, self.effort = client, model, effort
        self.cache = ResponseCache(cache_dir)
        self.log_path = log_path
        self.calls, self.cached_hits, self.failures, self.cost = 0, 0, 0, 0.0
        self.problems: list[dict] = []
        self._lock = threading.Lock()

    def _key(self, stage: str, system: str, prompt: str, schema: dict, attempt: int) -> int:
        digest = hashlib.sha256(json.dumps(
            [self.model, self.effort, stage, system, prompt, schema, attempt],
            sort_keys=True).encode()).digest()
        return int.from_bytes(digest[:8], "big") & 0x7FFFFFFFFFFFFFFF

    def _write(self, row: dict) -> None:
        if self.log_path is None:
            return
        with self._lock, open(self.log_path, "a") as f:
            f.write(json.dumps(row) + "\n")

    def call(self, stage: str, system: str, user: str, schema: dict,
             check: Optional[Callable[[dict], str]] = None,
             max_tokens: int = 16000, tries: int = 3) -> dict:
        note = ""
        for attempt in range(tries):
            prompt = user + note
            seed = self._key(stage, system, prompt, schema, attempt)
            record = self.cache.get_record(seed)
            started = time.time()
            meta = {}
            if record:
                raw, cached = record["raw"], True
                with self._lock:
                    self.cached_hits += 1
            else:
                raw = self.client.generate(system, prompt, schema, seed=seed,
                                           max_tokens=max_tokens)
                meta = dict(getattr(self.client, "last_meta", None) or {})
                cached = False
                with self._lock:
                    self.cost += meta.get("cost_usd") or 0.0
                    self.calls += 1
                self.cache.put(seed, system + "\n\n" + prompt, raw,
                               extra={"stage": stage, **meta})
            usage = meta.get("usage") or {}
            row = {"stage": stage, "attempt": attempt, "cached": cached,
                   "seconds": round(time.time() - started, 1),
                   "prompt_tokens": usage.get("prompt_tokens"),
                   "completion_tokens": usage.get("completion_tokens"),
                   "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                   "finish": meta.get("finish_reason"), "cost": meta.get("cost_usd"),
                   "prompt_chars": len(system) + len(prompt)}
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as err:
                problem = f"Your previous answer was not valid JSON ({err})."
                if meta.get("finish_reason") == "length":
                    problem = "Your previous answer was cut off for length. Keep it shorter."
                parsed = None
            else:
                problem = check(parsed) if check else ""
            row["problem"] = problem or None
            self._write(row)
            if not problem:
                return parsed
            with self._lock:
                self.failures += 1
                self.problems.append({"stage": stage, "attempt": attempt, "problem": problem})
            note = f"\n\nYour previous answer had a problem: {problem} Answer again."
        raise RuntimeError(f"{stage}: no usable answer after {tries} tries ({note.strip()})")
