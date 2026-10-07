# Study 2, second count: baseline 2 (persistent new place) and a word match on the nightly notes

Computed by `persistent_move.py` beside this file. Baseline 2 reads the last-seen (no model) cells, the same sighting streams as RESULTS_baseline.md. The word match reads the log-and-notes cells. Definitions are in the script's docstring; the ones that needed a decision are repeated here.

- New sighting: object o in room r on day d, and none of o's earlier sightings with day >= d-7 is in r. An object with no earlier sighting at all in that window is skipped (not new).
- Moved: a new sighting followed, as the object's very next sighting, by another in the same room; the move day is the day of the confirming sighting. V2 also requires the confirming sighting on a later day.
- W[d] = distinct objects with a move day in d-2..d. Alarm day when W[d] >= k. k = 1 + the largest W on days 1-13 among the other households (zero alarm days on their days 1-13).
- Delay: first alarm day in 14..23 minus 14 (0 = day 14). False alarms: alarm days 1-13, raw and x30/13. Return alarms: alarm days 24-31, separate. The 50-day run also scores 32..41 and 42..49.

## Baseline 2, ten households, 31 days, 8 questions a day

Cells under `results/self_improve/overnight_wave/cells/last_seen_no_model`. Present: 10 of 10. None missing.

### Per-household scores, leave-one-out k


**V1: confirming sighting any time later**

| household | k (alarm when distinct movers in 3 days >= k) | own max W days 1-13 | delay from day 14 | false alarm days 1-13 (raw) | false alarms per month (x30/13) | alarm days 24-31 (return) | all alarm days |
|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 9 | 7 | none | 0 | 0.00 | 0 | - |
| hh_s19_t03 | 9 | 2 | none | 0 | 0.00 | 0 | - |
| hh_s20_t03 | 9 | 3 | none | 0 | 0.00 | 1 | 26 |
| hh_s32_t03 | 9 | 3 | none | 0 | 0.00 | 0 | - |
| hh_s48_t03 | 9 | 8 | 1 | 0 | 0.00 | 0 | 15 |
| hh_s63_t03 | 9 | 3 | none | 0 | 0.00 | 0 | - |
| hh_s93_t03 | 9 | 3 | none | 0 | 0.00 | 0 | - |
| hh_s109_t03 | 9 | 5 | none | 0 | 0.00 | 0 | - |
| hh_s123_t03 | 9 | 1 | none | 0 | 0.00 | 0 | - |
| hh_s151_t03 | 9 | 8 | none | 0 | 0.00 | 0 | - |

Delay from day 14: mean 1.00, sd 0.00 over n = 1 detected; 9 of 10 with no alarm on days 14-23.
False alarms per month: mean 0.00; households with any false alarm day: 0 of 10.
Households with at least one return alarm: 1 of 10.

**V2: confirming sighting on a later day**

| household | k (alarm when distinct movers in 3 days >= k) | own max W days 1-13 | delay from day 14 | false alarm days 1-13 (raw) | false alarms per month (x30/13) | alarm days 24-31 (return) | all alarm days |
|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 6 | 6 | none | 1 | 2.31 | 0 | 4 |
| hh_s19_t03 | 7 | 0 | none | 0 | 0.00 | 0 | - |
| hh_s20_t03 | 7 | 1 | none | 0 | 0.00 | 0 | - |
| hh_s32_t03 | 7 | 2 | none | 0 | 0.00 | 0 | - |
| hh_s48_t03 | 7 | 5 | none | 0 | 0.00 | 0 | - |
| hh_s63_t03 | 7 | 3 | none | 0 | 0.00 | 0 | - |
| hh_s93_t03 | 7 | 0 | none | 0 | 0.00 | 0 | - |
| hh_s109_t03 | 7 | 0 | none | 0 | 0.00 | 0 | - |
| hh_s123_t03 | 7 | 0 | none | 0 | 0.00 | 0 | - |
| hh_s151_t03 | 7 | 3 | none | 0 | 0.00 | 0 | - |

Delay from day 14: mean n/a, sd n/a over n = 0 detected; 10 of 10 with no alarm on days 14-23.
False alarms per month: mean 0.23; households with any false alarm day: 1 of 10.
Households with at least one return alarm: 0 of 10.

#### Contrast, not the Addendum's rule: k chosen on days 8-13 only

On days 1-7 the seven-day window is still filling, so an object's first visit to each of its ordinary rooms counts as a new place and its second sighting there as a move; most of the settled peaks above fall on days 1-6. This table chooses k on the pool's days 8-13 (zero alarm days there) and reports false alarms on days 8-13 (per month = x30/6), with the alarm days on 1-13 listed in full so the warm-up alarms are visible.

**V1: confirming sighting any time later**

| household | k (alarm when distinct movers in 3 days >= k) | own max W days 8-13 | delay from day 14 | false alarm days 8-13 (raw) | false alarms per month (x30/6) | alarm days 1-13 (all, incl. the warm-up week) | alarm days 24-31 (return) | all alarm days |
|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 5 | 1 | none | 0 | 0.00 | 3, 4, 5 | 1 | 3, 4, 5, 26 |
| hh_s19_t03 | 5 | 0 | none | 0 | 0.00 | - | 0 | - |
| hh_s20_t03 | 5 | 1 | 1 | 0 | 0.00 | - | 3 | 15, 16, 17, 24, 25, 26 |
| hh_s32_t03 | 5 | 3 | none | 0 | 0.00 | - | 0 | - |
| hh_s48_t03 | 4 | 4 | 0 | 1 | 5.00 | 2, 3, 4, 13 | 4 | 2, 3, 4, 13, 14, 15, 16, 17, 25, 26, 27, 28 |
| hh_s63_t03 | 5 | 1 | none | 0 | 0.00 | - | 2 | 26, 27 |
| hh_s93_t03 | 5 | 0 | 1 | 0 | 0.00 | - | 2 | 15, 16, 17, 25, 26 |
| hh_s109_t03 | 5 | 0 | none | 0 | 0.00 | 2, 3 | 0 | 2, 3 |
| hh_s123_t03 | 5 | 1 | 4 | 0 | 0.00 | - | 0 | 18, 19 |
| hh_s151_t03 | 5 | 1 | none | 0 | 0.00 | 4, 5, 6 | 3 | 4, 5, 6, 25, 26, 27 |

Delay from day 14: mean 1.50, sd 1.73 over n = 4 detected; 6 of 10 with no alarm on days 14-23.
False alarms per month: mean 0.50; households with any false alarm day: 1 of 10.
Households with at least one return alarm: 6 of 10.

**V2: confirming sighting on a later day**

| household | k (alarm when distinct movers in 3 days >= k) | own max W days 8-13 | delay from day 14 | false alarm days 8-13 (raw) | false alarms per month (x30/6) | alarm days 1-13 (all, incl. the warm-up week) | alarm days 24-31 (return) | all alarm days |
|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 4 | 1 | none | 0 | 0.00 | 3, 4, 5 | 0 | 3, 4, 5 |
| hh_s19_t03 | 4 | 0 | none | 0 | 0.00 | - | 0 | - |
| hh_s20_t03 | 4 | 0 | 1 | 0 | 0.00 | - | 0 | 15, 16, 17 |
| hh_s32_t03 | 4 | 2 | none | 0 | 0.00 | - | 0 | - |
| hh_s48_t03 | 3 | 3 | 1 | 1 | 5.00 | 2, 3, 4, 13 | 3 | 2, 3, 4, 13, 15, 16, 17, 26, 27, 28 |
| hh_s63_t03 | 4 | 1 | none | 0 | 0.00 | - | 2 | 26, 27 |
| hh_s93_t03 | 4 | 0 | none | 0 | 0.00 | - | 0 | - |
| hh_s109_t03 | 4 | 0 | none | 0 | 0.00 | - | 0 | - |
| hh_s123_t03 | 4 | 0 | 4 | 0 | 0.00 | - | 0 | 18, 19 |
| hh_s151_t03 | 4 | 1 | none | 0 | 0.00 | - | 0 | - |

