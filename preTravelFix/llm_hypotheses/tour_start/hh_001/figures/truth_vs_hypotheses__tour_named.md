# Ground truth vs hypotheses — hh_001 (working_professional_solo) · tour_named

Truth from the bank's program: activity blocks per day, what each object does during and after each activity, and its home. Hypotheses in the same layout. Objects are the join key; activity names differ by construction.

## day 0

### Activity schedule — truth

| activity | days | ~start | ~length | where | objects carried / placed during | landed after |
|---|---|---|---|---|---|---|
| night_sleep | both (20wd/8we, 7.0×/wk) | 0.0h | 5.0h | bed_b1 |  |  |
| wake_up | both (20wd/8we, 7.0×/wk) | 5.0h | 0.2h | bed_b1 |  | phone_mara→nightstand_b1 |
| take_medication | both (20wd/8we, 7.0×/wk) | 5.2h | 0.1h | bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1 |
| shower | both (19wd/3we, 5.5×/wk) | 5.2h | 0.2h | bathroom_shelf_ba1 |  | towel_mara→towel_rack_ba1 |
| get_ready | weekday (19wd/0we, 4.8×/wk) | 5.5h | 0.3h | bathroom_shelf_ba1 | hairbrush_mara→bathroom_shelf_ba1 | hairbrush_mara→bathroom_shelf_ba1, makeup_kit_mara→bathroom_shelf_ba1 |
| coffee | both (19wd/8we, 6.8×/wk) | 5.8h | 0.2h | counter_k1 | mug_mara→counter_k1 | mug_mara→counter_k1 |
| breakfast | both (20wd/8we, 7.0×/wk) | 6.0h | 0.2h | kitchen_table_k1 | bowl_shared_2→kitchen_table_k1, pan_shared_1→kitchen_table_k1 | bowl_shared_2→kitchen_table_k1, pan_shared_1→counter_k1 |
| meal_prep | both (20wd/5we, 6.2×/wk) | 6.2h | 0.2h | counter_k1 | pen_mara→counter_k1, plate_shared_2→counter_k1 | backpack_mara→chair_k1, pen_mara→kitchen_table_k1, plate_shared_2→counter_k1 |
| appointment | weekday (1wd/0we, 0.2×/wk) | 7.3h | 0.7h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | makeup_kit_mara→bathroom_shelf_ba1, wallet_mara→entry_table_e1, suitcase_mara→bedroom_floor_b1 |
| pet_care | weekend (0wd/1we, 0.2×/wk) | 8.0h | 0.2h | counter_k1 | watering_can_mara→counter_k1 | watering_can_mara→sink_k1 |
| nap | weekend (0wd/1we, 0.2×/wk) | 9.0h | 1.2h | bed_b1 |  |  |
| groceries | weekend (0wd/3we, 0.8×/wk) | 9.3h | 0.9h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | towel_mara→bedroom_floor_b1, keys_mara→entry_table_e1, umbrella_mara→entry_floor_e1, jacket_mara→entry_hook_e1, book_mara→couch_l1 … |
| batch_cooking | weekend (0wd/3we, 0.8×/wk) | 9.5h | 1.5h | counter_k1 | pot_shared_1→counter_k1 | tablet_mara→counter_k1, pot_shared_1→sink_k1 |
| laundry | weekend (0wd/4we, 1.0×/wk) | 9.5h | 0.5h | bedroom_floor_b1 |  | towel_mara→bedroom_floor_b1, laundry_basket_mara→bedroom_floor_b1 |
| work_away | weekday (18wd/0we, 4.5×/wk) | 9.6h | 4.1h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | phone_mara→kitchen_table_k1, backpack_mara→entry_hook_e1, plate_shared_2→kitchen_table_k1, laptop_mara→kitchen_table_k1, keys_mara→entry_table_e1 … |
| take_out_bins | weekend (0wd/1we, 0.2×/wk) | 10.0h | 0.2h | entry_floor_e1 |  |  |
| deep_clean | weekend (0wd/2we, 0.5×/wk) | 10.8h | 1.1h | couch_l1 | remote_shared_1→couch_l1, vacuum_cleaner_shared_1→couch_l1 | remote_shared_1→coffee_table_l1, laundry_basket_mara→bedroom_floor_b1, vacuum_cleaner_shared_1→bedroom_floor_b1, watering_can_mara→sink_k1 |
| walk | both (2wd/6we, 2.0×/wk) | 11.5h | 0.6h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | keys_mara→entry_table_e1, umbrella_mara→entry_floor_e1, jacket_mara→entry_hook_e1, book_mara→couch_l1 |
| tidy_up | both (4wd/5we, 2.2×/wk) | 11.5h | 0.3h | kitchen_table_k1 | pen_mara→kitchen_table_k1, bowl_shared_1→kitchen_table_k1 | pen_mara→kitchen_table_k1, laptop_mara→kitchen_table_k1, keys_mara→entry_table_e1, umbrella_mara→entry_floor_e1, bowl_shared_1→entry_table_e1 … |
| work_home | weekday (4wd/0we, 1.0×/wk) | 11.7h | 1.7h | kitchen_table_k1 | glasses_mara→kitchen_table_k1 | laptop_mara→kitchen_table_k1, charger_mara→kitchen_table_k1, notebook_mara→kitchen_table_k1, glasses_mara→kitchen_table_k1 |
| relax | weekend (0wd/1we, 0.2×/wk) | 12.0h | 1.0h | couch_l1 | blanket_mara→couch_l1 | blanket_mara→couch_l1 |
| wash_dishes | both (6wd/8we, 3.5×/wk) | 12.1h | 0.2h | sink_k1 | mug_mara→sink_k1, plate_shared_1→sink_k1, pot_shared_1→sink_k1 | mug_mara→dish_rack_k1, lunchbox_mara→counter_k1, plate_shared_1→dish_rack_k1, pot_shared_1→dish_rack_k1 |
| lunch | both (20wd/8we, 7.0×/wk) | 12.2h | 0.4h | kitchen_table_k1 | plate_shared_2→kitchen_table_k1 | plate_shared_2→kitchen_table_k1 |
| day_sleep | weekday (1wd/0we, 0.2×/wk) | 12.4h | 1.6h | bed_b1 |  |  |
| traveling | both (19wd/3we, 5.5×/wk) | 13.1h | 0.3h | None |  |  |
| hobby | both (1wd/1we, 0.5×/wk) | 13.4h | 0.8h | couch_l1 |  |  |
| reading | both (5wd/8we, 3.2×/wk) | 14.0h | 1.1h | couch_l1 | mug_mara→couch_l1, glasses_mara→couch_l1 | mug_mara→coffee_table_l1, book_mara→couch_l1, glasses_mara→coffee_table_l1 |
| video_call | both (1wd/1we, 0.5×/wk) | 14.1h | 0.8h | couch_l1 |  | headphones_mara→coffee_table_l1, tablet_mara→coffee_table_l1 |
| put_away_dishes | both (1wd/1we, 0.5×/wk) | 14.3h | 0.2h | dish_rack_k1 | bowl_shared_2→dish_rack_k1, mug_shared_1→dish_rack_k1 | bowl_shared_2→cupboard_k1, mug_shared_1→cupboard_k1 |
| lie_down | both (3wd/1we, 1.0×/wk) | 14.6h | 1.1h | bed_b1 |  |  |
| errands | weekday (1wd/0we, 0.2×/wk) | 15.7h | 0.5h | None |  |  |
| gym | both (4wd/3we, 1.8×/wk) | 16.0h | 0.7h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | backpack_mara→entry_hook_e1, yoga_mat_mara→couch_l1, water_bottle_mara→couch_l1 |
| night_out | weekday (1wd/0we, 0.2×/wk) | 16.0h | 2.0h | None |  |  |
| snack | weekday (7wd/0we, 1.8×/wk) | 16.2h | 0.2h | counter_k1 |  | bowl_shared_1→entry_table_e1 |
| socialise_home | weekday (1wd/0we, 0.2×/wk) | 17.2h | 1.8h | couch_l1 | mug_shared_1→couch_l1 | mug_shared_1→coffee_table_l1 |
| dinner | both (18wd/8we, 6.5×/wk) | 17.3h | 0.5h | kitchen_table_k1 | pan_shared_1→kitchen_table_k1, plate_shared_1→kitchen_table_k1 | pan_shared_1→sink_k1, plate_shared_1→kitchen_table_k1 |
| watch_tv | both (6wd/1we, 1.8×/wk) | 17.4h | 1.2h | couch_l1 | remote_shared_1→couch_l1, blanket_mara→couch_l1 | remote_shared_1→couch_l1, blanket_mara→couch_l1 |
| phone_time | both (6wd/1we, 1.8×/wk) | 17.6h | 0.2h | couch_l1 |  | phone_mara→couch_l1 |
| bedtime_routine | both (14wd/7we, 5.2×/wk) | 20.5h | 0.5h | bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1, hairbrush_mara→bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1, hairbrush_mara→bathroom_shelf_ba1, water_bottle_mara→nightstand_b1 |

### Activity schedule — hyp1: Mara is a WFH professional who rarely leaves; kitchen table is her permanent office and carry items stay at the entry al

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_routine | both (7×/wk) | 7.0h | 1.0h | mug_mara→counter_k1 (usually, left); water_bottle_mara→counter_k1 (usually, left) |
| work_day | weekday (5×/wk) | 8.5h | 8.5h | phone_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left); headphones_mara→kitchen_table_k1 (usually, left) |
| weekend_yoga | weekend (2×/wk) | 9.0h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, returned); headphones_mara→bedroom_floor_b1 (sometimes, returned) |
| lunch | both (7×/wk) | 12.5h | 1.0h | plate_shared_1→kitchen_table_k1 (usually, left); bowl_shared_1→kitchen_table_k1 (sometimes, left); water_bottle_mara→kitchen_table_k1 (usually, left) |
| evening_relax | both (7×/wk) | 19.5h | 3.0h | remote_shared_1→couch_l1 (usually, left); tablet_mara→couch_l1 (usually, left); blanket_mara→couch_l1 (usually, left) |

### Activity schedule — hyp2: Mara commutes to an external office; kitchen-table items are just overnight rest spots and she carries her full work kit

| activity | days | start | length | moves |
|---|---|---|---|---|
| commute_out | weekday (5×/wk) | 7.8h | 0.5h | keys_mara→OUT_OF_HOUSE (almost_always, left); wallet_mara→OUT_OF_HOUSE (almost_always, left); jacket_mara→OUT_OF_HOUSE (usually, left); backpack_mara→OUT_OF_HOUSE (usually, left); laptop_mara→OUT_OF_HOUSE (usually, left) … |
| weekend_yoga | weekend (2×/wk) | 9.0h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, returned); water_bottle_mara→bedroom_floor_b1 (usually, returned) |
| weekend_cooking | weekend (1×/wk) | 11.0h | 2.0h | pot_shared_1→counter_k1 (usually, returned); pan_shared_1→counter_k1 (usually, returned); bowl_shared_2→kitchen_table_k1 (usually, left) |
| commute_home | weekday (5×/wk) | 17.2h | 0.5h | keys_mara→entry_table_e1 (almost_always, returned); wallet_mara→entry_table_e1 (almost_always, returned); jacket_mara→entry_hook_e1 (usually, returned); backpack_mara→entry_hook_e1 (usually, returned); laptop_mara→kitchen_table_k1 (usually, returned) … |
| evening_tv | both (7×/wk) | 19.5h | 2.5h | remote_shared_1→couch_l1 (usually, left); tablet_mara→couch_l1 (sometimes, left) |

