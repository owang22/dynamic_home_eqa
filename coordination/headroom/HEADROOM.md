# Headroom: best simple rule against what the robot's own record could reach

Computed by `headroom.py` beside this file; charts `summary.png` and `study1.png` to `study4.png`, numbers `summary.json` and `study1.json` to `study4.json`. CPU only, no model run.

## Summary: gap from the best simple rule to the loose record ceiling

One row per setup and slice, as in `summary.png`. Gap = loose ceiling minus best rule, in points of first guess right (study 3: found within a budget of 60). Interval = 2.5th to 97.5th percentile of the gap under a bootstrap over households (10000 draws); for study 3's one household it is a paired bootstrap over its 67 questions, with the pairing reconstructed from the printed counts (rule 30 found, ceiling 36; the paired section's 12 discordant over all 155 findable with net 0 and towels 88 against 82 leave the 6 non-towel discordant questions all in the ceiling's favour).

| setup and slice | best rule | best rule, percent | loose ceiling | gap | interval | interval over | n questions | n households |
|---|---|---|---|---|---|---|---|---|
| Study 1, return windows (days 24-28 and 42-46) | last-seen | 88.2 | 100.0 | +11.8 | [+8.8, +13.8] | households | 720 | 3 |
| Study 1, ill days, mover questions | last-seen | 73.8 | 81.4 | +7.7 | [+4.7, +10.4] | households | 652 | 3 |
| Study 3, non-towel things, found within budget 60 | last seen (kind, then nearest) | 44.8 | 53.7 | +8.9 | [+3.0, +16.4] | questions | 67 | 1 |
| Study 4, first question after each move | alternate room | 44.2 | 55.8 | +11.6 | [+5.3, +18.0] | households | 86 | 10 |
| Study 4, car keys, first question after the move | alternate room | 45.5 | 57.6 | +12.1 | [+4.5, +19.7] | households | 66 | 10 |
| Study 4, pill box forward move, first question after it | all four rules 0 | 0.0 | 0.0 | +0.0 | [+0.0, +0.0] | households | 10 | 10 |
| Study 4, ordinary questions | same time of day | 85.1 | 95.6 | +10.5 | [+8.5, +12.5] | households | 2480 | 10 |

Reading check, record plus notes on days 24-28 (mean over the three households per day): day 24: 84.7, day 25: 83.3, day 26: 94.4, day 27: 93.1, day 28: 91.7; mean of the five days 89.4, pooled over the 360 questions 89.4 (equal n per day, so the two agree). Days 26-28 are 94.4, 93.1 and 91.7; days 24 and 25 are 84.7 and 83.3, which pull the window mean down.

Definitions, stated once. First guess right = `found_at_step == 1` on a search row (room level). Loose ceiling = the true room at question time is a room in which the robot had itself sighted that object at an earlier time. Routine ceiling = the true room is the room of the object's most recent earlier sighting, or the object was sighted in the true room on an earlier day within one hour of the same time of day. Both ceilings use the last-seen cell's own looks, and only sightings strictly before the question's time (a few questions share a time stamp with another question; sightings from that other search are not counted, which costs the ceilings at most one question in 3528 in study 1). Check made: in study 1, of the 3079 questions last-seen gets right, 3078 have loose ceiling 1 and one is a guess with no record. Headroom = ceiling minus the best simple rule on the same questions. Study 3 uses its own, already computed, ceiling (oracle among remembered places, then last-seen's exploration) and score (found within budget).

## Study 1, memory through a shift and back (three households, 49 days, 24 questions a day)

Last-seen is the only simple rule in this run, so it is the best rule. The ceilings are from the last-seen cell's looks; the last two columns give the same ceilings from the notes arm's own looks, because that arm's searches open different rooms and so its record differs.