Delay from day 14: mean 2.00, sd 1.73 over n = 3 detected; 7 of 10 with no alarm on days 14-23.
False alarms per month: mean 0.50; households with any false alarm day: 1 of 10.
Households with at least one return alarm: 2 of 10.

### Day by day, days 10-18

Objects whose move day is that day, and the 3-day distinct count W. The change is on day 14.



| household | row | d10 | d11 | d12 | d13 | d14 | d15 | d16 | d17 | d18 |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | moved that day (any) | 0 | 0 | 0 | 1 | 2 | 1 | 1 | 0 | 0 |
| hh_s2_t03 | 3-day distinct W (any) | 0 | 0 | 0 | 1 | 3 | 4 | 4 | 2 | 1 |
| hh_s2_t03 | moved that day (later_day) | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 |
| hh_s2_t03 | 3-day distinct W (later_day) | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 |
| hh_s19_t03 | moved that day (any) | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 |
| hh_s19_t03 | 3-day distinct W (any) | 0 | 0 | 0 | 0 | 0 | 2 | 4 | 4 | 2 |
| hh_s19_t03 | moved that day (later_day) | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| hh_s19_t03 | 3-day distinct W (later_day) | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 2 | 0 |
| hh_s20_t03 | moved that day (any) | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 |
| hh_s20_t03 | 3-day distinct W (any) | 1 | 1 | 0 | 0 | 0 | 6 | 6 | 6 | 0 |
| hh_s20_t03 | moved that day (later_day) | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| hh_s20_t03 | 3-day distinct W (later_day) | 0 | 0 | 0 | 0 | 0 | 4 | 4 | 4 | 0 |
| hh_s32_t03 | moved that day (any) | 1 | 1 | 1 | 0 | 0 | 2 | 0 | 0 | 0 |
| hh_s32_t03 | 3-day distinct W (any) | 2 | 3 | 3 | 2 | 1 | 2 | 2 | 2 | 0 |
| hh_s32_t03 | moved that day (later_day) | 0 | 1 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| hh_s32_t03 | 3-day distinct W (later_day) | 1 | 2 | 1 | 1 | 0 | 2 | 2 | 2 | 0 |
| hh_s48_t03 | moved that day (any) | 0 | 1 | 1 | 2 | 4 | 3 | 1 | 1 | 0 |
| hh_s48_t03 | 3-day distinct W (any) | 0 | 1 | 2 | 4 | 6 | 9 | 8 | 5 | 2 |
| hh_s48_t03 | moved that day (later_day) | 0 | 1 | 1 | 1 | 0 | 3 | 0 | 1 | 0 |
| hh_s48_t03 | 3-day distinct W (later_day) | 0 | 1 | 2 | 3 | 2 | 4 | 3 | 4 | 1 |
| hh_s63_t03 | moved that day (any) | 0 | 0 | 0 | 1 | 0 | 2 | 1 | 0 | 2 |
| hh_s63_t03 | 3-day distinct W (any) | 0 | 0 | 0 | 1 | 1 | 3 | 3 | 3 | 2 |
| hh_s63_t03 | moved that day (later_day) | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 2 |
| hh_s63_t03 | 3-day distinct W (later_day) | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 2 |
| hh_s93_t03 | moved that day (any) | 0 | 0 | 0 | 0 | 3 | 5 | 0 | 1 | 1 |
| hh_s93_t03 | 3-day distinct W (any) | 0 | 0 | 0 | 0 | 3 | 8 | 8 | 6 | 2 |
| hh_s93_t03 | moved that day (later_day) | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 |
| hh_s93_t03 | 3-day distinct W (later_day) | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 2 | 2 |
| hh_s109_t03 | moved that day (any) | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| hh_s109_t03 | 3-day distinct W (any) | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 2 |
| hh_s109_t03 | moved that day (later_day) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hh_s109_t03 | 3-day distinct W (later_day) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hh_s123_t03 | moved that day (any) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 2 |
| hh_s123_t03 | 3-day distinct W (any) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 5 |
| hh_s123_t03 | moved that day (later_day) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 2 |
| hh_s123_t03 | 3-day distinct W (later_day) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 5 |
| hh_s151_t03 | moved that day (any) | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 |
| hh_s151_t03 | 3-day distinct W (any) | 0 | 0 | 0 | 0 | 0 | 2 | 3 | 3 | 1 |
| hh_s151_t03 | moved that day (later_day) | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 |
| hh_s151_t03 | 3-day distinct W (later_day) | 0 | 0 | 0 | 0 | 0 | 2 | 3 | 3 | 1 |

### How high W runs in each window


V1: confirming sighting any time later:

| household | move events (whole run) | max W d1-7 (on day) | max W d8-13 (on day) | max W d1-13 (on day) | max W d14-23 (on day) | max W d24-31 (on day) |
|---|---|---|---|---|---|---|
| hh_s2_t03 | 23 | 7 (d4) | 1 (d13) | 7 (d4) | 4 (d15) | 5 (d26) |
| hh_s19_t03 | 8 | 2 (d1) | 0 (d8) | 2 (d1) | 4 (d16) | 2 (d25) |
| hh_s20_t03 | 26 | 3 (d1) | 1 (d9) | 3 (d1) | 6 (d15) | 10 (d26) |
| hh_s32_t03 | 16 | 1 (d7) | 3 (d11) | 3 (d11) | 3 (d20) | 4 (d26) |
| hh_s48_t03 | 34 | 8 (d4) | 4 (d13) | 8 (d4) | 9 (d15) | 8 (d26) |
| hh_s63_t03 | 17 | 3 (d5) | 1 (d13) | 3 (d5) | 3 (d15) | 5 (d26) |
| hh_s93_t03 | 20 | 3 (d2) | 0 (d8) | 3 (d2) | 8 (d15) | 6 (d25) |
| hh_s109_t03 | 12 | 5 (d2) | 0 (d8) | 5 (d2) | 4 (d20) | 1 (d28) |
| hh_s123_t03 | 11 | 1 (d1) | 1 (d8) | 1 (d1) | 5 (d18) | 3 (d25) |
| hh_s151_t03 | 21 | 8 (d6) | 1 (d8) | 8 (d6) | 3 (d16) | 5 (d25) |

V2: confirming sighting on a later day:

| household | move events (whole run) | max W d1-7 (on day) | max W d8-13 (on day) | max W d1-13 (on day) | max W d14-23 (on day) | max W d24-31 (on day) |
|---|---|---|---|---|---|---|
| hh_s2_t03 | 12 | 6 (d4) | 1 (d13) | 6 (d4) | 2 (d20) | 1 (d26) |
| hh_s19_t03 | 4 | 0 (d1) | 0 (d8) | 0 (d1) | 2 (d15) | 2 (d25) |
| hh_s20_t03 | 10 | 1 (d5) | 0 (d8) | 1 (d5) | 4 (d15) | 2 (d26) |
| hh_s32_t03 | 8 | 1 (d7) | 2 (d9) | 2 (d9) | 2 (d15) | 3 (d28) |
| hh_s48_t03 | 18 | 5 (d2) | 3 (d13) | 5 (d2) | 4 (d15) | 4 (d26) |
| hh_s63_t03 | 12 | 3 (d5) | 1 (d13) | 3 (d5) | 3 (d19) | 4 (d26) |
| hh_s93_t03 | 6 | 0 (d1) | 0 (d8) | 0 (d1) | 2 (d17) | 3 (d25) |
| hh_s109_t03 | 4 | 0 (d1) | 0 (d8) | 0 (d1) | 3 (d20) | 1 (d28) |
| hh_s123_t03 | 9 | 0 (d1) | 0 (d8) | 0 (d1) | 5 (d18) | 3 (d25) |
| hh_s151_t03 | 9 | 3 (d6) | 1 (d8) | 3 (d6) | 3 (d16) | 3 (d25) |

