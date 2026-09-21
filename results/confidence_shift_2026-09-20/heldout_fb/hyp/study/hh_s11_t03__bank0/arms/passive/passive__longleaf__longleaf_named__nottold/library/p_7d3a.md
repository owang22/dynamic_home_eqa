# p_7d3a — The Couch-First Blanket; Daytime Rest on the Couch, Armchair After 23:00

The blanket's resting place is the couch, not the coffee table. Across four days of sightings the blanket appears on couch_l1 at 07:00, 16:00, 17:00, and 19:00 (four sightings), on coffee_table_l1 at 14:00, 17:00, and 18:00 (three sightings), and on armchair_l1 at 03:00 (two sightings). The couch is the dominant daytime location: the blanket is draped over the couch while residents are in the living room during the day, and it shifts to the coffee table only in the mid-afternoon (14:00–18:00) when someone is settling in for a longer sit. After 23:00, when Hana comes home from her shift and settles into the armchair for late-night TV, the blanket moves to the armchair.

What sets this apart from the other documents: the default resting place for blanket_shared is couch_l1 (not coffee_table_l1 as most other documents assume), and the armchair_l1 block covers the 23:00–04:00 window. What would refute it: the blanket sighted on the coffee table at 07:00 or 19:00 on a weekday, or never sighted on the couch at any hour.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the couch during the weekday afternoon",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 16,
   "to": 19
  },
  {
   "claim": "The blanket is on the armchair in the early morning after Hana's shift",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekday",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The blanket is on the coffee table during the mid-afternoon",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 14,
   "to": 17
  }
 ],
 "targets": {
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
    "from": 14,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 5,
    "at": "armchair_l1",
    "chance": "usually"
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
    "from": 19,
    "to": 22,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 2,
    "to": 5,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "class:snack_bowl": [
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
    "to": 23,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 4,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "camera_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "almost_always"
   }
  ],
  "notebook_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "tablet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 12,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "class:dog_bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "class:dog_food_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "class:dog_leash": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
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
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
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
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
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
    "days": "both",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19.5,
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
    "from": 12,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
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
    "from": 12,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
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
    "from": 12,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
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
  "class:kettle": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "class:watering_can": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "balcony_floor_y1",
    "chance": "usually"
   }
  ],
  "class:vacuum_cleaner": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   }
  ],
  "class:duster": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "almost_always"
   }
  ]
 }
}
```
