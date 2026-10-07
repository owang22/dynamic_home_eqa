"""Calling the model: cached by a hash of everything that shapes the response,
retried with the problem named when a response fails a check."""
from __future__ import annotations

import hashlib
import json
import pathlib
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
    def __init__(self, client, cache_dir: pathlib.Path, model: str, effort: str) -> None:
        self.client, self.model, self.effort = client, model, effort
        self.cache = ResponseCache(cache_dir)
        self.calls, self.cached_hits, self.failures = 0, 0, 0
        self.cost = 0.0

    def call(self, stage: str, system: str, user: str, schema: dict,
             check: Optional[Callable[[dict], str]] = None,
             max_tokens: int = 16000, tries: int = 3) -> dict:
        note = ""
        for attempt in range(tries):
            prompt = user + note
            digest = hashlib.sha256(json.dumps(
                [self.model, self.effort, stage, system, prompt, schema, attempt],
                sort_keys=True).encode()).digest()
            seed = int.from_bytes(digest[:8], "big") & 0x7FFFFFFFFFFFFFFF
            record = self.cache.get_record(seed)
            if record:
                raw = record["raw"]
                self.cached_hits += 1
            else:
                raw = self.client.generate(system, prompt, schema, seed=seed,
                                           max_tokens=max_tokens)
                meta = getattr(self.client, "last_meta", None) or {}
                self.cost += meta.get("cost_usd") or 0.0
                self.cache.put(seed, system + "\n\n" + prompt, raw,
                               extra={"stage": stage, **meta})
                self.calls += 1
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as err:
                note = f"\n\nYour previous answer was not valid JSON ({err}). Answer again."
                self.failures += 1
                continue
            problem = check(parsed) if check else ""
            if not problem:
                return parsed
            self.failures += 1
            note = f"\n\nYour previous answer had a problem: {problem} Answer again."
        raise RuntimeError(f"{stage}: no usable answer after {tries} tries ({note.strip()})")


def check_household(h: dict) -> str:
    ids = [r["id"] for r in h["residents"]]
    if len(set(ids)) != len(ids):
        return "The two residents need different ids."
    owners = set(ids) | {"shared"}
    object_ids = [o["id"] for o in h["objects"]]
    if len(set(object_ids)) != len(object_ids):
        return "Object ids must be unique."
    bad = [o["id"] for o in h["objects"] if o["owner"] not in owners]
    if bad:
        return f"These objects have an owner that is not a resident id or 'shared': {bad}."
    if "sick" not in {s["id"] for s in h["situations"]}:
        return "There must be a situation with id 'sick'."
    for s in h["situations"]:
        if not set(s["happens_to"]) <= set(ids):
            return f"Situation {s['id']} happens_to must use resident ids {ids}."
    for d in h["small_disturbances"]:
        if d["who"] not in set(ids) | {"anyone"}:
            return f"Disturbance who must be a resident id or 'anyone', not {d['who']}."
    for r in h["residents"]:
        habit_ids = [x["id"] for x in r["response_habits"]]
        if len(set(habit_ids)) != len(habit_ids):
            return f"{r['id']}'s response habit ids must be unique."
        for item in r["weekly_routine"]:
            if to_minute(item["start"]) is None or to_minute(item["end"]) is None:
                return f"Routine times must be HH:MM, got {item['start']} and {item['end']}."
    return ""


def check_plan(plan: dict) -> str:
    for a in plan["activities"]:
        if to_minute(a["start"]) is None or to_minute(a["end"]) is None:
            return f"Times must be HH:MM, got {a['start']} and {a['end']}."
    return ""
