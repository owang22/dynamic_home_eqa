# E2 preliminary: headline policy comparison

**PRELIMINARY.** Run on every scene validated as of this batch (21 of the
100 eventually needed per stratum — see `pool_status.md`). Every number
here will be revised when the pool grows; it exists to be read now and to
surface integration problems today rather than on final-run day.

**Question:** Across the full policy set, which resense-vs-answer strategy
actually wins on accuracy, calibration, and travel cost — and does that
answer hold now that more than one scene is in the data?

**Setup:** Full policy set (`answer_immediately`, `always_resense`,
`confidence_stop`, `decay_threshold`, `decay_voi`, `decay_voi_routing`,
`tod_prior`; `conformal_decay_threshold` remains dropped — see
`conformal_coverage_repair.md`), both question axes (location, state), all
five swept `wait_hours` values, `decay_voi`/`decay_voi_routing` at
`latency_weight=0.01` (the validated binding value — see `voi_boundary.md`,
not the untested default). Clustered by scene (21 clusters for location,
9-15 for state, depending on stratum) with bootstrap confidence intervals
over scene-day clusters, not pooled-i.i.d.

## Headline numbers

Accuracy, 95% bootstrap CI, clustered over scenes:

| policy | stable location | volatile location | stable state | volatile state |
|---|---|---|---|---|
| always_resense (ceiling) | 0.619 [0.417, 0.824] (n=21) | 0.510 [0.343, 0.670] (n=21) | 1.000 [1.000, 1.000] (n=10) | 0.978 [0.933, 1.000] (n=15) |
| decay_threshold (ours) | 0.615 [0.409, 0.821] (n=21) | 0.474 [0.320, 0.620] (n=21) | 0.920 [0.840, 1.000] (n=10) | 0.767 [0.567, 0.933] (n=15) |
| decay_voi (ours) | 0.525 [0.316, 0.733] (n=21) | 0.438 [0.277, 0.599] (n=21) | 0.920 [0.840, 1.000] (n=10) | 0.767 [0.567, 0.933] (n=15) |
| decay_voi_routing (ours) | 0.525 [0.316, 0.733] (n=21) | 0.438 [0.277, 0.599] (n=21) | 0.920 [0.840, 1.000] (n=10) | 0.767 [0.567, 0.933] (n=15) |
| confidence_stop (literature) | 0.476 [0.263, 0.688] (n=21) | 0.366 [0.235, 0.500] (n=21) | 0.920 [0.840, 1.000] (n=10) | 0.767 [0.567, 0.933] (n=15) |
| answer_immediately (floor) | 0.476 [0.263, 0.688] (n=21) | 0.366 [0.235, 0.500] (n=21) | 0.920 [0.840, 1.000] (n=10) | 0.767 [0.567, 0.933] (n=15) |
| tod_prior (zero-sensing floor) | 0.133 [0.018, 0.291] (n=21) | 0.180 [0.077, 0.311] (n=21) | — (not run on state) | — |

Mean travel distance (m) — the cost side of the frontier:

| policy | stable location | volatile location |
|---|---|---|
| always_resense | 9.34 | 19.60 |
| decay_threshold | 4.73 | 16.10 |
| decay_voi / decay_voi_routing | 2.26 | 2.18 |
| answer_immediately / confidence_stop / tod_prior | 0.0 | 0.0 |

Mechanism decomposition (wrong->right = discovery, wrong->abstain =
selective abstention), summed across resensing policies:

| policy | hazard | wrong->right | wrong->abstain |
|---|---|---|---|
| always_resense | volatile | 7 | 0 |
| decay_threshold | volatile | 4 | 0 |
| decay_voi, decay_voi_routing, confidence_stop | stable + volatile | 0 | 0 |
| **total (resensing policies)** | | **11** | **0** |

## Plots