### What the rule reacts to: objects that moved on days 14-16 and in the three loudest settled windows

V1 (confirming sighting any time later). Each entry is object: room of the previous sighting -> new room (move day; the day it was first seen in the new room if earlier). '[true mover]' marks objects in the cell's ground-truth movers list; the tag is for the reader and is not used by the rule. The settled days listed are the three days 1-13 with the largest W, and the entries are all moves in that day's 3-day window.

**hh_s2_t03** (movers by ground truth, for the reader only: book_tomas, charger_tomas, glass_ines, glass_tomas, mug_ines, mug_tomas, notebook_tomas, water_bottle_tomas)

- day 14 (W=3): glass_tomas [true mover]: kitchen -> bedroom_1 (d14); water_bottle_tomas [true mover]: kitchen -> bedroom_1 (d14)
- day 15 (W=4): vitamins_tomas: kitchen -> bedroom_1 (d15)
- day 16 (W=4): bowl_ines: kitchen -> dining (d16, first seen there d15)
- settled day 4 (W=7, window days 2-4): glass_tomas [true mover]: dining -> kitchen (d2, first seen there d1); plate_tomas: dining -> kitchen (d2, first seen there d1); bowl_tomas: dining -> kitchen (d3, first seen there d2); mug_ines [true mover]: dining -> kitchen (d3, first seen there d1); snack_bowl_shared: living -> kitchen (d3, first seen there d2); bowl_ines: kitchen -> dining (d4); plate_ines: kitchen -> dining (d4, first seen there d3)
- settled day 3 (W=6, window days 1-3): charger_tomas [true mover]: office -> bedroom_1 (d1); glass_tomas [true mover]: dining -> kitchen (d2, first seen there d1); plate_tomas: dining -> kitchen (d2, first seen there d1); bowl_tomas: dining -> kitchen (d3, first seen there d2); mug_ines [true mover]: dining -> kitchen (d3, first seen there d1); snack_bowl_shared: living -> kitchen (d3, first seen there d2)
- settled day 5 (W=5, window days 3-5): bowl_tomas: dining -> kitchen (d3, first seen there d2); mug_ines [true mover]: dining -> kitchen (d3, first seen there d1); snack_bowl_shared: living -> kitchen (d3, first seen there d2); bowl_ines: kitchen -> dining (d4); plate_ines: kitchen -> dining (d4, first seen there d3)

**hh_s19_t03** (movers by ground truth, for the reader only: book_marco, charger_marco, glass_marco, mug_marco, mug_omar, notebook_marco, water_bottle_marco)

- day 14 (W=0): no object moved
- day 15 (W=2): glass_marco [true mover]: kitchen -> bedroom_1 (d15, first seen there d14); water_bottle_marco [true mover]: kitchen -> bedroom_1 (d15, first seen there d14)
- day 16 (W=4): blanket_shared: bedroom_1 -> living (d16); mug_marco [true mover]: kitchen -> living (d16)
- settled day 1 (W=2, window days 1-1): mug_omar [true mover]: kitchen -> office (d1); water_bottle_omar: kitchen -> office (d1)
- settled day 2 (W=2, window days 1-2): mug_omar [true mover]: kitchen -> office (d1); water_bottle_omar: kitchen -> office (d1)
- settled day 3 (W=2, window days 1-3): mug_omar [true mover]: kitchen -> office (d1); water_bottle_omar: kitchen -> office (d1)

**hh_s20_t03** (movers by ground truth, for the reader only: book_hana, charger_hana, glass_hana, glasses_hana, medication_hana, mug_hana, towel_aisha, water_bottle_aisha, water_bottle_hana)

- day 14 (W=0): no object moved
- day 15 (W=6): charger_hana [true mover]: office -> bedroom_1 (d15, first seen there d14); glass_hana [true mover]: kitchen -> bedroom_1 (d15); headphones_hana: office -> bedroom_1 (d15, first seen there d14); medication_hana [true mover]: bedroom_1 -> kitchen (d15); tablet_aisha: dining -> bedroom_1 (d15, first seen there d14); water_bottle_hana [true mover]: office -> bedroom_1 (d15, first seen there d14)
- day 16 (W=6): no object moved
- settled day 1 (W=3, window days 1-1): bowl_aisha: dining -> kitchen (d1); mug_aisha: dining -> kitchen (d1); tablet_aisha: dining -> living (d1)
- settled day 2 (W=3, window days 1-2): bowl_aisha: dining -> kitchen (d1); mug_aisha: dining -> kitchen (d1); tablet_aisha: dining -> living (d1)
- settled day 3 (W=3, window days 1-3): bowl_aisha: dining -> kitchen (d1); mug_aisha: dining -> kitchen (d1); tablet_aisha: dining -> living (d1)

**hh_s32_t03** (movers by ground truth, for the reader only: book_leo, charger_leo, glass_leo, mug_leo, tablet_leo, towel_aisha, water_bottle_aisha, water_bottle_leo)

- day 14 (W=1): no object moved
- day 15 (W=2): speaker_shared: kitchen -> living (d15, first seen there d14); tablet_leo [true mover]: kitchen -> living (d15, first seen there d14)
- day 16 (W=2): no object moved
- settled day 11 (W=3, window days 9-11): tablet_aisha: kitchen -> bedroom_3 (d9, first seen there d2); phone_elena: bedroom_2 -> kitchen (d10); notebook_elena: bedroom_2 -> kitchen (d11, first seen there d7)
- settled day 12 (W=3, window days 10-12): phone_elena: bedroom_2 -> kitchen (d10); notebook_elena: bedroom_2 -> kitchen (d11, first seen there d7); tablet_aisha: bedroom_3 -> kitchen (d12)
- settled day 9 (W=2, window days 7-9): phone_elena: kitchen -> bedroom_2 (d7, first seen there d2); tablet_aisha: kitchen -> bedroom_3 (d9, first seen there d2)

**hh_s48_t03** (movers by ground truth, for the reader only: book_marco, charger_marco, glass_marco, mug_marco, water_bottle_marco, water_bottle_priya)