### Activity schedule — hyp3: Mara works an evening shift (16:00-23:30) so she is home all day using the kitchen table, then leaves in the late aftern

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_recovery | weekday (5×/wk) | 6.5h | 1.0h | mug_mara→kitchen_table_k1 (usually, left); water_bottle_mara→kitchen_table_k1 (usually, left) |
| daytime_work | weekday (5×/wk) | 9.0h | 6.5h | laptop_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left); phone_mara→kitchen_table_k1 (usually, left) |
| weekend_yoga | weekend (2×/wk) | 10.0h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, returned); headphones_mara→bedroom_floor_b1 (usually, returned); water_bottle_mara→bedroom_floor_b1 (usually, returned) |
| shift_out | weekday (5×/wk) | 15.5h | 0.5h | keys_mara→OUT_OF_HOUSE (almost_always, left); wallet_mara→OUT_OF_HOUSE (almost_always, left); jacket_mara→OUT_OF_HOUSE (usually, left); phone_mara→OUT_OF_HOUSE (almost_always, left); backpack_mara→OUT_OF_HOUSE (sometimes, left) |
| shift_home | weekday (5×/wk) | 23.5h | 0.5h | keys_mara→entry_table_e1 (almost_always, returned); wallet_mara→entry_table_e1 (almost_always, returned); jacket_mara→entry_hook_e1 (usually, returned); phone_mara→nightstand_b1 (usually, returned); backpack_mara→entry_hook_e1 (sometimes, returned) |

### Activity schedule — hyp4: Mara is a student attending daytime classes; she carries notebook, pen, laptop, and backpack out each morning and the ki

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_routine | both (7×/wk) | 7.0h | 1.0h | mug_mara→counter_k1 (usually, left); water_bottle_mara→counter_k1 (usually, left) |
| class_out | weekday (5×/wk) | 8.2h | 0.5h | backpack_mara→OUT_OF_HOUSE (almost_always, left); laptop_mara→OUT_OF_HOUSE (usually, left); notebook_mara→OUT_OF_HOUSE (almost_always, left); pen_mara→OUT_OF_HOUSE (almost_always, left); keys_mara→OUT_OF_HOUSE (almost_always, left) … |
| weekend_yoga | weekend (2×/wk) | 9.5h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, returned); water_bottle_mara→bedroom_floor_b1 (usually, returned) |
| weekend_cooking | weekend (1×/wk) | 12.0h | 2.0h | pot_shared_1→counter_k1 (usually, returned); bowl_shared_1→kitchen_table_k1 (usually, left); plate_shared_1→kitchen_table_k1 (usually, left) |
| class_return | weekday (5×/wk) | 15.0h | 0.5h | backpack_mara→entry_hook_e1 (almost_always, returned); laptop_mara→kitchen_table_k1 (usually, returned); notebook_mara→kitchen_table_k1 (almost_always, returned); pen_mara→kitchen_table_k1 (almost_always, returned); keys_mara→entry_table_e1 (almost_always, returned) … |
| study_evening | weekday (5×/wk) | 18.0h | 3.0h | laptop_mara→kitchen_table_k1 (usually, left); notebook_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left); phone_mara→kitchen_table_k1 (sometimes, left) |

### Activity schedule — hyp5: Mara works from home but has a structured active routine: weekday lunch-break gym sessions and weekend social outings; t

| activity | days | start | length | moves |
|---|---|---|---|---|
| work_day | weekday (5×/wk) | 9.0h | 7.0h | laptop_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (usually, left); headphones_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left); phone_mara→kitchen_table_k1 (usually, left) |
| weekend_yoga | weekend (2×/wk) | 9.0h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, returned); headphones_mara→bedroom_floor_b1 (usually, returned); water_bottle_mara→bedroom_floor_b1 (usually, returned) |
| weekend_social | weekend (1×/wk) | 16.0h | 4.0h | keys_mara→OUT_OF_HOUSE (usually, returned); wallet_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (usually, returned); jacket_mara→OUT_OF_HOUSE (sometimes, returned) |
| gym_session | weekday (3×/wk) | 18.0h | 1.5h | water_bottle_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (usually, returned); jacket_mara→OUT_OF_HOUSE (usually, returned); keys_mara→OUT_OF_HOUSE (almost_always, returned) |
| cooking_dinner | both (5×/wk) | 18.5h | 1.0h | pot_shared_1→counter_k1 (usually, returned); pan_shared_1→counter_k1 (usually, returned); bowl_shared_1→kitchen_table_k1 (usually, left); plate_shared_1→kitchen_table_k1 (usually, left) |
| evening_tv | both (7×/wk) | 20.0h | 2.5h | remote_shared_1→couch_l1 (usually, left); tablet_mara→couch_l1 (usually, left); blanket_mara→couch_l1 (usually, left) |

### Per object — truth in the first column, each hypothesis beside it

| object | TRUTH | hyp1 | hyp2 | hyp3 | hyp4 | hyp5 |
|---|---|---|---|---|---|---|
| backpack_mara | home **entry_hook_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: meal_prep→chair_k1(0.5), work_away→entry_hook_e1(0.8), gym→entry_hook_e1(0.6) | — *(fallback)* | commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→entry_hook_e1 (usua,ret) | shift_out→OUT_OF_HOUSE (some,lef)<br>shift_home→entry_hook_e1 (some,ret) | class_out→OUT_OF_HOUSE (almo,lef)<br>class_return→entry_hook_e1 (almo,ret) | — *(fallback)* |
| blanket_mara | home **couch_l1**<br>during: watch_tv→couch_l1, relax→couch_l1<br>after: watch_tv→couch_l1(0.8), relax→couch_l1(0.8) | evening_relax→couch_l1 (usua,lef) | — *(fallback)* | — *(fallback)* | — *(fallback)* | evening_tv→couch_l1 (usua,lef) |
| book_mara | home **bookshelf_l1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→couch_l1(0.2), reading→couch_l1(0.6), walk→couch_l1(0.2) … | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| bowl_shared_1 | home **entry_table_e1**<br>during: tidy_up→kitchen_table_k1<br>after: tidy_up→entry_table_e1(0.9), snack→entry_table_e1(0.2) | lunch→kitchen_table_k1 (some,lef) | — *(fallback)* | — *(fallback)* | weekend_cooking→kitchen_table_k1 (usua,lef) | cooking_dinner→kitchen_table_k1 (usua,lef) |
| bowl_shared_2 | home **cupboard_k1**<br>during: breakfast→kitchen_table_k1, put_away_dishes→dish_rack_k1<br>after: breakfast→kitchen_table_k1(0.5), put_away_dishes→cupboard_k1(0.8) | — *(fallback)* | weekend_cooking→kitchen_table_k1 (usua,lef) | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| charger_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→kitchen_table_k1(0.6), work_home→kitchen_table_k1(0.9) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | work_day→kitchen_table_k1 (usua,lef) |
| glasses_mara | home **kitchen_table_k1**<br>during: reading→couch_l1, work_home→kitchen_table_k1<br>after: reading→coffee_table_l1(0.5), work_home→kitchen_table_k1(0.8) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| hairbrush_mara | home **bathroom_shelf_ba1**<br>during: get_ready→bathroom_shelf_ba1, bedtime_routine→bathroom_shelf_ba1<br>after: get_ready→bathroom_shelf_ba1(0.8), bedtime_routine→bathroom_shelf_ba1(0.6) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| headphones_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→kitchen_table_k1(0.5), video_call→coffee_table_l1(0.6) | work_day→kitchen_table_k1 (usua,lef)<br>weekend_yoga→bedroom_floor_b1 (some,ret) | — *(fallback)* | weekend_yoga→bedroom_floor_b1 (usua,ret) | — *(fallback)* | work_day→kitchen_table_k1 (usua,lef)<br>weekend_yoga→bedroom_floor_b1 (usua,ret) |
| jacket_mara | home **entry_hook_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→entry_hook_e1(0.7), walk→entry_hook_e1(0.6), groceries→entry_hook_e1(0.6) | — *(fallback)* | commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→entry_hook_e1 (usua,ret) | shift_out→OUT_OF_HOUSE (usua,lef)<br>shift_home→entry_hook_e1 (usua,ret) | — *(fallback)* | gym_session→OUT_OF_HOUSE (usua,ret)<br>weekend_social→OUT_OF_HOUSE (some,ret) |
| keys_mara | home **entry_table_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: tidy_up→entry_table_e1(0.9), work_away→entry_table_e1(0.8), walk→entry_table_e1(0.7) … | — *(fallback)* | commute_out→OUT_OF_HOUSE (almo,lef)<br>commute_home→entry_table_e1 (almo,ret) | shift_out→OUT_OF_HOUSE (almo,lef)<br>shift_home→entry_table_e1 (almo,ret) | class_out→OUT_OF_HOUSE (almo,lef)<br>class_return→entry_table_e1 (almo,ret) | gym_session→OUT_OF_HOUSE (almo,ret)<br>weekend_social→OUT_OF_HOUSE (usua,ret) |
| laptop_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: tidy_up→kitchen_table_k1(0.8), work_away→kitchen_table_k1(0.8), work_home→kitchen_table_k1(0.9) | — *(fallback)* | commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→kitchen_table_k1 (usua,ret) | daytime_work→kitchen_table_k1 (usua,lef) | class_out→OUT_OF_HOUSE (usua,lef)<br>class_return→kitchen_table_k1 (usua,ret)<br>study_evening→kitchen_table_k1 (usua,lef) | work_day→kitchen_table_k1 (usua,lef) |
| laundry_basket_mara | home **bedroom_floor_b1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: groceries→bedroom_floor_b1(0.8), deep_clean→bedroom_floor_b1(0.2), laundry→bedroom_floor_b1(0.8) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| lunchbox_mara | home **counter_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→sink_k1(0.6), wash_dishes→counter_k1(0.8) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| makeup_kit_mara | home **bathroom_shelf_ba1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: get_ready→bathroom_shelf_ba1(0.8), appointment→bathroom_shelf_ba1(0.6) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| medication_bottle_mara | home **bathroom_shelf_ba1**<br>during: take_medication→bathroom_shelf_ba1, bedtime_routine→bathroom_shelf_ba1<br>after: take_medication→bathroom_shelf_ba1(0.7), bedtime_routine→bathroom_shelf_ba1(0.6) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| mug_mara | home **cupboard_k1**<br>during: coffee→counter_k1, wash_dishes→sink_k1, reading→couch_l1<br>after: coffee→counter_k1(0.6), wash_dishes→dish_rack_k1(0.7), reading→coffee_table_l1(0.6) | work_day→kitchen_table_k1 (usua,lef)<br>morning_routine→counter_k1 (usua,lef) | — *(fallback)* | daytime_work→kitchen_table_k1 (usua,lef)<br>morning_recovery→kitchen_table_k1 (usua,lef) | study_evening→kitchen_table_k1 (usua,lef)<br>morning_routine→counter_k1 (usua,lef) | work_day→kitchen_table_k1 (usua,lef) |
| mug_shared_1 | home **cupboard_k1**<br>during: put_away_dishes→dish_rack_k1, socialise_home→couch_l1<br>after: put_away_dishes→cupboard_k1(0.8), socialise_home→coffee_table_l1(0.5) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| notebook_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→kitchen_table_k1(0.7), work_home→kitchen_table_k1(0.9) | — *(fallback)* | — *(fallback)* | — *(fallback)* | class_out→OUT_OF_HOUSE (almo,lef)<br>class_return→kitchen_table_k1 (almo,ret)<br>study_evening→kitchen_table_k1 (usua,lef) | — *(fallback)* |
| pan_shared_1 | home **cupboard_k1**<br>during: breakfast→kitchen_table_k1, dinner→kitchen_table_k1<br>after: breakfast→counter_k1(0.4), dinner→sink_k1(0.4) | — *(fallback)* | weekend_cooking→counter_k1 (usua,ret) | — *(fallback)* | — *(fallback)* | cooking_dinner→counter_k1 (usua,ret) |
| pen_mara | home **kitchen_table_k1**<br>during: meal_prep→counter_k1, tidy_up→kitchen_table_k1<br>after: meal_prep→kitchen_table_k1(0.6), tidy_up→kitchen_table_k1(0.7) | — *(fallback)* | — *(fallback)* | — *(fallback)* | class_out→OUT_OF_HOUSE (almo,lef)<br>class_return→kitchen_table_k1 (almo,ret) | — *(fallback)* |
| phone_mara | home **nightstand_b1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: wake_up→nightstand_b1(0.8), work_away→kitchen_table_k1(0.5), phone_time→couch_l1(0.5) | work_day→kitchen_table_k1 (usua,lef) | commute_out→OUT_OF_HOUSE (almo,lef)<br>commute_home→nightstand_b1 (usua,ret) | daytime_work→kitchen_table_k1 (usua,lef)<br>shift_out→OUT_OF_HOUSE (almo,lef)<br>shift_home→nightstand_b1 (usua,ret) | study_evening→kitchen_table_k1 (some,lef) | work_day→kitchen_table_k1 (usua,lef)<br>gym_session→OUT_OF_HOUSE (usua,ret)<br>weekend_social→OUT_OF_HOUSE (usua,ret) |
| plate_shared_1 | home **cupboard_k1**<br>during: dinner→kitchen_table_k1, wash_dishes→sink_k1<br>after: dinner→kitchen_table_k1(0.5), wash_dishes→dish_rack_k1(0.8) | lunch→kitchen_table_k1 (usua,lef) | — *(fallback)* | — *(fallback)* | weekend_cooking→kitchen_table_k1 (usua,lef) | cooking_dinner→kitchen_table_k1 (usua,lef) |
| plate_shared_2 | home **cupboard_k1**<br>during: meal_prep→counter_k1, lunch→kitchen_table_k1<br>after: meal_prep→counter_k1(0.6), work_away→kitchen_table_k1(0.5), lunch→kitchen_table_k1(0.5) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| pot_shared_1 | home **cupboard_k1**<br>during: wash_dishes→sink_k1, batch_cooking→counter_k1<br>after: wash_dishes→dish_rack_k1(0.5), batch_cooking→sink_k1(0.6) | — *(fallback)* | weekend_cooking→counter_k1 (usua,ret) | — *(fallback)* | weekend_cooking→counter_k1 (usua,ret) | cooking_dinner→counter_k1 (usua,ret) |
| remote_shared_1 | home **coffee_table_l1**<br>during: watch_tv→couch_l1, deep_clean→couch_l1<br>after: watch_tv→couch_l1(0.5), deep_clean→coffee_table_l1(0.5) | evening_relax→couch_l1 (usua,lef) | evening_tv→couch_l1 (usua,lef) | — *(fallback)* | — *(fallback)* | evening_tv→couch_l1 (usua,lef) |
| suitcase_mara | home **bedroom_floor_b1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: appointment→bedroom_floor_b1(0.1) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| tablet_mara | home **coffee_table_l1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→coffee_table_l1(0.7), batch_cooking→counter_k1(0.7), video_call→coffee_table_l1(0.7) | evening_relax→couch_l1 (usua,lef) | evening_tv→couch_l1 (some,lef) | — *(fallback)* | — *(fallback)* | evening_tv→couch_l1 (usua,lef) |
| towel_mara | home **towel_rack_ba1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: shower→towel_rack_ba1(0.8), groceries→bedroom_floor_b1(0.4), laundry→bedroom_floor_b1(0.4) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| umbrella_mara | home **entry_floor_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: tidy_up→entry_floor_e1(0.7), walk→entry_floor_e1(0.6), groceries→entry_floor_e1(0.6) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| vacuum_cleaner_shared_1 | home **bedroom_floor_b1**<br>during: deep_clean→couch_l1<br>after: deep_clean→bedroom_floor_b1(0.7) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| wallet_mara | home **entry_table_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→entry_table_e1(0.8), appointment→entry_table_e1(0.7) | — *(fallback)* | commute_out→OUT_OF_HOUSE (almo,lef)<br>commute_home→entry_table_e1 (almo,ret) | shift_out→OUT_OF_HOUSE (almo,lef)<br>shift_home→entry_table_e1 (almo,ret) | class_out→OUT_OF_HOUSE (almo,lef)<br>class_return→entry_table_e1 (almo,ret) | weekend_social→OUT_OF_HOUSE (usua,ret) |
| water_bottle_mara | home **counter_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→kitchen_table_k1(0.5), gym→couch_l1(0.4), bedtime_routine→nightstand_b1(0.6) | lunch→kitchen_table_k1 (usua,lef)<br>morning_routine→counter_k1 (usua,lef) | weekend_yoga→bedroom_floor_b1 (usua,ret) | morning_recovery→kitchen_table_k1 (usua,lef)<br>weekend_yoga→bedroom_floor_b1 (usua,ret) | weekend_yoga→bedroom_floor_b1 (usua,ret)<br>morning_routine→counter_k1 (usua,lef) | gym_session→OUT_OF_HOUSE (usua,ret)<br>weekend_yoga→bedroom_floor_b1 (usua,ret) |
| watering_can_mara | home **sink_k1**<br>during: pet_care→counter_k1<br>after: deep_clean→sink_k1(0.2), pet_care→sink_k1(0.7) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| yoga_mat_mara | home **couch_l1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: tidy_up→couch_l1(0.6), work_away→couch_l1(0.3), gym→couch_l1(0.3) | weekend_yoga→bedroom_floor_b1 (usua,ret) | weekend_yoga→bedroom_floor_b1 (usua,ret) | weekend_yoga→bedroom_floor_b1 (usua,ret) | weekend_yoga→bedroom_floor_b1 (usua,ret) | weekend_yoga→bedroom_floor_b1 (usua,ret) |

