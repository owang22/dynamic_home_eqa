# p_8e2a — The 19:00 Flash Cook: Kitchen Wakes at Seven, Clear by Eight

Hana arrives home at 17:30 and Priya has been home all afternoon. The kitchen sits cold from the morning: the pan, pot, and spatula stay in their storage spots (cupboard, cupboard, drawer) through the entire afternoon. At roughly 19:00 Hana starts cooking dinner — the pan and spatula come out to the counter, the recipe book is pulled from the pantry shelf, and the pot may join for a soup or sauce. This is a *flash* cook: the items are out for roughly 30–60 minutes. By 20:00 the cooking is done, plates come out of the cupboard to the kitchen table for serving, and the cookware goes back. By 21:00 the kitchen is clear again and the living room takes over for TV.

What sets this apart: the cooking window is 19-to-20, not 18-to-20 or 19-to-21. The 18:00 patrol pass catches the pan and spatula still in storage; the 19:00 pass catches them on the counter; the 20:00 pass catches plates at the table but the cookware already back in the cupboard. A document that places the pan on the counter at 18:00 (p_b9c4) or keeps it there through 21:00 (p_c1d6) is wrong at one of those passes.

Refutation: if the pan is seen on the counter at the 18:00 pass on multiple weekday evenings, or if the spatula is on the counter at 21:00, the 19-to-20 window is too narrow and this document fails.

```json
{
 "claims": [
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday because cooking has not started yet",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The pan is on the kitchen counter at 19:00 on a weekday during the flash cook",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The spatula is in the drawer at 18:00 on a weekday because the pan is not yet in use",
   "target": "spatula_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Hana's plate is at the kitchen table at 20:00 on a weekday because dinner is being served",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 20,
   "to": 21
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
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
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "plate_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 21,
    "at": "kitchen_table_k1",
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
    "days": "weekday",
    "from": 20,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:plate": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
