"""Closed-loop 30 deg turns at the console's max rate (0.6 rad/s), avoidance on; measures start delay and overshoot."""
import math, sys, time, threading
sys.argv.append("--check-only")  # motion_test only supplies helpers here
import motion_test as m
threading.Thread(target=m.reader, daemon=True).start()
while not m.last["ev"]: time.sleep(0.1)
print("avoid", m.cmd({"avoid": True}))
def turn(deg, wz=0.6, limit=5.0):
    time.sleep(1.5)
    y0 = m.pose()["odom"][2]; t0 = time.monotonic(); first = None
    try:
        while True:
            d = math.degrees(m.wrap(m.pose()["odom"][2] - y0))
            if first is None and abs(d) > 2: first = time.monotonic() - t0
            if abs(d) >= abs(deg) - 3: why = "reached"; break
            if time.monotonic() - t0 > limit: why = "time limit"; break
            m.cmd({"move": [0.0, 0.0, math.copysign(wz, deg)]}); time.sleep(0.1)
    finally:
        m.cmd({"action": "stop"})
    at_stop = math.degrees(m.wrap(m.pose()["odom"][2] - y0)); t_stop = time.monotonic() - t0
    time.sleep(1.5)
    final = math.degrees(m.wrap(m.pose()["odom"][2] - y0))
    print(f"asked {deg:+.0f}: {why}, started moving after {first if first is None else round(first,1)} s, "
          f"{at_stop:+.1f} at stop ({t_stop:.1f} s), {final:+.1f} settled")
turn(30); turn(-30); turn(30); turn(-30)
