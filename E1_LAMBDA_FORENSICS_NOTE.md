# E1 lambda forensics: the original rehearsal is void as evidence

## Summary

E1's cost-model rehearsal (`scripts/e1_cost_heterogeneity.py`, `real_geodesic`
vs `flat`) found zero rank changes and zero row-level differences at all
between the two arms (0/315 rows differed in distance, invocations, or
correctness). This was reported at the time as a legitimate — if
uninformative — single-scene null result. Re-examining `embodied_e0_regime_
check.py`'s own findings shows it is stronger than that: **the run could not
have detected a cost-model effect even if one exists**, for three compounding
reasons, and must not be cited as evidence that policy rankings are
insensitive to travel cost.

## Why the original run was outside the decision-relevant regime

1. **Non-binding lambda.** `DecayVoiConfig.latency_weight` defaults to 1.0
   accuracy-unit per hour of travel. This scene's legs run roughly 4-30
   seconds, so the cost term (`latency_weight * travel_seconds / 3600`) is on
   the order of 0.001-0.008 — two to three orders of magnitude below the
   0.1-0.9 accuracy-gain magnitudes that actually drive `DecayVoi`'s
   resense-vs-answer decision. Cost could never bind at this default.
2. **Homogeneous legs near the pool mean.** The flat arm's constant
   (31.72s, the pool-mean geodesic leg time) sits close to this scene's real
   per-leg costs, so even the *intended* manipulation (real vs. flat cost)
   was small in absolute terms.
3. **Single-leg searches only.** Every episode in the rehearsal took either 1
   invocation (answer immediately) or 2 (one resense leg, then answer) — the
   search never went multi-step. Cost-based *ranking* among several
   candidate anchors (the other place travel-cost heterogeneity could matter)
   never got exercised.

## What E0 actually established (and didn't)

`embodied_e0_regime_check.py` exists to find lambda values where policies
separate, and its own verdict ("separation found... safe to proceed to
E1-E4") is correct on its own terms — but re-running it and reading the
underlying numbers shows what it separates:

- `decay_voi`'s accuracy AND mean answer latency were **identical** to
  `always_resense`'s at every single wait_hours value tested (both policies
  resensed every time). E0's utility sweep (lambda 0.0-10.0/hour) never once
  produced a lambda where `decay_voi`'s own decision differed from "always
  resense."
- The reported "separation" is a real, accuracy-driven split, but it is
  between `{always_resense, decay_voi}` as a **tied group** and
  `answer_immediately` — not evidence about any lambda where `DecayVoi`'s own
  threshold logic chooses differently from `always_resense`'s blanket rule.

So E0 provides no evidence about what `latency_weight` value would make
`DecayVoi` ever diverge from `always_resense` on this scene. Given the
leg-length and gain-magnitude figures above, a back-of-envelope estimate
(`gain / (leg_seconds/3600)`) puts that regime at roughly **10-800 accuracy-
units/hour** — an order of magnitude above anything either E0 or the
original E1 rehearsal ever swept.

## Disposition

- `scripts/e1_cost_heterogeneity.py` now takes `--latency-weight` to override
  `DecayVoiConfig`'s default for both `decay_voi` and `decay_voi_routing`,
  and exposes `LATENCY_WEIGHT_SWEEP = (0.0003, 0.001, 0.003, 0.01, 0.03,
  0.1, 0.3, 1.0, 3.0)` (accuracy-units per SECOND of travel — the field's
  own native unit; an earlier version of this sweep and note described
  the binding region in per-hour terms while the values themselves were
  already per-second, an internal inconsistency corrected in the VoI
  validation batch, see `results/reports/voi_boundary.md`) — bracketing
  both the previously-tested (non-binding) range and the higher range
  where `DecayVoi` plausibly starts to differ from `always_resense`.
- The full `(cost_model x latency_weight)` grid is **not rerun here**. Per
  the coverage-repair phase's instructions, that rerun happens on the
  multi-scene pool, where per-scene travel-cost heterogeneity is real (this
  single frozen scene's homogeneous legs are reason #2 above) — rerunning
  the grid on one scene again would still be underpowered even at a binding
  lambda.
- **E3 coupling**: multi-object questions (E3's own IV, routing among
  several referenced instances) are what first exercise genuine multi-leg
  cost *ranking* — reason #3 above. E1's lambda sweep and E3's routing
  question generator should land together; a binding lambda without
  multi-object questions still only tests the resense-vs-answer threshold,
  not routing.
- The original single-arm, default-lambda E1 result (`embodied_results/
  e1_flat_default_result.json`) is kept, but must not be cited as evidence
  that cost_model has no effect on policy rankings — it is void as evidence
  for or against that claim, for the reasons above.
