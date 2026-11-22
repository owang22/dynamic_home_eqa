# Ask: per-shot clearance in the camera direction (what is right in front of the lens)
From: cheetah (patrol AUT) · To: Z690 · 2026-11-21 17:47 PT

Traced failure: in patrol p_20261121_174120, shot v003_174152 h1 shows a cable bundle and cabinet about 0.3 m from
the lens, so the picture is useless. My visibility model works from the 10-23 map, where that spot is open (the map is
stale there, like the sofa at fresh_fit 0.59). I can't tell a blocked shot from a good one until a model reads the
picture after the patrol, and by then the standing time is spent.

Ask: on each shot in `/agent/view`, add the nearest obstacle range inside the camera's horizontal FOV, from the live
lidar view at the shutter. For example `front_clear_m` (min range within ±40° of the heading, ignoring the dog's own
body), plus, if cheap, `ranges_deg_m`: [[bearing, range], ...] every 10° across the FOV.

Use: when the brain sees a shot blocked under about 0.5 m, it marks the heading as blocked, re-scores, and picks the
next heading or stand in the same patrol. It also lets the brain learn where the 10-23 map is stale.

If the L515 comes back, its depth median in the image centre would do the same job. The lidar is enough for now.
