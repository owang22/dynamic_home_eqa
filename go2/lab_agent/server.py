"""The lab agent's tools (an MCP server over stdio): drive the Go2 through the control PC's agent API, take and
remember pictures, search what the dog has seen, and work out where a thing is on the map.

Started by chat.sh / web.py through `claude --mcp-config mcp.json`; nothing to run by hand. Test without the
dog: python3 go2/lab_agent/server.py --selftest (--selftest-memory: memory tools only, no console calls
except the read-only /state.json and /map.png)

Moving the dog: no one needs to be next to the dog (Oliver's call, 2026-10-22, replacing his earlier rule). The
console keeps obstacle avoidance on and caps the speed; nothing here changes either. A person at the console always wins: a 409 or "aborted" is reported and
not retried. Client name on the console: cheetah-lab-agent.
"""
from __future__ import annotations

import io
import json
import math
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import memory as M  # noqa: E402

from mcp.server.fastmcp import FastMCP, Image  # noqa: E402

CLIENT = "cheetah-lab-agent"
mcp = FastMCP("lab")
LOG = M.DATA / "calls.jsonl"
STOP_FLAG = M.DATA / "stop_flag"       # written by the phone page's STOP; cleared when Oliver sends a new message
MOVES = {"go_to", "turn", "move", "look"}
NOTICES = []        # localization_notice summaries from the console (board #28), shown with the next tool reply


def http(method, path, body=None, timeout=200):
    data = json.dumps(dict(body or {}, client=CLIENT)).encode() if method == "POST" else None
    req = urllib.request.Request(M.CONSOLE + path, data, {"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            out = json.loads(raw) if raw[:1] in (b"{", b"[") else raw
            if isinstance(out, dict) and out.get("localization_notice"):
                n = out["localization_notice"]
                NOTICES.append(n.get("summary") or n.get("status") or json.dumps(n, default=str)[:300])
            return r.status, out
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:  # noqa: BLE001
            return e.code, {"raw": raw[:300].decode(errors="replace")}
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return 0, {"error": f"console not reachable: {e}"}


def logcall(name, args, out):
    M.DATA.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps({"t": round(time.time(), 2), "call": name, "args": args, "out": out}, default=str) + "\n")


class Refused(Exception):
    pass


def agent(name, **args):
    if name in MOVES and STOP_FLAG.exists():    # checked before every move, so a loop (look_around) halts mid-way
        raise Refused("STOP was pressed: no more moves until Oliver sends a new message")
    code, out = http("POST", f"/agent/{name}", args)
    logcall(name, args, {"http": code, "out": out})
    if code == 0:
        raise Refused(out["error"])
    if code == 409 or (isinstance(out, dict) and out.get("result") in ("refused", "aborted")):
        raise Refused(f"the console refused {name} (a person has control or pressed STOP): {out}. Not retrying.")
    return out


def ready():
    """Problems that stop a move, or []."""
    c1, st = http("GET", f"/agent/status?client={CLIENT}")
    if c1 == 0:
        return ["the console (control PC, port 8080) is not answering: is it running?"]
    _, s = http("GET", "/state.json")
    problems = []
    owner = (st or {}).get("owner")
    if owner and owner.get("client") != CLIENT:
        problems.append(f"someone else has control: {owner}")
    if (st or {}).get("safe") not in (None, "ok"):
        problems.append(f"console safety state: {st.get('safe')}")
    m = (s or {}).get("map") or {}
    if m.get("mode") != "localized":
        problems.append(f"not lined up with the map ({m.get('mode')}: {m.get('status')}); drive it a little from the console")
    return problems


def begin_move():
    if STOP_FLAG.exists():
        raise Refused("STOP was pressed: no more moves until Oliver sends a new message")
    p = ready()
    if p:
        raise Refused("not moving: " + "; ".join(p))
    agent("claim")


def snap(look_deg=0.0, source="photo"):
    """Take a photo, index it, return (record, jpg)."""
    if look_deg:
        agent("look", deg=look_deg)
    out = agent("photo")
    ph = out.get("photo") or out
    code, jpg = http("GET", ph["url"])
    if look_deg:
        agent("look", deg=0)
    if code != 200 or not isinstance(jpg, bytes):
        raise Refused(f"photo fetch failed ({code})")
    mp = ph.get("map_pose") or out.get("map_pose") or {}
    _, st = http("GET", "/state.json")
    loc = (st or {}).get("loc") if isinstance(st, dict) else None
    loc = {k: loc.get(k) for k in ("seq", "fit", "runner_up", "unsure", "status")} if isinstance(loc, dict) else None
    rec = M.add_picture(jpg, ph.get("t", time.time()), mp.get("x"), mp.get("y"),
                        None if mp.get("yaw") is None else round(math.degrees(mp["yaw"]), 1), source,
                        look_deg=ph.get("look_deg", look_deg), pid=ph.get("id"), background=True,
                        extra={"loc": loc, "loc_notices": list(NOTICES)} if loc or NOTICES else None)
    return rec, jpg


def small(jpg, width=960):
    from PIL import Image as PI
    im = PI.open(io.BytesIO(jpg))
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)))
    b = io.BytesIO()
    im.convert("RGB").save(b, "JPEG", quality=85)
    return Image(data=b.getvalue(), format="jpeg")


