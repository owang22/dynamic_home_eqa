# p_7e2a — Wednesday Friends Evening: the living room becomes the party

Hana and Priya have friends coming over this Wednesday evening. The message was sent during the day, so the household shifts into hosting mode by the time Hana walks in at 5:30. The living room is cleared of its usual clutter: the puzzle box goes back on the bookshelf (Priya pauses her jigsaw for guests), the board game comes down, the snack bowl and coasters migrate to the coffee table, and the guitar is within arm's reach. Hana will likely play a few songs while drinks are poured; the TV is on in the background with the remote on the couch. Priya's reading and headphones stay in her bedroom — she's in the living room for the social hour.

This hypothesis is distinguished from the library's existing documents by the specific Wednesday-evening social configuration: the board game is *out* of the bookshelf, the guitar is *in use* (ON_PERSON) rather than resting on the bedroom floor, and the snack bowl is on the coffee table rather than the kitchen counter. It also predicts that the 18:00 kitchen presence (both residents seen there Tuesday) is for drinks and prep, not full cooking — the pan and knife stay in the cupboard/drawer until at least 19:30.

What would refute it: if the board game is still on the bookshelf at 19:00 Wednesday, if the guitar is on the bedroom floor at 20:00, if the snack bowl is in the kitchen, or if Hana's jacket is still out of the house at 19:00 (she never came home).

```json
{
 "claims": [
  {
   "claim": "The board game is on the coffee table at 19:00 on Wednesday (friends are here)",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 18,
   "to": 21
  },
  {
   "claim": "The guitar is being played by Hana at 20:00 on Wednesday",
   "target": "guitar_hana",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The snack bowl is on the coffee table at 19:00 on Wednesday",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 18,
   "to": 21
  },
  {
   "claim": "Hana's jacket is at the entry hook at 19:00 on Wednesday (she is home)",
   "target": "jacket_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 18,
   "to": 21
  },
  {
   "claim": "The pan is still in the cupboard at 18:00 on a weekday (no cooking yet)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  }
 ],
 "targets": {
  "board_game_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "coasters_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 19,
    "to": 22,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 19,
    "to": 22,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "glass_hana": [
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekday",
    "from": 17.5,
    "to": 23,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 17.5,
    "to": 23,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "laptop_hana": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 23,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 19.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ]
 }
}
```