### Scorecard (exact joins only)

| hypothesis | objects mentioned | stated rest = true home | moves whose destination the truth ever uses | true carry-out objects it sends OUT_OF_HOUSE | objects it sends OUT that never leave | weekday-only activities |
|---|---|---|---|---|---|---|
| hyp1 | 10/35 | 0/0 | 9/13 | 0/19 | 0 | 1/5 (truth: 3) |
| hyp2 | 13/35 | 0/0 | 16/19 | 6/19 | 0 | 2/5 (truth: 3) |
| hyp3 | 10/35 | 0/0 | 13/18 | 5/19 | 0 | 4/5 (truth: 3) |
| hyp4 | 13/35 | 0/0 | 19/23 | 5/19 | 1 | 3/6 (truth: 3) |
| hyp5 | 17/35 | 0/0 | 18/23 | 5/19 | 0 | 2/6 (truth: 3) |

Truth: 19 objects leave the house during weekday work (backpack_mara, book_mara, charger_mara, headphones_mara, jacket_mara, keys_mara, laptop_mara, laundry_basket_mara, lunchbox_mara, makeup_kit_mara, notebook_mara, phone_mara, suitcase_mara, tablet_mara, towel_mara, umbrella_mara, wallet_mara, water_bottle_mara, yoga_mat_mara).

## day 3 revision

### Activity schedule — truth

| activity | days | ~start | ~length | where | objects carried / placed during | landed after |
|---|---|---|---|---|---|---|
| night_sleep | both (20wd/8we, 7.0×/wk) | 0.0h | 5.0h | bed_b1 |  |  |
| wake_up | both (20wd/8we, 7.0×/wk) | 5.0h | 0.2h | bed_b1 |  | phone_mara→nightstand_b1 |
| take_medication | both (20wd/8we, 7.0×/wk) | 5.2h | 0.1h | bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1 |
| shower | both (19wd/3we, 5.5×/wk) | 5.2h | 0.2h | bathroom_shelf_ba1 |  | towel_mara→towel_rack_ba1 |
| get_ready | weekday (19wd/0we, 4.8×/wk) | 5.5h | 0.3h | bathroom_shelf_ba1 | hairbrush_mara→bathroom_shelf_ba1 | hairbrush_mara→bathroom_shelf_ba1, makeup_kit_mara→bathroom_shelf_ba1 |
| coffee | both (19wd/8we, 6.8×/wk) | 5.8h | 0.2h | counter_k1 | mug_mara→counter_k1 | mug_mara→counter_k1 |
| breakfast | both (20wd/8we, 7.0×/wk) | 6.0h | 0.2h | kitchen_table_k1 | bowl_shared_2→kitchen_table_k1, pan_shared_1→kitchen_table_k1 | bowl_shared_2→kitchen_table_k1, pan_shared_1→counter_k1 |
| meal_prep | both (20wd/5we, 6.2×/wk) | 6.2h | 0.2h | counter_k1 | pen_mara→counter_k1, plate_shared_2→counter_k1 | backpack_mara→chair_k1, pen_mara→kitchen_table_k1, plate_shared_2→counter_k1 |
| appointment | weekday (1wd/0we, 0.2×/wk) | 7.3h | 0.7h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | makeup_kit_mara→bathroom_shelf_ba1, wallet_mara→entry_table_e1, suitcase_mara→bedroom_floor_b1 |
| pet_care | weekend (0wd/1we, 0.2×/wk) | 8.0h | 0.2h | counter_k1 | watering_can_mara→counter_k1 | watering_can_mara→sink_k1 |
| nap | weekend (0wd/1we, 0.2×/wk) | 9.0h | 1.2h | bed_b1 |  |  |
| groceries | weekend (0wd/3we, 0.8×/wk) | 9.3h | 0.9h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | towel_mara→bedroom_floor_b1, keys_mara→entry_table_e1, umbrella_mara→entry_floor_e1, jacket_mara→entry_hook_e1, book_mara→couch_l1 … |
| batch_cooking | weekend (0wd/3we, 0.8×/wk) | 9.5h | 1.5h | counter_k1 | pot_shared_1→counter_k1 | tablet_mara→counter_k1, pot_shared_1→sink_k1 |
| laundry | weekend (0wd/4we, 1.0×/wk) | 9.5h | 0.5h | bedroom_floor_b1 |  | towel_mara→bedroom_floor_b1, laundry_basket_mara→bedroom_floor_b1 |
| work_away | weekday (18wd/0we, 4.5×/wk) | 9.6h | 4.1h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | phone_mara→kitchen_table_k1, backpack_mara→entry_hook_e1, plate_shared_2→kitchen_table_k1, laptop_mara→kitchen_table_k1, keys_mara→entry_table_e1 … |
| take_out_bins | weekend (0wd/1we, 0.2×/wk) | 10.0h | 0.2h | entry_floor_e1 |  |  |
| deep_clean | weekend (0wd/2we, 0.5×/wk) | 10.8h | 1.1h | couch_l1 | remote_shared_1→couch_l1, vacuum_cleaner_shared_1→couch_l1 | remote_shared_1→coffee_table_l1, laundry_basket_mara→bedroom_floor_b1, vacuum_cleaner_shared_1→bedroom_floor_b1, watering_can_mara→sink_k1 |
| walk | both (2wd/6we, 2.0×/wk) | 11.5h | 0.6h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | keys_mara→entry_table_e1, umbrella_mara→entry_floor_e1, jacket_mara→entry_hook_e1, book_mara→couch_l1 |
| tidy_up | both (4wd/5we, 2.2×/wk) | 11.5h | 0.3h | kitchen_table_k1 | pen_mara→kitchen_table_k1, bowl_shared_1→kitchen_table_k1 | pen_mara→kitchen_table_k1, laptop_mara→kitchen_table_k1, keys_mara→entry_table_e1, umbrella_mara→entry_floor_e1, bowl_shared_1→entry_table_e1 … |
| work_home | weekday (4wd/0we, 1.0×/wk) | 11.7h | 1.7h | kitchen_table_k1 | glasses_mara→kitchen_table_k1 | laptop_mara→kitchen_table_k1, charger_mara→kitchen_table_k1, notebook_mara→kitchen_table_k1, glasses_mara→kitchen_table_k1 |
| relax | weekend (0wd/1we, 0.2×/wk) | 12.0h | 1.0h | couch_l1 | blanket_mara→couch_l1 | blanket_mara→couch_l1 |
| wash_dishes | both (6wd/8we, 3.5×/wk) | 12.1h | 0.2h | sink_k1 | mug_mara→sink_k1, plate_shared_1→sink_k1, pot_shared_1→sink_k1 | mug_mara→dish_rack_k1, lunchbox_mara→counter_k1, plate_shared_1→dish_rack_k1, pot_shared_1→dish_rack_k1 |
| lunch | both (20wd/8we, 7.0×/wk) | 12.2h | 0.4h | kitchen_table_k1 | plate_shared_2→kitchen_table_k1 | plate_shared_2→kitchen_table_k1 |
| day_sleep | weekday (1wd/0we, 0.2×/wk) | 12.4h | 1.6h | bed_b1 |  |  |
| traveling | both (19wd/3we, 5.5×/wk) | 13.1h | 0.3h | None |  |  |
| hobby | both (1wd/1we, 0.5×/wk) | 13.4h | 0.8h | couch_l1 |  |  |
| reading | both (5wd/8we, 3.2×/wk) | 14.0h | 1.1h | couch_l1 | mug_mara→couch_l1, glasses_mara→couch_l1 | mug_mara→coffee_table_l1, book_mara→couch_l1, glasses_mara→coffee_table_l1 |
| video_call | both (1wd/1we, 0.5×/wk) | 14.1h | 0.8h | couch_l1 |  | headphones_mara→coffee_table_l1, tablet_mara→coffee_table_l1 |
| put_away_dishes | both (1wd/1we, 0.5×/wk) | 14.3h | 0.2h | dish_rack_k1 | bowl_shared_2→dish_rack_k1, mug_shared_1→dish_rack_k1 | bowl_shared_2→cupboard_k1, mug_shared_1→cupboard_k1 |
| lie_down | both (3wd/1we, 1.0×/wk) | 14.6h | 1.1h | bed_b1 |  |  |
| errands | weekday (1wd/0we, 0.2×/wk) | 15.7h | 0.5h | None |  |  |
| gym | both (4wd/3we, 1.8×/wk) | 16.0h | 0.7h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | backpack_mara→entry_hook_e1, yoga_mat_mara→couch_l1, water_bottle_mara→couch_l1 |
| night_out | weekday (1wd/0we, 0.2×/wk) | 16.0h | 2.0h | None |  |  |
| snack | weekday (7wd/0we, 1.8×/wk) | 16.2h | 0.2h | counter_k1 |  | bowl_shared_1→entry_table_e1 |
| socialise_home | weekday (1wd/0we, 0.2×/wk) | 17.2h | 1.8h | couch_l1 | mug_shared_1→couch_l1 | mug_shared_1→coffee_table_l1 |
| dinner | both (18wd/8we, 6.5×/wk) | 17.3h | 0.5h | kitchen_table_k1 | pan_shared_1→kitchen_table_k1, plate_shared_1→kitchen_table_k1 | pan_shared_1→sink_k1, plate_shared_1→kitchen_table_k1 |
| watch_tv | both (6wd/1we, 1.8×/wk) | 17.4h | 1.2h | couch_l1 | remote_shared_1→couch_l1, blanket_mara→couch_l1 | remote_shared_1→couch_l1, blanket_mara→couch_l1 |
| phone_time | both (6wd/1we, 1.8×/wk) | 17.6h | 0.2h | couch_l1 |  | phone_mara→couch_l1 |
| bedtime_routine | both (14wd/7we, 5.2×/wk) | 20.5h | 0.5h | bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1, hairbrush_mara→bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1, hairbrush_mara→bathroom_shelf_ba1, water_bottle_mara→nightstand_b1 |

