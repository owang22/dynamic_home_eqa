# p_1e2f — Yuki's weekend errands: she takes keys, wallet, water bottle, and backpack midday

On weekends, Yuki sleeps in until about 10:00, then goes out for errands (11:00–14:00). She takes her keys, wallet, water bottle, and backpack. Her sunglasses go too (sunny errands). Her laptop and notebook stay home. Omar is home on weekends, doing his own errands around midday (taking bike lock, helmet, and possibly tablet). What sets this hypothesis apart: on weekend midday, Yuki's keys and wallet are OUT_OF_HOUSE, and Omar's bike lock is also OUT_OF_HOUSE (both out simultaneously). What would refute it: keys_yuki sighted at entry_floor_e1 on a Saturday between 11:00 and 14:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's keys are out of the house on Saturday midday",
   "target": "keys_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 11,
   "to": 14
  },
  {
   "claim": "Yuki's wallet is out of the house on Saturday midday",
   "target": "wallet_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 11,
   "to": 14
  },
  {
   "claim": "Omar's bike lock is out of the house on Saturday midday",
   "target": "bike_lock_omar",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 11,
   "to": 14
  },
  {
   "claim": "Yuki's laptop is at the entry hook on Saturday midday",
   "target": "laptop_yuki",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 11,
   "to": 14
  }
 ],
 "targets": {
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
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
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
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "backpack_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "sunglasses_yuki": [
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
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
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
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
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
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "laptop_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "notebook_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ]
 }
}
```
