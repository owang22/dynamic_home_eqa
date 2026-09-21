# p_e4b7 — The 19-to-20 Kitchen: Prep at 18, Cook at 19, Serve at 20

This document captures the precise two-phase rhythm of the weekday evening kitchen. The evidence is unambiguous: the pan sits in the cupboard at 18:00 on every observed day (2/2 sightings) and appears on the counter for the first time at 19:00. The spatula follows the same arc—drawer at 18 (3 sightings), counter at 19 (1 sighting). The recipe book shifts from the pantry shelf to the counter in the same window. Yet the knife is already out at 18 on most days (3/4 sightings at counter), indicating that chopping and prep begin an hour before the main cooking. Plates, by contrast, stay in the cupboard through 18 and 19 (Hana's plate: cupboard at both 18 and 19) and only appear on the kitchen table at 20:00 (3 sightings). This means the household cooks from 19 to 20 and serves at 20, a full hour later than the "18:00 dinner" hypothesis in p_b9c4 and the "17:5 start" in p_c1d6.

What sets this document apart: it places the pan, spatula, and recipe book in storage (cupboard/drawer/pantry) through 18:00 and only on the counter from 19 onward, while the knife is the exception that comes out early for prep. It also holds plates in the cupboard until 20, not 18 or 19. The pot is less consistent (cupboard 2 days, counter 1 day at 18), so this document puts it in the cupboard through 19 as well.

What would refute it: if the pan is reliably on the counter at 18:00 (not just the knife), the 19-to-20 gap collapses and this document's core claim fails. If plates appear on the table at 19 rather than 20, the serving window is wrong.

```json
{
 "claims": [
  {
   "claim": "The pan is still in the cupboard at 18:00 on a weekday because cooking has not started yet",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The pan is on the kitchen counter at 19:30 on a weekday during the main cooking phase",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Hana's plate is in the cupboard at 19:00 on a weekday because dinner is not yet served",
   "target": "plate_hana",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The spatula is in the drawer at 18:00 on a weekday because the pan is not yet in use",
   "target": "spatula_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "plate_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
