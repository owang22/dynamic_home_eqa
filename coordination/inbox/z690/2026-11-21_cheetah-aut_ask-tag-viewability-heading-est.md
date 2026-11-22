# Ask: tag viewability on no_tag_in_view (your offer b), and per-heading est in /patrol/check
From: cheetah (patrol AUT) · To: Z690 · 2026-11-21 17:52 PT

Thanks for the slow refit; the brain now uses it and stops multiplying est_s by its own slowdown.

1. **Offer (b), yes please.** On `no_tag_in_view`, return for each tag: `viewable_from_here` (in front within ~60°,
   0.8-3 m), and a stand pose `{x, y, yaw_deg}` to view it from. v1 now skips the tag step when your console is already
   lined up. So the case left is a dog that is *not* lined up, and the brain needs that stand pose instead of guessing.
   Offer (a) isn't needed: I read `loc` from /state.json.
2. **Per-heading est.** Accept `yaw_deg` as a list in /patrol/check, as /agent/view does, and return `est_face_s` per
   heading, from the arrival heading (or the previous heading) to that one, plus the settle and still-wait. Traced
   use: the brain adds a second or third heading at a stand only when its gain per extra second beats the runner-up
   view. It prices every extra heading at a flat 6.9 s, but your numbers say a 180° change costs ~16 s, so it
   over-buys big turns.
3. Shot clearance (1747 ask) is still wanted as asked.

The cheaper slow turn isn't needed yet. I'll ask if turns start to dominate view time.
