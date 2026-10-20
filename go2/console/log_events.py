"""Log the console's /events stream on cheetah, only while the dog is on (read-only; sends nothing to the dog).

    python3 go2/console/log_events.py          # runs until stopped; go2/console/go2-logger.service runs it for you

While the dog is off it only checks, once every 30 s, by reading one event from the console. The dog counts as on
when odometry is present and less than 2 s old in two checks in a row. It then streams /events into a new file per
session, and closes that file when odometry has been missing or stale for 60 s.

Writes go2/data/event_logs/<YYYY-MM-DD_HHMMSS>.jsonl.gz, one JSON object per line:
    {"t": unix time received, "odom": ..., "map_pose": ..., "age": ..., "rec": console recording on?}
    plus "cloud": {...}  on the first event that carries a new lidar grid (about 1-2 per second)
The grid is the console's: cells 0.1 m, in the odom frame, within 8 m of the dog.
"""
from __future__ import annotations

import gzip
import json
import os
import signal
import sys
import time
import urllib.request
from pathlib import Path

BASE = os.environ.get("GO2_CONSOLE", "http://172.17.40.64:8080")
OUT_DIR = Path(os.environ.get("GO2_EVENT_LOGS", Path(__file__).resolve().parents[1] / "data" / "event_logs"))
_FAST = os.environ.get("GO2_LOGGER_FAST") == "1"  # tests only: seconds instead of tens of seconds
CHECK_EVERY_S = 1 if _FAST else 30      # while the dog is off
CONSOLE_DOWN_WAIT_S = 1 if _FAST else 60
END_AFTER_STALE_S = 3 if _FAST else 60  # close the session file after this long without fresh odometry
FRESH_S = 2.0


class Stop(Exception):
    pass


def _stop(*_):
    raise Stop


def log(msg):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}", flush=True)


def live(e: dict) -> bool:
    age = (e.get("age") or {}).get("odom")
    return e.get("odom") is not None and age is not None and age < FRESH_S


def events(timeout=10):
    with urllib.request.urlopen(BASE + "/events", timeout=timeout) as r:
        for line in r:
            if line.startswith(b"data:"):
                yield json.loads(line[5:])


def one_event() -> dict | None:
    """One event from the console, or None if it cannot be reached."""
    try:
        return next(events(timeout=5))
    except Exception:  # noqa: BLE001 - console down, network blip, restart
        return None


def record_session() -> None:
    """Stream into one file until the odometry has been stale for END_AFTER_STALE_S, or the stream fails."""
    path = OUT_DIR / (time.strftime("%Y-%m-%d_%H%M%S") + ".jsonl.gz")
    n = clouds = 0
    last_cloud, last_live = None, time.monotonic()
    log(f"dog is on: logging to {path.name}")
    try:
        with gzip.open(path, "wt") as f:  # closed properly on stop, so the file is always complete
            for e in events():
                now = time.monotonic()
                if not live(e):
                    if now - last_live > END_AFTER_STALE_S:
                        break
                    continue
                last_live = now
                rec = {"t": round(time.time(), 3), "odom": e.get("odom"), "map_pose": e.get("map_pose"),
                       "age": e.get("age"), "rec": (e.get("rec") or {}).get("running")}
                c = e.get("cloud")
                key = (c or {}).get("n_total"), len((c or {}).get("obs", []))
                if c and key != last_cloud:
                    rec["cloud"], last_cloud = c, key
                    clouds += 1
                f.write(json.dumps(rec) + "\n")
                n += 1
                if n % 600 == 0:
                    f.flush()
                    log(f"{n} records, {clouds} lidar grids")
    except Stop:
        raise
    except Exception as ex:  # noqa: BLE001 - stream dropped; the main loop decides what next
        log(f"stream dropped ({ex})")
    finally:
        if n == 0:
            path.unlink(missing_ok=True)
        log(f"session closed: {n} records, {clouds} lidar grids" + ("" if n else " (empty file removed)"))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    signal.signal(signal.SIGTERM, _stop)
    log("watching for the dog (checks every 30 s while it is off)")
    state, seen_live = None, 0
    try:
        while True:
            e = one_event()
            if e is None:
                if state != "console down":
                    log(f"console not answering at {BASE}")
                    state = "console down"
                time.sleep(CONSOLE_DOWN_WAIT_S)
                continue
            seen_live = seen_live + 1 if live(e) else 0
            if seen_live >= 2:
                record_session()
                state, seen_live = None, 0
                continue
            if state != "off" and not seen_live:
                log("dog is off (no fresh odometry)")
                state = "off"
            time.sleep(CHECK_EVERY_S if not seen_live else 2)
    except (Stop, KeyboardInterrupt):
        log("stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
