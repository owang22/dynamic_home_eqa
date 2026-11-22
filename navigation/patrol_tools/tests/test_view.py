"""Step-3 offline tests through the console's real HTTP handler code (go2_dashboard.Handler with fake sockets):
/agent/patrol/start, /agent/view, /agent/patrol/stop, GET /patrols, /patrol/<id>, /patrol/<id>/<file>, refusals."""
import base64, io, json, math, os, sys, threading, time
sys.path.insert(0, "/tmp/s3test")
import numpy as np, cv2
import harness as H
from harness import World, fake_l515
import go2_patrol
import go2_dashboard as D          # module import only: no rclpy.init, no node, no publishers

RES = []
def ok(name, cond, info=""):
    RES.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (f"  [{info}]" if info else ""), flush=True)

C = "cheetah-patrol"
w = World()
D.AG, D.PATROLS, D.MAPPER, D.KEEPOUT, D.NODE, D.MARKERS, D.DEPLOYING = w.ag, w.pt, w.mapper, w.keepout, w.node, None, None


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

    def json(self): return json.loads(self.wfile.getvalue() or b"null")
    def body(self): return self.wfile.getvalue()


def post(path, body): return FH(path, body)
def get(path): return FH(path, method="GET")

stop_feed = threading.Event()
def feed():
    while not stop_feed.is_set():
        fake_l515(w.pt); time.sleep(0.12)
threading.Thread(target=feed, daemon=True).start()
time.sleep(0.4)

# refusals before a patrol
r = post("/agent/view", {"client": C, "x": 1.0, "y": 0.0, "yaw_deg": 0})
ok("view outside a patrol refused: no_patrol", r.code == 409 and r.json()["why"]["code"] == "no_patrol", r.json().get("why"))
w.ag.human_drives("console", "10.0.0.9")
r = post("/agent/patrol/start", {"client": C})
ok("patrol/start refused while a person has control", r.code == 409 and r.json()["why"]["code"] == "human_has_control", r.json())
w.ag.owner = None
D.DEPLOYING = {"msg": "deploy", "t": 1}
r = post("/agent/patrol/start", {"client": C})
ok("patrol/start refused while deploying (503)", r.code == 503 and r.json()["stop_reason"] == "deploying")
D.DEPLOYING = None

# start
r = post("/agent/patrol/start", {"client": C, "max_min": 10, "speed": "slow"})
out = r.json(); pid = out.get("patrol_id")
ok("patrol/start via console", r.code == 200 and pid and out.get("envelope", {}).get("patrol_id") == pid, out.get("why"))
r = post("/agent/claim", {"client": "ask-the-dog"})
ok("other agent claim refused: patrol_open", r.code == 409 and r.json()["why"]["code"] == "patrol_open")
n0 = len(w.node.calls)
r = post("/cmd", {"client": "ask-the-dog", "move": [0.3, 0, 0]})
ok("raw /cmd motion from agents refused during a patrol", r.code == 409 and not [c for c in w.node.calls[n0:] if c[2] == "move"], r.err)
r = post("/cmd", {"client": C, "move": [0.3, 0, 0]})
ok("raw /cmd motion from the patrol client refused too", r.code == 409)
r = post("/agent/status", {"client": C})
ok("status reply carries the envelope", r.code == 200 and r.json()["envelope"]["patrol_id"] == pid)
n0 = len(w.node.calls)
r = post("/agent/move", {"client": C, "m": 0.4})
mv = [c for c in w.node.calls[n0:] if c[2] == "move"]
ok("/agent/move goes through the envelope (0.3 m/s cap, envelope in reply)", r.code == 200 and r.json()["result"] == "done"
   and max(c[3] for c in mv) <= 0.3001 and "envelope" in r.json(), (r.json().get("result"), max(c[3] for c in mv)))
r = post("/agent/view", {"client": C, "x": -5.9, "y": 1.6, "yaw_deg": 0})
ok("view into keep-out refused", r.code == 409 and r.json()["why"]["code"] == "keep_out" and "reason" in r.json())
r = post("/agent/view", {"client": C, "x": 1.0})
ok("view bad arguments -> 400", r.code == 400)