def describe_rec(r):
    M.with_places([r])
    s = r.get("seen") or {}
    if r.get("seen") is None and not r.get("describe_error"):
        s = {"summary": "(description being written; look at the picture)"}
    pose = ("pose unknown" if r.get("x") is None or r.get("yaw_deg") is None
            else f"map ({r['x']:.2f}, {r['y']:.2f}) facing {r['yaw_deg']:.0f} deg")
    objs = ", ".join(f"{o['colour']} {o['name']} ({o['on']}, across {o['across']:.2f})" for o in s.get("objects", []))
    return (f"[{r['id']}] {r['time']} near {r.get('near_place')} ({r.get('near_place_m')} m), {pose}, look {r.get('look_deg', 0)} deg\n"
            f"  seen: {s.get('summary')}\n  people: {s.get('people')} {s.get('people_notes') or ''}\n"
            f"  objects: {objs}\n  states: {'; '.join(s.get('states', [])) or 'none'}")


def when(s):
    """'14:00', '2026-10-22 14:00', 'today', or None -> epoch seconds."""
    if not s:
        return None
    s = s.strip()
    if s == "today":
        return datetime.now().replace(hour=0, minute=0, second=0).timestamp()
    if s == "yesterday":
        return datetime.now().replace(hour=0, minute=0, second=0).timestamp() - 86400
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).timestamp()
        except ValueError:
            pass
    if ":" not in s:          # (2026-10-23: checked after the formats; before, 'YYYY-MM-DD' was always refused)
        raise Refused(f"time '{s}' not understood: use 'HH:MM', 'YYYY-MM-DD HH:MM', 'YYYY-MM-DD', 'today' or 'yesterday'")
    h, m = map(int, s.split(":"))
    return datetime.now().replace(hour=h, minute=m, second=0).timestamp()


def with_notices(out):
    """Put any line-up events the console reported (hand placement, jump, re-alignment) in front of a tool reply."""
    if not NOTICES:
        return out
    note = ("LOCALIZATION NOTICE: " + "; ".join(dict.fromkeys(NOTICES)) +
            ". The map pose changed outside your moves, so positions before and after this may not agree.")
    NOTICES.clear()
    if isinstance(out, list):
        return [note] + out
    return note + "\n" + str(out)


