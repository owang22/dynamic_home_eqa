"""11-22 margins tests (Oliver: margins too strict, the agent may lower them): footprint turn sweep over the turn still
to go, the margins tool (/agent/margins), ok_to_turn at the agent's margin, stall_info, and the stand sequence
(StandUp, wait for the rise, then BalanceStand)."""
import io, json, math, sys, threading, time, types
sys.path.insert(0, "/tmp/s3test")
import numpy as np
import harness as H
from harness import World
import go2_agent as A, go2_patrol, os, tempfile
A.HELD_FILE = os.path.join(tempfile.mkdtemp(), "held_cloud.json")
import go2_dashboard as D

RES = []
def ok(name, cond, info=""):
    RES.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (f"  [{info}]" if info else ""), flush=True)

C = "cheetah-patrol"


class Cloud:
    def __init__(self, w):
        self.w, self.obs, self.on = w, [], True
        threading.Thread(target=self.loop, daemon=True, name="cloud").start()
        time.sleep(0.3)

    def loop(self):
        while self.w.sim.run:
            if not self.on:
                time.sleep(0.2); continue
            with self.w.lock:
                self.w.latest["cloud"] = {"frame": "odom", "obs": [list(p) for p in self.obs], "flat": [],
                                          "under_obs": [], "under": []}
                self.w.latest["stamps"]["cloud"] = time.time()
            time.sleep(0.2)


def body_pt(w, bx, by):
    s = w.sim
    c, si = math.cos(s.yaw), math.sin(s.yaw)
    return s.x + c * bx - si * by, s.y + si * bx + c * by


def put(w, bx, by):
    w.cloud.obs = [[*body_pt(w, bx, by), 0.4]]
    time.sleep(0.35)


class FH(D.Handler):
    def __init__(self, path, body=None, method="POST"):
        raw = json.dumps(body).encode() if body is not None else b""
        self.client_address, self.path = ("127.0.0.1", 5555), path
        self.rfile, self.wfile = io.BytesIO(raw), io.BytesIO()
        self.headers = {"Content-Length": str(len(raw))}
        self.code, self.hdrs, self.err = None, {}, None
        (self.do_POST if method == "POST" else self.do_GET)()
    def send_response(self, code, message=None): self.code = code
    def send_header(self, k, v): self.hdrs[k] = v
    def end_headers(self): pass
    def send_error(self, code, message=None, explain=None): self.code, self.err = code, message
    def log_message(self, *a): pass
    def json(self): return json.loads(self.wfile.getvalue() or b"null")


w = World()
w.ag.planner = None
w.claim()
w.cloud = Cloud(w)
D.AG, D.PATROLS, D.MAPPER, D.KEEPOUT, D.NODE, D.MARKERS, D.DEPLOYING = w.ag, w.pt, w.mapper, w.keepout, w.node, None, None
ag = w.ag

# footprint sweep
put(w, 0.0, 0.30)
ok("side cell 0.30 m: a full turn is blocked", ag.sweep_hit(None) is not None)
ok("side cell 0.30 m: a 10 deg turn is clear", ag.sweep_hit(math.radians(10)) is None)
put(w, 0.0, 0.40)
ok("side cell 0.40 m: full turn blocked at the default margin (0.03 -> needs 0.42)", ag.sweep_hit(None) is not None)
ok("side cell 0.40 m: full turn clear at margin 0.0 (corner radius 0.383)", ag.sweep_hit(None, 0.0) is None)
ok("side cell 0.40 m: 40 deg left clear at the default margin", ag.sweep_hit(math.radians(40)) is None)
ok("side cell 0.40 m: 100 deg left blocked at the default margin", ag.sweep_hit(math.radians(100)) is not None)
put(w, 0.36, 0.0)
ok("cell 0.36 m dead ahead: even a 5 deg turn is blocked (inside the inflated body)", ag.sweep_hit(math.radians(5)) is not None)

# real turns through the tool
put(w, 0.0, 0.40)
code, out = ag.tool("turn", w.client if hasattr(w, "client") else C, {"client": C, "deg": 30, "timeout_s": 20})
ok("turn 30 deg next to a 0.40 m side cell: done", out.get("result") == "done", out)
put(w, 0.0, 0.40)
code, out = ag.tool("turn", C, {"client": C, "deg": 170, "timeout_s": 20})
ok("turn 170 deg there: turn_blocked with margin + obstacle in why", out.get("result") == "blocked"
   and (out.get("why") or {}).get("code") == "turn_blocked" and "turn_margin_m" in out["why"], out)

