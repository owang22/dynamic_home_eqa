"""A live console page for the lab dog on the lab network: camera, map with the dog and its route, status,
STOP, buttons to walk to a saved place, and the lab agent's chat (same agent as web.py and chat.sh).

    python3 go2/lab_agent/console_page.py     # prints http://172.17.31.231:8420/?k=... (lab network only)

The console's reads (/frame.jpg, /map.png, /state.json, /places on the control PC) are proxied through cheetah
with short timeouts and a small cache, so a slow console never hangs the page; a stale picture is marked stale.
Only three things send commands: STOP (web.console_stop: halts the dog, ends a running agent turn, writes
stop_flag), the place buttons (claim, go_to, release as client cheetah-console-page; refused while an agent turn
runs or a person has control) and the agent's own tools. Chat and /pic/ reuse web.py's handler.

Getting in: a password login (Oliver's choice, 2026-10-22: reachable from outside the lab through a Cloudflare
quick tunnel). The password is in go2/data/lab_agent/console_password (mode 600, not in git); a right password
gives a session cookie for 12 h. Wrong passwords: 5 from one address in 10 min lock that address out for 15 min;
20 in all in 10 min lock out everyone but the lab network for 15 min. Behind the tunnel the address is
CF-Connecting-IP. The URL key (console_key) still works, for tests from cheetah.
"""
from __future__ import annotations

import hmac
import json
import os
import secrets
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).parent))
import web as W  # noqa: E402

M = W.M
PORT = 8420
CLIENT = "cheetah-console-page"
KEYF = M.DATA / "console_key"
if not KEYF.exists():
    KEYF.write_text(secrets.token_urlsafe(24))
os.chmod(KEYF, 0o600)
KEY = KEYF.read_text().strip()
PWF = M.DATA / "console_password"
if not PWF.exists():
    PWF.write_text("nesl")
