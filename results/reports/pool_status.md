# Pool status

**Question:** How much of the multi-scene, multi-profile pool is actually
usable today, and what — if anything — is blocking the rest?

**Setup:** Disk-verified (not cached-state-trusted) `trace_validate` status
per scene-day, cross-checked against `scripts/yield_projector.py`'s
effective-N accounting.

## Headline numbers

Per-scene status (disk-verified today):

| scene | profile | location days OK | state days OK | qualified labels |
|---|---|---|---|---|
| 102343992 (frozen) | family_with_kids | 5/5 | 5/5 | 9 |
| 102344022 | family_with_kids | 4/4 present, generation incomplete | 0 | 0 |
| 102344049 | family_with_kids | 5/5 (**fixed this batch — day0 regenerated**) | 5/5 | 12 |
| 102344094 | single_professional_commuter | 5/5 | 5/5 | 4 |
| 102344115 | single_parent_young_kids | 5/5 | 5/5 | 7 |
| 102344193 | night_shift_worker_alone | 5/5 | 5/5 | 5 |
| 102344250 | family_with_toddler | 5/5 | 4/5 (state merge failed 1 day) | 6 |
| 102344280 | family_with_teens | 5/5 | 5/5 | 9 |
| 102344307 | college_students_shared_house | 5/5 | 5/5 | 8 |
| 102344328 | — | unreachable, excluded | — | 0 |
| 102344403 | college_student_alone | 5/5 | 5/5 | 3 |
| 102344439 | young_professional_couple | 5/5 | 5/5 | 5 |
| 102344457 | family_with_kids | 4/4 present, generation incomplete | 0 | 0 |
| 102344469 | — | unreachable, excluded | — | 0 |
| 102344529 | single_retiree | 5/5 | 5/5 | 5 |
| 102815835 | young_professional_couple | 5/5 | 5/5 | 5 |
| 102815859 | night_shift_worker_alone | 5/5 | 5/5 | 7 |
| 102816009 | family_with_toddler | 5/5 | 5/5 | 10 |
| 102816036 | roommates_shared_house | 5/5 | 4/5 (state merge failed 1 day) | 8 |
| 102816051 | family_with_toddler | 5/5 | 5/5 | 6 |
| 102816066 | — | unreachable, excluded | — | 0 |
| 102816114 | college_students_shared_house | 5/5 | 5/5 | 8 |
| 102816216 | young_professional_couple | 5/5 | 5/5 | 7 |
| 102816600 | — | unreachable, excluded | — | 0 |
| 102816615 | college_student_alone | 5/5 | 5/5 | 8 |
| 102816627 | single_retiree | 5/5 | 0 (never attempted) | 5 |
| 102816729 | family_with_kids | 5/5 | 5/5 | 6 |

**21 scenes fully qualify for the location axis today** (20 pool scenes +
the frozen scene, after the `102344049` fix below), spanning 13 distinct
household profiles.

Yield projector output (effective-N = qualifying scenes, the correct
denominator — see that script's own docstring for why raw label/day
counts overstate readiness), **re-run after the fix**:

| stratum | raw_N | n_clusters (effective) | bar | status |
|---|---|---|---|---|
| location/stable | 1680 | 21 | 100 | SHORT by 79 |
| location/volatile | 3920 | 21 | 100 | SHORT by 79 |
| state/stable | 420 | 12 | 100 | SHORT by 88 |
| state/volatile | 770 | 18 | 100 | SHORT by 82 |

## What is blocking completion — the must-fix found this batch

**`scripts/expand_scene_pool.py`'s `_scene_fully_generated` checked file
existence only**, short-circuiting *before* `_folder_ready`'s trace_validate
check ever ran. `102344049`'s day0 folder has failed trace_validate
(chain_breaks=4, re_inserts=26, no_ops=31, unattended=26) since before this
session's manifest.py integrity fixes — and has been silently re-reported
as "already generated" and skipped in every pool-expansion run since,
because the files exist even though their contents don't pass validation.
This is not a new guard; it is a bug in an existing, already-built
self-healing mechanism that was supposed to already catch exactly this
case. Fixed (`_scene_fully_generated` now delegates to `_folder_ready` for
every folder) and covered by a regression test
(`tests/test_scene_fully_generated.py`). **Confirmed working**: a recovery
pass regenerated `102344049`'s day0 fresh and it now passes trace_validate
(5/5 days, 12 qualified location labels, 3 qualified state labels —
`fridge_1`, `tv_1`, `wardrobe_1`), recovering one real scene that had been
silently stuck since before this session. The other two targets in the
same recovery pass did not recover: `102344022` and `102344457` still fail
generation on day 2 with a malformed-JSON LLM output — a different,
stochastic issue unrelated to the fixed bug, not retried further this
batch (not a stuck process, an LLM output-formatting failure that would
need either a retry-with-backoff or a prompt fix to address). `102344250`
and `102816036` still fail their state-merge trace_validate on one day
each — also unresolved, also a separate issue from the fixed bug.

Beyond that one fix, the remaining gap is **volume, not a stuck process**:
generation is actively running (this session alone added 19 scenes since
the frozen scene), qualification and validation are working correctly on
everything that completes, and the shortfall is that 20 of 100 needed
scenes exist per stratum. No ETA can be given for reaching 100 — throughput
depends on LLM generation time per scene (multi-day, several LLM calls
each) and the fraction of scenes that pass reachability (roughly 22/26 =
85% in the sample generated so far), not on any blocked step in the
pipeline.

## What is NOT yet supported by these numbers

- 4 candidate scenes failed the reachability pre-check entirely
  (unreachable rooms/anchors) and are permanently excluded, not "pending."
- The state axis's qualifying-scene count (12 stable / 18 volatile) is
  lower than the count of scenes with *some* valid state data (~19) because
  state question eligibility requires a specific state-labeled instance to
  pass the same two-property qualification rule as location (exists at
  patrol_start, reachable) — having valid state data on disk is necessary
  but not sufficient.
- The recovery pass fully resolved `102344049` but not `102344022` or
  `102344457` (separate, stochastic LLM generation failures) or the two
  state-merge failures (`102344250`, `102816036`) — see above.

**Traceability:** fingerprint `25e52eee014c3c72`, code_hash
`05102535c7dbb01b`. Reproduce with `scripts/yield_projector.py`. Fix:
`scripts/expand_scene_pool.py`'s `_scene_fully_generated`, tested by
`tests/test_scene_fully_generated.py`.
