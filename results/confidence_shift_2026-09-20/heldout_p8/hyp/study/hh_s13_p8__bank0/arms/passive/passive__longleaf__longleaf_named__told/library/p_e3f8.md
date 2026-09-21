# p_e3f8 — The Workaholic: Hana out 7:30-to-19, no guitar on weekdays

Hana is a workaholic. She leaves at 7:30 and does not return until 19:00 on weekdays. When she comes home she is tired: no guitar on weekdays (the guitar stays on the bedroom floor all evening), a quick dinner, and TV 20:00–21:30. Guitar is a weekend-only activity (14:00–17:00 on Saturday and Sunday). Priya is the main evening person: she does puzzles 15:00–17:00, watches TV 19:30–22:00, and goes to bed at 22:00.

What sets this apart: at 18:00 on a weekday, Hana is NOT home yet (her keys are still OUT_OF_HOUSE). The guitar is on the bedroom floor at 20:00 on a weekday (not being played). On a Saturday at 16:00 the guitar is ON_PERSON or on the coffee table. What would refute it: Hana's keys at entry_table_e1 at 18:00 on a weekday, or the guitar on the coffee table at 20:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Hana's keys are still out of the house at 18:00 on a weekday",
   "target": "keys_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 7.5,
   "to": 19
  },
  {
   "claim": "The guitar stays on the bedroom floor at 20:00 on a weekday",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "The guitar is being played at 16:00 on a Saturday",
   "target": "guitar_hana",
   "expect": "ON_PERSON",
   "days": "weekend",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Hana's laptop is out of the house at 18:00 on a weekday",
   "target": "laptop_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 7.5,
   "to": 19
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 19,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "charger_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 19,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 19,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 19,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 19,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 17,
    "at": "ON_PERSON",
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
    "to": 21.5,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "couch_l1",
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
    "from": 7,
    "to": 7.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:mug": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 7.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
