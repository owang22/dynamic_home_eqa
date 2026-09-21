# p_c5d1 — Weekend cycling buddies; bike gear goes out on Saturday and Sunday mornings

Both Yuki and Omar cycle on weekends for exercise or errands. Their bike locks and helmets are at the entry on weekdays (stored there), but on Saturday and Sunday mornings (roughly 09:00–14:00) they go OUT_OF_HOUSE. On weekdays, Omar sometimes cycles to his shift (out with bike lock and helmet 13:00–23:00), while Yuki does not cycle to work (she takes transit). The entry is a bike-gear staging area. What sets this hypothesis apart: on weekend mornings, both bike locks and both helmets are simultaneously OUT_OF_HOUSE, which no weekday hypothesis predicts. What would refute it: bike_lock_yuki or helmet_yuki sighted at the entry on a Saturday or Sunday between 09:00 and 14:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's bike lock is out of the house on weekend mornings",
   "target": "bike_lock_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 9,
   "to": 14
  },
  {
   "claim": "Yuki's helmet is out of the house on weekend mornings",
   "target": "helmet_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 9,
   "to": 14
  },
  {
   "claim": "Omar's bike lock is out of the house on weekend mornings",
   "target": "bike_lock_omar",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 9,
   "to": 14
  },
  {
   "claim": "Yuki's bike lock is at the entry table on weekday afternoons",
   "target": "bike_lock_yuki",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 14,
   "to": 22
  }
 ],
 "targets": {
  "bike_lock_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "helmet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "bike_lock_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "helmet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
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
  "wallet_yuki": [
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
  "mug_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
