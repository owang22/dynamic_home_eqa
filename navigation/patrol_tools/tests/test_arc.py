"""Offline tests for /agent/arc (go2_agent._arc): fake node / odom / cloud from harness.py. Nothing touches ROS or the dog."""
import io, json, math, sys, threading, time
sys.path.insert(0, "/tmp/arctest")
import numpy as np
import harness as H
from harness import World, fake_l515
import go2_agent as A, go2_patrol
import go2_dashboard as D          # module import only (no rclpy.init / node)

RES = []
def ok(name, cond, info=""):
    RES.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (f"  [{info}]" if info else ""), flush=True)

C = "cheetah-patrol"


class Cloud:
    """Keeps latest["cloud"] fresh (5 Hz) with self.obs [[x, y, top_z]] and self.under ([[x, y]] under_obs), odom frame."""
    def __init__(self, w):
        self.w, self.obs, self.under, self.on = w, [], [], True
        threading.Thread(target=self.loop, daemon=True, name="cloud").start()
        time.sleep(0.3)

    def loop(self):
        while self.w.sim.run:
            if self.on:
                with self.w.lock:
                    self.w.latest["cloud"] = {"frame": "odom", "obs": [list(p) for p in self.obs], "flat": [],
                                              "under_obs": [list(p) for p in self.under], "under": []}
                    self.w.latest["stamps"]["cloud"] = time.time()
            time.sleep(0.2)


def body_pt(w, bx, by):
    """A body-frame point (x ahead, y left of base_link now) in odom."""
    s = w.sim
    c, si = math.cos(s.yaw), math.sin(s.yaw)
    return s.x + c * bx - si * by, s.y + si * bx + c * by


def arc_pt(w, v, wz, s_m, lat=0.0):
    """A point s_m along the arc of (v, wz) from the dog's pose now, lat m to the left of the path (start frame)."""
    _, x, y, th = A.arc_poses(v, wz, s_m, 1)
    x, y, th = x[-1], y[-1], th[-1]
    return body_pt(w, x - math.sin(th) * lat, y + math.cos(th) * lat)


def world(planner=False):
    w = World()
    if not planner:
        w.ag.planner = None          # the saved map has furniture right behind START (map rear check tested apart)
    w.claim()
    w.cloud = Cloud(w)
    return w


def moves(w, n0):
    return [c for c in w.node.calls[n0:] if c[2] == "move"]


def arc(w, client="arc-test", **a):
    return w.ag.tool("arc", client, dict(a, client=client))


def bg(fn):
    res = {}
    th = threading.Thread(target=lambda: res.update(r=fn()))
    th.start()
    return th, res


# ---------------- argument checks ----------------
w = world()
for bad, why in [({"v_mps": 0.3, "w_radps": 0.3}, "neither distance nor yaw"),
                 ({"v_mps": 0.3, "w_radps": 0.3, "distance_m": 0.5, "end_yaw_deg": 30}, "both"),
                 ({"v_mps": 0.3, "w_radps": 0.3, "end_yaw_deg": -30}, "yaw sign mismatch"),
                 ({"v_mps": 0.3, "w_radps": 0.0, "end_yaw_deg": 30}, "yaw with w=0"),
                 ({"v_mps": 0.0, "w_radps": 0.3, "distance_m": 0.5}, "v=0"),
                 ({"v_mps": 0.3, "w_radps": 0.3, "distance_m": -0.5}, "negative distance"),
                 ({"v_mps": 0.3, "w_radps": 0.3, "distance_m": 0.5, "dry": "true"}, "dry as a string"),
                 ({"v_mps": 0.1, "w_radps": 0.6, "distance_m": 2.0}, "turns > 360 deg"),
                 ({"w_radps": 0.3, "distance_m": 0.5}, "no v")]:
    try:
        arc(w, **bad); raised = False
    except ValueError:
        raised = True
    ok(f"bad arguments -> ValueError (400): {why}", raised)

