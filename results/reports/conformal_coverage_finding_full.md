# Conformal coverage finding: distribution-free staleness guarantees hold only at short horizons

## Summary

`conformal_decay_threshold` — a `DecayThreshold` variant whose theta is
split-conformal calibrated for 1-alpha realized coverage instead of hand-picked
— was dropped from E2's headline policy comparison. After fixing two real
calibration bugs (a state-axis key mismatch, then a calibration-vs-deployment
statistic-space mismatch — see `embodied/belief.py`'s
`calibrate_conformal_theta` docstring), realized coverage still missed its
target at every swept `wait_hours` value except the shortest (0.25h), on both
the location and state axes. This is not a residual bug: two independent
follow-up checks ruled out the two most likely calibration-side explanations,
leaving kernel misspecification at longer horizons as the residual cause — a
finding about the belief model, not a defect in the calibration code.

## The numbers

Global theta (pooled across all natural calibration dwell events), checked
per `wait_hours` bucket on held-out (eval-day) data, alpha=0.1 (target
coverage 0.90):

| axis     | wait=0.25h | wait=0.5h | wait=1.0h | wait=2.0h | wait=4.0h |
|----------|-----------|-----------|-----------|-----------|-----------|
| location | 0.902 OK  | 0.686 MISS | 0.569 MISS | 0.436 MISS | 0.235 MISS |
| state    | 0.424 MISS | 0.303 MISS | 0.121 MISS | 0/66 trusted | 0/66 trusted |

Coverage declines **monotonically** with `wait_hours` on both axes — the
signature of a dwell-time covariate shift: calibration scores come from
natural historical dwell events (median ~1.1h for location, ~0.7h for state;
82% of location's natural dwells are already over by 4h), while deployment
queries validity at fixed elapsed times up to 4h, a regime calibration barely
represents.

After the Mondrian (group-conditional) fix — a separate theta per
`wait_hours` bucket, each scored at that bucket's own fixed elapsed time
(`belief.calibrate_conformal_theta_by_wait`) rather than at each event's own
natural dwell (an earlier, incorrect version of this fix reintroduced the
exact calibration-vs-deployment space mismatch the kernel-based rewrite was
built to eliminate):

| axis     | wait=0.25h | wait=0.5h | wait=1.0h | wait=2.0h | wait=4.0h |
|----------|-----------|-----------|-----------|-----------|-----------|
| location | 0.896 OK  | 0.688 MISS | 0.562 MISS | 0.415 MISS | 0.143 MISS |
| state    | 0.424 MISS | 0.303 MISS | 0.121 MISS | 0.061 MISS | 0.000 MISS |

The fix recovers coverage only at the shortest bucket. At longer waits it is
no better than the global theta, and on the state axis it is uniformly worse
(coverage falls to exactly 0 by wait=4h).

## Two follow-up checks, both ruled out

1. **Population mismatch** — calibration pools dwell events from every
   category with any historical change; deployment only asks about the 9
   `FROZEN_LABELS`-qualified objects, which are selected for being movable
   and could plausibly be more volatile than the general population.
   Restricting calibration to exactly those 9 categories changed theta from
   0.2211 to 0.2216 — a negligible shift, and coverage at every bucket was
   unchanged to three decimal places. **Rejected.**
2. **Finite-sample quantile correction** — the naive quantile index
   (`ceil(alpha*n)`) omits the standard split-conformal `+1` finite-sample
   correction (`floor(alpha*(n+1))`). With ~250-300 calibration events and
   ~95 distinct (category, state) score values, the corrected and
   uncorrected indices selected the identical score at every wait_hours
   bucket tested. **Rejected** as an explanation for a 29+ point miss (it
   would only ever matter at much smaller n).

## Mechanism (measured, not inferred): the kernel reliability diagram

`scripts/kernel_reliability_diagram.py` converts "kernel probably
misspecified" from an inference into a measurement: predicted validity
(binned) vs. empirically realized survival, per wait bucket, per axis
(`results/reports/kernel_reliability.csv`, plotted in
`results/reports/kernel_reliability.png`).

**Location** flips direction with horizon. At wait=0.25h, the lowest
predicted-validity bin (~0.025) realizes 0.632 — badly UNDER-confident
(predicts almost no chance of survival; two-thirds actually survive). At
wait=4.0h, predicted~=0.156 realizes only 0.056, and predicted~=0.368
realizes only 0.214 — now OVER-confident. A single global theta cannot
reconcile a kernel that is under-confident at short horizons and
over-confident at long ones; this is the direct mechanism behind the
coverage collapse, not just a symptom of it.

**State** is over-confident at every horizon, not just long ones: at
wait=0.25h, predicted~=0.827 realizes only 0.424 (predicts 83% survival,
less than half actually survive); at wait=4.0h, predicted~=0.501 realizes
0.000 (predicts a coin flip, zero of 66 held-out events actually
survived). This is a more severe and more uniform miscalibration than
location's — consistent with state coverage missing even at the
shortest wait_hours in the coverage check above, where location was
still OK there.

## Conclusion and disposition

With population mismatch and quantile-correction error both ruled out, the
residual explanation is that the fitted `TransitionKernel`'s exponential
(memoryless) decay model does not match this scene's real dwell-time
dynamics at longer horizons — a modeling gap, not a calibration bug. No
recalibration scheme can fix a threshold computed from a model that doesn't
describe the underlying process at the horizon being queried.

- `conformal_decay_threshold` is **dropped from E2's headline policy set**
  (`scripts/embodied_m3_gate.py`, `scripts/e1_cost_heterogeneity.py`). It no
  longer appears in `embodied_results/m2_result.json` / `m3_result.json` or
  any downstream attribution/headline table.
- The Mondrian machinery (`belief.calibrate_conformal_theta_by_wait`,
  `DecayThresholdConfig.theta_by_wait`) is **kept** — it is correctly
  implemented and generically useful for a future, better-fitting hazard
  model; the model it calibrates is what's wrong, not the calibration
  scheme itself.
- `scripts/conformal_coverage_check.py` remains the standing diagnostic
  (global check, per-wait-hours breakdown, dwell-distribution-vs-swept-wait
  plot, and Mondrian-fix verification) so a future hazard model can be
  checked against the same acceptance criterion before being reintroduced.

## Relevance to E4

This is direct evidence for E4's calibration-sensitivity claim: **a
distribution-free coverage guarantee on a fitted-kernel staleness belief
holds at short query horizons and degrades monotonically as the horizon
grows**, independent of how carefully the threshold itself is calibrated.
E4's prior-quality sweep (oracle / train-fit / perturbed / cross-profile)
should expect the same horizon-dependent degradation pattern, and this
write-up (with its per-bucket numbers) is the motivating baseline result for
that discussion, not a loose end to silently drop.