- day 14 (W=6): glass_marco [true mover]: kitchen -> bedroom_1 (d14); hair_dryer_priya: bedroom_2 -> bathroom (d14); skincare_marco: bathroom -> bedroom_1 (d14); toiletry_bag_marco: bathroom -> bedroom_1 (d14)
- day 15 (W=9): charger_marco [true mover]: entry -> bedroom_1 (d15, first seen there d14); jacket_marco: bedroom_1 -> entry (d15, first seen there d14); water_bottle_marco [true mover]: kitchen -> bedroom_1 (d15, first seen there d14)
- day 16 (W=8): blanket_shared: living -> bedroom_1 (d16)
- settled day 4 (W=8, window days 2-4): glass_priya: kitchen -> dining (d2, first seen there d1); plate_marco: kitchen -> dining (d2); plate_priya: kitchen -> dining (d2, first seen there d1); serving_dish_shared: kitchen -> dining (d2, first seen there d1); water_bottle_marco [true mover]: kitchen -> entry (d2, first seen there d1); water_bottle_priya [true mover]: kitchen -> dining (d2, first seen there d1); water_bottle_marco [true mover]: entry -> dining (d3, first seen there d2); hair_dryer_priya: bedroom_2 -> bathroom (d4); mug_priya: kitchen -> dining (d4)
- settled day 2 (W=7, window days 1-2): glass_marco [true mover]: kitchen -> dining (d1); glass_priya: kitchen -> dining (d2, first seen there d1); plate_marco: kitchen -> dining (d2); plate_priya: kitchen -> dining (d2, first seen there d1); serving_dish_shared: kitchen -> dining (d2, first seen there d1); water_bottle_marco [true mover]: kitchen -> entry (d2, first seen there d1); water_bottle_priya [true mover]: kitchen -> dining (d2, first seen there d1)
- settled day 3 (W=7, window days 1-3): glass_marco [true mover]: kitchen -> dining (d1); glass_priya: kitchen -> dining (d2, first seen there d1); plate_marco: kitchen -> dining (d2); plate_priya: kitchen -> dining (d2, first seen there d1); serving_dish_shared: kitchen -> dining (d2, first seen there d1); water_bottle_marco [true mover]: kitchen -> entry (d2, first seen there d1); water_bottle_priya [true mover]: kitchen -> dining (d2, first seen there d1); water_bottle_marco [true mover]: entry -> dining (d3, first seen there d2)

**hh_s63_t03** (movers by ground truth, for the reader only: book_dana, book_priya, charger_dana, glass_dana, glass_priya, mug_dana, mug_priya, tablet_priya, water_bottle_dana)

- day 14 (W=1): no object moved
- day 15 (W=3): book_dana [true mover]: dining -> living (d15); mug_dana [true mover]: dining -> living (d15)
- day 16 (W=3): tablet_priya [true mover]: dining -> living (d16)
- settled day 5 (W=3, window days 3-5): notebook_priya: bedroom_1 -> dining (d4, first seen there d3); book_dana [true mover]: bedroom_1 -> dining (d5, first seen there d4); mug_dana [true mover]: office -> dining (d5, first seen there d4)
- settled day 6 (W=3, window days 4-6): notebook_priya: bedroom_1 -> dining (d4, first seen there d3); book_dana [true mover]: bedroom_1 -> dining (d5, first seen there d4); mug_dana [true mover]: office -> dining (d5, first seen there d4)
- settled day 7 (W=2, window days 5-7): book_dana [true mover]: bedroom_1 -> dining (d5, first seen there d4); mug_dana [true mover]: office -> dining (d5, first seen there d4)

**hh_s93_t03** (movers by ground truth, for the reader only: book_ines, charger_ines, glass_ines, glasses_ines, medication_ines, mug_ines, mug_kwame, razor_kwame, water_bottle_ines)

- day 14 (W=3): medication_ines [true mover]: bathroom -> bedroom_1 (d14); vitamins_ines: kitchen -> bedroom_1 (d14); water_bottle_ines [true mover]: office -> bedroom_1 (d14)
- day 15 (W=8): blanket_shared: bedroom_1 -> living (d15); book_ines [true mover]: bedroom_1 -> living (d15); charger_ines [true mover]: office -> bedroom_1 (d15, first seen there d14); glasses_ines [true mover]: office -> living (d15); mug_ines [true mover]: office -> living (d15)
- day 16 (W=8): no object moved
- settled day 2 (W=3, window days 1-2): headset_ines: living -> office (d2); mug_ines [true mover]: kitchen -> office (d2); water_bottle_ines [true mover]: kitchen -> office (d2)
- settled day 3 (W=3, window days 1-3): headset_ines: living -> office (d2); mug_ines [true mover]: kitchen -> office (d2); water_bottle_ines [true mover]: kitchen -> office (d2)
- settled day 4 (W=3, window days 2-4): headset_ines: living -> office (d2); mug_ines [true mover]: kitchen -> office (d2); water_bottle_ines [true mover]: kitchen -> office (d2)

**hh_s109_t03** (movers by ground truth, for the reader only: book_yuki, charger_yuki, glass_yuki, mug_yuki, water_bottle_felix, water_bottle_yuki)

- day 14 (W=0): no object moved
- day 15 (W=0): no object moved
- day 16 (W=1): bowl_felix: kitchen -> dining (d16)
- settled day 2 (W=5, window days 1-2): charger_felix: office -> bedroom_2 (d1); glasses_felix: office -> bedroom_2 (d1); headphones_felix: office -> bedroom_2 (d1); water_bottle_felix [true mover]: kitchen -> office (d1); glass_yuki [true mover]: kitchen -> dining (d2); water_bottle_felix [true mover]: office -> dining (d2)
- settled day 3 (W=5, window days 1-3): charger_felix: office -> bedroom_2 (d1); glasses_felix: office -> bedroom_2 (d1); headphones_felix: office -> bedroom_2 (d1); water_bottle_felix [true mover]: kitchen -> office (d1); glass_yuki [true mover]: kitchen -> dining (d2); water_bottle_felix [true mover]: office -> dining (d2)
- settled day 1 (W=4, window days 1-1): charger_felix: office -> bedroom_2 (d1); glasses_felix: office -> bedroom_2 (d1); headphones_felix: office -> bedroom_2 (d1); water_bottle_felix [true mover]: kitchen -> office (d1)

**hh_s123_t03** (movers by ground truth, for the reader only: charger_priya, glass_priya, mug_priya, notebook_priya, water_bottle_priya)

- day 14 (W=0): no object moved
- day 15 (W=0): no object moved
- day 16 (W=0): no object moved
- settled day 1 (W=1, window days 1-1): mug_sam: office -> kitchen (d1)
- settled day 2 (W=1, window days 1-2): mug_sam: office -> kitchen (d1)
- settled day 3 (W=1, window days 1-3): mug_sam: office -> kitchen (d1)

**hh_s151_t03** (movers by ground truth, for the reader only: book_dana, charger_dana, glass_dana, glasses_felix, medication_dana, mug_dana, towel_dana, water_bottle_dana)

- day 14 (W=0): no object moved
- day 15 (W=2): medication_dana [true mover]: bathroom -> bedroom_1 (d15, first seen there d14); water_bottle_dana [true mover]: dining -> bedroom_1 (d15, first seen there d14)
- day 16 (W=3): glass_dana [true mover]: kitchen -> bedroom_1 (d16, first seen there d15)
- settled day 6 (W=8, window days 4-6): blanket_shared: living -> bedroom_1 (d4); charger_dana [true mover]: entry -> bedroom_1 (d4); headphones_dana: entry -> bedroom_1 (d4); pen_dana: entry -> bedroom_1 (d4); lunchbox_dana: entry -> kitchen (d5, first seen there d4); lunchbox_felix: entry -> kitchen (d5, first seen there d4); water_bottle_dana [true mover]: dining -> kitchen (d5); headphones_felix: entry -> office (d6, first seen there d5)
- settled day 5 (W=7, window days 3-5): blanket_shared: living -> bedroom_1 (d4); charger_dana [true mover]: entry -> bedroom_1 (d4); headphones_dana: entry -> bedroom_1 (d4); pen_dana: entry -> bedroom_1 (d4); lunchbox_dana: entry -> kitchen (d5, first seen there d4); lunchbox_felix: entry -> kitchen (d5, first seen there d4); water_bottle_dana [true mover]: dining -> kitchen (d5)
- settled day 4 (W=5, window days 2-4): mug_felix: dining -> kitchen (d2); blanket_shared: living -> bedroom_1 (d4); charger_dana [true mover]: entry -> bedroom_1 (d4); headphones_dana: entry -> bedroom_1 (d4); pen_dana: entry -> bedroom_1 (d4)

## Baseline 2, three households, 50 days, 24 questions a day

