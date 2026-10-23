"""watch_for: while a blocking move runs in another thread, poll the console's /frame.jpg, ask the small VLM one
narrow yes/no question per frame, and send /agent/stop when k of the last n frames say yes. Returns the hit
frames, so the big model (or the 27B) confirms before anyone says "found".

    from llm import LLM
    from watch import FrameJudge, watch_for
    judge = FrameJudge(LLM("http://127.0.0.1:8301/v1"), "Is there a person wearing a teal t-shirt in this picture?")
    out = watch_for("http://127.0.0.1:8499", judge, during=lambda: post(console, "/agent/go_to", {...}))

`console` is required (no default) so nothing reaches the real console by accident: a URL on the real control PC
(172.17.40.64) is refused unless allow_real=True or HIER_ALLOW_REAL_CONSOLE=1 (for later live use; not tonight).
The yes score is P("yes") from the first answer token's log-probabilities (vLLM logprobs), thresholded at `thr`.
"""
from __future__ import annotations

import json
import math
import os
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from llm import LLM, image_part

REAL_CONSOLE_HOSTS = {"172.17.40.64"}
CLIENT = "cheetah-lab-watch"


def check_console(console: str, allow_real: bool = False) -> str:
    host = urlparse(console).hostname
    if host in REAL_CONSOLE_HOSTS and not (allow_real or os.environ.get("HIER_ALLOW_REAL_CONSOLE") == "1"):
        raise PermissionError(f"refusing to drive the real console {console} (allow_real=False)")
    return console.rstrip("/")


def http(console, method, path, body=None, timeout=5.0):
    data = json.dumps(dict(body or {}, client=CLIENT)).encode() if method == "POST" else None
    req = urllib.request.Request(console + path, data, {"Content-Type": "application/json"}, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        return r.status, (json.loads(raw) if raw[:1] in (b"{", b"[") else raw)


class FrameJudge:
    """One narrow yes/no question per frame to a small VLM. Returns {"p_yes", "yes", "secs", "answer"}."""

    def __init__(self, vlm: LLM, question: str, thr: float = 0.5, width: int = 640):
        self.vlm, self.question, self.thr, self.width = vlm, question, thr, width

    def __call__(self, jpg: bytes) -> dict:
        msgs = [{"role": "user", "content": [image_part(jpg, self.width),
                                             {"type": "text", "text": f"{self.question} Answer with one word: yes or no."}]}]
        r = self.vlm.chat(msgs, max_tokens=1, logprobs=True)
        p_yes, p_no = 0.0, 0.0
        for tok in ((r.get("logprobs") or [{}])[0].get("top_logprobs") or []):
            w = tok["token"].strip().lower()
            if w == "yes":
                p_yes += math.exp(tok["logprob"])
            elif w == "no":
                p_no += math.exp(tok["logprob"])
        p = p_yes / (p_yes + p_no) if p_yes + p_no > 0 else (1.0 if r["text"].strip().lower().startswith("yes") else 0.0)
        return {"p_yes": round(p, 4), "yes": p >= self.thr, "secs": r["secs"], "answer": r["text"].strip()}


def watch_for(console: str, judge: FrameJudge, during=None, k: int = 2, n: int = 3, hz: float = 3.0,
              max_s: float = 120.0, on_hit: str = "stop", allow_real: bool = False, out_dir: str | None = None) -> dict:
    """Run `during` (a blocking move, e.g. lambda: http(console, "POST", "/agent/go_to", {...}, timeout=200)) in a
    thread and watch frames until it returns, max_s passes, or k of the last n frames say yes (then POST
    /agent/stop if on_hit == "stop"). Without `during`, watch for max_s seconds."""
    console = check_console(console, allow_real)
    move = {"result": None, "error": None, "returned_at": None}
    t0 = time.time()

    def run_move():
        try:
            move["result"] = during()
        except Exception as e:  # noqa: BLE001
            move["error"] = f"{type(e).__name__}: {e}"
        move["returned_at"] = round(time.time() - t0, 3)

    th = None
    if during is not None:
        th = threading.Thread(target=run_move, daemon=True)
        th.start()
    frames, ring, hit, stop_at, stop_reply = [], [], None, None, None
    while time.time() - t0 < max_s:
        if th is not None and not th.is_alive():
            break
        tf = time.time()
        try:
            _, jpg = http(console, "GET", "/frame.jpg", timeout=2.0)
            t_frame = round(time.time() - t0, 3)
            j = judge(jpg)
        except Exception as e:  # noqa: BLE001 - a missed frame is not a reason to stop the dog
            frames.append({"t": round(tf - t0, 3), "error": f"{type(e).__name__}: {e}"})
            time.sleep(1.0 / hz)
            continue
        f = {"t": t_frame, "fetch_s": round(t_frame - (tf - t0), 3), **j, "jpg": jpg}
        frames.append(f)
        ring = (ring + [j["yes"]])[-n:]
        if sum(ring) >= k:
            hit = f
            if on_hit == "stop":
                try:
                    stop_reply = http(console, "POST", "/agent/stop", {}, timeout=5.0)[1]
                except Exception as e:  # noqa: BLE001
                    stop_reply = {"error": f"{type(e).__name__}: {e}"}
                stop_at = round(time.time() - t0, 3)
            break
        time.sleep(max(0.0, 1.0 / hz - (time.time() - tf)))
    if th is not None:
        th.join(timeout=30)
    hits = [f for f in frames[-n:] if f.get("yes")] if hit else []
    paths = []
    if out_dir and hits:
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        for i, f in enumerate(hits):
            p = Path(out_dir) / f"hit_{int(time.time())}_{i}.jpg"
            p.write_bytes(f["jpg"])
            paths.append(str(p))
    strip = lambda f: {k_: v for k_, v in f.items() if k_ != "jpg"}  # noqa: E731
    return {"hit": hit is not None, "stop_sent_at": stop_at, "stop_reply": stop_reply,
            "hit_frames": [strip(f) for f in hits], "hit_paths": paths, "hit_jpgs": [f["jpg"] for f in hits],
            "frames": [strip(f) for f in frames], "move": move, "secs": round(time.time() - t0, 3)}


CONFIRM_SCHEMA = {"type": "object", "properties": {"why": {"type": "string", "maxLength": 200},
                                                   "answer": {"type": "string", "enum": ["yes", "no"]}},
                  "required": ["why", "answer"]}


def confirm(big: LLM, question: str, jpgs: list[bytes]) -> dict:
    """The stronger model checks the hit frames before anything is reported as found."""
    content = [image_part(j, 960) for j in jpgs[:3]]
    content.append({"type": "text", "text": f"These are frames from a robot dog's camera. {question} "
                                            "Answer yes only if it is clearly visible in at least one frame."})
    r = big.chat([{"role": "user", "content": content}], schema=CONFIRM_SCHEMA, max_tokens=300)
    return dict(r["json"] or {}, secs=r["secs"])
