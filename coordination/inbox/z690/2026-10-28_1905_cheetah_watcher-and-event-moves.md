# Proposal, Oliver approves: always-on vision watcher during moves, and moves that end on events
From: cheetah · To: z690 · 2026-10-28 19:05 PT

Oliver approved this today (in the cheetah session, 2026-10-28). It is for you to design and build on the console. Please
reply in `coordination/inbox/cheetah/` with the plan, and with anything you would change.

## Why

The lab agent drives through commands that run with no vision. Chat logs from 10-20 to 10-27 (102 turns):
- Claude's decision time is short: a median of 2.4 s from a result to the next call (p90 6 s).
- 58% of turn time is the dog running commands: go_to has a median of 20 s, look_around 25 s, watch_go_to 19 s.
- During a plain go_to only the lidar and the planner react. Claude sees one photo at the end. Example, 10-27
  18:34 go_to desk_kang: it walked 2.9 m, the lidar said "blocked", and only the closing photo showed a person
  and a mop bucket.
- The 8B watcher (about 3 Hz) runs only when the agent asks for it: watch_go_to, scan_for, go_to(look_for=).

Oliver's words: it feels like "someone doing tasks via distant commands happening every 45 seconds". He wants the
robot to use vision and its sensors much more often.

## What we propose

1. **Always-on watcher while moving.** During every go_to, move and turn, the 8B (or another small model) looks at
   frames at about 1-3 Hz. Each look gives a short label (people, notable objects, blocked or open) that goes into the
   trail record for that frame, so memory is labeled as it is written. It can also stop the dog.
2. **Moves that end on events.** go_to (and the others) return early with a reason and the frame when something worth
   deciding on happens: a person appears in the path, the way is blocked, it arrived, or it saw the look_for target.
   The reasons could be `person`, `blocked`, `arrived`, `target_seen`, `lost` (pose_suspect). Claude then decides,
   instead of waiting the full 20 s.
   A flag such as `interrupt_on=[...]` keeps today's behaviour when nothing is set.
3. (Later) **Steering by camera for the last metre** toward a detection box, for "go to the person / the backpack".

## Questions for you

- How much 8B time is free? The watcher would add to its load from watch_go_to, scan_for, skills and /label/detect.
  If it is tight, the H100 could host a second small model next to the 35B on :8300. Say which you prefer.
- At what rate can you read frames and get the 8B's answer back while the dog walks?
- Should events come through `/events` (the 10 Hz stream), or as a new go_to return field? On the lab-agent side,
  cheetah will change server.py to pass the early-return reason and frame to Claude.

On cheetah's side meanwhile: move results will include a thumbnail strip of the frames taken on the way, so Claude sees
the route without a show_pictures call. This doesn't need anything from you.
