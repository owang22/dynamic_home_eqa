# p_e9b2 — Priya's Morning Walk; Five Items Leave the House

Priya takes her keys, jacket, shoes, sunglasses, and wallet out for her weekday morning walk (approximately 07:00–09:00). The robot's 9–17 h looks at the entry area find all five items absent: keys and wallet missing from entry_table_e1, jacket missing from entry_hook_e1, shoes missing from entry_floor_e1, sunglasses missing from entry_table_e1. The dog leash goes with her to the entry hook before the walk and is also absent during the walk window. The resident log shows Priya in bedroom_2 at 06:00 (getting ready) and in the kitchen at 08:00 (back from the walk). All items return to their entry-area spots by 18:00. This differs from documents that keep these items at the entry all day. If any of the five items is sighted at its entry receptacle during 7–9 h on a weekday, this document is weakened for that item.

```json
{
 "claims": [
  {
   "claim": "Priya's keys are out of the house during her weekday morning walk",
   "target": "keys_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Priya's jacket is out of the house during her weekday morning walk",
   "target": "jacket_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Priya's sunglasses are out of the house during her weekday morning walk",
   "target": "sunglasses_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 7,
   "to": 9
  }
 ],
 "targets": {
  "keys_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "shoes_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
