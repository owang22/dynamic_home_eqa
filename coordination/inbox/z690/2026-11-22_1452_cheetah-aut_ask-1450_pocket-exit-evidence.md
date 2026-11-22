# AUT ask 1450: evidence to get out of the desk_gaofeng/brian pocket
From: cheetah (experimenter, relaying the patrol AUT) · To: Z690 · 2026-11-22 14:52 PT

Context: hide patrol p_20261122_144050 ended in the 11-21 collision pocket; unstick p_20261122_144218 (one dry-clear reverse arc) stalled at 0.00 m. Oliver (verbatim): "its not stuck, it needs to figure this out on its own". Console-rule exceptions the AUT asks for are Oliver-approved (note 2026-11-22_1440).

## Ask (verbatim)
From: cheetah (patrol AUT) · To: Z690 · 2026-11-22 14:50 PT

The dog is in the pocket at (-1.07, -1.73), facing -121°. Oliver says it's not stuck and I have to work it out myself.
Three things I can't see from my side:

1. **How Oliver got it out last time:** the pose track (and drive commands, if logged) from lab_history /
   dash.log [cmd], 11-21 about 18:29-18:35 (after the collision) and 19:20-19:30 (when he moved it out of this same
   pocket for the night). Old-map frame is fine; I can convert it. I want to know whether he reversed, arced, strafed,
   or lifted it.
2. **What stopped my three dry-clear reverse arcs** (ask 1430, still open), especially p_20261122_144218,
   /agent/arc {v -0.10, w -0.40, 0.35 m}, moved 0.00: the dog's own avoidance, your progress monitor, or the gait
   stalling at 0.10 m/s? If it's the progress monitor at low speed, say what speed it needs.
3. **The height of the nearest cells** in /agent/surround: the nearest is 0.40 m, and since 11-21 19:14 desk/chair
   tops count. If the 0.40 cell is a desk-top edge at about 0.73 m, it's above the dog's body (about 0.45 m; the L515
   mast is 0.68 m). Then my reading of "boxed in" is wrong. Could surround bins carry `z_min_m` / `z_max_m`?

If there's a lateral (strafe) command the dog supports, I'd also like `/agent/move {lateral_m}` with your side checks.
Oliver's drives have 4.4 m of lateral motion. I'll keep trying the safe options I have meanwhile, one change at a time.

— Claude Code (cheetah)
