# Pilot report

## 1. Cost, calls, rejected actions

- days lived: 7 complete
- model calls: 509 (cache hits 4), cost $1.46
  - act: 497 calls, $1.44; prompt tokens median 17185 max 18414; output median 1245 (reasoning 404); 12 s median
  - plan: 12 calls, $0.03; prompt tokens median 7890 max 8040; output median 1804 (reasoning 268); 17 s median
- answers that failed a check and were retried: 0
- actions carried out: 4165; rejected: 140 (3.3% of attempted)
- steps within a room the engine filled in (picked up from another spot in the room): 703
- rejected by verb: {'wear': 6, 'put_down': 54, 'pick_up': 59, 'say': 13, 'pocket': 1, 'give': 7}
- rejection reasons: Your hands are full (X, X). (20); You are not holding X (yours); it is on top X. (20); Say it to whom? mara is not someone else in the household. (13); You are already holding X. (9); You are not holding X; it is on top X. (6); X is not at X; you can only put X next to something that is there. (6); You are not holding X. (5); You are not holding X; it is inside X, on top X. (5)
- put_down relations used: {'on_top': 725, 'inside': 234, 'next_to': 51, 'default': 30}; put down out of sight: 107
- put into a bag or basket: 73
- times someone left home: 8; carrying: julian d1 08:01: travel_mug_red_insulated, underwear_gray_cotton_pair, socks_navy_wool_pair, work_shirt_pale_blue_oxford, work_trousers_navy_wool, belt_brown_leather, work_shoes_black_leather, backpack_charcoal_canvas, museum_badge_white_lanyard, jacket_navy_lightweight, wallet_black_canvas, keys_silver_ring, phone_dark_green_glass, laptop_black_museum, notebook_green_grid, pen_black_rollerball, water_bottle_steel_blue; mara d1 17:45: underwear_black_cotton_pair, socks_cream_ribbed_pair, evening_leggings_black_jersey, evening_sweatshirt_faded_plum, walking_shoes_white_canvas, keys_brass_house; julian d2 08:01: underwear_gray_cotton_pair, work_shirt_white_cotton_poplin, work_trousers_gray_wool_straight_leg, work_shoes_black_leather, backpack_charcoal_canvas, jacket_navy_lightweight, museum_badge_white_lanyard, wallet_black_canvas, phone_dark_green_glass, laptop_black_museum, notebook_green_grid, pen_black_rollerball, water_bottle_steel_blue, exhibition_notes_loose_cream_pages, keys_silver_ring; mara d2 17:25: canvas_tote_bag_natural_cotton, keys_brass_house, underwear_black_cotton_pair, house_slippers_gray_felt, reading_glasses_tortoiseshell_frames, evening_leggings_black_jersey, evening_sweatshirt_faded_plum, walking_shoes_white_canvas, wallet_brown_leather; mara d4 18:03: canvas_tote_bag_natural_cotton, work_trousers_charcoal_wide_leg, socks_cream_ribbed_pair, work_blouse_cream_linen, walking_shoes_white_canvas, wallet_brown_leather, keys_brass_house; mara d5 17:47: socks_cream_ribbed_pair, walking_shoes_white_canvas, evening_leggings_black_jersey, evening_sweatshirt_faded_plum, keys_brass_house; julian d6 14:09: shopping_bag_folded_blue_nylon, hoodie_faded_charcoal_pullover, sweatpants_gray_jersey, backpack_charcoal_canvas, jacket_navy_lightweight, wallet_black_canvas, keys_silver_ring, phone_dark_green_glass, laptop_black_museum, water_bottle_steel_blue, exhibition_notes_loose_cream_pages; julian d7 08:48: work_shirt_pale_blue_oxford, work_trousers_navy_wool, belt_brown_leather, work_shoes_black_leather, museum_badge_white_lanyard, jacket_navy_lightweight, backpack_charcoal_canvas, keys_silver_ring, laptop_black_museum, notebook_green_grid, pen_black_rollerball, water_bottle_steel_blue, phone_charger_white_usb_c, headphones_black_wireless, travel_mug_red_insulated, exhibition_floor_plan_folded_blueprint, exhibition_notes_loose_cream_pages, pencil_case_olive_canvas_zippered
- interruptions (a resident's actions stopped and they were asked again): 159 ({'disturbance': 9, 'speech': 149, 'handed something': 1}); long activities cut short: 59
- essentials missing when leaving the house: julian d1 08:01: none missing; mara d1 17:45: phone, wallet; julian d2 08:01: none missing; mara d2 17:25: phone; mara d4 18:03: phone; mara d5 17:47: phone, wallet; julian d6 14:09: none missing; julian d7 08:48: phone, wallet
- day 1 at night, wearing: julian: pajama_shirt_navy_cotton, pajama_bottoms_navy_cotton, underwear_gray_cotton_pair, sleep_mask_navy_padded_cotton; mara: pajama_top_soft_blue_cotton, pajama_bottoms_soft_blue_cotton, house_slippers_gray_felt, socks_cream_ribbed_pair, underwear_black_cotton_pair
- day 2 at night, wearing: mara: pajama_top_soft_blue_cotton, pajama_bottoms_soft_blue_cotton
- day 3 at night, wearing: julian: pajama_shirt_navy_cotton, pajama_bottoms_navy_cotton; mara: pajama_top_soft_blue_cotton, pajama_bottoms_soft_blue_cotton
- day 4 at night, wearing: julian: pajama_shirt_navy_cotton, pajama_bottoms_navy_cotton; mara: pajama_top_soft_blue_cotton, pajama_bottoms_soft_blue_cotton
- day 5 at night, wearing: julian: pajama_shirt_navy_cotton, pajama_bottoms_navy_cotton; mara: pajama_top_soft_blue_cotton, pajama_bottoms_soft_blue_cotton
- day 6 at night, wearing: julian: pajama_shirt_navy_cotton, pajama_bottoms_navy_cotton; mara: pajama_top_soft_blue_cotton, pajama_bottoms_soft_blue_cotton, house_slippers_gray_felt
- day 7 at night, wearing: julian: pajama_shirt_navy_cotton, pajama_bottoms_navy_cotton, sleep_mask_navy_padded_cotton; mara: pajama_top_soft_blue_cotton, pajama_bottoms_soft_blue_cotton, house_slippers_gray_felt, sleep_mask_charcoal_linen
- day 7: home activities skipped because their time had passed: julian Put on my jacket, collect my badge and keys from the hallway tray, and leave for the museum using the revised commute. (08:50-09:00, now 12:30)

## 2. Object types: instances moved, and where each instance ended each day

Learnable objects end up in a few places, not one and not many. Columns: start, then the end of each day. * marks a day it moved.

Types: 191; with any instance moved: 112; objects moved at least once: 153 of 276

### dinner plate: 4 of 4 instances moved
- dinner_plate_cream_ceramic: kitchen_wall_cabinet_by_the_corner_upper_corner_cabinet_shelf | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_island_island_countertop* | living_room_end_table_by_the_large_sofa_top* | living_room_end_table_by_the_large_sofa_top | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (4 distinct end places)
- dinner_plate_white_blue_rim: kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf | kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf (hidden) | kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf (hidden) | kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf (hidden) | living_room_dining_table_top* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (4 distinct end places)
- dinner_plate_white_green_rim: kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf | kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf (hidden) | kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf (hidden) | kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf (hidden) | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (3 distinct end places)
- dinner_plate_cream_floral: kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf | kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf (hidden) | kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf (hidden) | kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf (hidden) | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (4 distinct end places)

### fork: 4 of 4 instances moved
- fork_four_tine_steel: kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (2 distinct end places)
- fork_short_four_tine: kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (3 distinct end places)
- fork_long_four_tine: kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin*  (2 distinct end places)
- fork_rounded_handle: kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_small_shelf_base_drawer (hidden) | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin  (2 distinct end places)

### table knife: 4 of 4 instances moved
- table_knife_serrated_steel: inside fork_four_tine_steel | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (2 distinct end places)
- table_knife_plain_rounded: kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin  (2 distinct end places)
- table_knife_black_handle: kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin  (2 distinct end places)
- table_knife_slender_serrated: kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer (hidden) | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin  (2 distinct end places)

### water bottle: 4 of 4 instances moved
- water_bottle_clear_reusable: kitchen_kitchen_island_island_countertop | kitchen_kitchen_island_island_countertop | living_room_end_table_by_the_large_sofa_top* | living_room_large_sofa_seat* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_1_nightstand_by_the_first_bedroom_bed_top* | bedroom_1_nightstand_by_the_first_bedroom_bed_top | living_room_dining_table_top*  (6 distinct end places)
- water_bottle_clear_flip_top: hallway_floor | hallway_floor | hallway_floor | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top*  (2 distinct end places)
- water_bottle_steel_blue: inside backpack_charcoal_canvas | bedroom_2_floor (hidden) | bedroom_2_floor (hidden) | bedroom_2_floor (hidden) | bedroom_2_floor (hidden) | bedroom_2_floor (hidden) | kitchen_kitchen_island_island_countertop* | bedroom_2_floor (hidden)*  (2 distinct end places)
- water_bottle_amber_glass: living_room_end_table_by_the_shelf_top | living_room_end_table_by_the_shelf_top | living_room_end_table_by_the_shelf_top | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface* | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface  (2 distinct end places)

### book: 3 of 11 instances moved
- book_face_down_blue_cover: living_room_small_shelving_unit_by_the_sofa_fourth_shelf_from_the_bottom | living_room_small_shelving_unit_by_the_sofa_fourth_shelf_from_the_bottom | bedroom_1_tall_shelf_by_the_dresser_bottom_shelf* | bedroom_1_tall_shelf_by_the_dresser_bottom_shelf* | bedroom_1_tall_shelf_by_the_dresser_bottom_shelf* | bedroom_1_nightstand_by_the_first_bedroom_bed_top* | living_room_small_shelving_unit_by_the_sofa_top_shelf* | living_room_small_shelving_unit_by_the_sofa_top_shelf*  (4 distinct end places)
- book_paperback_green_cover: living_room_small_shelving_unit_by_the_sofa_fifth_shelf_from_the_bottom | living_room_small_shelving_unit_by_the_sofa_fifth_shelf_from_the_bottom* | living_room_small_shelving_unit_by_the_sofa_fifth_shelf_from_the_bottom | living_room_large_sofa_seat* | living_room_small_shelving_unit_by_the_sofa_top_shelf* | living_room_small_shelving_unit_by_the_sofa_top_shelf* | living_room_small_shelving_unit_by_the_sofa_top_shelf | living_room_small_shelving_unit_by_the_sofa_top_shelf  (3 distinct end places)
- book_paperback_ochre_cover: bedroom_1_tall_shelf_by_the_dresser_bottom_shelf | bedroom_1_tall_shelf_by_the_dresser_bottom_shelf | bedroom_1_tall_shelf_by_the_dresser_bottom_shelf | bedroom_1_tall_shelf_by_the_dresser_bottom_shelf | bedroom_1_tall_shelf_by_the_dresser_bottom_shelf | bedroom_1_tall_shelf_by_the_dresser_bottom_shelf | bedroom_1_nightstand_by_the_first_bedroom_bed_top* | bedroom_1_nightstand_by_the_first_bedroom_bed_top  (2 distinct end places)

### drinking glass: 3 of 3 instances moved
- drinking_glass_clear_tall: kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin*  (2 distinct end places)
- drinking_glass_clear_dimpled: kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin*  (2 distinct end places)
- drinking_glass_smoked_short: kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_upper_base_cabinet_wall_shelf (hidden) | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin  (2 distinct end places)

### glass tumbler: 3 of 3 instances moved
- glass_tumbler_clear_smooth: kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top  (2 distinct end places)
- glass_tumbler_clear_ribbed: living_room_dining_table_top | living_room_dining_table_top | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (3 distinct end places)
- glass_tumbler_clear_fluted: bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop  (2 distinct end places)

### mug: 3 of 3 instances moved
- mug_cream_striped: living_room_dining_table_top | living_room_dining_table_top | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | living_room_end_table_by_the_large_sofa_top* | living_room_end_table_by_the_large_sofa_top | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (6 distinct end places)
- mug_blue_ceramic: kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | living_room_end_table_by_the_large_sofa_top* | living_room_end_table_by_the_large_sofa_top | living_room_end_table_by_the_large_sofa_top | living_room_end_table_by_the_large_sofa_top | living_room_end_table_by_the_large_sofa_top*  (3 distinct end places)
- mug_yellow_ceramic: kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf | kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf (hidden) | kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf (hidden) | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop  (2 distinct end places)

### work trousers: 3 of 3 instances moved
- work_trousers_charcoal_wide_leg: bedroom_1_dresser_in_the_first_bedroom_top | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor  (1 distinct end places)
- work_trousers_navy_wool: bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_first_stack | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden)* | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden) | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden) | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden) | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden) | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)*  (2 distinct end places)
- work_trousers_gray_wool_straight_leg: bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)  (2 distinct end places)

