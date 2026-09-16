# Log reader reasoning · hh_001__bank0

Each answer's `why` is tagged by regular expressions (see the module docstring); one why can carry several kinds. Shares are of answered questions (questions whose reply was invalid have no why).

## log reader (one LLM call per decision) (`active__log_reader__named__f0`)

2254 answer decisions, 529 looks, 119 invalid replies (fallback answer used), 0 notes written, 48.6 M prompt tokens.

### What the reasoning talks about

| kind | answers | share | right when present |
|---|---|---|---|
| last seen | 2012 | 89% | 0.78 |
| routine | 449 | 20% | 0.93 |
| empty look | 376 | 17% | 0.67 |
| away | 49 | 2% | 0.55 |
| unseen object | 66 | 3% | 0.61 |
| none | 134 | 6% | 0.31 |

### How far back in the log the reasoning reaches

| oldest day cited | answers | share |
|---|---|---|
| no day cited | 154 | 7% |
| same day | 1331 | 59% |
| 1 day back | 474 | 21% |
| 2–6 days back | 262 | 12% |
| 7+ days back | 33 | 1% |

### By outcome

| outcome | n | last seen | routine | empty look | away | unseen object | none |
|---|---|---|---|---|---|---|---|
| right | 1692 | 93% | 25% | 15% | 2% | 2% | 2% |
| missed away | 233 | 79% | 3% | 24% | 5% | 2% | 18% |
| missed carried | 23 | 74% | 4% | 35% | 0% | 0% | 26% |
| false away | 11 | 27% | 0% | 18% | 82% | 73% | 0% |
| wrong room | 136 | 76% | 10% | 15% | 1% | 9% | 15% |
| right room, wrong spot | 159 | 86% | 5% | 23% | 0% | 1% | 14% |

### When the truth is OUT_OF_HOUSE

241 questions, 8 right; the reasoning mentions leaving / carrying / absence in 17 of them. What it answered instead: kitchen_table_k1 (65), entry_table_e1 (38), nightstand_b1 (17), entry_hook_e1 (16), sink_k1 (16), chair_k1 (15).

### Why it looked

| reason | looks |
|---|---|
| object never seen: guess a spot | 202 |
| confirm the last-seen spot | 135 |
| last spot was empty: try the next | 114 |
| other | 78 |

Most looked-at: sink_k1 (114), kitchen_table_k1 (74), counter_k1 (56), bathroom_shelf_ba1 (47), dish_rack_k1 (47), entry_table_e1 (38).

### Sampled reasonings

**right** (1672)

- day 12 24 h, wallet_mara → **towel_rack_ba1** (truth towel_rack_ba1): The last confirmed sighting of wallet_mara was at towel_rack_ba1 on d12 Sat 11:03. It has not been seen in any other location since, and no logs indicate it was moved. While it has historically been found in the entry area and kitchen, the most recent evidence points to the bathroom towel rack.
- day 26 12 h, blanket_mara → **couch_l1** (truth couch_l1): The most recent sighting of blanket_mara is at d26 Sat 08:10 on couch_l1. It has been consistently found on the couch in recent days (d25 Fri 08:20, d24 Thu 12:41, etc.) and there is no evidence of it moving since the morning check.
- day 14 6 h, umbrella_mara → **entry_floor_e1** (truth entry_floor_e1): The umbrella has been consistently found at entry_floor_e1 in every recent check (d13 Sun 11:09, d12 Sat 14:04, d11 Fri 14:32, d10 Thu 19:16, d09 Wed 22:15). There is no evidence of it moving to another location, and it is not listed in any other receptacle in the recent logs.
- day 1 22 h, makeup_kit_mara → **bathroom_shelf_ba1** (truth bathroom_shelf_ba1): The most recent sighting of makeup_kit_mara was at d01 Tue 18:43, when the robot looked inside bathroom_shelf_ba1 and found it there. No subsequent events in the log indicate it has been moved, and it is a stable object typically kept in the bathroom. Therefore, it is most likely still at bathroom_s

**missed away** (190)

