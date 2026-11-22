#!/usr/bin/env python3
"""Minimal keyboard control for the Go2 via go2_robot_sdk.

Run inside the driver container:  python3 /root/go2_keys.py
Movement keys must be held (key repeat); releasing them stops the dog.
"""
import select
import sys
import termios
import time
import tty

import rclpy
from geometry_msgs.msg import Twist
from go2_interfaces.msg import WebRtcReq

SPORT_TOPIC = "rt/api/sport/request"
CMD = {"StopMove": 1003, "StandUp": 1004, "StandDown": 1005, "BalanceStand": 1002,
       "Sit": 1009, "RiseSit": 1010, "Hello": 1016}

# The console's speed caps, so the keyboard can't drive faster than the console (Oliver, 11-21: keys reversed at up
# to 0.38 m/s while the console caps reverse at 0.25). Keep in step with go2_dashboard.SPEEDS / LIMITS / BACK_MAX.
SPEEDS = {"slow": (0.3, 0.2, 0.5), "normal": (0.5, 0.25, 0.8), "fast": (0.6, 0.3, 1.0)}   # m/s, m/s, rad/s
BACK_MAX = 0.25                        # m/s backwards for everyone: the dog barely sees behind itself
SPEED_FILE = "/maps/console_speed.txt"  # the preset chosen on the console page
DEADMAN_S = 0.3                        # stop if no movement key for this long


def speeds():
    """(forward, strafe, turn) caps for the console's current preset; normal if unknown."""
    try:
        name = open(SPEED_FILE).read().strip()
    except OSError:
        name = "normal"
    return name if name in SPEEDS else "normal", SPEEDS.get(name, SPEEDS["normal"])


def move_for(key):
    name, (lin, strafe, turn) = speeds()
    return name, {"w": (lin, 0.0, 0.0), "s": (-min(lin, BACK_MAX), 0.0, 0.0),
                  "a": (0.0, strafe, 0.0), "d": (0.0, -strafe, 0.0),
                  "q": (0.0, 0.0, turn), "e": (0.0, 0.0, -turn)}[key]


MOVES = "wsadqe"
ACTIONS = {
    "u": ("stand up", ["StandUp", "BalanceStand"]),
    "j": ("lie down", ["StandDown"]),
    "t": ("sit", ["Sit"]),
    "r": ("rise from sit", ["RiseSit"]),
    "h": ("wave hello", ["Hello"]),
}
HELP = """
Go2 keyboard control
  hold w/s   forward / back        hold a/d   strafe left / right
  hold q/e   turn left / right     space      stop
  u stand up   j lie down   t sit   r rise from sit   h hello
  x quit (stops the dog first)
"""


def main():
    rclpy.init()
    node = rclpy.create_node("go2_keys")
    vel_pub = node.create_publisher(Twist, "cmd_vel_out", 10)
    req_pub = node.create_publisher(WebRtcReq, "webrtc_req", 10)

    def send(name):
        msg = WebRtcReq()
        msg.api_id = CMD[name]
        msg.topic = SPORT_TOPIC
        msg.parameter = ""
        msg.priority = 1 if name == "StopMove" else 0
        req_pub.publish(msg)

    def say(text):
        sys.stdout.write("\r\033[K" + text)
        sys.stdout.flush()

    old = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    print(HELP)
    moving, last_move = False, 0.0
    try:
        while True:
            ready, _, _ = select.select([sys.stdin], [], [], 0.05)
            key = sys.stdin.read(1).lower() if ready else None

            if key and key in MOVES:
                preset, (x, y, z) = move_for(key)
                t = Twist()
                t.linear.x, t.linear.y, t.angular.z = x, y, z
                vel_pub.publish(t)
                moving, last_move = True, time.monotonic()
                say(f"moving  x={x:+.2f} y={y:+.2f} turn={z:+.1f}  ({preset} preset)")
            elif key == " ":
                send("StopMove")
                moving = False
                say("stop")
            elif key in ACTIONS:
                label, cmds = ACTIONS[key]
                send("StopMove")
                for c in cmds:
                    send(c)
                    time.sleep(0.2)
                moving = False
                say(label)
            elif key == "x":
                send("StopMove")
                say("stopped, quitting\n")
                time.sleep(0.3)
                break

            if moving and time.monotonic() - last_move > DEADMAN_S:
                send("StopMove")
                moving = False
                say("released: stop")
            rclpy.spin_once(node, timeout_sec=0)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)
        send("StopMove")
        time.sleep(0.2)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
