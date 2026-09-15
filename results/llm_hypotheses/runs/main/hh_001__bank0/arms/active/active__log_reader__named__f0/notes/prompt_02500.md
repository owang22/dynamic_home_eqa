# call 2500: remote_shared_1 at d25 Fri 08:26

## system

You control a home robot's memory. You read its sighting log and decide, for one question at a time, whether to look inside a receptacle or to answer where an object is.

## user

A home robot patrols a home and records what it sees. You will be given its log, then one question. Decide whether to look inside one receptacle first, or to answer now.

RECEPTACLES (every place an object can be):
  bed_b1  in bedroom
  nightstand_b1  in bedroom
  desk_b1  in bedroom
  bedroom_floor_b1  in bedroom
  couch_l1  in living
  coffee_table_l1  in living
  tv_stand_l1  in living
  bookshelf_l1  in living
  armchair_l1  in living
  counter_k1  in kitchen
  sink_k1  in kitchen
  cupboard_k1  in kitchen
  dish_rack_k1  in kitchen
  kitchen_table_k1  in kitchen
  chair_k1  in kitchen
  chair_k2  in kitchen
  bathroom_shelf_ba1  in bathroom
  towel_rack_ba1  in bathroom
  entry_table_e1  in entry
  entry_hook_e1  in entry
  entry_floor_e1  in entry
  ON_PERSON
  OUT_OF_HOUSE
ON_PERSON means a resident who is in the house is carrying the object. OUT_OF_HOUSE means the object is not in the house. Neither can be chosen as the target of a look.

LOG FORMAT: one line per event, oldest first. "dNN Day HH:MM <object> at <receptacle>" is a sighting; "dNN Day HH:MM look <receptacle>: <objects>" lists everything found inside that receptacle at that moment. Lines tagged [walkthrough] are from the robot's installation tour. The log lists what the robot saw; it is the only information there is.

SENSING: one look inspects one receptacle and reports every object inside it. Each look costs from a daily budget of 24 that resets at midnight. A look answers the current question and also stays in the log for every later question, so a look can be spent on learning rather than on the question at hand. There is no penalty for spending budget beyond not having it later.

SCORING: an answer scores one point if its first ranked receptacle is where the object actually is at the question's time, and zero otherwise.

OUTPUT: one JSON object. Either {"action": "sense", "receptacle": "<receptacle id>", "why": "..."} or {"action": "answer", "ranked": ["<most likely receptacle>", "...up to 5..."], "why": "..."}. Use receptacle ids exactly as listed.

OBJECTS the robot has seen so far:
  backpack_mara  (class: backpack)
  blanket_mara  (class: blanket)
  book_mara  (class: book)
  bowl_shared_1  (class: bowl)
  bowl_shared_2  (class: bowl)
  charger_mara  (class: charger)
  glasses_mara  (class: glasses)
  hairbrush_mara  (class: hairbrush)
  headphones_mara  (class: headphones)
  jacket_mara  (class: jacket)
  keys_mara  (class: keys)
  laptop_mara  (class: laptop)
  laundry_basket_mara  (class: laundry_basket)
  lunchbox_mara  (class: lunchbox)
  makeup_kit_mara  (class: makeup_kit)
  medication_bottle_mara  (class: medication_bottle)
  mug_mara  (class: mug)
  mug_shared_1  (class: mug)
  notebook_mara  (class: notebook)
  pan_shared_1  (class: pan)
  pen_mara  (class: pen)
  phone_mara  (class: phone)
  plate_shared_1  (class: plate)
  plate_shared_2  (class: plate)
  pot_shared_1  (class: pot)
  remote_shared_1  (class: remote)
  suitcase_mara  (class: suitcase)
  tablet_mara  (class: tablet)
  towel_mara  (class: towel)
  umbrella_mara  (class: umbrella)
  vacuum_cleaner_shared_1  (class: vacuum_cleaner)
  wallet_mara  (class: wallet)
  water_bottle_mara  (class: water_bottle)
  watering_can_mara  (class: watering_can)
  yoga_mat_mara  (class: yoga_mat)

