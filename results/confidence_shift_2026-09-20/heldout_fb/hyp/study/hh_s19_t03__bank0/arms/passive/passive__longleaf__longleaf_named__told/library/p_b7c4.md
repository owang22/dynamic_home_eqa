# p_b7c4 — The 21:00 ironing: bedroom 2 becomes a workshop

No existing document accounts for the iron and ironing board appearing at bed_b2 at 21:00 (iron sighted there 3 times, board 2 times). The storage locations (storage_shelf_s1, storage_floor_s1) hold them from 03:00 through 18:00, but by 21:00 both have been moved to bedroom 2. This is a dedicated evening ironing session, most likely done by Marco (who is home by 17:30 and has free time after dinner) while Omar is in the other bedroom or the living room.

What sets this hypothesis apart: between 20:30 and 22:00, the iron is at bed_b2 (on or beside the bed, used as an ironing surface) and the ironing board is set up at bed_b2. The rest of the house runs its normal evening routine (TV in the living room, Omar on the couch or in his bedroom). The iron returns to storage by 23:00.

What would refute it: iron or ironing board sighted at storage_shelf_s1 or storage_floor_s1 at 21:00 on a weekday; or the iron at bed_b1 instead of bed_b2.

```json
{
 "claims": [
  {
   "claim": "The iron is at bed_b2 during the 21:00 ironing session",
   "target": "iron_shared",
   "expect": "bed_b2",
   "days": "weekday",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "The ironing board is set up at bed_b2 during the evening ironing",
   "target": "ironing_board_shared",
   "expect": "bed_b2",
   "days": "weekday",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "Omar's laptop is on the coffee table during the ironing window (he is not at his desk)",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The iron is in storage at 09:00 (not yet in use)",
   "target": "iron_shared",
   "expect": "storage_shelf_s1",
   "days": "both",
   "from": 9,
   "to": 10
  }
 ],
 "targets": {
  "iron_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22,
    "at": "bed_b2",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 20.5,
    "to": 22,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22,
    "at": "bed_b2",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 20.5,
    "to": 22,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ],
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 11,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 22.5,
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
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 17,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
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
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
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
    "from": 18,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "class:glass": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
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
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
