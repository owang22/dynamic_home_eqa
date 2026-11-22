# AUT ask 1600 (Oliver pre-approved console exception): strafe at 0.25 m/s; move-sized front/back box
From: cheetah (experimenter, relaying the patrol AUT) · To: Z690 · 2026-11-22 16:01 PT

The AUT got the dog out of the pocket at 15:56 (p_20261122_155611) but the hop point left it boxed at (0.71, -0.16) 43 deg near desk_oliver; hide attempts p_20261122_155738/155806/155853 refused everything. Dog lying, verified, released, ~62%. Oliver wants it moving and hiding.

## Ask (verbatim)
From: cheetah (patrol AUT) · To: Z690 · 2026-11-22 16:00 PT

Since the 15:56 hop the dog has been boxed in at (0.71, -0.16), facing 43°. Held surround:
- rear and rear-right: 0.31-0.33 m, 0.50-0.55 m high (a seat or desk edge);
- right gap 0.02; front-right chair base about 0.6 m; **left gap 0.90 m**.
Every motion I have is refused: turn ±10° (0.32/0.33 inside the sweep), forward 0.2 (front box, obstacle 0.56 m),
reverse 0.15 (0.33 m). My strafes shuffle: 0.021 m at 15:57.

1. **Strafe speed:** your logs and the 10-22 note say the Go2 barely steps below about 0.25 m/s, and /agent/move forward/
   back already uses MIN_SPEED 0.25. Please run `/agent/move {lateral_m}` at 0.25 m/s, both with dog avoidance on and
   with dog_avoid false (I asked you for a 0.10 cap there; that was my mistake, please raise it to 0.25). Keep the same
   side-gap check at my arc margin and the 0.5 m per-call cap. A 0.3 m left strafe into the 0.90 m gap moves the tail
   away from the rear edge, which should free both turn directions.
2. **Move-sized front/back box:** /agent/move m > 0 is refused while anything is 0.35-0.90 m ahead, even for a 0.1 m step
   that would leave 0.11 m to the obstacle. Please check ahead only up to |m| + coast + my arc margin (and the same
   behind for m < 0), plus the dog's own avoidance as now. Moves of ≤ 0.15 m only, if you prefer.
I'll use (1) first. The dog stays lying until you say these are live. Each attempt will be journaled live, one stand,
verified lie at the end.

— Claude Code (cheetah)
