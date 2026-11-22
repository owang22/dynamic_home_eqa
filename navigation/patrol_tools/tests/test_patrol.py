"""Step-3 offline tests: envelope refusals, caps, monitor (lease lapse, stand budget, human takeover), never-moves."""
import json, math, os, sys, time, threading
sys.path.insert(0, "/tmp/s3test")
import harness as H
import go2_agent, go2_patrol
from harness import World, fake_l515

RES = []
def ok(name, cond, info=""):
    RES.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (f"  [{info}]" if info else ""), flush=True)

C = "cheetah-patrol"

def fresh(**kw):
    w = World(**kw)
    w.claim()
    return w

def start(w, **req):
    code, out = w.pt.start(C, dict({"max_min": 5, "speed": "slow"}, **req))
    return code, out

# ---------------- start refusals ----------------
w = fresh()
for setup, code_want, undo in [
    (lambda: w.batt.update(soc=20), "battery_low", lambda: w.batt.update(soc=80)),
    (lambda: w.batt.update(stale=True), "battery_unknown", lambda: w.batt.pop("stale")),
    (lambda: w.mot.update(level="warm", max=62), "motor_warm", lambda: w.mot.update(level="ok", max=40)),
    (lambda: w.mot.update(level="hot", max=71), "motor_warm", lambda: w.mot.update(level="ok", max=40)),
    (lambda: setattr(w, "mot_age", 30), "motors_unknown", lambda: setattr(w, "mot_age", 1)),
    (lambda: setattr(w.sim, "body_h", 0.07), "not_standing", lambda: setattr(w.sim, "body_h", 0.30)),
    (lambda: setattr(w.mapper, "lost_since", time.time()), "loc_lost", lambda: setattr(w.mapper, "lost_since", None)),
    (lambda: setattr(w.mapper, "suspect_since", time.time()), "loc_suspect", lambda: setattr(w.mapper, "suspect_since", None)),
    (lambda: setattr(w.mapper, "T", None), "no_map_pose", lambda: setattr(w.mapper, "T", (0.0, 0.0, 0.0))),
    (lambda: setattr(w, "deploying", {"msg": "x"}), "deploying", lambda: setattr(w, "deploying", None)),
    (lambda: setattr(w.sim, "roll", 0.8), "fallen", lambda: setattr(w.sim, "roll", 0.0)),
]:
    setup(); time.sleep(0.25)
    code, out = start(w)
    codes = [c["code"] for c in out.get("why_all", [out.get("why") or {}])]
    ok(f"start refused: {code_want}", code == 409 and code_want in codes and out["result"] == "refused", f"{code} {codes}")
    undo(); time.sleep(0.25)
code, out = start(w, max_min=0); ok("start 400 max_min=0", code == 400)
code, out = start(w, max_min=31); ok("start 400 max_min=31", code == 400)
code, out = start(w, speed="fast"); ok("start 400 speed=fast", code == 400)
# stand budget almost used
go2_patrol.STAND_BUDGET_S = 100.0
w.pt.stand_since = time.monotonic() - 50
code, out = start(w); ok("start refused: stand_budget", code == 409 and out["why"]["code"] == "stand_budget", out.get("why"))
go2_patrol.STAND_BUDGET_S = 600.0
w.pt.stand_since = time.monotonic()
# human holding control: agent_may_drive refuses (the console checks this before start)
w.ag.human_drives("console", "10.0.0.9")
ok("claim refused while a person holds control", w.claim() is not None and "person" in w.claim())
w.ag.owner = None
w.claim()

# ---------------- a good start ----------------
fake_l515(w.pt)
code, out = start(w)
pid = out.get("patrol_id")
ok("start ok", code == 200 and pid and pid.startswith("p_"), out.get("why"))
pdir = os.path.join(w.tmp, "lab_patrols", pid)
pj = json.load(open(os.path.join(pdir, "patrol.json")))
ok("patrol.json written", pj["state"] == "open" and pj["client"] == C and pj["limits"]["v"] == 0.3 and pj["limits"]["turn_v"] == 0.5,
   {k: pj["limits"][k] for k in ("v", "turn_v", "back_v", "back_m")})
mc = out["mount_check"]
ok("mount check: dog + L515 colour + depth files", all(os.path.exists(os.path.join(pdir, "mount", f)) for f in mc["files"].values())
   and set(mc["files"]) == {"dog", "l515_color", "l515_depth"}, mc["files"])