def safe(fn=None, moves=False):
    """Turn refusals and errors into a plain reply the agent can relay. A tool that moves the dog also sends stop
    on an unexpected error; a read-only tool never does (it could stop someone driving from the console)."""
    import functools

    def wrap(fn):
        @functools.wraps(fn)
        def run(*a, **k):
            try:
                out = fn(*a, **k)
            except Refused as e:
                out = f"REFUSED: {e}"
            except Exception as e:  # noqa: BLE001
                if moves:
                    http("POST", "/agent/stop", {}, timeout=5)
                    out = f"ERROR (sent stop): {type(e).__name__}: {e}"
                else:
                    out = f"ERROR: {type(e).__name__}: {e}"
            return with_notices(out)
        return run
    return wrap(fn) if fn else wrap


# ---- tools ----

@mcp.tool()
@safe
def status() -> str:
    """Is the console up, is the dog lined up with the map, where is it, who has control, and how big the memory is."""
    recs = M.load()
    mem = f"memory: {len(recs)} pictures, newest {max(recs, key=lambda r: r['t'])['time'] if recs else 'none'}"
    c, st = http("GET", f"/agent/status?client={CLIENT}")
    if c == 0:
        return f"console NOT reachable (dog or console off). {mem}. Memory search still works."
    _, s = http("GET", "/state.json")
    m = s.get("map") or {}
    mp = s.get("map_pose")
    pose = "unknown" if not mp else f"({mp['x']:.2f}, {mp['y']:.2f}) facing {math.degrees(mp['yaw']):.0f} deg"
    near = M.nearest_place(mp["x"], mp["y"]) if mp else (None, None)
    return (f"console up. map: {m.get('mode')} ({m.get('status')}). dog at {pose}, nearest place {near[0]} ({near[1]} m). "
            f"control owner: {st.get('owner')}. obstacle avoidance: {(s.get('control') or {}).get('avoid')}. "
            f"battery: {((s.get('battery') or {}).get('soc') if isinstance(s.get('battery'), dict) else s.get('battery'))}%. {mem}. "
            f"time now {datetime.now():%a %Y-%m-%d %H:%M}")


@mcp.tool()
@safe
def list_places() -> str:
    """The lab's saved places (ids to use with go_to), each with its standing spot and what it looks at."""
    P = M.places()
    if not P:
        return "no places known (console off and no saved copy)"
    return "\n".join(f"{pid}: stand ({p['x']:.2f}, {p['y']:.2f})"
                     + (f", looks at ({p['target']['x']:.2f}, {p['target']['y']:.2f})" if p.get("target") else "")
                     + (f" - {p['note']}" if p.get("note") else "") for pid, p in P.items())


@mcp.tool()
@safe(moves=True)
def go_to(place: str = "", x: float | None = None, y: float | None = None,
          yaw_deg: float | None = None) -> list:
    """Walk to a saved place (by id from list_places) or to map coordinates x, y (metres) facing yaw_deg
    (0 = +x, counter-clockwise). Then takes a photo there, remembers it and returns it."""
    begin_move()
    args = {"place": place} if place else {"x": x, "y": y, **({"yaw_deg": yaw_deg} if yaw_deg is not None else {})}
    for _ in range(3):                 # "no_route" came and went with live lidar points (board #16)
        r = agent("go_to", timeout_s=120, **args)
        if r.get("result") != "no_route":
            break
        time.sleep(2)
    head = (f"go_to {args}: {r.get('result')} {r.get('reason') or ''}; moved {r.get('moved_m')} m, "
            f"ended at {r.get('map_pose')}")
    if place and r.get("result") == "done":
        tgt = (M.places().get(place) or {}).get("target")
        mp = r.get("map_pose")
        if tgt and mp:             # face the thing from wherever it stopped (it can stop short near furniture)
            d = (math.degrees(math.atan2(tgt["y"] - mp["y"], tgt["x"] - mp["x"]) - mp["yaw"]) + 180) % 360 - 180
            if abs(d) > 12:
                agent("turn", deg=round(d, 1))
                head += f"; turned {d:.0f} deg to face the place's target"
    rec, jpg = snap(source="photo")
    return [head + "\n" + describe_rec(rec), small(jpg)]


