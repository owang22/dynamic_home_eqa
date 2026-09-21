# p_f8b3 — Yuki's afternoon vacuum: the living room gets cleaned 13:00–15:30

The per-object evidence for vacuum_cleaner_shared is striking: at 14:00 on a weekday the robot finds it on floor_l_l1 five times in a row, while at 10:00 the sightings are split (2 storage, 2 floor). The 17:00 and 18:00 patrols show it back in storage. This pattern says Yuki's main vacuuming session is in the early afternoon (roughly 13:00–15:30), not the late morning that p_4e8b predicted (9:30–11:00, which scored only 2-for / 2-against). The 10:00 floor sightings are likely a quick spot-cleaning or the tail of a shorter morning pass, but the bulk of the work—five consecutive 14:00 sightings on the living room floor—belongs to the afternoon.

What sets this apart from p_4e8b: the primary vacuuming window is 13:00–15:30 on weekdays, not 9:30–11:00. The vacuum rests at storage_floor_s1 from 15:30 onward and from 00:00 to 13:00. A short secondary pass at 10:00 is allowed but is not the main event.

What would refute this: the vacuum on floor_l_l1 at 09:00 or 11:00 (outside both windows); the vacuum at storage_floor_s1 at 14:00 on a weekday (it should be out on the floor); the vacuum at floor_l_l1 at 16:00 or later (cleaning should be done by 15:30).

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
   "claim": "The vacuum cleaner is in storage at 03:00 on a weekday",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The vacuum cleaner is back in storage by 17:00 on a weekday",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 16,
   "to": 18
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
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
    "days": "both",
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
