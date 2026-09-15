# call 2000: phone_mara at d19 Sat 22:28

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

OBJECTS LEAVE THE HOUSE: residents take things with them to work, to school, to the gym, on errands and on trips; an object that is out is invisible to every look while it is out, and the walkthrough happened at one instant, so anything that was out with someone then is missing from the walkthrough and first appears in the log later. A sighting anywhere in the house says the object is in; an empty look at its usual place, at an hour it is usually there, is weak evidence it is out. After the log you get, per object, a count of weekday daytime looks at its usual place that found it versus found nothing.

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
d00 Mon 15:20 look cupboard_k1: mug_shared_1, plate_shared_1, pot_shared_1
d00 Mon 15:29 look counter_k1: lunchbox_mara, plate_shared_2
d00 Mon 15:37 look kitchen_table_k1: bowl_shared_2, pen_mara
d00 Mon 15:37 look bathroom_shelf_ba1: makeup_kit_mara, medication_bottle_mara
d00 Mon 15:37 look towel_rack_ba1: towel_mara
d00 Mon 15:44 look chair_k1: mug_mara
d00 Mon 16:10 look sink_k1: pan_shared_1, watering_can_mara
d00 Mon 16:49 look couch_l1: blanket_mara, yoga_mat_mara
d00 Mon 16:52 look entry_table_e1: bowl_shared_1, keys_mara
d00 Mon 19:00 look entry_floor_e1: umbrella_mara
d00 Mon 19:00 look entry_hook_e1: (nothing)
d00 Mon 19:00 look entry_table_e1: bowl_shared_1, keys_mara
d00 Mon 19:33 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d00 Mon 19:56 look coffee_table_l1: remote_shared_1, tablet_mara
d00 Mon 20:10 look bookshelf_l1: book_mara
d00 Mon 20:33 look nightstand_b1: hairbrush_mara
d00 Mon 22:14 look bed_b1: (nothing)
d00 Mon 22:14 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d00 Mon 22:14 look desk_b1: (nothing)
d00 Mon 22:14 look nightstand_b1: hairbrush_mara
d01 Tue 06:43 look armchair_l1: (nothing)
d01 Tue 06:43 look bookshelf_l1: book_mara
d01 Tue 06:43 look coffee_table_l1: remote_shared_1, tablet_mara
d01 Tue 06:43 look couch_l1: blanket_mara, yoga_mat_mara
d01 Tue 06:43 look tv_stand_l1: (nothing)
d01 Tue 07:13 look entry_table_e1: bowl_shared_1
d01 Tue 08:33 look counter_k1: mug_mara, notebook_mara, pan_shared_1, plate_shared_2
d01 Tue 09:32 look cupboard_k1: mug_shared_1, pot_shared_1
d01 Tue 09:41 look chair_k1: (nothing)
d01 Tue 09:41 look chair_k2: (nothing)
d01 Tue 09:41 look counter_k1: mug_mara, notebook_mara, pan_shared_1, plate_shared_2
d01 Tue 09:41 look cupboard_k1: mug_shared_1, pot_shared_1
d01 Tue 09:41 look dish_rack_k1: pen_mara
d01 Tue 09:41 look kitchen_table_k1: plate_shared_1
d01 Tue 09:41 look sink_k1: bowl_shared_2, watering_can_mara
d01 Tue 11:24 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d01 Tue 11:30 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d01 Tue 12:49 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d01 Tue 12:49 look towel_rack_ba1: towel_mara
d01 Tue 14:01 look entry_table_e1: bowl_shared_1
d01 Tue 14:45 look kitchen_table_k1: plate_shared_1
d01 Tue 15:20 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d01 Tue 15:38 look coffee_table_l1: remote_shared_1, tablet_mara
d01 Tue 15:47 look entry_floor_e1: umbrella_mara
d01 Tue 15:47 look entry_hook_e1: (nothing)
d01 Tue 15:47 look entry_table_e1: bowl_shared_1
d01 Tue 16:24 look sink_k1: bowl_shared_2, lunchbox_mara, watering_can_mara
d01 Tue 17:13 look sink_k1: bowl_shared_2, lunchbox_mara, watering_can_mara
d01 Tue 18:23 look counter_k1: mug_mara, notebook_mara
d01 Tue 18:56 look bed_b1: (nothing)
d01 Tue 18:56 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d01 Tue 18:56 look desk_b1: (nothing)
d01 Tue 18:56 look nightstand_b1: phone_mara
d01 Tue 20:23 look cupboard_k1: headphones_mara, keys_mara, mug_shared_1, pot_shared_1
d01 Tue 21:08 look cupboard_k1: headphones_mara, keys_mara, mug_shared_1, pot_shared_1
d01 Tue 21:45 look armchair_l1: (nothing)
d01 Tue 21:45 look bookshelf_l1: book_mara
d01 Tue 21:45 look coffee_table_l1: remote_shared_1, tablet_mara
d01 Tue 21:45 look couch_l1: blanket_mara, water_bottle_mara, yoga_mat_mara
d01 Tue 21:45 look tv_stand_l1: (nothing)
d01 Tue 22:05 look kitchen_table_k1: charger_mara, glasses_mara, jacket_mara, laptop_mara, plate_shared_1, plate_shared_2
d01 Tue 22:40 look counter_k1: mug_mara, notebook_mara
d02 Wed 04:26 look kitchen_table_k1: charger_mara, glasses_mara, jacket_mara, laptop_mara, plate_shared_1, plate_shared_2
d02 Wed 04:57 look kitchen_table_k1: charger_mara, glasses_mara, jacket_mara, laptop_mara, plate_shared_1, plate_shared_2
d02 Wed 05:42 look counter_k1: mug_mara, notebook_mara
d02 Wed 05:48 look chair_k1: (nothing)
d02 Wed 05:48 look chair_k2: (nothing)
d02 Wed 05:48 look counter_k1: mug_mara, notebook_mara
d02 Wed 05:48 look cupboard_k1: headphones_mara, keys_mara, mug_shared_1, pot_shared_1
d02 Wed 05:48 look dish_rack_k1: pen_mara, wallet_mara
d02 Wed 05:48 look kitchen_table_k1: charger_mara, glasses_mara, jacket_mara, laptop_mara, plate_shared_1, plate_shared_2
d02 Wed 05:48 look sink_k1: bowl_shared_2, lunchbox_mara, pan_shared_1, watering_can_mara
d02 Wed 06:15 look cupboard_k1: headphones_mara, keys_mara, mug_shared_1, pot_shared_1
d02 Wed 06:37 look bathroom_shelf_ba1: hairbrush_mara, medication_bottle_mara
d02 Wed 07:32 look cupboard_k1: mug_shared_1, pot_shared_1
d02 Wed 08:55 look cupboard_k1: mug_shared_1, pot_shared_1
d02 Wed 08:55 look bathroom_shelf_ba1: hairbrush_mara, medication_bottle_mara
d02 Wed 08:55 look towel_rack_ba1: towel_mara
d02 Wed 09:46 look sink_k1: watering_can_mara
d02 Wed 10:22 look cupboard_k1: mug_shared_1, pot_shared_1
d02 Wed 10:33 look kitchen_table_k1: bowl_shared_2, makeup_kit_mara, mug_mara, pan_shared_1, plate_shared_1
d02 Wed 11:20 look couch_l1: blanket_mara, water_bottle_mara, yoga_mat_mara
d02 Wed 11:25 look sink_k1: watering_can_mara
d02 Wed 11:38 look kitchen_table_k1: bowl_shared_2, makeup_kit_mara, mug_mara, pan_shared_1, plate_shared_1
d02 Wed 12:20 look entry_floor_e1: umbrella_mara
d02 Wed 12:20 look entry_hook_e1: (nothing)
d02 Wed 12:20 look entry_table_e1: bowl_shared_1
d02 Wed 13:05 look couch_l1: blanket_mara, water_bottle_mara, yoga_mat_mara
d02 Wed 13:19 look kitchen_table_k1: bowl_shared_2, makeup_kit_mara, mug_mara, pan_shared_1, plate_shared_1
d02 Wed 13:33 look kitchen_table_k1: bowl_shared_2, makeup_kit_mara, mug_mara, pan_shared_1, plate_shared_1
d02 Wed 13:57 look kitchen_table_k1: bowl_shared_2, makeup_kit_mara, mug_mara, pan_shared_1, plate_shared_1
d02 Wed 14:18 look counter_k1: pen_mara, plate_shared_2
d02 Wed 14:24 look bathroom_shelf_ba1: hairbrush_mara, medication_bottle_mara
d02 Wed 15:21 look kitchen_table_k1: bowl_shared_2, makeup_kit_mara, mug_mara, pan_shared_1, plate_shared_1
d02 Wed 15:35 look bed_b1: (nothing)
d02 Wed 15:35 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d02 Wed 15:35 look desk_b1: (nothing)
d02 Wed 15:35 look nightstand_b1: (nothing)
d02 Wed 16:11 look cupboard_k1: mug_shared_1, pot_shared_1
d02 Wed 16:34 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara, makeup_kit_mara, mug_mara, pan_shared_1, plate_shared_1
d02 Wed 16:51 look nightstand_b1: (nothing)
d02 Wed 18:37 look counter_k1: (nothing)
d02 Wed 18:53 look armchair_l1: (nothing)
d02 Wed 18:53 look bookshelf_l1: (nothing)
d02 Wed 18:53 look coffee_table_l1: glasses_mara, remote_shared_1, tablet_mara
d02 Wed 18:53 look couch_l1: blanket_mara, water_bottle_mara, yoga_mat_mara
d02 Wed 18:53 look tv_stand_l1: (nothing)
d02 Wed 22:18 look chair_k1: notebook_mara, pen_mara
d02 Wed 22:18 look chair_k2: (nothing)
d02 Wed 22:18 look counter_k1: (nothing)
d02 Wed 22:18 look cupboard_k1: mug_shared_1
d02 Wed 22:18 look dish_rack_k1: lunchbox_mara, mug_mara
d02 Wed 22:18 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara, makeup_kit_mara
d02 Wed 22:18 look sink_k1: pan_shared_1, plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d03 Thu 00:19 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara, makeup_kit_mara
d03 Thu 05:11 look cupboard_k1: mug_shared_1
d03 Thu 05:43 look dish_rack_k1: lunchbox_mara, mug_mara
d03 Thu 05:59 look bathroom_shelf_ba1: hairbrush_mara
d03 Thu 05:59 look towel_rack_ba1: laptop_mara, towel_mara, wallet_mara
d03 Thu 07:32 look kitchen_table_k1: bowl_shared_2, charger_mara
d03 Thu 07:32 look cupboard_k1: mug_shared_1
d03 Thu 07:40 look nightstand_b1: book_mara
d03 Thu 08:43 look sink_k1: pan_shared_1, plate_shared_1, plate_shared_2, pot_shared_1, wallet_mara, watering_can_mara
d03 Thu 08:49 look counter_k1: medication_bottle_mara, mug_mara
d03 Thu 08:59 look entry_floor_e1: umbrella_mara
d03 Thu 08:59 look entry_hook_e1: backpack_mara, jacket_mara
d03 Thu 08:59 look entry_table_e1: bowl_shared_1, keys_mara
d03 Thu 10:44 look sink_k1: pan_shared_1, plate_shared_1, plate_shared_2, pot_shared_1, wallet_mara, watering_can_mara
d03 Thu 10:56 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara
d03 Thu 10:57 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara
d03 Thu 11:15 look nightstand_b1: book_mara, phone_mara
d03 Thu 11:27 look sink_k1: pan_shared_1, plate_shared_1, plate_shared_2, pot_shared_1, wallet_mara, watering_can_mara
d03 Thu 11:38 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara
d03 Thu 12:07 look couch_l1: blanket_mara, water_bottle_mara, yoga_mat_mara
d03 Thu 12:17 look bed_b1: (nothing)
d03 Thu 12:17 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d03 Thu 12:17 look desk_b1: (nothing)
d03 Thu 12:17 look nightstand_b1: book_mara, phone_mara
d03 Thu 12:41 look counter_k1: medication_bottle_mara, mug_mara
d03 Thu 13:02 look coffee_table_l1: remote_shared_1, tablet_mara
d03 Thu 13:14 look towel_rack_ba1: towel_mara
d03 Thu 13:14 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara
d03 Thu 15:05 look cupboard_k1: mug_shared_1
d03 Thu 15:20 look sink_k1: pan_shared_1, plate_shared_1, plate_shared_2, pot_shared_1, wallet_mara, watering_can_mara
d03 Thu 15:23 look armchair_l1: (nothing)
d03 Thu 15:23 look bookshelf_l1: (nothing)
d03 Thu 15:23 look coffee_table_l1: remote_shared_1, tablet_mara
d03 Thu 15:23 look couch_l1: blanket_mara, water_bottle_mara, yoga_mat_mara
d03 Thu 15:23 look tv_stand_l1: (nothing)
d03 Thu 16:03 look counter_k1: medication_bottle_mara, mug_mara
d03 Thu 17:21 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara
d03 Thu 18:24 look sink_k1: book_mara, jacket_mara, pan_shared_1, pot_shared_1, watering_can_mara
d03 Thu 18:35 look chair_k1: (nothing)
d03 Thu 18:35 look chair_k2: keys_mara, wallet_mara
d03 Thu 18:35 look counter_k1: medication_bottle_mara, mug_mara, plate_shared_2
d03 Thu 18:35 look cupboard_k1: mug_shared_1, notebook_mara
d03 Thu 18:35 look dish_rack_k1: backpack_mara, lunchbox_mara
d03 Thu 18:35 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara, pen_mara, plate_shared_1
d03 Thu 18:35 look sink_k1: book_mara, jacket_mara, pan_shared_1, pot_shared_1, watering_can_mara
d03 Thu 21:56 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara
d03 Thu 21:56 look towel_rack_ba1: towel_mara
d04 Fri 04:45 look counter_k1: medication_bottle_mara, mug_mara, plate_shared_2
d04 Fri 04:55 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d04 Fri 05:28 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara, pen_mara, plate_shared_1
d04 Fri 05:32 look sink_k1: book_mara, jacket_mara, pan_shared_1, pot_shared_1, watering_can_mara
d04 Fri 06:09 look entry_floor_e1: umbrella_mara
d04 Fri 06:09 look entry_hook_e1: (nothing)
d04 Fri 06:09 look entry_table_e1: bowl_shared_1
d04 Fri 06:41 look nightstand_b1: phone_mara
d04 Fri 06:59 look kitchen_table_k1: bowl_shared_2, pan_shared_1, plate_shared_1
d04 Fri 07:32 look sink_k1: book_mara, pot_shared_1, watering_can_mara
d04 Fri 08:23 look kitchen_table_k1: bowl_shared_2, pan_shared_1, plate_shared_1
d04 Fri 08:54 look bed_b1: (nothing)
d04 Fri 08:54 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d04 Fri 08:54 look desk_b1: (nothing)
d04 Fri 08:54 look nightstand_b1: (nothing)
d04 Fri 09:21 look chair_k2: (nothing)
d04 Fri 09:21 look cupboard_k1: mug_shared_1
d04 Fri 09:31 look kitchen_table_k1: bowl_shared_2, pan_shared_1, plate_shared_1
d04 Fri 10:12 look nightstand_b1: (nothing)
d04 Fri 10:30 look kitchen_table_k1: bowl_shared_2, pan_shared_1, plate_shared_1
d04 Fri 11:19 look armchair_l1: (nothing)
d04 Fri 11:19 look bookshelf_l1: (nothing)
d04 Fri 11:19 look coffee_table_l1: tablet_mara
d04 Fri 11:19 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d04 Fri 11:19 look tv_stand_l1: (nothing)
d04 Fri 11:22 look counter_k1: mug_mara, pen_mara, plate_shared_2
d04 Fri 11:33 look sink_k1: book_mara, pot_shared_1, watering_can_mara
d04 Fri 13:17 look entry_hook_e1: (nothing)
d04 Fri 13:22 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d04 Fri 14:09 look chair_k1: (nothing)
d04 Fri 14:09 look chair_k2: (nothing)
d04 Fri 14:09 look counter_k1: mug_mara, pen_mara, plate_shared_2
d04 Fri 14:09 look cupboard_k1: mug_shared_1
d04 Fri 14:09 look dish_rack_k1: (nothing)
d04 Fri 14:09 look kitchen_table_k1: bowl_shared_2, pan_shared_1, plate_shared_1
d04 Fri 14:09 look sink_k1: book_mara, pot_shared_1, watering_can_mara
d04 Fri 14:58 look sink_k1: book_mara, pot_shared_1, watering_can_mara
d04 Fri 15:27 look kitchen_table_k1: bowl_shared_2, pan_shared_1, plate_shared_1
d04 Fri 15:45 look sink_k1: book_mara, pot_shared_1, watering_can_mara
d04 Fri 15:47 look cupboard_k1: mug_shared_1
d04 Fri 15:47 look kitchen_table_k1: bowl_shared_2, pan_shared_1, plate_shared_1
d04 Fri 15:47 look sink_k1: book_mara, pot_shared_1, watering_can_mara
d04 Fri 16:22 look sink_k1: book_mara, pot_shared_1, watering_can_mara
d04 Fri 16:53 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d04 Fri 16:53 look towel_rack_ba1: towel_mara
d04 Fri 19:31 look entry_floor_e1: umbrella_mara
d04 Fri 19:31 look entry_hook_e1: backpack_mara, jacket_mara
d04 Fri 19:31 look entry_table_e1: bowl_shared_1, wallet_mara
d05 Sat 07:18 look counter_k1: mug_mara, pen_mara, plate_shared_2, water_bottle_mara
d05 Sat 07:45 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d05 Sat 07:56 look bed_b1: (nothing)
d05 Sat 07:56 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d05 Sat 07:56 look desk_b1: (nothing)
d05 Sat 07:56 look nightstand_b1: (nothing)
d05 Sat 08:23 look cupboard_k1: mug_shared_1
d05 Sat 09:11 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d05 Sat 09:32 look cupboard_k1: mug_shared_1
d05 Sat 10:31 look kitchen_table_k1: charger_mara, glasses_mara, headphones_mara, notebook_mara, plate_shared_1
d05 Sat 11:00 look armchair_l1: lunchbox_mara
d05 Sat 11:00 look bookshelf_l1: laptop_mara
d05 Sat 11:00 look coffee_table_l1: tablet_mara
d05 Sat 11:00 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d05 Sat 11:00 look tv_stand_l1: (nothing)
d05 Sat 12:31 look sink_k1: book_mara, pot_shared_1, watering_can_mara
d05 Sat 13:11 look sink_k1: book_mara, plate_shared_2, pot_shared_1, watering_can_mara
d05 Sat 13:16 look kitchen_table_k1: charger_mara, glasses_mara, headphones_mara, mug_mara, notebook_mara
d05 Sat 13:50 look chair_k1: (nothing)
d05 Sat 13:50 look chair_k2: (nothing)
d05 Sat 13:50 look counter_k1: lunchbox_mara, pan_shared_1, pen_mara, phone_mara, tablet_mara, water_bottle_mara
d05 Sat 13:50 look cupboard_k1: bowl_shared_2
d05 Sat 13:50 look dish_rack_k1: mug_shared_1, plate_shared_1
d05 Sat 13:50 look kitchen_table_k1: charger_mara, glasses_mara, headphones_mara, mug_mara, notebook_mara
d05 Sat 13:50 look sink_k1: book_mara, plate_shared_2, pot_shared_1, watering_can_mara
d05 Sat 14:55 look entry_hook_e1: backpack_mara
d05 Sat 15:02 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d05 Sat 16:05 look sink_k1: book_mara, plate_shared_2, pot_shared_1, watering_can_mara
d05 Sat 16:41 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d05 Sat 16:41 look towel_rack_ba1: (nothing)
d05 Sat 17:43 look entry_hook_e1: backpack_mara
d05 Sat 19:14 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d05 Sat 19:19 look counter_k1: lunchbox_mara, pan_shared_1, pen_mara, phone_mara, tablet_mara, water_bottle_mara
d05 Sat 19:37 look entry_floor_e1: umbrella_mara
d05 Sat 19:37 look entry_hook_e1: backpack_mara
d05 Sat 19:37 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d05 Sat 19:56 look kitchen_table_k1: charger_mara, glasses_mara, headphones_mara, notebook_mara
d05 Sat 21:29 look counter_k1: lunchbox_mara, pan_shared_1, pen_mara, phone_mara, tablet_mara, water_bottle_mara
d05 Sat 21:53 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d05 Sat 22:20 look bed_b1: (nothing)
d05 Sat 22:20 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, towel_mara, vacuum_cleaner_shared_1
d05 Sat 22:20 look desk_b1: (nothing)
d05 Sat 22:20 look nightstand_b1: book_mara
d05 Sat 22:29 look kitchen_table_k1: charger_mara, glasses_mara, headphones_mara, notebook_mara
d05 Sat 23:35 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d05 Sat 23:35 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d06 Sun 07:02 look kitchen_table_k1: charger_mara, glasses_mara, headphones_mara, notebook_mara
d06 Sun 07:03 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d06 Sun 07:21 look bookshelf_l1: laptop_mara
d06 Sun 07:51 look armchair_l1: (nothing)
d06 Sun 07:51 look bookshelf_l1: laptop_mara
d06 Sun 07:51 look coffee_table_l1: remote_shared_1
d06 Sun 07:51 look couch_l1: blanket_mara, yoga_mat_mara
d06 Sun 07:51 look tv_stand_l1: (nothing)
d06 Sun 08:40 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1
d06 Sun 09:01 look kitchen_table_k1: bowl_shared_1, bowl_shared_2, charger_mara, glasses_mara, headphones_mara, notebook_mara, pan_shared_1, pen_mara
d06 Sun 10:22 look sink_k1: plate_shared_1, pot_shared_1, watering_can_mara
d06 Sun 10:29 look entry_hook_e1: backpack_mara
d06 Sun 10:57 look chair_k1: (nothing)
d06 Sun 10:57 look chair_k2: mug_mara
d06 Sun 10:57 look counter_k1: lunchbox_mara, pen_mara, plate_shared_2, tablet_mara, water_bottle_mara
d06 Sun 10:57 look cupboard_k1: (nothing)
d06 Sun 10:57 look dish_rack_k1: mug_shared_1
d06 Sun 10:57 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara, laptop_mara, notebook_mara, pan_shared_1
d06 Sun 10:57 look sink_k1: plate_shared_1, pot_shared_1, watering_can_mara
d06 Sun 11:01 look counter_k1: lunchbox_mara, pen_mara, tablet_mara, water_bottle_mara
d06 Sun 12:04 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d06 Sun 13:01 look entry_hook_e1: backpack_mara
d06 Sun 13:29 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d06 Sun 13:29 look towel_rack_ba1: (nothing)
d06 Sun 14:00 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara, laptop_mara, notebook_mara, pan_shared_1
d06 Sun 14:12 look counter_k1: pen_mara, tablet_mara
d06 Sun 16:21 look entry_floor_e1: umbrella_mara
d06 Sun 16:21 look entry_hook_e1: backpack_mara
d06 Sun 16:21 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d06 Sun 17:22 look entry_hook_e1: backpack_mara
d06 Sun 19:21 look bed_b1: (nothing)
d06 Sun 19:21 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d06 Sun 19:21 look desk_b1: (nothing)
d06 Sun 19:21 look nightstand_b1: phone_mara
d06 Sun 19:49 look entry_hook_e1: backpack_mara
d06 Sun 20:59 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d06 Sun 21:58 look armchair_l1: glasses_mara
d06 Sun 21:58 look bookshelf_l1: jacket_mara, lunchbox_mara
d06 Sun 21:58 look coffee_table_l1: mug_mara, remote_shared_1
d06 Sun 21:58 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d06 Sun 21:58 look tv_stand_l1: (nothing)
d06 Sun 23:17 look bookshelf_l1: jacket_mara, lunchbox_mara
d07 Mon 04:52 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d07 Mon 05:07 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara, laptop_mara, notebook_mara, pan_shared_1
d07 Mon 06:13 look chair_k1: (nothing)
d07 Mon 06:13 look chair_k2: (nothing)
d07 Mon 06:13 look counter_k1: pen_mara, tablet_mara
d07 Mon 06:13 look cupboard_k1: (nothing)
d07 Mon 06:13 look dish_rack_k1: mug_shared_1
d07 Mon 06:13 look kitchen_table_k1: bowl_shared_2, charger_mara, headphones_mara, laptop_mara, mug_mara, notebook_mara, pan_shared_1
d07 Mon 06:13 look sink_k1: plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d07 Mon 08:26 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d07 Mon 09:12 look entry_table_e1: bowl_shared_1
d07 Mon 09:23 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara, water_bottle_mara
d07 Mon 09:23 look towel_rack_ba1: towel_mara
d07 Mon 09:38 look kitchen_table_k1: mug_mara
d07 Mon 09:55 look coffee_table_l1: remote_shared_1
d07 Mon 10:32 look nightstand_b1: (nothing)
d07 Mon 10:49 look counter_k1: pan_shared_1, pen_mara, tablet_mara
d07 Mon 11:21 look counter_k1: pan_shared_1, pen_mara, tablet_mara
d07 Mon 12:35 look entry_floor_e1: umbrella_mara
d07 Mon 12:35 look entry_hook_e1: (nothing)
d07 Mon 12:35 look entry_table_e1: bowl_shared_1
d07 Mon 13:07 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d07 Mon 13:59 look nightstand_b1: (nothing)
d07 Mon 14:01 look counter_k1: pan_shared_1, pen_mara, tablet_mara
d07 Mon 14:06 look sink_k1: bowl_shared_2, plate_shared_1, plate_shared_2, pot_shared_1, watering_can_mara
d07 Mon 14:20 look kitchen_table_k1: mug_mara
d07 Mon 14:36 look kitchen_table_k1: mug_mara
d07 Mon 15:05 look entry_table_e1: bowl_shared_1
d07 Mon 15:37 look kitchen_table_k1: mug_mara
d07 Mon 15:37 look bookshelf_l1: (nothing)
d07 Mon 15:53 look bed_b1: (nothing)
d07 Mon 15:53 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d07 Mon 15:53 look desk_b1: (nothing)
d07 Mon 15:53 look nightstand_b1: (nothing)
d07 Mon 16:00 look counter_k1: pan_shared_1, pen_mara, tablet_mara
d07 Mon 16:17 look cupboard_k1: (nothing)
d07 Mon 16:21 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara, water_bottle_mara
d07 Mon 16:41 look kitchen_table_k1: charger_mara, glasses_mara, headphones_mara, laptop_mara, mug_mara, notebook_mara, phone_mara, plate_shared_2
d07 Mon 18:17 look entry_hook_e1: backpack_mara, jacket_mara
d07 Mon 18:59 look armchair_l1: (nothing)
d07 Mon 18:59 look bookshelf_l1: (nothing)
d07 Mon 18:59 look coffee_table_l1: remote_shared_1
d07 Mon 18:59 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d07 Mon 18:59 look tv_stand_l1: (nothing)
d07 Mon 19:11 look sink_k1: bowl_shared_2, mug_mara, pan_shared_1, pot_shared_1, watering_can_mara
d07 Mon 22:18 look chair_k1: charger_mara, wallet_mara
d07 Mon 22:18 look chair_k2: (nothing)
d07 Mon 22:18 look counter_k1: lunchbox_mara, pen_mara, tablet_mara
d07 Mon 22:18 look cupboard_k1: (nothing)
d07 Mon 22:18 look dish_rack_k1: mug_shared_1, plate_shared_1
d07 Mon 22:18 look kitchen_table_k1: glasses_mara, headphones_mara, laptop_mara, notebook_mara, phone_mara, plate_shared_2
d07 Mon 22:18 look sink_k1: bowl_shared_2, mug_mara, pan_shared_1, pot_shared_1, watering_can_mara
d08 Tue 05:33 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d08 Tue 05:34 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d08 Tue 05:59 look entry_hook_e1: backpack_mara, jacket_mara
d08 Tue 06:38 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d08 Tue 06:38 look towel_rack_ba1: towel_mara
d08 Tue 06:48 look kitchen_table_k1: bowl_shared_2, glasses_mara, headphones_mara, laptop_mara, notebook_mara, pan_shared_1, pen_mara
d08 Tue 08:00 look sink_k1: plate_shared_2, pot_shared_1, watering_can_mara
d08 Tue 08:40 look kitchen_table_k1: bowl_shared_2, notebook_mara, pan_shared_1, pen_mara
d08 Tue 09:38 look entry_floor_e1: umbrella_mara
d08 Tue 09:38 look entry_hook_e1: (nothing)
d08 Tue 09:38 look entry_table_e1: bowl_shared_1
d08 Tue 09:44 look counter_k1: mug_mara, tablet_mara
d08 Tue 11:30 look cupboard_k1: (nothing)
d08 Tue 11:52 look kitchen_table_k1: bowl_shared_2, notebook_mara, pan_shared_1, pen_mara
d08 Tue 12:49 look bed_b1: (nothing)
d08 Tue 12:49 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d08 Tue 12:49 look desk_b1: (nothing)
d08 Tue 12:49 look nightstand_b1: water_bottle_mara
d08 Tue 14:00 look kitchen_table_k1: bowl_shared_2, notebook_mara, pan_shared_1, pen_mara
d08 Tue 15:11 look sink_k1: plate_shared_2, pot_shared_1, watering_can_mara
d08 Tue 15:15 look kitchen_table_k1: bowl_shared_2, notebook_mara, pan_shared_1, pen_mara
d08 Tue 15:33 look sink_k1: plate_shared_2, pot_shared_1, watering_can_mara
d08 Tue 15:35 look counter_k1: mug_mara, tablet_mara
d08 Tue 15:45 look entry_table_e1: bowl_shared_1
d08 Tue 15:57 look armchair_l1: (nothing)
d08 Tue 15:57 look bookshelf_l1: (nothing)
d08 Tue 15:57 look coffee_table_l1: remote_shared_1
d08 Tue 15:57 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d08 Tue 15:57 look tv_stand_l1: (nothing)
d08 Tue 16:01 look entry_hook_e1: (nothing)
d08 Tue 16:06 look cupboard_k1: (nothing)
d08 Tue 16:40 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, notebook_mara, pan_shared_1, pen_mara
d08 Tue 18:23 look entry_table_e1: bowl_shared_1
d08 Tue 19:22 look chair_k1: jacket_mara
d08 Tue 19:22 look chair_k2: wallet_mara
d08 Tue 19:22 look counter_k1: lunchbox_mara, mug_mara, tablet_mara
d08 Tue 19:22 look cupboard_k1: (nothing)
d08 Tue 19:22 look dish_rack_k1: mug_shared_1
d08 Tue 19:22 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, laptop_mara, notebook_mara, pan_shared_1, pen_mara, plate_shared_1
d08 Tue 19:22 look sink_k1: headphones_mara, plate_shared_2, pot_shared_1, watering_can_mara
d08 Tue 22:29 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara
d08 Tue 22:29 look towel_rack_ba1: towel_mara
d08 Tue 22:48 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d08 Tue 23:00 look entry_table_e1: bowl_shared_1
d09 Wed 00:24 look cupboard_k1: (nothing)
d09 Wed 05:57 look entry_floor_e1: umbrella_mara
d09 Wed 05:57 look entry_hook_e1: backpack_mara, keys_mara
d09 Wed 05:57 look entry_table_e1: bowl_shared_1
d09 Wed 06:21 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, laptop_mara, mug_mara, notebook_mara, pan_shared_1, pen_mara, plate_shared_1
d09 Wed 06:53 look entry_table_e1: bowl_shared_1
d09 Wed 07:26 look counter_k1: pen_mara, tablet_mara
d09 Wed 07:34 look sink_k1: plate_shared_2, pot_shared_1, watering_can_mara
d09 Wed 07:58 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d09 Wed 08:56 look sink_k1: plate_shared_2, pot_shared_1, watering_can_mara
d09 Wed 08:56 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, notebook_mara, pan_shared_1, plate_shared_1
d09 Wed 09:04 look entry_hook_e1: (nothing)
d09 Wed 09:12 look bed_b1: (nothing)
d09 Wed 09:12 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d09 Wed 09:12 look desk_b1: (nothing)
d09 Wed 09:12 look nightstand_b1: (nothing)
d09 Wed 09:45 look entry_table_e1: bowl_shared_1
d09 Wed 10:37 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, notebook_mara, pan_shared_1, plate_shared_1
d09 Wed 10:59 look counter_k1: pen_mara, tablet_mara
d09 Wed 11:54 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d09 Wed 12:31 look sink_k1: plate_shared_2, pot_shared_1, watering_can_mara
d09 Wed 12:36 look armchair_l1: (nothing)
d09 Wed 12:36 look bookshelf_l1: (nothing)
d09 Wed 12:36 look coffee_table_l1: remote_shared_1
d09 Wed 12:36 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d09 Wed 12:36 look tv_stand_l1: (nothing)
d09 Wed 13:19 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, notebook_mara, pan_shared_1, plate_shared_1
d09 Wed 13:19 look nightstand_b1: (nothing)
d09 Wed 14:03 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, notebook_mara, pan_shared_1, plate_shared_1
d09 Wed 14:16 look entry_hook_e1: (nothing)
d09 Wed 14:48 look counter_k1: pen_mara, tablet_mara
d09 Wed 15:32 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, notebook_mara, pan_shared_1, plate_shared_1
d09 Wed 15:35 look entry_table_e1: bowl_shared_1
d09 Wed 15:54 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d09 Wed 15:58 look chair_k1: backpack_mara, jacket_mara
d09 Wed 15:58 look chair_k2: (nothing)
d09 Wed 15:58 look counter_k1: pen_mara, tablet_mara
d09 Wed 15:58 look cupboard_k1: (nothing)
d09 Wed 15:58 look dish_rack_k1: mug_shared_1
d09 Wed 15:58 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara, mug_mara, notebook_mara, pan_shared_1, plate_shared_1, plate_shared_2, water_bottle_mara
d09 Wed 15:58 look sink_k1: lunchbox_mara, pot_shared_1, watering_can_mara
d09 Wed 18:48 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara, mug_mara, notebook_mara, plate_shared_1, plate_shared_2, water_bottle_mara
d09 Wed 19:12 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d09 Wed 19:12 look towel_rack_ba1: towel_mara
d09 Wed 20:47 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara, mug_mara, notebook_mara, plate_shared_2, water_bottle_mara
d09 Wed 22:15 look entry_floor_e1: umbrella_mara
d09 Wed 22:15 look entry_hook_e1: (nothing)
d09 Wed 22:15 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d10 Thu 04:33 look counter_k1: lunchbox_mara, pen_mara, tablet_mara
d10 Thu 04:38 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara, mug_mara, notebook_mara, plate_shared_2
d10 Thu 04:46 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara, mug_mara, notebook_mara, plate_shared_2
d10 Thu 04:46 look couch_l1: blanket_mara, book_mara, remote_shared_1, yoga_mat_mara
d10 Thu 05:20 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, headphones_mara, laptop_mara, mug_mara, notebook_mara, plate_shared_2
d10 Thu 05:20 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d10 Thu 06:10 look bed_b1: (nothing)
d10 Thu 06:10 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d10 Thu 06:10 look desk_b1: (nothing)
d10 Thu 06:10 look nightstand_b1: water_bottle_mara
d10 Thu 06:30 look sink_k1: bowl_shared_2, plate_shared_1, pot_shared_1, watering_can_mara
d10 Thu 07:18 look entry_hook_e1: (nothing)
d10 Thu 07:53 look kitchen_table_k1: laptop_mara, mug_mara, pan_shared_1, pen_mara
d10 Thu 07:53 look nightstand_b1: (nothing)
d10 Thu 08:32 look entry_hook_e1: (nothing)
d10 Thu 09:12 look kitchen_table_k1: laptop_mara, mug_mara, pan_shared_1, pen_mara
d10 Thu 09:19 look couch_l1: blanket_mara, book_mara, remote_shared_1, yoga_mat_mara
d10 Thu 09:33 look armchair_l1: (nothing)
d10 Thu 09:33 look bookshelf_l1: (nothing)
d10 Thu 09:33 look coffee_table_l1: (nothing)
d10 Thu 09:33 look couch_l1: blanket_mara, book_mara, remote_shared_1, yoga_mat_mara
d10 Thu 09:33 look tv_stand_l1: (nothing)
d10 Thu 10:09 look counter_k1: plate_shared_2, tablet_mara
d10 Thu 10:11 look nightstand_b1: (nothing)
d10 Thu 11:10 look entry_hook_e1: (nothing)
d10 Thu 11:10 look chair_k1: backpack_mara
d10 Thu 11:13 look entry_table_e1: bowl_shared_1
d10 Thu 12:05 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d10 Thu 12:39 look chair_k1: backpack_mara
d10 Thu 12:39 look chair_k2: (nothing)
d10 Thu 12:39 look counter_k1: plate_shared_2, tablet_mara
d10 Thu 12:39 look cupboard_k1: (nothing)
d10 Thu 12:39 look dish_rack_k1: mug_shared_1
d10 Thu 12:39 look kitchen_table_k1: laptop_mara, mug_mara, pan_shared_1, pen_mara
d10 Thu 12:39 look sink_k1: bowl_shared_2, plate_shared_1, pot_shared_1, watering_can_mara
d10 Thu 13:27 look counter_k1: plate_shared_2, tablet_mara
d10 Thu 14:22 look entry_table_e1: bowl_shared_1
d10 Thu 14:29 look cupboard_k1: (nothing)
d10 Thu 15:48 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara, medication_bottle_mara, notebook_mara, phone_mara
d10 Thu 15:48 look towel_rack_ba1: towel_mara, wallet_mara, water_bottle_mara
d10 Thu 16:26 look kitchen_table_k1: glasses_mara, laptop_mara, mug_mara, pan_shared_1
d10 Thu 16:33 look sink_k1: bowl_shared_2, plate_shared_1, pot_shared_1, watering_can_mara
d10 Thu 19:16 look entry_floor_e1: umbrella_mara
d10 Thu 19:16 look entry_hook_e1: charger_mara, jacket_mara
d10 Thu 19:16 look entry_table_e1: bowl_shared_1, keys_mara
d10 Thu 22:24 look bed_b1: (nothing)
d10 Thu 22:24 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d10 Thu 22:24 look desk_b1: (nothing)
d10 Thu 22:24 look nightstand_b1: water_bottle_mara
d11 Fri 05:33 look sink_k1: bowl_shared_2, plate_shared_1, pot_shared_1, watering_can_mara
d11 Fri 05:44 look kitchen_table_k1: glasses_mara, laptop_mara, mug_mara, pan_shared_1
d11 Fri 06:19 look cupboard_k1: (nothing)
d11 Fri 06:33 look armchair_l1: (nothing)
d11 Fri 06:33 look bookshelf_l1: (nothing)
d11 Fri 06:33 look coffee_table_l1: (nothing)
d11 Fri 06:33 look couch_l1: blanket_mara, book_mara, remote_shared_1, yoga_mat_mara
d11 Fri 06:33 look tv_stand_l1: (nothing)
d11 Fri 06:48 look entry_table_e1: bowl_shared_1, keys_mara
d11 Fri 06:56 look entry_table_e1: bowl_shared_1, keys_mara
d11 Fri 08:02 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara, notebook_mara
d11 Fri 08:26 look towel_rack_ba1: towel_mara, wallet_mara
d11 Fri 08:33 look chair_k1: backpack_mara
d11 Fri 08:33 look chair_k2: (nothing)
d11 Fri 08:33 look counter_k1: charger_mara, lunchbox_mara, medication_bottle_mara, pan_shared_1, pen_mara, plate_shared_2, tablet_mara
d11 Fri 08:33 look cupboard_k1: (nothing)
d11 Fri 08:33 look dish_rack_k1: mug_shared_1
d11 Fri 08:33 look kitchen_table_k1: bowl_shared_2, glasses_mara, laptop_mara, mug_mara, notebook_mara
d11 Fri 08:33 look sink_k1: plate_shared_1, pot_shared_1, watering_can_mara
d11 Fri 08:38 look sink_k1: plate_shared_1, pot_shared_1, watering_can_mara
d11 Fri 08:51 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara
d11 Fri 08:54 look entry_hook_e1: jacket_mara
d11 Fri 09:13 look sink_k1: plate_shared_1, pot_shared_1, watering_can_mara
d11 Fri 09:38 look towel_rack_ba1: towel_mara, wallet_mara
d11 Fri 09:48 look kitchen_table_k1: bowl_shared_2, glasses_mara, laptop_mara, mug_mara, notebook_mara
d11 Fri 10:06 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara
d11 Fri 10:06 look nightstand_b1: phone_mara, water_bottle_mara
d11 Fri 10:57 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara
d11 Fri 10:57 look towel_rack_ba1: towel_mara, wallet_mara
d11 Fri 10:58 look counter_k1: charger_mara, lunchbox_mara, medication_bottle_mara, pan_shared_1, pen_mara, plate_shared_2, tablet_mara
d11 Fri 14:03 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, plate_shared_2
d11 Fri 14:07 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara
d11 Fri 14:21 look counter_k1: lunchbox_mara, medication_bottle_mara, pan_shared_1, pen_mara, tablet_mara
d11 Fri 14:32 look entry_floor_e1: umbrella_mara
d11 Fri 14:32 look entry_hook_e1: jacket_mara
d11 Fri 14:32 look entry_table_e1: bowl_shared_1, keys_mara
d11 Fri 14:57 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara
d11 Fri 14:57 look sink_k1: plate_shared_1, pot_shared_1, watering_can_mara
d11 Fri 15:22 look towel_rack_ba1: towel_mara, wallet_mara
d11 Fri 15:37 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara
d11 Fri 15:38 look counter_k1: lunchbox_mara, medication_bottle_mara, pen_mara, plate_shared_2, tablet_mara
d11 Fri 16:50 look bed_b1: (nothing)
d11 Fri 16:50 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d11 Fri 16:50 look desk_b1: (nothing)
d11 Fri 16:50 look nightstand_b1: glasses_mara, phone_mara, water_bottle_mara
d11 Fri 18:50 look armchair_l1: (nothing)
d11 Fri 18:50 look bookshelf_l1: (nothing)
d11 Fri 18:50 look coffee_table_l1: notebook_mara, remote_shared_1
d11 Fri 18:50 look couch_l1: blanket_mara, book_mara, yoga_mat_mara
d11 Fri 18:50 look tv_stand_l1: (nothing)
d12 Sat 06:00 look counter_k1: lunchbox_mara, pan_shared_1, pen_mara, plate_shared_2, tablet_mara
d12 Sat 06:18 look kitchen_table_k1: bowl_shared_2, laptop_mara, mug_mara, plate_shared_1
d12 Sat 06:31 look entry_table_e1: bowl_shared_1, keys_mara
d12 Sat 06:53 look cupboard_k1: charger_mara
d12 Sat 07:23 look nightstand_b1: glasses_mara, phone_mara, water_bottle_mara
d12 Sat 07:27 look chair_k1: backpack_mara
d12 Sat 07:27 look chair_k2: (nothing)
d12 Sat 07:27 look counter_k1: lunchbox_mara, mug_mara, pan_shared_1, pen_mara, plate_shared_2, tablet_mara
d12 Sat 07:27 look cupboard_k1: charger_mara
d12 Sat 07:27 look dish_rack_k1: mug_shared_1
d12 Sat 07:27 look kitchen_table_k1: bowl_shared_2, laptop_mara, plate_shared_1
d12 Sat 07:27 look sink_k1: pot_shared_1, watering_can_mara
d12 Sat 07:38 look nightstand_b1: glasses_mara, phone_mara, water_bottle_mara
d12 Sat 07:45 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara, medication_bottle_mara
d12 Sat 08:43 look sink_k1: pot_shared_1, watering_can_mara
d12 Sat 08:48 look towel_rack_ba1: towel_mara, wallet_mara
d12 Sat 09:35 look kitchen_table_k1: bowl_shared_2, laptop_mara, plate_shared_1
d12 Sat 10:26 look sink_k1: pot_shared_1, watering_can_mara
d12 Sat 10:35 look kitchen_table_k1: bowl_shared_2, laptop_mara, plate_shared_1
d12 Sat 11:03 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara, medication_bottle_mara
d12 Sat 11:03 look towel_rack_ba1: towel_mara, wallet_mara
d12 Sat 11:20 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara, medication_bottle_mara
d12 Sat 11:55 look couch_l1: blanket_mara, book_mara, remote_shared_1, yoga_mat_mara
d12 Sat 13:01 look sink_k1: plate_shared_2, watering_can_mara
d12 Sat 13:15 look entry_hook_e1: backpack_mara, jacket_mara
d12 Sat 13:39 look sink_k1: plate_shared_2, watering_can_mara
d12 Sat 14:04 look entry_floor_e1: umbrella_mara
d12 Sat 14:04 look entry_hook_e1: backpack_mara, jacket_mara
d12 Sat 14:04 look entry_table_e1: bowl_shared_1, keys_mara
d12 Sat 14:14 look counter_k1: lunchbox_mara, pan_shared_1, tablet_mara
d12 Sat 14:21 look kitchen_table_k1: bowl_shared_2, laptop_mara, pen_mara
d12 Sat 14:30 look bathroom_shelf_ba1: hairbrush_mara, headphones_mara, makeup_kit_mara, medication_bottle_mara
d12 Sat 14:44 look counter_k1: lunchbox_mara, pan_shared_1, tablet_mara
d12 Sat 16:46 look bed_b1: (nothing)
d12 Sat 16:46 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d12 Sat 16:46 look desk_b1: (nothing)
d12 Sat 16:46 look nightstand_b1: glasses_mara, phone_mara, water_bottle_mara
d12 Sat 17:06 look kitchen_table_k1: bowl_shared_2, laptop_mara, pan_shared_1, pen_mara, plate_shared_1
d12 Sat 17:55 look nightstand_b1: glasses_mara, phone_mara, water_bottle_mara
d12 Sat 18:02 look nightstand_b1: glasses_mara, phone_mara, water_bottle_mara
d12 Sat 19:40 look armchair_l1: (nothing)
d12 Sat 19:40 look bookshelf_l1: (nothing)
d12 Sat 19:40 look coffee_table_l1: notebook_mara
d12 Sat 19:40 look couch_l1: blanket_mara, book_mara, remote_shared_1, yoga_mat_mara
d12 Sat 19:40 look tv_stand_l1: (nothing)
d12 Sat 22:29 look chair_k1: (nothing)
d12 Sat 22:29 look chair_k2: mug_mara
d12 Sat 22:29 look counter_k1: lunchbox_mara, tablet_mara
d12 Sat 22:29 look cupboard_k1: charger_mara, pot_shared_1
d12 Sat 22:29 look dish_rack_k1: mug_shared_1
d12 Sat 22:29 look kitchen_table_k1: bowl_shared_2, laptop_mara, pan_shared_1, pen_mara
d12 Sat 22:29 look sink_k1: plate_shared_1, plate_shared_2, watering_can_mara
d13 Sun 08:19 look bathroom_shelf_ba1: makeup_kit_mara, medication_bottle_mara
d13 Sun 08:19 look towel_rack_ba1: hairbrush_mara
d13 Sun 09:16 look cupboard_k1: charger_mara, pot_shared_1
d13 Sun 10:09 look couch_l1: blanket_mara, book_mara, remote_shared_1, yoga_mat_mara
d13 Sun 10:09 look entry_hook_e1: jacket_mara
d13 Sun 10:11 look towel_rack_ba1: hairbrush_mara
d13 Sun 10:47 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d13 Sun 10:51 look sink_k1: mug_mara, pan_shared_1, plate_shared_1, pot_shared_1, watering_can_mara
d13 Sun 10:54 look nightstand_b1: phone_mara, water_bottle_mara
d13 Sun 11:00 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pen_mara, plate_shared_2
d13 Sun 11:09 look entry_floor_e1: umbrella_mara
d13 Sun 11:09 look entry_hook_e1: jacket_mara
d13 Sun 11:09 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d13 Sun 12:28 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pen_mara, plate_shared_2
d13 Sun 13:08 look counter_k1: lunchbox_mara, tablet_mara
d13 Sun 13:54 look bed_b1: (nothing)
d13 Sun 13:54 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, towel_mara, vacuum_cleaner_shared_1
d13 Sun 13:54 look desk_b1: (nothing)
d13 Sun 13:54 look nightstand_b1: phone_mara, water_bottle_mara
d13 Sun 14:34 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pen_mara, plate_shared_2
d13 Sun 14:34 look dish_rack_k1: mug_shared_1, plate_shared_1, pot_shared_1
d13 Sun 15:10 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pen_mara, plate_shared_2
d13 Sun 16:04 look counter_k1: lunchbox_mara, tablet_mara
d13 Sun 16:43 look entry_hook_e1: (nothing)
d13 Sun 16:53 look armchair_l1: jacket_mara
d13 Sun 16:53 look bookshelf_l1: (nothing)
d13 Sun 16:53 look coffee_table_l1: book_mara, glasses_mara, notebook_mara
d13 Sun 16:53 look couch_l1: blanket_mara, mug_mara, remote_shared_1, yoga_mat_mara
d13 Sun 16:53 look tv_stand_l1: (nothing)
d13 Sun 16:56 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pen_mara, plate_shared_2
d13 Sun 17:06 look entry_hook_e1: (nothing)
d13 Sun 18:05 look nightstand_b1: phone_mara, water_bottle_mara
d13 Sun 18:28 look counter_k1: lunchbox_mara, tablet_mara
d13 Sun 18:37 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pen_mara, plate_shared_1, plate_shared_2
d13 Sun 18:41 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d13 Sun 19:06 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pen_mara, plate_shared_1, plate_shared_2
d13 Sun 19:50 look chair_k1: backpack_mara
d13 Sun 19:50 look chair_k2: (nothing)
d13 Sun 19:50 look counter_k1: lunchbox_mara, pan_shared_1, tablet_mara
d13 Sun 19:50 look cupboard_k1: charger_mara
d13 Sun 19:50 look dish_rack_k1: mug_shared_1, pot_shared_1
d13 Sun 19:50 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pen_mara, plate_shared_1, plate_shared_2
d13 Sun 19:50 look sink_k1: watering_can_mara
d13 Sun 20:08 look armchair_l1: jacket_mara
d13 Sun 20:15 look coffee_table_l1: book_mara, glasses_mara, notebook_mara
d13 Sun 22:27 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d13 Sun 22:27 look towel_rack_ba1: (nothing)
d14 Mon 05:18 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pen_mara, plate_shared_1, plate_shared_2
d14 Mon 05:22 look entry_hook_e1: (nothing)
d14 Mon 05:24 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pen_mara, plate_shared_1, plate_shared_2
d14 Mon 06:09 look kitchen_table_k1: bowl_shared_2, headphones_mara, laptop_mara, pan_shared_1, pen_mara, plate_shared_1, plate_shared_2
d14 Mon 06:14 look entry_floor_e1: umbrella_mara
d14 Mon 06:14 look entry_hook_e1: (nothing)
d14 Mon 06:14 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d14 Mon 06:27 look counter_k1: lunchbox_mara, mug_mara, pen_mara, tablet_mara
d14 Mon 06:33 look cupboard_k1: (nothing)
d14 Mon 06:56 look kitchen_table_k1: pan_shared_1, plate_shared_1
d14 Mon 07:07 look entry_hook_e1: (nothing)
d14 Mon 07:38 look kitchen_table_k1: pan_shared_1, plate_shared_1
d14 Mon 08:10 look counter_k1: lunchbox_mara, mug_mara, pen_mara, tablet_mara
d14 Mon 08:40 look entry_table_e1: bowl_shared_1, keys_mara
d14 Mon 08:53 look nightstand_b1: (nothing)
d14 Mon 09:28 look bed_b1: (nothing)
d14 Mon 09:28 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d14 Mon 09:28 look desk_b1: (nothing)
d14 Mon 09:28 look nightstand_b1: (nothing)
d14 Mon 09:40 look kitchen_table_k1: pan_shared_1, plate_shared_1
d14 Mon 10:17 look entry_hook_e1: (nothing)
d14 Mon 11:10 look counter_k1: lunchbox_mara, mug_mara, pen_mara, tablet_mara
d14 Mon 11:26 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d14 Mon 11:48 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d14 Mon 11:59 look entry_table_e1: bowl_shared_1, keys_mara
d14 Mon 12:26 look entry_table_e1: bowl_shared_1, keys_mara
d14 Mon 12:41 look armchair_l1: (nothing)
d14 Mon 12:41 look bookshelf_l1: (nothing)
d14 Mon 12:41 look coffee_table_l1: book_mara, notebook_mara
d14 Mon 12:41 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d14 Mon 12:41 look tv_stand_l1: (nothing)
d14 Mon 13:04 look kitchen_table_k1: pan_shared_1, plate_shared_1
d14 Mon 13:04 look sink_k1: bowl_shared_2, plate_shared_2, watering_can_mara
d14 Mon 13:32 look cupboard_k1: (nothing)
d14 Mon 13:37 look dish_rack_k1: mug_shared_1, pot_shared_1
d14 Mon 14:27 look kitchen_table_k1: pan_shared_1, plate_shared_1
d14 Mon 15:50 look chair_k1: backpack_mara
d14 Mon 15:50 look chair_k2: (nothing)
d14 Mon 15:50 look counter_k1: lunchbox_mara, mug_mara, pen_mara, tablet_mara
d14 Mon 15:50 look cupboard_k1: (nothing)
d14 Mon 15:50 look dish_rack_k1: mug_shared_1, pot_shared_1
d14 Mon 15:50 look kitchen_table_k1: pan_shared_1, plate_shared_1
d14 Mon 15:50 look sink_k1: bowl_shared_2, plate_shared_2, watering_can_mara
d14 Mon 19:03 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d14 Mon 19:03 look towel_rack_ba1: towel_mara
d14 Mon 22:32 look entry_floor_e1: umbrella_mara
d14 Mon 22:32 look entry_hook_e1: headphones_mara
d14 Mon 22:32 look entry_table_e1: keys_mara, wallet_mara
d15 Tue 00:18 look nightstand_b1: book_mara
d15 Tue 04:36 look kitchen_table_k1: charger_mara, glasses_mara, laptop_mara, water_bottle_mara
d15 Tue 04:55 look kitchen_table_k1: charger_mara, glasses_mara, laptop_mara, water_bottle_mara
d15 Tue 05:29 look bathroom_shelf_ba1: makeup_kit_mara, medication_bottle_mara
d15 Tue 05:36 look coffee_table_l1: notebook_mara
d15 Tue 05:38 look entry_hook_e1: headphones_mara
d15 Tue 05:43 look bed_b1: (nothing)
d15 Tue 05:43 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d15 Tue 05:43 look desk_b1: (nothing)
d15 Tue 05:43 look nightstand_b1: book_mara
d15 Tue 06:04 look nightstand_b1: book_mara
d15 Tue 06:05 look entry_hook_e1: headphones_mara
d15 Tue 06:41 look entry_table_e1: keys_mara, wallet_mara
d15 Tue 07:12 look counter_k1: bowl_shared_1, lunchbox_mara, pan_shared_1, plate_shared_2, tablet_mara
d15 Tue 07:17 look kitchen_table_k1: bowl_shared_2, charger_mara, glasses_mara, laptop_mara, mug_mara, pen_mara, water_bottle_mara
d15 Tue 08:24 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d15 Tue 08:34 look nightstand_b1: book_mara
d15 Tue 08:44 look cupboard_k1: (nothing)
d15 Tue 09:07 look armchair_l1: (nothing)
d15 Tue 09:07 look bookshelf_l1: (nothing)
d15 Tue 09:07 look coffee_table_l1: (nothing)
d15 Tue 09:07 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d15 Tue 09:07 look tv_stand_l1: (nothing)
d15 Tue 09:13 look counter_k1: bowl_shared_1, lunchbox_mara, pan_shared_1, plate_shared_2, tablet_mara
d15 Tue 11:44 look kitchen_table_k1: bowl_shared_2, mug_mara, pen_mara
d15 Tue 12:12 look coffee_table_l1: (nothing)
d15 Tue 12:19 look chair_k1: (nothing)
d15 Tue 12:19 look chair_k2: (nothing)
d15 Tue 12:19 look counter_k1: bowl_shared_1, lunchbox_mara, pan_shared_1, plate_shared_2, tablet_mara
d15 Tue 12:19 look cupboard_k1: (nothing)
d15 Tue 12:19 look dish_rack_k1: mug_shared_1, pot_shared_1
d15 Tue 12:19 look kitchen_table_k1: bowl_shared_2, mug_mara, pen_mara
d15 Tue 12:19 look sink_k1: plate_shared_1, watering_can_mara
d15 Tue 13:49 look towel_rack_ba1: towel_mara
d15 Tue 14:00 look entry_table_e1: (nothing)
d15 Tue 14:27 look sink_k1: plate_shared_1, watering_can_mara
d15 Tue 14:31 look kitchen_table_k1: bowl_shared_2, mug_mara, pen_mara
d15 Tue 14:46 look kitchen_table_k1: bowl_shared_2, mug_mara, pen_mara
d15 Tue 14:47 look sink_k1: plate_shared_1, watering_can_mara
d15 Tue 15:47 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d15 Tue 15:47 look towel_rack_ba1: towel_mara
d15 Tue 15:51 look entry_hook_e1: (nothing)
d15 Tue 18:58 look entry_floor_e1: umbrella_mara
d15 Tue 18:58 look entry_hook_e1: backpack_mara, charger_mara
d15 Tue 18:58 look entry_table_e1: (nothing)
d15 Tue 22:17 look bed_b1: (nothing)
d15 Tue 22:17 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d15 Tue 22:17 look desk_b1: (nothing)
d15 Tue 22:17 look nightstand_b1: book_mara, water_bottle_mara
d16 Wed 04:54 look kitchen_table_k1: bowl_shared_2, glasses_mara, headphones_mara, mug_mara, notebook_mara, pen_mara, plate_shared_1, plate_shared_2
d16 Wed 05:13 look kitchen_table_k1: bowl_shared_2, glasses_mara, headphones_mara, mug_mara, notebook_mara, pen_mara, plate_shared_1, plate_shared_2
d16 Wed 05:17 look cupboard_k1: (nothing)
d16 Wed 05:24 look armchair_l1: (nothing)
d16 Wed 05:24 look bookshelf_l1: (nothing)
d16 Wed 05:24 look coffee_table_l1: (nothing)
d16 Wed 05:24 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d16 Wed 05:24 look tv_stand_l1: (nothing)
d16 Wed 05:41 look kitchen_table_k1: bowl_shared_2, glasses_mara, headphones_mara, notebook_mara, pen_mara, plate_shared_1, plate_shared_2
d16 Wed 07:14 look kitchen_table_k1: pan_shared_1, plate_shared_1
d16 Wed 07:20 look towel_rack_ba1: towel_mara
d16 Wed 07:37 look counter_k1: bowl_shared_1, mug_mara, pen_mara, plate_shared_2, tablet_mara
d16 Wed 07:37 look entry_table_e1: (nothing)
d16 Wed 08:50 look chair_k1: (nothing)
d16 Wed 08:50 look chair_k2: (nothing)
d16 Wed 08:50 look counter_k1: bowl_shared_1, mug_mara, pen_mara, plate_shared_2, tablet_mara
d16 Wed 08:50 look cupboard_k1: (nothing)
d16 Wed 08:50 look dish_rack_k1: mug_shared_1, pot_shared_1
d16 Wed 08:50 look kitchen_table_k1: pan_shared_1, plate_shared_1
d16 Wed 08:50 look sink_k1: bowl_shared_2, watering_can_mara
d16 Wed 08:54 look nightstand_b1: book_mara
d16 Wed 09:07 look kitchen_table_k1: pan_shared_1, plate_shared_1
d16 Wed 09:32 look entry_hook_e1: charger_mara
d16 Wed 09:38 look kitchen_table_k1: pan_shared_1, plate_shared_1
d16 Wed 09:53 look sink_k1: bowl_shared_2, watering_can_mara
d16 Wed 10:19 look kitchen_table_k1: pan_shared_1, plate_shared_1
d16 Wed 10:40 look entry_hook_e1: charger_mara
d16 Wed 10:44 look kitchen_table_k1: pan_shared_1, plate_shared_1
d16 Wed 11:45 look dish_rack_k1: mug_shared_1, pot_shared_1
d16 Wed 11:50 look kitchen_table_k1: pan_shared_1, plate_shared_1
d16 Wed 11:52 look nightstand_b1: book_mara
d16 Wed 12:00 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d16 Wed 12:00 look towel_rack_ba1: towel_mara
d16 Wed 13:24 look counter_k1: bowl_shared_1, mug_mara, pen_mara, plate_shared_2, tablet_mara
d16 Wed 14:55 look kitchen_table_k1: pan_shared_1, plate_shared_1
d16 Wed 14:55 look entry_hook_e1: charger_mara
d16 Wed 15:26 look entry_floor_e1: umbrella_mara
d16 Wed 15:26 look entry_hook_e1: charger_mara
d16 Wed 15:26 look entry_table_e1: (nothing)
d16 Wed 16:36 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d16 Wed 17:04 look entry_table_e1: keys_mara, wallet_mara
d16 Wed 18:48 look bed_b1: (nothing)
d16 Wed 18:48 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d16 Wed 18:48 look desk_b1: (nothing)
d16 Wed 18:48 look nightstand_b1: book_mara, phone_mara
d16 Wed 22:04 look armchair_l1: (nothing)
d16 Wed 22:04 look bookshelf_l1: (nothing)
d16 Wed 22:04 look coffee_table_l1: (nothing)
d16 Wed 22:04 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d16 Wed 22:04 look tv_stand_l1: (nothing)
d17 Thu 05:17 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d17 Thu 05:35 look nightstand_b1: book_mara, phone_mara, water_bottle_mara
d17 Thu 05:39 look entry_hook_e1: charger_mara, headphones_mara, jacket_mara
d17 Thu 06:22 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d17 Thu 06:27 look kitchen_table_k1: bowl_shared_2, laptop_mara, notebook_mara
d17 Thu 06:36 look chair_k1: backpack_mara
d17 Thu 06:36 look chair_k2: glasses_mara
d17 Thu 06:36 look counter_k1: bowl_shared_1, medication_bottle_mara, mug_mara, pan_shared_1, pen_mara, plate_shared_2, tablet_mara
d17 Thu 06:36 look cupboard_k1: (nothing)
d17 Thu 06:36 look dish_rack_k1: lunchbox_mara, mug_shared_1, pot_shared_1
d17 Thu 06:36 look kitchen_table_k1: bowl_shared_2, laptop_mara, notebook_mara
d17 Thu 06:36 look sink_k1: plate_shared_1, watering_can_mara
d17 Thu 07:11 look entry_hook_e1: charger_mara, headphones_mara, jacket_mara
d17 Thu 09:06 look counter_k1: bowl_shared_1, medication_bottle_mara, mug_mara, pan_shared_1, plate_shared_2, tablet_mara
d17 Thu 09:14 look counter_k1: bowl_shared_1, medication_bottle_mara, mug_mara, pan_shared_1, plate_shared_2, tablet_mara
d17 Thu 09:21 look kitchen_table_k1: bowl_shared_2
d17 Thu 09:52 look bathroom_shelf_ba1: makeup_kit_mara
d17 Thu 09:52 look towel_rack_ba1: towel_mara
d17 Thu 09:59 look sink_k1: plate_shared_1, watering_can_mara
d17 Thu 10:12 look bathroom_shelf_ba1: makeup_kit_mara
d17 Thu 10:37 look kitchen_table_k1: bowl_shared_2
d17 Thu 10:39 look chair_k1: (nothing)
d17 Thu 10:56 look kitchen_table_k1: bowl_shared_2
d17 Thu 11:07 look kitchen_table_k1: bowl_shared_2
d17 Thu 11:09 look counter_k1: bowl_shared_1, medication_bottle_mara, mug_mara, pan_shared_1, plate_shared_2, tablet_mara
d17 Thu 11:17 look entry_table_e1: (nothing)
d17 Thu 11:29 look bathroom_shelf_ba1: makeup_kit_mara
d17 Thu 12:12 look kitchen_table_k1: bowl_shared_2
d17 Thu 12:36 look nightstand_b1: book_mara, hairbrush_mara, water_bottle_mara
d17 Thu 12:48 look entry_table_e1: (nothing)
d17 Thu 12:54 look entry_floor_e1: umbrella_mara
d17 Thu 12:54 look entry_hook_e1: (nothing)
d17 Thu 12:54 look entry_table_e1: (nothing)
d17 Thu 13:05 look entry_table_e1: (nothing)
d17 Thu 14:07 look bathroom_shelf_ba1: makeup_kit_mara
d17 Thu 14:49 look kitchen_table_k1: bowl_shared_2
d17 Thu 16:15 look bed_b1: (nothing)
d17 Thu 16:15 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d17 Thu 16:15 look desk_b1: (nothing)
d17 Thu 16:15 look nightstand_b1: book_mara, hairbrush_mara, water_bottle_mara
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
d18 Fri 05:20 look kitchen_table_k1: bowl_shared_2, laptop_mara, notebook_mara, plate_shared_1
d18 Fri 06:03 look entry_hook_e1: backpack_mara, charger_mara
d18 Fri 06:28 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d18 Fri 06:28 look towel_rack_ba1: towel_mara
d18 Fri 06:43 look kitchen_table_k1: pan_shared_1, pen_mara, plate_shared_1
d18 Fri 07:31 look entry_table_e1: bowl_shared_1
d18 Fri 08:22 look counter_k1: mug_mara, plate_shared_2, tablet_mara
d18 Fri 08:33 look kitchen_table_k1: pan_shared_1, pen_mara, plate_shared_1
d18 Fri 08:36 look sink_k1: bowl_shared_2, watering_can_mara
d18 Fri 08:36 look nightstand_b1: book_mara
d18 Fri 09:07 look counter_k1: mug_mara, plate_shared_2, tablet_mara
d18 Fri 09:09 look chair_k1: (nothing)
d18 Fri 09:31 look entry_floor_e1: umbrella_mara
d18 Fri 09:31 look entry_hook_e1: (nothing)
d18 Fri 09:31 look entry_table_e1: bowl_shared_1
d18 Fri 10:07 look sink_k1: bowl_shared_2, watering_can_mara
d18 Fri 10:07 look nightstand_b1: book_mara
d18 Fri 10:48 look kitchen_table_k1: pan_shared_1, pen_mara, plate_shared_1
d18 Fri 10:51 look entry_hook_e1: (nothing)
d18 Fri 11:06 look entry_table_e1: bowl_shared_1
d18 Fri 11:11 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d18 Fri 11:25 look entry_hook_e1: (nothing)
d18 Fri 11:25 look kitchen_table_k1: pan_shared_1, pen_mara, plate_shared_1
d18 Fri 11:41 look kitchen_table_k1: pan_shared_1, pen_mara, plate_shared_1
d18 Fri 11:44 look kitchen_table_k1: pan_shared_1, pen_mara, plate_shared_1
d18 Fri 11:53 look entry_table_e1: bowl_shared_1
d18 Fri 12:51 look bed_b1: (nothing)
d18 Fri 12:51 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d18 Fri 12:51 look desk_b1: (nothing)
d18 Fri 12:51 look nightstand_b1: book_mara
d18 Fri 13:06 look sink_k1: bowl_shared_2, watering_can_mara
d18 Fri 13:25 look counter_k1: mug_mara, plate_shared_2, tablet_mara
d18 Fri 13:54 look entry_table_e1: bowl_shared_1
d18 Fri 15:56 look armchair_l1: (nothing)
d18 Fri 15:56 look bookshelf_l1: (nothing)
d18 Fri 15:56 look coffee_table_l1: (nothing)
d18 Fri 15:56 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d18 Fri 15:56 look tv_stand_l1: (nothing)
d18 Fri 19:11 look chair_k1: notebook_mara
d18 Fri 19:11 look chair_k2: (nothing)
d18 Fri 19:11 look counter_k1: mug_mara, pan_shared_1, plate_shared_2, tablet_mara
d18 Fri 19:11 look cupboard_k1: glasses_mara
d18 Fri 19:11 look dish_rack_k1: mug_shared_1, phone_mara, pot_shared_1
d18 Fri 19:11 look kitchen_table_k1: charger_mara, headphones_mara, laptop_mara, pen_mara, plate_shared_1, water_bottle_mara
d18 Fri 19:11 look sink_k1: bowl_shared_2, lunchbox_mara, watering_can_mara
d18 Fri 22:27 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d18 Fri 22:27 look towel_rack_ba1: towel_mara
d19 Sat 07:14 look dish_rack_k1: mug_shared_1, phone_mara, pot_shared_1
d19 Sat 07:14 look kitchen_table_k1: charger_mara, headphones_mara, laptop_mara, pen_mara, plate_shared_1
d19 Sat 07:17 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d19 Sat 07:28 look entry_hook_e1: backpack_mara, jacket_mara
d19 Sat 07:49 look counter_k1: mug_mara, plate_shared_2, tablet_mara
d19 Sat 08:15 look nightstand_b1: book_mara, phone_mara, water_bottle_mara
d19 Sat 08:22 look entry_hook_e1: backpack_mara, jacket_mara
d19 Sat 08:22 look entry_floor_e1: umbrella_mara
d19 Sat 08:22 look entry_hook_e1: backpack_mara, jacket_mara
d19 Sat 08:22 look entry_table_e1: bowl_shared_1, keys_mara, wallet_mara
d19 Sat 08:53 look kitchen_table_k1: charger_mara, laptop_mara, pen_mara, plate_shared_1
d19 Sat 09:08 look couch_l1: blanket_mara, remote_shared_1, yoga_mat_mara
d19 Sat 09:12 look sink_k1: bowl_shared_2, lunchbox_mara, watering_can_mara
d19 Sat 09:47 look kitchen_table_k1: charger_mara, laptop_mara, pen_mara, plate_shared_1
d19 Sat 10:01 look sink_k1: bowl_shared_2, lunchbox_mara, watering_can_mara
d19 Sat 10:34 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d19 Sat 10:49 look kitchen_table_k1: charger_mara, glasses_mara, laptop_mara, pen_mara, plate_shared_1
d19 Sat 11:17 look bed_b1: (nothing)
d19 Sat 11:17 look bedroom_floor_b1: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1
d19 Sat 11:17 look desk_b1: (nothing)
d19 Sat 11:17 look nightstand_b1: book_mara, phone_mara, water_bottle_mara
d19 Sat 11:46 look entry_table_e1: bowl_shared_1, wallet_mara
d19 Sat 12:05 look kitchen_table_k1: charger_mara, laptop_mara, pen_mara, plate_shared_2
d19 Sat 12:57 look dish_rack_k1: lunchbox_mara, mug_shared_1, plate_shared_1, pot_shared_1
d19 Sat 13:05 look kitchen_table_k1: charger_mara, laptop_mara, pen_mara, plate_shared_2
d19 Sat 13:22 look kitchen_table_k1: charger_mara, glasses_mara, headphones_mara, laptop_mara, pen_mara, plate_shared_2
d19 Sat 13:25 look kitchen_table_k1: charger_mara, glasses_mara, headphones_mara, laptop_mara, pen_mara, plate_shared_2
d19 Sat 14:10 look armchair_l1: (nothing)
d19 Sat 14:10 look bookshelf_l1: (nothing)
d19 Sat 14:10 look coffee_table_l1: headphones_mara, wallet_mara
d19 Sat 14:10 look couch_l1: blanket_mara, mug_mara, phone_mara, remote_shared_1, yoga_mat_mara
d19 Sat 14:10 look tv_stand_l1: tablet_mara
d19 Sat 15:43 look dish_rack_k1: lunchbox_mara, mug_shared_1, plate_shared_1, pot_shared_1
d19 Sat 16:47 look kitchen_table_k1: charger_mara, glasses_mara, laptop_mara, pen_mara, plate_shared_2
d19 Sat 16:47 look chair_k1: notebook_mara, umbrella_mara
d19 Sat 16:47 look chair_k2: (nothing)
d19 Sat 16:47 look counter_k1: pan_shared_1
d19 Sat 16:47 look cupboard_k1: (nothing)
d19 Sat 16:47 look dish_rack_k1: lunchbox_mara, mug_shared_1, plate_shared_1, pot_shared_1
d19 Sat 16:47 look kitchen_table_k1: charger_mara, glasses_mara, laptop_mara, pen_mara, plate_shared_2
d19 Sat 16:47 look sink_k1: bowl_shared_2, watering_can_mara
d19 Sat 17:04 look kitchen_table_k1: charger_mara, glasses_mara, laptop_mara, pen_mara, plate_shared_2
d19 Sat 17:44 look counter_k1: pan_shared_1
d19 Sat 19:38 look bathroom_shelf_ba1: hairbrush_mara, makeup_kit_mara, medication_bottle_mara
d19 Sat 19:38 look towel_rack_ba1: towel_mara

