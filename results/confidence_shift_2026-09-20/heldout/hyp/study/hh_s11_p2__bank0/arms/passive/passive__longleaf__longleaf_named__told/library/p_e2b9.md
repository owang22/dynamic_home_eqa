# p_e2b9 — Tuesday Friends; the Serving Dish Moves, the Rest Stays (fork of p_e7c3)

The parent p_e7c3 was written for the Friday friends evening and predicted a full social-object migration: serving dish to the dining table, fruit bowl to the dining table, snack bowl to the coffee table, puzzle box to the dining table. The evidence from the Friday evening and the following days has been harsh: the fruit bowl claim scored **for 0, against 20** (it never left kitchen_table_k1), the snack bowl **for 0, against 27** (it stayed in the cupboard or on the counter), and the puzzle box **for 0, against 10** (it never left the bookshelf). Only the serving dish showed any movement toward the dining table (for 3, against 14), and even that was in the 20:00 pass, not the 18:00 window the parent specified.

The Tuesday message says friends are coming again. This fork keeps the serving-dish-to-dining-table prediction but narrows the window to 19–22h (the 18:00 pass still shows it in the cupboard). It drops the fruit bowl, snack bowl, and puzzle box from the dining/coffee table entirely — they stay in their normal resting spots. The plates and glasses do appear at the dining table at 20:00 (glass_priya 3/4, plate_priya 3/4), consistent with dinner being served to guests. The blanket shifts to the couch for the gathering, and the remote is at the coffee table or TV stand.

What would refute this fork: the fruit bowl found at the dining table during the evening; the puzzle box found off the bookshelf; the serving dish still in the cupboard at 20:00.

_(targets the fork left unstated are inherited from p_e7c3)_

```json
{
 "claims": [
  {
   "claim": "The serving dish is at the dining table during the Tuesday evening dinner for friends",
   "target": "serving_dish_shared",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "The fruit bowl stays at the kitchen table even during the friends evening",
   "target": "fruit_bowl_shared",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 18,
   "to": 23
  },
  {
   "claim": "The puzzle box stays on the bookshelf during the friends evening; no board games tonight",
   "target": "puzzle_box_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 18,
   "to": 23
  },
  {
   "claim": "Priya's glass is at the dining table during the Tuesday evening dinner service",
   "target": "glass_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
  "serving_dish_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "fruit_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 22,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 22,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 22,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "plate_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "glass_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "nightstand_b2",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "mug_priya": [
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ]
 }
}
```
