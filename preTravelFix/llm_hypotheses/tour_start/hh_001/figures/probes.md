# Probes — hh_001

## 1. Is single-winner collapse warranted?

Log-loss per question (lower is better), from each particle's own distribution at question time.

| arm | mixture (actual weights) | uniform average | single best particle | per-day oracle pick | per-question oracle pick | day-best changes | median best-vs-2nd gap |
|---|---|---|---|---|---|---|---|
| llm_fixed · tour_named | 1.332 | 1.278 | 1.266 (hyp2) | 1.246 | 0.929 | 13/24 days | 0.043 |
| llm · tour_named | 1.347 | 1.346 | 1.319 (hyp2) | 1.308 | 1.000 | 13/24 days | 0.033 |
| llm_fixed · tour_anonymized | 1.331 | 1.318 | 1.320 (hyp1) | 1.306 | 1.016 | 14/24 days | 0.010 |
| llm · tour_anonymized | 1.461 | 1.447 | 1.456 (hyp2) | 1.448 | 1.094 | 9/24 days | 0.032 |

### Fixed set, tour_named: who held the weight, and why

Days led by each hypothesis (true weights, replayed): hyp1 26, hyp2 2

| particle | sighting log-likelihood earned (presence) | (absence, weighted) | question log-loss | OUT_OF_HOUSE moves |
|---|---|---|---|---|
| hyp1 | -930 | -200 | 1.354 | 0 |
| hyp2 | -995 | -165 | 1.266 | 6 |
| hyp3 | -1014 | -183 | 1.369 | 5 |
| hyp4 | -1010 | -174 | 1.306 | 6 |
| hyp5 | -966 | -197 | 1.361 | 8 |
| stat | -1449 | -327 | 1.909 | — |

### Fixed set, tour_anonymized: who held the weight, and why

Days led by each hypothesis (true weights, replayed): hyp2 13, hyp1 9, hyp4 3, hyp3 3

| particle | sighting log-likelihood earned (presence) | (absence, weighted) | question log-loss | OUT_OF_HOUSE moves |
|---|---|---|---|---|
| hyp1 | -977 | -180 | 1.320 | 3 |
| hyp2 | -953 | -191 | 1.340 | 0 |
| hyp3 | -963 | -192 | 1.345 | 0 |
| hyp4 | -957 | -195 | 1.355 | 1 |
| hyp5 | -970 | -189 | 1.335 | 0 |
| stat | -1449 | -329 | 1.909 | — |

## 2. Named vs anonymized fixed sets — question by question

- correct: named 1394, anonymized 1396 of 2250
- both right 1366, named-only 28, anonymized-only 30
- argmax differs on 100 questions (4.4%); objects: [('mug_mara', 24), ('water_bottle_mara', 19), ('phone_mara', 13), ('headphones_mara', 11), ('remote_shared_1', 5), ('tablet_mara', 5), ('wallet_mara', 5), ('bowl_shared_1', 4)]

## 3. Re-asking vs fixed set — where it lost and gained

### tour_named

Re-asks: [(3, 'scheduled', True), (7, 'scheduled', True)]

| week | fixed right, re-ask wrong | re-ask right, fixed wrong |
|---|---|---|
| d3-6 | 11 | 2 |
| d7-13 | 41 | 27 |
| d14-20 | 42 | 25 |
| d21-27 | 29 | 32 |

- objects where re-asking lost most: [('medication_bottle_mara', 17), ('book_mara', 16), ('remote_shared_1', 10), ('glasses_mara', 9), ('lunchbox_mara', 6), ('bowl_shared_1', 6), ('wallet_mara', 6), ('water_bottle_mara', 5)]
- objects where it gained most: [('phone_mara', 15), ('laptop_mara', 9), ('keys_mara', 6), ('remote_shared_1', 6), ('backpack_mara', 5), ('wallet_mara', 5), ('mug_mara', 5), ('vacuum_cleaner_shared_1', 5)]
- log-loss damage per object (summed, re-ask − fixed): [('book_mara', 27.1), ('yoga_mat_mara', 15.9), ('water_bottle_mara', 12.0), ('lunchbox_mara', 11.4), ('watering_can_mara', 10.5), ('medication_bottle_mara', 10.2), ('tablet_mara', 9.7), ('notebook_mara', 9.4)]
- at the lost questions, truth was: [('OUT_OF_HOUSE', 28), ('kitchen_table_k1', 24), ('bathroom_shelf_ba1', 15), ('nightstand_b1', 10), ('entry_table_e1', 9)]; re-ask predicted: [('counter_k1', 31), ('kitchen_table_k1', 18), ('bookshelf_l1', 16), ('OUT_OF_HOUSE', 16), ('entry_table_e1', 10)]
- after the last revision: 35 objects have rest entries, and all hypotheses give the SAME rest for 35 of them

### tour_anonymized

Re-asks: [(3, 'scheduled', True), (7, 'scheduled', True)]

| week | fixed right, re-ask wrong | re-ask right, fixed wrong |
|---|---|---|
| d3-6 | 16 | 6 |
| d7-13 | 40 | 16 |
| d14-20 | 43 | 8 |
| d21-27 | 50 | 8 |

- objects where re-asking lost most: [('wallet_mara', 15), ('medication_bottle_mara', 12), ('mug_mara', 12), ('laundry_basket_mara', 12), ('suitcase_mara', 12), ('umbrella_mara', 8), ('bowl_shared_1', 8), ('bowl_shared_2', 7)]
- objects where it gained most: [('plate_shared_1', 5), ('backpack_mara', 5), ('phone_mara', 4), ('mug_mara', 3), ('pan_shared_1', 3), ('lunchbox_mara', 3), ('hairbrush_mara', 3), ('plate_shared_2', 2)]
- log-loss damage per object (summed, re-ask − fixed): [('plate_shared_2', 24.1), ('laundry_basket_mara', 23.2), ('wallet_mara', 22.1), ('suitcase_mara', 21.2), ('jacket_mara', 21.1), ('mug_mara', 20.6), ('bowl_shared_1', 18.1), ('umbrella_mara', 18.0)]
- at the lost questions, truth was: [('bedroom_floor_b1', 30), ('kitchen_table_k1', 29), ('OUT_OF_HOUSE', 22), ('bathroom_shelf_ba1', 19), ('entry_table_e1', 16)]; re-ask predicted: [('counter_k1', 41), ('entry_floor_e1', 31), ('couch_l1', 19), ('entry_hook_e1', 16), ('kitchen_table_k1', 10)]
- after the last revision: 27 objects have rest entries, and all hypotheses give the SAME rest for 17 of them