### bath towel: 2 of 4 instances moved
- bath_towel_sage_green_waffle: bathroom_2_bathroom_drawer_rack_by_the_shower_top_surface | bathroom_2_floor* | bathroom_2_bathroom_drawer_rack_by_the_shower_top_surface* | bedroom_2_bed_in_the_second_bedroom_mattress* | bathroom_2_floor* | bathroom_2_bathroom_drawer_rack_by_the_shower_top_surface* | bathroom_2_bathroom_drawer_rack_by_the_shower_top_surface* | bathroom_2_bathroom_drawer_rack_by_the_shower_top_surface*  (3 distinct end places)
- bath_towel_white_waffle: bathroom_1_curved_bathroom_shelf_upper_shelf | bathroom_1_curved_bathroom_shelf_upper_shelf | bathroom_1_curved_bathroom_shelf_upper_shelf | bathroom_1_curved_bathroom_shelf_upper_shelf | bathroom_1_curved_bathroom_shelf_upper_shelf | bathroom_1_curved_bathroom_shelf_upper_shelf | bedroom_1_floor* | bathroom_1_three_tier_bathroom_rack_rack_top*  (3 distinct end places)

### bed linen set: 2 of 4 instances moved
- bed_linen_set_sage_stripe_folded: bedroom_1_wardrobe_in_the_first_bedroom_inside | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_floor* | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden)*  (2 distinct end places)
- bed_linen_set_white_cotton_folded: bedroom_1_wardrobe_in_the_first_bedroom_inside | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden)* | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden)  (1 distinct end places)

### coffee mug: 2 of 3 instances moved
- coffee_mug_white_chipped: bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_1_nightstand_by_the_first_bedroom_bed_top* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface | living_room_end_table_by_the_large_sofa_top* | kitchen_kitchen_sink_cabinet_sink_basin* | living_room_dining_table_top*  (5 distinct end places)
- coffee_mug_green_speckled: living_room_end_table_by_the_large_sofa_top | living_room_end_table_by_the_large_sofa_top | living_room_end_table_by_the_large_sofa_top | kitchen_kitchen_sink_cabinet_sink_basin* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (4 distinct end places)

### envelope: 2 of 2 instances moved
- envelope_brown_kraft: living_room_dining_table_top | living_room_dining_table_top | living_room_dining_table_top | living_room_dining_table_top | living_room_dining_table_top | living_room_end_table_by_the_large_sofa_top* | living_room_end_table_by_the_large_sofa_top | living_room_end_table_by_the_large_sofa_top  (2 distinct end places)
- envelope_white_long_unopened: hallway_hallway_storage_cabinet_middle_shelf | hallway_hallway_storage_cabinet_middle_shelf | hallway_hallway_storage_cabinet_middle_shelf | hallway_hallway_storage_cabinet_middle_shelf | hallway_hallway_storage_cabinet_middle_shelf | hallway_hallway_storage_cabinet_middle_shelf | living_room_small_shelving_unit_by_the_sofa_top_shelf* | living_room_small_shelving_unit_by_the_sofa_top_shelf  (2 distinct end places)

### jeans: 2 of 2 instances moved
- jeans_midblue_relaxed_leg: bedroom_2_floor | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor* | bedroom_2_floor | bathroom_1_floor* | bedroom_1_floor*  (3 distinct end places)
- jeans_dark_indigo_straight_leg: bedroom_1_wardrobe_in_the_first_bedroom_inside | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_wardrobe_in_the_first_bedroom_inside (hidden) | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor  (2 distinct end places)

### keys: 2 of 2 instances moved
- keys_silver_ring: inside tray_shallow_walnut | hallway_hallway_storage_cabinet_middle_shelf* | living_room_dining_table_top* | living_room_dining_table_top | hallway_hallway_storage_cabinet_middle_shelf* | hallway_hallway_storage_cabinet_middle_shelf | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | hallway_hallway_storage_cabinet_middle_shelf*  (3 distinct end places)
- keys_brass_house: inside canvas_tote_bag_natural_cotton | bedroom_1_floor (hidden)* | bedroom_1_nightstand_by_the_wardrobe_top* | bedroom_1_nightstand_by_the_wardrobe_top | bedroom_1_floor (hidden)* | bedroom_1_nightstand_by_the_wardrobe_top* | bedroom_1_nightstand_by_the_wardrobe_top | bedroom_1_nightstand_by_the_wardrobe_top  (2 distinct end places)

