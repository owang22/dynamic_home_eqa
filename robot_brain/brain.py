"""Perception, memory and planning for a robot that is asked where things are.

The brain never moves the robot. The controller (go2/go2_patrol) walks, photographs and calls the
HTTP server (server.py), which calls this module. Model: Qwen3.8-27B with vision on the local vLLM
server (serve_vlm.sh, 127.0.0.1:8300). Every answer that names a place is forced by the output
grammar to be one of the robot's own position ids.

Memory is a JSON-lines file of observations: what the model listed in each picture, under the place
the robot stood at and the time. Questions are answered from the last MEMORY_DAYS of it.
"""
from __future__ import annotations

import base64
import datetime as dt
import io
import json
import math
import pathlib
import threading
import time
import urllib.request
import uuid

from PIL import Image

VLM_URL = "http://127.0.0.1:8300/v1/chat/completions"
MODEL = "Qwen/Qwen3.8-27B"
MAX_SIDE = 960            # pictures are downscaled to this before the model sees them
MAX_LOOKS = 8
MEMORY_DAYS = 7
NOTES_CHAR_LIMIT = 60000  # about 15k tokens of notes at most; oldest dropped first
VERIFY = False            # --verify: a yes is checked again on a close-up of its box (too strict: see README)

LIST_PROMPT = ("This picture was taken by a home robot standing at {place}. List the separate objects you "
               "can see lying on or in furniture or on the floor (not furniture, not things built into the "
               "room). Use short everyday names. For each give its bounding box as bbox_2d [x1, y1, x2, y2] "
               "in coordinates from 0 to 1000 relative to the picture width and height.")
LIST_SCHEMA = {"type": "object", "properties": {"objects": {"type": "array", "maxItems": 30, "items": {
    "type": "object", "properties": {
        "name": {"type": "string", "maxLength": 40},
        "bbox_2d": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 1000},
                    "minItems": 4, "maxItems": 4}},
    "required": ["name", "bbox_2d"]}}}, "required": ["objects"]}


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def parse_time(s: str | None) -> dt.datetime:
    if not s:
        return dt.datetime.now().astimezone()
    t = dt.datetime.fromisoformat(s)
    return t if t.tzinfo else t.astimezone()


class ModelError(RuntimeError):
    pass


def _jpeg_b64(img: Image.Image) -> str:
    b = io.BytesIO()
    img.convert("RGB").save(b, "JPEG", quality=88)
    return base64.b64encode(b.getvalue()).decode()


PATH_MAP: list[tuple[str, str]] = []   # (prefix the controller uses, prefix on this machine)


def host_path(p: str) -> str:
    """Paths sent from inside the controller's container (e.g. /data/...) mapped to this machine."""
    for a, b in PATH_MAP:
        if p.startswith(a):
            return b + p[len(a):]
    return p


def load_image(image_path: str | None = None, image_b64: str | None = None) -> Image.Image:
    if image_path:
        return Image.open(host_path(image_path))
    if image_b64:
        return Image.open(io.BytesIO(base64.b64decode(image_b64)))
    raise ValueError("give image_path or image_b64")


def shrink(img: Image.Image) -> Image.Image:
    s = MAX_SIDE / max(img.size)
    return img if s >= 1 else img.resize((round(img.size[0] * s), round(img.size[1] * s)), Image.LANCZOS)


