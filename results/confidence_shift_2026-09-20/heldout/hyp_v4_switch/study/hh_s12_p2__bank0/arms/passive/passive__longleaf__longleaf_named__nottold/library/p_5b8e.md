# p_5b8e — The charger stays home; a minimal work kit

Elena's work kit is deliberately small: laptop, notebook, pen, backpack, wallet, keys, hat, jacket, and shoes. She does NOT take her charger (the office has its own outlet), her umbrella (stays at the entry), her helmet or bike_lock (cycling is weekend-only), or her phone charger. The charger_elena sits at desk_b1 from the time she leaves until she returns, because it is plugged into the wall there. The umbrella_elena is a permanent fixture at entry_floor_e1. This hypothesis is specifically about which items travel and which do not. What sets this apart: p_7ef3 sends the charger OUT_OF_HOUSE; p_1e82 also sends it out. This document says the charger is at desk_b1 all day. What would refute it: charger_elena sighted OUT_OF_HOUSE or at a location other than desk_b1 between 9:00 and 16:00 on a weekday; or umbrella_elena sighted OUT_OF_HOUSE on a weekday.

```json
{
 "claims": [
  {
   "claim": "Elena's charger is at desk_b1 on weekday afternoons",
   "target": "charger_elena",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "Elena's umbrella stays at the entry floor on weekdays",
   "target": "umbrella_elena",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 8,
   "to": 17
  },
  {
   "claim": "Elena's bike lock stays at the entry table on weekdays",
   "target": "bike_lock_elena",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 8,
   "to": 17
  },
  {
   "claim": "Elena's laptop is out of the house on weekday afternoons",
   "target": "laptop_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 16
  }
 ],
 "targets": {
  "charger_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "desk_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "umbrella_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "helmet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "notebook_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "pen_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "backpack_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "hat_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "jacket_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "shoes_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "phone_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "towel_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 18,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "hair_dryer_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 7.5,
    "at": "sink_ba_ba1",
    "chance": "sometimes"
   }
  ],
  "skincare_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "toiletry_bag_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dresser_b1",
    "chance": "usually"
   }
  ],
  "book_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "mug_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "glass_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "plate_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
