"""
Seed/cache layer for reproducible LLM generation.

Every LLM call is seeded from a tuple (household_id, day, stage, occupant_index)
so datasets can be exactly regenerated for debugging.

Caching: raw LLM responses are persisted as JSON files keyed by the seed
integer so re-runs skip the model call entirely. The cache is content-addressed
by seed, not by prompt — if the prompt changes, pass force=True to regenerate.

Cache layout:
    <cache_dir>/
        <seed_hex>.json      # {"seed": int, "prompt": str, "raw": str}
"""
from __future__ import annotations

import hashlib
import json
import pathlib


def make_seed(household_id: str, day: int, stage: str, occupant_index: int = 0) -> int:
    """Deterministic seed from generation context.

    The seed is a 64-bit integer derived by hashing the four-tuple so it is
    independent of ordering and can be reproduced from metadata alone.
    """
    key    = f"{household_id}:{day}:{stage}:{occupant_index}"
    digest = hashlib.sha256(key.encode()).digest()
    return int.from_bytes(digest[:8], "little")


def seed_hex(seed: int) -> str:
    return f"{seed:016x}"


class ResponseCache:
    """Disk-backed cache for raw LLM responses.

    Args:
        cache_dir: Directory to store cached responses. Created if absent.
    """

    def __init__(self, cache_dir: pathlib.Path | str) -> None:
        self._dir = pathlib.Path(cache_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, seed: int) -> pathlib.Path:
        return self._dir / f"{seed_hex(seed)}.json"

    def get(self, seed: int) -> str | None:
        """Return cached raw LLM response string, or None if not cached."""
        p = self._path(seed)
        if p.exists():
            return json.loads(p.read_text()).get("raw")
        return None

    def put(self, seed: int, prompt: str, raw: str) -> None:
        """Persist a raw LLM response alongside its prompt for auditability."""
        self._path(seed).write_text(json.dumps({
            "seed":   seed,
            "prompt": prompt,
            "raw":    raw,
        }, indent=2))

    def has(self, seed: int) -> bool:
        return self._path(seed).exists()

    def clear(self, seed: int) -> None:
        p = self._path(seed)
        if p.exists():
            p.unlink()

    def size(self) -> int:
        return sum(1 for _ in self._dir.glob("*.json"))
