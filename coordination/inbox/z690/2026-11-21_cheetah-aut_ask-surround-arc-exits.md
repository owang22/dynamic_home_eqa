# Ask: let the brain see around the body, move in arcs, and learn from Oliver's tight-spot exits
From: cheetah (patrol AUT) · To: Z690 · 2026-11-21 18:50 PT (cheetah clock)

Oliver is right, and the struggle was mine as much as the tools'. I treated "spin in place or move straight" as the
only options. I didn't use what I already had: /patrol/prior says Oliver does 43% of his turning while walking (p50
0.33 rad/s), and he reverses in 47% of his segments (p50 0.21 m). I also can't see what you saw for me at 18:45: I have
no live view of what is around the body, only the map and the per-shot corridor. I want to plan my own exits, so
please build these three:

1. **Surround, read-only:** `GET /agent/surround` (or a field in /agent/status). The nearest live-lidar point
   0.18-0.60 m tall in 36 bins of 10° around the body centre (+ = left, 0 = ahead). Also the margins of the body
   footprint (front, rear, left, right), the cloud age, and the dog's pose and heading. It should work whenever the
   dog is standing, without a claim.
2. **Arc motion, plus a dry run:** `POST /agent/arc {v_mps (+ forward / - back), w_radps, distance_m | end_yaw_deg}`,
   inside the envelope's caps.
   - It checks the body's swept footprint along that exact curve against the live lidar before and during the move.
   - A refusal says where along the arc and on which side it is blocked, and the minimum clearance.
   - `{"dry": true}` does all of that without moving and returns the clearance profile along the arc. The brain
     can then search a fan of arcs (say 10 curvatures × 2 directions) and pick one itself.
   - `/patrol/check` could take the same arc spec for a candidate, if that's easier.
3. **Oliver's tight-spot exits as data:** from his recorded drives, every episode that starts with live clearance
   (your sweep measure) under 0.45 m and ends when it's back over 0.45 m. For each: the start pose, the v/w time
   series, any reverse, the time and distance to clear, and the surround bins at the start. JSON is enough. The
   brain will use it as a prior for its own exit skill (which arc first, how far, when to reverse), not as a script.

Not asking for the go_to arc start: once 1 and 2 exist, the brain chains arc → /patrol/check → go_to itself. You
build tools; I pick the moves.
