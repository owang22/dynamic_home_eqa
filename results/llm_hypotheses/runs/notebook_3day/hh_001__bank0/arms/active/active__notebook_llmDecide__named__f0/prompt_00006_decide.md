# call 6 (decide, agent None) at d00 Mon 04:42

## system

You are the dispatcher of a home robot. The robot is asked, many times a day, where one object is right now. A panel of agents has just given its forecast; you decide whether the robot answers now or first spends one of today's looks (opening one receptacle, or checking one resident it has listed). Looks are the panel's only source of learning: a look grades every agent on everything it predicted, so a look also pays off on later questions. Unspent looks are lost at midnight, and a day has far more questions than looks, so looks are rationed across the day: what a gain is worth depends on what other gains this day is likely to offer. For each candidate look you are told the one-step gain: how much the chance of answering THIS question right would rise. You also see today's ledger (every decision so far today and what each look found) and your own NOTE, which is your only memory: rewrite it on every call (at most 120 words) with what gains have been typical, when looks paid off, and how you plan to spend the rest of the day. Reply as JSON: {"action": "look" | "answer", "target": "<receptacle or resident id, for a look>", "why": "<one sentence>", "note": "<your rewritten note>"}.

Household objects are sometimes misplaced, forgotten, or moved for no reason.

## user

QUESTION: where is medication_bottle_mara right now? Asked at d00 Mon 04:42; the robot is in kitchen.

TODAY: looks left 8 of 8; questions so far today 1; looks used today 0. At most 3 looks per question; this question has used 0.
PREVIOUS DAYS: none yet - how many questions a day brings is for you to find out.

TODAY'S LEDGER:
  (first decision of the day)

YOUR NOTE:
(empty)

PANEL FORECAST (share of belief): nightstand_b1 30%, bathroom_shelf_ba1 12%, desk_b1 7%, counter_k1 6%, bed_b1 5%.
AGENTS' TOP SPOTS (by credibility): nightstand_b1 50%, bathroom_shelf_ba1 50%.

VALUE OF INFORMATION (one-step, this question only):
  look at nightstand_b1: chance of a right answer 30% -> 43% (gain 0.123)
  look at bathroom_shelf_ba1: chance of a right answer 30% -> 43% (gain 0.123)
  look at desk_b1: chance of a right answer 30% -> 37% (gain 0.066)
  look at counter_k1: chance of a right answer 30% -> 37% (gain 0.062)
  look at bed_b1: chance of a right answer 30% -> 35% (gain 0.049)

LOOKS SO FAR ON THIS QUESTION:
  nothing yet

LEGAL LOOK TARGETS NOW: bed_b1, nightstand_b1, desk_b1, bedroom_floor_b1, couch_l1, coffee_table_l1, tv_stand_l1, bookshelf_l1, armchair_l1, counter_k1, sink_k1, cupboard_k1, dish_rack_k1, kitchen_table_k1, chair_k1, chair_k2, bathroom_shelf_ba1, towel_rack_ba1, entry_table_e1, entry_hook_e1, entry_floor_e1.

Decide: answer now, or look (name the target). One sentence why.

## reply

{"action": "look", "target": "nightstand_b1", "why": "Highest one-step gain (0.123) and top agent credibility; first look of the day to establish baseline value.", "note": "Day 1, Q1. 8 looks left. Top gain 0.123 (nightstand/bathroom). Agents split 50/50. Plan: spend looks on high-gain targets (>0.10) to maximize learning; save looks for later if gains drop. First look: nightstand_b1."}
