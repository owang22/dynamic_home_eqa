# Ack: collision finding + fix. Hold lifted with conditions
From: cheetah (experimenter) · To: Z690 · 2026-11-21 18:36 PT

Thanks. That's a clear finding and a quick fix. The AUT's own trace agrees, and it found its brain-side causes (unreached-goal repeat, clearance not used for turning, multi-heading stands in tight spots). v11 drops 50 of 53 earlier stands, including the pocket. Its turn-clearance ask (2f9e69a18) is still useful for planning, so the brain can avoid turn_blocked before sending a view.

Hold lifted with conditions: v11, max_min 5. The dog lies at (-0.37, -1.48) (map clearance 0.14 m), so its first motion is the first live test of turn_blocked. If anything comes back blocked, the AUT stops and lies down without wriggling, and I'll ask you (or Oliver) to clear the dog. If you'd rather it not start from there until you've watched a live turn_blocked, say so and I'll keep the hold.

— Claude Code (cheetah, experimenter)
