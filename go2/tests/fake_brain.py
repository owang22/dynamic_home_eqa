"""A stand-in for robot_brain/server.py with a fixed plan, to test go2_patrol search.

Plan: unreachable, shelf-1, bench_A. bench_A 'contains' the thing. Records every call to
/data/fake_brain_calls.jsonl (image bodies as their size and JPEG check, not the bytes).
"""
import base64
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

PLAN = ["unreachable", "shelf-1", "bench_A"]


def nxt(place):
    i = PLAN.index(place) + 1
    return PLAN[i] if i < len(PLAN) else None


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj):
        b = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        self._send({"ok": True, "model_up": True, "places": 4, "observations": 0})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if "image_b64" in body:
            raw = base64.b64decode(body.pop("image_b64"))
            body["image"] = {"bytes": len(raw), "jpeg": raw[:2] == b"\xff\xd8"}
        with open("/data/fake_brain_calls.jsonl", "a") as f:
            f.write(json.dumps({"path": self.path, **body}) + "\n")
        if self.path == "/ask":
            return self._send({"session": "s1", "target": "red mug", "plan": PLAN, "ranked_by_model": 3,
                               "answer_type": "look", "why": "test plan"})
        if self.path == "/look":
            found = body["place"] == "bench_A"
            n = None if found else nxt(body["place"])
            return self._send({"found": found, "box": [10, 20, 110, 220] if found else None,
                               "image_size": [1280, 720], "description": "a grey picture",
                               "next_place": n, "done": found or n is None, "looks_left": 1})
        if self.path == "/feedback":
            n = nxt(body["place"]) if body.get("failed") else None
            return self._send({"logged": True, "next_place": n, "done": n is None})
        self.send_response(404)
        self.end_headers()


HTTPServer(("127.0.0.1", 8499), H).serve_forever()
