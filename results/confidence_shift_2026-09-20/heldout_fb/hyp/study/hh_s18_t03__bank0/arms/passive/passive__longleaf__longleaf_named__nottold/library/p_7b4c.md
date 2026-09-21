# p_7b4c — Ines's kitchen-table morning: bowl, vitamins, and mug at 7–9h before the office

Ines's morning begins in the kitchen. Around 7 she sits at the kitchen table with her bowl for a light breakfast (oatmeal or fruit), her vitamins, and her mug of tea or coffee. She stays at the kitchen table until about 9, then carries her mug to the office and settles at the desk. Her water bottle is already at the desk from the previous evening (or she fills it at the kitchen sink and brings it in at 8). Elena is still in the house at this hour (she leaves at 8), so both women may be in the kitchen or bedroom during the 7–8h window.

This document focuses on the 6:30–9h morning transition for Ines. It sets itself apart from p_a4e7 and p_f2b9 by explicitly placing the mug, bowl, and vitamins at the kitchen table during breakfast rather than at the desk. It differs from p_c4f8 (which also has a kitchen-table morning) by being more specific about the 7–8h window and by adding the water-bottle transition to the desk at 8h.

What would refute it: finding Ines's bowl at the kitchen table at 10h (it should be back in the cupboard after breakfast); finding the vitamins at the kitchen table at 12h (they should be taken and the bottle back in the cupboard); the mug being at the desk before 9h.

```json
{
 "claims": [
  {
   "claim": "Ines's bowl is at the kitchen table during the 7-to-9h breakfast window",
   "target": "bowl_ines",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Ines's vitamins are at the kitchen table in the morning",
   "target": "vitamins_ines",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Ines's mug is at the kitchen table before 9:00",
   "target": "mug_ines",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Ines's water bottle is at the office desk by 10:00 on weekdays",
   "target": "water_bottle_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Elena's keys are out of the house from 8:00 on weekdays",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  }
 ],
 "targets": {
  "mug_ines": [
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "bowl_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "vitamins_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "laptop_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 11,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 15,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "mug_elena": [
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_table_e1",
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
   }
  ]
 }
}
```
