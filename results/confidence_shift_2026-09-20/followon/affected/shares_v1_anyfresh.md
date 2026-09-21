# Affected share per day

20 households, 8960 questions. Affected = the object's location at question time was changed by a major event (guest_visit, sick_day: cause log), by a resident's weekend-only activity, or by the absence of the owner's routine weekday activity that uses the object (weekend template or sick-day removal).

## Pooled

| | Wed (d1) | Thu (d2) | Fri (d3) | Sat (d4) | Sun (d5) | Mon (d6) | Tue (d7) | all |
|---|---|---|---|---|---|---|---|---|
| **affected** (event, weekend activity or absence) | 5% (64/1280) | 8% (100/1280) | 9% (119/1280) | 20% (261/1280) | 24% (310/1280) | 9% (117/1280) | 10% (127/1280) | 12% (1098/8960) |
|   by major event (cause log) | 4% (52/1280) | 5% (65/1280) | 7% (91/1280) | 5% (61/1280) | 5% (65/1280) | 5% (70/1280) | 6% (77/1280) | 5% (481/8960) |
|   by weekend activity (per resident) | 0% (0/1280) | 0% (0/1280) | 0% (0/1280) | 11% (138/1280) | 12% (157/1280) | 2% (28/1280) | 1% (17/1280) | 4% (340/8960) |
|   by absence of a routine activity | 3% (39/1280) | 4% (56/1280) | 4% (49/1280) | 6% (82/1280) | 8% (107/1280) | 3% (42/1280) | 4% (51/1280) | 5% (426/8960) |
| cause-log-only label (event or household weekend activity) | 4% (52/1280) | 5% (65/1280) | 7% (91/1280) | 10% (127/1280) | 10% (127/1280) | 6% (83/1280) | 7% (85/1280) | 7% (630/8960) |
| other event (not told; counted unaffected) | 0% (4/1280) | 1% (11/1280) | 2% (26/1280) | 2% (32/1280) | 5% (61/1280) | 3% (42/1280) | 3% (41/1280) | 2% (217/8960) |
| small cause (episode/mood; counted unaffected) | 3% (38/1280) | 1% (18/1280) | 3% (42/1280) | 2% (20/1280) | 2% (20/1280) | 2% (28/1280) | 1% (16/1280) | 2% (182/8960) |
| shift day | 25% (320/1280) | 40% (512/1280) | 35% (448/1280) | 100% (1280/1280) | 100% (1280/1280) | 30% (384/1280) | 30% (384/1280) | 51% (4608/8960) |
| kind: event_moved | 4% (52/1280) | 5% (65/1280) | 7% (91/1280) | 5% (61/1280) | 5% (65/1280) | 5% (70/1280) | 6% (77/1280) | 5% (481/8960) |
| kind: weekend_moved | 0% (0/1280) | 0% (0/1280) | 0% (0/1280) | 11% (138/1280) | 12% (157/1280) | 2% (28/1280) | 1% (17/1280) | 4% (340/8960) |
| kind: stayed_put | 1% (12/1280) | 3% (35/1280) | 2% (28/1280) | 5% (62/1280) | 7% (88/1280) | 1% (19/1280) | 3% (33/1280) | 3% (277/8960) |
| kind: other_event | 0% (4/1280) | 1% (11/1280) | 2% (21/1280) | 2% (32/1280) | 5% (60/1280) | 3% (42/1280) | 3% (40/1280) | 2% (210/8960) |
| kind: small_cause | 3% (38/1280) | 1% (17/1280) | 3% (42/1280) | 1% (17/1280) | 1% (16/1280) | 2% (26/1280) | 1% (14/1280) | 2% (170/8960) |
| kind: plain | 92% (1174/1280) | 90% (1152/1280) | 86% (1098/1280) | 76% (970/1280) | 70% (894/1280) | 86% (1095/1280) | 86% (1099/1280) | 84% (7482/8960) |

## Per household

