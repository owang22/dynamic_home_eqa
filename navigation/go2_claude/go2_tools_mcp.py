#!/usr/bin/env python3
"""Robot tools for a Claude agent (Claude Code), over MCP on stdio.

go2_claude.sh starts a Claude Code session with only these tools. Each tool is a call to the
console's agent API (http://localhost:8080/agent/...), so the console's rules apply: a person at
the console always wins, one tool runs at a time, and the dog refuses to move if it has fallen or
its sensors are stale. Photos and the map come back as images the model can look at.
"""
import base64
import io
import json
import math
import os
import time
import urllib.error
import urllib.request

from mcp.server.fastmcp import FastMCP, Image
from PIL import Image as PILImage, ImageDraw, ImageFont

CONSOLE = os.environ.get("GO2_CONSOLE", "http://127.0.0.1:8080")
CLIENT = os.environ.get("GO2_AGENT_NAME", "claude-agent")
mcp = FastMCP("go2")


def call(tool, timeout=60, **args):
    """POST /agent/<tool>; returns the JSON reply (also for refusals and errors)."""
    req = urllib.request.Request(f"{CONSOLE}/agent/{tool}", data=json.dumps({"client": CLIENT, **args}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read())
        except ValueError:
            return {"result": "error", "reason": f"HTTP {e.code}"}
    except (urllib.error.URLError, OSError) as e:
        return {"result": "error", "reason": f"console not reachable: {e}"}


def get(path, timeout=10):
    with urllib.request.urlopen(CONSOLE + path, timeout=timeout) as r:
        return r.read()


def pose_text(out):
    mp = out.get("map_pose")
    if not mp:
        return "map pose: unknown (not lined up with the map)"
    return f"map pose: x={mp['x']:.2f} y={mp['y']:.2f} heading={math.degrees(mp['yaw']):.0f}°"


def brief(out, skip=("map_pose", "odom", "photo", "photos", "t")):
    return json.dumps({k: v for k, v in out.items() if k not in skip})


def photo_images(out):
    metas = out.get("photos") or ([out["photo"]] if out.get("photo") else [])
    items = []
    for m in metas:
        raw = base64.b64decode(m["jpeg_b64"]) if m.get("jpeg_b64") else get(m["url"])
        mp = m.get("map_pose") or {}
        head = f"photo {m['id']}" + (f" from x={mp['x']:.2f} y={mp['y']:.2f} facing {math.degrees(mp['yaw']):.0f}°"
                                     if mp else "") + (f", camera tilted {m['look_deg']}°" if m.get("look_deg") else "")
        items += [head, Image(data=shrink(raw, 1024), format="jpeg")]
    return items


def shrink(raw, width):
    img = PILImage.open(io.BytesIO(raw)).convert("RGB")
    if img.width > width:
        img = img.resize((width, round(img.height * width / img.width)))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=80)
    return buf.getvalue()


@mcp.tool()
def robot_status() -> str:
    """Who controls the dog, whether it is safe to move, its pose on the map, and what it is doing.
    Call this first. Map coordinates are metres; heading 0° = +x (east on the map), 90° = +y (north)."""
    s = call("status", timeout=10)
    owner = s.get("owner")
    return "\n".join([
        f"safe: {s.get('safe')}",
        f"in control: {owner['kind'] + ' ' + owner['client'] if owner else 'nobody (free)'}",
        f"running now: {s['current']['call'] if s.get('current') else 'nothing'}",
        pose_text(s),
    ])


@mcp.tool()
def list_places() -> str:
    """The named places on the map that people marked: id, description, where the thing is (target)
    and where the dog stands to see it (x, y, facing). go_to(place=id) drives to the standing spot
    and faces the thing."""
    places = json.loads(get("/places"))
    if not places:
        return "No places saved yet."
    rows = []
    for p in places.values():
        t = p.get("target")
        rows.append(f"- {p['id']}: {p.get('description') or '(no description)'}; "
                    + (f"thing at ({t['x']:.1f}, {t['y']:.1f}); " if t else "")
                    + f"stand at ({p['x']:.1f}, {p['y']:.1f}) facing {p['yaw_deg']:.0f}°")
    return "\n".join(rows)


