# call 15 (decide, agent None) at d01 Thu 08:09

## system

You are the dispatcher of a home robot. The robot is asked, about 6 times a day, where one object is right now. A panel of agents has just given its forecast; you decide whether the robot answers now or first spends part of today's budget on a look. A look is a whole room: it reveals every receptacle in it and who is there, and costs 1 if the room is the one the robot is already in, 4 otherwise (the robot then stays in that room). Pockets cannot be looked into: whether an object is on a person is inferred, never seen. Looks are the panel's only source of learning: a look grades every agent on everything it predicted, so a look also pays off on later questions. Unspent budget is lost at midnight. Today's budget is 12 units against about 6 questions: that is 3 looks if every one needs travel, more if the robot stays in one room, so budget is rationed across the day and the robot's current room matters — a question whose likely spots are in the room the robot is already in is cheap to check. What a gain is worth depends on what other gains this day is likely to offer. For each candidate look you are told the one-step gain: how much the chance of answering THIS question right would rise, and its cost. You also see today's ledger (every decision so far today and what each look found) and your own NOTE, which is your only memory: rewrite it on every call (at most 120 words) with what gains have been typical, when looks paid off, and how you plan to spend the rest of the day. Reply as JSON: {"action": "look" | "answer", "target": "<a receptacle id, for a look: the robot looks at the whole room that receptacle is in>", "why": "<one sentence>", "note": "<your rewritten note>"}.

Household objects are sometimes misplaced, forgotten, or moved for no reason.

## user

QUESTION: where is snack_bowl_shared right now? Asked at d01 Thu 08:09; the robot is in kitchen.

TODAY: budget left 11 of 12; questions so far today 1; looks used today 0. At most 3 looks per question; this question has used 1.
PREVIOUS DAYS: none yet - how many questions a day brings is for you to find out.

TODAY'S LEDGER:
  Thu 08:09 snack_bowl_shared: sure 36%, best gain +0.144 -> looked at counter_k1: result pending

YOUR NOTE:
Day 1, 08:09. Robot in Kitchen. Budget 12. Q1: snack_bowl. Panel favors dining_table (36%) and counter (14%). Looked counter (cost 1) to cover kitchen spots and potentially confirm/deny top candidate. Gain 0.144. Plan: Use remaining 11 budget for ~3-4 looks. Prioritize cheap looks in current room if possible. If counter look fails, consider dining room (cost 4) for dining_table/sideboard. Keep notes on agent accuracy.

PANEL FORECAST (share of belief): dining_table_d1 36%, counter_k1 13%, kitchen_table_k1 12%, sideboard_d1 6%, OUT_OF_HOUSE 4%.
AGENTS' TOP SPOTS (by credibility): dining_table_d1 100%.

VALUE OF INFORMATION (one-step, this question only):
  look at dining_table_d1: chance of a right answer 36% -> 48% (gain 0.125)
  look at kitchen_table_k1: chance of a right answer 36% -> 48% (gain 0.121)
  look at sideboard_d1: chance of a right answer 36% -> 42% (gain 0.063)
  look at ON_PERSON: chance of a right answer 36% -> 38% (gain 0.018)
  look at armchair_l1: chance of a right answer 36% -> 36% (gain 0.007)

LOOKS SO FAR ON THIS QUESTION:
  d01 Thu 08:09 look at chair_k1: (nothing)
  d01 Thu 08:09 look at cupboard_k1: bowl_hana, mug_hana
  d01 Thu 08:09 look at dish_rack_k1: (nothing)
  d01 Thu 08:09 look at drawer_k_k1: (nothing)
  d01 Thu 08:09 look at floor_k_k1: (nothing)
  d01 Thu 08:09 look at kitchen_table_k1: bowl_priya, fruit_bowl_shared, mug_priya, tablet_priya
  d01 Thu 08:09 look at pantry_shelf_k1: dog_bowl_shared, dog_food_bag_shared
  d01 Thu 08:09 look at sink_k1: cutting_board_shared, kitchen_knife_shared, pan_shared, plate_hana, plate_priya, pot_shared, spatula_shared
  d01 Thu 08:09 look at counter_k1: kettle_shared, plant_pot_2_shared, recipe_book_shared, shopping_bag_shared, toaster_shared, wall_clock_shared, water_bottle_priya

LEGAL LOOK TARGETS NOW: armchair_l1, balcony_floor_y1, balcony_table_y1, bathroom_shelf_ba1, bed_b1, bed_b2, bedroom_floor_b1, bedroom_floor_b2, bookshelf_l1, chair_d_d1, chair_k1, coffee_table_l1, couch_l1, cupboard_k1, desk_b1, desk_b2, dining_table_d1, dish_rack_k1, drawer_k_k1, dresser_b1, dresser_b2, entry_floor_e1, entry_hook_e1, entry_table_e1, floor_k_k1, floor_l_l1, kitchen_table_k1, medicine_cabinet_ba1, nightstand_b1, nightstand_b2, pantry_shelf_k1, shoe_rack_e1, side_table_l1, sideboard_d1, sink_ba_ba1, sink_k1, storage_floor_s1, storage_shelf_s1, towel_rack_ba1, tv_stand_l1, wardrobe_b1, wardrobe_b2, ON_PERSON.

Decide: answer now, or look (name the target). One sentence why.

## reply

{"action": "look", "target": "dining_table_d1", "why": "The top candidate (36%) is in the dining room; looking there offers the highest gain (0.125) and resolves the primary uncertainty.", "note": "Day 1, 08:09. Robot in Kitchen. Budget 11 left. Q1: snack_bowl. Kitchen fully searched (counter, table, sink, etc.) - snack_bowl NOT in kitchen. Panel strongly favors dining_table_d1 (36%). Looked dining_table_d1 (cost 4). If found, answer. If not, check sideboard_d1 (6%) or accept OUT_OF_HOUSE/low confidence. Remaining budget 7. Prioritize dining room spots. Note: Kitchen search was thorough; object likely in dining or living."}
