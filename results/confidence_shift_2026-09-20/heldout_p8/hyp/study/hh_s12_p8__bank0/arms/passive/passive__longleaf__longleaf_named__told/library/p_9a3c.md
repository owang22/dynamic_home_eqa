# p_9a3c — Social evening hub: dining table, board game out, armchair blanket

Friends come over Tuesday, Saturday, and Sunday evenings (roughly 18:00–22:00). The dining table becomes the serving hub: plates and glasses are set out for dinner, and the kettle is brought from the counter to the table to serve drinks. The board game is pulled from the bookshelf to the coffee table for group play. On weekend socials the blanket shifts to the armchair; on the Tuesday social it stays on the couch (the weekday resting spot). The dog roams the living room floor with its toy while guests arrive. The remote moves to the coffee table for group TV after dinner. Priya's guitar stays in the bedroom—she does not bring it out to perform for guests. Elena's baking tray is at the counter during the weekend prep window (16–19h) before the social dinner.

This document is refuted if: the board game is found at the bookshelf during the 18–22h social window on a night friends are expected; the blanket is on the armchair on a Tuesday evening (should be couch); the kettle is at the counter during the 17–20h serving window; or the guitar is in the living room during the social.

```json
{
 "claims": [
  {
   "claim": "The board game is at the coffee table during the evening social window when friends are over",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The blanket is on the armchair during the weekend evening social",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The kettle is at the dining table being used to serve drinks during the social evening",
   "target": "kettle_shared",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 17,
   "to": 20
  },
  {
   "claim": "Elena's plate is at the dining table during the social dinner",
   "target": "plate_elena",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 18,
   "to": 21
  },
  {
   "claim": "Priya's guitar stays on the bedroom floor during the social evening (not brought to the living room)",
   "target": "guitar_priya",
   "expect": "bedroom_floor_b1",
   "days": "both",
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
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
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
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "kettle_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "plate_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "glass_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
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
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
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
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