Cells under `results/self_improve/wave_the_second_illness/cells/last_seen_no_model`. Present: 3 of 3. None missing. k is chosen on the other two households of this run, as in RESULTS_baseline.md.

### Per-household scores, leave-one-out k (pool = the other two)


**V1: confirming sighting any time later**

| household | k (alarm when distinct movers in 3 days >= k) | own max W days 1-13 | delay from day 14 | delay from day 32 | false alarm days 1-13 (raw) | false alarms per month (x30/13) | alarm days 24-31 (return) | alarm days 42-49 (return) | all alarm days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 13 | 5 | none | none | 0 | 0.00 | 0 | 0 | - |
| hh_s32_t03 | 13 | 8 | none | none | 0 | 0.00 | 0 | 0 | - |
| hh_s48_t03 | 9 | 12 | 0 | none | 3 | 6.92 | 3 | 0 | 2, 3, 4, 14, 15, 16, 28, 29, 30 |

Delay from day 14: mean 0.00, sd 0.00 over n = 1 detected; 2 of 3 with no alarm on days 14-23.

Delay from day 32: mean n/a, sd n/a over n = 0 detected; 3 of 3 with no alarm on days 32-41.
False alarms per month: mean 2.31; households with any false alarm day: 1 of 3.
Households with at least one return alarm: 1 of 3.

**V2: confirming sighting on a later day**

| household | k (alarm when distinct movers in 3 days >= k) | own max W days 1-13 | delay from day 14 | delay from day 32 | false alarm days 1-13 (raw) | false alarms per month (x30/13) | alarm days 24-31 (return) | alarm days 42-49 (return) | all alarm days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 7 | 1 | none | none | 0 | 0.00 | 0 | 0 | - |
| hh_s32_t03 | 7 | 2 | none | none | 0 | 0.00 | 0 | 0 | - |
| hh_s48_t03 | 3 | 6 | 0 | none | 4 | 9.23 | 0 | 1 | 2, 3, 4, 5, 14, 15, 16, 45 |

Delay from day 14: mean 0.00, sd 0.00 over n = 1 detected; 2 of 3 with no alarm on days 14-23.

Delay from day 32: mean n/a, sd n/a over n = 0 detected; 3 of 3 with no alarm on days 32-41.
False alarms per month: mean 3.08; households with any false alarm day: 1 of 3.
Households with at least one return alarm: 1 of 3.

#### Contrast, not the Addendum's rule: k chosen on days 8-13 only


**V1: confirming sighting any time later**

| household | k (alarm when distinct movers in 3 days >= k) | own max W days 8-13 | delay from day 14 | delay from day 32 | false alarm days 8-13 (raw) | false alarms per month (x30/6) | alarm days 1-13 (all, incl. the warm-up week) | alarm days 24-31 (return) | alarm days 42-49 (return) | all alarm days |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 4 | 1 | 1 | 0 | 0 | 0.00 | 4 | 3 | 2 | 4, 15, 16, 17, 24, 25, 26, 32, 33, 34, 43, 44 |
| hh_s32_t03 | 4 | 0 | 4 | 0 | 0 | 0.00 | 2, 3, 4 | 5 | 3 | 2, 3, 4, 18, 19, 20, 24, 25, 26, 27, 31, 32, 33, 34, 37, 38, 39, 42, 43, 44 |
| hh_s48_t03 | 2 | 3 | 0 | 0 | 4 | 20.00 | 1, 2, 3, 4, 5, 6, 8, 9, 10, 13 | 8 | 6 | 1, 2, 3, 4, 5, 6, 8, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47 |

Delay from day 14: mean 1.67, sd 2.08 over n = 3 detected; 0 of 3 with no alarm on days 14-23.

Delay from day 32: mean 0.00, sd 0.00 over n = 3 detected; 0 of 3 with no alarm on days 32-41.
False alarms per month: mean 6.67; households with any false alarm day: 1 of 3.
Households with at least one return alarm: 3 of 3.

**V2: confirming sighting on a later day**

| household | k (alarm when distinct movers in 3 days >= k) | own max W days 8-13 | delay from day 14 | delay from day 32 | false alarm days 8-13 (raw) | false alarms per month (x30/6) | alarm days 1-13 (all, incl. the warm-up week) | alarm days 24-31 (return) | alarm days 42-49 (return) | all alarm days |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 1 | 1 | none | none | 3 | 15.00 | 10, 11, 12 | 0 | 2 | 10, 11, 12, 48, 49 |
| hh_s32_t03 | 2 | 0 | none | none | 0 | 0.00 | 3, 4 | 3 | 2 | 3, 4, 25, 26, 27, 46, 47 |
| hh_s48_t03 | 2 | 0 | 0 | none | 0 | 0.00 | 2, 3, 4, 5 | 2 | 3 | 2, 3, 4, 5, 14, 15, 16, 20, 26, 27, 45, 46, 47 |

Delay from day 14: mean 0.00, sd 0.00 over n = 1 detected; 2 of 3 with no alarm on days 14-23.

Delay from day 32: mean n/a, sd n/a over n = 0 detected; 3 of 3 with no alarm on days 32-41.
False alarms per month: mean 5.00; households with any false alarm day: 1 of 3.
Households with at least one return alarm: 3 of 3.

### Day by day


Around the first change (day 14):

| household | row | d10 | d11 | d12 | d13 | d14 | d15 | d16 | d17 | d18 |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | moved that day (any) | 1 | 0 | 0 | 0 | 2 | 6 | 0 | 0 | 0 |
| hh_s2_t03 | 3-day distinct W (any) | 1 | 1 | 1 | 0 | 2 | 8 | 8 | 6 | 0 |
| hh_s2_t03 | moved that day (later_day) | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hh_s2_t03 | 3-day distinct W (later_day) | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| hh_s32_t03 | moved that day (any) | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 4 |
| hh_s32_t03 | 3-day distinct W (any) | 0 | 0 | 0 | 0 | 3 | 3 | 3 | 0 | 4 |
| hh_s32_t03 | moved that day (later_day) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hh_s32_t03 | 3-day distinct W (later_day) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hh_s48_t03 | moved that day (any) | 0 | 0 | 0 | 3 | 10 | 2 | 2 | 1 | 1 |
| hh_s48_t03 | 3-day distinct W (any) | 2 | 1 | 0 | 3 | 12 | 14 | 14 | 5 | 4 |
| hh_s48_t03 | moved that day (later_day) | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 1 |
| hh_s48_t03 | 3-day distinct W (later_day) | 0 | 0 | 0 | 0 | 4 | 5 | 5 | 1 | 1 |

Around the second change (day 32):

| household | row | d28 | d29 | d30 | d31 | d32 | d33 | d34 | d35 | d36 |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | moved that day (any) | 0 | 0 | 0 | 0 | 5 | 1 | 1 | 0 | 0 |
| hh_s2_t03 | 3-day distinct W (any) | 0 | 0 | 0 | 0 | 5 | 6 | 7 | 2 | 1 |
| hh_s2_t03 | moved that day (later_day) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hh_s2_t03 | 3-day distinct W (later_day) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hh_s32_t03 | moved that day (any) | 0 | 1 | 0 | 3 | 7 | 1 | 1 | 1 | 1 |
| hh_s32_t03 | 3-day distinct W (any) | 1 | 2 | 1 | 4 | 10 | 11 | 9 | 3 | 3 |
| hh_s32_t03 | moved that day (later_day) | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| hh_s32_t03 | 3-day distinct W (later_day) | 1 | 1 | 0 | 0 | 1 | 1 | 1 | 0 | 0 |
| hh_s48_t03 | moved that day (any) | 8 | 2 | 0 | 0 | 3 | 1 | 2 | 0 | 0 |
| hh_s48_t03 | 3-day distinct W (any) | 9 | 11 | 10 | 2 | 3 | 4 | 6 | 3 | 2 |
| hh_s48_t03 | moved that day (later_day) | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hh_s48_t03 | 3-day distinct W (later_day) | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |

