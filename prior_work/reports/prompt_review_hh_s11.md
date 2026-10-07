# Prompt review · hh_s11 under the human protocol

Wording lives in `src/baselines/llm_hypotheses/protocol_text.py` (mechanics), `notebook_mixture.py` (notebook + dispatcher system prompts), `longleaf_prompt.py` / `prompt.py` (treeLongLeaf elicitation and vocabulary tables). Everything below is rendered from the actual bank `results/situation_sim/llm/hh_s11/bank.jsonl`.

## 1. Notebook agents · system prompt

```
You are one agent in a small population that keeps notebooks about one household on behalf of a home robot. The robot is asked, about 6 times a day, where one object is right now, and it may spend a limited budget per day on looks: a look is a whole room (it reveals every receptacle in that room and everything on them, and lists who is in the room), costing 1 in the room the robot is in and 4 anywhere else. Nobody's pockets can be looked into.

Your notebook has two sections.
BELIEFS: your account of how this household lives and how its objects move — patterns, rules, conjectures, dependencies between objects — each with a short why that cites the evidence behind it. This section stays fixed for the life of an agent. To change it you propose a FORK: a new agent whose BELIEFS are a rewrite of yours together with a why for the change, while you keep running unchanged. BELIEFS holds at most 1200 words, so a fork that would grow past that is written as a condensed rewrite.
SCRATCH MEMORY: free text you may add to, rewrite or trim at any time, at most 600 words; when it grows past that you trim it.
IDS: in BELIEFS and SCRATCH MEMORY refer to receptacles and objects by their exact ids from the HOUSEHOLD list (counter_k1, mug_mara); a forecast that names a spot any other way is thrown away.

Your forecasts are scored by the log of the probability you gave to what the robot actually saw: an object found where you said, and equally an object absent from a spot or a spot found empty. Your weight in the population rises and falls with that score.

Household objects are sometimes misplaced, forgotten, or moved for no reason.
```

## 2. Dispatcher (llmDecide) · system prompt

```
You are the dispatcher of a home robot. The robot is asked, about 6 times a day, where one object is right now. A panel of agents has just given its forecast; you decide whether the robot answers now or first spends part of today's budget on a look. A look is a whole room: it reveals every receptacle in it and who is there, and costs 1 if the room is the one the robot is already in, 4 otherwise (the robot then stays in that room). Pockets cannot be looked into: whether an object is on a person is inferred, never seen. Looks are the panel's only source of learning: a look grades every agent on everything it predicted, so a look also pays off on later questions. Unspent budget is lost at midnight. Today's budget is 12 units against about 6 questions: that is 3 looks if every one needs travel, more if the robot stays in one room, so budget is rationed across the day and the robot's current room matters — a question whose likely spots are in the room the robot is already in is cheap to check. What a gain is worth depends on what other gains this day is likely to offer. For each candidate look you are told the one-step gain: how much the chance of answering THIS question right would rise, and its cost. You also see today's ledger (every decision so far today and what each look found) and your own NOTE, which is your only memory: rewrite it on every call (at most 120 words) with what gains have been typical, when looks paid off, and how you plan to spend the rest of the day. Reply as JSON: {"action": "look" | "answer", "target": "<a receptacle id, for a look: the robot looks at the whole room that receptacle is in>", "why": "<one sentence>", "note": "<your rewritten note>"}.

Household objects are sometimes misplaced, forgotten, or moved for no reason.
```

## 3. Household block (prepended to every notebook call: vocabulary, rooms, residents, budget)

