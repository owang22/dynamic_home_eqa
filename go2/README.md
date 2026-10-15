# Go2 Pro: connecting, mapping, patrols

Software for getting pictures out of the lab's Unitree Go2 Pro for the object-search study.
It runs the lab's own driver, [nesl/Go2Controller](https://github.com/nesl/Go2Controller) pinned
at `f7898ac`, in Docker with two small patches. It adds a `go2_patrol` package that names positions
and photographs them on a patrol. What the study needs from the robot is in
`prior_work/results/rendered_look/lab_study/BRIEF_FOR_THE_DOG_AGENT.md`.

## 1. Network: put the computer and the dog on one network

The computer talks to the dog over Wi-Fi, through the same WebRTC link the Unitree phone app uses.
A Go2 Pro has no other way in. **Only one controller can connect at a time, so close the phone app.**

| the dog's Wi-Fi mode (set in the app) | the dog's address | the computer needs |
|---|---|---|
| its own hotspot ("AP"; your phone joins the dog's network) | always `192.168.12.1` | to join that hotspot |
| joined to another network ("STA") | in the app: Device → Data → Automatic Machine Inspection → STA Network: wlan0 | to be on the same network, with nothing blocking traffic between devices |

**cheetah's own Wi-Fi does not work yet.** Its card is a MediaTek MT7925 (PCI id `14c3:0717`).
This Linux (kernel 5.15) has no driver for it, so the card does not appear in `ip link`. There are
three ways round it:
1. **A USB Wi-Fi adapter that kernel 5.15 supports (recommended).** Choose one with a MediaTek
   MT7612U or MT7921AU chip, for example an Alfa AWUS036ACM. Plug it in, then
   `nmcli dev wifi connect "<dog's hotspot name>" password "<its password>"`. The wired connection
   stays the internet route.
2. **A newer kernel**, `sudo apt install linux-generic-hwe-22.04` (6.8, which has `mt7925e`), then a
   reboot. That also rebuilds the NVIDIA driver, so leave it until the GPU is stable.
3. **A small router** that both the dog (STA mode) and cheetah join. Use this if cheetah is not in
   the lab, or the hotspot does not reach the whole lab. Campus Wi-Fi with a university login will
   not work: the Go2 cannot sign in to that kind of network.

Range matters: during a patrol the dog streams video the whole time. If the link drops, the driver
loses the camera and stops sending walking commands.

## 2. First contact (no Docker, nothing moves)

```bash
conda activate go2          # made on cheetah 2026-10-13: unitree_webrtc_connect 2.2.0 + opencv
# elsewhere: conda create -n go2 python=3.10 && conda install -c conda-forge portaudio \
#            && pip install unitree_webrtc_connect opencv-python-headless
python go2/check_connection.py                    # hotspot mode
python go2/check_connection.py --ip 192.168.x.y   # dog on another network
```

It checks four things in order:
1. whether the dog answers at all;
2. which handshake the firmware uses. `data2=3` means firmware 1.1.15 or later, which needs a
   **per-dog key**;
3. whether the connection opens;
4. whether a camera picture arrives. The picture and the battery level are saved to `go2/data/checks/`.

**If it says a key is needed:** run `unitree-fetch-aes-key --email <the account the dog is
registered to> --device-type Go2` yourself. It ships with the library and asks Unitree's server.
Put the 32 hex characters it prints in `go2/robot.env` as `GO2_AES_KEY=`. Copy that file from
`robot.env.example`; it is not committed.

## 3. The robot software (Docker)

```bash
cd go2
docker build -t go2-lab -f docker/Dockerfile .    # once; about 10 minutes
cp robot.env.example robot.env                    # set ROBOT_IP (and GO2_AES_KEY if needed)
./run.sh robot mapping                            # terminal 1: driver, LiDAR, map, Nav2, RViz
./run.sh keyboard                                 # terminal 2: drive (i/j/k/l; slow down with x and c first)
```

`./run.sh robot` starts everything in the lab repo's `robot.launch.py`. The topics are:
- camera: `/camera/image_raw` (the lab README's `go2_camera/color/image` is out of date);
- position: `/odom` and `/tf`;
- LiDAR: `/point_cloud2` and `/scan`;
- the map: `/map`;
- walking goals: `navigate_to_pose`;
- body commands: `/webrtc_req`.

Foxglove can view all of it at `ws://localhost:8765`.

### The map

slam_toolbox can either build a map or use a saved one. A saved map assumes the dog is switched on
at the spot where that map was started (the **dock**), facing the same way. Mark the dock on the
floor with tape.

- `./run.sh robot lab_map` uses the map in the lab repo (about 9.5 × 9.5 m). We do not know whether
  it is our lab, or where its dock was, so treat it as unusable until someone confirms both.
- To make our own map:
  1. Run `./run.sh robot mapping`, starting from the dock.
  2. Drive slowly through every area the patrol will use and come back to the dock.
  3. Run `./run.sh save_map`. This writes `data/maps/lab.*`.
- From then on, `./run.sh robot` uses our map.
- Rebuild the map after the November cleanup, and note the rebuild in the log, because the cleanup
  moves what the map was built from.

### Positions and patrols

```bash
./run.sh record             # drive to each spot, face it, type a name ("dock" first; "bench_A 15" = tilt 15°)
./run.sh patrol dry_run     # first time: walk and photograph, no body tilt
./run.sh patrol             # a real patrol
./run.sh patrol only=bench_A,shelf_2
```

- **Output:** `data/patrols/<date>/<HHMM>/<id>.jpg` plus `patrol.json`, which has the target and
  actual position, how far off it stopped, the commanded tilt, the IMU roll/pitch/yaw at the
  picture, and every failure. The search benchmark reads this layout.
- **Failures:** a position that cannot be reached after 2 tries is logged and skipped. The dog
  returns to the dock at the end.
- **Stopping early:** Ctrl+C cancels the walking goal first, so the dog does not keep going.
- **Keyboard teleop:** commands from it take priority over the patrol (twist_mux). The keyboard
  window must stay open, but idle.
- **Before any patrol:** the RViz robot must sit on the map where the real dog is. If it does not,
  restart at the dock.

### Searching for one thing

```bash
./run.sh search "where is the red mug?"
```

- **Who decides what:** the robot brain (`robot_brain/`, built by another session; start it as
  `robot_brain/README.md` says) chooses where to look. This side does the walking and photographing.
- **The loop:**
  1. `/ask` gives a plan of position ids.
  2. The dog walks to the first one, photographs it, and sends the picture to `/look`.
  3. The brain answers whether the thing is in it, and which position to try next.
  4. A position the dog cannot reach is reported to `/feedback`, which names the next one.
- **When it stops:** when the thing is found, when the plan runs out, after 8 looks, or when the
  brain names a position that is not in `positions.yaml`.
- **Where the dog ends up:** where the search ended (`-p return_to_dock:=true` brings it back).
- **Output:** `data/searches/<date>/<HHMMSS>_<question>/look_<n>_<id>.jpg` plus `search.json`, with
  each look and the brain's answer to it.
- **Pictures:** sent to the brain as bytes, so it does not need to see this folder.
- **After a patrol:** let the brain read it, so its memory is current:
  `python -c "import sys; sys.path.insert(0,'robot_brain'); from client import Brain; print(Brain().ingest_patrol('/data/patrols/<date>/<HHMM>'))"`.
  This needs the brain started with `--path-map /data=$PWD/go2/data`.

`./run.sh bag` records the camera, positions and map to an MCAP bag until Ctrl+C. It is useful for
a first walk-through before positions exist.

## The lab setup since 2026-10-14: the control PC drives the dog

- **Who connects:** the dog is on lab Wi-Fi at `172.17.39.82`. The lab's control PC (`nesl-Z690-CLASSIFIED`,
  `172.17.40.64`) holds its one connection and runs a web console at `http://172.17.40.64:8080`. cheetah reaches it
  over the wired network, so cheetah's Wi-Fi card no longer matters. The console's endpoints and the agents' message
  board are in Oliver's doc "Go2 Robot Dog Lab Guide" (tabs "AI agent interface" and "Agent chat").
- **Measured from cheetah:** `GET /frame.jpg` is a 1280×720 JPEG (about 115 KB, 0.1–0.35 s old). `GET /events`
  sends pose, map pose, sensors and a lidar obstacle grid 10 times a second.
- **Driving:** `POST /cmd` answers 204. The dog needs about 0.6 rad/s to step round in a turn; slower turns barely
  move it. `console/motion_test.py` and `console/turn_test.py` are the first tests (avoidance on, a person next to
  the dog). At 0.6 rad/s, 30° turns settle within 6°; backing up 0.2 m gave 0.21 m.
- **ROS domain:** this computer's containers use `ROS_DOMAIN_ID=42`. The control PC's driver uses 78, and with host
  networking, anything published here on 78 (a patrol's tilt commands, say) would reach the real dog. `./run.sh robot`
  would also try to open a second connection to the dog, which it refuses while the control PC holds it.

## What was changed in the lab repo, and why

- **`patches/0001-firmware-key-support.patch`.** The lab's driver read the robot's handshake reply
  as plain text, which is right only for old firmware.
  - It now also unwraps the two newer forms: a key shared by all firmware below 1.1.15, and the
    per-dog key `GO2_AES_KEY` for 1.1.15 and later.
  - This follows `legion1581/go2_webrtc_connect` 2.2.0, and is checked against that library's own
    decryption on made-up data.
  - It also sends the hotspot-mode connection id (empty) when the address is 192.168.12.1, as that
    library does.
- **`patches/0002-launch-slam-params-from-env.patch`.**
  - `SLAM_PARAMS` picks mapping, the lab map, or our map. The launch file had no way to choose.
  - The raw point-cloud dump that wrote a file every 10 seconds is now off by default.
- **Docker.** The lab's Dockerfile cloned the upstream driver instead of the lab repo, so the lab's
  map and changes never reached the container. It also installed the teamwork and LLM stack, which
  the patrol does not need. `docker/Dockerfile` builds the pinned lab repo with the patches, and
  only the driver, the LiDAR processor and `go2_patrol`.
- **Camera calibration.** Use the 720p file. In the 1080p file the second and third rows of the
  camera matrix have 1 where 0 belongs. 720p gives a horizontal field of view of about 73°.

The driver does not retry. If the dog is not reachable when `./run.sh robot` starts, it logs
`Failed to get robot public key` and stops. Wait until the dog has fully started (about a minute
after power-on), close the phone app, and start it again.

## Not checked on the real dog yet

Everything above was tested on cheetah without the dog:
- `tests/test_patrol.sh` with `tests/fake_robot.py`;
- `tests/test_search.sh` with `tests/fake_brain.py` (a fixed plan) and the real `robot_brain/client.py`.

Still to check on the real dog:
- that the connection works with its firmware;
- **the tilt direction.** Nose-up is sent as negative pitch. Check the first tilted picture, and the
  IMU pitch recorded in `patrol.json`;
- how far off Nav2 stops in this lab;
- battery use per patrol.
