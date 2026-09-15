# call 250: wallet_mara at d03 Thu 05:43

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

WEEKDAY 9:00-17:00 LOOKS AT EACH OBJECT'S USUAL PLACE (found it / found nothing):
  blanket_mara: usually couch_l1 (7 sightings); found 4, found nothing 1
  book_mara: usually bookshelf_l1 (4 sightings); found 1, found nothing 0
  bowl_shared_1: usually entry_table_e1 (7 sightings); found 5, found nothing 0
  bowl_shared_2: usually kitchen_table_k1 (15 sightings); found 9, found nothing 3
  charger_mara: usually kitchen_table_k1 (7 sightings); found 1, found nothing 11
  glasses_mara: usually kitchen_table_k1 (5 sightings); found 0, found nothing 12
  hairbrush_mara: usually bathroom_shelf_ba1 (8 sightings); found 3, found nothing 3
  headphones_mara: usually cupboard_k1 (7 sightings); found 0, found nothing 8
  jacket_mara: usually kitchen_table_k1 (4 sightings); found 0, found nothing 12
  keys_mara: usually cupboard_k1 (6 sightings); found 0, found nothing 8
  laptop_mara: usually kitchen_table_k1 (4 sightings); found 0, found nothing 12
  laundry_basket_mara: usually bedroom_floor_b1 (7 sightings); found 4, found nothing 2
  lunchbox_mara: usually sink_k1 (6 sightings); found 1, found nothing 6
  makeup_kit_mara: usually kitchen_table_k1 (13 sightings); found 7, found nothing 5
  medication_bottle_mara: usually bathroom_shelf_ba1 (7 sightings); found 5, found nothing 1
  mug_mara: usually kitchen_table_k1 (16 sightings); found 7, found nothing 5
  mug_shared_1: usually cupboard_k1 (14 sightings); found 6, found nothing 2
  notebook_mara: usually counter_k1 (7 sightings); found 1, found nothing 4
  pan_shared_1: usually kitchen_table_k1 (13 sightings); found 7, found nothing 5
  pen_mara: usually kitchen_table_k1 (6 sightings); found 2, found nothing 10
  phone_mara: usually nightstand_b1 (1 sightings); found 0, found nothing 3
  plate_shared_1: usually kitchen_table_k1 (16 sightings); found 9, found nothing 3
  plate_shared_2: usually counter_k1 (10 sightings); found 4, found nothing 1
  pot_shared_1: usually cupboard_k1 (13 sightings); found 6, found nothing 2
  remote_shared_1: usually coffee_table_l1 (6 sightings); found 2, found nothing 1
  suitcase_mara: usually bedroom_floor_b1 (7 sightings); found 4, found nothing 2
  tablet_mara: usually coffee_table_l1 (6 sightings); found 2, found nothing 1
  towel_mara: usually towel_rack_ba1 (4 sightings); found 3, found nothing 0
  umbrella_mara: usually entry_floor_e1 (4 sightings); found 3, found nothing 0
  vacuum_cleaner_shared_1: usually bedroom_floor_b1 (7 sightings); found 4, found nothing 2
  wallet_mara: usually dish_rack_k1 (1 sightings); found 0, found nothing 1
  water_bottle_mara: usually couch_l1 (4 sightings); found 2, found nothing 3
  watering_can_mara: usually sink_k1 (9 sightings); found 6, found nothing 1
  yoga_mat_mara: usually couch_l1 (7 sightings); found 4, found nothing 1

QUESTION: where is wallet_mara right now?
NOW: d03 Thu 05:43
BUDGET: 22 looks left today; at most 21 more looks on this question.

## reply

{"action": "sense", "receptacle": "dish_rack_k1", "why": "The last time wallet_mara was seen was on d02 Wed 05:48 in dish_rack_k1. Since then, the robot has not looked inside dish_rack_k1, so we do not know if it is still there or has been moved. Checking its last known location is the most direct way to find it."}
