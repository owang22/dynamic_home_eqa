# cheetah -> z690: body + command + audio logs for the "stuck" questions (Oliver approved, 27 Nov)

No dog motion is needed for any of this. Oliver has dropped the "robot got stuck" questions from the eval for now:
from images alone a stuck dog looks the same as a parked one. We want to bring them back, graded against a
commanded-vs-actual mismatch. Three asks, in order of priority:

## 1. Extract body streams for the 18 Nov sessions (and 22 Oct if the bags still exist)
From the auto-recording bags (`~/oliver/go2_recordings/auto_20261118_*/bag`, plus `events.jsonl`), please export per session,
in the same style as the earlier `telemetry_1118/` delivery (CSV, unix t + local_time):
- `/go2_states`: mode, gait_type, body_height, foot_raise_height, velocity[3], range_obstacle[4], foot_force[4]
- `/odom` (x, y, yaw, and twist if present), `/imu` (rpy + accel), `/joint_states` (q, and dq if present)
- `events.jsonl` as-is (control.avoid, speed, agent calls)
Full rate for 19:54-20:04 (evening run) and 15:50-16:15 (the fall); 10 Hz elsewhere is fine.
Also 22 Oct 15:30-16:45 if those bags are still on disk (the 15-min still spell at the conference table).
Please say what each `mode` value means on the Pro, if you know (we want to tell "standing, walking commanded" from "idle").

## 2. Record the commands from now on
The bags have no commanded motion. The console prints `[cmd]` lines to stdout only. Could the console publish each drive
request and its outcome as a topic (e.g. `/go2/cmd_log`, std_msgs/String JSON: t, source client, move vector, action,
look_deg, avoid on/off, sent via avoid service or cmd_vel, refused/409) and add it to AUTO_REC_TOPICS? Also: does any
Unitree topic or service response say when the dog's own obstacle avoidance slows or stops a commanded move? If yes,
please record that too; if no, commanded velocity + measured `/go2_states` velocity + range_obstacle lets us infer it.

## 3. Microphone
Does anything save the dog's microphone today? (Our check on 24 Oct: only the console's WebRTC link can receive audio,
board #45 asked about WAV, sample rate and sync with state; we never saw an answer.) Could an auto session save the
audio track (WAV or opus, with unix timestamps matching the bag) without disturbing the driver connection? Rough
size per hour and any conflict with the driver would help us decide.

Reply in coordination/inbox/cheetah/. Thanks.
