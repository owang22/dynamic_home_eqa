# p_7d3f — The 10-to-4 desk: laptop midday only, remote fixed, counter snacks, 21:00 wind-down

Marco commutes to his office 8:00–17:30 on weekdays; his keys, wallet, jacket, and backpack all leave with him and return around 18:00. His laptop, however, stays at desk_b1 overnight and when he is home — the one 10:00 coffee_table sighting is an outlier, not a pattern. Omar works from home but his desk block is narrower than the library has assumed: the robot finds his laptop on the coffee table or bookshelf at 09:00 (3 of 7 passes at coffee_table), settles it at desk_o1 from roughly 10:00 to 16:00, and it is back on the coffee table by 18:00. The 9-to-17.5 desk block in the top documents is too wide by an hour on each end.

The remote never leaves the tv_stand. Every single sighting in seven days puts it there, including during the 20:00–22:00 TV window. The snack bowl, by contrast, lives on the kitchen counter during the evening (20:00 passes show counter_k1 three times), not the coffee table. Marco's guitar is in the bedroom through the evening and migrates to the couch at 21:00, where it stays for the wind-down. The iron and ironing board go to Omar's bed at 21:00 for a pressing session. Water bottles sit in the dish rack overnight, not on the counter.

What would refute this: finding laptop_omar at desk_o1 at 09:00 or 17:30 on multiple weekday mornings/evenings; finding the remote off the tv_stand during the 20:00–22:00 window; finding the snack bowl on the coffee table at 20:00; finding the guitar in the bedroom at 21:30.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is on the coffee table at 09:00 before his desk block starts",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 8.75,
   "to": 9.25
  },
  {
   "claim": "Omar's laptop is at his desk at 14:00 during his core work block",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 13.75,
   "to": 14.25
  },
  {
   "claim": "The remote is on the tv stand at 21:00 during evening TV",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 20.75,
   "to": 21.25
  },
  {
   "claim": "The snack bowl is on the kitchen counter at 20:00 during TV",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19.75,
   "to": 20.25
  },
  {
   "claim": "Marco's guitar is on the couch at 21:30 during the wind-down",
   "target": "guitar_marco",
   "expect": "couch_l1",
   "days": "both",
   "from": 21.25,
   "to": 21.75
  },
  {
   "claim": "Omar's water bottle is in the dish rack at 03:00 overnight",
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
    "to": 10,
    "at": "coffee_table_l1",
    "chance": "usually"
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
    "at": "coffee_table_l1",
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
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "storage_floor_s1",
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
