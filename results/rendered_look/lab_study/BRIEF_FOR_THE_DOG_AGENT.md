# What the object-search study needs from the Go2 Pro

Written 2026-10-01 by the rendering / search-benchmark session for the agent that sets up the dog
and its remote control. It says what the study needs the robot to deliver, and what is already known
about the robot, with sources. It does not say how to build it. Project page:
https://claude.ai/artifact/CXWkHsJrTLr57kKm5RQAbc (Plan tab has the study design).

## The study in three sentences

A robot patrols a lab on a fixed schedule for several weeks, photographing a fixed list of
positions, and a memory built from those pictures is asked where a named object is (and later,
when a bench or a person will be around). In November the lab is cleaned up and many objects
move or are thrown out; that is the shift the study measures recovery from. Everything is scored
against a ground-truth log kept by a person.

## What the robot must deliver, in order of need

1. **Still pictures from the front camera on request**, full resolution (1280x720 or better),
   saved as JPEG with: a timestamp, the position id the robot was at, the body pitch at the time,
   and which camera (built-in, or the raised one if an arm is built). One picture per position per
   patrol is enough; video is not needed.
2. **Going to a named position from a list and stopping there**, within about 0.3 m and 15
   degrees, then returning to the start point. 15 to 30 positions in one lab. Floor markers are
   acceptable at first. The study's walking-cost measure needs the metres between positions,
   which can be measured once by hand. Because the cleanup will move furniture and may wipe
   floor markers, the LiDAR map must be rebuilt right after it, and that rebuild logged as an
   event. Printed fiducial markers (AprilTags) on fixed walls and bench ends let each picture
   report which surfaces it shows, so a picture from a wrong viewpoint can be rejected in scoring;
   the dog agent need only not remove them.
3. **A patrol at fixed times** (for example 09:00, 12:00, 15:00 on weekdays), started by a named
   person from a laptop with one command, with a log of the actual start time, what was
   photographed and what failed. A missed or late patrol is fine if it is logged; a silent one is
   not. An independent reviewer (1 Oct) pointed out that a Go2 Pro has no charging dock, no
   remote power-on, and a battery of roughly 1.5 to 2 hours of walking that also drains while
   standing, so unattended all-day patrols are not possible on this hardware: the design
   requirement is fixed times, not unattendedness, and someone owns the battery rota.
4. **Body pitch control** (tilt the nose up to about 15 degrees) when photographing a table, since
   the built-in camera at about 0.37 m sees little of table and counter tops; the simulator study
   says 15 degrees is enough and more does not help.
5. Later: **a second camera on an arm** at about 0.8 to 1.0 m above the floor, tilted down, with
   the same picture format and metadata. The simulator study says table tops need the lens at
   about 0.7 m and counter tops about 1.0 m.

A simple file layout is enough: `patrols/<date>/<time>/<position_id>.jpg` plus one `patrol.json`
with the metadata and failures. The search benchmark already reads this shape of data
(`src/rendered_look/searchbench/`).

## What is known about the robot (gathered 2026-09-30; [P] = read on a primary source)

- Model: **Go2 Pro**. Unitree's documents say only the EDU (and partly the X) is supported for
  secondary development; the official SDK is wired (Ethernet), which the Pro does not expose. [P]
  https://support.unitree.com/home/en/developer/about_Go2 and the FAQ.
- The channel that works on a Pro is the **WebRTC link the phone app uses**, over Wi-Fi, no
  firmware change. Community libraries: https://github.com/legion1581/go2_webrtc_connect (video
  and movement commands; firmware 1.1.15 and later needs a per-robot key) and
  https://github.com/abizovnuralem/go2_ros2_sdk (ROS 2, publishes the front camera at
  `go2_camera/color/image`, with a camera calibration file for 1280x720). Verify both still work
  with the robot's firmware before planning around them.
- Front camera: Unitree gives 1080p/720p streams; field of view is quoted variously as 100x56
  degrees, 120 degrees, and about 73x45 degrees from the community calibration. Measure it with a
  tape and a wall rather than trusting any of these. Camera sits 0.043 m above and 0.327 m ahead
  of the body centre, looking straight ahead [P] go2_description.urdf; with the body at 0.32 to
  0.33 m standing, the lens is about **0.36 to 0.37 m above the floor** (derived, not published).
- Posture: the official interface has `Euler(roll, pitch, yaw)` with pitch in -0.75 to 0.75 rad
  (about 43 degrees), so a 15-degree tilt is available. Unitree's Sports Services document also
  lists `BodyHeight(float)` with range **-0.18 to +0.03 m** relative to the 0.33 m stand (for Go2
  EDU firmware before 1.1.6; the current sport_client.hpp no longer declares it). Either way the
  robot can crouch but raise its camera by at most 3 cm. [P] https://doc-cdn.unitree.com/6/55/en/6_55_en
  and sport_client.hpp in unitree_sdk2 (checked 2026-10-01).
- No depth camera on the Pro. The LiDAR (L1 or L2, 360 x 90-96 degrees) is under the head; it is
  what any mapping and going-to-position software will use. Community reports say localisation
  drifts; the study can tolerate 0.3 m.
- Standing size 70 x 31 x 40 cm; a raised camera changes balance and what the robot walks under.

## Things to settle in the first week

- **Who starts each patrol and charges the battery.** See item 3: there is no unattended mode on
  this hardware. One named person and a written rota.
- **Wi-Fi.** The WebRTC link needs the laptop on the same network as the robot; the Go2's station
  mode on an enterprise network with 802.1X login commonly does not work. Test on the lab's real
  network in week one, or use a dedicated router.
- **Doors and cables.** A closed inner door ends a patrol; the LiDAR is under the head and does not
  see low cables, so the route must be clear each morning.
- **The camera is frozen before the first patrol.** If an arm is coming, it is built and run from
  day one beside the built-in camera; a camera change mid-record is a confound the study cannot
  remove.
- **Which positions.** The study session will give a list once the lab's layout and object set are
  chosen; the dog agent needs only to accept a list of named positions with coordinates or markers.

Oliver is taking a first set of photographs from the built-in camera (counter, table, low table,
floor, from about 1 m and from a few metres back) to check the simulator's camera-height study; those
go to the study session, not the dog agent.
