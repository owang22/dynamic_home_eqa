# call 800 (look_forecast, agent a02) at d08 Tue 05:45

## system

You are one agent in a small population that keeps notebooks about one household on behalf of a home robot. The robot is asked, many times a day, where one object is right now, and it may spend a limited number of looks per day: a look opens one receptacle (it reveals everything inside and lists the residents in that room), or checks one resident the robot has just listed (it reveals everything they have on them).

Your notebook has two sections.
BELIEFS: your account of how this household lives and how its objects move — patterns, rules, conjectures, dependencies between objects — each with a short why that cites the evidence behind it. This section stays fixed for the life of an agent. To change it you propose a FORK: a new agent whose BELIEFS are a rewrite of yours together with a why for the change, while you keep running unchanged. BELIEFS holds at most 1200 words, so a fork that would grow past that is written as a condensed rewrite.
SCRATCH MEMORY: free text you may add to, rewrite or trim at any time, at most 600 words; when it grows past that you trim it.
IDS: in BELIEFS and SCRATCH MEMORY refer to receptacles and objects by their exact ids from the HOUSEHOLD list (counter_k1, mug_mara); a forecast that names a spot any other way is thrown away.

Your forecasts are scored by the log of the probability you gave to what the robot actually saw: an object found where you said, and equally an object absent from a spot or a spot found empty. Your weight in the population rises and falls with that score.

Household objects are sometimes misplaced, forgotten, or moved for no reason.

## user

HOUSEHOLD
OBJECTS (id (class)):
  backpack_mara (backpack)
  blanket_mara (blanket)
  book_mara (book)
  bowl_shared_1 (bowl)
  bowl_shared_2 (bowl)
  charger_mara (charger)
  glasses_mara (glasses)
  hairbrush_mara (hairbrush)
  headphones_mara (headphones)
  jacket_mara (jacket)
  keys_mara (keys)
  laptop_mara (laptop)
  laundry_basket_mara (laundry_basket)
  lunchbox_mara (lunchbox)
  makeup_kit_mara (makeup_kit)
  medication_bottle_mara (medication_bottle)
  mug_mara (mug)
  mug_shared_1 (mug)
  notebook_mara (notebook)
  pan_shared_1 (pan)
  pen_mara (pen)
  phone_mara (phone)
  plate_shared_1 (plate)
  plate_shared_2 (plate)
  pot_shared_1 (pot)
  remote_shared_1 (remote)
  suitcase_mara (suitcase)
  tablet_mara (tablet)
  towel_mara (towel)
  umbrella_mara (umbrella)
  vacuum_cleaner_shared_1 (vacuum_cleaner)
  wallet_mara (wallet)
  water_bottle_mara (water_bottle)
  watering_can_mara (watering_can)
  yoga_mat_mara (yoga_mat)

ROOMS AND RECEPTACLES:
  bedroom: bed_b1, nightstand_b1, desk_b1, bedroom_floor_b1
  living: couch_l1, coffee_table_l1, tv_stand_l1, bookshelf_l1, armchair_l1
  kitchen: counter_k1, sink_k1, cupboard_k1, dish_rack_k1, kitchen_table_k1, chair_k1, chair_k2
  bathroom: bathroom_shelf_ba1, towel_rack_ba1
  entry: entry_table_e1, entry_hook_e1, entry_floor_e1
Answer spots are every receptacle above plus ON_PERSON and OUT_OF_HOUSE. ON_PERSON means a resident who is in the house is carrying the object. OUT_OF_HOUSE means the object is not in the house. Neither can be chosen as the target of a look. A look at a receptacle also shows which residents are in that room. Looking at a resident shows what they are carrying, and is only possible after a look in the room they are in.

RESIDENTS: resident_1

LOOK BUDGET: 8 looks per day, reset at midnight.

YOUR NOTEBOOK (agent a02)
## BELIEFS
1. **No Home Bases**: Objects do not have consistent locations. Any object can be found in any receptacle with roughly equal probability, weighted slightly by object class (e.g., towels in bathroom, but also on bed_b1). 

2. **High Misplacement Rate**: 40% of objects are in 'wrong' locations at any given time. 'Wrong' means not in their logical category (e.g., laptop_mara on couch_l1, keys_mara in bathroom_shelf_ba1). 

3. **ON_PERSON Bias**: resident_1 carries multiple items at once (phone_mara, keys_mara, wallet_mara, water_bottle_mara, headphones_mara). These items are often ON_PERSON for extended periods. 

4. **Random Movement**: Objects move randomly between rooms. A look at one receptacle reveals little about others. 

5. **Forecasting Strategy**: Use looks to actively search. Prioritize checking ON_PERSON (via room looks) for small, high-value items (keys_mara, wallet_mara, phone_mara). For larger items, check the most recently used room (e.g., kitchen for food items, bedroom for personal care). Assume objects are absent from their 'logical' spots until proven otherwise. Use looks to eliminate possibilities.

## SCRATCH MEMORY
(empty)

NOW: d08 Tue 05:45. The robot is in bedroom. Looks left today: 3.
SEEN SO FAR ON THIS QUESTION:
  d08 Tue 05:45 look at nightstand_b1: glasses_mara, phone_mara, water_bottle_mara; residents here: nobody

REQUEST: the robot is about to look at receptacle bed_b1 (in bedroom). For up to 8 objects you think may be there right now, give the probability that it is there — each object is its own yes/no probability. Objects you leave out are taken as very unlikely to be there. Name objects by their exact ids from OBJECTS; a class name or a paraphrase is thrown away.

## reply

{"objects": [{"object": "water_bottle_mara", "p": 0.15}, {"object": "phone_mara", "p": 0.10}, {"object": "glasses_mara", "p": 0.10}, {"object": "headphones_mara", "p": 0.08}, {"object": "wallet_mara", "p": 0.05}, {"object": "keys_mara", "p": 0.05}, {"object": "towel_b1", "p": 0.03}, {"object": "book_b1", "p": 0.02}]}
