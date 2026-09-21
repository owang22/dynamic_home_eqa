# p_5c6a — The Remote on the Floor by Day, the TV Stand by Evening

The remote_shared sightings reveal a pattern that most documents in the library miss. From 00:00 through 16:00 the remote is on floor_l_l1 (x2) with a single sighting at tv_stand_l1 (x1) — it lives on the living-room floor during the day, probably dropped after a quick channel change or used while sitting on the couch. At 18:00 and 20:00 the balance flips: tv_stand_l1 x3, floor_l_l1 x1. Someone picks it up and sets it on the TV stand for the evening. At 22:00 it splits three ways (tv_stand_l1 x2, coffee_table_l1 x1, floor_l_l1 x1), reflecting the end-of-evening shuffle when it gets passed around the couch.

This document models that two-phase pattern: floor_l_l1 as the daytime resting spot, tv_stand_l1 from 18:00 onward, and a small chance of coffee_table_l1 in the last hour. It pairs the remote with the blanket (armchair_l1 by day, coffee_table_l1 by evening) and the snack bowl (counter_k1 by day, coffee_table_l1 by evening) to capture the full "evening TV set" that moves from its daytime positions to the coffee table around 20:00–22:00.

The document also places the serving_dish and the shared plates in their kitchen/dining cycle: cupboard_k1 or sink_k1 by day, dining_table_d1 during the 19:00–21:00 dinner window. The kitchen knife and cutting board follow the same rhythm: sink_k1 by day, counter_k1 during the 18:00–20:00 cooking window.

What would refute this: the remote on the TV stand at 10:00 or 14:00 (it should be on the floor); the blanket on the coffee table before 20:00; the serving dish at the dining table at 12:00 (no dinner yet).

```json
{
 "claims": [
  {
   "claim": "The remote is on the living room floor during the mid-morning, not on the TV stand",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "both",
   "from": 10,
   "to": 16
  },
  {
   "claim": "The remote is on the TV stand during the early-evening cooking window",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 18,
   "to": 21
  },
  {
   "claim": "The blanket is on the armchair during the afternoon, not on the coffee table",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "both",
   "from": 14,
   "to": 19
  },
  {
   "claim": "The serving dish is in the cupboard before dinner is being set",
   "target": "serving_dish_shared",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 12,
   "to": 17
  },
  {
   "claim": "The kitchen knife is in the drawer during the mid-afternoon",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "both",
   "from": 13,
   "to": 17
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "class:plate": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 9,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 9,
    "to": 13,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13,
    "to": 14,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 14,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
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
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 18,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 18,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
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
  ]
 }
}
```
