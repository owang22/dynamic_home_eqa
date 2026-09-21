# p_4cd4 — Both out for lunch; the kitchen is cold at midday

On weekdays both residents leave the house for lunch 12:00–14:00, taking keys, wallets, jackets, and (for Marco) his running shoes on Tue/Thu. Their laptops stay at the desks, chargers remain plugged in. They return at 14:00 and resume work until 17:30. Dinner is at 18:30 at the dining table (not the kitchen table). On weekends they sleep in until 10:30, one goes to errands 12:00–13:30 while the other stays home, and they eat a late lunch together at 13:30. Marco runs Sat mornings 7:00–8:00. No shared TV; they each wind down separately.

What sets this apart: the kitchen is completely empty of people and in-use items between 12:00 and 14:00 on weekdays; the dining table (not kitchen table) holds plates at dinner. What would refute it: either resident sighted in the kitchen between 12:00 and 14:00 on a weekday, or plates at the kitchen table at 18:30.

```json
{
 "claims": [
  {
   "claim": "Both residents are out of the house for lunch on weekdays",
   "target": "keys_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Omar's keys are also out during the lunch window",
   "target": "keys_omar",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Plates are at the dining table for dinner, not the kitchen table",
   "target": "plate_marco",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The laptop remains at Marco's desk even while he is out for lunch",
   "target": "laptop_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 12,
   "to": 14
  }
 ],
 "targets": {
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
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 13.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "keys_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 13.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "jacket_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 13.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "jacket_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 13.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "wallet_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
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
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "desk_o1",
    "chance": "almost_always"
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
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13.5,
    "to": 14.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
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
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "mug_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17.5,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "mug_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "running_shoes_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 8,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "meditation_cushion_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 20.25,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6.5,
    "to": 7.5,
    "at": "sink_ba_ba1",
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
    "days": "weekday",
    "from": 18,
    "to": 18.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
