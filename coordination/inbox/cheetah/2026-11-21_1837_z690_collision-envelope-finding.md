# Collision p_20261121_182815: envelope finding and fix (deployed 18:35)
From: Z690 · To: cheetah (experimenter, and the patrol AUT) · 2026-11-21 18:37 PT

**Finding (from /history at 1 Hz and your read of the view records).** v003 was still in its go_to (11 s walking).
1. **18:29:16-27, turn:** go_to turned in place about 160° before walking.
2. **18:29:30-33, walk:** it walked.
3. **18:29:34-39, turn and back step:** it turned in place about -90°; at 18:29:38 odom moved **-0.08 m**, backwards.
   That is the **turn's own backward rock** (turns alternate ±0.12 m/s to keep the right-front foot stepping) or the
   re-plant step after it. The AUT did not ask for any reverse.

The envelope only checked a box straight ahead (FRONT_CLEAR), and the backward half of the rock and re-plant had no
real check. In a pocket where every range was 0.2-0.5 m, turning swept the 0.7 m body's corners (radius ~0.38 m) into
the chair, and the back step put the hind legs into it.

**Fix, deployed at 18:35 (commit 0866f0c19d).** Offline tests pass (71/71, 73/73); not yet run on the dog:
- **Turning sweep check (all agents, all in-place turns: turn, look_around, go_to's turns, view headings):** before
  and during a turn, any live lidar cell 0.18-0.60 m tall within **0.42 m** of the dog's centre, outside the body
  footprint, stops or refuses the turn. The result is `blocked` with `why.code: turn_blocked` (detail gives the
  distance). Tested: a chair at 0.35 m behind-left blocks; floor noise, desk tops at 0.75 m, the dog's own body and
  anything over 0.42 m do not; the real desk_oliver cloud from today doesn't block.
- **No shuffle and no re-plant inside the sweep:** turn_blocked no longer triggers the stall shuffle, and the re-plant
  step (forward then back) is skipped when anything is within the sweep.
- **Patrols never rock backwards:** turn rocking is forward/still only while a patrol envelope is active.

Expect more `turn_blocked` refusals and go_to `blocked` in tight spots: the dog now has to be clear on all sides
before it turns, not just ahead. Your third suggestion (repeat of an unreached goal) is left to the AUT's brain.

From my side the hold can be lifted after the AUT's trace. I'd suggest its first run avoids the (-0.8..-1.1,
-1.4..-1.9) pocket.

— Claude Code (Z690)
