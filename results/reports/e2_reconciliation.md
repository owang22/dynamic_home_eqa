# decay_voi reconciliation: where E2 preliminary's headline gain comes from

**VERDICT: Mixed — a real counting bug (found and fixed) plus a real,
larger selective-abstention effect. Not a single bucket.**

- **Counting bug, confirmed and fixed**: `decay_voi`'s discovery count on
  volatile-location was reported as 0; the true, scene-aware count is 9.
  `stratified_decomposition()` and `decompose()` paired trials by
  `(policy, wait_hours, label)` without scene/eval_folder — on this
  21-scene pool, generic labels (`book_1`, `candle_1`, ...) recur across
  many scenes, so the pairing dict silently collapsed 505 trials onto 70
  keys, keeping only one scene's trial per collision. Fixed in both
  functions.
- **Selective abstention is the larger single contributor**: 19 of the 35
  outcome-differing pairs are `decay_voi` abstaining on a question the
  floor answered — and the floor was wrong on **all 19 of them** (0/19
  correct). 9 are genuine discoveries (traveled, floor was wrong,
  `decay_voi` came back right). The remaining 7 are `baseline_abstained_*`
  cases (the floor itself abstained, not a flip to attribute either way).
- **The gain is real, not noise**: paired bootstrap delta (`decay_voi` -
  `answer_immediately`) over 18 scene clusters is **+0.072, 95% CI
  [0.023, 0.131]** — excludes zero.

## Setup

Every volatile-location question (505) from `scripts/e2_preliminary_sweep.py`'s
21-scene output, paired by `(scene, eval_folder, wait_hours, label)`
between `decay_voi` and `answer_immediately` (the floor) and, separately,
`always_resense` (the ceiling). No reruns — existing logs only.

## 1. Paired reconciliation

| bucket | n | definition |
|---|---|---|
| identical (no travel, no abstain-divergence) | 470 | the expected bulk — verified, not assumed |
| `decay_voi` traveled, outcome differs | 16 | see breakdown below |
| `decay_voi` abstained, floor answered | 19 | floor correct on 0/19 of these |
| mystery (neither, yet differs) | **0** | would indicate a determinism bug — empty, no escalation needed |

Bucket 4 (mystery) is empty — `decay_voi` and `answer_immediately` reading
the same pre-travel belief state always produce the same non-traveled,
non-abstain-divergent outcome, as they should (both resolve to the same
`believed_anchor` when neither has moved). This is the check that clears
the paired data as trustworthy before anything else below is reported.

**Traveled + outcome differs, all 16 (full traces in `e2_voi_reconciliation.py`'s
own output — reproducible, not reprinted in full here):**

| floor outcome | decay_voi outcome | n | classification |
|---|---|---|---|
| wrong | right | 9 | genuine discovery (`wrong_to_right`) |
| abstained | right | 5 | `baseline_abstained_right` — not a flip, floor never answered |
| abstained | wrong | 2 | `baseline_abstained_wrong` — not a flip |

Every traveled+differs pair involved a real resense leg (`policy_invocations=2`
or more, `distance_traveled_m` from 0.74m to 26.37m) — `decay_voi` genuinely
walked somewhere and came back with new information in all 16 cases, not a
zero-cost state change.

**Abstained-where-floor-answered, all 19**: `decay_voi` traveled in every
one of these too (distances 3.64m–23.06m, `policy_invocations` 2-4), then
chose to abstain rather than commit to an answer its own search couldn't
resolve. The floor, forced to answer immediately, was wrong on **19/19**.
This is selective abstention working exactly as intended — every case
where `decay_voi` declined to answer, declining was the right call.

## 2. Abstain rates and two-way accuracy (pooled across all 505 questions, not scene-clustered — see item 3 for the clustered version)

| policy | abstain_rate | accuracy (non-abstained) | accuracy (all, abstain=0.5) |
|---|---|---|---|
| always_resense | 0.533 | 0.559 | 0.528 |
| decay_threshold | 0.527 | 0.527 | 0.513 |
| decay_voi | 0.521 | 0.467 | 0.484 |
| decay_voi_routing | 0.521 | 0.467 | 0.484 |
| confidence_stop | 0.497 | 0.390 | 0.445 |
| answer_immediately | 0.497 | 0.390 | 0.445 |
| tod_prior | 0.651 | 0.125 | 0.369 |

