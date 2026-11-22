"""Fakes for offline step-3 tests: a simulated dog (odom/imu/state/camera), a fake ROS node that records every
command (and the thread that sent it), fake L515 messages. Nothing here touches ROS or the real dog."""
import io, json, math, os, shutil, sys, tempfile, threading, time, types
sys.path.insert(0, "/tmp/s3test")
import numpy as np, cv2
import go2_agent, go2_patrol
from go2_agent import Agents
from go2_mapper import Mapper
from go2_nav import Planner

START = (0.53, -0.21, math.radians(41))


class FakeNode:
    def __init__(self, sim):
        self.sim, self.avoid, self.head, self.moving = sim, False, 0.0, False
        self.last_move = self.last_cmd = 0.0
        self.calls = []

    def _rec(self, *c):
        self.calls.append((threading.current_thread().name, time.monotonic()) + c)

    def move(self, x, y, z):
        self._rec("move", round(x, 3), round(y, 3), round(z, 3))
        self.sim.cmd = (x, y, z, time.monotonic())
        self.moving, self.last_move = True, time.monotonic()
        if self.head and (x or z):
            self.head = 0.0

    def stop(self):
        self._rec("stop")
        self.sim.cmd = (0.0, 0.0, 0.0, time.monotonic())
        self.moving = False

    def action(self, name):
        self._rec("action", name)
        self.head = 0.0
        self.sim.body_h = 0.07 if name == "lie" else 0.30

    def look(self, rad):
        self._rec("look", round(rad, 3))
        self.head = rad

    def send_head(self):
        self._rec("send_head", round(self.head, 3))


class Sim:
    """A dog that does what it is told: integrates commanded velocity at 50 Hz (stops 0.3 s after the last move)."""

    def __init__(self, latest, lock, full):
        self.latest, self.lock, self.full = latest, lock, full
        self.x, self.y, self.yaw = START
        self.cmd = (0.0, 0.0, 0.0, 0.0)
        self.body_h, self.roll, self.pitch_extra = 0.30, 0.0, 0.0
        self.look_holds = True
        self.node = None
        self.cam_on = True
        self.run = True
        self.img = np.random.default_rng(0).integers(0, 255, (720, 1280, 3), dtype=np.uint8)
        threading.Thread(target=self.loop, daemon=True, name="sim").start()

    def loop(self):
        t_prev, n = time.monotonic(), 0
        while self.run:
            time.sleep(0.02)
            now = time.monotonic(); dt = now - t_prev; t_prev = now
            vx, vy, wz, tc = self.cmd
            if now - tc > 0.3:
                vx = vy = wz = 0.0
            self.x += math.cos(self.yaw) * vx * dt
            self.y += math.sin(self.yaw) * vx * dt
            self.yaw = (self.yaw + wz * dt + math.pi) % (2 * math.pi) - math.pi
            head = self.node.head if self.node and self.look_holds else 0.0
            wall = time.time()
            with self.lock:
                self.latest["odom"] = {"pos": [self.x, self.y, 0.0], "yaw": self.yaw, "vel": [vx, vy, wz], "frame": "odom"}
                self.latest["imu"] = {"rpy": [self.roll, -head + self.pitch_extra, self.yaw], "gyro": [0, 0, wz], "acc": [0, 0, 9.8], "temp": 30}
                self.latest["state"] = {"mode": 1, "gait": 1, "body_height": self.body_h, "foot_raise": 0.08,
                                        "velocity": [vx, vy, 0], "obstacle": [0, 0, 0, 0], "foot_force": [0, 0, 0, 0]}
                for k in ("odom", "imu", "state"):
                    self.latest["stamps"][k] = wall
                n += 1
                if self.cam_on and n % 5 == 0:
                    self.full["img"], self.full["t"] = self.img, wall


def ros_time(t):
    return types.SimpleNamespace(sec=int(t), nanosec=int((t % 1) * 1e9))


def fake_l515(patrols, t=None):
    """One L515 frame set as the receiver publishes it (fake message objects, no ROS)."""
    t = t or time.time()
    st = ros_time(t)
    depth = (np.arange(240 * 320, dtype=np.uint16).reshape(240, 320) % 4000).astype("<u2")
    dm = types.SimpleNamespace(header=types.SimpleNamespace(stamp=st, frame_id="l515_depth"), height=240, width=320,
                               step=640, is_bigendian=0, encoding="16UC1", data=depth.tobytes())
    ok, jpg = cv2.imencode(".jpg", np.full((360, 640, 3), 120, np.uint8))
    cm = types.SimpleNamespace(header=types.SimpleNamespace(stamp=st, frame_id="l515_color"), format="jpeg", data=jpg.tobytes())

    def info(fid, w, h):
        return types.SimpleNamespace(header=types.SimpleNamespace(stamp=st, frame_id=fid), width=w, height=h,
                                     distortion_model="plumb_bob", d=[0.0] * 5, k=[300.0, 0, w / 2, 0, 300.0, h / 2, 0, 0, 1],
                                     r=[1.0, 0, 0, 0, 1, 0, 0, 0, 1], p=[300.0, 0, w / 2, 0, 0, 300.0, h / 2, 0, 0, 0, 1, 0])
    patrols.l515.on("depth", dm); patrols.l515.on("color", cm)
    patrols.l515.on("depth_info", info("l515_depth", 320, 240)); patrols.l515.on("color_info", info("l515_color", 640, 360))
    return depth


class World:
    """Agents (real) + Mapper/Planner (real, temp copy of the saved map) + Patrols (real) on a simulated dog."""

    def __init__(self, monitor=True):
        self.tmp = tempfile.mkdtemp(prefix="s3w_")
        shutil.copy("/maps/lab.grid.npz", self.tmp)
        self.latest = {"motors": None, "imu": None, "odom": None, "state": None, "joints": None, "cloud": None,
                       "map": None, "map_pose": None, "stamps": {}}
        self.lock = threading.Lock()
        self.full = {"img": None, "t": 0.0}
        self.sim = Sim(self.latest, self.lock, self.full)
        self.node = FakeNode(self.sim); self.sim.node = self.node
        self.ag = Agents(self.node, self.latest, self.lock, self.full)
        self.mapper = Mapper(self.tmp, "lab")
        self.mapper.T = (0.0, 0.0, 0.0)          # odom == map for the test
        self.ag.mapper, self.ag.planner = self.mapper, Planner(self.mapper)
        self.keepout = go2_patrol.Keepout(self.tmp, "lab")
        self.batt = {"soc": 80, "age_s": 1.0}
        self.mot = {"max": 40, "hottest": "RR_hip", "level": "ok", "warn_c": 60, "hot_c": 70}
        self.mot_age = 1.0
        self.deploying = None
        self.markers = {"frame_t": None, "list": []}
        self.pt = go2_patrol.Patrols(self.ag, self.keepout, self.tmp, "lab", {
            "battery": lambda: self.batt, "motors": lambda: (self.mot, self.mot_age),
            "deploying": lambda: self.deploying, "presets": lambda: {"slow": (0.3, 0.2, 0.5), "normal": (0.5, 0.25, 0.8)},
            "markers": lambda: dict(self.markers, frame_t=self.full["t"]) if self.markers.get("list") else self.markers})
        time.sleep(0.3)
        if monitor:
            self.pt.start_monitor()

    def claim(self, client="cheetah-patrol"):
        return self.ag.agent_may_drive(client, "10.0.0.2")

    def monitor_calls(self):
        return [c for c in self.node.calls if c[0] == "patrol-monitor"]

    def close(self):
        self.sim.run = False
