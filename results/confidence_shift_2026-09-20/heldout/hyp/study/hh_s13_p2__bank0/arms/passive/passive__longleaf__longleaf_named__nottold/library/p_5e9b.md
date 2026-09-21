# p_5e9b — The 20:00 Supper: Dinner Is Later Than the Library Thought

Every document in the library places the evening meal at 18:30–19:30. The clock-hour data says otherwise. At the 18:00 pass, plate_hana is at cupboard_k1 x4 (still in the cupboard), glass_hana is scattered across four receptacles (none at the table), and the pan is at cupboard_k1 x3. At the 20:00 pass, plate_hana is at kitchen_table_k1 x4, plate_priya at kitchen_table_k1 x4, glass_hana at kitchen_table_k1 x4, glass_priya at kitchen_table_k1 x4, and water_bottle_hana at kitchen_table_k1 x4. Both residents are sighted in the kitchen at 20:00 on Friday, Saturday, and Sunday. The pan at 20:00 is at sink_k1 x2, counter_k1 x1, dish_rack_k1 x1 — it has been used and is being washed. The meal happens at 20:00, and the cooking window is 19:00–20:00 (the pan moves from cupboard to counter to sink between the 18:00 and 20:00 passes).

This document shifts all evening meal objects to a 19:30–21:00 window. It also places the pan in the cupboard at 18:00 (not on the counter), which is where the 18:00 pass actually finds it three of four times. The p_b9c4 claim "pan on counter at 18:00" went against 12 times; the p_c1d6 claim "pan on counter at 18:00" also went against 12 times.

What sets this apart: at 20:00 on a weekday, all four plates and glasses are at kitchen_table_k1, and the pan is in the sink or dish rack (post-meal cleanup). At 18:00, the pan is in the cupboard. What would refute it: plates at kitchen_table_k1 at 18:00 on a weekday (they should still be in the cupboard), or the pan on the counter at 18:00.

```json
{
 "claims": [
  {
   "claim": "Hana's plate is at the kitchen table at 20:00 on a weekday",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Priya's glass is at the kitchen table at 20:00 on a weekday",
   "target": "glass_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Hana's water bottle is at the kitchen table at 20:00 on a weekday",
   "target": "water_bottle_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  }
 ],
 "targets": {
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
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "class:glass": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "class:mug": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "class:pan": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "class:pot": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21,
    "at": "sink_k1",
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
    "days": "both",
    "from": 20,
    "to": 21,
    "at": "sink_k1",
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
    "days": "both",
    "from": 20,
    "to": 21,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
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