### laptop: 2 of 2 instances moved
- laptop_silver_compact: inside canvas_tote_bag_natural_cotton | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_second_desk_drawer (hidden)* | bedroom_1_bed_in_the_first_bedroom_mattress* | bedroom_2_desk_in_the_second_bedroom_desk_surface*  (3 distinct end places)
- laptop_black_museum: inside backpack_charcoal_canvas | bedroom_2_floor (hidden)* | bedroom_2_floor (hidden) | bedroom_2_floor (hidden) | bedroom_2_floor (hidden) | bedroom_2_floor (hidden) | bedroom_2_floor (hidden) | bedroom_2_floor (hidden)  (1 distinct end places)

### notebook: 2 of 2 instances moved
- notebook_red_ruled: inside canvas_tote_bag_natural_cotton | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden)* | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden) | living_room_dining_table_top*  (3 distinct end places)
- notebook_green_grid: inside backpack_charcoal_canvas | bedroom_2_floor (hidden) | bedroom_2_floor (hidden) | bedroom_2_bed_in_the_second_bedroom_mattress* | bedroom_2_bed_in_the_second_bedroom_mattress* | bedroom_2_bed_in_the_second_bedroom_mattress* | bedroom_2_bed_in_the_second_bedroom_mattress | living_room_dining_table_top*  (3 distinct end places)

### pajama bottoms: 2 of 2 instances moved
- pajama_bottoms_soft_blue_cotton: inside None | with mara* | with mara* | with mara* | with mara* | with mara* | with mara* | with mara*  (1 distinct end places)
- pajama_bottoms_navy_cotton: inside None | with julian* | bedroom_2_floor* | with julian* | with julian* | with julian* | with julian* | with julian*  (2 distinct end places)

### pen: 2 of 2 instances moved
- pen_blue_gel: inside pen_case_black_zippered | bedroom_2_desk_in_the_second_bedroom_desk_surface (hidden) | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden)* | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden) | kitchen_kitchen_island_island_countertop*  (3 distinct end places)
- pen_black_rollerball: inside backpack_charcoal_canvas | bedroom_2_floor (hidden) | bedroom_2_floor (hidden) | bedroom_2_bed_in_the_second_bedroom_mattress* | bedroom_2_bed_in_the_second_bedroom_mattress* | bedroom_2_bed_in_the_second_bedroom_mattress* | bedroom_2_bed_in_the_second_bedroom_mattress | living_room_dining_table_top*  (3 distinct end places)

### phone: 2 of 2 instances moved
- phone_black_glass: bedroom_1_nightstand_by_the_wardrobe_top | bedroom_1_nightstand_by_the_wardrobe_top* | bedroom_1_nightstand_by_the_wardrobe_top* | bedroom_1_nightstand_by_the_wardrobe_top* | bedroom_1_nightstand_by_the_wardrobe_top* | bedroom_1_nightstand_by_the_wardrobe_top* | bedroom_1_nightstand_by_the_wardrobe_top* | bedroom_1_nightstand_by_the_wardrobe_top*  (1 distinct end places)
- phone_dark_green_glass: bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top*  (2 distinct end places)

### phone charger: 2 of 6 instances moved
- phone_charger_white_braided: bedroom_1_nightstand_by_the_wardrobe_top | bedroom_1_nightstand_by_the_wardrobe_top | bedroom_1_nightstand_by_the_wardrobe_top | bedroom_1_nightstand_by_the_wardrobe_top | bedroom_1_nightstand_by_the_wardrobe_top* | bedroom_1_nightstand_by_the_wardrobe_top | bedroom_1_nightstand_by_the_wardrobe_top | bedroom_1_nightstand_by_the_wardrobe_top  (1 distinct end places)
- phone_charger_white_usb_c: bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_floor (hidden)*  (2 distinct end places)

### reading glasses: 2 of 3 instances moved
- reading_glasses_tortoiseshell_frames: bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top* | bathroom_1_double_bathroom_sink_cabinet_countertop* | bedroom_1_nightstand_by_the_first_bedroom_bed_top* | bedroom_1_nightstand_by_the_first_bedroom_bed_top* | bedroom_1_nightstand_by_the_first_bedroom_bed_top* | bedroom_1_nightstand_by_the_first_bedroom_bed_top* | living_room_small_sofa_seat (hidden)*  (3 distinct end places)
- reading_glasses_thin_gold_frames: inside reading_glasses_case_blue_canvas | living_room_end_table_by_the_large_sofa_top (hidden) | bedroom_1_nightstand_by_the_first_bedroom_bed_top* | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top* | bedroom_1_nightstand_by_the_first_bedroom_bed_top*  (2 distinct end places)

### receipt: 2 of 2 instances moved
- receipt_long_thermal_paper: living_room_small_shelving_unit_by_the_sofa_fifth_shelf_from_the_bottom | living_room_small_shelving_unit_by_the_sofa_fifth_shelf_from_the_bottom* | living_room_small_shelving_unit_by_the_sofa_fourth_shelf_from_the_bottom* | living_room_large_sofa_seat* | living_room_small_shelving_unit_by_the_sofa_top_shelf | living_room_small_shelving_unit_by_the_sofa_top_shelf | living_room_small_shelving_unit_by_the_sofa_top_shelf | living_room_small_shelving_unit_by_the_sofa_top_shelf  (4 distinct end places)
- receipt_small_white_thermal: bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface | living_room_small_shelving_unit_by_the_sofa_top_shelf* | living_room_small_shelving_unit_by_the_sofa_top_shelf  (2 distinct end places)

### sleep mask: 2 of 2 instances moved
- sleep_mask_navy_padded_cotton: bedroom_2_nightstand_by_the_second_bedroom_bed_top | with julian* | bedroom_2_floor* | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor | with julian*  (2 distinct end places)
- sleep_mask_charcoal_linen: bedroom_1_nightstand_by_the_first_bedroom_bed_lower_drawer | bedroom_1_nightstand_by_the_first_bedroom_bed_lower_drawer (hidden) | bedroom_1_nightstand_by_the_first_bedroom_bed_lower_drawer (hidden) | bedroom_1_nightstand_by_the_first_bedroom_bed_lower_drawer (hidden) | bedroom_1_nightstand_by_the_first_bedroom_bed_lower_drawer (hidden) | bedroom_1_nightstand_by_the_first_bedroom_bed_lower_drawer (hidden) | bedroom_1_nightstand_by_the_first_bedroom_bed_lower_drawer (hidden) | with mara*  (2 distinct end places)

### socks: 2 of 2 instances moved
- socks_cream_ribbed_pair: bedroom_1_dresser_in_the_first_bedroom_lower_drawer | with mara* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor | bedroom_1_floor  (2 distinct end places)
- socks_navy_wool_pair: bedroom_2_large_bedroom_storage_cabinet_lowest_drawer_in_the_first_stack | bedroom_2_floor* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)  (2 distinct end places)

### toothbrush: 2 of 2 instances moved
- toothbrush_teal_soft_bristle: inside toothbrush_holder_clear_ribbed_cup | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface* | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface* | toilet_bathroom_drawer_cabinet_by_the_sink_smaller_top_surface* | bathroom_1_double_bathroom_sink_cabinet_countertop* | bathroom_1_double_bathroom_sink_cabinet_countertop* | bathroom_1_double_bathroom_sink_cabinet_countertop  (3 distinct end places)
- toothbrush_navy_medium_bristle: inside toothbrush_holder_clear_ribbed_cup | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface* | toilet_bathroom_drawer_cabinet_by_the_sink_smaller_top_surface* | bathroom_2_shower_room_sink_cabinet_sink_basin* | bathroom_2_shower_room_sink_cabinet_sink_basin* | bathroom_2_shower_room_sink_cabinet_sink_basin*  (3 distinct end places)

### underwear: 2 of 2 instances moved
- underwear_black_cotton_pair: bedroom_1_dresser_in_the_first_bedroom_lower_drawer | with mara* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor | bedroom_1_floor | bedroom_1_floor | bedroom_1_floor  (2 distinct end places)
- underwear_gray_cotton_pair: bedroom_2_large_bedroom_storage_cabinet_lowest_drawer_in_the_first_stack | with julian* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)  (2 distinct end places)

### work shirt: 2 of 2 instances moved
- work_shirt_pale_blue_oxford: bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_first_stack | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden)* | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden) | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden) | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden) | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden) | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)*  (2 distinct end places)
- work_shirt_white_cotton_poplin: bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack | bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_second_stack (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)  (2 distinct end places)

### adhesive tape: 1 of 1 instances moved
- adhesive_tape_clear_dispenser: bedroom_2_desk_in_the_second_bedroom_first_desk_drawer | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden) | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden) | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden) | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden) | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden) | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden) | kitchen_kitchen_island_island_countertop*  (2 distinct end places)