@mcp.tool()
@safe(moves=True)
def turn(deg: float) -> list:
    """Turn in place (positive = left), then take, remember and return a photo."""
    begin_move()
    r = agent("turn", deg=deg)
    rec, jpg = snap()
    return [f"turn {deg}: {r.get('result')} {r.get('reason') or ''}, turned {r.get('turned_deg')} deg\n" + describe_rec(rec), small(jpg)]


@mcp.tool()
@safe(moves=True)
def move(metres: float) -> list:
    """Walk straight forward (negative = back), at most 1.5 m, obstacle avoidance on. Then photo."""
    begin_move()
    m = max(-1.0, min(1.5, metres))
    r = agent("move", m=m)
    rec, jpg = snap()
    return [f"move {m} (asked {metres}): {r.get('result')} {r.get('reason') or ''}, moved {r.get('moved_m')} m\n" + describe_rec(rec), small(jpg)]


@mcp.tool()
@safe(moves=True)
def look_around(views: int = 4) -> list:
    """Turn in place through a full circle, taking `views` photos (2-8); all are remembered and returned."""
    begin_move()
    views = max(2, min(8, views))
    out = []
    for i in range(views):
        if i:
            agent("turn", deg=360 / views)
        rec, jpg = snap(source="look_around")
        out += [describe_rec(rec), small(jpg, 640)]
    return out


@mcp.tool()
@safe
def photo(look_deg: float = 0.0) -> list:
    """Take a photo from where the dog stands (look_deg tilts the camera: up to about +16 = up, -5 = down).
    Does not walk. The photo is remembered and returned."""
    if STOP_FLAG.exists() and look_deg:
        raise Refused("STOP was pressed: no camera tilt until Oliver sends a new message")
    agent("claim")
    rec, jpg = snap(look_deg=look_deg)
    return [describe_rec(rec), small(jpg)]


@mcp.tool()
@safe
def stop() -> str:
    """Stop the dog now (always allowed)."""
    return json.dumps(agent("stop"))


@mcp.tool()
@safe
def release() -> str:
    """Give control back (do this when Oliver's request is done)."""
    return json.dumps(agent("release"))


@mcp.tool()
@safe
def search_memory(query: str, since: str = "", until: str = "", place: str = "", limit: int = 12,
                  mode: str = "fused") -> str:
    """Search everything the dog has seen. query: words such as 'grey backpack' or 'person'. since/until:
    'HH:MM' (today), 'YYYY-MM-DD HH:MM', or 'today'. place: a place id (pictures taken nearest to it).
    mode: "fused" (default: picture similarity plus the descriptions' words, so it also finds things the
    descriptions missed), "words" (the descriptions' words only, as before), "images" (picture similarity only).
    Returns matching pictures (best match first) with time, place, pose and the matched object. Results are ranked
    by similarity, not proof: look at the pictures (show_pictures) before answering. For where a thing is now, use
    where_is."""
    if mode not in ("fused", "words", "images"):
        raise Refused(f"mode '{mode}' not understood: use fused, words or images")
    hits = M.search(query, since=when(since), until=when(until), place=place or None, k=max(1, min(30, limit)),
                    mode=mode)
    recs = M.load()
    span = f"{min(recs, key=lambda r: r['t'])['time']} to {max(recs, key=lambda r: r['t'])['time']}" if recs else "empty"
    if not hits:
        return f"no pictures match '{query}' (memory: {len(recs)} pictures, {span})"
    lines = [f"{len(hits)} matches, mode {mode} (memory: {len(recs)} pictures, {span}):"]
    for b in hits:
        mt = b.get("match")
        sim = f"picture similarity {b['image_score']:.2f}; " if b.get("image_score") is not None else ""
        lines.append(f"[{b['id']}] {b['time']} near {b['near_place']}, pose {b['pose']}; {sim}"
                     + (f"match: {mt['colour']} {mt['name']} on {mt['on']} at across {mt['across']:.2f}; " if mt
                        else ("description does not name it; " if mode != "words" else ""))
                     + f"people {b['people']}; {b['summary']}")
    return "\n".join(lines)


