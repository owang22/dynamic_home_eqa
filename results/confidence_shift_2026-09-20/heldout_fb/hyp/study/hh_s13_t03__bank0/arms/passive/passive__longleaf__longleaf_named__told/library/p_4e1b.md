# p_4e1b — Priya's Midday: Shopping Bag on Counter, Vacuum in the Living Room

Priya is home all day on weekdays. Her midday (12:00–14:00) is when she unpacks errands: the shopping bag appears on the kitchen counter at 12:00 and 13:00 (five and three sightings respectively), then goes back to the pantry by 18:00. Her plate is on the kitchen table from 13:00 onward (lunch, then dinner prep). Her glass stays at her nightstand in bedroom-b2 during the midday (she drinks from it at her desk or bed, not in the kitchen).

The vacuum cleaner is in storage at 09:00 and 14:00 but is on the living room floor (floor_l_l1) at 15:00 — Priya vacuums the living room in the mid-afternoon. By 18:00 it is back in storage. This is a regular weekday chore.

This document is distinct from all existing ones: no current document places the shopping bag on the counter at midday, or the vacuum on the living room floor at 15:00, or Priya's glass at the nightstand during midday hours.

What would refute this: the shopping bag in the pantry at 12:00, the vacuum in storage at 15:00, or Priya's glass in the kitchen at 13:00.

```json
{
 "claims": [
  {
   "claim": "The shopping bag is on the kitchen counter at 12:30 on a weekday (Priya just returned from errands)",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "The vacuum cleaner is on the living room floor at 15:30 on a weekday (Priya is vacuuming)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 15,
   "to": 16
  },
  {
   "claim": "Priya's glass is on her nightstand at 13:00 on a weekday (she drinks at her bedside, not in the kitchen)",
   "target": "glass_priya",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 12,
   "to": 15
  },
  {
   "claim": "The vacuum cleaner is back in storage at 18:00 on a weekday (chore finished)",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Priya's plate is on the kitchen table at 13:00 on a weekday (lunch in progress)",
   "target": "plate_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 13,
   "to": 15
  }
 ],
 "targets": {
  "shopping_bag_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 15,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 16,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
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
  "plate_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 18,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
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
    "from": 9,
    "to": 18,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
  "keys_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 11,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
