# p_2f8b — 18:00 Prep: Knife and Pot Out, Pan Still In

The 18:00 kitchen is a prep stage, not a cooking stage. The knife is on the counter three out of four times at 18:00 (chopping vegetables, slicing ingredients), the pot is on the counter once out of three (a sauce or soup starting), but the pan is firmly in the cupboard both times it was looked for at 18:00, and the spatula is in the drawer three out of four times. By 19:00 the picture flips: pan on the counter, spatula on the counter, recipe book on the counter. This two-phase pattern — prep at 18, cook at 19 — explains why the "pan on counter at 18" claims in p_b9c4 and p_c1d6 keep getting hammered (against 16 and against 24 respectively) while the "pan in cupboard at 18" claims in p_4c8f, p_7b4e, and p_8e4d hold up.

What sets this apart from p_7b4e: p_7b4e says the spatula is in the drawer at 18:00 (correct) but does not explicitly place the knife on the counter at 18:00 or the pot partially out. This document makes the knife-on-counter-at-18:00 its central prediction, which no other document claims.

What would refute it: if the pan is found on the counter at 18:00 on multiple weekday evenings, or if the knife stays in the drawer at 18:00 while the pan is already out.

```json
{
 "claims": [
  {
   "claim": "The kitchen knife is on the counter at 18:00 on a weekday (prep chopping underway)",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday (not yet in use)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The pan is on the counter at 19:00 on a weekday (main cooking started)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 20
  },
  {
   "claim": "The spatula is in the drawer at 18:00 on a weekday (not yet needed)",
   "target": "spatula_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  }
 ],
 "targets": {
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