| questions | last-seen (best rule) | record plus notes | loose ceiling | routine ceiling | headroom, loose | headroom, routine | n questions | n households | loose ceiling from the notes arm's looks | routine, same |
|---|---|---|---|---|---|---|---|---|---|---|
| days 24-28 | 89.7 | 89.4 | 100.0 | 100.0 | 10.3 | 10.3 | 360 | 3 | 99.7 | 99.7 |
| days 42-46 | 86.7 | 94.2 | 100.0 | 100.0 | 13.3 | 13.3 | 360 | 3 | 99.7 | 99.7 |
| days 24-28 and 42-46 | 88.2 | 91.8 | 100.0 | 100.0 | 11.8 | 11.8 | 720 | 3 | 99.7 | 99.7 |
| days 24-28, movers | 82.7 | 83.2 | 100.0 | 100.0 | 17.3 | 17.3 | 191 | 3 | 100.0 | 100.0 |
| days 42-46, movers | 75.6 | 88.4 | 100.0 | 100.0 | 24.4 | 24.4 | 172 | 3 | 100.0 | 100.0 |
| days 24-28 and 42-46, movers | 79.3 | 85.7 | 100.0 | 100.0 | 20.7 | 20.7 | 363 | 3 | 100.0 | 100.0 |
| ill days 14-23 and 32-41 | 86.6 | 93.5 | 91.6 | 91.4 | 5.0 | 4.8 | 1440 | 3 | 98.3 | 98.0 |
| ill days, movers | 73.8 | 88.0 | 81.4 | 81.0 | 7.7 | 7.2 | 652 | 3 | 96.9 | 96.2 |
| all days 1-49 | 87.3 | 91.5 | 95.1 | 94.6 | 7.9 | 7.3 | 3528 | 3 | 98.2 | 97.6 |
| all days, movers | 77.8 | 85.6 | 91.3 | 90.3 | 13.6 | 12.6 | 1717 | 3 | 97.5 | 96.3 |

Per household, days 24-28 and 42-46 pooled (right / n): hh_s2_t03: last-seen 209, notes 220, loose 240, routine 240 of 240; hh_s32_t03: last-seen 219, notes 224, loose 240, routine 240 of 240; hh_s48_t03: last-seen 207, notes 217, loose 240, routine 240 of 240.

Mean daily gap to the loose ceiling, by stretch of days: settled 1-13 8.0, ill 14-23 4.6, return 24-31 8.7, ill 32-41 5.4, return 42-49 13.9 points. To the routine ceiling: 6.5, 4.3, 8.7, 5.3, 13.7. Largest single-day gaps to the loose ceiling: day 25 (17), day 48 (17), day 49 (17), day 42 (15), day 7 (15).

Note. The headroom sits in the two return windows and on the mover questions there: in days 24-28 and 42-46 pooled both ceilings are 100.0 (every asked object had been sighted in its settled room before the illness) while last-seen is 88.2 on all questions and 79.3 on the 363 mover questions, so the gap is 11.8 and 20.7 points; during the ill days the ceilings themselves fall (loose 91.6, routine 91.4 against last-seen 86.6), so the gap there is 5.0 points. The record-plus-notes method is above the last-seen-record loose ceiling on 14 of 49 days (days 1, 15, 16, 17, 18, 20, 22, 23, 34, 35, 36, 37, 38, 39), which is possible because that arm opens different rooms and so holds a different record, and on day 1 because a guess with no record can still be right; by its own looks its loose ceiling on the ill days is 98.3.

## Study 2, noticing a routine changed (ten households, 31 days, change on day 14)

