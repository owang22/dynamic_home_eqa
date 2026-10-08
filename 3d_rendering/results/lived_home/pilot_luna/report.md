# Pilot report

## 1. Cost, calls, rejected actions

- days lived: 7 complete
- model calls: 366 (cache hits 12), cost $0.92
  - act: 354 calls, $0.89; prompt tokens median 12439 max 13943; output median 1162 (reasoning 394); 12 s median
  - plan: 12 calls, $0.03; prompt tokens median 6135 max 6320; output median 1691 (reasoning 278); 19 s median
- answers that failed a check and were retried: 0
- actions carried out: 3424; rejected: 70 (2.0% of attempted)
- steps within a room the engine filled in (picked up from another spot in the room): 696
- rejected by verb: {'pick_up': 44, 'put_down': 22, 'wear': 1, 'pocket': 1, 'say': 2}
- rejection reasons: You are not holding X. (21); Your hands are full (X, X). (20); You do not see X (yours) anywhere you can reach in the X; you last saw (6); You do not see X anywhere you can reach in the dining; you last saw it (3); You are already holding X. (3); You do not see X (yours) anywhere you can reach in the living; you las (3); X is not at X. There you see: X, X, X. (2); X is with Daniel. (1)
- put_down relations used: {'on': 656, 'in': 127, 'on_top_of': 11, 'default': 11, 'next_to': 43, 'under': 1}; put down out of sight: 170
- put into a bag or basket: 14
- times someone left home: 9; carrying: daniel d1 06:30: repair_bag_black_canvas, lunch_container_black_snap_lid, work_trousers_khaki_straight_leg, underwear_gray_cotton_pair, socks_charcoal_ankle_pair, work_shirt_blue_cotton_plaid, work_belt_brown_leather, work_boots_brown_leather, multimeter_yellow_digital, screwdriver_set_assorted_handles, replacement_fuses_clear_plastic_case, flashlight_black_led, work_gloves_gray_rubberized, tape_measure_yellow_black, truck_keys_silver_ring; mara d1 07:47: reading_glasses_tortoiseshell_frames, underwear_blue_cotton_pair, bra_beige_cotton, work_trousers_charcoal_straight_leg, work_blouse_cream_button_front, socks_cream_wool_pair, work_flats_black_leather, work_blazer_navy_tailored, work_backpack_charcoal_padded, transit_badge_clear_clipped, phone_black_glass, wallet_brown_leather, keys_brass_house, work_laptop_silver_compact, planner_green_spiral, pen_black_gel, transit_map_folder_blue_expanding; daniel d2 06:32: repair_bag_black_canvas, lunch_container_black_snap_lid, underwear_gray_cotton_pair, socks_charcoal_ankle_pair, work_trousers_navy_utility, work_shirt_gray_polo, work_belt_brown_leather, multimeter_yellow_digital, screwdriver_set_assorted_handles, replacement_fuses_clear_plastic_case, flashlight_black_led, work_gloves_gray_rubberized, tape_measure_yellow_black, wallet_black_nylon; mara d2 07:45: bra_beige_cotton, underwear_blue_cotton_pair, work_trousers_charcoal_straight_leg, work_blouse_cream_button_front, socks_cream_wool_pair, work_blazer_navy_tailored, work_flats_black_leather, transit_badge_clear_clipped, work_backpack_charcoal_padded, phone_black_glass, wallet_brown_leather, keys_brass_house, work_laptop_silver_compact, planner_green_spiral, pen_black_gel, transit_map_folder_blue_expanding; mara d3 07:46: work_blouse_cream_button_front, work_trousers_charcoal_straight_leg, socks_cream_wool_pair, work_flats_black_leather, work_blazer_navy_tailored, transit_badge_clear_clipped, work_backpack_charcoal_padded, wallet_brown_leather, work_laptop_silver_compact, planner_green_spiral, pen_black_gel, transit_map_folder_blue_expanding; mara d4 07:20: underwear_blue_cotton_pair, bra_beige_cotton, leggings_black_stretch, work_blouse_cream_button_front, work_trousers_charcoal_straight_leg, work_blazer_navy_tailored, work_flats_black_leather, transit_badge_clear_clipped, work_backpack_charcoal_padded, wallet_brown_leather, work_laptop_silver_compact, planner_green_spiral, pen_black_gel, transit_map_folder_blue_expanding, headphones_black_over_ear; mara d5 07:46: underwear_blue_cotton_pair, bra_beige_cotton, work_trousers_charcoal_straight_leg, work_blouse_cream_button_front, work_flats_black_leather, transit_badge_clear_clipped, work_backpack_charcoal_padded, phone_black_glass, wallet_brown_leather, keys_brass_house, work_laptop_silver_compact, headphones_black_over_ear; mara d6 10:47: tote_bag_canvas_blue, underwear_blue_cotton_pair, bra_beige_cotton, leggings_black_stretch, socks_cream_wool_pair, hoodie_gray_zip_fleece, walking_shoes_gray_mesh, grocery_list_white_handwritten, sunglasses_brown_tortoiseshell, phone_black_glass; daniel d7 10:18: repair_bag_black_canvas, sleep_pants_charcoal_drawstring, sleep_shirt_charcoal_cotton, socks_charcoal_ankle_pair, underwear_gray_cotton_pair, work_trousers_navy_utility, work_shirt_gray_polo, work_belt_brown_leather, work_keys_brass_tagged, work_boots_brown_leather, jacket_olive_quilted, work_gloves_gray_rubberized, multimeter_yellow_digital, replacement_fuses_clear_plastic_case, flashlight_black_led, tape_measure_yellow_black, water_bottle_steel_silver_screw_top, phone_dark_blue_glass, wallet_black_nylon
- interruptions (a resident's actions stopped and they were asked again): 104 ({'speech': 99, 'disturbance': 5}); long activities cut short: 37
- essentials missing when leaving the house: daniel d1 06:30: phone, wallet; mara d1 07:47: none missing; daniel d2 06:32: phone, keys; mara d2 07:45: none missing; mara d3 07:46: phone, keys; mara d4 07:20: phone, keys; mara d5 07:46: none missing; mara d6 10:47: keys, wallet; daniel d7 10:18: none missing
- day 1 at night, wearing: daniel: sleep_shirt_charcoal_cotton, sleep_pants_charcoal_drawstring, sleep_mask_navy_cotton
- day 2 at night, wearing: nobody wears anything
- day 3 at night, wearing: daniel: sleep_shirt_charcoal_cotton, sleep_pants_charcoal_drawstring
- day 4 at night, wearing: daniel: sleep_shirt_charcoal_cotton, sleep_pants_charcoal_drawstring; mara: pajama_top_navy_cotton, pajama_bottoms_navy_cotton
- day 5 at night, wearing: nobody wears anything
- day 6 at night, wearing: daniel: sleep_shirt_charcoal_cotton, sleep_pants_charcoal_drawstring
- day 7 at night, wearing: nobody wears anything

## 2. Object types: instances moved, and where each instance ended each day

Learnable objects end up in a few places, not one and not many. Columns: start, then the end of each day. * marks a day it moved.

Types: 197; with any instance moved: 108; objects moved at least once: 139 of 272

### plate: 4 of 4 instances moved
- plate_white_scalloped: dining_table_center | dining_table_center | kitchen_drying_mat* | kitchen_drying_mat* | kitchen_sink_basin (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_sink_basin (hidden)*  (4 distinct end places)
- plate_white_blue_rimmed: kitchen_upper_cabinet_right | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_dishwasher_interior (hidden)* | dining_table_left_end*  (3 distinct end places)
- plate_plain_cream: kitchen_upper_cabinet_right | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_dishwasher_interior (hidden)* | kitchen_drying_mat*  (3 distinct end places)
- plate_green_botanical: kitchen_upper_cabinet_right | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_dishwasher_interior (hidden)* | dining_table_center*  (3 distinct end places)

### spoon: 4 of 4 instances moved
- spoon_rounded_silver: kitchen_drawer_top | kitchen_drawer_top (hidden) | kitchen_drawer_top (hidden) | kitchen_drying_mat* | kitchen_sink_basin (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden) | kitchen_dishwasher_interior (hidden)  (4 distinct end places)
- spoon_slim_handle: kitchen_drawer_top | kitchen_drawer_top (hidden) | kitchen_drawer_top (hidden) | kitchen_counter_prep_area* | kitchen_sink_basin (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden) | kitchen_dishwasher_interior (hidden)  (4 distinct end places)
- spoon_heavy_handle: kitchen_drawer_top | kitchen_drawer_top (hidden) | kitchen_drawer_top (hidden) | kitchen_drawer_top (hidden) | kitchen_drawer_top (hidden) | kitchen_drawer_top (hidden) | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden)*  (2 distinct end places)
- spoon_small_oval_bowl: kitchen_drawer_top | kitchen_drawer_top (hidden) | kitchen_drawer_top (hidden) | kitchen_drawer_top (hidden) | kitchen_drawer_top (hidden) | kitchen_drawer_top (hidden) | kitchen_sink_basin (hidden)* | kitchen_dishwasher_interior (hidden)*  (3 distinct end places)

### bowl: 3 of 3 instances moved
- bowl_gray_stoneware: kitchen_upper_cabinet_right | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_drying_mat* | kitchen_sink_basin (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden)*  (4 distinct end places)
- bowl_blue_ceramic: living_coffee_table_right | living_coffee_table_right | living_coffee_table_right | living_coffee_table_right | kitchen_sink_basin (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_sink_basin (hidden)* | kitchen_sink_basin (hidden)*  (3 distinct end places)
- bowl_cream_striped: kitchen_upper_cabinet_right | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | kitchen_upper_cabinet_right (hidden) | main_bedroom_bed_right_side* | main_bedroom_bed_right_side  (2 distinct end places)

### fork: 3 of 3 instances moved
- fork_four_tine_steel: dining_table_center | dining_table_center* | dining_table_center* | kitchen_drying_mat* | kitchen_sink_basin (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden)* | dining_table_left_end*  (5 distinct end places)
- fork_four_tine_silver: kitchen_drawer_top | dining_table_center* | dining_table_center* | kitchen_drying_mat* | kitchen_sink_basin (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden) | dining_table_center*  (4 distinct end places)
- fork_four_tine_brushed: kitchen_drawer_top | kitchen_drawer_top (hidden) | kitchen_drawer_top (hidden) | dining_table_right_end* | kitchen_sink_basin (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden) | kitchen_sink_basin (hidden)*  (4 distinct end places)

### mug: 3 of 7 instances moved
- mug_blue_ceramic: kitchen_island_center | kitchen_counter_left_end* | kitchen_island_center* | main_bedroom_nightstand_right_top* | kitchen_island_center* | kitchen_island_center* | kitchen_sink_basin (hidden)* | dining_table_center*  (5 distinct end places)
- mug_red_enamel: living_coffee_table_right | living_coffee_table_right | living_coffee_table_right | living_coffee_table_right | living_coffee_table_right | living_coffee_table_right | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden)  (2 distinct end places)
- mug_black_matte: dining_table_right_end | dining_table_right_end | dining_table_right_end | dining_table_right_end | dining_table_right_end | dining_table_right_end | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden)  (2 distinct end places)