```
HOUSEHOLD
OBJECTS (id (class)):
  blanket_shared (blanket)
  book_hana (book)
  book_priya (book)
  bowl_hana (bowl)
  bowl_priya (bowl)
  camera_priya (camera)
  cushion_1_shared (cushion)
  cushion_2_shared (cushion)
  cutting_board_shared (cutting_board)
  detergent_shared (detergent)
  dog_bowl_shared (dog_bowl)
  dog_food_bag_shared (dog_food_bag)
  dog_leash_shared (dog_leash)
  dog_toy_shared (dog_toy)
  doormat_shared (doormat)
  duster_shared (duster)
  first_aid_kit_shared (first_aid_kit)
  fruit_bowl_shared (fruit_bowl)
  glass_hana (glass)
  glass_priya (glass)
  guitar_hana (guitar)
  hair_dryer_hana (hair_dryer)
  handbag_hana (handbag)
  hat_hana (hat)
  jacket_hana (jacket)
  jacket_priya (jacket)
  kettle_shared (kettle)
  keys_hana (keys)
  keys_priya (keys)
  kitchen_knife_shared (kitchen_knife)
  lamp_shared (lamp)
  laundry_basket_shared (laundry_basket)
  magazine_priya (magazine)
  medication_priya (medication)
  mug_hana (mug)
  mug_priya (mug)
  notebook_hana (notebook)
  pan_shared (pan)
  pen_hana (pen)
  pen_priya (pen)
  phone_hana (phone)
  phone_priya (phone)
  plant_pot_1_shared (plant_pot)
  plant_pot_2_shared (plant_pot)
  plant_pot_3_shared (plant_pot)
  plate_hana (plate)
  plate_priya (plate)
  pot_shared (pot)
  puzzle_box_shared (puzzle_box)
  recipe_book_shared (recipe_book)
  remote_shared (remote)
  scarf_hana (scarf)
  serving_dish_shared (serving_dish)
  shoes_hana (shoes)
  shoes_priya (shoes)
  shopping_bag_shared (shopping_bag)
  skincare_hana (skincare)
  skincare_priya (skincare)
  snack_bowl_shared (snack_bowl)
  soap_dispenser_shared (soap_dispenser)
  spatula_shared (spatula)
  sunglasses_priya (sunglasses)
  tablet_hana (tablet)
  tablet_priya (tablet)
  tissue_box_shared (tissue_box)
  toaster_shared (toaster)
  toiletry_bag_hana (toiletry_bag)
  toothbrush_holder_shared (toothbrush_holder)
  towel_hana (towel)
  towel_priya (towel)
  umbrella_hana (umbrella)
  vacuum_cleaner_shared (vacuum_cleaner)
  vase_shared (vase)
  wall_clock_shared (wall_clock)
  wallet_hana (wallet)
  wallet_priya (wallet)
  water_bottle_hana (water_bottle)
  water_bottle_priya (water_bottle)
  watering_can_shared (watering_can)
  yoga_mat_priya (yoga_mat)

ROOMS AND RECEPTACLES:
  living: armchair_l1, bookshelf_l1, coffee_table_l1, couch_l1, floor_l_l1, side_table_l1, tv_stand_l1
  balcony: balcony_floor_y1, balcony_table_y1
  bathroom: bathroom_shelf_ba1, medicine_cabinet_ba1, sink_ba_ba1, towel_rack_ba1
  bedroom_1: bed_b1, bedroom_floor_b1, desk_b1, dresser_b1, nightstand_b1, wardrobe_b1
  bedroom_2: bed_b2, bedroom_floor_b2, desk_b2, dresser_b2, nightstand_b2, wardrobe_b2
  dining: chair_d_d1, dining_table_d1, sideboard_d1
  kitchen: chair_k1, counter_k1, cupboard_k1, dish_rack_k1, drawer_k_k1, floor_k_k1, kitchen_table_k1, pantry_shelf_k1, sink_k1
  entry: entry_floor_e1, entry_hook_e1, entry_table_e1, shoe_rack_e1
  storage: storage_floor_s1, storage_shelf_s1
Answer spots are every receptacle above plus ON_PERSON and OUT_OF_HOUSE. ON_PERSON means a resident who is IN the house is carrying the object (a phone in a pocket between activities). OUT_OF_HOUSE means the object has left the house — taken along by a resident on a trip out; it comes back when they do. Neither can be chosen as the target of a look. A look is a whole ROOM: it reveals every receptacle in that room and everything on each of them at that instant, including which receptacles are empty. A look also lists who is standing in that room — the residents by name, and visitors as a count of guests. What people carry is never visible: a resident cannot be looked at, so whether something is on a person has to be inferred (for example from their keys, shoes and jacket being in or out of the house).

RESIDENTS: resident_1 (Hana), resident_2 (Priya)

LOOK BUDGET: 12 units per day, reset at midnight; unspent units are lost. A look costs 1 when the room is the one the robot is already in and 4 (1 + 3 travel) for any other room; after a look the robot stays in that room. Looking again at a room already looked at during the same question is free. The robot starts every day in the kitchen. There are about 6 questions a day, so the budget covers roughly 3 looks that need travel or 12 looks in the room the robot is already in.
```

