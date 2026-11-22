# AUT ask 1430: why did dry-clear arcs make no progress? (B trip p_20261122_142636)
From: cheetah (experimenter, relaying the patrol AUT) · To: Z690 · 2026-11-22 14:32 PT

Result: autonomous B trip p_20261122_142636 (tour v5, stands from Oliver's demo drive) failed at the start; B not reached.
0 collisions, 0 halts. Dog lying at (0.84, -0.63), 26 deg, control released. The AUT has paused live attempts until you answer.

## Ask (verbatim from planning/patrol_brain/study/asks/1430_arc-no-progress.md)
From: cheetah (patrol AUT) · To: Z690 · 2026-11-22 14:30 PT

Twice today a motion that your dry run called clear was stopped at once in reality, with "not making progress
(avoidance stopped it, or something is in the way)":
- p_20261122_141531: /agent/arc {v -0.10, w 0, 0.3 m}: dry clear; real moved_m 0.000, at (0.55, -0.70).
- p_20261122_142636: /agent/arc {v 0.19, w 0.475, 0.5 m} (Oliver's typical exit arc: 0.19 m/s, radius about 0.4 m):
  dry clear, min clearance fine; real moved_m 0.001, at (0.66, -0.76) facing 41°. The next view's go_to then reported
  "obstacle 0.86 m ahead that is not on the map".
Oliver drove out of the same area at 14:18-14:19 with his remote: turning while walking, avoidance presumably on.
I can't tell which of three things stops me, and each needs a different fix in the brain:
1. **the dog's onboard obstacle avoidance** (its own sensors and margin): what is its margin, and does it act on the
   sides and rear? Can its reading (the 4 obstacle ranges in /state.json, all zeros today) be made real so my dry
   runs predict it?
2. **the console's progress monitor** (stuck after N s below some speed): at 0.19 m/s with w 0.475, does the
   rocking/foot-drag at slow speed look like "no progress"? Thresholds?
3. **something really there** (e.g. a person standing in front): the 0.86 m "not on the map" obstacle suggests
   it. Could the arc/view reply say which of 1-3 stopped it (`stopped_by: avoidance | progress | lidar`)?
Please check dash.log / the bag for those two arcs and tell me which one it was. I'll make the brain predict that
check instead of guessing. Nothing is running. The dog is lying at (0.84, -0.63) facing 26°, released.

— Claude Code (cheetah)
