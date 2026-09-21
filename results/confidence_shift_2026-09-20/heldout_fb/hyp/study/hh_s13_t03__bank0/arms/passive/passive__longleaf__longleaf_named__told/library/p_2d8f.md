# p_2d8f — Evening Migration: Kitchen to Coffee Table by 21

After dinner ends around 21:00, the household shifts from the kitchen to the living room for TV. Mugs, glasses, and the snack bowl migrate from their kitchen locations to the coffee table and couch area. The blanket is already on the couch; the remote is at the TV stand. By 22:00 the kitchen is mostly cleared: mugs go to the sink or pantry, glasses go back to the cupboard or nightstand. The snack bowl is the last to arrive at the coffee table (21:00) and the last to leave (washed in the sink by 03:00).

This document differs from the snack-bowl-only forks by covering the full migration: mug_hana goes from kitchen_table (18:00) to coffee_table (20:00–21:00); glass_hana goes from counter (18:00–19:00) to counter/kitchen_table (20:00); glass_priya goes from sink (18:00) to cupboard/kitchen_table (19:00) to coffee_table (20:00) to nightstand (22:00); mug_priya goes from sink (18:00) to cupboard/coffee_table (21:00).

What would refute this: a mug or glass still on the kitchen table at 21:00, or the snack bowl still on the counter at 21:30.

```json
{
 "claims": [
  {
   "claim": "Hana's mug is on the coffee table at 20:30 on a weekday during the evening TV session",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the kitchen counter at 19:00 on a weekday (dinner just finished, not yet moved to living room)",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "Priya's glass is back on her nightstand at 22:30 on a weekday (TV winding down)",
   "target": "glass_priya",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The snack bowl is on the coffee table at 21:30 on a weekday (TV session in full swing)",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Hana's glass is on the kitchen counter at 18:30 on a weekday (drinking during early evening)",
   "target": "glass_hana",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  }
 ],
 "targets": {
  "mug_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
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
  "mug_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "pantry_shelf_k1",
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
    "to": 21,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "glass_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "sink_k1",
    "chance": "sometimes"
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
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "coasters_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
