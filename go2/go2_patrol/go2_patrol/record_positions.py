"""Name the spots the patrol will photograph, by driving the dog to each one.

Drive the dog with the joystick or keyboard (see go2/README.md). At each spot, face what should be
photographed and type a name. The robot's position and heading in the map are saved to the
positions file, with a preview picture so the list can be checked later.

    ros2 run go2_patrol record_positions --ros-args -p positions_file:=/data/positions.yaml

Commands at the prompt:
    dock               record the start spot first (where the dog is switched on)
    bench_A            record the current spot under that name
    bench_A 15         ... and tilt the nose up 15 degrees for its picture
    list | undo | quit
"""
from __future__ import annotations

import math
import re
import sys
import threading
import time
from pathlib import Path

import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from tf2_ros import Buffer, TransformListener

from .common import load_positions, lookup_pose, now_iso, save_image, save_positions

NAME_RE = re.compile(r"^[A-Za-z0-9_\-]+$")


class Recorder(Node):
    def __init__(self):
        super().__init__("record_positions")
        self.declare_parameter("positions_file", "/data/positions.yaml")
        self.declare_parameter("map_frame", "map")
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("image_topic", "/camera/image_raw")
        self.path = Path(self.get_parameter("positions_file").value)
        self.map_frame = self.get_parameter("map_frame").value
        self.base_frame = self.get_parameter("base_frame").value
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.bridge = CvBridge()
        self.last_image = None
        self.create_subscription(Image, self.get_parameter("image_topic").value,
                                 self._on_image, qos_profile_sensor_data)
        self.positions = load_positions(self.path) if self.path.exists() else []

    def _on_image(self, msg):
        self.last_image = msg

    def record(self, name: str, pitch_deg: float) -> str:
        pose = None
        for _ in range(6):  # the transform can lag a moment after start-up or a map reload
            pose = lookup_pose(self.tf_buffer, self.map_frame, self.base_frame)
            if pose is not None:
                break
        if pose is None:
            return (f"no position: the {self.map_frame}->{self.base_frame} transform is missing. "
                    "Is the map loaded and the dog localised (RViz shows it on the map)?")
        x, y, yaw = pose
        entry = {"id": name, "x": round(x, 3), "y": round(y, 3), "yaw_deg": round(math.degrees(yaw), 1),
                 "pitch_deg": pitch_deg, "recorded": now_iso()}
        for _ in range(20):  # up to 2 s for the first camera frame
            if self.last_image is not None:
                break
            time.sleep(0.1)
        if self.last_image is not None:
            preview = self.path.parent / "position_previews" / f"{name}.jpg"
            save_image(self.bridge, self.last_image, preview)
            entry["preview"] = str(preview.relative_to(self.path.parent))
        replaced = any(p["id"] == name for p in self.positions)
        self.positions = [p for p in self.positions if p["id"] != name] + [entry]
        save_positions(self.path, self.positions)
        note = "" if self.last_image is not None else " (no camera picture yet, so no preview)"
        return f"{'replaced' if replaced else 'recorded'} {name}: x={x:.2f} y={y:.2f} heading={entry['yaw_deg']} deg{note}"


def prompt_loop(node: Recorder):
    print(__doc__.split("Commands at the prompt:")[1])
    if not any(p["id"] == "dock" for p in node.positions):
        print("No 'dock' yet: record the start spot first.\n")
    for line in sys.stdin:
        words = line.split()
        if not words:
            continue
        cmd = words[0]
        if cmd in ("quit", "exit", "q"):
            break
        if cmd == "list":
            for p in node.positions:
                print(f"  {p['id']:<20} x={p['x']:7.2f} y={p['y']:7.2f} heading={p['yaw_deg']:6.1f} pitch={p['pitch_deg']}")
            print(f"  {len(node.positions)} positions in {node.path}")
            continue
        if cmd == "undo":
            if node.positions:
                gone = node.positions.pop()
                save_positions(node.path, node.positions)
                print(f"removed {gone['id']}")
            continue
        if not NAME_RE.match(cmd):
            print("names use letters, digits, _ and - only")
            continue
        try:
            pitch = float(words[1]) if len(words) > 1 else 0.0
        except ValueError:
            print("the second word is the nose-up tilt in degrees, e.g. 'bench_A 15'")
            continue
        if not 0.0 <= pitch <= 25.0:
            print("tilt must be between 0 and 25 degrees")
            continue
        print(node.record(cmd, pitch))
    rclpy.shutdown()


def main():
    rclpy.init()
    node = Recorder()
    threading.Thread(target=prompt_loop, args=(node,), daemon=True).start()
    try:
        rclpy.spin(node)
    except Exception:  # noqa: BLE001 - shutdown from the prompt thread ends spin
        pass


if __name__ == "__main__":
    main()
