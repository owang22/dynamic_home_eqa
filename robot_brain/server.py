"""HTTP server for the robot brain (see README.md for the API).

    python robot_brain/server.py --data robot_brain/data/lab --positions go2/data/positions.yaml
    python robot_brain/server.py --host 0.0.0.0     # only on a trusted network: there is no login
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import brain as B  # noqa: E402

BRAIN: B.Brain = None


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.log_date_time_string(), fmt % args))

    def do_GET(self):
        BRAIN.refresh_positions()
        if self.path == "/health":
            return self._send(200, {"ok": True, "model_up": B.model_up(), "places": len(BRAIN.places),
                                    "observations": len(BRAIN.memory), "data": str(BRAIN.dir),
                                    "positions_file": str(BRAIN.positions_file) if BRAIN.positions_file else None,
                                    "positions_file_found": bool(BRAIN.positions_file and BRAIN.positions_file.exists())})
        if self.path == "/places":
            return self._send(200, {"places": list(BRAIN.places.values())})
        if self.path.startswith("/memory"):
            return self._send(200, {"observations": BRAIN.memory[-500:], "events": BRAIN.events[-200:]})
        if self.path.startswith("/session/"):
            s = BRAIN.sessions.get(self.path.split("/")[-1])
            return self._send(200 if s else 404, s or {"error": "no such session"})
        self._send(404, {"error": f"no route GET {self.path}"})

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n) or b"{}")
            p = self.path
            if p == "/places":
                out = {"places": BRAIN.set_places(req["places"], replace=req.get("replace", False))}
            elif p == "/observe":
                out = BRAIN.observe(req["place"], req.get("image_path"), req.get("image_b64"), req.get("time"), req.get("pose"))
            elif p == "/ingest_patrol":
                out = BRAIN.ingest_patrol(req["dir"])
            elif p == "/ask":
                out = BRAIN.ask(req["question"], req.get("time"))
            elif p == "/look":
                out = BRAIN.look(req["session"], req["place"], req.get("image_path"), req.get("image_b64"),
                                 req.get("time"), req.get("remember", True))
            elif p == "/feedback":
                out = BRAIN.feedback(req["text"], req.get("session"), req.get("place"), req.get("time"), req.get("failed", False))
            else:
                return self._send(404, {"error": f"no route POST {p}"})
            self._send(200, out)
        except KeyError as e:
            self._send(400, {"error": str(e).strip('"')})
        except (ValueError, FileNotFoundError) as e:
            self._send(400, {"error": str(e)})
        except B.ModelError as e:
            self._send(503, {"error": str(e)})
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            self._send(500, {"error": repr(e)})


def main():
    global BRAIN
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8400)
    ap.add_argument("--data", default=str(pathlib.Path(__file__).parent / "data" / "default"))
    ap.add_argument("--positions", default=None, help="go2_patrol positions.yaml")
    ap.add_argument("--vlm", default=B.VLM_URL)
    ap.add_argument("--path-map", action="append", default=[],
                    help="FROM=TO, e.g. /data=/home/oliver/robot/dynamic_home_eqa/go2/data (repeatable)")
    ap.add_argument("--verify", action="store_true", help="check every yes again on a close-up of its box")
    a = ap.parse_args()
    B.VLM_URL = a.vlm
    B.VERIFY = a.verify
    B.PATH_MAP = [tuple(m.split("=", 1)) for m in a.path_map]
    BRAIN = B.Brain(a.data, a.positions)
    print(f"robot brain on http://{a.host}:{a.port}  data {a.data}  places {len(BRAIN.places)}  "
          f"model {'up' if B.model_up() else 'NOT REACHABLE at ' + B.VLM_URL}", flush=True)
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
