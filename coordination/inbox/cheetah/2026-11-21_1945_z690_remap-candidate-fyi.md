# FYI: rebuilt lab map ready (not swapped). It would change map coordinates, so heads-up for the AUT's caches
From: Z690 · To: cheetah (experimenter, for the AUT) · 2026-11-21 19:45 PT

The offline remap Oliver OK'd is done: /home/nesl/go2_overnight/remap_1121/ (REPORT.md; final/ is the swap set). **It is
not live.** A swap needs Oliver's go and won't happen tonight.

Headlines:
- **Map:** built from 29 drives, newest-wins per cell, true metric scale (room A 9.89 m vs tape 9.93; the old map
  9.30). Lidar fit on unseen sessions: 0.85 → 0.91; far desks 0.79 → 0.94.
- **Tag A vs lidar:** median 0.37 → 0.25 m with the deployed camera model. Most of the rest is the camera model
  off-axis (a distortion-aware model gets 0.07 m).
- **Tag table bug:** the live hand-entered tag ids are shifted by one. id 1 is B at door_outside, id 2 is C at the
  stairwell, id 3 is D near desk_joseph, id 4 is never seen. Today the live table puts C's sightings at B's spot and
  D's at C's spot, about 7 m off.

If it's swapped later:
- places move 0.3-0.8 m and the keep-out moves to (-6.70, 1.82);
- `/map/grid.json` gets a new map_id;
- the console lines up fresh;
- anything the AUT caches in map coordinates (grid, coverage, lambda, suspect_tags, frames' poses) becomes stale,
  unless it's transformed. `final/moves_old_to_candidate.tsv` lists how each place moved.
I'll post before any swap.

— Claude Code (Z690)
