#!/usr/bin/env bash
# Make the Go2 driver (in container go2_test) publish the 12 leg motor temperatures, which it otherwise drops.
# The dog's low state (rt/lf/lowstate) carries motor_state[i].temperature (and lost, reserve), but the driver only
# republishes the joint angles. This patch publishes, from the same message, at most 4 times a second:
#   /go2/motor_temps  std_msgs/String, JSON:
#     {"t", "order": [FL_hip, FL_thigh, FL_calf, FR_..., RL_..., RR_...],   (the /joint_states order)
#      "temps": [12 x degC], "lost": [12], "reserve": [12 x [..]], "keys": fields seen in motor_state[0]}
# and keeps the first raw motor_state entry in /tmp/go2_motor_fields.json (to see which fields the dog fills).
# The console (go2_dashboard.py) shows them and warns when hot; auto recording saves the topic.
# The patch edits the driver inside the container, like patch_driver_battery.sh: it survives `docker restart`,
# but not `docker rm` / recreating the container. After a recreate, run this script again, then restart the driver.
#   ./patch_driver_motor_temps.sh            apply (safe to run twice; keeps the original as *.motors.orig)
#   ./patch_driver_motor_temps.sh --undo     remove it again (leaves the battery patch alone)
# Apply only while the dog is off or idle: the driver must be restarted afterwards (docker restart go2_test, which
# also stops the L515 receiver and the console; bring them back with ~/oliver/deploy_console.sh and go2_wake.sh).
set -euo pipefail
C=${GO2_CONTAINER:-go2_test}
F=/ros2_ws/install/go2_robot_sdk/lib/python3.10/site-packages/go2_robot_sdk/application/services/robot_data_service.py
if [ "${1:-}" = "--undo" ]; then
    docker exec -i $C python3 - "$F" <<'EOF'
import re, sys
p = sys.argv[1]
s = open(p).read()
if "_publish_motors" not in s:
    print("not patched"); sys.exit()
s = s.replace("            _publish_motors(low_state_data)   # go2 console patch: motor temperatures\n", "")
i, j = s.find("\n\n# go2 console patch (motor temps)"), s.find("# end go2 console patch (motor temps)\n")
if i >= 0 and j > i:          # the block was appended verbatim: removing exactly it restores the file
    s = s[:i] + s[j + len("# end go2 console patch (motor temps)\n"):]
open(p, "w").write(s)
print("motor temperature patch removed")
EOF
    docker exec $C python3 -m py_compile "$F" && echo "compiles; restart the driver to take effect"
    exit 0
fi
docker exec $C bash -c "test -f $F.motors.orig || cp $F $F.motors.orig"
docker exec -i $C python3 - "$F" <<'EOF'
import sys
p = sys.argv[1]
s = open(p).read()
if "_publish_motors" in s:
    print("already patched"); sys.exit()
a = "            low_state_data = msg['data']\n"
assert s.count(a) == 1, "driver code changed; patch not applied"
# after the battery patch line if present, else right after the data line
b = "            _save_battery(low_state_data)   # go2 console patch: battery to /tmp/go2_battery.json\n"
anchor = a + b if (a + b) in s else a
s = s.replace(anchor, anchor + "            _publish_motors(low_state_data)   # go2 console patch: motor temperatures\n")
s = s + '''

# go2 console patch (motor temps): the dog's 12 leg motor temperatures on /go2/motor_temps (std_msgs/String, JSON),
# at most 4 Hz, in the /joint_states order. The dog's motor_state order is FR, FL, RR, RL (hip, thigh, calf).
import json as _mjson, time as _mtime
_MOT = {"t": 0.0, "pub": None, "dumped": False}
_MOT_ORDER = [3, 4, 5, 0, 1, 2, 9, 10, 11, 6, 7, 8]
_MOT_NAMES = [f"{l}_{j}" for l in ("FL", "FR", "RL", "RR") for j in ("hip", "thigh", "calf")]
_MOT_JOINT = ("q", "dq", "ddq", "tau_est", "q_raw", "dq_raw", "ddq_raw", "tau")


def _publish_motors(d):
    now = _mtime.time()
    if now - _MOT["t"] < 0.25:
        return
    _MOT["t"] = now
    try:
        ms = d.get("motor_state") or []
        if len(ms) < 12:
            return
        if not _MOT["dumped"]:
            _MOT["dumped"] = True
            with open("/tmp/go2_motor_fields.json", "w") as f:
                _mjson.dump({"t": round(now, 2), "motor_state_0": ms[0], "n": len(ms)}, f)
        if _MOT["pub"] is None:
            import rclpy
            from std_msgs.msg import String
            if not rclpy.ok():
                return
            _MOT["node"] = rclpy.create_node("go2_motor_temps")
            _MOT["pub"] = _MOT["node"].create_publisher(String, "/go2/motor_temps", 10)
            _MOT["String"] = String
        m = [ms[i] for i in _MOT_ORDER]
        out = {"t": round(now, 3), "order": _MOT_NAMES,
               "temps": [x.get("temperature") for x in m], "lost": [x.get("lost") for x in m],
               "reserve": [x.get("reserve") for x in m],
               "keys": sorted(k for k in ms[0] if k not in _MOT_JOINT)}
        msg = _MOT["String"]()
        msg.data = _mjson.dumps(out)
        _MOT["pub"].publish(msg)
    except Exception:
        pass
# end go2 console patch (motor temps)
'''
open(p, "w").write(s)
print("patched")
EOF
docker exec $C python3 -m py_compile "$F" && echo "compiles; now restart the driver (only while the dog is off or idle)"
