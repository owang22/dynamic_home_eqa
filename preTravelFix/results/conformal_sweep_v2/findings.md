# Conformal program v2: sensing on top of soft negative evidence

Inputs: the same 20 households as sweep v1 (10 calibration / 10 test,
split seed 0), the same alphas (0.02-0.5), plus `--taus 0.2,0.4,0.6,0.8`
and `--gammas 0.01,0.05,0.1` (ACI target alpha 0.3, the v1 sweep's best
static point). Two arms rerun unchanged from v1 (`sweep_results.csv`
etc. under `results/conformal_sweep_v2/` at the bank's default budget
and at budget 90), then three budgets {24, 45, 90} for the frontier.
Beliefs: the frozen panel plus PeriodicPersistence and HierarchyBackoff
(the same five as v1). Produced by
`python -m baselines.conformal.sweep`, `.frontier`, `.mechanism`.

## 1. Achievable alpha floor, old vs new semantics

"Achievable" here means the smallest alpha whose fitted global quantile
is meaningfully below 1 (`<= 0.9`; a threshold at `1.0 - epsilon` moves
trivially with the new floor mass alone and says nothing). Old vs new
compares `results/conformal_sweep_v1/alpha_to_0.5_budget90/calibration.json`
against `results/conformal_sweep_v2/budget90/calibration.json`, same
banks and split.

| belief | old floor | new floor |
|---|---|---|
| LastObservation | 0.4 | 0.4 |
| MostFrequentLocation | 0.4 | 0.3 |
| TimetableLookup | 0.4 | 0.4 |
| PeriodicPersistence | 0.4 | 0.4 |
| HierarchyBackoff | 0.4 | 0.3 |

