# p_d1e6 — Friends evening: board game at the coffee table, guitar on the floor, Tuesday included

Friends come over on Saturday evening, Sunday evening, and Tuesday evening (per the residents' messages). The social gathering is in the living room, not the dining room. Dinner is served at the dining table around 19:30–21:00, but the evening socialising — board games, guitar playing, conversation — happens in the living room from about 20:00 onward. The board game comes out to the coffee table at 21:00 (the 22:00 patrol finds it there on weekends); it is NOT at the dining table. Priya plays guitar on the living-room floor for the guests from 19:00 to 22:00. Elena's laptop is at the coffee table during the day on weekends since she is home.

What sets this apart from p_3f7a (board game at dining_table_d1 19–22h, 5 against): the board game is at the COFFEE TABLE, not the dining table. The 22:00 weekend sighting confirms coffee_table_l1. What sets it apart from p_9c1d (board game at coffee table 20–22h, 2 against): the game is not out at 20:00; it appears at the coffee table by 21:00–22:00. The window is 21–23, not 20–22. What sets it apart from p_9b3c (dinner 19:30–21, board game 20–22): the board game window is later, and this document explicitly includes Tuesday as a friends evening (though the JSON can only encode weekday/weekend, the prose records the Tuesday pattern).

This is refuted if the board game is at the dining table during the friends evening, or if the guitar is in the bedroom during the evening social, or if the laptop is not at the coffee table on weekend midday.

```json
{
 "claims": [
  {
   "claim": "The board game is on the coffee table during the weekend friends evening at 22:00",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Priya's guitar is on the living-room floor during the weekend friends evening",
   "target": "guitar_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Elena's laptop is at the coffee table on a weekend midday because she is home",
   "target": "laptop_elena",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 10,
   "to": 16
  },
  {
   "claim": "The baking tray is at the kitchen counter during Saturday morning baking",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 9,
   "to": 12
  }
 ],
 "targets": {
  "board_game_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 23,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "guitar_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 19,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
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
    "to": 24,
    "at": "coffee_table_l1",
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
  "plate_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 19,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "wallet_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
