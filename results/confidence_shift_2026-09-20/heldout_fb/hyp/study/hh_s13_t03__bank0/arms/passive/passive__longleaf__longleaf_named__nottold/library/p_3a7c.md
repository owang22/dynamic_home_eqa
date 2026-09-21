# p_3a7c — The 18:30 Cook, 20:00 Dinner, 21:00 Coffee Table, 22:30 Desk

Hana arrives home at 17:30 and drops her laptop, charger, water bottle, and pen at the entry hook. By 18:00 she is in the kitchen with the knife already out, prepping vegetables. The pan stays in the cupboard until 18:30, when it joins the counter. The spatula follows at 18:30. Cooking runs 18:30 to 19:30. At 19:30 the plates come out and dinner is eaten at the kitchen table until 20:30. Between 20:00 and 20:30 the mugs and snack bowl migrate from the kitchen to the coffee table. The blanket leaves the couch at 20:30 and moves to the coffee table for the TV session, which runs until 22:00. At 22:00 Hana takes the laptop to desk_b1 for an evening work session that lasts until 23:30. Priya goes to bed at 22:30. The guitar stays on the bedroom floor all evening—no weekday playing. The remote stays at the TV stand on weekdays, never moving to the couch.

This document differs from p_b9c4 (which places the pan on the counter from 17:30) and p_c1d6 (which claims a noon cooking window for Priya). The evidence is clear: the pan is in the cupboard at the 18:00 pass (2 sightings) and on the counter at 19:00 (1 sighting), pinning the move to the 18:00–19:00 gap. The knife is on the counter at 18:00 (3 sightings) but the pan is not yet out, so prep begins before the pan arrives. The snack bowl is on the counter at 18:00–19:00 (4 sightings) and on the coffee table at 21:00 (2 sightings), confirming a 20:00–20:30 transition. The laptop is at the entry hook at 18:00 and at the desk at 22:00–23:00, with no sightings in between—Hana works from 22:00, not 21:00.

This document is refuted if the pan is found on the counter before 18:30, if dinner plates are at the coffee table rather than the kitchen table, if Hana's laptop is at the desk before 21:30, or if the guitar is off the bedroom floor during the 19:00–23:00 window on a weekday.

```json
{
 "claims": [
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday (cooking has not started yet)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.75,
   "to": 18.25
  },
  {
   "claim": "The pan is on the kitchen counter at 19:00 on a weekday (cooking in progress)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.75,
   "to": 19.25
  },
  {
   "claim": "Hana's plate is at the kitchen table at 20:00 on a weekday (dinner in progress)",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19.75,
   "to": 20.25
  },
  {
   "claim": "Priya's mug is at the coffee table at 21:30 on a weekday (TV session)",
   "target": "mug_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 22
  },
  {
   "claim": "Hana's laptop is at desk_b1 at 22:30 on a weekday (evening work session)",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 22,
   "to": 23.5
  }
 ],
 "targets": {
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.75,
    "to": 19.5,
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
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "class:plate": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 20.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22.5,
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
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "laptop_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 23.5,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "charger_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
