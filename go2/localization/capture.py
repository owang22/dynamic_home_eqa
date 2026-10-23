"""Passive camera + pose logger for the localization tests, 2026-10-23. Read-only: GETs /frame.jpg and /state.json
from the console, never /agent/* or a POST, so it cannot move the dog or take control.

    python3 go2/localization/capture.py [--hz 1] [--name 2026-10-23_tests]   # Ctrl-C to stop
    python3 go2/localization/capture.py --mark A1        # from another shell: note "dog is on mark A1 now"

Writes go2/data/localization_runs/<name>/: frames/<ms>.jpg and poses.jsonl, one line per frame with the map pose,
odom, IMU attitude, the console's line-up state (loc) and the newest drift-correction attempt. --mark appends a
{"mark": ...} line with the time, so test steps (still test start, on mark A, survey walk) can be found offline.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.request
from pathlib import Path

BASE = "http://172.17.40.64:8080"
DATA = Path(__file__).resolve().parents[1] / "data" / "localization_runs"


def get(path, timeout=3):
    with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hz", type=float, default=1.0)
    ap.add_argument("--name", default=time.strftime("%Y-%m-%d_tests"))
    ap.add_argument("--mark", help="append a marker line and exit")
    a = ap.parse_args()
    out = DATA / a.name
    (out / "frames").mkdir(parents=True, exist_ok=True)
    log = out / "poses.jsonl"
    if a.mark:
        with log.open("a") as f:
            f.write(json.dumps({"t": round(time.time(), 3), "mark": a.mark}) + "\n")
        print(f"marked {a.mark}")
        return
    print(f"logging to {out} at {a.hz} Hz", flush=True)
    n, fails = 0, 0
    while True:
        t0 = time.time()
        try:
            s = json.loads(get("/state.json"))
            jpg = get("/frame.jpg")
            t = time.time()
            name = f"{int(t * 1000)}.jpg"
            (out / "frames" / name).write_bytes(jpg)
            loc = s.get("loc") or {}
            m = s.get("map") or {}
            row = {"t": round(t, 3), "frame": name, "map_pose": s.get("map_pose"), "odom": s.get("odom"),
                   "rpy": (s.get("imu") or {}).get("rpy"), "gyro": (s.get("imu") or {}).get("gyro"),
                   "look_deg": (s.get("control") or {}).get("look_deg"), "map_mode": m.get("mode"),
                   "loc": {k: loc.get(k) for k in ("seq", "status", "fit", "runner_up", "unsure")},
                   "track": (loc.get("track") or [None])[-1] if isinstance(loc.get("track"), list) else loc.get("track"),
                   "age": s.get("age")}
            with log.open("a") as f:
                f.write(json.dumps(row) + "\n")
            n, fails = n + 1, 0
            if n % 60 == 0:
                print(f"{time.strftime('%H:%M:%S')} {n} frames", flush=True)
        except Exception as e:  # noqa: BLE001  console restarts or the dog drops off Wi-Fi: keep trying
            fails += 1
            if fails in (1, 10) or fails % 60 == 0:
                print(f"{time.strftime('%H:%M:%S')} console not answering ({fails}): {e}", flush=True)
        time.sleep(max(0.0, 1 / a.hz - (time.time() - t0)))


if __name__ == "__main__":
    main()
