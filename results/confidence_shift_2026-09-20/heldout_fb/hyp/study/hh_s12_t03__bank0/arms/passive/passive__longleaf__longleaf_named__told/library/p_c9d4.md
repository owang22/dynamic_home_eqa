# p_c9d4 — The 20:00 dinner: cooking 17–19, table set by 19:30, cleared by 21:30

The weekday dinner sequence runs as follows. Cooking begins around 17:00 (the pot appears on the counter at 17:00, the recipe book moves to the counter at 17:00 and 19:00). Active cooking with the pan, cutting board, and knife occupies 18:00–19:00 (all three are on the counter or kitchen table in that window). The table is set by 19:30: Priya's water bottle and glass appear at the dining table at 19:00, and Elena's glass and plate appear at the dining table at 20:00 (five and three sightings respectively). Dinner is consumed 19:30–21:00. By 21:00–21:30 the table is cleared: Priya's glass is back at the sink at 21:00, and Elena's plate returns to the cupboard by 22:00.

This document differs from p_a1b2 (dinner 18.5–20) and p_4c7d (dinner 19.5–21) by centring the plate-and-glass window at 20:00, matching the clock-hour evidence where plate_elena and glass_elena first appear at the dining table at 20:00. It differs from p_a3f7 (dinner 19:30–21, cook 17–19:30) by narrowing the cooking window and adding the specific 17:00 pot and recipe-book sightings. It differs from p_5f2b (retired, 5-to-8 prep) by placing the main cooking at 17–19 rather than 17–20.

What would refute this document: plate_elena or glass_elena at the dining table before 19:00 on a weekday; the pot on the counter before 16:30 on a weekday; the cutting board in the cupboard at 18:30 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Elena's plate is at the dining table during the 20:00 dinner on a weekday",
   "target": "plate_elena",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Elena's glass is at the dining table during the 20:00 dinner on a weekday",
   "target": "glass_elena",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The pot is on the kitchen counter during the 17:00\u201319:00 weekday cooking window",
   "target": "pot_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Priya's water bottle is at the dining table during the 20:00 dinner on a weekday",
   "target": "water_bottle_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The cutting board is on the kitchen counter during the 18:00\u201319:00 weekday cooking window",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
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
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
    "to": 19.5,
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
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21.5,
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
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "glass_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ]
 }
}
```
