# p_3d7e — Weekend friends evening: baking morning, board games and guitar at night

Elena and Priya are both home on Saturday, off their weekday routines. Elena bakes in the morning — the baking tray comes out of the pantry to the counter around 9 and stays there through the midday baking session. In the evening, friends arrive around 6:30–7. The dining table gets set for a larger group: extra plates, glasses, and bowls come out of the cupboard. A board game is pulled from the bookshelf and set on the coffee table. Priya brings her guitar out of the bedroom into the living room to play for the group. The shared blanket goes on the couch for the guests to settle in. The dog is more active with the extra people, so the toy stays on the living room floor. Both residents are in the living and dining areas from about 18:00 onward.

What sets this apart from the weekday documents: the baking tray is at the counter (not the pantry) on weekend mornings; the guitar is in the living room (not the bedroom floor) on weekend evenings; the board game is on the coffee table (not the bookshelf); and the blanket is on the couch specifically for guests rather than drifting between couch and coffee table. The dog bowl stays at the kitchen floor as always.

This would be refuted if the baking tray is seen at the pantry shelf on a Saturday morning between 9 and 12, if the guitar is found at the bedroom floor during a Saturday evening, or if the board game stays on the bookshelf through the evening.

```json
{
 "claims": [
  {
   "claim": "The baking tray is at the kitchen counter during Saturday morning baking",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 9,
   "to": 12
  },
  {
   "claim": "The board game is on the coffee table during Saturday evening with friends",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Priya's guitar is in the living room during Saturday evening",
   "target": "guitar_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The blanket is on the couch during Saturday evening with guests",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  }
 ],
 "targets": {
  "baking_tray_shared": [
   {
    "days": "weekend",
    "from": 9,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   }
  ],
  "board_game_shared": [
   {
    "days": "weekend",
    "from": 18,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "guitar_priya": [
   {
    "days": "weekend",
    "from": 18,
    "to": 22,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 18,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "plate_elena": [
   {
    "days": "weekend",
    "from": 18,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "plate_priya": [
   {
    "days": "weekend",
    "from": 18,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "glass_elena": [
   {
    "days": "weekend",
    "from": 18,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "almost_always"
   }
  ],
  "glass_priya": [
   {
    "days": "weekend",
    "from": 18,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "almost_always"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "weekend",
    "from": 10,
    "to": 23,
    "at": "floor_l_l1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "almost_always"
   }
  ],
  "mug_elena": [
   {
    "days": "weekend",
    "from": 9,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekend",
    "from": 9,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