### How high W runs in each window


V1: confirming sighting any time later:

| household | move events (whole run) | max W d1-7 (on day) | max W d8-13 (on day) | max W d1-13 (on day) | max W d14-23 (on day) | max W d24-31 (on day) | max W d32-41 (on day) | max W d42-49 (on day) |
|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 33 | 5 (d4) | 1 (d10) | 5 (d4) | 8 (d15) | 6 (d25) | 7 (d34) | 4 (d43) |
| hh_s32_t03 | 56 | 8 (d3) | 0 (d8) | 8 (d3) | 6 (d20) | 6 (d25) | 11 (d33) | 5 (d42) |
| hh_s48_t03 | 76 | 12 (d3) | 3 (d9) | 12 (d3) | 14 (d15) | 11 (d29) | 6 (d34) | 8 (d43) |

V2: confirming sighting on a later day:

| household | move events (whole run) | max W d1-7 (on day) | max W d8-13 (on day) | max W d1-13 (on day) | max W d14-23 (on day) | max W d24-31 (on day) | max W d32-41 (on day) | max W d42-49 (on day) |
|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 2 | 0 (d1) | 1 (d10) | 1 (d10) | 0 (d14) | 0 (d24) | 0 (d32) | 1 (d48) |
| hh_s32_t03 | 9 | 2 (d3) | 0 (d8) | 2 (d3) | 0 (d14) | 3 (d27) | 1 (d32) | 2 (d46) |
| hh_s48_t03 | 19 | 6 (d4) | 0 (d8) | 6 (d4) | 5 (d15) | 2 (d26) | 0 (d32) | 3 (d45) |

### What the rule reacts to (first change, V1)


**hh_s2_t03** (movers by ground truth, for the reader only: book_tomas, charger_tomas, glass_ines, glass_tomas, mug_ines, mug_tomas, notebook_tomas, water_bottle_tomas)

- day 14 (W=2): glass_tomas [true mover]: dining -> bedroom_1 (d14); water_bottle_tomas [true mover]: kitchen -> bedroom_1 (d14)
- day 15 (W=8): blanket_shared: bedroom_1 -> living (d15); book_tomas [true mover]: bedroom_1 -> living (d15); mug_tomas [true mover]: kitchen -> living (d15); plate_tomas: kitchen -> living (d15); snack_bowl_shared: kitchen -> living (d15); vitamins_tomas: kitchen -> bedroom_1 (d15)
- day 16 (W=8): no object moved
- settled day 4 (W=5, window days 2-4): bowl_tomas: dining -> kitchen (d2); water_bottle_tomas [true mover]: office -> kitchen (d2); bowl_ines: kitchen -> dining (d4); glass_ines [true mover]: kitchen -> dining (d4); water_bottle_ines: kitchen -> dining (d4)
- settled day 5 (W=3, window days 3-5): bowl_ines: kitchen -> dining (d4); glass_ines [true mover]: kitchen -> dining (d4); water_bottle_ines: kitchen -> dining (d4)
- settled day 6 (W=3, window days 4-6): bowl_ines: kitchen -> dining (d4); glass_ines [true mover]: kitchen -> dining (d4); water_bottle_ines: kitchen -> dining (d4)

**hh_s32_t03** (movers by ground truth, for the reader only: book_leo, charger_leo, glass_leo, mug_leo, tablet_leo, towel_aisha, water_bottle_aisha, water_bottle_leo)

- day 14 (W=3): glass_leo [true mover]: kitchen -> bedroom_1 (d14); tablet_aisha: kitchen -> bedroom_3 (d14); water_bottle_leo [true mover]: kitchen -> bedroom_1 (d14)
- day 15 (W=3): no object moved
- day 16 (W=3): no object moved
- settled day 3 (W=8, window days 1-3): water_bottle_leo [true mover]: office -> kitchen (d1); charger_leo [true mover]: office -> bedroom_1 (d2); mug_leo [true mover]: office -> kitchen (d2); notebook_elena: bedroom_2 -> kitchen (d2, first seen there d1); tablet_leo [true mover]: bedroom_1 -> kitchen (d2); vacuum_cleaner_shared: living -> entry (d2); ironing_board_shared: bedroom_1 -> bedroom_2 (d3, first seen there d2); phone_leo: kitchen -> bathroom (d3)
- settled day 4 (W=7, window days 2-4): charger_leo [true mover]: office -> bedroom_1 (d2); mug_leo [true mover]: office -> kitchen (d2); notebook_elena: bedroom_2 -> kitchen (d2, first seen there d1); tablet_leo [true mover]: bedroom_1 -> kitchen (d2); vacuum_cleaner_shared: living -> entry (d2); ironing_board_shared: bedroom_1 -> bedroom_2 (d3, first seen there d2); phone_leo: kitchen -> bathroom (d3)
- settled day 2 (W=6, window days 1-2): water_bottle_leo [true mover]: office -> kitchen (d1); charger_leo [true mover]: office -> bedroom_1 (d2); mug_leo [true mover]: office -> kitchen (d2); notebook_elena: bedroom_2 -> kitchen (d2, first seen there d1); tablet_leo [true mover]: bedroom_1 -> kitchen (d2); vacuum_cleaner_shared: living -> entry (d2)

**hh_s48_t03** (movers by ground truth, for the reader only: book_marco, charger_marco, glass_marco, mug_marco, water_bottle_marco, water_bottle_priya)

- day 14 (W=12): charger_marco [true mover]: entry -> bedroom_1 (d14); glass_marco [true mover]: dining -> bedroom_1 (d14); hair_dryer_priya: bedroom_2 -> bathroom (d14); headphones_marco: office -> bedroom_1 (d14, first seen there d13); headphones_priya: entry -> bedroom_2 (d14, first seen there d13); jacket_priya: entry -> bedroom_2 (d14, first seen there d13); scarf_priya: entry -> bedroom_2 (d14, first seen there d13); skincare_marco: bathroom -> bedroom_1 (d14); toiletry_bag_marco: bathroom -> bedroom_1 (d14); water_bottle_marco [true mover]: kitchen -> bedroom_1 (d14)
- day 15 (W=14): blanket_shared: living -> bedroom_1 (d15, first seen there d14); bowl_marco: kitchen -> dining (d15)
- day 16 (W=14): skincare_priya: bathroom -> bedroom_2 (d16); vitamins_marco: kitchen -> bedroom_1 (d16)
- settled day 3 (W=12, window days 1-3): bowl_priya: dining -> kitchen (d1); glass_marco [true mover]: kitchen -> dining (d1); mug_marco [true mover]: dining -> office (d1); mug_priya: dining -> kitchen (d1); tablet_priya: bedroom_2 -> dining (d1); glass_priya: kitchen -> dining (d2, first seen there d1); plate_marco: kitchen -> dining (d2); plate_priya: kitchen -> dining (d2, first seen there d1); serving_dish_shared: kitchen -> dining (d2, first seen there d1); book_marco [true mover]: dining -> bedroom_1 (d3, first seen there d1); charger_priya: bedroom_2 -> entry (d3, first seen there d2); water_bottle_marco [true mover]: dining -> kitchen (d3)
- settled day 4 (W=10, window days 2-4): glass_priya: kitchen -> dining (d2, first seen there d1); plate_marco: kitchen -> dining (d2); plate_priya: kitchen -> dining (d2, first seen there d1); serving_dish_shared: kitchen -> dining (d2, first seen there d1); book_marco [true mover]: dining -> bedroom_1 (d3, first seen there d1); charger_priya: bedroom_2 -> entry (d3, first seen there d2); water_bottle_marco [true mover]: dining -> kitchen (d3); hair_dryer_priya: bedroom_2 -> bathroom (d4); laptop_marco: office -> dining (d4); skincare_marco: bathroom -> bedroom_1 (d4, first seen there d3)
- settled day 2 (W=9, window days 1-2): bowl_priya: dining -> kitchen (d1); glass_marco [true mover]: kitchen -> dining (d1); mug_marco [true mover]: dining -> office (d1); mug_priya: dining -> kitchen (d1); tablet_priya: bedroom_2 -> dining (d1); glass_priya: kitchen -> dining (d2, first seen there d1); plate_marco: kitchen -> dining (d2); plate_priya: kitchen -> dining (d2, first seen there d1); serving_dish_shared: kitchen -> dining (d2, first seen there d1)