@mcp.tool()
@safe
def show_pictures(ids: list[str]) -> list:
    """Look at remembered pictures (up to 6 ids from search_memory or people_seen), with their full descriptions."""
    by = {r["id"]: r for r in M.load()}
    out = []
    for i in ids[:6]:
        r = by.get(i)
        if not r:
            out.append(f"[{i}] not in memory")
            continue
        out += [describe_rec(r), small(Path(r["path"]).read_bytes())]
    return out


@mcp.tool()
@safe
def people_seen(since: str = "today", until: str = "") -> str:
    """How many people the pictures show, over time: one line per picture with anyone in it, plus a count of
    pictures taken per hour (so 'no people' can be told apart from 'no pictures')."""
    t0, t1 = when(since), when(until)
    recs = M.with_places([r for r in M.load() if r.get("seen") and (not t0 or r["t"] >= t0) and (not t1 or r["t"] <= t1)])
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


@mcp.tool()
@safe
def locate(thing: str, ids: list[str]) -> str:
    """Where a thing is on the map, from pictures that show it (ids you have looked at and confirmed). The local
    vision model finds it in each picture; each sighting is a line from the camera pose; two or more lines from
    different directions give a position. Also suggests where to stand to see it (for go_to)."""
    by = {r["id"]: r for r in M.load()}
    # (2026-10-23) no maxLength on why: cutting it mid-sentence made the 8B pad with whitespace to max_tokens
    sch = {"type": "object", "additionalProperties": False, "properties": {"why": {"type": "string"},
                                            "present": {"type": "string", "enum": ["yes", "no"]},
                                            "across": {"type": "number", "minimum": 0, "maximum": 1},
                                            "metres_away": {"type": "number", "minimum": 0.2, "maximum": 8}},
           "required": ["why", "present", "across", "metres_away"]}
    sights, unread = [], []
    for i in ids[:12]:
        r = by.get(i)
        if not r or r.get("x") is None:
            continue
        a = None
        for _ in range(2):                 # one bad answer skips that picture, not the whole call
            try:
                a = M.ask_vlm(f"A robot dog's camera picture (camera 0.4 m above the floor, about 73 degrees wide). Is "
                              f"{thing} in it? If yes: where is its centre across the picture (0 = left edge, 1 = right "
                              f"edge), and about how many metres from the camera is it? If no, across 0.5 and metres 1. "
                              f"First give your reason in one short sentence.",
                              [Path(r["path"]).read_bytes()], sch, 400, fallback=True)
                break
            except Exception as e:  # noqa: BLE001
                err = f"{i}: {type(e).__name__}: {e}"
        if a is None:
            unread.append(err)
            continue
        if a["present"] == "yes" and r.get("yaw_deg") is not None:
            b = math.radians(M.bearing_line(r, a["across"]))
            sights.append({"id": i, "t": r["t"], "time": r["time"], "x": r["x"], "y": r["y"], "b": b,
                           "d": a["metres_away"], "why": a["why"]})
    if not sights:
        return (f"the vision model did not find {thing} in any of {ids}"
                + (f" ({len(unread)} could not be read: {'; '.join(unread)[:300]})" if unread else ""))
    sights.sort(key=lambda s: s["t"])
    days = {datetime.fromtimestamp(s["t"]).date() for s in sights}
    import numpy as np
    pos, how = None, ""
    if len(sights) >= 2:
        A, v = np.zeros((2, 2)), np.zeros(2)
        for s in sights:
            u = np.array([math.cos(s["b"]), math.sin(s["b"])])
            P = np.eye(2) - np.outer(u, u)
            A += P
            v += P @ np.array([s["x"], s["y"]])
        spread = max(abs(math.degrees(math.remainder(s["b"] - t["b"], 2 * math.pi))) for s in sights for t in sights)
        base = max(math.hypot(s["x"] - t["x"], s["y"] - t["y"]) for s in sights for t in sights)
        if spread >= 15 and base >= 0.5 and abs(np.linalg.det(A)) > 1e-3:
            p = np.linalg.solve(A, v)
            ahead = all((p[0] - s["x"]) * math.cos(s["b"]) + (p[1] - s["y"]) * math.sin(s["b"]) > 0.2 for s in sights)
            if ahead:          # in front of every camera, not behind one (lines cross both ways)
                pos = p
                how = f"crossing of {len(sights)} sight lines, {spread:.0f} deg apart, cameras up to {base:.1f} m apart"
    if pos is None:                           # one direction only: along the line at the estimated distance
        s = sights[-1]
        pos = np.array([s["x"] + s["d"] * math.cos(s["b"]), s["y"] + s["d"] * math.sin(s["b"])])
        how = f"one viewing direction ({s['id']}), distance guessed by the vision model ({s['d']} m): rough"
    near = M.nearest_place(float(pos[0]), float(pos[1]))
    # where to stand: 0.9 m back from it toward the camera that saw it, facing it; checked with the route preview
    s = sights[-1]
    back = math.atan2(s["y"] - pos[1], s["x"] - pos[0])
    stand = None
    for dist in (0.9, 1.2, 0.7, 1.5):
        sx, sy = pos[0] + dist * math.cos(back), pos[1] + dist * math.sin(back)
        code, plan = http("GET", f"/nav/plan?x={sx:.2f}&y={sy:.2f}")
        if isinstance(plan, dict) and "error" not in plan:
            stand = {"x": round(sx, 2), "y": round(sy, 2), "yaw_deg": round(math.degrees(back + math.pi), 1),
                     "route_m": plan.get("length_m")}
            break
    lines = [f"{thing}: about ({pos[0]:.2f}, {pos[1]:.2f}) on the map, nearest place {near[0]} ({near[1]} m); {how}"]
    if len(days) > 1:
        lines.append(f"  WARNING: sightings span {len(days)} days; the thing may have moved, or these may be different things")
    lines += [f"  seen in [{s['id']}] {s['time']}: {s['why']}" for s in sights]
    if unread:
        lines.append(f"  {len(unread)} picture(s) could not be read by the vision model: {'; '.join(unread)[:300]}")
    lines.append(f"  stand to see it: {stand}" if stand else
                 "  stand to see it: no route found (console off, or no reachable spot 0.7-1.5 m from it)")
    return "\n".join(lines)