### apron: 1 of 1 instances moved
- apron_striped_linen: kitchen_kitchen_island_lower_island_shelf | bedroom_2_floor* | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor  (1 distinct end places)

### art catalog: 1 of 1 instances moved
- art_catalog_large_cream_cover: living_room_tall_bookcase_by_the_tv_third_shelf_from_the_bottom | living_room_tall_bookcase_by_the_tv_third_shelf_from_the_bottom | living_room_tall_bookcase_by_the_tv_third_shelf_from_the_bottom | living_room_tall_bookcase_by_the_tv_third_shelf_from_the_bottom | living_room_tall_bookcase_by_the_tv_third_shelf_from_the_bottom | living_room_tall_bookcase_by_the_tv_third_shelf_from_the_bottom | living_room_tall_bookcase_by_the_tv_third_shelf_from_the_bottom | living_room_large_sofa_seat*  (2 distinct end places)

### backpack: 1 of 1 instances moved
- backpack_charcoal_canvas: bedroom_2_floor | bedroom_2_floor* | bedroom_2_floor* | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor* | bedroom_2_floor*  (1 distinct end places)

### banana: 1 of 1 instances moved
- banana_yellow_bunch: kitchen_kitchen_island_island_countertop | kitchen_kitchen_island_island_countertop | kitchen_corner_kitchen_counter_corner_countertop* | kitchen_corner_kitchen_counter_corner_countertop | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_island_island_countertop*  (4 distinct end places)

### bathrobe: 1 of 1 instances moved
- bathrobe_charcoal_cotton: bathroom_2_floor | bedroom_2_bed_in_the_second_bedroom_mattress* | bedroom_2_bed_in_the_second_bedroom_mattress | bedroom_2_bed_in_the_second_bedroom_mattress* | bedroom_2_floor* | bedroom_2_floor* | bedroom_2_floor* | bedroom_2_floor  (2 distinct end places)

### belt: 1 of 1 instances moved
- belt_brown_leather: bedroom_2_large_bedroom_storage_cabinet_second_drawer_in_the_first_stack | bedroom_2_floor* | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor | bathroom_2_floor*  (2 distinct end places)

### binder clips: 1 of 1 instances moved
- binder_clips_black_metal_pair: living_room_dining_table_top | living_room_dining_table_top | living_room_dining_table_top | living_room_dining_table_top | living_room_small_shelving_unit_by_the_sofa_fourth_shelf_from_the_bottom* | living_room_small_shelving_unit_by_the_sofa_fourth_shelf_from_the_bottom | living_room_small_shelving_unit_by_the_sofa_fourth_shelf_from_the_bottom | living_room_small_shelving_unit_by_the_sofa_fourth_shelf_from_the_bottom  (2 distinct end places)

### body wash: 1 of 1 instances moved
- body_wash_blue_pump_bottle: bathroom_1_curved_bathroom_shelf_lower_shelf | bathroom_1_curved_bathroom_shelf_lower_shelf | bathroom_1_curved_bathroom_shelf_lower_shelf | bathroom_1_curved_bathroom_shelf_lower_shelf | bathroom_2_shower_room_sink_cabinet_sink_basin* | bathroom_2_shower_room_sink_cabinet_sink_basin* | bathroom_2_shower_room_sink_cabinet_sink_basin* | bathroom_2_shower_room_sink_cabinet_sink_basin*  (2 distinct end places)

### bowl: 1 of 1 instances moved
- bowl_white_cereal: inside glass_tumbler_clear_smooth | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin* | living_room_end_table_by_the_large_sofa_top* | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (4 distinct end places)

### brass spoon: 1 of 1 instances moved
- brass_spoon_small_tarnished: kitchen_kitchen_sink_cabinet_sink_cabinet_countertop | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf (hidden)* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop  (3 distinct end places)

### candle: 1 of 1 instances moved
- candle_cream_glass_jar: living_room_tv_console_top | living_room_tv_console_top | living_room_tv_console_top | living_room_tv_console_top | living_room_tv_console_top | living_room_tv_console_top | living_room_dining_table_top* | living_room_dining_table_top  (2 distinct end places)

### canvas folder: 1 of 1 instances moved
- canvas_folder_ochre_buttoned: bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden)* | bedroom_1_bed_in_the_first_bedroom_mattress* | bedroom_1_dresser_in_the_first_bedroom_top*  (4 distinct end places)

### canvas tote bag: 1 of 1 instances moved
- canvas_tote_bag_natural_cotton: bedroom_1_wardrobe_in_the_first_bedroom_inside | bedroom_2_desk_in_the_second_bedroom_desk_surface* | kitchen_floor* | kitchen_floor | hallway_floor* | hallway_floor | hallway_floor | hallway_floor  (3 distinct end places)

### cardigan: 1 of 1 instances moved
- cardigan_moss_green_knit: bedroom_1_dresser_in_the_first_bedroom_top | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor  (1 distinct end places)

### cereal box: 1 of 1 instances moved
- cereal_box_yellow_oat: kitchen_tall_kitchen_cabinet_with_oven_bottom_oven_cabinet_compartment | kitchen_tall_kitchen_cabinet_with_oven_bottom_oven_cabinet_compartment (hidden) | kitchen_tall_kitchen_cabinet_with_oven_bottom_oven_cabinet_compartment (hidden) | kitchen_tall_kitchen_cabinet_with_oven_bottom_oven_cabinet_compartment (hidden)* | kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf (hidden)* | kitchen_kitchen_island_island_countertop* | kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf (hidden)* | kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf (hidden)*  (3 distinct end places)

### cheddar cheese: 1 of 1 instances moved
- cheddar_cheese_yellow_wrapped_wedge: inside tomato_two_red_vine | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_fridge_freezer_middle_shelf_in_the_upper_fridge_door (hidden)* | kitchen_fridge_freezer_middle_shelf_in_the_upper_fridge_door (hidden)* | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop* | kitchen_fridge_freezer_middle_shelf_in_the_upper_fridge_door (hidden)* | kitchen_fridge_freezer_middle_shelf_in_the_upper_fridge_door (hidden)  (3 distinct end places)

### chef knife: 1 of 1 instances moved
- chef_knife_black_handle: kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_base_drawer | kitchen_double_kitchen_base_cabinet_by_the_bridge_cabinet_bridge_side_countertop* | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop* | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop* | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (5 distinct end places)

### coffee beans: 1 of 1 instances moved
- coffee_beans_brown_paper_bag: kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop | kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf (hidden)* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop | kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf (hidden)*  (3 distinct end places)

### cold medicine: 1 of 1 instances moved
- cold_medicine_amber_bottle: inside first_aid_kit_red_zippered | hallway_hallway_storage_cabinet_middle_shelf (hidden) | hallway_hallway_storage_cabinet_middle_shelf (hidden) | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface* | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface* | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface  (2 distinct end places)

### cooking oil: 1 of 1 instances moved
- cooking_oil_olive_glass: kitchen_kitchen_island_island_countertop | kitchen_double_kitchen_base_cabinet_by_the_bridge_cabinet_bridge_side_countertop* | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_cabinet_beside_the_sink_lower_shelf_beside_the_sink (hidden)* | kitchen_kitchen_cabinet_beside_the_sink_lower_shelf_beside_the_sink (hidden) | kitchen_kitchen_cabinet_beside_the_sink_lower_shelf_beside_the_sink (hidden) | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (4 distinct end places)

### cracker packet: 1 of 1 instances moved
- cracker_packet_opened_blue: inside snack_bowl_orange_ceramic | living_room_dining_table_top | living_room_dining_table_top | kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf (hidden)* | kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf (hidden)* | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop* | kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf (hidden)* | kitchen_wall_cabinet_by_the_base_cabinets_lower_base_cabinet_wall_shelf (hidden)  (3 distinct end places)

### cutting board: 1 of 1 instances moved
- cutting_board_thick_bamboo: kitchen_double_kitchen_base_cabinet_by_the_bridge_cabinet_bridge_side_countertop | kitchen_double_kitchen_base_cabinet_by_the_bridge_cabinet_bridge_side_countertop | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop* | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop* | kitchen_kitchen_island_island_countertop* | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop*  (4 distinct end places)

### deodorant: 1 of 1 instances moved
- deodorant_gray_roll_on: bathroom_2_bathroom_drawer_rack_by_the_toilet_third_compartment_from_the_bottom | bathroom_2_bathroom_drawer_rack_by_the_toilet_third_compartment_from_the_bottom (hidden) | bathroom_2_bathroom_drawer_rack_by_the_toilet_third_compartment_from_the_bottom (hidden)* | bathroom_2_bathroom_drawer_rack_by_the_toilet_third_compartment_from_the_bottom (hidden) | bathroom_2_bathroom_drawer_rack_by_the_toilet_third_compartment_from_the_bottom (hidden) | bathroom_2_bathroom_drawer_rack_by_the_toilet_third_compartment_from_the_bottom (hidden) | bathroom_2_bathroom_drawer_rack_by_the_toilet_third_compartment_from_the_bottom (hidden) | bathroom_2_bathroom_drawer_rack_by_the_toilet_third_compartment_from_the_bottom (hidden)  (1 distinct end places)

