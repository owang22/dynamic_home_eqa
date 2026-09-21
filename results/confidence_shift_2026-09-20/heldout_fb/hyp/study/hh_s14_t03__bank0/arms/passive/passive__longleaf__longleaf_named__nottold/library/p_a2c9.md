# p_a2c9 — Shopping bag: Yuki unpacks at the counter, empty bags end at the entry

The shopping_bag_shared sightings tell a clear three-act story on weekdays. At 03:00 the bag is at pantry_shelf_k1 (2 sightings) or floor_k_k1 (1)—its resting spot between errands. At 14:00 it is at counter_k1 (3 sightings): Yuki has just returned from her afternoon errand (roughly 13:00–14:30) and is unpacking groceries at the kitchen counter. By 18:00 it is back at pantry_shelf_k1 (1 sighting), and by 23:00 the empty bags are at entry_floor_e1 (2 sightings)—dumped or set aside near the door.

What sets this apart: the shopping bag is actively at counter_k1 during 14:00–16:00 on weekdays (Yuki unpacking), not at pantry_shelf_k1 where most documents park it all day. The entry_floor_e1 placement at 22:00–24:00 is a distinct evening state (empty bags waiting to be recycled).

What would refute this: the shopping bag at pantry_shelf_k1 at 14:00 on a weekday (it should be at the counter being unpacked); the shopping bag at counter_k1 at 03:00 (it should be at the pantry shelf); the shopping bag at entry_floor_e1 at 12:00 (too early for the evening dump).

```json
{
 "claims": [
  {
   "claim": "The shopping bag is at the kitchen counter during Yuki's weekday afternoon unpacking",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 14,
   "to": 16
  },
  {
   "claim": "The shopping bag is at the pantry shelf at 03:00 on a weekday",
   "target": "shopping_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The shopping bag is on the entry floor in the evening after unpacking",
   "target": "shopping_bag_shared",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 22,
   "to": 24
  }
 ],
 "targets": {
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "sometimes"
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
  "class:wall_clock": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "class:cutting_board": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
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
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "class:dog_food_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "class:baking_tray": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "class:mixing_bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ]
 }
}
```
