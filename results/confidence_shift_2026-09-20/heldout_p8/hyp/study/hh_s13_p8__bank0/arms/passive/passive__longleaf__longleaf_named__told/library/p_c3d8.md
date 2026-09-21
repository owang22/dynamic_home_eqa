# p_c3d8 — Minimal Travel: almost nothing leaves the house

Hana takes only her keys and phone to work. She uses the office computer, so the laptop stays home. She leaves her jacket, hat, handbag, sunglasses, wallet, water bottle, and charger at home. The entry hook still has her jacket, hat, handbag, charger, pen, and water bottle at 12:00 on a weekday. Priya rarely leaves: she takes a short walk 9:30–10:00 (keys and jacket go with her) but does not go out for errands. Her wallet, sunglasses, and phone stay home.

What sets this apart: at 12:00 on a weekday, jacket_hana is at entry_hook_e1 (not OUT_OF_HOUSE). water_bottle_hana is at entry_hook_e1. handbag_hana is at entry_hook_e1. wallet_hana is at entry_table_e1. In the standard hypothesis all of these are OUT_OF_HOUSE. What would refute it: jacket_hana OUT_OF_HOUSE at 12:00 on a weekday, or handbag_hana OUT_OF_HOUSE at 12:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Hana's jacket is at the entry hook at noon on a weekday",
   "target": "jacket_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Hana's handbag is at the entry hook at noon on a weekday",
   "target": "handbag_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Hana's wallet is at the entry table at noon on a weekday",
   "target": "wallet_hana",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Priya's wallet is at the entry table at 15:00 on a weekday",
   "target": "wallet_priya",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 13,
   "to": 17
  }
 ],
 "targets": {
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
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 10,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "laptop_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "jacket_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "hat_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "handbag_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "sunglasses_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 22,
    "at": "counter_k1",
    "chance": "usually"
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
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 10,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 10,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
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
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "ON_PERSON",
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
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
