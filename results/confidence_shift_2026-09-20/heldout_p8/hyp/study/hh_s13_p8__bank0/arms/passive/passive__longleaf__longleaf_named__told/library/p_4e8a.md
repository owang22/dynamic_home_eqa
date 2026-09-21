# p_4e8a — Wednesday Guest Evening: The Living Room Fills

Hana and Priya have friends coming over this Wednesday evening. The message arrived Wednesday, so the decisive test is tonight. When guests arrive around 18:00 the living room becomes the social space: the board game comes off the bookshelf to the coffee table, the snack bowl is full and sits on the coffee table, and the blanket is on the couch for comfort. The guitar stays on the bedroom floor — social time takes priority over playing. The remote stays on the TV stand; the TV is off while everyone is talking. Extra plates come out of the cupboard to the kitchen table for food and drinks. Both residents are in the living room for most of the evening, and the friends join them there.

What sets this apart from the other documents: the board game and snack bowl are on the coffee table (not the bookshelf and counter), the guitar is explicitly NOT being played, and the remote is NOT in use. This contrasts with p_b1c6 (guitar as the evening anchor, ON_PERSON 19-21) and p_a7b2 (Priya's social circle, which puts the board game on the coffee table but does not model the full guest evening with snacks, plates, and the guitar sidelined).

What would refute it: if the board game is on the bookshelf at 20:00 Wednesday, or if the guitar is sighted ON_PERSON or on the coffee table, or if the remote is on the coffee table (TV on).

```json
{
 "claims": [
  {
   "claim": "The board game is on the coffee table during the Wednesday guest evening",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The guitar stays on the bedroom floor and is not played during the Wednesday guest evening",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The remote stays on the TV stand during the Wednesday guest evening",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the coffee table during the Wednesday guest evening",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
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
    "from": 18,
    "to": 22,
    "at": "coffee_table_l1",
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
    "from": 18,
    "to": 22,
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "tv_stand_l1",
    "chance": "almost_always"
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
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
  "coasters_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
