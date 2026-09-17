# call 1000 (question_forecast, agent a40) at d04 Fri 07:15

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
  backpack_elias (backpack)
  backpack_noa (backpack)
  backpack_priya (backpack)
  blanket_noa (blanket)
  book_noa (book)
  bowl_shared_1 (bowl)
  charger_elias (charger)
  charger_shared_1 (charger)
  hairbrush_priya (hairbrush)
  headphones_elias (headphones)
  jacket_elias (jacket)
  jacket_priya (jacket)
  keys_elias (keys)
  keys_priya (keys)
  laptop_elias (laptop)
  laundry_basket_shared_1 (laundry_basket)
  lunchbox_priya (lunchbox)
  makeup_kit_priya (makeup_kit)
  medication_bottle_noa (medication_bottle)
  mug_elias (mug)
  mug_priya (mug)
  notebook_elias (notebook)
  pan_shared_1 (pan)
  pen_elias (pen)
  phone_elias (phone)
  phone_priya (phone)
  plate_shared_1 (plate)
  pot_shared_1 (pot)
  remote_shared_1 (remote)
  suitcase_shared_1 (suitcase)
  tablet_shared_1 (tablet)
  towel_noa (towel)
  toy_noa (toy)
  umbrella_shared_1 (umbrella)
  vacuum_cleaner_shared_1 (vacuum_cleaner)
  wallet_elias (wallet)
  wallet_priya (wallet)
  water_bottle_elias (water_bottle)
  water_bottle_noa (water_bottle)
  water_bottle_priya (water_bottle)
  yoga_mat_priya (yoga_mat)

ROOMS AND RECEPTACLES:
  bedroom_1: bed_b1, nightstand_b1, desk_b1, bedroom_floor_b1
  bedroom_2: bed_b2, nightstand_b2, desk_b2, bedroom_floor_b2, crib_b2
  living: couch_l1, coffee_table_l1, tv_stand_l1, bookshelf_l1, armchair_l1, toy_chest_l1
  kitchen: counter_k1, sink_k1, cupboard_k1, dish_rack_k1, kitchen_table_k1, chair_k1, chair_k2, high_chair_k1
  bathroom: bathroom_shelf_ba1, towel_rack_ba1
  entry: entry_table_e1, entry_hook_e1, entry_floor_e1
Answer spots are every receptacle above plus ON_PERSON and OUT_OF_HOUSE. ON_PERSON means a resident who is in the house is carrying the object. OUT_OF_HOUSE means the object is not in the house. Neither can be chosen as the target of a look. A look at a receptacle also shows which residents are in that room. Looking at a resident shows what they are carrying, and is only possible after a look in the room they are in.

RESIDENTS: resident_1, resident_2, resident_3

LOOK BUDGET: 8 looks per day, reset at midnight.

YOUR NOTEBOOK (agent a40)
## BELIEFS
1. Resident Identity: resident_1=Elias, resident_2=Priya, resident_3=Noa.
2. Core Principle: 'Static Clusters' vs. 'Mobile Items'. In the morning (05:00-08:00), residents are often stationary at specific receptacles. Their personal items are either in a static cluster at that receptacle or in a fixed 'drop-off' zone. They are rarely ON_PERSON unless explicitly observed. Forecasting items ON_PERSON for residents during routine hours is a high-risk error.
3. Elias (resident_1) Patterns:
- Location: bedroom_1, specifically desk_b1.
- Static Cluster at desk_b1: charger_elias, headphones_elias, notebook_elias. These are consistently found here.
- Absent from desk_b1: laptop_elias, phone_elias, pen_elias, keys_elias, wallet_elias, mug_elias, water_bottle_elias. Do not forecast these at desk_b1.
- Mobile/ON_PERSON: Elias is typically NOT carrying items while at desk_b1. If he is in bedroom_1, assume empty hands unless observed otherwise.
- Other Locations: phone_elias is mobile (seen in bathroom/kitchen). jacket_elias/backpack_elias are NOT at entry_hook_e1 in the morning (Elias is in bedroom_1).
4. Priya (resident_2) Patterns:
- Location: bathroom (early morning) or kitchen.
- Static Cluster at counter_k1: lunchbox_priya, mug_priya, phone_priya, water_bottle_priya. These items remain at counter_k1 even when Priya is in the bathroom. Do not forecast them ON_PERSON.
- Bathroom Shelf (bathroom_shelf_ba1): UNRELIABLE. Observed empty multiple times despite Priya being present. Do not forecast hairbrush_priya or makeup_kit_priya here without explicit recent observation. They are likely in a bag or ON_PERSON during active routine, but shelf is not a safe default.
- Entry Hook (entry_hook_e1): wallet_priya is often static here. jacket_priya/backpack_priya are NOT here in the morning.
- ON_PERSON: Priya is typically NOT carrying items while in bathroom/kitchen. Assume empty hands unless observed.
5. Noa (resident_3) Patterns:
- Location: bedroom_2 (morning/night). Not living room in early morning.
- Items: toy_noa, blanket_noa, book_noa, towel_noa, water_bottle_noa, medication_bottle_noa, backpack_noa.
- Static Cluster: Items are often in bed_b2, desk_b2, or ON_PERSON. Crib_b2 is often empty.
- Entry Hook: backpack_noa is often at entry_hook_e1, even if Noa is in bedroom_2.
6. Shared/Other Objects:
- entry_hook_e1: Primary drop-off for backpacks (noa, priya sometimes) and wallets (priya). NOT for Elias's items in morning.
- counter_k1: Primary drop-off for Priya's kitchen items and shared chargers.
- desk_b1: Primary drop-off for Elias's desk items (charger, headphones, notebook).
7. Forecasting Rules:
- If resident is in Room X, check their known Static Cluster in Room X first.
- If item is not in Static Cluster, check known Drop-off Zones (entry, counter).
- Assign low probability (<0.1) to items ON_PERSON for residents in routine locations unless there is specific evidence of movement.
- Assign low probability to bathroom_shelf_ba1 for toiletries unless explicitly seen there recently.