This setup scores detection, not first guess right, so the headroom here is visibility: whether the robot's own record contains the change at all. Movers are the objects flagged `is_a_mover` on the search rows; a mover's new room is a room it truly occupies on days 14-23 and never on days 1-13 (bank truth rows; on-person and out-of-house excluded). Residents do appear in `looks.jsonl` (`residents_seen`, a list of names on each look, the room being the look's target), so the ill resident (resident 1 in every bank) is reported too.

| household | movers | with a new room | seen in a new room by day 14 | by day 16 | by day 18 | by day 23 | by day 31 | with a new place | seen at a new place by day 23 | ill resident sightings days 1-13 | days 14-23 | share out of routine by day 23 | same measure on days 1-13 (leave one out) | seen in bedroom 09-17 by day 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 8 | 3 | 33.3 | 33.3 | 100.0 | 100.0 | 100.0 | 5 | 100.0 | 64 | 23 | 69.6 | 1.6 | yes |
| hh_s19_t03 | 7 | 3 | 33.3 | 100.0 | 100.0 | 100.0 | 100.0 | 5 | 100.0 | 22 | 21 | 90.5 | 9.1 | yes |
| hh_s20_t03 | 8 | 3 | 33.3 | 66.7 | 66.7 | 100.0 | 100.0 | 6 | 83.3 | 66 | 32 | 75.0 | 0.0 | yes |
| hh_s32_t03 | 8 | 5 | 60.0 | 60.0 | 60.0 | 100.0 | 100.0 | 6 | 83.3 | 67 | 24 | 58.3 | 3.0 | no |
| hh_s48_t03 | 6 | 4 | 50.0 | 100.0 | 100.0 | 100.0 | 100.0 | 6 | 83.3 | 28 | 23 | 78.3 | 7.1 | yes |
| hh_s63_t03 | 9 | 5 | 0.0 | 40.0 | 100.0 | 100.0 | 100.0 | 8 | 62.5 | 36 | 22 | 77.3 | 0.0 | no |
| hh_s93_t03 | 9 | 6 | 50.0 | 100.0 | 100.0 | 100.0 | 100.0 | 7 | 100.0 | 67 | 36 | 83.3 | 3.0 | yes |
| hh_s109_t03 | 6 | 3 | 0.0 | 0.0 | 100.0 | 100.0 | 100.0 | 5 | 100.0 | 12 | 15 | 73.3 | 8.3 | no |
| hh_s123_t03 | 4 | 2 | 0.0 | 50.0 | 100.0 | 100.0 | 100.0 | 4 | 100.0 | 22 | 30 | 63.3 | 0.0 | yes |
| hh_s151_t03 | 7 | 5 | 40.0 | 60.0 | 60.0 | 60.0 | 60.0 | 6 | 66.7 | 18 | 18 | 66.7 | 27.8 | yes |
| mean | | | 30.0 | 61.0 | 88.7 | 96.0 | 96.0 | | 87.9 | | | 73.6 | 6.0 | 7 of 10 |

| day | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 27 | 31 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mean share of movers seen in a new room, percent | 30.0 | 44.3 | 61.0 | 75.3 | 88.7 | 92.0 | 96.0 | 96.0 | 96.0 | 96.0 | 96.0 | 96.0 |
| mean share of movers seen at a new place, percent | 32.4 | 42.5 | 59.3 | 71.6 | 79.6 | 84.6 | 87.9 | 87.9 | 87.9 | 87.9 | 87.9 | 87.9 |

Note. Of 72 flagged movers over the ten households, 33 have no room-level new room (they move within a room or to a place they also used on settled days); the room-level shares are over the rest. By the end of day 14 the robot has seen on average 30 percent of the movers in a new room, by day 16 61 percent and by day 23 96 percent, so the days on which the record does not yet hold the change are 14 to about 17. For the ill resident, 74 percent of sightings on days 14-23 are out of routine against 6 percent for the settled days judged the same way, and 7 of 10 households have a daytime bedroom sighting of them by day 16.

## Study 3, costly looks (one household, 248 searches; found within budget, of findable non-towel things)

Numbers are read from `coordination/studies/study3_costly_looks/gate_oracle_within_memory.txt` (the 'within the budget' tables, column 3) and checked against `dry_run_fake_nearest.txt` on every shared row. Here the ceiling is the study's own: an oracle choosing among remembered places, then last-seen's exploration when memory has nothing; the plain oracle is 100.

| budget | best rule | best rule, percent | ceiling (oracle within memory, then last seen) | headroom | plain oracle | last seen (nearest) | floor: oracle within memory only | n questions | n households |
|---|---|---|---|---|---|---|---|---|---|
| 30 | same time of day (nearest) | 35.8 | 38.8 | 3.0 | 100 | 31.3 | 6.0 | 67 | 1 |
| 60 | last seen (kind, then nearest) | 44.8 | 53.7 | 8.9 | 100 | 41.8 | 6.0 | 67 | 1 |
| 120 | last seen (kind, then nearest) | 53.7 | 61.2 | 7.5 | 100 | 52.2 | 6.0 | 67 | 1 |

Note. The gap between the best rule and the record-reachable ceiling is 3.0, 8.9 and 7.5 points at budgets 30, 60 and 120, while the gap to the plain oracle is 64, 55 and 46 points. On all findable things (towels included, n = 155) the ceiling is 69.7, 76.1, 83.2 against the rule that is best on that count, 67.1 (most frequent (kind, then nearest)), 76.1 (last seen (kind, then nearest)), 80.0 (last seen (kind, then nearest)).

## Study 4, rare things that matter (ten households, 32 days, 8 ordinary questions a day plus the rare-mover questions)

Slices as in `score_rare_movers.py`. For the rules, unseen and seen are each arm's own slices (its looks decide them); the ceilings' unseen and seen are the last-seen cell's, so the n shown is the last-seen cell's.

| slice | last-seen | most frequent | same time of day | alternate room | best rule | loose ceiling | routine ceiling | headroom, loose | headroom, routine | n questions (last-seen cell) | n households |
|---|---|---|---|---|---|---|---|---|---|---|---|
| first question after each move | 3.5 (3/86) | 33.7 (29/86) | 32.6 (28/86) | 44.2 (38/86) | alternate room | 55.8 | 50.0 | 11.6 | 5.8 | 86 | 10 |
| unseen | 0.5 (1/190) | 14.8 (28/189) | 13.6 (26/191) | 21.0 (39/186) | alternate room | 23.7 | 21.1 | 2.7 | 0.1 | 190 | 10 |
| after a miss | 0.9 (1/107) | 0.9 (1/106) | 0.9 (1/109) | 1.0 (1/103) | alternate room | 0.0 | 0.0 | -1.0 | -1.0 | 107 | 10 |
| seen | 100.0 (393/393) | 50.0 (197/394) | 45.2 (177/392) | 2.5 (10/397) | last-seen | 100.0 | 100.0 | 0.0 | 0.0 | 393 | 10 |
| background | 97.8 (405/414) | 72.7 (301/414) | 70.5 (292/414) | 31.9 (132/414) | last-seen | 97.6 | 97.6 | -0.2 | -0.2 | 414 | 10 |
| ordinary | 81.0 (2009/2480) | 75.3 (1867/2480) | 85.1 (2111/2480) | 63.7 (1579/2480) | same time of day | 95.6 | 93.9 | 10.5 | 8.8 | 2480 | 10 |
| pill box, forward (first question) | 0.0 (0/10) | 0.0 (0/10) | 0.0 (0/10) | 0.0 (0/10) | last-seen | 0.0 | 0.0 | 0.0 | 0.0 | 10 | 10 |
| pill box, return (first question) | 20.0 (2/10) | 100.0 (10/10) | 90.0 (9/10) | 80.0 (8/10) | most frequent | 100.0 | 100.0 | 0.0 | 0.0 | 10 | 10 |
| car keys (first question) | 1.5 (1/66) | 28.8 (19/66) | 28.8 (19/66) | 45.5 (30/66) | alternate room | 57.6 | 50.0 | 12.1 | 4.5 | 66 | 10 |

Note. On the first question after each of the 86 moves the best rule (alternate room) is 44.2 and the loose ceiling 55.8, the routine ceiling 50.0; on the unseen slice the loose ceiling is 23.7 against the best rule 21.0, and on the seen slice 100.0 against 100.0. The pill box forward move has a loose ceiling of 0 (the bedside had never been sighted holding it) and the return move 100; the car keys 58. The small negative headrooms on 'after a miss' and 'background' come from each rule being scored on its own slice while the ceiling uses the last-seen cell's; they are within one question.

## Files

- coordination/headroom/headroom.py
- coordination/headroom/HEADROOM.md
- coordination/headroom/summary.png
- coordination/headroom/summary.json
- coordination/headroom/study1.png
- coordination/headroom/study1.json
- coordination/headroom/study2.png
- coordination/headroom/study2.json
- coordination/headroom/study3.png
- coordination/headroom/study3.json
- coordination/headroom/study4.png
- coordination/headroom/study4.json
