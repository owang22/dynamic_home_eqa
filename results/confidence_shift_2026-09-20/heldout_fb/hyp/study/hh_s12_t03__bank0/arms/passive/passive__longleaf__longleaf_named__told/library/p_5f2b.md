# p_5f2b — The 5-to-8 cooking and dinner prep

Weekday cooking happens in a narrow window around 17:00–18:00. The pot and the recipe book are both seen on the kitchen counter at 17:00 and back in their resting spots (cupboard and pantry shelf) by 18:00. That one-hour gap is the cooking session: someone (most likely Priya, who is home, or Elena who arrives at 17:30) pulls the pot out, consults the recipe, cooks, and puts everything back. The cutting board and knife block are already on the counter as their resting spots, so they are available without a visible move. The plates and glasses are in the cupboard or sink at 18:00 (not yet at the table), confirming that dinner is *set* after 18:00 and eaten around 19:00–20:00.

This document focuses exclusively on the 17–20 h cooking-to-dinner transition and says nothing about the commute or the office. It complements p_9d4e (which covers 18–23 h TV) by covering the kitchen side. It is refuted if the pot is found in the cupboard at 17:00 (no cooking) or if the recipe book is on the counter at 12:00 (cooking at a different time).

```json
{
 "claims": [
  {
   "claim": "The pot is on the kitchen counter during the weekday cooking window",
   "target": "pot_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 17,
   "to": 18
  },
  {
   "claim": "The recipe book is on the kitchen counter during the weekday cooking window",
   "target": "recipe_book_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 17,
   "to": 18
  },
  {
   "claim": "Elena's plate is at the dining table during dinner",
   "target": "plate_elena",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The pot is back in the cupboard after cooking is done",
   "target": "pot_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
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
    "from": 17,
    "to": 18,
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
    "from": 17,
    "to": 18,
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
    "from": 19,
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
    "from": 19,
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
   }
  ]
 }
}
```
