"""Export body streams from auto-recording bags to CSV (unix t + local_time), full rate.
usage: export_body.py OUT_DIR SESSION_DIR...   (run in go2_test with ROS sourced)"""
import csv, datetime, math, os, shutil, sys
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

TOPICS = ["/go2_states", "/odom", "/imu", "/joint_states"]

def lt(t):
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def rpy(q):
    x, y, z, w = q
    r = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    p = math.asin(max(-1.0, min(1.0, 2 * (w * y - z * x))))
    yw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return r, p, yw

def rows(topic, m, t):
    if topic == "/go2_states":
        return ([t, lt(t), m.mode, m.progress, m.gait_type, m.body_height, m.foot_raise_height, *m.position, *m.velocity,
                 *m.range_obstacle, *m.foot_force])
    if topic == "/odom":
        p, o, tw = m.pose.pose.position, m.pose.pose.orientation, m.twist.twist
        return [t, lt(t), p.x, p.y, p.z, rpy((o.x, o.y, o.z, o.w))[2], tw.linear.x, tw.linear.y, tw.angular.z]
    if topic == "/imu":
        # go2_interfaces/IMU: rpy (rad, from the dog), accelerometer, gyroscope, temperature
        return [t, lt(t), *m.rpy, *m.accelerometer, *m.gyroscope, m.temperature]
    if topic == "/joint_states":
        return [t, lt(t), *m.position, *(m.velocity or [])]

HEAD = {
    "/go2_states": ["t", "local_time", "mode", "progress", "gait_type", "body_height", "foot_raise_height", "pos_x", "pos_y",
                    "pos_z", "vel_x", "vel_y", "vel_yaw", "range_front", "range_right", "range_rear", "range_left",
                    "foot_force_0", "foot_force_1", "foot_force_2", "foot_force_3"],
    "/odom": ["t", "local_time", "x", "y", "z", "yaw", "twist_vx", "twist_vy", "twist_wz"],
    "/imu": ["t", "local_time", "roll", "pitch", "yaw", "acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z", "temp_c"],
}

def export(sess, out):
    r = rosbag2_py.SequentialCompressionReader()   # auto bags: zstd per message
    r.open(rosbag2_py.StorageOptions(uri=os.path.join(sess, "bag"), storage_id="sqlite3"),
           rosbag2_py.ConverterOptions("cdr", "cdr"))
    types = {t.name: t.type for t in r.get_all_topics_and_types()}
    r.set_filter(rosbag2_py.StorageFilter(topics=[t for t in TOPICS if t in types]))
    cls = {t: get_message(types[t]) for t in TOPICS if t in types}
    od = os.path.join(out, os.path.basename(sess)); os.makedirs(od, exist_ok=True)
    fs, ws, n = {}, {}, {}
    while r.has_next():
        topic, data, ns = r.read_next()
        m = deserialize_message(data, cls[topic]); t = ns / 1e9
        if topic not in ws:
            fs[topic] = open(os.path.join(od, topic.strip("/") + ".csv"), "w", newline="")
            ws[topic] = csv.writer(fs[topic])
            h = HEAD.get(topic)
            if h is None:   # joint_states: names from the first message
                h = ["t", "local_time"] + [f"q_{j}" for j in m.name] + ([f"dq_{j}" for j in m.name] if m.velocity else [])
            ws[topic].writerow(h)
        ws[topic].writerow([f"{v:.6f}" if isinstance(v, float) else v for v in rows(topic, m, t)])
        n[topic] = n.get(topic, 0) + 1
    for f in fs.values(): f.close()
    ev = os.path.join(sess, "events.jsonl")
    if os.path.exists(ev): shutil.copy(ev, od)
    print(os.path.basename(sess), n, flush=True)

out = sys.argv[1]
for s in sys.argv[2:]:
    export(s, out)
