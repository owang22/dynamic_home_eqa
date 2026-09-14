# Ground truth vs hypotheses — hh_001 (working_professional_solo) · tour_named · tl0_bank0

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
| appointment | weekday (1wd/0we, 0.2×/wk) | 7.3h | 0.7h | ELSEWHERE | phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, makeup_kit_mara→OUT_OF_HOUSE, suitcase_mara→OUT_OF_HOUSE | makeup_kit_mara→bathroom_shelf_ba1, wallet_mara→entry_table_e1, suitcase_mara→bedroom_floor_b1 |
| pet_care | weekend (0wd/1we, 0.2×/wk) | 8.0h | 0.2h | counter_k1 | watering_can_mara→counter_k1 | watering_can_mara→sink_k1 |
| nap | weekend (0wd/1we, 0.2×/wk) | 9.0h | 1.2h | bed_b1 |  |  |
| groceries | weekend (0wd/3we, 0.8×/wk) | 9.3h | 0.9h | None |  |  |
| batch_cooking | weekend (0wd/3we, 0.8×/wk) | 9.5h | 1.5h | counter_k1 | pot_shared_1→counter_k1 | pot_shared_1→sink_k1, tablet_mara→counter_k1 |
| laundry | weekend (0wd/4we, 1.0×/wk) | 9.5h | 0.5h | bedroom_floor_b1 |  | towel_mara→bedroom_floor_b1, laundry_basket_mara→bedroom_floor_b1 |
| work_away | weekday (18wd/0we, 4.5×/wk) | 9.6h | 4.1h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | phone_mara→kitchen_table_k1, backpack_mara→entry_hook_e1, plate_shared_2→kitchen_table_k1, laptop_mara→kitchen_table_k1, keys_mara→entry_table_e1 … |
| take_out_bins | weekend (0wd/1we, 0.2×/wk) | 10.0h | 0.2h | entry_floor_e1 |  |  |
| deep_clean | weekend (0wd/2we, 0.5×/wk) | 10.8h | 1.1h | couch_l1 | remote_shared_1→couch_l1, vacuum_cleaner_shared_1→couch_l1 | remote_shared_1→coffee_table_l1, laundry_basket_mara→bedroom_floor_b1, vacuum_cleaner_shared_1→bedroom_floor_b1, watering_can_mara→sink_k1 |
| walk | both (2wd/6we, 2.0×/wk) | 11.5h | 0.6h | ELSEWHERE | phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE, book_mara→OUT_OF_HOUSE | jacket_mara→entry_hook_e1, book_mara→couch_l1 |
| tidy_up | both (4wd/5we, 2.2×/wk) | 11.5h | 0.3h | kitchen_table_k1 | pen_mara→kitchen_table_k1, bowl_shared_1→kitchen_table_k1 | pen_mara→kitchen_table_k1, laptop_mara→kitchen_table_k1, keys_mara→entry_table_e1, umbrella_mara→entry_floor_e1, bowl_shared_1→entry_table_e1 … |
| work_home | weekday (4wd/0we, 1.0×/wk) | 11.7h | 1.7h | kitchen_table_k1 | glasses_mara→kitchen_table_k1 | laptop_mara→kitchen_table_k1, charger_mara→kitchen_table_k1, notebook_mara→kitchen_table_k1, glasses_mara→kitchen_table_k1 |
| relax | weekend (0wd/1we, 0.2×/wk) | 12.0h | 1.0h | couch_l1 | blanket_mara→couch_l1 | blanket_mara→couch_l1 |
| wash_dishes | both (6wd/8we, 3.5×/wk) | 12.1h | 0.2h | sink_k1 | mug_mara→sink_k1, plate_shared_1→sink_k1, pot_shared_1→sink_k1 | mug_mara→dish_rack_k1, lunchbox_mara→counter_k1, plate_shared_1→dish_rack_k1, pot_shared_1→dish_rack_k1 |
| lunch | both (20wd/8we, 7.0×/wk) | 12.2h | 0.4h | kitchen_table_k1 | plate_shared_2→kitchen_table_k1 | plate_shared_2→kitchen_table_k1 |
| day_sleep | weekday (1wd/0we, 0.2×/wk) | 12.4h | 1.6h | bed_b1 |  |  |
| traveling | both (19wd/3we, 5.5×/wk) | 13.1h | 0.3h | None |  |  |
| hobby | both (1wd/1we, 0.5×/wk) | 13.4h | 0.8h | couch_l1 |  |  |
| reading | both (5wd/8we, 3.2×/wk) | 14.0h | 1.1h | couch_l1 | mug_mara→couch_l1, glasses_mara→couch_l1 | mug_mara→coffee_table_l1, glasses_mara→coffee_table_l1, book_mara→couch_l1 |
| video_call | both (1wd/1we, 0.5×/wk) | 14.1h | 0.8h | couch_l1 |  | headphones_mara→coffee_table_l1, tablet_mara→coffee_table_l1 |
| put_away_dishes | both (1wd/1we, 0.5×/wk) | 14.3h | 0.2h | dish_rack_k1 | bowl_shared_2→dish_rack_k1, mug_shared_1→dish_rack_k1 | bowl_shared_2→cupboard_k1, mug_shared_1→cupboard_k1 |
| lie_down | both (3wd/1we, 1.0×/wk) | 14.6h | 1.1h | bed_b1 |  |  |
| errands | weekday (1wd/0we, 0.2×/wk) | 15.7h | 0.5h | None |  |  |
| gym | both (4wd/3we, 1.8×/wk) | 16.0h | 0.7h | ELSEWHERE | phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, water_bottle_mara→OUT_OF_HOUSE, yoga_mat_mara→OUT_OF_HOUSE | backpack_mara→entry_hook_e1, yoga_mat_mara→couch_l1, water_bottle_mara→couch_l1 |
| night_out | weekday (1wd/0we, 0.2×/wk) | 16.0h | 2.0h | None |  |  |
| snack | weekday (7wd/0we, 1.8×/wk) | 16.2h | 0.2h | counter_k1 |  | bowl_shared_1→entry_table_e1 |
| socialise_home | weekday (1wd/0we, 0.2×/wk) | 17.2h | 1.8h | couch_l1 | mug_shared_1→couch_l1 | mug_shared_1→coffee_table_l1 |
| dinner | both (18wd/8we, 6.5×/wk) | 17.3h | 0.5h | kitchen_table_k1 | pan_shared_1→kitchen_table_k1, plate_shared_1→kitchen_table_k1 | pan_shared_1→sink_k1, plate_shared_1→kitchen_table_k1 |
| watch_tv | both (6wd/1we, 1.8×/wk) | 17.4h | 1.2h | couch_l1 | remote_shared_1→couch_l1, blanket_mara→couch_l1 | remote_shared_1→couch_l1, blanket_mara→couch_l1 |
| phone_time | both (6wd/1we, 1.8×/wk) | 17.6h | 0.2h | couch_l1 |  | phone_mara→couch_l1 |
| bedtime_routine | both (14wd/7we, 5.2×/wk) | 20.5h | 0.5h | bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1, hairbrush_mara→bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1, hairbrush_mara→bathroom_shelf_ba1, water_bottle_mara→nightstand_b1 |

### Activity schedule — hyp1: Mara is a full-time office worker away 8:30-17:30 Mon-Fri; all carry items including keys leave with her, so keys should

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_prep | weekday (5×/wk) | 7.0h | 1.5h | mug_mara→counter_k1 (usually, left); water_bottle_mara→counter_k1 (usually, left); lunchbox_mara→counter_k1 (usually, left) |
| work_commute_out | weekday (5×/wk) | 8.5h | 9.0h | keys_mara→OUT_OF_HOUSE (almost_always, returned); phone_mara→OUT_OF_HOUSE (almost_always, returned); wallet_mara→OUT_OF_HOUSE (almost_always, returned); jacket_mara→OUT_OF_HOUSE (usually, returned); backpack_mara→OUT_OF_HOUSE (almost_always, returned) … |
| weekend_yoga | weekend (2×/wk) | 9.0h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, left); water_bottle_mara→bedroom_floor_b1 (usually, returned) |
| weekend_cleaning | weekend (1×/wk) | 10.0h | 2.0h | vacuum_cleaner_shared_1→bedroom_floor_b1 (usually, returned); blanket_mara→bed_b1 (sometimes, returned) |
| evening_dinner | weekday (5×/wk) | 18.5h | 1.5h | class:plate→kitchen_table_k1 (usually, left); class:bowl→kitchen_table_k1 (usually, left); pan_shared_1→counter_k1 (usually, returned) |

### Activity schedule — hyp2: Mara works from home 9:00-16:30 using her tablet; laptop stays in a bag on the desk; at 15:08 she is home but in transit

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_coffee | both (7×/wk) | 7.0h | 0.5h | mug_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (sometimes, left) |
| wfh_work_block | weekday (5×/wk) | 9.0h | 7.5h | tablet_mara→coffee_table_l1 (almost_always, left); mug_mara→coffee_table_l1 (usually, left); water_bottle_mara→coffee_table_l1 (usually, left) |
| weekend_outing | weekend (2×/wk) | 11.0h | 4.0h | keys_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (almost_always, returned); jacket_mara→OUT_OF_HOUSE (usually, returned); backpack_mara→OUT_OF_HOUSE (usually, returned) |
| afternoon_errand | weekday (3×/wk) | 14.0h | 1.5h | jacket_mara→ON_PERSON (usually, returned); backpack_mara→ON_PERSON (usually, returned); phone_mara→ON_PERSON (almost_always, left); wallet_mara→ON_PERSON (almost_always, left) |
| evening_yoga | weekday (3×/wk) | 18.0h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, left); headphones_mara→bedroom_floor_b1 (usually, returned) |

### Activity schedule — hyp3: Mara works a part-time afternoon shift (13:30-18:00) and leaves her house keys on the entry table because she uses a key

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_study_work | weekday (5×/wk) | 9.0h | 3.5h | laptop_mara→kitchen_table_k1 (usually, left); notebook_mara→kitchen_table_k1 (usually, left); pen_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left) |
| weekend_yoga | weekend (2×/wk) | 9.5h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, left); water_bottle_mara→bedroom_floor_b1 (usually, returned) |
| weekend_grocery | weekend (1×/wk) | 10.0h | 1.5h | keys_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (almost_always, returned); wallet_mara→OUT_OF_HOUSE (almost_always, returned) |
| afternoon_shift | weekday (5×/wk) | 13.5h | 4.5h | phone_mara→OUT_OF_HOUSE (almost_always, returned); wallet_mara→OUT_OF_HOUSE (almost_always, returned); jacket_mara→OUT_OF_HOUSE (usually, returned); backpack_mara→OUT_OF_HOUSE (usually, returned); water_bottle_mara→OUT_OF_HOUSE (usually, returned) |
| evening_relax | both (7×/wk) | 19.0h | 2.0h | tablet_mara→couch_l1 (usually, left); blanket_mara→couch_l1 (usually, left); remote_shared_1→couch_l1 (usually, left) |

