# Uncertainty-aware prediction methods on the regime testbench — 2026-09-21 (research agent, for Oliver)

Setting: sightings stream (03:00 round + found-it feedback 10 min after each question), "where is X?" questions during
routine activities, one in-house spot + a confidence per answer. Banks (coordinator's R6, repeat-free): **sick10_all**
(10 hh, 32 days, 24 q/day, everyone sick days 14-23, return 24-31) and **sick10_owner** (10 hh, 16 q/day, one resident's own
things). Every method wraps the timetable counter (2 h bins) — frozen, or with a 72 h / 24 h half-life — and every wrapper's
degenerate setting reproduces the classical log to the digit (0 answer / 0 top-probability mismatches on 4130 + 7198 rows
per base, four bases). Expectations were written before each run (uq/regime/EXPECTATIONS.md); per-day tables, fire days
per household and reliability bins are in uq/regime/<bank>/check.md; the roster runs in ~3 s per household
(uq/regime/roster.sh). Earlier banks (sick_owner, sick_all, sick_spell, holiday_to_work) are in uq/regime/report.md and
contain repeated questions (P2) — provisional.

On the Regime Search page (https://claude.ai/artifact/H1q17m8yUpCEac8kAek2pc): `mart_tt72`, `ocp_tt`, `bma_tt`.

## Three questions, one line each

1. **Does an existing staleness detector see the shift?** Yes: the CUSUM e-detector (threshold 1000) fires on day 14 in
   10/10 households of sick10_all on the frozen timetable (8/10 on the 72 h one) with 0-2/10 lead false alarms in 13 days;
   the return is seen only on a base that itself breaks there — 5/10 with the 72 h base + reset, 0/10 on the frozen base
   (nothing to detect); at 16 q/day (sick10_owner) it drops to 5-6/10 on day 14.
2. **Does conformal prediction stay honest across the shift?** Yes: coverage 0.906-0.930 per stage (target 0.90) with sets
   2.3 → 15-21 on days 14-16 and back to ~2 by day 22; both variants miss on the shift day itself (0.67-0.76); the return
   shows as a coverage loss (0.85-0.88 on days 24-26 on the 72 h base), not as larger sets.
3. **Does hedging over memory lengths help?** In the spell, +5 to +10 points over the frozen base (66.0 / 69.0 vs 60.9 on
   sick10_all; 71.1 / 74.5 vs 64.5 on sick10_owner) but 3-11 under the best single half-life (24 h: 76.9 / 80.2); on the return it hedges the drop
   away (79.7 = frozen) — by construction it cannot show the break-again.

## The roster

| agent | paper | adaptation here | knobs |
|---|---|---|---|
| ocp | Angelopoulos, Barber, Bates, *Online conformal prediction with decaying step sizes*, ICML 2024; relevance-weighted scores from Ren et al., *Explore until Confident*, 2024 | score 1 − Rel·p(y); set = {y: score ≤ q_t}; q_t moves by η_t·(miss − α) on the feedback, η_t = max(0.005, 0.05·t^−0.6); confidence 1/|set| | α 0.1, η floor 0.005, Rel half-life 24 h (no effect here: feedback keeps everything fresh) |
| nexcp | Barber, Candès, Ramdas, Tibshirani, *Conformal prediction beyond exchangeability*, Ann. Stat. 2023 | (1−α) quantile of the time-weighted past scores (weights 2^−age/τ_w) plus a unit mass at +∞; same score | τ_w 24 h / 72 h / ∞ |
| mon / mart | Vovk et al. conformal test martingale; Shin, Ramdas, Rinaldo, *E-detectors*, NEJSDS 2024 | conformal p-values of the truth's score against the window since the last fire, simple-mixture betting over ε∈(0,1), **CUSUM restart** (each grid point restarts at 1 when it falls below 1); fire at 1000; repeated questions (same object, no new sighting) do not step it; `mart`: counts ×0.1 at a fire | δ 1e-3, min window 20, optional sliding window 96, discount factor |
| bma | Herbster & Warmuth 1998 fixed share; Raftery et al. 2010 dynamic model averaging | counters with half-lives {24, 72, 168, ∞} h, weights updated by each counter's probability of every positive sighting, share 0.02 to uniform; `bma_obj`: one weight vector per object | half-life set, share |
| LLM channels | Tian et al. 2023 (verbalized); Kadavath et al. 2022 / KnowNo (token probability); Farquhar et al. Nature 2024, Lyu et al. 2024 (agreement) | naive-memory prompt; (a) stated confidence, (b) first-token probability of the chosen letter in a 10-way multiple choice, (c) share of 5 samples at T 0.7 agreeing with the greedy answer | local Qwen3.8-27B only |

## Accuracy per stage, mean ± 1 sd across 10 households (lead 1-13 | sick 14-23 | return 24-31)

| agent | sick10_all | sick10_owner |
|---|---|---|
| timetable, frozen (`none_tt`) | 72.1±7.1 \| 60.9±11.8 \| 79.7±6.7 | 72.4±8.1 \| 64.5±18.4 \| 79.0±7.9 |
| timetable, 72 h half-life | 73.0±7.2 \| 72.0±6.2 \| 71.5±4.8 | 73.1±7.9 \| 77.4±7.2 \| 71.7±6.4 |
| timetable, 24 h half-life | 72.2±6.6 \| 76.9±4.4 \| 72.4±5.3 | 72.1±8.0 \| 80.2±4.7 \| 73.0±3.2 |
| most frequent, frozen | 54.4 \| 29.2 \| 59.6 | 59.1 \| 41.5 \| 60.1 |
| e-detector + reset ×0.1, frozen base (`mart_tt`) | 71.9±7.4 \| 75.8±6.3 \| 65.4±8.7 | 72.3±7.9 \| 79.0±3.7 \| 67.1±14.6 |
| e-detector + reset, 72 h base (`mart_tt72`) | 73.0±7.2 \| 76.3±5.9 \| 71.1±4.5 | 73.0±7.8 \| 80.5±4.9 \| 72.8±4.8 |
| BMA, global weights (`bma_tt`) | 73.0±7.0 \| 66.0±8.3 \| 79.7±6.0 | 73.1±7.7 \| 71.1±12.2 \| 77.9±6.9 |
| BMA, per-object weights (`bma_obj`) | 73.0±7.1 \| 69.0±7.0 \| 78.8±5.5 | 73.3±7.7 \| 74.5±8.7 \| 76.7±6.6 |

Per day, sick10_all, frozen timetable: 80 (day 13) → 35 47 55 56 64 67 72 64 75 74 → 80 78 79 82 … (no return drop);
72 h: 82 → 34 49 61 72 78 81 86 83 88 88 → 54 60 71 77 76 81; `mart_tt72`: 82 → 40 59 71 82 82 82 86 85 89 88 → 54 59 72 75.
Larger than 1 sd: the day-14 drop on every base; sick stage frozen vs 72 h / 24 h (60.9±11.8 vs 72.0±6.2 / 76.9±4.4);
the reset gain (mart_tt 75.8±6.3 vs frozen 60.9±11.8); the return drop of forgetting/reset bases vs frozen (65.4±8.7 and
71.1±4.5 vs 79.7±6.7). Within 1 sd: BMA vs frozen in the sick stage (66.0±8.3 / 69.0±7.0 vs 60.9±11.8).

## Staleness detector (CUSUM e-detector, threshold 1000): fires per household

| base / variant | sick10_all: day 14-15 | lead false alarms | return 24-26 | sick10_owner: day 14-15 | lead | return |
|---|---|---|---|---|---|---|
| frozen, monitor | **10/10** (all on day 14) | 2/10 (days 9, 10) | 0/10 | 6/10 | 1/10 | 0/10 |
| 72 h, monitor | 8/10 | 0/10 | 0/10 | 5/10 | 1/10 | 0/10 |
| 24 h, monitor | 3/10 | 0/10 | 2/10 | 1/10 | 1/10 | 2/10 |
| 72 h, monitor, sliding window 96 | 6/10 | 0/10 | 2/10 | 5/10 | 1/10 | 2/10 |
| 24 h, monitor, sliding window 96 | 4/10 | 1/10 | **6/10** | 0/10 | 1/10 | 3/10 |
| **72 h, reset ×0.1 (`mart_tt72`)** | **8/10** | **0/10** | **5/10** | 5/10 | 1/10 | 3/10 |

sick10_all fire days per household, mart_tt72: s0:14,24 s2:14,24 s3:14,24 s4:14 s5:14,26,28 s6:14 s7:14,24 s8:14 (s1, s9 never).
What it needs: ~20 non-duplicate questions whose error rate rose by ≥ 30 points (synthetic: median 21 questions for a
90 → 50% shift, 2/50 false alarms in 1000 stationary steps). sick10_all's 24 q/day (≈15 non-duplicate) meets that on the
first sick day; sick10_owner's 16 q/day (≈10) is under the floor, hence 5-6/10. The frozen base never fires on the return
because its own accuracy rises there — correct for a one-sided test. The forgetting bases' return drop (88 → 54 → 60 → 71)
lasts one or two days ≈ 30 non-duplicate questions, which is why the 72 h monitor sees it in 0-2/10 and only the reset
variant (whose window holds the re-learned spell) or the 24 h base with a sliding window reach 5-6/10.

## Conformal prediction: coverage (target 0.90) and set size

| agent | sick10_all lead \| sick \| return | day 13 → 14 → 15 → 16 (cov/set) | day 23 → 24 → 25 (cov/set) | sick10_owner lead \| sick \| return |
|---|---|---|---|---|
| ocp, frozen base | 0.918 \| 0.906 \| 0.928 | 0.94/2.3 → 0.71/14.9 → 0.88/17.2 → 0.93/18.9 | 0.94/2.9 → 0.95/2.2 → 0.93/2.2 | 0.925 \| 0.916 \| 0.928 |
| ocp, 72 h base | 0.920 \| 0.907 \| 0.890 | 0.93/2.3 → 0.72/16.0 → 0.91/20.3 → 0.94/17.4 | 0.93/2.6 → 0.88/1.9 → 0.85/3.5 | 0.932 \| 0.917 \| 0.883 |
| nexcp τ_w 24 h, frozen | 0.934 \| 0.930 \| 0.925 | 0.93/7.0 → 0.76/21.4 → 0.95/27.7 → 0.99/26.6 | 0.93/4.2 → 0.93/2.4 → 0.92/2.7 | 0.951 \| 0.947 \| 0.931 (over-covers at 16 q/day: sets 9-10 in the lead) |
| nexcp τ_w 72 h, frozen | 0.919 \| 0.923 \| 0.921 | 0.94/3.7 → 0.67/12.0 → 0.90/20.2 → 0.95/22.7 | 0.95/4.5 → 0.94/2.4 → 0.92/2.3 | 0.934 \| 0.913 \| 0.922 |

Both hold 0.90-0.93 per stage; both miss on the first shift day (0.65-0.76) and recover by day 15 (weighted quantile) or
day 16 (decaying step), with sets 7-10× larger during the spell that shrink back to ~2 by day 22. Rel-weighting (Ren et
al.) changes coverage by ≤ 0.005: the feedback keeps every asked object fresh. On the return the frozen base is right, so
its sets stay at 2; on the 72 h base the return costs 5-7 points of coverage on days 24-26 without larger sets — the truth
is then at floor mass and the threshold cannot climb to it within a one-day event (set size is a knife-edge on the floor
atom of the base's distribution; that, not the method, is why ocp and nexcp set sizes differ by up to 3× at equal coverage).

## BMA over half-lives (sick10_all, mean weight over households)

short half-lives (24 h + 72 h): 0.06 on day 13 → 0.68 day 14 → 0.55 → 0.36 (day 16) → 0.07 by day 22 → 0.03 on days 24-26;
infinite memory: 0.84 → 0.22 → … → 0.66 (day 23) → 0.93 (day 24). Up on days 14-16 and down by day 22 as predicted; NOT up
again on the return, because the frozen counter is the best predictor there and the mixture moves back to it within a day —
so BMA keeps the frozen base's return (79.7 = frozen) and does not show a drop-again; its cost is the spell (66.0 vs 72.0 for
the 72 h base). Per-object weights help by +3 in the spell (69.0; 74.5 vs 71.1 on sick10_owner) but do not reach the 72 h
base: each object is sighted ~1-3× a day, so its own weights move 0.07 → 0.21 on days 14-15 where the global vector moves
0.06 → 0.68.

## LLM confidence channels (local Qwen3.8-27B, naive memory; two tests, one household each, 2-3 days)

sick_owner hh_s0 (provisional bank), days 13/14, 64 questions, 162 calls: accuracy 91% → 38% (the LLM breaks with the
timetable, 100 → 22). Verbalized confidence 0.886 → 0.873, correct-vs-wrong separation +0.012 (flat, as expected);
sample agreement 0.875 → 0.731, separation +0.195 — the only channel that notices; token probability 0.934 → 0.886,
separation +0.036 on the greedy answer, +0.114 on its own multiple-choice answer (MCQ accuracy 78% → 62%).
sick10_all hh_s0 (primary bank), days 13/14/24, 72 questions, 234 calls: accuracy 75% → 54% → 75% (the frozen timetable in
this household: 80 → 35 → 80; the naive-memory LLM drops half as far because it reads recent sightings). Here NO channel
reaches the bar: verbalized 0.856 → 0.829 → 0.892 (separation +0.026); agreement 0.825 → 0.858 → 0.883 (it went UP on the
shift day; separation +0.069); token 0.885 → 0.805 → 0.868 (separation +0.051, +0.075 on its own MCQ answer). So the
+0.195 agreement separation seen on sick_owner hh_s0 does not replicate on the primary bank; with n ≈ 70 per test the
standard error of a mean difference is ~0.05-0.07, so both tests are single-household, low-power evidence. Reliability
(both tests pooled in the summaries): 87-91% of questions sit in the top verbalized bin regardless of correctness.

## Reviewer follow-ups (2026-09-21 evening): a fixed hedge, a planning metric, per-person detection

Four results added after review; expectations for each written first in `uq/regime/EXPECTATIONS.md`, numbers below.

### Fixed-share hedge: the loss function was rewarding calibration, not accuracy

The original hedge (`bma_tt`) scores each memory-length counter by ITS OWN predictive probability of the seen spot
(log-loss / Bayes mixing) — that rewards a well-calibrated, SMOOTH distribution, not whichever counter is more often
literally right. On days 19-23 of the spell the 1-day counter (tt24) is 10-15 points more accurate than the frozen
one, yet the hedge's weight had already drained back to frozen by day 22-23 — the reviewer's suspicion, confirmed.
Fix (`--score hit`): score each counter 1.0 if ITS OWN argmax equals the seen spot, 0.05 otherwise — plain 0-1 accuracy,
immune to how a counter spreads its remaining mass. On days 19-23 specifically (10 hh, both banks): `bma_hit` 84.4±3.5
(sick10_all) / 85.9±4.7 (sick10_owner) vs tt24's own 85.8±3.1 / 87.5±3.9 — within 1.4-1.6 points. Over the full spell
(14-23, the harder early-readaptation days included) it is close but not quite there: 74.4±5.0 / 77.9±6.4 vs tt24's
76.9±4.4 / 80.2±4.7 (2.3-2.5 points short); return stays near frozen (78.5±6.4 / 76.8±6.4 vs 79.7±6.7 / 79.0±7.9, 1.2-2.2
points). Either way, a large gain over the old hedge (66.0→74.4 / 71.1→77.9 in the spell). It genuinely re-adapts, not
just averages: short-half-life weight snaps 0.79→0.18 the same day the return starts. Alpha sweep {0.02, 0.10, 0.30}:
the hypothesized tradeoff (higher alpha = faster return, less spell stability) did not appear — 0.02 (the existing
default) wins on both stages simultaneously; fixed-share pulls toward UNIFORM every step, so a larger alpha just dilutes
the current leader rather than tracking it faster. `--group person`: a further +0.4-2.4 points on sick10_owner's spell
(single-owner regime) but not on sick10_all (everyone sick — nothing for per-person grouping to differentiate); the real
per-person test is the detection section below. Code: `uq_agents.py --score {predictive,hit,tempered}`.

### Planning metric: search cost, rooms, and an ask-or-search policy — with a matched-rate control

For every question of every dist-logging agent: rank of the truth in the agent's own probability order ("places
searched"), distinct rooms entered by that point, and a policy — search (cost = rank) if confident (top_prob ≥ τ, or
conformal set ≤ k), else ask a resident at a flat cost c and retrieve directly. Full write-up: `uq/planning/README.md`.
Raw-confidence table (τ=0.6, k=3): the e-detector+reset (`mart_tt72`) costs LESS on the sick days than its own un-reset
base (2.04 vs 2.14 at c=2, sick10_all) and than the frozen baseline (3.28) — "ask more, search less" on the days it
should, "no cost" on plain days (lead costs within hundredths). `last_seen` is the cautionary case: its own confidence
sits ≥ 0.6 on 100% of questions in every stage (matches the ~98%-claimed finding from the calibration chart), so the
policy never lets it ask — it pays the full 12-14-place search cost of its bad guesses everywhere. `ocp_tt` (honest
sets): cost RISES on the sick days at every k tested (1, 2, 3) — it wraps the frozen base unmodified (its places/rooms
columns are row-for-row identical to `none_tt`'s), and a conformal set-size threshold does not reliably flag "my point
guess is about to be wrong today" — it is calibrated to a coverage target, a different question.
**Matched-rate control (the reviewer's check on whether this is a real effect or a threshold-scale artifact):** per
agent, pick τ/k from LEAD-day data alone so the lead-day ask rate equals a fixed target (25% or 50%), then apply that
SAME threshold to sick/return. Only `mart_tt72` clears the bar at both rates on both banks — sick10_all sick-stage cost
3.31→2.55 (25% target) and 2.67→2.25 (50% target); sick10_owner 2.92→2.48 and 2.40→2.30. `bma_tt`, which looked like a
clear win in the raw table, does NOT clear it — matched cost RISES on sick days at both rates on both banks (e.g.
sick10_all 3.15→3.55 at 25%): its raw-table win was mostly the scale confound (at τ=0.6 its raw lead ask rate was
already 68%, far above the other agents', pinning its lead cost near the ask floor already). `none_tt72` (the same
base with no detector) also fails the matched test. `ocp_tt`'s negative finding is unchanged and now scale-independent.
**Conclusion: the planning-metric win is specifically about the detector-triggered targeted reset, not about "having an
uncertainty signal" in general.** Code: `uq_planning.py`, `--match-rates 0.25,0.5`.

### Per-person detection and reset: the "which beliefs should become less trusted" answer

New regime `sick10_partial` (resident_1/Yuki sick days 14-23; questions about EVERYONE's things, 634 q/hh about Yuki vs
110 about her housemate) is where a shared, household-wide signal cannot tell the two people apart: the frozen
timetable's own confidence rises on BOTH the affected and unaffected resident's objects during the spell (0.52→0.56 and
0.49→0.63) — no learner's stated confidence separates them. Built: one e-detector per resident (`--group person` on
`--agent martingale`), each firing and resetting only that resident's own known object bins, plus a told-oracle upper
bound (`--detector off --oracle-schedule "14:resident_1,24:resident_1"`). Degenerate checks: `--group global`
reproduces `mart_tt72`/`mart_tt`/`martw_tt72` to the digit (caught and fixed an RNG-seed regression from the refactor
before trusting any of this — problems_found.md P4).
**Specificity: perfect.** Across 10 households, every fire under the per-person detector is tagged `resident_1`;
resident_2's own detector fires in 0/10 households, ever (the global detector fires day 14 in 5/10, tagged simply
"global" — it cannot distinguish). Per-person catches resident_1's break in 4/10 households vs the global detector's
5/10 — a small, real cost of splitting the stream, traded for zero false positives.
**Collateral damage: real, but on confidence, not accuracy.** resident_2's ACCURACY under the global reset is not
measurably worse than frozen (75.6→76.2 sick10_partial mean, within noise) — the reset does not make them more often
WRONG. It does make them measurably less SURE: confidence 36.3→31.8 (sick), 38.1→35.3 (return) — the global reset
discounts every object's counts, including theirs. Under the per-person reset, resident_2's accuracy AND confidence are
bit-for-bit identical to frozen in every stage (an exact match, not just close) — the reset never touches them.
Told-oracle: resident_1 82.2 sick / 73.2 return vs the detected version's 79.4 / 70.4 — 2.8-2.9 points is the cost of
detection lag; resident_2 exact-match to frozen (scoped only to resident_1, as it should be).
**Per-person conformal (follow-up):** splitting the online-conformal threshold per resident the same way reduces but
does not eliminate resident_2's collateral set-size growth on the shift days (9.7→6.7 on day 14, 12.2→8.9 on day 15,
global vs per-person; verified 0/744 cross-assignment, not a bug) — unlike a discrete reset, an online-conformal
threshold's calibration quality itself depends on sample size, and resident_2 only has ~110 questions to calibrate on
(vs 744 for resident_1), so their own per-person threshold is wobblier even in the lead stage (day 12-13 set size 2.6→4.7
just from the split). Code: `uq_agents.py --group person` now works for `bma`, `martingale`, and `ocp`; `--oracle-schedule`.

