# Fleet failure diagnoses

Companion to `fleet_summary.md` (same run: config
`src/baselines/configs/fleet.yaml`, seed 0). Every bank ran under the
one shared hh1 recipe (90 questions/day from day 3, 10 sightings/day,
budget 24/day, uniform queries in the household's own awake time). 11 of
12 banks fail at least one gate. Per the fleet rules, nothing was tuned
per bank and no household content was edited; diagnoses below classify
each failure as generator content, instrument-scale mismatch, or
hard-but-healthy, for the generation workstream to act on.

## The two precedent failure classes were checked first — both clean

- **Duplicate YAML mapping keys silently dropping movement rules** (the
  hh1 cereal-bowl precedent): a duplicate-key scan over every fleet
  household's YAML files (`persona/detailed_activities/object_motions`
  for revamp_v1, `persona/story/program/object_movement/
  expanded_motions` for storyfirst) found **zero duplicate mapping
  keys**. The revamp_v1 simulator also rejects them loudly since the
  original fix.
- **Question window misaligned with the household's awake time** (the
  night-shifter precedent): questions and sightings are drawn from
  resident non-sleep blocks since that fix, and a direct audit of all 12
  exported banks measured **0.000** of question times inside
  whole-household sleep in every bank (storyfirst sleep blocks are named
  `night_sleep*`/`nap*`, which the exporter's sleep filter matches).

Neither precedent recurs. The failures below have three other causes.

## Cause 1 — discriminative collapse: the shared sighting budget starves
## per-object evidence on large inventories (11/12 banks; instrument-scale
## mismatch, not a content bug)

`discriminative` needs the three panel beliefs to spread > 0.03
somewhere. Measured spread against per-object evidence rate (10
sightings/day shared across the whole inventory, 21 days):

| bank | objects | sightings /object/day | spread | verdict |
|---|---|---|---|---|
| revamp_v1 hh1 | 17 | 0.51 | 0.052 | PASS |
| revamp_v1 hh3 | 26 | 0.38 | 0.006 | FAIL |
| storyfirst hh1 | 30 | 0.26 | 0.022 | FAIL |
| storyfirst hh10 | 28 | 0.32 | 0.001 | FAIL |
| storyfirst hh2 | 36 | 0.21 | 0.006 | FAIL |
| storyfirst hh3 | 39 | 0.25 | 0.012 | FAIL |
| storyfirst hh4 | 53 | 0.15 | 0.003 | FAIL |
| storyfirst hh5 | 35 | 0.23 | 0.006 | FAIL |
| storyfirst hh6 | 43 | 0.19 | 0.004 | FAIL |
| storyfirst hh7 | 32 | 0.29 | 0.015 | FAIL |
| storyfirst hh8 | 36 | 0.27 | 0.010 | FAIL |
| storyfirst hh9 | 51 | 0.17 | 0.004 | FAIL |

The mechanism: with ~3-6 sightings per object over the whole episode, a
history is a handful of points — the mode of a 4-point histogram IS the
most recent point most of the time, and the timetable's 1-hour bins are
almost always empty so it runs its most-frequent fallback. All three
beliefs then answer from nearly identical evidence and the spread
collapses. hh1's PASS at 0.51 sightings/object/day (the level the recipe
was calibrated at, on a 17-object inventory) against the monotone
collapse below ~0.3 makes the cause clear. This is not a generator
defect and not an exporter defect: it is the shared config's FIXED
10/day sighting rate meeting inventories 2-3x larger than the one it was
tuned on. **Recommendation to the workstream**: revise the instrument
config globally (deliberately, once) to scale ambient evidence with
inventory, e.g. sightings_per_day = ceil(0.5 x n_objects) — the rate
per object hh1 passed at — and re-run the fleet. Per-bank tuning stays
prohibited; this is a single global rule change.

> **TESTED — see `sighting_scale_experiment.md`.** The diagnosis holds:
> scaling sightings with inventory cuts discriminative failures from
> 11/12 to 1/12, and spread rises monotonically with evidence on every
> probed bank, so the beliefs were being starved into agreement rather
> than being inherently alike. Two corrections to this paragraph. The
> dosage proposed here (0.5/object/day) is TOO LOW — it lands under the
> 0.03 gate on all four probed banks and even regresses the hh1
> calibration bank from PASS to FAIL, because the 0.51 figure above
> ignores that ~15% of draws are dropped as unobservable while the
> object is out of the house. The measured feasible rate is
> **1.0/object/day**. And the fix is not free: more evidence raises
> passive accuracy, which pushes three already-stationary banks past the
> `not_trivial` ceiling and raises the bar `not_impossible` must clear —
> so fix stationarity (Cause 3) FIRST.

## Cause 2 — not_impossible: budget 24 buys < 0.15 over passive on big,
## busy houses (10/12 banks; partly the same scale mismatch, partly
## hard-but-healthy)

`search@24` margins over the best passive belief: +0.174 (hh1 v1, PASS)
and +0.215 (storyfirst hh10, PASS) versus +0.01..+0.14 elsewhere. Two
compounding mechanisms, both visible in the bank tables:

