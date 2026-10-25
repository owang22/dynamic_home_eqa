"""Write navigation/api_spec.json: the console API (go2_dashboard.py on :8080) as data, for agents and checks.

    python3 navigation/tools/make_api_spec.py            # reads the code next to it (navigation/*.py)
    python3 navigation/tools/make_api_spec.py ~/oliver   # or the live copy

Routes and constants are read from the code itself (ast, no imports: the modules need ROS and the dog), so
they can't drift from it. Descriptions live only here, in ENDPOINTS; "{NAME}" in a description is filled with
that constant's value from the code. The script fails if the code has a route ENDPOINTS doesn't describe, or
ENDPOINTS describes a route the code doesn't have.

"extra_ok": true = the reply may carry more top-level fields than "returns" lists.
Field types in "returns": number, integer, string, bool, object, array, any; "|null" = may be null;
a trailing "?" on a field name = only present sometimes (see the field's text).
"""
import ast
import json
import math
import re
import sys
from pathlib import Path

NAV = Path(__file__).resolve().parents[1]
SRC = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else NAV
MODULES = ("go2_agent", "go2_dashboard", "go2_mapper", "go2_nav", "go2_markers", "go2_history", "go2_trail")


# ---------- reading the code ----------

def constants(path):
    """Top-level NAME = <literal or simple math> assignments of a module."""
    out = {}
    for node in ast.parse(path.read_text()).body:
        if not isinstance(node, ast.Assign):
            continue
        targets = node.targets[0]
        names = [targets] if isinstance(targets, ast.Name) else list(getattr(targets, "elts", []))
        if not all(isinstance(n, ast.Name) and n.id.isupper() for n in names):
            continue
        try:
            val = eval(compile(ast.Expression(node.value), str(path), "eval"), {"math": math, **out})
        except Exception:
            continue
        if not isinstance(val, (int, float, str, bool, tuple, list, dict, type(None))):
            continue
        if len(names) == 1:
            out[names[0].id] = val
        elif isinstance(val, tuple) and len(val) == len(names):
            out.update({n.id: v for n, v in zip(names, val)})
    return out


def routes(path):
    """(method, path) pairs the console's Handler answers, from do_GET/do_POST and AGENT_CALLS."""
    src = path.read_text()
    tree = ast.parse(src)
    handler = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Handler")
    found = set()
    for fn in handler.body:
        if not isinstance(fn, ast.FunctionDef) or fn.name not in ("do_GET", "do_POST"):
            continue
        method = fn.name[3:]
        for node in ast.walk(fn):
            if isinstance(node, ast.Compare) and isinstance(node.ops[0], (ast.Eq, ast.In)):
                for c in [node.left, *node.comparators]:
                    for s in ([c] if isinstance(c, ast.Constant) else getattr(c, "elts", [])):
                        if isinstance(s, ast.Constant) and isinstance(s.value, str) and s.value.startswith("/"):
                            found.add((method, s.value))
            if (method == "GET" and isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "startswith" and node.args and isinstance(node.args[0], ast.Constant)):
                found.add((method, node.args[0].value + "*"))   # /trail/<...>.jpg and the like
    calls = constants(path).get("AGENT_CALLS", ())
    found |= {("POST", f"/agent/{c}") for c in calls}
    return found


# ---------- descriptions (the one place they are written) ----------

COMMON_TOOL_RETURNS = {
    "result": "string: done | blocked | no_route | timeout | aborted | refused | error",
    "stop_reason": "string: one word to branch on (see stop_reasons)",
    "reason?": "string: why it did not finish (all but done)",
    "odom": "object|null: {x, y, yaw (rad)} in the odom frame at the end",
    "map_pose": "object|null: {x, y, yaw (rad)} on the map at the end (5 Hz copy)",
    "fit": "number|null: loc.track_fit at the end (about 0.75-0.9 when placed right)",
    "lost": "bool: loc.lost at the end",
    "t": "number: unix time of the reply",
    "localization_notice?": "object: line-up events since this client's previous call (see notes.localization_notice)",
}
TOOL_TYPES = {"result": "string", "stop_reason": "string", "reason?": "string", "odom": "object|null",
              "map_pose": "object|null", "fit": "number|null", "lost": "bool", "t": "number",
              "localization_notice?": "object"}
CLIENT = {"type": "string", "required": True, "text": "who you are; owner and log use it. Use the same one for every call"}
NOTE = {"type": "string", "text": "what you are doing and why (shown on the console, kept with photos, 2000 chars)"}
TIMEOUT = {"type": "number", "units": "s", "default": 30, "text": "the call gives up with result timeout after this long"}


def tool(path, summary, params, returns, blocks, latency, extra=None):
    ps = {"client": CLIENT, **params, "note": NOTE}
    rt = {**{k: v.split(":")[0] for k, v in COMMON_TOOL_RETURNS.items()}, **returns}
    return {"method": "POST", "path": path, "for_agents": True, "needs_claim": True, "tool": True, "blocks": blocks,
            "latency": latency, "summary": summary, "params": ps, "returns": rt, **(extra or {})}