## Three bugs found on the first household (uq/problems_found.md)

P1 — the plain mixture martingale can never fire on a 28-day bank: over ~400 stationary questions its value decays to ~1e-5
(shows 0.000 from day 3), and a 100× rise from there is out of reach even for a 100 → 22 drop. This is also why the
previous agent's runs fired 0/72 shift days. Fix: CUSUM restart (Shin-Ramdas-Rinaldo's e-detector), threshold 1000.
P2 — repeated questions counted as repeated evidence: the day-19 "fire" of hh_s0 was mug_yuki asked 5× within minutes
during evening_tv before the found-it feedback landed — one miss, five p-values of 0.001-0.013. Fix: a repeat with no
new sighting of the object does not step the detector (the banks were then regenerated repeat-free).
P3 — the LLM token-probability channel: under a JSON-string schema Qwen's tokenizer has merged tokens '"A'..'"I' but not
'"J', so a bare '"' first token forced "J) somewhere else" (4/6 of the first rows, confidence 0.00). Fix: the letter is
asked without a schema.
P4 — `DiscountedTimetable.discount()` accepted an `objects=` filter and silently dropped it (never stored, never
checked), so every "targeted" reset before today was actually global. Harmless until today: every existing caller
passed `objects=None` anyway. Would have silently broken the per-person reset above had it shipped unfixed. Fixed,
zero regression confirmed (uq_synth.py all-pass; every degenerate check and every existing mart_tt/mart_tt72 fire-day
count unchanged to the digit).