@mcp.tool()
def view_map() -> list:
    """The lab map as an image: white = open floor, black = walls and furniture (0.2-0.6 m tall),
    grey = not mapped. Grid lines every metre, labelled with map coordinates. Blue dots = places,
    red arrow = the dog. Use it to plan where to go and to pick x/y for go_to."""
    st = json.loads(get("/state.json"))
    m, pose = st.get("map"), st.get("map_pose")
    if not m:
        return ["No map."]
    places = json.loads(get("/places"))
    img = PILImage.open(io.BytesIO(get("/map.png"))).convert("RGB")
    S = 4
    img = img.resize((img.width * S, img.height * S), PILImage.NEAREST)
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    res, (ox, oy), H = m["resolution"], m["origin"], m["height"]

    def px(x, y):
        return (x - ox) / res * S, (H - (y - oy) / res) * S

    for gx in range(math.ceil(ox), math.floor(ox + m["width"] * res) + 1):
        x0, _ = px(gx, 0)
        d.line([(x0, 0), (x0, img.height)], fill=(170, 190, 230) if gx else (90, 120, 220), width=1)
        d.text((x0 + 2, 2), str(gx), fill=(40, 60, 160), font=font)
    for gy in range(math.ceil(oy), math.floor(oy + H * res) + 1):
        _, y0 = px(0, gy)
        d.line([(0, y0), (img.width, y0)], fill=(170, 190, 230) if gy else (90, 120, 220), width=1)
        d.text((2, y0 + 1), str(gy), fill=(40, 60, 160), font=font)
    for p in places.values():
        t = p.get("target") or {"x": p["x"], "y": p["y"]}
        tx, ty = px(t["x"], t["y"])
        d.ellipse([tx - 5, ty - 5, tx + 5, ty + 5], fill=(30, 120, 220))
        d.text((tx + 7, ty - 6), p["id"], fill=(10, 60, 160), font=font)
    if pose:
        x, y = px(pose["x"], pose["y"])
        a = pose["yaw"]
        pts = [(x + 22 * math.cos(a), y - 22 * math.sin(a)),
               (x + 12 * math.cos(a + 2.4), y - 12 * math.sin(a + 2.4)),
               (x + 12 * math.cos(a - 2.4), y - 12 * math.sin(a - 2.4))]
        d.polygon(pts, fill=(220, 30, 30), outline=(120, 0, 0))
        d.text((x + 14, y + 8), "dog", fill=(160, 0, 0), font=font)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return [f"Map {m['width'] * res:.0f} x {H * res:.0f} m. " + pose_text({"map_pose": pose}),
            Image(data=buf.getvalue(), format="png")]


@mcp.tool()
def take_photo(note: str = "") -> list:
    """Stop, wait until the dog is still, and take a photo with the front camera (head height ~0.3 m,
    about 80° wide). Returns the image and where it was taken."""
    out = call("photo", timeout=30, inline=True, note=note)
    if out.get("result") != "done":
        return [brief(out)]
    return photo_images(out) + [pose_text(out)]


@mcp.tool()
def look_around(n: int = 4, note: str = "") -> list:
    """Take n photos (1-12) while turning a full circle in place, n equal steps. Good for getting
    oriented or searching a spot. Returns all the photos."""
    out = call("look_around", timeout=150, n=n, inline=True, note=note, timeout_s=120)
    return photo_images(out) + [brief(out), pose_text(out)]


@mcp.tool()
def go_to(place: str = "", x: float | None = None, y: float | None = None, yaw_deg: float | None = None,
          note: str = "") -> str:
    """Drive to a saved place (place=id) or a map point (x, y in metres, optional yaw_deg to face
    after). Plans a route around furniture on the map, re-plans around new obstacles, and stops if
    blocked. Takes up to ~2 minutes. Result: done, blocked, no_route, aborted (a person took over),
    or error, with the final pose."""
    args = {"timeout_s": 120, "note": note}
    if place:
        args["place"] = place
    elif x is not None and y is not None:
        args.update(x=x, y=y)
        if yaw_deg is not None:
            args["yaw_deg"] = yaw_deg
    else:
        return "give place, or x and y"
    out = call("go_to", timeout=140, **args)
    return brief(out) + "\n" + pose_text(out)


@mcp.tool()
def move(metres: float, note: str = "") -> str:
    """Walk straight forward (+) or back (-), at most 3 m. Stops early if something is in the way."""
    out = call("move", timeout=40, m=metres, note=note)
    return brief(out) + "\n" + pose_text(out)


@mcp.tool()
def turn(degrees: float, note: str = "") -> str:
    """Turn in place: + = left (counter-clockwise), - = right."""
    out = call("turn", timeout=40, deg=degrees, note=note)
    return brief(out) + "\n" + pose_text(out)


@mcp.tool()
def tilt_camera(degrees: float) -> str:
    """Tilt the whole body to point the camera up (+, up to ~15° in practice) or down (-, only a few
    degrees). 0 = level. Walking levels it again. Then take_photo."""
    out = call("look", timeout=20, deg=degrees)
    return brief(out)


@mcp.tool()
def save_place(id: str, description: str, x: float | None = None, y: float | None = None) -> str:
    """Name a place so people and other agents can find it later (id: a-z, 0-9, _). Without x/y: the
    dog's current spot, with the thing taken to be the first obstacle straight ahead. With x/y: the
    thing is at that map point and a standing spot next to it is chosen."""
    body = {"id": id, "description": description, "client": CLIENT}
    if x is not None and y is not None:
        body["target"] = {"x": x, "y": y}
    req = urllib.request.Request(f"{CONSOLE}/places", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode()
    except urllib.error.HTTPError as e:
        return e.read().decode()


@mcp.tool()
def note(text: str) -> str:
    """Tell the people watching what you are doing or what you found (shown on the console)."""
    return brief(call("say", timeout=10, text=text))


@mcp.tool()
def stop() -> str:
    """Stop the dog now."""
    return brief(call("stop", timeout=10))


@mcp.tool()
def release_control() -> str:
    """Give up control of the dog when you are finished."""
    return brief(call("release", timeout=10))


if __name__ == "__main__":
    mcp.run()
