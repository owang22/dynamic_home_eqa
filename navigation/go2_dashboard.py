#!/usr/bin/env python3
"""Live Go2 sensor dashboard with drive controls, served over HTTP.

Drive controls accept requests from this machine and the lab subnet (CONTROL_NETS).
One person drives at a time; anyone can press Stop.
Recordings (ROS 2 bags) go to /recordings, mounted from ~/oliver/go2_recordings on the host.

Run inside the driver container:  python3 /root/go2_dashboard.py [port]
Then open http://localhost:8080 on this machine (or http://<this-machine-ip>:8080).
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "2")        # numpy's thread pools otherwise grab every core
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
import array
import atexit
import ipaddress
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.parse
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2
import numpy as np
import rclpy
from geometry_msgs.msg import Twist
from go2_interfaces.msg import IMU, Go2State, WebRtcReq
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, CompressedImage, Image, JointState, PointCloud2
from std_msgs.msg import String
from sensor_msgs_py import point_cloud2

from go2_agent import AGENT_LEASE_S, BUMP_H, UNDER_TOP_MAX, Agents, check_name
from go2_mapper import CLICK_MARKER_R, HINT_YAW_TOL, Mapper, marker_lineup_pose, wrap
from go2_nav import Planner
from go2_trail import Trail
from go2_markers import Markers
from go2_marker_table import MarkerTable
from go2_examples import Examples
from go2_history import History, sample_from
import go2_patrol

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
CELL = 0.1            # metres per grid cell in the top view
OBSTACLE_MIN_H = 0.1  # cell counts as obstacle if its top is this far above the floor
MAP_MAX_TURN = 0.15   # rad/s; clouds taken while turning faster than this don't go on the map
CLOUD_RADIUS = 8.0   # metres around the robot shown in the top view

SPORT_TOPIC = "rt/api/sport/request"
AVOID_TOPIC = "rt/api/obstacles_avoid/request"
# obstacles_avoid service API ids (unitree_sdk2 ObstaclesAvoidClient)
AVOID_SWITCH_SET, AVOID_MOVE, AVOID_USE_API = 1001, 1003, 1004
CONTROL_NETS = [ipaddress.ip_network(n) for n in ("127.0.0.0/8", "172.17.0.0/18")]  # localhost + lab Wi-Fi/LAN
DRIVER_HOLD_S = 3.0        # a driver keeps control this long after their last command
CMD = {"StopMove": 1003, "StandUp": 1004, "StandDown": 1005, "BalanceStand": 1002, "Euler": 1007}
HEAD_MAX = math.radians(30)   # how far the body may tilt to point the camera up or down
UP_SIGN = -1                  # Euler pitch sign that raises the nose: untested on the dog, flip if Look up looks down
ACTIONS = {"stop": [], "stand": ["StandUp", "BalanceStand"], "lie": ["StandDown"]}
LIMITS = (0.6, 0.3, 1.0)   # max vx, vy (m/s), yaw rate (rad/s). Below ~0.3 m/s the Go2 shuffles (gait recording, 10-22)
# The console's speed setting caps everyone, people and agents (Oliver, 10-23: agent runs were too fast and
# aggressive at 0.5 m/s). Slow is the default; the setting survives console restarts.
SPEEDS = {"slow": (0.3, 0.2, 0.5), "normal": (0.5, 0.25, 0.8), "fast": LIMITS}
SPEED_FILE = "/maps/console_speed.txt"
DEADMAN_S = 0.3            # stop if the browser stops sending moves for this long
BACK_MAX = 0.25            # m/s backwards for everyone: the dog barely sees behind itself
AVOID_DEFAULT = True       # the dog's obstacle avoidance starts on; agent motions rely on it
NODE = None
# Deploys (deploy_console.sh): POST /deploying stops the dog and refuses all motion until this process ends; the page
# shows an overlay and reloads itself when it sees a new BOOT_ID. The driver has no command timeout and the dog keeps
# the last obstacle-avoid Move velocity, so the console must stop the dog itself before it goes away (stop_dog).
DEPLOYING = None           # {"t", "msg"} while a deploy is under way
BOOT_ID = f"{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"
WATCHDOG = None           # last POST /watchdog from ~/oliver/go2_watchdog.py (host): {dog, for_s, ..., last_action, received_t}
DOG_ST = {"state": None, "since": 0.0, "active_t": 0.0}
DOG_OFF_S = 10.0          # odom older than this: the dog is off (same rule as go2_watchdog.py)
DOG_IDLE_S = 30.0         # no motion, posture change or command for this long: idle
MOTION_AGENT_CALLS = ("claim", "move", "turn", "look_around", "go_to", "look", "posture", "relocalize", "patrol/start", "view")
AG = None                  # agent tools and who has control (go2_agent.py)
MAPPER = None              # lab map built from the lidar clouds (go2_mapper.py)
EXAMPLES = None            # objects labelled by example from camera frames (go2_examples.py)
HIST = None                # state once a second over the last hours (go2_history.py)
MARKERS = None             # printed ArUco markers in view (go2_markers.py)
MARKER_TABLE = None        # where they are on the map (go2_marker_table.py): re-anchors the pose
TRAIL = None               # camera frames along the way, with map poses (go2_trail.py)
AGENT_CALLS = ("claim", "release", "stop", "say", "status", "move", "turn", "photo", "look_around", "go_to", "look",
               "posture", "relocalize", "patrol/start", "patrol/stop", "view")
PATROLS = None             # patrol envelope, monitor and patrol files (go2_patrol.Patrols)
PRIOR_DIR = os.path.join("/maps", f"{os.environ.get('MAP_NAME', 'lab')}_prior")   # Oliver's driving prior (11-21)

REC_DIR = "/recordings"
REC_TOPICS = {"camera": ["/camera/image_raw", "/camera/camera_info"],
              "lidar": ["/point_cloud2"],
              "pose": ["/odom", "/imu", "/tf", "/tf_static", "/joint_states", "/go2_states",
                       "/go2/motor_temps"],     # motor temperatures (patch_driver_motor_temps.sh; absent without it)
              # RealSense L515 on the dog (l515_go2_pi4_bridge receiver, may be off). Colour as the Pi's JPEG, depth
              # as raw 16-bit mm; /go2/l515/points and the raw colour image are left out (rebuilt from these).
              "l515": ["/go2/l515/color/image_raw/compressed", "/go2/l515/color/camera_info",
                       "/go2/l515/depth/image_raw", "/go2/l515/depth/camera_info"]}
L515_URL = os.environ.get("GO2_L515_URL", "http://127.0.0.1:8081")   # the bridge's page: frames + status.json
AGENT_CHAT_URL = os.environ.get("GO2_AGENT_CHAT_URL", "http://127.0.0.1:8091")   # go2_agent_chat.py on the host
L515_VIEW_HZ = 4.0         # console L515 panel refresh while someone is looking at it
REC_MIN_FREE_GB = 20       # refuse to start below this, stop automatically below half of it
HOST_UID = 1000            # recordings are handed to the host user when they finish

# Automatic run recording (AutoRecorder below): every session with the dog is saved, whoever sets it up.
# Off switch: GO2_AUTO_REC=0 in the container's environment (or `docker exec -e`), default on.
AUTO_REC = os.environ.get("GO2_AUTO_REC", "1").strip().lower() not in ("0", "false", "off", "no")
AUTO_REC_IDLE_S = float(os.environ.get("GO2_AUTO_REC_IDLE_S", 240))  # no motion and no commands this long: stop
AUTO_REC_FRESH_S = 2.0     # /go2_states and camera both newer than this: the dog is connected
AUTO_REC_LOST_S = 15.0     # no /go2_states for this long: the dog disconnected
AUTO_REC_MIN_FREE_GB = 50  # don't start below this; stop cleanly below AUTO_REC_MIN_FREE_GB - 5
AUTO_REC_MOVE = (0.08, 0.15)   # odom speed m/s, turn rad/s above which the dog counts as moving
AUTO_REC_POSTURE_M = 0.05  # body height change (standing up, lying down) that counts as activity
AUTO_REC_JPEG_Q = 80       # camera saved as full-size JPEG (~80 KB/frame) instead of raw 2.7 MB frames
# The L515 topics are always listed: ros2 bag record subscribes to each listed topic whenever it appears (polls
# discovery), so an L515 that is off or starts mid-session neither blocks nor delays the Go2 topics; its topics are
# simply missing from the bag (tested 2026-11-16). Measured with the L515 at ~8 Hz: depth 614 KB -> ~207 KB per
# frame with zstd, colour JPEG ~46 KB: about +7.6 GB/hour (~9 GB/hour at its 10 Hz max) on top of the Go2's ~4.
AUTO_REC_TOPICS = (["/camera/image_raw/compressed", "/camera/camera_info", "/point_cloud2"] + REC_TOPICS["pose"]
                   + REC_TOPICS["l515"])
# zstd per message shrinks lidar clouds ~5x. rosbag2's compression queue defaults to 1 and then drops messages
# (most clouds were lost in a replay test), so give it room and two threads.
AUTO_REC_ARGS = ["--compression-mode", "message", "--compression-format", "zstd",
                 "--compression-queue-size", "200", "--compression-threads", "2"]
AUTO_INDEX = "auto_index.jsonl"   # one line per finished auto session, in REC_DIR


class Recorder:
    """Runs `ros2 bag record` for the chosen sensor groups."""

    def __init__(self):
        self.proc, self.name, self.groups, self.started = None, None, [], 0.0
        self.size, self.size_t, self.by, self.error = 0, 0.0, None, None
        self.auto = False          # True while the running recording belongs to AutoRecorder
        self.lock = threading.Lock()

    def free_gb(self):
        return shutil.disk_usage(REC_DIR).free / 1e9

    def running(self):
        return bool(self.proc and self.proc.poll() is None)

    def start(self, groups, by, auto=None):
        """Manual: groups from REC_TOPICS. auto={"name": bag path under REC_DIR, "topics": [...], "args": [...],
        "min_free": GB} is AutoRecorder's session: same recorder, its own topics and bag options."""
        with self.lock:
            if self.proc and self.proc.poll() is None:
                if self.auto and not auto:
                    return "Auto recording is already saving this session; press Stop recording first for a manual one"
                return "Already recording"
            if auto:
                groups, extra, topics = ["camera", "lidar", "pose", "l515"], " ".join(auto.get("args", [])), " ".join(auto["topics"])
                if self.free_gb() < auto.get("min_free", REC_MIN_FREE_GB):
                    return f"Less than {auto.get('min_free', REC_MIN_FREE_GB)} GB free on disk"
                self.name = auto["name"]
            else:
                groups = [g for g in REC_TOPICS if g in groups]
                if not any(g in groups for g in ("camera", "lidar", "l515")):
                    return "Choose camera, lidar or L515 in Settings"
                if self.free_gb() < REC_MIN_FREE_GB:
                    return f"Less than {REC_MIN_FREE_GB} GB free on disk"
                self.name = time.strftime("go2_%Y%m%d_%H%M%S_") + "_".join(g for g in groups if g != "pose")
                extra, topics = "", " ".join(t for g in groups for t in REC_TOPICS[g])
            env = dict(os.environ, HOME="/tmp", ROS_LOG_DIR="/tmp/roslog_rec")
            # Runs as root like the driver: ROS's shared-memory transport delivers nothing between
            # different users, so a recorder running as the host user saved empty bags.
            self.proc = subprocess.Popen(
                ["bash", "-c", "source /opt/ros/humble/setup.bash && source /ros2_ws/install/setup.bash"
                 f" && exec ros2 bag record {extra} -o {REC_DIR}/{self.name} {topics}"],
                env=env, stdout=subprocess.DEVNULL, stderr=open("/tmp/rec.log", "w"))
            self.handed = False
            self.groups, self.started, self.size, self.by, self.error = groups, time.time(), 0, by, None
            self.auto = bool(auto)
            return None

    def stop(self):
        with self.lock:
            if self.proc and self.proc.poll() is None:
                self.proc.send_signal(signal.SIGINT)   # lets rosbag2 finish writing metadata
                try:
                    self.proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
            self.hand_over()

    def hand_over(self):
        """Give a finished recording to the host user."""
        if not self.name or getattr(self, "handed", True) or (self.proc and self.proc.poll() is None):
            return
        self.handed = True
        for d, dirs, files in os.walk(os.path.join(REC_DIR, self.name)):
            for f in [d] + [os.path.join(d, x) for x in files]:
                try:
                    os.chown(f, HOST_UID, HOST_UID)
                except OSError:
                    pass

    def dir_size(self, path):
        return sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(path) for f in fs)

    def status(self):
        running = bool(self.proc and self.proc.poll() is None)
        if not running:
            self.hand_over()      # it may have ended by itself
        if self.proc and not running and self.started and self.error is None and time.time() - self.started < 5:
            self.error = "Recorder exited right away; see /tmp/rec.log in the container"
        now = time.time()
        if now - self.size_t > 1.0:
            self.size_t = now
            if running:
                self.size = self.dir_size(os.path.join(REC_DIR, self.name))
                if self.free_gb() < REC_MIN_FREE_GB / 2:
                    self.error = "Stopped: disk almost full"
                    threading.Thread(target=self.stop, daemon=True).start()
            self._past = sorted(
                ({"name": n, "mb": round(self.dir_size(os.path.join(REC_DIR, n)) / 1e6, 1)}
                 for n in os.listdir(REC_DIR) if os.path.isdir(os.path.join(REC_DIR, n))),
                key=lambda x: x["name"], reverse=True)[:8]
            self._free = round(self.free_gb())
        return {"running": running, "auto": running and self.auto, "name": self.name, "groups": self.groups, "by": self.by,
                "secs": round(now - self.started) if running else 0, "mb": round(self.size / 1e6, 1),
                "error": self.error, "past": getattr(self, "_past", []), "free_gb": getattr(self, "_free", None)}




def _trim_snapshot(snap):
    """The console state for a session's events.jsonl: what /events streams, minus the bulky parts (lidar cells,
    localization history, photos, notes) and minus who is driving (not needed for the dataset)."""
    out = {}
    for k, v in snap.items():
        if k == "live":
            continue
        if v and k == "cloud":
            v = {"frame": v.get("frame"), "n_total": v.get("n_total"), "floor_z": v.get("floor_z"),
                 "obs_cells": len(v.get("obs") or [])}
        elif v and k == "loc":
            v = {kk: vv for kk, vv in v.items() if kk not in ("events", "track", "marker")}
        elif v and k == "motors":     # integer temps in the /joint_states order (FL, FR, RL, RR x hip, thigh, calf)
            v = {kk: v.get(kk) for kk in ("temps", "max", "hottest", "level", "err", "stale")}
        elif v and k == "agents":
            v = {"call": (v.get("current") or {}).get("call")}
        elif v and k == "control":
            v = {kk: vv for kk, vv in v.items() if kk not in ("driver", "driver_ip", "speeds")}
        elif v and k == "rec":
            v = {kk: v.get(kk) for kk in ("running", "auto", "name", "mb", "free_gb")}
        out[k] = v
    return out


def _bag_counts(bag):
    """{topic: message count} from a finished bag's metadata.yaml, or None (no metadata: still open or crashed)."""
    try:
        import yaml
        with open(os.path.join(bag, "metadata.yaml")) as fh:
            info = yaml.safe_load(fh)["rosbag2_bagfile_information"]
        return {t["topic_metadata"]["name"]: int(t["message_count"]) for t in info["topics_with_message_count"]}
    except Exception:
        return None


def _chown_tree(path):
    for d, _, files in os.walk(path):
        for f in [d] + [os.path.join(d, x) for x in files]:
            try:
                os.chown(f, HOST_UID, HOST_UID)
            except OSError:
                pass


class AutoRecorder:
    """Saves every session with the dog, whoever sets it up (Oliver, lab board #50, 2026-11-08).

    Starts when the console has both /go2_states and camera frames after a connect. Stops when the dog disconnects
    (no /go2_states for AUTO_REC_LOST_S), after AUTO_REC_IDLE_S with no motion and no commands (standing still or
    lying down), or cleanly when free disk drops below min_free - 5 GB (and won't start below min_free). A new
    connect, or activity after an idle stop, starts a new session.
    Each session is REC_DIR/auto_YYYYMMDD_HHMMSS/ holding bag/ (the Recorder's ros2 bag: camera as JPEG, lidar,
    pose topics, zstd per message) and events.jsonl (console state once a second plus discrete events; no driver
    identity). REC_DIR/auto_index.jsonl gets one line per finished session, with the topics actually recorded (message
    counts from the bag's metadata) and whether the L515 was there.
    With the manual Record button: Stop recording during an auto session ends it and pauses auto recording until the
    dog reconnects; Record during an auto session is refused (no double recording); while a manual recording runs
    auto recording waits, and resumes after it if the dog is active.
    """

    def __init__(self, rec, enabled=AUTO_REC, idle_s=AUTO_REC_IDLE_S, min_free=AUTO_REC_MIN_FREE_GB, rec_dir=None):
        self.rec, self.enabled, self.idle_s, self.min_free = rec, enabled, idle_s, min_free
        self.rec_dir = rec_dir or REC_DIR
        self.connected, self.paused, self.disk_low = False, False, False
        self.last_active, self.retry_at, self.height = 0.0, 0.0, None
        self.session = None        # {"name", "dir", "start", "fh"}
        self.last = None           # the previous session's index line
        self.events = deque(maxlen=12)
        self.loc_seq, self.agent_t = None, 0.0
        self.lock = threading.RLock()

    # ---------- state machine (one tick a second) ----------
    def tick(self, now, sig, snap=None):
        """sig: state_age, camera_age (s), vel [vx, vy, wz] or None, cmd_age (s since the last motion command),
        body_height (m) or None, free_gb. snap: callable giving the console snapshot, for events.jsonl."""
        with self.lock:
            self._tick(now, sig)
            if self.session and snap:
                self._write_state(now, snap())

    def _tick(self, now, sig):
        st_age, cam_age = sig.get("state_age", 1e9), sig.get("camera_age", 1e9)
        if not self.connected and st_age < AUTO_REC_FRESH_S and cam_age < AUTO_REC_FRESH_S:
            self.connected, self.paused, self.disk_low, self.height = True, False, False, None
            self.last_active = now
            self._event(now, "connected")
        elif self.connected and st_age > AUTO_REC_LOST_S:
            self.connected = False
            self._event(now, "disconnected")
            if self.session:
                self._stop(now, "disconnected")
        if self.connected:
            v, h = sig.get("vel"), sig.get("body_height")
            active = sig.get("cmd_age", 1e9) < 2.0
            if v and (math.hypot(v[0], v[1]) > AUTO_REC_MOVE[0] or abs(v[2]) > AUTO_REC_MOVE[1]):
                active = True
            if h is not None:
                if self.height is None:
                    self.height = h
                elif abs(h - self.height) > AUTO_REC_POSTURE_M:     # stood up or lay down (also from the app/remote)
                    self.height, active = h, True
            if active:
                self.last_active = now
        if self.session and sig.get("l515_live"):
            self.session["l515_seen"] = True
        free = sig.get("free_gb")
        if self.session:
            if not (self.rec.running() and self.rec.auto):
                self._stop(now, "recorder_exited" + (f": {self.rec.error}" if self.rec.error else ""))
                self.retry_at = now + 60.0          # don't spin on a recorder that keeps failing
            elif free is not None and free < self.min_free - 5:
                self._stop(now, f"disk_low: {free:.0f} GB free")
                self.disk_low = True
            elif now - self.last_active > self.idle_s:
                lying = sig.get("body_height") is not None and sig["body_height"] < 0.18   # go2_agent.MIN_BODY_H
                self._stop(now, "lying_down" if lying else "idle")
        elif (self.enabled and self.connected and not self.paused and now >= self.retry_at
              and now - self.last_active <= self.idle_s and not self.rec.running()):
            if free is not None and free < self.min_free:
                if not self.disk_low:
                    self._event(now, "not_started", reason=f"disk_low: {free:.0f} GB free, need {self.min_free}")
                    self.disk_low = True
            else:
                self.disk_low = False
                self._start(now)

    def _start(self, now):
        name = time.strftime("auto_%Y%m%d_%H%M%S", time.localtime(now))
        d = os.path.join(self.rec_dir, name)
        try:
            os.makedirs(d, exist_ok=True)
            fh = open(os.path.join(d, "events.jsonl"), "a")
        except OSError as e:
            self._event(now, "not_started", reason=str(e))
            self.retry_at = now + 60.0
            return
        err = self.rec.start([], "auto", auto={"name": f"{name}/bag", "topics": AUTO_REC_TOPICS,
                                               "args": AUTO_REC_ARGS, "min_free": self.min_free})
        if err:
            fh.close()
            shutil.rmtree(d, ignore_errors=True)
            self._event(now, "not_started", reason=err)
            self.retry_at = now + 60.0
            return
        self.session = {"name": name, "dir": d, "start": now, "fh": fh, "l515_seen": False}
        self.loc_seq, self.agent_t = None, now
        self._event(now, "auto_rec_start", session=name, topics=AUTO_REC_TOPICS)

    def _stop(self, now, reason):
        s = self.session
        if self.rec.running() and self.rec.auto:
            self.rec.stop()                 # SIGINT: rosbag2 finishes its metadata
        self.rec.auto = False
        self._event(now, "auto_rec_stop", session=s["name"], reason=reason)
        self.session = None
        try:
            s["fh"].close()
        except OSError:
            pass
        _chown_tree(s["dir"])
        self.last = self._index(s["name"], s["start"], now, reason, self.rec.dir_size(s["dir"]) if os.path.isdir(s["dir"]) else 0,
                                l515_seen=s.get("l515_seen"))

    def _index(self, name, start, end, reason, size, l515_seen=None):
        counts = _bag_counts(os.path.join(self.rec_dir, name, "bag"))
        if counts is not None:     # what the bag really holds; listed topics that never published are absent
            l515 = any(counts.get(t) for t in REC_TOPICS["l515"])
        else:
            l515 = l515_seen
        line = {"name": name, "start": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(start)),
                "end": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(end)), "start_t": round(start, 2),
                "end_t": round(end, 2), "secs": round(end - start), "reason": reason, "bytes": size,
                "gb": round(size / 1e9, 3), "gb_per_hour": round(size / 1e9 * 3600 / (end - start), 2) if end - start > 60 else None,
                "topics": AUTO_REC_TOPICS, "topics_recorded": sorted(t for t, n in counts.items() if n) if counts else None,
                "msg_counts": counts, "l515": l515,
                "camera": f"jpeg q{AUTO_REC_JPEG_Q}", "bag_compression": "zstd per message"}
        p = os.path.join(self.rec_dir, AUTO_INDEX)
        try:
            with open(p, "a") as fh:
                fh.write(json.dumps(line) + "\n")
            os.chown(p, HOST_UID, HOST_UID)
        except OSError as e:
            print(f"[autorec] could not write {p}: {e}", flush=True)
        return line

    def _event(self, now, kind, **kw):
        e = {"t": round(now, 2), "at": time.strftime("%H:%M:%S", time.localtime(now)), "event": kind, **kw}
        self.events.append(e)
        print(f"[autorec] {json.dumps(e)}", flush=True)
        if self.session:
            self._write({"kind": "event", **e})

    def _write(self, obj):
        try:
            self.session["fh"].write(json.dumps(obj, default=str) + "\n")
            self.session["fh"].flush()
        except (OSError, ValueError):
            pass

    def _write_state(self, now, snap):
        """Console state once a second, plus new line-up events and agent calls since the last line."""
        loc = snap.get("loc") or {}
        evs = loc.get("events") or []
        if self.loc_seq is None:                      # only events from this session on
            self.loc_seq = max((e.get("seq", 0) for e in evs), default=0)
        for e in evs:
            if e.get("seq", 0) > self.loc_seq:
                self._write({"kind": "loc_event", **e})
        self.loc_seq = max([self.loc_seq] + [e.get("seq", 0) for e in evs])
        for e in (snap.get("agents") or {}).get("log") or []:
            if e.get("t", 0) > self.agent_t:
                self._write({"kind": "agent_call", **{k: v for k, v in e.items() if k != "client"}})
                self.agent_t = e["t"]
        self._write({"kind": "state", "t": round(now, 2), **_trim_snapshot(snap)})

    # ---------- console hooks ----------
    def user_stop(self, now=None):
        """A person pressed Stop recording during an auto session: end it, no auto recording until a reconnect."""
        with self.lock:
            if self.session:
                self._stop(now or time.time(), "stopped_by_user")
                self.paused = True
                self._event(now or time.time(), "paused_until_reconnect")
            else:
                self.rec.stop()

    def shutdown(self):
        with self.lock:
            if self.session:
                self._stop(time.time(), "console_stopped")

    def recover(self):
        """At console start: index sessions that a crash or kill left without an index line."""
        p = os.path.join(self.rec_dir, AUTO_INDEX)
        try:
            done = {json.loads(x)["name"] for x in open(p) if x.strip()}
        except (OSError, ValueError, KeyError):
            done = set()
        try:
            names = sorted(n for n in os.listdir(self.rec_dir) if n.startswith("auto_") and os.path.isdir(os.path.join(self.rec_dir, n)))
        except OSError:
            return
        for n in names:
            if n in done:
                continue
            d = os.path.join(self.rec_dir, n)
            try:
                start = time.mktime(time.strptime(n, "auto_%Y%m%d_%H%M%S"))
            except ValueError:
                continue
            end = max([os.path.getmtime(os.path.join(a, f)) for a, _, fs in os.walk(d) for f in fs] + [start])
            _chown_tree(d)
            self.last = self._index(n, start, end, "console_ended_unexpectedly", self.rec.dir_size(d))

    def status(self):
        """For /state.json and /events (rec.auto_info). Lock-free so a stopping recorder never stalls the console."""
        s, now = self.session, time.time()
        if not self.enabled:
            state = "off"
        elif s:
            state = "recording"
        elif not self.connected:
            state = "waiting_for_dog"
        elif self.paused:
            state = "paused_until_reconnect"
        elif self.disk_low:
            state = "disk_low"
        elif self.rec.running():
            state = "manual_recording"
        else:
            state = "idle"
        return {"enabled": self.enabled, "state": state, "session": s and s["name"],
                "secs": round(now - s["start"]) if s else 0,
                "idle_s": round(now - self.last_active) if self.connected else None,
                "idle_limit_s": self.idle_s, "min_free_gb": self.min_free, "last": self.last,
                "events": list(self.events)[-6:]}


REC = Recorder()
AUTO = AutoRecorder(REC)

lock = threading.Lock()
# Motor temperatures (/go2/motor_temps from patch_driver_motor_temps.sh). Neither the SDK nor the driver documents the
# Go2's over-temperature limits, so these are our own: warn at 60 degC, hot at 70 (2026-11-18: the dog collapsed by itself
# after standing 8 min, most likely motor over-temperature protection).
MOTOR_WARN_C = 60
MOTOR_HOT_C = 70
MOTOR_STALE_S = 10.0
latest = {"motors": None, "imu": None, "odom": None, "state": None, "joints": None, "cloud": None,
          "map": None, "map_pose": None, "stamps": {}}
map_png = {"data": None}         # latest lab map as PNG, for /map.png
jpeg = {"data": None, "t": 0.0}
full = {"img": None, "t": 0.0}   # latest camera frame at full size, for /frame.jpg
jpeg_cond = threading.Condition()


class L515View:
    """The RealSense L515 for the console, read from the bridge's page (L515_URL, l515_go2_pi4_bridge/web.py) so the
    console needs no extra ROS subscriptions and remote viewers only need port 8080. status.json is polled once a
    second (for /state.json l515 and the auto recorder); colour and colourised depth frames are fetched at
    L515_VIEW_HZ only while a browser asked for them in the last 10 s (/l515/color.jpg, /l515/depth.jpg)."""

    KINDS = ("color", "depth")

    def __init__(self, url=L515_URL):
        self.url = url.rstrip("/")
        self.cond = threading.Condition()
        self.frames = {k: (None, 0.0) for k in self.KINDS}     # kind -> (jpeg bytes, frame time)
        self.wanted = {k: 0.0 for k in self.KINDS}             # kind -> last time a browser asked
        self.st = {"online": False, "fps": None, "age_s": None, "bridge": False}

    def start(self):
        threading.Thread(target=self._status_loop, daemon=True).start()
        for k in self.KINDS:
            threading.Thread(target=self._frame_loop, args=(k,), daemon=True).start()
        return self

    def _get(self, path, timeout):
        import urllib.request
        with urllib.request.urlopen(self.url + path, timeout=timeout) as r:
            return r.status, r.read(), r.headers

    def _status_loop(self):
        while True:
            try:
                _, body, _ = self._get("/status.json", 1.5)
                c = json.loads(body).get("camera") or {}
                age = c.get("age")
                self.st = {"online": bool(c.get("live")), "fps": c.get("fps"),
                           "age_s": round(age, 1) if age is not None else None, "bridge": True,
                           "depth": c.get("depth"), "color": c.get("color")}
            except Exception:
                self.st = {"online": False, "fps": None, "age_s": None, "bridge": False}
            time.sleep(1.0)

    def _frame_loop(self, kind):
        after = 0.0
        while True:
            t0 = time.time()
            if t0 - self.wanted[kind] > 10 or not self.st["online"]:
                time.sleep(0.5)
                continue
            try:
                code, body, hdr = self._get(f"/{kind}.jpg?after={after!r}", 6)   # the bridge waits up to 5 s
                if code == 200 and body:
                    after = float(hdr.get("X-Frame-T") or time.time())
                    with self.cond:
                        self.frames[kind] = (body, after)
                        self.cond.notify_all()
            except Exception:
                after = 0.0
                time.sleep(1.0)
            time.sleep(max(0.0, 1.0 / L515_VIEW_HZ - (time.time() - t0)))

    def frame(self, kind, after, wait=3.0):
        """Newest frame newer than `after`, waiting up to `wait` s; (None, 0) if none."""
        self.wanted[kind] = time.time()
        with self.cond:
            self.cond.wait_for(lambda: self.frames[kind][1] > after, timeout=wait)
            data, t = self.frames[kind]
        return (data, t) if data is not None and t > after else (None, 0.0)

    def status(self):
        return {k: self.st.get(k) for k in ("online", "fps", "age_s", "bridge", "depth", "color")}

    def passthrough(self, path, timeout=7):
        """GET path on the bridge page: (status, body, headers), or (None, None, None) if it is not running."""
        import urllib.error
        try:
            return self._get(path, timeout)
        except urllib.error.HTTPError as e:
            return e.code, e.read(), e.headers
        except Exception:
            return None, None, None

    @staticmethod
    def embed(page):
        """The bridge page for the console panel: its fetches under /l515/, no header, no Record box, compact grid."""
        page = page.replace("fetch('/", "fetch('/l515/")
        css = ("<style>header{display:none}section:has(#recBtn){display:none}"
               "main{grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr))!important;gap:6px!important;padding:0!important}"
               "section{padding:6px!important}body{background:transparent}</style>")
        # hold the page's frame fetches while the console's panel is being dragged (no flicker; resumes on drop)
        hold = ("<script>(()=>{const f=window.fetch.bind(window);window.fetch=async(...a)=>{"
                "const w=()=>new Promise(r=>setTimeout(r,100));while(parent!==window&&parent.__DRAG)await w();"
                "const res=await f(...a);while(parent!==window&&parent.__DRAG)await w();return res}})()</script>")
        return page.replace("</head>", css + hold + "</head>", 1)


L515 = L515View()


def r(x, n=3):
    return round(float(x), n)


