# p_9c3d — Weekday Evening Settle: By 18:00 the Kitchen Is Put Away and the Remote Is on the TV Stand

On weekdays, Hana leaves for her afternoon-to-night shift at about 13:40 and does not return until 23:00. The 16:00 and 18:00 robot passes therefore capture Priya alone in the house, winding down from her afternoon errands and preparing the evening. Between 16:00 and 18:00 the kitchen is systematically put away: the cutting board moves from the sink to the counter, the knife and spatula go back into the drawer, the pan and pot are shelved in the cupboard, Priya's plate goes from the sink into the cupboard, and the dog food bag is stored on the pantry shelf. In the living room, the blanket migrates from the armchair to the coffee table, the remote settles onto the TV stand, and Priya's book and magazine end up on the coffee table. Priya's water bottle moves from the dining table to the coffee table. By 18:00 the house is in its "evening rest" configuration, waiting for Hana to come home.

What sets this document apart: it specifically predicts the **18:00 weekday** positions, which differ from both the morning resting spots and the mid-afternoon transition spots. The blanket is on the **coffee_table_l1** (not the armchair where it sits at 08:00, and not the couch where it sometimes appears at 16:00). The remote is on the **tv_stand_l1** (not the floor where it sits at 08:00). The dog food bag is on the **pantry_shelf_k1** (not the kitchen floor where it sits at 08:00). Priya's plate is in the **cupboard_k1** (not the dining table or sink). The cutting board is on the **counter_k1** (not the sink). The kitchen knife and spatula are in the **drawer_k_k1** (not the sink or counter).

This document is refuted if, at 18:00 on a weekday, the remote is on the floor, the blanket is on the armchair, the dog food bag is on the kitchen floor, or the cutting board is still at the sink.

```json
{
 "claims": [
  {
   "claim": "The remote is on the TV stand at 18:00 on a weekday, not on the floor",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The shared blanket is on the coffee table at 18:00 on a weekday, not on the armchair",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The dog food bag is on the pantry shelf at 18:00 on a weekday, not on the kitchen floor",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Priya's plate is in the cupboard at 18:00 on a weekday, not on the dining table",
   "target": "plate_priya",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 15,
    "at": "floor_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
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
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
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
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 16,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_priya": [
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
    "to": 17,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "book_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "magazine_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "tablet_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "bowl_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "cupboard_k1",
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
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 15,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "floor_l_l1",
    "chance": "rarely"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   }
  ],
  "class:skincare": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "class:bowl": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "class:plant_pot": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "side_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