LOG:
d00 Mon 15:08 [walkthrough] blanket_mara at couch_l1
d00 Mon 15:08 [walkthrough] book_mara at bookshelf_l1
d00 Mon 15:08 [walkthrough] bowl_shared_1 at entry_table_e1
d00 Mon 15:08 [walkthrough] bowl_shared_2 at kitchen_table_k1
d00 Mon 15:08 [walkthrough] hairbrush_mara at nightstand_b1
d00 Mon 15:08 [walkthrough] laundry_basket_mara at bedroom_floor_b1
d00 Mon 15:08 [walkthrough] lunchbox_mara at counter_k1
d00 Mon 15:08 [walkthrough] makeup_kit_mara at bathroom_shelf_ba1
d00 Mon 15:08 [walkthrough] medication_bottle_mara at bathroom_shelf_ba1
d00 Mon 15:08 [walkthrough] mug_mara at chair_k1
d00 Mon 15:08 [walkthrough] mug_shared_1 at cupboard_k1
d00 Mon 15:08 [walkthrough] pan_shared_1 at sink_k1
d00 Mon 15:08 [walkthrough] pen_mara at kitchen_table_k1
d00 Mon 15:08 [walkthrough] plate_shared_1 at cupboard_k1
d00 Mon 15:08 [walkthrough] plate_shared_2 at counter_k1
d00 Mon 15:08 [walkthrough] pot_shared_1 at cupboard_k1
d00 Mon 15:08 [walkthrough] remote_shared_1 at coffee_table_l1
d00 Mon 15:08 [walkthrough] suitcase_mara at bedroom_floor_b1
d00 Mon 15:08 [walkthrough] tablet_mara at coffee_table_l1
d00 Mon 15:08 [walkthrough] towel_mara at towel_rack_ba1
d00 Mon 15:08 [walkthrough] umbrella_mara at entry_floor_e1
d00 Mon 15:08 [walkthrough] vacuum_cleaner_shared_1 at bedroom_floor_b1
d00 Mon 15:08 [walkthrough] watering_can_mara at sink_k1
d00 Mon 15:08 [walkthrough] yoga_mat_mara at couch_l1
d00 Mon 15:37 look bathroom_shelf_ba1: makeup_kit_mara, medication_bottle_mara
d00 Mon 15:37 look towel_rack_ba1: towel_mara
d00 Mon 15:44 look chair_k1: mug_mara
d00 Mon 16:10 look sink_k1: pan_shared_1, watering_can_mara
d00 Mon 16:34 look cupboard_k1: mug_shared_1, phone_mara, plate_shared_1, pot_shared_1
d00 Mon 18:11 look entry_hook_e1: (nothing)
d00 Mon 19:00 look entry_floor_e1: umbrella_mara
d00 Mon 19:00 look entry_hook_e1: (nothing)
d00 Mon 19:00 look entry_table_e1: bowl_shared_1, keys_mara
d00 Mon 19:33 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d00 Mon 19:56 look coffee_table_l1: remote_shared_1, tablet_mara
d00 Mon 20:21 look couch_l1: blanket_mara, yoga_mat_mara
d00 Mon 20:33 look nightstand_b1: hairbrush_mara
d00 Mon 21:31 look bathroom_shelf_ba1: makeup_kit_mara, medication_bottle_mara
d00 Mon 22:14 look bed_b1: (nothing)
d00 Mon 22:14 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d00 Mon 22:14 look desk_b1: (nothing)
d00 Mon 22:14 look nightstand_b1: hairbrush_mara
d01 Tue 05:18 look towel_rack_ba1: towel_mara
d01 Tue 06:43 look armchair_l1: (nothing)
d01 Tue 06:43 look bookshelf_l1: book_mara
d01 Tue 06:43 look coffee_table_l1: remote_shared_1, tablet_mara
d01 Tue 06:43 look couch_l1: blanket_mara, yoga_mat_mara
d01 Tue 06:43 look tv_stand_l1: (nothing)
d01 Tue 07:02 look entry_table_e1: bowl_shared_1
d01 Tue 07:13 look entry_table_e1: bowl_shared_1
d01 Tue 07:58 look sink_k1: bowl_shared_2, watering_can_mara
d01 Tue 08:12 look cupboard_k1: mug_shared_1, pot_shared_1
d01 Tue 08:33 look counter_k1: mug_mara, notebook_mara, pan_shared_1, plate_shared_2
d01 Tue 08:33 look kitchen_table_k1: plate_shared_1
d01 Tue 09:41 look chair_k1: (nothing)
d01 Tue 09:41 look chair_k2: (nothing)
d01 Tue 09:41 look counter_k1: mug_mara, notebook_mara, pan_shared_1, plate_shared_2
d01 Tue 09:41 look cupboard_k1: mug_shared_1, pot_shared_1
d01 Tue 09:41 look dish_rack_k1: pen_mara
d01 Tue 09:41 look kitchen_table_k1: plate_shared_1
d01 Tue 09:41 look sink_k1: bowl_shared_2, watering_can_mara
d01 Tue 12:22 look entry_hook_e1: (nothing)
d01 Tue 12:22 look entry_floor_e1: umbrella_mara
d01 Tue 12:49 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d01 Tue 12:49 look towel_rack_ba1: towel_mara
d01 Tue 15:08 look entry_hook_e1: (nothing)
d01 Tue 15:08 look entry_floor_e1: umbrella_mara
d01 Tue 15:47 look entry_floor_e1: umbrella_mara
d01 Tue 15:47 look entry_hook_e1: (nothing)
d01 Tue 15:47 look entry_table_e1: bowl_shared_1
d01 Tue 16:18 look cupboard_k1: mug_shared_1, phone_mara, pot_shared_1
d01 Tue 18:43 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d01 Tue 18:43 look nightstand_b1: phone_mara
d01 Tue 18:56 look bed_b1: (nothing)
d01 Tue 18:56 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d01 Tue 18:56 look desk_b1: (nothing)
d01 Tue 18:56 look nightstand_b1: phone_mara
d01 Tue 19:38 look entry_hook_e1: backpack_mara
d01 Tue 20:33 look entry_table_e1: bowl_shared_1
d01 Tue 21:45 look armchair_l1: (nothing)
d01 Tue 21:45 look bookshelf_l1: book_mara
d01 Tue 21:45 look coffee_table_l1: remote_shared_1, tablet_mara
d01 Tue 21:45 look couch_l1: blanket_mara, water_bottle_mara, yoga_mat_mara
d01 Tue 21:45 look tv_stand_l1: (nothing)
d02 Wed 05:39 look entry_hook_e1: backpack_mara
d02 Wed 05:39 look entry_floor_e1: umbrella_mara
d02 Wed 05:42 look counter_k1: mug_mara, notebook_mara
d02 Wed 05:42 look kitchen_table_k1: charger_mara, glasses_mara, jacket_mara, laptop_mara, plate_shared_1, plate_shared_2
d02 Wed 05:42 look sink_k1: bowl_shared_2, lunchbox_mara, pan_shared_1, watering_can_mara
d02 Wed 05:48 look chair_k1: (nothing)
d02 Wed 05:48 look chair_k2: (nothing)
d02 Wed 05:48 look counter_k1: mug_mara, notebook_mara
d02 Wed 05:48 look cupboard_k1: headphones_mara, keys_mara, mug_shared_1, pot_shared_1
d02 Wed 05:48 look dish_rack_k1: pen_mara, wallet_mara
d02 Wed 05:48 look kitchen_table_k1: charger_mara, glasses_mara, jacket_mara, laptop_mara, plate_shared_1, plate_shared_2
d02 Wed 05:48 look sink_k1: bowl_shared_2, lunchbox_mara, pan_shared_1, watering_can_mara
d02 Wed 06:37 look bathroom_shelf_ba1: hairbrush_mara, medication_bottle_mara
d02 Wed 08:37 look bathroom_shelf_ba1: hairbrush_mara, medication_bottle_mara
d02 Wed 08:55 look bathroom_shelf_ba1: hairbrush_mara, medication_bottle_mara
d02 Wed 08:55 look towel_rack_ba1: towel_mara
d02 Wed 11:25 look sink_k1: watering_can_mara
d02 Wed 11:38 look counter_k1: pen_mara, plate_shared_2
d02 Wed 12:16 look coffee_table_l1: remote_shared_1, tablet_mara
d02 Wed 12:20 look entry_floor_e1: umbrella_mara
d02 Wed 12:20 look entry_hook_e1: (nothing)
d02 Wed 12:20 look entry_table_e1: bowl_shared_1
d02 Wed 13:05 look couch_l1: blanket_mara, water_bottle_mara, yoga_mat_mara
d02 Wed 15:21 look counter_k1: pen_mara, plate_shared_2
d02 Wed 15:35 look bed_b1: (nothing)
d02 Wed 15:35 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d02 Wed 15:35 look desk_b1: (nothing)
d02 Wed 15:35 look nightstand_b1: (nothing)
d02 Wed 16:08 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara, makeup_kit_mara, mug_mara, pan_shared_1, plate_shared_1
d02 Wed 16:11 look cupboard_k1: mug_shared_1, pot_shared_1
d02 Wed 17:19 look bookshelf_l1: book_mara
d02 Wed 18:39 look entry_hook_e1: backpack_mara, jacket_mara
d02 Wed 18:53 look armchair_l1: (nothing)
d02 Wed 18:53 look bookshelf_l1: (nothing)
d02 Wed 18:53 look coffee_table_l1: glasses_mara, remote_shared_1, tablet_mara
d02 Wed 18:53 look couch_l1: blanket_mara, water_bottle_mara, yoga_mat_mara
d02 Wed 18:53 look tv_stand_l1: (nothing)
d02 Wed 19:41 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara, makeup_kit_mara
d02 Wed 20:03 look cupboard_k1: mug_shared_1
d02 Wed 20:22 look bathroom_shelf_ba1: hairbrush_mara, medication_bottle_mara
d02 Wed 20:45 look sink_k1: pan_shared_1, plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d02 Wed 21:58 look cupboard_k1: mug_shared_1
d02 Wed 21:58 look nightstand_b1: book_mara
d02 Wed 22:18 look chair_k1: notebook_mara, pen_mara
d02 Wed 22:18 look chair_k2: (nothing)
d02 Wed 22:18 look counter_k1: (nothing)
d02 Wed 22:18 look cupboard_k1: mug_shared_1
d02 Wed 22:18 look dish_rack_k1: lunchbox_mara, mug_mara
d02 Wed 22:18 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara, makeup_kit_mara
d02 Wed 22:18 look sink_k1: pan_shared_1, plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d03 Thu 05:43 look dish_rack_k1: lunchbox_mara, mug_mara
d03 Thu 05:59 look bathroom_shelf_ba1: hairbrush_mara
d03 Thu 05:59 look towel_rack_ba1: laptop_mara, towel_mara, wallet_mara
d03 Thu 06:57 look entry_floor_e1: umbrella_mara
d03 Thu 08:43 look sink_k1: pan_shared_1, plate_shared_1, plate_shared_2, pot_shared_1, wallet_mara, watering_can_mara
d03 Thu 08:49 look counter_k1: medication_bottle_mara, mug_mara
d03 Thu 08:49 look chair_k1: notebook_mara, pen_mara
d03 Thu 08:59 look entry_floor_e1: umbrella_mara
d03 Thu 08:59 look entry_hook_e1: backpack_mara, jacket_mara
d03 Thu 08:59 look entry_table_e1: bowl_shared_1, keys_mara
d03 Thu 09:05 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara
d03 Thu 09:47 look towel_rack_ba1: laptop_mara, towel_mara
d03 Thu 10:44 look sink_k1: pan_shared_1, plate_shared_1, plate_shared_2, pot_shared_1, wallet_mara, watering_can_mara
d03 Thu 10:57 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara
d03 Thu 11:15 look cupboard_k1: glasses_mara, mug_shared_1
d03 Thu 11:15 look nightstand_b1: book_mara, phone_mara
d03 Thu 11:27 look sink_k1: pan_shared_1, plate_shared_1, plate_shared_2, pot_shared_1, wallet_mara, watering_can_mara
d03 Thu 12:17 look bed_b1: (nothing)
d03 Thu 12:17 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d03 Thu 12:17 look desk_b1: (nothing)
d03 Thu 12:17 look nightstand_b1: book_mara, phone_mara
d03 Thu 12:35 look couch_l1: blanket_mara, water_bottle_mara, yoga_mat_mara
d03 Thu 15:20 look sink_k1: pan_shared_1, plate_shared_1, plate_shared_2, pot_shared_1, wallet_mara, watering_can_mara
d03 Thu 15:23 look armchair_l1: (nothing)
d03 Thu 15:23 look bookshelf_l1: (nothing)
d03 Thu 15:23 look coffee_table_l1: remote_shared_1, tablet_mara
d03 Thu 15:23 look couch_l1: blanket_mara, water_bottle_mara, yoga_mat_mara
d03 Thu 15:23 look tv_stand_l1: (nothing)
d03 Thu 16:03 look chair_k1: (nothing)
d03 Thu 16:40 look cupboard_k1: mug_shared_1, notebook_mara
d03 Thu 17:21 look chair_k1: (nothing)
d03 Thu 18:24 look sink_k1: book_mara, jacket_mara, pan_shared_1, pot_shared_1, watering_can_mara
d03 Thu 18:25 look towel_rack_ba1: towel_mara
d03 Thu 18:35 look chair_k1: (nothing)
d03 Thu 18:35 look chair_k2: keys_mara, wallet_mara
d03 Thu 18:35 look counter_k1: medication_bottle_mara, mug_mara, plate_shared_2
d03 Thu 18:35 look cupboard_k1: mug_shared_1, notebook_mara
d03 Thu 18:35 look dish_rack_k1: backpack_mara, lunchbox_mara
d03 Thu 18:35 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara, pen_mara, plate_shared_1
d03 Thu 18:35 look sink_k1: book_mara, jacket_mara, pan_shared_1, pot_shared_1, watering_can_mara
d03 Thu 18:44 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara
d03 Thu 21:56 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara
d03 Thu 21:56 look towel_rack_ba1: towel_mara
d04 Fri 04:45 look dish_rack_k1: backpack_mara, lunchbox_mara
d04 Fri 04:48 look sink_k1: book_mara, jacket_mara, pan_shared_1, pot_shared_1, watering_can_mara
d04 Fri 06:09 look entry_floor_e1: umbrella_mara
d04 Fri 06:09 look entry_hook_e1: (nothing)
d04 Fri 06:09 look entry_table_e1: bowl_shared_1
d04 Fri 06:41 look nightstand_b1: phone_mara
d04 Fri 06:59 look kitchen_table_k1: bowl_shared_2, pan_shared_1, plate_shared_1
d04 Fri 07:55 look coffee_table_l1: tablet_mara
d04 Fri 08:54 look bed_b1: (nothing)
d04 Fri 08:54 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d04 Fri 08:54 look desk_b1: (nothing)
d04 Fri 08:54 look nightstand_b1: (nothing)
d04 Fri 09:31 look kitchen_table_k1: bowl_shared_2, pan_shared_1, plate_shared_1
d04 Fri 11:19 look armchair_l1: (nothing)
d04 Fri 11:19 look bookshelf_l1: (nothing)
d04 Fri 11:19 look coffee_table_l1: tablet_mara
d04 Fri 11:19 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d04 Fri 11:19 look tv_stand_l1: (nothing)
d04 Fri 11:33 look dish_rack_k1: (nothing)
d04 Fri 11:35 look kitchen_table_k1: bowl_shared_2, pan_shared_1, plate_shared_1
d04 Fri 11:37 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d04 Fri 12:32 look sink_k1: book_mara, pot_shared_1, watering_can_mara
d04 Fri 13:38 look towel_rack_ba1: towel_mara
d04 Fri 14:09 look chair_k1: (nothing)
d04 Fri 14:09 look chair_k2: (nothing)
d04 Fri 14:09 look counter_k1: mug_mara, pen_mara, plate_shared_2
d04 Fri 14:09 look cupboard_k1: mug_shared_1
d04 Fri 14:09 look dish_rack_k1: (nothing)
d04 Fri 14:09 look kitchen_table_k1: bowl_shared_2, pan_shared_1, plate_shared_1
d04 Fri 14:09 look sink_k1: book_mara, pot_shared_1, watering_can_mara
d04 Fri 16:53 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d04 Fri 16:53 look towel_rack_ba1: towel_mara
d04 Fri 17:31 look sink_k1: book_mara, pot_shared_1, watering_can_mara
d04 Fri 17:31 look kitchen_table_k1: bowl_shared_2, pan_shared_1, plate_shared_1
d04 Fri 17:31 look dish_rack_k1: (nothing)
d04 Fri 19:31 look entry_floor_e1: umbrella_mara
d04 Fri 19:31 look entry_hook_e1: backpack_mara, jacket_mara
d04 Fri 19:31 look entry_table_e1: bowl_shared_1, wallet_mara
d04 Fri 19:51 look counter_k1: mug_mara, pen_mara, plate_shared_2, water_bottle_mara
d05 Sat 07:45 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d05 Sat 07:56 look bed_b1: (nothing)
d05 Sat 07:56 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d05 Sat 07:56 look desk_b1: (nothing)
d05 Sat 07:56 look nightstand_b1: (nothing)
d05 Sat 08:16 look counter_k1: mug_mara, pan_shared_1, pen_mara, plate_shared_2, water_bottle_mara
d05 Sat 08:23 look entry_table_e1: bowl_shared_1
d05 Sat 08:38 look sink_k1: book_mara, bowl_shared_2, pot_shared_1, watering_can_mara
d05 Sat 08:38 look dish_rack_k1: (nothing)
d05 Sat 08:38 look kitchen_table_k1: charger_mara, notebook_mara, plate_shared_1
d05 Sat 09:16 look nightstand_b1: (nothing)
d05 Sat 10:38 look towel_rack_ba1: towel_mara
d05 Sat 11:00 look armchair_l1: lunchbox_mara
d05 Sat 11:00 look bookshelf_l1: laptop_mara
d05 Sat 11:00 look coffee_table_l1: tablet_mara
d05 Sat 11:00 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d05 Sat 11:00 look tv_stand_l1: (nothing)
d05 Sat 11:21 look cupboard_k1: bowl_shared_2
d05 Sat 11:24 look nightstand_b1: (nothing)
d05 Sat 11:33 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d05 Sat 11:36 look cupboard_k1: bowl_shared_2
d05 Sat 13:16 look kitchen_table_k1: charger_mara, glasses_mara, headphones_mara, mug_mara, notebook_mara
d05 Sat 13:50 look chair_k1: (nothing)
d05 Sat 13:50 look chair_k2: (nothing)
d05 Sat 13:50 look counter_k1: lunchbox_mara, pan_shared_1, pen_mara, phone_mara, tablet_mara, water_bottle_mara
d05 Sat 13:50 look cupboard_k1: bowl_shared_2
d05 Sat 13:50 look dish_rack_k1: mug_shared_1, plate_shared_1
d05 Sat 13:50 look kitchen_table_k1: charger_mara, glasses_mara, headphones_mara, mug_mara, notebook_mara
d05 Sat 13:50 look sink_k1: book_mara, plate_shared_2, pot_shared_1, watering_can_mara
d05 Sat 16:41 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d05 Sat 16:41 look towel_rack_ba1: (nothing)
d05 Sat 17:43 look sink_k1: plate_shared_2, pot_shared_1, watering_can_mara
d05 Sat 18:55 look entry_hook_e1: backpack_mara
d05 Sat 19:14 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d05 Sat 19:37 look entry_floor_e1: umbrella_mara
d05 Sat 19:37 look entry_hook_e1: backpack_mara
d05 Sat 19:37 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d05 Sat 20:15 look cupboard_k1: bowl_shared_2
d05 Sat 21:29 look counter_k1: lunchbox_mara, pan_shared_1, pen_mara, phone_mara, tablet_mara, water_bottle_mara
d05 Sat 22:20 look bed_b1: (nothing)
d05 Sat 22:20 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, towel_mara, vacuum_cleaner_shared_1
d05 Sat 22:20 look desk_b1: (nothing)
d05 Sat 22:20 look nightstand_b1: book_mara
d05 Sat 22:25 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d05 Sat 22:37 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d06 Sun 07:02 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d06 Sun 07:51 look armchair_l1: (nothing)
d06 Sun 07:51 look bookshelf_l1: laptop_mara
d06 Sun 07:51 look coffee_table_l1: remote_shared_1
d06 Sun 07:51 look couch_l1: blanket_mara, yoga_mat_mara
d06 Sun 07:51 look tv_stand_l1: (nothing)
d06 Sun 08:20 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, notebook_mara, pan_shared_1
d06 Sun 08:40 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1
d06 Sun 10:22 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d06 Sun 10:29 look entry_hook_e1: backpack_mara
d06 Sun 10:57 look chair_k1: (nothing)
d06 Sun 10:57 look chair_k2: mug_mara
d06 Sun 10:57 look counter_k1: lunchbox_mara, pen_mara, plate_shared_2, tablet_mara, water_bottle_mara
d06 Sun 10:57 look cupboard_k1: (nothing)
d06 Sun 10:57 look dish_rack_k1: mug_shared_1
d06 Sun 10:57 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara, laptop_mara, notebook_mara, pan_shared_1
d06 Sun 10:57 look sink_k1: plate_shared_1, pot_shared_1, watering_can_mara
d06 Sun 13:01 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d06 Sun 13:01 look entry_hook_e1: backpack_mara
d06 Sun 13:29 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d06 Sun 13:29 look towel_rack_ba1: (nothing)
d06 Sun 14:35 look counter_k1: pen_mara, tablet_mara
d06 Sun 15:34 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d06 Sun 16:21 look entry_floor_e1: umbrella_mara
d06 Sun 16:21 look entry_hook_e1: backpack_mara
d06 Sun 16:21 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d06 Sun 19:21 look bed_b1: (nothing)
d06 Sun 19:21 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d06 Sun 19:21 look desk_b1: (nothing)
d06 Sun 19:21 look nightstand_b1: phone_mara
d06 Sun 21:58 look armchair_l1: glasses_mara
d06 Sun 21:58 look bookshelf_l1: jacket_mara, lunchbox_mara
d06 Sun 21:58 look coffee_table_l1: mug_mara, remote_shared_1
d06 Sun 21:58 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d06 Sun 21:58 look tv_stand_l1: (nothing)
d06 Sun 22:37 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d07 Mon 04:52 look counter_k1: pen_mara, tablet_mara
d07 Mon 05:07 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara, laptop_mara, notebook_mara, pan_shared_1
d07 Mon 06:13 look chair_k1: (nothing)
d07 Mon 06:13 look chair_k2: (nothing)
d07 Mon 06:13 look counter_k1: pen_mara, tablet_mara
d07 Mon 06:13 look cupboard_k1: (nothing)
d07 Mon 06:13 look dish_rack_k1: mug_shared_1
d07 Mon 06:13 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara, laptop_mara, mug_mara, notebook_mara, pan_shared_1
d07 Mon 06:13 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d07 Mon 08:11 look coffee_table_l1: remote_shared_1
d07 Mon 08:16 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara, water_bottle_mara
d07 Mon 08:50 look cupboard_k1: (nothing)
d07 Mon 08:50 look kitchen_table_k1: mug_mara
d07 Mon 09:12 look entry_table_e1: bowl_shared_1
d07 Mon 09:23 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara, water_bottle_mara
d07 Mon 09:23 look towel_rack_ba1: towel_mara
d07 Mon 11:21 look kitchen_table_k1: mug_mara
d07 Mon 11:21 look counter_k1: pan_shared_1, pen_mara, tablet_mara
d07 Mon 12:26 look dish_rack_k1: mug_shared_1
d07 Mon 12:35 look entry_floor_e1: umbrella_mara
d07 Mon 12:35 look entry_hook_e1: (nothing)
d07 Mon 12:35 look entry_table_e1: bowl_shared_1
d07 Mon 13:59 look sink_k1: bowl_shared_2, plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d07 Mon 14:01 look bookshelf_l1: (nothing)
d07 Mon 14:01 look kitchen_table_k1: mug_mara
d07 Mon 14:01 look counter_k1: pan_shared_1, pen_mara, tablet_mara
d07 Mon 14:01 look sink_k1: bowl_shared_2, plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d07 Mon 14:01 look cupboard_k1: (nothing)
d07 Mon 15:53 look bed_b1: (nothing)
d07 Mon 15:53 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d07 Mon 15:53 look desk_b1: (nothing)
d07 Mon 15:53 look nightstand_b1: (nothing)
d07 Mon 16:00 look kitchen_table_k1: mug_mara
d07 Mon 16:00 look counter_k1: pan_shared_1, pen_mara, tablet_mara
d07 Mon 16:00 look sink_k1: bowl_shared_2, plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d07 Mon 16:00 look cupboard_k1: (nothing)
d07 Mon 16:00 look dish_rack_k1: mug_shared_1
d07 Mon 18:17 look entry_hook_e1: backpack_mara, jacket_mara
d07 Mon 18:57 look entry_floor_e1: umbrella_mara
d07 Mon 18:59 look armchair_l1: (nothing)
d07 Mon 18:59 look bookshelf_l1: (nothing)
d07 Mon 18:59 look coffee_table_l1: remote_shared_1
d07 Mon 18:59 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d07 Mon 18:59 look tv_stand_l1: (nothing)
d07 Mon 21:14 look sink_k1: bowl_shared_2, mug_mara, pan_shared_1, pot_shared_1, watering_can_mara
d07 Mon 22:18 look chair_k1: charger_mara, wallet_mara
d07 Mon 22:18 look chair_k2: (nothing)
d07 Mon 22:18 look counter_k1: lunchbox_mara, pen_mara, tablet_mara
d07 Mon 22:18 look cupboard_k1: (nothing)
d07 Mon 22:18 look dish_rack_k1: mug_shared_1, plate_shared_1
d07 Mon 22:18 look kitchen_table_k1: glasses_mara, headphones_mara, laptop_mara, notebook_mara, phone_mara, plate_shared_2
d07 Mon 22:18 look sink_k1: bowl_shared_2, mug_mara, pan_shared_1, pot_shared_1, watering_can_mara
d08 Tue 05:31 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d08 Tue 05:34 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d08 Tue 05:34 look counter_k1: lunchbox_mara, pen_mara, tablet_mara
d08 Tue 05:34 look sink_k1: bowl_shared_2, mug_mara, pan_shared_1, pot_shared_1, watering_can_mara
d08 Tue 05:34 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d08 Tue 06:38 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d08 Tue 06:38 look towel_rack_ba1: towel_mara
d08 Tue 06:48 look kitchen_table_k1: bowl_shared_2, glasses_mara, headphones_mara, laptop_mara, notebook_mara, pan_shared_1, pen_mara
d08 Tue 06:48 look sink_k1: plate_shared_2, pot_shared_1, watering_can_mara
d08 Tue 07:34 look entry_hook_e1: (nothing)
d08 Tue 09:38 look entry_floor_e1: umbrella_mara
d08 Tue 09:38 look entry_hook_e1: (nothing)
d08 Tue 09:38 look entry_table_e1: bowl_shared_1
d08 Tue 11:30 look dish_rack_k1: mug_shared_1, plate_shared_1
d08 Tue 12:49 look bed_b1: (nothing)
d08 Tue 12:49 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d08 Tue 12:49 look desk_b1: (nothing)
d08 Tue 12:49 look nightstand_b1: water_bottle_mara
d08 Tue 15:11 look sink_k1: plate_shared_2, pot_shared_1, watering_can_mara
d08 Tue 15:35 look counter_k1: mug_mara, tablet_mara
d08 Tue 15:57 look armchair_l1: (nothing)
d08 Tue 15:57 look bookshelf_l1: (nothing)
d08 Tue 15:57 look coffee_table_l1: remote_shared_1
d08 Tue 15:57 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d08 Tue 15:57 look tv_stand_l1: (nothing)
d08 Tue 16:01 look entry_hook_e1: (nothing)
d08 Tue 16:06 look dish_rack_k1: mug_shared_1, plate_shared_1
d08 Tue 18:23 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, laptop_mara, notebook_mara, pan_shared_1, pen_mara, plate_shared_1
d08 Tue 18:23 look entry_table_e1: bowl_shared_1
d08 Tue 18:23 look chair_k1: jacket_mara
d08 Tue 18:23 look counter_k1: lunchbox_mara, mug_mara, tablet_mara
d08 Tue 18:23 look sink_k1: headphones_mara, plate_shared_2, pot_shared_1, watering_can_mara
d08 Tue 19:22 look chair_k1: jacket_mara
d08 Tue 19:22 look chair_k2: wallet_mara
d08 Tue 19:22 look counter_k1: lunchbox_mara, mug_mara, tablet_mara
d08 Tue 19:22 look cupboard_k1: (nothing)
d08 Tue 19:22 look dish_rack_k1: mug_shared_1
d08 Tue 19:22 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, laptop_mara, notebook_mara, pan_shared_1, pen_mara, plate_shared_1
d08 Tue 19:22 look sink_k1: headphones_mara, plate_shared_2, pot_shared_1, watering_can_mara
d08 Tue 21:34 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara
d08 Tue 22:19 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, laptop_mara, notebook_mara, pan_shared_1, pen_mara, plate_shared_1
d08 Tue 22:29 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara
d08 Tue 22:29 look towel_rack_ba1: towel_mara
d09 Wed 00:24 look dish_rack_k1: mug_shared_1
d09 Wed 05:57 look entry_floor_e1: umbrella_mara
d09 Wed 05:57 look entry_hook_e1: backpack_mara, keys_mara
d09 Wed 05:57 look entry_table_e1: bowl_shared_1
d09 Wed 06:53 look chair_k2: (nothing)
d09 Wed 06:53 look chair_k1: (nothing)
d09 Wed 06:53 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, notebook_mara, pan_shared_1, plate_shared_1
d09 Wed 06:53 look counter_k1: pen_mara, tablet_mara
d09 Wed 06:53 look cupboard_k1: (nothing)
d09 Wed 06:53 look sink_k1: plate_shared_2, pot_shared_1, watering_can_mara
d09 Wed 07:58 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d09 Wed 08:46 look towel_rack_ba1: towel_mara
d09 Wed 08:56 look sink_k1: plate_shared_2, pot_shared_1, watering_can_mara
d09 Wed 08:56 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, notebook_mara, pan_shared_1, plate_shared_1
d09 Wed 09:12 look bed_b1: (nothing)
d09 Wed 09:12 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d09 Wed 09:12 look desk_b1: (nothing)
d09 Wed 09:12 look nightstand_b1: (nothing)
d09 Wed 10:37 look sink_k1: plate_shared_2, pot_shared_1, watering_can_mara
d09 Wed 10:59 look counter_k1: pen_mara, tablet_mara
d09 Wed 10:59 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, notebook_mara, pan_shared_1, plate_shared_1
d09 Wed 11:54 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d09 Wed 11:54 look counter_k1: pen_mara, tablet_mara
d09 Wed 11:54 look sink_k1: plate_shared_2, pot_shared_1, watering_can_mara
d09 Wed 11:54 look nightstand_b1: (nothing)
d09 Wed 11:54 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d09 Wed 12:36 look armchair_l1: (nothing)
d09 Wed 12:36 look bookshelf_l1: (nothing)
d09 Wed 12:36 look coffee_table_l1: remote_shared_1
d09 Wed 12:36 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d09 Wed 12:36 look tv_stand_l1: (nothing)
d09 Wed 13:03 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, notebook_mara, pan_shared_1, plate_shared_1
d09 Wed 13:19 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, notebook_mara, pan_shared_1, plate_shared_1
d09 Wed 13:19 look nightstand_b1: (nothing)
d09 Wed 14:48 look counter_k1: pen_mara, tablet_mara
d09 Wed 15:54 look chair_k2: (nothing)
d09 Wed 15:58 look chair_k1: backpack_mara, jacket_mara
d09 Wed 15:58 look chair_k2: (nothing)
d09 Wed 15:58 look counter_k1: pen_mara, tablet_mara
d09 Wed 15:58 look cupboard_k1: (nothing)
d09 Wed 15:58 look dish_rack_k1: mug_shared_1
d09 Wed 15:58 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara, mug_mara, notebook_mara, pan_shared_1, plate_shared_1, plate_shared_2, water_bottle_mara
d09 Wed 15:58 look sink_k1: lunchbox_mara, pot_shared_1, watering_can_mara
d09 Wed 19:12 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d09 Wed 19:12 look towel_rack_ba1: towel_mara
d09 Wed 22:15 look entry_floor_e1: umbrella_mara
d09 Wed 22:15 look entry_hook_e1: (nothing)
d09 Wed 22:15 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d10 Thu 04:42 look sink_k1: pan_shared_1, plate_shared_1, pot_shared_1, watering_can_mara
d10 Thu 04:42 look counter_k1: lunchbox_mara, pen_mara, tablet_mara
d10 Thu 04:43 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara, mug_mara, notebook_mara, plate_shared_2
d10 Thu 04:46 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara, mug_mara, notebook_mara, plate_shared_2
d10 Thu 04:46 look sink_k1: pan_shared_1, plate_shared_1, pot_shared_1, watering_can_mara
d10 Thu 05:00 look bathroom_shelf_ba1: makeup_kit_mara
d10 Thu 05:20 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d10 Thu 06:10 look bed_b1: (nothing)
d10 Thu 06:10 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d10 Thu 06:10 look desk_b1: (nothing)
d10 Thu 06:10 look nightstand_b1: water_bottle_mara
d10 Thu 06:30 look sink_k1: bowl_shared_2, plate_shared_1, pot_shared_1, watering_can_mara
d10 Thu 07:18 look entry_hook_e1: (nothing)
d10 Thu 07:53 look kitchen_table_k1: laptop_mara, mug_mara, pan_shared_1, pen_mara
d10 Thu 07:53 look nightstand_b1: (nothing)
d10 Thu 07:53 look counter_k1: plate_shared_2, tablet_mara
d10 Thu 08:32 look entry_hook_e1: (nothing)
d10 Thu 09:33 look armchair_l1: (nothing)
d10 Thu 09:33 look bookshelf_l1: (nothing)
d10 Thu 09:33 look coffee_table_l1: (nothing)
d10 Thu 09:33 look couch_l1: blanket_mara, book_mara, remote_shared_1, yoga_mat_mara
d10 Thu 09:33 look tv_stand_l1: (nothing)
d10 Thu 09:38 look towel_rack_ba1: towel_mara
d10 Thu 10:11 look kitchen_table_k1: laptop_mara, mug_mara, pan_shared_1, pen_mara
d10 Thu 10:11 look nightstand_b1: (nothing)
d10 Thu 10:11 look counter_k1: plate_shared_2, tablet_mara
d10 Thu 11:10 look entry_hook_e1: (nothing)
d10 Thu 11:10 look chair_k1: backpack_mara
d10 Thu 12:05 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d10 Thu 12:39 look chair_k1: backpack_mara
d10 Thu 12:39 look chair_k2: (nothing)
d10 Thu 12:39 look counter_k1: plate_shared_2, tablet_mara
d10 Thu 12:39 look cupboard_k1: (nothing)
d10 Thu 12:39 look dish_rack_k1: mug_shared_1
d10 Thu 12:39 look kitchen_table_k1: laptop_mara, mug_mara, pan_shared_1, pen_mara
d10 Thu 12:39 look sink_k1: bowl_shared_2, plate_shared_1, pot_shared_1, watering_can_mara
d10 Thu 12:56 look kitchen_table_k1: laptop_mara, mug_mara, pan_shared_1, pen_mara
d10 Thu 12:56 look nightstand_b1: (nothing)
d10 Thu 13:27 look sink_k1: bowl_shared_2, plate_shared_1, pot_shared_1, watering_can_mara
d10 Thu 13:27 look counter_k1: plate_shared_2, tablet_mara
d10 Thu 15:48 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara, medication_bottle_mara, notebook_mara, phone_mara
d10 Thu 15:48 look towel_rack_ba1: towel_mara, wallet_mara, water_bottle_mara
d10 Thu 19:16 look entry_floor_e1: umbrella_mara
d10 Thu 19:16 look entry_hook_e1: charger_mara, jacket_mara
d10 Thu 19:16 look entry_table_e1: bowl_shared_1, keys_mara
d10 Thu 22:24 look bed_b1: (nothing)
d10 Thu 22:24 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d10 Thu 22:24 look desk_b1: (nothing)
d10 Thu 22:24 look nightstand_b1: water_bottle_mara
d11 Fri 05:33 look sink_k1: bowl_shared_2, plate_shared_1, pot_shared_1, watering_can_mara
d11 Fri 06:19 look dish_rack_k1: mug_shared_1
d11 Fri 06:33 look armchair_l1: (nothing)
d11 Fri 06:33 look bookshelf_l1: (nothing)
d11 Fri 06:33 look coffee_table_l1: (nothing)
d11 Fri 06:33 look couch_l1: blanket_mara, book_mara, remote_shared_1, yoga_mat_mara
d11 Fri 06:33 look tv_stand_l1: (nothing)
d11 Fri 06:48 look entry_table_e1: bowl_shared_1, keys_mara
d11 Fri 06:48 look chair_k2: (nothing)
d11 Fri 06:48 look counter_k1: lunchbox_mara, medication_bottle_mara, pan_shared_1, pen_mara, plate_shared_2, tablet_mara
d11 Fri 06:48 look entry_hook_e1: charger_mara, jacket_mara
d11 Fri 06:48 look kitchen_table_k1: bowl_shared_2, glasses_mara, laptop_mara, mug_mara
d11 Fri 06:56 look towel_rack_ba1: towel_mara, wallet_mara
d11 Fri 08:02 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara, notebook_mara
d11 Fri 08:05 look sink_k1: plate_shared_1, pot_shared_1, watering_can_mara
d11 Fri 08:33 look chair_k1: backpack_mara
d11 Fri 08:33 look chair_k2: (nothing)
d11 Fri 08:33 look counter_k1: charger_mara, lunchbox_mara, medication_bottle_mara, pan_shared_1, pen_mara, plate_shared_2, tablet_mara
d11 Fri 08:33 look cupboard_k1: (nothing)
d11 Fri 08:33 look dish_rack_k1: mug_shared_1
d11 Fri 08:33 look kitchen_table_k1: bowl_shared_2, glasses_mara, laptop_mara, mug_mara, notebook_mara
d11 Fri 08:33 look sink_k1: plate_shared_1, pot_shared_1, watering_can_mara
d11 Fri 08:38 look sink_k1: plate_shared_1, pot_shared_1, watering_can_mara
d11 Fri 08:54 look dish_rack_k1: mug_shared_1
d11 Fri 10:06 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara
d11 Fri 10:06 look nightstand_b1: phone_mara, water_bottle_mara
d11 Fri 10:57 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara
d11 Fri 10:57 look towel_rack_ba1: towel_mara, wallet_mara
d11 Fri 14:12 look counter_k1: lunchbox_mara, medication_bottle_mara, pan_shared_1, pen_mara, tablet_mara
d11 Fri 14:32 look entry_floor_e1: umbrella_mara
d11 Fri 14:32 look entry_hook_e1: jacket_mara
d11 Fri 14:32 look entry_table_e1: bowl_shared_1, keys_mara
d11 Fri 14:57 look sink_k1: plate_shared_1, pot_shared_1, watering_can_mara
d11 Fri 15:00 look towel_rack_ba1: towel_mara, wallet_mara
d11 Fri 16:20 look counter_k1: lunchbox_mara, pan_shared_1, pen_mara, plate_shared_2, tablet_mara
d11 Fri 16:20 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara, medication_bottle_mara
d11 Fri 16:50 look bed_b1: (nothing)
d11 Fri 16:50 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d11 Fri 16:50 look desk_b1: (nothing)
d11 Fri 16:50 look nightstand_b1: glasses_mara, phone_mara, water_bottle_mara
d11 Fri 17:04 look sink_k1: pot_shared_1, watering_can_mara
d11 Fri 17:20 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, plate_shared_1
d11 Fri 18:50 look armchair_l1: (nothing)
d11 Fri 18:50 look bookshelf_l1: (nothing)
d11 Fri 18:50 look coffee_table_l1: notebook_mara, remote_shared_1
d11 Fri 18:50 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d11 Fri 18:50 look tv_stand_l1: (nothing)
d11 Fri 19:09 look counter_k1: lunchbox_mara, pan_shared_1, pen_mara, plate_shared_2, tablet_mara
d12 Sat 06:18 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, plate_shared_1
d12 Sat 06:25 look towel_rack_ba1: towel_mara, wallet_mara
d12 Sat 06:31 look entry_table_e1: bowl_shared_1, keys_mara
d12 Sat 06:53 look dish_rack_k1: mug_shared_1
d12 Sat 07:19 look cupboard_k1: charger_mara
d12 Sat 07:27 look chair_k1: backpack_mara
d12 Sat 07:27 look chair_k2: (nothing)
d12 Sat 07:27 look counter_k1: lunchbox_mara, mug_mara, pan_shared_1, pen_mara, plate_shared_2, tablet_mara
d12 Sat 07:27 look cupboard_k1: charger_mara
d12 Sat 07:27 look dish_rack_k1: mug_shared_1
d12 Sat 07:27 look kitchen_table_k1: bowl_shared_2, laptop_mara, plate_shared_1
d12 Sat 07:27 look sink_k1: pot_shared_1, watering_can_mara
d12 Sat 07:45 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara, medication_bottle_mara
d12 Sat 08:43 look sink_k1: pot_shared_1, watering_can_mara
d12 Sat 08:47 look nightstand_b1: glasses_mara, phone_mara, water_bottle_mara
d12 Sat 10:35 look counter_k1: lunchbox_mara, pan_shared_1, pen_mara, plate_shared_2, tablet_mara
d12 Sat 11:03 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara, medication_bottle_mara
d12 Sat 11:03 look towel_rack_ba1: towel_mara, wallet_mara
d12 Sat 13:01 look sink_k1: plate_shared_2, watering_can_mara
d12 Sat 14:04 look entry_floor_e1: umbrella_mara
d12 Sat 14:04 look entry_hook_e1: backpack_mara, jacket_mara
d12 Sat 14:04 look entry_table_e1: bowl_shared_1, keys_mara
d12 Sat 14:21 look kitchen_table_k1: bowl_shared_2, laptop_mara, pen_mara
d12 Sat 14:21 look sink_k1: plate_shared_2, watering_can_mara
d12 Sat 15:11 look dish_rack_k1: mug_shared_1, plate_shared_1
d12 Sat 16:46 look bed_b1: (nothing)
d12 Sat 16:46 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d12 Sat 16:46 look desk_b1: (nothing)
d12 Sat 16:46 look nightstand_b1: glasses_mara, phone_mara, water_bottle_mara
d12 Sat 19:28 look sink_k1: plate_shared_1, plate_shared_2, watering_can_mara
d12 Sat 19:40 look armchair_l1: (nothing)
d12 Sat 19:40 look bookshelf_l1: (nothing)
d12 Sat 19:40 look coffee_table_l1: notebook_mara
d12 Sat 19:40 look couch_l1: blanket_mara, book_mara, remote_shared_1, yoga_mat_mara
d12 Sat 19:40 look tv_stand_l1: (nothing)
d12 Sat 21:20 look bathroom_shelf_ba1: headphones_mara, makeup_kit_mara, medication_bottle_mara
d12 Sat 21:24 look dish_rack_k1: mug_shared_1
d12 Sat 22:29 look chair_k1: (nothing)
d12 Sat 22:29 look chair_k2: mug_mara
d12 Sat 22:29 look counter_k1: lunchbox_mara, tablet_mara
d12 Sat 22:29 look cupboard_k1: charger_mara, pot_shared_1
d12 Sat 22:29 look dish_rack_k1: mug_shared_1
d12 Sat 22:29 look kitchen_table_k1: bowl_shared_2, laptop_mara, pan_shared_1, pen_mara
d12 Sat 22:29 look sink_k1: plate_shared_1, plate_shared_2, watering_can_mara
d12 Sat 23:15 look bathroom_shelf_ba1: headphones_mara, makeup_kit_mara, medication_bottle_mara
d13 Sun 07:40 look sink_k1: plate_shared_1, plate_shared_2, watering_can_mara
d13 Sun 08:19 look bathroom_shelf_ba1: makeup_kit_mara, medication_bottle_mara
d13 Sun 08:19 look towel_rack_ba1: hairbrush_mara
d13 Sun 09:16 look cupboard_k1: charger_mara, pot_shared_1
d13 Sun 10:09 look couch_l1: blanket_mara, book_mara, remote_shared_1, yoga_mat_mara
d13 Sun 10:09 look entry_hook_e1: jacket_mara
d13 Sun 10:47 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d13 Sun 10:51 look sink_k1: mug_mara, pan_shared_1, plate_shared_1, pot_shared_1, watering_can_mara
d13 Sun 10:54 look nightstand_b1: phone_mara, water_bottle_mara
d13 Sun 11:00 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pen_mara, plate_shared_2
d13 Sun 11:09 look entry_floor_e1: umbrella_mara
d13 Sun 11:09 look entry_hook_e1: jacket_mara
d13 Sun 11:09 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d13 Sun 13:54 look bed_b1: (nothing)
d13 Sun 13:54 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, towel_mara, vacuum_cleaner_shared_1
d13 Sun 13:54 look desk_b1: (nothing)
d13 Sun 13:54 look nightstand_b1: phone_mara, water_bottle_mara
d13 Sun 14:34 look sink_k1: pan_shared_1, watering_can_mara
d13 Sun 14:34 look dish_rack_k1: mug_shared_1, plate_shared_1, pot_shared_1
d13 Sun 14:41 look counter_k1: lunchbox_mara, tablet_mara
d13 Sun 16:36 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pen_mara, plate_shared_2
d13 Sun 16:43 look chair_k1: backpack_mara
d13 Sun 16:53 look armchair_l1: jacket_mara
d13 Sun 16:53 look bookshelf_l1: (nothing)
d13 Sun 16:53 look coffee_table_l1: book_mara, glasses_mara, notebook_mara
d13 Sun 16:53 look couch_l1: blanket_mara, mug_mara, remote_shared_1, yoga_mat_mara
d13 Sun 16:53 look tv_stand_l1: (nothing)
d13 Sun 18:28 look counter_k1: lunchbox_mara, tablet_mara
d13 Sun 19:06 look sink_k1: watering_can_mara
d13 Sun 19:14 look sink_k1: watering_can_mara
d13 Sun 19:50 look chair_k1: backpack_mara
d13 Sun 19:50 look chair_k2: (nothing)
d13 Sun 19:50 look counter_k1: lunchbox_mara, pan_shared_1, tablet_mara
d13 Sun 19:50 look cupboard_k1: charger_mara
d13 Sun 19:50 look dish_rack_k1: mug_shared_1, pot_shared_1
d13 Sun 19:50 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pen_mara, plate_shared_1, plate_shared_2
d13 Sun 19:50 look sink_k1: watering_can_mara
d13 Sun 20:36 look bathroom_shelf_ba1: makeup_kit_mara, medication_bottle_mara
d13 Sun 22:27 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d13 Sun 22:27 look towel_rack_ba1: (nothing)
d13 Sun 23:11 look sink_k1: watering_can_mara
d13 Sun 23:28 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d14 Mon 05:18 look sink_k1: watering_can_mara
d14 Mon 05:24 look cupboard_k1: charger_mara
d14 Mon 05:43 look sink_k1: watering_can_mara
d14 Mon 06:14 look entry_floor_e1: umbrella_mara
d14 Mon 06:14 look entry_hook_e1: (nothing)
d14 Mon 06:14 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d14 Mon 06:33 look dish_rack_k1: mug_shared_1, pot_shared_1
d14 Mon 07:35 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d14 Mon 07:38 look counter_k1: lunchbox_mara, mug_mara, pen_mara, tablet_mara
d14 Mon 09:28 look bed_b1: (nothing)
d14 Mon 09:28 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d14 Mon 09:28 look desk_b1: (nothing)
d14 Mon 09:28 look nightstand_b1: (nothing)
d14 Mon 09:33 look sink_k1: bowl_shared_2, plate_shared_2, watering_can_mara
d14 Mon 09:40 look nightstand_b1: (nothing)
d14 Mon 10:17 look entry_hook_e1: (nothing)
d14 Mon 11:26 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d14 Mon 12:41 look armchair_l1: (nothing)
d14 Mon 12:41 look bookshelf_l1: (nothing)
d14 Mon 12:41 look coffee_table_l1: book_mara, notebook_mara
d14 Mon 12:41 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d14 Mon 12:41 look tv_stand_l1: (nothing)
d14 Mon 13:04 look sink_k1: bowl_shared_2, plate_shared_2, watering_can_mara
d14 Mon 13:11 look dish_rack_k1: mug_shared_1, pot_shared_1
d14 Mon 15:36 look kitchen_table_k1: pan_shared_1, plate_shared_1
d14 Mon 15:50 look chair_k1: backpack_mara
d14 Mon 15:50 look chair_k2: (nothing)
d14 Mon 15:50 look counter_k1: lunchbox_mara, mug_mara, pen_mara, tablet_mara
d14 Mon 15:50 look cupboard_k1: (nothing)
d14 Mon 15:50 look dish_rack_k1: mug_shared_1, pot_shared_1
d14 Mon 15:50 look kitchen_table_k1: pan_shared_1, plate_shared_1
d14 Mon 15:50 look sink_k1: bowl_shared_2, plate_shared_2, watering_can_mara
d14 Mon 16:43 look towel_rack_ba1: towel_mara
d14 Mon 19:01 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d14 Mon 19:03 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d14 Mon 19:03 look towel_rack_ba1: towel_mara
d14 Mon 21:43 look kitchen_table_k1: charger_mara, glasses_mara, laptop_mara, water_bottle_mara
d14 Mon 22:32 look entry_floor_e1: umbrella_mara
d14 Mon 22:32 look entry_hook_e1: headphones_mara
d14 Mon 22:32 look entry_table_e1: keys_mara, wallet_mara
d14 Mon 23:51 look nightstand_b1: book_mara
d15 Tue 04:36 look sink_k1: bowl_shared_2, pan_shared_1, plate_shared_1, plate_shared_2, watering_can_mara
d15 Tue 05:29 look bathroom_shelf_ba1: makeup_kit_mara, medication_bottle_mara
d15 Tue 05:43 look bed_b1: (nothing)
d15 Tue 05:43 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d15 Tue 05:43 look desk_b1: (nothing)
d15 Tue 05:43 look nightstand_b1: book_mara
d15 Tue 06:04 look nightstand_b1: book_mara
d15 Tue 06:05 look entry_hook_e1: headphones_mara
d15 Tue 07:12 look counter_k1: bowl_shared_1, lunchbox_mara, pan_shared_1, plate_shared_2, tablet_mara
d15 Tue 08:24 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d15 Tue 08:34 look nightstand_b1: book_mara
d15 Tue 08:44 look dish_rack_k1: mug_shared_1, pot_shared_1
d15 Tue 09:07 look armchair_l1: (nothing)
d15 Tue 09:07 look bookshelf_l1: (nothing)
d15 Tue 09:07 look coffee_table_l1: (nothing)
d15 Tue 09:07 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d15 Tue 09:07 look tv_stand_l1: (nothing)
d15 Tue 09:48 look sink_k1: plate_shared_1, watering_can_mara
d15 Tue 10:16 look counter_k1: bowl_shared_1, lunchbox_mara, pan_shared_1, plate_shared_2, tablet_mara
d15 Tue 11:44 look sink_k1: plate_shared_1, watering_can_mara
d15 Tue 12:19 look chair_k1: (nothing)
d15 Tue 12:19 look chair_k2: (nothing)
d15 Tue 12:19 look counter_k1: bowl_shared_1, lunchbox_mara, pan_shared_1, plate_shared_2, tablet_mara
d15 Tue 12:19 look cupboard_k1: (nothing)
d15 Tue 12:19 look dish_rack_k1: mug_shared_1, pot_shared_1
d15 Tue 12:19 look kitchen_table_k1: bowl_shared_2, mug_mara, pen_mara
d15 Tue 12:19 look sink_k1: plate_shared_1, watering_can_mara
d15 Tue 13:07 look dish_rack_k1: mug_shared_1, pot_shared_1
d15 Tue 13:49 look towel_rack_ba1: towel_mara
d15 Tue 15:47 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d15 Tue 15:47 look towel_rack_ba1: towel_mara
d15 Tue 15:49 look sink_k1: plate_shared_1, watering_can_mara
d15 Tue 17:22 look chair_k1: jacket_mara, laptop_mara
d15 Tue 17:24 look counter_k1: bowl_shared_1, lunchbox_mara, tablet_mara
d15 Tue 18:16 look entry_table_e1: (nothing)
d15 Tue 18:58 look entry_floor_e1: umbrella_mara
d15 Tue 18:58 look entry_hook_e1: backpack_mara, charger_mara
d15 Tue 18:58 look entry_table_e1: (nothing)
d15 Tue 21:26 look kitchen_table_k1: bowl_shared_2, glasses_mara, headphones_mara, mug_mara, notebook_mara, pen_mara, plate_shared_1, plate_shared_2, water_bottle_mara
d15 Tue 21:31 look sink_k1: wallet_mara, watering_can_mara
d15 Tue 22:17 look bed_b1: (nothing)
d15 Tue 22:17 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d15 Tue 22:17 look desk_b1: (nothing)
d15 Tue 22:17 look nightstand_b1: book_mara, water_bottle_mara
d16 Wed 04:54 look kitchen_table_k1: bowl_shared_2, glasses_mara, headphones_mara, mug_mara, notebook_mara, pen_mara, plate_shared_1, plate_shared_2
d16 Wed 05:13 look sink_k1: wallet_mara, watering_can_mara
d16 Wed 05:17 look dish_rack_k1: mug_shared_1, pot_shared_1
d16 Wed 05:24 look armchair_l1: (nothing)
d16 Wed 05:24 look bookshelf_l1: (nothing)
d16 Wed 05:24 look coffee_table_l1: (nothing)
d16 Wed 05:24 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d16 Wed 05:24 look tv_stand_l1: (nothing)
d16 Wed 05:26 look chair_k1: jacket_mara, laptop_mara
d16 Wed 05:41 look sink_k1: wallet_mara, watering_can_mara
d16 Wed 07:20 look towel_rack_ba1: towel_mara
d16 Wed 07:37 look counter_k1: bowl_shared_1, mug_mara, pen_mara, plate_shared_2, tablet_mara
d16 Wed 07:37 look entry_table_e1: (nothing)
d16 Wed 07:37 look entry_hook_e1: charger_mara
d16 Wed 08:50 look chair_k1: (nothing)
d16 Wed 08:50 look chair_k2: (nothing)
d16 Wed 08:50 look counter_k1: bowl_shared_1, mug_mara, pen_mara, plate_shared_2, tablet_mara
d16 Wed 08:50 look cupboard_k1: (nothing)
d16 Wed 08:50 look dish_rack_k1: mug_shared_1, pot_shared_1
d16 Wed 08:50 look kitchen_table_k1: pan_shared_1, plate_shared_1
d16 Wed 08:50 look sink_k1: bowl_shared_2, watering_can_mara
d16 Wed 08:54 look nightstand_b1: book_mara
d16 Wed 09:53 look dish_rack_k1: mug_shared_1, pot_shared_1
d16 Wed 12:00 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d16 Wed 12:00 look towel_rack_ba1: towel_mara
d16 Wed 13:24 look counter_k1: bowl_shared_1, mug_mara, pen_mara, plate_shared_2, tablet_mara
d16 Wed 14:15 look sink_k1: bowl_shared_2, watering_can_mara
d16 Wed 15:26 look entry_floor_e1: umbrella_mara
d16 Wed 15:26 look entry_hook_e1: charger_mara
d16 Wed 15:26 look entry_table_e1: (nothing)
d16 Wed 16:42 look kitchen_table_k1: laptop_mara, notebook_mara, pan_shared_1, phone_mara, plate_shared_1
d16 Wed 16:54 look sink_k1: bowl_shared_2, plate_shared_2, watering_can_mara
d16 Wed 18:48 look bed_b1: (nothing)
d16 Wed 18:48 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d16 Wed 18:48 look desk_b1: (nothing)
d16 Wed 18:48 look nightstand_b1: book_mara, phone_mara
d16 Wed 20:43 look sink_k1: bowl_shared_2, pan_shared_1, plate_shared_1, plate_shared_2, watering_can_mara
d16 Wed 21:09 look dish_rack_k1: lunchbox_mara, mug_shared_1, pot_shared_1
d16 Wed 22:04 look armchair_l1: (nothing)
d16 Wed 22:04 look bookshelf_l1: (nothing)
d16 Wed 22:04 look coffee_table_l1: (nothing)
d16 Wed 22:04 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d16 Wed 22:04 look tv_stand_l1: (nothing)
d16 Wed 22:11 look entry_table_e1: keys_mara, wallet_mara
d16 Wed 23:07 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d17 Thu 05:35 look nightstand_b1: book_mara, phone_mara, water_bottle_mara
d17 Thu 05:39 look chair_k1: backpack_mara
d17 Thu 06:25 look bathroom_shelf_ba1: makeup_kit_mara
d17 Thu 06:27 look sink_k1: plate_shared_1, watering_can_mara
d17 Thu 06:36 look chair_k1: backpack_mara
d17 Thu 06:36 look chair_k2: glasses_mara
d17 Thu 06:36 look counter_k1: bowl_shared_1, medication_bottle_mara, mug_mara, pan_shared_1, pen_mara, plate_shared_2, tablet_mara
d17 Thu 06:36 look cupboard_k1: (nothing)
d17 Thu 06:36 look dish_rack_k1: lunchbox_mara, mug_shared_1, pot_shared_1
d17 Thu 06:36 look kitchen_table_k1: bowl_shared_2, laptop_mara, notebook_mara
d17 Thu 06:36 look sink_k1: plate_shared_1, watering_can_mara
d17 Thu 07:11 look entry_hook_e1: charger_mara, headphones_mara, jacket_mara
d17 Thu 09:06 look dish_rack_k1: mug_shared_1, pen_mara, pot_shared_1
d17 Thu 09:14 look counter_k1: bowl_shared_1, medication_bottle_mara, mug_mara, pan_shared_1, plate_shared_2, tablet_mara
d17 Thu 09:14 look dish_rack_k1: mug_shared_1, pen_mara, pot_shared_1
d17 Thu 09:52 look bathroom_shelf_ba1: makeup_kit_mara
d17 Thu 09:52 look towel_rack_ba1: towel_mara
d17 Thu 09:59 look sink_k1: plate_shared_1, watering_can_mara
d17 Thu 10:12 look bathroom_shelf_ba1: makeup_kit_mara
d17 Thu 11:07 look kitchen_table_k1: bowl_shared_2
d17 Thu 11:09 look sink_k1: plate_shared_1, watering_can_mara
d17 Thu 11:11 look kitchen_table_k1: bowl_shared_2
d17 Thu 11:11 look sink_k1: plate_shared_1, watering_can_mara
d17 Thu 11:17 look entry_table_e1: (nothing)
d17 Thu 11:29 look bathroom_shelf_ba1: makeup_kit_mara
d17 Thu 12:12 look counter_k1: bowl_shared_1, medication_bottle_mara, mug_mara, pan_shared_1, plate_shared_2, tablet_mara
d17 Thu 12:48 look entry_table_e1: (nothing)
d17 Thu 12:54 look entry_floor_e1: umbrella_mara
d17 Thu 12:54 look entry_hook_e1: (nothing)
d17 Thu 12:54 look entry_table_e1: (nothing)
d17 Thu 13:05 look entry_table_e1: (nothing)
d17 Thu 13:05 look sink_k1: plate_shared_1, watering_can_mara
d17 Thu 15:18 look dish_rack_k1: mug_shared_1, pen_mara, pot_shared_1
d17 Thu 16:12 look bathroom_shelf_ba1: makeup_kit_mara
d17 Thu 16:15 look bed_b1: (nothing)
d17 Thu 16:15 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d17 Thu 16:15 look desk_b1: (nothing)
d17 Thu 16:15 look nightstand_b1: book_mara, hairbrush_mara, water_bottle_mara
d17 Thu 16:30 look entry_hook_e1: backpack_mara, charger_mara
d17 Thu 16:41 look sink_k1: lunchbox_mara, plate_shared_1, plate_shared_2, water_bottle_mara, watering_can_mara
d17 Thu 19:18 look armchair_l1: (nothing)
d17 Thu 19:18 look bookshelf_l1: (nothing)
d17 Thu 19:18 look coffee_table_l1: glasses_mara
d17 Thu 19:18 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d17 Thu 19:18 look tv_stand_l1: mug_mara
d17 Thu 22:22 look chair_k1: jacket_mara
d17 Thu 22:22 look chair_k2: (nothing)
d17 Thu 22:22 look counter_k1: medication_bottle_mara, tablet_mara
d17 Thu 22:22 look cupboard_k1: headphones_mara
d17 Thu 22:22 look dish_rack_k1: mug_shared_1, pen_mara, pot_shared_1
d17 Thu 22:22 look kitchen_table_k1: bowl_shared_2, laptop_mara, notebook_mara, phone_mara, plate_shared_1
d17 Thu 22:22 look sink_k1: lunchbox_mara, pan_shared_1, plate_shared_2, water_bottle_mara, watering_can_mara
d18 Fri 05:20 look sink_k1: lunchbox_mara, pan_shared_1, plate_shared_2, water_bottle_mara, watering_can_mara
d18 Fri 06:03 look entry_hook_e1: backpack_mara, charger_mara
d18 Fri 06:28 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d18 Fri 06:28 look towel_rack_ba1: towel_mara
d18 Fri 08:22 look sink_k1: bowl_shared_2, watering_can_mara
d18 Fri 08:37 look kitchen_table_k1: pan_shared_1, pen_mara, plate_shared_1
d18 Fri 08:37 look nightstand_b1: book_mara
d18 Fri 09:09 look chair_k1: (nothing)
d18 Fri 09:31 look entry_floor_e1: umbrella_mara
d18 Fri 09:31 look entry_hook_e1: (nothing)
d18 Fri 09:31 look entry_table_e1: bowl_shared_1
d18 Fri 11:05 look kitchen_table_k1: pan_shared_1, pen_mara, plate_shared_1
d18 Fri 11:06 look entry_table_e1: bowl_shared_1
d18 Fri 11:25 look entry_hook_e1: (nothing)
d18 Fri 11:41 look counter_k1: mug_mara, plate_shared_2, tablet_mara
d18 Fri 11:53 look entry_table_e1: bowl_shared_1
d18 Fri 12:51 look bed_b1: (nothing)
d18 Fri 12:51 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d18 Fri 12:51 look desk_b1: (nothing)
d18 Fri 12:51 look nightstand_b1: book_mara
d18 Fri 13:06 look dish_rack_k1: mug_shared_1, pot_shared_1
d18 Fri 13:25 look sink_k1: bowl_shared_2, watering_can_mara
d18 Fri 15:56 look armchair_l1: (nothing)
d18 Fri 15:56 look bookshelf_l1: (nothing)
d18 Fri 15:56 look coffee_table_l1: (nothing)
d18 Fri 15:56 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d18 Fri 15:56 look tv_stand_l1: (nothing)
d18 Fri 16:22 look dish_rack_k1: mug_shared_1, phone_mara, pot_shared_1
d18 Fri 18:27 look cupboard_k1: glasses_mara
d18 Fri 19:11 look chair_k1: notebook_mara
d18 Fri 19:11 look chair_k2: (nothing)
d18 Fri 19:11 look counter_k1: mug_mara, pan_shared_1, plate_shared_2, tablet_mara
d18 Fri 19:11 look cupboard_k1: glasses_mara
d18 Fri 19:11 look dish_rack_k1: mug_shared_1, phone_mara, pot_shared_1
d18 Fri 19:11 look kitchen_table_k1: charger_mara, headphones_mara, laptop_mara, pen_mara, plate_shared_1, water_bottle_mara
d18 Fri 19:11 look sink_k1: bowl_shared_2, lunchbox_mara, watering_can_mara
d18 Fri 20:22 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d18 Fri 22:27 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d18 Fri 22:27 look towel_rack_ba1: towel_mara
d18 Fri 23:36 look sink_k1: bowl_shared_2, lunchbox_mara, watering_can_mara
d19 Sat 07:14 look dish_rack_k1: mug_shared_1, phone_mara, pot_shared_1
d19 Sat 07:27 look sink_k1: bowl_shared_2, lunchbox_mara, watering_can_mara
d19 Sat 07:49 look counter_k1: mug_mara, plate_shared_2, tablet_mara
d19 Sat 08:22 look entry_floor_e1: umbrella_mara
d19 Sat 08:22 look entry_hook_e1: backpack_mara, jacket_mara
d19 Sat 08:22 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d19 Sat 09:47 look kitchen_table_k1: charger_mara, laptop_mara, pen_mara, plate_shared_1
d19 Sat 09:47 look sink_k1: bowl_shared_2, lunchbox_mara, watering_can_mara
d19 Sat 10:34 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d19 Sat 11:17 look bed_b1: (nothing)
d19 Sat 11:17 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d19 Sat 11:17 look desk_b1: (nothing)
d19 Sat 11:17 look nightstand_b1: book_mara, phone_mara, water_bottle_mara
d19 Sat 12:05 look kitchen_table_k1: charger_mara, laptop_mara, pen_mara, plate_shared_2
d19 Sat 12:57 look dish_rack_k1: lunchbox_mara, mug_shared_1, plate_shared_1, pot_shared_1
d19 Sat 13:22 look sink_k1: bowl_shared_2, watering_can_mara
d19 Sat 14:10 look armchair_l1: (nothing)
d19 Sat 14:10 look bookshelf_l1: (nothing)
d19 Sat 14:10 look coffee_table_l1: headphones_mara, wallet_mara
d19 Sat 14:10 look couch_l1: blanket_mara, mug_mara, phone_mara, remote_shared_1, yoga_mat_mara
d19 Sat 14:10 look tv_stand_l1: tablet_mara
d19 Sat 16:47 look chair_k1: notebook_mara, umbrella_mara
d19 Sat 16:47 look chair_k2: (nothing)
d19 Sat 16:47 look counter_k1: pan_shared_1
d19 Sat 16:47 look cupboard_k1: (nothing)
d19 Sat 16:47 look dish_rack_k1: lunchbox_mara, mug_shared_1, plate_shared_1, pot_shared_1
d19 Sat 16:47 look kitchen_table_k1: charger_mara, glasses_mara, laptop_mara, pen_mara, plate_shared_2
d19 Sat 16:47 look sink_k1: bowl_shared_2, watering_can_mara
d19 Sat 16:50 look towel_rack_ba1: towel_mara
d19 Sat 18:00 look entry_hook_e1: backpack_mara, jacket_mara
d19 Sat 18:11 look entry_table_e1: bowl_shared_1, keys_mara
d19 Sat 19:30 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d19 Sat 19:38 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d19 Sat 19:38 look towel_rack_ba1: towel_mara
d19 Sat 21:19 look dish_rack_k1: lunchbox_mara, mug_shared_1, pot_shared_1
d19 Sat 22:30 look entry_floor_e1: (nothing)
d19 Sat 22:30 look entry_hook_e1: backpack_mara, jacket_mara
d19 Sat 22:30 look entry_table_e1: bowl_shared_1, keys_mara
d20 Sun 07:28 look bed_b1: (nothing)
d20 Sun 07:28 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d20 Sun 07:28 look desk_b1: (nothing)
d20 Sun 07:28 look nightstand_b1: hairbrush_mara, water_bottle_mara
d20 Sun 08:11 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, laptop_mara, pan_shared_1, pen_mara, plate_shared_1, plate_shared_2
d20 Sun 08:41 look towel_rack_ba1: (nothing)
d20 Sun 09:22 look entry_hook_e1: backpack_mara
d20 Sun 09:44 look sink_k1: watering_can_mara
d20 Sun 10:22 look armchair_l1: book_mara, jacket_mara
d20 Sun 10:22 look bookshelf_l1: remote_shared_1
d20 Sun 10:22 look coffee_table_l1: (nothing)
d20 Sun 10:22 look couch_l1: blanket_mara, headphones_mara, vacuum_cleaner_shared_1, yoga_mat_mara
d20 Sun 10:22 look tv_stand_l1: tablet_mara
d20 Sun 11:14 look bathroom_shelf_ba1: makeup_kit_mara, medication_bottle_mara
d20 Sun 12:32 look entry_floor_e1: (nothing)
d20 Sun 12:35 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, laptop_mara, pan_shared_1, pen_mara
d20 Sun 12:49 look counter_k1: lunchbox_mara
d20 Sun 13:02 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, laptop_mara, pan_shared_1, pen_mara
d20 Sun 13:04 look sink_k1: plate_shared_2, water_bottle_mara, watering_can_mara
d20 Sun 13:32 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d20 Sun 13:40 look chair_k1: backpack_mara, notebook_mara, umbrella_mara
d20 Sun 13:40 look chair_k2: (nothing)
d20 Sun 13:40 look counter_k1: lunchbox_mara
d20 Sun 13:40 look cupboard_k1: pot_shared_1
d20 Sun 13:40 look dish_rack_k1: mug_shared_1, plate_shared_1
d20 Sun 13:40 look kitchen_table_k1: bowl_shared_2, charger_mara, laptop_mara, pan_shared_1, pen_mara
d20 Sun 13:40 look sink_k1: plate_shared_2, water_bottle_mara, watering_can_mara
d20 Sun 15:02 look nightstand_b1: hairbrush_mara, phone_mara
d20 Sun 16:38 look bathroom_shelf_ba1: makeup_kit_mara, medication_bottle_mara
d20 Sun 16:38 look towel_rack_ba1: towel_mara
d20 Sun 16:43 look sink_k1: plate_shared_2, water_bottle_mara, watering_can_mara
d20 Sun 18:49 look kitchen_table_k1: bowl_shared_2, charger_mara, laptop_mara, pen_mara, plate_shared_1
d20 Sun 19:22 look entry_floor_e1: (nothing)
d20 Sun 19:22 look entry_hook_e1: (nothing)
d20 Sun 19:22 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d20 Sun 20:23 look dish_rack_k1: mug_shared_1
d20 Sun 20:36 look sink_k1: plate_shared_2, water_bottle_mara, watering_can_mara
d20 Sun 22:20 look bed_b1: (nothing)
d20 Sun 22:20 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara
d20 Sun 22:20 look desk_b1: (nothing)
d20 Sun 22:20 look nightstand_b1: phone_mara
d20 Sun 23:19 look counter_k1: lunchbox_mara, pan_shared_1
d21 Mon 00:01 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d21 Mon 00:03 look sink_k1: plate_shared_2, water_bottle_mara, watering_can_mara
d21 Mon 05:13 look entry_hook_e1: (nothing)
d21 Mon 05:32 look sink_k1: plate_shared_2, water_bottle_mara, watering_can_mara
d21 Mon 06:04 look dish_rack_k1: mug_shared_1
d21 Mon 06:23 look armchair_l1: jacket_mara
d21 Mon 06:23 look bookshelf_l1: remote_shared_1
d21 Mon 06:23 look coffee_table_l1: glasses_mara
d21 Mon 06:23 look couch_l1: blanket_mara, book_mara, headphones_mara, vacuum_cleaner_shared_1, yoga_mat_mara
d21 Mon 06:23 look tv_stand_l1: tablet_mara
d21 Mon 06:45 look kitchen_table_k1: bowl_shared_2, charger_mara, laptop_mara, plate_shared_1
d21 Mon 06:56 look entry_table_e1: bowl_shared_1
d21 Mon 07:00 look sink_k1: watering_can_mara
d21 Mon 07:47 look kitchen_table_k1: bowl_shared_2, plate_shared_1
d21 Mon 07:47 look counter_k1: mug_mara, pan_shared_1, pen_mara, plate_shared_2
d21 Mon 07:53 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d21 Mon 08:18 look towel_rack_ba1: towel_mara
d21 Mon 09:36 look chair_k1: umbrella_mara
d21 Mon 09:36 look chair_k2: (nothing)
d21 Mon 09:36 look counter_k1: mug_mara, pan_shared_1, pen_mara, plate_shared_2
d21 Mon 09:36 look cupboard_k1: pot_shared_1
d21 Mon 09:36 look dish_rack_k1: mug_shared_1
d21 Mon 09:36 look kitchen_table_k1: bowl_shared_2, plate_shared_1
d21 Mon 09:36 look sink_k1: watering_can_mara
d21 Mon 12:02 look cupboard_k1: pot_shared_1
d21 Mon 12:23 look kitchen_table_k1: bowl_shared_2, plate_shared_1
d21 Mon 12:28 look counter_k1: mug_mara, pan_shared_1, pen_mara, plate_shared_2
d21 Mon 12:29 look entry_table_e1: bowl_shared_1
d21 Mon 13:01 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d21 Mon 13:01 look towel_rack_ba1: towel_mara
d21 Mon 15:01 look dish_rack_k1: mug_shared_1
d21 Mon 15:08 look nightstand_b1: (nothing)
d21 Mon 15:56 look entry_floor_e1: (nothing)
d21 Mon 15:56 look entry_hook_e1: (nothing)
d21 Mon 15:56 look entry_table_e1: bowl_shared_1
d21 Mon 16:37 look chair_k1: umbrella_mara
d21 Mon 18:16 look kitchen_table_k1: bowl_shared_2, lunchbox_mara, pan_shared_1, plate_shared_2
d21 Mon 19:16 look bed_b1: (nothing)
d21 Mon 19:16 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara
d21 Mon 19:16 look desk_b1: laptop_mara
d21 Mon 19:16 look nightstand_b1: (nothing)
d21 Mon 19:43 look sink_k1: plate_shared_1, pot_shared_1, watering_can_mara
d21 Mon 21:01 look counter_k1: pen_mara, water_bottle_mara
d21 Mon 21:33 look kitchen_table_k1: bowl_shared_2, lunchbox_mara, pan_shared_1, plate_shared_2
d21 Mon 21:46 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d21 Mon 22:17 look armchair_l1: (nothing)
d21 Mon 22:17 look bookshelf_l1: remote_shared_1
d21 Mon 22:17 look coffee_table_l1: book_mara, glasses_mara, mug_mara
d21 Mon 22:17 look couch_l1: blanket_mara, vacuum_cleaner_shared_1, yoga_mat_mara
d21 Mon 22:17 look tv_stand_l1: tablet_mara
d22 Tue 05:10 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d22 Tue 05:12 look kitchen_table_k1: bowl_shared_2, lunchbox_mara, pan_shared_1, plate_shared_2
d22 Tue 05:20 look nightstand_b1: (nothing)
d22 Tue 06:07 look sink_k1: plate_shared_1, pot_shared_1, watering_can_mara
d22 Tue 06:30 look chair_k1: backpack_mara, umbrella_mara
d22 Tue 06:30 look chair_k2: notebook_mara
d22 Tue 06:30 look counter_k1: water_bottle_mara
d22 Tue 06:30 look cupboard_k1: (nothing)
d22 Tue 06:30 look dish_rack_k1: mug_shared_1
d22 Tue 06:30 look kitchen_table_k1: bowl_shared_2, lunchbox_mara, mug_mara, pan_shared_1, pen_mara
d22 Tue 06:30 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d22 Tue 09:29 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d22 Tue 09:31 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d22 Tue 09:31 look towel_rack_ba1: towel_mara
d22 Tue 12:03 look counter_k1: (nothing)
d22 Tue 12:03 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d22 Tue 12:38 look entry_floor_e1: (nothing)
d22 Tue 12:38 look entry_hook_e1: (nothing)
d22 Tue 12:38 look entry_table_e1: bowl_shared_1
d22 Tue 13:45 look nightstand_b1: (nothing)
d22 Tue 14:31 look kitchen_table_k1: bowl_shared_2, mug_mara, pan_shared_1, pen_mara
d22 Tue 14:41 look entry_table_e1: bowl_shared_1
d22 Tue 15:47 look bed_b1: (nothing)
d22 Tue 15:47 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara
d22 Tue 15:47 look desk_b1: (nothing)
d22 Tue 15:47 look nightstand_b1: (nothing)
d22 Tue 15:49 look kitchen_table_k1: bowl_shared_2, mug_mara, pan_shared_1, pen_mara
d22 Tue 19:03 look armchair_l1: (nothing)
d22 Tue 19:03 look bookshelf_l1: (nothing)
d22 Tue 19:03 look coffee_table_l1: book_mara
d22 Tue 19:03 look couch_l1: blanket_mara, remote_shared_1, vacuum_cleaner_shared_1, yoga_mat_mara
d22 Tue 19:03 look tv_stand_l1: (nothing)
d22 Tue 19:31 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d22 Tue 20:05 look sink_k1: lunchbox_mara, pot_shared_1, watering_can_mara
d22 Tue 20:19 look chair_k1: keys_mara, tablet_mara
d22 Tue 20:32 look nightstand_b1: (nothing)
d22 Tue 21:12 look cupboard_k1: (nothing)
d22 Tue 21:12 look entry_hook_e1: charger_mara
d22 Tue 22:12 look chair_k1: keys_mara, tablet_mara
d22 Tue 22:12 look chair_k2: headphones_mara
d22 Tue 22:12 look counter_k1: (nothing)
d22 Tue 22:12 look cupboard_k1: (nothing)
d22 Tue 22:12 look dish_rack_k1: backpack_mara, jacket_mara, mug_shared_1
d22 Tue 22:12 look kitchen_table_k1: bowl_shared_2, glasses_mara, laptop_mara, mug_mara, notebook_mara, pan_shared_1, pen_mara, plate_shared_1, plate_shared_2
d22 Tue 22:12 look sink_k1: lunchbox_mara, pot_shared_1, watering_can_mara
d23 Wed 05:16 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d23 Wed 05:31 look dish_rack_k1: backpack_mara, jacket_mara, mug_shared_1
d23 Wed 05:37 look chair_k1: keys_mara, tablet_mara
d23 Wed 06:16 look entry_table_e1: bowl_shared_1, wallet_mara
d23 Wed 06:37 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d23 Wed 06:37 look towel_rack_ba1: towel_mara
d23 Wed 07:12 look entry_hook_e1: (nothing)
d23 Wed 07:52 look nightstand_b1: (nothing)
d23 Wed 08:40 look entry_table_e1: bowl_shared_1
d23 Wed 09:57 look nightstand_b1: (nothing)
d23 Wed 09:58 look entry_floor_e1: umbrella_mara
d23 Wed 09:58 look entry_hook_e1: (nothing)
d23 Wed 09:58 look entry_table_e1: bowl_shared_1
d23 Wed 10:38 look sink_k1: bowl_shared_2, pot_shared_1, watering_can_mara
d23 Wed 11:00 look kitchen_table_k1: pan_shared_1, plate_shared_1
d23 Wed 11:00 look counter_k1: mug_mara, pen_mara, plate_shared_2
d23 Wed 11:21 look entry_hook_e1: (nothing)
d23 Wed 12:57 look bed_b1: (nothing)
d23 Wed 12:57 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara
d23 Wed 12:57 look desk_b1: (nothing)
d23 Wed 12:57 look nightstand_b1: (nothing)
d23 Wed 13:57 look dish_rack_k1: mug_shared_1
d23 Wed 14:16 look dish_rack_k1: mug_shared_1
d23 Wed 14:21 look nightstand_b1: (nothing)
d23 Wed 14:21 look kitchen_table_k1: pan_shared_1, plate_shared_1
d23 Wed 15:41 look sink_k1: bowl_shared_2, pot_shared_1, watering_can_mara
d23 Wed 16:00 look armchair_l1: (nothing)
d23 Wed 16:00 look bookshelf_l1: (nothing)
d23 Wed 16:00 look coffee_table_l1: book_mara
d23 Wed 16:00 look couch_l1: blanket_mara, remote_shared_1, vacuum_cleaner_shared_1, yoga_mat_mara
d23 Wed 16:00 look tv_stand_l1: (nothing)
d23 Wed 16:57 look sink_k1: bowl_shared_2, charger_mara, plate_shared_2, pot_shared_1, watering_can_mara
d23 Wed 19:08 look chair_k1: headphones_mara, notebook_mara, tablet_mara
d23 Wed 19:08 look chair_k2: (nothing)
d23 Wed 19:08 look counter_k1: pan_shared_1, pen_mara
d23 Wed 19:08 look cupboard_k1: keys_mara
d23 Wed 19:08 look dish_rack_k1: backpack_mara, lunchbox_mara, mug_shared_1
d23 Wed 19:08 look kitchen_table_k1: glasses_mara, laptop_mara, phone_mara, plate_shared_1, water_bottle_mara
d23 Wed 19:08 look sink_k1: bowl_shared_2, charger_mara, plate_shared_2, pot_shared_1, watering_can_mara
d23 Wed 20:42 look towel_rack_ba1: towel_mara
d23 Wed 22:34 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d23 Wed 22:34 look towel_rack_ba1: towel_mara
d23 Wed 23:38 look sink_k1: bowl_shared_2, charger_mara, plate_shared_2, pot_shared_1, watering_can_mara
d24 Thu 00:26 look kitchen_table_k1: glasses_mara, laptop_mara, plate_shared_1
d24 Thu 05:26 look entry_table_e1: bowl_shared_1, wallet_mara
d24 Thu 05:27 look sink_k1: bowl_shared_2, charger_mara, plate_shared_2, pot_shared_1, watering_can_mara
d24 Thu 06:02 look dish_rack_k1: backpack_mara, lunchbox_mara, mug_shared_1
d24 Thu 06:20 look entry_floor_e1: umbrella_mara
d24 Thu 06:20 look entry_hook_e1: (nothing)
d24 Thu 06:20 look entry_table_e1: bowl_shared_1, wallet_mara
d24 Thu 06:45 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, pan_shared_1, plate_shared_1
d24 Thu 06:45 look nightstand_b1: water_bottle_mara
d24 Thu 07:55 look chair_k1: tablet_mara
d24 Thu 09:22 look towel_rack_ba1: towel_mara
d24 Thu 09:22 look bed_b1: (nothing)
d24 Thu 09:22 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara
d24 Thu 09:22 look desk_b1: (nothing)
d24 Thu 09:22 look nightstand_b1: water_bottle_mara
d24 Thu 09:50 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, pan_shared_1, plate_shared_1
d24 Thu 10:49 look dish_rack_k1: mug_shared_1
d24 Thu 11:13 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d24 Thu 11:22 look sink_k1: pot_shared_1, watering_can_mara
d24 Thu 12:12 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, pan_shared_1, plate_shared_1
d24 Thu 12:12 look counter_k1: pen_mara, plate_shared_2
d24 Thu 12:12 look sink_k1: pot_shared_1, watering_can_mara
d24 Thu 12:12 look dish_rack_k1: mug_shared_1
d24 Thu 12:41 look armchair_l1: (nothing)
d24 Thu 12:41 look bookshelf_l1: (nothing)
d24 Thu 12:41 look coffee_table_l1: (nothing)
d24 Thu 12:41 look couch_l1: blanket_mara, book_mara, remote_shared_1, vacuum_cleaner_shared_1
d24 Thu 12:41 look tv_stand_l1: (nothing)
d24 Thu 13:46 look sink_k1: pot_shared_1, watering_can_mara
d24 Thu 15:06 look entry_table_e1: bowl_shared_1
d24 Thu 15:46 look entry_table_e1: bowl_shared_1
d24 Thu 15:48 look chair_k1: tablet_mara
d24 Thu 15:48 look chair_k2: (nothing)
d24 Thu 15:48 look counter_k1: pen_mara, plate_shared_2
d24 Thu 15:48 look cupboard_k1: (nothing)
d24 Thu 15:48 look dish_rack_k1: mug_shared_1
d24 Thu 15:48 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, pan_shared_1, plate_shared_1
d24 Thu 15:48 look sink_k1: pot_shared_1, watering_can_mara
d24 Thu 17:38 look entry_table_e1: bowl_shared_1, keys_mara, phone_mara, wallet_mara
d24 Thu 18:10 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d24 Thu 19:07 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d24 Thu 19:07 look towel_rack_ba1: towel_mara
d24 Thu 21:18 look entry_floor_e1: umbrella_mara
d24 Thu 22:15 look entry_floor_e1: umbrella_mara
d24 Thu 22:15 look entry_hook_e1: jacket_mara
d24 Thu 22:15 look entry_table_e1: bowl_shared_1, keys_mara, phone_mara, wallet_mara
d25 Fri 04:55 look bed_b1: (nothing)
d25 Fri 04:55 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara
d25 Fri 04:55 look desk_b1: (nothing)
d25 Fri 04:55 look nightstand_b1: water_bottle_mara
d25 Fri 06:34 look sink_k1: plate_shared_1, watering_can_mara
d25 Fri 06:34 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, laptop_mara, mug_mara, notebook_mara, pan_shared_1
d25 Fri 06:50 look sink_k1: plate_shared_1, watering_can_mara
d25 Fri 07:14 look sink_k1: plate_shared_1, watering_can_mara
d25 Fri 08:06 look sink_k1: plate_shared_1, watering_can_mara
d25 Fri 08:20 look armchair_l1: (nothing)
d25 Fri 08:20 look bookshelf_l1: (nothing)
d25 Fri 08:20 look coffee_table_l1: (nothing)
d25 Fri 08:20 look couch_l1: blanket_mara, book_mara, remote_shared_1, vacuum_cleaner_shared_1, yoga_mat_mara
d25 Fri 08:20 look tv_stand_l1: (nothing)

QUESTION: where is remote_shared_1 right now?
NOW: d25 Fri 08:26
BUDGET: 19 looks left today; at most 21 more looks on this question.

## reply

{"action": "answer", "ranked": ["couch_l1", "coffee_table_l1", "tv_stand_l1", "bookshelf_l1", "armchair_l1"], "why": "The most recent sighting of remote_shared_1 was at d25 Fri 08:20, where it was found on couch_l1. No subsequent events in the log indicate it has moved. The other living room receptacles are ranked lower as plausible alternative locations, but couch_l1 is the most strongly supported by the latest evidence."}
