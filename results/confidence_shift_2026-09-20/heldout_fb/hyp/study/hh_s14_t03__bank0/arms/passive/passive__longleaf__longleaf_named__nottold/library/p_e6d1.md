# p_e6d1 — Evening TV prep: serving dish to the table, then snacks to the coffee table

The serving_dish_shared and snack_bowl_shared sightings reveal a two-stage evening preparation. The serving dish leaves the cupboard after dinner (18:00) and appears at kitchen_table_k1 at 20:00 (2 sightings), then moves to coffee_table_l1 by 21:00 (2 sightings) where it stays through 23:00 (1 sighting). The snack bowl stays in the cupboard through 18:00, appears at counter_k1 at 22:00 (3 sightings—being filled with snacks), and then shows up at coffee_table_l1 at 23:00 (1 sighting) alongside the serving dish.

What sets this apart: the serving dish has a distinct intermediate stop at kitchen_table_k1 (20:00–21:00) before reaching the coffee table, while the snack bowl goes directly from cupboard to counter (being filled) to coffee table (23:00). The two objects arrive at the coffee table at different times: serving dish at 21:00, snack bowl at 23:00. This is not a single "TV time" dump but a gradual evening setup.

What would refute this: the serving dish at coffee_table_l1 at 19:00 (too early; it should still be at the kitchen table or cupboard); the snack bowl at coffee_table_l1 at 20:00 (it should still be in the cupboard); the serving dish at cupboard_k1 at 22:00 (it should already be at the coffee table).

```json
{
 "claims": [
  {
   "claim": "The serving dish is on the kitchen table just after dinner before moving to the living room",
   "target": "serving_dish_shared",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 20,
   "to": 21
  },
  {
   "claim": "The serving dish is on the coffee table during the evening TV period",
   "target": "serving_dish_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 24
  },
  {
   "claim": "The snack bowl is on the kitchen counter being filled for evening snacks",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The snack bowl is on the coffee table during late-evening TV",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 23,
   "to": 24
  }
 ],
 "targets": {
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
    "from": 20,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "coffee_table_l1",
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
    "from": 20,
    "to": 23.5,
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
  "class:candle": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:tissue_box": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
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
  "class:cutting_board": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
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
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
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
    "days": "both",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
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
  "class:keys": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "class:wallet": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "class:scarf": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:shoes": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ]
 }
}
```
