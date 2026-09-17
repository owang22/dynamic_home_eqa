# call 1200 (look_forecast, agent a01) at d09 Wed 00:20

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

RESIDENTS: resident_1 (Mara), resident_2 (Leo), resident_3 (Sofia)

LOOK BUDGET: 8 looks per day, reset at midnight.

YOUR NOTEBOOK (agent a01)
## BELIEFS
BELIEFS: The household operates on a strict 'personal territory' model. Each resident (Mara, Leo, Sofia) has a designated bedroom (bedroom_1, bedroom_2, bedroom_3 respectively) and a corresponding desk (desk_b1, desk_b2, desk_b3). Personal items (backpacks, laptops, phones, wallets, keys, mugs, notebooks, jackets, umbrellas, water bottles, chargers, gaming controllers, headphones, glasses, hairbrushes, makeup kits, medication bottles, lunchboxes) are almost exclusively found in the owner's bedroom or on the owner's person. Shared spaces (living, kitchen, entry) contain only communal items (blanket_1, remote_1, vacuum_cleaner_1, plates, bowls, pans, pots, laundry_basket_1) or items temporarily moved for immediate use. Why: This is the most common household organization pattern; it minimizes search space by mapping object ownership to specific rooms. Evidence: None yet, but this is the baseline assumption for a new installation. If an object is missing from its owner's bedroom, it is likely ON_PERSON or OUT_OF_HOUSE. If a personal item is found in a shared space, it is an anomaly or temporary state. The entry area (entry_table_e1, entry_hook_e1) is the primary drop zone for keys, wallets, and jackets upon arrival/departure. The kitchen counter (counter_k1) is the primary drop zone for mugs, water bottles, and phones during meal times. The living room (coffee_table_l1, tv_stand_l1) is the primary drop zone for remotes, controllers, and books during leisure time. Bedroom floors (bedroom_floor_b1, bedroom_floor_b2, bedroom_floor_b3) are the primary drop zone for jackets, backpacks, and shoes upon entering the bedroom. Nightstands (nightstand_b1, nightstand_b2, nightstand_b3) are the primary drop zone for phones, glasses, and chargers at night. Desks (desk_b1, desk_b2, desk_b3) are the primary drop zone for laptops, notebooks, pens, and chargers during work/study. Beds (bed_b1, bed_b2, bed_b3) are the primary drop zone for blankets, pillows, and occasionally forgotten items like phones or glasses. Bathroom shelves (bathroom_shelf_ba1) are the primary drop zone for hairbrushes, makeup kits, and medication bottles. Towel racks (towel_rack_ba1) are the primary drop zone for towels and occasionally hairbrushes. Kitchen cupboards (cupboard_k1) are the primary drop zone for plates, bowls, pans, and pots. Dish racks (dish_rack_k1) are the primary drop zone for dirty dishes. Kitchen tables (kitchen_table_k1) are the primary drop zone for food items and occasionally phones or notebooks. Chairs (chair_k1, chair_k2) are the primary drop zone for jackets, bags, and occasionally phones. Couches (couch_l1) are the primary drop zone for blankets, pillows, and occasionally phones or remotes. Armchairs (armchair_l1) are the primary drop zone for blankets, pillows, and occasionally phones or books. Bookshelves (bookshelf_l1) are the primary drop zone for books. Game shelves (game_shelf_l1) are the primary drop zone for gaming controllers and consoles. TV stands (tv_stand_l1) are the primary drop zone for remotes and occasionally phones or chargers. Coffee tables (coffee_table_l1) are the primary drop zone for remotes, books, and occasionally phones or mugs. Entry floors (entry_floor_e1) are the primary drop zone for shoes and occasionally umbrellas. Entry hooks (entry_hook_e1) are the primary drop zone for jackets and umbrellas. Entry tables (entry_table_e1) are the primary drop zone for keys, wallets, and occasionally phones. Laundry baskets (laundry_basket_1) are the primary drop zone for dirty clothes. Vacuum cleaners (vacuum_cleaner_1) are stored in a closet or garage, but if in the house, likely in the living room or entry. Why: This detailed mapping allows the robot to prioritize looks based on object class and owner. For example, if asked for 'phone_leo', the robot should first check desk_b2, then nightstand_b2, then ON_PERSON (if Leo is home), then bedroom_floor_b2, then counter_k1, then coffee_table_l1. If asked for 'keys_mara', the robot should first check entry_table_e1, then ON_PERSON (if Mara is home), then desk_b1, then nightstand_b1. This strategy maximizes the probability of finding the object in the first look.

