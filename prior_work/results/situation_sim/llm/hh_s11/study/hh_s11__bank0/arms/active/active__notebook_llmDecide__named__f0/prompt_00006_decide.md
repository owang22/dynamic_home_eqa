# call 6 (decide, agent None) at d01 Thu 08:09

## system

You are the dispatcher of a home robot. The robot is asked, about 6 times a day, where one object is right now. A panel of agents has just given its forecast; you decide whether the robot answers now or first spends part of today's budget on a look. A look is a whole room: it reveals every receptacle in it and who is there, and costs 1 if the room is the one the robot is already in, 4 otherwise (the robot then stays in that room). Pockets cannot be looked into: whether an object is on a person is inferred, never seen. Looks are the panel's only source of learning: a look grades every agent on everything it predicted, so a look also pays off on later questions. Unspent budget is lost at midnight. Today's budget is 12 units against about 6 questions: that is 3 looks if every one needs travel, more if the robot stays in one room, so budget is rationed across the day and the robot's current room matters — a question whose likely spots are in the room the robot is already in is cheap to check. What a gain is worth depends on what other gains this day is likely to offer. For each candidate look you are told the one-step gain: how much the chance of answering THIS question right would rise, and its cost. You also see today's ledger (every decision so far today and what each look found) and your own NOTE, which is your only memory: rewrite it on every call (at most 120 words) with what gains have been typical, when looks paid off, and how you plan to spend the rest of the day. Reply as JSON: {"action": "look" | "answer", "target": "<a receptacle id, for a look: the robot looks at the whole room that receptacle is in>", "why": "<one sentence>", "note": "<your rewritten note>"}.

Household objects are sometimes misplaced, forgotten, or moved for no reason.

## user

QUESTION: where is snack_bowl_shared right now? Asked at d01 Thu 08:09; the robot is in kitchen.

TODAY: budget left 12 of 12; questions so far today 1; looks used today 0. At most 3 looks per question; this question has used 0.
PREVIOUS DAYS: none yet - how many questions a day brings is for you to find out.

TODAY'S LEDGER:
  (first decision of the day)

YOUR NOTE:
(empty)

PANEL FORECAST (share of belief): dining_table_d1 36%, counter_k1 14%, sideboard_d1 8%, kitchen_table_k1 7%, coffee_table_l1 4%.
AGENTS' TOP SPOTS (by credibility): dining_table_d1 100%.

VALUE OF INFORMATION (one-step, this question only):
  look at counter_k1: chance of a right answer 36% -> 50% (gain 0.144)
  look at dining_table_d1: chance of a right answer 36% -> 50% (gain 0.144)
  look at sideboard_d1: chance of a right answer 36% -> 44% (gain 0.081)
  look at kitchen_table_k1: chance of a right answer 36% -> 43% (gain 0.072)
  look at coffee_table_l1: chance of a right answer 36% -> 40% (gain 0.036)

LOOKS SO FAR ON THIS QUESTION:
  nothing yet

LEGAL LOOK TARGETS NOW: armchair_l1, balcony_floor_y1, balcony_table_y1, bathroom_shelf_ba1, bed_b1, bed_b2, bedroom_floor_b1, bedroom_floor_b2, bookshelf_l1, chair_d_d1, chair_k1, coffee_table_l1, couch_l1, counter_k1, cupboard_k1, desk_b1, desk_b2, dining_table_d1, dish_rack_k1, drawer_k_k1, dresser_b1, dresser_b2, entry_floor_e1, entry_hook_e1, entry_table_e1, floor_k_k1, floor_l_l1, kitchen_table_k1, medicine_cabinet_ba1, nightstand_b1, nightstand_b2, pantry_shelf_k1, shoe_rack_e1, side_table_l1, sideboard_d1, sink_ba_ba1, sink_k1, storage_floor_s1, storage_shelf_s1, towel_rack_ba1, tv_stand_l1, wardrobe_b1, wardrobe_b2, ON_PERSON.

Decide: answer now, or look (name the target). One sentence why.

## reply

{"action": "look", "target": "counter_k1", "why": "Looking at the kitchen counter is the cheapest option (cost 1) that reveals the top two most likely locations (dining table and counter), maximizing information gain per unit of budget.", "note": "Day 1, 08:09. Robot in Kitchen. Budget 12. Q1: snack_bowl. Panel favors dining_table (36%) and counter (14%). Looked counter (cost 1) to cover kitchen spots and potentially confirm/deny top candidate. Gain 0.144. Plan: Use remaining 11 budget for ~3-4 looks. Prioritize cheap looks in current room if possible. If counter look fails, consider dining room (cost 4) for dining_table/sideboard. Keep notes on agent accuracy."}