### Activity schedule — hyp1: Mara works from home; laptop and phone stay in the house (laptop kitchen_table 2/2, phone nightstand 2/2, keys seen once

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_routine | both (7×/wk) | 7.0h | 1.0h | mug_mara→counter_k1 (usually, left); water_bottle_mara→counter_k1 (usually, left); medication_bottle_mara→counter_k1 (usually, left) |
| work_day | weekday (5×/wk) | 8.5h | 8.5h | laptop_mara→kitchen_table_k1 (usually, left); phone_mara→kitchen_table_k1 (usually, left); headphones_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left) |
| weekend_yoga | weekend (2×/wk) | 9.0h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, returned); headphones_mara→bedroom_floor_b1 (sometimes, returned) |
| midday_cooking | both (7×/wk) | 12.0h | 1.5h | pan_shared_1→counter_k1 (usually, returned); plate_shared_2→counter_k1 (usually, returned); mug_mara→counter_k1 (sometimes, left); water_bottle_mara→counter_k1 (usually, left); bowl_shared_2→sink_k1 (sometimes, returned) |
| evening_relax | both (7×/wk) | 19.5h | 3.0h | remote_shared_1→coffee_table_l1 (usually, returned); tablet_mara→coffee_table_l1 (usually, left); blanket_mara→couch_l1 (usually, left) |

### Activity schedule — hyp2: Mara commutes to an external office. Weakened by data: laptop seen at kitchen_table 2/2 days, phone at nightstand 2/2, k

| activity | days | start | length | moves |
|---|---|---|---|---|
| commute_out | weekday (5×/wk) | 7.8h | 0.5h | keys_mara→OUT_OF_HOUSE (usually, left); wallet_mara→OUT_OF_HOUSE (usually, left); jacket_mara→OUT_OF_HOUSE (usually, left); backpack_mara→OUT_OF_HOUSE (usually, left); laptop_mara→OUT_OF_HOUSE (usually, left) … |
| weekend_yoga | weekend (2×/wk) | 9.0h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, returned); water_bottle_mara→bedroom_floor_b1 (usually, returned) |
| midday_cooking | both (7×/wk) | 12.0h | 1.5h | pan_shared_1→counter_k1 (usually, returned); plate_shared_2→counter_k1 (usually, returned); medication_bottle_mara→counter_k1 (usually, left) |
| commute_home | weekday (5×/wk) | 17.2h | 0.5h | keys_mara→entry_table_e1 (usually, returned); wallet_mara→entry_table_e1 (usually, returned); jacket_mara→entry_hook_e1 (usually, returned); backpack_mara→entry_hook_e1 (usually, returned); laptop_mara→kitchen_table_k1 (usually, returned) … |
| evening_tv | both (7×/wk) | 19.5h | 2.5h | remote_shared_1→coffee_table_l1 (usually, returned); tablet_mara→coffee_table_l1 (sometimes, left) |

### Activity schedule — hyp3: Mara works an evening shift (16:00-23:30); she is home all day using the kitchen table, then leaves in the late afternoo

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_recovery | weekday (5×/wk) | 6.5h | 1.0h | mug_mara→counter_k1 (usually, left); water_bottle_mara→counter_k1 (usually, left); medication_bottle_mara→counter_k1 (usually, left) |
| daytime_work | weekday (5×/wk) | 9.0h | 6.5h | laptop_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left); phone_mara→kitchen_table_k1 (usually, left); headphones_mara→kitchen_table_k1 (usually, left) |
| weekend_yoga | weekend (2×/wk) | 10.0h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, returned); headphones_mara→bedroom_floor_b1 (usually, returned); water_bottle_mara→bedroom_floor_b1 (usually, returned) |
| midday_cooking | both (7×/wk) | 12.0h | 1.5h | pan_shared_1→counter_k1 (usually, returned); plate_shared_2→counter_k1 (usually, returned); mug_mara→counter_k1 (sometimes, left) |
| shift_out | weekday (5×/wk) | 15.5h | 0.5h | keys_mara→OUT_OF_HOUSE (usually, left); wallet_mara→OUT_OF_HOUSE (usually, left); jacket_mara→OUT_OF_HOUSE (usually, left); phone_mara→OUT_OF_HOUSE (usually, left); backpack_mara→OUT_OF_HOUSE (sometimes, left) |
| shift_home | weekday (5×/wk) | 23.5h | 0.5h | keys_mara→entry_table_e1 (usually, returned); wallet_mara→entry_table_e1 (usually, returned); jacket_mara→entry_hook_e1 (usually, returned); phone_mara→nightstand_b1 (usually, returned); backpack_mara→entry_hook_e1 (sometimes, returned) |

### Activity schedule — hyp4: Mara is a student in daytime classes; she carries notebook, pen, laptop, backpack out each morning. Weakened: notebook s

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_routine | both (7×/wk) | 7.0h | 1.0h | mug_mara→counter_k1 (usually, left); water_bottle_mara→counter_k1 (usually, left); medication_bottle_mara→counter_k1 (usually, left) |
| class_out | weekday (5×/wk) | 8.2h | 0.5h | backpack_mara→OUT_OF_HOUSE (usually, left); laptop_mara→OUT_OF_HOUSE (usually, left); notebook_mara→OUT_OF_HOUSE (usually, left); pen_mara→OUT_OF_HOUSE (usually, left); keys_mara→OUT_OF_HOUSE (usually, left) … |
| weekend_yoga | weekend (2×/wk) | 9.5h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, returned); water_bottle_mara→bedroom_floor_b1 (usually, returned) |
| midday_cooking | both (7×/wk) | 12.0h | 1.5h | pan_shared_1→counter_k1 (usually, returned); plate_shared_2→counter_k1 (usually, returned) |
| class_return | weekday (5×/wk) | 15.0h | 0.5h | backpack_mara→entry_hook_e1 (usually, returned); laptop_mara→kitchen_table_k1 (usually, returned); notebook_mara→kitchen_table_k1 (usually, returned); pen_mara→kitchen_table_k1 (usually, returned); keys_mara→entry_table_e1 (usually, returned) … |
| study_evening | weekday (5×/wk) | 18.0h | 3.0h | laptop_mara→kitchen_table_k1 (usually, left); notebook_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left); tablet_mara→coffee_table_l1 (sometimes, left) |

### Activity schedule — hyp5: Mara works from home with a structured active routine: 3x/week evening gym and weekend social outings. Kitchen table is 

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_routine | both (7×/wk) | 7.0h | 1.0h | mug_mara→counter_k1 (usually, left); water_bottle_mara→counter_k1 (usually, left); medication_bottle_mara→counter_k1 (usually, left) |
| work_day | weekday (5×/wk) | 9.0h | 7.0h | laptop_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (usually, left); headphones_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left); phone_mara→kitchen_table_k1 (usually, left) |
| weekend_yoga | weekend (2×/wk) | 9.0h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, returned); headphones_mara→bedroom_floor_b1 (usually, returned); water_bottle_mara→bedroom_floor_b1 (usually, returned) |
| midday_cooking | both (7×/wk) | 12.0h | 1.5h | pan_shared_1→counter_k1 (usually, returned); plate_shared_2→counter_k1 (usually, returned); mug_mara→counter_k1 (sometimes, left); water_bottle_mara→counter_k1 (usually, left) |
| weekend_social | weekend (1×/wk) | 16.0h | 4.0h | keys_mara→OUT_OF_HOUSE (usually, returned); wallet_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (usually, returned); jacket_mara→OUT_OF_HOUSE (sometimes, returned) |
| gym_session | weekday (3×/wk) | 18.0h | 1.5h | water_bottle_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (usually, returned); jacket_mara→OUT_OF_HOUSE (usually, returned); keys_mara→OUT_OF_HOUSE (usually, returned) |
| evening_tv | both (7×/wk) | 20.0h | 2.5h | remote_shared_1→coffee_table_l1 (usually, returned); tablet_mara→coffee_table_l1 (usually, left); blanket_mara→couch_l1 (usually, left) |

### Per object — truth in the first column, each hypothesis beside it

