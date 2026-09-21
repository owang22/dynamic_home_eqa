# p_d1c3 — Weekend Drift: The Living Room and Entry Floor Take Over

The "mixture's worst objects" list is dominated by weekend mis-predictions: blanket at armchair_l1 (12x), jacket_priya at entry_floor_e1 (14x), remote at coffee_table_l1 (13x), shopping_bag at kitchen_table_k1 (12x), shoes_hana at entry_floor_e1 (9x), vacuum at floor_l_l1 (18x). On weekdays these objects sit at their "proper" spots (couch, hook, tv_stand, pantry, shoe_rack, storage). On weekends they migrate. The clock-hour data confirms every one of these shifts consistently across all weekend passes.

This document is a pure weekend-routine hypothesis. It says: on weekends, the blanket lives on the armchair (Priya naps there, or it is draped over the armchair while she sits in the living room doing puzzles). Priya's jacket slides from the hook to the entry floor (she takes it off and drops it on the floor rather than re-hanging it). Hana's shoes end up on the entry floor in the evening (she kicks them off and leaves them). The shopping bag moves to the kitchen table (she unpacks groceries there and leaves the bag out). The vacuum stays on the living room floor (it is used more on weekends and not put back in storage). The remote rests on the coffee table (they sit in the living room, not at the TV, for most of the day).

What sets this apart: at 16:00 on a Saturday, the blanket is at armchair_l1, jacket_priya at entry_floor_e1, shopping_bag at kitchen_table_k1, and vacuum at floor_l_l1. What would refute it: the blanket at couch_l1 at 16:00 on a Saturday, or jacket_priya at entry_hook_e1 at 16:00 on a Saturday.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the armchair at 16:00 on a Saturday",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Priya's jacket is on the entry floor at 16:00 on a Saturday",
   "target": "jacket_priya",
   "expect": "entry_floor_e1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The shopping bag is at the kitchen table at 14:00 on a Saturday",
   "target": "shopping_bag_shared",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 12,
   "to": 16
  },
  {
   "claim": "The vacuum cleaner is on the living room floor at 12:00 on a Saturday",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 10,
   "to": 14
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "jacket_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "shoes_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 16,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
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
    "days": "weekend",
    "from": 14,
    "to": 22,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "board_game_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   }
  ],
  "towel_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 18,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "bowl_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
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
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