# ---------------- a clear forward arc ----------------
n0 = len(w.node.calls)
code, out = arc(w, v_mps=0.3, w_radps=0.3, distance_m=0.6)
ok("clear forward arc (distance): done/arrived", out["result"] == "done" and out["stop_reason"] == "arrived", out.get("reason"))
ok("  stops at the length (0.6 m +-0.06)", abs(out["moved_m"] - 0.6) < 0.06, out["moved_m"])
ok("  heading change = length * w / v (34.4 deg +-5)", abs(out["turned_deg"] - 34.4) < 5, out["turned_deg"])
mv = moves(w, n0)
ok("  every command is (0.3, 0, 0.3)", mv and all(abs(c[3] - 0.3) < 1e-3 and abs(c[5] - 0.3) < 1e-3 and c[4] == 0 for c in mv),
   set((c[3], c[5]) for c in mv))
ok("  arc info", out["arc"]["radius_m"] == 1.0 and out["arc"]["ends_on"] == "distance_m" and out["min_clearance_m"] is None, out["arc"])
code, out = arc(w, v_mps=0.3, w_radps=-0.5, end_yaw_deg=-45)
ok("clear forward arc (end_yaw_deg -45, right): done", out["result"] == "done" and abs(out["turned_deg"] + 45) < 5
   and abs(out["moved_m"] - math.radians(45) * 0.6) < 0.08, (out["turned_deg"], out["moved_m"]))
ok("non-patrol arc has no caps", w.ag.caps is None)

# ---------------- refused / allowed by the swept footprint ----------------
# straight (w = 0): a cell 0.6 m ahead beside the path. Clear iff lateral > BODY_HW + ARC_MARGIN (0.205)
for lat, want in [(0.0, False), (0.22, False), (0.25, True), (-0.22, False), (-0.25, True)]:   # margin 0.08 (body half-width 0.155)
    w.cloud.obs = [[*arc_pt(w, 0.3, 0.0, 0.6, lat), 0.4]]; time.sleep(0.3)
    n0 = len(w.node.calls)
    code, out = arc(w, v_mps=0.3, w_radps=0.0, distance_m=0.5)
    clear = out["result"] == "done"
    ok(f"straight arc, cell 0.6 m ahead at lateral {lat:+.2f}: {'runs' if want else 'refused'}", clear == want and
       (want or (out["result"] == "refused" and out["why"]["code"] == "arc_blocked" and not moves(w, n0))),
       f"{out['result']} {out.get('why', {}).get('side')} clr {out.get('why', {}).get('clearance_m')}")
    if not want:
        side = out["why"]["side"]
        ok(f"  side reported ({side})", ("front" in side) if lat == 0 else (("left" if lat > 0 else "right") in side), out["why"])
# curved (R = 1 m, left): inner sweep boundary R - HW = 0.845 from the turning centre, outer corners sqrt(HL^2 + (R+HW)^2) = 1.207
R = 1.0
def centre_pt(w, r, ang):        # point at radius r from the turning centre (0, R) at arc angle ang (start frame)
    return body_pt(w, r * math.sin(ang), R - r * math.cos(ang))
for r, want, what in [(0.845 - A.ARC_MARGIN - 0.02, True, "just inside the inner sweep + margin"),
                      (0.845 - A.ARC_MARGIN + 0.015, False, "inner edge within the margin"),
                      (1.207 + A.ARC_MARGIN + 0.02, True, "just outside the outer corners + margin"),
                      (1.207 + A.ARC_MARGIN - 0.03, False, "outer corner within the margin")]:
    w.cloud.obs = [[*centre_pt(w, r, 0.3), 0.3]]; time.sleep(0.3)
    code, out = arc(w, v_mps=0.3, w_radps=0.3, distance_m=0.6, dry=True)
    ok(f"curved arc R=1, cell at r={r:.3f} ({what}): clear={want}", out["clear"] == want,
       f"min {out['min_clearance_m']} {out.get('blocked_at') and out['blocked_at']['side']}")
