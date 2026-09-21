# p_d7f3 — Weekday evening: staggered cook, 20:00 meal, sink drying

Yuki arrives home around 17:30 on weekdays and starts cooking almost immediately. Omar is at his afternoon-to-night shift (out roughly 13:40–23:00), so the evening kitchen work is entirely hers. The evidence from the single Tuesday pass shows a clear three-phase evening: a **cooking phase** (17:30–19:00) in which the cutting board is out on the counter while the knife is still in the drawer and the pan still in the cupboard; a **meal phase** (≈19:30–21:00) in which plates, glasses, and Yuki's water bottle are on the dining table; and a **cleanup-and-wind-down phase** (21:00–23:00) in which everything used ends up at the sink to dry, the pot goes back to the pantry, the snack bowl migrates to the coffee table, and the remote shifts from the TV stand to the side table as Yuki settles into the living room.

What sets this hypothesis apart: p_c007 places the pan and knife on the counter during 18–19.5 h, but the 18:00 pass finds the pan in the cupboard and the knife in the drawer—they have not yet been taken out. p_a1b2 puts plates on the dining table during 18–19.5 h, but the 18:00 pass finds them in the cupboard; they arrive at the table closer to 20:00. p_b2c8 keeps Yuki's water bottle at the entry hook until 23:00, yet the 20:00 pass finds it on the dining table with the meal. This document shifts the meal window later (19.5–21 h) and the cooking-item wash window earlier (19–22 h at the sink), and it tracks the water bottle from hook → table → sink rather than leaving it at the hook.

Refutation: if future passes show the pan or knife on the counter at 18:00 (supporting p_c007), or plates on the table before 19:30 (supporting p_a1b2), or the water bottle still at the entry hook at 20:00 (supporting p_b2c8), this document's windows are wrong. If Omar is seen in the kitchen or dining room before 22:30 on a weekday, the "Yuki cooks alone" premise shifts.

```json
{
 "claims": [
  {
   "claim": "Yuki's plate is on the dining table during the 20:00 meal on weekdays",
   "target": "plate_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Yuki's water bottle is on the dining table during the meal, not still at the entry hook",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The pan is at the sink (washed) by 20:00 on weekdays, not still on the counter",
   "target": "pan_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 19.5,
   "to": 22
  },
  {
   "claim": "The cutting board is on the counter during active cooking at 18:00 on weekdays",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The snack bowl is on the coffee table during Yuki's evening TV at 22:00 on weekdays",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 22,
   "to": 24
  }
 ],
 "targets": {
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 23,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 23,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 18.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 23,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 18.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 23,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "plate_yuki": [
   {
    "days": "weekday",
    "from": 17,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "weekday",
    "from": 17,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "weekday",
    "from": 17,
    "to": 19.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "mug_yuki": [
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "side_table_l1",
    "chance": "usually"
   }
  ],
  "laptop_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "keys_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "backpack_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "helmet_omar": [
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "bike_lock_omar": [
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "tablet_omar": [
   {
    "days": "weekday",
    "from": 7,
    "to": 23,
    "at": "chair_k1",
    "chance": "usually"
   }
  ]
 }
}
```
