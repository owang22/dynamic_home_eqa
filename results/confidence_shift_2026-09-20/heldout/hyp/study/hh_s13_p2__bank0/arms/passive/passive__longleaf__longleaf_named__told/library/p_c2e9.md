# p_c2e9 — Saturday Puzzle Morning: Priya's Jigsaw at the Coffee Table 10-to-14

On Saturday, Priya has her late-morning walk (brief, around 10:00–10:30) and then settles into her jigsaw puzzle. The puzzle box comes off the bookshelf and is set at the coffee table in the living room from about 10:00 to 14:00. She works at the table, not at her desk, because it is a weekend and she is "around the house more." Hana is in the kitchen preparing brunch or at her desk browsing; the guitar stays on the bedroom floor (no playing in the morning).

What sets this document apart: it is the only one that places the puzzle box at coffee_table_l1 during a weekend mid-morning window. p_8a3c also predicts the puzzle at the coffee table 10–14, but this document is more specific about Priya's book staying on the bookshelf (she is doing the puzzle, not reading) and about Hana's laptop being at desk_b1 (she is home but not at the kitchen table).

Refutation: if the puzzle box is still on the bookshelf at 12:00, the coffee-table claim fails. If Priya's book is at the armchair or nightstand at 12:00, the bookshelf claim fails. If the guitar is NOT on the bedroom floor at 12:00, the resting claim fails.

```json
{
 "claims": [
  {
   "claim": "The puzzle box is on the coffee table at 12:00 on a Saturday because Priya is doing her jigsaw",
   "target": "puzzle_box_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 10,
   "to": 14
  },
  {
   "claim": "Priya's book is on the bookshelf at 12:00 on a Saturday because she is doing the puzzle, not reading",
   "target": "book_priya",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 10,
   "to": 14
  },
  {
   "claim": "The guitar is on the bedroom floor at 12:00 on a Saturday because Hana is not playing in the morning",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 10,
   "to": 14
  },
  {
   "claim": "Priya's headphones are at her desk at 12:00 on a Saturday (all-day resting spot)",
   "target": "headphones_priya",
   "expect": "desk_b2",
   "days": "weekend",
   "from": 10,
   "to": 14
  },
  {
   "claim": "Hana's laptop is at her desk at 12:00 on a Saturday because she is home and may be browsing",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 10,
   "to": 14
  }
 ],
 "targets": {
  "puzzle_box_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 14,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "book_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "headphones_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "almost_always"
   }
  ],
  "notebook_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "almost_always"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "laptop_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "keys_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "keys_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "phone_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 22,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "class:plate": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 16,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