### dish towel: 1 of 1 instances moved
- dish_towel_white_red_stripe: kitchen_kitchen_cabinet_beside_the_sink_counter_beside_the_sink | kitchen_kitchen_cabinet_beside_the_sink_counter_beside_the_sink | kitchen_kitchen_cabinet_beside_the_sink_counter_beside_the_sink | kitchen_kitchen_cabinet_beside_the_sink_counter_beside_the_sink | kitchen_kitchen_cabinet_beside_the_sink_counter_beside_the_sink | kitchen_kitchen_cabinet_beside_the_sink_counter_beside_the_sink | kitchen_kitchen_cabinet_beside_the_sink_counter_beside_the_sink | kitchen_kitchen_cabinet_beside_the_sink_counter_beside_the_sink*  (1 distinct end places)

### electric kettle: 1 of 1 instances moved
- electric_kettle_white_plastic: kitchen_kitchen_cabinet_beside_the_sink_counter_beside_the_sink | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_island_island_countertop*  (2 distinct end places)

### evening leggings: 1 of 1 instances moved
- evening_leggings_black_jersey: bedroom_1_floor | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor*  (1 distinct end places)

### evening sweatshirt: 1 of 1 instances moved
- evening_sweatshirt_faded_plum: bedroom_1_floor | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor*  (1 distinct end places)

### evening t-shirt: 1 of 1 instances moved
- evening_t_shirt_rust_cotton: bedroom_2_large_bedroom_storage_cabinet_lowest_drawer_in_the_second_stack | bedroom_2_large_bedroom_storage_cabinet_lowest_drawer_in_the_second_stack (hidden) | bedroom_2_large_bedroom_storage_cabinet_lowest_drawer_in_the_second_stack (hidden) | bedroom_2_large_bedroom_storage_cabinet_lowest_drawer_in_the_second_stack (hidden) | bedroom_2_floor* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)  (3 distinct end places)

### exhibition floor plan: 1 of 1 instances moved
- exhibition_floor_plan_folded_blueprint: living_room_dining_table_top | living_room_dining_table_top | living_room_dining_table_top | living_room_small_shelving_unit_by_the_sofa_fourth_shelf_from_the_bottom* | living_room_small_shelving_unit_by_the_sofa_fourth_shelf_from_the_bottom | living_room_small_shelving_unit_by_the_sofa_fourth_shelf_from_the_bottom | living_room_small_shelving_unit_by_the_sofa_fourth_shelf_from_the_bottom | bedroom_2_floor (hidden)*  (3 distinct end places)

### exhibition notes: 1 of 1 instances moved
- exhibition_notes_loose_cream_pages: bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_floor (hidden)* | bedroom_2_floor (hidden) | bedroom_2_floor (hidden) | bedroom_2_floor (hidden) | bedroom_2_floor (hidden) | living_room_end_table_by_the_large_sofa_top* | bedroom_2_floor (hidden)*  (2 distinct end places)

### facial cleanser: 1 of 1 instances moved
- facial_cleanser_white_pump_bottle: bathroom_2_shower_room_sink_cabinet_top_shelf | bathroom_2_shower_room_sink_cabinet_sink_basin* | bathroom_2_shower_room_sink_cabinet_sink_basin | bathroom_2_shower_room_sink_cabinet_sink_basin* | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface* | bathroom_2_shower_room_sink_cabinet_sink_basin* | bathroom_2_shower_room_sink_cabinet_sink_basin | bathroom_2_shower_room_sink_cabinet_sink_basin  (2 distinct end places)

### first-aid kit: 1 of 1 instances moved
- first_aid_kit_red_zippered: hallway_hallway_storage_cabinet_middle_shelf | hallway_hallway_storage_cabinet_middle_shelf | hallway_hallway_storage_cabinet_middle_shelf | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface* | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface  (2 distinct end places)

### flashlight: 1 of 1 instances moved
- flashlight_black_rubber: hallway_hallway_storage_cabinet_top_shelf | hallway_hallway_storage_cabinet_top_shelf | hallway_hallway_storage_cabinet_top_shelf | hallway_hallway_storage_cabinet_top_shelf | hallway_hallway_storage_cabinet_top_shelf | hallway_hallway_storage_cabinet_top_shelf | living_room_dining_table_top* | living_room_dining_table_top  (2 distinct end places)

### frying pan: 1 of 1 instances moved
- frying_pan_black_nonstick: kitchen_single_kitchen_base_cabinet_by_the_oven_lower_oven_side_compartment | kitchen_single_kitchen_base_cabinet_by_the_oven_lower_oven_side_compartment (hidden) | kitchen_gas_stove_and_oven_first_stovetop_burner* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (4 distinct end places)

### hand cream: 1 of 1 instances moved
- hand_cream_lavender_metal_tube: bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top*  (1 distinct end places)

### headphones: 1 of 1 instances moved
- headphones_black_wireless: bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_floor (hidden)*  (2 distinct end places)

