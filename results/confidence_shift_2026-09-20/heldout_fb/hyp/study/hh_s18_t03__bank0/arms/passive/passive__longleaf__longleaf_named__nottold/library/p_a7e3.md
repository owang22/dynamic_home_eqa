# p_a7e3 — Ines's mobile morning: laptop in hand until the afternoon desk session

Ines works from home but does not anchor to the desk for the full 9-to-5:30 stretch. Across four weekday patrol passes her laptop is found at desk_o1 only at 10:00, 16:00, and 17:00, while 24 looks at the desk during 9–17h come up empty. The most parsimonious reading is that she carries the laptop between the kitchen table, the office floor, and her lap during the morning (9–12h), settles it on the desk for a focused afternoon block (roughly 14–17h), and pushes it to the office floor at 18:00 when the work day ends. Her charger, water bottle, and headphones mirror the pattern: absent from the desk before noon, present in the afternoon. Elena commutes to her office in town from about 8 to 5:30; her laptop, keys, backpack, and headphones leave with her and return by 18:00.

This document separates itself from p_a3f7 (laptop at desk all day) and p_3e7a / p_8f2b (laptop on the floor all day) by placing the laptop ON_PERSON during the morning and at the desk only in the afternoon. The twelve weak-for hits on p_7f3a's ON_PERSON claim—empty looks at the desk during 9–16h—support the mobile-morning reading. It would be refuted if the laptop is consistently found at desk_o1 during 9–12h, or if it is never seen at the desk at all.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is on her person during weekday morning work",
   "target": "laptop_ines",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 9,
   "to": 12
  },
  {
   "claim": "Ines's laptop is at the office desk during weekday afternoon work",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Ines's charger is at the office desk during weekday afternoon",
   "target": "charger_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Elena's laptop is out of the house during weekday work hours",
   "target": "laptop_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "The remote is on the coffee table during evening TV",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "floor_o_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ],
  "charger_ines": [
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "weekday",
    "from": 8,
    "to": 11,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
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
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
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
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ],
  "laptop_elena": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "headphones_elena": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
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
  ]
 }
}
```