### Activity schedule — hyp4: Mara is a freelancer/parent home all day; at 15:08 she just returned from a 14:00 errand and is still dressed (jacket on

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_coffee_brew | both (7×/wk) | 7.0h | 1.0h | mug_mara→counter_k1 (almost_always, left); water_bottle_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (sometimes, left) |
| weekend_yoga_session | weekend (2×/wk) | 9.0h | 1.0h | yoga_mat_mara→bedroom_floor_b1 (usually, left); headphones_mara→bedroom_floor_b1 (usually, returned) |
| freelance_work_block | weekday (5×/wk) | 10.0h | 3.0h | laptop_mara→desk_b1 (usually, left); notebook_mara→desk_b1 (usually, left); pen_mara→desk_b1 (usually, left) |
| afternoon_errand | weekday (3×/wk) | 14.0h | 1.0h | jacket_mara→ON_PERSON (usually, returned); backpack_mara→ON_PERSON (usually, returned); phone_mara→ON_PERSON (almost_always, left); wallet_mara→ON_PERSON (almost_always, left); keys_mara→ON_PERSON (usually, returned) |
| evening_cooking | both (7×/wk) | 18.5h | 1.5h | pan_shared_1→counter_k1 (usually, left); pot_shared_1→counter_k1 (sometimes, returned); class:plate→kitchen_table_k1 (usually, left) |

### Activity schedule — hyp5: Mara is a homebody who stays in all day; at 15:08 she is relaxing and the missing items are ON_PERSON because she is in 

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_routine | both (7×/wk) | 6.5h | 1.0h | mug_mara→kitchen_table_k1 (usually, left); phone_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (usually, left) |
| daytime_home_chill | both (7×/wk) | 9.0h | 6.0h | tablet_mara→coffee_table_l1 (almost_always, left); blanket_mara→couch_l1 (usually, left); remote_shared_1→coffee_table_l1 (usually, left); headphones_mara→coffee_table_l1 (sometimes, left) |
| weekend_brunch_out | weekend (2×/wk) | 11.0h | 2.0h | keys_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (almost_always, returned); wallet_mara→OUT_OF_HOUSE (almost_always, returned); jacket_mara→OUT_OF_HOUSE (usually, returned) |
| sunday_cleaning | weekend (1×/wk) | 14.0h | 2.0h | vacuum_cleaner_shared_1→bedroom_floor_b1 (usually, returned); laundry_basket_mara→bedroom_floor_b1 (usually, left); blanket_mara→bed_b1 (sometimes, returned) |
| evening_gym_outing | weekday (4×/wk) | 18.8h | 2.5h | keys_mara→OUT_OF_HOUSE (usually, returned); phone_mara→ON_PERSON (almost_always, left); jacket_mara→ON_PERSON (usually, returned); backpack_mara→ON_PERSON (usually, returned); water_bottle_mara→ON_PERSON (usually, returned) |

### Per object — truth in the first column, each hypothesis beside it

| object | TRUTH | hyp1 | hyp2 | hyp3 | hyp4 | hyp5 |
|---|---|---|---|---|---|---|
| backpack_mara | home **entry_hook_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE<br>after: meal_prep→chair_k1(0.5), work_away→entry_hook_e1(0.8), gym→entry_hook_e1(0.8) | work_commute_out→OUT_OF_HOUSE (almo,ret) | afternoon_errand→ON_PERSON (usua,ret)<br>weekend_outing→OUT_OF_HOUSE (usua,ret) | afternoon_shift→OUT_OF_HOUSE (usua,ret) | rest entry_floor_e1<br>afternoon_errand→ON_PERSON (usua,ret) | rest entry_floor_e1<br>evening_gym_outing→ON_PERSON (usua,ret) |
| blanket_mara | home **couch_l1**<br>during: watch_tv→couch_l1, relax→couch_l1<br>after: watch_tv→couch_l1(0.8), relax→couch_l1(0.8) | weekend_cleaning→bed_b1 (some,ret) | — *(fallback)* | evening_relax→couch_l1 (usua,lef) | — *(fallback)* | daytime_home_chill→couch_l1 (usua,lef)<br>sunday_cleaning→bed_b1 (some,ret) |
| book_mara | home **bookshelf_l1**<br>during: walk→OUT_OF_HOUSE<br>after: reading→couch_l1(0.6), walk→couch_l1(0.7) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| bowl_shared_1 | home **entry_table_e1**<br>during: tidy_up→kitchen_table_k1<br>after: tidy_up→entry_table_e1(0.9), snack→entry_table_e1(0.2) | rest cupboard_k1<br>evening_dinner→kitchen_table_k1 (usua,lef) | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 |
| bowl_shared_2 | home **cupboard_k1**<br>during: breakfast→kitchen_table_k1, put_away_dishes→dish_rack_k1<br>after: breakfast→kitchen_table_k1(0.5), put_away_dishes→cupboard_k1(0.8) | rest cupboard_k1<br>evening_dinner→kitchen_table_k1 (usua,lef) | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 |
| charger_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: work_away→kitchen_table_k1(0.7), work_home→kitchen_table_k1(0.9) | rest nightstand_b1 | rest desk_b1<br>morning_coffee→kitchen_table_k1 (some,lef) | rest desk_b1 | rest kitchen_table_k1<br>morning_coffee_brew→kitchen_table_k1 (some,lef) | rest kitchen_table_k1<br>morning_routine→kitchen_table_k1 (usua,lef) |
| glasses_mara | home **kitchen_table_k1**<br>during: reading→couch_l1, work_home→kitchen_table_k1<br>after: reading→coffee_table_l1(0.5), work_home→kitchen_table_k1(0.8) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| hairbrush_mara | home **bathroom_shelf_ba1**<br>during: get_ready→bathroom_shelf_ba1, bedtime_routine→bathroom_shelf_ba1<br>after: get_ready→bathroom_shelf_ba1(0.8), bedtime_routine→bathroom_shelf_ba1(0.6) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| headphones_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: work_away→kitchen_table_k1(0.8), video_call→coffee_table_l1(0.6) | rest desk_b1 | rest desk_b1<br>evening_yoga→bedroom_floor_b1 (usua,ret) | rest bedroom_floor_b1 | rest kitchen_table_k1<br>weekend_yoga_session→bedroom_floor_b1 (usua,ret) | rest coffee_table_l1<br>daytime_home_chill→coffee_table_l1 (some,lef) |
| jacket_mara | home **entry_hook_e1**<br>during: work_away→OUT_OF_HOUSE, walk→OUT_OF_HOUSE<br>after: work_away→entry_hook_e1(0.7), walk→entry_hook_e1(0.7) | work_commute_out→OUT_OF_HOUSE (usua,ret) | rest entry_hook_e1<br>afternoon_errand→ON_PERSON (usua,ret)<br>weekend_outing→OUT_OF_HOUSE (usua,ret) | rest entry_hook_e1<br>afternoon_shift→OUT_OF_HOUSE (usua,ret) | rest entry_hook_e1<br>afternoon_errand→ON_PERSON (usua,ret) | rest entry_hook_e1<br>evening_gym_outing→ON_PERSON (usua,ret)<br>weekend_brunch_out→OUT_OF_HOUSE (usua,ret) |
| keys_mara | home **entry_table_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE<br>after: tidy_up→entry_table_e1(0.9), work_away→entry_table_e1(0.8) | work_commute_out→OUT_OF_HOUSE (almo,ret) | weekend_outing→OUT_OF_HOUSE (usua,ret) | weekend_grocery→OUT_OF_HOUSE (usua,ret) | afternoon_errand→ON_PERSON (usua,ret) | evening_gym_outing→OUT_OF_HOUSE (usua,ret)<br>weekend_brunch_out→OUT_OF_HOUSE (usua,ret) |
| laptop_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: tidy_up→kitchen_table_k1(0.8), work_away→kitchen_table_k1(0.9), work_home→kitchen_table_k1(0.9) | rest desk_b1<br>work_commute_out→OUT_OF_HOUSE (almo,ret) | rest desk_b1 | rest desk_b1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest desk_b1<br>freelance_work_block→desk_b1 (usua,lef) | rest desk_b1 |
| laundry_basket_mara | home **bedroom_floor_b1**<br>after: deep_clean→bedroom_floor_b1(0.2), laundry→bedroom_floor_b1(0.8) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | sunday_cleaning→bedroom_floor_b1 (usua,lef) |
| lunchbox_mara | home **counter_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: work_away→sink_k1(0.6), wash_dishes→counter_k1(0.8) | rest cupboard_k1<br>morning_prep→counter_k1 (usua,lef) | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 |
| makeup_kit_mara | home **bathroom_shelf_ba1**<br>during: appointment→OUT_OF_HOUSE<br>after: get_ready→bathroom_shelf_ba1(0.8), appointment→bathroom_shelf_ba1(0.8) | rest nightstand_b1 | rest bathroom_shelf_ba1 | rest nightstand_b1 | rest kitchen_table_k1 | rest bathroom_shelf_ba1 |
| medication_bottle_mara | home **bathroom_shelf_ba1**<br>during: take_medication→bathroom_shelf_ba1, bedtime_routine→bathroom_shelf_ba1<br>after: take_medication→bathroom_shelf_ba1(0.7), bedtime_routine→bathroom_shelf_ba1(0.6) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| mug_mara | home **cupboard_k1**<br>during: coffee→counter_k1, wash_dishes→sink_k1, reading→couch_l1<br>after: coffee→counter_k1(0.6), wash_dishes→dish_rack_k1(0.7), reading→coffee_table_l1(0.6) | rest cupboard_k1<br>morning_prep→counter_k1 (usua,lef) | rest cupboard_k1<br>wfh_work_block→coffee_table_l1 (usua,lef)<br>morning_coffee→kitchen_table_k1 (usua,lef) | rest cupboard_k1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest counter_k1<br>morning_coffee_brew→counter_k1 (almo,lef) | rest cupboard_k1<br>morning_routine→kitchen_table_k1 (usua,lef) |
| mug_shared_1 | home **cupboard_k1**<br>during: put_away_dishes→dish_rack_k1, socialise_home→couch_l1<br>after: put_away_dishes→cupboard_k1(0.8), socialise_home→coffee_table_l1(0.5) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| notebook_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: work_away→kitchen_table_k1(0.9), work_home→kitchen_table_k1(0.9) | rest desk_b1 | rest desk_b1 | rest kitchen_table_k1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest desk_b1<br>freelance_work_block→desk_b1 (usua,lef) | rest desk_b1 |
| pan_shared_1 | home **cupboard_k1**<br>during: breakfast→kitchen_table_k1, dinner→kitchen_table_k1<br>after: breakfast→counter_k1(0.4), dinner→sink_k1(0.4) | rest cupboard_k1<br>evening_dinner→counter_k1 (usua,ret) | rest cupboard_k1 | rest cupboard_k1 | rest counter_k1<br>evening_cooking→counter_k1 (usua,lef) | rest cupboard_k1 |
| pen_mara | home **kitchen_table_k1**<br>during: meal_prep→counter_k1, tidy_up→kitchen_table_k1<br>after: meal_prep→kitchen_table_k1(0.6), tidy_up→kitchen_table_k1(0.7) | rest desk_b1 | rest desk_b1 | rest kitchen_table_k1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>freelance_work_block→desk_b1 (usua,lef) | rest kitchen_table_k1 |
| phone_mara | home **nightstand_b1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE<br>after: wake_up→nightstand_b1(0.8), work_away→kitchen_table_k1(0.5), phone_time→couch_l1(0.5) | work_commute_out→OUT_OF_HOUSE (almo,ret) | afternoon_errand→ON_PERSON (almo,lef)<br>weekend_outing→OUT_OF_HOUSE (almo,ret) | afternoon_shift→OUT_OF_HOUSE (almo,ret)<br>weekend_grocery→OUT_OF_HOUSE (almo,ret) | afternoon_errand→ON_PERSON (almo,lef) | rest kitchen_table_k1<br>morning_routine→kitchen_table_k1 (usua,lef)<br>evening_gym_outing→ON_PERSON (almo,lef)<br>weekend_brunch_out→OUT_OF_HOUSE (almo,ret) |
| plate_shared_1 | home **cupboard_k1**<br>during: dinner→kitchen_table_k1, wash_dishes→sink_k1<br>after: dinner→kitchen_table_k1(0.5), wash_dishes→dish_rack_k1(0.8) | evening_dinner→kitchen_table_k1 (usua,lef) | — *(fallback)* | — *(fallback)* | evening_cooking→kitchen_table_k1 (usua,lef) | — *(fallback)* |
| plate_shared_2 | home **cupboard_k1**<br>during: meal_prep→counter_k1, lunch→kitchen_table_k1<br>after: meal_prep→counter_k1(0.6), work_away→kitchen_table_k1(0.5), lunch→kitchen_table_k1(0.5) | rest cupboard_k1<br>evening_dinner→kitchen_table_k1 (usua,lef) | rest cupboard_k1 | rest cupboard_k1 | rest counter_k1<br>evening_cooking→kitchen_table_k1 (usua,lef) | rest cupboard_k1 |
| pot_shared_1 | home **cupboard_k1**<br>during: wash_dishes→sink_k1, batch_cooking→counter_k1<br>after: wash_dishes→dish_rack_k1(0.5), batch_cooking→sink_k1(0.6) | — *(fallback)* | — *(fallback)* | — *(fallback)* | evening_cooking→counter_k1 (some,ret) | — *(fallback)* |
| remote_shared_1 | home **coffee_table_l1**<br>during: watch_tv→couch_l1, deep_clean→couch_l1<br>after: watch_tv→couch_l1(0.5), deep_clean→coffee_table_l1(0.5) | rest tv_stand_l1 | rest tv_stand_l1 | rest tv_stand_l1<br>evening_relax→couch_l1 (usua,lef) | rest tv_stand_l1 | rest tv_stand_l1<br>daytime_home_chill→coffee_table_l1 (usua,lef) |
| suitcase_mara | home **bedroom_floor_b1**<br>during: appointment→OUT_OF_HOUSE<br>after: appointment→bedroom_floor_b1(0.7) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| tablet_mara | home **coffee_table_l1**<br>after: batch_cooking→counter_k1(0.7), video_call→coffee_table_l1(0.7) | — *(fallback)* | wfh_work_block→coffee_table_l1 (almo,lef) | evening_relax→couch_l1 (usua,lef) | — *(fallback)* | daytime_home_chill→coffee_table_l1 (almo,lef) |
| towel_mara | home **towel_rack_ba1**<br>after: shower→towel_rack_ba1(0.8), laundry→bedroom_floor_b1(0.4) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| umbrella_mara | home **entry_floor_e1**<br>after: tidy_up→entry_floor_e1(0.7) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| vacuum_cleaner_shared_1 | home **bedroom_floor_b1**<br>during: deep_clean→couch_l1<br>after: deep_clean→bedroom_floor_b1(0.7) | weekend_cleaning→bedroom_floor_b1 (usua,ret) | — *(fallback)* | — *(fallback)* | — *(fallback)* | sunday_cleaning→bedroom_floor_b1 (usua,ret) |
| wallet_mara | home **entry_table_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE<br>after: work_away→entry_table_e1(0.8), appointment→entry_table_e1(0.7) | work_commute_out→OUT_OF_HOUSE (almo,ret) | afternoon_errand→ON_PERSON (almo,lef) | afternoon_shift→OUT_OF_HOUSE (almo,ret)<br>weekend_grocery→OUT_OF_HOUSE (almo,ret) | afternoon_errand→ON_PERSON (almo,lef) | weekend_brunch_out→OUT_OF_HOUSE (almo,ret) |
| water_bottle_mara | home **counter_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE<br>after: work_away→kitchen_table_k1(0.6), gym→couch_l1(0.5), bedtime_routine→nightstand_b1(0.6) | rest counter_k1<br>morning_prep→counter_k1 (usua,lef)<br>weekend_yoga→bedroom_floor_b1 (usua,ret) | rest desk_b1<br>wfh_work_block→coffee_table_l1 (usua,lef) | rest counter_k1<br>afternoon_shift→OUT_OF_HOUSE (usua,ret)<br>weekend_yoga→bedroom_floor_b1 (usua,ret) | rest kitchen_table_k1<br>morning_coffee_brew→kitchen_table_k1 (usua,lef) | rest counter_k1<br>evening_gym_outing→ON_PERSON (usua,ret) |
| watering_can_mara | home **sink_k1**<br>during: pet_care→counter_k1<br>after: deep_clean→sink_k1(0.2), pet_care→sink_k1(0.7) | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* | — *(fallback)* |
| yoga_mat_mara | home **couch_l1**<br>during: gym→OUT_OF_HOUSE<br>after: tidy_up→couch_l1(0.6), gym→couch_l1(0.8) | rest bedroom_floor_b1<br>weekend_yoga→bedroom_floor_b1 (usua,lef) | rest bedroom_floor_b1<br>evening_yoga→bedroom_floor_b1 (usua,lef) | rest couch_l1<br>weekend_yoga→bedroom_floor_b1 (usua,lef) | rest couch_l1<br>weekend_yoga_session→bedroom_floor_b1 (usua,lef) | rest couch_l1 |

