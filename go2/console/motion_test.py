"""First motion test from cheetah through the lab console (control PC, 172.17.40.64:8080):
turn ~30 deg left, turn back, back up 0.2 m, stop. Run 2026-10-14 with a person next to the dog.
Closed loop on odometry from /events; every move has its own time limit; any error sends stop.
    python3 go2/console/motion_test.py [--check-only]
The console answers 204 on success. Below about 0.6 rad/s the dog does not step, so turns barely happen.
"""
import json, math, sys, threading, time, urllib.request, urllib.error
from pathlib import Path

BASE = "http://172.17.40.64:8080"
CLIENT = "cheetah"
OUT = Path(__file__).resolve().parents[1] / "data" / "motion_tests" / time.strftime("%Y-%m-%d_%H%M")
OUT.mkdir(parents=True, exist_ok=True)
last = {"ev": None, "t": 0.0}


def reader():
    with urllib.request.urlopen(BASE + "/events", timeout=10) as r:
        for line in r:
            if line.startswith(b"data:"):
                last["ev"], last["t"] = json.loads(line[5:]), time.monotonic()


def ev():
    if time.monotonic() - last["t"] > 1.0:
        raise RuntimeError("events stale (>1 s)")
    return last["ev"]


def cmd(body):
    body = dict(body, client=CLIENT)
    req = urllib.request.Request(BASE + "/cmd", json.dumps(body).encode(), {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=2) as r:
            return r.status, r.read().decode()[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]


def frame(name):
    with urllib.request.urlopen(BASE + "/frame.jpg", timeout=5) as r:
        (OUT / name).write_bytes(r.read())
        return float(r.headers.get("X-Frame-Age", "nan"))


def pose():
    e = ev()
    o, m = e["odom"], e.get("map_pose")
    return {"odom": [o["pos"][0], o["pos"][1], o["yaw"]], "map": [m["x"], m["y"], m["yaw"]] if m else None}


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def drive(vx, wz, done, limit_s):
    """Resend the move every 0.1 s until done(pose) or the time limit; returns why it ended."""
    t0 = time.monotonic()
    while True:
        if done(pose()):
            return "reached"
        if time.monotonic() - t0 > limit_s:
            return "time limit"
        st, txt = cmd({"move": [vx, 0.0, wz]})
        if not 200 <= st < 300:
            return f"cmd refused {st}: {txt}"
        time.sleep(0.1)


def main():
    threading.Thread(target=reader, daemon=True).start()
    for _ in range(30):
        if last["ev"]:
            break
        time.sleep(0.1)
    e = ev()
    log = {"start_age": e["age"], "control": e["control"], "state": e["state"]}
    print("ages", e["age"]); print("control", e["control"]); print("state", e["state"])
    limits = {"odom": 1.0, "state": 1.0, "camera": 1.0, "cloud": 3.0}  # cloud updates ~1 Hz
    stale = {k: e["age"].get(k) for k in limits if e["age"].get(k) is None or e["age"][k] > limits[k]}
    if stale:
        sys.exit(f"stale sensors {stale}: not moving")
    if e["control"].get("driver") not in (None, CLIENT):
        sys.exit(f"someone else is driving: {e['control']}")
    if "--check-only" in sys.argv:
        return
    log["before"] = pose(); log["before_frame_age"] = frame("before.jpg")
    try:
        log["avoid"] = cmd({"avoid": True}); print("avoid", log["avoid"])
        log["stand"] = cmd({"action": "stand"}); print("stand", log["stand"])
        time.sleep(2.0)
        y0 = pose()["odom"][2]
        log["turn"] = drive(0.0, 0.4, lambda p: abs(wrap(p["odom"][2] - y0)) >= math.radians(28), 4.0)
        print("turn", log["turn"])
        cmd({"action": "stop"}); time.sleep(1.5)
        log["after_turn"] = pose()
        y1 = pose()["odom"][2]
        log["turn_back"] = drive(0.0, -0.4, lambda p: abs(wrap(p["odom"][2] - y1)) >= math.radians(28), 4.0)
        print("turn back", log["turn_back"])
        cmd({"action": "stop"}); time.sleep(1.5)
        log["after_turn_back"] = pose()
        x0, yy0 = pose()["odom"][:2]
        log["forward"] = drive(-0.15, 0.0, lambda p: math.hypot(p["odom"][0] - x0, p["odom"][1] - yy0) >= 0.18, 4.0)  # backward 0.2 m: a person sits in front
        print("forward", log["forward"])
    finally:
        log["stop"] = cmd({"action": "stop"}); print("stop", log["stop"])
    time.sleep(1.5)
    log["after"] = pose(); log["after_frame_age"] = frame("after.jpg"); log["end_state"] = ev()["state"]
    b, t, a = log["before"]["odom"], log["after_turn"]["odom"], log["after"]["odom"]
    log["turned_deg"] = round(math.degrees(wrap(t[2] - b[2])), 1)
    tb = log["after_turn_back"]["odom"]
    log["turned_back_deg"] = round(math.degrees(wrap(tb[2] - t[2])), 1)
    log["forward_m"] = round(math.hypot(a[0] - tb[0], a[1] - tb[1]), 3)
    log["heading_change_while_forward_deg"] = round(math.degrees(wrap(a[2] - tb[2])), 1)
    if log["before"]["map"] and log["after"]["map"]:
        bm, am = log["before"]["map"], log["after"]["map"]
        log["map_moved_m"] = round(math.hypot(am[0] - bm[0], am[1] - bm[1]), 3)
        log["map_turned_deg"] = round(math.degrees(wrap(am[2] - bm[2])), 1)
    (OUT / "log.json").write_text(json.dumps(log, indent=1))
    print(json.dumps({k: log[k] for k in log if k not in ("start_age", "state", "end_state")}, indent=1))


if __name__ == "__main__":
    main()
