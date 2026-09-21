# p_f6d2 — Evening TV Setup: Serving Dish and Snacks to the Coffee Table

After dinner (around 19:30), the household settles into the living room for TV. The serving dish moves from the kitchen table (where it held dinner, sighted at 20:00) to the coffee table (sighted at 21:00 and 23:00). The snack bowl, which rests in the cupboard or on the counter during the day, appears on the counter at 22:00 and on the coffee table at 23:00 — it is brought out for evening snacking. The remote is at the TV stand during the day and on the coffee table during TV hours (19:30–22:00), as other documents already model.

This document focuses on the 20:00–23:30 evening window and the specific migration of the serving dish and snack bowl into the living room. It differs from p_b7c2 (which puts the snack bowl on the coffee table 19:30–22:00) by extending the window to 23:30 (the 23:00 sighting at coffee_table_l1) and by adding the serving dish's two-stage move (kitchen table at 20:00 → coffee table at 21:00+).

Refutation: if the serving dish is found in the cupboard at 21:00 or 22:00 on a weekday evening, or if the snack bowl is never on the coffee table after 22:00 in 5+ passes, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The serving dish is on the coffee table during the evening TV period",
   "target": "serving_dish_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23.5
  },
  {
   "claim": "The snack bowl is on the coffee table during the evening TV period",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 24
  },
  {
   "claim": "The serving dish is on the kitchen table just after dinner before moving to the living room",
   "target": "serving_dish_shared",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 19.5,
   "to": 21
  }
 ],
 "targets": {
  "serving_dish_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 22.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22.5,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:remote": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
