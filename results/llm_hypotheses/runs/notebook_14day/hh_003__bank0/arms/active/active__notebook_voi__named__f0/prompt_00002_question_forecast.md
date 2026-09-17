# call 2 (question_forecast, agent a01) at d00 Mon 06:06

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
  backpack_nico (backpack)
  backpack_talia (backpack)
  blanket_talia (blanket)
  book_marisol (book)
  bowl_shared_1 (bowl)
  charger_marisol (charger)
  charger_nico (charger)
  dog_leash_shared_1 (dog_leash)
  gaming_controller_shared_1 (gaming_controller)
  glasses_marisol (glasses)
  hairbrush_marisol (hairbrush)
  headphones_nico (headphones)
  headphones_talia (headphones)
  jacket_marisol (jacket)
  jacket_nico (jacket)
  keys_marisol (keys)
  keys_nico (keys)
  keys_talia (keys)
  laptop_talia (laptop)
  laundry_basket_shared_1 (laundry_basket)
  lunchbox_nico (lunchbox)
  lunchbox_talia (lunchbox)
  medication_bottle_marisol (medication_bottle)
  mug_marisol (mug)
  mug_talia (mug)
  notebook_marisol (notebook)
  notebook_talia (notebook)
  pan_shared_1 (pan)
  pen_marisol (pen)
  pen_talia (pen)
  phone_marisol (phone)
  phone_nico (phone)
  phone_talia (phone)
  plate_shared_1 (plate)
  pot_shared_1 (pot)
  remote_shared_1 (remote)
  towel_marisol (towel)
  umbrella_shared_1 (umbrella)
  vacuum_cleaner_shared_1 (vacuum_cleaner)
  wallet_marisol (wallet)
  wallet_nico (wallet)
  wallet_talia (wallet)
  water_bottle_marisol (water_bottle)
  water_bottle_nico (water_bottle)
  water_bottle_talia (water_bottle)

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

YOUR NOTEBOOK (agent a01)
## BELIEFS
BELIEFS: The household operates on a high-order routine. Objects have fixed 'home' receptacles. 
1. Personal items (keys, wallet, phone, water_bottle) are kept ON_PERSON during the day and moved to nightstands (nightstand_b1, nightstand_b2, nightstand_b3) at night. 
2. Kitchen items (mug_marisol, mug_talia, plate_shared_1, bowl_shared_1) are used at kitchen_table_k1 or counter_k1 and returned to cupboard_k1 or dish_rack_k1. 
3. Bedroom items (laptop_talia, notebook_talia, headphones_talia) are on desk_b2 or bed_b2. 
4. Living room items (remote_shared_1, gaming_controller_shared_1) are on coffee_table_l1 or tv_stand_l1. 
5. Residents: resident_1 (Marisol) is in bedroom_1, resident_2 (Nico) in bedroom_2, resident_3 (Talia) in bedroom_3. 
6. Time-based: 00:00-07:00 residents in bedrooms. 07:00-18:00 residents in living/kitchen. 18:00-22:00 residents in living/kitchen. 22:00-00:00 residents in bedrooms. 
7. Misplacement is rare (<5%). If an object is not in its home spot, it is likely ON_PERSON of the owner. 
8. Shared items (umbrella_shared_1, dog_leash_shared_1) are in entry_table_e1 or entry_hook_e1. 
9. Bathroom items (towel_marisol, hairbrush_marisol) are in bathroom_shelf_ba1 or towel_rack_ba1. 
10. Laundry (laundry_basket_shared_1) is in bedroom_1 or living. 
11. Medication (medication_bottle_marisol) is in nightstand_b1. 
12. Charging (charger_marisol, charger_nico) is in desk_b1 or desk_b2. 
Why: This model assumes a disciplined household where objects are not left out. It maximizes predictability for the robot by assuming 'home' spots are always correct unless the owner is present.

## SCRATCH MEMORY
(empty)

NOW: d00 Mon 06:06. The robot is in kitchen. Looks left today: 8.
SEEN SO FAR ON THIS QUESTION: nothing yet.

REQUEST: where is wallet_marisol right now? Give a probability for up to 6 spots you consider possible — receptacles, ON_PERSON, OUT_OF_HOUSE — summing to 1; spots you leave out are taken as very unlikely. If ON_PERSON gets any probability, also give carrier (the resident id) and carrier_room (the room you think that resident is in now). Why: at most 15 words. Name spots by their exact ids from ROOMS AND RECEPTACLES above; a room name, a paraphrase or an id that is not in that list is thrown away.

## reply

{"spots": [{"spot": "nightstand_b1", "p": 0.85}, {"spot": "ON_PERSON", "p": 0.10}, {"spot": "OUT_OF_HOUSE", "p": 0.05}], "carrier": "resident_1", "carrier_room": "bedroom_1", "why": "06:06 is night routine; Marisol's wallet stays on her nightstand."}