## What each method can and cannot show on this testbench

- **e-detector**: with false alarms controlled (0-2/10 households over 13 lead days), fires on the first sick day in every
  household of sick10_all and in 5-6/10 of sick10_owner (16 q/day is under its ~20-question floor). It shows the return only
  on a base that itself breaks on the return, and only as the reset variant on the 72 h base (5/10) or the 24 h base with a
  sliding window (6/10): the return drop is a 1-2 day event at the detection floor. It cannot fire on the frozen base's
  return — there is nothing to detect.
- **detector + reset**: turns the detector into an adapting learner: +15 points in the spell over the frozen base (75.8 vs
  60.9), and a drop-again on the return (65.4 / 71.1 vs 79.7) — the full learn / break / re-learn / break-again shape, from a
  method with a false-alarm guarantee rather than a tuned half-life.
- **conformal (both)**: coverage stays at 0.90-0.93 per stage across both boundaries with sets that grow 7-10× during the
  spell; both miss on the shift day itself. It says "unsure" for as long as the base is wrong, not that the regime changed;
  the weighted quantile reacts one day faster at 1.5-3× the set size, and with a 24 h weight window it over-covers at 16 q/day
  (sets 9-10 in the lead); a 72 h window fixes that.
- **BMA**: hedges correctly and by construction cannot show the return drop; +5-10 in the spell over the frozen base, −3 to
  −6 under the 72 h base. Per-object weights are too slow at 1-3 sightings a day. Scored on 0-1 hits instead of log-loss
  (`--score hit`) it closes most of that gap (within 1.4-1.6 points of the best single memory on the exact days a
  reviewer flagged) — the original log-loss scoring was rewarding calibration, not accuracy, a distinct failure mode
  from the return-drop tradeoff.
