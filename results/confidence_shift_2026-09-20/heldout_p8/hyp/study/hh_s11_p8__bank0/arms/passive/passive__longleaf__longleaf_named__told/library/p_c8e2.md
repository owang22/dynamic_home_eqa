# p_c8e2 — Weekday Kitchen: Plates at the Kitchen Table, Spatula in the Drawer, Dog Food to the Pantry

This document corrects the weekday kitchen picture that p_e9b2 gets wrong. The evidence shows that Priya's plate is not left on the dining table overnight; by the 16:00 pass it has moved to the sink or kitchen table, and by 18:00 it is in the cupboard. The dining table is a weekend and early-morning spot, not a weekday afternoon one. The spatula is in the drawer by 16:00 on weekdays, not on the counter as p_e9b2 claims. The dog food bag starts the day on the kitchen floor (where the dog eats) but is moved to the pantry shelf by the afternoon. The shopping bag, when present, stays at the pantry shelf rather than being unpacked on the counter.

This document sets itself apart by placing the weekday afternoon kitchen in its "put away" state: dishes in the cupboard or at the sink, utensils in the drawer, the dog food bag stored. The dining table is clear by mid-afternoon on weekdays because Hana is at work and Priya has finished her light dinner.

What would refute this: a weekday 14–20 h sighting of plate_priya on dining_table_d1, spatula_shared on counter_k1, or dog_food_bag_shared on floor_k_k1 after 14:00.

Objects that travel: Hana takes her handbag, keys, wallet, jacket, and phone out of the house at ~13:40 on weekdays and returns at ~23:00. Priya takes her keys, sunglasses, and jacket out for her morning walk (~7–9 h) and afternoon errands (~15–17 h). The dog leash goes out with Priya during walks.

```json
{
 "claims": [
  {
   "claim": "Priya's plate is at the kitchen table or in the cupboard on weekday afternoons, not on the dining table",
   "target": "plate_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 17
  },
  {
   "claim": "The spatula is in the kitchen drawer on weekday afternoons, not on the counter",
   "target": "spatula_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 14,
   "to": 20
  },
  {
   "claim": "The dog food bag is on the pantry shelf on weekday afternoons, not on the kitchen floor",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 14,
   "to": 20
  },
  {
   "claim": "The shopping bag stays on the pantry shelf on weekdays, not on the kitchen counter",
   "target": "shopping_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 8,
   "to": 20
  }
 ],
 "targets": {
  "plate_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 10,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "plate_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
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
    "from": 6,
    "to": 9,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
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
    "days": "both",
    "from": 6,
    "to": 12,
    "at": "floor_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 23,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
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
    "from": 6,
    "to": 9,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "keys_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
