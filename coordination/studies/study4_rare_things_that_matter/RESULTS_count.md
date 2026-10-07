# Study 4, rare things that matter: the count

Produced by `rare_moves.py` in this directory. Definitions are in the script's docstring and in SETUP.md. Two levels are reported throughout: **place** (receptacle id, as SETUP says 'place changes') and **room** (what first-guess-right is scored at; a move between two spots in the same room is not a room-level move). Moves to or from ON_PERSON / OUT_OF_HOUSE count as moves at both levels (room = 'beyond reach').

## Summary

| wave | level | households | asked-about objects | objects with 0 moves | objects with 1-3 moves | questions asked | rare-move questions | rare-move questions in the full bank | all-move questions | other questions |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| overnight_wave | place | 10 | 145 | 15 | 1 | 2480 | 1 | 2 | 1459 | 1021 |
| overnight_wave | room | 10 | 145 | 46 | 8 | 2480 | 6 | 18 | 1046 | 1434 |
| wave_the_second_illness | place | 3 | 46 | 5 | 0 | 3528 | 0 | 0 | 1909 | 1619 |
| wave_the_second_illness | room | 3 | 46 | 14 | 2 | 3528 | 1 | 1 | 1338 | 2190 |

The rare-move slice (questions asked within 24 h after a move of an object with at most 3 moves) holds 1 question at place level and 6 at room level in the ten-home run, and 0 / 1 in the 50-day run, so no difference between methods is measurable on it: the paired 2 SE against last-seen is undefined where only one household has a question in the slice, and 40 to 63 points where five do (ten-home run, room level; section 3(a) of each wave). The full bank (24 questions a day) holds 18 such questions at most. Nearly every rare mover never moves at all (towels at place level; towels, razors, books and some glasses, mugs and notebooks at room level). Of the eight room-level rare movers in the ten-home run that do move, six move exactly twice, out on day 12-14 and back on day 24-31 (the bank's sick block is days 14-23); the other two, and both in the 50-day run, change room and change back within one day. Every question falls in exactly one of the all-move / other slices; none is unclassified. The 'pairs' column counts consecutive move pairs A->B, B->A on one calendar day, so a run A->B->A->B on one day counts two pairs.

# overnight_wave (ten homes, 31 days, 8 questions a day)

cells: `results/self_improve/overnight_wave/cells`; banks: `results/self_improve/varied_homes/ten_homes/banks`


## 1 (place level). Moves per asked-about object

A move is a change of place; rare mover = at most 3 moves. `nq` = questions the cells asked about the object. `pairs` = change-and-change-back within one calendar day (counted as two moves).


### hh_s109_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_felix | 10 | 3 | 0 | 7 | 1 | 5 |  |
| book_yuki | 9 | 2 | 0 | 6 | 3 | 8 |  |
| charger_felix | 359 | 283 | 0 | 32 | 30 | 92 |  |
| charger_yuki | 82 | 4 | 44 | 26 | 2 | 10 |  |
| glass_felix | 139 | 34 | 0 | 31 | 7 | 29 |  |
| glass_yuki | 68 | 9 | 0 | 28 | 6 | 19 |  |
| glasses_felix | 371 | 269 | 0 | 32 | 19 | 86 |  |
| mug_felix | 365 | 190 | 0 | 32 | 31 | 89 |  |
| mug_yuki | 70 | 10 | 0 | 26 | 9 | 20 |  |
| notebook_felix | 32 | 17 | 0 | 14 | 32 | 87 |  |
| notebook_yuki | 50 | 5 | 44 | 22 | 1 | 1 |  |
| towel_felix | 0 | 0 | 0 | 0 | 27 | 85 | yes |
| towel_yuki | 18 | 5 | 0 | 13 | 30 | 81 |  |
| water_bottle_felix | 377 | 210 | 0 | 32 | 44 | 114 |  |
| water_bottle_yuki | 111 | 0 | 44 | 23 | 6 | 18 |  |

histogram of moves per object: 0: 1, 4-10: 2, 11-30: 1, 31-100: 5, 101-300: 2, >300: 4

rare movers (1 of 15): towel_felix

### hh_s123_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_sam | 49 | 11 | 0 | 22 | 9 | 22 |  |
| charger_priya | 67 | 12 | 44 | 23 | 5 | 22 |  |
| glass_priya | 65 | 11 | 0 | 26 | 10 | 52 |  |
| glass_sam | 130 | 46 | 0 | 32 | 27 | 88 |  |
| mug_priya | 38 | 7 | 0 | 15 | 9 | 26 |  |
| mug_sam | 164 | 58 | 0 | 31 | 23 | 84 |  |
| notebook_priya | 48 | 8 | 44 | 22 | 0 | 4 |  |
| razor_priya | 41 | 14 | 0 | 26 | 20 | 21 |  |
| razor_sam | 41 | 13 | 0 | 27 | 4 | 16 |  |
| towel_priya | 8 | 1 | 0 | 7 | 60 | 192 |  |
| towel_sam | 0 | 0 | 0 | 0 | 68 | 176 | yes |
| water_bottle_priya | 78 | 7 | 15 | 25 | 13 | 41 |  |

histogram of moves per object: 0: 1, 4-10: 1, 31-100: 8, 101-300: 2

rare movers (1 of 12): towel_sam

### hh_s151_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_dana | 15 | 1 | 0 | 11 | 6 | 25 |  |
| charger_dana | 78 | 8 | 44 | 28 | 6 | 25 |  |
| glass_dana | 70 | 13 | 0 | 30 | 20 | 44 |  |
| glass_felix | 127 | 32 | 0 | 32 | 28 | 80 |  |
| glasses_felix | 8 | 1 | 0 | 5 | 0 | 3 |  |
| medication_dana | 15 | 4 | 12 | 9 | 3 | 7 |  |
| mug_dana | 41 | 4 | 0 | 17 | 5 | 20 |  |
| mug_felix | 198 | 90 | 0 | 32 | 30 | 99 |  |
| razor_dana | 47 | 15 | 0 | 29 | 16 | 18 |  |
| towel_dana | 13 | 4 | 0 | 9 | 66 | 179 |  |
| towel_felix | 0 | 0 | 0 | 0 | 45 | 176 | yes |
| water_bottle_dana | 109 | 2 | 44 | 25 | 7 | 29 |  |
| water_bottle_felix | 147 | 2 | 64 | 32 | 16 | 39 |  |

histogram of moves per object: 0: 1, 4-10: 1, 11-30: 3, 31-100: 4, 101-300: 4

rare movers (1 of 13): towel_felix

### hh_s19_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_marco | 9 | 1 | 0 | 6 | 4 | 12 |  |
| book_omar | 8 | 1 | 0 | 5 | 1 | 2 |  |
| charger_marco | 38 | 14 | 0 | 20 | 6 | 23 |  |
| glass_marco | 76 | 19 | 0 | 28 | 11 | 33 |  |
| glass_omar | 139 | 41 | 0 | 32 | 14 | 47 |  |
| mug_marco | 78 | 16 | 0 | 27 | 13 | 29 |  |
| mug_omar | 403 | 198 | 0 | 32 | 39 | 140 |  |
| notebook_marco | 57 | 10 | 44 | 23 | 2 | 5 |  |
| notebook_omar | 67 | 33 | 0 | 21 | 43 | 125 |  |
| towel_marco | 32 | 16 | 0 | 16 | 29 | 79 |  |
| towel_omar | 0 | 0 | 0 | 0 | 21 | 72 | yes |
| water_bottle_marco | 130 | 11 | 46 | 25 | 9 | 32 |  |
| water_bottle_omar | 379 | 217 | 0 | 32 | 56 | 145 |  |

histogram of moves per object: 0: 1, 4-10: 2, 31-100: 6, 101-300: 2, >300: 2

rare movers (1 of 13): towel_omar

### hh_s20_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_aisha | 11 | 5 | 0 | 6 | 2 | 8 |  |
| book_hana | 11 | 1 | 0 | 7 | 8 | 19 |  |
| charger_aisha | 108 | 7 | 64 | 32 | 1 | 11 |  |
| charger_hana | 253 | 211 | 0 | 24 | 25 | 83 |  |
| glass_aisha | 80 | 9 | 0 | 32 | 12 | 30 |  |
| glass_hana | 152 | 58 | 0 | 32 | 16 | 43 |  |
| glasses_hana | 248 | 183 | 0 | 28 | 23 | 76 |  |
| medication_hana | 61 | 25 | 44 | 31 | 0 | 3 |  |
| mug_aisha | 30 | 0 | 0 | 12 | 3 | 4 |  |
| mug_hana | 289 | 151 | 0 | 31 | 24 | 105 |  |
| razor_aisha | 38 | 12 | 0 | 24 | 11 | 11 |  |
| tablet_aisha | 14 | 3 | 0 | 9 | 1 | 4 |  |
| towel_aisha | 12 | 4 | 0 | 8 | 26 | 110 |  |
| towel_hana | 0 | 0 | 0 | 0 | 53 | 121 | yes |
| water_bottle_aisha | 147 | 0 | 64 | 32 | 8 | 24 |  |
| water_bottle_hana | 260 | 150 | 0 | 23 | 35 | 92 |  |

histogram of moves per object: 0: 1, 11-30: 5, 31-100: 3, 101-300: 7

rare movers (1 of 16): towel_hana

### hh_s2_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_tomas | 14 | 3 | 0 | 10 | 6 | 21 |  |
| charger_tomas | 251 | 199 | 0 | 24 | 27 | 64 |  |
| glass_ines | 128 | 32 | 0 | 31 | 17 | 49 |  |
| glass_tomas | 93 | 18 | 0 | 26 | 13 | 35 |  |
| mug_ines | 82 | 5 | 0 | 30 | 10 | 30 |  |
| mug_tomas | 274 | 127 | 0 | 28 | 26 | 100 |  |
| notebook_tomas | 46 | 24 | 0 | 14 | 14 | 69 |  |
| towel_ines | 0 | 0 | 0 | 0 | 47 | 128 | yes |
| towel_tomas | 0 | 0 | 0 | 0 | 53 | 148 | yes |
| water_bottle_ines | 124 | 1 | 44 | 32 | 10 | 20 |  |
| water_bottle_tomas | 308 | 145 | 26 | 27 | 25 | 80 |  |

histogram of moves per object: 0: 2, 11-30: 1, 31-100: 3, 101-300: 4, >300: 1

rare movers (2 of 11): towel_ines, towel_tomas

### hh_s32_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_aisha | 14 | 3 | 0 | 11 | 2 | 9 |  |
| book_elena | 22 | 8 | 0 | 14 | 3 | 9 |  |
| book_leo | 9 | 3 | 0 | 6 | 4 | 11 |  |
| charger_aisha | 111 | 2 | 64 | 32 | 1 | 7 |  |
| charger_leo | 240 | 181 | 0 | 25 | 18 | 56 |  |
| glass_aisha | 91 | 18 | 0 | 32 | 8 | 17 |  |
| glass_elena | 153 | 46 | 0 | 32 | 12 | 44 |  |
| glass_leo | 119 | 36 | 0 | 29 | 14 | 28 |  |
| mug_aisha | 45 | 3 | 0 | 16 | 0 | 2 |  |
| mug_elena | 93 | 5 | 0 | 32 | 7 | 29 |  |
| mug_leo | 267 | 127 | 0 | 32 | 22 | 73 |  |
| notebook_elena | 62 | 26 | 0 | 32 | 6 | 15 |  |
| notebook_leo | 38 | 19 | 0 | 13 | 18 | 60 |  |
| tablet_aisha | 30 | 12 | 0 | 16 | 0 | 8 |  |
| tablet_leo | 40 | 9 | 0 | 24 | 3 | 13 |  |
| towel_aisha | 16 | 4 | 0 | 12 | 38 | 87 |  |
| towel_elena | 0 | 0 | 0 | 0 | 36 | 94 | yes |
| towel_leo | 0 | 0 | 0 | 0 | 29 | 93 | yes |
| water_bottle_aisha | 149 | 7 | 65 | 32 | 5 | 17 |  |
| water_bottle_leo | 232 | 104 | 0 | 27 | 22 | 72 |  |

histogram of moves per object: 0: 2, 4-10: 1, 11-30: 4, 31-100: 6, 101-300: 7

rare movers (2 of 20): towel_elena, towel_leo

### hh_s48_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_marco | 46 | 7 | 0 | 26 | 11 | 28 |  |
| book_priya | 4 | 1 | 0 | 3 | 3 | 5 |  |
| charger_marco | 57 | 10 | 44 | 28 | 6 | 14 |  |
| charger_priya | 109 | 3 | 64 | 32 | 0 | 15 |  |
| glass_marco | 94 | 29 | 0 | 27 | 20 | 71 |  |
| glass_priya | 81 | 5 | 0 | 32 | 16 | 35 |  |
| mug_marco | 125 | 43 | 0 | 31 | 33 | 118 |  |
| mug_priya | 28 | 1 | 0 | 12 | 1 | 5 |  |
| notebook_priya | 68 | 13 | 64 | 32 | 0 | 1 |  |
| razor_priya | 56 | 14 | 0 | 31 | 20 | 20 |  |
| tablet_priya | 19 | 7 | 0 | 11 | 4 | 7 |  |
| towel_marco | 0 | 0 | 0 | 0 | 63 | 181 | yes |
| towel_priya | 36 | 13 | 0 | 19 | 52 | 167 |  |
| water_bottle_marco | 119 | 1 | 44 | 27 | 14 | 42 |  |
| water_bottle_priya | 151 | 0 | 64 | 32 | 5 | 35 |  |

histogram of moves per object: 0: 1, 4-10: 1, 11-30: 2, 31-100: 7, 101-300: 4

rare movers (1 of 15): towel_marco

### hh_s63_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_dana | 24 | 8 | 0 | 15 | 6 | 19 |  |
| book_priya | 3 | 1 | 0 | 2 | 1 | 2 | yes |
| charger_dana | 51 | 15 | 44 | 26 | 5 | 19 |  |
| glass_dana | 140 | 45 | 0 | 31 | 18 | 61 |  |
| glass_priya | 136 | 38 | 0 | 32 | 22 | 67 |  |
| glasses_priya | 50 | 11 | 0 | 30 | 11 | 27 |  |
| mug_dana | 172 | 59 | 0 | 30 | 22 | 93 |  |
| mug_priya | 90 | 6 | 0 | 32 | 24 | 51 |  |
| notebook_priya | 56 | 14 | 0 | 32 | 7 | 29 |  |
| razor_dana | 52 | 17 | 0 | 32 | 8 | 14 |  |
| tablet_dana | 0 | 0 | 0 | 0 | 3 | 7 | yes |
| tablet_priya | 53 | 9 | 0 | 30 | 14 | 38 |  |
| towel_dana | 0 | 0 | 0 | 0 | 32 | 116 | yes |
| towel_priya | 0 | 0 | 0 | 0 | 56 | 133 | yes |
| water_bottle_dana | 126 | 6 | 44 | 29 | 10 | 37 |  |
| water_bottle_priya | 79 | 10 | 0 | 32 | 9 | 31 |  |

histogram of moves per object: 0: 3, 3: 1, 11-30: 1, 31-100: 7, 101-300: 4

rare movers (4 of 16): book_priya, tablet_dana, towel_dana, towel_priya

### hh_s93_t03  (n_days 32, 248 questions asked, 743 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_ines | 8 | 3 | 0 | 5 | 9 | 19 |  |
| charger_ines | 56 | 22 | 0 | 20 | 37 | 90 |  |
| glass_ines | 80 | 18 | 0 | 24 | 22 | 46 |  |
| glass_kwame | 51 | 3 | 0 | 22 | 4 | 14 |  |
| glasses_ines | 196 | 131 | 0 | 25 | 14 | 88 |  |
| medication_ines | 41 | 9 | 0 | 23 | 6 | 18 |  |
| mug_ines | 241 | 131 | 0 | 30 | 32 | 129 |  |
| mug_kwame | 77 | 10 | 0 | 32 | 7 | 18 |  |
| razor_ines | 48 | 12 | 0 | 29 | 18 | 18 |  |
| razor_kwame | 44 | 15 | 0 | 25 | 3 | 14 |  |
| towel_ines | 0 | 0 | 0 | 0 | 27 | 82 | yes |
| towel_kwame | 0 | 0 | 0 | 0 | 37 | 100 | yes |
| water_bottle_ines | 226 | 109 | 0 | 24 | 30 | 102 |  |
| water_bottle_kwame | 72 | 14 | 64 | 32 | 2 | 5 |  |

histogram of moves per object: 0: 2, 4-10: 1, 31-100: 8, 101-300: 3

rare movers (2 of 14): towel_ines, towel_kwame

### rare movers that move at all (place level): when, and the questions that follow

| household | object | moves (day: from->to) | asked questions within 24 h | bank questions within 24 h |
|---|---|---|---:|---:|
| hh_s63_t03 | book_priya | d5: nightstand_b1->bed_b1; d5: bed_b1->nightstand_b1; d13: nightstand_b1->bed_b1 | 1 | 2 |

### odd things (place level)

- move on every day or all but one (42): hh_s109_t03/charger_felix (359 moves), hh_s109_t03/glass_felix (139 moves), hh_s109_t03/glasses_felix (371 moves), hh_s109_t03/mug_felix (365 moves), hh_s109_t03/water_bottle_felix (377 moves), hh_s123_t03/glass_sam (130 moves), hh_s123_t03/mug_sam (164 moves), hh_s151_t03/glass_felix (127 moves), hh_s151_t03/mug_felix (198 moves), hh_s151_t03/water_bottle_felix (147 moves), hh_s19_t03/glass_omar (139 moves), hh_s19_t03/mug_omar (403 moves), hh_s19_t03/water_bottle_omar (379 moves), hh_s20_t03/charger_aisha (108 moves), hh_s20_t03/glass_aisha (80 moves), hh_s20_t03/glass_hana (152 moves), hh_s20_t03/medication_hana (61 moves), hh_s20_t03/mug_hana (289 moves), hh_s20_t03/water_bottle_aisha (147 moves), hh_s2_t03/glass_ines (128 moves), hh_s2_t03/water_bottle_ines (124 moves), hh_s32_t03/charger_aisha (111 moves), hh_s32_t03/glass_aisha (91 moves), hh_s32_t03/glass_elena (153 moves), hh_s32_t03/mug_elena (93 moves), hh_s32_t03/mug_leo (267 moves), hh_s32_t03/notebook_elena (62 moves), hh_s32_t03/water_bottle_aisha (149 moves), hh_s48_t03/charger_priya (109 moves), hh_s48_t03/glass_priya (81 moves), hh_s48_t03/mug_marco (125 moves), hh_s48_t03/notebook_priya (68 moves), hh_s48_t03/razor_priya (56 moves), hh_s48_t03/water_bottle_priya (151 moves), hh_s63_t03/glass_dana (140 moves), hh_s63_t03/glass_priya (136 moves), hh_s63_t03/mug_priya (90 moves), hh_s63_t03/notebook_priya (56 moves), hh_s63_t03/razor_dana (52 moves), hh_s63_t03/water_bottle_priya (79 moves), hh_s93_t03/mug_kwame (77 moves), hh_s93_t03/water_bottle_kwame (72 moves)
- never move (15): hh_s109_t03/towel_felix (27 asked), hh_s123_t03/towel_sam (68 asked), hh_s151_t03/towel_felix (45 asked), hh_s19_t03/towel_omar (21 asked), hh_s20_t03/towel_hana (53 asked), hh_s2_t03/towel_ines (47 asked), hh_s2_t03/towel_tomas (53 asked), hh_s32_t03/towel_elena (36 asked), hh_s32_t03/towel_leo (29 asked), hh_s48_t03/towel_marco (63 asked), hh_s63_t03/tablet_dana (3 asked), hh_s63_t03/towel_dana (32 asked), hh_s63_t03/towel_priya (56 asked), hh_s93_t03/towel_ines (27 asked), hh_s93_t03/towel_kwame (37 asked)
- in the bank's questions but never asked by the cells (7): hh_s123_t03/notebook_priya (4 in bank), hh_s151_t03/glasses_felix (3 in bank), hh_s20_t03/medication_hana (3 in bank), hh_s32_t03/mug_aisha (2 in bank), hh_s32_t03/tablet_aisha (8 in bank), hh_s48_t03/charger_priya (15 in bank), hh_s48_t03/notebook_priya (1 in bank)

### all households, histogram of moves per object (place level)

| moves | objects |
|---|---:|
| 0 | 15 |
| 1 | 0 |
| 2 | 0 |
| 3 | 1 |
| 4-10 | 9 |
| 11-30 | 17 |
| 31-100 | 57 |
| 101-300 | 39 |
| >300 | 7 |

## 2 (place level). Questions within 24 h after a move

| household | questions | rare-move questions | rare movers asked about | rare-move questions in the full bank | all-move questions | other (no move of the object in the prior 24 h) | about never-moving objects |
|---|---:|---:|---:|---:|---:|---:|---:|
| hh_s109_t03 | 248 | 0 | 0 | 0 | 183 | 65 | 27 |
| hh_s123_t03 | 248 | 0 | 0 | 0 | 113 | 135 | 68 |
| hh_s151_t03 | 248 | 0 | 0 | 0 | 133 | 115 | 45 |
| hh_s19_t03 | 248 | 0 | 0 | 0 | 190 | 58 | 21 |
| hh_s20_t03 | 248 | 0 | 0 | 0 | 150 | 98 | 53 |
| hh_s2_t03 | 248 | 0 | 0 | 0 | 123 | 125 | 100 |
| hh_s32_t03 | 248 | 0 | 0 | 0 | 136 | 112 | 65 |
| hh_s48_t03 | 248 | 0 | 0 | 0 | 144 | 104 | 63 |
| hh_s63_t03 | 248 | 1 | 1 | 2 | 143 | 105 | 91 |
| hh_s93_t03 | 248 | 0 | 0 | 0 | 144 | 104 | 64 |
| **total** | 2480 | 1 | | 2 | 1459 | 1021 | 597 |

The rare-move questions are a subset of the all-move questions. A question is in exactly one of: all-move, other. 'In the full bank' counts all the bank's questions (24 a day), not only those the cells asked.

How the asked-question count in the rare slice depends on the rare threshold (place level, all households):

| at most this many moves | asked questions within 24 h after a move of such an object |
|---:|---:|
| 3 | 1 |
| 5 | 2 |
| 10 | 24 |
| 20 | 81 |
| 30 | 91 |

## 3 (place level). First guess right (found_at_step == 1), per cent

`most_frequent_offline` is an offline estimate computed here from the bank: for each question, the room the object was truly in most often at the times of the earlier asked questions about it (ties by most recent); no guess before the first question about an object. It uses true rooms, which no robot had; the cells used what they saw.


### (a) rare-move questions

| method | hh_s109_t03 | hh_s123_t03 | hh_s151_t03 | hh_s19_t03 | hh_s20_t03 | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | hh_s63_t03 | hh_s93_t03 | pooled | pooled n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| a_small_working_memory_and_an_archive | – | – | – | – | – | – | – | – | 0.0 | – | 0.0 | 1 |
| claim_store_told_if_it_was_right | – | – | – | – | – | – | – | – | 0.0 | – | 0.0 | 1 |
| incremental_edits | – | – | – | – | – | – | – | – | 100.0 | – | 100.0 | 1 |
| last_seen_no_model | – | – | – | – | – | – | – | – | 100.0 | – | 100.0 | 1 |
| prior_only_no_notes | – | – | – | – | – | – | – | – | 0.0 | – | 0.0 | 1 |
| the_log_and_notes_about_the_routine | – | – | – | – | – | – | – | – | 100.0 | – | 100.0 | 1 |
| wholesale_rewrite | – | – | – | – | – | – | – | – | – | – | – | 0 |
| most_frequent_offline | – | – | – | – | – | – | – | – | 0.0 | – | 0.0 | 1 |

Paired per-household difference against `last_seen_no_model` (points; households with the method present and a non-empty slice):

| method | n households | mean | SE | 2 SE | per household |
|---|---:|---:|---:|---:|---|
| a_small_working_memory_and_an_archive | 1 | -100.0 | – | – | s63:-100 |
| claim_store_told_if_it_was_right | 1 | -100.0 | – | – | s63:-100 |
| incremental_edits | 1 | +0.0 | – | – | s63:+0 |
| prior_only_no_notes | 1 | -100.0 | – | – | s63:-100 |
| the_log_and_notes_about_the_routine | 1 | +0.0 | – | – | s63:+0 |
| wholesale_rewrite | 0 | – | – | – |  |
| most_frequent_offline | 1 | -100.0 | – | – | s63:-100 |

### (b) all-move questions

| method | hh_s109_t03 | hh_s123_t03 | hh_s151_t03 | hh_s19_t03 | hh_s20_t03 | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | hh_s63_t03 | hh_s93_t03 | pooled | pooled n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| a_small_working_memory_and_an_archive | 73.8 | 57.5 | 37.6 | 80.5 | 36.7 | 75.6 | 55.9 | 47.9 | 63.6 | 33.3 | 57.2 | 1459 |
| claim_store_told_if_it_was_right | 73.8 | 73.5 | 39.8 | 81.1 | 22.7 | 54.5 | 73.5 | 65.3 | 74.8 | 56.9 | 62.3 | 1459 |
| incremental_edits | 71.6 | 73.5 | 58.6 | 85.3 | 40.7 | 60.2 | 69.1 | 61.1 | 59.4 | 56.9 | 64.3 | 1459 |
| last_seen_no_model | 72.7 | 70.8 | 56.4 | 73.2 | 66.7 | 71.5 | 77.2 | 68.1 | 87.4 | 78.5 | 72.4 | 1459 |
| prior_only_no_notes | 21.3 | 58.4 | 29.3 | 52.6 | 16.0 | 13.0 | 27.9 | 41.0 | 7.7 | 29.9 | 29.8 | 1459 |
| the_log_and_notes_about_the_routine | 79.2 | 75.2 | 66.9 | 82.1 | 77.3 | 82.1 | 83.8 | 73.6 | 65.7 | 80.6 | 76.9 | 1459 |
| wholesale_rewrite | – | – | – | – | – | 48.8 | – | – | – | – | 48.8 | 123 |
| most_frequent_offline | 78.1 | 78.8 | 78.9 | 75.8 | 76.0 | 79.7 | 76.5 | 72.2 | 81.1 | 76.4 | 77.2 | 1459 |

Paired per-household difference against `last_seen_no_model` (points; households with the method present and a non-empty slice):

| method | n households | mean | SE | 2 SE | per household |
|---|---:|---:|---:|---:|---|
| a_small_working_memory_and_an_archive | 10 | -16.0 | 5.2 | 10.3 | s109:+1 s123:-13 s151:-19 s19:+7 s20:-30 s2:+4 s32:-21 s48:-20 s63:-24 s93:-45 |
| claim_store_told_if_it_was_right | 10 | -10.7 | 4.8 | 9.6 | s109:+1 s123:+3 s151:-17 s19:+8 s20:-44 s2:-17 s32:-4 s48:-3 s63:-13 s93:-22 |
| incremental_edits | 10 | -8.6 | 4.2 | 8.4 | s109:-1 s123:+3 s151:+2 s19:+12 s20:-26 s2:-11 s32:-8 s48:-7 s63:-28 s93:-22 |
| prior_only_no_notes | 10 | -42.5 | 6.4 | 12.9 | s109:-51 s123:-12 s151:-27 s19:-21 s20:-51 s2:-59 s32:-49 s48:-27 s63:-80 s93:-49 |
| the_log_and_notes_about_the_routine | 10 | +4.4 | 3.0 | 6.1 | s109:+7 s123:+4 s151:+11 s19:+9 s20:+11 s2:+11 s32:+7 s48:+6 s63:-22 s93:+2 |
| wholesale_rewrite | 1 | -22.8 | – | – | s2:-23 |
| most_frequent_offline | 10 | +5.1 | 2.5 | 5.0 | s109:+5 s123:+8 s151:+23 s19:+3 s20:+9 s2:+8 s32:-1 s48:+4 s63:-6 s93:-2 |

### (c) all other questions

| method | hh_s109_t03 | hh_s123_t03 | hh_s151_t03 | hh_s19_t03 | hh_s20_t03 | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | hh_s63_t03 | hh_s93_t03 | pooled | pooled n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| a_small_working_memory_and_an_archive | 89.2 | 99.3 | 93.0 | 82.8 | 89.8 | 90.4 | 91.1 | 98.1 | 86.7 | 79.8 | 90.7 | 1021 |
| claim_store_told_if_it_was_right | 95.4 | 98.5 | 93.0 | 93.1 | 92.9 | 96.8 | 97.3 | 96.2 | 98.1 | 93.3 | 95.7 | 1021 |
| incremental_edits | 93.8 | 100.0 | 96.5 | 96.6 | 90.8 | 98.4 | 92.0 | 94.2 | 95.2 | 92.3 | 95.2 | 1021 |
| last_seen_no_model | 95.4 | 97.0 | 94.8 | 94.8 | 93.9 | 94.4 | 93.8 | 98.1 | 98.1 | 99.0 | 96.0 | 1021 |
| prior_only_no_notes | 95.4 | 94.1 | 87.8 | 84.5 | 87.8 | 88.8 | 92.0 | 83.7 | 86.7 | 72.1 | 87.4 | 1021 |
| the_log_and_notes_about_the_routine | 95.4 | 99.3 | 97.4 | 100.0 | 98.0 | 98.4 | 100.0 | 99.0 | 94.3 | 98.1 | 98.0 | 1021 |
| wholesale_rewrite | – | – | – | – | – | 83.2 | – | – | – | – | 83.2 | 125 |
| most_frequent_offline | 90.8 | 94.1 | 91.3 | 82.8 | 83.7 | 89.6 | 87.5 | 91.3 | 90.5 | 79.8 | 88.5 | 1021 |

Paired per-household difference against `last_seen_no_model` (points; households with the method present and a non-empty slice):

| method | n households | mean | SE | 2 SE | per household |
|---|---:|---:|---:|---:|---|
| a_small_working_memory_and_an_archive | 10 | -5.9 | 2.1 | 4.1 | s109:-6 s123:+2 s151:-2 s19:-12 s20:-4 s2:-4 s32:-3 s48:+0 s63:-11 s93:-19 |
| claim_store_told_if_it_was_right | 10 | -0.5 | 0.8 | 1.7 | s109:+0 s123:+1 s151:-2 s19:-2 s20:-1 s2:+2 s32:+4 s48:-2 s63:+0 s93:-6 |
| incremental_edits | 10 | -0.9 | 1.1 | 2.2 | s109:-2 s123:+3 s151:+2 s19:+2 s20:-3 s2:+4 s32:-2 s48:-4 s63:-3 s93:-7 |
| prior_only_no_notes | 10 | -8.7 | 2.5 | 4.9 | s109:+0 s123:-3 s151:-7 s19:-10 s20:-6 s2:-6 s32:-2 s48:-14 s63:-11 s93:-27 |
| the_log_and_notes_about_the_routine | 10 | +2.1 | 1.0 | 1.9 | s109:+0 s123:+2 s151:+3 s19:+5 s20:+4 s2:+4 s32:+6 s48:+1 s63:-4 s93:-1 |
| wholesale_rewrite | 1 | -11.2 | – | – | s2:-11 |
| most_frequent_offline | 10 | -7.8 | 1.6 | 3.1 | s109:-5 s123:-3 s151:-3 s19:-12 s20:-10 s2:-5 s32:-6 s48:-7 s63:-8 s93:-19 |

## 4 (place level). Rare-move questions per household and the detectable gap

| household | rare-move questions |
|---|---:|
| hh_s109_t03 | 0 |
| hh_s123_t03 | 0 |
| hh_s151_t03 | 0 |
| hh_s19_t03 | 0 |
| hh_s20_t03 | 0 |
| hh_s2_t03 | 0 |
| hh_s32_t03 | 0 |
| hh_s48_t03 | 0 |
| hh_s63_t03 | 1 |
| hh_s93_t03 | 0 |

Best method on the rare-move slice by pooled first guess right (ties all listed): `incremental_edits` (100.0%). Paired against `last_seen_no_model` over 1 households with a non-empty slice: mean +0.0, SE –, 2 SE –. (The paired table under 3(a) has every method.)

Best method on the rare-move slice by pooled first guess right (ties all listed): `the_log_and_notes_about_the_routine` (100.0%). Paired against `last_seen_no_model` over 1 households with a non-empty slice: mean +0.0, SE –, 2 SE –. (The paired table under 3(a) has every method.)

## 1 (room level). Moves per asked-about object

A move is a change of room; rare mover = at most 3 moves. `nq` = questions the cells asked about the object. `pairs` = change-and-change-back within one calendar day (counted as two moves).


### hh_s109_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_felix | 0 | 0 | 0 | 0 | 1 | 5 | yes |
| book_yuki | 2 | 0 | 0 | 2 | 3 | 8 | yes |
| charger_felix | 359 | 327 | 0 | 32 | 30 | 92 |  |
| charger_yuki | 65 | 9 | 44 | 23 | 2 | 10 |  |
| glass_felix | 112 | 81 | 0 | 31 | 7 | 29 |  |
| glass_yuki | 43 | 19 | 0 | 23 | 6 | 19 |  |
| glasses_felix | 371 | 290 | 0 | 32 | 19 | 86 |  |
| mug_felix | 341 | 248 | 0 | 32 | 31 | 89 |  |
| mug_yuki | 48 | 23 | 0 | 25 | 9 | 20 |  |
| notebook_felix | 0 | 0 | 0 | 0 | 32 | 87 | yes |
| notebook_yuki | 47 | 20 | 44 | 22 | 1 | 1 |  |
| towel_felix | 0 | 0 | 0 | 0 | 27 | 85 | yes |
| towel_yuki | 0 | 0 | 0 | 0 | 30 | 81 | yes |
| water_bottle_felix | 352 | 283 | 0 | 32 | 44 | 114 |  |
| water_bottle_yuki | 96 | 6 | 44 | 23 | 6 | 18 |  |

histogram of moves per object: 0: 4, 2: 1, 31-100: 5, 101-300: 1, >300: 4

rare movers (5 of 15): book_felix, book_yuki, notebook_felix, towel_felix, towel_yuki

### hh_s123_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_sam | 39 | 17 | 0 | 22 | 9 | 22 |  |
| charger_priya | 59 | 17 | 44 | 23 | 5 | 22 |  |
| glass_priya | 2 | 0 | 0 | 2 | 10 | 52 | yes |
| glass_sam | 0 | 0 | 0 | 0 | 27 | 88 | yes |
| mug_priya | 20 | 7 | 0 | 13 | 9 | 26 |  |
| mug_sam | 112 | 82 | 0 | 30 | 23 | 84 |  |
| notebook_priya | 47 | 18 | 44 | 22 | 0 | 4 |  |
| razor_priya | 0 | 0 | 0 | 0 | 20 | 21 | yes |
| razor_sam | 0 | 0 | 0 | 0 | 4 | 16 | yes |
| towel_priya | 0 | 0 | 0 | 0 | 60 | 192 | yes |
| towel_sam | 0 | 0 | 0 | 0 | 68 | 176 | yes |
| water_bottle_priya | 27 | 3 | 14 | 11 | 13 | 41 |  |

histogram of moves per object: 0: 5, 2: 1, 11-30: 2, 31-100: 3, 101-300: 1

rare movers (6 of 12): glass_priya, glass_sam, razor_priya, razor_sam, towel_priya, towel_sam

### hh_s151_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_dana | 4 | 1 | 0 | 3 | 6 | 25 |  |
| charger_dana | 60 | 13 | 44 | 23 | 6 | 25 |  |
| glass_dana | 47 | 21 | 0 | 25 | 20 | 44 |  |
| glass_felix | 107 | 75 | 0 | 32 | 28 | 80 |  |
| glasses_felix | 8 | 3 | 0 | 5 | 0 | 3 |  |
| medication_dana | 13 | 5 | 12 | 7 | 3 | 7 |  |
| mug_dana | 30 | 15 | 0 | 15 | 5 | 20 |  |
| mug_felix | 179 | 131 | 0 | 32 | 30 | 99 |  |
| razor_dana | 0 | 0 | 0 | 0 | 16 | 18 | yes |
| towel_dana | 0 | 0 | 0 | 0 | 66 | 179 | yes |
| towel_felix | 0 | 0 | 0 | 0 | 45 | 176 | yes |
| water_bottle_dana | 95 | 2 | 44 | 23 | 7 | 29 |  |
| water_bottle_felix | 132 | 8 | 64 | 32 | 16 | 39 |  |

histogram of moves per object: 0: 3, 4-10: 2, 11-30: 2, 31-100: 3, 101-300: 3

rare movers (3 of 13): razor_dana, towel_dana, towel_felix

### hh_s19_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_marco | 4 | 1 | 0 | 3 | 4 | 12 |  |
| book_omar | 0 | 0 | 0 | 0 | 1 | 2 | yes |
| charger_marco | 36 | 17 | 0 | 19 | 6 | 23 |  |
| glass_marco | 2 | 0 | 0 | 2 | 11 | 33 | yes |
| glass_omar | 0 | 0 | 0 | 0 | 14 | 47 | yes |
| mug_marco | 28 | 15 | 0 | 13 | 13 | 29 |  |
| mug_omar | 336 | 304 | 0 | 32 | 39 | 140 |  |
| notebook_marco | 50 | 22 | 44 | 23 | 2 | 5 |  |
| notebook_omar | 22 | 11 | 0 | 11 | 43 | 125 |  |
| towel_marco | 0 | 0 | 0 | 0 | 29 | 79 | yes |
| towel_omar | 0 | 0 | 0 | 0 | 21 | 72 | yes |
| water_bottle_marco | 78 | 11 | 44 | 23 | 9 | 32 |  |
| water_bottle_omar | 282 | 250 | 0 | 32 | 56 | 145 |  |

histogram of moves per object: 0: 4, 2: 1, 4-10: 1, 11-30: 2, 31-100: 3, 101-300: 1, >300: 1

rare movers (5 of 13): book_omar, glass_marco, glass_omar, towel_marco, towel_omar

### hh_s20_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_aisha | 0 | 0 | 0 | 0 | 2 | 8 | yes |
| book_hana | 2 | 0 | 0 | 2 | 8 | 19 | yes |
| charger_aisha | 85 | 17 | 64 | 32 | 1 | 11 |  |
| charger_hana | 245 | 222 | 0 | 23 | 25 | 83 |  |
| glass_aisha | 62 | 30 | 0 | 32 | 12 | 30 |  |
| glass_hana | 128 | 96 | 0 | 32 | 16 | 43 |  |
| glasses_hana | 242 | 191 | 0 | 24 | 23 | 76 |  |
| medication_hana | 59 | 27 | 44 | 31 | 0 | 3 |  |
| mug_aisha | 20 | 10 | 0 | 10 | 3 | 4 |  |
| mug_hana | 267 | 196 | 0 | 30 | 24 | 105 |  |
| razor_aisha | 0 | 0 | 0 | 0 | 11 | 11 | yes |
| tablet_aisha | 14 | 3 | 0 | 9 | 1 | 4 |  |
| towel_aisha | 0 | 0 | 0 | 0 | 26 | 110 | yes |
| towel_hana | 0 | 0 | 0 | 0 | 53 | 121 | yes |
| water_bottle_aisha | 129 | 2 | 64 | 32 | 8 | 24 |  |
| water_bottle_hana | 244 | 189 | 0 | 23 | 35 | 92 |  |

histogram of moves per object: 0: 4, 2: 1, 11-30: 2, 31-100: 3, 101-300: 6

rare movers (5 of 16): book_aisha, book_hana, razor_aisha, towel_aisha, towel_hana

### hh_s2_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_tomas | 2 | 0 | 0 | 2 | 6 | 21 | yes |
| charger_tomas | 243 | 220 | 0 | 23 | 27 | 64 |  |
| glass_ines | 107 | 76 | 0 | 31 | 17 | 49 |  |
| glass_tomas | 71 | 47 | 0 | 23 | 13 | 35 |  |
| mug_ines | 58 | 28 | 0 | 30 | 10 | 30 |  |
| mug_tomas | 251 | 183 | 0 | 28 | 26 | 100 |  |
| notebook_tomas | 0 | 0 | 0 | 0 | 14 | 69 | yes |
| towel_ines | 0 | 0 | 0 | 0 | 47 | 128 | yes |
| towel_tomas | 0 | 0 | 0 | 0 | 53 | 148 | yes |
| water_bottle_ines | 107 | 11 | 44 | 32 | 10 | 20 |  |
| water_bottle_tomas | 278 | 186 | 26 | 23 | 25 | 80 |  |

histogram of moves per object: 0: 3, 2: 1, 31-100: 2, 101-300: 5

rare movers (4 of 11): book_tomas, notebook_tomas, towel_ines, towel_tomas

### hh_s32_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_aisha | 0 | 0 | 0 | 0 | 2 | 9 | yes |
| book_elena | 0 | 0 | 0 | 0 | 3 | 9 | yes |
| book_leo | 4 | 1 | 0 | 3 | 4 | 11 |  |
| charger_aisha | 86 | 10 | 64 | 32 | 1 | 7 |  |
| charger_leo | 234 | 211 | 0 | 23 | 18 | 56 |  |
| glass_aisha | 2 | 1 | 0 | 1 | 8 | 17 | yes |
| glass_elena | 0 | 0 | 0 | 0 | 12 | 44 | yes |
| glass_leo | 2 | 0 | 0 | 2 | 14 | 28 | yes |
| mug_aisha | 0 | 0 | 0 | 0 | 0 | 2 | yes |
| mug_elena | 0 | 0 | 0 | 0 | 7 | 29 | yes |
| mug_leo | 222 | 189 | 0 | 32 | 22 | 73 |  |
| notebook_elena | 62 | 30 | 0 | 32 | 6 | 15 |  |
| notebook_leo | 0 | 0 | 0 | 0 | 18 | 60 | yes |
| tablet_aisha | 28 | 12 | 0 | 16 | 0 | 8 |  |
| tablet_leo | 37 | 13 | 0 | 24 | 3 | 13 |  |
| towel_aisha | 0 | 0 | 0 | 0 | 38 | 87 | yes |
| towel_elena | 0 | 0 | 0 | 0 | 36 | 94 | yes |
| towel_leo | 0 | 0 | 0 | 0 | 29 | 93 | yes |
| water_bottle_aisha | 99 | 2 | 64 | 32 | 5 | 17 |  |
| water_bottle_leo | 165 | 140 | 0 | 23 | 22 | 72 |  |

histogram of moves per object: 0: 9, 2: 2, 4-10: 1, 11-30: 1, 31-100: 4, 101-300: 3

rare movers (11 of 20): book_aisha, book_elena, glass_aisha, glass_elena, glass_leo, mug_aisha, mug_elena, notebook_leo, towel_aisha, towel_elena, towel_leo

### hh_s48_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_marco | 28 | 10 | 0 | 17 | 11 | 28 |  |
| book_priya | 0 | 0 | 0 | 0 | 3 | 5 | yes |
| charger_marco | 49 | 17 | 44 | 23 | 6 | 14 |  |
| charger_priya | 89 | 15 | 64 | 32 | 0 | 15 |  |
| glass_marco | 69 | 45 | 0 | 23 | 20 | 71 |  |
| glass_priya | 62 | 30 | 0 | 32 | 16 | 35 |  |
| mug_marco | 114 | 62 | 0 | 31 | 33 | 118 |  |
| mug_priya | 20 | 9 | 0 | 11 | 1 | 5 |  |
| notebook_priya | 67 | 26 | 64 | 32 | 0 | 1 |  |
| razor_priya | 0 | 0 | 0 | 0 | 20 | 20 | yes |
| tablet_priya | 18 | 7 | 0 | 11 | 4 | 7 |  |
| towel_marco | 0 | 0 | 0 | 0 | 63 | 181 | yes |
| towel_priya | 4 | 0 | 0 | 4 | 52 | 167 |  |
| water_bottle_marco | 99 | 11 | 44 | 23 | 14 | 42 |  |
| water_bottle_priya | 132 | 4 | 64 | 32 | 5 | 35 |  |

histogram of moves per object: 0: 3, 4-10: 1, 11-30: 3, 31-100: 6, 101-300: 2

rare movers (3 of 15): book_priya, razor_priya, towel_marco

### hh_s63_t03  (n_days 32, 248 questions asked, 744 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_dana | 23 | 9 | 0 | 14 | 6 | 19 |  |
| book_priya | 0 | 0 | 0 | 0 | 1 | 2 | yes |
| charger_dana | 49 | 18 | 44 | 25 | 5 | 19 |  |
| glass_dana | 110 | 79 | 0 | 31 | 18 | 61 |  |
| glass_priya | 110 | 78 | 0 | 32 | 22 | 67 |  |
| glasses_priya | 46 | 17 | 0 | 29 | 11 | 27 |  |
| mug_dana | 143 | 96 | 0 | 29 | 22 | 93 |  |
| mug_priya | 62 | 30 | 0 | 32 | 24 | 51 |  |
| notebook_priya | 54 | 22 | 0 | 32 | 7 | 29 |  |
| razor_dana | 0 | 0 | 0 | 0 | 8 | 14 | yes |
| tablet_dana | 0 | 0 | 0 | 0 | 3 | 7 | yes |
| tablet_priya | 52 | 12 | 0 | 30 | 14 | 38 |  |
| towel_dana | 0 | 0 | 0 | 0 | 32 | 116 | yes |
| towel_priya | 0 | 0 | 0 | 0 | 56 | 133 | yes |
| water_bottle_dana | 102 | 10 | 44 | 26 | 10 | 37 |  |
| water_bottle_priya | 62 | 30 | 0 | 32 | 9 | 31 |  |

histogram of moves per object: 0: 5, 11-30: 1, 31-100: 6, 101-300: 4

rare movers (5 of 16): book_priya, razor_dana, tablet_dana, towel_dana, towel_priya

### hh_s93_t03  (n_days 32, 248 questions asked, 743 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_ines | 2 | 0 | 0 | 2 | 9 | 19 | yes |
| charger_ines | 8 | 0 | 0 | 8 | 37 | 90 |  |
| glass_ines | 6 | 3 | 0 | 3 | 22 | 46 |  |
| glass_kwame | 0 | 0 | 0 | 0 | 4 | 14 | yes |
| glasses_ines | 187 | 163 | 0 | 23 | 14 | 88 |  |
| medication_ines | 39 | 15 | 0 | 23 | 6 | 18 |  |
| mug_ines | 201 | 177 | 0 | 23 | 32 | 129 |  |
| mug_kwame | 0 | 0 | 0 | 0 | 7 | 18 | yes |
| razor_ines | 0 | 0 | 0 | 0 | 18 | 18 | yes |
| razor_kwame | 0 | 0 | 0 | 0 | 3 | 14 | yes |
| towel_ines | 0 | 0 | 0 | 0 | 27 | 82 | yes |
| towel_kwame | 0 | 0 | 0 | 0 | 37 | 100 | yes |
| water_bottle_ines | 175 | 151 | 0 | 23 | 30 | 102 |  |
| water_bottle_kwame | 64 | 31 | 64 | 32 | 2 | 5 |  |

histogram of moves per object: 0: 6, 2: 1, 4-10: 2, 31-100: 2, 101-300: 3

rare movers (7 of 14): book_ines, glass_kwame, mug_kwame, razor_ines, razor_kwame, towel_ines, towel_kwame

### rare movers that move at all (room level): when, and the questions that follow

| household | object | moves (day: from->to) | asked questions within 24 h | bank questions within 24 h |
|---|---|---|---:|---:|
| hh_s109_t03 | book_yuki | d14: bedroom_1->living; d24: living->bedroom_1 | 0 | 2 |
| hh_s123_t03 | glass_priya | d14: kitchen->bedroom_1; d24: bedroom_1->kitchen | 1 | 5 |
| hh_s19_t03 | glass_marco | d14: kitchen->bedroom_1; d24: bedroom_1->kitchen | 1 | 2 |
| hh_s20_t03 | book_hana | d12: bedroom_1->living; d24: living->bedroom_1 | 1 | 3 |
| hh_s2_t03 | book_tomas | d14: bedroom_1->living; d25: living->bedroom_1 | 1 | 2 |
| hh_s32_t03 | glass_aisha | d13: kitchen->living; d13: living->kitchen | 0 | 0 |
| hh_s32_t03 | glass_leo | d14: kitchen->bedroom_1; d24: bedroom_1->kitchen | 0 | 2 |
| hh_s93_t03 | book_ines | d14: bedroom_1->living; d31: living->bedroom_1 | 2 | 2 |

### odd things (room level)

- never move (46): hh_s109_t03/book_felix (1 asked), hh_s109_t03/notebook_felix (32 asked), hh_s109_t03/towel_felix (27 asked), hh_s109_t03/towel_yuki (30 asked), hh_s123_t03/glass_sam (27 asked), hh_s123_t03/razor_priya (20 asked), hh_s123_t03/razor_sam (4 asked), hh_s123_t03/towel_priya (60 asked), hh_s123_t03/towel_sam (68 asked), hh_s151_t03/razor_dana (16 asked), hh_s151_t03/towel_dana (66 asked), hh_s151_t03/towel_felix (45 asked), hh_s19_t03/book_omar (1 asked), hh_s19_t03/glass_omar (14 asked), hh_s19_t03/towel_marco (29 asked), hh_s19_t03/towel_omar (21 asked), hh_s20_t03/book_aisha (2 asked), hh_s20_t03/razor_aisha (11 asked), hh_s20_t03/towel_aisha (26 asked), hh_s20_t03/towel_hana (53 asked), hh_s2_t03/notebook_tomas (14 asked), hh_s2_t03/towel_ines (47 asked), hh_s2_t03/towel_tomas (53 asked), hh_s32_t03/book_aisha (2 asked), hh_s32_t03/book_elena (3 asked), hh_s32_t03/glass_elena (12 asked), hh_s32_t03/mug_aisha (0 asked), hh_s32_t03/mug_elena (7 asked), hh_s32_t03/notebook_leo (18 asked), hh_s32_t03/towel_aisha (38 asked), hh_s32_t03/towel_elena (36 asked), hh_s32_t03/towel_leo (29 asked), hh_s48_t03/book_priya (3 asked), hh_s48_t03/razor_priya (20 asked), hh_s48_t03/towel_marco (63 asked), hh_s63_t03/book_priya (1 asked), hh_s63_t03/razor_dana (8 asked), hh_s63_t03/tablet_dana (3 asked), hh_s63_t03/towel_dana (32 asked), hh_s63_t03/towel_priya (56 asked), hh_s93_t03/glass_kwame (4 asked), hh_s93_t03/mug_kwame (7 asked), hh_s93_t03/razor_ines (18 asked), hh_s93_t03/razor_kwame (3 asked), hh_s93_t03/towel_ines (27 asked), hh_s93_t03/towel_kwame (37 asked)
- move on every day or all but one (32): hh_s109_t03/charger_felix (359 moves), hh_s109_t03/glass_felix (112 moves), hh_s109_t03/glasses_felix (371 moves), hh_s109_t03/mug_felix (341 moves), hh_s109_t03/water_bottle_felix (352 moves), hh_s151_t03/glass_felix (107 moves), hh_s151_t03/mug_felix (179 moves), hh_s151_t03/water_bottle_felix (132 moves), hh_s19_t03/mug_omar (336 moves), hh_s19_t03/water_bottle_omar (282 moves), hh_s20_t03/charger_aisha (85 moves), hh_s20_t03/glass_aisha (62 moves), hh_s20_t03/glass_hana (128 moves), hh_s20_t03/medication_hana (59 moves), hh_s20_t03/water_bottle_aisha (129 moves), hh_s2_t03/glass_ines (107 moves), hh_s2_t03/water_bottle_ines (107 moves), hh_s32_t03/charger_aisha (86 moves), hh_s32_t03/mug_leo (222 moves), hh_s32_t03/notebook_elena (62 moves), hh_s32_t03/water_bottle_aisha (99 moves), hh_s48_t03/charger_priya (89 moves), hh_s48_t03/glass_priya (62 moves), hh_s48_t03/mug_marco (114 moves), hh_s48_t03/notebook_priya (67 moves), hh_s48_t03/water_bottle_priya (132 moves), hh_s63_t03/glass_dana (110 moves), hh_s63_t03/glass_priya (110 moves), hh_s63_t03/mug_priya (62 moves), hh_s63_t03/notebook_priya (54 moves), hh_s63_t03/water_bottle_priya (62 moves), hh_s93_t03/water_bottle_kwame (64 moves)
- in the bank's questions but never asked by the cells (7): hh_s123_t03/notebook_priya (4 in bank), hh_s151_t03/glasses_felix (3 in bank), hh_s20_t03/medication_hana (3 in bank), hh_s32_t03/mug_aisha (2 in bank), hh_s32_t03/tablet_aisha (8 in bank), hh_s48_t03/charger_priya (15 in bank), hh_s48_t03/notebook_priya (1 in bank)

### all households, histogram of moves per object (room level)

| moves | objects |
|---|---:|
| 0 | 46 |
| 1 | 0 |
| 2 | 8 |
| 3 | 0 |
| 4-10 | 7 |
| 11-30 | 13 |
| 31-100 | 37 |
| 101-300 | 29 |
| >300 | 5 |

## 2 (room level). Questions within 24 h after a move

| household | questions | rare-move questions | rare movers asked about | rare-move questions in the full bank | all-move questions | other (no move of the object in the prior 24 h) | about never-moving objects |
|---|---:|---:|---:|---:|---:|---:|---:|
| hh_s109_t03 | 248 | 0 | 0 | 2 | 150 | 98 | 90 |
| hh_s123_t03 | 248 | 1 | 1 | 5 | 42 | 206 | 179 |
| hh_s151_t03 | 248 | 0 | 0 | 0 | 97 | 151 | 127 |
| hh_s19_t03 | 248 | 1 | 1 | 2 | 136 | 112 | 65 |
| hh_s20_t03 | 248 | 1 | 1 | 3 | 135 | 113 | 92 |
| hh_s2_t03 | 248 | 1 | 1 | 2 | 112 | 136 | 114 |
| hh_s32_t03 | 248 | 0 | 0 | 2 | 70 | 178 | 145 |
| hh_s48_t03 | 248 | 0 | 0 | 0 | 91 | 157 | 86 |
| hh_s63_t03 | 248 | 0 | 0 | 0 | 131 | 117 | 100 |
| hh_s93_t03 | 248 | 2 | 1 | 2 | 82 | 166 | 96 |
| **total** | 2480 | 6 | | 18 | 1046 | 1434 | 1094 |

The rare-move questions are a subset of the all-move questions. A question is in exactly one of: all-move, other. 'In the full bank' counts all the bank's questions (24 a day), not only those the cells asked.

How the asked-question count in the rare slice depends on the rare threshold (room level, all households):

| at most this many moves | asked questions within 24 h after a move of such an object |
|---:|---:|
| 3 | 6 |
| 5 | 17 |
| 10 | 29 |
| 20 | 45 |
| 30 | 91 |

## 3 (room level). First guess right (found_at_step == 1), per cent

`most_frequent_offline` is an offline estimate computed here from the bank: for each question, the room the object was truly in most often at the times of the earlier asked questions about it (ties by most recent); no guess before the first question about an object. It uses true rooms, which no robot had; the cells used what they saw.


### (a) rare-move questions

| method | hh_s109_t03 | hh_s123_t03 | hh_s151_t03 | hh_s19_t03 | hh_s20_t03 | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | hh_s63_t03 | hh_s93_t03 | pooled | pooled n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| a_small_working_memory_and_an_archive | – | 0.0 | – | 100.0 | 0.0 | 0.0 | – | – | – | 0.0 | 16.7 | 6 |
| claim_store_told_if_it_was_right | – | 0.0 | – | 0.0 | 0.0 | 0.0 | – | – | – | 0.0 | 0.0 | 6 |
| incremental_edits | – | 0.0 | – | 100.0 | 0.0 | 0.0 | – | – | – | 0.0 | 16.7 | 6 |
| last_seen_no_model | – | 0.0 | – | 0.0 | 0.0 | 0.0 | – | – | – | 100.0 | 33.3 | 6 |
| prior_only_no_notes | – | 0.0 | – | 0.0 | 0.0 | 0.0 | – | – | – | 100.0 | 33.3 | 6 |
| the_log_and_notes_about_the_routine | – | 0.0 | – | 100.0 | 0.0 | 0.0 | – | – | – | 50.0 | 33.3 | 6 |
| wholesale_rewrite | – | – | – | – | – | 0.0 | – | – | – | – | 0.0 | 1 |
| most_frequent_offline | – | 0.0 | – | 0.0 | 0.0 | 0.0 | – | – | – | 0.0 | 0.0 | 6 |

Paired per-household difference against `last_seen_no_model` (points; households with the method present and a non-empty slice):

| method | n households | mean | SE | 2 SE | per household |
|---|---:|---:|---:|---:|---|
| a_small_working_memory_and_an_archive | 5 | +0.0 | 31.6 | 63.2 | s123:+0 s19:+100 s20:+0 s2:+0 s93:-100 |
| claim_store_told_if_it_was_right | 5 | -20.0 | 20.0 | 40.0 | s123:+0 s19:+0 s20:+0 s2:+0 s93:-100 |
| incremental_edits | 5 | +0.0 | 31.6 | 63.2 | s123:+0 s19:+100 s20:+0 s2:+0 s93:-100 |
| prior_only_no_notes | 5 | +0.0 | 0.0 | 0.0 | s123:+0 s19:+0 s20:+0 s2:+0 s93:+0 |
| the_log_and_notes_about_the_routine | 5 | +10.0 | 24.5 | 49.0 | s123:+0 s19:+100 s20:+0 s2:+0 s93:-50 |
| wholesale_rewrite | 1 | +0.0 | – | – | s2:+0 |
| most_frequent_offline | 5 | -20.0 | 20.0 | 40.0 | s123:+0 s19:+0 s20:+0 s2:+0 s93:-100 |

### (b) all-move questions

| method | hh_s109_t03 | hh_s123_t03 | hh_s151_t03 | hh_s19_t03 | hh_s20_t03 | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | hh_s63_t03 | hh_s93_t03 | pooled | pooled n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| a_small_working_memory_and_an_archive | 68.7 | 23.8 | 18.6 | 73.5 | 31.1 | 75.9 | 44.3 | 17.6 | 62.6 | 13.4 | 47.6 | 1046 |
| claim_store_told_if_it_was_right | 68.7 | 40.5 | 21.6 | 75.0 | 16.3 | 51.8 | 64.3 | 46.2 | 74.0 | 37.8 | 51.4 | 1046 |
| incremental_edits | 65.3 | 28.6 | 43.3 | 81.6 | 35.6 | 58.0 | 62.9 | 38.5 | 57.3 | 37.8 | 53.6 | 1046 |
| last_seen_no_model | 66.7 | 23.8 | 40.2 | 64.0 | 64.4 | 69.6 | 61.4 | 50.5 | 86.3 | 64.6 | 62.7 | 1046 |
| prior_only_no_notes | 6.0 | 16.7 | 8.2 | 37.5 | 7.4 | 7.1 | 14.3 | 12.1 | 1.5 | 11.0 | 12.0 | 1046 |
| the_log_and_notes_about_the_routine | 76.0 | 33.3 | 54.6 | 75.0 | 75.6 | 81.2 | 68.6 | 58.2 | 63.4 | 68.3 | 68.5 | 1046 |
| wholesale_rewrite | – | – | – | – | – | 46.4 | – | – | – | – | 46.4 | 112 |
| most_frequent_offline | 75.3 | 61.9 | 72.2 | 71.3 | 75.6 | 80.4 | 70.0 | 60.4 | 81.7 | 73.2 | 73.5 | 1046 |

Paired per-household difference against `last_seen_no_model` (points; households with the method present and a non-empty slice):

| method | n households | mean | SE | 2 SE | per household |
|---|---:|---:|---:|---:|---|
| a_small_working_memory_and_an_archive | 10 | -16.2 | 6.4 | 12.7 | s109:+2 s123:+0 s151:-22 s19:+10 s20:-33 s2:+6 s32:-17 s48:-33 s63:-24 s93:-51 |
| claim_store_told_if_it_was_right | 10 | -9.5 | 6.1 | 12.2 | s109:+2 s123:+17 s151:-19 s19:+11 s20:-48 s2:-18 s32:+3 s48:-4 s63:-12 s93:-27 |
| incremental_edits | 10 | -8.3 | 5.1 | 10.2 | s109:-1 s123:+5 s151:+3 s19:+18 s20:-29 s2:-12 s32:+1 s48:-12 s63:-29 s93:-27 |
| prior_only_no_notes | 10 | -47.0 | 6.9 | 13.8 | s109:-61 s123:-7 s151:-32 s19:-26 s20:-57 s2:-62 s32:-47 s48:-38 s63:-85 s93:-54 |
| the_log_and_notes_about_the_routine | 10 | +6.3 | 3.4 | 6.7 | s109:+9 s123:+10 s151:+14 s19:+11 s20:+11 s2:+12 s32:+7 s48:+8 s63:-23 s93:+4 |
| wholesale_rewrite | 1 | -23.2 | – | – | s2:-23 |
| most_frequent_offline | 10 | +13.0 | 4.0 | 7.9 | s109:+9 s123:+38 s151:+32 s19:+7 s20:+11 s2:+11 s32:+9 s48:+10 s63:-5 s93:+9 |

### (c) all other questions

| method | hh_s109_t03 | hh_s123_t03 | hh_s151_t03 | hh_s19_t03 | hh_s20_t03 | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | hh_s63_t03 | hh_s93_t03 | pooled | pooled n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| a_small_working_memory_and_an_archive | 91.8 | 91.7 | 92.1 | 90.2 | 89.4 | 89.0 | 82.6 | 98.7 | 85.5 | 72.3 | 88.1 | 1434 |
| claim_store_told_if_it_was_right | 95.9 | 96.6 | 92.1 | 94.6 | 91.2 | 95.6 | 92.1 | 96.8 | 96.6 | 89.2 | 94.0 | 1434 |
| incremental_edits | 95.9 | 100.0 | 97.4 | 95.5 | 90.3 | 97.1 | 86.0 | 96.2 | 94.0 | 88.6 | 94.1 | 1434 |
| last_seen_no_model | 96.9 | 97.6 | 96.0 | 95.5 | 92.9 | 94.1 | 93.8 | 98.1 | 98.3 | 98.2 | 96.2 | 1434 |
| prior_only_no_notes | 93.9 | 90.3 | 87.4 | 87.5 | 88.5 | 87.5 | 73.6 | 86.0 | 85.5 | 65.7 | 83.8 | 1434 |
| the_log_and_notes_about_the_routine | 94.9 | 99.5 | 98.0 | 100.0 | 97.3 | 97.8 | 100.0 | 99.4 | 94.0 | 97.6 | 98.1 | 1434 |
| wholesale_rewrite | – | – | – | – | – | 82.4 | – | – | – | – | 82.4 | 136 |
| most_frequent_offline | 90.8 | 92.2 | 92.7 | 84.8 | 83.2 | 88.2 | 86.0 | 91.7 | 88.9 | 80.1 | 88.0 | 1434 |

Paired per-household difference against `last_seen_no_model` (points; households with the method present and a non-empty slice):

| method | n households | mean | SE | 2 SE | per household |
|---|---:|---:|---:|---:|---|
| a_small_working_memory_and_an_archive | 10 | -7.8 | 2.3 | 4.7 | s109:-5 s123:-6 s151:-4 s19:-5 s20:-4 s2:-5 s32:-11 s48:+1 s63:-13 s93:-26 |
| claim_store_told_if_it_was_right | 10 | -2.1 | 0.9 | 1.8 | s109:-1 s123:-1 s151:-4 s19:-1 s20:-2 s2:+1 s32:-2 s48:-1 s63:-2 s93:-9 |
| incremental_edits | 10 | -2.1 | 1.3 | 2.7 | s109:-1 s123:+2 s151:+1 s19:+0 s20:-3 s2:+3 s32:-8 s48:-2 s63:-4 s93:-10 |
| prior_only_no_notes | 10 | -11.6 | 2.8 | 5.6 | s109:-3 s123:-7 s151:-9 s19:-8 s20:-4 s2:-7 s32:-20 s48:-12 s63:-13 s93:-33 |
| the_log_and_notes_about_the_routine | 10 | +1.7 | 1.0 | 2.0 | s109:-2 s123:+2 s151:+2 s19:+4 s20:+4 s2:+4 s32:+6 s48:+1 s63:-4 s93:-1 |
| wholesale_rewrite | 1 | -11.8 | – | – | s2:-12 |
| most_frequent_offline | 10 | -8.3 | 1.3 | 2.6 | s109:-6 s123:-5 s151:-3 s19:-11 s20:-10 s2:-6 s32:-8 s48:-6 s63:-9 s93:-18 |

## 4 (room level). Rare-move questions per household and the detectable gap

| household | rare-move questions |
|---|---:|
| hh_s109_t03 | 0 |
| hh_s123_t03 | 1 |
| hh_s151_t03 | 0 |
| hh_s19_t03 | 1 |
| hh_s20_t03 | 1 |
| hh_s2_t03 | 1 |
| hh_s32_t03 | 0 |
| hh_s48_t03 | 0 |
| hh_s63_t03 | 0 |
| hh_s93_t03 | 2 |

Best method on the rare-move slice by pooled first guess right (ties all listed): `prior_only_no_notes` (33.3%). Paired against `last_seen_no_model` over 5 households with a non-empty slice: mean +0.0, SE 0.0, 2 SE 0.0. (The paired table under 3(a) has every method.)

Best method on the rare-move slice by pooled first guess right (ties all listed): `the_log_and_notes_about_the_routine` (33.3%). Paired against `last_seen_no_model` over 5 households with a non-empty slice: mean +10.0, SE 24.5, 2 SE 49.0. (The paired table under 3(a) has every method.)

## Notes on this wave

- true_room in last_seen's searches.jsonl agrees with the bank on all but 0 rows.

# wave_the_second_illness (three homes, 50 days, 24 questions a day)

cells: `results/self_improve/wave_the_second_illness/cells`; banks: `results/self_improve/varied_homes/all_generated_v2_twice/banks`


## 1 (place level). Moves per asked-about object

A move is a change of place; rare mover = at most 3 moves. `nq` = questions the cells asked about the object. `pairs` = change-and-change-back within one calendar day (counted as two moves).


### hh_s2_t03  (n_days 50, 1176 questions asked, 1176 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_tomas | 25 | 4 | 0 | 18 | 34 | 34 |  |
| charger_tomas | 335 | 267 | 0 | 35 | 95 | 95 |  |
| glass_ines | 195 | 53 | 0 | 49 | 82 | 82 |  |
| glass_tomas | 127 | 25 | 0 | 36 | 59 | 59 |  |
| mug_ines | 128 | 8 | 0 | 48 | 50 | 50 |  |
| mug_tomas | 386 | 178 | 0 | 44 | 155 | 155 |  |
| notebook_tomas | 60 | 33 | 0 | 18 | 92 | 92 |  |
| towel_ines | 0 | 0 | 0 | 0 | 223 | 223 | yes |
| towel_tomas | 0 | 0 | 0 | 0 | 242 | 242 | yes |
| water_bottle_ines | 186 | 2 | 66 | 50 | 30 | 30 |  |
| water_bottle_tomas | 414 | 190 | 38 | 38 | 114 | 114 |  |

histogram of moves per object: 0: 2, 11-30: 1, 31-100: 1, 101-300: 4, >300: 3

rare movers (2 of 11): towel_ines, towel_tomas

### hh_s32_t03  (n_days 50, 1176 questions asked, 1176 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_aisha | 24 | 5 | 0 | 16 | 15 | 15 |  |
| book_elena | 31 | 11 | 0 | 20 | 11 | 11 |  |
| book_leo | 25 | 8 | 0 | 14 | 15 | 15 |  |
| charger_aisha | 178 | 6 | 100 | 50 | 11 | 11 |  |
| charger_leo | 320 | 248 | 0 | 34 | 90 | 90 |  |
| glass_aisha | 144 | 28 | 0 | 50 | 24 | 24 |  |
| glass_elena | 235 | 71 | 0 | 50 | 76 | 76 |  |
| glass_leo | 174 | 54 | 0 | 43 | 45 | 45 |  |
| mug_aisha | 75 | 5 | 0 | 27 | 5 | 5 |  |
| mug_elena | 147 | 7 | 0 | 50 | 46 | 46 |  |
| mug_leo | 371 | 167 | 0 | 50 | 114 | 114 |  |
| notebook_elena | 95 | 39 | 0 | 50 | 22 | 22 |  |
| notebook_leo | 54 | 27 | 0 | 18 | 81 | 81 |  |
| tablet_aisha | 44 | 16 | 0 | 25 | 11 | 11 |  |
| tablet_leo | 61 | 12 | 0 | 38 | 26 | 26 |  |
| towel_aisha | 33 | 11 | 0 | 22 | 143 | 143 |  |
| towel_elena | 0 | 0 | 0 | 0 | 159 | 159 | yes |
| towel_leo | 0 | 0 | 0 | 0 | 157 | 157 | yes |
| water_bottle_aisha | 240 | 10 | 101 | 50 | 27 | 27 |  |
| water_bottle_leo | 324 | 145 | 0 | 43 | 98 | 98 |  |

histogram of moves per object: 0: 2, 11-30: 2, 31-100: 7, 101-300: 6, >300: 3

rare movers (2 of 20): towel_elena, towel_leo

### hh_s48_t03  (n_days 50, 1176 questions asked, 1176 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_marco | 59 | 7 | 0 | 36 | 45 | 45 |  |
| book_priya | 9 | 1 | 0 | 6 | 10 | 10 |  |
| charger_marco | 84 | 17 | 60 | 43 | 30 | 30 |  |
| charger_priya | 173 | 5 | 100 | 50 | 28 | 28 |  |
| glass_marco | 143 | 42 | 0 | 42 | 106 | 106 |  |
| glass_priya | 128 | 7 | 0 | 50 | 55 | 55 |  |
| mug_marco | 182 | 66 | 0 | 48 | 175 | 175 |  |
| mug_priya | 48 | 3 | 0 | 21 | 9 | 9 |  |
| notebook_priya | 106 | 23 | 100 | 50 | 2 | 2 |  |
| razor_priya | 84 | 23 | 0 | 47 | 30 | 30 |  |
| tablet_priya | 31 | 11 | 0 | 18 | 11 | 11 |  |
| towel_marco | 0 | 0 | 0 | 0 | 283 | 283 | yes |
| towel_priya | 46 | 17 | 0 | 25 | 270 | 270 |  |
| water_bottle_marco | 160 | 3 | 60 | 37 | 65 | 65 |  |
| water_bottle_priya | 233 | 0 | 100 | 50 | 57 | 57 |  |

histogram of moves per object: 0: 1, 4-10: 1, 31-100: 6, 101-300: 7

rare movers (1 of 15): towel_marco

### rare movers that move at all (place level): when, and the questions that follow

none: every rare mover has zero moves.

### odd things (place level)

- move on every day or all but one (13): hh_s2_t03/glass_ines (195 moves), hh_s2_t03/water_bottle_ines (186 moves), hh_s32_t03/charger_aisha (178 moves), hh_s32_t03/glass_aisha (144 moves), hh_s32_t03/glass_elena (235 moves), hh_s32_t03/mug_elena (147 moves), hh_s32_t03/mug_leo (371 moves), hh_s32_t03/notebook_elena (95 moves), hh_s32_t03/water_bottle_aisha (240 moves), hh_s48_t03/charger_priya (173 moves), hh_s48_t03/glass_priya (128 moves), hh_s48_t03/notebook_priya (106 moves), hh_s48_t03/water_bottle_priya (233 moves)
- never move (5): hh_s2_t03/towel_ines (223 asked), hh_s2_t03/towel_tomas (242 asked), hh_s32_t03/towel_elena (159 asked), hh_s32_t03/towel_leo (157 asked), hh_s48_t03/towel_marco (283 asked)

### all households, histogram of moves per object (place level)

| moves | objects |
|---|---:|
| 0 | 5 |
| 1 | 0 |
| 2 | 0 |
| 3 | 0 |
| 4-10 | 1 |
| 11-30 | 3 |
| 31-100 | 14 |
| 101-300 | 17 |
| >300 | 6 |

## 2 (place level). Questions within 24 h after a move

| household | questions | rare-move questions | rare movers asked about | rare-move questions in the full bank | all-move questions | other (no move of the object in the prior 24 h) | about never-moving objects |
|---|---:|---:|---:|---:|---:|---:|---:|
| hh_s2_t03 | 1176 | 0 | 0 | 0 | 567 | 609 | 465 |
| hh_s32_t03 | 1176 | 0 | 0 | 0 | 681 | 495 | 316 |
| hh_s48_t03 | 1176 | 0 | 0 | 0 | 661 | 515 | 283 |
| **total** | 3528 | 0 | | 0 | 1909 | 1619 | 1064 |

The rare-move questions are a subset of the all-move questions. A question is in exactly one of: all-move, other. 'In the full bank' counts all the bank's questions (24 a day), not only those the cells asked.

How the asked-question count in the rare slice depends on the rare threshold (place level, all households):

| at most this many moves | asked questions within 24 h after a move of such an object |
|---:|---:|
| 3 | 0 |
| 5 | 0 |
| 10 | 6 |
| 20 | 6 |
| 30 | 38 |

## 3 (place level). First guess right (found_at_step == 1), per cent

`most_frequent_offline` is an offline estimate computed here from the bank: for each question, the room the object was truly in most often at the times of the earlier asked questions about it (ties by most recent); no guess before the first question about an object. It uses true rooms, which no robot had; the cells used what they saw.


### (a) rare-move questions

| method | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | pooled | pooled n |
|---|---:|---:|---:|---:|---:|
| ACE_as_published | – | – | – | – | 0 |
| incremental_edits | – | – | – | – | 0 |
| last_seen_no_model | – | – | – | – | 0 |
| ours_told_the_night_before | – | – | – | – | 0 |
| the_log_and_notes_about_the_routine | – | – | – | – | 0 |
| most_frequent_offline | – | – | – | – | 0 |

Paired per-household difference against `last_seen_no_model` (points; households with the method present and a non-empty slice):

| method | n households | mean | SE | 2 SE | per household |
|---|---:|---:|---:|---:|---|
| ACE_as_published | 0 | – | – | – |  |
| incremental_edits | 0 | – | – | – |  |
| ours_told_the_night_before | 0 | – | – | – |  |
| the_log_and_notes_about_the_routine | 0 | – | – | – |  |
| most_frequent_offline | 0 | – | – | – |  |

### (b) all-move questions

| method | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | pooled | pooled n |
|---|---:|---:|---:|---:|---:|
| ACE_as_published | 67.5 | 81.4 | 55.8 | 68.4 | 1909 |
| incremental_edits | 64.7 | 63.0 | 56.3 | 61.2 | 1909 |
| last_seen_no_model | 78.7 | 86.5 | 69.1 | 78.2 | 1909 |
| ours_told_the_night_before | 83.1 | 87.4 | 80.8 | 83.8 | 1909 |
| the_log_and_notes_about_the_routine | 82.0 | 88.1 | 83.2 | 84.6 | 1909 |
| most_frequent_offline | 78.7 | 80.3 | 75.5 | 78.2 | 1909 |

Paired per-household difference against `last_seen_no_model` (points; households with the method present and a non-empty slice):

| method | n households | mean | SE | 2 SE | per household |
|---|---:|---:|---:|---:|---|
| ACE_as_published | 3 | -9.9 | 2.4 | 4.9 | s2:-11 s32:-5 s48:-13 |
| incremental_edits | 3 | -16.8 | 3.4 | 6.8 | s2:-14 s32:-23 s48:-13 |
| ours_told_the_night_before | 3 | +5.6 | 3.2 | 6.3 | s2:+4 s32:+1 s48:+12 |
| the_log_and_notes_about_the_routine | 3 | +6.3 | 3.9 | 7.8 | s2:+3 s32:+2 s48:+14 |
| most_frequent_offline | 3 | +0.1 | 3.6 | 7.2 | s2:+0 s32:-6 s48:+6 |

### (c) all other questions

| method | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | pooled | pooled n |
|---|---:|---:|---:|---:|---:|
| ACE_as_published | 97.7 | 98.6 | 95.0 | 97.1 | 1619 |
| incremental_edits | 98.2 | 95.4 | 97.3 | 97.0 | 1619 |
| last_seen_no_model | 99.2 | 98.4 | 96.3 | 98.0 | 1619 |
| ours_told_the_night_before | 99.5 | 99.2 | 99.0 | 99.3 | 1619 |
| the_log_and_notes_about_the_routine | 99.5 | 99.8 | 99.8 | 99.7 | 1619 |
| most_frequent_offline | 89.3 | 93.5 | 91.3 | 91.2 | 1619 |

Paired per-household difference against `last_seen_no_model` (points; households with the method present and a non-empty slice):

| method | n households | mean | SE | 2 SE | per household |
|---|---:|---:|---:|---:|---|
| ACE_as_published | 3 | -0.9 | 0.5 | 1.1 | s2:-1 s32:+0 s48:-1 |
| incremental_edits | 3 | -1.0 | 1.2 | 2.3 | s2:-1 s32:-3 s48:+1 |
| ours_told_the_night_before | 3 | +1.3 | 0.7 | 1.5 | s2:+0 s32:+1 s48:+3 |
| the_log_and_notes_about_the_routine | 3 | +1.7 | 0.9 | 1.9 | s2:+0 s32:+1 s48:+3 |
| most_frequent_offline | 3 | -6.6 | 1.6 | 3.3 | s2:-10 s32:-5 s48:-5 |

## 4 (place level). Rare-move questions per household and the detectable gap

| household | rare-move questions |
|---|---:|
| hh_s2_t03 | 0 |
| hh_s32_t03 | 0 |
| hh_s48_t03 | 0 |

No rare-move questions in any household; no gap is detectable on this slice.

## 1 (room level). Moves per asked-about object

A move is a change of room; rare mover = at most 3 moves. `nq` = questions the cells asked about the object. `pairs` = change-and-change-back within one calendar day (counted as two moves).


### hh_s2_t03  (n_days 50, 1176 questions asked, 1176 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_tomas | 8 | 2 | 0 | 6 | 34 | 34 |  |
| charger_tomas | 324 | 293 | 0 | 31 | 95 | 95 |  |
| glass_ines | 165 | 113 | 0 | 49 | 82 | 82 |  |
| glass_tomas | 94 | 60 | 0 | 32 | 59 | 59 |  |
| mug_ines | 90 | 42 | 0 | 48 | 50 | 50 |  |
| mug_tomas | 351 | 252 | 0 | 43 | 155 | 155 |  |
| notebook_tomas | 0 | 0 | 0 | 0 | 92 | 92 | yes |
| towel_ines | 0 | 0 | 0 | 0 | 223 | 223 | yes |
| towel_tomas | 0 | 0 | 0 | 0 | 242 | 242 | yes |
| water_bottle_ines | 159 | 16 | 66 | 49 | 30 | 30 |  |
| water_bottle_tomas | 373 | 246 | 38 | 32 | 114 | 114 |  |

histogram of moves per object: 0: 3, 4-10: 1, 31-100: 2, 101-300: 2, >300: 3

rare movers (3 of 11): notebook_tomas, towel_ines, towel_tomas

### hh_s32_t03  (n_days 50, 1176 questions asked, 1176 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_aisha | 0 | 0 | 0 | 0 | 15 | 15 | yes |
| book_elena | 0 | 0 | 0 | 0 | 11 | 11 | yes |
| book_leo | 8 | 2 | 0 | 6 | 15 | 15 |  |
| charger_aisha | 138 | 19 | 100 | 50 | 11 | 11 |  |
| charger_leo | 314 | 282 | 0 | 32 | 90 | 90 |  |
| glass_aisha | 2 | 1 | 0 | 1 | 24 | 24 | yes |
| glass_elena | 0 | 0 | 0 | 0 | 76 | 76 | yes |
| glass_leo | 14 | 9 | 0 | 5 | 45 | 45 |  |
| mug_aisha | 2 | 1 | 0 | 1 | 5 | 5 | yes |
| mug_elena | 0 | 0 | 0 | 0 | 46 | 46 | yes |
| mug_leo | 304 | 252 | 0 | 50 | 114 | 114 |  |
| notebook_elena | 94 | 44 | 0 | 50 | 22 | 22 |  |
| notebook_leo | 0 | 0 | 0 | 0 | 81 | 81 | yes |
| tablet_aisha | 42 | 17 | 0 | 25 | 11 | 11 |  |
| tablet_leo | 53 | 19 | 0 | 33 | 26 | 26 |  |
| towel_aisha | 0 | 0 | 0 | 0 | 143 | 143 | yes |
| towel_elena | 0 | 0 | 0 | 0 | 159 | 159 | yes |
| towel_leo | 0 | 0 | 0 | 0 | 157 | 157 | yes |
| water_bottle_aisha | 156 | 4 | 100 | 50 | 27 | 27 |  |
| water_bottle_leo | 218 | 183 | 0 | 32 | 98 | 98 |  |

histogram of moves per object: 0: 8, 2: 2, 4-10: 1, 11-30: 1, 31-100: 3, 101-300: 3, >300: 2

rare movers (10 of 20): book_aisha, book_elena, glass_aisha, glass_elena, mug_aisha, mug_elena, notebook_leo, towel_aisha, towel_elena, towel_leo

### hh_s48_t03  (n_days 50, 1176 questions asked, 1176 in the bank)

| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |
|---|---:|---:|---:|---:|---:|---:|---|
| book_marco | 35 | 11 | 0 | 23 | 45 | 45 |  |
| book_priya | 0 | 0 | 0 | 0 | 10 | 10 | yes |
| charger_marco | 68 | 25 | 60 | 32 | 30 | 30 |  |
| charger_priya | 140 | 22 | 100 | 50 | 28 | 28 |  |
| glass_marco | 104 | 68 | 0 | 34 | 106 | 106 |  |
| glass_priya | 98 | 48 | 0 | 50 | 55 | 55 |  |
| mug_marco | 159 | 87 | 0 | 46 | 175 | 175 |  |
| mug_priya | 36 | 16 | 0 | 20 | 9 | 9 |  |
| notebook_priya | 105 | 39 | 100 | 50 | 2 | 2 |  |
| razor_priya | 0 | 0 | 0 | 0 | 30 | 30 | yes |
| tablet_priya | 30 | 12 | 0 | 18 | 11 | 11 |  |
| towel_marco | 0 | 0 | 0 | 0 | 283 | 283 | yes |
| towel_priya | 4 | 0 | 0 | 4 | 270 | 270 |  |
| water_bottle_marco | 134 | 13 | 60 | 32 | 65 | 65 |  |
| water_bottle_priya | 206 | 5 | 100 | 50 | 57 | 57 |  |

histogram of moves per object: 0: 3, 4-10: 1, 11-30: 1, 31-100: 4, 101-300: 6

rare movers (3 of 15): book_priya, razor_priya, towel_marco

### rare movers that move at all (room level): when, and the questions that follow

| household | object | moves (day: from->to) | asked questions within 24 h | bank questions within 24 h |
|---|---|---|---:|---:|
| hh_s32_t03 | glass_aisha | d13: kitchen->living; d13: living->kitchen | 0 | 0 |
| hh_s32_t03 | mug_aisha | d37: kitchen->bedroom_3; d37: bedroom_3->kitchen | 1 | 1 |

### odd things (room level)

- move on every day or all but one (10): hh_s2_t03/glass_ines (165 moves), hh_s2_t03/water_bottle_ines (159 moves), hh_s32_t03/charger_aisha (138 moves), hh_s32_t03/mug_leo (304 moves), hh_s32_t03/notebook_elena (94 moves), hh_s32_t03/water_bottle_aisha (156 moves), hh_s48_t03/charger_priya (140 moves), hh_s48_t03/glass_priya (98 moves), hh_s48_t03/notebook_priya (105 moves), hh_s48_t03/water_bottle_priya (206 moves)
- never move (14): hh_s2_t03/notebook_tomas (92 asked), hh_s2_t03/towel_ines (223 asked), hh_s2_t03/towel_tomas (242 asked), hh_s32_t03/book_aisha (15 asked), hh_s32_t03/book_elena (11 asked), hh_s32_t03/glass_elena (76 asked), hh_s32_t03/mug_elena (46 asked), hh_s32_t03/notebook_leo (81 asked), hh_s32_t03/towel_aisha (143 asked), hh_s32_t03/towel_elena (159 asked), hh_s32_t03/towel_leo (157 asked), hh_s48_t03/book_priya (10 asked), hh_s48_t03/razor_priya (30 asked), hh_s48_t03/towel_marco (283 asked)

### all households, histogram of moves per object (room level)

| moves | objects |
|---|---:|
| 0 | 14 |
| 1 | 0 |
| 2 | 2 |
| 3 | 0 |
| 4-10 | 3 |
| 11-30 | 2 |
| 31-100 | 9 |
| 101-300 | 11 |
| >300 | 5 |

## 2 (room level). Questions within 24 h after a move

| household | questions | rare-move questions | rare movers asked about | rare-move questions in the full bank | all-move questions | other (no move of the object in the prior 24 h) | about never-moving objects |
|---|---:|---:|---:|---:|---:|---:|---:|
| hh_s2_t03 | 1176 | 0 | 0 | 0 | 493 | 683 | 557 |
| hh_s32_t03 | 1176 | 1 | 1 | 1 | 359 | 817 | 688 |
| hh_s48_t03 | 1176 | 0 | 0 | 0 | 486 | 690 | 323 |
| **total** | 3528 | 1 | | 1 | 1338 | 2190 | 1568 |

The rare-move questions are a subset of the all-move questions. A question is in exactly one of: all-move, other. 'In the full bank' counts all the bank's questions (24 a day), not only those the cells asked.

How the asked-question count in the rare slice depends on the rare threshold (room level, all households):

| at most this many moves | asked questions within 24 h after a move of such an object |
|---:|---:|
| 3 | 1 |
| 5 | 22 |
| 10 | 32 |
| 20 | 36 |
| 30 | 46 |

## 3 (room level). First guess right (found_at_step == 1), per cent

`most_frequent_offline` is an offline estimate computed here from the bank: for each question, the room the object was truly in most often at the times of the earlier asked questions about it (ties by most recent); no guess before the first question about an object. It uses true rooms, which no robot had; the cells used what they saw.


### (a) rare-move questions

| method | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | pooled | pooled n |
|---|---:|---:|---:|---:|---:|
| ACE_as_published | – | 0.0 | – | 0.0 | 1 |
| incremental_edits | – | 0.0 | – | 0.0 | 1 |
| last_seen_no_model | – | 100.0 | – | 100.0 | 1 |
| ours_told_the_night_before | – | 100.0 | – | 100.0 | 1 |
| the_log_and_notes_about_the_routine | – | 100.0 | – | 100.0 | 1 |
| most_frequent_offline | – | 0.0 | – | 0.0 | 1 |

Paired per-household difference against `last_seen_no_model` (points; households with the method present and a non-empty slice):

| method | n households | mean | SE | 2 SE | per household |
|---|---:|---:|---:|---:|---|
| ACE_as_published | 1 | -100.0 | – | – | s32:-100 |
| incremental_edits | 1 | -100.0 | – | – | s32:-100 |
| ours_told_the_night_before | 1 | +0.0 | – | – | s32:+0 |
| the_log_and_notes_about_the_routine | 1 | +0.0 | – | – | s32:+0 |
| most_frequent_offline | 1 | -100.0 | – | – | s32:-100 |

### (b) all-move questions

| method | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | pooled | pooled n |
|---|---:|---:|---:|---:|---:|
| ACE_as_published | 64.1 | 66.0 | 42.6 | 56.8 | 1338 |
| incremental_edits | 60.2 | 65.2 | 41.2 | 54.6 | 1338 |
| last_seen_no_model | 75.5 | 74.7 | 60.5 | 69.8 | 1338 |
| ours_told_the_night_before | 80.5 | 76.3 | 74.1 | 77.1 | 1338 |
| the_log_and_notes_about_the_routine | 79.5 | 78.3 | 77.2 | 78.3 | 1338 |
| most_frequent_offline | 78.1 | 73.0 | 71.8 | 74.4 | 1338 |

Paired per-household difference against `last_seen_no_model` (points; households with the method present and a non-empty slice):

| method | n households | mean | SE | 2 SE | per household |
|---|---:|---:|---:|---:|---|
| ACE_as_published | 3 | -12.6 | 2.7 | 5.5 | s2:-11 s32:-9 s48:-18 |
| incremental_edits | 3 | -14.7 | 2.9 | 5.7 | s2:-15 s32:-9 s48:-19 |
| ours_told_the_night_before | 3 | +6.8 | 3.5 | 7.1 | s2:+5 s32:+2 s48:+14 |
| the_log_and_notes_about_the_routine | 3 | +8.1 | 4.3 | 8.6 | s2:+4 s32:+4 s48:+17 |
| most_frequent_offline | 3 | +4.1 | 3.8 | 7.6 | s2:+3 s32:-2 s48:+11 |

### (c) all other questions

| method | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | pooled | pooled n |
|---|---:|---:|---:|---:|---:|
| ACE_as_published | 96.9 | 98.5 | 94.3 | 96.7 | 2190 |
| incremental_edits | 97.8 | 81.6 | 97.5 | 91.7 | 2190 |
| last_seen_no_model | 99.3 | 98.9 | 95.5 | 97.9 | 2190 |
| ours_told_the_night_before | 99.6 | 99.4 | 99.1 | 99.4 | 2190 |
| the_log_and_notes_about_the_routine | 99.4 | 99.5 | 99.9 | 99.6 | 2190 |
| most_frequent_offline | 88.6 | 91.6 | 89.9 | 90.1 | 2190 |

Paired per-household difference against `last_seen_no_model` (points; households with the method present and a non-empty slice):

| method | n households | mean | SE | 2 SE | per household |
|---|---:|---:|---:|---:|---|
| ACE_as_published | 3 | -1.3 | 0.6 | 1.1 | s2:-2 s32:-0 s48:-1 |
| incremental_edits | 3 | -5.6 | 5.9 | 11.9 | s2:-1 s32:-17 s48:+2 |
| ours_told_the_night_before | 3 | +1.5 | 1.1 | 2.2 | s2:+0 s32:+0 s48:+4 |
| the_log_and_notes_about_the_routine | 3 | +1.7 | 1.3 | 2.7 | s2:+0 s32:+1 s48:+4 |
| most_frequent_offline | 3 | -7.9 | 1.5 | 3.0 | s2:-11 s32:-7 s48:-6 |

## 4 (room level). Rare-move questions per household and the detectable gap

| household | rare-move questions |
|---|---:|
| hh_s2_t03 | 0 |
| hh_s32_t03 | 1 |
| hh_s48_t03 | 0 |

Best method on the rare-move slice by pooled first guess right (ties all listed): `ours_told_the_night_before` (100.0%). Paired against `last_seen_no_model` over 1 households with a non-empty slice: mean +0.0, SE –, 2 SE –. (The paired table under 3(a) has every method.)

Best method on the rare-move slice by pooled first guess right (ties all listed): `the_log_and_notes_about_the_routine` (100.0%). Paired against `last_seen_no_model` over 1 households with a non-empty slice: mean +0.0, SE –, 2 SE –. (The paired table under 3(a) has every method.)

## Notes on this wave

- true_room in last_seen's searches.jsonl agrees with the bank on all but 0 rows.
