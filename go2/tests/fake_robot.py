"""A stand-in for the dog and Nav2, to test record_positions and patrol without the robot.

Serves navigate_to_pose (walks 1 s, then 'arrives' 5 cm short; a goal at x == 99 is aborted, to
test failure handling), publishes map->base_link at the current pose, a numbered camera picture
at 10 Hz, an IMU message, and logs every /webrtc_req it receives to /data/fake_webrtc.jsonl.
"""
import json
import math
import time

import numpy as np
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import TransformStamped
from go2_interfaces.msg import IMU, WebRtcReq
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import Image
from tf2_ros import TransformBroadcaster


class FakeRobot(Node):
    def __init__(self):
        super().__init__("fake_robot")
        self.x, self.y, self.yaw = 0.0, 0.0, 0.0
        self.n = 0
        self.bridge = CvBridge()
        self.tf = TransformBroadcaster(self)
        self.cam = self.create_publisher(Image, "/camera/image_raw", 10)
        self.imu = self.create_publisher(IMU, "imu", 10)
        self.create_subscription(WebRtcReq, "webrtc_req", self._on_req, 10)
        ActionServer(self, NavigateToPose, "navigate_to_pose", self._navigate, callback_group=ReentrantCallbackGroup())
        self.create_timer(0.1, self._tick)

    def _on_req(self, m):
        with open("/data/fake_webrtc.jsonl", "a") as f:
            f.write(json.dumps({"api_id": m.api_id, "topic": m.topic, "parameter": m.parameter}) + "\n")

    def _tick(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id, t.child_frame_id = "map", "base_link"
        t.transform.translation.x, t.transform.translation.y = self.x, self.y
        t.transform.rotation.z, t.transform.rotation.w = math.sin(self.yaw / 2), math.cos(self.yaw / 2)
        self.tf.sendTransform(t)
        self.n += 1
        img = np.full((720, 1280, 3), (self.n * 7) % 255, np.uint8)
        self.cam.publish(self.bridge.cv2_to_imgmsg(img, encoding="bgr8"))
        m = IMU()
        m.rpy = [0.0, -0.2, self.yaw]
        self.imu.publish(m)

    def _navigate(self, handle):
        p = handle.request.pose.pose
        time.sleep(1.0)
        if abs(p.position.x - 99.0) < 1e-6:
            handle.abort()
            return NavigateToPose.Result()
        self.x, self.y = p.position.x - 0.05, p.position.y
        self.yaw = 2 * math.atan2(p.orientation.z, p.orientation.w)
        handle.succeed()
        return NavigateToPose.Result()


def main():
    rclpy.init()
    ex = MultiThreadedExecutor()
    ex.add_node(FakeRobot())
    ex.spin()


if __name__ == "__main__":
    main()