w.cloud.obs = [[*centre_pt(w, 0.845 - A.ARC_MARGIN + 0.015, 0.3), 0.3]]; time.sleep(0.3)
code, out = arc(w, v_mps=0.3, w_radps=0.3, distance_m=0.6)
ok("  real run refused there, with s_m / heading / side / clearance", out["result"] == "refused" and out["stop_reason"] == "refused"
   and out["why"]["code"] == "arc_blocked" and "left" in out["why"]["side"] and 0 < out["why"]["s_m"] <= 0.6
   and "heading_deg" in out["why"] and out["why"]["clearance_m"] < A.ARC_MARGIN and "obstacle" in out["why"], out["why"])
w.cloud.obs = [[*centre_pt(w, 1.207 + A.ARC_MARGIN - 0.03, 0.45), 0.3]]; time.sleep(0.3)
code, out = arc(w, v_mps=0.3, w_radps=0.3, distance_m=0.6, dry=True)
ok("  outer hit is on the right side (front-right corner)", out["blocked_at"] and out["blocked_at"]["side"] == "front-right corner",
   out.get("blocked_at"))
# cells inside the current footprint are the dog itself; floor cells don't count; tall cells and under_obs do
w.cloud.obs = [[*body_pt(w, 0.25, 0.10), 0.4], [*body_pt(w, -0.3, -0.1), 0.3], [*arc_pt(w, 0.3, 0.0, 0.6), 0.1]]; time.sleep(0.3)
code, out = arc(w, v_mps=0.3, w_radps=0.0, distance_m=0.5, dry=True)
ok("cells inside the body now and floor cells are ignored", out["clear"] and out["min_clearance_m"] is None, out["min_clearance_m"])
w.cloud.obs = [[*arc_pt(w, 0.3, 0.0, 0.6), 1.3]]; time.sleep(0.3)
code, out = arc(w, v_mps=0.3, w_radps=0.0, distance_m=0.5, dry=True)
ok("a tall cell (wall top 1.3 m) blocks", not out["clear"], out["min_clearance_m"])
w.cloud.obs = [[*arc_pt(w, 0.3, 0.0, 0.6), 0.75]]; time.sleep(0.3)
code, out = arc(w, v_mps=0.3, w_radps=0.0, distance_m=0.5, dry=True)
ok("a desk top with open floor under it does not block", out["clear"], out["min_clearance_m"])
w.cloud.obs = []; w.cloud.under = [list(arc_pt(w, 0.3, 0.0, 0.6))]; time.sleep(0.3)
code, out = arc(w, v_mps=0.3, w_radps=0.0, distance_m=0.5, dry=True)
ok("under_obs (chair seat under a top) blocks", not out["clear"])
w.cloud.under = []
w.cloud.obs = [[*body_pt(w, 0.0, 0.155 + 0.03), 0.4]]; time.sleep(0.3)
code, out = arc(w, v_mps=0.3, w_radps=0.0, distance_m=0.5, dry=True)
ok("a cell 3 cm beside the body now blocks at s=0", not out["clear"] and out["blocked_at"]["s_m"] == 0.0
   and out["blocked_at"]["side"] == "left edge", out.get("blocked_at"))
w.cloud.obs = []; time.sleep(0.3)

w.cloud.obs = [[*body_pt(w, 0.35 + 0.5 + 0.07, 0.0), 0.4]]; time.sleep(0.3)
code, out = arc(w, v_mps=0.3, w_radps=0.0, distance_m=0.5, dry=True)
ok("a cell 7 cm past the front at the arc's end blocks (coast allowance 9 cm)", not out["clear"] and out["blocked_at"]["side"] == "front edge",
   out.get("blocked_at"))
w.cloud.obs = []; time.sleep(0.3)

# ---------------- no / stale cloud ----------------
w.cloud.on = False
with w.lock:
    w.latest["stamps"]["cloud"] = time.time() - 5
