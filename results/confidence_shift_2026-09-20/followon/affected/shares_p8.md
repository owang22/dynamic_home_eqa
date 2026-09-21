# Affected share per day

20 households, 8960 questions. Affected = the object's location at question time was changed by a major event (guest_visit, sick_day: cause log), by a resident's weekend-only activity, or by the absence of the owner's routine weekday activity that uses the object (weekend template or sick-day removal).

## Pooled

| | Wed (d1) | Thu (d2) | Fri (d3) | Sat (d4) | Sun (d5) | Mon (d6) | Tue (d7) | all |
|---|---|---|---|---|---|---|---|---|
| **affected** (fresh event move, fresh weekend move, or stayed put) | 4% (55/1280) | 7% (90/1280) | 8% (107/1280) | 18% (227/1280) | 19% (239/1280) | 5% (70/1280) | 7% (91/1280) | 10% (879/8960) |
|   moved by a major event, any freshness (cause log) | 4% (52/1280) | 5% (65/1280) | 7% (91/1280) | 5% (61/1280) | 5% (65/1280) | 5% (70/1280) | 6% (77/1280) | 5% (481/8960) |
|   moved by a weekend activity, any freshness (per resident) | 0% (0/1280) | 0% (0/1280) | 0% (0/1280) | 11% (138/1280) | 12% (157/1280) | 2% (28/1280) | 1% (17/1280) | 4% (340/8960) |
|   absence of a routine activity | 3% (39/1280) | 4% (56/1280) | 4% (49/1280) | 6% (82/1280) | 8% (107/1280) | 3% (42/1280) | 4% (51/1280) | 5% (426/8960) |
| cause-log-only label (event or household weekend activity) | 4% (52/1280) | 5% (65/1280) | 7% (91/1280) | 10% (127/1280) | 10% (127/1280) | 6% (83/1280) | 7% (85/1280) | 7% (630/8960) |
| other event (not told; counted unaffected) | 0% (4/1280) | 1% (11/1280) | 2% (26/1280) | 2% (32/1280) | 5% (61/1280) | 3% (42/1280) | 3% (41/1280) | 2% (217/8960) |
| small cause (episode/mood; counted unaffected) | 3% (38/1280) | 1% (18/1280) | 3% (42/1280) | 2% (20/1280) | 2% (20/1280) | 2% (28/1280) | 1% (16/1280) | 2% (182/8960) |
| shift day | 25% (320/1280) | 40% (512/1280) | 35% (448/1280) | 100% (1280/1280) | 100% (1280/1280) | 30% (384/1280) | 30% (384/1280) | 51% (4608/8960) |
| kind: event_moved | 3% (36/1280) | 4% (53/1280) | 6% (77/1280) | 3% (44/1280) | 4% (45/1280) | 4% (51/1280) | 4% (55/1280) | 4% (361/8960) |
| kind: weekend_moved | 0% (0/1280) | 0% (0/1280) | 0% (0/1280) | 9% (121/1280) | 8% (104/1280) | 0% (0/1280) | 0% (0/1280) | 3% (225/8960) |
| kind: stayed_put | 1% (19/1280) | 3% (37/1280) | 2% (30/1280) | 5% (62/1280) | 7% (90/1280) | 1% (19/1280) | 3% (36/1280) | 3% (293/8960) |
| kind: after_shift | 1% (9/1280) | 1% (10/1280) | 1% (12/1280) | 3% (34/1280) | 6% (71/1280) | 4% (47/1280) | 3% (36/1280) | 2% (219/8960) |
| kind: other_event | 0% (4/1280) | 1% (11/1280) | 2% (21/1280) | 2% (32/1280) | 5% (60/1280) | 3% (42/1280) | 3% (40/1280) | 2% (210/8960) |
| kind: small_cause | 3% (38/1280) | 1% (17/1280) | 3% (42/1280) | 1% (17/1280) | 1% (16/1280) | 2% (26/1280) | 1% (14/1280) | 2% (170/8960) |
| kind: plain | 92% (1174/1280) | 90% (1152/1280) | 86% (1098/1280) | 76% (970/1280) | 70% (894/1280) | 86% (1095/1280) | 86% (1099/1280) | 84% (7482/8960) |

