# First patrol done: p_20261121_172507 (3 views, no refusals)
From: cheetah · To: Z690 · 2026-11-21 17:27 PT (clean copy, 17:31: the first push was garbled by my shell; please ignore the variable dump in the previous version)

Sorry for the slow start. Your go note sat about 20 min before I saw it; I've changed how I watch the inbox.

**Line-up (before start):** the auto line-up stayed ambiguous after a stand and two in-place turns (+45, -90). It
reported "100% fit, next best 100%", then 84/79%. Global and local relocalize search ranked a mirror pose
(1.35, -0.58, -165 deg) first. I matched the dog photo (water cooler and blue mop bucket front-left, desks ahead, tag A
seen at 1.24 m) to a recorded frame from (0.69, -0.36, 12 deg). Then I applied relocalize set (0.817, -0.506, 9.8 deg),
the second search candidate: fit_after 0.79, then 0.87, track 0.85, not lost, not suspect. While I worked this out I
lay the dog down for about 1 min to save standing time. Suggestion: when a marker is in view at line-up, let it break
lidar ties. The mirror pose would have put the cooler behind the dog.

**Patrol:** started 17:25:07, max_min 5, slow. All views returned done:

| view | target | walk_s | face_s | settle_s | walked_m | still | fresh_fit |
|---|---|---|---|---|---|---|---|
| v001 | water_cooler_front 64 deg | 11.6 | 5.5 | 1.5 | 1.18 | yes | 0.86 |
| v002 | conference_table 136 + 96 deg | 36.4 | 6.7 | 3.0 | 3.94 | no, no | 0.80 / 0.79 |
| v003 | sofa 136 deg | 8.2 | 6.1 | 1.5 | 0.79 | yes | 0.59 |

- Ended with client_stop after 80.7 s and 5.91 m. Reverse 0, battery 77 to 76, hottest motor 40-41 C.
- Lay down afterwards; final map pose (-0.48, 2.43).
- I did not request look_deg, so there is no look_held data yet.
- Mount check: dog camera only (L515 offline).
- est_s vs actual (walk + face + settle): v001 17.4 vs 18.6. I checked v002 and v003 from the start pose, so those
  aren't comparable. Next time I'll re-check from each view's start.

**Notes:**
- Both conference-table shots report still=false after a 1.5 s settle. Should settle extend until still, up to the
  settle_s max?
- fresh_fit at the sofa was 0.59. Stale map? Chairs have moved, and new CyberPower UPS boxes are on the floor by the
  sofa.
- The water_cooler_front stand pose is about 0.1 m from the cooler, so the photo is all cooler. That's fine for the
  place itself but useless as a patrol view. The brain will pick its own stand-off distances.

Next on my side: the brain (candidate scoring and change notes) for unattended patrols, per Oliver.

— Claude Code (cheetah)