- **Planning (search cost / ask-or-search)**: only the detector-triggered reset shows a real, scale-independent
  "ask more, search less" effect on shift days (confirmed at matched lead-day ask rates of 25% and 50%, both banks);
  the hedge's apparent win in a naive fixed-threshold comparison was mostly a confound (it asks far more often on
  ordinary days too), and honest-sets' conformal set size does not, by itself, flag "my answer is about to be wrong."
- **Per-person detection/reset**: the only mechanism that can tell an affected household member from an unaffected one
  when a shared confidence signal cannot (0.52→0.56 vs 0.49→0.63, both rising) — 0/10 false fires on the unaffected
  resident, exact-match accuracy AND confidence preserved for them under a per-person reset, vs a measurable confidence
  (not accuracy) leak under a global one. A per-person conformal threshold reduces the same leak but not to zero — it
  is also fighting a sample-size problem (the unaffected group asked about 6× less often here).
- **LLM channels**: verbalized confidence is uninformative on both tests (flat 0.83-0.89, ~90% of questions in the top
  bin, separation ≤ 0.03); sample agreement separated correct from wrong by +0.195 and fell 0.14 on the shift day in one
  household (sick_owner hh_s0) but only +0.069 and rose on the shift day in the other (sick10_all hh_s0); token probability
  +0.04-0.08. Two households, ~70 questions each, local model only: not enough to rank the channels — the one firm
  statement is that verbalized confidence carries no signal here.

