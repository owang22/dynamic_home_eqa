# HOMER+ data inventory (Phase 0)

Dataset: HOMER+ (Patel, Prakash & Chernova, CoRL 2023), cloned from
`Maithili/HOMER_PLUS` @ HEAD into `third_party/` (gitignored, 4.3 GB).
3 households, 65 train + 10 test days each; per day ~200 full-state
VirtualHome graph snapshots at action timestamps (minutes from
midnight, simulator day 06:00-24:00, native dt=10 min).

| household | objects | receptacles | train rows | test rows | moves/day | ever-move frac |
|---|---|---|---|---|---|---|
| A | 50 | 26 | 8198 | 1225 | 75.6 | 0.92 |
| B | 49 | 29 | 7405 | 1133 | 64.8 | 0.94 |
| C | 39 | 25 | 6720 | 1034 | 64.4 | 0.95 |

Rows are CHANGE-POINTS of the canonical trace (day-initial state +
every receptacle change), not raw snapshots; see the loader docstring
for the state-vs-transition decision and the receptacle-resolution
rule (most-specific parent; the room only as a last resort).

## Per-object movement frequency (train moves per object)

**HouseholdA** — 4 objects never move; mover quartiles max=578, p75=148, median=70, p25=62. Top movers: plate (578), spoon (500), remote_control (354), bowl (304), cookingpot (278), fryingpan (278), instrument_guitar (234), knife (225)

**HouseholdB** — 3 objects never move; mover quartiles max=457, p75=150, median=70, p25=44. Top movers: spoon (457), plate (286), cookingpot (286), fryingpan (286), remote_control (240), bowl (221), book (220), tooth_paste (209)

**HouseholdC** — 2 objects never move; mover quartiles max=338, p75=150, median=90, p25=70. Top movers: instrument_guitar (338), book (290), plate (290), cookingpot (290), fryingpan (290), spoon (290), remote_control (264), notebook (190)

## Held-out draws (E2)

k=2, 5 draws per household, seed 0, drawn from objects averaging >= 1 move per 5 train days. Masks in `data/homer_traces/heldout_masks.json`.

## Dataset surprises worth knowing

1. **Object naming leaks household identity** (relevant to the separate leak audit; not fixed here): each household has unique class_names — A only: cd_player, food_jam, food_peanut_butter, knife; B only: clothes_jacket, dresser, groceries, mail; C only: drinking_glass, food_apple, painkillers. 53 class_names are shared.
2. **Snapshots carry redundant location edges** (room AND furniture); resolving parents by edge order silently collapses every object to its room. The loader resolves by specificity and pins receptacle counts in a regression test.
3. **No weekday structure**: FreMEn's recovered spectra put ~all amplitude on the 24 h family (12 h second); the 7-day components are &le; 0.004 mean amplitude in every household (`reports/homer_spectra/`). Time-of-day is the only usable periodicity.
4. **HOMER-Noise**: not present in the HOMER_PLUS repository; the original HOMER generator lives in GT-RAIL/rail_tasksim (homer branch). Neither acquired in this pilot; the loader carries the household directory name through as-is so variants can join later.
