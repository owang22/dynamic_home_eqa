# p_a6c1 — Marco's personal items stay home during his work shift: water bottle and mug at the coffee table, glass at the kitchen table for lunch

Marco leaves for work at 13:40 and returns at 23:00 on weekdays, but he does not take his water bottle, mug, or glass with him. The water bottle is found at coffee_table_l1 at 14:00, 16:00, and 18:00 on weekdays (three separate sightings while he is at work). His mug is at coffee_table_l1 at 14:00 on a weekday. His glass is at kitchen_table_k1 at 13:00 (lunch before he leaves) and at counter_k1 at 23:00 (just after he arrives home). At night (03:00) his glass is at nightstand_b1 (bedside) and his water bottle is at entry_hook_e1 or entry_floor_e1 (he sets it down at the entry when he comes in from work).

What sets this apart from the "work kit" documents (p_b7c2, p_8e2f, p_4a7c): those documents claim the lunchbox, vitamins, and journal leave the house. This document says the water bottle, mug, and glass do NOT leave. They remain at home on the coffee table or kitchen table while Marco is at work.

What would refute this: the water bottle at OUT_OF_HOUSE during 14–22h on a weekday (it should be at coffee_table_l1); the mug at OUT_OF_HOUSE during 14–18h on a weekday; the glass at nightstand_b1 at 14:00 on a weekday (it should be at the kitchen table or cupboard, not the bedside).

```json
{
 "claims": [
  {
   "claim": "Marco's water bottle is at the coffee table during his weekday work shift",
   "target": "water_bottle_marco",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 13,
   "to": 19
  },
  {
   "claim": "Marco's mug is at the coffee table during his weekday work shift",
   "target": "mug_marco",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Marco's glass is at the kitchen table during his weekday pre-work lunch",
   "target": "glass_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12.5,
   "to": 13.5
  },
  {
   "claim": "Marco's glass is at the kitchen counter just after he returns home on a weekday",
   "target": "glass_marco",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 22.5,
   "to": 24
  }
 ],
 "targets": {
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "mug_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "glass_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "lunchbox_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "vitamins_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "phone_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 14,
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23,
    "at": "entry_table_e1",
    "chance": "sometimes"
   }
  ],
  "class:keys": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "class:wallet": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "class:scarf": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:umbrella": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "class:shoes": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "class:backpack": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:notebook": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:doormat": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "class:toaster": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "class:kettle": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "class:knife_block": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "class:remote": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:lamp": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "side_table_l1",
    "chance": "almost_always"
   }
  ],
  "class:dog_toy": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
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
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6.75,
    "to": 8.5,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ]
 }
}
```