- day 10 11 h, jacket_mara → **chair_k1** (truth OUT_OF_HOUSE): The most recent sighting of jacket_mara is at chair_k1 at d10 Thu 11:10, which is the exact time of the question. The log confirms the robot just looked at chair_k1 and found the jacket there.
- day 21 15 h, headphones_mara → **couch_l1** (truth OUT_OF_HOUSE): The most recent sighting of headphones_mara was on d21 Mon 06:23 at couch_l1. It has not been seen in any other location since then, and no logs from d21 Mon 06:23 to d21 Mon 15:01 indicate it has moved. Therefore, it is most likely still at couch_l1.
- day 21 8 h, phone_mara → **nightstand_b1** (truth OUT_OF_HOUSE): The most recent sighting of phone_mara was at nightstand_b1 on d20 Sun 15:02 and again at d20 Sun 22:20. It has not been seen in any other location since then, and the bedroom was checked at d20 Sun 22:20 (nightstand_b1 had it) and d21 Mon 05:13 (entry_hook was empty, but bedroom wasn't re-checked).
- day 18 8 h, wallet_mara → **entry_table_e1** (truth OUT_OF_HOUSE): The most recent confirmed sighting of wallet_mara was at entry_table_e1 on d16 Wed 22:11. Since then, the robot has not looked inside entry_table_e1, so it is the most likely current location. Other locations where it was previously seen (sink_k1, chair_k2, towel_rack_ba1) are less likely as they ha

**wrong room** (118)

- day 27 15 h, mug_mara → **kitchen_table_k1** (truth coffee_table_l1): The last confirmed sighting of mug_mara was at coffee_table_l1 on d26 Sat 22:14. Since then, it has not appeared in any of the recent kitchen sweeps (d27 Sun 08:21, 13:48) or other checked locations. Given its frequent presence in the kitchen area (counter, sink, kitchen table) in the days prior, it
- day 26 12 h, umbrella_mara → **counter_k1** (truth entry_floor_e1): The most recent sighting of umbrella_mara is at counter_k1 on d26 Sat 07:23. It has not been seen elsewhere since then, and no later look of counter_k1 has reported it missing, making counter_k1 the most likely current location.
- day 26 16 h, glasses_mara → **kitchen_table_k1** (truth nightstand_b1): The most recent sighting of glasses_mara was at d26 Sat 12:57, where it was found in kitchen_table_k1. No later logs show it being moved, making kitchen_table_k1 the most likely current location.
- day 9 18 h, wallet_mara → **chair_k2** (truth entry_table_e1): The last confirmed sighting of wallet_mara was at chair_k2 on d08 Tue 19:22. It has not been seen in any subsequent looks of chair_k2 (d09 Wed 06:53, 15:54, 15:58) or other likely locations like the entry table or kitchen table. Since the budget is 0, I must answer based on the last known location,

**right room, wrong spot** (141)

- day 24 13 h, pen_mara → **kitchen_table_k1** (truth counter_k1): The most recent sighting of pen_mara was at d24 Thu 12:12 on counter_k1. Since then, the robot has only checked living room receptacles (12:41) and has not re-inspected the kitchen. It is most likely still on the counter, or has been moved to the nearby kitchen table, sink, or dish rack.
- day 18 19 h, notebook_mara → **kitchen_table_k1** (truth chair_k1): The last confirmed sighting of notebook_mara was at kitchen_table_k1 on d17 Thu 22:22. Since then, the robot has checked kitchen_table_k1 (d18 Fri 08:37 and 11:05) and it was not there, but it has not been seen in any other receptacle. It is possible it was moved to another kitchen surface like the
- day 12 22 h, hairbrush_mara → **bathroom_shelf_ba1** (truth towel_rack_ba1): The last confirmed sighting of hairbrush_mara was at d12 Sat 11:03 in bathroom_shelf_ba1. It was not present in the subsequent check of that same shelf at d12 Sat 21:20 (which showed headphones_mara, makeup_kit_mara, medication_bottle_mara). Since it is missing from its usual spot, it is likely near
- day 24 23 h, charger_mara → **sink_k1** (truth kitchen_table_k1): The last confirmed sighting of charger_mara was in sink_k1 at d24 Thu 05:27. It has not been seen in any other receptacle since then, and no later look of sink_k1 has reported it missing (the most recent sink look was d24 Thu 15:48, which showed pot_shared_1 and watering_can_mara, but did not list c

**false away** (11)

- day 0 20 h, laptop_mara → **OUT_OF_HOUSE** (truth kitchen_table_k1): The object 'laptop_mara' has never been seen in the log, nor was it present during the initial walkthrough. Since the robot has not detected it in any receptacle or on a person, and it was not part of the initial inventory, the most likely status is that it is not in the house.
- day 0 22 h, water_bottle_mara → **OUT_OF_HOUSE** (truth kitchen_table_k1): The object 'water_bottle_mara' has never appeared in the sighting log or in any 'look' results. Since the log is the only source of information and the object is not listed among the objects seen so far, it is most likely not in the house.
- day 6 13 h, jacket_mara → **OUT_OF_HOUSE** (truth bookshelf_l1): The last confirmed sighting of jacket_mara was at entry_hook_e1 on d04 Fri 19:31. It was not present at entry_hook_e1 on d05 Sat 18:55 or d06 Sun 10:29. It was last seen in the kitchen area (sink_k1) on d04 Fri 12:32. Given it has been missing from its usual spots for over a day and is a common item
- day 0 19 h, notebook_mara → **OUT_OF_HOUSE** (truth counter_k1): The object 'notebook_mara' has never been seen in the log, nor was it present during the initial walkthrough. Since the robot has not detected it in any receptacle or on a person, and it was not part of the initial inventory, the most likely status is that it is not in the house.

**missed carried** (17)

- day 15 22 h, keys_mara → **entry_table_e1** (truth ON_PERSON): The last confirmed sighting of keys_mara was at entry_table_e1 on d14 Mon 22:32. Since then, the entry table was checked on d15 Tue 18:16 and 18:58, and it was empty both times. The entry hook was checked at 18:58 and contained backpack_mara and charger_mara, but not keys_mara. Given the keys were l
- day 9 23 h, phone_mara → **kitchen_table_k1** (truth ON_PERSON): The last confirmed sighting of phone_mara was on d07 Mon 22:18 at kitchen_table_k1. It has not been seen in any subsequent logs, including the most recent kitchen sweep on d09 Wed 15:58 (where it was absent from the table) and the bedroom sweep on d09 Wed 11:54 (where the nightstand was empty). Give
- day 25 1 h, headphones_mara → **kitchen_table_k1** (truth ON_PERSON): The last confirmed sighting of headphones_mara was at kitchen_table_k1 on d23 Wed 19:08. It was not present in the subsequent kitchen_table_k1 look on d24 Thu 00:26, indicating it was moved. It has not been seen in any other receptacle since then. Given its recent history of being in the kitchen are
- day 5 18 h, jacket_mara → **sink_k1** (truth ON_PERSON): The most recent sighting of jacket_mara was at sink_k1 on d04 Fri 17:31. It has not been seen in any other location since then, and the sink_k1 has been checked multiple times since (d04 17:31, d05 08:38, d05 17:43) without the jacket appearing elsewhere. While it is possible it was moved, the last


## log reader, aided (`active__log_reader_aided__named__f0`)

2213 answer decisions, 637 looks, 153 invalid replies (fallback answer used), 0 notes written, 58.2 M prompt tokens.

### What the reasoning talks about

| kind | answers | share | right when present |
|---|---|---|---|
| last seen | 1883 | 85% | 0.75 |
| routine | 607 | 27% | 0.93 |
| empty look | 255 | 12% | 0.73 |
| away | 204 | 9% | 0.67 |
| unseen object | 87 | 4% | 0.75 |
| none | 204 | 9% | 0.43 |

### How far back in the log the reasoning reaches

| oldest day cited | answers | share |
|---|---|---|
| no day cited | 242 | 11% |
| same day | 1243 | 56% |
| 1 day back | 341 | 15% |
| 2–6 days back | 302 | 14% |
| 7+ days back | 85 | 4% |

### By outcome

| outcome | n | last seen | routine | empty look | away | unseen object | none |
|---|---|---|---|---|---|---|---|
| right | 1602 | 88% | 35% | 12% | 8% | 4% | 5% |
| missed away | 195 | 66% | 3% | 8% | 10% | 1% | 33% |
| missed carried | 22 | 73% | 0% | 9% | 9% | 0% | 27% |
| false away | 33 | 61% | 15% | 12% | 76% | 58% | 0% |
| carried/away swap | 1 | 0% | 0% | 0% | 100% | 0% | 0% |
| wrong room | 144 | 80% | 10% | 13% | 8% | 1% | 17% |
| right room, wrong spot | 216 | 89% | 6% | 13% | 4% | 0% | 10% |

### When the truth is OUT_OF_HOUSE

241 questions, 46 right; the reasoning mentions leaving / carrying / absence in 45 of them. What it answered instead: kitchen_table_k1 (57), OUT_OF_HOUSE (46), entry_table_e1 (31), nightstand_b1 (27), counter_k1 (23), sink_k1 (13).

### Why it looked

| reason | looks |
|---|---|
| confirm the last-seen spot | 274 |
| object never seen: guess a spot | 217 |
| last spot was empty: try the next | 82 |
| other | 64 |

Most looked-at: kitchen_table_k1 (190), sink_k1 (76), counter_k1 (62), entry_table_e1 (57), entry_hook_e1 (53), nightstand_b1 (48).

### Sampled reasonings

**right** (1548)

- day 13 21 h, plate_shared_2 → **kitchen_table_k1** (truth kitchen_table_k1): The most recent look at the kitchen table (d13 Sun 19:06) found plate_shared_2 there. The next look at that location (d13 Sun 19:50) also found it. No subsequent looks at the kitchen table have occurred, and the object has not been seen elsewhere since then. The kitchen table is its most frequent lo
- day 15 7 h, pen_mara → **kitchen_table_k1** (truth kitchen_table_k1): The most recent look at kitchen_table_k1 (d15 Tue 07:17) found pen_mara there. The current time is 07:28, only 11 minutes later, making it the most likely location. Other kitchen receptacles are secondary possibilities given the object's frequent movement within the kitchen area.
- day 2 5 h, laptop_mara → **kitchen_table_k1** (truth kitchen_table_k1): The most recent look at the laptop's usual place (kitchen_table_k1) at d02 Wed 04:26, just 29 minutes before the question, explicitly found laptop_mara there. No subsequent events suggest it has moved. The weekday stats (0 found / 5 not found during 9-17) are irrelevant to the current 4:55 AM time a
- day 9 14 h, pan_shared_1 → **kitchen_table_k1** (truth kitchen_table_k1): The most recent look at the kitchen table (d09 Wed 14:03) found pan_shared_1 there. It has been consistently found at the kitchen table or sink in recent days, and the kitchen table is its designated 'usual place' with a high hit rate (19/53). No evidence suggests it has moved since 14:03.

**missed away** (132)

- day 27 8 h, keys_mara → **entry_table_e1** (truth OUT_OF_HOUSE): The most recent look at entry_table_e1 at d27 Sun 08:28 (just 4 minutes before 'now') found only bowl_shared_1, meaning keys_mara is not there. However, keys_mara is frequently seen at entry_table_e1 (29/35 weekday looks) and was last seen there at d26 Sat 16:38. It is also often found at entry_hook
- day 25 12 h, backpack_mara → **chair_k1** (truth OUT_OF_HOUSE): The backpack is frequently seen at chair_k1 (e.g., d10, d11, d12, d13, d14, d17, d22) and dish_rack_k1 (e.g., d22, d23). It was last seen at entry_hook_e1 on d19, but the hook has been empty in recent checks (d21, d22, d23, d24, d25). Given the high frequency of sightings at chair_k1 and dish_rack_k
- day 23 10 h, notebook_mara → **kitchen_table_k1** (truth OUT_OF_HOUSE): The most recent sighting of notebook_mara was at kitchen_table_k1 on d22 Tue 20:06. It was not present in the kitchen_table_k1 look at d23 Wed 06:10, but it was found at coffee_table_l1 at d23 Wed 09:36 (the current time). Since the question asks where it is 'right now' and the log entry for the cur
- day 18 12 h, keys_mara → **entry_table_e1** (truth OUT_OF_HOUSE): The most recent look at entry_table_e1 (d18 Fri 11:53) found bowl_shared_1 but not keys_mara. However, keys_mara was last seen at entry_table_e1 on d18 Fri 09:31. It is common for keys to be moved to the entry_hook_e1 or left on a chair near the entry. Given the high frequency of keys being at entry

**wrong room** (124)

- day 27 18 h, tablet_mara → **tv_stand_l1** (truth counter_k1): The last time tablet_mara was seen was on d27 Sun 08:21 at chair_k1. It has not been seen since. On d25 Fri 11:46 it was also at chair_k1. On d24 Thu 15:48 it was at chair_k1. It has a strong recent history of being at chair_k1. However, on d26 Sat 22:14, the living room was checked and the tablet w
- day 17 16 h, jacket_mara → **entry_hook_e1** (truth chair_k1): The most recent sighting of jacket_mara was at entry_hook_e1 at d17 Thu 07:11. Although the entry hook was empty at 12:54, the jacket is a common item to be carried on the person or moved to a chair when the resident is home. Given the high frequency of it being out or on the person (low found count
- day 13 19 h, towel_mara → **towel_rack_ba1** (truth bedroom_floor_b1): The most recent sighting of towel_mara was at d13 Sun 13:54 in bedroom_floor_b1. However, its usual place is towel_rack_ba1, where it was found in 10 of 21 weekday daytime looks and never found missing when checked. The move to the bedroom floor on Saturday and Sunday suggests it may have been used
- day 19 24 h, headphones_mara → **kitchen_table_k1** (truth coffee_table_l1): The last time headphones_mara was seen was on d19 Sat 13:25 at kitchen_table_k1. It has not been seen in any other location since then. While it has been found in other places like the bathroom shelf and entry hook in the past, the most recent sighting is the strongest indicator of its current locat

**right room, wrong spot** (204)

- day 11 16 h, charger_mara → **kitchen_table_k1** (truth cupboard_k1): The charger was last seen at kitchen_table_k1 on d10 Thu 04:38. Since then, the robot has looked at kitchen_table_k1 multiple times (most recently d11 Fri 15:37) and the charger is no longer there. It has also been checked at counter_k1 (d11 Fri 15:38), sink_k1 (d11 Fri 14:57), and cupboard_k1 (d11
- day 18 14 h, mug_mara → **kitchen_table_k1** (truth counter_k1): The most recent sighting of mug_mara was at counter_k1 at d18 Fri 09:07. However, the kitchen table has been checked multiple times since then (11:25, 11:41, 11:44) and mug_mara was not present. The counter was checked at 13:25 (11 minutes ago) and mug_mara was present. Given the short time elapsed
- day 8 17 h, laptop_mara → **kitchen_table_k1** (truth chair_k1): The most recent look at the kitchen table (d08 Tue 16:40) found the laptop there. Although it has been missing from its usual spot during weekday daytime hours (suggesting it might be out of the house or in a less frequent location like the bookshelf), the direct sighting at the current time is the
- day 13 19 h, hairbrush_mara → **bathroom_shelf_ba1** (truth towel_rack_ba1): The most recent look at the hairbrush's usual place, bathroom_shelf_ba1, was at d13 Sun 08:19 and found it there. The next look at that receptacle was at d13 Sun 10:11 (towel_rack_ba1, which found the hairbrush), but the bathroom shelf was not re-inspected after 08:19. Given its high frequency of be

**false away** (33)

- day 1 16 h, charger_mara → **OUT_OF_HOUSE** (truth kitchen_table_k1): The object 'charger_mara' has never appeared in the log, including the initial walkthrough. Since it was not present in the house at the start of the log and has not been seen since, it is most likely out of the house (e.g., with a resident at work or school).
- day 0 22 h, water_bottle_mara → **OUT_OF_HOUSE** (truth kitchen_table_k1): The object 'water_bottle_mara' has never appeared in the sighting log or in any of the recorded looks. Since the log is the only source of information and the object is not present in any known receptacle, it is most likely out of the house.
- day 2 6 h, backpack_mara → **OUT_OF_HOUSE** (truth entry_hook_e1): The object 'backpack_mara' has never appeared in the log, including the initial walkthrough. Since it is not in the list of objects seen so far and has no recorded sightings, it is most likely out of the house with a resident.
- day 1 16 h, phone_mara → **OUT_OF_HOUSE** (truth cupboard_k1): The object 'phone_mara' has never appeared in the log, including the initial walkthrough. According to the rules, an object that is out of the house is invisible to every look and is missing from the walkthrough. Since the robot has never seen it, it is most likely out of the house with a resident.

**missed carried** (18)

- day 19 12 h, keys_mara → **entry_table_e1** (truth ON_PERSON): The most recent look at entry_table_e1 at d19 Sat 11:46 explicitly listed keys_mara inside it. This is direct, current evidence of its location.
- day 5 19 h, jacket_mara → **entry_hook_e1** (truth ON_PERSON): The most recent sighting of jacket_mara was at entry_hook_e1 at d05 Sat 17:43. It was last seen at kitchen_table_k1 on d02 Wed 16:34 and sink_k1 on d03 Thu 18:24. Given the recency of the entry hook sighting and the fact that it is a common place for jackets to be hung, entry_hook_e1 is the most lik
- day 5 18 h, jacket_mara → **entry_hook_e1** (truth ON_PERSON): The most recent look at entry_hook_e1 at d05 Sat 17:43 (the exact current time) found jacket_mara there. This is direct, up-to-date evidence. The object was also seen at entry_hook_e1 on d04 Fri 19:31 and d03 Thu 08:59, making it a plausible location, though it has been absent from its 'usual' kitch
- day 24 21 h, headphones_mara → **kitchen_table_k1** (truth ON_PERSON): The last time headphones_mara was seen was on d23 Wed 19:08, where it was found in chair_k1. Since then, the robot has not looked inside chair_k1. However, the object's usual place is kitchen_table_k1, where it has been seen frequently in the past (e.g., d22 Tue 22:12 in chair_k2, d20 Sun 10:22 in c

