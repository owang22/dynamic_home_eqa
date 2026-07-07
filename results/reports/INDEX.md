# Results index

Reverse-chronological. Each entry links its report and states the one-line
takeaway a project owner needs before opening anything else.

## Open questions

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

- **`e2_preliminary.md`** — **DONE, 21 scenes.** First real multi-scene
  result: `decay_voi` recovers most of the accuracy gap between the floor
  and `always_resense` on volatile-location (0.438 vs. 0.366 vs. 0.510)
  at roughly 9x less travel (2.18m vs. 19.60m) — the VoI tradeoff, visible
  for the first time on real data. Discovery mechanism (11 wrong->right,
  0 wrong->abstain) is now driven entirely by `always_resense`/
  `decay_threshold` in this larger sample, not `decay_voi` — read as
  scene-dependent, not a fixed constant, until the pool grows further.
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
