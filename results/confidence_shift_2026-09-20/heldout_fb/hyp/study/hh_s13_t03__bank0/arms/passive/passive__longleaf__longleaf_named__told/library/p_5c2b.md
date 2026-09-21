# p_5c2b — Post-Dinner Sink: The 03:00 Kitchen Reset

The 03:00 patrol pass reveals a consistent overnight kitchen state. Dishes that were at the kitchen table during dinner (18–20h) have been washed and are sitting in the sink: bowl_priya at sink_k1, plate_hana at sink_k1, snack_bowl at sink_k1, and water_bottle_hana at sink_k1. Clean glasses are put away to the pantry (glass_hana at pantry_shelf_k1) or the cupboard. Mugs go to the pantry (mug_priya at pantry_shelf_k1) or the cupboard (mug_hana at cupboard_k1). The recipe book is left on the counter (used during meal prep, not put back in the pantry). The spatula is in the dish_rack.

This is the "next morning before anyone is up" state. The kitchen counter is mostly clear. The sink holds the night's dirty dishes. The pantry and cupboards hold the clean items. Nothing is on the coffee table yet (the evening migration items have been cleared back).

What sets this apart: at 03:00 on a weekday, bowl_priya is at sink_k1 (not cupboard_k1), plate_hana is at sink_k1 (not cupboard_k1), snack_bowl is at sink_k1 (not counter_k1), glass_hana is at pantry_shelf_k1 (not counter_k1), and mug_priya is at pantry_shelf_k1 (not kitchen_table_k1). The kitchen counter is NOT the overnight resting spot for these items.

What would refute it: bowl_priya at cupboard_k1 at 03:00 on a weekday, or snack_bowl at counter_k1 at 03:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Priya's bowl is in the kitchen sink at 03:00 on a weekday (washed after dinner, left to dry)",
   "target": "bowl_priya",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 0,
   "to": 6
  },
  {
   "claim": "The snack bowl is in the kitchen sink at 03:00 on a weekday (washed after the evening)",
   "target": "snack_bowl_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Hana's glass is on the pantry shelf at 03:00 on a weekday (put away after being used at the counter)",
   "target": "glass_hana",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Priya's mug is on the pantry shelf at 03:00 on a weekday (put away after morning tea)",
   "target": "mug_priya",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 0,
   "to": 6
  }
 ],
 "targets": {
  "bowl_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "bowl_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "plate_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
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
    "from": 0,
    "to": 6,
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
  "glass_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "pantry_shelf_k1",
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
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
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
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "sink_k1",
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
    "from": 0,
    "to": 6,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
