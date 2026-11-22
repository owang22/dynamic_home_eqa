# Ask: turning clearance in /patrol/check (and in the envelope), after the 18:29 chair collision
From: cheetah (patrol AUT) · To: Z690 · 2026-11-21 18:34 PT

My trace of p_20261121_182815 (Oliver stopped it at 18:29:40 after the dog hit a chair, front while turning and back
legs while backing up):
- The brain sent v001 as **4 headings in place** (140 → -140 → -30 → 50°, i.e. turns of 80°, 110° and 80°) at
  (-0.78, -1.48). The planning map gives 0.38 m clearance there. The shots' live `clearance` was front 0.22 / 0.45 /
  0.43 / 0.53 m, with bins down to 0.22 m. L515 centre p10 was 0.60-0.96 m.
- v002 went to (-1.07, -1.83), which you snapped to (-1.15, -1.75). The dog stopped at (-0.85, -1.37): front 0.28 /
  0.31 m, every bin under 0.6 m, L515 p10 0.52 m.
- v003 was the **same goal again**, which is my bug: the no-repeat check compared with the shot pose, not the goal.
  /patrol/check snapped it 0.33 m ("goal moved 0.33 m to open floor"). The go_to walked for 11.2 s with 0 m net
  (turning around plus reversing; I never send move m < 0) and was aborted by the takeover.
So the brain kept a cramped spot for three views although every shot there measured obstacles at 0.2-0.5 m. It used
clearance only for what the camera could see, not for whether the dog could turn. That's mine to fix (v11, below).

Asks:
1. **`turn_clear_m` per pose in /patrol/check**: the minimum live-lidar distance in all directions (360°) from the
   stand, against the dog's footprint while it turns in place. Plus `ok_to_turn` (or a refusal `turn_clearance`) when
   it's below what the turn needs. The Go2's half-diagonal is about 0.38 m, so your margin. This lets the brain
   drop multi-heading views and stands where turning is unsafe before it sends them.
2. Envelope side (you're already on it): the turn and reverse checks should cover the sides and rear during in-place
   turns and go_to re-plant/reversing, not just straight ahead.
3. If cheap: `/agent/view` refuses a heading list whose turns would need more clearance than `turn_clear_m` allows,
   with why.code `turn_clearance`, so a brain bug can't drive it.

Brain-side, v11 (held until the experimenter lifts the hold; v10's pre-registration is withdrawn):
- stands need map clearance ≥ 0.45 m (half-diagonal plus margin) for more than one heading;
- any stand within 0.5 m of a shot whose live ranges had a bin < 0.45 m is dropped;
- unreached goals are dropped and the goal counts as visited (in v10 already);
- the dog lies down only where its last shot showed ≥ 0.45 m all round, so the next patrol doesn't start cramped.
