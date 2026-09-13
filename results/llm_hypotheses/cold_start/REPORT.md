# Cold start and re-asking — hh_001

Stop point per the brief: cold start built, three-layer re-asking built, random-slice policy
built, both protocols run on hh_001 under named and anonymized conditions, the four figures
plus the per-object oracle analysis produced. No extra households, no prompt tuning beyond
valid output. Scoring throughout: `ON_PERSON ≡ OUT_OF_HOUSE`. Error bars on every series.

**One household, one bank seed, one elicitation per condition. Read the mechanisms, not the
third decimal.**

## Headline

| passive protocol (fixed patrol, no policy) | top-1 | log-loss |
|---|---|---|
| Oracle (ceiling) | 0.767 ± 0.009 | 0.658 ± 0.022 |
| MostFrequent 24 h | 0.638 ± 0.010 | 1.408 ± 0.026 |
| Periodic (no-LLM arm) | 0.621 ± 0.010 | 1.909 ± 0.052 |
| LLM cold-start named, **fixed set** | 0.620 ± 0.010 | **1.332 ± 0.028** |
| LLM cold-start anonymized, fixed set | 0.620 ± 0.010 | 1.331 ± 0.027 |
| LLM cold-start named, **re-asking** (days 3, 7) | 0.603 ± 0.010 | 1.347 ± 0.030 |
| LLM cold-start anonymized, re-asking | 0.571 ± 0.010 | 1.461 ± 0.029 |

| active protocol (myopic VoI λ=0.05) | top-1 (answer) | log-loss (belief) | random senses |
|---|---|---|---|
| Oracle, f=0 | 0.808 ± 0.008 | 0.791 ± 0.036 | 0 |
| Periodic, f=0 / f=0.1 | 0.714 / 0.721 | 1.425 / 1.402 | 0 / 50 |
| LLM fixed set, f=0 / f=0.1 | **0.712** / 0.700 | **0.987** / 1.025 | 0 / 50 |
| LLM re-asking, f=0 / f=0.1 | 0.673 / 0.684 | 1.115 / 1.074 | 0 / 50 |

Paired, 95% CI, * = excludes zero:

| comparison | top-1 | log-loss |
|---|---|---|
| re-asking − fixed (named) | −0.016 [−0.029, −0.004]* | +0.015 [−0.006, +0.036] |
| re-asking − fixed (anonymized) | −0.049 [−0.061, −0.037]* | +0.130 [+0.114, +0.146]* |
| named − anonymized (fixed set) | −0.001 [−0.008, +0.005] | +0.000 [−0.012, +0.012] |
| named − anonymized (re-asking) | +0.032 [+0.018, +0.046]* | −0.114 [−0.139, −0.091]* |
| LLM named fixed − Periodic | −0.018 [−0.032, −0.004]* | −0.562 [−0.632, −0.501]* |
| random slice 0.1 − 0 (re-asking) | +0.011 [−0.002, +0.024] | −0.040 [−0.072, −0.009]* |
| random slice 0.1 − 0 (fixed set) | −0.013 [−0.023, −0.004]* | +0.037 [+0.018, +0.057]* |

## Findings

**1. The cold start works as well as a week of history did.** Hypotheses written from one
tour, held fixed, score 0.620 / 1.332 — against 0.620 / ~1.33 for the earlier round's
hypotheses written from seven days of sightings. The 7-day history bought nothing. Same
shape as before against the no-LLM arm: no top-1 gain, a large log-loss gain (−0.56 nats).

**2. Re-asking made things worse, and the mechanism is visible.** Both revisions returned five
valid hypotheses (after a parser fix, below), yet the re-asking arm trails the fixed set on
every metric, by a lot in the anonymized condition (−4.9 points, +0.13 nats). Two causes:

- *The revisions reinstated the full rest map.* The cold-start hypotheses wrote **zero** rest
  entries; the day-7 revisions wrote 175 (named) and 122 (anonymized). Shown per-object
  statistics and an "objects no hypothesis covers" list, the model covered everything. But a
  stated rest is 3 pseudo-sightings on top of the real ones — after a week of data it is
  redundant at best and harmful whenever the guess deviates from the data.
- *Weight inheritance.* A revised hypothesis that keeps its id keeps its log-weight. The named
  day-7 revision rewrote h1 while it held 0.95 of the mixture; the mixture then spent days
  re-learning (h1 ended at 0.00, h2 at 0.93). Recomputing the weight by replaying the
  likelihood, rather than inheriting it, is the obvious fix — not applied, per the brief.

