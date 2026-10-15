#!/bin/bash
# Start the dog's software in Docker, or run one of the tools inside it.
#
#   ./run.sh robot [mapping|lab_map|our_map]   driver + map + Nav2 + RViz (default: our_map if saved, else lab_map)
#   ./run.sh keyboard                          drive with the keyboard (in a second terminal)
#   ./run.sh record                            name positions (in a second terminal)
#   ./run.sh patrol [only=a,b] [dry_run]       one patrol (in a second terminal)
#   ./run.sh search "where is the red mug?"    look for one thing, the robot brain choosing where
#   ./run.sh save_map                          save the map built in mapping mode to data/maps/lab
#   ./run.sh bag                               record camera + position to a bag, until Ctrl+C
#   ./run.sh shell                             a shell inside the running container
#
# Settings come from go2/robot.env (copy robot.env.example); data lands in go2/data/.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DATA="$HERE/data"
mkdir -p "$DATA/maps" "$DATA/patrols" "$DATA/searches" "$DATA/bags"
[ -f "$HERE/robot.env" ] && source "$HERE/robot.env"
: "${ROBOT_IP:=192.168.12.1}"
# not 78: the lab driver on the control PC uses 78, and with host networking anything published
# here on 78 (a patrol's tilt commands, say) would reach the real dog. Set 78 only to drive it from here.
: "${ROS_DOMAIN_ID:=42}"
IMAGE=go2-lab
NAME=go2

in_container() { docker exec -it "$NAME" /entrypoint.sh "$@"; }

case "${1:-}" in
  robot)
    mode="${2:-}"
    if [ -z "$mode" ]; then [ -f "$DATA/maps/lab.posegraph" ] && mode=our_map || mode=lab_map; fi
    case "$mode" in
      mapping) slam=/ros2_ws/install/go2_patrol/share/go2_patrol/config/slam_mapping.yaml ;;
      our_map) slam=/ros2_ws/install/go2_patrol/share/go2_patrol/config/slam_localize_ours.yaml ;;
      lab_map) slam=/ros2_ws/install/go2_robot_sdk/share/go2_robot_sdk/config/mapper_params_online_async.yaml ;;
      *) echo "unknown map mode $mode"; exit 1 ;;
    esac
    echo "dog at $ROBOT_IP, map: $mode, ROS domain $ROS_DOMAIN_ID  (close the Unitree phone app first;"
    echo " the dog takes one connection, so stop the lab driver on the control PC: docker rm -f go2_test)"
    xhost +local: >/dev/null 2>&1 || true
    docker run --rm -it --name "$NAME" --net=host --ipc=host \
      -e DISPLAY="${DISPLAY:-:1}" -v /tmp/.X11-unix:/tmp/.X11-unix \
      -e ROS_DOMAIN_ID="$ROS_DOMAIN_ID" -e ROBOT_IP="$ROBOT_IP" -e CONN_TYPE=webrtc -e GO2_AES_KEY="${GO2_AES_KEY:-}" -e SLAM_PARAMS="$slam" \
      -v "$DATA":/data -w /data -v "$HERE/../robot_brain":/brain:ro \
      "$IMAGE" ros2 launch go2_robot_sdk robot.launch.py joystick:="${JOYSTICK:-false}"
    ;;
  keyboard)
    # twist_mux gives this topic priority over Nav2
    in_container ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=cmd_vel_joy ;;
  record)
    in_container ros2 run go2_patrol record_positions --ros-args -p positions_file:=/data/positions.yaml ;;
  patrol)
    shift; args=(-p positions_file:=/data/positions.yaml -p out_root:=/data/patrols)
    for a in "$@"; do
      case "$a" in only=*) args+=(-p "only:=${a#only=}") ;; dry_run) args+=(-p dry_run:=true) ;; *) echo "unknown $a"; exit 1 ;; esac
    done
    in_container ros2 run go2_patrol patrol --ros-args "${args[@]}" ;;
  search)
    # needs the robot brain running on this machine (robot_brain/README.md)
    [ -n "${2:-}" ] || { echo 'usage: ./run.sh search "where is the red mug?"'; exit 1; }
    in_container ros2 run go2_patrol search --ros-args -p positions_file:=/data/positions.yaml \
      -p out_root:=/data/searches -p question:="$2" ;;
  save_map)
    # after driving the whole lab in mapping mode; the next ./run.sh robot uses it (start the dog at the dock)
    in_container ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '/data/maps/lab'}"
    in_container ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: '/data/maps/lab'}}" ;;
  bag)
    in_container ros2 bag record -s mcap -o "/data/bags/$(date +%Y-%m-%d_%H%M)" /camera/image_raw /camera/camera_info /tf /tf_static /odom /imu /map ;;
  shell)
    in_container bash ;;
  *)
    sed -n '2,12p' "$0"; exit 1 ;;
esac
