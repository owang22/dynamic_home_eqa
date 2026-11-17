"""Container side: per sighting, lidar points (dog frame at the camera frame time) near the detection."""
import json, math, sys, bisect, collections
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from nav_msgs.msg import Odometry
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
S = json.load(open("/snap/sightings.json"))
by = collections.defaultdict(list)
for i, s in enumerate(S): by[s["session"]].append(i)
WIN, CAM, R = 2.0, 0.30, 0.6
res = {}
for sess, idx in by.items():
    r = rosbag2_py.SequentialCompressionReader()
    r.open(rosbag2_py.StorageOptions(uri=f"/rec/{sess}/bag", storage_id="sqlite3"), rosbag2_py.ConverterOptions("cdr", "cdr"))
    r.set_filter(rosbag2_py.StorageFilter(topics=["/odom", "/point_cloud2"]))
    fts = sorted(S[i]["frame_t"] for i in idx)
    od, clouds = [], []
    while r.has_next():
        topic, data, t = r.read_next(); t = t / 1e9
        if topic == "/odom":
            m = deserialize_message(data, Odometry); p, o = m.pose.pose.position, m.pose.pose.orientation
            od.append((t, p.x, p.y, p.z, math.atan2(2 * (o.w * o.z + o.x * o.y), 1 - 2 * (o.y * o.y + o.z * o.z))))
        else:
            k = bisect.bisect_left(fts, t)          # a sighting within [t, t + WIN]?
            if k < len(fts) and fts[k] - t <= WIN:
                m = deserialize_message(data, PointCloud2)
                clouds.append((t, point_cloud2.read_points_numpy(m, field_names=("x", "y", "z"), skip_nans=True).astype(np.float32)))
    ot = [o[0] for o in od]
    def pose_at(t):
        k = min(max(bisect.bisect_left(ot, t), 1), len(ot) - 1); a, b = od[k - 1], od[k]
        w = 0 if b[0] == a[0] else min(1, max(0, (t - a[0]) / (b[0] - a[0])))
        yaw = a[4] + w * ((b[4] - a[4] + math.pi) % (2 * math.pi) - math.pi)
        return a[1] + w * (b[1] - a[1]), a[2] + w * (b[2] - a[2]), a[3] + w * (b[3] - a[3]), yaw
    ct = [c[0] for c in clouds]
    for i in idx:
        s = S[i]; ft = s["frame_t"]; m = s["m"]
        x0, y0, z0, yaw = pose_at(ft)
        lo, hi = bisect.bisect_left(ct, ft - WIN), bisect.bisect_right(ct, ft + 0.05)
        if hi <= lo: continue
        pts = np.concatenate([clouds[k][1] for k in range(lo, hi)])
        c, sn = math.cos(yaw), math.sin(yaw)
        dx, dy = pts[:, 0] - x0, pts[:, 1] - y0
        d = np.c_[c * dx + sn * dy, -sn * dx + c * dy, pts[:, 2] - z0]       # dog frame (x fwd, y left, z up from base)
        tx, ty = CAM + m["z"], -m["x"]
        near = d[np.hypot(d[:, 0] - tx, d[:, 1] - ty) < R]
        res[f"p{i}"] = near.astype(np.float32); res[f"m{i}"] = np.array([hi - lo, z0], np.float32)
    print(sess, len(idx), "sightings,", len(clouds), "clouds kept", flush=True)
np.savez_compressed("/snap/points.npz", **res)
