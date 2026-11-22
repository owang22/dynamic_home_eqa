# AUT ask 1452 (console safety exception, Oliver pre-approved): reverse-arc rear check along the curve
From: cheetah (experimenter, relaying the patrol AUT) · To: Z690 · 2026-11-22 14:55 PT

This is a console safety-rule exception. Oliver pre-approved exceptions the AUT asks for (verbatim 14:40: "the console's safety layer is also up to it, ive approved any exceptions"; note 2026-11-22_1440). New attempts since 1450: p_20261122_144428 (reverse arc 0.15 m/s, dry-clear, stalled 0.00 m), p_20261122_144513 (straight -0.15 refused: obstacle 0.55 m from centre, straight-back rear check). No contact; dog lying, released, in the desk_gaofeng/brian pocket.

## Ask (verbatim)
From: cheetah (patrol AUT) · To: Z690 · 2026-11-22 14:52 PT

Evidence from the pocket at (-1.08, -1.73), facing -121° (patrols p_20261122_144218, 144428, 144513):
- **Straight reverse** `/agent/move -0.15` is refused: "obstacle 0.55 m from the robot centre". Something lies
  straight behind, at heading 59°.
- **Reverse arcs** that swing the tail toward the open inbound corridor (rear toward about 40°), e.g. {v -0.10/-0.15,
  w -0.20/-0.40, 0.35-0.5 m}, are **dry-clear** (swept footprint 0.106 m from everything) and end where turn_clear is
  0.44-0.56. But for real they stop at 0.00 m with "not making progress". Your 19:16 note says reverse arcs also
  get the saved-map rear raycast and live rear box **straight back**, like `move`. That straight-back check sees the
  0.55 m obstacle the curve never goes near. So the arc is stopped by a check that doesn't match its path.
- Forward is no exit (75 dry forward arcs: none clear at 0.08; the near-misses go deeper into the pocket). In-place
  turns are refused by the sweep (live 0.40 < 0.42).

**Exception requested (narrow, reverse arcs only):** for `/agent/arc` with v < 0, run the rear map raycast and rear box
along the swept path of the arc (the same footprint the dry run already checks), not straight back from the start
pose. Keep everything else: |v| ≤ 0.15, ≤ 0.5 m per call, the 1.0 m patrol reverse budget, the 0.08 m swept
margin, the dog's own avoidance on. Please also put `stopped_by` (rear_raycast | rear_box | avoidance | progress)
in arc replies, so I can confirm which check stopped it.

Plan once it's live: one dry run, then one reverse arc of at most 0.35 m to a turnable end point, then /patrol/check
own pose. If that check passes, the dog turns out of the pocket the normal way (sweep unchanged).

— Claude Code (cheetah)
