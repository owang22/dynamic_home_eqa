# p_c4f8 — Ines's two-anchor day: kitchen table morning, office desk afternoon

Ines's day splits into two clear anchors. From about 6:30 to 9:00 she is at the kitchen table: her mug, a bowl, and her vitamins are all there at 07:00 and 08:00, and her water bottle is still in the dish rack or sink. Around 8:00–9:00 she moves to the office and her water bottle appears at desk_o1. The afternoon anchor (13:00–18:00) is the office desk: charger, water bottle, mug, and headphones all converge there, and the laptop is found at the desk at 16:00 and 17:00. At 18:00 the laptop shifts to the office floor and the water bottle goes to the sink or kitchen table for dinner. Elena leaves for her office around 8:00 and returns by 17:30; her items sit at the entry (keys, sunglasses, wallet, backpack, headphones) and the bedroom desk (laptop) while she is out.

This document differs from p_a3f7 by explicitly separating the morning kitchen anchor from the afternoon office anchor, and from p_7f3a by not claiming ON_PERSON for the laptop (instead the laptop is at the desk during the afternoon and unaccounted for in the morning, falling through to sighting statistics). It would be refuted if Ines's mug is found at the office desk before 12:00, or if her laptop is consistently at the desk during 9–12h.

```json
{
 "claims": [
  {
   "claim": "Ines's mug is at the kitchen table in the morning before work",
   "target": "mug_ines",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 6,
   "to": 9
  },
  {
   "claim": "Ines's laptop is at the office desk during weekday late-afternoon work",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 15,
   "to": 18
  },
  {
   "claim": "Ines's water bottle is at the kitchen table during dinner",
   "target": "water_bottle_ines",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "Elena's keys are out of the house during weekday work hours",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Ines's headphones are at the office desk during weekday afternoon work",
   "target": "headphones_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 14,
   "to": 18
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
  "water_bottle_ines": [
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
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
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 15,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
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
