# p_9e2a — Yuki's water bottle: overnight rack, work absence, evening three-stop migration

Yuki's water bottle follows a strict daily arc that no single document in the library captures in full. Overnight (00:00–08:00) it dries at dish_rack_k1. At roughly 08:00 she grabs it and it leaves the house with her for the workday (08:00–17:30, OUT_OF_HOUSE). When she arrives home around 17:30–18:00, the bottle lands at entry_hook_e1 (the same hook as her jacket and backpack). During dinner (19:30–21:00) it migrates to the dining table, though the sightings show a near-even split between dining_table_d1 and sink_k1 at the 20:00 pass—she may set it down at the table and then rinse it at the sink before it goes back. By 22:00 it is back at dish_rack_k1 for the night.

This hypothesis is set apart from p_f9b3 (which places the bottle at the dining table at 20:00 with a "for 2, against 6" record, suggesting the table is not the dominant dinner-time spot) and from p_5e9b (which sends the bottle to the sink after the meal, "for 1, against 8"). The raw 20:00 sightings show dining_table_d1 ×2 and sink_k1 ×2—neither dominates, so this document gives both a "sometimes" chance and lets the robot's statistics break the tie.

Refutation: finding the water bottle at the dish rack between 09:00 and 17:00 on a weekday (it should be out of the house); finding it at the entry hook after 19:00 (it should have moved to the dining area); finding it at a receptacle other than dish_rack, entry_hook, dining_table, or sink_k1 at any hour.

```json
{
 "claims": [
  {
   "claim": "Yuki's water bottle is at the dish rack at 22:00 on a weekday after dinner",
   "target": "water_bottle_yuki",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Yuki's water bottle is at the entry hook at 18:00 on a weekday when she arrives home",
   "target": "water_bottle_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Yuki's water bottle is out of the house at 12:00 on a weekday",
   "target": "water_bottle_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 11,
   "to": 13
  },
  {
   "claim": "Yuki's water bottle is at the dish rack at 04:00 on a weekday overnight",
   "target": "water_bottle_yuki",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 2,
   "to": 6
  }
 ],
 "targets": {
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
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
    "from": 14,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "class:mug": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 18,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
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
    "days": "both",
    "from": 10,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
    "from": 20,
    "to": 22,
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
    "from": 20,
    "to": 22,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   }
  ],
  "class:kitchen_knife": [
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
    "to": 22,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "class:cutting_board": [
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
    "to": 22,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "class:spatula": [
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
    "to": 22,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "class:kettle": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "class:toaster": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "class:knife_block": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "class:wall_clock": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "class:fruit_bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "class:snack_bowl": [
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
    "chance": "sometimes"
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
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "class:blanket": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "class:book": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "class:journal": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bed_b1",
    "chance": "almost_always"
   }
  ],
  "class:pen": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "class:glasses": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "class:doormat": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "class:vacuum_cleaner": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "class:lamp": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "side_table_l1",
    "chance": "almost_always"
   }
  ],
  "class:plant_pot": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "side_table_l1",
    "chance": "almost_always"
   }
  ],
  "class:picture_frame": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "side_table_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
