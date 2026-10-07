# Slot summary — 54 households = 18 cells x 3 variants (seed 0, 2026-08-29)

## Merge notes

- night_shift_worker_solo (old hh_010) is working_professional_solo plus a night_shift overlay — merged into that overlay cell, not kept as an archetype.

## Proposed archetype additions (from the structural audit of the storyfirst 10)

- single_senior_solo: the base list has no single-senior home.
- multigenerational_family: the base list has no three-generation home.

## Overlay cells and why

- working_professional_solo__night_shift: the merged old night_shift_worker_solo; cleanest solo night signal
- working_couple_no_children__night_shift: one partner on nights, desync without children
- working_couple_no_children__opposite_schedules: the classic two-earner deliberate desync
- single_parent_teens__rotating_shift: rotating healthcare parent with self-managing teens: high routine variance plus dependents
- working_professional_solo__irregular_gig: solo gig worker: the most irregular single-resident signal
- college_roommates__irregular_gig: students with gig shifts: multi-resident irregularity

## Ruled-out archetype x overlay pairs

- retired_couple / single_senior_solo x any work overlay: nobody is employed; there is no schedule to overlay
- single_adult_wfh / remote_worker_couple x night_shift or opposite_schedules: remote work decouples work hours from leaving the house, so the overlay barely changes what a robot in the home observes
- researcher_household x any overlay: its schedule is already the irregular_academic condition; stacking another schedule double-treats one home
- college_roommates x rotating_shift: a fixed rotation implies stable shift employment, not believable for full-time students; irregular_gig covers them instead
- couple_with_toddler x opposite_schedules: believable (tag-team childcare) but not chosen: the toddler adds a second unusual signal and the overlay budget is 5-6 cells
- family_teen_and_child x night_shift: believable but not chosen for the same single-factor reason

## Households