os.chmod(PWF, 0o600)
SESS: dict[str, float] = {}                # cookie token -> expiry
FAILS: list[tuple[float, str]] = []        # (time, address) of wrong passwords
LOCKED: dict[str, float] = {}              # address (or "*" for everyone outside the lab) -> locked until
LOGIN_LOCK = threading.Lock()
LOGIN = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lab dog login</title><style>
:root{--bg:#f6f5f1;--fg:#1d1d1b;--line:#dedbd2;--accent:#2f5d50;--card:#fff;--bad:#c62828}
@media (prefers-color-scheme:dark){:root{--bg:#161614;--fg:#ecebe6;--line:#3a3934;--accent:#7fb8a5;--card:#22221f;--bad:#ef5350}}
body{margin:0;min-height:100vh;display:grid;place-items:center;background:var(--bg);color:var(--fg);font:16px system-ui,sans-serif;padding:16px;box-sizing:border-box}
form{display:flex;flex-direction:column;gap:12px;width:min(320px,100%)}h1{font-size:20px;margin:0}
input{font:inherit;padding:12px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--fg)}
button{font:inherit;font-weight:600;padding:12px;border:0;border-radius:10px;background:var(--accent);color:var(--bg)}
p{color:var(--bad);margin:0;min-height:1.2em}</style></head><body>
<form method="post" action="/login"><h1>Lab dog console</h1><input type="password" name="pw" placeholder="Password" autofocus autocomplete="current-password">
<button>Log in</button><p>{msg}</p></form></body></html>"""


def client_ip(h):
    return h.headers.get("CF-Connecting-IP") or h.client_address[0]


def from_lab(h):
    return not h.headers.get("CF-Connecting-IP") and h.client_address[0].startswith(("127.", "172.17."))


def try_login(h, pw):
    """(ok, message). Lockouts are checked before the password, so a locked address learns nothing."""
    now, ip = time.time(), client_ip(h)
    with LOGIN_LOCK:
        FAILS[:] = [f for f in FAILS if now - f[0] < 600]
        for who in (ip, "*"):
            if LOCKED.get(who, 0) > now and not (who == "*" and from_lab(h)):
                return False, "Too many wrong tries. Try again later."
        if hmac.compare_digest(pw.encode(), PWF.read_text().strip().encode()):
            return True, ""
        FAILS.append((now, ip))
        if sum(1 for _, a in FAILS if a == ip) >= 5:
            LOCKED[ip] = now + 900
        if len(FAILS) >= 20:
            LOCKED["*"] = now + 900
    with open(M.DATA / "console_page.log", "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} wrong password from {ip}\n")
    return False, "Wrong password."

# path -> (seconds to keep, timeout)
PROXY = {"/frame.jpg": (0.25, 2.5), "/map.png": (20, 5), "/state.json": (0.3, 2.5), "/places": (15, 5),
         "/map/objects": (15, 5), "/map/layer.png?layer=mid": (30, 5), "/map/layer.png?layer=high": (30, 5)}
_cache: dict[str, tuple[float, bytes, str]] = {}
_locks = {p: threading.Lock() for p in PROXY}


def proxy_key(u):
    """/c/<path> on this page -> the console path; height layers keep their ?layer= (only mid and high)."""
    layer = parse_qs(u.query).get("layer", [""])[0]
    return "/" + u.path[3:] + (f"?layer={layer}" if layer else "")


def fetch(path):
    """(body, content type, stale) from the cache or the console. Never raises."""
    keep, timeout = PROXY[path]
    with _locks[path]:                       # one console request per path at a time, however many viewers
        hit = _cache.get(path)
        if hit and time.time() - hit[0] < keep:
            return hit[1], hit[2], False
        try:
            with urllib.request.urlopen(M.CONSOLE + path, timeout=timeout) as r:
                body, ctype = r.read(), r.headers.get("Content-Type", "application/octet-stream")
            if path == "/state.json":
                body = json.dumps(trim(json.loads(body))).encode()
                ctype = "application/json"
            _cache[path] = (time.time(), body, ctype)
            return body, ctype, False
        except Exception:  # noqa: BLE001
            if hit:
                return hit[1], hit[2], True
            return b'{"error": "console not reachable"}', "application/json", True


def trim(s):
    """Only what the page draws (the full state carries the lidar cloud: tens of kB at 3 Hz)."""
    a = s.get("agents") or {}
    lv = s.get("live") or {}
    return {"t": time.time(), "map": {k: (s.get("map") or {}).get(k) for k in
                                      ("resolution", "origin", "width", "height", "mode", "status", "saved_at", "t",
                                       "room_deg")},
            "live": {"new": lv.get("new") or [], "cleared": lv.get("cleared") or []},   # changes vs the saved map
            "markers": (s.get("markers") or {}).get("list") or [],
            "map_pose": s.get("map_pose"), "nav": s.get("nav"), "owner": a.get("owner"), "current": a.get("current"),
            "notes": a.get("notes"), "log": (a.get("log") or [])[-6:], "control": s.get("control"),
            "age": s.get("age"), "body_height": (s.get("state") or {}).get("body_height"),
            "agent_turn": W.LOCK.locked(), "stop_flag": W.STOP_FLAG.exists(),
            "loc": {k: (s.get("loc") or {}).get(k) for k in ("status", "seq", "fit", "runner_up", "unsure")},
            "battery": (s.get("battery") or {}).get("soc")}


def console(method, path, body=None, timeout=150):
    data = json.dumps(dict(body or {}, client=CLIENT)).encode() if method == "POST" else None
    req = urllib.request.Request(M.CONSOLE + path, data, {"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:  # noqa: BLE001
            return e.code, {}
    except Exception as e:  # noqa: BLE001
        return 0, {"error": str(e)}


def go_place(place):
    """A place button: claim, go_to, release. One message line back."""
    places = json.loads(fetch("/places")[0] or b"{}")
    if place not in places:
        return f"unknown place {place}"
    if W.LOCK.locked():
        return "not moving: the agent is working on a chat message (press STOP to end it first)"
    W.STOP_FLAG.unlink(missing_ok=True)          # pressing a place button is a new instruction from Oliver
    code, out = console("POST", "/agent/claim")
    if code != 200 or (isinstance(out, dict) and out.get("result") not in (None, "done", "ok")):
        return f"not moving: the console refused the claim ({code} {out})"
    try:
        code, out = console("POST", "/agent/go_to", {"place": place, "timeout_s": 120})
        return (f"go_to {place}: {out.get('result')} {out.get('reason') or ''} - moved {out.get('moved_m')} m"
                if isinstance(out, dict) else f"go_to {place}: {code} {out}")
    finally:
        console("POST", "/agent/release")


PAGE = (Path(__file__).parent / "console_page.html").read_text


class H(W.H):
    def session(self):
        for part in (self.headers.get("Cookie") or "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == "dogs" and SESS.get(v, 0) > time.time():
                return True
        return False

    def ok(self):
        k = parse_qs(urlparse(self.path).query).get("k", [""])[0]
        if (k and hmac.compare_digest(k.encode(), KEY.encode())) or self.session():
            return True
        if urlparse(self.path).path == "/" and self.command == "GET":
            self.send_response(303)
            self.send_header("Location", "/login")
            self.end_headers()
        else:
            self.send_error(403)
        return False

    def send(self, code, body, ctype, extra=()):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        for k, v in extra:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/login":
            self.send(200, LOGIN.replace("{msg}", "").encode(), "text/html; charset=utf-8")
            return
        if not self.ok():
            return
        if u.path == "/":
            self.send(200, PAGE().encode(), "text/html; charset=utf-8")
        elif u.path.startswith("/c/") and proxy_key(u) in PROXY:
            body, ctype, stale = fetch(proxy_key(u))
            self.send(200, body, ctype, [("X-Stale", "1" if stale else "0")])
        elif u.path.startswith("/pic/"):
            super().do_GET()                  # web.H checks its own key in ok(): ours, via this override
        else:
            self.send_error(404)

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/login":
            n = min(int(self.headers.get("Content-Length") or 0), 1000)
            pw = parse_qs(self.rfile.read(n).decode(errors="replace")).get("pw", [""])[0]
            ok, msg = try_login(self, pw)
            if not ok:
                self.send(200, LOGIN.replace("{msg}", msg).encode(), "text/html; charset=utf-8")
                return
            tok = secrets.token_urlsafe(32)
            SESS[tok] = time.time() + 12 * 3600
            secure = "; Secure" if self.headers.get("CF-Connecting-IP") else ""
            self.send_response(303)
            self.send_header("Set-Cookie", f"dogs={tok}; HttpOnly; SameSite=Strict; Path=/; Max-Age=43200{secure}")
            self.send_header("Location", "/")
            self.end_headers()
            return
        if u.path == "/note":                  # Collect mode: a hidden note, grade or page action; never reaches the agent
            if not self.ok():
                return
            n = min(int(self.headers.get("Content-Length") or 0), 20000)
            body = json.loads(self.rfile.read(n) or b"{}")
            ep = W.collect.clean_id(body.get("episode"))
            if not ep:
                self.send(400, b'{"error": "no episode"}', "application/json")
                return
            frame = state = None
            if body.get("kind", "note") == "note":
                jpg, ctype, stale = fetch("/frame.jpg")
                frame = jpg if ctype.startswith("image") else None
                st = json.loads(fetch("/state.json")[0] or b"{}")
                state = {k: st.get(k) for k in ("map_pose", "loc", "battery", "owner", "current", "nav", "control", "age")}
                state["camera_stale"] = stale
            ev = W.collect.note(ep, body, frame, state)
            self.send(200, json.dumps({"ok": True, "t": ev["t"], "frame": ev.get("frame")}).encode(), "application/json")
            return
        if u.path == "/go":
            if not self.ok():
                return
            n = int(self.headers.get("Content-Length") or 0)
            place = json.loads(self.rfile.read(n) or b"{}").get("place", "")
            self.send(200, go_place(place).encode(), "text/plain; charset=utf-8")
            return
        super().do_POST()                     # /ask (agent chat) and /stop


def main():
    addr = f"http://{W.lan_ip()}:{PORT}/?k={KEY}"
    print("console page (lab network):", addr, flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()


if __name__ == "__main__":
    main()