n0 = len(w.node.calls)
code, out = arc(w, v_mps=0.3, w_radps=0.0, distance_m=0.5)
ok("stale cloud: refused no_live_cloud, nothing sent", out["result"] == "refused" and out["why"]["code"] == "no_live_cloud"
   and not moves(w, n0), out.get("reason"))
w.cloud.on = True; time.sleep(0.4)
th, res = bg(lambda: arc(w, v_mps=0.3, w_radps=0.0, distance_m=2.0))
time.sleep(1.0); w.cloud.on = False; th.join(10); w.cloud.on = True
out = res["r"][1]
ok("cloud goes stale mid-arc: stops, stale_sensors", out["result"] == "error" and out["stop_reason"] == "stale_sensors"
   and 0.2 < out["moved_m"] < 1.5, (out.get("reason"), out.get("moved_m")))
time.sleep(0.4)

# ---------------- stops mid-arc when an obstacle appears ----------------
v, wz = 0.3, 0.3
target = arc_pt(w, v, wz, 1.5)
th, res = bg(lambda: arc(w, v_mps=v, w_radps=wz, distance_m=1.5))
time.sleep(1.2)
w.cloud.obs = [[*target, 0.4]]
th.join(10)
out = res["r"][1]
ok("obstacle appears on the remaining arc: blocked/obstacle mid-arc", out["result"] == "blocked" and out["stop_reason"] == "obstacle"
   and out["why"]["code"] == "arc_blocked" and 0.25 < out["moved_m"] < 1.2, (out.get("reason"), out.get("moved_m")))
w.cloud.obs = []; time.sleep(0.3)

# ---------------- stall ----------------
real_move = w.node.move
w.node.move = lambda x, y, z: w.node._rec("move", round(x, 3), round(y, 3), round(z, 3))   # the dog doesn't move
code, out = arc(w, v_mps=0.3, w_radps=0.3, distance_m=0.5)
w.node.move = real_move
ok("stall: blocked / stuck", out["result"] == "blocked" and out["stop_reason"] == "stuck", out.get("reason"))

# ---------------- abort / human takeover ----------------
th, res = bg(lambda: arc(w, v_mps=0.3, w_radps=0.2, distance_m=2.0))
time.sleep(1.0); w.ag.interrupt("stop from agent arc-test"); th.join(10)
out = res["r"][1]
ok("agent stop aborts the arc", out["result"] == "aborted" and out["stop_reason"] == "stop" and out["moved_m"] > 0.1, out.get("reason"))
w.claim()
th, res = bg(lambda: arc(w, v_mps=0.3, w_radps=0.2, distance_m=2.0))
time.sleep(1.0); n_stop = len(w.node.calls); w.ag.human_drives("console", "10.0.0.9"); th.join(10)
out = res["r"][1]
ok("human takeover aborts the arc", out["result"] == "aborted" and out["stop_reason"] == "person", out.get("reason"))
time.sleep(0.4)
mv_after = [c for c in w.node.calls[n_stop:] if c[2] == "move"]
ok("  no velocity after the takeover (at most one in-flight tick)", len(mv_after) <= 1, len(mv_after))
w.ag.owner = None; w.claim()

# ---------------- dry run ----------------
w.cloud.obs = [[*arc_pt(w, 0.3, 0.3, 0.5, 0.0), 0.4]]; time.sleep(0.3)
n0, lm = len(w.node.calls), w.ag.last_motion
code, out = arc(w, v_mps=0.3, w_radps=0.3, distance_m=0.8, dry=True)
ok("dry run: zero commands (no move, no stop)", len(w.node.calls) == n0 and w.ag.last_motion == lm, w.node.calls[n0:])
p = out["profile"]
pa = [r for r in p if not r.get("coast")]
ok("dry run: profile rows every <= 5 cm / 3 deg, s 0..0.8, then coast rows to 0.8 + 0.3 s * v", out["dry"] and len(pa) >= 17
   and p[0]["s_m"] == 0 and abs(pa[-1]["s_m"] - 0.8) < 0.05 and abs(p[-1]["s_m"] - 0.89) < 1e-6 and out["arc"]["coast_m"] == 0.09
   and all(b["s_m"] - a["s_m"] <= 0.0501 for a, b in zip(p, p[1:])), (len(p), pa[-1]["s_m"], p[-1]["s_m"]))
