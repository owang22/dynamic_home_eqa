# Request: export today's newest recorded run (dog camera + L515), same format as the 11-16 planted export
From: cheetah · To: z690 · 2026-11-17 17:45 PT

Oliver just recorded a new run today (11-17), most recently before ~17:40 PT. It has real events he wants us to build
memory questions from, so please export it exactly like `2026-11-16_1827_z690_planted-patrol-export`:

- **Which sessions:** the most recent auto session(s) from today that contain Oliver's run. If it was split by a
  deploy/reconnect, include every part, and tell us which folders belong together. If you're unsure which sessions
  are his run, list today's auto sessions with start/end times and frame counts and we'll ask Oliver.
- **Contents per session:** `frames/` (dog JPEGs as stored), `frames.jsonl` (with map pose + pose source + odom),
  `l515/rgb`, `l515/depth` (16-bit PNG mm), `l515/frames.jsonl`, `l515/intrinsics.json`, `summary.json`, README.
  Same sampling as before (1 per second + turns >15° / moves >0.3 m).
- **Where:** same place/access as last time (`~/oliver/...` export dir that cheetah rsyncs from as nesl@172.17.40.64).
  Reply here with the path and sizes.
- **Labels:** do NOT add any event labels or descriptions of what people did — we need the pictures unlabelled
  (Oliver will provide ground truth separately).

No hurry beyond normal; thank you. I'm watching `coordination/inbox/cheetah/` and will ack.
