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

live.jsonl (same folder) holds every event the agent streams for a turn that has an episode (the prompt, then
each note, tool call, tool result (cut to 4 kB), reply, picture list and the end), one line each with the turn's
id (tid), so the console page's Monitor view can show a turn live, whoever sent it (read_live below).

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
LIVE = DIR / "live.jsonl"
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


def live(**fields):
    """Append one streamed event of a turn to live.jsonl (web.py, for the Monitor view). Never raises."""
    try:
        import fcntl
        t = time.time()
        line = json.dumps({"t": round(t, 3), **fields}, ensure_ascii=False) + "\n"
        DIR.mkdir(parents=True, exist_ok=True)
        with _LOCK, LIVE.open("a") as f:           # flock too: web.py and console_page.py both write here
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(line)
            fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as e:  # noqa: BLE001 - the Monitor log must never break a turn
        print("live log failed:", e, flush=True)


def _tail(path, since, window, cap):
    """(complete lines after byte offset `since`, next offset, cut). since < 0, or past the end (file moved or
    replaced): start `window` bytes before the end, at a line start. At most `cap` bytes per call."""
    try:
        size = path.stat().st_size
    except FileNotFoundError:
        return [], 0, False
    cut = False
    if since < 0 or since > size:
        since = max(0, size - window)
        cut = since > 0
    if since == size:
        return [], size, cut
    with path.open("rb") as f:
        if since > 0:                               # land on a line start
            f.seek(since - 1)
            if f.read(1) != b"\n":
                f.readline()
        start = f.tell()
        buf = f.read(cap)
    end = buf.rfind(b"\n") + 1                      # only whole lines; a half-written one waits for the next call
    out = []
    for ln in buf[:end].splitlines():
        try:
            out.append(json.loads(ln))
        except ValueError:
            pass
    return out, start + end, cut


def read_live(since=-1, esince=-1):
    """The Monitor view's poll: new live.jsonl events after byte offset `since`, and new hidden notes and grades
    (note, verdict) from events.jsonl after `esince`. A first call (-1) gets the last ~600 kB / 300 kB."""
    ev, nxt, cut = _tail(LIVE, since, 600_000, 1_000_000)
    notes, enxt, ecut = _tail(LOG, esince, 300_000, 1_000_000)
    notes = [{k: v for k, v in n.items() if k != "robot"} for n in notes if n.get("kind") in ("note", "verdict")]
    return {"events": ev, "next": nxt, "notes": notes, "enext": enxt, "cut": cut or ecut}
