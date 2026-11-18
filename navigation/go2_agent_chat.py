#!/usr/bin/env python3
"""Go2 "Ask the dog" agent runner: chat with a Claude agent that has only the robot tools.

Runs on the HOST (the console's container has no claude CLI), listening on 127.0.0.1:8091 only; the console proxies
/agentchat/* to it so a phone needs port 8080 alone. Each message starts `claude -p` with exactly the restrictions of
go2_claude.sh (only the go2 MCP tools, Bash/Edit/Write/Web/Task disallowed, prompt.md appended); follow-ups pass
--resume <claude session id> so the conversation continues. One run at a time.

  POST /chat        {"session": id|null, "text": "...", "model": "opus"|"sonnet"} -> {"run", "session"}; 409 busy
  GET  /chat/stream?run=R&from=N   long-poll (up to 20 s): {"events": [...], "next": N2, "done": bool}
  POST /chat/stop   {"run"}: kill the claude process group, then POST STOP to the console (the dog halts)
  GET  /chat/conv?session=S        a conversation's transcript (events of every run)
  GET  /chat/status                {"busy", "run", "session"}
Events: {"kind": "start"|"user"|"text"|"tool"|"tool_result"|"photo"|"result"|"error"|"end", ...}.
Log: ~/oliver/logs/agent_chat/YYYYMMDD.jsonl. Stdlib only, Python 3.8 (host /usr/bin/python3).
"""
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(HERE, "go2_claude")
PORT = int(os.environ.get("GO2_CHAT_PORT", "8091"))
CLAUDE = (os.environ.get("GO2_CLAUDE_BIN") or __import__("shutil").which("claude")
          or os.path.expanduser("~/.local/bin/claude"))     # cron has no ~/.local/bin on PATH
CONSOLE = os.environ.get("GO2_CONSOLE", "http://127.0.0.1:8080")
LOG_DIR = os.environ.get("GO2_CHAT_LOG_DIR", os.path.join(HERE, "logs", "agent_chat"))
MODELS = ("opus", "sonnet")
KEEP_CONVS = 20
MAX_TEXT = 4000
# Exactly go2_claude.sh's restrictions. Do not widen.
ALLOWED = "mcp__go2__*"
DISALLOWED = "Bash,Edit,Write,WebFetch,WebSearch,Task,NotebookEdit"
CHAT_NOTE = ("\n\nYou are chatting with a person through the console's \"Ask the dog\" panel, often from a phone. "
             "Answer questions briefly and plainly. Only move the dog when the person asks for something that needs "
             "it; if they say not to move, do not call go_to, move, turn, look_around or tilt_camera.")

LOCK = threading.Lock()
CONVS = {}      # conv id -> {"id", "claude_session", "model", "runs": [run ids], "t"}
RUNS = {}       # run id -> {"id", "conv", "proc", "events", "done", "cond", "t"}
ACTIVE = {"run": None}


def log(obj):
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(os.path.join(LOG_DIR, time.strftime("%Y%m%d") + ".jsonl"), "a") as f:
            f.write(json.dumps(obj, default=str) + "\n")
    except OSError:
        pass


def emit(run, ev):
    ev = dict(ev, t=round(time.time(), 2))
    with run["cond"]:
        run["events"].append(ev)
        run["cond"].notify_all()
    log({"run": run["id"], "conv": run["conv"], **ev})


def short(name):
    return name[len("mcp__go2__"):] if name.startswith("mcp__go2__") else name


def result_text(content):
    if isinstance(content, str):
        return content
    parts = []
    for p in content or []:
        if isinstance(p, dict) and p.get("type") == "text":
            parts.append(p.get("text", ""))
        elif isinstance(p, dict) and p.get("type") == "image":
            parts.append("[image]")
    return " ".join(parts)


