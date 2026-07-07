"""
llm_prior/cache.py — the one cached LLM client L0's infrastructure rules
require: every call keyed by (model_id, prompt_hash, mode, seed), disk-
persisted so scoring is reproducible offline and pytest never needs a
live model. Distinct from generation/cache.py's ResponseCache (that one
is keyed by a generation-context seed alone, content-addressed for a
different reproducibility need — regenerating one household's data
deterministically, not measuring an elicited prior against a fixed
prompt/model/mode combination).

Cache layout: <cache_dir>/<key_hex>.json, one file per (model_id,
prompt_hash, mode, seed) — {"model_id", "prompt_hash", "mode", "seed",
"prompt", "raw_response"}. The prompt is stored alongside the response
purely for human auditability; the cache key never depends on prompt
TEXT directly (only prompt_hash, computed by llm_prior/prompts.py's
prompt_hash()), so a caller must pass a stable hash, not recompute it
differently at read vs. write time.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Optional


def cache_key(model_id: str, prompt_hash: str, mode: str, seed: int) -> str:
    payload = f"{model_id}:{prompt_hash}:{mode}:{seed}"
    return hashlib.sha256(payload.encode()).hexdigest()[:24]


class EliciationCache:
    def __init__(self, cache_dir: pathlib.Path | str) -> None:
        self._dir = pathlib.Path(cache_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, model_id: str, prompt_hash: str, mode: str, seed: int) -> pathlib.Path:
        return self._dir / f"{cache_key(model_id, prompt_hash, mode, seed)}.json"

    def get(self, model_id: str, prompt_hash: str, mode: str, seed: int) -> Optional[dict]:
        p = self._path(model_id, prompt_hash, mode, seed)
        if p.exists():
            return json.loads(p.read_text())
        return None

    def put(self, model_id: str, prompt_hash: str, mode: str, seed: int, prompt: str, raw_response) -> None:
        p = self._path(model_id, prompt_hash, mode, seed)
        p.write_text(json.dumps({
            "model_id": model_id, "prompt_hash": prompt_hash, "mode": mode, "seed": seed,
            "prompt": prompt, "raw_response": raw_response,
        }, indent=2))

    def has(self, model_id: str, prompt_hash: str, mode: str, seed: int) -> bool:
        return self._path(model_id, prompt_hash, mode, seed).exists()
