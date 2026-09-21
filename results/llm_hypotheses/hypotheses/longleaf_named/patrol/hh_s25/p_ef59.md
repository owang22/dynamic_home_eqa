# p_ef59 — Staggered starts; Marco is a 6 AM runner, Omar a 10 AM starter

Marco wakes at 5:45, showers, runs 6:15–7:15 (Tue/Thu/Sat), then starts work at 8:00. Omar sleeps in until 8:30, showers, and starts work at 9:30. They eat breakfast separately: Marco at 7:30, Omar at 9:00. Lunch is 12:30 for both, at the kitchen table, and they both go out on Wednesdays. In the evening Marco meditates 19:00–19:45, then they share dinner at 19:30. Omar reads on the armchair 21:30–22:30. On weekends Marco runs at 7:00, Omar reads 9:00–11:00, errands 12:00–14:00.

What sets this apart: on weekday mornings between 8:00 and 9:30, Marco's laptop is open at desk_b1 while Omar's laptop is still closed at desk_o1 or the charger is at the nightstand. Marco's running shoes are out of the house 6:15–7:15 on Tue/Thu. What would refute it: Omar's laptop in use (sighted at desk_o1 with charger plugged in) before 9:00 on a weekday, or Marco's running shoes at the shoe rack at 6:45 on a Tuesday.

```json
{
 "claims": [
  {
   "claim": "Marco's running shoes are out of the house during his Tuesday run",
   "target": "running_shoes_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 6.25,
   "to": 7.25
  },
  {
   "claim": "Omar's laptop is still at the desk but not in active use before 9:30 on weekdays",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 7,
   "to": 9.5
  },
  {
   "claim": "Marco's water bottle is out of the house during his morning run",
   "target": "water_bottle_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 6.25,
   "to": 7.25
  },
  {
   "claim": "The meditation cushion is on the bedroom floor during Marco's evening meditation on weekdays",
   "target": "meditation_cushion_marco",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 19,
   "to": 19.75
  }
 ],
 "targets": {
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
    "from": 8,
    "to": 17.5,
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
    "from": 9.5,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9.5,
    "at": "desk_o1",
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
    "from": 7.5,
    "to": 8,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
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
    "to": 9.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "almost_always"
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
    "days": "weekday",
    "from": 6.25,
    "to": 7.25,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 8,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6.25,
    "to": 7.25,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 8,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "desk_b1",
    "chance": "sometimes"
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
    "from": 6.25,
    "to": 7.25,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12.5,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
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
    "from": 12.5,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
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
    "from": 6.25,
    "to": 7.25,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12.5,
    "to": 14,
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
    "from": 12.5,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "from": 19,
    "to": 19.75,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "book_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 22.5,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 22.5,
    "at": "armchair_l1",
    "chance": "sometimes"
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
    "from": 7.5,
    "to": 8.25,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 9.75,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12.5,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.25,
    "to": 20.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12.5,
    "to": 14,
    "at": "kitchen_table_k1",
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
    "from": 12.5,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.25,
    "to": 20.5,
    "at": "kitchen_table_k1",
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
    "days": "weekday",
    "from": 21,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
    "from": 5.75,
    "to": 6.5,
    "at": "sink_ba_ba1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 9,
    "at": "sink_ba_ba1",
    "chance": "sometimes"
   }
  ],
  "razor_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 5.75,
    "to": 6.5,
    "at": "sink_ba_ba1",
    "chance": "almost_always"
   }
  ],
  "hair_dryer_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 9,
    "at": "sink_ba_ba1",
    "chance": "sometimes"
   }
  ]
 }
}
```