### hoodie: 1 of 1 instances moved
- hoodie_faded_charcoal_pullover: bedroom_2_large_bedroom_storage_cabinet_middle_drawer_in_the_first_stack | bedroom_2_large_bedroom_storage_cabinet_middle_drawer_in_the_first_stack (hidden) | bedroom_2_large_bedroom_storage_cabinet_middle_drawer_in_the_first_stack (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bedroom_2_floor* | bedroom_2_floor*  (3 distinct end places)

### house slippers: 1 of 2 instances moved
- house_slippers_gray_felt: bedroom_1_floor | with mara | bedroom_1_floor* | bedroom_1_floor | bedroom_1_floor | bedroom_1_floor* | with mara* | with mara  (2 distinct end places)

### jacket: 1 of 1 instances moved
- jacket_navy_lightweight: living_room_armchair_by_the_shelving_seat | hallway_floor* | living_room_armchair_by_the_shelving_seat* | living_room_armchair_by_the_shelving_seat | living_room_armchair_by_the_shelving_seat | living_room_armchair_by_the_shelving_seat | bedroom_2_floor* | bedroom_2_floor*  (3 distinct end places)

### laundry hamper: 1 of 2 instances moved
- laundry_hamper_gray_canvas: bedroom_1_floor | bedroom_1_floor | bedroom_1_floor | bedroom_1_floor | bedroom_1_floor | bedroom_1_floor | bedroom_1_floor | bedroom_1_floor*  (1 distinct end places)

### leftover container: 1 of 1 instances moved
- leftover_container_square_clear_plastic: inside cheddar_cheese_yellow_wrapped_wedge | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop (hidden) | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop (hidden) | kitchen_fridge_freezer_middle_shelf_in_the_upper_fridge_door (hidden) | kitchen_fridge_freezer_middle_shelf_in_the_upper_fridge_door (hidden)* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (3 distinct end places)

### lettuce: 1 of 1 instances moved
- lettuce_green_loose_head: kitchen_fridge_freezer_bottom_lower_door_shelf | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_fridge_freezer_lower_shelf_in_the_upper_fridge_door (hidden)* | kitchen_fridge_freezer_bottom_upper_door_shelf (hidden)* | kitchen_fridge_freezer_lower_shelf_in_the_upper_fridge_door (hidden)* | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop* | kitchen_fridge_freezer_middle_shelf_in_the_upper_fridge_door (hidden)* | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop*  (5 distinct end places)

### medicine: 1 of 1 instances moved
- medicine_amber_pill_bottle: bedroom_1_nightstand_by_the_wardrobe_upper_drawer | bedroom_1_nightstand_by_the_wardrobe_upper_drawer (hidden) | bedroom_1_nightstand_by_the_wardrobe_upper_drawer (hidden) | bedroom_1_nightstand_by_the_wardrobe_upper_drawer (hidden) | bedroom_1_nightstand_by_the_wardrobe_upper_drawer (hidden) | bedroom_1_nightstand_by_the_wardrobe_top* | bedroom_1_nightstand_by_the_wardrobe_top | bedroom_1_nightstand_by_the_wardrobe_top  (2 distinct end places)

### milk carton: 1 of 1 instances moved
- milk_carton_blue_white: kitchen_fridge_freezer_bottom_upper_door_shelf | kitchen_fridge_freezer_bottom_upper_door_shelf (hidden) | kitchen_fridge_freezer_bottom_upper_door_shelf (hidden) | kitchen_fridge_freezer_bottom_upper_door_shelf (hidden)* | kitchen_fridge_freezer_bottom_upper_door_shelf (hidden)* | kitchen_kitchen_island_island_countertop* | kitchen_fridge_freezer_lower_shelf_in_the_upper_fridge_door (hidden)* | kitchen_fridge_freezer_lower_shelf_in_the_upper_fridge_door (hidden)*  (3 distinct end places)

### moisturizer: 1 of 1 instances moved
- moisturizer_small_pink_tube: bathroom_1_double_bathroom_sink_cabinet_countertop | bathroom_1_double_bathroom_sink_cabinet_countertop | bathroom_1_double_bathroom_sink_cabinet_countertop | bathroom_1_double_bathroom_sink_cabinet_countertop | bathroom_1_double_bathroom_sink_cabinet_countertop | bathroom_1_double_bathroom_sink_cabinet_countertop | bathroom_1_double_bathroom_sink_cabinet_countertop | bathroom_1_double_bathroom_sink_cabinet_countertop*  (1 distinct end places)

### multipurpose cleaner: 1 of 1 instances moved
- multipurpose_cleaner_blue_spray_bottle: kitchen_kitchen_sink_cabinet_lower_sink_cabinet_shelf | kitchen_kitchen_sink_cabinet_lower_sink_cabinet_shelf (hidden) | kitchen_kitchen_sink_cabinet_lower_sink_cabinet_shelf (hidden) | kitchen_kitchen_sink_cabinet_lower_sink_cabinet_shelf (hidden) | kitchen_kitchen_sink_cabinet_lower_sink_cabinet_shelf (hidden) | kitchen_kitchen_sink_cabinet_lower_sink_cabinet_shelf (hidden) | kitchen_kitchen_sink_cabinet_lower_sink_cabinet_shelf (hidden) | kitchen_kitchen_sink_cabinet_lower_sink_cabinet_shelf (hidden)*  (1 distinct end places)

### museum badge: 1 of 1 instances moved
- museum_badge_white_lanyard: inside tray_shallow_walnut | hallway_hallway_storage_cabinet_middle_shelf* | hallway_hallway_storage_cabinet_middle_shelf* | hallway_hallway_storage_cabinet_middle_shelf | hallway_hallway_storage_cabinet_middle_shelf | hallway_hallway_storage_cabinet_middle_shelf | hallway_hallway_storage_cabinet_middle_shelf | hallway_hallway_storage_cabinet_middle_shelf*  (1 distinct end places)

### painkillers: 1 of 1 instances moved
- painkillers_white_blister_box: inside first_aid_kit_red_zippered | hallway_hallway_storage_cabinet_middle_shelf (hidden) | hallway_hallway_storage_cabinet_middle_shelf (hidden) | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top  (2 distinct end places)

### pajama shirt: 1 of 1 instances moved
- pajama_shirt_navy_cotton: inside None | with julian* | bedroom_2_floor* | with julian* | with julian* | with julian* | with julian* | with julian*  (2 distinct end places)

### pajama top: 1 of 1 instances moved
- pajama_top_soft_blue_cotton: inside None | with mara* | with mara* | with mara* | with mara* | with mara* | with mara* | with mara*  (1 distinct end places)

### paring knife: 1 of 1 instances moved
- paring_knife_short_red_handle: inside chef_knife_black_handle | kitchen_double_kitchen_base_cabinet_by_the_bridge_cabinet_bridge_side_countertop | kitchen_kitchen_island_island_countertop | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop* | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop  (4 distinct end places)

### pasta packet: 1 of 1 instances moved
- pasta_packet_clear_red_label: inside cereal_box_yellow_oat | kitchen_double_kitchen_base_cabinet_by_the_bridge_cabinet_bridge_side_countertop* | kitchen_kitchen_island_island_countertop* | kitchen_tall_kitchen_cabinet_with_oven_bottom_oven_cabinet_compartment (hidden)* | kitchen_tall_kitchen_cabinet_with_oven_bottom_oven_cabinet_compartment (hidden) | kitchen_tall_kitchen_cabinet_with_oven_bottom_oven_cabinet_compartment (hidden) | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_island_island_countertop*  (3 distinct end places)

### pen case: 1 of 1 instances moved
- pen_case_black_zippered: inside canvas_tote_bag_natural_cotton | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden)* | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden) | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden)  (2 distinct end places)

### pencil: 1 of 2 instances moved
- pencil_red_hexagonal: bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface  (1 distinct end places)

### pencil case: 1 of 1 instances moved
- pencil_case_olive_canvas_zippered: bedroom_2_small_shelf_by_the_desk_top | bedroom_2_small_shelf_by_the_desk_top | bedroom_2_small_shelf_by_the_desk_top | bedroom_2_small_shelf_by_the_desk_top | bedroom_2_small_shelf_by_the_desk_top | bedroom_2_small_shelf_by_the_desk_top | bedroom_2_small_shelf_by_the_desk_top | bedroom_2_floor (hidden)*  (2 distinct end places)

### plates: 1 of 1 instances moved
- plates_white_stack: kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf | kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf (hidden) | kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf (hidden) | kitchen_wall_cabinet_by_the_corner_lower_corner_cabinet_shelf (hidden) | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_island_island_countertop | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_island_island_countertop  (2 distinct end places)

### project tube: 1 of 1 instances moved
- project_tube_white_cardboard_capped: living_room_floor | living_room_floor | living_room_floor | living_room_floor | living_room_floor | living_room_floor | bedroom_2_floor* | bedroom_2_floor  (2 distinct end places)

### proof pages: 1 of 1 instances moved
- proof_pages_marked_cream: bedroom_2_desk_in_the_second_bedroom_desk_surface | bedroom_2_desk_in_the_second_bedroom_desk_surface (hidden)* | bedroom_2_desk_in_the_second_bedroom_desk_surface (hidden)* | bedroom_2_desk_in_the_second_bedroom_desk_surface (hidden)* | bedroom_2_desk_in_the_second_bedroom_desk_surface (hidden)* | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden)* | bedroom_1_bed_in_the_first_bedroom_mattress (hidden)* | bedroom_1_dresser_in_the_first_bedroom_top (hidden)*  (4 distinct end places)

### reading glasses case: 1 of 2 instances moved
- reading_glasses_case_blue_canvas: living_room_end_table_by_the_large_sofa_top | living_room_end_table_by_the_large_sofa_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top* | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | bedroom_1_nightstand_by_the_first_bedroom_bed_top | living_room_small_sofa_seat*  (3 distinct end places)

### remote control: 1 of 1 instances moved
- remote_control_black_slim: living_room_tv_console_top | living_room_end_table_by_the_large_sofa_top* | living_room_end_table_by_the_large_sofa_top* | living_room_large_sofa_seat* | living_room_end_table_by_the_large_sofa_top* | living_room_end_table_by_the_large_sofa_top* | living_room_end_table_by_the_large_sofa_top | living_room_end_table_by_the_large_sofa_top  (2 distinct end places)

### saucepan: 1 of 1 instances moved
- saucepan_stainless_steel_small: kitchen_gas_stove_and_oven_first_stovetop_burner | kitchen_gas_stove_and_oven_first_stovetop_burner | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (4 distinct end places)

### shampoo: 1 of 1 instances moved
- shampoo_amber_pump_bottle: bathroom_1_curved_bathroom_shelf_upper_shelf | bathroom_1_curved_bathroom_shelf_upper_shelf | bathroom_1_curved_bathroom_shelf_upper_shelf | bathroom_1_curved_bathroom_shelf_upper_shelf | bathroom_1_curved_bathroom_shelf_upper_shelf | bathroom_1_curved_bathroom_shelf_upper_shelf | bathroom_1_curved_bathroom_shelf_upper_shelf | bathroom_1_curved_bathroom_shelf_upper_shelf*  (1 distinct end places)

### shopping bag: 1 of 2 instances moved
- shopping_bag_folded_blue_nylon: kitchen_single_kitchen_base_cabinet_by_the_small_shelf_lower_small_shelf_cabinet_compartment | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_lower_small_shelf_cabinet_compartment (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_lower_small_shelf_cabinet_compartment (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_lower_small_shelf_cabinet_compartment (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_lower_small_shelf_cabinet_compartment (hidden) | kitchen_single_kitchen_base_cabinet_by_the_small_shelf_lower_small_shelf_cabinet_compartment (hidden) | hallway_hallway_storage_cabinet_bottom_shelf* | hallway_hallway_storage_cabinet_bottom_shelf  (2 distinct end places)

### snack bowl: 1 of 1 instances moved
- snack_bowl_orange_ceramic: living_room_dining_table_top | living_room_dining_table_top | living_room_dining_table_top | living_room_dining_table_top | living_room_dining_table_top* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_sink_cabinet_sink_basin* | kitchen_kitchen_island_island_countertop*  (3 distinct end places)

### sticky notes: 1 of 1 instances moved
- sticky_notes_pink_square_pad: living_room_dining_table_top | living_room_dining_table_top | living_room_dining_table_top | living_room_dining_table_top | living_room_dining_table_top | living_room_end_table_by_the_large_sofa_top* | living_room_end_table_by_the_large_sofa_top | living_room_end_table_by_the_large_sofa_top  (2 distinct end places)

### style sheet: 1 of 1 instances moved
- style_sheet_printed_white: inside canvas_tote_bag_natural_cotton | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_desk_surface* | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden)* | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden) | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden)  (2 distinct end places)