| id | wave | cell | v | res | ages | r1 wake | r1 work | gen seed |
|---|---|---|---|---|---|---|---|---|
| hh_001 | pilot | working_professional_solo | 1 | 1 | 35 | 300 | 410-940 | 304154638 |
| hh_002 | hard5 | multigenerational_family | 1 | 5 | 78,42,42,14,8 | 360 | None-None | 907791554 |
| hh_003 | hard5 | single_parent_teens__rotating_shift | 1 | 3 | 51,16,16 | 330 | 390-960 | 1213262598 |
| hh_004 | hard5 | working_couple_no_children__night_shift | 1 | 2 | 31,36 | 360 | 401-945 | 762240036 |
| hh_005 | hard5 | working_couple_no_children__opposite_schedules | 1 | 2 | 31,40 | 300 | 425-945 | 157716008 |
| hh_006 | hard5 | working_professional_solo__irregular_gig | 1 | 1 | 30 | 300 | 400-400 | 201526753 |
| hh_007 | wave1 | college_roommates | 1 | 3 | 22,21,19 | 420 | None-None | 1156720620 |
| hh_008 | wave1 | college_roommates__irregular_gig | 1 | 3 | 19,21,21 | 360 | None-None | 565299404 |
| hh_009 | wave1 | couple_with_toddler | 1 | 3 | 34,29,2 | 360 | 500-900 | 1001741671 |
| hh_010 | wave1 | family_teen_and_child | 1 | 4 | 47,44,15,8 | 255 | 420-930 | 1068120953 |
| hh_011 | wave1 | remote_worker_couple | 1 | 2 | 41,42 | 360 | 420-900 | 657933162 |
| hh_012 | wave1 | researcher_household | 1 | 1 | 35 | 330 | 948-1290 | 1945759662 |
| hh_013 | wave1 | retired_couple | 1 | 2 | 77,78 | 360 | None-None | 1287894418 |
| hh_014 | wave1 | single_adult_wfh | 1 | 1 | 30 | 300 | 450-900 | 682628153 |
| hh_015 | wave1 | single_parent_teens | 1 | 3 | 50,14,15 | 330 | 395-900 | 1957296732 |
| hh_016 | wave1 | single_senior_solo | 1 | 1 | 82 | 330 | None-None | 1236269670 |
| hh_017 | wave1 | working_couple_no_children | 1 | 2 | 41,44 | 390 | 450-960 | 2078395046 |
| hh_018 | wave1 | working_couple_no_children | 2 | 2 | 27,27 | 330 | 425-1080 | 110674599 |
| hh_019 | wave1 | working_professional_solo | 2 | 1 | 29 | 390 | 453-900 | 291604999 |
| hh_020 | wave1 | working_professional_solo__night_shift | 1 | 1 | 43 | None | 1257-360 | 1402755819 |
| hh_021 | wave2 | college_roommates | 2 | 3 | 19,20,20 | 390 | None-None | 1073087898 |
| hh_022 | wave2 | college_roommates | 3 | 3 | 21,20,23 | 330 | None-None | 960753085 |
| hh_023 | wave2 | college_roommates__irregular_gig | 2 | 3 | 23,23,19 | 420 | None-None | 1015568207 |
| hh_024 | wave2 | college_roommates__irregular_gig | 3 | 3 | 22,21,23 | 390 | 910-935 | 206012189 |
| hh_025 | wave2 | couple_with_toddler | 2 | 3 | 39,36,2 | 330 | 390-900 | 40695967 |
| hh_026 | wave2 | couple_with_toddler | 3 | 3 | 39,28,2 | 360 | 420-990 | 1237741 |
| hh_027 | wave2 | family_teen_and_child | 2 | 4 | 48,45,15,8 | 390 | 480-1095 | 1394472761 |
| hh_028 | wave2 | family_teen_and_child | 3 | 4 | 40,49,17,7 | 390 | 540-1170 | 1239876988 |
| hh_029 | wave2 | multigenerational_family | 2 | 5 | 76,40,46,15,9 | 420 | None-None | 1750917190 |
| hh_030 | wave2 | multigenerational_family | 3 | 5 | 70,45,35,14,7 | 390 | None-None | 1068120953 |
| hh_031 | wave2 | remote_worker_couple | 2 | 2 | 37,28 | 360 | 420-900 | 1835152518 |
| hh_032 | wave2 | remote_worker_couple | 3 | 2 | 38,45 | 330 | 390-900 | 1911440703 |
| hh_033 | wave2 | researcher_household | 2 | 1 | 29 | None | 1290-1080 | 354079257 |
| hh_034 | wave2 | researcher_household | 3 | 1 | 35 | None | 930-180 | 345259570 |
| hh_035 | wave2 | retired_couple | 2 | 2 | 69,77 | 420 | None-None | 1541862789 |
| hh_036 | wave2 | retired_couple | 3 | 2 | 73,80 | 420 | None-None | 1563383377 |
| hh_037 | wave2 | single_adult_wfh | 2 | 1 | 38 | 315 | 365-900 | 1896339382 |
| hh_038 | wave2 | single_adult_wfh | 3 | 1 | 29 | 360 | 420-930 | 977582393 |
| hh_039 | wave2 | single_parent_teens | 2 | 3 | 46,16,14 | 390 | 415-990 | 110674599 |
| hh_040 | wave2 | single_parent_teens | 3 | 3 | 44,15,17 | 360 | 451-1095 | 1711154941 |
| hh_041 | wave2 | single_parent_teens__rotating_shift | 2 | 3 | 43,14,14 | 420 | 430-840 | 1094886520 |
| hh_042 | wave2 | single_parent_teens__rotating_shift | 3 | 3 | 48,14,15 | 270 | 475-1035 | 1533175664 |
| hh_043 | wave2 | single_senior_solo | 2 | 1 | 76 | 390 | None-None | 1946832091 |
| hh_044 | wave2 | single_senior_solo | 3 | 1 | 79 | 300 | None-None | 481412254 |
| hh_045 | wave2 | working_couple_no_children | 3 | 2 | 27,43 | 330 | 497-1050 | 284073755 |
| hh_046 | wave2 | working_couple_no_children__night_shift | 2 | 2 | 44,37 | 270 | 345-840 | 1927008121 |
| hh_047 | wave2 | working_couple_no_children__night_shift | 3 | 2 | 40,38 | 360 | 450-1050 | 397782113 |
| hh_048 | wave2 | working_couple_no_children__opposite_schedules | 2 | 2 | 44,32 | 360 | 473-1020 | 1547117794 |
| hh_049 | wave2 | working_couple_no_children__opposite_schedules | 3 | 2 | 33,42 | 300 | 415-960 | 1732548466 |
| hh_050 | wave2 | working_professional_solo | 3 | 1 | 28 | 360 | 465-990 | 1410807026 |
| hh_051 | wave2 | working_professional_solo__irregular_gig | 2 | 1 | 35 | None | 250-120 | 1502789247 |
| hh_052 | wave2 | working_professional_solo__irregular_gig | 3 | 1 | 40 | None | 245-870 | 1557233255 |
| hh_053 | wave2 | working_professional_solo__night_shift | 2 | 1 | 38 | None | 1080-360 | 393236267 |
| hh_054 | wave2 | working_professional_solo__night_shift | 3 | 1 | 42 | None | 1155-260 | 639825825 |