### Scorecard (exact joins only)

| hypothesis | objects mentioned | stated rest = true home | moves whose destination the truth ever uses | true carry-out objects it sends OUT_OF_HOUSE | objects it sends OUT that never leave | weekday-only activities |
|---|---|---|---|---|---|---|
| hyp1 | 23/35 | 5/15 | 15/18 | 6/15 | 0 | 3/5 (truth: 3) |
| hyp2 | 21/35 | 6/16 | 7/15 | 4/15 | 0 | 3/5 (truth: 3) |
| hyp3 | 22/35 | 9/16 | 13/17 | 6/15 | 0 | 2/5 (truth: 3) |
| hyp4 | 22/35 | 6/17 | 7/17 | 0/15 | 0 | 2/5 (truth: 3) |
| hyp5 | 24/35 | 10/18 | 13/19 | 4/15 | 0 | 1/5 (truth: 3) |

Truth: 15 objects leave the house during weekday work (backpack_mara, book_mara, charger_mara, headphones_mara, jacket_mara, keys_mara, laptop_mara, lunchbox_mara, makeup_kit_mara, notebook_mara, phone_mara, suitcase_mara, wallet_mara, water_bottle_mara, yoga_mat_mara).

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
| appointment | weekday (1wd/0we, 0.2×/wk) | 7.3h | 0.7h | ELSEWHERE | phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, makeup_kit_mara→OUT_OF_HOUSE, suitcase_mara→OUT_OF_HOUSE | makeup_kit_mara→bathroom_shelf_ba1, wallet_mara→entry_table_e1, suitcase_mara→bedroom_floor_b1 |
| pet_care | weekend (0wd/1we, 0.2×/wk) | 8.0h | 0.2h | counter_k1 | watering_can_mara→counter_k1 | watering_can_mara→sink_k1 |
| nap | weekend (0wd/1we, 0.2×/wk) | 9.0h | 1.2h | bed_b1 |  |  |
| groceries | weekend (0wd/3we, 0.8×/wk) | 9.3h | 0.9h | None |  |  |
| batch_cooking | weekend (0wd/3we, 0.8×/wk) | 9.5h | 1.5h | counter_k1 | pot_shared_1→counter_k1 | pot_shared_1→sink_k1, tablet_mara→counter_k1 |
| laundry | weekend (0wd/4we, 1.0×/wk) | 9.5h | 0.5h | bedroom_floor_b1 |  | towel_mara→bedroom_floor_b1, laundry_basket_mara→bedroom_floor_b1 |
| work_away | weekday (18wd/0we, 4.5×/wk) | 9.6h | 4.1h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | phone_mara→kitchen_table_k1, backpack_mara→entry_hook_e1, plate_shared_2→kitchen_table_k1, laptop_mara→kitchen_table_k1, keys_mara→entry_table_e1 … |
| take_out_bins | weekend (0wd/1we, 0.2×/wk) | 10.0h | 0.2h | entry_floor_e1 |  |  |
| deep_clean | weekend (0wd/2we, 0.5×/wk) | 10.8h | 1.1h | couch_l1 | remote_shared_1→couch_l1, vacuum_cleaner_shared_1→couch_l1 | remote_shared_1→coffee_table_l1, laundry_basket_mara→bedroom_floor_b1, vacuum_cleaner_shared_1→bedroom_floor_b1, watering_can_mara→sink_k1 |
| walk | both (2wd/6we, 2.0×/wk) | 11.5h | 0.6h | ELSEWHERE | phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE, book_mara→OUT_OF_HOUSE | jacket_mara→entry_hook_e1, book_mara→couch_l1 |
| tidy_up | both (4wd/5we, 2.2×/wk) | 11.5h | 0.3h | kitchen_table_k1 | pen_mara→kitchen_table_k1, bowl_shared_1→kitchen_table_k1 | pen_mara→kitchen_table_k1, laptop_mara→kitchen_table_k1, keys_mara→entry_table_e1, umbrella_mara→entry_floor_e1, bowl_shared_1→entry_table_e1 … |
| work_home | weekday (4wd/0we, 1.0×/wk) | 11.7h | 1.7h | kitchen_table_k1 | glasses_mara→kitchen_table_k1 | laptop_mara→kitchen_table_k1, charger_mara→kitchen_table_k1, notebook_mara→kitchen_table_k1, glasses_mara→kitchen_table_k1 |
| relax | weekend (0wd/1we, 0.2×/wk) | 12.0h | 1.0h | couch_l1 | blanket_mara→couch_l1 | blanket_mara→couch_l1 |
| wash_dishes | both (6wd/8we, 3.5×/wk) | 12.1h | 0.2h | sink_k1 | mug_mara→sink_k1, plate_shared_1→sink_k1, pot_shared_1→sink_k1 | mug_mara→dish_rack_k1, lunchbox_mara→counter_k1, plate_shared_1→dish_rack_k1, pot_shared_1→dish_rack_k1 |
| lunch | both (20wd/8we, 7.0×/wk) | 12.2h | 0.4h | kitchen_table_k1 | plate_shared_2→kitchen_table_k1 | plate_shared_2→kitchen_table_k1 |
| day_sleep | weekday (1wd/0we, 0.2×/wk) | 12.4h | 1.6h | bed_b1 |  |  |
| traveling | both (19wd/3we, 5.5×/wk) | 13.1h | 0.3h | None |  |  |
| hobby | both (1wd/1we, 0.5×/wk) | 13.4h | 0.8h | couch_l1 |  |  |
| reading | both (5wd/8we, 3.2×/wk) | 14.0h | 1.1h | couch_l1 | mug_mara→couch_l1, glasses_mara→couch_l1 | mug_mara→coffee_table_l1, glasses_mara→coffee_table_l1, book_mara→couch_l1 |
| video_call | both (1wd/1we, 0.5×/wk) | 14.1h | 0.8h | couch_l1 |  | headphones_mara→coffee_table_l1, tablet_mara→coffee_table_l1 |
| put_away_dishes | both (1wd/1we, 0.5×/wk) | 14.3h | 0.2h | dish_rack_k1 | bowl_shared_2→dish_rack_k1, mug_shared_1→dish_rack_k1 | bowl_shared_2→cupboard_k1, mug_shared_1→cupboard_k1 |
| lie_down | both (3wd/1we, 1.0×/wk) | 14.6h | 1.1h | bed_b1 |  |  |
| errands | weekday (1wd/0we, 0.2×/wk) | 15.7h | 0.5h | None |  |  |
| gym | both (4wd/3we, 1.8×/wk) | 16.0h | 0.7h | ELSEWHERE | phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, water_bottle_mara→OUT_OF_HOUSE, yoga_mat_mara→OUT_OF_HOUSE | backpack_mara→entry_hook_e1, yoga_mat_mara→couch_l1, water_bottle_mara→couch_l1 |
| night_out | weekday (1wd/0we, 0.2×/wk) | 16.0h | 2.0h | None |  |  |
| snack | weekday (7wd/0we, 1.8×/wk) | 16.2h | 0.2h | counter_k1 |  | bowl_shared_1→entry_table_e1 |
| socialise_home | weekday (1wd/0we, 0.2×/wk) | 17.2h | 1.8h | couch_l1 | mug_shared_1→couch_l1 | mug_shared_1→coffee_table_l1 |
| dinner | both (18wd/8we, 6.5×/wk) | 17.3h | 0.5h | kitchen_table_k1 | pan_shared_1→kitchen_table_k1, plate_shared_1→kitchen_table_k1 | pan_shared_1→sink_k1, plate_shared_1→kitchen_table_k1 |
| watch_tv | both (6wd/1we, 1.8×/wk) | 17.4h | 1.2h | couch_l1 | remote_shared_1→couch_l1, blanket_mara→couch_l1 | remote_shared_1→couch_l1, blanket_mara→couch_l1 |
| phone_time | both (6wd/1we, 1.8×/wk) | 17.6h | 0.2h | couch_l1 |  | phone_mara→couch_l1 |
| bedtime_routine | both (14wd/7we, 5.2×/wk) | 20.5h | 0.5h | bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1, hairbrush_mara→bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1, hairbrush_mara→bathroom_shelf_ba1, water_bottle_mara→nightstand_b1 |

