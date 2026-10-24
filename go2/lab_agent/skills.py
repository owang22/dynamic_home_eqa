"""Skills the lab agent writes for itself (Oliver, 2026-10-23: "let the agent draft its own functions and methods
like watch_go_to").

A skill is a short Python function `def run(robot, ...)` that Opus writes with write_skill, checks with test_skill
(a dry run against a pretend robot: nothing moves) and runs on the dog with run_skill. The `robot` object only
offers the same calls the agent's own tools use: go_to, turn, move, look, photo, ask (a yes/no question to the
small vision model about the current camera frame), watch_go_to, scan_for, pose, places, search_memory, sleep,
log. Every move goes through server.py's agent(): claim, the STOP flag, calls.jsonl logging, and the console's own
obstacle avoidance and speed cap all still apply, so a skill can do nothing a chain of tool calls could not. A
skill run has a time limit (max_s, at most 300 s); going over it, an error, or STOP ends the run and sends stop.

The code check is a guard against mistakes, not a security sandbox: no imports except a few pure modules (math,
random, statistics, json, re, itertools, collections), no file or network access by name, no names starting with
an underscore. The author is the lab agent itself.

Stored in go2/data/lab_agent/skills/<name>/: v<N>.py for each version and meta.json (description, versions with
the reason for each, every run with its arguments, result and outcome notes). Old versions are kept.
"""
from __future__ import annotations

import ast
import builtins
import json
import re
import sys
import threading
import time
from pathlib import Path

import memory as M

DIR = M.DATA / "skills"
NAME = re.compile(r"[a-z][a-z0-9_]{1,40}")
ALLOWED_IMPORTS = {"math", "random", "statistics", "json", "re", "itertools", "collections"}
BANNED = {"open", "exec", "eval", "compile", "__import__", "globals", "locals", "vars", "getattr", "setattr",
          "delattr", "input", "breakpoint", "exit", "quit", "memoryview", "help", "dir", "type", "object"}
SAFE_BUILTINS = {k: getattr(builtins, k) for k in (
    "abs all any bool dict enumerate filter float frozenset int isinstance len list map max min range "
    "reversed round set sorted str sum tuple zip divmod pow repr Exception ValueError RuntimeError KeyError "
    "IndexError TypeError StopIteration ZeroDivisionError True False None").split()}
MAX_S = 300.0
DRY_WALL_S = 10.0         # a dry run gets 10 s of real time and at most 2000 calls
DRY_MAX_CALLS = 2000
DRY_SECS = {"go_to": 15.0, "watch_go_to": 15.0, "scan_for": 10.0, "turn": 3.0, "move": 3.0, "look": 0.5,
            "photo": 1.5, "ask": 0.3, "search_memory": 0.3}   # pretend durations, so time limits work in dry runs


class SkillTimeout(Exception):
    pass


class SkillError(Exception):
    pass


# ---- storage ----

def meta(name):
    f = DIR / name / "meta.json"
    return json.loads(f.read_text()) if f.exists() else None


def save_meta(name, m):
    (DIR / name).mkdir(parents=True, exist_ok=True)
    tmp = DIR / name / "meta.json.tmp"
    tmp.write_text(json.dumps(m, indent=1, default=str))
    tmp.replace(DIR / name / "meta.json")


def code_of(name, version=None):
    m = meta(name)
    if not m:
        raise SkillError(f"no skill '{name}' (list_skills shows what exists)")
    v = version or m["versions"][-1]["v"]
    f = DIR / name / f"v{v}.py"
    if not f.exists():
        raise SkillError(f"skill '{name}' has no version {v}")
    return v, f.read_text()


# ---- checking and loading ----

