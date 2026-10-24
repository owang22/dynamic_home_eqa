"""Read-only views of what the console shows, for the lab agent (Oliver, 2026-10-23: "let the driver agent see the
lidar map and planner info if it requests it ... same for any other kind of sensor info I see on the console").

Tools (none of them move the dog or take control; they only GET /state.json, /map.png and /nav/plan):
    show_map(route_to | x, y, radius_m)  the saved lidar map drawn like the console (desk-top layer, furniture outlines,
                                         changes against the saved map, places and targets, the dog, its route, a
                                         previewed route, markers in view) with a 1 m grid
    plan_route(place | x, y)             the planner's route preview: length, waypoints, or why there is none
    sensors()                            IMU, odometry, body state, foot forces, joints, battery, line-up tracking,
                                         markers, nearest obstacles around the dog, data ages, control settings

The raw lidar cloud is used only for clearance (sensors, robot.clearance), not drawn: like the console's own map
panel, the map shows `live` (cells that changed against the saved map, already in the map frame).

Frames: the console's lidar cloud (`cloud.obs`, 10 cm cells with a height) is accumulated over the session in the
odom frame. It is moved into the map frame with the odom and map poses from the same snapshot; a rotation search
against the saved map agreed with that transform (2026-10-23). Odom drifts (about 20% short on distance, 7-14 deg per
full turn), so far-away or old cells no longer line up with the map: only cells within NEAR_M of the dog are drawn or
used. Cells at 0.1-0.15 m are floor noise and the dog's own legs; cells above BODY_H are overhangs (table tops) the
dog can walk under, so clearance ignores them and the map draws them in orange.
"""
from __future__ import annotations

import io
import json
import math

import memory as M

NEAR_M = 4.0
MIN_H, BODY_H = 0.15, 0.5
SECTORS = [("front", 0), ("front-left", 45), ("left", 90), ("back-left", 135), ("back", 180),
           ("back-right", -135), ("right", -90), ("front-right", -45)]


def snapshot(S):
    code, s = S.http("GET", "/state.json")
    if code != 200 or not isinstance(s, dict):
        raise S.Refused(f"console not answering ({code}): {s if isinstance(s, dict) else ''}")
    return s


def odom_to_map(s):
    """Function (x, y) in odom -> (x, y) in map, from the snapshot's odom and map poses; None if either is missing."""
    od, mp = s.get("odom") or {}, s.get("map_pose")
    if not mp or not od.get("pos") or od.get("yaw") is None:
        return None
    d = mp["yaw"] - od["yaw"]
    c, si = math.cos(d), math.sin(d)
    ox, oy = od["pos"][0], od["pos"][1]

    def f(x, y):
        dx, dy = x - ox, y - oy
        return mp["x"] + c * dx - si * dy, mp["y"] + si * dx + c * dy
    return f


def obstacles_map(s, near_m=NEAR_M, min_h=MIN_H):
    """Live lidar obstacle cells near the dog in map coordinates: [(x, y, height_m)]."""
    f, mp = odom_to_map(s), s.get("map_pose")
    cl = s.get("cloud") or {}
    if not f or not mp:
        return []
    out = []
    for p in cl.get("obs") or []:
        h = p[2] if len(p) > 2 else 1.0
        if h <= min_h:
            continue
        x, y = f(p[0], p[1])
        if math.hypot(x - mp["x"], y - mp["y"]) <= near_m:
            out.append((x, y, h))
    return out


def clearance(s, max_m=3.0, self_m=0.35):
    """Nearest live obstacle in each of 8 directions around the dog (relative to where it faces), in metres."""
    mp = s.get("map_pose")
    if not mp:
        return {}
    out = {name: None for name, _ in SECTORS}
    for x, y, h in obstacles_map(s, near_m=max_m):
        if h > BODY_H:
            continue
        d = math.hypot(x - mp["x"], y - mp["y"])
        if d < self_m or d > max_m:
            continue
        rel = math.degrees(math.atan2(y - mp["y"], x - mp["x"]) - mp["yaw"])
        rel = (rel + 180) % 360 - 180
        name = min(SECTORS, key=lambda sc: abs((rel - sc[1] + 180) % 360 - 180))[0]
        if out[name] is None or d < out[name]:
            out[name] = round(d, 2)
    return out


def plan(S, place="", x=None, y=None):
    q = f"place={place}" if place else f"x={float(x):.2f}&y={float(y):.2f}"
    code, p = S.http("GET", f"/nav/plan?{q}")
    return code, p if isinstance(p, dict) else {"error": str(p)[:300]}


