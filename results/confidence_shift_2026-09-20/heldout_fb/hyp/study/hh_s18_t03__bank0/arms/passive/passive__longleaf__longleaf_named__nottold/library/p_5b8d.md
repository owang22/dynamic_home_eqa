# p_5b8d — Ines's kitchen-table morning and desk afternoon: mug and bottle follow the work rhythm

Ines's day has two distinct spatial anchors. The morning (6–9 h) is kitchen-centred: her mug is at the kitchen table for breakfast, her water bottle is being filled or carried to the office, and her vitamins and bowl are at the kitchen table. Once the work session starts (9 h), the mug moves to the office desk and stays there through the afternoon (13–18 h), while the water bottle is at the desk but periodically goes to the kitchen sink to be refilled (the 14:00 patrol catches it at sink_k1). The charger, headphones, and pen never leave the desk. Ines does not leave the house on weekdays; her keys, sunglasses, and wallet stay at the entry table all day. Elena's personal items (keys, backpack, jacket, sunglasses, wallet) leave at 8 and return at 17:30.

What sets this apart: p_a3f7 and p_d1e5 put the mug at desk_o1 all day (1 for, 25 against for mug_ines at desk_o1). p_c4f8 puts the mug at the kitchen table 6–9 h (1 for, 4 against) which is closer but does not extend the afternoon desk block. This document explicitly separates the morning kitchen anchor from the afternoon desk anchor for the mug, and adds the water bottle's sink excursions.

What would refute it: a look at the kitchen table at 7:00 that finds no mug (it is already at the desk), or a look at desk_o1 at 15:00 that finds neither mug nor water bottle (Ines is not at the desk at all).

```json
{
 "claims": [
  {
   "claim": "Ines's mug is at the kitchen table in the morning before work",
   "target": "mug_ines",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 6.5,
   "to": 8
  },
  {
   "claim": "Ines's water bottle is at the office desk during weekday midday work",
   "target": "water_bottle_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 15
  },
  {
   "claim": "Ines's mug is at the office desk during weekday afternoon work",
   "target": "mug_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Ines's keys are at the entry table during weekday work hours",
   "target": "keys_ines",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Ines's laptop is at the office desk during the late-afternoon session",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 16,
   "to": 17
  }
 ],
 "targets": {
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
  "water_bottle_ines": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
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
    "chance": "usually"
   }
  ],
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
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "headphones_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "bed_b1",
    "chance": "usually"
   }
  ],
  "keys_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "sunglasses_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "wallet_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
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
  "vitamins_ines": [
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "bowl_ines": [
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
