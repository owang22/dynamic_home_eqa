# p_8e4a — Cooking at 19:00; dinner at the dining table 19:30–21:00

Both residents cook together (or one cooks while the other helps) starting around 19:00. The pan, spatula, kitchen knife, and recipe book migrate to the counter during the 19:00–20:00 cooking window. Dinner is served at the dining table (not the kitchen table) around 19:30–20:00: plates, glasses, and the water bottle appear at dining_table_d1 at 20:00. After dinner, dishes go to the sink or dish rack, and the cooking implements return to the cupboard or drawer by 20:30. The snack bowl and remote move to the living room for evening TV around 20:30–22:00.

This document is distinct from p_2f8e (which placed cooking at 19:00 with the counter as workstation) in that it adds the dinner-at-dining-table phase and the post-dinner transition. It is distinct from p_4389 (which put plates at the kitchen table) because the 20:00 sightings clearly show plates and glasses at dining_table_d1.

What would refute it: if the pan is found at the counter at 18:00 (too early) or if dinner plates are consistently at the kitchen table rather than the dining table, the timing or location is wrong.

```json
{
 "claims": [
  {
   "claim": "The pan is on the counter during the 19:00 cooking window",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Omar's plate is at the dining table during dinner",
   "target": "plate_omar",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Marco's glass is at the dining table during dinner",
   "target": "glass_marco",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The spatula is on the counter during the cooking window",
   "target": "spatula_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The recipe book is at the pantry shelf before cooking starts",
   "target": "recipe_book_shared",
   "expect": "pantry_shelf_k1",
   "days": "both",
   "from": 17,
   "to": 19
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
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 23,
    "at": "cupboard_k1",
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
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
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
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "plate_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 23,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "plate_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 23,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "glass_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "glass_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
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
    "days": "both",
    "from": 20.5,
    "to": 22.5,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 20.5,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