| household | shift days | affected on shift days | on non-shift days | all | weekend activities seen | absent activities seen |
|---|---|---|---|---|---|---|
| hh_s10 | [4, 5] | 28% (36/128) | 0% (0/320) | 8% (36/448) | chores, cook_dinner, dinner, dust, gaming, lunch | commute_work, evening_tv, shift, snack |
| hh_s11 | [3, 4, 5, 7] | 28% (71/256) | 2% (4/192) | 17% (75/448) | dinner, play_guitar, wash_dishes | chores, errands, evening_tv, lunch, shift, snack, yoga |
| hh_s12 | [4, 5, 7] | 29% (55/192) | 1% (2/256) | 13% (57/448) | lunch | commute_work, evening_tv, yoga |
| hh_s13 | [1, 2, 4, 5] | 18% (45/256) | 2% (4/192) | 11% (49/448) | chores, lunch | commute_work, errands, evening_tv, snack |
| hh_s14 | [2, 3, 4, 5, 6] | 25% (79/320) | 3% (4/128) | 19% (83/448) | cook_dinner, dinner, evening_tv, wash_dishes | errands, lunch, shift |
| hh_s15 | [1, 2, 3, 4, 5] | 22% (70/320) | 0% (0/128) | 16% (70/448) | bake, chores, lunch, nap, shower | commute_work, evening_tv, gaming |
| hh_s16 | [4, 5, 6] | 30% (58/192) | 0% (0/256) | 13% (58/448) | bake, lunch, shower | commute_work |
| hh_s17 | [2, 4, 5, 6, 7] | 23% (73/320) | 0% (0/128) | 16% (73/448) | shower | classes, evening_tv, lunch, snack, study, walk |
| hh_s18 | [4, 5] | 10% (13/128) | 0% (1/320) | 3% (14/448) | chores, lunch, shower | commute_work |
| hh_s19 | [2, 3, 4, 5] | 16% (42/256) | 4% (7/192) | 11% (49/448) | dust, lunch, shower | commute_work, lunch, play_guitar, snack, work_session |
| hh_s20 | [1, 3, 4, 5] | 21% (53/256) | 5% (10/192) | 14% (63/448) | chores, dust, fix_something, lunch, shower | commute_work, evening_tv, lunch, read, work_session |
| hh_s21 | [4, 5] | 29% (37/128) | 2% (8/320) | 10% (45/448) | bake, chores, shower | classes, cook_dinner, evening_tv, read, yoga |
| hh_s22 | [3, 4, 5] | 32% (61/192) | 1% (2/256) | 14% (63/448) | cook_dinner, dinner, evening_tv, lunch, movie, read_living, wash_dishes | commute_work, shift, snack |
| hh_s23 | [4, 5, 6, 7] | 19% (49/256) | 0% (0/192) | 11% (49/448) | chores, cook_dinner, dinner, movie, shower | lunch_out, shift, snack, work_session |
| hh_s24 | [1, 2, 4, 5, 6] | 17% (54/320) | 4% (5/128) | 13% (59/448) | chores, shower | lunch, work_session |
| hh_s25 | [1, 4, 5] | 12% (24/192) | 0% (1/256) | 6% (25/448) | shower | lunch_out, work_session |
| hh_s26 | [2, 3, 4, 5, 6] | 19% (61/320) | 3% (4/128) | 15% (65/448) | chores, fix_something, lunch, shower | commute_work, gaming, lunch, work_session |
| hh_s27 | [4, 5] | 23% (30/128) | 6% (18/320) | 11% (48/448) | cook_dinner, dinner, evening_tv, read_living, wash_dishes | shift, snack |
| hh_s28 | [2, 4, 5, 7] | 16% (42/256) | 2% (3/192) | 10% (45/448) | chores, dust, lunch, shower | commute_work, evening_tv, lunch_out |
| hh_s29 | [4, 5, 7] | 33% (64/192) | 3% (8/256) | 16% (72/448) | bake, shower | gaming, journal, lunch, snack, work_session |

## Weekend-affected placements by activity

| activity | questions |
|---|---|
| shower | 99 |
| lunch | 49 |
| chores | 35 |
| evening_tv | 32 |
| dust | 25 |
| dinner | 24 |
| bake | 19 |
| cook_dinner | 16 |
| movie | 12 |
| wash_dishes | 9 |
| gaming | 7 |
| read_living | 6 |
| fix_something | 4 |
| nap | 2 |
| play_guitar | 1 |

## Absence-affected questions by missing activity

| activity | questions |
|---|---|
| evening_tv | 97 |
| commute_work | 85 |
| work_session | 75 |
| lunch | 56 |
| snack | 54 |
| shift | 35 |
| classes | 28 |
| gaming | 22 |
| study | 12 |
| yoga | 10 |
| errands | 9 |
| lunch_out | 6 |
| read | 6 |
| cook_dinner | 5 |
| journal | 5 |
| play_guitar | 2 |
| chores | 1 |
| walk | 1 |
