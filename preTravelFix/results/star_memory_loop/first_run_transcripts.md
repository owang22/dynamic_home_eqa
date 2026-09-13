# First run: LastObservation x StarQwen x budget 24 on hh_001_timeline_seed0

## q0158  [truly_out]
object book_mara at t=409437 (day 4)
```
recall_object_history(book_mara) ->
memory of book_mara, newest first:
- 0.3h ago: absent from sink_k1 (kitchen)
- 0.6h ago: absent from counter_k1 (kitchen)
- 1.0h ago: absent from towel_rack_ba1 (bathroom)
- 1.0h ago: absent from bathroom_shelf_ba1 (bathroom)
- 1.8h ago: absent from sink_k1 (kitchen)
- 1.9h ago: absent from counter_k1 (kitchen)
- 1.9h ago: absent from cupboard_k1 (kitchen)
- 2.3h ago: absent from couch_l1 (living)
- 3.7h ago: absent from sink_k1 (kitchen)
- 3.7h ago: absent from kitchen_table_k1 (kitchen)
- 3.7h ago: absent from dish_rack_k1 (kitchen)
- 3.7h ago: absent from cupboard_k1 (kitchen)
recall_object_history(book_mara) ->
memory of book_mara, newest first:
- 0.3h ago: absent from sink_k1 (kitchen)
- 0.6h ago: absent from counter_k1 (kitchen)
- 1.0h ago: absent from towel_rack_ba1 (bathroom)
- 1.0h ago: absent from bathroom_shelf_ba1 (bathroom)
- 1.8h ago: absent from sink_k1 (kitchen)
- 1.9h ago: absent from counter_k1 (kitchen)
- 1.9h ago: absent from cupboard_k1 (kitchen)
- 2.3h ago: absent from couch_l1 (living)
- 3.7h ago: absent from sink_k1 (kitchen)
- 3.7h ago: absent from kitchen_table_k1 (kitchen)
- 3.7h ago: absent from dish_rack_k1 (kitchen)
- 3.7h ago: absent from cupboard_k1 (kitchen)
recall_time_pattern(book_mara, +/-1h) ->
memory: no sightings of book_mara near hour 17:00 on any day
recall_object_history(book_mara) ->
memory of book_mara, newest first:
- 0.3h ago: absent from sink_k1 (kitchen)
- 0.6h ago: absent from counter_k1 (kitchen)
- 1.0h ago: absent from towel_rack_ba1 (bathroom)
- 1.0h ago: absent from bathroom_shelf_ba1 (bathroom)
- 1.8h ago: absent from sink_k1 (kitchen)
- 1.9h ago: absent from counter_k1 (kitchen)
- 1.9h ago: absent from cupboard_k1 (kitchen)
- 2.3h ago: absent from couch_l1 (living)
- 3.7h ago: absent from sink_k1 (kitchen)
- 3.7h ago: absent from kitchen_table_k1 (kitchen)
- 3.7h ago: absent from dish_rack_k1 (kitchen)
- 3.7h ago: absent from cupboard_k1 (kitchen)
rejected: recall cap reached (4 per question)
sense bookshelf_l1 -> book_mara NOT here (contents: empty)
sense bed_b1 -> book_mara NOT here (contents: empty)
sense nightstand_b1 -> book_mara NOT here (contents: hairbrush_mara)
sense desk_b1 -> book_mara NOT here (contents: empty)
fallback to belief argmax: step cap reached
```
answer: ON_PERSON  truth: OUT_OF_HOUSE  correct: False  senses: 4  overridden: False
stats: {"recalls": 4, "senses": 4, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 1, "fallbacks": 1, "step_cap_hits": 1}

