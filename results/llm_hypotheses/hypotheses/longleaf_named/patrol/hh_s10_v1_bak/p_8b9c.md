# p_8b9c — The entry hook is a permanent storage spot; Yuki's items are always there

The entry hook is where Yuki stores her backpack, water bottle, laptop, notebook, and jacket permanently. She does NOT take the laptop, notebook, or water bottle to work (she uses a work laptop and a work water bottle). Only her keys and wallet leave the house on weekdays. The backpack stays (it holds her work bag but she has a separate work bag). What sets this hypothesis apart: laptop_yuki, notebook_yuki, and water_bottle_yuki are ALWAYS at the entry hook, even during weekday work hours. This is a middle ground between p_09c6 (nothing travels) and p_a3f7 (everything travels). What would refute it: laptop_yuki or water_bottle_yuki sighted OUT_OF_HOUSE on any day.

```json
{
 "claims": [
  {
   "claim": "Yuki's laptop is at the entry hook on a Wednesday at noon",
   "target": "laptop_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 11,
   "to": 14
  },
  {
   "claim": "Yuki's water bottle is at the entry hook on a Thursday at noon",
   "target": "water_bottle_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 11,
   "to": 14
  },
  {
   "claim": "Yuki's keys are out of the house on a Wednesday at noon",
   "target": "keys_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 11,
   "to": 14
  },
  {
   "claim": "Yuki's notebook is at the entry hook on a Friday at noon",
   "target": "notebook_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 11,
   "to": 14
  }
 ],
 "targets": {
  "laptop_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "notebook_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "backpack_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
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
  "sunglasses_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
