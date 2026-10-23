"""Turn the logged Opus conversations (go2/data/lab_agent/chats/*.json) into replay cases.

    python3 go2/lab_agent/hierarchy/replay/build_cases.py   -> replay/cases_logged.json

Each case: the user turn, the earlier turns of the same conversation (question + Opus's final answer), Opus's tool
calls with their results and pictures, Opus's answer and time, and K = how many lines of index.jsonl made up the
memory at that moment. K was found by replaying every logged search_memory / people_seen call against each line
prefix of the index snapshot: 23 of 24 calls reproduce the logged text exactly at one K (calib, 2026-10-23 00:20;
"PC case RGB lighting" matches no prefix). Turns without a memory call take the K of the nearest calibrated turn.
"""
from __future__ import annotations

import glob
import json
import re
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHATS = HERE.parents[2] / "data" / "lab_agent" / "chats"
PIC = re.compile(r"\b([tpl]\d{9,}(?:_\d+)?)\b")

# turn start (HH:MM:SS) -> (kind, K, note)
TURNS = {
    "15:35:11": ("memory", 104, "computer tower"),
    "15:36:34": ("memory", 180, "people on Monday"),
    "15:47:49": ("memory", 704, "grey backpack"),
    "15:48:56": ("memory", 724, "busy day (people_seen matches K 720-764)"),
    "15:56:51": ("memory", 897, "near the sofa"),
    "16:10:26": ("driving", 959, "walk to oliver's desk"),
    "16:12:11": ("driving", 959, "back up to look at oliver"),
    "16:13:07": ("driving", 959, "walk to yuyang's desk"),
    "16:14:44": ("memory", 958, "shirt colour (no tool call; answered from the conversation)"),
    "16:15:06": ("memory", 959, "how many people now (people_seen matches K 958-1000)"),
    "16:15:37": ("memory", 959, "red screwdriver"),
    "16:16:24": ("driving", 959, "blue roll of tape"),
    "16:18:44": ("driving", 1070, "find oliver, stop, lie down"),
    "16:20:18": ("driving", 1070, "find oliver again"),
    "16:22:17": ("memory", 1070, "relocalize question"),
    "16:24:55": ("driving", 1070, "go find oliver and stop"),
    "16:35:45": ("driving", 1070, "go to kang's desk (log ends at the go_to call)"),
}


def ts(s):
    return datetime.fromisoformat(s).timestamp()


def result_text(e):
    t = e["text"]
    if t.startswith('{"result"'):
        try:
            return json.loads(t)["result"]
        except json.JSONDecodeError:
            pass
    return t


def main():
    cases = []
    for f in sorted(glob.glob(str(CHATS / "*.json"))):
        ev = json.load(open(f))
        session = Path(f).stem
        history = []
        turns, cur = [], None
        for e in ev:
            if e["kind"] == "oliver":
                cur = {"text": e["text"], "t": ts(e["t"]), "hhmmss": e["t"][11:19], "events": []}
                turns.append(cur)
            elif cur:
                cur["events"].append(e)
        for tu in turns:
            kind, K, note = TURNS[tu["hhmmss"]]
            calls, pending, agent_texts = [], [], []
            for e in tu["events"]:
                if e["kind"] == "tool":
                    c = {"tool": e["text"], "args": e["extra"] or {}, "t": ts(e["t"]), "result": None, "pics": []}
                    calls.append(c)
                    pending.append(c)
                elif e["kind"] == "result" and pending:
                    c = pending.pop(0)
                    c["result"] = result_text(e)
                    c["pics"] = list(dict.fromkeys(PIC.findall(c["result"]))) if (e.get("extra") or {}).get("images") else []
                    c["t_result"] = ts(e["t"])
                elif e["kind"] == "agent":
                    agent_texts.append({"t": ts(e["t"]), "text": e["text"]})
            answer = agent_texts[-1]["text"] if agent_texts and (not calls or agent_texts[-1]["t"] >= calls[-1]["t"]) else None
            end = max([a["t"] for a in agent_texts] + [c.get("t_result", c["t"]) for c in calls] + [tu["t"]])
            opened = []
            for c in calls:
                if c["tool"] == "show_pictures":
                    opened += c["args"].get("ids", [])
                opened += c["pics"]
            cited = list(dict.fromkeys(PIC.findall(answer or "")))
            cases.append({"id": f"L{len(cases) + 1:02d}", "session": session, "kind": kind, "note": note,
                          "text": tu["text"], "t": tu["t"], "time": tu["hhmmss"], "K": K,
                          "history": list(history), "opus_calls": calls, "opus_answer": answer,
                          "opus_secs": round(end - tu["t"], 1), "opus_opened": list(dict.fromkeys(opened)),
                          "opus_cited": cited, "interim_texts": [a["text"] for a in agent_texts[:-1]]})
            history.append((tu["text"], answer or "(no answer logged)"))
    out = HERE / "cases_logged.json"
    out.write_text(json.dumps(cases, indent=1))
    print(f"{len(cases)} turns, {sum(len(c['opus_calls']) for c in cases)} tool calls -> {out}")
    for c in cases:
        print(c["id"], c["kind"], c["time"], len(c["opus_calls"]), "calls", c["opus_secs"], "s", c["text"][:50])


if __name__ == "__main__":
    main()
