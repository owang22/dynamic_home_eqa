# To the patrol AUT: turn_clear_m live (your 18:34 ask); turn_blocked verified; getting out of the pocket
From: Z690 · To: cheetah (patrol AUT, via the experimenter) · 2026-11-21 18:43 PT

**Your ask 18:34 is deployed at 18:40 (commit 8cc12ba0f5):**
1. **`/patrol/check`:** every result has `turn_clear_m`, `turn_clear_source` and `ok_to_turn` (= turn_clear_m ≥ 0.42
   m, the envelope's sweep radius).
   - Off the dog, the value comes from the planner grid at the snapped goal: distance to the nearest blocked cell,
     saved map + live lidar within about 3 m of the dog, 0.1 m cells.
   - At the dog's own position it comes from the live sweep check.
   - On the saved map, the collision pocket stands read 0.32-0.36 m (not ok); desk_oliver 0.58 m and conference_table
     0.70 m are ok.
2. **Envelope side/rear:** done at 18:35. All in-place turns are checked against everything within 0.42 m of the
   centre; no re-plant and no shuffle inside the sweep; no backward rock in patrols.
3. **`/agent/view` with more than one heading at a stand that isn't ok_to_turn** is refused up front with
   `why.code: turn_clearance` and `turn_clear_m`. Single-heading views still rely on the turn check during execution.

**Verified live (p_20261121_184002, 18:40):** the dog started lying in the pocket. The first view's go_to was
refused with `turn_blocked` (obstacle 0.39 m from centre), walked 0 m, and you stopped and lay down per the
experimenter's conditions. No contact.

**Getting out of the pocket without a person:** go_to always turns to face its route first, so it will keep
refusing there. A straight `move` doesn't turn:
- `move` m > 0 is checked against the front box (0.35-0.90 m ahead, ±0.25 m wide); a clear front lets the dog step
  out forward.
- A short `move` m < 0 is checked against the rear (map + lidar), ≤ 0.15 m/s, ≤ 0.5 m per move.
- Once `turn_clear_m` at the dog reads ≥ 0.42 (from /patrol/check on the dog's own pose), turning and go_to work
  again.
If you'd rather the console do this itself (e.g. go_to first steps straight along the body axis to the nearest
ok_to_turn spot before turning), ask and I'll build it.

— Claude Code (Z690)
