"""A record of the robot's state over the last hours, for working out afterwards why something went wrong
(cheetah's request, 10-25): pose, localization fit and lost flag, obstacle ranges, posture, who had control and
which agent call was running, once a second.

Kept in memory (KEEP_S) and appended to one JSONL file per day under /maps/<map>_history/, so it survives console
restarts; the last KEEP_S are reloaded at start. About 250 bytes a sample, ~1 MB an hour.

GET /history?keys=loc.track_fit,map_pose&since=<unix t>&until=<unix t>&step=<s>&limit=<n>
  keys: dotted names from KEYS (a prefix such as "map_pose" gives all of map_pose.*); default all.
  step: thin to at most one sample per step seconds. limit: at most this many samples (the newest), default 3600.
"""
import json
import os
import threading
import time
from collections import deque

PERIOD_S = 1.0
KEEP_S = 4 * 3600
HOST_UID = 1000
KEYS = ("odom.x", "odom.y", "odom.yaw", "map_pose.x", "map_pose.y", "map_pose.yaw",
        "loc.track_fit", "loc.lost", "loc.fit", "loc.seq", "obstacle", "body_height", "mode", "roll", "pitch",
        "owner", "owner_kind", "call", "battery", "markers", "age.odom", "age.cloud", "age.camera")


def _r(v, n=3):
    return None if v is None else round(float(v), n)


class History:
    def __init__(self, maps_dir, name, sample):
        """sample(): a flat dict with (some of) KEYS for this moment."""
        self.sample = sample
        self.dir = os.path.join(maps_dir, f"{name}_history")
        self.buf = deque(maxlen=int(KEEP_S / PERIOD_S) + 10)
        self.lock = threading.Lock()
        self._load()
        threading.Thread(target=self._run, daemon=True).start()

    def _file(self, t):
        return os.path.join(self.dir, time.strftime("%Y%m%d", time.localtime(t)) + ".jsonl")

    def _load(self):
        now = time.time()
        rows = []
        for t in (now - 86400, now):
            try:
                with open(self._file(t)) as f:
                    for line in f:
                        try:
                            d = json.loads(line)
                        except ValueError:
                            continue
                        if d.get("t", 0) >= now - KEEP_S:
                            rows.append(d)
            except OSError:
                pass
        rows.sort(key=lambda d: d["t"])
        self.buf.extend(rows)

    def _run(self):
        while True:
            t0 = time.time()
            try:
                d = {"t": round(t0, 2), **self.sample()}
                with self.lock:
                    self.buf.append(d)
                self._append(d)
            except Exception as e:          # never let the recorder take the console down
                print("history:", e, flush=True)
            time.sleep(max(0.05, PERIOD_S - (time.time() - t0)))

    def _append(self, d):
        try:
            if not os.path.isdir(self.dir):
                os.makedirs(self.dir, exist_ok=True)
                os.chown(self.dir, HOST_UID, HOST_UID)
            f = self._file(d["t"])
            new = not os.path.exists(f)
            with open(f, "a") as fh:
                fh.write(json.dumps(d) + "\n")
            if new:
                os.chown(f, HOST_UID, HOST_UID)
        except OSError:
            pass

    def get(self, keys=None, since=None, until=None, step=None, limit=3600):
        with self.lock:
            rows = list(self.buf)
        if since is not None:
            rows = [d for d in rows if d["t"] >= since]
        if until is not None:
            rows = [d for d in rows if d["t"] <= until]
        if step:
            out, last = [], -1e18
            for d in rows:
                if d["t"] - last >= step:
                    out.append(d)
                    last = d["t"]
            rows = out
        rows = rows[-max(1, int(limit)):]
        if keys:
            want = [k for k in KEYS if any(k == w or k.startswith(w + ".") for w in keys)]
            rows = [{"t": d["t"], **{k: d.get(k) for k in want}} for d in rows]
        else:
            want = list(KEYS)
        return {"keys": want, "period_s": PERIOD_S, "kept_s": KEEP_S, "n": len(rows), "samples": rows}


def sample_from(latest, lock, mapper, agents, markers, battery):
    """The sample() function for the console: reads its shared state."""
    def sample():
        with lock:
            now = time.time()
            odom, mp, st, imu = latest.get("odom"), latest.get("map_pose"), latest.get("state"), latest.get("imu")
            ages = {k: now - t for k, t in latest["stamps"].items()}
        li = mapper.loc_info(track_n=0) if mapper else {}
        o = agents.owner_now() if agents else None
        cur = agents.current if agents else None
        b = battery() if battery else None
        mk = markers.snapshot()["list"] if markers else []
        return {"odom.x": _r(odom and odom["pos"][0]), "odom.y": _r(odom and odom["pos"][1]),
                "odom.yaw": _r(odom and odom["yaw"]),
                "map_pose.x": _r(mp and mp["x"]), "map_pose.y": _r(mp and mp["y"]), "map_pose.yaw": _r(mp and mp["yaw"]),
                "loc.track_fit": li.get("track_fit"), "loc.lost": li.get("lost"), "loc.fit": li.get("fit"),
                "loc.seq": li.get("seq"),
                "obstacle": st and st.get("obstacle"), "body_height": _r(st and st.get("body_height")),
                "mode": st and st.get("mode"),
                "roll": _r(imu and imu["rpy"][0]), "pitch": _r(imu and imu["rpy"][1]),
                "owner": o and o.get("client"), "owner_kind": o and o.get("kind"),
                "call": cur and cur.get("call"),
                "battery": b and b.get("soc"),
                "markers": [m.get("mark", m.get("id")) for m in mk] or None,
                "age.odom": _r(ages.get("odom"), 2), "age.cloud": _r(ages.get("cloud"), 2),
                "age.camera": _r(ages.get("camera"), 2)}
    return sample
