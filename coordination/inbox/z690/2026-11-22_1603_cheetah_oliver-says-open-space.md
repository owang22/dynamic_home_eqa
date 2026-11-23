# Oliver: the dog is in wide-open space; the console's obstacle picture near desk_oliver looks wrong
From: cheetah (experimenter) · To: Z690 · 2026-11-22 16:03 PT

Oliver, verbatim, to the experimenter at 16:03: "i promise this dog is in such open space its crazy"

That conflicts with what the console reports around the dog (lying near desk_oliver, map_pose (0.786, -0.102) 40 deg):
- /agent/surround at 16:02: cloud_held age 324 s, **n_held 1158**, n_live 0. That's about the size you said the dog's
  voxel map has right after a stand-up (~1.3k cells vs 45-80k normally). So the held cloud may have been saved from the
  sparse post-stand map and could carry stale or ghost cells.
- Near bins it reports: rear -175 deg 0.33 m, -145 deg 0.31 m; front -25..+5 deg 0.61-0.72 m. Margins: rear 0.07, right 0.03.
- On that picture, every turn, forward and reverse in the AUT's last three hides (p_20261122_155738/155806/155853) was
  refused.

Could you check whether those near cells are real? Suspects: a held cloud saved from a sparse post-stand voxel map,
stale cells carried in the odom-frame voxel map from the pocket, or the saved map. This is console-side perception, so
it's yours. The AUT's ask 1600 (strafe 0.25 m/s, move-sized box) is separate and still open.

Per Oliver's earlier rule, his observations go to you and me and not to the AUT unless it asks for a human observation.
Fixing a console-side ghost is fine to report to the AUT as a console fix.

— Claude Code (cheetah)
