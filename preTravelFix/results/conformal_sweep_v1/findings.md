# Conformal-triggered sensing on the fleet banks

Inputs: the 20 current households (`households__generated__gpt-5.6-terra__hh_001..020`,
seed-0 timelines, 28 days, 90 questions/day from day 3, round-robin room
visits). Household split by salted hash, split seed 0, 10 calibration /
10 test households (22,500 test questions per cell). Beliefs: the frozen
panel plus PeriodicPersistence and HierarchyBackoff. Produced by
`python -m baselines.conformal.sweep` (see `provenance.json` beside each
arm; the per-question dumps are regenerable and gitignored).

Two arms:

- `./` — the brief's defaults: alphas 0.02/0.05/0.1/0.2, the bank's own
  budget of 24 senses/day.
- `alpha_to_0.5_budget90/` — alphas up to 0.5 and `--budget 90` (one
  sense per question), the regime where the calibration actually bites.

## What the default arm shows

At alpha <= 0.2 the conformal quantile is vacuous (qhat = 1.0) in every
age bin for every belief but one cell: passive miscoverage on these banks
is ~0.45 overall (0.17 at 0-6 h, 0.40 at 6-24 h, 0.61 at 24-72 h, 0.63
at 72 h+), far above alpha, so the only set that meets the target is
"every receptacle". ConformalSense then senses on every question, and
with 24 senses for 90 questions the budget is exhausted early every day
by every sensing policy: all of them land on exactly 24 senses/day and
within +-0.005 of SequentialSearch's accuracy. The default arm cannot
separate global from age-binned calibration.

## Three-line summary (the PR questions)

1. Yes: global calibration under-covers old-age bins badly. At alpha 0.4
   (target 0.60) one global quantile covers 0.75-0.83 at 0-6 h, ~0.60 at
   6-24 h, 0.39 at 24-72 h and 0.37 at 72 h+, for every belief; age-binned
   fitting puts a vacuous quantile on the two old bins (coverage 1.0) and
   a tight one on the young bins (0.60-0.63 at 0-6 h).
2. No: age-binned calibration does not save budget at equal accuracy. In
   the budget-90 arm the best point for every graded belief is GLOBAL
   alpha 0.3 (PeriodicPersistence 0.810 accuracy at 0.85 senses/question,
   MostFrequent 0.800 at 0.95, HierarchyBackoff 0.799 at 0.94); the
   age-binned policies at comparable budget sit 0.02-0.05 lower
   (PeriodicPersistence 0.794 at 0.91, 0.782 at 0.80), because sensing
   every old question and rarely sensing young ones is the wrong
   allocation: the young questions are the ones a single sense resolves.
3. The bank's 24 senses/day cap makes every sensing policy identical, so
   the sense-or-answer trade-off has to be read at a larger budget; the
   headline gain there is conformal global alpha 0.3 over
   SequentialSearch at LOWER budget (+0.09 accuracy at 0.85 vs 1.00
   senses/question for PeriodicPersistence).
