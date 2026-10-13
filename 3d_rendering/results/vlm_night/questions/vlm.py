"""Small client for the local vision model (Qwen3.8-27B on vLLM, port 8300).

    ask(prompt, images=[path, ...], think=False, schema=None) -> (text, info)
Images go in as base64 JPEG data URLs, in the order given, each preceded by its caption
when captions are passed. Temperature 0. Results are cached on disk by request hash, so a
rerun of a script only pays for new calls (note: vLLM at temperature 0 is not fully
deterministic across server restarts, so cached and fresh answers can differ slightly).
"""
from __future__ import annotations

import base64
import hashlib
import json
import pathlib
import time
import urllib.request

URL = "http://127.0.0.1:8300/v1/chat/completions"
MODEL = "Qwen/Qwen3.8-27B"
CACHE = pathlib.Path(__file__).parent / "cache"
CACHE.mkdir(exist_ok=True)


def _img(path) -> dict:
    data = base64.b64encode(pathlib.Path(path).read_bytes()).decode()
    return {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{data}"}}


def ask(prompt: str, images=(), captions=None, think: bool = False, schema: dict | None = None,
        max_tokens: int = 2048, system: str | None = None):
    content = []
    for i, p in enumerate(images):
        if captions:
            content.append({"type": "text", "text": captions[i]})
        content.append(_img(p))
    content.append({"type": "text", "text": prompt})
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": content}]
    body = {"model": MODEL, "messages": msgs, "temperature": 0.0, "max_tokens": max_tokens,
            "chat_template_kwargs": {"enable_thinking": think}}
    if schema:
        body["response_format"] = {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}}
    key = hashlib.sha256(json.dumps([body["messages"][-1]["content"][-1], [(str(p), pathlib.Path(p).stat().st_mtime_ns, pathlib.Path(p).stat().st_size) for p in images], captions,
                                     think, schema, max_tokens, system, prompt]).encode()).hexdigest()[:24]
    f = CACHE / f"{key}.json"
    if f.exists():
        r = json.loads(f.read_text())
        return r["text"], r["info"]
    t0 = time.time()
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            out = json.loads(urllib.request.urlopen(req, timeout=3600).read())
            break
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                raise
            time.sleep(5)
    msg = out["choices"][0]["message"]
    text = msg.get("content") or ""
    info = {"seconds": round(time.time() - t0, 2), "usage": out.get("usage"),
            "reasoning": (msg.get("reasoning_content") or msg.get("reasoning") or "")[:4000],
            "finish": out["choices"][0].get("finish_reason")}
    f.write_text(json.dumps({"text": text, "info": info}))
    return text, info


def yes_no(prompt, images=(), captions=None):
    """A yes/no answer forced by the output grammar. An earlier version read the first word of a
    free reply with max_tokens=5; the model often began 'Based on a careful examination...',
    which was cut off and read as 'no' (49 of 60 looks at the right furniture)."""
    schema = {"type": "object", "properties": {"answer": {"type": "string", "enum": ["yes", "no"]}},
              "required": ["answer"]}
    text, _ = ask(prompt, images, captions=captions, schema=schema, max_tokens=30)
    try:
        return json.loads(text)["answer"] == "yes"
    except Exception:  # noqa: BLE001
        return None


def choice(prompt, letters, images=(), captions=None):
    schema = {"type": "object", "properties": {"answer": {"type": "string", "enum": list(letters)}},
              "required": ["answer"]}
    text, _ = ask(prompt, images, captions=captions, schema=schema, max_tokens=30)
    try:
        return json.loads(text)["answer"]
    except Exception:  # noqa: BLE001
        return None