**3. Named ≈ anonymized on cold start — but not because names don't matter.** The fixed-set
arms are identical to three decimals; the median total-variation distance between their
predictions is **0.003**. The cold-start hypotheses cover 21–23 of 35 objects, 0–3 by all
five, with no rest entries; every uncovered object falls through to the converter's
statistical fallback, which is the same in both conditions. The particles disagree on the
argmax on 22% of questions. Dropping the rest-map rule — right for a household with data —
removed the one place a cold-start hypothesis states something about most objects. The
predicted "gap widest on day 0, shrinking" does not appear; the gap is ~0 through day 7
and opens *after* the day-7 revision, entirely because the anonymized revision was worse.

**4. The log-loss gain is NOT averaging over disagreeing hypotheses.** ESS in the passive
named arm sits at 1.0–1.5 for most of the episode: the weight is on one hypothesis at a
time. The gain comes from the winning particle's own distribution — rule overlay on a
72 h-decayed Dirichlet — being better calibrated than Periodic's, not from the mixture.
The active arms keep 2–4 effective particles (sensing adds evidence that keeps rivals
alive), which is where the mixture is doing mixture work.

**5. The per-object oracle exposes the cost of single-winner collapse.** A hindsight pick of
each object's best hypothesis saves 0.10 nats/question (fixed named). The gain is
concentrated on the carry items — phone, wallet, laptop, jacket, keys, headphones — all
best predicted by **h2 ("commutes")**, while the mixture sat on **h1 ("works from home",
weight 0.83)**. One hypothesis per household is the wrong granularity: the right hypothesis
differs by object. Negative bars (mug, glasses) are objects where the mixture beat every
single particle.

**6. The quality trigger never fired.** The 40-sighting running mean of `log p(sighting)`
stayed between −0.5 and −1.7 in every arm, above the −2.3 threshold — the mixture, with its
statistical particle, explained the patrol well enough. Only the scheduled asks ran. The
threshold is a knob; on this evidence it would need to sit near −1.5 to fire at all, and
the dips that deep coincide with days 3 and 7 anyway.

**7. Random slice: mixed, small.** With re-asking it helps log-loss (−0.040*); with the fixed
set it hurts (+0.037*); on Periodic nothing. Reading: the slice's value is in what it feeds
back — it helped only the arm that revises. The active LLM fixed arm answers as accurately
as Periodic (0.712 vs 0.714) with far better log-loss (0.99 vs 1.43).

**8. Unsensable destinations get only negative evidence.** An `OUT_OF_HOUSE` rule can never
be confirmed (nothing is sighted there) and only accrues failures when the object is seen
in-house during its window, so its fitted chance can only fall and it never reaches the
"held" threshold. The revision report is therefore silent on exactly the rules that matter
most for carry items; the anonymized revisions dropped their `OUT_OF_HOUSE` moves 4 → 0.
Same unobservability as the scoring fix, now in the feedback loop. Fix: count an empty look
at the object's expected in-house receptacles during the window as weak confirmation.

## Two things fixed mid-run

- `rest` came back as a list of `{"target": X, "at": Y}` in 4 of 8 revisions (the model
  generalized the `distinguishing_check` shape). The parser now accepts both shapes strictly;
  the first attempt is preserved as `*__rest_bug/`.
- Two hypotheses wanted per-weekday schedules (`tuesday_thursday`) and were correctly rejected
  by the weekday/weekend/both vocabulary; the repair round fixed them. The model wants finer
  day structure than the schema allows.

## Cost

Cold-start elicitation: 544 s / 15,291 tokens (named), 499 s / 14,019 (anonymized) — a third
cheaper than the history-fed prompt. Revisions: 8 calls, 434–1,696 s each; active arms
1,191 s and 1,171 s live generation. Total live LLM time this round ≈ 2.5 h including the
parser-fix rerun (cache replayed 6 calls free).

## Files

`results/llm_hypotheses/cold_start/hh_001/<arm>/` — `per_question.jsonl.gz` (mixture and
per-particle distributions, ESS, truth), `diagnostics.json` (re-ask events, sighting-quality
series, ESS history, final weights and hypotheses), `revisions/*.json` (every revision
prompt and response), `provenance.json`. `figures/` — the four figures, `tables.md`,
`per_object_oracle.json`. Code: `llm_hypotheses/{prompt,revise,run_cold_start,
analyze_cold_start}.py`, `beliefs/llm_hypothesis_mixture.py` (re-asking layer),
`policies/random_slice_sense.py`. 35 tests across the four new suites.

## Not done

hh_002; the weight-recompute fix; the unsensable-destination evidence fix; a rest-map policy
for cold start (e.g. rest required on day 0, dropped on revision); per-object hypothesis
selection. Each is a one-line finding above; none was in the brief.
