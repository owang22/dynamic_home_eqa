"""Spend guard for the hosted-generation pilot (Task 1.5).

Every hosted response is priced from a small committed rate table
(src/revamp_v2/hosted_rates.yaml) and accumulated into a FILE-BACKED
ledger, because the pilot spans several CLI invocations (generate.py,
then story_calendar.py) and the $5 cap is one cap for the whole pilot,
not per process. Crossing the cap raises SpendCapExceeded with a spend
summary; a new call is also refused up front (preflight) once the ledger
already stands at or past the cap.

Reasoning tokens count as output tokens — OpenAI's `completion_tokens`
already includes them (`completion_tokens_details.reasoning_tokens` is a
breakdown, not an addition), so pricing completion_tokens at the output
rate is exactly the brief's rule. Cached prompt tokens (from
`prompt_tokens_details.cached_tokens`) are priced at the table's
cached-input rate when one is given, else at the full input rate.

Environment knobs (all optional):
  HOSTED_RATES_YAML   rate table path   (default src/revamp_v2/hosted_rates.yaml,
                                         resolved against the repo root)
  HOSTED_SPEND_CAP    dollars           (default 5.0)
  HOSTED_SPEND_LEDGER ledger json path  (default /tmp/dynamic-home-eqa-hosted-spend.json)
"""
from __future__ import annotations

import fcntl
import json
import os
import pathlib

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
DEFAULT_RATES = _REPO_ROOT / "src" / "revamp_v2" / "hosted_rates.yaml"
DEFAULT_CAP = 5.0
DEFAULT_LEDGER = "/tmp/dynamic-home-eqa-hosted-spend.json"


class SpendCapExceeded(RuntimeError):
    pass


def _load_rates(path: pathlib.Path) -> dict:
    import yaml
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict) or not data:
        raise ValueError(f"rate table {path} is empty or not a mapping")
    for model, r in data.items():
        for key in ("input_per_1m", "output_per_1m"):
            if not isinstance(r.get(key), (int, float)):
                raise ValueError(
                    f"rate table {path}: {model} lacks numeric {key}")
    return data


class SpendGuard:
    """Prices hosted calls and enforces the pilot cap across processes."""

    def __init__(self, rates: dict, cap_usd: float,
                 ledger_path: str | pathlib.Path) -> None:
        self.rates = rates
        self.cap_usd = float(cap_usd)
        self.ledger_path = pathlib.Path(ledger_path)

    @classmethod
    def from_env(cls) -> "SpendGuard":
        rates_path = pathlib.Path(
            os.environ.get("HOSTED_RATES_YAML") or DEFAULT_RATES)
        cap = float(os.environ.get("HOSTED_SPEND_CAP") or DEFAULT_CAP)
        ledger = os.environ.get("HOSTED_SPEND_LEDGER") or DEFAULT_LEDGER
        return cls(_load_rates(rates_path), cap, ledger)

    # ------------------------------------------------------------ rates --
    def rate_for(self, model: str) -> dict:
        """Exact key, else the longest table key that prefixes `model` —
        response `model` fields carry dated snapshot ids that extend the
        alias the table is written in. Unknown models fail loudly:
        spending unpriced is the one thing this module must never do."""
        if model in self.rates:
            return self.rates[model]
        hits = sorted((k for k in self.rates if model.startswith(k)),
                      key=len, reverse=True)
        if hits:
            return self.rates[hits[0]]
        raise KeyError(
            f"no rate for model {model!r} in the committed rate table "
            f"({sorted(self.rates)}) — add it before spending on it")

    @staticmethod
    def price(rate: dict, usage: dict) -> float:
        prompt = int(usage.get("prompt_tokens") or 0)
        cached = int((usage.get("prompt_tokens_details") or {})
                     .get("cached_tokens") or 0)
        completion = int(usage.get("completion_tokens") or 0)
        cached_rate = rate.get("cached_input_per_1m", rate["input_per_1m"])
        return ((prompt - cached) * rate["input_per_1m"]
                + cached * cached_rate
                + completion * rate["output_per_1m"]) / 1e6

    # ----------------------------------------------------------- ledger --
    def _read(self) -> dict:
        if self.ledger_path.exists():
            try:
                return json.loads(self.ledger_path.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        return {"spent_usd": 0.0, "calls": 0, "by_model": {}}

    def summary(self) -> str:
        led = self._read()
        by = ", ".join(f"{m}: ${v['usd']:.4f} ({v['calls']} calls)"
                       for m, v in sorted(led["by_model"].items()))
        return (f"hosted spend ${led['spent_usd']:.4f} of "
                f"${self.cap_usd:.2f} cap across {led['calls']} call(s)"
                + (f" [{by}]" if by else ""))

    def spent(self) -> float:
        return float(self._read()["spent_usd"])

    def preflight(self) -> None:
        """Refuse to START a call once the ledger stands at/past the cap."""
        if self.spent() >= self.cap_usd:
            raise SpendCapExceeded(
                f"spend cap reached before the call: {self.summary()}")

    def charge(self, model: str, usage: dict) -> float:
        """Record one response's cost; raise AFTER recording if the total
        crosses the cap (the tokens are already spent — the ledger must
        say so even as the run aborts). Returns this call's cost."""
        cost = self.price(self.rate_for(model), usage or {})
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        lock = self.ledger_path.with_suffix(".lock")
        with open(lock, "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            led = self._read()
            led["spent_usd"] = float(led["spent_usd"]) + cost
            led["calls"] = int(led["calls"]) + 1
            per = led["by_model"].setdefault(model, {"usd": 0.0, "calls": 0})
            per["usd"] += cost
            per["calls"] += 1
            tmp = self.ledger_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(led, indent=2))
            tmp.replace(self.ledger_path)
            total = led["spent_usd"]
        if total > self.cap_usd:
            raise SpendCapExceeded(
                f"spend cap crossed by this call: {self.summary()}")
        return cost