ok("patrol files chowned to 1000", os.stat(os.path.join(pdir, "patrol.json")).st_uid == 1000 and os.stat(pdir).st_uid == 1000)
ok("mount check did not move the dog", not [c for c in w.node.calls if c[2] == "move"])
code2, out2 = start(w)
ok("second start refused: patrol_open", code2 == 409 and out2["why"]["code"] == "patrol_open")
w.claim("other-agent")
ok("other agent blocked by patrol", w.pt.blocks("other-agent") is not None and w.pt.blocks(C) is None)
env = w.pt.envelope_for(C)
ok("envelope fields", set(["patrol_id", "time_left_s", "battery", "hottest_motor_c", "motor_level", "standing_s",
                           "stand_budget_s", "reverse_used_m", "loc"]) <= set(env) and set(env["loc"]) == {"lost", "suspect", "track_fit"}, env)

# ---------------- caps: forward / turn / reverse ----------------
n0 = len(w.node.calls)
code, out = w.pt.tool("move", C, {"m": 0.6, "client": C})
mv = [c for c in w.node.calls[n0:] if c[2] == "move"]
ok("slow forward cap 0.30 m/s", out["result"] == "done" and max(c[3] for c in mv) <= 0.3001, f"max {max(c[3] for c in mv)} moved {out.get('moved_m')}")
n0 = len(w.node.calls)
code, out = w.pt.tool("turn", C, {"deg": 60, "client": C})
mv = [c for c in w.node.calls[n0:] if c[2] == "move"]
ok("slow turn cap 0.5 rad/s", out["result"] == "done" and max(abs(c[5]) for c in mv) <= 0.5001, f"max {max(abs(c[5]) for c in mv)}")
w.pt.p["speed"] = "normal"
n0 = len(w.node.calls)
code, out = w.pt.tool("move", C, {"m": 0.8, "client": C})
mv = [c for c in w.node.calls[n0:] if c[2] == "move"]
ok("normal forward cap 0.40 m/s", max(c[3] for c in mv) <= 0.4001 and max(c[3] for c in mv) > 0.35, f"max {max(c[3] for c in mv)}")
n0 = len(w.node.calls)
code, out = w.pt.tool("turn", C, {"deg": -60, "client": C})
mv = [c for c in w.node.calls[n0:] if c[2] == "move"]
ok("normal turn cap 0.6 rad/s", max(abs(c[5]) for c in mv) <= 0.6001, f"max {max(abs(c[5]) for c in mv)}")
# the saved map has furniture right behind the start spot (go2_agent's map raycast stopped the first try at -0.43 m,
# which is the existing REAR_CLEAR check working): test the reverse budget with the map raycast off (no cloud either)
planner, w.ag.planner = w.ag.planner, None
n0 = len(w.node.calls)
code, out = w.pt.tool("move", C, {"m": -0.8, "client": C})
mv = [c for c in w.node.calls[n0:] if c[2] == "move"]
ok("reverse clamped to 0.5 m at <=0.15 m/s", out.get("clamped", {}).get("m") == -0.5 and min(c[3] for c in mv) >= -0.1501
   and -0.55 < out["moved_m"] < -0.44, f"moved {out.get('moved_m')} minv {min(c[3] for c in mv)} {out.get('clamped')}")
code, out = w.pt.tool("move", C, {"m": -0.8, "client": C})
used = w.pt.p["reverse_used_m"]
code, out = w.pt.tool("move", C, {"m": -0.3, "client": C})
ok("reverse budget 1.0 m per patrol", used > 0.9 and (code == 409 and out["why"]["code"] == "reverse_budget"
   or abs(out.get("moved_m", 0)) < 0.12), f"used {used:.2f} -> {out.get('why') or out.get('moved_m')}")
w.ag.planner = planner
ok("non-patrol agent tools have no caps", w.ag.caps is None)
# keep-out goal and route
code, out = w.pt.tool("go_to", C, {"x": -5.9, "y": 1.6, "client": C})
ok("go_to into keep-out refused", code == 409 and out["why"]["code"] == "keep_out", out.get("why"))