ok("dry run: blocked ahead, clearance falls to the hit", out["clear"] is False and out["blocked_at"]["code"] == "arc_blocked"
   and "front" in out["blocked_at"]["side"] and p[0]["clearance_m"] > out["blocked_at"]["clearance_m"]
   and out["min_clearance_m"] < 0, (out["blocked_at"]["s_m"], out["min_clearance_m"]))
ok("dry run: stop_reason done, end_pose given", out["stop_reason"] == "done" and out["end_pose"] and "x" in out["end_pose"], out.get("end_pose"))
w.cloud.obs = []; time.sleep(0.3)
code, out = arc(w, v_mps=0.1, w_radps=0.6, end_yaw_deg=350, dry=True)
ok("dry run: long profile thinned to ARC_PROFILE_MAX", out["clear"] and len(out["profile"]) <= A.ARC_PROFILE_MAX, len(out["profile"]))
w.close()

# ---------------- saved-map rear check (planner on, START has furniture behind it) ----------------
w = world(planner=True)
code, out = arc(w, v_mps=-0.15, w_radps=0.1, distance_m=0.4)
ok("reverse arc from START: stopped mid-arc by the saved-map rear check", out["result"] == "blocked" and out["stop_reason"] == "obstacle"
   and out["why"]["code"] == "rear_blocked" and out["why"]["source"] == "saved_map" and -0.4 < out["moved_m"] < -0.02,
   (out.get("why"), out.get("moved_m")))
code, out = arc(w, v_mps=-0.15, w_radps=0.1, distance_m=0.3, dry=True)
ok("  dry run there says so (clear false, rear_blocked saved_map)", out["clear"] is False and out["rear_blocked"]["source"] == "saved_map")
n0 = len(w.node.calls)
code, out = arc(w, v_mps=-0.15, w_radps=0.1, distance_m=0.3)
ok("  and a real reverse arc there is refused before moving", out["result"] == "refused" and out["why"]["code"] == "rear_blocked"
   and not moves(w, n0), out.get("why"))
code, out = arc(w, v_mps=0.3, w_radps=0.1, distance_m=0.3, dry=True)
ok("  forward arc there: no rear check", out["clear"] and "rear_blocked" not in out)
w.cloud.obs = [[*body_pt(w, -0.5, 0.0), 0.4]]; time.sleep(0.3)
pl, w.ag.planner = w.ag.planner, None
code, out = arc(w, v_mps=-0.15, w_radps=0.0, distance_m=0.1, dry=True)
ok("  live rear box (no map): 0.5 m behind refuses even a 0.1 m reverse arc", out["clear"] is False and out["rear_blocked"]["source"] == "live_rear_box",
   out.get("rear_blocked"))
w.ag.planner = pl
w.close()

# ---------------- patrol envelope: caps, curvature, reverse budget, dry runs ----------------
w = world(); fake_l515(w.pt)
code, st = w.pt.start(C, {"max_min": 5, "speed": "slow"})
ok("patrol start", code == 200, st.get("why"))
w.claim(C)
n0 = len(w.node.calls)
code, out = w.pt.tool("arc", C, {"v_mps": 0.5, "w_radps": 0.9, "distance_m": 0.4, "client": C})
mv = moves(w, n0)
ratio = set(round(c[5] / c[3], 2) for c in mv)
ok("patrol slow: caps v 0.30 / w 0.50, scaled together (curvature 1.8 kept)", out["result"] == "done" and
   max(c[3] for c in mv) <= 0.3001 and max(abs(c[5]) for c in mv) <= 0.5001 and ratio == {1.8}, (ratio, out["arc"].get("clamped")))