## Reproduce (any bank dir under results/regime_search/<regime>/banks, ~3 s per household for the whole roster)

```
U=results/confidence_shift_2026-09-20/uq/regime
$U/roster.sh <regime> hh_s0 hh_s1 hh_s2 hh_s3 hh_s4 hh_s5 hh_s6 hh_s7 hh_s8 hh_s9      # all agents -> $U/<regime>/<agent>/hh_s*.jsonl (+ .side.json)
AGENTS="mart_tt72 ocp_tt bma_tt" $U/roster.sh <regime> hh_s0 ...                      # a subset; existing logs are moved to <agent>/old_HHMM/, never deleted
cd src && python3 -m baselines.patrol.uq_check --dir ../$U/<regime> --classical ../results/regime_search/<regime>/classical --md ../$U/<regime>/check.md
cd .. && python3 $U/make_report.py sick10_owner sick10_all <regime>                   # -> $U/report_auto.md (headline table + per-regime sections)
cd src && python3 -m baselines.patrol.uq_synth                                          # synthetic checks (conformal, martingale, cusum)
python3 -m baselines.patrol.uq_llm --bank ../results/regime_search/<regime>/banks/hh_s0_t03.jsonl --out ../results/confidence_shift_2026-09-20/uq/llm_channels/<name> --day-list 13,14,24
python3 ../results/confidence_shift_2026-09-20/uq/llm_channels/summarize.py ../results/confidence_shift_2026-09-20/uq/llm_channels/<name>/hh_s0.jsonl

# hedge scoring/grouping (evening follow-ups)
AGENTS="bma_hit bma_person" $U/roster.sh <regime> hh_s0 ...                             # --score hit --share 0.02 [--group person]
# per-person detection / reset / told-oracle (sick10_partial: resident_1 sick, everyone's objects asked)
AGENTS="detperson_tt72 oracle_tt72 ocpperson_tt" $U/roster.sh sick10_partial hh_s0 ...   # --group person on martingale and ocp; --oracle-schedule "14:resident_1,24:resident_1" --detector off
# planning metric: search cost / rooms / ask-or-search policy, no new agent runs (reads the dist field already in the logs above)
python3 -m baselines.patrol.uq_planning --regime <regime> --agents none_tt,none_tt72,none_lastseen,mart_tt72,bma_tt,ocp_tt --tau 0.6 --k 3 --costs 2,4 --match-rates 0.25,0.5 --out ../results/confidence_shift_2026-09-20/uq/planning
```
uq_check prints the E1-E7 lines (E1 = digit check of every `none_*` agent against the classical rows, which must read
0 mismatches before anything else is believed); the expectations behind them are in $U/EXPECTATIONS.md. Agent definitions
(one line each) are at the top of roster.sh; `python3 -m baselines.patrol.uq_agents --help` lists every knob (the evening
additions: `--score {predictive,hit,tempered}`, `--group {global,object,person}` for `bma`/`martingale`/`ocp`, `--detector
off` and `--oracle-schedule "day:owner,..."` for a told-upper-bound reset). REPORT.md itself is hand-written from check.md
and uq/planning/*.md — the numbers to refresh are the per-stage mean ± sd table, the fire table ("fire days per household"
in check.md), the coverage table, and the planning-metric tables (raw + matched-rate).