def parse_line(run, conv, line):
    try:
        ev = json.loads(line)
    except ValueError:
        return
    t = ev.get("type")
    if t == "system" and ev.get("subtype") == "init":
        if ev.get("session_id"):
            conv["claude_session"] = ev["session_id"]
        emit(run, {"kind": "start", "model": ev.get("model"), "tools": [short(x) for x in ev.get("tools") or []]})
    elif t == "assistant":
        for c in (ev.get("message") or {}).get("content") or []:
            if c.get("type") == "text" and c.get("text", "").strip():
                emit(run, {"kind": "text", "text": c["text"].strip()})
            elif c.get("type") == "tool_use":
                emit(run, {"kind": "tool", "id": c.get("id"), "name": short(c.get("name", "")), "args": c.get("input") or {}})
    elif t == "user":
        for c in (ev.get("message") or {}).get("content") or []:
            if isinstance(c, dict) and c.get("type") == "tool_result":
                txt = result_text(c.get("content"))
                low = txt.lower()
                ok = not c.get("is_error") and not any(w in low for w in ('"refused"', '"error"', "not_owner"))
                emit(run, {"kind": "tool_result", "id": c.get("tool_use_id"), "ok": ok,
                           "summary": re.sub(r"\s+", " ", txt)[:300]})
                for pid in re.findall(r"\bphoto ([\w.-]+)", txt):
                    emit(run, {"kind": "photo", "url": f"/agent/photos/{pid}.jpg"})
    elif t == "result":
        if ev.get("session_id"):
            conv["claude_session"] = ev["session_id"]
        emit(run, {"kind": "result", "text": ev.get("result"), "is_error": bool(ev.get("is_error")),
                   "cost_usd": ev.get("total_cost_usd"), "duration_s": round((ev.get("duration_ms") or 0) / 1000, 1),
                   "turns": ev.get("num_turns")})


def command(conv, model):
    with open(os.path.join(TOOLS_DIR, "prompt.md")) as f:
        prompt = f.read() + CHAT_NOTE
    cmd = [CLAUDE, "-p", "--model", model,
           "--mcp-config", os.path.join(TOOLS_DIR, "mcp.json"), "--strict-mcp-config",
           "--allowedTools", ALLOWED, "--disallowedTools", DISALLOWED,
           "--append-system-prompt", prompt,
           "--output-format", "stream-json", "--verbose"]
    if conv.get("claude_session"):
        cmd += ["--resume", conv["claude_session"]]
    return cmd


def start(session, text, model):
    with LOCK:
        if ACTIVE["run"] and not RUNS[ACTIVE["run"]]["done"]:
            return None, "busy"
        conv = CONVS.get(session) if session else None
        if conv is None:
            conv = {"id": uuid.uuid4().hex[:12], "claude_session": None, "model": model, "runs": [], "t": time.time()}
            CONVS[conv["id"]] = conv
            for old in sorted(CONVS.values(), key=lambda c: c["t"])[:-KEEP_CONVS]:
                CONVS.pop(old["id"], None)
                for r in old["runs"]:
                    RUNS.pop(r, None)
        run = {"id": uuid.uuid4().hex[:12], "conv": conv["id"], "proc": None, "events": [], "done": False,
               "cond": threading.Condition(), "t": time.time()}
        RUNS[run["id"]] = run
        conv["runs"].append(run["id"])
        conv["t"], conv["model"] = time.time(), model
        ACTIVE["run"] = run["id"]
    emit(run, {"kind": "user", "text": text, "model": model})
    cmd = command(conv, model)
    log({"run": run["id"], "conv": conv["id"], "kind": "cmd", "argv": [a if len(a) < 200 else a[:60] + "…" for a in cmd]})
    env = dict(os.environ, GO2_AGENT_NAME="ask-the-dog")
    try:
        proc = subprocess.Popen(cmd, cwd=TOOLS_DIR, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env=env, start_new_session=True)       # own process group: Stop kills all of it
    except OSError as e:
        emit(run, {"kind": "error", "text": f"could not start claude: {e}"})
        emit(run, {"kind": "end", "code": None})
        run["done"] = True
        return run, None
    run["proc"] = proc
    proc.stdin.write(text.encode())          # the prompt on stdin: text starting with "-" can't be taken for an option
    proc.stdin.close()
    threading.Thread(target=reader, args=(run, conv), daemon=True).start()
    return run, None


def reader(run, conv):
    proc = run["proc"]
    err = []
    t = threading.Thread(target=lambda: err.extend(proc.stderr.read().decode("utf-8", "replace").splitlines()[-20:]), daemon=True)
    t.start()
    for raw in proc.stdout:
        parse_line(run, conv, raw.decode("utf-8", "replace"))
    code = proc.wait()
    t.join(2)
    if code and not run.get("stopped"):
        emit(run, {"kind": "error", "text": "claude exited with code %s: %s" % (code, " | ".join(err[-3:])[:500])})
    emit(run, {"kind": "end", "code": code, "stopped": bool(run.get("stopped"))})
    with run["cond"]:
        run["done"] = True
        run["cond"].notify_all()


