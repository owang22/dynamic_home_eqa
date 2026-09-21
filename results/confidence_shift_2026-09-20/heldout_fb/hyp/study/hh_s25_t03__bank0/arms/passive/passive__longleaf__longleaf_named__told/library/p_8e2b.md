# p_8e2b — Weekend shift: sleep in, balcony gardening at 11, dinner at 20, blanket on coffee table

On weekends the household runs on a different clock, as the residents' messages confirm: "we're off our usual routine and around the house more." Both residents sleep in—glasses appear at the bathroom shelf at 07:00–09:00 rather than 06:00–07:00 on weekdays. Around 10:00–12:00, Marco tends the houseplants on the balcony and the watering can moves from the floor to the table (seen there at 11:00 on the weekend). Midday is for errands; shopping bags appear at the kitchen counter at 16:00–17:00 as groceries are unpacked. Dinner is later on weekends (20:00–21:30 rather than 19:00–20:30 on weekdays), so the pan, spatula, and recipe book hit the counter at 19:30–20:30. The blanket shifts from the couch (weekday evening) to the coffee table (weekend evening), where it is used for reading and napping. Omar spends long stretches at the kitchen table in the afternoon—his glass was seen there five times at 14:00 on a weekend, suggesting a long midday drink or snack. The residents are more "around the house": more bathroom time (towels at the shelf at 11:00), more kitchen time, less desk time.

This document is the only one that systematically shifts all meal and activity windows later on weekends, places the blanket at the coffee table on weekends (vs. couch on weekdays), and predicts the watering can on the balcony table at 10:00–12:00. It sets itself apart from p_a1b2 and p_4389 which treat weekdays and weekends identically, and from p_a387 (retired) which split the weekend by resident rather than by time-of-day shift.

This document is refuted if: the blanket is on the couch during weekend evenings (20:00–23:00); dinner starts before 19:30 on a weekend; the watering can is never seen on the balcony table; or the shopping bags are not at the counter on weekend afternoons.

```json
{
 "claims": [
  {
   "claim": "The watering can is in use on the balcony table during weekend morning gardening",
   "target": "watering_can_shared",
   "expect": "balcony_table_y1",
   "days": "weekend",
   "from": 10,
   "to": 11.5
  },
  {
   "claim": "The blanket is on the coffee table during weekend evenings",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 20,
   "to": 23
  },
  {
   "claim": "The serving dish is at the dining table during the later weekend dinner",
   "target": "serving_dish_shared",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 20,
   "to": 21.5
  },
  {
   "claim": "Omar's glasses are on the bathroom shelf during the later weekend morning",
   "target": "glasses_omar",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Omar's glass is at the kitchen table during the weekend midday stretch",
   "target": "glass_omar",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 13,
   "to": 16
  }
 ],
 "targets": {
  "watering_can_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "balcony_floor_y1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "balcony_table_y1",
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
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21,
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
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
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
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "class:plate": [
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
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "class:glass": [
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
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 18,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "glasses_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 9,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 22.5,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 9,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "glass_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 16,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ]
 }
}
```
