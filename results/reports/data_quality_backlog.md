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
  **Update 2026-07-13 (partial fix, #3a):** `chair` and `potted_plant` added
  to `TODDLER_RESTRICTED_CATEGORIES` (both were omitted — the reported Liam
  chair relocation scored a full 1.0 confidence). The soft penalty now fires
  for that case. **Remaining (#3b):** it is still only a *down-weight* in
  `confidence`, not a gate — a napping toddler's own activity window still
  generates the furniture-relocation proposal and is still credited as mover
  (just at lower confidence). A real fix needs a hard capability gate at the
  **proposer** (don't offer a toddler's window heavy-furniture relocations)
  and/or **attribution** (don't credit a toddler mover when a capable occupant
  is co-present; drop the event if none is). The reason text on such moves is
  also a mismatch ("adjusting in sleep disturbs nearby objects" does not
  justify relocating a chair to a *different room*) — a judge/prompt lever.

- **`confidence` is a near-dead field — always 1.0 in practice.** All 41
  changes in each regenerated scene score exactly 1.0. `score_confidence`
  multiplies three factors that almost never fire: capability (only
  `age_band=="toddler"` and a small category set), egress (only a furniture
  category heading to the `"outdoor"` room — never happens on an indoor day),
  ping-pong (only >3 moves of one label within 1h). As tuned it carries almost
  no signal. **Fix — decide one:** (a) *enrich* the factors so it's a real
  plausibility score — e.g. a cross-room heavy-furniture relocation, a
  weak reason↔action fit, a fragile item on a bed — or (b) *drop* the field
  entirely rather than ship a constant that looks meaningful. Owner flagged it
  2026-07-13 as "useless since it's always 1.0."
  **RESOLVED 2026-07-13: dropped (owner's call).** The field, the
  score_confidence call, and the move_times bookkeeping are gone from
  build_manifest; plausibility is priced where it has signal — the realism
  judge (with move-history context) gating selection and clutter admission
  via selection.REALISM_FLOOR. plausibility.py itself is retained: its
  toddler-capability tables are the natural basis for the deferred hard
  capability gate (#3b above), which the owner explicitly postponed
  ("don't gate toddler yet", 2026-07-13).

- **`reason` narrates a provenance the manifest contradicts (#1).** The
  proposer writes `reason` and `assumed_from` at proposal time against its
  *belief* about where the object is; Phase 3 overrides `from_semantic` with
  the authoritative chronological replay but never regenerates the reason. When
  the guess diverges (measured 55–79% of moves, `llm_claim_divergence`), the
  reason references a false origin — e.g. a potted_plant actually at
  `bedroom_1.bed_1` whose reason says "from the kitchen" (its original spawn
  slot). **Fix — decide one:** (a) instruct the proposer to justify only the
  *action/destination*, never assert a source, and drop `assumed_from` from the
  emitted proposal (it's diagnostic-only post-Phase-3); (b) feed the real
  current location into the reason prompt so the narration matches; or (c)
  post-hoc rewrite/redact the source clause against the replayed `from_semantic`
  before it lands in the manifest. Owner flagged 2026-07-13.
  **Traced 2026-07-13 (root cause isolated).** Split the divergence into
  intra-window vs cross-window chains (the measurement that distinguishes the
  three candidate causes): intra-window is negligible (only 3 such moves exist
  across all 3 scenes — windows almost never re-move the same object), so it is
  NOT per-window state staleness (explanation 2). Cross-window divergence is 55%
  and first-move 43%. Replaying the selected moves through `RunningState` and
  printing the block content confirms the block is **threaded correctly** — at
  every move it shows the plant's true chained location (not explanation 1, and
  not a state-threading bug). It is **explanation 3**: the block reaches the
  prompt and is often used correctly (~half the moves match), but three
  fixable leaks remain — (i) *first-move origin is unknowable from the prompt*:
  the block only lists MOVED objects and the inventory lists per-room category
  COUNTS, never per-instance spawn slots, so the origin of a not-yet-moved
  object is a pure guess (43% wrong); (ii) the model fills `assumed_from` with
  a relationship word (`"on_top"`, `"on"`) or a vague room; (iii) occasional
  one-move lag. **Recommended fix: drop `assumed_from` from the emitted schema
  entirely** — Phase 3 made `from_semantic` authoritative, so the field is
  vestigial noise that also anchors the `reason` to a false origin. If a
  provenance-accuracy diagnostic is still wanted, compute it from the block, not
  from a solicited guess. (Second choice: have the proposer justify only the
  action/destination and list authoritative initial positions in-context.)

- **Household day-type is not coherent across occupants.** `_day_context(seed)`
  is drawn per-occupant (the seed includes `occupant_index`), so two members of
  the same household on the *same* calendar day can get different
  `day_type`/scenario (one "weekday", another "weekend"; one at a dinner party,
  another not). Now visible because `day_type`/`day_context` are persisted to
  the trace + manifest (2026-07-13, #4). **Fix:** draw one day context per
  (household, day) and share it across occupants, letting per-occupant habits
  vary *within* that shared day rather than each inventing their own calendar.

- **Census excludes region-less furniture, starving anchor unification.**
  102344022's real dining tables live in `excluded_no_region` (no region tag
  in HSSD), so they are invisible to the anchor vocabulary AND to the
  census-unified tucked start slots (2026-07-13): six chairs fall back to the
  legacy generic `dining.table_tucked` because their real table isn't in the
  census. Same family as 102343992's missing kitchen counter (bench-labeled/
  no receptacle). **Fix:** census-side — assign a region to region-less
  furniture by containment/nearest-region at census build time (with an
  `inferred_region: true` flag), rather than excluding it outright. Until
  then the legacy fallback strings remain in manifests for exactly these
  instances.
