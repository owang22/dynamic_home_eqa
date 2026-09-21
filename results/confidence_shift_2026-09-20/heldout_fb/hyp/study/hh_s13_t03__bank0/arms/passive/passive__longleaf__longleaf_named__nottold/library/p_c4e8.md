# p_c4e8 — No Laptop Travel, Water Bottle Wandering (fork of p_f5a0)

This is a fork of p_f5a0. The core claim (laptop stays home at desk_b1) is unchanged and still plausible. However, the water bottle claim has gone against 3 times since the last call. The evidence shows water_bottle_hana at sink_k1 and dish_rack_k1 at 03:00, at entry_hook_e1 at 18:00, and at kitchen_table_k1 at 20:00. It is NOT at counter_k1 during the day. The water bottle follows Hana: it's in the kitchen at night (washed and drying), dumped at the entry hook when she gets home, then moves to the kitchen table for her evening drink.

What changed from the parent: water_bottle_hana no longer sits at counter_k1 from 7 to 22. Instead it cycles: sink/dish_rack overnight, entry_hook in the early evening, kitchen_table later in the evening. The claim about water bottle at counter is replaced with a claim about it at the entry hook at 18:00.

What would refute it: water_bottle_hana at counter_k1 at 12:00 on a weekday, or laptop_hana OUT_OF_HOUSE at 12:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at desk_b1 at noon on a weekday",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Hana's water bottle is at the entry hook at 18:00 on a weekday (just got home)",
   "target": "water_bottle_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Hana's water bottle is at the kitchen table at 20:00 on a weekday (evening drink)",
   "target": "water_bottle_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19.5,
   "to": 21.5
  },
  {
   "claim": "Hana's jacket is out of the house at noon on a weekday",
   "target": "jacket_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 17,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 21,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 21,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 2,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 19.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "charger_hana": [
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
    "chance": "usually"
   }
  ],
  "jacket_hana": [
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
   }
  ],
  "hat_hana": [
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
   }
  ],
  "handbag_hana": [
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
  "wallet_hana": [
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
  "sunglasses_hana": [
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
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "ON_PERSON",
    "chance": "usually"
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
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
