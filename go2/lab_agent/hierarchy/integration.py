"""How the lead plugs the hierarchy into server.py / web.py (2026-10-23). Nothing here is imported by them yet.

1. Skill tools for Opus in server.py (the first thing to turn on). At the end of server.py, before
   `if __name__ == "__main__":`, add:

       sys.path.insert(0, str(Path(__file__).parent / "hierarchy"))
       import integration
       integration.register(mcp, sys.modules[__name__])

   This adds two MCP tools that move the dog through server.py's own agent()/begin_move()/snap(), so claim,
   STOP_FLAG, calls.jsonl logging and photo indexing stay where they are:
     watch_go_to(query, place | x,y,yaw_deg, max_s, person)  go_to while the 8B watches ~3 frames/s; stop on 2-of-3
     scan_for(query, step_deg, views)                        turn in steps, 8B looks at each view, stop on a hit
   Add to SYSTEM.md, under "Driving the dog":
     - "Find <person or thing> and stop": use watch_go_to (walking) or scan_for (turning in place), not a chain of
       short moves. It stops the dog itself when the small vision model sees it; check the returned frames
       yourself before saying you found it.
   Needs: the 8B on the control PC (172.17.40.64:8000, board #32; :8301 on cheetah before 2026-10-23) and the 27B on :8300 for the confirm step.
   Env: HIER_SMALL_URL, HIER_MID_URL. The real console is allowed here (allow_real=True) because these run only
   when Opus calls them during a live turn.
   Unchecked on the dog: what /agent/go_to returns when /agent/stop arrives mid-way. server.py's agent() raises
   Refused on "aborted"; the watcher catches that in its move thread and reports "stopped on sight".

2. Router in web.py (stop fast path + named places to the 8B), in do_POST before launching claude:

       from router import classify; from agent import run_turn, handoff_text; import integration
       route = classify(text, list(M.places()))
       if route.name == "stop": emit("done", console_stop()); return        # web.py already does this for a
                                                                            # bare "stop" while busy; now always
       if route.tier == "small":
           out = run_turn(text, integration.ServerEnv(), SMALL, big=lambda t, h: None, place_ids=list(M.places()),
                          places_text=server.list_places())
           if out["tier"] == "small": emit("text", out["answer"]); emit("done", ...); return
           text = handoff_text(...) + "\n\nOliver: " + text       # then fall through to the usual claude -p turn
   (`out["handoff"]` already holds the handoff text.) Everything else keeps going to claude -p as today.

3. Not recommended yet: memory Q&A on the 8B (see the report: 0.43 alone vs 0.83 for Opus on 30 checked
   questions; with signals + 27B verify ~0.75-0.78 at ~55-60% Opus).
"""
from __future__ import annotations

import os
import re

from llm import LLM

SMALL_URL = os.environ.get("HIER_SMALL_URL", "http://172.17.40.64:8000/v1")   # control PC GPU 1 (board #32); was :8301 on cheetah
MID_URL = os.environ.get("HIER_MID_URL", "http://127.0.0.1:8300/v1")
PERSON = re.compile(r"\b(person|people|man|woman|someone|somebody|oliver|khang|kang|him|her|wearing|shirt|t-shirt)\b", re.I)


class ServerEnv:
    """The small agent's tools = server.py's own tool functions (photos indexed, STOP flag honoured)."""

    def __init__(self, server_module):
        self.S = server_module

    def call(self, tool, args):
        fn = getattr(self.S, tool, None)
        if fn is None:
            return f"ERROR: no tool {tool}", []
        out = fn(**{k: v for k, v in args.items() if v not in ("", None)})
        if not isinstance(out, list):
            return str(out), []
        text = "\n".join(o for o in out if isinstance(o, str))
        ids = re.findall(r"\[([tpl]\d{9,}(?:_\d+)?)\]", text)
        imgs = [o.data for o in out if hasattr(o, "data")]
        return text, [(ids[i] if i < len(ids) else f"img{i}", d) for i, d in enumerate(imgs)]