### sweatpants: 1 of 1 instances moved
- sweatpants_gray_jersey: bedroom_2_large_bedroom_storage_cabinet_lowest_drawer_in_the_second_stack | bedroom_2_large_bedroom_storage_cabinet_lowest_drawer_in_the_second_stack (hidden) | bedroom_2_large_bedroom_storage_cabinet_lowest_drawer_in_the_second_stack (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)* | bedroom_2_floor* | bedroom_2_floor*  (3 distinct end places)

### table spoon: 1 of 1 instances moved
- table_spoon_rounded_steel: inside table_knife_serrated_steel | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_sink_cabinet_sink_basin | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_island_island_countertop  (2 distinct end places)

### tea bag: 1 of 1 instances moved
- tea_bag_earl_grey_sachet: kitchen_kitchen_sink_cabinet_sink_cabinet_countertop | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | living_room_end_table_by_the_large_sofa_top* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | living_room_end_table_by_the_large_sofa_top*  (3 distinct end places)

### thermometer: 1 of 1 instances moved
- thermometer_digital_white: inside first_aid_kit_red_zippered | hallway_hallway_storage_cabinet_middle_shelf (hidden) | hallway_hallway_storage_cabinet_middle_shelf (hidden) | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | toilet_bathroom_drawer_cabinet_by_the_sink_larger_top_surface* | bathroom_2_bathroom_drawer_rack_by_the_shower_top_surface* | bathroom_2_bathroom_drawer_rack_by_the_shower_top_surface* | bedroom_2_nightstand_by_the_second_bedroom_bed_top*  (4 distinct end places)

### throw blanket: 1 of 1 instances moved
- throw_blanket_rust_wool: living_room_large_sofa_seat | living_room_large_sofa_seat* | living_room_large_sofa_seat | living_room_large_sofa_seat* | living_room_large_sofa_seat | living_room_large_sofa_seat | living_room_large_sofa_seat | living_room_large_sofa_seat  (1 distinct end places)

### tissues: 1 of 2 instances moved
- tissues_cube_white_blue_print: bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | bedroom_2_nightstand_by_the_second_bedroom_bed_top | living_room_end_table_by_the_large_sofa_top* | living_room_end_table_by_the_large_sofa_top | living_room_end_table_by_the_large_sofa_top | living_room_end_table_by_the_large_sofa_top | living_room_end_table_by_the_large_sofa_top  (2 distinct end places)

### tomato: 1 of 1 instances moved
- tomato_two_red_vine: kitchen_fridge_freezer_lower_shelf_in_the_upper_fridge_door | kitchen_double_kitchen_base_cabinet_by_the_bridge_cabinet_bridge_side_countertop* | kitchen_kitchen_island_island_countertop* | kitchen_fridge_freezer_lower_shelf_in_the_upper_fridge_door (hidden)* | kitchen_fridge_freezer_lower_shelf_in_the_upper_fridge_door (hidden)* | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop* | kitchen_fridge_freezer_middle_shelf_in_the_upper_fridge_door (hidden)* | kitchen_double_kitchen_base_cabinet_by_the_wall_cabinet_wall_side_countertop*  (5 distinct end places)

### toothpaste: 1 of 1 instances moved
- toothpaste_white_mint_tube: toilet_bathroom_drawer_cabinet_by_the_sink_smaller_top_surface | toilet_bathroom_drawer_cabinet_by_the_sink_smaller_top_surface* | toilet_bathroom_drawer_cabinet_by_the_sink_smaller_top_surface | toilet_bathroom_drawer_cabinet_by_the_sink_smaller_top_surface* | toilet_bathroom_drawer_cabinet_by_the_sink_smaller_top_surface* | bathroom_2_shower_room_sink_cabinet_sink_basin* | bathroom_2_shower_room_sink_cabinet_sink_basin* | bathroom_2_shower_room_sink_cabinet_sink_basin*  (2 distinct end places)

### travel mug: 1 of 1 instances moved
- travel_mug_red_insulated: kitchen_kitchen_cabinet_beside_the_sink_counter_beside_the_sink | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_island_island_countertop | kitchen_kitchen_island_island_countertop | kitchen_kitchen_island_island_countertop | living_room_end_table_by_the_large_sofa_top* | living_room_end_table_by_the_large_sofa_top | bedroom_2_floor (hidden)*  (3 distinct end places)

### tray: 1 of 1 instances moved
- tray_shallow_walnut: hallway_hallway_storage_cabinet_middle_shelf | living_room_dining_table_top* | living_room_dining_table_top* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop* | hallway_hallway_storage_cabinet_middle_shelf* | hallway_hallway_storage_cabinet_middle_shelf | hallway_hallway_storage_cabinet_middle_shelf | hallway_hallway_storage_cabinet_middle_shelf  (3 distinct end places)

### usb flash drive: 1 of 1 instances moved
- usb_flash_drive_silver_swivel: living_room_dining_table_top | living_room_dining_table_top | living_room_dining_table_top | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden)* | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden) | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden) | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden) | bedroom_2_desk_in_the_second_bedroom_first_desk_drawer (hidden)  (2 distinct end places)

### walking shoes: 1 of 1 instances moved
- walking_shoes_white_canvas: hallway_floor | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor | bedroom_1_floor  (1 distinct end places)

### wallet: 1 of 2 instances moved
- wallet_black_canvas: inside tray_shallow_walnut | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden)* | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bathroom_1_bathroom_hamper_cabinet_inside_the_hamper_cabinet (hidden) | bedroom_2_nightstand_by_the_second_bedroom_bed_top* | bedroom_2_nightstand_by_the_second_bedroom_bed_top  (2 distinct end places)

### watering can: 1 of 1 instances moved
- watering_can_small_galvanized: balcony_floor | balcony_floor | balcony_floor* | balcony_floor | balcony_floor | balcony_floor | balcony_floor* | balcony_floor  (1 distinct end places)

### wooden spoon: 1 of 1 instances moved
- wooden_spoon_long_beech: kitchen_kitchen_island_island_countertop | kitchen_double_kitchen_base_cabinet_by_the_bridge_cabinet_bridge_side_countertop* | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_cabinet_beside_the_sink_lower_shelf_beside_the_sink (hidden)* | kitchen_kitchen_cabinet_beside_the_sink_lower_shelf_beside_the_sink (hidden) | kitchen_kitchen_cabinet_beside_the_sink_lower_shelf_beside_the_sink (hidden) | kitchen_kitchen_island_island_countertop* | kitchen_kitchen_sink_cabinet_sink_cabinet_countertop*  (4 distinct end places)

### work blouse: 1 of 1 instances moved
- work_blouse_cream_linen: bedroom_1_dresser_in_the_first_bedroom_top | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor* | bedroom_1_floor  (1 distinct end places)

### work shoes: 1 of 1 instances moved
- work_shoes_black_leather: bedroom_2_floor | bedroom_2_floor* | bedroom_2_floor* | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor | bedroom_2_floor | bathroom_2_floor*  (2 distinct end places)

Types never moved (79): air freshener, bath mat, bathroom scale, batteries, body lotion, bookmark, butter dish, coaster, colander, comb, conditioner, cotton rounds, cotton swabs, dental floss, dish soap, duvet, earrings, egg carton, extension cord, foot scrubber, game controller, gardening gloves, hair clip, hair tie, hair towel, hairbrush, hand soap, hand towel, hdmi cable, headband, jewelry box, laundry detergent, loofah, lunch container, mail, measuring tape, mixing bowl, model, multitool, museum catalog, nail brush, nail clippers, nail file, newspaper, oven mitt, pencil cup, pepper grinder, pillow, plasters, potted plant, potting soil, power bank, razor, recipe notebook, rice jar, rubber, ruler, salt shaker, scarf, scissors, shaving cream, shower cap, shower squeegee, sketchbook, soap bar, soup bowl, spatula, sponge, stain remover, sugar jar, tea box, toilet paper, toiletry bag, toothbrush holder, tote bag, trash bags, umbrella, usb cable, whisk

## 3. Response habits: trigger present, habit followed

From each activity answer: which habits' triggers the resident said were true, and which habit they followed.