# ---------------- refusals during a patrol (transient) ----------------
for setup, want, undo in [
    (lambda: setattr(w.mapper, "lost_since", time.time()), "loc_lost", lambda: setattr(w.mapper, "lost_since", None)),
    (lambda: setattr(w.mapper, "suspect_since", time.time()), "loc_suspect", lambda: setattr(w.mapper, "suspect_since", None)),
    (lambda: setattr(w.sim, "body_h", 0.10), "not_standing", lambda: setattr(w.sim, "body_h", 0.30)),
    (lambda: setattr(w.sim, "roll", 0.7), "fallen", lambda: setattr(w.sim, "roll", 0.0)),
    (lambda: setattr(w, "mot_age", 30), "motors_unknown", lambda: setattr(w, "mot_age", 1)),
]:
    setup(); time.sleep(0.3)
    code, out = w.pt.tool("move", C, {"m": 0.3, "client": C})
    ok(f"motion refused in patrol: {want}", code == 409 and out["why"]["code"] == want and "reason" in out, out.get("why"))
    undo(); time.sleep(0.3)
code, out = w.pt.tool("photo", C, {"client": C})
ok("photo still allowed", out.get("result") == "done", out.get("reason"))
code, out = w.pt.stop(C)
ok("stop: client_stop", code == 200 and out["summary"]["stop_reason"] == "client_stop" and
   json.load(open(os.path.join(pdir, "patrol.json")))["stop_reason"] == "client_stop")
ok("monitor sent only stop / lie (so far)", all(c[2] in ("stop", "action") for c in w.monitor_calls()), set(c[2] for c in w.monitor_calls()))
w.close()

# ---------------- sticky halts while a tool runs (battery, motor, time) ----------------
for name, setup in [("battery_low", lambda w: w.batt.update(soc=20)), ("motor_warm", lambda w: w.mot.update(level="warm", max=61)),
                    ("time_up", lambda w: w.pt.p.update(started_t=w.pt.p["started_t"] - 5 * 60))]:
    w = fresh(); fake_l515(w.pt)
    code, out = start(w)
    res = {}
    th = threading.Thread(target=lambda: res.update(r=w.pt.tool("move", C, {"m": 2.0, "client": C})))
    th.start(); time.sleep(1.5); setup(w); th.join(10)
    code, out = res["r"]
    ok(f"monitor stops a running move: {name}", out["result"] == "aborted" and out["stop_reason"] == name
       and out["why"]["code"] == name, f"{out.get('result')} {out.get('stop_reason')} moved {out.get('moved_m')}")
    code, out = w.pt.tool("move", C, {"m": 0.3, "client": C})
    ok(f"halted patrol refuses motion: {name}", code == 409 and out["why"]["code"] == name and w.pt.p["state"] == "halted")
    time.sleep(0.5)
    ok(f"{name}: stop and stand, no lie down", not [c for c in w.node.calls if c[2] == "action"] and w.sim.body_h > 0.2)
    code, out = w.pt.tool("posture", C, {"pose": "lie", "client": C})
    time.sleep(0.6)
    ok(f"{name}: lying down allowed; halted+lying ends the patrol", out.get("result") == "done" and w.pt.p["state"] == "ended"
       and w.pt.p["stop_reason"] == name, (out.get("result"), w.pt.p["state"], w.pt.p["stop_reason"]))
    w.close()

# ---------------- lease lapse -> stop + grace -> resume, then -> end ----------------
go2_agent.AGENT_LEASE_S = 1.0
go2_patrol.LEASE_GRACE_S = 2.0
w = fresh(); fake_l515(w.pt)
code, out = start(w)
n_stop0 = len([c for c in w.monitor_calls() if c[2] == "stop"])
time.sleep(1.6)
ok("lease lapse -> grace", w.pt.p["state"] == "grace", w.pt.p["state"])
ok("lease lapse -> monitor stopped the dog (and nothing else)", len([c for c in w.monitor_calls() if c[2] == "stop"]) > n_stop0
   and all(c[2] == "stop" for c in w.monitor_calls()))
env = w.pt.envelope_for(C)
ok("grace shown in envelope", env["state"] == "grace" and 0 < env["grace_left_s"] <= 2.0, env.get("grace_left_s"))
ok("other agents still blocked in grace", w.pt.blocks("other") is not None)
w.claim(); w.pt.touch(C)
time.sleep(0.3)
ok("same client resumes within grace", w.pt.p["state"] == "open", w.pt.p["state"])
code, out = w.pt.start(C, {"patrol_id": w.pt.p["patrol_id"]})
ok("start with same patrol_id = resume", code == 200 and out.get("resumed"))
time.sleep(1.4 + 2.4)
ok("grace over -> ended lease_lapsed", w.pt.p["state"] == "ended" and w.pt.p["stop_reason"] == "lease_lapsed", w.pt.p["stop_reason"])
ok("lease lapse: no lie down, no motion from monitor", all(c[2] == "stop" for c in w.monitor_calls()) and w.sim.body_h > 0.2)
go2_agent.AGENT_LEASE_S = 60.0
go2_patrol.LEASE_GRACE_S = 120.0
w.close()

