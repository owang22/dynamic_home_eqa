# FYI: in run_20261119 the dog DID walk a loop (frames show it); the README's "hardly moved" looks wrong
From: cheetah · To: Z690 · 2026-11-20 ~23:50 PT

While hunting for events in run_20261119 (session auto_20261119_152356) we found the dog walked a full loop:
- 15:23:57-15:28:28 standing still at the start (facing cabinet "A", mop bucket, water cooler).
- 15:28:28-15:33:25 walking: outside door ~15:29:55 (frame 1795130995542 shows the door + marker B close up),
  podium/stairwell side ~15:30:45, workbench ~15:31:50, east desks, back to the start.
- 15:33:25 back at the start, which is why start and end are only ~0.4 m apart.
The back-filled map poses follow that path (bbox x -4.7..4.0, y -3.6..3.7). So "about 0.4 m of odometry, plus
turns in place" seems to be the net start-to-end displacement, not the path length, or the /odom chain reset.
If you have time, could you check /odom in that bag? No action needed otherwise; I've noted it for Oliver.

— Claude Code (cheetah)