### Activity schedule — hyp1: Mara works a morning shift 7:30-11:30 at a nearby location she walks to (cafe, library, co-working space); keys and wall

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_prep | weekday (5×/wk) | 7.0h | 0.5h | mug_mara→counter_k1 (usually, left); water_bottle_mara→counter_k1 (usually, left) |
| morning_shift | weekday (5×/wk) | 7.5h | 4.0h | phone_mara→OUT_OF_HOUSE (almost_always, returned); water_bottle_mara→OUT_OF_HOUSE (usually, returned); jacket_mara→OUT_OF_HOUSE (usually, returned) |
| weekend_yoga | weekend (2×/wk) | 9.0h | 1.0h | yoga_mat_mara→couch_l1 (usually, left); water_bottle_mara→couch_l1 (usually, returned) |
| afternoon_admin | weekday (5×/wk) | 13.0h | 3.0h | laptop_mara→kitchen_table_k1 (usually, left); pen_mara→kitchen_table_k1 (usually, left); notebook_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (sometimes, left) |
| evening_dinner | both (7×/wk) | 18.5h | 1.5h | class:plate→kitchen_table_k1 (usually, left); class:bowl→kitchen_table_k1 (usually, left); pan_shared_1→counter_k1 (usually, returned) |

### Activity schedule — hyp2: Mara works from home 9:00-16:30 using tablet as primary screen at coffee table and laptop at kitchen table; at 13:00 she

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_coffee | both (7×/wk) | 7.0h | 0.5h | mug_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (sometimes, left) |
| wfh_work_block | weekday (5×/wk) | 9.0h | 7.5h | tablet_mara→coffee_table_l1 (almost_always, left); mug_mara→coffee_table_l1 (usually, left); water_bottle_mara→coffee_table_l1 (usually, left); headphones_mara→coffee_table_l1 (sometimes, left) |
| weekend_outing | weekend (2×/wk) | 11.0h | 4.0h | keys_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (almost_always, returned); jacket_mara→OUT_OF_HOUSE (usually, returned); backpack_mara→ON_PERSON (usually, returned) |
| midday_video_call | weekday (3×/wk) | 12.5h | 1.0h | laptop_mara→ON_PERSON (usually, returned); headphones_mara→ON_PERSON (usually, returned) |
| evening_relax | both (7×/wk) | 19.0h | 2.0h | tablet_mara→couch_l1 (usually, left); blanket_mara→couch_l1 (usually, left) |

### Activity schedule — hyp3: Mara works a part-time afternoon shift 13:30-18:00 at a workplace where she uses a key fob, so house keys stay at entry 

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_study_work | weekday (5×/wk) | 9.0h | 3.5h | laptop_mara→kitchen_table_k1 (usually, left); notebook_mara→kitchen_table_k1 (usually, left); pen_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left); glasses_mara→kitchen_table_k1 (usually, left) |
| weekend_yoga | weekend (2×/wk) | 9.5h | 1.0h | yoga_mat_mara→couch_l1 (usually, left); water_bottle_mara→couch_l1 (usually, returned) |
| weekend_grocery | weekend (1×/wk) | 10.0h | 1.5h | keys_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (almost_always, returned); wallet_mara→OUT_OF_HOUSE (almost_always, returned) |
| afternoon_shift | weekday (5×/wk) | 13.5h | 4.5h | phone_mara→OUT_OF_HOUSE (almost_always, returned); wallet_mara→OUT_OF_HOUSE (almost_always, returned); jacket_mara→OUT_OF_HOUSE (usually, returned); backpack_mara→ON_PERSON (usually, returned); water_bottle_mara→OUT_OF_HOUSE (usually, returned) |
| evening_relax | both (7×/wk) | 19.0h | 2.0h | tablet_mara→couch_l1 (usually, left); blanket_mara→couch_l1 (usually, left); book_mara→couch_l1 (sometimes, left) |

### Activity schedule — hyp4: Mara is a freelancer home all day working at kitchen table; at 15:00 she just returned from a 14:00 errand (pharmacy, po

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_coffee_brew | both (7×/wk) | 7.0h | 1.0h | mug_mara→counter_k1 (almost_always, left); water_bottle_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (sometimes, left) |
| weekend_yoga_session | weekend (2×/wk) | 9.0h | 1.0h | yoga_mat_mara→couch_l1 (usually, left); headphones_mara→couch_l1 (usually, returned) |
| freelance_work_block | weekday (5×/wk) | 10.0h | 3.0h | laptop_mara→kitchen_table_k1 (usually, left); notebook_mara→kitchen_table_k1 (usually, left); pen_mara→kitchen_table_k1 (usually, left); glasses_mara→kitchen_table_k1 (usually, left) |
| afternoon_errand | weekday (3×/wk) | 14.0h | 1.0h | jacket_mara→ON_PERSON (usually, returned); backpack_mara→ON_PERSON (usually, returned); phone_mara→ON_PERSON (almost_always, left); wallet_mara→ON_PERSON (almost_always, left); keys_mara→ON_PERSON (usually, returned) |
| evening_cooking | both (7×/wk) | 18.5h | 1.5h | pan_shared_1→counter_k1 (usually, left); pot_shared_1→counter_k1 (sometimes, returned); class:plate→kitchen_table_k1 (usually, left) |

### Activity schedule — hyp5: Mara is a homebody who stays in all day with no regular outings; daytime is lounging on couch with tablet and blanket; e

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_routine | both (7×/wk) | 6.5h | 1.0h | mug_mara→kitchen_table_k1 (usually, left); phone_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (usually, left) |
| daytime_home_chill | both (7×/wk) | 9.0h | 6.0h | tablet_mara→coffee_table_l1 (almost_always, left); blanket_mara→couch_l1 (usually, left); headphones_mara→coffee_table_l1 (sometimes, left); book_mara→couch_l1 (sometimes, left) |
| weekend_brunch_out | weekend (1×/wk) | 11.0h | 2.0h | keys_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (almost_always, returned); wallet_mara→OUT_OF_HOUSE (almost_always, returned); jacket_mara→OUT_OF_HOUSE (usually, returned) |
| sunday_cleaning | weekend (1×/wk) | 14.0h | 2.0h | vacuum_cleaner_shared_1→bedroom_floor_b1 (usually, returned); laundry_basket_mara→bedroom_floor_b1 (usually, left); blanket_mara→bed_b1 (sometimes, returned) |
| evening_wind_down | both (7×/wk) | 19.0h | 2.0h | phone_mara→nightstand_b1 (usually, left); book_mara→couch_l1 (usually, left); glasses_mara→couch_l1 (sometimes, left) |

### Per object — truth in the first column, each hypothesis beside it

