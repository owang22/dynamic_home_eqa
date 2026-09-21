# p_c8d1 — Elena's full commute: eight objects leave at 8, return at 17:30

Elena's work day is a clean in-out cycle. At 8 she grabs her keys, wallet, sunglasses, phone, headphones, jacket, shoes, and backpack from the entry, plus her laptop from the bedroom desk, and walks out. None of these objects are in the house between 8 and 17:30 on weekdays. At 17:30 she returns and everything reappears at the entry (keys, wallet, sunglasses, backpack, jacket, shoes) or the bedroom (laptop, phone, headphones). On weekends nothing leaves; the objects stay at their resting spots.

This document is a pure Elena-commute claim. It sets itself apart from p_b8c2 (nothing ever leaves) by asserting that eight specific objects are OUT_OF_HOUSE for the full work day. It differs from p_a3f7 and p_d1e5 in that it covers the full set of objects rather than just keys and laptop, and it places the return at 17:30 rather than 17:00.

What would refute it: finding any of the eight objects in the house during 8–17h on a weekday; finding them at the entry at 03:00 on a weekday morning (they should be there) and then not at the entry at 18:00 (they should be back).

```json
{
 "claims": [
  {
   "claim": "Elena's backpack is out of the house during her weekday work day",
   "target": "backpack_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Elena's keys are out of the house during her weekday work day",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Elena's laptop is out of the house during her weekday work day",
   "target": "laptop_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Elena's jacket is out of the house during her weekday work day",
   "target": "jacket_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Elena's sunglasses are out of the house during her weekday work day",
   "target": "sunglasses_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  }
 ],
 "targets": {
  "laptop_elena": [
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
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "desk_b1",
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
  "wallet_elena": [
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
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "sunglasses_elena": [
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
  "backpack_elena": [
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
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "jacket_elena": [
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
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_elena": [
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
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "headphones_elena": [
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
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "phone_elena": [
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
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "scarf_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "hat_elena": [
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