ok("  clamped reported", out["arc"]["clamped"]["scale"] == round(min(0.3 / 0.5, 0.5 / 0.9), 3), out["arc"]["clamped"])
ok("  heading change follows the asked curvature (0.4 m * 1.8 = 41 deg +-6)", abs(out["turned_deg"] - math.degrees(0.72)) < 6, out["turned_deg"])
w.pt.p["speed"] = "normal"
n0 = len(w.node.calls)
code, out = w.pt.tool("arc", C, {"v_mps": 0.5, "w_radps": -0.9, "distance_m": 0.4, "client": C})
mv = moves(w, n0)
ok("patrol normal: v <= 0.40, |w| <= 0.60, curvature kept", max(c[3] for c in mv) <= 0.4001 and max(abs(c[5]) for c in mv) <= 0.6001
   and set(round(c[5] / c[3], 2) for c in mv) == {-1.8}, (max(c[3] for c in mv), max(abs(c[5]) for c in mv)))
walked0, used0 = w.pt.p["walked_m"], w.pt.p["reverse_used_m"]
n0 = len(w.node.calls)
code, out = w.pt.tool("arc", C, {"v_mps": -0.3, "w_radps": -0.3, "distance_m": 0.8, "client": C})
mv = moves(w, n0)
ok("reverse arc in patrol: |v| <= 0.15, curvature kept, capped at back_m 0.5", out["result"] == "done" and min(c[3] for c in mv) >= -0.1501
   and set(round(c[5] / c[3], 2) for c in mv) == {1.0} and out["arc"]["capped"]["length_m"] == 0.5 and -0.56 < out["moved_m"] < -0.44,
   (min(c[3] for c in mv), out.get("moved_m"), out["arc"].get("capped")))
ok("  counts toward the reverse budget and walked_m", abs(w.pt.p["reverse_used_m"] - used0 + out["moved_m"]) < 1e-6
   and w.pt.p["walked_m"] > walked0, (w.pt.p["reverse_used_m"], w.pt.p["walked_m"]))
code, out = w.pt.tool("arc", C, {"v_mps": -0.15, "w_radps": 0.2, "distance_m": 0.8, "client": C})
used = w.pt.p["reverse_used_m"]
ok("  second reverse arc capped to what is left", out["result"] == "done" and used > 0.9, (out.get("arc", {}).get("capped"), used))
code, out = w.pt.tool("arc", C, {"v_mps": -0.15, "w_radps": 0.2, "distance_m": 0.3, "client": C})
ok("  budget used up: refused reverse_budget", code == 409 and out["why"]["code"] == "reverse_budget", (used, out.get("why"), out.get("moved_m")))
code, out = w.pt.tool("arc", C, {"v_mps": 0.3, "w_radps": 0.2, "distance_m": 0.3, "client": C})
ok("  forward arcs still allowed", out["result"] == "done", out.get("reason"))
# dry runs inside the patrol: allowed even when motion is refused, send nothing, don't reset the standing clock
w.mapper.suspect_since = time.time(); time.sleep(0.4)
code, out = w.pt.tool("arc", C, {"v_mps": 0.3, "w_radps": 0.3, "distance_m": 0.5, "client": C})
ok("patrol: real arc refused on an envelope condition (loc_suspect)", code == 409 and out["why"]["code"] == "loc_suspect", out.get("why"))
time.sleep(1.0)
ss, lm, n0 = w.pt.stand_since, w.ag.last_motion, len(w.node.calls)
code, out = w.pt.tool("arc", C, {"v_mps": 0.3, "w_radps": 0.3, "distance_m": 0.5, "dry": True, "client": C})
time.sleep(0.5)
ok("patrol: dry run allowed while motion is refused", code == 200 and out["result"] == "done" and out["dry"], out.get("why"))
ok("  dry run: nothing sent by the tool or the monitor", len(w.node.calls) == n0, w.node.calls[n0:])
ok("  dry run: standing clock not reset", w.pt.stand_since == ss and w.ag.last_motion == lm and w.pt._standing_s() > 1.0,
   (w.pt._standing_s(),))