# pick a goal ~1 m away on open floor
mp = w.ag.map_pose_now()
cands = [{"x": mp["x"] + d * math.cos(a), "y": mp["y"] + d * math.sin(a)} for d in (1.0, 0.8, 1.2) for a in np.radians(np.arange(0, 360, 30))]
code, chk = go2_patrol.check(cands, w.ag, w.keepout)
goal = next(c for c, rr in zip(cands, chk["results"]) if rr["ok"] and 0.6 < rr["route_m"] < 1.6 and rr["snapped_m"] < 0.1)
print("goal", goal, flush=True)
w.markers = {"list": [{"id": 0, "mark": "A", "z": 2.1, "bearing_deg": 3.0}]}
t0 = time.time()
_need = go2_patrol.TURN_NEED_M
go2_patrol.TURN_NEED_M = 9.9                 # any stand is too tight: 2 headings must be refused up front
r = post("/agent/view", {"client": C, "x": goal["x"], "y": goal["y"], "yaw_deg": [0, 90]})
ok("tight stand: multi-heading view refused (turn_clearance)", r.code == 409 and r.json()["why"]["code"] == "turn_clearance", r.json())
go2_patrol.TURN_NEED_M = 0.0                 # the fixture stand is 0.32 m; test the view mechanics regardless
r = post("/agent/view", {"client": C, "x": goal["x"], "y": goal["y"], "yaw_deg": [0, 90], "look_deg": 10, "settle_s": 0.5})
v = r.json()
print("view took", round(time.time() - t0, 1), "s; result", v.get("result"), v.get("reason"), flush=True)
ok("view done", r.code == 200 and v["result"] == "done", (v.get("result"), v.get("reason"), v.get("stop_reason")))
vdir = os.path.join(w.tmp, "lab_patrols", pid, "views", v["view_id"])
ok("two shots", len(v["shots"]) == 2 and [s["yaw_deg"] for s in v["shots"]] == [0, 90])
for i, s in enumerate(v["shots"]):
    ok(f"shot {i}: files on disk", set(s["files"]) == {"dog", "l515_color", "l515_depth"} and
       all(os.path.exists(os.path.join(vdir, f)) for f in s["files"].values()), s["files"])
    dog = cv2.imread(os.path.join(vdir, s["files"]["dog"]))
    ok(f"shot {i}: full-size dog JPEG", dog is not None and dog.shape[:2] == (720, 1280) and s["dog"]["width"] == 1280)
    dep = cv2.imread(os.path.join(vdir, s["files"]["l515_depth"]), cv2.IMREAD_UNCHANGED)
    ok(f"shot {i}: raw 16-bit depth PNG", dep is not None and dep.dtype == np.uint16 and dep.shape == (240, 320)
       and int(dep[10, 10]) == (10 * 320 + 10) % 4000)
    l = s["l515"]
    ok(f"shot {i}: L515 infos + timestamps", l and l["depth_info"]["k"][0] == 300.0 and l["color_info"]["width"] == 640
       and l["depth_stamp"] and l["color_stamp"] == l["depth_stamp"] and abs(l["dt_to_dog_s"]) <= 0.6, {k: l.get(k) for k in ("depth_stamp", "color_stamp", "dt_to_dog_s")})
    ok(f"shot {i}: pose + loc", s["pose"] and set(s["loc"]) == {"map_id", "track_fit", "fresh_fit", "lost", "suspect"}, s["loc"])
    ok(f"shot {i}: marker sighting", s["markers"]["list"] and s["markers"]["list"][0]["mark"] == "A")
    ok(f"shot {i}: look/pitch/still", s["look_deg"] == 10 and s["body_pitch_deg"] is not None and s["look_held"] is True
       and s["still"] is True, {k: s.get(k) for k in ("look_deg", "look_deg_cmd", "body_pitch_deg", "body_pitch_before_deg", "look_pitch_change_deg", "look_held", "still")})
mp = w.ag.map_pose_now()
ok("faced the last heading", abs(go2_patrol.wrap_deg(math.degrees(mp["yaw"]) - 90)) < 8, round(math.degrees(mp["yaw"]), 1))
ok("timing keys", set(v["timing"]) == {"plan_s", "walk_s", "face_s", "settle_s", "photo_s"} and v["timing"]["walk_s"] > 1
   and v["timing"]["settle_s"] >= 1.0, v["timing"])
ok("walked_m, battery_end, hottest_motor_c_end, stop_reason", v["walked_m"] > 0.5 and v["battery_end"] == 80
   and v["hottest_motor_c_end"] == 40 and v["stop_reason"] == "done", (v["walked_m"], v["stop_reason"]))
ok("view reply envelope", set(["patrol_id", "time_left_s", "battery", "hottest_motor_c", "motor_level", "standing_s",
                                "stand_budget_s", "reverse_used_m", "loc"]) <= set(v["envelope"]))
ok("look re-sent during settle and levelled after", any(c[2] == "send_head" for c in w.node.calls) and
   [c for c in w.node.calls if c[2] == "look"][-1][3] == 0.0)
vj = json.load(open(os.path.join(vdir, "view.json")))
ok("view.json has the same content", vj["view_id"] == v["view_id"] and len(vj["shots"]) == 2 and vj["timing"] == v["timing"])
ok("view caps recorded", vj["caps"]["v"] == 0.3)
# URLs
for s in v["shots"]:
    for k, u in s["urls"].items():
        g = get(u)
        ok(f"GET {u.split('/')[-1]}", g.code == 200 and g.body() == open(os.path.join(vdir, s["files"][k]), "rb").read()
           and g.hdrs.get("Content-Type") == go2_patrol.FILE_TYPES[os.path.splitext(u)[1]])
