# Tag tour result + AUT ask 1416 (arrival heading, view without final turn)
From: cheetah (experimenter, relaying the patrol AUT) · To: Z690 · 2026-11-22 14:20 PT

## Result (AUT report, relayed unchanged in substance)
Tags A, C and D were reached and read; B was not. 0 collisions, 0 safety halts.
- p_20261122_141012: A at 1.07 m, D at 0.95 m, C at 1.70 m (all in the marker list).
- p_20261122_141226, 141437, 141531: B attempts plus return. No usable stand for B; return within 0.001 m / 0.14 m / 0.17 m of start; final turn to 52° refused each time.
- Refusals: turn_blocked x4 (2 final turns at start, 2 B launch views). One reverse arc dry-run "clear" was stopped for real by the dog's own avoidance.
- Dog now: lying at (0.54, -0.75), about -83°, control released, battery 90%. It is boxed in at the start spot; the AUT asks that a person turn it back to face ~52°.
- Program: tour.py v1-v4 (shas journaled before each run); brain.py stayed v15 (sha checked before every run).

## Ask 1416 (verbatim from planning/patrol_brain/study/asks/1416_arrival-heading-view.md)
Tour status: tags A, C and D were reached and read (p_20261122_141012). **B was not.** Every stand within 4 m in front
of B reads turn_clear ≤ 0.42 m: the floor there is an aisle about 0.84 m wide, so the dog can't turn in place anywhere
in it. The only turnable stand on B's side (1.01, -0.21) is 4.5 m away, and the dog couldn't get there from the start
spot: turn_clear 0.40, an obstacle 0.6 m ahead, and the dog's own avoidance stopped a 0.3 m reverse that your dry run
had called clear.

What would let me read B without breaking any rule: walk INTO the aisle already facing B, take the picture at the
arrival heading, and leave the way I came. For that I need:

1. **`arrival_heading_deg` per pose in /patrol/check**: the heading of the planned route's last segment. Then I can
   pick stands whose arrival already faces the tag (within the camera's ±40°).
2. **`/agent/view {..., face: "arrival"}`** (or `yaw_deg: null`): after the go_to, no turn at all; settle and shoot
   at whatever heading the dog arrived with, and report it. That's the same envelope, minus the in-place turn that
   the aisle can't take.
3. **Clarify the small-turn rule:** does the turn-sweep check refuse a final face turn of a few degrees? If turns
   under about 5° are exempt or checked differently, say so; I'll plan to that.
4. **Dry-run/real mismatch:** /agent/arc dry {v -0.10, w 0, 0.3 m} said clear, but the real one stopped at once with
   "not making progress (avoidance stopped it, or something is in the way)", i.e. the dog's own avoidance behind it.
   If the dry run can't know what the dog's own sensors see behind, mark reverse results as `rear_unverified`, so I
   stop trusting them.

The dog is lying at (0.54, -0.75) facing about -83° and boxed in (front 0.19 m along any arc, left edge 0.07 m,
reverse stopped by its own avoidance). I'm not trying to wriggle it out: Oliver or a person should turn it back to
face 52°, which is how he left it this morning.

— Claude Code (cheetah)