# margins tool over HTTP
r = FH("/agent/margins", {"client": C, "turn_margin_m": 0.0, "why": "Oliver turned 190 deg here with 0.46 m clearance"})
ok("margins set (200)", r.code == 200 and r.json()["margins"]["turn_margin_m"] == 0.0 and "set by" in r.json()["margins"]["source"], r.json())
ok("margins in force for the owner", ag.margins()["turn_margin_m"] == 0.0)
put(w, 0.0, 0.40)
code, out = ag.tool("turn", C, {"client": C, "deg": 170, "timeout_s": 20})
ok("turn 170 deg next to the 0.40 m cell at turn margin 0.0: not refused up front (turns > 30 deg; the sim's forward "
   "rock may bring the cell inside 0.383 m later)", out.get("result") == "done" or abs(out.get("turned_deg") or 0) > 30, out)
r = FH("/agent/margins", {"client": C, "turn_margin_m": 0.5})
ok("margin above max refused (400)", r.code == 400, r.json())
r = FH("/agent/margins", {"client": C})
ok("margins with nothing to set refused (400)", r.code == 400)
r = FH("/agent/margins", {"client": C, "get": True})
ok("margins get", r.code == 200 and r.json()["margins"]["turn_margin_m"] == 0.0)
w.cloud.obs = []
time.sleep(0.3)
ok("ok_to_turn need follows the margin (0.383 at 0.0)", go2_patrol.turn_need_m(ag) == 0.383, go2_patrol.turn_need_m(ag))
r = FH("/agent/margins", {"client": C, "arc_margin_m": 0.03})
ok("arc margin set, turn margin kept", r.json()["margins"]["arc_margin_m"] == 0.03 and r.json()["margins"]["turn_margin_m"] == 0.0)
r = FH("/agent/margins", {"client": C, "reset": True})
ok("reset -> defaults", r.json()["margins"]["source"] == "default" and r.json()["margins"]["turn_margin_m"] == A.TURN_MARGIN_M
   and go2_patrol.turn_need_m(ag) == 0.423, (r.json(), go2_patrol.turn_need_m(ag)))
ok("another client's margins do not apply to the owner", (FH("/agent/margins", {"client": "other", "turn_margin_m": 0.0}).code == 200)
   and ag.margins()["turn_margin_m"] == A.TURN_MARGIN_M)

# lateral move (AUT ask 1450)
put(w, 0.0, 0.30)          # left side: 0.145 m free beyond the body side
code, out = ag.tool("move", C, {"client": C, "lateral_m": 0.2, "timeout_s": 10})
ok("strafe 0.2 m left with 0.145 m free: refused side_blocked", out.get("result") == "refused" and out["why"]["code"] == "side_blocked", out)
y0 = w.sim.y; x0 = w.sim.x
code, out = ag.tool("move", C, {"client": C, "lateral_m": -0.2, "timeout_s": 10})
ok("strafe 0.2 m right (clear): done, moved sideways", out.get("result") == "done" and abs(out["moved_m"] + 0.2) < 0.05, out)
code, out = ag.tool("move", C, {"client": C, "lateral_m": 0.1, "m": 0.3})
ok("m and lateral_m together refused (400)", code == 400)
ok("sim got lateral commands", any(c[2] == "move" and abs(c[4]) > 0.05 for c in w.node.calls), [c for c in w.node.calls if c[2] == "move"][-2:])
# surround detail: one band cell and one tall cell
w.cloud.obs = [[*body_pt(w, 0.8, 0.0), 0.40], [*body_pt(w, 0.0, -0.9), 1.6]]
time.sleep(0.35)
sr = ag.surround()
det = [b for b in sr.get("bins_detail", []) if b.get("d_m") is not None]
ok("surround bins_detail: kinds + z of the nearest cells", any(b["kind"] == "band" and b["z_max_m"] == 0.4 for b in det)
   and any(b["kind"] == "tall" and b["z_min_m"] == 1.6 for b in det) and len(sr["bins"]) == 36, det)

# strafe inside a patrol (AUT ask 1507): allowed, not counted as reverse
from harness import fake_l515
fake_l515(w.pt)
w.cloud.obs = []; time.sleep(0.3)
code, st = w.pt.start(C, {"max_min": 5, "speed": "slow"})
ok("patrol start", code == 200, st)
code, out = w.pt.tool("move", C, {"client": C, "lateral_m": -0.2, "timeout_s": 10})
ok("patrol: strafe right done", code == 200 and out.get("result") == "done", out)
ok("patrol: strafe not counted as reverse", w.pt.p["reverse_used_m"] == 0.0, w.pt.p["reverse_used_m"])
w.pt.stop(C)
w.claim(C)