# ---------------- stand budget -> lie down, end ----------------
go2_patrol.STAND_BUDGET_S = 4.0
go2_patrol.STAND_START_MIN_S = 1.0
w = fresh(); fake_l515(w.pt)
code, out = start(w)
ok("start for stand budget", code == 200, out.get("why"))
time.sleep(1.0)
w.claim(); w.pt.tool("move", C, {"m": 0.3, "client": C})     # walking resets the clock
s_after_walk = w.pt._standing_s()
ok("walking resets standing_s", s_after_walk < 1.0, s_after_walk)
for _ in range(60):
    w.claim(); time.sleep(0.1)
    if w.pt.p["state"] == "ended":
        break
lies = [c for c in w.monitor_calls() if c[2] == "action"]
ok("stand budget -> lie down + stand_budget", w.pt.p["stop_reason"] == "stand_budget" and lies and lies[-1][3] == "lie"
   and w.sim.body_h < 0.1, (w.pt.p["stop_reason"], lies))
ok("stand budget: monitor sent only stop / lie", all(c[2] in ("stop",) or c[2:] == ("action", "lie") for c in w.monitor_calls()))
w.close()

# after a lease_lapsed ending the stand budget still watches the dog
go2_agent.AGENT_LEASE_S = 0.5
go2_patrol.LEASE_GRACE_S = 0.5
go2_patrol.STAND_BUDGET_S = 3.0
w = fresh(); fake_l515(w.pt); start(w)
for _ in range(80):
    time.sleep(0.1)
    if w.sim.body_h < 0.1:
        break
ok("after lease_lapsed end, stand budget still lies the unattended dog down", w.pt.p["stop_reason"] == "lease_lapsed" and w.sim.body_h < 0.1,
   (w.pt.p["stop_reason"], w.sim.body_h))
w.close()
go2_agent.AGENT_LEASE_S = 60.0; go2_patrol.LEASE_GRACE_S = 120.0; go2_patrol.STAND_BUDGET_S = 600.0; go2_patrol.STAND_START_MIN_S = 120.0

# ---------------- human takeover ----------------
w = fresh(); fake_l515(w.pt); start(w)
res = {}
th = threading.Thread(target=lambda: res.update(r=w.pt.tool("move", C, {"m": 2.0, "client": C})))
th.start(); time.sleep(1.2)
w.ag.human_drives("console", "10.0.0.9")
th.join(10); time.sleep(0.4)
ok("human takeover aborts the tool", res["r"][1]["result"] == "aborted" and res["r"][1]["stop_reason"] == "person", res["r"][1].get("stop_reason"))
ok("human takeover ends the patrol", w.pt.p["state"] == "ended" and w.pt.p["stop_reason"] == "human_took_over")
ok("human takeover: monitor sent nothing", not w.monitor_calls(), w.monitor_calls())
w.ag.owner = None
w.claim()
code, out = w.pt.tool("move", C, {"m": 0.1, "client": C}) if w.pt.owns(C) else (None, None)
ok("after the end the client is no longer in the envelope", not w.pt.owns(C))
w.close()

# ---------------- deploying during a patrol ----------------
w = fresh(); fake_l515(w.pt); start(w)
w.deploying = {"msg": "deploy"}; time.sleep(0.5)
ok("deploying ends the patrol", w.pt.p["stop_reason"] == "deploying")
w.close()

# ---------------- console restart closes stale patrols ----------------
w = fresh(); fake_l515(w.pt); start(w)
pid = w.pt.p["patrol_id"]
p2 = go2_patrol.Patrols(w.ag, w.keepout, w.tmp, "lab", w.pt.hooks)
ok("stale open patrol closed at console start", json.load(open(os.path.join(w.tmp, "lab_patrols", pid, "patrol.json")))["stop_reason"] == "console_restart")
w.close()

print(f"\n{sum(r for _, r in RES)}/{len(RES)} passed")