| object | TRUTH | hyp1 | hyp2 | hyp3 | hyp4 | hyp5 |
|---|---|---|---|---|---|---|
| backpack_mara | home **entry_hook_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE<br>after: meal_prep→chair_k1(0.5), work_away→entry_hook_e1(0.8), gym→entry_hook_e1(0.8) | rest chair_k1 | rest chair_k1<br>weekend_outing→ON_PERSON (usua,ret) | rest chair_k1<br>afternoon_shift→ON_PERSON (usua,ret) | rest chair_k1<br>afternoon_errand→ON_PERSON (usua,ret) | rest chair_k1 |
| blanket_mara | home **couch_l1**<br>during: watch_tv→couch_l1, relax→couch_l1<br>after: watch_tv→couch_l1(0.8), relax→couch_l1(0.8) | rest couch_l1 | rest couch_l1<br>evening_relax→couch_l1 (usua,lef) | rest couch_l1<br>evening_relax→couch_l1 (usua,lef) | rest couch_l1 | rest couch_l1<br>daytime_home_chill→couch_l1 (usua,lef)<br>sunday_cleaning→bed_b1 (some,ret) |
| book_mara | home **bookshelf_l1**<br>during: walk→OUT_OF_HOUSE<br>after: reading→couch_l1(0.6), walk→couch_l1(0.7) | rest bookshelf_l1 | rest bookshelf_l1 | rest bookshelf_l1<br>evening_relax→couch_l1 (some,lef) | rest bookshelf_l1 | rest bookshelf_l1<br>daytime_home_chill→couch_l1 (some,lef)<br>evening_wind_down→couch_l1 (usua,lef) |
| bowl_shared_1 | home **entry_table_e1**<br>during: tidy_up→kitchen_table_k1<br>after: tidy_up→entry_table_e1(0.9), snack→entry_table_e1(0.2) | rest kitchen_table_k1<br>evening_dinner→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1 |
| bowl_shared_2 | home **cupboard_k1**<br>during: breakfast→kitchen_table_k1, put_away_dishes→dish_rack_k1<br>after: breakfast→kitchen_table_k1(0.5), put_away_dishes→cupboard_k1(0.8) | rest sink_k1<br>evening_dinner→kitchen_table_k1 (usua,lef) | rest sink_k1 | rest sink_k1 | rest sink_k1 | rest sink_k1 |
| charger_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: work_away→kitchen_table_k1(0.7), work_home→kitchen_table_k1(0.9) | rest kitchen_table_k1 | rest kitchen_table_k1<br>morning_coffee→kitchen_table_k1 (some,lef) | rest kitchen_table_k1 | rest kitchen_table_k1<br>morning_coffee_brew→kitchen_table_k1 (some,lef) | rest kitchen_table_k1<br>morning_routine→kitchen_table_k1 (usua,lef) |
| glasses_mara | home **kitchen_table_k1**<br>during: reading→couch_l1, work_home→kitchen_table_k1<br>after: reading→coffee_table_l1(0.5), work_home→kitchen_table_k1(0.8) | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>freelance_work_block→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>evening_wind_down→couch_l1 (some,lef) |
| hairbrush_mara | home **bathroom_shelf_ba1**<br>during: get_ready→bathroom_shelf_ba1, bedtime_routine→bathroom_shelf_ba1<br>after: get_ready→bathroom_shelf_ba1(0.8), bedtime_routine→bathroom_shelf_ba1(0.6) | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 |
| headphones_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: work_away→kitchen_table_k1(0.8), video_call→coffee_table_l1(0.6) | rest kitchen_table_k1 | rest kitchen_table_k1<br>wfh_work_block→coffee_table_l1 (some,lef)<br>midday_video_call→ON_PERSON (usua,ret) | rest kitchen_table_k1 | rest kitchen_table_k1<br>weekend_yoga_session→couch_l1 (usua,ret) | rest coffee_table_l1<br>daytime_home_chill→coffee_table_l1 (some,lef) |
| jacket_mara | home **entry_hook_e1**<br>during: work_away→OUT_OF_HOUSE, walk→OUT_OF_HOUSE<br>after: work_away→entry_hook_e1(0.7), walk→entry_hook_e1(0.7) | rest entry_hook_e1<br>morning_shift→OUT_OF_HOUSE (usua,ret) | rest entry_hook_e1<br>weekend_outing→OUT_OF_HOUSE (usua,ret) | rest entry_hook_e1<br>afternoon_shift→OUT_OF_HOUSE (usua,ret) | rest entry_hook_e1<br>afternoon_errand→ON_PERSON (usua,ret) | rest entry_hook_e1<br>weekend_brunch_out→OUT_OF_HOUSE (usua,ret) |
| keys_mara | home **entry_table_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE<br>after: tidy_up→entry_table_e1(0.9), work_away→entry_table_e1(0.8) | rest entry_table_e1 | rest entry_table_e1<br>weekend_outing→OUT_OF_HOUSE (usua,ret) | rest entry_table_e1<br>weekend_grocery→OUT_OF_HOUSE (usua,ret) | rest entry_table_e1<br>afternoon_errand→ON_PERSON (usua,ret) | rest entry_table_e1<br>weekend_brunch_out→OUT_OF_HOUSE (usua,ret) |
| laptop_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: tidy_up→kitchen_table_k1(0.8), work_away→kitchen_table_k1(0.9), work_home→kitchen_table_k1(0.9) | rest kitchen_table_k1<br>afternoon_admin→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>midday_video_call→ON_PERSON (usua,ret) | rest kitchen_table_k1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>freelance_work_block→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 |
| laundry_basket_mara | home **bedroom_floor_b1**<br>after: deep_clean→bedroom_floor_b1(0.2), laundry→bedroom_floor_b1(0.8) | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1<br>sunday_cleaning→bedroom_floor_b1 (usua,lef) |
| lunchbox_mara | home **counter_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: work_away→sink_k1(0.6), wash_dishes→counter_k1(0.8) | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 |
| makeup_kit_mara | home **bathroom_shelf_ba1**<br>during: appointment→OUT_OF_HOUSE<br>after: get_ready→bathroom_shelf_ba1(0.8), appointment→bathroom_shelf_ba1(0.8) | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 |
| medication_bottle_mara | home **bathroom_shelf_ba1**<br>during: take_medication→bathroom_shelf_ba1, bedtime_routine→bathroom_shelf_ba1<br>after: take_medication→bathroom_shelf_ba1(0.7), bedtime_routine→bathroom_shelf_ba1(0.6) | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 |
| mug_mara | home **cupboard_k1**<br>during: coffee→counter_k1, wash_dishes→sink_k1, reading→couch_l1<br>after: coffee→counter_k1(0.6), wash_dishes→dish_rack_k1(0.7), reading→coffee_table_l1(0.6) | rest counter_k1<br>morning_prep→counter_k1 (usua,lef)<br>afternoon_admin→kitchen_table_k1 (some,lef) | rest counter_k1<br>wfh_work_block→coffee_table_l1 (usua,lef)<br>morning_coffee→kitchen_table_k1 (usua,lef) | rest counter_k1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest counter_k1<br>morning_coffee_brew→counter_k1 (almo,lef) | rest counter_k1<br>morning_routine→kitchen_table_k1 (usua,lef) |
| mug_shared_1 | home **cupboard_k1**<br>during: put_away_dishes→dish_rack_k1, socialise_home→couch_l1<br>after: put_away_dishes→cupboard_k1(0.8), socialise_home→coffee_table_l1(0.5) | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 |
| notebook_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: work_away→kitchen_table_k1(0.9), work_home→kitchen_table_k1(0.9) | rest kitchen_table_k1<br>afternoon_admin→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 | rest kitchen_table_k1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>freelance_work_block→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 |
| pan_shared_1 | home **cupboard_k1**<br>during: breakfast→kitchen_table_k1, dinner→kitchen_table_k1<br>after: breakfast→counter_k1(0.4), dinner→sink_k1(0.4) | rest counter_k1<br>evening_dinner→counter_k1 (usua,ret) | rest counter_k1 | rest counter_k1 | rest counter_k1<br>evening_cooking→counter_k1 (usua,lef) | rest counter_k1 |
| pen_mara | home **kitchen_table_k1**<br>during: meal_prep→counter_k1, tidy_up→kitchen_table_k1<br>after: meal_prep→kitchen_table_k1(0.6), tidy_up→kitchen_table_k1(0.7) | rest kitchen_table_k1<br>afternoon_admin→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 | rest kitchen_table_k1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>freelance_work_block→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 |
| phone_mara | home **nightstand_b1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE<br>after: wake_up→nightstand_b1(0.8), work_away→kitchen_table_k1(0.5), phone_time→couch_l1(0.5) | rest nightstand_b1<br>morning_shift→OUT_OF_HOUSE (almo,ret) | rest nightstand_b1<br>weekend_outing→OUT_OF_HOUSE (almo,ret) | rest nightstand_b1<br>afternoon_shift→OUT_OF_HOUSE (almo,ret)<br>weekend_grocery→OUT_OF_HOUSE (almo,ret) | rest nightstand_b1<br>afternoon_errand→ON_PERSON (almo,lef) | rest nightstand_b1<br>morning_routine→kitchen_table_k1 (usua,lef)<br>evening_wind_down→nightstand_b1 (usua,lef)<br>weekend_brunch_out→OUT_OF_HOUSE (almo,ret) |
| plate_shared_1 | home **cupboard_k1**<br>during: dinner→kitchen_table_k1, wash_dishes→sink_k1<br>after: dinner→kitchen_table_k1(0.5), wash_dishes→dish_rack_k1(0.8) | rest kitchen_table_k1<br>evening_dinner→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1<br>evening_cooking→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 |
| plate_shared_2 | home **cupboard_k1**<br>during: meal_prep→counter_k1, lunch→kitchen_table_k1<br>after: meal_prep→counter_k1(0.6), work_away→kitchen_table_k1(0.5), lunch→kitchen_table_k1(0.5) | rest counter_k1<br>evening_dinner→kitchen_table_k1 (usua,lef) | rest counter_k1 | rest counter_k1 | rest counter_k1<br>evening_cooking→kitchen_table_k1 (usua,lef) | rest counter_k1 |
| pot_shared_1 | home **cupboard_k1**<br>during: wash_dishes→sink_k1, batch_cooking→counter_k1<br>after: wash_dishes→dish_rack_k1(0.5), batch_cooking→sink_k1(0.6) | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1<br>evening_cooking→counter_k1 (some,ret) | rest cupboard_k1 |
| remote_shared_1 | home **coffee_table_l1**<br>during: watch_tv→couch_l1, deep_clean→couch_l1<br>after: watch_tv→couch_l1(0.5), deep_clean→coffee_table_l1(0.5) | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 |
| suitcase_mara | home **bedroom_floor_b1**<br>during: appointment→OUT_OF_HOUSE<br>after: appointment→bedroom_floor_b1(0.7) | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 |
| tablet_mara | home **coffee_table_l1**<br>after: batch_cooking→counter_k1(0.7), video_call→coffee_table_l1(0.7) | rest coffee_table_l1 | rest coffee_table_l1<br>wfh_work_block→coffee_table_l1 (almo,lef)<br>evening_relax→couch_l1 (usua,lef) | rest coffee_table_l1<br>evening_relax→couch_l1 (usua,lef) | rest coffee_table_l1 | rest coffee_table_l1<br>daytime_home_chill→coffee_table_l1 (almo,lef) |
| towel_mara | home **towel_rack_ba1**<br>after: shower→towel_rack_ba1(0.8), laundry→bedroom_floor_b1(0.4) | rest towel_rack_ba1 | rest towel_rack_ba1 | rest towel_rack_ba1 | rest towel_rack_ba1 | rest towel_rack_ba1 |
| umbrella_mara | home **entry_floor_e1**<br>after: tidy_up→entry_floor_e1(0.7) | rest entry_floor_e1 | rest entry_floor_e1 | rest entry_floor_e1 | rest entry_floor_e1 | rest entry_floor_e1 |
| vacuum_cleaner_shared_1 | home **bedroom_floor_b1**<br>during: deep_clean→couch_l1<br>after: deep_clean→bedroom_floor_b1(0.7) | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1<br>sunday_cleaning→bedroom_floor_b1 (usua,ret) |
| wallet_mara | home **entry_table_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE<br>after: work_away→entry_table_e1(0.8), appointment→entry_table_e1(0.7) | rest entry_table_e1 | rest entry_table_e1 | rest entry_table_e1<br>afternoon_shift→OUT_OF_HOUSE (almo,ret)<br>weekend_grocery→OUT_OF_HOUSE (almo,ret) | rest entry_table_e1<br>afternoon_errand→ON_PERSON (almo,lef) | rest entry_table_e1<br>weekend_brunch_out→OUT_OF_HOUSE (almo,ret) |
| water_bottle_mara | home **counter_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE<br>after: work_away→kitchen_table_k1(0.6), gym→couch_l1(0.5), bedtime_routine→nightstand_b1(0.6) | rest kitchen_table_k1<br>morning_shift→OUT_OF_HOUSE (usua,ret)<br>morning_prep→counter_k1 (usua,lef)<br>weekend_yoga→couch_l1 (usua,ret) | rest kitchen_table_k1<br>wfh_work_block→coffee_table_l1 (usua,lef) | rest kitchen_table_k1<br>afternoon_shift→OUT_OF_HOUSE (usua,ret)<br>weekend_yoga→couch_l1 (usua,ret) | rest kitchen_table_k1<br>morning_coffee_brew→kitchen_table_k1 (usua,lef) | rest counter_k1 |
| watering_can_mara | home **sink_k1**<br>during: pet_care→counter_k1<br>after: deep_clean→sink_k1(0.2), pet_care→sink_k1(0.7) | rest sink_k1 | rest sink_k1 | rest sink_k1 | rest sink_k1 | rest sink_k1 |
| yoga_mat_mara | home **couch_l1**<br>during: gym→OUT_OF_HOUSE<br>after: tidy_up→couch_l1(0.6), gym→couch_l1(0.8) | rest couch_l1<br>weekend_yoga→couch_l1 (usua,lef) | rest couch_l1 | rest couch_l1<br>weekend_yoga→couch_l1 (usua,lef) | rest couch_l1<br>weekend_yoga_session→couch_l1 (usua,lef) | rest couch_l1 |

