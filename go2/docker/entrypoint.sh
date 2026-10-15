#!/bin/bash
# ROBOT_IP, CONN_TYPE, GO2_AES_KEY and SLAM_PARAMS come from `docker run -e` (see go2/run.sh)
source /opt/ros/humble/setup.bash
source /ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-42}   # 78 is the lab driver's; see run.sh
export CONN_TYPE=${CONN_TYPE:-webrtc}
export ROBOT_IP=${ROBOT_IP:-192.168.12.1}
cat >> ~/.bashrc <<'RC'
source /opt/ros/humble/setup.bash
source /ros2_ws/install/setup.bash
RC
exec "$@"
