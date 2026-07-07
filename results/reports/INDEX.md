# Results index

Reverse-chronological. Each entry links its report and states the one-line
takeaway a project owner needs before opening anything else.

## Open questions

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
