"""One patrol: walk to every named position, photograph it, walk back to the dock.

    ros2 run go2_patrol patrol --ros-args -p positions_file:=/data/positions.yaml

Writes  <out_root>/<YYYY-MM-DD>/<HHMM>/<position_id>.jpg  and a patrol.json beside them. patrol.json
is rewritten after every position, so a patrol that stops halfway still says how far it got and why.
A position that cannot be reached or photographed is logged as failed, and the patrol moves on.
"""
from __future__ import annotations

import datetime
import json
import math
import time
from pathlib import Path

import rclpy
import rclpy.signals
from action_msgs.msg import GoalStatus
from cv_bridge import CvBridge
from geometry_msgs.msg import PoseStamped
from go2_interfaces.msg import IMU, WebRtcReq
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from tf2_ros import Buffer, TransformListener

from .common import (BALANCE_STAND, EULER, SPORT_TOPIC, load_positions, lookup_pose, now_iso, save_image,
                     write_json_atomic)

STATUS = {GoalStatus.STATUS_SUCCEEDED: "reached", GoalStatus.STATUS_ABORTED: "nav2 gave up",
          GoalStatus.STATUS_CANCELED: "canceled"}


class Patrol(Node):
    def __init__(self):
        super().__init__("go2_patrol")
        p = self.declare_parameter
        p("positions_file", "/data/positions.yaml")
        p("out_root", "/data/patrols")
        p("image_topic", "/camera/image_raw")
        p("map_frame", "map")
        p("base_frame", "base_link")
        p("settle_s", 2.0)          # stand still this long before the picture (no motion blur)
        p("nav_timeout_s", 120.0)   # per position
        p("tries", 2)               # navigation attempts per position
        p("dock_id", "dock")
        p("only", "")               # comma-separated ids: photograph just these (for testing)
        p("dry_run", False)         # navigate and log, but do not tilt the body
        g = lambda k: self.get_parameter(k).value  # noqa: E731
        self.cfg = {k: g(k) for k in ("positions_file", "out_root", "image_topic", "map_frame", "base_frame",
                                      "settle_s", "nav_timeout_s", "tries", "dock_id", "only", "dry_run")}
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.bridge = CvBridge()
        self.nav = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.webrtc = self.create_publisher(WebRtcReq, "webrtc_req", 10)
        self.last_image, self.last_image_t = None, 0.0
        self.last_rpy = None
        self.active_goal = None  # cancelled on Ctrl+C, or Nav2 would keep walking to it
        self.create_subscription(Image, self.cfg["image_topic"], self._on_image, qos_profile_sensor_data)
        self.create_subscription(IMU, "imu", lambda m: setattr(self, "last_rpy", list(m.rpy)), 10)

    def _on_image(self, msg):
        self.last_image, self.last_image_t = msg, time.monotonic()

    # --- helpers -------------------------------------------------------------------------------
    def spin_for(self, seconds: float):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            rclpy.spin_once(self, timeout_sec=0.05)

    def sport(self, api_id: int, parameter: dict | None = None):
        msg = WebRtcReq()
        msg.api_id, msg.topic, msg.priority = api_id, SPORT_TOPIC, 0
        msg.parameter = json.dumps(parameter) if parameter is not None else ""
        self.webrtc.publish(msg)

    def go_to(self, pos: dict) -> tuple[str, float]:
        goal = NavigateToPose.Goal()
        ps = PoseStamped()
        ps.header.frame_id = self.cfg["map_frame"]
        ps.header.stamp = self.get_clock().now().to_msg()
        ps.pose.position.x, ps.pose.position.y = float(pos["x"]), float(pos["y"])
        yaw = math.radians(float(pos.get("yaw_deg", 0.0)))
        ps.pose.orientation.z, ps.pose.orientation.w = math.sin(yaw / 2), math.cos(yaw / 2)
        goal.pose = ps
        t0 = time.monotonic()
        send = self.nav.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send, timeout_sec=10.0)
        handle = send.result() if send.done() else None
        if handle is None or not handle.accepted:
            return "goal refused by nav2", time.monotonic() - t0
        self.active_goal = handle
        result = handle.get_result_async()
        rclpy.spin_until_future_complete(self, result, timeout_sec=float(self.cfg["nav_timeout_s"]))
        self.active_goal = None
        if not result.done():
            cancel = handle.cancel_goal_async()
            rclpy.spin_until_future_complete(self, cancel, timeout_sec=5.0)
            return f"timed out after {self.cfg['nav_timeout_s']:.0f} s", time.monotonic() - t0
        return STATUS.get(result.result().status, f"status {result.result().status}"), time.monotonic() - t0

    def photograph(self, path: Path) -> dict:
        """Wait for a frame that arrived after the robot stopped, and save it."""
        settled_at = time.monotonic()
        self.spin_for(float(self.cfg["settle_s"]))
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline and (self.last_image is None or self.last_image_t <= settled_at):
            rclpy.spin_once(self, timeout_sec=0.05)
        if self.last_image is None or self.last_image_t <= settled_at:
            raise RuntimeError("no camera frame arrived within 5 s of stopping")
        w, h = save_image(self.bridge, self.last_image, path)
        return {"picture": path.name, "width": w, "height": h, "taken": now_iso(),
                "imu_rpy_deg": [round(math.degrees(a), 1) for a in self.last_rpy] if self.last_rpy else None}

    def visit(self, pos: dict, picture: Path) -> dict:
        """Walk to one position (with retries), tilt if asked, photograph it, level again.
        Returns the record patrol.json keeps for that position; result is 'photographed' or 'failed: ...'."""
        rec = {"id": pos["id"], "target": {k: pos.get(k) for k in ("x", "y", "yaw_deg", "pitch_deg")},
               "started": now_iso(), "attempts": []}
        outcome = None
        for _ in range(int(self.cfg["tries"])):
            outcome, secs = self.go_to(pos)
            rec["attempts"].append({"outcome": outcome, "seconds": round(secs, 1)})
            if outcome == "reached":
                break
        if outcome != "reached":
            rec["result"] = f"failed: {outcome}"
            self.get_logger().warn(f"{pos['id']}: {rec['result']}")
            return rec
        pitch = float(pos.get("pitch_deg", 0) or 0)
        pose = None
        try:
            if pitch and not self.cfg["dry_run"]:
                self.sport(BALANCE_STAND)
                self.spin_for(0.5)
                self.sport(EULER, {"x": 0.0, "y": -math.radians(pitch), "z": 0.0})  # negative pitch = nose up
                rec["pitch_commanded_deg"] = pitch
            rec.update(self.photograph(picture))
            # where it stood for the picture (on arrival the last position update can be stale)
            pose = lookup_pose(self.tf_buffer, self.cfg["map_frame"], self.cfg["base_frame"])
            rec["result"] = "photographed"
        except Exception as e:  # noqa: BLE001 - log it and carry on with the next position
            rec["result"] = f"failed: {e}"
        finally:
            if pitch and not self.cfg["dry_run"]:
                self.sport(EULER, {"x": 0.0, "y": 0.0, "z": 0.0})
                self.spin_for(0.8)
        if pose:
            x, y, yaw = pose
            rec["actual"] = {"x": round(x, 3), "y": round(y, 3), "yaw_deg": round(math.degrees(yaw), 1)}
            rec["off_by_m"] = round(math.hypot(x - pos["x"], y - pos["y"]), 3)
            rec["heading_off_deg"] = round((math.degrees(yaw) - pos.get("yaw_deg", 0) + 180) % 360 - 180, 1)
        self.get_logger().info(f"{pos['id']}: {rec['result']}"
                               + (f" ({rec['off_by_m']} m off)" if "off_by_m" in rec else ""))
        return rec

    def cancel_active_goal(self) -> str:
        if self.active_goal is None:
            return ""
        cancel = self.active_goal.cancel_goal_async()
        rclpy.spin_until_future_complete(self, cancel, timeout_sec=5.0)
        return "; walking goal cancelled" if cancel.done() else "; CANCEL NOT CONFIRMED"

    # --- the patrol ----------------------------------------------------------------------------
    def run(self) -> int:
        positions = load_positions(self.cfg["positions_file"])
        dock = next((p for p in positions if p["id"] == self.cfg["dock_id"]), None)
        todo = [p for p in positions if p["id"] != self.cfg["dock_id"]]
        if self.cfg["only"]:
            keep = {s.strip() for s in self.cfg["only"].split(",")}
            todo = [p for p in todo if p["id"] in keep]
        started = datetime.datetime.now().astimezone()
        out = Path(self.cfg["out_root"]) / started.strftime("%Y-%m-%d") / started.strftime("%H%M")
        out.mkdir(parents=True, exist_ok=True)
        log = {"started": started.isoformat(timespec="seconds"), "finished": None, "ended_because": None,
               "positions_file": str(self.cfg["positions_file"]), "settings": self.cfg,
               "camera": "built-in front camera", "positions": []}
        logf = out / "patrol.json"
        write_json_atomic(logf, log)
        self.get_logger().info(f"patrol of {len(todo)} positions -> {out}")

        if not self.nav.wait_for_server(timeout_sec=30.0):
            log["ended_because"] = "nav2 is not running (no navigate_to_pose server after 30 s)"
            log["finished"] = now_iso()
            write_json_atomic(logf, log)
            self.get_logger().error(log["ended_because"])
            return 2
        try:
            for pos in todo:
                rec = self.visit(pos, out / f"{pos['id']}.jpg")
                log["positions"].append(rec)
                write_json_atomic(logf, log)
            log["ended_because"] = "all positions tried"
        except KeyboardInterrupt:
            log["ended_because"] = "stopped by the operator (Ctrl+C)"
            log["ended_because"] += self.cancel_active_goal()
        if dock is not None and log["ended_because"] == "all positions tried":
            outcome, secs = self.go_to(dock)
            log["return_to_dock"] = {"outcome": outcome, "seconds": round(secs, 1)}
        log["finished"] = now_iso()
        done = sum(r.get("result") == "photographed" for r in log["positions"])
        log["summary"] = f"{done} of {len(todo)} photographed"
        write_json_atomic(logf, log)
        self.get_logger().info(f"{log['summary']}; log in {logf}")
        return 0 if done == len(todo) else 1


def main():
    # rclpy's own Ctrl+C handler shuts ROS down at once, leaving no way to cancel the walking goal
    rclpy.init(signal_handler_options=rclpy.signals.SignalHandlerOptions.NO)
    node = Patrol()
    try:
        code = node.run()
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
    raise SystemExit(code)


if __name__ == "__main__":
    main()