### reading glasses: 3 of 3 instances moved
- reading_glasses_tortoiseshell_frames: main_bedroom_nightstand_left_top | bathroom_vanity_right_counter* | bathroom_vanity_right_counter | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top*  (2 distinct end places)
- reading_glasses_clear_amber_frames: main_bedroom_nightstand_left_lower_shelf | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top* | kitchen_island_center* | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top | main_bedroom_nightstand_left_top | main_bedroom_nightstand_left_top  (2 distinct end places)
- reading_glasses_blue_frames: living_side_table_top | living_side_table_top | living_side_table_top | living_side_table_top | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top | main_bedroom_nightstand_left_top | main_bedroom_nightstand_left_top  (2 distinct end places)

### socks: 3 of 5 instances moved
- socks_cream_wool_pair: main_bedroom_dresser_drawer_bottom_left | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot | main_bedroom_bed_foot | main_bedroom_bed_foot* | main_bedroom_bed_foot*  (1 distinct end places)
- socks_charcoal_ankle_pair: main_bedroom_dresser_drawer_top_right | main_bedroom_bed_foot* | laundry_hamper_inside (hidden)* | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | main_bedroom_bed_foot*  (2 distinct end places)
- socks_navy_ankle_pair: laundry_drying_rack | laundry_drying_rack | laundry_drying_rack | laundry_drying_rack | laundry_drying_rack | laundry_drying_rack | main_bedroom_dresser_drawer_top_left (hidden)* | main_bedroom_dresser_drawer_top_left (hidden)  (2 distinct end places)

### water bottle: 3 of 3 instances moved
- water_bottle_clear_reusable: kitchen_counter_right_of_sink | kitchen_counter_right_of_sink* | kitchen_counter_right_of_sink | kitchen_counter_right_of_sink | living_coffee_table_right* | living_sofa_right_arm* | living_coffee_table_right* | main_bedroom_bed_right_side*  (4 distinct end places)
- water_bottle_steel_silver_screw_top: main_bedroom_bed_right_side | main_bedroom_bed_right_side | main_bedroom_bed_right_side | main_bedroom_nightstand_right_top* | main_bedroom_nightstand_right_top* | main_bedroom_nightstand_right_top* | main_bedroom_nightstand_right_top* | garage_shelf_left_middle (hidden)*  (3 distinct end places)
- water_bottle_clear_teal: kitchen_island_right_end | kitchen_island_right_end | kitchen_island_right_end | bathroom_vanity_right_counter* | dining_table_center* | dining_table_center | bedroom_two_bed_right_side* | dining_table_center*  (4 distinct end places)

### work trousers: 3 of 3 instances moved
- work_trousers_charcoal_straight_leg: main_bedroom_closet_left_rod | main_bedroom_bed_foot* | main_bedroom_closet_left_rod (hidden)* | bedroom_two_bed_foot* | main_bedroom_bed_foot* | bedroom_two_closet_floor (hidden)* | bedroom_two_closet_floor (hidden) | bedroom_two_closet_floor (hidden)  (4 distinct end places)
- work_trousers_navy_utility: laundry_hamper_inside | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden)* | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden)*  (1 distinct end places)
- work_trousers_khaki_straight_leg: main_bedroom_closet_right_rod | laundry_hamper_inside (hidden)* | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden)  (1 distinct end places)

### cardigan: 2 of 2 instances moved
- cardigan_rust_knit: main_bedroom_dresser_top_left | main_bedroom_dresser_top_left | main_bedroom_bed_foot* | main_bedroom_bed_foot | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_closet_right_rod (hidden)* | main_bedroom_closet_right_rod (hidden)  (3 distinct end places)
- cardigan_cream_cotton_knit: laundry_drying_rack | laundry_drying_rack | laundry_drying_rack | laundry_drying_rack | laundry_drying_rack | laundry_drying_rack | main_bedroom_closet_right_rod (hidden)* | main_bedroom_closet_right_rod (hidden)  (2 distinct end places)

### glass: 2 of 3 instances moved
- glass_amber_tumbler: dining_table_right_end | dining_table_right_end | kitchen_drying_mat* | kitchen_drying_mat | kitchen_sink_basin (hidden)* | dining_table_right_end* | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden)  (4 distinct end places)
- glass_tall_clear: kitchen_upper_cabinet_left | kitchen_upper_cabinet_left (hidden) | kitchen_upper_cabinet_left (hidden) | kitchen_drying_mat* | kitchen_sink_basin (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden) | kitchen_dishwasher_interior (hidden)  (4 distinct end places)

