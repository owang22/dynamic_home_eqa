# call 200 (look_forecast, agent a03) at d01 Tue 00:42

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

YOUR NOTEBOOK (agent a03)
## BELIEFS
BELIEFS: The household is a shared space. Objects are moved between rooms by different residents. At 00:00, residents are often in the living room (couch_l1, armchair_l1) for socializing or media consumption. 

1. Resident Activity: At 00:00, residents are likely in the living room. They may be watching TV (remote_1 on coffee_table_l1), playing games (gaming_controller_leo on game_shelf_l1), or talking. 
2. Object Sharing: Objects are shared. For example, mugs (mug_leo, mug_mara) may be in the kitchen or living room. Books (book_sofia) may be on the bookshelf_l1 or coffee_table_l1. 
3. Personal Items: Personal items (keys, wallet, phone) are often left on the coffee_table_l1 or couch_l1. 
4. Clothing: Jackets and backpacks are often on the entry_hook_e1 or bedroom_floor_b1/b2/b3. 
5. Kitchen Items: Kitchen items are often in the kitchen (counter_k1, cupboard_k1) but may be brought to the living room (coffee_table_l1). 
6. Forecasting: To find an object, check the living room first (coffee_table_l1, couch_l1, bookshelf_l1). Then check the kitchen (counter_k1, cupboard_k1). Then check the resident's bedroom. 
7. Resident Presence: Residents are likely in the living room. If a resident is in a bedroom, they are asleep. 
8. Dependencies: Objects are often grouped by activity. If residents are watching TV, remote_1 and gaming_controller_leo are likely on the coffee_table_l1 or game_shelf_l1. 
9. Anomalies: Objects are frequently moved between rooms. Do not assume an object is in its 'home' spot. 
10. Look Strategy: Prioritize the living room. Check ON_PERSON for residents in the living room. 
11. Confidence: Medium confidence in resident activity. Low confidence in object locations. 
12. Verification: If a look reveals a resident in a bedroom, update beliefs about their activity level. If an object is found in a 'home' spot, update beliefs about sharing.

## SCRATCH MEMORY
(empty)

NOW: d01 Tue 00:42. The robot is in bedroom_1. Looks left today: 3.
SEEN SO FAR ON THIS QUESTION:
  d01 Tue 00:42 look at nightstand_b1: phone_mara; residents here: resident_1

REQUEST: the robot is about to look at receptacle desk_b1 (in bedroom_1). For up to 8 objects you think may be there right now, give the probability that it is there — each object is its own yes/no probability. Objects you leave out are taken as very unlikely to be there. Name objects by their exact ids from OBJECTS; a class name or a paraphrase is thrown away.

## reply

{"objects": [{"object": "phone_mara", "p": 0.05}, {"object": "wallet_mara", "p": 0.05}, {"object": "keys_mara", "p": 0.05}, {"object": "notebook_mara", "p": 0.05}, {"object": "pen_mara", "p": 0.05}, {"object": "charger_mara", "p": 0.05}, {"object": "glasses_mara", "p": 0.05}, {"object": "water_bottle_mara", "p": 0.05}]}
