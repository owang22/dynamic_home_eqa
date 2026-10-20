"""One patrol round through the lab console's agent API (control PC, http://172.17.40.64:8080): visit places,
photograph each, come back to the home place (desk_oliver), release. For the evidence-memory trial.

    python3 go2/console/lab_round.py --plan-only                     # preview every route; nothing moves
    python3 go2/console/lab_round.py --views --places water_cooler,sofa   # viewpoint mode (use this one)
    python3 go2/console/lab_round.py --places water_cooler:16,desk_oliver # place mode; name:deg tilts the camera

Viewpoint mode (--views): the goal is a photo that shows the thing, not a fixed standing spot. view_plan.py ranks
camera positions around the thing (its position from view_targets.json or the console's place target; its size
sets the distance); each is checked with the console's route preview, driven to with go_to {x, y, yaw_deg},
photographed, and checked by the local vision model ("does it clearly show ...?"). A thing cut off at a side ->
one turn toward it. Up to 3 drives per place; confirmed views are saved in go2/data/views.json and tried first
next time.
Place mode: go_to the saved place, turn to face its target from wherever the dog stopped, photograph, and compare
with the place's preview picture. In the 2026-10-19 tests this stopped in the wrong spot near furniture (the
saved standing spots there have no route; board #17), which is why viewpoint mode exists.

Pictures: go2/data/patrols/<date>/<HHMM>/<place>.jpg (the layout evidence_memory/lab.py reads), plus round.json
with every call and result. Not yet run on the dog: viewpoint mode. A person stays next to the dog; a person at
the console always wins; any error sends stop and release.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://172.17.40.64:8080"
CLIENT = "cheetah-round"
VLM = "http://127.0.0.1:8300/v1/chat/completions"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT = "desk_oliver,water_cooler,workbench,desk_gaofeng,desk_kang,conference_table,sofa"


def http(method, path, body=None, timeout=200):
    data = json.dumps(dict(body or {}, client=CLIENT)).encode() if method == "POST" else None
    req = urllib.request.Request(BASE + path, data, {"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw[:1] in (b"{", b"[") else raw)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:  # noqa: BLE001
            return e.code, {"raw": raw[:300].decode(errors="replace")}


def tool(name, log, **args):
    t0 = time.time()
    code, out = http("POST", f"/agent/{name}", args)
    rec = {"t": round(t0, 2), "call": name, "args": args, "http": code, "out": out, "s": round(time.time() - t0, 1)}
    log.append(rec)
    short = {k: out.get(k) for k in ("result", "reason", "moved_m", "turned_deg", "replans", "route_m")} if isinstance(out, dict) else out
    print(f"  {name} {args} -> {code} {short}", flush=True)
    if code == 409 or (isinstance(out, dict) and out.get("result") in ("refused", "aborted")):
        raise RuntimeError(f"{name}: {out}")
    return out


def check_ready(need_free=True):
    _, st = http("GET", "/agent/status")
    _, s = http("GET", "/state.json")
    owner = (st or {}).get("owner")
    problems = []
    if need_free and owner and owner.get("client") != CLIENT:
        problems.append(f"someone has control: {owner}")
    if (st or {}).get("safe") not in (None, "ok"):
        problems.append(f"safe = {st.get('safe')}")
    mode = (s.get("map") or {}).get("mode")
    if mode != "localized":
        problems.append(f"map mode {mode}: {(s.get('map') or {}).get('status')}")
    return problems, s


def ask_vlm(prompt, images, schema):
    content = [{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(b).decode()}} for b in images]
    content.append({"type": "text", "text": prompt})
    body = {"model": "Qwen/Qwen3.8-27B", "temperature": 0, "max_tokens": 400,
            "messages": [{"role": "user", "content": content}], "chat_template_kwargs": {"enable_thinking": False},
            "response_format": {"type": "json_schema", "json_schema": {"name": "a", "schema": schema}}}
    req = urllib.request.Request(VLM, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(json.loads(r.read())["choices"][0]["message"]["content"])


ARRIVE = {"type": "object", "properties": {
    "same_view": {"type": "string", "enum": ["yes", "partly", "no"]},
    "thing_position": {"type": "string", "enum": ["centred", "left", "right", "not in view"]},
    "turn_deg": {"type": "integer", "minimum": -60, "maximum": 60},
    "why": {"type": "string", "maxLength": 200}}, "required": ["why", "same_view", "thing_position", "turn_deg"]}


def arrival(place, desc, preview, photo):
    """Compare the new photo with the saved preview of the place. turn_deg > 0 = turn left."""
    return ask_vlm(f"Picture 1 is the saved view of the place '{place}' ({desc or 'no description'}). Picture 2 is what the "
                   f"robot's camera sees now, after driving there. Does picture 2 show the same view? Where is the "
                   f"place's main thing in picture 2? If it is off to one side, how many degrees should the robot turn to "
                   f"centre it (positive = turn left, negative = turn right; the camera is about 80 degrees wide)? "
                   f"Reason first.", [preview, photo], ARRIVE)


SHOWS = {"type": "object", "properties": {"why": {"type": "string", "maxLength": 200},
                                          "shows": {"type": "string", "enum": ["clearly", "partly", "no"]},
                                          "turn_deg": {"type": "integer", "minimum": -40, "maximum": 40}},
         "required": ["why", "shows", "turn_deg"]}


def shows(jpg, what):
    return ask_vlm(f"A low robot camera picture. Does it clearly show {what}? 'clearly' = the thing is in view and "
                   f"recognisable; 'partly' = cut off or mostly hidden; 'no' = not in view. If partly and it is cut off at "
                   f"a side, how many degrees should the robot turn to centre it (positive = left)? Reason first.",
                   [jpg], SHOWS)


def view_round_place(p, places, vt, log, r):
    """Viewpoint mode: try ranked viewpoints until a photo clearly shows the thing (at most 3 drives)."""
    import numpy as np
    import nav_proto as N
    import view_plan as V
    from PIL import Image
    import io
    cfg = vt.get(p, {})
    tgt = cfg.get("target_override") or places[p].get("target") or {"x": places[p]["x"], "y": places[p]["y"]}
    _, png = http("GET", "/map.png")
    _, st = http("GET", "/state.json")
    G = N.Grid(np.array(Image.open(io.BytesIO(png)).convert("L")), st["map"])
    mp = st["map_pose"]
    g = G.dijkstra(G.nearest_ok(G.cell(mp["x"], mp["y"])))
    cands = V.viewpoints(G, g, (tgt["x"], tgt["y"]), cfg.get("width_m", 0.6), cfg.get("top_m", 0.8), k=6, name=p)
    r["target_used"], r["candidates"], r["tries"] = tgt, cands, []
    drives = 0
    for c in cands:
        code, plan = http("GET", f"/nav/plan?x={c['x']}&y={c['y']}")
        if not isinstance(plan, dict) or "error" in plan:
            r["tries"].append({"cand": c, "console_plan": plan})
            continue
        if drives >= 3:
            break
        drives += 1
        go = tool("go_to", log, x=c["x"], y=c["y"], yaw_deg=c["yaw_deg"], timeout_s=120)
        t = {"cand": c, "go_to": go}
        if go.get("result") != "done":
            r["tries"].append(t)
            continue
        if c.get("tilt_deg"):
            tool("look", log, deg=c["tilt_deg"])
        ph, jpg = photo(log)
        chk = shows(jpg, cfg.get("show", p.replace("_", " ")))
        print(f"  shows: {chk}", flush=True)
        if chk["shows"] == "partly" and abs(chk["turn_deg"]) >= 8:
            tool("turn", log, deg=float(chk["turn_deg"]))
            ph, jpg = photo(log)
            chk = shows(jpg, cfg.get("show", p.replace("_", " ")))
            print(f"  after turn: {chk}", flush=True)
        if c.get("tilt_deg"):
            tool("look", log, deg=0)
        t.update(photo=ph, check=chk)
        r["tries"].append(t)
        if chk["shows"] == "clearly":
            V.remember_view(p, ph["photo"]["map_pose"], ph["photo"]["url"], chk["why"])
            r["arrived"] = "clearly shown"
            return jpg
        r["last_jpg"] = True
        last = jpg
    r["arrived"] = "not shown"
    return locals().get("last")


def photo(log):
    out = tool("photo", log)
    url = (out.get("photo") or out).get("url")          # the reply nests it: {"result", "photo": {"url", ...}}
    code, jpg = http("GET", url)
    if code != 200 or not isinstance(jpg, bytes):
        raise RuntimeError(f"photo fetch {code}")
    return out, jpg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--places", default=DEFAULT, help="comma list; name:deg tilts the camera at that place")
    ap.add_argument("--home", default="desk_oliver")
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--no-check", action="store_true", help="skip the arrival check")
    ap.add_argument("--stamp", default=None, help="folder time HHMM (default: now)")
    ap.add_argument("--views", action="store_true", help="viewpoint mode: drive to ranked viewpoints until a photo "
                                                          "clearly shows the thing (view_plan.py, view_targets.json)")
    a = ap.parse_args()
    items = [(p.split(":")[0], float(p.split(":")[1]) if ":" in p else 0.0) for p in a.places.split(",") if p]
    _, places = http("GET", "/places")
    missing = [p for p, _ in items + [(a.home, 0)] if p not in places]
    if missing:
        sys.exit(f"unknown places: {missing}")
    for p, _ in items + [(a.home, 0)]:
        code, plan = http("GET", f"/nav/plan?place={p}")
        print(f"plan {p}: {plan.get('length_m') if isinstance(plan, dict) else plan} m {plan.get('error', '') if isinstance(plan, dict) else ''}")
    if a.plan_only:
        return
    problems, _ = check_ready()
    if problems:
        sys.exit("not starting: " + "; ".join(problems))
    out_dir = ROOT / "data" / "patrols" / time.strftime("%Y-%m-%d") / (a.stamp or time.strftime("%H%M"))
    out_dir.mkdir(parents=True, exist_ok=True)
    log, rec = [], {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "places": {}, "home": a.home}
    try:
        tool("claim", log)
        vt = json.loads((Path(__file__).parent / "view_targets.json").read_text())
        for p, deg in items:
            print(f"{p}:", flush=True)
            if a.views:
                r = {}
                jpg = view_round_place(p, places, vt, log, r)
                if jpg:
                    (out_dir / f"{p}.jpg").write_bytes(jpg)
                rec["places"][p] = r
                continue
            r = {"go_to": tool("go_to", log, place=p, timeout_s=120)}
            for _ in range(2):      # "no route" came and went with the live lidar in the first test (17:35)
                if r["go_to"].get("result") != "no_route":
                    break
                time.sleep(2)
                r["go_to"] = tool("go_to", log, place=p, timeout_s=120)
            if r["go_to"].get("result") != "done":
                r["skipped"] = "go_to " + str(r["go_to"].get("result"))
                rec["places"][p] = r
                continue
            # Face the thing itself: go_to may stop away from the standing spot (a standing spot in a tight corner
            # has no route, and the console then drives to the nearest open floor), so turn from where the dog
            # actually is toward the place's target (17:45 test: the cooler run ended facing a chair).
            tgt, mp = places[p].get("target"), r["go_to"].get("map_pose")
            if tgt and mp:
                bearing = math.degrees(math.atan2(tgt["y"] - mp["y"], tgt["x"] - mp["x"]))
                dturn = (bearing - math.degrees(mp["yaw"]) + 180) % 360 - 180
                r["face_target"] = {"bearing_deg": round(bearing, 1), "turn_deg": round(dturn, 1),
                                    "dist_m": round(math.hypot(tgt["x"] - mp["x"], tgt["y"] - mp["y"]), 2)}
                if abs(dturn) > 10:
                    tool("turn", log, deg=round(dturn, 1))
            if deg:
                r["look"] = tool("look", log, deg=deg)
            ph, jpg = photo(log)
            r["photos"] = [ph]
            if not a.no_check:
                code, prev = http("GET", f"/places/{p}.jpg")
                for k in range(2):
                    chk = arrival(p, places[p].get("description"), prev, jpg) if code == 200 else None
                    r.setdefault("checks", []).append(chk)
                    print(f"  check: {chk}", flush=True)
                    # turn only when the view matches and the thing is to one side; in a test the model also gave
                    # turn angles for views of a different place, which would send the dog the wrong way
                    if not chk or chk["same_view"] == "no" or chk["thing_position"] not in ("left", "right") \
                            or abs(chk["turn_deg"]) < 8:
                        r["arrived"] = "confirmed" if chk and chk["same_view"] != "no" else "not confirmed"
                        break
                    tool("turn", log, deg=float(chk["turn_deg"]))
                    ph, jpg = photo(log)
                    r["photos"].append(ph)
            (out_dir / f"{p}.jpg").write_bytes(jpg)
            if deg:
                tool("look", log, deg=0)
            rec["places"][p] = r
        rec["home_go_to"] = tool("go_to", log, place=a.home, timeout_s=120)
    except (Exception, KeyboardInterrupt) as e:  # noqa: BLE001
        rec["error"] = repr(e)
        print("STOPPING:", repr(e), flush=True)
        http("POST", "/agent/stop")
    finally:
        http("POST", "/agent/release")
        rec["ended"] = time.strftime("%Y-%m-%d %H:%M:%S")
        rec["log"] = log
        (out_dir / "round.json").write_text(json.dumps(rec, indent=1, default=str))
        print(f"saved {len(list(out_dir.glob('*.jpg')))} pictures and round.json in {out_dir}")


if __name__ == "__main__":
    main()