| object | TRUTH | hyp1 | hyp2 | hyp3 | hyp4 | hyp5 |
|---|---|---|---|---|---|---|
| backpack_mara | home **entry_hook_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: meal_prep→chair_k1(0.5), work_away→entry_hook_e1(0.8), gym→entry_hook_e1(0.6) | — *(fallback)* | commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→entry_hook_e1 (usua,ret) | shift_out→OUT_OF_HOUSE (some,lef)<br>shift_home→entry_hook_e1 (some,ret) | class_out→OUT_OF_HOUSE (usua,lef)<br>class_return→entry_hook_e1 (usua,ret) | — *(fallback)* |
| blanket_mara | home **couch_l1**<br>during: watch_tv→couch_l1, relax→couch_l1<br>after: watch_tv→couch_l1(0.8), relax→couch_l1(0.8) | evening_relax→couch_l1 (usua,lef) | — *(fallback)* | — *(fallback)* | — *(fallback)* | evening_tv→couch_l1 (usua,lef) |
| book_mara | home **bookshelf_l1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→couch_l1(0.2), reading→couch_l1(0.6), walk→couch_l1(0.2) … | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| bowl_shared_1 | home **entry_table_e1**<br>during: tidy_up→kitchen_table_k1<br>after: tidy_up→entry_table_e1(0.9), snack→entry_table_e1(0.2) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| bowl_shared_2 | home **cupboard_k1**<br>during: breakfast→kitchen_table_k1, put_away_dishes→dish_rack_k1<br>after: breakfast→kitchen_table_k1(0.5), put_away_dishes→cupboard_k1(0.8) | midday_cooking→sink_k1 (some,ret) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| charger_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→kitchen_table_k1(0.6), work_home→kitchen_table_k1(0.9) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | work_day→kitchen_table_k1 (usua,lef) |
| glasses_mara | home **kitchen_table_k1**<br>during: reading→couch_l1, work_home→kitchen_table_k1<br>after: reading→coffee_table_l1(0.5), work_home→kitchen_table_k1(0.8) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| hairbrush_mara | home **bathroom_shelf_ba1**<br>during: get_ready→bathroom_shelf_ba1, bedtime_routine→bathroom_shelf_ba1<br>after: get_ready→bathroom_shelf_ba1(0.8), bedtime_routine→bathroom_shelf_ba1(0.6) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| headphones_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→kitchen_table_k1(0.5), video_call→coffee_table_l1(0.6) | work_day→kitchen_table_k1 (usua,lef)<br>weekend_yoga→bedroom_floor_b1 (some,ret) | — *(fallback)* | daytime_work→kitchen_table_k1 (usua,lef)<br>weekend_yoga→bedroom_floor_b1 (usua,ret) | — *(fallback)* | work_day→kitchen_table_k1 (usua,lef)<br>weekend_yoga→bedroom_floor_b1 (usua,ret) |
| jacket_mara | home **entry_hook_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→entry_hook_e1(0.7), walk→entry_hook_e1(0.6), groceries→entry_hook_e1(0.6) | — *(fallback)* | commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→entry_hook_e1 (usua,ret) | shift_out→OUT_OF_HOUSE (usua,lef)<br>shift_home→entry_hook_e1 (usua,ret) | — *(fallback)* | gym_session→OUT_OF_HOUSE (usua,ret)<br>weekend_social→OUT_OF_HOUSE (some,ret) |
| keys_mara | home **entry_table_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: tidy_up→entry_table_e1(0.9), work_away→entry_table_e1(0.8), walk→entry_table_e1(0.7) … | — *(fallback)* | commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→entry_table_e1 (usua,ret) | shift_out→OUT_OF_HOUSE (usua,lef)<br>shift_home→entry_table_e1 (usua,ret) | class_out→OUT_OF_HOUSE (usua,lef)<br>class_return→entry_table_e1 (usua,ret) | gym_session→OUT_OF_HOUSE (usua,ret)<br>weekend_social→OUT_OF_HOUSE (usua,ret) |
| laptop_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: tidy_up→kitchen_table_k1(0.8), work_away→kitchen_table_k1(0.8), work_home→kitchen_table_k1(0.9) | work_day→kitchen_table_k1 (usua,lef) | commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→kitchen_table_k1 (usua,ret) | daytime_work→kitchen_table_k1 (usua,lef) | class_out→OUT_OF_HOUSE (usua,lef)<br>class_return→kitchen_table_k1 (usua,ret)<br>study_evening→kitchen_table_k1 (usua,lef) | work_day→kitchen_table_k1 (usua,lef) |
| laundry_basket_mara | home **bedroom_floor_b1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: groceries→bedroom_floor_b1(0.8), deep_clean→bedroom_floor_b1(0.2), laundry→bedroom_floor_b1(0.8) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| lunchbox_mara | home **counter_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→sink_k1(0.6), wash_dishes→counter_k1(0.8) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| makeup_kit_mara | home **bathroom_shelf_ba1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: get_ready→bathroom_shelf_ba1(0.8), appointment→bathroom_shelf_ba1(0.6) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| medication_bottle_mara | home **bathroom_shelf_ba1**<br>during: take_medication→bathroom_shelf_ba1, bedtime_routine→bathroom_shelf_ba1<br>after: take_medication→bathroom_shelf_ba1(0.7), bedtime_routine→bathroom_shelf_ba1(0.6) | morning_routine→counter_k1 (usua,lef) | midday_cooking→counter_k1 (usua,lef) | morning_recovery→counter_k1 (usua,lef) | morning_routine→counter_k1 (usua,lef) | morning_routine→counter_k1 (usua,lef) |
| mug_mara | home **cupboard_k1**<br>during: coffee→counter_k1, wash_dishes→sink_k1, reading→couch_l1<br>after: coffee→counter_k1(0.6), wash_dishes→dish_rack_k1(0.7), reading→coffee_table_l1(0.6) | morning_routine→counter_k1 (usua,lef)<br>work_day→kitchen_table_k1 (usua,lef)<br>midday_cooking→counter_k1 (some,lef) | — *(fallback)* | morning_recovery→counter_k1 (usua,lef)<br>daytime_work→kitchen_table_k1 (usua,lef)<br>midday_cooking→counter_k1 (some,lef) | morning_routine→counter_k1 (usua,lef)<br>study_evening→kitchen_table_k1 (usua,lef) | morning_routine→counter_k1 (usua,lef)<br>work_day→kitchen_table_k1 (usua,lef)<br>midday_cooking→counter_k1 (some,lef) |
| mug_shared_1 | home **cupboard_k1**<br>during: put_away_dishes→dish_rack_k1, socialise_home→couch_l1<br>after: put_away_dishes→cupboard_k1(0.8), socialise_home→coffee_table_l1(0.5) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| notebook_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→kitchen_table_k1(0.7), work_home→kitchen_table_k1(0.9) | — *(fallback)* | — *(fallback)* | — *(fallback)* | class_out→OUT_OF_HOUSE (usua,lef)<br>class_return→kitchen_table_k1 (usua,ret)<br>study_evening→kitchen_table_k1 (usua,lef) | — *(fallback)* |
| pan_shared_1 | home **cupboard_k1**<br>during: breakfast→kitchen_table_k1, dinner→kitchen_table_k1<br>after: breakfast→counter_k1(0.4), dinner→sink_k1(0.4) | midday_cooking→counter_k1 (usua,ret) | midday_cooking→counter_k1 (usua,ret) | midday_cooking→counter_k1 (usua,ret) | midday_cooking→counter_k1 (usua,ret) | midday_cooking→counter_k1 (usua,ret) |
| pen_mara | home **kitchen_table_k1**<br>during: meal_prep→counter_k1, tidy_up→kitchen_table_k1<br>after: meal_prep→kitchen_table_k1(0.6), tidy_up→kitchen_table_k1(0.7) | — *(fallback)* | — *(fallback)* | — *(fallback)* | class_out→OUT_OF_HOUSE (usua,lef)<br>class_return→kitchen_table_k1 (usua,ret) | — *(fallback)* |
| phone_mara | home **nightstand_b1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: wake_up→nightstand_b1(0.8), work_away→kitchen_table_k1(0.5), phone_time→couch_l1(0.5) | work_day→kitchen_table_k1 (usua,lef) | commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→nightstand_b1 (usua,ret) | daytime_work→kitchen_table_k1 (usua,lef)<br>shift_out→OUT_OF_HOUSE (usua,lef)<br>shift_home→nightstand_b1 (usua,ret) | — *(fallback)* | work_day→kitchen_table_k1 (usua,lef)<br>gym_session→OUT_OF_HOUSE (usua,ret)<br>weekend_social→OUT_OF_HOUSE (usua,ret) |
| plate_shared_1 | home **cupboard_k1**<br>during: dinner→kitchen_table_k1, wash_dishes→sink_k1<br>after: dinner→kitchen_table_k1(0.5), wash_dishes→dish_rack_k1(0.8) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| plate_shared_2 | home **cupboard_k1**<br>during: meal_prep→counter_k1, lunch→kitchen_table_k1<br>after: meal_prep→counter_k1(0.6), work_away→kitchen_table_k1(0.5), lunch→kitchen_table_k1(0.5) | midday_cooking→counter_k1 (usua,ret) | midday_cooking→counter_k1 (usua,ret) | midday_cooking→counter_k1 (usua,ret) | midday_cooking→counter_k1 (usua,ret) | midday_cooking→counter_k1 (usua,ret) |
| pot_shared_1 | home **cupboard_k1**<br>during: wash_dishes→sink_k1, batch_cooking→counter_k1<br>after: wash_dishes→dish_rack_k1(0.5), batch_cooking→sink_k1(0.6) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| remote_shared_1 | home **coffee_table_l1**<br>during: watch_tv→couch_l1, deep_clean→couch_l1<br>after: watch_tv→couch_l1(0.5), deep_clean→coffee_table_l1(0.5) | evening_relax→coffee_table_l1 (usua,ret) | evening_tv→coffee_table_l1 (usua,ret) | — *(fallback)* | — *(fallback)* | evening_tv→coffee_table_l1 (usua,ret) |
| suitcase_mara | home **bedroom_floor_b1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: appointment→bedroom_floor_b1(0.1) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| tablet_mara | home **coffee_table_l1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→coffee_table_l1(0.7), batch_cooking→counter_k1(0.7), video_call→coffee_table_l1(0.7) | evening_relax→coffee_table_l1 (usua,lef) | evening_tv→coffee_table_l1 (some,lef) | — *(fallback)* | study_evening→coffee_table_l1 (some,lef) | evening_tv→coffee_table_l1 (usua,lef) |
| towel_mara | home **towel_rack_ba1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: shower→towel_rack_ba1(0.8), groceries→bedroom_floor_b1(0.4), laundry→bedroom_floor_b1(0.4) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| umbrella_mara | home **entry_floor_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: tidy_up→entry_floor_e1(0.7), walk→entry_floor_e1(0.6), groceries→entry_floor_e1(0.6) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| vacuum_cleaner_shared_1 | home **bedroom_floor_b1**<br>during: deep_clean→couch_l1<br>after: deep_clean→bedroom_floor_b1(0.7) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| wallet_mara | home **entry_table_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→entry_table_e1(0.8), appointment→entry_table_e1(0.7) | — *(fallback)* | commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→entry_table_e1 (usua,ret) | shift_out→OUT_OF_HOUSE (usua,lef)<br>shift_home→entry_table_e1 (usua,ret) | class_out→OUT_OF_HOUSE (usua,lef)<br>class_return→entry_table_e1 (usua,ret) | weekend_social→OUT_OF_HOUSE (usua,ret) |
| water_bottle_mara | home **counter_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→kitchen_table_k1(0.5), gym→couch_l1(0.4), bedtime_routine→nightstand_b1(0.6) | morning_routine→counter_k1 (usua,lef)<br>midday_cooking→counter_k1 (usua,lef) | weekend_yoga→bedroom_floor_b1 (usua,ret) | morning_recovery→counter_k1 (usua,lef)<br>weekend_yoga→bedroom_floor_b1 (usua,ret) | morning_routine→counter_k1 (usua,lef)<br>weekend_yoga→bedroom_floor_b1 (usua,ret) | morning_routine→counter_k1 (usua,lef)<br>midday_cooking→counter_k1 (usua,lef)<br>gym_session→OUT_OF_HOUSE (usua,ret)<br>weekend_yoga→bedroom_floor_b1 (usua,ret) |
| watering_can_mara | home **sink_k1**<br>during: pet_care→counter_k1<br>after: deep_clean→sink_k1(0.2), pet_care→sink_k1(0.7) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| yoga_mat_mara | home **couch_l1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: tidy_up→couch_l1(0.6), work_away→couch_l1(0.3), gym→couch_l1(0.3) | weekend_yoga→bedroom_floor_b1 (usua,ret) | weekend_yoga→bedroom_floor_b1 (usua,ret) | weekend_yoga→bedroom_floor_b1 (usua,ret) | weekend_yoga→bedroom_floor_b1 (usua,ret) | weekend_yoga→bedroom_floor_b1 (usua,ret) |

