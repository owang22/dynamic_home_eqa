"""Model clients for the LLM-agent harness. One interface:
    client.generate(system, user, schema, seed=None, temperature=...) -> str

Local Qwen (OpenAI-compatible vLLM endpoint) is the tested path. The API
classes below are thin stubs for the frontier-model axis (spec 2.3: prompts
held fixed across models; model identity is an experimental axis, not a
tuning target). Anthropic models do not support guided JSON grammars or
seeds — schema conformance is prompted and validated caller-side, and
determinism is best-effort (temperature 0) — report both as protocol
differences when comparing against the local guided-decoding runs.
"""
from __future__ import annotations

import json
import os


def local_qwen(endpoint: str = "http://127.0.0.1:8300",
               model: str = "Qwen/Qwen3.6-35B-A3B"):
    from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient
    return OpenAIHTTPClient(endpoint, model)


class OpenAIClient:
    """OpenAI API client for the frontier-model axis. Reads the key from
    OPENAI_API_KEY or ~/.config/dynamic_eqa/openai_key (one line). Uses
    response_format json_schema (strict) — the closest analogue to the local
    guided decoding — plus per-request seed, so the protocol gap vs the local
    runs is smaller than for providers without grammar support. Report the
    remaining differences (server-side sampling, model updates) as protocol
    caveats."""

    def __init__(self, model: str = "gpt-5.2"):
        import os, pathlib as _pl
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            kf = _pl.Path(os.environ.get("DYNAMIC_EQA_OPENAI_KEYFILE",
                         "~/.config/dynamic_eqa/openai_key")).expanduser()
            if kf.exists():
                key = kf.read_text().strip()
        if not key:
            raise RuntimeError(
                "no OpenAI key: set OPENAI_API_KEY or write it to "
                "~/.config/dynamic_eqa/openai_key")
        from openai import OpenAI
        self.client = OpenAI(api_key=key)
        self.model = model

    # $/1M tokens (input, output). VERIFY against current OpenAI pricing —
    # placeholders below are estimates; the ledger always records exact token
    # counts, so costs can be recomputed later from the JSONL regardless.
    PRICES = {}

    def generate(self, system: str, user: str, schema: dict,
                 seed=None, temperature: float = 0.2) -> str:
        import copy as _copy, json as _json, time as _time, pathlib as _pl
        strict = _copy.deepcopy(schema)
        strict.setdefault("additionalProperties", False)
        t0 = _time.time()
        kwargs = dict(
            model=self.model,
            seed=(int(seed) & 0x7FFFFFFF) if seed is not None else None,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            response_format={"type": "json_schema",
                             "json_schema": {"name": "decision",
                                             "strict": True,
                                             "schema": strict}})
        try:
            resp = self.client.chat.completions.create(temperature=temperature, **kwargs)
        except Exception as e:
            if "temperature" not in str(e):
                raise
            # reasoning-class models pin temperature to the default — a
            # protocol difference vs the local temp-0.2 runs; report it
            resp = self.client.chat.completions.create(**kwargs)
        dt = _time.time() - t0
        u = resp.usage
        led = _pl.Path(__file__).resolve().parents[3] / "reports/llm_agent/api_usage.jsonl"
        led.parent.mkdir(parents=True, exist_ok=True)
        pin, pout = self.PRICES.get(self.model, (None, None)) or (None, None)
        cost = (u.prompt_tokens * pin + u.completion_tokens * pout) / 1e6             if pin is not None else None
        with led.open("a") as fh:
            fh.write(_json.dumps({
                "ts": _time.strftime("%Y-%m-%dT%H:%M:%S"), "model": self.model,
                "prompt_tokens": u.prompt_tokens,
                "completion_tokens": u.completion_tokens,
                "latency_s": round(dt, 2), "est_cost_usd": cost}) + "\n")
        return resp.choices[0].message.content


class AnthropicClient:
    """Untested stub — requires ANTHROPIC_API_KEY. Validates JSON against the
    schema's required keys caller-side; retries once on parse failure."""

    def __init__(self, model: str = "claude-sonnet-5"):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = model

    def generate(self, system: str, user: str, schema: dict,
                 seed=None, temperature: float = 0.0) -> str:
        prompt = (user + "\n\nRespond ONLY with a JSON object matching: "
                  + json.dumps(schema))
        for _ in range(2):
            msg = self.client.messages.create(
                model=self.model, max_tokens=1024, temperature=temperature,
                system=system, messages=[{"role": "user", "content": prompt}])
            text = msg.content[0].text.strip()
            if text.startswith("```"):
                text = text.strip("`").lstrip("json").strip()
            try:
                obj = json.loads(text)
                if all(k in obj for k in schema.get("required", [])):
                    return json.dumps(obj)
            except json.JSONDecodeError:
                continue
        raise ValueError("model did not return schema-conformant JSON")