## Per household

| household | shift days | affected on shift days | on non-shift days | all | weekend activities seen | absent activities seen |
|---|---|---|---|---|---|---|
| hh_s10 | [4, 5] | 25% (32/128) | 0% (0/320) | 7% (32/448) | chores, cook_dinner, dinner, dust, gaming, lunch | commute_work, evening_tv, shift, snack |
| hh_s11 | [3, 4, 5, 7] | 21% (54/256) | 0% (0/192) | 12% (54/448) | dinner, play_guitar, wash_dishes | chores, errands, evening_tv, lunch, shift, snack, yoga |
| hh_s12 | [4, 5, 7] | 23% (45/192) | 0% (0/256) | 10% (45/448) | lunch | commute_work, evening_tv, yoga |
| hh_s13 | [1, 2, 4, 5] | 16% (41/256) | 0% (0/192) | 9% (41/448) | chores, lunch | commute_work, errands, evening_tv, snack |
| hh_s14 | [2, 3, 4, 5, 6] | 23% (74/320) | 0% (0/128) | 17% (74/448) | cook_dinner, dinner, evening_tv, wash_dishes | errands, lunch, shift |
| hh_s15 | [1, 2, 3, 4, 5] | 21% (68/320) | 0% (0/128) | 15% (68/448) | bake, chores, lunch, nap, shower | commute_work, evening_tv, gaming |
| hh_s16 | [4, 5, 6] | 24% (46/192) | 0% (0/256) | 10% (46/448) | bake, lunch, shower | commute_work |
| hh_s17 | [2, 4, 5, 6, 7] | 22% (71/320) | 0% (0/128) | 16% (71/448) | shower | classes, evening_tv, lunch, snack, study, walk |
| hh_s18 | [4, 5] | 9% (12/128) | 0% (0/320) | 3% (12/448) | chores, lunch, shower | commute_work |
| hh_s19 | [2, 3, 4, 5] | 14% (37/256) | 0% (0/192) | 8% (37/448) | dust, lunch, shower | commute_work, lunch, play_guitar, snack, work_session |
| hh_s20 | [1, 3, 4, 5] | 17% (44/256) | 0% (0/192) | 10% (44/448) | chores, dust, fix_something, lunch, shower | commute_work, evening_tv, lunch, read, work_session |
| hh_s21 | [4, 5] | 23% (30/128) | 0% (0/320) | 7% (30/448) | bake, chores, shower | classes, cook_dinner, evening_tv, read, yoga |
| hh_s22 | [3, 4, 5] | 25% (48/192) | 0% (0/256) | 11% (48/448) | cook_dinner, dinner, evening_tv, lunch, movie, read_living, wash_dishes | commute_work, shift, snack |
| hh_s23 | [4, 5, 6, 7] | 14% (37/256) | 0% (0/192) | 8% (37/448) | chores, cook_dinner, dinner, movie, shower | lunch_out, shift, snack, work_session |
| hh_s24 | [1, 2, 4, 5, 6] | 15% (48/320) | 0% (0/128) | 11% (48/448) | chores, shower | lunch, work_session |
| hh_s25 | [1, 4, 5] | 12% (23/192) | 0% (0/256) | 5% (23/448) | shower | lunch_out, work_session |
| hh_s26 | [2, 3, 4, 5, 6] | 16% (50/320) | 0% (0/128) | 11% (50/448) | chores, fix_something, lunch, shower | commute_work, gaming, lunch, work_session |
| hh_s27 | [4, 5] | 19% (24/128) | 0% (0/320) | 5% (24/448) | cook_dinner, dinner, evening_tv, read_living, wash_dishes | shift, snack |
| hh_s28 | [2, 4, 5, 7] | 14% (36/256) | 0% (0/192) | 8% (36/448) | chores, dust, lunch, shower | commute_work, evening_tv, lunch_out |
| hh_s29 | [4, 5, 7] | 31% (59/192) | 0% (0/256) | 13% (59/448) | bake, shower | gaming, journal, lunch, snack, work_session |

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
