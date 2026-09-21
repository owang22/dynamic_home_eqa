# p_a4e2 — Both drive on weekdays; cycling gear stays home all day (fork of p_3f8a)

This is a fork of p_3f8a with one targeted correction. The parent document claimed Yuki's keys land on the entry floor (entry_floor_e1) when she returns at 17:30. Nine consecutive looks in the 18–19 h window found the keys at entry_table_e1 instead (the per-object evidence shows entry_table_e1 as the dominant resting spot, 2/4 sighted days, and the hourly sightings at 20:00 and 22:00 show entry_table_e1 x2 versus entry_floor_e1 x1). The keys are set down on the small entry table, not dropped on the floor. Everything else in the parent—helmets and bike locks at the entry all day, Yuki's carry-kit out 08:00–17:30, Omar's carry-kit out 13:40–23:00—remains unchanged and is strongly supported by the 12/12 empty looks during work hours.

What changed: the keys_yuki claim now expects entry_table_e1; a new target block places keys_yuki at entry_table_e1 for the evening hours (17.5–24) on weekdays. The prose refutation is unchanged.

```json
{
 "claims": [
  {
   "claim": "Yuki's helmet is at the entry hook on a weekday at 14:00 while she is at work",
   "target": "helmet_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Omar's bike lock is at the entry table on a weekday at 16:00 while he is at work",
   "target": "bike_lock_omar",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Yuki's laptop is out of the house on a weekday at 12:00",
   "target": "laptop_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 11,
   "to": 13
  },
  {
   "claim": "Omar's handbag is out of the house on a weekday at 18:00",
   "target": "handbag_omar",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Yuki's keys are at the entry table on a weekday at 20:00 after she returns home",
   "target": "keys_yuki",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 19,
   "to": 21
  }
 ],
 "targets": {
  "helmet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "helmet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "keys_yuki": [
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
  "laptop_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "notebook_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "backpack_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "sunglasses_yuki": [
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
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "shoes_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "handbag_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "lunchbox_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "notebook_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "pen_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "scarf_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "shoes_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
