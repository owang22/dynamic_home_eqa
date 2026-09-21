# p_6a1b — Priya's Social Visits: Kitchen Tea, No Board Game (fork of p_a7b2)

The parent (p_a7b2) predicted the board game on the coffee table and the snack bowl on the coffee table during Priya's Wednesday and Friday afternoon visits. All four of those claims went against. The board game was at bookshelf_l1 at 16:00; the snack bowl was at sink_k1 at 16:00. The social visits may still happen, but they do not involve the board game or the living room.

This fork reinterprets the visits as **kitchen tea-and-chat**: friends come over, Priya makes tea in the kitchen, and they sit at the kitchen table. The mug_priya goes to the kitchen table. The glass_priya is at the sink (washed and ready). The board game stays on the bookshelf. The snack bowl stays in the kitchen (sink or counter). Hana is at work, so it is Priya hosting alone. The visits are quiet and domestic, not a living-room game night.

What changed from the parent: the board game is removed from the coffee table entirely (stays on bookshelf). The snack bowl stays in the kitchen. The social surface is the kitchen table, not the coffee table. The phone is still ON_PERSON during the visit (Priya is on the phone with friends or answering the door). The guitar block is removed (it was speculative).

What would refute it: if the board game is sighted off the bookshelf at 16:00 on a Wednesday or Friday, or if the snack bowl is on the coffee table, or if Priya is in the living room at 16:00 while the kitchen is empty.

_(targets the fork left unstated are inherited from p_a7b2)_

```json
{
 "claims": [
  {
   "claim": "The board game stays on the bookshelf at 16:00 on a Wednesday",
   "target": "board_game_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Priya's mug is on the kitchen table at 16:00 on a weekday during a social visit",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The snack bowl is in the kitchen (sink) at 16:00 on a weekday, not on the coffee table",
   "target": "snack_bowl_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The board game stays on the bookshelf at 16:00 on a Friday",
   "target": "board_game_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 14,
   "to": 17
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
    "from": 17,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "coasters_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "coffee_table_l1",
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
    "from": 14,
    "to": 17,
    "at": "ON_PERSON",
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
    "to": 9,
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
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
