# Study 2 baseline: the surprise count, computed

Computed by `surprise_count.py` beside this file, from the last-seen (no model) cells. The definitions are in the script's docstring; the ones that needed a decision are repeated here.

- Stream: every sighting from every look, in (day, time, file order). A look records every object in the room it opened, so one look can add many sightings at once.
- A (last-seen): predicted room = room of the object's previous sighting.
- B (7-day commonest): predicted room = commonest room among the object's earlier sightings with day >= today-7 (past seven days plus earlier today); ties go to the most recent room.
- Alarm day: the sum of surprising sightings over days d-2..d exceeds T. Each day over T is one alarm day.
- Threshold, strict (SETUP's rule read literally): T is the smallest integer such that every other household in the pool has alarms*30/13 <= 1 on days 1-13. One alarm in 13 days is 2.3 a month, so this means zero alarm days on days 1-13 for every pool household; T equals the largest 3-day sum any pool household shows on days 1-13.
- Threshold, loose (reported for contrast only): at most one raw alarm day on days 1-13 per pool household, which is 2.3 a month and does not meet the SETUP bar.
- Delay: first alarm day in 14..23 minus 14 (0 = day 14); 'none' if no alarm by day 23. Return alarms on days 24-31 are counted separately and are not false alarms.

## Ten households, 31 days, 8 questions a day

Cells under `results/self_improve/overnight_wave/cells/last_seen_no_model`. Present: 10 of 10. None missing.
Per household: sightings in the stream, and sightings skipped for lack of an earlier sighting (A) or of one in the 7-day window (B).

| household | sightings | skipped A | skipped B | sightings/day, days 1-13 mean | days 14-23 mean |
|---|---|---|---|---|---|
| hh_s2_t03 | 2537 | 62 | 79 | 84 | 79 |
| hh_s19_t03 | 3912 | 79 | 102 | 130 | 114 |
| hh_s20_t03 | 3455 | 83 | 107 | 105 | 130 |
| hh_s32_t03 | 4653 | 99 | 124 | 153 | 162 |
| hh_s48_t03 | 3701 | 96 | 124 | 141 | 102 |
| hh_s63_t03 | 2238 | 66 | 91 | 71 | 80 |
| hh_s93_t03 | 3236 | 77 | 113 | 107 | 103 |
| hh_s109_t03 | 3213 | 79 | 104 | 113 | 105 |
| hh_s123_t03 | 3961 | 84 | 122 | 131 | 120 |
| hh_s151_t03 | 3451 | 86 | 131 | 121 | 113 |

### Per-household scores, leave-one-out threshold


**Definition A: last-seen room** (threshold rule: strict)

| household | T (alarm when 3-day sum > T) | delay from day 14 | false alarm days 1-13 (raw) | false alarms per month | alarm days 24-31 (return) |
|---|---|---|---|---|---|
| hh_s2_t03 | 42 | none | 1 | 2.31 | 0 |
| hh_s19_t03 | 47 | none | 0 | 0.00 | 0 |
| hh_s20_t03 | 47 | none | 0 | 0.00 | 1 |
| hh_s32_t03 | 47 | none | 0 | 0.00 | 0 |
| hh_s48_t03 | 47 | none | 0 | 0.00 | 0 |
| hh_s63_t03 | 47 | none | 0 | 0.00 | 0 |
| hh_s93_t03 | 47 | none | 0 | 0.00 | 0 |
| hh_s109_t03 | 47 | none | 0 | 0.00 | 0 |
| hh_s123_t03 | 47 | none | 0 | 0.00 | 0 |
| hh_s151_t03 | 47 | none | 0 | 0.00 | 0 |

Delay from day 14 over households: mean n/a, sd n/a (n = 0 detected; 10 with no alarm on days 14-23; 'none' excluded from the mean).
False alarms per month over households: mean 0.23.
Households with at least one return alarm: 1 of 10.

**Definition B: commonest room, past 7 days** (threshold rule: strict)

| household | T (alarm when 3-day sum > T) | delay from day 14 | false alarm days 1-13 (raw) | false alarms per month | alarm days 24-31 (return) |
|---|---|---|---|---|---|
| hh_s2_t03 | 47 | none | 0 | 0.00 | 2 |
| hh_s19_t03 | 47 | none | 0 | 0.00 | 0 |
| hh_s20_t03 | 47 | 2 | 0 | 0.00 | 4 |
| hh_s32_t03 | 47 | none | 0 | 0.00 | 0 |
| hh_s48_t03 | 47 | 2 | 0 | 0.00 | 0 |
| hh_s63_t03 | 47 | none | 0 | 0.00 | 0 |
| hh_s93_t03 | 47 | 2 | 0 | 0.00 | 3 |
| hh_s109_t03 | 47 | none | 0 | 0.00 | 0 |
| hh_s123_t03 | 47 | none | 0 | 0.00 | 0 |
| hh_s151_t03 | 42 | none | 2 | 4.62 | 0 |

Delay from day 14 over households: mean 2.00, sd 0.00 (n = 3 detected; 7 with no alarm on days 14-23; 'none' excluded from the mean).
False alarms per month over households: mean 0.46.
Households with at least one return alarm: 3 of 10.

#### The same with the loose threshold rule (not SETUP's bar; for contrast)

**Definition A: last-seen room** (threshold rule: loose)

| household | T (alarm when 3-day sum > T) | delay from day 14 | false alarm days 1-13 (raw) | false alarms per month | alarm days 24-31 (return) |
|---|---|---|---|---|---|
| hh_s2_t03 | 42 | none | 1 | 2.31 | 0 |
| hh_s19_t03 | 42 | none | 0 | 0.00 | 0 |
| hh_s20_t03 | 42 | none | 0 | 0.00 | 3 |
| hh_s32_t03 | 42 | none | 0 | 0.00 | 0 |
| hh_s48_t03 | 42 | none | 0 | 0.00 | 0 |
| hh_s63_t03 | 42 | none | 0 | 0.00 | 0 |
| hh_s93_t03 | 42 | none | 0 | 0.00 | 0 |
| hh_s109_t03 | 42 | 1 | 0 | 0.00 | 0 |
| hh_s123_t03 | 42 | none | 0 | 0.00 | 0 |
| hh_s151_t03 | 41 | none | 2 | 4.62 | 0 |

Delay from day 14 over households: mean 1.00, sd 0.00 (n = 1 detected; 9 with no alarm on days 14-23; 'none' excluded from the mean).
False alarms per month over households: mean 0.69.
Households with at least one return alarm: 1 of 10.

**Definition B: commonest room, past 7 days** (threshold rule: loose)

| household | T (alarm when 3-day sum > T) | delay from day 14 | false alarm days 1-13 (raw) | false alarms per month | alarm days 24-31 (return) |
|---|---|---|---|---|---|
| hh_s2_t03 | 46 | none | 0 | 0.00 | 2 |
| hh_s19_t03 | 46 | none | 0 | 0.00 | 0 |
| hh_s20_t03 | 46 | 2 | 0 | 0.00 | 4 |
| hh_s32_t03 | 46 | none | 0 | 0.00 | 0 |
| hh_s48_t03 | 46 | 1 | 0 | 0.00 | 0 |
| hh_s63_t03 | 46 | none | 0 | 0.00 | 0 |
| hh_s93_t03 | 46 | 2 | 0 | 0.00 | 3 |
| hh_s109_t03 | 46 | none | 0 | 0.00 | 0 |
| hh_s123_t03 | 46 | none | 0 | 0.00 | 0 |
| hh_s151_t03 | 40 | none | 2 | 4.62 | 0 |

Delay from day 14 over households: mean 1.67, sd 0.58 (n = 3 detected; 7 with no alarm on days 14-23; 'none' excluded from the mean).
False alarms per month over households: mean 0.46.
Households with at least one return alarm: 3 of 10.

### Day-by-day counts, days 10-18

Raw surprising-sighting counts per day under both definitions, with the number of sightings and the number of rooms opened that day. The change is on day 14.



| household | row | d10 | d11 | d12 | d13 | d14 | d15 | d16 | d17 | d18 |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | surprising (A last-seen) | 2 | 4 | 13 | 6 | 15 | 3 | 9 | 5 | 14 |
| hh_s2_t03 | surprising (B 7-day) | 2 | 5 | 12 | 6 | 18 | 9 | 13 | 7 | 21 |
| hh_s2_t03 | sightings | 62 | 60 | 104 | 86 | 102 | 58 | 98 | 84 | 114 |
| hh_s2_t03 | looks (rooms opened) | 8 | 8 | 12 | 9 | 13 | 8 | 12 | 11 | 12 |
| hh_s19_t03 | surprising (A last-seen) | 4 | 2 | 4 | 4 | 5 | 2 | 15 | 7 | 6 |
| hh_s19_t03 | surprising (B 7-day) | 4 | 2 | 4 | 2 | 4 | 4 | 10 | 7 | 6 |
| hh_s19_t03 | sightings | 125 | 113 | 113 | 119 | 83 | 94 | 174 | 97 | 95 |
| hh_s19_t03 | looks (rooms opened) | 9 | 9 | 9 | 10 | 10 | 10 | 13 | 9 | 9 |
| hh_s20_t03 | surprising (A last-seen) | 9 | 8 | 3 | 7 | 15 | 13 | 6 | 5 | 1 |
| hh_s20_t03 | surprising (B 7-day) | 7 | 8 | 3 | 6 | 14 | 26 | 17 | 12 | 4 |
| hh_s20_t03 | sightings | 121 | 97 | 73 | 89 | 174 | 152 | 95 | 148 | 110 |
| hh_s20_t03 | looks (rooms opened) | 10 | 9 | 9 | 9 | 17 | 15 | 13 | 13 | 10 |
| hh_s32_t03 | surprising (A last-seen) | 6 | 4 | 5 | 4 | 5 | 4 | 3 | 1 | 6 |
| hh_s32_t03 | surprising (B 7-day) | 5 | 4 | 3 | 1 | 5 | 8 | 6 | 4 | 3 |
| hh_s32_t03 | sightings | 155 | 204 | 131 | 135 | 150 | 201 | 207 | 172 | 190 |
| hh_s32_t03 | looks (rooms opened) | 9 | 9 | 9 | 9 | 12 | 14 | 11 | 12 | 13 |
| hh_s48_t03 | surprising (A last-seen) | 15 | 6 | 10 | 2 | 20 | 10 | 6 | 5 | 5 |
| hh_s48_t03 | surprising (B 7-day) | 17 | 10 | 11 | 5 | 27 | 15 | 12 | 11 | 4 |
| hh_s48_t03 | sightings | 158 | 96 | 133 | 92 | 171 | 139 | 89 | 106 | 72 |
| hh_s48_t03 | looks (rooms opened) | 11 | 10 | 11 | 10 | 15 | 11 | 10 | 9 | 8 |
| hh_s63_t03 | surprising (A last-seen) | 1 | 1 | 1 | 1 | 0 | 2 | 2 | 8 | 5 |
| hh_s63_t03 | surprising (B 7-day) | 1 | 0 | 1 | 1 | 0 | 6 | 3 | 6 | 5 |
| hh_s63_t03 | sightings | 53 | 74 | 68 | 59 | 63 | 120 | 75 | 99 | 75 |
| hh_s63_t03 | looks (rooms opened) | 8 | 8 | 9 | 8 | 8 | 14 | 10 | 10 | 8 |
| hh_s93_t03 | surprising (A last-seen) | 3 | 3 | 8 | 2 | 8 | 6 | 4 | 1 | 4 |
| hh_s93_t03 | surprising (B 7-day) | 3 | 0 | 4 | 1 | 8 | 20 | 21 | 11 | 8 |
| hh_s93_t03 | sightings | 87 | 95 | 146 | 77 | 138 | 142 | 74 | 97 | 99 |
| hh_s93_t03 | looks (rooms opened) | 9 | 9 | 11 | 8 | 13 | 11 | 8 | 8 | 8 |
| hh_s109_t03 | surprising (A last-seen) | 7 | 3 | 2 | 16 | 14 | 15 | 6 | 9 | 10 |
| hh_s109_t03 | surprising (B 7-day) | 5 | 2 | 0 | 9 | 8 | 8 | 3 | 7 | 5 |
| hh_s109_t03 | sightings | 81 | 76 | 77 | 134 | 155 | 111 | 121 | 141 | 109 |
| hh_s109_t03 | looks (rooms opened) | 10 | 9 | 8 | 11 | 14 | 12 | 12 | 14 | 10 |
| hh_s123_t03 | surprising (A last-seen) | 2 | 5 | 2 | 1 | 3 | 1 | 5 | 3 | 2 |
| hh_s123_t03 | surprising (B 7-day) | 1 | 3 | 2 | 1 | 1 | 4 | 3 | 7 | 9 |
| hh_s123_t03 | sightings | 161 | 152 | 110 | 129 | 177 | 131 | 106 | 124 | 84 |
| hh_s123_t03 | looks (rooms opened) | 9 | 10 | 9 | 9 | 12 | 13 | 9 | 10 | 8 |
| hh_s151_t03 | surprising (A last-seen) | 5 | 8 | 0 | 0 | 24 | 6 | 3 | 10 | 12 |
| hh_s151_t03 | surprising (B 7-day) | 2 | 9 | 2 | 0 | 14 | 11 | 10 | 12 | 13 |
| hh_s151_t03 | sightings | 107 | 107 | 69 | 68 | 162 | 107 | 89 | 139 | 127 |
| hh_s151_t03 | looks (rooms opened) | 10 | 10 | 8 | 8 | 14 | 11 | 11 | 11 | 13 |

### How high the count runs in each window

Mean surprising sightings a day in the settled, sick and return windows, and the largest 3-day sum inside each window (the day it falls on). The strict threshold for a household is the largest settled-window 3-day sum among the other nine, so a household is detected only if its sick-window maximum exceeds that.

Definition A: last-seen room:

| household | mean/day d1-13 | mean/day d14-23 | mean/day d24-31 | max 3-day sum d1-13 (on day) | max 3-day sum d14-23 (on day) | max 3-day sum d24-31 (on day) |
|---|---|---|---|---|---|---|
| hh_s2_t03 | 7.9 | 5.9 | 8.2 | 47 (d5) | 34 (d14) | 39 (d25) |
| hh_s19_t03 | 5.2 | 8.1 | 7.4 | 26 (d3) | 30 (d22) | 34 (d24) |
| hh_s20_t03 | 7.5 | 10.3 | 10.8 | 37 (d5) | 37 (d23) | 49 (d24) |
| hh_s32_t03 | 3.6 | 3.3 | 5.2 | 15 (d12) | 14 (d14) | 26 (d29) |
| hh_s48_t03 | 8.4 | 6.0 | 9.2 | 38 (d5) | 36 (d16) | 40 (d26) |
| hh_s63_t03 | 1.5 | 3.9 | 1.6 | 10 (d6) | 17 (d19) | 18 (d25) |
| hh_s93_t03 | 4.4 | 3.6 | 4.5 | 19 (d5) | 18 (d14) | 19 (d25) |
| hh_s109_t03 | 7.7 | 7.5 | 5.2 | 31 (d4) | 45 (d15) | 22 (d24) |
| hh_s123_t03 | 1.5 | 2.8 | 2.9 | 9 (d12) | 10 (d18) | 14 (d25) |
| hh_s151_t03 | 7.5 | 8.4 | 6.6 | 42 (d5) | 33 (d16) | 37 (d30) |

Definition B: commonest room, past 7 days:

| household | mean/day d1-13 | mean/day d14-23 | mean/day d24-31 | max 3-day sum d1-13 (on day) | max 3-day sum d14-23 (on day) | max 3-day sum d24-31 (on day) |
|---|---|---|---|---|---|---|
| hh_s2_t03 | 7.7 | 9.0 | 11.0 | 42 (d5) | 41 (d18) | 57 (d26) |
| hh_s19_t03 | 5.4 | 6.5 | 7.1 | 30 (d4) | 24 (d19) | 28 (d28) |
| hh_s20_t03 | 6.3 | 12.8 | 13.6 | 31 (d6) | 57 (d16) | 75 (d26) |
| hh_s32_t03 | 3.0 | 4.2 | 6.6 | 14 (d11) | 19 (d16) | 28 (d26) |
| hh_s48_t03 | 9.0 | 7.7 | 10.2 | 41 (d5) | 54 (d16) | 44 (d26) |
| hh_s63_t03 | 1.2 | 4.4 | 3.6 | 9 (d6) | 16 (d19) | 26 (d25) |
| hh_s93_t03 | 2.5 | 8.9 | 10.5 | 13 (d4) | 52 (d17) | 65 (d26) |
| hh_s109_t03 | 5.5 | 5.2 | 4.0 | 26 (d3) | 25 (d15) | 17 (d24) |
| hh_s123_t03 | 1.3 | 3.4 | 3.2 | 6 (d12) | 19 (d18) | 17 (d26) |
| hh_s151_t03 | 8.2 | 9.6 | 9.9 | 47 (d6) | 35 (d16) | 40 (d28) |

### Alarm days under the strict threshold, every day 1-31


Definition A: last-seen room:

| household | T | alarm days |
|---|---|---|
| hh_s2_t03 | 42 | 5 |
| hh_s19_t03 | 47 | - |
| hh_s20_t03 | 47 | 24 |
| hh_s32_t03 | 47 | - |
| hh_s48_t03 | 47 | - |
| hh_s63_t03 | 47 | - |
| hh_s93_t03 | 47 | - |
| hh_s109_t03 | 47 | - |
| hh_s123_t03 | 47 | - |
| hh_s151_t03 | 47 | - |

Definition B: commonest room, past 7 days:

| household | T | alarm days |
|---|---|---|
| hh_s2_t03 | 47 | 25, 26 |
| hh_s19_t03 | 47 | - |
| hh_s20_t03 | 47 | 16, 17, 24, 25, 26, 27 |
| hh_s32_t03 | 47 | - |
| hh_s48_t03 | 47 | 16 |
| hh_s63_t03 | 47 | - |
| hh_s93_t03 | 47 | 16, 17, 25, 26, 27 |
| hh_s109_t03 | 47 | - |
| hh_s123_t03 | 47 | - |
| hh_s151_t03 | 42 | 5, 6 |

### Does the robot look into the rooms the sick resident's things go to?

Ground truth is used here only to describe the data, not in the baseline. 'Rooms the movers go to when sick' are the true rooms of mover objects on days 14-23 that are not the object's true room on days 1-13, from searches.jsonl.

| household | movers | rooms the movers go to when sick (not their settled room) | looks into those rooms on day 14 / +1 / +2 | first day >= 14 the robot opened one |
|---|---|---|---|---|
| hh_s2_t03 | 8 | bedroom_1, kitchen, living | 5 / 2 / 3 | 14 |
| hh_s19_t03 | 7 | bedroom_1, living | 1 / 2 / 2 | 14 |
| hh_s20_t03 | 9 | bedroom_1, living | 1 / 4 / 4 | 14 |
| hh_s32_t03 | 8 | bedroom_1, living | 1 / 4 / 2 | 14 |
| hh_s48_t03 | 6 | bedroom_1, dining, kitchen, living | 7 / 5 / 5 | 14 |
| hh_s63_t03 | 9 | bedroom_1, living | 0 / 3 / 2 | 15 |
| hh_s93_t03 | 9 | bedroom_1, kitchen, living | 6 / 9 / 5 | 14 |
| hh_s109_t03 | 6 | bedroom_1, kitchen, living | 4 / 2 / 2 | 14 |
| hh_s123_t03 | 5 | bedroom_1, living | 1 / 1 / 1 | 14 |
| hh_s151_t03 | 8 | bathroom, bedroom_1, living | 6 / 6 / 7 | 14 |

## Three households, 50 days, 24 questions a day

Cells under `results/self_improve/wave_the_second_illness/cells/last_seen_no_model`. Present: 3 of 3. None missing. The last question day is 49, so the second return is days 42-49. The threshold is chosen leave-one-out within these three (on the other two), because at 24 questions a day the sighting rate is about three times the 8-a-day run and a threshold tuned there would not transfer.

| household | sightings | skipped A | skipped B | sightings/day, days 1-13 mean | days 14-23 mean | days 32-41 mean |
|---|---|---|---|---|---|---|
| hh_s2_t03 | 11481 | 76 | 99 | 248 | 233 | 226 |
| hh_s32_t03 | 19992 | 104 | 167 | 409 | 426 | 393 |
| hh_s48_t03 | 16516 | 98 | 115 | 332 | 365 | 347 |

### Per-household scores, leave-one-out threshold (pool = the other two)


**Definition A: last-seen room** (threshold rule: strict)

| household | T (alarm when 3-day sum > T) | delay from day 14 | delay from day 32 | false alarm days 1-13 (raw) | false alarms per month | alarm days 24-31 (return) | alarm days 42-49 (return) |
|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 67 | none | none | 0 | 0.00 | 0 | 3 |
| hh_s32_t03 | 67 | none | none | 0 | 0.00 | 0 | 0 |
| hh_s48_t03 | 67 | none | none | 0 | 0.00 | 0 | 1 |

Delay from day 14 over households: mean n/a, sd n/a (n = 0 detected; 3 with no alarm on days 14-23; 'none' excluded from the mean).

Delay from day 32 over households: mean n/a, sd n/a (n = 0 detected; 3 with no alarm on days 32-41; 'none' excluded from the mean).
False alarms per month over households: mean 0.00.
Households with at least one return alarm: 2 of 3.

**Definition B: commonest room, past 7 days** (threshold rule: strict)

| household | T (alarm when 3-day sum > T) | delay from day 14 | delay from day 32 | false alarm days 1-13 (raw) | false alarms per month | alarm days 24-31 (return) | alarm days 42-49 (return) |
|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 80 | 0 | 0 | 0 | 0.00 | 2 | 4 |
| hh_s32_t03 | 80 | 2 | 1 | 0 | 0.00 | 2 | 4 |
| hh_s48_t03 | 73 | 0 | 1 | 3 | 6.92 | 7 | 5 |

Delay from day 14 over households: mean 0.67, sd 1.15 (n = 3 detected; 0 with no alarm on days 14-23; 'none' excluded from the mean).

Delay from day 32 over households: mean 0.67, sd 0.58 (n = 3 detected; 0 with no alarm on days 32-41; 'none' excluded from the mean).
False alarms per month over households: mean 2.31.
Households with at least one return alarm: 3 of 3.

#### The same with the loose threshold rule (for contrast)

**Definition A: last-seen room** (threshold rule: loose)

| household | T (alarm when 3-day sum > T) | delay from day 14 | delay from day 32 | false alarm days 1-13 (raw) | false alarms per month | alarm days 24-31 (return) | alarm days 42-49 (return) |
|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 60 | none | 0 | 3 | 6.92 | 0 | 7 |
| hh_s32_t03 | 67 | none | none | 0 | 0.00 | 0 | 0 |
| hh_s48_t03 | 67 | none | none | 0 | 0.00 | 0 | 1 |

Delay from day 14 over households: mean n/a, sd n/a (n = 0 detected; 3 with no alarm on days 14-23; 'none' excluded from the mean).

Delay from day 32 over households: mean 0.00, sd 0.00 (n = 1 detected; 2 with no alarm on days 32-41; 'none' excluded from the mean).
False alarms per month over households: mean 2.31.
Households with at least one return alarm: 2 of 3.

**Definition B: commonest room, past 7 days** (threshold rule: loose)

| household | T (alarm when 3-day sum > T) | delay from day 14 | delay from day 32 | false alarm days 1-13 (raw) | false alarms per month | alarm days 24-31 (return) | alarm days 42-49 (return) |
|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 78 | 0 | 0 | 0 | 0.00 | 3 | 4 |
| hh_s32_t03 | 78 | 2 | 1 | 0 | 0.00 | 2 | 4 |
| hh_s48_t03 | 73 | 0 | 1 | 3 | 6.92 | 7 | 5 |

Delay from day 14 over households: mean 0.67, sd 1.15 (n = 3 detected; 0 with no alarm on days 14-23; 'none' excluded from the mean).

Delay from day 32 over households: mean 0.67, sd 0.58 (n = 3 detected; 0 with no alarm on days 32-41; 'none' excluded from the mean).
False alarms per month over households: mean 2.31.
Households with at least one return alarm: 3 of 3.

### Day-by-day counts, days 10-18 and days 28-36


Around the first change (day 14):

| household | row | d10 | d11 | d12 | d13 | d14 | d15 | d16 | d17 | d18 |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | surprising (A last-seen) | 12 | 12 | 18 | 18 | 19 | 11 | 3 | 11 | 11 |
| hh_s2_t03 | surprising (B 7-day) | 15 | 6 | 19 | 15 | 51 | 51 | 30 | 27 | 36 |
| hh_s2_t03 | sightings | 203 | 206 | 246 | 224 | 374 | 194 | 219 | 199 | 269 |
| hh_s2_t03 | looks (rooms opened) | 26 | 25 | 28 | 28 | 43 | 25 | 24 | 25 | 27 |
| hh_s32_t03 | surprising (A last-seen) | 7 | 6 | 10 | 7 | 13 | 7 | 3 | 1 | 8 |
| hh_s32_t03 | surprising (B 7-day) | 8 | 12 | 6 | 4 | 24 | 29 | 32 | 29 | 29 |
| hh_s32_t03 | sightings | 341 | 404 | 382 | 351 | 453 | 436 | 533 | 428 | 370 |
| hh_s32_t03 | looks (rooms opened) | 26 | 25 | 26 | 25 | 33 | 30 | 35 | 30 | 28 |
| hh_s48_t03 | surprising (A last-seen) | 20 | 2 | 5 | 10 | 25 | 16 | 15 | 14 | 11 |
| hh_s48_t03 | surprising (B 7-day) | 28 | 6 | 13 | 15 | 75 | 42 | 53 | 53 | 28 |
| hh_s48_t03 | sightings | 355 | 252 | 273 | 232 | 478 | 347 | 340 | 365 | 349 |
| hh_s48_t03 | looks (rooms opened) | 29 | 25 | 26 | 30 | 45 | 35 | 37 | 36 | 35 |

Around the second change (day 32):

| household | row | d28 | d29 | d30 | d31 | d32 | d33 | d34 | d35 | d36 |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | surprising (A last-seen) | 2 | 3 | 14 | 26 | 23 | 10 | 6 | 2 | 4 |
| hh_s2_t03 | surprising (B 7-day) | 2 | 10 | 9 | 18 | 58 | 27 | 34 | 13 | 12 |
| hh_s2_t03 | sightings | 183 | 176 | 200 | 217 | 286 | 182 | 235 | 209 | 180 |
| hh_s2_t03 | looks (rooms opened) | 24 | 24 | 26 | 27 | 32 | 24 | 25 | 24 | 24 |
| hh_s32_t03 | surprising (A last-seen) | 8 | 10 | 4 | 10 | 15 | 9 | 4 | 5 | 5 |
| hh_s32_t03 | surprising (B 7-day) | 13 | 19 | 3 | 15 | 31 | 39 | 28 | 23 | 14 |
| hh_s32_t03 | sightings | 494 | 503 | 293 | 396 | 409 | 446 | 333 | 449 | 362 |
| hh_s32_t03 | looks (rooms opened) | 26 | 25 | 24 | 27 | 28 | 26 | 24 | 24 | 24 |
| hh_s48_t03 | surprising (A last-seen) | 16 | 12 | 15 | 3 | 23 | 22 | 11 | 10 | 10 |
| hh_s48_t03 | surprising (B 7-day) | 57 | 22 | 24 | 2 | 46 | 42 | 40 | 34 | 23 |
| hh_s48_t03 | sightings | 219 | 239 | 323 | 241 | 368 | 342 | 399 | 329 | 406 |
| hh_s48_t03 | looks (rooms opened) | 27 | 26 | 26 | 25 | 34 | 32 | 35 | 35 | 36 |

### How high the count runs in each window


Definition A: last-seen room:

| household | mean/day d1-13 | mean/day d14-23 | mean/day d24-31 | mean/day d32-41 | mean/day d42-49 | max 3-day sum d1-13 (on day) | max 3-day sum d14-23 (on day) | max 3-day sum d24-31 (on day) | max 3-day sum d32-41 (on day) | max 3-day sum d42-49 (on day) |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 15.0 | 9.9 | 14.9 | 10.8 | 21.1 | 67 (d6) | 55 (d14) | 59 (d25) | 63 (d32) | 70 (d46) |
| hh_s32_t03 | 7.7 | 6.0 | 7.8 | 7.5 | 9.5 | 30 (d4) | 30 (d14) | 24 (d26) | 34 (d33) | 41 (d44) |
| hh_s48_t03 | 13.7 | 13.0 | 13.0 | 13.4 | 19.8 | 67 (d9) | 56 (d16) | 57 (d26) | 56 (d34) | 72 (d44) |

Definition B: commonest room, past 7 days:

| household | mean/day d1-13 | mean/day d14-23 | mean/day d24-31 | mean/day d32-41 | mean/day d42-49 | max 3-day sum d1-13 (on day) | max 3-day sum d14-23 (on day) | max 3-day sum d24-31 (on day) | max 3-day sum d32-41 (on day) | max 3-day sum d42-49 (on day) |
|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 15.2 | 24.9 | 22.9 | 23.4 | 32.2 | 73 (d7) | 132 (d16) | 133 (d25) | 119 (d34) | 138 (d43) |
| hh_s32_t03 | 9.4 | 19.4 | 20.8 | 19.1 | 22.9 | 39 (d4) | 90 (d17) | 108 (d26) | 98 (d34) | 137 (d44) |
| hh_s48_t03 | 19.2 | 34.4 | 32.8 | 30.8 | 29.2 | 80 (d10) | 170 (d16) | 141 (d26) | 128 (d34) | 101 (d44) |

### Alarm days under the strict threshold, every day 1-49


Definition A: last-seen room:

| household | T | alarm days |
|---|---|---|
| hh_s2_t03 | 67 | 43, 45, 46 |
| hh_s32_t03 | 67 | - |
| hh_s48_t03 | 67 | 44 |

Definition B: commonest room, past 7 days:

| household | T | alarm days |
|---|---|---|
| hh_s2_t03 | 80 | 14, 15, 16, 17, 18, 25, 26, 32, 33, 34, 42, 43, 44, 45 |
| hh_s32_t03 | 80 | 16, 17, 18, 25, 26, 33, 34, 35, 42, 43, 44, 45 |
| hh_s48_t03 | 73 | 5, 9, 10, 14, 15, 16, 17, 18, 19, 24, 25, 26, 27, 28, 29, 30, 33, 34, 35, 36, 37, 38, 39, 40, 43, 44, 45, 46, 49 |

### Does the robot look into the rooms the sick resident's things go to? (first spell)


| household | movers | rooms the movers go to when sick (not their settled room) | looks into those rooms on day 14 / +1 / +2 | first day >= 14 the robot opened one |
|---|---|---|---|---|
| hh_s2_t03 | 8 | bedroom_1, kitchen, living | 11 / 10 / 10 | 14 |
| hh_s32_t03 | 8 | bedroom_1, entry, living | 2 / 8 / 5 | 14 |
| hh_s48_t03 | 6 | bedroom_1, kitchen, living | 11 / 11 / 12 | 14 |

## Notes on what makes the number easy or hard

Plain description of what in the data drives the numbers above. The figures quoted are from the tables in
this file (ten-household run unless said otherwise).

1. How much the robot sees. In the 8-questions-a-day run the robot opens about 8 to 19 rooms a day and records
   roughly 50 to 300 sightings a day (per-household means 71 to 153 on days 1-13). In the 24-questions-a-day run
   it is roughly 24 to 45 rooms and 180 to 530 sightings a day. A look writes down every object in the room, so
   the daily count moves with how many rooms were opened and which ones: one look into the dining room at
   a meal time adds up to nine surprising sightings at once (every plate, glass, mug and bottle that was
   last seen in the kitchen).

2. Settled days are not quiet. Under definition A the settled-window mean is 1.5 to 8.4 surprising
   sightings a day and the largest settled 3-day sums are 47 (hh_s2, days 3-5) and 42 (hh_s151, days
   4-6). Listing the surprising sightings on hh_s2 days 4-5 shows what they are: crockery and water bottles
   moving kitchen <-> dining at meals, and the residents' mugs, bottles and chargers moving between office,
   entry, bedroom and kitchen, each move seen at whatever time of day a question happened to fall. That is
   the ordinary routine, not noise in the sensor. The sick-window 3-day sums under A peak at 10 to 45, the
   same range as the settled peaks; in 6 of 10 households the settled maximum is at or above the sick
   maximum under A, and in 4 of 10 under B.

3. The threshold is set by the two loudest households. Leave-one-out with zero alarms allowed on days 1-13
   makes T the largest settled 3-day sum among the other nine, which is 47 for every household except the
   loud one itself (42). The loud households (hh_s2, hh_s151) are the ones that go over on their own days
   1-13 when held out. Settled peaks come early: under A the largest 3-day sum in days 1-7 exceeds the one
   in days 8-13 in 8 of 10 households (hh_s32 and hh_s123 are the exceptions; both are quiet throughout).
   SETUP says days 1-13, so no shorter window was used.

4. The change itself is small in sighting terms. The movers are 5 to 9 objects per household. Even if the
   robot saw every one of them in a new room on day 14, that adds at most 5 to 9 surprising sightings to a
   settled background of 1.5 to 8 a day. Day-14 counts under A are 0 to 24, against settled days that
   reach 22. The robot does look where the sick resident's things go: the first day on or after 14 on
   which it opens one of those rooms is day 14 in 9 of 10 households (day 15 in hh_s63), with 0 to 7 such
   looks on day 14.

5. The two definitions count a lasting move differently. A counts a move once (the next sighting in the
   new room is expected). B keeps counting the object as surprising until the new room is the commonest
   of the past seven days, so a lasting move gives a run of raised days (hh_s20 days 15-17: 26, 17, 12;
   hh_s93 days 15-17: 20, 21, 11). That is why B detects in 3 of 10 (all with delay 2, on the day-16
   window) and A in none, why B detects both spells in all three 50-day households (delays 0 to 2), and why
   B raises more return alarms.

6. The return is a change of the same size. Under both definitions the largest 3-day sum of the whole run
   is often on days 24-28: under A the return-window maximum exceeds the sick-window maximum in 9 of 10
   households (hh_s109 is the exception); under B the return raises alarms in 3 of 10 households (and in all three 50-day
   households, after both spells) while the sickness raises them in 3 of 10.

7. The 50-day run. Thresholds there come from two households each, and hh_s48's own settled days are
   louder than the other two, so it gets 3 alarm days on days 1-13 (6.9 a month) under B. Under A no spell
   is detected in any of the three; under B both spells are detected in all three.

8. The mean and standard deviation of the delay are over detected households only (0, 1 or 3 of 10), so
   they describe few households; the "none" count beside them is the larger part of the result.

9. The strict and loose threshold rules differ little: T drops from 47 to 40-46 and A gains one detection
   (hh_s109, delay 1, at T=42). With only 13 calibration days, "at most one false alarm per month" cannot
   be met by anything other than zero alarms, so the strict rule is the one SETUP's words describe.

