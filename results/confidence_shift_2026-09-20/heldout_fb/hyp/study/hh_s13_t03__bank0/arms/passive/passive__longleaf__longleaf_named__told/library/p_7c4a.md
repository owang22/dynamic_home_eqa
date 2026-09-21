# p_7c4a — The 19:00 Cook: Kitchen Cold at 18, Hot at 19, Served at 20

Hana arrives home at 17:30 on weekdays and begins light prep — the knife and cutting board come out at 18:00, the recipe book moves to the counter. But the heavy cooking does not start until 19:00: the pan is still in the cupboard at 18:00 (2/2 sightings) and appears on the counter at 19:00 (2/2 sightings). The pot follows the identical pattern. The spatula stays in the drawer at 18:00 (3/4 sightings) and moves to the counter at 19:00. Dinner plates appear on the kitchen table at 20:00 (3/5 sightings), confirming service at eight. This is a three-phase evening: prep 18–19, cook 19–20, serve 20–21.

On weekends the cook is later still: the pan is in the cupboard at 03:00 and only appears on the counter at 17:00–18:00, with the knife out at 17:00 (2 sightings) and the spatula at 19:00.

This document directly contradicts any hypothesis that places the pan, pot, or spatula on the counter at 18:00 on a weekday. What would refute it: seeing the pan on the counter at 18:00 on two or more occasions, or seeing dinner plates on the kitchen table before 19:30.

```json
{
 "claims": [
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday because the main cooking has not started yet",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The pan is on the kitchen counter at 19:30 on a weekday during the main cooking phase",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20.5
  },
  {
   "claim": "Hana's plate is on the kitchen table at 20:00 on a weekday because dinner is being served",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The spatula is in the drawer at 18:00 on a weekday because the pan is not yet in use",
   "target": "spatula_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17.5,
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
    "days": "weekend",
    "from": 0,
    "to": 17,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
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
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 17,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17.5,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 16.5,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 16.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 17.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 16.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
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
    "days": "weekend",
    "from": 0,
    "to": 18.5,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
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
    "to": 17,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 16.5,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 16.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "plate_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
