"""A phone page for the lab agent: chat with it from anywhere on the lab network.

    python3 go2/lab_agent/web.py            # prints the address to open, e.g. http://172.17.31.231:8410/?k=...
                                            # also indexes new console trail frames every 2 min (--no-watch: not)

Each message runs the same agent as chat.sh (claude -p, Opus on Oliver's Max plan, only the lab tools), resuming
one conversation per page load; the reply streams in, with each tool call shown as a grey line and every picture
it mentions shown inline. The STOP button posts /agent/stop to the console directly (always allowed), whatever the
agent is doing. The page needs the key in its address (printed at start, kept in go2/data/lab_agent/web_key), since
the agent can move the dog and the lab network is shared.
"""
from __future__ import annotations

import json
import re
import secrets
import socket
import subprocess
import sys
import threading
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import memory as M  # noqa: E402

PORT = 8410
KEYF = M.DATA / "web_key"
M.DATA.mkdir(parents=True, exist_ok=True)
KEY = KEYF.read_text().strip() if KEYF.exists() else secrets.token_urlsafe(12)
KEYF.write_text(KEY)
SESSF = M.DATA / "web_sessions.json"  # session ids that have had a turn (survives a web.py restart)
SESSIONS: dict[str, bool] = json.loads(SESSF.read_text()) if SESSF.exists() else {}
class TurnLock:
    """One agent turn at a time across every page process (web.py, console_page.py): a thread lock plus an
    flock on go2/data/lab_agent/agent_turn.lock."""

    def __init__(self):
        import fcntl
        self.fcntl, self.t, self.f = fcntl, threading.Lock(), open(M.DATA / "agent_turn.lock", "a")

    def acquire(self, blocking=False):
        if not self.t.acquire(blocking=False):
            return False
        try:
            self.fcntl.flock(self.f, self.fcntl.LOCK_EX | self.fcntl.LOCK_NB)
            return True
        except OSError:
            self.t.release()
            return False

    def release(self):
        self.fcntl.flock(self.f, self.fcntl.LOCK_UN)
        self.t.release()

    def locked(self):
        if self.t.locked():
            return True
        try:
            self.fcntl.flock(self.f, self.fcntl.LOCK_EX | self.fcntl.LOCK_NB)
            self.fcntl.flock(self.f, self.fcntl.LOCK_UN)
            return False
        except OSError:
            return True


LOCK = TurnLock()                     # one agent turn at a time (one dog), across processes
RUNNING: dict[str, subprocess.Popen] = {}   # the agent process now running, if any
STOP_FLAG = M.DATA / "stop_flag"      # server.py refuses moves while this exists


