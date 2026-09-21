# p_a61d — p_g7h8 — Block work with coffee breaks; mugs cycle to the counter

Both residents work in blocks: 9:00–11:30, break 11:30–12:00, 12:00–14:30, lunch 14:30–15:15 (at home, kitchen table), 15:15–17:30. During breaks they go to the kitchen, and mugs are at the counter. On weekdays the mugs are at the counter 11:30–12:00 and 14:30–15:15. They eat a light lunch at the kitchen table 14:30–15:15. Evening: shared TV 20:00–22:00, then Omar reads, Marco meditates. Weekend: sleep in till 10, errands 12–14 (one or both out), Marco runs Sat 7:00.

What sets this apart: mugs are at the counter (not the desk) during the 11:30–12:00 and 14:30–15:15 windows on weekdays. The kitchen table is in use at 14:30, not 12:30. What would refute it: mugs at the desk at 11:45 on a weekday, or the kitchen table empty at 14:45.

```json
{
 "claims": [
  {
   "claim": "Marco's mug is at the counter during his mid-morning break on weekdays",
   "target": "mug_marco",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 11.5,
   "to": 12
  },
  {
   "claim": "Omar's mug is at the counter during the lunch break on weekdays",
   "target": "mug_omar",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 14.5,
   "to": 15.25
  },
  {
   "claim": "Plates are at the kitchen table during the 14:30 lunch on weekdays",
   "target": "plate_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 14.5,
   "to": 15.25
  },
  {
   "claim": "The remote is on the coffee table during evening TV",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
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
    "to": 11.5,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 12,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14.5,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14.5,
    "to": 15.25,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 15.25,
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
    "to": 11.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 12,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14.5,
    "to": 15.25,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 15.25,
    "to": 17.5,
    "at": "desk_o1",
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
    "days": "weekday",
    "from": 14.5,
    "to": 15.25,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
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
    "from": 14.5,
    "to": 15.25,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
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
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 22,
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
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "snack_bowl_shared": [
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
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
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
    "days": "weekend",
    "from": 12,
    "to": 14,
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
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "from": 22.25,
    "to": 23,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
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
    "days": "weekday",
    "from": 22.25,
    "to": 23,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