def check(code):
    """Problems with the code, or [] (also requires a top-level def run(robot, ...))."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"syntax error line {e.lineno}: {e.msg}"]
    probs = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module or ""]
            probs += [f"line {n.lineno}: import of '{m}' not allowed (allowed: {', '.join(sorted(ALLOWED_IMPORTS))})"
                      for m in mods if m.split(".")[0] not in ALLOWED_IMPORTS]
        elif isinstance(n, ast.Name) and n.id in BANNED:
            probs.append(f"line {n.lineno}: '{n.id}' not allowed")
        elif isinstance(n, ast.Attribute) and n.attr.startswith("_"):
            probs.append(f"line {n.lineno}: attribute '{n.attr}' not allowed (no names starting with _)")
        elif isinstance(n, ast.Name) and n.id.startswith("__"):
            probs.append(f"line {n.lineno}: name '{n.id}' not allowed")
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            probs.append(f"line {n.lineno}: global/nonlocal not allowed")
    runs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run"]
    if not runs:
        probs.append("needs a top-level function: def run(robot, ...)")
    elif not runs[0].args.args or runs[0].args.args[0].arg != "robot":
        probs.append("run's first argument must be robot")
    return probs


def load(code):
    probs = check(code)
    if probs:
        raise SkillError("code check failed: " + "; ".join(probs))

    def imp(name, *a, **k):
        if name.split(".")[0] not in ALLOWED_IMPORTS:
            raise ImportError(f"import of {name} not allowed")
        return __import__(name, *a, **k)
    g = {"__builtins__": dict(SAFE_BUILTINS, __import__=imp), "__name__": "skill"}
    exec(compile(code, "<skill>", "exec"), g)  # noqa: S102 - checked above; author is the lab agent
    return g["run"]


# ---- the robot object a skill sees ----

class Robot:
    """What a skill can do. Real moves go through server.py (S)."""

    def __init__(self, S, max_s, dry=False, fake_yes_after=None):
        self.S, self.dry, self.t0, self.max_s = S, dry, time.time(), max_s
        self.trace, self.photos, self.calls, self.n_calls, self.vt = [], [], [], 0, 0.0
        self.fake_yes_after, self.n_ask = fake_yes_after, 0
        self._llm = None

    # bookkeeping
    def _tick(self, call, args):
        if self.dry:
            self.vt += DRY_SECS.get(call, float(args.get("s", 0)) if call == "sleep" else 0.0)
            if self.n_calls >= DRY_MAX_CALLS:
                raise SkillTimeout(f"made {DRY_MAX_CALLS} calls in the dry run without finishing (a loop that never ends?)")
        if self._t() > self.max_s:
            raise SkillTimeout(f"over the {self.max_s:.0f} s limit" + (" (pretend time in the dry run)" if self.dry else ""))
        self.n_calls += 1
        if len(self.calls) < 300:
            self.calls.append(f"{self._t():5.1f}s {call}({', '.join(f'{k}={v}' for k, v in args.items())})")

    def _t(self):
        return time.time() - self.t0 + self.vt

    def elapsed(self):
        return round(self._t(), 1)

    def remaining(self):
        return round(self.max_s - self._t(), 1)

    def log(self, *msg):
        """Add a line to what run_skill reports back."""
        self.trace.append(f"{self.elapsed():5.1f}s " + " ".join(str(m) for m in msg)[:400])

    def sleep(self, s):
        """Wait up to 10 s."""
        self._tick("sleep", {"s": s})
        if not self.dry:
            time.sleep(max(0.0, min(10.0, float(s), self.remaining())))

    # reading
    def pose(self):
        """{'x', 'y', 'yaw_deg'} on the map, or None."""
        _, s = self.S.http("GET", "/state.json")
        mp = (s or {}).get("map_pose") if isinstance(s, dict) else None
        if not mp:
            return None
        import math
        return {"x": round(mp["x"], 3), "y": round(mp["y"], 3), "yaw_deg": round(math.degrees(mp["yaw"]), 1)}

    def state(self):
        """Line-up state, battery, current route and control settings."""
        _, s = self.S.http("GET", "/state.json")
        s = s if isinstance(s, dict) else {}
        loc = s.get("loc") or {}
        return {"loc": {k: loc.get(k) for k in ("status", "fit", "runner_up", "unsure")},
                "battery": (s.get("battery") or {}).get("soc") if isinstance(s.get("battery"), dict) else s.get("battery"),
                "map_mode": (s.get("map") or {}).get("mode"), "nav": s.get("nav"), "control": s.get("control")}

    def clearance(self):
        """Nearest live lidar obstacle (m, within 3 m; None = clear) in 8 directions relative to where the dog
        faces: front, front-left, left, back-left, back, back-right, right, front-right."""
        self._tick("clearance", {})
        import console_view as CV
        return CV.clearance(CV.snapshot(self.S))

    def plan(self, place="", x=None, y=None):
        """The planner's route preview without moving: {'length_m', 'points': [(x, y)], 'error'}."""
        self._tick("plan", {"place": place, "x": x, "y": y})
        import console_view as CV
        _, p = CV.plan(self.S, place, x, y)
        return {"length_m": p.get("length_m"), "points": CV.path_points(p), "error": p.get("error") or p.get("why")}

    def sensors(self):
        """The console's full sensor snapshot as a dict (imu, odom, state, battery, markers, loc, map, control...),
        without the raw lidar cloud."""
        self._tick("sensors", {})
        import console_view as CV
        s = CV.snapshot(self.S)
        return {k: v for k, v in s.items() if k not in ("cloud", "live", "joints")}

    def places(self):
        """{place id: {'x', 'y'}}."""
        return {k: {"x": v["x"], "y": v["y"]} for k, v in M.places().items()}

    def search_memory(self, query, k=8):
        """Pictures from memory: list of {'id', 'time', 'place', 'pose', 'summary'} (best match first)."""
        self._tick("search_memory", {"query": query})
        hits = M.search(query, k=max(1, min(20, int(k))))
        return [{"id": h["id"], "time": h["time"], "place": h.get("near_place"), "pose": h.get("pose"),
                 "summary": h.get("summary")} for h in hits]

    def ask(self, question):
        """Ask the small vision model a yes/no question about the current camera frame.
        Returns {'yes': bool, 'p_yes': float}. Fast (~0.2 s) but can be fooled: confirm with photo()."""
        self._tick("ask", {"question": question})
        self.n_ask += 1
        if self.dry:
            y = self.fake_yes_after is not None and self.n_ask > self.fake_yes_after
            return {"yes": y, "p_yes": 0.9 if y else 0.1}
        from watch import FrameJudge
        code, jpg = self.S.http("GET", "/frame.jpg")
        if code != 200 or not isinstance(jpg, bytes):
            raise SkillError(f"camera frame fetch failed ({code})")
        r = FrameJudge(self.llm(), question)(jpg)
        return {"yes": r["yes"], "p_yes": r["p_yes"]}

    def llm(self):
        if self._llm is None:
            import integration
            from llm import LLM
            self._llm = LLM(integration.SMALL_URL, name="small")
        return self._llm

    # moving (each checks STOP via server.agent and the time limit)
    def _move(self, name, **args):
        self._tick(name, args)
        if self.dry:
            return {"result": "done", "dry_run": True, "moved_m": args.get("m"), "turned_deg": args.get("deg"),
                    "map_pose": None}
        return self.S.agent(name, **args)

    def go_to(self, place="", x=None, y=None, yaw_deg=None, timeout_s=120):
        """Walk to a place id or map x, y (yaw_deg optional). Returns the console's reply:
        {'result': 'done' | 'no_route' | 'timeout' | ..., 'reason', 'moved_m', 'map_pose', 'why'}."""
        args = {"place": place} if place else {"x": x, "y": y, **({"yaw_deg": yaw_deg} if yaw_deg is not None else {})}
        return self._move("go_to", timeout_s=min(float(timeout_s), max(5.0, self.remaining())), **args)

    def turn(self, deg):
        """Turn in place (positive = left). Returns {'result', 'turned_deg', ...}."""
        return self._move("turn", deg=float(deg))

    def move(self, m):
        """Walk straight (negative = back), clamped to -1.0 .. 1.5 m. Returns {'result', 'moved_m', ...}."""
        return self._move("move", m=max(-1.0, min(1.5, float(m))))

    def look(self, deg):
        """Tilt the camera (about +16 up to -5 down; 0 = level)."""
        return self._move("look", deg=float(deg))

    def stop(self):
        self.calls.append(f"{self.elapsed():5.1f}s stop()")
        return {"result": "done"} if self.dry else self.S.agent("stop")

    def photo(self, note=""):
        """Take a photo, add it to memory and to what run_skill returns. Returns its picture id."""
        self._tick("photo", {"note": note} if note else {})
        if self.dry:
            pid = f"dry{len(self.photos) + 1}"
            self.photos.append((pid, note, None, None))
            return pid
        rec, jpg = self.S.snap(source="skill")
        self.photos.append((rec["id"], note, rec, jpg))
        return rec["id"]

    def watch_go_to(self, query, place="", x=None, y=None, yaw_deg=None, max_s=120):
        """go_to while the small vision model watches for `query` and stops the dog on sight (2 of 3 frames).
        Returns {'stopped_on_sight': bool, 'move_result', 'frames_checked'}."""
        self._tick("watch_go_to", {"query": query, "place": place, "x": x, "y": y})
        if self.dry:
            self.n_ask += 1
            y_ = self.fake_yes_after is not None and self.n_ask > self.fake_yes_after
            return {"stopped_on_sight": y_, "move_result": "aborted" if y_ else "done", "frames_checked": 10}
        import integration
        import tools as T
        args = {"place": place} if place else {"x": x, "y": y, **({"yaw_deg": yaw_deg} if yaw_deg is not None else {})}
        r = T.watch_go_to(self.S.M.CONSOLE, self.llm(), query, k=2, n=3, hz=3.0,
                          max_s=min(float(max_s), self.remaining()), allow_real=True,
                          also_person=bool(integration.PERSON.search(query)),
                          move=lambda: self.S.agent("go_to", timeout_s=120, **args))
        return {k: r.get(k) for k in ("stopped_on_sight", "move_result", "frames_checked", "frame_errors")}

    def scan_for(self, query, step_deg=45, views=8):
        """Turn in steps; stop at the first view where the small vision model sees `query`.
        Returns {'found': bool, 'view', 'turned_deg'}."""
        self._tick("scan_for", {"query": query})
        if self.dry:
            self.n_ask += 1
            y_ = self.fake_yes_after is not None and self.n_ask > self.fake_yes_after
            return {"found": y_, "view": 1 if y_ else None, "turned_deg": 45 if y_ else 360}
        import tools as T
        r = T.scan_for(self.S.M.CONSOLE, self.llm(), query, step_deg=float(step_deg), views=max(1, min(8, int(views))),
                       allow_real=True, turn=lambda deg: self.S.agent("turn", deg=deg))
        return {k: r.get(k) for k in ("found", "view", "turned_deg")}


