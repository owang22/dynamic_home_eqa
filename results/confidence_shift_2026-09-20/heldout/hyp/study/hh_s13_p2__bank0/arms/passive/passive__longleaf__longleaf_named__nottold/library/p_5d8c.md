# p_5d8c — Priya the Homebody: nothing of hers leaves the house

Every clock-hour sighting of keys_priya, jacket_priya, wallet_priya, sunglasses_priya, phone_priya, and shoes_priya places them in their home locations (entry_table_e1, entry_hook_e1, nightstand_b2, shoe_rack_e1) at every hour from 00:00 through 22:00 on weekdays. There is no single sighting of any Priya object OUT_OF_HOUSE. The "found nothing" results in the 9–17h window (3 for keys, 3 for jacket, 3 for shoes, 4 for sunglasses) are a minority and may reflect brief moments during a balcony walk or a quick trip to the garden, not a true departure from the house. Priya is 70+ and retired; she does not drive, does not take the bus to errands, and her "morning walk" is a stroll on the balcony or in the garden. Her phone stays on the nightstand. Her keys, wallet, and sunglasses stay on the entry table. Her jacket stays on the hook.

What sets this apart from p_a3f1 and p_f7a2: at 12:00 on a Tuesday, keys_priya is at entry_table_e1 (not OUT_OF_HOUSE), phone_priya is at nightstand_b2, jacket_priya is at entry_hook_e1. No Priya object is ever OUT_OF_HOUSE. What would refute it: keys_priya sighted OUT_OF_HOUSE at any hour, or phone_priya sighted OUT_OF_HOUSE at any hour.

```json
{
 "claims": [
  {
   "claim": "Priya's keys are at the entry table at 15:00 on a weekday",
   "target": "keys_priya",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Priya's phone is at the nightstand at 14:00 on a weekday",
   "target": "phone_priya",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Priya's jacket is at the entry hook at 10:00 on a weekday",
   "target": "jacket_priya",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 11
  },
  {
   "claim": "Priya's sunglasses are at the entry table at 15:00 on a weekday",
   "target": "sunglasses_priya",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 14,
   "to": 16
  }
 ],
 "targets": {
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "almost_always"
   }
  ],
  "shoes_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 15,
    "to": 17,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ],
  "notebook_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "almost_always"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "laptop_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
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
