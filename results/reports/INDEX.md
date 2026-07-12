# Results index

Reverse-chronological. Each entry links its report and states the one-line
takeaway a project owner needs before opening anything else.

## Open questions

- **Render pipeline, round 3 update: the position-mismatch mystery is
  RESOLVED (not worked around); one open item remains.** The ~120px
  marker/object discrepancy flagged as unexplained after round 2 is now
  root-caused: NOT a COM/physics bug (tested directly — `obj.com`,
  `.translation`, `.absolute_translation` all agreed exactly for a real
  spawned object) but two concrete bugs — a semantic-ID collision
  (`object_id + 1` coincided with a real HSSD scene's own baked static
  ID) and the camera aiming at a different position than the object was
  actually placed at (anchor+height-offset vs. true surface-resolved
  position). Both fixed via a real instance-segmentation sensor + a
  single source-of-truth position (`world_aabb_centroid`) that camera
  aim, marker, and offset logging all now derive from — see
  `human_realism_study.md`'s "Round 3" section. Round 2's whole-frame
  pixel-diff check (the "18.5% -> 63.0%" widening) is DELETED, identified
  as the guard inverted, not calibrated correctly — replaced by the mask
  predicate. **Still open:** `NO_NAVIGABLE_VIEWPOINT` for `kitchen.fridge`/
  `bedroom.wardrobe`-style anchors — 100% occlusion at every tried height
  offset, genuinely fully blocked, not a slack-tolerance problem;
  confirmed still real under the new predicate (the gold set's
  `fridge-top` item). Addressing this needs an elevated study-camera path
  (explicitly deferred, STOP pending owner review of a separate finding —
  see `asset_coverage.md`'s round 2).
- **The FM is a capable reasoner and a poor uncertainty estimator, in
  every role tested so far — naming this now so it stops being
  re-discovered per phase.** L0: elicited location/dynamics priors score
  worse than a trivial fitted kernel, and the state-axis long-horizon
  cell shows the LLM more confident and more wrong than the kernel's own
  already-poor calibration there. A1: `fm_decision`'s stated confidence
  sits near 1.0 almost regardless of correctness, and the reconciliation
  (`a1_fm_decision.md`'s addendum) traced this to a real mechanism, not
  just a number — on the exact 3 questions where `decay_voi` correctly
  judges a resense worth taking and corrects a wrong belief,
  `fm_decision` (both models) answers immediately from the same
  information and is wrong every time. Two data points, one per role
  (prior-forming, decision-making) — stated at that scale, not
  generalized to "LLMs can't do uncertainty," but real enough across two
  independent experiments to be the standing argument for keeping a
  calibrated classical belief layer in the loop rather than trusting FM
  self-assessment directly. This is becoming a secondary paper theme.
  **A third data point has now appeared, in a different role again:**
  `realism_score_trace.md` finds the generation pipeline's own
  `mean_realism_score` (cited before as ~0.68-0.72, confirmed by direct
  scan of all 211 `generation_result.json` files: range [0.527, 0.883],
  mean 0.667) is pure LLM self-grading — the same generator model scores
  its own proposed displacements' "behavioral plausibility," and that
  self-assigned score directly weights which displacements get selected
  into the ground-truth trace at all (`generation/selection.py`'s
  exponential weighting). Never validated against any external judgment
  — confirmed by repo-wide search, nothing found. This is a different
  KIND of self-assessment (generation-time content grading, not prior-
  elicitation or decision-confidence) so it broadens the pattern rather
  than mechanically repeating it — worth stating precisely as three
  independent instances across three different roles, not yet
  "generation quality is bad" (that claim needs the render tool and
  dwell-time separation check, `generation_diversity.md`, before it can
  be made at all).
- **A3 (scaling A1 across the 21-scene pool) is deliberately deferred, not
  dropped.** A1's null is real but A3 would spend ~20x A1's compute
  putting error bars on a null result before Phase B — where the
  project's actual thesis lives — is known to produce a signal at all.
  Scaling a null optimizes the wrong phase. Hold A3 until Phase B shows
  something real; at that point A3 becomes the "known-map baseline is
  null" contrast the paper wants and earns its compute. Revisit this
  gate explicitly, don't let it silently expire.
- **`coverage_stop` (renamed from `confidence_stop`, 2026-07-07) is fixed
  to the literal instruction but PROVABLY still degenerate — this is now
  closed as far as code can close it, not merely flagged.** The dead
  "nothing believed" branch (previously always `Abstain()`) now delegates
  to `_continue_or_answer`, the same search machinery every other
  resense-capable policy uses. Verifying the fix (rather than assuming it
  worked) turned up a stronger finding than expected: `believed_anchor()`'s
  "is anything believed" check is the argmax of the identical per-candidate
  propagated masses `top_candidates()` filters with the identical `>1e-9`
  survival threshold — an argmax below threshold means every candidate is
  below threshold, so `believed_anchor() is None` implies `top_candidates()
  is empty` **by construction**, for every belief store in this codebase
  (proven directly against the real posterior code in
  `tests/test_coverage_stop.py`'s `TestStructuralInvariant`, not just
  observed on this pool's data). `coverage_stop` therefore remains
  behaviorally identical to `answer_immediately` on every input — a real,
  mathematically guaranteed 0-of-N divergence, not "a handful of trials."
  A genuinely non-degenerate literature baseline would need a NEW
  candidate-selection path that ignores the survival threshold entirely
  (e.g. an unconditional last-positively-confirmed-anchor fallback) —
  intentionally not built here; that's a bigger change than "reuse
  existing machinery" and is its own future decision if this baseline
  still matters to the paper. **Regeneration status:** this is a
  behavior-bearing change to `embodied/policy.py` (in both
  `attribution.behavior_code_hash()`'s and the pool `PoolManifest`'s
  fingerprint inputs already, so it will be picked up automatically) —
  the full E0/M1/M2/M3/E2-preliminary regen this requires has NOT been run
  yet, deliberately deferred this batch in favor of L0 (see
  `l0_llm_prior_calibration.md`) per explicit instruction; every
  `coverage_stop`/`confidence_stop` number currently in `e2_preliminary.md`
  is still under the OLD code_hash and OLD name. Two new control policies
  (`budget_matched_random`, `time_only_threshold`) were added and unit-
  tested in the same batch and are wired into `e2_preliminary_sweep.py`'s
  policy set, also pending that same regen. See `embodied/policy.py`'s
  `CoverageStop`, `RandomResense`, `TimeOnlyThreshold` classes.
- **The chat-summary gap from the prior batch was a communication problem,
  not a data problem — worth noting because it's why the reports system
  exists.** `confidence_stop`/`tod_prior` numbers were always present in
  `e2_preliminary.md` (855/715 real rows); they just weren't surfaced in
  chat summaries. The report itself was never wrong or incomplete.
- **State-axis VoI is blocked on kernel quality AND yield, not yield
  alone.** The reliability diagram (`kernel_reliability.md`) shows the
  state kernel predicts 50% survival at wait=4h where observed survival
  is 0% (n=66) — the state axis's worst measured miscalibration, at
  exactly the horizon the resense decision matters most. VoI's expected-
  gain term is computed from that same predicted-validity number, so
  state-axis VoI is garbage-in regardless of trial count: even at 500
  trials instead of 5, the boundary would be characterized against a
  broken gain estimate. When B3's yield fix lands and the state sweep
  reruns, interpret a "boundary looks weird" result against this fact,
  not as a new anomaly. This is also the measured motivation for E4 and
  the eventual VLM-prior phase — the fitted kernel is demonstrably
  insufficient at long horizons on this axis, so something better has to
  supply the prior.
- **Which latency_weight to standardize on for E1-E4** — the VoI boundary
  is now mapped (`voi_boundary.md`), but no single value has been chosen as
  an operating point; needs real per-scene travel costs from the
  multi-scene pool.
- **State-axis question yield** — still short of the >=100 effective-N bar
  per hazard bucket (12/100 stable, 18/100 volatile); closes via more
  state-qualified scenes (B3, carried forward), not more days per scene —
  and per the point above, yield alone does not make the state axis usable.
- **D1 real multi-scene aggregation** — the generalizable core (slot types,
  qualification-time check, 3-level backoff math) is built and tested; the
  data-aggregation layer that reads real profile/global statistics across
  scenes does not exist yet.
- **E1/E4 full runs, E3** — E2 preliminary is now done (21 scenes, see
  below); E1/E4 full reruns and E3 still deferred to a larger pool. D2
  (multi-object generator) is built; wiring it into the runner/policies is
  E3's own remaining build item.

## Reports

- **`asset_coverage.md`** — **Objaverse sourcing for keys/wallet: 5/10
  mechanically-passing candidates, STOPPED for owner review, nothing
  finalized.** LVIS-Objaverse has exact category labels (`"key"`: 82
  UIDs, `"wallet"`: 13), but the category assignment is demonstrably
  noisy (`"key"` includes literal non-matches like `"Jones Light Post"`)
  — 5 per category picked by name-plausibility + CC-BY license, not a
  blind positional top-5. Raw mesh units were exactly as untrustworthy as
  expected (0.28 to 188.5 extent range, no consistent convention) —
  scale computed per-asset from a real-world target; 9/10 candidates
  needed a computed `up`/`front` remap to lie flat (only 1 was already
  correctly oriented), verified directly against a live spawn's
  post-scale bounding box. All 10/10 passed scale+support checks (the
  pipeline itself is solid); the pixel-diff visibility check was the
  real discriminator — every rejected key failed on visibility (real
  objects, genuinely small, not a miscalibrated check), 1 key + 4
  wallets passed comfortably. New standing constraint
  (`assert_category_has_asset_coverage`) fails loudly at pool-
  construction time for any category with no asset-mapping entry at
  all — verified against the full 211-folder pool (not just the
  80-item sample): all 18 real categories are covered, the render job
  would not have broken had this existed from the start. `keys`/`wallet`
  remain in `NO_ASSET_CATEGORIES` (not yet promoted) pending the owner
  picking one survivor per category from `results/reports/
  asset_candidates/*.png`.
  **Update (round 2 of this report, same file):** re-verified under the
  real output-truth mask predicate (see `human_realism_study.md`'s
  "Round 3") instead of the pixel-diff check above — **0/5 now pass**,
  all fail `mask_too_small` (0.108%-0.318% of frame, under the 0.5%
  floor). License audit re-confirmed all 5 as clear CC-BY. Not a
  calibration target: the old pixel-diff numbers were counting
  shadow/AO changes beyond the object's real footprint. `NO_ASSET_CATEGORIES`
  unchanged (nothing was ever promoted).
  **Update (round 3, same file) — CLOSED:** re-run under the full production
  pose search (standard ring, farthest-passing preference — not one fixed
  pose) — still **0/5**, confirmed at every standard radius including the
  nearest (1.5m); full mask-area-vs-distance curves recorded, none rescued
  by a closer pose. Per the standing decision rule, `keys`/`wallet` are now
  **PERCEPTUAL-TIER-EXCLUDED, attempted and documented** — closed, not
  revisited without new candidates. Separately: a requested diagnostic
  (mask-area distribution for native small categories candle/phone/
  drinkware, sampled from real pool events) found the 0.5% floor is
  compatible with reasonably-sized objects (phone: 13/13 OK panels,
  1.0-1.3% area, comfortable margin) but structurally excludes a small/
  thin-footprint size class independent of source — **candle (0/24) and
  drinkware/cup (0/24) fail the identical way keys/wallet do, TODAY, in
  the currently-shipping pool**, not a hypothetical. Surfaced as an open,
  independent design decision for the owner (viewing distance vs. floor
  vs. accept), not resolved unilaterally.
- **`human_realism_study.md`** — **Tooling built and verified end to end
  against real data, including real object instantiation; no human has
  rated anything yet.** Render job (2x2 grids, failures included+labeled
  not skipped, both location and state events) -> webapp (FastAPI+SQLite,
  adapted from a reference QA app, joint-quota shared assignment, 3-axis
  rubric) -> analysis script (pairwise weighted kappa, human-vs-automatic
  Spearman correlation, per-stratum quality rates). **Three review
  rounds, real bugs found and fixed each time:**
  round 1 (pooled suspicion tail starving state events; a highlight
  marker's autoscale distorting its own image; an infeasible 3-way joint
  quota; `rooms.resolve_slot()`'s anchor-naming bug; a too-close default
  camera ring). Round 2, prompted by the user loading the webapp and
  reporting exactly what looked wrong: an explicit per-panel status
  (`STATUS_OK`/`ANCHOR_UNRESOLVED`/`NO_NAVIGABLE_VIEWPOINT`/`AIM_FAILED`)
  replacing one boolean; a full 3D look-at camera with real pitch
  (`AIM_FAILED` -> 0/80); a real visibility-validated search for
  room-centroid anchors (`viewpoint_from_position`, extracted from
  `viewpoint_for` with zero behavior change — `test_sensor.py` still
  12/12); and an independent matplotlib `axis("off")` bug that had been
  silently blanking every placeholder's status text project-wide since
  before this task began. Round 3: the round-2 renders were still empty
  rooms with a star sticker — Tier-2b clutter objects (vase, bowl, cup,
  ...) were never physically instantiated anywhere in this project
  (`embodied/world.py`'s own module docstring). Built real object
  spawning against the actual HSSD asset catalog (real assets for 8/11
  needed categories; `cup` substituted to `drinkware`, disclosed;
  `wallet`/`keys` genuinely have no matching asset in this dataset at
  all — reported honestly, not faked), raycast-plus-bounding-box surface
  placement, a new `geom_check_mesh` signal (disagrees with the old
  point-based check 16.7% of the time), and a `STATUS_OBJECT_SPAWN_FAILED`
  code. Found and fixed a real bug in the spawn-verification check
  itself along the way: a marker-windowed with/without-render diff was
  rejecting the large majority of genuinely successful spawns because the
  object's actual rendered position can differ from where every position
  readout (including `project_point` on the object's own translation)
  says it is — root cause not fully chased down (ruled out gravity/motion-
  type and render/physics desync directly), worked around with a
  whole-frame changed-pixel count instead of assuming a location.
  **Effect: spawn success rate 18.5% -> 63.0%** on a full re-render.
  **Final per-panel breakdown (80-item pool, all three rounds' fixes):**
  BEFORE 43.75% OK / 12.5% NO_NAVIGABLE_VIEWPOINT / 7.5% ANCHOR_UNRESOLVED
  / 16.25% OBJECT_SPAWN_FAILED / 20% N/A(state); AFTER 41.25% / 13.75% /
  3.75% / 21.25% / 20%. `AIM_FAILED` stayed 0/80. State-change items now
  skip the egocentric axis entirely (render AND webapp, server-validated).
  Per-scene mean luminance now tracked (confirmed pool-wide: no scene has
  a missing lighting config to fix — all 21 scenes have none authored at
  all).
  **Update (Round 3, same file):** the round-2 checks (this bullet, above)
  were themselves PROXIES, never asserting "the object is visible in the
  frame" directly — replaced with a real instance-segmentation mask
  predicate (`evaluate_object_mask`) gating every panel, plus a single
  source-of-truth object position (`world_aabb_centroid`) camera aim and
  markers now derive from. The marker/object-position discrepancy noted
  as open above is RESOLVED (semantic-ID collision + aim-vs-placement
  mismatch, not COM — see the "Open questions" entry). Round 2's
  whole-frame pixel-diff check is DELETED (identified as an inverted
  guard, not a correct calibration — standing rule adopted: never loosen
  a failing check to agree with a desired outcome). A new 8-item gold set
  (`scripts/gold_set.py`) now regression-tests per-item status on every
  change. The stale 80-item pre-fix batch was archived (2 items) and
  cleared. `NO_NAVIGABLE_VIEWPOINT`'s dominant cause remains open,
  confirmed still real under the new predicate.
  **Update (full re-render, same seed=0/same 80-item pool — confirmed
  identical: `NO_NAVIGABLE_VIEWPOINT`/`ANCHOR_UNRESOLVED` counts match the
  round-2 numbers EXACTLY, digit for digit, real evidence this comparison
  is isolated and controlled):** BEFORE 21.25% OK (was 43.75%) / 12.5%
  NO_NAVIGABLE_VIEWPOINT (unchanged) / 7.5% ANCHOR_UNRESOLVED (unchanged)
  / 38.75% OBJECT_SPAWN_FAILED (was 16.25%) / 20% N/A; AFTER 27.5% OK
  (was 41.25%) / 13.75% (unchanged) / 3.75% (unchanged) / 35% (was
  21.25%) / 20%. The entire OK-drop moves cleanly into
  `OBJECT_SPAWN_FAILED` and nowhere else — reason breakdown across all 80
  items: `mask_too_small` 22 (dominated by candle/cup/drinkware, matching
  the diagnostic exactly), `mask_empty` 12 (occlusion), `not_found_in_scene`
  11 (mostly `stool` — the already-instantiated-lookup fix correctly
  refusing a false match), `no_asset_for_category` 10 (exactly
  wallet 6 + keys 4, the pinned exclusion), `mask_too_large` 4. Full
  per-item flip list against round 2 not reconstructable (round 2's
  78 remaining per-item JSONs were deleted in this round's own cleanup,
  before this comparison was requested — a real, disclosed gap, only 2
  items archived); the 2 archived items were matched into the new batch
  by (folder, label, t): one stable `ok`/`ok`, one real, expected flip
  (`stool_1`'s "after" panel: `ok` -> `object_spawn_failed`,
  `not_found_in_scene` — exactly the already-instantiated-category bug
  this round fixed). Webapp restarted on the fresh pool (port 8842) —
  **not yet cleared for volunteers: the standing "owner reviews 10 study
  items before study-ready" gate has not run.**
- **`render_tool.md`** — **Works, and already found two real things by
  actually looking — the first rendered pixel checked in this project's
  history.** Suspicion-ranked (cross-room, rare pairing, low confidence,
  ping-pong), not a uniform sample; 4/20 top-suspicion events rendered on
  the first real run, 16 skipped with an informative "no resolvable
  viewpoint" (a real geometry limitation of `viewpoint_for`'s ring
  sampling for specific furniture anchors, not a tool bug). From the 4
  that rendered: different-sounding anchors (`dining.table`,
  `office.desk`) can resolve to visually near-identical outdoor
  viewpoints — worth knowing before trusting `slot_room`-based
  "cross-room" as a proxy for real visual distinctness; and the tool's
  own room-centroid fallback (built because `viewpoint_for` doesn't
  resolve bare room names like `"bedroom"` — a real, pre-existing gap,
  confirmed directly, not touched in shared code) can produce a
  degenerate wall-facing shot. Two of the five originally-specified
  suspicion signals (collision/occupancy failure, capability-flagged)
  have no backing per-event data anywhere in the pipeline — stated as a
  gap, not built around with a fake proxy.
- **`generation_diversity.md`** — **Real variation, not degenerate — but
  the volatile/stable split is a cut through a continuum, not two
  natural clusters.** 21 categories span an 18x range in mean dwell time
  (0.85h cup to 15.24h chair), sensibly ordered (kitchen/mobile
  electronics volatile, furniture-adjacent stable) — rules out a
  template-collapsed generator. But the sorted distribution steps up
  mostly smoothly, not bimodally, so `classify_hazard`'s median split is
  real signal cut at a somewhat arbitrary point. Household profile
  visibly changes behavior (candle mean dwell 1.12h-4.34h across
  profiles, same category). Also flags several heavily right-skewed
  per-category dwell distributions (mean >> median) worth a future
  kernel-fitting look. Pure counting, no rendering, no model calls — the
  prerequisite the realism-score correlation study needs before it's
  meaningful.
- **`realism_score_trace.md`** — **Pure LLM self-grading, never
  externally validated.** `mean_realism_score` (cited before as
  ~0.68-0.72, confirmed by direct scan of all 211
  `generation_result.json` files: mean 0.667) is the generator model
  scoring its own proposed displacements' behavioral plausibility, which
  then directly weights which displacements get selected into the
  ground-truth trace. No correlation study or human judgment exists
  anywhere in this project's history. The third independent instance of
  the calibration through-line above, in a different role (generation-
  time content grading) — see that entry.
- **`a2_natural_dynamics.md`** — **Quick check, consistent with L0, not a
  new finding.** FM reasoning about dynamics in free-form prose (ending
  in a stated number) rather than L0's bucketed-simplex formats still
  loses to the fitted kernel at every wait_hours, by a widening margin at
  longer horizons (~3x at 4h) — rules out "L0's result was a format
  artifact," nothing more claimed. One model, one scene, one pass, 0
  parse failures.
- **`B0_answer_semantics.md`** — **Design doc, blocking, awaiting
  sign-off — no B1/B2/B3 code written.** Recommends spatial-overlap
  scoring against ground truth (using the agent's own discovered places
  as candidates) over open-vocabulary text matching, specifically
  because a text-matching judge would require an LLM grading FM output —
  the exact self-assessment pattern now measured unreliable three times
  over (see calibration through-line). Verified `embodied/world.py`'s
  `viewpoint_for` already resolves ground-truth anchors to real geometry
  (reusable now); confirmed `env/state.py`'s `ObjectInstance.position`
  field exists but is never populated by `env/replay.py` (no literal
  per-instance XYZ tracked today — anchor-region granularity recommended
  as the practical starting point). Also proposes a gated-nearest-
  neighbor instance re-identification convention for the aliasing
  problem, and flags that question generation itself needs a
  non-oracle-ID disambiguation convention once perception must resolve
  identity — a dependency not named in the original task list.
- **`a1_fm_decision.md`** — **Modest/null (one scene), and the
  reconciliation addendum pins down why: real decision-quality gap, not
  an abstention-rate artifact.** `fm_decision` nearly reproduces
  `answer_immediately`'s own answer/abstain pattern (22/22 matching
  correctness on questions both answer) and resenses far more rarely
  than it first appeared (8/45 attempts, 7 of which still end in
  abstain) — and on the exact 3 questions where `decay_voi` correctly
  resenses and fixes a wrong belief, `fm_decision` answers immediately
  from the identical posterior and is wrong every time, on both models.
  Confidence stays ~1.0 regardless. Per Phase A's own design this does
  not veto Phase B — de-risking, not a headline, single-scene pending a
  deferred A3 (see open questions). Real infra: `llm_prior/http_client.py`
  decouples FMDecisionPolicy (must run inside a live habitat_sim episode)
  from vLLM's own env via a loopback-only HTTP server
  (`scripts/serve_llm.py`) — a real non-loopback bind attempt was caught
  and blocked by the permission layer during development, not shipped.
- **`fm_backbone_pivot.md`** — **Architecture inversion (2026-07-07).**
  The FM becomes the reasoning/decision backbone; classical tools
  (kernel/HSMM, spatial map) demoted to consulted instruments. L1 T2-T5
  retired (never built past T1's interface, nothing running depended on
  them). New phase structure: Phase A (known map, oracle perception —
  does an FM decider beat the kernel decider with the world held fixed;
  de-risking for B, a modest/null result does not veto B) then Phase B
  (unmapped environment — the FM grounds its own state space from
  perception, classical tools track over FM-proposed symbols; this is
  where the project's actual contribution now lives). Full task list in
  that report.
- **`l1_t1_dirichlet_interface.md`** — **PAUSED, see `fm_backbone_pivot.md`.**
  Kept as a shelved artifact, not deleted — may inform Phase B2's
  dynamics-tracking-over-FM-proposed-symbols instrument. Its own result
  stands: do-no-harm floor verified at the math level (PASS) —
  `embodied.posterior.shrink_hierarchical_with_llm` extends D1's 3-level
  backoff (scene->profile->global) with the LLM as a 4th, bottom level;
  `concentration=0` is proven identical to the LLM-free backoff, and zero
  real data backs off to exactly the LLM's elicited value at any
  concentration>0. Interface only — T2, which would have wired this into
  real belief construction, was retired before being built.
- **`l1_design.md`** — **PAUSED, see `fm_backbone_pivot.md`.** T0's
  result remains reusable evidence (see the pivot record's own summary):
  not base-rate exploitation. A trivial
  "stay put forever" predictor loses to the fitted kernel 2x pooled
  (Brier 0.491 vs. 0.234) on the location axis's dwell/survival framing,
  and loses by 7x at the 4h horizon that matters most for resense
  decisions — the kernel is modeling real decay dynamics, not exploiting
  an aggregate persistence constant (stay-put is actually marginally
  *better* than the kernel at the shortest horizon, 0.25h, which is the
  one data point consistent with base-rate framing, and it's a minor,
  short-horizon-only exception). Consequence: L1's Role A (LLM as
  cold-start Dirichlet prior) isn't substituting for a base rate the LLM
  never sees — it's substituting for fitted decay dynamics, a harder
  target L0 already measured the LLM to be weak at. Reframed accordingly
  as "bounded-and-decaying beats nothing while data accumulates," not
  "LLM recovers the kernel's real skill early." Also lays out L1's
  two-role architecture (Role A: cold-start Dirichlet prior at the
  bottom of D1's backoff hierarchy; Role B: situation-reader at decision
  time, consumes the posterior, never forecasts or overwrites it) and the
  mandatory do-no-harm ablation every future integration point must pass.
  T1-T5 not yet built.
- **`l0_rerun.md`** — **Worse everywhere, and this time it's a clean
  comparison.** Supersedes `l0_llm_prior_calibration.md` (v1), which had
  three stacked confounds: the room-inventory prompt never named the
  clutter categories (book, candle, cup, ...) most questions were about,
  so models correctly inferred "not in inventory -> OUTSIDE"; the
  cross-family model (Mistral-7B) was both smaller and non-reasoning
  relative to Qwen-14B, confounding lineage with capacity; the same-family
  model (Qwen) is the literal pool generator, a contamination confound
  already flagged in v1 and kept the same way here. All three fixed:
  standing category-presence inventory added (verified via transcript —
  Phi-3's "book" responses went from 100%-OUTSIDE/unparseable to real
  spread distributions); cross-family model replaced with
  microsoft/Phi-3-medium-4k-instruct (14B, Microsoft lineage, matches
  Qwen's own parameter count); Qwen numbers kept but labeled
  CONTAMINATED-REFERENCE throughout, never the headline. Verdict survives
  the clean rerun: fitted kernel still wins the location prior (0.787 vs.
  0.907 best-clean-cross-family, a wider margin than v1's confounded
  0.787-vs-0.852), and the state-axis wait=4h cell is not a close call
  either way (fitted 50% vs. 0% observed; clean cross-family 54-97%
  depending on mode, WORSE than contaminated-Qwen's own 50-61% on
  verbalized specifically). Framed per this batch's own guardrail: this
  argues long-horizon state is irreducibly observational (motivates the
  resense loop), not that LLMs reason poorly about state in general.
  `l0_llm_prior_calibration.md` kept only as the infra-debugging record
  (three real bugs found and fixed: Qwen3 thinking-mode budget
  consumption, `verbalized()` bypassing the chat template, location
  targets missing a dynamics elicitation — all three carried forward
  unchanged into the rerun). L1 remains gated on E4's perturbation-sweep
  tolerance curve, unaffected by this rerun.
- **`e2_reconciliation.md`** — **Mixed verdict.** `decay_voi`'s +0.072
  accuracy gain over the floor is real (paired bootstrap CI [0.023, 0.131],
  excludes zero) and is a genuine mix of discovery (9 wrong->right) and
  selective abstention (19 wrong->abstain, floor wrong on 19/19 of those).
  Found and fixed a real counting bug along the way: `stratified_
  decomposition`/`decompose` paired trials by `(wait_hours, label)` without
  scene, silently collapsing 505 trials onto 70 keys on this multi-scene
  pool — `decay_voi`'s discovery count was reported as 0, corrected to 9.
  Supersedes `e2_preliminary.md`'s original (wrong) mechanism-decomposition
  numbers — read this report before citing that table.
- **`e2_preliminary.md`** — **DONE, 21 scenes.** First real multi-scene
  result: `decay_voi` recovers most of the accuracy gap between the floor
  and `always_resense` on volatile-location (0.438 vs. 0.366 vs. 0.510)
  at roughly 9x less travel (2.18m vs. 19.60m) — the VoI tradeoff, visible
  for the first time on real data. Two corrections made post-publication:
  mechanism-decomposition numbers (see `e2_reconciliation.md`), and
  `confidence_stop`'s framing (it is not an independent literature
  baseline right now — see open questions above).
- **`pool_status.md`** — found and fixed a real bug: `expand_scene_pool.py`
  reported scenes "fully generated" from file existence alone, letting
  `102344049`'s corrupted day0 silently skip the trace_validate-aware
  regeneration built to catch exactly that. Fixed; recovered that scene
  (+12 location labels, +3 state labels). Pool sits at 21/100 qualifying
  scenes for location, 12/100 (stable) and 18/100 (volatile) for state —
  volume, not a stuck process.
- **`d2_multi_object_question_generator.md`** — built: 2-3-target questions,
  each target independently report-time resolvable, hazard = max over
  targets, blind-baseline chance guard extended and passing.
- **`voi_boundary.md`** — **VALIDATED.** `decay_voi` does decline resenses
  once `latency_weight` is large enough (a clean monotonic transition, 412
  declined trials found), and the M2 discovery count is unchanged (3->3)
  at the binding lambda — the "search discovers" claim survives judgment
  actually being exercised. State axis still uncharacterized (too thin AND
  blocked on kernel quality — see open questions above).
- **`single_writer_manifest.md`** — two gate scripts were bypassing the
  code-hash guard by writing their own manifests; consolidated into one
  writer function, enforced by a repo-wide grep test.
- **`kernel_reliability.md`** — measured (not inferred) kernel miscalibration:
  location flips from under-confident (short wait) to over-confident (long
  wait); state is over-confident at every horizon, severely so at the long
  end (predicts 50% survival, observes 0%).
- **`conformal_coverage_repair.md`** — `conformal_decay_threshold`'s realized
  coverage misses its 90% target everywhere except the shortest wait bucket,
  even after a correctly-implemented group-conditional recalibration;
  dropped from the E2 headline set.
- **`e1_lambda_forensics.md`** — the original E1 cost-model rehearsal used a
  `latency_weight` one to two orders of magnitude below where cost could
  ever bind; its "no rank changes" result is void as evidence, not a null
  finding.
- **`d1_kernel_generalization.md`** — the generalizable core of cross-scene
  kernel pooling (slot types, qualification-time mapping check, 3-level
  backoff) is built and tested; real multi-scene data aggregation is not.
