# p_4e7a — Wed/Thu Friends: Kitchen Dinner, Then Living Room

Hana and Priya have friends coming over both Wednesday and Thursday evenings, as confirmed by the residents' messages. The evening unfolds in two acts: first a shared dinner at the kitchen table (roughly 18:00–20:00), then a migration to the living room for drinks, conversation, and possibly a board game (20:00–22:00). This document corrects p_7e2a, which placed the board game and snack bowl on the coffee table at 19:00—five and eight looks respectively found them elsewhere. The snack bowl clock data (counter at 18–19h, coffee table at 21h) shows it stays in the kitchen through dinner and only migrates to the coffee table after the table is cleared. Hana's jacket is consistently absent from the entry hook in the evening (seven against-counts across multiple documents), suggesting she hangs it in the bedroom or wardrobe rather than leaving it at the door. The guitar may come out for a casual performance, but no sightings confirm this yet.

What sets this apart: the two-act structure (kitchen → living room) with a clear 20:00 transition, and the explicit Thursday coverage that no other document provides. If the board game is sighted on the kitchen table during dinner hours, or if the snack bowl is found on the coffee table before 20:00 on a friend-evening, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is still on the kitchen counter at 19:00 on a Wednesday evening (dinner in progress)",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "Plates are on the kitchen table during dinner at 19:00 on a Thursday evening",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The board game is back on the bookshelf at 18:00 on a Wednesday (friends just arrived, game not yet out)",
   "target": "board_game_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Hana's jacket is out of the house during weekday work hours",
   "target": "jacket_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  }
 ],
 "targets": {
  "board_game_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
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
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 23,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
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
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
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
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "ON_PERSON",
    "chance": "rarely"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
