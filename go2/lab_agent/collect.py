"""Data-collection log for the console page's Collect mode (Oliver, 2026-10-23).

Everything goes to go2/data/collection/events.jsonl, one JSON line per event, plus a camera frame per note in
go2/data/collection/frames/. The agent never reads this folder: notes typed here are hidden from it.

Event kinds (all carry t, iso, episode; most carry session, the agent conversation id, and turn, the prompt
number within the episode):
    episode   a new episode started (title)
    prompt    a message sent to the agent (text, expected: Oliver's hidden expectation, model)
    done      how that turn ended (ok, text, answer: the agent's reply, tools: tool calls in order, secs)
    note      a hidden side note (note_kind: fact | expected | behavior | other, text) with the map pose,
              localization state and a camera frame at that moment
    verdict   Oliver's grade of a turn (text: right | partly | wrong, optional comment)
    action    something Oliver did on the page (place button, STOP) and what came back

The full agent transcript for a session (every tool call and result) is in the Claude Code project folder
~/.claude/projects/-home-oliver-robot-dynamic-home-eqa-go2-lab-agent/<session>.jsonl and in
go2/data/lab_agent/chats/.
"""
from __future__ import annotations

import json
import re
import threading
import time
from pathlib import Path

DIR = Path(__file__).resolve().parents[1] / "data" / "collection"
LOG = DIR / "events.jsonl"
FRAMES = DIR / "frames"
_LOCK = threading.Lock()
KINDS = {"episode", "prompt", "done", "note", "verdict", "action"}


def clean_id(s, n=64):
    return re.sub(r"[^A-Za-z0-9_.:-]", "", str(s or ""))[:n]


def log(kind, episode, **fields):
    """Append one event; returns it."""
    if kind not in KINDS:
        raise ValueError(kind)
    t = time.time()
    ev = {"t": round(t, 3), "iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t)), "kind": kind,
          "episode": clean_id(episode), **fields}
    DIR.mkdir(parents=True, exist_ok=True)
    with _LOCK, LOG.open("a") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    return ev


def note(episode, body, frame=None, state=None):
    """A note from the page: keep the camera frame and robot state with it so it can be checked later."""
    kind = body.get("kind") if body.get("kind") in KINDS - {"prompt", "done"} else "note"
    fields = {k: body.get(k) for k in ("session", "turn", "note_kind", "text", "title", "tags", "comment")
              if body.get(k) not in (None, "", [])}
    for k in ("text", "title", "comment"):
        if k in fields:
            fields[k] = str(fields[k])[:4000]
    if state:
        fields["robot"] = state
    if frame:
        FRAMES.mkdir(parents=True, exist_ok=True)
        name = f"{int(time.time() * 1000)}.jpg"
        (FRAMES / name).write_bytes(frame)
        fields["frame"] = name
    return log(kind, episode, **fields)
