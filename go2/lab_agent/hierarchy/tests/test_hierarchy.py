"""End-to-end tests of the hierarchy against fake_console.py (no dog, nothing sent to the real console).

    python3 go2/lab_agent/hierarchy/tests/test_hierarchy.py [--small http://127.0.0.1:8301/v1]

Needs the small VLM server (8B on :8301). The big model is a stub that records what it was handed.
"""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import fake_console  # noqa: E402
from agent import ConsoleEnv, run_turn  # noqa: E402
from llm import LLM  # noqa: E402
from memtools import Memory  # noqa: E402
from tools import scan_for, watch_go_to  # noqa: E402
from watch import check_console  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--small", default="http://127.0.0.1:8301/v1")
ap.add_argument("--port", type=int, default=8496)
a = ap.parse_args()
LAB = json.load(open(HERE / "watch_data" / "labels.json"))
NEG = [f["id"] for f in LAB if f["teal"] == "0"][:30]
POS = [f["id"] for f in LAB if f["teal"] == "1"]
small = LLM(a.small)
mem = Memory.from_index(sorted((HERE / "replay" / "data").glob("index_snapshot_*.jsonl"))[0])
P = list(mem.P)
URL = f"http://127.0.0.1:{a.port}"
results = {}


def fresh(frames, **kw):
    srv, C = fake_console.serve(frames, a.port, **kw)
    return srv, C


def done(srv):
    srv.shutdown()
    srv.server_close()
    time.sleep(0.2)


def check(name, cond, info=""):
    results[name] = bool(cond)
    print(("PASS " if cond else "FAIL ") + name, info, flush=True)


# 0. the real console is refused
try:
    check_console("http://172.17.40.64:8080")
    check("real console refused", False)
except PermissionError:
    check("real console refused", True)

# 1. stop fast path: no model at all
srv, C = fresh(NEG)
bigcalls = []
out = run_turn("STOP!", ConsoleEnv(URL, mem), small, lambda t, h: bigcalls.append((t, h)) or "big", P)
check("stop fast path", out["tier"] == "none" and any(c["call"] == "POST stop" for c in C.calls) and not bigcalls,
      f"{out['secs']} s")
done(srv)

# 2. named place: the small model drives (go_to desk_kang), releases, answers
srv, C = fresh(NEG, go_to_s=2)
out = run_turn("Go to kang'desk", ConsoleEnv(URL, mem), small, lambda t, h: "big", P, mem.list_places())
gotos = [c for c in C.calls if c["call"] == "POST go_to"]
check("named place by small model", out["tier"] == "small" and gotos and gotos[0]["args"].get("place") == "desk_kang",
      f"{out['tier']} {[(s['tool'], s.get('args')) for s in out.get('small_steps', [])]} {out['secs']} s")
check("released after the move", any(c["call"] == "POST release" for c in C.calls))
done(srv)

# 3. no_route -> the whole turn goes to the big model with the transcript
srv, C = fresh(NEG, replies={"go_to": {"result": "no_route", "reason": "no route: the goal is not connected"}})
got = {}
out = run_turn("walk to oliver's desk", ConsoleEnv(URL, mem), small, lambda t, h: got.update(h=h) or "big answer", P,
               mem.list_places())
check("escalates on no_route", out["tier"] == "small->big" and "no_route" in (out.get("why") or ""),
      f"why: {out.get('why')}; go_to calls {sum(c['call'] == 'POST go_to' for c in C.calls)}")
check("no retry after no_route", sum(c["call"] == "POST go_to" for c in C.calls) == 1)
done(srv)

# 4. people question goes straight up
out = run_turn("how many people are in the lab right now", ConsoleEnv(URL, mem), small, lambda t, h: "big", P)
check("people -> big", out["tier"] == "big", out.get("why"))

# 5. watch_go_to: stop arrives while go_to blocks
frames = NEG[:6] + POS[:8] + NEG[6:20]
srv, C = fresh(frames, fps=1.0, go_to_s=40)
r = watch_go_to(URL, small, "a person wearing a teal t-shirt", place="desk_oliver", k=2, n=3, hz=3)
ret = next((c for c in C.calls if c["call"] == "go_to returned"), {})
stop_t = next((c["t"] for c in C.calls if c["call"] == "POST stop"), None)
check("watch_go_to stops mid-move", r["stopped_on_sight"] and ret.get("out", {}).get("result") == "aborted"
      and stop_t is not None and stop_t < 15, f"stop at {stop_t} s, first target frame at ~6 s, {r['frames_checked']} frames")
done(srv)

# 6. watch_go_to with no target: no stop, go_to completes
srv, C = fresh(NEG, fps=1.0, go_to_s=15)
r = watch_go_to(URL, small, "a person wearing a teal t-shirt", place="desk_oliver", k=2, n=3, hz=3, max_s=30)
check("watch_go_to no false stop", not r["stopped_on_sight"] and not any(c["call"] == "POST stop" for c in C.calls),
      f"{r['frames_checked']} frames")
done(srv)

# 7. scan_for: each turn advances the playlist by one frame; the target is in view 3
srv, C = fresh(NEG[:3] + POS[:4], fps=1.0, turn_s=1.0)
r = scan_for(URL, small, "a person wearing a teal t-shirt", step_deg=45, views=8, settle_s=0.1)
check("scan_for finds and stops turning", r["found"] and r["view"] == 3, f"view {r.get('view')}, {r['secs']} s")
done(srv)

print(json.dumps(results))
(HERE / "tests" / "last_results.json").write_text(json.dumps(results, indent=1))
sys.exit(0 if all(results.values()) else 1)