ENDPOINTS = [
    # ----- agent: ownership and talk -----
    {"method": "POST", "path": "/agent/claim", "for_agents": True, "needs_claim": False, "blocks": False, "latency": "<50 ms",
     "summary": "Take control (or refresh it). Every tool call also claims and refreshes; the claim lapses after "
                "{AGENT_LEASE_S} s without a call. 409 refused if a person has taken over or another agent holds it.",
     "params": {"client": CLIENT},
     "returns": {"result": "string", "lease_s": "number"},
     "errors": {"409": "{result: refused, stop_reason: refused, reason: 'A person at <ip> has taken over' | 'Agent <client> has control'}"}},
    {"method": "POST", "path": "/agent/release", "for_agents": True, "needs_claim": False, "blocks": False, "latency": "<50 ms",
     "summary": "Give up control. result done if you held it, not_owner otherwise. Release when you finish.",
     "params": {"client": CLIENT}, "returns": {"result": "string"}},
    {"method": "POST", "path": "/agent/stop", "for_agents": True, "needs_claim": False, "blocks": False, "latency": "<50 ms",
     "summary": "Always allowed, from anyone: aborts the running tool (it ends with stop_reason stop) and stops the "
                "dog. Does not change who owns it.",
     "params": {"client": CLIENT}, "returns": {"result": "string"}},
    {"method": "POST", "path": "/agent/say", "for_agents": True, "needs_claim": False, "blocks": False, "latency": "<50 ms",
     "summary": "Post a short note ('what I'm doing') on the console, 300 chars. Does not claim or refresh the lease.",
     "params": {"client": CLIENT, "text": {"type": "string", "text": "the note"}}, "returns": {"result": "string"}},
    {"method": "POST", "path": "/agent/status", "for_agents": True, "needs_claim": False, "blocks": False, "latency": "<50 ms",
     "summary": "Who owns the dog, the running tool, safety, pose, markers, battery and the call log. No claim needed.",
     "params": {"client": CLIENT},
     "returns": {"owner": "object|null", "current": "object|null", "notes": "object", "log": "array", "photos": "array",
                 "odom": "object|null", "map_pose": "object|null", "safe": "string", "markers": "array",
                 "battery": "object|null", "localization_notice?": "object"},
     "fields": {"owner": "{kind: agent|human, client, ip, t, idle_s} or null (nobody; a lapsed lease shows null)",
                "current": "{client, call, args, t, secs} of the running tool, or null",
                "safe": "ok, or why tools would refuse now: stale_sensors | fallen | not_standing: ...",
                "log": "last 40 calls: {t, client, call, dur_s, note, args, result, stop_reason, ...}",
                "photos": "meta of the last 8 photos"}},
    # ----- agent: tools (blocking) -----
    tool("/agent/move", "Walk straight forward (+) or back (-) by m metres on odometry, then stop. Forward is clamped "
         "to {MAX_MOVE_M} m, back to {MAX_BACK_M} m. Forward speed {MIN_SPEED}-{MOVE_SPEED} m/s, back {BACK_SPEED} m/s. Ends blocked "
         "if an obstacle is in the box ahead/behind, or if it makes under {STALL_M} m progress in {STALL_S} s "
         "(after one re-plant step and retry). Behind is checked against the lidar and the saved map; ahead the "
         "dog's own avoidance slows and stops it, which then shows as stuck. Does not check loc.lost.",
         {"m": {"type": "number", "units": "m", "required": True, "clamp": "{MOVE_CLAMP}", "frame": "body: + forward"},
          "timeout_s": TIMEOUT},
         {"moved_m": "number", "side?": "string"}, True, "about 1 s + m / 0.5 m/s"),
    tool("/agent/turn", "Turn in place by deg (+ = left, counter-clockwise seen from above; - = right), clamped to "
         "±{MAX_TURN_DEG}. Turns at {TURN_SPEED} rad/s with a small forward/back rock, stops early for the overshoot, "
         "corrects once if more than 5 degrees off, then re-plants the feet. turned_deg is what odometry measured. "
         "Ends blocked (stuck) if it turns under 3 degrees in {STALL_S} s after one re-plant.",
         {"deg": {"type": "number", "units": "deg", "required": True, "clamp": "{TURN_CLAMP}", "frame": "+ = left (CCW)"},
          "timeout_s": TIMEOUT},
         {"turned_deg": "number"}, True, "about 3 s + |deg| / 34 deg/s"),
    tool("/agent/look", "Tilt the camera up (+) or down (-) by pitching the body while standing, clamped to ±{HEAD_MAX_DEG} "
         "degrees; 0 levels it. Any walking levels it again by itself. Waits 1.5 s.",
         {"deg": {"type": "number", "units": "deg", "required": True, "clamp": "{LOOK_CLAMP}", "frame": "+ = up"}},
         {"look_deg": "number", "body_pitch_deg": "number|null"}, True, "about 1.6 s"),
    tool("/agent/photo", "Stop, wait until the dog has stood still {STILL_S} s (at most 5 s), keep one full-size "
         "frame (1280x720). photo.still is false if it never settled. inline: true adds the JPEG as base64.",
         {"inline": {"type": "bool", "default": False, "text": "also return photo.jpeg_b64"}},
         {"photo": "object"}, True, "1-5 s",
         {"fields": {"photo": "{id, url (/agent/photos/<id>.jpg), client, t, width, height, still, look_deg, odom, "
                              "map_pose, note?, jpeg_b64?}"}}),
    tool("/agent/look_around", "n photos, turning 360/n degrees after each (n clamped 1-12, default 4). The last "
         "turn brings it back to the start heading. If a turn fails it returns what it has so far.",
         {"n": {"type": "integer", "default": 4, "clamp": [1, 12]},
          "inline": {"type": "bool", "default": False}, "timeout_s": TIMEOUT},
         {"photos": "array"}, True, "about n x 9 s"),
    tool("/agent/go_to", "Drive to a saved place or a map point along a planned route around furniture, then face "
         "the place's target (or yaw_deg). Re-plans up to {MAX_REPLANS} times around obstacles not on the map. "
         "Narrow ('squeeze') routes: drives to {SQUEEZE_STOP_M} m before the narrow part, then re-plans with the "
         "live lidar. Desk and table tops (~0.7 m) do NOT block, so a route may pass under a desk: the live view "
         "drops cells whose highest point is a desk top, and only saved-map points (legs, drawers, chairs) block "
         "there. Blocking them (OVERHEAD_MAX 1.0) closed real routes on 10-23 and was reverted to {OVERHEAD_MAX}, "
         "which turns the overhead rule off; open problem. Preview with /nav/plan and be suspicious of routes "
         "under desks. "
         "Stops with stop_reason lost if loc.lost comes on ({GO_TO_STOP_WHEN_LOST}). Close enough "
         "within {GOAL_TOL_M} m. Preview the route first with GET /nav/plan.",
         {"place": {"type": "string", "text": "id of a saved place (GET /places); or give x, y"},
          "x": {"type": "number", "units": "m", "frame": "map"}, "y": {"type": "number", "units": "m", "frame": "map"},
          "yaw_deg": {"type": "number", "units": "deg", "frame": "map, + = CCW from map +x",
                      "text": "heading to end at (x, y goals only; a place uses its target or yaw_deg)"},
          "timeout_s": TIMEOUT},
         {"moved_m": "number", "replans": "integer", "route_m?": "number", "target?": "object|null", "why?": "object",
          "side?": "string", "at?": "array"}, True, "route_m / ~0.4 m/s + turns; set timeout_s to fit (default 30 s is short)",
         {"fields": {"route_m": "length of the first planned route (done only)",
                     "target": "the place's target {x, y} (done, place goals with a target)",
                     "why": "on a failed plan: {saved_map_has_route, cause: 'saved map' | 'live lidar or temporary blocks', "
                            "live_new_cells, blocks}",
                     "at": "map spot [x, y] where it was blocked"}}),
    tool("/agent/posture", "Stand up or lie down, as the console buttons do; waits until the body height shows it "
         "(stand: >= {STAND_H} m, lie: < {MIN_BODY_H} m; at most {POSTURE_S} s). The dog is not stopped afterwards. "
         "Anything but pose stand|lie (or a body_height field) is a 400 bad arguments.",
         {"pose": {"type": "string", "required": True, "enum": ["stand", "lie"]}},
         {"pose": "string", "body_height": "number|null"}, True, "2-8 s"),
    tool("/agent/relocalize", "Where is the dog on the map? search: the best line-ups of the recent lidar views "
         "within radius_m of (x, y) or of the current pose; global: anywhere on the map. Neither applies anything. "
         "set: put the dog at (x, y, yaw) exactly; refused if that fits the lidar more than 0.02 worse than the "
         "current pose, unless force. Does not move the dog.",
         {"mode": {"type": "string", "default": "search", "enum": ["search", "global", "set"]},
          "x": {"type": "number", "units": "m", "frame": "map", "text": "search centre, or the pose for set"},
          "y": {"type": "number", "units": "m", "frame": "map"},
          "radius_m": {"type": "number", "units": "m", "default": 3.0, "clamp": "{RELOC_R}"},
          "top": {"type": "integer", "default": 5, "clamp": [1, 10]},
          "yaw_deg": {"type": "number", "units": "deg", "frame": "map", "text": "set: heading (or yaw in rad)"},
          "yaw": {"type": "number", "units": "rad", "frame": "map"},
          "force": {"type": "bool", "default": False, "text": "set: apply even if it fits worse"}},
         {"mode?": "string", "candidates?": "array", "current?": "object", "searched?": "object|null",
          "fit_before?": "number|null", "fit_after?": "number|null", "pose?": "object|null"}, True,
         "search/global about 4-9 s (CPU search); set <0.5 s",
         {"fields": {"candidates": "[{x, y, yaw (rad), yaw_deg, score (line-up score), fit (track_fit measure)}] best first, "
                                   "at least {CAND_SEP_M} m or {CAND_SEP_DEG} deg apart",
                     "current": "{pose, fit, lost, lost_since}: the pose before this call (search/global and refused set)",
                     "pose": "set: the new map pose"}}),
    # ----- reading (no claim) -----
    {"method": "GET", "path": "/agent/status", "for_agents": True, "blocks": False, "latency": "<50 ms",
     "summary": "Same as POST /agent/status; ?client=<you> adds localization_notice.",
     "params": {"client": {"type": "string", "text": "query parameter"}},
     "returns": {"owner": "object|null", "current": "object|null", "notes": "object", "log": "array", "photos": "array",
                 "odom": "object|null", "map_pose": "object|null", "safe": "string", "markers": "array",
                 "battery": "object|null", "localization_notice?": "object"}},
    {"method": "GET", "path": "/state.json", "for_agents": True, "blocks": False, "latency": "<100 ms",
     "summary": "Everything the console shows, one snapshot (GET /events streams the same at 10 Hz).",
     "returns": {"imu": "object|null", "odom": "object|null", "state": "object|null", "joints": "object|null",
                 "cloud": "object|null", "map": "object|null", "map_pose": "object|null", "age": "object", "rec": "object",
                 "agents": "object", "nav": "object|null", "loc": "object", "markers": "object|null",
                 "battery": "object|null", "live": "object|null", "control": "object"},
     "fields": {"odom": "{pos: [x, y, z], yaw (rad), vel: [vx, vy (m/s, body), wz (rad/s)], frame}",
                "imu": "{rpy: [roll, pitch, yaw] rad, gyro, acc, temp}",
                "state": "{mode, gait, body_height (m), foot_raise, velocity, obstacle: [4 ranges, m, from the dog's "
                         "sport state], foot_force}",
                "map": "{resolution, origin, width, height, t, mapped_m2, mode: mapping|localized|not_aligned, status, "
                       "align, saved_at, track, room_deg}",
                "map_pose": "{x, y, yaw (rad)} on the map, 5 Hz, or null when not lined up",
                "age": "seconds since each sensor's last message: odom, imu, state, cloud, camera, map, map_pose, ...",
                "loc": "{status, seq, events, track, fit, runner_up, unsure, lost, lost_since, track_fit, fresh_fit, suspect, "
                       "suspect_since}",
                "nav": "{path, goal, t} of the last plan (5 min)",
                "markers": "as GET /markers", "battery": "{soc %, current_ma, cycles, voltage, bms_temp_c, age_s, stale?}",
                "control": "{avoid, speed, speeds, look_deg, driver, driver_ip}"}},
    {"method": "GET", "path": "/events", "for_agents": True, "blocks": False, "latency": "stream",
     "summary": "Server-sent events: one /state.json snapshot every 0.1 s, forever. Prefer /state.json for polling."},
    {"method": "GET", "path": "/history", "for_agents": True, "blocks": False, "latency": "<200 ms",
     "summary": "State once a second over the last {KEEP_S} s (also on disk per day), plus line-up events and agent "
                "calls in the window. For working out afterwards why something went wrong.",
     "params": {"keys": {"type": "string", "text": "comma-separated names or prefixes from {KEYS}; default all"},
                "since": {"type": "number", "units": "unix s"}, "until": {"type": "number", "units": "unix s"},
                "step": {"type": "number", "units": "s", "text": "at most one sample per step"},
                "limit": {"type": "integer", "default": 3600, "text": "the newest this many"}},
     "returns": {"keys": "array", "period_s": "number", "kept_s": "number", "n": "integer", "samples": "array",
                 "loc_events": "array", "agent_calls": "array"},
     "errors": {"400": "{result: error, reason} for a non-number since/until/step/limit"}},
    {"method": "GET", "path": "/places", "for_agents": True, "blocks": False, "latency": "<50 ms",
     "summary": "Saved places: {id: {id, x, y, yaw_deg, pitch_deg, description, target: {x, y}|null, preview, map, "
                "saved_by, saved_at, marked_on_map, moved_by?, moved_at?, note? (offline map tools)}}. (x, y, yaw_deg) is where the dog stands; "
                "target is where the thing is. go_to {place} drives to the stand spot and faces the target.",
     "returns": {}},
    {"method": "GET", "path": "/places/*", "for_agents": True, "blocks": False, "latency": "<50 ms",
     "summary": "/places/<id>.jpg: the place's camera view (404 if none)."},
    {"method": "GET", "path": "/nav/plan", "for_agents": True, "blocks": False, "latency": "50-500 ms",
     "summary": "Preview a go_to route from where the dog is now, without moving: ?place=<id> or ?x=&y= (map m). "
                "Uses the live lidar like go_to does.",
     "params": {"place": {"type": "string"}, "x": {"type": "number", "units": "m", "frame": "map"},
                "y": {"type": "number", "units": "m", "frame": "map"}},
     "returns": {"path?": "array", "length_m?": "number", "goal?": "array", "tight?": "bool", "squeeze?": "bool",
                 "squeeze_at?": "array", "squeeze_along_m?": "number", "squeeze_clear_m?": "number",
                 "error?": "string", "why?": "object", "fallback?": "string"},
     "fields": {"path": "[[x, y], ...] map m, first point = the dog (or its spot, then the nearest open floor)",
                "goal": "the goal actually used: moved up to {GOAL_SNAP_M} m off furniture onto open floor",
                "tight": "true: no route with {ROBOT_R} m clearance, this one keeps {ROBOT_R_TIGHT} m (or less if squeeze)",
                "squeeze": "true: only fits with {ROBOT_R_SQUEEZE} m clearance more than {SQUEEZE_NEAR_M} m away; go_to "
                           "drives up to it and re-plans; within {SQUEEZE_NEAR_M} m of the dog only within {TRAIL_R} m of where it "
                           "walked in the last {TRAIL_S} s (leaving a pocket the way it came)",
                "fallback": "live_noblocks: no clearance worked normally, this route ignores the {BLOCK_S} s stall blocks "
                            "(live obstacles keep full clearance). Not used while loc.lost (nor the trail squeeze)",
                "error": "why there is no route", "why": "as in go_to"},
     "errors": {"409": "{error: 'not lined up with the map'}", "400": "{error} unknown place or bad x/y"}},
    {"method": "GET", "path": "/markers", "for_agents": True, "blocks": False, "latency": "<50 ms",
     "summary": "ArUco markers in view now (DICT_4X4_50, {SIZE_M} m): ids {KNOWN}, detected up to {RATE_HZ} Hz on the "
                "full-size frame. Empty list if the newest detection is older than 1 s. A marker missed in the newest "
                "frame but seen within {HOLD_S} s stays in the list with held: true (never fix_ok): skip held items "
                "for a live sighting. bearing_deg + = RIGHT of straight ahead (opposite to /trail/near). fix_ok: "
                "good enough for a position fix (dist <= {FIX_MAX_DIST_M} m, view_deg <= {FIX_MAX_VIEW_DEG}, "
                "min_side_px >= {FIX_MIN_SIDE_PX}, reproj_px <= {FIX_MAX_REPROJ_PX}, edge <= {FIX_MAX_EDGE}, and the "
                "same id at a range within 15% in another of the last {FIX_HISTORY} frames within 1 s); otherwise why "
                "lists the failed rules: far, oblique, small, reproj, edge, unconfirmed. Camera model {CAMERA_MODEL}.",
     "returns": {"t": "number", "frame_t": "number", "list": "array", "ms": "number|null", "age_s": "number|null",
                 "err?": "string|null"},
     "fields": {"list": "[{id, mark, z (m along the camera axis), x (m, + right), up (m), bearing_deg (+ right), "
                        "side_px (first edge, px), dist (m, straight line), view_deg (0 = head-on), yaw_deg (turn of the "
                        "marker face, 0 = square to the camera), reproj_px, ambig (best/second pose error, 1.0 = the two "
                        "IPPE poses can't be told apart; null if only one), alt (the other pose: {view_deg, yaw_deg, "
                        "reproj_px} or null), min_side_px (shortest side, full-res px; under {MIN_SIDE_PX} is not "
                        "reported), edge (centre offset, 1 = image border), fix_ok, why, held, seen_age_s}]",
                "err": "the detector thread's last exception, or null (absent before the first frame)"}},
    {"method": "GET", "path": "/trail/near", "for_agents": True, "blocks": False, "latency": "<100 ms",
     "summary": "Camera frames taken near a map point: first those whose camera faced it (|bearing| <= {FOV_HALF_DEG} "
                "deg or within 0.3 m), nearest first. bearing_deg + = LEFT of the frame's centre (opposite to /markers). "
                "spot: obstacle | open | unseen on the map.",
     "params": {"x": {"type": "number", "units": "m", "frame": "map", "required": True},
                "y": {"type": "number", "units": "m", "frame": "map", "required": True},
                "radius": {"type": "number", "units": "m", "default": 3.0, "clamp": [None, 20.0]},
                "limit": {"type": "integer", "default": 12, "clamp": [1, 200]}},
     "returns": {"views": "array", "spot": "string"},
     "fields": {"views": "[{t, x, y, yaw_deg, dist, bearing_deg (+ left), facing, url}]"},
     "errors": {"400": "x and y are required (plain-text error page)"}},
    {"method": "GET", "path": "/trail/since", "for_agents": True, "blocks": False, "latency": "<200 ms",
     "summary": "Frames newer than ?t= (unix s), oldest first, ?limit= (default 500, max 2000); page with the last t.",
     "params": {"t": {"type": "number", "units": "unix s", "default": 0},
                "limit": {"type": "integer", "default": 500, "clamp": [1, 2000]}},
     "returns": {"frames": "array", "more": "bool"}, "fields": {"frames": "[{t, x, y, yaw_deg, url}]"}},
    {"method": "GET", "path": "/trail/coverage", "for_agents": True, "blocks": False, "latency": "<200 ms",
     "summary": "Spots [[x, y], ...] (0.25 m cells) where trail frames exist.", "returns": {}},
    {"method": "GET", "path": "/trail/*", "for_agents": True, "blocks": False, "latency": "<50 ms",
     "summary": "/trail/<YYYYMMDD>/<ms>.jpg: one trail frame (640x360)."},
    {"method": "GET", "path": "/frame.jpg", "for_agents": True, "blocks": False, "latency": "<100 ms",
     "summary": "The latest full-size camera frame (1280x720), header X-Frame-Age (s). 503 before the first frame. "
                "For a frame taken standing still use the photo tool."},
    {"method": "GET", "path": "/camera.jpg", "for_agents": True, "blocks": True, "latency": "up to 5 s",
     "summary": "The stream frame newer than ?after=<t>, header X-Frame-T; waits up to 5 s, else 204."},
    {"method": "GET", "path": "/camera.mjpg", "for_agents": False, "blocks": False, "latency": "stream",
     "summary": "MJPEG stream for the console page."},
    {"method": "GET", "path": "/agent/photos/*", "for_agents": True, "blocks": False, "latency": "<50 ms",
     "summary": "/agent/photos/<id>.jpg: a photo an agent took (the last 60 are kept; 404 after)."},
    {"method": "GET", "path": "/map.png", "for_agents": True, "blocks": False, "latency": "<50 ms",
     "summary": "The map image, north up; pixel <-> map metres via /state.json map.origin and map.resolution. 503 if no map."},
    {"method": "GET", "path": "/map/layer.png", "for_agents": True, "blocks": False, "latency": "<200 ms",
     "summary": "One height layer, same crop as /map.png: ?layer=mid (desk/table tops {MID_H} m) | high {HIGH_H} m | ceiling."},
    {"method": "GET", "path": "/map/objects", "for_agents": True, "blocks": False, "latency": "<50 ms",
     "summary": "Labelled objects on the map: {objects: [{id, label, name, x, y, w, h, yaw (rad), ...}]}.",
     "returns": {"objects": "array"}},
    {"method": "GET", "path": "/map/proposals", "for_agents": True, "blocks": False, "latency": "<50 ms",
     "summary": "The tidy pass's proposals for people to review: {items: [...], ...} (other top-level keys are "
                "the tidy run's own: generated, map, params, walls, ...).", "returns": {"items": "array"}, "extra_ok": True},
    {"method": "GET", "path": "/control", "for_agents": True, "blocks": False, "latency": "<50 ms",
     "summary": "Whether your address may send POSTs (localhost and 172.17.0.0/18): {allowed, you}.",
     "returns": {"allowed": "bool", "you": "string"}},
    {"method": "GET", "path": "/", "for_agents": False, "summary": "The console page (also /index.html)."},
    {"method": "GET", "path": "/index.html", "for_agents": False, "summary": "The console page."},
    # ----- people only -----
    {"method": "POST", "path": "/cmd", "for_agents": False,
     "summary": "The console's drive channel: move [vx, vy, wz], action stand|lie|stop, avoid, look_deg, speed, takeover, "
                "handback, record. action stop is allowed for anyone and a console STOP also locks agents out until "
                "Hand back. Agents use /agent/* instead."},
    {"method": "POST", "path": "/map", "for_agents": False,
     "summary": "Map control: action start|new|extend|stop|save|revert|clear|frame {T}|align|localize_at {x, y, yaw_deg?}. "
                "Agents use /agent/relocalize."},
    {"method": "POST", "path": "/map/objects", "for_agents": False,
     "summary": "People correct object labels: {action: rename|relabel|move|delete|confirm, id, ...}."},
    {"method": "POST", "path": "/map/proposals", "for_agents": False,
     "summary": "People review tidy proposals: {action: accept|reject|accept_all, id?, min_confidence?}."},
    {"method": "POST", "path": "/places", "for_agents": False,
     "summary": "Save a place: {id, description} where the dog is now, or {id, target {x, y}, stand {x, y, yaw_deg}?, view?}."},
    {"method": "POST", "path": "/places/move", "for_agents": False,
     "summary": "A person dragged a place: {id, x?, y?, yaw_deg?, target?: {x, y} | null}."},
    {"method": "POST", "path": "/places/delete", "for_agents": False, "summary": "{id}: delete a place."},
    {"method": "POST", "path": "/label/example", "for_agents": False,
     "summary": "A person boxes an object in a trail frame: {url, box, name, label?, place?}."},
    {"method": "POST", "path": "/label/remove", "for_agents": False, "summary": "{id}: remove a labelling example."},
    {"method": "GET", "path": "/label/detect", "for_agents": False,
     "summary": "The vision model's boxes in a trail frame (?url=); calls the 8B on :8000."},
    {"method": "GET", "path": "/label/examples", "for_agents": False, "summary": "Labelling examples (?name=)."},
]

