# p_2c8d — Ines's full-day floor workspace with charger and headphones at the desk

This document takes the floor-workspace hypothesis to its logical conclusion: Ines works from the office floor (floor_o_o1) for the entire 09:00–18:00 window on weekdays. The laptop, water bottle, and mug are all on the floor beside her. However, the charger and headphones are NOT on the floor—they remain on desk_o1 because that is where they are stored overnight and where the power outlet is. The pen also stays on desk_o1 (it is a desk item, not a floor item).

The key difference from p_7f3e: here the laptop NEVER visits the desk during the work day. The 10:00 and 16:00–17:00 desk sightings are explained as the robot catching the laptop mid-transition (she briefly picks it up to charge or adjust, then sets it back on the floor). The 24 empty looks at desk_o1 during 9–17h are fully explained: the laptop is on the floor the entire time.

Elena's commute is standard: out 08:00–17:30 weekdays. The 21:00 TV migration applies as in other documents.

What sets this apart from p_7f3e: no desk visits for the laptop at all. If the laptop is found at desk_o1 at 10:00 or 16:00 on a weekday and stays there for more than a few minutes, this document is wrong while p_7f3e is right.

Refutation: three or more sightings of laptop_ines at desk_o1 during 9:00–17:00 on different weekday hours would refute the "never at desk" claim.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is on the office floor at 10:00 on weekdays",
   "target": "laptop_ines",
   "expect": "floor_o_o1",
   "days": "weekday",
   "from": 9,
   "to": 12
  },
  {
   "claim": "Ines's laptop is on the office floor at 16:00 on weekdays",
   "target": "laptop_ines",
   "expect": "floor_o_o1",
   "days": "weekday",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Ines's charger is on the office desk at 15:00 on weekdays",
   "target": "charger_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Elena's keys are out of the house at 12:00 on weekdays",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "The remote is on the coffee table at 22:00 on both days",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 9,
    "to": 18,
    "at": "floor_o_o1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "floor_o_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "charger_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "office_shelf_o1",
    "chance": "sometimes"
   }
  ],
  "headphones_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "pen_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 15,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_ines": [
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
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
  "keys_elena": [
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
   }
  ],
  "backpack_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
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
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23.5,
    "at": "coffee_table_l1",
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
    "from": 21,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
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
  ]
 }
}
```
