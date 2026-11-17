#!/usr/bin/env bash
# Deploy a console version to the running driver container: the one way to restart the console.
#   ~/oliver/deploy_console.sh [git-ref]      (default HEAD of ~/dynamic_home_eqa)
# 1. takes navigation/go2_dashboard.py and go2_mapper.py from the git ref (not the working copies)
# 2. POST /deploying: the console stops the dog, refuses all motion and shows a "deploying" overlay; checks the
#    dog's odom speed is ~0 and sends STOP again if not
# 3. copies the files into the container (and to ~/oliver, which run_go2_keys.sh copies from)
# 4. SIGTERMs the console by PID and waits for it to exit (it stops the dog again and closes the auto session)
# 5. starts it the way run_go2_keys.sh does and waits for /state.json
# 6. prints the new boot id, the L515 and auto recording state
# Never restarts the driver or the container. The driver has no command timeout: the dog keeps the last velocity
# it was given, which is why every step above stops it explicitly.
# Env: GO2_CONTAINER (go2_test), GO2_PORT (8080), GO2_REPO (~/dynamic_home_eqa), GO2_OLIVER (~/oliver; empty = skip).
set -u
C=${GO2_CONTAINER:-go2_test}
PORT=${GO2_PORT:-8080}
REPO=${GO2_REPO:-$HOME/dynamic_home_eqa}
OLIVER=${GO2_OLIVER-$HOME/oliver}
REF=${1:-HEAD}
ROS='source /opt/ros/humble/setup.bash && source /ros2_ws/install/setup.bash'
FILES="go2_dashboard.py go2_mapper.py"
PAT='^python3 /root/go2_dashboard.py'
die() { echo "deploy_console: $*" >&2; exit 1; }
# HTTP from inside the container, so this works whatever its network setup
http() { docker exec "$C" curl -s -m 5 "$@"; }
console_pid() { docker exec "$C" pgrep -f "$PAT"; }
speed() {  # prints "v w" (m/s, rad/s) from /state.json, or "? ?"
    http "http://localhost:$PORT/state.json" | docker exec -i "$C" python3 -c '
import json, math, sys
try:
    v = (json.load(sys.stdin).get("odom") or {}).get("vel")
    print(f"{math.hypot(v[0], v[1]):.3f} {abs(v[2]):.3f}" if v else "? ?")
except Exception:
    print("? ?")'
}
moving() { read -r v w <<<"$(speed)"; [ "$v" = "?" ] && return 1
    awk -v v="$v" -v w="$w" 'BEGIN{exit !(v > 0.05 || w > 0.10)}'; }
