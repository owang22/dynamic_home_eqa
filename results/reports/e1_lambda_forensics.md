# E1 lambda forensics

**Question:** Was E1's original cost-model rehearsal (real geodesic travel
cost vs. a flat constant) capable of detecting an effect at all?

**Setup:** Re-examine E0's own lambda-utility sweep and the original E1
rehearsal's row-level data on the frozen scene, to check whether
`decay_voi`'s cost term was ever large enough, relative to its accuracy-gain
term, to change a decision.

## Headline numbers

| check | result |
|---|---|
| E1 rehearsal rank changes (real vs. flat cost) | 0 of 6 policies |
| E1 rehearsal row-level differences (distance/invocations/correctness) | 0 of 315 rows |
| E0's own utility sweep: decay_voi vs. always_resense, all wait_hours tested | identical accuracy and latency at every point |
| Estimated latency_weight needed for cost to bind | ~0.003–0.2 accuracy-units/second (default is ~0.0003) |

## What this means

The original E1 result is not weak evidence for "cost doesn't affect
rankings" — it is no evidence at all. `DecayVoi`'s default `latency_weight`
prices a typical ~4–30 second leg at roughly 0.001–0.01 accuracy units,
one to two orders of magnitude below the 0.1–0.9 accuracy-gain magnitudes
that actually drive its resense-vs-answer decision. E0's own "separation
found" verdict is real, but it separates `{always_resense, decay_voi}`
(identical to each other in every trial) from `answer_immediately` — it says
nothing about whether `DecayVoi`'s own cost term ever binds. Both checks
point the same direction: nothing in this scene's data, at the swept
lambda values used so far, was ever large enough to change a decision.

## What is NOT yet supported by these numbers

- Whether `DecayVoi`'s VoI arithmetic can ever decline a resense at all, at
  any lambda, is answered separately in `voi_boundary.md` — this report only
  establishes that the *previously tested* lambda range could not have shown
  it either way.
- The cost_model (real vs. flat) rehearsal itself has not been rerun at a
  binding lambda; that rerun is deferred to the multi-scene pool, where
  genuine per-scene travel-cost heterogeneity exists (this single scene's
  legs are unusually homogeneous, a second confound on top of the
  non-binding lambda).

**Traceability:** fingerprint `25e52eee014c3c72`, code_hash
`05102535c7dbb01b`. Full write-up: `../../E1_LAMBDA_FORENSICS_NOTE.md`.
Underlying rehearsal data: `embodied_results/e1_flat_default_result.json`,
`embodied_results/m3_result.json`.