### Scorecard (exact joins only)

| hypothesis | objects mentioned | stated rest = true home | moves whose destination the truth ever uses | true carry-out objects it sends OUT_OF_HOUSE | objects it sends OUT that never leave | weekday-only activities |
|---|---|---|---|---|---|---|
| hyp1 | 13/35 | 0/0 | 12/17 | 0/19 | 0 | 1/5 (truth: 3) |
| hyp2 | 13/35 | 0/0 | 16/19 | 6/19 | 0 | 2/5 (truth: 3) |
| hyp3 | 13/35 | 0/0 | 18/23 | 5/19 | 0 | 4/6 (truth: 3) |
| hyp4 | 13/35 | 0/0 | 18/23 | 5/19 | 1 | 3/6 (truth: 3) |
| hyp5 | 16/35 | 0/0 | 21/26 | 5/19 | 0 | 2/7 (truth: 3) |

Truth: 19 objects leave the house during weekday work (backpack_mara, book_mara, charger_mara, headphones_mara, jacket_mara, keys_mara, laptop_mara, laundry_basket_mara, lunchbox_mara, makeup_kit_mara, notebook_mara, phone_mara, suitcase_mara, tablet_mara, towel_mara, umbrella_mara, wallet_mara, water_bottle_mara, yoga_mat_mara).

## day 7 revision

### Activity schedule — truth

| activity | days | ~start | ~length | where | objects carried / placed during | landed after |
|---|---|---|---|---|---|---|
| night_sleep | both (20wd/8we, 7.0×/wk) | 0.0h | 5.0h | bed_b1 |  |  |
| wake_up | both (20wd/8we, 7.0×/wk) | 5.0h | 0.2h | bed_b1 |  | phone_mara→nightstand_b1 |
| take_medication | both (20wd/8we, 7.0×/wk) | 5.2h | 0.1h | bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1 |
| shower | both (19wd/3we, 5.5×/wk) | 5.2h | 0.2h | bathroom_shelf_ba1 |  | towel_mara→towel_rack_ba1 |
| get_ready | weekday (19wd/0we, 4.8×/wk) | 5.5h | 0.3h | bathroom_shelf_ba1 | hairbrush_mara→bathroom_shelf_ba1 | hairbrush_mara→bathroom_shelf_ba1, makeup_kit_mara→bathroom_shelf_ba1 |
| coffee | both (19wd/8we, 6.8×/wk) | 5.8h | 0.2h | counter_k1 | mug_mara→counter_k1 | mug_mara→counter_k1 |
| breakfast | both (20wd/8we, 7.0×/wk) | 6.0h | 0.2h | kitchen_table_k1 | bowl_shared_2→kitchen_table_k1, pan_shared_1→kitchen_table_k1 | bowl_shared_2→kitchen_table_k1, pan_shared_1→counter_k1 |
| meal_prep | both (20wd/5we, 6.2×/wk) | 6.2h | 0.2h | counter_k1 | pen_mara→counter_k1, plate_shared_2→counter_k1 | backpack_mara→chair_k1, pen_mara→kitchen_table_k1, plate_shared_2→counter_k1 |
| appointment | weekday (1wd/0we, 0.2×/wk) | 7.3h | 0.7h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | makeup_kit_mara→bathroom_shelf_ba1, wallet_mara→entry_table_e1, suitcase_mara→bedroom_floor_b1 |
| pet_care | weekend (0wd/1we, 0.2×/wk) | 8.0h | 0.2h | counter_k1 | watering_can_mara→counter_k1 | watering_can_mara→sink_k1 |
| nap | weekend (0wd/1we, 0.2×/wk) | 9.0h | 1.2h | bed_b1 |  |  |
| groceries | weekend (0wd/3we, 0.8×/wk) | 9.3h | 0.9h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | towel_mara→bedroom_floor_b1, keys_mara→entry_table_e1, umbrella_mara→entry_floor_e1, jacket_mara→entry_hook_e1, book_mara→couch_l1 … |
| batch_cooking | weekend (0wd/3we, 0.8×/wk) | 9.5h | 1.5h | counter_k1 | pot_shared_1→counter_k1 | tablet_mara→counter_k1, pot_shared_1→sink_k1 |
| laundry | weekend (0wd/4we, 1.0×/wk) | 9.5h | 0.5h | bedroom_floor_b1 |  | towel_mara→bedroom_floor_b1, laundry_basket_mara→bedroom_floor_b1 |
| work_away | weekday (18wd/0we, 4.5×/wk) | 9.6h | 4.1h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | phone_mara→kitchen_table_k1, backpack_mara→entry_hook_e1, plate_shared_2→kitchen_table_k1, laptop_mara→kitchen_table_k1, keys_mara→entry_table_e1 … |
| take_out_bins | weekend (0wd/1we, 0.2×/wk) | 10.0h | 0.2h | entry_floor_e1 |  |  |
| deep_clean | weekend (0wd/2we, 0.5×/wk) | 10.8h | 1.1h | couch_l1 | remote_shared_1→couch_l1, vacuum_cleaner_shared_1→couch_l1 | remote_shared_1→coffee_table_l1, laundry_basket_mara→bedroom_floor_b1, vacuum_cleaner_shared_1→bedroom_floor_b1, watering_can_mara→sink_k1 |
| walk | both (2wd/6we, 2.0×/wk) | 11.5h | 0.6h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | keys_mara→entry_table_e1, umbrella_mara→entry_floor_e1, jacket_mara→entry_hook_e1, book_mara→couch_l1 |
| tidy_up | both (4wd/5we, 2.2×/wk) | 11.5h | 0.3h | kitchen_table_k1 | pen_mara→kitchen_table_k1, bowl_shared_1→kitchen_table_k1 | pen_mara→kitchen_table_k1, laptop_mara→kitchen_table_k1, keys_mara→entry_table_e1, umbrella_mara→entry_floor_e1, bowl_shared_1→entry_table_e1 … |
| work_home | weekday (4wd/0we, 1.0×/wk) | 11.7h | 1.7h | kitchen_table_k1 | glasses_mara→kitchen_table_k1 | laptop_mara→kitchen_table_k1, charger_mara→kitchen_table_k1, notebook_mara→kitchen_table_k1, glasses_mara→kitchen_table_k1 |
| relax | weekend (0wd/1we, 0.2×/wk) | 12.0h | 1.0h | couch_l1 | blanket_mara→couch_l1 | blanket_mara→couch_l1 |
| wash_dishes | both (6wd/8we, 3.5×/wk) | 12.1h | 0.2h | sink_k1 | mug_mara→sink_k1, plate_shared_1→sink_k1, pot_shared_1→sink_k1 | mug_mara→dish_rack_k1, lunchbox_mara→counter_k1, plate_shared_1→dish_rack_k1, pot_shared_1→dish_rack_k1 |
| lunch | both (20wd/8we, 7.0×/wk) | 12.2h | 0.4h | kitchen_table_k1 | plate_shared_2→kitchen_table_k1 | plate_shared_2→kitchen_table_k1 |
| day_sleep | weekday (1wd/0we, 0.2×/wk) | 12.4h | 1.6h | bed_b1 |  |  |
| traveling | both (19wd/3we, 5.5×/wk) | 13.1h | 0.3h | None |  |  |
| hobby | both (1wd/1we, 0.5×/wk) | 13.4h | 0.8h | couch_l1 |  |  |
| reading | both (5wd/8we, 3.2×/wk) | 14.0h | 1.1h | couch_l1 | mug_mara→couch_l1, glasses_mara→couch_l1 | mug_mara→coffee_table_l1, book_mara→couch_l1, glasses_mara→coffee_table_l1 |
| video_call | both (1wd/1we, 0.5×/wk) | 14.1h | 0.8h | couch_l1 |  | headphones_mara→coffee_table_l1, tablet_mara→coffee_table_l1 |
| put_away_dishes | both (1wd/1we, 0.5×/wk) | 14.3h | 0.2h | dish_rack_k1 | bowl_shared_2→dish_rack_k1, mug_shared_1→dish_rack_k1 | bowl_shared_2→cupboard_k1, mug_shared_1→cupboard_k1 |
| lie_down | both (3wd/1we, 1.0×/wk) | 14.6h | 1.1h | bed_b1 |  |  |
| errands | weekday (1wd/0we, 0.2×/wk) | 15.7h | 0.5h | None |  |  |
| gym | both (4wd/3we, 1.8×/wk) | 16.0h | 0.7h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | backpack_mara→entry_hook_e1, yoga_mat_mara→couch_l1, water_bottle_mara→couch_l1 |
| night_out | weekday (1wd/0we, 0.2×/wk) | 16.0h | 2.0h | None |  |  |
| snack | weekday (7wd/0we, 1.8×/wk) | 16.2h | 0.2h | counter_k1 |  | bowl_shared_1→entry_table_e1 |
| socialise_home | weekday (1wd/0we, 0.2×/wk) | 17.2h | 1.8h | couch_l1 | mug_shared_1→couch_l1 | mug_shared_1→coffee_table_l1 |
| dinner | both (18wd/8we, 6.5×/wk) | 17.3h | 0.5h | kitchen_table_k1 | pan_shared_1→kitchen_table_k1, plate_shared_1→kitchen_table_k1 | pan_shared_1→sink_k1, plate_shared_1→kitchen_table_k1 |
| watch_tv | both (6wd/1we, 1.8×/wk) | 17.4h | 1.2h | couch_l1 | remote_shared_1→couch_l1, blanket_mara→couch_l1 | remote_shared_1→couch_l1, blanket_mara→couch_l1 |
| phone_time | both (6wd/1we, 1.8×/wk) | 17.6h | 0.2h | couch_l1 |  | phone_mara→couch_l1 |
| bedtime_routine | both (14wd/7we, 5.2×/wk) | 20.5h | 0.5h | bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1, hairbrush_mara→bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1, hairbrush_mara→bathroom_shelf_ba1, water_bottle_mara→nightstand_b1 |

### Activity schedule — hyp1: Mara works from home. CONFIRMED: laptop 5/5 and charger 5/5 at kitchen_table_k1; phone 5/5 at nightstand_b1 (NOT kitchen

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_routine | both (7×/wk) | 7.0h | 1.0h | mug_mara→counter_k1 (usually, left); water_bottle_mara→counter_k1 (usually, left); medication_bottle_mara→counter_k1 (usually, left) |
| work_day | weekday (5×/wk) | 8.5h | 8.5h | laptop_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (usually, left); headphones_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left); notebook_mara→kitchen_table_k1 (sometimes, left) … |
| weekend_yoga | weekend (2×/wk) | 9.0h | 1.0h | headphones_mara→couch_l1 (sometimes, returned) |
| midday_cooking | both (7×/wk) | 12.0h | 1.5h | pan_shared_1→counter_k1 (usually, returned); plate_shared_2→counter_k1 (usually, returned); mug_mara→counter_k1 (sometimes, left); water_bottle_mara→counter_k1 (usually, left); bowl_shared_2→sink_k1 (sometimes, returned) |
| evening_relax | both (7×/wk) | 19.5h | 3.0h | remote_shared_1→coffee_table_l1 (usually, returned); tablet_mara→coffee_table_l1 (usually, left); blanket_mara→couch_l1 (usually, left) |

### Activity schedule — hyp2: Mara commutes to an external office. VERY WEAK (weight 0.02): laptop 5/5 at kitchen_table, phone 5/5 at nightstand, keys

