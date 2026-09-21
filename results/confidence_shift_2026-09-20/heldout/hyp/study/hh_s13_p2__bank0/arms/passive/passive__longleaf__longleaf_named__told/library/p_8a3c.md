# p_8a3c — Saturday Full-Home: Neither Resident Leaves, Hobbies Loose

Hana and Priya are both in the house all day Saturday. Hana's weekday travel objects—keys, jacket, handbag, wallet, sunglasses, shoes, scarf—remain at the entry because she has no office to go to. Her laptop stays at desk_b1; she may browse or read but does not commute. Priya's keys and jacket also stay at the entry; her late-morning walk is brief (perhaps 10:00–10:30) and she is back before the robot's next pass. The phrase "around the house more" means both residents drift through the kitchen and living room rather than retreating to bedrooms.

What sets this document apart: it is the only one in which **nothing leaves the house on Saturday**. No OUT_OF_HOUSE block appears. Hana's guitar is played in the late afternoon (15–18 h) as a weekend hobby, moving to ON_PERSON for that window. Priya's puzzle box comes off the bookshelf for a mid-morning session (10–14 h) at the coffee table. Brunch is at the kitchen table 10–13 h.

Refutation: any sighting of Hana's keys, handbag, wallet, or sunglasses anywhere in the house during a window when another document says they are out (or vice-versa) would shift weight. If the guitar is still on the bedroom floor at 16:00, the ON_PERSON claim fails. If the puzzle box is still on the bookshelf at 12:00, the coffee-table claim fails.

```json
{
 "claims": [
  {
   "claim": "Hana's keys are at the entry table at 10:00 on a Saturday because she is home, not at work",
   "target": "keys_hana",
   "expect": "entry_table_e1",
   "days": "weekend",
   "from": 8,
   "to": 12
  },
  {
   "claim": "Hana's laptop is at desk_b1 at 10:00 on a Saturday because she does not commute on weekends",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 8,
   "to": 14
  },
  {
   "claim": "The guitar is being played by Hana at 16:00 on a Saturday as a weekend hobby",
   "target": "guitar_hana",
   "expect": "ON_PERSON",
   "days": "weekend",
   "from": 15,
   "to": 18
  },
  {
   "claim": "Priya's keys are at the entry table at 14:00 on a Saturday because she is home, not on a walk",
   "target": "keys_priya",
   "expect": "entry_table_e1",
   "days": "weekend",
   "from": 13,
   "to": 16
  },
  {
   "claim": "Hana's handbag is at the entry hook at 10:00 on a Saturday because she has not gone out",
   "target": "handbag_hana",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 8,
   "to": 12
  }
 ],
 "targets": {
  "keys_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "sunglasses_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "shoes_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ],
  "scarf_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "laptop_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "phone_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 22,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 15,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 18,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 14,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "phone_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 22,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "class:plate": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 16,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "class:glass": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "class:mug": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