`decay_voi` abstains slightly more often than the floor (0.521 vs 0.497) —
consistent with the 19-pair selective-abstention finding above. The
non-abstained accuracy numbers here are pooled across all questions
(every question weighted equally), which is why they differ from the
scene-clustered 0.438/0.366 in `e2_preliminary.md` (every scene weighted
equally there) — both are legitimate, answering different questions
("what fraction of individual questions" vs. "what does the average scene
look like").

## 3. Clustered bootstrap CIs

Matches `e2_preliminary.md`'s headline numbers exactly (same clustering):

| policy | accuracy | 95% CI | n_clusters |
|---|---|---|---|
| decay_voi | 0.438 | [0.277, 0.599] | 18 |
| answer_immediately | 0.366 | [0.235, 0.500] | 18 |
| always_resense | 0.510 | [0.343, 0.670] | 18 |

Paired deltas (resampling the same scene indices for both series per
iteration, not two independent bootstraps):

| comparison | delta | 95% CI | excludes zero? |
|---|---|---|---|
| decay_voi − answer_immediately | +0.072 | [0.023, 0.131] | **yes** |
| decay_voi − always_resense | −0.072 | [−0.134, −0.015] | **yes** |

Both deltas exclude zero: `decay_voi` is confidently better than the floor
and confidently worse than the ceiling, at 18 scene clusters.

## 4. Flip-attribution audit — the counting bug

`stratified_decomposition()` (`scripts/e2_headline_comparison.py`) and
`decompose()` (`scripts/e0_mechanism_decomposition.py`) both built their
baseline-pairing dictionaries as `{(wait_hours, label): row}` (the latter)
or `{(policy, wait_hours, label): row}` (the former) — no scene or
eval_folder. On a single-scene result file this is harmless (one scene,
no collisions). On this 21-scene pool it is not: **505 `answer_immediately`
volatile-location trials collapsed to 70 distinct `(wait_hours, label)`
keys**, because generic object labels recur across most scenes' qualified-
label sets (`book_1` alone appears in 15 of the 21 scenes at `wait=0.25`).
Whichever scene's row was not last in file/dict iteration order was
silently dropped from the baseline dictionary, undercounting every
policy's flip totals — most visibly `decay_voi`'s, reported as **0**
`wrong_to_right` on volatile-location before the fix.

Corrected counts (both functions now key on `(scene, eval_folder,
wait_hours, label)`, reusing `cluster_key` — this module's own existing
unit-of-independence concept, not a new one):

| policy | wrong_to_right | wrong_to_abstain |
|---|---|---|
| always_resense | 22 | 38 |
| decay_threshold | 15 | 36 |
| decay_voi | **9** (was 0) | **19** (was 0) |
| decay_voi_routing | 9 | 19 |
| confidence_stop | 0 | 0 |

`confidence_stop`'s 0/0 here is not evidence the fix under-counted it —
it is genuinely structurally identical to `answer_immediately` (see the
correction in `e2_preliminary.md`), so 0 flips against that same baseline
is the correct, expected result, not a residual bug.

Fixed in both functions; regression tests added
(`tests/test_e0_mechanism_decomposition.py`,
`tests/test_e2_headline_comparison.py`) constructing two scenes sharing a
label at the same `wait_hours` and asserting both survive independently.
`e2_preliminary.md`'s mechanism-decomposition CSV has been regenerated
with the fix — the headline accuracy table itself was never affected (it
never went through this pairing dictionary), only the decomposition was.

This was **not** the multi-leg-search truncation this task's own hypothesis
led with — every traveled trial's full route (multiple `goto_resense`/
`goto_anchor` legs) was already present in `log` and available to
`_resense_anchors()`. The bug was a pairing-key collision upstream of
where multi-leg attribution happens at all.

## What is NOT yet supported by these numbers

- This reconciles one stratum (volatile-location) on 21 scenes. The
  stable-location and both state strata are not reconciled here.
- 9 genuine discoveries and 19 correctly-declined-abstentions on 505
  questions is a real but small absolute count; whether this pattern
  holds in shape (discovery: abstention roughly 1:2) as the pool grows
  toward 100 scenes is not established by this data.
- The abstain-scored-at-0.5 "accuracy (all)" column is one convention
  (`ScoringConfig.r_abstain`); it is reported for the denominator-effect
  comparison item 2 asked for, not proposed as a replacement headline
  metric.

**Traceability:** code_hash `05102535c7dbb01b`. Reproduce with
`scripts/e2_voi_reconciliation.py` (reads `embodied_results/diagnostics/`
directly, no reruns). Fix: `scripts/e2_headline_comparison.py`'s
`stratified_decomposition`, `scripts/e0_mechanism_decomposition.py`'s
`decompose`. Regenerated: `e2_PRELIMINARY_mechanism_decomposition.csv`.
