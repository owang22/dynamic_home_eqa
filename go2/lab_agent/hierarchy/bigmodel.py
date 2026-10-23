"""The big model: Opus through `claude -p` (as web.py runs it), with results cached and a hard call budget.

Replay/eval use (memory frozen, no console):
    from bigmodel import opus_memory_turn
    r = opus_memory_turn(question, index, K, now, history=[...])     # cached by its inputs

Every real claude -p call is appended to logs/claude_calls.jsonl; a call is refused once that file holds
HIER_OPUS_BUDGET calls (default 40), so an evaluation loop cannot run away. Cached answers cost nothing.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "replay" / "cache" / "opus"
LEDGER = HERE / "logs" / "claude_calls.jsonl"
SYSTEM = HERE.parent / "SYSTEM.md"
PY = "/home/oliver/miniconda3/bin/python3"
BUDGET = int(os.environ.get("HIER_OPUS_BUDGET", "40"))


class BudgetExceeded(RuntimeError):
    pass


def calls_made() -> int:
    return sum(1 for _ in LEDGER.open()) if LEDGER.exists() else 0


def prompt_text(question: str, history: list | None) -> str:
    if not history:
        return question
    h = "".join(f"Oliver (earlier): {q}\nYou (earlier): {a}\n\n" for q, a in history)
    return f"Earlier in this conversation:\n\n{h}Now Oliver says: {question}"


def run_claude(prompt: str, mcp_env: dict, model: str = "opus", timeout: int = 600, tag: str = "") -> dict:
    """One claude -p turn with only the memory-only MCP server. Returns {answer, calls, secs, cost, raw_events}."""
    if calls_made() >= BUDGET:
        raise BudgetExceeded(f"{calls_made()} claude -p calls already made (budget {BUDGET})")
    cfg = {"mcpServers": {"lab": {"command": PY, "args": [str(HERE / "mem_mcp.py")], "env": mcp_env}}}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=HERE / "logs") as f:
        json.dump(cfg, f)
        cfgp = f.name
    cmd = ["claude", "-p", "--model", model, "--mcp-config", cfgp, "--strict-mcp-config", "--tools", "",
           "--allowedTools", "mcp__lab__*", "--append-system-prompt-file", str(SYSTEM),
           "--disable-slash-commands", "--output-format", "stream-json", "--verbose", "--", prompt]
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as lf:
        lf.write(json.dumps({"t": time.time(), "tag": tag, "model": model, "prompt": prompt[:200]}) + "\n")
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=HERE, stdin=subprocess.DEVNULL)
    secs = time.time() - t0
    calls, texts, result, opened = [], [], None, []
    for line in p.stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            for b in ev["message"].get("content", []):
                if b.get("type") == "tool_use":
                    name = b["name"].replace("mcp__lab__", "")
                    calls.append({"tool": name, "args": b.get("input") or {}, "t": round(time.time() - t0, 1)})
                    if name == "show_pictures":
                        opened += (b.get("input") or {}).get("ids", [])
                elif b.get("type") == "text" and b["text"].strip():
                    texts.append(b["text"])
        elif ev.get("type") == "result":
            result = ev
    answer = (result or {}).get("result") or (texts[-1] if texts else None)
    os.unlink(cfgp)
    return {"answer": answer, "calls": calls, "opened": list(dict.fromkeys(opened)), "secs": round(secs, 1),
            "duration_ms": (result or {}).get("duration_ms"), "cost_usd": (result or {}).get("total_cost_usd"),
            "is_error": (result or {}).get("is_error", p.returncode != 0), "stderr": p.stderr[-500:],
            "model": model}


def opus_memory_turn(question: str, index: Path, K: int | None, now: float, history=None, dog_status: str | None = None,
                     model: str = "opus", tag: str = "", stamp_time: bool = False) -> dict:
    """stamp_time: start the prompt with the replay's time. Needed because claude -p knows the real date: without it,
    Opus re-running a 2026-10-22 turn on 10-23 calls 10-22 "yesterday" (found 2026-10-23 02:20 on L03/L05). The 30
    generated questions ran without it (their answers were checked against the key; the status tool gives the time)."""
    key_parts = [question, str(index), K, now, history, dog_status, model] + (["stamped"] if stamp_time else [])
    key = hashlib.sha256(json.dumps(key_parts).encode()).hexdigest()[:20]
    cf = CACHE / f"{key}.json"
    if cf.exists():
        return dict(json.loads(cf.read_text()), cached=True)
    env = {"HIER_INDEX": str(index), "HIER_NOW": str(now)}
    if K is not None:
        env["HIER_K"] = str(K)
    if dog_status:
        env["HIER_DOG_STATUS"] = dog_status
    prompt = prompt_text(question, history)
    if stamp_time:
        from datetime import datetime
        prompt = (f"[Replay of a past conversation: the time now is {datetime.fromtimestamp(now):%a %Y-%m-%d %H:%M}; "
                  f"'today' means that day. The dog cannot be driven in this replay.]\n\n" + prompt)
    r = run_claude(prompt, env, model=model, tag=tag)
    r.update(question=question, K=K, now=now, stamp_time=stamp_time)
    if not r["is_error"] and r["answer"]:
        CACHE.mkdir(parents=True, exist_ok=True)
        cf.write_text(json.dumps(r, indent=1))
    return dict(r, cached=False)