stop_cmd() { http -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' \
    -d '{"action":"stop","client":"deploy_console"}' "http://localhost:$PORT/cmd"; }
ros_stop() {  # straight to the driver, for consoles without /deploying (or none at all): avoid-zero move + StopMove
    docker exec "$C" bash -c "$ROS && for i in 1 2 3; do
        timeout 3 ros2 topic pub --once /webrtc_req go2_interfaces/msg/WebRtcReq \"{api_id: 1003, topic: rt/api/obstacles_avoid/request, parameter: '{\\\"x\\\": 0.0, \\\"y\\\": 0.0, \\\"yaw\\\": 0.0, \\\"mode\\\": 0}', priority: 1}\" >/dev/null 2>&1
        timeout 3 ros2 topic pub --once /webrtc_req go2_interfaces/msg/WebRtcReq \"{api_id: 1003, topic: rt/api/sport/request, parameter: '', priority: 1}\" >/dev/null 2>&1
    done" && echo "  sent avoid-zero + StopMove to the driver directly"
}

# ---- 1. files from git
[ "$(docker inspect -f '{{.State.Running}}' "$C" 2>/dev/null)" = "true" ] || die "container $C is not running (start it with run_go2_keys.sh; this script never does)"
SHA=$(git -C "$REPO" rev-parse --short "$REF^{commit}") || die "unknown git ref $REF in $REPO"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
for f in $FILES; do
    git -C "$REPO" show "$SHA:navigation/$f" > "$TMP/$f" || die "navigation/$f not in $SHA"
done
for f in $FILES; do python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$TMP/$f" || die "$f from $SHA does not parse"; done
echo "Deploying console from $REPO @ $SHA ($(git -C "$REPO" log -1 --format=%s "$SHA" | cut -c1-70))"

# ---- 2. deploying: stop the dog, refuse motion, overlay
OLD=$(console_pid)
[ "$(echo "$OLD" | wc -w)" -le 1 ] || die "more than one console process in $C: $OLD"
OLD_DEPLOYING=0
if [ -n "$OLD" ]; then
    code=$(http -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' \
        -d "{\"msg\": \"deploy_console.sh: $SHA\"}" "http://localhost:$PORT/deploying")
    if [ "$code" = 200 ]; then
        OLD_DEPLOYING=1; echo "Console $OLD: deploying mode on (dog stopped, motion refused, overlay shown)"
    else
        echo "Console $OLD has no /deploying (HTTP $code; older version): sending STOP instead"
        stop_cmd >/dev/null
    fi
    sleep 1
    for i in 1 2 3; do
        if moving; then read -r v w <<<"$(speed)"; echo "  dog still moving ($v m/s, $w rad/s): STOP again"; stop_cmd >/dev/null; sleep 1
        else break; fi
    done
    read -r v w <<<"$(speed)"; echo "  odom speed now $v m/s, turn $w rad/s"
    if moving; then echo "  WARNING: odom still shows motion after 3 STOPs (check the dog!). Continuing: the old console"
        echo "  stops it again on exit and the new one sends a stop when it starts."; fi
else
    echo "No console running in $C; starting one"
fi

# ---- 3. copy
for f in $FILES; do docker cp -q "$TMP/$f" "$C:/root/$f" || die "docker cp $f failed"; done
if [ -n "$OLIVER" ] && [ -d "$OLIVER" ]; then
    for f in $FILES; do
        if [ -f "$OLIVER/$f" ] && ! cmp -s "$TMP/$f" "$OLIVER/$f"; then cp "$OLIVER/$f" "$OLIVER/$f.before_deploy"; fi
        cp "$TMP/$f" "$OLIVER/$f"
    done
fi

# ---- 4. stop the old console
if [ -n "$OLD" ]; then
    docker exec "$C" kill -TERM "$OLD"
    for i in $(seq 40); do docker exec "$C" kill -0 "$OLD" 2>/dev/null || break; sleep 0.5; done
    if docker exec "$C" kill -0 "$OLD" 2>/dev/null; then
        echo "  console $OLD did not exit in 20 s: SIGKILL"; docker exec "$C" kill -KILL "$OLD"; sleep 1
    fi
    echo "Old console $OLD exited"
    [ "$OLD_DEPLOYING" = 1 ] || ros_stop    # an old console doesn't stop the dog when it exits
fi

# ---- 5. start
docker exec -d "$C" bash -c "$ROS && exec python3 /root/go2_dashboard.py $PORT > /tmp/dash.log 2>&1"
ok=0
for i in $(seq 40); do
    if http -f -o /dev/null "http://localhost:$PORT/state.json"; then ok=1; break; fi
    sleep 1
done
[ "$ok" = 1 ] || die "new console did not answer within 40 s; see /tmp/dash.log in $C"
sleep 3   # L515 status and auto recording settle

# ---- 6. report
http "http://localhost:$PORT/state.json" | docker exec -i "$C" python3 -c '
import json, sys
s = json.load(sys.stdin)
l, a, d = s.get("l515") or {}, (s.get("rec") or {}).get("auto_info") or {}, s.get("deploying")
print("New console up: pid in container", sys.argv[1], "boot_id", s.get("boot_id"))
print("  deploying:", d)
print("  L515: online={} fps={} age_s={} bridge={}".format(l.get("online"), l.get("fps"), l.get("age_s"), l.get("bridge")))
print("  auto recording: state={} session={}".format(a.get("state"), a.get("session")))
' "$(console_pid)"