## q0347  [stale_in_house]
object blanket_mara at t=565696 (day 6)
```
recall_object_history(blanket_mara) ->
memory of blanket_mara, newest first:
- 0.7h ago: absent from chair_k1 (kitchen)
- 0.7h ago: absent from kitchen_table_k1 (kitchen)
- 0.7h ago: absent from counter_k1 (kitchen)
- 1.3h ago: seen at couch_l1 (living)
- 1.7h ago: absent from sink_k1 (kitchen)
- 1.7h ago: absent from kitchen_table_k1 (kitchen)
- 1.7h ago: absent from dish_rack_k1 (kitchen)
- 1.7h ago: absent from cupboard_k1 (kitchen)
- 1.7h ago: absent from counter_k1 (kitchen)
- 1.7h ago: absent from chair_k2 (kitchen)
- 1.7h ago: absent from chair_k1 (kitchen)
- 1.7h ago: absent from coffee_table_l1 (living)
sense couch_l1 -> FOUND blanket_mara
answer couch_l1 (found)
```
answer: couch_l1  truth: couch_l1  correct: True  senses: 1  overridden: False
stats: {"recalls": 1, "senses": 1, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q0337  [stale_in_house]
object makeup_kit_mara at t=586367 (day 6)
```
recall_object_history(makeup_kit_mara) ->
memory of makeup_kit_mara, newest first:
- 0.5h ago: absent from entry_floor_e1 (entry)
- 1.0h ago: absent from entry_table_e1 (entry)
- 1.8h ago: absent from towel_rack_ba1 (bathroom)
- 1.8h ago: absent from counter_k1 (kitchen)
- 2.1h ago: absent from kitchen_table_k1 (kitchen)
- 2.1h ago: absent from entry_table_e1 (entry)
- 2.1h ago: absent from entry_hook_e1 (entry)
- 2.1h ago: absent from entry_floor_e1 (entry)
- 3.8h ago: absent from kitchen_table_k1 (kitchen)
- 4.0h ago: absent from counter_k1 (kitchen)
- 4.6h ago: absent from couch_l1 (living)
- 4.9h ago: absent from towel_rack_ba1 (bathroom)
answer OUT_OF_HOUSE
```
answer: OUT_OF_HOUSE  truth: bathroom_shelf_ba1  correct: False  senses: 0  overridden: True
stats: {"recalls": 1, "senses": 0, "answered_from_memory": 1, "answered_by_selector": 1, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q0423  [came_back]
object umbrella_mara at t=670328 (day 7)
```
recall_object_history(umbrella_mara) ->
memory of umbrella_mara, newest first:
- 0.4h ago: absent from sink_k1 (kitchen)
- 0.4h ago: absent from sink_k1 (kitchen)
- 1.0h ago: absent from counter_k1 (kitchen)
- 2.1h ago: absent from nightstand_b1 (bedroom)
- 2.1h ago: absent from desk_b1 (bedroom)
- 2.1h ago: absent from bedroom_floor_b1 (bedroom)
- 2.1h ago: absent from bed_b1 (bedroom)
- 2.5h ago: absent from sink_k1 (kitchen)
- 3.2h ago: absent from entry_floor_e1 (entry)
- 4.1h ago: absent from cupboard_k1 (kitchen)
- 4.9h ago: absent from counter_k1 (kitchen)
- 5.4h ago: absent from entry_table_e1 (entry)
recall_object_history(umbrella_mara) ->
memory of umbrella_mara, newest first:
- 0.4h ago: absent from sink_k1 (kitchen)
- 0.4h ago: absent from sink_k1 (kitchen)
- 1.0h ago: absent from counter_k1 (kitchen)
- 2.1h ago: absent from nightstand_b1 (bedroom)
- 2.1h ago: absent from desk_b1 (bedroom)
- 2.1h ago: absent from bedroom_floor_b1 (bedroom)
- 2.1h ago: absent from bed_b1 (bedroom)
- 2.5h ago: absent from sink_k1 (kitchen)
- 3.2h ago: absent from entry_floor_e1 (entry)
- 4.1h ago: absent from cupboard_k1 (kitchen)
- 4.9h ago: absent from counter_k1 (kitchen)
- 5.4h ago: absent from entry_table_e1 (entry)
recall_time_pattern(umbrella_mara, +/-1h) ->
sightings of umbrella_mara near hour 18:00 (+/-1h), by receptacle:
- entry_floor_e1 (entry): 4x, newest 23.8h ago
sense entry_hook_e1 -> umbrella_mara NOT here (contents: jacket_mara)
sense entry_table_e1 -> umbrella_mara NOT here (contents: bowl_shared_1, keys_mara, wallet_mara)
answer OUT_OF_HOUSE
```
answer: OUT_OF_HOUSE  truth: entry_floor_e1  correct: False  senses: 2  overridden: True
stats: {"recalls": 3, "senses": 2, "answered_from_memory": 0, "answered_by_selector": 1, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q0512  [truly_out]
object phone_mara at t=738642 (day 8)
```
recall_object_history(phone_mara) ->
memory of phone_mara, newest first:
- 0.5h ago: absent from nightstand_b1 (bedroom)
- 0.5h ago: absent from desk_b1 (bedroom)
- 0.5h ago: absent from bedroom_floor_b1 (bedroom)
- 0.5h ago: absent from bed_b1 (bedroom)
- 1.0h ago: absent from entry_floor_e1 (entry)
- 1.5h ago: absent from kitchen_table_k1 (kitchen)
- 2.8h ago: absent from bathroom_shelf_ba1 (bathroom)
- 3.3h ago: absent from kitchen_table_k1 (kitchen)
- 3.6h ago: absent from entry_table_e1 (entry)
- 3.6h ago: absent from entry_hook_e1 (entry)
- 3.6h ago: absent from entry_floor_e1 (entry)
- 5.0h ago: absent from sink_k1 (kitchen)
recall_time_pattern(phone_mara, +/-1h) ->
sightings of phone_mara near hour 13:00 (+/-1h), by receptacle:
- nightstand_b1 (bedroom): 2x, newest 119.5h ago
sense couch_l1 -> phone_mara NOT here (contents: blanket_mara, watering_can_mara)
sense coffee_table_l1 -> phone_mara NOT here (contents: empty)
sense tv_stand_l1 -> phone_mara NOT here (contents: empty)
sense bed_b1 -> phone_mara NOT here (contents: empty)
sense nightstand_b1 -> phone_mara NOT here (contents: empty)
recall_object_history(phone_mara) ->
memory of phone_mara, newest first:
- 0.0h ago: absent from nightstand_b1 (bedroom)
- 0.0h ago: absent from bed_b1 (bedroom)
- 0.0h ago: absent from tv_stand_l1 (living)
- 0.0h ago: absent from coffee_table_l1 (living)
- 0.0h ago: absent from couch_l1 (living)
- 0.5h ago: absent from nightstand_b1 (bedroom)
- 0.5h ago: absent from desk_b1 (bedroom)
- 0.5h ago: absent from bedroom_floor_b1 (bedroom)
- 0.5h ago: absent from bed_b1 (bedroom)
- 1.0h ago: absent from entry_floor_e1 (entry)
- 1.5h ago: absent from kitchen_table_k1 (kitchen)
- 2.8h ago: absent from bathroom_shelf_ba1 (bathroom)
fallback to belief argmax: step cap reached
```
answer: kitchen_table_k1  truth: OUT_OF_HOUSE  correct: False  senses: 5  overridden: False
stats: {"recalls": 3, "senses": 5, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 1, "step_cap_hits": 1}

## q0462  [came_back]
object umbrella_mara at t=758644 (day 8)
```
recall_object_history(umbrella_mara) ->
memory of umbrella_mara, newest first:
- 0.7h ago: absent from couch_l1 (living)
- 3.1h ago: absent from tv_stand_l1 (living)
- 3.1h ago: absent from couch_l1 (living)
- 3.1h ago: absent from coffee_table_l1 (living)
- 3.1h ago: absent from bookshelf_l1 (living)
- 3.1h ago: absent from armchair_l1 (living)
- 3.4h ago: absent from entry_floor_e1 (entry)
- 3.4h ago: absent from couch_l1 (living)
- 4.0h ago: absent from kitchen_table_k1 (kitchen)
- 4.5h ago: absent from entry_floor_e1 (entry)
- 5.6h ago: absent from nightstand_b1 (bedroom)
- 5.6h ago: absent from bed_b1 (bedroom)
recall_object_history(umbrella_mara) ->
memory of umbrella_mara, newest first:
- 0.7h ago: absent from couch_l1 (living)
- 3.1h ago: absent from tv_stand_l1 (living)
- 3.1h ago: absent from couch_l1 (living)
- 3.1h ago: absent from coffee_table_l1 (living)
- 3.1h ago: absent from bookshelf_l1 (living)
- 3.1h ago: absent from armchair_l1 (living)
- 3.4h ago: absent from entry_floor_e1 (entry)
- 3.4h ago: absent from couch_l1 (living)
- 4.0h ago: absent from kitchen_table_k1 (kitchen)
- 4.5h ago: absent from entry_floor_e1 (entry)
- 5.6h ago: absent from nightstand_b1 (bedroom)
- 5.6h ago: absent from bed_b1 (bedroom)
recall_time_pattern(umbrella_mara, +/-1h) ->
sightings of umbrella_mara near hour 18:00 (+/-1h), by receptacle:
- entry_floor_e1 (entry): 4x, newest 48.4h ago
sense entry_hook_e1 -> umbrella_mara NOT here (contents: backpack_mara, jacket_mara)
sense entry_floor_e1 -> FOUND umbrella_mara
answer entry_floor_e1 (found)
```
answer: entry_floor_e1  truth: entry_floor_e1  correct: True  senses: 2  overridden: False
stats: {"recalls": 3, "senses": 2, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q0617  [stale_in_house]
object towel_mara at t=847439 (day 9)
```
recall_object_history(towel_mara) ->
memory of towel_mara, newest first:
- 0.1h ago: absent from kitchen_table_k1 (kitchen)
- 0.3h ago: absent from counter_k1 (kitchen)
- 0.4h ago: seen at towel_rack_ba1 (bathroom)
- 0.4h ago: absent from bathroom_shelf_ba1 (bathroom)
- 1.0h ago: absent from chair_k1 (kitchen)
- 1.2h ago: absent from couch_l1 (living)
- 2.0h ago: absent from kitchen_table_k1 (kitchen)
- 3.7h ago: absent from sink_k1 (kitchen)
- 3.7h ago: absent from kitchen_table_k1 (kitchen)
- 3.7h ago: absent from dish_rack_k1 (kitchen)
- 3.7h ago: absent from cupboard_k1 (kitchen)
- 3.7h ago: absent from counter_k1 (kitchen)
sense towel_rack_ba1 -> FOUND towel_mara
answer towel_rack_ba1 (found)
```
answer: towel_rack_ba1  truth: towel_rack_ba1  correct: True  senses: 1  overridden: False
stats: {"recalls": 1, "senses": 1, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q0582  [stale_in_house]
object umbrella_mara at t=862268 (day 9)
```
recall_object_history(umbrella_mara) ->
memory of umbrella_mara, newest first:
- 0.2h ago: absent from bathroom_shelf_ba1 (bathroom)
- 0.2h ago: absent from cupboard_k1 (kitchen)
- 1.4h ago: absent from entry_table_e1 (entry)
- 1.4h ago: absent from entry_hook_e1 (entry)
- 1.4h ago: seen at entry_floor_e1 (entry)
- 2.1h ago: absent from kitchen_table_k1 (kitchen)
- 3.0h ago: absent from sink_k1 (kitchen)
- 3.2h ago: absent from cupboard_k1 (kitchen)
- 4.1h ago: absent from towel_rack_ba1 (bathroom)
- 4.3h ago: absent from kitchen_table_k1 (kitchen)
- 4.4h ago: absent from counter_k1 (kitchen)
- 4.5h ago: absent from towel_rack_ba1 (bathroom)
answer entry_floor_e1
```
answer: entry_floor_e1  truth: entry_floor_e1  correct: True  senses: 0  overridden: True
stats: {"recalls": 1, "senses": 0, "answered_from_memory": 1, "answered_by_selector": 1, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q0636  [stale_in_house]
object book_mara at t=944445 (day 10)
```
recall_object_history(book_mara) ->
memory of book_mara, newest first:
- 1.9h ago: absent from bathroom_shelf_ba1 (bathroom)
- 2.1h ago: absent from kitchen_table_k1 (kitchen)
- 3.0h ago: absent from entry_table_e1 (entry)
- 3.0h ago: absent from entry_hook_e1 (entry)
- 3.0h ago: absent from entry_floor_e1 (entry)
- 3.3h ago: absent from towel_rack_ba1 (bathroom)
- 3.3h ago: absent from kitchen_table_k1 (kitchen)
- 4.8h ago: absent from kitchen_table_k1 (kitchen)
- 5.2h ago: absent from bathroom_shelf_ba1 (bathroom)
- 5.2h ago: absent from kitchen_table_k1 (kitchen)
- 5.4h ago: absent from couch_l1 (living)
- 6.4h ago: absent from towel_rack_ba1 (bathroom)
recall_object_history(book_mara) ->
memory of book_mara, newest first:
- 1.9h ago: absent from bathroom_shelf_ba1 (bathroom)
- 2.1h ago: absent from kitchen_table_k1 (kitchen)
- 3.0h ago: absent from entry_table_e1 (entry)
- 3.0h ago: absent from entry_hook_e1 (entry)
- 3.0h ago: absent from entry_floor_e1 (entry)
- 3.3h ago: absent from towel_rack_ba1 (bathroom)
- 3.3h ago: absent from kitchen_table_k1 (kitchen)
- 4.8h ago: absent from kitchen_table_k1 (kitchen)
- 5.2h ago: absent from bathroom_shelf_ba1 (bathroom)
- 5.2h ago: absent from kitchen_table_k1 (kitchen)
- 5.4h ago: absent from couch_l1 (living)
- 6.4h ago: absent from towel_rack_ba1 (bathroom)
recall_time_pattern(book_mara, +/-2h) ->
sightings of book_mara near hour 22:00 (+/-2h), by receptacle:
- bookshelf_l1 (living): 2x, newest 216.6h ago
- entry_table_e1 (entry): 1x, newest 24.2h ago
sense bookshelf_l1 -> book_mara NOT here (contents: empty)
sense bed_b1 -> book_mara NOT here (contents: empty)
sense coffee_table_l1 -> book_mara NOT here (contents: empty)
answer OUT_OF_HOUSE
```
answer: OUT_OF_HOUSE  truth: ON_PERSON  correct: False  senses: 3  overridden: True
stats: {"recalls": 3, "senses": 3, "answered_from_memory": 0, "answered_by_selector": 1, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q0871  [stale_in_house]
object watering_can_mara at t=1074695 (day 12)
```
recall_object_history(watering_can_mara) ->
memory of watering_can_mara, newest first:
- 2.5h ago: absent from counter_k1 (kitchen)
- 3.3h ago: seen at couch_l1 (living)
- 3.3h ago: absent from kitchen_table_k1 (kitchen)
- 15.2h ago: absent from counter_k1 (kitchen)
- 15.3h ago: absent from tv_stand_l1 (living)
- 15.3h ago: seen at couch_l1 (living)
- 15.3h ago: absent from coffee_table_l1 (living)
- 15.3h ago: absent from bookshelf_l1 (living)
- 15.3h ago: absent from armchair_l1 (living)
- 16.1h ago: absent from kitchen_table_k1 (kitchen)
- 16.8h ago: absent from counter_k1 (kitchen)
- 17.1h ago: absent from entry_floor_e1 (entry)
sense couch_l1 -> FOUND watering_can_mara
answer couch_l1 (found)
```
answer: couch_l1  truth: couch_l1  correct: True  senses: 1  overridden: False
stats: {"recalls": 1, "senses": 1, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q0810  [stale_in_house]
object yoga_mat_mara at t=1088614 (day 12)
```
recall_object_history(yoga_mat_mara) ->
memory of yoga_mat_mara, newest first:
- 0.6h ago: absent from dish_rack_k1 (kitchen)
- 0.6h ago: absent from counter_k1 (kitchen)
- 1.4h ago: absent from towel_rack_ba1 (bathroom)
- 1.4h ago: absent from bathroom_shelf_ba1 (bathroom)
- 1.5h ago: absent from kitchen_table_k1 (kitchen)
- 1.8h ago: absent from cupboard_k1 (kitchen)
- 2.1h ago: absent from counter_k1 (kitchen)
- 2.2h ago: absent from kitchen_table_k1 (kitchen)
- 2.6h ago: absent from dish_rack_k1 (kitchen)
- 3.5h ago: absent from kitchen_table_k1 (kitchen)
- 3.8h ago: absent from sink_k1 (kitchen)
- 3.8h ago: absent from kitchen_table_k1 (kitchen)
recall_time_pattern(yoga_mat_mara, +/-1h) ->
sightings of yoga_mat_mara near hour 14:00 (+/-1h), by receptacle:
- couch_l1 (living): 6x, newest 144.1h ago
sense couch_l1 -> yoga_mat_mara NOT here (contents: blanket_mara, watering_can_mara)
sense bedroom_floor_b1 -> yoga_mat_mara NOT here (contents: laundry_basket_mara, suitcase_mara)
recall_object_history(yoga_mat_mara) ->
memory of yoga_mat_mara, newest first:
- 0.0h ago: absent from bedroom_floor_b1 (bedroom)
- 0.0h ago: absent from couch_l1 (living)
- 0.6h ago: absent from dish_rack_k1 (kitchen)
- 0.6h ago: absent from counter_k1 (kitchen)
- 1.4h ago: absent from towel_rack_ba1 (bathroom)
- 1.4h ago: absent from bathroom_shelf_ba1 (bathroom)
- 1.5h ago: absent from kitchen_table_k1 (kitchen)
- 1.8h ago: absent from cupboard_k1 (kitchen)
- 2.1h ago: absent from counter_k1 (kitchen)
- 2.2h ago: absent from kitchen_table_k1 (kitchen)
- 2.6h ago: absent from dish_rack_k1 (kitchen)
- 3.5h ago: absent from kitchen_table_k1 (kitchen)
answer OUT_OF_HOUSE
```
answer: OUT_OF_HOUSE  truth: ON_PERSON  correct: False  senses: 2  overridden: True
stats: {"recalls": 3, "senses": 2, "answered_from_memory": 0, "answered_by_selector": 1, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q1025  [stale_in_house]
object plate_shared_1 at t=1233726 (day 14)
```
recall_object_history(plate_shared_1) ->
memory of plate_shared_1, newest first:
- 0.0h ago: absent from towel_rack_ba1 (bathroom)
- 0.2h ago: seen at sink_k1 (kitchen)
- 1.4h ago: absent from entry_table_e1 (entry)
- 1.4h ago: absent from entry_hook_e1 (entry)
- 1.4h ago: absent from entry_floor_e1 (entry)
- 2.1h ago: absent from counter_k1 (kitchen)
- 7.1h ago: seen at sink_k1 (kitchen)
- 7.5h ago: absent from dish_rack_k1 (kitchen)
- 8.2h ago: absent from towel_rack_ba1 (bathroom)
- 8.2h ago: absent from bathroom_shelf_ba1 (bathroom)
- 8.7h ago: absent from kitchen_table_k1 (kitchen)
- 9.1h ago: absent from counter_k1 (kitchen)
sense sink_k1 -> FOUND plate_shared_1
answer sink_k1 (found)
```
answer: sink_k1  truth: sink_k1  correct: True  senses: 1  overridden: False
stats: {"recalls": 1, "senses": 1, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q1188  [came_back]
object towel_mara at t=1405993 (day 16)
```
recall_object_history(towel_mara) ->
memory of towel_mara, newest first:
- 0.2h ago: absent from sink_k1 (kitchen)
- 7.8h ago: absent from sink_k1 (kitchen)
- 8.3h ago: absent from nightstand_b1 (bedroom)
- 8.3h ago: absent from desk_b1 (bedroom)
- 8.3h ago: absent from bedroom_floor_b1 (bedroom)
- 8.3h ago: absent from bed_b1 (bedroom)
- 9.0h ago: absent from entry_table_e1 (entry)
- 9.0h ago: absent from kitchen_table_k1 (kitchen)
- 9.4h ago: absent from counter_k1 (kitchen)
- 10.5h ago: absent from entry_table_e1 (entry)
- 10.6h ago: absent from sink_k1 (kitchen)
- 10.7h ago: absent from kitchen_table_k1 (kitchen)
recall_object_history(towel_mara) ->
memory of towel_mara, newest first:
- 0.2h ago: absent from sink_k1 (kitchen)
- 7.8h ago: absent from sink_k1 (kitchen)
- 8.3h ago: absent from nightstand_b1 (bedroom)
- 8.3h ago: absent from desk_b1 (bedroom)
- 8.3h ago: absent from bedroom_floor_b1 (bedroom)
- 8.3h ago: absent from bed_b1 (bedroom)
- 9.0h ago: absent from entry_table_e1 (entry)
- 9.0h ago: absent from kitchen_table_k1 (kitchen)
- 9.4h ago: absent from counter_k1 (kitchen)
- 10.5h ago: absent from entry_table_e1 (entry)
- 10.6h ago: absent from sink_k1 (kitchen)
- 10.7h ago: absent from kitchen_table_k1 (kitchen)
recall_object_history(towel_mara) ->
memory of towel_mara, newest first:
- 0.2h ago: absent from sink_k1 (kitchen)
- 7.8h ago: absent from sink_k1 (kitchen)
- 8.3h ago: absent from nightstand_b1 (bedroom)
- 8.3h ago: absent from desk_b1 (bedroom)
- 8.3h ago: absent from bedroom_floor_b1 (bedroom)
- 8.3h ago: absent from bed_b1 (bedroom)
- 9.0h ago: absent from entry_table_e1 (entry)
- 9.0h ago: absent from kitchen_table_k1 (kitchen)
- 9.4h ago: absent from counter_k1 (kitchen)
- 10.5h ago: absent from entry_table_e1 (entry)
- 10.6h ago: absent from sink_k1 (kitchen)
- 10.7h ago: absent from kitchen_table_k1 (kitchen)
recall_object_history(towel_mara) ->
memory of towel_mara, newest first:
- 0.2h ago: absent from sink_k1 (kitchen)
- 7.8h ago: absent from sink_k1 (kitchen)
- 8.3h ago: absent from nightstand_b1 (bedroom)
- 8.3h ago: absent from desk_b1 (bedroom)
- 8.3h ago: absent from bedroom_floor_b1 (bedroom)
- 8.3h ago: absent from bed_b1 (bedroom)
- 9.0h ago: absent from entry_table_e1 (entry)
- 9.0h ago: absent from kitchen_table_k1 (kitchen)
- 9.4h ago: absent from counter_k1 (kitchen)
- 10.5h ago: absent from entry_table_e1 (entry)
- 10.6h ago: absent from sink_k1 (kitchen)
- 10.7h ago: absent from kitchen_table_k1 (kitchen)
rejected: recall cap reached (4 per question)
fallback to belief argmax: illegal action: recall cap reached (4 per question)
```
answer: towel_rack_ba1  truth: towel_rack_ba1  correct: True  senses: 0  overridden: False
stats: {"recalls": 4, "senses": 0, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 2, "fallbacks": 1, "step_cap_hits": 0}

## q1172  [truly_out]
object suitcase_mara at t=1412320 (day 16)
```
recall_object_history(suitcase_mara) ->
memory of suitcase_mara, newest first:
- 0.4h ago: absent from sink_k1 (kitchen)
- 1.4h ago: seen at bedroom_floor_b1 (bedroom)
- 1.5h ago: absent from tv_stand_l1 (living)
- 1.5h ago: absent from couch_l1 (living)
- 1.5h ago: absent from coffee_table_l1 (living)
- 1.5h ago: absent from bookshelf_l1 (living)
- 1.5h ago: absent from armchair_l1 (living)
- 1.9h ago: absent from sink_k1 (kitchen)
- 9.5h ago: absent from sink_k1 (kitchen)
- 10.1h ago: absent from nightstand_b1 (bedroom)
- 10.1h ago: absent from desk_b1 (bedroom)
- 10.1h ago: seen at bedroom_floor_b1 (bedroom)
sense bedroom_floor_b1 -> suitcase_mara NOT here (contents: empty)
recall_object_history(suitcase_mara) ->
memory of suitcase_mara, newest first:
- 0.0h ago: absent from bedroom_floor_b1 (bedroom)
- 0.4h ago: absent from sink_k1 (kitchen)
- 1.4h ago: seen at bedroom_floor_b1 (bedroom)
- 1.5h ago: absent from tv_stand_l1 (living)
- 1.5h ago: absent from couch_l1 (living)
- 1.5h ago: absent from coffee_table_l1 (living)
- 1.5h ago: absent from bookshelf_l1 (living)
- 1.5h ago: absent from armchair_l1 (living)
- 1.9h ago: absent from sink_k1 (kitchen)
- 9.5h ago: absent from sink_k1 (kitchen)
- 10.1h ago: absent from nightstand_b1 (bedroom)
- 10.1h ago: absent from desk_b1 (bedroom)
recall_time_pattern(suitcase_mara, +/-6h) ->
sightings of suitcase_mara near hour 08:00 (+/-6h), by receptacle:
- bedroom_floor_b1 (bedroom): 12x, newest 1.4h ago
sense bed_b1 -> suitcase_mara NOT here (contents: empty)
sense nightstand_b1 -> suitcase_mara NOT here (contents: empty)
sense desk_b1 -> suitcase_mara NOT here (contents: empty)
recall_object_history(suitcase_mara) ->
memory of suitcase_mara, newest first:
- 0.0h ago: absent from desk_b1 (bedroom)
- 0.0h ago: absent from nightstand_b1 (bedroom)
- 0.0h ago: absent from bed_b1 (bedroom)
- 0.0h ago: absent from bedroom_floor_b1 (bedroom)
- 0.4h ago: absent from sink_k1 (kitchen)
- 1.4h ago: seen at bedroom_floor_b1 (bedroom)
- 1.5h ago: absent from tv_stand_l1 (living)
- 1.5h ago: absent from couch_l1 (living)
- 1.5h ago: absent from coffee_table_l1 (living)
- 1.5h ago: absent from bookshelf_l1 (living)
- 1.5h ago: absent from armchair_l1 (living)
- 1.9h ago: absent from sink_k1 (kitchen)
fallback to belief argmax: step cap reached
```
answer: tv_stand_l1  truth: OUT_OF_HOUSE  correct: False  senses: 4  overridden: False
stats: {"recalls": 4, "senses": 4, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 1, "step_cap_hits": 1}

## q1175  [truly_out]
object laundry_basket_mara at t=1422716 (day 16)
```
recall_object_history(laundry_basket_mara) ->
memory of laundry_basket_mara, newest first:
- 1.2h ago: absent from sink_k1 (kitchen)
- 1.2h ago: absent from kitchen_table_k1 (kitchen)
- 1.2h ago: absent from dish_rack_k1 (kitchen)
- 1.2h ago: absent from cupboard_k1 (kitchen)
- 1.2h ago: absent from counter_k1 (kitchen)
- 1.2h ago: absent from chair_k2 (kitchen)
- 1.2h ago: absent from chair_k1 (kitchen)
- 1.2h ago: absent from coffee_table_l1 (living)
- 2.0h ago: absent from couch_l1 (living)
- 2.9h ago: absent from desk_b1 (bedroom)
- 2.9h ago: absent from nightstand_b1 (bedroom)
- 2.9h ago: absent from bed_b1 (bedroom)
recall_object_history(laundry_basket_mara) ->
memory of laundry_basket_mara, newest first:
- 1.2h ago: absent from sink_k1 (kitchen)
- 1.2h ago: absent from kitchen_table_k1 (kitchen)
- 1.2h ago: absent from dish_rack_k1 (kitchen)
- 1.2h ago: absent from cupboard_k1 (kitchen)
- 1.2h ago: absent from counter_k1 (kitchen)
- 1.2h ago: absent from chair_k2 (kitchen)
- 1.2h ago: absent from chair_k1 (kitchen)
- 1.2h ago: absent from coffee_table_l1 (living)
- 2.0h ago: absent from couch_l1 (living)
- 2.9h ago: absent from desk_b1 (bedroom)
- 2.9h ago: absent from nightstand_b1 (bedroom)
- 2.9h ago: absent from bed_b1 (bedroom)
recall_time_pattern(laundry_basket_mara, +/-1h) ->
sightings of laundry_basket_mara near hour 11:00 (+/-1h), by receptacle:
- bedroom_floor_b1 (bedroom): 2x, newest 263.7h ago
sense bedroom_floor_b1 -> laundry_basket_mara NOT here (contents: empty)
answer OUT_OF_HOUSE
```
answer: OUT_OF_HOUSE  truth: OUT_OF_HOUSE  correct: True  senses: 1  overridden: True
stats: {"recalls": 3, "senses": 1, "answered_from_memory": 0, "answered_by_selector": 1, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q1199  [came_back]
object keys_mara at t=1444610 (day 16)
```
recall_object_history(keys_mara) ->
memory of keys_mara, newest first:
- 1.0h ago: absent from entry_table_e1 (entry)
- 1.0h ago: absent from entry_hook_e1 (entry)
- 1.0h ago: absent from entry_floor_e1 (entry)
- 1.2h ago: absent from sink_k1 (kitchen)
- 2.9h ago: absent from sink_k1 (kitchen)
- 4.0h ago: absent from sink_k1 (kitchen)
- 4.3h ago: absent from towel_rack_ba1 (bathroom)
- 4.3h ago: absent from bathroom_shelf_ba1 (bathroom)
- 4.5h ago: absent from kitchen_table_k1 (kitchen)
- 4.6h ago: absent from couch_l1 (living)
- 5.7h ago: absent from sink_k1 (kitchen)
- 6.1h ago: absent from bedroom_floor_b1 (bedroom)
recall_time_pattern(keys_mara, +/-1h) ->
sightings of keys_mara near hour 17:00 (+/-1h), by receptacle:
- entry_table_e1 (entry): 4x, newest 96.3h ago
- kitchen_table_k1 (kitchen): 1x, newest 190.3h ago
- counter_k1 (kitchen): 1x, newest 240.2h ago
recall_object_history(keys_mara) ->
memory of keys_mara, newest first:
- 1.0h ago: absent from entry_table_e1 (entry)
- 1.0h ago: absent from entry_hook_e1 (entry)
- 1.0h ago: absent from entry_floor_e1 (entry)
- 1.2h ago: absent from sink_k1 (kitchen)
- 2.9h ago: absent from sink_k1 (kitchen)
- 4.0h ago: absent from sink_k1 (kitchen)
- 4.3h ago: absent from towel_rack_ba1 (bathroom)
- 4.3h ago: absent from bathroom_shelf_ba1 (bathroom)
- 4.5h ago: absent from kitchen_table_k1 (kitchen)
- 4.6h ago: absent from couch_l1 (living)
- 5.7h ago: absent from sink_k1 (kitchen)
- 6.1h ago: absent from bedroom_floor_b1 (bedroom)
recall_object_history(keys_mara) ->
memory of keys_mara, newest first:
- 1.0h ago: absent from entry_table_e1 (entry)
- 1.0h ago: absent from entry_hook_e1 (entry)
- 1.0h ago: absent from entry_floor_e1 (entry)
- 1.2h ago: absent from sink_k1 (kitchen)
- 2.9h ago: absent from sink_k1 (kitchen)
- 4.0h ago: absent from sink_k1 (kitchen)
- 4.3h ago: absent from towel_rack_ba1 (bathroom)
- 4.3h ago: absent from bathroom_shelf_ba1 (bathroom)
- 4.5h ago: absent from kitchen_table_k1 (kitchen)
- 4.6h ago: absent from couch_l1 (living)
- 5.7h ago: absent from sink_k1 (kitchen)
- 6.1h ago: absent from bedroom_floor_b1 (bedroom)
rejected: recall cap reached (4 per question)
sense entry_table_e1 -> FOUND keys_mara
answer entry_table_e1 (found)
```
answer: entry_table_e1  truth: entry_table_e1  correct: True  senses: 1  overridden: False
stats: {"recalls": 4, "senses": 1, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 1, "fallbacks": 0, "step_cap_hits": 0}

## q1245  [came_back]
object umbrella_mara at t=1451448 (day 16)
```
recall_object_history(umbrella_mara) ->
memory of umbrella_mara, newest first:
- 0.9h ago: absent from couch_l1 (living)
- 1.5h ago: absent from kitchen_table_k1 (kitchen)
- 1.9h ago: absent from entry_table_e1 (entry)
- 2.9h ago: absent from entry_table_e1 (entry)
- 2.9h ago: absent from entry_hook_e1 (entry)
- 2.9h ago: absent from entry_floor_e1 (entry)
- 3.1h ago: absent from sink_k1 (kitchen)
- 4.8h ago: absent from sink_k1 (kitchen)
- 5.9h ago: absent from sink_k1 (kitchen)
- 6.2h ago: absent from towel_rack_ba1 (bathroom)
- 6.2h ago: absent from bathroom_shelf_ba1 (bathroom)
- 6.4h ago: absent from kitchen_table_k1 (kitchen)
recall_time_pattern(umbrella_mara, +/-1h) ->
sightings of umbrella_mara near hour 19:00 (+/-1h), by receptacle:
- entry_floor_e1 (entry): 7x, newest 24.2h ago
sense entry_hook_e1 -> umbrella_mara NOT here (contents: backpack_mara, charger_mara, jacket_mara)
sense entry_floor_e1 -> FOUND umbrella_mara
answer entry_floor_e1 (found)
```
answer: entry_floor_e1  truth: entry_floor_e1  correct: True  senses: 2  overridden: False
stats: {"recalls": 2, "senses": 2, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q1307  [stale_in_house]
object tablet_mara at t=1531524 (day 17)
```
recall_object_history(tablet_mara) ->
memory of tablet_mara, newest first:
- 0.5h ago: absent from bathroom_shelf_ba1 (bathroom)
- 0.8h ago: seen at coffee_table_l1 (living)
- 1.3h ago: absent from nightstand_b1 (bedroom)
- 1.3h ago: absent from desk_b1 (bedroom)
- 1.3h ago: absent from bedroom_floor_b1 (bedroom)
- 1.3h ago: absent from bed_b1 (bedroom)
- 1.6h ago: absent from sink_k1 (kitchen)
- 1.9h ago: absent from bathroom_shelf_ba1 (bathroom)
- 4.5h ago: absent from bathroom_shelf_ba1 (bathroom)
- 4.6h ago: absent from entry_table_e1 (entry)
- 4.6h ago: absent from entry_hook_e1 (entry)
- 4.6h ago: absent from entry_floor_e1 (entry)
sense coffee_table_l1 -> FOUND tablet_mara
answer coffee_table_l1 (found)
```
answer: coffee_table_l1  truth: coffee_table_l1  correct: True  senses: 1  overridden: False
stats: {"recalls": 1, "senses": 1, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q1404  [came_back]
object wallet_mara at t=1577372 (day 18)
```
recall_object_history(wallet_mara) ->
memory of wallet_mara, newest first:
- 0.7h ago: absent from bathroom_shelf_ba1 (bathroom)
- 7.9h ago: absent from sink_k1 (kitchen)
- 7.9h ago: absent from kitchen_table_k1 (kitchen)
- 7.9h ago: absent from dish_rack_k1 (kitchen)
- 7.9h ago: absent from cupboard_k1 (kitchen)
- 7.9h ago: absent from counter_k1 (kitchen)
- 7.9h ago: absent from chair_k2 (kitchen)
- 7.9h ago: absent from chair_k1 (kitchen)
- 10.2h ago: absent from sink_k1 (kitchen)
- 10.8h ago: absent from bathroom_shelf_ba1 (bathroom)
- 11.0h ago: absent from tv_stand_l1 (living)
- 11.0h ago: absent from couch_l1 (living)
recall_object_history(wallet_mara) ->
memory of wallet_mara, newest first:
- 0.7h ago: absent from bathroom_shelf_ba1 (bathroom)
- 7.9h ago: absent from sink_k1 (kitchen)
- 7.9h ago: absent from kitchen_table_k1 (kitchen)
- 7.9h ago: absent from dish_rack_k1 (kitchen)
- 7.9h ago: absent from cupboard_k1 (kitchen)
- 7.9h ago: absent from counter_k1 (kitchen)
- 7.9h ago: absent from chair_k2 (kitchen)
- 7.9h ago: absent from chair_k1 (kitchen)
- 10.2h ago: absent from sink_k1 (kitchen)
- 10.8h ago: absent from bathroom_shelf_ba1 (bathroom)
- 11.0h ago: absent from tv_stand_l1 (living)
- 11.0h ago: absent from couch_l1 (living)
recall_object_history(wallet_mara) ->
memory of wallet_mara, newest first:
- 0.7h ago: absent from bathroom_shelf_ba1 (bathroom)
- 7.9h ago: absent from sink_k1 (kitchen)
- 7.9h ago: absent from kitchen_table_k1 (kitchen)
- 7.9h ago: absent from dish_rack_k1 (kitchen)
- 7.9h ago: absent from cupboard_k1 (kitchen)
- 7.9h ago: absent from counter_k1 (kitchen)
- 7.9h ago: absent from chair_k2 (kitchen)
- 7.9h ago: absent from chair_k1 (kitchen)
- 10.2h ago: absent from sink_k1 (kitchen)
- 10.8h ago: absent from bathroom_shelf_ba1 (bathroom)
- 11.0h ago: absent from tv_stand_l1 (living)
- 11.0h ago: absent from couch_l1 (living)
recall_time_pattern(wallet_mara, +/-6h) ->
sightings of wallet_mara near hour 06:00 (+/-6h), by receptacle:
- entry_table_e1 (entry): 6x, newest 96.9h ago
- entry_hook_e1 (entry): 2x, newest 353.8h ago
- kitchen_table_k1 (kitchen): 1x, newest 359.6h ago
sense entry_table_e1 -> FOUND wallet_mara
answer entry_table_e1 (found)
```
answer: entry_table_e1  truth: entry_table_e1  correct: True  senses: 1  overridden: False
stats: {"recalls": 4, "senses": 1, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q1414  [truly_out]
object headphones_mara at t=1583689 (day 18)
```
recall_object_history(headphones_mara) ->
memory of headphones_mara, newest first:
- 0.4h ago: absent from kitchen_table_k1 (kitchen)
- 0.6h ago: absent from kitchen_table_k1 (kitchen)
- 0.7h ago: absent from sink_k1 (kitchen)
- 1.2h ago: absent from towel_rack_ba1 (bathroom)
- 1.2h ago: absent from bathroom_shelf_ba1 (bathroom)
- 1.3h ago: absent from kitchen_table_k1 (kitchen)
- 1.7h ago: absent from kitchen_table_k1 (kitchen)
- 1.8h ago: absent from entry_table_e1 (entry)
- 2.4h ago: absent from bathroom_shelf_ba1 (bathroom)
- 9.7h ago: absent from sink_k1 (kitchen)
- 9.7h ago: absent from kitchen_table_k1 (kitchen)
- 9.7h ago: absent from dish_rack_k1 (kitchen)
recall_object_history(headphones_mara) ->
memory of headphones_mara, newest first:
- 0.4h ago: absent from kitchen_table_k1 (kitchen)
- 0.6h ago: absent from kitchen_table_k1 (kitchen)
- 0.7h ago: absent from sink_k1 (kitchen)
- 1.2h ago: absent from towel_rack_ba1 (bathroom)
- 1.2h ago: absent from bathroom_shelf_ba1 (bathroom)
- 1.3h ago: absent from kitchen_table_k1 (kitchen)
- 1.7h ago: absent from kitchen_table_k1 (kitchen)
- 1.8h ago: absent from entry_table_e1 (entry)
- 2.4h ago: absent from bathroom_shelf_ba1 (bathroom)
- 9.7h ago: absent from sink_k1 (kitchen)
- 9.7h ago: absent from kitchen_table_k1 (kitchen)
- 9.7h ago: absent from dish_rack_k1 (kitchen)
recall_time_pattern(headphones_mara, +/-6h) ->
sightings of headphones_mara near hour 07:00 (+/-6h), by receptacle:
- kitchen_table_k1 (kitchen): 15x, newest 26.4h ago
- counter_k1 (kitchen): 6x, newest 138.1h ago
- dish_rack_k1 (kitchen): 2x, newest 117.3h ago
- entry_hook_e1 (entry): 1x, newest 75.0h ago
sense kitchen_table_k1 -> headphones_mara NOT here (contents: bowl_shared_2)
sense couch_l1 -> headphones_mara NOT here (contents: blanket_mara, watering_can_mara)
sense bed_b1 -> headphones_mara NOT here (contents: empty)
sense nightstand_b1 -> headphones_mara NOT here (contents: glasses_mara)
sense tv_stand_l1 -> headphones_mara NOT here (contents: empty)
fallback to belief argmax: step cap reached
```
answer: OUT_OF_HOUSE  truth: OUT_OF_HOUSE  correct: True  senses: 5  overridden: False
stats: {"recalls": 3, "senses": 5, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 1, "step_cap_hits": 1}

## q1415  [truly_out]
object tablet_mara at t=1598415 (day 18)
```
recall_object_history(tablet_mara) ->
memory of tablet_mara, newest first:
- 0.2h ago: absent from entry_table_e1 (entry)
- 0.8h ago: absent from nightstand_b1 (bedroom)
- 0.9h ago: absent from entry_floor_e1 (entry)
- 1.1h ago: absent from couch_l1 (living)
- 2.3h ago: absent from entry_table_e1 (entry)
- 2.3h ago: absent from entry_hook_e1 (entry)
- 2.3h ago: absent from entry_floor_e1 (entry)
- 3.4h ago: absent from kitchen_table_k1 (kitchen)
- 4.1h ago: absent from tv_stand_l1 (living)
- 4.1h ago: absent from nightstand_b1 (bedroom)
- 4.1h ago: absent from bed_b1 (bedroom)
- 4.1h ago: absent from couch_l1 (living)
recall_time_pattern(tablet_mara, +/-1h) ->
sightings of tablet_mara near hour 12:00 (+/-1h), by receptacle:
- chair_k1 (kitchen): 2x, newest 287.5h ago
- coffee_table_l1 (living): 1x, newest 313.0h ago
sense couch_l1 -> tablet_mara NOT here (contents: blanket_mara, watering_can_mara)
sense coffee_table_l1 -> tablet_mara NOT here (contents: remote_shared_1)
recall_object_history(tablet_mara) ->
memory of tablet_mara, newest first:
- 0.0h ago: absent from coffee_table_l1 (living)
- 0.0h ago: absent from couch_l1 (living)
- 0.2h ago: absent from entry_table_e1 (entry)
- 0.8h ago: absent from nightstand_b1 (bedroom)
- 0.9h ago: absent from entry_floor_e1 (entry)
- 1.1h ago: absent from couch_l1 (living)
- 2.3h ago: absent from entry_table_e1 (entry)
- 2.3h ago: absent from entry_hook_e1 (entry)
- 2.3h ago: absent from entry_floor_e1 (entry)
- 3.4h ago: absent from kitchen_table_k1 (kitchen)
- 4.1h ago: absent from tv_stand_l1 (living)
- 4.1h ago: absent from nightstand_b1 (bedroom)
sense tv_stand_l1 -> tablet_mara NOT here (contents: empty)
sense desk_b1 -> tablet_mara NOT here (contents: empty)
recall_object_history(tablet_mara) ->
memory of tablet_mara, newest first:
- 0.0h ago: absent from desk_b1 (bedroom)
- 0.0h ago: absent from tv_stand_l1 (living)
- 0.0h ago: absent from coffee_table_l1 (living)
- 0.0h ago: absent from couch_l1 (living)
- 0.2h ago: absent from entry_table_e1 (entry)
- 0.8h ago: absent from nightstand_b1 (bedroom)
- 0.9h ago: absent from entry_floor_e1 (entry)
- 1.1h ago: absent from couch_l1 (living)
- 2.3h ago: absent from entry_table_e1 (entry)
- 2.3h ago: absent from entry_hook_e1 (entry)
- 2.3h ago: absent from entry_floor_e1 (entry)
- 3.4h ago: absent from kitchen_table_k1 (kitchen)
fallback to belief argmax: step cap reached
```
answer: ON_PERSON  truth: OUT_OF_HOUSE  correct: False  senses: 4  overridden: False
stats: {"recalls": 4, "senses": 4, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 1, "step_cap_hits": 1}

## q1429  [came_back]
object backpack_mara at t=1620702 (day 18)
```
recall_object_history(backpack_mara) ->
memory of backpack_mara, newest first:
- 2.1h ago: absent from tv_stand_l1 (living)
- 2.1h ago: absent from couch_l1 (living)
- 2.1h ago: absent from coffee_table_l1 (living)
- 2.1h ago: absent from bookshelf_l1 (living)
- 2.1h ago: absent from armchair_l1 (living)
- 3.2h ago: absent from coffee_table_l1 (living)
- 3.9h ago: absent from entry_table_e1 (entry)
- 4.5h ago: absent from couch_l1 (living)
- 5.2h ago: absent from nightstand_b1 (bedroom)
- 5.2h ago: absent from desk_b1 (bedroom)
- 5.2h ago: absent from bedroom_floor_b1 (bedroom)
- 5.2h ago: absent from bed_b1 (bedroom)
answer OUT_OF_HOUSE
```
answer: OUT_OF_HOUSE  truth: entry_hook_e1  correct: False  senses: 0  overridden: True
stats: {"recalls": 1, "senses": 0, "answered_from_memory": 1, "answered_by_selector": 1, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q1879  [came_back]
object laundry_basket_mara at t=2056167 (day 23)
```
recall_object_history(laundry_basket_mara) ->
memory of laundry_basket_mara, newest first:
- 0.3h ago: absent from sink_k1 (kitchen)
- 0.3h ago: absent from kitchen_table_k1 (kitchen)
- 0.3h ago: absent from dish_rack_k1 (kitchen)
- 0.3h ago: absent from cupboard_k1 (kitchen)
- 0.3h ago: absent from counter_k1 (kitchen)
- 0.3h ago: absent from chair_k2 (kitchen)
- 0.3h ago: absent from chair_k1 (kitchen)
- 0.4h ago: absent from couch_l1 (living)
- 0.8h ago: absent from coffee_table_l1 (living)
- 1.7h ago: absent from couch_l1 (living)
- 2.4h ago: absent from coffee_table_l1 (living)
- 3.6h ago: absent from tv_stand_l1 (living)
recall_object_history(laundry_basket_mara) ->
memory of laundry_basket_mara, newest first:
- 0.3h ago: absent from sink_k1 (kitchen)
- 0.3h ago: absent from kitchen_table_k1 (kitchen)
- 0.3h ago: absent from dish_rack_k1 (kitchen)
- 0.3h ago: absent from cupboard_k1 (kitchen)
- 0.3h ago: absent from counter_k1 (kitchen)
- 0.3h ago: absent from chair_k2 (kitchen)
- 0.3h ago: absent from chair_k1 (kitchen)
- 0.4h ago: absent from couch_l1 (living)
- 0.8h ago: absent from coffee_table_l1 (living)
- 1.7h ago: absent from couch_l1 (living)
- 2.4h ago: absent from coffee_table_l1 (living)
- 3.6h ago: absent from tv_stand_l1 (living)
recall_object_history(laundry_basket_mara) ->
memory of laundry_basket_mara, newest first:
- 0.3h ago: absent from sink_k1 (kitchen)
- 0.3h ago: absent from kitchen_table_k1 (kitchen)
- 0.3h ago: absent from dish_rack_k1 (kitchen)
- 0.3h ago: absent from cupboard_k1 (kitchen)
- 0.3h ago: absent from counter_k1 (kitchen)
- 0.3h ago: absent from chair_k2 (kitchen)
- 0.3h ago: absent from chair_k1 (kitchen)
- 0.4h ago: absent from couch_l1 (living)
- 0.8h ago: absent from coffee_table_l1 (living)
- 1.7h ago: absent from couch_l1 (living)
- 2.4h ago: absent from coffee_table_l1 (living)
- 3.6h ago: absent from tv_stand_l1 (living)
recall_time_pattern(laundry_basket_mara, +/-1h) ->
sightings of laundry_basket_mara near hour 19:00 (+/-1h), by receptacle:
- bedroom_floor_b1 (bedroom): 5x, newest 24.4h ago
sense bedroom_floor_b1 -> FOUND laundry_basket_mara
answer bedroom_floor_b1 (found)
```
answer: bedroom_floor_b1  truth: bedroom_floor_b1  correct: True  senses: 1  overridden: False
stats: {"recalls": 4, "senses": 1, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q1979  [truly_out]
object suitcase_mara at t=2129129 (day 24)
```
recall_object_history(suitcase_mara) ->
memory of suitcase_mara, newest first:
- 0.2h ago: absent from sink_k1 (kitchen)
- 0.2h ago: absent from kitchen_table_k1 (kitchen)
- 0.2h ago: absent from dish_rack_k1 (kitchen)
- 0.2h ago: absent from cupboard_k1 (kitchen)
- 0.2h ago: absent from counter_k1 (kitchen)
- 0.2h ago: absent from chair_k2 (kitchen)
- 0.2h ago: absent from chair_k1 (kitchen)
- 1.1h ago: absent from sink_k1 (kitchen)
- 2.5h ago: absent from sink_k1 (kitchen)
- 3.3h ago: absent from tv_stand_l1 (living)
- 3.3h ago: absent from couch_l1 (living)
- 3.3h ago: absent from coffee_table_l1 (living)
recall_object_history(suitcase_mara) ->
memory of suitcase_mara, newest first:
- 0.2h ago: absent from sink_k1 (kitchen)
- 0.2h ago: absent from kitchen_table_k1 (kitchen)
- 0.2h ago: absent from dish_rack_k1 (kitchen)
- 0.2h ago: absent from cupboard_k1 (kitchen)
- 0.2h ago: absent from counter_k1 (kitchen)
- 0.2h ago: absent from chair_k2 (kitchen)
- 0.2h ago: absent from chair_k1 (kitchen)
- 1.1h ago: absent from sink_k1 (kitchen)
- 2.5h ago: absent from sink_k1 (kitchen)
- 3.3h ago: absent from tv_stand_l1 (living)
- 3.3h ago: absent from couch_l1 (living)
- 3.3h ago: absent from coffee_table_l1 (living)
recall_object_history(suitcase_mara) ->
memory of suitcase_mara, newest first:
- 0.2h ago: absent from sink_k1 (kitchen)
- 0.2h ago: absent from kitchen_table_k1 (kitchen)
- 0.2h ago: absent from dish_rack_k1 (kitchen)
- 0.2h ago: absent from cupboard_k1 (kitchen)
- 0.2h ago: absent from counter_k1 (kitchen)
- 0.2h ago: absent from chair_k2 (kitchen)
- 0.2h ago: absent from chair_k1 (kitchen)
- 1.1h ago: absent from sink_k1 (kitchen)
- 2.5h ago: absent from sink_k1 (kitchen)
- 3.3h ago: absent from tv_stand_l1 (living)
- 3.3h ago: absent from couch_l1 (living)
- 3.3h ago: absent from coffee_table_l1 (living)
recall_object_history(suitcase_mara) ->
memory of suitcase_mara, newest first:
- 0.2h ago: absent from sink_k1 (kitchen)
- 0.2h ago: absent from kitchen_table_k1 (kitchen)
- 0.2h ago: absent from dish_rack_k1 (kitchen)
- 0.2h ago: absent from cupboard_k1 (kitchen)
- 0.2h ago: absent from counter_k1 (kitchen)
- 0.2h ago: absent from chair_k2 (kitchen)
- 0.2h ago: absent from chair_k1 (kitchen)
- 1.1h ago: absent from sink_k1 (kitchen)
- 2.5h ago: absent from sink_k1 (kitchen)
- 3.3h ago: absent from tv_stand_l1 (living)
- 3.3h ago: absent from couch_l1 (living)
- 3.3h ago: absent from coffee_table_l1 (living)
rejected: recall cap reached (4 per question)
fallback to belief argmax: illegal action: recall cap reached (4 per question)
```
answer: bedroom_floor_b1  truth: OUT_OF_HOUSE  correct: False  senses: 0  overridden: False
stats: {"recalls": 4, "senses": 0, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 2, "fallbacks": 1, "step_cap_hits": 0}

## q2075  [came_back]
object tablet_mara at t=2288905 (day 26)
```
recall_object_history(tablet_mara) ->
memory of tablet_mara, newest first:
- 0.8h ago: absent from sink_k1 (kitchen)
- 0.8h ago: absent from kitchen_table_k1 (kitchen)
- 0.8h ago: absent from dish_rack_k1 (kitchen)
- 0.8h ago: absent from cupboard_k1 (kitchen)
- 0.8h ago: absent from counter_k1 (kitchen)
- 0.8h ago: absent from chair_k2 (kitchen)
- 0.8h ago: absent from chair_k1 (kitchen)
- 0.8h ago: absent from couch_l1 (living)
- 1.2h ago: absent from counter_k1 (kitchen)
- 1.7h ago: absent from bedroom_floor_b1 (bedroom)
- 3.3h ago: absent from tv_stand_l1 (living)
- 3.3h ago: absent from couch_l1 (living)
recall_object_history(tablet_mara) ->
memory of tablet_mara, newest first:
- 0.8h ago: absent from sink_k1 (kitchen)
- 0.8h ago: absent from kitchen_table_k1 (kitchen)
- 0.8h ago: absent from dish_rack_k1 (kitchen)
- 0.8h ago: absent from cupboard_k1 (kitchen)
- 0.8h ago: absent from counter_k1 (kitchen)
- 0.8h ago: absent from chair_k2 (kitchen)
- 0.8h ago: absent from chair_k1 (kitchen)
- 0.8h ago: absent from couch_l1 (living)
- 1.2h ago: absent from counter_k1 (kitchen)
- 1.7h ago: absent from bedroom_floor_b1 (bedroom)
- 3.3h ago: absent from tv_stand_l1 (living)
- 3.3h ago: absent from couch_l1 (living)
recall_time_pattern(tablet_mara, +/-1h) ->
sightings of tablet_mara near hour 11:00 (+/-1h), by receptacle:
- coffee_table_l1 (living): 2x, newest 145.0h ago
- chair_k1 (kitchen): 2x, newest 479.3h ago
sense coffee_table_l1 -> FOUND tablet_mara
answer coffee_table_l1 (found)
```
answer: coffee_table_l1  truth: coffee_table_l1  correct: True  senses: 1  overridden: False
stats: {"recalls": 3, "senses": 1, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q2139  [came_back]
object yoga_mat_mara at t=2300614 (day 26)
```
recall_object_history(yoga_mat_mara) ->
memory of yoga_mat_mara, newest first:
- 0.3h ago: absent from bathroom_shelf_ba1 (bathroom)
- 1.2h ago: absent from dish_rack_k1 (kitchen)
- 1.3h ago: absent from towel_rack_ba1 (bathroom)
- 1.3h ago: absent from bathroom_shelf_ba1 (bathroom)
- 1.3h ago: absent from kitchen_table_k1 (kitchen)
- 1.4h ago: absent from bedroom_floor_b1 (bedroom)
- 1.5h ago: seen at couch_l1 (living)
- 2.4h ago: absent from dish_rack_k1 (kitchen)
- 2.5h ago: absent from kitchen_table_k1 (kitchen)
- 2.7h ago: absent from counter_k1 (kitchen)
- 2.9h ago: seen at couch_l1 (living)
- 3.1h ago: absent from bedroom_floor_b1 (bedroom)
sense couch_l1 -> FOUND yoga_mat_mara
answer couch_l1 (found)
```
answer: couch_l1  truth: couch_l1  correct: True  senses: 1  overridden: False
stats: {"recalls": 1, "senses": 1, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## q2212  [stale_in_house]
object backpack_mara at t=2360737 (day 27)
```
recall_object_history(backpack_mara) ->
memory of backpack_mara, newest first:
- 0.3h ago: absent from nightstand_b1 (bedroom)
- 0.5h ago: absent from bedroom_floor_b1 (bedroom)
- 0.5h ago: absent from kitchen_table_k1 (kitchen)
- 0.6h ago: absent from bathroom_shelf_ba1 (bathroom)
- 9.7h ago: absent from tv_stand_l1 (living)
- 9.7h ago: absent from couch_l1 (living)
- 9.7h ago: absent from coffee_table_l1 (living)
- 9.7h ago: absent from bookshelf_l1 (living)
- 9.7h ago: absent from armchair_l1 (living)
- 12.5h ago: absent from nightstand_b1 (bedroom)
- 12.5h ago: absent from desk_b1 (bedroom)
- 12.5h ago: absent from bedroom_floor_b1 (bedroom)
recall_object_history(backpack_mara) ->
memory of backpack_mara, newest first:
- 0.3h ago: absent from nightstand_b1 (bedroom)
- 0.5h ago: absent from bedroom_floor_b1 (bedroom)
- 0.5h ago: absent from kitchen_table_k1 (kitchen)
- 0.6h ago: absent from bathroom_shelf_ba1 (bathroom)
- 9.7h ago: absent from tv_stand_l1 (living)
- 9.7h ago: absent from couch_l1 (living)
- 9.7h ago: absent from coffee_table_l1 (living)
- 9.7h ago: absent from bookshelf_l1 (living)
- 9.7h ago: absent from armchair_l1 (living)
- 12.5h ago: absent from nightstand_b1 (bedroom)
- 12.5h ago: absent from desk_b1 (bedroom)
- 12.5h ago: absent from bedroom_floor_b1 (bedroom)
recall_object_history(backpack_mara) ->
memory of backpack_mara, newest first:
- 0.3h ago: absent from nightstand_b1 (bedroom)
- 0.5h ago: absent from bedroom_floor_b1 (bedroom)
- 0.5h ago: absent from kitchen_table_k1 (kitchen)
- 0.6h ago: absent from bathroom_shelf_ba1 (bathroom)
- 9.7h ago: absent from tv_stand_l1 (living)
- 9.7h ago: absent from couch_l1 (living)
- 9.7h ago: absent from coffee_table_l1 (living)
- 9.7h ago: absent from bookshelf_l1 (living)
- 9.7h ago: absent from armchair_l1 (living)
- 12.5h ago: absent from nightstand_b1 (bedroom)
- 12.5h ago: absent from desk_b1 (bedroom)
- 12.5h ago: absent from bedroom_floor_b1 (bedroom)
recall_time_pattern(backpack_mara, +/-6h) ->
sightings of backpack_mara near hour 07:00 (+/-6h), by receptacle:
- entry_hook_e1 (entry): 12x, newest 73.9h ago
- chair_k1 (kitchen): 5x, newest 499.3h ago
- kitchen_table_k1 (kitchen): 3x, newest 18.0h ago
- dish_rack_k1 (kitchen): 3x, newest 357.1h ago
- sink_k1 (kitchen): 1x, newest 313.2h ago
sense entry_hook_e1 -> FOUND backpack_mara
answer entry_hook_e1 (found)
```
answer: entry_hook_e1  truth: entry_hook_e1  correct: True  senses: 1  overridden: False
stats: {"recalls": 4, "senses": 1, "answered_from_memory": 0, "answered_by_selector": 0, "unparseable": 0, "illegal": 0, "fallbacks": 0, "step_cap_hits": 0}

## Cell totals
accuracy 17/27
cache: {"hits": 0, "misses": 129, "hit_rate": 0.0, "new_prompt_tokens": 110391, "new_completion_tokens": 2970, "cache_path": "/home/oliver/robot/dynamic_home_eqa/results/star_memory_loop/llm_cache/LastObservation__StarQwen__24.jsonl", "entries": 129}
wall: 25.1s