"""One user turn through the hierarchy: rules route -> (stop fast path | small model with live escalation | big).

    from agent import run_turn, ConsoleEnv
    env = ConsoleEnv(console="http://127.0.0.1:8499", memory=Memory.from_index(...))   # console is required
    out = run_turn("walk to kang's desk", env, small=LLM("http://127.0.0.1:8301/v1"), big=my_big)

`big(text, handoff)` runs the big model on the turn and returns its answer; `handoff` is None (routed straight up)
or a dict with the reason and what the small model did so far (calls, results, picture ids it opened), to pass on
as context: the whole remaining turn goes up, not one step. In web.py that is claude -p (see INTEGRATION.md).
"""
from __future__ import annotations

import json
import time

from llm import LLM
from router import Monitor, classify
from small_agent import MOVES, SmallAgent
from watch import check_console, http


class ConsoleEnv:
    """The small model's driving tools against a console base URL (required). Mirrors server.py's go_to / turn /
    move / photo / stop / release / status, but does not index photos into the memory (tests must not write to
    go2/data/lab_agent); memory tools come from an optional memtools.Memory."""

    def __init__(self, console: str, memory=None, allow_real: bool = False, stop_flag=None):
        self.console = check_console(console, allow_real)
        self.m = memory
        self.stop_flag = stop_flag          # a callable -> True while STOP is pressed (server.py's STOP_FLAG)

    def post(self, name, args=None, timeout=200):
        return http(self.console, "POST", f"/agent/{name}", args or {}, timeout=timeout)[1]

    def call(self, tool, args):
        try:
            if tool in MOVES and self.stop_flag and self.stop_flag():
                return "REFUSED: STOP was pressed: no more moves until Oliver sends a new message", []
            if tool == "stop":
                return json.dumps(self.post("stop", timeout=5)), []
            if tool == "release":
                return json.dumps(self.post("release", timeout=5)), []
            if tool == "status":
                st = http(self.console, "GET", "/agent/status")[1]
                s = http(self.console, "GET", "/state.json")[1]
                return f"console up. map: {(s.get('map') or {}).get('mode')}. dog at {s.get('map_pose')}. control owner: {st.get('owner')}", []
            if tool == "list_places":
                return (self.m.list_places() if self.m else "no places"), []
            if tool in ("go_to", "turn", "move", "photo", "look_around"):
                self.post("claim", timeout=5)
                if tool == "go_to":
                    a = {"place": args["place"]} if args.get("place") else {k: args[k] for k in ("x", "y", "yaw_deg") if args.get(k) is not None}
                    r = self.post("go_to", dict(a, timeout_s=120))
                    head = f"go_to {a}: {r.get('result')} {r.get('reason') or ''}; moved {r.get('moved_m')} m"
                elif tool == "turn":
                    r = self.post("turn", {"deg": args["deg"]})
                    head = f"turn {args['deg']}: {r.get('result')} {r.get('reason') or ''}"
                elif tool == "move":
                    m = max(-1.0, min(1.5, float(args["metres"])))
                    r = self.post("move", {"m": m})
                    head = f"move {m}: {r.get('result')} {r.get('reason') or ''}"
                else:
                    head = tool
                    r = {}
                ph = self.post("photo")
                p = ph.get("photo") or {}
                jpg = http(self.console, "GET", p["url"])[1] if p.get("url") else None
                if r.get("result") in ("refused", "aborted"):
                    head = f"REFUSED: the console {r.get('result')} {tool}: {r}. Not retrying."
                return head, ([(p.get("id", "photo"), jpg)] if isinstance(jpg, bytes) else [])
            if self.m is not None and tool in ("search_memory", "show_pictures", "people_seen"):
                from small_agent import MemEnv
                return MemEnv(self.m).call(tool, args)
            if tool == "ask_expert":
                return "handing over to the expert", []
            return f"ERROR: {tool} is not available", []
        except Exception as e:  # noqa: BLE001
            if tool in MOVES:
                try:
                    self.post("stop", timeout=5)
                except Exception:  # noqa: BLE001
                    pass
                return f"ERROR (sent stop): {type(e).__name__}: {e}", []
            return f"ERROR: {type(e).__name__}: {e}", []


def handoff_text(h: dict) -> str:
    """The context the big model gets when a turn is escalated mid-way."""
    lines = [f"A smaller model started on this request and handed it to you because: {h['reason']}.",
             "What it did so far (do not repeat moves that already failed):"]
    for s in h["steps"]:
        if s.get("tool") and s["tool"] != "answer":
            lines.append(f"- {s['tool']} {json.dumps(s.get('args'))} -> {(s.get('result') or '')[:300]}")
    if h.get("opened"):
        lines.append(f"Pictures it looked at: {', '.join(h['opened'])}")
    lines.append("Continue from here.")
    return "\n".join(lines)


def run_turn(text: str, env, small: LLM, big, place_ids: list[str], places_text: str = "", history=None,
             now: float | None = None, max_steps: int = 4, answer_rule: str = "neg_ok", stop_fn=None) -> dict:
    t0 = time.time()
    route = classify(text, place_ids)
    if route.name == "stop":
        reply = (stop_fn or (lambda: env.call("stop", {})[0]))()
        return {"route": route.name, "tier": "none", "answer": f"Stopped. ({reply})", "secs": round(time.time() - t0, 3)}
    if route.tier == "big":
        return {"route": route.name, "why": route.why, "tier": "big", "answer": big(text, None),
                "secs": round(time.time() - t0, 3)}
    mon = Monitor(route, max_steps=max_steps, stop_on_signal=True, answer_rule=answer_rule)
    ag = SmallAgent(small, env, route.tools, max_steps=max_steps + 2, place_ids=place_ids, places_text=places_text,
                    now=now, on_step=mon.on_step, prompt="v2")
    tr = ag.run(text, history)
    if mon.escalated or not tr["answer"]:
        h = {"reason": mon.reason or "no answer", "steps": tr["steps"], "opened": tr["opened"]}
        return {"route": route.name, "tier": "small->big", "why": h["reason"], "small_steps": tr["steps"],
                "answer": big(text, h), "handoff": handoff_text(h), "secs": round(time.time() - t0, 3)}
    return {"route": route.name, "tier": "small", "answer": tr["answer"]["text"], "small_steps": tr["steps"],
            "secs": round(time.time() - t0, 3)}
