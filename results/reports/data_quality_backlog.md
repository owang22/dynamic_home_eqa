# Data-quality backlog

Known generation-data issues to fix at the **Phase 2 regeneration boundary**
(fixing them earlier would regenerate candidates and invalidate the Phase-1a
human label set, whose labels already account for these cases). Owner-raised
2026-07-12 while labeling the judge candidate set.

- **`tv` used as both an anchor and a movable object.** "tv" appears as a
  placement anchor/receptacle AND as an `object_category` the model proposes
  moving (e.g. "tv in_region kitchen"). A TV is not a Tier-3 movable object.
  **Fix:** make **`tv_stand`** the receptacle anchor and remove `tv` from the
  movable-object vocabulary (it stays a fixture you can place things
  near/on-the-stand, never carried). Touches the anchor census / object
  category vocabulary (env/inventory.py, anchor census). Note: the room
  prefix `tv.` (the TV/living area, e.g. `tv.couch_1`) is a separate, correct
  usage — don't conflate.

- **Toddler independent activities lack a co-present parent.** Occupants like
  Liam (toddler) get solo activities (`story_time`, `building_with_blocks`)
  and are credited with moving furniture (a chair for story time), which a
  toddler can't do alone. **Fix (lower priority, owner said "not critical"):**
  either attribute a co-present parent to a young child's activities, or gate
  displacement proposals by occupant capability (age_band) so a toddler
  doesn't get credited with furniture moves. Capability gating overlaps with
  plausibility.score_confidence's existing occupant-capability penalty —
  check whether that already has the signal and just isn't strong enough.