def ask_model(prompt: str, images=(), captions=None, schema=None, max_tokens=1500, timeout=600) -> str:
    content = []
    for i, img in enumerate(images):
        if captions:
            content.append({"type": "text", "text": captions[i]})
        content.append({"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + _jpeg_b64(shrink(img))}})
    content.append({"type": "text", "text": prompt})
    body = {"model": MODEL, "messages": [{"role": "user", "content": content}], "temperature": 0.0,
            "max_tokens": max_tokens, "chat_template_kwargs": {"enable_thinking": False}}
    if schema:
        body["response_format"] = {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}}
    req = urllib.request.Request(VLM_URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    last = None
    for attempt in range(3):
        try:
            out = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
            return out["choices"][0]["message"].get("content") or ""
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2)
    raise ModelError(f"vision model at {VLM_URL} did not answer: {last}")


def model_up() -> bool:
    try:
        urllib.request.urlopen(VLM_URL.replace("/chat/completions", "/models"), timeout=5).read()
        return True
    except Exception:  # noqa: BLE001
        return False


def to_pixels(b, size):
    """bbox_2d in 0-1000 -> pixels of the picture as the robot sent it."""
    w, h = size
    return [round(b[0] * w / 1000), round(b[1] * h / 1000), round(b[2] * w / 1000), round(b[3] * h / 1000)]


class Brain:
    def __init__(self, data_dir: str | pathlib.Path, positions_file: str | None = None):
        self.dir = pathlib.Path(data_dir)
        (self.dir / "pictures").mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.places: dict[str, dict] = {}          # id -> {id, x?, y?, room?, description?}
        self.sessions: dict[str, dict] = {}
        self.memory: list[dict] = []
        self.events: list[dict] = []
        p = self.dir / "places.json"
        if p.exists():
            self.places = json.loads(p.read_text())
        self.positions_file = pathlib.Path(positions_file) if positions_file else None
        self._positions_mtime = None
        self.refresh_positions()
        m = self.dir / "memory.jsonl"
        if m.exists():
            self.memory = [json.loads(l) for l in m.read_text().splitlines() if l.strip()]
        s = self.dir / "sessions.json"
        if s.exists():
            self.sessions = json.loads(s.read_text())

    # ------------------------------------------------------------------ places
    def refresh_positions(self):
        """Read the controller's positions file when it first appears or whenever it changes, so the
        server can start before any position is recorded."""
        f = self.positions_file
        if f is None or not f.exists():
            return False
        m = f.stat().st_mtime_ns
        if m == self._positions_mtime:
            return False
        try:
            self.load_positions(f)
        except Exception:  # noqa: BLE001  (half-written file: try again on the next call)
            return False
        self._positions_mtime = m
        return True

    def load_positions(self, path):
        import yaml
        data = yaml.safe_load(pathlib.Path(path).read_text()) or {}
        items = data.get("positions", []) if isinstance(data, dict) else data
        for it in items:
            pid = str(it["id"])
            cur = self.places.get(pid, {})
            cur.update({"id": pid, "x": it.get("x"), "y": it.get("y")})
            self.places[pid] = cur
        self._save_places()
        return list(self.places)

    def set_places(self, items: list[dict], replace: bool = False):
        if replace:
            self.places = {}
        for it in items:
            pid = str(it["id"])
            cur = self.places.get(pid, {"id": pid})
            cur.update({k: v for k, v in it.items() if v is not None})
            cur["id"] = pid
            self.places[pid] = cur
        self._save_places()
        return list(self.places)

    def _save_places(self):
        (self.dir / "places.json").write_text(json.dumps(self.places, indent=1))

    def place_label(self, pid):
        p = self.places.get(pid, {})
        extra = ", ".join(v for v in [p.get("description"), p.get("room")] if v)
        return f"{pid} ({extra})" if extra else pid

    def _check_place(self, pid):
        if pid not in self.places:
            raise KeyError(f"unknown place {pid!r}; known places: {sorted(self.places)}")

    # ------------------------------------------------------------------ observe
    def observe(self, place, image_path=None, image_b64=None, time_iso=None, pose=None, source="observe"):
        self.refresh_positions()
        self._check_place(place)
        img = load_image(image_path, image_b64)
        when = parse_time(time_iso)
        keep = self.dir / "pictures" / f"{when.strftime('%Y%m%d_%H%M%S')}_{place}_{uuid.uuid4().hex[:6]}.jpg"
        img.convert("RGB").save(keep, quality=90)
        t0 = time.time()
        text = ask_model(LIST_PROMPT.format(place=self.place_label(place)), [img], schema=LIST_SCHEMA)
        try:
            objs = json.loads(text)["objects"]
        except Exception:  # noqa: BLE001
            objs = []
        seen, out = set(), []
        for o in objs:
            name = o["name"].strip(" -*•.").lower()
            if not name or (name, tuple(o["bbox_2d"])) in seen:
                continue
            seen.add((name, tuple(o["bbox_2d"])))
            out.append({"name": name, "box": to_pixels(o["bbox_2d"], img.size)})
        rec = {"place": place, "time": when.isoformat(timespec="seconds"), "objects": out, "picture": str(keep),
               "size": list(img.size), "pose": pose, "source": source, "seconds": round(time.time() - t0, 1)}
        with self.lock:
            self.memory.append(rec)
            with open(self.dir / "memory.jsonl", "a") as f:
                f.write(json.dumps(rec) + "\n")
        return rec

    def ingest_patrol(self, folder):
        self.refresh_positions()
        import concurrent.futures as cf
        folder = pathlib.Path(host_path(str(folder)))
        log = json.loads((folder / "patrol.json").read_text())
        done = {(r["place"], r["time"]) for r in self.memory}
        out = {"observed": [], "skipped": []}
        jobs = []
        for p in log.get("positions", []):
            pid = str(p.get("id"))
            if p.get("result") != "photographed":
                out["skipped"].append({"id": pid, "why": p.get("result")})
                continue
            if pid not in self.places:
                self.places[pid] = {"id": pid, "x": (p.get("target") or {}).get("x"), "y": (p.get("target") or {}).get("y")}
                self._save_places()
            when = parse_time(p.get("taken") or log.get("started")).isoformat(timespec="seconds")
            if (pid, when) in done:
                out["skipped"].append({"id": pid, "why": "already in memory"})
                continue
            jobs.append((pid, str(folder / p.get("picture", f"{pid}.jpg")), when, p.get("actual")))
        with cf.ThreadPoolExecutor(4) as ex:
            recs = list(ex.map(lambda j: self.observe(j[0], image_path=j[1], time_iso=j[2], pose=j[3],
                                                      source=f"patrol {folder}"), jobs))
        out["observed"] = [{"id": r["place"], "objects": [o["name"] for o in r["objects"]]} for r in recs]
        return out

    # ------------------------------------------------------------------ ask
    def notes_text(self, before: dt.datetime) -> str:
        """Day-by-day notes: what was seen at each place, newest last, oldest dropped past the limit."""
        start = before - dt.timedelta(days=MEMORY_DAYS)
        recs = sorted((r for r in self.memory if start <= parse_time(r["time"]) < before), key=lambda r: r["time"])
        lines = []
        for r in recs:
            t = parse_time(r["time"])
            names = list(dict.fromkeys(o["name"] for o in r["objects"]))
            lines.append(f"{t.strftime('%a %d %b %H:%M')}  at {self.place_label(r['place'])}: "
                         + (", ".join(names) if names else "nothing seen"))
        events = [e for e in self.events if start <= parse_time(e["time"]) < before]
        for e in events:
            lines.append(f"{parse_time(e['time']).strftime('%a %d %b %H:%M')}  note from the robot: {e['text']}")
        lines.sort()
        text = "\n".join(lines)
        while len(text) > NOTES_CHAR_LIMIT and lines:
            lines.pop(0)
            text = "\n".join(lines)
        return text

    def nearest_fill(self, order):
        """Pad a plan with the remaining places, nearest first from the last one (when positions are known)."""
        left = [p for p in self.places if p not in order]
        out = list(order)
        cur = self.places.get(out[-1]) if out else None
        while left:
            if cur and cur.get("x") is not None and all(self.places[p].get("x") is not None for p in left):
                nxt = min(left, key=lambda p: math.hypot(self.places[p]["x"] - cur["x"], self.places[p]["y"] - cur["y"]))
            else:
                nxt = left[0]
            out.append(nxt)
            left.remove(nxt)
            cur = self.places[nxt]
        return out

    def ask(self, question, time_iso=None):
        self.refresh_positions()
        if not self.places:
            raise KeyError("no places known: POST /places or start the server with --positions")
        when = parse_time(time_iso)
        ids = sorted(self.places)
        notes = self.notes_text(when)
        prompt = (
            "You are a home robot. You walk to fixed places in the home, take pictures and note what you "
            "see. Here are your notes from the past days (place ids with descriptions):\n\n"
            f"{notes or '(no notes yet)'}\n\n"
            f"It is now {when.strftime('%a %d %b %H:%M')}. Someone asks: \"{question}\"\n"
            "List up to 8 places to go and look, most likely first. Think about where it was last seen, "
            "where it usually is, and where people leave it at this time of day.\n"
            "target: the thing exactly as the person named it, with all its words (\"evening shirt\", not "
            "\"shirt\"; \"work loafers\", not \"shoes\").\n"
            "answer_type: \"look\" in almost every case. Use \"put away\" or \"someone has it\" only when your "
            "notes say so directly (for example a note from the robot that a person took it); use \"not in my "
            "notes\" when your notes never mention anything like it. Always list places to look.\n"
            "Places (use these ids exactly):\n"
            + "\n".join(self.place_label(p) for p in ids))
        schema = {"type": "object", "properties": {
            "target": {"type": "string", "maxLength": 60},
            "answer_type": {"type": "string", "enum": ["look", "not in my notes", "put away", "someone has it"]},
            "plan": {"type": "array", "items": {"type": "string", "enum": ids}, "maxItems": MAX_LOOKS},
            "why": {"type": "string", "maxLength": 400}},
            "required": ["target", "answer_type", "plan", "why"]}
        t0 = time.time()
        ans = json.loads(ask_model(prompt, schema=schema, max_tokens=900))
        plan = list(dict.fromkeys(p for p in ans["plan"] if p in self.places))
        ranked = len(plan)
        plan = self.nearest_fill(plan)[:MAX_LOOKS]
        sid = uuid.uuid4().hex[:10]
        sess = {"session": sid, "question": question, "target": ans["target"], "asked": when.isoformat(timespec="seconds"),
                "plan": plan, "ranked_by_model": ranked, "answer_type": ans["answer_type"], "why": ans["why"],
                "looked": [], "failed": [], "found": None, "done": False, "seconds": round(time.time() - t0, 1)}
        with self.lock:
            self.sessions[sid] = sess
            self._save_sessions()
        return {k: sess[k] for k in ["session", "target", "plan", "ranked_by_model", "answer_type", "why", "seconds"]}

    def _save_sessions(self):
        (self.dir / "sessions.json").write_text(json.dumps(self.sessions, indent=1))

    def _next(self, sess):
        tried = set(sess["looked"]) | set(sess["failed"])
        for p in sess["plan"]:
            if p not in tried:
                return p
        return None

    # ------------------------------------------------------------------ look
    def look(self, session, place, image_path=None, image_b64=None, time_iso=None, remember=True):
        self.refresh_positions()
        sess = self.sessions[session]
        self._check_place(place)
        img = load_image(image_path, image_b64)
        t = sess["target"]
        prompt = (f"You are a home robot standing at {self.place_label(place)}, looking for the {t} "
                  f"(the question was: \"{sess['question']}\"). Is the {t} itself visible in this picture? A "
                  f"similar thing of another kind does not count. If yes, give its "
                  "bounding box as bbox_2d [x1, y1, x2, y2] in coordinates from 0 to 1000; if no, give [0, 0, 0, 0]. "
                  "Describe in one short sentence what you see where it would be.")
        schema = {"type": "object", "properties": {
            "visible": {"type": "string", "enum": ["yes", "no"]},
            "bbox_2d": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 1000}, "minItems": 4, "maxItems": 4},
            "description": {"type": "string", "maxLength": 200}},
            "required": ["visible", "bbox_2d", "description"]}
        t0 = time.time()
        ans = json.loads(ask_model(prompt, [img], schema=schema, max_tokens=300))
        found = ans["visible"] == "yes"
        box = to_pixels(ans["bbox_2d"], img.size) if found and any(ans["bbox_2d"]) else None
        checked = None
        if found and box and VERIFY:
            checked = self._verify(img, box, t)
            found = checked
            if not found:
                box = None
        with self.lock:
            if place not in sess["looked"]:
                sess["looked"].append(place)
            if found:
                sess["found"], sess["done"] = place, True
            nxt = None if found else self._next(sess)
            if nxt is None:
                sess["done"] = True
            self._save_sessions()
        if remember:   # the look is also an observation, listed in the background so the reply is not delayed
            threading.Thread(target=self._remember, args=(place, img.copy(), time_iso), daemon=True).start()
        return {"session": session, "place": place, "found": found, "box": box, "image_size": list(img.size), "first_answer": ans["visible"], "checked_close_up": checked,
                "description": ans["description"], "next_place": nxt, "done": sess["done"],
                "looks_left": len([p for p in sess["plan"] if p not in sess["looked"] and p not in sess["failed"]]),
                "seconds": round(time.time() - t0, 1)}

    def _verify(self, img, box, target):
        """Second look at a yes: the box region enlarged, next to the whole picture, asked again strictly."""
        x1, y1, x2, y2 = box
        w, h = x2 - x1, y2 - y1
        m = max(w, h) * 0.3 + 10
        crop = img.crop((max(0, x1 - m), max(0, y1 - m), min(img.size[0], x2 + m), min(img.size[1], y2 + m)))
        if max(crop.size) < 448:
            k = 448 / max(crop.size)
            crop = crop.resize((round(crop.size[0] * k), round(crop.size[1] * k)), Image.LANCZOS)
        prompt = (f"The second picture is a close-up of one object from the first picture. Is that object a {target}? "
                  f"Answer no if it is a different kind of thing, even a similar one.")
        schema = {"type": "object", "properties": {"answer": {"type": "string", "enum": ["yes", "no"]}}, "required": ["answer"]}
        try:
            return json.loads(ask_model(prompt, [img, crop], captions=["Whole picture:", "Close-up:"], schema=schema, max_tokens=20))["answer"] == "yes"
        except Exception:  # noqa: BLE001
            return True

    def _remember(self, place, img, time_iso):
        b = io.BytesIO()
        img.convert("RGB").save(b, "JPEG", quality=90)
        try:
            self.observe(place, image_b64=base64.b64encode(b.getvalue()).decode(), time_iso=time_iso, source="look")
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------ feedback
    def feedback(self, text, session=None, place=None, time_iso=None, failed=False):
        ev = {"time": parse_time(time_iso).isoformat(timespec="seconds"), "text": text, "session": session, "place": place}
        with self.lock:
            self.events.append(ev)
            with open(self.dir / "events.jsonl", "a") as f:
                f.write(json.dumps(ev) + "\n")
            out = {"logged": True}
            if session and session in self.sessions:
                sess = self.sessions[session]
                if place and failed and place not in sess["failed"]:
                    sess["failed"].append(place)
                nxt = self._next(sess)
                if nxt is None:
                    sess["done"] = True
                out.update(next_place=nxt, done=sess["done"])
                self._save_sessions()
        return out