@mcp.tool()
@safe
def where_is(thing: str, limit: int = 4) -> str:
    """Where a thing probably is now, from memory only (does not move the dog). Uses the object instances built
    from all pictures: each is one physical thing seen in one or more pictures, with a map position, when it was
    first and last seen, newer pictures that looked at that spot and did not show it, and P(still there).
    Ends with a suggestion: answer, answer with a caveat, or go and look (with the walk length). Open the listed
    pictures (show_pictures) before you answer. Furniture and clutter (chairs, desks, boxes, cables) are not
    tracked: use search_memory for those."""
    import memory_instances as MI
    insts = MI.fresh_instances()
    same, other = MI.match(thing, insts)
    if not same and not other:
        hits = M.search(thing, k=5)
        return (f"no tracked object matches '{thing}' ({len(insts)} tracked objects; furniture and clutter are not "
                f"tracked). Best pictures from search_memory: " + ", ".join(f"[{b['id']}] {b['time']}" for b in hits)
                + ". Open them before answering.")
    now = time.time()
    by = {r["id"]: r for r in M.load()}
    lines = [f"'{thing}': {len(same)} matching object(s) remembered"
             + (f", plus {len(other)} of the same kind in another colour" if other else "")
             + f" (time now {datetime.now():%a %H:%M}; P(still there) model: memory_instances.py)."]
    for n, i in enumerate((same + other)[:max(1, min(8, limit))]):
        ago_h = (now - i["last_seen"]) / 3600
        miss = i["missed_after_last_seen"]
        tag = "" if i in same else " [other colour]"
        lines.append(f"{n + 1}. {i['colour']} {i['name']}{tag} on {i['on']}, at map ({i['x']}, {i['y']}) "
                     f"+-{i['uncertainty_m']} m ({i['how']}), near {i['near_place']} ({i['near_place_m']} m).")
        lines.append(f"   seen in {i['n_pictures']} pictures, {i['first_time']} to {i['last_time']} "
                     f"({ago_h:.0f} h ago); pictures: {', '.join(i['pictures'][-3:])}"
                     + (f"; probably the same one seen there on {', '.join(i['chain_days'])}"
                        if len(i.get('chain_days', [])) > 1 else "")
                     + (f"; poses: {i['pose_quality']} (older map poses: position less sure)"
                        if not i['pose_quality'].startswith(str(i['n_sightings'])) else ""))
        if miss:
            lines.append(f"   NOT seen in {len(miss)} newer picture(s) that looked at that spot: "
                         + ", ".join(f"[{m}] {by[m]['time'][4:] if m in by else ''}" for m in miss[-4:])
                         + (" (the descriptions rarely name this kind, so this means little: open them)"
                            if MI.DESCRIBE_RECALL.get(i["name"], 1) < 0.5 else ""))
        lines.append(f"   P(still there) = {i['p_still']:.2f}")
    best = (same or other)[0]
    p = best["p_still"]
    if p >= 0.7:
        say = "answer: probably still there"
    elif p >= 0.3:
        say = "answer with a caveat (it may have moved), or offer to go and look"
    else:
        say = "go and look (memory is stale or newer pictures missed it), after telling Oliver what the memory says"
    if best["n_pictures"] == 1:
        say += "; it was seen in one picture only: check that picture first"
    if best["uncertainty_m"] > 1.5:
        say += f"; the position is rough (+-{best['uncertainty_m']} m), say so"
    rt = MI.route(best["x"], best["y"])
    if rt:
        walk = (f"walk about {rt['route_m']} m to stand at ({rt['stand']['x']}, {rt['stand']['y']}) facing "
                f"{rt['stand']['yaw_deg']} deg" if rt.get("route_m") else "no standing spot found on the saved map")
        lines.append(f"Suggestion for #1: {say}. To look: {walk} (dog now at ({rt['dog_at']['x']}, {rt['dog_at']['y']}), "
                     f"{rt['straight_m']} m in a straight line).")
    else:
        lines.append(f"Suggestion for #1: {say}. (Console off: no walk length.)")
    lines.append("Questions about the past (\"did you see it Monday?\") need no look: answer from the pictures.")
    return "\n".join(lines)


