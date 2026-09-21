# p_a1f3 — Ines's mobile work day: laptop in hand midday, accessories anchored at the desk

Ines works from home in the office room, but she is not glued to the desk. The patrol passes catch her laptop at desk_o1 at 10:00, 16:00, and 17:00, yet 24 of 26 looks at desk_o1 during 9–17 h find nothing. The pattern that fits: she starts at the desk around 9, picks the laptop up and works on it while moving around the office (or the adjacent living area) through the middle of the day, then sets it back on the desk for the final stretch before 17:30. Her charger, headphones, and pen stay on the desk throughout because they are tethered or simply left there; only the laptop and her drink travel with her. Elena commutes as usual: keys, backpack, and jacket leave at 8 and return at 17:30.

What sets this apart: every other live document either pins the laptop to desk_o1 all day (p_a3f7, p_d1e5 — both heavily contradicted) or to floor_o_o1 (p_3e7a, p_7d4e, p_c4d9 — all failed). This document puts it ON_PERSON during 10–15 h, a window where no patrol pass has yet looked, so the claim is testable the next time Ines is asked for her laptop mid-morning.

What would refute it: a look at desk_o1 during 11–14 h that finds the laptop there (it is not mobile), or a look at ON_PERSON that finds Ines empty-handed while the laptop is sighted at some other fixed receptacle.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is on her person during the weekday midday mobile session",
   "target": "laptop_ines",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 11,
   "to": 14
  },
  {
   "claim": "Ines's charger is at the office desk during weekday afternoon work",
   "target": "charger_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "Ines's mug is at the kitchen table in the morning before work",
   "target": "mug_ines",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 7,
   "to": 8.5
  },
  {
   "claim": "Ines's headphones are at the office desk during weekday late-afternoon work",
   "target": "headphones_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Elena's keys are out of the house during her weekday work day",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 15,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 12,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ],
  "charger_ines": [
   {
    "days": "weekday",
    "from": 9,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "headphones_ines": [
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "mug_ines": [
   {
    "days": "both",
    "from": 6,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "pen_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "jacket_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
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
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ]
 }
}
```
