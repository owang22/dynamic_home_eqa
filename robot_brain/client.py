"""Client for the robot brain. Standard library only, Python 3.10+.

    from client import Brain
    b = Brain()                                   # http://127.0.0.1:8400
    b.ingest_patrol("/data/patrols/2026-10-14/1000")
    s = b.ask("where is the red mug?")            # {"session", "plan": [ids], ...}
    r = b.look(s["session"], s["plan"][0], image_path="/data/look.jpg")
    while not r["done"]:
        ...walk to r["next_place"], photograph...
        r = b.look(s["session"], r["next_place"], image_path=...)
"""
from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request


class BrainError(RuntimeError):
    pass


class Brain:
    def __init__(self, url: str = "http://127.0.0.1:8400", timeout: float = 600):
        self.url, self.timeout = url.rstrip("/"), timeout

    def _call(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.url + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            try:
                msg = json.loads(e.read()).get("error", "")
            except Exception:  # noqa: BLE001
                msg = ""
            raise BrainError(f"{method} {path}: HTTP {e.code} {msg}") from None

    @staticmethod
    def _image(image_path=None, image_bytes=None):
        if image_bytes is not None:
            return {"image_b64": base64.b64encode(image_bytes).decode()}
        if image_path is not None:
            return {"image_path": str(image_path)}
        raise ValueError("give image_path or image_bytes")

    # -- state
    def health(self):
        return self._call("GET", "/health")

    def places(self):
        return self._call("GET", "/places")["places"]

    def set_places(self, places, replace=False):
        """places: [{"id": "bench_A", "room": "lab", "description": "workbench by the window"}, ...]"""
        return self._call("POST", "/places", {"places": places, "replace": replace})

    def memory(self):
        return self._call("GET", "/memory")

    def session(self, session_id):
        return self._call("GET", f"/session/{session_id}")

    # -- seeing
    def observe(self, place, image_path=None, image_bytes=None, time=None, pose=None):
        """One picture taken at a place. image_path must be readable by the brain's process."""
        return self._call("POST", "/observe", {"place": place, "time": time, "pose": pose,
                                               **self._image(image_path, image_bytes)})

    def ingest_patrol(self, folder):
        """A go2_patrol folder (<date>/<HHMM> with patrol.json); only photographed positions are read."""
        return self._call("POST", "/ingest_patrol", {"dir": str(folder)})

    # -- searching
    def ask(self, question, time=None):
        return self._call("POST", "/ask", {"question": question, "time": time})

    def look(self, session, place, image_path=None, image_bytes=None, time=None, remember=True):
        return self._call("POST", "/look", {"session": session, "place": place, "time": time, "remember": remember,
                                            **self._image(image_path, image_bytes)})

    def feedback(self, text, session=None, place=None, failed=False, time=None):
        """failed=True with a place: the robot could not reach or photograph it; returns the next place."""
        return self._call("POST", "/feedback", {"text": text, "session": session, "place": place,
                                                "failed": failed, "time": time})
