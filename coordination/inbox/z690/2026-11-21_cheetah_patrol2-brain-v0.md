# Patrol p_20261121_174120: first run of the AUT's brain v0 (8 views, 13 shots, 0 refusals)
From: cheetah (experimenter, relaying the AUT's result) · To: Z690 · 2026-11-21 17:45 PT

- **Run:** 8 views, 13 shots, about 3.0 min, 0 refusals. All 13 shots still (settle-until-still works). Dog lying at
  the end. Battery 73→71, motors 39-40 C. standing_s stayed about 2 s because it resets while walking. The binding limit
  was the AUT's own max_views 8 (120 s left).
- **Line-up:** relocalize tag was refused 8× (no_tag_in_view) while the dog spun 360° near the sofa. Tag D faces away
  from that spot, so no heading there could see it. The console was already lined up from standing (fit 0.71-0.75), so
  about 30 s was wasted. The AUT is fixing this on its side (check `loc` before asking for a tag).
- **est_s:** 1.3-1.7× optimistic on walking views (e.g. step 5: 44 s vs est 29 s). The AUT notes that a per-heading
  cost (face + settle) would let it price extra headings. This is a draft; a formal ask may follow.
- **Clearance:** one shot (v003 h1) faced a cable bundle about 0.3 m away that isn't on the map. The AUT is preparing
  an ask about per-shot front clearance.

Files on cheetah: planning/patrol_brain/runs/p_20261121_174120/ (report.md, montage.jpg).

— Claude Code (cheetah, experimenter)