### hoodie: 2 of 2 instances moved
- hoodie_gray_zip_fleece: bedroom_two_bed_foot | bedroom_two_bed_foot | bedroom_two_bed_foot | main_bedroom_bed_foot* | main_bedroom_bed_foot | main_bedroom_bed_foot | main_bedroom_bed_foot* | bathroom_vanity_right_counter*  (3 distinct end places)
- hoodie_navy_fleece: living_sofa_right_arm | living_sofa_right_arm | living_sofa_right_arm | living_sofa_right_arm | living_sofa_right_arm | living_sofa_right_arm | living_sofa_right_cushion* | entry_coat_hook_middle_right*  (3 distinct end places)

### kitchen dishcloth: 2 of 2 instances moved
- kitchen_dishcloth_blue_checked: kitchen_drying_mat | kitchen_drying_mat | kitchen_drying_mat | kitchen_drying_mat | kitchen_drying_mat | kitchen_drying_mat | kitchen_counter_right_end* | kitchen_counter_right_end  (2 distinct end places)
- kitchen_dishcloth_yellow_striped: kitchen_drying_mat | kitchen_drying_mat | kitchen_drying_mat | kitchen_drying_mat | kitchen_drying_mat | kitchen_drying_mat | kitchen_counter_right_end* | kitchen_counter_right_end  (2 distinct end places)

### pen: 2 of 4 instances moved
- pen_black_gel: inside work_backpack_charcoal_padded | bedroom_two_desk_top_left (hidden) | bedroom_two_desk_top_left (hidden) | bedroom_two_desk_top_left (hidden) | bedroom_two_desk_top_right* | bedroom_two_desk_top_right | kitchen_island_left_end* | dining_table_center*  (4 distinct end places)
- pen_red_ballpoint: living_coffee_table_center | living_coffee_table_center | living_coffee_table_center | living_coffee_table_center | living_coffee_table_center | living_coffee_table_center | living_media_console_top_left* | living_coffee_table_left*  (3 distinct end places)

### phone: 2 of 2 instances moved
- phone_black_glass: main_bedroom_nightstand_left_top | main_bedroom_bed_foot (hidden)* | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top*  (2 distinct end places)
- phone_dark_blue_glass: main_bedroom_nightstand_right_top | main_bedroom_nightstand_right_top* | main_bedroom_nightstand_right_top* | living_side_table_top* | main_bedroom_nightstand_right_top* | main_bedroom_nightstand_right_top* | main_bedroom_nightstand_right_top* | main_bedroom_bed_right_side*  (3 distinct end places)

### phone charger: 2 of 9 instances moved
- phone_charger_white_braided: main_bedroom_nightstand_left_top | main_bedroom_nightstand_left_top | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top | main_bedroom_nightstand_left_top*  (1 distinct end places)
- phone_charger_green_braided_usb_c: entry_console_top | entry_console_top | entry_console_right_drawer (hidden)* | entry_console_right_drawer (hidden) | entry_console_right_drawer (hidden) | entry_console_right_drawer (hidden) | entry_console_right_drawer (hidden) | entry_console_right_drawer (hidden)  (2 distinct end places)

### toothbrush: 2 of 2 instances moved
- toothbrush_navy_medium_bristle: inside toothbrush_cup_white_ceramic_blue_stripe | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter*  (1 distinct end places)
- toothbrush_teal_soft_bristle: inside toothbrush_cup_white_ceramic_blue_stripe | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter  (1 distinct end places)

### underwear: 2 of 4 instances moved
- underwear_blue_cotton_pair: bedroom_two_closet_upper_shelf | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot*  (1 distinct end places)
- underwear_gray_cotton_pair: main_bedroom_dresser_drawer_bottom_right | main_bedroom_bed_foot* | laundry_hamper_inside (hidden)* | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | main_bedroom_bed_foot*  (2 distinct end places)

### wallet: 2 of 2 instances moved
- wallet_brown_leather: main_bedroom_nightstand_right_drawer | main_bedroom_dresser_top_left* | main_bedroom_closet_left_rod (hidden)* | bedroom_two_bed_foot (hidden) | main_bedroom_bed_foot (hidden) | bedroom_two_closet_floor (hidden) | bedroom_two_closet_floor (hidden) | bedroom_two_closet_floor (hidden)  (5 distinct end places)
- wallet_black_nylon: inside work_trousers_navy_utility | laundry_hamper_inside (hidden) | main_bedroom_nightstand_right_drawer (hidden)* | main_bedroom_nightstand_right_drawer (hidden) | main_bedroom_nightstand_right_drawer (hidden) | main_bedroom_nightstand_right_drawer (hidden) | main_bedroom_nightstand_right_drawer (hidden) | main_bedroom_nightstand_right_drawer (hidden)*  (2 distinct end places)

### work shirt: 2 of 2 instances moved
- work_shirt_gray_polo: laundry_hamper_inside | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden)* | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden)*  (1 distinct end places)
- work_shirt_blue_cotton_plaid: main_bedroom_closet_right_rod | laundry_hamper_inside (hidden)* | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden)  (1 distinct end places)

### allergy tablets: 1 of 1 instances moved
- allergy_tablets_white_labeled_bottle: bathroom_medicine_lower_shelf | bathroom_medicine_lower_shelf (hidden)* | bathroom_medicine_lower_shelf (hidden)* | bathroom_vanity_right_counter* | bathroom_vanity_right_counter* | bathroom_vanity_right_counter* | bathroom_vanity_right_counter* | bathroom_vanity_right_counter*  (2 distinct end places)

### apple: 1 of 1 instances moved
- apple_red_gala: inside fruit_bowl_shallow_white | kitchen_counter_prep_area | kitchen_counter_prep_area | kitchen_counter_prep_area | kitchen_counter_prep_area | kitchen_counter_prep_area | living_coffee_table_right* | dining_table_center*  (3 distinct end places)

### banana: 1 of 1 instances moved
- banana_small_ripe_bunch: inside fruit_bowl_shallow_white | kitchen_counter_prep_area | kitchen_counter_prep_area | main_bedroom_nightstand_right_top* | bedroom_three_bed_foot* | main_bedroom_bed_right_side* | dining_table_center* | dining_table_center*  (5 distinct end places)

### bath towel: 1 of 1 instances moved
- bath_towel_white_waffle_weave: bathroom_tub_edge | bathroom_towel_hook* | bathroom_towel_hook* | bathroom_towel_hook | bathroom_towel_hook* | bathroom_towel_hook | bedroom_two_bed_foot* | bathroom_towel_hook*  (2 distinct end places)

### body wash: 1 of 1 instances moved
- body_wash_blue_translucent_bottle: bathroom_shower_caddy | bathroom_shower_caddy* | bathroom_shower_caddy* | bathroom_shower_caddy | bathroom_shower_caddy* | bathroom_shower_caddy | bathroom_shower_caddy | bathroom_shower_caddy  (1 distinct end places)

### bra: 1 of 1 instances moved
- bra_beige_cotton: main_bedroom_dresser_drawer_top_left | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot*  (1 distinct end places)

### chef knife: 1 of 1 instances moved
- chef_knife_black_handle: kitchen_drawer_second | kitchen_drawer_second (hidden) | kitchen_drawer_second (hidden) | kitchen_drawer_second (hidden) | kitchen_drawer_second (hidden) | kitchen_drawer_second (hidden) | kitchen_drawer_second (hidden) | kitchen_drawer_top (hidden)*  (2 distinct end places)

### cleaning rag: 1 of 1 instances moved
- cleaning_rag_blue_cotton_square: garage_shelf_right_bottom | garage_shelf_right_bottom | garage_shelf_right_bottom | garage_shelf_right_bottom | garage_shelf_right_bottom | garage_shelf_right_bottom | kitchen_counter_right_of_sink* | kitchen_counter_prep_area*  (3 distinct end places)

