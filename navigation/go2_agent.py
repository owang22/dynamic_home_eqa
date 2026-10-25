"""Blocking movement tools for AI agents, served by go2_dashboard.py under /agent/*.

Agents claim the dog, then call one tool at a time; each call returns when the motion has
finished, was blocked, timed out or was aborted. A person at the console always wins:
driving from the console or pressing Take over aborts the agent's tool and ends its claim.
Every photo an agent takes is kept so the console can show what the agent saw.
"""
import base64
import json
import math
import os
import re
import threading
import time
from collections import deque

import cv2
import numpy as np

AGENT_LEASE_S = 60.0       # an agent's claim lapses after this long with no call
HUMAN_HOLD_S = 300.0       # a takeover lasts until Hand back, or this long with no console command
BACK_SPEED = 0.2                           # m/s backwards: the lidar barely sees behind the dog
MAX_BACK_M = 1.0                           # per move call
MOVE_SPEED, MIN_SPEED = 0.5, 0.25           # m/s; below ~0.3 the Go2 shuffles and drags its feet (10-22)
TURN_SPEED = 0.6                           # rad/s; the legs barely step below this (tested by cheetah, board #8)
# The right-front foot drags on pure spins and the feet don't re-plant when a turn stops (Oliver, 10-23):
TURN_ROCK_V, TURN_ROCK_S = 0.12, 0.6       # while turning in place, rock forward/back this fast (m/s), switching every this many s
REPLANT_V, REPLANT_S = 0.25, 0.5           # re-plant the feet: a short step forward at this speed for this long, then back
SHUFFLES = 1                               # stalls to shuffle out of (re-plant and retry) before giving up
TURN_OVERSHOOT = math.radians(6)           # the dog keeps turning about this much after stop
MAX_MOVE_M, MAX_TURN_DEG = 3.0, 360.0      # per call
FRONT_CLEAR = (0.35, 0.90, 0.25)           # obstacle box ahead of base_link: x from, x to, half width (m)
REAR_CLEAR = (0.30, 0.75, 0.22)            # and behind it, when backing up
BUMP_H = (0.18, 0.60)                      # heights above the floor the dog can bump into (m). The lidar
                                           # reports the floor itself in ~10 cm steps, and the dog fits under
                                           # desk and table tops, so neither counts.
LIVE_KEEP, LIVE_MIN_SEEN = 3, 2              # go_to: a live obstacle cell counts if seen in this many of the last clouds
OVERHEAD_MAX = 0.6                         # m: tops between BUMP_H[1] and this would block the route. Equal to
                                           # BUMP_H[1], so desk and table tops (~0.7 m) do NOT block: 1.0 closed every
                                           # route to B on 10-23 and was reverted. Open: routes can pass under desks
LIVE_R = 3.0                               # go_to: within this of the dog, plan on what the lidar sees now
STALL_S, STALL_M = 2.0, 0.03               # blocked if moved less than this in this long
TILT_LIMIT = 0.6                           # rad of roll/pitch that counts as fallen
MIN_BODY_H = 0.18                          # m; lower means lying down
STALE_S = 1.0                              # sensors older than this: refuse to move
GO_TO_STOP_WHEN_LOST = True                # go_to stops when the map says the dog is lost (loc.lost)
STAND_H = 0.24                             # m; posture stand is done once the body is at least this high (untested)
POSTURE_S = 8.0                            # posture: give up waiting for the body height after this long
RELOC_R = (0.5, 10.0)                      # relocalize search radius limits (m)
STILL_S = 1.0                              # photos are taken after standing still this long
GOAL_TOL_M = 0.20                          # go_to: close enough to the goal
WAYPOINT_TOL_M = 0.15                      # go_to: move on to the next leg this close to a corner
LOOKAHEAD_M = 0.5                          # go_to: steer toward the point this far ahead on the leg
STEER_GAIN, STEER_MAX = 1.5, 0.8           # go_to: turn rate (rad/s) per rad of heading error, and its cap
TURN_IN_PLACE = math.radians(45)           # go_to: heading error above this: stop and turn in place
MAX_REPLANS = 3                            # go_to: plan around new obstacles this many times
TRAIL_S, TRAIL_JUMP_M = 300.0, 0.3           # go_to: remember where the dog walked this long; forget it after a line-up jump
SQUEEZE_STOP_M = 1.0                       # go_to on a squeeze route: stop this far before the narrow part, look, re-plan
MAPS_DIR = "/maps"
MAP_NAME = os.environ.get("MAP_NAME", "lab")
HOST_UID = 1000


