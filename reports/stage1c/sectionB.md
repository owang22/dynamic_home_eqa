# Stage 1c — Section B (re-analysis on existing episode ep049w)

All CIs are 95% bootstrap CLUSTERED BY OBJECT (resample objects with replacement);
n_obj = object-cluster count (the real n), n_probe = probe count.

## B1. Within-stratum predictability attribution

Displaced location_now, b3(schedule_prior) vs b2, split at the predictability median
WITHIN each stratum:

| stratum | pred half | n_obj | b3 | b2 | lead |
|---|---|---|---|---|---|
| dynamic | low (med=0.459) | 6 | 0.337 [0.207,0.455] (n_obj=6, n_probe=3481) | 0.319 [0.262,0.369] (n_obj=6, n_probe=3481) | +0.018 |
| dynamic | high (med=0.459) | 5 | 0.547 [0.264,0.876] (n_obj=5, n_probe=3020) | 0.373 [0.326,0.406] (n_obj=5, n_probe=3020) | +0.174 |
| occasional | low (med=0.667) | 6 | 0.369 [0.190,0.552] (n_obj=6, n_probe=1970) | 0.400 [0.269,0.559] (n_obj=6, n_probe=1970) | -0.031 |
| occasional | high (med=0.667) | 6 | 0.173 [0.036,0.375] (n_obj=6, n_probe=1014) | 0.258 [0.144,0.399] (n_obj=6, n_probe=1014) | -0.086 |

Per-object paired lead vs predictability within the dynamic stratum:
Spearman rho=0.573 (p=0.066, 11 objects). CSV: b1_within_stratum.csv.

**Outcome: predictability has independent explanatory power within the dynamic stratum**
(high +0.174 vs low +0.018). It does NOT extend to the occasional stratum (both halves
negative): with 7 training days an occasional mover yields too few transitions to learn
per-object timing, and repeat24h inflates rare movers' predictability scores. Supported
claim: b3 beats b2 on objects that move frequently AND routine-locked. The occasional-
stratum question defers to the B6 tightness knob / longer horizons.

**Volatility-predictability collinearity (direct):** all 45 objects:
Pearson r=-0.786 (p=1.65e-10), Spearman rho=-0.905 (p=1.45e-17);
non-static only (32 objects): Pearson r=-0.676 (p=2.16e-05),
Spearman rho=-0.741 (p=1.22e-06).

## B2. room_now answerer comparison

Paired sweep on identical predictions (all tiers, displaced room_now; aggregate_mass =
current default; argmax_room = room of argmax receptacle, mass fallback when that room
is not among options). n_obj=24 displaced-carrying targets, n_probe=9617:

| tier | aggregate_mass (displaced) | argmax_room (displaced) |
|---|---|---|
| b0_lastseen | 0.099 [0.009,0.260] | 0.099 [0.009,0.260] |
| b1_longmem | 0.138 [0.029,0.298] | 0.137 [0.029,0.298] |
| b2_classdecay | 0.098 [0.008,0.260] | 0.098 [0.008,0.260] |
| b3(fremen) | 0.283 [0.107,0.464] | 0.277 [0.100,0.462] |
| b3(schedule_prior) | 0.297 [0.119,0.470] | 0.283 [0.104,0.464] |

**Outcome: NULL — `aggregate_mass` stays the default** (argmax_room is never better;
for b3 it is slightly worse). The moved-room result is NOT rescued: b3's 0.297 remains
point-above but not CI-separated from chance (0.25).

**Why room < location does not violate the coarsening inequality:** the inequality
holds for full-vocabulary argmax answering, but these are 4-option MCQs and the option
sets are built from the object's own history. Measured on 112 displaced probe
questions: the stale (last-seen) receptacle appears among the location_now options
42/112 = 0.38 of the time, while the stale ROOM
appears among the room_now options 111/112 = 0.99
of the time. A confidently-stale belief therefore has an escape hatch on location_now
(its mass sits on a receptacle that often is not offered, so relative mass among the
offered options can still find the truth) but almost never on room_now (the stale room
is nearly always offered and captures the argmax/mass). Room questions are structurally
harder in MCQ form; sub-chance tiers are confident-stale, not answerer-biased.

## B3. Hygiene: missing counts and reconciliations

**Per-stratum displaced counts (location_now):** dynamic n_probe=6501 over n_obj=11;
occasional n_probe=2984 over n_obj=12; static n_probe=132 over n_obj=**1** — every
static-stratum displaced cell (incl. b2's 0.455 and the -0.356 "lead") is a
single-object anecdote and is now flagged as such.

**Target selection (36 of 45):** per-stratum cap of 12 with test-day movers prioritized
(seeded rng, seed=7). The 9 excluded objects, none of which move on a test day:
- stool_3 (obj 41, static, moves_on_test=False)
- chair_3 (obj 11, static, moves_on_test=False)
- stool_2 (obj 40, static, moves_on_test=False)
- fridge_1 (obj 18, static, moves_on_test=False)
- potted_plant_4 (obj 35, static, moves_on_test=False)
- potted_plant_6 (obj 37, static, moves_on_test=False)
- book_3 (obj 2, occasional, moves_on_test=False)
- potted_plant_2 (obj 33, occasional, moves_on_test=False)
- leo_headphones (obj 20, dynamic, moves_on_test=True)

**Predictability median reconciliation:** 0.682 (report header) = median over the 27
NON-STATIC objects of the whole scene; 0.705 (half-split) = median over all 36 probe
TARGETS including 12 static ones. Two different populations, both correct; stage1c
labels every median with its population.
