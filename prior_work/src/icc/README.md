# icc/ — intraclass correlation per activity, from ATUS + CASAS

## Purpose and method

How much of the day-to-day variation in when a household does something is
**stable personal habit** versus **day-to-day noise**? That ratio is what a
household simulator needs: it decides how much a generated person should
resemble themselves from one day to the next. It is the intraclass
correlation

    ICC_a = sigma2_between / (sigma2_between + sigma2_within)

and neither available dataset can estimate it alone. ATUS observes **many
persons for one day each**, so its cross-sectional variance is
`sigma2_between + sigma2_within` with no way to separate the two. CASAS
observes **a few homes for many days**, which gives `sigma2_within` but
cannot estimate a population's between-person spread from four homes.
Together they can, by subtraction:

    ATUS  (many persons x 1 day)     -> sigma2_total  = between + within
    CASAS (few persons x many days)  -> sigma2_within
    ICC = 1 - sigma2_within / sigma2_total

The whole design follows from one constraint: **the subtraction is only
valid if both sources are reduced to the same measurement, on the same
activity vocabulary, with the same covariates removed.** Hence one
day-level schema (`schema.py`), one versioned crosswalk (`crosswalk.csv`),
and two loaders that share both.

## Data provenance and access

Neither input may be redistributed; both stay out of the repo (`.gitignore`)
and the tools regenerate everything from a fresh download.