def console_stop():
    try:
        req = urllib.request.Request(CONSOLE + "/cmd", data=json.dumps({"action": "stop", "client": "ask-the-dog"}).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=3) as r:
            return r.status
    except Exception as e:
        return str(e)


def stop(run_id):
    """SIGTERM the run's process group, STOP the dog right away, SIGKILL whatever is left after 3 s, STOP again."""
    run = RUNS.get(run_id) if run_id else (RUNS.get(ACTIVE["run"]) if ACTIVE["run"] else None)
    killed, pg = False, None
    if run and run["proc"] and run["proc"].poll() is None:
        run["stopped"] = True
        try:
            pg = os.getpgid(run["proc"].pid)
            os.killpg(pg, signal.SIGTERM)
            killed = True
        except ProcessLookupError:
            pg = None
    first = console_stop()
    if pg is not None:
        for _ in range(30):
            if run["proc"].poll() is not None:
                break
            time.sleep(0.1)
        try:
            os.killpg(pg, signal.SIGKILL)       # anything left in the group (claude ignoring TERM, the MCP server)
        except ProcessLookupError:
            pass
        console_stop()
    if run:
        emit(run, {"kind": "stopped", "killed": killed, "console_stop": first})
    return {"killed": killed, "console_stop": first}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def reply(self, code, obj):
        body = json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        try:
            return json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError:
            return None

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        req = self.body()
        if not isinstance(req, dict):
            return self.reply(400, {"error": "expected a JSON object"})
        if path == "/chat":
            text = str(req.get("text") or "").strip()
            model = req.get("model") or "opus"
            if not text:
                return self.reply(400, {"error": "text is empty"})
            if len(text) > MAX_TEXT:
                return self.reply(400, {"error": f"text longer than {MAX_TEXT} characters"})
            if model not in MODELS:
                return self.reply(400, {"error": "model must be opus or sonnet"})
            run, err = start(req.get("session"), text, model)
            if err:
                return self.reply(409, {"error": "busy: the agent is still working on the previous message",
                                        "run": ACTIVE["run"]})
            return self.reply(200, {"run": run["id"], "session": run["conv"]})
        if path == "/chat/stop":
            return self.reply(200, stop(req.get("run")))
        self.reply(404, {"error": "not found"})

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == "/chat/stream":
            run = RUNS.get((q.get("run") or [""])[0])
            if not run:
                return self.reply(404, {"error": "unknown run"})
            try:
                frm = max(0, int((q.get("from") or ["0"])[0]))
            except ValueError:
                frm = 0
            with run["cond"]:
                run["cond"].wait_for(lambda: len(run["events"]) > frm or run["done"], timeout=20)
                evs = run["events"][frm:]
                done = run["done"]
            return self.reply(200, {"events": evs, "next": frm + len(evs), "done": done and frm + len(evs) >= len(run["events"])})
        if u.path == "/chat/conv":
            conv = CONVS.get((q.get("session") or [""])[0])
            if not conv:
                return self.reply(404, {"error": "unknown session"})
            return self.reply(200, {"session": conv["id"], "model": conv["model"],
                                    "runs": [{"run": r, "done": RUNS[r]["done"], "events": RUNS[r]["events"]}
                                             for r in conv["runs"] if r in RUNS]})
        if u.path in ("/chat/status", "/health"):
            run = RUNS.get(ACTIVE["run"]) if ACTIVE["run"] else None
            busy = bool(run and not run["done"])
            return self.reply(200, {"busy": busy, "run": run["id"] if busy else None, "session": run["conv"] if busy else None})
        self.reply(404, {"error": "not found"})


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    srv.daemon_threads = True
    print(f"go2 agent chat on http://127.0.0.1:{PORT} (claude: {CLAUDE})", flush=True)
    log({"kind": "server_start", "port": PORT, "pid": os.getpid()})
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if ACTIVE["run"]:
            stop(ACTIVE["run"])


if __name__ == "__main__":
    main()
