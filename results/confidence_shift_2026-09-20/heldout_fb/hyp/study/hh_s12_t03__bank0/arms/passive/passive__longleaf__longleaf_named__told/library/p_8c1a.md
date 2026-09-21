# p_8c1a — Priya's afternoon anchor: vacuum 16–17, mug at kitchen table, bag at counter

This document focuses on Priya's midday-to-afternoon routine, which the existing library under-specifies. The evidence shows the vacuum cleaner at floor_l_l1 at 16:00 and 17:00 (with entry_floor at 18:00), confirming a living-room vacuum session 16:00–17:30 on weekdays. Priya's mug is at kitchen_table_k1 at 07:00 and 08:00 (morning tea/coffee at the kitchen table), then appears at coffee_table_l1 at 14:00, 20:00, and 21:00 (afternoon and evening drinks at the living room). The shopping bag sits at counter_k1 from 12:00 to 15:00 (7 sightings in that window), suggesting Priya keeps her reusable bag at the kitchen counter during her afternoon errand window (14:00–16:00). Her glasses are at the coffee table 15:00–22:00 (sightings at 15, 16, 20, 21, 22). The yoga mat stays in the wardrobe all day on weekdays (4 empty looks at wardrobe during 9–17h, no floor sightings).

What sets this apart: the vacuum is specifically at floor_l_l1 16–17:30 on weekdays, the shopping bag is at the counter 12–15, and Priya's mug is at the kitchen table in the morning. What would refute it: the vacuum at entry_floor at 16:30, or the shopping bag at the pantry shelf at 13:00.

```json
{
 "claims": [
  {
   "claim": "The vacuum is on the living-room floor during Priya's afternoon cleaning",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 16,
   "to": 17.5
  },
  {
   "claim": "Priya's mug is at the kitchen table in the morning",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 7,
   "to": 9
  },
  {
   "claim": "The shopping bag is at the kitchen counter during Priya's errand window",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 12,
   "to": 15
  },
  {
   "claim": "Priya's glasses are at the coffee table in the late afternoon",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 15,
   "to": 22
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 17.5,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
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
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "coffee_table_l1",
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
    "days": "weekday",
    "from": 12,
    "to": 15.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "backpack_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "helmet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "bike_lock_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
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
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
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
    "from": 12,
    "to": 13.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "class:water_bottle": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
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
    "from": 14,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
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
   },
   {
    "days": "both",
    "from": 13,
    "to": 15,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
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
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
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
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "kettle_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "class:plant_pot": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "side_table_l1",
    "chance": "usually"
   }
  ],
  "plant_pot_3_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 7.5,
    "at": "sink_ba_ba1",
    "chance": "usually"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "class:book": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "class:cushion": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "cushion_2_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "board_game_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "lamp_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "side_table_l1",
    "chance": "usually"
   }
  ],
  "doormat_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "vase_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "almost_always"
   }
  ],
  "iron_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   }
  ]
 }
}
```
