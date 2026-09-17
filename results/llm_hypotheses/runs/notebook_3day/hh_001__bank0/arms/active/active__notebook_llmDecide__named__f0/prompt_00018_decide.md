# call 18 (decide, agent None) at d00 Mon 04:42

## system

You are the dispatcher of a home robot. The robot is asked, many times a day, where one object is right now. A panel of agents has just given its forecast; you decide whether the robot answers now or first spends one of today's looks (opening one receptacle, or checking one resident it has listed). Looks are the panel's only source of learning: a look grades every agent on everything it predicted, so a look also pays off on later questions. Unspent looks are lost at midnight, and a day has far more questions than looks, so looks are rationed across the day: what a gain is worth depends on what other gains this day is likely to offer. For each candidate look you are told the one-step gain: how much the chance of answering THIS question right would rise. You also see today's ledger (every decision so far today and what each look found) and your own NOTE, which is your only memory: rewrite it on every call (at most 120 words) with what gains have been typical, when looks paid off, and how you plan to spend the rest of the day. Reply as JSON: {"action": "look" | "answer", "target": "<receptacle or resident id, for a look>", "why": "<one sentence>", "note": "<your rewritten note>"}.

Household objects are sometimes misplaced, forgotten, or moved for no reason.

## user

QUESTION: where is medication_bottle_mara right now? Asked at d00 Mon 04:42; the robot is in bedroom.

TODAY: looks left 7 of 8; questions so far today 1 of about 24; looks used today 1. At most 3 looks per question; this question has used 1.

TODAY'S LEDGER:
  Mon 04:42 medication_bottle_mara: sure 30%, best gain +0.123 -> looked at nightstand_b1: phone_mara

YOUR NOTE:
Day 00, 04:42. First question: medication_bottle_mara. Panel top: nightstand_b1 (30%), bathroom_shelf_ba1 (12%). Gains: nightstand/bathroom ~0.123, others <0.07. Strategy: Spend first look on highest gain target to establish baseline accuracy and update beliefs for the 23 remaining questions. 8 looks left.

PANEL FORECAST (share of belief): bathroom_shelf_ba1 17%, desk_b1 14%, nightstand_b1 10%, bed_b1 6%, counter_k1 5%.
AGENTS' TOP SPOTS (by credibility): desk_b1 39%, bathroom_shelf_ba1 36%, bed_b1 23%, nightstand_b1 2%.

VALUE OF INFORMATION (one-step, this question only):
  look at desk_b1: chance of a right answer 17% -> 31% (gain 0.140)
  look at bathroom_shelf_ba1: chance of a right answer 17% -> 31% (gain 0.140)
  look at bed_b1: chance of a right answer 17% -> 23% (gain 0.055)
  look at counter_k1: chance of a right answer 17% -> 22% (gain 0.047)
  look at resident resident_1: chance of a right answer 17% -> 21% (gain 0.040)

LOOKS SO FAR ON THIS QUESTION:
  d00 Mon 04:42 look at nightstand_b1: phone_mara; residents here: resident_1

LEGAL LOOK TARGETS NOW: bed_b1, desk_b1, bedroom_floor_b1, couch_l1, coffee_table_l1, tv_stand_l1, bookshelf_l1, armchair_l1, counter_k1, sink_k1, cupboard_k1, dish_rack_k1, kitchen_table_k1, chair_k1, chair_k2, bathroom_shelf_ba1, towel_rack_ba1, entry_table_e1, entry_hook_e1, entry_floor_e1, resident_1.

Decide: answer now, or look (name the target). One sentence why.

## reply

{"action": "look", "target": "desk_b1", "why": "The nightstand look was a miss, so I must spend my second allowed look on the highest-gain target (desk_b1, +0.140) to maximize the chance of finding the medication before answering.", "note": "Day 00, 04:42. Q1: medication_bottle_mara. Look 1 (nightstand_b1) found phone_mara, not med. Panel updated: desk_b1 (14%) and bathroom_shelf_ba1 (17%) are top candidates. Gains for both are 0.140. I have 1 look left for this question (max 3). Strategy: Use look 2 on desk_b1 (highest credibility agent support 39% + high gain). If found, answer. If not, answer with best remaining guess (bathroom_shelf_ba1). 7 looks left for day."}