| activity | days | start | length | moves |
|---|---|---|---|---|
| commute_out | weekday (5×/wk) | 7.8h | 0.5h | keys_mara→OUT_OF_HOUSE (usually, left); wallet_mara→OUT_OF_HOUSE (usually, left); jacket_mara→OUT_OF_HOUSE (usually, left); backpack_mara→OUT_OF_HOUSE (usually, left); laptop_mara→OUT_OF_HOUSE (usually, left) … |
| weekend_yoga | weekend (2×/wk) | 9.0h | 1.0h | headphones_mara→couch_l1 (sometimes, returned) |
| midday_cooking | both (7×/wk) | 12.0h | 1.5h | pan_shared_1→counter_k1 (usually, returned); plate_shared_2→counter_k1 (usually, returned); medication_bottle_mara→counter_k1 (usually, left) |
| commute_home | weekday (5×/wk) | 17.2h | 0.5h | keys_mara→entry_table_e1 (usually, returned); wallet_mara→entry_table_e1 (usually, returned); jacket_mara→entry_hook_e1 (usually, returned); backpack_mara→entry_hook_e1 (usually, returned); laptop_mara→kitchen_table_k1 (usually, returned) … |
| evening_tv | both (7×/wk) | 19.5h | 2.5h | remote_shared_1→coffee_table_l1 (usually, returned); tablet_mara→coffee_table_l1 (sometimes, left) |

### Activity schedule — hyp3: Mara works an evening shift (16:00–23:30). WEAK (weight 0.01): keys 4/4 at entry_table and jacket 4/4 at entry_hook stro

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_recovery | weekday (5×/wk) | 6.5h | 1.0h | mug_mara→counter_k1 (usually, left); water_bottle_mara→counter_k1 (usually, left); medication_bottle_mara→counter_k1 (usually, left) |
| daytime_work | weekday (5×/wk) | 9.0h | 6.5h | laptop_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left); headphones_mara→kitchen_table_k1 (usually, left) |
| weekend_yoga | weekend (2×/wk) | 10.0h | 1.0h | headphones_mara→couch_l1 (sometimes, returned); water_bottle_mara→couch_l1 (sometimes, returned) |
| midday_cooking | both (7×/wk) | 12.0h | 1.5h | pan_shared_1→counter_k1 (usually, returned); plate_shared_2→counter_k1 (usually, returned); mug_mara→counter_k1 (sometimes, left) |
| shift_out | weekday (5×/wk) | 15.5h | 0.5h | keys_mara→OUT_OF_HOUSE (usually, left); wallet_mara→OUT_OF_HOUSE (usually, left); jacket_mara→OUT_OF_HOUSE (usually, left); phone_mara→OUT_OF_HOUSE (usually, left); backpack_mara→OUT_OF_HOUSE (sometimes, left) |
| shift_home | weekday (5×/wk) | 23.5h | 0.5h | keys_mara→entry_table_e1 (usually, returned); wallet_mara→entry_table_e1 (usually, returned); jacket_mara→entry_hook_e1 (usually, returned); phone_mara→nightstand_b1 (usually, returned); backpack_mara→entry_hook_e1 (sometimes, returned) |

### Activity schedule — hyp4: Mara is a student in daytime classes. DEAD (weight 0.00): notebook 3/5 and pen 3/7 at kitchen_table (home locations), la

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_routine | both (7×/wk) | 7.0h | 1.0h | mug_mara→counter_k1 (usually, left); water_bottle_mara→counter_k1 (usually, left); medication_bottle_mara→counter_k1 (usually, left) |
| class_out | weekday (5×/wk) | 8.2h | 0.5h | backpack_mara→OUT_OF_HOUSE (usually, left); laptop_mara→OUT_OF_HOUSE (usually, left); notebook_mara→OUT_OF_HOUSE (usually, left); pen_mara→OUT_OF_HOUSE (usually, left); keys_mara→OUT_OF_HOUSE (usually, left) … |
| weekend_yoga | weekend (2×/wk) | 9.5h | 1.0h | headphones_mara→couch_l1 (sometimes, returned) |
| midday_cooking | both (7×/wk) | 12.0h | 1.5h | pan_shared_1→counter_k1 (usually, returned); plate_shared_2→counter_k1 (usually, returned) |
| class_return | weekday (5×/wk) | 15.0h | 0.5h | backpack_mara→entry_hook_e1 (usually, returned); laptop_mara→kitchen_table_k1 (usually, returned); notebook_mara→kitchen_table_k1 (usually, returned); pen_mara→kitchen_table_k1 (usually, returned); keys_mara→entry_table_e1 (usually, returned) … |
| study_evening | weekday (5×/wk) | 18.0h | 3.0h | laptop_mara→kitchen_table_k1 (usually, left); notebook_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left); tablet_mara→coffee_table_l1 (sometimes, left) |

### Activity schedule — hyp5: Mara works from home with an active routine. GYM PREDICTION FAILED (0/1): water_bottle was NOT out of the house at 18:30

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_routine | both (7×/wk) | 7.0h | 1.0h | mug_mara→counter_k1 (usually, left); water_bottle_mara→counter_k1 (usually, left); medication_bottle_mara→counter_k1 (usually, left) |
| work_day | weekday (5×/wk) | 9.0h | 7.0h | laptop_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (usually, left); headphones_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left) |
| weekend_yoga | weekend (2×/wk) | 9.0h | 1.0h | headphones_mara→couch_l1 (sometimes, returned); water_bottle_mara→couch_l1 (sometimes, returned) |
| midday_cooking | both (7×/wk) | 12.0h | 1.5h | pan_shared_1→counter_k1 (usually, returned); plate_shared_2→counter_k1 (usually, returned); mug_mara→counter_k1 (sometimes, left); water_bottle_mara→counter_k1 (usually, left) |
| weekend_social | weekend (1×/wk) | 16.0h | 4.0h | keys_mara→OUT_OF_HOUSE (usually, returned); wallet_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (usually, returned); jacket_mara→OUT_OF_HOUSE (sometimes, returned) |
| gym_session | weekday (2×/wk) | 18.0h | 1.5h | water_bottle_mara→OUT_OF_HOUSE (sometimes, returned); phone_mara→OUT_OF_HOUSE (sometimes, returned); keys_mara→OUT_OF_HOUSE (sometimes, returned) |
| evening_tv | both (7×/wk) | 20.0h | 2.5h | remote_shared_1→coffee_table_l1 (usually, returned); tablet_mara→coffee_table_l1 (usually, left); blanket_mara→couch_l1 (usually, left) |

### Per object — truth in the first column, each hypothesis beside it

