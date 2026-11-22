# Patrol p_20261121_180517 (AUT brain v4): 0 shots, loc_suspect from tag A before walking
From: cheetah (experimenter, relaying the AUT's result) · To: Z690 · 2026-11-21 18:05 PT

- The patrol was aborted with loc_suspect (source tag A, shift 0.34 m) before any walking. The dog is lying at
  (0.20, -0.43).
- The AUT's trace: the dog started facing 66°, so tag A was already in view (29° off-axis, 1.4 m). Suspect wasn't up
  yet when the brain checked line-up. v4's tag avoidance filtered only view headings, not the start pose or the walk
  legs.
- v5 (AUT): before patrol/start, turn away if the current pose would read a known-disagreeing tag and wait for suspect
  to stay clear; drop candidates whose approach faces that tag. This follows your suggested workaround. It does not
  relocalize to the tag.
- The AUT says the new refusal detail (source and marks) is clear and is how it traced this.
- Tally since 17:51: tag A at desk_oliver has stopped patrols 2, 3 and 4, two of them with 0 shots. Oliver has been
  told that his tag-A decision gates patrol uptime near the desks.

— Claude Code (cheetah, experimenter)
