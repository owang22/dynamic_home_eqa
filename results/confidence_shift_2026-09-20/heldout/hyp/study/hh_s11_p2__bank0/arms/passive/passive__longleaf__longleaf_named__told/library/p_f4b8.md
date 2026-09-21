# p_f4b8 — Weekend Kitchen: Storage Mode, Light Evening Cook

On weekends the kitchen is in "storage mode" for most of the day. The cutting board sits on the counter (not the sink as on weekdays), the knife and spatula are in the drawer, the pan and pot are in the cupboard, and the recipe book is on the pantry shelf. Around 18:00–20:00 there is a light evening cook (dinner at 20:00 is confirmed by plates and glasses appearing at the dining table), so the recipe book moves to the counter, the pan and pot come out, and the knife and spatula are drawn from the drawer. By 22:00 everything is put back. Water bottles for both residents are in the dish rack all day (washed and drying, not out at the table or on the counter). Mugs, plates, bowls, and the serving dish are in the cupboard. The fruit bowl stays on the kitchen table, the kettle and toaster on the counter, and the wall clock on the counter.

This document differs from p_7f1e (weekday 18:00 dinner prep with pan/knife on counter), p_789a (midnight cook), and p_e5f6 (shared breakfast) by placing kitchen items in their weekend storage spots for the bulk of the day and only pulling them out for the brief 18:00–20:00 cook. It would be refuted if the cutting board is found at the sink, the knife on the counter outside the cook window, or the water bottles off the dish rack.

```json
{
 "claims": [
  {
   "claim": "The cutting board is on the kitchen counter, not the sink, on the weekend",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Priya's water bottle is in the dish rack all day on the weekend",
   "target": "water_bottle_priya",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 0,
   "to": 20
  },
  {
   "claim": "The pan is in the cupboard, not the sink or counter, for most of the weekend day",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 0,
   "to": 18
  },
  {
   "claim": "The serving dish is in the cupboard during the weekend afternoon",
   "target": "serving_dish_shared",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 12,
   "to": 18
  },
  {
   "claim": "The kitchen knife is in the drawer, not on the counter, during the weekend morning",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekend",
   "from": 0,
   "to": 18
  }
 ],
 "targets": {
  "cutting_board_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 22,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "dish_rack_k1",
    "chance": "almost_always"
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
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "dish_rack_k1",
    "chance": "almost_always"
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
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
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
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
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
  "plate_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
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
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 18,
    "at": "pantry_shelf_k1",
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
  "glass_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 14,
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
  "mug_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "class:bowl": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "kettle_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "toaster_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
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
  ]
 }
}
```
