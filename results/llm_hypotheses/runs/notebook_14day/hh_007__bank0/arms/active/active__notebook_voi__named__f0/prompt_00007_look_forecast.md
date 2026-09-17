# call 7 (look_forecast, agent a02) at d00 Mon 07:33

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
  backpack_leo (backpack)
  backpack_mara (backpack)
  backpack_sofia (backpack)
  blanket_1 (blanket)
  book_sofia (book)
  bowl_leo (bowl)
  charger_leo (charger)
  charger_sofia (charger)
  gaming_controller_leo (gaming_controller)
  glasses_mara (glasses)
  hairbrush_sofia (hairbrush)
  headphones_leo (headphones)
  jacket_leo (jacket)
  jacket_mara (jacket)
  jacket_sofia (jacket)
  keys_leo (keys)
  keys_mara (keys)
  keys_sofia (keys)
  laptop_leo (laptop)
  laptop_mara (laptop)
  laundry_basket_1 (laundry_basket)
  lunchbox_sofia (lunchbox)
  makeup_kit_sofia (makeup_kit)
  medication_bottle_sofia (medication_bottle)
  mug_leo (mug)
  mug_mara (mug)
  notebook_leo (notebook)
  notebook_mara (notebook)
  pan_1 (pan)
  pen_mara (pen)
  phone_leo (phone)
  phone_mara (phone)
  phone_sofia (phone)
  plate_1 (plate)
  plate_2 (plate)
  pot_1 (pot)
  remote_1 (remote)
  umbrella_mara (umbrella)
  vacuum_cleaner_1 (vacuum_cleaner)
  wallet_leo (wallet)
  wallet_mara (wallet)
  wallet_sofia (wallet)
  water_bottle_mara (water_bottle)
  water_bottle_sofia (water_bottle)

ROOMS AND RECEPTACLES:
  bedroom_1: bed_b1, nightstand_b1, desk_b1, bedroom_floor_b1
  bedroom_2: bed_b2, nightstand_b2, desk_b2, bedroom_floor_b2
  bedroom_3: bed_b3, nightstand_b3, desk_b3, bedroom_floor_b3
  living: couch_l1, coffee_table_l1, tv_stand_l1, bookshelf_l1, armchair_l1, game_shelf_l1
  kitchen: counter_k1, sink_k1, cupboard_k1, dish_rack_k1, kitchen_table_k1, chair_k1, chair_k2
  bathroom: bathroom_shelf_ba1, towel_rack_ba1
  entry: entry_table_e1, entry_hook_e1, entry_floor_e1
Answer spots are every receptacle above plus ON_PERSON and OUT_OF_HOUSE. ON_PERSON means a resident who is in the house is carrying the object. OUT_OF_HOUSE means the object is not in the house. Neither can be chosen as the target of a look. A look at a receptacle also shows which residents are in that room. Looking at a resident shows what they are carrying, and is only possible after a look in the room they are in.

RESIDENTS: resident_1, resident_2, resident_3

LOOK BUDGET: 8 looks per day, reset at midnight.

YOUR NOTEBOOK (agent a02)
## BELIEFS
BELIEFS: The household is disorganized. Objects are rarely in their 'logical' spots. Residents are often awake at midnight, moving between rooms, and carrying items. 

1. Resident Activity: At 00:00, at least one resident is awake. They may be in the living room (couch_l1, armchair_l1) or kitchen (kitchen_table_k1). 
2. Object Scattering: Personal items (keys, wallet, phone) are often left on the coffee_table_l1, couch_l1, or kitchen_table_k1. 
3. Clothing: Jackets and backpacks are often on the bedroom_floor_b1/b2/b3 or the entry_floor_e1, not hung up. 
4. Kitchen Items: Mugs, bowls, and plates are often left on the counter_k1 or kitchen_table_k1, not in the cupboard_k1. 
5. Electronics: Laptops and headphones are often on the couch_l1 or coffee_table_l1. 
6. Forecasting: To find an object, check the living room first (coffee_table_l1, couch_l1). Then check the kitchen (counter_k1, kitchen_table_k1). Then check the resident's bedroom floor. 
7. Resident Presence: Residents are likely in the living room or kitchen. If a resident is in a bedroom, they are asleep. 
8. Dependencies: Objects are often grouped by resident. If resident_1 is in the living room, their items (backpack_leo, keys_leo, etc.) are likely nearby. 
9. Anomalies: Objects are frequently misplaced. Do not assume an object is in its 'home' spot. 
10. Look Strategy: Prioritize high-traffic areas (living room, kitchen). Check ON_PERSON for residents in these areas. 
11. Confidence: Low confidence in object locations. High confidence that residents are active. 
12. Verification: If a look reveals a resident in a bedroom, update beliefs about their activity level. If an object is found in a 'home' spot, update beliefs about organization.

## SCRATCH MEMORY
(empty)

NOW: d00 Mon 07:33. The robot is in kitchen. Looks left today: 7.
SEEN SO FAR ON THIS QUESTION: nothing yet.

REQUEST: the robot is about to look at receptacle nightstand_b3 (in bedroom_3). For up to 8 objects you think may be there right now, give the probability that it is there — each object is its own yes/no probability. Objects you leave out are taken as very unlikely to be there. Name objects by their exact ids from OBJECTS; a class name or a paraphrase is thrown away.

## reply

{"objects": [{"object": "phone_resident_3", "p": 0.35}, {"object": "glasses_resident_3", "p": 0.25}, {"object": "alarm_clock_resident_3", "p": 0.2}, {"object": "book_resident_3", "p": 0.15}, {"object": "keys_resident_3", "p": 0.1}, {"object": "wallet_resident_3", "p": 0.05}, {"object": "charger_cable_resident_3", "p": 0.05}, {"object": "tissue_box", "p": 0.02}]}
