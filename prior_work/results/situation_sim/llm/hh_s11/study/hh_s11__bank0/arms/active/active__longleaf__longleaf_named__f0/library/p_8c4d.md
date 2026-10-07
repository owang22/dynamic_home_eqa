# p_8c4d — The kitchen counter is a permanent display; dishes cycle sink-then-cupboard

This document isolates the "fixture" layer of the kitchen that no other document models explicitly. The counter_k1 is not a work surface that changes with the meal cycle; it is a permanent display shelf holding the kettle, toaster, wall clock, and plant_pot_2 every single day (3/3 sighted days, 3/3 weekday 9–17 h looks found them there, zero misses). The fruit_bowl_shared is likewise a permanent fixture on kitchen_table_k1 (3/3, 3/3). These items do not move for cooking, cleaning, or any other activity. What sets this document apart: it makes near-certain (almost_always) predictions for these five objects at all hours, and it models the dish/utensil cycle as a three-phase rotation—(1) 9–12 h: active use at sink_k1 during cooking, (2) 12–14 h: brief rest at sink_k1 or dish_rack_k1 while drying, (3) 14–19 h: stored in cupboard_k1, drawer_k_k1, or back on counter_k1. The day-2 16:00 walkthrough confirmed phase 3: pan, pot, plates, bowls, glasses, mugs, and spatula were all in cupboard or drawer, not at the sink. What would refute it: finding the kettle, toaster, or wall_clock anywhere other than counter_k1, or finding the fruit bowl off the kitchen table, at any hour on any day.

```json
{
 "claims": [
  {
   "claim": "The kettle is on the kitchen counter on weekday midday (permanent fixture)",
   "target": "kettle_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "The fruit bowl is on the kitchen table on weekday midday (permanent fixture)",
   "target": "fruit_bowl_shared",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "The pan is in the cupboard on weekday late afternoon (post-drying storage)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The toaster is on the kitchen counter on weekday midday (permanent fixture)",
   "target": "toaster_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
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
  "wall_clock_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "plant_pot_2_shared": [
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
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 14,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "class:bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 14,
    "to": 19,
    "at": "cupboard_k1",
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
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 14,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
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
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 14,
    "to": 19,
    "at": "cupboard_k1",
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
    "from": 9,
    "to": 12,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
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
    "from": 9,
    "to": 12,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 19,
    "at": "cupboard_k1",
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
    "from": 9,
    "to": 12,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 19,
    "at": "drawer_k_k1",
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
    "from": 9,
    "to": 12,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 19,
    "at": "drawer_k_k1",
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
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   }
  ]
 }
}
```