The floor did NOT drop the way the brief expected ("honest OUT_OF_HOUSE
mass fixes a chunk of passive miscoverage"): unchanged for three
beliefs, one step better for two. This is the arithmetic already
flagged before the sweep and confirmed by the migration replay: floor
mass on OUT_OF_HOUSE is `0.02/N` (~0.001 on a 23-receptacle bank) and
decays no further, while the in-house nonconformity scores this
calibration is fit on are dominated by ordinary staleness (a stale but
not-yet-fully-decayed last-seen receptacle), which the floor does not
touch. The one place the new semantics genuinely helps calibration is
qualitative, not in the achievable alpha: at alpha 0.3-0.4 the raw
global qhat itself is far from 1 under the new pipeline (0.997 vs 1.000
old at alpha 0.3) — technically non-vacuous — but the resulting set
still contains nearly everything, so it buys nothing practical until
alpha crosses into the 0.4 regime where the real drop happens under
both semantics alike.

## 2. Mechanism table (B1)

Per-belief tables and generated verdicts: `mechanism_by_age_case.csv`,
`mechanism.md` (built from the budget-90 sweep's
`conformal_global_alpha0.3` dump, test households, joined against
`results/conformal_sweep_v1/alpha_to_0.5_budget90` for the old-semantics
memory-answer column). Three expectations, per belief:

- **Sensing pays in stale_in_house** (accuracy given sensed vs answered
  from memory): held for 4 of 5 beliefs — LastObservation 0.990 vs
  0.777, MostFrequent 0.864 vs 0.798, HierarchyBackoff 0.877 vs 0.818,
  TimetableLookup 0.955 vs 0.673. PeriodicPersistence did NOT hold
  (0.796 sensed vs 0.826 memory) — its own policy chose which questions
  to sense, so this is a within-policy split, not a controlled
  comparison; PeriodicPersistence's memory answer is already strong on
  the questions it chooses not to sense.
- **came_back now addressable by graded beliefs**: held for every
  graded model — MostFrequent 0.000 -> 0.960, Timetable 0.000 -> 0.892,
  PeriodicPersistence 0.000 -> 0.964, HierarchyBackoff 0.000 -> 0.906
  (n=1450, passive/NeverSense). LastObservation is one-hot and not
  expected to move on this split (it went 0.000 -> 1.000 too, which is
  a byproduct of exact recency rather than graded reasoning).
- **truly_out near-worthless per single sense, but reachable by passive
  answering**: the first half held (first-sense hit rate ~0.000 for
  every belief, n=600-1000) — a single sense essentially never lands on
  a truly-out object, confirming sensing cannot fix this regime.
  The second half did NOT hold: memory-answer accuracy on truly_out
  fell from ~0.21 (old) to ~0.000 (new) for every belief. This is the
  same floor-mass arithmetic as section 1 and the migration replay's
  headline finding: passive OUT_OF_HOUSE answering is not reachable
  under a uniform floor design.

## 3. Does ResolvableMassSense dominate conformal-global?

Two ways to ask this, both reported (`results/conformal_sweep_v2/frontier.csv`,
`frontier.md`, `frontier.png`):

**Against ANY conformal-global/age-binned configuration** (i.e. is there
some tau that beats some alpha at equal-or-lower cost): yes, for every
belief at every budget — dozens of dominating pairs each cell. This is
the weak form; conformal has many alpha choices that are simply bad
(too conservative, sensing when it buys nothing), and beating one of
those is not interesting on its own.

**Against conformal's OWN best point on its frontier** (i.e. its
best-accuracy alpha/mode at that budget): the fairer test. At budget 90,
ResolvableMassSense wins outright for 3 of 5 beliefs — LastObservation
0.804 vs 0.784 (+0.020, at comparable cost 0.78 vs 0.70 senses/q),
TimetableLookup 0.741 vs 0.674 (+0.067, 1.00 vs 0.80 senses/q),
PeriodicPersistence 0.854 vs 0.852 (+0.002, near-tied) — and loses for
2 (MostFrequent 0.817 vs 0.835, HierarchyBackoff 0.791 vs 0.820,
conformal's age-binned mode ahead by 0.02-0.03). At budget 45 conformal-
global(alpha=0.5) is ahead on 4 of 5 beliefs, sometimes by a wide margin
(MostFrequent 0.739 vs 0.697, PeriodicPersistence 0.762 vs 0.726); at
budget 24 the two are within 0.005 of each other everywhere. So: no
uniform winner. ResolvableMassSense's advantage shows up specifically
at the highest budget on beliefs whose set often has one clearly-
dominant sensable member plus scattered small mass elsewhere (its gate
skips sensing when that scattered mass is below tau); conformal-global
is competitive-to-better in the middle budget where matching the
promised coverage rate directly captures more value than gating on
resolvability. Full grid across all (belief, budget, policy) triples in
`frontier.csv`.

## 4. ACI: coverage under drift, and the sensed-vs-oracle feedback gap

Per-day, per-belief coverage of the FIRST-decision prediction set
(before any sensing) against the target 1 - alpha = 0.70, gamma 0.05,
budget 90, `aci_coverage.csv`:

| belief | static mean (sd) | oracle-ACI mean (sd) | sensed-ACI mean (sd) |
|---|---|---|---|
| LastObservation | 0.748 (0.030) | 0.701 (0.017) | 0.634 (0.069) |
| MostFrequentLocation | 0.692 (0.064) | 0.701 (0.012) | 0.607 (0.060) |
| TimetableLookup | 0.732 (0.050) | 0.701 (0.012) | 0.542 (0.072) |
| PeriodicPersistence | 0.701 (0.058) | 0.702 (0.017) | 0.605 (0.063) |
| HierarchyBackoff | 0.704 (0.065) | 0.701 (0.012) | 0.621 (0.059) |

(mean/sd over the 25 query days; target 0.70.)

**Static vs oracle-ACI under drift**: for two of five beliefs (LastObs,
Timetable) the static calibration's day-averaged coverage sits 0.03-0.05
above target with day-to-day spread (sd) 0.03-0.05; oracle-feedback ACI
pulls the mean back onto target (0.701-0.702 for all five) and roughly
halves to a third of the spread (sd 0.012-0.017). For the other three
beliefs static was already close to target on average, but still noisier
day to day than ACI. So: ACI holds target coverage tighter than static
calibration everywhere in this run, and corrects a real miscalibration
for two of five beliefs — though the "drift" here is calibration-vs-test-
household mismatch from the one-time split, not within-household drift
over the 25 days (the households don't have enough non-stationarity in
this bank for day-to-day static failure to show up as a trend; STATUS's
rate-sweep entry has the discussion of how much these banks drift).

**Sensed vs oracle feedback**: the deployable feedback mode badly
undercovers — 0.54-0.63 mean coverage against the 0.70 target, a
persistent 0.07-0.16 gap below oracle's near-exact tracking, and *worse*
day-to-day spread than oracle (sd 0.06-0.07 vs 0.01-0.02) despite
similar mean alpha values by the end of the run (e.g. LastObs: oracle
mean_alpha 0.344, sensed mean_alpha 0.345 at gamma 0.1 — the two land in
a similar place but sensed's PATH there is noisy and slow). The cause is
selection: sensed feedback only fires on the ~1-4% of questions whose
own senses revealed the truth (`update_rate` in the csv), so alpha
tracks only a biased, sparse subsample and drifts too slowly to correct
transient runs of over- or under-coverage on the other 96-99% of
questions, which the coverage metric (measured on every question) still
counts against it. The ceiling-vs-deployable gap is real and large: a
system that can only use its own senses as calibration feedback should
not expect ACI to hold the promised coverage at these budgets, however
close oracle feedback makes it look.

## Summary

1. The floor-mass design does not lower the achievable alpha the way
   hoped; OUT_OF_HOUSE's floor share is too small to matter to
   calibration except at alpha already near 0.4-0.5, where the drop
   happens under both semantics.
2. The mechanism table's three expectations mostly held (sensing pays
   in stale_in_house, came_back addressable) with one clean exception
   each: PeriodicPersistence's own sensing choices already capture its
   easy memory cases, and truly_out passive answering is NOT reachable
   (confirms the migration replay's headline caveat with a second,
   independent measurement).
3. ResolvableMassSense dominates conformal-global's OWN best frontier
   point at the highest budget for 3 of 5 beliefs, loses at the middle
   budget for most, and ties at the lowest — no uniform winner, but a
   real and belief-dependent advantage at high budget where its
   resolvability gate has room to work.
4. ACI with oracle feedback holds target coverage tighter than static
   calibration (lower day-to-day variance everywhere, corrects a real
   0.03-0.05 static miscalibration for two of five beliefs); with
   sensed-only feedback it badly undercovers (0.07-0.16 below target)
   because its update rate is only 1-4% of questions and those are a
   biased subsample — the honest, deployable version of ACI on this
   task does not hold the promised coverage at these budgets.