## SCRATCH MEMORY
d03-d04 Patterns: Elias (resident_1) is stationary at desk_b1 in mornings. Static cluster: charger_elias, notebook_elias, water_bottle_elias. Absent: laptop_elias, phone_elias, pen_elias, keys_elias, wallet_elias, mug_elias, headphones_elias (mobile). Elias is NOT ON_PERSON with items; assume empty hands. Priya (resident_2) has a static kitchen cluster at counter_k1: lunchbox_priya, mug_priya, phone_priya, water_bottle_priya. These stay at counter_k1 even when she is in the bathroom. Priya is NOT ON_PERSON with items during routine; assume empty hands. Her toiletries (hairbrush_priya, makeup_kit_priya) are NOT reliably on bathroom_shelf_ba1 (observed empty); likely in bag or ON_PERSON only when active. Priya's entry cluster at entry_hook_e1 includes wallet_priya and jacket_priya (confirmed d04). Noa (resident_3) has backpack_noa at entry_hook_e1. d04 Fri 05:33: bedroom_floor_b1: backpack_priya, suitcase_shared_1, vacuum_cleaner_shared_1; residents 1, 2. Priya's backpack is on floor, not entry_hook_e1 (contradicts d04 05:33 entry obs). Elias's items absent from floor. Both residents in bedroom_1.
d04 Fri 07:09: d04 Fri 07:09 counter_k1: charger_shared_1, lunchbox_priya, mug_priya, phone_priya present; water_bottle_priya absent. resident_3 (Noa) in kitchen. Confirms Priya's static cluster minus water bottle. Noa's presence suggests potential interaction with shared items.
d04 Fri 07:15: d04 Fri 07:15 counter_k1: ONLY mug_priya present. Absent: lunchbox_priya, phone_priya, charger_shared_1, water_bottle_priya. resident_3 (Noa) in kitchen. Contradicts d04 07:09 obs which listed 4 items. Priya's 'static cluster' is unstable; items likely moved or taken by Noa. Do not assume cluster persistence.

NOW: d04 Fri 07:15. The robot is in kitchen. Looks left today: 3.
SEEN SO FAR ON THIS QUESTION:
  d04 Fri 07:15 look at counter_k1: mug_priya; residents here: resident_3

REQUEST: where is phone_priya right now? Give a probability for up to 6 spots you consider possible — receptacles, ON_PERSON, OUT_OF_HOUSE — summing to 1; spots you leave out are taken as very unlikely. If ON_PERSON gets any probability, also give carrier (the resident id) and carrier_room (the room you think that resident is in now). Why: at most 15 words. Name spots by their exact ids from ROOMS AND RECEPTACLES above; a room name, a paraphrase or an id that is not in that list is thrown away.

## reply

{"spots": [{"spot": "counter_k1", "p": 0.15}, {"spot": "ON_PERSON", "p": 0.25}, {"spot": "entry_hook_e1", "p": 0.20}, {"spot": "bedroom_floor_b1", "p": 0.15}, {"spot": "bathroom_shelf_ba1", "p": 0.10}, {"spot": "OUT_OF_HOUSE", "p": 0.15}], "carrier": "resident_2", "carrier_room": "bedroom_1", "why": "Cluster unstable; likely moved to entry, floor, or taken by Priya."}