WEEKDAY 9:00-17:00 LOOKS AT EACH OBJECT'S USUAL PLACE (found it / found nothing):
  backpack_mara: usually entry_hook_e1 (29 sightings); found 0, found nothing 20
  blanket_mara: usually couch_l1 (47 sightings); found 19, found nothing 1
  book_mara: usually nightstand_b1 (60 sightings); found 7, found nothing 14
  bowl_shared_1: usually entry_table_e1 (61 sightings); found 22, found nothing 6
  bowl_shared_2: usually kitchen_table_k1 (112 sightings); found 39, found nothing 25
  charger_mara: usually kitchen_table_k1 (66 sightings); found 6, found nothing 58
  glasses_mara: usually kitchen_table_k1 (56 sightings); found 6, found nothing 58
  hairbrush_mara: usually bathroom_shelf_ba1 (51 sightings); found 17, found nothing 7
  headphones_mara: usually kitchen_table_k1 (68 sightings); found 5, found nothing 59
  jacket_mara: usually entry_hook_e1 (30 sightings); found 1, found nothing 19
  keys_mara: usually entry_table_e1 (33 sightings); found 5, found nothing 23
  laptop_mara: usually kitchen_table_k1 (79 sightings); found 14, found nothing 50
  laundry_basket_mara: usually bedroom_floor_b1 (27 sightings); found 12, found nothing 2
  lunchbox_mara: usually counter_k1 (48 sightings); found 9, found nothing 25
  makeup_kit_mara: usually bathroom_shelf_ba1 (57 sightings); found 22, found nothing 2
  medication_bottle_mara: usually bathroom_shelf_ba1 (52 sightings); found 14, found nothing 10
  mug_mara: usually kitchen_table_k1 (92 sightings); found 28, found nothing 36
  mug_shared_1: usually dish_rack_k1 (46 sightings); found 6, found nothing 2
  notebook_mara: usually kitchen_table_k1 (59 sightings); found 11, found nothing 53
  pan_shared_1: usually kitchen_table_k1 (103 sightings); found 38, found nothing 26
  pen_mara: usually kitchen_table_k1 (95 sightings); found 16, found nothing 48
  phone_mara: usually nightstand_b1 (29 sightings); found 4, found nothing 17
  plate_shared_1: usually kitchen_table_k1 (110 sightings); found 33, found nothing 31
  plate_shared_2: usually counter_k1 (96 sightings); found 19, found nothing 15
  pot_shared_1: usually sink_k1 (78 sightings); found 18, found nothing 16
  remote_shared_1: usually couch_l1 (40 sightings); found 9, found nothing 11
  suitcase_mara: usually bedroom_floor_b1 (27 sightings); found 12, found nothing 2
  tablet_mara: usually counter_k1 (67 sightings); found 25, found nothing 9
  towel_mara: usually towel_rack_ba1 (30 sightings); found 14, found nothing 0
  umbrella_mara: usually entry_floor_e1 (25 sightings); found 9, found nothing 0
  vacuum_cleaner_shared_1: usually bedroom_floor_b1 (27 sightings); found 12, found nothing 2
  wallet_mara: usually entry_table_e1 (34 sightings); found 1, found nothing 27
  water_bottle_mara: usually nightstand_b1 (42 sightings); found 5, found nothing 16
  watering_can_mara: usually sink_k1 (78 sightings); found 33, found nothing 1
  yoga_mat_mara: usually couch_l1 (47 sightings); found 19, found nothing 1

QUESTION: where is phone_mara right now?
NOW: d19 Sat 22:28
BUDGET: 0 looks left today; at most 21 more looks on this question.

## reply

{"action": "answer", "ranked": ["couch_l1", "nightstand_b1", "dish_rack_k1", "kitchen_table_k1", "counter_k1"], "why": "The most recent sighting of phone_mara was at couch_l1 at d19 Sat 14:10. Since then, the robot has checked nightstand_b1 (d19 11:17), dish_rack_k1 (d19 16:47), kitchen_table_k1 (d19 17:04), and counter_k1 (d19 17:44), and the phone was not found in any of these locations. Therefore, it is most likely still at couch_l1."}
