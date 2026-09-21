# p_5d1f — Weekend Kitchen: Table Active for Meals, Pantry for Dry Storage, Counter for Baking

On Saturday and Sunday both residents are home all day (the messages confirm "we're off our usual routine and around the house more"). Marco goes out for errands around midday (12–14 h); Yuki takes her late-morning walk (10–11 h) with the dog. The kitchen table is the meal hub: bowls and plates come out for breakfast (~08:00–09:00), lunch (~12:00–14:00), and dinner (~18:00–19:00). Dry goods (baking tray, mixing bowl, dog food bag, shopping bags) rest on the pantry shelf between uses. The counter is active during baking sessions (Marco morning 09:00–12:00, Yuki afternoon/evening 16:00–19:00 or 18:00–22:00).

This differs from p_8c4d (which places the spatula on the counter 16–19 h weekend, scored for 2 against 4) and p_c37d (which places it 17–19 h, scored for 2 against 2). The weekend 03:00 sightings show the dog food bag on the pantry shelf (not the kitchen floor as p_3e7a claims), and the 13:00–14:00 sightings show plate_yuki at the kitchen table. If the dog food bag is on the kitchen floor at 07:00 on a Saturday, or if the baking tray is on the counter at 03:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The dog food bag is on the pantry shelf at 07:00 on a weekend, not on the kitchen floor",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekend",
   "from": 6.5,
   "to": 8.5
  },
  {
   "claim": "Yuki's plate is at the kitchen table at 14:00 on a weekend during the midday meal",
   "target": "plate_yuki",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Marco's keys are out of the house at 13:00 on a weekend during his midday errand",
   "target": "keys_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 12,
   "to": 14
  },
  {
   "claim": "The dog leash is on Yuki's person at 10:30 on a weekend during her late-morning walk",
   "target": "dog_leash_shared",
   "expect": "ON_PERSON",
   "days": "weekend",
   "from": 10,
   "to": 11
  }
 ],
 "targets": {
  "dog_food_bag_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11.5,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11.5,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:bowl": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "bowl_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "bowl_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "plate_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12.5,
    "to": 14.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "plate_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12.5,
    "to": 14.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "mixing_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "keys_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "phone_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "tablet_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
