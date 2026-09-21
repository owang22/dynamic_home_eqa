# p_7f3a — Weekend Rhythm, Revised: No Guitar Session, No Puzzle Table, Late Brunch (fork of p_e5f0)

The parent document (p_e5f0) predicted a structured weekend: guitar played 14:00–17:00, puzzle on the coffee table 10:00–14:00, brunch at 11:00–13:00. The Saturday evidence refutes all three. At 16:00 Saturday the guitar was on the couch (2×) or the bedroom floor (1×), never ON_PERSON. At 12:00 Saturday the puzzle box was on the bookshelf (1×) or the kitchen floor (1×), never the coffee table. Plates appeared at the kitchen table at 14:00 and 16:00 Saturday, not at noon.

What changed: (1) The guitar is not played on Saturday afternoon; it rests on the couch or bedroom floor. (2) The puzzle box is not set out on the coffee table; it stays on the bookshelf or is briefly on the kitchen floor. (3) The weekend meal is a late brunch/lunch at 14:00–16:00, not 11:00–13:00. (4) Hana's keys still go out midday for errands (no evidence against), and the evening TV/movie session is retained.

What would refute this document: guitar ON_PERSON at 16:00 Saturday, puzzle box on the coffee table at 12:00 Saturday, or plates on the kitchen table at 11:00 Saturday (early brunch instead of late).

```json
{
 "claims": [
  {
   "claim": "Hana's keys are at the entry table at 8:00 on a Saturday",
   "target": "keys_hana",
   "expect": "entry_table_e1",
   "days": "weekend",
   "from": 7,
   "to": 10
  },
  {
   "claim": "Plates are on the kitchen table at 15:00 on a Saturday (late brunch)",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 14,
   "to": 16.5
  },
  {
   "claim": "The guitar is on the couch at 16:00 on a Saturday (not being played)",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 15,
   "to": 17.5
  },
  {
   "claim": "The puzzle box is on the bookshelf at 12:00 on a Saturday (not set out)",
   "target": "puzzle_box_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 11,
   "to": 14
  }
 ],
 "targets": {
  "laptop_hana": [
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
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "jacket_hana": [
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
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20.5,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "floor_k_k1",
    "chance": "rarely"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 23,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "plate_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
