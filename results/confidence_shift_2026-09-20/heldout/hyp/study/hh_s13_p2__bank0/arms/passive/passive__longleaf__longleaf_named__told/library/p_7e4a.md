# p_7e4a — Wednesday Evening Social: Friends Over After Dinner, Living Room Takes Over

Hana and Priya live in this two-bedroom flat. Hana commutes to her office (out roughly 8:00–17:30 weekdays) and Priya is retired, home most of the day with a morning walk and an afternoon errand run. On the Wednesday in question the residents announced friends are coming over "this evening." This document models that specific social evening: the kitchen handles dinner as usual (Hana cooks, both eat at the kitchen table around 19:00–20:30), but the post-dinner phase is different from a quiet Tuesday. Instead of Hana heading to the bedroom floor for solo guitar and the two of them settling into a low-key TV watch, the living room becomes a social hub. The board game comes off the bookshelf and onto the coffee table, the snack bowl is refilled and set on the coffee table, glasses and mugs circulate for drinks, and Hana plays guitar for the group (on her person or propped on the coffee table) from about 20:30 to 22:00. The blanket is pulled onto the couch for the group to share. The remote is on the coffee table (TV on in the background, not the focus). The evening runs to about 23:00.

What sets this apart from the other documents: p_a7b2 models Priya's social visits in the *afternoon* (15–17 h) with the board game out; this document places the social activity in the *evening* (20:30–23 h) after dinner, with Hana present and playing guitar. p_c9d4 models a late night but keeps the remote and blanket on the *couch* at 22:00, which the Tuesday evidence contradicts (both were on the coffee table). p_a3f1 has the guitar on the bedroom floor in the 17–19 h window but says nothing about an evening social session. This document is the only one that predicts the board game, guitar, and snack bowl all on the coffee table simultaneously in the 21–23 h window on a weekday.

What would refute it: if on a Wednesday evening the board game is still on the bookshelf at 21:00 or 22:00, if the guitar is on the bedroom floor (not played) at 21:00, or if the residents are in the kitchen at 22:00 rather than the living room, the social-evening hypothesis is wrong. If Hana's laptop is found at the kitchen table or desk at 20:00 (rather than the entry hook or out of the house), the commuter baseline breaks.

Travelling objects: Hana's laptop, jacket, keys, handbag, wallet, pen, and water bottle are out of the house with her at work 8:00–17:30. Priya's keys and jacket are out with her on the afternoon errand 14:00–16:00. No objects are out during the social evening itself (friends bring nothing that the robot tracks).

```json
{
 "claims": [
  {
   "claim": "The board game is on the coffee table during the Wednesday social evening",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20.5,
   "to": 23
  },
  {
   "claim": "Hana is playing the guitar for friends at 21:00 on the social evening",
   "target": "guitar_hana",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "Hana's laptop is out of the house during weekday work hours",
   "target": "laptop_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "The snack bowl is on the coffee table during the social evening",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
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
    "from": 20.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
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
    "from": 19,
    "to": 21,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
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
    "from": 20.5,
    "to": 22,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23,
    "at": "coffee_table_l1",
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
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:glass": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
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
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
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
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ]
 }
}
```