class Collector(Node):
    def __init__(self):
        super().__init__("go2_dashboard")
        q = qos_profile_sensor_data
        self.create_subscription(IMU, "/imu", self.on_imu, q)
        self.create_subscription(Odometry, "/odom", self.on_odom, q)
        self.create_subscription(Go2State, "/go2_states", self.on_state, q)
        self.create_subscription(JointState, "/joint_states", self.on_joints, q)
        self.create_subscription(PointCloud2, "/point_cloud2", self.on_cloud, q)
        self.create_subscription(Image, "/camera/image_raw", self.on_image, q)
        self.create_subscription(String, "/go2/motor_temps", self.on_motors, 10)
        # L515 raw depth/colour/camera_info and the dog camera_info, kept briefly for /agent/view (read-only)
        types = {"Image": Image, "CompressedImage": CompressedImage, "CameraInfo": CameraInfo}
        for kind, typ, topic in go2_patrol.L515_TOPICS:
            self.create_subscription(types[typ], topic, lambda m, k=kind: PATROLS and PATROLS.l515.on(k, m), q)
        self._mlost = None
        self.create_timer(0.2, self.update_map_pose)
        self.create_timer(0.25, self.marker_fix_tick)
        self.create_timer(2.0, self.refresh_map)
        self.create_timer(20.0, lambda: MAPPER.autosave(latest["odom"]))
        self.create_timer(5.0, lambda: MAPPER.save_session(latest["odom"]))
        self._map_key = None
        self.last_cloud = 0.0
        self.vel_pub = self.create_publisher(Twist, "cmd_vel_out", 10)
        self.jpeg_pub = self.create_publisher(CompressedImage, "/camera/image_raw/compressed", 10)  # auto recording
        self.last_cmd = 0.0      # monotonic time of the last motion/posture command: AutoRecorder's idle check
        self.req_pub = self.create_publisher(WebRtcReq, "webrtc_req", 10)
        self.moving, self.last_move = False, 0.0
        self.avoid = False
        self.head = 0.0          # camera tilt from body pitch, rad, + = looking up
        try:
            self.speed = open(SPEED_FILE).read().strip()
        except OSError:
            self.speed = "slow"
        if self.speed not in SPEEDS:
            self.speed = "slow"
        self.driver, self.driver_ip, self.driver_t = None, None, 0.0
        self.create_timer(0.05, self.deadman)
        self._sync = self.create_timer(2.0, self.sync_avoid)

    def sync_avoid(self):
        """Once at startup: turn the dog's obstacle avoidance on (the console's default), so its
        state matches ours. Untick it on the console to drive without it."""
        self._sync.cancel()
        self.set_avoid(AVOID_DEFAULT)

    def req(self, api_id, topic, param="", priority=0):
        msg = WebRtcReq()
        msg.api_id, msg.topic, msg.priority = api_id, topic, priority
        msg.parameter = param if isinstance(param, str) else json.dumps(param)
        self.req_pub.publish(msg)

    def send(self, name):
        self.req(CMD[name], SPORT_TOPIC, "", 1 if name == "StopMove" else 0)

    def stop(self):
        if self.avoid:
            self.req(AVOID_MOVE, AVOID_TOPIC, {"x": 0.0, "y": 0.0, "yaw": 0.0, "mode": 0}, 1)
        self.send("StopMove")
        if self.head:        # StopMove may reset the body pose; keep looking where we were
            self.send_head()

    def send_head(self):
        self.req(CMD["Euler"], SPORT_TOPIC, {"x": 0.0, "y": round(UP_SIGN * self.head, 3), "z": 0.0})

    def look(self, rad):
        """Tilt the body so the camera looks up (+) or down (-); only while standing still."""
        if DEPLOYING:
            return
        self.head = max(-HEAD_MAX, min(HEAD_MAX, float(rad)))
        self.last_cmd = time.monotonic()
        self.moving = False
        self.send("BalanceStand")
        time.sleep(0.1)
        self.send_head()

    def claim(self, client, ip):
        """One driver at a time: True if this client may drive now."""
        now = time.monotonic()
        if self.driver not in (None, client) and now - self.driver_t < DRIVER_HOLD_S:
            return False
        self.driver, self.driver_ip, self.driver_t = client, ip, now
        return True

    def move(self, x, y, z):
        if DEPLOYING:            # backstop for agent loops still running: no motion while deploying
            self.moving = False
            return
        x, y, z = (max(-l, min(l, float(v))) for v, l in zip((x, y, z), SPEEDS[self.speed]))
        x = max(-BACK_MAX, x)
        self.last_cmd = time.monotonic()
        if self.head and (x or y or z):     # level off before walking
            self.head = 0.0
            self.send_head()
        if self.avoid:
            # Routed through the dog's obstacle-avoidance service, which slows/stops near obstacles
            self.req(AVOID_MOVE, AVOID_TOPIC, {"x": round(x, 2), "y": round(y, 2), "yaw": round(z, 2), "mode": 0})
        else:
            t = Twist()
            t.linear.x, t.linear.y, t.angular.z = x, y, z
            self.vel_pub.publish(t)
        self.moving, self.last_move = True, time.monotonic()

    def set_avoid(self, on):
        self.moving = False
        self.stop()
        self.avoid = bool(on)
        self.req(AVOID_SWITCH_SET, AVOID_TOPIC, {"enable": self.avoid})
        time.sleep(0.2)
        self.req(AVOID_USE_API, AVOID_TOPIC, {"is_remote_commands_from_api": self.avoid})

    def action(self, name):
        self.moving = False
        if DEPLOYING:
            return
        self.last_cmd = time.monotonic()
        self.head = 0.0      # standing up or lying down resets the body pose
        self.stop()
        for c in ACTIONS[name]:
            time.sleep(0.2)
            self.send(c)

    def deadman(self):
        if self.moving and time.monotonic() - self.last_move > DEADMAN_S:
            self.moving = False
            self.stop()

    def stamp(self, key):
        latest["stamps"][key] = time.time()

    def on_imu(self, m):
        with lock:
            latest["imu"] = {"rpy": [r(v) for v in m.rpy],
                             "gyro": [r(v) for v in m.gyroscope],
                             "acc": [r(v) for v in m.accelerometer],
                             "temp": int(m.temperature)}
            self.stamp("imu")

    def on_odom(self, m):
        p, o = m.pose.pose.position, m.pose.pose.orientation
        yaw = math.atan2(2 * (o.w * o.z + o.x * o.y), 1 - 2 * (o.y * o.y + o.z * o.z))
        vel = self.odom_vel(time.monotonic(), p.x, p.y, yaw)
        with lock:
            latest["odom"] = {"pos": [r(p.x), r(p.y), r(p.z)], "yaw": r(yaw),
                              "vel": [r(v) for v in vel], "frame": m.header.frame_id}
            self.stamp("odom")

    def odom_vel(self, t, x, y, yaw):
        """Body-frame (vx, vy, wz) from successive odometry poses. The Go2 driver leaves the twist in
        /odom empty, so without this everything that checks whether the dog is turning saw zero."""
        prev = getattr(self, "_odom_prev", None)
        vel = getattr(self, "_odom_vel", [0.0, 0.0, 0.0])
        if prev is None or t - prev[0] > 1.0:
            self._odom_prev, self._odom_vel = (t, x, y, yaw), [0.0, 0.0, 0.0]
            return self._odom_vel
        dt = t - prev[0]
        if dt < 0.04:           # wait for a longer step: tiny ones are mostly noise
            return vel
        dx, dy = x - prev[1], y - prev[2]
        c, s = math.cos(prev[3]), math.sin(prev[3])
        raw = [(c * dx + s * dy) / dt, (-s * dx + c * dy) / dt,
               ((yaw - prev[3] + math.pi) % (2 * math.pi) - math.pi) / dt]
        a = min(1.0, dt / 0.15)  # smooth over ~0.15 s
        self._odom_vel = [v + a * (w - v) for v, w in zip(vel, raw)]
        self._odom_prev = (t, x, y, yaw)
        return self._odom_vel

    def on_state(self, m):
        with lock:
            latest["state"] = {"mode": int(m.mode), "gait": int(m.gait_type),
                               "body_height": r(m.body_height),
                               "foot_raise": r(m.foot_raise_height),
                               "velocity": [r(v) for v in m.velocity],
                               "obstacle": [r(v) for v in m.range_obstacle],
                               "foot_force": [int(v) for v in m.foot_force]}
            self.stamp("state")

    def on_motors(self, m):
        """/go2/motor_temps (JSON, /joint_states order): temps, max, hottest, per-leg max, motors whose lost count grew."""
        try:
            d = json.loads(m.data)
            names, temps = d.get("order") or [], d.get("temps") or []
            if len(names) != 12 or len(temps) != 12:
                return
            t = [None if v is None else int(round(float(v))) for v in temps]
            valid = [(v, n) for v, n in zip(t, names) if v is not None]
            mx, hot = max(valid) if valid else (None, None)
            lost = d.get("lost") or [None] * 12
            prev, self._mlost = self._mlost, lost
            err = [n for n, a, b in zip(names, prev or [], lost) if isinstance(a, (int, float)) and isinstance(b, (int, float)) and b > a]
            legs = {}
            for v, n in zip(t, names):
                if v is not None:
                    legs[n[:2]] = max(legs.get(n[:2], v), v)
            level = "hot" if mx is not None and mx >= MOTOR_HOT_C else "warm" if mx is not None and mx >= MOTOR_WARN_C else "ok"
            with lock:
                latest["motors"] = {"temps": t, "order": names, "max": mx, "hottest": hot, "legs": legs, "err": err,
                                    "lost": lost, "level": level, "warn_c": MOTOR_WARN_C, "hot_c": MOTOR_HOT_C}
                self.stamp("motors")
        except (ValueError, TypeError):
            pass

    def on_joints(self, m):
        with lock:
            latest["joints"] = {"name": list(m.name),
                                "pos": [r(v) for v in m.position]}
            self.stamp("joints")

    def on_cloud(self, m):
        now = time.time()
        if now - self.last_cloud < 0.5:   # 2 Hz is plenty for the top view
            return
        self.last_cloud = now
        pts = point_cloud2.read_points_numpy(m, field_names=("x", "y", "z"), skip_nans=True)
        if pts.size == 0:
            return
        with lock:
            odom = latest["odom"]
        cx, cy = (odom["pos"][0], odom["pos"][1]) if odom and m.header.frame_id != "base_link" else (0.0, 0.0)
        near = pts[(np.abs(pts[:, 0] - cx) < CLOUD_RADIUS) & (np.abs(pts[:, 1] - cy) < CLOUD_RADIUS)]
        if len(near) == 0:
            return
        # Collapse to a fixed 2D grid (no random sampling, so the view is stable frame to frame).
        # Each cell keeps its highest point; cells well above the floor count as obstacles.
        floor = float(np.percentile(near[:, 2], 20))
        # The dog's own cloud smears walls into arcs while it turns, so only map while it isn't turning.
        if MAPPER and m.header.frame_id != "base_link" and odom and abs(odom["vel"][2]) < MAP_MAX_TURN:
            MAPPER.add_cloud(near, floor, (odom["pos"][0], odom["pos"][1]))
        ij = np.floor(near[:, :2] / CELL).astype(np.int64)
        key = ij[:, 0] * 100003 + ij[:, 1]
        order = np.lexsort((near[:, 2], key))
        last = np.r_[key[order][1:] != key[order][:-1], True]
        top = order[last]
        cells = np.c_[(ij[top] + 0.5) * CELL, near[top, 2] - floor]
        obs = cells[(cells[:, 2] > OBSTACLE_MIN_H) & (cells[:, 2] < 2.0)]
        flat = cells[cells[:, 2] <= OBSTACLE_MIN_H]
        # A cell whose top is a desk, table or chair back (BUMP_H[1]..UNDER_TOP_MAX) hides what is under it when only
        # the highest point is kept. Look at all its points: something at bump height under the top -> under_obs
        # (an obstacle), else under (open floor under a top). go2_agent._update_live passes both to the planner.
        hs = near[order, 2] - floor
        starts = np.r_[0, np.nonzero(last)[0][:-1] + 1]      # first sorted point of each cell (top = its last)
        bump = np.logical_or.reduceat((hs > BUMP_H[0]) & (hs < BUMP_H[1]), starts)
        topped = (cells[:, 2] >= BUMP_H[1]) & (cells[:, 2] < UNDER_TOP_MAX)
        under_obs, under = cells[topped & bump, :2], cells[topped & ~bump, :2]
        with lock:
            latest["cloud"] = {"frame": m.header.frame_id, "n_total": int(len(pts)), "cell": CELL,
                               "floor_z": r(floor, 2),
                               "obs": np.round(obs.astype(np.float64), 2).tolist(),
                               "flat": np.round(flat[:, :2].astype(np.float64), 2).tolist(),
                               "under_obs": np.round(under_obs.astype(np.float64), 2).tolist(),
                               "under": np.round(under.astype(np.float64), 2).tolist()}
        if AG and AG.planner:
            AG.update_live()     # the route planner's view of what's around the dog now
            self.stamp("cloud")

    def refresh_map(self):
        """Re-render the lab map when it or its alignment changed."""
        key = (MAPPER.version, MAPPER.T, MAPPER.status, (MAPPER.track_info or {}).get("at"))
        if key == self._map_key:
            return
        self._map_key = key
        png, meta = MAPPER.png()
        with lock:
            map_png["data"] = png
            latest["map"] = meta
            if meta:
                self.stamp("map")

    def marker_fix_tick(self):
        """Each new detector frame: surveyed markers seen well re-anchor the map position (Mapper.marker_fix)."""
        if not (MARKERS and MARKER_TABLE and MAPPER):
            return
        snap = MARKERS.latest
        if snap.get("frame_t") == getattr(self, "_mk_frame", None) or not snap.get("list"):
            return
        self._mk_frame = snap.get("frame_t")
        with lock:
            odom = latest["odom"]
        # Not lined up and a usable tag in view: line up from the tag by itself, as "Line up again" would (Oliver
        # 11-21: vision should settle the line-up without anyone pressing a button). Pose only, never motion.
        now = time.time()
        if (MAPPER.T is None and not MAPPER._aligning and not MAPPER.mapping and odom is not None
                and now - getattr(self, "_auto_tag_t", 0.0) > AUTO_TAG_LINEUP_S):
            choice = marker_lineup_choice()
            if choice["via"] == "marker":
                self._auto_tag_t = now
                err = MAPPER.lineup_from_marker(odom, choice["pose"], by="auto: tag in view")
                print(f"[lineup] auto from tag {choice['pose']['best']['mark']}: {err or 'started'}", flush=True)
        rec = MAPPER.marker_fix(odom, snap["list"], MARKER_TABLE.get())
        if rec and rec.get("action") not in (None, "agree"):
            print(f"[markers] {rec}", flush=True)

    def update_map_pose(self):
        """Robot pose on the lab map; also lines a new session up with the saved map when needed."""
        with lock:
            odom = latest["odom"]
        MAPPER.try_align(odom)
        pose = MAPPER.pose(odom)
        log_pose(odom, pose)
        with lock:
            latest["map_pose"] = pose
            if pose:
                self.stamp("map_pose")
        with jpeg_cond:
            data, t = jpeg["data"], jpeg["t"]
        li = MAPPER.loc_info() if pose else {}
        TRAIL.offer(pose, data, t, odom["vel"][2] if odom else 0.0,
                    loc={"map_id": MAPPER.saved_at, "track_fit": li.get("track_fit"), "fresh_fit": li.get("fresh_fit"),
                         "lost": li.get("lost"), "suspect": li.get("suspect")} if pose else None)

    def on_image(self, m):
        if m.encoding not in ("bgr8", "rgb8"):
            return
        img = np.frombuffer(m.data, np.uint8).reshape(m.height, m.width, 3)
        if m.encoding == "rgb8":
            img = img[:, :, ::-1]
        with lock:
            full["img"], full["t"] = img, time.time()
        if REC.auto and REC.running():   # auto recording saves the camera as full-size JPEG (~35x smaller than raw)
            ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, AUTO_REC_JPEG_Q])
            if ok:
                c = CompressedImage()
                c.header, c.format = m.header, "bgr8; jpeg compressed bgr8"
                c.data = array.array("B", buf.tobytes())
                self.jpeg_pub.publish(c)
        img = cv2.resize(img, (640, int(640 * m.height / m.width)))
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if ok:
            with jpeg_cond:
                jpeg["data"], jpeg["t"] = buf.tobytes(), time.time()
                jpeg_cond.notify_all()
            with lock:
                self.stamp("camera")


NOTICE_SEEN = {}     # client -> last line-up event seq it was told about


def localization_notice(client):
    """Line-up events (placements, line-ups, jumps) since this client's previous call, or None."""
    seq = MAPPER.event_seq
    last = NOTICE_SEEN.get(client)
    NOTICE_SEEN[client] = seq
    if last is None or seq == last:
        return None
    info = MAPPER.loc_info(track_n=0)
    evs = [e for e in info["events"] if e["seq"] > last]
    return {"events": evs, "status": info["status"], "fit": info["fit"], "runner_up": info["runner_up"],
            "unsure": info["unsure"],
            "summary": "; ".join(f"{e['kind'].replace('_', ' ')}"
                                 + (f" from tag {e['marker']}" if e.get("via") == "marker" else " (lidar)" if e.get("via") == "lidar" else "")
                                 + f" at {time.strftime('%H:%M:%S', time.localtime(e['t']))}"
                                 + (f" from ({e['from']['x']:.2f}, {e['from']['y']:.2f})" if e.get("from") else "")
                                 + (f" to ({e['to']['x']:.2f}, {e['to']['y']:.2f})" if e.get("to") else "")
                                 for e in evs)}


def lineup_reject_text(rejected):
    """Why no marker could seed a line-up, for the console status: 'no marker in view' or per tag reasons."""
    if not rejected:
        return "no marker in view"
    if rejected[0].get("id") is None:
        return "no marker in view (" + "; ".join(rejected[0]["why"]) + ")"
    return "no usable marker (" + "; ".join(f"tag {r['mark']}: {', '.join(r['why'])}" for r in rejected) + ")"


def click_vs_marker(click, pose):
    """How a Set-dog-position click compares with the marker pose: {x, y, yaw, dist_m, turn_deg, conflict}; conflict
    is the status text when the marker puts the dog outside the clicked region (CLICK_MARKER_R, HINT_YAW_TOL)."""
    x, y, yaw = click
    tag = pose["best"]["mark"]
    dist = math.hypot(pose["x"] - x, pose["y"] - y)
    turn = None if yaw is None else abs(math.degrees(wrap(pose["yaw"] - yaw)))
    conflict = []
    if dist > CLICK_MARKER_R:
        conflict.append(f"tag {tag} puts the dog {dist:.1f} m from your click")
    if turn is not None and turn > math.degrees(HINT_YAW_TOL):
        conflict.append(f"tag {tag} has the dog facing {turn:.0f}° away from your arrow")
    return {"x": round(x, 3), "y": round(y, 3), "yaw": None if yaw is None else round(yaw, 4), "dist_m": round(dist, 3),
            "turn_deg": None if turn is None else round(turn, 1),
            "conflict": ("; ".join(conflict) + f"; used tag {tag}") if conflict else None}


def marker_lineup_choice():
    """For "Line up again": {"via": "marker", "pose", "used", "rejected"} from the latest detector frame, or
    {"via": "lidar", "note": why no marker was used, "rejected"}."""
    snap = MARKERS.latest if MARKERS else {}
    ft = snap.get("frame_t") or 0.0
    age = time.time() - ft if ft else None
    if age is None:
        pose, used, rej = None, [], []
    else:
        pose, used, rej = marker_lineup_pose(snap.get("list") or [], MARKER_TABLE.get() if MARKER_TABLE else {}, age)
    if pose:
        clash = marker_clash(pose)
        if clash:
            return {"via": "lidar", "note": clash, "rejected": rej, "marker_pose": pose}
        return {"via": "marker", "pose": pose, "used": used, "rejected": rej}
    return {"via": "lidar", "note": lineup_reject_text(rej), "rejected": rej}


AUTO_TAG_LINEUP_S = 10.0  # not lined up: try a line-up from a tag in view at most this often


def tag_lineup_for_agent(client, wait_s=10.0):
    """relocalize mode "tag" (go2_agent): line up from a tag in view now, wait for the result. Without a usable tag,
    say why and where the tags are, so the agent can turn towards one."""
    tags = [{"tag": v.get("name"), "x": round(v["x"], 2), "y": round(v["y"], 2), "facing_deg": round(v["facing_deg"], 1)}
            for v in (MARKER_TABLE.get() if MARKER_TABLE else {}).values()]
    choice = marker_lineup_choice()
    if choice["via"] != "marker":
        return {"result": "refused", "reason": f"no usable tag in view: {choice.get('note') or 'none seen'}. "
                "Turn to face a tag from 0.8-3 m (within ~30 deg of its front) and try again.",
                "why": {"code": "no_tag_in_view", "detail": choice.get("note")}, "tags": tags}
    with lock:
        odom = latest["odom"]
    err = MAPPER.lineup_from_marker(odom, choice["pose"], by=f"agent {client}")
    if err:
        return {"result": "error", "reason": err, "tags": tags}
    end = time.time() + wait_s
    while MAPPER._aligning and time.time() < end:
        time.sleep(0.2)
    ok = MAPPER.T is not None and not MAPPER._aligning
    with lock:
        odom = latest["odom"]
    return {"result": "done" if ok else "error", "via": "tag", "tag": choice["pose"]["best"]["mark"],
            "status": MAPPER.status, "pose": MAPPER.pose(odom), **({} if ok else {"reason": "the line-up did not finish"})}


MARKER_CLASH_M = 1.5     # a marker pose this far from a confident lidar pose is not used for a line-up
MARKER_CLASH_FIT = 0.7   # confident: track or fresh fit at least this, not lost, not suspect


def marker_clash(pose):
    """Why a marker pose should not be used, or None. Guards against a wrong marker table entry: on 2026-11-16 the
    detector's tag D (id 3) was listed in the table as tag_C 6 m away, so a line-up from D would have put the dog
    6 m off. Only refuses when the current lidar pose is confident and far from the marker's."""
    with lock:
        odom = latest["odom"]
    cur = MAPPER.pose(odom) if MAPPER and odom else None
    if not cur:
        return None
    loc = MAPPER.loc_info(track_n=0)
    fit = loc.get("track_fit") or loc.get("fresh_fit") or 0.0
    if loc.get("lost") or loc.get("suspect") or fit < MARKER_CLASH_FIT:
        return None
    d = math.hypot(pose["x"] - cur["x"], pose["y"] - cur["y"])
    if d <= MARKER_CLASH_M:
        return None
    return (f"tag {pose['best']['mark']} puts the dog {d:.1f} m from the current lidar pose (fit {fit:.2f}); not used,"
            " check the marker table")


def objects_path():
    return os.path.join("/maps", f"{os.environ.get('MAP_NAME', 'lab')}_objects.json")


def load_objects():
    """Labelled objects on the map (desk, sofa, ...), written by the labelling pass (go2_label.py) and
    corrected by people on the console: {"objects": [{id, label, name, x, y, w, h, yaw, ...}], ...}."""
    try:
        with open(objects_path()) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"objects": []}


def proposals_path():
    return os.path.join("/maps", f"{os.environ.get('MAP_NAME', 'lab')}_proposals.json")


def apply_proposal(item, by):
    """Carry out one accepted tidy-pass proposal (go2_tidy.py): move a place, or add / move an object."""
    ch, kind = item.get("change") or {}, item.get("kind")
    if kind == "place_move":
        p = AG.move_place(str(item.get("target_id")), by, ch.get("x"), ch.get("y"), ch.get("yaw_deg"), ch.get("target"))
        if p is None:
            raise ValueError(f"no place {item.get('target_id')}")
        return p
    if kind in ("object_new", "object_move"):
        data = load_objects()
        oid = item.get("target_id") or f"tidy_{item.get('id')}"
        obj = next((o for o in data["objects"] if o.get("id") == oid), None)
        if obj is None:
            obj = {"id": oid}
            data["objects"].append(obj)
        obj.update({k: ch[k] for k in ("label", "name", "x", "y", "w", "h", "yaw") if k in ch})
        obj.update(source="tidy", confirmed_by=by, confirmed_t=round(time.time(), 1))
        tmp = objects_path() + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=1)
        os.chown(tmp, 1000, 1000)
        os.replace(tmp, objects_path())
        return obj
    raise ValueError(f"unknown proposal kind {kind}")


def battery():
    """The dog's battery, from /tmp/go2_battery.json, written by the patched driver (patch_driver_battery.sh):
    {soc %, current mA, voltage V, temps, cycles, age_s}, or None if the driver isn't patched."""
    try:
        with open("/tmp/go2_battery.json") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    b = d.get("bms_state") or {}
    out = {"soc": b.get("soc"), "current_ma": b.get("current"), "cycles": b.get("cycle"),
           "voltage": d.get("power_v"), "bms_temp_c": b.get("bq_ntc"), "age_s": round(time.time() - d.get("t", 0), 1)}
    if out["voltage"] is None and b.get("cell_vol"):
        out["voltage"] = round(sum(b["cell_vol"]) / 1000.0, 2)
    return out if out["age_s"] < 30 else dict(out, stale=True)


POSELOG = {"t": 0.0}


def log_pose(odom, pose):
    """Every 0.2 s: odom, map pose and the map<-odom transform, so camera frames and recordings can be put on
    the map afterwards (labelling, offline analysis). One file per day; small (~2 MB/hour)."""
    now = time.time()
    if odom is None or now - POSELOG["t"] < 0.19:
        return
    POSELOG["t"] = now
    d = os.path.join("/maps", f"{os.environ.get('MAP_NAME', 'lab')}_poselog")
    f = os.path.join(d, time.strftime("%Y%m%d") + ".jsonl")
    try:
        if not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
            os.chown(d, 1000, 1000)
        with open(f, "a") as fh:
            fh.write(json.dumps({"t": round(now, 3), "odom": [odom["pos"][0], odom["pos"][1], odom["yaw"]],
                                 "map": [pose["x"], pose["y"], pose["yaw"]] if pose else None,
                                 "T": [round(v, 5) for v in MAPPER.T] if MAPPER.T else None,
                                 "mapping": MAPPER.mapping}) + "\n")
    except OSError:
        pass


def dog_status(snap):
    """{state: off|idle|active, for_s, odom_age_s, idle_s}: off when odom is older than DOG_OFF_S; idle when nothing
    moved and no command or posture change for DOG_IDLE_S (the auto recorder's activity rule, plus odom motion and
    console commands); else active."""
    now = time.time()
    age = (snap.get("age") or {}).get("odom")
    od = snap.get("odom") or {}
    v = od.get("vel")
    if v and (math.hypot(v[0], v[1]) > AUTO_REC_MOVE[0] or abs(v[2]) > AUTO_REC_MOVE[1]):
        DOG_ST["active_t"] = now
    if NODE and time.monotonic() - NODE.last_cmd < 2.0:
        DOG_ST["active_t"] = now
    if AUTO.connected and AUTO.last_active:
        DOG_ST["active_t"] = max(DOG_ST["active_t"], AUTO.last_active)
    idle = now - DOG_ST["active_t"] if DOG_ST["active_t"] else None
    if age is None or age > DOG_OFF_S:
        state = "off"
    elif idle is None or idle >= DOG_IDLE_S:
        state = "idle"
    else:
        state = "active"
    if state != DOG_ST["state"]:
        DOG_ST["state"], DOG_ST["since"] = state, now
    if state == "off":
        for_s = age
    elif state == "idle":
        for_s = idle
    else:
        for_s = now - DOG_ST["since"]
    return {"state": state, "for_s": None if for_s is None else round(for_s, 1),
            "odom_age_s": None if age is None else round(age, 1), "idle_s": None if idle is None else round(idle, 1)}


_STOPPED_AT_EXIT = []


def agent_chat_proxy(handler, method, rest, body=None):
    """Forward /agentchat/<rest> to the host's agent runner (go2_agent_chat.py). Lab network only."""
    import urllib.error
    import urllib.request
    req = urllib.request.Request(f"{AGENT_CHAT_URL}/{rest}", data=body, method=method,
                                 headers={"Content-Type": "application/json"} if body is not None else {})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code, data = r.status, r.read()
    except urllib.error.HTTPError as e:
        code, data = e.code, e.read()
    except Exception:
        code, data = 502, json.dumps({"error": "the agent runner is not running (go2_agent_chat.py on the control PC)"}).encode()
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(data)


def stop_dog(reason, times=4, gap=0.1):
    """What the STOP button does (interrupt agents, obstacle-avoid zero move if avoidance is on, StopMove, plus a zero
    Twist), sent `times` times over ~0.3 s so it gets through. Safe to call from any thread and at shutdown."""
    print(f"[stop] stopping the dog: {reason}", flush=True)
    try:
        if AG:
            AG.interrupt(reason)
    except Exception as e:
        print(f"[stop] interrupt failed: {e!r}", flush=True)
    for i in range(times):
        try:
            NODE.moving = False
            NODE.stop()
            NODE.vel_pub.publish(Twist())
        except Exception as e:
            print(f"[stop] publish failed: {e!r}", flush=True)
        if i < times - 1:
            time.sleep(gap)


def stop_at_exit(reason="console shutting down"):
    """Once per process: refuse motion, then stop the dog (before the auto session is closed)."""
    global DEPLOYING
    if _STOPPED_AT_EXIT or NODE is None:
        return
    _STOPPED_AT_EXIT.append(time.time())
    DEPLOYING = DEPLOYING or {"t": round(time.time(), 2), "msg": reason}
    stop_dog(reason)
    time.sleep(0.1)          # let DDS hand the last stop to the driver before the node goes away


