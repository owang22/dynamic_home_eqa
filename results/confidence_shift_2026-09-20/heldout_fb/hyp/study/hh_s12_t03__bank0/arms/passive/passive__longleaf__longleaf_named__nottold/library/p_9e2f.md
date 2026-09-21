# p_9e2f — Cooking 18:30–20, dinner 19:30–21 (fork of p_5f2b)

Forked from p_5f2b to correct the cooking window. The 17:00 pass finds the pot in the cupboard (2 of 3 looks) and the recipe book in the pantry; the 18:00 pass confirms both in their resting spots. The 19:00 pass finds the pot on the counter and the recipe book on the counter. Cooking is 18:30–20:00, not 17:00–18:00. The parent's "pot back in cupboard 18–19" claim went against 7 times because the pot is still in the cupboard at 18:00 (not yet pulled out) and is on the counter by 19:00 (cooking underway). The corrected window is 18:30–20:00 for cooking and 19:30–21:00 for dinner at the table.

Weekday cooking happens in a narrow window around 18:30–20:00. Priya (home all day) or Elena (arrived 17:30) pulls the pot out, consults the recipe, cooks, and sets the table. The cutting board and knife block are already on the counter as their resting spots. The plates and glasses are in the cupboard at 18:00 (confirmed by the pass) and at the dining table by 20:00 (3 sightings of plate_elena). Dinner is eaten 19:30–21:00.

This document is refuted if the pot is on the counter at 17:00 (cooking earlier than claimed) or if plates are at the dining table at 18:00 (dinner earlier than claimed).

```json
{
 "claims": [
  {
   "claim": "The pot is on the kitchen counter during the weekday cooking window",
   "target": "pot_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 20
  },
  {
   "claim": "The recipe book is on the kitchen counter during the weekday cooking window",
   "target": "recipe_book_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 20
  },
  {
   "claim": "Elena's plate is at the dining table during dinner",
   "target": "plate_elena",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The pot is back in the cupboard after cooking is done",
   "target": "pot_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 20,
   "to": 21.5
  }
 ],
 "targets": {
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "plate_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