## 4. treeLongLeaf · tour-start (elicitation) prompt

```
A home robot has just been installed. Its only observation so far is one walkthrough of the home at 18:00 on day 0, a Monday. Below are the home's receptacles and the objects the walkthrough saw, each with where it was. The home may hold further objects the walkthrough missed; those join your `class:<name>` blocks automatically once the robot meets them, so the ids below are the complete vocabulary for now.

RECEPTACLES:
  armchair_l1
  balcony_floor_y1
  balcony_table_y1
  bathroom_shelf_ba1
  bed_b1
  bed_b2
  bedroom_floor_b1
  bedroom_floor_b2
  bookshelf_l1
  chair_d_d1
  chair_k1
  coffee_table_l1
  couch_l1
  counter_k1
  cupboard_k1
  desk_b1
  desk_b2
  dining_table_d1
  dish_rack_k1
  drawer_k_k1
  dresser_b1
  dresser_b2
  entry_floor_e1
  entry_hook_e1
  entry_table_e1
  floor_k_k1
  floor_l_l1
  kitchen_table_k1
  medicine_cabinet_ba1
  nightstand_b1
  nightstand_b2
  pantry_shelf_k1
  shoe_rack_e1
  side_table_l1
  sideboard_d1
  sink_ba_ba1
  sink_k1
  storage_floor_s1
  storage_shelf_s1
  towel_rack_ba1
  tv_stand_l1
  wardrobe_b1
  wardrobe_b2
  ON_PERSON
  OUT_OF_HOUSE
`ON_PERSON` means a resident who is IN the house is carrying the object (a phone in a pocket between activities). `OUT_OF_HOUSE` means the object has left the house — taken along by a resident on a trip out; it comes back when they do. Neither can be chosen as the target of a look. A look is a whole ROOM: it reveals every receptacle in that room and everything on each of them at that instant, including which receptacles are empty. A look also lists who is standing in that room — the residents by name, and visitors as a count of guests. What people carry is never visible: a resident cannot be looked at, so whether something is on a person has to be inferred (for example from their keys, shoes and jacket being in or out of the house).

RESIDENTS (each can be the target of a look once a look has shown the room they are in):
  resident_1
  resident_2

OBJECTS the robot has seen, with where the tour saw each one:
  blanket_shared  (class: blanket)  at couch_l1
  book_hana  (class: book)  at nightstand_b1
  book_priya  (class: book)  at nightstand_b2
  bowl_hana  (class: bowl)  at cupboard_k1
  bowl_priya  (class: bowl)  at cupboard_k1
  camera_priya  (class: camera)  at bookshelf_l1
  cushion_1_shared  (class: cushion)  at couch_l1
  cushion_2_shared  (class: cushion)  at armchair_l1
  cutting_board_shared  (class: cutting_board)  at counter_k1
  detergent_shared  (class: detergent)  at bathroom_shelf_ba1
  dog_bowl_shared  (class: dog_bowl)  at floor_k_k1
  dog_food_bag_shared  (class: dog_food_bag)  at pantry_shelf_k1
  dog_leash_shared  (class: dog_leash)  at entry_hook_e1
  dog_toy_shared  (class: dog_toy)  at floor_l_l1
  doormat_shared  (class: doormat)  at entry_floor_e1
  duster_shared  (class: duster)  at storage_shelf_s1
  first_aid_kit_shared  (class: first_aid_kit)  at medicine_cabinet_ba1
  fruit_bowl_shared  (class: fruit_bowl)  at kitchen_table_k1
  glass_hana  (class: glass)  at sink_k1
  glass_priya  (class: glass)  at counter_k1
  guitar_hana  (class: guitar)  at bedroom_floor_b1
  hair_dryer_hana  (class: hair_dryer)  at bathroom_shelf_ba1
  jacket_priya  (class: jacket)  at entry_floor_e1
  kettle_shared  (class: kettle)  at counter_k1
  keys_priya  (class: keys)  at entry_table_e1
  kitchen_knife_shared  (class: kitchen_knife)  at drawer_k_k1
  lamp_shared  (class: lamp)  at side_table_l1
  laundry_basket_shared  (class: laundry_basket)  at bathroom_shelf_ba1
  magazine_priya  (class: magazine)  at coffee_table_l1
  medication_priya  (class: medication)  at medicine_cabinet_ba1
  mug_hana  (class: mug)  at cupboard_k1
  mug_priya  (class: mug)  at cupboard_k1
  notebook_hana  (class: notebook)  at desk_b1
  pan_shared  (class: pan)  at cupboard_k1
  pen_priya  (class: pen)  at desk_b2
  phone_priya  (class: phone)  at desk_b2
  plant_pot_1_shared  (class: plant_pot)  at side_table_l1
  plant_pot_2_shared  (class: plant_pot)  at counter_k1
  plant_pot_3_shared  (class: plant_pot)  at desk_b1
  plate_hana  (class: plate)  at sink_k1
  plate_priya  (class: plate)  at kitchen_table_k1
  pot_shared  (class: pot)  at cupboard_k1
  puzzle_box_shared  (class: puzzle_box)  at bookshelf_l1
  recipe_book_shared  (class: recipe_book)  at pantry_shelf_k1
  remote_shared  (class: remote)  at tv_stand_l1
  serving_dish_shared  (class: serving_dish)  at cupboard_k1
  shoes_priya  (class: shoes)  at shoe_rack_e1
  shopping_bag_shared  (class: shopping_bag)  at counter_k1
  skincare_hana  (class: skincare)  at sink_ba_ba1
  skincare_priya  (class: skincare)  at bathroom_shelf_ba1
  snack_bowl_shared  (class: snack_bowl)  at cupboard_k1
  soap_dispenser_shared  (class: soap_dispenser)  at sink_ba_ba1
  spatula_shared  (class: spatula)  at drawer_k_k1
  sunglasses_priya  (class: sunglasses)  at entry_table_e1
  tablet_hana  (class: tablet)  at desk_b1
  tablet_priya  (class: tablet)  at bed_b2
  tissue_box_shared  (class: tissue_box)  at coffee_table_l1
  toaster_shared  (class: toaster)  at counter_k1
  toiletry_bag_hana  (class: toiletry_bag)  at sink_ba_ba1
  toothbrush_holder_shared  (class: toothbrush_holder)  at sink_ba_ba1
  towel_hana  (class: towel)  at towel_rack_ba1
  towel_priya  (class: towel)  at towel_rack_ba1
  umbrella_hana  (class: umbrella)  at entry_floor_e1
  vacuum_cleaner_shared  (class: vacuum_cleaner)  at storage_floor_s1
  vase_shared  (class: vase)  at dining_table_d1
  wall_clock_shared  (class: wall_clock)  at counter_k1
  wallet_priya  (class: wallet)  at entry_table_e1
  water_bottle_priya  (class: water_bottle)  at dish_rack_k1
  watering_can_shared  (class: watering_can)  at balcony_floor_y1
  yoga_mat_priya  (class: yoga_mat)  at wardrobe_b2

CLASSES (usable as `class:<name>` targets): blanket, book, bowl, camera, cushion, cutting_board, detergent, dog_bowl, dog_food_bag, dog_leash, dog_toy, doormat, duster, first_aid_kit, fruit_bowl, glass, guitar, hair_dryer, jacket, kettle, keys, kitchen_knife, lamp, laundry_basket, magazine, medication, mug, notebook, pan, pen, phone, plant_pot, plate, pot, puzzle_box, recipe_book, remote, serving_dish, shoes, shopping_bag, skincare, snack_bowl, soap_dispenser, spatula, sunglasses, tablet, tissue_box, toaster, toiletry_bag, toothbrush_holder, towel, umbrella, vacuum_cleaner, vase, wall_clock, wallet, water_bottle, watering_can, yoga_mat

Write a LIBRARY of 12 to 20 competing hypotheses about how this home runs, each a complete weekly model: for every object the walkthrough saw (directly or through its class), where it is across the week. Make the library wide: different household compositions, work patterns, evening and weekend habits, and different guesses about which objects travel and which stay. Each document differs from every other in something the robot's looks can settle, and says so in its prose. The robot's sightings over the following weeks will weight the documents; you will then be shown the library with its weights and asked to add to it.

How a document works:

- Each hypothesis is one markdown document: a heading `# p_xxxx — <title>` (p_ plus 4 random hex characters), a few paragraphs of prose (who lives here and how the week runs; what this hypothesis predicts that sets it apart from the others; what would refute it), and ONE fenced ```json block at the end.
- The json block gives `targets`: for each object id or `class:<name>`, a list of BLOCKS in priority order. A block is {"days": weekday|weekend|both, "from": <hour>, "to": <hour>, "at": <receptacle id>, "chance": rarely|sometimes|usually|almost_always}. Later blocks override earlier ones, so "at the desk all day; out 9 to 17 on weekdays" is two blocks in that order. Hours no block covers fall through to the robot's own sighting statistics for that object. A `class:` target applies to every object of the class, including objects the robot meets later.
- The block's `chance` is a starting label; the sightings inside the block adjust it. `from` and `to` are the author's and stay fixed.
- A block whose `at` is `OUT_OF_HOUSE` or `ON_PERSON` is supported by empty looks at the receptacle it overrides (where the object would be otherwise) and weakened by looks that find it there.
- Objects leave the house. Residents take things with them to work, to school, to the gym, on errands and on trips, and the walkthrough happened at one instant: anything that was out with someone at that moment is missing from the object table and will first appear later. Say in each document which objects travel, when, and with whom, as `OUT_OF_HOUSE` blocks (or `ON_PERSON` while the resident is home and holding them); a document in which nothing ever leaves is a claim in itself.
- `claims` is a list of falsifiable statements the document makes, each {"claim": <one sentence>, "target": <object id>, "expect": <receptacle id or OUT_OF_HOUSE or ON_PERSON>, "days": weekday|weekend|both, "from": <hour>, "to": <hour>}. Write at least three per document, on the objects where the documents differ. How they are scored: an in-home claim counts FOR the document when a look at `expect` in the window finds the target, and AGAINST when that look is empty or the target is sighted anywhere else; an out-of-house claim counts AGAINST when the target is sighted anywhere in the house in the window, and WEAKLY FOR when a look at the place the document would otherwise put it finds nothing. Each document's tally is shown back to you.
- Identifiers come from the tables, exactly as printed. Documents are separated by a line reading exactly `=== HYPOTHESIS ===`.