### Scorecard (exact joins only)

| hypothesis | objects mentioned | stated rest = true home | moves whose destination the truth ever uses | true carry-out objects it sends OUT_OF_HOUSE | objects it sends OUT that never leave | weekday-only activities |
|---|---|---|---|---|---|---|
| hyp1 | 35/35 | 25/35 | 15/16 | 3/15 | 0 | 3/5 (truth: 3) |
| hyp2 | 35/35 | 25/35 | 8/14 | 3/15 | 0 | 2/5 (truth: 3) |
| hyp3 | 35/35 | 25/35 | 15/18 | 5/15 | 0 | 2/5 (truth: 3) |
| hyp4 | 35/35 | 25/35 | 12/18 | 0/15 | 0 | 2/5 (truth: 3) |
| hyp5 | 35/35 | 25/35 | 15/17 | 4/15 | 0 | 0/5 (truth: 3) |

Truth: 15 objects leave the house during weekday work (backpack_mara, book_mara, charger_mara, headphones_mara, jacket_mara, keys_mara, laptop_mara, lunchbox_mara, makeup_kit_mara, notebook_mara, phone_mara, suitcase_mara, wallet_mara, water_bottle_mara, yoga_mat_mara).

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
| appointment | weekday (1wd/0we, 0.2×/wk) | 7.3h | 0.7h | ELSEWHERE | phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, makeup_kit_mara→OUT_OF_HOUSE, suitcase_mara→OUT_OF_HOUSE | makeup_kit_mara→bathroom_shelf_ba1, wallet_mara→entry_table_e1, suitcase_mara→bedroom_floor_b1 |
| pet_care | weekend (0wd/1we, 0.2×/wk) | 8.0h | 0.2h | counter_k1 | watering_can_mara→counter_k1 | watering_can_mara→sink_k1 |
| nap | weekend (0wd/1we, 0.2×/wk) | 9.0h | 1.2h | bed_b1 |  |  |
| groceries | weekend (0wd/3we, 0.8×/wk) | 9.3h | 0.9h | None |  |  |
| batch_cooking | weekend (0wd/3we, 0.8×/wk) | 9.5h | 1.5h | counter_k1 | pot_shared_1→counter_k1 | pot_shared_1→sink_k1, tablet_mara→counter_k1 |
| laundry | weekend (0wd/4we, 1.0×/wk) | 9.5h | 0.5h | bedroom_floor_b1 |  | towel_mara→bedroom_floor_b1, laundry_basket_mara→bedroom_floor_b1 |
| work_away | weekday (18wd/0we, 4.5×/wk) | 9.6h | 4.1h | ELSEWHERE | laptop_mara→OUT_OF_HOUSE, phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE … | phone_mara→kitchen_table_k1, backpack_mara→entry_hook_e1, plate_shared_2→kitchen_table_k1, laptop_mara→kitchen_table_k1, keys_mara→entry_table_e1 … |
| take_out_bins | weekend (0wd/1we, 0.2×/wk) | 10.0h | 0.2h | entry_floor_e1 |  |  |
| deep_clean | weekend (0wd/2we, 0.5×/wk) | 10.8h | 1.1h | couch_l1 | remote_shared_1→couch_l1, vacuum_cleaner_shared_1→couch_l1 | remote_shared_1→coffee_table_l1, laundry_basket_mara→bedroom_floor_b1, vacuum_cleaner_shared_1→bedroom_floor_b1, watering_can_mara→sink_k1 |
| walk | both (2wd/6we, 2.0×/wk) | 11.5h | 0.6h | ELSEWHERE | phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, jacket_mara→OUT_OF_HOUSE, book_mara→OUT_OF_HOUSE | jacket_mara→entry_hook_e1, book_mara→couch_l1 |
| tidy_up | both (4wd/5we, 2.2×/wk) | 11.5h | 0.3h | kitchen_table_k1 | pen_mara→kitchen_table_k1, bowl_shared_1→kitchen_table_k1 | pen_mara→kitchen_table_k1, laptop_mara→kitchen_table_k1, keys_mara→entry_table_e1, umbrella_mara→entry_floor_e1, bowl_shared_1→entry_table_e1 … |
| work_home | weekday (4wd/0we, 1.0×/wk) | 11.7h | 1.7h | kitchen_table_k1 | glasses_mara→kitchen_table_k1 | laptop_mara→kitchen_table_k1, charger_mara→kitchen_table_k1, notebook_mara→kitchen_table_k1, glasses_mara→kitchen_table_k1 |
| relax | weekend (0wd/1we, 0.2×/wk) | 12.0h | 1.0h | couch_l1 | blanket_mara→couch_l1 | blanket_mara→couch_l1 |
| wash_dishes | both (6wd/8we, 3.5×/wk) | 12.1h | 0.2h | sink_k1 | mug_mara→sink_k1, plate_shared_1→sink_k1, pot_shared_1→sink_k1 | mug_mara→dish_rack_k1, lunchbox_mara→counter_k1, plate_shared_1→dish_rack_k1, pot_shared_1→dish_rack_k1 |
| lunch | both (20wd/8we, 7.0×/wk) | 12.2h | 0.4h | kitchen_table_k1 | plate_shared_2→kitchen_table_k1 | plate_shared_2→kitchen_table_k1 |
| day_sleep | weekday (1wd/0we, 0.2×/wk) | 12.4h | 1.6h | bed_b1 |  |  |
| traveling | both (19wd/3we, 5.5×/wk) | 13.1h | 0.3h | None |  |  |
| hobby | both (1wd/1we, 0.5×/wk) | 13.4h | 0.8h | couch_l1 |  |  |
| reading | both (5wd/8we, 3.2×/wk) | 14.0h | 1.1h | couch_l1 | mug_mara→couch_l1, glasses_mara→couch_l1 | mug_mara→coffee_table_l1, glasses_mara→coffee_table_l1, book_mara→couch_l1 |
| video_call | both (1wd/1we, 0.5×/wk) | 14.1h | 0.8h | couch_l1 |  | headphones_mara→coffee_table_l1, tablet_mara→coffee_table_l1 |
| put_away_dishes | both (1wd/1we, 0.5×/wk) | 14.3h | 0.2h | dish_rack_k1 | bowl_shared_2→dish_rack_k1, mug_shared_1→dish_rack_k1 | bowl_shared_2→cupboard_k1, mug_shared_1→cupboard_k1 |
| lie_down | both (3wd/1we, 1.0×/wk) | 14.6h | 1.1h | bed_b1 |  |  |
| errands | weekday (1wd/0we, 0.2×/wk) | 15.7h | 0.5h | None |  |  |
| gym | both (4wd/3we, 1.8×/wk) | 16.0h | 0.7h | ELSEWHERE | phone_mara→OUT_OF_HOUSE, keys_mara→OUT_OF_HOUSE, wallet_mara→OUT_OF_HOUSE, backpack_mara→OUT_OF_HOUSE, water_bottle_mara→OUT_OF_HOUSE, yoga_mat_mara→OUT_OF_HOUSE | backpack_mara→entry_hook_e1, yoga_mat_mara→couch_l1, water_bottle_mara→couch_l1 |
| night_out | weekday (1wd/0we, 0.2×/wk) | 16.0h | 2.0h | None |  |  |
| snack | weekday (7wd/0we, 1.8×/wk) | 16.2h | 0.2h | counter_k1 |  | bowl_shared_1→entry_table_e1 |
| socialise_home | weekday (1wd/0we, 0.2×/wk) | 17.2h | 1.8h | couch_l1 | mug_shared_1→couch_l1 | mug_shared_1→coffee_table_l1 |
| dinner | both (18wd/8we, 6.5×/wk) | 17.3h | 0.5h | kitchen_table_k1 | pan_shared_1→kitchen_table_k1, plate_shared_1→kitchen_table_k1 | pan_shared_1→sink_k1, plate_shared_1→kitchen_table_k1 |
| watch_tv | both (6wd/1we, 1.8×/wk) | 17.4h | 1.2h | couch_l1 | remote_shared_1→couch_l1, blanket_mara→couch_l1 | remote_shared_1→couch_l1, blanket_mara→couch_l1 |
| phone_time | both (6wd/1we, 1.8×/wk) | 17.6h | 0.2h | couch_l1 |  | phone_mara→couch_l1 |
| bedtime_routine | both (14wd/7we, 5.2×/wk) | 20.5h | 0.5h | bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1, hairbrush_mara→bathroom_shelf_ba1 | medication_bottle_mara→bathroom_shelf_ba1, hairbrush_mara→bathroom_shelf_ba1, water_bottle_mara→nightstand_b1 |

### Activity schedule — hyp1: Mara takes a short morning walk/errand 7:15-7:45 (pharmacy, post, neighbour's garden) carrying only water bottle and jac

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_prep | weekday (5×/wk) | 7.0h | 0.5h | mug_mara→counter_k1 (usually, left); water_bottle_mara→counter_k1 (usually, left) |
| morning_walk | weekday (5×/wk) | 7.2h | 0.5h | water_bottle_mara→OUT_OF_HOUSE (usually, returned); jacket_mara→OUT_OF_HOUSE (usually, returned) |
| weekend_yoga | weekend (2×/wk) | 9.0h | 1.0h | yoga_mat_mara→couch_l1 (usually, left); water_bottle_mara→couch_l1 (usually, returned) |
| afternoon_admin | weekday (5×/wk) | 13.0h | 3.0h | laptop_mara→kitchen_table_k1 (usually, left); pen_mara→kitchen_table_k1 (usually, left); notebook_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (sometimes, left) |
| evening_dinner | both (7×/wk) | 18.5h | 1.5h | class:plate→kitchen_table_k1 (usually, left); class:bowl→kitchen_table_k1 (usually, left); pan_shared_1→kitchen_table_k1 (usually, returned) |