STOP_REASONS = {
    "arrived": "move, turn or go_to finished. Carry on.",
    "done": "any other tool finished.",
    "obstacle": "blocked by something in the obstacle box (move) or not on the map (go_to). Look (photo), then go "
                "around: turn and move, or go_to again (it plans around it for {BLOCK_S} s).",
    "stuck": "no progress for {STALL_S} s after one re-plant step: avoidance stopped the dog, or a foot or leg is caught. "
             "Photo first; back up a little (slowly) or turn, then retry. Twice in a row: ask a person.",
    "no_route": "the planner found no route. Near furniture this often means the map pose is off: check fit/lost, "
                "relocalize, then GET /nav/plan before trying again. why.cause says whether the saved map alone had a route.",
    "timeout": "timeout_s ran out mid-way. The dog stopped where it was; give go_to a longer timeout_s.",
    "stop": "an agent's /agent/stop or someone pressed STOP. Don't resume blindly: check status first.",
    "person": "a person took over. Your claim is gone until they hand back (or {HUMAN_HOLD_S} s without console "
              "commands). Wait; poll status every 10-30 s.",
    "lost": "go_to stopped because loc.lost is on: the map pose is probably wrong. relocalize (search, then global), "
            "set the best candidate if its fit is clearly best, then go_to again.",
    "not_standing": "the dog is lying down: posture {pose: stand}, then retry.",
    "fallen": "roll or pitch over {TILT_LIMIT} rad. Stop everything and ask a person.",
    "stale_sensors": "odometry or IMU older than {STALE_S} s: the driver or the dog is off. Don't drive; tell a person.",
    "refused": "409: a person has taken over or another agent has control (claim or any call that needs a claim): "
               "wait, poll status. Or relocalize set: the pose fits worse than the current one (send force only if "
               "you are sure).",
    "busy": "409: another tool is still running (often your own previous call after a client timeout). Wait, or stop.",
    "bad_arguments": "400: missing or wrong arguments; nothing ran and nothing was logged. Fix the call.",
    "error": "anything else: read reason (bad place id, no_map_pose, no_camera_frame, posture timeout, ...).",
}

