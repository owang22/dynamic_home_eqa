# call 2: mug_shared_1 at d00 Mon 15:20

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
  hairbrush_mara  (class: hairbrush)
  laundry_basket_mara  (class: laundry_basket)
  lunchbox_mara  (class: lunchbox)
  makeup_kit_mara  (class: makeup_kit)
  medication_bottle_mara  (class: medication_bottle)
  mug_mara  (class: mug)
  mug_shared_1  (class: mug)
  pan_shared_1  (class: pan)
  pen_mara  (class: pen)
  plate_shared_1  (class: plate)
  plate_shared_2  (class: plate)
  pot_shared_1  (class: pot)
  remote_shared_1  (class: remote)
  suitcase_mara  (class: suitcase)
  tablet_mara  (class: tablet)
  towel_mara  (class: towel)
  umbrella_mara  (class: umbrella)
  vacuum_cleaner_shared_1  (class: vacuum_cleaner)
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

WEEKDAY 9:00-17:00 LOOKS AT EACH OBJECT'S USUAL PLACE (found it / found nothing):
  blanket_mara: usually couch_l1 (1 sightings); found 1, found nothing 1
  book_mara: usually bookshelf_l1 (1 sightings); found 1, found nothing 0
  bowl_shared_1: usually entry_table_e1 (1 sightings); found 1, found nothing 0
  bowl_shared_2: usually kitchen_table_k1 (1 sightings); found 1, found nothing 1
  hairbrush_mara: usually nightstand_b1 (1 sightings); found 1, found nothing 0
  laundry_basket_mara: usually bedroom_floor_b1 (1 sightings); found 1, found nothing 2
  lunchbox_mara: usually counter_k1 (1 sightings); found 1, found nothing 1
  makeup_kit_mara: usually bathroom_shelf_ba1 (1 sightings); found 1, found nothing 1
  medication_bottle_mara: usually bathroom_shelf_ba1 (1 sightings); found 1, found nothing 1
  mug_mara: usually chair_k1 (1 sightings); found 1, found nothing 0
  mug_shared_1: usually cupboard_k1 (1 sightings); found 1, found nothing 2
  pan_shared_1: usually sink_k1 (1 sightings); found 1, found nothing 1
  pen_mara: usually kitchen_table_k1 (1 sightings); found 1, found nothing 1
  plate_shared_1: usually cupboard_k1 (1 sightings); found 1, found nothing 2
  plate_shared_2: usually counter_k1 (1 sightings); found 1, found nothing 1
  pot_shared_1: usually cupboard_k1 (1 sightings); found 1, found nothing 2
  remote_shared_1: usually coffee_table_l1 (1 sightings); found 1, found nothing 1
  suitcase_mara: usually bedroom_floor_b1 (1 sightings); found 1, found nothing 2
  tablet_mara: usually coffee_table_l1 (1 sightings); found 1, found nothing 1
  towel_mara: usually towel_rack_ba1 (1 sightings); found 1, found nothing 0
  umbrella_mara: usually entry_floor_e1 (1 sightings); found 1, found nothing 0
  vacuum_cleaner_shared_1: usually bedroom_floor_b1 (1 sightings); found 1, found nothing 2
  watering_can_mara: usually sink_k1 (1 sightings); found 1, found nothing 1
  yoga_mat_mara: usually couch_l1 (1 sightings); found 1, found nothing 1

QUESTION: where is mug_shared_1 right now?
NOW: d00 Mon 15:20
BUDGET: 24 looks left today; at most 21 more looks on this question.

## reply

{"action": "sense", "receptacle": "cupboard_k1", "why": "The walkthrough at 15:08 placed mug_shared_1 in cupboard_k1. It is now 15:20, only 12 minutes later. While the object has a history of being found missing from its usual spot (2 times), a direct look at its last known location is the most efficient way to confirm if it is still there or has been moved, especially given the short time elapsed."}