### Activity schedule — hyp2: Mara works from home 9:00-16:30 using tablet as primary screen at coffee table (living room) with mug and water bottle n

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_coffee | both (7×/wk) | 7.0h | 0.5h | mug_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (sometimes, left) |
| wfh_work_block | weekday (5×/wk) | 9.0h | 7.5h | tablet_mara→coffee_table_l1 (almost_always, left); mug_mara→coffee_table_l1 (usually, left); water_bottle_mara→coffee_table_l1 (usually, left) |
| weekend_outing | weekend (2×/wk) | 11.0h | 4.0h | keys_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (almost_always, returned); jacket_mara→OUT_OF_HOUSE (usually, returned); backpack_mara→ON_PERSON (usually, returned) |
| evening_relax | both (7×/wk) | 19.0h | 2.0h | tablet_mara→couch_l1 (usually, left); blanket_mara→couch_l1 (usually, left) |

### Activity schedule — hyp3: Mara works a part-time afternoon shift 13:30-18:00 at a workplace where she uses a key fob, so house keys stay at entry 

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_study_work | weekday (5×/wk) | 9.0h | 3.5h | laptop_mara→kitchen_table_k1 (usually, left); notebook_mara→kitchen_table_k1 (usually, left); pen_mara→kitchen_table_k1 (usually, left); mug_mara→kitchen_table_k1 (usually, left); glasses_mara→kitchen_table_k1 (usually, left) |
| weekend_yoga | weekend (2×/wk) | 9.5h | 1.0h | yoga_mat_mara→couch_l1 (usually, left); water_bottle_mara→couch_l1 (usually, returned) |
| weekend_grocery | weekend (1×/wk) | 10.0h | 1.5h | keys_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (almost_always, returned); wallet_mara→OUT_OF_HOUSE (almost_always, returned) |
| afternoon_shift | weekday (5×/wk) | 13.5h | 4.5h | phone_mara→OUT_OF_HOUSE (almost_always, returned); wallet_mara→OUT_OF_HOUSE (almost_always, returned); jacket_mara→OUT_OF_HOUSE (usually, returned); backpack_mara→ON_PERSON (usually, returned); water_bottle_mara→OUT_OF_HOUSE (usually, returned) |
| evening_relax | both (7×/wk) | 19.0h | 2.0h | tablet_mara→couch_l1 (usually, left); blanket_mara→couch_l1 (usually, left); book_mara→couch_l1 (sometimes, left) |

### Activity schedule — hyp4: Mara is a freelancer home all day working at kitchen table 10:00-13:00; at 14:00 she takes a short errand (pharmacy, pos

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_coffee_brew | both (7×/wk) | 7.0h | 1.0h | mug_mara→counter_k1 (almost_always, left); water_bottle_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (sometimes, left) |
| weekend_yoga_session | weekend (2×/wk) | 9.0h | 1.0h | yoga_mat_mara→couch_l1 (usually, left); headphones_mara→couch_l1 (usually, returned) |
| freelance_work_block | weekday (5×/wk) | 10.0h | 3.0h | laptop_mara→kitchen_table_k1 (usually, left); notebook_mara→kitchen_table_k1 (usually, left); pen_mara→kitchen_table_k1 (usually, left); glasses_mara→kitchen_table_k1 (usually, left) |
| afternoon_errand | weekday (3×/wk) | 14.0h | 1.0h | jacket_mara→ON_PERSON (usually, returned); backpack_mara→ON_PERSON (usually, returned); phone_mara→ON_PERSON (almost_always, left); wallet_mara→ON_PERSON (almost_always, left); keys_mara→ON_PERSON (usually, returned) |
| evening_cooking | both (7×/wk) | 18.5h | 1.5h | pan_shared_1→kitchen_table_k1 (usually, left); pot_shared_1→counter_k1 (sometimes, returned); class:plate→kitchen_table_k1 (usually, left) |

### Activity schedule — hyp5: Mara is a homebody who stays in all day with no regular outings; daytime is lounging on couch with tablet and blanket; e

| activity | days | start | length | moves |
|---|---|---|---|---|
| morning_routine | both (7×/wk) | 6.5h | 1.0h | mug_mara→kitchen_table_k1 (usually, left); phone_mara→kitchen_table_k1 (usually, left); charger_mara→kitchen_table_k1 (usually, left) |
| daytime_home_chill | both (7×/wk) | 9.0h | 6.0h | tablet_mara→coffee_table_l1 (almost_always, left); blanket_mara→couch_l1 (usually, left); book_mara→couch_l1 (sometimes, left) |
| weekend_brunch_out | weekend (1×/wk) | 11.0h | 2.0h | keys_mara→OUT_OF_HOUSE (usually, returned); phone_mara→OUT_OF_HOUSE (almost_always, returned); wallet_mara→OUT_OF_HOUSE (almost_always, returned); jacket_mara→OUT_OF_HOUSE (usually, returned) |
| sunday_cleaning | weekend (1×/wk) | 14.0h | 2.0h | vacuum_cleaner_shared_1→bedroom_floor_b1 (usually, returned); laundry_basket_mara→bedroom_floor_b1 (usually, left); blanket_mara→bed_b1 (sometimes, returned) |
| evening_wind_down | both (7×/wk) | 19.0h | 2.0h | phone_mara→nightstand_b1 (usually, left); book_mara→couch_l1 (usually, left); glasses_mara→couch_l1 (sometimes, left) |

### Per object — truth in the first column, each hypothesis beside it