g = get(v["urls"]["view_json"]); ok("GET view.json", g.code == 200 and g.json()["view_id"] == v["view_id"])
g = get(f"/patrol/{pid}"); pj = g.json()
ok("GET /patrol/<id>: patrol.json + views", g.code == 200 and pj["patrol_id"] == pid and len(pj["views"]) == 1
   and pj["views"][0]["headings"] == [0, 90] and "envelope" in pj)
g = get("/patrols"); ok("GET /patrols lists it", g.code == 200 and any(p["patrol_id"] == pid for p in g.json()["patrols"]))
mc = pj["mount_check"]
ok("mount check URLs served", all(get(u).code == 200 for u in mc["urls"].values()), list(mc["urls"]))

# second view: look springs back, L515 off, inline
w.sim.look_holds = False
stop_feed.set(); time.sleep(1.0)
r = post("/agent/view", {"client": C, "x": goal["x"], "y": goal["y"], "yaw_deg": 45, "look_deg": -8, "settle_s": 0.3, "inline": True})
v2 = r.json()
s = v2["shots"][0] if v2.get("shots") else {}
ok("view 2 done (already there: no walk)", r.code == 200 and v2["result"] == "done", (v2.get("result"), v2.get("reason")))
ok("look springing back is flagged look_held=false", s.get("look_held") is False, {k: s.get(k) for k in ("look_pitch_change_deg", "look_held")})
ok("L515 offline -> l515 null, no L515 files", s.get("l515") is None and set(s.get("files", {})) == {"dog"})
ok("inline base64 only when asked", base64.b64decode(s["inline"]["dog"])[:2] == b"\xff\xd8" and "inline" not in v["shots"][0])

# path validation (GET /patrol/<id>/...)
vid = v["view_id"]
os.symlink("/etc/passwd", os.path.join(vdir, "leak.json"))
bad = [f"/patrol/{pid}/../patrol.json", f"/patrol/{pid}/views/../../../../etc/passwd", f"/patrol/{pid}/views/{vid}/../../../x.json",
       f"/patrol/..%2f..%2fetc/passwd", f"/patrol/{pid}/%2e%2e/patrol.json", f"/patrol/{pid}/.patrol.json",
       f"/patrol/{pid}/views/{vid}/view.py", f"/patrol/{pid}//etc/passwd", f"/patrol/{pid}/views/{vid}/leak.json",
       f"/patrol/p_20261121_000000/patrol.json", f"/patrol/../maps/lab.places.json", f"/patrol/{pid}/a/b/c/d.json",
       f"/patrol/{pid}/views\\..\\patrol.json", "/patrol/check", "/patrol/x"]
for b in bad:
    g = get(b)
    ok(f"rejected: {b[len('/patrol/'):][:60]}", g.code == 404, g.code)
ok("patrol_file unit: absolute rel / traversal / NUL", all(go2_patrol.patrol_file(os.path.join(w.tmp, "lab_patrols"), pid, r) is None
   for r in ("/etc/passwd", "..", "views/..", "patrol.json\x00.jpg", "", "views/" + vid + "/h0_dog.jpg/..")))
ok("GET /patrol/<id>/patrol.json allowed", get(f"/patrol/{pid}/patrol.json").code == 200)

# deploying: view refused (503), patrol/stop still allowed
D.DEPLOYING = {"msg": "deploy", "t": 1}
r = post("/agent/view", {"client": C, "x": goal["x"], "y": goal["y"], "yaw_deg": 0})
ok("view refused while deploying", r.code == 503)
D.DEPLOYING = None
r = post("/agent/patrol/stop", {"client": "someone-else"})
ok("patrol/stop by another client refused", r.code == 409)
r = post("/agent/patrol/stop", {"client": C})
ok("patrol/stop", r.code == 200 and r.json()["summary"]["stop_reason"] == "client_stop" and r.json()["summary"]["n_views"] == 2
   and r.json()["envelope"]["state"] == "ended", r.json().get("summary"))
pj = json.load(open(os.path.join(w.tmp, "lab_patrols", pid, "patrol.json")))
ok("patrol.json summary", pj["summary"]["stop_reason"] == "client_stop" and pj["state"] == "ended" and pj["walked_m"] > 0.5, pj["summary"])
ok("brief for the header", w.pt.brief()["state"] == "ended" and w.pt.brief()["stop_reason"] == "client_stop")
r = post("/agent/claim", {"client": "ask-the-dog"})
ok("after the patrol the client still holds its ordinary lease", r.code == 409 and "cheetah-patrol" in r.json()["reason"])
post("/agent/release", {"client": C})
r = post("/agent/claim", {"client": "ask-the-dog"})
ok("after release other agents may claim again", r.code == 200)
ok("monitor only ever sent stop / lie", all(c[2] == "stop" or c[2:] == ("action", "lie") for c in w.monitor_calls()),
   set(c[2] for c in w.monitor_calls()))
print(f"\n{sum(r for _, r in RES)}/{len(RES)} passed")
