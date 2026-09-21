# p_3d8f — Weekend: guitar on the couch, book on the couch, water bottle at the rack, dog food stays in the pantry

Weekends follow a distinct rhythm from weekdays. Yuki's guitar is on the couch at 14:00 (three consecutive weekend sightings), suggesting she plays it in the living room in the afternoon. Marco's book is on the couch at 03:00 on a Saturday (he was reading before bed the previous evening). His water bottle is at the dish rack at 03:00 Saturday (washed and drying overnight, unlike weekdays where it sits at the entry). The dog food bag never leaves the pantry shelf on weekends (5/5 sightings at pantry_shelf_k1 at 03:00, 07:00, 08:00, 11:00, 14:00), unlike weekdays where it appears on the kitchen floor during morning feeding. The shopping bag appears at the counter at 13:00–14:00 on weekends (Yuki unpacking groceries after her midday errands).

What sets this apart from the weekday documents: the guitar is at couch_l1 (not bedroom_floor_b1) during weekend afternoons; the water bottle is at dish_rack_k1 (not entry_hook_e1) in the weekend early morning; the dog food bag is at pantry_shelf_k1 all day (not floor_k_k1 during 7:00–8:50); the shopping bag is at counter_k1 during 13:00–15:00 (unpacking).

What would refute this: the guitar at bedroom_floor_b1 at 14:00 on a Saturday; the water bottle at entry_hook_e1 at 06:00 on a Saturday; the dog food bag at floor_k_k1 at 08:00 on a Saturday; the shopping bag at pantry_shelf_k1 at 14:00 on a Saturday (it should be at the counter being unpacked).

```json
{
 "claims": [
  {
   "claim": "Yuki's guitar is on the living room couch during her weekend afternoon practice",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 13,
   "to": 16
  },
  {
   "claim": "Marco's book is on the living room couch in the weekend early morning",
   "target": "book_marco",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Marco's water bottle is at the dish rack in the weekend early morning",
   "target": "water_bottle_marco",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 2,
   "to": 8
  },
  {
   "claim": "The dog food bag is in the pantry shelf during the weekend morning",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekend",
   "from": 6.5,
   "to": 9
  }
 ],
 "targets": {
  "guitar_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 17,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "book_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 6.75,
    "to": 8.5,
    "at": "floor_k_k1",
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
   },
   {
    "days": "weekend",
    "from": 12.5,
    "to": 15,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 15,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20.5,
    "to": 23,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 6,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "bed_b1",
    "chance": "sometimes"
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
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "ON_PERSON",
    "chance": "usually"
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
  "class:doormat": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
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
  ]
 }
}
```
