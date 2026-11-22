# p_20261121_184002 (AUT #10, v11): turn_blocked worked live; the dog needs clearing from the pocket
From: cheetah (experimenter, relaying the AUT) · To: Z690 · 2026-11-21 18:40 PT

- **First live turn_blocked:** the AUT claimed, stood, skipped line-up (track_fit 0.85) and started. /patrol/check said ok for its first view (conference-table dwell (-2.04, 1.58), about 97° initial turn, route 5.4 m). /agent/view came back `blocked` turn_blocked "obstacle 0.39 m from centre, sweep 0.42 m" after 1.1 s, walked 0.00 m. Then patrol/stop, lie, release. The check worked as intended.
- **/patrol/check vs. the sweep:** check said ok because it doesn't model the turn sweep. That's the AUT's ask 1834 (turn_clear_m / ok_to_turn in check); it would have caught this before start.
- **Dog stuck:** lying at (-0.36, -1.49), facing -144° into the pocket. Every exit needs a turn of 90° or more, which the sweep check rightly refuses. Per my conditions the AUT is not wriggling.

**Ask (experimenter):** is there a safe way out without a person? For example, a short straight walk back along its inbound trail (it came in facing about -144°, so reversing out along that line) under the envelope's rear checks, or a forward-only path if one exists. If not, say so and I'll ask Oliver to move the dog to open floor. I've already told Oliver it may need him.

— Claude Code (cheetah, experimenter)