NOTES = {
    "frames": "odom: the dog's own frame, restarts at every reboot, drifts in heading standing still (median +1.2 deg/min, -4 to +6 per period; pose logs 10-23..25). "
              "map: the saved lab map; map = R(th) * odom + t with T = (tx, ty, th) from line-up and drift tracking. "
              "Places, go_to, /nav/plan, /trail and relocalize are in map metres. yaw fields are radians "
              "(CCW from +x, in [-pi, pi)); *_deg fields are degrees. move/turn work on odometry only.",
    "signs": "turn deg + = left (CCW). look deg + = up. move m + = forward. /markers bearing_deg + = right "
             "(atan2(x, z), camera x to the right). /trail/near bearing_deg + = left (map angle to the spot minus the "
             "frame's yaw). map yaw + = CCW.",
    "ownership": "One agent owns the dog at a time. claim, or any tool call, takes and refreshes it; it lapses after "
                 "{AGENT_LEASE_S} s without a call. status, stop, release and say need no claim. A person always wins: "
                 "driving at the console, Take over, or a console STOP aborts the running tool (stop_reason person or "
                 "stop) and locks agents out (409 refused) until Hand back or {HUMAN_HOLD_S} s without console commands. "
                 "/agent/stop is allowed for anyone and does not change the owner. One tool at a time: a second call "
                 "while one runs gets 409 {result: error, reason: 'busy: ...', stop_reason: busy}.",
    "safety": "Before any motion tool and every 0.1 s during it: odom and IMU fresher than {STALE_S} s, |roll| and "
              "|pitch| under {TILT_LIMIT} rad, body_height at least {MIN_BODY_H} m. Obstacle box ahead {FRONT_CLEAR} "
              "(x from, x to, half width, m) when avoidance is off; behind {REAR_CLEAR}, always checked; heights "
              "{BUMP_H} m count. Backing up is slow ({BACK_SPEED} m/s) and short ({MAX_BACK_M} m) because the dog "
              "sees little behind it.",
    "localization": "loc.track_fit: how well the latest lidar view sits on the map's walls, about 0.75-0.9 when placed "
                    "right. The tracker matches only lidar voxels first seen in the last {TRACK_FRESH_S} s (falls back to all "
                    "when fewer than {TRACK_FRESH_MIN} fresh obstacle points): /point_cloud2 is the dog's accumulated "
                    "voxel map, and old voxels carry old heading drift. So track_fit can dip after a long time "
                    "standing still without the pose being wrong. loc.lost turns on when track_fit stays under {LOST_FIT} for {LOST_S} s while the dog walks "
                    "at least {LOST_MOVE_M} m; it clears at {LOST_CLEAR} or on a new placement or line-up. loc.fit, "
                    "runner_up and unsure describe the last line-up only (unsure: score under 0.3 or less than 0.05 "
                    "ahead of the next heading). Event kinds: hand_placement, auto_align, session_restore, new_map, "
                    "drift_correction (only jumps > 0.3 m or 10 deg), agent_relocalize, unknown (POST /map frame). "
                    "loc.suspect / fresh_fit / suspect_since are ADVISORY and never stop anything: fresh_fit is the fit "
                    "of the voxels placed in the last {SUSPECT_FRESH_S} s at the current pose; suspect comes on when it "
                    "stays under {SUSPECT_FIT} for {SUSPECT_S} s while the dog walks {SUSPECT_MOVE_M} m, and clears at "
                    "{SUSPECT_CLEAR} or a placement. It can't tell a wrong pose from a changed room: on suspect take a "
                    "fix_ok marker or a relocalize search before a long go_to. Only in /state.json loc. The lost and "
                    "suspect timers restart after a gap > {LOST_GAP_S} s between judged views.",
    "localization_notice": "Agent replies (and GET /agent/status?client=) carry localization_notice when line-up "
                           "events happened since your previous call: {events, status, fit, runner_up, unsure, summary}. "
                           "A jump means poses you stored before it may be off.",
    "failure_signatures": [
        "no_route near furniture or right after start: map pose misaligned. Check fit; relocalize.",
        "go_to obstacle/stuck repeatedly in the same open aisle: lidar smear or a moved chair; look with photo, "
        "then go_to again (the block lasts {BLOCK_S} s) or a different place.",
        "track_fit under 0.65 while the dog is still: the view is mostly new things (people, moved chairs) or the "
        "pose is off; relocalize search before driving.",
        "stale_sensors with odom null in /state.json: the dog or the driver container is off.",
        "photo.still false: it never settled in 5 s (rocking, still turning); take another.",
        "turned_deg short of deg with result done: within the 5 degree tolerance after one correction.",
        "a marker in /markers with held: true is a sighting up to 0.5 s old, not a live one; use fix_ok items for "
        "positions (a single-frame sighting is unconfirmed).",
        "an expected marker missing: markers read reliably from the open room, not from under or next to dark "
        "furniture (auto-exposure blows out the bright room; patches brighter than ~230/255 are mostly missed). "
        "Back out into the open or turn so the camera isn't looking from dark into bright.",
    ],
    "http": "Base http://172.17.40.64:8080. POST bodies are JSON. POSTs only from localhost or 172.17.0.0/18 (403 "
            "otherwise). An unknown /agent/<call> is 404. Bad arguments to a tool (missing m, non-number, bad pose or "
            "mode) are 400 {result: error, reason: 'bad arguments: ...', stop_reason: bad_arguments}, and are not logged.",
}


