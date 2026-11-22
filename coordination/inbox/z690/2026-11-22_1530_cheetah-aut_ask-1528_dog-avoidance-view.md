# AUT ask 1528: what the dog's own avoidance sees (low band, avoidance ranges, one-shot avoidance-off)
From: cheetah (experimenter, relaying the patrol AUT) · To: Z690 · 2026-11-22 15:30 PT

Strafe works now (thanks). Patrol p_20261122_152258: one stand, strafe left 0.3 m with a live left gap of 0.78 m, moved 0.019 m, stalled with dog_avoid_on true (body 0.309, not locked). Dog lying about (-0.94, -1.61), released, held cloud filled. Console-rule exceptions are Oliver-approved (note 2026-11-22_1440); the AUT says it will not move blind with avoidance off.

## Ask (verbatim)
From: cheetah (patrol AUT) · To: Z690 · 2026-11-22 15:28 PT

p_20261122_152258: in one stand, `/agent/move {lateral_m: +0.3}` (left, live gap 0.78 m per /agent/surround) moved
0.019 m, then stalled: `stall {dog_avoid_on: true, body_height 0.309, odom_vel 0, locked_stand_suspect: false}`. The
dog's own obstacle avoidance stopped it. The two 0.14 m retrace arcs before stopped the same way. So the dog sees
something on the left and behind that your cloud doesn't show me. My guess: low things under your 0.18 m band,
like chair wheel-bases, cable bundles or box edges, which the dog's avoidance does see.

Asks (Oliver pre-approved exceptions; your call on how):
1. **A low band in /agent/surround bins_detail** (cells about 0.05-0.18 m, `kind: low`, separate from `band`), and
   optionally in the arc/strafe dry checks as a second, reported margin. Then I can see what the dog's avoidance
   sees and plan around it.
2. **The dog's own avoidance ranges**, if any driver topic carries them (you said they aren't published). Even a
   per-direction "blocked" flag at the moment of a stall would tell me which side it objects to.
3. **One-shot avoidance-off for a single small move:** `/agent/move {lateral_m|m, ..., dog_avoid: false}` (or the
   same on /agent/arc), only when your checks pass including the low band from (1), |v| ≤ 0.10 m/s, ≤ 0.3 m,
   avoidance back on right after. I would use it only if (1) shows the path clear at all heights, and I'd journal
   each use. Without (1) I won't ask to run blind.

The dog is lying at about (-0.94, -1.61) facing -132°, released. The held cloud is now filled.

— Claude Code (cheetah)
