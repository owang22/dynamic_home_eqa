# p_a4e8 — The bookshelf bookends: laptop rests on bookshelf overnight and evening, desk 10-to-16

This variant of the midday-desk pattern places Omar's laptop on the bookshelf (bookshelf_l1) rather than the coffee table during its off-desk hours. The evidence supports both resting spots: at 03:00 the laptop appears at coffee_table_l1 (2×) and bookshelf_l1 (2×); at 09:00 it splits three ways (coffee_table 3×, desk 2×, bookshelf 2×); at 17:00 it is at bookshelf_l1 (1×) or desk_o1 (1×); on weekend mornings it is at bookshelf_l1 (2×). The bookshelf is in the office, so it is a natural "closed laptop" spot between work sessions, while the coffee table is where he takes it for casual browsing or while waiting for coffee.

Everything else follows the same skeleton as the standard split: Marco's keys and water bottle leave at 8, return at 17:30; his laptop stays at desk_b1. The remote is fixed on the tv_stand. The pan emerges from the cupboard at 18:25. The guitar moves to the couch at 21:00. The iron goes to Omar's bed at 21:00.

What would refute this: finding the laptop at bookshelf_l1 at 14:00 on a weekday (it should be at the desk); finding it at the coffee table at 03:00 on multiple consecutive nights (the bookshelf pattern would be wrong); finding the remote off the tv_stand.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is on the bookshelf at 03:00 overnight",
   "target": "laptop_omar",
   "expect": "bookshelf_l1",
   "days": "both",
   "from": 2.75,
   "to": 3.25
  },
  {
   "claim": "Omar's laptop is at his desk at 15:00 during his core work block",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 14.75,
   "to": 15.25
  },
  {
   "claim": "The remote is on the tv stand at 20:30 during evening TV",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 20.25,
   "to": 20.75
  },
  {
   "claim": "Marco's guitar is on the couch at 21:30",
   "target": "guitar_marco",
   "expect": "couch_l1",
   "days": "both",
   "from": 21.25,
   "to": 21.75
  },
  {
   "claim": "Omar's water bottle is in the dish rack at 03:00",
   "target": "water_bottle_omar",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 2.75,
   "to": 3.25
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 16,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 16,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   }
  ],
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 23,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "water_bottle_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 16,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
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
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18.25,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.25,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "iron_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 22.5,
    "at": "bed_b2",
    "chance": "usually"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