def path_points(p):
    """[(x, y)] from a plan or nav dict, whatever the key ('path', 'route', 'waypoints')."""
    pts = (p or {}).get("path") or (p or {}).get("route") or (p or {}).get("waypoints") or []
    out = []
    for q in pts:
        if isinstance(q, dict) and "x" in q:
            out.append((q["x"], q["y"]))
        elif isinstance(q, (list, tuple)) and len(q) >= 2:
            out.append((q[0], q[1]))
    return out


def plan_text(p, label):
    if "error" in p or p.get("result") == "no_route":
        return f"route to {label}: NONE. {p.get('error') or p.get('reason') or ''} {p.get('why') or ''}".strip()
    pts = path_points(p)
    keep = pts if len(pts) <= 8 else [pts[int(i * (len(pts) - 1) / 7)] for i in range(8)]
    extra = {k: v for k, v in p.items() if k not in ("path", "route", "waypoints") and not isinstance(v, (list, dict))}
    return (f"route to {label}: {p.get('length_m', '?')} m, {len(pts)} points"
            + (f"; via {', '.join(f'({a:.2f}, {b:.2f})' for a, b in keep)}" if keep else "")
            + (f"; {json.dumps(extra, default=str)[:300]}" if extra else ""))


def marker_positions(s):
    """Markers in view now, placed on the map the way the console draws them: from the camera (0.33 m ahead of the
    pose point), the marker's range along the heading minus its bearing (positive = right of centre)."""
    mp, mk = s.get("map_pose"), s.get("markers") or {}
    out = []
    for m in mk.get("list") or []:
        if mp and m.get("z") is not None and m.get("bearing_deg") is not None:
            cx, cy = mp["x"] + 0.33 * math.cos(mp["yaw"]), mp["y"] + 0.33 * math.sin(mp["yaw"])
            a = mp["yaw"] - math.radians(m["bearing_deg"])
            d = math.hypot(m["z"], m.get("x") or 0)
            out.append({**m, "map_x": round(cx + d * math.cos(a), 2), "map_y": round(cy + d * math.sin(a), 2)})
        else:
            out.append(m)
    return out