| object | TRUTH | hyp1 | hyp2 | hyp3 | hyp4 | hyp5 |
|---|---|---|---|---|---|---|
| backpack_mara | home **entry_hook_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE<br>after: meal_prep→chair_k1(0.5), work_away→entry_hook_e1(0.8), gym→entry_hook_e1(0.8) | rest entry_hook_e1 | rest entry_hook_e1<br>weekend_outing→ON_PERSON (usua,ret) | rest entry_hook_e1<br>afternoon_shift→ON_PERSON (usua,ret) | rest entry_hook_e1<br>afternoon_errand→ON_PERSON (usua,ret) | rest entry_hook_e1 |
| blanket_mara | home **couch_l1**<br>during: watch_tv→couch_l1, relax→couch_l1<br>after: watch_tv→couch_l1(0.8), relax→couch_l1(0.8) | rest couch_l1 | rest couch_l1<br>evening_relax→couch_l1 (usua,lef) | rest couch_l1<br>evening_relax→couch_l1 (usua,lef) | rest couch_l1 | rest couch_l1<br>daytime_home_chill→couch_l1 (usua,lef)<br>sunday_cleaning→bed_b1 (some,ret) |
| book_mara | home **bookshelf_l1**<br>during: walk→OUT_OF_HOUSE<br>after: reading→couch_l1(0.6), walk→couch_l1(0.7) | rest bookshelf_l1 | rest bookshelf_l1 | rest bookshelf_l1<br>evening_relax→couch_l1 (some,lef) | rest bookshelf_l1 | rest bookshelf_l1<br>daytime_home_chill→couch_l1 (some,lef)<br>evening_wind_down→couch_l1 (usua,lef) |
| bowl_shared_1 | home **entry_table_e1**<br>during: tidy_up→kitchen_table_k1<br>after: tidy_up→entry_table_e1(0.9), snack→entry_table_e1(0.2) | rest entry_table_e1<br>evening_dinner→kitchen_table_k1 (usua,lef) | rest entry_table_e1 | rest entry_table_e1 | rest entry_table_e1 | rest entry_table_e1 |
| bowl_shared_2 | home **cupboard_k1**<br>during: breakfast→kitchen_table_k1, put_away_dishes→dish_rack_k1<br>after: breakfast→kitchen_table_k1(0.5), put_away_dishes→cupboard_k1(0.8) | rest sink_k1<br>evening_dinner→kitchen_table_k1 (usua,lef) | rest sink_k1 | rest sink_k1 | rest sink_k1 | rest sink_k1 |
| charger_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: work_away→kitchen_table_k1(0.7), work_home→kitchen_table_k1(0.9) | rest kitchen_table_k1 | rest kitchen_table_k1<br>morning_coffee→kitchen_table_k1 (some,lef) | rest kitchen_table_k1 | rest kitchen_table_k1<br>morning_coffee_brew→kitchen_table_k1 (some,lef) | rest kitchen_table_k1<br>morning_routine→kitchen_table_k1 (usua,lef) |
| glasses_mara | home **kitchen_table_k1**<br>during: reading→couch_l1, work_home→kitchen_table_k1<br>after: reading→coffee_table_l1(0.5), work_home→kitchen_table_k1(0.8) | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>freelance_work_block→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>evening_wind_down→couch_l1 (some,lef) |
| hairbrush_mara | home **bathroom_shelf_ba1**<br>during: get_ready→bathroom_shelf_ba1, bedtime_routine→bathroom_shelf_ba1<br>after: get_ready→bathroom_shelf_ba1(0.8), bedtime_routine→bathroom_shelf_ba1(0.6) | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 |
| headphones_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: work_away→kitchen_table_k1(0.8), video_call→coffee_table_l1(0.6) | rest entry_hook_e1 | rest entry_hook_e1 | rest entry_hook_e1 | rest entry_hook_e1<br>weekend_yoga_session→couch_l1 (usua,ret) | rest entry_hook_e1 |
| jacket_mara | home **entry_hook_e1**<br>during: work_away→OUT_OF_HOUSE, walk→OUT_OF_HOUSE<br>after: work_away→entry_hook_e1(0.7), walk→entry_hook_e1(0.7) | rest entry_hook_e1<br>morning_walk→OUT_OF_HOUSE (usua,ret) | rest entry_hook_e1<br>weekend_outing→OUT_OF_HOUSE (usua,ret) | rest entry_hook_e1<br>afternoon_shift→OUT_OF_HOUSE (usua,ret) | rest entry_hook_e1<br>afternoon_errand→ON_PERSON (usua,ret) | rest entry_hook_e1<br>weekend_brunch_out→OUT_OF_HOUSE (usua,ret) |
| keys_mara | home **entry_table_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE<br>after: tidy_up→entry_table_e1(0.9), work_away→entry_table_e1(0.8) | rest entry_table_e1 | rest entry_table_e1<br>weekend_outing→OUT_OF_HOUSE (usua,ret) | rest entry_table_e1<br>weekend_grocery→OUT_OF_HOUSE (usua,ret) | rest entry_table_e1<br>afternoon_errand→ON_PERSON (usua,ret) | rest entry_table_e1<br>weekend_brunch_out→OUT_OF_HOUSE (usua,ret) |
| laptop_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: tidy_up→kitchen_table_k1(0.8), work_away→kitchen_table_k1(0.9), work_home→kitchen_table_k1(0.9) | rest kitchen_table_k1<br>afternoon_admin→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 | rest kitchen_table_k1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>freelance_work_block→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 |
| laundry_basket_mara | home **bedroom_floor_b1**<br>after: deep_clean→bedroom_floor_b1(0.2), laundry→bedroom_floor_b1(0.8) | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1<br>sunday_cleaning→bedroom_floor_b1 (usua,lef) |
| lunchbox_mara | home **counter_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: work_away→sink_k1(0.6), wash_dishes→counter_k1(0.8) | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 |
| makeup_kit_mara | home **bathroom_shelf_ba1**<br>during: appointment→OUT_OF_HOUSE<br>after: get_ready→bathroom_shelf_ba1(0.8), appointment→bathroom_shelf_ba1(0.8) | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1 |
| medication_bottle_mara | home **bathroom_shelf_ba1**<br>during: take_medication→bathroom_shelf_ba1, bedtime_routine→bathroom_shelf_ba1<br>after: take_medication→bathroom_shelf_ba1(0.7), bedtime_routine→bathroom_shelf_ba1(0.6) | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 | rest bathroom_shelf_ba1 |
| mug_mara | home **cupboard_k1**<br>during: coffee→counter_k1, wash_dishes→sink_k1, reading→couch_l1<br>after: coffee→counter_k1(0.6), wash_dishes→dish_rack_k1(0.7), reading→coffee_table_l1(0.6) | rest counter_k1<br>morning_prep→counter_k1 (usua,lef)<br>afternoon_admin→kitchen_table_k1 (some,lef) | rest counter_k1<br>wfh_work_block→coffee_table_l1 (usua,lef)<br>morning_coffee→kitchen_table_k1 (usua,lef) | rest counter_k1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest counter_k1<br>morning_coffee_brew→counter_k1 (almo,lef) | rest counter_k1<br>morning_routine→kitchen_table_k1 (usua,lef) |
| mug_shared_1 | home **cupboard_k1**<br>during: put_away_dishes→dish_rack_k1, socialise_home→couch_l1<br>after: put_away_dishes→cupboard_k1(0.8), socialise_home→coffee_table_l1(0.5) | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 |
| notebook_mara | home **kitchen_table_k1**<br>during: work_away→OUT_OF_HOUSE<br>after: work_away→kitchen_table_k1(0.9), work_home→kitchen_table_k1(0.9) | rest kitchen_table_k1<br>afternoon_admin→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 | rest kitchen_table_k1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1<br>freelance_work_block→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 |
| pan_shared_1 | home **cupboard_k1**<br>during: breakfast→kitchen_table_k1, dinner→kitchen_table_k1<br>after: breakfast→counter_k1(0.4), dinner→sink_k1(0.4) | rest kitchen_table_k1<br>evening_dinner→kitchen_table_k1 (usua,ret) | rest kitchen_table_k1 | rest kitchen_table_k1 | rest kitchen_table_k1<br>evening_cooking→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 |
| pen_mara | home **kitchen_table_k1**<br>during: meal_prep→counter_k1, tidy_up→kitchen_table_k1<br>after: meal_prep→kitchen_table_k1(0.6), tidy_up→kitchen_table_k1(0.7) | rest counter_k1<br>afternoon_admin→kitchen_table_k1 (usua,lef) | rest counter_k1 | rest counter_k1<br>morning_study_work→kitchen_table_k1 (usua,lef) | rest counter_k1<br>freelance_work_block→kitchen_table_k1 (usua,lef) | rest counter_k1 |
| phone_mara | home **nightstand_b1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE<br>after: wake_up→nightstand_b1(0.8), work_away→kitchen_table_k1(0.5), phone_time→couch_l1(0.5) | rest nightstand_b1 | rest nightstand_b1<br>weekend_outing→OUT_OF_HOUSE (almo,ret) | rest nightstand_b1<br>afternoon_shift→OUT_OF_HOUSE (almo,ret)<br>weekend_grocery→OUT_OF_HOUSE (almo,ret) | rest nightstand_b1<br>afternoon_errand→ON_PERSON (almo,lef) | rest nightstand_b1<br>morning_routine→kitchen_table_k1 (usua,lef)<br>evening_wind_down→nightstand_b1 (usua,lef)<br>weekend_brunch_out→OUT_OF_HOUSE (almo,ret) |
| plate_shared_1 | home **cupboard_k1**<br>during: dinner→kitchen_table_k1, wash_dishes→sink_k1<br>after: dinner→kitchen_table_k1(0.5), wash_dishes→dish_rack_k1(0.8) | rest sink_k1<br>evening_dinner→kitchen_table_k1 (usua,lef) | rest sink_k1 | rest sink_k1 | rest sink_k1<br>evening_cooking→kitchen_table_k1 (usua,lef) | rest sink_k1 |
| plate_shared_2 | home **cupboard_k1**<br>during: meal_prep→counter_k1, lunch→kitchen_table_k1<br>after: meal_prep→counter_k1(0.6), work_away→kitchen_table_k1(0.5), lunch→kitchen_table_k1(0.5) | rest counter_k1<br>evening_dinner→kitchen_table_k1 (usua,lef) | rest counter_k1 | rest counter_k1 | rest counter_k1<br>evening_cooking→kitchen_table_k1 (usua,lef) | rest counter_k1 |
| pot_shared_1 | home **cupboard_k1**<br>during: wash_dishes→sink_k1, batch_cooking→counter_k1<br>after: wash_dishes→dish_rack_k1(0.5), batch_cooking→sink_k1(0.6) | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1<br>evening_cooking→counter_k1 (some,ret) | rest cupboard_k1 |
| remote_shared_1 | home **coffee_table_l1**<br>during: watch_tv→couch_l1, deep_clean→couch_l1<br>after: watch_tv→couch_l1(0.5), deep_clean→coffee_table_l1(0.5) | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 | rest cupboard_k1 |
| suitcase_mara | home **bedroom_floor_b1**<br>during: appointment→OUT_OF_HOUSE<br>after: appointment→bedroom_floor_b1(0.7) | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 |
| tablet_mara | home **coffee_table_l1**<br>after: batch_cooking→counter_k1(0.7), video_call→coffee_table_l1(0.7) | rest coffee_table_l1 | rest coffee_table_l1<br>wfh_work_block→coffee_table_l1 (almo,lef)<br>evening_relax→couch_l1 (usua,lef) | rest coffee_table_l1<br>evening_relax→couch_l1 (usua,lef) | rest coffee_table_l1 | rest coffee_table_l1<br>daytime_home_chill→coffee_table_l1 (almo,lef) |
| towel_mara | home **towel_rack_ba1**<br>after: shower→towel_rack_ba1(0.8), laundry→bedroom_floor_b1(0.4) | rest towel_rack_ba1 | rest towel_rack_ba1 | rest towel_rack_ba1 | rest towel_rack_ba1 | rest towel_rack_ba1 |
| umbrella_mara | home **entry_floor_e1**<br>after: tidy_up→entry_floor_e1(0.7) | rest entry_floor_e1 | rest entry_floor_e1 | rest entry_floor_e1 | rest entry_floor_e1 | rest entry_floor_e1 |
| vacuum_cleaner_shared_1 | home **bedroom_floor_b1**<br>during: deep_clean→couch_l1<br>after: deep_clean→bedroom_floor_b1(0.7) | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1 | rest bedroom_floor_b1<br>sunday_cleaning→bedroom_floor_b1 (usua,ret) |
| wallet_mara | home **entry_table_e1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE, appointment→OUT_OF_HOUSE, walk→OUT_OF_HOUSE<br>after: work_away→entry_table_e1(0.8), appointment→entry_table_e1(0.7) | rest entry_table_e1 | rest entry_table_e1 | rest entry_table_e1<br>afternoon_shift→OUT_OF_HOUSE (almo,ret)<br>weekend_grocery→OUT_OF_HOUSE (almo,ret) | rest entry_table_e1<br>afternoon_errand→ON_PERSON (almo,lef) | rest entry_table_e1<br>weekend_brunch_out→OUT_OF_HOUSE (almo,ret) |
| water_bottle_mara | home **counter_k1**<br>during: work_away→OUT_OF_HOUSE, gym→OUT_OF_HOUSE<br>after: work_away→kitchen_table_k1(0.6), gym→couch_l1(0.5), bedtime_routine→nightstand_b1(0.6) | rest kitchen_table_k1<br>morning_walk→OUT_OF_HOUSE (usua,ret)<br>morning_prep→counter_k1 (usua,lef)<br>weekend_yoga→couch_l1 (usua,ret) | rest kitchen_table_k1<br>wfh_work_block→coffee_table_l1 (usua,lef) | rest kitchen_table_k1<br>afternoon_shift→OUT_OF_HOUSE (usua,ret)<br>weekend_yoga→couch_l1 (usua,ret) | rest kitchen_table_k1<br>morning_coffee_brew→kitchen_table_k1 (usua,lef) | rest kitchen_table_k1 |
| watering_can_mara | home **sink_k1**<br>during: pet_care→counter_k1<br>after: deep_clean→sink_k1(0.2), pet_care→sink_k1(0.7) | rest sink_k1 | rest sink_k1 | rest sink_k1 | rest sink_k1 | rest sink_k1 |
| yoga_mat_mara | home **couch_l1**<br>during: gym→OUT_OF_HOUSE<br>after: tidy_up→couch_l1(0.6), gym→couch_l1(0.8) | rest couch_l1<br>weekend_yoga→couch_l1 (usua,lef) | rest couch_l1 | rest couch_l1<br>weekend_yoga→couch_l1 (usua,lef) | rest couch_l1<br>weekend_yoga_session→couch_l1 (usua,lef) | rest couch_l1 |

### Scorecard (exact joins only)

| hypothesis | objects mentioned | stated rest = true home | moves whose destination the truth ever uses | true carry-out objects it sends OUT_OF_HOUSE | objects it sends OUT that never leave | weekday-only activities |
|---|---|---|---|---|---|---|
| hyp1 | 35/35 | 24/35 | 14/15 | 2/15 | 0 | 3/5 (truth: 3) |
| hyp2 | 35/35 | 24/35 | 7/11 | 3/15 | 0 | 1/4 (truth: 3) |
| hyp3 | 35/35 | 24/35 | 15/18 | 5/15 | 0 | 2/5 (truth: 3) |
| hyp4 | 35/35 | 24/35 | 12/18 | 0/15 | 0 | 2/5 (truth: 3) |
| hyp5 | 35/35 | 24/35 | 14/16 | 4/15 | 0 | 0/5 (truth: 3) |

Truth: 15 objects leave the house during weekday work (backpack_mara, book_mara, charger_mara, headphones_mara, jacket_mara, keys_mara, laptop_mara, lunchbox_mara, makeup_kit_mara, notebook_mara, phone_mara, suitcase_mara, wallet_mara, water_bottle_mara, yoga_mat_mara).

## Prediction provenance (share of object-days)

| set | panel | activity rule | stated rest | tour only | statistical fallback | never sighted |
|---|---|---|---|---|---|---|
| fixed | hyp1 | 6% | 26% | 2% | 64% | 1% |
| fixed | hyp2 | 4% | 30% | 2% | 63% | 1% |
| fixed | hyp3 | 0% | 34% | 2% | 62% | 1% |
| fixed | hyp4 | 0% | 37% | 2% | 59% | 1% |
| fixed | hyp5 | 6% | 34% | 2% | 56% | 1% |
| fixed | mixture leader | 0% | 4% | 2% | 92% | 1% |
| re-asking | hyp1 | 4% | 55% | 2% | 38% | 1% |
| re-asking | hyp2 | 2% | 55% | 2% | 39% | 1% |
| re-asking | hyp3 | 0% | 58% | 2% | 39% | 1% |
| re-asking | hyp4 | 0% | 58% | 2% | 38% | 1% |
| re-asking | hyp5 | 5% | 56% | 2% | 36% | 1% |
| re-asking | mixture leader | 0% | 4% | 2% | 92% | 1% |

Figures: provenance__tour_named__fixed.png, provenance__tour_named__reask.png
