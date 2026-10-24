"""Skill tools for the big model (Opus or the 27B) that run the small model locally, written so the lead can
register them in server.py later (see INTEGRATION.md). Every function takes the console base URL as a required
argument; watch.check_console refuses the real control PC unless allow_real / HIER_ALLOW_REAL_CONSOLE=1.

  watch_go_to(console, small, query, place=..., or x/y/yaw_deg)  go_to while the 8B watches frames; stop on k-of-n
  scan_for(console, small, query, step_deg=45, views=8)        turn in steps, 8B looks at each view, stop on a hit
  verify_pictures(small, jpgs_by_id, question)                 yes/no + P(yes) per remembered picture
  ask_expert(...)                                              see agent.py (the small model's way up)

The 8B never reports "found" alone: watch_go_to and scan_for return the hit frames, and with `confirm_llm` the
27B checks them (watch.confirm) before the result says confirmed.
"""
from __future__ import annotations

import time

from llm import LLM
from watch import FrameJudge, check_console, confirm, http, watch_for


def _q(query: str) -> str:
    q = query.strip().rstrip("?")
    return q + "?" if q.lower().startswith(("is ", "are ", "does ", "do ", "can ")) else f"Is there {q} in this picture?"


def watch_go_to(console: str, small: LLM, query: str, place: str = "", x: float | None = None, y: float | None = None,
                yaw_deg: float | None = None, k: int = 2, n: int = 3, hz: float = 3.0, max_s: float = 150.0,
                confirm_llm: LLM | None = None, also_person: bool = False, allow_real: bool = False,
                move=None) -> dict:
    """Walk (go_to) and stop as soon as the small VLM sees `query` in k of the last n frames.
    move: optional callable doing the blocking go_to (server.py passes its own agent("go_to", ...) so claim,
    STOP flag and logging stay in one place); default: POST {console}/agent/go_to directly."""
    console = check_console(console, allow_real)
    args = {"place": place} if place else {"x": x, "y": y, **({"yaw_deg": yaw_deg} if yaw_deg is not None else {})}
    if move is None:
        def move():
            return http(console, "POST", "/agent/go_to", dict(args, timeout_s=120), timeout=max_s + 10)[1]
    judge = FrameJudge(small, _q(query))
    if also_person:          # the AND rule: cuts static false hits (watch_eval: red-shirt control 3 -> 1 false stops)
        pj = FrameJudge(small, "Is there a person in this picture?")
        inner = judge

        def judge(jpg):  # noqa: F811
            a = inner(jpg)
            if a["yes"]:
                b = pj(jpg)
                a = dict(a, yes=b["yes"], p_person=b["p_yes"], secs=a["secs"] + b["secs"])
            return a
    out = watch_for(console, judge, during=move, k=k, n=n, hz=hz, max_s=max_s, allow_real=allow_real)
    res = {"query": query, "go_to": args, "stopped_on_sight": out["hit"], "stop_sent_at_s": out["stop_sent_at"],
           "move_result": out["move"]["result"],
           "frames_checked": sum("error" not in f for f in out["frames"]),     # judged by the small VLM
           "frame_errors": sum("error" in f for f in out["frames"]),           # frame fetch or VLM call failed
           "hit_frames": out["hit_frames"], "secs": out["secs"]}
    if out["hit"] and confirm_llm is not None:
        res["confirmed"] = confirm(confirm_llm, _q(query), out["hit_jpgs"])
    res["_hit_jpgs"] = out["hit_jpgs"]
    return res


def scan_for(console: str, small: LLM, query: str, step_deg: float = 45.0, views: int = 8, settle_s: float = 0.6,
             confirm_llm: LLM | None = None, allow_real: bool = False, turn=None) -> dict:
    """Turn in place in steps; at each stop the small VLM looks at two frames; stop turning on a double yes."""
    console = check_console(console, allow_real)
    judge = FrameJudge(small, _q(query))
    if turn is None:
        def turn(deg):
            return http(console, "POST", "/agent/turn", {"deg": deg}, timeout=60)[1]
    seen, t0 = [], time.time()
    for i in range(views):
        if i:
            turn(step_deg)
        time.sleep(settle_s)
        js = []
        for _ in range(2):
            _, jpg = http(console, "GET", "/frame.jpg", timeout=2.0)
            js.append((judge(jpg), jpg))
            time.sleep(0.25)
        seen.append({"view": i, "turned_deg": i * step_deg, "p_yes": [j["p_yes"] for j, _ in js]})
        if all(j["yes"] for j, _ in js):
            res = {"found": True, "view": i, "turned_deg": i * step_deg, "views": seen, "secs": round(time.time() - t0, 2),
                   "_hit_jpgs": [jpg for _, jpg in js]}
            if confirm_llm is not None:
                res["confirmed"] = confirm(confirm_llm, _q(query), res["_hit_jpgs"])
            return res
    return {"found": False, "views": seen, "secs": round(time.time() - t0, 2)}


def verify_pictures(small: LLM, jpgs_by_id: dict[str, bytes], question: str) -> list[dict]:
    """The 8B answers one yes/no question per picture: [{id, yes, p_yes, secs}]."""
    judge = FrameJudge(small, _q(question))
    return [{"id": i, **judge(j)} for i, j in jpgs_by_id.items()]
