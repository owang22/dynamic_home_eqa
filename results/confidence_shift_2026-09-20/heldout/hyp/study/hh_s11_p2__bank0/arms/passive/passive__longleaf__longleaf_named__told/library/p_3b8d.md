# p_3b8d — Priya's 7-to-9 Walk; the Whole Entry Set Goes Out

Priya takes her weekday morning walk from roughly 7 to 9. She grabs her keys, jacket, shoes, sunglasses, and wallet from the entry area, plus the dog leash from its hook. All five personal items and the leash are absent from their usual spots during the 9–17 h window — the robot's looks at entry_table_e1, entry_hook_e1, and entry_floor_e1 find nothing. By the 08:00 pass she is back in the kitchen (resident sighting), and her keys appear on the entry hook at 08:00 before settling back on the table by 18:00. On weekends her walk is later (late morning, roughly 10–12), so the items stay out a bit longer. This document captures the full set of travelling items together, which no single existing document does: p_bcd1 covers the leash and toy, p_a3f7 covers the keys, but the jacket, shoes, sunglasses, and wallet are not grouped with them.

What would refute this document: a look at entry_table_e1 at 8:00 on a weekday that finds Priya's keys, jacket, sunglasses, or wallet; a look at entry_hook_e1 at 8:00 that finds the dog leash; a resident look showing Priya in the house at 7:30 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Priya's keys are out of the house during her weekday morning walk",
   "target": "keys_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 7.5,
   "to": 8.5
  },
  {
   "claim": "Priya's jacket is out of the house during her weekday morning walk",
   "target": "jacket_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 7.5,
   "to": 8.5
  },
  {
   "claim": "The dog leash is out of the house during Priya's weekday morning walk",
   "target": "dog_leash_shared",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 7.5,
   "to": 8.5
  }
 ],
 "targets": {
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
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "shoes_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "wallet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "camera_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
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
  ],
  "class:bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