def console_stop(client="cheetah-lab-page"):
    """STOP: halt the dog, end the running agent turn, and block further moves until the next message."""
    STOP_FLAG.write_text(str(__import__("time").time()))
    p = RUNNING.get("p")
    if p and p.poll() is None:
        p.kill()
    req = urllib.request.Request(M.CONSOLE + "/agent/stop", json.dumps({"client": client}).encode(),
                                 {"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            body = r.read()[:200].decode(errors="replace")
            return f"STOPPED: console replied {r.status} {body}; agent turn ended" if p else f"STOPPED: console replied {r.status} {body}"
    except Exception as e:  # noqa: BLE001
        return f"STOP FAILED to reach the console: {e}. Use the console's STOP."


def release():
    req = urllib.request.Request(M.CONSOLE + "/agent/release", json.dumps({"client": "cheetah-lab-agent"}).encode(),
                                 {"Content-Type": "application/json"}, method="POST")
    try:
        urllib.request.urlopen(req, timeout=5).read()
    except Exception:  # noqa: BLE001
        pass
PIC = re.compile(r"\b([tp]\d{9,}(?:_\d+)?|l\d{9,})\b")

PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lab dog</title><style>
:root{--bg:#f6f5f1;--fg:#1d1d1b;--mute:#76736b;--card:#fff;--line:#dedbd2;--accent:#2f5d50;--stop:#c62828}
@media (prefers-color-scheme:dark){:root{--bg:#161614;--fg:#ecebe6;--mute:#9b988f;--card:#22221f;--line:#3a3934;--accent:#7fb8a5;--stop:#ef5350}}
*{box-sizing:border-box}html,body{height:100%}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.45 system-ui,sans-serif;display:flex;flex-direction:column}
header{display:flex;gap:10px;align-items:center;padding:10px 14px;border-bottom:1px solid var(--line)}
header b{flex:1}#st{font-size:13px;color:var(--mute)}
#stop{background:var(--stop);color:#fff;border:0;border-radius:10px;font-weight:700;font-size:18px;padding:12px 22px}
#log{flex:1;overflow-y:auto;padding:12px 14px;display:flex;flex-direction:column;gap:10px}
.m{max-width:100%;padding:10px 12px;border-radius:12px;white-space:pre-wrap;overflow-wrap:anywhere}
.u{align-self:flex-end;background:var(--accent);color:var(--bg)}.a{background:var(--card);border:1px solid var(--line)}
.t{font-size:13px;color:var(--mute);font-family:ui-monospace,monospace;overflow-wrap:anywhere}
.pics{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}.pics img{width:calc(50% - 3px);border-radius:8px}
form{display:flex;gap:8px;padding:10px 14px;border-top:1px solid var(--line)}
textarea{flex:1;min-width:0;font:inherit;padding:10px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--fg);resize:none}
button.s{background:var(--accent);color:var(--bg);border:0;border-radius:10px;padding:0 18px;font-weight:600}
</style></head><body>
<header><b>Lab dog</b><span id="st">ready</span><button id="stop">STOP</button></header>
<div id="log"></div>
<form id="f"><textarea id="q" rows="2" placeholder="Where is the grey backpack?"></textarea><button class="s">Send</button></form>
<script>
const K=new URLSearchParams(location.search).get('k'),S=crypto.randomUUID?crypto.randomUUID():String(Date.now());
const log=document.getElementById('log'),st=document.getElementById('st');
function add(cls,text){const d=document.createElement('div');d.className='m '+cls;d.textContent=text;log.appendChild(d);log.scrollTop=1e9;return d}
function pics(el,ids){if(!ids.length)return;const p=document.createElement('div');p.className='pics';
 ids.forEach(i=>{const im=document.createElement('img');im.src='/pic/'+i+'?k='+K;im.onclick=()=>open(im.src);p.appendChild(im)});el.appendChild(p);log.scrollTop=1e9}
document.getElementById('stop').onclick=async()=>{st.textContent='sending stop…';
 try{const r=await fetch('/stop?k='+K,{method:'POST'});const t=await r.text();add('t',t);st.textContent=t.startsWith('STOPPED')?'stopped':'STOP FAILED'}catch(e){add('t','STOP FAILED: '+e+' — use the console');st.textContent='STOP FAILED'}};
document.getElementById('f').onsubmit=async e=>{e.preventDefault();const q=document.getElementById('q');const text=q.value.trim();if(!text)return;q.value='';
 add('u',text);st.textContent='working…';let cur=null;
 try{const r=await fetch('/ask?k='+K,{method:'POST',body:JSON.stringify({session:S,text})});const rd=r.body.getReader(),dec=new TextDecoder();let buf='';
  for(;;){const {value,done}=await rd.read();if(done)break;buf+=dec.decode(value,{stream:true});let i;
   while((i=buf.indexOf('\n'))>=0){const line=buf.slice(0,i);buf=buf.slice(i+1);if(!line)continue;const ev=JSON.parse(line);
    if(ev.kind==='text'){cur=add('a',ev.text);pics(cur,ev.pics)}
    else if(ev.kind==='tool'){add('t','· '+ev.text)}
    else if(ev.kind==='pics'){pics(add('t','pictures'),ev.pics)}
    else if(ev.kind==='done'){st.textContent=ev.text}}}}
 catch(err){add('t','error: '+err);st.textContent='error'}};
</script></body></html>"""


def save_transcripts():
    """Copy and export the agent's conversations to go2/data/lab_agent/chats/ (transcripts.py)."""
    try:
        import transcripts
        transcripts.main(quiet=True)
    except Exception as e:  # noqa: BLE001
        print("transcript export failed:", e, flush=True)


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("172.17.40.64", 8080))
        return s.getsockname()[0]
    finally:
        s.close()


def agent_cmd(session, text):
    resume = ["--resume", session] if SESSIONS.get(session) else ["--session-id", session]
    return ["claude", "-p", "--model", "opus", "--mcp-config", str(HERE / "mcp.json"), "--strict-mcp-config",
            "--tools", "", "--allowedTools", "mcp__lab__*", "--append-system-prompt-file", str(HERE / "SYSTEM.md"),
            "--disable-slash-commands", "--output-format", "stream-json", "--verbose", *resume, "--", text]


def short_tool(block):
    name = block.get("name", "").replace("mcp__lab__", "")
    args = ", ".join(f"{k}={v}" for k, v in (block.get("input") or {}).items())
    return f"{name}({args})"


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def ok(self):
        if parse_qs(urlparse(self.path).query).get("k", [""])[0] != KEY:
            self.send_error(403)
            return False
        return True

    def do_GET(self):
        u = urlparse(self.path)
        if not self.ok():
            return
        if u.path == "/":
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
        elif u.path.startswith("/pic/"):
            pid = u.path.split("/")[-1]
            f = M.PICS / f"{pid}.jpg"
            if not re.fullmatch(r"[A-Za-z0-9_]+", pid) or not f.exists():
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.end_headers()
            self.wfile.write(f.read_bytes())
        else:
            self.send_error(404)

    def do_POST(self):
        u = urlparse(self.path)
        if not self.ok():
            return
        if u.path == "/stop":
            msg = console_stop()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(msg.encode())
            return
        if u.path != "/ask":
            self.send_error(404)
            return
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        session, text = str(uuid.UUID(body["session"])), body["text"][:4000]
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.end_headers()

        def emit(kind, text, pics=()):
            self.wfile.write((json.dumps({"kind": kind, "text": text, "pics": list(pics)}) + "\n").encode())
            self.wfile.flush()

        if not LOCK.acquire(blocking=False):
            if re.fullmatch(r"\W*(stop|halt|wait|no)\W*", text.strip().lower()):
                emit("done", console_stop())
            else:
                emit("done", "busy: the agent is still working on the last message (press STOP to end it)")
            return
        p = None
        try:
            STOP_FLAG.unlink(missing_ok=True)          # a new message from Oliver lifts an earlier STOP
            errf = open(M.DATA / "web_agent_stderr.log", "a")
            p = subprocess.Popen(agent_cmd(session, text), stdout=subprocess.PIPE, stderr=errf,
                                 stdin=subprocess.DEVNULL, text=True, cwd=HERE)
            RUNNING["p"] = p
            shown = set()
            for line in p.stdout:
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("type") == "assistant":
                    for b in ev["message"].get("content", []):
                        if b.get("type") == "text" and b["text"].strip():
                            ids = [i for i in dict.fromkeys(PIC.findall(b["text"])) if (M.PICS / f"{i}.jpg").exists()]
                            shown.update(ids)
                            emit("text", b["text"], ids[:8])
                        elif b.get("type") == "tool_use":
                            emit("tool", short_tool(b))
                elif ev.get("type") == "user":                  # tool results: show photos the dog just took
                    for b in ev["message"].get("content", []):
                        if b.get("type") != "tool_result":
                            continue
                        c = b.get("content")
                        txt = " ".join(x.get("text", "") for x in c if isinstance(x, dict)) if isinstance(c, list) else str(c)
                        new = [i for i in dict.fromkeys(PIC.findall(txt)) if i.startswith(("p", "l"))
                               and i not in shown and (M.PICS / f"{i}.jpg").exists()]
                        if new:
                            shown.update(new)
                            emit("pics", "", new)
                        if txt.startswith(("REFUSED", "ERROR")):
                            emit("tool", txt[:300])
                elif ev.get("type") == "result":
                    if not ev.get("is_error"):
                        SESSIONS[session] = True
                        SESSF.write_text(json.dumps(SESSIONS))
                    emit("done", f"done in {ev.get('duration_ms', 0) / 1000:.0f} s" + (" (error)" if ev.get("is_error") else ""))
            p.wait()
            if p.returncode and p.returncode > 0:
                emit("done", f"agent exited with an error ({p.returncode}); see go2/data/lab_agent/web_agent_stderr.log")
            elif p.returncode and p.returncode < 0:
                emit("done", "agent turn ended by STOP")
        except (BrokenPipeError, ConnectionResetError):
            # the phone locked or left the page: end the turn rather than let it drive on unseen
            if p and p.poll() is None:
                p.kill()
                http_stop = console_stop("cheetah-lab-page-disconnect")
                print("client left mid-turn:", http_stop, flush=True)
        finally:
            RUNNING.pop("p", None)
            release()
            LOCK.release()
            threading.Thread(target=save_transcripts, daemon=True).start()


def main():
    if "--no-watch" not in sys.argv:
        threading.Thread(target=M.watch, daemon=True).start()
    addr = f"http://{lan_ip()}:{PORT}/?k={KEY}"
    print("open on your phone (lab network):", addr, flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()


if __name__ == "__main__":
    main()
