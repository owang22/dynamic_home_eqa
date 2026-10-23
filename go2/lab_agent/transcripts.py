"""Export the lab agent's conversations to readable files, for study.

    python3 go2/lab_agent/transcripts.py            # all conversations -> go2/data/lab_agent/chats/

Every agent turn (phone page, console page, chat.sh) is a Claude Code session; Claude Code keeps its full
transcript under ~/.claude/projects/-home-oliver-robot-dynamic-home-eqa-go2-lab-agent/<session>.jsonl. This writes,
per session, <date>_<start>_<session8>.md (what Oliver typed, what the agent said, every tool call with its
arguments, the text part of every tool result, pictures by id) and the same as .json (one event per line item) for
analysis, and keeps a copy of the raw transcript in chats/raw/ (Claude Code deletes its own after about 30 days).
Pictures stay in go2/data/lab_agent/pictures/ under the ids the transcript names. web.py runs this after every
agent turn.
"""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

SRC = Path.home() / ".claude" / "projects" / "-home-oliver-robot-dynamic-home-eqa-go2-lab-agent"
OUT = Path(__file__).resolve().parents[1] / "data" / "lab_agent" / "chats"
SYSTEM_START = "<system-reminder>"


def local(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()


def events(path):
    """[(time, kind, text, extra)] in order: kind = oliver | agent | tool | result."""
    out = []
    for line in path.read_text().splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") not in ("user", "assistant") or "message" not in e:
            continue
        t = local(e["timestamp"]) if e.get("timestamp") else None
        c = e["message"].get("content")
        if isinstance(c, str):
            if e["type"] == "user" and not c.startswith(SYSTEM_START):
                out.append((t, "oliver", c, None))
            continue
        for b in c or []:
            if b.get("type") == "text" and b["text"].strip():
                if e["type"] == "assistant":
                    out.append((t, "agent", b["text"], None))
                elif not b["text"].startswith(SYSTEM_START):
                    out.append((t, "oliver", b["text"], None))
            elif b.get("type") == "tool_use":
                out.append((t, "tool", b["name"].replace("mcp__lab__", ""), b.get("input")))
            elif b.get("type") == "tool_result":
                rc = b.get("content")
                if isinstance(rc, list):
                    txt = "\n".join(x.get("text", "") for x in rc if x.get("type") == "text")
                    n_img = sum(x.get("type") == "image" for x in rc)
                else:
                    txt, n_img = str(rc), 0
                out.append((t, "result", txt, {"images": n_img}))
    return out


def to_md(sid, ev):
    first = next((t for t, *_ in ev if t), None)
    lines = [f"# Lab agent conversation {sid}", "", f"Started {first:%a %Y-%m-%d %H:%M:%S}" if first else "", ""]
    for t, kind, text, extra in ev:
        hhmm = f"{t:%H:%M:%S}" if t else "--:--:--"
        if kind == "oliver":
            lines += [f"## {hhmm} Oliver", "", text, ""]
        elif kind == "agent":
            lines += [f"**{hhmm} agent:**", "", text, ""]
        elif kind == "tool":
            lines += [f"- `{hhmm}` tool **{text}** `{json.dumps(extra, ensure_ascii=False)}`"]
        else:
            short = text if len(text) < 1200 else text[:1200] + f" ... ({len(text)} chars)"
            img = f" [+{extra['images']} picture(s)]" if extra and extra.get("images") else ""
            lines += ["  - result" + img + ":", "", "    " + short.replace("\n", "\n    "), ""]
    return "\n".join(lines)


def main(quiet=False):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "raw").mkdir(exist_ok=True)
    for p in sorted(SRC.glob("*.jsonl")):
        raw = OUT / "raw" / p.name
        if raw.exists() and raw.stat().st_mtime >= p.stat().st_mtime:
            continue
        shutil.copy2(p, raw)
        ev = events(p)
        if not any(k == "oliver" for _, k, *_ in ev):
            continue
        first = next((t for t, *_ in ev if t), None)
        stem = f"{first:%Y-%m-%d_%H%M}_{p.stem[:8]}" if first else p.stem[:8]
        (OUT / f"{stem}.md").write_text(to_md(p.stem, ev))
        (OUT / f"{stem}.json").write_text(json.dumps(
            [{"t": t.isoformat() if t else None, "kind": k, "text": x, "extra": e} for t, k, x, e in ev],
            ensure_ascii=False, indent=0))
        n = {k: sum(1 for _, kk, *_ in ev if kk == k) for k in ("oliver", "agent", "tool")}
        if not quiet:
            print(f"{stem}: {n['oliver']} messages from Oliver, {n['agent']} agent replies, {n['tool']} tool calls")


if __name__ == "__main__":
    main()