## SCRATCH MEMORY
d04-d08 Patterns: 1) counter_k1 is the primary multi-resident morning hub (P~0.80) for persistent items (backpacks, mugs, phones, keys, lunchboxes, water bottles). Prioritize over bedrooms when residents are in kitchen. 2) coffee_table_l1 is a high-probability (P~0.80) static drop zone for Leo's personal items (phone, headphones, bowl, mug) even when absent. Contradicts 'personal territory' model; prioritize over desk_b2/nightstand_b2. 3) nightstand_b1 is a high-probability (P~0.80) static drop zone for Mara's phone and glasses, whether present or absent. 4) nightstand_b3 is a static storage hub for Sofia's charger (P~0.70) and medication (P~0.80); low probability for phone. 5) bookshelf_l1 is a static drop zone for Leo's charger (P~0.50) even when absent; prioritize over desk_b2/nightstand_b2. 6) entry_table_e1 is unreliable for static storage (P~0.15-0.20 for phones when away); keys rarely found here. 7) cupboard_k1 is often empty; do not forecast personal items there without evidence. 8) bed_b1 is not a drop zone for Mara's phone/glasses (P~0.05); validates nightstand_b1 as primary. 9) sink_k1 is a drop zone for mugs (mug_mara P~0.40) and wallets (wallet_leo P~0.30). 10) dish_rack_k1 holds pot_1 (P high). 11) Leo is frequently active in kitchen during mornings; often co-occurs with Mara. 12) Absence of remote_1/laptop_leo at coffee_table_l1 lowers their priors there. 13) Absence of books at bookshelf_l1 lowers their priors there. d08 Tue 00:23: bookshelf_l1: charger_leo; nobody. Confirms bookshelf_l1 as a static drop zone for Leo's charger (P~0.50) even when absent. Prioritize bookshelf_l1 over desk_b2/nightstand_b2 for charger_leo. Absence of books lowers their priors here. Do not forecast other personal items here without evidence.
d08 Tue 00:23: d08 Tue 00:23: desk_b3: hairbrush_sofia, makeup_kit_sofia; nobody. Confirms desk_b3 as static storage for Sofia's grooming items (P~0.80) even when absent. Prioritize desk_b3 over bathroom_shelf_ba1 for these. Absence of laptop/notebook lowers their priors here. Do not forecast other personal items here without evidence.
d08 Tue 00:23: d08 Tue 00:23: bed_b3 empty; nobody. Confirms bed_b3 is not a drop zone for Sofia's personal items (P~0.05). Prioritize desk_b3 (grooming) and nightstand_b3 (charger/meds) over bed_b3. Absence of items here lowers priors for phone/jacket/backpack at bed_b3.
d08 Tue 00:28: d08 Tue 00:28: nightstand_b3: charger_sofia, medication_bottle_sofia, phone_sofia; nobody. Confirms nightstand_b3 as static hub for Sofia's charger/meds/phone (P~0.80) even when absent. Prioritize over desk_b3/bed_b3. Absence of other items lowers their priors here.
d08 Tue 00:39: d08 Tue 00:39: coffee_table_l1: laptop_leo; nobody. Confirms coffee_table_l1 as a valid drop zone for laptop_leo (P~0.40) even when absent. Prioritize over desk_b2 for laptop_leo. Absence of remote_1 lowers its prior here. Do not forecast other personal items here without evidence.

NOW: d09 Wed 00:20. The robot is in bedroom_2. Looks left today: 5.
RESIDENTS TODAY (from the robot's looks):
  resident_1: not seen today
  resident_2: bedroom_2 00:20 · last seen 00:20 in bedroom_2
  resident_3: not seen today
  rooms looked at with nobody there: living 00:20
SEEN SO FAR ON THIS QUESTION:
  d09 Wed 00:20 look at bookshelf_l1: (nothing); residents here: nobody
  d09 Wed 00:20 look at desk_b2: (nothing); residents here: resident_2

REQUEST: the robot is about to look at resident resident_2 (in bedroom_2). For up to 8 objects you think may be there right now, give the probability that it is there — each object is its own yes/no probability. Objects you leave out are taken as very unlikely to be there. Name objects by their exact ids from OBJECTS; a class name or a paraphrase is thrown away.

## reply

{"objects": [{"object": "phone_leo", "p": 0.35}, {"object": "laptop_leo", "p": 0.25}, {"object": "backpack_leo", "p": 0.20}, {"object": "jacket_leo", "p": 0.15}, {"object": "water_bottle_leo", "p": 0.10}, {"object": "wallet_leo", "p": 0.05}, {"object": "keys_leo", "p": 0.05}, {"object": "charger_leo", "p": 0.05}]}