- **More receptacles per sense.** The hh1 recipe was budgeted for 15
  sensable receptacles; storyfirst houses have 22-35. A sequential
  search that misses pays proportionally more budget per find, and
  OUT_OF_HOUSE answers (11-19% of questions on the family/commuter
  banks: hh1 0.18, hh2 0.19, hh4 0.18, hh6 0.16, hh9 0.15) are provable
  only by sweeping every sensable receptacle — at 30+ receptacles that
  is more than a day's budget for one question.
- **More churn than budget.** The multi-resident banks move 100-210
  objects/day (hh4: 211, hh6: 196, hh2/hh3: 105) against 24 senses/day;
  evidence goes stale before it can be revisited. This is the "world
  outruns finite sensing" regime that is genuinely the task — on a
  smaller inventory it would read as hard-but-healthy.

Classification: the low margins are dominated by the same instrument
scale mismatch as Cause 1 (budget fixed while house size grew). Where
the margin is smallest (revamp_v1 hh3 at +0.012), the primary cause is
Cause 3 below: passive is already high because the world barely moves,
so sensing has little left to buy. **Recommendation**: revisit the
budget as part of the same single global config revision (e.g. budget
proportional to sensable receptacles), and re-test not_impossible after
the stationarity content fixes land.

## Cause 3 — stationarity: dead-inventory objects drag modal share over
## 0.60 (6/12 banks; generator CONTENT problem — flagged, not fixed here)

Failing banks and their concrete artifacts (per-object dwell-weighted
modal share from the healthcheck reports):

- **revamp_v1 hh3** (0.685): 5/26 objects >= 0.95 — `charger_hall`
  (1.00), `wallet_gordon` (0.98), `laptop_shared` (0.96),
  `book_meilin`/`wallet_meilin`/`notebook_meilin` (~0.95). The retired
  couple's object_motions rules for these objects fire rarely or move
  them home within minutes.
- **storyfirst hh1** (0.622): `blanket_elena`, `laundry_basket_elena`
  (1.00 — never move at all), `watering_can_elena` (0.97), `bowl_2`
  (0.96).
- **storyfirst hh3** (0.613): `vacuum_cleaner_1`, `laundry_basket_1`
  (0.99); plus a long tail of 0.8-class objects.
- **storyfirst hh7** (0.668): `watering_can_leena`,
  `laundry_basket_leena` (1.00), `yoga_mat_leena` (0.99), and 0.87-0.90
  for towel/suitcase/backpack — a WFH persona whose rules rarely fire.
- **storyfirst hh8** (0.623): `laptop_nadia`, `yoga_mat_nadia`,
  `vacuum_cleaner_1` (1.00), `keys_nadia` (0.96 — keys that never
  leave!).
- **storyfirst hh9** (0.653): 8/51 objects at ~1.00 (`laptop_priya`,
  `notebook_priya`, `pen_priya`, `medication_bottle_eli`,
  `yoga_mat_eli`, `vacuum_cleaner_1`, ...).

Pattern: chore/utility objects (laundry baskets, vacuum cleaners,
watering cans, yoga mats) get inventory slots but no movement program
that actually fires, and several personal items are anchored to one
resident spot. Each 1.00-share object adds ~1/n_objects of pure
stationarity. Per the fleet rules these are flagged for the generation
workstream (either give the utility objects real usage rules with dwell,
or drop them from the inventory); household YAML was not edited.

## Per-bank verdicts

| bank | failing gates | classification |
|---|---|---|
| revamp_v1 hh3 | stationarity 0.685, not_impossible +0.012, discriminative 0.006 | content (Cause 3) + scale (Causes 1-2) |
| storyfirst hh1 | stationarity 0.622, not_impossible +0.136, discriminative 0.022 | content + scale |
| storyfirst hh10 | discriminative 0.001 | scale (Cause 1) only — otherwise the healthiest storyfirst bank |
| storyfirst hh2 | not_impossible +0.079, discriminative 0.006 | scale |
| storyfirst hh3 | stationarity 0.613, not_impossible +0.081, discriminative 0.012 | content + scale |
| storyfirst hh4 | not_impossible +0.053, discriminative 0.003 | scale (largest house: 53 objects, 32 receptacles, 211 moves/day) |
| storyfirst hh5 | not_impossible +0.096, discriminative 0.006 | scale |
| storyfirst hh6 | not_impossible +0.033, discriminative 0.004 | scale |
| storyfirst hh7 | stationarity 0.668, not_impossible +0.123, discriminative 0.015 | content + scale |
| storyfirst hh8 | stationarity 0.623, not_impossible +0.138, discriminative 0.010 | content + scale |
| storyfirst hh9 | stationarity 0.653, not_impossible +0.093, discriminative 0.004 | content + scale |

No exporter or simulator plumbing defect surfaced in this run: solvable
is 1.000 and powered is 1620 on every bank, both precedent classes are
clean, and every failure traces to bank content or to the fixed
instrument scale meeting bigger households.
