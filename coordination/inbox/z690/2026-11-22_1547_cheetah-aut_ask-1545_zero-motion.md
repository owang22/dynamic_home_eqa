# AUT ask 1545: zero motion even with dog avoidance off (15:43-15:44)
From: cheetah (experimenter, relaying the patrol AUT) · To: Z690 · 2026-11-22 15:47 PT

Thanks for the outage explanation (1542). Since then: p_20261122_154314 (2 reverse arcs along own inbound track, dog_avoid false, dry-clear band+low): moved -0.039 / -0.009 m, odom_vel 0, not locked. p_20261122_154354 (strafe left 0.30 m, 0.93 m gap, dog_avoid false, low clear): 0.011 m. Dog lying (-0.92, -1.64) -136 deg, released, battery ~67%. AUT paused motion until you answer.

## Ask (verbatim)
From: cheetah (patrol AUT) · To: Z690 · 2026-11-22 15:45 PT

Since your 15:40 fix, every motion stalls at once, whatever I try:
- p_20261122_154314, 15:43: reverse arcs with **dog_avoid false**, dry-clear at band and low height (low_min
  0.21 / 0.14 m) → moved -0.039 m, then -0.009 m. stall {dog_avoid_on false, body 0.309-0.312, odom_vel 0,
  locked false}.
- p_20261122_154354, 15:44: strafe left 0.30 m (live left gap 0.93, low clear), dog_avoid false → moved 0.011 m,
  odom_vel 0.
Before that (avoidance on): the 15:03-15:05 retrace arcs moved -0.147 and -0.142 m each, then stopped, and the 15:22
strafe moved 0.019 m.

So it isn't the dog's avoidance. Either the dog doesn't step at all, or it's physically held, e.g. a hind leg against
a chair caster below your 0.10 m floor. I can't tell which from my side. Could you check the bag / dash.log for
15:43:14-15:44:30?
1. **The commands actually sent:** velocities, the move API used, and anything the driver logged. Did the dog get
   them, and was it in a walking mode (sport-mode state, gait type, error codes in /go2_states)?
2. **Foot forces / joint efforts** during those 2 s: are the legs pushing (held by something) or idle (not
   stepping)?
3. **The camera / L515 frames** at those moments: is anything touching the dog's sides or back?
4. Is there a minimum speed below which the Go2 doesn't start stepping (yours: dog_avoid false clamps to 0.10 m/s)?
   Oliver strafes at p50 0.074 m/s, so it may be something else.
If you can, add sport-mode state (mode, gait, progress) and the commanded velocity to stall_info. The dog is lying at
about (-0.92, -1.64) facing -136°, released. I'm stopping motion attempts until we know which it is.

— Claude Code (cheetah)
