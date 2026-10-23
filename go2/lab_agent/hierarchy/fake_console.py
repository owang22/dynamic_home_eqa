"""A stand-in for the control PC console's agent API, to test stop/watch logic without the dog.

    python3 fake_console.py --port 8499 --frames ids.txt --fps 4 --go-to-s 30

go2/tests/fake_robot.py stands in for Nav2 over ROS and has no HTTP agent API, so this fakes the HTTP side:
  GET  /frame.jpg      the "live" picture: a playlist of real pictures (go2/data/lab_agent/pictures) that advances
                       at --fps while a move is running (frozen when the dog stands), like the camera of a walking dog
  GET  /state.json     localized, a map pose        GET /agent/status   no owner, safe ok
  POST /agent/claim | release | photo | look        done at once
  POST /agent/go_to | turn | move                   BLOCK for --go-to-s / --turn-s / --move-s seconds, unless
                       /agent/stop arrives: then they return {"result": "aborted", "reason": "stopped"} at once
                       (what the real console returns in that case is not logged anywhere yet: check on the dog)
  POST /agent/stop     always accepted, also while a move blocks (ThreadingHTTPServer)
  GET  /calls          every call with its arrival time (for test assertions)
  replies={"go_to": {...}} makes a move answer at once with that reply (e.g. no_route), to test escalation
"""
from __future__ import annotations

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PICS = Path(__file__).resolve().parents[2] / "data" / "lab_agent" / "pictures"


class Console:
    def __init__(self, frames: list[str], fps: float = 4.0, go_to_s: float = 30, turn_s: float = 4, move_s: float = 5,
                 replies: dict | None = None):
        self.frames, self.fps = frames, fps
        self.replies = replies or {}     # e.g. {"go_to": {"result": "no_route", ...}}: answered at once instead
        self.durs = {"go_to": go_to_s, "turn": turn_s, "move": move_s}
        self.stop_ev = threading.Event()
        self.lock = threading.Lock()
        self.calls: list[dict] = []
        self.moving_since: float | None = None
        self.played = 0.0          # playlist position (frames) accumulated over moves
        self.t0 = time.time()

    def log(self, **kw):
        with self.lock:
            self.calls.append({"t": round(time.time() - self.t0, 3), **kw})

    def frame_index(self) -> int:
        pos = self.played
        if self.moving_since is not None:
            pos += (time.time() - self.moving_since) * self.fps
        return min(int(pos), len(self.frames) - 1)

    def frame(self) -> tuple[int, bytes]:
        i = self.frame_index()
        return i, (PICS / f"{self.frames[i]}.jpg").read_bytes()

    def move(self, name: str, args: dict) -> dict:
        if name in self.replies:
            return dict(self.replies[name])
        self.stop_ev.clear()
        self.moving_since = time.time()
        t0 = time.time()
        stopped = self.stop_ev.wait(self.durs[name])
        self.played += (time.time() - self.moving_since) * self.fps
        self.moving_since = None
        el = round(time.time() - t0, 3)
        if stopped:
            return {"result": "aborted", "reason": "stopped", "elapsed_s": el, "frame_index": self.frame_index()}
        return {"result": "done", "elapsed_s": el, "frame_index": self.frame_index(),
                "map_pose": {"x": 0.0, "y": 0.0, "yaw": 0.0}}


def handler(C: Console):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, code, body, ctype="application/json"):
            b = body if isinstance(body, bytes) else json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            p = self.path.split("?")[0]
            if p == "/frame.jpg":
                i, jpg = C.frame()
                C.log(call="GET /frame.jpg", frame_index=i, frame=C.frames[i])
                return self.send(200, jpg, "image/jpeg")
            if p == "/state.json":
                return self.send(200, {"map": {"mode": "localized", "status": "fake"},
                                       "map_pose": {"x": 0.0, "y": 0.0, "yaw": 0.0}, "control": {"avoid": True}})
            if p == "/agent/status":
                return self.send(200, {"owner": None, "safe": "ok"})
            if p == "/calls":
                return self.send(200, C.calls)
            if p.startswith("/agent/photos/"):
                return self.send(200, C.frame()[1], "image/jpeg")
            self.send(404, {"error": "not faked"})

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
            name = self.path.split("?")[0].removeprefix("/agent/")
            C.log(call=f"POST {name}", args=body)
            if name == "stop":
                C.stop_ev.set()
                return self.send(200, {"result": "done"})
            if name in C.durs:
                out = C.move(name, body)
                C.log(call=f"{name} returned", out=out)
                return self.send(200, out)
            if name == "photo":
                i, _ = C.frame()
                return self.send(200, {"result": "done", "photo": {"id": f"fake_{i}", "url": f"/agent/photos/fake_{i}.jpg",
                                                                   "t": time.time(), "map_pose": {"x": 0, "y": 0, "yaw": 0}}})
            if name in ("claim", "release", "look"):
                return self.send(200, {"result": "done"})
            self.send(404, {"error": "not faked"})
    return H


def serve(frames, port=8499, **kw) -> tuple[ThreadingHTTPServer, Console]:
    """Start in a background thread (for tests). Returns (server, console); server.shutdown() to end."""
    C = Console(frames, **kw)
    srv = ThreadingHTTPServer(("127.0.0.1", port), handler(C))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, C


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8499)
    ap.add_argument("--frames", required=True, help="text file: one picture id per line")
    ap.add_argument("--fps", type=float, default=4.0)
    ap.add_argument("--go-to-s", type=float, default=30)
    a = ap.parse_args()
    ids = [l.strip() for l in open(a.frames) if l.strip()]
    srv, _ = serve(ids, a.port, fps=a.fps, go_to_s=a.go_to_s)
    print(f"fake console on http://127.0.0.1:{a.port} with {len(ids)} frames", flush=True)
    threading.Event().wait()