## Word match on the nightly notes of the log-and-notes method

**This is a word match, not a reading.** A night 'matches' when its text contains one of the listed words; a match does not mean the note describes the change, and the quoted sentences below are there so a reader can judge that.

Cells under `results/self_improve/overnight_wave/cells/the_log_and_notes_about_the_routine`. These cells have no notes_by_night.jsonl and no nightly summaries; the notes are a claim store (notes.json) in which each claim keeps the night it was first written and the prior wording of every revision, so the text written on each night is rebuilt exactly (new claims as first worded, plus each revision's reason and the wording after it). Two views are scored:
- *written that night*: only the text the model added or changed on night n (the primary view);
- *whole file at end of night*: every claim as it read at the end of night n (a claim written on night 3 containing 'since' matches every later night under this view).

Words: ill, sick, unwell, not well, resting, changed, no longer, used to, now stays, now keeps, since (case-insensitive; ill/sick also match illness/sickness). Delay = first matching night >= 13, minus 14. False mentions = matching nights among 1-13.

### View 1: text written that night

| household | claims in file | first matching night >= 13 | delay from night 14 | matching nights 1-13 (false mentions) | all matching nights | words that fired (whole run) |
|---|---|---|---|---|---|---|
| hh_s2_t03 | 35 | 20 | 6 | 0 (-) | 20 | no longer x1 |
| hh_s19_t03 | 35 | none | none | 0 (-) | - | - |
| hh_s20_t03 | 48 | 16 | 2 | 0 (-) | 16, 29 | changed x2 |
| hh_s32_t03 | 38 | none | none | 1 (3) | 3 | changed x1 |
| hh_s48_t03 | 67 | 13 | -1 | 5 (3, 4, 6, 7, 13) | 3, 4, 6, 7, 13, 14, 15, 30, 31 | resting x3, changed x3, since x3, no longer x1 |
| hh_s63_t03 | 48 | none | none | 1 (5) | 5 | no longer x1 |
| hh_s93_t03 | 64 | 19 | 5 | 4 (2, 3, 4, 10) | 2, 3, 4, 10, 19, 23, 27 | changed x5, no longer x3, since x1 |
| hh_s109_t03 | 40 | 19 | 5 | 0 (-) | 19, 24, 29 | changed x2, resting x1 |
| hh_s123_t03 | 48 | 17 | 3 | 0 (-) | 17, 18, 20, 21, 31 | changed x3, resting x2, since x1, no longer x1 |
| hh_s151_t03 | 48 | 15 | 1 | 2 (9, 12) | 9, 12, 15, 18, 22 | changed x3, no longer x2, resting x1 |

Delay over households with a matching night >= 13: mean 3.00, sd 2.52, n = 7; 3 with none. Households with at least one false mention: 5 of 10.

### View 2: whole notes file as it read at the end of the night

| household | claims in file | first matching night >= 13 | delay from night 14 | matching nights 1-13 (false mentions) | all matching nights | words that fired (whole run) |
|---|---|---|---|---|---|---|
| hh_s2_t03 | 35 | none | none | 0 (-) | - | - |
| hh_s19_t03 | 35 | none | none | 0 (-) | - | - |
| hh_s20_t03 | 48 | none | none | 0 (-) | - | - |
| hh_s32_t03 | 38 | none | none | 0 (-) | - | - |
| hh_s48_t03 | 67 | 13 | -1 | 1 (13) | 13, 14, 15 | since x2, resting x1 |
| hh_s63_t03 | 48 | none | none | 1 (5) | 5 | no longer x1 |
| hh_s93_t03 | 64 | none | none | 3 (2, 3, 4) | 2, 3, 4 | no longer x3 |
| hh_s109_t03 | 40 | none | none | 0 (-) | - | - |
| hh_s123_t03 | 48 | 20 | 6 | 0 (-) | 20 | since x1 |
| hh_s151_t03 | 48 | none | none | 1 (9) | 9 | no longer x1 |

Delay over households with a matching night >= 13: mean 2.50, sd 4.95, n = 2; 8 with none. Households with at least one false mention: 4 of 10.

### Quoted sentences, view 1, from the first matching night >= 13

Three households chosen as the first three in the study's household order that have a matching night; the sentence is the one that holds the first match in that night's text, with the claim id and whether the line is a new claim or a revision. Below those, one line per remaining household, so nothing is hidden.

- **hh_s2_t03**, night 20 (delay 6), words no longer: "The previous belief is no longer supported by recent evidence."
  - the whole note line it sits in: `[claim_0015 revised] why: Today's sightings show the plate in the living room, not the kitchen. The previous belief is no longer supported by recent evidence.`
- **hh_s19_t03**: no matching night 13-31.
- **hh_s20_t03**, night 16 (delay 2), words changed: "This suggests she may be working on a different device or has changed her setup."
  - the whole note line it sits in: `[claim_0001 revised] why: The office contained only minimal items on Day 16, unlike previous days where a full workstation was present. This suggests she may be working on a different device or has changed her setup. | now: Hana works from the office during the day. On Day 16, only her pen and mouse were found on the office desk. Her laptop, charger, glasses, headphones, mug, and water bottle were not in the office. (when: When Hana is working during the day)`
- **hh_s32_t03**: no matching night 13-31.
- **hh_s48_t03**, night 13 (delay -1), words since: "It has been on the sink since Day 9."
  - the whole note line it sits in: `[claim_0011 revised] why: Consistent location on the sink across multiple sightings today. | now: Priya's razor is on the bathroom sink. Observed on sink at 08:36, 09:55, and 19:26 on Day 13. It has been on the sink since Day 9. (when: General state, observed Day 9-13.)`
- **hh_s63_t03**: no matching night 13-31.
- **hh_s93_t03**, night 19 (delay 5), words changed: "[claim_0006 revised] why: Location changed from side table to coffee table between Day 18 and Day 19."
- **hh_s109_t03**, night 19 (delay 5), words resting: "This suggests the coffee table is his default resting spot for glasses in the living room."
- **hh_s123_t03**, night 17 (delay 3), words changed: "[claim_0012 revised] why: Location changed from counter to sink between 15:10 and 20:59."
- **hh_s151_t03**, night 15 (delay 1), words changed: "[claim_0001 revised] why: The towel location changed from shelf to rack during the morning and stayed on the rack for the rest of the day."

### The false mentions, view 1: the sentence behind each matching night 1-13

- hh_s32_t03, night 3, words changed: "The food bag location changed from chair to pantry shelf."
- hh_s48_t03, night 3, words resting: "[claim_0003 revised] why: The bag has been on the sink for multiple consecutive mornings, suggesting this is its current resting place rather than a temporary mid-day state."
- hh_s48_t03, night 4, words no longer: "It is no longer in the bathroom."
- hh_s48_t03, night 6, words changed: "[claim_0003 revised] why: Location changed from sink to shelf between Day 5 and Day 6."
- hh_s48_t03, night 7, words since: "[claim_0003 revised] why: The bag has consistently been on the sink since 08:01 on Day 7, contradicting the previous note that it was on the shelf."
- hh_s48_t03, night 13, words since: "It has been on the sink since Day 9."
- hh_s63_t03, night 5, words no longer: "However, by evening (21:29) it is no longer there."
- hh_s93_t03, night 2, words changed, no longer, since: "[claim_0003 revised] why: Medication location changed from cabinet to shelf between 07:11 and 08:47."
- hh_s93_t03, night 3, words no longer: "By 19:24, her mug and water bottle are in the kitchen, and her laptop is no longer in the office."
- hh_s93_t03, night 4, words no longer: "By 20:01 on Day 4, her water bottle is in the kitchen, and her laptop, mug, and glasses are no longer in the office."
- hh_s93_t03, night 10, words changed: "[claim_0021 revised] why: Water bottle location changed from office to kitchen between afternoon and evening on Day 10."
- hh_s151_t03, night 9, words no longer: "The razor is no longer on the sink; it is on the shelf."
- hh_s151_t03, night 12, words changed: "[claim_0003 revised] why: The razor's location changed from shelf to sink between 07:31 and 08:12, indicating a morning routine shift."

## Plain notes on anything odd

Written after reading the tables above. Figures quoted are from this file (ten-household run unless said).

1. Under the Addendum's rule (k from days 1-13, zero alarm days in the pool), baseline 2 V1 detects 1 of 10
   households (hh_s48, delay 1) at zero false alarm days and one return-alarm household; V2 detects 0 of 10 with
   one false alarm day (hh_s2, day 4). k is 9 for V1 in every household (7 for V2), set by hh_s48 and hh_s151,
   whose largest settled W (8) falls on days 4 and 6. The Addendum's prediction (0-2 days in at least seven of
   ten) is not met under this rule.

