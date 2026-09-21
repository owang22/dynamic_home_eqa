# p_f6a3 — Cooking 18:30–20:00: pot on stove, recipe book on counter at the edges

The pot is in the cupboard at 17:00 (×2) and 18:00 (×2) on weekdays. It appears on the counter at 19:00 (×1) and is in the pantry at 20:00 (×1). The recipe book is on the counter at 17:00 (×1, checking recipes before starting) and 19:00 (×1, actively cooking), but in the pantry at 18:00 (×1). The cutting board is on the counter at 18:00 and 19:00. The pan is in the cupboard at 18:00 (×1) and on the counter at 18:00 (×1).

This means: cooking begins around 18:30 when the pot is taken from the cupboard to the stove. The pot is on the stove (invisible to the robot, not at any listed receptacle) from 18:30 to about 19:30. It is briefly set on the counter at 19:00 (perhaps to check the contents). By 20:00 it is put away in the pantry. The recipe book is consulted at 17:00 (planning) and again at 19:00 (mid-cook reference), returning to the pantry between.

What sets this apart from p_4f8a (cooking 17–19:30) and p_5f2b (cooking 17–18): the pot is NOT on the counter at 17:00 or 18:00; it is in the cupboard. The cooking window is 18:30–20:00, not 17:00–19:00. The recipe book's 17:00 counter sighting is pre-planning, not active cooking.

Refutation: if the pot is on the counter at 17:00 or 18:00 on a weekday (it would mean cooking started earlier), or if the recipe book is on the counter at 18:00 (it is in the pantry at that pass).

```json
{
 "claims": [
  {
   "claim": "The pot is in the cupboard at 18:00 on a weekday",
   "target": "pot_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 18.5
  },
  {
   "claim": "The recipe book is on the kitchen counter at 19:00 on a weekday",
   "target": "recipe_book_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The pot is in the pantry at 20:00 on a weekday",
   "target": "pot_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 19.5,
   "to": 20.5
  },
  {
   "claim": "The cutting board is on the kitchen counter at 19:00 on a weekday",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
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
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
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
    "days": "weekday",
    "from": 17,
    "to": 17.5,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 23,
    "at": "counter_k1",
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
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22.5,
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
    "days": "weekend",
    "from": 3,
    "to": 6,
    "at": "cupboard_k1",
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
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "knife_block_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
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
  "toaster_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
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
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 3,
    "to": 6,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
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
  "mixing_bowl_shared": [
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
  ]
 }
}
```