## What differs inside a cell

Across a cell's 3 variants only these change: the timing tuples (fresh ATUS draws), point ages within each band, the generation seed, and (at generation time) names and the specific job title inside the fixed occupation category.

## Group tags: households where the tag is the only unusual thing

- has_senior: 9
- has_teenagers: 9
- has_young_children: 9
- irregular_academic: 3
- irregular_gig: 6
- multigenerational: 3
- night_shift: 6
- opposite_schedules: 3
- rotating_shift: 3
- single_occupant: 12
- student_household: 3
- wfh_household: 6

## Tag overlap (households carrying both)

| | has_senior | has_teenagers | has_young_children | irregular_academic | irregular_gig | multigenerational | night_shift | opposite_schedules | rotating_shift | single_occupant | student_household | wfh_household |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| has_senior | (9) | 3 | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 3 | 0 | 0 |
| has_teenagers | 3 | (12) | 6 | 0 | 0 | 3 | 0 | 0 | 3 | 0 | 0 | 0 |
| has_young_children | 3 | 6 | (9) | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| irregular_academic | 0 | 0 | 0 | (3) | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| irregular_gig | 0 | 0 | 0 | 0 | (6) | 0 | 0 | 0 | 0 | 3 | 3 | 0 |
| multigenerational | 3 | 3 | 3 | 0 | 0 | (3) | 0 | 0 | 0 | 0 | 0 | 0 |
| night_shift | 0 | 0 | 0 | 0 | 0 | 0 | (6) | 0 | 0 | 3 | 0 | 0 |
| opposite_schedules | 0 | 0 | 0 | 0 | 0 | 0 | 0 | (3) | 0 | 0 | 0 | 0 |
| rotating_shift | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | (3) | 0 | 0 | 0 |
| single_occupant | 3 | 0 | 0 | 3 | 3 | 0 | 3 | 0 | 0 | (18) | 0 | 3 |
| student_household | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | (6) | 0 |
| wfh_household | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | (6) |

## ATUS group fallbacks (thin groups borrowed a neighbor)

- nonworking_adult|evening|15-24|weekday -> full_time|evening|15-24|weekday
- nonworking_adult|non_workday|under-15|weekday -> nonworking_adult|non_workday|15-24|weekday
- nonworking_adult|non_workday|under-15|weekend -> nonworking_adult|non_workday|15-24|weekend
- part_time|split_irregular|15-24|weekday -> full_time|split_irregular|15-24|weekday
- part_time|split_irregular|25-44|weekday -> full_time|split_irregular|25-44|weekday
