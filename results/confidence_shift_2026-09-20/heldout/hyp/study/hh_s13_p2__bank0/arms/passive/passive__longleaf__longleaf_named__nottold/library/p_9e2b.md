# p_9e2b — The Three Meal Times: Kitchen Table at 8, 13, and 20

The mixture's worst-objects list is dominated by kitchen items predicted at sink_k1 but actually at kitchen_table_k1 or cupboard_k1. The clock-hour data reveals a clear three-meal rhythm that most documents in the library miss or only partially capture. Breakfast is at 8:00 (mug_priya at kitchen_table ×4, bowl_priya at kitchen_table ×4). Lunch is around 12–14 (bowl_priya at kitchen_table, glass_priya at kitchen_table ×2). Dinner is at 20:00 (glass_priya at kitchen_table ×4, glass_hana at kitchen_table ×4, water_bottle_hana at kitchen_table ×4, plate_hana at kitchen_table ×4). Between meals the objects are in the sink or cupboard. At 22:00 the mugs and snack bowl migrate to the coffee table for the TV session.

What sets this apart: at 13:00 on a weekday, bowl_priya is at kitchen_table_k1 (not sink_k1), and glass_priya is at kitchen_table_k1 (not sink_k1). At 22:00, mug_hana is at coffee_table_l1 (not sink_k1 or cupboard_k1). What would refute it: bowl_priya at sink_k1 at 13:00 on a weekday, or mug_hana at sink_k1 at 22:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Priya's bowl is at the kitchen table at 13:00 on a weekday (lunch)",
   "target": "bowl_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 15
  },
  {
   "claim": "Priya's glass is at the kitchen table at 20:00 on a weekday (dinner)",
   "target": "glass_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Hana's mug is at the coffee table at 22:00 on a weekday (TV time)",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21.5,
   "to": 23
  },
  {
   "claim": "Priya's mug is at the kitchen table at 08:00 on a weekday (breakfast)",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 9
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
    "days": "both",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 12,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 15,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 15,
    "to": 19,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
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
    "days": "both",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 13,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13,
    "to": 15,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 15,
    "to": 19,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "glass_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 19,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 9.5,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
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
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 12,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 14,
    "to": 20,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
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
    "to": 16,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
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
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
