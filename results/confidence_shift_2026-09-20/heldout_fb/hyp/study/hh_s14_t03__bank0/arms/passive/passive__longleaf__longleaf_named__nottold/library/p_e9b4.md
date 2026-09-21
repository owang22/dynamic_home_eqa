# p_e9b4 — Afternoon vacuum on weekdays, evening vacuum on weekends; storage shelf is the resting spot (fork of p_f8b3)

The parent p_f8b3 correctly identified the weekday afternoon vacuum (13:00–15:30, five consecutive 14:00 sightings on floor_l_l1). However, its claim that the vacuum returns to storage_floor_s1 by 17:00 has scored 0-for / 3-against: at 17:00 on weekdays the robot finds it at storage_shelf_s1 (x2), not storage_floor_s1. The 18:00 and 19:00 sightings are split between the two storage locations, suggesting the vacuum is parked on the shelf after use, not on the floor.

What changed: I replaced the 16–18h block from storage_floor_s1 to storage_shelf_s1. I added weekend blocks: the vacuum rests at storage_shelf_s1 all day (03:00 and 14:00 weekend sightings confirm this), with an evening vacuuming session around 20:30–23:00 (21:00 weekend: floor_l_l1 x2). The 23:00 weekend sighting at storage_floor_s1 is the tail end of the evening session.

What would refute this fork: the vacuum at storage_shelf_s1 at 14:00 on a weekday (it should be on the living room floor); the vacuum on floor_l_l1 at 10:00 on a weekend (no weekend morning vacuum is evidenced); the vacuum at storage_shelf_s1 at 21:00 on a weekend (it should be in use on the floor).

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor during Yuki's weekday afternoon vacuuming",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 13,
   "to": 15.5
  },
  {
   "claim": "The vacuum cleaner is on the storage shelf at 17:00 on a weekday after the afternoon session",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_shelf_s1",
   "days": "weekday",
   "from": 16.5,
   "to": 18
  },
  {
   "claim": "The vacuum cleaner is on the living room floor during the weekend evening vacuum",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 20.5,
   "to": 23
  },
  {
   "claim": "The vacuum cleaner is on the storage shelf at 14:00 on a weekend",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_shelf_s1",
   "days": "weekend",
   "from": 13,
   "to": 15
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15.5,
    "at": "floor_l_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 10.5,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20.5,
    "to": 23,
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
    "days": "weekday",
    "from": 6.75,
    "to": 8.5,
    "at": "floor_k_k1",
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
  "class:wall_clock": [
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
  "class:lamp": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "side_table_l1",
    "chance": "almost_always"
   }
  ],
  "class:candle": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:tissue_box": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
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
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 10,
    "to": 14,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
  "class:ironing_board": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   }
  ],
  "class:toolbox": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   }
  ],
  "class:board_game": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
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
  ]
 }
}
```
