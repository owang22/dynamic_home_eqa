# p_d5e7 — Priya's Bedroom Fortress: her objects never leave bedroom-b2

Priya is very territorial about her bedroom (bedroom_b2, desk_b2, nightstand_b2). Her book, phone, headphones, and notebook are in the bedroom at all times. She does not take them to the living room or kitchen. She reads in bed or at the desk. She does puzzles at the desk, not the coffee table. Her toiletry bag, razor, and towel are in the bathroom. The only time her objects leave the bedroom is when she goes out (walk, errands) — and then only jacket, keys, wallet, sunglasses, phone.

What sets this apart: at 15:00 on a weekday, book_priya is at nightstand_b2 (not kitchen_table_k1 or couch_l1). notebook_priya is at desk_b2. puzzle_box_shared is at desk_b2 (not coffee_table_l1). In the kitchen-hub hypothesis the book is at the kitchen table. What would refute it: book_priya at kitchen_table_k1 or couch_l1 at any time, or notebook_priya at coffee_table_l1.

```json
{
 "claims": [
  {
   "claim": "Priya's book is at the nightstand at 15:00 on a weekday",
   "target": "book_priya",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Priya's notebook is at desk_b2 at 15:00 on a weekday",
   "target": "notebook_priya",
   "expect": "desk_b2",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The puzzle box is at desk_b2 during Priya's puzzle time",
   "target": "puzzle_box_shared",
   "expect": "desk_b2",
   "days": "weekday",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Priya's headphones are on the bed at 15:00 on a weekday",
   "target": "headphones_priya",
   "expect": "bed_b2",
   "days": "weekday",
   "from": 14,
   "to": 17
  }
 ],
 "targets": {
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 10,
    "to": 17,
    "at": "desk_b2",
    "chance": "usually"
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
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bed_b2",
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
    "from": 8,
    "to": 9,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "ON_PERSON",
    "chance": "usually"
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
    "at": "desk_b2",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 14,
    "at": "desk_b2",
    "chance": "usually"
   }
  ],
  "toiletry_bag_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "razor_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "ON_PERSON",
    "chance": "sometimes"
   }
  ],
  "towel_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "ON_PERSON",
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
    "from": 8,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "OUT_OF_HOUSE",
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
    "from": 8,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
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
    "from": 8,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 9,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ]
 }
}
```