def render(S, s, route=None, radius_m=0.0):
    """PNG bytes: the map with overlays, cropped to radius_m around the dog if given."""
    from PIL import Image, ImageDraw, ImageFont
    code, png = S.http("GET", "/map.png")
    m = s.get("map") or {}
    if code != 200 or not isinstance(png, bytes) or not m.get("resolution"):
        raise S.Refused("map image not available from the console")
    res, (ox, oy), H = m["resolution"], m["origin"], m["height"]
    k = 3                                                   # pixels per map cell in the output
    base = Image.open(io.BytesIO(png)).convert("RGB")
    im = base.resize((base.width * k, base.height * k), Image.NEAREST)
    g = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 13)
    except Exception:  # noqa: BLE001
        font = ImageFont.load_default()

    def px(x, y):
        return (x - ox) / res * k, (H - 1 - (y - oy) / res) * k
    # 1 m grid with labels
    for gx in range(math.ceil(ox), math.floor(ox + m["width"] * res) + 1):
        u, _ = px(gx, 0)
        g.line([(u, 0), (u, im.height)], fill=(200, 215, 235), width=1)
        g.text((u + 2, im.height - 16), f"x={gx}", fill=(90, 110, 150), font=font)
    for gy in range(math.ceil(oy), math.floor(oy + H * res) + 1):
        _, v = px(0, gy)
        g.line([(0, v), (im.width, v)], fill=(200, 215, 235), width=1)
        g.text((2, v - 15), f"y={gy}", fill=(90, 110, 150), font=font)
    code, lay = S.http("GET", "/map/layer.png?layer=mid")   # desk tops, tinted orange, as on the console
    if code == 200 and isinstance(lay, bytes):
        L = Image.open(io.BytesIO(lay)).convert("L").resize(im.size, Image.NEAREST)
        im.paste((235, 160, 70), mask=L.point(lambda v: 110 if v < 100 else 0))
        g = ImageDraw.Draw(im)
    lv = s.get("live") or {}                                 # changes against the saved map (map frame)
    for pts, col in ((lv.get("cleared") or [], (47, 168, 79)), (lv.get("new") or [], (224, 54, 44))):
        for x, y in pts:
            u, v = px(x, y)
            g.rectangle([u - 3, v - 3, u + 3, v + 3], fill=col)
    code, objs = S.http("GET", "/map/objects")               # furniture outlines with names
    for o in (objs.get("objects") or []) if isinstance(objs, dict) else []:
        c, sn, hw, hh = math.cos(o.get("yaw") or 0), math.sin(o.get("yaw") or 0), o["w"] / 2, o["h"] / 2
        corners = [px(o["x"] + a * c - b * sn, o["y"] + a * sn + b * c) for a, b in ((hw, hh), (-hw, hh), (-hw, -hh), (hw, -hh))]
        g.polygon(corners, outline=(70, 90, 210))
        u, v = px(o["x"], o["y"])
        g.text((u - 20, v - 6), (o.get("name") or o.get("label") or "").replace("_", " "), fill=(50, 60, 180), font=font)
    for pid, p in M.places().items():                        # places: stand spot, line to what it looks at, label
        u, v = px(p["x"], p["y"])
        t = p.get("target")
        if t:
            tu, tv = px(t["x"], t["y"])
            g.line([(u, v), (tu, tv)], fill=(170, 110, 200), width=1)
            g.ellipse([tu - 4, tv - 4, tu + 4, tv + 4], fill=(120, 30, 160))
        g.ellipse([u - 3, v - 3, u + 3, v + 3], outline=(120, 30, 160))
        g.text((u + 6, v - 8), pid, fill=(120, 30, 160), font=font)
    for pts, col in ((path_points(s.get("nav")), (21, 101, 192)), (route or [], (0, 170, 210))):   # route followed, previewed
        if len(pts) > 1:
            g.line([px(*q) for q in pts], fill=col, width=4)
    for mk in marker_positions(s):
        if "map_x" in mk:
            u, v = px(mk["map_x"], mk["map_y"])
            g.rectangle([u - 6, v - 6, u + 6, v + 6], outline=(0, 0, 0), width=2, fill=(255, 235, 59))
            g.text((u + 8, v - 8), f"marker {mk.get('mark')}", fill=(0, 0, 0), font=font)
    mp = s.get("map_pose")
    if mp:                                                  # the dog: arrow pointing where it faces
        u, v = px(mp["x"], mp["y"])
        a = -mp["yaw"]
        pts = [(16, 0), (-9, -9), (-4, 0), (-9, 9)]
        g.polygon([(u + x * math.cos(a) - y * math.sin(a), v + x * math.sin(a) + y * math.cos(a)) for x, y in pts],
                  fill=(230, 81, 0), outline=(0, 0, 0))
        if radius_m:
            r = radius_m / res * k
            im = im.crop((max(0, int(u - r)), max(0, int(v - r)), min(im.width, int(u + r)), min(im.height, int(v + r))))
    b = io.BytesIO()
    im.save(b, "PNG", optimize=True)
    return b.getvalue()