### cleaning sponge: 1 of 1 instances moved
- cleaning_sponge_yellow_scrub: garage_shelf_right_bottom | garage_shelf_right_bottom | garage_shelf_right_bottom | garage_shelf_right_bottom | garage_shelf_right_bottom | garage_shelf_right_bottom | garage_shelf_right_bottom | kitchen_counter_right_of_sink*  (2 distinct end places)

### cleaning spray: 1 of 1 instances moved
- cleaning_spray_green_trigger: laundry_upper_cabinet_left | laundry_upper_cabinet_left (hidden) | laundry_upper_cabinet_left (hidden) | laundry_upper_cabinet_left (hidden) | laundry_upper_cabinet_left (hidden) | laundry_upper_cabinet_left (hidden) | kitchen_counter_right_of_sink* | kitchen_lower_cabinet_right (hidden)*  (3 distinct end places)

### coaster: 1 of 1 instances moved
- coaster_cork_round: living_coffee_table_center | living_coffee_table_center | living_coffee_table_center | living_coffee_table_center | living_coffee_table_center | living_coffee_table_center | living_coffee_table_right* | living_coffee_table_right  (2 distinct end places)

### cold medicine: 1 of 1 instances moved
- cold_medicine_amber_orange_cap: bathroom_medicine_lower_shelf | bathroom_medicine_lower_shelf (hidden) | bathroom_medicine_lower_shelf (hidden) | bathroom_vanity_right_counter* | bathroom_vanity_right_counter* | bathroom_vanity_right_counter* | bathroom_vanity_right_counter* | bathroom_vanity_right_counter*  (2 distinct end places)

### crossword book: 1 of 1 instances moved
- crossword_book_yellow_pocket: dining_sideboard_top_left | dining_sideboard_top_left | dining_sideboard_top_left | dining_sideboard_top_left | dining_sideboard_top_left | dining_sideboard_top_left | dining_sideboard_top_left | dining_table_center*  (2 distinct end places)

### cutting board: 1 of 1 instances moved
- cutting_board_rectangular_bamboo: kitchen_counter_prep_area | kitchen_counter_prep_area | kitchen_counter_prep_area | kitchen_counter_prep_area | kitchen_lower_cabinet_left (hidden)* | kitchen_lower_cabinet_left (hidden) | kitchen_counter_prep_area* | kitchen_counter_left_of_sink*  (3 distinct end places)

### deodorant: 1 of 1 instances moved
- deodorant_white_twist_stick: bathroom_vanity_right_counter | bathroom_vanity_right_counter | bathroom_vanity_right_counter* | bathroom_vanity_right_counter | bathroom_vanity_right_counter | bathroom_vanity_right_counter | bathroom_vanity_right_counter | bathroom_vanity_right_counter  (1 distinct end places)

### evening t-shirt: 1 of 1 instances moved
- evening_t_shirt_faded_red: main_bedroom_bed_foot | main_bedroom_bed_foot* | main_bedroom_bed_foot* | laundry_hamper_inside (hidden)* | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden)*  (2 distinct end places)

### face moisturizer: 1 of 1 instances moved
- face_moisturizer_small_pink_pump: bathroom_vanity_right_counter | bathroom_vanity_right_counter* | bathroom_vanity_right_counter | bathroom_vanity_right_counter* | bathroom_vanity_right_counter | bathroom_vanity_right_counter | bathroom_vanity_right_counter* | bathroom_vanity_right_counter  (1 distinct end places)

### fruit bowl: 1 of 1 instances moved
- fruit_bowl_shallow_white: kitchen_counter_prep_area | kitchen_counter_prep_area | kitchen_counter_prep_area | kitchen_counter_prep_area | kitchen_counter_prep_area | kitchen_counter_prep_area | dining_table_center* | dining_table_center  (2 distinct end places)

### frying pan: 1 of 1 instances moved
- frying_pan_black_cast_iron: kitchen_lower_cabinet_right | kitchen_stovetop_front_left_burner* | kitchen_stovetop_front_left_burner | kitchen_stovetop_front_left_burner | kitchen_stovetop_front_left_burner | kitchen_stovetop_front_left_burner | kitchen_counter_prep_area* | kitchen_oven_interior (hidden)*  (3 distinct end places)

### grocery list: 1 of 1 instances moved
- grocery_list_white_handwritten: kitchen_fridge_door_bins | kitchen_fridge_door_bins (hidden) | kitchen_fridge_door_bins (hidden)* | kitchen_fridge_door_bins (hidden) | kitchen_fridge_door_bins (hidden) | kitchen_fridge_door_bins (hidden) | entry_console_lower_shelf (hidden)* | entry_console_lower_shelf (hidden)  (2 distinct end places)

### hand towel: 1 of 1 instances moved
- hand_towel_blue_striped: bathroom_towel_hook | bathroom_towel_hook | bathroom_towel_hook | bathroom_towel_hook | bathroom_towel_hook | bathroom_towel_hook | bathroom_towel_hook | laundry_counter_left*  (2 distinct end places)

### headphones: 1 of 1 instances moved
- headphones_black_over_ear: bedroom_two_desk_top_right | bedroom_two_desk_top_right | bedroom_two_desk_top_right | bedroom_two_desk_top_right | bedroom_two_desk_top_left* | bedroom_two_desk_top_left (hidden)* | bedroom_two_desk_top_left (hidden) | bedroom_two_desk_top_left (hidden)  (2 distinct end places)

### jacket: 1 of 1 instances moved
- jacket_olive_quilted: entry_coat_hook_left | entry_coat_hook_left | entry_coat_hook_left | entry_coat_hook_left | entry_coat_hook_left | entry_coat_hook_left | entry_coat_hook_left | entry_coat_hook_right*  (2 distinct end places)

### jeans: 1 of 3 instances moved
- jeans_dark_blue_relaxed: main_bedroom_bed_foot | main_bedroom_bed_foot* | main_bedroom_bed_foot | main_bedroom_bed_foot | main_bedroom_bed_foot | main_bedroom_bed_foot | main_bedroom_bed_foot | main_bedroom_bed_foot  (1 distinct end places)

### kettle: 1 of 1 instances moved
- kettle_black_electric: kitchen_counter_left_end | kitchen_counter_left_end* | kitchen_counter_left_end* | kitchen_counter_left_end | kitchen_sink_basin (hidden)* | kitchen_counter_right_of_sink* | kitchen_counter_prep_area* | kitchen_counter_prep_area*  (4 distinct end places)

### keys: 1 of 1 instances moved
- keys_brass_house: entry_console_left_drawer | main_bedroom_bed_foot (hidden)* | entry_console_left_drawer (hidden)* | entry_console_left_drawer (hidden) | entry_console_left_drawer (hidden) | bedroom_two_closet_floor (hidden)* | bedroom_two_closet_floor (hidden) | bedroom_two_closet_floor (hidden)  (3 distinct end places)

### laundry detergent: 1 of 1 instances moved
- laundry_detergent_white_blue_pour: laundry_counter_left | laundry_counter_left | laundry_counter_left | laundry_counter_left | laundry_counter_left | laundry_counter_left | laundry_washer_top* | laundry_washer_top  (2 distinct end places)

### leggings: 1 of 1 instances moved
- leggings_black_stretch: main_bedroom_dresser_top_left | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | bathroom_vanity_right_counter*  (2 distinct end places)

### library book: 1 of 2 instances moved
- library_book_red_paperback: living_side_table_top | living_side_table_top | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top* | living_coffee_table_right* | living_bookshelf_lower_shelf* | living_coffee_table_left*  (5 distinct end places)

### lounge shorts: 1 of 1 instances moved
- lounge_shorts_blue_plaid: main_bedroom_bed_foot | main_bedroom_bed_foot | main_bedroom_bed_foot* | laundry_hamper_inside (hidden)* | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden)*  (2 distinct end places)