def cut_path(path, upto_m):
    """The first upto_m metres of a polyline [[x, y], ...] (just its start if upto_m < 0.3)."""
    if upto_m < 0.3:
        return path[:1]
    out, left = [path[0]], upto_m
    for a, b in zip(path, path[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        if seg >= left:
            f = left / seg
            out.append([round(a[0] + (b[0] - a[0]) * f, 2), round(a[1] + (b[1] - a[1]) * f, 2)])
            return out
        out.append(b)
        left -= seg
    return out


def stop_reason(call, out):
    """Why a tool call ended, as one word an agent can branch on (cheetah, 10-25): arrived (move, turn, go_to
    finished), done (other tools), obstacle, stuck (no progress), no_route, timeout, stop (STOP or the agent's
    stop), person (a person took over), lost, not_standing, fallen, stale_sensors, refused, busy, error.
    The console adds bad_arguments (HTTP 400) and refused (409: a person or another agent has control)."""
    res, why = out.get("result"), str(out.get("reason") or "")
    if res == "done":
        return "arrived" if call in ("move", "turn", "go_to") else "done"
    if res == "blocked":
        return "obstacle" if "obstacle" in why or "something not on the map" in why else "stuck"
    if res in ("no_route", "timeout", "refused"):
        return res
    if res == "aborted":
        return "person" if "took over" in why or "person" in why else "stop"
    for k in ("lost", "not_standing", "fallen", "stale_sensors", "busy"):
        if why.startswith(k):
            return k
    return "error"


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


class Aborted(Exception):
    pass


class Agents:
    def __init__(self, node, latest, lock, full):
        self.node, self.latest, self.lock, self.full = node, latest, lock, full
        self.owner = None              # {"kind": "agent"|"human", "client", "ip", "t"}
        self.busy = threading.Lock()   # one tool at a time
        self.abort = threading.Event()
        self.abort_reason = ""
        self.current = None            # {"client", "call", "args", "t"}
        self.notes = {}                # client -> latest free-text note ("what I'm doing")
        self.log = deque(maxlen=40)
        self.photos = deque(maxlen=60)  # {"id", "jpeg", "meta"}
        self.photo_n = 0
        self.last_motion = 0.0
        self.places_lock = threading.Lock()
        self.mapper = None             # set by the console: map frame (go2_mapper.py)
        self.planner = None            # and route planning (go2_nav.py)
        self.live_hist = deque(maxlen=LIVE_KEEP)   # recent lidar clouds in map frame, for the planner
        self._live_cloud = None
        self._live_lock = threading.Lock()
        self._trail = deque()          # (t, x, y) map poses the dog walked, for the planner's set_trail
        self._trail_T = None
        self._stop_if_lost = False     # set while a go_to runs (GO_TO_STOP_WHEN_LOST)

    # ---------- ownership ----------
    def owner_now(self):
        o, now = self.owner, time.monotonic()
        if o and now - o["t"] > (AGENT_LEASE_S if o["kind"] == "agent" else HUMAN_HOLD_S):
            self.owner = o = None
        return o

    def agent_may_drive(self, client, ip):
        """Claim or refresh for an agent. Returns None if OK, else the reason it may not."""
        o = self.owner_now()
        if o and o["kind"] == "human":
            return f"A person at {o['ip']} has taken over"
        if o and o["client"] != client:
            return f"Agent {o['client']} has control"
        self.owner = {"kind": "agent", "client": client, "ip": ip, "t": time.monotonic()}
        return None

    def human_drives(self, client, ip):
        """Console activity: a person always wins over an agent."""
        o = self.owner_now()
        if o and o["kind"] == "agent":
            self.interrupt(f"a person at {ip} took over")
        self.owner = {"kind": "human", "client": client, "ip": ip, "t": time.monotonic()}

    def hand_back(self):
        if self.owner and self.owner["kind"] == "human":
            self.owner = None

    def release(self, client):
        if self.owner and self.owner["kind"] == "agent" and self.owner["client"] == client:
            self.owner = None
            return True
        return False

    def interrupt(self, reason):
        if self.current:
            self.abort_reason = reason
            self.abort.set()
        self.node.moving = False
        self.node.stop()

    def status(self):
        o = self.owner_now()
        cur = self.current
        return {"owner": dict(o, idle_s=round(time.monotonic() - o["t"], 1)) if o else None,
                "current": dict(cur, secs=round(time.time() - cur["t"], 1)) if cur else None,
                "notes": self.notes, "log": list(self.log)[-40:],
                "photos": [p["meta"] for p in list(self.photos)[-8:]]}

    # ---------- sensor helpers ----------
    def snap(self):
        with self.lock:
            now = time.time()
            ages = {k: now - t for k, t in self.latest["stamps"].items()}
            return (self.latest["odom"], self.latest["imu"], self.latest["state"], self.latest["cloud"],
                    self.latest["map_pose"], ages)

    def check_safe(self):
        odom, imu, state, _, _, ages = self.snap()
        if odom is None or ages.get("odom", 99) > STALE_S or ages.get("imu", 99) > STALE_S:
            return "stale_sensors"
        if abs(imu["rpy"][0]) > TILT_LIMIT or abs(imu["rpy"][1]) > TILT_LIMIT:
            return "fallen"
        if state and state["body_height"] < MIN_BODY_H:
            return "not_standing: the dog is lying down; call posture {\"pose\": \"stand\"} first"
        return None

    def obstacle(self, direction, force=False):
        """Nearest obstacle distance in a box ahead (direction=+1) or behind (-1), from the lidar grid.
        Ahead: None while the dog's own obstacle avoidance is on (it slows and stops the dog itself, and
        a stall then counts as blocked). Behind: always checked, also against the saved map, because
        the dog's avoidance is poor when backing up."""
        if direction < 0:
            hit = self._map_behind()
            if hit is not None:
                return hit
        elif self.node.avoid and not force:
            return None
        odom, _, _, cloud, _, ages = self.snap()
        if not cloud or not cloud["obs"] or ages.get("cloud", 99) > 3.0 or cloud["frame"] == "base_link":
            return None
        pts = np.asarray(cloud["obs"], dtype=np.float64)
        dx, dy = pts[:, 0] - odom["pos"][0], pts[:, 1] - odom["pos"][1]
        c, s = math.cos(odom["yaw"]), math.sin(odom["yaw"])
        fx, fy = (c * dx + s * dy) * direction, -s * dx + c * dy
        x0, x1, half = FRONT_CLEAR if direction > 0 else REAR_CLEAR
        hit = (fx > x0) & (fx < x1) & (np.abs(fy) < half) & (pts[:, 2] > BUMP_H[0]) & (pts[:, 2] < BUMP_H[1])
        return float(fx[hit].min()) if hit.any() else None

    def _map_behind(self):
        """Distance to the nearest saved-map obstacle in the box behind the dog, or None."""
        mp = self.map_pose_now()
        if mp is None or self.planner is None:
            return None
        x0, x1, half = REAR_CLEAR
        back = mp["yaw"] + math.pi
        best = None
        for off in (-half, 0.0, half):
            sx = mp["x"] + math.cos(back + math.pi / 2) * off
            sy = mp["y"] + math.sin(back + math.pi / 2) * off
            hit = self.planner.raycast(sx, sy, back, max_m=x1, min_m=x0)
            if hit:
                d = math.hypot(hit[0] - sx, hit[1] - sy)
                best = d if best is None else min(best, d)
        return best

    def pose_out(self):
        odom, _, _, _, mp, _ = self.snap()
        return {"odom": {"x": odom["pos"][0], "y": odom["pos"][1], "yaw": odom["yaw"]} if odom else None,
                "map_pose": mp}

    def tick(self, deadline):
        if self.abort.is_set():
            raise Aborted(self.abort_reason or "stopped")
        if time.monotonic() > deadline:
            raise TimeoutError
        bad = self.check_safe()
        if bad:
            raise RuntimeError(bad)
        if self._stop_if_lost and self.mapper is not None and self.mapper.lost_since is not None:
            raise RuntimeError(f"lost: the map fit has been low since {time.strftime('%H:%M:%S', time.localtime(self.mapper.lost_since))}"
                               "; the map pose is probably wrong. Use relocalize before driving on")

    # ---------- tool runner ----------
    def run(self, client, call, args, fn, stop=True):
        if not self.busy.acquire(blocking=False):
            return 409, {"result": "error", "reason": "busy: another tool is running", "stop_reason": "busy"}
        self.abort.clear()
        self.abort_reason = ""
        t0 = time.time()
        self.current = {"client": client, "call": call, "args": args, "t": t0}
        if args.get("note"):
            self.notes[client] = {"text": str(args["note"])[:2000], "t": time.time()}
        try:
            out = fn()
        except Aborted as e:
            out = {"result": "aborted", "reason": str(e)}
        except TimeoutError:
            out = {"result": "timeout", "reason": "timeout_s reached"}
        except RuntimeError as e:
            out = {"result": "error", "reason": str(e)}
        finally:
            self.node.moving = False
            if stop:             # not after a posture change: StopMove could undo lying down
                self.node.stop()
            self.current = None
            self.busy.release()
            if self.owner and self.owner["kind"] == "agent" and self.owner["client"] == client:
                self.owner["t"] = time.monotonic()
        out.update(self.pose_out(), t=round(time.time(), 2))
        out.setdefault("stop_reason", stop_reason(call, out))
        if self.mapper is not None:
            li = self.mapper.loc_info(track_n=0)
            out.setdefault("fit", li.get("track_fit"))
            out.setdefault("lost", li.get("lost"))
            out.setdefault("suspect", li.get("suspect"))
        # everything but bulky fields, so the console can show the whole call when a row is opened
        brief = {k: v for k, v in out.items() if k not in ("photo", "photos", "t", "odom", "image", "jpeg_b64", "map_png")
                 and len(json.dumps(v, default=str)) < 2000}
        shot = out.get("photos") or ([out["photo"]] if isinstance(out.get("photo"), dict) else [])
        if shot:
            brief["photos"] = [p["id"] for p in shot]
            ids = set(brief["photos"])
            for p in self.photos:      # keep the agent's note with its photos
                if p["meta"]["id"] in ids and args.get("note"):
                    p["meta"]["note"] = str(args["note"])[:2000]
        self.log.append({"t": round(time.time(), 2), "client": client, "call": call,
                         "dur_s": round(time.time() - t0, 1),
                         "note": str(args.get("note") or "")[:2000],
                         "args": {k: v for k, v in args.items() if k not in ("client", "note")}, **brief})
        return 200, out

    # ---------- motions ----------
    def _move(self, m, timeout_s):
        m = max(-MAX_BACK_M, min(MAX_MOVE_M, float(m)))
        sign = 1 if m >= 0 else -1
        deadline = time.monotonic() + timeout_s
        odom0 = self.snap()[0]
        if odom0 is None:
            raise RuntimeError("stale_sensors")
        x0, y0, yaw0 = odom0["pos"][0], odom0["pos"][1], odom0["yaw"]
        hist, done = deque(), 0.0
        shuffles, t_start = SHUFFLES, time.monotonic()
        while True:
            self.tick(deadline)
            odom = self.snap()[0]
            done = ((odom["pos"][0] - x0) * math.cos(yaw0) + (odom["pos"][1] - y0) * math.sin(yaw0)) * sign
            left = abs(m) - done
            if left <= 0.03:
                return {"result": "done", "moved_m": round(done * sign, 3)}
            ob = self.obstacle(sign)
            if ob is not None:
                return {"result": "blocked", "side": "front" if sign > 0 else "back",
                        "reason": f"obstacle {ob:.2f} m from the robot centre", "moved_m": round(done * sign, 3)}
            now = time.monotonic()
            hist.append((now, done))
            while hist and now - hist[0][0] > STALL_S:
                hist.popleft()
            if now - t_start > STALL_S + 0.5 and hist and done - hist[0][1] < STALL_M:
                if shuffles > 0:              # a foot may be stuck: re-plant and try again
                    shuffles -= 1
                    self.node.moving = False
                    self.node.stop()
                    self._replant()
                    hist.clear()
                    t_start = time.monotonic()
                    continue
                return {"result": "blocked", "side": "front" if sign > 0 else "back",
                        "reason": "not making progress (avoidance stopped it, or something is in the way)",
                        "moved_m": round(done * sign, 3)}
            v = max(MIN_SPEED, min(MOVE_SPEED, left * 1.2)) * sign if sign > 0 else -BACK_SPEED
            self.node.move(v, 0.0, 0.0)
            self.last_motion = time.monotonic()
            time.sleep(0.1)

    def _turn(self, deg, timeout_s, replant=True):
        """Turn at full rate, stop early for the overshoot, settle, then correct once if off by > 5 degrees.
        A stall gets one shuffle (re-plant) and a retry; at the end the feet are re-planted."""
        deg = max(-MAX_TURN_DEG, min(MAX_TURN_DEG, float(deg)))
        deadline = time.monotonic() + timeout_s
        total = 0.0
        want = math.radians(deg)
        shuffles = SHUFFLES
        attempt = 0
        while attempt < 2:
            err = want - total
            if attempt and abs(err) <= math.radians(5):
                break
            r = self._turn_once(err, deadline)
            self.node.moving = False
            self.node.stop()
            self._settle(0.8)
            total += r["turned"] + wrap(self.snap()[0]["yaw"] - r["yaw"])   # includes the overshoot
            if r["result"] == "blocked" and shuffles > 0:
                shuffles -= 1
                self._replant()
                continue
            if r["result"] != "done":
                return {"result": r["result"], "side": "turn", "reason": r["reason"],
                        "turned_deg": round(math.degrees(total), 1)}
            attempt += 1
        if replant:
            self._replant()
        return {"result": "done", "turned_deg": round(math.degrees(total), 1)}

    def _replant(self):
        """A short step forward and back so the feet lift and land squarely again (after a turn, or to get
        unstuck). Skipped if either way is blocked. Returns True if it stepped."""
        if REPLANT_S <= 0 or self.obstacle(1) is not None or self.obstacle(-1) is not None:
            return False
        back_v = min(REPLANT_V, BACK_SPEED)
        o = self.snap()[0]
        x0, y0, c, s = o["pos"][0], o["pos"][1], math.cos(o["yaw"]), math.sin(o["yaw"])

        def along():                  # how far ahead of the start the dog is now (m, odom)
            p = self.snap()[0]["pos"]
            return (p[0] - x0) * c + (p[1] - y0) * s

        def drive(v, until, secs):
            end = time.monotonic() + secs
            while time.monotonic() < end and not until():
                if self.abort.is_set():
                    raise Aborted(self.abort_reason or "stopped")
                self.node.move(v, 0.0, 0.0)
                self.last_motion = time.monotonic()
                time.sleep(0.1)
            self.node.moving = False
            self.node.stop()
            self._settle(0.25)
        # forward for a fixed time, then back until the dog is where it started (closed loop on odom,
        # so the two halves cancel: open loop left the dog up to 20 cm back after a 360, 10-23)
        drive(REPLANT_V, lambda: False, REPLANT_S)
        drive(-back_v, lambda: along() <= 0.01, 3 * REPLANT_S * REPLANT_V / back_v)
        return True

    def _settle(self, secs):
        end = time.monotonic() + secs
        while time.monotonic() < end:
            if self.abort.is_set():
                raise Aborted(self.abort_reason or "stopped")
            time.sleep(0.05)

    def _turn_once(self, rad, deadline):
        """One turn of `rad` (signed) at full rate. Returns how far it turned (signed) and the yaw when it stopped."""
        target, sign = abs(rad), 1 if rad >= 0 else -1
        early = min(TURN_OVERSHOOT, target * 0.4)
        start = time.monotonic()
        prev = self.snap()[0]["yaw"]
        turned, hist = 0.0, deque()
        while target - turned > early:
            self.tick(deadline)
            yaw = self.snap()[0]["yaw"]
            turned += wrap(yaw - prev) * sign
            prev = yaw
            now = time.monotonic()
            hist.append((now, turned))
            while hist and now - hist[0][0] > STALL_S:
                hist.popleft()
            if now - start > STALL_S + 0.5 and hist and turned - hist[0][1] < math.radians(3):
                return {"result": "blocked", "reason": "not turning", "turned": turned * sign, "yaw": yaw}
            # rock forward/back a little while turning so every foot keeps stepping (no dragged pivot foot)
            rock = TURN_ROCK_V if int((now - start) / TURN_ROCK_S) % 2 == 0 else -min(TURN_ROCK_V, BACK_SPEED)
            self.node.move(rock if TURN_ROCK_S > 0 else 0.0, 0.0, TURN_SPEED * sign)
            self.last_motion = time.monotonic()
            time.sleep(0.1)
        return {"result": "done", "turned": turned * sign, "yaw": prev}

    def _photo(self, client, timeout_s=5.0):
        """Wait until the dog has stood still ~1 s, then keep one full-size frame."""
        self.node.moving = False
        self.node.stop()
        deadline = time.monotonic() + timeout_s
        still_since = None
        while True:
            if self.abort.is_set():
                raise Aborted(self.abort_reason or "stopped")
            odom = self.snap()[0]
            moving = odom is None or abs(odom["vel"][0]) > 0.03 or abs(odom["vel"][1]) > 0.03 or abs(odom["vel"][2]) > 0.05
            now = time.monotonic()
            still_since = None if moving else (still_since or now)
            if still_since and now - still_since >= STILL_S and now - self.last_motion >= STILL_S:
                break
            if now > deadline:
                break     # take it anyway and say so
            time.sleep(0.05)
        with self.lock:
            img, ft = self.full["img"], self.full["t"]
        if img is None or time.time() - ft > 2.0:
            raise RuntimeError("no_camera_frame")
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        self.photo_n += 1
        pid = f"p{int(time.time())}_{self.photo_n}"
        meta = {"id": pid, "url": f"/agent/photos/{pid}.jpg", "client": client, "t": round(ft, 2),
                "width": int(img.shape[1]), "height": int(img.shape[0]),
                "still": bool(still_since and time.monotonic() - still_since >= STILL_S),
                "look_deg": round(math.degrees(self.node.head)), **self.pose_out()}
        self.photos.append({"id": pid, "jpeg": buf.tobytes(), "meta": meta})
        return meta

    def photo_bytes(self, pid):
        for p in self.photos:
            if p["id"] == pid:
                return p["jpeg"]
        return None

    # ---------- tools (called by the HTTP handler) ----------
    def tool(self, call, client, args):
        timeout_s = float(args.get("timeout_s", 30))
        inline = bool(args.get("inline"))

        def with_b64(meta):
            if inline:
                meta = dict(meta, jpeg_b64=base64.b64encode(self.photo_bytes(meta["id"])).decode())
            return meta

        if call == "move":
            return self.run(client, call, args, lambda: self._move(args["m"], timeout_s))
        if call == "turn":
            return self.run(client, call, args, lambda: self._turn(args["deg"], timeout_s))
        if call == "photo":
            return self.run(client, call, args, lambda: {"result": "done", "photo": with_b64(self._photo(client))})
        if call == "look_around":
            n = max(1, min(12, int(args.get("n", 4))))

            def look():
                shots, deadline = [], time.monotonic() + timeout_s
                for i in range(n):
                    shots.append(with_b64(self._photo(client)))
                    if n > 1:
                        r = self._turn(360.0 / n, max(1.0, deadline - time.monotonic()))
                        if r["result"] != "done":
                            return {"result": r["result"], "reason": r.get("reason"), "photos": shots}
                return {"result": "done", "photos": shots}
            return self.run(client, call, args, look)
        if call == "go_to":
            def go_to():
                self._stop_if_lost = GO_TO_STOP_WHEN_LOST      # only while this go_to runs (run() holds the tool lock)
                try:
                    return self._go_to(args, timeout_s)
                finally:
                    self._stop_if_lost = False
            return self.run(client, call, args, go_to)
        if call == "look":
            return self.run(client, call, args, lambda: self._look(float(args["deg"])))
        if call == "posture":
            return self.run(client, call, args, lambda: self._posture(args), stop=False)
        if call == "relocalize":
            return self.run(client, call, args, lambda: self._relocalize(client, args))
        raise KeyError(call)

    def _posture(self, args):
        """Lie down or stand up, as the console's buttons do; waits until the body height shows it."""
        pose = str(args.get("pose", ""))
        if pose not in ("stand", "lie") or "body_height" in args:
            raise ValueError("pose must be stand or lie (crouch and body_height are not supported yet)")
        odom, imu, state, _, _, ages = self.snap()
        if (odom is None or state is None or ages.get("imu", 99) > STALE_S or ages.get("state", 99) > STALE_S):
            raise RuntimeError("stale_sensors")
        if abs(imu["rpy"][0]) > TILT_LIMIT or abs(imu["rpy"][1]) > TILT_LIMIT:
            raise RuntimeError("fallen: a person must right the dog")
        self.node.action(pose)
        end = time.monotonic() + POSTURE_S
        while True:
            self._settle(0.1)
            _, _, state, _, _, ages = self.snap()
            h = state["body_height"] if state and ages.get("state", 99) < STALE_S else None
            if h is not None and (h >= STAND_H if pose == "stand" else h < MIN_BODY_H):
                if pose == "stand":
                    self._settle(0.5)     # let the balance stand settle before the next move
                return {"result": "done", "pose": pose, "body_height": round(h, 3)}
            if time.monotonic() > end:
                return {"result": "error", "pose": pose, "body_height": h,
                        "reason": f"the body height did not show {pose} within {POSTURE_S:.0f} s"}

    def _relocalize(self, client, args):
        """search / global: where the dog could be on the map (not applied). set: put it at x, y, yaw."""
        m = self.mapper
        if m is None:
            raise RuntimeError("no map")
        odom = self.snap()[0]
        mode = str(args.get("mode", "search"))
        cur = m.pose(odom)
        cur_fit = m.view_fit(m.T) if m.T is not None else None
        here = {"pose": cur, "fit": cur_fit, "lost": m.lost_since is not None, "lost_since": m.lost_since}
        if mode in ("search", "global"):
            centre = radius = None
            if mode == "search":
                if "x" in args and "y" in args:
                    centre = (float(args["x"]), float(args["y"]))
                elif cur:
                    centre = (cur["x"], cur["y"])
                else:
                    return {"result": "error", "reason": "no current map pose to search around; send x, y or mode global"}
                radius = max(RELOC_R[0], min(RELOC_R[1], float(args.get("radius_m", 3.0))))
            top = max(1, min(10, int(args.get("top", 5))))
            cands, err = m.candidates(odom, centre, radius, top)
            if err:
                return {"result": "error", "reason": err, "current": here}
            return {"result": "done", "mode": mode, "candidates": cands, "current": here,
                    "searched": None if centre is None else {"x": centre[0], "y": centre[1], "radius_m": radius}}
        if mode == "set":
            yaw = math.radians(float(args["yaw_deg"])) if "yaw_deg" in args else float(args["yaw"])
            info, err = m.set_pose(odom, float(args["x"]), float(args["y"]), yaw, by=client,
                                   force=bool(args.get("force")))
            if err:
                return {"result": "refused", "reason": err, **info, "current": here}
            return {"result": "done", **info, "pose": m.pose(odom)}
        raise ValueError("mode must be search, global or set")

    def _look(self, deg):
        """Tilt the camera up (+) or down (-) by pitching the body while standing; 0 levels it.
        Moving levels it again by itself."""
        self.node.look(math.radians(deg))
        time.sleep(1.5)
        self.tick(time.monotonic() + 1)
        imu = self.snap()[1]
        return {"result": "done", "look_deg": round(math.degrees(self.node.head)),
                "body_pitch_deg": round(math.degrees(imu["rpy"][1]), 1) if imu else None}

    def map_pose_now(self):
        """Robot pose on the map from the latest odometry (faster than the 5 Hz map_pose)."""
        odom = self.snap()[0]
        if odom is None or self.mapper is None or self.mapper.T is None:
            return None
        x, y, yaw = self.mapper.to_map(odom["pos"][0], odom["pos"][1], odom["yaw"])
        self._note_trail(odom, x, y)
        return {"x": x, "y": y, "yaw": yaw}

    def _note_trail(self, odom, x, y):
        """Where the dog walked (map frame), for the planner's squeeze-out-the-way-you-came (set_trail).
        A line-up that moves the dog more than TRAIL_JUMP_M makes the old trail meaningless: start over."""
        T, now = tuple(self.mapper.T), time.time()
        trail = self._trail
        if trail and now - trail[-1][0] < 0.2:
            return
        old = self._trail_T
        if old is not None and old != T:
            c, s_ = math.cos(old[2]), math.sin(old[2])
            o = odom["pos"]
            if math.hypot(old[0] + c * o[0] - s_ * o[1] - x, old[1] + s_ * o[0] + c * o[1] - y) > TRAIL_JUMP_M:
                trail.clear()
        self._trail_T = T
        trail.append((now, x, y))
        while trail and now - trail[0][0] > TRAIL_S:
            trail.popleft()

    def update_live(self):
        """Give the planner what the lidar sees right now around the dog: it overrides the saved map
        there (things moved, or the map was wrong). The saved map itself isn't changed. Called for
        each new cloud (note_cloud) and before planning."""
        odom, _, _, cloud, _, ages = self.snap()
        if (cloud is None or odom is None or cloud.get("frame") == "base_link" or ages.get("cloud", 99) > 3.0
                or self.mapper is None or self.mapper.T is None or self.planner is None):
            return
        with self._live_lock:
            self._update_live(cloud, odom)

    def _update_live(self, cloud, odom):
        if cloud is not self._live_cloud:
            self._live_cloud = cloud
            obs, free, over = [], [], []
            # each cell of the cloud holds its highest point: bump height is an obstacle, floor height
            # is open floor. A desk or table top (up to OVERHEAD_MAX) blocks the route too: the dog would
            # fit under a desk, but must not go there (Oliver, 10-23: a go_to took a "shortcut" under one).
            # The saved map only has 0.2-0.6 m, so this comes from the live lidar.
            for x, y, h in cloud["obs"]:
                if BUMP_H[0] < h < BUMP_H[1]:
                    obs.append(self.mapper.to_map(x, y)[:2])
                elif h <= BUMP_H[0]:
                    free.append(self.mapper.to_map(x, y)[:2])
                elif h < OVERHEAD_MAX:
                    over.append(self.mapper.to_map(x, y)[:2])
            free += [self.mapper.to_map(x, y)[:2] for x, y in cloud["flat"]]
            self.live_hist.append((obs, free, over))
        # an obstacle cell counts once it shows up in a few clouds in a row (cuts flicker)
        need = min(LIVE_MIN_SEEN, len(self.live_hist))

        def steady(i):
            seen = {}
            for h in self.live_hist:
                for k in {(round(x, 1), round(y, 1)) for x, y in h[i]}:
                    seen[k] = seen.get(k, 0) + 1
            return [k for k, n in seen.items() if n >= need]
        free_now = self.live_hist[-1][1]
        mp = self.mapper.to_map(odom["pos"][0], odom["pos"][1])
        self.planner.set_live(steady(0), free_now, mp[0], mp[1], LIVE_R, over=steady(2))

    def _goal(self, args):
        """(x, y, yaw or None, place or None) for a go_to: a saved place, or x/y[/yaw_deg] on the map."""
        if "place" in args:
            p = self.places().get(str(args["place"]))
            if not p:
                raise RuntimeError(f"unknown place {args['place']}")
            yaw = math.radians(p["yaw_deg"])
            t = p.get("target")
            if t:      # face the thing itself
                yaw = math.atan2(t["y"] - p["y"], t["x"] - p["x"])
            return p["x"], p["y"], yaw, p
        yaw = math.radians(float(args["yaw_deg"])) if args.get("yaw_deg") is not None else None
        return float(args["x"]), float(args["y"]), yaw, None

    def _go_to(self, args, timeout_s):
        """Drive to a place or map point along a planned route, around furniture; re-plan around
        obstacles that aren't on the map; finally face the place's target (or yaw_deg)."""
        gx, gy, gyaw, place = self._goal(args)
        if self.planner is None:
            raise RuntimeError("no planner")
        deadline = time.monotonic() + timeout_s
        moved, replans, first_plan, squeezes = 0.0, 0, None, 0
        while True:
            mp = self.map_pose_now()
            if mp is None:
                raise RuntimeError("no_map_pose: the console is not lined up with the map")
            if math.hypot(gx - mp["x"], gy - mp["y"]) < GOAL_TOL_M:
                break
            self.update_live()
            self.planner.set_trail([(x, y) for _, x, y in self._trail])
            plan = self.planner.plan(mp["x"], mp["y"], gx, gy)
            if "error" in plan:
                why = {"why": plan["why"]} if plan.get("why") else {}
                if replans:
                    return {"result": "blocked", "moved_m": round(moved, 2), "replans": replans,
                            "reason": "something not on the map blocks the way, and there is no other route", **why}
                return {"result": "no_route", "reason": plan["error"], "moved_m": round(moved, 2), "replans": replans, **why}
            first_plan = first_plan or plan
            gx, gy = plan["goal"]          # may have moved off furniture onto open floor
            path = plan["path"]
            if plan.get("squeeze_along_m") is not None:
                # the map shows a gap narrower than the dog's clearance: drive up to it, then re-plan with the
                # live lidar looking at it (it is usually smear). If it really is too narrow, the next plan fails.
                path = cut_path(path, plan["squeeze_along_m"] - SQUEEZE_STOP_M)
                squeezes += 1
                if len(path) < 2 or squeezes > 8:
                    return {"result": "no_route", "moved_m": round(moved, 2), "replans": replans,
                            "reason": f"the way looks too narrow near {plan['squeeze_at']} even up close"}
            r = self._follow(path[1:], deadline)
            moved += r.pop("moved_m", 0.0)
            if r["result"] == "done":
                continue
            if r["result"] == "blocked" and r.get("at") and replans < MAX_REPLANS:
                replans += 1
                self.planner.block(*r["at"], r=0.15)
                self._settle(0.5)
                continue
            return dict(r, moved_m=round(moved, 2), replans=replans)
        if gyaw is not None:
            mp = self.map_pose_now()
            d = math.degrees(wrap(gyaw - mp["yaw"]))
            if abs(d) > 5:
                r = self._turn(d, max(1.0, deadline - time.monotonic()))
                if r["result"] != "done":
                    return dict(r, moved_m=round(moved, 2), replans=replans)
        out = {"result": "done", "moved_m": round(moved, 2), "replans": replans,
               "route_m": first_plan["length_m"] if first_plan else 0.0}
        if place and place.get("target"):
            out["target"] = place["target"]
        return out

    def _follow(self, path, deadline):
        """Drive the legs of a planned route. Returns result, moved_m and, when blocked, `at`: the
        map spot of the obstacle."""
        moved = 0.0
        prev = self.map_pose_now()
        ax, ay = prev["x"], prev["y"]          # start of the current leg
        shuffles = SHUFFLES
        for i, (wx, wy) in enumerate(path):
            last = i == len(path) - 1
            tol = GOAL_TOL_M * 0.6 if last else WAYPOINT_TOL_M
            hist = deque()
            lx, ly = wx - ax, wy - ay
            leg = math.hypot(lx, ly) or 1e-6
            while True:
                self.tick(deadline)
                mp = self.map_pose_now()
                moved += math.hypot(mp["x"] - prev["x"], mp["y"] - prev["y"])
                prev = mp
                dist = math.hypot(wx - mp["x"], wy - mp["y"])
                along = ((mp["x"] - ax) * lx + (mp["y"] - ay) * ly) / leg
                if dist < tol or (not last and along >= leg):
                    break
                # steer toward a point a little ahead on the leg, so the dog stays on the line
                k = min(leg, max(0.0, along) + LOOKAHEAD_M) / leg
                px, py = ax + lx * k, ay + ly * k
                err = wrap(math.atan2(py - mp["y"], px - mp["x"]) - mp["yaw"])
                if abs(err) > TURN_IN_PLACE:
                    self.node.moving = False
                    self.node.stop()
                    self._settle(0.3)
                    r = self._turn(math.degrees(err), max(1.0, deadline - time.monotonic()), replant=False)   # walking re-plants
                    if r["result"] != "done":
                        return dict(r, moved_m=moved)
                    hist.clear()
                    prev = self.map_pose_now()
                    continue
                ob = self.obstacle(1)
                if ob is not None:
                    self.node.moving = False
                    self.node.stop()
                    return {"result": "blocked", "side": "front", "moved_m": moved,
                            "reason": f"obstacle {ob:.2f} m ahead that is not on the map",
                            "at": [mp["x"] + math.cos(mp["yaw"]) * (ob + 0.1), mp["y"] + math.sin(mp["yaw"]) * (ob + 0.1)]}
                now = time.monotonic()
                hist.append((now, dist))
                while hist and now - hist[0][0] > STALL_S:
                    hist.popleft()
                if now - hist[0][0] > STALL_S - 0.3 and hist[0][1] - dist < STALL_M:
                    self.node.moving = False
                    self.node.stop()
                    if shuffles > 0:          # a foot may be stuck: re-plant and try again
                        shuffles -= 1
                        self._replant()
                        hist.clear()
                        prev = self.map_pose_now()
                        continue
                    return {"result": "blocked", "side": "front", "moved_m": moved, "stall": True,
                            "reason": "not making progress (something is in the way, or avoidance stopped it)",
                            "at": [mp["x"] + math.cos(mp["yaw"]) * 0.5, mp["y"] + math.sin(mp["yaw"]) * 0.5]}
                v = MOVE_SPEED if not last else max(MIN_SPEED, min(MOVE_SPEED, dist * 1.2))
                v *= max(0.6, math.cos(err))
                self.node.move(v, 0.0, max(-STEER_MAX, min(STEER_MAX, STEER_GAIN * err)))
                self.last_motion = time.monotonic()
                time.sleep(0.1)
            ax, ay = wx, wy
        self.node.moving = False
        self.node.stop()
        return {"result": "done", "moved_m": moved}

    # ---------- places (stored next to the map) ----------
    def places_path(self):
        return os.path.join(MAPS_DIR, f"{MAP_NAME}.places.json")

    def places(self):
        try:
            with open(self.places_path()) as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}

    def save_place(self, pid, description, by, pose=None, image=None, target=None):
        """Save a place. A place is where the dog stands (x, y, yaw_deg: what go_to drives to) and,
        when known, target: where the thing itself is.
        - pose None: the dog's spot now with its camera view; the target is the first mapped obstacle
          straight ahead, if any within 4 m.
        - pose {x, y, yaw}: a stand spot picked on the map, with target (x, y) or None and image
          (an earlier camera frame) or None."""
        if not re.fullmatch(r"[a-z0-9_]{1,40}", pid or ""):
            raise ValueError("id must be 1-40 characters of a-z, 0-9 or _")
        if pose is not None:
            mp, img = pose, image
        else:
            mp = self.snap()[4]
            if mp is None:
                raise ValueError("no map pose: mapping or localization is not running")
            mp = dict(mp, pitch_deg=round(math.degrees(self.node.head)))
            with self.lock:
                img = self.full["img"]
            if target is None and self.planner is not None:
                target = self.planner.raycast(mp["x"], mp["y"], mp["yaw"])
        prev_dir = os.path.join(MAPS_DIR, f"{MAP_NAME}_places")
        os.makedirs(prev_dir, exist_ok=True)
        preview = None
        stale = os.path.join(prev_dir, f"{pid}.jpg")
        if img is None and os.path.exists(stale):
            os.remove(stale)      # replacing a place: don't keep the old one's picture
        if img is not None:
            preview = f"{pid}.jpg"
            cv2.imwrite(os.path.join(prev_dir, preview), img, [cv2.IMWRITE_JPEG_QUALITY, 85])
            os.chown(os.path.join(prev_dir, preview), HOST_UID, HOST_UID)
        with self.places_lock:
            places = self.places()
            places[pid] = {"id": pid, "x": round(mp["x"], 3), "y": round(mp["y"], 3),
                           "yaw_deg": round(math.degrees(mp["yaw"]), 1),
                           "pitch_deg": float(mp.get("pitch_deg", 0.0)), "description": str(description or "")[:300],
                           "target": {"x": round(target[0], 2), "y": round(target[1], 2)} if target else None,
                           "preview": f"/places/{preview}" if preview else None, "map": MAP_NAME,
                           "saved_by": by, "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                           "marked_on_map": pose is not None}
            self._write(places)
        os.chown(prev_dir, HOST_UID, HOST_UID)
        return places[pid]

    def move_place(self, pid, by, x=None, y=None, yaw_deg=None, target=None):
        """A person drags a place on the map: change its stand spot, heading and/or target, keeping its photo
        and description. target: {x, y}, or False to remove it."""
        with self.places_lock:
            places = self.places()
            p = places.get(pid)
            if p is None:
                return None
            if x is not None:
                p["x"] = round(float(x), 3)
            if y is not None:
                p["y"] = round(float(y), 3)
            if yaw_deg is not None:
                p["yaw_deg"] = round((float(yaw_deg) + 180) % 360 - 180, 1)
            if target is False:
                p["target"] = None
            elif target is not None:
                p["target"] = {"x": round(float(target["x"]), 2), "y": round(float(target["y"]), 2)}
            p["moved_by"], p["moved_at"] = by, time.strftime("%Y-%m-%d %H:%M:%S")
            self._write(places)
            return p

    def delete_place(self, pid):
        with self.places_lock:
            places = self.places()
            if places.pop(pid, None) is None:
                return False
            self._write(places)
            return True

    def _write(self, places):
        tmp = self.places_path() + ".tmp"
        with open(tmp, "w") as f:
            json.dump(places, f, indent=1)
        os.chown(tmp, HOST_UID, HOST_UID)
        os.replace(tmp, self.places_path())