def sensors_text(s):
    imu, od, st, bat = s.get("imu") or {}, s.get("odom") or {}, s.get("state") or {}, s.get("battery") or {}
    m, loc, mk, ctl, age = s.get("map") or {}, s.get("loc") or {}, s.get("markers") or {}, s.get("control") or {}, s.get("age") or {}
    mp = s.get("map_pose")
    deg = (lambda v: [round(math.degrees(x), 1) for x in v]) if imu.get("rpy") else (lambda v: v)
    track = m.get("track") or {}
    ev = (loc.get("events") or [])[-4:]
    cl = clearance(s)
    jn = s.get("joints") or {}
    lines = [
        f"pose: map ({mp['x']:.2f}, {mp['y']:.2f}) facing {math.degrees(mp['yaw']):.0f} deg" if mp else "pose: unknown",
        f"map: {m.get('mode')} ({m.get('status')}); saved {m.get('saved_at')}; {m.get('mapped_m2')} m2 mapped; room_deg {m.get('room_deg')}",
        f"line-up tracking (latest scan match): {json.dumps(track, default=str)[:300]}",
        f"line-up state: seq {loc.get('seq')}, unsure {loc.get('unsure')}, fit {loc.get('fit')}, runner-up {loc.get('runner_up')}",
        "recent line-up events: " + ("; ".join(f"{e.get('kind')} at {e.get('t')}" for e in ev) or "none"),
        f"nearest live obstacle by direction (m, within 3 m, {MIN_H}-{BODY_H} m high; none = clear): "
        + ", ".join(f"{k} {v if v is not None else 'none'}" for k, v in cl.items()),
        f"lidar cloud: {(s.get('cloud') or {}).get('n_total')} points, {len((s.get('cloud') or {}).get('obs') or [])} obstacle cells "
        f"({(s.get('cloud') or {}).get('cell')} m), floor z {(s.get('cloud') or {}).get('floor_z')}",
        f"IMU: roll/pitch/yaw {deg(imu.get('rpy') or [])} deg, gyro {imu.get('gyro')} rad/s, accel {imu.get('acc')} m/s2, temp {imu.get('temp')} C",
        f"odometry: pos {od.get('pos')}, yaw {round(math.degrees(od['yaw']), 1) if od.get('yaw') is not None else None} deg, vel {od.get('vel')}",
        f"body: mode {st.get('mode')}, gait {st.get('gait')}, height {st.get('body_height')} m, foot raise {st.get('foot_raise')}, "
        f"velocity {st.get('velocity')}, the dog's own obstacle range front/back/left/right (m) {st.get('obstacle')}",
        f"foot forces (FL, FR, RL, RR): {st.get('foot_force')}",
        "joints (rad): " + ", ".join(f"{n.replace('_joint', '')} {p}" for n, p in zip(jn.get("name") or [], jn.get("pos") or [])),
        f"battery: {bat.get('soc')}%, {bat.get('voltage') and round(bat['voltage'], 2)} V, {bat.get('current_ma')} mA "
        f"(negative = discharging), BMS temp {bat.get('bms_temp_c')} C, {bat.get('cycles')} cycles",
        "markers in view: " + ("; ".join(
            f"{x.get('mark')} (id {x.get('id')}) {x.get('z')} m away, bearing {x.get('bearing_deg')} deg"
            + (f", on the map near ({x['map_x']}, {x['map_y']})" if 'map_x' in x else "") for x in marker_positions(s)) or "none"),
        f"route being followed: {len(path_points(s.get('nav')))} points" if s.get("nav") else "route being followed: none",
        f"control: avoidance {ctl.get('avoid')}, speed {ctl.get('speed')} {ctl.get('speeds', {}).get(ctl.get('speed'))}, "
        f"camera tilt {ctl.get('look_deg')} deg, person driving: {ctl.get('driver')}",
        f"agent owner: {(s.get('agents') or {}).get('owner')}; recording: {(s.get('rec') or {}).get('running')}",
        "data age (s): " + ", ".join(f"{k} {v}" for k, v in age.items()),
    ]
    return "\n".join(lines)


def register(mcp, S):
    """Add the read-only console views to server.py's MCP server. S = the server module."""

    @mcp.tool()
    @S.safe
    def show_map(route_to: str = "", x: float | None = None, y: float | None = None, radius_m: float = 0.0) -> list:
        """The lab's lidar map drawn like the control PC console: walls and furniture (dark), desk tops (orange
        tint), named furniture outlines (blue), changes against the saved map (red = new obstacle, green = cleared),
        places (purple), the dog (orange arrow), the route it is following (blue), markers in view (yellow) and a
        1 m grid labelled in map coordinates (drawn north-up, not turned to the room angle, so the grid reads
        directly). route_to (a place id) or x, y also previews the planner's route there (cyan) without moving. radius_m crops to that distance around the dog (0 = whole map). Read-only."""
        s = snapshot(S)
        route, note = None, ""
        if route_to or x is not None:
            _, p = plan(S, route_to, x, y)
            route = path_points(p)
            note = "\n" + plan_text(p, route_to or f"({x}, {y})")
        png = render(S, s, route, radius_m)
        from mcp.server.fastmcp import Image
        mp = s.get("map_pose")
        head = (f"map {(s.get('map') or {}).get('mode')}, dog at "
                + (f"({mp['x']:.2f}, {mp['y']:.2f}) facing {math.degrees(mp['yaw']):.0f} deg" if mp else "unknown")
                + ". Map frame: 0 deg = +x (right on the image), counter-clockwise positive; +y is up." + note)
        return [head, Image(data=png, format="png")]

    @mcp.tool()
    @S.safe
    def plan_route(place: str = "", x: float | None = None, y: float | None = None) -> str:
        """Ask the console's route planner for a route from where the dog is to a place id or map x, y, without
        moving: its length and waypoints, or why there is no route. Read-only."""
        if not place and x is None:
            raise S.Refused("give a place id or x and y")
        _, p = plan(S, place, x, y)
        return plan_text(p, place or f"({x}, {y})")

    @mcp.tool()
    @S.safe
    def sensors() -> str:
        """Everything the console's sensors report right now: pose, map and line-up tracking, the nearest live lidar
        obstacle in 8 directions around the dog, IMU, odometry, body state, foot forces, joint angles, battery,
        markers in view, the route being followed, control settings and how fresh each reading is. Read-only."""
        return sensors_text(snapshot(S))

    return show_map, plan_route, sensors