### lunch container: 1 of 1 instances moved
- lunch_container_black_snap_lid: entry_shoe_rack_top | entry_console_top* | dining_table_center* | kitchen_drying_mat* | kitchen_sink_basin (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden) | kitchen_dishwasher_interior (hidden)  (5 distinct end places)

### magazine: 1 of 1 instances moved
- magazine_home_repair: living_coffee_table_right | living_coffee_table_right | living_coffee_table_right | living_coffee_table_right | living_coffee_table_right | living_coffee_table_right | living_media_console_top_right* | living_media_console_top_right  (2 distinct end places)

### mail stack: 1 of 1 instances moved
- mail_stack_neat_white: dining_table_left_end | dining_table_left_end* | dining_table_left_end* | dining_table_left_end | dining_table_left_end | dining_table_left_end | dining_table_left_end | dining_table_left_end  (1 distinct end places)

### mixing bowl: 1 of 1 instances moved
- mixing_bowl_large_stainless: kitchen_lower_cabinet_left | kitchen_lower_cabinet_left (hidden) | kitchen_lower_cabinet_left (hidden) | kitchen_lower_cabinet_left (hidden) | kitchen_lower_cabinet_left (hidden) | kitchen_lower_cabinet_left (hidden) | kitchen_lower_cabinet_left (hidden) | kitchen_fridge_lower_shelf (hidden)*  (2 distinct end places)

### napkin: 1 of 1 instances moved
- napkin_blue_cotton: dining_table_center | dining_table_center | dining_table_center | dining_table_center | kitchen_counter_prep_area* | laundry_hamper_inside (hidden)* | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden)  (3 distinct end places)

### newspaper: 1 of 1 instances moved
- newspaper_folded_local: dining_table_left_end | living_sofa_middle_cushion* | living_coffee_table_right* | living_coffee_table_right | living_coffee_table_right | living_coffee_table_right | dining_sideboard_top_right* | dining_sideboard_top_right  (3 distinct end places)

### notebook: 1 of 3 instances moved
- notebook_blue_graph_cover: bedroom_two_desk_drawer_bottom | bedroom_two_desk_drawer_bottom (hidden) | bedroom_two_desk_drawer_bottom (hidden) | bedroom_two_desk_drawer_bottom (hidden) | bedroom_two_desk_top_right* | bedroom_two_desk_top_right | bedroom_two_desk_top_right | bedroom_two_desk_top_right  (2 distinct end places)

### olive oil: 1 of 1 instances moved
- olive_oil_amber_glass_bottle: kitchen_counter_left_of_stove | kitchen_counter_left_of_stove | kitchen_counter_left_of_stove | kitchen_counter_left_of_stove | kitchen_counter_left_of_stove | kitchen_counter_prep_area* | kitchen_counter_right_of_sink* | kitchen_pantry_lower_shelf (hidden)*  (4 distinct end places)

### pajama bottoms: 1 of 1 instances moved
- pajama_bottoms_navy_cotton: inside None | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | with mara* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot*  (2 distinct end places)

### pajama top: 1 of 1 instances moved
- pajama_top_navy_cotton: inside None | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | with mara* | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot*  (2 distinct end places)

### paperback: 1 of 3 instances moved
- paperback_blue_mystery: living_coffee_table_center | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top | main_bedroom_nightstand_left_top | main_bedroom_nightstand_left_top | main_bedroom_nightstand_left_top* | main_bedroom_bed_right_side* | main_bedroom_bed_right_side*  (2 distinct end places)

### paring knife: 1 of 1 instances moved
- paring_knife_green_handle: kitchen_drawer_second | kitchen_drawer_second (hidden) | kitchen_drawer_second (hidden) | kitchen_drawer_second (hidden) | kitchen_drawer_second (hidden) | kitchen_drawer_second (hidden) | kitchen_drawer_second (hidden) | kitchen_drawer_top (hidden)*  (2 distinct end places)

### pasta: 1 of 1 instances moved
- pasta_spiral_whole_wheat: kitchen_pantry_middle_shelf | dining_table_center* | dining_table_center | kitchen_pantry_middle_shelf (hidden)* | kitchen_pantry_middle_shelf (hidden) | kitchen_counter_prep_area* | kitchen_counter_prep_area* | kitchen_fridge_lower_shelf (hidden)*  (4 distinct end places)

### planner: 1 of 1 instances moved
- planner_green_spiral: inside work_backpack_charcoal_padded | bedroom_two_desk_top_left (hidden) | bedroom_two_desk_top_left (hidden) | bedroom_two_desk_top_left (hidden) | bedroom_two_desk_top_right* | bedroom_two_desk_top_right | kitchen_island_left_end* | dining_table_center*  (4 distinct end places)

### pocket notebook: 1 of 1 instances moved
- pocket_notebook_black_spiral: kitchen_counter_right_of_sink | kitchen_counter_right_end* | dining_sideboard_top_right* | dining_sideboard_top_right | dining_sideboard_top_right | dining_sideboard_top_right | dining_sideboard_top_right | living_coffee_table_center*  (3 distinct end places)

### prescription bottle: 1 of 1 instances moved
- prescription_bottle_amber_labeled: bathroom_medicine_lower_shelf | bathroom_medicine_lower_shelf (hidden) | bathroom_medicine_lower_shelf (hidden) | bathroom_medicine_lower_shelf (hidden)* | bathroom_medicine_lower_shelf (hidden)* | bathroom_medicine_lower_shelf (hidden)* | bathroom_medicine_lower_shelf (hidden)* | bathroom_medicine_lower_shelf (hidden)*  (1 distinct end places)

### quilt: 1 of 1 instances moved
- quilt_blue_patchwork: bedroom_three_bed_foot | bedroom_three_bed_foot | bedroom_three_bed_foot | bedroom_three_bed_foot | bedroom_three_bed_foot | main_bedroom_bed_right_side* | main_bedroom_bed_right_side | main_bedroom_bed_right_side  (2 distinct end places)

### razor: 1 of 1 instances moved
- razor_black_pivot_handle: bathroom_tub_edge | bathroom_tub_edge | bathroom_tub_edge* | bathroom_tub_edge | bathroom_tub_edge | bathroom_tub_edge | bathroom_tub_edge | bathroom_tub_edge  (1 distinct end places)

### receipt: 1 of 1 instances moved
- receipt_long_grocery: living_side_table_top | living_side_table_top | living_side_table_top | living_side_table_top | living_side_table_top | living_side_table_top | dining_table_left_end* | living_coffee_table_left*  (3 distinct end places)

### remote control: 1 of 1 instances moved
- remote_control_black_rubber: inside tray_bamboo_square | living_coffee_table_center* | living_coffee_table_center* | living_coffee_table_center* | living_coffee_table_center* | living_sofa_middle_cushion* | living_side_table_top* | living_side_table_top  (3 distinct end places)

### repair bag: 1 of 1 instances moved
- repair_bag_black_canvas: laundry_counter_center | entry_console_top* | main_bedroom_bed_left_side* | main_bedroom_bed_left_side | main_bedroom_bed_left_side | main_bedroom_bed_left_side | bedroom_two_desk_top_left* | garage_shelf_left_middle*  (4 distinct end places)

### salt grinder: 1 of 1 instances moved
- salt_grinder_clear_wooden_top: kitchen_counter_right_end | kitchen_counter_right_end | kitchen_counter_right_end | kitchen_counter_right_end | kitchen_counter_right_end | kitchen_counter_right_end | kitchen_counter_right_end* | kitchen_counter_right_end  (1 distinct end places)

### saucepan: 1 of 1 instances moved
- saucepan_small_steel_with_lid: kitchen_lower_cabinet_right | dining_table_center* | dining_table_center | kitchen_stovetop_front_left_burner* | kitchen_stovetop_front_left_burner | kitchen_lower_cabinet_right (hidden)* | kitchen_stovetop_front_left_burner* | dining_table_center*  (3 distinct end places)