# ---- running ----

def execute(fn, robot, args, max_s):
    """max_s: real seconds allowed."""
    """Run fn(robot, **args) in a thread with a line-level time limit. (ok, value or error text)."""
    out = {}
    deadline = time.time() + max_s + 5

    def line(frame, event, arg):
        if time.time() > deadline:
            raise SkillTimeout(f"over the {max_s:.0f} s limit")
        return line

    def tracer(frame, event, arg):      # line checks only inside the skill's own code (cheap elsewhere)
        return line if frame.f_code.co_filename == "<skill>" else None

    fn.__globals__["print"] = robot.log  # stdout is the MCP pipe: print goes to the run's log instead

    def target():
        sys.settrace(tracer)
        try:
            out["value"] = fn(robot, **args)
            out["ok"] = True
        except Exception as e:  # noqa: BLE001
            out["ok"], out["error"] = False, e
        finally:
            sys.settrace(None)
    th = threading.Thread(target=target, daemon=True)
    th.start()
    th.join(max_s + 15)
    if th.is_alive():
        return False, SkillTimeout("did not finish (stuck in a call)")
    return out.get("ok", False), out.get("value") if out.get("ok") else out.get("error")


def report(name, v, robot, ok, val, dry):
    head = (f"{'DRY RUN (nothing moved) of' if dry else 'ran'} skill {name} v{v} in {robot.elapsed()} s: "
            + (f"returned {repr(val)[:1500]}" if ok else f"FAILED: {type(val).__name__}: {val}"))
    calls = robot.calls[:20] + (["  ..."] if len(robot.calls) > 40 else []) + robot.calls[-20:] if len(robot.calls) > 40 else robot.calls
    lines = [head, f"calls ({robot.n_calls}):", *calls]
    if robot.trace:
        lines += ["log:", *robot.trace[-40:]]
    return "\n".join(lines)


