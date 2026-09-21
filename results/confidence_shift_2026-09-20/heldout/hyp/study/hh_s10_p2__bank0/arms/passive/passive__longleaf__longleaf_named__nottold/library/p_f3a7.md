# p_f3a7 — Yuki's solo weekday dinner: chop, cook, eat, wash, watch

On weekday evenings Yuki comes home at 5:30 and starts cooking almost immediately. Omar is on his afternoon-to-night shift until 11, so she cooks and eats alone. The Tuesday evidence traces the full arc: at 18:00 she is in the kitchen with the cutting board on the counter (chopping), the pan still in the cupboard, the knife in the drawer. The meal is served at the dining table, not the kitchen table: by 20:00 the plates, glasses, and her water bottle are all at the dining table while the cooking tools have already been moved to the sink. By 22:00 the dishes are done and she has shifted to the living room for TV — the remote has moved from the TV stand to the side table, the snack bowl from the sink to the coffee table, and the blanket is on the couch.

This hypothesis differs from p_c007 in that the active-cooking window is 18:00–19:30 and the pan is in the cupboard at 18:00 (not at the counter as p_c007 claims for 18–19.5 h). It differs from p_b2c8 in that Yuki's water bottle and other items do migrate from the entry to the dining table for the meal; the entry is not a permanent dumping ground. It differs from p_a1b2 in that the plates are at the dining table from roughly 19:30 to 21:00, not from 18:00.

Refutation: if Omar is seen cooking or eating at the table on a weekday evening; if the meal is at the kitchen table; if cooking starts before 17:00; if the water bottle stays at the entry hook through the meal; if the remote is still at the TV stand at 22:00.

```json
{
 "claims": [
  {
   "claim": "The cutting board is on the counter while Yuki chops vegetables before cooking",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "Yuki's plate is at the dining table during the weekday meal",
   "target": "plate_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Yuki's water bottle is at the dining table during the weekday meal",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The remote is at the side table during Yuki's evening TV",
   "target": "remote_shared",
   "expect": "side_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The pan is at the sink after cooking, during dishwashing",
   "target": "pan_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
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
    "days": "weekday",
    "from": 19.5,
    "to": 22,
    "at": "sink_k1",
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
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 22,
    "at": "sink_k1",
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
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 22,
    "at": "sink_k1",
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
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 22,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
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
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "plate_yuki": [
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
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 22.5,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
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
    "to": 22.5,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
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
    "to": 22.5,
    "at": "sink_k1",
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
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "side_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 21,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
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
  ],
  "laptop_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:toiletry_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "class:razor": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