### screwdriver set: 1 of 1 instances moved
- screwdriver_set_assorted_handles: inside repair_bag_black_canvas | living_media_console_top_right* | living_media_console_top_right* | living_media_console_top_right | living_media_console_top_right | living_media_console_top_right | living_media_console_top_right | living_media_console_top_right  (1 distinct end places)

### shampoo: 1 of 1 instances moved
- shampoo_amber_pump_bottle: bathroom_shower_caddy | bathroom_shower_caddy* | bathroom_shower_caddy | bathroom_shower_caddy | bathroom_shower_caddy | bathroom_shower_caddy | bathroom_shower_caddy | bathroom_shower_caddy  (1 distinct end places)

### shaving cream: 1 of 1 instances moved
- shaving_cream_white_aerosol_can: bathroom_tub_edge | bathroom_tub_edge | bathroom_tub_edge* | bathroom_tub_edge | bathroom_tub_edge | bathroom_tub_edge | bathroom_tub_edge | bathroom_tub_edge  (1 distinct end places)

### sheet set: 1 of 1 instances moved
- sheet_set_white_cotton_queen: main_bedroom_closet_upper_shelf | main_bedroom_closet_upper_shelf (hidden) | main_bedroom_closet_upper_shelf (hidden) | main_bedroom_closet_upper_shelf (hidden) | main_bedroom_closet_upper_shelf (hidden) | main_bedroom_closet_upper_shelf (hidden) | bedroom_two_bed_foot* | bedroom_two_bed_left_side*  (3 distinct end places)

### sleep mask: 1 of 1 instances moved
- sleep_mask_navy_cotton: main_bedroom_bed_right_side | with daniel* | main_bedroom_bed_right_side* | main_bedroom_bed_right_side | main_bedroom_nightstand_right_top* | main_bedroom_nightstand_right_top | main_bedroom_nightstand_right_top | main_bedroom_nightstand_right_top  (3 distinct end places)

### sleep pants: 1 of 1 instances moved
- sleep_pants_charcoal_drawstring: inside None | with daniel* | laundry_hamper_inside (hidden)* | with daniel* | with daniel | main_bedroom_bed_foot* | with daniel* | main_bedroom_bed_foot*  (3 distinct end places)

### sleep shirt: 1 of 1 instances moved
- sleep_shirt_charcoal_cotton: inside None | with daniel* | laundry_hamper_inside (hidden)* | with daniel* | with daniel | main_bedroom_bed_foot* | with daniel* | main_bedroom_bed_foot*  (3 distinct end places)

### t-shirt: 1 of 2 instances moved
- t_shirt_gray_soft_cotton: laundry_dryer_drum | laundry_dryer_drum (hidden) | laundry_dryer_drum (hidden) | laundry_dryer_drum (hidden) | laundry_dryer_drum (hidden) | laundry_dryer_drum (hidden) | bedroom_three_dresser_drawer_two (hidden)* | bedroom_three_dresser_drawer_two (hidden)  (2 distinct end places)

### tape measure: 1 of 1 instances moved
- tape_measure_yellow_black: living_media_console_top_right | entry_console_top (hidden)* | main_bedroom_bed_left_side (hidden) | main_bedroom_bed_left_side (hidden) | main_bedroom_bed_left_side (hidden) | main_bedroom_bed_left_side (hidden) | bedroom_two_desk_top_left (hidden) | garage_shelf_left_middle (hidden)  (4 distinct end places)

### tea mug: 1 of 1 instances moved
- tea_mug_cream_blue_rimmed: main_bedroom_nightstand_left_top | main_bedroom_nightstand_left_top | living_coffee_table_right* | kitchen_drying_mat* | kitchen_sink_basin (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden)* | kitchen_dishwasher_interior (hidden)*  (5 distinct end places)

### tea tin: 1 of 1 instances moved
- tea_tin_green_square: kitchen_pantry_middle_shelf | kitchen_pantry_middle_shelf (hidden) | kitchen_counter_prep_area* | kitchen_upper_cabinet_right (hidden)* | kitchen_pantry_upper_shelf (hidden)* | kitchen_upper_cabinet_left (hidden)* | kitchen_pantry_middle_shelf (hidden)* | kitchen_pantry_middle_shelf (hidden)*  (5 distinct end places)

### thermometer: 1 of 1 instances moved
- thermometer_digital_white: bathroom_medicine_upper_shelf | bathroom_medicine_upper_shelf (hidden) | bathroom_medicine_upper_shelf (hidden) | living_side_table_top* | living_side_table_top* | living_side_table_top* | main_bedroom_nightstand_right_top* | bathroom_medicine_lower_shelf (hidden)*  (4 distinct end places)

### throw blanket: 1 of 1 instances moved
- throw_blanket_mustard_woven: living_sofa_left_cushion | living_sofa_left_cushion | living_sofa_left_cushion | living_sofa_left_cushion* | living_sofa_left_cushion* | living_sofa_middle_cushion* | living_sofa_right_arm* | living_sofa_middle_cushion*  (3 distinct end places)

### tissue box: 1 of 1 instances moved
- tissue_box_blue_floral: bathroom_vanity_left_counter | bathroom_vanity_left_counter | bathroom_vanity_left_counter | main_bedroom_nightstand_right_top* | main_bedroom_nightstand_right_top | main_bedroom_nightstand_right_top* | main_bedroom_nightstand_right_top | main_bedroom_bed_right_side*  (3 distinct end places)

### tomato sauce: 1 of 1 instances moved
- tomato_sauce_red_glass_jar: kitchen_pantry_middle_shelf | kitchen_counter_right_end* | kitchen_pantry_middle_shelf (hidden)* | kitchen_pantry_middle_shelf (hidden)* | kitchen_pantry_middle_shelf (hidden) | kitchen_counter_prep_area* | kitchen_counter_prep_area* | kitchen_pantry_middle_shelf (hidden)*  (3 distinct end places)

### toothpaste: 1 of 1 instances moved
- toothpaste_white_green_tube: bathroom_vanity_left_counter | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter* | bathroom_vanity_left_counter*  (1 distinct end places)

### tote bag: 1 of 1 instances moved
- tote_bag_canvas_blue: entry_console_top | entry_console_top | entry_console_lower_shelf* | entry_console_lower_shelf | entry_console_lower_shelf | entry_console_lower_shelf | entry_console_lower_shelf* | entry_console_lower_shelf  (2 distinct end places)

### towel: 1 of 3 instances moved
- towel_gray_hand: bathroom_towel_hook | bathroom_towel_hook | bathroom_towel_hook | bathroom_towel_hook | bathroom_towel_hook | bathroom_towel_hook | bedroom_two_bed_foot* | bedroom_two_bed_foot  (2 distinct end places)

### transit badge: 1 of 1 instances moved
- transit_badge_clear_clipped: entry_console_top | bedroom_two_desk_top_left* | main_bedroom_nightstand_left_top* | bedroom_two_bed_foot* | main_bedroom_dresser_top_right* | main_bedroom_nightstand_left_top* | main_bedroom_nightstand_left_top | main_bedroom_nightstand_left_top  (4 distinct end places)

### transit map folder: 1 of 1 instances moved
- transit_map_folder_blue_expanding: inside work_backpack_charcoal_padded | bedroom_two_desk_top_left (hidden) | bedroom_two_desk_top_left (hidden) | bedroom_two_desk_top_left (hidden) | bedroom_two_desk_top_right* | bedroom_two_desk_top_right | bedroom_two_desk_top_right | bedroom_two_desk_top_right  (2 distinct end places)