def register(mcp, S, small_url: str = SMALL_URL, mid_url: str = MID_URL):
    """Add watch_go_to and scan_for to server.py's MCP server. S = the server module."""
    import tools as T

    clients = {}

    def llm(url, name):
        """Connect on first use, not at import: LLM() asks the server for its model name, and server.py must still
        start (with all its other tools) when the 8B or 27B is down (lead, 2026-10-23)."""
        if name not in clients:
            clients[name] = LLM(url, name=name)
        return clients[name]

    def mid():
        try:
            return llm(mid_url, "mid")
        except Exception:  # noqa: BLE001 - the 27B confirm is optional; without it the frames go to Opus unchecked
            return None

    def small_ready():
        """Refuse before moving if the small VLM is not answering: otherwise the dog would walk the whole route
        with every frame check failing and nothing watching (lead, 2026-10-23)."""
        import urllib.request
        try:
            urllib.request.urlopen(small_url.rstrip("/") + "/models", timeout=3).read()
        except Exception as e:  # noqa: BLE001
            raise S.Refused(f"the small vision model at {small_url} is not answering ({type(e).__name__}), so nothing "
                            f"would watch the camera. It runs on the control PC (Docker go2_vlm, GPU 1): ask Oliver to check it, "
                            f"or use go_to / turn with photos instead.")

    def frames_out(r):
        return [S.small(j, 640) for j in r.get("_hit_jpgs", [])[:2]]

    @mcp.tool()
    @S.safe(moves=True)
    def watch_go_to(query: str, place: str = "", x: float | None = None, y: float | None = None,
                    yaw_deg: float | None = None, max_s: float = 120.0, person: bool | None = None) -> list:
        """Walk like go_to (a place id, or x, y, yaw_deg), while the local small vision model watches the camera
        about 3 times a second and stops the dog as soon as it sees `query` (e.g. 'a person wearing a teal
        t-shirt') in 2 of the last 3 frames. Returns whether it stopped on sight, the frames that triggered it
        (look at them yourself before saying you found it), and a photo from where the dog stopped."""
        small_ready()
        S.begin_move()
        args = {"place": place} if place else {"x": x, "y": y, **({"yaw_deg": yaw_deg} if yaw_deg is not None else {})}
        r = T.watch_go_to(S.M.CONSOLE, llm(small_url, "small"), query, k=2, n=3, hz=3.0, max_s=max_s, confirm_llm=mid(),
                          also_person=bool(PERSON.search(query)) if person is None else person, allow_real=True,
                          move=lambda: S.agent("go_to", timeout_s=120, **args))
        head = (f"watch_go_to {args} for '{query}': " + (
            f"STOPPED ON SIGHT after {r['stop_sent_at_s']} s ({r['frames_checked']} frames checked); 27B check of "
            f"the hit frames: {r.get('confirmed')}" if r["stopped_on_sight"] else
            f"not seen in {r['frames_checked']} frames; go_to ended: {r['move_result']}")) + (
            f" WARNING: {r['frame_errors']} frame checks failed, so parts of the route were not watched."
            if r.get("frame_errors") else "")
        rec, jpg = S.snap(source="photo")
        return [head, *frames_out(r), S.describe_rec(rec), S.small(jpg)]

    @mcp.tool()
    @S.safe(moves=True)
    def scan_for(query: str, step_deg: float = 45.0, views: int = 8) -> list:
        """Turn in place in steps of step_deg (up to `views` views); at each view the local small vision model
        looks for `query` and the turning stops at the first view where it sees it twice. Returns the view and
        the frames (check them yourself), plus a photo from where the dog faces now."""
        small_ready()
        S.begin_move()
        r = T.scan_for(S.M.CONSOLE, llm(small_url, "small"), query, step_deg=step_deg, views=max(1, min(8, views)), confirm_llm=mid(),
                       allow_real=True, turn=lambda deg: S.agent("turn", deg=deg))
        head = (f"scan_for '{query}': " + (f"seen at view {r['view']} (turned {r['turned_deg']} deg); 27B check: "
                                            f"{r.get('confirmed')}" if r["found"] else f"not seen in {len(r['views'])} views"))
        rec, jpg = S.snap(source="photo")
        return [head, *frames_out(r), S.describe_rec(rec), S.small(jpg)]

    return watch_go_to, scan_for
