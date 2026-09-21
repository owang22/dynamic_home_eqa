# p_3e8b — The 20:00 Living Room Takeover: A Coordinated Evening Shift

At 20:00 on weekdays the living room becomes the evening hub in a coordinated shift that happens within roughly a 30-minute window. The blanket moves from the couch (where it sits all day: 03:00×4, 08:00×1, 09:00×5, 15:00×1, 18:00×2) to the coffee table (20:00×1, 21:00×2, 22:00×1). The remote moves from the TV stand (03:00×4, 18:00×1) to the coffee table (20:00×2, 21:00×2). The snack bowl moves from the kitchen counter (17:00×2, 18:00×1, 19:00×3) to the coffee table (20:00×2, 21:00×4). Priya's mug moves from the kitchen table (15:00×3) to the coffee table (20:00×1, 21:00×1, 22:00×3). Hana's mug follows the same path (18:00 kitchen_table×1 → 20:00 coffee_table×1, 21:00×2).

On weekends the shift is less sharp: the blanket splits between armchair and coffee table from 18:00 onward, the remote is on the coffee table at 20:00 (4 sightings) but also on the TV stand and armchair at 21:00, and the snack bowl appears at the coffee table at 21:00 (1 sighting) alongside the sink (1 sighting).

This document sets itself apart by placing the snack bowl at the kitchen counter at 19:00 (not yet migrated) and the blanket on the couch at 18:00 (not yet migrated). What would refute it: seeing the blanket still on the couch at 21:00, the remote at the TV stand at 21:00, or the snack bowl at the counter at 20:30.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the couch at 18:00 on a weekday before the evening TV session begins",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 17,
   "to": 19.5
  },
  {
   "claim": "The remote is at the TV stand at 18:00 on a weekday before the evening TV session begins",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 17,
   "to": 19.5
  },
  {
   "claim": "The snack bowl is on the kitchen counter at 19:00 on a weekday before it is carried to the living room",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The blanket is on the coffee table at 21:00 on a weekday during the TV session",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20.5,
   "to": 22
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 20,
    "at": "couch_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 22,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 20,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "mug_priya": [
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
    "to": 14,
    "at": "cupboard_k1",
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
    "to": 20,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
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
   }
  ]
 }
}
```
