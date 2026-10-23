"""Memory-only lab tools over a frozen copy of the picture memory: no console access at all.

The same search and wording as server.py (search_memory, show_pictures, people_seen, list_places), but
- the records come from a given index file, optionally cut to its first K lines (the memory as it was at a
  logged turn: index.jsonl is append-only, so a line prefix is the memory at some moment),
- "today" / "HH:MM" are relative to a given `now` (the turn's time), not the wall clock,
- places come from a saved copy, so nothing calls the console (memory.places() is replaced in this process).

Used by the replay harness, by the small agent, and by mem_mcp.py (the MCP server the big model gets in replay).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "replay"))
# The 2026-10-22 word search (the one that produced the logged answers), pinned: memory.py changes tonight.
# Set HIER_MEMORY=live to use go2/lab_agent/memory.py instead.
if __import__("os").environ.get("HIER_MEMORY") == "live":
    sys.path.insert(0, str(HERE.parent))
    import memory as M  # noqa: E402
else:
    import memory_2026_10_22 as M  # noqa: E402

DEFAULT_PLACES = HERE / "replay" / "data" / "places_snapshot.json"


class Memory:
    def __init__(self, recs: list[dict], places: dict, now: float, pics_dir: Path = M.PICS):
        self.recs = [r for r in recs]
        self.P = places
        self.now = now
        self.pics_dir = pics_dir
        M.places = lambda: self.P            # memory.with_places()/nearest_place() must not ask the console
        M.CONSOLE = "http://127.0.0.1:9"     # and if anything still tries, it goes nowhere
        self.by = {r["id"]: r for r in self.recs}

    @classmethod
    def from_index(cls, index: Path, upto_line: int | None = None, now: float | None = None,
                   places: Path = DEFAULT_PLACES) -> "Memory":
        by = {}
        with open(index) as f:
            for i, l in enumerate(f):
                if upto_line is not None and i >= upto_line:
                    break
                if l.strip():
                    r = json.loads(l)
                    by[r["id"]] = r                # a later line for the same id wins, as in memory.load()
        recs = list(by.values())
        now = now if now is not None else max(r["t"] for r in recs) + 60
        return cls(recs, json.loads(Path(places).read_text()), now)

    # ---- helpers ----
    def when(self, s: str | None):
        if not s:
            return None
        s = s.strip()
        day0 = datetime.fromtimestamp(self.now).replace(hour=0, minute=0, second=0, microsecond=0)
        if s == "today":
            return day0.timestamp()
        if s == "yesterday":
            return day0.timestamp() - 86400
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(s, fmt).timestamp()
            except ValueError:
                pass
        if ":" in s:
            h, m = map(int, s.split(":")[:2])
            return day0.replace(hour=h, minute=m).timestamp()
        raise ValueError(f"time '{s}' not understood: use 'HH:MM', 'YYYY-MM-DD HH:MM', 'YYYY-MM-DD', 'today' or 'yesterday'")

    def span(self):
        if not self.recs:
            return "empty"
        a, b = min(self.recs, key=lambda r: r["t"]), max(self.recs, key=lambda r: r["t"])
        return f"{a['time']} to {b['time']}"

    def describe_rec(self, r):
        M.with_places([r], self.P)
        s = r.get("seen") or {}
        if r.get("seen") is None:
            s = {"summary": "(no description yet; look at the picture)"}
        pose = ("pose unknown" if r.get("x") is None or r.get("yaw_deg") is None
                else f"map ({r['x']:.2f}, {r['y']:.2f}) facing {r['yaw_deg']:.0f} deg")
        objs = ", ".join(f"{o['colour']} {o['name']} ({o['on']}, across {o['across']:.2f})" for o in s.get("objects", []))
        return (f"[{r['id']}] {r['time']} near {r.get('near_place')} ({r.get('near_place_m')} m), {pose}, look {r.get('look_deg', 0)} deg\n"
                f"  seen: {s.get('summary')}\n  people: {s.get('people')} {s.get('people_notes') or ''}\n"
                f"  objects: {objs}\n  states: {'; '.join(s.get('states', [])) or 'none'}")

    # ---- tools (same output text as server.py) ----
    def search_memory(self, query: str, since: str = "", until: str = "", place: str = "", limit: int = 12) -> str:
        kw = {"mode": "words", "synonyms": False} if "word_hits" in dir(M) else {}
        hits = M.search(query, since=self.when(since), until=self.when(until), place=place or None,
                        k=max(1, min(30, int(limit or 12))), recs=self.recs, **kw)
        n = len(self.recs)
        if not hits:
            return f"no pictures match '{query}' (memory: {n} pictures, {self.span()})"
        lines = [f"{len(hits)} matches (memory: {n} pictures, {self.span()}):"]
        for b in hits:
            mt = b.get("match")
            lines.append(f"[{b['id']}] {b['time']} near {b['near_place']}, pose {b['pose']}; "
                         + (f"match: {mt['colour']} {mt['name']} on {mt['on']} at across {mt['across']:.2f}; " if mt else "")
                         + f"people {b['people']}; {b['summary']}")
        return "\n".join(lines)

    def show_pictures(self, ids: list[str]) -> tuple[str, list[tuple[str, bytes]]]:
        """Text with full descriptions, and [(id, jpg)] for the pictures found."""
        txt, jpgs = [], []
        for i in list(ids)[:6]:
            r = self.by.get(i)
            if not r:
                txt.append(f"[{i}] not in memory")
                continue
            txt.append(self.describe_rec(r))
            p = self.pics_dir / f"{i}.jpg"
            if p.exists():
                jpgs.append((i, p.read_bytes()))
        return "\n".join(txt), jpgs

    def people_seen(self, since: str = "today", until: str = "") -> str:
        t0, t1 = self.when(since), self.when(until)
        recs = M.with_places([r for r in self.recs if r.get("seen") and (not t0 or r["t"] >= t0)
                              and (not t1 or r["t"] <= t1)], self.P)
        if not recs:
            return "no pictures in that time"
        hours = {}
        recs.sort(key=lambda r: r["t"])
        for r in recs:
            h = datetime.fromtimestamp(r["t"]).strftime("%a %H:00")
            n, p, mx = hours.get(h, (0, 0, 0))
            hours[h] = (n + 1, p + (r["seen"]["people"] > 0), max(mx, r["seen"]["people"]))
        lines = ["per hour: pictures / with people / most people in one picture"]
        lines += [f"  {h}: {n} / {p} / {mx}" for h, (n, p, mx) in hours.items()]
        lines.append("pictures with people:")
        lines += [f"[{r['id']}] {r['time']} near {r['near_place']}: {r['seen']['people']} - {r['seen']['people_notes']}"
                  for r in recs if r["seen"]["people"] > 0][:60]
        return "\n".join(lines)

    def list_places(self) -> str:
        return "\n".join(f"{pid}: stand ({p['x']:.2f}, {p['y']:.2f})"
                         + (f", looks at ({p['target']['x']:.2f}, {p['target']['y']:.2f})" if p.get("target") else "")
                         + (f" - {p['note']}" if p.get("note") else "") for pid, p in self.P.items())

    def status(self, dog_text: str | None = None) -> str:
        newest = max(self.recs, key=lambda r: r["t"])["time"] if self.recs else "none"
        mem = f"memory: {len(self.recs)} pictures, newest {newest}"
        head = dog_text or "console not available in this replay (the dog is not driven here)"
        return f"{head}. {mem}. time now {datetime.fromtimestamp(self.now):%a %Y-%m-%d %H:%M}"

    # ---- locate (as server.py, but the vision model is a given LLM and there is no route check) ----
    def locate(self, thing: str, ids: list[str], vlm) -> str:
        import math
        import numpy as np
        sch = {"type": "object", "properties": {"why": {"type": "string", "maxLength": 160},
                                                "present": {"type": "string", "enum": ["yes", "no"]},
                                                "across": {"type": "number", "minimum": 0, "maximum": 1},
                                                "metres_away": {"type": "number", "minimum": 0.2, "maximum": 8}},
               "required": ["why", "present", "across", "metres_away"]}
        from llm import image_part
        sights = []
        for i in list(ids)[:12]:
            r = self.by.get(i)
            if not r or r.get("x") is None or r.get("yaw_deg") is None:
                continue
            p = self.pics_dir / f"{i}.jpg"
            q = (f"A robot dog's camera picture (camera 0.4 m above the floor, about 73 degrees wide). Is {thing} "
                 f"in it? If yes: where is its centre across the picture (0 = left edge, 1 = right edge), and about "
                 f"how many metres from the camera is it? If no, across 0.5 and metres 1. Reason first.")
            a = vlm.chat([{"role": "user", "content": [image_part(p.read_bytes(), 1280), {"type": "text", "text": q}]}],
                         schema=sch, max_tokens=300)["json"] or {}
            if a.get("present") == "yes":
                b = math.radians(M.bearing_line(r, a["across"]))
                sights.append({"id": i, "t": r["t"], "time": r["time"], "x": r["x"], "y": r["y"], "b": b,
                               "d": a["metres_away"], "why": a["why"]})
        if not sights:
            return f"the vision model did not find {thing} in any of {ids}"
        sights.sort(key=lambda s: s["t"])
        days = {datetime.fromtimestamp(s["t"]).date() for s in sights}
        pos, how = None, ""
        if len(sights) >= 2:
            A, v = np.zeros((2, 2)), np.zeros(2)
            for s in sights:
                u = np.array([math.cos(s["b"]), math.sin(s["b"])])
                Pm = np.eye(2) - np.outer(u, u)
                A += Pm
                v += Pm @ np.array([s["x"], s["y"]])
            spread = max(abs(math.degrees(math.remainder(s["b"] - t["b"], 2 * math.pi))) for s in sights for t in sights)
            base = max(math.hypot(s["x"] - t["x"], s["y"] - t["y"]) for s in sights for t in sights)
            if spread >= 15 and base >= 0.5 and abs(np.linalg.det(A)) > 1e-3:
                pp = np.linalg.solve(A, v)
                if all((pp[0] - s["x"]) * math.cos(s["b"]) + (pp[1] - s["y"]) * math.sin(s["b"]) > 0.2 for s in sights):
                    pos = pp
                    how = f"crossing of {len(sights)} sight lines, {spread:.0f} deg apart, cameras up to {base:.1f} m apart"
        if pos is None:
            s = sights[-1]
            pos = np.array([s["x"] + s["d"] * math.cos(s["b"]), s["y"] + s["d"] * math.sin(s["b"])])
            how = f"one viewing direction ({s['id']}), distance guessed by the vision model ({s['d']} m): rough"
        near = M.nearest_place(float(pos[0]), float(pos[1]), self.P)
        lines = [f"{thing}: about ({pos[0]:.2f}, {pos[1]:.2f}) on the map, nearest place {near[0]} ({near[1]} m); {how}"]
        if len(days) > 1:
            lines.append(f"  WARNING: sightings span {len(days)} days; the thing may have moved, or these may be different things")
        lines += [f"  seen in [{s['id']}] {s['time']}: {s['why']}" for s in sights]
        lines.append("  stand to see it: route check not available in this replay")
        return "\n".join(lines)
