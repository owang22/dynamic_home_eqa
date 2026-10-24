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
import collect  # noqa: E402

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
.d{font-size:14px;padding:6px 10px;border-radius:10px;border:1px solid var(--line)}.d.good{color:var(--accent)}.d.bad{color:var(--stop,#c62828);border-color:currentColor}.n{font-size:14px;color:var(--mute);font-style:italic;padding:0 4px;white-space:pre-wrap}details.t summary{cursor:pointer;list-style:none}details.t summary::-webkit-details-marker{display:none}details.t[open] summary{color:var(--fg)}details.t pre{white-space:pre-wrap;overflow-wrap:anywhere;margin:6px 0 0;max-height:320px;overflow:auto;font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--fg)}select.mdl{font:inherit;font-size:13px;border:1px solid var(--line);border-radius:8px;padding:4px 6px;background:var(--card,var(--bg));color:var(--fg)}
button.s{background:var(--accent);color:var(--bg);border:0;border-radius:10px;padding:0 18px;font-weight:600}
</style></head><body>
<header><b>Lab dog</b><select id="mdl" class="mdl" title="Model for the next message; the conversation carries over"><option value="opus:high">Opus · thorough</option><option value="opus:medium">Opus · quicker</option><option value="sonnet:medium">Sonnet · fast</option><option value="sonnet:low">Sonnet · fastest</option></select><span id="st">ready</span><button id="stop">STOP</button></header>
<div id="log"></div>
<form id="f"><textarea id="q" rows="2" placeholder="Where is the grey backpack?"></textarea><button class="s">Send</button></form>
<script>
const K=new URLSearchParams(location.search).get('k'),S=crypto.randomUUID?crypto.randomUUID():String(Date.now());
const log=document.getElementById('log'),st=document.getElementById('st');
function add(cls,text){const d=document.createElement('div');d.className='m '+cls;d.textContent=text;log.appendChild(d);log.scrollTop=1e9;return d}
function pics(el,ids){if(!ids.length)return;const p=document.createElement('div');p.className='pics';
 ids.forEach(i=>{const im=document.createElement('img');im.src='/pic/'+i+'?k='+K;im.onclick=()=>open(im.src);p.appendChild(im)});el.appendChild(p);log.scrollTop=1e9}
const calls={};
function detail(sum,body){const d=document.createElement('details');d.className='m t';const s=document.createElement('summary');s.textContent=sum;
 const b=document.createElement('pre');b.textContent=body;d.append(s,b);log.appendChild(d);log.scrollTop=1e9;return b}
const mdl=document.getElementById('mdl');try{mdl.value=localStorage.getItem('mdl')||'opus:high'}catch(e){}
mdl.onchange=()=>{try{localStorage.setItem('mdl',mdl.value)}catch(e){}};
function onev(ev,setst){
 if(ev.kind==='text'){pics(add('a',ev.text),ev.pics)}
 else if(ev.kind==='note'){pics(add('n',ev.text),ev.pics)}
 else if(ev.kind==='tool'){lastTool=ev.text.split('(')[0];calls[ev.id]=detail('▸ '+ev.text,'(running…)')}
 else if(ev.kind==='result'){const extra=ev.images?'\n['+ev.images+' picture'+(ev.images>1?'s':'')+' given to the agent]':'';
  if(calls[ev.id]){calls[ev.id].textContent=(ev.text||'(empty)')+extra}else{detail('▸ result',(ev.text||'')+extra)}}
 else if(ev.kind==='pics'){pics(add('t','new photos'),ev.pics)}
 else if(ev.kind==='done'){gotDone=true;const bad=ev.ok===false;add('d '+(bad?'bad':'good'),(bad?'✗ ':'✓ ')+ev.text);setst(ev.text);try{navigator.vibrate&&navigator.vibrate(bad?[90,60,90]:60)}catch(e){}if(document.hidden){document.title=(bad?'✗ ':'✓ ')+'Lab dog'}}}
let T0=0,lastTool='',gotDone=false,timer=null;
function begin(setst){T0=Date.now();gotDone=false;lastTool='';clearInterval(timer);timer=setInterval(()=>setst('working… '+Math.round((Date.now()-T0)/1000)+' s'+(lastTool?' · '+lastTool:'')),1000)}
function finish(setst){clearInterval(timer);if(!gotDone){add('d bad','✗ The connection closed before the agent finished. It may still be running: press STOP if the dog is moving, or ask again.');setst('connection lost')}}
document.addEventListener('visibilitychange',()=>{if(!document.hidden)document.title='Lab dog'});
document.getElementById('stop').onclick=async()=>{st.textContent='sending stop…';
 try{const r=await fetch('/stop?k='+K,{method:'POST'});const t=await r.text();add('t',t);st.textContent=t.startsWith('STOPPED')?'stopped':'STOP FAILED'}catch(e){add('t','STOP FAILED: '+e+' — use the console');st.textContent='STOP FAILED'}};
document.getElementById('f').onsubmit=async e=>{e.preventDefault();const q=document.getElementById('q');const text=q.value.trim();if(!text)return;q.value='';
 add('u',text);begin(t=>st.textContent=t);
 try{const r=await fetch('/ask?k='+K,{method:'POST',body:JSON.stringify({session:S,text,model:mdl.value})});const rd=r.body.getReader(),dec=new TextDecoder();let buf='';
  for(;;){const {value,done}=await rd.read();if(done)break;buf+=dec.decode(value,{stream:true});let i;
   while((i=buf.indexOf('\n'))>=0){const line=buf.slice(0,i);buf=buf.slice(i+1);if(!line)continue;const ev=JSON.parse(line);
    onev(ev,t=>st.textContent=t)}}}
 catch(err){gotDone=true;clearInterval(timer);add('d bad','✗ Lost the connection: '+err);st.textContent='error'}finish(t=>st.textContent=t)};
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


MODELS = {"opus:high": ("opus", "high"), "opus:medium": ("opus", "medium"),     # page menu -> --model, --effort;
          "sonnet:medium": ("sonnet", "medium"), "sonnet:low": ("sonnet", "low")}  # the conversation carries over


def agent_cmd(session, text, choice="opus:high"):
    resume = ["--resume", session] if SESSIONS.get(session) else ["--session-id", session]
    model, effort = MODELS.get(choice, MODELS["opus:high"])
    return ["claude", "-p", "--model", model, "--effort", effort, "--mcp-config", str(HERE / "mcp.json"), "--strict-mcp-config",
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

        wlock = threading.Lock()
        ep = body.get("episode")          # Collect mode on the console page: record the turn in collect.py's log
        rec = {"answer": [], "tools": [], "t0": __import__("time").time()}
        if ep:
            collect.log("prompt", ep, session=session, turn=body.get("turn"), text=text, model=body.get("model"),
                        expected=str(body.get("expected") or "")[:4000] or None)

        def emit(kind, text, pics=(), **extra):
            if ep and kind == "text":
                rec["answer"].append(text)
            elif ep and kind == "tool":
                rec["tools"].append(text[:300])
            elif ep and kind == "done":
                collect.log("done", ep, session=session, turn=body.get("turn"), ok=extra.get("ok"), text=text,
                            answer="\n\n".join(rec["answer"]), tools=rec["tools"],
                            secs=round(__import__("time").time() - rec["t0"], 1))
            with wlock:
                self.wfile.write((json.dumps({"kind": kind, "text": text, "pics": list(pics), **extra}) + "\n").encode())
                self.wfile.flush()

        def heartbeat(done):       # a blank line every 15 s: the Cloudflare tunnel drops a reply that is silent ~100 s
            while not done.wait(15):
                try:
                    with wlock:
                        self.wfile.write(b"\n")
                        self.wfile.flush()
                except OSError:
                    return

        if not LOCK.acquire(blocking=False):
            if re.fullmatch(r"\W*(stop|halt|wait|no)\W*", text.strip().lower()):
                emit("done", console_stop())
            else:
                emit("done", "busy: the agent is still working on the last message (press STOP to end it)", ok=False)
            return
        p = None
        try:
            STOP_FLAG.unlink(missing_ok=True)          # a new message from Oliver lifts an earlier STOP
            errf = open(M.DATA / "web_agent_stderr.log", "a")
            p = subprocess.Popen(agent_cmd(session, text, str(body.get("model", "opus:high"))), stdout=subprocess.PIPE, stderr=errf,
                                 stdin=subprocess.DEVNULL, text=True, cwd=HERE)
            RUNNING["p"] = p
            shown = set()
            beat = threading.Event()
            threading.Thread(target=heartbeat, args=(beat,), daemon=True).start()
            pending = []           # the agent's last text: a note if a tool call follows it, else part of the answer
            said = {"text": False, "ended": False}

            def flush(kind):
                while pending:
                    t, ids = pending.pop(0)
                    said["text"] = said["text"] or kind == "text"
                    emit(kind, t, ids)
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
                            flush("text")
                            pending.append((b["text"], ids[:8]))
                        elif b.get("type") == "tool_use":
                            flush("note")
                            emit("tool", short_tool(b), id=b.get("id", ""))
                elif ev.get("type") == "user":                  # tool results: show photos the dog just took
                    for b in ev["message"].get("content", []):
                        if b.get("type") != "tool_result":
                            continue
                        c = b.get("content")
                        txt = " ".join(x.get("text", "") for x in c if isinstance(x, dict)) if isinstance(c, list) else str(c)
                        n_img = sum(1 for x in c if isinstance(x, dict) and x.get("type") == "image") if isinstance(c, list) else 0
                        emit("result", txt[:6000] + (" …" if len(txt) > 6000 else ""), id=b.get("tool_use_id", ""),
                             images=n_img)
                        new = [i for i in dict.fromkeys(PIC.findall(txt)) if i.startswith(("p", "l"))
                               and i not in shown and (M.PICS / f"{i}.jpg").exists()]
                        if new:
                            shown.update(new)
                            emit("pics", "", new)
                        if txt.startswith(("REFUSED", "ERROR")):
                            emit("tool", txt[:300])
                elif ev.get("type") == "result":
                    flush("text")
                    if not ev.get("is_error"):
                        SESSIONS[session] = True
                        SESSF.write_text(json.dumps(SESSIONS))
                    secs = ev.get("duration_ms", 0) / 1000
                    if ev.get("is_error"):
                        emit("done", f"failed after {secs:.0f} s: {str(ev.get('result') or ev.get('subtype') or 'error')[:300]}", ok=False)
                    else:
                        if not said["text"]:
                            emit("text", "(The agent finished without writing a reply.)")
                        emit("done", f"finished in {secs:.0f} s", ok=True)
                    said["ended"] = True
            flush("text")
            beat.set()
            p.wait()
            if p.returncode and p.returncode < 0:
                emit("done", "stopped: the agent turn was ended by STOP", ok=False)
            elif p.returncode and p.returncode > 0 and not said["ended"]:
                errf.flush()
                tail = (M.DATA / "web_agent_stderr.log").read_text(errors="replace").strip().splitlines()[-3:]
                emit("done", f"failed: the agent exited with code {p.returncode}. " + " | ".join(tail)[-400:], ok=False)
            elif not said["ended"]:
                emit("done", "ended without a result from the agent (no reply, no error)", ok=False)
        except (BrokenPipeError, ConnectionResetError):
            # the phone locked or left the page: end the turn rather than let it drive on unseen
            if ep:
                collect.log("done", ep, session=session, turn=body.get("turn"), ok=False,
                            text="the page disconnected mid-turn; the turn was ended",
                            answer="\n\n".join(rec["answer"]), tools=rec["tools"])
            if p and p.poll() is None:
                p.kill()
                http_stop = console_stop("cheetah-lab-page-disconnect")
                print("client left mid-turn:", http_stop, flush=True)
        except Exception as e:  # noqa: BLE001 - anything else: say so on the page instead of going quiet
            try:
                emit("done", f"failed: {type(e).__name__}: {e}"[:400], ok=False)
            except OSError:
                pass
            if p and p.poll() is None:
                p.kill()
                console_stop("cheetah-lab-page-error")
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
