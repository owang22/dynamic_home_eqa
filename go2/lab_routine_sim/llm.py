"""Client for the local Qwen3.8-27B (vLLM on 127.0.0.1:8300, started by serve_qwen.sh). Temperature 0, no cache:
a rerun is a real rerun. Returns (parsed JSON or None, info)."""
from __future__ import annotations

import json
import time
import urllib.request

URL = "http://127.0.0.1:8300/v1/chat/completions"
MODEL = "Qwen/Qwen3.8-27B"


class ServerDown(RuntimeError):
    pass


def ask_json(system: str, prompt: str, schema: dict, think: bool = True, max_tokens: int = 12000):
    body = {"model": MODEL, "temperature": 0.0, "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "chat_template_kwargs": {"enable_thinking": think},
            "response_format": {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}}}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    t0 = time.time()
    for attempt in range(8):
        try:
            out = json.loads(urllib.request.urlopen(req, timeout=3600).read())
            break
        except Exception as e:  # noqa: BLE001 - server busy or restarting
            if attempt == 7:
                # not a model answer: raise, so the day is not saved and a resume redoes it
                raise ServerDown(repr(e)) from e
            time.sleep(15 * (attempt + 1))
    ch = out["choices"][0]
    text = ch["message"].get("content") or ""
    reasoning = ch["message"].get("reasoning_content") or ch["message"].get("reasoning") or ""
    info = {"seconds": round(time.time() - t0, 1), "usage": out.get("usage"), "finish": ch.get("finish_reason"),
            "reasoning": reasoning[-3000:]}
    try:
        return json.loads(text), info
    except Exception:  # noqa: BLE001 - truncated or not JSON
        info["bad_text"] = text[:2000]
        return None, info


def _post(body):
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    for attempt in range(8):
        try:
            return json.loads(urllib.request.urlopen(req, timeout=3600).read())
        except Exception as e:  # noqa: BLE001
            if attempt == 7:
                raise ServerDown(repr(e)) from e
            time.sleep(15 * (attempt + 1))


def ask_json_budget(system: str, prompt: str, schema: dict, think_budget: int = 4000, answer_tokens: int = 7000):
    """Thinking capped at think_budget tokens: think freely up to the cap, then close the thinking and answer under
    the JSON grammar (the usual Qwen budget method). Unthinking Qwen writes 'X is at its last place'; unbudgeted
    thinking took 15-25k tokens a call (DESIGN.md)."""
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
    t0 = time.time()
    o1 = _post({"model": MODEL, "messages": msgs, "max_tokens": think_budget, "temperature": 0.0,
                "chat_template_kwargs": {"enable_thinking": True}})
    m1 = o1["choices"][0]["message"]
    thought = (m1.get("reasoning_content") or m1.get("reasoning") or "").strip()
    cut = o1["choices"][0].get("finish_reason") == "length"
    pre = "<think>\n" + thought + ("\n\nI have to stop thinking and give the answer now." if cut else "") + "\n</think>\n\n"
    o2 = _post({"model": MODEL, "messages": msgs + [{"role": "assistant", "content": pre}], "max_tokens": answer_tokens,
                "temperature": 0.0, "continue_final_message": True, "add_generation_prompt": False,
                "chat_template_kwargs": {"enable_thinking": True},
                "response_format": {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}}})
    m2 = o2["choices"][0]["message"]
    text = m2.get("content") or m2.get("reasoning_content") or m2.get("reasoning") or ""  # no </think> in the answer
    info = {"seconds": round(time.time() - t0, 1), "think_tokens": (o1.get("usage") or {}).get("completion_tokens"),
            "thinking_cut": cut, "usage": o2.get("usage"), "finish": o2["choices"][0].get("finish_reason"),
            "reasoning": thought[-3000:]}
    try:
        return json.loads(text), info
    except Exception:  # noqa: BLE001
        info["bad_text"] = text[:2000]
        return None, info