# held cloud (AUT ask 1510): lying -> lidar off; just stood up -> sparse map rebuilding
rich = [[*body_pt(w, 1.0 + 0.1 * k, 0.6), 0.4] for k in range(20)] + [[*body_pt(w, 0.0, 0.40), 0.4]]
w.cloud.obs = rich; time.sleep(0.4)
ag.snap()
w.sim.body_h = 0.08
w.cloud.on = False; time.sleep(3.5)
sr = ag.surround()
ok("lying, lidar off: surround uses the held cloud, flagged", sr.get("cloud_held") and sr["cloud_held"]["why"].startswith("lying")
   and sr["bins"] and any(b[1] is not None for b in sr["bins"]), sr.get("cloud_held"))
code, out = ag.tool("arc", C, {"client": C, "v_mps": 0.2, "w_radps": 0.0, "distance_m": 0.3, "dry": True})
ok("lying: arc dry run works on the held cloud", out.get("dry") and "clear" in out and "no_live_cloud" not in str(out.get("reason")), out.get("reason"))
ok("lying: turn sweep sees the held 0.40 m side cell", ag.sweep_hit(None) is not None)
time.sleep(0.5)
ok("lie-down saved the held cloud to disk", os.path.exists(A.HELD_FILE), A.HELD_FILE)
ag._held, ag._held_merge, ag._held_loaded = None, None, False      # as after a console restart while lying
ok("after a restart while lying: held cloud reloaded from disk", ag.sweep_hit(None) is not None
   and (ag.surround().get("cloud_held") or {}).get("why", "").startswith("lying"))
w.sim.body_h = 0.30
w.cloud.obs = [[*body_pt(w, 2.5, 0.0), 0.4]]; w.cloud.on = True; time.sleep(0.4)
_, _, _, cl, _, ages = ag.snap()
ok("just stood up (sparse live map): held cells merged with live", cl.get("held") and len(cl["obs"]) == len(rich) + 1
   and cl["held"]["why"].startswith("just stood"), (cl.get("held"), len(cl.get("obs") or [])))
w.cloud.obs = rich + [[*body_pt(w, 2.5, 0.0), 0.4]]; time.sleep(0.4)
_, _, _, cl, _, _ = ag.snap()
ok("live map rebuilt: held no longer used", not cl.get("held"))
w.cloud.obs = [[*body_pt(w, 2.5, 0.0), 0.4]]; time.sleep(0.3)
w.sim.x += 0.2; time.sleep(0.3)
_, _, _, cl, _, _ = ag.snap()
ok("dog moved: held cloud dropped", not cl.get("held"))
w.cloud.obs = []; time.sleep(0.3)

# stall_info
si = ag.stall_info()
ok("stall_info fields", {"dog_avoid_on", "body_height", "locked_stand_suspect", "hint"} <= set(si), si)

# stand sequence (Collector.action with a fake self): StandUp, wait for the rise, then BalanceStand
sent, hs = [], iter([0.08, 0.15, 0.25, 0.31, 0.329, 0.329, 0.329, 0.329, 0.329] + [0.329] * 50)
fake = types.SimpleNamespace(moving=False, head=0.0, last_cmd=0.0, stop=lambda: sent.append(("StopMove", time.monotonic())),
                             send=lambda c: sent.append((c, time.monotonic())))
D.DEPLOYING = None
stop_feed = threading.Event()
def feed():
    while not stop_feed.is_set():
        with D.lock:
            D.latest["state"] = {"body_height": next(hs)}
        time.sleep(0.1)
threading.Thread(target=feed, daemon=True).start()
t0 = time.monotonic()
D.Collector.action(fake, "stand")
stop_feed.set()
names = [c for c, _ in sent]
tu = next(t for c, t in sent if c == "StandUp")
tb = next(t for c, t in sent if c == "BalanceStand")
ok("stand: StandUp, then BalanceStand twice, after the rise", names[-3:] == ["StandUp", "BalanceStand", "BalanceStand"] and tb - tu >= 0.6,
   (names, round(tb - tu, 2)))
ok("stand returns within 5 s", time.monotonic() - t0 < 5.0)
print(f"\n{sum(r for _, r in RES)}/{len(RES)} passed")
w.sim.run = False