| resident | habit | how often (stated) | answers with trigger | followed | followed with trigger | followed without trigger | days followed |
|---|---|---|---|---|---|---|---|
| mara | mara_stress_walk: when When a client sends a rushed or contradictory revision request, She closes the laptop, takes a brisk walk, and returns with a short written list of what actually needs doing. | most times | 3 of 267 | 2 | 2 | 0 | [1] |
| mara | mara_tired_food: when When she has worked past 19:00, She stops cooking and asks Julian to order noodles or makes toast with cheese. | sometimes | 1 of 267 | 1 | 1 | 0 | [4] |
| mara | mara_sick_care: when When Julian feels unwell, She makes ginger tea, puts painkillers and water on the end table, and quietly checks his temperature. | almost always | 73 of 267 | 56 | 50 | 6 | [3, 4, 5] |
| mara | mara_interruption: when When someone interrupts a sentence she is editing, She goes very still, rereads the sentence aloud, and answers more patiently than her expression suggests. | most times | 2 of 267 | 3 | 2 | 1 | [5, 6] |
| julian | julian_crisis_mode: when When a work problem becomes urgent, He becomes unusually cheerful, makes a handwritten checklist, and starts calling people immediately. | almost always | 3 of 232 | 2 | 2 | 0 | [3] |
| julian | julian_tired_order: when When he gets home after a late gallery setup, He orders food, showers, and refuses to discuss the day until he has eaten. | most times | 4 of 232 | 4 | 4 | 0 | [3, 5] |
| julian | julian_hosting: when When friends are coming over, He rearranges the dining table, fills the fridge with drinks, and puts music on far too early. | almost always | 8 of 232 | 5 | 5 | 0 | [6] |
| julian | julian_frustrated_fix: when When something in the apartment breaks, He tries to repair it immediately, even if the correct response would be to call the landlord. | most times | 0 of 232 | 0 | 0 | 0 | - |

## 4. Sick days against normal days

Sick days: [3, 4, 5]; sick: ['julian']

### mara (the other resident)

| day | sick day | wake | sleep | minutes out | objects moved | rooms by actions | stress | tired | mood | health |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 |  | 07:30 | 22:15 | 45 | 41 | bedroom_1 52, bedroom_2 34, kitchen 30, living_room 19 | 0.4 | 0.8 | 2.4 | 3.0 |
| 2 |  | 07:30 | 22:15 | 80 | 40 | bedroom_1 55, kitchen 55, bedroom_2 42, living_room 18 | 0.0 | 0.9 | 2.8 | 3.0 |
| 3 | yes | 07:00 | 22:30 | 0 | 51 | kitchen 100, bedroom_2 78, bedroom_1 40, living_room 25 | 0.8 | 1.0 | 2.0 | 3.0 |
| 4 | yes | 07:00 | 22:30 | 45 | 48 | bedroom_2 107, kitchen 87, bedroom_1 38, living_room 16 | 0.6 | 1.1 | 2.0 | 3.0 |
| 5 | yes | 07:00 | 22:25 | 45 | 54 | bedroom_2 87, kitchen 85, bedroom_1 64, living_room 30 | 0.8 | 1.1 | 2.0 | 3.0 |
| 6 |  | 08:30 | 22:30 | 0 | 55 | bedroom_1 83, kitchen 82, living_room 61, bathroom_1 10 | 0.5 | 0.9 | 2.7 | 3.0 |
| 7 |  | 08:00 | 22:00 | 0 | 56 | kitchen 156, living_room 65, bedroom_1 54, bathroom_1 14 | 0.2 | 1.0 | 2.5 | 3.0 |

Moved only on sick days: cooking_oil_olive_glass, first_aid_kit_red_zippered, mug_yellow_ceramic, painkillers_white_blister_box, paring_knife_short_red_handle, phone_charger_white_braided, phone_dark_green_glass, thermometer_digital_white, travel_mug_red_insulated, tray_shallow_walnut, wooden_spoon_long_beech

Moved only on other days: adhesive_tape_clear_dispenser, bath_towel_sage_green_waffle, bath_towel_white_waffle, bed_linen_set_sage_stripe_folded, bed_linen_set_white_cotton_folded, book_paperback_ochre_cover, candle_cream_glass_jar, dish_towel_white_red_stripe, drinking_glass_clear_dimpled, drinking_glass_clear_tall, drinking_glass_smoked_short, fork_long_four_tine, fork_rounded_handle, fork_short_four_tine, glass_tumbler_clear_fluted, glass_tumbler_clear_ribbed, hand_cream_lavender_metal_tube, jeans_midblue_relaxed_leg, laundry_hamper_gray_canvas, moisturizer_small_pink_tube, multipurpose_cleaner_blue_spray_bottle, pencil_red_hexagonal, plates_white_stack, reading_glasses_case_blue_canvas, reading_glasses_thin_gold_frames, receipt_small_white_thermal, remote_control_black_slim, shampoo_amber_pump_bottle, sleep_mask_charcoal_linen, snack_bowl_orange_ceramic, table_knife_black_handle, table_knife_plain_rounded, table_knife_slender_serrated, water_bottle_steel_blue, watering_can_small_galvanized

### julian (sick)

| day | sick day | wake | sleep | minutes out | objects moved | rooms by actions | stress | tired | mood | health |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 |  | 07:15 | 22:00 | 629 | 29 | bedroom_2 58, kitchen 31, living_room 21, hallway 12 | 0.5 | 0.9 | 2.8 | 3.0 |
| 2 |  | 07:15 | 21:30 | 629 | 30 | kitchen 47, bedroom_2 29, living_room 15, hallway 7 | 0.7 | 1.1 | 2.7 | 3.0 |
| 3 | yes | 07:15 | 21:30 | 0 | 36 | living_room 67, bedroom_2 65, kitchen 27, toilet 14 | 1.3 | 2.8 | 1.1 | 1.2 |
| 4 | yes | 07:30 | 22:00 | 0 | 33 | bedroom_2 71, living_room 33, toilet 32, kitchen 28 | 1.2 | 2.7 | 1.0 | 1.0 |
| 5 | yes | 07:30 | 22:00 | 0 | 29 | bedroom_2 57, living_room 51, bathroom_2 32, kitchen 27 | 1.1 | 2.7 | 1.1 | 1.1 |
| 6 |  | 08:30 | 22:30 | 36 | 58 | kitchen 120, living_room 107, bathroom_2 45, bedroom_2 40 | 0.8 | 1.4 | 2.5 | 2.3 |
| 7 |  | 07:30 | 21:30 | 222 | 49 | kitchen 115, bedroom_2 67, bathroom_2 36, living_room 36 | 1.0 | 1.0 | 2.1 | 3.0 |

Moved only on sick days: binder_clips_black_metal_pair, brass_spoon_small_tarnished, cold_medicine_amber_bottle, envelope_brown_kraft, evening_t_shirt_rust_cotton, facial_cleanser_white_pump_bottle, first_aid_kit_red_zippered, medicine_amber_pill_bottle, mug_cream_striped, sticky_notes_pink_square_pad, tea_bag_earl_grey_sachet, tissues_cube_white_blue_print, usb_flash_drive_silver_swivel, water_bottle_amber_glass

Moved only on other days: apron_striped_linen, art_catalog_large_cream_cover, backpack_charcoal_canvas, belt_brown_leather, candle_cream_glass_jar, chef_knife_black_handle, coffee_beans_brown_paper_bag, coffee_mug_green_speckled, cutting_board_thick_bamboo, deodorant_gray_roll_on, dinner_plate_cream_floral, drinking_glass_clear_dimpled, drinking_glass_clear_tall, envelope_white_long_unopened, exhibition_notes_loose_cream_pages, flashlight_black_rubber, fork_long_four_tine, fork_rounded_handle, fork_short_four_tine, frying_pan_black_nonstick, headphones_black_wireless, jacket_navy_lightweight, laptop_black_museum, museum_badge_white_lanyard, painkillers_white_blister_box, pencil_case_olive_canvas_zippered, phone_charger_white_usb_c, project_tube_white_cardboard_capped, saucepan_stainless_steel_small, shopping_bag_folded_blue_nylon, sleep_mask_navy_padded_cotton, socks_navy_wool_pair, table_knife_black_handle, table_knife_plain_rounded, table_knife_serrated_steel, table_knife_slender_serrated, table_spoon_rounded_steel, travel_mug_red_insulated, wallet_black_canvas, water_bottle_steel_blue, work_shirt_pale_blue_oxford, work_shirt_white_cotton_poplin, work_shoes_black_leather, work_trousers_gray_wool_straight_leg, work_trousers_navy_wool

## 5. Excerpts

See the hand-written section in the pilot write-up, chosen from replay.md.