2. The settled peaks are a warm-up effect of the definition, not meal-time moves persisting. On days 1-7 the
   seven-day window is still filling: the first time an object is seen in each of its ordinary rooms (crockery
   seen in the dining room on day 1 and in the kitchen on day 2) the room has no earlier sighting, so the
   object counts as having moved there. The largest settled W is on days 1-6 in 9 of 10 households; on days
   8-13 W never exceeds 4 (hh_s48) and is 0 to 3 elsewhere, while the sick-window peaks are 3 to 9. The
   object lists for the loudest settled windows show it: plates, bowls and glasses kitchen <-> dining on days
   1-4, and a resident's charger, headphones, pen first seen in one room and then another. The Addendum says
   days 1-13, so that is the rule reported; the days-8-13 contrast is labelled as a contrast.

3. Under the contrast (k from days 8-13: k = 5 for V1, 4 or 3 for V2), V1 detects 4 of 10 (hh_s48 0,
   hh_s20 1, hh_s93 1, hh_s123 4; mean 1.5, sd 1.7), with one false alarm day on days 8-13 (hh_s48 day 13,
   W = 4 from a jacket, a hair dryer, a scarf and a towel moving between entry, bathroom and bedrooms on days 11-13) and warm-up alarms on days 2-6 in 4 households
   (hh_s2, hh_s48, hh_s109, hh_s151). Return alarms then appear in 6 of 10. V2 detects 3 of 10 (delays 1,
   1, 4). Six (V1) or seven (V2) households are still not detected within the sick window.

4. Why the change gives small counts. The rule needs two consecutive sightings of the same object in a room
   it had not been seen in for a week; one look into the bedroom gives the first sighting, and the confirming
   one needs a later look into the same room before the object is seen anywhere else. Of the 5-9 ground-truth
   movers per household, 3 to 6 get a move day inside days 14-23 (hh_s2 4 of 8, hh_s19 3 of 7, hh_s20 6 of 9,
   hh_s32 4 of 8, hh_s48 4 of 6, hh_s63 5 of 9, hh_s93 6 of 9, hh_s109 3 of 6, hh_s123 3 of 5, hh_s151 3 of
   8), and they do not all fall in one three-day window: the daily "moved" counts on days 14-16 are 0 to 6.
   Objects outside the movers list also move with the sick resident (vitamins, blanket_shared, headphones,
   skincare, toiletry bag, tablet) and count the same. hh_s123's first moves are on days 17-18 although it
   looked into the sick rooms on day 14 (RESULTS_baseline.md): its objects were each seen once there, not
   twice in a row, until day 17.

5. V2 (confirming sighting on a later day) halves the move events (e.g. hh_s2 23 -> 12, hh_s48 34 -> 18) and
   removes most of the day-14 and day-15 events, because two looks into the bedroom on the same sick day are
   what usually confirm a move. It lowers the warm-up peaks less than it lowers the sick-window peaks in most
   households.

6. 50-day run (24 questions a day). hh_s48 is louder than the other two in its own settled week (W = 12 on
   day 3 against k = 9 from hh_s2 and hh_s32), so it has 3 false alarm days (2, 3, 4; 6.9 a month) and detects
   the first spell at delay 0 but not the second (W peaks at 6 on days 32-41, under 9). hh_s2 and hh_s32 get
   k = 13 from hh_s48 and detect nothing in either spell (their spell peaks are 8 and 6, 7 and 11). Under the
   days-8-13 contrast V1 detects both spells in all three (delays 1, 4, 0 and 0, 0, 0), with 8 to 20 alarm
   days per household over the run and hh_s48 at k = 2 alarming on 40 of 49 days.

7. Notes word match. None of ill, sick, illness, sickness, unwell or "not well" appears in any night's text in
   any of the ten households, in either view. The words that fire are changed (19 nights), no longer (9),
   since (5), resting (7), almost all in a revision's "why" line about one object's place within a day
   ("Location changed from counter to sink between 15:10 and 20:59"). View 1 (text written that night): 7 of 10
   households have a matching night on or after night 13 (nights 13, 15, 16, 17, 19, 19, 20; delays -1 to 6,
   mean 3.0, sd 2.5); 5 of 10 have false mentions on nights 1-13 (1 to 5 nights). The first-match sentences
   on or after night 13 are about: a plate (hh_s2, night 20), Hana's office being empty on day 16 (hh_s20,
   night 16; Hana's things are the movers in that household), a razor on a sink "since Day 9" (hh_s48, night
   13), a medication's side table (hh_s93, night 19), a glasses' coffee table (hh_s109), a counter-to-sink
   move (hh_s123), Dana's towel shelf-to-rack (hh_s151, night 15; towel_dana is in that household's movers
   list). The reader decides which of these describe the change; the word match does not.

8. View 2 (the whole file as it read each night) matches less than view 1 because a revision's "why" text is
   not part of the file state, only the statement and holds_under are; 2 of 10 households match on or after
   night 13 under view 2. The Addendum's "first night whose note contains" is closer to view 1.

9. Night 13 is counted as "on or after night 13" as the brief says, so hh_s48's delay is -1; the match on that
   night (razor, "since Day 9") precedes the change.

10. Mechanics worth knowing. The log-and-notes cells hold no notes_by_night.jsonl; the per-night text was
    rebuilt from notes.json's claims (first_written_day and revision_history keep every earlier wording), so
    it is exact for what was written, including wording later overwritten. Sightings skipped for having no
    sighting of the object in the previous seven days: 79 of 2,537 in hh_s2 (first sightings and
    reappearances after a week unseen). The word list was applied to all text, not only to text "applied to a
    resident or an object" as the Addendum says; no such filter was attempted.