def selftest(memory_only=False):
    """--selftest-memory skips status (it asks the console's /agent/status) and list_places."""
    if not memory_only:
        print(status())
        print(list_places()[:300])
    print(search_memory("black office chair", limit=3))
    print(search_memory("black office chair", limit=3, mode="words"))
    print(people_seen(since="2026-10-19")[:1500])
    print(where_is("grey backpack"))


# Skill tools from the small/large hierarchy (hierarchy/REPORT.md, added 2026-10-23): watch_go_to and scan_for
# let the local Qwen3-VL-8B (:8301) watch the camera and stop the dog on sight. They refuse to move if it is down.
sys.path.insert(0, str(Path(__file__).parent / "hierarchy"))
import integration  # noqa: E402

integration.register(mcp, sys.modules[__name__])

# Skills the agent writes for itself (skills.py, Oliver 2026-10-23): write_skill, test_skill, run_skill, note_skill,
# list_skills, read_skill.
import skills  # noqa: E402

skills.register(mcp, sys.modules[__name__])

# Read-only views of the console's map, route planner and sensors (console_view.py, Oliver 2026-10-23).
import console_view  # noqa: E402

console_view.register(mcp, sys.modules[__name__])

if __name__ == "__main__":
    if "--selftest" in sys.argv or "--selftest-memory" in sys.argv:
        selftest(memory_only="--selftest-memory" in sys.argv)
    else:
        mcp.run()
