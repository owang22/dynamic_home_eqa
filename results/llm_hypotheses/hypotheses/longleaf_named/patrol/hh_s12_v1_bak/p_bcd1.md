# p_bcd1 — Saturday is baking-and-cycling day; Sunday is rest and ironing

The weekend has a fixed structure. Saturday morning (8:30–12:00) Elena bakes: the baking_tray, mixing_bowl, and recipe_book come out of the pantry shelf to the kitchen counter. Saturday afternoon (14:00–17:00) Elena cycles to see friends: helmet, bike_lock, backpack are OUT_OF_HOUSE. Sunday is quieter: Priya does yoga 10:00–11:00 (yoga mat on living room floor), and in the afternoon (14:00–16:00) they iron together: the iron comes out of the wardrobe and the ironing board is set up on the bedroom floor. Elena's weekday commute is standard (8:00–17:30, all items out). Priya's weekday walk is 8:00–9:00. What sets this apart: on Saturday between 9:00 and 11:00, the pantry shelf is missing the baking tray and mixing bowl (they're on the counter), and on Sunday between 14:00 and 16:00 the iron is NOT in the wardrobe. What would refute it: baking_tray at pantry_shelf_k1 on Saturday at 10:00, or iron at wardrobe_b1 on Sunday at 15:00.

```json
{
 "claims": [
  {
   "claim": "The baking tray is on the kitchen counter on Saturday morning",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 9,
   "to": 11
  },
  {
   "claim": "The mixing bowl is on the kitchen counter on Saturday morning",
   "target": "mixing_bowl_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 9,
   "to": 11
  },
  {
   "claim": "Elena's helmet is out of the house Saturday afternoon",
   "target": "helmet_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The iron is out of the wardrobe on Sunday afternoon",
   "target": "iron_shared",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Priya's yoga mat is on the living room floor Sunday morning",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 10,
   "to": 11
  }
 ],
 "targets": {
  "baking_tray_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8.5,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "mixing_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8.5,
    "to": 12,
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
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8.5,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "iron_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "helmet_elena": [
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
    "days": "weekend",
    "from": 14,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "bike_lock_elena": [
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
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
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
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "charger_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
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
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 15,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "sometimes"
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
    "from": 6.5,
    "to": 9,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