### tray: 1 of 1 instances moved
- tray_bamboo_square: living_coffee_table_left | living_coffee_table_left | living_coffee_table_left | living_coffee_table_left | living_coffee_table_left | kitchen_counter_right_of_sink* | kitchen_counter_right_of_sink | kitchen_counter_right_of_sink  (2 distinct end places)

### truck keys: 1 of 1 instances moved
- truck_keys_silver_ring: entry_coat_hook_middle_right | entry_coat_hook_middle_right* | entry_coat_hook_middle_right* | entry_coat_hook_middle_right | entry_coat_hook_middle_right | entry_coat_hook_middle_right | entry_coat_hook_middle_right | entry_coat_hook_middle_right*  (1 distinct end places)

### walking shoes: 1 of 1 instances moved
- walking_shoes_gray_mesh: main_bedroom_closet_floor_right | main_bedroom_closet_floor_right (hidden) | main_bedroom_closet_floor_right (hidden) | main_bedroom_closet_floor_right (hidden) | main_bedroom_closet_floor_right (hidden) | main_bedroom_closet_floor_right (hidden) | main_bedroom_bed_foot* | main_bedroom_bed_foot  (2 distinct end places)

### wooden spoon: 1 of 1 instances moved
- wooden_spoon_long_honey_colored: kitchen_drawer_top | kitchen_counter_right_end* | kitchen_drawer_top (hidden)* | kitchen_drawer_top (hidden) | kitchen_drawer_top (hidden) | kitchen_drawer_top (hidden) | kitchen_counter_prep_area* | dining_table_center*  (4 distinct end places)

### work backpack: 1 of 1 instances moved
- work_backpack_charcoal_padded: bedroom_two_desk_top_left | bedroom_two_desk_top_left* | bedroom_two_desk_top_left* | bedroom_two_desk_top_left* | bedroom_two_desk_top_left* | bedroom_two_desk_top_left* | bedroom_two_desk_top_left | bedroom_two_desk_top_left  (1 distinct end places)

### work belt: 1 of 1 instances moved
- work_belt_brown_leather: laundry_hamper_inside | main_bedroom_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot | main_bedroom_bed_foot | main_bedroom_bed_foot | main_bedroom_bed_foot | entry_shoe_rack_top*  (2 distinct end places)

### work blazer: 1 of 1 instances moved
- work_blazer_navy_tailored: main_bedroom_closet_left_rod | main_bedroom_closet_door_hook* | main_bedroom_closet_right_rod (hidden)* | bedroom_two_bed_foot* | main_bedroom_bed_foot* | main_bedroom_bed_foot | main_bedroom_closet_left_rod (hidden)* | main_bedroom_closet_left_rod (hidden)  (5 distinct end places)

### work blouse: 1 of 1 instances moved
- work_blouse_cream_button_front: main_bedroom_closet_left_rod | main_bedroom_bed_foot* | main_bedroom_closet_left_rod (hidden)* | bedroom_two_bed_foot* | main_bedroom_bed_foot* | bedroom_two_closet_floor (hidden)* | bedroom_two_closet_floor (hidden) | bedroom_two_closet_floor (hidden)  (4 distinct end places)

### work boots: 1 of 1 instances moved
- work_boots_brown_leather: entry_shoe_rack_lower_shelf | entry_shoe_rack_lower_shelf* | entry_shoe_rack_lower_shelf | entry_shoe_rack_lower_shelf | entry_shoe_rack_lower_shelf | entry_shoe_rack_lower_shelf | entry_shoe_rack_lower_shelf | entry_shoe_rack_lower_shelf*  (1 distinct end places)

### work flats: 1 of 1 instances moved
- work_flats_black_leather: main_bedroom_closet_floor_left | entry_shoe_rack_top* | main_bedroom_closet_floor_right (hidden)* | bedroom_two_bed_foot* | main_bedroom_bed_foot* | bedroom_two_closet_floor (hidden)* | bedroom_two_closet_floor (hidden) | bedroom_two_closet_floor (hidden)  (5 distinct end places)

### work gloves: 1 of 1 instances moved
- work_gloves_gray_rubberized: inside repair_bag_black_canvas | entry_console_top (hidden) | main_bedroom_bed_left_side (hidden) | main_bedroom_bed_left_side (hidden) | main_bedroom_bed_left_side (hidden) | main_bedroom_bed_left_side (hidden) | bedroom_two_desk_top_left (hidden) | entry_shoe_rack_top*  (4 distinct end places)

### work keys: 1 of 1 instances moved
- work_keys_brass_tagged: laundry_hamper_inside | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | laundry_hamper_inside (hidden) | entry_console_top*  (2 distinct end places)

### work laptop: 1 of 1 instances moved
- work_laptop_silver_compact: inside work_backpack_charcoal_padded | bedroom_two_desk_top_left (hidden) | bedroom_two_desk_top_left (hidden)* | bedroom_two_desk_top_left (hidden) | bedroom_two_desk_top_left* | bedroom_two_desk_top_left (hidden)* | bedroom_two_desk_top_left (hidden) | bedroom_two_desk_top_left (hidden)  (1 distinct end places)

### yoga mat: 1 of 1 instances moved
- yoga_mat_purple_rolled: main_bedroom_bed_underneath | main_bedroom_bed_underneath (hidden) | main_bedroom_bed_underneath (hidden) | living_sofa_left_arm* | living_sofa_left_arm | living_sofa_left_arm | bedroom_two_bed_underneath (hidden)* | bedroom_two_bed_underneath (hidden)  (3 distinct end places)

### yogurt: 1 of 1 instances moved
- yogurt_strawberry_four_pack: kitchen_fridge_upper_shelf | kitchen_fridge_upper_shelf (hidden) | kitchen_fridge_lower_shelf (hidden)* | kitchen_fridge_lower_shelf (hidden)* | bedroom_three_bed_foot* | main_bedroom_bed_right_side* | kitchen_counter_prep_area* | dining_table_right_end*  (6 distinct end places)

Types never moved (89): appliance manuals, appliance parts cans, batteries, bicycle pump, blouse, bookmark, camping lantern, candle, cap, cardboard box, caulk gun, charging cable, clothespins, conditioner, cookbook, cordless drill, dish soap, drill bit case, dryer sheets, duffel bag, earbuds, earplugs, eggs, extension cord, first-aid kit, flashlight, game controller, grocery bag, hair clip, hair ties, hairbrush, hand cream, hand lotion, hand soap, hardcover book, hex key set, holiday lights, jewelry dish, laundry bag, lint roller, measuring cup, measuring spoons, microfiber cloth, multimeter, painkiller, paint roller, paint tray, peanut butter, pencil, pencil case, pepper grinder, pillow, placemat, plaster box, plunger, popcorn, raincoat, replacement fuses, rice, ruler, safety goggles, sandals, sandpaper packet, scarf, scissors, screw, serving platter, sewing kit, shoehorn, shorts, sketchbook, slippers, soldering iron, spatula, stain remover, sticky notes, storage box, suitcase, sunglasses, sweater, table knife, tape, toaster, toilet paper roll, toothbrush cup, umbrella, whisk, work apron, wristwatch

## 3. Response habits: trigger present, habit followed

From each activity answer: which habits' triggers the resident said were true, and which habit they followed.