| object | TRUTH | hyp1 | hyp2 | hyp3 | hyp4 | hyp5 |
|---|---|---|---|---|---|---|
| backpack_mara | home **entry_hook_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: meal_prep→chair_k1(0.5), work_away→entry_hook_e1(0.8), gym→entry_hook_e1(0.6) | rest entry_hook_e1 | rest entry_hook_e1<br>commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→entry_hook_e1 (usua,ret) | rest entry_hook_e1<br>shift_out→OUT_OF_HOUSE (some,lef)<br>shift_home→entry_hook_e1 (some,ret) | rest entry_hook_e1<br>class_out→OUT_OF_HOUSE (usua,lef)<br>class_return→entry_hook_e1 (usua,ret) | rest entry_hook_e1 |
| blanket_mara | home **couch_l1**<br>during: watch_tv→couch_l1, relax→couch_l1<br>after: watch_tv→couch_l1(0.8), relax→couch_l1(0.8) | rest couch_l1<br>evening_relax→couch_l1 (usua,lef) | rest couch_l1 | rest couch_l1 | rest couch_l1 | rest couch_l1<br>evening_tv→couch_l1 (usua,lef) |
| book_mara | home **bookshelf_l1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→couch_l1(0.2), reading→couch_l1(0.6), walk→couch_l1(0.2) … | rest bookshelf_l1 | rest bookshelf_l1 | rest bookshelf_l1 | rest bookshelf_l1 | rest bookshelf_l1 |
| bowl_shared_1 | home **entry_table_e1**<br>during: tidy_up→kitchen_table_k1<br>after: tidy_up→entry_table_e1(0.9), snack→entry_table_e1(0.2) | rest entry_table_e1 | rest entry_table_e1 | rest entry_table_e1 | rest entry_table_e1 | rest entry_table_e1 |
| bowl_shared_2 | home **cupboard_k1**<br>during: breakfast→kitchen_table_k1, put_away_dishes→dish_rack_k1<br>after: breakfast→kitchen_table_k1(0.5), put_away_dishes→cupboard_k1(0.8) | rest sink_k1<br>midday_cooking→sink_k1 (some,ret) | rest sink_k1 | rest sink_k1 | rest sink_k1 | rest sink_k1 |
| charger_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→kitchen_table_k1(0.6), work_home→kitchen_table_k1(0.9) | rest kitchen_table_k1<br>work_day→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 | rest kitchen_table_k1<br>daytime_work→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 | rest kitchen_table_k1<br>work_day→kitchen_table_k1 (usua,lef) |
| glasses_mara | home **kitchen_table_k1**<br>during: reading→couch_l1, work_home→kitchen_table_k1<br>after: reading→coffee_table_l1(0.5), work_home→kitchen_table_k1(0.8) | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1 |
| hairbrush_mara | home **bathroom_shelf_ba1**<br>during: get_ready→bathroom_shelf_ba1, bedtime_routine→bathroom_shelf_ba1<br>after: get_ready→bathroom_shelf_ba1(0.8), bedtime_routine→bathroom_shelf_ba1(0.6) | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 |
| headphones_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→kitchen_table_k1(0.5), video_call→coffee_table_l1(0.6) | rest kitchen_table_k1<br>work_day→kitchen_table_k1 (usua,lef)<br>weekend_yoga→couch_l1 (some,ret) | rest kitchen_table_k1<br>weekend_yoga→couch_l1 (some,ret) | rest kitchen_table_k1<br>daytime_work→kitchen_table_k1 (usua,lef)<br>weekend_yoga→couch_l1 (some,ret) | rest kitchen_table_k1<br>weekend_yoga→couch_l1 (some,ret) | rest kitchen_table_k1<br>work_day→kitchen_table_k1 (usua,lef)<br>weekend_yoga→couch_l1 (some,ret) |
| jacket_mara | home **entry_hook_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→entry_hook_e1(0.7), walk→entry_hook_e1(0.6), groceries→entry_hook_e1(0.6) | rest entry_hook_e1 | rest entry_hook_e1<br>commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→entry_hook_e1 (usua,ret) | rest entry_hook_e1<br>shift_out→OUT_OF_HOUSE (usua,lef)<br>shift_home→entry_hook_e1 (usua,ret) | rest entry_hook_e1 | rest entry_hook_e1<br>weekend_social→OUT_OF_HOUSE (some,ret) |
| keys_mara | home **entry_table_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: tidy_up→entry_table_e1(0.9), work_away→entry_table_e1(0.8), walk→entry_table_e1(0.7) … | rest entry_table_e1 | rest entry_table_e1<br>commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→entry_table_e1 (usua,ret) | rest entry_table_e1<br>shift_out→OUT_OF_HOUSE (usua,lef)<br>shift_home→entry_table_e1 (usua,ret) | rest entry_table_e1<br>class_out→OUT_OF_HOUSE (usua,lef)<br>class_return→entry_table_e1 (usua,ret) | rest entry_table_e1<br>gym_session→OUT_OF_HOUSE (some,ret)<br>weekend_social→OUT_OF_HOUSE (usua,ret) |
| laptop_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: tidy_up→kitchen_table_k1(0.8), work_away→kitchen_table_k1(0.8), work_home→kitchen_table_k1(0.9) | rest kitchen_table_k1<br>work_day→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→kitchen_table_k1 (usua,ret) | rest kitchen_table_k1<br>daytime_work→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>class_out→OUT_OF_HOUSE (usua,lef)<br>class_return→kitchen_table_k1 (usua,ret)<br>study_evening→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>work_day→kitchen_table_k1 (usua,lef) |
| laundry_basket_mara | home **bedroom_floor_b1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: groceries→bedroom_floor_b1(0.8), deep_clean→bedroom_floor_b1(0.2), laundry→bedroom_floor_b1(0.8) | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 |
| lunchbox_mara | home **counter_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→sink_k1(0.6), wash_dishes→counter_k1(0.8) | rest counter_k1 | rest counter_k1 | rest counter_k1 | rest counter_k1 | rest counter_k1 |
| makeup_kit_mara | home **bathroom_shelf_ba1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: get_ready→bathroom_shelf_ba1(0.8), appointment→bathroom_shelf_ba1(0.6) | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 |
| medication_bottle_mara | home **bathroom_shelf_ba1**<br>during: take_medication→bathroom_shelf_ba1, bedtime_routine→bathroom_shelf_ba1<br>after: take_medication→bathroom_shelf_ba1(0.7), bedtime_routine→bathroom_shelf_ba1(0.6) | rest bathroom_shelf_ba1<br>morning_routine→counter_k1 (usua,lef) | rest bathroom_shelf_ba1<br>midday_cooking→counter_k1 (usua,lef) | rest bathroom_shelf_ba1<br>morning_recovery→counter_k1 (usua,lef) | rest bathroom_shelf_ba1<br>morning_routine→counter_k1 (usua,lef) | rest bathroom_shelf_ba1<br>morning_routine→counter_k1 (usua,lef) |
| mug_mara | home **cupboard_k1**<br>during: coffee→counter_k1, wash_dishes→sink_k1, reading→couch_l1<br>after: coffee→counter_k1(0.6), wash_dishes→dish_rack_k1(0.7), reading→coffee_table_l1(0.6) | rest counter_k1<br>morning_routine→counter_k1 (usua,lef)<br>work_day→kitchen_table_k1 (usua,lef)<br>midday_cooking→counter_k1 (some,lef) | rest counter_k1 | rest counter_k1<br>morning_recovery→counter_k1 (usua,lef)<br>daytime_work→kitchen_table_k1 (usua,lef)<br>midday_cooking→counter_k1 (some,lef) | rest counter_k1<br>morning_routine→counter_k1 (usua,lef)<br>study_evening→kitchen_table_k1 (usua,lef) | rest counter_k1<br>morning_routine→counter_k1 (usua,lef)<br>work_day→kitchen_table_k1 (usua,lef)<br>midday_cooking→counter_k1 (some,lef) |
| mug_shared_1 | home **cupboard_k1**<br>during: put_away_dishes→dish_rack_k1, socialise_home→couch_l1<br>after: put_away_dishes→cupboard_k1(0.8), socialise_home→coffee_table_l1(0.5) | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 |
| notebook_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→kitchen_table_k1(0.7), work_home→kitchen_table_k1(0.9) | rest kitchen_table_k1<br>work_day→kitchen_table_k1 (some,lef) | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1<br>class_out→OUT_OF_HOUSE (usua,lef)<br>class_return→kitchen_table_k1 (usua,ret)<br>study_evening→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 |
| pan_shared_1 | home **cupboard_k1**<br>during: breakfast→kitchen_table_k1, dinner→kitchen_table_k1<br>after: breakfast→counter_k1(0.4), dinner→sink_k1(0.4) | rest counter_k1<br>midday_cooking→counter_k1 (usua,ret) | rest counter_k1<br>midday_cooking→counter_k1 (usua,ret) | rest counter_k1<br>midday_cooking→counter_k1 (usua,ret) | rest counter_k1<br>midday_cooking→counter_k1 (usua,ret) | rest counter_k1<br>midday_cooking→counter_k1 (usua,ret) |
| pen_mara | home **kitchen_table_k1**<br>during: meal_prep→counter_k1, tidy_up→kitchen_table_k1<br>after: meal_prep→kitchen_table_k1(0.6), tidy_up→kitchen_table_k1(0.7) | rest kitchen_table_k1<br>work_day→kitchen_table_k1 (some,lef) | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1<br>class_out→OUT_OF_HOUSE (usua,lef)<br>class_return→kitchen_table_k1 (usua,ret) | rest kitchen_table_k1 |
| phone_mara | home **nightstand_b1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: wake_up→nightstand_b1(0.8), work_away→kitchen_table_k1(0.5), phone_time→couch_l1(0.5) | rest nightstand_b1 | rest nightstand_b1<br>commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→nightstand_b1 (usua,ret) | rest nightstand_b1<br>shift_out→OUT_OF_HOUSE (usua,lef)<br>shift_home→nightstand_b1 (usua,ret) | rest nightstand_b1 | rest nightstand_b1<br>gym_session→OUT_OF_HOUSE (some,ret)<br>weekend_social→OUT_OF_HOUSE (usua,ret) |
| plate_shared_1 | home **cupboard_k1**<br>during: dinner→kitchen_table_k1, wash_dishes→sink_k1<br>after: dinner→kitchen_table_k1(0.5), wash_dishes→dish_rack_k1(0.8) | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1 |
| plate_shared_2 | home **cupboard_k1**<br>during: meal_prep→counter_k1, lunch→kitchen_table_k1<br>after: meal_prep→counter_k1(0.6), work_away→kitchen_table_k1(0.5), lunch→kitchen_table_k1(0.5) | rest counter_k1<br>midday_cooking→counter_k1 (usua,ret) | rest counter_k1<br>midday_cooking→counter_k1 (usua,ret) | rest counter_k1<br>midday_cooking→counter_k1 (usua,ret) | rest counter_k1<br>midday_cooking→counter_k1 (usua,ret) | rest counter_k1<br>midday_cooking→counter_k1 (usua,ret) |
| pot_shared_1 | home **cupboard_k1**<br>during: wash_dishes→sink_k1, batch_cooking→counter_k1<br>after: wash_dishes→dish_rack_k1(0.5), batch_cooking→sink_k1(0.6) | rest dish_rack_k1 | rest dish_rack_k1 | rest dish_rack_k1 | rest dish_rack_k1 | rest dish_rack_k1 |
| remote_shared_1 | home **coffee_table_l1**<br>during: watch_tv→couch_l1, deep_clean→couch_l1<br>after: watch_tv→couch_l1(0.5), deep_clean→coffee_table_l1(0.5) | rest cupboard_k1<br>evening_relax→coffee_table_l1 (usua,ret) | rest cupboard_k1<br>evening_tv→coffee_table_l1 (usua,ret) | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1<br>evening_tv→coffee_table_l1 (usua,ret) |
| suitcase_mara | home **bedroom_floor_b1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: appointment→bedroom_floor_b1(0.1) | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 |
| tablet_mara | home **coffee_table_l1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→coffee_table_l1(0.7), batch_cooking→counter_k1(0.7), video_call→coffee_table_l1(0.7) | rest coffee_table_l1<br>evening_relax→coffee_table_l1 (usua,lef) | rest coffee_table_l1<br>evening_tv→coffee_table_l1 (some,lef) | rest coffee_table_l1 | rest coffee_table_l1<br>study_evening→coffee_table_l1 (some,lef) | rest coffee_table_l1<br>evening_tv→coffee_table_l1 (usua,lef) |
| towel_mara | home **towel_rack_ba1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: shower→towel_rack_ba1(0.8), groceries→bedroom_floor_b1(0.4), laundry→bedroom_floor_b1(0.4) | rest towel_rack_ba1 | rest towel_rack_ba1 | rest towel_rack_ba1 | rest towel_rack_ba1 | rest towel_rack_ba1 |
| umbrella_mara | home **entry_floor_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: tidy_up→entry_floor_e1(0.7), walk→entry_floor_e1(0.6), groceries→entry_floor_e1(0.6) | rest entry_floor_e1 | rest entry_floor_e1 | rest entry_floor_e1 | rest entry_floor_e1 | rest entry_floor_e1 |
| vacuum_cleaner_shared_1 | home **bedroom_floor_b1**<br>during: deep_clean→couch_l1<br>after: deep_clean→bedroom_floor_b1(0.7) | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 |
| wallet_mara | home **entry_table_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→entry_table_e1(0.8), appointment→entry_table_e1(0.7) | rest entry_table_e1 | rest entry_table_e1<br>commute_out→OUT_OF_HOUSE (usua,lef)<br>commute_home→entry_table_e1 (usua,ret) | rest entry_table_e1<br>shift_out→OUT_OF_HOUSE (usua,lef)<br>shift_home→entry_table_e1 (usua,ret) | rest entry_table_e1<br>class_out→OUT_OF_HOUSE (usua,lef)<br>class_return→entry_table_e1 (usua,ret) | rest entry_table_e1<br>weekend_social→OUT_OF_HOUSE (usua,ret) |
| water_bottle_mara | home **counter_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: work_away→kitchen_table_k1(0.5), gym→couch_l1(0.4), bedtime_routine→nightstand_b1(0.6) | rest counter_k1<br>morning_routine→counter_k1 (usua,lef)<br>midday_cooking→counter_k1 (usua,lef) | rest counter_k1 | rest counter_k1<br>morning_recovery→counter_k1 (usua,lef)<br>weekend_yoga→couch_l1 (some,ret) | rest counter_k1<br>morning_routine→counter_k1 (usua,lef) | rest counter_k1<br>morning_routine→counter_k1 (usua,lef)<br>midday_cooking→counter_k1 (usua,lef)<br>gym_session→OUT_OF_HOUSE (some,ret)<br>weekend_yoga→couch_l1 (some,ret) |
| watering_can_mara | home **sink_k1**<br>during: pet_care→counter_k1<br>after: deep_clean→sink_k1(0.2), pet_care→sink_k1(0.7) | rest sink_k1 | rest sink_k1 | rest sink_k1 | rest sink_k1 | rest sink_k1 |
| yoga_mat_mara | home **couch_l1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE …<br>after: tidy_up→couch_l1(0.6), work_away→couch_l1(0.3), gym→couch_l1(0.3) | rest couch_l1 | rest couch_l1 | rest couch_l1 | rest couch_l1 | rest couch_l1 |

### Scorecard (exact joins only)

| hypothesis | objects mentioned | stated rest = true home | moves whose destination the truth ever uses | true carry-out objects it sends OUT_OF_HOUSE | objects it sends OUT that never leave | weekday-only activities |
|---|---|---|---|---|---|---|
| hyp1 | 35/35 | 28/35 | 14/18 | 0/19 | 0 | 1/5 (truth: 3) |
| hyp2 | 35/35 | 28/35 | 16/18 | 6/19 | 0 | 2/5 (truth: 3) |
| hyp3 | 35/35 | 28/35 | 19/22 | 5/19 | 0 | 4/6 (truth: 3) |
| hyp4 | 35/35 | 28/35 | 18/22 | 5/19 | 1 | 3/6 (truth: 3) |
| hyp5 | 35/35 | 28/35 | 20/23 | 5/19 | 0 | 2/7 (truth: 3) |

Truth: 19 objects leave the house during weekday work (backpack_mara, book_mara, charger_mara, headphones_mara, jacket_mara, keys_mara, laptop_mara, laundry_basket_mara, lunchbox_mara, makeup_kit_mara, notebook_mara, phone_mara, suitcase_mara, tablet_mara, towel_mara, umbrella_mara, wallet_mara, water_bottle_mara, yoga_mat_mara).

## Prediction provenance (share of object-days)

| set | panel | activity rule | stated rest | tour only | statistical fallback | never sighted |
|---|---|---|---|---|---|---|
| fixed | hyp1 | 2% | 0% | 5% | 93% | 0% |
| fixed | hyp2 | 2% | 0% | 4% | 94% | 0% |
| fixed | hyp3 | 4% | 0% | 5% | 91% | 0% |
| fixed | hyp4 | 3% | 0% | 4% | 93% | 0% |
| fixed | hyp5 | 0% | 0% | 5% | 94% | 0% |
| fixed | mixture leader | 2% | 0% | 5% | 93% | 0% |
| re-asking | hyp1 | 1% | 52% | 5% | 42% | 0% |
| re-asking | hyp2 | 2% | 50% | 4% | 44% | 0% |
| re-asking | hyp3 | 1% | 52% | 5% | 42% | 0% |
| re-asking | hyp4 | 2% | 50% | 4% | 44% | 0% |
| re-asking | hyp5 | 0% | 51% | 5% | 43% | 0% |
| re-asking | mixture leader | 1% | 51% | 5% | 44% | 0% |

Figures: provenance__tour_named__fixed.png, provenance__tour_named__reask.png
