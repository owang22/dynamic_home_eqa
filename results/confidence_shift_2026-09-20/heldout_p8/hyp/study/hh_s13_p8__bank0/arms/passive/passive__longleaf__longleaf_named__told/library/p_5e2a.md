# p_5e2a — Thursday Guest Evening: The Kitchen Fills Again

The message says friends are coming Thursday evening as well. This is a second night of the same kitchen-dinner routine. The kitchen table fills with plates and mugs. The counter holds the snack bowl and glass. The living room stays quiet: board game on the bookshelf, guitar on the bedroom floor, remote on the TV stand. Hana comes home from work at 17:30, drops her things at the entry, and joins Priya in the kitchen.

What sets this apart from p_8f3d (the Wednesday fork): this document explicitly covers Thursday. The targets are the same kitchen-dinner pattern, but the claims are scoped to Thursday so the robot can distinguish the two evenings. If the Thursday evening looks different from Wednesday (e.g., no cooking, a movie night instead), this document will lose weight while p_8f3d retains its Wednesday-specific evidence.

What would refute it: if the board game is off the bookshelf at 19:00 Thursday, or if both residents are in the living room at 19:00 Thursday while the kitchen is empty, or if the snack bowl is on the coffee table.

```json
{
 "claims": [
  {
   "claim": "The board game stays on the bookshelf during the Thursday guest dinner",
   "target": "board_game_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The snack bowl is at the kitchen counter during the Thursday guest dinner",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 21
  },
  {
   "claim": "Hana's mug is on the kitchen table during the Thursday guest dinner",
   "target": "mug_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The guitar stays on the bedroom floor during the Thursday guest dinner",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 18,
   "to": 22
  }
 ],
 "targets": {
  "board_game_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
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
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
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
    "from": 18,
    "to": 20,
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
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "glass_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
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
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
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
   }
  ]
 }
}
```
