# p_7a3f — The 19:00 Cook: cooking tools hit the counter at 18:30, not 17:30 (fork of p_b9c4)

This is a fork of p_b9c4. The evidence is clear: pan_shared was at cupboard_k1 at 18:00 (2 sightings) and only appeared at counter_k1 at 19:00. The spatula was at drawer_k_k1 at 18:00 and on counter_k1 at 19:00. The recipe book was at pantry_shelf_k1 at 18:00 and on counter_k1 at 19:00. The cooking window is 18:30–20:00, not 17:30–19:00. Hana comes home around 17:30, spends the first half hour settling in, then starts cooking at 18:30 and serves around 19:30–20:00.

What changed from the parent: the cooking window shifts from 17.5–19 to 18.5–20. The cutting board gets a weekday 9–17.5 drawer override (it is NOT at counter_k1 during work hours — 8 empty looks). A recipe_book_shared target is added (pantry at rest, counter during cooking). The pan-at-cupboard-at-noon claim is retained and now the pan-at-cupboard-at-18:00 is the expected state (not a refutation).

What would refute it: pan_shared at counter_k1 at 18:00 on a weekday, or spatula_shared at counter_k1 at 18:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday (cooking has not started yet)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 18.5
  },
  {
   "claim": "The pan is on the kitchen counter at 19:00 on a weekday (cooking in progress)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 20
  },
  {
   "claim": "The spatula is in the drawer at 18:00 on a weekday (not yet in use)",
   "target": "spatula_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 18.5
  },
  {
   "claim": "The recipe book is on the counter at 19:00 on a weekday (Hana is following a recipe)",
   "target": "recipe_book_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 20
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "sometimes"
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
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
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
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:mug": [
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
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