| input | what | how to obtain |
|---|---|---|
| `atus/atus_00002.dat.gz` | IPUMS ATUS hierarchical extract, 198,090 respondent-days, **2006–2025** (2009 absent from this extract), 3,778,113 activity records | build an extract at [ipums.org/atus](https://www.ipums.org/atus); IPUMS terms of use forbid redistribution |
| `casas/{aruba,cairo,milan,tulum2}/activities.csv` | labelled ADL episodes from four CASAS free-living testbeds (220 / 57 / 62 / 147 days) | Zenodo record 17180309; only labelled activity intervals are kept, never raw sensor streams |

Checksums (first 16 MiB + byte length) of every input are recorded in
`reports/icc/provenance.json` on each build, along with the git commit, the
crosswalk version and hash, the RNG seed, and library versions.

The ATUS extract carries no DDI codebook, so its fixed-width layout was
inferred and then validated against the survey's own invariants — see
`atus/README.md`. Relevant here: the diary date sits at person-record offset
40 and was confirmed by reproducing ATUS's deliberate weekend oversampling
(Sat 24.2% / Sun 25.8% / weekdays ~10% each).

## Activity crosswalk

`crosswalk.csv` — one row per canonical activity, with the mapping to raw
CASAS labels and ATUS code prefixes, the measurement rules, and a
**rationale column stating what is known to be wrong with it**. It is
versioned; downstream artefacts pin its hash. Current version: **4**.

Included: `wake`, `sleep`, `meal_prep`, `eating`, `dishes`, `housekeeping`,
`leisure`, `work_home`, `leave_home`, `hygiene`.

Deliberately excluded, with reasons in the file:

* `bed_toilet` — CASAS senses nocturnal bathroom trips reliably; ATUS
  respondents do not report them. Including it would yield a spuriously low
  ICC driven by measurement asymmetry, not behaviour.
* `meds` — two testbeds, 19–44 episodes, and ATUS 010301 is far broader
  than taking a pill.
* `idiosyncratic` — single-testbed labels with tiny counts, or pure
  room-presence labels (`Master_Bedroom_Activity`) with no activity
  semantics.
* `wake_labels` — cairo's explicit `R1_Wake`/`R2_Wake` labels. Waking is
  derived from sleep episodes in every source instead, so the `wake`
  variance cannot be partly a variance of labelling method across testbeds.

Known ambiguities, recorded rather than hidden: milan's `Kitchen_Activity`
is a superset of meal preparation (it also covers eating and cleanup in that
testbed's labelling); milan's bathroom labels are room presence, not
hygiene; aruba's `Relax` is a leisure catch-all firing ~13x/day.

## Estimation procedure

**Day boundary at 04:00**, not midnight, so a night's sleep is not split in
two; this also matches the ATUS diary window exactly. `start_min` is minutes
from that boundary.

**Canonical statistic per (person, day, activity)** — otherwise
multi-occurrence activities produce meaningless start variance:
`start_min` from the activity's start rule, `duration_min` = SUM of
occurrences, `n_occurrences` = count.

**Start rules** (per activity, in the crosswalk): `first`, `last`,
`spans_end` (the onset of the episode still running at the window end — how
bedtime is defined), `none` (a start time is not a meaningful quantity, used
where an activity fires many times a day). Waking is the end of the episode
already running at the window *start*, the mirror of `spans_end`.
No circular statistics are needed anywhere, which is the reason for the
04:00 anchor; any future activity that genuinely wraps must declare `none`
or the crosswalk review must add circular handling.

**Episode merging** (`merge_gap_min`, 60 min for sleep and wake): ambient
sensors fragment one night's sleep into several episodes where self-report
records one. Unmerged, CASAS "waking" caught a 01:30 interruption and
"bedtime" a 03:00 re-settle — within-person SDs of 5.2 h and 2.8 h that are
artefacts of labelling granularity.

**CASAS episode-to-day assignment is by OVERLAP**, not by start: an episode
running 23:00 → 07:00 contributes to two diary days, exactly as an ATUS
window would split it.

**sigma2_within (CASAS)** is the residual scale of a random-intercept model,

    value ~ C(dow_type),  groups = person_id          (statsmodels MixedLM)

The random intercept absorbs each person's habitual level — that is
between-person variance and must not leak into the within estimate — and the
weekday/weekend fixed effect absorbs the regime difference, which is
structure the simulator models explicitly rather than noise.

**sigma2_total (ATUS)** is the **weighted** variance of the same day-level
statistic after removing the weighted weekday/weekend means — the same
covariate, removed the same way, so the two numbers are commensurable.

**Measures**: `start_min`; `log_duration` (durations are right-skewed, so a
raw-scale variance is dominated by the tail); `participation`.

**De-heaping.** ATUS respondents round reported times to :00/:15/:30, a
spike comb that inflates the raw variance. Each day-level statistic is
de-heaped by inferring granularity from its own modulus (30 → 15 → 10 → 5 →
1 min) and adding U(−g/2, +g/2), seeded. Jitter is applied to the
STATISTIC, never to raw episode boundaries, so diary contiguity is never
broken. CASAS timestamps are sensor-derived and need no de-heaping, which
is precisely why the ATUS side must be corrected before comparison.

**Weights.** ATUS oversamples weekends, so unweighted moments are not
population moments; every respondent carries the final weight from the
person record. **2020 is excluded**: this extract's weight field is blank
for all 8,782 diaries of that year (2020 needs ATUS's special
pandemic-period weight, a different variable) *and* 2020 contains a
structural break (collection suspended 2020-03-18 to 2020-05-09; the rest
are lockdown days). Either reason alone would justify exclusion.

**Uncertainty** is a block bootstrap (B = 200): persons resampled with
replacement, and within a person contiguous 7-day blocks resampled rather
than individual days — day-level resampling would destroy the serial
correlation `phi_ar1` measures and understate the within-person variance's
uncertainty. ATUS diaries are resampled with replacement in the same draw,
so the CI covers both sides of the identity.

**phi_ar1** is the lag-1 autocorrelation of person-demeaned residuals
ordered by date, averaged over persons: the "streaky week" parameter a day
generator needs. `resid_skew`/`resid_kurtosis` are reported so a sampler can
choose a heavy-tailed draw where warranted rather than assuming Gaussian.

**Participation** is reported as variance components on the 0/1 scale
(method of moments), NOT as a binomial GLMM: with six CASAS person levels a
GLMM's person-level variance is not identified, and reporting one would
imply precision that is not there.

## Guardrails

* **A negative ICC is never clamped.** `sigma2_within > sigma2_total` means
  the two sources are not measuring the same thing — crosswalk mismatch,
  differing measurement noise, or CASAS residents genuinely more erratic
  than the ATUS population. Such rows get `status = FLAGGED_NEGATIVE`, are
  excluded from the automated path, and require a documented manual
  resolution. The note records whether the bootstrap CI includes zero
  (consistent with a true ICC of 0) or excludes it (a substantive
  source disagreement).
* **Degenerate measures** are separated from negative ones: 99.9% of ATUS
  respondents sleep on any given day, so "does this person sleep?" has no
  between-person variance to estimate. Those rows are
  `DEGENERATE_NO_VARIANCE`, not an ICC near ±infinity.
* **Insufficient data** is reported, not estimated: a row needs ≥ 3 CASAS
  persons with ≥ 10 valid days each and ≥ 500 ATUS diaries.
* **`valid_day` is a flag, never a silent drop**, and every exclusion is
  counted in `provenance.json` (`drops`).

## Outputs

`reports/icc/icc_table.csv`, one row per (activity, measure):

| field | units | meaning |
|---|---|---|
| `activity` | — | canonical activity id (crosswalk) |
| `measure` | — | `start_min` \| `log_duration` \| `participation` |
| `status` | — | `OK` \| `FLAGGED_NEGATIVE` \| `DEGENERATE_NO_VARIANCE` \| `INSUFFICIENT_DATA` |
| `n_casas_persons` | count | CASAS person levels contributing (≥ 10 valid days each) |
| `n_casas_days` | count | CASAS person-days used |
| `n_atus_diaries` | count | ATUS respondent-days used |
| `sigma2_within` | min² (or log-min², or 0/1 var) | CASAS residual scale |
| `sigma2_total` | same as above | ATUS weighted variance, dow-adjusted |
| `icc` | — | `1 − within/total`; NaN when not estimable |
| `icc_lo`, `icc_hi` | — | 2.5 / 97.5 percentile, block bootstrap |
| `phi_ar1` | — | lag-1 autocorrelation, person-demeaned |
| `resid_skew`, `resid_kurtosis` | — | shape of the within-person residuals |
| `note` | — | why a row is flagged, and what to do about it |

`reports/icc/sensitivity.csv` — the same ICCs shifted ±0.15 and clipped to
[0, 1]; downstream work should show its conclusions do not turn on which
column it used. `reports/icc/provenance.json` — checksums, versions, seeds,
counts, drop reports.

## Results (crosswalk v4, seed 0)

21 estimable rows: **15 OK**, 3 `FLAGGED_NEGATIVE`, 1
`DEGENERATE_NO_VARIANCE`, and start/duration rows for `dishes`,
`housekeeping` and `hygiene` at `INSUFFICIENT_DATA`.

Timing habits are strongly personal — activity start times carry the
highest ICCs (`meal_prep` 0.82, `wake` 0.56, `eating` 0.59, `work_home`
0.58, `sleep` bedtime 0.53, `leave_home` 0.46) — whereas how LONG an
activity lasts is much less so (`meal_prep` log-duration 0.46, `work_home`
0.43, `leisure` 0.17, `eating` 0.01). Whether an activity happens at all is
nearly all between-person for optional activities (`hygiene` 0.99,
`meal_prep` 0.98, `leisure` 0.83) and near zero for `work_home` (0.00,
flagged). `phi_ar1` is small throughout (−0.03 … 0.34), so day-to-day
residuals are close to independent once the person's level and the
weekday/weekend regime are removed; `housekeeping` participation (0.34) and
`leisure` duration (0.30) are the streakiest.

Three flagged rows, each a real finding rather than a bug:

1. `sleep` **log_duration** (ICC −1.72, CI −6.56…0.30). CASAS nightly sleep
   duration varies far more than ATUS's, because an unlabelled night
   truncates the measured total while self-report always reports a full
   night. CI includes 0.
2. `eating` **participation** (−0.95, CI −2.80…1.00). ATUS respondents eat
   on 96% of days; CASAS misses eating episodes on some days. Sensor recall,
   not behaviour.
3. `work_home` **participation** (−0.04, CI −0.94…0.89). Indistinguishable
   from zero — consistent with a true ICC of 0, i.e. whether someone works
   at home on a given day is not a stable trait in this CASAS sample.

## Assumptions and known biases

A reviewer should be able to attack these one at a time.

1. **CASAS demographic skew.** Four homes, skewed single-occupant and older
   than the ATUS population. Their `sigma2_within` may not be the general
   population's. Unquantified; `sensitivity.csv` exists for this reason.
2. **Household-level labels in multi-resident homes.** Most CASAS labels are
   home-level. In cairo and tulum2 (two residents each), a home-level label
   mixes residents, inflating its day-to-day variance and therefore biasing
   ICCs **downward**. Resident-tagged labels (`R1_`/`R2_`) are split
   correctly; the rest are not.
3. **Cross-source measurement asymmetry.** Sensors and self-report fail
   differently — sensors miss unlabelled episodes, respondents forget short
   ones and round times. Episode merging and de-heaping address the two
   largest known asymmetries; others remain.
4. **The crosswalk itself.** Many-to-one mappings (`Kitchen_Activity`,
   `Relax`) are judgement calls; each is recorded with a confidence level.
5. **ATUS self-report error** beyond heaping (recall bias, social
   desirability) is not modelled.
6. **One diary day per ATUS respondent** means `sigma2_total` is estimated
   across persons and days simultaneously; the decomposition assumes the
   within-person component is homogeneous across the population.
7. **2009 is absent** from this extract, and 2020 is excluded by us; the
   remaining span is 2006–2025.
8. **`phi_ar1` is estimated from ≤ 220-day CASAS series** on four homes, so
   it is indicative rather than precise.

## Validation

`tests/test_icc_*.py` (30 tests):

* **synthetic recovery** — the estimator is run on data whose true
  components are known by construction: a true ICC of 0.835 is recovered to
  within 0.06, `sigma2_within` to 15%, `sigma2_total` to 5%, and a known
  AR(1) φ = 0.6 to within 0.08. A sampler or algebra bug is invisible in the
  output otherwise.
* **guardrails** — a deliberately erratic synthetic panel yields a negative
  ICC that is flagged and *not* clamped; a universal participation measure
  is `DEGENERATE`, not negative; two CASAS persons trigger
  `INSUFFICIENT_DATA`.
* **Stage A reductions** — day boundary, clipping, each start rule, the
  `spans_end` rule specifically rejecting a day whose evening sleep went
  unlabelled, merging, and the merge-repairs-the-measure case.
* **crosswalk invariants** — every mapping has a rationale; included
  activities have both sides; a label may feed at most one duration-bearing
  activity; mixed versions rejected.
* **regression pin** — the committed table's values are pinned, and the
  committed provenance must carry the current crosswalk hash, so editing the
  crosswalk without rebuilding fails the suite.

## Reproduction

```bash
# environment: python 3.11, numpy 1.26.4, scipy 1.12.0, statsmodels 0.14.0
PYTHONPATH=src python -m icc.cli build --out reports/icc --seed 0
PYTHONPATH=src python -m pytest tests/test_icc_*.py -q
```

Runtime ~3 minutes, dominated by one streaming pass over 3.8 M ATUS
activity records (22 s) and 200 bootstrap resamples per row. Fully
determined by `--seed` (de-heaping jitter and both bootstraps); rebuilding
with the same seed and inputs reproduces `icc_table.csv` byte for byte.

## Versioning policy

`crosswalk.csv` carries a single `version` on every row; any semantic change
bumps all rows together and requires a rebuild. `provenance.json` pins the
crosswalk version *and* content hash next to the table's own hash, and a
test fails if the committed table was built against a different crosswalk.
Downstream profile banks should pin the crosswalk version and the
`icc_table_sha256` they consumed, the same discipline as a charter loader
refusing a DRAFT profile.

## Limitations

This package **measures** the ICC; it does not yet build profiles from it.
The remaining half of the design — per-household profile construction
(`person_mean = cluster_mean + icc * (observed − cluster_mean)`, with
weekday and weekend regimes drawn from clustered ATUS respondents), the
AR(1) latent day factor generator, and the round-trip variance check that
regenerates N synthetic profiles and recovers both input variances — is not
implemented here. `phi_ar1`, the residual shape columns, and
`sensitivity.csv` exist so that step can be built without re-deriving
anything.

## Citation

American Time Use Survey, IPUMS ATUS (Hofferth, Flood, Sobek, Backman).
CASAS smart-home datasets, Center for Advanced Studies in Adaptive Systems,
Washington State University (Cook et al.). Both require citation per their
own terms; neither is redistributed here.
