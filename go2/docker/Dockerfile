# The lab's Go2 driver (nesl/Go2Controller, pinned) plus our patches and the go2_patrol package.
# Only what robot.launch.py and the patrol need is built: the lab repo's teamwork, speech and LLM
# packages are left out. Build from go2/:   docker build -t go2-lab -f docker/Dockerfile .
FROM ros:humble-ros-base-jammy
SHELL ["/bin/bash", "-c"]
ARG NESL_COMMIT=f7898ac0d035272dc7212707e017ad27e4fe4558

RUN apt-get update && apt-get install -y --no-install-recommends \
      git python3-pip ffmpeg libavdevice-dev libavfilter-dev libopus-dev libvpx-dev libsrtp2-dev pkg-config \
      ros-humble-rviz2 ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-slam-toolbox \
      ros-humble-pointcloud-to-laserscan ros-humble-twist-mux ros-humble-joy ros-humble-teleop-twist-joy \
      ros-humble-teleop-twist-keyboard ros-humble-foxglove-bridge ros-humble-cv-bridge \
      ros-humble-image-transport ros-humble-compressed-image-transport ros-humble-image-tools \
      ros-humble-vision-msgs ros-humble-robot-state-publisher ros-humble-tf-transformations \
      ros-humble-sensor-msgs-py ros-humble-rosbag2-storage-mcap \
    && rm -rf /var/lib/apt/lists/*

# versions as in the lab repo's requirements.txt (aiortc 1.9.0, numpy 1.26.4)
RUN pip install --no-cache-dir aiortc==1.9.0 aiohttp wasmtime open3d pycryptodome opencv-python-headless \
      numpy==1.26.4 requests pyyaml transforms3d python-dotenv

WORKDIR /ros2_ws/src
RUN git clone https://github.com/nesl/Go2Controller.git nesl && cd nesl && git checkout -q ${NESL_COMMIT} \
    && git submodule update --init --recursive
COPY patches /patches
RUN cd nesl && git apply --verbose /patches/*.patch
# slam_toolbox reads the lab's saved map from /ros2_ws/lab_map.* (mapper_params_online_async.yaml)
RUN cp nesl/lab_map.* /ros2_ws/
COPY go2_patrol /ros2_ws/src/go2_patrol
# two SLAM settings next to the lab's: build a new map, or use one we saved under /data/maps/lab
RUN cfg=nesl/go2_robot_sdk/config/mapper_params_online_async.yaml && mkdir -p go2_patrol/config \
    && sed -e 's/^\(\s*\)mode: localization/\1mode: mapping/' -e '/map_file_name:/d' -e '/map_start_at_dock:/d' \
         $cfg > go2_patrol/config/slam_mapping.yaml \
    && sed -e 's#map_file_name: .*#map_file_name: /data/maps/lab#' $cfg > go2_patrol/config/slam_localize_ours.yaml \
    && grep -q 'mode: mapping' go2_patrol/config/slam_mapping.yaml \
    && grep -q '/data/maps/lab' go2_patrol/config/slam_localize_ours.yaml

WORKDIR /ros2_ws
RUN source /opt/ros/humble/setup.bash \
    && colcon build --packages-up-to go2_robot_sdk lidar_processor go2_patrol 2>&1 | tail -20 \
    && test -f install/go2_patrol/lib/go2_patrol/patrol && test -f install/go2_robot_sdk/lib/go2_robot_sdk/go2_driver_node

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