def record_run(name, v, args, dry, ok, val, robot):
    m = meta(name)
    m.setdefault("runs", []).append({
        "t": round(time.time(), 1), "iso": time.strftime("%Y-%m-%d %H:%M:%S"), "v": v, "args": args, "dry": dry,
        "ok": ok, "result": repr(val)[:500] if ok else f"{type(val).__name__}: {val}"[:500],
        "secs": robot.elapsed(), "n_calls": robot.n_calls, "photos": [p[0] for p in robot.photos]})
    save_meta(name, m)
    return len(m["runs"])


def register(mcp, S):
    """Add the skill tools to server.py's MCP server. S = the server module."""

    @mcp.tool()
    @S.safe
    def write_skill(name: str, description: str, code: str, why: str) -> str:
        """Save a skill you wrote: Python with `def run(robot, ...)`, returning a short result (a dict or string).
        Use it for a routine you expect to repeat or that needs tight timing (checking the camera between steps,
        backing out of a stuck spot, searching an area systematically). description: what it does and its
        arguments. why: what you observed that made you write or change it. Saving again under the same name adds
        a new version (old ones are kept). Then test it with test_skill before run_skill.
        The robot object: go_to(place | x, y, yaw_deg), turn(deg), move(m), look(deg), photo(note) -> id,
        ask(question) -> {'yes', 'p_yes'} (small vision model on the current frame, ~0.2 s, can be fooled),
        watch_go_to(query, place | x, y), scan_for(query, step_deg, views), pose(), state(), places(),
        clearance() -> nearest lidar obstacle in 8 directions, plan(place | x, y) -> route preview, sensors(),
        search_memory(query, k), sleep(s), log(...), elapsed(), remaining(), stop().
        Allowed imports: math, random, statistics, json, re, itertools, collections. No files or network."""
        if not NAME.fullmatch(name):
            raise S.Refused("name: lowercase letters, digits and _, 2-41 characters, starting with a letter")
        probs = check(code)
        if probs:
            return "NOT SAVED, fix these:\n" + "\n".join(probs)
        m = meta(name) or {"name": name, "created": time.strftime("%Y-%m-%d %H:%M:%S"), "versions": [], "runs": []}
        v = (m["versions"][-1]["v"] + 1) if m["versions"] else 1
        (DIR / name).mkdir(parents=True, exist_ok=True)
        (DIR / name / f"v{v}.py").write_text(code)
        m["description"] = description
        m["versions"].append({"v": v, "t": time.strftime("%Y-%m-%d %H:%M:%S"), "why": why, "description": description})
        save_meta(name, m)
        return f"saved {name} v{v}. Next: test_skill('{name}', args) (dry run, nothing moves), then run_skill."

    @mcp.tool()
    @S.safe
    def test_skill(name: str, args: dict | None = None, fake_yes_after: int | None = None, max_s: float = 120.0) -> str:
        """Dry run of a skill against a pretend robot: nothing moves. Moves return 'done', ask/watch/scan answer
        'no' (or 'yes' after fake_yes_after questions, to test the found branch), photos are placeholders; pose,
        places and memory are real. Moves take pretend time (go_to 15 s, turn 3 s, ...) so max_s works as in a real
        run. Shows the calls it would make and what it returned or the error."""
        v, code = code_of(name)
        fn = load(code)
        robot = Robot(S, max(5.0, min(MAX_S, float(max_s))), dry=True, fake_yes_after=fake_yes_after)
        ok, val = execute(fn, robot, args or {}, DRY_WALL_S)
        record_run(name, v, args or {}, True, ok, val, robot)
        return report(name, v, robot, ok, val, True)

    @mcp.tool()
    @S.safe(moves=True)
    def run_skill(name: str, args: dict | None = None, max_s: float = 120.0) -> list:
        """Run a saved skill on the dog (latest version), after a quick dry run. Ends and sends stop if it errors,
        goes over max_s (at most 300 s), or STOP is pressed. Returns what it returned, the calls it made, its log
        lines and up to 4 of its photos. Afterwards, record whether it did what it was for with note_skill."""
        v, code = code_of(name)
        fn = load(code)
        max_s = max(5.0, min(MAX_S, float(max_s)))
        dry = Robot(S, max_s, dry=True)
        ok, val = execute(fn, dry, args or {}, DRY_WALL_S)
        if not ok:
            record_run(name, v, args or {}, True, ok, val, dry)
            return [f"NOT RUN: the dry run failed first.\n" + report(name, v, dry, ok, val, True)]
        S.begin_move()
        robot = Robot(S, max_s)
        ok, val = execute(fn, robot, args or {}, max_s)
        if not ok:
            S.http("POST", "/agent/stop", {}, timeout=5)
        n = record_run(name, v, args or {}, False, ok, val, robot)
        out = [report(name, v, robot, ok, val, False) + (" (stop sent)" if not ok else "") + f"\n(run #{n} of {name})"]
        for pid, note, rec, jpg in robot.photos[-4:]:
            out += [(f"photo note: {note}\n" if note else "") + S.describe_rec(rec), S.small(jpg, 640)]
        return out

    @mcp.tool()
    @S.safe
    def note_skill(name: str, worked: bool, note: str) -> str:
        """Record whether the last real run of a skill did what it was for (checked against the photos, not just
        its return value), and what you learned: when it works, when it does not, what to change."""
        m = meta(name)
        if not m:
            raise S.Refused(f"no skill '{name}'")
        real = [r for r in m.get("runs", []) if not r.get("dry")]
        if real:
            real[-1]["worked"], real[-1]["note"] = worked, note
        m.setdefault("notes", []).append({"t": time.strftime("%Y-%m-%d %H:%M:%S"), "worked": worked, "note": note,
                                          "v": m["versions"][-1]["v"]})
        save_meta(name, m)
        return f"noted on {name}: {'worked' if worked else 'did not work'}"

    @mcp.tool()
    @S.safe
    def list_skills() -> str:
        """Skills you have written: what each does, versions, how often real runs worked, and your latest notes."""
        if not DIR.exists():
            return "no skills yet (write_skill makes one)"
        lines = []
        for d in sorted(p for p in DIR.iterdir() if (p / "meta.json").exists()):
            m = json.loads((d / "meta.json").read_text())
            real = [r for r in m.get("runs", []) if not r.get("dry")]
            judged = [r for r in real if "worked" in r]
            lines.append(f"{m['name']} v{m['versions'][-1]['v']}: {m.get('description', '')}\n  real runs {len(real)}"
                         f" ({sum(r['ok'] for r in real)} finished without error; judged worked "
                         f"{sum(bool(r['worked']) for r in judged)}/{len(judged)})"
                         + "".join(f"\n  note {n['t']}: {'worked' if n['worked'] else 'failed'}: {n['note']}"
                                   for n in m.get("notes", [])[-3:]))
        return "\n".join(lines) or "no skills yet (write_skill makes one)"

    @mcp.tool()
    @S.safe
    def read_skill(name: str, version: int | None = None) -> str:
        """A skill's code (latest version unless given) and the reason recorded for each version."""
        v, code = code_of(name, version)
        m = meta(name)
        hist = "\n".join(f"  v{x['v']} {x['t']}: {x['why']}" for x in m["versions"])
        return f"{name} v{v}\n{hist}\n---\n{code}"

    return write_skill, test_skill, run_skill, note_skill, list_skills, read_skill
