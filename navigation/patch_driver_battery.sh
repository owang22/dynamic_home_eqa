#!/usr/bin/env bash
# Make the Go2 driver (in container go2_test) save the dog's battery state for the console.
# The driver gets the battery in the dog's low state but publishes no battery topic; this patch writes the
# battery part (everything except motor_state) to /tmp/go2_battery.json inside the container, at most every 2 s.
# The console reads that file and shows the battery. Safe to run twice; keeps the original as *.orig.
#   ./patch_driver_battery.sh            apply, then restart the driver (./run_go2_keys.sh --reset)
#   ./patch_driver_battery.sh --undo     put the original back
set -euo pipefail
C=go2_test
F=/ros2_ws/install/go2_robot_sdk/lib/python3.10/site-packages/go2_robot_sdk/application/services/robot_data_service.py
if [ "${1:-}" = "--undo" ]; then
    docker exec $C bash -c "test -f $F.orig && cp $F.orig $F && echo restored"
    exit 0
fi
docker exec $C bash -c "test -f $F.orig || cp $F $F.orig"
docker exec -i $C python3 - "$F" <<'EOF'
import sys
p = sys.argv[1]
s = open(p).read()
if "_save_battery" in s:
    print("already patched"); sys.exit()
a = "            low_state_data = msg['data']\n"
assert s.count(a) == 1, "driver code changed; patch not applied"
s = s.replace(a, a + "            _save_battery(low_state_data)   # go2 console patch: battery to /tmp/go2_battery.json\n")
s += '''

# go2 console patch (10-23): keep the latest battery part of the dog's low state for the console. Max every 2 s.
import json as _json, os as _os, time as _time
_BATT = {"t": 0.0}


def _save_battery(d):
    now = _time.time()
    if now - _BATT["t"] < 2.0:
        return
    _BATT["t"] = now
    try:
        out = {k: v for k, v in d.items() if k != "motor_state"}
        out["t"] = round(now, 2)
        with open("/tmp/go2_battery.json.tmp", "w") as f:
            _json.dump(out, f)
        _os.replace("/tmp/go2_battery.json.tmp", "/tmp/go2_battery.json")
    except Exception:
        pass
'''
open(p, "w").write(s)
print("patched")
EOF
docker exec $C python3 -m py_compile "$F" && echo "compiles; now restart the driver: ./run_go2_keys.sh --reset"