def snapshot():
    """Everything the console shows, as one JSON-able dict (sent on /events and /state.json)."""
    with lock:
        now = time.time()
        snap = {k: v for k, v in latest.items() if k != "stamps"}
        if snap.get("cloud"):          # the under-top cells are for the planner only; keep /events the size it was
            snap["cloud"] = {k: v for k, v in snap["cloud"].items() if k not in ("under", "under_obs")}
        snap["age"] = {k: r(now - t, 2) for k, t in latest["stamps"].items()}
        if snap.get("motors"):
            snap["motors"] = dict(snap["motors"], stale=now - latest["stamps"].get("motors", 0) > MOTOR_STALE_S)
    mono = time.monotonic()
    snap["rec"] = REC.status()
    snap["rec"]["auto_info"] = AUTO.status()   # rec.auto is true while auto recording runs
    snap["agents"] = AG.status()
    last = AG.planner.last if AG.planner else None
    snap["nav"] = {k: last[k] for k in ("path", "goal", "t") if k in last} if last and time.time() - last["t"] < 300 else None
    snap["loc"] = MAPPER.loc_info()
    snap["markers"] = MARKERS.snapshot() if MARKERS else None
    snap["battery"] = battery()
    snap["l515"] = L515.status()
    snap["boot_id"] = BOOT_ID
    snap["dog_status"] = dog_status(snap)
    snap["watchdog"] = WATCHDOG
    snap["deploying"] = DEPLOYING
    snap["patrol"] = PATROLS.brief() if PATROLS else None
    lv = AG.planner.overlay() if AG.planner else None
    snap["live"] = lv if lv and time.time() - lv["t"] < 5 else None
    snap["control"] = {"avoid": NODE.avoid, "speed": NODE.speed, "speeds": SPEEDS, "look_deg": round(math.degrees(NODE.head)),
                       "driver": NODE.driver if mono - NODE.driver_t < DRIVER_HOLD_S else None,
                       "driver_ip": NODE.driver_ip}
    return snap


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def can_control(self):
        try:
            ip = ipaddress.ip_address(self.client_address[0].removeprefix("::ffff:"))
        except ValueError:
            return False
        return ip.is_loopback or any(ip in n for n in CONTROL_NETS)

    def send_json(self, code, obj):
        client = getattr(self, "notice_for", None)
        if client and isinstance(obj, dict):
            n = localization_notice(client)
            if n:
                obj = dict(obj, localization_notice=n)
            env = PATROLS.envelope_for(client) if PATROLS else None
            if env and "envelope" not in obj:
                obj = dict(obj, envelope=env)
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_bytes(self, body, ctype):
        if body is None:
            return self.send_error(404)
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def agent_post(self, call, req):
        """Blocking agent tools. A person at the console always wins (see go2_agent.py)."""
        client, ip = str(req.get("client") or ""), self.client_address[0]
        if not client:
            return self.send_json(400, {"result": "error", "reason": "client is required"})
        self.notice_for = client
        if call == "status":
            return self.send_json(200, {**AG.status(), **AG.pose_out(), "safe": AG.check_safe() or "ok", "markers": MARKERS.snapshot()["list"] if MARKERS else [], "battery": battery()})
        if call == "stop":                       # always allowed
            AG.interrupt(f"stop from agent {client}")
            return self.send_json(200, {"result": "done"})
        if call == "release":
            return self.send_json(200, {"result": "done" if AG.release(client) else "not_owner"})
        if call == "say":
            AG.notes[client] = {"text": str(req.get("text", ""))[:300], "t": time.time()}
            return self.send_json(200, {"result": "done"})
        if call == "patrol/stop":                # stops first, then ends the patrol (go2_patrol.Patrols.stop)
            return self.send_json(*PATROLS.stop(client))
        blk = PATROLS.blocks(client)             # an open patrol: no other agent may claim the dog
        if blk:
            return self.send_json(409, {"result": "refused", "reason": blk["detail"], "stop_reason": "refused", "why": blk})
        why = AG.agent_may_drive(client, ip)
        if why:
            return self.send_json(409, {"result": "refused", "reason": why, "stop_reason": "refused",
                                        "why": {"code": "human_has_control" if "person" in why else "agent_has_control",
                                                "detail": why}})
        if call == "claim":
            PATROLS.touch(client)
            return self.send_json(200, {"result": "done", "lease_s": AGENT_LEASE_S})
        try:
            if call == "patrol/start":
                code, out = PATROLS.start(client, req)
            elif call == "view":
                code, out = PATROLS.view(client, req)
            elif PATROLS.owns(client):           # the patrol envelope around the existing tools
                code, out = PATROLS.tool(call, client, req)
            else:
                code, out = AG.tool(call, client, req)
        except (KeyError, ValueError, TypeError) as e:
            return self.send_json(400, {"result": "error", "reason": f"bad arguments: {e}", "stop_reason": "bad_arguments"})
        return self.send_json(code, out)

    def do_POST(self):
        path = self.path.split("?")[0]
        if not (path in ("/cmd", "/map", "/map/objects", "/map/proposals", "/deploying", "/watchdog", "/patrol/check") or path.startswith(("/agent/", "/places", "/label/", "/agentchat/"))):
            return self.send_error(404)
        if path == "/watchdog":     # ~/oliver/go2_watchdog.py on this machine: its latest status, shown on the page
            try:
                ip = ipaddress.ip_address(self.client_address[0].removeprefix("::ffff:"))
            except ValueError:
                ip = None
            if not (ip and ip.is_loopback):
                return self.send_error(403, "/watchdog is for this machine only")
            try:
                req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                if not isinstance(req, dict):
                    raise ValueError("expected a JSON object")
            except ValueError as e:
                return self.send_error(400, str(e))
            global WATCHDOG
            WATCHDOG = dict(req, received_t=round(time.time(), 2))
            return self.send_json(200, {"result": "done"})
        if path == "/deploying":    # deploy_console.sh, this machine only: stop the dog, refuse motion until restart
            try:
                ip = ipaddress.ip_address(self.client_address[0].removeprefix("::ffff:"))
            except ValueError:
                ip = None
            if not (ip and ip.is_loopback):
                return self.send_error(403, "/deploying is for this machine only")
            try:
                req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            except ValueError:
                req = {}
            global DEPLOYING
            DEPLOYING = {"t": round(time.time(), 2), "msg": str(req.get("msg") or "deploying a new console version")[:200]}
            stop_dog(f"console is deploying: {DEPLOYING['msg']}")
            return self.send_json(200, {"result": "done", "deploying": DEPLOYING, "boot_id": BOOT_ID})
        if not self.can_control():
            return self.send_error(403, "Drive controls only work from the lab network")
        if path.startswith("/agentchat/"):        # "Ask the dog": the host's agent runner; Stop always goes through
            rest = path[len("/agentchat/"):]
            if DEPLOYING and rest == "chat":
                return self.send_json(503, {"error": "console is deploying; try again when it is back"})
            return agent_chat_proxy(self, "POST", rest, self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError as e:
            return self.send_error(400, str(e))
        if path.startswith("/agent/"):
            call = path[len("/agent/"):]
            if call not in AGENT_CALLS:
                return self.send_error(404)
            if DEPLOYING and call in MOTION_AGENT_CALLS:
                return self.send_json(503, {"result": "refused", "reason": "console is deploying", "stop_reason": "deploying",
                                            "deploying": DEPLOYING})
            return self.agent_post(call, req)
        if path == "/label/example":
            # {url: trail frame, box: [x1, y1, x2, y2] fractions, name, label?, place: bool, client}: a person says
            # "this box in this photo is <name>". Recomputes the object from all its examples; place=true also saves
            # a place to stand (where the best photo was taken from, facing the object).
            by = str(req.get("client") or "console")[:60]
            try:
                ex = EXAMPLES.add(req.get("url"), req.get("box") or [], str(req.get("name", "")).strip(),
                                  req.get("label"), by)
            except (ValueError, TypeError) as e:
                return self.send_json(400, {"result": "error", "reason": str(e)})
            obj, est = EXAMPLES.upsert_object(objects_path(), ex["name"], by)
            place = None
            if req.get("place") and est:
                st = est["stand"]
                rec, f = EXAMPLES.frame(st["frame"])
                place = AG.save_place(ex["name"], f"labelled from {est['examples']} photo(s)", by,
                                      pose={"x": st["x"], "y": st["y"], "yaw": st["yaw"]}, image=cv2.imread(f),
                                      target=tuple(est["centre"]))
            return self.send_json(200, {"result": "done", "example": ex, "object": obj, "estimate": est, "place": place})
        if path == "/label/remove":
            exs = [e for e in EXAMPLES.load()["examples"] if e["id"] == req.get("id")]
            if not exs or not EXAMPLES.remove(req.get("id")):
                return self.send_json(404, {"result": "error", "reason": "no example with that id"})
            obj, _ = EXAMPLES.upsert_object(objects_path(), exs[0]["name"], str(req.get("client") or "console")[:60])
            return self.send_json(200, {"result": "done", "object": obj})
        if path == "/map/objects":
            # people correct the labelling: {action: rename|relabel|delete|confirm|move|set, id, name?, label?},
            # or add one by hand: {action: add, name, label, x, y, w?, h?, yaw?, aruco_id?}.
            # aruco_id (0-49, DICT_4X4_50) makes the object a marker; yaw is the way its printed face looks out.
            data = load_objects()
            act = req.get("action")

            def aruco(v):
                if v is None or v == "":
                    return None
                try:
                    f = float(v)
                except (TypeError, ValueError):
                    f = -1.0
                if isinstance(v, bool) or f != int(f) or not 0 <= f <= 49:
                    raise ValueError("aruco_id must be a whole number 0-49")
                return int(f)

            def taken(a, me=None):
                # one saved marker per id: the marker checks look markers up by id
                o = next((o for o in data["objects"] if o.get("aruco_id") == a and o.get("id") != me), None)
                if o:
                    raise ValueError(f"marker id {a} is already used by {o.get('name') or o.get('id')}")
            try:
                if act == "add":
                    name = check_name(req.get("name"))
                    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")[:30] or "object"
                    ids = {o.get("id") for o in data["objects"]}
                    oid, n = f"hand_{slug}", 2
                    while oid in ids:
                        oid, n = f"hand_{slug}_{n}", n + 1
                    obj = {"id": oid, "name": name, "label": str(req.get("label") or "").strip().lower()[:40],
                           "x": round(float(req["x"]), 3), "y": round(float(req["y"]), 3),
                           "w": round(float(req.get("w") or 0.4), 3), "h": round(float(req.get("h") or 0.4), 3),
                           "yaw": round(float(req.get("yaw") or 0.0), 4), "source": "hand"}
                    if aruco(req.get("aruco_id")) is not None:
                        taken(aruco(req.get("aruco_id")))
                        obj["aruco_id"] = aruco(req.get("aruco_id"))
                    data["objects"].append(obj)
                else:
                    obj = next((o for o in data["objects"] if o.get("id") == req.get("id")), None)
                    if obj is None:
                        return self.send_json(404, {"result": "error", "reason": "no object with that id"})
                    if act == "set":         # {aruco_id: 0-49, or null to clear}
                        a = aruco(req.get("aruco_id"))
                        if a is None:
                            obj.pop("aruco_id", None)
                        else:
                            taken(a, obj.get("id"))
                            obj["aruco_id"] = a
            except (KeyError, TypeError, ValueError) as e:
                return self.send_json(400, {"result": "error", "reason": str(e) if not isinstance(e, KeyError) else "add needs name, x and y"})
            if act == "delete":
                data["objects"].remove(obj)
            elif act == "rename":
                name = str(req.get("name") or "").strip()
                try:
                    obj["name"] = check_name(name) if name else ""
                except ValueError as e:
                    return self.send_json(400, {"result": "error", "reason": str(e)})
            elif act == "relabel":
                obj["label"] = str(req.get("label") or obj.get("label", ""))[:40]
            elif act == "move":          # {x?, y?, yaw? (rad), w?, h?}: a person dragged or resized it
                try:
                    for k in ("x", "y", "yaw", "w", "h"):
                        if req.get(k) is not None:
                            obj[k] = round(float(req[k]), 3)
                except (TypeError, ValueError):
                    return self.send_json(400, {"result": "error", "reason": "x, y, yaw, w, h must be numbers"})
            elif act not in ("confirm", "add", "set"):
                return self.send_json(400, {"result": "error", "reason": "action must be add, rename, relabel, move, set, delete or confirm"})
            if act != "delete":
                obj["confirmed_by"] = str(req.get("client") or "console")[:60]
                obj["confirmed_t"] = round(time.time(), 1)
            tmp = objects_path() + ".tmp"
            with open(tmp, "w") as f:
                json.dump(data, f, indent=1)
            os.chown(tmp, 1000, 1000)
            os.replace(tmp, objects_path())
            return self.send_json(200, {"result": "done", "object": None if act == "delete" else obj})
        if path == "/places":
            # {id, description} saves where the dog is now. Marking on the map instead:
            # target {x, y} = where the thing is; stand {x, y, yaw_deg} = where the dog should stand to
            # see it (e.g. where it stood for the chosen camera view), else picked automatically;
            # view = that camera view's URL, for the picture.
            try:
                pose = image = target = None
                t, st = req.get("target"), req.get("stand")
                if st is None and req.get("x") is not None:          # older form: x, y, yaw_deg
                    st = {"x": req["x"], "y": req["y"], "yaw_deg": req.get("yaw_deg")}
                if t is not None:
                    target = (float(t["x"]), float(t["y"]))
                if st is not None:
                    pose = {"x": float(st["x"]), "y": float(st["y"]), "yaw": math.radians(float(st.get("yaw_deg") or 0.0))}
                elif target is not None:
                    found = AG.planner.stand_for(*target)
                    if found is None:
                        raise ValueError("no open floor near that spot for the dog to stand on")
                    pose = {"x": found[0], "y": found[1], "yaw": found[2]}
                if pose is not None and req.get("view"):
                    f = TRAIL.path(str(req["view"]).removeprefix("/trail/"))
                    if f is None:
                        raise ValueError("that camera view no longer exists")
                    image = cv2.imread(f)
                return self.send_json(200, AG.save_place(str(req.get("id", "")), req.get("description", ""),
                                                         str(req.get("client") or self.client_address[0]),
                                                         pose=pose, image=image, target=target))
            except (ValueError, TypeError, KeyError) as e:
                return self.send_json(400, {"result": "error", "reason": str(e)})
        if path == "/patrol/check":
            # dry run for a patrol brain: [{x, y, yaw_deg?}] -> ok / refused + why, route_m, est_s. No claim, no motion.
            code, out = go2_patrol.check(req.get("poses"), AG, KEEPOUT)
            return self.send_json(code, out)
        if path == "/map":
            act = req.get("action")
            with lock:
                odom = latest["odom"]
            if act == "start":     # extend the saved map when lined up with it, else a new one
                err = MAPPER.start_mapping(odom, fresh=MAPPER.T is None or not MAPPER.seen.any())
            elif act == "clear":
                err = MAPPER.clear()
            elif act == "frame":    # set the odom -> map transform by hand: {"T": [tx, ty, theta_rad]}
                MAPPER.T, err = tuple(float(v) for v in req["T"][:3]), None
                MAPPER.pending, MAPPER.resume_mapping = None, False
            elif act in ("new", "extend"):
                err = MAPPER.start_mapping(odom, fresh=act == "new")
            elif act == "stop":
                err = MAPPER.stop_mapping()
            elif act == "revert":
                err = MAPPER.revert()
            elif act == "save":
                err = MAPPER.save(odom)
            elif act == "align":
                # Vision first (Oliver: localization fixes must use vision): a surveyed marker in view seeds the
                # line-up and the lidar only refines near it; with none usable, the lidar searches the whole map.
                err, lineup = None, marker_lineup_choice()
                if lineup["via"] == "marker":
                    err = MAPPER.lineup_from_marker(odom, lineup["pose"], by=str(req.get("client") or self.client_address[0])[:60])
                else:
                    MAPPER.align_note = lineup["note"]
                    MAPPER.T = None
                    MAPPER.try_align(odom, force=True)
                    if not MAPPER._aligning:          # nothing started (no lidar yet, mapping): don't keep the note
                        MAPPER.align_note = None
                print(f"[lineup] Line up again: {json.dumps(lineup, default=str)}", flush=True)
                NODE._map_key = None
                if err:
                    return self.send_json(409, {"result": "error", "reason": err, "lineup": lineup})
                return self.send_json(200, {"result": "done", "lineup": lineup, **MAPPER.info()})
            elif act == "localize_at":   # a person clicked where the dog is: {"x", "y", "yaw_deg"?}
                # The click only narrows the region (Oliver, 2026-11-16). A usable marker in view decides the pose
                # (a conflict with the click is reported, not hidden); without one, the lidar's good-enough line-up
                # closest to the click (and dragged heading) wins.
                try:
                    yaw = req.get("yaw_deg")
                    click = (float(req["x"]), float(req["y"]), None if yaw is None else math.radians(float(yaw)))
                except (KeyError, TypeError, ValueError):
                    return self.send_json(400, {"result": "error", "reason": "localize_at needs x and y (map metres), optional yaw_deg"})
                by = str(req.get("client") or "console")[:60]
                lineup = marker_lineup_choice()
                if lineup["via"] == "marker":
                    lineup["click"] = click_vs_marker(click, lineup["pose"])
                    err = MAPPER.lineup_from_marker(odom, lineup["pose"], by=by, click=lineup["click"])
                else:
                    MAPPER.align_note = lineup["note"]
                    err = MAPPER.localize_at(odom, *click, by=by)
                    if err:
                        MAPPER.align_note = None
                print(f"[lineup] Set dog position: {json.dumps(lineup, default=str)}", flush=True)
                NODE._map_key = None
                if err:
                    return self.send_json(409, {"result": "error", "reason": err, "lineup": lineup})
                return self.send_json(200, {"result": "done", "lineup": lineup, **MAPPER.info()})
            else:
                return self.send_json(400, {"result": "error", "reason": "action must be start, new, extend, stop, save, revert, clear, frame, align or localize_at"})
            NODE._map_key = None
            if err:
                return self.send_json(409, {"result": "error", "reason": err})
            return self.send_json(200, {"result": "done", **MAPPER.info()})
        if path == "/map/proposals":
            # {action: accept|reject|accept_all, id?, min_confidence?, client}: review the tidy pass's proposals
            by = str(req.get("client") or "console")[:60]
            try:
                with open(proposals_path()) as f:
                    data = json.load(f)
            except (OSError, ValueError):
                return self.send_json(404, {"result": "error", "reason": "no proposals"})
            act, done, errors = req.get("action"), [], []
            if act == "accept_all":
                todo = [i for i in data["items"] if not i.get("status")
                        and float(i.get("confidence", 0)) >= float(req.get("min_confidence", 0))]
            else:
                todo = [i for i in data["items"] if i.get("id") == req.get("id")]
                if not todo:
                    return self.send_json(404, {"result": "error", "reason": "no proposal with that id"})
            for item in todo:
                try:
                    if act in ("accept", "accept_all"):
                        apply_proposal(item, by)
                        item["status"] = "accepted"
                    elif act == "reject":
                        item["status"] = "rejected"
                    else:
                        return self.send_json(400, {"result": "error", "reason": "action must be accept, reject or accept_all"})
                    item["reviewed_by"], item["reviewed_t"] = by, round(time.time(), 1)
                    done.append(item["id"])
                except (ValueError, KeyError, TypeError) as e:
                    errors.append(f"{item.get('id')}: {e}")
            tmp = proposals_path() + ".tmp"
            with open(tmp, "w") as f:
                json.dump(data, f, indent=1)
            os.chown(tmp, 1000, 1000)
            os.replace(tmp, proposals_path())
            return self.send_json(200, {"result": "done", "done": done, "errors": errors})
        if path == "/places/move":
            # {id, x?, y?, yaw_deg?, target?: {x, y} | null, client}: a person dragged a place on the map
            try:
                tgt = req.get("target", None)
                p = AG.move_place(str(req.get("id", "")), str(req.get("client") or "console")[:60],
                                  req.get("x"), req.get("y"), req.get("yaw_deg"),
                                  False if ("target" in req and tgt is None) else tgt)
            except (KeyError, TypeError, ValueError) as e:
                return self.send_json(400, {"result": "error", "reason": f"bad arguments: {e}"})
            return self.send_json(200 if p else 404, {"result": "done", "place": p} if p else {"result": "not_found"})
        if path == "/places/rename":
            # {id, to, client}: keeps the spot, target, photo and description
            try:
                p = AG.rename_place(str(req.get("id", "")), req.get("to"), str(req.get("client") or "console")[:60])
            except ValueError as e:
                return self.send_json(400, {"result": "error", "reason": str(e)})
            return self.send_json(200 if p else 404, {"result": "done", "place": p} if p else {"result": "not_found"})
        if path == "/places/delete":
            return self.send_json(200, {"result": "done" if AG.delete_place(str(req.get("id", ""))) else "not_found"})
        try:
            client, ip = str(req.get("client", "")), self.client_address[0]
            console = bool(req.get("console"))       # sent by the console page: a person
            if "record" in req:                      # recording is independent of driving
                if req["record"]:
                    err = REC.start(req.get("groups", []), ip)     # refused while an auto session runs
                    if err:
                        return self.send_error(409, err)
                elif REC.auto and REC.running():
                    AUTO.user_stop()      # ends the auto session; auto recording pauses until the dog reconnects
                else:
                    REC.stop()
            elif req.get("action") == "stop":        # anyone may stop the dog, always
                AG.interrupt(f"STOP pressed at {ip}" if console else f"stop from {client or ip}")
                if console:      # a person's STOP also locks agents out until Hand back, so none moves next
                    AG.human_drives(client, ip)
                NODE.moving = False
                NODE.stop()
            elif "speed" in req:                     # the speed cap for everyone; doesn't take control
                if req["speed"] not in SPEEDS:
                    return self.send_error(400, "speed must be slow, normal or fast")
                NODE.speed = req["speed"]
                try:
                    with open(SPEED_FILE, "w") as f:
                        f.write(NODE.speed)
                except OSError:
                    pass
            elif req.get("takeover"):                # a person takes control from any agent
                if not console:
                    return self.send_error(400, "takeover is for the console")
                AG.human_drives(client, ip)
                NODE.moving = False
                NODE.stop()
            elif req.get("handback"):
                AG.hand_back()
            elif DEPLOYING and any(k in req for k in ("move", "avoid", "look_deg")) or (DEPLOYING and req.get("action") in ACTIONS):
                return self.send_error(503, "console is deploying")
            elif console and (AG.human_drives(client, ip) or not NODE.claim(client, ip)):
                return self.send_error(409, f"Someone at {NODE.driver_ip} is driving")
            elif not console and PATROLS.is_open():
                return self.send_error(409, "a patrol is open: agents drive through /agent/* only")
            elif not console and AG.agent_may_drive(client or ip, ip):
                return self.send_error(409, AG.agent_may_drive(client or ip, ip))
            elif not console and AG.current:
                return self.send_error(409, "An agent tool is running")
            elif "move" in req:
                NODE.move(*req["move"][:3])
            elif "avoid" in req:
                NODE.set_avoid(req["avoid"])
            elif "look_deg" in req:          # camera tilt, + = up
                NODE.look(math.radians(float(req["look_deg"])))
            elif req.get("action") in ACTIONS:
                NODE.action(req["action"])
            else:
                return self.send_error(400, "Expected move, action, avoid or look_deg")
        except (ValueError, TypeError) as e:
            return self.send_error(400, str(e))
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path == "/control":
            body = json.dumps({"allowed": self.can_control(), "you": self.client_address[0]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        elif self.path in ("/", "/index.html"):
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                while True:
                    self.wfile.write(b"data: " + json.dumps(snapshot()).encode() + b"\n\n")
                    self.wfile.flush()
                    time.sleep(0.1)
            except (BrokenPipeError, ConnectionResetError):
                pass
        elif self.path.startswith("/agent/photos/") and self.path.endswith(".jpg"):
            self.send_bytes(AG.photo_bytes(self.path[len("/agent/photos/"):-4]), "image/jpeg")
        elif self.path.split("?")[0] == "/state.json":
            self.send_json(200, snapshot())
        elif self.path.split("?")[0] == "/history":
            # state once a second over the last hours (go2_history.py), plus line-up events and agent calls in that window
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            try:
                num = lambda k: float(q[k][0]) if k in q else None      # noqa: E731
                keys = [k for k in q.get("keys", [""])[0].split(",") if k]
                out = HIST.get(keys or None, num("since"), num("until"), num("step"), int(num("limit") or 3600))
            except ValueError as e:
                return self.send_json(400, {"result": "error", "reason": str(e)})
            lo, hi = num("since") or 0, num("until") or 1e12
            out["loc_events"] = [e for e in MAPPER.loc_info(track_n=0)["events"] if lo <= e["t"] <= hi]
            out["agent_calls"] = [e for e in AG.status()["log"] if lo <= e["t"] <= hi]
            self.send_json(200, out)
        elif self.path.split("?")[0] == "/agent/status":
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            self.notice_for = q.get("client", [None])[0]
            self.send_json(200, {**AG.status(), **AG.pose_out(), "safe": AG.check_safe() or "ok", "markers": MARKERS.snapshot()["list"] if MARKERS else [], "battery": battery()})
        elif self.path.split("?")[0] == "/places":
            self.send_json(200, AG.places())
        elif self.path.startswith("/places/") and self.path.endswith(".jpg"):
            # names may hold spaces and quotes, so the URL is percent-encoded; never leave the places folder
            name = urllib.parse.unquote(self.path.split("?")[0][len("/places/"):])
            if "/" in name or "\\" in name or name.startswith("."):
                return self.send_error(404)
            try:
                with open(os.path.join("/maps", f"{os.environ.get('MAP_NAME', 'lab')}_places", name), "rb") as fh:
                    self.send_bytes(fh.read(), "image/jpeg")
            except OSError:
                self.send_error(404)
        elif self.path.split("?")[0] == "/trail/near":
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            try:
                x, y = float(q["x"][0]), float(q["y"][0])
                radius = min(float(q.get("radius", [3.0])[0]), 20.0)
                limit = max(1, min(int(q.get("limit", [12])[0]), 200))
            except (KeyError, ValueError):
                return self.send_error(400, "x and y are required (optional radius in m, limit)")
            self.send_json(200, {"views": TRAIL.near(x, y, radius, limit), "spot": MAPPER.cell_state(x, y)})
        elif self.path.split("?")[0] == "/trail/since":
            # frames newer than ?t= (unix seconds), oldest first; page with the last frame's t
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            try:
                t = float(q.get("t", [0])[0])
                limit = max(1, min(int(q.get("limit", [500])[0]), 2000))
            except ValueError:
                return self.send_error(400, "t must be unix seconds (optional limit)")
            frames = TRAIL.since(t, limit)
            self.send_json(200, {"frames": frames, "more": len(frames) == limit})
        elif self.path.split("?")[0] == "/nav/grid":
            # read-only look at the planning grid around ?x=&y= (map m; default the dog), ?r= m (default 2, max 4);
            # PNG, or ?json=1 for the narrowest clearance along the last route and cell counts. No planning.
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            mp = AG.map_pose_now()
            try:
                x = float(q["x"][0]) if "x" in q else (mp or {})["x"]
                y = float(q["y"][0]) if "y" in q else (mp or {})["y"]
                r = float(q.get("r", [2.0])[0])
            except (KeyError, TypeError, ValueError):
                return self.send_json(400, {"error": "x and y (map m) are required when the dog has no map pose; r in m"})
            want_json = q.get("json", ["0"])[0] not in ("0", "")
            robot = (mp["x"], mp["y"], mp["yaw"]) if mp else None
            out = AG.planner.grid_view(x, y, r, robot=robot, as_json=want_json) if AG.planner else None
            if out is None:
                return self.send_json(503, {"error": "planner busy or no map; try again"})
            if want_json:
                return self.send_json(200, out)
            self.send_bytes(out, "image/png")
        elif self.path.split("?")[0] == "/nav/plan":
            # preview a route: ?place=<id> or ?x=&y=, from where the robot is now
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            mp = AG.map_pose_now()
            if mp is None:
                return self.send_json(409, {"error": "not lined up with the map"})
            try:
                if "place" in q:
                    gx, gy, _, _ = AG._goal({"place": q["place"][0]})
                else:
                    gx, gy = float(q["x"][0]), float(q["y"][0])
            except (KeyError, ValueError, RuntimeError) as e:
                return self.send_json(400, {"error": str(e)})
            AG.update_live()
            self.send_json(200, AG.planner.plan(mp["x"], mp["y"], gx, gy))
        elif self.path.split("?")[0] == "/markers":
            # markers in view now: [{id, mark, z (m along the camera axis), x (m, + right), bearing_deg, side_px}]
            self.send_json(200, MARKERS.snapshot() if MARKERS else {"list": []})
        elif self.path.split("?")[0] == "/trail/coverage":
            self.send_json(200, TRAIL.coverage())
        elif self.path.startswith("/trail/") and self.path.endswith(".jpg"):
            f = TRAIL.path(self.path[len("/trail/"):])
            if f is None:
                return self.send_error(404)
            with open(f, "rb") as fh:
                self.send_bytes(fh.read(), "image/jpeg")
        elif self.path.split("?")[0] == "/map/grid.json":
            # the saved map + height layers + keep-outs + map_id, for offline coverage (cheetah's patrol brain)
            out = go2_patrol.grid_json(MAPPER, KEEPOUT)
            if out is None:
                return self.send_json(503, {"error": "no map"})
            self.send_json(200, out)
        elif self.path.split("?")[0] == "/map/keepout":
            self.send_json(200, {"zones": KEEPOUT.zones()})
        elif self.path.split("?")[0] == "/patrol/views":
            # candidate viewpoints with geometry (places, Oliver's dwell spots, sampled cells x 8 headings): keep-out,
            # seen_n / last_seen_t from trail + patrol frames near the pose, route_m / est_s from the dog now
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            try:
                limit = max(1, min(int(q.get("limit", [400])[0]), 3000))
            except ValueError:
                return self.send_error(400, "limit must be an integer")
            sampled = q.get("sampled", ["1"])[0] not in ("0", "")
            self.send_json(200, go2_patrol.views(AG, KEEPOUT, TRAIL, AG.places(), PRIOR_DIR, PATROLS, sampled, limit))
        elif self.path.split("?")[0] == "/patrol/prior":
            out, err = go2_patrol.prior(PRIOR_DIR)
            if out is None:
                return self.send_json(503, {"error": f"no driving prior: {err}"})
            self.send_json(200, out)
        elif self.path.split("?")[0] in ("/patrol/prior/REPORT.md", "/patrol/prior/paths.png"):
            name = self.path.split("?")[0].rsplit("/", 1)[1]
            try:
                with open(os.path.join(PRIOR_DIR, name), "rb") as fh:
                    body = fh.read()
            except OSError:
                return self.send_error(404)
            self.send_bytes(body, "text/markdown; charset=utf-8" if name.endswith(".md") else "image/png")
        elif self.path.split("?")[0] == "/patrols":
            self.send_json(200, PATROLS.list())
        elif self.path.startswith("/patrol/") and self.path.split("?")[0].count("/") == 2:
            # /patrol/<patrol_id>: patrol.json + its views (GET /patrol/check etc. fall through to 404)
            out = PATROLS.get(self.path.split("?")[0][len("/patrol/"):])
            if out is None:
                return self.send_error(404)
            self.send_json(200, out)
        elif self.path.startswith("/patrol/"):
            # /patrol/<patrol_id>/<file>: a patrol's files (mount check, views); names are validated, no traversal
            pid, _, rel = self.path.split("?")[0][len("/patrol/"):].partition("/")
            body, ctype = PATROLS.file(pid, rel)
            if body is None:
                return self.send_error(404)
            self.send_bytes(body, ctype)
        elif self.path.split("?")[0] == "/map/layer.png":
            # one height layer, same crop as /map.png: ?layer=mid (desk/table tops) | high | ceiling
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            name = q.get("layer", ["mid"])[0]
            if name not in ("mid", "high", "ceiling"):
                return self.send_error(400, "layer must be mid, high or ceiling")
            body = MAPPER.layer_png(name)
            if body is None:
                return self.send_error(503, "no map")
            self.send_bytes(body, "image/png")
        elif self.path.split("?")[0] == "/map/objects":
            self.send_json(200, load_objects())
        elif self.path.split("?")[0] == "/map/proposals":
            try:
                with open(proposals_path()) as f:
                    self.send_json(200, json.load(f))
            except (OSError, ValueError):
                self.send_json(200, {"items": []})
        elif self.path.split("?")[0] == "/label/detect":
            # the vision model's boxes in one trail frame: ?url=/trail/<day>/<ms>.jpg (a few s the first time)
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            try:
                self.send_json(200, {"boxes": EXAMPLES.detect(q.get("url", [""])[0])})
            except ValueError as e:
                self.send_json(400, {"error": str(e)})
            except OSError as e:
                self.send_json(503, {"error": f"vision model not answering: {e}"})
        elif self.path.split("?")[0] == "/label/examples":
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            exs = EXAMPLES.load()["examples"]
            if q.get("name"):
                exs = [e for e in exs if e["name"] == q["name"][0]]
            self.send_json(200, {"examples": exs})
        elif self.path.split("?")[0] == "/map.png":
            with lock:
                body = map_png["data"]
            if body is None:
                return self.send_error(503, "no map: mapping or localization is not running")
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        elif self.path.split("?")[0] == "/frame.jpg":
            # One full-size frame (1280x720 on the Go2), for vision models that need detail.
            with lock:
                img, t = full["img"], full["t"]
            if img is None:
                self.send_error(503, "no camera frame yet")
                return
            ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
            body = buf.tobytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Frame-Age", f"{time.time() - t:.2f}")
            self.end_headers()
            self.wfile.write(body)
        elif self.path.split("?")[0] == "/camera.jpg":
            # Latest stream frame, newer than ?after=<t>; waits up to 5 s, else 204. The page
            # loops on this, so it picks the camera back up by itself after any restart.
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            try:
                after = float(q.get("after", ["0"])[0])
            except ValueError:
                after = 0.0
            with jpeg_cond:
                jpeg_cond.wait_for(lambda: jpeg["data"] is not None and jpeg["t"] > after, timeout=5)
                data, t = jpeg["data"], jpeg["t"]
            if data is None or t <= after:
                self.send_response(204)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Frame-T", repr(t))
            self.end_headers()
            self.wfile.write(data)
        elif self.path.startswith("/agentchat/"):
            if not self.can_control():
                return self.send_error(403, "Ask the dog only works from the lab network")
            return agent_chat_proxy(self, "GET", self.path[len("/agentchat/"):])
        elif self.path.split("?")[0] in ("/l515", "/l515/", "/l515/status.json", "/l515/cloud.bin"):
            # The bridge's own page (l515_go2_pi4_bridge web.py: colour, depth, 3-D point cloud preview) through this
            # port, for the console's L515 panel (an iframe). Its fetches are rewritten to /l515/...; colour and depth
            # come from the shared cache below, status and cloud are passed through. Its own Record box is hidden
            # (the console records the L515).
            p = self.path.split("?")[0]
            if p == "/l515":
                self.send_response(301); self.send_header("Location", "/l515/"); self.end_headers(); return
            code, body, hdr = L515.passthrough("/" if p == "/l515/" else self.path[5:])
            if code is None:
                return self.send_error(502, "L515 bridge page (port 8081) is not running")
            ctype = hdr.get("Content-Type", "application/octet-stream")
            if p == "/l515/":
                body = L515.embed(body.decode("utf-8", "replace")).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            if hdr.get("X-Frame-T"):
                self.send_header("X-Frame-T", hdr["X-Frame-T"])
            self.end_headers()
            self.wfile.write(body)
        elif self.path.split("?")[0] in ("/l515/color.jpg", "/l515/depth.jpg"):
            # L515 colour / colourised depth (red = near, blue = 5 m+), proxied from the bridge page; newer than
            # ?after=<t>, waits up to 3 s, else 204 (also while the L515 is off).
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            try:
                after = float(q.get("after", ["0"])[0])
            except ValueError:
                after = 0.0
            data, t = L515.frame(self.path.split("?")[0][6:-4], after)
            if data is None:
                self.send_response(204)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Frame-T", repr(t))
            self.end_headers()
            self.wfile.write(data)
        elif self.path.split("?")[0] == "/camera.mjpg":
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()
            last = 0.0
            try:
                while True:
                    with jpeg_cond:
                        jpeg_cond.wait_for(lambda: jpeg["t"] > last, timeout=5)
                        data, last = jpeg["data"], jpeg["t"]
                    if data is None:
                        continue
                    self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                                     + str(len(data)).encode() + b"\r\n\r\n" + data + b"\r\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
        else:
            self.send_error(404)


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Go2 Live Sensors</title>
<style>
:root{--bg:#0f1214;--panel:#171b1e;--line:#262c31;--fg:#dfe5e8;--dim:#7d8a92;--accent:#4fb3a9;
--warn:#e0a84a;--bad:#e06a5a;--x:#e06a5a;--y:#7cc46d;--z:#5b9be0;
--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;--sans:system-ui,-apple-system,"Segoe UI",sans-serif}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.4 var(--sans)}
header{display:flex;flex-wrap:wrap;gap:12px;align-items:baseline;padding:14px 16px;border-bottom:1px solid var(--line)}
h1{font-size:17px;margin:0;font-weight:600;letter-spacing:.01em}
.sub{color:var(--dim);font-size:12px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-left:auto}
.chip{font:11px var(--mono);padding:3px 8px;border-radius:99px;border:1px solid var(--line);color:var(--dim)}
.chip.ok{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 45%,transparent)}
.chip.stale{color:var(--warn);border-color:color-mix(in srgb,var(--warn) 45%,transparent)}
.chip.dead{color:var(--bad);border-color:color-mix(in srgb,var(--bad) 45%,transparent)}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px;padding:12px 16px 24px}
section{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:12px;min-width:0}
h2{margin:0 0 10px;font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--dim);font-weight:600;display:flex;justify-content:space-between}
h2 span{font:11px var(--mono);letter-spacing:0;text-transform:none}
.wide{grid-column:span 2}@media (max-width:700px){.wide{grid-column:auto}}
.kv{display:grid;grid-template-columns:auto 1fr;gap:4px 14px;font:13px var(--mono);font-variant-numeric:tabular-nums}
.kv dt{color:var(--dim)}.kv dd{margin:0;text-align:right}
canvas{width:100%;display:block}
#cam{width:100%;max-height:78vh;aspect-ratio:16/9;object-fit:contain;background:#000;border-radius:3px}
.feet{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.foot{font:12px var(--mono)}.bar{height:8px;background:var(--line);border-radius:4px;overflow:hidden;margin-top:3px}
.bar i{display:block;height:100%;background:var(--accent);width:0;transition:width .1s}
table{width:100%;border-collapse:collapse;font:12px var(--mono);font-variant-numeric:tabular-nums}
th{color:var(--dim);font-weight:400;text-align:right;padding:2px 4px}th:first-child,td:first-child{text-align:left}
td{text-align:right;padding:2px 4px;border-top:1px solid var(--line)}
.legend{font:11px var(--mono);color:var(--dim);display:flex;gap:10px;margin-top:6px}
.drive{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start}
.pad{display:grid;grid-template-columns:repeat(3,64px);grid-template-rows:repeat(3,52px);gap:6px;touch-action:none;user-select:none}
.pad button,.acts button{font:600 13px var(--sans);color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:6px;cursor:pointer}
.pad button small{display:block;font:11px var(--mono);color:var(--dim);font-weight:400}
.pad button.on{background:var(--accent);color:var(--bg);border-color:var(--accent)}
.pad button.on small{color:var(--bg)}
#bstop{background:color-mix(in srgb,var(--bad) 25%,var(--bg));border-color:var(--bad)}
.acts{display:grid;grid-template-columns:repeat(3,auto);gap:6px}.speeds{display:flex;gap:4px;align-items:center;font-size:13px;margin:2px 0 8px}.speeds button{font:12px var(--sans);padding:4px 10px;border-radius:5px;border:1px solid var(--line);background:var(--bg);color:var(--fg);cursor:pointer}.speeds button.on{background:var(--accent);border-color:var(--accent);color:#fff}
.looks{display:grid;gap:6px}.looks small{color:var(--dim);font-weight:400}#lookstate{font:12px var(--mono);color:var(--dim)}.acts button{padding:9px 12px}
button:focus-visible,input:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
button:disabled{opacity:.4;cursor:not-allowed}
.arm{display:flex;gap:8px;align-items:center;font-weight:600}.arm input{width:18px;height:18px}
.dstat{font:12px var(--mono);color:var(--dim);min-height:1.4em}.dstat.live{color:var(--accent)}
.help{font-size:12px;color:var(--dim);max-width:30ch;display:grid;gap:6px}
.recrow{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
#recbtn{display:inline-flex;gap:8px;align-items:center;font:600 14px var(--sans);padding:10px 16px;border-radius:6px;border:1px solid var(--line);background:var(--bg);color:var(--fg);cursor:pointer}
#recbtn i{width:12px;height:12px;border-radius:50%;background:var(--bad)}
#recbtn.on{background:var(--bad);border-color:var(--bad);color:#fff}#recbtn.on i{background:#fff;border-radius:2px}
#gear{font:13px var(--sans);padding:9px 12px;border-radius:6px;border:1px solid var(--line);background:var(--bg);color:var(--fg);cursor:pointer}
.recinfo{font:13px var(--mono);font-variant-numeric:tabular-nums;color:var(--dim)}.recinfo b{color:var(--fg);font-weight:500}
#settings{margin-top:12px;padding:12px;border:1px solid var(--line);border-radius:6px;display:grid;gap:8px;max-width:520px}
#settings label{display:flex;gap:8px;align-items:baseline}#settings small{color:var(--dim)}
.past{margin-top:10px;font:12px var(--mono);color:var(--dim);display:grid;gap:2px}
.err{color:var(--bad)}.autorec{display:inline-flex;gap:6px;align-items:center;font:600 12px var(--sans);color:#fff;background:var(--bad);border-radius:10px;padding:2px 10px}.autorec[hidden]{display:none}.autorec i{width:8px;height:8px;border-radius:50%;background:#fff}
.full{grid-column:1/-1}
section.sz2{grid-column:span 2}section.sz3{grid-column:1/-1}@media (max-width:700px){section.sz2{grid-column:auto}}
h2 .szc{display:inline-flex;gap:2px;margin-left:8px}h2>span:first-of-type{margin-left:auto}
h2 .szc button{font:10px var(--mono);padding:1px 5px;border:1px solid var(--line);border-radius:3px;background:var(--bg);color:var(--dim);cursor:pointer}
h2 .szc button.on{color:var(--accent);border-color:var(--accent)}
.chatlog{min-height:160px;max-height:60vh;overflow:auto;display:flex;flex-direction:column;gap:6px;padding:4px 2px;font:14px/1.45 var(--sans)}
main.free .chatlog{max-height:none}
.chatlog .u{align-self:flex-end;background:var(--accent);color:#fff;padding:6px 10px;border-radius:10px 10px 2px 10px;max-width:85%;white-space:pre-wrap;overflow-wrap:anywhere}
.chatlog .a{align-self:flex-start;background:var(--bg);border:1px solid var(--line);padding:6px 10px;border-radius:10px 10px 10px 2px;max-width:92%;white-space:pre-wrap;overflow-wrap:anywhere}
.chatlog .tl{font:12px var(--mono);color:var(--dim);overflow-wrap:anywhere}.chatlog .tl b{color:var(--fg);font-weight:500}.chatlog .tl .ok{color:var(--accent)}.chatlog .tl .no{color:var(--bad)}
.chatlog .ph{display:flex;gap:6px;flex-wrap:wrap}.chatlog .ph img{width:140px;aspect-ratio:16/9;object-fit:cover;border-radius:4px;cursor:zoom-in;background:#000}
.chatlog .meta{font:11px var(--mono);color:var(--dim)}.chatlog .err{color:var(--bad);font:12px var(--mono)}.chathint{color:var(--dim);font-size:12px}
.chatform{display:grid;gap:6px;margin-top:6px}#chatin{width:100%;font:15px var(--sans);padding:8px;border-radius:6px;border:1px solid var(--line);background:var(--bg);color:var(--fg);resize:vertical}
.chatbar{display:flex;gap:6px;flex-wrap:wrap;align-items:center}.chatbar button,.chatbar select{font:13px var(--sans);padding:7px 12px;border-radius:6px}
.chatstop{background:#a33!important;color:#fff!important;border-color:#a33!important;font-weight:700!important;padding:7px 20px!important}.chatstop:disabled{opacity:.4}
#chatst.busy::before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--accent);margin-right:6px;animation:chatp 1s infinite}
@keyframes chatp{50%{opacity:.2}}
@media (max-width:699px){main>#ctlbar{order:-2}main>#chatsec{order:-1;grid-column:1/-1}#chatin{font-size:16px;min-height:3.4em}.chatbar button,.chatbar select{padding:10px 14px;font-size:15px}.chatstop{flex:1}}
.motchip{font:12px var(--mono);padding:3px 8px;border-radius:99px;border:1px solid var(--line);color:var(--fg);cursor:pointer;user-select:none}
.motchip.warm{background:#4d3b12;border-color:#a77d1c;color:#ffe6a8}.motchip.hot{background:#5a1f1f;border-color:#a33;color:#ffd7d7;font-weight:700}
.motchip.stale{color:var(--dim)}
.motwarn{flex-basis:100%;order:3;display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-weight:600;padding:8px 10px;border-radius:6px;background:#4d3b12;color:#ffe6a8}
.motwarn.hot{background:#5a1f1f;color:#ffd7d7}.motwarn[hidden]{display:none}.motwarn button{font-weight:700;padding:6px 16px}
.dogst{display:flex;gap:8px;align-items:center;font:12px var(--mono);color:var(--dim);flex-wrap:wrap}
.dogst b{font:700 14px var(--sans);letter-spacing:.06em;padding:4px 12px;border-radius:6px;border:1px solid var(--line);color:var(--fg)}
.dogst b.off{background:#5a1f1f;border-color:#a33;color:#ffd7d7}.dogst b.idle{background:#4d3b12;border-color:#a77d1c;color:#ffe6a8}
.dogst b.active{background:#1f4d36;border-color:#2f8a5f;color:#c9f5dc}
#deployov{position:fixed;inset:0;z-index:1000;background:rgba(10,12,14,.93);display:grid;place-items:center;padding:16px}#deployov[hidden]{display:none}
#deployov>div{max-width:34em;text-align:center;display:grid;gap:12px;font:15px/1.5 var(--sans);color:var(--fg)}#deployov b{font-size:19px}
#deployov small{color:var(--dim);font:12px var(--mono)}#deployov button{justify-self:center;padding:8px 22px;font-weight:600}
.l515v{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:10px}.l515v figure{margin:0;min-width:0}
.l515v img{width:100%;display:block;border-radius:4px;background:#000}.l515v figcaption{font:11px var(--mono);color:var(--dim);margin-top:4px}
#l515f{width:100%;min-height:320px;border:0;display:block;background:transparent}#l515f[hidden]{display:none}
.l515off[hidden]{display:none}  /* the bug behind "waiting for L515 frames…": display:grid beat [hidden] */
.l515off{aspect-ratio:4/3;display:grid;place-items:center;border-radius:4px;background:var(--bg);border:1px dashed var(--line);color:var(--dim);font:12px var(--mono);text-align:center;padding:8px}
.mknote{font:12px var(--mono);color:var(--dim);margin-top:6px}.mknote b{color:var(--warn);font-weight:600}
h2 .grip{font-style:normal;font-size:14px;line-height:1;margin:-2px 6px 0 -2px;padding:0 2px;color:var(--dim);cursor:grab;touch-action:none;user-select:none;-webkit-user-select:none}h2 .grip:hover{color:var(--accent)}
main.free{grid-template-columns:repeat(12,minmax(0,1fr));grid-template-rows:auto;grid-auto-rows:var(--rowh,40px);align-items:stretch}
main.free>section:not(.ctlbar){display:flex;flex-direction:column;overflow:hidden;position:relative;min-height:0}
/* the panel frame does not scroll; its body does, inside the frame's padding, so no scrollbar sits under the resize
   handles (which live on the frame, in the padding, above the body) */
.pbody{min-width:0}main.free .pbody{flex:1 1 auto;min-height:0;overflow:auto;display:flex;flex-direction:column;margin-bottom:8px}  /* ends where the 20 px corner handle starts */
main.free>section.ctlbar{grid-column:1/-1;grid-row:1}main.free>section[hidden]{display:none}
main.free .fill{flex:1 1 0;min-height:80px}main.free #cam{max-height:none;aspect-ratio:auto;height:auto}
main.free #l515f{min-height:120px}main.free .l515off{aspect-ratio:auto}
main.free h2.draghd{cursor:grab;user-select:none;-webkit-user-select:none;touch-action:none}
.rsz,.rsz-r,.rsz-b{display:none}
main.free .rsz{display:block;position:absolute;right:0;bottom:0;width:20px;height:20px;cursor:nwse-resize;touch-action:none;z-index:6;
 background:linear-gradient(135deg,transparent 52%,var(--dim) 52%,var(--dim) 60%,transparent 60%,transparent 70%,var(--dim) 70%,var(--dim) 78%,transparent 78%,transparent 86%,var(--dim) 86%,var(--dim) 94%,transparent 94%);
 background-size:14px 14px;background-position:right 2px bottom 2px;background-repeat:no-repeat;opacity:.7;border-bottom-right-radius:6px}
main.free .rsz:hover{opacity:1;background-color:color-mix(in srgb,var(--accent) 18%,transparent)}
main.free .rsz-r{display:block;position:absolute;top:36px;right:0;bottom:20px;width:8px;cursor:ew-resize;touch-action:none;z-index:5}
main.free .rsz-b{display:block;position:absolute;left:0;right:20px;bottom:0;height:8px;cursor:ns-resize;touch-action:none;z-index:5}
main.free .rsz-r:hover,main.free .rsz-b:hover{background:color-mix(in srgb,var(--accent) 25%,transparent)}
.lghost{pointer-events:none;border:1.5px dashed var(--accent);border-radius:6px;background:color-mix(in srgb,var(--accent) 8%,transparent);z-index:0}.lghost[hidden]{display:none}
main>section.dragging{z-index:5;box-shadow:0 8px 30px rgba(0,0,0,.45);opacity:.85;outline:2px dashed var(--accent);outline-offset:2px}body.dragging,body.dragging *{cursor:grabbing!important;user-select:none;-webkit-user-select:none}
#resetlayout{font:11px var(--mono);padding:3px 8px;border-radius:5px;border:1px solid var(--line);background:var(--bg);color:var(--dim);cursor:pointer}#resetlayout:hover{color:var(--fg)}
.mapzoom{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:0 0 6px;font:11px var(--mono);color:var(--dim)}
.mapzoom button{font:12px var(--mono);min-width:28px;padding:3px 7px;border-radius:4px;border:1px solid var(--line);background:var(--bg);color:var(--fg);cursor:pointer}
.mapzoom label{display:inline-flex;gap:4px;align-items:center}
.maplayers{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:0 0 8px;font:12px var(--sans);color:var(--fg)}.maplayers>span{color:var(--dim);font:11px var(--mono)}
.maplayers label{display:inline-flex;gap:5px;align-items:center;padding:3px 10px 3px 6px;border:1px solid var(--line);border-radius:99px;background:var(--bg);cursor:pointer;user-select:none}
.maplayers label:has(input:checked){border-color:var(--accent);color:var(--accent)}.maplayers input{margin:0;accent-color:var(--accent)}.maplayers i{width:9px;height:9px;border-radius:2px;display:inline-block}
#map{touch-action:none}
.mapctl{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-top:8px}
#placedog.on{border-color:var(--accent,#2b6cb0);color:var(--accent,#2b6cb0);font-weight:600}
#map.placing{cursor:crosshair}
#propsec{--prop:#c77dff}.propbar{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;font-size:12px}.propbar label{display:inline-flex;gap:4px;align-items:center}
#propsec .propbar button,#propsec .pbtns button,#propbig button{font:12px var(--sans);padding:4px 9px;border-radius:5px;border:1px solid var(--line);background:var(--bg);color:var(--fg);cursor:pointer}
#propsec .pbtns button.ok{border-color:var(--accent);color:var(--accent)}#propsec small{color:var(--dim);font:11px var(--mono)}
.prow{border-top:1px solid var(--line);padding:8px 6px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 10px;cursor:pointer;border-left:3px solid transparent}
.prow.hl{border-left-color:var(--prop);background:color-mix(in srgb,var(--prop) 9%,transparent)}.prow.rev{opacity:.55}
.prow .ps{font-size:13px}.pk{font:10px var(--mono);color:var(--prop);border:1px solid color-mix(in srgb,var(--prop) 50%,transparent);border-radius:99px;padding:0 6px;margin-right:6px;white-space:nowrap}
.pconf{display:inline-block;vertical-align:middle;width:90px;height:5px;background:var(--line);border-radius:3px;margin-right:6px}.pconf i{display:block;height:100%;border-radius:3px;background:var(--accent)}.pconf i.lo{background:var(--warn)}
.preason{color:var(--dim);font-size:12px}.pflag{display:inline-block;color:var(--warn);font:11px var(--mono);border:1px solid color-mix(in srgb,var(--warn) 45%,transparent);border-radius:99px;padding:0 6px;margin:2px 4px 0 0}
.pev{display:flex;gap:4px;margin-top:4px}.pev img{width:84px;aspect-ratio:16/9;object-fit:cover;border-radius:2px;background:#000;cursor:zoom-in}
.pbtns{display:flex;flex-direction:column;gap:4px}.pstat{font:11px var(--mono);color:var(--dim)}#propbig{margin-top:8px}#propbig img{width:100%;border-radius:4px;display:block;margin-bottom:6px}
.mapzoom button.on{border-color:var(--accent);color:var(--accent)}
.edithint[hidden]{display:none}.edithint{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;margin:0 0 8px;padding:6px 8px;border:1px dashed var(--accent);border-radius:5px;font:11px var(--mono);color:var(--fg)}.edithint label{display:inline-flex;gap:4px;align-items:center;color:var(--accent)}.edithint small{color:var(--dim)}.edithint button{font:11px var(--mono);padding:2px 7px;border-radius:4px;border:1px solid var(--accent);background:var(--bg);color:var(--fg);cursor:pointer}.edithint button.on{background:var(--accent);color:var(--bg)}
.mapctl button{font:12px var(--sans);padding:5px 9px;border-radius:5px;border:1px solid var(--line);background:var(--bg);color:var(--fg);cursor:pointer}
.mapstatus{flex-basis:100%;font:12px var(--mono);color:var(--dim)}
.maprow{display:grid;gap:6px;border-top:1px solid var(--line);padding-top:10px}
.mapstate{font:12px var(--mono);color:var(--dim)}.mapstate.on{color:var(--accent)}
.mapbtns{display:flex;flex-wrap:wrap;gap:6px}
.mapbtns button{font:600 13px var(--sans);color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:6px;cursor:pointer;padding:9px 12px}
.ctlbar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between}
.chip.bhi{color:var(--y);border-color:color-mix(in srgb,var(--y) 45%,transparent)}.battwarn{flex-basis:100%;order:3;color:var(--bad);font-weight:600;display:flex;gap:10px;align-items:center}.battwarn[hidden]{display:none}.battwarn button{font:11px var(--mono);padding:1px 7px;border:1px solid var(--line);border-radius:4px;background:var(--bg);color:var(--dim);cursor:pointer}
.ctlbar.agent{border-color:var(--warn);background:color-mix(in srgb,var(--warn) 10%,var(--panel))}
.ctlbar.human{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 10%,var(--panel))}
#ctltext{font-size:15px}#ctltext small{display:block;color:var(--dim);font:12px var(--mono);margin-top:2px}
.ctlbtns{display:flex;gap:8px}
.ctlbtns button{font:600 14px var(--sans);padding:10px 16px;border-radius:6px;border:1px solid var(--line);background:var(--bg);color:var(--fg);cursor:pointer}
#takeover{background:var(--bad);border-color:var(--bad);color:#fff}
.agview{display:grid;grid-template-columns:minmax(0,3fr) minmax(0,2fr);gap:12px}@media (max-width:800px){.agview{grid-template-columns:1fr}}
.agview figure{margin:0}.agview img#agimg{width:100%;aspect-ratio:16/9;object-fit:contain;background:#000;border-radius:3px;display:block}
.agview figcaption,.agnow{font:12px var(--mono);color:var(--dim);margin-top:6px}
.agnow b{color:var(--fg);font-weight:500}
.thumbs{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:8px 0}
.thumbs img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:3px;cursor:pointer;border:2px solid transparent}
.thumbs img.sel{border-color:var(--accent)}
#aglog{width:100%;border-collapse:collapse;table-layout:fixed;font:12px var(--mono);font-variant-numeric:tabular-nums}#aglog td{text-align:left;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:2px 8px 2px 0;vertical-align:baseline;line-height:1.45}#aglog td:nth-child(1){width:calc(8ch + 10px);color:var(--dim)}#aglog td:nth-child(2){width:calc(17ch + 10px);color:var(--dim)}#aglog td:nth-child(4){width:32%;padding-right:2px}#aglog b{font-weight:600;color:var(--fg)}#aglog .lgargs{color:var(--dim)}#aglog td.ok{color:var(--accent)}#aglog tr.row{cursor:pointer}#aglog tr.row:hover td{background:var(--line)}#aglog tr.row.open td{background:var(--panel);border-top:1px solid var(--line)}#aglog tr.det td{white-space:normal;padding:0 0 6px calc(8ch + 10px);border-bottom:1px solid var(--line)}.lgnote{margin:2px 0 4px;font:13px/1.45 var(--sans);color:var(--fg);overflow-wrap:anywhere}.lgkv{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,24em),1fr));gap:0 20px;font:12px/1.45 var(--mono)}.lgkv>div{display:grid;grid-template-columns:9ch minmax(0,1fr);gap:0 8px}.lgkv>div>span:first-child{color:var(--dim);font-size:11px;overflow:hidden;text-overflow:ellipsis}.lgkv>div>span+span{overflow-wrap:anywhere;color:var(--fg)}.lgkv .ok{color:var(--accent)!important}.lgkv .err{color:var(--bad)!important}.aglogw{margin-top:6px}@media (max-width:520px){#aglog td:nth-child(2){display:none}#aglog tr.det td{padding-left:0}}.loghd{display:flex;gap:8px;align-items:center;margin-top:8px;font-size:12px;color:var(--dim)}.loghd button{font:12px var(--sans);padding:2px 8px}
.pl{display:grid;grid-template-columns:64px 1fr auto auto;gap:8px;align-items:center;font-size:13px;padding:4px 0;border-top:1px solid var(--line)}
.pl img{width:64px;aspect-ratio:16/9;object-fit:cover;border-radius:3px;background:#000}.pl small{color:var(--dim);font:11px var(--mono);display:block}
.pl button,#plform button{font:12px var(--sans);padding:5px 9px;border-radius:5px;border:1px solid var(--line);background:var(--bg);color:var(--fg);cursor:pointer}
#plform,#dropform{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
#map{cursor:crosshair}
#lblsec div button,#lblsec form button{font:12px var(--sans);padding:5px 9px;border-radius:5px;border:1px solid var(--line);background:var(--bg);color:var(--fg);cursor:pointer}#lblsec div button.on{border-color:var(--accent);color:var(--accent)}
#lblsec input:not([type=checkbox]),#lblsec select{font:13px var(--sans);padding:5px 8px;border-radius:5px;border:1px solid var(--line);background:var(--bg);color:var(--fg);min-width:0}
#lblsec small{color:var(--dim);font:11px var(--mono)}.lblsrc,#lblform{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:13px}#lblform{margin-top:8px}#lblname{flex:1 1 140px}
#lblform label{display:inline-flex;gap:5px;align-items:center;font-size:12px}
.lblthumbs{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:6px;max-height:300px;overflow:auto;margin-top:8px}
.lblthumbs figure,.lblexs figure{margin:0;cursor:pointer;border:2px solid transparent;border-radius:4px}.lblthumbs figure.sel{border-color:var(--accent)}
.lblthumbs img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;background:#000;border-radius:2px}
.lblthumbs figcaption,.lblexs figcaption{font:10px var(--mono);color:var(--dim);padding:2px;display:flex;justify-content:space-between;align-items:center;gap:4px}
.lblthumbs figcaption{flex-wrap:wrap;row-gap:0}.lblthumbs figcaption span{white-space:nowrap}
.lblstage{position:relative;margin-top:10px;line-height:0}.lblstage img{width:100%;display:block;border-radius:4px;background:#000;min-height:60px}
#lblov{position:absolute;inset:0;touch-action:none;cursor:crosshair;user-select:none;-webkit-user-select:none}
.lbox{position:absolute;border:2px dashed var(--warn);pointer-events:none}.lbox span{position:absolute;left:-2px;top:-17px;font:11px/15px var(--mono);background:rgba(15,18,20,.85);color:var(--warn);padding:0 4px;white-space:nowrap}
.lbox.sel{border:3px solid var(--accent)}.lbox.sel span{color:var(--accent)}
.lblexs{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:6px;margin-top:6px}.lblexs .exw{position:relative;line-height:0}.lblexs img{width:100%;display:block;border-radius:2px;background:#000}
.lblexs .lbox{border-width:2px;border-style:solid;border-color:var(--accent)}#lblsec .lblexs button{font:10px var(--mono);padding:1px 6px}
#objp,#addp{margin-top:10px;padding-top:10px;border-top:1px solid var(--line);font-size:13px}:is(#objp,#addp) .droph{display:flex;flex-wrap:wrap;gap:8px;align-items:center}:is(#objp,#addp) small{color:var(--dim);font:11px var(--mono)}
:is(#objp,#addp) form{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}:is(#objp,#addp) input{flex:1 1 120px;min-width:0;font:13px var(--sans);padding:6px 8px;border-radius:5px;border:1px solid var(--line);background:var(--bg);color:var(--fg)}
:is(#objp,#addp) form label{display:inline-flex;gap:4px;align-items:center;font:11px var(--mono);color:var(--dim)}:is(#objp,#addp) label input{flex:0 0 72px;width:72px}
:is(#objp,#addp) button{font:12px var(--sans);padding:5px 9px;border-radius:5px;border:1px solid var(--line);background:var(--bg);color:var(--fg);cursor:pointer}#objp .objsw{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px}
#drop{margin-top:10px;padding-top:10px;border-top:1px solid var(--line);font-size:13px}
#drop .droph{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
#drop small{color:var(--dim);font:11px var(--mono)}
#dropbig{width:100%;aspect-ratio:16/9;object-fit:contain;background:#000;border-radius:4px;margin-top:8px;display:block}
#dropviews{display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:6px;margin-top:8px}
#dropviews figure{margin:0;cursor:pointer;border:2px solid transparent;border-radius:4px}
#dropviews figure.sel{border-color:var(--accent)}
#dropviews img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;border-radius:2px;background:#000}
#dropviews figcaption{font:10px var(--mono);color:var(--dim);padding:2px}
#drop button,#dropform button{font:12px var(--sans);padding:5px 9px;border-radius:5px;border:1px solid var(--line);background:var(--bg);color:var(--fg);cursor:pointer}
#dropform input[type=text],#plform input{flex:1 1 120px;min-width:0;font:13px var(--sans);padding:6px 8px;border-radius:5px;border:1px solid var(--line);background:var(--bg);color:var(--fg)}
.legend b{font-weight:400}.lx{color:var(--x)}.ly{color:var(--y)}.lz{color:var(--z)}
</style></head><body>
<header><h1>Go2 Live Sensors</h1><span class="sub" id="conn">connecting…</span><span id="autorec" class="autorec" role="status" title="Every session with the dog is saved automatically to ~/oliver/go2_recordings (auto_*)" hidden><i></i>auto recording</span>
<div class="dogst" id="dogst" role="status"><b id="dogstb">…</b><span id="dogstt"></span><span id="motst" class="motchip" role="button" tabindex="0" hidden title="Motor temperatures"></span><span id="l515stc"></span><span id="wdst"></span></div><div class="chips" id="chips"></div><button id="resetlayout" type="button" title="Put every panel back in its default place and size">Reset layout</button></header>
<main>
<section class="full ctlbar" id="ctlbar"><div id="ctltext">Control: checking…</div>
<div class="ctlbtns"><button id="takeover">Take over</button><button id="handback" hidden>Hand back to agents</button></div><div class="motwarn" id="motwarn" role="alert" hidden><span id="motwarntxt"></span><button type="button" id="motlie" title="Lie the dog down (what the Drive panel's Lie down does)">Lie down</button></div><div class="battwarn" id="battwarn" role="alert" hidden><span id="battwarntxt"></span><button type="button" id="battwarnx" title="Hide until the next 10% drop">ok</button></div></section>
<section class="full"><h2>Live camera <span id="camage"></span></h2><img id="cam" class="fill" alt="Front camera stream"><div class="mknote" id="mknote"></div></section>
<section class="wide" id="l515sec"><h2>L515 depth camera <span id="l515st">checking…</span></h2>
<iframe id="l515f" class="fill" title="L515 live view: colour, depth and 3-D point cloud (the bridge page, through this console)" hidden></iframe>
<div class="l515off fill" id="l515off">checking…</div></section>
<section class="wide" id="chatsec"><h2>Ask the dog <span id="chatst"></span></h2>
<div id="chatlog" class="chatlog fill" aria-live="polite"><div class="chathint">Ask a question, or ask the dog to go somewhere or look for something. The agent only has the robot tools; Take over or STOP always wins.</div></div>
<form id="chatform" class="chatform"><textarea id="chatin" rows="2" placeholder="Ask the dog… (Enter sends, Shift+Enter for a new line)" aria-label="Message for the dog's agent"></textarea>
<div class="chatbar"><select id="chatmodel" aria-label="Model"><option value="opus">Opus</option><option value="sonnet">Sonnet</option></select>
<button type="submit" id="chatsend">Send</button><button type="button" id="chatstop" class="chatstop" disabled>Stop</button><button type="button" id="chatnew">New conversation</button></div></form></section>
<section class="wide"><h2>Drive <span id="dnote"></span></h2><div class="drive">
<div class="pad" id="pad">
<button data-k="q">↺<small>Q</small></button><button data-k="w">↑<small>W</small></button><button data-k="e">↻<small>E</small></button>
<button data-k="a">←<small>A</small></button><button id="bstop">STOP<small>space</small></button><button data-k="d">→<small>D</small></button>
<span></span><button data-k="s">↓<small>S</small></button><span></span></div>
<div style="display:grid;gap:10px">
<label class="arm"><input type="checkbox" id="armed"> Enable driving</label>
<label class="arm"><input type="checkbox" id="avoid"> Obstacle avoidance</label>
<div class="speeds" id="speeds">Speed <button data-sp="slow">Slow</button><button data-sp="normal">Normal</button><button data-sp="fast">Fast</button></div>
<div class="acts"><button data-a="stand">Stand up</button><button data-a="lie">Lie down</button></div>
<div class="looks"><strong>Camera tilt</strong> <span id="lookstate">level</span>
<div class="acts"><button data-look="6">Look up<small> R</small></button><button data-look="0">Level</button><button data-look="-6">Look down<small> F</small></button></div></div>
<div class="maprow"><strong>Mapping</strong> <span id="mapstate" class="mapstate">…</span>
<div class="mapbtns"><button data-map="start" data-when="idle">Start mapping</button><button data-map="save" data-when="mapping">Stop and save</button>
<button data-map="clear" data-when="any">Clear map</button><button data-map="revert" data-when="any">Back to saved map</button></div></div>
<div class="dstat" id="dstat">Disarmed</div></div>
<div class="help"><span>Tick Enable driving first; it's a safety switch so stray clicks and keys do nothing.</span>
<span>Hold a direction to move; letting go stops the dog within 0.3 s. Keys work while this tab is focused.</span>
<span><span id="speedtxt"></span> Backing up is always capped at 0.25 m/s: the dog barely sees behind itself. STOP always wins over agents.</span>
<span>One person drives at a time. Anyone can press STOP.</span>
<span>Look up / down tilts the whole body while standing still, about 6° per press, up to 30°. It levels off by itself when you drive.</span>
<span>Obstacle avoidance makes the dog slow down and stop near obstacles. It applies to this page only, not the terminal controller.</span></div>
</div></section>
<section class="wide" id="agsec" hidden><h2>Photos taken by agents <span id="agcount"></span></h2>
<div class="agview"><figure><img id="agimg" alt="Latest photo taken by an agent" hidden><figcaption id="agcap">No agent photos yet. Photos appear here when an agent calls photo or look_around.</figcaption></figure>
<div><div class="agnow" id="agnow"></div><div class="thumbs" id="agthumbs"></div></div></div>
<div class="aglogw"><div class="loghd">Agent calls (click a row for the full text) <button id="logall">Show all in full</button></div><table id="aglog"></table></div></section>
<section class="wide"><h2>Recording <span id="recnote"></span></h2>
<div class="recrow"><button id="recbtn"><i></i><span>Record</span></button>
<button id="gear" aria-expanded="false" aria-controls="settings">Settings</button>
<span class="recinfo" id="recinfo"></span></div>
<div id="settings" hidden>
<strong>What to record</strong>
<label><input type="checkbox" id="r_camera" checked> Camera <small>front camera, raw 1280×720 at ~5 fps, about 50 GB/hour</small></label>
<label><input type="checkbox" id="r_lidar" checked> Lidar <small>point cloud at ~7 Hz, about 25 GB/hour</small></label>
<label><input type="checkbox" id="r_l515" checked> L515 depth camera <small>colour JPEG + raw 16-bit depth at up to 10 fps, about 20 GB/hour (manual bags are not compressed); skipped if the L515 is off</small></label>
<label><input type="checkbox" id="r_pose" checked> Robot pose <small>odometry, IMU, joints, transforms; tiny, needed to line lidar frames up</small></label>
<small>Saved as ROS 2 bags in ~/oliver/go2_recordings on the control PC. These settings are remembered in this browser.</small>
<small>Auto recording saves every session by itself (auto_* folders: camera as JPEG, lidar, pose, L515 colour + depth when it is on, console events; about 4 GB/hour, about 12 GB/hour with the L515). It starts when the dog connects and stops when it disconnects or has been idle for 4 minutes. Stop recording during it pauses it until the dog reconnects.</small>
</div>
<div class="past" id="past"></div></section>
<section><h2>Lidar, top view <span id="cloudinfo"></span></h2><canvas id="cloud" class="fill" width="600" height="600"></canvas>
<div class="legend">grid lines every 2 m · grey = open floor seen · yellow→red = obstacle 10 cm→1.2 m tall · arrow = robot heading</div></section>
<section class="wide"><h2>Map <span id="mapinfo"></span></h2><div class="mapzoom"><button id="zin" type="button" title="Zoom in (or scroll on the map)">+</button><button id="zout" type="button" title="Zoom out">−</button><button id="zfit" type="button" title="Show the whole map">Fit</button><label><input type="checkbox" id="zfollow"> follow dog</label><span>labels</span><button id="lsm" type="button" title="Smaller labels">A−</button><button id="llg" type="button" title="Bigger labels">A+</button><label title="Turn the drawing so the room's walls run straight across and up; the map itself is unchanged">view <select id="zrot"><option value="north">North up</option><option value="room">Room square</option></select></label><button id="editpl" type="button" title="Drag places (and a selected object) on the map">Edit places</button><span id="zinfo"></span></div>
<div class="edithint" id="edithint" hidden><span>drag a place's dot to move it · drag its arrow tip to turn it · drag the ◆ to move the thing itself · drag a selected object's centre ■ to move it · drag a tag's spot to move it, and drag the circle at the arrow tip so the arrow points out of the tag's printed face, into the room · Esc or the button to finish</span><button type="button" id="addobj" title="Then click the map where the object or marker is">Add object</button><label><input type="checkbox" id="snapw" checked> snap to walls</label><small>hold Shift to place freely</small></div>
<div class="maplayers"><span>Show:</span><label title="Desk and table tops"><input type="checkbox" data-layer="mid"><i style="background:rgb(230,140,40)"></i>Desk tops</label><label title="Shelves, cabinet tops, door frames"><input type="checkbox" data-layer="high"><i style="background:rgb(160,90,220)"></i>High</label><label title="Ceiling height: darker = lower"><input type="checkbox" data-layer="ceiling"><i style="background:linear-gradient(90deg,#444,#ccc)"></i>Ceiling</label><label title="Labelled objects; click one to rename, relabel, confirm or delete it"><input type="checkbox" data-layer="objects"><i style="border:1.5px dashed var(--warn)"></i>Objects</label></div><canvas id="map" class="fill" width="600" height="600"></canvas>
<div class="legend" id="maplegend">white = open floor · black = walls and furniture · grey = not seen yet · arrow = robot · dots = places (line to where the dog stands to see it) · dashed = agent route · green / red squares = what the lidar sees now clears / adds for route planning · click the map to mark a place</div>
<div class="mapctl"><span id="mapstatus" class="mapstatus"></span>
<button data-map="new" data-when="idle">Start new map</button><button data-map="extend" data-when="idle">Extend map</button>
<button data-map="save" data-when="mapping">Stop and save</button><button data-map="stop" data-when="mapping">Stop without saving</button><button data-map="align" data-when="idle">Line up again</button><button id="placedog" type="button" title="Click on the map where the dog is now; drag toward where it faces if you know. The console then works out the exact spot and heading near there.">Set dog position</button><button data-map="revert" data-when="any">Back to saved map</button></div>
<div id="drop" hidden>
<div class="droph"><strong>New place at <span id="dropxy"></span></strong><span id="dropspot"></span><button id="dropx" type="button">Cancel</button></div>
<small id="dropvnote"></small>
<img id="dropbig" alt="Camera view picked for this place" hidden>
<div id="dropviews"></div>
<small id="dropstandnote"></small>
<form id="dropform"><input type="text" id="dropid" placeholder="name, e.g. Joseph's desk" maxlength="60" required><input type="text" id="droppdesc" placeholder="what is here"><button>Save place</button></form>
<small id="dropmsg"></small>
</div>
<div id="objp" hidden>
<div class="droph"><strong id="objtitle"></strong><small id="objmeta"></small><button id="objx" type="button">Close</button></div>
<form id="objren"><input type="text" id="objname" placeholder="name, e.g. oliver's desk"><button>Rename</button></form>
<form id="objrel"><input type="text" id="objlabel" list="objlabels" placeholder="label, e.g. desk"><datalist id="objlabels"></datalist><button>Relabel</button>
<button type="button" id="objrot" title="Line its sides up with the room's walls">Rotate to room</button><button type="button" id="objok">Confirm</button><button type="button" id="objdel">Delete</button></form>
<form id="objset"><label title="ArUco tag id 0-49 (4x4_50); empty = not a tag">tag id <input type="number" id="objaruco" min="0" max="49" step="1" placeholder="none"></label><label>w m <input type="number" id="objw" min="0.05" max="30" step="0.05" required></label><label>h m <input type="number" id="objh" min="0.05" max="30" step="0.05" required></label><label title="map degrees, 0 = map +x, 90 = +y; for a marker, the way its printed face looks out">faces ° <input type="number" id="objyaw" step="1" required></label><button>Save</button></form>
<small id="objmsg"></small>
</div>
<div id="addp" hidden>
<div class="droph"><strong>New object at <span id="addxy"></span></strong><button id="addx" type="button">Cancel</button></div>
<form id="addform"><input type="text" id="addname" placeholder="name, e.g. tag_A or Joseph's desk" maxlength="60" required autocomplete="off"><input type="text" id="addlabel" list="objlabels" placeholder="label, e.g. aruco marker" maxlength="40">
<label title="ArUco tag id 0-49 (4x4_50); leave empty for a plain object">tag id <input type="number" id="addaruco" min="0" max="49" step="1" placeholder="none"></label><label title="map degrees, 0 = map +x, 90 = +y">faces ° <input type="number" id="addyaw" step="1" value="0"></label><button>Add</button></form>
<small>A tag (the printed ArUco square) is an object with a tag id. Mount it flat on furniture or a wall; "faces" is the way its printed face looks out, away from the wall (in Edit places, drag the circle at the arrow tip so the arrow points out of the tag's printed face, into the room). Size defaults to 0.4 × 0.4 m.</small>
<small id="addmsg"></small>
</div></section>
<section class="wide" id="lblsec"><h2>Label from photos <span id="lblnote"></span></h2>
<div class="lblsrc"><label>Days <select id="lbldays"><option value="today">Today</option><option value="drive">Today since 14:31 (mapping drive)</option><option value="2d">Last 2 days</option><option value="all">All</option></select></label><label>Photos since <input type="time" id="lblsince" value="00:00"></label><button id="lblload" type="button">Load</button>
<span>or</span><button id="lblspot" type="button" title="Then click a spot on the map to get the photos that looked at it">Pick spot on map</button><small id="lblsrcnote"></small></div>
<div class="lblthumbs" id="lblthumbs"></div><button id="lblmore" type="button" hidden>Load more</button>
<div id="lblwork" hidden>
<div class="lblstage"><img id="lblimg" alt="Camera photo to label"><div id="lblov"></div></div>
<small id="lbldet"></small>
<form id="lblform"><input type="text" id="lblname" list="lblnames" placeholder="name, e.g. Oliver's desk" maxlength="60" required autocomplete="off"><datalist id="lblnames"></datalist>
<select id="lbllabel"></select><label><input type="checkbox" id="lblplace"> also save as a place to go to</label><button>Add example</button></form>
<small id="lblmsg"></small>
</div>
<div id="lblexwrap" hidden><small id="lblexnote"></small><div class="lblexs" id="lblexs"></div></div>
<div class="legend">Pick photos that show one thing, click a suggested box or drag your own around it, name it and add it. Two or more photos from different spots place it best. The thing appears on the map under Objects.</div></section>
<section class="wide" id="propsec"><h2>Map suggestions <span id="propnote"></span></h2>
<div class="propbar"><button id="propall" type="button" title="Accept every pending suggestion with confidence 0.7 or more">Accept all ≥ 0.7</button>
<label><input type="checkbox" id="propshowrev"> show accepted/rejected</label><label><input type="checkbox" id="propmapall"> show all suggestions on map</label><small id="propmsg"></small></div>
<div id="proplist"></div>
<div id="propbig" hidden><img id="propbigimg" alt="Evidence photo"><button id="propbigx" type="button">Close photo</button></div>
<div class="legend">An automatic tidy pass suggests moving places and adding or moving objects. Point at or click a suggestion to see it on the map in purple: an arrow from where the place is now to where it would go, its new heading and ◆ thing, or the object's new outline.</div></section>
<section><h2>Places <span id="plnote"></span></h2><div id="places"></div>
<form id="plform"><input id="plid" type="text" placeholder="name, e.g. Sofa 2" maxlength="60" required><input id="pldesc" type="text" placeholder="what is here"><button>Save this spot</button></form>
<div class="legend">Saves where the dog stands now, and guesses where the thing is: the first wall or furniture straight ahead of the camera. To mark a place later, click the thing on the map instead. Click a place here to show its camera cone. Agents read this list.</div></section>
<section><h2>Orientation (IMU)</h2><canvas id="rpyplot" class="fill" width="600" height="180"></canvas>
<div class="legend"><b class="lx">roll</b><b class="ly">pitch</b><b class="lz">yaw</b> · last 20 s, degrees</div>
<dl class="kv" id="imu" style="margin-top:10px"></dl></section>
<section><h2>Odometry</h2><dl class="kv" id="odom"></dl></section>
<section><h2>Body state</h2><dl class="kv" id="state"></dl></section>
<section><h2>Foot contact force</h2><div class="feet" id="feet"></div></section>
<section><h2>Joint angles (rad)</h2><table id="joints"></table></section>
</main>
<div id="deployov" role="alertdialog" aria-live="assertive" hidden><div><b>Deploying a new console version, driving is paused.</b>
<span id="deploytxt">This page reloads by itself.</span><small id="deploymsg"></small>
<button type="button" id="deploystop" title="The console already stopped the dog; this sends STOP again">STOP the dog</button></div></div>
<script>
const $=id=>document.getElementById(id);
const deg=v=>(v*180/Math.PI).toFixed(1);
const f=(v,n=2)=>(v>=0?' ':'')+Number(v).toFixed(n);
const kv=(el,rows)=>{el.innerHTML=rows.map(([k,v])=>`<dt>${k}</dt><dd>${v}</dd>`).join('')};
const hist=[];const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();

function plotRPY(){const c=$('rpyplot');if(FREE){const r=c.getBoundingClientRect();if(r.width>50&&r.height>50&&(Math.abs(c.width-r.width)>2||Math.abs(c.height-r.height)>2)){c.width=Math.round(r.width);c.height=Math.round(r.height)}}
 else if(c.width!==600||c.height!==180){c.width=600;c.height=180}
 const g=c.getContext('2d'),W=c.width,H=c.height;g.clearRect(0,0,W,H);
 const now=performance.now()/1000;g.strokeStyle=css('--line');g.lineWidth=1;
 [-30,0,30].forEach(d=>{const y=H/2-d/45*(H/2);g.beginPath();g.moveTo(0,y);g.lineTo(W,y);g.stroke();
  g.fillStyle=css('--dim');g.font='11px monospace';g.fillText(d+'°',4,y-3)});
 ['--x','--y','--z'].forEach((col,i)=>{g.strokeStyle=css(col);g.lineWidth=1.6;g.beginPath();
  hist.forEach((h,j)=>{const x=W-(now-h.t)/20*W,y=H/2-Math.max(-45,Math.min(45,h.v[i]*180/Math.PI))/45*(H/2);
   j?g.lineTo(x,y):g.moveTo(x,y)});g.stroke()})}

// draw canvases at their on-screen size (sharp at any panel size); returns the size in CSS px
// (square, but never taller than most of the window)
function fit(c){const dpr=window.devicePixelRatio||1,rc=c.getBoundingClientRect(),w=Math.max(100,Math.round(rc.width||600)),
 fill=FREE&&c.classList.contains('fill'),   // free layout: the panel decides the size; the canvas fills it
 h=fill?Math.max(80,Math.round(rc.height)):Math.min(w,Math.max(300,Math.round(innerHeight*0.85))),nw=Math.round(w*dpr),nh=Math.round(h*dpr);
 if(fill&&c.style.height)c.style.height='';
 if(c.width!==nw||c.height!==nh){c.width=nw;c.height=nh;if(!fill)c.style.height=h+'px'}c.getContext('2d').setTransform(dpr,0,0,dpr,0,0);return [w,h]}
function plotCloud(cl,od){const c=$('cloud'),W=Math.min(...fit(c)),g=c.getContext('2d'),R=8,s=W/(2*R);g.clearRect(0,0,c.width,c.height);
 g.strokeStyle=css('--line');g.lineWidth=1;for(let m=-R;m<=R;m+=2){const p=W/2+m*s;
  g.beginPath();g.moveTo(p,0);g.lineTo(p,W);g.moveTo(0,p);g.lineTo(W,p);g.stroke()}
 const local=cl&&cl.frame==='base_link';const cx=(!local&&od)?od.pos[0]:0,cy=(!local&&od)?od.pos[1]:0;
 if(cl){const c2=cl.cell*s;g.fillStyle=css('--line');
  for(const [x,y] of cl.flat)g.fillRect(W/2+(x-cx)*s-c2/2,W/2-(y-cy)*s-c2/2,c2,c2);
  for(const [x,y,h] of cl.obs){const t=Math.min(1,h/1.2);g.fillStyle=`hsl(${45-t*40} 90% ${62-t*10}%)`;
   g.fillRect(W/2+(x-cx)*s-c2/2,W/2-(y-cy)*s-c2/2,c2,c2)}}
 const yaw=local?0:(od?od.yaw:0);g.save();g.translate(W/2,W/2);g.rotate(-yaw);g.fillStyle=css('--fg');
 g.beginPath();g.moveTo(14,0);g.lineTo(-9,7);g.lineTo(-5,0);g.lineTo(-9,-7);g.closePath();g.fill();g.restore()}

const mapImg=new Image();let mapT=null;let PLACES={};let VIEW={z:1,u:null,v:null,follow:false,label:12},PAN=null;
try{Object.assign(VIEW,JSON.parse(localStorage.getItem('go2view')||'{}'),{u:null,v:null})}catch(e){}
const saveView=()=>{try{localStorage.setItem('go2view',JSON.stringify({z:VIEW.z,follow:VIEW.follow,label:VIEW.label,rot:VIEW.rot}))}catch(e){}};
// view rotation: 'room' turns the drawing by the room's wall angle (map frame, deg, from the snapshot's map.room_deg) so walls are square on screen
let ROOM_DEG=-44;
let mapXf=null,PLACING=false,PDOWN=null,DROP=null,COVER=[],NAV=null,LIVE=null,SELPLACE=null;
let EDIT={on:false,drag:null,cross:null,handles:[],msg:'',msgT:0};   // Edit places mode; drag = the handle being dragged, with a live preview copy
// semantic map: height layers (mid = desk tops, high = shelves, ceiling) and labelled objects, each toggled in the zoom row
const LAY={on:{},img:{},t:{},last:{}};try{Object.assign(LAY.on,JSON.parse(localStorage.getItem('go2layers')||'{}'))}catch(e){}
const LAYTINT={mid:[230,140,40],high:[160,90,220]};let OBJS=[],SELOBJ=null;
const OBJLABELS=['desk','table','chair','sofa','cabinet','shelf','door','box','bin','plant','monitor','bed','counter','fridge'];
const MARKCOL='#d81b8c';   // saved markers (objects with an aruco_id): a magenta arrow; live detections stay orange squares
// a saved marker's arrow: from its spot, the way its printed face looks out; longer in Edit places so the tip circle is easy to grab
const markLen=LS=>EDIT.on?30:16*Math.sqrt(LS),markName=o=>o.name||`#${o.aruco_id}`;
const OBJPAL=['#e0a84a','#5b9be0','#7cc46d','#d46ad4','#e06a5a','#4fb3a9','#c9b458','#9a8cf0','#e08a5a','#6ac4d4'];
const objCol=l=>{let i=OBJLABELS.indexOf(l);if(i<0){i=0;for(const ch of String(l))i=(i*31+ch.charCodeAt(0))>>>0}return OBJPAL[i%OBJPAL.length]};
// fetch a layer when its toggle is on and the map changed, at most every 5 s; keep only the useful cells, tinted
function loadLayer(n,m){if(LAY.t[n]===m.t||Date.now()-(LAY.last[n]||0)<5000)return;LAY.t[n]=m.t;LAY.last[n]=Date.now();
 const im=new Image();im.onload=()=>{const c=document.createElement('canvas');c.width=im.naturalWidth;c.height=im.naturalHeight;const g=c.getContext('2d');g.drawImage(im,0,0);
  const d=g.getImageData(0,0,c.width,c.height),a=d.data,tint=LAYTINT[n];
  for(let i=0;i<a.length;i+=4){const v=a[i];if(tint){if(v<100){a[i]=tint[0];a[i+1]=tint[1];a[i+2]=tint[2];a[i+3]=255}else a[i+3]=0}
   else if(Math.abs(v-205)<2)a[i+3]=0}
  g.putImageData(d,0,0);LAY.img[n]=c;plotMap(lastMap,lastPose)};
 im.onerror=()=>{LAY.img[n]=null};im.src=(LAYSRC[n]||`/map/layer.png?layer=${n}&t=${m.t}`)}
const LAYSRC={};   // test hook: override a layer's URL
async function loadObjects(){try{const j=await (await fetch('/map/objects')).json();OBJS=j.objects||[]}catch(e){return}
 if(SELOBJ){SELOBJ=OBJS.find(o=>o.id===SELOBJ.id)||null;if(SELOBJ)showObj(SELOBJ,1);else $('objp').hidden=true}plotMap(lastMap,lastPose)}
// the object whose (rotated) rectangle holds map point x, y; small ones get a 0.15 m margin
function objAt(x,y){for(let i=OBJS.length-1;i>=0;i--){const o=OBJS[i],dx=x-o.x,dy=y-o.y,c=Math.cos(o.yaw||0),sn=Math.sin(o.yaw||0);
 if(Math.abs(dx*c+dy*sn)<=Math.max(o.w/2,0.15)&&Math.abs(-dx*sn+dy*c)<=Math.max(o.h/2,0.15))return o}return null}
function plotMap(m,p){const c=$('map'),[W,H]=fit(c),g=c.getContext('2d');g.clearRect(0,0,W,H);
 if(!m){$('mapinfo').textContent='no map';$('mapstatus').textContent='No map yet. Press Start mapping, then drive slowly around the lab.';
  $('mapstate').textContent='off · no map yet';document.querySelectorAll('[data-map]').forEach(b=>{const w=b.dataset.when;b.hidden=w==='mapping'||b.dataset.map==='extend'||b.dataset.map==='align'});return}
 $('mapstatus').textContent=PLACING?PLACE_HINT:EDIT.msg&&Date.now()-EDIT.msgT<8000?EDIT.msg:m.status+(m.mode==='mapping'?' · drive slowly to fill it in':'')+(LIVE&&LIVE.shift&&LIVE.shift.suspect?' · ⚠ '+(LIVE.shift.text||'live view looks shifted against the map'):'');
 const mapping=m.mode==='mapping';
 $('mapstate').textContent=mapping?`on · ${m.mapped_m2} m² seen`:m.mode==='localized'?'off · lined up with the saved map':'off · '+m.status;$('mapstate').className='mapstate'+(mapping?' on':'');
 document.querySelectorAll('[data-map]').forEach(b=>{const w=b.dataset.when;b.hidden=w==='any'?false:(w==='mapping')!==mapping});
 $('placedog').hidden=mapping;if(mapping&&PLACING)setPlacing(false);
 if(m.t!==mapT){mapT=m.t;mapImg.src='/map.png?t='+m.t}
 if(!mapImg.complete||!mapImg.naturalWidth)return;
 // zoom and pan: VIEW.u, v = map image pixel at the canvas centre
 if(VIEW.u==null||VIEW.mw!==m.width||VIEW.mh!==m.height){VIEW.u=m.width/2;VIEW.v=m.height/2;VIEW.mw=m.width;VIEW.mh=m.height}
 if(VIEW.follow&&p){VIEW.u=(p.x-m.origin[0])/m.resolution;VIEW.v=m.height-(p.y-m.origin[1])/m.resolution}
 // never lose the map: bad saved values reset, and the centre can't be panned off the map
 if(!isFinite(VIEW.z)||VIEW.z<1)VIEW.z=1;if(!isFinite(VIEW.u)||!isFinite(VIEW.v)){VIEW.u=m.width/2;VIEW.v=m.height/2}
 VIEW.u=Math.min(m.width,Math.max(0,VIEW.u));VIEW.v=Math.min(m.height,Math.max(0,VIEW.v));
 if(m.room_deg!=null&&isFinite(m.room_deg))ROOM_DEG=m.room_deg;
 // one transform, map image pixel -> canvas px: centre on (VIEW.u, VIEW.v), scale, rotate; its inverse turns clicks back into the map
 const RD=VIEW.rot==='room'?ROOM_DEG:0,RR=RD*Math.PI/180,rc=Math.abs(Math.cos(RR)),rs=Math.abs(Math.sin(RR));
 const s=Math.min(W/(m.width*rc+m.height*rs),H/(m.width*rs+m.height*rc))*VIEW.z;
 const M=new DOMMatrix().translate(W/2,H/2).rotate(RD).scale(s).translate(-VIEW.u,-VIEW.v);
 $('zinfo').textContent=VIEW.z>1.01?`${VIEW.z.toFixed(1)}×`:'';
 g.save();g.transform(M.a,M.b,M.c,M.d,M.e,M.f);g.imageSmoothingEnabled=false;g.drawImage(mapImg,0,0,m.width,m.height);
 for(const n of ['ceiling','mid','high']){if(!LAY.on[n])continue;loadLayer(n,m);if(LAY.img[n]){g.globalAlpha=n==='ceiling'?.5:.75;g.drawImage(LAY.img[n],0,0,m.width,m.height);g.globalAlpha=1}}
 g.restore();
 $('mapinfo').textContent=`${(m.width*m.resolution).toFixed(0)}×${(m.height*m.resolution).toFixed(0)} m · ${m.mapped_m2} m² seen`;
 mapXf={s,M,inv:M.inverse(),RR,m};
 const mp=(x,y)=>{const u=(x-m.origin[0])/m.resolution,v=m.height-(y-m.origin[1])/m.resolution;return [M.a*u+M.c*v+M.e,M.b*u+M.d*v+M.f]};
 const ppm=s/m.resolution;   // canvas px per metre
 // place names with a dark outline so they read on white floor and black walls
 const label=(t,x,y,col)=>{g.save();g.lineWidth=3;g.strokeStyle='rgba(15,18,20,.85)';g.lineJoin='round';g.strokeText(t,x,y);g.fillStyle=col||css('--accent');g.fillText(t,x,y);g.restore()};
 const arrow=(x,y,yaw,col,sz=1)=>{g.save();g.translate(x,y);g.rotate(RR-yaw);g.scale(sz,sz);g.fillStyle=col;g.beginPath();g.moveTo(11,0);g.lineTo(-7,6);g.lineTo(-3,0);g.lineTo(-7,-6);g.closePath();g.fill();g.restore()};
 // camera view cone: what the front camera sees (about 40 degrees each side)
 const cone=(x,y,yaw,len,col)=>{g.save();g.fillStyle=col;g.globalAlpha=.18;g.beginPath();g.moveTo(x,y);g.arc(x,y,len,RR-yaw-0.7,RR-yaw+0.7);g.closePath();g.fill();
  g.globalAlpha=.6;g.strokeStyle=col;g.lineWidth=1;g.stroke();g.restore()};
 if(NAV&&NAV.path&&NAV.path.length>1){g.save();g.strokeStyle=css('--z');g.lineWidth=2.5;g.setLineDash([6,4]);g.beginPath();
  NAV.path.forEach(([x,y],i)=>{const [cx,cy]=mp(x,y);i?g.lineTo(cx,cy):g.moveTo(cx,cy)});g.stroke();g.restore();
  const [ex,ey]=mp(...NAV.path[NAV.path.length-1]);g.strokeStyle=css('--z');g.lineWidth=2;g.beginPath();g.arc(ex,ey,6,0,7);g.stroke()}
 if(LIVE){const q=Math.max(2,0.1/m.resolution*s);g.save();g.globalAlpha=.55;
  g.fillStyle='#2fa84f';LIVE.cleared.forEach(([x,y])=>{const [cx,cy]=mp(x,y);g.fillRect(cx-q/2,cy-q/2,q,q)});
  g.fillStyle='#e0362c';LIVE.new.forEach(([x,y])=>{const [cx,cy]=mp(x,y);g.fillRect(cx-q/2,cy-q/2,q,q)});g.restore()}
 if(LBLDOTS){const [sx,sy]=mp(...LBLDOTS.spot);g.save();g.lineWidth=1.5;g.strokeStyle='rgba(15,18,20,.85)';
  for(const q of LBLDOTS.pts){const [px,py]=mp(q.x,q.y);g.fillStyle=SECTCOL[q.k];g.beginPath();g.arc(px,py,4,0,7);g.fill();g.stroke()}
  g.strokeStyle=css('--accent');g.lineWidth=2;g.beginPath();g.arc(sx,sy,7,0,7);g.stroke();g.restore()}
 if(DROP){g.fillStyle=css('--z');g.globalAlpha=.35;for(const [x,y] of COVER){const [cx,cy]=mp(x,y);g.fillRect(cx-1.5,cy-1.5,3,3)}g.globalAlpha=1;
  const [dx,dy]=mp(DROP.x,DROP.y);
  const v=DROP.view;if(v){const [vx,vy]=mp(v.x,v.y);cone(vx,vy,v.yaw_deg*Math.PI/180,Math.max(Math.hypot(dx-vx,dy-vy)+0.5*ppm,1.5*ppm),css('--warn'));
   g.strokeStyle=css('--warn');g.setLineDash([4,3]);g.beginPath();g.moveTo(vx,vy);g.lineTo(dx,dy);g.stroke();g.setLineDash([]);arrow(vx,vy,v.yaw_deg*Math.PI/180,css('--warn'))}
  g.strokeStyle=css('--warn');g.lineWidth=2;g.beginPath();g.arc(dx,dy,8,0,7);g.moveTo(dx-12,dy);g.lineTo(dx+12,dy);g.moveTo(dx,dy-12);g.lineTo(dx,dy+12);g.stroke()}
 const LS=VIEW.label/11;g.font=`${VIEW.label}px monospace`;
 if(LAY.on.objects)for(const o0 of OBJS){const o=objDrag(o0.id)?{...o0,...EDIT.drag.cur}:o0,col=objCol(o.label),c=Math.cos(o.yaw||0),sn=Math.sin(o.yaw||0),hw=o.w/2,hh=o.h/2;
  // a marker (object with an aruco_id): one small arrow from its spot, pointing out of its printed face, and its name; selected = thicker
  if(o.aruco_id!=null){const sel=SELOBJ&&o.id===SELOBJ.id,[kx,ky]=mp(o.x,o.y),L=markLen(LS),hd=(sel?7:5)*Math.sqrt(LS),a=RR-(o.yaw||0),ca=Math.cos(a),sa=Math.sin(a);
   g.save();g.translate(kx,ky);g.rotate(a);g.lineCap='round';g.lineJoin='round';
   const shape=()=>{g.beginPath();g.moveTo(0,0);g.lineTo(L-hd*.6,0);g.stroke();g.beginPath();g.moveTo(L,0);g.lineTo(L-hd,hd*.6);g.lineTo(L-hd,-hd*.6);g.closePath();g.fill();g.stroke()};
   g.strokeStyle=g.fillStyle='rgba(15,18,20,.6)';g.lineWidth=sel?6:4.5;shape();   // thin dark edge so it reads on white floor
   g.strokeStyle=g.fillStyle=MARKCOL;g.lineWidth=sel?3.5:2;shape();
   g.beginPath();g.arc(0,0,(sel?3:2.2)*Math.sqrt(LS),0,7);g.fill();g.restore();
   // name on the side away from the arrow, so the two never overlap
   g.save();g.font=`${Math.round(VIEW.label*.85)}px monospace`;const t=markName(o),tw=g.measureText(t).width,r=9*Math.sqrt(LS)+tw/2;
   label(t,kx-ca*r-tw/2,ky-sa*r+VIEW.label*.3,MARKCOL);g.restore();continue}
  // light by default: thin outline only; the selected object gets a faint fill and a thicker line
  const sel=SELOBJ&&o.id===SELOBJ.id;g.save();g.strokeStyle=col;g.lineWidth=sel?3:1.25;g.globalAlpha=sel?1:.7;if(!o.confirmed_by)g.setLineDash([4,4]);g.beginPath();
  [[hw,hh],[-hw,hh],[-hw,-hh],[hw,-hh]].forEach(([u,v],i)=>{const [px,py]=mp(o.x+u*c-v*sn,o.y+u*sn+v*c);i?g.lineTo(px,py):g.moveTo(px,py)});
  g.closePath();if(sel){g.globalAlpha=.12;g.fillStyle=col;g.fill();g.globalAlpha=1}g.stroke();g.restore();
  // names only for named or confirmed objects big enough on screen (zoom in to see more), or the selected one
  if(sel||((o.name||o.confirmed_by)&&Math.max(o.w,o.h)*ppm>=40)){const t=o.name||o.label,[lx,ly]=mp(o.x,o.y);
   g.save();g.font=`${Math.round(VIEW.label*.85)}px monospace`;label(t,lx-g.measureText(t).width/2,ly+4*LS,col);g.restore()}}
 for(const q0 of Object.values(PLACES)){const q=editCur(q0),[sx,sy]=mp(q.x,q.y),t=q.target;
  if(t){const [tx,ty]=mp(t.x,t.y);g.strokeStyle=css('--accent');g.globalAlpha=.5;g.lineWidth=1;g.beginPath();g.moveTo(sx,sy);g.lineTo(tx,ty);g.stroke();g.globalAlpha=1;
   if(q.id===SELPLACE)cone(sx,sy,q.yaw_deg*Math.PI/180,Math.hypot(tx-sx,ty-sy)+0.5*ppm,css('--accent'));
   arrow(sx,sy,q.yaw_deg*Math.PI/180,css('--accent'),.6);g.fillStyle=css('--accent');g.beginPath();g.arc(tx,ty,4.5*Math.sqrt(LS),0,7);g.fill();label(q.id,tx+6*LS,ty-4*LS)}
  else{if(q.id===SELPLACE)cone(sx,sy,q.yaw_deg*Math.PI/180,1.5*ppm,css('--accent'));g.fillStyle=css('--accent');g.beginPath();g.arc(sx,sy,4*Math.sqrt(LS),0,7);g.fill();label(q.id,sx+6*LS,sy-4*LS)}}
 if(EDIT.on)editDraw(g,mp,RR);
 propDraw(g,mp,RR);
 // ArUco markers in view: camera 0.33 m ahead of the pose point, then the marker's range along heading minus bearing (+ = right)
 if(p&&MARKERS.length){const q=5*Math.sqrt(LS),cx=p.x+0.33*Math.cos(p.yaw),cy=p.y+0.33*Math.sin(p.yaw);g.save();
  for(const k of MARKERS){const r=Math.hypot(k.z,k.x),a=p.yaw-k.bearing_deg*Math.PI/180,[kx,ky]=mp(cx+r*Math.cos(a),cy+r*Math.sin(a));
   g.fillStyle=css('--warn');g.strokeStyle='rgba(15,18,20,.85)';g.lineWidth=1.5;g.fillRect(kx-q,ky-q,2*q,2*q);g.strokeRect(kx-q,ky-q,2*q,2*q);
   label(String(k.mark),kx+q+3*LS,ky-q,css('--warn'))}g.restore()}
 if(p){const [px,py]=mp(p.x,p.y);
  g.save();g.translate(px,py);g.rotate(RR-p.yaw);g.fillStyle=css('--bad');
  g.beginPath();g.moveTo(12,0);g.lineTo(-8,6);g.lineTo(-4,0);g.lineTo(-8,-6);g.closePath();g.fill();g.restore()}}
mapImg.onload=()=>plotMap(lastMap,lastPose);let lastMap=null,lastPose=null,lastCloud=null,MARKERS=[];
// patrol chip (header): the open patrol, its time left and why it stopped (go2_patrol.Patrols.brief)
function patrolChip(p){if(!p)return '';const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 const ended=p.state==='ended',why=ended?p.stop_reason:p.halt||(p.state==='grace'?'lease lapsed, grace':'');
 return `<span class="chip ${ended?'dead':p.halt||p.state==='grace'?'stale':'ok'}" title="patrol by ${esc(p.client)}">patrol ${esc(p.patrol_id)} · ${ended?'ended':Math.round(p.time_left_s/60*10)/10+' min left'}${why?' · '+esc(why):''}</span>`}
// battery chip (header) and low-battery notice (control bar); battery is null until the driver reports it
function battChip(b){if(!b||b.soc==null)return '<span class="chip dead" title="no battery reading yet">battery —</span>';
 const soc=Math.round(b.soc),cls=b.stale?'stale':soc>50?'bhi':soc>=20?'stale':'dead',chg=b.current_ma>0;
 const tip=[b.voltage!=null&&`${(+b.voltage).toFixed(2)} V`,b.current_ma!=null&&`${(b.current_ma/1000).toFixed(2)} A ${b.current_ma>0?'(charging?)':'(discharging)'}`,
  Array.isArray(b.bms_temp_c)&&`BMS ${b.bms_temp_c.map(t=>Math.round(t)+'°C').join(' / ')}`,b.cycles!=null&&`${b.cycles} cycles`,b.age_s!=null&&`${(+b.age_s).toFixed(0)} s old`].filter(Boolean).join(' · ');
 return `<span class="chip ${cls}" title="${esc(tip)}">🔋 ${soc}%${chg?' ⚡':''}${b.stale?' stale':''}</span>`}
let BATTSTEP=null;   // the 10% step we last warned at (or the user dismissed); warn again only below a lower step
function battWarn(b){const el=$('battwarn');if(!b||b.soc==null||b.stale){el.hidden=true;return}const soc=Math.round(b.soc);
 if(soc>=20){BATTSTEP=null;el.hidden=true;return}const step=Math.floor(soc/10);
 if(BATTSTEP===null||step<BATTSTEP){BATTSTEP=step;el.hidden=false}
 $('battwarntxt').textContent=`Battery low: ${soc}% — dock or charge soon`}
$('battwarnx').addEventListener('click',()=>{$('battwarn').hidden=true});
const FEET=['FR','FL','RR','RL'];const SENS=['imu','odom','state','joints','cloud','camera'];
function render(d){const a=d.age||{};
 if(deployCheck(d))return;
 if(window.__DRAG){PENDING=d;return}
 if(!CHAT.busy){const o=(d.agents||{}).owner;$('chatst').textContent=o&&o.kind==='human'?'agents locked out: press Hand back to agents so it can move':''}     // a panel is being dragged: no DOM/canvas updates until it is dropped
 renderDog(d,a);
 if(d.l515)renderL515(d.l515);
 if(d.rec)renderRec(d.rec);if(d.agents)renderAgents(d.agents);
 if(d.control){ctl=d.control;$('avoid').checked=ctl.avoid;if(ctl.speed)showSpeed(ctl.speed,ctl.speeds);
  const lk=ctl.look_deg||0,bp=d.imu?Math.round(d.imu.rpy[1]*180/Math.PI):null;
  $('lookstate').textContent=(lk?`${Math.abs(lk)}° ${lk>0?'up':'down'}`:'level')+(bp!=null?` · body pitch ${bp>0?'+':''}${bp}°`:'');
  const other=ctl.driver&&ctl.driver!==CLIENT;if(allowed)$('dnote').textContent=other?`driving: ${ctl.driver_ip}`:(ctl.driver?'you are driving':'');}
 $('chips').innerHTML=SENS.map(k=>{const t=a[k];const cls=t==null?'dead':t<1.5?'ok':t<5?'stale':'dead';
  return `<span class="chip ${cls}">${k} ${t==null?'—':t<1.5?'live':t.toFixed(0)+'s'}</span>`}).join('')+battChip(d.battery)+patrolChip(d.patrol);
 battWarn(d.battery);
 if(d.imu){const i=d.imu;hist.push({t:performance.now()/1000,v:i.rpy});while(hist.length&&performance.now()/1000-hist[0].t>20)hist.shift();
  kv($('imu'),[['roll / pitch / yaw (°)',`${deg(i.rpy[0])} / ${deg(i.rpy[1])} / ${deg(i.rpy[2])}`],
   ['gyro (rad/s)',i.gyro.map(v=>f(v)).join(' ')],['accel (m/s²)',i.acc.map(v=>f(v)).join(' ')],['IMU temp (°C)',i.temp]])}
 plotRPY();
 if(d.odom){const o=d.odom;kv($('odom'),[['frame',o.frame],['x / y / z (m)',o.pos.map(v=>f(v)).join(' ')],
  ['heading (°)',deg(o.yaw)],['vx / vy (m/s)',f(o.vel[0])+' '+f(o.vel[1])],['turn rate (rad/s)',f(o.vel[2])]])}
 if(d.state){const s=d.state;kv($('state'),[['mode',s.mode],['gait type',s.gait],['body height (m)',f(s.body_height,3)],
  ['foot raise (m)',f(s.foot_raise,3)],['velocity (m/s)',s.velocity.map(v=>f(v)).join(' ')],
  ['obstacle range F/B/L/R (m)',s.obstacle.map(v=>f(v,1)).join(' ')]]);
  const mx=Math.max(100,...s.foot_force);$('feet').innerHTML=s.foot_force.map((v,k)=>
   `<div class="foot">${FEET[k]} <span style="float:right">${v}</span><div class="bar"><i style="width:${v/mx*100}%"></i></div></div>`).join('')}
 if(d.joints){const j=d.joints,legs={};j.name.forEach((n,k)=>{const [leg,part]=n.split('_');(legs[leg]??={})[part]=j.pos[k]});
  $('joints').innerHTML='<tr><th>leg</th><th>hip</th><th>thigh</th><th>calf</th></tr>'+Object.entries(legs).map(([l,p])=>
   `<tr><td>${l}</td><td>${f(p.hip)}</td><td>${f(p.thigh)}</td><td>${f(p.calf)}</td></tr>`).join('')}
 if(d.cloud)$('cloudinfo').textContent=`${d.cloud.obs.length} obstacle cells · ${d.cloud.n_total} pts`;
 if(d.markers){MARKERS=d.markers.list||[];$('mknote').innerHTML=MARKERS.length?MARKERS.map(k=>{const b=Math.round(k.bearing_deg);
  return `tag <b>${String(k.mark).replace(/[<&]/g,'')}</b>: ${k.z.toFixed(2)} m, ${b?Math.abs(b)+'° '+(b>0?'right':'left'):'straight ahead'}`}).join(' · '):'no tags in view'}
 plotCloud(d.cloud,d.odom);lastCloud=[d.cloud,d.odom];lastMap=d.map;lastPose=d.map_pose;NAV=d.nav;LIVE=d.live;plotMap(d.map,d.map_pose);$('camage').textContent=a.camera!=null?`${a.camera.toFixed(1)} s old`:'no frames'}

// The camera <img> stream does not reconnect by itself when the console restarts; restart it whenever the event stream (re)connects.
async function camLoop(){let after=0;const cam=$('cam');
 for(;;){if(document.hidden||window.__DRAG){await new Promise(f=>setTimeout(f,1000));continue}
  try{const r=await fetch('/camera.jpg?after='+after,{cache:'no-store'});
   if(r.status===200&&window.__DRAG){await r.blob();continue}   // a frame that arrives mid-drag is dropped (next one is newer)
   if(r.status===200){after=+r.headers.get('X-Frame-T')||0;const u=URL.createObjectURL(await r.blob()),old=cam.src;
     cam.src=u;if(old.startsWith('blob:'))URL.revokeObjectURL(old)}
   else if(r.status!==204)throw new Error(r.status)}
  catch(e){after=0;await new Promise(f=>setTimeout(f,1000))}}}
camLoop();
// L515 depth camera: the bridge page (colour, depth, 3-D cloud) in an iframe, proxied by the console at /l515/
// (one port). Loaded only while the L515 is online and this tab is visible, so it never holds connections otherwise.
let L515ON=false;
function l515Frame(){const f=$('l515f'),want=L515ON&&!document.hidden;
 if(want&&f.hidden){f.src='/l515/';f.hidden=false;$('l515off').hidden=true}
 else if(!want&&!f.hidden){f.hidden=true;f.src='about:blank';$('l515off').hidden=false}}
function renderL515(l){L515ON=!!l.online;
 $('l515st').textContent=l.online?`${l.fps!=null?l.fps.toFixed(1):'?'} fps · frame ${l.age_s!=null?l.age_s.toFixed(1):'?'} s old${l.depth?' · depth '+l.depth:''}`
  :l.bridge?'L515 offline (bridge running, no frames from the Pi)':'L515 offline';
 if(!l.online)$('l515off').textContent=l.bridge?'L515 offline: no frames from the Pi':'L515 offline: start the Pi sender, then scripts/run_pc.sh in l515_go2_pi4_bridge';
 l515Frame()}
// outside the free layout the iframe takes its content's height (same origin through the proxy)
$('l515f').addEventListener('load',()=>{try{const d=$('l515f').contentDocument;if(!d||!d.body)return;
 new ResizeObserver(()=>{if(!FREE)$('l515f').style.height=d.documentElement.scrollHeight+'px'}).observe(d.body)}catch(e){}});
// Dog on/off/idle, computed here from the ages the page already gets: off when odom is over 10 s old, idle after
// 30 s with no motion, posture change or command (the server's idle clock), else active.
const dur=s=>s==null?'?':s<90?Math.round(s)+' s':s<5400?Math.round(s/60)+' min':(s/3600).toFixed(1)+' h';
function renderDog(d,a){const ds=d.dog_status||{},odom=a.odom,idle=ds.idle_s!=null?ds.idle_s:(d.rec&&d.rec.auto_info||{}).idle_s;
 const st=odom==null||odom>10?'off':idle==null||idle>=30?'idle':'active',b=$('dogstb');
 b.className=st;b.textContent=st==='off'?'DOG OFF':st==='idle'?'IDLE':'ACTIVE';
 $('dogstt').textContent=st==='off'?(odom==null?'no data':`no data for ${dur(odom)}`):st==='idle'?`idle ${dur(idle)}`:'';
 const l=d.l515||{},w=d.watchdog,wfresh=w&&Date.now()/1000-w.received_t<60;
 $('l515stc').textContent='L515 '+(wfresh&&w.l515_asleep?'asleep':l.online?'online':'offline');
 $('wdst').textContent=wfresh&&w.last_action?'watchdog: '+w.last_action:'';
 renderMotors(d.motors,a.motors)}
// Motors: header chip (tap for per-leg max) and a banner when hot. Lie down only on a person's click, never by itself.
const MOTWARN=60,MOTHOT=70;let MOTLEGS=false;
const mname=n=>n?n.replace('_',' '):'?';
function renderMotors(m,age){const c=$('motst'),b=$('motwarn');
 if(!m||m.max==null){c.hidden=true;b.hidden=true;return}
 const stale=m.stale||age==null||age>10,wc=m.warn_c||MOTWARN,hc=m.hot_c||MOTHOT,lvl=stale?'stale':m.max>=hc?'hot':m.max>=wc?'warm':'';
 c.hidden=false;c.className='motchip '+lvl;
 const legs=['FL','FR','RL','RR'].map(l=>`${l} ${m.legs&&m.legs[l]!=null?m.legs[l]:'?'}°`).join(' · ');
 c.textContent=stale?'Motors: no data':MOTLEGS?'Motors '+legs:`Motors ${m.max} °C`;c.title=`Hottest: ${mname(m.hottest)} ${m.max} °C · per leg: ${legs}`+(m.err&&m.err.length?` · lost packets: ${m.err.join(', ')}`:'')+(stale?' (no fresh data)':'');
 const show=!stale&&(lvl==='warm'||lvl==='hot');b.hidden=!show;b.className='motwarn'+(lvl==='hot'?' hot':'');
 if(show)$('motwarntxt').textContent=`Motors ${lvl==='hot'?'very hot':'hot'} (${mname(m.hottest)} ${m.max} °C): lie the dog down to let it cool`}
$('motst').addEventListener('click',()=>{MOTLEGS=!MOTLEGS});
$('motlie').addEventListener('click',()=>{post({action:'lie'});$('dstat').textContent='Lie down (motors hot)'});
// Deploys: the console sends boot_id (new per start) and deploying {t, msg}. While deploying: overlay, no driving.
// A new boot id, or getting data again after the console was down, reloads the page (new page code).
var PENDING=null;   // latest /events data held back during a panel drag
var DEPLOY=false,BOOT=null,lastMsg=Date.now(),wasDown=false;
function deployCheck(d){lastMsg=Date.now();
 if(d.boot_id){if(BOOT&&d.boot_id!==BOOT){location.reload();return true}BOOT=d.boot_id}
 if(wasDown){location.reload();return true}
 DEPLOY=!!d.deploying;$('deployov').hidden=!DEPLOY;
 if(DEPLOY){if(armed||held.size)setArmed(false);$('deploymsg').textContent=d.deploying.msg||''}
 return false}
setInterval(()=>{if(document.hidden)return;const down=Date.now()-lastMsg;
 if(down>5000){wasDown=true;fetch('/state.json',{cache:'no-store'}).then(r=>r.ok&&location.reload()).catch(()=>{})}
 if(DEPLOY){setArmed(false);$('deploytxt').textContent=down>60000?'The console has not come back after a minute. Reload this page by hand; if it still does not load, check the console on the control PC.':'This page reloads by itself.'}},3000);
$('deploystop').addEventListener('click',()=>post({action:'stop'}));
// "Ask the dog": chat with a Claude agent run by go2_agent_chat.py on the host (proxied at /agentchat/). The agent only
// has the robot tools; the console's agent rules apply (Take over / STOP win). Stop kills the run and stops the dog.
const CHAT={session:null,run:null,from:0,busy:false,tools:{}};
try{CHAT.session=localStorage.getItem('go2chat')||null;const m=localStorage.getItem('go2chatmodel');if(m)$('chatmodel').value=m}catch(e){}
const cesc=t=>String(t==null?'':t).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function chatAdd(cls,html){const d=document.createElement('div');d.className=cls;d.innerHTML=html;const L=$('chatlog');
 const stick=L.scrollHeight-L.scrollTop-L.clientHeight<60;L.appendChild(d);if(stick)L.scrollTop=L.scrollHeight;return d}
function chatBusy(b,txt){CHAT.busy=b;$('chatst').className=b?'busy':'';$('chatst').textContent=txt||(b?'working…':'');
 $('chatstop').disabled=!b;$('chatsend').disabled=b}
const argtxt=a=>Object.entries(a||{}).filter(([k,v])=>v!==''&&v!=null).map(([k,v])=>typeof v==='string'?v:k+'='+JSON.stringify(v)).join(' ');
function chatEvent(e){
 if(e.kind==='user')chatAdd('u',cesc(e.text));
 else if(e.kind==='text')chatAdd('a',cesc(e.text));
 else if(e.kind==='tool'){CHAT.tools[e.id]=chatAdd('tl',`› <b>${cesc(e.name)}</b> ${cesc(argtxt(e.args))} <span>…</span>`);chatBusy(true,e.name+'…')}
 else if(e.kind==='tool_result'){const el=CHAT.tools[e.id];if(el){const s=el.querySelector('span');s.className=e.ok?'ok':'no';
   s.textContent=e.ok?'done':'refused: '+e.summary.slice(0,140);s.title=e.summary}chatBusy(true,'thinking…')}
 else if(e.kind==='photo'){let row=$('chatlog').lastElementChild;if(!row||!row.classList.contains('ph'))row=chatAdd('ph','');
   const i=document.createElement('img');i.src=e.url;i.alt='Photo the agent took';i.loading='lazy';i.onclick=()=>open(e.url,'_blank');row.appendChild(i)}
 else if(e.kind==='result')chatAdd('meta',`${e.is_error?'error · ':''}${e.duration_s!=null?e.duration_s+' s':''}${e.turns?' · '+e.turns+' turns':''}${e.cost_usd!=null?' · $'+e.cost_usd.toFixed(3):''}`);
 else if(e.kind==='error')chatAdd('err',cesc(e.text));
 else if(e.kind==='stopped')chatAdd('err','stopped'+(e.killed?' (agent ended)':'')+'; STOP sent to the dog');
 else if(e.kind==='start')chatBusy(true,'thinking…')}
async function chatPoll(run){CHAT.run=run;CHAT.from=0;chatBusy(true);
 while(CHAT.run===run){try{const r=await fetch(`/agentchat/chat/stream?run=${run}&from=${CHAT.from}`,{cache:'no-store'});
   if(!r.ok)throw new Error(r.status);const j=await r.json();j.events.forEach(chatEvent);CHAT.from=j.next;if(j.done)break}
  catch(e){await new Promise(f=>setTimeout(f,1500))}}
 if(CHAT.run===run){CHAT.run=null;chatBusy(false)}}
async function chatSend(){const text=$('chatin').value.trim();if(!text||CHAT.busy)return;
 const model=$('chatmodel').value;try{localStorage.setItem('go2chatmodel',model)}catch(e){}
 chatBusy(true,'starting…');let r,j;
 try{r=await fetch('/agentchat/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session:CHAT.session,text,model})});j=await r.json()}
 catch(e){chatAdd('err','could not reach the console');chatBusy(false);return}
 if(!r.ok){chatAdd('err',cesc(j.error||('error '+r.status)));chatBusy(false);if(r.status===409&&j.run)chatPoll(j.run);return}
 $('chatin').value='';CHAT.session=j.session;try{localStorage.setItem('go2chat',j.session)}catch(e){}
 const h=$('chatlog').querySelector('.chathint');if(h)h.remove();chatPoll(j.run)}
$('chatform').addEventListener('submit',e=>{e.preventDefault();chatSend()});
$('chatin').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();chatSend()}});
$('chatstop').addEventListener('click',async()=>{const run=CHAT.run;chatBusy(true,'stopping…');
 // the runner kills the agent and sends STOP to the console (agents may still drive after: the next chat works);
 // if the runner can't be reached, the page's own STOP halts the dog (and locks agents out until Hand back)
 let ok=false;try{ok=(await fetch('/agentchat/chat/stop',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({run})})).ok}catch(e){}
 if(!ok)post({action:'stop'});if(!CHAT.run)chatBusy(false)});
$('chatnew').addEventListener('click',()=>{if(CHAT.busy)return;CHAT.session=null;try{localStorage.removeItem('go2chat')}catch(e){}
 $('chatlog').innerHTML='<div class="chathint">New conversation.</div>'});
(async()=>{try{if(CHAT.session){const r=await fetch('/agentchat/chat/conv?session='+CHAT.session,{cache:'no-store'});
   if(r.ok){const j=await r.json();$('chatlog').innerHTML='';j.runs.forEach(x=>x.events.forEach(chatEvent));chatBusy(false)}else CHAT.session=null}
  const s=await(await fetch('/agentchat/chat/status',{cache:'no-store'})).json();
  if(s.busy&&s.run&&s.session===CHAT.session){$('chatlog').innerHTML='';const r=await fetch('/agentchat/chat/conv?session='+s.session);
   const j=await r.json();j.runs.filter(x=>x.run!==s.run).forEach(x=>x.events.forEach(chatEvent));chatPoll(s.run)}
  else if(s.busy)chatBusy(false,'agent busy with another conversation')}
 catch(e){$('chatst').textContent='agent runner offline'}})();

// Browsers allow 6 connections per host:port (HTTP/1.1). /events holds one for as long as the tab is open, so with
// six console tabs nothing else (camera, L515 frames) ever loaded: "waiting for L515 frames…" forever (2026-11-16).
// Background tabs now close their stream and pause their image loops; they catch up when shown again.
let ES=null;
function connect(){if(ES)return;const es=ES=new EventSource('/events');es.onopen=()=>{$('conn').textContent='streaming from '+location.host};
 es.onmessage=e=>render(JSON.parse(e.data));es.onerror=()=>{$('conn').textContent='disconnected, retrying…'}}
document.addEventListener('visibilitychange',()=>{
 if(document.hidden){if(ES){ES.close();ES=null}$('conn').textContent='paused while this tab is in the background'}
 else{lastMsg=Date.now();connect()}
 l515Frame()});
connect();

const GROUPS=['camera','lidar','l515','pose'];
try{const saved=JSON.parse(localStorage.getItem('recGroups')||'null');if(saved)GROUPS.forEach(g=>$('r_'+g).checked=saved.includes(g))}catch(e){}
GROUPS.forEach(g=>$('r_'+g).addEventListener('change',()=>{try{localStorage.setItem('recGroups',JSON.stringify(GROUPS.filter(x=>$('r_'+x).checked)))}catch(e){}}));
$('gear').addEventListener('click',()=>{const h=!$('settings').hidden;$('settings').hidden=h;$('gear').setAttribute('aria-expanded',String(!h))});
let recRunning=false;
$('recbtn').addEventListener('click',async()=>{const body=recRunning?{record:false}:{record:true,groups:GROUPS.filter(g=>$('r_'+g).checked)};
 $('recbtn').disabled=true;try{const r=await fetch('/cmd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if(!r.ok){const t=await r.text();const m=t.match(/<p>Message: (.*?)\./);$('recnote').innerHTML=`<span class="err">${m?m[1]:'Could not start ('+r.status+')'}</span>`}else $('recnote').textContent=''}
 finally{$('recbtn').disabled=false}});
const hms=s=>[Math.floor(s/3600),Math.floor(s/60)%60,s%60].map(v=>String(v).padStart(2,'0')).join(':');
const AUTOTXT={off:'Auto recording is off (GO2_AUTO_REC=0)',waiting_for_dog:'Auto recording starts when the dog connects',
 paused_until_reconnect:'Auto recording paused until the dog reconnects',disk_low:'Auto recording not started: disk below the free-space floor',
 manual_recording:'Auto recording waits for this manual recording',idle:'Auto recording stopped while the dog is idle; resumes when it moves'};
function renderRec(r){recRunning=r.running;$('recbtn').classList.toggle('on',r.running);$('recbtn').querySelector('span').textContent=r.running?'Stop recording':'Record';
 const a=r.auto_info||{};$('autorec').hidden=!r.auto;
 $('recinfo').innerHTML=r.running?`${r.auto?'<b class="err">auto recording</b> · ':''}<b>${hms(r.secs)}</b> · ${r.mb>1000?(r.mb/1000).toFixed(1)+' GB':r.mb+' MB'} · ${r.auto?'camera (JPEG), lidar, pose'+(L515ON?', L515':''):r.groups.join(', ')+' · started from '+r.by}`
  :(r.error?`<span class="err">${r.error}</span> · `:'')+(AUTOTXT[a.state]?AUTOTXT[a.state]+' · ':'')+(r.free_gb!=null?`${r.free_gb} GB free`:'');
 $('past').innerHTML=r.past.length?'Saved recordings:<br>'+r.past.map(p=>`${p.name} · ${p.mb>1000?(p.mb/1000).toFixed(1)+' GB':p.mb+' MB'}`).join('<br>'):''}

const DIR={w:[1,0,0],s:[-1,0,0],a:[0,1,0],d:[0,-1,0],q:[0,0,1],e:[0,0,-1]},SPEEDS={slow:[0.3,0.2,0.5],normal:[0.5,0.25,0.8],fast:[0.6,0.3,1.0]};let SPEED='slow',LIM=SPEEDS[SPEED];
const held=new Set();let armed=false,allowed=false,wasMoving=false;
const CLIENT=Math.random().toString(36).slice(2);let ctl={};
const post=b=>fetch('/cmd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...b,client:CLIENT,console:true})})
 .then(async r=>{if(r.status===409){held.clear();paint();$('dstat').textContent='Someone else is driving. Wait for them to stop.';return}
  if(!r.ok)throw new Error(r.status)}).catch(e=>{$('dstat').textContent='Command failed ('+e.message+'). Is the dashboard still running?'});
function setArmed(v){armed=v&&allowed&&!DEPLOY;$('armed').checked=armed;held.clear();paint();
 document.querySelectorAll('#pad button,.acts button').forEach(b=>b.disabled=!armed&&b.id!=='bstop');$('avoid').disabled=!armed;
 $('dstat').textContent=armed?'Armed: hold a direction':'Disarmed';$('dstat').className='dstat'+(armed?' live':'')}
function paint(){document.querySelectorAll('#pad [data-k]').forEach(b=>b.classList.toggle('on',held.has(b.dataset.k)))}
function stop(){held.clear();paint();wasMoving=false;if(allowed)post({action:'stop'})}
setInterval(()=>{if(!armed)return;
 if(held.size){const v=[0,0,0];held.forEach(k=>DIR[k].forEach((d,i)=>v[i]+=d));const m=v.map((d,i)=>Math.sign(d)*LIM[i]);
  post({move:m});wasMoving=true;$('dstat').textContent=`moving  x=${m[0].toFixed(1)} y=${m[1].toFixed(1)} turn=${m[2].toFixed(1)}`}
 else if(wasMoving){wasMoving=false;$('dstat').textContent='Armed: stopped'}},100);
addEventListener('keydown',e=>{
 // typing in a text box (chat, labels, place names) must never drive the dog: no WASD/QE, no space-STOP, no R/F
 if(e.target.closest&&e.target.closest('textarea,select,[contenteditable="true"],input:not([type=checkbox]):not([type=radio]):not([type=range]):not([type=button])'))return;
 if(e.target.tagName==='INPUT'&&e.key!==' ')return;const k=e.key.toLowerCase();
 if(k===' '){e.preventDefault();stop();return}if(armed&&DIR[k]){e.preventDefault();held.add(k);paint()}
 if(!e.repeat&&(k==='r'||k==='f')){e.preventDefault();look(k==='r'?6:-6)}});
addEventListener('keyup',e=>{const k=e.key.toLowerCase();if(held.delete(k))paint()});
addEventListener('blur',()=>{if(held.size)stop()});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&held.size)stop()});
document.querySelectorAll('#pad [data-k]').forEach(b=>{const k=b.dataset.k;
 b.addEventListener('pointerdown',e=>{if(!armed)return;b.setPointerCapture(e.pointerId);held.add(k);paint()});
 ['pointerup','pointercancel','lostpointercapture'].forEach(ev=>b.addEventListener(ev,()=>{if(held.delete(k))paint()}))});
$('bstop').addEventListener('click',stop);
// speed cap: one server-side setting for everyone (people and agents); the snapshot's control.speed is the truth
function showSpeed(n,sp){if(sp)Object.assign(SPEEDS,sp);if(!SPEEDS[n])return;SPEED=n;LIM=SPEEDS[n];
 document.querySelectorAll('#speeds [data-sp]').forEach(b=>b.classList.toggle('on',b.dataset.sp===n));
 $('speedtxt').textContent=`${n}: ${LIM[0]} m/s forward, ${LIM[1]} sideways, ${LIM[2]} rad/s turning — applies to everyone, agents included.`}
document.querySelectorAll('#speeds [data-sp]').forEach(b=>b.addEventListener('click',()=>{const n=b.dataset.sp;showSpeed(n);
 post({speed:n});$('dstat').textContent=`Speed set to ${n} for everyone`}));showSpeed(SPEED);
document.querySelectorAll('.acts [data-a]').forEach(b=>b.addEventListener('click',()=>{if(!armed)return;held.clear();paint();
 post({action:b.dataset.a});$('dstat').textContent=b.textContent}));
function look(step){if(!armed)return;held.clear();paint();const cur=ctl.look_deg||0,to=step?Math.max(-30,Math.min(30,cur+step)):0;
 ctl.look_deg=to;post({look_deg:to});$('dstat').textContent=to?`Camera tilted ${Math.abs(to)}° ${to>0?'up':'down'}`:'Camera level'}
document.querySelectorAll('[data-look]').forEach(b=>b.addEventListener('click',()=>look(+b.dataset.look)));
$('avoid').addEventListener('change',e=>{if(!armed){e.target.checked=!!ctl.avoid;return}held.clear();paint();post({avoid:e.target.checked});
 $('dstat').textContent='Obstacle avoidance '+(e.target.checked?'on':'off')});
$('armed').addEventListener('change',e=>{setArmed(e.target.checked);if(!e.target.checked)stop()});
fetch('/control').then(r=>r.json()).then(c=>{allowed=c.allowed;
 $('dnote').textContent=allowed?'':'view only: your computer is not on the lab network';$('armed').disabled=!allowed;setArmed(false)});
setArmed(false);

const ago=t=>{const s=Date.now()/1000-t;return s<60?Math.round(s)+' s ago':Math.round(s/60)+' min ago'};
const esc=t=>String(t).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmtPose=m=>m&&m.map_pose?`map ${m.map_pose.x.toFixed(2)}, ${m.map_pose.y.toFixed(2)} · ${deg(m.map_pose.yaw)}°`:'no map pose';
let agSel=null,agLatest=null;
function showPhoto(m){if(!m)return;agSel=m.id;$('agimg').src=m.url;$('agimg').hidden=false;
 $('agcap').textContent=`${m.client} · ${ago(m.t)} · ${fmtPose(m)}${m.still?'':' · taken while moving'}${m.note?' · '+m.note:''}`;
 document.querySelectorAll('#agthumbs img').forEach(i=>i.classList.toggle('sel',i.dataset.id===m.id))}
function renderAgents(a){const o=a.owner,cur=a.current,bar=$('ctlbar');
 bar.className='full ctlbar'+(o?' '+o.kind:'');
 let t;if(!o)t='Control: free<small>Agents can claim the dog. People can drive from this page.</small>';
 else if(o.kind==='agent')t=`Agent <b>${esc(o.client)}</b> is driving<small>${cur?`doing ${esc(cur.call)} ${esc(JSON.stringify(Object.fromEntries(Object.entries(cur.args).filter(([k])=>!['client','note','inline'].includes(k)))))} for ${cur.secs.toFixed(0)} s`:`idle for ${o.idle_s.toFixed(0)} s (claim lapses at 60 s)`} · from ${o.ip}</small>`;
 else t=(o.client===CLIENT?'<b>You have control.</b>':`A person at ${o.ip} has control.`)+'<small>Agents are locked out until Hand back (or 5 min with no driving).</small>';
 $('ctltext').innerHTML=t;
 $('takeover').hidden=!!(o&&o.kind==='human'&&o.client===CLIENT);$('handback').hidden=!(o&&o.kind==='human');
 $('takeover').disabled=$('handback').disabled=!allowed;
 const notes=Object.entries(a.notes||{});
 $('agnow').innerHTML=notes.length?notes.map(([c,n])=>`<b>${esc(c)}</b>: ${esc(n.text)} <span>(${ago(n.t)})</span>`).join('<br>'):'Agents can post what they are doing with a note.';
 const ph=a.photos||[];$('agsec').hidden=!ph.length&&!notes.length&&!(a.log||[]).length;$('agcount').textContent=ph.length?`${ph.length} recent photos`:'';
 const ids=ph.map(p=>p.id).join();if($('agthumbs').dataset.ids!==ids){$('agthumbs').dataset.ids=ids;
  $('agthumbs').innerHTML=ph.slice().reverse().map(p=>`<img src="${p.url}" data-id="${p.id}" alt="photo by ${esc(p.client)}">`).join('');
  document.querySelectorAll('#agthumbs img').forEach(i=>i.onclick=()=>showPhoto(ph.find(p=>p.id===i.dataset.id)))}
 const last=ph[ph.length-1];if(last&&last.id!==agLatest){agLatest=last.id;showPhoto(last)}
 renderLog(a.log||[])}
let LOGALL=false,LASTLOG=[];const OPENLOG=new Set();try{LOGALL=localStorage.getItem('go2logall')==='1'}catch(e){}
// agent call log: one truncated line per call; click (or "Show all in full") opens a compact key/value block
const LOGOK=new Set(['done','ok']);
const lgEmpty=v=>v==null||v===''||(Array.isArray(v)&&!v.length)||(typeof v==='object'&&!Array.isArray(v)&&!Object.keys(v).length);
function lgVal(v){if(typeof v==='number')return Number.isInteger(v)?String(v):String(+v.toFixed(Math.abs(v)>=100?1:2));
 if(typeof v==='boolean')return v?'yes':'no';if(typeof v==='string')return v;
 if(Array.isArray(v))return v.map(x=>x!==null&&typeof x==='object'?JSON.stringify(x):lgVal(x)).join(', ');
 if(v&&typeof v==='object')return Object.entries(v).filter(([,x])=>!lgEmpty(x)).map(([k,x])=>`${k} ${x!==null&&typeof x==='object'?JSON.stringify(x):lgVal(x)}`).join(', ');
 return String(v)}
function logDetail(e){const skip=new Set(['t','client','call','args','note','result','reason','dur_s','map_pose','photos']);
 const R=[['when',new Date(e.t*1000).toLocaleString()]];
 if(!lgEmpty(e.args))R.push(['asked',lgVal(e.args)]);
 if(e.reason)R.push(['result',(e.result||'?')+' — '+e.reason,LOGOK.has(e.result)?'ok':'err']);   // the row already shows a bare result
 if(e.dur_s!=null)R.push(['took',lgVal(e.dur_s)+' s']);
 for(const [k,v] of Object.entries(e))if(!skip.has(k)&&!lgEmpty(v))R.push([k,lgVal(v)]);
 if(e.map_pose)R.push(['ended at',fmtPose(e)]);
 if(!lgEmpty(e.photos))R.push(['photos',e.photos.join(', ')]);
 return (e.note?`<p class="lgnote">${esc(e.note)}</p>`:'')+'<div class="lgkv">'+R.map(([k,v,c])=>`<div><span>${esc(k)}</span><span${c?` class="${c}"`:''}>${esc(v)}</span></div>`).join('')+'</div>'}
function renderLog(log){LASTLOG=log;$('logall').textContent=LOGALL?'Collapse all':'Show all in full';
 $('aglog').innerHTML=log.slice().reverse().map(e=>{const k=e.t+'|'+e.client,open=LOGALL||OPENLOG.has(k),ok=LOGOK.has(e.result);
  const args=lgEmpty(e.args)?'':lgVal(e.args),res=(e.result||'?')+(e.reason?': '+e.reason:'');
  return `<tr class="row${open?' open':''}" data-k="${esc(k)}"${e.note?` title="${esc(e.note.slice(0,300))}"`:''}><td>${new Date(e.t*1000).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false})}</td><td>${esc(e.client)}</td><td><b>${esc(e.call)}</b> <span class="lgargs">${esc(args)}</span></td><td class="${ok?'ok':'err'}">${esc(res)}</td></tr>`
   +(open?`<tr class="det"><td colspan="4">${logDetail(e)}</td></tr>`:'')}).join('')}
$('aglog').addEventListener('click',ev=>{const tr=ev.target.closest('tr.row');if(!tr||getSelection().toString())return;
 const k=tr.dataset.k;OPENLOG.has(k)?OPENLOG.delete(k):OPENLOG.add(k);renderLog(LASTLOG)});
$('logall').addEventListener('click',()=>{LOGALL=!LOGALL;OPENLOG.clear();try{localStorage.setItem('go2logall',LOGALL?'1':'0')}catch(e){}renderLog(LASTLOG)});
$('takeover').addEventListener('click',()=>{held.clear();paint();post({takeover:true});$('dstat').textContent='You took over: agents are locked out'});
$('handback').addEventListener('click',()=>{stop();post({handback:true})});
async function loadPlaces(){try{PLACES=await (await fetch('/places')).json()}catch(e){return}
 const v=Object.values(PLACES);$('plnote').textContent=v.length?v.length+' saved':'';
 $('places').innerHTML=v.length?v.map(p=>`<div class="pl"><img src="${esc(p.preview||'')}" alt=""><div data-sel="${esc(p.id)}" style="cursor:pointer">${esc(p.id)}<small>${esc(p.description||'')}${p.target?` · thing at ${p.target.x.toFixed(1)}, ${p.target.y.toFixed(1)}`:''} · stand ${p.x.toFixed(1)}, ${p.y.toFixed(1)} facing ${Math.round(p.yaw_deg)}°</small></div><button data-ren="${esc(p.id)}">Rename</button><button data-del="${esc(p.id)}">Delete</button></div>`).join('')
  :'<div class="legend">No places yet.</div>';
 document.querySelectorAll('[data-sel]').forEach(d=>d.onclick=()=>{SELPLACE=SELPLACE===d.dataset.sel?null:d.dataset.sel;plotMap(lastMap,lastPose)});
 document.querySelectorAll('[data-del]').forEach(b=>b.onclick=async()=>{if(!confirm('Delete place '+b.dataset.del+'?'))return;
  await fetch('/places/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:b.dataset.del})});loadPlaces()});
 document.querySelectorAll('[data-ren]').forEach(b=>b.onclick=async()=>{const id=b.dataset.ren,to=(prompt('New name for '+id,id)||'').trim();if(!to||to===id)return;
  const r=await fetch('/places/rename',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,to,client:'console '+CLIENT})});
  const j=await r.json().catch(()=>({}));if(!r.ok){$('plnote').innerHTML=`<span class="err">${esc(j.reason||r.status)}</span>`;return}if(SELPLACE===id)SELPLACE=to;loadPlaces()})}
$('plform').addEventListener('submit',async e=>{e.preventDefault();
 const r=await fetch('/places',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:$('plid').value.trim(),description:$('pldesc').value,client:'console '+CLIENT})});
 if(!r.ok){const j=await r.json().catch(()=>({}));$('plnote').innerHTML=`<span class="err">${esc(j.reason||r.status)}</span>`;return}
 $('plid').value=$('pldesc').value='';loadPlaces()});
loadPlaces();setInterval(loadPlaces,5000);
const hhmm=t=>{const d=new Date(t*1000);return d.toLocaleDateString(undefined,{month:'short',day:'numeric'})+' '+d.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})};
const side=b=>Math.abs(b)<=10?'ahead':Math.abs(b)>=100?'behind':`${Math.abs(b)}° ${b>0?'left':'right'}`;
function pickView(v){DROP.view=v;$('dropbig').hidden=!v;if(v)$('dropbig').src=v.url;
 document.querySelectorAll('#dropviews figure').forEach(f=>f.classList.toggle('sel',!!v&&f.dataset.url===v.url));
 $('dropstandnote').textContent=v?'Agents will stand where the dog took this view (arrow) and turn to face the dot.'
  :'No view picked: agents will stand on open floor next to the dot, facing it.';plotMap(lastMap,lastPose)}
function mapAt(e){const c=$('map'),b=c.getBoundingClientRect(),{inv,m}=mapXf;
 const px=e.clientX-b.left,py=e.clientY-b.top,q=inv.transformPoint({x:px,y:py});
 const x=m.origin[0]+q.x*m.resolution,y=m.origin[1]+(m.height-q.y)*m.resolution;
 const inside=!(x<m.origin[0]||y<m.origin[1]||x>m.origin[0]+m.width*m.resolution||y>m.origin[1]+m.height*m.resolution);
 return {x,y,px,py,inside}}
// "Set dog position": click where the dog is, or press there and drag toward where it faces
const PLACE_HINT='Click where the dog is now. To give its heading too, press there and drag the way it faces.';
function setPlacing(on){PLACING=on;PDOWN=null;$('placedog').classList.toggle('on',on);$('map').classList.toggle('placing',on);
 $('placedog').textContent=on?'Cancel':'Set dog position';
 if(on){DROP=null;$('drop').hidden=true}
 plotMap(lastMap,lastPose)}
$('placedog').addEventListener('click',()=>setPlacing(!PLACING));
$('map').addEventListener('pointerdown',e=>{if(!PLACING||!mapXf)return;const a=mapAt(e);if(!a.inside)return;
 e.preventDefault();$('map').setPointerCapture(e.pointerId);PDOWN=a});
$('map').addEventListener('pointermove',e=>{if(!PLACING||!PDOWN)return;const a=mapAt(e);plotMap(lastMap,lastPose);
 const g=$('map').getContext('2d');g.save();g.strokeStyle=g.fillStyle='#2b6cb0';g.lineWidth=3;
 g.beginPath();g.arc(PDOWN.px,PDOWN.py,6,0,7);g.fill();
 if(Math.hypot(a.px-PDOWN.px,a.py-PDOWN.py)>12){g.beginPath();g.moveTo(PDOWN.px,PDOWN.py);g.lineTo(a.px,a.py);g.stroke()}g.restore()});
$('map').addEventListener('pointerup',async e=>{if(!PLACING||!PDOWN)return;const d=PDOWN,a=mapAt(e);PDOWN=null;
 const body={action:'localize_at',x:+d.x.toFixed(2),y:+d.y.toFixed(2)};
 if(Math.hypot(a.px-d.px,a.py-d.py)>12)body.yaw_deg=+(Math.atan2(a.y-d.y,a.x-d.x)*180/Math.PI).toFixed(0);
 setPlacing(false);PLACED=Date.now();
 $('mapstatus').textContent=`Lining up near (${body.x}, ${body.y})${body.yaw_deg!=null?`, facing about ${body.yaw_deg}°`:''}…`;
 const r=await fetch('/map',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 const j=await r.json().catch(()=>({}));if(!r.ok)$('mapstatus').innerHTML=`<span class="err">${esc(j.reason||('failed '+r.status))}</span>`});
let PLACED=0;
// screen offset (canvas px) -> map image pixels, undoing the view rotation
const unrot=(dx,dy,s)=>{const c=Math.cos(mapXf.RR),n=Math.sin(mapXf.RR);return [(c*dx+n*dy)/s,(-n*dx+c*dy)/s]};
function zoomAt(f,px,py){if(!mapXf)return;const {s,inv}=mapXf,b=$('map').getBoundingClientRect(),W=b.width,H=b.height;
 const nz=Math.min(16,Math.max(1,VIEW.z*f));if(nz===VIEW.z)return;
 const q=inv.transformPoint({x:px,y:py}),ns=s*nz/VIEW.z;VIEW.z=nz;
 if(nz===1){VIEW.u=VIEW.mw/2;VIEW.v=VIEW.mh/2}else{const [du,dv]=unrot(px-W/2,py-H/2,ns);VIEW.u=q.x-du;VIEW.v=q.y-dv}
 saveView();plotMap(lastMap,lastPose)}
$('map').addEventListener('wheel',e=>{if(!mapXf)return;e.preventDefault();const a=mapAt(e);zoomAt(e.deltaY<0?1.25:0.8,a.px,a.py)},{passive:false});
$('map').addEventListener('pointerdown',e=>{if(PLACING||!mapXf||e.button!==0)return;PAN={x:e.clientX,y:e.clientY,u:VIEW.u,v:VIEW.v,moved:false,id:e.pointerId}});
$('map').addEventListener('pointermove',e=>{if(!PAN)return;const dx=e.clientX-PAN.x,dy=e.clientY-PAN.y;
 if(!PAN.moved&&Math.hypot(dx,dy)<6)return;if(!PAN.moved){PAN.moved=true;$('map').setPointerCapture(PAN.id);VIEW.follow=false;$('zfollow').checked=false}
 const [du,dv]=unrot(dx,dy,mapXf.s);VIEW.u=PAN.u-du;VIEW.v=PAN.v-dv;plotMap(lastMap,lastPose)});
$('map').addEventListener('pointerup',()=>{if(PAN&&PAN.moved){PLACED=Date.now();saveView()}PAN=null});
const W2=()=>{const b=$('map').getBoundingClientRect();return [b.width/2,b.height/2]};
$('zin').addEventListener('click',()=>zoomAt(1.5,...W2()));$('zout').addEventListener('click',()=>zoomAt(1/1.5,...W2()));
$('zfit').addEventListener('click',()=>{VIEW.z=1;VIEW.u=VIEW.mw/2;VIEW.v=VIEW.mh/2;VIEW.follow=false;$('zfollow').checked=false;saveView();plotMap(lastMap,lastPose)});
$('zrot').value=VIEW.rot==='room'?'room':'north';$('zrot').addEventListener('change',e=>{VIEW.rot=e.target.value;saveView();plotMap(lastMap,lastPose)});
$('zfollow').checked=VIEW.follow;$('zfollow').addEventListener('change',e=>{VIEW.follow=e.target.checked;saveView();plotMap(lastMap,lastPose)});
$('lsm').addEventListener('click',()=>{VIEW.label=Math.max(9,VIEW.label-2);saveView();plotMap(lastMap,lastPose)});
$('llg').addEventListener('click',()=>{VIEW.label=Math.min(28,VIEW.label+2);saveView();plotMap(lastMap,lastPose)});
// stable per-panel key (id, else heading text), shared by the size and order code; fixed once at load
document.querySelectorAll('main>section').forEach((sec,i)=>{const h=sec.querySelector('h2');sec.dataset.k=sec.id||(h&&h.firstChild.textContent.trim())||String(i)});
const secKey=sec=>sec.dataset.k;
// redraw every canvas after a panel moves or changes size
function redrawAll(){plotMap(lastMap,lastPose);if(lastCloud)plotCloud(...lastCloud);plotRPY()}
// Free layout (Oliver, 2026-11-16): panels sit on a 12-column grid with ~40 px rows. Drag a panel by its header bar
// (not its buttons or inputs) to move it, drag the corner handle to resize; both snap to the grid with a faint outline
// of the target, and other panels move down out of the way. Saved per browser (go2layout); Reset layout restores the
// default. Phones (< 700 px): one column, no dragging.
var FREE=false;
// every panel's content (all but its header) goes in a .pbody: the body scrolls, the frame keeps the resize handles
document.querySelectorAll('main>section').forEach(sec=>{const h=sec.querySelector(':scope>h2');if(!h||sec.id==='ctlbar')return;
 const b=document.createElement('div');b.className='pbody';while(h.nextSibling)b.appendChild(h.nextSibling);sec.appendChild(b)});
const MAIN=document.querySelector('main'),CTL=$('ctlbar'),panels=()=>[...MAIN.children].filter(s=>s.tagName==='SECTION'&&s!==CTL);
const COLS=12,GAP=12,LKEY='go2layout';
let PLAY={},GHOST=null;            // PLAY: key -> {x, y, w, h} as the person left it (the base); shown positions resolve collisions
const pitch=()=>{const W=MAIN.clientWidth-32,cw=(W-GAP*(COLS-1))/COLS,rh=Math.max(30,Math.min(48,Math.round(W/36)));return {cw,rh,cx:cw+GAP,cy:rh+GAP}};
function defaults(){const P=pitch(),sky=new Array(COLS).fill(0),out={};
 panels().forEach(sec=>{const w=sec.classList.contains('full')?12:sec.classList.contains('wide')?8:4;
  const nat=sec.hidden?200:sec.getBoundingClientRect().height,
   h=Math.max(sec.querySelector('.fill')?8:3,Math.min(24,Math.ceil((nat+GAP)/P.cy)));   // camera/map/L515: room to fill
  let best=null;for(let x=0;x<=COLS-w;x++){const y=Math.max(...sky.slice(x,x+w));if(!best||y<best.y)best={x,y}}
  out[secKey(sec)]={x:best.x,y:best.y,w,h};for(let i=best.x;i<best.x+w;i++)sky[i]=best.y+h});
 return out}
const hit=(a,b)=>a.x<b.x+b.w&&b.x<a.x+a.w&&a.y<b.y+b.h&&b.y<a.y+a.h;
function resolve(base,fixed){   // visible panels only; `fixed` keeps its spot, the rest move down until clear (gridstack style)
 const items=panels().filter(s=>!s.hidden&&base[secKey(s)]).map(s=>({k:secKey(s),...base[secKey(s)]}));
 items.sort((a,b)=>(b.k===fixed)-(a.k===fixed)||a.y-b.y||a.x-b.x);
 const placed=[],out={...base};
 for(const it of items){let c;while((c=placed.find(p=>hit(p,it))))it.y=c.y+c.h;placed.push(it);out[it.k]={x:it.x,y:it.y,w:it.w,h:it.h}}
 return out}
function place(sec,r){sec.style.gridColumn=`${r.x+1} / span ${r.w}`;sec.style.gridRow=`${r.y+2} / span ${r.h}`}
function apply(shown){panels().forEach(s=>{const r=shown[secKey(s)];if(r)place(s,r)})}
function relayout(){if(FREE){apply(resolve(PLAY,null));MAIN.style.setProperty('--rowh',pitch().rh+'px')}scheduleRedraw()}
function saveLay(){try{localStorage.setItem(LKEY,JSON.stringify(PLAY))}catch(e){}}
let rdq=false;function scheduleRedraw(){if(rdq||window.__DRAG)return;rdq=true;requestAnimationFrame(()=>{rdq=false;if(window.__DRAG)return;try{redrawAll()}catch(e){}})}
function setFree(on){if(on===FREE)return;FREE=on;MAIN.classList.toggle('free',on);
 if(!on){panels().forEach(s=>{s.style.gridColumn=s.style.gridRow='';s.style.transform=''});scheduleRedraw();return}
 let saved=null;try{saved=JSON.parse(localStorage.getItem(LKEY)||'null')}catch(e){}
 const def=defaults();PLAY={};
 // saved panels keep their spots; panels new since then go below everything
 let bottom=0;if(saved)panels().forEach(s=>{const r=saved[secKey(s)];if(r){PLAY[secKey(s)]=r;bottom=Math.max(bottom,r.y+r.h)}});
 panels().forEach(s=>{const k=secKey(s);if(!PLAY[k])PLAY[k]=saved?{...def[k],x:0,y:bottom+def[k].y}:def[k]});
 relayout()}
function ghost(r){if(!GHOST){GHOST=document.createElement('div');GHOST.className='lghost';MAIN.appendChild(GHOST)}
 if(!r){GHOST.hidden=true;return}GHOST.hidden=false;place(GHOST,r)}
const NODRAG='button,input,select,textarea,label,a,summary,[contenteditable],iframe,canvas';
panels().forEach(sec=>{const h=sec.querySelector('h2');if(!h)return;
 h.classList.add('draghd');h.title='Drag to move this panel';
 const rz=document.createElement('i');rz.className='rsz';rz.title='Drag to resize';
 const er=document.createElement('i');er.className='rsz-r';er.title='Drag to change the width';
 const eb=document.createElement('i');eb.className='rsz-b';eb.title='Drag to change the height';sec.append(er,eb,rz);
 let d=null;
 const start=(e,mode)=>{if(!FREE||e.button)return;if(mode==='move'&&e.target.closest(NODRAG))return;
  const k=secKey(sec),r=resolve(PLAY,null)[k];d={mode,k,x0:e.clientX,y0:e.clientY,r0:{...r},base:{...PLAY},cur:{...r},moved:false};
  e.currentTarget.setPointerCapture(e.pointerId);e.preventDefault();e.stopPropagation()};
 const move=e=>{if(!d)return;const P=pitch(),dx=e.clientX-d.x0,dy=e.clientY-d.y0;
  if(!d.moved&&Math.hypot(dx,dy)<4)return;
  if(!d.moved){d.moved=true;window.__DRAG=true;sec.classList.add('dragging');document.body.classList.add('dragging')}
  const r={...d.r0};
  if(d.mode==='move'){r.x=Math.max(0,Math.min(COLS-r.w,Math.round(d.r0.x+dx/P.cx)));r.y=Math.max(0,Math.round(d.r0.y+dy/P.cy));sec.style.transform=`translate(${dx}px,${dy}px)`}
  else{if(d.mode!=='h')r.w=Math.max(2,Math.min(COLS-r.x,Math.round(d.r0.w+dx/P.cx)));
   if(d.mode!=='w')r.h=Math.max(2,Math.round(d.r0.h+dy/P.cy))}  // size applied on drop
  if(e.clientY<50)scrollBy(0,-18);else if(e.clientY>innerHeight-50)scrollBy(0,18);
  if(r.x===d.cur.x&&r.y===d.cur.y&&r.w===d.cur.w&&r.h===d.cur.h&&GHOST&&!GHOST.hidden)return;
  d.cur=r;ghost(r)};       // only the snap outline moves during a drag (no panel resizes, no redraws: no flicker)
 const end=()=>{if(!d)return;const dd=d;d=null;if(!dd.moved)window.__DRAG=false;sec.style.transform='';sec.classList.remove('dragging');document.body.classList.remove('dragging');ghost(null);
  if(!dd.moved)return;PLAY=resolve({...dd.base,[dd.k]:dd.cur},dd.k);saveLay();
  window.__DRAG=false;window.__ROQUIET=performance.now()+300;apply(resolve(PLAY,null));
  // one redraw with the latest data once the new sizes are laid out
  requestAnimationFrame(()=>{const p=PENDING;PENDING=null;try{if(p)render(p);else redrawAll()}catch(e){}})};
 h.addEventListener('pointerdown',e=>start(e,'move'));rz.addEventListener('pointerdown',e=>start(e,'size'));
 er.addEventListener('pointerdown',e=>start(e,'w'));eb.addEventListener('pointerdown',e=>start(e,'h'));
 [h,rz,er,eb].forEach(el=>{el.addEventListener('pointermove',move);el.addEventListener('pointerup',end);el.addEventListener('pointercancel',end)})});
// panels that appear or disappear (agent photos, suggestions) re-flow; canvases redraw when their panel changes size
// (render() sets .hidden on every /events message; setting it fires a mutation even when unchanged, which used to
// relayout and redraw everything 10 times a second: only react when a panel really appeared or disappeared)
const VIS=new Map(panels().map(s=>[s,s.hidden]));
const MO=new MutationObserver(()=>{let ch=false;panels().forEach(s=>{if(VIS.get(s)!==s.hidden){VIS.set(s,s.hidden);ch=true}});if(ch&&FREE)relayout()});
panels().forEach(s=>MO.observe(s,{attributes:true,attributeFilter:['hidden']}));
const RO=new ResizeObserver(()=>{if(performance.now()<(window.__ROQUIET||0))return;scheduleRedraw()});['map','cloud','rpyplot'].forEach(id=>$(id)&&RO.observe($(id)));
const wide=()=>innerWidth>=700;
addEventListener('resize',()=>{setFree(wide());relayout()});
setFree(wide());
$('resetlayout').addEventListener('click',()=>{try{['go2layout','go2order'].forEach(k=>localStorage.removeItem(k));
 for(let i=localStorage.length-1;i>=0;i--){const k=localStorage.key(i);if(k&&k.startsWith('go2sz:'))localStorage.removeItem(k)}}catch(err){}location.reload()});
$('map').addEventListener('click',async e=>{if(!mapXf||PLACING||Date.now()-PLACED<500)return;
 const {x,y,inside}=mapAt(e);if(!inside)return;
 if(LBLPICK){lblPick(false);lblNear(x,y);return}
 if(ADDING){addAt(x,y);return}
 const hit=LAY.on.objects&&objAt(x,y);if(hit){DROP=null;$('drop').hidden=true;showObj(hit);plotMap(lastMap,lastPose);return}
 if(SELOBJ){SELOBJ=null;$('objp').hidden=true}
 DROP={x,y,view:null,spot:null};$('drop').hidden=false;$('dropxy').textContent=`${x.toFixed(2)}, ${y.toFixed(2)}`;
 $('dropspot').textContent='';$('dropviews').innerHTML='';$('dropvnote').textContent='Looking for camera views near here…';$('dropmsg').textContent='';pickView(null);
 const mine=DROP;let r;try{[r,COVER]=await Promise.all([fetch(`/trail/near?x=${x}&y=${y}`).then(q=>q.json()),fetch('/trail/coverage').then(q=>q.json())])}catch(err){$('dropvnote').textContent='Could not load camera views.';return}
 if(DROP!==mine)return;DROP.spot=r.spot;
 $('dropspot').innerHTML=r.spot==='obstacle'?'<span class="err">on furniture or a wall</span>':r.spot==='unseen'?'<span class="err">not mapped yet</span>':'open floor';
 const fv=r.views.filter(v=>v.facing).length;
 $('dropvnote').textContent=r.views.length?`${r.views.length} camera views from within 3 m${fv?`, ${fv} looking toward this spot`:''}. Pick one for the place's picture. Blue dots on the map show where views exist.`
  :'No camera views near here yet. They are kept while the dog drives around lined up with the map. You can still save the place, without a picture.';
 $('dropviews').innerHTML=r.views.map(v=>`<figure data-url="${v.url}"><img src="${v.url}" alt="camera view" loading="lazy"><figcaption>${hhmm(v.t)} · ${v.dist} m · ${v.facing?'spot '+side(v.bearing_deg):'facing away'}</figcaption></figure>`).join('');
 document.querySelectorAll('#dropviews figure').forEach((f,i)=>f.onclick=()=>pickView(r.views[i]));
 if(r.views[0]&&r.views[0].facing)pickView(r.views[0]);else plotMap(lastMap,lastPose);$('dropid').focus()});
$('dropx').addEventListener('click',()=>{DROP=null;$('drop').hidden=true;plotMap(lastMap,lastPose)});
// object panel: rename, relabel, confirm, delete (POST /map/objects; allowed while someone else drives)
$('objlabels').innerHTML=['tag',...OBJLABELS].map(l=>`<option value="${l}">`).join('');
// Add object (Edit places): press the button, click the map, fill in the form; the object is drawn and draggable like the others
let ADDING=false,ADDAT=null;
function setAdding(on){ADDING=on;$('addobj').classList.toggle('on',on);$('addobj').textContent=on?'Cancel add':'Add object';if(on){editMsg('click the map where the object or tag is');ADDAT=null;$('addp').hidden=true}plotMap(lastMap,lastPose)}
$('addobj').addEventListener('click',()=>setAdding(!ADDING));
function addAt(x,y){setAdding(false);ADDAT={x,y};DROP=null;$('drop').hidden=true;$('addp').hidden=false;$('addxy').textContent=`${x.toFixed(2)}, ${y.toFixed(2)}`;$('addmsg').textContent='';plotMap(lastMap,lastPose);$('addname').focus()}
const addClose=()=>{ADDAT=null;$('addp').hidden=true;plotMap(lastMap,lastPose)};
$('addx').addEventListener('click',addClose);
$('addform').addEventListener('submit',async e=>{e.preventDefault();if(!ADDAT)return;const av=$('addaruco').value.trim();
 const body={action:'add',name:$('addname').value.trim(),label:$('addlabel').value.trim().toLowerCase()||(av!==''?'tag':''),x:+ADDAT.x.toFixed(2),y:+ADDAT.y.toFixed(2),
  yaw:+((+$('addyaw').value||0)*Math.PI/180).toFixed(4),aruco_id:av===''?null:+av,client:'console '+CLIENT};
 $('addmsg').textContent='…';let r,j={};try{r=await fetch('/map/objects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});j=await r.json().catch(()=>({}))}
 catch(err){$('addmsg').innerHTML='<span class="err">failed: is the console running?</span>';return}
 if(!r.ok){$('addmsg').innerHTML=`<span class="err">${esc(j.reason||('failed '+r.status))}</span>`;return}
 $('addname').value=$('addlabel').value=$('addaruco').value='';addClose();editMsg(`added ${j.object.name}`);
 const cb=document.querySelector('[data-layer=objects]');if(!cb.checked){cb.checked=true;cb.dispatchEvent(new Event('change'))}
 await loadObjects();const o=OBJS.find(o=>o.id===j.object.id);if(o)showObj(o);plotMap(lastMap,lastPose)});
function showObj(o,keep){SELOBJ=o;$('objp').hidden=false;if(!keep)$('objmsg').textContent='';
 $('objtitle').innerHTML=`<span class="objsw" style="background:${objCol(o.label)}"></span>${esc(o.name||o.label)}`;
 $('objmeta').textContent=`${o.label}${o.aruco_id!=null?` · tag ${o.aruco_id}`:''} · ${o.source==='hand'?'added by hand':`${o.votes??0} votes`} · ${o.w.toFixed(1)}×${o.h.toFixed(1)} m at ${o.x.toFixed(1)}, ${o.y.toFixed(1)}`+(o.confirmed_by?` · confirmed by ${o.confirmed_by}`:' · not confirmed');
 if(document.activeElement!==$('objname'))$('objname').value=o.name||'';if(document.activeElement!==$('objlabel'))$('objlabel').value=o.label||'';
 if(!$('objset').contains(document.activeElement)){$('objaruco').value=o.aruco_id??'';$('objw').value=+o.w.toFixed(2);$('objh').value=+o.h.toFixed(2);$('objyaw').value=Math.round((o.yaw||0)*180/Math.PI)}}
async function objPost(b){if(!SELOBJ)return;const id=SELOBJ.id;$('objmsg').textContent='…';let r,j={};
 try{r=await fetch('/map/objects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...b,id,client:'console '+CLIENT})});j=await r.json().catch(()=>({}))}
 catch(e){$('objmsg').innerHTML='<span class="err">failed: is the console running?</span>';return}
 if(!r.ok){$('objmsg').innerHTML=`<span class="err">${esc(j.reason||('failed '+r.status))}</span>`;return}
 if(b.action==='delete'){SELOBJ=null;$('objp').hidden=true}else if(j.object){document.activeElement.blur();showObj(j.object);$('objmsg').textContent={rename:'Renamed',relabel:'Relabelled',move:'Moved',confirm:'Confirmed',set:'Saved'}[b.action]||'Done'}
 loadObjects();return true}
$('objx').addEventListener('click',()=>{SELOBJ=null;$('objp').hidden=true;plotMap(lastMap,lastPose)});
$('objren').addEventListener('submit',e=>{e.preventDefault();objPost({action:'rename',name:$('objname').value.trim()})});
$('objrel').addEventListener('submit',e=>{e.preventDefault();const l=$('objlabel').value.trim().toLowerCase();if(l)objPost({action:'relabel',label:l})});
$('objok').addEventListener('click',()=>objPost({action:'confirm'}));
// marker id (set) and size / facing (move), only what changed
$('objset').addEventListener('submit',async e=>{e.preventDefault();const o=SELOBJ;if(!o)return;const av=$('objaruco').value.trim(),aid=av===''?null:+av;
 const w=+$('objw').value,h=+$('objh').value,yaw=+(+$('objyaw').value*Math.PI/180).toFixed(4),mv={};
 if(Math.abs(w-o.w)>0.004)mv.w=w;if(Math.abs(h-o.h)>0.004)mv.h=h;if(Math.round((o.yaw||0)*180/Math.PI)!==+$('objyaw').value)mv.yaw=yaw;
 if(aid!==(o.aruco_id??null)&&!await objPost({action:'set',aruco_id:aid}))return;
 if(Object.keys(mv).length)await objPost({action:'move',...mv})});
$('objrot').addEventListener('click',()=>objPost({action:'move',yaw:+(ROOM_DEG*Math.PI/180).toFixed(4)}));
$('objdel').addEventListener('click',()=>{if(SELOBJ&&confirm(`Delete ${SELOBJ.name||SELOBJ.label} from the map?`))objPost({action:'delete'})});
document.querySelectorAll('[data-layer]').forEach(b=>{const n=b.dataset.layer;b.checked=!!LAY.on[n];b.addEventListener('change',()=>{LAY.on[n]=b.checked;
 try{localStorage.setItem('go2layers',JSON.stringify(LAY.on))}catch(e){}if(b.checked){LAY.t[n]=null;LAY.last[n]=0;if(n==='objects')loadObjects()}
 if(n==='objects'&&!b.checked){SELOBJ=null;$('objp').hidden=true}plotMap(lastMap,lastPose)})});
loadObjects();setInterval(()=>{if(LAY.on.objects)loadObjects()},10000);
// ---- Map suggestions: review the tidy pass's proposals (GET/POST /map/proposals), previewed on the map in purple
let PROPS={items:[],hover:null,sel:null,vis:true};
function propDraw(g,mp,RR){const show=[],all=$('propmapall').checked;
 for(const it of PROPS.items){if(it.status)continue;const hl=it.id===PROPS.hover||it.id===PROPS.sel;if(hl||all)show.push([it,hl])}
 if(!show.length)return;const col=css('--prop')||'#c77dff';g.save();g.font='11px monospace';
 const txt=(t,x,y)=>{g.lineWidth=3;g.strokeStyle='rgba(15,18,20,.85)';g.strokeText(t,x,y);g.fillStyle=col;g.fillText(t,x,y)};
 for(const [it,hl] of show.sort((a,b)=>a[1]-b[1])){const ch=it.change||{};g.globalAlpha=hl?1:.35;g.strokeStyle=g.fillStyle=col;g.lineWidth=hl?2.5:1.5;
  if(it.kind==='place_move'){const cur=PLACES[it.target_id],[nx,ny]=mp(ch.x,ch.y);
   if(cur){const [cx,cy]=mp(cur.x,cur.y),a=Math.atan2(ny-cy,nx-cx);g.setLineDash([5,4]);g.beginPath();g.moveTo(cx,cy);g.lineTo(nx,ny);g.stroke();g.setLineDash([]);
    if(Math.hypot(nx-cx,ny-cy)>14){g.beginPath();g.moveTo(nx-9*Math.cos(a-.45),ny-9*Math.sin(a-.45));g.lineTo(nx,ny);g.lineTo(nx-9*Math.cos(a+.45),ny-9*Math.sin(a+.45));g.stroke()}
    g.beginPath();g.arc(cx,cy,4,0,7);g.stroke()}
   if(ch.target){const [tx,ty]=mp(ch.target.x,ch.target.y);g.lineWidth=1;g.beginPath();g.moveTo(nx,ny);g.lineTo(tx,ty);g.stroke();
    g.beginPath();g.moveTo(tx,ty-7);g.lineTo(tx+7,ty);g.lineTo(tx,ty+7);g.lineTo(tx-7,ty);g.closePath();g.fill()}
   if(ch.yaw_deg!=null){const a=RR-ch.yaw_deg*Math.PI/180;g.save();g.translate(nx,ny);g.rotate(a);g.beginPath();g.moveTo(13,0);g.lineTo(-7,6);g.lineTo(-3,0);g.lineTo(-7,-6);g.closePath();g.fill();g.restore()}
   else{g.beginPath();g.arc(nx,ny,5,0,7);g.fill()}
   if(hl)txt(it.target_id,nx+10,ny-8)}
  else{const c=Math.cos(ch.yaw||0),sn=Math.sin(ch.yaw||0),hw=(ch.w||0.5)/2,hh=(ch.h||0.5)/2,cur=it.kind==='object_move'&&OBJS.find(o=>o.id===it.target_id);
   if(cur){const [ax,ay]=mp(cur.x,cur.y),[bx,by]=mp(ch.x,ch.y);g.setLineDash([5,4]);g.beginPath();g.moveTo(ax,ay);g.lineTo(bx,by);g.stroke();g.setLineDash([])}
   g.beginPath();[[hw,hh],[-hw,hh],[-hw,-hh],[hw,-hh]].forEach(([u,v],i)=>{const [px,py]=mp(ch.x+u*c-v*sn,ch.y+u*sn+v*c);i?g.lineTo(px,py):g.moveTo(px,py)});g.closePath();
   if(hl){g.globalAlpha=.15;g.fill();g.globalAlpha=1}g.stroke();if(hl){const [lx,ly]=mp(ch.x,ch.y);txt(ch.name||ch.label||it.target_id||'',lx+8,ly-8)}}}
 g.restore()}
function propRender(){const all=PROPS.items,pend=all.filter(i=>!i.status).sort((a,b)=>(b.confidence||0)-(a.confidence||0)),rev=all.filter(i=>i.status);
 $('propnote').textContent=all.length?`${pend.length} to review`:'';const list=$('propshowrev').checked?pend.concat(rev):pend;
 const KIND={place_move:'move place',object_new:'new object',object_move:'move object'};
 $('proplist').innerHTML=list.length?list.map(it=>{const c=Math.max(0,Math.min(1,+it.confidence||0));
  return `<div class="prow${it.status?' rev':''}${it.id===PROPS.hover||it.id===PROPS.sel?' hl':''}" data-pid="${esc(it.id)}"><div>
   <div class="ps"><span class="pk">${KIND[it.kind]||esc(it.kind)}</span>${esc(it.summary||it.target_id||it.id)}</div>
   <div><span class="pconf" title="confidence ${c.toFixed(2)}"><i class="${c<0.5?'lo':''}" style="width:${c*100}%"></i></span><small>${c.toFixed(2)}</small></div>
   ${it.reason?`<div class="preason">${esc(it.reason)}</div>`:''}${(it.flags||[]).map(f=>`<span class="pflag">⚠ ${esc(f)}</span>`).join('')}
   ${(it.evidence||[]).length?`<div class="pev">${it.evidence.slice(0,3).map(u=>`<img src="${esc(u)}" data-big="${esc(u)}" alt="evidence photo" loading="lazy">`).join('')}</div>`:''}</div>
   <div class="pbtns">${it.status?`<span class="pstat">${esc(it.status)}${it.reviewed_by?' by '+esc(it.reviewed_by):''}</span>`
    :`<button type="button" class="ok" data-act="accept">Accept</button><button type="button" data-act="reject">Reject</button>`}</div></div>`}).join('')
  :`<div class="legend">${all.length?'Nothing left to review.':'No suggestions yet. They appear here after a tidy run.'}</div>`;
 $('proplist').querySelectorAll('.prow').forEach(r=>{const id=r.dataset.pid;
  r.onmouseenter=()=>{PROPS.hover=id;r.classList.add('hl');plotMap(lastMap,lastPose)};r.onmouseleave=()=>{PROPS.hover=null;if(PROPS.sel!==id)r.classList.remove('hl');plotMap(lastMap,lastPose)};
  r.onclick=e=>{const b=e.target.closest('button'),im=e.target.closest('[data-big]');
   if(im){$('propbigimg').src=im.dataset.big;$('propbig').hidden=false;return}
   if(b){propAct(b.dataset.act,id);return}
   PROPS.sel=PROPS.sel===id?null:id;propRender();plotMap(lastMap,lastPose)}})}
async function loadProps(){let j;try{j=await (await fetch('/map/proposals')).json()}catch(e){return}PROPS.items=j.items||[];
 if(PROPS.sel&&!PROPS.items.some(i=>i.id===PROPS.sel&&!i.status))PROPS.sel=null;propRender();plotMap(lastMap,lastPose)}
async function propAct(action,id){const body={action,client:'console '+CLIENT};if(id)body.id=id;if(action==='accept_all')body.min_confidence=0.7;
 $('propmsg').textContent='…';let r=null,j={};
 try{r=await fetch('/map/proposals',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});j=await r.json().catch(()=>({}))}catch(e){}
 const done=(j.done||[]).length,errs=j.errors||[];
 $('propmsg').innerHTML=!r||!r.ok?`<span class="err">${esc(j.reason||(r?'failed '+r.status:'no answer'))}</span>`
  :`${action==='reject'?'rejected':'accepted'} ${done}${errs.length?` · <span class="err">${errs.length} failed: ${esc(errs.map(e=>typeof e==='string'?e:(e.reason||e.error||JSON.stringify(e))).join('; '))}</span>`:''}`;
 if(PROPS.sel===id)PROPS.sel=null;await Promise.all([loadProps(),loadPlaces(),loadObjects()]);plotMap(lastMap,lastPose)}
$('propall').addEventListener('click',()=>{const n=PROPS.items.filter(i=>!i.status&&(+i.confidence||0)>=0.7).length;
 if(!n){$('propmsg').textContent='nothing pending at 0.7 or above';return}if(confirm(`Accept ${n} suggestion${n>1?'s':''} with confidence 0.7 or more?`))propAct('accept_all')});
$('propshowrev').addEventListener('change',propRender);$('propmapall').addEventListener('change',()=>plotMap(lastMap,lastPose));
$('propbigx').addEventListener('click',()=>{$('propbig').hidden=true});
// poll every 15 s while the panel is on screen, so a new tidy run shows up
try{new IntersectionObserver(es=>{PROPS.vis=es[0].isIntersecting;if(PROPS.vis)loadProps()}).observe($('propsec'))}catch(e){}
loadProps();setInterval(()=>{if(PROPS.vis&&!document.hidden)loadProps()},15000);
// ---- Edit places: drag stand dots, heading tips, thing markers (and a selected object) with mouse or touch; snaps to walls
const OBJKINDS=['obj','objyaw'],objDrag=id=>EDIT.drag&&OBJKINDS.includes(EDIT.drag.kind)&&EDIT.drag.id===id;
const editCur=q=>EDIT.drag&&!OBJKINDS.includes(EDIT.drag.kind)&&EDIT.drag.id===q.id?EDIT.drag.cur:q;
function editDraw(g,mp,RR){const H=[];g.save();g.lineWidth=1.5;
 for(const q0 of Object.values(PLACES)){const q=editCur(q0),[sx,sy]=mp(q.x,q.y),a=RR-(q.yaw_deg||0)*Math.PI/180,tx=sx+30*Math.cos(a),ty=sy+30*Math.sin(a);
  if(q.target){const [gx,gy]=mp(q.target.x,q.target.y);g.strokeStyle=css('--accent');g.setLineDash([3,3]);g.beginPath();g.moveTo(sx,sy);g.lineTo(gx,gy);g.stroke();g.setLineDash([]);
   g.fillStyle=css('--accent');g.strokeStyle='rgba(15,18,20,.9)';g.beginPath();g.moveTo(gx,gy-8);g.lineTo(gx+8,gy);g.lineTo(gx,gy+8);g.lineTo(gx-8,gy);g.closePath();g.fill();g.stroke();H.push({kind:'target',id:q.id,px:gx,py:gy})}
  g.strokeStyle=css('--warn');g.beginPath();g.moveTo(sx,sy);g.lineTo(tx,ty);g.stroke();
  g.fillStyle=css('--warn');g.strokeStyle='rgba(15,18,20,.9)';g.beginPath();g.arc(tx,ty,5,0,7);g.fill();g.stroke();H.push({kind:'yaw',id:q.id,px:tx,py:ty});
  g.fillStyle='#fff';g.strokeStyle=css('--accent');g.lineWidth=2.5;g.beginPath();g.arc(sx,sy,6,0,7);g.fill();g.stroke();g.lineWidth=1.5;H.push({kind:'stand',id:q.id,px:sx,py:sy})}
 if(SELOBJ&&LAY.on.objects){const o0=OBJS.find(o=>o.id===SELOBJ.id);if(o0){const o=objDrag(o0.id)?{...o0,...EDIT.drag.cur}:o0,[ox,oy]=mp(o.x,o.y);
  if(o.aruco_id==null){g.fillStyle='#fff';g.strokeStyle=objCol(o.label);g.lineWidth=2.5;g.fillRect(ox-5,oy-5,10,10);g.strokeRect(ox-5,oy-5,10,10);H.push({kind:'obj',id:o.id,px:ox,py:oy})}}}
 // every marker: drag its spot to move it, the circle at its arrow tip to turn it (the arrow itself is drawn with the objects)
 if(LAY.on.objects)for(const o0 of OBJS){if(o0.aruco_id==null)continue;const o=objDrag(o0.id)?{...o0,...EDIT.drag.cur}:o0,[ox,oy]=mp(o.x,o.y),a=RR-(o.yaw||0),L=markLen(VIEW.label/11)+6,tx=ox+L*Math.cos(a),ty=oy+L*Math.sin(a);
  g.lineWidth=1.5;g.strokeStyle='rgba(15,18,20,.9)';g.fillStyle=css('--warn');g.beginPath();g.arc(tx,ty,5,0,7);g.fill();g.stroke();
  g.strokeStyle=MARKCOL;g.lineWidth=2;g.beginPath();g.arc(ox,oy,6,0,7);g.stroke();
  H.push({kind:'objyaw',id:o.id,px:tx,py:ty},{kind:'obj',id:o.id,px:ox,py:oy})}
 if(ADDAT){const [ax,ay]=mp(ADDAT.x,ADDAT.y);g.strokeStyle=css('--warn');g.lineWidth=2;g.beginPath();g.arc(ax,ay,8,0,7);g.moveTo(ax-12,ay);g.lineTo(ax+12,ay);g.moveTo(ax,ay-12);g.lineTo(ax,ay+12);g.stroke()}
 if(EDIT.cross){const [cx,cy]=mp(...EDIT.cross);g.strokeStyle=css('--bad');g.lineWidth=2.5;g.beginPath();g.moveTo(cx-7,cy-7);g.lineTo(cx+7,cy+7);g.moveTo(cx+7,cy-7);g.lineTo(cx-7,cy+7);g.stroke()}
 g.restore();EDIT.handles=H}
function editHit(e){if(!EDIT.on||!mapXf)return null;const b=$('map').getBoundingClientRect(),px=e.clientX-b.left,py=e.clientY-b.top;let best=null;
 for(const h of EDIT.handles){const d=Math.hypot(h.px-px,h.py-py);if(d<=12&&(!best||d<best.d))best={...h,d}}return best}
// base map pixels (0 = wall/furniture, 254 = free), read once per map image
let MAPPX=null;
function mapPx(){if(!lastMap||!mapImg.naturalWidth)return null;if(MAPPX&&MAPPX.src===mapImg.src)return MAPPX;
 const c=document.createElement('canvas');c.width=mapImg.naturalWidth;c.height=mapImg.naturalHeight;const g=c.getContext('2d');g.drawImage(mapImg,0,0);let d;
 try{d=g.getImageData(0,0,c.width,c.height).data}catch(e){return null}const a=new Uint8Array(c.width*c.height);for(let i=0;i<a.length;i++)a[i]=d[i*4];
 return MAPPX={src:mapImg.src,w:c.width,h:c.height,a}}
// nearest wall corner (preferred) or wall cell within 0.3 m of map point x, y. Returns {w: the wall point, p: where to put it}:
// off = 0 puts it on the wall (things); off > 0 puts it that many metres out into free space (stand spots)
function wallSnap(x,y,off){const P=mapPx(),m=lastMap;if(!P)return null;const res=m.resolution;
 const toPx=(x,y)=>[(x-m.origin[0])/res,m.height-(y-m.origin[1])/res],toM=(u,v)=>[m.origin[0]+u*res,m.origin[1]+(m.height-v)*res];
 const val=(u,v)=>{u=Math.floor(u);v=Math.floor(v);return u<0||v<0||u>=P.w||v>=P.h?205:P.a[v*P.w+u]},occ=(u,v)=>val(u,v)<50,free=(u,v)=>val(u,v)>250;
 const [cu,cv]=toPx(x,y),R=0.3/res,al=ROOM_DEG*Math.PI/180,A1=[Math.cos(al),-Math.sin(al)],A2=[-Math.sin(al),-Math.cos(al)],neg=d=>[-d[0],-d[1]];   // room axes, pixel coords
 const arm=(u,v,d)=>occ(u+d[0]*2,v+d[1]*2)&&occ(u+d[0]*4,v+d[1]*4);
 let corner=null,edge=null;
 for(let v=Math.floor(cv-R);v<=cv+R;v++)for(let u=Math.floor(cu-R);u<=cu+R;u++){const pu=u+.5,pv=v+.5,dd=Math.hypot(pu-cu,pv-cv);if(dd>R||!occ(pu,pv))continue;
  if(!edge||dd<edge.d)edge={u:pu,v:pv,d:dd};
  const p1=arm(pu,pv,A1),m1=arm(pu,pv,neg(A1)),p2=arm(pu,pv,A2),m2=arm(pu,pv,neg(A2));
  // a corner: the wall goes on along exactly one direction of each room axis (an L)
  if(p1!==m1&&p2!==m2&&(!corner||dd<corner.d))corner={u:pu,v:pv,d:dd,arms:[p1?A1:neg(A1),p2?A2:neg(A2)]}}
 const hit=corner||edge;if(!hit)return null;const w=toM(hit.u,hit.v);if(!off)return {w,p:w};
 const n=off/res,cands=corner?[[corner.arms[0][0]+corner.arms[1][0],corner.arms[0][1]+corner.arms[1][1]],neg([corner.arms[0][0]+corner.arms[1][0],corner.arms[0][1]+corner.arms[1][1]])]:[A1,neg(A1),A2,neg(A2)];
 cands.push([cu-hit.u,cv-hit.v]);let best=null;
 for(const c of cands){const l=Math.hypot(c[0],c[1]);if(l<1e-6)continue;const eu=hit.u+c[0]/l*n,ev=hit.v+c[1]/l*n;if(!free(eu,ev))continue;
  const dc=Math.hypot(eu-cu,ev-cv);if(!best||dc<best.d)best={eu,ev,d:dc}}
 return {w,p:best?toM(best.eu,best.ev):[x,y]}}
function editMsg(t){EDIT.msg=t;EDIT.msgT=Date.now();$('mapstatus').textContent=t}
function setEdit(on){EDIT.on=on;EDIT.drag=null;EDIT.cross=null;if(!on&&ADDING)setAdding(false);$('editpl').classList.toggle('on',on);$('editpl').textContent=on?'Done editing':'Edit places';$('edithint').hidden=!on;
 if(!on)$('map').style.cursor='';if(on&&PLACING)setPlacing(false);plotMap(lastMap,lastPose)}
$('editpl').addEventListener('click',()=>setEdit(!EDIT.on));
addEventListener('keydown',e=>{if(e.key==='Escape'&&EDIT.on){if(ADDING)setAdding(false);else if(EDIT.drag){EDIT.drag=null;EDIT.cross=null;plotMap(lastMap,lastPose)}else setEdit(false)}});
// these listen on the map's parent in the capture phase, so a grabbed handle never reaches the pan / click / place-marking handlers
const MAPBOX=$('map').parentNode;
MAPBOX.addEventListener('pointerdown',e=>{if(e.target!==$('map')||e.button)return;const h=editHit(e);if(!h)return;
 e.stopPropagation();e.preventDefault();$('map').setPointerCapture(e.pointerId);const a=mapAt(e);
 if(OBJKINDS.includes(h.kind)){const o=OBJS.find(o=>o.id===h.id);EDIT.drag={kind:h.kind,id:h.id,orig:{x:o.x,y:o.y,yaw:o.yaw||0},cur:{x:o.x,y:o.y,yaw:o.yaw||0},off:[o.x-a.x,o.y-a.y],name:o.name||o.label}}
 else{const q=PLACES[h.id],t=q.target;EDIT.drag={kind:h.kind,id:h.id,orig:q,cur:{...q,target:t?{...t}:null},off:h.kind==='target'?[t.x-a.x,t.y-a.y]:[q.x-a.x,q.y-a.y]}}
 $('map').style.cursor='grabbing';plotMap(lastMap,lastPose)},true);
MAPBOX.addEventListener('pointermove',e=>{const d=EDIT.drag;if(!d){if(EDIT.on&&e.target===$('map'))$('map').style.cursor=editHit(e)?'grab':'';return}
 e.stopPropagation();const a=mapAt(e),x=a.x+d.off[0],y=a.y+d.off[1],snap=$('snapw').checked&&!e.shiftKey;EDIT.cross=null;
 if(d.kind==='obj'){d.cur.x=x;d.cur.y=y}
 else if(d.kind==='objyaw'){let ang=Math.atan2(a.y-d.cur.y,a.x-d.cur.x)*180/Math.PI;
  if(!e.shiftKey){const r=ang-ROOM_DEG,k=Math.round(r/90);if(Math.abs(r-k*90)<=8)ang=ROOM_DEG+k*90}d.cur.yaw=ang*Math.PI/180}
 else if(d.kind==='yaw'){let ang=Math.atan2(a.y-d.cur.y,a.x-d.cur.x)*180/Math.PI;
  if(!e.shiftKey){const r=ang-ROOM_DEG,k=Math.round(r/90);if(Math.abs(r-k*90)<=8)ang=ROOM_DEG+k*90}   // square to the room within 8 degrees
  d.cur.yaw_deg=+((((ang+180)%360+360)%360)-180).toFixed(1)}
 else{const sp=snap?wallSnap(x,y,d.kind==='stand'?0.5:0):null,p=sp?sp.p:[x,y];if(sp)EDIT.cross=sp.w;
  if(d.kind==='stand'){d.cur.x=p[0];d.cur.y=p[1]}else d.cur.target={x:p[0],y:p[1]}}
 plotMap(lastMap,lastPose)},true);
MAPBOX.addEventListener('pointercancel',e=>{if(!EDIT.drag)return;e.stopPropagation();EDIT.drag=null;EDIT.cross=null;plotMap(lastMap,lastPose)},true);
MAPBOX.addEventListener('pointerup',async e=>{const d=EDIT.drag;if(!d)return;e.stopPropagation();EDIT.drag=null;EDIT.cross=null;PLACED=Date.now();$('map').style.cursor='grab';
 const r2=v=>+(+v).toFixed(2),o=d.orig,c=d.cur;let url,body,name=d.id;
 if(d.kind==='obj'){if(c.x===o.x&&c.y===o.y){plotMap(lastMap,lastPose);return}url='/map/objects';body={action:'move',id:d.id,x:r2(c.x),y:r2(c.y)};name=d.name;
  const ob=OBJS.find(x=>x.id===d.id);if(ob){ob.x=body.x;ob.y=body.y}}
 else if(d.kind==='objyaw'){if(c.yaw===o.yaw){plotMap(lastMap,lastPose);return}url='/map/objects';body={action:'move',id:d.id,yaw:+c.yaw.toFixed(4)};name=d.name;
  const ob=OBJS.find(x=>x.id===d.id);if(ob)ob.yaw=body.yaw}
 else{url='/places/move';body={id:d.id};
  if(d.kind==='stand'&&(c.x!==o.x||c.y!==o.y)){body.x=r2(c.x);body.y=r2(c.y)}
  if(d.kind==='yaw'&&c.yaw_deg!==o.yaw_deg)body.yaw_deg=c.yaw_deg;
  if(d.kind==='target'&&c.target&&(!o.target||c.target.x!==o.target.x||c.target.y!==o.target.y))body.target={x:r2(c.target.x),y:r2(c.target.y)};
  if(Object.keys(body).length===1){plotMap(lastMap,lastPose);return}
  PLACES[d.id]={...o,...(body.x!=null?{x:body.x,y:body.y}:{}),...(body.yaw_deg!=null?{yaw_deg:body.yaw_deg}:{}),...(body.target?{target:body.target}:{})}}
 body.client='console '+CLIENT;plotMap(lastMap,lastPose);editMsg(`moving ${name}…`);let r=null,j={};
 try{r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});j=await r.json().catch(()=>({}))}catch(err){}
 editMsg(r&&r.ok?`moved ${name}`:`could not move ${name}: ${j.reason||(r?r.status:'no answer')}`);
 if(OBJKINDS.includes(d.kind)){await loadObjects();if(SELOBJ&&SELOBJ.id===d.id)showObj(OBJS.find(x=>x.id===d.id)||SELOBJ,1)}else await loadPlaces();plotMap(lastMap,lastPose)},true);
// label from photos: pick trail photos (since a time, or of a map spot), box the thing, name it; the server places it
const LBLLABELS=['desk','office chair','sofa','conference table','table','cabinet','shelf','door','box','printer','water cooler','trash bin','monitor','other'];
let LBLPICK=false,LBL={frame:null,boxes:[],sel:null,drag:null,last:0};
$('lbllabel').innerHTML=LBLLABELS.map(l=>`<option>${l}</option>`).join('');
const clock=t=>new Date(t*1000).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',second:'2-digit'});
function lblPick(on){LBLPICK=on;$('lblspot').classList.toggle('on',on);$('lblsrcnote').textContent=on?'click a spot on the map…':''}
// photo time window: the Days choice, starting at the "since" time on its first day (All = everything)
function lblStart(){const v=$('lbldays').value;if(v==='all')return 0;const [h,m]=($('lblsince').value||'00:00').split(':').map(Number),d=new Date();
 if(v==='2d')d.setDate(d.getDate()-1);d.setHours(h||0,m||0,0,0);let t=d.getTime()/1000;
 if(v==='drive'){const k=new Date();k.setHours(14,31,0,0);t=Math.max(t,k.getTime()/1000)}return t}
// where each photo was taken from, seen from the spot: 8 sectors of 45° (map up = N)
const SECT=['E','NE','N','NW','W','SW','S','SE'],SECTAR=['←','↙','↓','↘','→','↗','↑','↖'],SECTCOL=['#e06a5a','#e0a84a','#c9b458','#7cc46d','#4fb3a9','#5b9be0','#9a8cf0','#d46ad4'];
let LBLDOTS=null;   // {spot:[x,y], pts:[{x,y,k}]} drawn on the map while spot photos are listed
function lblThumbs(frames,append){const el=$('lblthumbs');if(!append)el.innerHTML='';
 el.insertAdjacentHTML('beforeend',frames.map(f=>`<figure data-url="${esc(f.url)}"${f.k!=null?` title="taken ${f.dist!=null?f.dist+' m ':''}${SECT[f.k]} of the spot"`:''}><img src="${esc(f.url)}" alt="camera photo" loading="lazy"><figcaption>${f.k!=null?`<span style="color:${SECTCOL[f.k]}">${SECTAR[f.k]} from ${SECT[f.k]}</span>`:''}<span>${hhmm(f.t)}</span></figcaption></figure>`).join(''));
 el.querySelectorAll('figure:not([data-on])').forEach(fg=>{fg.dataset.on=1;fg.onclick=()=>lblOpen(fg.dataset.url,fg)})}
async function lblSince(more){let t=LBL.last;if(!more)t=lblStart();if(LBLDOTS){LBLDOTS=null;plotMap(lastMap,lastPose)}
 $('lblsrcnote').textContent='loading…';let j;try{j=await (await fetch(`/trail/since?t=${t}&limit=200`)).json()}catch(e){$('lblsrcnote').textContent='could not load photos';return}
 const fr=j.frames||[];if(fr.length)LBL.last=fr[fr.length-1].t;lblThumbs(fr,more);$('lblmore').hidden=!j.more;
 $('lblsrcnote').textContent=`${$('lblthumbs').children.length} photos${j.more?' (more available)':''}`}
// spot mode: up to 200 photos that looked at the spot, filtered by day, then up to 4 per direction (nearest first) so every side shows
async function lblNear(x,y){$('lblsrcnote').textContent=`photos of ${x.toFixed(1)}, ${y.toFixed(1)}…`;let j;
 try{j=await (await fetch(`/trail/near?x=${x.toFixed(2)}&y=${y.toFixed(2)}&radius=5&limit=200`)).json()}catch(e){$('lblsrcnote').textContent='could not load photos';return}
 const t0=lblStart(),all=(j.views||[]).filter(v=>v.t>=t0),fac=all.filter(v=>v.facing),use=fac.length?fac:all,by=SECT.map(()=>[]);
 for(const v of use){const a=Math.atan2(v.y-y,v.x-x),k=Math.floor((((a+Math.PI/8)%(2*Math.PI))+2*Math.PI)%(2*Math.PI)/(Math.PI/4))%8;
  by[k].push({...v,k,dist:v.dist??+Math.hypot(v.x-x,v.y-y).toFixed(1)})}
 const pick=by.flatMap(g=>g.sort((a,b)=>a.dist-b.dist).slice(0,4));lblThumbs(pick);$('lblmore').hidden=true;
 LBLDOTS={spot:[x,y],pts:pick.map(v=>({x:v.x,y:v.y,k:v.k}))};plotMap(lastMap,lastPose);
 const cnt=by.map((g,k)=>g.length?`${SECT[k]} ${g.length}`:'').filter(Boolean).join(' · ');
 $('lblsrcnote').textContent=pick.length?`${pick.length} of ${use.length} ${fac.length?'facing ':''}photos of ${x.toFixed(1)}, ${y.toFixed(1)}, by direction: ${cnt}`
  :`no photos of ${x.toFixed(1)}, ${y.toFixed(1)} in this time window${(j.views||[]).length?' (try All days)':''}`;
 $('lblsec').scrollIntoView({block:'nearest',behavior:'smooth'})}
$('lblload').addEventListener('click',()=>{lblPick(false);lblSince(false)});$('lblmore').addEventListener('click',()=>lblSince(true));
$('lblspot').addEventListener('click',()=>{lblPick(!LBLPICK);if(LBLPICK)$('map').scrollIntoView({block:'nearest',behavior:'smooth'})});
// boxes are [x1, y1, x2, y2] fractions of the photo; drawn as divs so they follow the image size
const boxDiv=(b,txt,cls)=>`<div class="lbox ${cls||''}" style="left:${b[0]*100}%;top:${b[1]*100}%;width:${(b[2]-b[0])*100}%;height:${(b[3]-b[1])*100}%">${txt?`<span>${esc(txt)}</span>`:''}</div>`;
function lblDraw(){const sel=LBL.sel;let h=LBL.boxes.map((b,i)=>boxDiv(b.box,b.label,sel&&sel.i===i?'sel':'')).join('');
 if(sel&&sel.i==null)h+=boxDiv(sel.box,'your box','sel');if(LBL.drag&&LBL.drag.box)h+=boxDiv(LBL.drag.box,'','sel');$('lblov').innerHTML=h}
async function lblOpen(url,fg){document.querySelectorAll('#lblthumbs figure').forEach(f=>f.classList.toggle('sel',f===fg));
 LBL.frame=url;LBL.boxes=[];LBL.sel=null;$('lblwork').hidden=false;$('lblimg').src=url;$('lblmsg').textContent='';lblDraw();
 $('lbldet').textContent='Asking the vision model for boxes (a few seconds the first time)… or drag a box yourself.';
 let r,j={};try{r=await fetch('/label/detect?url='+encodeURIComponent(url));j=await r.json().catch(()=>({}))}catch(e){j={error:'not answering'}}
 if(LBL.frame!==url)return;if(!r||!r.ok||j.error){$('lbldet').textContent=`No suggestions (${j.error||r.status}). Drag a box around the thing.`;return}
 LBL.boxes=j.boxes||[];lblDraw();$('lbldet').textContent=LBL.boxes.length?`${LBL.boxes.length} suggestions: click one, or drag your own box.`:'No suggestions: drag a box around the thing.'}
const lblAt=e=>{const b=$('lblov').getBoundingClientRect();return [Math.min(1,Math.max(0,(e.clientX-b.left)/b.width)),Math.min(1,Math.max(0,(e.clientY-b.top)/b.height)),e.clientX,e.clientY]};
$('lblov').addEventListener('pointerdown',e=>{if(e.button)return;e.preventDefault();$('lblov').setPointerCapture(e.pointerId);LBL.drag={a:lblAt(e),box:null}});
$('lblov').addEventListener('pointermove',e=>{const d=LBL.drag;if(!d)return;const p=lblAt(e);if(!d.box&&Math.hypot(p[2]-d.a[2],p[3]-d.a[3])<6)return;
 d.box=[Math.min(d.a[0],p[0]),Math.min(d.a[1],p[1]),Math.max(d.a[0],p[0]),Math.max(d.a[1],p[1])];lblDraw()});
$('lblov').addEventListener('pointerup',e=>{const d=LBL.drag;if(!d)return;LBL.drag=null;
 if(d.box){if(d.box[2]-d.box[0]>0.02&&d.box[3]-d.box[1]>0.02)LBL.sel={i:null,box:d.box}}
 else{const [x,y]=d.a;let best=null;LBL.boxes.forEach((b,i)=>{const q=b.box,ar=(q[2]-q[0])*(q[3]-q[1]);if(x>=q[0]&&x<=q[2]&&y>=q[1]&&y<=q[3]&&(!best||ar<best.ar))best={i,ar}});
  if(best){const b=LBL.boxes[best.i];LBL.sel={i:best.i,box:b.box};const l=String(b.label||'').toLowerCase();
   const o=LBLLABELS.find(x=>x===l)||LBLLABELS.find(x=>x.split(' ').includes(l)||l.includes(x))||'other';$('lbllabel').value=o}}
 lblDraw()});
$('lblov').addEventListener('pointercancel',()=>{LBL.drag=null;lblDraw()});
$('lblname').addEventListener('input',e=>{const v=e.target.value.trim();clearTimeout(LBL.nt);LBL.nt=setTimeout(()=>lblExamples(v),400)});
$('lblname').addEventListener('focus',()=>{const ns=new Set([...OBJS.map(o=>o.name).filter(Boolean),...Object.keys(PLACES)]);$('lblnames').innerHTML=[...ns].sort().map(n=>`<option value="${esc(n)}">`).join('')});
async function lblExamples(name){if(!name){$('lblexwrap').hidden=true;return}let j;try{j=await (await fetch('/label/examples?name='+encodeURIComponent(name))).json()}catch(e){return}
 if($('lblname').value.trim()!==name)return;const ex=j.examples||[];$('lblexwrap').hidden=false;
 $('lblexnote').textContent=ex.length?`${name}: ${ex.length} example photo${ex.length>1?'s':''}`:`${name}: no examples yet`;
 $('lblexs').innerHTML=ex.map(x=>`<figure><div class="exw"><img src="${esc(x.url)}" alt="example photo" loading="lazy">${boxDiv(x.box,'')}</div><figcaption><span>${x.t?clock(x.t):''} · ${esc(x.label||'')}</span><button type="button" data-rm="${esc(x.id)}" title="Remove this example">remove</button></figcaption></figure>`).join('');
 $('lblexs').querySelectorAll('[data-rm]').forEach(b=>b.onclick=async()=>{b.disabled=true;try{await fetch('/label/remove',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:b.dataset.rm,client:'console '+CLIENT})})}catch(e){}
  lblExamples(name);lblShowObj(name)})}
async function lblShowObj(name){const cb=document.querySelector('[data-layer=objects]');if(!cb.checked){cb.checked=true;cb.dispatchEvent(new Event('change'))}
 await loadObjects();const o=OBJS.find(o=>o.id==='named_'+name);if(o){showObj(o);plotMap(lastMap,lastPose)}}
$('lblform').addEventListener('submit',async e=>{e.preventDefault();const name=$('lblname').value.trim();
 if(!LBL.frame||!LBL.sel){$('lblmsg').innerHTML='<span class="err">Pick a suggested box or drag one around the thing first.</span>';return}
 $('lblmsg').textContent='Adding…';let r,j={};
 try{r=await fetch('/label/example',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:LBL.frame,box:LBL.sel.box.map(v=>+v.toFixed(4)),name,label:$('lbllabel').value,place:$('lblplace').checked,client:'console '+CLIENT})});j=await r.json().catch(()=>({}))}
 catch(err){$('lblmsg').innerHTML='<span class="err">failed: is the console running?</span>';return}
 if(!r.ok){$('lblmsg').innerHTML=`<span class="err">${esc(j.reason||('failed '+r.status))}</span>`;return}
 const est=j.estimate;$('lblmsg').textContent=est?`${name}: ${est.examples} photo${est.examples>1?'s':''}, placed by ${est.how} at (${est.centre[0].toFixed(2)}, ${est.centre[1].toFixed(2)})${j.place?' · saved as a place':''}`
  :`${name}: example saved; could not place it yet (add a photo from another spot)`;
 LBL.sel=null;lblDraw();lblExamples(name);lblShowObj(name);if(j.place)loadPlaces()});
$('dropform').addEventListener('submit',async e=>{e.preventDefault();if(!DROP)return;const v=DROP.view;
 const id=$('dropid').value.trim();
 if(PLACES[id]&&!confirm(`A place called ${id} already exists. Replace it?`))return;
 // the place: the thing is at the dot; the dog stands where it took the view, facing the dot
 const stand=v?{x:v.x,y:v.y,yaw_deg:Math.hypot(DROP.x-v.x,DROP.y-v.y)>0.3?Math.atan2(DROP.y-v.y,DROP.x-v.x)*180/Math.PI:v.yaw_deg}:null;
 const body={id,description:$('droppdesc').value,client:'console '+CLIENT,target:{x:DROP.x,y:DROP.y},stand,view:v?v.url:null};
 const r=await fetch('/places',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 const j=await r.json().catch(()=>({}));
 if(!r.ok){$('dropmsg').innerHTML=`<span class="err">${esc(j.reason||r.status)}</span>`;return}
 $('dropid').value=$('droppdesc').value='';DROP=null;$('drop').hidden=true;await loadPlaces();plotMap(lastMap,lastPose);
 $('plnote').textContent=`saved ${id}`});
document.querySelectorAll('[data-map]').forEach(b=>b.addEventListener('click',async()=>{
 const ask={new:'Replace the map? Click again',clear:'Erase the map on screen? Click again',revert:'Drop unsaved changes? Click again'}[b.dataset.map];
 if(ask&&!b.dataset.sure){const t=b.textContent;b.dataset.sure=1;b.textContent=ask;setTimeout(()=>{delete b.dataset.sure;b.textContent=t},4000);return}
 if(b.dataset.sure){delete b.dataset.sure;b.textContent={new:'Start new map',clear:'Clear map',revert:'Back to saved map'}[b.dataset.map]}
 const r=await fetch('/map',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:b.dataset.map})});
 const j=await r.json().catch(()=>({}));$('mapstatus').textContent=r.ok?(j.status||'done'):(j.reason||('failed '+r.status))}));
</script></body></html>"""


def auto_rec_signals():
    """What AutoRecorder.tick needs from the live console."""
    now = time.time()
    with lock:
        st, odom, state = latest["stamps"], latest["odom"], latest["state"]
        sig = {"state_age": now - st.get("state", 0.0), "camera_age": now - st.get("camera", 0.0),
               "vel": odom["vel"] if odom and now - st.get("odom", 0.0) < 2.0 else None,
               "body_height": state["body_height"] if state and now - st.get("state", 0.0) < 2.0 else None}
    sig["cmd_age"] = time.monotonic() - NODE.last_cmd
    sig["l515_live"] = L515.st["online"]
    try:
        sig["free_gb"] = REC.free_gb()
    except OSError:
        sig["free_gb"] = None
    return sig


def auto_rec_loop():
    while True:
        time.sleep(1.0)
        try:
            AUTO.tick(time.time(), auto_rec_signals(), snapshot)
        except Exception as e:      # never let the recorder take the console down
            print(f"[autorec] tick failed: {e!r}", flush=True)


def main():
    rclpy.init()
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))  # rclpy otherwise swallows SIGTERM
    atexit.register(stop_at_exit, "console exiting")
    global NODE
    node = NODE = Collector()
    global AG, MAPPER, TRAIL, MARKERS, EXAMPLES, HIST
    AG = Agents(node, latest, lock, full)
    MAPPER = Mapper("/maps", os.environ.get("MAP_NAME", "lab"))
    TRAIL = Trail("/maps", os.environ.get("MAP_NAME", "lab"))
    global KEEPOUT
    KEEPOUT = go2_patrol.Keepout("/maps", os.environ.get("MAP_NAME", "lab"))
    MARKERS = Markers(full, lock)
    global PATROLS

    def motors():
        with lock:
            return latest["motors"], time.time() - latest["stamps"].get("motors", 0)
    PATROLS = go2_patrol.Patrols(AG, KEEPOUT, "/maps", os.environ.get("MAP_NAME", "lab"), {
        "battery": battery, "motors": motors, "deploying": lambda: DEPLOYING, "presets": lambda: SPEEDS,
        "markers": lambda: MARKERS.snapshot() if MARKERS else None})
    global MARKER_TABLE
    MARKER_TABLE = MarkerTable("/maps", os.environ.get("MAP_NAME", "lab"), log=lambda m: print(m, flush=True))
    EXAMPLES = Examples("/maps", os.environ.get("MAP_NAME", "lab"), MAPPER, TRAIL)
    AG.mapper, AG.planner = MAPPER, Planner(MAPPER)
    AG.tag_lineup = tag_lineup_for_agent
    AG.planner.fail_log = os.path.join("/maps", f"{os.environ.get('MAP_NAME', 'lab')}_nav_failures.jsonl")
    PATROLS.start_monitor()
    threading.Thread(target=rclpy.spin, args=(node,), daemon=True).start()
    L515.start()
    AUTO.recover()
    threading.Thread(target=auto_rec_loop, daemon=True).start()
    HIST = History("/maps", os.environ.get("MAP_NAME", "lab"), sample_from(latest, lock, MAPPER, AG, MARKERS, battery))
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    srv.daemon_threads = True
    print(f"Go2 dashboard on http://0.0.0.0:{PORT}  (Ctrl+C to stop)", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_at_exit("console shutting down")     # first: the dog keeps its last velocity otherwise
        AUTO.shutdown()
        REC.stop()
        MAPPER.autosave(latest["odom"])
        MAPPER.save_session(latest["odom"])
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