ok("  dry run: no envelope interrupt", not [e for e in w.pt.p["events"] if e["kind"] == "interrupt"])
w.mapper.suspect_since = None; time.sleep(0.4)
# the monitor interrupts a running arc on an envelope condition
th, res = bg(lambda: w.pt.tool("arc", C, {"v_mps": 0.3, "w_radps": 0.2, "distance_m": 2.0, "client": C}))
time.sleep(1.2); w.batt.update(soc=20); th.join(10)
out = res["r"][1]
ok("patrol monitor stops a running arc (battery_low)", out["result"] == "aborted" and out["stop_reason"] == "battery_low", out.get("stop_reason"))
ok("go2_patrol.MOTION_CALLS has arc", "arc" in go2_patrol.MOTION_CALLS)
w.close()

# ---------------- console routing (go2_dashboard.Handler) ----------------
w = world()
w.ag.owner = None
D.AG, D.PATROLS, D.MAPPER, D.KEEPOUT, D.NODE, D.MARKERS, D.DEPLOYING = w.ag, w.pt, w.mapper, w.keepout, w.node, None, None


class FH(D.Handler):
    def __init__(self, path, body=None):
        raw = json.dumps(body).encode()
        self.client_address, self.path = ("127.0.0.1", 5555), path
        self.rfile, self.wfile = io.BytesIO(raw), io.BytesIO()
        self.headers = {"Content-Length": str(len(raw))}
        self.code, self.hdrs, self.err = None, {}, None
        self.do_POST()
    def send_response(self, code, message=None): self.code = code
    def send_header(self, k, v): self.hdrs[k] = v
    def end_headers(self): pass
    def send_error(self, code, message=None, explain=None): self.code, self.err = code, message
    def json(self): return json.loads(self.wfile.getvalue() or b"null")


ok("arc in AGENT_CALLS and MOTION_AGENT_CALLS", "arc" in D.AGENT_CALLS and "arc" in D.MOTION_AGENT_CALLS)
r = FH("/agent/arc", {"client": "arc-http", "v_mps": 0.3, "w_radps": 0.3, "distance_m": 0.3, "dry": True})
ok("HTTP dry arc: 200 + profile", r.code == 200 and r.json().get("dry") and r.json().get("profile"), (r.code, r.err))
r = FH("/agent/arc", {"client": "arc-http", "v_mps": 0.3, "w_radps": 0.3})
ok("HTTP bad arguments: 400", r.code == 400 and r.json()["stop_reason"] == "bad_arguments", r.json())
r = FH("/agent/arc", {"client": "other", "v_mps": 0.3, "w_radps": 0.3, "distance_m": 0.3, "dry": True})
ok("HTTP: another agent holding the claim -> 409 (dry runs need the claim too)", r.code == 409, r.json())
D.DEPLOYING = {"t": 0, "msg": "test"}
n0 = len(w.node.calls)
r = FH("/agent/arc", {"client": "arc-http", "v_mps": 0.3, "w_radps": 0.3, "distance_m": 0.3, "dry": True})
r2 = FH("/agent/arc", {"client": "arc-http", "v_mps": 0.3, "w_radps": 0.3, "distance_m": 0.3})
ok("HTTP while deploying: 503 for real and dry arcs, nothing sent", r.code == 503 and r2.code == 503 and len(w.node.calls) == n0)
D.DEPLOYING = None
r = FH("/agent/arc", {"client": "arc-http", "v_mps": 0.3, "w_radps": 0.3, "distance_m": 0.3})
ok("HTTP real arc: done", r.code == 200 and r.json()["result"] == "done", r.json().get("reason"))
w.close()

print(f"\n{sum(r for _, r in RES)}/{len(RES)} passed", flush=True)