| resident | habit | how often (stated) | answers with trigger | followed | followed with trigger | followed without trigger | days followed |
|---|---|---|---|---|---|---|---|
| mara | mapstress: when When work becomes politically tense or a project deadline moves suddenly, I take a brisk twenty-minute walk around the corner lot and nearby streets before trying to talk about it. | most times | 0 of 181 | 0 | 0 | 0 | - |
| mara | teaillness: when When Daniel feels sick or has had a difficult day, I make ginger tea and put it on the right side of the living-room coffee table without asking many questions. | almost always | 46 of 181 | 29 | 29 | 0 | [3, 4, 5, 6] |
| mara | tiredfood: when When I am too tired to cook after a long meeting day, I order Thai food and eat it at the dining table while apologizing that I did not plan ahead. | sometimes | 0 of 181 | 0 | 0 | 0 | - |
| mara | clutterreset: when When the house feels visually crowded, I do a fast reset of the entry, sofa, and kitchen counters before I can relax. | most times | 23 of 181 | 18 | 18 | 0 | [2, 3, 6, 7] |
| daniel | fixstress: when When a customer cancels late or a repair call goes badly, I spend twenty or thirty minutes doing a small, definite repair in the garage rather than discussing the problem immediately. | most times | 1 of 183 | 0 | 0 | 0 | - |
| daniel | tiredtakeout: when When I get home after an overloaded route, I skip cooking, suggest sandwiches or takeout, and sit on the sofa before changing out of my work shirt. | sometimes | 1 of 183 | 0 | 0 | 0 | - |
| daniel | irritablehunger: when When I have missed lunch or been stuck in traffic, I become terse and start rummaging for food in the pantry until Mara points it out. | most times | 1 of 183 | 0 | 0 | 0 | - |
| daniel | quietcomfort: when When Mara is upset but does not want advice, I make coffee, sit nearby, and fix or sharpen something quietly instead of asking repeated questions. | almost always | 0 of 183 | 0 | 0 | 0 | - |

## 4. Sick days against normal days

Sick days: [3, 4, 5]; sick: ['daniel']

### mara (the other resident)

| day | sick day | wake | sleep | minutes out | objects moved | rooms by actions | stress | tired | mood | health |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 |  | 06:30 | 21:00 | 553 | 25 | main_bedroom 49, dining 23, bathroom 16, kitchen 14 | 0.6 | 0.8 | 2.6 | 3.0 |
| 2 |  | 06:30 | 21:35 | 585 | 37 | main_bedroom 66, kitchen 38, dining 16, entry 11 | 0.2 | 0.8 | 2.8 | 3.0 |
| 3 | yes | 06:30 | 21:30 | 644 | 39 | kitchen 61, main_bedroom 49, living 18, dining 15 | 0.6 | 1.2 | 2.1 | 3.0 |
| 4 | yes | 06:15 | 21:45 | 625 | 42 | kitchen 100, main_bedroom 43, bedroom_two 32, living 15 | 0.7 | 1.3 | 2.1 | 3.0 |
| 5 | yes | 06:15 | 21:30 | 599 | 43 | kitchen 88, main_bedroom 47, dining 20, living 18 | 0.5 | 1.2 | 2.1 | 3.0 |
| 6 |  | 07:30 | 22:30 | 74 | 72 | kitchen 141, living 79, main_bedroom 65, dining 30 | 0.6 | 1.0 | 2.8 | 3.0 |
| 7 |  | 07:30 | 21:30 | 0 | 59 | kitchen 134, dining 67, living 56, main_bedroom 49 | 0.5 | 1.0 | 2.7 | 3.0 |

Moved only on sick days: glass_tall_clear, headphones_black_over_ear, lunch_container_black_snap_lid, napkin_blue_cotton, notebook_blue_graph_cover, reading_glasses_blue_frames, spoon_rounded_silver, spoon_slim_handle, transit_map_folder_blue_expanding, tray_bamboo_square

Moved only on other days: apple_red_gala, banana_small_ripe_bunch, bath_towel_white_waffle_weave, cardigan_cream_cotton_knit, chef_knife_black_handle, cleaning_rag_blue_cotton_square, cleaning_sponge_yellow_scrub, cleaning_spray_green_trigger, coaster_cork_round, crossword_book_yellow_pocket, fruit_bowl_shallow_white, frying_pan_black_cast_iron, grocery_list_white_handwritten, hand_towel_blue_striped, hoodie_navy_fleece, jacket_olive_quilted, kitchen_dishcloth_blue_checked, kitchen_dishcloth_yellow_striped, laundry_detergent_white_blue_pour, magazine_home_repair, mail_stack_neat_white, mixing_bowl_large_stainless, mug_black_matte, mug_red_enamel, newspaper_folded_local, paring_knife_green_handle, pen_red_ballpoint, phone_charger_green_braided_usb_c, plate_green_botanical, plate_plain_cream, plate_white_blue_rimmed, pocket_notebook_black_spiral, receipt_long_grocery, repair_bag_black_canvas, salt_grinder_clear_wooden_top, sheet_set_white_cotton_queen, socks_navy_ankle_pair, spoon_heavy_handle, spoon_small_oval_bowl, t_shirt_gray_soft_cotton, throw_blanket_mustard_woven, tote_bag_canvas_blue, towel_gray_hand, walking_shoes_gray_mesh, wallet_brown_leather, water_bottle_clear_reusable, water_bottle_clear_teal, wooden_spoon_long_honey_colored, work_belt_brown_leather, work_gloves_gray_rubberized, work_keys_brass_tagged

### daniel (sick)

| day | sick day | wake | sleep | minutes out | objects moved | rooms by actions | stress | tired | mood | health |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 |  | 05:45 | 22:00 | 600 | 33 | main_bedroom 38, kitchen 23, bathroom 16, entry 15 | 0.7 | 1.0 | 2.7 | 3.0 |
| 2 |  | 05:30 | 21:45 | 598 | 28 | bathroom 36, main_bedroom 35, living 12, entry 11 | 0.2 | 0.8 | 2.8 | 3.0 |
| 3 | yes | 05:45 | 20:00 | 0 | 21 | bathroom 35, living 32, main_bedroom 30, kitchen 23 | 1.0 | 2.7 | 1.1 | 1.0 |
| 4 | yes | 06:15 | 20:30 | 0 | 21 | bathroom 35, bedroom_three 29, living 23, kitchen 18 | 0.9 | 2.9 | 1.2 | 1.0 |
| 5 | yes | 06:30 | 21:30 | 0 | 20 | main_bedroom 50, living 40, bathroom 26, dining 14 | 1.0 | 3.0 | 1.1 | 1.0 |
| 6 |  | 07:30 | 21:00 | 0 | 20 | living 58, main_bedroom 41, bathroom 30, kitchen 24 | 0.8 | 2.1 | 1.8 | 1.1 |
| 7 |  | 08:00 | 22:00 | 432 | 38 | living 50, kitchen 37, main_bedroom 30, laundry 27 | 1.3 | 1.8 | 2.3 | 1.9 |

Moved only on sick days: bowl_blue_ceramic, mug_blue_ceramic, quilt_blue_patchwork, spoon_rounded_silver, spoon_slim_handle

Moved only on other days: bowl_cream_striped, cleaning_rag_blue_cotton_square, cleaning_sponge_yellow_scrub, deodorant_white_twist_stick, fork_four_tine_silver, frying_pan_black_cast_iron, jacket_olive_quilted, jeans_dark_blue_relaxed, lunch_container_black_snap_lid, newspaper_folded_local, paperback_blue_mystery, pasta_spiral_whole_wheat, pen_red_ballpoint, plate_white_blue_rimmed, pocket_notebook_black_spiral, razor_black_pivot_handle, receipt_long_grocery, repair_bag_black_canvas, saucepan_small_steel_with_lid, screwdriver_set_assorted_handles, shampoo_amber_pump_bottle, shaving_cream_white_aerosol_can, socks_charcoal_ankle_pair, spoon_heavy_handle, spoon_small_oval_bowl, tape_measure_yellow_black, tomato_sauce_red_glass_jar, truck_keys_silver_ring, underwear_gray_cotton_pair, wallet_black_nylon, wooden_spoon_long_honey_colored, work_belt_brown_leather, work_boots_brown_leather, work_gloves_gray_rubberized, work_keys_brass_tagged, work_shirt_blue_cotton_plaid, work_shirt_gray_polo, work_trousers_khaki_straight_leg, work_trousers_navy_utility

## 5. Excerpts

See the hand-written section in the pilot write-up, chosen from replay.md.
