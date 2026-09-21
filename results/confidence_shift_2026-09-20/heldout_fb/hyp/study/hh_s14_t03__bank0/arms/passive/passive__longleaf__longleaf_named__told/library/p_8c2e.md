# p_8c2e — Sick Day Afternoon: Both Home, Kitchen and Living Room Active

With Marco home sick and Yuki skipping her afternoon errand, both residents are in the house from roughly 13:00 to 23:00. The kitchen table sees an afternoon snack or early dinner; the living room sees the blanket pulled over the bed or couch, the remote at the TV stand, and the snack bowl migrated to the coffee table for the evening. Marco's water bottle is at the coffee table or kitchen table rather than out with him at work. The dog food bag sits on the pantry shelf between the morning and evening feedings. The board game may be brought out from the bookshelf for the evening.

This document differs from the standard split (where Marco is out 13:40–23:00 and the living room is quiet in the afternoon) by predicting active occupancy of both the kitchen and living room with both residents present. It also predicts the snack bowl on the coffee table in the evening (21–23 h), where the standard split has it at the counter.

This document is refuted if Marco is sighted OUT_OF_HOUSE during 14–18 h, or if the blanket is sighted at the couch during 14–18 h (rather than the bed), or if the snack bowl is at the counter at 22:00.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the bed during Marco's afternoon rest",
   "target": "blanket_shared",
   "expect": "bed_b1",
   "days": "weekday",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Marco's water bottle is at the coffee table in the afternoon while he rests",
   "target": "water_bottle_marco",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The snack bowl is on the coffee table during the evening with both residents home",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The dog food bag is on the pantry shelf at midday between feedings",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 12,
   "to": 14
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 13,
    "to": 19,
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 2,
    "to": 5,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
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
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "board_game_shared": [
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "class:glass": [
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "class:plate": [
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
