# p_7b4e — The 19:00 Dinner: Kitchen Cold Until Seven

Hana works in town and arrives home at 17:30. Priya is retired and home all day. Neither cooks at 18:00 — the kitchen stays cold through the early evening. The actual cooking window opens at 19:00, when Hana (or Priya, on some nights) starts dinner. The evidence is unambiguous: the pan sits in the cupboard at 18:00 and is on the counter at 19:00; the spatula is in the drawer at 18:00 and on the counter at 19:00; the recipe book is on the pantry shelf at 18:00 and on the counter at 19:00. Plates come out to the kitchen table around 19:00–20:00. By 21:00 the cooking is done and items migrate to the sink and dish rack.

This document sets itself apart by placing ALL cooking items in storage from 11:00 through 19:00 and on the counter only from 19:00 to 21:00. Documents that put the pan or knife on the counter at 17:30–18:00 are wrong: the 18:00 patrol pass finds the pan in the cupboard and the spatula in the drawer. The 19:00 pass finds them on the counter.

What would refute this: a sighting of the pan, spatula, or knife on the counter before 18:30 on a weekday, or a sighting of them still in storage after 19:30.

```json
{
 "claims": [
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday because cooking has not started yet",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The pan is on the kitchen counter at 19:30 on a weekday during dinner cooking",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The spatula is in the drawer at 18:00 on a weekday (not yet in use)",
   "target": "spatula_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The recipe book is on the counter at 19:30 on a weekday (being referenced during cooking)",
   "target": "recipe_book_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Hana's plate is in the cupboard at 18:00 on a weekday (dinner not yet served)",
   "target": "plate_hana",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "class:plate": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "almost_always"
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
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "class:bowl": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