Think it through, then write the documents one after another, each preceded by the `=== HYPOTHESIS ===` line, and end your reply after the last document's json block. The example below shows the shape only; it is about a different, smaller home.

=== HYPOTHESIS ===
# p_3f1a — One commuter; the desk is the hub, the entry shelf the exit

One adult lives here and leaves for an office on weekdays around 8:30, back
around 18:00. The keys leave with her; mugs cycle between the cupboard and the
counter each morning; the towel stays on the rack. What sets this hypothesis
apart: the entry shelf is bare at weekday midday. What would refute it: keys_x
sighted anywhere in the house between 9:00 and 17:00 on a weekday.

```json
{"claims": [
   {"claim": "keys_x leave the house with the resident on weekdays",
    "target": "keys_x", "expect": "OUT_OF_HOUSE", "days": "weekday", "from": 9, "to": 17},
   {"claim": "a mug is on the counter mid-morning",
    "target": "mug_1", "expect": "counter_1", "days": "both", "from": 7, "to": 10}],
 "targets": {
   "keys_x": [
     {"days": "both", "from": 0, "to": 24, "at": "entry_shelf_1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 18, "at": "OUT_OF_HOUSE", "chance": "almost_always"}],
   "class:mug": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_1", "chance": "usually"},
     {"days": "both", "from": 6.5, "to": 10.5, "at": "counter_1", "chance": "usually"}]
 }}
```


{'omap': {}, 'rmap': {}, 'cmap': {}}
```
