# p_9c2e — Tablet Stays Home at the Kitchen Table During Work Hours (fork of p_8e1b)

This fork of p_8e1b offers an alternative to the "tablet travels" hypothesis. The tablet's claim at coffee_table_l1 has failed 3 times, but the tablet has only 2 receptacles in 30 sightings (counter_k1 and one other). If the tablet is NOT out of the house during weekday 9–14, it must be at one of those 2 places. Since it is not at the counter (6 empty looks during 9–17), and the coffee table is failing, the remaining candidate is the kitchen table — the workspace where the laptop sits in the evenings and where the notebook and pen live.

What changed from p_8e1b: (1) The tablet_mara target now defaults to kitchen_table_k1 (the workspace) instead of coffee_table_l1. (2) A weekday 9–14 block keeps it at the kitchen table (Mara leaves it there as a reference device, or it is where she does quick tasks before/after the co-working window). (3) A weekend and evening block at counter_k1 captures its statistical "usual" place. (4) The claim now expects the tablet at kitchen_table_k1 during weekday 9–14. (5) The coffee_table_l1 block is retained only for weekday 6–8.5 (morning use).

What sets this apart from p_8e1b: the tablet is at the kitchen table (not the coffee table) during weekday work hours, and it is IN the house. What sets this apart from p_3a7f (the sibling fork): the tablet does NOT leave the house; it is at the kitchen table. What would refute it: the tablet found OUT_OF_HOUSE (i.e., not in the house) during weekday 9–14, or the tablet found at the coffee table on a weekday at 10:00.

```json
{
 "claims": [
  {
   "claim": "The tablet is at the kitchen table during weekday work hours (stays home at the workspace, not the coffee table)",
   "target": "tablet_mara",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 14
  },
  {
   "claim": "The glasses are out of the house during weekday work hours (travels with Mara to the co-working space)",
   "target": "glasses_mara",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 14
  },
  {
   "claim": "The phone is out of the house during weekday work hours (travels with Mara)",
   "target": "phone_mara",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 14
  },
  {
   "claim": "The keys are out of the house during weekday work hours (travels with Mara)",
   "target": "keys_mara",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 14
  }
 ],
 "targets": {
  "laptop_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "charger_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "headphones_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "glasses_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "phone_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "notebook_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "pen_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "water_bottle_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "keys_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "wallet_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "jacket_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "backpack_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "tablet_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 8.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 14,
    "to": 18,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared_1": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "yoga_mat_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "book_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "medication_bottle_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "makeup_kit_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8.5,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "hairbrush_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "towel_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "lunchbox_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "umbrella_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "suitcase_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "laundry_basket_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "vacuum_cleaner_shared_1": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 15,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "watering_can_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "class:mug": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
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
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "bowl_shared_1": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "bowl_shared_2": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:pan": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "class:pot": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "plate_shared_1": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_shared_2": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