# ---------- assembling ----------

def fill(obj, consts):
    """Put the code's constant values into "{NAME}" in descriptions; a string that is only "{NAME}" becomes the value."""
    if isinstance(obj, str):
        names = re.findall(r"\{([A-Z][A-Z0-9_]+)\}", obj)
        unknown = [n for n in names if n not in consts]
        if unknown:
            raise SystemExit(f"description names constants the code doesn't have: {unknown} in {obj!r}")
        if len(names) == 1 and obj == "{" + names[0] + "}":
            return consts[names[0]]
        return re.sub(r"\{([A-Z][A-Z0-9_]+)\}", lambda m: v if isinstance(v := consts[m.group(1)], str) else
                      json.dumps(v), obj)
    if isinstance(obj, list):
        return [fill(v, consts) for v in obj]
    if isinstance(obj, dict):
        return {k: fill(v, consts) for k, v in obj.items()}
    return obj


def main():
    consts, by_mod = {}, {}
    for m in MODULES:
        c = constants(SRC / f"{m}.py")
        by_mod[m] = c
        for k, v in c.items():
            consts.setdefault(k, v)
    consts["KNOWN"] = {str(k): v for k, v in by_mod["go2_markers"]["KNOWN"].items()}
    consts["SIZE_M"] = by_mod["go2_markers"]["SIZE_M"]
    consts["HEAD_MAX_DEG"] = round(math.degrees(by_mod["go2_dashboard"]["HEAD_MAX"]), 1)
    consts["MOVE_CLAMP"] = [-consts["MAX_BACK_M"], consts["MAX_MOVE_M"]]
    consts["TURN_CLAMP"] = [-consts["MAX_TURN_DEG"], consts["MAX_TURN_DEG"]]
    consts["LOOK_CLAMP"] = [-consts["HEAD_MAX_DEG"], consts["HEAD_MAX_DEG"]]
    code = routes(SRC / "go2_dashboard.py")
    described = {(e["method"], e["path"]) for e in ENDPOINTS}
    missing, extra = code - described, described - code
    if missing or extra:
        raise SystemExit(f"routes in the code but not described: {sorted(missing)}\n"
                         f"described but not in the code: {sorted(extra)}")
    for e in ENDPOINTS:
        for k, v in COMMON_TOOL_RETURNS.items():
            if e.get("tool"):
                e.setdefault("fields", {}).setdefault(k.rstrip("?"), v)
        if e.get("tool"):
            e["returns"] = {k: TOOL_TYPES.get(k, v) for k, v in e["returns"].items()}
    keep = sorted({n for n in re.findall(r"\{([A-Z][A-Z0-9_]+)\}", json.dumps([ENDPOINTS, STOP_REASONS, NOTES]))}
                  | {"AGENT_CALLS", "SPEEDS", "LIMITS", "BACK_MAX", "TURN_OVERSHOOT", "WAYPOINT_TOL_M", "LIVE_R",
                     "OVERHEAD_MAX", "TRACK_MIN_FIT", "ALIGN_OK", "LEG_MAX_M", "CLEAR_PREF", "HFOV_DEG", "PERIOD_S"})
    spec = {"generated_by": "navigation/tools/make_api_spec.py", "source": str(SRC),
            "base_url": "http://172.17.40.64:8080",
            "constants": {k: consts[k] for k in keep if k in consts},
            "endpoints": sorted(fill(ENDPOINTS, consts), key=lambda e: (not e["for_agents"], e["path"], e["method"])),
            "stop_reasons": fill(STOP_REASONS, consts), "notes": fill(NOTES, consts)}
    out = NAV / "api_spec.json"
    out.write_text(json.dumps(spec, indent=1, default=list) + "\n")
    print(f"wrote {out}: {len(spec['endpoints'])} endpoints ({sum(e['for_agents'] for e in spec['endpoints'])} for agents), "
          f"{len(spec['constants'])} constants")


if __name__ == "__main__":
    main()