![Accuracy vs. mean answer latency](e2_frontier_accuracy_vs_latency_PRELIMINARY.png)
![Accuracy vs. mean travel distance](e2_frontier_accuracy_vs_travel_PRELIMINARY.png)

## What this means

**`decay_voi` is the actual frontier win here.** On location/volatile — the
stratum where resensing matters most — it recovers most of the gap between
the floor (0.366) and the ceiling (0.510) while traveling 2.18m on average,
against `always_resense`'s 19.60m: roughly 9x less travel for accuracy
within 0.07 of the ceiling. `decay_threshold` sits closer to the ceiling on
accuracy (0.474) but travels 16.10m doing it — barely cheaper than
always-resensing. This is the value-of-information tradeoff the project's
central claim is about, visible for the first time on real multi-scene
data, not one scene's rehearsal.

**Discovery, not selective abstention, is still the separating mechanism**
— 11 wrong-to-right flips against 0 wrong-to-abstain, matching the
single-scene M2 finding's shape. But on this larger sample, all 11
discoveries come from `always_resense` and `decay_threshold`; `decay_voi`
contributes zero in this data, unlike the single-scene check in
`voi_boundary.md` (which found 3, unchanged between lambda settings). This
is not a contradiction — different scene mix, different specific trials —
but it means `decay_voi`'s discovery contribution should be read as
scene-dependent, not a fixed constant, until the pool is much larger.

`confidence_stop` and `answer_immediately` are numerically identical on
every cell measured — `confidence_stop`'s literature stopping rule never
actually differs from never resensing on this pool's data (it never
triggers), which is itself worth noting rather than assuming the two
policies are redundant by design.

`tod_prior` is far below every resensing policy and below the answer-
immediately floor (0.133/0.180 vs. 0.476/0.366) — a schedule-only prior
with zero live sensing does not substitute for observing anything on this
pool, which is the point of the comparison, not a surprise.

## What is too thin to call

Every cell above has a real (non-degenerate) bootstrap CI (n_clusters >= 5
throughout, 21 for location), so nothing here needed a bare point estimate
— but several CIs are still wide (e.g., `always_resense` stable location:
[0.417, 0.824], a 40-point span) reflecting genuine between-scene variance
at 21 scenes, not sampling noise to be explained away. Differences smaller
than roughly 0.1 accuracy between policies within the same stratum should
not be read as resolved rankings yet — `decay_threshold` vs. `decay_voi` on
stable location (0.615 vs. 0.525) has overlapping CIs and needs more scenes
before that gap is a confident claim rather than a point estimate.

## What is NOT yet supported by these numbers

- 21 of the 100 scenes needed per stratum — every number here will move as
  the pool grows toward that bar (`pool_status.md`).
- `decay_voi`/`decay_voi_routing` used `latency_weight=0.01`, the value
  validated as genuinely binding on the frozen scene alone
  (`voi_boundary.md`) — not yet re-validated as the right operating point
  across this broader, more travel-cost-heterogeneous scene set.
- `decay_voi_routing` is numerically identical to `decay_voi` throughout,
  as expected — no multi-object questions exist yet to exercise its
  routing logic (D2 built the generator this batch; wiring it into the
  runner is still open, see `d2_multi_object_question_generator.md`).
- State axis n_clusters (9-15) is well short of location's (21) — the
  state-axis numbers above are real but on a smaller scene set, and (per
  `INDEX.md`'s open questions) the state kernel is separately known to be
  severely miscalibrated at long horizons, which may be depressing every
  state-axis resensing policy's accuracy independent of scene count.

**Traceability:** code_hash `05102535c7dbb01b` (per-scene fingerprints
differ by design — each hashes that scene's own labels/folders; see
`scripts/e2_preliminary_report.py`'s `check_consistency`). Reproduce with
`scripts/e2_preliminary_sweep.py` then `scripts/e2_preliminary_report.py`.
Full data: `e2_PRELIMINARY_headline.csv`, `e2_PRELIMINARY_mechanism_decomposition.csv`.
